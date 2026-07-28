# Paper 11 — Bridging Text and Speech for Emotion Understanding: Explainable Multimodal Transformer Fusion with Unified Audio–Text Attribution

- **Authors:** Ashutosh Pandey, Jasmeet Singh, Maninder Kaur
- **Venue / year:** Journal of Intelligence (MDPI), 13(12):159, 2025 (CC-BY; mirror PMC12733550)
- **Links:** abs https://www.mdpi.com/2079-3200/13/12/159 · PDF `pdfs/11-bridging-text-speech-fusion.pdf`
- **Group:** survey / benchmark (fusion framework)

**Summary:** RoBERTa (text) + WavLM (audio) chiếu vào latent space chung; attribution Integrated-Gradients/Occlusion tách phần đóng góp linguistic vs acoustic.

**Relevance to Pebble:** Kiến trúc audio+text fusion cụ thể + phương pháp explainability chuyển được sang voice-mode. Venue tier thấp hơn IEEE/Interspeech — rank vì topical fit.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Profile assembled at analysis time** (from `docs/intent/constraints.md` + `docs/spec/capabilities/voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`):
Pebble = a primary **ordinal suicide-risk text** program (BERT-family encoder, teacher-LLM silver labels, strict gold-holdout + subject-level splits, ordinal-aware QWK/MAE) **plus** an adjacent active **voice** stream: a frozen WavLM-Large / emotion2vec backbone with **three heterogeneous MTL heads** — emotion (CE), affect (valence+arousal, CCC loss), crisis (BCE under a **hard recall floor ≥0.90**) — balanced by **Kendall uncertainty weighting**; voice+text fusion is the named forward direction. This paper is a **single-head, end-to-end late-fusion** emotion classifier (RoBERTa-base + WavLM-Base-Plus) on MELD, 5 categories, with post-hoc XAI attribution.

**Per-dimension scores (before the number):**
- **D1** (multi-task heterogeneous heads; w=3) = **0** — one classification head over 5 emotion categories; no continuous/regression head, no safety head, no MTL at all.
- **D2** (mental-health / crisis domain; w=2) = **0** — generic conversational emotion (MELD / "Friends" TV); mental health is only rhetorical framing in the intro.
- **D3** (emotion-transfer corpora; w=1) = **1** — MELD is a categorical emotion corpus usable for Pebble's emotion head, though not one of the listed GoEmotions/EmpatheticDialogues/intensity sets.
- **D4** (teacher-LLM silver-label distillation; w=2) = **0** — human-annotated MELD labels only; no distillation.
- **D5** (principled MTL loss balancing; w=2) = **0** — plain cross-entropy, single objective; no uncertainty/GradNorm/PCGrad.
- **D6** (safety/crisis recall constraint as objective; w=2) = **0** — per-class recall is reported, but no recall-floor constraint drives training/thresholding.
- **D7** (encoder backbone match; w=1) = **2** — WavLM-Base-Plus **and** RoBERTa-base directly match both Pebble streams' backbone families.

**Overlap:** `(3·0 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·2) / 26 × 100 = 3/26 × 100` = **12%** — **peripheral (<40%)**.

- **Closest on:** D7 (exact WavLM+RoBERTa backbone match) and, weakly, D3 (MELD as an emotion corpus).
- **Best point (Method to adopt):** the **unified per-modality attribution** — Integrated Gradients on text tokens + Occlusion on fixed audio windows — decomposes a single prediction into linguistic vs acoustic-prosodic evidence.
  - **How to apply to Pebble:** wrap the same IG(text)+Occlusion(audio) pass around the crisis head so every flag raised under the hard recall floor carries a "driven by prosody vs. lexical content" attribution — the clinical-auditability layer a bare recall number can't provide, and the one thing here that a generic fusion recipe doesn't already give us.
- **Caveats:** open-access, full text read (no paywalled sections). Confidence-lowering mismatches, not unread gaps: (1) fine-tuned **end-to-end**, opposite to Pebble's frozen-backbone probe; (2) MELD uses the standard split with **no speaker/subject-disjoint guarantee**, which would violate Pebble's subject-level integrity constraint if reused as-is; (3) statistical power is thin (Wilcoxon p=0.125, 3 seeds); (4) 83% MELD accuracy is a within-distribution number, not a gold-holdout result. The fusion recipe (project 768→256, concat→512, dropout 0.3, 2-layer head; ablation: 128-d bottleneck > 256 > 512) is a usable secondary blueprint when Pebble reaches the fusion forward direction.

## Deep research — full-PDF read (2026-07-10)

