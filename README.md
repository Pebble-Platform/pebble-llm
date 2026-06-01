# Pebble Emotion Classifier

Multi-task fine-tuning of **NeoBERT** (`chandar-lab/NeoBERT`) into a self-hosted
emotion classifier for Pebble's Decision Engine. The classifier runs *before*
generation and emits structured scores from typed heads. **Gemini 2.5 Flash-Lite
is the backup path.**

> Full rationale, datasets, gates, timeline, and open questions live in
> [`pebble-finetuning-strategy-v3.md`](./pebble-finetuning-strategy-v3.md).
> Code references it by section (e.g. `§5.2`).

## What it produces

One structured output per message (strategy §2):

```json
{ "energy": 0.0, "severity": 0.0, "socialIsolation": 0.0,
  "receptivity": 0.0, "detectedEmotion": "", "safetyFlag": false }
```

`themeRepetition` and `sessionTrajectory` are intentionally **not** model outputs —
the Decision Engine computes those.

## Layout

```
configs/            Hydra-style YAML (data / model / training / serving) → loaded into typed pydantic Config
src/pebble_llm/
  config.py         Typed config loading
  data/             taxonomy + GoEmotions mapping, silver-label ingestion, external loaders, user-level splits
  models/           multi-task heads, NeoBERT wrapper, weighted multi-task loss
  training/         staged trainer (encoder freeze → unfreeze), GoEmotions pre-training
  evaluation/       §7 metrics + Protocol B target checks
  serving/          FastAPI /classify, schemas, inference
  utils/            seeding, logging / experiment tracking
scripts/            prepare_dataset, run_pretrain, run_train, run_eval, export_onnx (Track B spike)
annotation/         Protocol A/B, viability gates, annotator wellbeing
data/               raw / interim / processed / external (gitignored — never commit)
serving/            Dockerfile + serving notes (Track A GPU baseline)
tests/              taxonomy, heads, losses, metrics, splits
notebooks/          EDA only
```

## Setup

```bash
uv sync --all-extras --dev    # or: make install
cp .env.example .env          # fill in W&B / GCP / serving values
pre-commit install
```

> NeoBERT needs FlashAttention/xformers on **GPU** for training. Those deps are
> commented out in `pyproject.toml` — install them on GPU hosts. Pin the model
> `revision` and vendor the modeling code before any real run (§6.1 Step 0).

## Workflow

```bash
make data       # ingest silver labels → splits (§5.5)        [stub: wire Firestore]
make pretrain   # emotion head on GoEmotions (§6.1 Step 1)    [stub]
make train      # multi-task fine-tune, ≥3 seeds (§6.1 Step 2)
make eval       # Protocol B test set vs §7 targets
make serve      # local FastAPI /classify
make check      # ruff + mypy + pytest
```

## Status

Scaffold with functional skeletons. **Implemented & tested:** taxonomy + GoEmotions
mapping, multi-task heads, weighted loss, §7 metrics, user-level splitting, serving
schemas/app shape. **TODO (marked in-code):** Firestore ingestion, GoEmotions
pre-training loop, train eval/checkpointing, ONNX export spike, checkpoint loading
in serving.

## Hard gates before deploy (from the strategy)

- No deployment without a completed **Protocol B** evaluation (§6.1 Step 5).
- `safetyFlag` recall **≥ 0.95** or the classifier's safety output is supplementary only (§7).
- 0.5–0.8 severity-band MAE ≤ 0.15 — else **do not deploy** (§8.3).
- Energy/severity independence check before training; drop the energy head if |r| > 0.7 (§5.2).
- Generator migration off Gemini 2.0 Flash before **2026-06-01** (OQ5).

---

### ⚠️ Note on `.claude/CLAUDE.md`

The committed `.claude/CLAUDE.md` describes a **TypeScript/pnpm/Biome** stack — that
belongs to a different project and does not match this Python ML repo. It should be
rewritten for this project (uv, ruff, mypy, pytest) or removed. Flagged, not changed.
