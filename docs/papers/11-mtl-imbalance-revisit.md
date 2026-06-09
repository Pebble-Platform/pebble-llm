# Paper 11 — Revisit the Imbalance Optimization in Multi-task Learning

> Enrichment set · Pillar 1 (MTL loss balancing). Analysis depth: abstract + HTML. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** 2025 (experimental analysis).
- **Link:** [arXiv:2509.23915](https://arxiv.org/abs/2509.23915) · open
- **Pebble pillar:** principled MTL loss balancing — the **null hypothesis** Pebble's experiment must rule out.

## Summary
Benchmarks the exact methods Pebble is weighing (Kendall uncertainty, GradNorm, PCGrad, MGDA, CAGrad, Nash-MTL, FAMO) head-to-head on vision foundation models. Headline finding: simply scaling each task loss by its gradient norm matches an expensive grid search, and elaborate gradient-surgery methods give inconsistent gains.

## Overlap with Pebble — 27% (peripheral)
`D1=1, D2=0, D3=0, D4=0, D5=2, D6=0, D7=0` → (3·1 + 2·2)/26 = 7/26 = **27%**
- **Closest on:** D5 — it benchmarks the precise methods Pebble is choosing among.

## Best point — Design lesson
Gradient-norm scaling ≈ grid search; heavier methods (PCGrad/Nash-MTL/CAGrad) are inconsistent.
- **How to apply to Pebble:** Start with a cheap GradNorm-style gradient-norm rescale as the baseline balancer; treat PCGrad/Nash-MTL as something to *beat*, not the default — but note the asymmetry below.

## Dataset
Method/analysis paper — no dataset to acquire (NYUv2, Pascal, CelebA, Omnidata, Replica).

## Caveats
Pure computer-vision study — zero NLP/encoder/mental-health content, so transfer is by analogy. Crucially its tasks are homogeneous and **unconstrained**: it never tests a hard recall-floored head, so "gradient-norm scaling ≈ grid search" is **untested under Pebble's safety-recall ≥ 0.95 regime** — which is precisely Pebble's novel territory. Exact scaling formula not legible in the fetched PDF.
