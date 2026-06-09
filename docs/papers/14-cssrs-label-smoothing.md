# Paper 14 — Semi-Supervised Deep Label Smoothing for Suicide Risk Detection

> Enrichment set · Pillar 4 (C-SSRS severity). Analysis depth: abstract + arXiv HTML. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** 2024.
- **Link:** [arXiv:2405.05795](https://arxiv.org/abs/2405.05795) · open
- **Pebble pillar:** suicide-risk severity — benchmarks the **exact Reddit C-SSRS 500-user dataset Pebble already downloaded** (`data/external/cssrs/`).

## Summary
A CNN over learnable embeddings does single-task 5-class C-SSRS suicide-risk classification, with soft-label smoothing via MC-Dropout uncertainty. Improves the C-SSRS benchmark from 43.12% → 52.33% accuracy.

## Overlap with Pebble — 23% (peripheral)
`D1=0, D2=2, D3=0, D4=0, D5=0, D6=1, D7=0` → (2·2 + 2·1)/26 = 6/26 = **23%**
- **Closest on:** D2 (suicide-risk domain) and partial D6 (crisis-class recall reported, not enforced).

## Best point — Baseline to beat
A clean, citable benchmark on the dataset Pebble has: **43.12% → 52.33% acc, 49.23% weighted-balanced acc, 47.77% macro recall**, using only a CNN.
- **How to apply to Pebble:** Report Pebble's NeoBERT crisis/severity path against these numbers; a 250M pretrained encoder + GoEmotions warm-start should clear 52% acc / 49% balanced acc, and macro-recall is where the high-recall safety head shows its value.
- *Secondary (not headline):* MC-Dropout soft labels capture inter-rater disagreement — a possible regularizer for noisy Gemini silver labels.

## Dataset
Uses CSSRS-Reddit (already acquired, CC-BY-4.0). No new acquisition.

## Caveats
Architecture details from arXiv HTML v1. Despite the "semi-supervised" title, no unlabeled-data/pseudo-label mechanism is described (MC-Dropout self-relabeling only) — D4 and the semi-supervised claim are weaker than the title. No transformer/MTL/regression. Value to Pebble is almost entirely a comparison number on a shared dataset.
