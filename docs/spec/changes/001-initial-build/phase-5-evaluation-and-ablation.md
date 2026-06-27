# Phase 5 — Evaluation, baselines & ablation

**Status:** partial
**Depends on:** phases 2–4

**Goal:** the two honest framings and the full ablation/baseline grid are
reported side by side, so each contribution is separable and each number traces
to a run.

## Scope

- **Within-distribution 5-fold CV** on the 10k (macro-F1 0.653 ±0.005 > paper
  0.5098) — framed as a *comparable protocol*, not the gated benchmark.
- **Gold-holdout** (clinical CSSRS held out): macro-F1 0.385 → 0.418, QWK,
  MAE, per-class F1. See `kaggle/finetuning-message/r2-within-dist-cv/`,
  `src/pebble_llm/evaluation/`, `PAPER-PLAN` §5.
- **Ablation:** dual-CORAL / flat-CE / CORN+GCE; CORN-only vs GCE-only; ±LLM-augment.
- **Baselines:** plain-RoBERTa-CE, BiLSTM-MTL on the same split.
- OUT of scope: prose write-up (phase 6).

## Exit criteria

- Every cell of the ablation + baseline table is a real run with macro-F1, QWK,
  MAE reported (I6) and a cited log (I5).
- The 0.385/0.357 number discrepancy is resolved to the canonical (rebalance)
  run across all docs.
- Encoder and loss-family decisions (open decisions 1–2) are resolved on data
  and recorded as ADRs in `../../decisions/`.

## Verification (filled when phase formalized)

| # | Intent | Check | Where |
|---|---|---|---|
| 1 | Honest framing, no benchmark overclaim (constraints §3) | report states "comparable within-dist protocol", not the gated benchmark | review, per PR |
| 2 | Ordinal metrics on every comparison (I6) | report-lint over the metric tables | CI report-lint |
| 3 | Each number cites a run (I5) | every table cell links a kernel id + log | review |

## Review notes

- **Number-sync is a non-engineering blocker:** 0.385 (rebalance) vs 0.357
  (older spec) must be unified by the author choosing the canonical run before
  submission — name the owner.
- **Baseline gap:** BiLSTM-MTL + plain-RoBERTa-CE on the common split are not yet
  run (paper §3 item 3); these are the reviewer-expected comparison columns.
- **Gated-encoder caveat:** a *real* gated encoder needs an HF token (further
  work); until then "beat the paper" stays framed as comparable-protocol only.
