# Paper 12 — MentalBERT: Publicly Available Pretrained Language Models for Mental Healthcare

> Enrichment set · Pillar 2 (mental-health encoders). Analysis depth: abstract + PDF excerpt. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Ji, Zhang, Ansari, Fu, Tiwari, Cambria. LREC 2022.
- **Link:** [arXiv:2110.15621](https://arxiv.org/abs/2110.15621) · open · weights on HF (`mental/mental-bert-base-uncased`, `mental/mental-roberta-base`, `AIMH/mental-roberta-large`)
- **Pebble pillar:** domain-adaptive mental-health encoder backbone / baseline.

## Summary
BERT/RoBERTa-base (~110M) domain-adaptively MLM-pretrained on mental-health Reddit, evaluated on single-task depression, stress, and suicidal-ideation detection. Domain pretraining beats general-domain BERT on these tasks.

## Overlap with Pebble — 27% (peripheral)
`D1=0, D2=2, D3=0, D4=0, D5=0, D6=1, D7=1` → (2·2 + 2·1 + 1·1)/26 = 7/26 = **27%**
- **Closest on:** D2 (mental-health/crisis text incl. suicidality) and D7 (encoder-only BERT/RoBERTa family — but base ~110M, half NeoBERT's 250M).

## Best point — Method to adopt
Domain-adaptive MLM continued-pretraining on mental-health text is a cheap, validated win, upstream of head design.
- **How to apply to Pebble:** Run a short MLM continued-pretraining pass of NeoBERT on in-domain emotional-support/Reddit text (or benchmark against MentalRoBERTa) for a better-adapted `[CLS]` start in the low-resource regime.

## Dataset / weights status
Model weights available on HF (soft-gate), **CC-BY-NC-4.0 → research-only, NOT deployable**. Pretraining corpus is private (not released). Eval datasets (CLPsych 2015, eRisk 2018) are gated/research-only. → use as a **research-arm** warm-start/baseline only; the deployed encoder must warm-start from an openly-licensed backbone.

## Caveats
Pre-LLM-distillation work, so D4/D5 absence is expected. Exact param count / per-dataset F1 not fully rendered; D6/D7 scored conservatively. Already referenced as the "MentalBERT line" in `related-work-survey.md`.
