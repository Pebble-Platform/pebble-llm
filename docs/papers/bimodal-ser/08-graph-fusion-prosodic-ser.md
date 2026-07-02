# Paper 08 — Enhancing SER with Graph-Based Multimodal Fusion and Prosodic Features

- **Authors:** Alef Iury Ferreira, Lucas Rafael Gris, Alexandre Ferro Filho, Lucas Ólives, Daniel Ribeiro, Luiz Fernando, Fernanda Lustosa, Rodrigo Tanaka, Frederico Oliveira, Arlindo Galvão Filho (Federal University of Goiás, Brazil, et al.)
- **Venue / year:** Interspeech 2025 SER-Naturalistic-Conditions Challenge system, arXiv 2025
- **Links:** abs https://arxiv.org/abs/2506.02088 · PDF `pdfs/08-graph-fusion-prosodic-ser.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Fusion đa encoder — Wav2Vec2/HuBERT/WavLM/Whisper/XEUS + RoBERTa — qua graph attention networks, kèm prosodic features.

**Relevance to Pebble:** Trả lời trực tiếp câu "chọn SSL audio encoder nào + text encoder nào + fuse ra sao".

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Pebble profile used (assembled at analysis time):** Primary = ordinal suicide-risk **text** classification, LLM/weak silver labels augmenting a scarce clinical gold set under **gold-holdout**, ordinal-aware, BERT-family encoder. Adjacent **voice** stream = heterogeneous MTL on a **frozen WavLM-Large / emotion2vec** backbone — 3 heads (emotion CE, affect V/A via **CCC**, crisis under a **hard recall floor**) balanced by **Kendall uncertainty weighting**; named next step = swap proxy labels for **MSP-Podcast** (A/V/D) + DAIC. Voice+text **fusion** is the forward direction.

### Analysis — Graph-Fusion + Prosodic SER (Interspeech 2025 challenge)
- **Overlap:** 12% (peripheral) — D1=0, D2=0, D3=1, D4=0, D5=0, D6=0, D7=2
  - D1=0 single-task categorical emotion (no heterogeneous continuous/safety heads); D2=0 podcast affect, not crisis; D3=1 emotion corpus and it is **MSP-Podcast**, the voice task's named next real-label target; D4=0 CED audio-tag distillation + vote ensemble, not teacher-LLM silver labels; D5=0 inverse-freq weighted CE, no principled MTL balancing; D6=0 Recall reported but no recall-floor objective; D7=2 direct backbone match (WavLM/Wav2Vec2/HuBERT/Whisper/XEUS + RoBERTa-Large).
- **Closest on:** D7 (SSL audio + text encoder family, identical to the voice stream) and D3 (MSP-Podcast, the exact next-step corpus).
- **Best point (Design lesson):** Their frozen-feature SSL backbone bake-off on naturalistic MSP-Podcast ranks **Whisper Large V3 (Macro F1 0.366) > XEUS 0.323 > WavLM-Large 0.313 > HuBERT 0.274 > Wav2Vec2 0.178** — on spontaneous emotional speech the ASR-pretrained Whisper/XEUS features beat WavLM/Wav2Vec2, and simple concat fusion (0.388) nearly matches complex graph fusion / MDAT (0.401) at this data scale.
  - **How to apply to Pebble:** when the voice-mtl-heads task swaps its RAVDESS proxy for real MSP-Podcast, add **Whisper Large V3 and XEUS** to the frozen-backbone comparison instead of assuming WavLM/emotion2vec, and keep the fusion baseline as plain concatenation before investing in graph attention.
- **Caveats:** Full PDF read (arXiv v1, not paywalled). Low overlap is honest, not incomplete: this is a single-task categorical **challenge system** with no heterogeneous MTL heads, no MTL loss-balancing, no crisis/recall constraint, and no LLM weak-label distillation — its value to Pebble is confined to backbone selection (D7) and the shared MSP-Podcast corpus (D3), not the core ordinal/MTL thesis.
