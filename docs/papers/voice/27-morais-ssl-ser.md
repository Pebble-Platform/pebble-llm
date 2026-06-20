# Paper 27 — Speech Emotion Recognition using Self-Supervised Features

## 1. Bibliographic info

**Title:** Speech Emotion Recognition using Self-Supervised Features

**Authors:** Edmilson Morais (Edmilson da Silva Morais), Ron Hoory, Weizhong Zhu, Itai Gat, Matheus Damasceno, Hagai Aronowitz — all IBM Research AI.

**Year / venue:** ICASSP 2022 (IEEE International Conference on Acoustics, Speech and Signal Processing), pp. 6922–6926. Preprint arXiv:2202.03896.

**Index terms (verbatim):** "Speech emotion recognition, self-supervised features, end-to-end systems."

**One-line summary:** A modular Upstream (self-supervised acoustic encoder) + Downstream (pooling + linear classifier) SER system that, with careful fine-tuning, checkpoint averaging, and an ECAPA-TDNN aggregator, reaches speech-only SOTA on IEMOCAP (77.76% UA) — matching a strong audio+text multimodal baseline (78.30% UA).

## 2. Why this paper is in the Pebble set

Pebble's thesis has a **voice-message modality**: children may send short spoken clips rather than typed text. For that path Pebble needs an **acoustic emotion encoder**, and the first design decision is *which self-supervised speech backbone* to stand up (wav2vec 2.0 vs HuBERT vs WavLM) and *what downstream head* to bolt on. This paper is a clean, controlled baseline matrix for exactly that choice on English speech: it isolates the contributions of (a) the SSL backbone, (b) fine-tuning the backbone vs freezing it, (c) the frame→utterance pooling/aggregator, (d) checkpoint averaging, and (e) backbone fusion — all on the canonical IEMOCAP benchmark with the standard SUPERB split. It is the audio-side analogue of the text-encoder bake-off Pebble runs for NeoBERT/ModernBERT/MentalBERT (D-A).

This paper is **not** about child speech, not about mental-health speech, and not about turn-level mid-conversation scoring — it is adult acted/dyadic-conversation English. Its value to Pebble is the *method and the relative ranking of design choices*, not the absolute IEMOCAP numbers.

## Deep research — full-PDF read (2026-06-16)

### Source-access note

Read from the local PDF `docs/papers/pdfs/27-morais-ssl-ser.pdf` via `pdftotext` (full body, all sections, Table 1 and Table 2 transcribed verbatim). The Read tool cannot render PDFs, so text extraction was done with `pdftotext "27-morais-ssl-ser.pdf" -`.

Provenance validation:
- **Venue / identity** — WebSearch (`Morais Hoory "Speech Emotion Recognition using Self-Supervised Features" ICASSP 2022 IEMOCAP wav2vec HuBERT 77.76`) resolved the paper to ICASSP 2022, pp. 6922–6926, arXiv:2202.03896, IBM Research AI authorship. URL: https://arxiv.org/abs/2202.03896 and https://www.semanticscholar.org/paper/3e8ac2a46b83498ddd171c179ad97763271908c6 . Status: ✔ corroborated.
- **Abstract claim** (speech-only matches speech+text multimodal SOTA) — WebFetch on https://arxiv.org/abs/2202.03896 confirmed the abstract's central claim and the ICASSP 2022 / 5-page / 2-table structure. Status: ✔ corroborated.
- **Numeric details** (Table 1 WACC/UACC per experiment; Table 2 SOTA comparison) — these live only in the PDF body. The local PDF is the arXiv version of record; the abstract and venue are corroborated and consistent, so the in-table numbers are taken from the extracted PDF text and tagged ≈ (single-source: present in the authoritative arXiv PDF, not independently re-derivable from a second venue copy). No preprint-vs-published delta was found.
- **Cross-reference for the WavLM gap** — WebSearch (`SUPERB benchmark wav2vec2 HuBERT WavLM IEMOCAP emotion recognition`) confirmed that WavLM is a *later/parallel* SSL model benchmarked elsewhere (EmoBox, the wav2vec2/HuBERT SUPERB benchmark arXiv:2111.02735) but is **not** in this paper. URL: https://arxiv.org/abs/2111.02735 , https://arxiv.org/pdf/2406.07162 (EmoBox). Status: ✔ corroborated that WavLM is absent here.

