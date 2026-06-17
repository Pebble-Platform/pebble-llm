# Paper 41 — Speech Emotion Recognition in Mental Health: Systematic Review of Voice-Based Applications

## 1. Bibliographic info

**Title:** Speech Emotion Recognition in Mental Health: Systematic Review of Voice-Based Applications

**Authors:** Eric Jordan (ObTIC, Sorbonne Université, Paris), Raphaël Terrisse (URCI Mental Health Dept, Brest Medical University Hospital; EA 7479 SPURBO, Université de Bretagne Occidentale), Valeria Lucarini (Université Paris Cité, IPNP / INSERM U1266; GHU-Paris Psychiatrie et Neurosciences, Hôpital Sainte-Anne), Motasem Alrahabi (ObTIC, Sorbonne), Marie-Odile Krebs (IPNP / GHU-Paris), Julien Desclés (Université Paris Cité), Christophe Lemey (corresponding; URCI Brest; SPURBO; IMT Atlantique, Lab-STICC).

**Year / venue:** *JMIR Mental Health* 2025; vol. 12, e74260. DOI 10.2196/74260. PROSPERO registration CRD420251006669.

**Keywords (verbatim):** "affective computing; machine learning; mental health; psychology; psychiatry; speech emotion recognition; voice".

**Frame for Pebble:** This is the **clinical-evidence scoping reference** for the Pebble thesis voice-message × mental-health intersection. It is NOT a method paper Pebble copies hyperparameters from; it is the systematic survey that (a) establishes that voice/acoustic emotion features carry real diagnostic signal for depression, suicide risk, and psychosis, (b) names which acoustic features predict which condition, (c) maps the dataset and modelling landscape, and (d) catalogues the open gaps (dataset scarcity, generalization, deployment) that scope and justify Pebble's voice-modality chapter. Pebble v1 is **text-only** (NeoBERT on transcribed/typed child messages); this paper is the evidence base for a **future voice-modality extension** and for honestly bounding what voice could add.

## 2. Problem motivation

The authors frame SER as a maturing field (origins in 1990s speech processing) now intersecting psychiatry, where "the links between individuals' emotional states and pathological diagnoses are of particular interest." The clinical premise: "Intonation, rhythm, pitch, and other acoustic features of speech convey subtle emotional cues, reflecting an individual's psychological well-being," and automated analysis of these cues "offers several advantages for improving patient care, enabling early detection of mental health issues, and enhancing the overall health care experience." SER's claimed advantages are that it is **noninvasive, objective, and amenable to automated/longitudinal monitoring** — a "noninvasive and objective window into patients' mental states."

The review's stated objective: "investigate the performance of tools combining SER and artificial intelligence approaches with a view to their use within clinical contexts and to determine the extent to which SER technologies have already been applied within clinical contexts."

## 3. Position in the literature

The authors situate the work at the convergence of three threads. First, **the history of SER** — categorical emotion models (Ekman's "big six": happiness, sadness, anger, fear, disgust, surprise; Plutchik's 8-primary "wheel of emotions" adding trust and anticipation plus an intensity dimension) versus **dimensional / continuous models** (the 2-D valence–arousal circumplex of Russell). They note categorical models dominate SER "as they offer well-defined categories that facilitate annotation and classification," while dimensional approaches "remain comparatively underexplored." Second, **the psychiatric shift from categorical to dimensional nosology** — DSM/ICD categories vs. the NIMH Research Domain Criteria (RDoC) and the Hierarchical Taxonomy of Psychopathology (HiTOP), both of which frame disorders as continua of dysfunction (internalizing / externalizing / thought disorders). Third, a **methodological operationalization unique to this review: the direct vs. indirect SER distinction** — *direct* SER explicitly recognizes emotion as a task (train/fine-tune on emotion-labeled data, then relate detected emotions to conditions); *indirect* SER uses emotionally-relevant acoustic features (e.g., openSMILE feature sets) in a mental-health classifier without any emotion label being used.

