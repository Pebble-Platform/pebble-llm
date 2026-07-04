"""Local CPU smoke for the voice backbone pilot — produces a REAL serving artifact.

Small subset of RAVDESS + a frozen WavLM-Base encoder + the multi-task probe
(emotion softmax + distress safety head), saved as the same artifact bundle the
Kaggle notebook emits, so src/pebble_llm/serving/voice_app.py can serve it.

This is the cheap local stand-in for the GPU Kaggle run (WavLM-Large + emotion2vec):
identical serving code path, smaller encoder + fewer clips.

    PYTHONPATH=src .venv-voice/bin/python scripts/voice_local_smoke.py
"""

from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torch.nn.functional as F
import torchaudio
from datasets import load_dataset
from sklearn.metrics import f1_score, precision_score, recall_score

from pebble_llm.models.heads import EmotionHead, SafetyHead

EMOTIONS = ["neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised"]
EMO2ID = {e: i for i, e in enumerate(EMOTIONS)}
DISTRESS = {"sad", "angry", "fearful", "disgust"}
SR, MAX_SEC = 16000, 4.0
MAX_SAMPLES = int(SR * MAX_SEC)
TRAIN_ACTORS, VAL_ACTORS = set(range(1, 13)), {21, 22, 23, 24}
RECALL_FLOOR, SAFETY_POS_WEIGHT = 0.90, 3.0


def parse_actor(ex) -> int:
    sid = ex.get("speaker_id")
    if isinstance(sid, str):
        d = "".join(c for c in sid if c.isdigit())
        return int(d) if d else -1
    return int(sid) if sid is not None else -1


def fix_len(w: np.ndarray) -> np.ndarray:
    return w[:MAX_SAMPLES] if len(w) >= MAX_SAMPLES else np.pad(w, (0, MAX_SAMPLES - len(w)))


def build_records_from_dir(ravdess_dir: str, max_train: int, max_val: int):
    """Load from a local RAVDESS extract; emotion + actor parsed from the filename
    (03-01-EE-II-SS-RR-AA.wav, EE=emotion 01..08, AA=actor 01..24)."""
    from glob import glob

    train, val = [], []
    files = sorted(glob(os.path.join(ravdess_dir, "**", "*.wav"), recursive=True))
    for path in files:
        parts = Path(path).stem.split("-")
        if len(parts) < 7:
            continue
        emo_idx, actor = int(parts[2]) - 1, int(parts[6])
        bucket = train if actor in TRAIN_ACTORS else (val if actor in VAL_ACTORS else None)
        if bucket is None or len(bucket) >= (max_train if bucket is train else max_val):
            continue
        wav, sr = sf.read(path, dtype="float32", always_2d=True)
        wav = wav.mean(axis=1)
        if sr != SR:
            wav = torchaudio.functional.resample(torch.from_numpy(wav), sr, SR).numpy()
        wav = fix_len(wav.astype(np.float32))
        emo = EMOTIONS[emo_idx]
        bucket.append({"wav": wav, "emo": emo_idx, "distress": int(emo in DISTRESS)})
    return train, val


def build_records(max_train: int, max_val: int):
    ds = load_dataset("narad/ravdess", split="train", trust_remote_code=True)
    int2str = ds.features["labels"].int2str
    train, val = [], []
    for ex in ds:
        actor = parse_actor(ex)
        bucket = train if actor in TRAIN_ACTORS else (val if actor in VAL_ACTORS else None)
        if bucket is None:
            continue
        cap = max_train if bucket is train else max_val
        if len(bucket) >= cap:
            continue
        a = ex["audio"]
        wav = np.asarray(a["array"], dtype=np.float32)
        if a["sampling_rate"] != SR:
            wav = torchaudio.functional.resample(torch.from_numpy(wav), a["sampling_rate"], SR).numpy()
        wav = fix_len(wav.astype(np.float32))
        emo = int2str(ex["labels"])
        bucket.append({"wav": wav, "emo": EMO2ID[emo], "distress": int(emo in DISTRESS)})
        if len(train) >= max_train and len(val) >= max_val:
            break
    return train, val


def extract(wavs, hf_id, dim):
    from transformers import AutoFeatureExtractor, WavLMModel

    fe = AutoFeatureExtractor.from_pretrained(hf_id)
    enc = WavLMModel.from_pretrained(hf_id).eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(wavs), 8):
            batch = wavs[i : i + 8]
            inp = fe(batch, sampling_rate=SR, return_tensors="pt", padding=True)
            out.append(enc(**inp).last_hidden_state.mean(dim=1).numpy())
            print(f"  extracted {min(i + 8, len(wavs))}/{len(wavs)}", end="\r")
    print()
    return np.concatenate(out, 0)


