# Paper 30 — GeMAPS / eGeMAPS: The Geneva Minimalistic Acoustic Parameter Set for Voice Research and Affective Computing

## 1. Bibliographic info

**Title:** The Geneva Minimalistic Acoustic Parameter Set (GeMAPS) for Voice Research and Affective Computing.

**Authors:** Florian Eyben (TU München / Univ. Genève / audEERING), Klaus R. Scherer (Univ. Genève), Björn W. Schuller (Univ. Passau / Imperial College London / Univ. Genève), Johan Sundberg (KTH Stockholm), Elisabeth André (Univ. Augsburg), Carlos Busso (UT Dallas), Laurence Y. Devillers (Paris-Sorbonne / CNRS-LIMSI), Julien Epps (UNSW / NICTA), Petri Laukka (Stockholm Univ.), Shrikanth S. Narayanan (SAIL, USC), Khiet P. Truong (Univ. Twente).

**Year / venue:** *IEEE Transactions on Affective Computing*, Vol. 7, No. 2, pp. 190–202, April–June 2016. DOI 10.1109/TAFFC.2015.2457417. Licensed CC-BY 3.0. The recommendation was conceived at the Geneva "Bridge Meeting" (Swiss Center of Affective Sciences, 1–2 Sept 2013).

**Index terms (verbatim):** "Affective Computing, Acoustic Features, Standard, Emotion Recognition, Speech Analysis, Geneva Minimalistic Parameter Set".

**Implementation:** publicly available in the openSMILE toolkit (config `GeMAPSv01a` / `eGeMAPSv01a`; modern `eGeMAPSv02`). This is the standardization paper behind the feature sets the rest of the voice-speech papers in the Pebble set assume.

## 2. One-paragraph summary

GeMAPS is the field's deliberate counter-move against brute-force acoustic feature sets (ComParE's 6,373 features etc.). Instead of "collect everything that ever helped a classifier," an interdisciplinary panel of voice scientists agreed on a **minimalistic, theoretically-motivated, interpretable** set of acoustic parameters that index affective physiological changes in voice production. The **minimalistic GeMAPS = 62 parameters** derived from **18 low-level descriptors (LLDs)** plus 6 temporal features; the **extended eGeMAPS = 88 parameters**, adding 7 cepstral/spectral LLDs (MFCC 1–4, spectral flux, formant 2–3 bandwidths) and the equivalent sound level. Selection followed three criteria: (a) potential to index affective physiological changes in voice production, (b) proven value in prior literature plus reliable automatic extractability, (c) theoretical significance. Evaluated on six affective-speech corpora for binary arousal/valence with leave-one-speaker-out SVMs, eGeMAPS reaches **~79.7% UAR on arousal** and **~66.4% on valence** — "remarkably comparable" to the largest brute-force sets at **less than 2%** of their size. For Pebble, this is the canonical acoustic vocabulary that operationalizes "tone of voice / âm sắc": F0, jitter, shimmer, HNR, loudness, formants, spectral balance — an **interpretable, low-dimensional feature baseline** for the voice-message modality.

## 3. Why this paper is in the Pebble set (voice-message modality)

Pebble's primary path is text (NeoBERT encoder), but the thesis includes a **voice-message** modality: a child may send a short audio clip. To score that clip turn-level, the waveform must first become features. eGeMAPS defines *which* features — the expert-curated, interpretable acoustic vocabulary that every speech-emotion benchmark in this set (ComParE, AVEC, INTERSPEECH challenges) reports against. Where paper 29 (openSMILE) supplies the *engine*, this paper supplies the *vocabulary and its validation*: precisely the 18 GeMAPS LLDs / 88 eGeMAPS parameters, the rationale for each, and the cross-corpus arousal/valence numbers that justify choosing a small interpretable set over a 6k brute-force one. It moves **D-D** (severity/energy regression — acoustic transfer source + the interpretable feature substrate and arousal/valence metrics), and **D-H** (datasets / feature anchors / calibration). It is the citation Pebble needs whenever it claims an "interpretable acoustic baseline for the voice modality."

## Deep research — full-PDF read (2026-06-16)

### Source-access note

