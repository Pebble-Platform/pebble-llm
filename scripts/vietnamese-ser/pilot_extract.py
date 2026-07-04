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
          --turn-split (cut at speaker-turn boundaries -> single-speaker utterances;
                        needs --hf-token; caches raw turns to diar_turns.csv)
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
MIN_UTT = 2.0        # s — drop shorter (whole single-speaker region / no-turn-split mode)
MIN_UTT_TURN = 1.5   # s — drop shorter for pieces carved from a multi-speaker region
MAX_UTT = 10.0       # s — split longer
MERGE_GAP = 0.4      # s — merge VAD regions separated by less than this
PREMERGE_GAP = 0.6   # s — merge adjacent same-speaker turns closer than this (de-fragment)
PAD = 0.10           # s — padding added to each side of a cut


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


def _premerge_turns(turns: list[tuple[float, float, str]]
                    ) -> list[tuple[float, float, str]]:
    """T1: merge adjacent same-speaker turns < PREMERGE_GAP apart (de-fragment pyannote)."""
    by_spk: dict[str, list[list[float]]] = {}
    for a, b, spk in turns:
        by_spk.setdefault(spk, []).append([a, b])
    out: list[tuple[float, float, str]] = []
    for spk, lst in by_spk.items():
        lst.sort()
        cur = list(lst[0])
        for a, b in lst[1:]:
            if a - cur[1] < PREMERGE_GAP:
                cur[1] = max(cur[1], b)
            else:
                out.append((cur[0], cur[1], spk))
                cur = [a, b]
        out.append((cur[0], cur[1], spk))
    return out


def turn_split(merged: list[list[float]], turns: list[tuple[float, float, str]]
               ) -> list[tuple[float, float, str, float]]:
    """Split merged VAD regions at speaker-turn boundaries (before the 2-10 s split).

    Hybrid design (v2): single-speaker regions are kept intact (never shrunk); only
    genuinely multi-speaker regions are cut at turn edges. Each returned piece is tagged
    with the min-duration threshold that applies to it — MIN_UTT for a whole single-speaker
    region, MIN_UTT_TURN for a piece carved out of a multi-speaker region.

      T1  pre-merge adjacent same-speaker turns (de-fragment pyannote) — see _premerge_turns.
      T2  a region whose substantially-overlapping (> OVL_MIN) turns are all one speaker
          (or none) is ONE intact piece carrying that speaker (or ""); no cut inside.
      T3  in a multi-speaker region, cut at turn edges; each "" gap (diarization miss) is
          folded into a neighbour (X,"",X and region-edge -> that speaker; X,"",Y -> split
          at midpoint). A >=2-voice overlap is DROPPED and acts as a hard barrier that ""
          is never folded across.
    """
    DROP = "\x00drop"
    OVL_MIN = 0.05      # s — ignore mere edge-touch when deciding a region's speakers
    mturns = _premerge_turns(turns)                                          # T1
    out: list[list] = []
    for rstart, rend in merged:
        region_spk = {spk for a, b, spk in mturns
                      if min(b, rend) - max(a, rstart) > OVL_MIN}
        if len(region_spk) <= 1:                                             # T2
            out.append([rstart, rend, next(iter(region_spk), ""), MIN_UTT])
            continue
        # T3 — carve the multi-speaker region at turn edges
        bounds = {rstart, rend}
        for a, b, _ in mturns:
            if b > rstart and a < rend:
                if rstart < a < rend:
                    bounds.add(a)
                if rstart < b < rend:
                    bounds.add(b)
        pts = sorted(bounds)
        seq: list[list] = []
        for a, b in zip(pts, pts[1:]):
            mid = (a + b) / 2
            spks = [spk for ts, te, spk in mturns if ts <= mid < te]
            seq.append([a, b, DROP if len(spks) >= 2 else (spks[0] if spks else "")])
        resolved: list[list] = []                                           # fold "" gaps
        for i, (a, b, lab) in enumerate(seq):
            if lab != "":
                resolved.append([a, b, lab])
                continue
            left = seq[i - 1][2] if i > 0 else None
            right = seq[i + 1][2] if i < len(seq) - 1 else None
            lspk = left if left not in (None, DROP) else None
            rspk = right if right not in (None, DROP) else None
            if lspk and rspk and lspk != rspk:
                mid = (a + b) / 2
                resolved.append([a, mid, lspk])
                resolved.append([mid, b, rspk])
            elif lspk:
                resolved.append([a, b, lspk])
            elif rspk:
                resolved.append([a, b, rspk])
            else:
                resolved.append([a, b, ""])
        for a, b, lab in resolved:
            if lab != DROP and out and out[-1][2] == lab and out[-1][3] == MIN_UTT_TURN \
                    and a - out[-1][1] < MERGE_GAP:
                out[-1][1] = b
            else:
                out.append([a, b, lab, MIN_UTT_TURN])
    return [(a, b, spk, md) for a, b, spk, md in out if spk != DROP]


