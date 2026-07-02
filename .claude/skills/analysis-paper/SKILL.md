---
name: analysis-paper
description: "[Research] Score how much a paper overlaps with the Pebble project (a reproducible 0–100% rubric across 7 dimensions), then pick the single most useful, transferable point for the project. Use after a paper is identified (by research-paper or named by the user). Triggers on: 'how relevant is this paper', 'analyze this paper', 'percent overlap', 'what can we use from this paper', 'is this paper useful'."
argument-hint: "<paper title / arXiv id / URL>"
---

## Quick Summary

**Goal:** Produce (a) a **reproducible overlap %** between a paper and Pebble, and (b) **one** concrete, highest-value point Pebble can use from it.
**Workflow:** Read the paper → score 7 dimensions → compute % → pick the single best transferable point → write the analysis block.
**Key rule:** Write the per-dimension scores *before* computing the percentage. Never skip to a number. The "good point" must be **one** thing, actionable, with a how-to-apply line.

---

## When to Use

- After `research-paper` surfaces a candidate, or the user names a specific paper.
- To decide whether a paper is worth a deep read, a baseline run, or a citation.

---

## Pebble profile (what we score against)

**Do not hardcode the profile — assemble it at analysis time from the repo's IDD
layers** (intent = why/scope, capabilities = current truth). A snapshot written
into this file goes stale (a pre-2026-07-02 version described Pebble as
text-only and systematically under-scored speech papers).

1. `docs/intent/constraints.md` — the research question, scope in/out, hard
   constraints (gold-holdout, ethics). This bounds what "useful to Pebble" means.
2. `docs/spec/capabilities/` — current truth per stream. Read the ones matching
   the paper's modality/topic; at minimum:
   - text / ordinal risk → `ordinal-modeling.md`, `data-and-labeling.md`, `label-quality.md`
   - voice / multimodal → `voice-multimodal.md` (its authoritative detail lives in the task docs it names, e.g. `docs/tasks/voice-mtl-heads.md`)
3. **State the assembled profile in 2–4 lines at the top of your output**, before
   scoring — the score must be auditable against the profile actually used.

> Orientation only (verify against the docs above, never score from this line):
> the repo currently has a primary ordinal suicide-risk **text** program
> (NeoBERT-class encoder, teacher-LLM silver labels, gold-holdout eval) and an
> adjacent active **voice** stream (emotion2vec/WavLM backbone; MTL heads:
> emotion + affect-CCC + crisis recall-floor), with voice+text fusion as the
> forward direction.

**Comparability note:** analysis blocks written before 2026-07-02 were scored
against the stale text-only profile — re-score before comparing their % with
newer ones.

## Step 1 — Read the paper
Use `WebFetch` on the abstract/PDF (arXiv, ACL Anthology, DOI). If paywalled, use the abstract + any open preprint/sibling and **mark unread sections explicitly** — never guess scores for what you can't see.

## Step 2 — Score the 7 dimensions

Score each dimension **0 / 1 / 2** (0 = absent, 1 = partial, 2 = strong/direct match):

| # | Dimension | Weight |
|---|-----------|--------|
| D1 | Multi-task **heterogeneous heads** (categorical + continuous; +safety = strong) | 3 |
| D2 | **Mental-health / crisis** domain | 2 |
| D3 | **Emotion-transfer corpora** (GoEmotions / EmpatheticDialogues / intensity) | 1 |
| D4 | **Teacher-LLM silver-label distillation** | 2 |
| D5 | **Principled MTL loss balancing** (uncertainty / GradNorm / PCGrad / Nash-MTL) | 2 |
| D6 | **Safety/crisis recall constraint** as an objective | 2 |
| D7 | **Encoder backbone** match with an active Pebble stream (text: BERT-family ~250M; voice: emotion2vec/WavLM-class SSL) | 1 |

Write the scores out loud before computing:

> D1=2, D2=2, D3=1, D4=0, D5=1, D6=0, D7=2

## Step 3 — Compute overlap %

```
overlap% = ( Σ weightᵢ × scoreᵢ ) / ( Σ weightᵢ × 2 ) × 100
         = ( Σ weightᵢ × scoreᵢ ) / 26 × 100
```

(Σ of weights = 13; max per dimension = 2 → denominator 26.) Round to the nearest whole percent. Add a one-line band: **≥70% core** · **40–69% adjacent** · **<40% peripheral**.

## Step 4 — Pick the single best point

Choose **one** highest-value transferable element. Tag it as exactly one of:

- **Method to adopt** (a technique Pebble should use)
- **Baseline to beat** (a published number/setup Pebble must compare against)
- **Dataset to reuse** (hand off to `find-dataset`)
- **Design lesson** (a pitfall/decision the paper settles — e.g., ordinal loss for C-SSRS)
- **Framing / citation** (positions Pebble's contribution)

Give it one **"How to apply to Pebble:"** line. Resist listing several — pick the one with the highest leverage for Pebble's current stage.

## Step 5 — Write the analysis block

```markdown
### Analysis — <paper short title>
- **Overlap:** <N>% (<band>) — D1=…, D2=…, D3=…, D4=…, D5=…, D6=…, D7=…
- **Closest on:** <the 1–2 strongest dimensions>
- **Best point (<tag>):** <one sentence>.
  - **How to apply to Pebble:** <one line>.
- **Caveats:** <paywalled sections / unverified claims, if any>
```

---

## Key Rules

- **Scores before the number.** The per-dimension line must appear before the %. The formula is fixed — same paper → same score.
- **One point, not a list.** The deliverable is the single most useful takeaway, with a concrete apply-line.
- **Don't score the unseen.** Paywalled section → mark it, don't fabricate a score; note it lowers confidence.
- **Stay grounded in the profile you assembled from intent + capabilities.** Overlap is with *this* project, not generic relevance.
