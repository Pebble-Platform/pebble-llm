# Paper 22 — ModernBERT: A Modern Bidirectional Encoder

> Enrichment set · Pillar 7 (encoder backbone). Analysis depth: abstract-only. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Warner et al. 2024.
- **Link:** [arXiv:2412.13663](https://arxiv.org/pdf/2412.13663) · open · weights on HF (base 149M / large 395M)
- **Pebble pillar:** alternative encoder backbone / baseline vs NeoBERT.

## Summary
An efficient encoder-only transformer (GeGLU, RoPE, alternating local-global attention, full unpadding) trained with MLM on 2T tokens, native 8,192-token context, SOTA classification/retrieval, best-in-class GPU efficiency. Released base (149M) and large (395M).

## Overlap with Pebble — 8% (peripheral)
`D1=0, D2=0, D3=0, D4=0, D5=0, D6=0, D7=2` → (1·2)/26 = 2/26 = **8%**
- **Closest on:** D7 only — same class of modern encoder as NeoBERT (named in the rubric); base/large bracket NeoBERT's ~250M.

## Best point — Baseline to beat
The strongest publicly available same-size-class encoder alternative to NeoBERT, with long (8K) context.
- **How to apply to Pebble:** Add ModernBERT-base/large as the head-to-head backbone baseline — fine-tune the identical three-head stack and report whether NeoBERT actually beats it, so the backbone choice is evidence-backed not assumed. Its long context is the natural fallback if multi-turn inputs exceed NeoBERT's window.

## Dataset
Backbone paper — no dataset to acquire.

## Caveats
Abstract-only, but the abstract fully determines D1–D6 absent / D7 strong, so score confidence is high. ModernBERT contributes no method on Pebble's core questions (heterogeneous MTL, distillation, crisis-recall) — value is purely backbone/baseline + efficiency reference.
