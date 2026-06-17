# Paper 26 — WavLM: Large-Scale Self-Supervised Pre-Training for Full Stack Speech Processing

## 1. Bibliographic info

**Title:** WavLM: Large-Scale Self-Supervised Pre-Training for Full Stack Speech Processing

**Authors:** Sanyuan Chen, Chengyi Wang, Zhengyang Chen, Yu Wu (corresponding, yuwu1@microsoft.com), Shujie Liu, Zhuo Chen, Jinyu Li, Naoyuki Kanda, Takuya Yoshioka, Xiong Xiao, Jian Wu, Long Zhou, Shuo Ren, Yanmin Qian, Yao Qian, Jian Wu, Michael Zeng, Xiangzhan Yu, Furu Wei. (First three authors equal contribution; work done at Microsoft.)

**Affiliations:** Microsoft (Azure Speech / Microsoft Research), Shanghai Jiao Tong University, Harbin Institute of Technology.

**Year / venue:** Published in *IEEE Journal of Selected Topics in Signal Processing* (JSTSP), Vol. 16, No. 6, Oct. 2022, pp. 1505–1518. Local PDF is arXiv:2110.13900v5 (cs.CL, 17 Jun 2022). DOI 10.1109/JSTSP.2022.3188113. Code + checkpoints at https://aka.ms/wavlm.

**Index terms (verbatim):** "Self-Supervised Learning, Speech Pre-Training".

## 2. Problem motivation

Self-supervised learning (SSL) had succeeded in NLP and in speech for ASR/phoneme tasks, but "in other speech tasks, it is still the standard practice to train models from scratch with task-specific datasets." Non-ASR speech tasks (speaker ID, diarization, separation, paralinguistics/emotion) are short of supervised data and would benefit most from a general pre-trained acoustic encoder. The paper's thesis is that a *single* SSL model can serve the **full stack** of speech tasks rather than a family of task-specialized models.

Two concrete drawbacks of prior SSL models (HuBERT, wav2vec 2.0) motivate the design:
1. They are "unsatisfactory for multi-speaker tasks" — separation on top of HuBERT gave only marginal gains over training from scratch, because the pre-training neither enforced speaker discrimination nor included multi-speaker audio.
2. They rely on audiobook data (Libri-Light / LibriSpeech); ">90% audio data derived from audiobook," and that domain mismatch hurts downstream tasks whose acoustic characteristics differ from clean read speech.

## 3. Position in the literature

WavLM extends the **HuBERT** offline-clustering / masked-prediction paradigm. The paper situates SSL into three families: generative (autoencoding/autoregressive frame prediction), discriminative (CPC, wav2vec/vq-wav2vec/wav2vec 2.0, DiscreteBERT, HuBERT, w2v-BERT), and multi-task (PASE/PASE+, UniSpeech). It is positioned against the **SUPERB** benchmark (Yang et al.), where HuBERT was the prior best generalist, and against **UniSpeech-SAT** (speaker-aware HuBERT). WavLM claims to be "the first to explore SSL for full stack tasks instead of focusing on ASR or other specific tasks," achieving this "even without scaling up the model size to 8 billion parameters" (a jab at the concurrent BigSSL).

## 4. Method — the three modifications over HuBERT

WavLM = HuBERT backbone + masked-prediction loss + **three additive changes**:

**(A) Masked speech denoising + prediction (the core novelty).** Inputs are *simulated noisy/overlapped* speech; the target is to predict the pseudo-labels of the **original (clean) main-speaker** speech on the masked region (HuBERT-style k-means cluster targets on MFCC, then on latent features in iteration 2). Concretely (Algorithm 1): for 20% of utterances, a primary utterance is mixed with either a secondary utterance from the same batch (energy ratio U(−5,5) dB) or a DNS noise clip (energy ratio U(−5,20) dB); overlap is constrained to **< 50%** so the primary speaker is always dominant/longer and remains identifiable. The model must denoise + separate + predict content of the main speaker — implicitly forcing speaker discrimination, separation, and enhancement capability into the representation. Loss is the masked-region cross-entropy over cluster IDs, applied only on masked indices (Eq. 7).

