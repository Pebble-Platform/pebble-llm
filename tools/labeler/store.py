"""Foundation for the labeler backend: config, the SQLite record store, records, paths.

ROOT / STATE are module globals set once via set_root(); the other modules read
them as ``store.ROOT`` / ``store.STATE`` (never ``from store import ROOT``, which
would bind the pre-set None).

Persistence = SQLite ``state.db`` (WAL, one row per record, whole record as a JSON
blob keyed on ``(epkey, id)``). ``STATE`` stays an in-RAM mirror rebuilt from the DB
at load() so every read path (episodes.py, server.py) is unchanged; only writes go
to the DB — ``put()`` upserts one row, ``save()`` reconciles the whole mirror in one
transaction. ADR-004: SQLite gives ACID + integrity_check + hot backup (VACUUM INTO).
"""

from __future__ import annotations

import csv
import json
import re
import sqlite3
import threading
from datetime import UTC, datetime
from pathlib import Path

from fastapi import HTTPException

CLIP_RE = re.compile(r"^seg\d+$")

ROOT: Path | None = None
DB_PATH: Path | None = None
STATE: dict[str, dict] = {}  # "epKey\tid" -> label record (in-RAM mirror of state.db)
LOCK = threading.Lock()
_CONN: sqlite3.Connection | None = None  # single writer conn, guarded by LOCK


def set_root(root: Path) -> None:
    global ROOT, DB_PATH
    ROOT = root
    DB_PATH = root / "state.db"


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def skey(ep_key: str, clip_id: str) -> str:
    return f"{ep_key}\t{clip_id}"


def fnum(*vals) -> float:
    for v in vals:
        if v:
            try:
                return float(v)
            except ValueError:
                pass
    return 0.0


# ---------- persistence (SQLite state.db, WAL) ----------
def connect(db_path: Path) -> sqlite3.Connection:
    """Open state.db with the labeler's durability pragmas + ensure the schema.

    WAL + synchronous=NORMAL: crash-safe for a single writer (can only lose the
    last transaction on power loss, never corrupt the DB — ADR-004). Shared by
    the server (via load) and the migration script.
    """
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS records ("
        "epkey TEXT NOT NULL, id TEXT NOT NULL, data TEXT NOT NULL, ts TEXT, "
        "PRIMARY KEY (epkey, id))"
    )
    # Online second-pass queue + ratings (change 011). One row = one PRESENTATION of a
    # clip to one annotator: the assignment (annotator, seq -> clip) and that
    # annotator's answer live together, answer columns NULL/'' until rated.
    #
    # Keyed (annotator, seq), NOT (epkey, id, annotator): the pre-registered QC protocol
    # seeds ~10% duplicate clips to measure self-consistency, so the SAME clip is shown
    # to the SAME annotator twice and must yield two independent rows.
    #
    # `records` is untouched — the owner's label of record stays there, so an invited
    # annotator cannot overwrite it by construction.
    conn.execute(
        "CREATE TABLE IF NOT EXISTS assignments ("
        "annotator TEXT NOT NULL, seq INTEGER NOT NULL, "
        "epkey TEXT NOT NULL, id TEXT NOT NULL, "
        "kind TEXT NOT NULL DEFAULT 'normal', "  # normal | gold | dup | trap
        "emotion TEXT NOT NULL DEFAULT '', valence INTEGER, arousal INTEGER, "
        "skip_reason TEXT NOT NULL DEFAULT '', listen_ms INTEGER NOT NULL DEFAULT 0, "
        "ts TEXT, "  # NULL = not answered yet
        "PRIMARY KEY (annotator, seq))"
    )
    conn.commit()
    return conn


def load() -> None:
    """Open the DB and rebuild the in-RAM STATE mirror from it."""
    global _CONN
    STATE.clear()
    _CONN = connect(DB_PATH)
    for epkey, cid, data in _CONN.execute("SELECT epkey, id, data FROM records"):
        STATE[skey(epkey, cid)] = json.loads(data)


