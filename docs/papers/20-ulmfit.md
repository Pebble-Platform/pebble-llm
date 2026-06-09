# Paper 20 — ULMFiT: Universal Language Model Fine-tuning for Text Classification

> Enrichment set · Pillar 6 (staged fine-tuning). Analysis depth: abstract-only. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Howard & Ruder. ACL 2018.
- **Link:** [arXiv:1801.06146](https://arxiv.org/abs/1801.06146) · [ACL](https://aclanthology.org/P18-1031.pdf) · open
- **Pebble pillar:** staged freeze→unfreeze schedule (canonical citation).

## Summary
Inductive transfer-learning framework for NLP introducing **gradual unfreezing**, **discriminative (per-layer) learning rates**, and **slanted triangular learning rates (STLR)** to fine-tune a pretrained AWD-LSTM language model on small target data without catastrophic forgetting.

## Overlap with Pebble — 4% (peripheral)
`D1=0, D2=0, D3=0, D4=0, D5=0, D6=0, D7=1` → (1·1)/26 = 1/26 = **4%**
- **Closest on:** D7 only, and partial — it shares the "pretrain-then-fine-tune a neural LM for classification" paradigm, but the backbone is an AWD-LSTM, not a BERT/RoBERTa/NeoBERT-class transformer.

## Best point — Method (citation anchor)
The staged fine-tuning recipe: gradual unfreezing + discriminative LRs + STLR — the canonical, citable foundation for fine-tuning on small target data without forgetting.
- **How to apply to Pebble:** Pebble's "frozen encoder → unfreeze" schedule should adopt gradual unfreezing (top NeoBERT layers first, then deeper) + discriminative LRs (lower for lower layers, higher for heads) + a slanted-triangular/warmup-decay LR — directly relevant given the tiny target set (~5K silver + ~1K human). Cite ULMFiT as the source.

## Dataset
Method paper — no dataset to acquire.

## Caveats
Abstract-only; the specific technique definitions are taken from the well-known published method, not re-verified line-by-line. Low domain/architecture overlap — value is purely the fine-tuning schedule, since largely superseded by transformer-native practice. Treat as a framing/citation anchor.
