# Phase 9 — Monitoring & Iteration

**Span:** Ongoing (post-deployment)
**Owners:** AI eng + product
**Strategy refs:** §9, OQ4
**Depends on:** [Phase 8](08-staged-rollout.md) (100% rollout)

## Objective

Keep the classifier healthy against drift and recalibrate against distribution shift.

## Monitoring

- **Classifier–generator drift** — shadow scoring (first 4 weeks) then spot-checks.
- **Safety-flag agreement** across classifier, keyword regex, generation heuristic —
  disagreements logged, reviewed weekly.
- **Serving health (NeoBERT primary)** — endpoint p95/p99 latency, error rate, GPU/CPU
  utilization, cold-start frequency, OOM/restarts. Alert on regressions.
- **JSON validation failure rate** — backup (Gemini) path only; alert > 2%/1h.
- **Fallback rate** attributable to classifier timeouts/failures vs the Phase 1 baseline.
- **User-facing metrics** — session length, return rate, path distribution
  (LIGHTEN spike ⇒ suspect low severity scores).
- **Per-dimension score distributions** — weekly histograms; shifts indicate population
  change or model drift.

## Retraining cadence

- **Monthly:** append new silver labels; retrain if the dataset grew > 20% since last run.
- **Quarterly:** fresh **human** annotation (200–500, Protocol B methodology) — the
  irreducibly manual recalibration step.
- **Ad-hoc:** retrain immediately if production safety recall < 0.95, a critical safety
  misclassification surfaces, or (backup path) JSON validation failure > 5% sustained.

## Automation stance (OQ4)

Automate **retraining** after ~3 clean manual cycles. Keep **deployment** human-gated
indefinitely for any safety-bearing version — never auto-deploy without re-verifying
safety recall on a **fresh human-annotated** test set.

**Index:** [../phases.md](../phases.md)
