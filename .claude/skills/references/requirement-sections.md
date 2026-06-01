# Requirement Sections

From raw idea + domain docs + research (if done) + user answers, fill every section of `templates/spec.md`. Zero implementation details -- writing HOW means you've gone too far.

## Required sections

- **Intent** -- *what* this feature does (scope) and *why* it exists (motivation), as two distinct concerns. They should breathe separately.
- **Model** -- key nouns and concepts with precise definitions. Define terms **before** using them in requirements. Every term referenced in REQs, ACs, or Invariants should appear here. Misaligned terms propagate silently when an AI is the implementer.
- **Boundaries** -- explicit in-scope, out-of-scope, and ambiguity policy. The ambiguity policy is one of:
  - `Halt and ask` -- stop when the spec doesn't cover a case
  - `Conservative interpretation` -- pick the safest option
  - `Closest matching rule` -- apply the nearest existing rule
- **Functional requirements** (REQ-XXX) -- testable, MUST / SHOULD / MAY language per BCP 14 / RFC 2119 / RFC 8174.
- **Non-functional requirements** (NFR-XXX) -- performance, reliability, security, observability, error handling. **Kept separate** from functional REQs so they are not lost in a flat list.
- **Examples** -- at least 1 valid and 1 invalid input-output pair. Informative by default; promote to AC if the behavior must be binding.
- **Acceptance criteria** -- WHEN/THEN format, each mapping to a REQ/NFR ID.
- **Invariants** -- conditions that must always hold true (before, during, after the change).
- **Verification matrix** -- REQ/NFR -> AC -> verification method -> evidence. Can be partial at spec time.

## Overlapping / bug-fix path

If the target sub-feature folder already exists (reuse flow), append a new REQ block to the existing `spec.md` under a `## YYYY-MM-DD -- {short description}` heading instead of overwriting. Keep prior REQ/AC IDs intact; continue numbering from the highest existing ID.

## Self-review checklist

- [ ] Domain docs were fetched and read, OR user confirmed greenfield
- [ ] Intent has both What and Why, stated separately
- [ ] Model defines every term used in REQs, ACs, and Invariants
- [ ] Boundaries has in-scope AND out-of-scope AND ambiguity policy
- [ ] Every REQ is testable with MUST/SHOULD/MAY language (BCP 14)
- [ ] NFRs are separated from functional REQs
- [ ] Examples include at least 1 valid and 1 invalid case
- [ ] No vague terms ("fast", "user-friendly", "appropriate", "etc.")
- [ ] Research findings cited with sources (if research was done)
- [ ] Acceptance criteria use WHEN/THEN and map to REQ/NFR IDs
- [ ] No implementation details (no code paths, file names, or technical architecture)
- [ ] No source code was read during this phase
- [ ] Assumptions documented in Open Questions
- [ ] Verification matrix covers every REQ and NFR
