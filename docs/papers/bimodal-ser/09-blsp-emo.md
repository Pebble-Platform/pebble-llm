# Paper 09 — BLSP-Emo: Towards Empathetic Large Speech-Language Models

- **Authors:** Chen Wang, Minpeng Liao, Zhongqiang Huang, Junhong Wu, Chengqing Zong, Jiajun Zhang
- **Venue / year:** arXiv preprint, 06/2024
- **Links:** abs https://arxiv.org/abs/2406.03872 · PDF `pdfs/09-blsp-emo.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Speech-LM hai giai đoạn: semantic alignment (ASR data) → emotion alignment (SER continuation task), hướng tới phản hồi đồng cảm.

**Relevance to Pebble:** Audio-LLM analogue gần nhất với framing emotional-support-chat của Pebble.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Profile scored against (assembled 2026-07-03 from IDD layers):** primary = ordinal suicide-risk **text** classification, teacher-LLM **silver labels** → BERT-family encoder, **gold-holdout** eval, ordinal-aware losses (QWK/MAE) — validity/ethics over SOTA (`docs/intent/constraints.md`). Adjacent **voice** stream (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`): frozen **emotion2vec/WavLM-Large** backbone + shared trunk, **3 heterogeneous heads** (emotion CE · affect V/A **CCC** · crisis BCE under **hard recall-floor 0.90**), **Kendall uncertainty weighting**, trained on **RAVDESS** proxy labels, Kaggle run pending.

### Analysis — BLSP-Emo
- **Overlap:** 35% (peripheral) — D1=1, D2=0, D3=1, D4=2, D5=0, D6=0, D7=1.
  - Formula: (3·1 + 2·0 + 1·1 + 2·2 + 2·0 + 2·0 + 1·1)/26 = 9/26 = 35%.
- **Closest on:** D4 (teacher-LLM silver-label distillation — LLM generates emotion-conditioned continuations as supervision, distilled via KD); secondarily D3/D7 (SER corpora incl. RAVDESS; WavLM/HuBERT/wav2vec2 baselines = Pebble's voice backbones).
- **Best point (Baseline to beat):** Table 1 reports **encoder-based SER classifiers on the exact backbone+corpus Pebble's voice stream uses** — WavLM-Large = **70.3%** acc on RAVDESS (5-class), 68.9% IEMOCAP; HuBERT-Large 70.5% RAVDESS; wav2vec2-Large 64.0% RAVDESS.
  - **How to apply to Pebble:** use WavLM-Large 70.3% / RAVDESS as the external sanity-check comparator for the emotion head in the pending `voice-mtl-heads` Kaggle run — but note the labels aren't apples-to-apples (BLSP-Emo maps RAVDESS onto a 5-class {neutral,happy,sad,angry,surprise} set as an OOD test; the MTL probe uses 8-class RAVDESS with a random 10-fold split), so treat it as a ballpark for a frozen-backbone SER head, not a matched benchmark.
- **Caveats:** end-to-end **generative** empathetic Speech-LLM (Whisper enc + Qwen-7B + modality adapter) — architecturally far from Pebble's frozen-probe MTL classifier; no continuous/regression head, no principled MTL balancing, no crisis/safety objective, not a clinical/mental-health domain (hence D2/D5/D6=0). PDF read pages 1–5 (method + main-results tables); later sections (multi-turn conversation, cross-lingual generalization, appendices B/C) unread — not needed for the score, but confidence on those is lower.

## Deep research — full-PDF read (2026-07-10)

> Analyzed against the **current ViEmoSpeech profile + Decision Register (V-A…V-H)** in
> `docs/tasks/paper-deep-analysis.md`, NOT the stale text-stream profile in the "Analysis"
> block above (which scored this paper for the archived suicide-risk product and is retained
> only as history). This section is APPENDED; nothing above is altered.

### Source-access note

Local PDF `pdfs/09-blsp-emo.pdf` (arXiv:2406.03872**v1**, 6 Jun 2024) read end-to-end via
`pdftotext` — method (§2), experiment setup (§3), all main-results tables (Tables 1–5), the
cross-lingual table (Table 3), ablations (§4.2), the ChatGPT/MultiTask analysis (§4.3),
Limitations, and Appendices B–E (dataset table, training details, prompts, qualitative examples).
Provenance validation:
- **Venue status** — search `BLSP-Emo … 2406.03872 published venue` resolved to
  `https://arxiv.org/abs/2406.03872`; the paper is an **arXiv preprint** (cs.CL, 6 Jun 2024),
  code+weights at `github.com/cwang621/blsp-emo` / `huggingface.co/cwang621/blsp-emo`. No
  peer-reviewed venue confirmed in the arXiv HTML (a ResearchGate mirror hints at a later
  posting but is not corroborable) → treated as preprint; v1 is the only version, so no
  preprint-vs-published delta to reconcile. ✔
- **Table 1 numbers** — cross-checked against the arXiv HTML render
  `https://arxiv.org/html/2406.03872v1`; the load-bearing MELD figure **BLSP-Emo = 57.3%**
  matches the local PDF exactly and equals the **0.573** that bimodal-03 (EAA) cites. ✔
  All Table 1 rows below are corroborated against that HTML render.

### What the paper actually does

**Goal.** Build an end-to-end empathetic speech-LLM that understands *both* semantics *and*
paralinguistic emotion in speech and generates empathetic text, using ONLY existing ASR + SER
datasets (no new emotion-conditioned instruction data). It is an **Audio-Language Model (ALM)**,
not a discriminative SER fusion network.

**Architecture (§2.1, App. C).** Whisper-large-v2 **encoder** → convolution **modality adapter**
(3× 1-D conv, stride 2, kernel 5, pad 2, ×8 downsample, bottleneck dim 512) → **Qwen-7B-Chat** LLM.
✔ (App. C).

**Two-stage alignment (the core method):**
1. **Semantic alignment (§2.2).** Behavior-cloning on ASR data: prompt the *text* LLM to continue a
   transcript, then train the speech model to emit the *same* continuation from speech, via a
   **KL-divergence knowledge-distillation loss** (Eq. 1). **Only the modality adapter is tuned;
   speech encoder + LLM stay frozen.** Produces the "BLSP" checkpoint.
2. **Emotion alignment (§2.3).** From SER triples (speech `s`, transcript `x`, emotion `e`), prompt
   the LLM to write an **emotion-aware continuation** ("Continue … that reflects a `<emotion>` tone
   … `<transcript>`"). Then fine-tune the model to reproduce that continuation **from speech alone**
   (prompt no longer names the emotion — the model must read it off the audio). Primary loss = LM
   loss on the continuation (Eq. 2), **plus an auxiliary SER classification head** on pooled adapter
   hidden states (Eq. 3). **Here the speech encoder AND the LLM are unfrozen** (LLM via **PLoRA**,
   R=16, α=16, applied only to speech tokens), plus the adapter and the classifier. ✔ (§2.3, App. C).

**Data (§3.1, App. B/Table 6).** Semantic stage: ~**1.9M** English (speech, transcript) pairs
(LibriSpeech + CommonVoice 13 + GigaSpeech-M) + a comparable Chinese set from WeNetSpeech. Emotion
stage: ~**70k** utts from IEMOCAP + MELD + CMU-MOSEI + MEAD + ESD (EN+ZH), collapsed to **5 classes:
neutral, happy, sad, angry, surprise**. In-domain test = IEMOCAP S5 + MELD-test; OOD = RAVDESS +
MerBench; zero-shot cross-lingual = AESDD (Gr), CaFE (Fr), RESD (Ru). ✔

**Key results (all Acc%, corroborated ✔):**
- **Table 1 (standalone SER).** BLSP-Emo tops the board overall: **IEMOCAP 76.0 · MELD 57.3 ·
  RAVDESS 72.0** (MerBench t1/t2 60.0/54.7). Encoder classifiers: **WavLM-Large 68.9/54.6/70.3**,
  **HuBERT-Large 64.6/53.2/70.5**, **wav2vec2-Large 69.3/54.8/64.0**. **SALMONN-7B** (a rival ALM)
  is far worse: 67.0/32.9/38.8. Text-only baselines are the tell: **Text+LLM RAVDESS = 11.1%**,
  **Whisper(ASR)+LLM RAVDESS = 13.7%**, yet Text/Whisper+LLM are *comparable-or-better on MELD*
  (54.0/53.8) — i.e. text is informative on conversational TV content but near-useless on
  acted/fixed-sentence content.
- **Table 2 (SpeechAlpaca, synthetic TTS instructions).** BLSP-Emo SER **83.8%**, GPT-4 quality
  **8.8**, empathy **7.7**; BLSP-SER (fine-tuned to predict the label directly) collapses on
  response quality (1.9/2.1) — proving the *continuation* objective, not label prediction, preserves
  instruction-following. ✔
- **Table 3 (zero-shot cross-lingual).** BLSP-Emo avg **63.4** (AESDD 68.8 / CaFE 75.3 / RESD 46.2),
  best overall; emotion knowledge transfers to unseen languages. ✔
- **Table 4 (ablation).** Remove semantic-alignment pretraining → IEMOCAP **76.0→68.5**, quality
  **8.8→6.7** (semantic-first is essential). Remove the auxiliary SER loss → IEMOCAP **76.0→72.2**,
  RAVDESS **72.0→66.6** (aux SER helps *natural-speech* SER, no effect on the synthetic
  SpeechAlpaca). ✔
- **Table 5.** Constructing continuations with the **same internal LLM** beats using ChatGPT
  (BLSP-ChatGPT worse on every metric), and **emotion-aware continuation** beats a naive
  **continuation+SER multi-task** framing (BLSP-MultiTask worse across the board). ✔

### Parts directly useful for ViEmoSpeech (tagged by Decision ID)

1. **[V-A] The staged "semantic-first, emotion-second" curriculum — as a *schedule* concept, not an
   architecture.** BLSP-Emo's headline ablation (Table 4: w/o semantic pretraining, IEMOCAP
   76.0→68.5, quality 8.8→6.7 ✔) says paralinguistic-emotion alignment only works *after* the model
   is semantically grounded. This is the same ordering signal as bimodal-05 (task-alternating > naive
   joint) and C²SER (bimodal-01). **Transfer risk: HIGH on the architecture, LOW on the ordering.**
   BLSP-Emo achieves "fusion" by *unfreezing and fine-tuning a 7B LLM + the whole Whisper encoder*
   with PLoRA — the polar opposite of ViEmoSpeech's frozen-backbone + small learned-fusion
   constraint. So it is an **ALM existence proof (like C²SER), not a copyable fusion template** (that
   role belongs to FAS/CASE vn-07 and EAA bimodal-03). What *does* transfer: a two-phase training
   plan — (a) align/warm the PhoBERT-over-PhoWhisper text branch on our transcripts first, (b) then
   train the audio↔text fusion for emotion — rather than one cold joint objective.

2. **[V-C] Auxiliary categorical SER head on top of the primary objective improves natural-speech
   SER.** Table 4 w/o-SER row: IEMOCAP 76.0→72.2 and RAVDESS 72.0→66.6 ✔ when the aux classification
   loss (Eq. 3) is removed. **Transfer risk: LOW/MEDIUM** — this is a generic multi-objective
   regularizer that survives register change (it helped *natural* speech, not the synthetic set).
   Concretely: keep an **auxiliary audio-only (or text-only) categorical emotion head alongside the
   fused head** in our model, exactly the audio-anchoring safeguard vn-12 argued for.

3. **[V-C] Text-channel-on-acted-content evidence: Text/Whisper+LLM = 11.1% / 13.7% on RAVDESS but
   ≈54% on MELD (Table 1 ✔).** **Transfer risk: LOW — this is the most ViEmoSpeech-relevant number
   in the paper.** RAVDESS is *acted, fixed carrier sentences* (semantically emotion-neutral) — the
   text channel carries essentially nothing (near-chance). MELD is *conversational TV dialogue* —
   text is informative. ViEmoSpeech is cut from **acted VN TV drama**, whose scripted lines sit
   between these poles but lean toward the acted/low-text-signal regime for many turns. This says our
   PhoBERT-over-PhoWhisper branch **cannot be assumed to carry emotion the way conversational-corpus
   results suggest**, and quantifies the register-dependence the cross-cutting synthesis already
   flagged.

4. **[V-B] Frozen-vs-fine-tuned encoder anchors.** WavLM-Large **70.3** / HuBERT-Large **70.5** /
   wav2vec2-Large **64.0** on RAVDESS; WavLM **68.9** / wav2vec2 **69.3** / HuBERT **64.6** on
   IEMOCAP (Table 1 ✔). Whisper-large-v2 encoder, once **emotion-fine-tuned** inside BLSP-Emo,
   reaches 72.0 RAVDESS / 76.0 IEMOCAP — i.e. a Whisper encoder is a viable SER backbone, but *only
   after fine-tuning*. **Transfer risk: MEDIUM** — every encoder number here is from a *fine-tuned*
   encoder + pooling + linear head, so these are NOT frozen-backbone bars; they tell us WavLM ≈
   HuBERT ≥ wav2vec2 and that Whisper-encoder is defensible, but they don't settle our frozen-vs-FT
   question. Keep the WavLM frozen arm as default (consistent with bimodal-12) and treat
   Whisper-encoder as an ASR-adjacent alternative worth an A/B, noting PhoWhisper is already in the
   pipeline for ASR.

### How each part helps ViEmoSpeech succeed

- **V-A → training-schedule ADR, not a model swap.** Write the fusion experiment as two phases:
  Phase-1 warm-start the text branch (PhoBERT fine-tune on our ASR transcripts + emotion labels),
  Phase-2 train the audio↔text fusion head with the backbone frozen. Cite BLSP-Emo Table 4 as
  evidence that emotion alignment on a *semantically-cold* model underperforms — the paralinguistic
  signal needs a grounded semantic scaffold first. Do **not** cite BLSP-Emo as a fusion architecture;
  our positioning line: "unlike generative ALMs (BLSP-Emo, C²SER) that fine-tune a multi-B-param LLM,
  we keep the backbone frozen and learn a small fusion module."
- **V-C → concrete head config.** Add an auxiliary audio-only 7-class emotion head (small linear on
  pooled WavLM features) trained jointly with the fused head; use BLSP-Emo's Eq. 3 + Table-4
  ablation as the precedent that this aux head lifts *natural-speech* SER. This also operationalizes
  the vn-12 "modality-dropout / audio-anchoring" safeguard against text-collapse.
- **V-C → the acted-content stress test.** Build an explicit eval slice of *low-lexical-content*
  turns (short exclamations, emotion-neutral carrier lines) and report audio-only vs text-only vs
  fused there. BLSP-Emo's RAVDESS 11.1% text-only is the citation that on such turns the text branch
  is at chance — so the fusion's job on those turns is to *not* be dragged toward text.
- **V-B → keep the ladder honest.** Put WavLM-Large (frozen) as the default audio arm; record
  BLSP-Emo's fine-tuned encoder numbers as an upper-bound reference (fine-tuned, not frozen) so we
  don't mistake a 70% fine-tuned RAVDESS bar for a frozen-probe target. Add a Whisper-encoder A/B
  since PhoWhisper is already loaded for ASR.

### Child mental-health / ViEmoSpeech transfer-risk lens

- **This is an ALM, so it is an *existence proof*, not a build target — same verdict as C²SER
  (bimodal-01).** BLSP-Emo fine-tunes Whisper-large-v2 + Qwen-7B-Chat (PLoRA) on ~1.9M ASR + 70k SER
  utts across 4× A100 (2.5 days + 3 h). ViEmoSpeech's constraint is a *frozen* backbone + small
  fusion on ~18k VN utts. We can borrow its *findings* (semantic-first ordering, aux-SER benefit,
  same-LLM data construction) but not its recipe.
- **Register match is partial and favorable-to-cite.** BLSP-Emo trains/tests heavily on **acted**
  corpora (IEMOCAP, RAVDESS, MEAD, ESD all "Act" in Table 6) — the same acted regime as VN TV drama.
  Its honest acted numbers (IEMOCAP 76, RAVDESS 72, *with a fine-tuned 7B ALM*) sit far below the
  leaky VN baselines (vn-08 86.6, vn-10 0.87) and are a useful sanity anchor for what acted 5-class
  SER actually costs.
- **"Empathetic response" framing ≠ our task.** Their downstream is *generating* empathetic text
  (SpeechAlpaca quality/empathy 8.8/7.7 via GPT-4 judge). ViEmoSpeech does *labeling* (7-class + V/A
  + distress), no generation, no child-directed dialogue. Their empathy metric is a GPT-4 preference
  on synthetic TTS — no clinical or child-safety grounding; do not import it. Our distress head stays
  an acted-drama proxy with a recall floor (V-F), untouched by this paper.
- **Language transfer is encouraging but shallow.** Zero-shot to Greek/French/Russian (Table 3, avg
  63.4 ✔) shows emotion cues learned in EN+ZH transfer to unseen languages — mild positive signal
  that a Vietnamese emotion signal is learnable — but none of their languages is tonal in the lexical
  sense, and they never probe tone, so this says nothing about the tone×emotion channel competition
  that is our novelty.

### Limitations & open questions for ViEmoSpeech (incl. explicit contradictions/gaps)

- **CONTRADICTION vs ViEmoSpeech's core constraint (frozen backbone).** BLSP-Emo's entire "emotion
  understanding" gain comes from *unfreezing* the encoder and LLM in stage 2 (§2.3). If the frozen
  audio channel proves too weak on our acted VN clips, this paper is the reminder that the field's
  strongest empathetic ALMs bought their paralinguistic sensitivity by fine-tuning — a lever we have
  deliberately foreclosed. Mitigation to test: a lightweight partial-unfreeze (top encoder layers
  only) A/B, budgeted but bounded.
- **CONTRADICTION / triangulation on text dominance.** BLSP-Emo's Text+LLM **RAVDESS 11.1%** (Table
  1 ✔) directly contradicts vn-12's "semantics dominate" claim and corroborates vn-08's "text
  near-useless on VN acted (38–44%)" and bimodal-01's "text collapses on acted tonal (13.93)". The
  reconciliation stands: text-reliance is **register-dependent** — high on conversational content
  (MELD ≈54%), near-chance on acted fixed-sentence content (RAVDESS 11.1%). Our hook must be the
  *measurable acoustic-channel* claim (tone×emotion in F0/phonation, vn-06/vn-13), not a blanket
  "text carries more load."
