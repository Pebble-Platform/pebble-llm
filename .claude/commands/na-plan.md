---
name: na-plan
description: "Phase 1: Planning workflow. Produces 01-spec.md, 02-tdd.md, 03-plan.md, and 04-task.md for a ticket by composing existing planning skills and agents."
allowed_tools: ["Skill", "Agent", "Read", "Write", "Bash"]
---

# /na-plan — Phase 1: Planning

Ticket ID: $ARGUMENTS

## Goal

Produce four planning documents for ticket **$ARGUMENTS** in `specs/tickets/$ARGUMENTS/` by composing the project's existing planning skills and agents. Team reviews each document before any code is written (Phase 2).

## Success criteria

- `01-spec.md`, `02-tdd.md`, `03-plan.md`, `04-task.md` all exist in `specs/tickets/$ARGUMENTS/`
- Each document has an explicit human approval recorded before the next step starts
- The final line of this command is "STOP. Do not implement." — no code is written in this phase

## Workflow

### Step 1 — Gather ticket info

If an Azure DevOps MCP or CLI is available, fetch the ticket:

```bash
az boards work-item show --id $ARGUMENTS --organization https://dev.azure.com/neurondAI/ --output json
```

Otherwise, ask the user for: ticket title, description, acceptance criteria, linked items / prior context.

**Input quality check.** If the ticket is too vague to plan — no testable acceptance criteria, ambiguous scope, undefined or contradictory key terms — STOP and ask the user to clarify before proceeding. Do not attempt to work around vague input, and do not proceed to Step 2 until the gaps are closed.

Create `specs/tickets/$ARGUMENTS/` if it does not exist.

### Step 2 — Produce `01-spec.md` via `/na-analyze-requirement`

Invoke `/na-analyze-requirement` with the ticket info from Step 1, instructing it to write to `specs/tickets/$ARGUMENTS/01-spec.md`. The skill runs its own Self-Check (mechanical REQ ↔ AC ↔ V linkage + body-audience greps) before returning — trust that gate; do not add a second reviewer on top.

Read the written file to confirm it exists and contains the canonical sections from `.claude/templates/spec.md`.

**Approval gate — `01-spec.md`:**

Summarize to the user:

- Type (New feature / Improvement / Fix bug / Big feature) and Size (S / M / L / XL)
- Number of `REQ-xxx` and `AC-xxx`
- Scope: In / Out (brief)
- Open Questions (if any)
- Risks with Impact ≥ High

Then ask:

> `01-spec.md` is ready at `specs/tickets/$ARGUMENTS/01-spec.md`.
> Respond: **approve** / **revise** (with feedback) / **edit** (you edit directly; tell me when done).

- **revise:** re-invoke `/na-analyze-requirement` with the original input plus the feedback. Return to this gate.
- **edit:** wait for the user to confirm; re-read the file; return to this gate.
- **approve:** continue to Step 3.

### Step 3 — Produce `02-tdd.md` via `project-architect` agent

Spawn the `project-architect` agent:

- Input: `specs/tickets/$ARGUMENTS/01-spec.md`
- Output: `specs/tickets/$ARGUMENTS/02-tdd.md`
- Template: `.claude/templates/architecture.md` — follow its sections and the scope rule at the top (architectural decisions only; SQL, full validation, and file manifests belong in `03-plan.md`).

Instruction to the agent:

> The architecture doc is a high-level document, target ~150 lines, and contains architecture only — no Requirement Traceability, no Risks & Open Questions, no Out of Scope section. Read `01-spec.md` first. Record each real architectural choice as an `ADR-xxx` entry (2–5 total) with alternatives considered and explicit trade-offs — skip the ADR format when no reasonable alternative exists, do not fabricate. **Each ADR should include a small Mermaid diagram** (sequence / flowchart / component) when the decision changes where code runs or how requests flow; a picture is often worth more than a paragraph for ADR review. §3 High-level Design is one Mermaid diagram plus short prose, no column lists / endpoint signatures / file paths / line numbers — those belong in `03-plan.md` and `04-task.md`.

After completion, read the file and verify:

