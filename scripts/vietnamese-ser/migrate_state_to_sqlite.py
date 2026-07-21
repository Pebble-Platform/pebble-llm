"""One-off bootstrap: import the labeler's state.jsonl into the new SQLite store.db.

Context (ADR-004, 2026-07-21): the labeler moves its persistence from a single
full-rewrite state.jsonl to SQLite (`state.db`, WAL) — ACID per-row writes, no
whole-file clobber, `PRAGMA integrity_check`, hot backup via `VACUUM INTO`. This
reads each line of state.jsonl and upserts it as one row (whole record as a JSON
blob keyed on (epkey, id)), reusing the server's own schema via ``store.connect``.

Idempotent (INSERT OR REPLACE) + non-destructive: backs up an existing state.db
before writing; leaves state.jsonl untouched as the import source.

⚠ Run with the labeler server STOPPED — a running server (new code) holds the DB
and its in-RAM STATE; migrating underneath it would race its reconcile-save.

Usage (from repo root):
  PYTHONIOENCODING=utf-8 python scripts/vietnamese-ser/migrate_state_to_sqlite.py
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EPISODES = REPO / "data" / "vietnamese-ser" / "episodes"
STATE_JSONL = EPISODES / "state.jsonl"
DB_PATH = EPISODES / "state.db"

sys.path.insert(0, str(REPO / "tools" / "labeler"))  # reuse the server's schema/pragmas
import store  # noqa: E402


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console
    if not STATE_JSONL.exists():
        sys.exit(f"state.jsonl not found: {STATE_JSONL}")
    recs = [
        json.loads(ln) for ln in STATE_JSONL.read_text(encoding="utf-8").splitlines() if ln.strip()
    ]

    if DB_PATH.exists():
        bak = DB_PATH.with_name(f"state.db.bak-{datetime.now():%Y%m%d-%H%M%S}")
        shutil.copy2(DB_PATH, bak)
        print(f"backup existing db: {bak.name}")

    conn = store.connect(DB_PATH)
    with conn:
        conn.executemany(
            "INSERT OR REPLACE INTO records (epkey, id, data, ts) VALUES (?, ?, ?, ?)",
            [
                (r["epKey"], r["id"], json.dumps(r, ensure_ascii=False), r.get("ts", ""))
                for r in recs
            ],
        )
    n_db = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    conn.close()

    print(f"imported: jsonl={len(recs)}  db_rows={n_db}  ->  {DB_PATH.relative_to(REPO)}")
    if n_db != len(recs):
        sys.exit(f"⚠ count mismatch (jsonl={len(recs)} db={n_db}) — check for duplicate (epKey,id)")


if __name__ == "__main__":
    main()
