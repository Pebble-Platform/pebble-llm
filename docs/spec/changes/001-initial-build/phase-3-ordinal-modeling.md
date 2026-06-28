# Phase 3 — Ordinal modeling + noise-robust loss

**Status:** done (loss/head verified 5-fold; encoder choice deferred to phase 5)
**Depends on:** phase 2 (splits), phase 0 (pinned stack)

**Goal:** a hierarchical dual-head model trained with a noise-robust ordinal
loss (CORN + GCE) that improves the rare Behavior class without abandoning
ordinal structure.

## Scope

- Encoder (MentalRoBERTa / NeoBERT — choice deferred to phase 5 measurement) +
  dual-head (post → sequence). See
  `kaggle/finetuning-message/r2-suicide-risk-dualhead/`, `src/pebble_llm/models/`.
- **Contribution 1 — CORN + GCE:** per-threshold weights (CORN) + low-confidence
  down-weighting (GCE), replacing CORAL+Focal. Result (5-fold×10ep): gold macro-F1
  0.385 → **0.402**, Behavior-F1 0.183 → **0.260**, QWK **0.361**. See `PAPER-PLAN` §3.
- Env-gated rebalance (`R2_BALANCE`, WeightedRandomSampler) — default behavior
  unchanged.
- OUT of scope: label cleaning (phase 4), the final ablation table (phase 5).

## Exit criteria

- ✅ The CORN+GCE run reproduces gold macro-F1 **0.402 ±0.013** and Behavior-F1
  **0.260** on the pinned stack, QWK 0.361 reported (I6).
- ✅ A single Kaggle config runs within the 12h GPU cap (epochs ≤ 10) — 5-fold×10ep ≈ 8.8h.

## Verification

| # | Intent | Check | Where | Status |
|---|---|---|---|---|
| 1 | Ordinal metrics reported (I6) | log has macro-F1 0.4022±0.0132 + QWK 0.361 + MAE + per-class (Beh 0.260) | `kaggle/finetuning-message/r2-corn-gce/out/r2-corn-gce.log` | ✅ |
| 2 | Reproducible on pinned stack (I5) | 5-fold mean reported with std 0.0132; kernel `phatneurondai/r2-corn-gce` v2 | same log | ✅ |
| 3 | CORN vs GCE disentangled | 2×2 grid (corn-only 0.410/0.250, gce-only 0.399/0.229) | `r2-corn-only/out`, `r2-gce-only/out` | ✅ → ADR-001 |

## Review notes

- **Honest framing (corrected):** CORN+GCE does **not** beat flat-CE on macro
  (0.402 < 0.422); the contribution rests on (a) beating the dual CORAL+Focal
  baseline (+0.017 macro / +0.077 Behavior) and (b) preserving ordinal structure.
  The "flat-CE > tri-objective" paradox is reported as a finding, not hidden.
  (An earlier 3-fold preview overstated this as 0.418/0.317 — corrected to the
  5-fold numbers.)
- **Resolved:** CORN-only/GCE-only ablation ran → **CORN is the primary lever**;
  recorded as ADR-001 (open decision #2, loss family).
- **Deferred:** encoder choice still moves to phase 5.
