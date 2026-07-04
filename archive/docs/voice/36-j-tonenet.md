# Paper 36 — J-ToneNet: A Transformer-based Encoding Network for Improving Tone Classification in Continuous Speech via F0 Sequences

## 1. Bibliographic info

**Title:** J-ToneNet: A Transformer-based Encoding Network for Improving Tone Classification in Continuous Speech via F0 Sequences

**Authors:** Yi-Fen Liu (corresponding, yfliu@fcu.edu.tw) and Xiang-Li Lu, Department of Information Engineering and Computer Science, Feng-Chia University, Taiwan.

**Year / venue:** Interspeech 2023 (Dublin, Ireland, 20–24 August 2023), pages 2138–2142. ISCA Archive id `liu23e_interspeech`. DOI 10.21437/Interspeech.2023-695.

**Journal extension:** the same authors published a longer follow-on, "Learning and consolidating the contextualized contour representations of tones from F0 sequences and durational variations via transformers," *The Journal of the Acoustical Society of America* **156**(5):3353 (2024) — the J-ToneNet design carried forward and expanded.

**Funding:** National Science and Technology Council, Taiwan, project 110-2222-E-035-005-MY2.

**Index terms (verbatim):** "pitch contour, tonal coarticulation, speech rhythm, jointly learning, encoder, BERT, Transformer layers".

## 2. Problem motivation

Mandarin Chinese is a tonal language: four lexical tones on full syllables (high `/55/`, rising `/25/`, dipping `/214/`, falling `/51/`) distinguish word meaning purely through the shape of the fundamental-frequency (f0) contour. Most prior tone classifiers work on **isolated syllables** and lean on richer features than f0 alone — spectrograms, MFCCs, energy — to hit high accuracy. The paper's thesis is that the real difficulty is not the isolated syllable but **continuous speech**, where tonal contours are distorted by **coarticulation** (a tone's contour is pulled toward its neighbors) and by **speech-rhythm / speech-rate** effects. Models built "in absence of context" cannot discriminate a coarticulated tone from a citation tone. The authors note that, e.g., Tone 3 is often realized as a low-falling `/21/` and Tone 2 as a dipping `/323/` in spoken Taiwan Mandarin — variants a context-free model never sees cleanly.

Tone classification matters for (a) computer-aided language learning (CALL) for L2 Mandarin learners and (b) raising recognition accuracy in Mandarin ASR. The stated gap: "there are relatively few documented deep learning models based on transformers or the BERT-based framework to encode the pitch curve information from the f0 value sequences for tone classification." J-ToneNet fills that gap with an f0-only, fully-transformer, utterance-level model.

## 3. Position in the literature

