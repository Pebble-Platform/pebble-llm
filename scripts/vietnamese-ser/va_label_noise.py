"""How do valence/arousal labels affect the vnser-train results, and what would WRONG
V/A labels do?

1. Diagnostics of the current V/A labels: scale use, per-emotion means, how much of V/A
   the emotion category already explains (eta^2), emotion-inconsistent combinations,
   and how often a second rater changed them (anchored passes -> upper bound on
   agreement).
2. Simulation on the cached v7 features (LOSO, 5 seeds): corrupt V/A with several error
   types, applied to EVERY clip (one annotator labels train and test alike), and score
   the affect head against the corrupted labels (what we would report) and against the
   original labels (what the model really learned). Emotion macro-F1 is recomputed
   under each corruption to confirm it does not move.

    PYTHONIOENCODING=utf-8 .venv-vnser/Scripts/python.exe scripts/vietnamese-ser/va_label_noise.py \
        --stage data/vietnamese-ser/kaggle-upload/viemospeech-pilot \
        --features data/vietnamese-ser/kaggle-output/vnser-train-v7/features_wavlm-large.npz \
        --reviews data/vietnamese-ser/episodes/gold-reviews \
        --out docs/reports/baseline-1324/va-noise.json
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
from iaa_report import krippendorff_alpha

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "vnser_train", ROOT / "kaggle/vietnamese-ser/vnser-train/vnser-train.py"
)
k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(k)
E = k.EMOTIONS
SEEDS = [0, 1, 2, 3, 4]
NEG = {"anger", "fear_anxiety", "sadness", "disgust"}


def eta2(y, groups):
    grand = y.mean()
    between = sum(((groups == g).sum()) * (y[groups == g].mean() - grand) ** 2 for g in set(groups))
    return float(between / ((y - grand) ** 2).sum())


def corrupt(v, a, kind, rng):
    v, a = v.copy(), a.copy()
    n = len(v)
    if kind.startswith("random_"):  # p% of clips get a uniformly random 1-5 value
        p = int(kind.split("_")[1]) / 100
        for x in (v, a):
            m = rng.random(n) < p
            x[m] = rng.integers(1, 6, m.sum())
    elif kind.startswith("jitter_"):  # p% of clips off by one step
        p = int(kind.split("_")[1]) / 100
        for x in (v, a):
            m = rng.random(n) < p
            x[m] = np.clip(x[m] + rng.choice([-1, 1], m.sum()), 1, 5)
    elif kind == "arousal_plus1":  # systematic: every arousal one step too high
        a = np.clip(a + 1, 1, 5)
    elif kind == "compress_to_mid":  # rater avoids extremes: 1->2, 5->4
        v, a = np.clip(v, 2, 4), np.clip(a, 2, 4)
    elif kind == "valence_flip_20":  # 20% of clips get the valence pole reversed
        m = rng.random(n) < 0.2
        v[m] = 6 - v[m]
    return v, a


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--features", required=True)
    ap.add_argument("--reviews", required=True, help="gold-reviews/ directory")
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()

    m = pd.read_csv(Path(a_.stage) / "manifest.csv")
    m = m[m["emotion"].isin(E)].dropna(subset=["valence", "arousal"]).reset_index(drop=True)
    m["series"] = m["ep"].str.split("/").str[0]
    z = np.load(a_.features, allow_pickle=True)
    feats = dict(zip(z["clips"], z["emb"]))
    X = np.stack([feats[c] for c in m["clip"]])
    y, v, a = k.encode_labels(m)
    emo = m["emotion"].to_numpy()
    names = sorted(m["series"].unique())
    sf = m["series"].map({s: i for i, s in enumerate(names)}).to_numpy()
    res = {"n": len(m)}

    # ── 1. diagnostics ───────────────────────────────────────────────────
    res["scale_use"] = {
        "valence": {int(s): int((v == s).sum()) for s in range(1, 6)},
        "arousal": {int(s): int((a == s).sum()) for s in range(1, 6)},
    }
    res["per_emotion"] = {
        e: {
            "n": int((emo == e).sum()),
            "valence_mean": float(v[emo == e].mean()),
            "valence_sd": float(v[emo == e].std()),
            "arousal_mean": float(a[emo == e].mean()),
            "arousal_sd": float(a[emo == e].std()),
        }
        for e in E
    }
    res["eta2_from_emotion"] = {"valence": eta2(v, emo), "arousal": eta2(a, emo)}
    res["corr_valence_arousal"] = float(np.corrcoef(v, a)[0, 1])
    res["inconsistent"] = {
        "joy_valence_le2": int(((emo == "joy") & (v <= 2)).sum()),
        "negative_emotion_valence_ge4": int((np.isin(emo, list(NEG)) & (v >= 4)).sum()),
        "anger_arousal_le2": int(((emo == "anger") & (a <= 2)).sum()),
        "sadness_arousal_ge5": int(((emo == "sadness") & (a >= 5)).sum()),
        "neutral_valence_extreme": int(((emo == "neutral") & ((v == 1) | (v == 5))).sum()),
    }

    raters = {}
    for f in sorted(Path(a_.reviews).glob("*.json")):
        d = [r for r in json.loads(f.read_text(encoding="utf-8")).values() if not r.get("rejected")]
        if len(d) < 50:
            continue
        out = {"n": len(d)}
        for fld in ("valence", "arousal"):
            o = np.array([r["original"][fld] for r in d], float)
            b = np.array([r["answer"][fld] for r in d], float)
            out[fld] = {
                "changed_pct": float((o != b).mean()),
                "mean_abs_diff": float(np.abs(o - b).mean()),
                "alpha_ordinal": krippendorff_alpha(
                    [[x, w] for x, w in zip(o, b)], [1, 2, 3, 4, 5], "ordinal"
                ),
            }
        raters[f.stem] = out
    res["second_rater_anchored"] = raters

    # ── 2. simulation ────────────────────────────────────────────────────
    kinds = [
        "clean",
        "random_10",
        "random_20",
        "random_30",
        "random_50",
        "jitter_30",
        "jitter_60",
        "arousal_plus1",
        "compress_to_mid",
        "valence_flip_20",
    ]
    sim = {}
    for kind in kinds:
        rows = []
        for s in SEEDS:
            rng = np.random.default_rng(1000 + s)
            vn, an = (v, a) if kind == "clean" else corrupt(v, a, kind, rng)
            with contextlib.redirect_stdout(io.StringIO()):
                p = k.oof_predict(X, sf, y, vn, an, seed=s)
            rows.append(
                {
                    "emotion_macro_f1": k.macro_f1(y, p[0], len(E)),
                    "ccc_val_vs_reported": k.ccc(vn, p[1]),
                    "ccc_aro_vs_reported": k.ccc(an, p[2]),
                    "ccc_val_vs_original": k.ccc(v, p[1]),
                    "ccc_aro_vs_original": k.ccc(a, p[2]),
                }
            )
        sim[kind] = {key: float(np.mean([r[key] for r in rows])) for key in rows[0]}
        print(
            f"[{kind:16s}] F1={sim[kind]['emotion_macro_f1']:.4f} "
            f"V rep/orig={sim[kind]['ccc_val_vs_reported']:.3f}/{sim[kind]['ccc_val_vs_original']:.3f} "
            f"A rep/orig={sim[kind]['ccc_aro_vs_reported']:.3f}/{sim[kind]['ccc_aro_vs_original']:.3f}"
        )
    res["simulation_loso"] = sim

    # ── 3. V/A read off the emotion class instead of regressed from audio ──
    out = {}
    with contextlib.redirect_stdout(io.StringIO()):
        p = k.oof_predict(X, sf, y, v, a, seed=0)
    for name, lab in (("true_emotion", y), ("predicted_emotion", p[0])):
        pv, pa = np.zeros(len(y)), np.zeros(len(y))
        for f_ in set(sf):
            tr, te = sf != f_, sf == f_
            for c in range(len(E)):
                sel = te & (lab == c)
                pv[sel] = v[tr & (y == c)].mean()
                pa[sel] = a[tr & (y == c)].mean()
        out[name] = {"ccc_valence": k.ccc(v, pv), "ccc_arousal": k.ccc(a, pa)}
    out["direct_regression"] = {"ccc_valence": k.ccc(v, p[1]), "ccc_arousal": k.ccc(a, p[2])}
    res["va_from_emotion_loso"] = out

    Path(a_.out).write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        json.dumps(
            {kk: res[kk] for kk in res if kk != "simulation_loso"}, indent=1, ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()
