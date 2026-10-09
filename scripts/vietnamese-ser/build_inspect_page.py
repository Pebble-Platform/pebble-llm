"""Local listening page: each clip at three stages, to catch data that went wrong.

  1. before processing -- the same [start, end] cut from the ORIGINAL episode mp3 (music
     still in), stream-copied with ffmpeg so nothing is re-encoded;
  2. after processing  -- the 16 kHz mono Demucs-vocals clip the model trains on;
  3. test              -- the owner label and the out-of-fold prediction of a vnser-train
     run (predictions.csv: LOSO and GroupKFold), right / wrong / not in the benchmark.

Plus a few automatic checks per clip (too short, quiet, clipped, mostly silent, clip
length != manifest length, vocals much quieter than the original) so suspicious clips
can be filtered instead of found by ear.

LOCAL ONLY: the page, the original-audio cuts and the transcripts it shows are written
under data/ (gitignored) and reference clips on this machine. Never commit or upload the
output (intent constraint 1).

    PYTHONIOENCODING=utf-8 .venv-vnser/Scripts/python.exe scripts/vietnamese-ser/build_inspect_page.py \
        --predictions docs/reports/baseline-5cls-v9/predictions.csv
    start data/vietnamese-ser/inspect/index.html
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "vietnamese-ser"

# heuristic flags -- shown on the page with these thresholds, never used to drop data
SHORT_S, LONG_S = 1.0, 15.0
QUIET_DBFS = -35.0
CLIP_FRAC = 0.001
SILENT_FRAC = 0.5
DUR_TOL_S = 0.05
VOCAL_DROP_DB = -12.0
# pilot_extract.py pads every cut by PAD on each side (clamped at t=0), so a clip is
# 0, 0.1 or 0.2 s longer than end - start; anything else means label and wav disagree
PAD = 0.10


def dbfs(x: np.ndarray) -> float:
    return float(20 * np.log10(np.sqrt(np.mean(x**2)) + 1e-9))


def read_mono(path: Path) -> tuple[np.ndarray, int]:
    x, sr = sf.read(path, dtype="float32")
    return (x.mean(axis=1) if x.ndim > 1 else x), sr


def cut_original(src: Path, dst: Path, start: float, end: float) -> bool:
    if dst.is_file():
        return True
    dst.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-ss",
            f"{start:.3f}",
            "-to",
            f"{end:.3f}",
            "-i",
            str(src),
            "-c",
            "copy",
            str(dst),
        ],
        capture_output=True,
    )
    return r.returncode == 0 and dst.is_file()


def pred(r, ev: str) -> dict | None:
    """One eval's prediction for a manifest row; None if the clip is not in the benchmark."""
    e = getattr(r, f"pred_{ev}")
    if not isinstance(e, str):
        return None
    return {
        "e": e,
        "v": float(getattr(r, f"pred_valence_{ev}")),
        "a": float(getattr(r, f"pred_arousal_{ev}")),
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--manifest",
        default=str(DATA / "kaggle-upload" / "viemospeech-pilot" / "manifest.csv"),
        help="the manifest the predictions were made on (all 7 labels)",
    )
    ap.add_argument("--predictions", required=True, help="predictions.csv from a vnser-train run")
    ap.add_argument("--episodes", default=str(DATA / "episodes"))
    ap.add_argument("--raw", default=str(DATA / "raw"))
    ap.add_argument("--out", default=str(DATA / "inspect"))
    a = ap.parse_args()

    out, episodes, raw = Path(a.out), Path(a.episodes), Path(a.raw)
    m = pd.read_csv(a.manifest)
    p = pd.read_csv(a.predictions)
    m = m.merge(
        p[[c for c in p.columns if c.startswith("pred_")] + ["ep", "id", "fold"]],
        on=["ep", "id"],
        how="left",
    )
    print(f"{len(m)} clips in manifest, {m['pred_loso'].notna().sum()} with predictions")

    rows, failed = [], 0
    for i, r in enumerate(m.itertuples(index=False)):
        series, ep_name = r.ep.split("/", 1)
        clip = episodes / r.ep / "clips" / f"{r.id}.wav"
        orig = out / "original" / series / ep_name / f"{r.id}.mp3"
        no_ts = not (r.end > r.start)  # label row without usable timestamps
        ok = not no_ts and cut_original(
            raw / series / f"{ep_name}.mp3", orig, max(0.0, r.start - PAD), r.end + PAD
        )
        failed += not ok and not no_ts

        x, sr = read_mono(clip)
        dur = len(x) / sr
        frames = x[: len(x) // 400 * 400].reshape(-1, 400)  # 25 ms frames at 16 kHz
        silent = float((20 * np.log10(np.sqrt((frames**2).mean(1)) + 1e-9) < -45).mean())
        clip_level, peak = dbfs(x), float(np.abs(x).max())
        orig_level = dbfs(read_mono(orig)[0]) if ok else None

        flags = []
        if dur < SHORT_S:
            flags.append("ngắn")
        if dur > LONG_S:
            flags.append("dài")
        if clip_level < QUIET_DBFS:
            flags.append("nhỏ tiếng")
        if (np.abs(x) >= 0.999).mean() > CLIP_FRAC:
            flags.append("clipping")
        if silent > SILENT_FRAC:
            flags.append("nhiều im lặng")
        if not no_ts and min(abs(dur - r.dur - k) for k in (0, PAD, 2 * PAD)) > DUR_TOL_S:
            flags.append("lệch độ dài")
        if no_ts:
            flags.append("thiếu timestamp")
        if orig_level is not None and clip_level - orig_level < VOCAL_DROP_DB:
            flags.append("giọng mất sau tách nhạc")
        if not ok and not no_ts:
            flags.append("không cắt được bản gốc")

        rows.append(
            {
                "ep": r.ep,
                "id": r.id,
                "series": series,
                "t": [r.start, r.end],
                "emo": r.emotion,
                "val": r.valence,
                "aro": r.arousal,
                "text": r.gold_text if isinstance(r.gold_text, str) else "",
                "dur": round(dur, 2),
                "sr": sr,
                "db": round(clip_level, 1),
                "db_orig": None if orig_level is None else round(orig_level, 1),
                "peak": round(peak, 3),
                "silent": round(silent, 2),
                "flags": flags,
                "orig": os.path.relpath(orig, out).replace("\\", "/"),
                "clip": os.path.relpath(clip, out).replace("\\", "/"),
                "loso": pred(r, "loso"),
                "gkf": pred(r, "gkf"),
                "fold": None if pd.isna(r.fold) else int(r.fold),
            }
        )
        if (i + 1) % 200 == 0:
            print(f"  {i + 1}/{len(m)}")

    meta = {
        "manifest": str(Path(a.manifest).relative_to(ROOT)).replace("\\", "/"),
        "predictions": str(Path(a.predictions).resolve().relative_to(ROOT)).replace("\\", "/"),
        "thresholds": {
            "short_s": SHORT_S,
            "long_s": LONG_S,
            "quiet_dbfs": QUIET_DBFS,
            "clip_frac": CLIP_FRAC,
            "silent_frac": SILENT_FRAC,
            "dur_tol_s": DUR_TOL_S,
            "pad_s": PAD,
            "vocal_drop_db": VOCAL_DROP_DB,
        },
    }
    template = (Path(__file__).parent / "inspect_page.html").read_text(encoding="utf-8")
    html = template.replace(
        "/*__DATA__*/null", json.dumps({"meta": meta, "rows": rows}, ensure_ascii=False)
    )
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")
    n_flag = sum(1 for r in rows if r["flags"])
    print(
        f"wrote {out / 'index.html'} · {len(rows)} clips · {n_flag} flagged · {failed} original cuts failed"
    )


if __name__ == "__main__":
    main()
