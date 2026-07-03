"""vnser-extract — batch port of pilot_extract.py to Kaggle P100 GPU.

Runs the pilot dialogue-extraction pipeline over EVERY audio/video file in a
Kaggle dataset, one folder of outputs per episode, plus a run-wide SUMMARY.md.
Self-contained (repo pattern: one file per kernel — no repo imports); the stage
functions are copied from scripts/vietnamese-ser/pilot_extract.py.

Per-episode pipeline (each stage cached — re-run skips finished stages):
  ffmpeg -> demucs (vocals) -> silero VAD -> [turn-split] -> cut 2-10s -> PhoWhisper ASR
  When an HF_TOKEN secret exists, pyannote/speaker-diarization-3.1 runs BEFORE the cut and
  utterances are split at speaker-turn boundaries (single-speaker by construction); the raw
  turns are cached to diar_turns.csv. No token -> plain VAD cuts, empty speaker column.
Output per episode -> /kaggle/working/<ep>/:
  segments.csv (with speaker col) · diar_turns.csv · transcripts.csv · speakers.csv ·
  clips/*.wav · report.md

--- Kaggle P100 gotchas (do not "fix" these) -----------------------------------
* P100 is sm_60. The default Kaggle image torch does NOT run on it, so the first
  thing the kernel does is pin torch==2.5.1+cu121 (see _pip_install).
* pyannote.audio is pinned to 3.x here (torch 2.5.1 does not run pyannote 4.x).
  pyannote 3.x uses `use_auth_token=` — NOT the 4.x `token=` API used locally.
  The 3.x pipeline call returns an Annotation directly (no .speaker_diarization
  wrapper). torchaudio 2.5.1 still ships an internal I/O backend, so on Kaggle
  the sitecustomize soundfile shim used locally is NOT needed.

--- Smoke mode (local CPU test before pushing) ---------------------------------
  VNSER_SMOKE=1  -> process only the first 60s of the first file, skip diarization,
                    skip pip install (deps already in .venv-vnser).
  Run locally with the torchaudio shim on PYTHONPATH, e.g.:
    PYTHONIOENCODING=utf-8 VNSER_SMOKE=1 PYTHONPATH=scripts/vietnamese-ser \
      VNSER_INPUT=data/vietnamese-ser/raw VNSER_OUTPUT=data/vietnamese-ser/smoke_out \
      .venv-vnser/Scripts/python kaggle/vietnamese-ser/vnser-extract/vnser-extract.py

Media + outputs live under data/** (gitignored) — never commit them.
"""

from __future__ import annotations

import csv
import json
import os
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
SMOKE_SECONDS = 60

SMOKE = os.environ.get("VNSER_SMOKE") == "1"
ON_KAGGLE = os.path.exists("/kaggle/input")
MEDIA_EXTS = {".mp4", ".mkv", ".mp3", ".wav", ".m4a", ".avi", ".mov", ".flac", ".webm", ".aac"}


def sh(cmd: list[str]) -> None:
    print(">>", " ".join(cmd))
    subprocess.run(cmd, check=True)


def _pip_install() -> None:
    # P100 = sm_60: pin torch 2.5.1+cu121 (default image torch won't run on P100).
    sh([sys.executable, "-m", "pip", "install", "-q",
        "torch==2.5.1", "torchaudio==2.5.1",
        "--index-url", "https://download.pytorch.org/whl/cu121"])
    # pyannote 3.x (torch 2.5.1 does not run pyannote 4.x).
    sh([sys.executable, "-m", "pip", "install", "-q",
        "demucs", "silero-vad", "transformers", "soundfile", "pyannote.audio==3.*"])


def get_hf_token() -> str | None:
    tok = os.environ.get("HF_TOKEN")
    if tok:
        return tok
    try:
        from kaggle_secrets import UserSecretsClient
        return UserSecretsClient().get_secret("HF_TOKEN")
    except Exception as e:  # noqa: BLE001 — any failure => run without diarization
        print(f"[warn] no HF_TOKEN secret ({e}); diarization sẽ bị bỏ qua")
        return None


def stage_audio(inp: Path, outdir: Path) -> Path:
    wav = outdir / "audio_full.wav"
    if not wav.exists():
        cmd = ["ffmpeg", "-y", "-i", str(inp), "-vn", "-ac", "1", "-ar", str(SR)]
        if SMOKE:
            cmd += ["-t", str(SMOKE_SECONDS)]  # only first 60s in smoke mode
        cmd += [str(wav)]
        sh(cmd)
    return wav


