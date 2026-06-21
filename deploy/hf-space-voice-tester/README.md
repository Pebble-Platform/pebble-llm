---
title: Pebble Voice Model Tester
emoji: 🎙️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Pebble Voice Model Tester (HF Space)

Cloud serving of the emotion2vec / WavLM reproduction heads so a **local client can call them
over HTTP** — and so **emotion2vec runs** (its `funasr` dep installs on this Linux image, unlike
the Intel-mac local env). Open the Space URL for the interactive UI, or POST to the API.

## Endpoints
- `GET  /`                       — interactive web UI (pick model + sample, run, see result)
- `GET  /api/models`             — discovered models (`models/artifact_*/`)
- `GET  /api/samples`            — bundled RAVDESS samples (truth from filename)
- `POST /api/infer`              — `model_id` + (`sample_id` | `file`) → prediction JSON

## Call it from local
```bash
# UI:    open https://<user>-pebble-voice-tester.hf.space
# API:
curl -s -X POST https://<user>-pebble-voice-tester.hf.space/api/infer \
  -F model_id=emotion2vec--superb-frame \
  -F file=@my.wav
# or the helper:
.venv-voice/bin/python scripts/voice_remote_infer.py \
  https://<user>-pebble-voice-tester.hf.space emotion2vec--superb-frame my.wav
```

## Deploy / update
This folder IS the Space repo. From repo root:
```bash
pip install huggingface_hub
huggingface-cli login                       # needs a write token
huggingface-cli repo create pebble-voice-tester --type space --space_sdk docker
git clone https://huggingface.co/spaces/<user>/pebble-voice-tester /tmp/space
cp -r deploy/hf-space-voice-tester/* /tmp/space/ && cd /tmp/space
git add -A && git commit -m "deploy voice tester" && git push
```
First build takes a few minutes (installs torch + funasr, downloads backbone weights on first
request). Add a model by dropping an `artifact_*/` bundle into `models/`.

> Free CPU tier: WavLM-Large ≈ 1–3 s/clip, emotion2vec similar after warm-up. For lower latency
> use a GPU Space (paid) — no code change needed.
