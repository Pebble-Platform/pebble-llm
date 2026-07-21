"""Report labeling progress per series: videos, human labels, labeled duration.

Reads the labeler's source of truth directly (state.db, ADR-003/ADR-004) plus a
scan of the episode dirs — no running server needed.

  videos   = epNN[_K] dirs that have cut clips (same rule as the labeler listing)
  labels   = records with an emotion and not rejected
  duration = sum(end - start) over those same records

Also breaks the labeled records down by emotion, gender, and age_group (audios +
duration each); "(chưa gán)" = labeled but that demographic not set yet.

Usage:
  PYTHONIOENCODING=utf-8 python scripts/vietnamese-ser/labeler_stats.py \
      [--root data/vietnamese-ser/episodes]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from labeler_store import read_records

ROOT = Path(__file__).resolve().parents[2]
EP_RE = re.compile(r"^ep\d+(_\d+)?$", re.IGNORECASE)


def hms(sec: float) -> str:
    s = round(sec)
    return f"{s // 3600}:{s // 60 % 60:02d}:{s % 60:02d}"


def breakdown(title: str, d: dict[str, list]) -> None:
    """Print an '<title> | audios | duration' table, most-frequent first."""
    w = max([len(k) for k in d] + [len(title)])
    print(f"\n{title:<{w}}  {'audios':>6}  {'duration':>9}")
    for k, (n, dur) in sorted(d.items(), key=lambda kv: -kv[1][0]):
        print(f"{k:<{w}}  {n:>6}  {hms(dur):>9}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default="data/vietnamese-ser/episodes")
    args = ap.parse_args()

    root = (ROOT / args.root).resolve() if not Path(args.root).is_absolute() else Path(args.root)
    if not root.is_dir():
        raise SystemExit(f"--root is not a directory: {root}")

    # series -> [videos, labels, duration]
    stats: dict[str, list] = {}
    # emotion / gender / age_group -> [audios, duration]
    per_label: dict[str, list] = {}
    per_gender: dict[str, list] = {}
    per_age: dict[str, list] = {}

    for ep in sorted(p for p in root.rglob("*") if p.is_dir() and EP_RE.match(p.name)):
        if not any((ep / "clips").glob("seg*.wav")):
            continue
        series = ep.parent.relative_to(root).as_posix() or "(root)"
        stats.setdefault(series, [0, 0, 0.0])[0] += 1

    for r in read_records(root):
        if not r.get("emotion") or r.get("rejected"):
            continue
        series = Path(r["epKey"]).parent.as_posix()
        series = "(root)" if series == "." else series
        dur = r["end"] - r["start"]
        row = stats.setdefault(series, [0, 0, 0.0])
        row[1] += 1
        row[2] += dur
        for d, key in (
            (per_label, r["emotion"]),
            (per_gender, r.get("gender") or "(chưa gán)"),
            (per_age, r.get("age_group") or "(chưa gán)"),
        ):
            cell = d.setdefault(key, [0, 0.0])
            cell[0] += 1
            cell[1] += dur

    w = max([len(s) for s in stats] + [len("TOTAL")])
    print(f"{'series':<{w}}  {'videos':>6}  {'labels':>6}  {'duration':>9}")
    for series, (v, n, d) in sorted(stats.items()):
        print(f"{series:<{w}}  {v:>6}  {n:>6}  {hms(d):>9}")
    tv, tn, td = (sum(c) for c in zip(*stats.values())) if stats else (0, 0, 0.0)
    print("-" * (w + 27))
    print(f"{'TOTAL':<{w}}  {tv:>6}  {tn:>6}  {hms(td):>9}")

    breakdown("emotion", per_label)
    breakdown("gender", per_gender)
    breakdown("age", per_age)


if __name__ == "__main__":
    main()
