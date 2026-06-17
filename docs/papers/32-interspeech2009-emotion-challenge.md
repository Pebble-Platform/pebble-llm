# Paper 32 — The INTERSPEECH 2009 Emotion Challenge

## 1. Bibliographic info

**Title:** The INTERSPEECH 2009 Emotion Challenge

**Authors:** Björn Schuller (Institute for Human-Machine Communication, Technische Universität München, Germany), Stefan Steidl, Anton Batliner (Chair of Pattern Recognition, Friedrich-Alexander University Erlangen-Nuremberg, Germany).

**Year / venue:** Proceedings of INTERSPEECH 2009, 6–10 September 2009, Brighton, UK, pp. 312–315. ISCA. DOI 10.21437/Interspeech.2009-103.

**Keywords (verbatim):** "emotion, challenge, feature types, classification".

**Why this paper for Pebble:** This is the paper that *standardised* speech-emotion-recognition (SER) evaluation. It is the founding installment of the long-running INTERSPEECH ComParE / Paralinguistics challenge series, and it introduced (a) the FAU-AIBO children's emotion corpus with a fixed speaker-independent split, (b) the IS09 384-dimensional acoustic feature set (16 LLDs × functionals), and (c) the convention that **Unweighted Average (UA) recall**, not accuracy, is the primary metric for imbalanced emotion. For Pebble's voice-message modality thesis, this is the canonical citation for *how SER is evaluated* and *why class-imbalanced emotion needs UA*.

## 2. Problem motivation

The authors open with a structural complaint about the SER field circa 2009: in contrast to Automatic Speech Recognition (ASR) and Speaker Recognition, "practically no standardised corpora and test-conditions exist to compare performances under exactly the same conditions." Two specific failures are named:

1. **Non-comparable evaluation.** "Reading results on randomly partitioned data, one does not know the exact configuration. As a consequence, figures are not comparable, even if 10-fold cross-validation is used by two different sites: the splits may be completely different." Most prior work used subject-dependent testing or percentage-split / cross-validation *with random instance selection*, which leaks target-speaker data into training. Only **Leave-One-Subject-Out** or **Leave-One-Subject-Group-Out** truly guarantees speaker independence.
2. **Unrealistic data.** "Practically all databases which have been used by different sites such as the freely available and highly popular EMO-DB do not contain realistic, non-prompted speech but prompted, acted speech." Acted data has clean, balanced classes whose acoustics "cannot simply be transferred to realistic data."

A third, quieter problem: **feature-set chaos.** "There is practically no same feature set found twice: high diversity is not only found in the selection of low-level descriptors (LLD), but also in the perceptual adaptation, speaker adaptation, and — most of all — selection and implementation of functionals." This is contrasted against ASR's settled MFCC/RASTA/PLP standards.

The challenge is positioned as the public successor to the CEICES initiative (ref [5]), where seven sites compared classifiers under identical conditions but "was not fully open to the public."

## 3. The challenge design (three sub-challenges)

Built on **non-prototypical five- or two-class** emotion problems (the whole corpus, not a clean subset):

- **Open Performance Sub-Challenge** — own features, own classifiers, but must obey the fixed test/train split.
- **Classifier Sub-Challenge** — participants use the organisers' standard 384-feature ARFF files (sub-sample, transform, bootstrap, fuse classifiers via ROVER / ensemble); audio files may not be used.
- **Feature Sub-Challenge** — participants upload their best ≤100 features per unit of analysis; organisers test them with identical settings and pool them in a feature-selection process. Test-set labels are hidden; up to 25 prediction uploads per participant return confusion matrices.

**Primary metric, stated explicitly:** "As classes are unbalanced, the primary measure to optimise will be unweighted average (UA) recall, and secondly the weighted average (WA) recall (i. e. accuracy)." This single sentence is the load-bearing methodological contribution for Pebble.

## 4. Dataset deep dive — FAU-AIBO Emotion Corpus

**Collection.** Recordings of **51 children (age 10–13, 21 male, 30 female)** interacting with Sony's pet robot Aibo in a Wizard-of-Oz setup — the children believed Aibo obeyed their commands, but a human operator drove it through a fixed disobedient sequence to provoke emotional reactions. Collected at **two schools, MONT and OHM**. ~**9.2 hours of speech** (without pauses). High-quality wireless headset, DAT recorder, 16-bit, 48 kHz down-sampled to 16 kHz. Spontaneous **German** child speech.

