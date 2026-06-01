# Phase 2 — Taxonomy & Viability Gates

**Span:** Week 3
**Owners:** 3 annotators (2 days), AI eng (1 day)
**Strategy refs:** §3.2, §3.3, §3.4
**Depends on:** [Phase 1](01-data-collection-tooling.md) (tool built, 100+ labels)

## Objective

Freeze the taxonomy and decide which subjective dimensions survive — **before** the
expensive annotation pass. Changing these later forces a pipeline restart
(2–3 days now vs 2–3 weeks later).

## Tasks

- **Taxonomy pilot:** 100 messages, stratified by severity quartile (25/quartile),
  3 annotators label from scratch (no Gemini pre-fill, no anchoring). Compute pairwise
  confusion rates.
  - **Decision rule:** any two labels confused > 40% → merge. Likely candidates:
    frustration/anger, anxiety/confusion, exhaustion/sadness.
  - Finalize taxonomy; update the GoEmotions mapping table and annotation guidelines.
- **socialIsolation viability gate** (Krippendorff α on the pilot):
  - α < 0.5 → **drop**, replace with a Decision-Engine keyword heuristic.
  - 0.5 ≤ α < 0.6 → keep with relaxed MAE target 0.25; re-evaluate after first run.
  - α ≥ 0.6 → proceed normally.
- **receptivity viability gate** (same α thresholds):
  - α < 0.5 → prefer collapsing to a binary venting/seeking head (what the Decision
    Engine consumes) or a heuristic.
  - DailyDialog act-labels are noisy (rhetorical-question vents) — weight human
    annotations heavily.

## Exit gate

- Taxonomy frozen → update `src/pebble_llm/data/taxonomy.py`.
- socialIsolation / receptivity dispositions recorded in
  `configs/config.yaml > model.score_dims`.

## Decision point

These gates can permanently **remove model heads**. Lock before Phase 3 begins.

**Next:** [Phase 3 — Human Annotation](03-human-annotation.md)
