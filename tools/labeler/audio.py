"""Audio file ops for recut (F1) and split (F5): soundfile slicing + _orig backup.

Pure filesystem/audio — no STATE. Routes orchestrate the state.jsonl updates.
"""

from __future__ import annotations

import io
import re
import shutil
from pathlib import Path

import numpy as np
import soundfile as sf
import store
from fastapi import HTTPException


def next_seg_num(ep: Path) -> int:
    """Next free seg index in clips/ (max existing + 1; 0 if none)."""
    nums = [
        int(m.group(1))
        for p in (ep / "clips").glob("seg*.wav")
        if (m := re.fullmatch(r"seg(\d+)", p.stem))
    ]
    return max(nums) + 1 if nums else 0


def _write(path: Path, data, sr, subtype) -> None:
    """Atomic wav write: tmp (.wav ext, hidden from seg*.wav glob) -> rename."""
    tmp = path.parent / f".tmp_{path.name}"
    sf.write(str(tmp), data, sr, subtype=subtype, format="WAV")
    tmp.replace(path)


def backup_orig(ep: Path, clip_id: str) -> None:
    """Copy the pristine clip to clips/_orig/ once (first recut/split)."""
    orig = ep / "clips" / "_orig" / f"{clip_id}.wav"
    if not orig.exists():
        orig.parent.mkdir(exist_ok=True)
        shutil.copy2(store.clip_wav(ep, clip_id), orig)


def restore_orig(ep: Path, clip_id: str) -> bool:
    """Restore the clip from clips/_orig/; False if no backup exists."""
    orig = ep / "clips" / "_orig" / f"{clip_id}.wav"
    if not orig.is_file():
        return False
    shutil.copy2(orig, store.clip_wav(ep, clip_id))
    return True


def read_context(ep: Path, start: float, end: float, pad: float) -> bytes:
    """[start-pad, end+pad] of the episode's full audio as WAV bytes (context preview).

    Reads the full-mix audio (fallback vocals) at the clip's absolute episode-time
    bounds so the labeler can hear pad seconds before/after the cut. Read-only.
    """
    path = next((ep / n for n in ("audio_full.wav", "vocals_16k.wav") if (ep / n).is_file()), None)
    if path is None:
        raise HTTPException(404, "no episode audio (audio_full/vocals_16k)")
    info = sf.info(str(path))
    sr = info.samplerate
    i0 = max(0, int((start - pad) * sr))
    i1 = min(info.frames, int((end + pad) * sr))
    if i1 <= i0:
        raise HTTPException(400, "context range out of bounds")
    data, _ = sf.read(str(path), start=i0, stop=i1, dtype="float32")
    buf = io.BytesIO()
    sf.write(buf, data, sr, subtype=info.subtype, format="WAV")
    return buf.getvalue()


def full_duration(ep: Path) -> float:
    """Total seconds of the episode's de-musiced vocals (0 if missing)."""
    src = ep / "vocals_16k.wav"
    if not src.is_file():
        return 0.0
    info = sf.info(str(src))
    return round(info.frames / info.samplerate, 3)


def read_full_slice(ep: Path, a: float, b: float, pad: float = 0.0) -> bytes:
    """[a-pad, b+pad] of the episode's de-musiced vocals as WAV bytes (segment view).

    Reads vocals_16k.wav (music removed) so the human hears clean speech + context
    while choosing a region on the full episode timeline. Read-only.
    """
    src = ep / "vocals_16k.wav"
    if not src.is_file():
        raise HTTPException(404, "no vocals_16k.wav for this episode")
    info = sf.info(str(src))
    sr = info.samplerate
    i0 = max(0, int((a - pad) * sr))
    i1 = min(info.frames, int((b + pad) * sr))
    if i1 <= i0:
        raise HTTPException(400, "slice range out of bounds")
    data, _ = sf.read(str(src), start=i0, stop=i1, dtype="float32")
    buf = io.BytesIO()
    sf.write(buf, data, sr, subtype=info.subtype, format="WAV")
    return buf.getvalue()