1. Frontmatter has `ticket: $ARGUMENTS` and a `spec:` link to `01-spec.md`.
2. §2 contains between 1 and 5 `ADR-xxx` entries.
3. §3 contains at least one ```` ```mermaid ```` block, AND at least half of the ADRs in §2 include a Mermaid diagram (round up).
4. The document ends at §4 Migration & Rollout — no Requirement Traceability, Risks & Open Questions, or Out of Scope sections.
5. Total file length is ≤ 200 lines (soft ceiling; ~150 is the target).
6. No forbidden vague phrases: `TBD`, `appropriate`, `as needed`, `standard`, `will be implemented`.
7. No leaked implementation detail: no `CREATE TABLE`, no ```` ```typescript ```` blocks declaring function signatures, no `app/...:lineNumber` citations.

If any check fails, re-spawn the agent naming the specific gap. Do not paper over it.

**Approval gate — `02-tdd.md`:**

Summarize to the user:

- Key ADRs (ID + one-line decision each)
- §3 diagram shape (one sentence — "sequence diagram of Auth.js → layout guard → redirect")
- Migration approach (phased / flagged / big-bang)

Then ask:

> `02-tdd.md` is ready at `specs/tickets/$ARGUMENTS/02-tdd.md`.
> Respond: **approve** / **revise** (with feedback) / **edit** (you edit directly; tell me when done).

- **revise:** re-spawn `project-architect` with the spec + feedback; return to this gate.
- **edit:** wait for user confirmation; re-read the file; re-run the 7 verification checks; return to this gate.
- **approve:** continue to Step 4.

### Step 4 — Produce `03-plan.md` via `/write-phase-plan`

Invoke `/write-phase-plan` with the ticket ID. It reads `01-spec.md` + `02-tdd.md` and produces a **high-level phased roadmap** at `specs/tickets/$ARGUMENTS/03-plan.md` following `.claude/templates/phase-plan.md`. The plan sits between the TDD (why + shape) and the task list (what + where): it captures *the phases*, their order, and their exit criteria — nothing more.

Instruction to the skill:

> The plan is a high-level document, target ~150 lines. Produce 3–5 phases; each phase has Purpose, Size (S/M/L), Depends on, and verifiable Exit criteria — not a task list. Use the `diagram` skill complexity rubric to pick ASCII or Mermaid for §3 Phase Dependency Graph (ASCII is usually enough for 3–5 phases). Every `REQ-xxx` from the spec MUST appear in §5 Requirement Traceability, mapped to exactly one delivering phase (or to §7 if explicitly deferred). Log sequencing ambiguities in §6 Open Questions. Do NOT write file paths, function signatures, SQL, per-field validation, or specific test file names — those belong in `04-task.md`.

After completion, read the file and verify:

