---
name: na-bug-fix-package
description: "[Bug] Step 3 of /na-investigate-bug — produce the 3-doc fix package (problem / solution / fix-steps) from .claude/templates/bug-*.md. Reads the prior bug-context.md + RCA docs and turns them into review-ready artifacts. Use after /na-bug-rca."
argument-hint: "<path to bug folder>"
---

> **[IMPORTANT]** Use `TaskCreate` to break work into small tasks BEFORE starting — one task per doc produced (3), plus prep and Self-Check.

## Quick Summary

**Goal:** Produce three review-ready documents that hand the bug off for fixing:

- `bug-<slug>.md` — the problem
- `bug-<slug>-solution.md` — the solution (design, **no code**)
- `bug-<slug>-fix-steps.md` — the implementation runbook

**Workflow:** Confirm slug → Read prior docs → Draft problem doc → Draft solution doc → Draft fix-steps doc → Cross-link & Self-Check.
**Key rule:** Three audiences, three docs. Solution has zero code. Fix-steps has all the code. Acceptance criteria are identical across all three.

---

## When to Use

- After `/na-bug-rca` has produced at least one RCA doc.
- When you're ready to hand off the bug for implementation (or to write the PR description).

Skip for trivial bugs where the fix is obvious and a single PR description is enough.

---

## Input / Output

**Input** (via `$ARGUMENTS` or user message):
- Path to the bug folder (e.g. `specs/features/chat/bug-token-usage-spike/`)

The folder must already contain:
- `bug-context.md` (from `/na-bug-reproduce`)
- One or more RCA docs (from `/na-bug-rca`)
- The raw log files

**Output** in the same folder:

| File | Template | Audience | Code allowed? |
|---|---|---|---|
| `bug-<slug>.md` | `.claude/templates/bug-problem.md` | BA / PM / triage | Minimal — only the `file.ts:NN` of the root cause |
| `bug-<slug>-solution.md` | `.claude/templates/bug-solution.md` | reviewer / tech lead | **No code blocks > 1 pseudo-line** |
| `bug-<slug>-fix-steps.md` | `.claude/templates/bug-fix-steps.md` | implementer | All code, before/after, runbook |

---

## Workflow

### 0. Resolve `<slug>`

The slug was chosen in `/na-bug-reproduce` Step 2 and is recorded in `bug-context.md` (the folder name itself, e.g. `bug-token-usage-spike` → slug `token-usage-spike`). Confirm by reading the folder name. **All three filenames use this slug** — they must match exactly.

If the slug is missing or unclear, ask the user via `AskUserQuestion`. Do not pick a new slug — it must match the folder name (so cross-links from RCA docs to fix-package docs work).

### 1. Read prior docs

Read in this order:

1. `bug-context.md` — for §4 Identifiers and the headline symptom.
2. Every RCA doc — for the root causes (F1 / F2 / F3), citations, and numeric headline values.
3. Skim the raw logs only if the RCA docs reference a line you need to quote directly.

While reading, capture in working notes:

- The invariant violated (often surfaces in the RCA TL;DR).
- The list of root causes with their `file.ts:NN` locations.
- The numeric impact (e.g. "1.8× tokens, 3.7× cost").
- The list of changes the fix will need to make (mentioned implicitly in the RCA "and that's why X happens" sections).

### 2. Draft `bug-<slug>.md` from `.claude/templates/bug-problem.md`

Copy the template into `<folder>/bug-<slug>.md` and fill it in.

**Section-by-section sourcing:**

| Template section | Source |
|---|---|
| Frontmatter + header bar | `bug-context.md` §1 + ticket |
| §1 Summary | RCA TL;DR sentences, condensed to 2–3 |
| §2 The relevant invariant | RCA "the invariant" claim, or derived from the root cause |
| §3 Root cause(s) | One subsection per RCA doc / F-label. Cite `file.ts:NN`. Show minimal reproducer code. |
| §4 Reproduction | `bug-context.md §3` + RCA "concrete numbers" sections |
| §5 Impact | Derived from the affected surface + the inflation factor / downstream effects |
| §6 Out of scope | RCA "adjacent bugs surfaced" + bug-context §5 deferred questions |
| §7 Acceptance criteria | Numbered list — the testable post-conditions |

**Length target:** ~150–250 lines for a typical bug. If the bug spans 5+ layers, allow up to ~400 lines but split into clear sections.

### 3. Draft `bug-<slug>-solution.md` from `.claude/templates/bug-solution.md`

Copy the template into `<folder>/bug-<slug>-solution.md` and fill it in.

