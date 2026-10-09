"""vnser-train — pilot SER baseline (speech-only, frozen WavLM-Large) on ViEmoSpeech.

HUMAN-LABEL era (ADR-003): the corpus label of record is the human `emotion` /
`valence` / `arousal` from tools/labeler (state.db), NOT the 2-teacher consensus the
earlier version of this kernel trained on. Reads the private Kaggle dataset
`phatneurondai/viemospeech-pilot` (manifest.csv built by
scripts/vietnamese-ser/build_kaggle_gold.py + clips/*.wav 16kHz), extracts a frozen
WavLM-Large embedding per clip (masked-mean pool, cached), trains two linear-probe
heads:
  * emotion  — 5-class (neutral/anger/joy/fear_anxiety/sadness; ADR-006: disgust and
               surprise clips stay labeled in the corpus but are left out of train and
               benchmark — the ablation mode keeps its frozen 7 classes), weighted-CE by class frequency. Reported with macro-F1 AND UAR
               (unweighted average recall — the imbalanced-SER standard) + per-class
               support. No sample weighting (human labels carry no teacher confidence).
  * affect   — valence / arousal (1-5) regression, CCC loss.
(distress head dropped: the 750 human-clean clips have ZERO distress positives —
 distress was removed from the labeler form 2026-07-10.)

--- TWO EVALS (do not strip from the report) -----------------------------------
Two shows with disjoint casts (ve-nha-di-con, chay-tron-thanh-xuan).
  A) GroupKFold(ep): fold by EPISODE, pools both series. Cast recurs across episodes
     WITHIN a series, so identity leaks within-series → this number is OPTIMISTIC.
  B) Leave-one-series-out: train on one show, test the other. Different shows share
     no actors → cross-cast, TRUE speaker-disjoint (I4 / ADR-002 whole-series held-out)
     — the honest generalization number.
Labels are a SINGLE human annotator (no inter-annotator κ yet — ADR-003 gap): report
the numbers as pilot baselines, never as a settled accuracy claim (I6). The A→B gap
shows how much within-series identity leak inflates A.

--- Kaggle P100 gotchas (do not "fix") -----------------------------------------
P100 = sm_60: the default image torch won't run on it, so the kernel first pins
torch==2.5.1+cu121. torchaudio 2.5.1 keeps an internal I/O backend, so the local
soundfile shim is not needed here.

--- Two modes ------------------------------------------------------------------
Baseline (manifest without reviewed columns): the two evals above, one label set.
ABLATION (manifest WITH emotion_reviewed/valence_reviewed/arousal_reviewed/agreed, or
VNSER_ABLATION=1): change 012 — four label arms over the SAME clips, folds and frozen
features, every arm scored on the SAME fixed test labels. Pre-registered in
docs/spec/changes/012-label-quality-ablation/preregistration.md; the decision rule in
`verdict()` is applied mechanically so the conclusion cannot be picked after the fact.

--- Smoke mode (local CPU test before pushing) ---------------------------------
  VNSER_SMOKE=1 -> a slice from each series, few epochs, skip pip install. Run e.g.:
    VNSER_SMOKE=1 VNSER_INPUT=<dir with manifest.csv + clips/> \
      VNSER_OUTPUT=/tmp/vnser_train_smoke .venv-vnser/Scripts/python.exe \
      kaggle/vietnamese-ser/vnser-train/vnser-train.py

Media + outputs live under data/** locally (gitignored) — never commit them.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

EMOTIONS = ["neutral", "anger", "joy", "fear_anxiety", "sadness", "disgust", "surprise"]
BENCHMARK_EXCLUDE = ("disgust", "surprise")  # ADR-006: baseline trains/scores 5 classes
BACKBONE = "microsoft/wavlm-large"
N_SPLITS = 5
SEED = 0
GROUP_COL = "ep"  # fold by episode (speaker diarization ids are unreliable, not remapped)

SMOKE = os.environ.get("VNSER_SMOKE") == "1"
ABLATION = os.environ.get("VNSER_ABLATION") == "1"  # change 012; also auto-on, see main()
SEEDS = [int(x) for x in os.environ.get("VNSER_SEEDS", "0,1,2,3,4,5,6,7,8,9").split(",")]
ON_KAGGLE = os.path.exists("/kaggle/input")
# torchvision pinned to the torch-2.5.1 partner (0.20.1): transformers' feature-
# extractor import pulls in torchvision, and Kaggle's preinstalled torchvision (built
# for torch 2.10) then fails with "torchvision::nms does not exist", cascading to a
# WavLMModel import error. transformers pinned to 4.46.3: newer transformers refuse
# torch.load on torch<2.6 (CVE-2025-32434) unless the checkpoint is safetensors, but
# microsoft/wavlm-large ships a .bin — and we cannot bump torch (2.6 is unsafe on the
# P100/sm_60). 4.46.3 predates that guard and is compatible with 2.5.1.
PIP_PINS = [
    "torch==2.5.1", "torchvision==0.20.1", "torchaudio==2.5.1",
    "transformers==4.46.3", "soundfile", "pandas", "numpy",
]


def _pip_install() -> None:
    # P100 = sm_60: pin torch 2.5.1+cu121 (default image torch won't run on P100).
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "--extra-index-url",
         "https://download.pytorch.org/whl/cu121", *PIP_PINS],
        check=True,
    )


# ── features ─────────────────────────────────────────────────────────────────
def extract_features(manifest, input_root: Path, cache: Path):
    """Frozen WavLM-Large masked-mean embedding per clip -> {clip: np.ndarray[1024]}.

    Cached to `cache` (.npz); re-run loads it instead of recomputing.
    """
    import numpy as np

    if cache.exists():
        z = np.load(cache, allow_pickle=True)
        print(f"[features] cache hit: {cache} ({len(z['clips'])} clips)")
        return {c: e for c, e in zip(z["clips"], z["emb"])}

    import soundfile as sf
    import torch
    from transformers import AutoFeatureExtractor, WavLMModel

    device = "cuda" if torch.cuda.is_available() else "cpu"
    fe = AutoFeatureExtractor.from_pretrained(BACKBONE)
    model = WavLMModel.from_pretrained(BACKBONE).to(device).eval()

    clips, embs = [], []
    for i, clip in enumerate(manifest["clip"].tolist()):
        wav, _ = sf.read(input_root / clip, dtype="float32")
        if wav.ndim > 1:
            wav = wav.mean(axis=1)
        inp = fe(wav, sampling_rate=16000, return_tensors="pt").input_values.to(device)
        with torch.no_grad():
            hidden = model(inp).last_hidden_state  # [1, T, 1024]
        embs.append(hidden.mean(dim=1).squeeze(0).cpu().numpy())  # masked-mean (no pad here)
        clips.append(clip)
        if (i + 1) % 100 == 0:
            print(f"[features] {i + 1}/{len(manifest)}")
    emb = np.stack(embs).astype("float32")
    np.savez(cache, clips=np.array(clips), emb=emb)
    print(f"[features] wrote {cache}")
    return dict(zip(clips, emb))


# ── splits ───────────────────────────────────────────────────────────────────
def assign_folds(manifest, n_splits: int = N_SPLITS):
    """Deterministic greedy GroupKFold over episode (`ep`); heaviest group first."""
    sizes = manifest.groupby(GROUP_COL).size()
    order = sorted(sizes.index, key=lambda g: (-int(sizes[g]), g))
    load = [0] * n_splits
    gf: dict = {}
    for g in order:
        f = min(range(n_splits), key=lambda i: (load[i], i))
        gf[g] = f
        load[f] += int(sizes[g])
    return [gf[k] for k in manifest[GROUP_COL]]


# ── heads + metrics ──────────────────────────────────────────────────────────
def _train_linear(X, y, task: str, n_classes: int, class_w=None, epochs=200, seed=SEED):
    import torch

    torch.manual_seed(seed)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    Xt = torch.tensor(X, dtype=torch.float32).to(dev)
    out_dim = n_classes if task == "cls" else 2
    head = torch.nn.Linear(X.shape[1], out_dim).to(dev)
    opt = torch.optim.Adam(head.parameters(), lr=1e-3, weight_decay=1e-4)

    if task == "cls":
        yt = torch.tensor(y, dtype=torch.long).to(dev)
        cw = torch.tensor(class_w, dtype=torch.float32).to(dev) if class_w is not None else None
        lossf = torch.nn.CrossEntropyLoss(weight=cw)
    else:  # reg2
        yt = torch.tensor(y, dtype=torch.float32).to(dev)

    for _ in range(epochs):
        opt.zero_grad()
        z = head(Xt)
        loss = lossf(z, yt) if task == "cls" else _ccc_loss(z, yt)
        loss.backward()
        opt.step()
    head.eval()
    return head


def _ccc_loss(pred, target):
    loss = 0.0
    for k in range(target.shape[1]):
        x, y = pred[:, k], target[:, k]
        vx, vy = x - x.mean(), y - y.mean()
        cov = (vx * vy).mean()
        ccc = 2 * cov / (x.var(unbiased=False) + y.var(unbiased=False) + (x.mean() - y.mean()) ** 2 + 1e-8)
        loss = loss + (1 - ccc)
    return loss / target.shape[1]


def macro_f1(y_true, y_pred, n_classes):
    import numpy as np

    f1s = []
    for c in range(n_classes):
        tp = int(((y_pred == c) & (y_true == c)).sum())
        fp = int(((y_pred == c) & (y_true != c)).sum())
        fn = int(((y_pred != c) & (y_true == c)).sum())
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * p * r / (p + r) if p + r else 0.0)
    return float(np.mean(f1s))


def uar(y_true, y_pred, n_classes):
    """Unweighted average recall (balanced accuracy) — the imbalanced-SER standard.

    Averages per-class recall over classes PRESENT in y_true (a class with no test
    support is excluded rather than counted as recall 0).
    """
    import numpy as np

    recs = []
    for c in range(n_classes):
        support = int((y_true == c).sum())
        if support == 0:
            continue
        tp = int(((y_pred == c) & (y_true == c)).sum())
        recs.append(tp / support)
    return float(np.mean(recs)) if recs else float("nan")


def ccc(y_true, y_pred):
    import numpy as np

    x, y = np.asarray(y_pred, float), np.asarray(y_true, float)
    cov = ((x - x.mean()) * (y - y.mean())).mean()
    return float(2 * cov / (x.var() + y.var() + (x.mean() - y.mean()) ** 2 + 1e-8))


def bootstrap_ci(fn, *arrays, n=1000, seed=SEED):
    import numpy as np

    rng = np.random.default_rng(seed)
    m = len(arrays[0])
    vals = []
    for _ in range(n):
        idx = rng.integers(0, m, m)
        v = fn(*[a[idx] for a in arrays])
        if v == v:  # skip nan
            vals.append(v)
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return float(lo), float(hi)


# ── orchestration ────────────────────────────────────────────────────────────
def encode_labels(manifest, emo_col="emotion", val_col="valence", aro_col="arousal"):
    """(emotion index array, valence, arousal) from the named manifest columns."""
    import numpy as np

    emo_idx = {e: i for i, e in enumerate(EMOTIONS)}
    return (
        np.array([emo_idx.get(e, -1) for e in manifest[emo_col]]),
        manifest[val_col].to_numpy(float),
        manifest[aro_col].to_numpy(float),
    )


def oof_predict(X, folds, emo_label, val, aro, train_mask=None, seed=SEED):
    """Out-of-fold predictions over an arbitrary integer `folds` array.

    `train_mask` narrows what a fold may TRAIN on (change 012 arms C/C'); every row is
    still predicted, so the scored test set stays identical across arms.
    """
    import numpy as np
    import torch

    fold_ids = sorted(set(int(f) for f in folds))
    n = len(emo_label)
    oof_emo = np.full(n, -1)
    oof_val = np.full(n, np.nan)
    oof_aro = np.full(n, np.nan)
    keep = np.ones(n, bool) if train_mask is None else np.asarray(train_mask, bool)

    for f in fold_ids:
        tr, va = (folds != f) & keep, folds == f
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6
        Xtr, Xva = (X[tr] - mu) / sd, (X[va] - mu) / sd

        # emotion (7-class), weighted-CE by train class frequency
        etr = tr & (emo_label >= 0)
        eva = va & (emo_label >= 0)
        if etr.sum() and eva.sum():
            counts = np.bincount(emo_label[etr], minlength=len(EMOTIONS))
            cw = len(emo_label[etr]) / (len(EMOTIONS) * np.maximum(counts, 1))
            head = _train_linear(
                (X[etr] - mu) / sd, emo_label[etr], "cls", len(EMOTIONS),
                class_w=cw, epochs=40 if SMOKE else 200, seed=seed,
            )
            with torch.no_grad():
                p = head(torch.tensor((X[eva] - mu) / sd, dtype=torch.float32,
                                      device=next(head.parameters()).device))
            oof_emo[eva] = p.argmax(1).cpu().numpy()

        # affect (all rows)
        head = _train_linear(Xtr, np.stack([val[tr], aro[tr]], 1), "reg2", 2,
                             epochs=40 if SMOKE else 300, seed=seed)
        with torch.no_grad():
            p = head(torch.tensor(Xva, dtype=torch.float32,
                                  device=next(head.parameters()).device)).cpu().numpy()
        oof_val[va], oof_aro[va] = p[:, 0], p[:, 1]
        print(f"[cv] fold {f} done")
    return oof_emo, oof_val, oof_aro


def score(emo_label, oof_emo, val, oof_val, aro, oof_aro, test_mask=None):
    """Metrics over the rows selected by `test_mask` (default: all)."""
    import numpy as np

    sel = np.ones(len(emo_label), bool) if test_mask is None else np.asarray(test_mask, bool)
    em = sel & (emo_label >= 0)  # affect scores over `sel`; emotion also needs a valid class
    val, oof_val, aro, oof_aro = val[sel], oof_val[sel], aro[sel], oof_aro[sel]
    emo_label, oof_emo = emo_label[em], oof_emo[em]
    f1 = macro_f1(emo_label, oof_emo, len(EMOTIONS))
    f1_ci = bootstrap_ci(lambda a, b: macro_f1(a, b, len(EMOTIONS)), emo_label, oof_emo)
    ua = uar(emo_label, oof_emo, len(EMOTIONS))
    ua_ci = bootstrap_ci(lambda a, b: uar(a, b, len(EMOTIONS)), emo_label, oof_emo)
    cv, cv_ci = ccc(val, oof_val), bootstrap_ci(ccc, val, oof_val)
    ca, ca_ci = ccc(aro, oof_aro), bootstrap_ci(ccc, aro, oof_aro)
    per_class = {EMOTIONS[c]: int((emo_label == c).sum()) for c in range(len(EMOTIONS))}
    return {
        "emotion_macro_f1": f1, "emotion_macro_f1_ci95": f1_ci,
        "emotion_uar": ua, "emotion_uar_ci95": ua_ci,
        "emotion_n": len(emo_label), "emotion_support": per_class,
        "ccc_valence": cv, "ccc_valence_ci95": cv_ci,
        "ccc_arousal": ca, "ccc_arousal_ci95": ca_ci,
    }


def cv_metrics(manifest, X, folds):
    """Baseline path: out-of-fold CV on the owner labels, scored on every row.

    Returns (metrics, oof) so the per-clip predictions can be written out too.
    """
    emo_label, val, aro = encode_labels(manifest)
    oof = oof_predict(X, folds, emo_label, val, aro)
    return score(emo_label, oof[0], val, oof[1], aro, oof[2]), oof


def _metric_rows(m: dict) -> list[str]:
    return [
        "| Head | Metric | Value | 95% CI |",
        "|---|---|---|---|",
        f"| emotion ({len(EMOTIONS)}-class) | macro-F1 | {m['emotion_macro_f1']:.3f} | "
        f"[{m['emotion_macro_f1_ci95'][0]:.3f}, {m['emotion_macro_f1_ci95'][1]:.3f}] |",
        f"| emotion ({len(EMOTIONS)}-class) | UAR | {m['emotion_uar']:.3f} | "
        f"[{m['emotion_uar_ci95'][0]:.3f}, {m['emotion_uar_ci95'][1]:.3f}] |",
        f"| affect | CCC valence | {m['ccc_valence']:.3f} | "
        f"[{m['ccc_valence_ci95'][0]:.3f}, {m['ccc_valence_ci95'][1]:.3f}] |",
        f"| affect | CCC arousal | {m['ccc_arousal']:.3f} | "
        f"[{m['ccc_arousal_ci95'][0]:.3f}, {m['ccc_arousal_ci95'][1]:.3f}] |",
    ]


def write_report(m_gkf, m_loso, series_names, manifest, out_dir: Path, split_hash: str):
    cnt = {e: int((manifest["emotion"] == e).sum()) for e in EMOTIONS}
    lines = [
        "# vnser-train — pilot SER baseline (speech-only, frozen WavLM-Large)",
        "",
        "> ⚠ **PILOT, HUMAN single-annotator labels (train labels single-pass; blind owner↔rater κ 0.513 on a 343-clip sample, change 014).**",
        "> Report as pilot baselines, NOT a settled accuracy claim (I6). Two evals below:",
        "> **GroupKFold(ep)** pools both series → identity leaks WITHIN a series (cast",
        "> recurs) → optimistic. **Leave-one-series-out** trains on one show and tests the",
        "> other → cross-cast, TRUE speaker-disjoint (I4 / ADR-002) — the honest number.",
        "",
        f"- backbone: `{BACKBONE}` (frozen, masked-mean pool) + linear probe",
        f"- series: {series_names}",
        f"- clips: {len(manifest)} human-clean · emotion {len(EMOTIONS)}-class",
        f"- split_hash (gkf): `{split_hash}` · seed {SEED}",
        f"- emotion class counts (full set): {cnt}",
        "",
        "## Eval A — GroupKFold(ep), within-pool (optimistic)",
        "",
        *_metric_rows(m_gkf),
        "",
    ]
    if m_loso is not None:
        lines += [
            "## Eval B — Leave-one-series-out, cross-cast (TRUE speaker-disjoint)",
            "",
            *_metric_rows(m_loso),
            "",
            "> The gap A→B measures how much the within-series identity leak inflates A.",
            "",
        ]
    lines += [
        "UAR (unweighted average recall = balanced accuracy) is the imbalanced-SER",
        "standard; macro-F1 shown alongside. Thin classes (fear_anxiety/sadness) have small",
        "test support — read their contribution with the CI, not point values.",
        "",
        "Anchor (NOT apples-to-apples): WavLM-Large ~34/33 macro-F1 on MSP-Podcast",
        "8-class [bimodal-ser paper 02] — different language, labels, class count.",
    ]
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


# ── change 012: label-quality ablation ───────────────────────────────────────
# Pre-registered in docs/spec/changes/012-label-quality-ablation/preregistration.md.
# Same clips, same folds, same frozen features in every arm — ONLY the training label
# column changes — and every arm is scored on the SAME fixed test labels (the clips the
# second rater left unchanged), so the delta measures the labels and not the ruler.
ARMS = ("A_owner", "B_reviewed", "C_agreed", "C_owner_sizematched")
DELTA_PAIRS = (("B_reviewed", "A_owner"), ("C_agreed", "C_owner_sizematched"))
DECISION_THRESHOLD = 0.02  # preregistration §7


def arm_spec(manifest, seed: int) -> dict:
    """arm -> (train_mask, emotion col, valence col, arousal col)."""
    import numpy as np

    n = len(manifest)
    agreed = manifest["agreed"].to_numpy() == 1
    every = np.ones(n, bool)

    # C-prime — owner labels on a size-matched subsample, stratified by (series x emotion)
    # to match C's class mix. Without it, C vs A confounds "cleaner labels" with "fewer
    # labels" (preregistration §3).
    rng = np.random.default_rng(seed)
    idx = np.arange(n)
    series, emo = manifest["series"].to_numpy(), manifest["emotion"].to_numpy()
    sized = np.zeros(n, bool)
    for (sr, em), want in manifest[agreed].groupby(["series", "emotion"]).size().items():
        pool = idx[(series == sr) & (emo == em)]
        sized[rng.choice(pool, size=min(int(want), len(pool)), replace=False)] = True

    return {
        "A_owner": (every, "emotion", "valence", "arousal"),
        "B_reviewed": (every, "emotion_reviewed", "valence_reviewed", "arousal_reviewed"),
        "C_agreed": (agreed, "emotion", "valence", "arousal"),
        "C_owner_sizematched": (sized, "emotion", "valence", "arousal"),
    }


def pool_seeds(preds):
    """Across seeds: modal emotion, mean valence/arousal (preregistration §5)."""
    import numpy as np

    emo = np.stack([p[0] for p in preds])
    modal = np.array([
        np.bincount(col[col >= 0], minlength=len(EMOTIONS)).argmax() if (col >= 0).any() else -1
        for col in emo.T
    ])
    return modal, np.mean([p[1] for p in preds], 0), np.mean([p[2] for p in preds], 0)


def paired_delta(fn, y, pred_p, pred_q, n=1000, seed=SEED):
    """Delta of a metric between two arms, bootstrapped over the SHARED test rows.

    Both arms are resampled with the same indices: the test labels are identical, so the
    only thing the interval reflects is which clips landed in the sample. Two separate
    overlapping CIs would not answer this (preregistration §5).
    """
    import numpy as np

    rng = np.random.default_rng(seed)
    point = fn(y, pred_p) - fn(y, pred_q)
    vals = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        v = fn(y[i], pred_p[i]) - fn(y[i], pred_q[i])
        if v == v:
            vals.append(v)
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return {"delta": float(point), "ci95": [float(lo), float(hi)]}


def verdict(d: dict) -> str:
    """The pre-registered decision rule (§7), applied without a chance to reinterpret."""
    lo, hi = d["ci95"]
    if lo <= 0 <= hi or abs(d["delta"]) < DECISION_THRESHOLD:
        return "H0 - label noise is not the bottleneck; stop spending adjudication on model quality"
    if d["delta"] >= DECISION_THRESHOLD:
        return "review pays off - extend it to the rest of the corpus"
    return "review makes labels WORSE - fix the guideline before annotating further"


def run_ablation(manifest, X, evals, out_dir: Path, split_hash: str) -> dict:
    import numpy as np

    # a clip an arm cannot label is a clip that breaks the fixed-set design (§2)
    missing = [c for c in ("emotion_reviewed", "valence_reviewed", "arousal_reviewed")
               if c not in manifest.columns or manifest[c].isna().any()]
    if missing or not manifest["emotion_reviewed"].isin(EMOTIONS).all():
        raise SystemExit(
            f"manifest lacks complete reviewed labels ({missing or 'bad emotion value'}) - rebuild "
            "with build_kaggle_gold.py --keys ... --reviews ..."
        )

    test_mask = manifest["agreed"].to_numpy() == 1
    # scoring ALWAYS uses the owner columns: on `agreed` rows the second rater kept them
    # byte-for-byte, so this is the one ruler both arms are measured against.
    y_emo, y_val, y_aro = encode_labels(manifest)
    print(f"[ablation] {len(manifest)} clips, test set = {int(test_mask.sum())} agreed, "
          f"seeds {SEEDS}")

    out = {"n_clips": len(manifest), "n_test": int(test_mask.sum()), "seeds": SEEDS,
           "split_hash": split_hash, "threshold": DECISION_THRESHOLD, "evals": {}}
    for ev, folds in evals.items():
        pooled, per_seed = {}, {}
        for arm in ARMS:
            preds = []
            for seed in SEEDS:
                train_mask, ec, vc, ac = arm_spec(manifest, seed)[arm]
                emo_l, val_l, aro_l = encode_labels(manifest, ec, vc, ac)
                preds.append(oof_predict(X, folds, emo_l, val_l, aro_l,
                                         train_mask=train_mask, seed=seed))
                per_seed.setdefault(arm, []).append(
                    score(y_emo, preds[-1][0], y_val, preds[-1][1], y_aro, preds[-1][2],
                          test_mask)["emotion_macro_f1"])
                print(f"[ablation] {ev} · {arm} · seed {seed} · train n={int(train_mask.sum())}")
            pooled[arm] = pool_seeds(preds)

        arms_out = {
            arm: {**score(y_emo, pooled[arm][0], y_val, pooled[arm][1], y_aro, pooled[arm][2],
                          test_mask),
                  "macro_f1_per_seed": per_seed[arm],
                  "train_n": int(arm_spec(manifest, SEEDS[0])[arm][0].sum())}
            for arm in ARMS
        }
        keep = test_mask & (y_emo >= 0)
        yt = y_emo[keep]
        deltas = {}
        for hi_arm, lo_arm in DELTA_PAIRS:
            d = paired_delta(lambda a, b: macro_f1(a, b, len(EMOTIONS)),
                             yt, pooled[hi_arm][0][keep], pooled[lo_arm][0][keep])
            diff = np.array(per_seed[hi_arm]) - np.array(per_seed[lo_arm])
            d["seed_range"] = [float(diff.min()), float(diff.max())]
            deltas[f"{hi_arm}-{lo_arm}"] = d
        out["evals"][ev] = {"arms": arms_out, "deltas": deltas}

    (out_dir / "metrics_ablation.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    write_ablation_report(out, out_dir)
    return out


def write_ablation_report(out: dict, out_dir: Path) -> None:
    lines = [
        "# Change 012 - label-quality ablation (pre-registered)",
        "",
        f"- clips: {out['n_clips']} (fixed set, identical in every arm)",
        f"- test set: **{out['n_test']} clips the second rater left unchanged** - same labels",
        "  for every arm, so only the TRAINING labels vary.",
        f"- seeds: {out['seeds']} · split_hash `{out['split_hash']}`",
        "",
        "> This is NOT a kappa and NOT a headline accuracy. The review pass was anchored",
        "> (the rater saw the owner's label first) - preregistration §8.",
    ]
    for ev, blk in out["evals"].items():
        lines += ["", f"## Eval - {ev}", "",
                  "| Arm | train n | macro-F1 | 95% CI | UAR | CCC val | CCC aro |",
                  "|---|--:|--:|---|--:|--:|--:|"]
        for arm, m in blk["arms"].items():
            lo, hi = m["emotion_macro_f1_ci95"]
            lines.append(
                f"| {arm} | {m['train_n']} | {m['emotion_macro_f1']:.3f} | [{lo:.3f}, {hi:.3f}] | "
                f"{m['emotion_uar']:.3f} | {m['ccc_valence']:.3f} | {m['ccc_arousal']:.3f} |")
        lines += ["", "### Paired deltas (macro-F1, shared bootstrap over test clips)", "",
                  "| Comparison | Δ | 95% CI | per-seed Δ range | verdict (§7) |",
                  "|---|--:|---|---|---|"]
        for name, d in blk["deltas"].items():
            lo, hi = d["ci95"]
            r0, r1 = d["seed_range"]
            lines.append(f"| {name} | {d['delta']:+.3f} | [{lo:+.3f}, {hi:+.3f}] | "
                         f"[{r0:+.3f}, {r1:+.3f}] | {verdict(d)} |")
    lines += ["", "The decision rule was fixed before the run; the verdict column applies it",
              "mechanically. `C_agreed` vs `A_owner` is NOT a valid comparison (different",
              "training-set size) - compare it to `C_owner_sizematched` instead."]
    (out_dir / "ablation.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))

def _resolve_input_root() -> Path:
    """Locate the folder holding manifest.csv.

    Honors VNSER_INPUT for local runs; on Kaggle the dataset mount slug can differ
    from the ref, so search /kaggle/input for the manifest instead of hardcoding.
    """
    env = os.environ.get("VNSER_INPUT")
    if env:
        return Path(env)
    default = Path("/kaggle/input/viemospeech-pilot")
    if (default / "manifest.csv").exists():
        return default
    for m in Path("/kaggle/input").glob("*/**/manifest.csv"):
        print(f"[data] resolved input root -> {m.parent}")
        return m.parent
    raise FileNotFoundError(
        "manifest.csv not found under /kaggle/input — is the dataset attached? "
        f"contents: {[str(p) for p in Path('/kaggle/input').glob('*')]}"
    )


def main() -> None:
    global EMOTIONS  # narrowed to the classes the manifest carries, below
    sys.stdout.reconfigure(encoding="utf-8")
    if ON_KAGGLE and not SMOKE:
        _pip_install()

    import numpy as np
    import pandas as pd

    input_root = _resolve_input_root()
    out_dir = Path(os.environ.get("VNSER_OUTPUT", "/kaggle/working"))
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = pd.read_csv(input_root / "manifest.csv")
    # human-clean manifest (build_kaggle_gold.py): every row has a human emotion, not
    # rejected, not multi. Keep rows with a valid emotion + valence/arousal present.
    manifest = manifest[manifest["emotion"].isin(EMOTIONS)]
    manifest = manifest.dropna(subset=["valence", "arousal"]).reset_index(drop=True)
    manifest["series"] = manifest["ep"].str.split("/").str[0]
    # A Kaggle script kernel gets no env vars, so the MANIFEST picks the mode: the
    # ablation dataset is exactly the one carrying a second rater's columns (change 012).
    # build_kaggle_gold.py always writes the column, so test for values, not presence.
    ablate = ABLATION or (
        "emotion_reviewed" in manifest.columns and manifest["emotion_reviewed"].notna().any()
    )
    if not ablate:  # ADR-006; change 012 stays on the 7 classes it was frozen with
        manifest = manifest[~manifest["emotion"].isin(BENCHMARK_EXCLUDE)].reset_index(drop=True)
    # The label set is whatever canonical classes the manifest carries: a class-subset
    # dataset (build_kaggle_gold.py --drop-emotions) must not be scored as 7-class, or
    # macro-F1 averages in zeros for classes that cannot occur.
    EMOTIONS = [e for e in EMOTIONS if (manifest["emotion"] == e).any()]
    if SMOKE:
        # keep a slice from EACH series so the leave-one-series-out path also runs
        manifest = manifest.groupby("series", group_keys=False).head(30).reset_index(drop=True)
    print(f"[data] {len(manifest)} clean clips from {input_root} · "
          f"mode={'ablation (change 012)' if ablate else 'baseline'}")

    gkf = np.array(assign_folds(manifest))
    manifest["fold"] = gkf
    feats = extract_features(manifest, input_root, out_dir / "features_wavlm-large.npz")
    X = np.stack([feats[c] for c in manifest["clip"]])

    series_names = sorted(manifest["series"].unique())
    sfolds = None
    if len(series_names) >= 2:
        smap = {s: i for i, s in enumerate(series_names)}
        sfolds = manifest["series"].map(smap).to_numpy()
    # eval A: GroupKFold(ep) — within-pool (identity leaks within a series)
    # eval B: leave-one-series-out — cross-cast, TRUE speaker-disjoint
    m_gkf, oof_gkf = (None, None) if ablate else cv_metrics(manifest, X, gkf)
    m_loso, oof_loso = (None, None) if ablate or sfolds is None else cv_metrics(manifest, X, sfolds)

    import hashlib
    pairs = sorted(f"{c},{f}" for c, f in zip(manifest["clip"], gkf))
    split_hash = hashlib.md5("\n".join(pairs).encode()).hexdigest()

    if ablate:  # change 012 — label arms, not a new baseline
        evals = {"groupkfold": gkf}
        if sfolds is not None:
            evals["leave_one_series_out"] = sfolds
        run_ablation(manifest, X, evals, out_dir, split_hash)
        return
    art = out_dir / "artifact_wavlm-large"
    art.mkdir(exist_ok=True)
    (art / "config.json").write_text(json.dumps({
        "backbone": BACKBONE, "emotions": EMOTIONS, "n_splits": N_SPLITS, "seed": SEED,
        "split_hash": split_hash, "pip_pins": PIP_PINS, "n_clips": len(manifest),
        "series": series_names, "label_source": "human single-annotator (ADR-003)",
        "eval_groupkfold": "GroupKFold(ep) — within-pool, identity leaks within series",
        "eval_leave_one_series_out": "cross-cast, true speaker-disjoint (I4/ADR-002)",
        "metrics_groupkfold": m_gkf, "metrics_leave_one_series_out": m_loso,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "metrics.json").write_text(json.dumps(
        {"groupkfold": m_gkf, "leave_one_series_out": m_loso}, indent=2), encoding="utf-8")
    # per-clip out-of-fold predictions, for listening checks (tools: build_inspect_page.py).
    # ids + labels + predictions only: no audio, no transcript (I1).
    pred = manifest[["ep", "id", "clip", "series", "fold", "emotion", "valence", "arousal"]].copy()
    for name, oof in (("gkf", oof_gkf), ("loso", oof_loso)):
        if oof is None:
            continue
        pred[f"pred_{name}"] = [EMOTIONS[i] if i >= 0 else "" for i in oof[0]]
        pred[f"pred_valence_{name}"] = np.round(oof[1], 3)
        pred[f"pred_arousal_{name}"] = np.round(oof[2], 3)
    pred.to_csv(out_dir / "predictions.csv", index=False)
    write_report(m_gkf, m_loso, series_names, manifest, out_dir, split_hash)


if __name__ == "__main__":
    main()
