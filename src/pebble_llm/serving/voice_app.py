"""FastAPI app exposing /classify-voice (voice extension).

Verifies a Kaggle-trained voice affect model end-to-end: upload a wav, get the
emotion + distress (safety) head outputs. Run with:

    VOICE_ARTIFACT=artifacts/voice/artifact_wavlm-large \\
      .venv-voice/bin/uvicorn pebble_llm.serving.voice_app:app --port 8081

Then:  curl -F "file=@sample_val.wav" http://localhost:8081/classify-voice
"""

from __future__ import annotations

import os
from functools import lru_cache

from fastapi import FastAPI, File, HTTPException, UploadFile

from pebble_llm.serving.voice_inference import VoiceClassifier, load_waveform
from pebble_llm.serving.voice_schemas import VoiceClassifyResponse

app = FastAPI(title="Pebble Voice Affect Verifier", version="0.1.0")


@lru_cache(maxsize=1)
def get_classifier() -> VoiceClassifier:
    artifact = os.environ.get("VOICE_ARTIFACT", "artifacts/voice/artifact_wavlm-large")
    device = os.environ.get("VOICE_DEVICE", "cpu")
    return VoiceClassifier(artifact, device=device)


@app.get("/health")
def health() -> dict[str, str]:
    c = get_classifier()
    return {"status": "ok", "backbone": c.cfg["backbone"], "emotions": ",".join(c.emotions)}


@app.post("/classify-voice", response_model=VoiceClassifyResponse)
async def classify_voice(file: UploadFile = File(...)) -> VoiceClassifyResponse:
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="empty upload")
    clf = get_classifier()
    wav = load_waveform(raw, clf.sr, clf.max_samples)
    return clf.classify(wav)