**Section-by-section sourcing:**

| Template section | Source |
|---|---|
| §1 Goal | Restate the post-fix state from §7 Acceptance criteria (in user/system terms) |
| §2 Guiding principle | The invariant from `bug-<slug>.md §2`, framed as a design principle |
| §3 Solution overview | One S-item per coordinated change. Mark the keystone. |
| §4 Why this approach over alternatives | One rejected alternative minimum. Name its drawback. |
| §5 Solution detail | One subsection per S-item — describe what changes conceptually. **File names allowed, code is not.** |
| §6 Risk analysis | Risk × Likelihood × Mitigation |
| §7 Verification approach | Map 1:1 to `bug-<slug>.md §7` |
| §8 Non-goals | Mirror `bug-<slug>.md §6` |
| §9 Acceptance criteria | **Verbatim from `bug-<slug>.md §7`** |

**The no-code rule:** if you find yourself writing a code block longer than one pseudo-line of syntax, stop. Move it to fix-steps. The solution doc must be evaluable as a *design* — a reviewer should be able to say "yes, fix the bug this way" or "no, do it differently" without seeing TypeScript.

**Length target:** ~150–250 lines.

### 4. Draft `bug-<slug>-fix-steps.md` from `.claude/templates/bug-fix-steps.md`

Copy the template into `<folder>/bug-<slug>-fix-steps.md` and fill it in.

**Section-by-section sourcing:**

| Template section | Source |
|---|---|
| Estimated effort | Sized phases — round to 0.25 day; total at the bottom |
| Phase 0 | Branch + baselines + screenshots + local repro confirmation |
| Phase 1..N | One phase per S-item in the solution doc, in dependency order. Each phase: Why → File(s) → Before/After code → Verify. |
| Tests phase | Update fixtures, hand-compute expected values, run `pnpm lint:fix` / `pnpm type-check` / `pnpm test:unit` |
| Staging rollout | Deploy → generate event → assert invariant → regression check |
| Backfill phase | Optional; targeted-vs-full decision; safety steps (read-only first, transaction, before/after CSV) |
| PROD rollout | Merge → deploy → backfill → ticket update → stakeholder notification |
| Rollback plan | Per-phase reversal |
| Definition of done | Checkbox list mirroring §7 of the bug doc |

**Code is required here.** Show before/after snippets for the key changes — but mark them as illustrative; the implementer reads surrounding context before pasting.

**Phase ordering rule:** if a later phase emits warnings unless an earlier phase landed (e.g. a new metric needs a pricing rate row), the dependency goes in the "Why first" header of the earlier phase. Order is not arbitrary.

**Length target:** ~250–400 lines. Fix-steps docs are runbooks; they trade brevity for completeness.

### 5. Cross-link and Self-Check

Add cross-links between the three docs (templates already include the link bar at the top — verify URLs resolve relative to the folder).

Mechanical Self-Check — read each doc, do NOT tick from memory:

- [ ] All three filenames use the **same `<slug>`** matching the folder name.
- [ ] `bug-<slug>.md §7` and `bug-<slug>-solution.md §9` are **identical** (acceptance criteria match verbatim).
- [ ] `bug-<slug>-fix-steps.md` Definition of Done has one checkbox per acceptance criterion.
- [ ] **`bug-<slug>-solution.md` contains no code block longer than one pseudo-line.** Scan every triple-backtick.
- [ ] Every `file.ts:NN` in the problem doc resolves via `Grep`.
- [ ] Fix-steps Phase 0 exists and captures "before" state.
- [ ] Fix-steps Rollback plan exists per phase.
- [ ] Fix-steps phases are orderable — each phase's Verify is independent of later phases.
- [ ] Out-of-scope items in `bug-<slug>.md §6` are not silently bundled into the fix-steps.

If any box fails, fix before declaring the package ready for review.

---

## Key Rules

- **Three audiences, three docs.**
  - Problem doc → BA / PM / triage. The story of what's wrong.
  - Solution doc → reviewer / tech lead. The design call.
  - Fix-steps doc → implementer. The runbook.
- **Solution has no code.** If you need code to explain it, it's not a design decision — it's an implementation detail. Move it.
- **Acceptance criteria are sacred.** Identical across all three docs. The PR ships iff every criterion is verifiable as done.
- **Out-of-scope is filed, not bundled.** Adjacent bugs surface their own tickets. Bundling expands review surface and delays the fix.
- **Sticky slug.** The folder name `bug-<slug>` is the source of truth for `<slug>`. Every produced filename matches.
