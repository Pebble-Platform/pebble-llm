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

## Results so far
- **Run B (gold + balance) — VALID:** GOLD macro-F1 **0.3849** ±0.007 (baseline 0.3569, +0.028), QWK 0.398
  (+0.020), MAE 0.822 (better), val-on-LLM 0.666. Per-class gold F1: Indicator 0.502 · Ideation 0.480 ·
  **Behavior 0.183** (still the bottleneck) · Attempt 0.374. Rebalance helps globally; Behavior ceiling is now
  a LABEL-QUALITY problem (634 noisy LLM labels), not sampling. Reports: `docs/reports/r2-ab-results.{md,html}`.
- **Run A (within-dist) — failed twice on a data-mount bug, re-running v3:**
  - v1: explicit `R2_DATA` path wrong → Zenodo fallback → 392 only.
  - v2: `*/sequences.csv` glob (one level) → empty → Zenodo → 392 (CV 0.197, invalid).
  - **Root cause (diagnostic kernel `r2-diag`):** the dataset mounts at
    `/kaggle/input/datasets/fabiocarava/r2-cssrs-combined-10k/sequences.csv` (3 levels deep), so a one-level
    glob misses it; `**/sequences.csv` (recursive) finds it. **Fix:** recursive glob in both `load_cssrs` +
    `_combined_path`. v3 RUNNING.
- **Within-dist proxy (interim):** Run B val-on-LLM 0.666 > paper 0.5098.

- 2026-06-24 — **Switched Kaggle account** (fabiocarava hit GPU quota → `pathnguyen`). CLI auths via
  `~/.kaggle/access_token` (overwrote with new KGAT_ token; old backed up). Re-uploaded the 10k as private
  dataset `pathnguyen/r2-cssrs-combined-10k`; re-pushed Run A as `pathnguyen/r2-within-dist-cv-10k-balanced`
  (v1, RUNNING) with the recursive-glob fix. Run B already valid on the old account — not re-run.

## ✅ RUN A COMPLETE (2026-06-26): within-dist CV = 0.653 > paper 0.5098 — BEAT PAPER (clean number)
On the phone-verified account `phatneurondai`, Run A (`r2-within-dist-cv-10k-balanced`) **COMPLETED**. It loaded the
**full 10,072 sequences** `[4091, 3783, 711, 1487]` from the mounted dataset (recursive-glob fix worked — no Zenodo
392 fallback). **5-fold within-distribution CV macro-F1 = 0.6530 ±0.0048** (folds [0.649, 0.660, 0.656, 0.654, 0.646]).
→ **vs paper 0.5098: +0.143 (+28% rel) — we beat the paper on its own within-distribution framing**, replacing the
earlier val-on-LLM 0.666 proxy with the clean apples-to-apples number. (Caveat: comparable protocol on our enriched
10k, not the paper's exact gated benchmark — frame as "method beats the paper's reported number on a comparable
within-distribution protocol".) Log: `kaggle/finetuning-message/r2-within-dist-cv/out/r2-within-dist-cv-10k-balanced.log`.

### ✅ BLOCKER RESOLVED (2026-06-25): switched to phone-verified account `phatneurondai`
User provided a new, **phone-verified** Kaggle account `phatneurondai` (GPU Tesla P100 + Internet both confirmed
working via a probe kernel — `torch.cuda.is_available()=True`, urllib fetch HTTP 200). Re-uploaded the 10k as
`phatneurondai/r2-cssrs-combined-10k` and re-pushed Run A with the recursive-glob fix + epochs 10 + balance ON.
(Account lineage + verification gotcha saved to memory `kaggle-run-needs-token`.)

## ⚠️ (HISTORICAL) BLOCKER (2026-06-24): pathnguyen not phone-verified
Run A on `pathnguyen` ERRORed at pip install — **no internet in the kernel** (`Temporary failure in name
resolution` → torch install failed). Kaggle disables Internet + GPU for **non-phone-verified** accounts even
when `enable_internet: true` is requested. → **User must phone-verify `pathnguyen`** (Kaggle → Settings →
Phone verification), then re-enable GPU+Internet. Then re-push Run A. (Offline workaround = pre-upload torch
wheels + the HF model as datasets + run on GPU — but GPU also needs verification, so verification is required.)

## Remaining Action Items
- [ ] **User: phone-verify `pathnguyen` on Kaggle** (unlocks Internet + GPU for kernels)
- [ ] Re-push Run A (pathnguyen) → confirm it loaded 10k → record clean within-dist CV macro-F1 vs 0.5098
- [ ] Update `docs/reports/r2-ab-results.{md,html}` with the clean Run A number + final verdict
- [ ] (cleanup) delete the throwaway `r2-diag` kernel/dir
