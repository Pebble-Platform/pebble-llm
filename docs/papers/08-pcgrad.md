# Paper 08 — Gradient Surgery for Multi-Task Learning (PCGrad)

> Enrichment set · Pillar 1 (MTL loss balancing). Analysis depth: abstract-level. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Yu, Kumar, Gupta, Levine, Hausman, Finn. NeurIPS 2020.
- **Link:** [arXiv:2001.06782](https://arxiv.org/abs/2001.06782) · open
- **Pebble pillar:** principled multi-task loss balancing (named in Pebble's rubric).

## Summary
When two task gradients conflict (negative cosine similarity), projects one onto the normal plane of the other before the update — a model-agnostic, loss-weight-free way to stop tasks fighting. Demonstrated on vision and RL.

## Overlap with Pebble — 27% (peripheral)
`D1=1, D2=0, D3=0, D4=0, D5=2, D6=0, D7=0` → (3·1 + 2·2)/26 = 7/26 = **27%**
- **Closest on:** D5 (PCGrad is named in the rubric and the survey's recommended angle #1). Faint D1 (generic multi-head support).

## Best point — Method to adopt
Targets gradient *direction* conflict, complementary to magnitude schemes (Kendall/GradNorm target *scale*).
- **How to apply to Pebble:** Add PCGrad as a third arm in the balancing comparison. Especially relevant because Pebble's heads are heterogeneous (MSE vs CE vs high-weight BCE) where direction conflict is the likely failure mode. **Exempt/protect the crisis head from projection** so it can't erode the recall ≥ 0.95 floor.

## Dataset
Method paper — no dataset to acquire (vision/RL).

## Caveats
Abstract-only. No NLP, no encoder LM, no heterogeneous categorical+continuous+safety setup, no recall constraint — transfer is by analogy. A method/citation source, not a results baseline.
