"""FastAPI app exposing /classify (strategy §6.1 Step 4).

The Pebble backend calls this BEFORE the Gemini generation call; the Decision
Engine consumes the structured scores to route. Run locally with:

    uv run uvicorn pebble_llm.serving.app:app --reload --port 8080
"""

from __future__ import annotations

import os
from functools import lru_cache

from fastapi import FastAPI

from pebble_llm.config import Config, load_config
from pebble_llm.serving.inference import Classifier
from pebble_llm.serving.schemas import ClassifyRequest, ClassifyResponse

app = FastAPI(title="Pebble Emotion Classifier", version="0.1.0")


@lru_cache(maxsize=1)
def get_classifier() -> Classifier:
    cfg_path = os.environ.get("SERVING_CONFIG", "configs/serving/default.yaml")
    cfg: Config = load_config(cfg_path)
    return Classifier(cfg)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest) -> ClassifyResponse:
    return get_classifier().classify(req)
