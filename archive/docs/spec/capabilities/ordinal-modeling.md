# Ordinal modeling (capability)

> **Status:** authoritative for the loss/head; encoder choice still
> measurement-deferred (phase 5). Implementation:
> `kaggle/finetuning-message/{r2-corn-gce,r2-corn-only,r2-gce-only}/`,
> `src/pebble_llm/models/` (`heads.py`, `losses.py`).
> Owned by `../changes/001-initial-build/phase-3-ordinal-modeling.md`.

**What it covers:** the encoder (MentalRoBERTa / NeoBERT, choice is
measurement-decided), the hierarchical dual-head (post → sequence), and the
**noise-robust ordinal loss** — CORN (per-threshold weights, replaces CORAL's
shared weight) + GCE (down-weights low-confidence/noisy samples, replaces Focal).

**Current truth (gold-holdout, 5-fold×10ep, kernel `r2-corn-gce` v2):** CORN+GCE
gold macro-F1 **0.402 ±0.013**, Behavior-F1 **0.260**, QWK **0.361** — beats the
prior dual-head CORAL+Focal (0.385 / 0.183) by +0.017 macro / +0.077 Behavior
while keeping ordinal structure. It does **not** beat flat-CE on macro (0.422):
flat-CE (no ordinal head) leads overall on gold; CORN+GCE is the best *ordinal*
configuration — used when ordinal ranking (QWK) is required.

**Ablation 2×2 [head × 3rd-loss] (same split/seed) — disentangles the gain:**

| | Focal | GCE |
|---|---|---|
| **CORAL** | dual 0.385 / 0.183 | gce-only 0.399 / 0.229 |
| **CORN** | corn-only 0.410 / 0.250 | corn+gce 0.402 / 0.260 |

**CORN (head) is the primary lever** (+0.025 macro / +0.067 Behavior vs dual);
GCE contributes independently but smaller (+0.014 / +0.046); the combination is
sub-additive on macro yet best on the rare Behavior class. Differences among the
three variants are within fold std (0.015–0.025). See ADR-001.

**Binds invariants:** I5 (each number cites its kernel+log), I6 (ordinal-aware:
QWK/MAE reported alongside F1).
