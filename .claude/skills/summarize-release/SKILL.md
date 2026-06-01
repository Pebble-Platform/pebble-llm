---
name: summarize-release
version: 1.0.0
description: "[Git] Generate a release summary markdown file in docs/releases/. Use after a release tag is created. Triggers on: 'summarize release', 'release summary', 'release notes', 'generate release', 'na-release-summary'."
argument-hint: "<version-tag> [base-tag] (e.g. v0.3.5 v0.3.4)"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, TaskCreate, TaskUpdate
---

## Quick Summary

**Goal:** Generate a structured release summary at `docs/releases/{version}.md` from git commits and related docs.
**Workflow:** Resolve tags -> Collect commits -> Find related docs -> Deduplicate vs previous release -> Categorize -> Write file
**Key Rules:** Only include items NEW to this release (not in previous). Bug docs live under `specs/bugs/`, feature docs under `specs/features/`. Sections are Bug Fixes, Features, Other Changes — only include sections that have content.

## Workflow

### Step 1: Resolve Version Tags

Parse arguments: `{version}` (required), `{base}` (optional).

```bash
# If base not provided, find the previous tag
git tag --list 'v*' --sort=-version:refname
```

Auto-detect base: the tag immediately before `{version}` in semver order (skip pre-release tags like `-rc`, `-beta`).

### Step 2: Collect Commits

```bash
# Non-merge commits (the actual work)
git log {base}..{version} --no-merges --format="%h %s%n%b---"

# Merge commits (for PR branch context)
git log {base}..{version} --merges --format="%h %s"
```

### Step 3: Find Related Documentation

Search for docs tagged with this release version:

```bash
grep -r "RELEASED.*{version}" docs/ --include="*.md" -l
```

Read each doc's `## Summary` or first paragraph to understand the bug/feature context.

### Step 4: Deduplicate Against Previous Release

If `docs/releases/{base}.md` exists, read it. Remove any items from the current commit list that are already documented there. This is critical — raw commit logs often span broader ranges.

### Step 5: Categorize & Group

Classify each remaining commit into sections:

| Section | When to use |
|---------|-------------|
| **Bug Fixes** | Commits fixing bugs, docs under `specs/bugs/` |
| **Features** | New capabilities, docs under `specs/features/` |
| **Other Changes** | Infrastructure, dependencies, refactoring, chores |

Group related commits under a descriptive subsection heading: `### {Area} — {Short Problem/Feature Description}`

### Step 6: Write Release File

Output to `docs/releases/{version}.md` following the template in `references/release-format-template.md`.

Rules:
- Each subsection links to related docs with `> **Docs:** [label](relative-path) | ...`
- Bullet points describe WHAT changed in business terms, not implementation details
- Only include sections (Bug Fixes / Features / Other Changes) that have content
- Use relative paths for doc links (e.g. `../bugs/workspace/bugfix-plan.md`)
- Today's date for release date unless the tag has a known date

### Step 7: Review

Read the generated file. Verify:
- No items duplicated from previous release
- All doc links resolve to real files
- Sections are balanced (no single-bullet subsections — merge small items)
- Headings describe the problem/feature, not the implementation

## Related

- `changelog` — business-focused CHANGELOG.md entries
- `branch-comparison` — detailed diff analysis between branches
- `commit` — conventional commit formatting
