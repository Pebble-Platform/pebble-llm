# Paper 09 — Multi-Task Learning as a Bargaining Game (Nash-MTL)

> Enrichment set · Pillar 1 (MTL loss balancing). Analysis depth: abstract-level. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Navon, Shamsian, Achituve, Maron, Kawaguchi, Chechik, Fetaya. ICML 2022.
- **Link:** [arXiv:2202.01017](https://arxiv.org/abs/2202.01017) · open
- **Pebble pillar:** principled multi-task loss balancing (named in Pebble's rubric).

## Summary
Frames per-task gradient combination as a Nash bargaining game, computing a single update direction whose per-task gains are balanced multiplicatively — making it scale-invariant across heterogeneous losses. Evaluated on vision/RL (NYUv2, CityScapes, CelebA, QM9, MTRL).

## Overlap with Pebble — 27% (peripheral)
`D1=1, D2=0, D3=0, D4=0, D5=2, D6=0, D7=0` → (3·1 + 2·2)/26 = 7/26 = **27%**
- **Closest on:** D5 (named in the rubric); weak partial D1 (head-agnostic, operates over any per-task gradient set).

## Best point — Method to adopt
Scale-invariance across MSE/CE/BCE is the property most likely to keep the high-recall BCE gradient from being swamped.
- **How to apply to Pebble:** Add Nash-MTL as a fourth balancing arm (static λ vs Kendall vs GradNorm vs Nash-MTL) — directly serves the survey's strongest angle (heterogeneous MTL under a hard safety-recall constraint).

## Dataset
Method paper — no dataset to acquire (vision/RL).

## Caveats
Abstract-only; vision/RL, not NLP-affect. Nash-MTL solves a small optimization per step (extra wall-clock) — relevant for Kaggle-GPU budgeting. A pure optimizer to borrow, not a comparable system.
