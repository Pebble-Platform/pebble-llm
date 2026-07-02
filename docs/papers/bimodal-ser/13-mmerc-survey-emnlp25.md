# Paper 13 — Multimodal Emotion Recognition in Conversations: A Survey of Methods, Trends, Challenges and Prospects

- **Authors:** Chengyan Wu, Yiqiang Cai, Yang Liu, Pengxu Zhu, Yun Xue, Ziwei Gong, Julia Hirschberg, Bolei Ma
- **Venue / year:** EMNLP 2025 Findings
- **Links:** abs https://arxiv.org/abs/2505.20511 · PDF `pdfs/13-mmerc-survey-emnlp25.pdf`
- **Group:** survey / benchmark

**Summary:** Survey mới nhất map fusion methodologies + evaluation protocols cho conversational ER text+audio(+visual).

**Relevance to Pebble:** Bản đồ chiến lược fusion audio+text — điểm vào chọn kiến trúc cho voice+message.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled profile (from `docs/intent/constraints.md` + `docs/spec/capabilities/voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`):** Pebble is a primary **ordinal suicide-risk text** program (BERT-class encoder, teacher-LLM silver labels, gold-holdout eval, ordinal QWK/MAE) plus an adjacent active **voice** stream (frozen emotion2vec/WavLM backbone; 3 heterogeneous MTL heads — emotion CE + affect valence/arousal CCC + crisis BCE under a hard recall ≥ 0.90 floor — balanced by Kendall uncertainty weighting). Forward direction: **voice+text fusion**. "Useful" = advances heterogeneous MTL heads, principled loss balancing, crisis-recall safety, silver-label distillation, or a fusion architecture for the text-primary + voice-auxiliary setup.

### Analysis — MMERC survey (Wu et al., EMNLP 2025 Findings)
- **Overlap:** 31% (peripheral) — D1=0, D2=1, D3=1, D4=1, D5=1, D6=0, D7=1
  - D1=0 (survey centers modality *fusion*, not heterogeneous categorical+continuous heads; all reported metrics are classification — WA/WF1/macro-F1/micro-F1)
  - D2=1 (emotion recognition is the affective substrate of Pebble's voice crisis head, but no mental-health/crisis framing; only a passing "intelligent healthcare" application mention)
  - D3=1 (catalogs canonical emotion corpora IEMOCAP/MELD/CMU-MOSEI/MEmoR/AVEC — voice-relevant, but not the named text transfer sets GoEmotions/EmpatheticDialogues/intensity)
  - D4=1 (surveys generation-based LLM-for-ERC methods — InstructERC, DialogueLLM, MLLMs — loosely adjacent to teacher-LLM labeling, but no silver-label-for-augmentation distillation pattern)
  - D5=1 (its "equal modality weights" vs "text-dominant primary-auxiliary" fusion taxonomy, and the challenges-section push for learnable modality gates / uncertainty-aware fusion / modality dropout, are adjacent to loss balancing — but it is *modality* weighting, not MTL *task*-loss balancing like Kendall/GradNorm/PCGrad)
  - D6=0 (no safety/crisis recall constraint anywhere; standard classification objectives only)
  - D7=1 (text feature-extraction table lists RoBERTa/sBERT — matches Pebble's BERT-family text backbone; audio extractors are older openSMILE/COVAREP/librosa, **not** the emotion2vec/WavLM SSL backbone Pebble's voice stream uses)
  - `(3·0 + 2·1 + 1·1 + 2·1 + 2·1 + 2·0 + 1·1)/26 × 100 = 8/26 × 100 = 31%`
- **Closest on:** the modality-fusion taxonomy (D5 — text-dominant primary-auxiliary vs equal-weight) and the canonical emotion corpora it maps (D3).
- **Best point (Design lesson):** The survey settles that for a text-primary system the winning architecture is a **text-dominant primary-auxiliary fusion** — text stays the core and audio/prosody is injected as an auxiliary cue via cross-modal attention (e.g. Zou et al.'s "weaker modalities as multimodal prompts"), which the survey reports outperforms naive equal-weight concatenation while preserving the strong modality's integrity.
  - **How to apply to Pebble:** When wiring the adjacent voice stream into the primary text risk model, adopt this text-dominant scheme (voice/prosody as auxiliary injected via cross-modal attention onto the BERT text encoder) rather than equal-weight fusion — it matches Pebble's text-primary intent, keeps the gold-holdout text model as the frozen-value core, and gives a citable design justification instead of re-deriving the fusion axis.
- **Caveats:** It is a **survey** — a design-space map, not a runnable method or a number to beat; no baseline metric to reproduce. Scored on a full read of §1–7 (intro, methodology, datasets/eval, methods taxonomy, challenges, conclusion). Zero coverage of Pebble's differentiators: crisis/mental-health domain, heterogeneous categorical+continuous MTL heads, hard recall-floor safety objective, teacher-LLM silver-label augmentation, and ordinal-aware metrics — hence the peripheral band despite the topical adjacency to the voice fusion direction. Voice SSL backbones (emotion2vec/WavLM) are not featured; the audio extractors surveyed predate them.