**Important scope correction vs the task brief.** The brief asked for "wav2vec2 vs HuBERT vs WavLM" and "which layers helped." This paper compares only **wav2vec 2.0 and HuBERT** (no WavLM) and runs **no per-layer / layer-weighting analysis** (it fine-tunes the whole backbone and averages checkpoints; it never reports which transformer layer carries emotion). Both are surfaced below as explicit gaps, with the external sources (SUPERB benchmark, EmoBox) that Pebble must consult to complete the WavLM and layer-selection corners of the matrix.

### What the paper actually does

**Problem framing (§2).** SER as a mapping from continuous speech `S` to a discrete categorical emotion `E`, using the **Upstream + Downstream** paradigm (the speech analogue of BERT-style pretrain-then-head): the Upstream is a task-independent, self-supervised, frozen-or-fine-tuned acoustic encoder (front-end / feature extractor); the Downstream is a task-dependent back-end that aggregates frame-level features to an utterance embedding and classifies it.

**Upstream models compared (§2):** the latest release of **Wav2Vec 2.0** (the "Robust wav2vec 2.0" release, ref [14], arXiv:2104.01027) and **HuBERT** (Hidden-Unit BERT, ref [17], arXiv:2106.07447). A standard **filter-bank (Fbank)** and a fine-tuned **BERT** (text) serve as baselines (§3.2). **No WavLM, no data2vec, no Whisper.**

**Downstream models (§2):** two variants —
1. **Mean Average Pooling** aggregator → Linear Classifier (LC).
2. **ECAPA-TDNN** aggregator [20] → Linear Classifier. ECAPA-TDNN is borrowed from speaker verification: emphasized channel-attention, multi-layer feature propagation and aggregation, with attentive statistics pooling.

**Dataset (§2.1): IEMOCAP** [21], ~12 h multimodal dyadic conversation, 5 sessions, 10 speakers. Following prior work, only `angry`, `happy`, `excited`, `sad`, `neutral` utterances are used, and **`excited` is merged into `happy`** → 4-class problem, **5,531 utterances** (happy 1,636, angry 1,103, sad 1,084, neutral 1,708). Evaluation is **leave-one-session-out 5-fold CV**: each fold uses 2 speakers for test, the other 8 speakers' samples split 80/20 train/val. **The split is identical to SUPERB's** [18] (train/val/test per fold).

**Fine-tuning recipe (§2.2):** each Upstream model is fine-tuned *jointly* with a simple Mean-Pooling + Linear-Classifier head on IEMOCAP categorical labels, separately for each of the 5 folds → 5 fine-tuned Upstream models (one per fold).

**Checkpoint averaging (§2.3):** to cut output variance, the **5 best fine-tuned checkpoints** (selected purely on validation accuracy; test never observed) are **weight-averaged** [22] — done per fold, for both wav2vec 2.0 and HuBERT → 10 "FT-AVG" Upstream models. The same averaging is applied to the Downstream model checkpoints.

**Experiment grid (§3.1, Figure 3 / Figure 4, Table 1):**
- Exp 1–2: W2V2 / HuBERT, Mean pooling, **no** averaging of either model.
- Exp 3–4: W2V2 / HuBERT, Mean pooling, **both** Upstream + Downstream averaged.
- Exp 5–6: W2V2 / HuBERT, **ECAPA-TDNN** aggregator, both averaged.
- Exp 7: **early fusion** of HuBERT + W2V2 features (concatenated before the single ECAPA-TDNN).
- Exp 8: **late fusion** of two ECAPA-TDNN utterance embeddings (one on W2V2, one on HuBERT).
- Exp 9 (baseline): Fbank → ECAPA → LC (no SSL, audio).
- Exp 10 (baseline): BERT (text, on ground-truth transcripts) → ECAPA → LC.
- Exp 11 (baseline): Fbank & BERT late fusion (audio+text).

