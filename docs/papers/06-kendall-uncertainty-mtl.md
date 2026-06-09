# Paper 06 — Multi-Task Learning Using Uncertainty to Weigh Losses

> Enrichment set · Pillar 1 (MTL loss balancing). Analysis depth: abstract-level. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Kendall, Gal, Cipolla. CVPR 2018.
- **Link:** [arXiv:1705.07115](https://arxiv.org/abs/1705.07115) · open
- **Pebble pillar:** principled multi-task loss balancing (the canonical "Kendall" method named in Pebble's strategy).

## Summary
Jointly trains regression (depth) + classification (semantic/instance segmentation) heads on a shared CNN backbone, weighting each task loss by a learned homoscedastic-uncertainty term so noisier/harder tasks down-weight themselves automatically.

## Overlap with Pebble — 38% (peripheral)
`D1=2, D2=0, D3=0, D4=0, D5=2, D6=0, D7=0` → (3·2 + 2·2)/26 = 10/26 = **38%**
- **Closest on:** D5 (the canonical uncertainty-weighting method) and D1 (joint regression + classification on a shared trunk — the same heterogeneous-head structure Pebble has).

## Best point — Method to adopt
Replace hand-tuned λ with a learned per-task log-variance: `L = Σ exp(−sᵢ)·Lᵢ + sᵢ`, so MSE/CE/BCE units stop fighting each other.
- **How to apply to Pebble:** Add a learnable log-variance per head (continuous / emotion-softmax / safety-BCE); this is the first MTL arm to try, before GradNorm. **Floor or cap the safety head's weight** (or keep its asymmetric positive-class weight) — pure uncertainty weighting has no notion of a recall floor and could silently down-weight it below recall 0.95.

## Dataset
Method paper — no dataset to acquire (vision: NYUv2/CityScapes-style depth+segmentation).

## Caveats
Scored from abstract only; backbone is a CNN and the entire setup is computer-vision, so D2/D3/D4/D6/D7 are firmly 0. Value is purely the loss-balancing formulation. The "peripheral" band understates leverage: it's a method-only match on Pebble's single most relevant open question (D5).