The full PDF **was read end-to-end** — `pdfs/30-egemaps.pdf` is the IEEE-accepted (CC-BY) version of *IEEE T-AFFC* 2016, 10.1109/TAFFC.2015.2457417, extracted with `pdftotext`. All LLD enumerations, parameter counts, functional definitions, dataset descriptions, and Table 1/2/3 numbers below are read directly from that full text (§3.1 minimalistic set, §3.2 extension, §4 baseline evaluation, Tables 1–3, §5 discussion).

Published-version provenance validated:

- **Venue + counts.** Search: *"GeMAPS 62 parameters eGeMAPS 88 parameters 18 LLD Eyben 2016 IEEE Transactions Affective Computing arousal valence UAR"*. Resolved: dblp `https://dblp.org/rec/journals/taffco/EybenSSSABDELNT16.html` and USC-SAIL preprint `https://sail.usc.edu/publications/files/eyben-preprinttaffc-2015.pdf`. Confirmed published as **IEEE T-AFFC Vol. 7, No. 2, pp. 190–202 (2016)**; **eGeMAPS = 88 parameters**; "eGeMAPS performs best for arousal, reaching almost 80% UAR." ✔ corroborated. The local accepted-version PDF and the published version agree on all load-bearing counts; no preprint delta on the numbers.
- **GeMAPS = 62 / 18 LLD; eGeMAPS extension = +7 LLD → 88.** Read from §3.1 ("In total, 62 parameters are contained in the Geneva Minimalistic Standard Parameter Set") and §3.2 ("the extended … eGeMAPS contains 88 parameters"). Cross-checked against the openSMILE/audEERING documentation summarized in paper 29's deep-read. ✔ corroborated.
- **UAR numbers (Table 2):** GeMAPS arousal 79.59 / valence 65.32; eGeMAPS 79.71 / 66.44; ComParE 78.00 / 67.17. Read directly from Table 2 of the PDF. The local PDF's prose has one transposition slip ("third best for arousal" where the data clearly means valence — eGeMAPS is *best* on arousal at 79.71 and *third* on valence behind ComParE 67.17 and InterSp12 66.71); numbers in the table are unambiguous and used here. ≈ approximate on the prose, ✔ corroborated on the table figures.

### What the paper actually does

**Goal (§1–2).** Decades of voice science produced a proliferation of acoustic parameters used selectively, extracted differently (even within "the same" tool like Praat, with non-public settings), making cross-study comparison impossible. Brute-force ML sets (often >6,000 features) compound the problem: they over-adapt to small training sets, generalize poorly cross-corpus (worse than small sets despite better intra-corpus scores, per [20]), and are essentially uninterpretable. The paper proposes a **standardized, minimalistic, interpretable** parameter set as a common baseline — one any team can adopt alongside their own task-specific features, enabling replication and cumulative evidence. Implementation is open-source in openSMILE so the exact computation is fixed, not just the parameter names.

**Selection criteria (§3).** Three: (1) potential of a parameter to index physiological changes in voice production during affective processes; (2) frequency and success of the parameter in past literature; (3) theoretical significance. This is explicitly *interdisciplinary-consensus-driven*, contrasted (§2) with the engineering-driven CEICES "collector" approach.

**The 18 GeMAPS LLDs (§3.1), by group — read verbatim:**

*Frequency-related (6 LLDs):*
- **Pitch** — logarithmic F0 on a semitone scale starting at 27.5 Hz (semitone 0).
- **Jitter** — deviations in individual consecutive F0 period lengths.
- **Formant 1, 2, 3 frequency** — centre frequency of the first/second/third formant (3 LLDs).
- **Formant 1 bandwidth** — bandwidth of the first formant.

*Energy/amplitude-related (3 LLDs):*
- **Shimmer** — difference of peak amplitudes of consecutive F0 periods.
- **Loudness** — perceived signal intensity estimate from an auditory spectrum.
- **Harmonics-to-Noise Ratio (HNR)** — energy in harmonic components vs. energy in noise-like components.

