---
title: [Ticket Title] — Implementation Plan
ticket: [ID]
status: draft
owner: [team or person]
date: [Auto]
spec: specs/tickets/[ID]/01-spec.md
tdd: specs/tickets/[ID]/02-tdd.md
---

# [Ticket Title] — Implementation Plan

> **Scope rule — this is a *high-level* document.** It captures the *phases* of work, their order, and how they fit together — nothing more. File paths, function signatures, SQL, per-field validation, specific test names, and concrete task steps belong in `04-task.md`. If a sentence here describes mechanical detail a reviewer cannot disagree with, move it downstream. Target length: **~150 lines**, one screen per section.

## 1. Overview

<!-- 2–3 sentences linking back to spec + TDD. End with a single "Sequencing driver" sentence naming the main reason the phases are ordered the way they are. -->

**Spec:** `specs/tickets/[ID]/01-spec.md`
**TDD:** `specs/tickets/[ID]/02-tdd.md`

**Sequencing driver:** [one sentence — e.g., "DB migration must ship before the new code path reads it" or "Fail-closed env validation must land before the gate is wired in"]

## 2. Phases

<!-- 3–5 phases. Each phase is a logical slice that could (in principle) be reviewed and merged independently. More than 5 means you are listing tasks, not phases. Fewer than 2 means the work probably does not need a phased plan. -->

### Phase 1: [Name]

- **Purpose:** [one sentence — what this phase delivers]
- **Size:** S / M / L  (S ≤ 3 tasks, M = 4–8 tasks, L = 9+ tasks)
- **Depends on:** [prior phase(s), or "None"]
- **Exit criteria:**
  - [Verifiable bullet — what "done" looks like]
  - [Verifiable bullet]
- **Key risk:** [one line, or "none"]

### Phase 2: [Name]

<!-- Repeat. Aim for 3–5 phases total. -->

## 3. Phase Dependency Graph

<!-- One diagram. Use the `diagram` skill's complexity rules to pick ASCII or Mermaid. For 3–5 phases, ASCII is almost always enough. -->

```
Phase 1 → Phase 2 → Phase 3
             ↓
           Phase 4
```

## 4. Risks & Rollback

**Cross-phase risks:**

<!-- Risks that span phases. Per-phase risks stay inside §2. -->

- [Risk] — **Affects:** [phase(s)] — **Mitigation:** [one line, or "accepted"]

**Rollback posture:**

- **Per-phase:** [Are phases independently revertable? If not, name the coupling.]
- **Whole-ticket:** [One sentence — how to undo everything shipped here.]

## 5. Requirement Traceability

<!-- Every REQ-xxx from 01-spec.md MUST appear here at least once, mapped to the phase that delivers it. A REQ deferred via an open question cites §7 instead of leaving the row blank. -->

| REQ ID | Delivered by | Notes |
| --- | --- | --- |
| `REQ-001` | Phase 1 | [one-line how] |
| `REQ-002` | Phase 2 | [one-line how] |

## 6. Open Questions

<!-- Questions that would reshape the phase breakdown or ordering. Do NOT re-copy open questions from the TDD unless they change the plan. -->

- `OQ-001`: [Question] — **Status:** open / resolved — **Needs:** [who decides]

## 7. Out of Scope for This Plan

<!-- Things that belong in 04-task.md or a follow-up ticket. Short guard-rail list. -->

- [Item] — deferred to `04-task.md` (task-level detail)
- [Item] — follow-up ticket / explicit non-goal