def stage_demucs(wav: Path, outdir: Path) -> Path:
    voc16 = outdir / "vocals_16k.wav"
    if voc16.exists():
        return voc16
    # demucs auto-uses CUDA when available; writes <out>/htdemucs/<stem>/vocals.wav
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

    merged: list[list[float]] = []
    for r in regions:
        if merged and r["start"] - merged[-1][1] < MERGE_GAP:
            merged[-1][1] = r["end"]
        else:
            merged.append([r["start"], r["end"]])

    # turn-split BEFORE the 2-10 s split; fallback: whole region, empty speaker
    pieces = turn_split(merged, turns) if turns is not None else [
        (s, e, "", MIN_UTT) for s, e in merged]

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
    # We only ever pass raw arrays (never a torchcodec decoder), so the branch is dead
    # weight — disable it when torchcodec can't load. No-op on Kaggle where it works.
    try:
        import torchcodec  # noqa: F401
    except Exception:
        import transformers.pipelines.automatic_speech_recognition as _asr_mod
        _asr_mod.is_torchcodec_available = lambda: False

    device = 0 if torch.cuda.is_available() else -1
    asr = pipeline("automatic-speech-recognition", model=model_id, device=device)
    rows = []
    for i, s in enumerate(segs):
        # decode the clip with soundfile and hand the pipeline a raw array — avoids
        # transformers' file-path branch (which imports torchcodec; its DLLs are
        # broken on this Windows box). Clips are already 16 kHz mono.
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
    """Run pyannote 3.x once and cache raw turns to diar_turns.csv; return [(start,end,speaker)].

    Cached: if diar_turns.csv exists, read it back (never re-run pyannote).
    """
    turns_csv = outdir / "diar_turns.csv"
    if turns_csv.exists():
        rows = list(csv.DictReader(turns_csv.open(encoding="utf-8")))
        return [(float(r["start"]), float(r["end"]), r["speaker"]) for r in rows]
    import soundfile as sf
    import torch
    from pyannote.audio import Pipeline

    # pyannote 3.x on Kaggle: use_auth_token= (NOT the 4.x token= used locally).
    pipe = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=hf_token)
    if torch.cuda.is_available():
        pipe.to(torch.device("cuda"))
    # in-memory waveform: robust regardless of the active audio backend
    wav, sr = sf.read(str(voc16), dtype="float32")
    diar = pipe({"waveform": torch.from_numpy(wav).unsqueeze(0), "sample_rate": sr})
    ann = getattr(diar, "speaker_diarization", diar)  # 3.x returns Annotation directly
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


def write_report(outdir: Path, inp: Path, segs: list[dict], full_wav: Path) -> dict:
    import wave

    with wave.open(str(full_wav), "rb") as w:
        total = w.getnframes() / w.getframerate()
    speech = sum(s["end"] - s["start"] for s in segs)
    durs = sorted(s["end"] - s["start"] for s in segs)
    median = durs[len(durs) // 2] if durs else 0.0
    single = None
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
        f"- Số utterance: **{len(segs)}** · độ dài median {median:.1f}s\n"
        f"{spk_line}"
        f"- Files: `segments.csv` · `clips/` · `transcripts.csv` (nếu chạy ASR)\n\n"
        f"Ngưỡng GO đề xuất (tracking doc M3): yield ≥ ~25%/tập.\n"
    )
    (outdir / "report.md").write_text(report, encoding="utf-8")
    print(report)
    return {"ep": inp.name, "total_min": total / 60, "speech_min": speech / 60,
            "n_utt": len(segs), "single": single}


def find_episodes(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.suffix.lower() in MEDIA_EXTS)


def process(inp: Path, out_root: Path, hf_token: str | None, whisper: str) -> dict:
    outdir = out_root / inp.stem
    outdir.mkdir(parents=True, exist_ok=True)
    full = stage_audio(inp, outdir)
    voc = stage_demucs(full, outdir)
    # turn-split default ON when a token exists (scale needs single-speaker from the start);
    # no token -> turns=None -> fallback to plain VAD cuts (empty speaker column).
    turns = load_diar_turns(voc, outdir, hf_token) if (hf_token and not SMOKE) else None
    segs = stage_vad(voc, outdir, turns)
    clips = stage_cut(voc, segs, outdir)
    if hf_token and not SMOKE:
        stage_diar(voc, segs, outdir, hf_token)
    stage_asr(clips, segs, outdir, whisper)
    return write_report(outdir, inp, segs, full)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # Vietnamese report -> avoid cp1252 crash on Windows
    if ON_KAGGLE and not SMOKE:
        _pip_install()

    input_root = Path(os.environ.get("VNSER_INPUT", "/kaggle/input/vnser-episodes"))
    out_root = Path(os.environ.get("VNSER_OUTPUT", "/kaggle/working"))
    whisper = os.environ.get("VNSER_WHISPER", "vinai/PhoWhisper-base")
    out_root.mkdir(parents=True, exist_ok=True)

    hf_token = None if SMOKE else get_hf_token()
    eps = find_episodes(input_root)
    if not eps:
        print(f"[error] no media files under {input_root}")
        sys.exit(1)
    if SMOKE:
        eps = eps[:1]
        print(f"[smoke] chỉ xử lý 60s đầu của: {eps[0].name} (bỏ diarization)")
    print(f"Xử lý {len(eps)} tập từ {input_root}")

    summaries = [process(ep, out_root, hf_token, whisper) for ep in eps]

    lines = ["# vnser-extract — batch summary", "",
             "| ep | phút | thoại(phút) | yield | utt | đơn-nói |",
             "|---|---:|---:|---:|---:|---:|"]
    tot_utt = tot_speech = 0.0
    for s in summaries:
        y = s["speech_min"] / s["total_min"] if s["total_min"] else 0.0
        single = f"{s['single']}/{s['n_utt']}" if s["single"] is not None else "—"
        lines.append(f"| {s['ep']} | {s['total_min']:.1f} | {s['speech_min']:.1f} | "
                     f"{y:.0%} | {s['n_utt']} | {single} |")
        tot_utt += s["n_utt"]
        tot_speech += s["speech_min"]
    lines += ["", f"**Tổng: {len(summaries)} tập · {tot_speech / 60:.1f}h thoại sạch · "
              f"{int(tot_utt)} utterance.**"]
    summary = "\n".join(lines) + "\n"
    (out_root / "SUMMARY.md").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
