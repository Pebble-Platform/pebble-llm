# Paper 21 — Recall and Learn: Fine-tuning with Less Forgetting (RecAdam)

> Enrichment set · Pillar 6 (staged fine-tuning). Analysis depth: abstract + method summary. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Chen, Hou, Gao, Jiang, et al. EMNLP 2020.
- **Link:** [arXiv:2004.12651](https://arxiv.org/pdf/2004.12651) · open
- **Pebble pillar:** catastrophic-forgetting mitigation during the unfreeze stage.

## Summary
A fine-tuning optimizer that mitigates catastrophic forgetting via (1) a quadratic L2 penalty anchoring weights to the pretrained init ("Pretraining Simulation," EWC-style, no original data needed) plus (2) an annealing coefficient that ramps the downstream loss in gradually ("Objective Shifting"). On GLUE, BERT-base matched fine-tuned BERT-large.

## Overlap with Pebble — 15% (peripheral)
`D1=0, D2=0, D3=0, D4=0, D5=1, D6=0, D7=2` → (2·1 + 1·2)/26 = 4/26 = **15%**
- **Closest on:** D7 (BERT encoder fine-tuning, same as NeoBERT) and partial D5 (principled annealed weighting between a "recall" objective and the downstream objective, framed as MTL).

## Best point — Method to adopt
Pretraining-anchor penalty + objective annealing → fine-tune with substantially less forgetting.
- **How to apply to Pebble:** Swap AdamW for RecAdam during the unfreeze stage so NeoBERT retains its pretrained/GoEmotions-warm-started representations while adapting to the ~5K Gemini silver labels — a principled, drop-in alternative/complement to the hand-tuned freeze→unfreeze ramp; addresses low-resource overfitting/forgetting.

## Dataset
Method paper — no dataset to acquire (GLUE).

## Caveats
Abstract/method-summary only; exact penalty formula, annealing schedule, and per-task GLUE numbers not retrievable → D5 scored on the mechanism, not verified equations. Single-task in the original work and head/balancing-agnostic — it does **not** address Pebble's core heterogeneous-head balancing problem; a complementary optimizer, not a substitute for Kendall/GradNorm.
