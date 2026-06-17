# Paper 25 — emotion2vec: Self-Supervised Pre-Training for Speech Emotion Representation

## 1. Bibliographic info

**Title:** emotion2vec: Self-Supervised Pre-Training for Speech Emotion Representation

**Authors:** Ziyang Ma (Shanghai Jiao Tong University, corresponding), Zhisheng Zheng (SJTU), Jiaxin Ye (Fudan University), Jinchao Li (The Chinese University of Hong Kong), Zhifu Gao (Alibaba), Shiliang Zhang (Alibaba), Xie Chen (SJTU).

**Affiliations:** Shanghai Jiao Tong University; Fudan University; The Chinese University of Hong Kong; Alibaba.

**Year / venue:** Findings of the Association for Computational Linguistics: ACL 2024, pages 15747–15760, August 11–16, 2024.

**Code/checkpoints:** https://github.com/ddlBoJack/emotion2vec (code, checkpoints, and extracted features).

**One-line thesis:** A *universal* speech-emotion representation backbone — pre-trained with self-supervised online distillation on 262 hours of emotion audio — that, with only a frozen encoder + linear probe, beats general SSL models (HuBERT/WavLM/data2vec) and SER specialists on IEMOCAP and across 10 languages.

## 2. Problem motivation

Speech-emotion tasks (SER, sentiment analysis) historically use FBank/MFCC features (semantically poor) or features from general speech SSL models (wav2vec 2.0, HuBERT, WavLM). The latter are strong but "not entirely suitable for emotional tasks" — they were pre-trained for phonetic/ASR content, not affect. Two ad-hoc fixes exist: (a) fine-tune a general SSL model on each emotion dataset (expensive; conclusions are data-/model-specific), or (b) distill a single SER model (e.g. Vesper, distilled from WavLM-large) whose *universal* representation capability is unproven. The paper argues the field needs a single, frozen, *universal* emotion representation that works out-of-the-box across many emotion tasks and languages — the speech-emotion analogue of a text emotion embedding. emotion2vec fills that gap.

## 3. Position in the literature

Two SSL families are distinguished by their self-supervised target type. **Offline targets** require a pre-trained teacher before pre-training: HuBERT and WavLM (K-means targets), PBERT/MonoBERT/PolyBERT (phoneme targets). **Online targets** update the teacher *during* pre-training via online distillation: data2vec / data2vec 2.0 (frame-level MLM loss) and CA-DINO (utterance-level cross-entropy). emotion2vec belongs to the online-distillation family and is distinctive in **combining utterance-level loss AND frame-level loss** — its claimed novelty is that global (whole-utterance) and local (frame) information both carry emotion, so both pretext tasks are needed. On the representation side, prior speech-emotion work either uses frozen general SSL features directly or fine-tunes them per-task; emotion2vec is positioned as the first *universal speech emotion* representation model, analogous to text emotion embeddings (Emo2Vec, etc.).

## 4. Method deep dive

### 4.1 Pipeline (teacher–student online distillation)

Two networks share architecture: a **teacher T** and **student S**, each = feature extractor F (7-layer 1-D CNN) + backbone B (multi-layer Transformer). Both are initialized from the **same pre-trained weights** (data2vec or data2vec 2.0). Given raw audio X:
- Teacher: downsampled features Z0ᵀ = Fᵀ(X) fed directly to Bᵀ.
- Student: Z0ˢ = Fˢ(X), then **masked** (l = 5 consecutive frames, each frame a mask-start with probability p = 0.5), with a learnable **utterance embedding U** prepended before the backbone Bˢ.
- The teacher target Yᵀ is the **average of the top k = 8 Transformer blocks**' outputs.
- Outputs: student utterance-level embedding Uˢ and frame-level embedding Yˢ.

### 4.2 Utterance-level loss (global emotion)

MSE between the temporally-pooled teacher frame output and the temporally-pooled student utterance output:

