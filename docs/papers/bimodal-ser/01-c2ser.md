# Paper 01 — C²SER: Steering Language Model to Stable Speech Emotion Recognition via Contextual Perception and Chain of Thought

- **Authors:** Zhixian Zhao, Xinfa Zhu, Xinsheng Wang, Shuiyuan Wang, Xuelong Geng, Wenjie Tian, Lei Xie
- **Venue / year:** IEEE TASLP, 2025
- **Links:** abs https://arxiv.org/abs/2502.18186 · PDF `pdfs/01-c2ser.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Audio-LLM SER kết hợp Whisper (semantic) + **emotion2vec-S** (acoustic), dùng chain-of-thought + self-distillation để ổn định phân loại cảm xúc.

**Relevance to Pebble:** emotion2vec là audio backbone Pebble đã chọn — đây là reference kiến trúc trực tiếp cho việc nhúng nó vào pipeline có LLM teacher/distillation.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

### Analysis — C²SER
- **Profile assembled at analysis time** (intent + capabilities, not the stale text-only snapshot): Pebble = primary **ordinal suicide-risk text** program (NeoBERT ~250M, Gemini silver labels, honest gold-holdout eval; ordinal-aware QWK/MAE; ethics + reproducibility) **plus an active adjacent voice stream** (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`): a **frozen WavLM-Large / emotion2vec backbone** + shared trunk carrying **three heterogeneous heads** — emotion (CE), affect valence+arousal (**continuous, CCC loss**), crisis (BCE under a **hard recall floor 0.90**) — balanced by **Kendall uncertainty weighting**, currently on proxy labels with **MSP-Podcast (A/V/D)** and **DAIC (crisis)** as the next real-label targets. Backbone fine-tune is an explicit non-goal (features stay frozen).
- **Supersedes the 2026-07-02 score of 31% computed against the stale text-only profile.**
- **Overlap:** D1=0, D2=0, D3=1, D4=2, D5=1, D6=0, D7=2 → (Σ wᵢ·scoreᵢ = 3·0+2·0+1·1+2·2+2·1+2·0+1·2 = 9) / 26 × 100 = **35% (peripheral)**
- **Closest on:** D7 (Emotion2Vec-S is a released extension of **emotion2vec — the voice stream's actual frozen backbone**, and the paper also benchmarks WavLM) and D4 (dual-teacher intersection silver-labeling + explicit→implicit self-distillation).
- **Best point (Method to adopt):** C²SER's **Emotion2Vec-S** adds a **category-level contrastive loss** on top of emotion2vec's utterance/frame losses and, per Table V, consistently beats plain Emotion2Vec and WavLM-base on emotion accuracy across Chinese/English/multilingual test sets — and its checkpoint is publicly released.
  - **How to apply to Pebble:** swap the voice stream's frozen feature extractor to the released **Emotion2Vec-S** checkpoint for the emotion head — a drop-in upgrade that respects the "backbone stays frozen" non-goal (no fine-tune), needs no architecture change to the 3-head MTL probe, and is testable in the pending `pebble-voice-mtl-heads` Kaggle run as an A/B against the current emotion2vec features.
- **Caveats:** Single-task **categorical** SER via a generative ALM — **no** heterogeneous heads (D1=0), **no** continuous/ordinal or crisis-recall objective (D5 loss balancing is hand-tuned λ_utt=0.1 / λ_cate=100, explicitly **not** Kendall/GradNorm → D5=1 partial only; D6=0), and **no** mental-health/crisis domain (D2=0). D3=1 partial: it trains on real speech-emotion corpora incl. **MSP-Podcast** (a voice-stream target), but uses them as flat categorical SER, not continuous affect. The Emotion2Vec-S swap and the dual-teacher gate transfer to the **voice** stream and the **text** silver-label stage respectively; neither touches the NeoBERT architecture. Scored from pp. 1–8 (abstract, related work, full method, data prep, experiment setup, Table V results); ablation tables were skimmed and do not affect the dimension scores.
