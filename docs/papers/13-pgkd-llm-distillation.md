# Paper 13 — PGKD: Performance-Guided LLM Knowledge Distillation for Text Classification

> Enrichment set · Pillar 3 (LLM-teacher distillation). Analysis depth: abstract + arXiv HTML. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** EMNLP 2024 (Industry).
- **Link:** [arXiv:2411.05045](https://arxiv.org/abs/2411.05045) · [ACL Anthology](https://aclanthology.org/2024.emnlp-main.215/) · open
  - *(Corrected: the enrichment doc's ResearchGate link 386201474 returns 403; this is the real id.)*
- **Pebble pillar:** teacher-LLM silver-label distillation into a small student.

## Summary
A **Claude-3** teacher generates synthetic training data into a **BERT-base student** via a performance-guided active-learning loop: the student's per-class validation metrics + hard negatives (high-confidence misclassifications) are fed back to the teacher, which generates the next batch of targeted silver examples — rather than one static silver set.

## Overlap with Pebble — 19% (peripheral)
`D1=0, D2=0, D3=0, D4=2, D5=0, D6=0, D7=1` → (2·2 + 1·1)/26 = 5/26 = **19%**
- **Closest on:** D4 (teacher-LLM silver-label distillation into a small student) and partial D7 (BERT-base student, same family as NeoBERT but ~110M).

## Best point — Method to adopt
The **iterative, error-targeted** distillation loop — generate new silver data for exactly the student's current failure regions.
- **How to apply to Pebble:** Make Gemini silver-label generation iterative: after each training round, surface the safety head's false-negatives and worst per-bin severity/emotion errors back to Gemini and ask for new examples in those regions. Directly serves the recall ≥ 0.95 floor by concentrating new silver on missed crisis cases.

## Dataset
Method paper — datasets are general-domain (news/reviews/Q&A), not relevant to acquire.

## Caveats
ResearchGate URL 403'd; scored from open arXiv HTML + EMNLP abstract (full method/results visible). Single-task multi-class, general domain, no continuous heads / MTL / safety — those dimensions are genuine zeros. The 130×/25× efficiency claims are inference-cost, not relevant to Pebble's training-side use.
