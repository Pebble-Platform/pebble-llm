# Paper 02 — ABHINAYA: A System for Speech Emotion Recognition In Naturalistic Conditions Challenge

- **Authors:** Soumya Dutta, Smruthi Balaji, Varada R, Viveka Salinamakki, Sriram Ganapathy
- **Venue / year:** Interspeech 2025 (challenge system, SOTA post-challenge)
- **Links:** abs https://arxiv.org/abs/2505.18217 · PDF `pdfs/02-abhinaya-ser-challenge.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Kết hợp speech-SSL + text-LLM + fused speech-text models, ensemble majority-voting, loss chống class imbalance.

**Relevance to Pebble:** Cùng lab với bài LLM-distillation ICASSP 2025 đã cite; blueprint production cho fusion speech+text với imbalance-aware losses — map thẳng sang bài toán crisis-class imbalance.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

### Analysis — ABHINAYA (SER Naturalistic Challenge, Interspeech 2025)
> Supersedes the 2026-07-02 score of 12% computed against the stale text-only profile.

- **Profile scored against (assembled at analysis time):** (1) primary intent — honest ordinal suicide-risk **text** classification with LLM silver labels + gold-holdout eval; (2) active **voice** stream (`voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`) — heterogeneous MTL heads on a **frozen WavLM-Large / emotion2vec** backbone (emotion CE + affect **CCC** + crisis **hard recall-floor 0.90**, Kendall uncertainty weighting), currently on RAVDESS proxy labels, **named next step = swap to MSP-Podcast (A/V/D) + DAIC (crisis)**.
- **Overlap:** D1=0, D2=0, D3=1, D4=0, D5=0, D6=1, D7=2 → 19% (peripheral)
  - Formula: (3·0 + 2·0 + 1·1 + 2·0 + 2·0 + 2·1 + 1·2) / 26 × 100 = 5/26 × 100 ≈ 19%.
- **Closest on:** D7 (**WavLM-Large SSL backbone** — exact match to the voice stream's frozen encoder) and, weaker, D6/D3 (rare-class imbalance objective on a categorical emotion corpus).
- **Best point (Baseline to beat):** ABHINAYA's speech-only **S1 = WavLM-Large (317M)** with attentive-statistics pooling + a softmax emotion head scores **34.43 balanced-val / 33 test macro-F1** on **MSP-Podcast** 8-class categorical emotion — the same backbone and (per the voice roadmap) the same dataset Pebble's voice emotion head will move to.
  - **How to apply to Pebble:** When `voice-mtl-heads` swaps RAVDESS proxy labels for real MSP-Podcast (the roadmap's next task), anchor the emotion head against ABHINAYA's ~34% val / 33% test WavLM-Large single-model macro-F1 as the honest baseline, and trial its **attentive-statistics pooling** against the current masked-mean pool on the shared trunk.
- **Caveats:** Full paper read (no paywall). Score rose from 12%→19% only because the assembled profile now includes the voice stream, flipping D7 (0→2) on the WavLM backbone match; the text-primary dimensions (D1 heterogeneous heads, D2 crisis domain, D4 LLM-teacher distillation, D5 MTL gradient balancing) remain 0 — this is single-task categorical SER, and the LLMs (LLaMA-3 8B/70B, SALMONN) are encoders/classifiers, not label teachers. The baseline is **emotion-head only**: ABHINAYA has no continuous A/V/D head (despite MSP-Podcast carrying those labels) and no recall-floor/safety objective, so it is **not** a comparator for Pebble's affect-CCC or crisis heads. MSP-Podcast test labels are hidden (leaderboard-only), so numbers are balanced-val macro-F1 + hidden-test macro-F1.
