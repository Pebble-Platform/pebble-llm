# Phase 6 — IEEE paper, ethics & number-synced reports

**Status:** not started
**Depends on:** phases 1–5 (all numbers final)

**Goal:** a submittable IEEE draft whose every claim is backed by a phase-5
number and whose ethics/provenance section satisfies the clinical-track bar.

## Scope

- Draft per `PAPER-PLAN` §4 outline: Intro, Related Work (papers 42–57),
  Method (3 contributions + gold-holdout framing), Data & labeling, Experiments,
  Limitations & Ethics, Conclusion.
- **Ethics & provenance §:** r/SuicideWatch scrape method, ~9% content-filter,
  de-identification, single-LLM-labeling limitation, gold-protocol deviation.
- Reports (`docs/reports/*.{md,html}`) mirror the final canonical numbers.
- OUT of scope: any new experiment (those are phase 5 or a future change).

## Exit criteria

- Every headline number in the draft cites a phase-5 run/log (I5) and every
  model-comparison table carries QWK/MAE alongside macro-F1 (I6).
- The reviewer-risk rebuttals (paper §5) are each addressed in-text.
- Reports and paper agree on the canonical numbers (no 0.385/0.357 split).

## Verification (filled when phase formalized)

| # | Intent | Check | Where |
|---|---|---|---|
| 1 | No uncited headline number (I5) | report-lint: each metric cell links a source | CI report-lint |
| 2 | Ordinal metrics present (I6) | report-lint over paper tables | CI report-lint |
| 3 | Ethics section complete | manual clinical-track checklist sign-off | Sign-off |

## Review notes

- **This phase is mostly writing, but the long poles are upstream** (κ set,
  cleaned-pool retrain, baselines) — do not start the draft expecting those to
  be free; they are phase-4/5 blockers that gate §4/§5.
- **External blocker:** IEEE clinical/ethics requirements may need an
  institutional sign-off the engineering work can't produce — name the owner
  early so it doesn't stall submission.
