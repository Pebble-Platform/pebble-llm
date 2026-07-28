"""Package HUMAN-labeled clips (state.db) into the PRIVATE Kaggle pilot dataset.

Current-truth export (ADR-003: human labels are the corpus; the older
build_kaggle_dataset.py packaged the superseded 2-teacher view). Sources
tools/labeler's label store via ``labeler_store.read_records`` (state.db, ADR-004):
keeps clips with a human ``emotion`` and not ``rejected``; copies their wav;
writes manifest.csv + metadata; optionally pushes.

Manifest columns (per user decision 2026-07-20): emotion / valence / arousal +
timestamps + human text, NO speaker/gender/age — speakers are still raw diarization
ids (not yet reassigned to cast characters), so those fields would ship the known
wrong values. Teacher emotion is kept as a *suggestion* column only (not a label).

Usage (from repo root):
  PYTHONIOENCODING=utf-8 python scripts/vietnamese-ser/build_kaggle_gold.py         # stage only
  PYTHONIOENCODING=utf-8 python scripts/vietnamese-ser/build_kaggle_gold.py --push  # + version dataset

PRIVATE only: clips derive from copyrighted episodes — research use, NEVER public
(intent constraint #1). Uploading to a private dataset is the user's risk call
(scale-plan §6, PA A).
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

from labeler_store import read_records

ROOT = Path(__file__).resolve().parents[2]
SLUG = "viemospeech-pilot"
EPISODES = ROOT / "data" / "vietnamese-ser" / "episodes"

COLS = [
    "ep",
    "id",
    "clip",
    "start",
    "end",
    "dur",
    "emotion",
    "valence",
    "arousal",
    "gold_text",
    "opus_suggest",
    "sonnet_suggest",
    "annotator",
    "ts",
]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--owner", default="phatneurondai")
    ap.add_argument("--push", action="store_true")
    args = ap.parse_args()

    recs = read_records(EPISODES)

    stage = ROOT / "data" / "vietnamese-ser" / "kaggle-upload" / SLUG
    clips_out = stage / "clips"
    if stage.exists():
        shutil.rmtree(stage)  # clean rebuild so a re-run doesn't ship stale clips
    clips_out.mkdir(parents=True, exist_ok=True)

    rows, skipped_no_wav = [], 0
    for r in recs:
        # corpus-clean (I3): human emotion, not rejected, not human-flagged multi-voice
        if not r.get("emotion") or r.get("rejected") or r.get("multi"):
            continue
        src = EPISODES / r["epKey"] / "clips" / f"{r['id']}.wav"
        if not src.is_file():
            skipped_no_wav += 1
            continue
        clip_name = r["epKey"].replace("/", "__") + f"__{r['id']}.wav"
        shutil.copy2(src, clips_out / clip_name)
        start, end = r.get("start"), r.get("end")
        dur = (
            round(end - start, 3)
            if isinstance(start, (int, float)) and isinstance(end, (int, float))
            else ""
        )
        rows.append(
            [
                r["epKey"],
                r["id"],
                f"clips/{clip_name}",
                start,
                end,
                dur,
                r["emotion"],
                r.get("valence"),
                r.get("arousal"),
                r.get("gold_text", ""),
                r.get("opus", ""),
                r.get("sonnet", ""),
                r.get("annotator", ""),
                r.get("ts", ""),
            ]
        )

    with (stage / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        w.writerows(rows)

    (stage / "README.md").write_text(
        f"# ViEmoSpeech pilot — human labels (PRIVATE, research only)\n\n"
        f"Utterances: {len(rows)} (human `emotion`, rejected excluded). Clips 16 kHz "
        f"mono, cut from Demucs vocals.\n\n"
        f"Labels are single human annotator (state.db, tools/labeler). Columns: "
        f"emotion (7-class), valence/arousal (1-5), gold_text (human-corrected), plus "
        f"opus_suggest/sonnet_suggest = LLM *suggestions* (NOT labels, ADR-003).\n\n"
        f"**No speaker/gender/age**: speakers not yet reassigned from diarization ids "
        f"to cast characters — omitted rather than ship wrong values.\n\n"
        f"Derived from copyrighted VN TV drama — research use, **never make public**.\n",
        encoding="utf-8",
    )
    (stage / "dataset-metadata.json").write_text(
        json.dumps(
            {
                "title": "ViEmoSpeech pilot (private)",
                "id": f"{args.owner}/{SLUG}",
                "licenses": [{"name": "other"}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"staged: {stage}")
    print(
        f"utterances={len(rows)}  clips={len(list(clips_out.glob('*.wav')))}  "
        f"skipped_no_wav={skipped_no_wav}"
    )

    if args.push:
        st = subprocess.run(
            ["uvx", "--from", "kaggle", "kaggle", "datasets", "status", f"{args.owner}/{SLUG}"],
            capture_output=True,
            text=True,
        )
        exists = st.returncode == 0 and "not found" not in (st.stdout + st.stderr).lower()
        # Run from the staging PARENT with a single-segment -p (SLUG). The kaggle CLI
        # on Windows builds a temp upload path from the -p value; a multi-segment path
        # (data/.../viemospeech-pilot) yields uploads\data/.../<slug>_manifest.csv.json
        # whose intermediate dirs don't exist -> manifest.csv fails with ENOENT while
        # clips.zip still uploads. A one-level -p keeps the temp name flat.
        action = "version" if exists else "create"  # create = private by default
        cmd = ["uvx", "--from", "kaggle", "kaggle", "datasets", action,
               "-p", SLUG, "--dir-mode", "zip"]
        if exists:
            cmd += ["-m", f"human labels: {len(rows)} utt"]
        subprocess.run(cmd, check=True, cwd=stage.parent)
        print("pushed (private).")


if __name__ == "__main__":
    main()