def _upsert(rec: dict) -> None:
    """Write one record (caller holds LOCK). Single-row transaction."""
    with _CONN:
        _CONN.execute(
            "INSERT OR REPLACE INTO records (epkey, id, data, ts) VALUES (?, ?, ?, ?)",
            (rec["epKey"], rec["id"], json.dumps(rec, ensure_ascii=False), rec.get("ts", "")),
        )


def save() -> None:
    """Reconcile the whole in-RAM STATE into the DB in ONE transaction (caller holds LOCK).

    Used by the multi-record routes (segment/reject-bulk/split/undo-split): upsert
    every current record and drop DB rows no longer in STATE (e.g. undo-split
    deletes children). Atomic — a mid-write failure rolls back, never a partial DB.
    """
    with _CONN:
        _CONN.executemany(
            "INSERT OR REPLACE INTO records (epkey, id, data, ts) VALUES (?, ?, ?, ?)",
            [
                (r["epKey"], r["id"], json.dumps(r, ensure_ascii=False), r.get("ts", ""))
                for r in STATE.values()
            ],
        )
        live = {(r["epKey"], r["id"]) for r in STATE.values()}
        stale = [
            row for row in _CONN.execute("SELECT epkey, id FROM records") if tuple(row) not in live
        ]
        if stale:
            _CONN.executemany("DELETE FROM records WHERE epkey = ? AND id = ?", stale)


def manual_record(
    ep_key: str, cid: str, series: str, episode: str, start: float, end: float, text: str
) -> dict:
    """A fresh record for a clip the human cut from full audio (no segments.csv row).

    ``manual_segment`` marks provenance (human-picked span, not auto VAD∩turn).
    Carries its own asr/yt/opus_detail like a split child so episodes.build()
    renders it without a CSV lookup. Text seeds ``gold_text`` from the YT script.
    """
    return {
        "epKey": ep_key,
        "id": cid,
        "series": series,
        "episode": episode,
        "gender": "",  # per-clip human demographic (set on label)
        "age_group": "",
        "dialect": "",
        "start": start,
        "end": end,
        "asr": "",
        "yt": text,
        "opus": "",
        "sonnet": "",
        "opus_detail": None,
        "sonnet_detail": None,
        "emotion": "",
        "valence": None,
        "arousal": None,
        "distress": False,
        "note": "",
        "recut": False,
        "excised": [],
        "gold_text": text,
        "rejected": False,
        "reject_reason": "",
        "manual_segment": True,
        "annotator": "",
        "ts": now(),
    }


def put(ep_key: str, clip_id: str, rec: dict) -> dict:
    """Store one record and persist — the single-write path used by most routes."""
    with LOCK:
        STATE[skey(ep_key, clip_id)] = rec
        _upsert(rec)
    return rec


# ---------- online second-pass queue + ratings (change 011) ----------
def assign(annotator: str, items: list[tuple[str, str, str]]) -> int:
    """Install an annotator's fixed, pre-shuffled queue: [(epkey, clip_id, kind), ...].

    Idempotent per annotator: refuses to overwrite a queue that already has answers,
    so a re-run can never wipe work already done.
    """
    with LOCK, _CONN:
        answered = _CONN.execute(
            "SELECT COUNT(*) FROM assignments WHERE annotator = ? AND ts IS NOT NULL", (annotator,)
        ).fetchone()[0]
        if answered:
            raise ValueError(
                f"{annotator} already answered {answered} items — refusing to reassign"
            )
        _CONN.execute("DELETE FROM assignments WHERE annotator = ?", (annotator,))
        _CONN.executemany(
            "INSERT INTO assignments (annotator, seq, epkey, id, kind) VALUES (?, ?, ?, ?, ?)",
            [(annotator, i, ep, cid, kind) for i, (ep, cid, kind) in enumerate(items)],
        )
    return len(items)


def next_seq(annotator: str) -> dict | None:
    """The annotator's first unanswered queue item, or None when the queue is done."""
    row = _CONN.execute(
        "SELECT seq, epkey, id FROM assignments "
        "WHERE annotator = ? AND ts IS NULL ORDER BY seq LIMIT 1",
        (annotator,),
    ).fetchone()
    return None if row is None else {"seq": row[0], "epkey": row[1], "id": row[2]}


