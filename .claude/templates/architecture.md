---
title: [Ticket Title] — Architecture
ticket: [ID]
status: draft
owner: [team or person]
date: [Auto]
spec: specs/tickets/[ID]/01-spec.md
---

# [Ticket Title] — Architecture Document

> **Scope rule — this is a *high-level* document.** It captures the *why* and the *shape* of the solution, nothing more. Concrete types, SQL, validation rules, file manifests, function signatures, and step-by-step implementation belong in `03-plan.md` and `04-task.md`. If a sentence here describes mechanical detail a reviewer cannot disagree with, move it downstream. Target length: **one screen per section, no more than ~150 lines total.**

## 1. Context & Goal

<!-- 2–4 sentences. Link back to the spec, state the gap between current and target state. -->

**Spec:** `specs/tickets/[ID]/01-spec.md`

**Single most important outcome:** [one sentence — the one thing that, if missed, makes the whole design a failure]

## 2. Architecture Decisions

<!-- One `ADR-xxx` per *real* architectural bet — the 2–5 decisions a reasonable engineer could disagree with. Obvious choices do not need ADRs. If you have more than 5 ADRs, you're writing the plan, not the design.

**Each ADR should include a small Mermaid diagram** — a sequence diagram, flowchart, or component box — whenever it helps a reviewer *see* the decision. A 6-line diagram contrasting "chosen flow" vs "rejected alternative" is worth a paragraph of prose. Skip the diagram only when the decision is purely a data-shape or policy choice that a picture would not clarify. -->

### ADR-001: [Decision title]

- **Decision:** [What was chosen, one sentence.]
- **Alternatives considered:**
  - [Option A] — [why rejected, one line]
  - [Option B] — [why rejected, one line]
- **Diagram:**

  ```mermaid
  %% Recommended: sequence diagram for flow decisions, flowchart for control-flow decisions,
  %% component diagram for module-placement decisions. Keep it under ~15 lines.
  sequenceDiagram
      actor Caller
      participant A as [Chosen component]
      participant B as [Downstream]
      Caller->>A: [request]
      A->>B: [delegation]
      B-->>A: [result]
      A-->>Caller: [response]
  ```

- **Rationale:** [Why the chosen option wins. Reference specific `REQ-xxx` or invariants from the spec where applicable.]
- **Trade-offs:** [What we give up. Be honest.]

### ADR-002: [Decision title]

<!-- Repeat as needed. Aim for 2–5 total. The Diagram field is optional per-ADR but strongly recommended for any decision that changes *where* code runs or *how* requests flow. -->

## 3. High-level Design

<!-- Describe the *shape* of the solution: what the key components are, where they sit, how data flows. One diagram plus short prose. Do NOT list columns, types, endpoint signatures, file paths, or line numbers — that is implementation and belongs in 03-plan.md. -->

```mermaid
[System / sequence / flowchart diagram — pick whichever best shows the new interaction]
```

**Key components:**

- **[Component name]** — [one-line role]
- **[Component name]** — [one-line role]

**How it fits together:** [2–3 sentences on the happy path — what happens when the feature is exercised normally]

**Touchpoints with existing systems:** [bullet list, one line each — "layer X now calls helper Y", not "method foo() now returns bar"]

## 4. Migration & Rollout

- **Approach:** [phased / feature-flagged / big-bang — one sentence why]
- **Feature flag / env gate:** [name, or "none"]
- **Rollback:** [one sentence — what "undo" looks like]
- **Backward compatibility:** [one sentence — is old behavior preserved for non-participants?]
