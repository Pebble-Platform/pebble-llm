---
name: read-paper
description: "[Research] Read one scientific paper efficiently with the three-pass method: Pass 1 (5-min triage → worth reading?), Pass 2 (evidence check → do the experiments support the claims?), Pass 3 (only if we'll build on it). Each pass has an explicit stop-gate; the deliverable is a verdict + a 3–5 line note. Use when the user names a paper and wants it read/understood (not scored — that's analysis-paper). Triggers on: 'read this paper', 'đọc bài này', 'summarize this paper', 'is this paper any good', 'what does this paper actually show'."
argument-hint: "<paper title / arXiv id / URL>"
---

## Quick Summary

**Goal:** Understand a paper in the minimum time that supports a correct verdict — and **stop as early as the verdict allows**.
**Workflow:** Pass 1 (triage, ~5 min) → stop-gate → Pass 2 (evidence check, the core pass) → stop-gate → Pass 3 (mental re-implementation, rare).
**Deliverable:** a markdown note file at `docs/papers/reads/<slug>.md` (verdict + evidence block), plus a 1–2 line verdict in chat.
**Key rule:** Never read linearly page 1 → end. Every pass answers one named question; the note is a **verdict + evidence block**, not a section-by-section retelling.

Boundaries with sibling skills:
- Want a reproducible **overlap % with Pebble** → `analysis-paper` (this skill's Pass-2 findings feed it).
- Want the **gold-standard full-PDF deep read** written into `docs/papers/` → the `deep-read-paper` agent (≈ Pass 3 done properly).
- Want to **find** papers → `research-paper`.

---

## Read with a question

Before Pass 1, state in one line **why we are reading this** (e.g. "does it threaten our novelty claim?", "is its dataset usable?", "is the method worth adopting?"). If the user gave no reason, default to: *"what, if anything, does this change for Pebble?"* Purposeful reading is what makes the stop-gates work.

## Pass 1 — Triage (~5 minutes): "Is it worth reading further?"

Read ONLY: title + abstract → intro → section headings → **conclusion** → skim references (which ones do we already know?).

Fetch via `WebFetch` (arXiv `/abs/` then `/html/` or `/pdf/`; ACL Anthology; DOI). If paywalled, use the abstract + any open preprint and **mark what you couldn't see**.

After Pass 1 you must be able to state:
1. **Category** — method / dataset / survey / position / replication.
2. **Contribution** — the one-sentence claim the authors would defend.
3. **Relevance** — does it touch the reading question?

**Stop-gate 1:** If relevance is low, STOP. Output the verdict ("not worth Pass 2 because …") + the 3-line note. Most papers should die here.

## Pass 2 — Evidence check (~1 hour): "Does the evidence carry the claim?"

Skip proofs and related work. Go straight to **figures, tables, and the experimental-setup section**. Work through this checklist (calibrated for ML/SER papers — the repo's home turf):

| # | Question | What to look for |
|---|----------|------------------|
| Q1 | **Claim–evidence gap** | Does the title/abstract promise more than what was measured? (e.g. "diagnosis" claimed, emotion classification measured) |
| Q2 | **Dataset reality** | N samples, N speakers, total duration, who labeled it, inter-annotator agreement, license |
| Q3 | **Split hygiene** | Speaker-independent or random split? Any train/test leakage path (same speaker, same episode, same session)? This is where inflated numbers hide |
| Q4 | **Baseline fairness** | Compared against what? Same data/split/features? Tuned equally? |
| Q5 | **Numbers** | Copy the headline metrics exactly (UA/WA/F1/CCC …), with the split they were measured on |
| Q6 | **Limitations** | Stated honestly, or absent (a red flag by itself)? |

Rules within Pass 2:
- **Quote exact numbers** — never paraphrase a metric.
- **Distinguish "the paper doesn't say" from "no".** Unstated speaker-independence is a finding, not a gap to fill charitably.
- If a table contradicts the abstract, the table wins.

**Stop-gate 2:** Pass 3 only if we will **implement, extend, or formally review** the paper. "Interesting" is not a reason.

## Pass 3 — Mental re-implementation (hours): "Could I have written this?"

Re-derive the method from the problem statement as if you were the author; compare your design against theirs at every choice point. Differences are either your misunderstanding (fix it) or the paper's hidden assumptions (record them). For Pebble papers, prefer delegating this pass to the `deep-read-paper` agent so the result lands in `docs/papers/` permanently.

## Output — write the note file

**Before writing, check for an existing entry:** `Grep` the paper's title / arXiv id under `docs/papers/**`. If the paper already has a numbered stream entry (`docs/papers/<stream>/NN-*.md`), that entry is the authoritative deep read — still write the read note, but link the entry in a `**Stream entry:**` line and don't duplicate its content.

Write the note to **`docs/papers/reads/<slug>.md`** (create the folder on first use; slug = short kebab-case of the paper, e.g. `vnemos-dynamic-cbam.md`), in the user's language:

```markdown
# Read — <paper full title>

- **Source:** <venue year> · <arXiv/DOI link> · <code link if any>
- **Read:** <YYYY-MM-DD>, stopped after Pass <N>
- **Reading question:** <the one-line "why we read this">

## Verdict
<stopped after Pass N> — <one sentence why>

## Notes
- **Claim:** <what the authors say>
- **Evidence:** <what was actually measured — exact numbers, split, dataset size>
- **Gap / red flags:** <claim–evidence gap, leakage risk, missing license … or "none found">
- **For Pebble:** <one line: citation / baseline / cautionary example / dataset lead / nothing>
- **Stream entry:** <link to docs/papers/<stream>/NN-*.md, or "none">
```

Papers that die at stop-gate 1 get the same file — a 5-line "not worth Pass 2" note prevents re-triaging the same paper next month.

End the chat turn with the file path + the Verdict line only; the file is the artifact.

---

## Key Rules

- **Stop-gates are the point.** Reading every paper to Pass 2 is the failure mode this skill exists to prevent.
- **Never read what you can't cite.** Paywalled/missing sections get marked, never guessed.
- **Q1 and Q3 first.** Claim–evidence gap and split hygiene kill more papers than any other check.
- **Verdict before detail.** The output block leads with the verdict; supporting detail follows.
- **Hand off, don't duplicate.** Overlap scoring → `analysis-paper`; dataset acquisition → `find-dataset`; permanent deep read → `deep-read-paper`.
