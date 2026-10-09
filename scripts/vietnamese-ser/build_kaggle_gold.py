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

``--keys`` restricts the export to the clips listed in a queue TSV and ``--reviews``
joins a second rater's pass from ``gold-reviews/<user>.json`` into the *_reviewed
columns. Together they stage the fixed clip set for the label-quality ablation
(change 012 §2): same clips in every arm, only the label column differs.

Usage (from repo root):
  PYTHONIOENCODING=utf-8 python scripts/vietnamese-ser/build_kaggle_gold.py         # stage only
  PYTHONIOENCODING=utf-8 python scripts/vietnamese-ser/build_kaggle_gold.py --push  # + version dataset
  # change 012 ablation set (1071 clips, owner + reviewed labels side by side):
  PYTHONIOENCODING=utf-8 python scripts/vietnamese-ser/build_kaggle_gold.py \
      --slug viemospeech-ablation-012 \
      --keys docs/spec/changes/011-online-multi-annotator/review-candidates.tsv \
      --reviews data/vietnamese-ser/episodes/gold-reviews/vyphan.json

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
    "emotion_reviewed",
    "valence_reviewed",
    "arousal_reviewed",
    "agreed",
    "opus_suggest",
    "sonnet_suggest",
    "annotator",
    "ts",
]


def _read_keys(path: Path) -> set[str]:
    """'epKey/clip_id' keys from a queue TSV (first column, '#' comments skipped)."""
    return {
        ln.split("	")[0]
        for ln in path.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.startswith("#")
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--owner", default="phatneurondai")
    ap.add_argument("--push", action="store_true")
    ap.add_argument(
        "--slug",
        default=SLUG,
        help="dataset slug; use a separate one for an "
        "ablation set so the pilot dataset is not overwritten",
    )
    ap.add_argument("--keys", help="queue TSV; keep only its 'epKey/clip_id' rows (change 012 §2)")
    ap.add_argument("--reviews", help="gold-reviews/<user>.json; join the 2nd rater's pass")
    ap.add_argument(
        "--drop-emotions",
        default="",
        help="comma list of emotions whose clips are left out (class-subset run); "
        "the kernel then trains/scores only the classes present",
    )
    args = ap.parse_args()
    drop = {e for e in args.drop_emotions.split(",") if e}

    recs = read_records(EPISODES)
    keys = _read_keys(Path(args.keys)) if args.keys else None
    reviews = json.loads(Path(args.reviews).read_text(encoding="utf-8")) if args.reviews else {}

    stage = ROOT / "data" / "vietnamese-ser" / "kaggle-upload" / args.slug
    clips_out = stage / "clips"
    if stage.exists():
        shutil.rmtree(stage)  # clean rebuild so a re-run doesn't ship stale clips
    clips_out.mkdir(parents=True, exist_ok=True)

    rows, skipped_no_wav, skipped_off_queue, skipped_rev_rejected = [], 0, 0, 0
    for r in recs:
        # corpus-clean (I3): human emotion, not rejected, not human-flagged multi-voice
        if not r.get("emotion") or r.get("rejected") or r.get("multi"):
            continue
        if r["emotion"] in drop:
            continue
        key = f"{r['epKey']}/{r['id']}"
        if keys is not None and key not in keys:
            skipped_off_queue += 1
            continue
        rev = reviews.get(key)
        if rev and rev.get("rejected"):
            # the 2nd rater threw the clip out: drop it from EVERY arm rather than ship
            # a row that only one arm can train on (change 012 §2 -- fixed clip set).
            skipped_rev_rejected += 1
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
                (rev["answer"]["emotion"] if rev else ""),
                (rev["answer"]["valence"] if rev else ""),
                (rev["answer"]["arousal"] if rev else ""),
                (int(rev["agreed"]) if rev else ""),
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
        + (f"Class subset: clips labeled {sorted(drop)} are LEFT OUT.\n\n" if drop else "")
        + f"Labels are single human annotator (state.db, tools/labeler). Columns: "
        f"emotion (7-class), valence/arousal (1-5), gold_text (human-corrected), plus "
        f"opus_suggest/sonnet_suggest = LLM *suggestions* (NOT labels, ADR-003).\n\n"
        f"`emotion_reviewed`/`valence_reviewed`/`arousal_reviewed` = a SECOND rater's pass "
        f"({sum(1 for x in rows if x[10])} rows); `agreed`=1 means that rater kept the owner's "
        f"values unchanged, so those rows carry identical labels in both columns (change 012).\n\n"
        f"**No speaker/gender/age**: speakers not yet reassigned from diarization ids "
        f"to cast characters — omitted rather than ship wrong values.\n\n"
        f"Derived from copyrighted VN TV drama — research use, **never make public**.\n",
        encoding="utf-8",
    )
    (stage / "dataset-metadata.json").write_text(
        json.dumps(
            {
                "title": f"ViEmoSpeech {args.slug} (private)",
                "id": f"{args.owner}/{args.slug}",
                "licenses": [{"name": "other"}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"staged: {stage}")
    print(
        f"utterances={len(rows)}  clips={len(list(clips_out.glob('*.wav')))}  "
        f"skipped_no_wav={skipped_no_wav}  skipped_off_queue={skipped_off_queue}  "
        f"skipped_rev_rejected={skipped_rev_rejected}  reviewed={sum(1 for x in rows if x[10])}"
    )

    if args.push:
        st = subprocess.run(
            [
                "uvx",
                "--from",
                "kaggle",
                "kaggle",
                "datasets",
                "status",
                f"{args.owner}/{args.slug}",
            ],
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
        cmd = [
            "uvx",
            "--from",
            "kaggle",
            "kaggle",
            "datasets",
            action,
            "-p",
            args.slug,
            "--dir-mode",
            "zip",
        ]
        if exists:
            cmd += ["-m", f"human labels: {len(rows)} utt"]
        subprocess.run(cmd, check=True, cwd=stage.parent)
        print("pushed (private).")


if __name__ == "__main__":
    main()