> Analyzed against the **current ViEmoSpeech profile + Decision Register V-A…V-H**
> (`docs/tasks/paper-deep-analysis.md`), NOT the archived text-stream profile / D-A…D-H that
> the "Analysis" section above uses. This is the **closest architectural match to our PhoBERT+WavLM
> plan** in the whole related-work set — a BERT-family text encoder + WavLM audio encoder fused for
> categorical emotion — so the read focuses on the exact fusion mechanism, the frozen-vs-fine-tuned
> question, the per-modality contribution numbers (the text-vs-audio dominance evidence), and the
> attribution method as a candidate instrument for our tone×emotion channel-competition figure.

### Source-access note

Read from the local PDF `docs/papers/bimodal-ser/pdfs/11-bridging-text-speech-fusion.pdf` via
`pdftotext` (full 24-page body, all 4 tables, 3 algorithm listings, Eqs 1–6). The local PDF **is
the published venue version** — MDPI *Journal of Intelligence* 13(12):159, DOI
10.3390/jintelligence13120159, published 3 Dec 2025, CC-BY (page footers `J. Intell. 2025, 13, 159`,
received 15 Sep / accepted 28 Nov 2025), so there is no preprint-vs-published delta to reconcile.
Web validation:
- Published record + headline numbers confirmed via WebSearch (`Pandey Singh Kaur "Bridging Text
  and Speech" Journal of Intelligence 2025 …`) → resolved DOI https://doi.org/10.3390/jintelligence13120159
  and PMC mirror https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12733550/ (0.83 accuracy / 5 classes /
  RoBERTa+WavLM / IG+Occlusion — all match the local PDF). The MDPI HTML page itself returns HTTP 403
  to the fetch tool (bot protection), so headline facts are corroborated via the PMC/DOI records + the
  venue-version PDF. **✔**