**Results — Table 1 (WACC = weighted accuracy, UACC = unweighted accuracy; both %):**

| Set | # | Modality | Upstream (FT / AVG) | Downstream (AGG / AVG) | WACC | UACC |
|---|---|---|---|---|---|---|
| 1.A | 1 | S | W2V2 (FT, no AVG) | Mean (no AVG) | 74.09 | 74.56 |
| 1.A | 2 | S | HuBERT (FT, no AVG) | Mean (no AVG) | 72.99 | 73.45 |
| 1.A | 3 | S | W2V2 (FT, AVG) | Mean (AVG) | 76.47 | 76.86 |
| 1.A | 4 | S | HuBERT (FT, AVG) | Mean (AVG) | 75.20 | 75.80 |
| 1.B | 5 | S | W2V2 (FT, AVG) | ECAPA (AVG) | 76.58 | 77.36 |
| 1.B | 6 | S | HuBERT (FT, AVG) | ECAPA (AVG) | 75.56 | 77.04 |
| 1.B | 7 | S | **HuBERT + W2V2 (early fusion, FT, AVG)** | **ECAPA (AVG)** | **77.07** | **77.76** |
| 1.B | 8 | S | HuBERT & W2V2 (late fusion, FT, AVG) | ECAPA (AVG) | 76.78 | 77.52 |
| 2 | 9 | S | Fbank (no FT) | ECAPA (AVG) | 56.52 | 57.60 |
| 2 | 10 | T | BERT (FT, AVG) | ECAPA (AVG) | 69.34 | 70.07 |
| 2 | 11 | S+T | Fbank & BERT (late fusion) | ECAPA (AVG) | 70.56 | 71.46 |

All Table 1 numbers ≈ (authoritative arXiv PDF, single-source).

**Results — Table 2 (SOTA comparison, UACC %, 5-fold CV IEMOCAP):**

| # | Method | Modalities | UACC |
|---|---|---|---|
| 1 | Sajjad et al. [23] | Audio | 72.25 |
| 2 | Wang et al. [24] | Audio | 73.30 |
| 3 | Liu et al. [25] | Audio | 70.78 |
| 4 | Zhao et al. [26] | Audio | 71.70 |
| 5 | Wu et al. [6] | Audio + Text | 78.30 |
| — | **Ours (exp. 7)** | **Audio** | **77.76** |

All Table 2 numbers ≈ (authoritative arXiv PDF, single-source).

**Discussion / ablation observations (§4.1), verbatim deltas:**
1. **Checkpoint averaging** (exp 3,4 vs 1,2): +**2.38%** WACC for W2V2, +**2.21%** WACC for HuBERT. (Averaging both Upstream and Downstream.)
2. **ECAPA-TDNN vs Mean pooling** (exp 5,6 vs 3,4): ECAPA "slightly outperforms" mean pooling. (Numerically: W2V2 76.58 vs 76.47 WACC; HuBERT 75.56 vs 75.20.)
3. **Early vs late backbone fusion** (exp 7 vs 8): early fusion of HuBERT+W2V2 features **outperforms** late fusion (77.07 vs 76.78 WACC; 77.76 vs 77.52 UACC).
4. **SSL vs Fbank** (any of exp 1–8 vs exp 9): SSL beats hand-crafted filter-bank "by a very large margin" (best 77.07 vs 56.52 WACC ≈ **+20 points**).
5. **SSL audio vs fine-tuned BERT on gold transcripts** (set 1.B vs exp 10): the best audio-only SSL beats text-BERT by "around 6%" (77.07 vs 69.34 WACC).
6. **SSL audio vs Fbank+BERT multimodal baseline** (set 1.B vs exp 11): audio-only SSL beats the audio+text baseline by "around 5%" (77.07 vs 70.56 WACC).
7. **Headline** (Table 2): exp 7 (audio-only, 77.76 UACC) ≈ the strongest *audio+text* literature baseline (Wu et al. 78.30) and is "the best result reported so far for SER using 5-fold CV on IEMOCAP for the case of speech-only input."

