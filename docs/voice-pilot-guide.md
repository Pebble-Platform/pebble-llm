# Voice Pilot — Operating Guide

> How to run, download, and verify the voice backbone pilot end-to-end.
> Decision + justification live in [`voice-method-selection.md`](./voice-method-selection.md);
> the survey is [`related-work-voice-multimodal.md`](./related-work-voice-multimodal.md).
> This file is the **how-to**.

The pilot compares two frozen speech encoders — **emotion2vec** (primary) vs **WavLM-Large**
(baseline) — with Pebble's heterogeneous heads (8-way emotion softmax + a recall-floored distress
head) on RAVDESS. There are **two ways to run it**: the GPU run on Kaggle (the real result) and a
local CPU stand-in (a cheap real artifact for serving). Both emit the **same artifact bundle**, so
the FastAPI verifier serves either one unchanged.

---

## 0. What gets produced (the artifact contract)

Both runs write one bundle per backbone:

```
artifact_<backbone>/
  config.json        # backbone_hf_id, embed_dim, emotions[], distress_emotions[],
                     # safety_threshold, sample_rate, max_samples, head dims, ...
  emotion_head.pt    # EmotionHead state_dict   (src/pebble_llm/models/heads.py)
  safety_head.pt     # SafetyHead state_dict
  sample_val.wav     # one 16 kHz val clip, for a quick smoke
```

The FastAPI app reads `config.json` to pick the backbone + threshold, then loads the two heads.
Nothing else is needed to serve. `embed_dim` is **1024** for WavLM-Large, **768** for
emotion2vec / WavLM-Base.

---

## Path A — Kaggle GPU run (the thesis result)

**Prereq (one-time):** the API key is stored at `~/.kaggle/access_token` (a raw key, **not** the
`kaggle.json` the CLI expects). Install the CLI and build `kaggle.json` from it (username =
`fabiocarava`, from the kernel ids). Do **not** echo the key:

```bash
.venv-voice/bin/pip install kaggle            # or: pip install kaggle
KEY=$(tr -d ' \t\n\r' < ~/.kaggle/access_token)
printf '{"username":"fabiocarava","key":"%s"}' "$KEY" > ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
.venv-voice/bin/kaggle kernels list --mine    # verify auth (lists your kernels)
```

**Run:**

```bash
python kaggle/pebble-voice-backbone/build_ipynb.py                       # (re)assemble the .ipynb from cells
.venv-voice/bin/kaggle kernels push   -p kaggle/pebble-voice-backbone
.venv-voice/bin/kaggle kernels status fabiocarava/pebble-voice-backbone  # poll until not RUNNING
.venv-voice/bin/kaggle kernels output fabiocarava/pebble-voice-backbone -p kaggle/pebble-voice-backbone/out
```

> Poll loop (status is external — nothing notifies you):
> ```bash
> while .venv-voice/bin/kaggle kernels status fabiocarava/pebble-voice-backbone | grep -q RUNNING; do sleep 90; done
> ```

`out/` then holds `results_voice_backbone.{csv,json}`, `sample_val.wav`, and
`artifact_emotion2vec/` + `artifact_wavlm-large/`.

> **Editing the experiment:** change the `.py` cells in `kaggle/pebble-voice-backbone/`
> (`c1_imports.py` … `c5_results.py`), then re-run `build_ipynb.py` before pushing. Never edit the
> `.ipynb` by hand — it's generated.

---

## Path B — local CPU stand-in (no Kaggle needed)

Uses WavLM-Base on a RAVDESS subset. Same pipeline, smaller encoder/data — enough to produce a real
servable artifact and exercise the whole serving path.

```bash
# 1. one-time env (Intel mac -> torch is capped at 2.2.2; see Troubleshooting)
/usr/local/bin/python3.12 -m venv .venv-voice
.venv-voice/bin/python -m pip install "torch==2.2.2" "torchaudio==2.2.2" "numpy<2" \
  "transformers==4.48.2" "datasets>=3.0,<4" "fastapi>=0.115" "uvicorn[standard]" \
  soundfile scikit-learn scipy pandas python-multipart

# 2. get RAVDESS (HF download is flaky on slow links; pull the Zenodo zip directly)
mkdir -p data/external/ravdess && cd data/external/ravdess
curl -L -C - --retry 8 --retry-all-errors -o Audio_Speech_Actors_01-24.zip \
  "https://zenodo.org/records/1188976/files/Audio_Speech_Actors_01-24.zip?download=1"
unzip -q -o Audio_Speech_Actors_01-24.zip && cd -

# 3. train a real artifact (~5 min CPU)
PYTHONPATH=src .venv-voice/bin/python scripts/voice_local_smoke.py --ravdess-dir data/external/ravdess
```

