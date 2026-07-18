"""FastAPI backend for tools/labeler — change 003 (thin routes; logic in modules).

Run (from repo root):
  .venv-vnser/Scripts/python.exe tools/labeler/server.py \
      --root data/vietnamese-ser/episodes
  # then open http://127.0.0.1:8000/index.html

Layers: store.py (config/state.jsonl/records/paths) · episodes.py (read/join) ·
audio.py (soundfile recut/split). Binds 127.0.0.1 only; data/** is copyrighted
media, local-only (intent §1). Human labels are the source of truth (ADR-003).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import audio
import episodes
import store
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

HERE = Path(__file__).resolve().parent
app = FastAPI(title="ViEmoSpeech labeler")


# ---------- request models ----------
class GoldIn(BaseModel):
    emotion: str
    valence: int
    arousal: int
    distress: bool = False
    note: str = ""
    gold_text: str | None = None  # human text of record; None = keep existing
    speaker: str | None = None  # F6: human speaker; None = keep seeded/existing
    annotator: str = "human"


class RecutIn(BaseModel):
    a: float  # keep-region start, clip-local seconds
    b: float  # keep-region end
    text: str = ""  # human-corrected text (audio changed)


class ExciseIn(BaseModel):
    a: float  # remove-region start, clip-local seconds
    b: float  # remove-region end
    text: str = ""  # human-corrected text (audio changed)


class RejectIn(BaseModel):
    reason: str = "other"  # multi_speaker | noise | bad_cut | split | other


class SplitIn(BaseModel):
    ts: list[float]  # split points, clip-local seconds, strictly increasing, k >= 1


# ---------- reads ----------
@app.get("/episodes")
def get_episodes() -> list[dict]:
    return episodes.listing()


@app.get("/episode/{ep_key:path}")
def get_episode(ep_key: str) -> dict:
    return episodes.build(ep_key, store.episode_dir(ep_key))


@app.get("/clip/{ep_key:path}/{clip_id}.wav")
def get_clip(ep_key: str, clip_id: str) -> FileResponse:
    ep = store.episode_dir(ep_key, clip_id)
    # no-store: file bị ghi đè khi recut/split → browser phải lấy bản mới, không cache
    return FileResponse(
        store.clip_wav(ep, clip_id), media_type="audio/wav", headers={"Cache-Control": "no-store"}
    )


@app.get("/context/{ep_key:path}/{clip_id}.wav")
def get_context(ep_key: str, clip_id: str, pad: float = 10.0) -> Response:
    """Serve [start-pad, end+pad] of the full episode audio (context preview, read-only)."""
    ep = store.episode_dir(ep_key, clip_id)
    rec = store.STATE.get(store.skey(ep_key, clip_id))
    if rec:
        start, end = rec["start"], rec["end"]
    else:
        seg = store.by_id(store.read_csv(ep / "segments.csv")).get(clip_id, {})
        start, end = store.fnum(seg.get("start")), store.fnum(seg.get("end"))
    return Response(
        audio.read_context(ep, start, end, pad),
        media_type="audio/wav",
        headers={"Cache-Control": "no-store"},
    )


@app.get("/gold")
def all_gold() -> list[dict]:
    """Every human label record (source of truth = state.jsonl)."""
    return list(store.STATE.values())


# ---------- label / recut / reject / split ----------
@app.post("/gold/{ep_key:path}/{clip_id}")
def put_gold(ep_key: str, clip_id: str, g: GoldIn) -> dict:
    """Save the human label of record (merges into any existing recut/split state)."""
    ep = store.episode_dir(ep_key, clip_id)
    rec = store.seed_record(ep_key, clip_id, ep)
    rec.update(
        {
            "emotion": g.emotion,
            "valence": g.valence,
            "arousal": g.arousal,
            "distress": g.distress,
            "note": g.note,
            "annotator": g.annotator or "human",
            "ts": store.now(),
        }
    )
    if g.speaker is not None:  # F6: human speaker overrides diarization
        rec["speaker"] = g.speaker
    if g.gold_text is not None:  # save edited text on confirm (not only on recut)
        rec["gold_text"] = g.gold_text
    return store.put(ep_key, clip_id, rec)


@app.post("/recut/{ep_key:path}/{clip_id}/undo")
def undo_recut(ep_key: str, clip_id: str) -> dict:
    """Restore the pristine clip audio + original boundaries from clips/_orig/."""
    ep = store.episode_dir(ep_key, clip_id)
    if not audio.restore_orig(ep, clip_id):
        raise HTTPException(404, "no backup to restore")
    seg = store.by_id(store.read_csv(ep / "segments.csv")).get(clip_id, {})
    rec = store.seed_record(ep_key, clip_id, ep)
    rec.update(
        {
            "start": store.fnum(seg.get("start")),
            "end": store.fnum(seg.get("end")),
            "recut": False,
            "excised": [],
            "gold_text": "",
            "ts": store.now(),
        }
    )
    return store.put(ep_key, clip_id, rec)


@app.post("/recut/{ep_key:path}/{clip_id}")
def put_recut(ep_key: str, clip_id: str, rc: RecutIn) -> dict:
    """Trim clip to [a,b] (clip-local seconds); back up original once; edit text."""
    ep = store.episode_dir(ep_key, clip_id)
    audio.trim(ep, clip_id, rc.a, rc.b)  # validates + backup + atomic slice
    rec = store.seed_record(ep_key, clip_id, ep)
    base = rec["start"]  # current clip's episode-time start (cumulative)
    rec.update(
        {
            "start": base + rc.a,
            "end": base + rc.b,
            "recut": True,
            "gold_text": rc.text,
            "ts": store.now(),
        }
    )
    return store.put(ep_key, clip_id, rec)


@app.post("/excise/{ep_key:path}/{clip_id}")
def put_excise(ep_key: str, clip_id: str, ex: ExciseIn) -> dict:
    """Remove [a,b] from the clip's middle; concatenate the rest (stays one clip).

    start/end keep the original bounding span; the removed region is appended to
    ``excised`` (clip-local seconds) so nothing is silently lost (provenance).
    Undo via /recut/undo (restores clips/_orig/ + clears excised).
    """
    ep = store.episode_dir(ep_key, clip_id)
    audio.excise(ep, clip_id, ex.a, ex.b)  # validates + backup + atomic concat
    rec = store.seed_record(ep_key, clip_id, ep)
    rec["excised"] = [*rec.get("excised", []), [ex.a, ex.b]]
    rec.update({"recut": True, "gold_text": ex.text, "ts": store.now()})
    return store.put(ep_key, clip_id, rec)


@app.post("/reject/{ep_key:path}/{clip_id}/undo")
def unreject(ep_key: str, clip_id: str) -> dict:
    """Clear the reject flag (clip returns to the labelable pool)."""
    ep = store.episode_dir(ep_key, clip_id)
    rec = store.seed_record(ep_key, clip_id, ep)
    rec.update({"rejected": False, "reject_reason": "", "ts": store.now()})
    return store.put(ep_key, clip_id, rec)


@app.post("/reject/{ep_key:path}/{clip_id}")
def put_reject(ep_key: str, clip_id: str, rj: RejectIn) -> dict:
    """Flag a clip as substandard — kept on disk, excluded downstream (phase 4)."""
    ep = store.episode_dir(ep_key, clip_id)
    rec = store.seed_record(ep_key, clip_id, ep)
    rec.update({"rejected": True, "reject_reason": rj.reason, "ts": store.now()})
    return store.put(ep_key, clip_id, rec)


@app.post("/split/{ep_key:path}/{clip_id}/undo")
def undo_split(ep_key: str, clip_id: str) -> dict:
    """Undo a split: delete all child clips (files + records), un-reject parent."""
    ep = store.episode_dir(ep_key, clip_id)
    parent = store.STATE.get(store.skey(ep_key, clip_id))
    if not parent or not parent.get("split_children"):
        raise HTTPException(404, "not a split parent")
    with store.LOCK:
        for ch in parent["split_children"]:
            wav = ep / "clips" / f"{ch}.wav"
            if wav.is_file():
                wav.unlink()
            store.STATE.pop(store.skey(ep_key, ch), None)
        parent = dict(parent)
        parent.update({"rejected": False, "reject_reason": "", "ts": store.now()})
        parent.pop("split_children", None)
        store.STATE[store.skey(ep_key, clip_id)] = parent
        store.save()
    return parent


@app.post("/split/{ep_key:path}/{clip_id}")
def put_split(ep_key: str, clip_id: str, sp: SplitIn) -> dict:
    """Split clip at ts[] into len(ts)+1 NEW clips (next seg numbers); parent kept + rejected."""
    if not sp.ts:
        raise HTTPException(400, "ts must have at least 1 cut point")
    ep = store.episode_dir(ep_key, clip_id)
    parent = store.seed_record(ep_key, clip_id, ep)
    with store.LOCK:
        ids = audio.split(ep, clip_id, sp.ts)  # validates increasing/in-range + atomic slice
        prov = store.inherited_provenance(ep, parent)
        p_start, p_end = parent["start"], parent["end"]
        bounds = [p_start, *(p_start + t for t in sp.ts), p_end]
        children = [
            store.child_record(ep_key, cid, parent, prov, s, e)
            for cid, s, e in zip(ids, bounds[:-1], bounds[1:])
        ]
        for rec in children:
            store.STATE[store.skey(ep_key, rec["id"])] = rec
        parent.update(
            {
                "rejected": True,
                "reject_reason": "split",
                "split_children": [c["id"] for c in children],
                "ts": store.now(),
            }
        )
        store.STATE[store.skey(ep_key, clip_id)] = parent
        store.save()
    return {"parent": parent, "children": children}


# Static UI (index.html) — mounted last so API routes win.
# no-cache: browser phải revalidate mỗi lần — tránh chạy JS cũ (cache) với HTML
# mới sau khi sửa UI (ES-module lệch phiên bản → TypeError giữa selectClip).
class _NoCacheStatic(StaticFiles):
    def file_response(self, *args, **kwargs):
        resp = super().file_response(*args, **kwargs)
        resp.headers["Cache-Control"] = "no-cache"
        return resp


app.mount("/", _NoCacheStatic(directory=str(HERE), html=True), name="ui")


def main() -> None:
    ap = argparse.ArgumentParser(description="ViEmoSpeech labeler backend")
    ap.add_argument(
        "--root",
        default="data/vietnamese-ser/episodes",
        help="episodes/ directory (default: %(default)s)",
    )
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    root = Path(a.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"--root is not a directory: {root}")
    store.set_root(root)
    store.load()
    print(
        f"labeler: root={root}  ({len(store.STATE)} labels)  ->  http://{a.host}:{a.port}/index.html"
    )
    uvicorn.run(app, host=a.host, port=a.port, log_level="info")


if __name__ == "__main__":
    main()