The claimed gap: "To the best of our knowledge, this study is the first systematic review to provide a synthesized overview of SER in psychiatry." A companion scoping review on the same intersection (Frontiers in Psychology 2025, "Speech analysis and speech emotion recognition in mental disease: a scoping review") appeared concurrently, underlining the topic's novelty.

## 4. Method — PRISMA systematic review

**Protocol.** PRISMA guidelines, pre-registered in PROSPERO (CRD420251006669). Risk of bias assessed with **QUADAS-2** (Quality Assessment of Diagnostic Accuracy Studies 2).

**Databases & search.** PubMed, IEEE Xplore, arXiv, and ScienceDirect, queried "up until February 2025." Search string (verbatim): `("emotion recognition" OR "affective computing" OR "emotional analysis") AND ("psychiatry" OR "psychology") AND ("speech" OR "voice")`. ✔ corroborated (PMC).

**Inclusion criteria (Textbox 1):** (1) analysis of a **speech / audio** signal; (2) a **direct or indirect emotion-recognition** component (indirect includes openSMILE feature-set use); (3) speech data from a **clinical context**.

**Exclusion criteria:** audio analyzed only jointly with another modality (e.g., text); no diagnosis/prognosis aspect (emotions studied in isolation without correlation to patient outcomes); pathology was **neurological rather than mental-health** (e.g., Alzheimer); review papers without an experimental component.

**Screening.** Two authors applied eligibility criteria; disagreements would escalate to the full group ("no such cases were encountered"). Title/abstract screen, then full assessment of whether the design includes a **direct evaluation of diagnostic performance** via ML metrics (F1, accuracy, AUC) or statistical correlation.

**PRISMA flow (Figure 3).** **3648 studies screened → 85 (2.33%) reports retrieved/assessed → 14 (20% of the 85) included.** ✔ corroborated (PMC). Most common exclusion reasons at the final step: "lack of speech analysis alone (ie, models using only text or a combination of audio and other modalities)" or "absence of a diagnostic perspective."

**Breakdown of the 14 included studies (Abstract + Results):**
- **Suicide risk / suicidal ideation (SI): 3/14 (21%)** ✔
- **Depression / mood disorders: 8/14 (57%)** ✔
- **Psychotic disorders: 3/14 (21%)** ✔
- ⚠ **Internal inconsistency to flag:** the Abstract gives 57% / 21% / 21%; the body-text PRISMA-results paragraph restates the same counts as "3 (18%)… 8 (53%)… 3 (18%)" — these percentages do not sum and disagree with the abstract. The **counts (3 / 8 / 3 of 14)** are the authoritative figures; the body-text percentages are a typo. Status: counts ✔ corroborated; body-text % ✖ (paper-internal error).

**QUADAS-2 risk of bias (Figure 4).** "Most of the included studies had a low risk of bias across all fields." Main exception: **patient selection — 5 studies high risk** (3 sampled only clinical populations with no control group; 2 lacked a representative sample). High applicability concern for patient selection in 2 cases; unclear concern in 4 studies. ✔ corroborated (PMC). Full QUADAS-2 in Multimedia Appendix 1.

## 5. Narrative review — methods, features, datasets

### 5a. Acoustic / prosodic feature families
- **Acoustic features** (millisecond timescale, physical sound-wave properties): frequency/pitch, intensity, spectral characteristics. **MFCCs** "capture the spectral characteristics of speech (ie, how energy is distributed across different frequencies)" — e.g., higher energy in mid/high frequencies for anger or joy.
- **Prosodic features** (longer timescale): **pitch contours** (variation in fundamental frequency F0 over time, distinguishing sadness from excitement), **speech rate**, **pauses**.
- **Formants** influenced by vocal-tract shape/tension (e.g., smiling shifts formant values).
- **Spectral**: MFCCs, spectral slope, formants, spectral flux.

### 5b. openSMILE toolkit
"Among the most prevalent tools used for acoustic feature extraction." Provides standardized **feature sets** — notably **eGeMAPS** (extended Geneva Minimalistic Acoustic Parameter Set), **emobase**, and **ComParE**. Strengths cited: ease of use and **standardization** ("allowing for more straightforward comparison between results") and **interpretability** vs. end-to-end models.