**Annotation.** Segmented automatically into "turns" via a 1-s pause threshold. **Five labellers** (advanced linguistics students) annotated each *word* independently as neutral (default) or one of ten other classes. Labels resolved by **majority voting (MV)**: ≥3 of 5 labellers must agree. Word-level MV counts: joyful (101), surprised (0), emphatic (2,528), helpless (3), touchy/irritated (225), angry (84), motherese (1,260), bored (11), reprimanding (310), rest (3), neutral (39,169); 4,707 words had no MV; **48,401 words total**.

**Unit of analysis = chunk.** Prior work [1, Table 7.22] showed the best unit is "neither the word nor the turn, but some intermediate chunk." Manually defined chunks on syntactic-prosodic criteria are used. **The whole corpus = 18,216 chunks** is used (not a prototypical subset).

**The two label schemes (the heart of the protocol).**

*5-class* — cover classes Anger (= angry + touchy + reprimanding), Emphatic, Neutral, Positive (= motherese + joyful), Rest:

| Class | A | E | N | P | R | Total |
|---|---|---|---|---|---|---|
| train | 881 | 2,093 | 5,590 | 674 | 721 | 9,959 |
| test | 611 | 1,508 | 5,377 | 215 | 546 | 8,257 |
| total | 1,492 | 3,601 | 10,967 | 889 | 1,267 | 18,216 |

(Table 1.) Severely imbalanced: Neutral is 60% of the data; Positive and Rest are <5% each.

*2-class* — NEGative (= angry + touchy + reprimanding + emphatic) vs IDLe (all non-negative):

| Class | NEG | IDL | Total |
|---|---|---|---|
| train | 3,358 | 6,601 | 9,959 |
| test | 2,465 | 5,792 | 8,257 |
| total | 5,823 | 12,393 | 18,216 |

(Table 2.)

**Speaker-independent split (the reproducibility lever).** "Speaker independence is guaranteed by using the data of one school (OHM, 13 male, 13 female) for training and the data of the other school (MONT, 8 male, 17 female) for testing." Train chunks are in sequential order with child IDs; **test chunks are presented in random order with no speaker information** — preventing any test-time speaker adaptation. Transliterations + corpus vocabulary are provided for ASR / linguistic-feature training.

**Chance baselines.** Picking the majority class gives WA (accuracy) **70.1%** (2-class) and **65.1%** (5-class); chance UA recall is **50%** (2-class) and **20%** (5-class). These numbers are the reason accuracy is misleading — a do-nothing classifier scores 65–70% accuracy.

## 5. The IS09 feature set (384 features)

Provided via the open-source **openSMILE** toolkit for "highest transparency." Construction:

**16 low-level descriptors (LLDs)**, each with its delta (Δ) coefficient → 32 contours:
zero-crossing-rate (ZCR), RMS frame energy, pitch frequency F0 (normalised to 500 Hz), harmonics-to-noise ratio (HNR by autocorrelation), and **MFCC 1–12** (HTK-compatible).

**12 functionals** applied per chunk to each contour: mean, standard deviation, kurtosis, skewness, minimum value, maximum value, relative position (of min/max), range, and two linear-regression coefficients (offset, slope) with their mean-square error (MSE).

**Total: 16 × 2 × 12 = 384 attributes per chunk** (Table 3). This is the "IS09" / IS09-emotion feature set still cited as a standard baseline 15+ years later.

## 6. Baseline systems and results

Two "predominant architectures" are benchmarked, deliberately using only public, default-configured tools (HTK + WEKA) for reproducibility:

**Dynamic modelling (HMM, on LLD contours).** Linear left-right HMM, one model per emotion, varying state counts (1/3/5), 2 Gaussian mixtures, 6+4 Baum-Welch iterations, Viterbi decoding. Up-sampling has no effect here (one HMM per class, equal priors).

| Task | #States | UA recall | WA recall |
|---|---|---|---|
| 2-class | 1 | 62.3 | 71.7 |
| 2-class | 3 | 62.9 | 57.5 |
| 2-class | 5 | **66.1** | 65.3 |
| 5-class | 1 | 35.5 | 50.8 |
| 5-class | 3 | 35.2 | 34.7 |
| 5-class | 5 | **35.9** | 37.2 |

(Table 4, recall columns.)

**Static modelling (SVM on the 384 features).** Sequential minimal optimisation, **linear kernel**, pairwise multi-class. Class imbalance handled by **SMOTE** up-sampling of the training set; whole-set **standardisation** also tested. Pre-processing strategies: B = balancing (SMOTE), S = standardisation; "-" = neither. Order matters because standardisation behaves differently after balancing.

