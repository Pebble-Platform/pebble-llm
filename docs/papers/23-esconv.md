# Paper 23 — Towards Emotional Support Dialog Systems (ESConv)

> Enrichment set · Pillar 7 (emotional-support domain). Analysis depth: abstract + annotation summary + dataset fetch. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Liu, Zheng, Demasi, Sabour, Li, Yu, Jiang, Huang. ACL 2021.
- **Link:** [arXiv:2106.01144](https://arxiv.org/abs/2106.01144) · [ACL 2021.acl-long.269](https://aclanthology.org/2021.acl-long.269/) · open
- **Pebble pillar:** in-domain emotional-support dialogue dataset (Pebble's downstream domain).

## Summary
Introduces ESConv: 1,300 multi-turn emotional-support dialogues (38K turns) with pre-chat **emotion category + 1–5 emotion-intensity** ratings, per-utterance **support-strategy** labels, and seeker feedback scores. The modeling side is generative (strategy-conditioned BlenderBot), not a multi-task affect encoder.

## Overlap with Pebble — 31% (peripheral)
`D1=1, D2=2, D3=1, D4=0, D5=0, D6=0, D7=0` → (3·1 + 2·2 + 1·1)/26 = 8/26 = **31%**
- **Closest on:** D2 (emotional-support / psychological-distress domain) and D1 (label space spans categorical emotion/problem/strategy + continuous intensity & feedback — though no multi-head encoder is built).

## Best point — Dataset to reuse
Human **emotion category + 1–5 intensity** + feedback scores in exactly Pebble's support domain — paired categorical + continuous affect labels.
- **How to apply to Pebble:** Map intensity → `severity`/`energy` and emotion → the softmax head; use as a small in-domain **human-labeled calibration slice** to check Gemini silver scores against real human intensity (a calibration anchor for the distillation angle).

## Dataset status — ✅ ACQUIRED
`data/external/esconv/` (ESConv.json + train/valid/test = 910/195/195 convs). **License CC-BY-NC-4.0 → research-only, NOT deployable.** Source: [HF thu-coai/esconv](https://huggingface.co/datasets/thu-coai/esconv) / [GitHub thu-coai](https://github.com/thu-coai/Emotional-Support-Conversation).
- `emotion_type` (anxiety/depression/sadness/anger/fear/shame/disgust/nervousness/…) maps to the emotion head; `strategy` (8 classes) is a candidate new head.
- **Next step:** add `load_esconv()` to `external.py` (mirror `load_semeval_intensity`); document the NC license in the docstring (research arm only).

## Caveats
Architecture details from abstract + secondary summaries. A dialog-*generation* paper — no affect classifier/encoder, no continuous head, no safety head, no distillation, no MTL balancing → D4–D7 = 0. Value is the labeled dataset, not a method.
