# Paper 24 — MMER: Multimodal Multi-task Learning for Speech Emotion Recognition

## 1. Bibliographic info

**Title:** MMER: Multimodal Multi-task Learning for Speech Emotion Recognition

**Authors:** Sreyan Ghosh, Utkarsh Tyagi, S Ramaneswaran, Harshvardhan Srivastava, Dinesh Manocha (University of Maryland, College Park; NVIDIA, Bangalore; IIT Delhi).

**Year / venue:** Interspeech 2023 (ISCA), `ghosh23b_interspeech`. Preprint: arXiv:2203.16794 (v5, 3 Jun 2023). The earlier arXiv title was "MMER: Multimodal Multi-task learning for Emotion Recognition in Spoken Utterances"; the published Interspeech title is the one above.

**Index terms (verbatim):** "speech emotion recognition, human-computer interaction".

**Code:** https://github.com/Sreyan88/MMER

## 2. Why this paper is in the Pebble set

Pebble v1 is a text-only encoder (NeoBERT) scoring child mental-health text turn-level. The thesis reserves a **voice-message modality extension**: children increasingly interact by voice notes, and emotional tone is carried as much by prosody (pitch, energy, rhythm) as by words. MMER is the single cleanest published recipe for **fusing acoustic + text into one emotion classifier**, and — crucially — it is **multi-task**, which is exactly Pebble's architecture (shared encoder, multiple heads). MMER is therefore the reference design for "what does Pebble's emotion head look like once a voice channel exists, and audio is available alongside the ASR transcript Pebble already needs?"

It is also a cautionary anchor: MMER's numbers are **acted adult studio speech (IEMOCAP)**, five categorical emotions, utterance-level. None of those conditions hold for Pebble (spontaneous child speech, GoEmotions 12-label space, turn-level, in-the-wild audio). The deep read below separates the transferable architecture from the non-transferable benchmark.

---

## Deep research — full-PDF read (2026-06-16)

### Source-access note

The local PDF `pdfs/24-mmer-multimodal-mtl-ser.pdf` was read end-to-end via
`pdftotext` (the Read tool cannot render PDFs). The local file is arXiv:2203.16794 **v5**
(3 Jun 2023). Every load-bearing number was then cross-checked against the **published
Interspeech 2023 version** (ISCA Archive `ghosh23b_interspeech.pdf`), downloaded and
extracted with `pdftotext` directly — because the WebFetch summarizer model hallucinated
the table (it returned WA 72.98% / 39M params / batch 16 / LR 1e-4, none of which appear
in either PDF). The direct text extraction of the published PDF is authoritative and
**matches the local arXiv v5 verbatim** on all headline figures.

Validation traces:
- Search "MMER Multimodal Multi-task Learning Speech Emotion Recognition Ghosh Interspeech 2023 IEMOCAP" → resolved to `https://www.isca-archive.org/interspeech_2023/ghosh23b_interspeech.html` (abstract, authors, venue confirmed) and `.../ghosh23b_interspeech.pdf` (full table).
- Published-PDF `pdftotext` grep confirmed: MMER WA **81.2%**, **228M** params, **75.0%** WA with Google ASR transcripts, baselines RoBERTa **78.1%** / wav2vec-2.0 **78.9%** / naive multimodal **79.8%**, hyper-params batch 4 / accum-grad 4 / 100 epochs / LR 1e-5 / α,β,γ=0.1.
- Conflict rule: published == preprint v5 here, so no delta. Earlier arXiv versions used a different title and an extra augmented-contrastive framing, but v5/published are aligned.

Status tags below: ✔ corroborated (in both local + published PDF) / ≈ approximate / ✖ uncorroborated.

### What the paper actually does

**Goal.** Speech Emotion Recognition (SER): assign one of *j* categorical emotions to a spoken
utterance `u_i = (a_i, t_i)` where `a_i` is the raw audio and `t_i` the transcript (ASR or
human). MMER's thesis: text is now a cheap complementary signal (ASR is near-optimal), and
SER benefits most from **auxiliary tasks that inject extra knowledge** into a shared encoder.

