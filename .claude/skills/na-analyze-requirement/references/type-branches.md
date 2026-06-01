# Type Branches — na-analyze-requirement

The three non-default workflow branches that replace or augment Steps 4–6 of the main workflow:

- **Big feature** decomposition (Step 4 — mandatory when Type=Big feature)
- **Fix bug** lightweight spec (replaces Steps 3–5 when Type=Fix bug)
- **Rejection spec** (replaces Steps 4–5 when Feasibility = ❌)

Load this file when Step 1 routes into one of these branches, or when Step 3 concludes not-feasible.

> Output paths come from the main `SKILL.md` Output Path Resolution table — do not invent alternate locations in this file.

---

## 4. Decompose (Big feature only)

**Skip this step for Fix bug / Improvement / New feature.** If the Type is **Big feature**, do NOT try to write one giant spec. Break the work into spec-sized sub-tasks first.

**Goal:** Produce a set of sub-tasks where each is independently specifiable, independently testable, and independently mergeable. Each sub-task is its own Type (**New feature**, **Improvement**, or **Fix bug**). If any sub-task is still a **Big feature** after one pass, decompose it again.

### Actions

1. **Identify natural seams.** Use Step 2's context to find existing module/layer boundaries. Good seams:
   - **Layer** — DB migration / backend API / frontend UI / infra
   - **Feature** — user-facing capabilities that can ship independently
   - **Data domain** — independent models or bounded contexts
   - **Rollout phase** — foundation → feature → polish
2. **Split along seams.** For each sub-task, record:
   - `Slug` — kebab-case identifier (e.g. `schema-migration`, `batch-upload-api`, `multi-file-picker`)
   - `Purpose` — 1–2 sentences
   - `Type` — must be **New feature**, **Improvement**, or **Fix bug** (never another **Big feature** — decompose again if it is)
   - `Depends on` — other slugs that must ship first (forms a DAG)
   - `In scope` / `Out of scope` — explicit bullets, enforcing that each sub-task owns a distinct slice
3. **Validate the decomposition:**
   - Dependency graph is a **DAG** (no cycles)
   - **Union of all sub-task In scope = original request scope** (no gap)
   - Every sub-task is **independently valuable** or explicitly tagged as a foundation that unblocks others
   - No sub-task is a **Big feature** (never leak a Big feature through)

### Decomposition table (goes into the parent spec)

| Slug | Purpose | Type | Depends on | Order |
|---|---|---|---|---|
| `schema-migration` | Add `document_batch` table + relations | Improvement | — | 1 |
| `batch-upload-api` | Batch upload endpoint + validation + per-file status | New feature | `schema-migration` | 2 |
| `multi-file-picker` | Multi-file picker + batch progress UI in chat sidebar | New feature | `batch-upload-api` | 3 |

### Output structure

- **Parent spec** at the path resolved by the main skill's Output Path Resolution table holds:
  - Frontmatter with `status: draft (decomposed)`
  - `Purpose`, `Problem Statement`
  - **Cross-cutting Invariants** (those that span sub-tasks)
  - **Cross-cutting Risks** (integration, rollout, compat)
  - **Affected Areas** at the system level
  - **Decomposition** table (the table above)
  - **Open Questions** that affect the whole decomposition
  - NO `Normative Contract`, NO `Acceptance Criteria`, NO `Verification Matrix` — those live in the sub-specs
- **Sub-specs** at the sub-spec path (see main SKILL Output Path Resolution):
  - Each is a **full spec** produced by running Steps 2 → 3 → 5 → 6 → 7 scoped to that sub-task
  - Has its own `REQ-xxx`, `AC-xxx`, `V-xxx`, Invariants (local), Risks (local)
  - Frontmatter includes `parent: ../../01-spec.md`

### Loop after decomposition (default: spans multiple invocations)

A single invocation rarely has context budget for a parent spec + every sub-spec. The default flow is:

1. **This invocation** — produce the parent spec only (frontmatter, Purpose, Problem Statement, cross-cutting Invariants/Risks, Affected Areas, Decomposition table). Tag every row in the Decomposition table `status: pending`. Do NOT begin sub-specs in the same invocation unless the "single-pass exception" below applies.
2. **Subsequent invocations** — each one picks the next `pending` sub-task in dependency order and runs Steps 2 → 3 → 5 → 6 → 7 scoped to that sub-task. As each sub-spec lands, flip the parent Decomposition row: `pending` → `in progress` → `draft`.

**Single-pass exception:** You MAY produce parent + all sub-specs in one invocation only if BOTH hold: (a) the decomposition has ≤ 3 sub-tasks AND (b) each sub-task is small enough that Step 2 for all of them combined fits within the Step 2 budget (see `context-feasibility.md#budget`). Otherwise STOP after the parent — a shallow oversized run is worse than a deep focused one.

### Self-check for decomposition

```
- [ ] No sub-task is a Big feature (recursive decomposition done)
- [ ] Dependency graph is a DAG — no cycles
- [ ] Union of sub-task In scope covers the original request (no gap)
- [ ] No sub-task scope overlaps another (no double-write)
- [ ] Cross-cutting invariants live in the parent spec only, not duplicated
- [ ] Parent spec has NO REQ-xxx (REQs belong to sub-specs)
- [ ] Every sub-spec has a declared parent in its frontmatter
```

