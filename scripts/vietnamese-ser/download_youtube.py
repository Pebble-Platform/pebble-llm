"""Download audio (+ optional VN captions) for a range of episodes from a YouTube
series playlist, into data/vietnamese-ser/raw/<series>/epNN[_P].<ext> (gitignored).

Robust to playlists in reverse / arbitrary order: the episode id is parsed from each
video TITLE ("Tập N" or "Tập N.P"), never from playlist position — these playlists
list the newest/last part first (e.g. "Về nhà đi con" lists Tập 85 first, Tập 01 last;
"Chạy trốn thanh xuân" lists Tập 1.1 last).

Episode ids are tuples so both schemes work: "Tập 7" -> (7,), "Tập 3.2" -> (3, 2).
--episodes takes comma-separated singles and ranges, compared as tuples:
  "2-10"      -> (2,)..(10,)          e.g. Về nhà đi con
  "1.1-3.2"   -> (1,1)..(3,2)         includes 1.3 and 2.3 (they sort before 3.2)
  "5.1,5.3"   -> exactly those two
Range granularity should match the title: a "1-3" range on a "Tập X.Y" series stops
at (3,) and so DROPS 3.1/3.2 — use "1.1-3.9" to include them.

A download-archive (.download-archive.txt in --outdir) records finished videos, so a
re-run resumes and skips what's done (safe for a flaky connection over many episodes).

Usage (inside .venv-vnser, from repo root):
  python scripts/vietnamese-ser/download_youtube.py \
    --playlist "https://www.youtube.com/playlist?list=PLBXLcd_VlESNhK8eoS_wGZuB877b0N5mR" \
    --episodes 1.1-3.2 --outdir data/vietnamese-ser/raw/chay-tron-thanh-xuan
Optional: --audio-format m4a (default mp3) · --no-subs (skip captions)

Media stays under data/** (gitignored) — never commit. Research use only.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

TITLE_RE = re.compile(r"Tập\s+0*(\d+(?:\.\d+)*)", re.IGNORECASE)


def part_id(s: str) -> tuple[int, ...]:
    """'1.1' -> (1, 1) · '10' -> (10,) — the sortable episode key."""
    return tuple(int(x) for x in s.strip().split("."))


def parse_selection(spec: str) -> list[tuple]:
    """Comma-separated singles/ranges -> matchers: ('one', key) | ('range', lo, hi)."""
    sel: list[tuple] = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            sel.append(("range", part_id(a), part_id(b)))
        elif part:
            sel.append(("one", part_id(part)))
    return sel


def selected(key: tuple[int, ...], sel: list[tuple]) -> bool:
    return any(
        (m[0] == "one" and key == m[1]) or (m[0] == "range" and m[1] <= key <= m[2]) for m in sel
    )


def clip_name(key: tuple[int, ...]) -> str:
    """(3, 2) -> 'ep03_2' · (7,) -> 'ep07'."""
    return f"ep{key[0]:02d}" + "".join(f"_{x}" for x in key[1:])


def list_playlist(url: str) -> dict[tuple[int, ...], str]:
    """Flat-list the playlist -> {episode_key: video_id} parsed from titles."""
    out = subprocess.run(
        [sys.executable, "-m", "yt_dlp", "--flat-playlist", "--print", "%(title)s\t%(id)s", url],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    found: dict[tuple[int, ...], str] = {}
    for line in out.stdout.splitlines():
        if "\t" not in line:
            continue
        title, vid = line.rsplit("\t", 1)
        m = TITLE_RE.search(title)
        if m:
            found.setdefault(part_id(m.group(1)), vid.strip())  # first title wins on dup
    return found


def download(video_id: str, name: str, outdir: Path, audio_format: str, subs: bool) -> None:
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
        "--retries",
        "10",
        "--download-archive",
        str(archive),
        "-o",
        str(outdir / f"{name}.%(ext)s"),
    ]
    if subs:
        cmd += ["--write-subs", "--write-auto-subs", "--sub-langs", "vi", "--convert-subs", "srt"]
    cmd.append(f"https://www.youtube.com/watch?v={video_id}")
    subprocess.run(cmd, check=True)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # Vietnamese titles -> avoid cp1252 crash
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--playlist", required=True)
    ap.add_argument("--episodes", required=True, help="e.g. 2-10 or 1.1-3.2 or 5.1,5.3")
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--audio-format", default="mp3")
    ap.add_argument("--no-subs", action="store_true", help="skip caption download")
    args = ap.parse_args()

    sel = parse_selection(args.episodes)
    found = list_playlist(args.playlist)
    todo = sorted(k for k in found if selected(k, sel))
    if not todo:
        print("Không có tập nào khớp trong playlist.")
        return
    args.outdir.mkdir(parents=True, exist_ok=True)
    labels = ".".join(str(x) for x in todo[0]) + " … " + ".".join(str(x) for x in todo[-1])
    print(f"Sẽ tải {len(todo)} video (Tập {labels}) → {args.outdir}")
    failed: list[tuple[int, ...]] = []
    for key in todo:
        name = clip_name(key)
        print(f"\n=== {name}  (Tập {'.'.join(str(x) for x in key)}, id={found[key]}) ===")
        try:
            download(found[key], name, args.outdir, args.audio_format, not args.no_subs)
        except subprocess.CalledProcessError:
            failed.append(key)  # one bad video shouldn't kill the batch — retry on re-run
            print(f"⚠ Lỗi tải {name}, bỏ qua (archive sẽ skip video đã xong khi chạy lại).")
    print(
        f"\nXong {len(todo) - len(failed)}/{len(todo)} video. File: {args.outdir}/ep*.{args.audio_format}"
    )
    if failed:
        print("Thất bại: " + ", ".join(".".join(map(str, k)) for k in failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