`L_Utt = (mean(Yᵀ) − mean(Uˢ))²`   (Eq. 6–8)

Three variants to compute it (Fig. 2): **Token** (single utterance token, Nu = 1), **Chunk** (multiple utterance tokens — aggregates more global info), **Global** (no extra tokens; temporal-pool the frame output Yˢ). Ablation picks **Chunk** as best.

### 4.3 Frame-level loss (contextual emotion)

MSE on the **masked frames only** (standard MLM pretext): `L_Frm = (1/M) Σ_{i∈M} (Yᵢᵀ − Yᵢˢ)²`  (Eq. 9).

### 4.4 Online distillation objective

Total student loss: **L = L_Frm + α · L_Utt** (Eq. 10), with α tunable. Student updates by backprop; **teacher updates by EMA** of the student: `θᵀ_{t+1} = τ·θᵀ_t + (1−τ)·θˢ_{t+1}` (Eq. 11), where τ **increases linearly from 0.999 → 0.99999** over pre-training. In practice the teacher's feature extractor Fᵀ is *copied directly* from Fˢ each step; only the backbone Bᵀ is EMA-updated. No external/frozen teacher is needed — the teacher *is* a slow-moving copy of the student (BYOL/data2vec-style bootstrap).

### 4.5 Initialization, hyperparameters, training overhead

- **Initial models:** data2vec or data2vec 2.0 (both pre-trained on LibriSpeech 960h). Same 7-layer 1-D CNN feature extractor: kernels (5,2,2,2,2,2,2), strides (10,3,3,3,3,2,2) → **320× downsampling**; 16 kHz raw audio → 50 Hz / 512-dim features; linear projection 512→768 before masking. Backbone = 12-layer Transformer, 768 model dim, 3072 FFN, 12 heads (data2vec 2.0 adds a 4-layer CNN decoder, MAE-style, encoding only unmasked frames for efficiency).
- **Pre-training:** 262 hours of unlabeled emotion data; 4× NVIDIA A10 GPUs simulating 16 GPUs (update frequency 4); **100 epochs**, ~37 min/epoch; dynamic batch, max 1×10⁶ tokens; Adam, LR 7.5×10⁻⁵, weight decay 1×10⁻², cosine schedule with 5% linear warm-up; α = 1; teacher EMA τ 0.999→0.99999.
- **Downstream:** the pre-trained emotion2vec is **frozen**; only a lightweight head is trained. Non-sequential tasks use the SUPERB recipe (two linear layers with a ReLU between, hidden dim 256). Sequential tasks use a 2-layer GRU.

## 5. Datasets

**Pre-training corpus (262 h total, all English; Table 1 / Appendix B.1):** IEMOCAP (7.0 h), MELD (12.2 h), CMU-MOSEI (91.9 h), MEAD (37.3 h), MSP-Podcast v1.8 (113.5 h) → 169,053 utterances. (Note: these five overlap with downstream English benchmarks; out-of-domain generalization is shown on held-out languages/datasets.)

**Downstream / evaluation (18 emotional datasets in total, 10 languages):** IEMOCAP, MELD, RAVDESS-Speech, RAVDESS-Song, SAVEE, CMU-MOSI, CMU-MOSEI (English); M3ED (Mandarin), SUBESCO (Bangla), CaFE (French), EmoDB (German), AESDD (Greek), EMOVO (Italian), ShEMO (Persian), RESD (Russian), URDU (Urdu). RAVDESS and SAVEE are **out-of-domain** (not seen in pre-training); the 9 non-English sets are out-of-domain languages.

## 6. Results

### 6.1 IEMOCAP main result — linear probe vs SSL backbones (Table 2)

SUPERB protocol: freeze upstream, train linear head (downstream hidden dim 256). IEMOCAP merges `excited`+`happy` → 4 classes. WA = weighted accuracy (overall), UA = unweighted (class-averaged), WF1 = weighted-F1. Reported WA (%):