| Task | Process | UA recall | WA recall |
|---|---|---|---|
| 2-class | – | 62.7 | 72.6 |
| 2-class | S | **67.6** | 68.3 |
| 2-class | B | **67.7** | 65.5 |
| 5-class | – | 28.9 | **65.6** |
| 5-class | S | **38.2** | 39.2 |
| 5-class | B | 38.0 | 32.2 |

(Table 5, recall columns.)

**The official challenge baselines** (the numbers the community competed against): **2-class UA ≈ 67.7%, 5-class UA = 38.2%** (best SVM rows). Note the diagnostic pattern in the 5-class "–" row: **WA 65.6% but UA only 28.9%** — a classifier that mostly predicts Neutral scores near-chance accuracy yet is *useless*, which UA exposes immediately. Tightening for accuracy (WA) and tightening for UA pull in opposite directions on imbalanced data; the authors optimise UA.

**On realism (Sec. 4).** Earlier MV-only / prototypical-subset experiments reached 4-class UA "above 65%," and "using only very prototypical cases, an unweighted average recall close to 80%"; mapping to 2 classes "could be pushed above 90%." Using the *whole, realistic* corpus deliberately "scale[s] down our expectations" — by analogy with ASR's read-to-spontaneous transition where error roughly doubles. This is an explicit statement that *prototypical-subset SER numbers do not transfer to in-the-wild data.*

## Deep research — full-PDF read (2026-06-16)

### Source-access note

Read from the local PDF `docs/papers/pdfs/32-interspeech2009-emotion-challenge.pdf` via `pdftotext` (full text, all 4 pages incl. Tables 1–5 and the references). The PDF carries DOI `10.21437/Interspeech.2009-103` and the ISCA copyright line, i.e. it *is* the venue version, so there is no preprint-vs-published delta to reconcile.

Web validation performed:
- Search `"INTERSPEECH 2009 Emotion Challenge Schuller Steidl Batliner FAU Aibo 384 features baseline UA WA recall"` → ISCA Archive landing page `https://www.isca-archive.org/interspeech_2009/schuller09_interspeech.html` confirms title, authorship, the FAU-Aibo basis, the 384-feature set, and "unweighted average (UA) recall" as primary metric. ✔
- Search `"FAU Aibo Emotion Corpus 18216 chunks 51 children 5-class 2-class speaker independent OHM MONT"` → FAU Pattern Recognition Lab corpus page + corroborating papers confirm **18,216 chunks, 51 children, ~9.2 h, ~48k words, 5 labellers, word-level annotation, 2- and 5-class mappings**. ✔
- Search `"INTERSPEECH 2009 Emotion Challenge baseline 5-class unweighted average recall 38.2%"` → multiple downstream SER papers cite **38.2% UA (5-class)** and ~67% UA (2-class) as *the* IS09 baselines. ✔ The HMM-vs-SVM split (5-class: 35.5% HMM dynamic, 28.9% raw SVM static) is also corroborated, matching Tables 4–5 exactly.

All load-bearing numbers below are tagged ✔ corroborated (number both in the venue PDF and re-cited by ≥1 independent source) or ≈ approximate (rounded / "above" phrasing in the paper itself).

### What the paper actually does

It defines a reproducible SER benchmark and reports two reference baselines.

- **Corpus:** FAU-AIBO, **18,216 chunks** of spontaneous German child speech (51 children, age 10–13, ~9.2 h) [§2 / Table 1–2]. ✔
- **Labels:** word-level by 5 raters, majority-vote (≥3/5), collapsed to chunk-level into a **5-class** scheme (Anger / Emphatic / Neutral / Positive / Rest) and a **2-class** scheme (NEGative / IDLe) [§2]. ✔
- **Split:** strict **speaker-independent**, school-disjoint — train = OHM (9,959 chunks), test = MONT (8,257 chunks); test presented in random order with no speaker IDs [§2, Tables 1–2]. ✔
- **Features:** **IS09 = 384** = 16 LLD × 2 (+Δ) × 12 functionals, via openSMILE [§3 / Table 3]. ✔
- **Baselines:** HMM (dynamic, on LLDs) and **SVM** (static, on the 384 features, SMOTE balancing + standardisation), both in default-config public toolkits (HTK, WEKA) [§5]. ✔
- **Metric:** **UA recall primary**, WA recall (= accuracy) secondary, *because classes are unbalanced* [§1, §4]. ✔
- **Headline baseline results [Tables 4–5]:** ✔
  - 2-class: SVM best **UA 67.7% / WA 65.5%** (balancing); HMM best UA 66.1%. Majority-class accuracy = 70.1%, UA chance = 50%.
  - 5-class: SVM best **UA 38.2% / WA 39.2%** (standardisation); raw SVM UA 28.9% but WA 65.6%. Majority-class accuracy = 65.1%, UA chance = 20%.
