# Paper vn-10 — Emotional Vietnamese Speech-Based Depression Diagnosis Using Dynamic Attention Mechanism

- **Authors:** Quang-Anh N.D., Manh-Hung Ha, Thai Kim Dinh, Minh-Duc Pham, Ninh Nguyen Van (VNU Hà Nội)
- **Venue / year:** arXiv Dec 2024; Springer chapter (10.1007/978-3-032-00267-9_23)
- **Links:** abs https://arxiv.org/abs/2412.08683 · PDF `pdfs/10-vn-depression-dynamic-cbam.pdf`
- **Group:** vietnamese-ser / VNEMOS-line baseline, distress-adjacent

**Summary:** Dynamic-CBAM (omni-dimensional dynamic convolution attention) +
BiGRU on the VNEMOS dataset (250 clips, MFCC-only best config) for 5-class
emotion as a depression-diagnosis proxy; UA 0.87 / WA 0.86 / F1 0.87.

**Relevance to ViEmoSpeech:** Audio-only VN baseline number; evidence the
VNEMOS author cluster has not explored bimodal or tone-aware framing. Their
"emotion as depression proxy" framing is a cautionary contrast for our
distress-is-a-proxy discipline (V-F, honest framing).

> Stub created 2026-07-10 (task `docs/tasks/paper-deep-analysis.md`); deep-read pending.

## Deep research — full-PDF read (2026-07-10)

### Source-access note

Read the full local PDF `pdfs/10-vn-depression-dynamic-cbam.pdf` (arXiv:2412.08683v1,
`cs.SD`, 11 Dec 2024) via `pdftotext` — method, dataset, all equations (Eq 1–9), and every
table (Tables 1–4). The paper is 9 pages, single study. The **published/venue version** is a
Springer chapter (ICAMCS-line 2024 proceedings, DOI 10.1007/978-3-032-00267-9_23); Springer
full text is paywalled (link redirects to `idp.springer.com` auth) — **not bypassed**.

Web-validated the load-bearing numbers against non-paywalled surfaces:
- Headline UA/WA/F1 = 0.87/0.86/0.87 on VNEMOS — **✔ corroborated**. Query: *"Emotional
  Vietnamese Speech-Based Depression Diagnosis Dynamic Attention Mechanism VNEMOS UA 0.87"* →
  `https://arxiv.org/abs/2412.08683` and the Springer abstract snippet both report
  "0.87 UA, 0.86 WA, 0.87 F1-score". Preprint and venue agree; no delta found.
- Table 4 full ablation ladder (0.73 → 0.87) — **✔ corroborated** against the arXiv HTML
  (`https://arxiv.org/html/2412.08683v1`), which reproduces every row identically to the local
  PDF.
- VNEMOS = 250 segments / ~30 min / 27 movies-series-live-shows / 5 emotions — **✔ corroborated**
  in-text and cross-checked against the dataset's own source paper (VNEMOS, ICDV 2024,
  10.1109/icdv61346.2024.10616411, `https://ieeexplore.ieee.org/document/10616411/`). Minor
  cross-source discrepancy: web summaries of the *VNEMOS ICDV paper* cite "89% accuracy" for the
  original DNN, whereas this depression paper reports the prior VNEMOS baseline as UA 0.85 in its
  Table 4 row "Anh, N. Q., et al. [20]" — **≈ approximate** (different metric/config; not
  load-bearing here).

### What the paper actually does

**Claim vs. content.** The title and abstract sell "depression diagnosis." The actual model is a
**5-class acted-emotion classifier** (anger, happiness, sadness, fear, neutral) trained with
plain cross-entropy (Eq 6). **Depression is never operationalized** — there is no depression
label, no PHQ/BDI/clinical anchor, no emotion→depression mapping rule, and no depressed-subject
data. The depression framing is entirely rhetorical: the Introduction asserts depressed people
"speak slowly, trembly, and lose emotion," and the Conclusion calls the emotion model "the
prerequisite step" toward a future depression system. §4 even lists the classes inconsistently
("anger, sadness, happiness, anxiety, and neutral" — "anxiety" swapped for "fear"), signalling
the emotion set itself is loosely handled. This is the single most important thing the paper
demonstrates for us, and it is a *negative* example (see V-F below).

**Architecture.** Two designs are compared (Fig 3):
- (a) **Dual-stream**: stream 1 = raw waveform (5 s @ 16 kHz) → four 1D CBM blocks
  (Conv-BatchNorm-MaxPool) → Bi-GRU (Eq 5); stream 2 = MFCC → four 2D CBM blocks →
  **Dynamic-CBAM** → concatenate → dense classifier (outputs 0–4).
- (b) **Proposed / final**: **MFCC-only, single stream** — drops the raw-waveform branch
  "to avoid data corrupted spike-noises in the raw waveform."
