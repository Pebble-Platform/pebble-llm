"""Emotion-head pre-training on GoEmotions (strategy §6.1 Step 1).

Freeze the encoder for the first `freeze_encoder_epochs` (default 2) so the
emotion head converges without destabilising the pretrained representations,
then unfreeze for the remaining epochs at `lr_encoder` (default 1e-5) for
shallow adaptation. Only the emotion head drives the loss here.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import AutoTokenizer  # type: ignore[import-untyped]

from pebble_llm.config import Config
from pebble_llm.data.datasets import EmotionDataset, Example
from pebble_llm.data.external import load_goemotions_for_emotion_head
from pebble_llm.data.taxonomy import LABEL_TO_ID
from pebble_llm.evaluation.metrics import emotion_macro_f1
from pebble_llm.models.neobert_multitask import NeoBERTMultiTask

logger = logging.getLogger(__name__)


def _build_goemotions_dataset(split: str, tokenizer: object, cfg: Config) -> EmotionDataset:
    ds = load_goemotions_for_emotion_head(split)
    examples = [
        Example(
            text=row["text"],
            scores={d: 0.0 for d in cfg.model.score_dims},
            emotion_id=LABEL_TO_ID[row["pebble_label"]],
            safety_flag=False,
        )
        for row in ds
    ]
    return EmotionDataset(examples, tokenizer, cfg.model.score_dims, cfg.data.max_seq_length)


def _evaluate(model: NeoBERTMultiTask, loader: DataLoader, device: torch.device) -> float:  # type: ignore[type-arg]
    model.eval()
    all_preds: list[np.ndarray] = []
    all_labels: list[np.ndarray] = []
    with torch.no_grad():
        for batch in loader:
            logits = model(
                batch["input_ids"].to(device),
                batch["attention_mask"].to(device),
            )["emotion_logits"]
            all_preds.append(logits.argmax(-1).cpu().numpy())
            all_labels.append(batch["emotion_id"].numpy())
    return emotion_macro_f1(np.concatenate(all_preds), np.concatenate(all_labels))


def pretrain_emotion_head(cfg: Config) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_fp16 = cfg.training.fp16 and device.type == "cuda"
    output_dir = Path(cfg.training.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Loading tokenizer from %s", cfg.model.name)
    tokenizer = AutoTokenizer.from_pretrained(
        cfg.model.name,
        revision=cfg.model.revision,
        trust_remote_code=cfg.model.trust_remote_code,
    )

    logger.info("Building GoEmotions datasets")
    train_ds = _build_goemotions_dataset("train", tokenizer, cfg)
    val_ds = _build_goemotions_dataset("validation", tokenizer, cfg)
    train_loader = DataLoader(
        train_ds, batch_size=cfg.training.batch_size, shuffle=True, num_workers=2, pin_memory=True
    )
    val_loader = DataLoader(
        val_ds, batch_size=cfg.training.batch_size * 2, shuffle=False, num_workers=2, pin_memory=True
    )

    logger.info("Initialising NeoBERTMultiTask on %s", device)
    model = NeoBERTMultiTask(cfg.model).to(device)
    scaler = torch.amp.GradScaler("cuda", enabled=use_fp16)

    use_wandb = False
    try:
        import wandb  # type: ignore[import-untyped]

        wandb.init(project="pebble-emotion-pretrain", config=cfg.training.model_dump())
        use_wandb = True
    except Exception:
        pass

    optimizer: AdamW | None = None
    best_f1 = 0.0

    for epoch in range(cfg.training.epochs):
        # Rebuild optimizer at phase transitions only
        if epoch == 0:
            model.set_encoder_trainable(False)
            optimizer = AdamW(
                model.emotion_head.parameters(),
                lr=cfg.training.lr_heads,
                weight_decay=cfg.training.weight_decay,
            )
            logger.info("Epoch 0: encoder frozen, training emotion head only (lr=%.1e)", cfg.training.lr_heads)
        elif epoch == cfg.training.freeze_encoder_epochs:
            model.set_encoder_trainable(True)
            optimizer = AdamW(
                [
                    {"params": model.encoder.parameters(), "lr": cfg.training.lr_encoder},
                    {"params": model.emotion_head.parameters(), "lr": cfg.training.lr_heads},
                ],
                weight_decay=cfg.training.weight_decay,
            )
            logger.info(
                "Epoch %d: encoder unfrozen (lr_encoder=%.1e, lr_heads=%.1e)",
                epoch,
                cfg.training.lr_encoder,
                cfg.training.lr_heads,
            )

        assert optimizer is not None
        model.train()
        total_loss = 0.0

        for batch in train_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["emotion_id"].to(device)

            with torch.autocast(device_type=device.type, enabled=use_fp16):
                logits = model(input_ids, attention_mask)["emotion_logits"]
                loss = F.cross_entropy(logits, labels)

            optimizer.zero_grad()
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        val_f1 = _evaluate(model, val_loader, device)

        frozen = epoch < cfg.training.freeze_encoder_epochs
        logger.info(
            "Epoch %d/%d | loss=%.4f | val_macro_f1=%.4f | frozen=%s",
            epoch + 1,
            cfg.training.epochs,
            avg_loss,
            val_f1,
            frozen,
        )

        if use_wandb:
            wandb.log({"epoch": epoch, "train_loss": avg_loss, "val_macro_f1": val_f1})

        ckpt = {"epoch": epoch, "state_dict": model.state_dict(), "val_f1": val_f1}
        torch.save(ckpt, output_dir / f"epoch_{epoch}.pt")

        if val_f1 > best_f1:
            best_f1 = val_f1
            torch.save(ckpt, output_dir / "best.pt")
            logger.info("  -> new best checkpoint (val_macro_f1=%.4f)", best_f1)

    logger.info(
        "Pre-training complete. Best val_macro_f1=%.4f. Checkpoint: %s/best.pt",
        best_f1,
        output_dir,
    )
    if use_wandb:
        wandb.finish()