**What is NOT in the paper:** no WavLM/data2vec/Whisper; no per-layer or layer-weighting analysis (whole-backbone fine-tuning only); no base-vs-large size sweep reported as a table; no per-emotion confusion or per-class F1; no calibration; no learning-rate / freeze-vs-fine-tune table (fine-tuning is always on); no inference-latency or model-size numbers.

### Parts directly useful for Pebble

Each tagged with the Decision ID it moves and a transfer-risk note.

1. **Backbone bake-off as the audio-encoder selection method (D-A).** The Upstream+Downstream paradigm with a fixed downstream and a swappable SSL front-end is the exact protocol Pebble should run to pick its voice-message encoder. Here W2V2 ≥ HuBERT in every matched cell (exp 1>2, 3>4, 5>6), but the gap is small (≤1.3 WACC) and the **fusion of the two** wins — so the "right" answer is a small matrix, not a single pick. *Transfer risk: medium.* The ranking is on adult acted English; on child spontaneous speech the order can flip (child-speech ASR literature generally favors models pretrained on more diverse/robust audio). The *method* transfers cleanly; the *winner* must be re-measured on child data.

2. **Downstream head = aggregator + linear classifier; ECAPA-TDNN ≥ mean pooling (D-A, D-B).** The frame→utterance pooling is the load-bearing downstream choice. ECAPA-TDNN (attentive statistics pooling with channel attention) edges mean pooling at equal cost. For Pebble's voice head, this says: start with mean pooling for the cheap baseline, but budget an attentive-pooling variant. *Transfer risk: low.* Pooling choice is task-agnostic; the small ECAPA gain is plausibly robust, though on very short child clips attentive pooling has less to attend to.

3. **Checkpoint (weight) averaging for variance reduction: +2.2–2.4% WACC (D-B, D-E).** Averaging the 5 best validation checkpoints of the fine-tuned backbone (and the downstream) is the single largest "free" gain in the paper — larger than the ECAPA-vs-mean or early-vs-late-fusion deltas. This is a generic fine-tuning trick (it is *not* audio-specific) and applies equally to Pebble's **NeoBERT text encoder** fine-tuning, not just the voice head. *Transfer risk: low.* Weight averaging of checkpoints from the same run is architecture-agnostic and cheap; it stabilizes silver-label-noisy fine-tuning, which is precisely Pebble's regime.

4. **Early > late multimodal/multi-backbone fusion (D-A, D-H).** Early fusion (concatenate features, one aggregator) beat late fusion (separate aggregators, fuse embeddings). If Pebble ever fuses audio+text (voice clip + ASR transcript) or two acoustic backbones, the default should be early/feature-level fusion. *Transfer risk: medium.* Demonstrated only on two acoustic SSL streams; audio+text fusion with a strong text encoder may behave differently (the multimodal SER literature is mixed), so treat as a default-to-try, not a law.

5. **The SUPERB-identical 5-fold leave-one-session-out split + WACC/UACC dual metric (D-D, D-H).** Reporting both weighted and unweighted accuracy on a speaker-disjoint split is the right evaluation hygiene for an imbalanced emotion benchmark, and matching SUPERB makes results comparable. Pebble's voice-head eval should adopt **speaker-disjoint folds** and **report UA (macro/unweighted) alongside WA**, because child emotion classes will be imbalanced just like IEMOCAP. *Transfer risk: low.* Pure evaluation methodology; transfers directly. The speaker-disjoint discipline is *more* important for Pebble, where overfitting to a few child voices is a real risk.

