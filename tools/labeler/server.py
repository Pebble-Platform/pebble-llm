"""FastAPI backend for tools/labeler — change 003 (thin routes; logic in modules).

Run (from repo root):
  .venv-vnser/Scripts/python.exe tools/labeler/server.py \
      --root data/vietnamese-ser/episodes
  # then open http://127.0.0.1:8000/index.html

Layers: store.py (config/state.db/records/paths) · episodes.py (read/join) ·
audio.py (soundfile recut/split). Binds 127.0.0.1 only; data/** is copyrighted
media, local-only (intent §1). Human labels are the source of truth (ADR-003).
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import audio
import auth
import episodes
import store
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

HERE = Path(__file__).resolve().parent
app = FastAPI(title="ViEmoSpeech labeler")

# Shell files an unauthenticated browser may load — markup/JS only, no corpus data.
# Everything else goes through the guard below.
PUBLIC = {"/rate.html", "/rate.js"}


@app.middleware("http")
async def guard(request: Request, call_next):
    """The single security boundary (ADR-005 safeguard #2) — deny by default.

    One middleware rather than a dependency on each of ~20 routes: a boundary you can
    audit in one place cannot be defeated by forgetting to decorate a new route. Any
    route added later is owner-only until someone deliberately puts it under /rate.
    """
    path = request.url.path
    if path in PUBLIC:
        return await call_next(request)
    try:
        p = auth.principal(request)
        if not (path.startswith("/rate/") or p.is_admin):
            raise HTTPException(403, "admin only")
    except HTTPException as e:
        return JSONResponse({"detail": e.detail}, status_code=e.status_code)
    request.state.principal = p
    return await call_next(request)


# ---------- request models ----------
class GoldIn(BaseModel):
    emotion: str
    valence: int
    arousal: int
    distress: bool = False
    note: str = ""
    gold_text: str | None = None  # human text of record; None = keep existing
    gender: str = ""  # per-clip human demographic: "" | female | male
    age_group: str = ""  # "" | child | teen | young_adult | middle_aged | senior
    dialect: str = ""  # "" | north | central | south (Bắc/Trung/Nam — hệ thanh điệu khác nhau)
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


class RejectBulkIn(BaseModel):
    ids: list[str]  # clip ids the user multi-selected to reject in one go
    reason: str = "other"


class SplitIn(BaseModel):
    ts: list[float]  # split points, clip-local seconds, strictly increasing, k >= 1


class SegmentIn(BaseModel):
    a: float  # region start, episode seconds (on the full de-musiced audio)
    b: float  # region end
    text: str = ""  # YouTube-script text of the span (seeds gold_text)


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


@app.get("/stats")
def get_stats() -> dict:
    """Live labeling-progress dashboard data (see stats.html); recomputed per call."""
    return episodes.stats()


@app.get("/gold")
def all_gold() -> list[dict]:
    """Every human label record (source of truth = state.db)."""
    return list(store.STATE.values())


@app.get("/script/{ep_key:path}")
def get_script(ep_key: str) -> dict:
    """YouTube subtitle timeline + full-audio duration for manual segmentation."""
    ep = store.episode_dir(ep_key)
    return {"duration": audio.full_duration(ep), "blocks": episodes.youtube_script(ep)}


@app.get("/segment-audio/{ep_key:path}.wav")
def get_segment_audio(ep_key: str, a: float, b: float, pad: float = 0.0) -> Response:
    """[a-pad, b+pad] of the de-musiced vocals (preview a candidate region, read-only)."""
    ep = store.episode_dir(ep_key)
    return Response(
        audio.read_full_slice(ep, a, b, pad),
        media_type="audio/wav",
        headers={"Cache-Control": "no-store"},
    )


# ---------- gold-set audition (change 011, qc-protocol §2.1 step 2) ----------
CHANGE_011 = HERE.parent.parent / "docs" / "spec" / "changes" / "011-online-multi-annotator"


class GoldSetIn(BaseModel):
    keys: list[str]  # "epKey/clip_id" rows the owner confirmed are obvious


@app.get("/gold-candidates")
def gold_candidates() -> list[dict]:
    """The shortlist from pick_gold_candidates.py, joined with the owner's own label."""
    tsv = CHANGE_011 / "gold-candidates.tsv"
    if not tsv.is_file():
        raise HTTPException(404, "run scripts/vietnamese-ser/pick_gold_candidates.py first")
    out, kept = [], set()
    if (CHANGE_011 / "gold-set.txt").is_file():
        kept = {
            ln.strip()
            for ln in (CHANGE_011 / "gold-set.txt").read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")
        }
    for ln in tsv.read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        key, emotion, *_ = ln.split("\t")
        ep_key, _, clip_id = key.rpartition("/")
        out.append(
            {
                "key": key,
                "emotion": emotion,
                "wav": f"/clip/{ep_key}/{clip_id}.wav",
                "keep": (not kept) or key in kept,  # first pass: all in, drop the unclear
            }
        )
    return out


@app.post("/gold-set")
def save_gold_set(g: GoldSetIn) -> dict:
    """Write the confirmed gold set. This file is part of the frozen pre-registration."""
    path = CHANGE_011 / "gold-set.txt"
    path.write_text(
        "# Gold anchors — owner-confirmed obvious (qc-protocol §2.1).\n"
        "# NOT 'the right answer': catches an annotator who is not listening,\n"
        "# never one who hears differently. Generated by the labeler audition screen.\n"
        + "\n".join(g.keys)
        + "\n",
        encoding="utf-8",
    )
    return {"written": len(g.keys), "path": str(path)}


@app.get("/review")
def review() -> dict:
    """Per-clip comparison of every rater's judgment (owner-only, change 011).

    One row per clip: the owner's label of record plus what each annotator said, so
    disagreement can be inspected where it actually lives instead of only in aggregate.
    An annotator may appear twice on one clip — that is the QC duplicate, and seeing
    both answers side by side is exactly the point.
    """
    rows: dict[tuple[str, str], dict] = {}
    for r in store.all_ratings():
        key = (r["epkey"], r["id"])
        row = rows.setdefault(
            key, {"epKey": r["epkey"], "id": r["id"], "kinds": set(), "ratings": {}}
        )
        row["kinds"].add(r["kind"])
        row["ratings"].setdefault(r["annotator"], []).append(
            {
                "emotion": r["emotion"],
                "valence": r["valence"],
                "arousal": r["arousal"],
                "skip": r["skip_reason"],
                "listen_ms": r["listen_ms"],
            }
        )

    out = []
    for (ep_key, clip_id), row in rows.items():
        rec = store.STATE.get(store.skey(ep_key, clip_id), {})
        # majority over one answer per rater (first presentation) + the owner's label
        votes = [a[0]["emotion"] for a in row["ratings"].values() if a[0]["emotion"]]
        if rec.get("emotion"):
            votes.append(rec["emotion"])
        top, n = ("", 0)
        if votes:
            top, n = Counter(votes).most_common(1)[0]
        out.append(
            {
                "key": f"{ep_key}/{clip_id}",
                "wav": f"/clip/{ep_key}/{clip_id}.wav",
                "kind": sorted(row["kinds"]),
                "owner": {
                    "emotion": rec.get("emotion", ""),
                    "valence": rec.get("valence"),
                    "arousal": rec.get("arousal"),
                },
                "ratings": row["ratings"],
                "majority": top if n >= 2 else "no_agreement",
                "unanimous": bool(votes) and n == len(votes),
                "n_votes": len(votes),
            }
        )
    out.sort(key=lambda r: (r["unanimous"], r["key"]))  # disagreement first
    return {
        "annotators": sorted({a for r in out for a in r["ratings"]}),
        "rows": out,
    }


# ---------- online second-pass rating (change 011) ----------
class RateIn(BaseModel):
    emotion: str = ""  # "" only when skipping
    valence: int | None = None
    arousal: int | None = None
    skip_reason: str = ""  # unclear | multi_speaker | bad_cut | no_speech
    listen_ms: int = 0  # audio actually played (QC §2.3 min-time gate)


@app.get("/rate/next")
def rate_next(request: Request) -> dict:
    """The annotator's next queue slot — position + progress only, never clip identity."""
    who = request.state.principal
    item = store.next_seq(who.id)
    prog = store.progress(who.id)
    return {"seq": None if item is None else item["seq"], **prog}


@app.get("/rate/clip/{seq}.wav")
def rate_clip(request: Request, seq: int) -> FileResponse:
    """Serve one clip BY QUEUE POSITION — the annotator's only path to audio.

    Addressing by position (not epKey/clip_id) means an annotator cannot enumerate the
    corpus or reassemble a contiguous scene: they can only fetch slots assigned to them,
    in an order that was shuffled once at assignment (ADR-005 safeguards #2/#4).
    """
    who = request.state.principal
    ep_key, clip_id = store.assignment_clip(who.id, seq)
    auth.log_access(who.id, "clip", f"{ep_key}/{clip_id}")
    ep = store.episode_dir(ep_key, clip_id)
    return FileResponse(
        store.clip_wav(ep, clip_id), media_type="audio/wav", headers={"Cache-Control": "no-store"}
    )


@app.post("/rate/{seq}")
def rate_save(request: Request, seq: int, r: RateIn) -> dict:
    """Save one judgment. Writes only this annotator's own slot; `records` untouched."""
    who = request.state.principal
    if not r.emotion and not r.skip_reason:
        raise HTTPException(400, "need an emotion or a skip reason")
    store.save_rating(
        who.id, seq, r.emotion, r.valence, r.arousal, r.skip_reason, max(0, r.listen_ms)
    )
    auth.log_access(who.id, "rate", f"seq={seq} {r.emotion or r.skip_reason}")
    return store.progress(who.id)


@app.get("/rate/whoami")
def rate_whoami(request: Request) -> dict:
    return {"id": request.state.principal.id, **store.progress(request.state.principal.id)}


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
            "gender": g.gender,  # per-clip human demographic (replaces cast lookup)
            "age_group": g.age_group,
            "dialect": g.dialect,
            "annotator": g.annotator or "human",
            "ts": store.now(),
        }
    )
    if g.gold_text is not None:  # save edited text on confirm (not only on recut)
        rec["gold_text"] = g.gold_text
    return store.put(ep_key, clip_id, rec)