### 5c. Model families (chronological)
- **Traditional ML on handcrafted features:** SVM, k-NN, decision trees, random forest, logistic regression.
- **RNNs:** LSTM and bidirectional LSTM (temporal dependency capture).
- **CNNs on spectrograms** (post-2012).
- **Transformers / SSL:** "the state-of-the-art approach," including BERT-style and **wav2vec 2.0**; one cited hybrid 2D-CNN+LSTM self-attention model on MFCCs reached "average test accuracy of 90%." Multimodal **CLAP** (contrastive language-audio pretraining) noted as a 0-shot-capable frontier architecture (but multimodal works were excluded from the 14).

### 5d. Datasets surveyed (general SER; **note: "few to no datasets are available that serve both SER and mental health applications"**)
| Dataset | Type | Size / detail | Relevance |
|---|---|---|---|
| **DAIC-WOZ** | clinical semistructured interviews (audio+transcript) | 193 interviews, 5–20 min each, North-American English; depression/anxiety/PTSD distress questionnaires (PHQ-8) | the one genuinely clinical dataset; used by multiple depression studies |
| **RAVDESS** | acted multimodal (audio+face), speech+song | 7365 recordings (4320 speech / 3036 song), 24 actors, 2 intensity levels + neutral | general SER, acted |
| **FAU-AIBO** | **spontaneous speech from German children** interacting with a robot | word-level annotation of **11 emotional states** by 5 judges; INTERSPEECH 2009 Challenge; "significant challenge… even for state-of-the-art methods" | only child-speech corpus mentioned — directly relevant to Pebble's child register |
| **IEMOCAP** | acted+improvised multimodal (audio+motion capture) | ~12 h; both categorical and dimensional labels | general SER benchmark |
| **CaFE** | Canadian-French acted emotional speech | 12 actors, 6 Ekman emotions + neutral, ~69 min | illustrates scarcity of non-English resources |

The authors stress the **English/Mandarin dominance** and single-cultural-context composition of these datasets as a generalization risk.

## 6. Results by pathology (the load-bearing evidence)

### Suicide risk / SI (3 studies)
- **Gerczuk et al [19]** — sex-specific suicide-risk classification with interpretable (acoustic) + deep features; best result from an **emotion-fine-tuned wav2vec 2.0**, **81% balanced accuracy** (high- vs low-risk), achieved by **training separately per sex**. Direction-of-effect differs by sex: agitation → ↑suicide risk in males, opposite in females. Predictive spectral features: **spectral slope (0–500 Hz), alpha ratio, F1 bandwidth.** ✔ corroborated (81% balanced accuracy, PMC).
- **Gideon et al [20]** — natural phone conversations, recently-discharged patients; SER classifier on acoustic features using **PANAS** self-report emotion labels. Max **AUC 0.78** classifying emotion labels; **AUC 0.79** using **emotional variability** to separate SI vs others. Finding: SI group showed **lower emotional variability**. ✔ corroborated (AUCs, PMC). (Note: this is the *speech→emotion→pathology* indirect pipeline.)
- **Belouali et al [3]** — US veterans; acoustic + prosodic + linguistic features, multiple models (random forest, logistic regression, deep NN), feature selection. Best (acoustic + linguistic): **sensitivity 0.86, specificity 0.70, AUC 0.80.** SI voices: **lower SD of energy contours in voiced segments, lower kurtosis/skewness** → "flatter and less animated… more monotonous voices." ✔ corroborated (0.86 / 0.70 / 0.80, PMC).
- **Overall suicide signal:** "AUC approximately 0.8 and accuracy approximately 80%."