def assignment_clip(annotator: str, seq: int) -> tuple[str, str]:
    """Resolve (epkey, clip_id) for one of THIS annotator's queue slots.

    The only way an annotator reaches audio: they address clips by queue position, so
    they never learn an episode/clip id and cannot enumerate or reassemble a scene
    (ADR-005 safeguards #2/#4).
    """
    row = _CONN.execute(
        "SELECT epkey, id FROM assignments WHERE annotator = ? AND seq = ?", (annotator, seq)
    ).fetchone()
    if row is None:
        raise HTTPException(404, "not in your queue")
    return row[0], row[1]


def save_rating(
    annotator: str,
    seq: int,
    emotion: str = "",
    valence: int | None = None,
    arousal: int | None = None,
    skip_reason: str = "",
    listen_ms: int = 0,
) -> None:
    """Record one answer. Touches only this annotator's own queue slot."""
    with LOCK, _CONN:
        cur = _CONN.execute(
            "UPDATE assignments SET emotion = ?, valence = ?, arousal = ?, "
            "skip_reason = ?, listen_ms = ?, ts = ? WHERE annotator = ? AND seq = ?",
            (emotion, valence, arousal, skip_reason, listen_ms, now(), annotator, seq),
        )
        if not cur.rowcount:
            raise HTTPException(404, "not in your queue")


def progress(annotator: str) -> dict:
    row = _CONN.execute(
        "SELECT COUNT(*), COUNT(ts) FROM assignments WHERE annotator = ?", (annotator,)
    ).fetchone()
    return {"total": row[0], "done": row[1]}


def all_ratings() -> list[dict]:
    """Every answered row across annotators — the input to the κ/α report (M7)."""
    cols = (
        "annotator",
        "seq",
        "epkey",
        "id",
        "kind",
        "emotion",
        "valence",
        "arousal",
        "skip_reason",
        "listen_ms",
        "ts",
    )
    rows = _CONN.execute(
        f"SELECT {', '.join(cols)} FROM assignments WHERE ts IS NOT NULL ORDER BY annotator, seq"
    )
    return [dict(zip(cols, r, strict=True)) for r in rows]


# ---------- csv ----------
def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def by_id(rows: list[dict]) -> dict[str, dict]:
    return {r["id"]: r for r in rows if r.get("id")}


# ---------- paths (ROOT-relative, traversal-safe) ----------
def safe(ep_key: str) -> Path:
    p = (ROOT / ep_key).resolve()
    if p != ROOT and ROOT not in p.parents:
        raise HTTPException(400, "path escapes root")
    return p


def episode_dir(ep_key: str, clip_id: str | None = None) -> Path:
    """Validate an optional clip id + resolve the episode dir (404 if missing)."""
    if clip_id is not None and not CLIP_RE.match(clip_id):
        raise HTTPException(400, "bad clip id")
    ep = safe(ep_key)
    if not ep.is_dir():
        raise HTTPException(404, "no such episode")
    return ep


def clip_wav(ep: Path, clip_id: str) -> Path:
    wav = (ep / "clips" / f"{clip_id}.wav").resolve()
    if (ROOT not in wav.parents) or not wav.is_file():
        raise HTTPException(404, "no such clip")
    return wav


# ---------- records ----------
def seed_record(ep_key: str, clip_id: str, ep: Path) -> dict:
    """Existing state record (a mutable copy) or a fresh seed with CSV provenance.

    Both /gold (label fields) and /recut (audio fields) merge into the same
    record, so neither clobbers the other's fields.
    """
    key = skey(ep_key, clip_id)
    if key in STATE:
        return dict(STATE[key])
    seg = by_id(read_csv(ep / "segments.csv")).get(clip_id, {})
    op = by_id(read_csv(ep / "labels_opus.csv")).get(clip_id, {})
    so = by_id(read_csv(ep / "labels_sonnet.csv")).get(clip_id, {})
    return {
        "epKey": ep_key,
        "id": clip_id,
        "series": ep.parent.relative_to(ROOT).as_posix() or "(root)",
        "episode": ep.name,
        "gender": "",  # per-clip human demographic (set on label)
        "age_group": "",
        "dialect": "",
        "start": fnum(seg.get("start")),
        "end": fnum(seg.get("end")),
        "opus": op.get("emotion", ""),  # teacher suggestion, not a label of record
        "sonnet": so.get("emotion", ""),
        "emotion": "",
        "valence": None,
        "arousal": None,
        "distress": False,
        "note": "",
        "recut": False,
        "excised": [],
        "gold_text": "",
        "rejected": False,
        "reject_reason": "",
        "annotator": "",
        "ts": "",
    }