6. **SSL beats hand-crafted features by ~20 points (D-A).** Fbank→ECAPA (exp 9) collapses to 56.52 WACC vs 77.07 for SSL. This is the empirical justification for using a pretrained SSL encoder at all rather than MFCC/Fbank + a from-scratch net. *Transfer risk: low.* The "use SSL, not hand-crafted features" conclusion is robust across the SER literature and almost certainly holds for child speech too.

### How each part helps Pebble succeed

- **Voice-head encoder selection (D-A).** Stand up a `voice_encoder` benchmark harness that mirrors this paper: fixed downstream (mean pooling → linear), swap the Upstream among {wav2vec2-base/large, HuBERT-base/large, **WavLM-base/large — which this paper omits but SUPERB/EmoBox show is often the SER leader**}, fine-tune each, report WA+UA on speaker-disjoint folds. Use this paper's relative deltas as priors: expect ECAPA ≈ mean + ~0.2–1%, checkpoint-avg ≈ +2%, early-fusion ≈ +0.3%. Concrete artifact: `experiments/voice_encoder_bakeoff/` producing a Table-1-shaped CSV.
- **Cheap stability win, both heads (D-B, D-E).** Add **checkpoint weight-averaging** (average the top-k validation checkpoints of a single run) to Pebble's standard fine-tuning loop — for the NeoBERT text encoder AND any voice encoder. The paper measures +2.2–2.4% on a noisy 4-class task; under Pebble's silver-label noise this variance reduction is exactly the right tool, and it costs only checkpoint storage. Concrete artifact: a `--avg-top-k` flag in the trainer + report the with/without delta as an ablation row.
- **Pooling head design (D-A, D-B).** Implement the voice classifier head as `aggregator → linear`, with aggregator pluggable between `mean` and `ECAPA-TDNN`. Ship mean pooling as v-baseline; keep ECAPA as the upgrade. This matches Pebble's `emotion` (12-label) and `severity` (regression) heads, which would each sit on top of the shared utterance embedding.
- **Fusion default (D-A, D-H).** If/when Pebble fuses a child's voice clip with its ASR transcript (text → NeoBERT) for emotion/severity, default to **early feature-level concatenation before the shared head**, per exp 7 > exp 8. Concrete artifact: an `early_fusion` config that concatenates pooled audio embedding + NeoBERT [CLS] before the heads.
- **Evaluation hygiene (D-D, D-H).** Adopt **speaker-disjoint CV** and **dual WA/UA reporting** as the voice-head's standard scorecard; this is also the right frame for the severity-regression voice path (D-D's Pearson metric should be reported per-speaker-fold to avoid speaker leakage inflating it).
- **Don't ship Fbank (D-A).** The 20-point SSL-over-Fbank gap is the citation that justifies the GPU/integration cost of an SSL encoder in the voice path rather than a lightweight spectral-feature MLP.

### Child mental-health lens

- **Domain transfer is the central risk.** Every number here is **adult, acted/elicited, English, studio-quality dyadic conversation** (IEMOCAP). Pebble's voice messages are **children, spontaneous, in-the-wild (phone mic, background noise), possibly short**, and emotionally about distress/safety rather than the acted angry/happy/sad/neutral palette. The 77.76 UA is **not a target Pebble should expect to hit on child data** — child-speech SER consistently underperforms adult SER, and IEMOCAP's 4 acted classes are not Pebble's 12 GoEmotions-mapped emotions or its severity scale. Use the paper for *method ranking*, never as an absolute bar.
- **Backbone pretraining data matters more for children.** wav2vec2/HuBERT are pretrained on adult read/conversational English (LibriSpeech/Libri-Light). Child fundamental frequency, formants, and speaking rate are out-of-distribution. This is precisely where **WavLM** (pretrained with more speaker/noise augmentation and overlapping speech) tends to win on robustness — and this paper *omits it*. Pebble's bake-off must include WavLM and, ideally, a child-speech-adapted continued-pretraining pass (the audio analogue of D-F's domain-adaptive MLM).
- **Severity from voice is the higher-stakes, under-evidenced path.** This paper does categorical emotion only. Pebble's `severity` head (regression) on voice has **no support here** — prosodic distress intensity from child speech is a genuinely open problem and must not inherit the categorical numbers' optimism. Treat the voice severity path as exploratory; keep the v1 child-facing safety decision text-led and heuristic, not voice-model-led.
- **Privacy/ethics of child voice.** Raw child audio is far more identifying than text (voiceprints, background speakers, location cues). Any voice path needs on-device or tightly-controlled processing, deletion-by-default of raw audio after embedding, and guardian consent — a stricter regime than the text pipeline. SSL embeddings are not anonymous; treat them as PII.
- **Mitigations.** (1) Re-measure the whole matrix on a child-speech emotion set before trusting any ranking. (2) Include WavLM and a noise-robust backbone. (3) Add child-speech continued self-supervised pretraining if any unlabeled child audio is available. (4) Report UA/macro and per-class recall (not just WA) so rare distress classes aren't masked by a happy/neutral majority — the same recall-floor discipline Pebble applies to text.