- **Realism caveat:** prototypical-subset SER reached ~80% UA (4-class) / >90% (2-class), but on the *full realistic corpus* performance is "plainly lower" [§4]. ≈ (paper uses "above"/"close to" phrasing).

### Parts directly useful for Pebble

1. **UA recall as the primary metric for imbalanced emotion** [§1, §4]. → **D-C, D-G.** The single most transferable idea: with 60% Neutral, *accuracy is a vanity metric* (the raw SVM scored WA 65.6% / UA 28.9%). Pebble's emotion head (12-label, GoEmotions-mapped) and severity head are both class-imbalanced; UA recall (= macro-recall) must be a reported, optimised metric, not just accuracy/F1.
   - *Transfer risk:* **Low.** This is a metric choice, modality-agnostic — it transfers directly from speech to text emotion. The only caveat is that Pebble's emotion head is *multi-label* (GoEmotions) while IS09 is single-label; macro-recall generalises but must be computed per-label then averaged.

2. **Speaker- / source-independent split discipline** [§2, Tables 1–2]. → **D-H.** The school-disjoint OHM/MONT split, with test chunks stripped of speaker IDs, is the gold standard against the leakage the paper warns about ("random instance selection... may contain annotated data of the target speakers"). → Pebble must split its silver-labelled corpus by *child / source*, never by random row, or it will over-report.
   - *Transfer risk:* **Low–medium.** The principle is universal; the wrinkle is that Pebble's silver labels come from reused public datasets (GoEmotions/SemEval/WASSA), so "speaker independence" becomes "*dataset-of-origin* and *author/subreddit independence*." The leakage risk is real (GoEmotions has repeated Reddit authors) and the mitigation is the same: group-disjoint splitting.

3. **The macro-recall floor mindset for safety-relevant minority classes** [§4]. → **D-C, D-G.** The 5-class results show the minority classes (Positive 5%, Rest 7%) are exactly where a high-accuracy model collapses; UA forces the model to be measured on them. → Pebble's severity / high-distress tiers are the analogous rare-but-critical classes; the recall-floor policy is the operational version of "optimise UA."
   - *Transfer risk:* **Medium.** IS09's classes are emotion cover-classes with no safety semantics; Pebble's high-severity tier is genuinely safety-critical, so a *floor* (recall ≥ target) is stronger than IS09's "optimise the average." The direction transfers; the strictness must increase.

4. **The "prototypical-subset numbers don't transfer to realistic data" warning** [§4]. → **D-C, D-D, D-H.** Same corpus: ~80% UA on clean cases vs 38.2% UA on the whole set. → A direct caution for Pebble's severity-transfer plan (D-D): bars borrowed from clean benchmark subsets will overstate achievable performance on messy child-register turns.
   - *Transfer risk:* **Low.** This is a cross-cutting lesson about realistic vs curated data that applies a fortiori to Pebble's silver-label / child-register regime.

5. **The 384-feature openSMILE recipe itself** [§3, Table 3]. → **D-A (voice modality only).** If/when Pebble adds a *voice-message* path, IS09 (and its descendants eGeMAPS / ComParE) is the canonical, cheap, reproducible acoustic front-end and the baseline every SER paper reports against.
   - *Transfer risk:* **High for v1.** Pebble v1 is a *text* encoder (NeoBERT); these acoustic features do not feed it. This point is a v2/voice-modality artifact, not a v1 head. Flagged as forward-looking, not actionable now.

### How each part helps Pebble succeed

- **Emotion head (D-C):** Add **UA recall (macro-recall over the 12 GoEmotions labels)** to the emotion-head eval card alongside micro-F1 and accuracy, and make it the *selection* metric for checkpoints. Concretely: a model that scores high micro-F1 by always predicting the frequent labels (neutral, approval) will have low UA — exactly the IS09 failure mode — and should be rejected. This is the existing C-SSRS macro-recall bar (47.8%) generalised to the emotion head.
- **Severity head (D-C, D-D, D-G):** Report severity performance with a per-tier recall table, not just Pearson r. IS09's Table 5 is the template: show UA next to WA so a reviewer sees the imbalance cost. Set the high-severity tier recall as a *floor* and let precision float — the operational analogue of "optimise UA."
- **Data splits (D-H):** Build the train/val/test split *group-disjoint by source dataset and by author/subreddit where IDs exist*, mirroring OHM/MONT. Add a unit-test-style check that no author/source ID appears in two partitions. This is the cheapest defense against the inflated-number trap the whole paper is built to prevent.
- **Bar-setting (D-D):** When importing transfer bars (SemEval/WASSA Pearson, C-SSRS accuracy), annotate each with whether it came from a *prototypical/curated* or *full/realistic* split, and discount accordingly — IS09 quantifies the gap (≈80% → 38% UA) as the cost of going realistic.
- **Voice path (D-A, v2):** If a voice-message head is scoped, start from the openSMILE eGeMAPS/ComParE descendant of this 384-set as the baseline front-end and report UA on FAU-AIBO-style child speech for external comparability.

