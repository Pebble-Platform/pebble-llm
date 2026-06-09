# Paper 16 — Evaluating LLM Reasoning for Suicide Screening with the C-SSRS

> Enrichment set · Pillar 4 (C-SSRS severity). Analysis depth: abstract + arXiv HTML. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** 2025.
- **Link:** [arXiv:2505.13480](https://arxiv.org/abs/2505.13480) · open · [code](https://github.com/av9ash/llm_cssrs_code)
- **Pebble pillar:** suicide-risk severity; LLM-vs-human label agreement (informs the Gemini-teacher question).

## Summary
Zero-shot evaluation of frozen decoder LLMs (Claude/GPT/Mistral/LLaMA) on the C-SSRS 7-point ordinal scale over r/SuicideWatch posts — no fine-tuning, no heads. Analyzes where models' severity judgments err.

## Overlap with Pebble — 31% (peripheral)
`D1=0, D2=2, D3=0, D4=1, D5=0, D6=1, D7=0` → (2·2 + 2·1 + 2·1)/26 = 8/26 = **31%**
- **Closest on:** D2 (suicide-risk domain) and, weakly, D6/D4 (crisis severity as the task; LLM-vs-human agreement on severity labels).

## Best point — Design lesson
Models make almost all errors between **adjacent** C-SSRS levels (ordinal sensitivity); Mistral wins on ordinal *error*, not exact accuracy.
- **How to apply to Pebble:** For the CSSRS-Reddit signal feeding Pebble's severity head, use an **ordinal / distance-aware loss and metric** (MAE / QWK / ordinal-regression CE), not flat CE, so adjacent-level confusions cost less than far ones — and report ordinal error, not just macro-F1.

## Dataset
Uses public r/SuicideWatch; no new dataset to acquire. Code is open.

## Caveats
Scored from abstract + HTML landing page; full PDF (confusion matrices, dataset size/split, prompt design) unread → lowers confidence on D4/D6. Zero-shot evaluation of frozen LLMs — no encoder fine-tuning, MTL, or actual distillation training, so D1/D3/D5/D7 are firmly 0.
