"""Pilot: extract clean Vietnamese dialogue utterances from one TV-series episode.

Pipeline (each stage cached — re-running skips finished stages):
  1. ffmpeg   : video/audio -> mono 16 kHz wav
  2. demucs   : separate music/SFX -> vocals stem
  3. silero   : VAD on vocals -> merged speech regions -> 2-10 s utterances
  4. cut      : export each utterance as wav + segments.csv
  5. asr      : PhoWhisper transcript per utterance -> transcripts.csv
  (+ optional: pyannote diarization to count speakers per utterance, --hf-token)
Ends with report.md: yield stats (the pilot's deliverable).

Usage (from repo root, inside .venv-vnser — see README.md):
  python scripts/vietnamese-ser/pilot_extract.py --input data/vietnamese-ser/raw/ep01.mp4
Optional: --outdir ... --whisper vinai/PhoWhisper-base --cut-source vocals|original
          --hf-token hf_xxx (enables pyannote/speaker-diarization-3.1, gated)
          --skip-asr (yield numbers only, no transcripts)

Media files and all outputs live under data/** (gitignored) — never commit them.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

SR = 16000
MIN_UTT = 2.0    # s — drop shorter
MAX_UTT = 10.0   # s — split longer
MERGE_GAP = 0.4  # s — merge VAD regions separated by less than this
PAD = 0.10       # s — padding added to each side of a cut


def sh(cmd: list[str]) -> None:
    print(">>", " ".join(cmd))
    subprocess.run(cmd, check=True)


def stage_audio(inp: Path, outdir: Path) -> Path:
    wav = outdir / "audio_full.wav"
    if not wav.exists():
        sh(["ffmpeg", "-y", "-i", str(inp), "-vn", "-ac", "1", "-ar", str(SR), str(wav)])
    return wav


def stage_demucs(wav: Path, outdir: Path) -> Path:
    voc16 = outdir / "vocals_16k.wav"
    if voc16.exists():
        return voc16
    # demucs writes <out>/htdemucs/<stem>/vocals.wav (44.1 kHz stereo)
    sh([sys.executable, "-m", "demucs", "--two-stems", "vocals", "-n", "htdemucs",
        "-o", str(outdir / "demucs"), str(wav)])
    raw_voc = outdir / "demucs" / "htdemucs" / wav.stem / "vocals.wav"
    sh(["ffmpeg", "-y", "-i", str(raw_voc), "-ac", "1", "-ar", str(SR), str(voc16)])
    return voc16


def stage_vad(voc16: Path, outdir: Path) -> list[dict]:
    segf = outdir / "segments.json"
    if segf.exists():
        return json.loads(segf.read_text(encoding="utf-8"))
    from silero_vad import get_speech_timestamps, load_silero_vad, read_audio

    model = load_silero_vad()
    audio = read_audio(str(voc16), sampling_rate=SR)
    regions = get_speech_timestamps(audio, model, sampling_rate=SR, return_seconds=True)

    # merge close regions
    merged: list[list[float]] = []
    for r in regions:
        if merged and r["start"] - merged[-1][1] < MERGE_GAP:
            merged[-1][1] = r["end"]
        else:
            merged.append([r["start"], r["end"]])

    # split long regions into <= MAX_UTT chunks, drop < MIN_UTT
    segs: list[dict] = []
    for start, end in merged:
        dur = end - start
        n = max(1, int(dur // MAX_UTT) + (1 if dur % MAX_UTT > 0 else 0))
        step = dur / n
        for i in range(n):
            s, e = start + i * step, start + (i + 1) * step
            if e - s >= MIN_UTT:
                segs.append({"id": f"seg{len(segs):05d}", "start": round(s, 2), "end": round(e, 2)})
    segf.write_text(json.dumps(segs, indent=1), encoding="utf-8")
    return segs


def stage_cut(src_wav: Path, segs: list[dict], outdir: Path) -> Path:
    clip_dir = outdir / "clips"
    clip_dir.mkdir(exist_ok=True)
    done_flag = outdir / ".cut_done"
    if not done_flag.exists():
        for s in segs:
            clip = clip_dir / f"{s['id']}.wav"
            if clip.exists():
                continue
            start = max(0.0, s["start"] - PAD)
            dur = (s["end"] + PAD) - start
            sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.2f}", "-t", f"{dur:.2f}",
                "-i", str(src_wav), "-ac", "1", "-ar", str(SR), str(clip)])
        done_flag.touch()
    with (outdir / "segments.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "start", "end", "dur", "clip"])
        for s in segs:
            w.writerow([s["id"], s["start"], s["end"], round(s["end"] - s["start"], 2),
                        f"clips/{s['id']}.wav"])
    return clip_dir


def stage_asr(clip_dir: Path, segs: list[dict], outdir: Path, model_id: str) -> Path:
    out = outdir / "transcripts.csv"
    if out.exists():
        return out
    import torch
    from transformers import pipeline

    device = 0 if torch.cuda.is_available() else -1
    asr = pipeline("automatic-speech-recognition", model=model_id, device=device)
    rows = []
    for i, s in enumerate(segs):
        text = asr(str(clip_dir / f"{s['id']}.wav"))["text"].strip()
        rows.append([s["id"], s["start"], s["end"], text])
        if (i + 1) % 25 == 0:
            print(f"  asr {i + 1}/{len(segs)}")
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "start", "end", "text"])
        w.writerows(rows)
    return out


def stage_diar(voc16: Path, segs: list[dict], outdir: Path, hf_token: str) -> None:
    out = outdir / "speakers.csv"
    if out.exists():
        return
    import soundfile as sf
    import torch
    from pyannote.audio import Pipeline

    pipe = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=hf_token)
    # in-memory waveform: avoids pyannote's file decoders (torchcodec DLL broken on this box)
    wav, sr = sf.read(str(voc16), dtype="float32")
    diar = pipe({"waveform": torch.from_numpy(wav).unsqueeze(0), "sample_rate": sr})
    ann = getattr(diar, "speaker_diarization", diar)  # pyannote 4.x wraps the Annotation
    turns = [(t.start, t.end, spk) for t, _, spk in ann.itertracks(yield_label=True)]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "n_speakers", "speakers"])
        for s in segs:
            spks = {spk for a, b, spk in turns if a < s["end"] and b > s["start"]}
            w.writerow([s["id"], len(spks), "|".join(sorted(spks))])


def write_report(outdir: Path, inp: Path, segs: list[dict], full_wav: Path) -> None:
    import wave

    with wave.open(str(full_wav), "rb") as w:
        total = w.getnframes() / w.getframerate()
    speech = sum(s["end"] - s["start"] for s in segs)
    durs = sorted(s["end"] - s["start"] for s in segs)
    spk_line = ""
    spk_csv = outdir / "speakers.csv"
    if spk_csv.exists():
        rows = list(csv.DictReader(spk_csv.open(encoding="utf-8")))
        single = sum(1 for r in rows if r["n_speakers"] == "1")
        spk_line = f"- Utterance đơn-người-nói (pyannote): **{single}/{len(rows)}** ({single / len(rows):.0%})\n"
    report = (
        f"# Pilot yield report — {inp.name}\n\n"
        f"- Tổng thời lượng tập: **{total / 60:.1f} phút**\n"
        f"- Thoại sạch sau Demucs+VAD (utterance {MIN_UTT:.0f}–{MAX_UTT:.0f}s): "
        f"**{speech / 60:.1f} phút** → **yield {speech / total:.0%}**\n"
        f"- Số utterance: **{len(segs)}** · độ dài median {durs[len(durs) // 2]:.1f}s\n"
        f"{spk_line}"
        f"- Files: `segments.csv` · `clips/` · `transcripts.csv` (nếu chạy ASR)\n\n"
        f"Ngưỡng GO đề xuất (tracking doc M3): yield ≥ ~25%/tập.\n"
    )
    (outdir / "report.md").write_text(report, encoding="utf-8")
    print(report)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # Vietnamese in report -> avoid cp1252 crash on Windows
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--outdir", type=Path, default=None)
    ap.add_argument("--whisper", default="vinai/PhoWhisper-base")
    ap.add_argument("--cut-source", choices=["vocals", "original"], default="vocals")
    ap.add_argument("--hf-token", default=None, help="enables pyannote diarization (gated model)")
    ap.add_argument("--skip-asr", action="store_true")
    args = ap.parse_args()

    outdir = args.outdir or Path("data/vietnamese-ser/pilot") / args.input.stem
    outdir.mkdir(parents=True, exist_ok=True)

    full = stage_audio(args.input, outdir)
    voc = stage_demucs(full, outdir)
    segs = stage_vad(voc, outdir)
    src = voc if args.cut_source == "vocals" else full
    clips = stage_cut(src, segs, outdir)
    if args.hf_token:
        stage_diar(voc, segs, outdir, args.hf_token)
    if not args.skip_asr:
        stage_asr(clips, segs, outdir, args.whisper)
    write_report(outdir, args.input, segs, full)


if __name__ == "__main__":
    main()
