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

> **Frame for the voice thesis.** emotion2vec is the thesis's chosen **PRIMARY speech backbone**
> (WavLM-Large/MIT is the fallback). The thesis = "voice-first stress and crisis detection for
> emotional-support chat: a speech-encoder affect model with uncertainty-weighted heterogeneous heads
> (emotion softmax + continuous regression + high-recall safety/crisis BCE) under a HARD crisis-recall
> floor, LLM silver-label distillation, NeoBERT text fused in as support." This section reads the
> camera-ready end-to-end and pulls **exact, per-decision numbers** to settle the five open backbone
> decisions — it is not a summary. Every number carries a Table/§/line ref and a validation status.

### Source-access note

- **PDF read:** the project-local `docs/papers/voice/pdfs/25-emotion2vec.pdf` was **not present** at
  read time (`pdfs/` empty; `find … -iname "*emotion2vec*.pdf"` returned nothing). The deep read was
  therefore done against the **authoritative venue camera-ready**, fetched and converted locally:
  `aclanthology.org/2024.findings-acl.931.pdf` → `pdftotext` → 1,907 lines, all of Tables 2–11,
  every equation, and the Limitation section read end-to-end. This is the published ACL Findings 2024
  version (pp. 15747–15760), i.e. **the most authoritative source** — there is no preprint-vs-venue
  conflict to resolve because the read *is* the venue text.
- **Web-validated (queries + resolved URLs):**
  - Venue / page range / "10 languages" / abstract — query *"emotion2vec Self-Supervised Pre-Training
    Speech Emotion Representation ACL Findings 2024 IEMOCAP WA 71.79 linear probe"* →
    `https://aclanthology.org/2024.findings-acl.931/` and `https://dblp.org/rec/conf/acl/MaZYLGZ024.html`.
    **✔ corroborated** (Findings of ACL 2024, pp. 15747–15760; "10 different languages").
  - Table 8 init ablation (cold-start 61.34 → data2vec 70.2 → data2vec 2.0 71.79) — query
    *"emotion2vec Table 8 initialization cold start data2vec warm start IEMOCAP WA ablation"* → second
    public source confirms the exact triple. **✔ corroborated**.
  - Table 2/3/4 numbers, SUPERB head text, α ablation, Fig-3 arousal text, Limitation — read **directly
    off the venue PDF text** (`/tmp/e2v.txt` lines cited inline below). **✔ corroborated** (venue).
  - Weight **license** + emotion2vec+ variants — `github.com/ddlBoJack/emotion2vec/blob/main/README.md`:
    repo shows an **MIT badge but no explicit license on the checkpoints**; emotion2vec+ seed/base/large
    fine-tuned on **201 / 4,788 / 42,526 h** (base ~90M, large ~300M), **not in the paper**. License for
    deployment is therefore **⚠ ambiguous**, not corroborated-permissive.
- **Status tags:** ✔ corroborated against the venue text/metadata · ≈ venue-internal number (single
  source, internally consistent) · ✖ uncorroborated (none used).

### What the paper actually does (validated numbers)

- **Method = online SELF-distillation (EMA teacher), NOT LLM distillation.** Teacher T and student S
  share architecture and are **both warm-started from the same pre-trained checkpoint** (data2vec /
  data2vec 2.0, LS-960); student sees masked input (mask l=5, p=0.5) + a learnable utterance embedding;
  teacher target = mean of the **top k=8** Transformer blocks; the **teacher is an EMA copy of the
  student**, τ linearly **0.999 → 0.99999** (Eq. 11; venue lines 215, 349–351, 422). Loss
  `L = L_Frm + α·L_Utt`, **α=1 best** (Table 11). This is **data2vec/BYOL-style bootstrap**, no external
  teacher, no pseudo-labels. **✔ corroborated** (venue §3.4, lines 103–125, 349–351).
- **Pre-training data: 262 h** unlabeled adult English emotion audio (IEMOCAP 7.0 + MELD 12.2 +
  CMU-MOSEI 91.9 + MEAD 37.3 + MSP-Podcast 113.5 = 169,053 utts) — Table 1. **≈** (venue-internal;
  abstract only says "open-source unlabeled emotion data").
- **Backbone size: 93.79M** upstream (12-layer Transformer, 768-dim); downstream head **0.20M** — Table 2.
  Base ~90M **✔** corroborated (README).