**Architecture — Multimodal Dynamic Fusion Network (MDFN).** Two frozen SSL feature extractors
feed a learned cross-modal interaction module:
- **Acoustic encoder:** `wav2vec-2.0-base`, Facebook checkpoint pre-trained on 960h LibriSpeech. Outputs `e^a_i ∈ R^{J×768}` (frames at 20ms stride / 25ms hop; J depends on audio length). ✔
- **Text encoder:** `RoBERTa-BASE` from HuggingFace, used **as a frozen feature extractor — not fine-tuned**. Outputs `e^t_i ∈ R^{M×768}` for M tokens. ✔ (This is a notable design choice: only the fusion module + acoustic path are trained.)
- `d = 768` for both (base architectures). ✔

**Multimodal Interaction Module (MMI).** Three Cross-Modal Encoder (CME) blocks (B, C, D), each
a transformer layer with h-head cross-modal attention (CMA), residual + feed-forward, plus an
acoustic gate E:
- **Block B** — `CMA(A, T)`: acoustic embeddings A as queries, RoBERTa T as keys/values → produces P (speech-conditioned token reps). Eq. (1): `CMA(A,T)=softmax([W_q A]·[W_k T]/√(d/m))[W_v T]`.
- **Block C** — feeds P back with original T as queries, P as keys/values → **Speech-Aware Word Representations** R.
- **Block D** — T as queries, A as keys/values → **Word-Aware Speech Representations** Q (word-to-frame alignment).
- **Acoustic gate E** (Eq. 2): `g = σ(W_g[R;Q] + B_g)`, then `Q = g·Q` — a sigmoid gate that dynamically suppresses redundant/noisy speech frames.
- Final MMI rep `M = [Q; R] ∈ R^{2d}`, down-projected by linear `l(·)` to d. ✔

**Four jointly optimized tasks** (total loss `L = L_CE + α·L_CTC + β·L_SCL + γ·L_ACL`): ✔
1. **Cross-Entropy (L_CE)** — the SER objective. Final embedding = concat of max-pooled wav2vec-2.0 reps `mp(A)` and MMI reps `mp(M)` → linear + softmax over 4 emotion classes (Eq. 3).
2. **CTC loss (L_CTC)** — an **ASR auxiliary task**: linear projection of un-pooled A → character logits, CTC against the uppercased, punctuation-stripped transcript. Forces the model to learn the monotonic speech↔text alignment and linguistic structure.
3. **Supervised Contrastive Learning (L_SCL)** — instance discrimination on MMI reps M using emotion labels: same-emotion instances are positives, different-emotion are negatives (Algorithm 1). Sharpens emotion-discriminative features.
4. **Augmented Contrastive Learning (L_ACL / "AGL")** — robustness/invariance task: text is **back-translated** (semantic-preserving augmentation), then **re-synthesized to speech via zero-shot speaker-conditioned TTS (YourTTS)** conditioned on a *different* speaker expressing a *similar* emotion. Contrastive loss between original and augmented multimodal reps → enforces speaker-invariant, semantically-invariant emotion features.

**Dataset — IEMOCAP.** ~12 hours of speech, 10 speakers, 5 scripted dyadic sessions, professional
actors. Standard 4-class setup: Happy, Angry, Neutral, Sad, Excited → **Excited merged into Happy**
(so effectively 4 classes). Evaluation = **5-fold leave-one-session-out cross-validation**, averaging
**weighted accuracy (WA)** across folds. ✔

**Hyper-parameters.** batch size **4**, accum-grad **4** (effective batch 16), **100 epochs**, LR
held constant at **1e-5**, AdamW implied. `α=β=γ=0.1`, grid-searched over `{1, 0.1, 0.01, 0.001}`.
Each step ~10 min on one **A100**. **MMER = 228M parameters.** ✔

