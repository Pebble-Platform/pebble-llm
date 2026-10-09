"""EXPLORATORY (not pre-registered): does changing the emotion class set help?

Two variants against the 7-class probe, on the change-015 features, LOSO, 10 seeds pooled:
  * drop disgust + surprise (5 classes) — scored on the clips whose label is one of the 5
    remaining classes, F1 over those 5 classes, for BOTH models. Comparing a 5-class
    macro-F1 with a 7-class one is not a comparison (fewer, easier classes; higher chance),
    so the naive pair is written out only to show that gap.
  * merge disgust -> anger (6 classes) — all clips, the 7-class model's disgust predictions
    collapsed to anger too, F1 over the same 6 classes.
Layers: 24 (baseline feature) and 16 (the layer change 015's in-fold selection picked most
often — chosen after seeing 015, said plainly in the report). Human side: owner<->blind
Cohen κ recomputed from the change-014 confusion matrix for each class set.

Writes docs/reports/015/classset.json (+ classset.md). render_015_report.py adds a section
from it. Any decision to change the benchmark's class set needs its own pre-registered change.

Usage (from repo root, a few CPU minutes):
  PYTHONIOENCODING=utf-8 PYTHONPATH=scripts/vietnamese-ser \
    .venv-vnser/Scripts/python.exe scripts/vietnamese-ser/classset_015.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys

import numpy as np
import pandas as pd
from analyze_emotion_features import FEAT_DIR, REPORT_DIR, ROOT, SEEDS, load_kernel, quiet

LAYERS = (24, 16)
KAPPA_MD = ROOT / "docs" / "reports" / "014" / "kappa.md"


def f1_over(y, p, classes) -> dict[int, float]:
    out = {}
    for c in classes:
        tp = int(((p == c) & (y == c)).sum())
        fp = int(((p == c) & (y != c)).sum())
        fn = int(((p != c) & (y == c)).sum())
        pr = tp / (tp + fp) if tp + fp else 0.0
        rc = tp / (tp + fn) if tp + fn else 0.0
        out[c] = 2 * pr * rc / (pr + rc) if pr + rc else 0.0
    return out


def human_kappa(emotions: list[str]) -> dict:
    """Cohen κ owner<->blind from the 014 confusion table, per class set."""
    rows = [
        ln
        for ln in KAPPA_MD.read_text(encoding="utf-8").splitlines()
        if re.match(rf"\| ({'|'.join(emotions)}) \|", ln)
    ][-7:]
    names = [r.split("|")[1].strip() for r in rows]
    m = np.array([[int(x) for x in r.split("|")[2:9]] for r in rows])

    def kappa(mat):
        n = mat.sum()
        po, pe = np.trace(mat) / n, (mat.sum(0) * mat.sum(1)).sum() / n**2
        return float((po - pe) / (1 - pe))

    i, j = names.index("disgust"), names.index("anger")
    merged = m.copy()
    merged[j] += merged[i]
    merged[:, j] += merged[:, i]
    keep6 = [k for k in range(7) if k != i]
    keep5 = [k for k, nm in enumerate(names) if nm not in ("disgust", "surprise")]
    return {
        "n": int(m.sum()),
        "seven": kappa(m),
        "merge_disgust_anger": kappa(merged[np.ix_(keep6, keep6)]),
        # κ over the clips BOTH raters put in the 5 kept classes (a clip with either label
        # in disgust/surprise drops out, as it would from a 5-class benchmark)
        "drop_disgust_surprise": kappa(m[np.ix_(keep5, keep5)]),
        "n_drop": int(m[np.ix_(keep5, keep5)].sum()),
        "disgust_row": dict(zip(names, m[i].tolist())),
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    vt = load_kernel(False)
    E = vt.EMOTIONS
    D, A, S = E.index("disgust"), E.index("anger"), E.index("surprise")
    eg = pd.read_csv(FEAT_DIR / "egemaps.csv")
    emb = np.load(FEAT_DIR / "wavlm_layers.npz", allow_pickle=True)["emb"]
    emo, val, aro = vt.encode_labels(eg)
    sf = eg["series"].map({s: i for i, s in enumerate(sorted(eg["series"].unique()))}).to_numpy()

    keep5 = ~np.isin(emo, [D, S])
    c5 = [c for c in range(7) if c not in (D, S)]
    emo_m = np.where(emo == D, A, emo)
    c6 = [c for c in range(7) if c != D]
    mf = lambda y, p, cl: float(np.mean(list(f1_over(y, p, cl).values())))  # noqa: E731
    names = lambda d: {E[c]: v for c, v in d.items()}  # noqa: E731

    out = {
        "seeds": list(SEEDS),
        "n_all": len(eg),
        "n_5": int(keep5.sum()),
        "n_disgust": int((emo == D).sum()),
        "n_surprise": int((emo == S).sum()),
        "human": human_kappa(E),
        "layers": {},
    }
    for layer in LAYERS:
        X = emb[:, layer]

        def run(lab, mask=None, X=X):
            preds = [
                quiet(vt.oof_predict, X, sf, lab, val, aro, train_mask=mask, seed=s) for s in SEEDS
            ]
            return vt.pool_seeds(preds)[0]

        p7, p5, p6 = run(emo), run(emo, keep5), run(emo_m)
        y5, a7, a5 = emo[keep5], p7[keep5], p5[keep5]
        p7m, p6m = np.where(p7 == D, A, p7), np.where(p6 == D, A, p6)
        d5 = vt.paired_delta(lambda y, p: mf(y, p, c5), y5, a5, a7)
        d6 = vt.paired_delta(lambda y, p: mf(y, p, c6), emo_m, p6m, p7m)
        out["layers"][str(layer)] = {
            "seven_macro_f1": vt.macro_f1(emo, p7, 7),
            "seven_per_class": names(f1_over(emo, p7, range(7))),
            "drop": {
                "naive_5class": mf(y5, a5, c5),
                "seven_model": mf(y5, a7, c5),
                "five_model": mf(y5, a5, c5),
                "delta": d5,
                "per_class_seven": names(f1_over(y5, a7, c5)),
                "per_class_five": names(f1_over(y5, a5, c5)),
                "seven_sent_to_dropped": int(np.isin(a7, [D, S]).sum()),
            },
            "merge": {
                "seven_model": mf(emo_m, p7m, c6),
                "merged_model": mf(emo_m, p6m, c6),
                "delta": d6,
                "per_class_seven": names(f1_over(emo_m, p7m, c6)),
                "per_class_merged": names(f1_over(emo_m, p6m, c6)),
                "disgust_predicted_as": {
                    E[c]: int(v) for c, v in enumerate(np.bincount(p7[emo == D], minlength=7))
                },
            },
        }
        print(f"[layer {layer}] drop Δ {d5['delta']:+.3f} · merge Δ {d6['delta']:+.3f}")

    out["git_commit"] = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT
    ).stdout.strip()
    (REPORT_DIR / "classset.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    lines = [
        "# Change 015 — EXPLORATORY: class-set variants (not pre-registered)",
        "",
        f"- clips {out['n_all']} · 5-class subset {out['n_5']} · seeds {out['seeds']} · LOSO",
        f"- human κ owner↔blind (014, n={out['human']['n']}): 7-class "
        f"{out['human']['seven']:.3f} · disgust→anger {out['human']['merge_disgust_anger']:.3f}"
        f" · drop disgust+surprise {out['human']['drop_disgust_surprise']:.3f} "
        f"(n={out['human']['n_drop']})",
        "",
        "| layer | variant | 7-class model | variant model | Δ | 95% CI |",
        "|---|---|--:|--:|--:|---|",
    ]
    for layer, r in out["layers"].items():
        for name, k, a_, b_ in (
            ("drop disgust+surprise (5 cls)", "drop", "seven_model", "five_model"),
            ("merge disgust→anger (6 cls)", "merge", "seven_model", "merged_model"),
        ):
            d = r[k]["delta"]
            lines.append(
                f"| {layer} | {name} | {r[k][a_]:.3f} | {r[k][b_]:.3f} | "
                f"{d['delta']:+.3f} | [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}] |"
            )
    (REPORT_DIR / "classset.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[done] {REPORT_DIR / 'classset.json'}")


if __name__ == "__main__":
    main()
