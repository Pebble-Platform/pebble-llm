---
name: na-analyze-requirement
description: "[Planning] Analyze a raw request/requirement — classify it, assess feasibility, define scope, and produce a spec document (01-spec.md). Use as the first step of the planning workflow — before solution design."
argument-hint: "<raw request or requirement description>"
---

> **[IMPORTANT]** Use `TaskCreate` to break ALL work into small tasks BEFORE starting — one task per workflow step (1–7), plus a final Self-Check task.

## Quick Summary

**Goal:** Analyze a raw request and produce a structured `01-spec.md` ready to feed into Phase 2 (Solution Design).
**Workflow:** Capture & Classify → Context → Feasibility → Decompose (Big feature only) → Refine → Write → Self-Check.
**Key rule:** Spec focuses on WHAT, not HOW. The body must be readable by a BA/PO with no repo access; technical details live in the Engineering Appendix.

---

## When to Use

- First step of the planning workflow, before solution design.
- When a new request needs scope, feasibility, and testable acceptance criteria before implementation.
- Complements `/scan-requirement` (which produces a RAD): run this after the RAD, or directly when the request is already well-scoped.

---

## Input / Output

**Input:** A raw request — user story, bug report, technical task, PRD excerpt, Slack/email summary, or free-text. Access via `$ARGUMENTS` or from the user's message.

**Output Path Resolution:**

| Scenario | Output path |
|---|---|
| Inside `/plan` workflow (ticket known) | `specs/tickets/{id}/01-spec.md` |
| Standalone (no ticket) | `plans/{slug}/01-spec.md` |
| Big feature sub-spec | `{parent-dir}/sub/{sub-slug}/01-spec.md` |
| Rejection spec | same as normal path; frontmatter `status: rejected` |

---

## Tool Palette

| Tool | Role | Fallback if unavailable |
|---|---|---|
| `gitnexus_query` | Find execution flows touched by the request | `Grep` + `Glob` on concept keywords |
| `gitnexus_context` | Callers/callees of a named symbol | `Grep` for symbol name across repo |
| `gitnexus_impact` | Blast radius (upstream callers) for edits | `Grep` for callers of the changed symbol |
| `AskUserQuestion` | Clarify ambiguity, confirm classification | Autonomous Fallback (below) |

**Autonomous Fallback:** If `AskUserQuestion` is not in the palette (batch / agent spawn), do NOT block. Make reasonable assumptions, record each in Open Questions with a confidence tag (High/Medium/Low) and rationale, and set frontmatter `status: draft — assumptions made`. Never silently guess Tier 2 dimensions (security, compliance, revenue). Full protocol: `references/context-feasibility.md` → Autonomous Fallback.

---

## Workflow

### 1. Capture & Classify

Structure the raw request and classify its Type. **Name what's confusing.** If the request is ambiguous, multiple interpretations exist, or a simpler approach is visible, surface it — use `AskUserQuestion` to resolve (or Autonomous Fallback).

**Capture fields:**

| Field | Value |
|---|---|
| Requester | name, role |
| Raw Request | verbatim quote or summary |
| Core Problem | the actual problem being solved |
| Constraints | deadline, budget, technology, compliance |
| Priority | Critical / High / Medium / Low |

**Type (decides routing — Type wins over Size):**

| Type | Indicators | Workflow branch |
|---|---|---|
| **New feature** | No existing implementation, new user flow, new module | Full (Steps 2 → 3 → 5 → 6 → 7) |
| **Improvement** | Existing feature enhanced, refactored, optimized, or tech-debt repaid | Full (Steps 2 → 3 → 5 → 6 → 7) |
| **Fix bug** | Something broken, regression, unexpected behavior | Lightweight (`references/type-branches.md` → Lightweight Spec (Fix bug)) |
| **Big feature** | Spans services / layers, effort in weeks+, multiple independent slices | Decompose (Step 4) then spawn sub-specs |

**Size (scopes the depth of each section within the chosen Type):**

| Size | Examples | Depth |
|---|---|---|
| Skip | Typo fix, config value change, dep bump | No spec — just do it |
| S | Single-file fix, add a field to existing API, update validation rule | Small-request sections only (see Step 6) |
| M / L / XL | Multi-file feature, new endpoint, schema migration, new service | Full section set |

> **Type wins.** A Fix bug is always lightweight; a Big feature always decomposes; Size only controls how deeply each remaining section is filled.

### 2. Gather Context

Collect enough evidence to write a defensible spec. Bounded — not a full codebase read. See `references/context-feasibility.md` → Gather Context for the budget, business-context search order, and tool sequence.

**Side-Effect Check via GitNexus (MANDATORY when repo is indexed).** Run `mcp__gitnexus__list_repos` first.

- If indexed, both passes are required:
  1. **Wiki pass** — query the GitNexus wiki for existing feature pages whose scope overlaps the request. Enumerate every affected feature, module, or flow and capture the wiki citation.
  2. **Relationship pass** — for each candidate symbol/module surfaced by the wiki or the request, run `gitnexus_query`, `gitnexus_context`, and `gitnexus_impact` to list upstream callers and downstream dependents.