### Depression / mood disorders (8 studies — the plurality)
- **Wang et al [6]** — DAIC-WOZ + PHQ-8; SVM/RF vs. transformer; best = complex transformer, **accuracy 77%, F1 0.63** (transformers > traditional ML on same data).
- **Yang et al [46]** — bipolar vs unipolar depression vs control; emotion profiles from an SVM trained on eNTERFACE, fed to LSTM+BiLSTM; **77% 3-way accuracy.**
- **Yang et al [47]** (2013) — major depressive disorder over 21 weeks; **switching-pause duration + F0**; as depression severity ↓, **pause duration shortened & became less variable**, accounting for **32% of within-subject variance** in depression scores; linear discriminant classifier **69.5% accuracy** on severity.
- **Stepanov et al [48]** — AVEC 2017 / DAIC-WOZ PHQ-8 regression; best = **low-level openSMILE features → LSTM**; **spectral features more predictive than prosodic or voice-quality.**
- **Mao et al [49]** — DAIC-WOZ prosodic features (glottal flow, voice quality, spectral); hybrid DL model **98.7% accuracy, F1 0.987** ("almost perfectly distinguish… control and depression groups"). ✔ corroborated (98.7% / 0.987, PMC). ⚠ outlier-high (see §10).
- **Yang et al [50]** — transformer on frequency parameters, DAIC-WOZ + proprietary; **F1 0.78 (DAIC-WOZ) and 0.87 (proprietary)**; **600–700 Hz band most important** (Mandarin vowel /e/ or /ɤ/) — proposed as a depression biomarker.
- **Zhou et al [21]** — older adults with MCI (depression/anxiety/apathy); **F2 and spectral flux negatively associated with depression**; **higher MFCC 4 positively associated** with depression.
- **Trend (2013 → 2023):** accuracy rose from **69% (2 prosodic features, 2013) → 98% (rich prosodic features + DL, 2023)**.

### Psychotic disorders (3 studies)
- **Chakraborty et al [51]** — schizophrenia vs control via **openSMILE emobase**; best = **linear SVM + PCA, 79.49% accuracy** (vs 66.67% majority-class baseline). NSA-16 negative-symptom-item prediction: **62%–85% accuracy** (SVM/KNN/decision trees). ✔ corroborated (79.49%, PMC).
- **Çokal et al [18]** — schizophrenia ± formal thought disorder (FTD), first-degree relatives, controls (15 each, n=60); **pause analysis** (duration, filler presence, syntactic context). Schizophrenia without FTD → more **unfilled pauses**; FTD → longer **utterance-initial pauses**.
- **de Boer et al [53]** — **eGeMAPS + random forest**; **86% accuracy** schizophrenia-spectrum vs control, **74%** negative- vs positive-symptom patients; argues for "validating language features as biomarkers in psychiatry." ✔ corroborated (86%, PMC).
- **Notable gap the authors flag:** "**none of the works included in the reviewed sample involved a direct analysis of emotions in the context of psychotic disorders**" — psychosis evidence is entirely *indirect* SER.

### Biomarker synthesis (Overview of Biomarkers)
- **Prosodic/temporal:** pitch (F0), energy, pause patterns, speech rate. Shorter/less-variable pauses ↔ rising depression severity [47]; longer utterance-initial pauses in FTD [18]; lower energy variability / flatter contours in suicidal speech [3].
- **Spectral:** MFCCs, spectral slope, formants, spectral flux; spectral slope/alpha-ratio/F1-bandwidth → suicide risk [19]; F2 + spectral flux (−) and MFCC 4 (+) → depression [21]; Mandarin-vowel formant bands → depression [50].
- **Model-driven importance:** voiced segments/second, spectral flux, pitch percentiles top-ranked for schizophrenia/depression; spectral > prosodic for PHQ [48].
- **Theme:** acoustic-feature models offered as **interpretable alternatives to end-to-end models** — an explicit performance-vs-interpretability trade.

## 7. Authors' stated open gaps & future directions

