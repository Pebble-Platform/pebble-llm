# Run Guideline — Text 3-seed + Voice (end to end)

> One page to run everything: the **text** NeoBERT MLM 3-seed model, and the **voice**
> WavLM-Large backbone pilot + demo website. Both GPU jobs run on **Kaggle** (no local
> GPU needed) and are driven by one script: [`scripts/run_kaggle.py`](../scripts/run_kaggle.py).
>
> Deep dives: text rationale → [`pebble-finetuning-strategy-v3.md`](../pebble-finetuning-strategy-v3.md);
> voice decision → [`voice-method-selection.md`](./voice-method-selection.md);
> voice how-to → [`voice-pilot-guide.md`](./voice-pilot-guide.md).

```
                    scripts/run_kaggle.py  (build -> push -> poll -> fetch)
                   /                                                        \
   TEXT: pebble-mlm-ablation-3seed                       VOICE: pebble-voice-backbone
   GoEmotions + EI-reg, MLM adapt,                       RAVDESS, frozen WavLM-Large vs
   fine-tune BOTH arms x 3 seeds                         emotion2vec, heads x 3 seeds
   -> results_summary.csv, *.pt                          -> artifact_<backbone>/, results
                                                                     |
                                                         serve the website (this repo)
                                                         uvicorn voice_web:app :8080
```

---

## 0. One-time setup

### 0a. Kaggle auth (needed for BOTH jobs)
The raw API key lives at `~/.kaggle/access_token`. The driver builds `~/.kaggle/kaggle.json`
from it automatically on first run (username `fabiocarava`). Just make the CLI available:

```bash
python -m pip install kaggle          # into whatever Python you'll run the driver with
python -m kaggle kernels list --mine  # sanity check: lists your kernels
```

> If you ever see `401`: the key is the **raw token** at `~/.kaggle/access_token`, not a
> `kaggle.json`. Delete a stale `kaggle.json` and let the driver rebuild it.

### 0b. Local Python env (only needed to SERVE the voice demo, not to run Kaggle)
```bash
python -m venv .venv-voice
.venv-voice/Scripts/python.exe -m pip install --upgrade pip
.venv-voice/Scripts/python.exe -m pip install torch torchaudio transformers \
  soundfile "numpy<2" fastapi "uvicorn[standard]" python-multipart
```
(On Windows the venv interpreter is `.venv-voice/Scripts/python.exe`; on macOS/Linux it's
`.venv-voice/bin/python`. `torch==2.12.1` has Python 3.14 wheels — no pin needed here.)

---

## 1. TEXT — dataset + 3-seed model

**What it is:** adapt `chandar-lab/NeoBERT` once with MLM on a big *separate* in-domain corpus
(GoEmotions raw + tweet_eval, deduped against the eval set), then fine-tune **both arms**
(MLM-on vs MLM-off) across **3 seeds** `[13, 42, 1337]` for a paired delta. **The datasets
(GoEmotions, EI-reg) download inside the kernel** — nothing to prepare locally. Cells
`s1…s8` are in `kaggle/pebble-mlm-ablation-3seed/`.

> ⚠️ Local `scripts/run_train.py` / `prepare_dataset.py` are **stubs** — the real text run is
> this Kaggle kernel. `make train` does not train.

### Run it
```bash
python scripts/run_kaggle.py --job text
```
This assembles the notebook (`build_ipynb.py`), pushes a GPU run, polls status until it
completes (~status every 90 s), then downloads outputs to `kaggle/pebble-mlm-ablation-3seed/out/`.

> Pushing starts a **billable P100 GPU run** (tens of minutes). To only re-download a run you
> already started: `python scripts/run_kaggle.py --job text --no-build --no-push`.

### Outputs
| File | Contents |
|---|---|
| `results_summary.csv` | per-arm mean±std + the paired `delta (on-off)` row |
| `results_per_seed.csv` | one row per (arm, seed) — written incrementally, survives interrupts |
| `mlm_encoder.pt` | the MLM-adapted encoder (fp32) |
| `pebble_model.pt` | shippable exported model from cell s8 |