- **Dynamic-CBAM** = standard CBAM (channel attention Eq 1 + spatial attention Eq 2, combined
  Eq 3) with the spatial-attention convolution replaced by **ODConv** (omni-dimensional dynamic
  convolution, Eq 4) so kernel weights are input-dependent.

**Data & preprocessing.** VNEMOS: 250 clips, ~30 min total, from 27 movies / series / live shows
(mixed natural + acted). **Mirror-padding** (repeat the clip) pads short segments to the 5 s
window. Preprocessing text says "resample with 160kHz … windows with 8kHz" — an evident typo for
16 kHz sample rate; do not treat literally.

**Training / eval protocol.** epoch=100, lr=0.001, batch=32, Adam, cross-entropy; RTX 2080 Ti.
**5-fold stratified cross-validation, stratified by class** (§3.3). Metrics: UA (unweighted /
macro accuracy), WA (weighted accuracy), precision/recall/F1 (Eq 7–9).

**Results (Table 4, 5-fold CV averages) — ✔ corroborated:**

| Config | Input | UA | WA | F1 |
|---|---|---|---|---|
| One-stream | waveform | 0.73 | 0.72 | 0.73 |
| One-stream GRU | waveform | 0.80 | 0.79 | 0.80 |
| One-stream GRU | MFCC | 0.82 | 0.81 | 0.82 |
| One-stream Bi-GRU | waveform | 0.76 | 0.75 | 0.76 |
| Dual-stream Bi-GRU | waveform+MFCC | 0.84 | 0.83 | 0.84 |
| Dual-stream Dynamic-CBAM | waveform+MFCC | 0.85 | 0.85 | 0.85 |
| Dual-stream Dynamic-CBAM Bi-GRU | waveform+MFCC | 0.86 | 0.85 | 0.86 |
| **Proposed (MFCC-only)** | MFCC | **0.87** | **0.86** | **0.87** |
| Anh et al. [20] (prior VNEMOS) | MFCC | 0.85 | 0.83 | 0.85 |

Headline: the **MFCC-only model beats the best dual-stream config by +0.01 UA** (0.87 vs 0.86);
adding the raw-waveform branch never helped and often hurt.

### Parts directly useful for Pebble

1. **The "emotion-as-depression-proxy" framing gap — a governance/labeling anti-pattern
   [V-F].** This paper labels 5 acted emotions and *asserts* depression relevance with zero
   clinical linkage or depressed-population data. It is the cleanest published example in our
   VN set of the exact overclaim ViEmoSpeech's distress head must NOT make. Concrete artifact:
   the distress-head spec in `docs/spec/capabilities/` and the method paper's framing paragraph
   should cite this as the contrast — "distress flag = acted-drama proxy, explicitly not a
   clinical or depression signal; we do not infer disorder from emotion."
   **Transfer risk:** none technically — we copy the *lesson, not the method*. The risk is
   reputational if ViEmoSpeech drifts toward the same overclaim, which this paper makes vivid.

2. **VNEMOS as a VN audio-only baseline number — but a *soft* one [V-G].** UA 0.87 / WA 0.86 /
   F1 0.87 is the number to cite in our baselines table (alongside 2412.09829 and 2604.01711).
   **Critically, the split is 5-fold CV stratified *by class*, NOT speaker-disjoint** (§3.3), on
   only 250 clips from 27 sources with heavy per-source speaker reuse — so the same actors almost
   certainly appear in train and test folds. Concrete artifact: the `V-G` eval-protocol doc and
   the baselines table must annotate this number as **"speaker-leaky, not comparable to our
   speaker-disjoint holdout"** — an *upper-bound-inflated* reference, not a bar to claim on equal
   footing.
   **Transfer risk:** high. A 0.87 obtained under speaker leakage on 250 clips will not survive a
   speaker-disjoint split; our comparable numbers will look worse and that is *correct*, not a
   regression. State this plainly wherever the number appears.

3. **MFCC-only ≥ raw-waveform dual-stream — a feature-choice data point [V-B].** Their best model
   drops the raw-waveform branch; every waveform-inclusive row is ≤ the MFCC-only row (Table 4).
   They attribute the raw-waveform branch's failure to "spike-noise." Concrete artifact: the
   `V-B` audio-backbone experiment — weak evidence that on tiny VN drama corpora, hand-crafted
   spectral features (MFCC) can match or beat a jointly-trained raw-waveform CNN, i.e. a
   raw-audio model is not automatically better when data is scarce.
   **Transfer risk:** high, and it partly cuts *against* our plan. The result is a 1D-CNN trained
   from scratch on 250 clips — it says nothing about **pretrained** raw-waveform SSL encoders
   (WavLM / emotion2vec), which is what V-B actually proposes. Read it as "don't train a raw-audio
   CNN from scratch on our corpus," not "don't use WavLM."