def cut_from_full(ep: Path, a: float, b: float) -> tuple[str, float, float]:
    """Cut vocals_16k.wav[a,b] (episode seconds) into a NEW clip; return (id, a, b).

    Human-driven segmentation: unlike the auto VAD∩turn cut, the human picks the
    span (guided by the YouTube script). Music-removed vocals is the cut source.
    """
    if b - a <= 0.05:
        raise HTTPException(400, "selection too short")
    src = ep / "vocals_16k.wav"
    if not src.is_file():
        raise HTTPException(404, "no vocals_16k.wav for this episode")
    info = sf.info(str(src))
    sr = info.samplerate
    i0, i1 = max(0, int(a * sr)), min(info.frames, int(b * sr))
    if i1 <= i0:
        raise HTTPException(400, "selection out of range")
    data, _ = sf.read(str(src), start=i0, stop=i1, dtype="float32")
    cid = f"seg{next_seg_num(ep):05d}"
    _write(ep / "clips" / f"{cid}.wav", data, sr, info.subtype)
    return cid, a, b


def trim(ep: Path, clip_id: str, a: float, b: float) -> None:
    """Back up once, then overwrite the clip with [a,b] (clip-local seconds)."""
    if b - a <= 0.01:
        raise HTTPException(400, "empty selection")
    wav = store.clip_wav(ep, clip_id)
    backup_orig(ep, clip_id)
    info = sf.info(str(wav))
    data, sr = sf.read(str(wav), dtype="float32")
    i0, i1 = max(0, int(a * sr)), min(len(data), int(b * sr))
    if i1 <= i0:
        raise HTTPException(400, "selection out of range")
    _write(wav, data[i0:i1], sr, info.subtype)


def excise(ep: Path, clip_id: str, a: float, b: float) -> None:
    """Back up once, then remove [a,b] (clip-local seconds) and concatenate the rest.

    The clip stays ONE file — [0,a] and [b,dur] are joined (unlike split, which
    makes separate children). start/end are untouched by the caller; the removed
    region is recorded in the record's ``excised`` list (provenance).
    """
    if b - a <= 0.01:
        raise HTTPException(400, "empty selection")
    wav = store.clip_wav(ep, clip_id)
    backup_orig(ep, clip_id)
    info = sf.info(str(wav))
    data, sr = sf.read(str(wav), dtype="float32")
    i0, i1 = max(0, int(a * sr)), min(len(data), int(b * sr))
    if i1 <= i0 or i0 <= 0 or i1 >= len(data):
        raise HTTPException(400, "excise region must be strictly inside the clip")
    _write(wav, np.concatenate([data[:i0], data[i1:]]), sr, info.subtype)


def split(ep: Path, clip_id: str, ts: list[float]) -> list[str]:
    """Write len(ts)+1 NEW child clips (next seg numbers) from the parent; return their ids.

    ts must be strictly increasing and each point strictly inside (0, duration).
    """
    wav = store.clip_wav(ep, clip_id)
    info = sf.info(str(wav))
    data, sr = sf.read(str(wav), dtype="float32")
    idxs = [int(t * sr) for t in ts]
    if any(idxs[i] >= idxs[i + 1] for i in range(len(idxs) - 1)):
        raise HTTPException(400, "split points must be strictly increasing")
    if idxs[0] <= 0 or idxs[-1] >= len(data):
        raise HTTPException(400, "split point out of range")
    n = next_seg_num(ep)
    ids = [f"seg{n + i:05d}" for i in range(len(idxs) + 1)]
    bounds = [0, *idxs, len(data)]
    for cid, i0, i1 in zip(ids, bounds[:-1], bounds[1:]):
        _write(ep / "clips" / f"{cid}.wav", data[i0:i1], sr, info.subtype)
    return ids
