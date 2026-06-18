# pebble-voice-backbone — frozen speech-encoder backbone selection

Pilot for the voice modality: **emotion2vec (primary) vs WavLM-Large (baseline)**,
Pebble's heterogeneous heads (8-way emotion softmax + a high-distress recall head)
on RAVDESS, 3 seeds, paired delta. Rationale: [`docs/voice-method-selection.md`](../../docs/voice-method-selection.md).

## Build the notebook

```bash
python kaggle/pebble-voice-backbone/build_ipynb.py   # -> pebble_voice_backbone.ipynb
```

## Push + run on Kaggle

Auth (one-time): the API key is at `~/.kaggle/access_token` (raw key, not `kaggle.json`).
Build `kaggle.json` from it — username `fabiocarava` — without echoing the key:

```bash
.venv-voice/bin/pip install kaggle
KEY=$(tr -d ' \t\n\r' < ~/.kaggle/access_token)
printf '{"username":"fabiocarava","key":"%s"}' "$KEY" > ~/.kaggle/kaggle.json && chmod 600 ~/.kaggle/kaggle.json
```

Run:

```bash
.venv-voice/bin/kaggle kernels push   -p kaggle/pebble-voice-backbone
.venv-voice/bin/kaggle kernels status fabiocarava/pebble-voice-backbone        # poll until not RUNNING
.venv-voice/bin/kaggle kernels output fabiocarava/pebble-voice-backbone -p kaggle/pebble-voice-backbone/out
```

`out/` will contain: `results_voice_backbone.{csv,json}`, `sample_val.wav`, and
`artifact_<backbone>/` bundles (`config.json` + `emotion_head.pt` + `safety_head.pt`).

## Verify a downloaded artifact (FastAPI)

```bash
VOICE_ARTIFACT=kaggle/pebble-voice-backbone/out/artifact_wavlm-large \
  PYTHONPATH=src .venv-voice/bin/uvicorn pebble_llm.serving.voice_app:app --port 8081
# then:
PYTHONPATH=src .venv-voice/bin/python scripts/voice_verify_client.py \
  kaggle/pebble-voice-backbone/out/sample_val.wav
```

## Local CPU stand-in (no Kaggle)

`scripts/voice_local_smoke.py` runs the same pipeline with WavLM-Base on a small
RAVDESS subset and writes `artifacts/voice/artifact_wavlm-base/` — a real bundle
the same FastAPI app serves.
