---
title: [Ticket Title]
ticket: [ID]
status: draft
owner: [team or person]
date: [Auto]
normative: true
---

# [Ticket Title]

## Intent

**What:** <!-- What this feature does. The "what" constrains scope.
1-2 sentences. -->

**Why:** <!-- Why it exists — the problem, gap, or motivation.
The "why" is rationale. They should breathe separately from "what".
1-2 sentences. -->

## Model

<!-- Key nouns and concepts with their definitions. Define terms
precisely so the AI agent uses them consistently across all phases.
This is one of the highest-leverage sections for AI-consumed specs.
Misaligned definitions propagate silently. A human will eventually
notice that "user" means "authenticated account" in one place and
"browser session" in another. An AI will not. Define the terms first,
then use them precisely in the requirements. -->

| Term | Definition |
|------|-----------|
| [Term] | [Precise definition as used in THIS spec] |

## Boundaries

In scope:

<!-- Bulleted list. Be specific — name modules, APIs, UI surfaces,
data domains. Each bullet should be verifiable. -->

Out of scope:

<!-- Bulleted list. Explicitly exclude adjacent areas that someone
might assume are included. -->

On ambiguity:

<!-- What the AI should do when the spec does not cover a case.
Pick one:
- "Halt and ask" — agent stops and asks for clarification
- "Conservative interpretation" — agent picks the safest option
- "Closest matching rule" — agent applies the nearest existing rule
-->

## Normative Contract

### Functional Requirements

<!-- The authoritative functional requirements. Each requirement is
testable, uses MUST / MUST NOT / SHOULD language (per BCP 14 /
RFC 2119 / RFC 8174), and has a unique ID. These are the hard
constraints the solution must satisfy.

- MUST — hard constraints. Violations are bugs.
- SHOULD — strong defaults. Exceptions need justification.
- MAY — optional behaviors.

- `REQ-001`: [Subject] MUST [do something specific and verifiable].
- `REQ-002`: [Subject] MUST NOT [violate some constraint].
- `REQ-003`: [Subject] SHOULD [preferred behavior with rationale].
-->

### Non-Functional Requirements

<!-- Performance, reliability, security, observability, error detection,
reporting, handling, recovery, and required responses to undesired
events. Separated from functional requirements to prevent them being
lost in a flat list. This is one of the easiest areas for AI-generated
work to stay too functional and too happy-path.

- `NFR-001`: [Subject] MUST [measurable non-functional constraint].
-->

## Examples

<!-- Valid and invalid input and output pairs. Examples are informative
by default. If an example must be binding, promote that behavior into
a requirement, acceptance criterion, or explicit conformance test.

Valid:
- [input] -> [expected output]

Invalid:
- [input] -> [expected error/rejection]
-->

## Affected Areas

<!-- Enumerate what this work touches at a high level — features,
services, data domains, integrations, user flows.

| # | Area | Notes |
|---|------|-------|
| 1 | [Feature / service / domain] | New / Modified / Replaced |
-->

## Invariants

<!-- Conditions that MUST remain true at all times — before, during,
and after the change. These are the "always true" guarantees the
system provides. Strong candidates: boundary conditions, state
transitions, data invariants, integration contracts, security
constraints, error handling obligations.

- [Invariant statement]
-->

## Acceptance Criteria

<!-- Testable scenarios in WHEN/THEN format. Each maps back to one
or more REQ-xxx or NFR-xxx. The discipline is to write acceptance
criteria so they can be unambiguously verified — ideally by a machine,
at minimum by a human following a deterministic procedure.

"The UI shall be intuitive" is not a useful criterion.
"Given X, when Y, then Z" is.

- `AC-001`: WHEN [condition] THEN [expected outcome].
- `AC-002`: WHEN [failure condition] THEN [graceful handling].
-->

## Verification Matrix

<!-- How each requirement is verified. Every REQ-xxx and NFR-xxx must
have at least one verification entry. The matrix captures
requirement-verifying tests — tests that prove a specific REQ or AC
has been met. Implementation-supporting tests (regression guards,
edge-case safety nets) emerge naturally during development and do not
need to appear here.

The matrix does not need to be complete at spec time. It can be filled
in as implementation proceeds. By final signoff, each accepted
requirement should have a clear verification approach.

| REQ ID | AC ID | Verification Method | Evidence |
|--------|-------|---------------------|----------|
| `REQ-001` | `AC-001` | [Automated test / Manual / Log inspection] | [test file or procedure] |
-->

## Risks and Mitigations

<!-- Identify what could go wrong, rate the impact, and define
a mitigation.

| Risk | Impact | Mitigation |
|------|--------|------------|
| [What could go wrong] | Critical / High / Medium / Low | [How to prevent or recover] |
-->

## Open Questions

<!-- Anything unclear that needs PO/team input before proceeding.

- `OQ-001`: [Question] — **Status:** open / resolved
-->
