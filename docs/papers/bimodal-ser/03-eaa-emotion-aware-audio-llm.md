# Paper 03 — EAA: Emotion-Aware Audio LLMs with Dual Cross-Attention and Context-Aware Instruction Tuning

- **Authors:** Hongfei Du, Sidi Lu, Gang Zhou, Ye Gao
- **Venue / year:** Interspeech 2025 (pp. 5433–5437)
- **Links:** abs https://www.isca-archive.org/interspeech_2025/du25b_interspeech.html · PDF `pdfs/03-eaa-emotion-aware-audio-llm.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Dual cross-attention fuse luồng acoustic + semantic trong audio-LLM, instruction tuning theo context; motivation nêu rõ mental-health monitoring.

**Relevance to Pebble:** Reference kiến trúc sạch nhất cho một fusion layer cross-modal attention giữa audio và text.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

### Analysis — EAA (Emotion-Aware Audio LLM)
- **Profile used (voice-aware, assembled 2026-07-02):** text stream (NeoBERT ~250M, teacher-LLM silver labels, gold-holdout, ordinal) **+ active voice stream** (`voice-mtl-heads`: frozen WavLM-Large/emotion2vec SSL backbone → 3 heterogeneous heads emotion/affect-CCC/crisis-recall-floor, Kendall weighting; voice+text fusion is the forward direction).
- **Overlap:** D1=0, D2=1, D3=1, D4=0, D5=0, D6=0, D7=2 → **19%** (peripheral). Formula: (3·0 + 2·1 + 1·1 + 2·0 + 2·0 + 2·0 + 1·2)/26 × 100 = 5/26 × 100 = 19.2% ≈ 19%. **Supersedes the 2026-07-02 score of 12% computed against the stale text-only profile** (the lift is D7 0→2: HuBERT is a WavLM-class SSL speech encoder, a direct backbone-family match to the active voice stream).
- **Closest on:** D7 (frozen SSL speech-encoder backbone — HuBERT semantic + BEATs acoustic — is the same WavLM/emotion2vec-class family the voice stream uses) and D2/D3 (mental-health named as motivation; MELD is a 7-class categorical dialogue-emotion corpus overlapping the voice emotion head). Everything else — heterogeneous multi-task heads, continuous/affect + safety heads, LLM silver-label distillation, principled MTL loss balancing, crisis recall constraint — is absent (EAA is single-task categorical SER).
- **Best point (Design lesson):** The attention ablation settles a fusion-direction question for the voice+text roadmap — bidirectional **dual** cross-attention (0.687 acc) beats single-direction cross-attention (semantic-as-query 0.610, acoustic-as-query 0.671) and plain self-attention (0.675); *acoustic-as-query attending to semantic key/value* is the stronger single direction, and they concatenate the original un-fused features with the fused outputs to preserve modality-specific information (Eq. 4).
  - **How to apply to Pebble:** For the stated voice+text fusion step (after `voice-mtl-heads` lands), fuse the frozen-SSL voice features with the NeoBERT text stream via bidirectional dual cross-attention with a residual concat of original + fused streams — not a simple concat/linear projection — and default to acoustic/voice-as-query if forced to pick one direction. This is a near-term-relevant design choice now that voice is an active stream, not a deferred text-only footnote.
- **Caveats:** Full 5-page PDF read, no paywall — scores high-confidence. EAA is single-task (emotion word generated as LLaMA-3-8B text output, LoRA), so D1/D4/D5/D6 are genuinely 0; its "distillation" is an LLM producing labels directly, not a teacher silvering data for a small encoder. Mental-health is motivation only; evaluation is MELD (TV-show dialogue SER), not a clinical/crisis corpus. Value remains a fusion-architecture reference for the bimodal roadmap; the fusion sits inside audio (acoustic↔semantic), whereas Pebble's fusion is voice↔text, so the mechanism transfers but the modality pairing differs.
