# Paper 05 — Beyond Classification: Towards Speech Emotion Reasoning with Multitask AudioLLMs

- **Authors:** Wenyu Zhang et al. (I2R/A*STAR)
- **Venue / year:** arXiv preprint 2025
- **Links:** abs https://arxiv.org/abs/2506.06820 · PDF `pdfs/05-speech-emotion-reasoning-audiollm.pdf`
- **Group:** audio+text (trục chính)

**Summary:** AudioLLM dual-encoder sinh reasoning có bằng chứng thay vì chỉ nhãn, qua "reasoning-augmented supervision".

**Relevance to Pebble:** Analogue phía speech của silver-labeling bằng Gemini-teacher (điểm liên tục + giải thích).

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Pebble profile assembled at analysis time** (from `docs/intent/constraints.md` +
`docs/spec/capabilities/voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`):
Pebble's primary program is *honest* weak-supervision for **ordinal suicide-risk
text** classification (teacher-LLM silver labels → NeoBERT-class encoder →
**gold-holdout** CSSRS eval; QWK/MAE ordinal metrics; subject-level splits). The
adjacent **voice** stream puts **heterogeneous MTL heads on a frozen SSL backbone**
(emotion2vec / WavLM-Large): emotion cross-entropy + affect **V/A CCC** regression +
**crisis head under a hard recall floor (0.90)**, balanced by **Kendall uncertainty
weighting**; voice+text fusion is the forward direction. "Useful to Pebble" = it
moves one of these levers (heterogeneous heads, teacher-LLM silver supervision,
principled MTL balancing, crisis-recall objective, SSL backbone).

### Analysis — Speech Emotion Reasoning with Multitask AudioLLMs
- **Overlap:** 38% (peripheral, boundary of adjacent) — D1=1, D2=0, D3=0, D4=2, D5=1, D6=0, D7=1
  - Σ wᵢ·scoreᵢ = 3·1 + 2·0 + 1·0 + 2·2 + 2·1 + 2·0 + 1·1 = 10 → 10/26 = **38%**.
- **Closest on:** D4 (teacher-LLM generates the reasoning-augmented supervision — a
  Gemma-2-9B-IT teacher writes evidence-grounded rationales from transcript+label to
  train the student AudioLLM; the direct speech analogue of Pebble's Gemini
  silver-labeling). Partial support on D5 (task-alternating training is an MTL-balancing
  strategy, but not the uncertainty/GradNorm/PCGrad family Pebble uses) and D7
  (emotion2vec / HuBERT / WavLM tested as the emotion-centric encoder — a backbone-class
  match — though used as LLM feature extractors, not frozen-SSL + probe heads).
- **Best point (Method to adopt):** Pairing each label with an LLM-generated,
  **evidence-grounded rationale** (quoted spans + justification) as auxiliary supervision
  raised recognition accuracy ~20 pts on average, not just interpretability
  (Table 1: label-only avg 38.2 → evidence-grounded reasoning 58.1), and they score
  rationale quality with an LLM-as-judge **Groundedness** metric (are quotes real vs
  hallucinated) separate from label correctness.
  - **How to apply to Pebble:** When generating Gemini silver risk labels, also elicit a
    short evidence-grounded rationale (quoted post spans + why-this-level) and use its
    **groundedness** as a *label-quality filter* — drop/down-weight silver labels whose
    rationale is ungrounded/hallucinated before they enter the training pool. This feeds
    `label-quality.md` directly and keeps gold-holdout intact (rationales augment the
    train-side silver labels only; eval stays CSSRS gold).
- **Caveats:** Full PDF read (pp. 1–6, incl. abstract, method, Table 1) — no paywall.
  Architecture is a **generative dual-encoder AudioLLM** (Whisper-Large-v3 + emotion
  encoder → Gemma-2-9B LoRA), structurally far from Pebble's frozen-SSL + light MTL
  probe heads and from the NeoBERT text encoder. **No** mental-health/crisis domain
  (D2=0), **no** continuous regression or safety head (all outputs are generated text,
  so D1 is only partial), **no** crisis-recall objective (D6=0). D4=2 is scored
  generously: the classification *label* stays gold (IEMOCAP/MELD) — the LLM generates
  *rationales* (silver supervision), not the label itself, so it is silver-**supervision**
  distillation rather than silver-**label** distillation. Score sits on the 40%
  peripheral/adjacent boundary.
