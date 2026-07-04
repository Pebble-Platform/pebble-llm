# Splits & gold-holdout (capability — STUB)

> **Status:** stub. Authoritative detail lives in
> `src/pebble_llm/data/splits.py`, `tests/test_splits.py`, and the gold-holdout
> protocol description in `PAPER-PLAN-text-ordinal-suicide.md` §1.
> Owned by `../changes/001-initial-build/phase-2-splits-and-holdout.md`.

**What it covers:** subject/user-level split assignment (same user ⇒ same split,
deterministic), and the **gold-holdout protocol** that keeps the weak/LLM-labeled
train pool strictly disjoint from the held-out clinical-gold eval pool —
the framing that makes the measured benefit honest (within-LLM 0.67 ≠ gold 0.385).

**Binds invariants:** I1 (no subject leakage), I2 (gold/train disjoint),
I3 (deterministic). I1 and I3 are already enforced by `tests/test_splits.py`.
