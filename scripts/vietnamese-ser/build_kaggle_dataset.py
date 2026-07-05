"""Package labeled episodes into a PRIVATE Kaggle dataset for pilot SER training.

Collects every episode under episodes/<series>/ that has BOTH labels_opus.csv and
labels_sonnet.csv, builds one manifest.csv (segments x both teachers + consensus +
clean flag), copies clips into a staging dir, writes dataset-metadata.json, then
creates/updates the Kaggle dataset via the CLI (uvx kaggle).

Manifest columns:
  ep,id,clip,start,end,dur,speaker,text_phowhisper,text_youtube,
  emotion_opus,emotion_sonnet,emotion_consensus (empty when teachers disagree),
  valence_mean,arousal_mean,distress_or,multi_speaker_or,conf_min,is_clean
`is_clean` = has speaker AND not multi_speaker_or  ->  the pilot-training subset.

Usage:
  PYTHONIOENCODING=utf-8 python scripts/vietnamese-ser/build_kaggle_dataset.py \
      --series ve-nha-di-con [--push]
Without --push it only stages (data/vietnamese-ser/kaggle-upload/) for inspection.

PRIVATE dataset only (is_private in metadata): clips derive from copyrighted
episodes — research use, never make this public (intent constraint #1).
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SLUG = "viemospeech-pilot"


def load(p: Path) -> dict[str, dict]:
    return {r["id"]: r for r in csv.DictReader(p.open(encoding="utf-8"))}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--series", default="ve-nha-di-con")
    ap.add_argument("--owner", default="phatneurondai")
    ap.add_argument("--push", action="store_true")
    args = ap.parse_args()

    epsdir = ROOT / "data" / "vietnamese-ser" / "episodes" / args.series
    stage = ROOT / "data" / "vietnamese-ser" / "kaggle-upload" / SLUG
    clips_out = stage / "clips"
    clips_out.mkdir(parents=True, exist_ok=True)

    rows_out: list[list] = []
    eps_used: list[str] = []
    for epdir in sorted(epsdir.glob("ep*")):
        lo, ls = epdir / "labels_opus.csv", epdir / "labels_sonnet.csv"
        seg_f, yt_f = epdir / "segments.csv", epdir / "transcripts_yt.csv"
        if not (lo.exists() and ls.exists() and seg_f.exists() and yt_f.exists()):
            continue
        ep = epdir.name
        eps_used.append(ep)
        op, so, yt = load(lo), load(ls), load(yt_f)
        for s in csv.DictReader(seg_f.open(encoding="utf-8")):
            i = s["id"]
            o, n, y = op.get(i), so.get(i), yt.get(i, {})
            if not (o and n):
                continue
            clip_src = epdir / "clips" / f"{i}.wav"
            clip_name = f"{ep}_{i}.wav"
            if clip_src.exists() and not (clips_out / clip_name).exists():
                shutil.copy2(clip_src, clips_out / clip_name)
            dis_or = "True" in (o["distress"], n["distress"])
            mss_or = "True" in (o["multi_speaker_suspect"], n["multi_speaker_suspect"])
            consensus = o["emotion"] if o["emotion"] == n["emotion"] else ""
            clean = bool(s.get("speaker", "").strip()) and not mss_or
            rows_out.append([
                ep, i, f"clips/{clip_name}", s["start"], s["end"], s["dur"],
                s.get("speaker", ""), y.get("text_phowhisper", ""), y.get("text_youtube", ""),
                o["emotion"], n["emotion"], consensus,
                (int(o["valence"]) + int(n["valence"])) / 2,
                (int(o["arousal"]) + int(n["arousal"])) / 2,
                dis_or, mss_or,
                min(float(o["confidence"]), float(n["confidence"])), clean,
            ])

    with (stage / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ep", "id", "clip", "start", "end", "dur", "speaker",
                    "text_phowhisper", "text_youtube", "emotion_opus", "emotion_sonnet",
                    "emotion_consensus", "valence_mean", "arousal_mean", "distress_or",
                    "multi_speaker_or", "conf_min", "is_clean"])
        w.writerows(rows_out)

    n_clean = sum(1 for r in rows_out if r[-1])
    n_cons = sum(1 for r in rows_out if r[11])
    (stage / "README.md").write_text(
        f"# ViEmoSpeech pilot (PRIVATE — research only)\n\n"
        f"Episodes: {', '.join(eps_used)} · utterances: {len(rows_out)} · "
        f"clean (single-speaker, both gates): {n_clean} · teacher-consensus emotion: {n_cons}.\n"
        f"Clips 16 kHz mono, cut from Demucs vocals at speaker-turn boundaries.\n"
        f"Labels: two independent LLM teachers (opus/sonnet), prompt versioned in the\n"
        f"pebble-llm repo (scripts/vietnamese-ser/m4_prompt.md). Train on is_clean rows;\n"
        f"use emotion_consensus (or teacher columns for soft labels).\n",
        encoding="utf-8")
    (stage / "dataset-metadata.json").write_text(json.dumps({
        "title": "ViEmoSpeech pilot (private)",
        "id": f"{args.owner}/{SLUG}",
        "licenses": [{"name": "other"}],
    }, indent=2), encoding="utf-8")

    print(f"staged: {stage}")
    print(f"eps={eps_used} rows={len(rows_out)} clean={n_clean} consensus={n_cons} "
          f"clips={len(list(clips_out.glob('*.wav')))}")

    if args.push:
        r = subprocess.run(["uvx", "--from", "kaggle", "kaggle", "datasets", "status",
                            f"{args.owner}/{SLUG}"], capture_output=True, text=True)
        if "not found" in (r.stdout + r.stderr).lower() or r.returncode != 0:
            cmd = ["uvx", "--from", "kaggle", "kaggle", "datasets", "create",
                   "-p", str(stage), "--dir-mode", "zip"]
        else:
            cmd = ["uvx", "--from", "kaggle", "kaggle", "datasets", "version",
                   "-p", str(stage), "--dir-mode", "zip", "-m", f"eps {','.join(eps_used)}"]
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
