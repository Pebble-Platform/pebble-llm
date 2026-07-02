# Paper 19 — HiCMAE: Hierarchical Contrastive Masked Autoencoder for Self-Supervised Audio-Visual Emotion Recognition

- **Authors:** Licai Sun, Zheng Lian, Bin Liu, Jianhua Tao
- **Venue / year:** Information Fusion (Elsevier), 2024
- **Links:** abs https://arxiv.org/abs/2401.05698 · PDF `pdfs/19-hicmae.pdf` (bản arXiv; journal paywalled)
- **Group:** audio-visual (đối chứng)

**Summary:** Masked-modeling + contrastive pretraining trên audio-visual không nhãn, fine-tune trên 9 dataset categorical/dimensional.

**Relevance to Pebble:** Cùng logic "pretrain rẻ, fine-tune trên nhãn khan hiếm" như GoEmotions warm-start + Gemini silver labels.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Profile assembled at analysis time** (from `docs/intent/constraints.md` + `docs/spec/capabilities/voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`): Pebble's primary intent is *text* ordinal suicide-risk with LLM weak labels under gold-holdout/honest eval — HiCMAE touches none of that. The relevant surface is the **adjacent voice stream**: a *frozen SSL audio backbone* (WavLM-Large / emotion2vec) + shared SUPERB trunk carrying **three heterogeneous heads** — emotion (CE), affect valence/arousal (CCC), crisis (BCE under a hard recall floor) — balanced by Kendall uncertainty weighting, with **voice+text fusion as the forward direction**.

### Analysis — HiCMAE (audio-visual SSL emotion)
- **Overlap:** D1=1, D2=0, D3=1, D4=0, D5=0, D6=0, D7=1 → (3·1 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·1)/26 = 5/26 = **19% (peripheral)**
- **Closest on:** D1 (one SSL backbone serves *both* categorical emotion and *dimensional* valence — the same categorical+continuous split Pebble's voice MTL heads target, though HiCMAE fine-tunes each task separately rather than as joint heterogeneous heads) and D7 (an SSL audio(-visual) emotion backbone, same "frozen-SSL-features + downstream probe" family as WavLM/emotion2vec, but audio-*visual* not audio-only, and self-trained on VoxCeleb2 rather than a WavLM/emotion2vec checkpoint).
- **Best point (Baseline to beat):** HiCMAE reports per-dataset WAR/WF1 on exactly the corpora Pebble's voice stream uses — RAVDESS, IEMOCAP, CREMA-D, MSP-IMPROV (categorical) and valence via Pearson (dimensional) — with public code + pretrained checkpoints, i.e. a published *bimodal SSL* ceiling for SER on shared benchmarks.
  - **How to apply to Pebble:** in the `voice-mtl-heads` writeup, cite HiCMAE's RAVDESS/IEMOCAP WAR as the audio-visual SSL upper bound and frame Pebble's audio-only frozen-probe numbers as the honest, lower-resource comparator — the same "modality gap" caveat the proxy-label note already carries; do not treat it as an apples-to-apples baseline (it adds the visual channel Pebble lacks).
- **Caveats:** Journal version paywalled; scored from the arXiv PDF (abstract + Sec. 1–3 + Fig. 2 radar) — exact per-dataset tables and loss weights not fully read. D5=0/D6=0 confident (no principled MTL balancing, no safety/recall objective — HiCMAE's losses are reconstruction + contrastive, not task-balanced heads); D1 held at 1 because categorical+dimensional are separate fine-tunes, not simultaneous heterogeneous heads. No mental-health/crisis (D2=0) and no teacher-LLM distillation (D4=0).