1. **Dataset scarcity & mismatch.** "Few to no datasets are available that serve both SER and mental health applications." The only genuinely clinical one (DAIC-WOZ) is small (193 interviews). Most SER datasets are **acted** (RAVDESS, IEMOCAP, CaFE), not spontaneous clinical speech.
2. **Generalization across populations/cultures/languages.** Datasets are overwhelmingly **English or Mandarin, single-cultural-context**; "variations in speech patterns, dialects, and cultural norms can impact… performance," demanding "robust validation and adaptation strategies… across different demographics."
3. **Lack of comparability / no shared challenges.** "The variety of methods… led to difficulties in directly comparing different studies, even those applied to the same pathologies." They call for **shared challenges** (cf. INTERSPEECH 2009, AVEC) to standardize datasets/features/metrics — blocked by "the sharing of confidential data."
4. **Interpretability vs. performance trade.** Complex models beat interpretable acoustic-feature models but resist clinical interpretation; "a trade-off must be found between classification performance and interpretability."
5. **Deployment / clinical-workflow integration.** "Translating NLP results into routine clinical practice… implying rapid, replicable, and scalable analysis, presents specific challenges," including recording/transcription inaccuracy and EHR-workflow integration. "Future work should focus on how clinicians can use these technologies **collaboratively**."
6. **Two proposed pipelines.** **(A) Speech → Pathology** (dominant in the literature; direct mapping). **(B) Speech → Emotion → Pathology** (rare; only Gideon [20]) — the authors **advocate (B)** because it "offers a clear interpretation of why a given classification was made" and supports collaborative clinical use; risk = SER-system error propagation, so SER-system selection is critical.
7. **Direct emotion analysis for psychosis** is unexplored.
8. **Within-subject / longitudinal monitoring** (ecological momentary assessment) is the named frontier, over between-subject diagnosis.

---

## Deep research — full-PDF read (2026-06-16)

> Read against the **published JMIR Mental Health version** (mental.jmir.org/2025/1/e74260; DOI 10.2196/74260) and the PMC mirror (PMC12521853). Local PDF is `pdfs/41-jordan-ser-mentalhealth-review.pdf` (the JMIR XSL-FO render). All load-bearing numbers below were cross-checked against the PMC HTML. This section adds the Pebble-specific judgment that §§1–7 above do not, and tags transferable parts with Decision IDs.

### Source-access note

- **PDF read:** `pdftotext "docs/papers/pdfs/41-jordan-ser-mentalhealth-review.pdf" -` → full body, all 4 figures' captions, both proposed pipelines, references. The diacritics garble in pdftotext (e.g., "Çokal" → "�okal", "eGeMAPS" intact) but numbers are clean.
- **Web validation:** WebSearch `Jordan Terrisse Lucarini "Speech Emotion Recognition in Mental Health" JMIR systematic review` → resolved the JMIR landing page and PMC12521853. WebFetch of PMC confirmed: 14 included / 3/8/3 breakdown / 3648 screened → 85 retrieved → 14 included / 5 high-risk patient-selection / and every headline metric (Gerczuk 81% bal-acc; Belouali 0.86/0.70/0.80; Mao 98.7%/0.987; de Boer 86%; Chakraborty 79.49%). DOI 10.2196/74260, PROSPERO CRD420251006669 confirmed.
- **Conflict note:** This is a *published* venue version, not a preprint — no preprint delta to reconcile. The one internal disagreement (abstract 57/21/21% vs body 53/18/18%) is a paper-internal typo; counts (3/8/3 of 14) govern.
- **Status tags:** ✔ corroborated against PMC; ≈ approximate / rounded; ✖ uncorroborated or paper-internal error.

### What the paper actually does

A **PRISMA systematic review** (PROSPERO-registered, QUADAS-2 bias scoring) of **voice-only** SER applied to mental-health diagnosis/prognosis. From **3648 screened → 85 retrieved → 14 included** (✔). Breakdown: **depression/mood 8/14 (57%)**, **suicide/SI 3/14 (21%)**, **psychosis 3/14 (21%)** (✔ counts; body-text percentages are a ✖ paper-internal typo). It contributes: (1) an **operational direct-vs-indirect SER taxonomy** (indirect = openSMILE features in a classifier with no emotion label; direct = explicit emotion recognition then related to pathology); (2) a **feature→condition biomarker map** (energy flattening/monotone prosody → suicide; pause shortening + F0 → depression severity; unfilled/utterance-initial pauses → schizophrenia±FTD; spectral slope/alpha-ratio → suicide; F2/spectral-flux/MFCC4 → depression); (3) a **two-pipeline proposal** advocating **Speech→Emotion→Pathology** over the dominant **Speech→Pathology** for interpretability. **Headline performance envelope: AUC ≈ 0.8 and accuracy ≈ 70–80% for between-group discrimination**, with handcrafted-feature + classical-ML (SVM/RF on openSMILE/eGeMAPS) still competitive with deep/SSL models, and one DAIC-WOZ depression outlier at 98.7%/0.987 (Mao [49], ✔ but see risk below).