- Record every finding as a **Side Effect** bullet in the spec (Boundaries / Out-of-Scope or Open Questions): `{affected area} — {why impacted} — {gitnexus evidence}`.
- If the graph reports stale, mark findings advisory and add an Open Question.
- If the repo is NOT indexed, fall back to the regular tool sequence in `references/context-feasibility.md` and note "gitnexus not indexed — side effects assessed from docs + grep" in Open Questions.

### 3. Assess Feasibility

Evaluate Tier 1 (code-assessable) and flag Tier 2 (human input) dimensions. Produce a verdict: Feasible / Conditionally / Not feasible. See `references/context-feasibility.md` → Feasibility Assessment.

- **Not feasible** → write a rejection spec (`references/type-branches.md` → Rejection Spec) and stop.
- **Big feature** → go to Step 4.
- Otherwise → go to Step 5.

### 4. Decompose (Big feature only)

Break the work into independently specifiable, testable, and mergeable sub-tasks. Produce a parent spec with a Decomposition table; spawn sub-specs later in dependency order. See `references/type-branches.md` → Decompose (Big feature only).

### 5. Refine Requirements

For New feature / Improvement / each Big feature sub-task, produce:

- **Normative requirements** (`REQ-xxx`, MUST / MUST NOT / SHOULD) — atomic, testable, solution-agnostic
- **Invariants** — conditions that MUST hold before/during/after the change
- **Acceptance Criteria** (`AC-xxx`, WHEN/THEN) — linked back to REQs, covering happy + failure/edge cases
- **Risks** with Impact (Critical/High/Medium/Low) + Mitigation
- **Scope** — explicit In / Out lists
- **Dependencies** — blocking work, recorded in Open Questions or Risks

Full detail + body-vs-appendix rewrite examples: `references/spec-authoring.md` → Refine Requirements.

### 6. Write Spec Document

Compile into the spec template. Output path comes from the Output Path Resolution table above. Every spec has a **body** (reviewer-facing) and an **Engineering Appendix** (engineering-only).

**Body sections** (MUST be readable by a BA/PO with no repo access — no file paths, no code identifiers, no SDK terms):

`Purpose` · `Scope` (In/Out) · `Problem Statement` · `Normative Contract` · `Invariants` · `Acceptance Criteria` · `Verification Matrix` · `Risks and Mitigations` · `Open Questions`

**Engineering Appendix — Affected Areas** (last section, always) — the ONLY place `file:line`, class/function/variable names, cookie/constant names, and SDK terms are allowed.

Analysis-to-template mapping and body-vs-appendix rewrite examples: `references/spec-authoring.md` → Write Spec Document.

**Small-request (Size S) exception:** produce the same spec but only fill Frontmatter, Purpose, Scope, Problem Statement, Normative Contract, Acceptance Criteria, and Open Questions. Omit the other body sections entirely (no empty stubs).

**Frontmatter fields:**

| Field | Value |
|---|---|
| `title` | from ticket or request summary |
| `ticket` | ticket ID or slug |
| `status` | `draft` \| `draft — assumptions made` (autonomous) \| `draft (decomposed)` (Big feature parent) \| `rejected` |
| `owner` | requester's team or person |
| `date` | today |
| `normative` | `true` (or `false` for rejection specs) |
| `parent` | sub-specs only: `../../01-spec.md` |

### 7. Self-Check

Before returning, run the Self-Check against the relevant checklist in `references/spec-authoring.md` → Self-Check:

- **Standalone spec** (New feature / Improvement / Fix bug / any Big feature sub-spec) — checklist includes mechanical REQ ↔ AC ↔ V linkage, body-audience greps, and appendix-location check.
- **Big feature parent spec (decomposed)** — checklist verifies DAG, coverage, no leaked REQs, and parent-only cross-cutting concerns.

It is a mechanical read-through of the produced spec — do NOT tick from memory. If any box fails, fix before handing off.

---

## Key Rules

- **WHAT, not HOW** — analyze the requirement, not the solution. Solution design is Phase 2.
- **Body = BA-readable.** If a product reviewer cannot state back (a) what will change, (b) what will not, (c) how they'll know it worked, and (d) which decisions are open, the body has failed the audience check.
- **Evidence-based** — every affected area in the appendix has a real `file:line`. No imagined references.
- **Flag, don't guess** — Tier 2 unknowns (security, compliance, revenue) go to Open Questions, never silent assumptions.
- **YAGNI** — analyze only what the request asks for; no speculative future needs.
- **Feasibility before refinement** — do not invest in REQs/ACs for a rejected request.

---

## Incremental Update

When requirements change for an existing spec, update in place rather than starting fresh. Full procedure (read existing → diff → update only affected sections → append Changelog → preserve path): `references/context-feasibility.md` → Incremental Update.
