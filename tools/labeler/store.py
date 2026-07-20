"""Foundation for the labeler backend: config, the state.jsonl store, records, paths.

ROOT / STATE are module globals set once via set_root(); the other modules read
them as ``store.ROOT`` / ``store.STATE`` (never ``from store import ROOT``, which
would bind the pre-set None).
"""

from __future__ import annotations

import csv
import json
import re
import threading
from datetime import UTC, datetime
from pathlib import Path

from fastapi import HTTPException

CLIP_RE = re.compile(r"^seg\d+$")

ROOT: Path | None = None
STATE_PATH: Path | None = None
CAST_PATH: Path | None = None
STATE: dict[str, dict] = {}  # "epKey\tid" -> label record (source of truth for labels)
CAST: dict[str, list[dict]] = {}  # series -> [{name, gender, age_group}] (per-film cast)
LOCK = threading.Lock()


def set_root(root: Path) -> None:
    global ROOT, STATE_PATH, CAST_PATH
    ROOT = root
    STATE_PATH = root / "state.jsonl"
    CAST_PATH = root / "cast.json"


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


# ---------- persistence ----------
def load() -> None:
    STATE.clear()
    if STATE_PATH and STATE_PATH.exists():
        for line in STATE_PATH.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                STATE[skey(r["epKey"], r["id"])] = r
    load_cast()


def save() -> None:
    """Atomic full rewrite (jsonl small at this scale): tmp -> rename."""
    tmp = STATE_PATH.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for r in STATE.values():
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(STATE_PATH)


# ---------- per-film cast (character roster: name + gender + age_group) ----------
def load_cast() -> None:
    CAST.clear()
    if CAST_PATH and CAST_PATH.exists():
        CAST.update(json.loads(CAST_PATH.read_text(encoding="utf-8")))


def save_cast() -> None:
    tmp = CAST_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(CAST, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(CAST_PATH)


def set_cast(series: str, entries: list[dict]) -> list[dict]:
    """Replace one film's whole cast (config screen saves the full list)."""
    clean = [
        {
            "name": (e.get("name") or "").strip(),
            "gender": e.get("gender", ""),
            "age_group": e.get("age_group", ""),
        }
        for e in entries
        if (e.get("name") or "").strip()
    ]
    with LOCK:
        CAST[series] = clean
        save_cast()
    return clean


def cast_for(series: str) -> list[dict]:
    return CAST.get(series, [])


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
        "speaker": "",  # human assigns the character
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
        save()
    return rec


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
        "speaker": seg.get("speaker", ""),
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
        "speaker": parent["speaker"],  # default = parent; human edits via F6
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
