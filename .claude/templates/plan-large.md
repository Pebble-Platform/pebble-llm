# Plan: {{TICKET_ID}} -- {{FEATURE_NAME}}

> **Depth rule:** Every section must pass the "can an implementer code this without guessing?" test. If a section says *what* without *how*, it fails. See `references/depth-rules.md`.

**Classification:** Large (score: {{X}}/15 -- {{dimension breakdown}})
**Spec:** `spec/{{feature-slug}}/{{subfeature-slug}}/spec.md`
**Status:** Draft | Reviewed | Approved

## 1. Overview

**Ticket:** {{TICKET_ID}}

### 1.1 Summary

<!-- 2-3 sentences: what this change does and why -->

### 1.2 Functional Requirements Coverage

<!-- Map every FR from the spec to a plan section. Every FR must appear at least once. -->

| REQ ID | Description | Plan Section |
|--------|-------------|--------------|
| REQ-001 | ... | Section X.Y |

### 1.3 Non-Functional Requirements Coverage

| NFR ID | Description | How Addressed |
|--------|-------------|---------------|
| NFR-001 | ... | ... |

### 1.4 Approach Evaluation

<!-- Compare at least 2 approaches. -->

| Criterion | A: {{Approach Name}} | B: {{Approach Name}} |
|-----------|---------------------|---------------------|
| {{criterion}} | ... | ... |
| Fit with REQ-xxx | ... | ... |

**Chosen:** {{A or B}} -- {{rationale: why this approach, how it fits the spec requirements}}

---

## 2. Technical Context & Dependencies

<!-- Discovered from codebase investigation. Not available at spec time. -->

### 2.1 Standards Inherited

- `standards/{{file}}` -- {{what rules apply}}

### 2.2 Tech Stack

- Language: {{language and version}}
- Framework: {{framework}}
- Database: {{database and version}}
- Other: {{cache, queue, etc.}}

### 2.3 External Integrations

| Service | Purpose | Contract |
|---------|---------|----------|
| ... | ... | ... |

---

## 3. File & Dependency Map

### 3.1 Files to Create

| File Path | Purpose | Depends On |
|-----------|---------|------------|
| `path/to/new-file.ts` (NEW) | ... | ... |

### 3.2 Files to Modify

| File Path | Change Description | Backward Compatible? |
|-----------|--------------------|---------------------|
| `path/to/existing.ts` (MODIFY) | ... | Yes / No -- migration note |

### 3.3 New Dependencies

| Package | Version | Justification |
|---------|---------|---------------|
| ... | ... | Why this package, why not alternatives |

### 3.4 Dependency Graph

<!-- Show which new/modified files depend on which. -->

```
new-file.ts
  +-- existing-service.ts (no changes)
  +-- new-model.ts (NEW)
  +-- existing-middleware.ts (no changes)
```

---

## 4. API Design

<!-- Repeat this section for EVERY new or modified endpoint. -->

### 4.X {{METHOD}} {{ROUTE_PATH}}

**File:** `path/to/route.ts` (NEW | MODIFY)
**Auth:** {{auth requirements -- JWT, API key, public, roles}}
**Rate limit:** {{rate limit or "none"}}

**Request body:**
```json
{
  "fieldName": "type (constraints, required/optional, default)"
}
```

**Response {{STATUS_CODE}}:**
```json
{
  "field": "type"
}
```

**Error responses:**

| Code | Condition | Response Body |
|------|-----------|---------------|
| 400 | {{condition}} | `{ "code": "ERROR_CODE", "message": "..." }` |
| 404 | {{condition}} | `{ "code": "ERROR_CODE", "message": "..." }` |

**Validation rules:**

- `fieldName`: {{exact validation rule}}

---

## 5. Database Design

<!-- Repeat this section for EVERY new or modified table/collection. -->

### 5.X {{NEW TABLE | MODIFY TABLE}}: {{table_name}}

**Migration file:** `migrations/{{YYYYMMDD}}_{{description}}`
**Rollback:** {{exact SQL or description of rollback}}

```sql
CREATE TABLE {{table_name}} (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  -- list every column with type, constraints, defaults
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- indexes with rationale
CREATE INDEX idx_{{table}}_{{column}} ON {{table}}({{column}});
-- why: {{rationale for this index}}
```

**Enum/status values:**

- `{{column}}`: {{value1}}, {{value2}}, {{value3}}

**Relationships:**

- `{{column}}` -> `{{other_table}}({{column}})` (FK, CASCADE | SET NULL | RESTRICT)

---

## 6. Service & Module Design

<!-- Repeat for every new or significantly modified service/module. -->

### 6.X {{Service/Module Name}}

**File:** `path/to/service.ts` (NEW | MODIFY)
**Purpose:** {{one-line purpose}}

