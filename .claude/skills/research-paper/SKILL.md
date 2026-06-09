---
name: research-paper
description: "[Research] Find papers related to a topic and rank them by closeness to the Pebble project. Searches the web from multiple angles, dedupes, verifies venue/links, and emits structured related-work entries. Use when you need to discover prior art or enrich the related-work set. Triggers on: 'find related papers', 'research papers about', 'find prior art', 'literature search', 'enrich related work'."
argument-hint: "<topic / method / question to search for> [how many papers]"
---

## Quick Summary

**Goal:** Return a ranked, deduplicated set of *real* papers related to a topic, each as a structured entry that drops straight into `docs/related-work-*.md`.
**Workflow:** Scope → search from ≥3 angles → dedupe → verify → rank by closeness → emit entries.
**Key rule:** Every paper must have a resolvable link and a real venue. Never invent a title, author, or result. Flag anything you could not verify.

---

## When to Use

- Discovering prior art for a method, dataset, or research question.
- Enriching the existing related-work set (`docs/related-work-survey.md`, `docs/related-work-enrichment.md`).
- Skip if the user already named the exact papers — go straight to `analysis-paper`.

---

## Input / Output

**Input:** a topic / method / question (via `$ARGUMENTS` or user message); optional target count (default 5–8).

**Output:** a markdown block of ranked entries. Append to the relevant `docs/related-work-*.md` only if asked; otherwise return inline. Each entry:

```markdown
### <short title> — <one-line what-it-is>
- **Authors / Year / Venue:** …
- **Link:** [<resolvable URL>](…)  ·  **Access:** open | paywalled | preprint-only
- **Summary:** 1–2 sentences.
- **Closeness to Pebble:** which of the dimensions below it hits (and how strongly).
- **Why it matters here:** one line — baseline to beat / backbone to try / method to adopt / dataset / framing.
```

---

## Workflow

### 1. Scope the search
Restate the topic in one line. Identify which **Pebble closeness dimensions** the user cares about (default: all). These are the project's ranking axes (source of truth: `docs/related-work-survey.md`):

1. Multi-task encoder with **categorical + continuous** affect heads (ideally + safety head)
2. **Mental-health / crisis** text classification with transformer encoders
3. Transfer from **GoEmotions / EmpatheticDialogues / intensity corpora**
4. **Silver-label distillation from a teacher LLM** into a smaller student
5. **Principled multi-task loss balancing** (uncertainty weighting, GradNorm, PCGrad, Nash-MTL)
6. **Safety/crisis recall constraint** as a training-time objective
7. **Encoder backbone** match (BERT/RoBERTa/NeoBERT/ModernBERT, ~250M)

### 2. Search from ≥3 angles
Run separate `WebSearch` queries: by **method**, by **task/domain**, and by **dataset/benchmark**. Prefer arXiv, ACL Anthology, ScienceDirect, Nature, ACM DL, PMC, Zenodo, Papers-with-Code. Use the current year for "recent" framing.

### 3. Dedupe and verify
Merge duplicates (same paper, different host). For each survivor, confirm the **venue and a resolvable link** (`WebFetch` the abstract page if unsure). Mark `paywalled` / `preprint-only` honestly — do **not** fabricate results behind a paywall; write "numbers not retrievable" instead.

### 4. Rank by closeness
Order by how many closeness dimensions each hits and how strongly. Note the strongest 1–2 dimensions per paper. (For a precise score, hand the paper to the `analysis-paper` skill.)

### 5. Emit entries + a one-line synthesis
Output the ranked entries, then a single line naming the most useful 1–3 and why.

---

## Key Rules

- **No hallucinated papers.** Title, authors, venue, and link must be verifiable. If a result is uncertain, say so.
- **Real links only.** Prefer the canonical source (arXiv abstract, ACL Anthology, DOI). No guessed URLs.
- **Honest access labels.** Paywalled → don't invent the numbers; flag what's unretrievable.
- **Closeness, not just topicality.** Rank by the 7 dimensions above, not surface keyword match.
- **Don't analyze deeply here.** Percentage overlap + the single best takeaway belong to `analysis-paper`. This skill is discovery + ranking only.