**Key validated numbers:**
| # | Claim | Ref | Status | Trace |
|---|---|---|---|---|
| 1 | 14 studies included; 8 depression / 3 suicide / 3 psychosis | Abstract, Results (PRISMA) | ✔ | PMC12521853 (WebFetch) |
| 2 | 3648 screened → 85 retrieved → 14 included | Results, Fig 3 | ✔ | PMC12521853 |
| 3 | Gerczuk wav2vec2 = 81% balanced acc, sex-split suicide risk | Suicide §[19] | ✔ | PMC12521853 |
| 4 | Belouali SI = sensitivity 0.86 / specificity 0.70 / AUC 0.80 | Suicide §[3] | ✔ | PMC12521853 |
| 5 | Mao DAIC-WOZ depression = 98.7% acc / 0.987 F1 | Depression §[49] | ✔ (value) | PMC12521853 |
| 6 | de Boer eGeMAPS+RF schizophrenia = 86% acc; Chakraborty SVM 79.49% | Psychosis §[53],[51] | ✔ | PMC12521853 |
| 7 | 5/14 studies high QUADAS-2 risk on patient selection | Results, Fig 4 | ✔ | PMC12521853 |

### Parts directly useful for Pebble

1. **The emotion-representation menu (categorical Ekman/Plutchik vs dimensional valence–arousal) framed against psychiatric dimensional nosology (RDoC/HiTOP).** → **D-C, D-D.** The review explicitly aligns the **dimensional valence–arousal model** with severity-as-continuum psychiatry (RDoC, HiTOP internalizing/externalizing/thought-disorder spectra). This is independent external support for Pebble's **`severity` regression head** (continuous intensity) and for a **valence/arousal-style framing of the `emotion` head** rather than pure hard categorical labels. *Transfer risk:* HOLDS at the conceptual level (Pebble already chose a regression severity head); the **specific GoEmotions 12-label mapping** Pebble uses is categorical, so the dimensional argument supports the *severity* head more than the *emotion* head.
2. **The handcrafted-feature-beats-deep-model finding + interpretability trade.** → **D-A, D-B.** Across 14 studies, **classical ML on openSMILE/eGeMAPS features stayed competitive** (de Boer RF 86%; Chakraborty SVM 79.49%; Stepanov LSTM on openSMILE) and is offered as the **interpretable alternative to end-to-end models**. *Transfer risk:* PARTIAL — this is an **audio** finding; Pebble's input is **text**, where transformer encoders clearly dominate. But the **interpretability-vs-performance trade** the review elevates transfers directly to D-A (NeoBERT vs heavier backbones) and D-B (whether complex MTL balancing is worth its opacity for a child-safety tool that must be auditable).
3. **The feature→condition biomarker map, especially energy-flattening / monotone prosody → suicide and pause-pattern → depression severity.** → **D-D, D-G.** Belouali [3]: suicidal speech has **lower energy-contour SD, lower kurtosis/skewness** (flat, monotone). Yang [47]: **pause shortening + reduced variability tracks 32% of within-subject depression-severity variance.** *Transfer risk:* these are **acoustic** markers and **cannot be computed from Pebble's v1 text**. They scope a **future voice extension**, and they are the citation that **`energy` is a real construct** (currently heuristic in v1) — voice would make `energy` a learnable signal, not a guess.
4. **DAIC-WOZ as the canonical clinical-speech anchor + the dataset-scarcity gap.** → **D-H.** DAIC-WOZ (193 PHQ-8-scored interviews) is the single genuinely clinical corpus reused across the depression studies; the review's blunt verdict is "**few to no datasets… serve both SER and mental health**." *Transfer risk:* DAIC-WOZ is **adult, English, clinical-interview** register — not child companion-chat. It is a **calibration/transfer anchor candidate** for a future voice head, but not a child-register substitute.
5. **The Speech→Emotion→Pathology pipeline advocacy.** → **D-G, D-A.** The authors argue the indirect, two-stage pipeline (recognize emotion first, then map emotion→risk) is preferable for **clinical interpretability and collaborative use**. *Transfer risk:* HOLDS — this is **exactly Pebble's architecture**: an `emotion`/`severity` representation feeds a downstream Decision Engine, rather than a black-box message→risk classifier. The review is external clinical-evidence backing for Pebble's modular design choice.
6. **FAU-AIBO: spontaneous child speech is hard even for SOTA.** → **D-H, D-C.** The only child corpus mentioned (German children, 11 emotion states, 5 judges) "presents a significant challenge in achieving strong classification performance, even for state-of-the-art methods." *Transfer risk:* HOLDS as a **warning**, directly relevant to Pebble's child register — child emotional speech/text is a documented difficulty multiplier; severity/emotion accuracy bars set on adult data (D-C: 52% acc / 0.75 wF1 / 47.8% macro-recall) may not transfer down to children.

