"""Multi-task training loop (strategy §6.1 Step 2).

Implements the staged schedule that the small-dataset risk (§5.3) demands:
  1. Heads-only warmup with the encoder FROZEN for `freeze_encoder_epochs`.
  2. Unfreeze the encoder at a low LR; train jointly.
  3. Early stopping on val loss (patience 3, eval every 100 steps).
  4. Separate param groups: low LR for the encoder, higher for the heads.

The data loading is wired to ``MaskedMultiTaskDataset`` (built by ``run_train.py``);
the loss is per-head masked so the disjoint v1 transfer pools train the right head
per example (§5.5, ``build_dataset.py``).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader

from pebble_llm.config import Config
from pebble_llm.evaluation.metrics import emotion_macro_f1, mae
from pebble_llm.models.losses import MultiTaskLoss
from pebble_llm.models.neobert_multitask import NeoBERTMultiTask
from pebble_llm.utils.logging import get_logger
from pebble_llm.utils.seed import set_seed

logger = get_logger(__name__)


def _param_groups(model: NeoBERTMultiTask, cfg: Config) -> list[dict]:
    encoder_params = list(model.encoder.parameters())
    head_params = [
        p for n, p in model.named_parameters() if not n.startswith("encoder.")
    ]
    return [
        {"params": encoder_params, "lr": cfg.training.lr_encoder},
        {"params": head_params, "lr": cfg.training.lr_heads},
    ]


def _loss_args(out: dict, batch: dict) -> dict:
    """Map model outputs + a batch onto the masked MultiTaskLoss kwargs."""
    return {
        "score_pred": out["scores"],
        "score_target": batch["scores"],
        "emotion_logits": out["emotion_logits"],
        "emotion_target": batch["emotion_id"],
        "safety_logit": out["safety_logit"],
        "safety_target": batch["safety_flag"],
        "mask_score": batch["mask_score"],
        "mask_emotion": batch["mask_emotion"],
        "mask_safety": batch["mask_safety"],
    }


@torch.no_grad()
def _evaluate(
    model: NeoBERTMultiTask,
    loader: DataLoader,
    loss_fn: MultiTaskLoss,
    device: torch.device,
    severity_idx: int | None,
    use_fp16: bool,
) -> dict[str, float]:
    """Masked val loss + per-head metrics on the rows that label each head."""
    model.eval()
    total_loss, n_batches = 0.0, 0
    emo_pred: list[np.ndarray] = []
    emo_true: list[np.ndarray] = []
    sev_pred: list[np.ndarray] = []
    sev_true: list[np.ndarray] = []
    for batch in loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        with torch.autocast(device_type=device.type, enabled=use_fp16):
            out = model(batch["input_ids"], batch["attention_mask"])
            loss, _ = loss_fn(**_loss_args(out, batch))
        total_loss += loss.item()
        n_batches += 1

        emo_rows = batch["mask_emotion"].bool().cpu().numpy()
        if emo_rows.any():
            emo_pred.append(out["emotion_logits"].argmax(-1).cpu().numpy()[emo_rows])
            emo_true.append(batch["emotion_id"].cpu().numpy()[emo_rows])
        if severity_idx is not None:
            sev_rows = batch["mask_score"].bool().cpu().numpy()
            if sev_rows.any():
                sev_pred.append(out["scores"][:, severity_idx].float().cpu().numpy()[sev_rows])
                sev_true.append(batch["scores"][:, severity_idx].cpu().numpy()[sev_rows])

    metrics = {"val_loss": total_loss / max(n_batches, 1)}
    if emo_pred:
        metrics["emotion_macro_f1"] = emotion_macro_f1(
            np.concatenate(emo_pred), np.concatenate(emo_true)
        )
    if sev_pred:
        metrics["severity_mae"] = mae(np.concatenate(sev_pred), np.concatenate(sev_true))
    return metrics


def train(cfg: Config, train_loader: DataLoader, val_loader: DataLoader, seed: int) -> dict:
    """Train one seed; return the best val metrics. Loop over cfg.training.seeds upstream."""
    set_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_fp16 = cfg.training.fp16 and device.type == "cuda"
    severity_idx = (
        cfg.model.score_dims.index("severity") if "severity" in cfg.model.score_dims else None
    )

    model = NeoBERTMultiTask(cfg.model).to(device)
    loss_fn = MultiTaskLoss(
        w_score=cfg.training.loss_weight_score,
        w_emotion=cfg.training.loss_weight_emotion,
        w_safety=cfg.training.loss_weight_safety,
        safety_pos_weight=cfg.training.safety_pos_weight,
    ).to(device)
    optimizer = AdamW(_param_groups(model, cfg), weight_decay=cfg.training.weight_decay)
    scaler = torch.amp.GradScaler("cuda", enabled=use_fp16)

    # Stage 1: freeze encoder for the warmup epochs (§5.3). Param groups already
    # include the encoder, so toggling requires_grad is enough to (un)freeze it.
    model.set_encoder_trainable(False)

    output_dir = Path(cfg.training.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    best_val = float("inf")
    best_metrics: dict[str, float] = {}
    epochs_no_improve = 0

    for epoch in range(cfg.training.epochs):
        if epoch == cfg.training.freeze_encoder_epochs:
            logger.info("Unfreezing encoder at epoch %d", epoch)
            model.set_encoder_trainable(True)

        model.train()
        last_total = 0.0
        for batch in train_loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            optimizer.zero_grad()
            with torch.autocast(device_type=device.type, enabled=use_fp16):
                out = model(batch["input_ids"], batch["attention_mask"])
                loss, parts = loss_fn(**_loss_args(out, batch))
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            last_total = parts["loss_total"]

        val = _evaluate(model, val_loader, loss_fn, device, severity_idx, use_fp16)
        logger.info(
            "epoch %d/%d | train loss=%.4f | %s",
            epoch + 1,
            cfg.training.epochs,
            last_total,
            " ".join(f"{k}={v:.4f}" for k, v in val.items()),
        )

        if val["val_loss"] < best_val:
            best_val = val["val_loss"]
            best_metrics = {"seed": float(seed), **val}
            epochs_no_improve = 0
            torch.save(
                {"epoch": epoch, "state_dict": model.state_dict(), "val": val},
                output_dir / f"seed_{seed}_best.pt",
            )
            logger.info("  -> new best (val_loss=%.4f)", best_val)
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= cfg.training.early_stopping_patience:
                logger.info("Early stopping at epoch %d (patience %d)", epoch, cfg.training.early_stopping_patience)
                break

    return best_metrics
