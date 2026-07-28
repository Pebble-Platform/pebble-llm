# Paper 20 — AVT-CA: Multimodal Emotion Recognition using Audio-Video Transformer Fusion with Cross Attention

- **Authors:** Joe Dhanith P R, Shravan Venkatraman, et al.
- **Venue / year:** arXiv preprint 2024 (v4 01/2026; preprint-only — chưa thấy acceptance)
- **Links:** abs https://arxiv.org/abs/2407.18552 · PDF `pdfs/20-avt-ca.pdf` · code github.com/shravan-18/AVTCA
- **Group:** audio-visual (đối chứng)

**Summary:** Hierarchical visual attention (channel+spatial+local) fuse với audio qua cross-attention transformer; eval CMU-MOSEI, RAVDESS, CREMA-D.

**Relevance to Pebble:** Reference engineering cho fusion ablation; rank thấp vì chưa peer-reviewed.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled Pebble profile (at analysis time).** Primary stream: ordinal
suicide-risk **text** classification — teacher-LLM silver labels, gold-holdout
eval on held-out clinical CSSRS, subject-level splits, ordinal-aware losses/metrics
(QWK/MAE), reproducible-by-construction (`docs/intent/constraints.md`). Adjacent
**voice** stream (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`):
heterogeneous 3-head MTL on a **frozen emotion2vec / WavLM-Large** backbone —
emotion (CE), affect valence+arousal (**CCC loss**), crisis (BCE under a **hard
recall floor ≥0.90**), balanced by **Kendall uncertainty weighting**, trained on
RAVDESS frozen features; voice+text fusion is the forward (deferred) direction.

### Analysis — AVT-CA (audio-video cross-attention fusion)
- **Overlap:** 4% (peripheral) — D1=0, D2=0, D3=1, D4=0, D5=0, D6=0, D7=0
  - Formula: (3·0 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·0) / 26 × 100 = 1/26 × 100 ≈ 4%.
- **Closest on:** D3 (dataset) — trains/evaluates on **RAVDESS** and **CREMA-D**;
  RAVDESS is exactly the corpus Pebble's voice MTL probe uses. That single-corpus
  overlap is the only real tie.
- **Why the rest score 0:** single **categorical** emotion task (Angry/Disgust/
  Fear/Happy/Neutral/Sad), accuracy+F1 only — no continuous/affect head, so no
  heterogeneous MTL (D1=0) and no principled loss balancing (D5=0); general MER,
  no mental-health/crisis and no recall constraint (D2=D6=0); no teacher-LLM
  distillation (D4=0); backbone is a **custom audio-video transformer** with
  channel/spatial attention over pre-extracted features, **not** the emotion2vec/
  WavLM SSL Pebble's voice stream uses (D7=0). CMU-MOSEI is used categorically,
  not as sentiment-intensity regression.
- **Best point (Method to adopt — forward direction, low current leverage):** the
  **intermediate transformer fusion + agreement-driven cross-attention** — the
  cross-attention module selectively reinforces *mutually consistent* audio-visual
  cues and suppresses noisy ones, reporting large ablation gains vs early/late
  fusion.
  - **How to apply to Pebble:** bank it as the reference recipe for the deferred
    **voice+text fusion** step — swap the video branch for the frozen text encoder
    and gate voice↔text tokens by mutual agreement so a noisy voice frame can't
    override a confident text-risk signal; it is not actionable at the current
    stage (single-modality voice MTL heads + primary text), so it stays a citation
    for the fusion chapter, not a task.
- **Caveats:** **preprint-only** (arXiv v4, no peer review) — treat all numbers as
  unverified; reported RAVDESS 96.11% acc / CREMA-D / MOSEI 95.84% are
  **within-distribution** single-benchmark results, **not** gold-holdout, so they
  are not a Pebble baseline to beat. Loss function not stated explicitly in the
  abstract/intro; inferred single-task CE from the accuracy/F1-only reporting and
  categorical label set (pp. 1–2, 7–9 read; method-section loss equations not fully
  verified).

## Deep research — full-PDF read (2026-07-10)

> Scope note: this is the audio-**visual** control paper (lowest prior overlap, ~4%,
> preprint-only). Per the task brief this section is deliberately **proportionate** —
> its job is to confirm, with evidence, that the fusion mechanism adds nothing beyond
> the audio-text/audio-audio fusion templates already extracted from bimodal 03/06/07/17
> and vn-07, and to extract the one thing it *does* contribute: a clean **V-G negative
> exemplar** (leak-inflated benchmark numbers). It is short on purpose.

### Source-access note

Full text read from the local PDF `docs/papers/bimodal-ser/pdfs/20-avt-ca.pdf` via
`pdftotext -layout` (898 lines; abstract, sections I–VI, all of Tables I–V, and the
reference list read). Web-validation:
- Query `AVT-CA Audio-Video Transformer Fusion Cross Attention arXiv 2407.18552 RAVDESS
  96.11 CMU-MOSEI` -> resolved arXiv abstract `https://arxiv.org/abs/2407.18552`, HTML
  `https://arxiv.org/html/2407.18552v4`, and the Moonlight literature review
  `https://www.themoonlight.io/en/review/multimodal-emotion-recognition-using-audio-video-transformer-fusion-with-cross-attention`.
- **Publication status (corroborated):** preprint-only. arXiv:2407.18552v4 [cs.MM] dated
  20 Jan 2026; ResearchGate lists it as "Request PDF" (preprint), no journal/conference
  acceptance located. The local PDF stub's "v4 01/2026, preprint-only" is correct. All
  numbers below are therefore **within-distribution preprint results, not peer-reviewed**.
- Code repo confirmed live: `github.com/shravan-18/AVTCA`.

### What the paper actually does

- **Task/modalities.** Single-task **categorical** emotion classification (6–8 classes,
  dataset-dependent) over **audio + video (facial) frames**. There is **no text/ASR
  branch at all** — the corrected label vs the old stub is "audio-video", not
  audio-text. Loss is confirmed plain **cross-entropy** (Sec. III-D,
  `L_CE = -1/N sum sum y log yhat`); optimizer Adam, lr 0.01, weight decay 0.001, batch 8,
  128 epochs, ~72 h train (Sec. IV). (The stub's "inferred single-task CE" is now confirmed
  from the method section. Corroborated.)
- **Architecture.** Video branch = hierarchical attention stack: channel attention +
  spatial attention + local (patch) feature extractor + two inverted-residual (depthwise-
  separable conv) blocks (Sec. III-A2). Audio branch = two Conv1D->BN->ReLU->MaxPool blocks
  (Sec. III-A1). Fusion = **intermediate transformer fusion** (each modality gets
  self-attention transformer blocks) followed by a **bidirectional cross-attention** module:
  audio-as-query over video-as-key/value (`o_AV`) and video-as-query over audio-as-key/value
  (`o_VA`), combined with residual self-attention (Sec. III-B/C). Final: max-pool each
  modality -> element-wise add -> FC -> softmax (Sec. III-D).
- **Datasets (Sec. IV-A, Table I).** RAVDESS (7,356 files, 24 actors), CMU-MOSEI (~23,500
  utterances, 1,000+ YouTube speakers), CREMA-D (7,442 clips, 91 actors). Split =
  **random 80/20 train/val** (Table I "Train (80%) / Val (20%)"); **no speaker-disjoint
  split, no held-out OOD set, no cross-corpus test** is mentioned anywhere.
- **Headline results (Tables II–IV) — corroborated** (arXiv HTML + Moonlight review match
  the local PDF):
  - RAVDESS: AVT-CA **96.11% acc / 93.78% F1**; next best CNN [57] 95.95 / 92.17.
  - CMU-MOSEI: AVT-CA **95.84% acc / 94.13% F1**; next best MAG-BERT 84.71 / 84.51.
  - CREMA-D: AVT-CA **94.13% acc / 94.67% F1**; next best DE-III 83.70 / 79.50.
- **Ablation (Table V) — approximate** (table is typographically mangled in extraction, but
  the readable cells are self-consistent): single-mechanism configs land far lower —
  IT-4 (intermediate-transformer, 4 heads) 76.41 / 67.72 / 71.50 acc across
  RAVDESS/MOSEI/CREMA; CT-4 (cross-attention, 4 heads) 76.00 / 64.94 / 72.10 — and the
  **full IT-4+CT-4 model jumps to 96.11 / 95.84 / 94.13**, which the authors describe as an
  "approximately 20% increase in accuracy and F1-score" (Sec. V-D). The ablation varies only
  **# attention heads (1 vs 4) and which fusion block**; there is **no audio-only vs
  video-only modality ablation** and, since there is no text, **no ASR-noise ablation**.

### Parts directly useful for ViEmoSpeech (each tagged to a Decision ID + transfer risk)

Only two decisions are in scope, and one of them is a "do-not-adopt / redundant" finding —
which is itself the requested deliverable.

1. **V-A (fusion) — REDUNDANT; adopt nothing.** The AVT-CA cross-attention is textbook
   **bidirectional cross-modal attention** (softmax(Q_a K_v / sqrt(d)) * V_v and the symmetric
   video->audio path). The "agreement-driven / mutually-consistent cue reinforcement"
   framing in the abstract is just the ordinary property of the attention softmax — there is
   **no explicit token-selection, Top-K distillation, gating, or noise-gate operator** in the
   equations (Sec. III-B/C). Everything it does is already covered, and covered *better for our
   register*, by material we have banked:
   - **RJCMA (bimodal-17)** is the same idea — joint cross-modal attention on **audio-visual** —
     but with the objective we actually need (**CCC loss L=1-rho_c** for V/A) instead of flat CE.
   - **CASE/FAS (vn-07)** already gives us the *real* token-selection mechanism (Top-K L2-saliency
     token distillation + Q-Former) that AVT-CA only gestures at.
   - **BCAF (bimodal-07)** already gives the noise-aware fusion + per-modality deep-supervision safeguard.
   - The video-specific channel/spatial/local hierarchy is **non-transferable** — it operates on
     `R^{HxWxC}` facial tensors; ViEmoSpeech has no visual modality and swaps video->text.
   - **Transfer risk (fatal):** the whole architecture is audio<->**video**; our swap is
     audio<->**text/ASR**. Cross-modal attention where the second stream is a noisy ASR token
     sequence is a different problem (alignment, tokenization, ASR error) that this paper never
     touches. **Recommendation for V-A: cite as one more instance of standard bidirectional
     cross-modal attention; adopt nothing; the fusion shortlist stays FAS / gated / BCAF.**

2. **V-G (eval) — strong NEGATIVE exemplar.** The result profile is a copybook case of
   leak-inflated benchmarking, and naming it sharpens our ADR-002 protocol:
   - **Random 80/20 split on 24-actor RAVDESS / 91-actor CREMA-D** (Table I) = near-certain
     **speaker leakage** (same actor's clips in train and val). 96.11% on RAVDESS with a random
     split sits with the leaky VN numbers (vn-08 86.6, vn-10 0.87) and against honest
     speaker-disjoint anchors (THAI-SER WA~60, MSP naturalistic macro-F1~0.30, bimodal-15
     naturalistic ceiling ~0.65 UAR).
   - **95.84% on CMU-MOSEI — an in-the-wild YouTube corpus — is the red flag.** Realistic
     multimodal SOTA on MOSEI sits ~84% (their own strongest baseline MAG-BERT 84.71); a jump
     to 95.84% on *in-the-wild* data while acted RAVDESS/CREMA-D land at 96.11/94.13 means the
     model shows **near-identical accuracy on acted and in-the-wild corpora**, which is not how
     register generalization behaves (cf. bimodal-01 text collapses 63->14 across registers;
     the register axis is real). This is the signature of an evaluation artifact, not a robust model.
   - **"~20% ablation jump" from adding attention heads** (Table V, Sec. V-D) is implausibly large
     for a head-count change and further suggests the headline numbers are not measuring what
     they claim.
   - **Transfer risk:** these numbers are **not a baseline to beat** and must never enter our
     baselines table as a target. Their *value* is as the cautionary citation for why
     ViEmoSpeech publishes a speaker-disjoint + whole-series-holdout number with bootstrap CIs.
   - **Recommendation for V-G:** cite AVT-CA in the "what-not-to-do" row alongside bimodal-11's
     ill-defined RandomSplit and vn-08/vn-10's leaky CV — random within-corpus split + implausibly
     flat acc across acted/in-the-wild = the exact failure our eval protocol is designed to avoid.

### How each part helps ViEmoSpeech succeed (concrete actions)

- **V-A:** No new fusion experiment. In the method paper's related-work/fusion-shortlist
  paragraph, add one sentence: "bidirectional cross-modal attention (e.g., AVT-CA, RJCMA) is
  the generic template; we adopt the token-selecting FAS variant because our second stream is
  noisy ASR text, not aligned video." Net effect: closes V-A's audio-visual branch of the
  search with a citation, saves an ablation arm.
- **V-G:** Add an explicit "leak-inflated benchmarks" row to the baselines/eval-protocol table
  in the method paper, listing AVT-CA (RAVDESS 96.11 / MOSEI 95.84, random 80/20 split) as a
  concrete example of within-corpus speaker leakage, and pair it with our honest
  speaker-disjoint number to make the contrast legible to reviewers.

### Child / VN-SER transfer lens

Minimal, because the paper is out-of-register on every axis that matters to us:
- **No tone, no Vietnamese, no phonation.** Purely audio-visual acted/YouTube English-corpus
  MER -> contributes nothing to the tone x emotion claim (V-D untouched; the "0/N papers measure
  lexical-tone x emotion" tally is unchanged by this paper).
- **No dimensional labels, no distress.** Single categorical head only -> nothing for V/A-CCC
  (V-B/E) or the distress recall-floor (V-F). RAVDESS is common to our voice probe, but AVT-CA
  uses it categorically with a leaky split, so even the shared-corpus tie gives no usable number.
- **Ethics/mitigation:** the only carry-over is the eval-integrity lesson — for a child-facing
  corpus, an inflated benchmark number is worse than an honest low one, because it would be
  cited to justify unsafe automation. AVT-CA is the concrete anti-example.

### Limitations & open questions for ViEmoSpeech (>=1 explicit contradiction/gap)

- **Contradiction vs bimodal-15 (Schuller replication, IEEE TAFFC 2026) and vn-11 (THAI-SER):**
  bimodal-15 shows the honest naturalistic speaker-independent ceiling is **~0.65 UAR**, and
  THAI-SER's honest clean-acted anchor is **WA 59.80 / UA 57.81**. AVT-CA's 94–96% acc on the
  same *kind* of acted data (and on in-the-wild MOSEI) is flatly incompatible with those honest
  ceilings — the difference is the split protocol (random-within-corpus vs speaker-disjoint).
  This directly corroborates our decision to publish speaker-disjoint numbers and to flag any
  random-split leaderboard entry.
- **No ASR / no-text blind spot (shared with every fusion paper we've read):** AVT-CA has no text
  modality at all, so like RJCMA/BCAF/WavFusion it never confronts ASR noise — the axis where
  ViEmoSpeech's contribution actually lives. Confirms the ASR-robustness ablation is still
  unclaimed territory.
- **Open question (none blocking):** whether the Table V "~20% from adding heads" jump reflects a
  reporting/labeling error in the mangled table or a genuine (and therefore suspicious) result —
  irrelevant to our plan, noted only so the number is never quoted as a real component-contribution
  figure.