### How each part helps Pebble succeed

- **Severity head (D-C/D-D):** Cite this review's RDoC/HiTOP dimensional argument to justify the **regression severity head** in the thesis, and use the **pause-→-depression-severity (32% variance) and monotone-prosody-→-suicide** findings as the empirical motivation that "intensity/severity is acoustically real" — i.e., if/when Pebble adds voice, severity gains a directly-measurable substrate. Concretely: in the thesis voice chapter, position `severity` as the head most likely to benefit from an acoustic input.
- **`energy` head (currently heuristic, D-D):** This paper is the strongest single citation that **`energy` should eventually be learned from voice**, not heuristic. Belouali's energy-contour-SD finding gives a concrete feature (`std(energy_contour_voiced_segments)`) to extract from a future audio pipeline. Action: add a "v2 voice-extension" note to `energy`'s spec pointing at openSMILE eGeMAPS energy descriptors.
- **Backbone & MTL-balancing (D-A/D-B):** Use the review's interpretability-vs-performance framing to **defend NeoBERT-250M over a heavier model** and to **prefer a simpler, auditable loss-balancing scheme** for the child-safety context. The clinical-evidence point — that practitioners value interpretable handcrafted-feature models — supports keeping Pebble's stack legible.
- **Pipeline architecture (D-G/D-A):** Cite the Speech→Emotion→Pathology advocacy as **external validation of Pebble's modular emotion/severity → Decision Engine design** over an end-to-end message→risk model. This is a reviewer-facing argument: a respected JMIR review independently recommends exactly Pebble's separation of concerns for clinical interpretability.
- **Datasets / anchors (D-H):** Add **DAIC-WOZ** and **eGeMAPS/openSMILE feature sets** to the future-voice dataset register as the field-standard clinical-speech anchor and feature extractor; add **FAU-AIBO** as the cautionary child-speech benchmark. Do **not** treat any as a child-register text substitute for v1.
- **Performance-envelope realism (all):** Use **AUC ≈ 0.8 / accuracy ≈ 70–80%** as the honest **between-group ceiling** for voice-based mental-health discrimination in the thesis — and explicitly **discount the Mao 98.7% outlier** (see contradiction below) so Pebble does not set unrealistic voice expectations.

### Child mental-health lens

