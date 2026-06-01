---
title: "{Question being answered}"
ticket: "NA-XXXX"
related: ["./other-rca-doc.md"]
status: draft
---

# {Question being answered as a statement}

- **Ticket**: [NA-XXXX](https://dev.azure.com/neurondAI/Neurond%20Assistant/_workitems/edit/XXXX)
- **Related**: links to sibling RCA docs (e.g. `[architecture.md](./architecture.md)`)
- **Source**: exact log/file lines this doc reasons from (e.g. `claude-log.txt:7-33`, `lib/foo.ts:120-148`)
- **Scope**: one sentence — what this doc covers and what it does NOT cover

---

## TL;DR

One paragraph. The answer to the question, in plain language, with the headline number(s) or condition(s).

---

## 1. {The framing the rest of the doc unpacks}

Set up the mental model. One short paragraph. If a table or trace makes it cleaner, use one — narrative is fine when the bug is text-shaped.

## 2. {Evidence section}

Ground every claim in a log line or file:line citation. Prefer:

- A small table with columns: `step | time | observed value | source line | interpretation`
- Or a step-by-step trace block:

```
step  time     observed         source              interpretation
─────────────────────────────────────────────────────────────────
 0   13:25    inputTokens=6919  claude-log.txt:7    initial system+user
 1   13:25    inputTokens=9725  claude-log.txt:8    continuation
...
```

Keep observation and interpretation in separate columns. When they diverge, surface it.

## 3. {Math / proof section, if applicable}

Show the arithmetic. Tables of running totals, ratios, or deltas. Cite the rate / formula source (e.g. provider pricing page, `cost-calculation.ts:33-56`).

## 4. {Counterfactual / why-not section}

Address the obvious wrong explanations. "It's not a runaway loop because…" "It's not an Anthropic billing bug because…" — each rebuttal cites evidence.

## 5. {Implications, if separable from the fix}

What this analysis means for the dashboard, the user, or adjacent systems. Keep narrow — the fix lives in the fix-package docs, not here.

---

## One-line summary

Restate the headline so sibling docs can cross-link to a single sentence.
