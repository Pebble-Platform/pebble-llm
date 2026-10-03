"""One-off: backfill dialect="north" (Bắc) into existing labeler records in state.db.

Context (2026-07-22): the per-clip `dialect` field (Bắc/Trung/Nam — different tone
systems, intent §6) was just added to the labeler. Both pilot series in the corpus
(Về nhà đi con · Chạy trốn thanh xuân — VFC / Northern productions) are Northern-
accent, so every EXISTING record is backfilled to "north". New labels default to
"" until a human picks a region. This bulk assumption IS the provenance trail —
it is a source-level fact (production house), not a per-clip listening judgement.

Idempotent + non-destructive: only fills EMPTY/missing dialect (never overwrites a
value a human set to central/south), leaves every other field incl. `ts` as-is,
takes a consistent `VACUUM INTO` snapshot of state.db before writing.

⚠ Run with the labeler server STOPPED — a running server holds STATE in memory and
would clobber this on its next save (single-writer, intent). See tools/labeler/RUN.md.

Usage (from repo root):
  PYTHONIOENCODING=utf-8 .venv-vnser/Scripts/python.exe \
      scripts/vietnamese-ser/migrate_dialect_north.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "vietnamese-ser" / "episodes" / "state.db"
DIALECT = "north"  # Bắc — both pilot series are Northern-accent (VFC productions)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="report only, do not write")
    args = ap.parse_args()

    if not DB.exists():
        sys.exit(f"state.db not found: {DB}")

    conn = sqlite3.connect(DB, isolation_level=None)  # autocommit; VACUUM needs no open txn
    rows = conn.execute("SELECT epkey, id, data FROM records").fetchall()

    to_fill = []
    already = 0
    for epkey, cid, data in rows:
        rec = json.loads(data)
        if rec.get("dialect"):  # human already set a region — never overwrite
            already += 1
            continue
        rec["dialect"] = DIALECT
        to_fill.append((epkey, cid, json.dumps(rec, ensure_ascii=False), rec.get("ts", "")))

    print(f"records={len(rows)}  to_fill={len(to_fill)}  already_had_dialect={already}")

    if args.dry_run:
        print("dry-run: no write")
        return
    if not to_fill:
        print("nothing to fill")
        return

    bak = DB.with_name(f"state.db.bak-{datetime.now():%Y%m%d-%H%M%S}")
    conn.execute("VACUUM INTO ?", (str(bak),))  # consistent snapshot (ADR-004 hot backup)
    conn.execute("BEGIN")
    conn.executemany(
        "INSERT OR REPLACE INTO records (epkey, id, data, ts) VALUES (?, ?, ?, ?)", to_fill
    )
    conn.execute("COMMIT")
    print(f"filled={len(to_fill)}  backup={bak.name}")


if __name__ == "__main__":
    main()
