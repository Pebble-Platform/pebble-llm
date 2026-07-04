"""Pebble emotion-head pre-training — self-contained Kaggle script (§6.1 Step 1).

Validated GPU stack: torch==2.5.1 + xformers==0.0.28.post3 + transformers==4.48.2
Run on Kaggle with: GPU accelerator ON, Internet ON.
"""
from __future__ import annotations

# ── 0. Install pinned stack ────────────────────────────────────────────────────
import subprocess, sys

print(">>> Installing pinned GPU stack...")
subprocess.run([
    sys.executable, "-m", "pip", "install", "-q",
    "torch==2.5.1", "torchvision==0.20.1", "torchaudio==2.5.1",
    "xformers==0.0.28.post3",
    "--index-url", "https://download.pytorch.org/whl/cu121",
], check=True)
subprocess.run([
    sys.executable, "-m", "pip", "install", "-q",
    "transformers==4.48.2", "datasets>=3.0", "scikit-learn>=1.5",
], check=True)
print(">>> Stack installed.")

# ── 1. Imports ───────────────────────────��────────────────────────────────────
import logging
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from datasets import load_dataset                          # type: ignore
from sklearn.metrics import f1_score                       # type: ignore
from torch import nn
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModel, AutoTokenizer          # type: ignore

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ── 2. Config ─────────────────────────────────────────────────────────────────
@dataclass
class Config:
    # model
    model_name: str    = "chandar-lab/NeoBERT"
    revision: str      = "5424c8efeea6491b151d62dee55a752165407430"
    hidden_size: int   = 768
    head_dim: int      = 256
    dropout: float     = 0.1
    num_labels: int    = 12
    # data
    max_length: int    = 256
    # training  (§6.1 Step 1: 2 frozen + 2 unfrozen)
    epochs: int              = 4
    freeze_epochs: int       = 2
    batch_size: int          = 16
    lr_heads: float          = 2e-5
    lr_encoder: float        = 1e-5
    weight_decay: float      = 0.01
    fp16: bool               = True
    output_dir: str          = "/kaggle/working/checkpoints"

cfg = Config()

# ── 3. Taxonomy ───────────────────────────────────────────────────────────────
PEBBLE_LABELS = [
    "joy", "gratitude", "hope", "sadness", "frustration",
    "anxiety", "confusion", "loneliness", "exhaustion", "guilt", "calm", "neutral",
]
LABEL_TO_ID = {l: i for i, l in enumerate(PEBBLE_LABELS)}

GOEMOTIONS_TO_PEBBLE: dict[str, str] = {
    "joy": "joy",           "amusement": "joy",       "excitement": "joy",
    "admiration": "gratitude", "approval": "gratitude", "gratitude": "gratitude",
    "optimism": "hope",     "desire": "hope",
    "grief": "sadness",     "sadness": "sadness",      "disappointment": "sadness",
    "anger": "frustration", "annoyance": "frustration","disapproval": "frustration",
    "disgust": "frustration",
    "nervousness": "anxiety","fear": "anxiety",
    "confusion": "confusion","embarrassment": "confusion",
    "remorse": "guilt",
    "relief": "calm",       "caring": "calm",
    "love": "gratitude",    "pride": "joy",
    "neutral": "neutral",   "curiosity": "neutral",
    "realization": "neutral","surprise": "neutral",
}

def map_label(ge_label: str) -> str:
    return GOEMOTIONS_TO_PEBBLE.get(ge_label, "neutral")

# ── 4. Data ───────────────────────────────────────────────────────────────────
@dataclass
class Example:
    text: str
    label_id: int

def load_goemotions(split: str) -> list[Example]:
    ds = load_dataset("go_emotions", "simplified", split=split)
    label_names: list[str] = ds.features["labels"].feature.names
    examples = []
    for row in ds:
        primary = label_names[row["labels"][0]] if row["labels"] else "neutral"
        examples.append(Example(text=row["text"], label_id=LABEL_TO_ID[map_label(primary)]))
    return examples

class EmotionDataset(Dataset):
    def __init__(self, examples: list[Example], tokenizer, max_length: int):
        self.examples  = examples
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        ex = self.examples[idx]
        enc = self.tokenizer(
            ex.text, truncation=True, max_length=self.max_length,
            padding="max_length", return_tensors="pt",
        )
        return {
            "input_ids":      enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "label":          torch.tensor(ex.label_id, dtype=torch.long),
        }

