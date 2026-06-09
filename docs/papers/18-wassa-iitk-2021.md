# Paper 18 — WASSA@IITK at WASSA 2021: Multi-task Emotion + Empathy/Distress

> Enrichment set · Pillar 5 (intensity/empathy regression). Analysis depth: abstract + fetch. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** WASSA@IITK, WASSA 2021 (EACL workshop).
- **Link:** [arXiv:2104.09827](https://arxiv.org/abs/2104.09827) · open
- **Pebble pillar:** the closest published **regression + classification** multi-task design.

## Summary
An ELECTRA encoder trained multi-task: a categorical emotion-classification head + a continuous empathy/distress **regression** head on a shared encoder, for the WASSA 2021 empathy/distress essay shared task.

## Overlap with Pebble — 42% (ADJACENT) — highest in the enrichment set
`D1=2, D2=1, D3=1, D4=0, D5=0, D6=0, D7=2` → (3·2 + 2·1 + 1·1 + 1·2)/26 = 11/26 = **42%**
- **Closest on:** D1 (categorical emotion + continuous regression jointly on one encoder — Pebble's exact softmax+sigmoid-regression pattern) and D7 (ELECTRA, same family/scale as NeoBERT).

## Best point — Baseline to beat
Concrete ranked shared-task numbers: empathy/distress **Pearson r ≈ 0.533** (3rd), emotion **macro-F1 ≈ 0.5528** (1st), on Pebble's planned WASSA transfer source.
- **How to apply to Pebble:** When warm-starting/evaluating Pebble's continuous-score + emotion heads on WASSA empathy/distress (now downloaded — see paper 23 / `data/external/wassa_empathy/`), report against r≈0.53 and macro-F1≈0.55 to show what teacher-LLM distillation + principled balancing add over naive MTL.

## Dataset
WASSA 2021 empathy/distress essays — the Buechel et al. 2018 base is acquired (CC-BY, deployable) at `data/external/wassa_empathy/`.

## Caveats
Abstract + fetch only; exact ELECTRA variant (base vs large), param count, and loss-balancing scheme unread → D5/D7 lower confidence. D5=0 (no principled balancing mentioned); if the full paper documents a non-trivial weighting scheme, D5→1 (→50%).
