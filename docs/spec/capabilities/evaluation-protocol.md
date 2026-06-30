# Evaluation protocol (capability)

> **Status:** authoritative for the two framings + the loss ablation grid;
> baselines (plain-RoBERTa-CE, BiLSTM-MTL) and number-sync still owed.
> Implementation: `src/pebble_llm/evaluation/`,
> `kaggle/finetuning-message/{r2-within-dist-cv,r2-corn-gce,r2-corn-only,r2-gce-only}/`.
> Owned by `../changes/001-initial-build/phase-5-evaluation-and-ablation.md`.

**What it covers:** the two honest framings reported side by side —
(1) **within-distribution 5-fold CV** on the 10k (apples-to-apples with the
paper: macro-F1 0.653 ±0.005 > paper 0.5098), and (2) **gold-holdout** (clinical
CSSRS held out): best ordinal config CORN+GCE macro-F1 **0.402 ±0.013**
(dual-head baseline 0.385; flat-CE 0.422). Metrics: macro-F1, QWK, MAE,
per-class F1 — all 5-fold with std.

**Loss ablation grid (gold-holdout 5-fold×10ep, complete):**

| | Focal | GCE |
|---|---|---|
| **CORAL** | dual 0.385 / Beh 0.183 | gce-only 0.399 / 0.229 |
| **CORN** | corn-only 0.410 / 0.250 | corn+gce 0.402 / 0.260 |

flat-CE (no ordinal head) 0.422 / 0.285 remains the macro leader on gold —
reported as the honest "ordinal has a cost under LLM→gold shift" finding.

**Baselines (same split/seed, 5-fold×10ep):** plain-RoBERTa-CE 0.346 / Beh 0.169
/ QWK 0.292; BiLSTM-MTL 0.378 / 0.181 / 0.396 — both weakest on macro (< dual
0.385), confirming the hierarchical post→sequence + ordinal architecture adds
value over a flat encoder and a BiLSTM-MTL.

**Still owed:** resolve the 0.385/0.357 number discrepancy to the canonical
rebalance run.

**Binds invariants:** I2 (gold-holdout disjoint), I5 (each cell cites its
kernel+log), I6 (QWK/MAE alongside F1).