*Spectral (balance) parameters (9 LLDs):*
- **Alpha Ratio** — ratio of summed energy 50–1000 Hz to 1–5 kHz.
- **Hammarberg Index** — ratio of the strongest energy peak in 0–2 kHz to the strongest in 2–5 kHz.
- **Spectral Slope 0–500 Hz** and **Spectral Slope 500–1500 Hz** — linear regression slope of the log power spectrum within each band (2 LLDs).
- **Formant 1, 2, 3 relative energy** — ratio of the spectral harmonic-peak energy at each formant's centre frequency to the energy of the spectral peak at F0 (3 LLDs).
- **Harmonic difference H1–H2** — ratio of energy of the 1st F0 harmonic to the 2nd.
- **Harmonic difference H1–A3** — ratio of energy of the 1st F0 harmonic to the highest harmonic in the 3rd formant range.

(That is 6 + 3 + 9 = **18 LLDs**.)

**Smoothing.** All LLDs are smoothed with a symmetric 3-frame moving average; for pitch/jitter/shimmer, smoothing is done within voiced regions only (so voiced/unvoiced transitions are not smeared).

**How 18 LLDs become 62 parameters (§3.1):**
- **Arithmetic mean + coefficient of variation** (std-dev ÷ mean) applied to all 18 LLDs → **36 parameters**.
- To **loudness and pitch only**, 8 extra functionals each: 20th/50th/80th percentile, the 20–80th percentile range, and the mean + std-dev of the slope of rising/falling segments → +16, total **52 parameters**. All functionals applied to voiced regions only, *except* the loudness functionals (applied to all regions).
- Arithmetic mean of Alpha Ratio, Hammarberg Index, and the two spectral slopes over **unvoiced** segments → +4, total **56 parameters**.
- **6 temporal features**: rate of loudness peaks per second; mean and std-dev of continuously voiced-region length (F0 > 0); mean and std-dev of unvoiced-region length (F0 = 0, ≈ pauses); number of continuous voiced regions per second (pseudo-syllable rate) → **62 parameters total**. No minimum length is imposed on voiced/unvoiced regions; Viterbi-based F0 smoothing prevents spurious single-frame voicing.

**The eGeMAPS extension (§3.2): +7 LLDs, +26 parameters → 88:**
- **MFCC 1–4** (Mel-Frequency Cepstral Coefficients 1–4) and **spectral flux** (difference of spectra of two consecutive frames) — 5 spectral/cepstral LLDs.
- **Formant 2 bandwidth** and **Formant 3 bandwidth** — added for completeness with Formant 1 bandwidth (2 LLDs).
- Functionals: mean + coefficient of variation on all 7 added LLDs over all segments (formant bandwidths over voiced only) → +14. Plus: mean of spectral flux in unvoiced regions; mean + CV of spectral flux and of MFCC 1–4 in voiced regions → +11. Plus the **equivalent sound level** → +1. Total **+26 → 88 parameters (eGeMAPS)**.

**Selection rationale, per component (§2 literature synthesis):** F0 mean/variability/range and intensity (loudness) are the most consistently arousal-correlated descriptors across decades of work; spectral shape (alpha ratio, Hammarberg index, spectral slope) and **MFCC 1–4** carry **valence** information and are more robust under noise/reverberation than prosody; **formants** are sensitive to emotion and give near-state-of-the-art cognitive-load and depression results at a fraction of the dimensionality, and are deliberately included despite being neglected by many brute-force sets due to extraction difficulty; **jitter, shimmer, HNR** encode voice-quality / excitation-source changes; the **H1–H2 / H1–A3** harmonic differences index glottal adduction. Lower-order MFCCs are included (not higher) because, via the DCT-II basis, they capture spectral tilt / coarse energy distribution (affect-relevant) rather than fine phonetic detail.

