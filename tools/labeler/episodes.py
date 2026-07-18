"""Read-side: build the /episodes listing and one /episode's joined clip data."""

from __future__ import annotations

import re
from pathlib import Path

import store

EP_RE = re.compile(r"^ep\d+(_\d+)?$", re.IGNORECASE)


def _label(d: dict | None) -> dict | None:
    if not d:
        return None
    return {
        "emotion": d.get("emotion", ""),
        "valence": d.get("valence", ""),
        "arousal": d.get("arousal", ""),
        "distress": d.get("distress", ""),
        "multi_speaker_suspect": d.get("multi_speaker_suspect", ""),
    }


def listing() -> list[dict]:
    """Every epNN[_K] folder under ROOT that has cut clips, with progress counts."""
    out = []
    for ep_dir in sorted(p for p in store.ROOT.rglob("*") if p.is_dir() and EP_RE.match(p.name)):
        clips_dir = ep_dir / "clips"
        total = len(list(clips_dir.glob("seg*.wav"))) if clips_dir.is_dir() else 0
        if not total:
            continue
        ep_rel = ep_dir.relative_to(store.ROOT).as_posix()
        series_rel = ep_dir.parent.relative_to(store.ROOT).as_posix()
        recs = [r for k, r in store.STATE.items() if k.startswith(ep_rel + "\t")]
        out.append(
            {
                "epKey": ep_rel,
                "series": series_rel or "(root)",
                "epName": ep_dir.name,
                "total": total,
                "done": sum(1 for r in recs if r.get("emotion") and not r.get("rejected")),
                "rejected": sum(1 for r in recs if r.get("rejected")),
            }
        )
    return out


def build(ep_key: str, ep: Path) -> dict:
    """Join segments + transcripts + teacher suggestions + saved labels for one episode."""
    seg = store.by_id(store.read_csv(ep / "segments.csv"))
    tr_yt = store.by_id(store.read_csv(ep / "transcripts_yt.csv"))
    tr = store.by_id(store.read_csv(ep / "transcripts.csv"))
    opus = store.by_id(store.read_csv(ep / "labels_opus.csv"))
    sonnet = store.by_id(store.read_csv(ep / "labels_sonnet.csv"))

    clips = []
    for cid in sorted(p.stem for p in (ep / "clips").glob("seg*.wav")):
        s, y, t = seg.get(cid, {}), tr_yt.get(cid, {}), tr.get(cid, {})
        rec = store.STATE.get(store.skey(ep_key, cid))  # label; may carry recut boundaries
        if rec and rec.get("split_from"):
            # split child (F5): no CSV row exists for this id — the record
            # carries what it inherited from the parent at creation time
            # (store.inherited_provenance), not a CSV lookup.
            asr, yt_text = rec.get("asr", ""), rec.get("yt", "")
            o, n = rec.get("opus_detail"), rec.get("sonnet_detail")
        else:
            asr = y.get("text_phowhisper") or t.get("text") or ""
            yt_text = y.get("text_youtube", "")
            o, n = _label(opus.get(cid)), _label(sonnet.get(cid))
        clips.append(
            {
                "id": cid,
                # recut boundaries (in the record) win over the original segments.csv
                "start": rec["start"]
                if rec
                else store.fnum(s.get("start"), y.get("start"), t.get("start")),
                "end": rec["end"] if rec else store.fnum(s.get("end"), y.get("end"), t.get("end")),
                "speaker": rec["speaker"] if rec else s.get("speaker", ""),  # rec (F6) wins
                "asr": asr,
                "yt": yt_text,
                "opus": o,
                "sonnet": n,
                "disagree": bool(o and n and o["emotion"] != n["emotion"]),
                "gold": rec,
            }
        )
    seg_spk = {r.get("speaker") for r in seg.values() if r.get("speaker")}
    st_spk = {
        r.get("speaker")
        for k, r in store.STATE.items()
        if k.startswith(ep_key + "\t") and r.get("speaker")
    }
    return {"epKey": ep_key, "clips": clips, "speakers": sorted(seg_spk | st_spk)}