### How each part helps Pebble succeed

- **V-F / distress head.** Write the honest-proxy framing into the distress-head spec *now* and
  cite this paper as the anti-pattern: emotion classification on acted VN media is not depression
  detection. Our recall-floor objective is defined over an *acted-drama distress proxy*; any paper
  text touching clinical utility gets the same hedge. Action: add one sentence to the distress
  capability file — "we deliberately avoid the emotion→disorder inference made by
  Quang-Anh et al. (2024), which claims depression diagnosis from a 5-class acted-emotion model
  with no clinical anchor."
- **V-G / eval protocol + baselines.** Add the row to the baselines table with the leakage caveat,
  and use it to *justify* our speaker-disjoint + whole-series-holdout protocol (ADR-002): the
  contrast "0.87 under class-stratified CV vs. our lower-but-honest speaker-disjoint number" is
  itself a methodological point in the method paper. Action: baselines table gets a "split" column
  so VNEMOS's class-stratified CV is visibly distinguished from our speaker-disjoint numbers.
- **V-B / audio features.** Run the feature ablation with the *correct* comparison: pretrained
  WavLM/emotion2vec vs. MFCC vs. their fusion — *not* raw-CNN-from-scratch vs. MFCC. Their result
  only licenses "MFCC is a strong cheap baseline on small VN data"; keep an MFCC baseline arm so we
  can show whether SSL features actually beat it in our regime. One experiment worth running:
  whether MFCC's advantage here is because raw-waveform CNNs from scratch overfit 250 clips (which
  our pretrained backbone sidesteps).

### Child mental-health lens

- **Transfer validity: low as a corpus, useful as a warning.** VNEMOS is acted/natural VN adult
  media (movies, series, live shows), 5 basic emotions, no children, no distress/clinical labels.
  Nothing transfers to a child register directly; the *emotion taxonomy* (5 basic) is even
  narrower than our 7-class + V/A + distress scheme.
- **The overclaim is the ethics lesson.** A model that classifies acted anger/sadness and is then
  titled "depression diagnosis … so treatment and prevention can be started" is exactly the kind
  of clinical-utility leap that is dangerous in a child-facing context. ViEmoSpeech's discipline
  — distress is a *proxy flag with a recall floor*, feeding a decision layer, never a diagnosis —
  is the correct posture, and this paper shows the failure mode to avoid.
- **Human-label discipline (ADR-003).** VNEMOS's labels come from the same author cluster with no
  reported inter-annotator agreement, no speaker-disjoint discipline, and a proxy claim. It
  reinforces why our gold set needs κ/α and a whole-series human-labeled holdout before any
  headline claim.
- **Mitigation for us:** keep the distress head's outputs strictly non-diagnostic in copy and API;
  never let "emotion pattern" stand in for "mental-health status" in child-facing surfaces.

### Limitations & open questions for Pebble

- **Contradiction/gap vs. our plan (V-B):** this paper's "MFCC beats raw waveform" *appears* to
  undercut V-B's premise that a raw-waveform SSL backbone (WavLM/emotion2vec) is worth the cost.
  The contradiction is resolvable — theirs is a from-scratch 1D-CNN on 250 clips, ours is a
  pretrained SSL encoder — but it must be surfaced and tested, not assumed away. If our own
  ablation ever shows MFCC ≈ WavLM on the ViEmoSpeech corpus, that is a real finding, and this
  paper is the precedent. **Open question:** at what corpus size does a pretrained raw-audio
  backbone overtake MFCC on VN drama speech?
- **Contradiction/gap vs. our eval discipline (V-G):** their 0.87 is not speaker-disjoint (5-fold
  CV stratified by class on 250 clips / 27 sources). Any comparison that puts our speaker-disjoint
  number next to their 0.87 without the split caveat is apples-to-oranges and would understate
  ViEmoSpeech. This is the concrete contradiction to flag in the baselines table.
- **No tone, no text, no bimodality.** The VNEMOS cluster has published *only* audio-only,
  tone-agnostic models — confirming the ViEmoSpeech gap (tone×emotion, bimodal audio+text) is
  genuinely unoccupied by this group.
- **Margin is within noise.** +0.01 UA on ~50 test clips/fold is not a reliable ranking; the
  "MFCC-only is best" conclusion rests on a difference smaller than the CV variance the paper does
  not report (no std, no CIs). Treat the whole Table-4 ladder as directional only.
- **Small unresolved discrepancies:** the 5-emotion set is stated inconsistently (fear vs.
  anxiety); "160 kHz / 8 kHz" preprocessing is a typo for 16 kHz; and the prior VNEMOS baseline is
  cited as UA 0.85 here vs. "89% accuracy" in some web summaries of the ICDV paper — none
  load-bearing, but they lower confidence in the paper's numerical care.