- **Transfer validity is low for v1, scoping for v2.** Every one of the 14 studies is **audio**, and **all but FAU-AIBO are adults** (veterans, MDD patients, schizophrenia patients, older adults). Pebble v1 is **text-only, child-facing**. So this paper transfers as **evidence and scoping for a future voice modality**, NOT as method Pebble executes now. State this plainly in the thesis: the voice chapter is **justified and bounded** by this review, not implemented from it.
- **Child speech is documented-harder.** FAU-AIBO (the only child corpus) is flagged as resistant to SOTA. Combined with the review's generalization gap (English/Mandarin, single-culture, mostly acted data), this is direct support for Pebble's caution that **adult-derived accuracy bars (D-C) will not transfer cleanly to children** and that a **child-register calibration slice is mandatory** before any deployment claim.
- **Interpretability is a child-safety requirement, not a preference.** The review's performance-vs-interpretability trade lands harder for a child-facing tool: a clinician/guardian-facing system should prefer the **auditable Speech→Emotion→Pathology** decomposition Pebble already uses. The black-box 98.7% model is exactly what Pebble should *not* be.
- **Ethics: confidential-data sharing is the field's blocker.** The authors name "sharing of confidential data" as the main obstacle to shared challenges. For **children's voice** — biometric, identifying, and developmentally sensitive — this is sharper still. Pebble's voice extension must plan for on-device or in-infrastructure processing, guardian consent, and non-release, consistent with the governance pattern paper 01 (FAIIR) established for child text.
- **No safety/recall-floor evidence here.** This review reports **discrimination metrics (AUC/accuracy)**, never recall floors or calibration. It cannot inform Pebble's recall ≥ 0.95 safety policy (D-G); that remains a v2 question sourced elsewhere (C-SSRS/FAIIR).

### Limitations & open questions for Pebble

- **Contradiction #1 — the Mao 98.7% / 0.987 outlier vs the field envelope.** The review's own synthesis says "AUC ≈ 0.8, accuracy ≈ 70–80%," yet reports Mao et al [49] at **98.7% accuracy / 0.987 F1** on DAIC-WOZ depression. A 98.7% on a 193-interview corpus with 5/14 studies already flagged high-risk on patient selection is almost certainly **overfitting / optimistic small-sample evaluation**, and the review presents it uncritically next to far more modest numbers. **For Pebble:** do **not** cite 98.7% as an achievable voice ceiling; cite the **0.8 AUC / 70–80% accuracy** envelope. This is the explicit gap — the review aggregates incomparable studies without harmonizing evaluation rigor (which is itself one of its stated limitations: "difficulties in directly comparing different studies").
- **Contradiction #2 — dimensional-emotion advocacy vs Pebble's categorical `emotion` head.** The review argues the **dimensional valence–arousal** model is the more clinically-aligned representation and that categorical models merely "facilitate annotation." Pebble's `emotion` head is **categorical (12-label GoEmotions-mapped)**. The review supports Pebble's **severity** (dimensional) head but creates tension with the **emotion** head's categorical choice — a gap to address in the thesis: justify GoEmotions categories on engineering/label-availability grounds while acknowledging the review's dimensional preference.
- **Modality gap vs Pebble's whole v1.** This paper is **audio-only by inclusion criterion** (text-inclusive studies were *excluded*). Pebble v1 is **text-only**. The two are complementary, not overlapping — the paper cannot validate any text-encoder choice; it only scopes the voice extension. Treat it as the **voice-chapter evidence base**, not a method baseline.
- **Turn-level / mid-conversation absent.** Every study is **between-subject diagnosis** or session-level (the review names within-subject/longitudinal monitoring as a *future* direction). Pebble scores **turn-level, mid-conversation**. The review's metrics are session/subject-level and are **not comparable bars** for Pebble — only directional evidence that voice carries emotion/severity signal.
- **Child register: the gap Pebble can own.** The review documents that child speech (FAU-AIBO) is hard and that the field has **almost no child mental-health speech data**. A child-register voice/text emotion-severity resource and any analysis of how children indirectly voice distress would be a genuine contribution this review shows is missing — mirroring the same youth-register gap paper 01 (FAIIR) left open for text.
- **Open question worth pursuing:** whether DAIC-WOZ's PHQ-8 severity labels and eGeMAPS features could seed a **transfer-learning anchor** for Pebble's future voice `severity` head — promising for adults, unproven for children, and dependent on the documented child-speech difficulty.
