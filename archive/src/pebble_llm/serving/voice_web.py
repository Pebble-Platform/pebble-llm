"""Web demo for the voice affect model (voice extension).

A thin FastAPI app on top of VoiceClassifier: serves a single-page UI where you
pick a pre-loaded RAVDESS clip (or upload your own wav), run the WavLM-Large
emotion + distress heads, and see the response rendered. Reuses the exact
inference path of voice_app.py — this only adds sample browsing + a static UI.

    VOICE_ARTIFACT=kaggle/pebble-voice-backbone/out/artifact_wavlm-large \\
    VOICE_SAMPLES=data/external/voice_samples \\
      PYTHONPATH=src .venv-voice/Scripts/uvicorn pebble_llm.serving.voice_web:app --port 8080
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from pebble_llm.serving.voice_inference import VoiceClassifier, load_waveform
from pebble_llm.serving.voice_schemas import VoiceClassifyResponse

# RAVDESS filename: 03-01-EE-II-SS-RR-AA.wav ; EE is the 1-indexed emotion code.
RAVDESS_EMOTIONS = [
    "neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised",
]
STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Pebble Voice Affect — Demo", version="0.1.0")


@lru_cache(maxsize=1)
def get_classifier() -> VoiceClassifier:
    artifact = os.environ.get("VOICE_ARTIFACT", "kaggle/pebble-voice-backbone/out/artifact_wavlm-large")
    device = os.environ.get("VOICE_DEVICE", "cpu")
    return VoiceClassifier(artifact, device=device)


def samples_dir() -> Path:
    return Path(os.environ.get("VOICE_SAMPLES", "data/external/voice_samples"))


def true_label(name: str) -> str | None:
    """Parse the RAVDESS-encoded emotion from the filename, if present."""
    parts = Path(name).stem.split("-")
    if len(parts) >= 3 and parts[2].isdigit():
        idx = int(parts[2]) - 1
        if 0 <= idx < len(RAVDESS_EMOTIONS):
            return RAVDESS_EMOTIONS[idx]
    return None


def _safe_sample(name: str) -> Path:
    path = (samples_dir() / name).resolve()
    if path.parent != samples_dir().resolve() or not path.is_file():
        raise HTTPException(status_code=404, detail="sample not found")
    return path


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict[str, object]:
    c = get_classifier()
    return {
        "status": "ok",
        "backbone": c.cfg["backbone"],
        "emotions": c.emotions,
        "threshold": c.threshold,
        "n_samples": len(list(samples_dir().glob("*.wav"))) if samples_dir().exists() else 0,
    }


@app.get("/api/samples")
def list_samples() -> list[dict[str, object]]:
    d = samples_dir()
    if not d.exists():
        return []
    out = []
    for wav in sorted(d.glob("*.wav")):
        out.append({
            "name": wav.name,
            "trueLabel": true_label(wav.name),
            "url": f"/api/samples/{wav.name}",
        })
    return out


@app.get("/api/samples/{name}")
def get_sample(name: str) -> FileResponse:
    return FileResponse(_safe_sample(name), media_type="audio/wav")


@app.post("/api/classify-sample", response_model=VoiceClassifyResponse)
def classify_sample(name: str) -> VoiceClassifyResponse:
    raw = _safe_sample(name).read_bytes()
    clf = get_classifier()
    return clf.classify(load_waveform(raw, clf.sr, clf.max_samples))


@app.post("/api/classify", response_model=VoiceClassifyResponse)
async def classify_upload(file: UploadFile = File(...)) -> VoiceClassifyResponse:
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="empty upload")
    clf = get_classifier()
    return clf.classify(load_waveform(raw, clf.sr, clf.max_samples))


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
