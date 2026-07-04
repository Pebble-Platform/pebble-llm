"""Extract demo clips for the voice website — one held-out RAVDESS clip per emotion.

Reads the Zenodo RAVDESS speech zip and writes 8 clips (one per emotion, preferring
held-out actors 21-24, normal intensity) into the samples dir the web app serves.
RAVDESS filename 03-01-EE-II-SS-RR-AA.wav: EE = 1-indexed emotion code, AA = actor.

    python scripts/make_voice_samples.py
    python scripts/make_voice_samples.py --zip <path> --out data/external/voice_samples
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

EMOTIONS = ["neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised"]


def rank(name: str) -> tuple[int, int, int]:
    """Lower is preferred: held-out actor first, then normal intensity, then actor id."""
    p = Path(name).stem.split("-")
    actor, intensity = int(p[6]), int(p[3])
    return (0 if actor in (21, 22, 23, 24) else 1, intensity, actor)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", default="data/external/ravdess/Audio_Speech_Actors_01-24.zip")
    ap.add_argument("--out", default="data/external/voice_samples")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    z = zipfile.ZipFile(args.zip)

    best: dict[int, str] = {}
    for n in z.namelist():
        if not n.lower().endswith(".wav"):
            continue
        p = Path(n).stem.split("-")
        if len(p) < 7:
            continue
        ee = int(p[2])  # 1..8
        if ee not in best or rank(n) < rank(best[ee]):
            best[ee] = n

    for ee in sorted(best):
        data = z.read(best[ee])
        (out / Path(best[ee]).name).write_bytes(data)
        print(f"{EMOTIONS[ee - 1]:10s} <- {Path(best[ee]).name}")
    print(f"wrote {len(best)} samples -> {out}")


if __name__ == "__main__":
    main()
