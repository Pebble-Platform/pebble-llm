"""Download audio (+ optional VN captions) for a range of episodes from a YouTube
series playlist, into data/vietnamese-ser/raw/<series>/epNN.<ext> (gitignored).

Robust to playlists in reverse / arbitrary order: the episode number is parsed from
each video TITLE ("Tập N"), never from playlist position — the "Về nhà đi con"
playlist, for example, lists Tập 85 first and Tập 01 last, so playlist index != episode.

A download-archive (.download-archive.txt in --outdir) records finished videos, so a
re-run resumes and skips what's done (safe for a flaky connection over many episodes).

Usage (inside .venv-vnser, from repo root):
  python scripts/vietnamese-ser/download_youtube.py \
    --playlist "https://www.youtube.com/playlist?list=PLBXLcd_VlESMHHI4GyJu99FZfOHnx_vX-" \
    --episodes 2-10 --outdir data/vietnamese-ser/raw/ve-nha-di-con
Optional: --audio-format m4a (default mp3) · --no-subs (skip captions)

Media stays under data/** (gitignored) — never commit. Research use only.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

TITLE_RE = re.compile(r"Tập\s+0*(\d+)", re.IGNORECASE)


def parse_episodes(spec: str) -> list[int]:
    """'2-10' or '2,5,7' or '2-4,8' -> sorted unique episode numbers."""
    eps: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            eps.update(range(int(a), int(b) + 1))
        elif part:
            eps.add(int(part))
    return sorted(eps)


def list_playlist(url: str) -> dict[int, str]:
    """Flat-list the playlist -> {episode_number: video_id} parsed from titles."""
    out = subprocess.run(
        [sys.executable, "-m", "yt_dlp", "--flat-playlist", "--print", "%(title)s\t%(id)s", url],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    found: dict[int, str] = {}
    for line in out.stdout.splitlines():
        if "\t" not in line:
            continue
        title, vid = line.rsplit("\t", 1)
        m = TITLE_RE.search(title)
        if m:
            found.setdefault(int(m.group(1)), vid.strip())  # first title wins on dup
    return found


def download(video_id: str, ep: int, outdir: Path, audio_format: str, subs: bool) -> None:
    archive = outdir / ".download-archive.txt"
    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "-f",
        "bestaudio/best",
        "-x",
        "--audio-format",
        audio_format,
        "--no-overwrites",
        "--download-archive",
        str(archive),
        "-o",
        str(outdir / f"ep{ep:02d}.%(ext)s"),
    ]
    if subs:
        cmd += ["--write-subs", "--write-auto-subs", "--sub-langs", "vi", "--convert-subs", "srt"]
    cmd.append(f"https://www.youtube.com/watch?v={video_id}")
    subprocess.run(cmd, check=True)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # Vietnamese titles -> avoid cp1252 crash
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--playlist", required=True)
    ap.add_argument("--episodes", required=True, help="e.g. 2-10 or 2,5,7")
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--audio-format", default="mp3")
    ap.add_argument("--no-subs", action="store_true", help="skip caption download")
    args = ap.parse_args()

    want = set(parse_episodes(args.episodes))
    found = list_playlist(args.playlist)
    todo = sorted(want & found.keys())
    missing = sorted(want - found.keys())
    if missing:
        print(f"⚠ Không tìm thấy tập {missing} trong playlist (bỏ qua).")
    if not todo:
        print("Không có tập nào để tải.")
        return
    args.outdir.mkdir(parents=True, exist_ok=True)
    print(f"Sẽ tải {len(todo)} tập {todo} → {args.outdir}")
    for ep in todo:
        print(f"\n=== Tập {ep:02d} (id={found[ep]}) ===")
        download(found[ep], ep, args.outdir, args.audio_format, not args.no_subs)
    print(f"\nXong {len(todo)} tập. File: {args.outdir}/ep*.{args.audio_format}")


if __name__ == "__main__":
    main()
