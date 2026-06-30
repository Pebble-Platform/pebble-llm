# Voice model tester — local run guide (Windows)

> macOS / Linux version: [`voice-tester-guide-macos.md`](./voice-tester-guide-macos.md).

How to run the voice affect models (emotion2vec reproduction + WavLM) on Windows: the local web UI,
the CLI, and calling the cloud Space. Pairs with
[`docs/tasks/emotion2vec-reproduction.md`](./tasks/emotion2vec-reproduction.md) (the experiment)
and [`kaggle/voice/pebble-emotion2vec-repro/README.md`](../kaggle/voice/pebble-emotion2vec-repro/README.md)
(training on Kaggle). Commands use **PowerShell**.

## What runs where (Windows)

| | WavLM-Large | emotion2vec |
|---|---|---|
| **Local web tester** (`voice_tester`) | ✅ | ✅ *after `pip install funasr`* |
| **Local CLI** (`emotion2vec_repro_infer.py`) | ✅ | ✅ *after `pip install funasr`* |
| **Cloud Space**, called from local (`voice_remote_infer.py`) | ✅ | ✅ |
| **Kaggle kernel** (batch + demo cell) | ✅ | ✅ |

> **emotion2vec can usually run locally on Windows.** Unlike the Intel-mac, Windows has prebuilt
> `librosa`/`numba` wheels, so `funasr` installs. If `pip install funasr` succeeds, the tester lists
> emotion2vec as available and runs it locally. If it fails (build/toolchain issue), fall back to the
> cloud Space (§3) or Kaggle.

## 0. Prerequisites

Use Python 3.12. Create the venv once (PowerShell, from the repo root):

```powershell
py -3.12 -m venv .venv-voice
.venv-voice\Scripts\python -m pip install --upgrade pip
.venv-voice\Scripts\pip install "torch==2.2.2" "torchaudio==2.2.2" --index-url https://download.pytorch.org/whl/cpu
.venv-voice\Scripts\pip install "numpy<2" fastapi "uvicorn[standard]" python-multipart transformers soundfile
# optional — enables emotion2vec locally:
.venv-voice\Scripts\pip install funasr
```

> If you hit a PowerShell execution-policy error activating scripts, you don't need to *activate* —
> just call `.venv-voice\Scripts\python` directly as shown below.

You need at least one model bundle on disk. The tester auto-discovers `artifact_*\` folders under
`kaggle\voice\pebble-emotion2vec-repro\out2`, `…\out`, `kaggle\voice\pebble-voice-backbone\out`,
`artifacts\voice\`. Pull them from Kaggle (kernel README) or train a local stand-in:

```powershell
$env:PYTHONPATH="src"
.venv-voice\Scripts\python scripts\voice_local_smoke.py --ravdess-dir data\voice\external\ravdess
```

## 1. Local web tester (recommended)

```powershell
$env:PYTHONPATH="src"
.venv-voice\Scripts\python -m uvicorn pebble_llm.serving.voice_tester:app --port 8080
# open http://localhost:8080
```

First inference for a backbone downloads its weights from HF Hub (WavLM-Large ≈ 1.2 GB) — slow
once, cached after. API: `GET /api/models`, `GET /api/samples`, `POST /api/infer`
(`model_id` + `sample_id` | `file`).

## 2. Local CLI (single clip)

```powershell
.venv-voice\Scripts\python scripts\emotion2vec_repro_infer.py `
  kaggle\voice\pebble-emotion2vec-repro\out2\artifact_wavlm-large `
  kaggle\voice\pebble-emotion2vec-repro\out2\sample_val.wav
# -> PREDICTED: angry (p=0.897) + top-3
```

With `funasr` installed you can also point at `artifact_emotion2vec`.

## 3. Test emotion2vec via the cloud Space (from local)

Works even without `funasr` locally — the cloud does the inference.

```powershell
$env:HF_TOKEN="<your-hf-token>"          # the Space is private
$URL="https://pnguyen82-pebble-voice-tester.hf.space"

.venv-voice\Scripts\python scripts\voice_remote_infer.py $URL --list
.venv-voice\Scripts\python scripts\voice_remote_infer.py $URL `
  emotion2vec--superb-frame deploy\hf-space-voice-tester\samples\03-01-05-01-01-01-21.wav
# -> PREDICTED: angry   truth=angry
```

Or open the URL in a browser (logged into HF) for the same UI as §1.

## 4. Reproduce / retrain on Kaggle (optional)

```powershell
.venv-voice\Scripts\python kaggle\voice\pebble-emotion2vec-repro\build_ipynb.py
.venv-voice\Scripts\kaggle kernels push   -p kaggle\voice\pebble-emotion2vec-repro
.venv-voice\Scripts\kaggle kernels status fabiocarava/pebble-emotion2vec-reproduction
.venv-voice\Scripts\kaggle kernels output fabiocarava/pebble-emotion2vec-reproduction -p kaggle\voice\pebble-emotion2vec-repro\out2
```

Kaggle auth (build `kaggle.json` from the raw token, PowerShell):

```powershell
$key = (Get-Content "$HOME\.kaggle\access_token" -Raw).Trim()
'{"username":"fabiocarava","key":"' + $key + '"}' | Set-Content "$HOME\.kaggle\kaggle.json"
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `pip install funasr` fails | Use the cloud Space (§3) or Kaggle for emotion2vec; WavLM still runs locally. |
| `409 model needs 'funasr'` from the API | `funasr` isn't installed — `pip install funasr` or pick a WavLM bundle. |
| `running scripts is disabled on this system` | Don't activate the venv — call `.venv-voice\Scripts\python` directly (as above). |
| Port in use | `netstat -ano | findstr :8080` then `taskkill /PID <pid> /F`, or use another `--port`. |
| No models listed | No `artifact_*\` bundles on disk — pull from Kaggle or run the smoke script (§0). |
| First call very slow | Backbone weights downloading from HF Hub; later calls are cached. |
| Private Space returns 401/403 | `$env:HF_TOKEN="…"` (the client sends it as a bearer header). |