| Model | Pre-train corpus | #Upstream params | Downstream | WA(%) |
|---|---|---|---|---|
| wav2vec 2.0 base | LS-960 | 95.04M | Linear | 63.43 |
| HuBERT base | LS-960 | 94.68M | Linear | 64.92 |
| WavLM base | LS-960 | 94.70M | Linear | 65.94 |
| WavLM base+ | Mix-94k | 94.70M | Linear | 67.98 |
| data2vec base | LS-960 | 93.75M | Linear | 67.38 |
| data2vec 2.0 base | LS-960 | 93.78M | Linear | 68.58 |
| Vesper-4 | Mix-94k + LSSED-206 | 63.52M | Linear | 68.40 |
| Vesper-12 | Mix-94k + LSSED-206 | 164.29M | Linear | 70.70 |
| **emotion2vec** | LS-960 + Emo-262 | **93.79M** | Linear | **71.79** |
| **emotion2vec\*** | LS-960 + Emo-262 | 93.79M | Linear | **74.48** (leave-one-speaker-out, same-fold val/test) |
| wav2vec 2.0 large | LL-60k | 317.38M | Linear | 65.64 |
| HuBERT large | LL-60k | 316.61M | Linear | 67.62 |
| WavLM large | Mix-94k | 316.62M | Linear | 70.03 |
| TIM-Net (specialist, MFCC) | – | – | CNN (0.40M) | 68.29 |
| MSTR (specialist) | – | HuBERT-large | Transformer (27.0M) | 70.03 |
| DST (specialist) | – | WavLM-large | Transformer (22.78M) | 71.80 |

Headline: at ~93.79M upstream params + a **0.20M linear head**, emotion2vec (WA 71.79; 74.48 under the speaker-independent same-fold protocol) **beats every base and large general SSL model**, beats Vesper-12 (the WavLM-large-distilled SER specialist, 164.29M) with fewer params, and matches/exceeds SER specialists whose downstream nets are **2× (TIM-Net), 135× (MSTR), 114× (DST)** larger.

### 6.2 Other English datasets (Table 3, WA%)

| Model | MELD | RAVDESS | SAVEE |
|---|---|---|---|
| WavLM-base | 46.95 | 37.01 | 42.08 |
| data2vec 2.0 | 48.92 | 81.04 | 83.13 |
| **emotion2vec** | **51.88** | **82.43** | **84.38** |

(emotion2vec WF1: MELD 48.70, RAVDESS 82.86, SAVEE 84.45. RAVDESS/SAVEE are out-of-domain.)

### 6.3 Language generalization (Table 4)

On all **9 out-of-domain non-English** datasets emotion2vec leads every SSL baseline on WA/UA/WF1, e.g. WA: AESDD-Gr 72.33, EmoDB-De 84.34, SUBESCO-Bn 90.91, CaFE-Fr 74.52, EMOVO-It 61.21, ShEMO-Fa 79.97, RESD-Ru 64.75, M3ED-Zh 49.15, URDU 81.50.

### 6.4 Task generalization

