---
name: na-investigate-bug
description: "Bug investigation workflow. Produces bug-context.md, RCA docs, and the 3-doc fix package (problem / solution / fix-steps) for a bug by composing /na-bug-reproduce, /na-bug-rca, and /na-bug-fix-package."
allowed_tools: ["Skill", "AskUserQuestion", "Read", "Write", "Bash", "Grep", "Glob"]
---

# /na-investigate-bug — Bug investigation workflow

Input: $ARGUMENTS — a ticket id, a bug slug, a path to a log file, or a free-text symptom description.

## Goal

Produce a complete bug-investigation package in `specs/features/<area>/bug-<slug>/`:

- `bug-context.md` + saved log files (Step 1)
- One or more RCA docs answering specific named questions (Step 2)
- `bug-<slug>.md`, `bug-<slug>-solution.md`, `bug-<slug>-fix-steps.md` (Step 3)

Each step has an explicit human approval gate before the next step starts. No code is written by this command — only the docs above.

## Success criteria

- Output dir exists at `specs/features/<area>/bug-<slug>/`
- All required files exist (see Goal)
- Each step has a recorded approval (the user typed **approve**)
- The final line of this command is "STOP. Hand off to implementation." — no fix code is written here

## Workflow

### Step 0 — Gather input

Parse `$ARGUMENTS`:

- If it contains `NA-XXXX`, that is the ticket id.
- If it contains a path to a log file, remember the path for Step 1.
- If it is free text, treat it as the headline symptom.

Use `AskUserQuestion` to fill any gaps. You need, at minimum:

- A ticket id (or explicit "no ticket — track inline")
- A one-line symptom
- A path or attachment to at least one log file (server log, provider trace, or both)
- Severity and environment (PROD / staging / dev)

If the user can't provide a log file, STOP and explain why investigation requires evidence. Do not invent log content.

### Step 1 — Reproduce & collect logs via `/na-bug-reproduce`

Invoke the `na-bug-reproduce` skill with the gathered input. The skill runs its own Self-Check before returning — trust that gate.

After the skill returns, read `bug-context.md` and confirm:

1. Output dir is `specs/features/<area>/bug-<slug>/` and the folder exists.
2. Log files are saved into the folder (`log.txt`, `claude-log.txt`, or named equivalents).
3. `bug-context.md` is populated — every field, no `TBD` or `unknown` slots.
4. §4 Identifiers table has ≥ 1 row with a real `log.txt:NN` or `file.ts:NN` location.
5. §5 Open Questions has ≥ 1 question (or an explicit "no open questions — RCA may be straightforward").

If any check fails, re-invoke the skill naming the specific gap.

**Approval gate — Step 1:**

Summarize to the user:

- Slug + output dir
- Severity + environment
- Log files captured (with line counts)
- Reproduction status (reproducible / unreproducible — captured artifact)
- Identifier count + top suspect file
- Open question count

Then ask:

> Step 1 output is ready at `specs/features/<area>/bug-<slug>/`.
> Respond: **approve** / **revise** (with feedback) / **edit** (you edit directly; tell me when done).

- **revise:** re-invoke `/na-bug-reproduce` with the feedback. Return to this gate.
- **edit:** wait for the user to confirm; re-read `bug-context.md`; return to this gate.
- **approve:** continue to Step 2.

### Step 2 — Root-cause analysis via `/na-bug-rca`

Invoke the `na-bug-rca` skill with the bug folder path. The skill produces one or more RCA docs, each answering one named question, using the `.claude/templates/bug-rca-analysis.md` template. The skill runs its own Self-Check.

After completion, read each produced RCA doc and verify:

1. Each filename describes the question it answers (not `analysis-1.md`, not `rca.md`).
2. Each doc has the template structure: frontmatter, header bar, TL;DR, evidence sections, one-line summary.
3. Every numeric claim in TL;DR + headline tables has a `log.txt:NN` / `claude-log.txt:NN` citation. Spot-check 3 rows.
4. Every `file.ts:NN` citation resolves via `Grep`. Spot-check 2 citations.
5. If multi-cause, F1 / F2 / F3 labels are consistent across docs.
6. `bug-context.md §5` has been updated — every open question is resolved (with a link) or explicitly deferred.

If any check fails, re-invoke the skill naming the specific gap.

**Approval gate — Step 2:**

Summarize to the user:

- RCA doc count + the question each one answers
- Cause labels (F1 / F2 / F3) + one-line each
- Numeric headline (e.g. "8.36M displayed vs 4.64M real, 1.8× inflation")
- Deferred questions (if any)

Then ask:

> Step 2 RCA docs are ready in `specs/features/<area>/bug-<slug>/`.
> Respond: **approve** / **revise** (with feedback) / **edit** (you edit directly; tell me when done).

- **revise:** re-invoke `/na-bug-rca` with the feedback (e.g. "split F2 — write-path vs read-path are different causes"). Return to this gate.
- **edit:** wait for user confirmation; re-read the affected docs; re-run the 6 verification checks; return to this gate.
- **approve:** continue to Step 3.

### Step 3 — Fix package via `/na-bug-fix-package`

Invoke the `na-bug-fix-package` skill with the bug folder path. The skill produces three docs from `.claude/templates/bug-problem.md`, `bug-solution.md`, and `bug-fix-steps.md`. The skill runs its own Self-Check.

After completion, read all three produced files and verify:

1. All three filenames use the same `<slug>` (matches the folder name).
2. `bug-<slug>.md §7` and `bug-<slug>-solution.md §9` Acceptance Criteria lists are **identical** (`diff` if needed).
3. `bug-<slug>-fix-steps.md` Definition of Done has one checkbox per acceptance criterion.
4. `bug-<slug>-solution.md` contains **no code block longer than one pseudo-line**. Grep for triple-backticks and inspect each block.
5. Every `file.ts:NN` in the problem doc resolves via `Grep`.
6. Fix-steps Phase 0 exists and captures "before" state (branch + baselines + screenshot).
7. Fix-steps has a Rollback plan with per-phase reversal.
8. Out-of-scope items in `bug-<slug>.md §6` are NOT silently bundled into fix-steps phases.

If any check fails (especially 4 — code in solution doc), re-invoke the skill naming the specific gap.

**Approval gate — Step 3:**

Summarize to the user:

- Acceptance criteria count
- Solution overview: S-item count, keystone S-item
- Fix-steps phase count + total estimated effort
- Out-of-scope items (counted, not detailed)
- Top risk from solution §6

Then ask:

> Step 3 fix package is ready in `specs/features/<area>/bug-<slug>/`.
> Respond: **approve** / **revise** (with feedback) / **edit** (you edit directly; tell me when done).

- **revise:** re-invoke `/na-bug-fix-package` with the feedback. Return to this gate.
- **edit:** wait for user confirmation; re-read the docs; re-run the 8 verification checks; return to this gate.
- **approve:** continue to Step 4.

### Step 4 — Final summary

Print a summary of every produced doc with its path and key counts.

Tell the user:

> Bug investigation package ready in `specs/features/<area>/bug-<slug>/`:
>
> - `bug-context.md` — {N} identifiers captured, severity {1–4}, env {PROD/staging}
> - {RCA doc count} RCA doc(s) — {list of question-slugs}
> - `bug-<slug>.md` — {AC count} acceptance criteria, {cause count} root cause(s)
> - `bug-<slug>-solution.md` — {S-item count} solution items, {risk count} risks
> - `bug-<slug>-fix-steps.md` — {phase count} phases (~{N} days estimated)
>
> File the out-of-scope items from `bug-<slug>.md §6` as separate tickets. When ready, open the fix branch per `bug-<slug>-fix-steps.md` Phase 0.

**STOP. Hand off to implementation.**
