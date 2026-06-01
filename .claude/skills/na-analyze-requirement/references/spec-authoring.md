# Spec Authoring — na-analyze-requirement

Detailed guidance for **Step 5 (Refine Requirements)**, **Step 6 (Write Spec Document)**, and **Step 7 (Self-Check)**. Load this file when entering Step 5 of the main workflow, or when authoring a Big feature sub-spec.

> Output paths come from the main `SKILL.md` Output Path Resolution table. Context-gathering and feasibility rules live in `context-feasibility.md`. Type-specific branches (Big feature parent, Fix bug lightweight, Rejection) live in `type-branches.md`.

---

## Refine Requirements

**For New feature / Improvement requests, and for each sub-task produced by Step 4.** Transform the analyzed request into testable artifacts. This is where the spec's teeth get made.

Produce **all** of these:

**a. Normative requirements (`REQ-xxx`)** — the hard contract. Use MUST / MUST NOT / SHOULD:
- `REQ-001: <Subject> MUST <do something specific and verifiable>.`
- Each REQ must be **atomic** (one assertion), **testable** (can be mechanically verified), and **solution-agnostic** (no HOW).

**b. Invariants** — conditions that MUST hold at all times, before/during/after the change. Examples: "Existing session tokens continue to validate", "Uploaded files never exceed 50MB", "Chat history ordering is preserved".

**c. Acceptance criteria (`AC-xxx`)** — WHEN/THEN scenarios mapped back to REQs:
- `AC-001: WHEN <condition> THEN <expected outcome>. (satisfies REQ-001)`
- Cover happy path **and** failure/edge cases.
- Specific (no "fast"/"user-friendly"), testable, independent.

**d. Risks** — identify what could go wrong and how to prevent/recover. Draw from Step 3 findings:
- Every blast-radius caller from `gitnexus_impact` → candidate risk.
- Every migration, external dep, data change → candidate risk.
- Every Tier 2 unknown → candidate risk flagged as Open Question AND Risk.
- Populate the `Risks and Mitigations` table with Risk / Impact (Critical/High/Medium/Low) / Mitigation.

**e. Scope boundaries** — explicit In scope **and** Out of scope lists. For each adjacent area a reader might assume is included, explicitly exclude it.

**f. Dependencies** — anything that must be done before this work is unblocked. Record in Open Questions or Risks depending on certainty.

---

## Write Spec Document

Compile all analysis into the template. Output path is resolved by the main skill's Output Path Resolution table — do not invent alternate locations. Every section in the template must be filled or explicitly marked `N/A — <reason>`.

### Canonical template sections

This is the source of truth for spec sections. If `.claude/templates/spec.md` exists, it MUST match this list; if it does not exist yet, use this list directly.

**Body (non-technical reviewer-facing):**
`Purpose` · `Scope` (In/Out) · `Problem Statement` · `Normative Contract` · `Invariants` · `Acceptance Criteria` · `Verification Matrix` · `Risks and Mitigations` · `Open Questions`

**Appendix (engineering-only, at the very bottom):**
`Engineering Appendix — Affected Areas`

The body MUST be readable without opening any source file. The appendix is the **only** place where file paths, `file:line` refs, class/component/function/variable names, cookie or constant names, or SDK-specific terms may appear. If the template file has drifted from this list (extra or missing sections, or Affected Areas not in the appendix position), stop and raise it in Open Questions — do not silently adapt the mapping below.

### Analysis → Template mapping (cover every template section)

| Analysis output | Spec section | Body or Appendix |
|---|---|---|
| Core problem (Step 1) | **Purpose** + **Problem Statement** | Body — business language only |
| Scope In/Out (Step 5e) | **Scope** | Body — product-visible names only |
| Normative requirements (Step 5a) | **Normative Contract** | Body — no code identifiers in any REQ |
| Invariants (Step 5b) | **Invariants** | Body — paraphrase in business language |
| Acceptance criteria (Step 5c), linked to REQs | **Acceptance Criteria** | Body — WHEN/THEN in user-visible terms |
| Verification per REQ | **Verification Matrix** — every `REQ-xxx` needs at least one `V-xxx` entry (method, target, pass condition) | Body — describe tests by behavior, not by function name |
| Feasibility concerns + risks (Steps 3, 5d) | **Risks and Mitigations** | Body — risk statement and mitigation in business language |
| Tier 2 unknowns, dependencies, inferred Type | **Open Questions** | Body — phrased as product/design decisions, not engineering tasks |
| Affected code areas (Step 2, with `file:line`) | **Engineering Appendix — Affected Areas** (table, at the very bottom) | **Appendix only** — this is the only place in the spec where file paths, line numbers, class names, function names, cookie/constant names, and SDK-specific terms may appear |

