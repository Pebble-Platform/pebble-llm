"""Reimplementation — "Hierarchical Dual-Head Model for Suicide Risk Assessment via MentalRoBERTa"
(Yang et al., IEEE BigData 2025; arXiv:2510.20085).

Self-contained single file: runs on Kaggle (GPU + Internet ON) and locally (CPU smoke).
Method spec: docs/papers/finetuning-message/R2-DEEP-method-and-repro-vi.md

Dataset: Reddit C-SSRS 500 users (Gaur et al., Zenodo 2667859, CC-BY-4.0) — public stand-in for the
gated HKIE benchmark. 5 C-SSRS labels → paper's 4 ordinal levels (drop "Supportive";
Indicator/Ideation/Behavior/Attempt → 0/1/2/3). No timestamps → Δt=0.

Local smoke:   R2_SMOKE=1 R2_MODEL=prajjwal1/bert-tiny .venv-voice/bin/python notebooks/r2-suicide-risk-dualhead.py
Kaggle:        upload as script kernel, GPU + Internet ON, run.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

IS_KAGGLE = Path("/kaggle").exists()

# Kaggle run: gold-holdout eval on the enriched 10k by default (set before Config reads the env).
# Cap epochs at 10 (early stopping usually triggers earlier; keeps the 5-fold run under Kaggle's 12h GPU cap).
if IS_KAGGLE:
    os.environ.setdefault("R2_GOLD_HOLDOUT", "1")
    os.environ.setdefault("R2_EPOCHS", "10")

# ── 0. Pinned GPU stack (Kaggle only; local uses .venv-voice) ───────────────────
if IS_KAGGLE:
    import subprocess
    print(">>> Installing validated GPU stack (torch 2.5.1 + cu121) ...", flush=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "torch==2.5.1", "torchvision==0.20.1", "torchaudio==2.5.1",
                    "--index-url", "https://download.pytorch.org/whl/cu121"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "transformers==4.48.2", "scikit-learn>=1.3", "nltk>=3.8"], check=True)

import ast
import csv
import math
import random
import urllib.request
from dataclasses import dataclass

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import cohen_kappa_score, f1_score
from sklearn.model_selection import StratifiedKFold
from torch.utils.data import DataLoader, Dataset
from transformers import AutoConfig, AutoModel, AutoTokenizer

csv.field_size_limit(10**7)


# ── 1. Config ───────────────────────────────────────────────────────────────────
@dataclass
class Config:
    # NOTE: the original mental/mental-roberta-base is now a GATED HF repo (401 without a token).
    # We use a public mirror whose base encoder = MentalRoBERTa weights (a downstream-finetuned
    # checkpoint; AutoModel loads the roberta.* base and drops its classifier head). Faithful-enough
    # backbone. Override with R2_MODEL. See R2-DEEP-method-and-repro-vi.md §6.
    model_name: str = os.environ.get("R2_MODEL", "welsachy/mental-roberta-base-finetuned-depression")
    smoke: bool = bool(int(os.environ.get("R2_SMOKE", "0")))
    # gold-holdout: train on LLM-labeled pool (av9ash+scraped), eval folds on clinical CSSRS-500 test
    gold_holdout: bool = bool(int(os.environ.get("R2_GOLD_HOLDOUT", "0")))
    # data
    seq_len: int = 5                 # posts per user-sequence (paper: 5)
    max_length: int = 256            # tokens/post (paper: 512; reduced for speed)
    n_classes: int = 4
    data_url: str = ("https://zenodo.org/api/records/2667859/files/"
                     "500_Reddit_users_posts_labels.csv/content")
    # architecture
    freeze_layers: int = 6           # freeze embeddings + first 6 encoder layers (paper: 50%)
    n_transformer_layers: int = 3
    n_heads: int = 8                 # sequence transformer heads
    ffn_dim: int = 3072
    pool_heads: int = 4              # attention-pooling heads
    use_features: bool = True
    dropout: float = 0.3
    # loss weights (paper eq. 4)
    w_coral: float = 0.5
    w_ce: float = 0.3
    w_focal: float = 0.2
    label_smoothing: float = 0.1
    focal_gamma: float = 2.0
    # training
    lr_encoder: float = 2e-5
    lr_new: float = 1e-4
    weight_decay: float = 0.01
    batch_size: int = 8
    grad_accum: int = 2              # effective batch 16
    epochs: int = int(os.environ.get("R2_EPOCHS", "15"))
    warmup_ratio: float = 0.1
    patience: int = 5
    n_folds: int = 5
    max_grad_norm: float = 1.0
    aug_prob: float = 0.5            # text augmentation prob per post (train only)
    seed: int = 42
    output_dir: str = "/kaggle/working" if IS_KAGGLE else "./r2_out"

    def __post_init__(self):
        if self.smoke:                # tiny end-to-end wiring check on CPU
            self.max_length = 32
            self.seq_len = 3
            self.epochs = 1
            self.n_folds = 2
            self.batch_size = 2
            self.freeze_layers = 1


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
LABEL_MAP = {"Indicator": 0, "Ideation": 1, "Behavior": 2, "Attempt": 3}  # drop "Supportive"
LABEL_NAMES = ["Indicator", "Ideation", "Behavior", "Attempt"]


def set_seed(s: int):
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)


# ── 2. Data ──────────────────────────────────────────────────────────────────────
def _parse_posts(cell: str) -> list[str]:
    """CSSRS 'Post' column is a python-list-as-string. 28/500 fail literal_eval (escapes)
    → fall back to the raw cell as a single post."""
    try:
        v = ast.literal_eval(cell)
        if isinstance(v, list) and v:
            return [str(x) for x in v if str(x).strip()]
    except Exception:
        pass
    return [cell.strip("[]")]


def load_cssrs(cfg: Config) -> tuple[list[list[str]], list[int]]:
    # R2_DATA lets us point the loader at the enriched combined set (same User,Post,Label schema)
    local = Path(os.environ.get("R2_DATA", "data/finetuning-message/external/cssrs/500_Reddit_users_posts_labels.csv"))
    cache = Path(cfg.output_dir) / "cssrs500.csv"
    if local.exists():
        path = local
    else:
        Path(cfg.output_dir).mkdir(parents=True, exist_ok=True)
        if not cache.exists():
            print(">>> Downloading CSSRS-500 from Zenodo ...", flush=True)
            urllib.request.urlretrieve(cfg.data_url, cache)
        path = cache

    seqs, labels = [], []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            lab = row["Label"].strip()
            if lab not in LABEL_MAP:          # skip "Supportive"
                continue
            posts = _parse_posts(row["Post"])
            if not posts:
                continue
            posts = posts[-cfg.seq_len:]      # last `seq_len` posts (most recent)
            seqs.append(posts)
            labels.append(LABEL_MAP[lab])
    if cfg.smoke:
        seqs, labels = seqs[:12], labels[:12]
    return seqs, labels


def _combined_path(cfg: Config) -> Path:
    """Resolve the enriched combined CSV: R2_DATA env → Kaggle input dir → local r2-combined."""
    if os.environ.get("R2_DATA"):
        return Path(os.environ["R2_DATA"])
    for p in Path("/kaggle/input").glob("*/sequences.csv") if Path("/kaggle/input").exists() else []:
        return p
    return Path("data/finetuning-message/external/r2-combined/sequences.csv")


def load_combined(cfg: Config) -> tuple[list[list[str]], list[int], list[str]]:
    """Load the combined set WITH source tags (User,Post,Label,Source). Source ∈ {cssrs500, av9ash, scraped}."""
    path = _combined_path(cfg)
    seqs, labels, sources = [], [], []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            lab = row["Label"].strip()
            if lab not in LABEL_MAP:
                continue
            posts = _parse_posts(row["Post"])[-cfg.seq_len:]
            if not posts:
                continue
            seqs.append(posts)
            labels.append(LABEL_MAP[lab])
            sources.append(row.get("Source", "unknown"))
    return seqs, labels, sources


# --- text augmentation (train only); paper §III: deletion / swap / synonym -------
_WORDNET = None
def _get_wordnet():
    global _WORDNET
    if _WORDNET is None:
        try:
            import nltk
            from nltk.corpus import wordnet
            try:
                wordnet.ensure_loaded()
            except LookupError:
                nltk.download("wordnet", quiet=True)
            _WORDNET = wordnet
        except Exception:
            _WORDNET = False
    return _WORDNET


def augment(text: str) -> str:
    words = text.split()
    if len(words) < 4:
        return text
    op = random.choice(["delete", "swap", "synonym"])
    if op == "delete":
        keep = [w for w in words if random.random() > 0.10]
        return " ".join(keep) if keep else text
    if op == "swap":
        i, j = random.sample(range(len(words)), 2)
        words[i], words[j] = words[j], words[i]
        return " ".join(words)
    wn = _get_wordnet()                        # synonym replacement
    if not wn:
        return text
    out = list(words)
    for idx in range(len(out)):
        if random.random() < 0.10:
            syns = wn.synsets(out[idx])
            lemmas = {l.name().replace("_", " ") for s in syns for l in s.lemmas()
                      if l.name().lower() != out[idx].lower()}
            if lemmas:
                out[idx] = random.choice(list(lemmas))
    return " ".join(out)


def stat_features(posts: list[str], seq_len: int) -> np.ndarray:
    """post-length stats (mean/std/min/max words) + time-interval stats (all 0, no timestamps)."""
    wc = [len(p.split()) for p in posts] or [0]
    pad = [0.0, 0.0, 0.0, 0.0]                  # time-interval stats unavailable → zeros
    return np.array([np.mean(wc), np.std(wc), np.min(wc), np.max(wc), *pad], dtype=np.float32)


class CSSRSDataset(Dataset):
    def __init__(self, seqs, labels, tok, cfg: Config, train: bool):
        self.seqs, self.labels, self.tok, self.cfg, self.train = seqs, labels, tok, cfg, train

    def __len__(self):
        return len(self.seqs)

    def __getitem__(self, i):
        posts = list(self.seqs[i])
        if self.train and random.random() < self.cfg.aug_prob:
            posts = [augment(p) for p in posts]
        n = len(posts)
        posts = posts + [""] * (self.cfg.seq_len - n)        # pad to seq_len
        enc = self.tok(posts, truncation=True, max_length=self.cfg.max_length,
                       padding="max_length", return_tensors="pt")
        mask_valid = torch.zeros(self.cfg.seq_len, dtype=torch.bool)
        mask_valid[:n] = True                                 # True = real post
        dt = torch.zeros(self.cfg.seq_len, dtype=torch.float32)  # Δt=0 (no timestamps)
        feats = torch.from_numpy(stat_features(self.seqs[i], self.cfg.seq_len))
        return {
            "input_ids": enc["input_ids"],                   # (seq_len, L)
            "attention_mask": enc["attention_mask"],
            "valid": mask_valid,
            "dt": dt,
            "feats": feats,
            "label": torch.tensor(self.labels[i], dtype=torch.long),
        }


# ── 3. Model ─────────────────────────────────────────────────────────────────────
class HierarchicalDualHead(nn.Module):
    def __init__(self, cfg: Config, pretrained: bool = True):
        super().__init__()
        self.cfg = cfg
        if pretrained:
            self.encoder = AutoModel.from_pretrained(cfg.model_name)
        else:
            self.encoder = AutoModel.from_config(AutoConfig.from_pretrained(cfg.model_name))
        h = self.encoder.config.hidden_size
        self.h = h
        self._freeze(cfg.freeze_layers)

        # temporal embedding: ReLU(LayerNorm(W·Δt + b))
        self.time_fc = nn.Linear(1, h)
        self.time_ln = nn.LayerNorm(h)
        self.time_drop = nn.Dropout(cfg.dropout)

        # 3-layer sequence transformer
        layer = nn.TransformerEncoderLayer(
            d_model=h, nhead=cfg.n_heads, dim_feedforward=cfg.ffn_dim,
            dropout=cfg.dropout, activation="gelu", batch_first=True)
        self.seq_encoder = nn.TransformerEncoder(layer, num_layers=cfg.n_transformer_layers)

        # attention pooling with learnable query
        self.query = nn.Parameter(torch.randn(1, 1, h) * 0.02)
        self.pool = nn.MultiheadAttention(h, cfg.pool_heads, dropout=cfg.dropout, batch_first=True)
        self.pool_drop = nn.Dropout(cfg.dropout)

        # optional statistical-feature fusion (8 → 64 → fuse)
        if cfg.use_features:
            self.feat_mlp = nn.Sequential(nn.Linear(8, 64), nn.ReLU(), nn.Linear(64, 64), nn.ReLU())
            self.fuse = nn.Linear(h + 64, h)

        # dual heads
        self.coral_fc = nn.Linear(h, 1, bias=False)               # shared weight w_c
        self.coral_bias = nn.Parameter(torch.zeros(cfg.n_classes - 1))  # ordered thresholds
        self.cls_head = nn.Linear(h, cfg.n_classes)

    def _freeze(self, k: int):
        for name, p in self.encoder.named_parameters():
            if name.startswith("embeddings"):
                p.requires_grad = False
            elif ".layer." in name:
                li = int(name.split(".layer.")[1].split(".")[0])
                if li < k:
                    p.requires_grad = False

    def encode_posts(self, input_ids, attention_mask):
        B, S, L = input_ids.shape
        out = self.encoder(input_ids=input_ids.view(B * S, L),
                           attention_mask=attention_mask.view(B * S, L))
        cls = out.last_hidden_state[:, 0]                          # (B*S, h)
        return cls.view(B, S, self.h)

    def forward(self, input_ids, attention_mask, valid, dt, feats):
        e = self.encode_posts(input_ids, attention_mask)          # (B,S,h)
        e_time = self.time_drop(F.relu(self.time_ln(self.time_fc(dt.unsqueeze(-1)))))
        e = e + e_time
        pad_mask = ~valid                                         # True = pad (ignored)
        s = self.seq_encoder(e, src_key_padding_mask=pad_mask)    # (B,S,h)
        q = self.query.expand(e.size(0), -1, -1)
        u, _ = self.pool(q, s, s, key_padding_mask=pad_mask)      # (B,1,h)
        u = self.pool_drop(u.squeeze(1))                          # (B,h)
        if self.cfg.use_features:
            f = self.feat_mlp(feats)
            u = self.fuse(torch.cat([u, f], dim=-1))
        coral_logits = self.coral_fc(u) + self.coral_bias        # (B, n_classes-1)
        cls_logits = self.cls_head(u)                            # (B, n_classes)
        return coral_logits, cls_logits


# ── 4. Losses (tri-objective, paper eq. 4) ───────────────────────────────────────
def coral_loss(coral_logits, y, n_classes):
    # binary targets t_k = 1[y > k]
    levels = torch.arange(n_classes - 1, device=y.device).unsqueeze(0)
    t = (y.unsqueeze(1) > levels).float()
    return F.binary_cross_entropy_with_logits(coral_logits, t)


def focal_loss(cls_logits, y, alpha, gamma):
    logp = F.log_softmax(cls_logits, dim=-1)
    p = logp.exp()
    logp_y = logp.gather(1, y.unsqueeze(1)).squeeze(1)
    p_y = p.gather(1, y.unsqueeze(1)).squeeze(1)
    a = alpha[y]
    return (-a * (1 - p_y) ** gamma * logp_y).mean()


def coral_to_probs(coral_logits, n_classes):
    """cumulative P(y>k) → per-class probabilities."""
    pgt = torch.sigmoid(coral_logits)                            # (B, K-1) = P(y>k)
    B = coral_logits.size(0)
    probs = torch.zeros(B, n_classes, device=coral_logits.device)
    probs[:, 0] = 1 - pgt[:, 0]
    for k in range(1, n_classes - 1):
        probs[:, k] = pgt[:, k - 1] - pgt[:, k]
    probs[:, -1] = pgt[:, -1]
    return probs.clamp_min(1e-6)


# ── 5. Train / eval one fold ─────────────────────────────────────────────────────
def make_optim(model, cfg, total_steps):
    enc, new = [], []
    for n, p in model.named_parameters():
        if not p.requires_grad:
            continue
        (enc if n.startswith("encoder.") else new).append(p)
    opt = torch.optim.AdamW(
        [{"params": enc, "lr": cfg.lr_encoder}, {"params": new, "lr": cfg.lr_new}],
        weight_decay=cfg.weight_decay)
    warmup = int(cfg.warmup_ratio * total_steps)

    def lr_lambda(step):
        if step < warmup:
            return step / max(1, warmup)
        prog = (step - warmup) / max(1, total_steps - warmup)
        return 0.5 * (1 + math.cos(math.pi * prog))
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lr_lambda)
    return opt, sched


@torch.no_grad()
def evaluate(model, loader, cfg):
    model.eval()
    preds, gts = [], []
    for b in loader:
        coral, cls = model(b["input_ids"].to(DEVICE), b["attention_mask"].to(DEVICE),
                           b["valid"].to(DEVICE), b["dt"].to(DEVICE), b["feats"].to(DEVICE))
        p_final = 0.5 * coral_to_probs(coral, cfg.n_classes) + 0.5 * F.softmax(cls, dim=-1)
        preds.extend(p_final.argmax(-1).cpu().tolist())
        gts.extend(b["label"].tolist())
    f1 = f1_score(gts, preds, average="macro", zero_division=0)
    mae = float(np.mean(np.abs(np.array(preds) - np.array(gts))))
    qwk = cohen_kappa_score(gts, preds, weights="quadratic", labels=[0, 1, 2, 3])
    return {"macro_f1": f1, "mae": mae, "qwk": float(qwk if qwk == qwk else 0.0)}


def train_fold(cfg, tr_seq, tr_lab, va_seq, va_lab, tok, fold):
    model = HierarchicalDualHead(cfg, pretrained=True).to(DEVICE)
    tr = DataLoader(CSSRSDataset(tr_seq, tr_lab, tok, cfg, train=True),
                    batch_size=cfg.batch_size, shuffle=True)
    va = DataLoader(CSSRSDataset(va_seq, va_lab, tok, cfg, train=False),
                    batch_size=cfg.batch_size)
    counts = np.bincount(tr_lab, minlength=cfg.n_classes).astype(np.float32)
    alpha = torch.tensor(counts.sum() / (cfg.n_classes * np.maximum(counts, 1)),
                         dtype=torch.float32, device=DEVICE)
    total_steps = math.ceil(len(tr) / cfg.grad_accum) * cfg.epochs
    opt, sched = make_optim(model, cfg, total_steps)
    use_amp = DEVICE.type == "cuda"
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)

    best, best_state, bad = -1.0, None, 0
    for epoch in range(cfg.epochs):
        model.train(); opt.zero_grad()
        for step, b in enumerate(tr):
            with torch.autocast(device_type=DEVICE.type, enabled=use_amp):
                coral, cls = model(b["input_ids"].to(DEVICE), b["attention_mask"].to(DEVICE),
                                   b["valid"].to(DEVICE), b["dt"].to(DEVICE), b["feats"].to(DEVICE))
                y = b["label"].to(DEVICE)
                loss = (cfg.w_coral * coral_loss(coral, y, cfg.n_classes)
                        + cfg.w_ce * F.cross_entropy(cls, y, label_smoothing=cfg.label_smoothing)
                        + cfg.w_focal * focal_loss(cls, y, alpha, cfg.focal_gamma))
                loss = loss / cfg.grad_accum
            scaler.scale(loss).backward()
            if (step + 1) % cfg.grad_accum == 0:
                scaler.unscale_(opt)
                nn.utils.clip_grad_norm_(model.parameters(), cfg.max_grad_norm)
                scaler.step(opt); scaler.update(); sched.step(); opt.zero_grad()
        m = evaluate(model, va, cfg)
        print(f"  [fold {fold}] epoch {epoch}: macroF1={m['macro_f1']:.4f} "
              f"MAE={m['mae']:.4f} QWK={m['qwk']:.4f}", flush=True)
        if m["macro_f1"] > best:
            best, best_state, bad = m["macro_f1"], {k: v.cpu() for k, v in model.state_dict().items()}, 0
        else:
            bad += 1
            if bad >= cfg.patience:
                print(f"  [fold {fold}] early stop @ epoch {epoch}", flush=True)
                break
    return best, best_state


# ── 6. Main ──────────────────────────────────────────────────────────────────────
def run_gold_holdout(cfg: Config, tok, out: Path):
    """Train on the LLM-labeled pool (av9ash+scraped) with 5-fold CV; evaluate every fold's best model on the
    held-out clinical gold set (CSSRS-500). The gold metrics are the honest, non-circular numbers."""
    seqs, labels, sources = load_combined(cfg)
    labels = np.array(labels); sources = np.array(sources)
    gold = sources == "cssrs500"
    g_seq = [s for s, k in zip(seqs, gold) if k]; g_lab = labels[gold]
    p_seq = [s for s, k in zip(seqs, gold) if not k]; p_lab = labels[~gold]
    if cfg.smoke:
        g_seq, g_lab = g_seq[:8], g_lab[:8]; p_seq, p_lab = p_seq[:16], p_lab[:16]
    print(f">>> GOLD-HOLDOUT | test(gold)={len(g_seq)} {np.bincount(g_lab, minlength=4).tolist()} | "
          f"train-pool={len(p_seq)} {np.bincount(p_lab, minlength=4).tolist()} ({LABEL_NAMES})", flush=True)

    gold_loader = DataLoader(CSSRSDataset(g_seq, list(g_lab), tok, cfg, train=False), batch_size=cfg.batch_size)
    skf = StratifiedKFold(n_splits=cfg.n_folds, shuffle=True, random_state=cfg.seed)
    gold_f1, val_f1, best_g, best_state = [], [], -1.0, None
    for fold, (tr_idx, va_idx) in enumerate(skf.split(p_seq, p_lab)):
        tr_seq = [p_seq[i] for i in tr_idx]; tr_lab = p_lab[tr_idx].tolist()
        va_seq = [p_seq[i] for i in va_idx]; va_lab = p_lab[va_idx].tolist()
        f1v, state = train_fold(cfg, tr_seq, tr_lab, va_seq, va_lab, tok, fold)
        model = HierarchicalDualHead(cfg, pretrained=False).to(DEVICE)
        model.load_state_dict(state)
        gm = evaluate(model, gold_loader, cfg)
        val_f1.append(f1v); gold_f1.append(gm["macro_f1"])
        print(f">>> [fold {fold}] val-macroF1(LLM)={f1v:.4f} | GOLD macroF1={gm['macro_f1']:.4f} "
              f"MAE={gm['mae']:.4f} QWK={gm['qwk']:.4f}", flush=True)
        if gm["macro_f1"] > best_g:
            best_g, best_state = gm["macro_f1"], state
        if cfg.smoke:
            break

    print(f">>> GOLD test macro-F1: mean={np.mean(gold_f1):.4f} std={np.std(gold_f1):.4f} "
          f"folds={[round(x,4) for x in gold_f1]}", flush=True)
    print(f">>> (val-on-LLM macro-F1: mean={np.mean(val_f1):.4f} folds={[round(x,4) for x in val_f1]})", flush=True)
    ckpt = {"state_dict": best_state, "model_name": cfg.model_name, "n_classes": cfg.n_classes,
            "use_features": cfg.use_features, "label_names": LABEL_NAMES,
            "gold_macro_f1": float(np.mean(gold_f1))}
    torch.save(ckpt, out / "best_model.pt")
    print(f">>> saved {out/'best_model.pt'}  (best GOLD macro-F1={best_g:.4f})", flush=True)


def main():
    cfg = Config()
    set_seed(cfg.seed)
    out = Path(cfg.output_dir); out.mkdir(parents=True, exist_ok=True)
    print(f">>> device={DEVICE} model={cfg.model_name} smoke={cfg.smoke} gold_holdout={cfg.gold_holdout}", flush=True)
    if cfg.gold_holdout:
        run_gold_holdout(cfg, AutoTokenizer.from_pretrained(cfg.model_name), out)
        return

    seqs, labels = load_cssrs(cfg)
    labels = np.array(labels)
    print(f">>> {len(seqs)} sequences | class counts={np.bincount(labels).tolist()} "
          f"({LABEL_NAMES})", flush=True)
    tok = AutoTokenizer.from_pretrained(cfg.model_name)

    skf = StratifiedKFold(n_splits=cfg.n_folds, shuffle=True, random_state=cfg.seed)
    fold_metrics, best_overall, best_overall_state = [], -1.0, None
    for fold, (tr_idx, va_idx) in enumerate(skf.split(seqs, labels)):
        tr_seq = [seqs[i] for i in tr_idx]; tr_lab = labels[tr_idx].tolist()
        va_seq = [seqs[i] for i in va_idx]; va_lab = labels[va_idx].tolist()
        f1, state = train_fold(cfg, tr_seq, tr_lab, va_seq, va_lab, tok, fold)
        fold_metrics.append(f1)
        if f1 > best_overall:
            best_overall, best_overall_state = f1, state
        if cfg.smoke:
            break

    print(f">>> CV macro-F1: mean={np.mean(fold_metrics):.4f} "
          f"std={np.std(fold_metrics):.4f} folds={[round(x,4) for x in fold_metrics]}", flush=True)

    ckpt = {"state_dict": best_overall_state, "model_name": cfg.model_name,
            "n_classes": cfg.n_classes, "use_features": cfg.use_features,
            "label_names": LABEL_NAMES, "cv_macro_f1": float(np.mean(fold_metrics))}
    torch.save(ckpt, out / "best_model.pt")
    print(f">>> saved {out/'best_model.pt'}  (best fold macro-F1={best_overall:.4f})", flush=True)


if __name__ == "__main__":
    main()
