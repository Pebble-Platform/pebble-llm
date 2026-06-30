# Voice model tester — local run guide (macOS / Linux)

> Windows version: [`voice-tester-guide-windows.md`](./voice-tester-guide-windows.md).

How to run the voice affect models (emotion2vec reproduction + WavLM) on macOS/Linux: the local
web UI, the CLI, and calling the cloud Space. Pairs with
[`docs/tasks/emotion2vec-reproduction.md`](./tasks/emotion2vec-reproduction.md) (the experiment)
and [`kaggle/voice/pebble-emotion2vec-repro/README.md`](../kaggle/voice/pebble-emotion2vec-repro/README.md)
(training on Kaggle). Commands use **bash/zsh**.

## What runs where (macOS, esp. Intel)

| | WavLM-Large | emotion2vec |
|---|---|---|
| **Local web tester** (`voice_tester`) | ✅ | ❌ needs `funasr` (won't build on Intel-mac) |
| **Local CLI** (`emotion2vec_repro_infer.py`) | ✅ | ❌ same |
| **Cloud Space**, called from local (`voice_remote_infer.py`) | ✅ | ✅ |
| **Kaggle kernel** (batch + demo cell) | ✅ | ✅ |

> **Why emotion2vec is cloud-only on this Mac:** it depends on `funasr` → `librosa`/`numba`, which
> don't build on the Intel-mac / Python 3.12 env. WavLM runs locally via `transformers`. To test
> emotion2vec, use the HF Space (§3) or the Kaggle demo cell. (On Apple-silicon you can try
> `pip install funasr`; if it installs, emotion2vec will run locally too.)

## 0. Prerequisites

The voice stack lives in **`.venv-voice/`** (Python 3.12, torch 2.2.2 CPU, numpy<2). Create it once:

```bash
/usr/local/bin/python3.12 -m venv .venv-voice
.venv-voice/bin/pip install "torch==2.2.2" "torchaudio==2.2.2" "numpy<2"
.venv-voice/bin/pip install fastapi "uvicorn[standard]" python-multipart transformers soundfile
```

You need at least one model bundle on disk. The tester auto-discovers `artifact_*/` folders under
`kaggle/voice/pebble-emotion2vec-repro/out2`, `…/out`, `kaggle/voice/pebble-voice-backbone/out`,
`artifacts/voice/`. Pull them from Kaggle (kernel README) or train a local stand-in:

```bash
PYTHONPATH=src .venv-voice/bin/python scripts/voice_local_smoke.py --ravdess-dir data/voice/external/ravdess
```

## 1. Local web tester (recommended)

Interactive UI: pick a model + a RAVDESS sample (or upload a wav), run, see the predicted emotion
with probability bars. emotion2vec bundles show as disabled.

```bash
PYTHONPATH=src .venv-voice/bin/uvicorn pebble_llm.serving.voice_tester:app --port 8080
# open http://localhost:8080
```

First inference for a backbone downloads its weights from HF Hub (WavLM-Large ≈ 1.2 GB) — slow
once, cached after. API: `GET /api/models`, `GET /api/samples`, `POST /api/infer`
(`model_id` + `sample_id` | `file`).

## 2. Local CLI (single clip)

```bash
.venv-voice/bin/python scripts/emotion2vec_repro_infer.py \
  kaggle/voice/pebble-emotion2vec-repro/out2/artifact_wavlm-large \
  kaggle/voice/pebble-emotion2vec-repro/out2/sample_val.wav
# -> PREDICTED: angry (p=0.897) + top-3
```

## 3. Test emotion2vec via the cloud Space (from local)

emotion2vec runs on the HF Space; your Mac just calls it over HTTP — no torch/funasr needed locally.

```bash
export HF_TOKEN=<your-hf-token>          # the Space is private
URL=https://pnguyen82-pebble-voice-tester.hf.space

.venv-voice/bin/python scripts/voice_remote_infer.py $URL --list
.venv-voice/bin/python scripts/voice_remote_infer.py $URL \
  emotion2vec--superb-frame deploy/hf-space-voice-tester/samples/03-01-05-01-01-01-21.wav
# -> PREDICTED: angry   truth=angry
```

Or open the URL in a browser (logged into HF) for the same UI as §1.

## 4. Reproduce / retrain on Kaggle (optional)

```bash
.venv-voice/bin/python kaggle/voice/pebble-emotion2vec-repro/build_ipynb.py
.venv-voice/bin/kaggle kernels push   -p kaggle/voice/pebble-emotion2vec-repro
.venv-voice/bin/kaggle kernels status fabiocarava/pebble-emotion2vec-reproduction
.venv-voice/bin/kaggle kernels output fabiocarava/pebble-emotion2vec-reproduction -p kaggle/voice/pebble-emotion2vec-repro/out2
```

Kaggle auth (build `kaggle.json` from the raw token, without echoing it):

```bash
KEY=$(tr -d ' \t\n\r' < ~/.kaggle/access_token)
printf '{"username":"fabiocarava","key":"%s"}' "$KEY" > ~/.kaggle/kaggle.json && chmod 600 ~/.kaggle/kaggle.json
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: funasr` / emotion2vec disabled | Expected on Intel-mac — use the Space (§3) or Kaggle. |
| `409 model needs 'funasr'` from the API | Same: pick a WavLM bundle locally. |
| `Address already in use` | Another uvicorn is up — use a different `--port`, or `lsof -ti:8080 | xargs kill`. |
| No models listed | No `artifact_*/` bundles on disk — pull from Kaggle or run the smoke script (§0). |
| First call very slow | Backbone weights downloading from HF Hub; later calls are cached. |
| Private Space returns 401/403 | `export HF_TOKEN=…` (the client sends it as a bearer header). |
| `librosa`/`numba` build error | Don't install `funasr` on Intel-mac — unsupported by design; use cloud. |
