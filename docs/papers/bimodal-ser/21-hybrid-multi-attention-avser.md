# Paper 21 — Hybrid Multi-Attention Network for Audio-Visual Emotion Recognition Through Multimodal Feature Fusion

- **Authors:** Sathishkumar Moorthy, Yeon-Kug Moon
- **Venue / year:** Mathematics (MDPI), 13(7):1100, 2025 (OA)
- **Links:** abs https://www.mdpi.com/2227-7390/13/7/1100 · PDF `pdfs/21-hybrid-multi-attention-avser.pdf`
- **Group:** audio-visual (đối chứng)

**Summary:** Hybrid multi-attention fusion network cho audio-visual affect.

**Relevance to Pebble:** Fallback fusion-ablation reference; venue tier thấp — không phải primary pick.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled profile (at analysis time).** Pebble = a primary **ordinal suicide-risk TEXT** program (NeoBERT/BERT-family ~250M encoder, teacher-LLM silver labels, gold-holdout eval, ordinal-aware QWK/MAE) under a hard "never train+eval on the same label source" constraint (`docs/intent/constraints.md`); plus an adjacent **VOICE** stream (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`): frozen emotion2vec/WavLM-Large SSL backbone + shared trunk with **three heterogeneous heads** — emotion (CE), affect (valence+arousal, **CCC loss**), crisis (BCE under a **hard recall floor ≥0.90**) — balanced by **Kendall uncertainty weighting**; forward direction is voice+text fusion. Scored against this profile.

**Paper in one line.** An audio-visual (and text, on IEMOCAP) emotion-recognition model whose contribution is a hybrid cross-modal attention fusion (CSSA = SEMAT+SPAAT; HASPCM = SMA+PCMA; collaborative cross-attention) built to stay robust when modalities are non-complementary / noisy / missing. Categorical emotion classification on IEMOCAP; continuous valence–arousal regression (with CCC) on AffWild2/AFEW-VA. Backbones: 3D-CNN/ResNet (visual), openSMILE/1D-CNN (audio), TextCNN (text).

**Per-dimension scores (before the number):** D1=1, D2=0, D3=1, D4=0, D5=0, D6=0, D7=0

- D1 (heterogeneous heads, w3) = **1** — produces both a categorical output (IEMOCAP) and continuous V/A with CCC (AffWild2/AFEW-VA), the two output types Pebble's voice stream needs, but on separate datasets/experiments, not one joint heterogeneous-head topology, and no safety head.
- D2 (mental-health/crisis, w2) = **0** — general affect; only a passing "diagnosis of emotion-related disorders" mention.
- D3 (emotion-transfer / intensity corpora, w1) = **1** — AffWild2 & AFEW-VA are dimensional V/A *intensity* corpora (rubric includes "intensity"), but not GoEmotions/EmpatheticDialogues and not the speech-only V/A sets (MSP-Podcast) Pebble targets.
- D4 (teacher-LLM silver-label distillation, w2) = **0** — none in the proposed method.
- D5 (principled MTL loss balancing, w2) = **0** — imbalance handled by 20-bin discretization + over/under-sampling; no uncertainty/GradNorm/PCGrad/Nash-MTL.
- D6 (safety/crisis recall constraint, w2) = **0** — absent.
- D7 (backbone match, w1) = **0** — 3D-CNN/openSMILE/TextCNN; no emotion2vec/WavLM SSL and no BERT-family text encoder.

**Overlap:** (3·1 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·0) / 26 × 100 = 4/26 × 100 = **15%** — **peripheral (<40%)**.

- **Closest on:** D1 (categorical + continuous-CCC affect outputs) and D3 (V/A intensity corpora).
- **Best point (Design lesson):** The paper's motivating finding — standard cross-attention fusion *assumes complementary modalities* and degrades on real data where they are non-complementary, noisy, or missing; their fix models intra- **and** cross-modal relations jointly so conflicting/absent streams don't collapse the prediction.
  - **How to apply to Pebble:** For the forward voice+text fusion, do not assume the streams agree — a calm voice over a suicidal text is the safety-critical non-complementary case; adopt a fusion head that preserves each modality's intramodal signal and tolerates a missing/uninformative stream, and stress-test it under modality dropout rather than reporting only the both-present number.
- **Caveats:** MDPI/`Mathematics` venue, low tier; categorical vs continuous tasks are on different datasets, so the "heterogeneous heads" credit is partial. Audio-visual with non-SSL backbones — its AffWild2 CCC numbers (val 0.596 / aro 0.683) are **not** a fair baseline for Pebble's speech-only affect head. Read from the local PDF (abstract, §2.2 related work, §3.1, §4.3–4.4 results); MDPI HTML returned HTTP 403, so scoring is from the PDF only.
