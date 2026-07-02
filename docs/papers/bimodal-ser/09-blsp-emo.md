# Paper 09 — BLSP-Emo: Towards Empathetic Large Speech-Language Models

- **Authors:** Chen Wang, Minpeng Liao, Zhongqiang Huang, Junhong Wu, Chengqing Zong, Jiajun Zhang
- **Venue / year:** arXiv preprint, 06/2024
- **Links:** abs https://arxiv.org/abs/2406.03872 · PDF `pdfs/09-blsp-emo.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Speech-LM hai giai đoạn: semantic alignment (ASR data) → emotion alignment (SER continuation task), hướng tới phản hồi đồng cảm.

**Relevance to Pebble:** Audio-LLM analogue gần nhất với framing emotional-support-chat của Pebble.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Profile scored against (assembled 2026-07-03 from IDD layers):** primary = ordinal suicide-risk **text** classification, teacher-LLM **silver labels** → BERT-family encoder, **gold-holdout** eval, ordinal-aware losses (QWK/MAE) — validity/ethics over SOTA (`docs/intent/constraints.md`). Adjacent **voice** stream (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`): frozen **emotion2vec/WavLM-Large** backbone + shared trunk, **3 heterogeneous heads** (emotion CE · affect V/A **CCC** · crisis BCE under **hard recall-floor 0.90**), **Kendall uncertainty weighting**, trained on **RAVDESS** proxy labels, Kaggle run pending.

### Analysis — BLSP-Emo
- **Overlap:** 35% (peripheral) — D1=1, D2=0, D3=1, D4=2, D5=0, D6=0, D7=1.
  - Formula: (3·1 + 2·0 + 1·1 + 2·2 + 2·0 + 2·0 + 1·1)/26 = 9/26 = 35%.
- **Closest on:** D4 (teacher-LLM silver-label distillation — LLM generates emotion-conditioned continuations as supervision, distilled via KD); secondarily D3/D7 (SER corpora incl. RAVDESS; WavLM/HuBERT/wav2vec2 baselines = Pebble's voice backbones).
- **Best point (Baseline to beat):** Table 1 reports **encoder-based SER classifiers on the exact backbone+corpus Pebble's voice stream uses** — WavLM-Large = **70.3%** acc on RAVDESS (5-class), 68.9% IEMOCAP; HuBERT-Large 70.5% RAVDESS; wav2vec2-Large 64.0% RAVDESS.
  - **How to apply to Pebble:** use WavLM-Large 70.3% / RAVDESS as the external sanity-check comparator for the emotion head in the pending `voice-mtl-heads` Kaggle run — but note the labels aren't apples-to-apples (BLSP-Emo maps RAVDESS onto a 5-class {neutral,happy,sad,angry,surprise} set as an OOD test; the MTL probe uses 8-class RAVDESS with a random 10-fold split), so treat it as a ballpark for a frozen-backbone SER head, not a matched benchmark.
- **Caveats:** end-to-end **generative** empathetic Speech-LLM (Whisper enc + Qwen-7B + modality adapter) — architecturally far from Pebble's frozen-probe MTL classifier; no continuous/regression head, no principled MTL balancing, no crisis/safety objective, not a clinical/mental-health domain (hence D2/D5/D6=0). PDF read pages 1–5 (method + main-results tables); later sections (multi-turn conversation, cross-lingual generalization, appendices B/C) unread — not needed for the score, but confidence on those is lower.
