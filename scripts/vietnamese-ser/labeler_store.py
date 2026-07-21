"""Read the labeler's label store for downstream scripts (one place that knows the format).

The labeler persists to SQLite ``state.db`` (WAL, one JSON-blob row per record —
ADR-004). Build/stats scripts read the records through here so none of them hardcode
the table shape. Falls back to the legacy ``state.jsonl`` if ``state.db`` is absent
(transition safety). Stdlib only — importing this must NOT pull the server's FastAPI
deps, so it does not import tools/labeler's store.py.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def read_records(episodes_dir: Path) -> list[dict]:
    """Every label record as a dict, from state.db (else legacy state.jsonl)."""
    db = episodes_dir / "state.db"
    if db.exists():
        conn = sqlite3.connect(db)
        try:
            return [json.loads(data) for (data,) in conn.execute("SELECT data FROM records")]
        finally:
            conn.close()
    jsonl = episodes_dir / "state.jsonl"
    if jsonl.exists():
        return [
            json.loads(ln) for ln in jsonl.read_text(encoding="utf-8").splitlines() if ln.strip()
        ]
    return []
