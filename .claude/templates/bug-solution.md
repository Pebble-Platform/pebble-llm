---
title: "SOLUTION — {one-line headline}"
ticket: "NA-XXXX"
status: "design only — no code in this doc"
related: ["./bug-<slug>.md", "./bug-<slug>-fix-steps.md"]
---

# SOLUTION — {one-line headline}

- **Ticket**: [NA-XXXX](https://dev.azure.com/neurondAI/Neurond%20Assistant/_workitems/edit/XXXX)
- **Bug doc**: [bug-&lt;slug&gt;.md](./bug-<slug>.md)
- **Fix-steps**: [bug-&lt;slug&gt;-fix-steps.md](./bug-<slug>-fix-steps.md)
- **Status**: design only — no code in this doc; implementation steps live in the fix-steps doc
- **Scope**: one sentence — what changes and what is deliberately untouched

> **Rule**: this doc contains **no code blocks longer than one pseudo-line**. If you need to show code, put it in the fix-steps doc.

---

## 1. Goal

What "fixed" looks like, in user/system terms. One paragraph. Don't restate the bug — state the post-fix state.

## 2. Guiding principle

The invariant from `bug-<slug>.md §2`, restated as a design principle the solution will enforce end-to-end.

Example:
> **Stored metrics must be pairwise disjoint additive subsets of the API-reported usage.**

## 3. Solution overview

A table — one row per coordinated change. Mark optional follow-ups with O1 / O2 etc., gated separately.

| # | Layer | Change | Why |
|---|-------|--------|-----|
| **S1** | {write path / read path / data} | {what changes conceptually} | {which root cause this addresses} |
| **S2** | … | … | … |
| **S3** | … | … | … |
| **O1** (optional) | {layer} | {follow-up, not gating} | {why it can ship later} |

Identify the **keystone** change — the one that, once in, makes the rest simpler. Mark it.

## 4. Why this approach over alternatives

Compare at least one rejected alternative. Name its drawback. The reader should walk away knowing why we did NOT do the obvious-looking thing.

| Approach | What changes | Drawback |
|----------|--------------|----------|
| {Rejected option} | … | {why we said no} |
| **{Chosen option}** | … | {trade-off we accept} |

## 5. Solution detail — narrative form

One subsection per row in §3.

### 5.1 S1 — {short name}

Describe what changes conceptually. File names are allowed; code is not. Cover:

- What the function/layer currently does (1–2 sentences).
- What it does after the fix (1–2 sentences).
- Why the change preserves correctness for the cases that were already right.

### 5.2 S2 — {short name}

…

### 5.N O1 — {follow-up}, optional

…

## 6. Risk analysis

| Risk | Likelihood | Mitigation |
|------|-----------:|------------|
| {Stakeholders see numbers drop and call it a regression} | High | {comms plan / changelog line} |
| {Existing fixtures encode the old behavior} | Certain | {update fixtures in fix-steps Phase N} |
| … | … | … |

Mark anything **High likelihood × High impact** as needing pre-rollout sign-off.

## 7. Verification approach

How we'll prove the fix worked. Map 1:1 to `bug-<slug>.md §7`. Levels:

1. **Unit**: feed known payload through the changed function; assert invariant.
2. **Integration**: replay a captured incident; assert end-to-end output matches reality within tolerance.
3. **Dashboard / UX smoke**: load the affected page; confirm numbers match the new ground truth.
4. **Regression**: confirm non-affected providers / paths produce identical output to pre-fix.

## 8. Non-goals

What this fix deliberately does NOT do. Out-of-scope items from `bug-<slug>.md §6` are repeated here so the reviewer sees them in the design context.

## 9. Acceptance criteria

Mirror `bug-<slug>.md §7`. The list MUST be identical (modulo phrasing) — the fix-steps "Definition of Done" then references this list.

1. …
2. …
3. …
