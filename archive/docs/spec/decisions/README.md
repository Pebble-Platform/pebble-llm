# Decisions — ADR register (spec layer)

Append-only architecture/method decision records. When a cross-phase open
decision (see `../changes/001-initial-build/README.md`) is resolved **on
evidence**, record it here as an ADR and stop tracking it as "open".

> **Existing log:** the pre-IDD Phase-0 open-question log lives at
> [`../../decisions.md`](../../decisions.md) (OQ2/3/5/6, dimension scope). It is
> the historical record; new method decisions are ADRs below.

## ADR shape

```markdown
## ADR-NNN — <title>
**Date:** YYYY-MM-DD · **Status:** accepted | superseded by ADR-MMM
**Context:** what forced the decision (the open question + its constraint).
**Decision:** what was chosen.
**Evidence:** the run/number/log that decided it (research = measurement, not opinion).
**Consequences:** what this commits us to; what it forecloses.
```

## Register

| ADR | Title | Status |
|---|---|---|
| [001](ADR-001-loss-family-corn-gce.md) | Ordinal loss family = CORN+GCE (resolves change 001 open decision #2) | accepted |