#### Body-vs-appendix rewrite examples

Before authoring a REQ / AC / Invariant / Risk / OQ, take whatever you wrote during analysis and strip anything that would mean nothing to a BA. Examples:

| Raw analysis note (bad in body) | Body form (good) | Appendix form (good) |
|---|---|---|
| `REQ-005: chat requests MUST carry the extended-thinking flag through buildProviderOptions so Anthropic thinking block / Google thinkingConfig / OpenAI reasoningEffort is applied` | `REQ-005: When Extended thinking is on and the selected model supports it, subsequent chat requests MUST apply the configured extended-thinking behavior end-to-end.` | Appendix row lists `lib/ai/agent/shared/provider-options.ts:56-141` with note "continues to consume the thinking flag; no new backend params introduced" |
| `REQ-011: the SELECTED_CHAT_MODEL_ID cookie in consts\cookie-key.ts:2 MUST remain unchanged` | `REQ-011: The user's saved model preference MUST remain backward-compatible so that rolling back this change does not reset any user's previously-selected model.` | Appendix row lists the cookie constant and its file location with note "keep name and value format unchanged for rollback safety" |
| `Invariant: modelType === 'reasoning' still means isReasoningLocked (chat.tsx:135-138)` | `Invariant: Reasoning-only models continue to behave as 'thinking always on' — users cannot turn the mode off for them.` | Appendix row points to the chat screen state owner with note "preserve existing reasoning-locked behavior" |
| `Risk: attachment-dropdown.tsx:367 has handleThinkingToggle that conflicts with REQ-012` | `Risk: The current attachments menu already contains a thinking toggle, which conflicts with the stated "left menu stays unchanged" requirement. Decision needed before Phase 2.` | Appendix row points to the attachments menu file with note "existing in-menu thinking toggle — disposition TBD" |
| `OQ: should supportsExtendedThinking be a stored field or derived from modelType plus supportsXhighReasoning?` | `OQ: Should "supports extended thinking" be modelled as its own catalog field, or inferred from existing capability fields? (engineering decision, affects catalog migration shape)` | — (OQ does not belong in the appendix) |

### Frontmatter

- `title` — from ticket or request summary
- `ticket` — ticket ID or slug (see main skill Output Path Resolution for the exact format per scenario)
- `status` — `draft` (or `draft — assumptions made` for autonomous runs, `draft (decomposed)` for Big feature parents, `rejected` for infeasible requests)
- `owner` — requester's team or person
- `date` — today
- `normative` — `true` (or `false` for rejection specs)

---

## Self-Check

Before marking the task complete, verify the produced spec(s) against the relevant checklist.

### Standalone spec (New feature / Improvement / Fix bug, or any Big feature sub-spec)

> Before ticking the linkage boxes, **actually re-read the spec**. Build a list of every `REQ-xxx` ID, then for each one grep the AC section for the ID and the Verification Matrix for the ID. Do NOT tick from memory — mechanical cross-read only.

```
- [ ] Frontmatter: all 6 fields populated (sub-spec also has `parent`)
- [ ] Purpose + Problem Statement are clear and separate (Purpose = contract, Problem = why)
- [ ] Scope has BOTH In scope and Out of scope lists, phrased with product-visible names only
- [ ] Every REQ-xxx is atomic, testable, and solution-agnostic
- [ ] LINKAGE (mechanical): list every REQ-xxx → for each, find an AC that names it (e.g. "(REQ-001)" or "(satisfies REQ-001)") AND a Verification Matrix row whose mapping contains it. No unlinked REQ allowed.
- [ ] LINKAGE (reverse): no orphan AC or V-xxx — every AC and V row references at least one existing REQ-xxx.
- [ ] Engineering Appendix — Affected Areas is present as the LAST section of the spec and references real file:line locations
- [ ] Invariants stated or N/A with reason
- [ ] Risks table populated — each risk has Impact + Mitigation
- [ ] Open Questions captured for every unknown; no silent assumptions; each phrased as a product/design decision, not an engineering task
- [ ] No HOW in the body — solution decisions deferred to Phase 2
- [ ] AUDIENCE (mechanical): spec body (every section ABOVE `Engineering Appendix — Affected Areas`) contains ZERO file paths. Run these greps on the body only; each MUST return zero hits:
      - file extensions in body text: `\.(ts|tsx|js|jsx|py|sql|json|yml|yaml|md|css|scss)\b`
      - path separators in body text: backslash `\\` or forward-slash segments like `components/`, `lib/`, `app/`, `src/`, `consts/`, `types/`, `packages/`
      - line-number refs: `:\d{1,4}\b` inside fenced or backticked code spans
- [ ] AUDIENCE (mechanical): spec body contains ZERO code identifiers except product-visible names. Forbidden in body:
      - camelCase / PascalCase identifiers that name functions, hooks, components, types, or variables (e.g. `buildProviderOptions`, `ThinkingButton`, `useModel`, `isThinkingEnabled`, `modelType`, `handleThinkingToggle`, `tier`, `tagline`)
      - SDK-specific terms (e.g. `thinkingConfig`, `reasoningEffort`, `thinking block`, `provider-options`, `provider-options path`)
      - constant / cookie / env key names (e.g. `SELECTED_CHAT_MODEL_ID`)
      Allowed in body: product-visible labels as shown in the UI or spoken by users, quoted verbatim (e.g. "Extended thinking", "More models", "Connect SharePoint", "Web Search", "Deep Research").
- [ ] AUDIENCE (reviewer read-through): imagine a BA or PO with no repo access reading only the body. They can state back, in their own words, what will change, what will not, how they will know it worked, and which decisions are still open. If any of those four are unanswerable without opening the appendix, the body has failed the audience check.
```

