# Paper 10 — LibMTL: A Python Library for Deep Multi-Task Learning

> Enrichment set · Pillar 1 (MTL tooling). Analysis depth: abstract + README. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Lin & Zhang. JMLR 2023.
- **Link:** [JMLR 24(2023)](https://www.jmlr.org/papers/volume24/22-0347/22-0347.pdf) · open · [GitHub](https://github.com/median-research-group/LibMTL)
- **Pebble pillar:** tooling for the MTL loss-balancing experiment (D5).

## Summary
A PyTorch library implementing 27 weighting strategies — Uncertainty Weighting (Kendall), GradNorm, DWA, PCGrad, MGDA, CAGrad, IMTL, Nash-MTL — under one unified `Weighting` API across 8 MTL architectures. Backbone-agnostic; ships a BERT example.

## Overlap with Pebble — 31% (peripheral, high-leverage)
`D1=1, D2=0, D3=0, D4=0, D5=2, D6=0, D7=1` → (3·1 + 2·2 + 1·1)/26 = 8/26 = **31%**
- **Closest on:** D5 (the exact balancing family Pebble plans) and partial D7 (backbone-agnostic; can wrap NeoBERT).
- Note: it's a *tool*, not a method paper — value is implementation reuse on the one dimension it nails.

## Best point — Method (tool) to adopt
Run the entire "static λ vs principled balancing" comparison by swapping a config flag instead of reimplementing each balancer.
- **How to apply to Pebble:** Wrap NeoBERT as the shared backbone, register the three heads (regression / softmax / BCE-safety) as tasks, sweep `weighting=EW|UW|GradNorm|PCGrad|NashMTL` → an apples-to-apples ablation at near-zero impl cost. This is Pebble's #1 publishable angle.

## Dataset
Tooling — no dataset. (Examples are CV-centric.)

## Caveats
Scored from abstract/README. Verify before adopting: (1) that per-task loss is fully user-supplied so MSE+CE+BCE can be mixed in one model (appears so, unconfirmed); (2) gradient-surgery methods add memory/compute that may matter under Kaggle limits. Contributes engineering leverage on D5 only.
