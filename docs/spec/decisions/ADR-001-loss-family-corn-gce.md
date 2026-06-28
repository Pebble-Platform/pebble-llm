## ADR-001 — Ordinal loss family: CORN + GCE (over CORAL+Focal and flat-CE)

**Date:** 2026-06-28 · **Status:** accepted
**Resolves:** change 001 open decision #2 (loss family). Owner phases: 3, 5.

**Context:** the original dual-head used `0.5·CORAL + 0.3·CE + 0.2·Focal` and
collapsed on the rare clinical Behavior class (gold-holdout Behavior-F1 0.183).
A plain flat-CE arm unexpectedly beat the tri-objective on gold (0.422 vs 0.385
macro), implying CORAL's shared-weight head and Focal's hard-example
up-weighting were *hurting* under noisy LLM labels with an LLM→gold
distribution shift. The decision had to be made on data, not intuition.

**Decision:** for the ordinal head, replace **CORAL → CORN** (per-threshold
weights; a noisy rare-class label no longer contaminates all thresholds) and
**Focal → GCE** (`q=0.7`; down-weights low-confidence/likely-noisy samples
instead of up-weighting them). The configuration `0.5·CORN + 0.3·CE + 0.2·GCE`
is the chosen ordinal model. When pure macro-F1 (no ranking requirement) is the
only target, **flat-CE remains the reported leader on gold** — stated as a
finding, not hidden.

**Evidence (gold-holdout 5-fold×10ep, same split/seed, I5/I6):**

| | Focal | GCE |
|---|---|---|
| **CORAL** | dual 0.385 / Beh 0.183 | gce-only 0.399 / 0.229 |
| **CORN** | corn-only 0.410 / 0.250 | corn+gce 0.402 / 0.260 |

flat-CE 0.422 / 0.285. Disentangled from the dual baseline: **CORN (head) is the
primary lever** (+0.025 macro / +0.067 Behavior); GCE contributes independently
but smaller (+0.014 / +0.046); the combination is sub-additive on macro yet best
on Behavior (0.260). Differences among the three variants are within fold std
(0.015–0.025). Provenance (Kaggle keeps every version immutably):
`phatneurondai/r2-corn-gce@2` (5-fold; @1 = 3-fold preview), `r2-corn-only@2`,
`r2-gce-only@1` — logs under `kaggle/finetuning-message/{r2-corn-gce,r2-corn-only,r2-gce-only}/out/`.

**Consequences:**
- The ordinal capability (`capabilities/ordinal-modeling.md`) is now authoritative
  on CORN+GCE; `heads.py`/`losses.py` carry CORN + GCE (env-gated
  `R2_ORDINAL_HEAD`, `R2_LOSS_TYPE`).
- The paper frames contribution 1 as "CORN+GCE > CORAL+Focal, keeps ordinal" plus
  the honest "flat-CE leads macro on gold (ordinal has a cost under shift)" finding.
- Open: a CORN-only vs CORN+GCE significance test (differences are within std);
  q-sweep (0.5) optional. Does not block the decision.
</content>
