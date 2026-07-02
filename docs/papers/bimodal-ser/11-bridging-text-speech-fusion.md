# Paper 11 — Bridging Text and Speech for Emotion Understanding: Explainable Multimodal Transformer Fusion with Unified Audio–Text Attribution

- **Authors:** Ashutosh Pandey, Jasmeet Singh, Maninder Kaur
- **Venue / year:** Journal of Intelligence (MDPI), 13(12):159, 2025 (CC-BY; mirror PMC12733550)
- **Links:** abs https://www.mdpi.com/2079-3200/13/12/159 · PDF `pdfs/11-bridging-text-speech-fusion.pdf`
- **Group:** survey / benchmark (fusion framework)

**Summary:** RoBERTa (text) + WavLM (audio) chiếu vào latent space chung; attribution Integrated-Gradients/Occlusion tách phần đóng góp linguistic vs acoustic.

**Relevance to Pebble:** Kiến trúc audio+text fusion cụ thể + phương pháp explainability chuyển được sang voice-mode. Venue tier thấp hơn IEEE/Interspeech — rank vì topical fit.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Profile assembled at analysis time** (from `docs/intent/constraints.md` + `docs/spec/capabilities/voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`):
Pebble = a primary **ordinal suicide-risk text** program (BERT-family encoder, teacher-LLM silver labels, strict gold-holdout + subject-level splits, ordinal-aware QWK/MAE) **plus** an adjacent active **voice** stream: a frozen WavLM-Large / emotion2vec backbone with **three heterogeneous MTL heads** — emotion (CE), affect (valence+arousal, CCC loss), crisis (BCE under a **hard recall floor ≥0.90**) — balanced by **Kendall uncertainty weighting**; voice+text fusion is the named forward direction. This paper is a **single-head, end-to-end late-fusion** emotion classifier (RoBERTa-base + WavLM-Base-Plus) on MELD, 5 categories, with post-hoc XAI attribution.

**Per-dimension scores (before the number):**
- **D1** (multi-task heterogeneous heads; w=3) = **0** — one classification head over 5 emotion categories; no continuous/regression head, no safety head, no MTL at all.
- **D2** (mental-health / crisis domain; w=2) = **0** — generic conversational emotion (MELD / "Friends" TV); mental health is only rhetorical framing in the intro.
- **D3** (emotion-transfer corpora; w=1) = **1** — MELD is a categorical emotion corpus usable for Pebble's emotion head, though not one of the listed GoEmotions/EmpatheticDialogues/intensity sets.
- **D4** (teacher-LLM silver-label distillation; w=2) = **0** — human-annotated MELD labels only; no distillation.
- **D5** (principled MTL loss balancing; w=2) = **0** — plain cross-entropy, single objective; no uncertainty/GradNorm/PCGrad.
- **D6** (safety/crisis recall constraint as objective; w=2) = **0** — per-class recall is reported, but no recall-floor constraint drives training/thresholding.
- **D7** (encoder backbone match; w=1) = **2** — WavLM-Base-Plus **and** RoBERTa-base directly match both Pebble streams' backbone families.

**Overlap:** `(3·0 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·2) / 26 × 100 = 3/26 × 100` = **12%** — **peripheral (<40%)**.

- **Closest on:** D7 (exact WavLM+RoBERTa backbone match) and, weakly, D3 (MELD as an emotion corpus).
- **Best point (Method to adopt):** the **unified per-modality attribution** — Integrated Gradients on text tokens + Occlusion on fixed audio windows — decomposes a single prediction into linguistic vs acoustic-prosodic evidence.
  - **How to apply to Pebble:** wrap the same IG(text)+Occlusion(audio) pass around the crisis head so every flag raised under the hard recall floor carries a "driven by prosody vs. lexical content" attribution — the clinical-auditability layer a bare recall number can't provide, and the one thing here that a generic fusion recipe doesn't already give us.
- **Caveats:** open-access, full text read (no paywalled sections). Confidence-lowering mismatches, not unread gaps: (1) fine-tuned **end-to-end**, opposite to Pebble's frozen-backbone probe; (2) MELD uses the standard split with **no speaker/subject-disjoint guarantee**, which would violate Pebble's subject-level integrity constraint if reused as-is; (3) statistical power is thin (Wilcoxon p=0.125, 3 seeds); (4) 83% MELD accuracy is a within-distribution number, not a gold-holdout result. The fusion recipe (project 768→256, concat→512, dropout 0.3, 2-layer head; ablation: 128-d bottleneck > 256 > 512) is a usable secondary blueprint when Pebble reaches the fusion forward direction.