**(B) Gated relative position bias (gREP).** Replaces wav2vec2/HuBERT's convolutional relative position embedding with a **gated** relative position bias added to attention logits (Eqs. 3–6). A bucket relative position embedding with n=320 buckets, logarithmically spaced up to a max offset m=800, shared across all layers. The gate `g_i = sigmoid(q_i·u)` conditions the position bias on the **current speech content** — "the same distance offset ... tends to play different roles if one frame is silence while the other belongs to a speech segment." Improves content tasks (ASR/PR) at near-zero param/speed cost.

**(C) Scaled + diversified pre-training data → "Mix 94k hr."** 60k h Libri-Light + 10k h GigaSpeech (audiobooks/podcasts/YouTube; only the clean 10k of 40k used) + 24k h English VoxPopuli (European Parliament recordings) = **94k hours** of public English audio, vs HuBERT/wav2vec2's audiobook-only data. Diverse backgrounds reduce the audiobook bias.

Plus a **training-stabilization trick** for fp16: rescale attention logits by subtracting the per-row max before exp (Eq. 8, scale c=32) to avoid NaN overflow on large models.

## 5. Model variants and pre-training setup

| Variant | Layers | Hidden | Heads | Params | Pre-train data | Steps | Denoise % / noise-mix prob |
|---|---|---|---|---|---|---|---|
| WavLM Base | 12 | 768 | 8 | **94.70M** | LS 960 h | 400k | 20% / p_n=0 |
| WavLM Base+ | 12 | 768 | 8 | 94.70M | Mix 94k h | 1M | 20% / p_n=10% |
| WavLM Large | 24 | 1024 | 12 | **316.62M** | Mix 94k h | 700k | 20% / p_n=10% |

Conv feature encoder: 7 temporal-conv blocks, 512 channels, strides (5,2,2,2,2,2,2), kernels (10,3,3,3,3,2,2) → each output frame ≈ 25 ms of audio with 20 ms stride (i.e. 50 Hz frame rate). Base uses 6th-layer features of 1st-iteration HuBERT Base for clustering targets; Base+/Large use 9th-layer features of released 2nd-iteration HuBERT Base.

## 6. Experiments and results

### 6.1 SUPERB universal-representation benchmark (Table I)

Pre-trained model is **frozen**; downstream tasks consume a **learnable weighted sum of all layer hidden states**. 15 tasks across content / speaker / semantics / paralinguistics / generation. Overall score = average over tasks (QbE ×100; error rates → 1−err).

Key SUPERB numbers (Table I), focusing on the **Emotion Recognition (ER, paralinguistics aspect, IEMOCAP, accuracy ↑)** column and overall:

| Model | Params | ER Acc ↑ | SID Acc ↑ | SD DER ↓ | Overall ↑ |
|---|---|---|---|---|---|
| HuBERT Base | 94.68M | 64.92 | 81.42 | 5.88 | 70.9 |
| WavLM Base | 94.70M | **65.94** | 84.51 | 4.55 | 72.0 |
|   – w/o denoising task | 94.70M | 65.55 | 84.39 | 6.03 | 71.7 |
|   – w/o structure modification | 94.68M | 65.60 | 84.74 | 4.72 | 71.9 |
| WavLM Base+ | 94.70M | **68.65** | 89.42 | 3.50 | 73.4 |
| wav2vec 2.0 Large | 317.38M | 65.64 | 86.14 | 5.62 | 70.4 |
| HuBERT Large | 316.61M | 67.62 | 90.33 | 5.75 | 72.2 |
| **WavLM Large** | 316.62M | **70.62** | 95.49 | 3.24 | **74.6** |

