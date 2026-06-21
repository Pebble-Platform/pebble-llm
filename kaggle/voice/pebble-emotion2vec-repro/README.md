# pebble-emotion2vec-repro — reproduce emotion2vec Table 3 (RAVDESS)

Faithful reproduction of **emotion2vec** (Ma et al., ACL Findings 2024): frozen
`emotion2vec_base` + a **SUPERB linear probe** on RAVDESS, scored by the paper's own
metrics (WA/UA/WF1) and compared to **Table 3 (emotion2vec RAVDESS = WA 82.43 / UA 82.86 /
WF1 82.39)**. **WavLM-Large** is run under the same probe as the thesis comparator.

Protocol, sources, and decisions: [`docs/tasks/emotion2vec-reproduction.md`](../../../docs/tasks/emotion2vec-reproduction.md).
- All **1440** RAVDESS speech clips, all **8** classes.
- **Random 10-fold CV**, each fold a fresh stratified **80/10/10** split (paper §5.1).
- Head: `Linear(d,256) → ReLU → Linear(256,8)`, frozen single-layer feats, cross-entropy.
- Reports mean ± std of per-fold test WA/UA/WF1.

> This is a *paper reproduction* — distinct from the sibling `pebble-voice-backbone`
> pilot, which trains Pebble's own heterogeneous heads (emotion + distress) and Pebble
> metrics. Reuses that pilot's frozen-feature extractors verbatim.

## Build the notebook

```bash
python kaggle/voice/pebble-emotion2vec-repro/build_ipynb.py   # -> pebble_emotion2vec_repro.ipynb
```

## Push + run on Kaggle

Auth (one-time): API key at `~/.kaggle/access_token` (raw key); build `kaggle.json`
(username `fabiocarava`) without echoing the key:

```bash
.venv-voice/bin/pip install kaggle
KEY=$(tr -d ' \t\n\r' < ~/.kaggle/access_token)
printf '{"username":"fabiocarava","key":"%s"}' "$KEY" > ~/.kaggle/kaggle.json && chmod 600 ~/.kaggle/kaggle.json
```

Run:

```bash
.venv-voice/bin/kaggle kernels push   -p kaggle/voice/pebble-emotion2vec-repro
.venv-voice/bin/kaggle kernels status fabiocarava/pebble-emotion2vec-reproduction      # poll until not RUNNING
.venv-voice/bin/kaggle kernels output fabiocarava/pebble-emotion2vec-reproduction -p kaggle/voice/pebble-emotion2vec-repro/out
```

`out/` will contain: `results_emotion2vec_repro.{csv,json}`, `sample_val.wav`, and
`artifact_<backbone>/` bundles (`config.json` + `emotion_head.pt`).

## Local sample test (CLI)

```bash
PYTHONPATH=src .venv-voice/bin/python scripts/emotion2vec_repro_infer.py \
  kaggle/voice/pebble-emotion2vec-repro/out2/artifact_wavlm-large \
  kaggle/voice/pebble-emotion2vec-repro/out2/sample_val.wav
```

## Web tester (choose model + sample, see result)

A multi-model web UI that auto-discovers every `artifact_*/` bundle (this repro v1/v2, the
pilot, local artifacts), lets you pick the model + a RAVDESS sample (or upload a wav), and
shows the predicted emotion with probability bars. emotion2vec bundles need `funasr` locally
(absent → listed but disabled); WavLM bundles run with just transformers.

```bash
PYTHONPATH=src .venv-voice/bin/uvicorn pebble_llm.serving.voice_tester:app --port 8080
# open http://localhost:8080
```

Source: `src/pebble_llm/serving/voice_tester.py` + `static/voice_tester.html`. To add a model,
drop a bundle (`config.json` + `*_head.pt`) under any root in `ARTIFACT_ROOTS`.