**Results — Table 1 (IEMOCAP, WA, 5-fold CV):** ✔
| System | Modality | WA |
|---|---|---|
| Cai et al. [1] (prior SOTA, re-implemented 5-fold) | {a,t} | 77.1% |
| Yang et al. [39] | {a,t} | 77.7% |
| Morais et al. [2] (closest; 2× speech encoders, >2× params) | {a,t} | 77.4% |
| **Baseline** RoBERTa-BASE | {t} | **78.1%** |
| **Baseline** wav2vec-2.0 | {a} | **78.9%** |
| **Baseline** naive multimodal (concat pooled reps) | {a,t} | **79.8%** |
| **MMER w/o CTC** | {a,t} | **78.1%** |
| **MMER w/o SCL** | {a,t} | **78.9%** |
| **MMER w/o ACL** | {a,t} | **79.8%** |
| **MMER (full)** | {a,t} | **81.2%** |

(Note: the authors' own unimodal/naive baselines at 78–80% already exceed the cited prior-art
77.1% — partly a stronger training recipe, partly that prior numbers come from the literature
under varying CV folds; only Cai et al. was re-run under matched 5-fold CV.)

**Robustness to ASR.** With **Google ASR transcripts instead of gold transcripts at inference,
WA = 75.0%** (a ~6.2-point drop from 81.2%) — ✔, the single most Pebble-relevant number, because
Pebble would never have gold transcripts for child voice notes.

**Ablation reading (Table 1 + Fig. 2 confusion matrices).** Removing each auxiliary task drops WA:
−3.1 (CTC, 81.2→78.1), −2.3 (SCL, →78.9), −1.4 (ACL, →79.8). So **CTC/ASR is the most valuable
auxiliary task; ACL the least** — but ACL has a distinct qualitative effect: Fig. 2 shows **ACL
alleviates the neutral-class bias** (a known SER failure mode), while **CTC slightly amplifies
neutral bias** (the model leans on semantic/text cues and under-weights speech). SCL sits between.

**Stated limitations.** (1) Contrastive learning needs **large batch sizes** (hard with audio memory
cost). (2) **Pre-computed text features** (RoBERTa frozen) — text path can't adapt to the emotion task.

### Parts directly useful for Pebble (each tagged with Decision IDs)

1. **Frozen-RoBERTa-as-feature-extractor + trained fusion module** — MMER fine-tunes only the
   acoustic path and the cross-modal module; the text encoder is frozen. **(D-A, D-E)** For
   Pebble's voice extension, this is the cheapest integration shape: keep the **already-trained
   NeoBERT emotion encoder frozen**, add a wav2vec-2.0 acoustic branch + a small cross-modal
   fusion module, and train only the new parameters. NeoBERT *is* Pebble's "RoBERTa here." This
   is a staged warm-start: text head trained first (v1), audio bolted on later without disturbing
   it. **Transfer risk:** MMER froze RoBERTa because IEMOCAP is tiny (~12h); on a larger Pebble
   audio corpus, jointly fine-tuning the text encoder might help — frozen is the safe *starting*
   config, not necessarily the ceiling.

2. **CTC/ASR as the dominant multi-task auxiliary (−3.1 WA when removed)** — **(D-B)** This is
   direct evidence for Pebble's MTL design: an **auxiliary task that grounds the shared
   representation in the speech↔text alignment** is worth more than the contrastive tricks. For
   Pebble, the analogue when audio is present is a **CTC/ASR auxiliary head on the acoustic
   branch**, kept on during emotion training. **Transfer risk:** the benefit is largest precisely
   because text is the strong modality for emotion; if Pebble's voice users' transcripts are noisy
   child ASR, the auxiliary may instead inject noise — see point 5.

3. **Static loss weights α=β=γ=0.1, grid-searched over {1,0.1,0.01,0.001}** — **(D-B)** MMER
   reaches SOTA with **simple static λ weighting**, not GradNorm/PCGrad/Nash. The whole search
   space is one shared scalar per auxiliary loss. **Transfer risk:** MMER has 4 tasks on one
   dataset with no severe class imbalance beyond the neutral-bias; Pebble's MTL faces real label
   imbalance (rare high-severity) and heterogeneous heads (regression + softmax), where a single
   static λ may be insufficient — this paper supports *trying static-λ first* (cheap baseline)
   before reaching for LibMTL, not that static λ is always enough.