def threshold_at_recall(y, prob, floor):
    # highest threshold whose recall >= floor -> best precision while honoring the floor.
    best_t, best_p = 0.01, 0.0
    for t in np.linspace(0.01, 0.99, 99):
        pred = (prob >= t).astype(int)
        if recall_score(y, pred, zero_division=0) >= floor:
            best_t, best_p = float(t), precision_score(y, pred, zero_division=0)
    return float(best_t), float(best_p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone", default="microsoft/wavlm-base")
    ap.add_argument("--name", default="wavlm-base")
    ap.add_argument("--dim", type=int, default=768)
    ap.add_argument("--max-train", type=int, default=240)
    ap.add_argument("--max-val", type=int, default=96)
    ap.add_argument("--epochs", type=int, default=80)
    ap.add_argument("--seed", type=int, default=13)
    ap.add_argument("--out", default="artifacts/voice")
    ap.add_argument("--ravdess-dir", default=None, help="local RAVDESS extract (skips HF download)")
    args = ap.parse_args()

    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    print(f"[data] loading RAVDESS subset (train<= {args.max_train}, val<= {args.max_val})...")
    if args.ravdess_dir:
        train, val = build_records_from_dir(args.ravdess_dir, args.max_train, args.max_val)
    else:
        train, val = build_records(args.max_train, args.max_val)
    print(f"[data] train={len(train)} val={len(val)} "
          f"| train distress+={sum(r['distress'] for r in train)} "
          f"val distress+={sum(r['distress'] for r in val)}")

    print(f"[feat] frozen {args.backbone} on CPU...")
    Xtr = extract([r["wav"] for r in train], args.backbone, args.dim)
    Xva = extract([r["wav"] for r in val], args.backbone, args.dim)
    dim = Xtr.shape[1]

    emo_h, saf_h = EmotionHead(dim, len(EMOTIONS)), SafetyHead(dim)
    opt = torch.optim.AdamW(list(emo_h.parameters()) + list(saf_h.parameters()), lr=1e-3, weight_decay=1e-2)
    Xtr_t = torch.tensor(Xtr, dtype=torch.float)
    et = torch.tensor([r["emo"] for r in train], dtype=torch.long)
    dt = torch.tensor([r["distress"] for r in train], dtype=torch.float)
    pw = torch.tensor(SAFETY_POS_WEIGHT)
    for ep in range(args.epochs):
        emo_h.train(); saf_h.train(); opt.zero_grad()
        loss = F.cross_entropy(emo_h(Xtr_t), et) + F.binary_cross_entropy_with_logits(saf_h(Xtr_t), dt, pos_weight=pw)
        loss.backward(); opt.step()

    emo_h.eval(); saf_h.eval()
    with torch.no_grad():
        Xva_t = torch.tensor(Xva, dtype=torch.float)
        emo_pred = emo_h(Xva_t).argmax(-1).numpy()
        dis_prob = torch.sigmoid(saf_h(Xva_t)).numpy()
    emo_va = np.array([r["emo"] for r in val]); dis_va = np.array([r["distress"] for r in val])
    f1 = f1_score(emo_va, emo_pred, average="macro")
    rec = recall_score(dis_va, (dis_prob >= 0.5).astype(int), zero_division=0)
    thr, prec = threshold_at_recall(dis_va, dis_prob, RECALL_FLOOR)
    print(f"[eval] emo_macroF1={f1:.4f} distress_recall@0.5={rec:.3f} "
          f"precision@recall{RECALL_FLOOR}={prec:.3f} (thr={thr:.2f})")

    d = Path(args.out) / f"artifact_{args.name}"
    d.mkdir(parents=True, exist_ok=True)
    torch.save(emo_h.state_dict(), d / "emotion_head.pt")
    torch.save(saf_h.state_dict(), d / "safety_head.pt")
    json.dump({"backbone_hf_id": args.backbone, "backbone": args.name, "embed_dim": dim,
               "emotions": EMOTIONS, "distress_emotions": sorted(DISTRESS),
               "safety_threshold": thr, "recall_floor": RECALL_FLOOR, "sample_rate": SR,
               "max_samples": MAX_SAMPLES, "pooling": "mean", "head_dim": 256, "safety_head_dim": 64,
               "source": "local_smoke"}, open(d / "config.json", "w"), indent=2)
    sf.write(d / "sample_val.wav", val[0]["wav"], SR)
    print(f"[save] artifact bundle -> {d} (+ sample_val.wav, emo={EMOTIONS[val[0]['emo']]})")


if __name__ == "__main__":
    main()
