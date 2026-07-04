# Phase 8 — Staged Rollout

**Span:** Weeks 11–14
**Owners:** AI eng + product
**Strategy refs:** §10 W11–14, §8.2
**Depends on:** [Phase 7](07-serving-integration.md) (staging clean, shadow live)

## Objective

Ship gradually with safety monitoring at every step.

## Tasks

- **Week 11 — Rollout 10%.** Shadow scoring active. Monitor safety agreement, path
  distribution, serving health, latency.
- **Week 12 — Rollout 50%.** Review Week 11 data. **Proceed only if no safety
  regressions and path-distribution shift < 10% relative.**
- **Weeks 13–14 — Rollout 100%.** Shadow scoring continues 2 more weeks.

## Shadow-comparison thresholds (§8.2)

- Classifier vs generator severity disagreement > 0.3 for > 5% of weekly messages →
  investigate (stale classifier, prompt change, population shift).
- LIGHTEN spike > 10% relative → suspect the classifier systematically underscores severity.
- Treat divergence as a **signal to investigate**, never proof the classifier is wrong —
  classifier (NeoBERT) and generator (Gemini) are different model families, so agreement
  is a weak correctness proxy.
- **Discontinue shadow scoring only** when classifier/generator agree on severity within
  0.2 for > 90% of messages **and** the latest human audit is within target — never on
  generator agreement alone.

## Exit gate

- 100% traffic.
- No safety regression; path-distribution shift within bounds.

**Next:** [Phase 9 — Monitoring & Iteration](09-monitoring-iteration.md)
