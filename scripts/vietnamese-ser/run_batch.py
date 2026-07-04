"""Batch-run the extraction pipeline over a series' episodes (sequential, resumable).

For each epNN in range: convert raw/<series>/epNN.vi.srt -> youtube_transcripts.txt
(dedup consecutive rolling-caption lines), run pilot_extract.py (--turn-split when
HF_TOKEN is set, else fallback VAD cut), then align_youtube.py. Episodes whose
outdir already has report.md + transcripts.csv (+ transcripts_yt.csv when a caption
exists) are skipped, and pilot_extract's own stage caches make partial re-runs cheap.
Ends by writing episodes/<series>/summary.csv (one row per processed episode).

Usage (from repo root; heavy deps come from .venv-vnser via the interpreter path):
  set HF_TOKEN=hf_xxx   (PowerShell: $env:HF_TOKEN="hf_xxx")
  PYTHONIOENCODING=utf-8 python scripts/vietnamese-ser/run_batch.py \
      --series ve-nha-di-con --episodes 2-10
Optional: --skip-asr (yield stats only) · --python .venv-vnser/Scripts/python.exe

CPU time ~1.5-2h/episode (Demucs + pyannote + PhoWhisper) -> run overnight; safe to
Ctrl-C and re-run. Media stays under data/** (gitignored).
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRT_TIME = re.compile(r"^(\d{2}):(\d{2}):(\d{2})[,.]\d{3}\s*-->")


def srt_to_caption_txt(srt: Path, out: Path) -> int:
    """Convert an SRT file to the M:SS-per-line format align_youtube.py parses.

    Two-pass: parse cues, detect YouTube auto-sub ROLLING style (cues alternate
    [old line] / [old line + new line] — every text shows up twice), then emit:
    rolling -> last line of each cue, deduped; normal subs -> all lines joined.
    """
    cues: list[tuple[str, list[str]]] = []  # (M:SS, lines)
    start: str | None = None
    buf: list[str] = []
    for rawline in srt.read_text(encoding="utf-8", errors="replace").splitlines():
        m = SRT_TIME.match(rawline.strip())
        if m:
            if start is not None and buf:
                cues.append((start, buf))
            h, mnt, s = int(m.group(1)), int(m.group(2)), int(m.group(3))
            start = f"{h * 60 + mnt}:{s:02d}"
            buf = []
        elif rawline.strip() and not rawline.strip().isdigit():
            buf.append(rawline.strip())
    if start is not None and buf:
        cues.append((start, buf))

    # detect rolling: first line of a cue repeats the previous cue's last line
    rolls = sum(1 for (_, a), (_, b) in zip(cues, cues[1:]) if b and a and b[0] == a[-1])
    rolling = len(cues) > 10 and rolls / max(1, len(cues) - 1) > 0.3

    lines: list[str] = []
    prev = ""
    for ts, items in cues:
        text = items[-1] if rolling else " ".join(items)
        if text and text != prev:
            lines.append(f"{ts} {text}")
            prev = text
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def ep_done(outdir: Path, has_caption: bool) -> bool:
    need = [outdir / "report.md", outdir / "transcripts.csv"]
    if has_caption:
        need.append(outdir / "transcripts_yt.csv")
    return all(p.exists() for p in need)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--series", default="ve-nha-di-con")
    ap.add_argument("--episodes", default="2-10", help="e.g. 2-10 or 3")
    ap.add_argument("--python", default=str(ROOT / ".venv-vnser" / "Scripts" / "python.exe"))
    ap.add_argument("--skip-asr", action="store_true")
    args = ap.parse_args()

    lo, _, hi = args.episodes.partition("-")
    eps = range(int(lo), int(hi or lo) + 1)
    rawdir = ROOT / "data" / "vietnamese-ser" / "raw" / args.series
    epsdir = ROOT / "data" / "vietnamese-ser" / "episodes" / args.series
    # secrets from repo-root .env (gitignored) unless already set in the environment
    envfile = ROOT / ".env"
    if envfile.exists():
        for line in envfile.read_text(encoding="utf-8").splitlines():
            k, _, v = line.strip().partition("=")
            if k and v and k not in os.environ:
                os.environ[k] = v
    hf_token = os.environ.get("HF_TOKEN", "")
    env = {
        **os.environ,
        "PYTHONPATH": str(ROOT / "scripts" / "vietnamese-ser"),
        "PYTHONIOENCODING": "utf-8",
    }

    rows = []
    for n in eps:
        ep = f"ep{n:02d}"
        media = next(iter(sorted(rawdir.glob(f"{ep}.mp*"))), None) or next(
            iter(sorted(rawdir.glob(f"{ep}.m4a"))), None
        )
        if media is None:
            print(f"!! {ep}: không thấy media trong {rawdir} — bỏ qua")
            continue
        outdir = epsdir / ep
        outdir.mkdir(parents=True, exist_ok=True)

        srt = next(iter(sorted(rawdir.glob(f"{ep}*.srt"))), None)
        caption = outdir / "youtube_transcripts.txt"
        if srt and not caption.exists():
            print(f">> {ep}: SRT → caption ({srt_to_caption_txt(srt, caption)} block)")

        if ep_done(outdir, caption.exists()):
            print(f"== {ep}: đã xong — skip")
        else:
            cmd = [
                args.python,
                str(ROOT / "scripts" / "vietnamese-ser" / "pilot_extract.py"),
                "--input",
                str(media),
                "--outdir",
                str(outdir),
            ]
            if hf_token:
                cmd += ["--turn-split", "--hf-token", hf_token]
            if args.skip_asr:
                cmd += ["--skip-asr"]
            print(f">> {ep}: extract ({'turn-split' if hf_token else 'fallback VAD'})")
            subprocess.run(cmd, check=True, env=env)
            if caption.exists() and not args.skip_asr:
                # align failing must not kill the batch — extract (the expensive
                # part) is already done and cached; align can be re-run cheaply.
                try:
                    subprocess.run(
                        [
                            "uv",
                            "run",
                            "--with",
                            "rapidfuzz",
                            "python",
                            str(ROOT / "scripts" / "vietnamese-ser" / "align_youtube.py"),
                            "--pilot-dir",
                            str(outdir),
                        ],
                        check=True,
                        env=env,
                    )
                except subprocess.CalledProcessError as e:
                    print(f"!! {ep}: align lỗi (exit {e.returncode}) — extract vẫn OK, đi tiếp")

        segf = outdir / "segments.csv"
        if segf.exists():
            segs = list(csv.DictReader(segf.open(encoding="utf-8")))
            minutes = sum(float(s["dur"]) for s in segs) / 60
            single = sum(1 for s in segs if s.get("speaker", "").strip())
            rows.append([ep, len(segs), f"{minutes:.1f}", single])

    if rows:
        with (epsdir / "summary.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ep", "utterances", "minutes", "with_speaker"])
            w.writerows(rows)
        print(f"\n== summary: {epsdir / 'summary.csv'}")
        for r in rows:
            print("  ", r)


if __name__ == "__main__":
    main()