- **IEMOCAP linear-probe WA (Table 2, venue lines 815–859):** emotion2vec **71.79** (leave-one-session-out
  5-fold) vs data2vec 2.0 base **68.58**, WavLM-base+ **67.98**, **WavLM-large 70.03**, HuBERT-large
  **67.62**, wav2vec2-large **65.64**, Vesper-12 (WavLM-large-distilled, 164.29M) **70.70**. Speaker-fold
  variants: emotion2vec\* **74.48** (leave-one-speaker-out, same-fold val/test) and a further **72.94 /
  77.64** pair. Beats SER specialists TIM-Net **68.29** / MSTR **70.03** / DST **71.80** whose heads are
  0.40M / 27.0M / 22.78M (2×–135× larger) with a **0.20M** head. **✔ corroborated** (venue).
- **Honest spontaneous-speech number (Table 3, venue lines 870–910):** **MELD WA 51.88** (WF1 48.70) —
  far below the **acted** RAVDESS **82.43** / SAVEE **84.38**. MELD is the realistic in-the-wild proxy.
  **✔ corroborated** (venue).
- **Cross-lingual (Table 4, venue lines 936–1000):** frozen English-pretrained emotion2vec leads all SSL
  baselines on the **9 non-English** sets — AESDD-Gr **72.33**, EmoDB-De **84.34**, SUBESCO-Bn **90.91**,
  CaFE-Fr **74.52**. **✔ corroborated** (venue). ("13 datasets … 10 languages", venue line 68.)
- **Warm-start delta (Table 8): +10.45 WA** (cold-start **61.34** → data2vec 2.0 init **71.79**).
  **✔ corroborated** (venue + 2nd source).
- **Both losses needed (Table 9):** utterance-loss-only **collapses to 28.96**; frame-loss-only already
  **70.85**; frame+utt **71.79**. **✔ corroborated** (venue lines 1776–1791).
- **α ablation (Table 11):** 0→**70.85**, 0.1→**71.06**, 1→**72.14**, 10→**70.58** — static 1:1 wins.
  **✔ corroborated** (venue lines 1790–1793).
- **The decisive gap: zero continuous regression.** Every benchmark in the paper is **categorical SER**
  (4–8 classes) or **binary** sentiment (CMU-MOSI/MOSEI). The word "arousal" appears **only** in the
  Fig. 3 UMAP caption ("arousal refers to emotional intensity … emotion2vec exhibits a trend
  transitioning from high arousal to low arousal", venue lines 1251, 1348–1354) — a **qualitative
  cluster picture, not a regression result**. No valence/arousal/dominance CCC, Pearson, or MSE anywhere.
  **✔ corroborated** (exhaustive grep of venue: no "regress"/"CCC"/"valence" as a target).

### The five open backbone decisions — exact numbers + recommendation

**Decision 1 — Backbone choice: emotion2vec as PRIMARY over WavLM-Large? → YES, but as a tunable
hypothesis, not a settled fact. [D-A, D-H]**
- Evidence FOR: under one common protocol (Table 2 SUPERB linear probe), emotion2vec **71.79** beats
  **WavLM-large 70.03** while being **~3.4× smaller** (93.79M vs 316.62M) and pretrained on **~360× less
  audio** (262 h emotion vs 94k h general). It also beats the WavLM-large-distilled specialist Vesper-12
  (70.70, 164.29M). Cross-lingual transfer holds on 9 languages (EmoDB-De 84.34, SUBESCO-Bn 90.91).
  Warm-start lift is large (+10.45 WA, Table 8).
- Evidence for a **realistic bar**: the acted ceilings (RAVDESS 82.43 / SAVEE 84.38) are **not** the
  number to promise; the spontaneous-speech number **MELD ~52 WA** is. Pebble's child-distress audio is
  spontaneous, so anchor expectations to ~50s, not ~80s.
- **Recommendation:** lead with emotion2vec as PRIMARY (best emotion features per parameter, smallest
  model, public checkpoint). **But the 71.79 vs 70.03 gap is +1.76 WA on adult acted/podcast data** —
  small enough that on child spontaneous speech it could vanish or reverse. Keep WavLM-Large (MIT, proven
  dimensional-regression recipe) as a **funded fallback arm**, and make "did the emotion specialist
  actually beat the strong generalist on child voice?" an explicit thesis experiment. Decision direction:
  **emotion2vec primary, WavLM-Large mandatory comparator** — do not retire the fallback.

**Decision 2 — Frozen vs fine-tune: FROZEN + small head is the validated, competitive recipe. [D-A, D-E]**
- Exact head (venue lines 427, 684, 1197): non-sequential tasks use the **SUPERB recipe = two linear
  layers with a ReLU sandwiched between them, hidden dim 256**, total **0.20M params**, on **frozen**
  768-dim emotion2vec features. Sequential/conversational tasks use **2-layer GRU**. Sentiment uses the
  **mean of the last four layers** of the frozen encoder as input (venue line 1302).
- Is frozen competitive? **Yes, decisively here:** the frozen 0.20M-head probe (71.79) **beats every
  fully-fine-tuned/larger general SSL backbone** in Table 2 and matches/beats specialists with 100×+
  larger heads. The paper never fine-tunes the backbone for its main results.
- **Recommendation:** for Pebble's audio v1, **freeze emotion2vec and train only the heads** (mirror the
  SUPERB shape: 768→256→head, ReLU). Use **mean-of-last-4-layers** as the default feature (paper's choice
  for the most "semantic" tasks) and ablate vs last-layer. Frozen is cheaper, lower-variance, and a
  stronger baseline — only escalate to PEFT/partial-FT if a held-out child-voice head underperforms.