def stage_vad(voc16: Path, outdir: Path,
              turns: list[tuple[float, float, str]] | None = None) -> list[dict]:
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

    # turn-split BEFORE the 2-10 s split; fallback: whole region, empty speaker
    pieces = turn_split(merged, turns) if turns is not None else [
        (s, e, "", MIN_UTT) for s, e in merged]

    # split long pieces into <= MAX_UTT chunks, drop < per-piece min (MIN_UTT / MIN_UTT_TURN)
    segs: list[dict] = []
    for start, end, spk, min_dur in pieces:
        dur = end - start
        n = max(1, int(dur // MAX_UTT) + (1 if dur % MAX_UTT > 0 else 0))
        step = dur / n
        for i in range(n):
            s, e = start + i * step, start + (i + 1) * step
            if e - s >= min_dur:
                segs.append({"id": f"seg{len(segs):05d}", "start": round(s, 2),
                             "end": round(e, 2), "speaker": spk})
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
        w.writerow(["id", "start", "end", "dur", "speaker", "clip"])
        for s in segs:
            w.writerow([s["id"], s["start"], s["end"], round(s["end"] - s["start"], 2),
                        s.get("speaker", ""), f"clips/{s['id']}.wav"])
    return clip_dir


def stage_asr(clip_dir: Path, segs: list[dict], outdir: Path, model_id: str) -> Path:
    out = outdir / "transcripts.csv"
    if out.exists():
        return out
    import soundfile as sf
    import torch
    from transformers import pipeline

    # transformers' ASR preprocess does an unconditional `import torchcodec` when the
    # package is merely installed; its DLLs don't load on this box, which crashes ASR.
    # We only ever pass raw arrays, so disable the branch when torchcodec can't load.
    try:
        import torchcodec  # noqa: F401
    except Exception:
        import transformers.pipelines.automatic_speech_recognition as _asr_mod
        _asr_mod.is_torchcodec_available = lambda: False

    device = 0 if torch.cuda.is_available() else -1
    asr = pipeline("automatic-speech-recognition", model=model_id, device=device)
    rows = []
    for i, s in enumerate(segs):
        wav, sr = sf.read(str(clip_dir / f"{s['id']}.wav"), dtype="float32")
        text = asr({"raw": wav, "sampling_rate": sr})["text"].strip()
        rows.append([s["id"], s["start"], s["end"], text])
        if (i + 1) % 25 == 0:
            print(f"  asr {i + 1}/{len(segs)}")
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "start", "end", "text"])
        w.writerows(rows)
    return out


def load_diar_turns(voc16: Path, outdir: Path, hf_token: str) -> list[tuple[float, float, str]]:
    """Run pyannote once and cache raw turns to diar_turns.csv; return [(start,end,speaker)].

    Cached: if diar_turns.csv exists, read it back (never re-run pyannote — ~15-30 min CPU).
    """
    turns_csv = outdir / "diar_turns.csv"
    if turns_csv.exists():
        rows = list(csv.DictReader(turns_csv.open(encoding="utf-8")))
        return [(float(r["start"]), float(r["end"]), r["speaker"]) for r in rows]
    import soundfile as sf
    import torch
    from pyannote.audio import Pipeline

    pipe = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=hf_token)
    # in-memory waveform: avoids pyannote's file decoders (torchcodec DLL broken on this box)
    wav, sr = sf.read(str(voc16), dtype="float32")
    diar = pipe({"waveform": torch.from_numpy(wav).unsqueeze(0), "sample_rate": sr})
    ann = getattr(diar, "speaker_diarization", diar)  # pyannote 4.x wraps the Annotation
    turns = [(t.start, t.end, spk) for t, _, spk in ann.itertracks(yield_label=True)]
    with turns_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["start", "end", "speaker"])
        for a, b, spk in turns:
            w.writerow([round(a, 3), round(b, 3), spk])
    return turns


def write_speakers_csv(turns: list[tuple[float, float, str]], segs: list[dict],
                       outdir: Path) -> None:
    with (outdir / "speakers.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "n_speakers", "speakers"])
        for s in segs:
            spks = {spk for a, b, spk in turns if a < s["end"] and b > s["start"]}
            w.writerow([s["id"], len(spks), "|".join(sorted(spks))])


def stage_diar(voc16: Path, segs: list[dict], outdir: Path, hf_token: str) -> None:
    if (outdir / "speakers.csv").exists():
        return
    write_speakers_csv(load_diar_turns(voc16, outdir, hf_token), segs, outdir)


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
    ap.add_argument("--turn-split", action="store_true",
                    help="cut utterances at speaker-turn boundaries (single-speaker by "
                         "construction); requires --hf-token")
    ap.add_argument("--skip-asr", action="store_true")
    args = ap.parse_args()
    if args.turn_split and not args.hf_token:
        ap.error("--turn-split requires --hf-token (diarization drives the turn boundaries)")

    outdir = args.outdir or Path("data/vietnamese-ser/pilot") / args.input.stem
    outdir.mkdir(parents=True, exist_ok=True)

    full = stage_audio(args.input, outdir)
    voc = stage_demucs(full, outdir)
    # turn-split: diarize BEFORE building segments so cuts land on speaker boundaries
    turns = load_diar_turns(voc, outdir, args.hf_token) if args.turn_split else None
    segs = stage_vad(voc, outdir, turns)
    src = voc if args.cut_source == "vocals" else full
    clips = stage_cut(src, segs, outdir)
    if args.hf_token:
        stage_diar(voc, segs, outdir, args.hf_token)
    if not args.skip_asr:
        stage_asr(clips, segs, outdir, args.whisper)
    write_report(outdir, args.input, segs, full)


if __name__ == "__main__":
    main()