**Evaluation (§4).** Task = binary **arousal** and binary **valence** classification. Six affective-speech corpora, each mapped to common binary arousal/valence labels (Table 1): FAU AIBO (children's spontaneous German speech, valence only), TUM-AVIC (level of interest), EMO-DB (Berlin acted emotions), GEMEP (acted multimodal portrayals, 12 emotions across all 4 quadrants), SING (operatic sung emotion), VAM (German talk-show, spontaneous). Classifier = **SVM (SMO in WEKA)**, results averaged over the 9 highest of 17 complexity (C) settings for stability. **Leave-one-speaker(group)-out** cross-validation (8 folds; AIBO uses 2-fold OHM↔MONT). Training partitions class-balanced by up-sampling; features **z-normalized** (per-speaker standardization used for the headline numbers). Compared against five brute-force baselines: InterSp09 (384), InterSp10 (1,582), InterSp11 (4,368), InterSp12 (6,125), ComParE 2013/14 (6,373).

**Results (Table 2, UAR averaged over 5 corpora excl. FAU AIBO, per-speaker standardization):**

| Parameter set | # params | Arousal UAR | Valence UAR |
|---|---|---|---|
| **GeMAPS** | **62** | **79.59** | 65.32 |
| **eGeMAPS** | **88** | **79.71** | 66.44 |
| InterSp09 | 384 | 76.08 | 64.88 |
| InterSp10 | 1,582 | 76.50 | 64.44 |
| InterSp11 | 4,368 | 76.43 | 65.96 |
| InterSp12 | 6,125 | 77.26 | 66.71 |
| ComParE | 6,373 | 78.00 | 67.17 |

All numbers ✔ read from Table 2. **eGeMAPS is the single best set on arousal (79.71) — beating all five brute-force sets including ComParE.** On valence it is mid-pack (66.44), third behind ComParE (67.17) and InterSp12 (66.71). eGeMAPS ≥ GeMAPS everywhere, confirming the MFCC/spectral-flux extension matters most for valence (§4.4). Per-corpus best results (Table 3) show eGeMAPS winning binary arousal on GEMEP and binary valence on SING; on raw multi-class category tasks the large ComParE/InterSp12 sets win, but for the dimensional arousal/valence targets the minimal sets are competitive.

**Headline conclusion (§4.4–5).** "The GeMAPS sets show remarkably comparable performance given their minimalistic size of less than 2% of the largest (ComParE) set." The authors note valence still benefits from larger sets (a gap to close in future work) and flag that **cross-corpus generalization** — where small sets should win most — is the key future experiment. The paper closes by positioning glottal/voice-source parameters (inverse filtering) as the next extension.

### Parts directly useful for Pebble

1. **eGeMAPS (88-param) as the interpretable acoustic feature baseline for a voice head.** A compact, expert-curated, fixed-length vector spanning F0, jitter, shimmer, HNR, loudness, formants F1–F3, alpha ratio, Hammarberg index, spectral slope, MFCC 1–4, spectral flux — the exact "tone of voice / âm sắc" vocabulary, small enough to train a head on Pebble's modest data without the over-adaptation the paper warns 6k sets cause. **D-D** (acoustic transfer source + interpretable substrate), **D-H** (feature anchor). *Tag: openSMILE config `eGeMAPSv02`; `pebble/audio/features.py` emits an 88-float vector per voice message.*
2. **GeMAPS-62 as the "interpretability-maximal" variant.** When per-feature interpretability matters more than the last point of valence accuracy (e.g. explaining *why* a clip read as high-arousal to a clinician), the 62-param set with arithmetic-mean + coefficient-of-variation functionals is the readable subset. **D-D**, **D-G** (calibration/explanation policy, largely v2). *Tag: `GeMAPSv01b` as an ablation/explanation config.*
3. **The arousal/valence asymmetry is a design directive.** eGeMAPS is *best-in-class on arousal* (79.71 UAR) but only competitive on valence. Pebble's `energy` dimension (arousal-like) is therefore the **well-supported** acoustic target; emotional *valence* from audio alone is weaker and should lean on the text head. **D-D** (pick `energy`/arousal as the primary acoustic target), **D-B** (if folded into MTL, weight the acoustic head's contribution toward arousal-type outputs). *Tag: route acoustic features primarily to the `energy` head, not `emotion` valence.*
4. **Minimal-set rationale = the over-adaptation / cross-corpus argument.** The paper's central empirical claim — small interpretable sets generalize where 6k brute-force sets over-fit, especially cross-corpus — directly supports Pebble preferring eGeMAPS over ComParE given small, domain-shifted (adult→child) data. **D-D**, **D-H**. *Tag: default to eGeMAPS; ComParE-6373 only as a one-row upper-bound ablation.*
5. **Per-speaker z-normalization + up-sampling balancing as the evaluation protocol.** The headline numbers use per-speaker standardization (means/variances per speaker) and class-balancing by up-sampling — directly transferable to Pebble's per-child normalization and imbalanced silver labels. **D-D**, **D-C/D-B** (imbalance handling). *Tag: per-child feature standardization + up-sampled minority severity bins in the acoustic-head experiment.*
6. **The FAU AIBO child-speech anchor (§4.1.1).** One of the six corpora is **children aged 10–13** (51 kids, ~9.2h, spontaneous German Wizard-of-Oz emotion), the same corpus behind the INTERSPEECH 2009 Emotion Challenge (paper 32). It is the *only* child-voice data point in the GeMAPS validation, and binary *valence* was the only feasible label. **D-H** (child-voice calibration anchor), **D-D**. *Tag: FAU AIBO as a candidate child-voice calibration/sanity set if licensable.*