Metrics: `emo_macroF1`, `emo_ece`, `sev_pearson`, `sev_spearman`, `sev_mae`. Last run (for
reference): MLM-on emo macro-F1 `0.326±0.010` vs MLM-off `0.313±0.011` (delta `+0.013±0.010`);
severity Pearson slightly **down** under MLM. Read `results_summary.csv` for the live verdict.

### Tune without redoing MLM
Edit `s5_ft_setup.py`/`s6_run_seeds.py`, rebuild, push again — the MLM adaptation (s3/s4) is a
separate stage. To change seeds, edit `SEEDS` in `s1_imports.py`.

---

## 2. VOICE — backbone pilot (3 seeds)

**What it is:** frozen **WavLM-Large vs emotion2vec** on RAVDESS, Pebble's heads (8-way emotion
softmax + recall-floored distress head), **3 seeds**, paired delta. Cells `c1…c5` in
`kaggle/pebble-voice-backbone/`. **WavLM-Large won** (emo macro-F1 0.609 vs 0.537).

### Run it
```bash
python scripts/run_kaggle.py --job voice
```
Outputs land in `kaggle/pebble-voice-backbone/out/`:
`results_voice_backbone.{csv,json}`, `sample_val.wav`, and one bundle per backbone
`artifact_<backbone>/` = `config.json` + `emotion_head.pt` + `safety_head.pt`.

> The committed repo keeps only each bundle's `config.json`; the `.pt` head weights come from
> this fetch (or from `--no-build --no-push` if the kernel already ran).

---

## 3. VOICE — run the demo website

Serve the trained voice model behind a sample-picker UI (pick a RAVDESS clip or upload a wav →
run WavLM-Large → see emotion probabilities + distress/safety). The WavLM-Large encoder
(~1.2 GB) downloads from HuggingFace on first classify.

### 3a. Get demo samples (one held-out clip per emotion)
```bash
# RAVDESS speech zip (~208 MB) from Zenodo
mkdir -p data/external/ravdess
curl -L -C - --retry 8 --retry-all-errors -o data/external/ravdess/Audio_Speech_Actors_01-24.zip \
  "https://zenodo.org/records/1188976/files/Audio_Speech_Actors_01-24.zip?download=1"
# extract 8 actor-21 clips (one per emotion) into the samples dir the app serves
.venv-voice/Scripts/python.exe scripts/make_voice_samples.py
```

### 3b. Launch the site
```bash
PYTHONPATH=src \
VOICE_ARTIFACT=kaggle/pebble-voice-backbone/out/artifact_wavlm-large \
VOICE_SAMPLES=data/external/voice_samples \
  .venv-voice/Scripts/python.exe -m uvicorn pebble_llm.serving.voice_web:app --port 8080
```
Open **http://127.0.0.1:8080**. Endpoints: `/health`, `/api/samples`, `POST /api/classify-sample?name=`,
`POST /api/classify` (upload).

> Expect ~5/8 emotion accuracy on held-out actor 21 (matches the 0.61 macro-F1), and the
> distress head firing on most clips (high-recall/moderate-precision calibration) — that's the
> real model, faithfully shown.

---

## Cheat sheet

| Goal | Command |
|---|---|
| Run text 3-seed model | `python scripts/run_kaggle.py --job text` |
| Run voice backbone pilot | `python scripts/run_kaggle.py --job voice` |
| Re-download a finished run | `python scripts/run_kaggle.py --job text --no-build --no-push` |
| Any other kernel dir | `python scripts/run_kaggle.py --kernel <dir> --out <dir>` |
| Build samples for the demo | `.venv-voice/Scripts/python.exe scripts/make_voice_samples.py` |
| Serve the voice website | see §3b |
