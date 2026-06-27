# Phase 3 — Ordinal modeling + noise-robust loss

**Status:** mostly done (predates IDD init)
**Depends on:** phase 2 (splits), phase 0 (pinned stack)

**Goal:** a hierarchical dual-head model trained with a noise-robust ordinal
loss (CORN + GCE) that improves the rare Behavior class without abandoning
ordinal structure.

## Scope

- Encoder (MentalRoBERTa / NeoBERT — choice deferred to phase 5 measurement) +
  dual-head (post → sequence). See
  `kaggle/finetuning-message/r2-suicide-risk-dualhead/`, `src/pebble_llm/models/`.
- **Contribution 1 — CORN + GCE:** per-threshold weights (CORN) + low-confidence
  down-weighting (GCE), replacing CORAL+Focal. Result: gold Behavior-F1
  0.183 → 0.317 while QWK stays ~0.39. See `PAPER-PLAN` §3.
- Env-gated rebalance (`R2_BALANCE`, WeightedRandomSampler) — default behavior
  unchanged.
- OUT of scope: label cleaning (phase 4), the final ablation table (phase 5).

## Exit criteria

- The CORN+GCE run reproduces gold macro-F1 ≈ 0.418 and Behavior-F1 ≈ 0.317 on
  the pinned stack, with QWK reported (I6).
- A single Kaggle config runs within the 12h GPU cap (epochs ≤ 10).

## Verification (filled when phase formalized)

| # | Intent | Check | Where |
|---|---|---|---|
| 1 | Ordinal metrics reported (I6) | run log contains macro-F1 + QWK + MAE + per-class F1 | per result PR |
| 2 | Reproducible on pinned stack (I5) | re-run command reproduces within ±std | Sign-off, per result PR |

## Review notes

- **Risk:** CORN+GCE leads flat-CE only narrowly on macro-F1 (0.418 vs 0.422)
  but clearly on Behavior-F1; the contribution claim rests on Behavior + ordinal
  preservation, not on beating flat-CE overall — keep the framing exact (paper
  §3 resolves the "flat-CE > tri-objective" paradox).
- **Deferred decision:** encoder choice and CORN-only/GCE-only ablation move to
  phase 5.
