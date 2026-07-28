"""Run one feature set through the shared probe on both folds; print a results row.

Aligns an id-keyed feature .npz to the split folds (by ep::id), trains the shared
MTL probe (train_eval), and reports macro-F1 / CCC(V,A) / distress-recall averaged
over seeds, for fold1, fold2, and their mean — the benchmark table row.

Usage:  PYTHONPATH=scripts/vietnamese-ser python .../run_benchmark.py mfcc [more.npz ...]
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from data import load_fold
from train_eval import train_eval

REPO = Path(__file__).resolve().parents[3]
FEATDIR = REPO / "data/vietnamese-ser/benchmark/features"


def load_features(name: str) -> dict[str, np.ndarray]:
    z = np.load(FEATDIR / f"{name}.npz", allow_pickle=True)
    return dict(zip(z["ids"], z["X"]))


def align(feat: dict[str, np.ndarray], fold) -> np.ndarray:
    missing = [i for i in fold.ids if i not in feat]
    if missing:
        raise KeyError(f"{len(missing)} ids missing from features (e.g. {missing[:2]})")
    return np.stack([feat[i] for i in fold.ids])


def run_one(name: str) -> None:
    feat = load_features(name)
    print(f"\n=== {name} (dim={next(iter(feat.values())).shape[0]}) ===")
    per_fold = []
    for fold in ("fold1", "fold2"):
        tr, te = load_fold(fold, "train"), load_fold(fold, "test")
        out = train_eval(align(feat, tr), tr, align(feat, te), te)
        per_fold.append(out)
        mf, cv, ca, dr = (out["macro_f1"], out["ccc_valence"],
                          out["ccc_arousal"], out["distress_recall"])
        print(f"  {fold} (test={te.ids[0].split('::')[0].split('/')[0]}): "
              f"macroF1={mf[0]:.3f}±{mf[1]:.3f}  CCC-V={cv[0]:.3f}  CCC-A={ca[0]:.3f}  "
              f"distress-recall={dr[0]:.3f} (n+={out['support'] and int(te.distress.sum())})")
    mean_mf = np.mean([f["macro_f1"][0] for f in per_fold])
    mean_cv = np.mean([f["ccc_valence"][0] for f in per_fold])
    mean_ca = np.mean([f["ccc_arousal"][0] for f in per_fold])
    print(f"  MEAN: macroF1={mean_mf:.3f}  CCC-V={mean_cv:.3f}  CCC-A={mean_ca:.3f}")
    print("  per-class F1 (fold1):",
          {k: round(v, 2) for k, v in per_fold[0]["per_class_f1_mean"].items()})


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    names = sys.argv[1:] or ["mfcc"]
    for n in names:
        run_one(n)


if __name__ == "__main__":
    main()
