"""Post-hoc analysis of a vnser-train baseline run from its cached WavLM features.

Re-trains the kernel's own linear probes on CPU (the features are frozen, so this
reproduces the Kaggle numbers) and answers what the kernel report does not:

* LOSO split by direction, over 10 seeds -- the pooled number hides that most of
  its test rows are predicted by the model trained on the SMALLER series;
* size-matched directions + a learning curve (train on a subsample of the big
  series, test on the small one) -- is more labeling of the big series worth it?
* per-class F1 and the pooled LOSO confusion matrix;
* model accuracy on clips where two humans agreed vs disagreed (change 014 blind
  pass) -- how much of the error sits where the label itself is contested.

    PYTHONIOENCODING=utf-8 .venv-vnser/Scripts/python.exe scripts/vietnamese-ser/analyze_baseline.py \
        --stage data/vietnamese-ser/kaggle-upload/viemospeech-pilot \
        --features data/vietnamese-ser/kaggle-output/vnser-train-v7/features_wavlm-large.npz \
        --blind data/vietnamese-ser/episodes/gold-reviews/nhinguyen.json \
        --out docs/reports/baseline-1324/analysis.json
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
E = k.EMOTIONS
SEEDS = list(range(10))
CUTOFF = "2026-09-11T07:53:41+00:00"  # same rule as gold_review_kappa.py


def oof(X, folds, y, v, a, keep=None, seed=0):
    with contextlib.redirect_stdout(io.StringIO()):  # silence per-fold prints
        return k.oof_predict(X, folds, y, v, a, train_mask=keep, seed=seed)


def per_class_f1(y, p):
    out = {}
    for c, name in enumerate(E):
        tp = int(((p == c) & (y == c)).sum())
        fp = int(((p == c) & (y != c)).sum())
        fn = int(((p != c) & (y == c)).sum())
        pr = tp / (tp + fp) if tp + fp else 0.0
        rc = tp / (tp + fn) if tp + fn else 0.0
        out[name] = {
            "f1": 2 * pr * rc / (pr + rc) if pr + rc else 0.0,
            "recall": rc,
            "support": int((y == c).sum()),
        }
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--features", required=True)
    ap.add_argument("--blind", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    m = pd.read_csv(Path(a.stage) / "manifest.csv")
    m = m[m["emotion"].isin(E)].dropna(subset=["valence", "arousal"]).reset_index(drop=True)
    m["series"] = m["ep"].str.split("/").str[0]
    z = np.load(a.features, allow_pickle=True)
    feats = dict(zip(z["clips"], z["emb"]))
    X = np.stack([feats[c] for c in m["clip"]])
    y, v, ar = k.encode_labels(m)
    names = sorted(m["series"].unique())
    sf = m["series"].map({s: i for i, s in enumerate(names)}).to_numpy()
    gkf = np.array(k.assign_folds(m))
    sizes = {s: int((sf == i).sum()) for i, s in enumerate(names)}
    big, small = sorted(range(len(names)), key=lambda i: -sizes[names[i]])
    res = {"n": len(m), "series": sizes, "seeds": SEEDS}

    # 1. pooled + per-direction LOSO, and GKF, over seeds
    loso = [oof(X, sf, y, v, ar, seed=s) for s in SEEDS]
    gk = [oof(X, gkf, y, v, ar, seed=s) for s in SEEDS]

    def seed_stats(preds, mask=None):
        sel = np.ones(len(y), bool) if mask is None else mask
        f = [k.macro_f1(y[sel], p[0][sel], len(E)) for p in preds]
        cv = [k.ccc(v[sel], p[1][sel]) for p in preds]
        ca = [k.ccc(ar[sel], p[2][sel]) for p in preds]
        return {
            "macro_f1_mean": float(np.mean(f)),
            "macro_f1_min": float(min(f)),
            "macro_f1_max": float(max(f)),
            "ccc_valence_mean": float(np.mean(cv)),
            "ccc_arousal_mean": float(np.mean(ca)),
        }

    res["gkf"] = seed_stats(gk)
    res["loso_pooled"] = seed_stats(loso)
    res["loso_direction"] = {
        f"{names[1 - i]}->{names[i]}": {
            "n_train": sizes[names[1 - i]],
            "n_test": sizes[names[i]],
            **seed_stats(loso, sf == i),
        }
        for i in range(len(names))
    }
    s0 = k.score(y, loso[0][0], v, loso[0][1], ar, loso[0][2])
    res["loso_seed0_check"] = s0["emotion_macro_f1"]  # must equal the Kaggle report
    for i in range(len(names)):
        d = k.score(y, loso[0][0], v, loso[0][1], ar, loso[0][2], sf == i)
        res["loso_direction"][f"{names[1 - i]}->{names[i]}"]["seed0_ci95"] = d[
            "emotion_macro_f1_ci95"
        ]

    # 2. learning curve: train on n clips of one series, test on ALL of the other
    def curve(train_i, ns):
        out = []
        test_i = 1 - train_i
        pool = np.flatnonzero(sf == train_i)
        for n in ns:
            f = []
            for s in SEEDS:
                rng = np.random.default_rng(s)
                keep = sf == test_i  # the other fold must keep its rows (affect head)
                keep[rng.choice(pool, size=n, replace=False)] = True
                p = oof(X, sf, y, v, ar, keep=keep, seed=s)
                f.append(k.macro_f1(y[sf == test_i], p[0][sf == test_i], len(E)))
            out.append(
                {"n_train": n, "macro_f1_mean": float(np.mean(f)), "macro_f1_sd": float(np.std(f))}
            )
            print(f"[curve] {names[train_i]} n={n}: {np.mean(f):.3f} ± {np.std(f):.3f}")
        return out

    nb, ns = sizes[names[big]], sizes[names[small]]
    res["curve"] = {
        f"{names[big]}->{names[small]}": curve(big, [66, 132, 264, 500, 750, nb]),
        f"{names[small]}->{names[big]}": curve(small, [66, 132, ns]),
    }

    # 3. per-class F1 (seed-pooled modal prediction) + LOSO confusion
    for key, preds in (("gkf", gk), ("loso_pooled", loso)):
        modal = k.pool_seeds(preds)[0]
        res[key]["per_class"] = per_class_f1(y, modal)
        if key == "loso_pooled":
            res[key]["confusion"] = [
                [int(((y == r) & (modal == c)).sum()) for c in range(len(E))] for r in range(len(E))
            ]
    res["majority_baseline_macro_f1"] = k.macro_f1(y, np.full(len(y), E.index("neutral")), len(E))

    # 4. model on clips two humans agreed / disagreed on (blind pass, change 014)
    blind = json.loads(Path(a.blind).read_text(encoding="utf-8"))
    blind = {
        kk: r
        for kk, r in blind.items()
        if r["ts"] >= CUTOFF and not r["rejected"] and r["answer"].get("emotion")
    }
    key = (m["ep"] + "/" + m["id"]).to_numpy()
    hb = {}
    for ev, preds in (("gkf", gk), ("loso", loso)):
        modal = k.pool_seeds(preds)[0]
        rows = {"agree": [], "disagree": []}
        for i, kk in enumerate(key):
            r = blind.get(kk)
            if r is None:
                continue
            o, b = r["original"]["emotion"], r["answer"]["emotion"]
            pred = E[modal[i]]
            rows["agree" if o == b else "disagree"].append((pred == o, pred == b))
        hb[ev] = {
            g: {
                "n": len(rs),
                "acc_vs_owner": float(np.mean([x[0] for x in rs])),
                "acc_vs_blind": float(np.mean([x[1] for x in rs])),
                "matches_either": float(np.mean([x[0] or x[1] for x in rs])),
            }
            for g, rs in rows.items()
        }
    res["human_agreement_split"] = hb

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