- **Song emotion recognition (RAVDESS-Song, Table 5):** frozen emotion2vec + Linear → WA 85.0 / UA 85.2 / WF1 84.8, beating all *frozen* SSL baselines and on par with *fine-tuned* VQ-MAE-S specialists.
- **Emotion prediction in conversation (IEMOCAP, Table 6):** swapping speech features for emotion2vec lifts UAR/MacroF1 in both speech-only (UAR 77.19 / MacroF1 76.71 vs Shi 2023's 65.01 / 65.91) and speech+text multimodal (UAR 81.68 / MacroF1 80.75). EPC uses a hierarchical GRU over the previous 6 dialogue turns.
- **Sentiment analysis (CMU-MOSI/MOSEI, Table 7):** binary (neutral removed), mean of last 4 layers + linear. emotion2vec WF1 65.41 / 74.75 (MOSI/MOSEI), beating base data2vec, WavLM, and supervised Whisper-Encoder.

### 6.5 Visualization (Fig. 3, 5)

UMAP of first-linear-layer features: WavLM and data2vec show heavy overlap between high/low-arousal classes; emotion2vec separates arousal cleanly with a smooth high→low transition, and (Fig. 5, SUBESCO) gives tighter intra-class / wider inter-class margins on discrete emotions.

## 7. Ablations (Appendix C, leave-one-session-out 5-fold on IEMOCAP)

- **Initialization (Table 8):** cold-start WA 61.34 → data2vec init 70.2 → **data2vec 2.0 init 71.79**. Warm-starting the online-distillation teacher/student from a pre-trained model is worth ~+10 WA over cold start.
- **Training loss (Table 9):** utterance-loss-only collapses (WA 28.96). Frame-loss-only already works (WA 70.85). **Frame + utterance** is best (WA 71.79). Concatenating utt+frame embeddings downstream ≈ frame-only.
- **Utterance-loss variant (Table 10):** Token 70.46 / **Chunk 71.79** / Global 70.30.
- **Loss weight α (Table 11):** α = 0 → 70.85; 0.1 → 71.06; **1 → 72.14**; 10 → 70.58. A 1:1 frame:utterance ratio is best.

## 8. Authors' stated limitations

(1) emotion2vec gives a universal representation but **still needs a separately-trained downstream model per task** — it is a feature extractor, not an end-to-end multi-task system. (2) **Whether speaker information is removed is unexplored** — important for emotional-TTS use of the representation (i.e., the embedding may still carry speaker identity).

## Deep research — full-PDF read (2026-06-16)

> Frame: Pebble's thesis includes a planned **voice-message modality** — a child sends an audio
> clip, Pebble must score affect from speech (not only text). emotion2vec is the strongest candidate
> for a **drop-in, frozen, emotion-specialist SSL backbone for English speech** that feeds Pebble's
> emotion/severity heads on the audio side, exactly mirroring how NeoBERT serves the text side.
> This section reads against the **published ACL Findings 2024 camera-ready** (aclanthology.org/2024.findings-acl.931,
> pp. 15747–15760). The local PDF `pdfs/25-emotion2vec.pdf` carries the ACL 2024 page footer and
> page numbers, i.e. it *is* the camera-ready, so it is authoritative; the GitHub README is used as a
> second source for model size / language scope.

### Source-access note

- **Read:** full PDF extracted with `pdftotext "pdfs/25-emotion2vec.pdf" -` (1207 lines, ~52 KB);
  every table (2–11), the methods/equations, and Appendices A–D read end-to-end.
- **Web-validated:**
  - Venue, page range, abstract, "10 languages" claim — `aclanthology.org/2024.findings-acl.931/`
    (query: *"emotion2vec Self-Supervised Pre-Training for Speech Emotion Representation ACL Findings
    2024 IEMOCAP WA 262 hours"*). **✔ corroborated** (venue = Findings of ACL 2024, pp. 15747–15760;
    abstract confirms "10 different languages").
  - Model size (~90M base / ~300M large) + multilingual scope — `github.com/ddlBoJack/emotion2vec/blob/main/README.md`.
    **✔ corroborated** (base ~90M matches the paper's 93.79M; README also documents later
    emotion2vec+ seed/base/large variants fine-tuned on 201/4788/42526 h — *not in the paper*).
- **Conflict rule:** no preprint disagreement found; the local PDF = camera-ready, numbers used as-is.
- All numbers below carry their Table/Eq./§ ref and a status tag (✔ corroborated against venue
  metadata where the venue exposes it; ≈ in-PDF-only camera-ready number, internally consistent,
  not independently re-derivable from a second public source).

### What the paper actually does (validated numbers)

- **Pre-training data: 262 hours** of unlabeled English emotion audio (IEMOCAP 7.0 + MELD 12.2 +
  CMU-MOSEI 91.9 + MEAD 37.3 + MSP-Podcast 113.5 = 169,053 utts) — Table 1 / Appendix B.1. **≈** (in-PDF; abstract says only "open-source unlabeled emotion data").
- **Objective: online self-distillation, `L = L_Frm + α·L_Utt`** (Eq. 10), teacher = **EMA of student**,
  τ linearly **0.999→0.99999** (Eq. 11); teacher target = mean of top **k=8** Transformer blocks; mask
  l=5 frames, p=0.5; **α=1** best (Table 11). **≈** (in-PDF, ablation-supported).
- **Model size: 93.79M** upstream params (base, 12-layer Transformer, 768-dim), downstream head
  **0.20M** (two linear + ReLU) — Table 2. Base ~90M **✔** corroborated by GitHub README.
- **# benchmarks: 18 emotional datasets, 10 languages** (9 English + Mandarin/Bangla/French/German/
  Greek/Italian/Persian/Russian/Urdu); "13 datasets" used in the multilingual SER sweep — Table 1, §1.
  "10 languages" **✔** corroborated (abstract).
