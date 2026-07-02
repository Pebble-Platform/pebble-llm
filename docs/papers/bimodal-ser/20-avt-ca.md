# Paper 20 — AVT-CA: Multimodal Emotion Recognition using Audio-Video Transformer Fusion with Cross Attention

- **Authors:** Joe Dhanith P R, Shravan Venkatraman, et al.
- **Venue / year:** arXiv preprint 2024 (v4 01/2026; preprint-only — chưa thấy acceptance)
- **Links:** abs https://arxiv.org/abs/2407.18552 · PDF `pdfs/20-avt-ca.pdf` · code github.com/shravan-18/AVTCA
- **Group:** audio-visual (đối chứng)

**Summary:** Hierarchical visual attention (channel+spatial+local) fuse với audio qua cross-attention transformer; eval CMU-MOSEI, RAVDESS, CREMA-D.

**Relevance to Pebble:** Reference engineering cho fusion ablation; rank thấp vì chưa peer-reviewed.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled Pebble profile (at analysis time).** Primary stream: ordinal
suicide-risk **text** classification — teacher-LLM silver labels, gold-holdout
eval on held-out clinical CSSRS, subject-level splits, ordinal-aware losses/metrics
(QWK/MAE), reproducible-by-construction (`docs/intent/constraints.md`). Adjacent
**voice** stream (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`):
heterogeneous 3-head MTL on a **frozen emotion2vec / WavLM-Large** backbone —
emotion (CE), affect valence+arousal (**CCC loss**), crisis (BCE under a **hard
recall floor ≥0.90**), balanced by **Kendall uncertainty weighting**, trained on
RAVDESS frozen features; voice+text fusion is the forward (deferred) direction.

### Analysis — AVT-CA (audio-video cross-attention fusion)
- **Overlap:** 4% (peripheral) — D1=0, D2=0, D3=1, D4=0, D5=0, D6=0, D7=0
  - Formula: (3·0 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·0) / 26 × 100 = 1/26 × 100 ≈ 4%.
- **Closest on:** D3 (dataset) — trains/evaluates on **RAVDESS** and **CREMA-D**;
  RAVDESS is exactly the corpus Pebble's voice MTL probe uses. That single-corpus
  overlap is the only real tie.
- **Why the rest score 0:** single **categorical** emotion task (Angry/Disgust/
  Fear/Happy/Neutral/Sad), accuracy+F1 only — no continuous/affect head, so no
  heterogeneous MTL (D1=0) and no principled loss balancing (D5=0); general MER,
  no mental-health/crisis and no recall constraint (D2=D6=0); no teacher-LLM
  distillation (D4=0); backbone is a **custom audio-video transformer** with
  channel/spatial attention over pre-extracted features, **not** the emotion2vec/
  WavLM SSL Pebble's voice stream uses (D7=0). CMU-MOSEI is used categorically,
  not as sentiment-intensity regression.
- **Best point (Method to adopt — forward direction, low current leverage):** the
  **intermediate transformer fusion + agreement-driven cross-attention** — the
  cross-attention module selectively reinforces *mutually consistent* audio-visual
  cues and suppresses noisy ones, reporting large ablation gains vs early/late
  fusion.
  - **How to apply to Pebble:** bank it as the reference recipe for the deferred
    **voice+text fusion** step — swap the video branch for the frozen text encoder
    and gate voice↔text tokens by mutual agreement so a noisy voice frame can't
    override a confident text-risk signal; it is not actionable at the current
    stage (single-modality voice MTL heads + primary text), so it stays a citation
    for the fusion chapter, not a task.
- **Caveats:** **preprint-only** (arXiv v4, no peer review) — treat all numbers as
  unverified; reported RAVDESS 96.11% acc / CREMA-D / MOSEI 95.84% are
  **within-distribution** single-benchmark results, **not** gold-holdout, so they
  are not a Pebble baseline to beat. Loss function not stated explicitly in the
  abstract/intro; inferred single-task CE from the accuracy/F1-only reporting and
  categorical label set (pp. 1–2, 7–9 read; method-section loss equations not fully
  verified).
