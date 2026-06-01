---
title: "BUG — {one-line headline}"
ticket: "NA-XXXX"
severity: "1 | 2 | 3 | 4"
reported_on: "YYYY-MM-DD"
environment: "PROD | staging | dev"
reporter: "user@domain"
affected_surface: "page / API / agent path"
status: "open"
related: ["./bug-<slug>-solution.md", "./bug-<slug>-fix-steps.md"]
---

# BUG — {one-line headline}

- **Ticket**: [NA-XXXX](https://dev.azure.com/neurondAI/Neurond%20Assistant/_workitems/edit/XXXX)
- **Severity**: {1 Critical | 2 High | 3 Medium | 4 Low}
- **Reported on**: {YYYY-MM-DD} ({environment}, {reporter})
- **Affected surface**: {page / API / dashboard / agent path}
- **Related docs**: links to Step-2 RCA docs and to the solution + fix-steps siblings
- **Scope of this bug**: one sentence — what this ticket fixes and what is explicitly out of scope

---

## 1. Summary

2–3 sentences. The user-visible symptom and its impact. The number that matters (e.g. "dashboard shows 1.8× the real token count and 4× the real cost"). No root cause yet — that's §3.

## 2. The relevant invariant

The rule the system should obey, stated as a single sentence the reader can hold in their head. Often the cleanest naming of the bug is "invariant X is violated."

Example:
> `cache_read_input_tokens ⊆ input_tokens` — overlapping, not disjoint. The cached count is a discount-eligible subset of the total input, not an additional bucket.

## 3. Root cause(s)

One subsection per cause. If multiple causes compound, label them **F1 / F2 / F3** and explain how they interact in a final sub-paragraph.

### 3.1 F1 — {short name of the cause}

- **Where**: `path/to/file.ts:NN-MM` ({function name})
- **What**: one paragraph describing the misbehavior at that location.
- **Minimal reproducer / proof**: code excerpt or SQL that demonstrates it.
- **Effect**: the quantitative impact (e.g. "inflates `tokenCount` by 1.7×–1.9× at typical cache hit rates").

### 3.2 F2 — {second cause, if any}

…

### 3.3 How F1 and F2 compound (if multi-cause)

One paragraph naming the interaction. Tables welcome.

## 4. Reproduction

### 4.1 Black-box (no DB / log access)

Steps a tester can run in the UI. Numbered. Each step ends in an "Expect: …" line.

### 4.2 With DB / log access (deterministic)

SQL or log query that produces the broken number. Include the broken-vs-correct comparison so the reviewer can see the inflation factor in one query.

### 4.3 Concrete numbers from the captured incident

Quote the actual numbers from the RCA docs. Show: stored / displayed value, real provider-reported value, ratio.

## 5. Impact

- **Customer trust**: …
- **Internal forecasting / capacity planning**: …
- **Cost attribution**: …
- **Alarms / monitoring**: …

One bullet per affected surface. Skip surfaces that aren't affected — don't pad.

## 6. Out of scope (separate bugs)

Adjacent issues surfaced during investigation. Each gets a one-line description and (if filed) a ticket link. **Do not bundle these into this fix.**

## 7. Acceptance criteria

Numbered, testable statements the PR must satisfy. The solution and fix-steps docs mirror this list.

1. {Criterion 1 — what must be true after the fix}
2. {Criterion 2}
3. …
