# Data & LLM-labeling (capability — STUB)

> **Status:** stub — pointer into current authoritative docs, not yet absorbed.
> Authoritative detail lives in `docs/dataset-acquisition-plan.md`,
> `PAPER-PLAN-text-ordinal-suicide.md` §4, and `src/pebble_llm/data/`
> (`external.py`, `build_dataset.py`, `taxonomy.py`).
> Owned by `../changes/001-initial-build/phase-1-data-and-labeling.md`; the PR
> that ships phase 1 replaces this stub with the as-built description.

**What it covers:** acquiring the corpora (CSSRS-500 clinical gold, av9ash,
r/SuicideWatch scrape via pullpush), the LLM weak-labeling pipeline
(single-model `gpt-5.4-mini`, conf ≥ 0.6) onto the ordinal taxonomy
(Indicator < Ideation < Behavior < Attempt), de-identification + content
filtering, and assembling the combined ~10k dataset.

**Binds invariants:** I4 (no raw corpus/PII committed), I5 (provenance).
