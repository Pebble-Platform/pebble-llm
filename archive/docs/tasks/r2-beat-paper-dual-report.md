# R2 — beat-the-paper: dual report (within-dist + gold) + Behavior rebalance

- **Slug:** r2-beat-paper-dual-report
- **Status:** in-progress
- **Created:** 2026-06-24  ·  **Updated:** 2026-06-24
- **Owner:** Fabio / Claude

## Goal
Push R2 metrics toward / above the paper's 0.5098 macro-F1, on TWO honest framings:
(1) **within-distribution 5-fold CV** on the 10k (apples-to-apples with the paper), and
(2) **gold-holdout** (clinical CSSRS-500 held out) improved over the current 0.3569 — primarily by
**rebalancing the Behavior class** (only 6.5% of the pool, the macro-F1 drag). Produce a dual report.

## Requirements & Constraints
- **Functional:** add class-balanced sampling (env `R2_BALANCE`); run two Kaggle configs:
  Run A = within-dist CV on 10k + balance (vs paper); Run B = gold-holdout + balance (vs 0.3569).
- **Constraints:** keep changes surgical + env-gated (default behavior unchanged); stay under Kaggle 12h GPU
  cap (epochs ≤10); reuse the private dataset `fabiocarava/r2-cssrs-combined-10k`.
- **Non-goals (this round):** real gated encoder (needs HF token), multi-LLM ensemble relabel (needs more
  keys), real Δt wiring — noted as further work, not blocking.

## Milestones
- [ ] M1 — Add env-gated Behavior rebalance (WeightedRandomSampler) to train_fold
- [ ] M2 — Local CPU smoke: balance + both eval modes run
- [ ] M3 — Run A kernel (within-dist CV on 10k + balance) → vs paper 0.5098
- [ ] M4 — Run B kernel (gold-holdout + balance) → vs 0.3569
- [ ] M5 — Dual report: update HTML report with both numbers + verdict

## Decision Log
- **2026-06-24 — Two framings, both reported:** paper's 0.5098 is within-distribution CV; our 0.3569 is the
  stricter clinical gold-holdout. "Beat paper" means different things on each → report both. Insight:
  val-on-LLM was 0.638 > 0.5098, so within-dist may already beat the paper.
- **2026-06-24 — Behavior rebalance via WeightedRandomSampler (1/class_count), env `R2_BALANCE`:** Behavior is
  6.5% of pool and macro-F1 averages per-class → lifting its recall is the highest-ROI lever needing no new
  data. Keep the existing focal loss. Rejected: synthetic oversampling/SMOTE (text), targeted Behavior
  scraping (Behavior is rare in the wild → expensive), heavier α-only (sampler balances batches directly).
- **2026-06-24 — Two parallel kernels (gold + within-dist):** halves wall-clock vs sequential; ~18 GPU-h total
  fits the weekly quota. Each kernel dir sets its own mode via the IS_KAGGLE env block.

## Open Questions
<!-- none blocking; established techniques -->

## Research Findings
<!-- (none needed) -->

## Completed Work
- 2026-06-24 — Diagnosed levers from the gold-holdout run (Behavior 6.5%, LLM-label gap 0.28, val 0.638>paper).
- 2026-06-24 — M1: added `R2_BALANCE` WeightedRandomSampler (inverse-freq) to train_fold + per-class F1 in
  evaluate/prints (notebook + kaggle copies).
- 2026-06-24 — M2: local CPU smoke — both modes (within-dist CV + gold-holdout) run with balance + per-class F1.
- 2026-06-24 — M3/M4: pushed TWO parallel kernels, both RUNNING:
  - Run A (within-dist, vs paper): `fabiocarava/r2-within-dist-cv-10k-balanced` — default 5-fold CV on the full
    10k (`R2_DATA`=/kaggle/input/...), balance ON, epochs 10.
  - Run B (gold-holdout, vs 0.3569): `fabiocarava/r2-suicide-risk-dual-head-mentalroberta` v7 — gold-holdout +
    balance, epochs 10.

## Remaining Action Items
- [ ] Implement `R2_BALANCE` WeightedRandomSampler in train_fold (notebook + kaggle copy)
- [ ] Smoke both modes locally
- [ ] Create within-dist kernel dir; configure both kernels; push both
- [ ] Poll → retrieve → dual report
