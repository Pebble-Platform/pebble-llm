"""Multi-task training loop (strategy §6.1 Step 2).

Implements the staged schedule that the small-dataset risk (§5.3) demands:
  1. Heads-only warmup with the encoder FROZEN for `freeze_encoder_epochs`.
  2. Unfreeze the encoder at a low LR; train jointly.
  3. Early stopping on val loss (patience 3, eval every 100 steps).
  4. Separate param groups: low LR for the encoder, higher for the heads.

This is a runnable skeleton — the data loading and the eval loop are wired to the
stubs in data/ and evaluation/. Fill the TODOs to make it train for real.
"""

from __future__ import annotations

import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader

from pebble_llm.config import Config
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


def train(cfg: Config, train_loader: DataLoader, val_loader: DataLoader, seed: int) -> dict:
    """Train one seed; return the best val metrics. Loop over cfg.training.seeds upstream."""
    set_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = NeoBERTMultiTask(cfg.model).to(device)
    loss_fn = MultiTaskLoss(
        w_score=cfg.training.loss_weight_score,
        w_emotion=cfg.training.loss_weight_emotion,
        w_safety=cfg.training.loss_weight_safety,
        safety_pos_weight=cfg.training.safety_pos_weight,
    ).to(device)
    optimizer = AdamW(_param_groups(model, cfg), weight_decay=cfg.training.weight_decay)
    scaler = torch.cuda.amp.GradScaler(enabled=cfg.training.fp16)

    # Stage 1: freeze encoder for the warmup epochs (§5.3)
    model.set_encoder_trainable(False)

    for epoch in range(cfg.training.epochs):
        if epoch == cfg.training.freeze_encoder_epochs:
            logger.info("Unfreezing encoder at epoch %d", epoch)
            model.set_encoder_trainable(True)

        model.train()
        for batch in train_loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            optimizer.zero_grad()
            with torch.cuda.amp.autocast(enabled=cfg.training.fp16):
                out = model(batch["input_ids"], batch["attention_mask"])
                loss, parts = loss_fn(
                    score_pred=out["scores"],
                    score_target=batch["scores"],
                    emotion_logits=out["emotion_logits"],
                    emotion_target=batch["emotion_id"],
                    safety_logit=out["safety_logit"],
                    safety_target=batch["safety_flag"],
                )
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

        # TODO: eval on val_loader every cfg.training.eval_every_steps, early stop,
        #       checkpoint best, log to W&B (see evaluation/ and utils/logging.py).
        logger.info("epoch %d done | last train loss=%.4f", epoch, parts["loss_total"])

    # TODO: return real best-val metrics
    return {"seed": seed, "status": "skeleton — wire eval + checkpointing"}
