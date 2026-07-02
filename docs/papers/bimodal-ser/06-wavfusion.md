# Paper 06 — WavFusion: Towards wav2vec 2.0 Multimodal Speech Emotion Recognition

- **Authors:** Feng Li, Jiusong Luo, Wanjun Xia
- **Venue / year:** MMM 2025 (Springer LNCS)
- **Links:** abs https://arxiv.org/abs/2412.05558 · PDF `pdfs/06-wavfusion.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Gated cross-modal attention + homogeneous-feature-discrepancy learning, wav2vec2 audio + text branch, eval IEMOCAP/MELD.

**Relevance to Pebble:** Reference ablation gọn cho lựa chọn cơ chế fusion.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled Pebble profile (at analysis time):** Primary intent = *ordinal* suicide-risk **text** classification with LLM silver labels under strict gold-holdout (ordinal-aware, subject-level splits, reproducible; `docs/intent/constraints.md`). Adjacent **voice** stream (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`) = heterogeneous multi-task heads on a **frozen SSL speech backbone** (WavLM-Large / emotion2vec): emotion (CE) + affect (valence/arousal **CCC regression**) + crisis (BCE under a **hard recall floor**), balanced by **Kendall uncertainty weighting**; **voice+text fusion** is the forward direction.

### Analysis — WavFusion (audio+text+visual SER)
- **Overlap:** 19% (peripheral) — D1=0, D2=0, D3=1, D4=0, D5=1, D6=0, D7=2.
  - Formula: (3·0 + 2·0 + 1·1 + 2·0 + 2·1 + 2·0 + 1·2) / 26 × 100 = 5/26 × 100 ≈ 19%.
  - D1=0 single categorical emotion head + a representation-level margin loss — no continuous/safety heads. D2=0 general acted/TV SER, not mental-health/crisis (mental health only namechecked in intro). D3=1 IEMOCAP/MELD are emotion corpora but not the intensity/transfer exemplars. D4=0 no teacher-LLM labels (fully supervised gold). D5=1 balances CE + margin loss but via a hand-tuned scalar λ grid (Table 5), not the principled methods (uncertainty/GradNorm/PCGrad). D6=0 no recall constraint. D7=2 wav2vec2.0 audio SSL backbone (same family as the voice stream's WavLM/emotion2vec) **and** RoBERTa-base text (BERT-family, matches the text stream).
- **Closest on:** D7 (SSL-speech + RoBERTa backbones match both Pebble streams); secondarily D5 (a concrete two-loss balancing sensitivity study).
- **Best point (Method to adopt):** Gated cross-modal attention fusion — a learnable per-channel sigmoid gate `P = σ(FC(X_A→T ⊕ X_A→V))`, `X_F = P⊙X_A→T + (1−P)⊙X_A→V` (Eqs 10–11) that dynamically filters redundant/misleading cross-modal signal, ablated cleanly against naive concatenation (concat 66.78 → gated attention 70.6 WF1 on IEMOCAP, Table 6).
  - **How to apply to Pebble:** when the voice MTL heads gain a text branch, fuse the audio and text streams with this learnable gate rather than concatenation — it is a drop-in, cheap, citable fusion block and its concat-vs-gated ablation is the reference comparison for that design choice.
- **Caveats:** Read in full (arXiv PDF, all 11 pp) — no paywall. Single **categorical** emotion task only; no continuous/CCC head, no crisis/recall-floor objective, no ordinal structure, no LLM weak labels, no gold-holdout — so it touches Pebble's *architecture forward-direction*, not its core evaluation thesis. Fusion gains are modest (+0.74 WF1 IEMOCAP, +0.44 MELD); MELD uses a fixed split while IEMOCAP is 5-fold (no reported std). The margin ("homogeneous feature discrepancy") loss needs paired same-emotion-across-modality samples, which Pebble's proxy-labeled RAVDESS voice-only setup cannot supply.
