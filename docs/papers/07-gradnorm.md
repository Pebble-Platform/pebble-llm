# Paper 07 — GradNorm: Gradient Normalization for Adaptive Loss Balancing

> Enrichment set · Pillar 1 (MTL loss balancing). Analysis depth: abstract-level. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Chen, Badrinarayanan, Lee, Rabinovich. ICML 2018.
- **Link:** [arXiv:1711.02257](https://arxiv.org/abs/1711.02257) · open
- **Pebble pillar:** principled multi-task loss balancing (the "GradNorm" method named in Pebble's strategy).

## Summary
Rebalances task weights by equalizing the normalized gradient magnitudes at the last shared layer, using a single asymmetry hyperparameter α to control how aggressively faster-learning tasks are held back. Built for mixed regression + classification in one network.

## Overlap with Pebble — 38% (peripheral, borderline adjacent)
`D1=2, D2=0, D3=0, D4=0, D5=2, D6=0, D7=0` → (3·2 + 2·2)/26 = 10/26 = **38%**
- **Closest on:** D5 (named in Pebble's rubric) and D1 (explicitly for mixed regression + classification in one shared-trunk network — Pebble's MSE+CE+BCE situation).

## Best point — Method to adopt
Equalize per-task normalized gradient norms at the shared `[CLS]`/last-shared layer; α is the one knob.
- **How to apply to Pebble:** When the three heads diverge under static weights, apply GradNorm at the shared `[CLS]` with α≈1.5 and benchmark it head-to-head against Kendall uncertainty weighting (the two MTL arms on Pebble's roadmap).

## Dataset
Method paper — no dataset to acquire (vision + synthetic regression).

## Caveats
Abstract-level scoring. Two transfer risks: (1) GradNorm balances learning *rates*, not recall — it will not by itself guarantee the safety head's recall ≥ 0.95 (enforce via class weighting/thresholding on top). (2) Vision-only; no encoder, domain, or distillation content. Value is the optimization recipe, not domain/data.
