# Plan: {{FEATURE_NAME}}

**Classification:** Medium (score: {{X}}/15 -- {{dimension breakdown}})
**Spec:** `spec/{{feature-slug}}/{{subfeature-slug}}/spec.md`
**Status:** Draft | Reviewed | Approved

---

## 1. Summary

<!-- 2-3 sentences: what this change does and why this approach was chosen. -->

## 2. Requirements Coverage

<!-- Map every REQ and NFR from the spec. Every requirement must appear. -->

| REQ ID | Description | Plan Section |
|--------|-------------|--------------|
| REQ-001 | ... | Section X |

## 3. Technical Context

<!-- Discovered from codebase investigation. What this feature depends on. -->

- Inherits: <!-- standards this follows -->
- Tech stack: <!-- language, framework, database, services -->
- Integrations: <!-- external APIs, existing internal services -->

## 4. Approach Evaluation

<!-- Compare at least 2 approaches. -->

| Criterion | A: {{Approach Name}} | B: {{Approach Name}} |
|-----------|---------------------|---------------------|
| {{criterion}} | ... | ... |
| Fit with REQ-xxx | ... | ... |

**Chosen:** {{A or B}} -- {{rationale}}

---

## 5. Design Decisions

<!-- Include ONLY sections that apply. Omit sections with zero design decisions.
     Note omitted sections at the bottom of the plan.

     Available sections (include if relevant):
     - 5.1 API Design (if new/modified endpoints)
     - 5.2 Database Design (if schema changes)
     - 5.3 Service & Module Design (if new/modified services)
     - 5.4 Security Considerations (if security-relevant changes)

     For included sections, follow the depth rules in references/depth-rules.md.
-->

---

## 6. Affected Files

### 6.1 Files to Create

| File Path | Purpose | Depends On |
|-----------|---------|------------|
| `path/to/new-file.ts` (NEW) | ... | ... |

### 6.2 Files to Modify

| File Path | Change Description | Backward Compatible? |
|-----------|--------------------|---------------------|
| `path/to/existing.ts` (MODIFY) | ... | Yes / No |

### 6.3 New Dependencies

<!-- Omit if no new dependencies -->

| Package | Version | Justification |
|---------|---------|---------------|
| ... | ... | ... |

---

## 7. Validation Criteria

<!-- What must be verified before merge. -->

- [ ] {{criterion that proves the change works}}
- [ ] {{criterion that proves nothing is broken}}

### 7.1 Verification Plan

<!-- Map each REQ/NFR to its planned verification method and where the
     evidence will land. Evidence ultimately lives in
     spec/{feature}/{subfeature}/verification-report.md (template:
     .claude/templates/verification-report.md). -->

| REQ/NFR | Verification Method | Test Scope (unit / integration / E2E / manual / log) | Planned Test Location |
|---------|---------------------|------------------------------------------------------|-----------------------|
| REQ-001 | Automated test | unit | `test/path/file.test.ts` |
| NFR-001 | Log inspection | — | `{{bench/metric command}}` |

All rows are populated into the `verification-report.md` Trace Matrix during `/implementation`; `/verification` runs the commands and records Results.

## 8. Risks & Tradeoffs

| Risk | Severity | Likelihood | Mitigation |
|------|----------|-----------|------------|
| ... | ... | ... | ... |

---

<!-- Omitted sections (with rationale):
     - Section X: [reason — e.g., "no database changes in this spec"]
-->