**Decision 3 — Continuous regression head: NOT validated; this is the load-bearing GAP. [D-D]**
- emotion2vec is validated **only on categorical/binary** emotion. The **single** piece of
  arousal/continuous evidence is the **Fig. 3 UMAP** — qualitatively, emotion2vec separates high vs low
  arousal cleanly with a smooth high→low transition where WavLM/data2vec overlap (venue lines 1348–1354).
  There is **no Pearson/CCC/MSE arousal or severity number anywhere** in the paper.
- **Implication for Pebble's severity/arousal regression head:** the clean arousal manifold makes a
  **linear severity probe plausible**, but it is a hypothesis, not a measured result. The proven
  continuous-regression recipes in the corpus come from **WavLM/wav2vec2-robust** (Wagner TPAMI valence
  CCC 0.638; Odyssey-2024 dimensional baseline), **not** emotion2vec.
- **Recommendation:** **flag this gap explicitly in the thesis.** For the continuous severity/arousal
  head, (a) prototype a linear regression probe on frozen emotion2vec features and report **Pearson** on
  a held-out slice, but (b) **run WavLM-Large as the regression comparator from day one** since its
  dimensional CCC recipe is published. Do **not** assume emotion2vec's categorical SOTA transfers to
  regression — the only basis is one UMAP picture.

**Decision 4 — Distillation mechanism: SELF-distillation, must NOT be conflated with Pebble's Gemini
pipeline. [D-B, D-E/D-F clarification]**
- The "distillation" in emotion2vec is **online self-distillation**: an **EMA teacher** that is a
  slow-moving copy of the student (τ 0.999→0.99999, Eq. 11), data2vec/BYOL-style, **no external teacher,
  no labels** (venue §3.4). This is **orthogonal** to Pebble's **LLM silver-label distillation** (Gemini
  generates labels that supervise the heads). They live at different stages: emotion2vec's self-distill
  is **unsupervised representation pre-training**; Pebble's LLM distill is **supervised head training**.
- **Recommendation:** in related-work, file emotion2vec under "self-supervised backbone pre-training",
  and keep the Gemini→NeoBERT/audio pipeline as a **separate** "LLM-supervised head distillation" line
  (Dutta & Ganapathy is the correct analogue for *that*). Transferable prior from this paper for Pebble's
  **own** SSL choices: warm-starting an SSL objective beats cold start by **+10.45 WA** (Table 8) and a
  **masked/MLM pretext is the load-bearing loss** (frame-only 70.85 vs utt-only collapse 28.96, Table 9)
  — cross-modal support for Pebble's text-side domain-adaptive-MLM (D-F) and warm-start (D-E). Bonus
  MTL data point: static **1:1** loss weight beats up/down-weighting (Table 11) → start MTL with static λ
  before LibMTL (D-B).

**Decision 5 — Risks for a child-facing product: four hard blockers, all must be logged. [D-A, D-G, D-H]**
- **(a) Adult/acted pretraining, no child speech.** The full 262 h is adult: IEMOCAP/MEAD/SAVEE/RAVDESS
  acted, MSP-Podcast/CMU-MOSEI podcast/YouTube, MELD = *Friends* TV. **Zero child voice.** Child f0,
  formants, and prosody differ sharply; the frozen probe may mis-map child affect. **Mitigation:**
  validate the *probe* on a held-out child-voice slice before any claim; budget a child calibration set;
  consider light continued self-distillation on child audio (Table 8 says warm-start adaptation is
  high-leverage).
