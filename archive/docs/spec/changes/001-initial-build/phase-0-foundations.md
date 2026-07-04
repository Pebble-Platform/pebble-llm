# Phase 0 — Foundations: reproducible runner + invariants encoded

**Status:** in progress
**Depends on:** —

**Goal:** the honest-evaluation seam is mechanically guaranteed before any
number counts — the leakage, gold-holdout, determinism, no-PII, and pinned-stack
invariants each have a permanent test/gate, and experiments run on a pinned,
reproducible stack.

## Scope

- Establish the **pinned Kaggle stack** as the only sanctioned GPU run config
  (`torch==2.5.1` / `torchvision==0.20.1` / `torchaudio==2.5.1` /
  `xformers==0.0.28.post3` / `transformers==4.48.2`); Kaggle default torch 2.10
  is broken for P100/NeoBERT. See `progress.md` Phase 0/5, `docs/run-guideline.md`.
- Create `tests/invariants/` and mirror the intent invariants there
  (`docs/intent/invariants.md` I1–I6). I1/I3 already exist in
  `tests/test_splits.py` — move/alias them; add I2, I4, I5 (and the I6 report-lint).
- Add the **CI spec-gate** (PR touching `src/**` or `kaggle/**` updates
  `docs/spec/capabilities/**` or carries `Spec-Impact: none`).
- OUT of scope: training/modeling changes (phase 3), data acquisition (phase 1).

## Exit criteria

- `tests/invariants/` exists and runs in CI on every PR; I1–I4 are **green**,
  I5 and I6 are green or explicitly skipped-with-reason (never silently absent).
- A gold-holdout disjointness test (I2) fails loudly if any example id appears
  in both the weak-label train pool and the clinical-gold eval pool.
- `git ls-files data/ kaggle/` returns only allow-listed tooling files (I4).
- A documented, runnable command reproduces a known run's macro-F1 within its
  reported ±std using the pinned stack (I5).
- The capability stubs `experiment-runner`, `splits-and-holdout` are flipped to
  authoritative.

## Verification (each criterion → an executable check)

| # | Intent | Check | Where |
|---|---|---|---|
| 1 | No subject leakage across splits (I1) | `pytest tests/invariants/test_no_subject_leakage.py` (today: `tests/test_splits.py::test_user_level_no_leakage`) | CI, every PR |
| 2 | Gold/train label pools disjoint (I2) | `pytest tests/invariants/test_gold_holdout_disjoint.py` — asserts empty id-intersection | CI, every PR |
| 3 | Splits deterministic given seed (I3) | `pytest tests/invariants/test_split_deterministic.py` (today: `test_split_is_deterministic`) | CI, every PR |
| 4 | No raw corpus/PII committed (I4) | CI step: `git ls-files data/ kaggle/ \| grep -vf .ci/data-allowlist` is empty | CI, every PR |
| 5 | GPU runs pin the stack (I5) | CI step greps `kaggle/**` pip blocks for the five pinned versions; fails on a floated version | CI, every PR |
| 6 | Headline runs reproduce within ±std (I5) | Manual gate: documented re-run command + log diff in the change PR | Sign-off checklist, per result PR |
| 7 | Behavior changes touch the spec (rule 5) | CI spec-gate: `src/**`/`kaggle/**` diff requires `docs/spec/capabilities/**` diff or `Spec-Impact:` trailer | CI, every PR |

## Review notes

- **Hidden long pole:** I2 (gold-holdout disjointness) needs a stable example-id
  scheme that survives the LLM-labeling → assembly pipeline; if ids are
  regenerated per build, the test can't detect contamination. Pin id provenance
  in phase 1.
- **Risk:** the pinned-stack grep (check 5) is brittle to formatting; keep the
  pip install lines in a single canonical block per kernel so one grep covers them.
- **Non-engineering blocker:** CI may not currently run on this repo (no
  `.github/workflows` confirmed for tests). Owner must stand up the CI runner, or
  these gates degrade to local pre-commit only — name this explicitly rather than
  assume CI exists.
