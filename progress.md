# Progress

> Living status tracker. Update the **Current stage** line and the checklists as work moves.
> Plan lives in [`docs/phases/`](docs/phases/README.md); strategy in [`pebble-finetuning-strategy-v3.md`](pebble-finetuning-strategy-v3.md).

**Current stage:** ✅ **Phase 0 complete.** Pivoted to a **reuse-public-labels v1**: learn `detectedEmotion` (GoEmotions) + `severity` (SemEval/WASSA intensity) on free Kaggle GPU; the other 4 outputs are Decision-Engine heuristics. Annotation/safety/Gemini phases dropped for v1. See [`docs/decisions.md`](docs/decisions.md). **Next: Phase 5 (public-data prep + training).**
**Last updated:** 2026-05-29

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
- [ ] Firestore silver-label ingestion (`data/silver_labels.py`)
- [ ] GoEmotions emotion-head pre-training loop (`training/pretrain_emotion.py`)
- [ ] Train eval/checkpointing wiring (`training/trainer.py`, `scripts/run_*.py`)
- [ ] ONNX export spike (`scripts/export_onnx.py`)
- [ ] Checkpoint loading in serving (`serving/inference.py`)

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
| 5 | [Dataset Prep & Transfer Pre-train](docs/phases/05-dataset-prep-pretrain.md) | ⬜ **Next** (public data) |
| 6 | [Multi-task Training & Eval](docs/phases/06-training-evaluation.md) | ⬜ Not started |
| 7 | [Serving Build & Integration](docs/phases/07-serving-integration.md) | ⬜ Deferred (post-PoC) |
| 8 | [Staged Rollout](docs/phases/08-staged-rollout.md) | ⬜ Deferred |
| 9 | [Monitoring & Iteration](docs/phases/09-monitoring-iteration.md) | ⬜ Deferred |

Legend: ⬜ Not started · 🟡 Partial/In progress · ✅ Done · ⛔ Blocked

---

## Phase 0 — engineering foundation (done)

- [x] NeoBERT revision pinned to `5424c8e…` in `config.py` + configs
- [x] Modeling code vendored & tracked (`models/_neobert_vendor/`: model.py, rotary.py, config.json) + `scripts/vendor_neobert.py`
- [x] GPU check: **no local GPU** — training must run on a GPU host/CI (FlashAttention)
- [x] Decision log created (`docs/decisions.md`)

## Decisions — resolved (see `docs/decisions.md`)

- [x] **Data source (OQ5)** → reuse public dataset labels (no Gemini/silver labels)
- [x] **Dimension scope** → keep 6 outputs; learn `detectedEmotion` + `severity`; rest heuristic → `score_dims=[severity]`
- [x] **Clinical reviewer (OQ2)** → not needed for v1
- [x] **Annotation hiring (OQ3)** → not needed for v1
- [ ] **NeoBERT serving direction (OQ6)** → deferred to post-PoC (train on Kaggle first)
- [ ] **Cleanup:** `.claude/CLAUDE.md` describes a TypeScript/pnpm stack (wrong project) — rewrite for Python or remove

---

## Next action

**Phase 5 (public-data path):** wire the dataset loaders — GoEmotions → emotion head,
SemEval/WASSA intensity → severity — and run the emotion-head pre-train, then multi-task
train on Kaggle GPU. (Verify NeoBERT + FlashAttention/xformers runs on Kaggle's CUDA first.)
