# Phase 4 — Label quality: ordinal-aware CL + label-shift + κ

**Status:** partial (riskiest open subsystem — Behavior-class collapse)
**Depends on:** phase 1 (label provenance), phase 3 (a trained model)

**Goal:** the LLM→clinical-gold label gap is quantified and corrected — turning
the ~0.28 weak-supervision noise from an unexplained number a reviewer rejects
into a measured, addressed quantity.

## Scope

- **Contribution 3 — ordinal-aware Confident Learning:** confident-joint
  weighted by `|ỹ−ŷ|²` (cleans 100% far errors Behavior→Indicator, keeps 78%
  adjacent-borderline; flags 35.8% of Behavior labels suspect). See `PAPER-PLAN`
  §3, `docs/tasks/r2-method-improvements-for-contribution.md`.
- **Contribution 2 — label-shift correction:** measured `π_gold/π_train`
  Behavior = 3.0×; post-hoc Logit-Adjustment lifts Behavior-F1 0.357 → 0.41
  (oracle 0.44), 0 retrain.
- **κ-vs-gold + confusion:** Cohen's κ on the LLM/gold overlap set + LLM-vs-gold
  confusion matrix (the label-quality table IEEE requires).
- OUT of scope: the full baseline/ablation table (phase 5).

## Exit criteria

- κ(LLM, gold) and the LLM-vs-gold confusion matrix are computed on a documented
  overlap set and written where the paper's §4 can cite them.
- The ordinal-CL cleaning and the label-shift correction each have a reproducible
  artifact (Kaggle diag run / local numpy) with its number.

## Verification (filled when phase formalized)

| # | Intent | Check | Where |
|---|---|---|---|
| 1 | κ + confusion computed | artifact + number in `docs/papers`/`docs/reports` | per result PR |
| 2 | Cleaning/correction reproducible (I5) | documented re-run reproduces the reported lift | Sign-off |

## Review notes

- **Biggest project risk lives here.** Behavior-F1 0.18 is the macro-F1 drag and
  the clinical weak spot (missing "planning"); the three levers (CORN+GCE,
  logit-adjust, ordinal-CL) are verified individually but the *cleaned-pool
  retrain* (B-Arm2) is not yet run — that's the open item.
- **Blocking dependency:** κ needs the LLM/gold overlap set recovered (see
  `docs/tasks/enrich-suicide-risk-dataset.md`) — a data-provenance task, owner
  TBD, must resolve before §4 can be written.
