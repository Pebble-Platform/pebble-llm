# Plan: {{FEATURE_NAME}}

**Classification:** Small (score: {{X}}/15 -- {{dimension breakdown}})
**Spec:** `spec/{{feature-slug}}/{{subfeature-slug}}/spec.md`
**Status:** Draft | Reviewed | Approved

## Summary

<!-- 2-3 sentences: what approach was chosen and why. -->

## Requirements Coverage

| REQ ID | Description | How Addressed |
|--------|-------------|---------------|
| REQ-001 | ... | ... |

## Technical Context

<!-- What this feature depends on — discovered from codebase investigation.
Standards inherited, tech stack, existing services involved. -->

- Inherits: <!-- e.g. `standards/code-conventions.md` -->
- Tech stack: <!-- e.g. Express + PostgreSQL, existing auth middleware -->

## Approach

<!-- What approach was chosen and why. 1-2 paragraphs.
Reference existing patterns/utilities being reused. -->

## Affected Files

| File | Action | Change |
|------|--------|--------|
| `path/to/file` | Create / Modify | What changes and why |

## Risks & Tradeoffs

<!-- Identified risks, or "None — localized change with no side effects." -->

| Risk | Severity | Mitigation |
|------|----------|------------|
| ... | ... | ... |

## Verification Plan

<!-- One line. Evidence is always captured in verification-report.md
     (template: .claude/templates/verification-report.md). -->

Evidence captured in `spec/{{feature-slug}}/{{subfeature-slug}}/verification-report.md`; every REQ/AC gets a Trace Matrix row with Test Location + Command. `/verification` runs the commands, fills Results, and commits the verdict.
