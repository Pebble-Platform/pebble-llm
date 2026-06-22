---
name: long-task
description: "[Execution] Run a long-running, multi-session task against a single living Markdown tracking doc. Analyzes the request into goals/requirements/milestones, maintains the doc as work progresses (decisions, completed work, remaining items), and auto-spawns a research agent whenever an open question or uncertainty blocks progress — folding the findings back into the doc so every decision stays traceable. Use for any task too big or too long for one pass. Triggers on: 'start a long-running task', 'track this project', 'plan and execute this over time', 'keep a running plan for', 'this is a big task'."
argument-hint: "<the task / project to run> [doc slug]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Agent, TaskCreate, TaskUpdate
---

## Quick Summary

**Goal:** Drive a large, multi-step (often multi-session) task from a single **living tracking doc** at `docs/tasks/<slug>.md` — so goals, decisions, progress, and the reasoning behind each choice are always written down and resumable.

**Workflow:** Analyze the request → write the tracking doc → execute milestone by milestone, updating the doc as you go → on any blocking uncertainty, spawn `task-researcher` → fold its findings back into the doc → continue until done.

**Key rules:**
- The doc is the source of truth. Update it *as part of* doing the work, not after.
- Never guess past a blocking uncertainty — research it, record the answer and *why*, then proceed.
- Every decision in the doc carries its rationale and (if researched) a source. A future reader must be able to reconstruct why.

---

## When to Use

- A task spanning many steps or several sessions, where context will be lost and must be reconstructable.
- Work with open design questions, unknowns, or "what's the best way to…" decisions baked in.
- Skip for a quick, single-pass change — this is overhead you don't need there. For a one-ticket plan use `/na-plan`; for a bug use `/na-investigate-bug`. This skill is for open-ended execution that outlives one turn.

---

## Workflow

### Step 1 — Analyze the request

Restate the task in your own words. Derive and confirm before writing code:
- **Goal** — the outcome that means "done."
- **Requirements** — functional needs + hard constraints (perf, deps, repo conventions from `AGENTS.md`).
- **Unknowns** — anything you'd have to assume. These seed the Open Questions queue (Step 3).

If a genuine fork in scope exists (not a default-able detail), ask the user now. Otherwise pick sensible defaults and record them in the doc's Decision Log.

### Step 2 — Write the tracking doc

Pick a short kebab-case `<slug>` (from `$ARGUMENTS` or the goal). Write `docs/tasks/<slug>.md` using the **template below**. This is the deliverable's backbone — fill Goal, Requirements, Milestones, and seed Open Questions / Remaining Action Items.

Mirror the milestones into the harness task list (`TaskCreate`) so progress is visible in-session too.

### Step 3 — Execute, updating the doc continuously

Work milestone by milestone. After each meaningful unit of work, update the doc in the same turn:
- Tick completed items → **Completed Work** (with a one-line what/where, e.g. `path:line`).
- Record every non-trivial choice in the **Decision Log** (what, why, alternatives rejected).
- Keep **Remaining Action Items** current — add discovered work, remove done work.
- Move resolved questions out of **Open Questions**.
- Update **Status** (`planning` → `in-progress` → `blocked` → `done`) and the `Updated:` date.

Keep `TaskUpdate` in sync (`in_progress` when starting a milestone, `completed` when done).

### Step 4 — On a blocking uncertainty, research before proceeding

The moment progress depends on an answer you can't ground from the repo or what you already know — a design choice, an unfamiliar API, "what's the industry best practice for X", a library/version question — **do not guess**. Add it to **Open Questions**, then spawn the dedicated agent:

```
Agent(subagent_type: "task-researcher",
      description: "research <short question>",
      prompt: "<the single question> + task goal + the hard constraints + doc path docs/tasks/<slug>.md")
```

- **One question per agent.** If several independent questions block you, spawn them **in parallel** in one message.
- For a heavy, multi-source investigation, you may instead invoke the `/deep-research` skill — but the default is `task-researcher` (cheaper, scoped, returns one citable block).
- While research is out, either work on an unblocked milestone or wait — never proceed *past* the uncertainty on a guess.

### Step 5 — Fold findings back in

When the agent returns its block:
1. Paste it verbatim under **Research Findings** in the doc (keep them — they're the knowledge base).
2. Promote the recommendation into the **Decision Log** as the decision taken, citing the finding.
3. Resolve the matching **Open Question** (link to the finding).
4. Adjust **Milestones / Remaining Action Items** if the finding changed the plan.

Then continue execution (Step 3).

### Step 6 — Close out

When the Goal is met: set **Status: done**, confirm every milestone is checked, leave the Decision Log and Research Findings intact (they are the trace), and give the user a short summary pointing at `docs/tasks/<slug>.md`.

---

## Tracking Doc Template

Write this to `docs/tasks/<slug>.md`. Convert any relative dates to absolute.

```markdown
# <Task title>

- **Slug:** <slug>
- **Status:** planning | in-progress | blocked | done
- **Created:** <YYYY-MM-DD>  ·  **Updated:** <YYYY-MM-DD>
- **Owner:** <user / agent>

## Goal
<The outcome that means "done." One short paragraph.>

## Requirements & Constraints
- **Functional:** <what it must do>
- **Constraints:** <perf / deps / conventions / non-goals>

## Milestones
- [ ] M1 — <name> — <exit criterion>
- [ ] M2 — <name> — <exit criterion>
- [ ] M3 — <name> — <exit criterion>

## Decision Log
<!-- newest first; every entry: decision + why + alternatives rejected (+ source if researched) -->
- **<YYYY-MM-DD> — <decision>:** <why>. Rejected: <alts>. (see Research: <q> / <source>)

## Open Questions
<!-- anything blocking that needs research; move out once resolved -->
- [ ] <question> — <why it blocks> → researching via task-researcher

## Research Findings
<!-- task-researcher output blocks, pasted verbatim; this is the knowledge base -->
<!-- (empty until first research) -->

## Completed Work
- <YYYY-MM-DD> — <what was done> — <where: path:line / artifact>

## Remaining Action Items
- [ ] <next concrete step>
```

---

## Key Rules

- **The doc leads, not trails.** If the work and the doc disagree, the doc is stale — fix it in the same turn.
- **Surface, don't bury, uncertainty.** A guessed-past unknown is a silent bug. Route it through Step 4.
- **Traceable decisions.** Every Decision Log entry stands alone: a reader who lands on the doc cold can see what was chosen and why. Researched choices cite their finding.
- **Resumable.** Written so that on a fresh session you can read the doc top-to-bottom and pick up exactly where you stopped.
- **Stay surgical** (per `.claude/rules/03-surgical-changes.md`): the doc tracks the task; it isn't a license to refactor unrelated code.