4. **Acoustic gate `g = σ(W_g[R;Q]+B_g)` (Eq. 2)** — **(D-A)** A one-line sigmoid gate that
   down-weights redundant/noisy speech frames before fusion. **(D-G adjacent)** For Pebble's
   in-the-wild child audio (background noise, mic quality, short clips), an explicit
   frame-confidence gate is a cheap robustness primitive directly reusable in the fusion module.

5. **Google-ASR-transcript inference: WA 75.0% vs 81.2% gold (−6.2)** — **(D-D, D-H)** The honest
   cost of not having gold transcripts. Pebble will *only ever* have ASR transcripts for voice
   notes, so **75.0% is the more realistic transfer baseline than 81.2%.** **(D-H)** This is the
   number to anchor Pebble's voice-extension expectations and to motivate ASR-robustness training
   (e.g., training on ASR transcripts, not gold, to close the train/test mismatch).

6. **Back-translation + speaker-conditioned-TTS augmentation (ACL) reduces neutral-class bias**
   — **(D-B, D-H)** The augmentation pipeline (BT for semantic invariance, YourTTS re-synthesis
   for speaker invariance) is a concrete **data-augmentation recipe for an audio emotion head**,
   and the qualitative win is specifically on the **majority/neutral class** — the analogue of
   Pebble's dominant-emotion imbalance. **Transfer risk:** TTS-synthesized "emotional" child
   speech is itself a hard, under-validated generation problem; this is a v2+ idea, not v1.

### How each part helps Pebble succeed

- **Voice-message head design (point 1).** Concrete artifact: a `pebble/models/audio_fusion.py`
  module that takes (frozen NeoBERT token embeddings, wav2vec-2.0 frame embeddings) → 2–3
  cross-modal attention blocks → gated concat → the existing emotion/severity heads. Train only
  the fusion + acoustic params. This is the minimal, staged way to add voice without retraining v1.
- **Auxiliary-task selection (point 2).** When Pebble runs its MTL ablation, **add CTC/ASR as a
  candidate auxiliary head for the audio branch** and expect it to be the most valuable — MMER's
  −3.1 WA is the prior. Budget the experiment: emotion-only vs emotion+CTC vs emotion+CTC+SCL.
- **Loss-balancing experiment (point 3).** Run the **static-λ baseline first** (one shared scalar
  per auxiliary, grid `{1,0.1,0.01,0.001}`) before LibMTL methods; MMER shows SOTA is reachable
  there, so it's the right control to beat — not skip.
- **Robustness gate (points 4, 5).** Add the acoustic gate to the fusion module, and **evaluate
  the voice head on ASR transcripts, never gold** — report the ASR-vs-gold gap as MMER did
  (their −6.2 WA is the precedent that this gap must be measured, not assumed away).
- **Imbalance / neutral-bias mitigation (point 6).** Treat the BT+TTS pipeline as a v2 augmentation
  experiment specifically targeting Pebble's dominant-emotion class, and inspect the per-class
  confusion matrix (not just aggregate accuracy) to confirm it helps the minority emotions.

### Child mental-health lens

- **Modality fit is real, benchmark fit is not.** The *architecture* (fuse acoustic + ASR text,
  multi-task, gate noisy frames) transfers cleanly to Pebble's voice-note use case. The
  *evidence* does not: IEMOCAP is **acted adult studio speech, 4 merged emotions, balanced-ish,
  utterance-level**. Pebble targets **spontaneous child speech, 12-label GoEmotions-mapped space,
  severe imbalance, turn-level mid-conversation, noisy in-the-wild audio.** Every one of MMER's
  numbers (81.2/75.0 WA) is an *adult-acted* number that should be cited as architecture
  precedent, **not** as a performance bar Pebble can expect.
