# {{Project Name}}

<!-- Project-level instruction file for any agent (Claude, Cursor, Cline,
     or a human). Start lean; add instructions only when a specific
     instruction would prevent a specific mistake. See Spec-Driven
     AI-Native Development Guide, Section 9.1. -->

## Table of Contents
- [Repository Layout](#repository-layout)
- [Commands](#commands)
- [Key Conventions](#key-conventions)
- [How to Start a Change](#how-to-start-a-change)
- [How to Verify Work](#how-to-verify-work)

## Repository Layout

| Path | Purpose |
|------|---------|
| `standards/` | Project-wide durable context -- tech stack, coding conventions, unit test strategy, git branching strategy, folder standards. Start with `standards/README.md`. |
| `spec/` | Feature hierarchy. One folder per feature: `spec/{feature}/spec.md` (Part 1: Business Context) + `spec/{feature}/code_context.md` (Part 2: Coding Context). Per-change work lives in sub-feature folders `spec/{feature}/{subfeature}/` containing `spec.md` (normative delivery spec with REQ/AC IDs), optional `plan.md`, and optional `tasks.md`. Sub-feature slugs are stable -- a later bug fix reuses the same folder rather than creating a new one. |
| `{{source-root}}` | Application source code. |
| `{{test-root}}` | Tests. |

## Commands

<!-- Only the commands an agent or new contributor must know.
     Extracted during /init-project scan. -->

- Install: `{{install command}}`
- Build: `{{build command}}`
- Test: `{{test command}}`
- Lint: `{{lint command}}`
- Type-check: `{{type-check command or "n/a"}}`
- Run dev server: `{{dev command or "n/a"}}`

## Key Conventions

<!-- Only the non-obvious rules. Do not repeat what standards/ already
     documents -- link to it. -->

- Coding conventions: see [`standards/coding-conventions.md`](standards/coding-conventions.md)
- Folder standards: see [`standards/folder-standards.md`](standards/folder-standards.md)
- Git branching: see [`standards/git-branching-strategy.md`](standards/git-branching-strategy.md)
- Unit test strategy: see [`standards/unit-test-strategy.md`](standards/unit-test-strategy.md)
- {{non-obvious constraint 1}}
- {{non-obvious constraint 2}}

## How to Start a Change

1. Open or create a ticket describing the change.
2. Invoke `/analyze-business-requirements` with the ticket content. It picks the parent feature under `spec/` (confirmed with you) and produces `spec/{feature-slug}/{subfeature-slug}/spec.md`. If the sub-feature folder already exists (overlapping change / bug fix), the skill merges into it rather than creating a new folder.
3. Invoke `/design-solution` to classify size and produce a proportional plan (skipped for trivial Small changes).
4. Invoke `/implementation` to generate code against the spec + plan.
5. Invoke `/verification` as the final gate.

## When the Workflow Was Skipped

If code was merged without going through the workflow and the docs have drifted, use the standalone context skills to sync:

- `/update-specs` -- refreshes a feature's `spec.md` + `code_context.md` based on `git diff`. Asks for scope, shows a diff preview, writes only user-approved edits.
- `/update-standards` -- refreshes ONE `standards/*.md` (tech-stack, coding-conventions, unit-test-strategy, git-branching-strategy, or folder-standards) by re-running the init-project signal scanner for that file.

Both are invokable any time -- no ticket or workflow required.

## How to Verify Work

"Done" means:
- [ ] Every REQ in the spec maps to code + a test in the verification matrix.
- [ ] `{{test command}}` passes.
- [ ] `{{lint command}}` passes.
- [ ] `{{type-check command or "n/a"}}` passes (if applicable).
- [ ] Deviations from the spec are reconciled -- either code is changed to match the spec, or the spec is updated to reflect a legitimate discovery.
