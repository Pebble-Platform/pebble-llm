"""Local MFCC feature extractor (no GPU) — the non-SSL baseline arm (VNEMOS-line).

Per utt: MFCC(20) + delta + delta2 over 16 kHz mono, pooled to mean+std over time
=> a fixed 120-d utterance vector. Cached as an id-keyed .npz the runner aligns to
the split folds. Runs locally in .venv-vnser (torchaudio + the soundfile shim);
no Kaggle quota needed.

Usage:  PYTHONPATH=scripts/vietnamese-ser python .../extract_mfcc.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio

REPO = Path(__file__).resolve().parents[3]
KAGGLE = REPO / "data/vietnamese-ser/kaggle-upload/viemospeech-pilot"
OUT = REPO / "data/vietnamese-ser/benchmark/features/mfcc.npz"
SR = 16000

_mfcc = torchaudio.transforms.MFCC(
    sample_rate=SR, n_mfcc=20,
    melkwargs={"n_fft": 400, "hop_length": 160, "n_mels": 40},
)


def utt_vector(wav: np.ndarray) -> np.ndarray:
    x = torch.tensor(wav, dtype=torch.float32).unsqueeze(0)   # (1, T)
    m = _mfcc(x).squeeze(0)                                    # (20, frames)
    d1 = torchaudio.functional.compute_deltas(m)
    d2 = torchaudio.functional.compute_deltas(d1)
    feat = torch.cat([m, d1, d2], dim=0)                      # (60, frames)
    return torch.cat([feat.mean(1), feat.std(1)]).numpy()     # (120,)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    rows = list(csv.DictReader((KAGGLE / "manifest.csv").open(encoding="utf-8")))
    rows = [r for r in rows if r["is_clean"].lower() == "true"]
    ids, feats, missing = [], [], 0
    for i, r in enumerate(rows):
        wav_path = KAGGLE / r["clip"]
        if not wav_path.exists():
            missing += 1
            continue
        wav, sr = sf.read(wav_path)
        if wav.ndim > 1:
            wav = wav.mean(1)
        if sr != SR:
            wav = torchaudio.functional.resample(
                torch.tensor(wav, dtype=torch.float32), sr, SR).numpy()
        ids.append(f"{r['ep']}::{r['id']}")
        feats.append(utt_vector(wav.astype(np.float32)))
        if (i + 1) % 500 == 0:
            print(f"  {i + 1}/{len(rows)}")
    X = np.stack(feats).astype(np.float32)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez(OUT, ids=np.array(ids), X=X)
    print(f"wrote {OUT.relative_to(REPO)}: X={X.shape} | missing clips={missing}")


if __name__ == "__main__":
    main()
