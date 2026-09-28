"""Change 015 analysis: eGeMAPS statistics (§3) + WavLM layer-wise probe (§4).

Pre-registered, FROZEN 2026-09-27:
docs/spec/changes/015-emotion-acoustic-features/preregistration.md. Every constant below
mirrors a section of it — changing one needs a dated §9 amendment, not an edit here.

Reads the output of extract_emotion_features.py and writes egemaps_stats.md,
layer_probe.md and metrics.json to docs/reports/015/. The probe head, metrics, seed
pooling and paired bootstrap are imported from the baseline kernel (vnser-train.py), so
the setup is the baseline's / change 012 §10's by construction, not by copy.

--smoke permutes the labels (and subsamples, 2 seeds, short epochs): it exercises every
code path WITHOUT showing a real result before the pre-registration is committed.

Usage (from repo root; the full run is ~CPU-hours, keep the laptop on AC):
  PYTHONIOENCODING=utf-8 PYTHONPATH=scripts/vietnamese-ser \
    .venv-vnser/Scripts/python.exe scripts/vietnamese-ser/analyze_emotion_features.py
  # code test: ... analyze_emotion_features.py --smoke --out <scratch dir>
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from extract_emotion_features import META
from scipy.stats import false_discovery_control, kruskal, spearmanr

ROOT = Path(__file__).resolve().parents[2]
FEAT_DIR = ROOT / "data" / "vietnamese-ser" / "features" / "015"
REPORT_DIR = ROOT / "docs" / "reports" / "015"
KERNEL = ROOT / "kaggle" / "vietnamese-ser" / "vnser-train" / "vnser-train.py"

SEEDS = list(range(10))  # §4
N_LAYERS = 25  # hidden_states[0..24]; 24 == baseline
BASELINE_LAYER = 24
THRESHOLD = 0.02  # §5
MIN_GROUP = 20  # §3
AGE_MERGE = {"teen": "young_adult", "senior": "middle_aged"}  # §3
VOICE_QUALITY = [  # H1c / D2
    f"{f}_sma3nz_{s}"
    for f in ("jitterLocal", "shimmerLocaldB", "HNRdBACF", "logRelF0-H1-H2", "logRelF0-H1-A3")
    for s in ("amean", "stddevNorm")
]
H1A = ("F0semitoneFrom27.5Hz_sma3nz_amean", "loudness_sma3_amean")
PROSODY_PREFIX = ("F0semitone", "loudness", "equivalentSoundLevel")
RHYTHM = {
    "VoicedSegmentsPerSec",
    "MeanVoicedSegmentLengthSec",
    "StddevVoicedSegmentLengthSec",
    "MeanUnvoicedSegmentLength",
    "StddevUnvoicedSegmentLength",
}


def load_kernel(smoke: bool):
    if smoke:
        os.environ["VNSER_SMOKE"] = "1"  # the kernel reads it at import: short epochs
    spec = importlib.util.spec_from_file_location("vnser_train", KERNEL)
    vt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vt)
    return vt


def quiet(fn, *a, **kw):
    """oof_predict prints one line per fold; thousands of calls here."""
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **kw)


def feature_group(col: str) -> str:
    if col in VOICE_QUALITY:
        return "voice quality"
    if col.startswith(PROSODY_PREFIX) or col in RHYTHM:
        return "prosody"
    return "spectral"


# ── §3 eGeMAPS statistics ────────────────────────────────────────────────────
def norm_groups(eg: pd.DataFrame, min_group: int) -> pd.Series:
    """(gender × age_group) key per row, groups < min_group merged to the adjacent age."""
    age = eg["age_group"].copy()
    small = (eg["gender"] + "/" + age).map((eg["gender"] + "/" + age).value_counts()) < min_group
    if not age[small].isin(list(AGE_MERGE)).all():
        raise SystemExit(f"small group with no merge rule: {set(age[small]) - set(AGE_MERGE)}")
    age[small] = age[small].map(AGE_MERGE)
    key = eg["gender"] + "/" + age
    counts = key.value_counts()
    if (counts < min_group).any():
        raise SystemExit(f"group still < {min_group} after merge: {counts.to_dict()}")
    return key


def egemaps_stats(eg: pd.DataFrame, feats: list[str], emotions: list[str], min_group: int) -> dict:
    d = eg.dropna(subset=["gender", "age_group"]).reset_index(drop=True)
    key = norm_groups(d, min_group)
    x = d[feats].astype(float)
    g = x.groupby(key)
    z = (x - g.transform("mean")) / g.transform("std", ddof=0)

    rows, pvals = [], []
    for c in feats:
        h, p_kw = kruskal(*[z[c][d["emotion"] == e] for e in emotions])
        r_v, p_v = spearmanr(z[c], d["valence"])
        r_a, p_a = spearmanr(z[c], d["arousal"])
        rows.append(
            {
                "feature": c,
                "group": feature_group(c),
                "eps2": float(h / (len(d) - 1)),
                "rho_valence": float(r_v),
                "rho_arousal": float(r_a),
            }
        )
        pvals += [p_kw, p_v, p_a]
    q = false_discovery_control(np.array(pvals), method="bh")  # all 88 × 3 tests at once
    for i, r in enumerate(rows):
        r["q_kw"], r["q_valence"], r["q_arousal"] = (float(v) for v in q[3 * i : 3 * i + 3])

    by = {r["feature"]: r for r in rows}
    vq = [by[c] for c in VOICE_QUALITY]
    hyp = {
        "H1a": all(by[c]["rho_arousal"] > 0 and by[c]["q_arousal"] < 0.05 for c in H1A),
        "H1b": max(abs(r["rho_valence"]) for r in rows) < max(abs(r["rho_arousal"]) for r in rows),
        "H1c": any(abs(r["rho_valence"]) >= 0.1 and r["q_valence"] < 0.05 for r in vq),
    }
    medians = {
        c: {e: float(z[c][d["emotion"] == e].median()) for e in emotions}
        for c in [*H1A, *VOICE_QUALITY]
    }
    return {
        "n": len(d),
        "groups": key.value_counts().to_dict(),
        "features": rows,
        "hypotheses": hyp,
        "class_medians_z": medians,
    }


# ── §4 layer-wise probe ──────────────────────────────────────────────────────
def seed_preds(vt, X, folds, labels, seeds):
    return [quiet(vt.oof_predict, X, folds, *labels, seed=s) for s in seeds]


def pooled_score(vt, preds, labels):
    emo, val, aro = labels
    pe, pv, pa = vt.pool_seeds(preds)
    return vt.score(emo, pe, val, pv, aro, pa)


def pick_layer(vt, emb, eg, rows, labels, seed) -> tuple[int, list[float]]:
    """§4.2: ℓ* from inner GroupKFold(ep) over the TRAINING series only; ties -> larger."""
    sub = eg[rows].reset_index(drop=True)
    inner = np.array(vt.assign_folds(sub, n_splits=min(5, sub["ep"].nunique())))
    lab = [a[rows] for a in labels]
    f1s = []
    for layer in range(emb.shape[1]):
        oe = quiet(vt.oof_predict, emb[rows, layer], inner, *lab, seed=seed)[0]
        f1s.append(vt.macro_f1(lab[0], oe, len(vt.EMOTIONS)))
    return max(range(len(f1s)), key=lambda i: (f1s[i], i)), f1s


def verdict(d: dict) -> str:
    lo, hi = d["ci95"]
    if lo <= 0 <= hi or abs(d["delta"]) < THRESHOLD:
        return "H0 - keep layer 24"
    if d["delta"] >= THRESHOLD:
        return "in-fold layer selection beats layer 24 - switch the baseline feature (new change)"
    return "in-fold selection is WORSE - keep layer 24; inner-CV unstable at this size"


def layer_probe(vt, eg, emb, X_eg, seeds) -> dict:
    labels = vt.encode_labels(eg)
    series = sorted(eg["series"].unique())
    sfolds = eg["series"].map({s: i for i, s in enumerate(series)}).to_numpy()
    evals = {"groupkfold": np.array(vt.assign_folds(eg)), "leave_one_series_out": sfolds}

    curve, loso_seed_preds = {}, {}
    for layer in range(emb.shape[1]):
        curve[layer] = {}
        for ev, folds in evals.items():
            preds = seed_preds(vt, emb[:, layer], folds, labels, seeds)
            curve[layer][ev] = pooled_score(vt, preds, labels)
            if ev == "leave_one_series_out":
                loso_seed_preds[layer] = preds
        print(
            f"[4.1] layer {layer:2d} · LOSO F1 {curve[layer]['leave_one_series_out']['emotion_macro_f1']:.3f}"
        )

    egemaps = {
        ev: pooled_score(vt, seed_preds(vt, X_eg, f, labels, seeds), labels)
        for ev, f in evals.items()
    }
    print("[4.3] eGeMAPS probe done")

    # §4.2 — selected arm: per outer fold × seed, ℓ* chosen on the training series only
    chosen, sel_preds = [], []
    for s in seeds:
        pe, pv, pa = (np.full(len(eg), -1), np.full(len(eg), np.nan), np.full(len(eg), np.nan))
        for f, name in enumerate(series):
            best, inner_f1 = pick_layer(vt, emb, eg, sfolds != f, labels, s)
            chosen.append({"seed": s, "test_series": name, "layer": best, "inner_f1": inner_f1})
            out = quiet(vt.oof_predict, emb[:, best], sfolds, *labels, seed=s)
            te = sfolds == f
            pe[te], pv[te], pa[te] = out[0][te], out[1][te], out[2][te]
            print(f"[4.2] seed {s} · test {name} · ℓ*={best}")
        sel_preds.append((pe, pv, pa))

    base_preds = loso_seed_preds[BASELINE_LAYER]
    emo = labels[0]
    f1 = lambda a, b: vt.macro_f1(a, b, len(vt.EMOTIONS))  # noqa: E731
    d = vt.paired_delta(f1, emo, vt.pool_seeds(sel_preds)[0], vt.pool_seeds(base_preds)[0])
    diff = [f1(emo, p[0]) - f1(emo, q[0]) for p, q in zip(sel_preds, base_preds)]
    d["seed_range"] = [float(min(diff)), float(max(diff))]
    d["verdict"] = verdict(d)
    return {
        "series": series,
        "curve": curve,
        "egemaps_probe": egemaps,
        "selected": {"metrics": pooled_score(vt, sel_preds, labels), "chosen": chosen},
        "delta_selected_minus_24": d,
    }


# ── reports ──────────────────────────────────────────────────────────────────
CAVEATS = [
    "> ⚠ **Pilot, single-annotator labels** (ADR-003; owner↔blind κ 0.513) — NOT a headline",
    "> accuracy (I6). F0 / phonation features here carry **lexical tone and emotion mixed**:",
    "> no syllable-tone labels exist yet to separate them. Northern dialect only.",
]


def _ci(m, k):
    lo, hi = m[f"{k}_ci95"]
    return f"{m[k]:.3f} [{lo:.3f}, {hi:.3f}]"


def write_egemaps_report(st: dict, out: Path) -> None:
    yes = lambda b: "**TRUE**" if b else "**FALSE**"  # noqa: E731
    h = st["hypotheses"]
    lines = [
        "# Change 015 §3 — eGeMAPS vs emotion / valence / arousal",
        "",
        *CAVEATS,
        "> Normalised by (gender × age_group) only — **recording / mix differences between the",
        "> two series remain in these features** (D1). Clips are not independent (shared",
        "> speakers, episodes): read effect sizes; q-values only filter.",
        "",
        f"- clips: {st['n']} · normalisation groups: {st['groups']}",
        "- ε² = Kruskal–Wallis effect size over 7 classes; ρ = Spearman; q = BH over all 264 tests",
        "",
        "## Pre-registered hypotheses (§1)",
        "",
        "| | Hypothesis | Result |",
        "|---|---|---|",
        f"| H1a | arousal ρ > 0 with F0 mean AND loudness mean (q < 0.05) | {yes(h['H1a'])} |",
        f"| H1b | max \\|ρ valence\\| < max \\|ρ arousal\\| over 88 features | {yes(h['H1b'])} |",
        f"| H1c | ≥1 voice-quality feature with \\|ρ valence\\| ≥ 0.1, q < 0.05 | {yes(h['H1c'])} |",
    ]
    for grp in ("prosody", "voice quality", "spectral"):
        rs = sorted((r for r in st["features"] if r["group"] == grp), key=lambda r: -r["eps2"])
        lines += [
            "",
            f"## {grp} ({len(rs)} features)",
            "",
            "| feature | ε² | q KW | ρ valence | q | ρ arousal | q |",
            "|---|--:|--:|--:|--:|--:|--:|",
        ]
        lines += [
            f"| `{r['feature']}` | {r['eps2']:.3f} | {r['q_kw']:.2g} | {r['rho_valence']:+.3f} | "
            f"{r['q_valence']:.2g} | {r['rho_arousal']:+.3f} | {r['q_arousal']:.2g} |"
            for r in rs
        ]
    emos = list(next(iter(st["class_medians_z"].values())))
    lines += [
        "",
        "## Class medians (normalised z) — H1a / H1c features",
        "",
        "| feature | " + " | ".join(emos) + " |",
        "|---|" + "--:|" * len(emos),
    ]
    lines += [
        f"| `{c}` | " + " | ".join(f"{v:+.2f}" for v in m.values()) + " |"
        for c, m in st["class_medians_z"].items()
    ]
    (out / "egemaps_stats.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_probe_report(lp: dict, out: Path, seeds: list[int]) -> None:
    d = lp["delta_selected_minus_24"]
    lo, hi = d["ci95"]
    lines = [
        "# Change 015 §4 — where emotion lives in WavLM-Large (layer-wise linear probe)",
        "",
        *CAVEATS,
        "",
        f"- head/settings = baseline kernel (012 §10) · seeds {seeds} pooled · series {lp['series']}",
        "- §4.1 curve is DESCRIPTIVE: its peak was picked on the test folds. The decision",
        "  (§5) reads only the in-fold selection below.",
        "",
        "## §4.2 Decision — layer chosen inside the training fold vs layer 24 (LOSO)",
        "",
        "| Δ macro-F1 (ℓ* − 24) | 95% CI (paired bootstrap) | per-seed Δ range | verdict (§5) |",
        "|--:|---|---|---|",
        f"| {d['delta']:+.3f} | [{lo:+.3f}, {hi:+.3f}] | "
        f"[{d['seed_range'][0]:+.3f}, {d['seed_range'][1]:+.3f}] | {d['verdict']} |",
        "",
        "ℓ* per (test series × seed): "
        + ", ".join(
            f"{c['test_series'][:6]}/s{c['seed']}={c['layer']}" for c in lp["selected"]["chosen"]
        ),
        "",
        "## §4.1 Curve (pooled seeds) + §4.3 eGeMAPS probe",
        "",
        "| features | GKF macro-F1 | LOSO macro-F1 [CI] | LOSO UAR | LOSO CCC val | LOSO CCC aro |",
        "|---|--:|---|--:|--:|--:|",
    ]
    rows = [(f"layer {k}", v) for k, v in lp["curve"].items()] + [
        ("eGeMAPS-88", lp["egemaps_probe"])
    ]
    for name, m in rows:
        g, lo_ = m["groupkfold"], m["leave_one_series_out"]
        lines.append(
            f"| {name}{' (baseline)' if name == f'layer {BASELINE_LAYER}' else ''} | "
            f"{g['emotion_macro_f1']:.3f} | {_ci(lo_, 'emotion_macro_f1')} | {lo_['emotion_uar']:.3f} | "
            f"{lo_['ccc_valence']:.3f} | {lo_['ccc_arousal']:.3f} |"
        )
    (out / "layer_probe.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--features", type=Path, default=FEAT_DIR)
    ap.add_argument("--out", type=Path, default=REPORT_DIR)
    ap.add_argument("--smoke", action="store_true", help="permuted labels, subset, 2 seeds")
    args = ap.parse_args()
    if args.smoke and args.out.resolve() == REPORT_DIR.resolve():
        raise SystemExit("--smoke must write to a scratch --out, never docs/reports/015")
    vt = load_kernel(args.smoke)

    eg = pd.read_csv(args.features / "egemaps.csv")
    z = np.load(args.features / "wavlm_layers.npz", allow_pickle=True)
    assert (z["keys"] == eg["key"].to_numpy()).all(), "egemaps.csv / npz row order differs"
    emb = z["emb"]
    feats = [c for c in eg.columns if c not in META]
    assert len(feats) == 88 and not eg[feats].isna().any().any(), "expected 88 complete features"
    extract_cfg = json.loads((args.features / "config.json").read_text(encoding="utf-8"))
    seeds, min_group = SEEDS, MIN_GROUP

    if args.smoke:
        rng = np.random.default_rng(0)
        idx = np.sort(
            np.concatenate(
                [
                    rng.choice(np.flatnonzero(eg["series"] == s), 60, replace=False)
                    for s in sorted(eg["series"].unique())
                ]
            )
        )
        eg, emb = eg.iloc[idx].reset_index(drop=True), emb[idx]
        perm = rng.permutation(len(eg))  # destroy the real label signal
        eg[["emotion", "valence", "arousal"]] = (
            eg[["emotion", "valence", "arousal"]].iloc[perm].to_numpy()
        )
        seeds, min_group = [0, 1], 3  # a 120-clip subsample has tiny groups

    args.out.mkdir(parents=True, exist_ok=True)
    st = egemaps_stats(eg, feats, vt.EMOTIONS, min_group)
    write_egemaps_report(st, args.out)
    print(f"[3] hypotheses: {st['hypotheses']}")

    lp = layer_probe(vt, eg, emb, eg[feats].to_numpy(float), seeds)
    write_probe_report(lp, args.out, seeds)

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT
    ).stdout.strip()
    (args.out / "metrics.json").write_text(
        json.dumps(
            {
                "change": "015",
                "smoke": args.smoke,
                "n_clips": len(eg),
                "seeds": seeds,
                "preregistration": "docs/spec/changes/015-emotion-acoustic-features/preregistration.md",
                "analysis_git_commit": commit,
                "extraction": extract_cfg,
                "egemaps_stats": st,
                "layer_probe": lp,
            },
            indent=2,
            ensure_ascii=False,
            default=float,
        ),
        encoding="utf-8",
    )
    print(f"[done] {args.out}")


if __name__ == "__main__":
    main()