The paper situates itself against three families. **CNN tone models on spectral features** — Chen et al. (Interspeech 2016) and **ToneNet** (Gao, Sun, Yang, Interspeech 2019; ref [14] here — this repo's paper #33) achieved strong results on broadcast news using Mel-/FFT-spectrograms, but on **isolated** segments. **Recurrent / attention / joint-training hybrids** — Yang et al. (CBLSTM+attention, Interspeech 2018), Tang & Li (end-to-end with short-term context, APSIPA 2021), Huang et al. (encoder-decoder pitch tracking + joint training, ICASSP 2021) reduced error rates by adding context. **Pitch-free tone classification** — Ryant et al. (2014) classified tone without pitch tracking at all.

J-ToneNet's positioning is deliberately contrarian on two axes: (1) **f0-only** input (no spectrogram/MFCC/energy), inverting the field's "more features = better" trend, to isolate the contour-modeling problem; and (2) **transformer / BERT-style encoder over the f0 sequence**, borrowing the multi-`[CLS]` interval-segmentation trick from **BERTSUM** (Liu & Lapata, EMNLP-IJCNLP 2019) used there for multi-sentence summarization, repurposed here for multi-syllable utterances.

## 4. Datasets deep dive — FCU-VOICE-100 and MCDC-8

Two datasets in **different speaking styles** — this contrast is the experimental backbone. Both recorded in quiet rooms, sampled at **16 kHz**, force-aligned with the **ILAS phone aligner**, with manual postediting / human verification.

**FCU-VOICE-100 (prepared READ speech).** 400 Feng-Chia University students recruited; each group of 40 speakers (20 M / 20 F) read the same 250 reading prompts. 10 distinct prompt sets drawn from the Sinica Core Vocabulary Inventory — half frequently-used words, half sentences illustrating word use. Speakers read "with clarity and naturalness." Experiments use a **subset of 100 speakers**. After verification, **4,641 of 25,020 recordings were excluded** (only "correctly produced and properly aligned" sounds kept; ambiguous cases resolved by annotator–first-author consensus).

**MCDC-8 (spontaneous CONVERSATIONAL speech).** Eight 1-hour spontaneous conversations, free topics, 16 paired speakers, from the released **Mandarin Conversation Dialog Corpus (MCDC)**. Truncated into **6,060 speaking turns**. Verified on inter-pausing units (IPUs), words, syllables, and tone transcription.

**Processing units:** clausal chunks for read speech, IPUs for conversational speech.

**Table 1 (dataset characteristics):**

| Corpus | #Spkrs | #Utt | #Syls | Tone-verified | Mono/di-syllabic utts |
|---|---|---|---|---|---|
| FCU-VOICE-100 | 100 | 23,601 | 125,178 | Yes (53.4%) | 46.3% (~11,000) |
| MCDC-8 | 16 | 13,407 | 131,003 | Yes (75.9%) | 14.1% (1,890) |

Length distribution (Figure 2): in conversational MCDC-8, ~10% of utterances exceed **17 syllables** — much longer, more coarticulated material than the read corpus. This is the hard test for the context model.

## 5. Method

### 5.1 f0-contour input pipeline (segment features)

f0 extracted with **PRAAT** pitch tracking, then **log-transformed** and **normalized to [0,1]** per speaker using the f0 ceiling/floor at the **0.1% and 99.9% percentiles** of the speaker's range — abbreviated **normLogF0**. Two feature sets:

- **normLogF0(20):** per syllable, a **fixed 20-point** vector from interpolating the sequential f0 observations. This is the f0-only representation.
- **ToneFea(17):** a 17-dim hand-engineered expansion (Table 3 in paper): 2nd-order polynomial coefficients fit to the contour (feat 1–3), relative positions of minima/maxima (4–5), six quartile-difference features (6–11), and corresponding region slopes (12–17). Used as an "append" set to test whether engineered features still help over the raw contour.

### 5.2 Segment-based baselines (isolated syllables)

- **Random Forest** — 16,384 tree predictors; chosen for robustness to noisy f0 estimates from pitch tracking. The state-of-the-art-substitute baseline.
- **FFN** — two fully-connected layers, **GeLU** activations, last hidden → 512 neurons → softmax over 4 tones.
- **1D-CNN** — six conv layers, kernel size 4, stride 1, filters 128/256/512 (per 2 layers), average pooling (kernel 2) after layers 2 and 4, then two FC layers of 512 → softmax over 4 tones. GeLU throughout.

### 5.3 C-Net: tonal-contour encoder (Figure 3)

The core. A **BERTSUM-style bidirectional transformer over the f0 sequence**. Input building blocks (all summed at each f0 position):

1. **Pitch Embedding** — linear map of the 1-d f0 value to hidden dim **d = 512**; unvoiced/untracked and end-padding values are zeros.
2. **Positional Embedding** — **sinusoidal** (Vaswani-style) to mark pitch ordering.
3. **Token Embedding** — `[VAL]` for tracked pitch tokens, `[NAN]` for untracked/padding. A **`[CLS]` token inserted in front of every syllable or word**, aggregating contour info up to a boundary `[SEP]`.
4. **Segment Embedding** — interval segmentation with two symbols `E_A` / `E_B` to distinguish **odd vs even** tones in the utterance (the BERTSUM multi-sentence trick, here multi-syllable).

Transformer stack (**L = 4 layers**):

```
h_l = LN(h_{l-1} + MHAtt(h_{l-1}))      (1)
h_l = LN(h_l + FFN(h_l))                (2)
```

"Lower Transformer layers focus on adjacent pitches; higher layers, with self-attention, focus more on coarticulation effects of tones." The contour embedding of syllable *i* is the top-layer hidden vector of its `[CLS]` token.

### 5.4 R-Net: speech-rhythm auxiliary encoder

A parallel encoder taking **two duration sequences**: (a) raw syllable durations, (b) the difference between each syllable duration and the mean duration. A **Duration Embedding** (FC layer → d = 512) + positional embedding feed a **2-layer transformer** (same eqs. 1–2). Produces a rhythm embedding per syllable. R-Net is what injects speech-rate / rhythm context that pure f0 cannot carry.

### 5.5 J-ToneNet: fusion + joint learning

Fuse contour embedding and rhythm embedding by projecting both into a shared space and concatenating before layer norm. A **squeeze-and-excitation-style gating** (reverse-bottleneck: expand FC → GeLU → reduce FC) computes channel-attention weights, element-wise multiplied into the fused state, linear-projected back to d = 512, then a **tanh** transform for interpretability, then the classifier.

**Joint-learning loss (the headline contribution):**

```
L = CE(syllable-tone prediction, gold) + CE(word-tone prediction, gold)   (7)
```

The loss combines cross-entropy on **syllable tones** *and* on **word tones** (monosyllabic words and "certain disyllabic word tone pairs"). The motivation is the "compatible vs conflicting context" idea: a neighbor tone with similar register (e.g. `/55/-/55/`) vs different (e.g. `/51/-/55/`) shapes coarticulation, so jointly predicting word-level tone pairs consolidates the syllable-level contour representations.

### 5.6 Splits

Each dataset split **80% train / 10% dev / 10% test** by utterances.

## 6. Experiments and results — exact numbers (Table 3)

All numbers are **tone-classification accuracy (%)**. Left block = segment baselines on isolated syllables; right block = J-ToneNet ablation by utterance length.

**Segment baselines (isolated syllables):**

| Model | FCU-VOICE-100 F0 | FCU-VOICE-100 ToneFea | MCDC-8 F0 | MCDC-8 ToneFea |
|---|---|---|---|---|
| Random Forest | 52.5 | 57.2 | 44.8 | 48.9 |
| FFN | 50.5 | 55.9 | 43.6 | 44.9 |
| 1D-CNN | 52.6 | 56.7 | 45.4 | 45.4 |
| **J-ToneNet** | **91.0** | — | **61.7** | — |

**J-ToneNet component-removal ablation (overall + by utterance length in syllables):**

| Config | FCU Overall | FCU ≤2 | FCU 3–20 | FCU ≥21 | MCDC Overall | MCDC ≤2 | MCDC 3–20 | MCDC ≥21 |
|---|---|---|---|---|---|---|---|---|
| **J-ToneNet (full)** | **91.0** | 80.0 | 93.0 | 94.1 | **61.7** | 67.1 | 61.9 | 60.7 |
| − joint learning | 87.7 | 78.2 | 89.4 | 91.2 | 58.6 | 63.4 | 59.7 | 55.8 |
| − joint learn. & R-Net | 86.0 | 78.9 | 87.4 | 73.5 | 58.9 | 63.8 | 60.2 | 55.6 |
| only C-Net on SYL | 59.0 | — | 50.6 | — | — | — | — | — |

**Key readings:**
- **Read speech (FCU-VOICE-100):** J-ToneNet **91.0%** vs best segment baseline **57.2%** (RF + ToneFea) — a **+33.8-point** absolute jump. The win is overwhelming and grows with utterance length (94.1% at ≥21 syllables vs 80.0% at ≤2).
- **Spontaneous speech (MCDC-8):** J-ToneNet **61.7%** vs best baseline **48.9%** (RF + ToneFea) — **+12.8 points**, but absolute accuracy is much lower, and (unlike read speech) accuracy does **not** improve with length (60.7% at ≥21 vs 67.1% at ≤2).
- **Joint learning** contributes **+3.3 pts** on read (91.0 → 87.7) and **+3.1 pts** on conversational (61.7 → 58.6).
- **R-Net** is critical for **long read-speech** chunks: removing it collapses FCU ≥21-syllable accuracy from 91.2 → **73.5** (−17.7 pts). On conversational speech R-Net's effect is small/ambiguous.
- **C-Net alone on isolated syllables** scores only **59.0%** (FCU) — "effective, but largely falls behind" the utterance-level context model. This is the existence proof that **utterance context, not the encoder alone, drives the gains.**
- **ToneFea(17) hand features** help the read-speech baselines (RF 52.5→57.2) but give "slightly improvement or nearly no gain" on spontaneous neural models — the engineered features do not transfer to spontaneous speech.

The authors call the results "quite preliminary"; conversational results are explicitly "unsatisfactory" and flagged as future work (richer rhythm / vowel-merging modeling).

## 7. Authors' stated limitations

(a) Model "still in development," results "preliminary." (b) Conversational speech accuracy (~62%) is unsatisfactory; cause attributed to under-modeled rhythmic timing and vowel merging. (c) Future work = enriching rhythmic representations of inter-syllable timing. (d) Notably, the authors explicitly flag the model's value for "**clinical applications of screening children's speech on tone production**" (citing ref [33]) — the one direct child-facing hook in the paper.

## Deep research — full-PDF read (2026-06-16)

### Source-access note

The full PDF `docs/papers/pdfs/36-j-tonenet.pdf` was extracted with `pdftotext` (the local file is the camera-ready Interspeech 2023 proceedings PDF, with the footer "10.21437/Interspeech.2023-695" and pages 2138–2142 embedded). Validation:

- **Venue / DOI / pages / authors** — confirmed against the ISCA Archive entry. Query: "J-ToneNet Transformer Tone Classification Continuous Speech F0 Sequences Interspeech 2023 Liu Lu" → https://www.isca-archive.org/interspeech_2023/liu23e_interspeech.html (title, authors Yi-Fen Liu & Xiang-Li Lu, pp. 2138–2142, DOI 10.21437/Interspeech.2023-695). **✔ corroborated.** The ISCA page exposes only the abstract, so dataset names and all numbers come from the full local PDF, not the web.
- **Datasets** — `FCU-VOICE-100` (read) and `MCDC-8` (spontaneous, from the Mandarin Conversation Dialog Corpus) are named only in §2 of the full PDF. The ISCA abstract page does **not** name them; WebFetch of the ISCA page returned "none of the specific datasets appear." So dataset names are **✔ corroborated from the local camera-ready PDF text** (Table 1 + §2.1), web-unavailable. **≈** on any external cross-check of the corpora themselves (ILAS/MCDC are Tseng's Academia Sinica resources, not openly downloadable).
- **Journal extension** — the same authors' JASA 156(5):3353 (2024) "Learning and consolidating the contextualized contour representations of tones from F0 sequences and durational variations via transformers" was confirmed via search (AIP/Semantic Scholar listings); the AIP full text is paywalled (HTTP 403), so its numbers are **not** used here. The Interspeech camera-ready is the authoritative source for every number below.
- **Numbers** — all accuracies are read directly from Table 3 of the PDF. pdftotext mangled the two-block Table 3 layout (segment baselines and the length-ablation share rows); I reconstructed the mapping by matching the "Overall" J-ToneNet values (91.0 / 61.7) that appear in both blocks, which anchor the columns unambiguously. Tagged **✔ corroborated (single-source: camera-ready PDF)** — there is no second public copy with numbers to cross-check, so treat as transcription-verified rather than independently replicated.

**Important framing correction for the task brief:** the task asked for "accuracy vs the ToneNet CNN baseline." J-ToneNet does **not** re-run ToneNet (Gao et al. 2019, this repo's paper #33). ToneNet appears only as cited reference [14]. The in-paper baselines J-ToneNet beats are **Random Forest, FFN, and a 1D-CNN** — the 1D-CNN is the closest stand-in for a ToneNet-style convolutional model. So "vs ToneNet CNN" here means **vs the 1D-CNN segment baseline (52.6% F0 read / 45.4% conversational)**, not a head-to-head against the published ToneNet. This distinction is load-bearing and must not be overstated in a Pebble write-up.

### What the paper actually does

A fully-transformer, **f0-sequence-only** tone classifier for **continuous Mandarin speech**. Pipeline: PRAAT f0 → per-speaker log-normalize to [0,1] (normLogF0) → a BERTSUM-style encoder (**C-Net**, L=4) over the whole-utterance f0 stream with a `[CLS]` per syllable and odd/even interval-segment embeddings → fused via SE-style gating with a **rhythm encoder (R-Net, 2 layers)** over syllable durations → **joint syllable-tone + word-tone cross-entropy loss** (eq. 7). Trained 80/10/10 on two corpora of opposite style: read (FCU-VOICE-100, 23,601 utts) and spontaneous (MCDC-8, 13,407 utts). Headline: **91.0% read / 61.7% conversational tone accuracy**, vs best segment baseline 57.2% / 48.9%; ablations show **utterance context (not the encoder) is the driver** (C-Net alone on isolated syllables = 59.0%), **joint learning adds ~3 pts**, and **R-Net is essential for long read-speech chunks** (≥21 syllables: 91.2 → 73.5 without it).

### Parts directly useful for Pebble (each tagged with Decision IDs)

Pebble's relevant thesis branch is the **VOICE-MESSAGE modality**: a compact, on-device-friendly module that turns a child's spoken voice message into prosodic signal feeding the emotion/severity heads. J-ToneNet is the cleanest published recipe for a **small transformer over an f0 contour sequence**.

1. **f0-contour-only input + per-speaker normLogF0 normalization** (§5.1: log f0, normalize to [0,1] using 0.1%/99.9% percentiles; fixed 20-point interpolation per segment). **→ D-D (severity/energy regression — transfer source & input representation), D-H (datasets / feature substitutes).** This is a complete, cheap recipe for the f0 front-end of a Pebble voice-prosody head: PRAAT/librosa f0 → log → per-speaker min/max normalize → resample to fixed length. **Transfer risk:** the percentile-based per-speaker normalization needs *enough voiced frames per speaker* to estimate the 0.1/99.9 range; a single short child voice message may not give a stable range → Pebble would need a running per-child range or a population fallback. The contour pipeline transfers; the *normalization calibration* does not transfer turnkey.

2. **BERTSUM-style multi-`[CLS]` encoder with interval-segment embeddings over a non-text sequence** (§5.3: `[CLS]` per unit, `[SEP]` boundaries, odd/even `E_A`/`E_B` segment ids, sinusoidal positions, L=4, d=512). **→ D-A (encoder backbone — evidence a small bespoke transformer beats CNN/RF on contour data), D-B (multi-task structure).** Demonstrates that BERT's *input architecture* (the embedding-sum + special-token scheme), not a pretrained BERT checkpoint, is what carries the contour-modeling. **Transfer risk:** this is an **acoustic** encoder, fully separate from NeoBERT (the text encoder). It can only be a **parallel modality tower**, not a head on NeoBERT. Adopting it means committing to a multi-tower fusion architecture, which v1 (text-only) does not have.

3. **Joint multi-task loss = syllable-level + word-level CE on the same shared encoder** (eq. 7; ablation: +3.3 pts read, +3.1 conversational). **→ D-B (MTL loss balancing).** Concrete evidence that adding a *coarser-grained auxiliary head* (word-tone) that shares the encoder with the *fine-grained head* (syllable-tone) consolidates representations and lifts the fine head — a clean small-scale analogue of Pebble's emotion(12-label) + severity(regression) co-training. **Transfer risk:** here the two heads are the *same label family at two granularities* (tone), so they are naturally aligned; Pebble's emotion vs severity heads are *different label families* with different scales — the "auxiliary coarse head helps the fine head" result may not transfer when the tasks are not nested. Use as motivation for a *granularity-nested auxiliary head*, not as proof that arbitrary MTL helps.

4. **Length-stratified evaluation** (Table 3: accuracy reported separately for ≤2 / 3–20 / ≥21 syllable utterances). **→ D-G (threshold/recall-floor + eval policy).** The single most reusable *evaluation* idea: report metrics **stratified by input length**, because the model's behavior inverts with length (read speech improves with length; conversational degrades). **Transfer risk:** none — this is a pure evaluation-hygiene practice and transfers directly to Pebble's turn-level scoring (stratify by turn token-length and by conversation position).

5. **R-Net rhythm/duration auxiliary tower** (§5.4: duration + (duration − mean) sequences, 2-layer transformer, fused via SE gating). **→ D-D (energy/arousal proxy from prosody), D-B.** Speech-rate / rhythm is exactly the kind of signal Pebble's heuristic `energy` dimension wants. **Transfer risk:** R-Net helped read speech but gave "small/ambiguous" gains on spontaneous speech — and a child voice message is **spontaneous**, not read. The component that most resembles what Pebble needs (rhythm→arousal) is the one that *failed to generalize to spontaneous speech in this very paper.*

### How each part helps Pebble succeed

- **Stand up a `voice-prosody` feature module (point 1) as the v2 voice-message front-end.** Concrete artifact: a preprocessing function `f0_contour(wav) -> normLogF0[N]` (PRAAT/librosa f0 → log → per-speaker percentile normalize → fixed-length resample). This is the minimal, validated input recipe; it gives the voice modality a numeric contour the rest of the stack can consume. **(D-D, D-H)** Ship it behind a feature flag, text-only stays v1.
- **Prototype an `f0-transformer` tone/prosody head (point 2) as a separate modality tower, fused late.** Concrete artifact: a 4-layer, d=512 encoder mirroring C-Net (multi-`[CLS]`, sinusoidal pos, `[VAL]`/`[NAN]` tokens), trained first on a public Mandarin/tone or pitch corpus to validate the pipeline, then re-targeted to a prosody-→-emotion mapping. Its embedding is concatenated with NeoBERT's `[CLS]` at the fusion layer — **not** injected into NeoBERT. **(D-A, D-B)**
- **Adopt the granularity-nested auxiliary-head pattern (point 3) in the emotion head.** Concrete artifact: alongside the 12-label fine emotion head, add a coarse 3-way (positive/negative/neutral, the GoEmotions sentiment grouping) auxiliary head sharing the encoder, with summed CE — the direct analogue of J-ToneNet's syllable+word loss. Measure whether the coarse head lifts fine-label macro-F1 the way word-tone lifted syllable-tone (+3 pts). **(D-B)**
- **Make length-stratified reporting mandatory in the eval harness (point 4).** Concrete artifact: every eval table reports metrics bucketed by turn length (and conversation position). J-ToneNet shows a model can look fine on average while inverting by length — Pebble's recall-floor on severity must hold *within each length bucket*, not just overall. **(D-G)**
- **Treat R-Net (point 5) as the design seed for the `energy` heuristic's eventual learned replacement — but validate it on spontaneous child speech first.** Concrete artifact: a duration/rhythm feature `(dur, dur−mean)` per word, fed to a tiny transformer, mapped to the `energy` dimension. Gate its promotion from heuristic to learned on whether it beats the heuristic *on spontaneous speech*, given this paper's warning. **(D-D)**

### Child mental-health lens

- **Direct authorial endorsement of the child use-case.** The paper's closing remark (concluding remark d) explicitly names "clinical applications of screening children's speech on tone production" as a target — a rare on-paper bridge from tone modeling to child-facing screening. This is citable support for Pebble's voice-message thesis branch existing at all.
- **The modality is prosody, not lexical content — a privacy and register advantage.** An f0 contour carries *how* a child speaks, not *what words*; for a child-facing product, a prosody tower that never needs a transcript is a smaller PII surface than ASR-then-text. The normLogF0 pipeline (point 1) is transcript-free by construction.
- **Transfer-validity ceiling: this is Mandarin tone, not affect, and mostly read adult speech.** Every number here is *lexical-tone identity* (which of 4 tones), not *emotional state*. The mapping from f0 contour → emotion/arousal is a different, unproven task; J-ToneNet validates the *encoder over f0 contours* machinery, not the prosody→affect target. And the strong numbers (91%) are **read** speech from **adult university students**; child spontaneous speech is the regime where this paper itself underperforms (61.7%).
- **The failure mode is exactly Pebble's regime.** Spontaneous, longer, naturalistic speech — the closest analogue to a child talking freely into a companion app — is where accuracy fell to ~62% and where the rhythm component (R-Net) stopped helping. Pebble must not assume the read-speech gains carry over; the honest prior for child spontaneous prosody is "hard, near the conversational numbers."
- **Mitigations / ethics.** (1) Keep the voice tower **strictly v2 and behind a flag**; do not let an unvalidated prosody signal touch the safety/severity decision in v1. (2) Per-speaker f0 normalization is implicitly a *biometric* per-child profile — store as ephemeral per-session range, not a persisted voiceprint. (3) Any child-speech tone/prosody screening claim needs clinical/ethics review (the authors call their own results "preliminary"); Pebble should mirror that humility.

### Limitations & open questions for Pebble

- **Contradiction vs the task brief (and vs paper #33 ToneNet):** J-ToneNet is **not** benchmarked against ToneNet (#33). ToneNet reports ~99.16% on *isolated-syllable clean SCSC* data (mel-spectrogram CNN); J-ToneNet reports 91.0% read / 61.7% conversational on *f0-only, continuous* speech. These numbers are **not comparable** — different inputs (spectrogram vs f0), different units (isolated vs continuous), different corpora. Anyone citing "J-ToneNet beats ToneNet" would be wrong. The defensible claim is narrower: *on f0-only continuous-speech tone classification, a BERTSUM-style transformer with rhythm fusion and joint learning beats RF/FFN/1D-CNN segment baselines by 12–34 points.*
- **Single-source numbers.** No public second copy carries Table 3 (ISCA page is abstract-only; the JASA extension is paywalled). Numbers are transcription-verified from the camera-ready, not independently replicated — flag as such in any Pebble citation.
- **Gap vs Pebble's text-only v1 architecture.** J-ToneNet is an *acoustic* tower; nothing in it can be a head on NeoBERT. Adopting any of it forces a multi-tower fusion design that v1 does not have and `docs/decisions.md` does not yet provision. This is a v2-scope dependency, not a v1 lever.
- **No affect labels anywhere.** The paper proves f0→*tone-identity*; Pebble needs f0→*affect/severity*. There is no dataset in this paper that supplies emotion/severity targets for the prosody tower, so D-H gains nothing on the *label* side — only the *feature pipeline* transfers. Open question: what public corpus pairs child (or at least spontaneous) speech f0 with affect/arousal labels? J-ToneNet does not answer it.
- **R-Net's spontaneous-speech weakness undercuts the energy-head plan.** Pebble wanted prosodic rhythm as a learned `energy` signal; this paper's rhythm tower is precisely the component that did *not* generalize to spontaneous speech. Open question for Pebble: does a duration/rhythm encoder beat the v1 `energy` heuristic on *spontaneous child* speech, or does the heuristic stay competitive? Must be tested before any promotion.
