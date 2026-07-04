# R2 full 5-fold CV on Kaggle GPU with gold-holdout eval

- **Slug:** r2-kaggle-cv-gold-holdout
- **Status:** done ✅ (gold macro-F1 0.357 vs 0.237 baseline)
- **Created:** 2026-06-23  ·  **Updated:** 2026-06-24
- **Owner:** Fabio / Claude

## Goal
Run the R2 dual-head model on the enriched **10,072-sample** dataset with a **full 5-fold CV on Kaggle GPU**,
evaluating on a **held-out clinical gold set** (CSSRS-500, 392 samples) so the reported numbers reflect true
accuracy — not agreement with the LLM labels. Produce honest macro-F1 / MAE / QWK vs the 0.2374 baseline (392-only run).

## Requirements & Constraints
- **Functional:** gold-holdout = CSSRS-500 (392, clinical) held out as TEST; train pool = av9ash + scraped
  (~9,680, LLM-labeled); 5-fold stratified CV on the pool (train + early-stop val on LLM labels); evaluate
  each fold's best model on the gold TEST; report per-fold + mean GOLD macro-F1/MAE/QWK (the honest number)
  alongside the CV-val numbers.
- **Data on Kaggle:** combined CSV is local + gitignored → upload as a **PRIVATE** Kaggle dataset (mental-health
  source data), reference it in the kernel; kernel reads from `/kaggle/input/<slug>/`.
- **Constraints:** surgical changes to `notebooks/r2-suicide-risk-dualhead.py` (gated by an env flag, default
  behavior unchanged); keep the kaggle copy in sync; faithful to paper's arch/loss/training.
- **Non-goals:** no architecture change; no Behavior-class rebalancing yet (separate task).

## Milestones
- [ ] M1 — Add source-aware loader + gold-holdout mode to the script (env `R2_GOLD_HOLDOUT`)
- [ ] M2 — Local CPU smoke: gold-holdout path runs end-to-end on the combined CSV
- [ ] M3 — Upload combined CSV as a PRIVATE Kaggle dataset
- [ ] M4 — Wire kernel (dataset_source + input path + env), push, poll to COMPLETE
- [ ] M5 — Retrieve results; report gold macro-F1/MAE/QWK vs 0.2374 baseline; fold into docs

## Decision Log
- **2026-06-23 — Gold-holdout design:** CSSRS-500 (392 clinical) = fixed TEST; av9ash+scraped (~9.68k LLM) =
  CV pool. 5-fold stratified CV on the pool for training + early-stop val; each fold's best model also scored
  on the gold TEST → report mean gold metrics. Why: the only non-circular signal is the clinical gold; eval on
  LLM labels would measure LLM-agreement, not accuracy. Rejected: plain 5-fold on all 10k (circular);
  gold-in-training (wastes the only clean eval signal).
- **2026-06-23 — Gate behind `R2_GOLD_HOLDOUT` env, source split by the `Source` column:** keeps default
  (plain CV) behavior intact (surgical). Rejected: a separate script (duplication).
- **2026-06-23 — Private Kaggle dataset for the 10k:** data is public-sourced (Reddit + CC-BY) but
  mental-health → keep the Kaggle dataset PRIVATE. Consistent with prior Kaggle runs in this repo.

## Open Questions
<!-- none blocking; all known engineering -->

## Research Findings
<!-- (none needed — known engineering) -->

## Completed Work
- 2026-06-23 — Read the R2 script (Config, main CV loop, evaluate, load_cssrs) to scope surgical edits.
- 2026-06-23 — M1: added `load_combined` (source-aware) + `run_gold_holdout` + `R2_GOLD_HOLDOUT`/`R2_EPOCHS`
  env to `notebooks/r2-suicide-risk-dualhead.py`; synced kaggle copy (kaggle sets gold-holdout + epochs=10).
- 2026-06-23 — M2: local CPU smoke (bert-tiny) of gold-holdout path runs end-to-end (train-pool → fold → gold eval → save).
- 2026-06-23 — M3: uploaded combined CSV as PRIVATE Kaggle dataset `fabiocarava/r2-cssrs-combined-10k` (status ready).
- 2026-06-23 — M4: kernel-metadata `dataset_sources` → the dataset; pushed kernel **v6** (RUNNING). v5 (epochs 15)
  superseded — capped to 10 to stay under the 12h GPU cap (worst case ~8.6h; early stopping → ~5-6h realistic).

## Decision Log (append)
- **2026-06-23 — Cap Kaggle epochs at 10 (`R2_EPOCHS`):** 7.7k train × 5 folds × 15 epochs worst-case ~13h >
  Kaggle's 12h GPU cap → wasted run risk. Early stopping (patience 5) usually triggers <10 anyway, and more
  data needs fewer epochs. Local/default stays 15. Rejected: 3 folds (user wants full 5-fold); subsampling (loses data).

## ✅ FINAL RESULTS (kernel v6, ~9.1h GPU, 2026-06-24)
Train pool 9,680 LLM-labeled `[3992,3612,634,1442]` · held-out gold test = CSSRS-500 392 `[99,171,77,45]`.

| Run | Train data | Eval | macro-F1 | MAE | QWK |
|---|---|---|---|---|---|
| Baseline | 392 (CSSRS-500) | 5-fold CV on itself | 0.2374 | 0.724 | 0.241 |
| **This** | **10k (LLM-labeled pool)** | **held-out clinical gold** | **0.3569** ±0.012 | 0.840 | **0.378** |

- **Gold macro-F1 0.2374 → 0.3569** (+0.12, ~+50% rel) and **QWK 0.241 → 0.378** — and this is the *honest*
  held-out clinical number (non-circular), vs the baseline's own-CV number. Enrichment clearly helped.
- **val-on-LLM 0.638 vs gold 0.357**: the ~0.28 gap quantifies the LLM-label ↔ clinical-label distribution
  difference (model fits LLM labels well; clinical gold is harder).
- Below the paper's 0.5098 (expected: substitute data, LLM labels, Behavior only 6.5% of pool → weak there).
- Per-fold gold F1 very stable (std 0.012). Checkpoint: `out/best_model.pt` (best gold fold 0.378).

## Remaining Action Items
- [x] All milestones done. Optional next: rebalance Behavior class; wire real Δt; multi-LLM ensemble relabel.