WavLM Large is best on the overall score (74.6) and "outperforms HuBERT Large on 14 subtasks, ... an absolute 2.4 point improvement in the overall evaluation." Note **WavLM Base+ (94.7M) beats HuBERT Large and wav2vec 2.0 Large (≈317M) on overall** despite being ~3× smaller. For ER specifically, the progression is HuBERT Base 64.92 → WavLM Base 65.94 → WavLM Base+ 68.65 → WavLM Large 70.62; the largest jump comes from data scale (Base→Base+: +2.71 abs).

**Layer-weight analysis (Fig. 2–3):** bottom layers carry speaker information; top layers carry content/semantics; middle layers matter most for speaker tasks in Large. (Paralinguistic ER draws on a mix — the weighted-sum design is what lets one frozen encoder serve both speaker and content tasks.)

### 6.2 The two ablations (Table I, in-line)

- **w/o denoising task** (remove simulated noisy/overlapped mixing): biggest hit is **speaker diarization** (DER 4.55 → 6.03) and SD/SS/SV degrade — confirms the denoising task is what creates multi-speaker capability. ER barely moves (65.94 → 65.55).
- **w/o structure modification** (drop gated relative position bias): hits **PR and ASR** (content tasks) — confirms gREP is a content-task lever. ER essentially unchanged (65.94 → 65.60).

### 6.3 Beyond-SUPERB task-specific SOTA (encoder unfrozen where noted)

