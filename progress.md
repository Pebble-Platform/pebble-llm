# Progress

> Living status tracker. Update the **Current stage** line and the checklists as work moves.
> Plan lives in [`docs/phases/`](docs/phases/README.md); strategy in [`pebble-finetuning-strategy-v3.md`](pebble-finetuning-strategy-v3.md).

**Current stage:** 🟡 **Phase 5 in progress (public-data prep).** Reuse-public-labels v1: learn `detectedEmotion` (GoEmotions) + `severity` (SemEval-2018 EI-reg intensity) on free Kaggle GPU; the other 4 outputs are Decision-Engine heuristics. Annotation/safety/Gemini phases dropped for v1. See [`docs/decisions.md`](docs/decisions.md). **Kaggle GPU smoke test = GO** (NeoBERT loads + forward/backward) with a pinned stack. Data loaders + masked-multitask assembler done. **Next: emotion-head pre-train loop + trainer (Phase 6).**
**Last updated:** 2026-06-05

---

## Setup (pre-Phase-0) — done

- [x] Repo scaffold: `uv` project, `src/pebble_llm/` package, configs, tests, CI, serving Dockerfile
- [x] Phased plan broken out into `docs/phases/` (10 files) + overview `docs/phases.md`
- [x] Strategy doc reviewed (`pebble-finetuning-strategy-v3.md`)

### Code: implemented & tested
- [x] Taxonomy + GoEmotions mapping (`data/taxonomy.py`)
- [x] Multi-task heads + weighted loss (`models/heads.py`, `models/losses.py`)
- [x] §7 metrics + target checks (`evaluation/`)
- [x] User-level splitting (`data/splits.py`)
- [x] Serving schemas + FastAPI app shape (`serving/`)

### Code: stubs (TODO, marked in-source)
- [ ] Firestore silver-label ingestion (`data/silver_labels.py`) — N/A for v1
- [ ] GoEmotions emotion-head pre-training loop (`training/pretrain_emotion.py`)
- [ ] Train eval/checkpointing wiring (`training/trainer.py`, `scripts/run_*.py`)
- [ ] ONNX export spike (`scripts/export_onnx.py`) — deferred
- [ ] Checkpoint loading in serving (`serving/inference.py`) — deferred

---

## Phase status

> The phase docs in `docs/phases/` describe the **full Gemini/annotation strategy**.
> The reuse-labels v1 below uses only a subset — the rest is deferred or dropped.

| # | Phase | v1 disposition |
|---|---|---|
| 0 | [Pre-work & Foundations](docs/phases/00-prework-foundations.md) | ✅ Done |
| 1 | [Data Collection & Tooling](docs/phases/01-data-collection-tooling.md) | ⬜ N/A for v1 (no silver labels) |
| 2 | [Taxonomy & Viability Gates](docs/phases/02-taxonomy-viability-gates.md) | 🟡 Partial — emotion taxonomy/mapping yes; α viability gates N/A (those dims aren't learned) |
| 3 | [Human Annotation](docs/phases/03-human-annotation.md) | ⬜ Skipped for v1 |
| 4 | [Safety Data](docs/phases/04-safety-data.md) | ⬜ Skipped for v1 |
| 5 | [Dataset Prep & Transfer Pre-train](docs/phases/05-dataset-prep-pretrain.md) | 🟡 **In progress** — loaders + assembler done; pre-train loop next |
| 6 | [Multi-task Training & Eval](docs/phases/06-training-evaluation.md) | ⬜ Not started |
| 7 | [Serving Build & Integration](docs/phases/07-serving-integration.md) | ⬜ Deferred (post-PoC) |
| 8 | [Staged Rollout](docs/phases/08-staged-rollout.md) | ⬜ Deferred |
| 9 | [Monitoring & Iteration](docs/phases/09-monitoring-iteration.md) | ⬜ Deferred |

Legend: ⬜ Not started · 🟡 Partial/In progress · ✅ Done · ⛔ Blocked

---

## Phase 0 — engineering foundation (done)

- [x] NeoBERT revision pinned to `5424c8e…` in `config.py` + configs
- [x] Modeling code vendored & tracked (`models/_neobert_vendor/`: model.py, rotary.py, config.json) + `scripts/vendor_neobert.py`
- [x] GPU check: **no local GPU** — training must run on a GPU host (Kaggle).
  Corrected dep finding (from vendored `model.py`): **xformers + torch≥2.4 are the hard deps**;
  **flash_attn is optional** (packed-seq only; padded batches use torch SDPA). Earlier
  "FlashAttention blocker" note was wrong.
- [x] Decision log created (`docs/decisions.md`)

## Phase 5 — dataset prep + transfer (in progress)

- [x] **Kaggle GPU smoke test = GO** (`scripts/kaggle_smoke_test.py`): NeoBERT loads (222M),
  forward fp32+fp16 + backward all pass on a Kaggle P100. Driven headlessly via the kaggle CLI.
  - **Required pinned stack** (Kaggle's default torch 2.10 is broken — drops sm_60/P100 kernels
    and is too new for NeoBERT, which caused the earlier NaN/load failures, *not* a model bug):
    `torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 xformers==0.0.28.post3` (cu121) +
    `transformers==4.48.2` (matches NeoBERT's `config.json`).
- [x] **Severity loader** (`data/external.py::load_semeval_intensity`): SemEval-2018 EI-reg
  intensity → `severity` ∈ [0,1] (negatives = intensity, joy = 0.0 anchor). Lazy-downloads
  the per-emotion gold TSVs. Tested (`tests/test_external.py`).
- [x] **Emotion loader** (`data/external.py::load_goemotions_for_emotion_head`): parametrized by split.
- [x] **Masked-multitask assembler** (`data/build_dataset.py`): disjoint GoEmotions (emotion) +
  EI-reg (severity) pools → per-example masked records → `data/processed/*.jsonl`. Each row
  activates only its labeled head; safety head never trained in v1. Tested (`tests/test_build_dataset.py`).
- [ ] WASSA intensity augmentation (`load_wassa_intensity`) — stub, deferred (source unverified).
- [ ] Run the live `write_processed()` build (exercises real downloads — untested I/O).
- [ ] Emotion-head pre-train loop; trainer + masked multi-task loss wiring.

## Decisions — resolved (see `docs/decisions.md`)

- [x] **Data source (OQ5)** → reuse public dataset labels (no Gemini/silver labels)
- [x] **Dimension scope** → keep 6 outputs; learn `detectedEmotion` + `severity`; rest heuristic → `score_dims=[severity]`
- [x] **Clinical reviewer (OQ2)** → not needed for v1
- [x] **Annotation hiring (OQ3)** → not needed for v1
- [ ] **NeoBERT serving direction (OQ6)** → deferred to post-PoC (train on Kaggle first)
- [ ] **Cleanup:** `.claude/CLAUDE.md` describes a TypeScript/pnpm stack (wrong project) — rewrite for Python or remove

---
