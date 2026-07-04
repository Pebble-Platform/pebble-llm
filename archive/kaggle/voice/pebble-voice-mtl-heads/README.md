# pebble-voice-mtl-heads — heterogeneous multi-task heads on a frozen speech encoder

Thesis extension of the [`pebble-emotion2vec-repro`](../pebble-emotion2vec-repro/) probe: same frozen
backbone (`emotion2vec_base` / WavLM-Large) + shared **SUPERB trunk**, but **three heads** instead of one —
emotion (8-way CE), **affect** (valence+arousal, **CCC loss**), and **crisis** (BCE under a **hard recall
floor**) — balanced by **Kendall uncertainty weighting**.

Protocol, proxy-label caveat, and decisions: [`docs/tasks/voice-mtl-heads.md`](../../../docs/tasks/voice-mtl-heads.md).
- All **1440** RAVDESS speech clips, **random 10-fold CV**, fresh stratified **80/10/10** per fold.
- Trunk `Linear(d,256) → ReLU → masked-mean-pool`; heads `emo Linear(256,8)`, `reg Linear(256,2)`, `safe Linear(256,1)`.
- **Proxy targets** (RAVDESS has no continuous/crisis labels): affect = Russell circumplex (valence,
  arousal); crisis = `{angry, fearful, sad, disgust}`. Crisis threshold tuned on val to `recall ≥ 0.90`.
- Reports per-backbone mean ± std of WA/UA/WF1, CCC(valence,arousal), and crisis recall/precision@floor.

> Validates the multi-head + recall-floor **mechanics** on real frozen features. Scientifically meaningful
> CCC / crisis-recall numbers need real continuous + clinical labels (MSP-Podcast A/V/D, DAIC) — a later task.

## Build the notebook

```bash
.venv-voice/Scripts/python.exe kaggle/voice/pebble-voice-mtl-heads/build_ipynb.py   # -> pebble_voice_mtl_heads.ipynb
```

## Push + run on Kaggle

Auth is the same one-time `~/.kaggle/kaggle.json` setup as the repro kernel (username `fabiocarava`).

```bash
.venv-voice/bin/kaggle kernels push   -p kaggle/voice/pebble-voice-mtl-heads
.venv-voice/bin/kaggle kernels status fabiocarava/pebble-voice-mtl-heads            # poll until not RUNNING
.venv-voice/bin/kaggle kernels output fabiocarava/pebble-voice-mtl-heads -p kaggle/voice/pebble-voice-mtl-heads/out
```

`out/` will contain: `results_voice_mtl.{csv,json}`, `sample_val.wav`, and `artifact_<backbone>/`
bundles (`config.json` + `mtl_head.pt`).

## Local sample test (CLI)

```bash
PYTHONPATH=src .venv-voice/bin/python scripts/voice_mtl_infer.py \
  kaggle/voice/pebble-voice-mtl-heads/out/artifact_wavlm-large \
  kaggle/voice/pebble-voice-mtl-heads/out/sample_val.wav
```

Prints the predicted emotion (+ top-3), the affect valence/arousal, and the crisis probability vs the
recall-floor-tuned threshold. emotion2vec bundles need `funasr` locally; WavLM bundles run with just transformers.