### Child mental-health lens

This is, notably, **one of the very few child-speech corpora in the entire related-work set** — FAU-AIBO is 51 children aged 10–13, spontaneous, in-the-wild emotional speech. That makes its *methodological* lessons unusually on-target for a child-facing product, even though the modality (German acoustic speech) differs from Pebble v1 (English text).

- **Transfer validity (positive):** The *evaluation protocol* (UA-primary, speaker-independent split, whole-corpus realism) is modality- and language-agnostic and transfers cleanly to Pebble's text heads. The corpus demonstrates that child emotional signal is recoverable but *hard* (38.2% UA on 5 realistic classes) — a sober, honest bar for child-register emotion.
- **Transfer risk (negative):** The *content* does not transfer. (a) Modality: acoustic prosody ≠ NeoBERT text tokens; the 384 features are useless to a v1 text encoder. (b) Language: German child speech to a Sony robot ≠ English child chat to a companion app. (c) Emotion taxonomy: AIBO's cover-classes (Anger/Emphatic/Neutral/Positive/Rest, robot-directed irritation) ≠ GoEmotions' 12-label mental-health-relevant scheme. None of AIBO's *labels* should be reused as Pebble training targets.
- **Mitigations:** Use FAU-AIBO only as (1) a citation for the UA metric and speaker-independent-split conventions, and (2) — if a voice path is built — an external child-speech SER comparison set, never as a v1 training source.
- **Ethics:** FAU-AIBO is a Wizard-of-Oz deception study on minors (children believed the robot was autonomous), conducted in 2009 under that era's norms, and is access-gated for research. Pebble cannot reuse its data and should not replicate its deception design; cite it for protocol, not for data-collection methodology.

### Limitations & open questions for Pebble

- **Contradiction / gap vs Pebble's plan — accuracy-centric reporting.** IS09's core thesis is that **accuracy (WA) is actively misleading** on imbalanced emotion (raw SVM: WA 65.6% but UA 28.9%, 5-class). Any Pebble eval that leads with accuracy or micro-F1 on the emotion/severity heads directly violates this 15-year-old standard. Pebble's eval card must put **macro/UA recall first**. (This also sharpens D-C: the C-SSRS bars stated as "52% acc / 0.75 wF1 / 47.8% macro-recall" should be read with macro-recall as the binding constraint, exactly per IS09.)
- **Contradiction vs Paper 01 (FAIIR) on the metric.** FAIIR reports sample-averaged precision/recall/F1 and AUROC and *never reports UA / macro-recall*; its headline is recall-at-threshold (0.81) on multi-label tags. IS09 would call that an incomplete picture on imbalanced data. Pebble should report *both* families (FAIIR-style per-tag P/R/F1 *and* IS09-style UA/macro-recall) rather than inheriting either paper's blind spot.
- **Single-label vs multi-label mismatch.** IS09 is single-label (one emotion per chunk); Pebble's emotion head is multi-label (GoEmotions). "UA recall" as IS09 defines it (mean of per-class recalls in a confusion matrix) needs reformulation for multi-label — Pebble must define macro-recall as the mean of per-label binary recalls and state this explicitly, since the IS09 definition does not carry over verbatim.
- **No learned model, no calibration, no probabilities.** IS09 reports only point predictions from SVM/HMM; no calibration, no thresholds, no probability outputs. It gives Pebble *zero* guidance on the calibration / threshold policy (D-G) beyond "optimise UA." That gap must be filled from other papers.
- **Modality gap is total for v1.** Every concrete artifact in this paper (features, classifiers, corpus) is acoustic; only the *evaluation philosophy* survives the jump to text. Open question: does Pebble's voice-message thesis intend a genuine acoustic head (then IS09/openSMILE is the front-end and FAU-AIBO the comparison set), or only ASR-to-text (then IS09 contributes the metric and split discipline only, and the 384 features are irrelevant)? The scoping decision determines whether D-A's voice branch is live.
