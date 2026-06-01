---
name: na-bug-rca
description: "[Bug] Step 2 of /na-investigate-bug — analyze the captured logs and code to find root cause(s). Produces 1+ evidence-based RCA docs in specs/features/<area>/bug-<slug>/, each answering one named question. Uses template .claude/templates/bug-rca-analysis.md."
argument-hint: "<path to bug folder, e.g. specs/features/chat/bug-token-usage-spike>"
---

> **[IMPORTANT]** Use `TaskCreate` to break work into small tasks BEFORE starting — one task per workflow step (1–5), plus a final Self-Check task.

## Quick Summary

**Goal:** Turn the raw logs + `bug-context.md` (produced by `/na-bug-reproduce`) into a small set of focused RCA docs that prove the root cause(s) from evidence.
**Workflow:** Read context → Map suspect code paths → Decompose into questions → Produce one RCA doc per question (from template) → Cross-link & label compounding causes.
**Key rule:** Every numeric claim cites a log line. Every code claim cites `file.ts:NN`. Observation and interpretation live in separate columns.

---

## When to Use

- After `/na-bug-reproduce` has populated the bug folder with logs and `bug-context.md`.
- When `bug-context.md §5` has at least one open question the RCA must answer.

Skip if root cause is trivially obvious from the logs (e.g. literal stack trace points to a one-line fix) — go straight to `/na-bug-fix-package`.

---

## Input / Output

**Input** (via `$ARGUMENTS` or user message):
- Path to the bug folder (e.g. `specs/features/chat/bug-token-usage-spike/`)

The folder must already contain:
- `bug-context.md`
- At least one log file (`log.txt`, `claude-log.txt`, etc.)

**Output** in the same folder:
- One or more RCA docs, named after the question each answers.

Naming pattern: **`<question-slug>.md`**. Names describe the question, not the analysis number.

Examples that work:
- `why-4m-tokens.md` — Why did one user message burn 4M tokens?
- `tool-loop-trace.md` — Why did this trigger 19 API calls?
- `prefix-recount.md` — What is the "re-counted prefix" concretely?
- `req-<id>-estimate.md` — What did this specific request actually cost?
- `dashboard-inflation-math.md` — Where does the displayed 8.36M come from?

Names that don't work: `analysis-1.md`, `rca.md`, `investigation.md`.

**How many docs:** as many as the bug needs.
- Single-cause bug → 1 RCA doc is fine.
- Two compounding causes → 2 docs, each one named after its question.
- Sample-style multi-cause incident with infrastructure + data + display layers → 3–4 docs.

Don't pad. Don't merge unrelated questions into one doc.

---

## Workflow

### 1. Read context

Read `bug-context.md` end-to-end. Note:
- The §4 Identifiers table → these become the citations you'll use.
- The §5 Open Questions → these seed the questions you'll answer.
- The §3 Reproduction → tells you which incident is the audit-of-record.

### 2. Map suspect code paths

Use `Grep` / `Glob` / `Read` to walk from the captured identifiers into the codebase:

- For each suspect file referenced in §4, read the function(s) at the cited line range.
- For each log entry that names a source (`INFO ai/agent/foo`, `lib/db/queries/admin/xyz`), `Grep` for the emitter and identify the call site.
- If `gitnexus_query` / `gitnexus_context` / `gitnexus_impact` are available, use them to find callers / callees / blast radius. Otherwise `Grep` for the function name.

Build a small private map: `{observed log signal → source file:line → upstream caller}`. You won't write this map down; it's scaffolding for the questions in Step 3.

### 3. Decompose into questions

List every question that, if answered with evidence, would make the root cause(s) unfalsifiable. Each question becomes one RCA doc.

Good questions are:
- **Specific** — "Why does Σ-of-per-step `input_tokens` not equal conversation size?" not "What's wrong with token counting?"
- **Answerable from the captured evidence** — if the logs can't answer it, either capture more logs (back to `/na-bug-reproduce`) or mark the question as "needs more data" and defer.
- **Atomic** — one phenomenon per question. If a question has an "and" in it, split it.

If multiple causes compound (e.g. write-path double-counts AND read-path also re-sums), label them **F1 / F2 / F3** and write a separate doc for each. A final "how F1+F2 compound" subsection lives in the bug-problem doc, not here.

### 4. Produce RCA docs from the template

For each question, copy `.claude/templates/bug-rca-analysis.md` and fill it in:

- **Title** = the question stated as the headline answer ("Why a 'simple prompt' burns 4M tokens").
- **TL;DR** = one paragraph answer with the headline number.
- **Evidence sections** = tables / traces grounded in `log.txt:NN`, `claude-log.txt:NN`, or `file.ts:NN`.
- **Math section** (if numeric) = step-by-step arithmetic with cited rates.
- **Counterfactual section** = rebut the obvious wrong explanations.
- **One-line summary** = restate the answer so sibling docs can cross-link.

Evidence rules (non-negotiable):

- Every numeric claim has a source line. "4.6M tokens" must trace to rows in `claude-log.txt`.
- Every code claim has a `file.ts:NN` reference. `Grep` confirms the symbol exists at that location.
- Distinguish *observation* (from logs) from *interpretation* (your conclusion). Use separate columns in tables.
- Cite the math: if you apply a rate, link to the source (provider pricing page, `cost-calculation.ts:NN`).

### 5. Cross-link and label

After all RCA docs are written:

1. Add a `**Related**:` line at the top of each doc linking the sibling RCAs.
2. If multi-cause: confirm the F1 / F2 / F3 labels match across docs. Inconsistent labels are a frequent self-check failure.
3. Update `bug-context.md §5` Open Questions — mark each as **resolved (see `xyz.md`)** or **deferred (needs more data)**. Don't silently drop questions.

### 6. Self-Check

Mechanical pass — read each produced doc, do NOT tick from memory:

- [ ] Every RCA doc has the template's frontmatter, citations bar, TL;DR, evidence section(s), and one-line summary.
- [ ] Every numeric claim in TL;DR and headline tables has a `log.txt:NN` / `claude-log.txt:NN` citation.
- [ ] Every `file.ts:NN` citation resolves — run `Grep` for one symbol per doc to confirm the location.
- [ ] Tables separate observation from interpretation.
- [ ] If multi-cause, the same labels (F1 / F2 / F3) are used across sibling docs.
- [ ] Every open question in `bug-context.md §5` is either resolved by an RCA doc (citation included) or explicitly deferred.
- [ ] No doc named `analysis-1.md` or similar — every filename describes the question it answers.

If any box fails, fix before handing off to `/na-bug-fix-package`.

---

## Key Rules

- **One question, one doc.** Splitting is free; merging is expensive (the reader loses the train of evidence).
- **Observation vs interpretation.** Keep them in separate columns. When they diverge, surface the gap.
- **No imagined references.** If you cite `file.ts:NN`, `Grep` confirms it. If a line drifts during edits, update the citation, not the doc body.
- **Compounding causes get separate labels.** F1 / F2 / F3 with one doc each. The interaction summary belongs in the bug-problem doc, not the RCA docs.
- **No fix design here.** The RCA docs explain *why* the bug exists. The solution / fix-steps docs (next skill) explain *how* to fix it. Resist the urge to start solutioning.