- **Speaker verification (Table II, VoxCeleb1):** WavLM Large hits **0.383% / 0.480% / 0.986% EER** on Vox1-O/E/H (with large-margin FT + score calibration), beating ECAPA-TDNN and the VoxSRC-2021 winner. >35% relative EER improvement over Fbank.
- **Speaker diarization (Table III, CALLHOME):** WavLM Large + EEND-vector-clustering reaches **10.35% DER** overall (new SOTA), a 12.6% relative reduction over EEND-EDA-clustering. WavLM Base+ alone beats HuBERT Large.
- **Speech separation (Table IV, LibriCSS):** WavLM Large (frozen) average **6.0% WER**, a 27.7% relative reduction over the Conformer baseline; 32.5% relative at 40% overlap. (Freezing beats unfreezing because the eval set is real meeting audio vs. simulated training mixtures.)
- **ASR (Tables V–VI, LibriSpeech 960h):** WavLM Large reaches **1.8% / 3.2% WER** on test-clean/test-other — comparable to wav2vec 2.0 / HuBERT (ASR is not where WavLM's gains concentrate). Model scaling gives 38% relative WER reduction Base→Large.

## 7. Authors' stated limitations / future work

Conclusion is brief: future directions are (1) scaling model size further, (2) model compression for deployment ("limited test time resources in real scenarios"), and (3) jointly learning text+speech SSL. No fairness, demographic, child-speech, or out-of-English analysis is presented — WavLM is **English-only** by construction (it explicitly uses only the 24k English subset of multilingual VoxPopuli). The frozen-encoder SUPERB protocol "cannot show the power of pre-trained models," motivating the unfrozen task-specific experiments.

---

## Deep research — full-PDF read (2026-06-16)

> Read against the IEEE JSTSP 2022 published version (vol. 16(6):1505–1518, DOI
> 10.1109/JSTSP.2022.3188113); local PDF is `pdfs/26-wavlm.pdf` (arXiv:2110.13900v5). Numbers
> below cross-checked against the SUPERB benchmark table and Microsoft's `aka.ms/wavlm` /
> HuggingFace `microsoft/wavlm-*` cards. WavLM is the candidate **acoustic encoder for Pebble's
> voice-message modality** — a separate, optional input path from the NeoBERT *text* encoder, not a
> replacement for it. This section frames every transfer through that lens.

### Source-access note

- Full text extracted with `pdftotext "pdfs/26-wavlm.pdf" -` (the Read tool cannot render PDFs;
  per repo memory `pdf-extraction-local.md`). Read end-to-end: method (§IV), Algorithm 1
  (noisy/overlap simulation), Table I (SUPERB, all 15 tasks incl. ER), Tables II–VI (SV/SD/SS/ASR),
  and the two in-line ablations.
- **Web-validated numbers + traces:**
  - ER Acc / pre-training hours — query "WavLM SUPERB emotion recognition accuracy WavLM Large
    70.62 IEMOCAP HuBERT" → corroborated WavLM Large ER **70.62%** and 94k-hour
    (Libri-Light 60k + GigaSpeech 10k + VoxPopuli 24k) pre-training via
    https://arxiv.org/pdf/2110.13900v2 and HuggingFace `microsoft/wavlm-large`. **✔**
  - Denoising/gREP/data composition — query "WavLM 94k hours pre-training ... masked speech
    denoising gated relative position bias" → corroborated 20%-utterance corruption, gated rel.
    pos. bias, and the three-corpus split via emergentmind WavLM topic + unilm README. **✔**
  - Param counts / steps / 2.4-pt overall / 14 subtasks — WebFetch of
    https://ar5iv.labs.arxiv.org/html/2110.13900 confirmed 94.70M / 316.62M, 400k/1M/700k steps,
    "+2.4 point" overall, "14 subtasks." **✔** *Caveat:* ar5iv mis-aligned the ER row, printing
    HuBERT Large ER as 70.62 (= WavLM Large's value). The local PDF's ER column is a clean
    sequential list giving **HuBERT Large 67.62 / WavLM Large 70.62**, which is internally
    consistent and matches the published SUPERB leaderboard ordering; I use the PDF values and tag
    HuBERT Large ER **≈** (ar5iv conflict noted), WavLM Large ER **✔**.

### What the paper actually does (exact numbers, table refs)

- **One frozen acoustic encoder, 15 SUPERB tasks**, via learnable per-layer weighted-sum
  (Table I). WavLM Large overall **74.6 ✔** (+2.4 abs over HuBERT Large 72.2 ✔), best on 14/15.
- **Emotion Recognition (IEMOCAP, 4-class, accuracy):** WavLM Large **70.62% ✔**, WavLM Base+
  **68.65% ✔**, WavLM Base **65.94% ✔**, HuBERT Base 64.92 ✔, wav2vec 2.0 Large 65.64 ✔,
  HuBERT Large **67.62 ≈** (Table I, ParaL/ER column). Data scale is the dominant ER lever
  (Base→Base+ = +2.71 abs from 960h→94k h).
- **Three modifications, two ablations** (Table I): removing the **denoising task** spikes
  diarization DER 4.55→6.03 ✔ (multi-speaker capability comes from denoising); removing the
  **gated rel-pos bias** degrades PR/ASR ✔ (content lever). Neither ablation materially moves ER
  (±0.4), i.e. ER rides mostly on data scale + the speaker-discrimination signal, not on gREP.
- **Pre-training:** 94k h public English (60k Libri-Light + 10k GigaSpeech + 24k VoxPopuli) ✔;
  Base 400k / Base+ 1M / Large 700k steps ✔; 20% of utterances corrupted, overlap < 50% ✔.
- **Beyond-SUPERB SOTA:** SV VoxCeleb1 0.383/0.480/0.986% EER ✔; CALLHOME diarization 10.35% DER ✔;
  LibriCSS separation 6.0% avg WER (−27.7% rel) ✔; LibriSpeech ASR 1.8/3.2% WER ✔.

### Parts directly useful for Pebble (each tagged with Decision IDs)

1. **WavLM as the voice-message acoustic encoder for a paralinguistic/emotion head [D-A, D-D].**
   The exact analogue of NeoBERT-for-text. WavLM Large 70.62% / Base+ 68.65% on SUPERB ER is the
   published ceiling for a *frozen* SSL encoder + light head on English speech emotion — a concrete
   target and an architecture (frozen encoder + weighted-layer-sum + small head). WavLM Base+
   (94.7M) is the size/quality sweet spot: it beats both ~317M Large baselines on overall while
   staying child-deployable.
2. **Frozen-encoder + learnable per-layer weighted sum, not last-layer-only [D-A, D-E].** SUPERB's
   protocol (and WavLM's layer-weight analysis, Fig. 2–3) shows different tasks need different
   layers; paralinguistic/emotion content is *distributed*, not in the top layer. For Pebble's
   voice head this argues for a weighted-sum read-out over WavLM layers rather than a single CLS-like
   frame pool — and it lets the WavLM weights stay frozen (cheap, like Pebble's v1 staged-FT ethos).
3. **Severity/intensity as a regression target off WavLM features [D-D].** Pebble's `severity` head
   is regression (Pearson metric, intensity transfer). Speech emotion *dimensions* (arousal/valence)
   are the audio analogue; WavLM's frozen features + a small regressor are the standard, cheap path,
   and ER's data-scale sensitivity (Base→Base+ +2.71) tells Pebble that **for the voice path, more
   diverse unlabeled audio beats a bigger head** — the same lesson D-F/D-H push on the text side.
4. **Domain-diversity-over-clean-volume principle [D-F, D-H].** WavLM's headline finding is that
   adding non-audiobook audio (podcasts/YouTube/parliament) — not just more audiobook — is what
   lifted ASV/OOD-ASR/IC/SF/**ER**. This is the audio twin of Pebble's domain-adaptive-MLM (D-F) and
   dataset-substitute (D-H) decisions: register/domain match of the *unlabeled* pre-training corpus
   is a first-order lever, and an audiobook-trained encoder will under-serve spontaneous child speech.
5. **The denoising/overlap pre-training task as a robustness lever [D-A].** WavLM bakes
   noise/overlap robustness into the encoder via the masked-denoising objective (DER ablation
   proves it). Child voice messages are noisy, far-field, often multi-voice (siblings, TV) — WavLM
   is *already* the SSL encoder explicitly built for that, which is the single best argument for
   choosing it over wav2vec 2.0 / vanilla HuBERT for Pebble's voice path.

### How each part helps Pebble succeed (per-head / per-config action)

- **Voice-emotion head (maps to Pebble's `emotion`):** add an optional `voice_emotion` experiment —
  frozen `microsoft/wavlm-base-plus`, learnable layer-weights, a 2-layer MLP head over mean-pooled
  weighted-sum features, trained on an English SER corpus (IEMOCAP/MSP-Podcast) mapped onto Pebble's
  12-label GoEmotions scheme where possible. Success bar borrowed from SUPERB: ≥ Base+ 68.65% /
  Large 70.62% IEMOCAP-style 4-class accuracy on the *speech* slice; this is a *separate* head from
  the text `emotion` head, fused downstream, not a replacement. [D-A]
- **Voice-severity head (maps to `severity`):** reuse the same frozen WavLM features for a Pearson
  regression head against arousal/intensity labels; this gives Pebble a voice-side intensity signal
  parallel to the WASSA/SemEval text-side transfer (D-D), so the Decision Engine can corroborate
  text severity with prosodic severity. [D-D]
- **Encoder-size config:** default to **WavLM Base+ (94.7M)** for the voice path — matches NeoBERT's
  250M-ish total budget, runs on the same single-GPU Kaggle stack, and the paper proves it
  out-performs 3× larger encoders on the overall metric. Reserve Large only if the voice head is
  the bottleneck. [D-A]
- **Pre-training/adaptation config:** if a domain-adapted voice encoder is ever trained, copy the
  data principle — mix spontaneous/noisy child-adjacent audio in, don't just add more clean read
  speech; and keep the masked-denoising objective on (it is what buys multi-speaker/noise
  robustness). [D-F, D-H]

### Child mental-health lens (transfer validity, risks, mitigations, ethics)

- **Transfer validity — adult English, read+spontaneous, NOT child speech.** Every WavLM number is
  on adult corpora: IEMOCAP (adult acted dyads), VoxCeleb (celebrities), LibriSpeech (adult
  audiobook narrators), VoxPopuli (adult parliamentarians). **Children's acoustics differ sharply**
  — higher F0, shorter vocal tract, different formant structure, more disfluency, immature prosody.
  A WavLM ER accuracy of 70.62% on adult IEMOCAP does **NOT** transfer to a child voice head; treat
  it strictly as an *upper-bound analogue / architecture proof*, exactly as FAIIR's adult-comparable
  numbers were treated for text. This is the load-bearing transfer caveat.
- **Risk — domain + age double mismatch.** WavLM's own thesis (audiobook bias hurts when downstream
  acoustics differ) cuts against Pebble twice: child register *and* casual home recording both
  differ from the pre-training mix. Mitigation: any voice path must be validated on a held-out slice
  of *actual child voice messages* (or the closest open child-speech SER set, e.g. a child-emotion
  corpus), never claimed from SUPERB.
- **Risk — speaker identity is learned and strong (SID 95.49%, SV 0.383% EER).** WavLM is, by
  design, an excellent speaker fingerprinter. For a child-facing product that is a *privacy hazard*:
  WavLM embeddings can re-identify a child by voice. Mitigation: do not persist raw WavLM speaker
  embeddings; extract only the emotion/severity head outputs; if embeddings are cached, treat them
  as biometric PII under the same governance Pebble applies to text (consent, minimization,
  controlled storage), and prefer on-device feature extraction.
- **Ethics — modality consent.** Voice is biometric; a child-facing voice path needs explicit
  age-appropriate consent and guardian notification beyond what text needs. WavLM offers no fairness
  or child analysis, so Pebble owns that evaluation entirely.
- **Mitigation that fits Pebble's recall-floor ethos:** keep the voice head *advisory* into the
  Decision Engine, never an autonomous safety trigger — same product invariant as the text heads;
  fuse text+voice and let the rule layer / human pathway own escalation.

### Limitations & open questions for Pebble (incl. ≥1 contradiction/gap)

- **Contradiction vs. Pebble's plan (modality + label regime).** Pebble v1 (`docs/decisions.md`) is
  a **text** NeoBERT model on *silver-labeled mental-health text*, turn-level. WavLM is a **frozen
  acoustic** encoder evaluated on *gold* speech-emotion labels (IEMOCAP), utterance-level. The voice
  path is therefore **out of v1 scope** — adopting WavLM means adding a second modality, a second
  encoder, a second (audio) labeled-data pipeline, and biometric governance. The honest read: WavLM
  is a strong *v2+ voice-message* candidate, not a v1 component. Flag this explicitly so it is not
  conflated with the v1 text roadmap.
- **Contradiction vs. ModernBERT/NeoBERT (D-A) framing.** The encoder-backbone decision D-A is, in
  the rest of the corpus, a *text*-encoder bake-off (NeoBERT vs ModernBERT vs MentalBERT). WavLM
  does not compete in that bake-off at all; it answers a *different* D-A question (which **audio**
  encoder for the voice path). Do not let WavLM's "beats HuBERT/wav2vec2" claim leak into the text
  D-A argument — they are disjoint.
- **No ordinal/distance-aware emotion structure (vs. D-C).** SUPERB ER is flat 4-class accuracy;
  WavLM gives Pebble nothing on ordinal severity loss or recall-floor calibration (D-C, D-G). The
  voice-severity head would have to import those from the text-side decisions, not from this paper.
- **English-only.** WavLM uses only the 24k English subset of VoxPopuli and is not multilingual; any
  non-English child voice support is unaddressed.
- **Gold-label dependence.** All ER gains assume curated labels; Pebble has no gold child-speech
  emotion labels and would face the same silver-label problem on the audio side, *plus* the cost of
  collecting child audio — a strictly harder data position than the text path.
- **Open question worth resolving before any voice work:** is there an open child-speech emotion
  corpus with redistributable licensing? Without one, the voice path cannot be validated, and
  SUPERB's 70.62% is the only (non-transferring) anchor available.
