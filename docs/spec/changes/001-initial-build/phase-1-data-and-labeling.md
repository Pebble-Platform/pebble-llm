# Phase 1 — Data & LLM-labeling pipeline

**Status:** mostly done (predates IDD init)
**Depends on:** phase 0 (id-provenance for I2)

**Goal:** the combined ~10k ordinal dataset exists, assembled from CSSRS-500
clinical gold + av9ash + r/SuicideWatch scrape, weak-labeled by a single LLM,
de-identified and content-filtered, with documented provenance — and no raw
corpus or PII is committed.

## Scope

- LLM weak-labeling pipeline (single-model `gpt-5.4-mini`, conf ≥ 0.6) onto the
  ordinal taxonomy. See `PAPER-PLAN` §4, `src/pebble_llm/data/` (`external.py`,
  `build_dataset.py`, `taxonomy.py`), `docs/dataset-acquisition-plan.md`.
- Scrape provenance: r/SuicideWatch via pullpush, ~9% content-filtered,
  de-identification — documented for the ethics section.
- OUT of scope: split assignment (phase 2), label *quality* analysis (phase 4).

## Exit criteria

- The combined 10,072-sequence dataset `[4091, 3783, 711, 1487]` is reproducible
  from documented sources; the build runs end-to-end (`build_dataset.py`).
- Every committed file under `data/`/`kaggle/` is on the I4 allow-list; raw posts
  stay untracked.
- Provenance (sources, scrape method, filter rate, label model + threshold) is
  written where the paper's Data §4 / Ethics §6 can cite it.

## Verification (filled when phase formalized)

| # | Intent | Check | Where |
|---|---|---|---|
| 1 | No PII committed (I4) | `tests/invariants` data allow-list gate | CI, every PR |
| 2 | Dataset rebuilds to the documented class counts | `tests/test_build_dataset.py` + a build smoke run | CI + manual |

## Review notes

- **Hidden long pole disguised as a code task:** the κ-vs-gold analysis (phase 4)
  depends on a *recoverable overlap set* between LLM and gold labels — that
  recoverability is a phase-1 data-provenance decision. If the overlap isn't
  preserved at labeling time, phase 4 can't compute κ. Flag now.
- **Ethics blocker (needs owner):** the IEEE clinical track requires an explicit
  de-identification + content-filter writeup; this is non-engineering sign-off,
  not a code task.
