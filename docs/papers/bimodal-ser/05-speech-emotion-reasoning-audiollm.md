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

## Deep research — full-PDF read (2026-07-10)

> Re-read end-to-end against the **current ViEmoSpeech profile + Decision Register (V-A…V-H)**
> from `docs/tasks/paper-deep-analysis.md`. The stub's "Analysis (overlap with Pebble)" section
> above uses the **archived text-stream profile (D1–D7, NeoBERT/CSSRS)** and is stale — ignore
> its D-scores; this section supersedes it for ViEmoSpeech decisions. Cross-referenced with
> vn-08 (HGR VN-SER, 2604.01711), the other LLM-reasoning VN-SER paper.

### Source-access note

- **PDF read:** `pdftotext` on `docs/papers/bimodal-ser/pdfs/05-speech-emotion-reasoning-audiollm.pdf`
  (arXiv:2506.06820**v2** [cs.CL], 29 Sep 2025), full text incl. abstract, §§1–10, and all of
  Tables 1–7. Table columns 2/3/5–7 interleave badly in the text dump (multi-column layout); values
  below were reconstructed by cross-checking against the arXiv HTML.
- **Web validation.** Search `Beyond Classification Towards Speech Emotion Reasoning Multitask
  AudioLLMs 2506.06820 venue` → the paper is **arXiv-only** (cross-listed cs.CL / cs.SD / eess.AS),
  **no conference/journal acceptance stated** (Semantic Scholar + arXiv abs page, resolved
  `https://arxiv.org/abs/2506.06820`; alphaXiv `https://www.alphaxiv.org/overview/2506.06820v1`).
  Provenance rule: no venue version exists, so the local v2 PDF is authoritative.
- **Preprint-delta check.** Fetched the **v1** HTML (`https://arxiv.org/html/2506.06820v1`) and
  confirmed Table 1 (38.2 / 57.8 / 58.1 avg), Table 4 (Quotation 57.5 / Groundedness 82.8 /
  Relevance 65.3), and Table 5 (AudioLLM-Reasoning 59.3; WavLLM 50.8; Qwen2-Audio 49.8) are
  **identical v1→v2** ✔. Tables 2/3/6/7 and §7 numbers appear only in the PDF (not separately
  web-corroborated) → tagged ≈.

### What the paper actually does

