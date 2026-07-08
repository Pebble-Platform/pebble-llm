"""Audio file ops for recut (F1) and split (F5): soundfile slicing + _orig backup.

Pure filesystem/audio — no STATE. Routes orchestrate the state.jsonl updates.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

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


def split(ep: Path, clip_id: str, t: float) -> tuple[str, str]:
    """Write 2 NEW child clips (next seg numbers) from the parent; return their ids."""
    wav = store.clip_wav(ep, clip_id)
    info = sf.info(str(wav))
    data, sr = sf.read(str(wav), dtype="float32")
    i = int(t * sr)
    if i <= 0 or i >= len(data):
        raise HTTPException(400, "split point out of range")
    n = next_seg_num(ep)
    id_a, id_b = f"seg{n:05d}", f"seg{n + 1:05d}"
    _write(ep / "clips" / f"{id_a}.wav", data[:i], sr, info.subtype)
    _write(ep / "clips" / f"{id_b}.wav", data[i:], sr, info.subtype)
    return id_a, id_b
