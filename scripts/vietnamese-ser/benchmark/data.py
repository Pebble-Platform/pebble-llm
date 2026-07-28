"""Load the frozen benchmark split into label arrays (framework-agnostic).

Reads the fold CSVs from build_split.py and returns aligned per-utt targets that
every method's train/eval loop consumes. No audio, no torch — just ids + labels +
text, so this is importable anywhere (local numpy, or the Kaggle kernel).
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
SPLITS = REPO / "data/vietnamese-ser/benchmark/splits"

EMOTIONS = ["neutral", "anger", "joy", "sadness", "fear_anxiety", "disgust", "surprise"]
EMO2IDX = {e: i for i, e in enumerate(EMOTIONS)}


class Fold:
    """Aligned targets + text for one train or test split half."""

    def __init__(self, rows: list[dict]):
        self.ids = [f"{r['ep']}::{r['id']}" for r in rows]
        self.emotion = np.array([EMO2IDX[r["emotion"]] for r in rows], dtype=np.int64)
        self.emotion_name = [r["emotion"] for r in rows]
        self.valence = np.array([float(r["valence"]) for r in rows], dtype=np.float32)
        self.arousal = np.array([float(r["arousal"]) for r in rows], dtype=np.float32)
        self.distress = np.array([r["distress"].lower() == "true" for r in rows], dtype=bool)
        self.text_asr = [r["text_phowhisper"] for r in rows]
        self.text_caption = [r["text_youtube"] for r in rows]
        self.clip = [r["clip"] for r in rows]
        self.speaker = [f"{r['ep']}::{r['speaker']}" for r in rows]

    def __len__(self) -> int:
        return len(self.ids)

    def class_weights(self) -> np.ndarray:
        """Inverse-frequency weights over ALL 7 classes (0 count -> weight 0)."""
        counts = np.bincount(self.emotion, minlength=len(EMOTIONS)).astype(np.float64)
        w = np.zeros(len(EMOTIONS))
        nz = counts > 0
        w[nz] = counts[nz].sum() / (nz.sum() * counts[nz])
        return w.astype(np.float32)


def load_fold(name: str, half: str) -> Fold:
    """name in {fold1,fold2}; half in {train,test}."""
    path = SPLITS / f"{name}_{half}.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} — run build_split.py first")
    return Fold(list(csv.DictReader(path.open(encoding="utf-8"))))


def _selftest() -> None:
    for name in ("fold1", "fold2"):
        tr, te = load_fold(name, "train"), load_fold(name, "test")
        # speaker-disjoint invariant (whole-series => holds by construction; assert it)
        assert not (set(tr.speaker) & set(te.speaker)), f"{name}: speaker leak!"
        assert len(tr) and len(te)
        assert tr.valence.min() >= 1 and tr.valence.max() <= 5
        cw = tr.class_weights()
        assert cw.shape == (7,)
        print(f"{name}: train={len(tr)} test={len(te)} | "
              f"test present classes={sorted(set(te.emotion_name))} | "
              f"test distress+={int(te.distress.sum())}")
    print("data self-test OK (speaker-disjoint verified)")


if __name__ == "__main__":
    _selftest()
