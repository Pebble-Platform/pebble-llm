# Capabilities — current truth (spec layer)

One file per capability, describing **what the system does right now** — not how
it was built (that's `../changes/`) and not why (that's `../../intent/`). This
directory is the target of the CI spec-gate: a PR that changes behavior updates
the matching capability file in the same PR.

## Lifecycle of a capability file

1. **Stub** — names the design doc(s) that currently hold its authoritative
   detail and the change that builds/owns it. The design docs remain
   authoritative.
2. **Authoritative** — the PR that ships the capability's first change under
   IDD moves the relevant design content here (updated to match what was
   actually built) and leaves a pointer at the old design-doc section.
3. **Living** — every subsequent behavior change updates this file in the same
   PR (WORKFLOW.md rule 5 + spec-gate).

> **Scaffold note:** this repo is research and was substantially built before
> IDD init. These stubs are *current-truth pointers* into the docs that already
> describe each capability; they become authoritative as change `001` phases
> formalize them. Nothing was moved at init.

## Index

| Capability | File | Seeded from (current authoritative docs) | Owned by | Status |
|---|---|---|---|---|
| Data & LLM-labeling | [data-and-labeling.md](data-and-labeling.md) | `docs/dataset-acquisition-plan.md`, PAPER-PLAN §4, `src/pebble_llm/data/` | 001 / phase 1 | stub |
| Splits & gold-holdout | [splits-and-holdout.md](splits-and-holdout.md) | `src/pebble_llm/data/splits.py`, `tests/test_splits.py`, PAPER-PLAN §1 | 001 / phase 2 | stub |
| Ordinal modeling | [ordinal-modeling.md](ordinal-modeling.md) | `kaggle/finetuning-message/r2-suicide-risk-dualhead/`, `src/pebble_llm/models/`, PAPER-PLAN §3 (contrib 1) | 001 / phase 3 | stub |
| Label quality | [label-quality.md](label-quality.md) | PAPER-PLAN §3 (contrib 2–3), `docs/tasks/r2-method-improvements-for-contribution.md` | 001 / phase 4 | stub |
| Evaluation protocol | [evaluation-protocol.md](evaluation-protocol.md) | `src/pebble_llm/evaluation/`, `kaggle/finetuning-message/r2-within-dist-cv/`, PAPER-PLAN §5 | 001 / phase 5 | stub |
| Experiment runner | [experiment-runner.md](experiment-runner.md) | `kaggle/`, `scripts/`, `docs/run-guideline.md`, `progress.md` (pinned stack) | 001 / phase 0 | stub |
| Paper & reporting | [paper-and-reporting.md](paper-and-reporting.md) | `docs/papers/`, `docs/reports/`, `docs/related-work-*.md` | 001 / phase 6 | stub |
| Serving (deferred) | [serving.md](serving.md) | `src/pebble_llm/serving/`, `pebble-finetuning-strategy-v3.md` §3–4 | out of scope (further work) | stub |
| Voice / multimodal (adjacent) | [voice-multimodal.md](voice-multimodal.md) | `docs/voice-*.md`, `notebooks/` voice kernels, `data/voice/` | adjacent stream | stub |