- **IEMOCAP linear-probe WA: 71.79%** (leave-one-session-out 5-fold) / **74.48%** (emotion2vec\*,
  leave-one-speaker-out, same-fold val/test) — Table 2. vs HuBERT-base **64.92**, WavLM-base **65.94**,
  WavLM-base+ **67.98**, data2vec-2.0-base **68.58**, WavLM-**large** **70.03**, Vesper-12 (WavLM-large
  distilled, 164.29M) **70.70**. **≈** (in-PDF; representative SSL deltas are large and consistent
  across Tables 2–4).
- **Beats SER specialists with 2×/135×/114× smaller downstream nets** (TIM-Net 68.29 / MSTR 70.03 /
  DST 71.80 vs emotion2vec 71.79 with a 0.20M head) — Table 2. **≈**.
- **Warm-start matters: +10.45 WA** (cold-start 61.34 → data2vec-2.0 init 71.79) — Table 8. **≈**.
- **Both losses needed:** utt-only collapses (WA 28.96); frame-only 70.85; frame+utt 71.79 — Table 9. **≈**.

### Parts directly useful for Pebble (each tagged with Decision IDs)

1. **Frozen-encoder + linear-probe = the cheapest competitive SER recipe** — emotion2vec frozen +
   a **0.20M** linear head beats fully-fine-tuned/large SSL backbones (Table 2). **[D-A, D-E]** This is
   the audio-side mirror of Pebble's text plan: a frozen specialist backbone with light task heads,
   no expensive full fine-tune.
2. **emotion2vec is a drop-in audio backbone for the voice-message modality** — pre-trained,
   checkpoint public, English-strong, frozen-feature interface (768-dim). **[D-A, D-H]** It is the
   speech analogue of choosing NeoBERT over fine-tuning a generic encoder: pick the *emotion-specialist*
   SSL model, not a generic ASR SSL model (HuBERT/WavLM), for affect.
3. **Severity ≈ arousal, and emotion2vec separates arousal cleanly** (Fig. 3 UMAP; high/low-arousal
   clusters, smooth transition) — directly relevant to Pebble's **severity regression head**.
   **[D-D]** The continuous arousal manifold is a transfer source for a speech-side intensity signal,
   the audio counterpart of the WASSA/SemEval intensity transfer used on text.
4. **Online self-distillation with a frame-MLM + utterance loss, warm-started from a pre-trained
   checkpoint** (Eq. 10–11; Table 8 +10 WA from warm start). **[D-E, D-F]** Independent evidence that
   (a) warm-starting an SSL objective from an existing checkpoint beats cold start by a large margin,
   and (b) a masked/MLM-style pretext is the load-bearing loss (frame-only already at 70.85; utt-only
   collapses) — both reinforce Pebble's domain-adaptive-MLM (D-F) and staged warm-start (D-E) plans on
   the text side.
