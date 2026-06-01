# Conditional Research Guide

When to research and how to conduct targeted searches that inform requirements.

## Decision Matrix

After reading the project's business context (Step 3 of the workflow), evaluate gaps:

| Condition | Action |
|-----------|--------|
| Project context has gaps the idea depends on | Research |
| Assumptions surfaced in Step 1 remain unvalidated | Research |
| Domain is unfamiliar -- project docs don't cover it | Research |
| Competitive landscape is unclear | Research |
| User explicitly requests research | Research |
| Project context + user answers cover all needs | Skip |
| Domain is well-understood, no open gaps | Skip |

If skipping, note in spec: "Research skipped -- requirements derived from project context and user input."

## Search Strategy (3-8 searches)

Run in priority order. Stop when enough to inform requirements.

### 1. Problem Validation (1-2 searches)
Search: `"{problem domain}" user complaints OR pain points OR challenges`
Goal: Confirm the problem is real. Capture user language.

### 2. Existing Solutions (1-3 searches)
Search: `"{problem domain}" tools OR solutions OR alternatives`
Goal: What exists? What gaps remain? What's table-stakes?

### 3. User Expectations (1-2 searches)
Search: `"{problem domain}" best practices OR UX patterns`
Goal: What do users expect from this type of solution?

### 4. Failure Patterns (1 search)
Search: `"{problem domain}" failures OR mistakes OR pitfalls`
Goal: What should we avoid?

## Synthesizing Findings

After searches, produce:
- **Key insight**: One sentence -- most important discovery
- **User pain points**: 3-5 specific needs from real users
- **Competitive landscape**: What exists, what's missing
- **Risks discovered**: Pitfalls others faced
- **Requirement implications**: How findings shape the REQs

## Quality Rules

- Every finding must reference a specific source
- Discard generic advice -- keep only what informs requirements
- If research contradicts the original idea, report honestly
- "No relevant results" is valid -- note it and move on