**Public interface:**

```typescript
function processPayment(
  orderId: UUID,
  amount: Decimal,
  currency: string
): Promise<PaymentResult>
```

**Error cases:**

| Error | Condition | Propagation |
|-------|-----------|-------------|
| `OrderNotFoundError` | orderId not in DB | Throws -> controller returns 404 |

**Dependencies:**

- `path/to/repository.ts` -- {{what it uses from this module}}

---

## 7. Security Considerations

### 7.1 Auth Model

| Endpoint / Surface | Auth Method | Roles | Notes |
|-------------------|-------------|-------|-------|
| POST /api/v2/payments | JWT | admin, manager | ... |

### 7.2 Data Classification

| Data Field | Classification | Handling |
|-----------|---------------|----------|
| payment.amount | PII-financial | Encrypt at rest, audit log access |

### 7.3 Threat Surface

| Threat | Endpoint/Component | Mitigation |
|--------|-------------------|------------|
| SQL injection | POST /api/v2/payments | Parameterized queries via ORM |

### 7.4 Input Validation Summary

| Field | Endpoint | Rules |
|-------|----------|-------|
| orderId | POST /payments | UUID format, exists in DB |

---

## 8. Migration Strategy

### 8.1 Migration Order

1. `migrations/{{YYYYMMDD}}_{{name}}` -- {{description}}

### 8.2 Rollback Plan

| Step | Action | Verification |
|------|--------|-------------|
| 1 | Run rollback migration | Verify table dropped/reverted |
| 2 | Deploy previous version tag | Health check passes |

### 8.3 Backward Compatibility

| Change | Backward Compatible? | Migration Note |
|--------|---------------------|----------------|
| ... | Yes / No | ... |

---

## 9. Validation Criteria

<!-- What must be verified before merge.
     NOT a testing strategy — just the acceptance gates. -->

- [ ] All REQs from spec are satisfied (trace each one)
- [ ] All NFRs from spec are met (cite measurements)
- [ ] No regressions in existing functionality
- [ ] {{feature-specific validation criterion}}
- [ ] `verification-report.md` covers every REQ/NFR with concrete evidence (hard-fail rule)

### 9.1 Verification Plan

<!-- Full REQ/NFR -> verification mapping. Evidence lands in
     spec/{feature}/{subfeature}/verification-report.md (template:
     .claude/templates/verification-report.md). Drafted during
     /implementation, executed and committed by /verification. -->

#### 9.1.1 Automated Coverage

| REQ/NFR | AC | Test Layer (unit / integration / E2E) | Test File | Command |
|---------|-----|---------------------------------------|-----------|---------|
| REQ-001 | AC-001 | integration | `test/{{path}}.test.ts` | `{{test runner invocation}}` |

#### 9.1.2 Manual Procedures

<!-- Omit if all verification is automated. -->

| REQ/NFR | AC | Procedure Doc | Operator Role | Evidence Artifact |
|---------|-----|---------------|----------------|--------------------|
| REQ-00X | AC-00X-01 | `docs/manual/{{proc}}.md` | QA | screenshot + session notes |

#### 9.1.3 Log / Metric Inspection

<!-- Omit if no NFRs rely on observability evidence. -->

| NFR | Signal / Metric | Source Command | Threshold |
|-----|-----------------|-----------------|-----------|
| NFR-001 | p95 latency | `{{bench command}}` | < 100ms |

#### 9.1.4 Evidence Lifecycle

- During `/implementation`: rows added to `verification-report.md` with `Test Location` + `Command`; `Result` left blank.
- During `/verification`: commands executed, Results filled, verdict decided. Any row without passing evidence triggers a FAIL verdict (see `skills/verification/references/deviations.md`).

## 10. Risks & Tradeoffs

| Risk | Severity | Likelihood | Mitigation |
|------|----------|-----------|------------|
| {{risk description}} | High/Medium/Low | High/Medium/Low | {{specific mitigation}} |

---

## Appendix: Depth Self-Check

Before submitting this plan for review, verify:

- [ ] Every FR from the spec is mapped to at least one plan section (Section 1.2)
- [ ] Every NFR from the spec is addressed (Section 1.3)
- [ ] Every endpoint has exact route, JSON shapes, error table, validation rules, and file path (Section 4)
- [ ] Every database change has full SQL, column types, indexes, migration name, and rollback (Section 5)
- [ ] Every service has file path, typed function signatures, and error case table (Section 6)
- [ ] Security section covers auth per endpoint, data classification, and threat surface (Section 7)
- [ ] No forbidden phrases: "appropriate", "relevant", "proper", "similar to", "as needed", "etc.", "standard", "will be implemented", "TBD"
- [ ] All file paths reference existing files or are marked NEW
- [ ] Technical Context section documents inherited standards and tech stack
