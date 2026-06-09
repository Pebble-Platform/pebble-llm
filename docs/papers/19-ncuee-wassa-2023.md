# Paper 19 — NCUEE-NLP at WASSA 2023: Sentiment-Enhanced RoBERTa for Empathy + Emotion

> Enrichment set · Pillar 5 (intensity/empathy regression). Analysis depth: abstract + task desc. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** NCUEE-NLP, WASSA 2023 Shared Task 1 (ACL workshop).
- **Link:** [ACL Anthology 2023.wassa-1.49](https://aclanthology.org/2023.wassa-1.49/) · open
- **Pebble pillar:** continuous affect regression with RoBERTa-family encoders.

## Summary
An ensemble of three RoBERTa-family models (RoBERTa, RoBERTa-Twitter, EmoBERTa) for turn-level and essay-level empathy/distress/emotion-intensity **regression** at WASSA 2023. Track 2 (essay empathy/distress) Pearson 0.4178, rank 1 of 9.

## Overlap with Pebble — 31% (peripheral)
`D1=1, D2=1, D3=1, D4=0, D5=0, D6=0, D7=2` → (3·1 + 2·1 + 1·1 + 1·2)/26 = 8/26 = **31%**
- **Closest on:** D7 (RoBERTa encoder family) and D1 (continuous affect regression — but via separate ensembled models, not heterogeneous heads on a shared `[CLS]`; no categorical emotion or safety head).

## Best point — Method to adopt
Warm-starting from **affect/sentiment-domain-adapted checkpoints** (RoBERTa-Twitter, EmoBERTa) measurably lifts empathy/emotion regression over vanilla RoBERTa.
- **How to apply to Pebble:** Treat "affect-adapted init" as an explicit ablation arm alongside the GoEmotions warm-start and the staged freeze/unfreeze schedule — cheap signal on how much gain comes from affect-aware initialization vs the heads.

## Dataset
WASSA 2023 shared-task data (extends Buechel 2018; the base is acquired — see paper 23). Extended set is CodaLab-gated.

## Caveats
PDF body unreadable; architecture-level scores (D1, D5) rest on the ACL abstract + task description. "Ensemble of three RoBERTa variants" implies separate per-model heads, not one shared-encoder multi-task model → D1=1 (if a shared encoder w/ multiple heads, D1→2, ≈35%). No distillation/balancing/safety content.