### How each part helps Pebble succeed

- **Acoustic `energy` / `severity` (D-D).** Pebble's `energy` dimension (heuristic in v1) and `severity` regression are intrinsically acoustic (arousal/intensity). eGeMAPS gives the principled, *interpretable* feature vector to learn or anchor these on, and the paper's Table 2 proves the high-leverage subset for arousal is exactly the prosodic + voice-quality LLDs (loudness, F0 range, jitter, shimmer, HNR). Concrete action (v2 voice path): extract `eGeMAPSv02` per message, then either (a) train a small ridge/MLP head to predict `energy`/`severity` from the 88-vector, reporting **Pearson r** (matches the D-D convention), or (b) use loudness + F0-range + HNR functionals as a *better-grounded* heuristic `energy` proxy than the v1 text heuristic. The arousal-79.71 result is the evidence this works at the message level.
- **Pick arousal over valence for the acoustic head (D-D / D-B).** The 79.71-vs-66.44 asymmetry tells Pebble exactly where audio earns its keep: drive `energy` (arousal) from acoustics; keep `emotion` valence anchored on NeoBERT text. This avoids spending model capacity on the weak acoustic-valence signal and is a clean MTL routing decision.
- **Interpretable baseline for the thesis narrative.** eGeMAPS lets Pebble *name* what "tone of voice" means (this LLD list) and report it against the universal ComParE/AVEC baselines — the only way an acoustic head's quality is judgeable by reviewers. The "<2% of ComParE size, comparable performance" line is the citation that a small interpretable set is the right default.
- **Preprocessing recipe (D-H).** `pebble/audio/` = decode → resample 16 kHz mono → openSMILE `eGeMAPSv02` (18+7 LLDs → functionals) → 88-float vector → per-child z-normalize → cache. Thin wrapper over `opensmile-python` (audEERING), no C++ build. The same vector feeds a standalone acoustic head or late-fuses with NeoBERT's CLS embedding.
- **Cross-corpus / over-adaptation insurance.** Because Pebble's acoustic data will be small and domain-shifted (adult-trained norms → child voices), the paper's over-adaptation warning is the explicit reason to default to eGeMAPS-88 and treat ComParE-6373 as an ablation only. This is a guard against an acoustic head that looks good in-sample and collapses on real child clips.

### Child mental-health lens

