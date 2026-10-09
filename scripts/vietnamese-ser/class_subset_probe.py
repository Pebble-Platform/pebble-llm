"""What happens to the baseline if disgust / surprise leave the label set?

Re-trains the vnser-train linear probes on the cached WavLM features under a few label
sets and reports numbers that stay comparable across class counts:

* macro-F1 / UAR alone are NOT comparable (dropping the two weakest classes raises the
  mean mechanically), so each variant also reports Cohen's kappa model<->owner
  (chance-corrected) and its own chance level;
* `7cls_scored_on_<n>` is the current 7-class model averaged over the kept classes
  only -- the purely mechanical gain, with no retraining;
* human kappa per variant comes from the change-014 blind pass, remapped the same way.

    PYTHONIOENCODING=utf-8 .venv-vnser/Scripts/python.exe scripts/vietnamese-ser/class_subset_probe.py \
        --stage data/vietnamese-ser/kaggle-upload/viemospeech-pilot \
        --features data/vietnamese-ser/kaggle-output/vnser-train-v7/features_wavlm-large.npz \
        --blind data/vietnamese-ser/episodes/gold-reviews/nhinguyen.json \
        --out docs/reports/baseline-1324/class-subset.json
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "vnser_train", ROOT / "kaggle/vietnamese-ser/vnser-train/vnser-train.py"
)
k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(k)
E7 = list(k.EMOTIONS)
KEEP5 = ["neutral", "anger", "joy", "fear_anxiety", "sadness"]
KEEP6 = [*KEEP5, "disgust"]
SEEDS = list(range(10))
CUTOFF = "2026-09-11T07:53:41+00:00"  # same rule as gold_review_kappa.py

# variant -> (label set, remap {old: new or None=drop})
VARIANTS = {
    "7cls": (E7, {}),
    "5cls_drop": (KEEP5, {"disgust": None, "surprise": None}),
    "5cls_disgust_to_anger": (KEEP5, {"disgust": "anger", "surprise": None}),
    "6cls_drop_surprise": (KEEP6, {"surprise": None}),
}


def kappa(y, p, n):
    po = float((y == p).mean())
    pe = sum(float((y == c).mean()) * float((p == c).mean()) for c in range(n))
    return (po - pe) / (1 - pe)


def remap(labels, rm):
    return [rm.get(x, x) for x in labels]


def run_variant(m, X, labels, rm):
    lab = remap(m["emotion"].tolist(), rm)
    keep = np.array([x is not None for x in lab])
    mv = m[keep].reset_index(drop=True).copy()
    mv["emotion"] = [x for x in lab if x is not None]
    Xv = X[keep]
    k.EMOTIONS = labels  # kernel functions read the module global at call time
    n = len(labels)
    y, v, a = k.encode_labels(mv)
    names = sorted(mv["series"].unique())
    sf = mv["series"].map({s: i for i, s in enumerate(names)}).to_numpy()
    gkf = np.array(k.assign_folds(mv))
    out = {
        "n_clips": len(mv),
        "labels": labels,
        "support": {c: int((y == i).sum()) for i, c in enumerate(labels)},
        "chance_majority_macro_f1": k.macro_f1(y, np.full(len(y), np.bincount(y).argmax()), n),
        "chance_uar": 1 / n,
    }
    preds = {}
    for ev, folds in (("gkf", gkf), ("loso", sf)):
        f1, ua, kp = [], [], []
        dirs = {f"->{s}": [] for s in names}
        ps = []
        for s in SEEDS:
            with contextlib.redirect_stdout(io.StringIO()):
                p = k.oof_predict(Xv, folds, y, v, a, seed=s)
            ps.append(p)
            f1.append(k.macro_f1(y, p[0], n))
            ua.append(k.uar(y, p[0], n))
            kp.append(kappa(y, p[0], n))
            if ev == "loso":
                for i, sname in enumerate(names):
                    dirs[f"->{sname}"].append(k.macro_f1(y[sf == i], p[0][sf == i], n))
        modal = k.pool_seeds(ps)[0]
        out[ev] = {
            "macro_f1": float(np.mean(f1)),
            "macro_f1_range": [min(f1), max(f1)],
            "uar": float(np.mean(ua)),
            "kappa": float(np.mean(kp)),
            "per_class_f1": {c: _f1(y, modal, i) for i, c in enumerate(labels)},
        }
        if ev == "loso":
            out[ev]["by_test_series"] = {d: float(np.mean(s_)) for d, s_ in dirs.items()}
        preds[ev] = (y, modal, ps)
    k.EMOTIONS = E7
    return out, preds


def _f1(y, p, c):
    tp = int(((p == c) & (y == c)).sum())
    fp = int(((p == c) & (y != c)).sum())
    fn = int(((p != c) & (y == c)).sum())
    pr = tp / (tp + fp) if tp + fp else 0.0
    rc = tp / (tp + fn) if tp + fn else 0.0
    return 2 * pr * rc / (pr + rc) if pr + rc else 0.0


def human_kappa(blind, labels, rm):
    pairs = []
    for r in blind.values():
        o, b = (
            rm.get(r["original"]["emotion"], r["original"]["emotion"]),
            rm.get(r["answer"]["emotion"], r["answer"]["emotion"]),
        )
        if o is None or b is None:
            continue  # either rater used a dropped class -> not comparable in this label set
        pairs.append((labels.index(o), labels.index(b)))
    y, p = np.array([x[0] for x in pairs]), np.array([x[1] for x in pairs])
    return {
        "n": len(pairs),
        "raw_agreement": float((y == p).mean()),
        "kappa": kappa(y, p, len(labels)),
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--features", required=True)
    ap.add_argument("--blind", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    m = pd.read_csv(Path(a.stage) / "manifest.csv")
    m = m[m["emotion"].isin(E7)].dropna(subset=["valence", "arousal"]).reset_index(drop=True)
    m["series"] = m["ep"].str.split("/").str[0]
    z = np.load(a.features, allow_pickle=True)
    feats = dict(zip(z["clips"], z["emb"]))
    X = np.stack([feats[c] for c in m["clip"]])
    blind = {
        kk: r
        for kk, r in json.loads(Path(a.blind).read_text(encoding="utf-8")).items()
        if r["ts"] >= CUTOFF and not r["rejected"] and r["answer"].get("emotion")
    }

    res = {"seeds": SEEDS}
    preds7 = None
    for name, (labels, rm) in VARIANTS.items():
        out, preds = run_variant(m, X, labels, rm)
        out["human"] = human_kappa(blind, labels, rm)
        res[name] = out
        if name == "7cls":
            preds7 = preds
        print(
            f"[{name}] n={out['n_clips']} gkf={out['gkf']['macro_f1']:.3f} "
            f"loso={out['loso']['macro_f1']:.3f} kappa_loso={out['loso']['kappa']:.3f} "
            f"human_kappa={out['human']['kappa']:.3f}"
        )

    # mechanical effect: the 7-class model, averaged over the kept classes only
    for keep in (KEEP5, KEEP6):
        mech = {}
        for ev in ("gkf", "loso"):
            y, _, ps = preds7[ev]
            idx = [E7.index(c) for c in keep]
            mech[ev] = float(np.mean([np.mean([_f1(y, p[0], i) for i in idx]) for p in ps]))
        res[f"7cls_scored_on_{len(keep)}"] = mech
        print(f"[7cls scored on {len(keep)}] gkf={mech['gkf']:.3f} loso={mech['loso']:.3f}")

    Path(a.out).write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
