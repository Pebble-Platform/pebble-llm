"""Recap detection (change 006): find the audio span an episode replays from its
predecessor (the "recap" at the start of VN TV dramas), so its duplicate clips can
be bulk-marked once.

Method (task-researcher M1): log-mel feature-sequence cross-correlation. Reuse the
repo's torchaudio mel front-end, pool to 100ms superframes, L2-normalize (robust to
the two episodes being different transcodes), cosine-similarity matrix over the tail
of ep N-1 vs the head of ep N, pick the best diagonal, take the longest contiguous
high-similarity run as the span. Pure read + numpy/torch — no state mutation.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import soundfile as sf
import store
import torch
import torchaudio
from fastapi import HTTPException

SR = 16000
WIN = 240.0  # search window: tail of prev / head of cur (seconds)
POOL = 10  # 10ms mel frames -> 100ms superframes
HOP_S = POOL * 160 / SR  # superframe duration (0.1s)
# Constants calibrated on ve-nha-di-con (change 006): the one real recap ep05->ep06
# runs 13.5s @ mean-cosine 0.97, while incidental matches are <3s @ ~0.80-0.88 —
# a wide margin. Using vocals_16k (speech-separated) removes shared theme music, so
# jingle false positives (the 15s-min guard the research assumed) don't appear here.
MIN_RUN_S = 6.0  # shortest span reported as a recap
SMOOTH = 5  # moving-average superframes (~0.5s) to bridge tiny dips
TAU_FRAME = 0.85  # per-superframe cosine to count as "matching"
TAU_MEAN = 0.90  # mean cosine over the run to accept (real recap 0.97 >> incidental)
GAP = 8  # superframes (~0.8s) tolerated inside a run without splitting it
SIL_RMS = 0.0032  # ~-50 dBFS: below this a superframe is treated as silence

_MEL = torchaudio.transforms.MelSpectrogram(sample_rate=SR, n_fft=400, hop_length=160, n_mels=40)


def previous_episode(ep_key: str) -> tuple[str, Path]:
    """The sibling episode just before ep_key in the same series (has cut clips)."""
    ep = store.episode_dir(ep_key)
    sibs = sorted(
        (p for p in ep.parent.iterdir() if p.is_dir() and (p / "clips").glob("seg*.wav")),
        key=lambda p: [int(n) for n in re.findall(r"\d+", p.name)] or [0],
    )
    names = [p.name for p in sibs]
    if ep.name not in names or names.index(ep.name) == 0:
        raise HTTPException(404, "no previous episode to compare against")
    prev = sibs[names.index(ep.name) - 1]
    return prev.relative_to(store.ROOT).as_posix(), prev


def _audio_path(ep: Path) -> Path:
    for name in ("vocals_16k.wav", "audio_full.wav"):
        if (ep / name).is_file():
            return ep / name
    raise HTTPException(404, f"no episode audio (vocals_16k/audio_full) in {ep.name}")


def _load(ep: Path, *, head: bool) -> tuple[np.ndarray, float]:
    """Load the first (head) or last (tail) WIN seconds; return (mono float32, offset_s)."""
    path = _audio_path(ep)
    info = sf.info(str(path))
    dur = info.frames / info.samplerate
    if head:
        start_s = 0.0
        data, sr = sf.read(str(path), stop=int(WIN * info.samplerate), dtype="float32")
    else:
        start_s = max(0.0, dur - WIN)
        data, sr = sf.read(str(path), start=int(start_s * info.samplerate), dtype="float32")
    if data.ndim > 1:
        data = data.mean(axis=1)
    if sr != SR:  # pipeline wavs are 16k; resample only if a stray file isn't
        data = torchaudio.functional.resample(torch.from_numpy(data), sr, SR).numpy()
    return data, start_s


def _features(wav: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """L2-normalized 100ms log-mel superframes [n,40] + per-superframe RMS [n]."""
    mel = torch.log1p(_MEL(torch.from_numpy(wav)))  # [40, F]
    n = mel.shape[1] // POOL
    sfm = mel[:, : n * POOL].reshape(40, n, POOL).mean(2).T.numpy()  # [n,40]
    feat = sfm / np.maximum(np.linalg.norm(sfm, axis=1, keepdims=True), 1e-8)
    blk = POOL * 160
    m = min(len(wav) // blk, n)
    rms = np.zeros(n, dtype=np.float32)
    if m:
        rms[:m] = np.sqrt((wav[: m * blk].reshape(m, blk) ** 2).mean(1))
    return feat, rms


def _longest_run(good: np.ndarray) -> tuple[int, int]:
    """[start, end) of the longest contiguous True run (empty -> (0,0))."""
    if not good.any():
        return 0, 0
    edges = np.flatnonzero(np.diff(np.concatenate(([0], good.astype(np.int8), [0]))))
    starts, ends = edges[::2], edges[1::2]
    k = int((ends - starts).argmax())
    return int(starts[k]), int(ends[k])


def detect(prev_ep: Path, cur_ep: Path) -> dict:
    """Best repeated span between prev_ep's tail and cur_ep's head.

    Returns {matched, score, run_s, cur_span:[t0,t1], prev_span:[t0,t1]} — spans in
    absolute episode seconds. cur_span is what to mark in cur_ep; prev_span is the
    canonical copy in prev_ep.
    """
    a, a_off = _load(prev_ep, head=False)  # prev tail
    b, b_off = _load(cur_ep, head=True)  # cur head
    A, a_rms = _features(a)
    B, b_rms = _features(b)
    na, nb = len(A), len(B)
    min_run = int(MIN_RUN_S / HOP_S)
    empty = {
        "matched": False,
        "score": 0.0,
        "run_s": 0.0,
        "cur_span": [0.0, 0.0],
        "prev_span": [0.0, 0.0],
    }
    if na < min_run or nb < min_run:
        return empty
    S = A @ B.T  # cosine similarity (both L2-normalized)
    a_ok, b_ok = a_rms >= SIL_RMS, b_rms >= SIL_RMS
    kern = np.ones(SMOOTH) / SMOOTH

    best = {"len": 0, "mean": 0.0, "i0": 0, "i1": 0, "lag": 0}
    for lag in range(-(na - 1), nb):  # lag = j - i (cur index - prev index)
        i0 = max(0, -lag)
        i1 = min(na, nb - lag)
        if i1 - i0 < min_run:
            continue
        i = np.arange(i0, i1)
        diag = S[i, i + lag]
        # silence on either side shouldn't count as a match
        diag = np.where(a_ok[i] & b_ok[i + lag], diag, 0.0)
        sm = np.convolve(diag, kern, mode="same")
        good = sm >= TAU_FRAME
        # bridge short gaps (<=GAP) so a brief pause doesn't split a real run
        if GAP:
            pad = np.concatenate(([True], good, [True]))
            edges = np.flatnonzero(np.diff(pad.astype(np.int8)))
            for s, e in zip(edges[::2], edges[1::2]):  # s..e are False (gap) spans
                if s > 0 and e < len(good) and e - s <= GAP:
                    good[s:e] = True
        s, e = _longest_run(good)
        run = e - s
        if run > best["len"]:
            best = {
                "len": run,
                "mean": float(diag[s:e].mean()) if run else 0.0,
                "i0": i0 + s,
                "i1": i0 + e,
                "lag": lag,
            }

    run_s = best["len"] * HOP_S
    matched = run_s >= MIN_RUN_S and best["mean"] >= TAU_MEAN
    pi0, pi1 = best["i0"], best["i1"]  # prev-tail superframe indices
    cj0, cj1 = pi0 + best["lag"], pi1 + best["lag"]  # cur-head indices
    return {
        "matched": bool(matched),
        "score": round(best["mean"], 3),
        "run_s": round(run_s, 1),
        "cur_span": [round(b_off + cj0 * HOP_S, 2), round(b_off + cj1 * HOP_S, 2)],
        "prev_span": [round(a_off + pi0 * HOP_S, 2), round(a_off + pi1 * HOP_S, 2)],
    }


def clips_in_span(ep_key: str, ep: Path, span: list[float]) -> list[str]:
    """Clip ids whose [start,end] overlap span (recut boundaries in state win)."""
    t0, t1 = span
    out = []
    for row in store.read_csv(ep / "segments.csv"):
        cid = row.get("id")
        if not cid:
            continue
        rec = store.STATE.get(store.skey(ep_key, cid))
        start = rec["start"] if rec else store.fnum(row.get("start"))
        end = rec["end"] if rec else store.fnum(row.get("end"))
        if start < t1 and end > t0:
            out.append(cid)
    return sorted(out)