5. **Loss-balancing ablation = static 1:1 wins** (α: 0→70.85, 0.1→71.06, 1→72.14, 10→70.58; Table 11).
   **[D-B]** A clean, in-domain data point that a simple static loss weight (here 1:1) can beat both
   under- and over-weighting — relevant ammunition for Pebble's "start with static λ before reaching
   for Kendall/GradNorm" position on MTL balancing.
6. **Multilingual generalization from English-centric pre-training** — frozen English-trained
   emotion2vec leads all SSL baselines on 9 non-English SER sets (Table 4). **[D-H]** Evidence that an
   emotion SSL backbone transfers across language with only a re-trained linear head — useful if Pebble
   ever extends the voice modality beyond English.

### How each part helps Pebble succeed (concrete actions)

- **Voice-message head wiring [D-A/D-E].** Add an `audio/` path: `emotion2vec (frozen) → mean/last-4-layer
  768-dim features → {emotion 12-label head, severity regression head}`, exactly the SUPERB recipe
  (two linear + ReLU, hidden 256). Do **not** fine-tune the backbone in v1 — Table 2 shows the frozen
  probe already beats fine-tuned baselines, so this is both cheaper and a stronger baseline. Mirror the
  NeoBERT head shapes so the Decision Engine sees the same output contract from text and audio.