- **CROSS-REFERENCE anchor with EAA (bimodal-03).** EAA reports **MELD 0.687** for its dual
  cross-attention audio↔audio fusion (HuBERT+BEATs) vs BLSP-Emo's **0.573** (Table 1 ✔, = the 0.573
  EAA cites). A specialized sub-billion-param bimodal fusion **beats a 7B generative ALM by ~11 pts
  on MELD SER** — direct evidence for ViEmoSpeech's bet that a small learned fusion can out-classify
  a giant ALM on the discriminative SER task. (Caveat: not identical train sets, so treat as
  directional, not head-to-head.)
- **GAP — "tone" named, lexical tone untouched (Nth paper in the set).** The Limitations section
  lists "other types of paralinguistic cues in human speech, such as tones and intentions … not
  addressed" — but "tones" here means intonation/prosody, not **lexical tone**. Like CASE, C²SER,
  MDAT, THAI-SER before it, BLSP-Emo uses/mentions "tone" without ever treating lexical tone as a
  variable. V-D novelty remains fully intact and is now triangulated from another angle.
- **Open question for our aux-head design.** BLSP-Emo shows *label-prediction fine-tuning alone*
  (BLSP-SER) destroys downstream behavior (Table 2: quality 1.9) while an *auxiliary* SER loss on top
  of a generative objective helps (Table 4). We have no generative objective, so the destructive
  failure mode doesn't apply — but it is a caution that a categorical SER objective can dominate/warp
  a shared representation. Test our aux categorical head at low loss weight and watch the V/A-CCC and
  distress-recall heads for degradation.
