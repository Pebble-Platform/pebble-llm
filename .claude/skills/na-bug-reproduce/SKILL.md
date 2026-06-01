---
name: na-bug-reproduce
description: "[Bug] Step 1 of /na-investigate-bug — pin the bug, save raw logs verbatim into the bug folder, capture repro steps and identifiers. Produces bug-context.md plus the log files. Use first; it grounds every later analysis."
argument-hint: "<ticket-id or bug slug> [path/to/log/source]"
---

> **[IMPORTANT]** Use `TaskCreate` to break work into small tasks BEFORE starting — one task per workflow step (1–5), plus a final Self-Check task.

## Quick Summary

**Goal:** Produce a `bug-context.md` and a set of saved log files in `specs/features/<area>/bug-<slug>/`, so the RCA skill has unambiguous evidence to reason from.
**Workflow:** Pin the bug → Resolve output dir → Save logs verbatim → Reproduce (or document why not) → Inventory identifiers.
**Key rule:** Logs are saved unedited. `bug-context.md` quotes line ranges, never paraphrases.

---

## When to Use

- First step of `/na-investigate-bug`.
- Whenever a bug is reported and you need to pin it down before analyzing.

Skip for trivial bugs (typo, config flip) — open the PR directly.

---

## Input / Output

**Input** (via `$ARGUMENTS` or user message):
- Ticket id and/or bug slug
- Path or attachment to raw log source (server log, provider trace, dashboard export)

**Output** in `specs/features/<area>/bug-<slug>/`:
- `bug-context.md` — pins the bug and lists identifiers
- `log.txt` — raw server log, verbatim
- `claude-log.txt` (or named equivalent like `openai-log.txt`, `gemini-trace.json`) — provider-side trace, verbatim
- Optional: `screenshot.png`, `request.har`, etc. — any captured artifacts

The directory is created if it doesn't exist.

---

## Workflow

### 1. Pin the bug

Capture from the ticket / report:

| Field | Notes |
|---|---|
| Ticket | `NA-XXXX` + URL |
| One-line symptom | what is wrong, in user-visible terms |
| Affected surface | page / API / dashboard / agent path |
| Reporter | name + role + contact |
| Reported on | date (absolute, not "yesterday") |
| Environment | PROD / staging / dev |
| Severity | 1 Critical / 2 High / 3 Medium / 4 Low |

If any of these is missing, **ask the user via `AskUserQuestion`** before continuing. Do not invent values.

### 2. Resolve output directory

Compute the path: `specs/features/<area>/bug-<slug>/`

- `<area>` = affected module/feature (e.g. `chat`, `usage`, `auth`, `voice-mode`). Derive from the bug surface or the codebase structure.
- `<slug>` = short kebab-case description (e.g. `token-usage-spike`, `login-redirect-loop`, `dashboard-inflation`).

Confirm both with the user once via `AskUserQuestion` if either is ambiguous. The slug is sticky — every later doc in this bug folder uses it.

`mkdir -p` the directory.

### 3. Save logs verbatim

Copy every log source the user provides into the output dir, **unedited**:

- Server log → `log.txt`
- Provider trace → `claude-log.txt` / `openai-log.txt` / etc., named after the provider.
- Other artifacts → keep original names.

If logs are huge, you may slice to a ±30 min window around the incident, but:
- Use `Bash` (`head -n`, `sed -n 'X,Yp'`) with explicit line ranges.
- Record the slice range in `bug-context.md` ("server log lines 4 200–7 800 of original file `prod-2026-05-08.log`").
- Save the slice — never the edited original.

### 4. Reproduce (or document why not)

If reproducible:
- Record exact steps as a numbered list.
- Capture request id, conversation id, message id, user id, and timestamp for the reproduced incident.

If not reproducible:
- Write one sentence stating why (e.g. "PROD-only incident; staging lacks the data shape").
- Identify the captured artifact that stands in for a repro (e.g. "request id `req_011…` in `claude-log.txt:7-33`").

Either way, the RCA skill must be able to point at a specific incident.

### 5. Inventory identifiers

List every concrete identifier you'll cite in later docs. The RCA skill uses this as its lookup table.

| Kind | Value | Location |
|---|---|---|
| Request id | `req_011CanjPyHHTQAT7mnQ2fnVT` | `claude-log.txt:7-33` |
| Conversation id | `bd5c5157-79fa-4841-96ee-cfd79686976c` | `log.txt:194` |
| Message id | `526a836b-eb78-4681-acc4-47a086200038` | `log.txt:194` |
| User id | `d27568bd-…` | `log.txt:193` |
| Time window | `13:25:49 → 13:29:30` | `log.txt:110-194` |
| Suspect file | `lib/utils/cost-calculation.ts:33-56` | grep result |

### 5.5 Write `bug-context.md`

Use this exact shape:

```markdown
# Bug Context — {one-line symptom}

- **Ticket**: [NA-XXXX](...)
- **Severity**: {1–4}
- **Reported on**: {YYYY-MM-DD} ({environment}, {reporter})
- **Affected surface**: {page / API / agent path}
- **Output dir**: `specs/features/<area>/bug-<slug>/`

## 1. Symptom

One paragraph in user-visible terms.

## 2. Captured artifacts

- `log.txt` — server log, {range or "full capture"}.
- `claude-log.txt` — provider trace, {range or "full capture"}.
- {other artifacts}

If a slice was taken: name the original source and the slice range.

## 3. Reproduction

### Steps (if reproducible)

1. …
2. …

### Or — why not reproducible

One sentence + the artifact that stands in.

## 4. Identifiers

| Kind | Value | Location |
|---|---|---|
| Request id | … | `claude-log.txt:NN-MM` |
| Conversation id | … | `log.txt:NN` |
| Message id | … | `log.txt:NN` |
| User id | … | `log.txt:NN` |
| Time window | … | `log.txt:NN-MM` |
| Suspect file | `path/to/file.ts:NN-MM` | grep |

## 5. Open questions for RCA

Things the reproduction left unanswered. Each becomes a question the RCA skill must answer or explicitly defer.

- {open question}
```

### 6. Self-Check

Mechanical pass:

- [ ] Output dir is `specs/features/<area>/bug-<slug>/` and exists.
- [ ] Log files are saved verbatim (or slice range is recorded in §2).
- [ ] `bug-context.md` has every field populated — no `TBD` or `unknown` slots.
- [ ] Every row in the §4 Identifiers table has a real location citation (`log.txt:NN` or `file.ts:NN`). `Grep` confirms.
- [ ] If unreproducible, §3 names a specific captured artifact that stands in.
- [ ] Open questions in §5 are real questions, not "we should fix this" statements.

If any box fails, fix before handing off to `/na-bug-rca`.

---

## Key Rules

- **Verbatim logs.** No reformatting, no truncation outside an explicit slice window.
- **Identifiers must resolve.** Every id in §4 must be findable by `Grep` in the saved logs.
- **No analysis in this doc.** `bug-context.md` describes what happened and what was captured — it does not explain why. The RCA skill owns "why."
- **Sticky slug.** Once chosen in Step 2, `<slug>` is used by all sibling docs and by the fix-package skill.
