# Phase 7 — Serving Build & Integration

**Span:** Week 9
**Owners:** Backend + AI eng (4–5 days)
**Strategy refs:** §6.1 Steps 4–5, §8.1, §8.2
**Depends on:** [Phase 6](06-training-evaluation.md) (model passes eval; serving track chosen)

## Objective

Productionize the chosen serving track and integrate end-to-end.

## Tasks

- **Finalize Track A or B** and build the `/classify` container (FastAPI + Torch/ONNX
  Runtime). Add `min-instances=1` to eliminate cold starts on this latency-sensitive
  path. Deploy to staging.
  - **Track A (baseline):** GPU FP16 + FlashAttention, ~20–50ms, Cloud Run (L4) or Vertex.
  - **Track B (spike):** INT8 ONNX on CPU, ~50–150ms — only if the Week-8 spike succeeded.
- **Wire the backend:** classifier → Decision Engine → Gemini (sequential — generation
  consumes the routing decision). The Decision Engine adjusts path weights and passes a
  response-style directive to Gemini.
- **Shadow scoring:** score 10% of traffic with the single-call generator (computed,
  not used for routing) for the first 4 weeks. *(§8.2)*
- **Safety union-of-triggers** (§8.1): activate if ANY fire — classifier safetyFlag,
  keyword regex, or Gemini generation crisis heuristic. Log generation-heuristic events
  to `safety_events` and flag for review.
- **E2E tests** across all four routing paths + safety scenarios.
- **Experiment tracking** (§6.1 Step 5): every deployed version traces to its
  training-data snapshot + config + Protocol B eval. **No deploy without a completed
  Protocol B eval.** Rollback = repoint to the previous container/endpoint revision.

## Exit gate

- Staging clean across all paths + safety scenarios.
- Shadow scoring live; rollback path verified.

**Next:** [Phase 8 — Staged Rollout](08-staged-rollout.md)
