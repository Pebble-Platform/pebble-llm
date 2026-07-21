"""One-off: backfill per-clip gender/age_group into labeler state.jsonl from cast.json.

Context (2026-07-20): the labeler drops the speaker/cast indirection — demographics
become per-clip fields set at label time. This migrates existing labels so every
clip already reassigned to a real character carries gender/age_group DIRECTLY
(resolved by (series, speaker) from cast.json) — no relabeling needed.

Idempotent + non-destructive: only fills EMPTY gender/age_group (never overwrites),
keeps the speaker field as-is (provenance), backs up state.jsonl before writing.

⚠ Run with the labeler server STOPPED — a running server holds state.jsonl in
memory and would clobber this on its next save (intent: single-writer).

Usage (from repo root):
  PYTHONIOENCODING=utf-8 python scripts/vietnamese-ser/migrate_labeler_demographics.py
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EPISODES = ROOT / "data" / "vietnamese-ser" / "episodes"
STATE = EPISODES / "state.jsonl"
CAST = EPISODES / "cast.json"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console
    if not STATE.exists():
        sys.exit(f"state.jsonl not found: {STATE}")
    cast = json.loads(CAST.read_text(encoding="utf-8")) if CAST.exists() else {}
    demo = {(s, e["name"]): e for s, entries in cast.items() for e in entries}
    recs = [json.loads(ln) for ln in STATE.read_text(encoding="utf-8").splitlines() if ln.strip()]

    filled = already_had = no_match = 0
    for r in recs:
        spk = (r.get("speaker") or "").strip()
        if r.get("gender") or r.get("age_group"):
            already_had += 1
            continue
        e = demo.get((r.get("series", ""), spk))
        if e and (e.get("gender") or e.get("age_group")):
            r["gender"] = e.get("gender", "")
            r["age_group"] = e.get("age_group", "")
            filled += 1
        elif spk and not spk.startswith("SPEAKER_"):
            no_match += 1  # reassigned to a real name that isn't in cast.json

    bak = STATE.with_name(f"state.jsonl.bak-{datetime.now():%Y%m%d-%H%M%S}")
    shutil.copy2(STATE, bak)
    tmp = STATE.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(STATE)

    print(
        f"records={len(recs)}  filled={filled}  already_had_demo={already_had}  "
        f"real-name-not-in-cast={no_match}"
    )
    print(f"backup: {bak.name}")


if __name__ == "__main__":
    main()