**Goal.** Turn AudioLLM speech-emotion recognition from label-only classification into **emotion
*reasoning*** — the model outputs an emotion label *plus* a natural-language, evidence-grounded
explanation ("The speaker is clearly angry. Their statement 'I'm not starting over again'… suggests
frustration"). Three output tiers defined (Fig. 1): Label-Only < Interpretive Reasoning <
Evidence-Grounded Reasoning (quotes real spans + interprets them).

**Method — three coupled pieces (§3):**
1. **Reasoning-augmented supervision (§3.1).** A teacher LLM (**Gemma-2-9B-IT**) is fed the
   *transcript + gold emotion label + a reasoning prompt* and writes the explanation, which becomes
   the training target. Two prompt styles: **"Elaborate"** → evidence-grounded (quote explicit
   cues), **"Summarize"** → interpretive (implied context). The emotion *label stays gold*
   (IEMOCAP/MELD); only the rationale is LLM-generated. QA training pairs are built by sampling from
   a curated question pool ("How would you interpret the speaker's emotional state…").
2. **Dual-encoder fusion (§3.2).** A general **speech encoder** (fixed = Whisper-Large-v3) + a
   swappable **emotion-centric encoder**, each with a light MLP adapter (2 hidden, SiLU), projected
   to a shared space and concatenated, then fed to the LLM. Utterances zero-padded to 30 s → encoder
   seq len 1500; adapter **reshapes speech to 100 tokens and emotion to 10 tokens** ("condensed
   emotion-specific representation… complementary signal with minimal redundancy"). **Sequence-dim
   concat > feature-dim concat** (Table 2).
3. **Task-alternating training (§3.3).** Speech-centric tasks (ASR, SQA) train the speech
   encoder+adapter+LLM-LoRA; emotion-centric tasks (ER + explanation) train the emotion
   encoder+adapter+LLM-LoRA; the *other* branch is frozen each round. **Final epoch updates all
   adapters+LoRA jointly** for alignment. Backbone LLM adapted via **LoRA only** (not full FT).

**Config (§4.1):** Gemma-2-9B-IT LLM; Whisper-Large-v3 encoders; batch 48, 5 epochs, 8× H100, AdamW
(β 0.9/0.999), lr 5e-5. ✔ (method text).

**Data + eval (§4.2–4.3):** train/eval on **IEMOCAP** (10-class ER) and **MELD** (MELD-ER 7-class,
MELD-SR 3-class sentiment); semantic tasks from **MNSC** (Singlish SQA/ASR, chosen for low
pre-training contamination), Spoken-SQuAD, SLUE, LibriSpeech. Evaluated via **AudioBench** with
**LLM-as-a-Judge (Llama-3-70B-Instruct)** scoring binary semantic-alignment for ER/SR (normalized
0–100); ASR = WER.

**Key results (all avg over IEMOCAP/MELD-ER/MELD-SR unless noted):**
- **Reasoning targets beat label-only by ~20 pts** (Table 1): Label-Only **38.2** → Interpretive
  **57.8** → Evidence-Grounded **58.1** ✔. Note IEMOCAP jumps 18.6→60.8 (Interpretive) but
  Evidence-Grounded (58.6) is *lower* than Interpretive there.
- **Reasoning quality (Table 4):** ≥49% of responses contain a real quote (Quotation avg 57.5);
  **Groundedness 82.8** (quotes faithful to transcript), **Relevance 65.3** (quotes support the
  label) ✔.
- **Best end-to-end model (Table 5):** the final **AudioLLM-Reasoning** (Emotion2Vec+ Large emotion
  encoder, Alt-4-epoch) scores **59.3 avg**, beating WavLLM 50.8, Qwen2-Audio 49.8, Audio-Reasoner
  53.8, SALMONN 32.0 ✔ (top rows web-corroborated; others ≈).
- **Design ablations (Tables 2–3, ≈):** task-alternating > joint multitask (e.g. seq-concat Alt-1ep
  56.6 vs Joint 50.3); emotion encoder matters — **Emotion2Vec+ Large (Alt-4ep) = 59.3** best,
  Emotion2Vec+ base 54.8–56.2, **HuBERT-XL worst (49.5–50.8)**, Whisper-Tiny 49.5.
- **OOD generalization (Table 6, ≈):** on unseen **M3ED (Mandarin TV series)** 48.6 and **CPQA-ER
  (Singapore YouTube)** 49.0, AudioLLM-Reasoning beats Emotion2Vec+ Large (47.9 / 37.9) and
  Audio-Reasoner.
- **Emotion supervision is additive to a pre-trained base (Table 7, ≈):** adding emotion supervision
  to a base AudioLLM lifts ER/SR **+12.3** and **+22.4** pts on two configs while SQA/ASR stay
  within ~2 pts (WER 19.5→19.6; 3.8→3.6).
- **LLM-judge audit (§7, ≈):** on IEMOCAP 27.6% / MELD-ER 6% of predictions hit "special cases"
  (synonymy, multi-emotion, overlapping categories) where exact-match fails. Human check of 50
  special cases: only **2%** judge-correct/human-wrong, but **16% (IEMOCAP) / 30% (MELD-ER)**
  judge-wrong/human-correct → **the LLM judge is systematically conservative (under-credits)**.

### Parts directly useful for ViEmoSpeech (tagged with Decision IDs)

1. **Task-alternating multitask training over joint loss-summing — [V-A][V-G].** Each task family
   updates only its own encoder+adapter+LLM-LoRA branch; a final joint epoch aligns everything
   (Table 2: Alt beats Joint on the emotion tasks specifically, ~+4–6 pts). This is a concrete
   answer to "how do you carry emotion-CE + V/A-CCC + distress heads jointly without one head
   swamping the others."
2. **Dual-encoder with an asymmetric, condensed emotion token budget — [V-A][V-B].** General speech
   encoder → 100 tokens; **emotion-centric encoder → only 10 tokens** ("minimal redundancy"), fused
   by **sequence-dim concat** (> feature-dim). A design pattern for our audio+text/tone fusion: give
   the specialized (emotion/tone/phonation) stream a small dedicated slot rather than symmetric
   fusion.
3. **Emotion-centric encoder choice: Emotion2Vec+ ≥ Whisper-Large ≫ HuBERT-XL for ER — [V-B].**
   Table 3: Emotion2Vec+ Large (Alt-4ep) 59.3 vs HuBERT-XL 49.5–50.8, even though HuBERT-XL is
   larger (962M vs 164M). Pre-training *for emotion* beats scale. (Secondary to this paper's
   targets; corroborates our V-B lean.)
4. **Evidence-grounded reasoning target + separate Groundedness/Relevance rubric — [V-D][V-G].** The
   mechanism for producing *and scoring* an explanation of why an emotion was assigned: quote the
   evidence span, then score (0–2) whether the quote is real (Groundedness) and whether it supports
   the label (Relevance), *decoupled from label correctness*. This is the closest published template
   for how ViEmoSpeech's method paper could **explain a tone×emotion conflict** case.
5. **LLM-as-a-Judge with a human-validated conservativeness audit — [V-G].** Binary
   semantic-alignment scoring handles synonym/overlap emotion labels that exact-match breaks on
   (excited≈happy, anger≈frustration), *and* they measure the judge's error asymmetry against 4
   humans. Directly reusable if our tone×emotion explanation figure needs free-text scoring.
6. **Additive emotion supervision with bounded regression on other tasks — [V-A].** Table 7: bolting
   an emotion branch onto a trained base gained +12–22 pts ER with <2 pt ASR/SQA loss — evidence
   that a heterogeneous head can be *added* to a shared backbone without destroying the others,
   which is exactly the multi-head co-existence question in V-A.

### How each part helps ViEmoSpeech succeed

- **[V-A] Adopt task-alternating scheduling for the multi-head trainer.** Our heads are
  heterogeneous (emotion CE, V/A CCC, distress recall-floor) — a naive summed loss lets the
  high-gradient emotion-CE head dominate the CCC/distress heads. Port the alternating recipe:
  cycle *emotion-family* steps and *dimensional/distress-family* steps, updating only the active
  head + its adapter, then a joint final epoch. Concrete artifact: a `training/schedule` flag in the
  fusion trainer with an `alt_vs_joint` ablation row in the V-G eval table. **Transfer risk: HIGH.**
  Their alternation moved *encoders*; if ViEmoSpeech keeps a **frozen** audio backbone (V-B open),
  only adapters+heads alternate, a much weaker lever than what Table 2 measured — treat the +4–6 pt
  gain as an *upper bound* to test, not to assume.
- **[V-A][V-B] Give the emotion/tone stream a small dedicated token budget in fusion.** Copy the
  100-vs-10 asymmetric concat: let the phonation/tone-sensitive branch (emotion2vec / voice-quality
  vector from vn-06) occupy a short, condensed slot fused sequence-wise with the fuller
  PhoWhisper/PhoBERT semantic stream, so the tone channel is a *complementary* signal, not drowned.
  Concrete artifact: fusion module config `emotion_seq_len` << `speech_seq_len`. **Transfer risk:
  MEDIUM** — their fusion feeds a generative LLM; ours feeds classifier heads, so "token count" maps
  to pooled-segment count. The *principle* (asymmetric budget, seq-concat > feature-concat)
  transfers; the exact 100/10 does not.
- **[V-B] Default the audio branch to an emotion-pretrained encoder, keep HuBERT only as an arm.**
  Table 3 says emotion-pretraining beats raw scale for ER — aligns with our V-B lean toward
  emotion2vec(-S). Concrete artifact: the V-B encoder bake-off keeps Emotion2Vec+ as favourite,
  HuBERT-XL as a documented weak baseline. **Transfer risk: MEDIUM** — measured on English
  IEMOCAP/MELD, not VN tonal speech; emotion2vec's edge may shrink where lexical tone competes for
  the F0/phonation channel (vn-06/vn-13), so the arm must be *re-run* on ViEmoSpeech, not inherited.
- **[V-D][V-G] Use their evidence-grounded target + Groundedness/Relevance rubric as the *shape* of
  our tone×emotion explanation output.** When we want the method paper to *show* a tone×emotion
  conflict ("the word says X but the tone says Y"), emit a structured rationale (quote the syllable
  /token + name the competing channel) and score Groundedness (is the cited cue real?) separately
  from label accuracy. Concrete artifact: an optional `explanation` field on gold-slice conflict
  cases + a groundedness column in the V-G report. **Transfer risk: HIGH / redirect needed** — their
  grounding is in the **transcript (semantic content)**; a tone×emotion explanation must ground in
  the **acoustic/phonetic** channel (F0 contour, phonation), which their pipeline never scores. We'd
  need an *acoustic* groundedness metric — a genuine extension, not a copy.
- **[V-G] Borrow the LLM-judge conservativeness audit, not the judge as a headline metric.** If we
  ever score free-text emotion/tone explanations, replicate their 4-human check of 50 special cases
  and report the judge's false-wrong rate (theirs: up to 30% on MELD-ER). But our *primary* heads
  emit discrete labels + V/A scalars → use exact macro-F1 / CCC (V-G), reserving LLM-judge for the
  explanation figure only. **Transfer risk: LOW for the audit method; the judge itself is
  English-centric** (Llama-3-70B) and unvalidated on Vietnamese — do not run an LLM judge on VN
  output without a VN human calibration.

### Child / Vietnamese tone×emotion lens (transfer validity)

- **Architecture is the opposite pole from ViEmoSpeech.** This is a **9B generative AudioLLM
  (LoRA)** emitting free text; ViEmoSpeech is a **light multi-head classifier on a (likely frozen)
  SSL backbone** emitting labels + scalars. None of the absolute numbers transfer as bars; only the
  *training-schedule, fusion-topology, and evaluation-instrument* ideas do. State this explicitly in
  the method paper so a reviewer doesn't read Table 5's 59.3 as a comparable target.
- **The reasoning is semantic-grounded, which is exactly the channel VN tone contaminates.** Their
  Groundedness (82.8) rewards quoting the **transcript** — the "what is said." ViEmoSpeech's whole
  premise (vn-06 Shen, vn-13 Chang) is that in Vietnamese the **"how it is said" (F0/phonation)** is
  *shared with lexical tone*, so an explanation that only cites words misses the tone×emotion
  conflict entirely. Their headline "evidence-grounded is most desirable" therefore under-serves a
  tonal language: we must add an **acoustic-evidence** grounding axis they never had.
- **Found-speech, TV-drama OOD precedent is encouraging.** Their OOD set **M3ED = Mandarin Chinese
  TV series** (≈49.0) — a tonal-language, acted-drama corpus much like ViEmoSpeech's source — and
  the model generalized best there (Table 6, ≈). Weak but real signal that acted tonal-TV emotion is
  learnable; not a clinical/distress claim (their labels are 7 acted emotions, no distress axis).
- **Distress / safety is absent.** No recall-floor, no distress head, no clinical framing; Ethics
  §10 only warns generically about "misinterpretation of emotional cues." Nothing here informs V-F
  beyond the reminder that emotion≠distress. Do **not** cite this paper for the distress head.
- **Ethics/consent note for our own use.** Their supervision is LLM-teacher-authored rationales on
  public actor corpora; ViEmoSpeech under **ADR-003** restricts LLM teachers to *on-screen
  suggestion only*, human labels for training. If we ever import their rationale-generation trick,
  it must live on the *train-side auxiliary/explanation* channel with the human gold label intact —
  which is exactly their setup (label stays gold, only rationale is generated), so it is
  ADR-003-compatible *iff* rationales never become labels.

### Limitations & open questions for ViEmoSpeech (incl. contradictions/gaps)

- **Contradiction vs vn-08 (HGR VN-SER, 2604.01711) — the two LLM-reasoning routes diverge on who
  authors the reasoning.** vn-08 uses **human-guided** reasoning (human raters' clinical/contextual
  rationale steers the model; 86.6% / κ 0.857 on a *closed, non-speaker-disjoint* VN corpus — a
  leak-inflated ceiling per the wave-1 finding). Paper 05 uses **LLM-distilled** reasoning (Gemma-2
  writes rationales from transcript+gold-label; ~+20 pt on *public, contamination-controlled*
  IEMOCAP/MELD). **Shared blind spot both share with each other and with ViEmoSpeech's need:** both
  ground reasoning in **semantic/contextual content**, neither grounds in **acoustic tone** — so
  *neither* actually reasons over the tone×emotion channel competition that is ViEmoSpeech's
  novelty. That gap is our whitespace: an evidence-grounded explanation whose evidence is *phonetic*
  (F0/phonation), scored by an *acoustic* groundedness metric, is unpublished on either side.
- **Gap / contradiction vs the paper's own headline: grounding barely helps accuracy.**
  Evidence-Grounded (58.1) ≈ Interpretive (57.8) on average, and on IEMOCAP Interpretive (60.8)
  *beats* Evidence-Grounded (58.6) (Table 1 ✔). The ~20 pt jump is **label-only → any-reasoning**,
  not grounding specifically. Lesson for V-D: adding a reasoning target may lift emotion accuracy,
  but *acoustic grounding* should be justified for **explainability** (our method paper's story), not
  sold as an accuracy driver — we must measure both separately.
- **Contradiction vs ViEmoSpeech's frozen-backbone assumption (V-B).** Their gains ride on
  **trainable encoders + LoRA**; the task-alternating benefit (Table 2) is unmeasured for a frozen
  backbone. If we freeze (compute/legality/stability reasons), the V-A alternating lever may
  collapse — an open experiment, not a settled import.
- **LLM-as-a-Judge is English-only and conservative.** §7 shows the Llama-3-70B judge under-credits
  correct answers up to 30% (MELD-ER). For VN we have **no validated LLM judge**; V-G must stay on
  exact macro-F1 / CCC / recall@floor for the heads, with LLM-judge confined to (and human-calibrated
  for) any explanation figure.
- **No dimensional (V/A) or ordinal target anywhere.** Everything is categorical ER + 3-class SR;
  no valence/arousal regression, no CCC. So the paper offers **nothing for our V/A-CCC head** (V-G)
  — a real gap: our regression head's design must come from bimodal-12 (MSP-Podcast CCC) and vn-13,
  not here.
- **Open question:** does asymmetric fusion (10-token emotion slot) survive when the "emotion"
  stream is instead a **tone/phonation** stream competing with F0? Their emotion encoder and their
  labels never had lexical tone in the same channel — untested, and precisely the ViEmoSpeech
  experiment.

Sources: [arXiv abs 2506.06820](https://arxiv.org/abs/2506.06820) · [arXiv v1 HTML](https://arxiv.org/html/2506.06820v1) · [Semantic Scholar](https://www.semanticscholar.org/paper/a47dc5c7c024affc2312276a0bb6390dbb68d747) · [alphaXiv](https://www.alphaxiv.org/overview/2506.06820v1)