- **(b) Ambiguous weight license.** Repo MIT badge but **no explicit checkpoint license**, and pretraining
  corpora carry research-only terms → **deployment licensing unresolved**. WavLM-Large is cleanly **MIT**.
  **Mitigation:** for any shipped product, either obtain explicit license clarity or **default to the
  WavLM-Large/MIT fallback** — this is a real reason the fallback is non-optional.
- **(c) No speaker-leakage audit.** Authors' own Limitation (venue lines 1381–1384): "whether speaker
  information is removed [is] not explored." For a **child-facing** product, embeddings may carry a
  voiceprint. **Mitigation:** never persist raw audio or raw child embeddings; score ephemerally/on-device;
  run a speaker-ID probe on the features as a **pre-ship gate**.
- **(d) No calibration / no probability outputs.** Paper reports WA/UA/WF1 only — no ECE/reliability, no
  arousal threshold. Pebble's **hard crisis-recall floor** needs calibrated probabilities and a tuned
  threshold the backbone does not supply. **Mitigation:** add a calibration + recall-floor threshold step
  on top of the audio probes (D-G); the safety/crisis decision stays a separate high-recall BCE head with
  its own threshold, never a raw argmax of emotion2vec emotions.

### Child mental-health lens (transfer validity, risks, ethics)

- **Transfer risk is HIGH and asymmetric across the heads.** The categorical-emotion result transfers
  *best* (still adult→child domain gap); the **severity/arousal regression** transfers *worst* (no
  regression validation at all — Decision 3). The **safety/crisis** head gets **no** support from this
  paper (it is SER, not risk detection) — consistent with routing crisis through a dedicated high-recall
  head + the Decision Engine, not the emotion softmax.
- **Arousal ≠ severity for children.** A withdrawn, flat, low-arousal child can be high-severity. Because
  emotion2vec's only continuous signal is an **arousal** manifold, a naïve "high arousal = high risk" map
  would **miss quiet distress** — the most dangerous failure mode under a recall floor. The severity head
  must be trained against a severity target, not arousal proxied as severity.
- **Honest ceiling.** Promise on **MELD-style spontaneous numbers (~52 WA)**, not acted RAVDESS/SAVEE
  (~83). Set thesis expectations and the recall-floor feasibility analysis against the spontaneous figure.
- **Ethics.** Speaker-leakage (b/c above) + child data = treat features as PII; ephemeral scoring; explicit
  consent/data-handling section; the audio signal informs, never autonomously decides, escalation.

### Limitations & open questions for Pebble

- **Contradiction vs Pebble's "emotion2vec validates continuous regression" hope (the thesis's own
  backbone table caveat).** The related-work table already hedges "mostly categorical; less proven on
  regression" — this deep read **hardens that into a fact**: there is **literally no continuous-regression
  number** in the paper, only a UMAP. Any thesis sentence implying emotion2vec is validated for
  dimensional severity is unsupported; the regression evidence belongs to **WavLM/Wagner**, the fallback.
  This is the central contradiction to resolve before committing the severity head to emotion2vec.
- **Contradiction vs EmoBox crowning WavLM-Large.** The same authors' EmoBox 32-dataset benchmark ranks
  **WavLM-Large** as the best *general* backbone, using emotion2vec as the evaluation oracle rather than
  the across-the-board winner. So "emotion2vec is best" is **protocol-dependent** (IEMOCAP linear probe
  yes; broad EmoBox sweep no) — another reason the WavLM comparator is mandatory.
- **Granularity gap vs Pebble's turn-level text.** Half the objective is **utterance-level**; benchmarks
  are clip/utterance-level. A voice message is one utterance (fine), but the **text side is turn-level,
  mid-conversation** — the Decision Engine must define how an utterance-level audio score fuses with
  turn-level text scores; emotion2vec gives no cross-modal temporal-alignment guidance.
- **Pre-train/eval overlap.** 4 of 5 pre-training sets (IEMOCAP, MELD, CMU-MOSEI, MEAD) are also evaluated
  → weight the **OOD** evidence (RAVDESS/SAVEE + 9 languages, and especially noisy **MELD**) when
  estimating child-voice performance, not the in-domain 71.79 headline.
- **Which checkpoint?** Paper-grade **base (93.79M)** vs the later **emotion2vec+ seed/base/large**
  (201/4788/42526 h, no peer-reviewed numbers) — open question; needs a bake-off on Pebble's child-voice
  slice. Larger pretraining may help spontaneous speech (the weak MELD axis) but is undocumented.
- **No recall floor / no calibration** — the single biggest mismatch with Pebble's hard-recall thesis;
  must be supplied entirely by Pebble's own threshold + calibration layer (D-G).
