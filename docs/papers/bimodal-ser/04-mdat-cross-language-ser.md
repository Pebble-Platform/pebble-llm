# Paper 04 — Cross-Language SER Using Multimodal Dual Attention Transformers (MDAT)

- **Authors:** Syed Aun Muhammad Zaidi, Siddique Latif, Junaid Qadir
- **Venue / year:** arXiv preprint 2024 (under review, IEEE TAFFC)
- **Links:** abs https://arxiv.org/abs/2306.13804 · PDF `pdfs/04-mdat-cross-language-ser.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Graph attention + co-attention trên cặp encoder audio+text pretrained, tối ưu cho ít dữ liệu target-domain (cross-language).

**Relevance to Pebble:** Low-resource domain adaptation — đúng bài toán thích nghi sang miền clinical ít nhãn của Pebble. Lưu ý: preprint-only, cite trung thực.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Pebble profile used (assembled 2026-07-03 from `docs/intent/constraints.md` + `docs/spec/capabilities/voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`):** Primary text stream = ordinal suicide-risk classification, train on weak/LLM silver labels + evaluate on held-out clinical gold (gold-holdout always), ordinal losses/metrics (QWK/MAE), BERT-family encoder. Adjacent voice stream = frozen emotion2vec/WavLM SSL + shared trunk with heterogeneous MTL heads (emotion CE + affect V/A CCC + crisis BCE under a hard recall floor ≥0.90), Kendall uncertainty weighting; voice+text fusion is the forward direction.

### Analysis — MDAT (Cross-Language SER via Dual Attention Transformers)
- **Overlap:** 12% (peripheral) — D1=0, D2=0, D3=1, D4=0, D5=0, D6=0, D7=2 → (Σ wᵢ·scoreᵢ = 3)/26 × 100.
- **Closest on:** D7 (backbone match — XLS-R wav2vec2 SSL for audio + RoBERTa/BERT-family for text mirror both Pebble streams' backbones); weakly D3 (standard SER emotion corpora).
- **Best point (Method to adopt):** the **dual-attention fusion** — a co-attention layer (Lu et al. 2016 style, softmax-normalised) plus per-modality graph attention over the two frozen encoders, aligned by length pad/crop, which preserves modality-specific information while fusing and beats simple concatenation and BiLSTM/HCAM fusion on emotion.
  - **How to apply to Pebble:** when the voice stream moves to voice+text fusion, insert a co-attention block over the frozen WavLM/emotion2vec audio features and NeoBERT text features (pad/align lengths first) feeding the existing 3 MTL heads, instead of concatenation — a cheap, citable fusion upgrade that keeps each modality's signal.
- **Caveats:** preprint only (arXiv v3, under review IEEE TAFFC) — cite honestly, no benchmark claim. Single categorical emotion head → nothing transfers for head topology, MTL balancing (D1/D5=0), crisis recall floor (D6=0), or LLM distillation (D4=0). Reports UA only (no ordinal metrics). K-shot "low-resource adaptation" uses real gold target labels, so it is *not* the gold-holdout weak-label setting and does not model Pebble's clinical scarcity protocol.