1. Frontmatter has `ticket: $ARGUMENTS`, a `spec:` link to `01-spec.md`, and a `tdd:` link to `02-tdd.md`.
2. §2 contains between 3 and 5 phases. Each phase has all four fields populated: **Purpose**, **Size** (S/M/L), **Depends on**, **Exit criteria** (≥ 1 bullet).
3. §3 contains a phase dependency graph (either an ASCII fenced block or a ```` ```mermaid ```` block).
4. §5 references every `REQ-xxx` from `01-spec.md` at least once (grep both files to compare).
5. Total file length is ≤ 200 lines (soft ceiling; ~150 is the target).
6. No forbidden vague phrases: `TBD`, `appropriate`, `as needed`, `standard`, `will be implemented`.
7. No leaked implementation detail: no file paths (`app/.../*.ts`, `migrations/*.sql`), no `CREATE TABLE`, no ```` ```typescript ```` blocks declaring signatures, no `file.ts:123` citations, no specific test file names.

If any check fails, re-invoke the skill naming the specific gap. Do not paper over it.

**Approval gate — `03-plan.md`:**

Summarize to the user:

- Phase count (3–5) + names
- Size distribution (e.g., `S:1, M:2, L:1`)
- §3 dependency shape (one sentence — `"linear 1→2→3"` or `"2 parallel then merge"`)
- REQ coverage: `{covered}/{total}`
- Top 1–2 open questions blocking sequencing

Then ask:

> `03-plan.md` is ready at `specs/tickets/$ARGUMENTS/03-plan.md`.
> Respond: **approve** / **revise** (with feedback) / **edit** (you edit directly; tell me when done).

- **revise:** re-invoke `/write-phase-plan` with the feedback; return to this gate.
- **edit:** wait for user confirmation; re-read the file; re-run the 7 verification checks; return to this gate.
- **approve:** continue to Step 5.

### Step 5 — Produce `04-task.md` via `project-planner` agent

`04-task.md` is where implementation detail *first* lands in the workflow — file paths, function names, test commands, and commit messages all appear here for the first time. `project-planner` reads all three prior documents AND the codebase itself (via Grep/Glob/Read) to derive real file paths, because `03-plan.md` no longer carries them.

Spawn the `project-planner` agent:

- Inputs: `specs/tickets/$ARGUMENTS/01-spec.md`, `specs/tickets/$ARGUMENTS/02-tdd.md`, `specs/tickets/$ARGUMENTS/03-plan.md`
- Output: `specs/tickets/$ARGUMENTS/04-task.md`
- Template: `.claude/templates/task.md`

Instruction to the agent:

> Read all three input documents first, then explore the codebase to find real file paths (the TDD's ADRs tell you *where* code should go; you translate that into concrete files via Grep/Glob). Group tasks by the phases defined in `03-plan.md §2` — every phase must receive at least one task, and every task must belong to exactly one phase. Each `TASK-xxx` has Phase, Addresses (`REQ-xxx`), Files (with `(NEW)` or `(MODIFY)` tags), Dependencies, Complexity, and 5 TDD-style checkbox steps with real code and real commands — no placeholders. The Traceability table uses `REQ-xxx` (not `FR-xxx`). The Phase Coverage table maps every phase to its tasks. If a file path cannot be determined from the codebase, raise it in a `## Blockers` section rather than guessing.

After completion, read the file and verify:

1. Frontmatter / header names the correct ticket and cites all three upstream docs.
2. **Phase coverage:** every phase from `03-plan.md §2` appears in the `## Phase Coverage` table with ≥ 1 task. Grep both files to compare phase names.
3. **REQ coverage:** every `REQ-xxx` from `01-spec.md` appears in the `## Traceability` table with ≥ 1 task. Grep both files to compare.
4. Every `TASK-xxx` has all six fields populated: **Phase**, **Addresses**, **Files**, **Dependencies**, **Complexity**, and 5 checkbox steps.
5. No task references more than 3 files (count the comma-separated paths in its `Files` field).
6. Every `(MODIFY)` file path actually exists in the repo (Glob each path; flag any misses).
7. A Mermaid `graph TD` dependency block exists with no circular edges.
8. No `FR-xxx` references anywhere (should be `REQ-xxx`).

If any check fails, re-spawn the agent naming the specific gap. Do not paper over it — especially check 6 (ghost file paths) and check 2 (orphan phases).

**Approval gate — `04-task.md`:**

Summarize to the user:

- Task count and complexity breakdown: `S:x, M:y, L:z`
- Phase coverage: `{covered}/{total}` phases represented
- REQ coverage: `{covered}/{total}` requirements covered
- Dependency graph depth (longest chain length)
- Any `## Blockers` the agent raised
- Top 1–2 tasks with complexity `L` (flag for possible split)

Then ask:

> `04-task.md` is ready at `specs/tickets/$ARGUMENTS/04-task.md`.
> Respond: **approve** / **revise** (with feedback) / **edit** (you edit directly; tell me when done).

- **revise:** re-spawn `project-planner` with the feedback; return to this gate.
- **edit:** wait for user confirmation; re-read the file; re-run the 8 verification checks; return to this gate.
- **approve:** continue to Step 6.

### Step 6 — Final summary

Print a summary of all four documents with their paths and key counts.

Tell the user:

> Four planning documents ready in `specs/tickets/$ARGUMENTS/`:
>
> - `01-spec.md` — {REQ count} requirements, {AC count} acceptance criteria
> - `02-tdd.md` — {ADR count} architecture decisions, {line count} lines
> - `03-plan.md` — {phase count} phases (S:{x}/M:{y}/L:{z}), {line count} lines
> - `04-task.md` — {task count} tasks (S:{x}/M:{y}/L:{z}), {phase coverage}/{phase total} phases covered, {REQ coverage}/{REQ total} REQs covered
>
> Review and add "Status: Approved" to each document before running the implementation command for ticket `$ARGUMENTS`.

**STOP HERE. Do not implement anything.**