- Their Table-4 comparison baseline **TelME**: independently checked (WebSearch
  `TelME MELD emotion recognition weighted F1 …` → WebFetch https://arxiv.org/html/2401.12987v2).
  TelME's actual MELD result is **weighted-F1 67.37 on the full 7-class** set, and its **headline metric
  is weighted-F1, not accuracy**. This corroborates that this paper's "TelME 67.4%" row is being
  compared against the proposed model's **5-class accuracy 83%** — a metric-and-class-count mismatch
  (see Limitations). **✔**

### What the paper actually does

**Task / data.** Single-head 5-way categorical emotion classification on **MELD** (spontaneous
dialogue from the sitcom *Friends*). MELD ships 7 emotions; the authors **drop `disgust` and `fear`**
(too few samples, low inter-annotator agreement) leaving **Anger, Joy, Neutral, Sadness, Surprise**
(§3.1, §3.4). Audio pipeline (§3.2, Alg. 1): extract 48 kHz WAV from the video, **DeepFilterNet v2**
neural denoise (default weights, FFT 512 / hop 128), downsample to 16 kHz, per-utterance mean–variance
normalize, pad/truncate to a fixed **8 s (128,000 samples)**. Text: strip non-alphanumerics,
`RobertaTokenizerFast`, fixed **64 tokens**.

**Backbones (§4.1).** Audio = **WavLM-Base-Plus** (7-conv front-end, kernels [10,3,3,3,3,2,2] /
strides [5,2,2,2,2,2,2]; 12 transformer layers, 12 heads × 64-d; FFN 768→3072→768; pre-LN) →
**768-d** speech embedding. Text = **RoBERTa-base** (byte-level BPE ~50k vocab; 12 layers/12 heads;
FFN 768→3072→768; post-LN) → **768-d [CLS]** embedding. *How the WavLM frame sequence is pooled to a
single 768-d vector is never stated* (gap).

**Fusion (§4.2–4.4, the load-bearing mechanism, Eqs 1–4).** Late/feature-level concat:
1. Project each modality into a common subspace: `a' = W_a·a + b_a`, `t' = W_t·t + b_t`, with
   `W_a, W_t ∈ ℝ^{256×768}` → each modality to **256-d** (Eq 1).
2. **Concatenate**: `m = [a'; t'] ∈ ℝ^{512}` (Eq 2), then **dropout p=0.3**.
3. 2-layer MLP head: `h1 = ReLU(W1·m + b1)`, `W1 ∈ ℝ^{256×512}` (Eq 3); `ŷ = W2·h1 + b2`,
   `W2 ∈ ℝ^{C×256}` (Eq 4) → softmax.
There is **no cross-attention, no gating, no query-based alignment** — this is the *simplest possible*
learned fusion (project → concat → MLP), i.e. the "Concat" baseline that stronger designs beat.

**Training (§4.6).** **Fine-tuned end-to-end, NO layers frozen.** AdamW, lr **2e-5**, weight decay
**0.01**, batch **8**/GPU, linear warm-up over first **10%** steps, dropout **0.3**, grad-clip norm
**1.0**, CrossEntropy, max **15 epochs**, early-stop patience **2** on val loss (converged at epoch 4:
train acc 55→87%, val 70→83%, §5.4), **3 seeds (42, 123, 2025)** reported as mean±std. Stack:
transformers **4.41.0**, PyTorch 2.2.0, dual Tesla T4 16 GB.

**Explainability (§4.5, §5.5–5.8, Alg. 3).** **Integrated Gradients** (Sundararajan 2017; steps=10)
applied to **both** text tokens and the audio waveform; **Occlusion** on audio with window
`w = 0.1·fs = 1600 samples (0.1 s)`, stride `s = w/2 = 800`, interpolated back to length. IG(text)
highlights sentiment words ("great", "play", "song") and suppresses function words; IG/Occlusion(audio)
localize prosodic regions per class (Surprise = early/front-loaded burst; Sadness = diffuse sustained;
Anger = early + late spikes). §5.8 reports IG and Occlusion **agree** on voiced/harmonic regions.

**Results.** Multimodal **accuracy 0.83 ± 0.01, macro-F1 0.82 ± 0.01** (5-class, Table 2). Per-class
F1: **Sadness 0.90, Anger 0.85, Surprise 0.85, Joy 0.77, Neutral 0.74** (Table 2). Per-class one-vs-rest
AUC: Anger 0.9389, Joy 0.9089, Neutral 0.9019, **Sadness 0.9623**, Surprise 0.9546 (§5.2). Unimodal vs
multimodal (Table 3): **RoBERTa text-only 0.79 / macro-F1 0.78** (beats BERT 0.75, DistilBERT 0.76);
**WavLM audio-only 0.65 / 0.61** (beats Wav2Vec2 0.60 / 0.57); multimodal **0.83 / 0.82** — a
**+4–5% gain over the best unimodal (text)**. Significance across 3 seeds: **Wilcoxon W=6.00,
p=0.125; Sign test p=0.25** — *both non-significant at α=0.05* (§5.2). Ablation (§4.7): bottleneck
**128 → ~82%**, **512 → ~77%**, 256 "best balance"; **removing DeepFilterNet denoise degrades
accuracy**. SOTA table (Table 4): Proposed 83.0 vs Bi-LG-GCN 80.1 vs TelME 67.4 (see Limitations — a
metric/class mismatch).

### Parts directly useful for ViEmoSpeech (tagged by Decision ID)

1. **[V-A] The exact concat-projection-MLP fusion (Eqs 1–4) = our simplest learned-fusion baseline
   arm.** Project WavLM-768 and PhoBERT-768 each to a shared d (they use 256; ablation says a *smaller*
   128 bottleneck was better), concat → dropout 0.3 → 2-layer ReLU MLP → softmax. This is the minimal
   learned alternative to the withdrawn rule-fusion prior (vn-09) and the *floor* below cross-attention
   (bimodal-03) / gated (WavFusion) / Q-Former (vn-07 FAS). **Status of the numbers: ✔** (Table 2/3,
   venue version).
2. **[V-C] RoBERTa-base config as the direct PhoBERT analogue.** 64-token cap, [CLS] pooling, linear
   project to shared subspace, lr 2e-5, wd 0.01, warm-up 10%. Text-only RoBERTa **0.79/0.78** here is
   the clean-transcript ceiling of the text branch (Table 3, **✔**).
3. **[V-A / V-B] Fine-tuned end-to-end, no frozen layers** (§4.6) — their 0.83 is a *fully-fine-tuned*
   ceiling, not a frozen-probe bar. This is the counter-point to our V-B lean toward a **frozen** WavLM;
   it means their audio-only 0.65 is an *upper* estimate for WavLM's standalone capacity, and a frozen
   WavLM in our stack will sit below it. **✔** (§4.6).
4. **[V-G] Unified per-modality attribution: IG(text tokens) + Occlusion(audio windows)** (§4.5, Alg. 3)
   as a candidate instrument for explaining tone×emotion conflicts, plus the **reporting stack**:
   3-seed mean±std, per-class one-vs-rest AUC, and non-parametric significance tests. **✔** (§5.2, §5.5–5.8).
5. **[V-B] DeepFilterNet-v2 enhancement before the SSL encoder measurably helps** (ablation, §4.7).
   **≈ approximate** (reported as "consistent degradation" when removed, no isolated number).

### How each part helps ViEmoSpeech succeed

- **V-A baseline ladder (→ the method paper's fusion table).** Add this concat-projection-MLP as the
  **"simplest learned fusion" row** directly above the re-implemented vn-09 rule-fusion row and below
  our cross-attention / gated / FAS-style candidates. Concrete config to copy: project both 768-d
  streams to a **small shared dim (128, per their ablation, not 256/512), dropout 0.3, 2-layer ReLU MLP**.
  *Transfer risk (stated):* their **+4–5% multimodal-over-text gain is measured on CLEAN English gold
  transcripts** where text already hits 0.79; under Vietnamese **PhoWhisper ASR with tone-swap errors at
  high arousal** the text branch is degraded, so the *audio contribution in our regime should be larger*
  and this exact +4–5% will not transfer. They also **fine-tune end-to-end**; if we freeze WavLM (V-B),
  the concat baseline can underperform — so run **both frozen and fine-tuned WavLM arms** of the concat
  baseline, don't inherit their number.
- **V-C PhoBERT branch config.** Reuse the 64-token / [CLS] / lr 2e-5 recipe as the PhoBERT branch
  default. *Transfer risk:* their result is the strongest single evidence that **a strong text encoder
  dominates on clean transcripts** — and the strongest reason to **not** assume PhoBERT will dominate on
  our ASR transcripts. Feed the branch **ASR text** (not gold captions) in the primary arm and keep a
  gold-caption arm as the clean-transcript upper bound, so the ASR-noise penalty on the text branch is
  measured, not assumed (V-C is exactly this robustness question).
- **V-G attribution + eval instrument.** Port **Occlusion on aligned audio windows** as one lens for the
  tone×emotion channel-competition figure: occlude a syllable's rime and read the emotion-logit change,
  paired with IG on the corresponding PhoBERT token. Adopt their **3-seed mean±std + per-class
  one-vs-rest AUC** reporting (upgrade to ≥5 seeds per THAI-SER vn-11). *Transfer risk:* their occlusion
  window is a **fixed 0.1 s / 800-sample stride, unaligned to phones** — too coarse to isolate a
  syllable-tone from its emotion; we must **align windows to PhoWhisper syllable boundaries** and, per
  their own §5.8 caveat that attribution similarity "may reflect emotion-dependent correlations …
  rather than explicit cross-modal integration," **never present the attribution picture as proof of
  channel competition** — pair it with a quantitative metric (vn-13 Cramér's V on tone-vs-emotion,
  vn-06 layer-wise Ridge probe). Visual attribution is the illustration, not the measurement.
- **V-B enhancement step.** Their denoise-before-SSL ablation supports keeping an **enhancement stage
  before WavLM**. *Transfer risk:* their DeepFilterNet *removes* noise from clean sitcom audio; our
  Demucs stage *source-separates* to **restore** a music/noise substrate we deliberately keep — different
  goal, so treat "enhancement helps" as directional support only, and A/B our Demucs output vs raw.

### Child mental-health / ViEmoSpeech transfer lens

This is our **backbone pair** (WavLM + a BERT-family encoder), so transfer validity is unusually high on
architecture and unusually low on regime. What transfers and what does not:

- **Register match, language mismatch.** MELD is **acted TV-show dialogue** — the same acted-drama register
  as our VN TV-drama corpus, which is genuinely useful precedent (found/scripted dialogue, spontaneous
  within scenes). But it is **English and non-tonal**, so the paper says **nothing** about the
  tone×emotion F0/phonation competition that is our headline claim (V-D untouched — add to the running
  tally: still **0 of 16 papers** measure lexical-tone×emotion channel competition).
- **The text-dominance number is regime-specific and must not be over-read.** RoBERTa-alone **0.79** ≈
  multimodal **0.83**, audio-alone **0.65** — on **clean gold transcripts**, text carries the task and
  audio adds ~4 pts. This is the **opposite pole** from vn-08's VN-spontaneous-ASR "text near-useless"
  (38–44%). ViEmoSpeech sits between them: PhoWhisper ASR is cleaner than vn-08's setup but tone-corrupted
  at high arousal, and Vietnamese is tonal so the audio branch should carry *more* than MELD's +4 pts.
  ⇒ our method paper must frame audio contribution as **regime-dependent and measured per-register**,
  citing this paper as the clean-English anchor — not as generic "multimodal > unimodal" support.
- **Fine-tuned, not frozen, and not speaker-disjoint.** Two invariant conflicts for us: (a) they
  fine-tune both encoders end-to-end (our V-B leans frozen WavLM), and (b) their evaluation is **not
  speaker-disjoint** (MELD's standard split isn't, and Alg. 2's `RandomSplit(0.8/0.2)` certainly isn't) —
  which would violate our speaker-disjoint / whole-series-holdout invariant (ADR-002) if reused as-is.
  Their 0.83 is a within-distribution, non-speaker-disjoint number; our honest speaker-disjoint anchor
  will be lower (cf THAI-SER WA ~60, MSP naturalistic macro-F1 ~0.30).
- **No dimensional / distress output.** Purely 5-way categorical; no valence/arousal-CCC, no distress
  head — moves nothing for V-D (dimensional) or V-F (distress). The clinical framing is one sentence in
  the conclusion ("mental-health platforms could support emotional self-awareness"), with no clinical
  label — the same acted-categorical-emotion-with-clinical-veneer pattern V-F names as an anti-pattern.
- **Dropping the hard rare classes is a lesson against, not for.** They drop `fear` and `disgust` for low
  N / low agreement — directly opposite to our **≥50-clip rare-class floor** (ADR-002). Our design keeps
  rare classes with a floor and honest per-class reporting rather than deleting them to inflate accuracy.

### Limitations & open questions for ViEmoSpeech (incl. explicit contradiction/gap)

- **CONTRADICTION vs vn-08 and the cross-cutting synthesis (text-vs-audio dominance).** This paper's clean
  text dominance (RoBERTa 0.79 ≈ multimodal 0.83; audio 0.65) is the **direct opposite** of vn-08's
  "text near-useless" (38–44% VN ASR) and confirms cross-cutting synthesis point #1: **dominance is
  register/language-dependent, not settled.** It anchors the *clean-transcript, non-tonal, fine-tuned*
  pole. Load-bearing consequence: ViEmoSpeech's hook cannot cite "multimodal beats unimodal"
  generically — the audio-contribution magnitude is exactly what our tonal/ASR-noisy regime changes, and
  is the thing we must *measure*.
- **GAP / internal inconsistency — the evaluation set is not well-defined, so the headline metric is not
  comparable.** §3.1 states the **standard MELD splits** (train 10,000 / val 1109 / **test 1353**) and
  **WavLM-Base-Plus** audio, but **Algorithm 2** actually does `RandomSplit(D, [0.8, 0.2])` into
  **train/val only** (no held-out test) and instantiates a **`Wav2Vec2Processor("wav2vec2-base-960h")`**,
  not WavLM. Worse, the confusion-matrix true-positive counts (§5.3: Sadness **898** + Surprise 837 +
  Anger 753 + Joy 746 = **3,234** across just four classes) **exceed any plausible 20% split of the
  ~12,462-utterance 5-class set (~2,500)** and are far above the standard 1,353-utterance test set — so
  the reported 0.83 **cannot be mapped to the standard MELD test partition**. This makes **Table 4's SOTA
  comparison invalid**: 5-class accuracy on an under-specified, non-speaker-disjoint split vs **TelME's
  7-class weighted-F1 67.37** (validated ✔) and Bi-LG-GCN's number — different metric, different class
  count, different split. ⇒ ViEmoSpeech cites this as a **what-not-to-do for reporting**: it is exactly
  why our protocol fixes speaker-disjoint splits (ADR-002), reports macro-F1 (not accuracy) on a
  class-imbalanced set, and never compares across mismatched metrics.
- **Statistical power is absent, not just thin.** Wilcoxon **p=0.125** and Sign-test **p=0.25** are
  **both non-significant at α=0.05**, yet the text reads them as "consistently outperformed." 3 seeds
  cannot support a significance claim — our eval must use ≥5 seeds (vn-11) and report CIs honestly.
- **Frozen-vs-fine-tuned unanswered for our regime.** They only run fully-fine-tuned; there is **no
  frozen-encoder arm**, so this paper gives no evidence on whether a frozen WavLM (V-B) suffices — an
  open A/B we must run ourselves.
- **Attribution ≠ integration (their own caveat).** §5.8 concedes the IG/Occlusion agreement across
  modalities "may reflect emotion-dependent correlations between textual and acoustic content rather than
  explicit cross-modal integration." For V-G this is a direct warning: an attribution figure alone cannot
  substantiate the tone×emotion channel-competition claim; it must be backed by a quantitative,
  probe-based measurement (vn-06 Ridge probe, vn-13 statistical interaction / Cramér's V).
- **WavLM pooling unspecified** — how the frame sequence collapses to one 768-d vector (mean-pool? CLS?
  attention-pool?) is never stated; if we copy the recipe we must choose and report it (mid-layer
  mean-pool per vn-06 for tone-sensitivity).
