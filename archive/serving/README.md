# Serving

Lightweight FastAPI container exposing `POST /classify` (message + context → typed
scores). The Pebble backend calls it **before** the Gemini generation call; the
Decision Engine consumes the output to route (strategy §6.1 Step 4).

## Two tracks — decide via the Week-8 spike (§4, OQ6)

| Track | What | Latency target | Status |
|---|---|---|---|
| **A (baseline)** | GPU FP16, FlashAttention, on Cloud Run (NVIDIA L4) or a Vertex endpoint | ~20–50 ms | Assumed default |
| **B (spike)** | INT8 ONNX on CPU Cloud Run | ~50–150 ms | **Unproven** for NeoBERT — timebox; see `scripts/export_onnx.py` |

**Fallback ladder if serving is intractable:** NeoBERT-GPU → ModernBERT (proven
CPU/ONNX) → Gemini Flash-Lite backup.

## Local run

```bash
uv run uvicorn pebble_llm.serving.app:app --reload --port 8080
# or
make serve
```

## Build the image

```bash
make docker-build     # docker build -f serving/Dockerfile -t pebble-classifier:local .
```

Set `min-instances=1` at the platform level to eliminate cold starts on this
latency-sensitive path.