### Mini-example: Big feature parent spec

**Request:** "Migrate document ingestion from Postgres-only to Postgres + OpenSearch hybrid index so chat retrieval can use BM25 + vector."

After Step 4, the parent spec contains cross-cutting concerns and a Decomposition table only — no `REQ`, `AC`, or `V-xxx`. Sub-specs are produced by subsequent invocations in dependency order.

```markdown
---
title: Hybrid document index (Postgres + OpenSearch)
ticket: NA-2043
status: draft (decomposed)
owner: platform
date: 2026-04-10
normative: true
---

## Purpose
Introduce a hybrid retrieval path (BM25 + vector) without breaking current Postgres-only callers.

## Problem Statement
Retrieval quality is bottlenecked by single-index ranking. Adding OpenSearch alongside Postgres
unlocks hybrid scoring, but must land incrementally to avoid a regression in the live chat flow.

## Cross-cutting Invariants
- Existing document IDs remain stable across the migration.
- Current single-index retrieval continues to work until the hybrid path is cut over.

## Cross-cutting Risks
| Risk | Impact | Mitigation |
|---|---|---|
| OpenSearch cluster outage during dual-write window | High | Write-path feature flag + fallback to Postgres-only |
| Schema drift between the two indexes | High | Shared migration runner with a single source-of-truth mapping |

## Decomposition
| Slug | Purpose | Type | Depends on | Order | Sub-spec |
|---|---|---|---|---|---|
| `opensearch-infra` | Provision + configure OpenSearch cluster & IaC | New feature | — | 1 | `pending` |
| `ingestion-dual-write` | Dual-write new docs to both Postgres and OpenSearch | New feature | `opensearch-infra` | 2 | `pending` |
| `backfill-existing` | One-time backfill of existing Postgres docs into OpenSearch | Improvement | `ingestion-dual-write` | 3 | `pending` |
| `hybrid-retrieval` | Switch chat retrieval to BM25 + vector ranking | New feature | `backfill-existing` | 4 | `pending` |
| `single-write-cutover` | Remove Postgres-only write path after monitoring window | Improvement | `hybrid-retrieval` | 5 | `pending` |
```

The parent stops here. Each `pending` sub-spec is produced later at its resolved path and flips the parent row to `draft` when it lands.

---

## Lightweight Spec (Fix bug)

For **Fix bug** requests, produce the spec with only these sections filled — leave the rest out entirely, do not include empty stubs. This is the output of the Fix-bug routing: Step 2-lite → Step 5-lite → Step 6-lite → Step 7.

### Step 2-lite (mandatory)

Identify the broken execution flow (`gitnexus_query` on the symptom) and run `gitnexus_impact` on the broken symbol to capture d=1 callers for regression coverage. (Fallbacks: `Grep` for the symptom string; `Grep` for callers of the broken symbol.)

> Understanding blast radius before touching existing code is required by the "Surgical Changes" rule in `CLAUDE.md` — a bug fix is an edit. Do not skip this even though Fix bug is a lightweight flow.

### Step 5-lite (mandatory)

Write the minimal REQ/AC/V set below — one REQ per broken behavior, one AC that replays the reproducer, one V that pins the regression test.

### Spec contents

- Frontmatter
- Purpose (one sentence: what the bug is)
- Scope (In scope / Out of scope)
- Problem Statement (what's broken, how to reproduce)
- Normative Contract (usually 1–3 REQs — typically "the broken behavior MUST no longer occur")
- Affected Areas (from Step 2-lite — `file:line` of the broken symbol + d=1 callers)
- Acceptance Criteria (include the original reproducer as one AC)
- Verification Matrix (at least one entry per REQ — bugs stay testable)
- Open Questions (if any)

Skip Step 3, Step 4, and the fuller Step 5. Run Step 7 Self-Check against the standalone checklist in `spec-authoring.md#standalone-spec-new-feature--improvement--fix-bug-or-any-big-feature-sub-spec`.

---

## Rejection Spec (Feasibility = ❌)

When Step 3 concludes **Not feasible**, skip Steps 4 and 5 entirely and write a minimal rejection spec at the resolved output path with ONLY these sections. Do not leave other template sections as empty stubs — omit them.

**Frontmatter:** `status: rejected`, `normative: false` (a rejected spec is not a contract).

### Sections

- **Purpose** — 1 sentence: what was requested.
- **Problem Statement** — what the requester is trying to solve.
- **Affected Areas** — the investigation done before rejecting (proves it wasn't dismissed lightly). Include `file:line` references from Step 2.
- **Feasibility Verdict** — dedicated section replacing Normative Contract, containing:
  - The verdict (`❌ Not feasible`) and the primary reason in one line.
  - **Blocking reasons** — bulleted, each with concrete evidence (`file:line`, impact count from `gitnexus_impact`, architectural conflict, or constraint violation).
  - **What would unblock it** — conditions under which the request could become feasible (e.g. "after auth service migration lands", "if budget for external API is approved", "if data retention policy is relaxed").
  - **Suggested alternatives** — pointers to cheaper/feasible adjacent options, if any.
- **Open Questions** — anything the requester should confirm before re-opening.

After writing, return the rejection spec path to the caller and surface the verdict + top blocking reason to the user.
