# Paper 15 — Detection of Suicidal Risk on Social Media: A Hybrid Model

> Enrichment set · Pillar 4 (C-SSRS severity). Analysis depth: abstract-only. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** 2025.
- **Link:** [arXiv:2505.23797](https://arxiv.org/html/2505.23797v1) · open
- **Pebble pillar:** suicide-risk severity classification with a RoBERTa backbone.

## Summary
A four-level Reddit suicide-severity classifier combining RoBERTa contextual embeddings with TF-IDF + PCA handcrafted features, beating RoBERTa-only and BERT baselines.

## Overlap with Pebble — 31% (peripheral)
`D1=0, D2=2, D3=0, D4=0, D5=0, D6=1, D7=2` → (2·2 + 2·1 + 1·2)/26 = 8/26 = **31%**
- **Closest on:** D2 (suicide-risk/crisis text) and D7 (RoBERTa encoder backbone).

## Best point — Baseline to beat
Reports **weighted F1 = 0.7512** on a four-level Reddit suicide-severity task close to Pebble's safety head.
- **How to apply to Pebble:** Use 0.75 weighted-F1 as the comparison bar for Pebble's crisis/severity head on a four-level Reddit corpus; note their TF-IDF+PCA concatenation as a cheap ablation — but frame Pebble's advantage as a **recall-floored** safety head (≥0.95), since their weighted-F1 objective doesn't protect the highest-risk minority class.

## Dataset
Four-level Reddit severity setup, consistent with the C-SSRS / CSSRS-Reddit lineage (inferred, not confirmed). No new open dataset identified to acquire.

## Caveats
Abstract-only; PDF body not text-extractable. **Exact dataset name/size, the four class definitions, and per-class high-risk recall could not be verified.** D6 scored 1 (severity is the target) not 2 — no hard recall constraint or ordinal loss evidenced; lowest-confidence dimension.