@app.post("/segment/{ep_key:path}")
def put_segment(ep_key: str, s: SegmentIn) -> dict:
    """Cut a NEW clip from the full vocals for span [a,b]; seed a labelable record.

    Human-driven segmentation (episodes not yet labeled): the human picks the span
    on the full de-musiced audio guided by the YouTube script, instead of the auto
    VAD∩turn cut that was losing context. Appends (auto clips kept).
    """
    ep = store.episode_dir(ep_key)
    series = ep.parent.relative_to(store.ROOT).as_posix() or "(root)"
    with store.LOCK:
        cid, a, b = audio.cut_from_full(ep, s.a, s.b)
        rec = store.manual_record(ep_key, cid, series, ep.name, a, b, s.text)
        store.STATE[store.skey(ep_key, cid)] = rec
        store.save()
    return rec


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


@app.post("/reject-bulk/{ep_key:path}")
def put_reject_bulk(ep_key: str, rj: RejectBulkIn) -> list[dict]:
    """Reject many clips in one atomic save — user multi-selects rows, removes at once."""
    ep = store.episode_dir(ep_key)
    for cid in rj.ids:
        if not store.CLIP_RE.match(cid):
            raise HTTPException(400, f"bad clip id: {cid}")
    with store.LOCK:
        for cid in rj.ids:
            rec = store.seed_record(ep_key, cid, ep)
            rec.update({"rejected": True, "reject_reason": rj.reason, "ts": store.now()})
            store.STATE[store.skey(ep_key, cid)] = rec
        store.save()
        return [store.STATE[store.skey(ep_key, cid)] for cid in rj.ids]


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
    ap.add_argument(
        "--tokens",
        default=None,
        help="tokens.json (annotator access; default <root>/tokens.json if present)",
    )
    ap.add_argument(
        "--no-local-admin",
        action="store_true",
        help="require a token even from localhost (use when a tunnel is open)",
    )
    a = ap.parse_args()
    root = Path(a.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"--root is not a directory: {root}")
    store.set_root(root)
    store.load()
    tokens_path = Path(a.tokens) if a.tokens else root / "tokens.json"
    n_tok = auth.configure(tokens_path, not a.no_local_admin, root / "access.log")
    print(
        f"labeler: root={root}  ({len(store.STATE)} labels, {n_tok} tokens)"
        f"  ->  http://{a.host}:{a.port}/index.html"
    )
    if n_tok and not a.no_local_admin:
        print(
            "  note: loopback still gets admin without a token. A tunnel is proxied "
            "(x-forwarded-*) so it does NOT — but pass --no-local-admin for a "
            "belt-and-braces labeling round."
        )
    uvicorn.run(app, host=a.host, port=a.port, log_level="info")


if __name__ == "__main__":
    main()