- **Severity from arousal [D-D].** Train the audio severity head as a regression onto an arousal/intensity
  target; emotion2vec's clean arousal manifold (Fig. 3) is the reason a *linear* severity probe is
  plausible. Report Pearson (Pebble's chosen severity metric) on a held-out child-voice slice, the audio
  analogue of the text WASSA-intensity transfer.
- **Warm-start + MLM evidence [D-E/D-F].** Cite Table 8 (+10 WA cold→warm) and Table 9 (frame-MLM is the
  load-bearing loss) as cross-modal corroboration for Pebble's text-side domain-adaptive MLM pass and
  gradual-unfreeze/warm-start staging — "an SSL warm start + MLM pretext is worth ~10 points" is a
  transferable prior even though the modality differs.
- **MTL λ default [D-B].** Use Table 11 as a reason to *start* Pebble's emotion+severity MTL with a
  static 1:1 (or single tuned λ) and only escalate to LibMTL methods if a held-out head regresses —
  emotion2vec found static 1:1 optimal among {0, 0.1, 1, 10}.
- **Backbone-selection argument [D-A].** When justifying NeoBERT-over-generic on text, cite emotion2vec
  as the parallel audio result: an *emotion-specialist* SSL backbone beats general SSL (HuBERT/WavLM)
  and even larger models on affect, with a tiny head. The "specialist beats generalist at small head
  budget" thesis is symmetric across modalities.

### Child mental-health lens (transfer validity, risks, mitigations, ethics)

- **Adult/acted-speech provenance — transfer risk is HIGH.** The 262 h pre-training mix is adult speech:
  IEMOCAP/MEAD/SAVEE/RAVDESS are **acted** emotion by adult actors; MSP-Podcast/CMU-MOSEI are adult
  podcast/YouTube; MELD is adult TV (*Friends*). **No child speech anywhere.** Children's voices differ
  in pitch (much higher f0), formant structure, prosody, and emotional expression. A frozen
  English-adult-acted-emotion backbone may mis-represent child affect. **Mitigation:** treat emotion2vec
  as a *feature extractor only* and validate the *probe* on a held-out child-voice slice before any
  deployment claim; budget for a small child-voice calibration set; consider light domain-adaptive
  continued distillation on child audio if a calibration gap appears (the warm-start result, Table 8,
  says this is high-leverage).
- **Acted vs spontaneous distress.** The strongest numbers (RAVDESS/SAVEE WA 82–84) are on *acted*
  prototypical emotion; real child distress is spontaneous, indirect, often low-arousal/withdrawn. The
  MELD result (noisy, spontaneous TV) is much lower (WA 51.88) — a more honest proxy for in-the-wild
  difficulty. Pebble should anchor expectations to the MELD-style number, not the acted-dataset ceiling.
- **Arousal ≠ severity for children.** emotion2vec separates *arousal*; but a quiet, flat, withdrawn
  child can be high-severity at low arousal. The severity head must not equate "high arousal" with "high
  risk" — the audio severity signal is a *contributor*, not a decision, feeding the same human-escalation
  invariant Pebble already enforces on text.
- **Speaker-identity leakage (authors' own limitation).** The paper says it never checked whether speaker
  info is removed from the representation. For a **child-facing** product this is a privacy red flag:
  emotion2vec features may carry voiceprint/identity. **Mitigation:** never persist raw audio or raw
  embeddings tied to a child; score on-device/ephemerally where possible; document this in the data-handling
  section.
- **No safety/clinical claim.** emotion2vec is SER/sentiment, not risk detection. It can inform Pebble's
  *emotion* and *severity* heads but supplies **no learned safety signal** — consistent with Pebble v1's
  no-learned-safety-head decision; the audio side likewise routes through heuristics + the Decision Engine,
  not a learned safety classifier.

### Limitations & open questions for Pebble

- **Contradiction-or-gap vs Pebble's text-first, turn-level plan.** emotion2vec operates on whole
  *utterances* (utterance-level loss is half the objective) and is benchmarked utterance/clip-level; Pebble
  scores **turn-level, mid-conversation**. A voice message is naturally one utterance, so utterance-level
  is fine for the audio modality — *but* the text side and audio side then operate at different granularities
  (text = turn within a streaming conversation; audio = whole clip). Pebble must define how an
  utterance-level audio score fuses with turn-level text scores in the Decision Engine; emotion2vec gives
  no guidance on cross-modal temporal alignment. **Gap.**
- **Gap vs the rest of the corpus: this is the only speech paper.** Every other Pebble reference paper
  (FAIIR, C-SSRS, MentalBERT, WASSA, GoEmotions) is **text**. emotion2vec cannot be compared on the same
  bars (52% acc / 0.75 wF1 / 47.8% macro-recall for C-SSRS are text-severity bars; emotion2vec's IEMOCAP
  WA 71.79 is 4-class acted SER). The two modalities share *no* common benchmark — Pebble must build its
  own joint child-voice+text eval, or keep the modalities' metrics strictly separate.
- **Pre-training overlaps downstream.** Four of the five pre-training sets (IEMOCAP, MELD, CMU-MOSEI,
  MEAD) are also evaluated downstream; the cleanest out-of-domain evidence is RAVDESS/SAVEE and the 9
  languages. Pebble should weight the OOD numbers (and especially noisy-spontaneous MELD) when estimating
  real-world child-voice performance, not the in-domain headline.
- **emotion2vec+ exists but is undocumented in the paper.** The GitHub README adds emotion2vec+
  seed/base/large fine-tuned on 201/4788/42526 h — potentially stronger backbones, but with no peer-reviewed
  numbers. Open question: which checkpoint Pebble should adopt for the voice modality (paper-grade base vs
  the larger emotion2vec+ released later); needs an empirical bake-off on Pebble's own child-voice slice.
- **No calibration / no probability outputs.** Like FAIIR on text, emotion2vec reports WA/UA/WF1 with no
  calibration (ECE/reliability). Pebble's Decision Engine consumes scores, so the audio severity/emotion
  probes will need their own calibration step (D-G), which emotion2vec does not provide.
- **Speaker-info ablation never run** — the authors flag it; for a child product this is the first thing
  Pebble must measure before shipping audio.