### Big feature parent spec (decomposed)

```
- [ ] Frontmatter: all 6 fields + `status: draft (decomposed)`
- [ ] Purpose + Problem Statement cover the whole initiative in business language
- [ ] Engineering Appendix — Affected Areas covers the system-level impact (this is the only place file paths may appear)
- [ ] Cross-cutting Invariants + Risks listed (only those spanning sub-tasks), in business language
- [ ] Decomposition table present — every row has slug, purpose, type, depends-on, order, sub-spec status
- [ ] Step 4 decomposition self-check passes (DAG, full coverage, no overlap, no nested Big feature) — re-run it here; see `type-branches.md#self-check-for-decomposition`
- [ ] Parent spec has NO REQ-xxx, AC-xxx, or V-xxx (those belong in sub-specs)
- [ ] Every sub-spec referenced in the Decomposition either exists at its resolved path OR is tagged `pending` with a reason
- [ ] Open Questions captured; no silent assumptions
- [ ] AUDIENCE (mechanical): parent spec body (everything above `Engineering Appendix — Affected Areas`) contains zero file paths, zero code identifiers, zero SDK-specific terms — same greps as the standalone checklist
```

If any box fails, fix it before returning. For Big features, run the parent checklist AND the standalone sub-spec checklist once per produced sub-spec.

---

## Mini-Example (New feature)

**Request:** "Allow users to upload multiple office files at once in the document chat."

After Steps 1–5, the key parts of the spec look like:

```markdown
## Normative Contract
- REQ-001: The document upload endpoint MUST accept between 1 and 10 files per request.
- REQ-002: The system MUST reject requests where the combined file size exceeds 200MB.
- REQ-003: The system MUST process files in parallel and return a per-file success/failure status.
- REQ-004: The system MUST NOT regress single-file upload behavior.

## Invariants
- Previously uploaded files remain retrievable by their existing IDs.
- Per-file size limit (50MB) continues to apply to each individual file.

## Acceptance Criteria
- AC-001: WHEN a user uploads 5 valid files THEN all 5 are processed and appear in the chat context. (REQ-001, REQ-003)
- AC-002: WHEN a user uploads 11 files THEN the request is rejected with a clear error message. (REQ-001)
- AC-003: WHEN combined size > 200MB THEN the request is rejected before any file is processed. (REQ-002)
- AC-004: WHEN one file in a batch fails parsing THEN other files still succeed and the response reports which failed. (REQ-003)
- AC-005: WHEN a user uploads a single file THEN behavior matches the existing single-file flow. (REQ-004)

## Verification Matrix
| ID | Method | Target | Pass |
|---|---|---|---|
| V-001 | Integration test | 5-file upload | All 5 indexed, chat can reference them |
| V-002 | Unit test | Validator rejects 11-file payload | 400 response with error code `BATCH_LIMIT_EXCEEDED` |
| V-003 | Unit test | Aggregate size validator | Rejects at 200MB + 1 byte |
| V-004 | Integration test | Partial failure | Successful files processed, failed file reported |
| V-005 | Regression test | Single-file flow | Existing test suite passes unchanged |
```

Note how every `REQ` has at least one `AC` and one `V-xxx`, how Invariants protect the existing behavior, and how ACs cover both happy paths and failure modes.