→ writes `artifacts/voice/artifact_wavlm-base/`.

---

## Verify with FastAPI (works for either path)

```bash
# point at any artifact bundle (local or downloaded from Kaggle)
VOICE_ARTIFACT=artifacts/voice/artifact_wavlm-base \
  PYTHONPATH=src .venv-voice/bin/uvicorn pebble_llm.serving.voice_app:app --port 8081
```

```bash
curl -s http://localhost:8081/health
# {"status":"ok","backbone":"wavlm-base","emotions":"neutral,calm,..."}

PYTHONPATH=src .venv-voice/bin/python scripts/voice_verify_client.py \
  artifacts/voice/artifact_wavlm-base/sample_val.wav
# {"detectedEmotion":"...","emotionProbs":{...},"distressScore":0.x,"safetyFlag":bool,"backbone":"..."}
```

You can post **any** wav (any sample rate) — the app resamples to 16 kHz and pads/truncates to 4 s.

**Endpoints:** `GET /health`, `POST /classify-voice` (multipart `file=@clip.wav`).
**Env:** `VOICE_ARTIFACT` (bundle dir), `VOICE_DEVICE` (`cpu` default).

To serve the Kaggle WavLM-Large bundle instead:
```bash
VOICE_ARTIFACT=kaggle/pebble-voice-backbone/out/artifact_wavlm-large ...uvicorn...
```
(For an `emotion2vec` bundle the app needs `pip install funasr modelscope` in the venv.)

---

## Tests

```bash
PYTHONPATH=src .venv-voice/bin/python -m pytest tests/test_voice_serving.py -q -o addopts=""
```

`-o addopts=""` is required locally — the project pytest config enables `--cov`, but
`pytest-cov` isn't in `.venv-voice`. The tests stub the backbone, so they need no model download.

---

## How to read the result

- **emo macro-F1** — 8-way emotion; chance ≈ 0.125. The headline backbone-comparison number.
- **distress recall@0.5 / precision@recall-floor** — the safety head. The threshold is chosen as the
  **highest** value whose val recall ≥ 0.90 (recall floor), and precision is reported there. This is
  the voice analogue of Pebble's text safety head.
- **paired delta (emotion2vec − WavLM, per seed)** — the real verdict: did the emotion-specialized
  encoder actually beat the strong general one, controlling for seed noise.

---

## Troubleshooting (things that bite on this machine)

| Symptom | Cause / fix |
|---|---|
| `No matching distribution found for torch>=2.4` | Intel macOS — last x86_64 torch wheel is **2.2.2**. Pin `torch==2.2.2 torchaudio==2.2.2`. |
| `Failed building wheel for llvmlite/numba` | librosa's build dep won't compile here. **Don't install librosa** — use `soundfile` + `torchaudio` for load/resample. |
| `numpy` ABI / segfault with torch 2.2.2 | pin **`numpy<2`**. |
| `FSTimeoutError` downloading `narad/ravdess` | HF's fsspec has a hard timeout on slow links. Use the **Zenodo zip** + `--ravdess-dir` (Path B step 2). |
| `pytest: unrecognized arguments: --cov` | run with `-o addopts=""`. |
| safetyFlag always True / threshold ≈ 0.01 | the recall-floor selector must keep the **highest** qualifying threshold, not the first. Already fixed in `scripts/voice_local_smoke.py` + cell `c4_probe.py`. |
| emotion2vec arm shows "SKIPPED" on Kaggle | funasr/modelscope install or download failed — the WavLM baseline still runs. Re-check internet flag + the install cell. |
| `kaggle` says `401`/`Could not authenticate` | the key lives at `~/.kaggle/access_token`, not `kaggle.json`. Build `kaggle.json` from it (see Path A prereq). |

---

## File map

| Path | Role |
|---|---|
| `docs/voice-method-selection.md` | the decision + justification + plan |
| `kaggle/pebble-voice-backbone/` | the GPU notebook (cells + `build_ipynb.py` + `README.md`) |
| `scripts/voice_local_smoke.py` | local CPU stand-in that produces a real artifact |
| `scripts/voice_verify_client.py` | posts a wav to the running app |
| `src/pebble_llm/serving/voice_app.py` | FastAPI app (`/health`, `/classify-voice`) |
| `src/pebble_llm/serving/voice_inference.py` | loads bundle + backbone, runs the heads |
| `src/pebble_llm/serving/voice_schemas.py` | response schema |
| `tests/test_voice_serving.py` | waveform + classify-path tests |
