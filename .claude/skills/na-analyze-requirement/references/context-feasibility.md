# Context & Feasibility — na-analyze-requirement

Detailed guidance for **Step 2 (Gather Context)** and **Step 3 (Feasibility)**, plus the Autonomous Fallback and Incremental Update protocols. Load this file when the main workflow enters Step 2, when the feasibility verdict is in doubt, or when running in autonomous / incremental mode.

> Output Path Resolution, Tool Palette, and the Type / Size tables live in the main `SKILL.md`. Do not duplicate them here.

---

## Gather Context

Collect the minimum evidence needed to write a defensible spec. Keep this bounded — do not try to read the whole codebase.

### Budget (enforced — stop at the first cap hit, log what you skipped in Open Questions)

| Action | Cap |
|---|---|
| `gitnexus_query` calls | ≤ 3 |
| `gitnexus_context` calls | ≤ 5 |
| `Read` + `Grep` calls combined | ≤ 10 |
| Wall time on context gathering | ≤ 15 minutes of agent work |

Deeper exploration belongs in Phase 2 (solution design), not Phase 1. The goal here is to know *enough to write testable REQs* — not to understand the full implementation.

### Business context (check in order, stop at first hit)

1. `high-level-documents/` — if present
2. `docs/` — project documentation folder
3. Previous specs — `specs/tickets/*/01-spec.md`, `plans/*/01-spec.md`

If none exist, record "No project-level documentation found" in the spec and proceed.

### Code context (GitNexus first, Grep as fallback)

1. `gitnexus_query({query: "<feature concept>"})` → list the execution flows (processes) the request touches.
2. For each key symbol mentioned or implied: `gitnexus_context({name: "..."})` → find callers, callees, and participating processes.
3. Record `file:line` references for every affected area you identify — these feed the **Affected Areas** table in the spec.

### Related requirements

Scan previous specs for overlaps or conflicts with the current request. Record any found as Open Questions (to resolve with the PO) or Risks.

---

## Feasibility Assessment

Judge whether the request can be built within acceptable constraints.

### Tier 1 — Code-assessable (always fill)

| Dimension | Key Questions | Tool |
|---|---|---|
| **Architecture Impact** | Does this fit existing architecture? New service? Cross-service calls? | `gitnexus_query`, `Read` relevant modules |
| **Data Model Impact** | Schema changes? Migration? Consistency? | `Grep` for model files, ORM schemas |
| **Integration Complexity** | External APIs? Third-party deps? Cross-team work? | Read deps, search for existing clients |
| **Blast Radius** | For Improvement / Fix bug: who breaks if we touch the impacted symbols? | `gitnexus_impact({target, direction: "upstream"})` — record d=1 (WILL BREAK) and d=2 (LIKELY AFFECTED) |
| **Performance Impact** | Expected load? Latency requirements? Scalability? | Read existing benchmarks if any |
| **Effort Estimate** | Rough effort (hours / days / weeks / months) — may justify escalating from New feature to Big feature | — |

### Tier 2 — Requires human input (flag, do not guess)

| Dimension | Key Questions | If unknown |
|---|---|---|
| Security & Compliance | Auth/authz changes? PII handling? Regulatory requirements? | Add to Open Questions, flag `Needs Human Review` |
| Revenue Impact | Revenue-critical path? SLA? | Add to Open Questions |
| Business Priority | Confirmed by stakeholder? Deadline validated? | Use ticket priority as-is |

### Feasibility verdict

| Verdict | Criteria | Next |
|---|---|---|
| ✅ Feasible | Fits architecture, reasonable effort, acceptable risk | Step 4 (if Big feature) or Step 5 |
| ⚠️ Conditionally feasible | Needs migration, phased rollout, or dependency resolution | Document conditions → continue |
| ❌ Not feasible | Architecture mismatch, prohibitive effort, unacceptable risk | Write a rejection spec (see `type-branches.md#rejection-spec`), skip Steps 4 and 5 |

### Escalation check

If the effort estimate grew beyond "fits a single spec" during Step 3, escalate the Type to **Big feature** and go to Step 4 (Decompose) — see `type-branches.md#4-decompose-big-feature-only`.

---

## Type Playbook (per-Type focus for Steps 2–5)

| Type | Extra focus in Context (2) | Extra focus in Feasibility (3) | Extra focus in Refinement (5) |
|---|---|---|---|
| **Fix bug** | Trace the failing execution flow; find the reproducer in the wild | `gitnexus_impact` upstream on the broken symbol | REQs framed as "regression no longer occurs"; ACs include the reproducer |
| **Improvement** | Read the current implementation end-to-end; quantify the problem (perf, complexity, callers) | Migration path, backward compatibility, ROI vs risk of delay | Current-behavior invariants (preserve what works); REQs express measurable improvement (e.g., "p95 latency ≤ N ms") |
| **New feature** | Find the nearest existing pattern to model after | Architecture fit, new integration seams, new data model | Full REQ set; carefully bound Out of Scope against adjacent features |
| **Big feature** | Map the full landscape across layers; identify seam candidates | Architecture shift, cross-team coordination, phased rollout | Cross-cutting invariants only (in parent spec); detailed REQs live in sub-specs |

---

## Autonomous Fallback

If running in batch/autonomous mode (no user available, e.g. agent-spawned without interactive tools):

1. **Do not block on `AskUserQuestion`** — it may not be in the agent's tool palette.
2. **Make reasonable assumptions** from ticket data, prior specs, and code context.
3. **Document every assumption** explicitly in Open Questions with a confidence tag (High / Medium / Low) and the rationale.
4. **Set status to `draft — assumptions made`** instead of `draft`.
5. **Infer Type** from request wording; flag with confidence in Open Questions.
6. **Never silently guess Tier 2** (security, compliance, revenue) — always flag as Open Questions.

---

## Incremental Update

When a request changes for an existing spec, do NOT start from scratch:

1. **Read the existing spec** at the expected path (use the main skill's Output Path Resolution).
2. **Diff the change** — identify which template sections are affected.
3. **Update only affected sections** (map template sections to analysis steps):
   - Scope change → `Scope`, `Normative Contract`, `Acceptance Criteria`, re-run Step 3
   - New constraint → `Risks and Mitigations`, re-run Step 3 verdict
   - Priority change → frontmatter only
   - Requirement clarification → `Problem Statement`, specific `REQ`/`AC` entries
4. **Preserve the original file path** — do not create a new file.
5. **Append a Changelog entry** at the bottom:

   ```markdown
   ## Changelog

   | Date | Change | Sections Updated | Reason |
   |------|--------|------------------|--------|
   | {date} | {brief description} | {sections} | {why} |
   ```

**Incremental vs fresh:**
- **Incremental** — core problem unchanged; details shifted (scope adjustment, new constraint, priority).
- **Fresh** — the request has mutated so fundamentally that the original spec is no longer relevant.