- **One child-voice data point exists, and it's load-bearing.** FAU AIBO (§4.1.1) — children 10–13, spontaneous emotion — is in the GeMAPS validation, but **only binary valence was feasible** (the 5 original classes did not map to arousal), and AIBO was *excluded* from the headline Table 2 average. So eGeMAPS's strong arousal number is established on **adult** corpora; its child-voice evidence is valence-only and weaker (Table 3: eGeMAPS 73.4 UAR on AIBO valence). **Transfer risk:** the feature *vocabulary* transfers to children; the *performance numbers and any learned norms do not*. A jitter/shimmer/HNR/F0 model fit on adults will mis-fire on a 7-year-old.
- **Children's voices are acoustically a different regime.** Higher and more variable F0, shorter vocal tract (higher formants), naturally less stable phonation (higher baseline jitter/shimmer), and developmental change with age. eGeMAPS's semitone-F0 scale and formant/voice-quality LLDs are *defined* sensibly for children, but their affective *thresholds* are adult-calibrated. **Mitigation:** never reuse adult acoustic thresholds; re-fit/re-calibrate any acoustic head on child voice; treat age as a covariate; prefer per-child standardization (which the paper's protocol already uses) to absorb speaker-level offsets.
- **Arousal-first is also the safer child story.** Since the acoustic signal Pebble can trust most is arousal/`energy`, and arousal is *valence-ambiguous* (a child shouting with joy and a child shouting in distress are both high-arousal), the acoustic head must be **advisory, never a sole escalation trigger** — fully consistent with Pebble's "no learned safety head in v1" decision. Vocal cues (low HNR, high jitter, raised loudness) can *raise attention* (escalation-only, FAIIR-style) but a clinician/guardian pathway makes the call.
- **Privacy via feature reduction.** Raw child voice is biometric (voiceprint-identifying). eGeMAPS reduces a clip to a **non-invertible 88-float vector**; Pebble should extract at ingest, store the vector, and delete the waveform — a concrete data-minimization policy that the open, fully-specified eGeMAPS definition makes auditable.
- **Silver-label regime extends to audio.** Pebble has no human-annotated child-voice arousal labels. Any acoustic `energy`/`severity` target is itself silver (transferred from adult intensity corpora or text-derived). eGeMAPS fixes the *feature* problem, not the *label* problem; the D-C/D-D label-transfer risk is unchanged and arguably worse for audio (no child-voice C-SSRS/WASSA labels exist at all).

### Limitations & open questions for Pebble

- **Contradiction / gap vs. Pebble's turn-level plan (functionals discard within-message dynamics).** eGeMAPS collapses a whole utterance to one static 88-vector via functionals (means, CVs, percentiles). Pebble scores **turn-level / mid-conversation**. A single voice message is one turn so this aligns at the message level — but if Pebble ever wants *intra-message* trajectory (distress rising across a 30-second clip), the functional summary throws exactly that away. The set deliberately contains almost no dynamic features (only rising/falling-slope stats and, in eGeMAPS, spectral flux). **Mitigation:** keep LLD *contours* if intra-message dynamics matter, or window the clip.
- **Contradiction vs. paper 29 framing and the rest of the set (modality + label mismatch).** Paper 29 lists eGeMAPS at 88 params / "25 LLDs" — this paper specifies it precisely as **18 GeMAPS LLDs + 7 extension LLDs = 25**, and the 88 count comes from the functional expansion, not from 88 distinct LLDs; the precise breakdown (62 + 26) lives only here. More importantly, every text paper in the set (01 FAIIR, 12 MentalBERT, 14–16 C-SSRS, 18–19 WASSA) is **text-only**, and *none* of their labels (C-SSRS, GoEmotions, WASSA intensity) are aligned to audio. There is no published child-voice corpus carrying Pebble's silver labels, so the acoustic head cannot be trained against Pebble's existing labels without a transcription+alignment step — a genuine gap, not an integration detail.
- **Valence is the weak axis — directly relevant to `emotion`.** eGeMAPS is mid-pack on valence (66.44, behind ComParE 67.17). Pebble's `emotion` head is fundamentally a valence/category task. The paper's own conclusion ("for valence further important parameters must be identified") is an explicit warning that **acoustics alone will not carry Pebble's emotion classification** — text must remain primary, audio supplementary.
- **No cross-corpus numbers — the experiment Pebble most needs is missing.** The paper *argues* minimal sets generalize cross-corpus but defers the actual cross-corpus experiment to future work ("In future studies it should be investigated, whether the proposed minimalistic sets are able to obtain better generalisation in cross-database…"). Pebble's adult→child shift is exactly a cross-corpus problem, and this paper provides motivation but **no measured transfer number**. Open question Pebble must answer itself: does eGeMAPS-trained `energy` survive an adult→child domain shift, and by how much?
- **SVM-era, not deep-learning.** All numbers are SVM-on-functionals. eGeMAPS as input to a modern neural head (or fused with NeoBERT) is unstudied here; the UAR bars are SVM bars, not neural ones. They bound expectation but are not directly Pebble's architecture.
- **Open question — child-voice calibration anchor (D-D / D-H).** FAU AIBO is the obvious child-voice anchor in this paper, but it is German, 10–13yo, Wizard-of-Oz, valence-only, and gated. The unfilled D-H slot remains: what consented, age-tagged child-voice set calibrates the acoustic head? Without one, the voice path stays heuristic like v1 `energy`. Worth confirming FAU AIBO / GEMEP licensing as a sanity/calibration set even if not a training source.
