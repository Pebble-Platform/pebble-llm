---
title: [Ticket Title]
ticket: [ID]
status: draft
owner: [team or person]
date: [Auto]
normative: true
---

# [Ticket Title]

## Purpose

<!-- What this spec defines — the correctness contract for the work described
in the ticket. Frame it as closing a gap between the current state and the
target state. 2-4 sentences. -->

## Scope

In scope:

<!-- Bulleted list of what this work covers. Be specific — name modules,
APIs, UI surfaces, data domains. Each bullet should be verifiable. -->

Out of scope:

<!-- Bulleted list of what this ticket does NOT touch. Explicitly exclude
adjacent areas that someone might assume are included. -->

## Problem Statement

<!-- Why this work is needed. Describe the current state, its limitations or
pain points, and the specific issues that must be addressed. -->

## Normative Contract

<!-- The authoritative requirements. Each requirement is testable, uses MUST /
MUST NOT / SHOULD language, and has a unique ID. These are the hard
constraints the solution must satisfy.

- `REQ-001`: [Subject] MUST [do something specific and verifiable].
- `REQ-002`: [Subject] MUST NOT [violate some constraint].
- `REQ-003`: [Subject] SHOULD [preferred behavior with rationale].
-->

## Affected Areas

<!-- Enumerate what this work touches at a high level — features, services,
data domains, integrations, user flows. Use a table when the list is
non-trivial.

| # | Area | Notes |
| --- | --- | --- |
| 1 | [Feature / service / domain] | New / Modified / Replaced |
-->

## Invariants

<!-- Conditions that MUST remain true at all times — before, during, and after
the change. These are the "always true" guarantees the system provides.

- [Invariant statement]
- [Invariant statement]
-->

## Acceptance Criteria

<!-- Testable scenarios in WHEN/THEN format. Each maps back to one or more
REQ-xxx. Include both happy path and failure/edge cases.

- `AC-001`: WHEN [condition] THEN [expected outcome].
- `AC-002`: WHEN [failure condition] THEN [graceful handling].
-->

## Verification Matrix

<!-- How each requirement is verified. Every REQ-xxx must have at least one
verification entry.

| ID | Verification Method | Minimum Target | Pass Condition |
| --- | --- | --- | --- |
| `V-001` | [How to verify] | [What to measure] | [What "pass" looks like] |
-->

## Risks and Mitigations

<!-- Identify what could go wrong, rate the impact, and define a mitigation.

| Risk | Impact | Mitigation |
| --- | --- | --- |
| [What could go wrong] | Critical / High / Medium / Low | [How to prevent or recover] |
-->

## Open Questions

<!-- Anything unclear that needs PO/team input before proceeding.

- `OQ-001`: [Question] — **Status:** open / resolved
-->
