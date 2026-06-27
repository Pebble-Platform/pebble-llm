# Ordinal modeling (capability — STUB)

> **Status:** stub. Authoritative detail lives in
> `kaggle/finetuning-message/r2-suicide-risk-dualhead/r2-suicide-risk-dualhead.py`,
> `src/pebble_llm/models/` (`heads.py`, `losses.py`), and
> `PAPER-PLAN-text-ordinal-suicide.md` §3 (contribution 1).
> Owned by `../changes/001-initial-build/phase-3-ordinal-modeling.md`.

**What it covers:** the encoder (MentalRoBERTa / NeoBERT, choice is
measurement-decided), the hierarchical dual-head (post → sequence), and the
**noise-robust ordinal loss** — CORN (per-threshold weights) + GCE (down-weights
low-confidence samples), which replaced CORAL+Focal and lifted gold Behavior-F1
0.183 → 0.317 while keeping ordinal structure (QWK ~0.39).

**Binds invariants:** I6 (ordinal-aware: QWK/MAE reported alongside F1).
