# Phase 5 — Evaluation, baselines & ablation

**Status:** partial
**Depends on:** phases 2–4

**Goal:** the two honest framings and the full ablation/baseline grid are
reported side by side, so each contribution is separable and each number traces
to a run.

## Scope

- **Within-distribution 5-fold CV** on the 10k (macro-F1 0.653 ±0.005 > paper
  0.5098) — framed as a *comparable protocol*, not the gated benchmark.
- **Gold-holdout** (clinical CSSRS held out): best ordinal config CORN+GCE
  macro-F1 0.385 → **0.402**, QWK, MAE, per-class F1. See
  `kaggle/finetuning-message/r2-within-dist-cv/`, `src/pebble_llm/evaluation/`,
  `PAPER-PLAN` §5.
- **Ablation (✅ 2×2 complete):** dual-CORAL 0.385/0.183 · flat-CE 0.422/0.285 ·
  gce-only 0.399/0.229 · corn-only 0.410/0.250 · corn+gce 0.402/0.260 → CORN is
  the primary lever (ADR-001). Still: ±LLM-augment.
- **Baselines:** plain-RoBERTa-CE, BiLSTM-MTL on the same split.
- OUT of scope: prose write-up (phase 6).

## Exit criteria

- Every cell of the ablation + baseline table is a real run with macro-F1, QWK,
  MAE reported (I6) and a cited log (I5).
- The 0.385/0.357 number discrepancy is resolved to the canonical (rebalance)
  run across all docs.
- Encoder and loss-family decisions (open decisions 1–2) are resolved on data
  and recorded as ADRs in `../../decisions/`.

## Verification

| # | Intent | Check | Where | Status |
|---|---|---|---|---|
| 1 | Honest framing, no benchmark overclaim (constraints §3) | report states "comparable within-dist protocol", not the gated benchmark | reports + PAPER-PLAN §2 | ✅ |
| 2 | Ordinal metrics on every comparison (I6) | QWK/MAE alongside macro-F1 in every ablation cell | `r2-corn-gce/corn-only/gce-only` logs | ✅ |
| 3 | Each ablation cell cites a run (I5) | 2×2 grid → kernel id + log per cell | `kaggle/finetuning-message/r2-{corn-gce,corn-only,gce-only}/out/` | ✅ |
| 4 | Baselines on common split | plain-RoBERTa-CE **0.346/Beh 0.169/QWK 0.292**; BiLSTM-MTL **0.378/0.181/0.396** (5-fold×10ep, same split/seed) — both weakest on macro (< dual 0.385) → hierarchical+ordinal arch adds value | `fabiocarava/r2-baseline-{roberta,bilstm}@1` · logs `kaggle/finetuning-message/r2-baseline-*/out/` | ✅ |
| 5 | Number-sync 0.385/0.357 → canonical | one run chosen across all docs | author decision | ⬜ owed |

## Review notes

- **Ablation grid done (✅):** 2×2 [CORAL/CORN × Focal/GCE] all real 5-fold runs;
  loss-family open decision #2 resolved → **ADR-001** (CORN primary lever).
- **Number-sync is a non-engineering blocker:** 0.385 (rebalance) vs 0.357
  (older spec) must be unified by the author choosing the canonical run before
  submission — name the owner.
- **Baseline gap:** BiLSTM-MTL + plain-RoBERTa-CE on the common split are not yet
  run (paper §3 item 3); these are the reviewer-expected comparison columns.
- **Gated-encoder caveat:** a *real* gated encoder needs an HF token (further
  work); until then "beat the paper" stays framed as comparable-protocol only.