### Limitations & open questions for Pebble

- **Contradiction/gap vs the task brief and vs the broader SER literature — WavLM is absent.** The brief framed this as a "wav2vec2 vs HuBERT vs WavLM" matrix; the paper only has wav2vec2 and HuBERT (WavLM postdates/parallels it). The SUPERB/EmoBox benchmarks (arXiv:2111.02735, EmoBox arXiv:2406.07162) frequently rank **WavLM-large at or above HuBERT/wav2vec2 for SER**. So this paper's "W2V2 ≥ HuBERT" finding is **incomplete and possibly superseded** for backbone selection — Pebble cannot pick its voice encoder from this paper alone; it must run the third column (WavLM) itself.
- **No layer analysis — contradicts the "which layers helped" framing.** The brief asked which layers carry emotion; this paper fine-tunes the *whole* backbone and averages checkpoints, never inspecting per-layer contributions. The SUPERB ER protocol (frozen backbone + learned layer-weighting) is the standard way to see "which layers helped," and it generally finds **mid-to-upper transformer layers** most emotion-bearing. Pebble's bake-off should add a frozen+layer-weighted variant to recover this signal, since fine-tuning the full backbone is expensive and may be unnecessary if a few layers + pooling suffice.
- **Frozen-vs-fine-tuned is not ablated.** Fine-tuning is always on here; the paper never reports the (much cheaper) frozen-backbone SUPERB-style number, so Pebble has no guidance on the compute/accuracy trade for freezing — a real question given child-voice data scarcity (fine-tuning a large SSL model on few child clips risks overfitting; frozen + small head may transfer better).
- **Tiny, acted benchmark.** 5,531 utterances, 10 speakers, 4 acted classes. Speaker-fold variance is large; "slightly outperforms" deltas (ECAPA vs mean, 0.11 WACC) are within plausible noise. Pebble should treat sub-1% deltas here as ties, not orderings.
- **No calibration, no probabilities-for-decisions.** Like several Pebble-set papers, accuracy-only reporting; Pebble's Decision Engine needs calibrated severity/emotion probabilities from the voice path, which this paper does not address.
- **Cross-modal contradiction worth flagging vs Pebble's text-first plan.** The paper shows audio-only SSL beating a fine-tuned BERT on *gold transcripts* by ~6% (exp set 1.B vs exp 10). If that held for child distress, it would argue voice > text — but it almost certainly does **not** transfer: the BERT baseline here is deliberately under-tuned ("may not follow the most advanced SOTA techniques"), the transcripts are acted-emotion-laden, and Pebble's text path uses a domain-adapted NeoBERT, not a weak BERT. Pebble should keep text as the primary modality and treat voice as an additive signal, not a replacement, until measured on child data.
- **Open question for Pebble.** Is there *any* licensed child-speech emotion/distress corpus to anchor the bake-off? Without one, the voice path stays a research spike and the v1 child-facing decision remains text-led. Worth scoping a small in-house child-voice calibration slice (with consent) the way Pebble plans a child-register text calibration slice.