# ── 5. Model ──────────────────────────────────────────────────────────────────
class EmotionHead(nn.Module):
    def __init__(self, hidden: int, num_labels: int, head_dim: int, dropout: float):
        super().__init__()
        self.net = nn.Sequential(
            nn.Dropout(dropout), nn.Linear(hidden, head_dim),
            nn.GELU(),
            nn.Dropout(dropout), nn.Linear(head_dim, num_labels),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

class EmotionClassifier(nn.Module):
    def __init__(self, c: Config):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(
            c.model_name, revision=c.revision, trust_remote_code=True,
        )
        self.head = EmotionHead(c.hidden_size, c.num_labels, c.head_dim, c.dropout)

    def set_encoder_trainable(self, trainable: bool) -> None:
        for p in self.encoder.parameters():
            p.requires_grad = trainable

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls = out.last_hidden_state[:, 0, :]
        return self.head(cls)

# ── 6. Eval helper ────────────────────────────────────────────────────────────
def evaluate(model: EmotionClassifier, loader: DataLoader, device: torch.device) -> float:
    model.eval()
    preds, labels = [], []
    with torch.no_grad():
        for batch in loader:
            logits = model(batch["input_ids"].to(device), batch["attention_mask"].to(device))
            preds.append(logits.argmax(-1).cpu().numpy())
            labels.append(batch["label"].numpy())
    return float(f1_score(np.concatenate(labels), np.concatenate(preds), average="macro"))

# ── 7. Training loop ──────────────────────────────────────────────────────────
def train(c: Config) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_fp16 = c.fp16 and device.type == "cuda"
    out = Path(c.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    log.info("Device: %s | fp16: %s", device, use_fp16)
    log.info("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        c.model_name, revision=c.revision, trust_remote_code=True,
    )

    log.info("Loading GoEmotions...")
    train_ds = EmotionDataset(load_goemotions("train"),      tokenizer, c.max_length)
    val_ds   = EmotionDataset(load_goemotions("validation"), tokenizer, c.max_length)
    train_loader = DataLoader(train_ds, batch_size=c.batch_size, shuffle=True,  num_workers=2, pin_memory=True)
    val_loader   = DataLoader(val_ds,   batch_size=c.batch_size * 2, shuffle=False, num_workers=2, pin_memory=True)
    log.info("Train: %d examples | Val: %d examples", len(train_ds), len(val_ds))

    log.info("Loading NeoBERT...")
    model = EmotionClassifier(c).to(device)
    scaler = torch.amp.GradScaler("cuda", enabled=use_fp16)

    optimizer = None
    best_f1 = 0.0

    for epoch in range(c.epochs):
        # ── Phase transition: rebuild optimizer ──
        if epoch == 0:
            model.set_encoder_trainable(False)
            optimizer = AdamW(model.head.parameters(), lr=c.lr_heads, weight_decay=c.weight_decay)
            log.info("Epoch %d: encoder FROZEN  (lr=%.1e)", epoch, c.lr_heads)
        elif epoch == c.freeze_epochs:
            model.set_encoder_trainable(True)
            optimizer = AdamW([
                {"params": model.encoder.parameters(), "lr": c.lr_encoder},
                {"params": model.head.parameters(),    "lr": c.lr_heads},
            ], weight_decay=c.weight_decay)
            log.info("Epoch %d: encoder UNFROZEN (lr_enc=%.1e lr_head=%.1e)", epoch, c.lr_encoder, c.lr_heads)

        # ── Train ──
        model.train()
        total_loss = 0.0
        for batch in train_loader:
            ids  = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            lbls = batch["label"].to(device)

            with torch.autocast(device_type=device.type, enabled=use_fp16):
                loss = F.cross_entropy(model(ids, mask), lbls)

            optimizer.zero_grad()
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        val_f1   = evaluate(model, val_loader, device)

        log.info("Epoch %d/%d | loss=%.4f | val_macro_f1=%.4f", epoch + 1, c.epochs, avg_loss, val_f1)

        ckpt = {"epoch": epoch, "state_dict": model.state_dict(), "val_f1": val_f1, "config": c}
        torch.save(ckpt, out / f"epoch_{epoch}.pt")

        if val_f1 > best_f1:
            best_f1 = val_f1
            torch.save(ckpt, out / "best.pt")
            log.info("  -> new best (val_macro_f1=%.4f) saved to %s/best.pt", best_f1, out)

    log.info("Done. Best val_macro_f1=%.4f | checkpoint: %s/best.pt", best_f1, out)

# ── 8. Run ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    train(cfg)
