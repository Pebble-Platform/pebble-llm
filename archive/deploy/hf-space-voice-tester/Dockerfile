# Hugging Face Space (Docker SDK). Serves the voice model tester on port 7860.
FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg libsndfile1 git && rm -rf /var/lib/apt/lists/*

# HF Spaces run as a non-root user (uid 1000); set up a writable home.
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    HF_HOME=/home/user/.cache/huggingface \
    MODELSCOPE_CACHE=/home/user/.cache/modelscope \
    VOICE_TESTER_ROOTS=/home/user/app/models \
    VOICE_TESTER_SAMPLES=/home/user/app/samples

WORKDIR /home/user/app

# CPU torch first (smaller than the default CUDA build), then the rest.
RUN pip install --no-cache-dir --user \
        torch==2.2.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cpu
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

COPY --chown=user . .

EXPOSE 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
