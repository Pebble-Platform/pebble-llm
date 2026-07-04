# Phase 2 — Subject-level splits & gold-holdout protocol

**Status:** mostly done (predates IDD init)
**Depends on:** phase 0 (invariant tests), phase 1 (assembled data)

**Goal:** splits are assigned by subject (deterministically) and the weak/LLM
train pool is kept strictly disjoint from the held-out clinical-gold eval pool —
so the measured benefit is honest (within-LLM 0.67 ≠ gold 0.385).

## Scope

- Subject-level split assignment: `src/pebble_llm/data/splits.py::assign_split`
  (same user ⇒ same split). Within-distribution 5-fold CV likewise folds by
  subject, not post.
- Gold-holdout wiring: clinical CSSRS labels are eval-only; LLM labels are
  train-only. See `PAPER-PLAN` §1, `docs/tasks/r2-beat-paper-dual-report.md`.
- OUT of scope: the metrics computed on these splits (phase 5).

## Exit criteria

- I1 (no subject leakage) and I3 (determinism) green — already true via
  `tests/test_splits.py`; alias into `tests/invariants/`.
- I2 (gold/train disjoint) green: the disjointness test passes on the real
  assembled pools.

## Verification (filled when phase formalized)

| # | Intent | Check | Where |
|---|---|---|---|
| 1 | Same subject ⇒ same split (I1) | `test_user_level_no_leakage` | CI, every PR |
| 2 | Train/gold disjoint (I2) | `test_gold_holdout_disjoint` | CI, every PR |

## Review notes

- **Risk:** the gold set is small (392 clinical test sequences); subject-level
  holdout shrinks effective eval size. Report CIs (paper §5 reviewer-risk).
- **Judgment call:** the gold protocol differs from the paper's original
  (label-by-user, Δt=0); this is disclosed in Limitations (phase 6), not hidden.
