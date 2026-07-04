# Serving image for the /classify endpoint (strategy §6.1 Step 4, Track A = GPU FP16).
# For GPU (NVIDIA L4) builds, swap the base for an nvidia/cuda runtime image and
# install torch with CUDA wheels. This baseline image targets local/CPU smoke tests.

FROM python:3.11-slim

# uv for fast, reproducible installs
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install deps first for layer caching
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --extra serving --frozen || uv sync --no-dev --extra serving

# App code
COPY src ./src
COPY configs ./configs

ENV SERVING_CONFIG=configs/serving/default.yaml \
    PYTHONUNBUFFERED=1

EXPOSE 8080

# min-instances=1 at the platform level eliminates cold starts (§6.1 Step 4)
CMD ["uv", "run", "uvicorn", "pebble_llm.serving.app:app", "--host", "0.0.0.0", "--port", "8080"]
