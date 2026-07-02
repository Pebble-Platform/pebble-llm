# Paper 18 — Joint Multimodal Transformer for Emotion Recognition in the Wild

- **Authors:** Paul Waligora, Haseeb Aslam, Osama Zeeshan, Soufiane Belharbi, Alessandro Lameiras Koerich, Marco Pedersoli, Simon Bacon, Eric Granger
- **Venue / year:** CVPRW 2024
- **Links:** abs https://arxiv.org/abs/2403.10488 · PDF `pdfs/18-joint-multimodal-transformer.pdf`
- **Group:** audio-visual (đối chứng)

**Summary:** Key-based cross-attention giữa transformer backbone từng modality (face+voice, Affwild2), bắt quan hệ intra- + inter-modal.

**Relevance to Pebble:** Block cross-attention đơn giản, dễ port nhất để ghép audio branch vào text branch hiện có.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled Pebble profile (at analysis time):**
- *Primary (intent, `constraints.md`):* ordinal suicide-risk **text** classification; LLM/weak silver labels honestly augmenting a scarce clinical gold set; **gold-holdout** eval; ordinal-aware throughout (QWK/MAE); subject-level splits; BERT-family encoder.
- *Adjacent voice stream (`voice-multimodal.md` → `voice-mtl-heads.md`):* frozen WavLM-Large / emotion2vec backbone + shared trunk, **3 heterogeneous heads** — emotion CE, affect **valence+arousal with CCC loss**, crisis BCE under a **hard recall floor (0.90)** — balanced by **Kendall uncertainty weighting**. Forward direction: voice+text fusion.

### Analysis — Joint Multimodal Transformer (JMT)
- **Overlap:** 15% (peripheral) — D1=1, D2=0, D3=1, D4=0, D5=0, D6=0, D7=0
  - Computed: (3·1 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·0) / 26 × 100 = 4/26 × 100 = 15%.
- **Closest on:** D1 (continuous affect regressed with **CCC loss** — the exact objective of Pebble's voice *affect* head) and D3 (Affwild2 as an in-the-wild continuous valence/arousal corpus).
- **Best point (Method to adopt):** The JMT fusion block — key-based cross-attention between two per-modality transformer streams, **plus a third "joint representation" branch** (concatenated features fed back through the cross-attention) whose sole job is to inject redundancy and make fusion robust when one modality is noisy/missing; ablations isolate it at **+1.3–1.8% over a vanilla cross-attention transformer** and fusion beats every unimodal baseline.
  - **How to apply to Pebble:** Use this as the template for the deferred **voice+text fusion** — cross-attend the frozen voice-encoder stream against the NeoBERT text stream and add the concatenated joint branch as the noise-robustness mechanism for when the voice modality is absent/degraded; keep the shared **CCC loss** on the affect target the fusion inherits from the voice affect head.
- **Caveats:** Full PDF read (open, not paywalled). Everything transfers only to the *adjacent voice/fusion* stream, not the primary text program — hence peripheral. **No** heterogeneous multi-head MTL, **no** loss balancing (single-task CCC per experiment, so D5=0), **no** teacher/silver-label distillation (D4=0), **no** mental-health/crisis domain or recall constraint (D2=D6=0). Backbone does **not** match Pebble's voice SSL stack — audio branch is ResNet18 on spectrograms, not WavLM/emotion2vec (D7=0). Reported numbers are on Affwild2 (V/A) and BioVid pain, both gated/external, so they are not a directly comparable baseline for Pebble's RAVDESS proxy-label runs.
