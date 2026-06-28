"""Direction A — post-hoc LABEL-SHIFT correction (0 GPU, local CPU).

Loads a saved checkpoint (default: the flat-CE ablation, which has the most 'room' on Behavior),
runs inference on the 392 clinical gold (CSSRS-500) sequences, then applies — WITHOUT retraining —
  (1) Logit Adjustment (Menon et al. ICLR'21):   adj_logit_k = logit_k - tau * log(pi_train_k)
  (2) SLD-EM prior correction (Saerens et al. '02): EM on the posterior to estimate the target prior
  (3) Oracle (uses the TRUE gold prior pi_gold) — upper bound on what shift-correction can recover.

Why: P_train(y) (LLM pool) != P_gold(y) (clinical). Behavior is ~7% of the pool but ~20% of gold
(under-labelled ~2.7x). Correcting this systematic label shift should recover macro-F1 / Behavior-F1.

Run:
  R2_DATA=kaggle/finetuning-message/r2-cssrs-combined-dataset/sequences.csv \
  R2_CKPT=kaggle/finetuning-message/r2-ablation/out/best_model.pt \
  .venv-voice/bin/python kaggle/finetuning-message/r2-label-shift/posthoc_label_shift.py
"""
import importlib.util
import os
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader

# default local data + checkpoint
os.environ.setdefault("R2_DATA", "kaggle/finetuning-message/r2-cssrs-combined-dataset/sequences.csv")
os.environ.setdefault("R2_GOLD_HOLDOUT", "1")
CKPT = os.environ.get("R2_CKPT", "kaggle/finetuning-message/r2-ablation/out/best_model.pt")

# import the kernel module (Config / model / data loaders) by file path
KPATH = "kaggle/finetuning-message/r2-ablation/r2-ablation.py"
spec = importlib.util.spec_from_file_location("r2k", KPATH)
m = importlib.util.module_from_spec(spec)
sys.modules["r2k"] = m
spec.loader.exec_module(m)

LABELS = ["Indicator", "Ideation", "Behavior", "Attempt"]
BEH = 2


def macro_and_beh(y_true, y_pred):
    f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    per = f1_score(y_true, y_pred, average=None, labels=[0, 1, 2, 3], zero_division=0)
    return f1, per


def sld_em(p0, pi_train, n_iter=100, tol=1e-7):
    """Saerens-Latinne-Decaestecker EM: estimate target prior from posterior p0, return corrected q."""
    pi = np.full(p0.shape[1], 1.0 / p0.shape[1])
    for _ in range(n_iter):
        w = pi / pi_train
        q = p0 * w
        q /= q.sum(1, keepdims=True)
        new = q.mean(0)
        if np.abs(new - pi).max() < tol:
            pi = new
            break
        pi = new
    w = pi / pi_train
    q = p0 * w
    q /= q.sum(1, keepdims=True)
    return q, pi


def main():
    cfg = m.Config()
    cfg.gold_holdout = True
    print(f">>> model={cfg.model_name}  ckpt={CKPT}", flush=True)

    seqs, labels, sources = m.load_combined(cfg)
    labels = np.array(labels); sources = np.array(sources)
    gold = sources == "cssrs500"
    g_seq = [s for s, k in zip(seqs, gold) if k]
    g_lab = labels[gold]
    pool_lab = labels[~gold]
    pi_train = np.bincount(pool_lab, minlength=4).astype(np.float64); pi_train /= pi_train.sum()
    pi_gold = np.bincount(g_lab, minlength=4).astype(np.float64); pi_gold /= pi_gold.sum()
    print(f">>> gold={len(g_seq)} {np.bincount(g_lab, minlength=4).tolist()}  "
          f"pool-train={len(pool_lab)} {np.bincount(pool_lab, minlength=4).tolist()}", flush=True)
    print(f">>> pi_train={np.round(pi_train,3).tolist()}  pi_gold={np.round(pi_gold,3).tolist()}  "
          f"shift w(y)=pi_gold/pi_train={np.round(pi_gold/pi_train,2).tolist()}", flush=True)

    # build model (no 500MB download: random encoder via config, then load saved weights)
    model = m.HierarchicalDualHead(cfg, pretrained=False)
    ckpt = torch.load(CKPT, map_location="cpu")
    sd = ckpt["state_dict"] if "state_dict" in ckpt else ckpt
    missing, unexpected = model.load_state_dict(sd, strict=False)
    print(f">>> loaded ckpt (missing={len(missing)} unexpected={len(unexpected)})", flush=True)
    model.eval()

    # inference: collect CE-head logits over the 392 gold
    loader = DataLoader(m.CSSRSDataset(g_seq, list(g_lab), m.AutoTokenizer.from_pretrained(cfg.model_name),
                                       cfg, train=False), batch_size=cfg.batch_size)
    cls_logits, gts = [], []
    with torch.no_grad():
        for b in loader:
            _, cls = model(b["input_ids"], b["attention_mask"], b["valid"], b["dt"], b["feats"])
            cls_logits.append(cls.cpu().numpy()); gts.extend(b["label"].tolist())
    cls_logits = np.concatenate(cls_logits, 0)
    gts = np.array(gts)
    p0 = torch.softmax(torch.from_numpy(cls_logits), dim=-1).numpy()

    rows = []
    # baseline (flat-CE = CE head only)
    f1, per = macro_and_beh(gts, p0.argmax(1))
    rows.append(("baseline (no correction)", f1, per[BEH], per))

    # (1) Logit Adjustment, tau sweep
    log_pt = np.log(pi_train)
    for tau in (0.5, 1.0, 1.5):
        adj = cls_logits - tau * log_pt
        pred = adj.argmax(1)
        f1, per = macro_and_beh(gts, pred)
        rows.append((f"logit-adjust tau={tau}", f1, per[BEH], per))

    # (2) SLD-EM (estimates target prior from the gold inputs; no gold labels used)
    q, pi_hat = sld_em(p0, pi_train)
    f1, per = macro_and_beh(gts, q.argmax(1))
    rows.append((f"SLD-EM (pi_hat={np.round(pi_hat,3).tolist()})", f1, per[BEH], per))

    # (3) Oracle: use the TRUE gold prior (upper bound)
    w = pi_gold / pi_train
    q_or = p0 * w; q_or /= q_or.sum(1, keepdims=True)
    f1, per = macro_and_beh(gts, q_or.argmax(1))
    rows.append(("ORACLE (true pi_gold)", f1, per[BEH], per))

    print("\n=== Direction A — post-hoc label-shift correction (gold-holdout, flat-CE ckpt) ===")
    print(f"{'method':<34} {'macroF1':>8} {'BehF1':>7}   per-class[Ind,Idea,Beh,Att]")
    for name, f1, beh, per in rows:
        print(f"{name:<34} {f1:>8.4f} {beh:>7.4f}   {[round(float(x),3) for x in per]}")
    print("\n(neo: flat-CE baseline ~0.4215 / Behavior ~0.285 ; dual-head 0.3849 / 0.183)")


if __name__ == "__main__":
    main()
