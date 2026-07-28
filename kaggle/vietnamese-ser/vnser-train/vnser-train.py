"""vnser-train — pilot SER baseline (speech-only, frozen WavLM-Large) on ViEmoSpeech.

HUMAN-LABEL era (ADR-003): the corpus label of record is the human `emotion` /
`valence` / `arousal` from tools/labeler (state.db), NOT the 2-teacher consensus the
earlier version of this kernel trained on. Reads the private Kaggle dataset
`phatneurondai/viemospeech-pilot` (manifest.csv built by
scripts/vietnamese-ser/build_kaggle_gold.py + clips/*.wav 16kHz), extracts a frozen
WavLM-Large embedding per clip (masked-mean pool, cached), trains two linear-probe
heads:
  * emotion  — 7-class (neutral/anger/joy/fear_anxiety/sadness/disgust/surprise),
               weighted-CE by class frequency. Reported with macro-F1 AND UAR
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
BACKBONE = "microsoft/wavlm-large"
N_SPLITS = 5
SEED = 0
GROUP_COL = "ep"  # fold by episode (speaker diarization ids are unreliable, not remapped)

SMOKE = os.environ.get("VNSER_SMOKE") == "1"
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
def _train_linear(X, y, task: str, n_classes: int, class_w=None, epochs=200):
    import torch

    torch.manual_seed(SEED)
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
def cv_metrics(manifest, X, folds):
    """Out-of-fold CV over an arbitrary integer `folds` array; returns metrics.

    Called twice: GroupKFold(ep) (within-pool, identity leaks within a series) and
    leave-one-series-out (cross-cast → true speaker-disjoint).
    """
    import numpy as np
    import torch

    fold_ids = sorted(set(int(f) for f in folds))
    oof_emo = np.full(len(manifest), -1)
    oof_val = np.full(len(manifest), np.nan)
    oof_aro = np.full(len(manifest), np.nan)

    emo_idx = {e: i for i, e in enumerate(EMOTIONS)}
    emo_label = np.array([emo_idx.get(e, -1) for e in manifest["emotion"]])
    val = manifest["valence"].to_numpy(float)
    aro = manifest["arousal"].to_numpy(float)

    for f in fold_ids:
        tr, va = folds != f, folds == f
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
                class_w=cw, epochs=40 if SMOKE else 200,
            )
            with torch.no_grad():
                p = head(torch.tensor((X[eva] - mu) / sd, dtype=torch.float32,
                                      device=next(head.parameters()).device))
            oof_emo[eva] = p.argmax(1).cpu().numpy()

        # affect (all rows)
        head = _train_linear(Xtr, np.stack([val[tr], aro[tr]], 1), "reg2", 2,
                             epochs=40 if SMOKE else 300)
        with torch.no_grad():
            p = head(torch.tensor(Xva, dtype=torch.float32,
                                  device=next(head.parameters()).device)).cpu().numpy()
        oof_val[va], oof_aro[va] = p[:, 0], p[:, 1]
        print(f"[cv] fold {f} done")

    em = emo_label >= 0
    f1 = macro_f1(emo_label[em], oof_emo[em], len(EMOTIONS))
    f1_ci = bootstrap_ci(lambda a, b: macro_f1(a, b, len(EMOTIONS)), emo_label[em], oof_emo[em])
    ua = uar(emo_label[em], oof_emo[em], len(EMOTIONS))
    ua_ci = bootstrap_ci(lambda a, b: uar(a, b, len(EMOTIONS)), emo_label[em], oof_emo[em])
    cv, cv_ci = ccc(val, oof_val), bootstrap_ci(ccc, val, oof_val)
    ca, ca_ci = ccc(aro, oof_aro), bootstrap_ci(ccc, aro, oof_aro)
    per_class = {EMOTIONS[c]: int((emo_label[em] == c).sum()) for c in range(len(EMOTIONS))}
    return {
        "emotion_macro_f1": f1, "emotion_macro_f1_ci95": f1_ci,
        "emotion_uar": ua, "emotion_uar_ci95": ua_ci,
        "emotion_n": int(em.sum()), "emotion_support": per_class,
        "ccc_valence": cv, "ccc_valence_ci95": cv_ci,
        "ccc_arousal": ca, "ccc_arousal_ci95": ca_ci,
    }


def _metric_rows(m: dict) -> list[str]:
    return [
        "| Head | Metric | Value | 95% CI |",
        "|---|---|---|---|",
        f"| emotion (7-class) | macro-F1 | {m['emotion_macro_f1']:.3f} | "
        f"[{m['emotion_macro_f1_ci95'][0]:.3f}, {m['emotion_macro_f1_ci95'][1]:.3f}] |",
        f"| emotion (7-class) | UAR | {m['emotion_uar']:.3f} | "
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
        "> ⚠ **PILOT, HUMAN single-annotator labels (no inter-annotator κ yet — ADR-003).**",
        "> Report as pilot baselines, NOT a settled accuracy claim (I6). Two evals below:",
        "> **GroupKFold(ep)** pools both series → identity leaks WITHIN a series (cast",
        "> recurs) → optimistic. **Leave-one-series-out** trains on one show and tests the",
        "> other → cross-cast, TRUE speaker-disjoint (I4 / ADR-002) — the honest number.",
        "",
        f"- backbone: `{BACKBONE}` (frozen, masked-mean pool) + linear probe",
        f"- series: {series_names}",
        f"- clips: {len(manifest)} human-clean · emotion 7-class",
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
        "standard; macro-F1 shown alongside. Thin classes (surprise/disgust) have small",
        "test support — read their contribution with the CI, not point values.",
        "",
        "Anchor (NOT apples-to-apples): WavLM-Large ~34/33 macro-F1 on MSP-Podcast",
        "8-class [bimodal-ser paper 02] — different language, labels, class count.",
    ]
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
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
    if SMOKE:
        # keep a slice from EACH series so the leave-one-series-out path also runs
        manifest = manifest.groupby("series", group_keys=False).head(30).reset_index(drop=True)
    print(f"[data] {len(manifest)} clean clips from {input_root}")

    gkf = np.array(assign_folds(manifest))
    manifest["fold"] = gkf
    feats = extract_features(manifest, input_root, out_dir / "features_wavlm-large.npz")
    X = np.stack([feats[c] for c in manifest["clip"]])

    # eval A: GroupKFold(ep) — within-pool (identity leaks within a series)
    m_gkf = cv_metrics(manifest, X, gkf)
    # eval B: leave-one-series-out — cross-cast, TRUE speaker-disjoint
    series_names = sorted(manifest["series"].unique())
    m_loso = None
    if len(series_names) >= 2:
        smap = {s: i for i, s in enumerate(series_names)}
        sfolds = manifest["series"].map(smap).to_numpy()
        m_loso = cv_metrics(manifest, X, sfolds)

    import hashlib
    pairs = sorted(f"{c},{f}" for c, f in zip(manifest["clip"], gkf))
    split_hash = hashlib.md5("\n".join(pairs).encode()).hexdigest()
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
    write_report(m_gkf, m_loso, series_names, manifest, out_dir, split_hash)


if __name__ == "__main__":
    main()