def _teacher_label(row: dict) -> dict | None:
    """Full opus/sonnet suggestion shape (mirrors episodes.py's ``_label``).

    Needed so a split child can carry the parent's teacher suggestion in the
    same dict shape ``/episode`` returns for a normal clip — a child id has no
    row of its own in labels_opus.csv/labels_sonnet.csv to build that from.
    """
    if not row:
        return None
    return {
        "emotion": row.get("emotion", ""),
        "valence": row.get("valence", ""),
        "arousal": row.get("arousal", ""),
        "distress": row.get("distress", ""),
        "multi_speaker_suspect": row.get("multi_speaker_suspect", ""),
    }


def inherited_provenance(ep: Path, parent: dict) -> dict:
    """asr/yt text + opus/sonnet suggestions to copy into a split's children (F5).

    Looked up by the PARENT's own id in the episode CSVs (children get no CSV
    row of their own). If the parent is itself a split child (no CSV row
    either), reuse what it already inherited at its own creation.
    """
    if parent.get("split_from"):
        return {
            "asr": parent.get("asr", ""),
            "yt": parent.get("yt", ""),
            "opus": parent.get("opus", ""),
            "sonnet": parent.get("sonnet", ""),
            "opus_detail": parent.get("opus_detail"),
            "sonnet_detail": parent.get("sonnet_detail"),
        }
    pid = parent["id"]
    tr_yt = by_id(read_csv(ep / "transcripts_yt.csv")).get(pid, {})
    tr = by_id(read_csv(ep / "transcripts.csv")).get(pid, {})
    op = by_id(read_csv(ep / "labels_opus.csv")).get(pid, {})
    so = by_id(read_csv(ep / "labels_sonnet.csv")).get(pid, {})
    return {
        "asr": tr_yt.get("text_phowhisper") or tr.get("text") or "",
        "yt": tr_yt.get("text_youtube", ""),
        "opus": op.get("emotion", ""),
        "sonnet": so.get("emotion", ""),
        "opus_detail": _teacher_label(op),
        "sonnet_detail": _teacher_label(so),
    }


def child_record(ep_key: str, cid: str, parent: dict, prov: dict, start: float, end: float) -> dict:
    """A fresh, unlabeled record for a split child (id not in segments.csv).

    Record-shape choice (F5, 2026-07-09): ``opus``/``sonnet`` stay plain
    emotion strings, same as ``seed_record`` — that's what actions.js's
    gold.csv export compares/writes as strings. ``opus_detail``/``sonnet_detail``
    carry the full {emotion,valence,arousal,distress,multi_speaker_suspect}
    dict that episodes.build() needs to render the child exactly like a normal
    clip's /episode response (see episodes.py's split-child branch).
    """
    return {
        "epKey": ep_key,
        "id": cid,
        "series": parent["series"],
        "episode": parent["episode"],
        "gender": parent.get("gender", ""),  # inherit parent's demographic; human edits per child
        "age_group": parent.get("age_group", ""),
        "dialect": parent.get("dialect", ""),
        "start": start,
        "end": end,
        "asr": prov["asr"],
        "yt": prov["yt"],
        "opus": prov["opus"],
        "sonnet": prov["sonnet"],
        "opus_detail": prov["opus_detail"],
        "sonnet_detail": prov["sonnet_detail"],
        "emotion": "",
        "valence": None,
        "arousal": None,
        "distress": False,
        "note": "",
        "recut": False,
        "gold_text": "",
        "rejected": False,
        "reject_reason": "",
        "split_from": parent["id"],
        "annotator": "",
        "ts": now(),
    }