- **Children's prosody differs from adult actors'.** wav2vec-2.0-base is pre-trained on
  LibriSpeech (adult audiobook read speech). Child speech has higher pitch, different formants,
  and disfluency patterns; an adult-pretrained acoustic encoder may transfer poorly without a
  child-speech adaptation pass. This is the acoustic analogue of Pebble's text child-register gap.
- **ASR is the weak link, and it's worse for children.** MMER loses 6.2 WA on adult Google ASR.
  Child ASR word-error-rates are substantially higher than adult ASR in the literature, so
  Pebble's real-world voice-head degradation from the gold-transcript ceiling will likely **exceed**
  MMER's 6.2 points. The text branch (the strong modality for emotion per MMER's CTC ablation)
  is exactly the one most corrupted by child-ASR errors.
- **Ethics: voice is biometric.** A child's audio is identifying in a way text is not. Any Pebble
  voice extension must add voice-specific consent, on-device or scrubbed processing, and a clear
  policy that raw audio is not retained — a heavier governance bar than the text classifier.
- **No safety/distress emotions in IEMOCAP.** MMER's 4 classes (happy/angry/neutral/sad) contain
  no fear/anxiety/self-harm signal. The acted-emotion → real-distress transfer is unproven; MMER
  cannot tell Pebble anything about detecting *crisis* tone, only coarse valence/arousal.

### Limitations & open questions for Pebble

- **Contradiction vs Pebble's v1 plan (modality).** Pebble v1 is deliberately **text-only**; MMER's
  entire contribution is that **multimodal beats either unimodal** (81.2 vs text-only 78.1 vs
  speech-only 78.9). This is the strongest published case that *voice tone carries emotion signal
  text misses* — i.e., the explicit justification for the v2 voice extension, **and** the warning
  that a text-only model leaves ~3 WA points on the table when audio exists. The +1.4 over the
  naive-concat baseline (79.8→81.2) is the part attributable to the fancy fusion; the bigger jump
  is just *having both modalities at all*.
- **Contradiction vs FAIIR (paper 01) on auxiliary signal.** FAIIR's gains came from **domain-adaptive
  MLM** (self-supervised, in-domain text) before a single-task head; MMER's gains come from
  **supervised + contrastive + ASR multi-task** with no MLM pass. The two papers disagree on where
  the cheap performance lives — Pebble should treat MLM (D-F) and multi-task auxiliaries (D-B) as
  *independent* levers and ablate both, since neither paper tested the other's recipe.
- **Frozen text encoder vs Pebble's whole premise.** MMER **freezes** RoBERTa; Pebble's value is a
  *fine-tuned* domain encoder (NeoBERT on mental-health text). Whether to freeze NeoBERT in the
  fusion stage is therefore an open question MMER cannot answer — its freeze was forced by IEMOCAP's
  tiny size, not principled for Pebble's larger corpus.
- **Tiny, acted, adult benchmark.** 12h / 10 speakers / scripted. Confidence intervals across
  5-fold leave-one-session-out CV are **not reported** — with only 5 folds and 10 speakers, the
  81.2 vs 79.8 gap (1.4 WA) may not be statistically robust. Pebble should not over-index on the
  ranking of MMER's ablation deltas without variance estimates.
- **No calibration, no per-class recall floor.** MMER reports only WA (and confusion matrices). For
  Pebble's safety-adjacent emotion scoring, aggregate accuracy is the wrong target; MMER gives no
  guidance on calibrated probabilities or recall floors for minority/distress classes (D-G), which
  Pebble must add itself.
- **Open question worth one experiment:** does the CTC/ASR auxiliary still help when the transcript
  is *child* ASR (high WER) rather than gold/adult-ASR? MMER only tested gold vs adult-Google-ASR.
  If the auxiliary degrades under high-WER child transcripts, the most valuable MMER component is
  the least transferable — this is the single most important thing for Pebble to measure before
  committing to the multi-task voice design.
