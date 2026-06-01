---
title: "FIX STEPS — {one-line headline}"
ticket: "NA-XXXX"
status: "runbook"
related: ["./bug-<slug>.md", "./bug-<slug>-solution.md"]
---

# FIX STEPS — {one-line headline}

- **Ticket**: [NA-XXXX](https://dev.azure.com/neurondAI/Neurond%20Assistant/_workitems/edit/XXXX)
- **Bug**: [bug-&lt;slug&gt;.md](./bug-<slug>.md)
- **Solution narrative**: [bug-&lt;slug&gt;-solution.md](./bug-<slug>-solution.md)
- **Scope**: implementation order matters — follow phases top to bottom.

This is a checklist. Every step has: what to change, where, how to verify before moving on. Snippets are illustrative — read surrounding code before pasting.

---

## Estimated effort

| Phase | Effort | Risk |
|-------|--------|------|
| Phase 0 — Prep & baselines | {X} day | Low |
| Phase 1 — {data fix / pricing rates / etc.} | {X} day | {Low/Med/High} |
| Phase 2 — {write-path / core change} | {X} day | {Low/Med/High} |
| Phase 3 — {read-path / cleanup} | {X} day | {Low/Med/High} |
| Phase 4 — Tests | {X} day | Low |
| Phase 5 — Staging rollout & verification | {X} day | Medium |
| Phase 6 — Historical backfill (optional) | {X} day | Medium |
| Phase 7 — PROD rollout | {X} day | Medium |
| **Total** | **~{N} days** for one engineer |

---

## Phase 0 — Prep and baselines

Before touching code, capture the **current** state so you can prove the fix worked.

### 0.1 Create the branch

```bash
git checkout -b fix/NA-XXXX-<slug> dev
```

### 0.2 Pick reference rows / events for regression

Identify 2–3 deterministic records that exercise the bug. Record their IDs, raw payloads, and current broken outputs. These become test fixtures **and** the staging acceptance set.

### 0.3 Snapshot the affected surface

Screenshot the dashboard / page / API response that is currently wrong. Attach to the ticket. This is the "before" evidence for the acceptance review.

### 0.4 Verify the bug locally

Run the repro from `bug-<slug>.md §4.2` on a dev DB seeded with the reference rows. Confirm the broken behavior reproduces. If not, the local data doesn't trigger it — pick different rows.

---

## Phase 1 — {first ordering-critical change, e.g. data / migrations / pricing}

**Why first**: explain the ordering constraint. If a later phase depends on a metric / rate / column existing, do that here so the later phase doesn't log warnings or crash.

**File(s) / surface**: …

### 1.1 {Action}

```sql
-- or code block illustrating the change
```

### 1.2 Verify

A query / command that confirms the change landed. The next phase is **blocked** until this verifies.

---

## Phase 2 — {keystone change from solution §3}

**Why**: links to S1 in the solution doc.
**File**: `path/to/file.ts`

### 2.1 Current behavior

```typescript
// before — overlapping / broken
```

### 2.2 After

```typescript
// after — disjoint / correct
```

### 2.3 Verify locally

Hand-feed the reference payloads through the function (REPL or test). Assert outputs match the table from `bug-<slug>-solution.md §7`.

---

## Phase 3 — {read-path / pricing / cleanup}

**Why**: links to S2 / S3 in the solution doc.
**File**: …

### 3.1 Change

…

### 3.2 (Optional) defensive hardening

If S2 marks an optional follow-up, gate it behind a brief note explaining when to enable.

### 3.3 Verify

Run unit tests (Phase 4). Don't commit yet.

---

## Phase 4 — Tests

### 4.1 Update {unit-test file}

Add or update fixtures:

| Fixture | Input | Expected output |
|---------|-------|-----------------|
| `pure_path` | … | … |
| `mixed_path` | … | … |
| `edge_case` | … | … |

Assert each: returned value is correct AND the invariant from `bug-<slug>-solution.md §2` holds.

### 4.2 Update {integration-test file or fixture}

Re-baseline expected values for the reference rows from Phase 0.2. Hand-compute. Assert within tolerance (e.g. ±$0.0001 for cost).

### 4.3 Run

```
pnpm lint:fix
pnpm type-check
pnpm test:unit
```

All green before moving on.

---

## Phase 5 — Staging rollout & verification

### 5.1 Deploy to staging

Standard branch deploy. Note any data prerequisites from Phase 1.

### 5.2 Generate a representative event

Send the action that triggers the changed code path. Pick the resulting record.

### 5.3 Assert invariant on the new record

Provide the SQL / log query. Confirm the invariant from §2 of the solution holds. Confirm the numbers match what the provider / source-of-truth says, by hand.

### 5.4 Check the affected surface

Open the dashboard / page. Confirm the displayed value matches §5.3.

### 5.5 Regression check

Exercise a non-affected path (different provider / different mode). Confirm output is byte-identical to pre-fix. If any regression, **stop and debug**.

---

## Phase 6 — Historical backfill (optional, recommended for ticket closure)

Without this, the captured-incident period stays visible at the inflated values on the dashboard.

### 6.1 Scope

- **Targeted**: only the affected user / window (closes the ticket).
- **Full**: all rows since DB inception (separate ticket).

Targeted is recommended.

### 6.2 Backfill script

One-shot script (NOT a migration; this is a data correction):

1. Select target rows.
2. For each row, recompute corrected values per the invariant.
3. UPDATE the row.

### 6.3 Safety

- Run **read-only** (SELECT + log diff) first; eyeball 10 rows.
- Wrap UPDATE in a transaction; produce a before/after CSV.
- Run in staging against a copy of PROD first.

### 6.4 Re-roll any aggregations

If derived rollup tables exist (e.g. daily analytics), recompute them for the affected window.

### 6.5 Verify

Re-screenshot the affected surface for the captured-incident window. Confirm corrected values.

---

## Phase 7 — PROD rollout

### 7.1 Merge

PR title: `fix({module}): [NA-XXXX] {summary}`
Body: link to bug, solution, fix-steps.

### 7.2 Deploy code

Standard release. Any Phase 1 data prereqs should already be in PROD.

### 7.3 Run targeted backfill (Phase 6) in PROD

If applicable.

### 7.4 Update ticket

Attach:
- "Before" screenshot (Phase 0.3)
- "After" screenshot (Phase 6.5)
- Note: true source-of-truth value for the window was {X}, now displayed accurately.

### 7.5 Notify stakeholders

Short note to the team that owns the affected surface, noting any expected number drops/shifts.

---

## Rollback plan

If Phase 5 or 7 surfaces unexpected behavior:

1. **Code rollback**: revert the PR. New events return to previous behavior. (Note: this leaves Phase 1 data fixes in place — they're typically harmless on rollback; confirm per phase.)
2. **Backfill rollback** (Phase 6): use the before/after CSV from 6.2 to restore rows.
3. **Pricing/data rollback** (Phase 1): document per row whether it's safe to leave or must revert.

The risky phase is the backfill — gate it behind manual confirmation, not auto-run on deploy.

---

## Definition of done

Mirror `bug-<slug>.md §7` / `bug-<slug>-solution.md §9` as a checkbox list:

- [ ] AC 1 verified — {what was checked, where}
- [ ] AC 2 verified — …
- [ ] AC 3 verified — …
- [ ] Phase 5 staging verification passes for all reference rows.
- [ ] Phase 6 backfill (or its skip decision) is documented on the ticket.
- [ ] Phase 7 dashboards/surfaces confirm corrected values in PROD.
- [ ] Out-of-scope items from bug doc §6 are filed as separate tickets if not already.
