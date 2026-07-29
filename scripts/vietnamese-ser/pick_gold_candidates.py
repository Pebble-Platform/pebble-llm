"""Shortlist gold-anchor candidates for the owner to confirm by ear (change 011, M1 step 4).

qc-protocol §2.1 builds the gold set in three steps; this script does step 1 and the
sampling, and **cannot** do step 2 — the owner must still listen to each candidate and
keep only the ones that are obvious. Gold is not "the right answer": the owner's labels
are not independent ground truth. Gold means "easy enough that anyone listening
seriously lands on it", so it catches an annotator who is NOT LISTENING, never one who
hears differently.

Step 1 filter: owner, Opus and Sonnet all independently gave the same emotion. Then a
stratified draw across the 7 classes x 2 series.

    .venv-vnser/Scripts/python.exe scripts/vietnamese-ser/pick_gold_candidates.py

Writes a TSV of candidates with the on-disk wav path. Listen, delete the lines that are
not obvious, then keep the first column as
`docs/spec/changes/011-online-multi-annotator/gold-set.txt`.
"""

from __future__ import annotations

import argparse
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "labeler"))
import store

EMOTIONS = ["joy", "sadness", "anger", "fear_anxiety", "surprise", "disgust", "neutral"]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="shortlist gold candidates to confirm by ear")
    ap.add_argument("--root", default="data/vietnamese-ser/episodes")
    ap.add_argument("--per-class", type=int, default=5, help="candidates per emotion class")
    ap.add_argument(
        "--out", default="docs/spec/changes/011-online-multi-annotator/gold-candidates.tsv"
    )
    ap.add_argument("--seed", type=int, default=1128)
    a = ap.parse_args()

    root = Path(a.root).resolve()
    store.set_root(root)
    store.load()
    rng = random.Random(a.seed)

    # step 1: three independent judgements agree -> the clip is uncontroversial
    tri = [
        r
        for r in store.STATE.values()
        if r.get("emotion")
        and not r.get("rejected")
        and r.get("opus")
        and r.get("sonnet")
        and r["opus"] == r["sonnet"] == r["emotion"]
    ]

    cells: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in tri:
        cells[(r["emotion"], r.get("series", ""))].append(r)
    for v in cells.values():
        rng.shuffle(v)

    picked: list[dict] = []
    for emo in EMOTIONS:
        series = [k for k in cells if k[0] == emo]
        # alternate series so a class is never sourced from one film alone
        while sum(1 for p in picked if p["emotion"] == emo) < a.per_class and any(
            cells[k] for k in series
        ):
            for k in series:
                if cells[k] and sum(1 for p in picked if p["emotion"] == emo) < a.per_class:
                    picked.append(cells[k].pop())

    lines = ["# epKey/clip_id\temotion\twav, relative to --root (listen, delete non-obvious rows)"]
    for r in sorted(picked, key=lambda x: (x["emotion"], x["epKey"], x["id"])):
        # relative, not absolute: this file may end up committed, and an absolute path
        # would carry the local username into the repo for no benefit
        wav = f"{r['epKey']}/clips/{r['id']}.wav"
        lines.append(f"{r['epKey']}/{r['id']}\t{r['emotion']}\t{wav}")

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    got: dict[str, int] = defaultdict(int)
    for r in picked:
        got[r["emotion"]] += 1
    print(f"three-way agreement pool: {len(tri)}")
    print(f"candidates: {len(picked)}  " + "  ".join(f"{e}={got[e]}" for e in EMOTIONS))
    thin = [e for e in EMOTIONS if got[e] < a.per_class]
    if thin:
        print(f"  thin classes (took everything available): {', '.join(thin)}")
    print(f"-> {out}\n   Listen, delete non-obvious rows, keep column 1 as gold-set.txt")


if __name__ == "__main__":
    main()
