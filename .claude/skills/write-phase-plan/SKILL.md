---
name: write-phase-plan
description: "[Planning] Generate a high-level phased implementation plan from a spec + TDD. Produces a roadmap (3–5 phases, dependencies, exit criteria, REQ traceability) — NOT a file-level implementation plan. Implementation detail (file paths, signatures, SQL) lives in 04-task.md. Use in na-plan Step 4 to produce 03-plan.md. Triggers on: 'write phase plan', 'phase plan', 'rollout plan', 'high-level implementation plan', 'phased roadmap'."
argument-hint: "<ticket ID>"
---

# write-phase-plan — high-level phased roadmap

## Quick summary

**Goal:** Produce a roadmap that sequences work from a spec + TDD into **3–5 phases**, each with clear purpose, dependencies, size, and exit criteria. No file paths, no signatures, no SQL — those belong in `04-task.md`.

**Workflow:** Read inputs → break into phases → map dependencies → trace requirements → capture risks → write.

**Key rules:**
- Target **~150 lines**. If you exceed 200, you are writing tasks, not a plan.
- **3–5 phases.** More means you're task-listing; fewer means the work doesn't need a plan.
- **No mechanical detail** — no file paths, no function signatures, no `CREATE TABLE`, no specific test file names.
- **Every `REQ-xxx` must map to exactly one phase** (or to §7 Out of Scope if explicitly deferred).

---

## Inputs

- `specs/tickets/[ID]/01-spec.md` — requirements, acceptance criteria, invariants
- `specs/tickets/[ID]/02-tdd.md` — ADRs, high-level design, migration strategy
- **Template:** `.claude/templates/phase-plan.md` (authoritative — do not reorder, rename, or skip sections)

## Process

### Step 1 — Read both input documents

Read `01-spec.md` first. Note every `REQ-xxx` and whether it's MUST or SHOULD. Read `02-tdd.md` next. Note the `ADR-xxx` decisions and the §4 Migration & Rollout guidance — that section often implies the phase breakdown directly.

**Fail fast:** if either input is missing, stop and report. Do not attempt to plan from the spec alone or from the TDD alone.

### Step 2 — Break the work into 3–5 phases

A phase is a logical slice that could, in principle, be reviewed and merged independently. Each phase must satisfy all three:

1. **Delivers observable value OR unblocks the next phase** (no "setup" phases that just move code around with nothing to show)
2. **Has a verifiable exit criterion** (how does a reviewer know it's done?)
3. **Names its dependencies** (which prior phases must complete first)

**Common phase patterns — pick one as a starting point:**

| Shape of work | Typical phases |
| --- | --- |
| New feature | foundations → core behavior → polish → rollout |
| Migration | dual-write → cut-over → cleanup |
| Refactor | introduce new abstraction → migrate callers → remove old |
| New integration | contract freeze → implementation → testing → production rollout |
| Config / env change | schema + validation → callers → enforcement → cleanup |

If you find yourself writing **more than 5 phases**, collapse related ones — you are listing tasks, not phases. If you find yourself writing **fewer than 2**, the work probably does not need a phased plan and should be a single change.

### Step 3 — Size each phase

Mark each phase **S / M / L** using task-count buckets:

- **S** — ≤ 3 tasks, rough effort < 1 day
- **M** — 4–8 tasks, rough effort 1–3 days
- **L** — 9+ tasks, rough effort 3+ days

A plan with **more than one L phase** is a smell — try splitting the L phases further before writing them down.

### Step 4 — Draw the phase dependency graph

§3 needs a diagram showing which phases block which. **Use the `diagram` skill's complexity rubric** to pick ASCII vs Mermaid:

- 3–4 phases, linear or one fork → ASCII (score ≤ 6)
- 5 phases with multiple dependencies → Mermaid flowchart (score 7+)

ASCII is usually enough for a phase graph. Reserve Mermaid for plans with genuine parallelism or multi-way dependencies.

### Step 5 — Trace every REQ to a phase

Build the §5 traceability table. Every `REQ-xxx` from `01-spec.md` must map to exactly one phase — the phase that *delivers* the requirement (not every phase that touches code related to it).

For a SHOULD deferred via an open question, cite `§7 Out of Scope` instead of leaving the row blank.

### Step 6 — Capture cross-phase risks and rollback

**Cross-phase risks** go in §4 — risks that span multiple phases or only emerge after multiple phases have landed. Per-phase risks stay inside §2 as one-liners.

**Rollback posture** must name two things:

1. Whether phases are **independently revertable** — if Phase 3 ships and Phase 2 needs rollback, can you revert Phase 2 without also reverting Phase 3? If not, explain the coupling.
2. **Whole-ticket rollback** — one sentence on how to undo everything shipped.

## Hard rules — what NOT to write

- **No file paths.** Not in §2, not in §3, not anywhere. Paths live in `04-task.md`.
- **No function signatures, TypeScript type blocks, or interface declarations.**
- **No SQL bodies**, no `CREATE TABLE`, no migration DDL. Migration *strategy* (dual-write, big-bang) is fine in phase purpose; the SQL belongs in `04-task.md`.
- **No per-field validation or error code tables.**
- **No specific test file names** (`foo.test.ts`). Test *strategy* at a phase level ("Phase 3 adds integration tests for the gate") is fine.
- **No `file.ts:123` citations.** Line numbers are implementation detail.
- **Do NOT re-derive ADRs from the TDD.** The plan references ADRs by ID; it does not re-argue them.
- **Do NOT list tasks inside a phase.** A phase is a *bundle* of tasks; listing them here means `04-task.md` has nothing left to do.

## Output

Write to `specs/tickets/[ID]/03-plan.md`, following `.claude/templates/phase-plan.md` section-for-section. Do not reorder, rename, or add sections. Set `status: draft` in the frontmatter.

After writing, the caller (Step 4 of `na-plan`) will run verification checks. Do not try to self-verify — just produce the document and exit.
