# Phased Plan — per-phase files

One file per phase, derived from [`../../pebble-finetuning-strategy-v3.md`](../../pebble-finetuning-strategy-v3.md).
The overview table + cross-phase gates live in [`../phases.md`](../phases.md).

| # | Phase | Span |
|---|---|---|
| 0 | [Pre-work & Foundations](00-prework-foundations.md) | Week 0 |
| 1 | [Data Collection & Tooling](01-data-collection-tooling.md) | Weeks 1–2 |
| 2 | [Taxonomy & Viability Gates](02-taxonomy-viability-gates.md) | Week 3 |
| 3 | [Human Annotation](03-human-annotation.md) | Weeks 4–5 |
| 4 | [Safety Data](04-safety-data.md) | Week 6 |
| 5 | [Dataset Prep & Transfer Pre-training](05-dataset-prep-pretrain.md) | Week 7 |
| 6 | [Multi-task Training & Evaluation](06-training-evaluation.md) | Week 8 (+10) |
| 7 | [Serving Build & Integration](07-serving-integration.md) | Week 9 |
| 8 | [Staged Rollout](08-staged-rollout.md) | Weeks 11–14 |
| 9 | [Monitoring & Iteration](09-monitoring-iteration.md) | Ongoing |

> Phases are gated — do not advance until the exit criteria pass. The Week-10
> iteration buffer is folded into Phase 6. Several gates can terminate or redirect
> the project; see the cross-phase gate table in `../phases.md`.
