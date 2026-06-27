# Evaluation protocol (capability — STUB)

> **Status:** stub. Authoritative detail lives in `src/pebble_llm/evaluation/`,
> `kaggle/finetuning-message/r2-within-dist-cv/`, and
> `PAPER-PLAN-text-ordinal-suicide.md` §5.
> Owned by `../changes/001-initial-build/phase-5-evaluation-and-ablation.md`.

**What it covers:** the two honest framings reported side by side —
(1) **within-distribution 5-fold CV** on the 10k (apples-to-apples with the
paper: macro-F1 0.653 ±0.005 > paper 0.5098), and (2) **gold-holdout** (clinical
CSSRS held out: macro-F1 0.385 → 0.418). Metrics: macro-F1, QWK, MAE, per-class
F1. Plus the baselines (plain-RoBERTa-CE, BiLSTM-MTL) and the loss/augment
ablation table the paper requires.

**Binds invariants:** I2 (gold-holdout disjoint), I6 (QWK/MAE alongside F1).
