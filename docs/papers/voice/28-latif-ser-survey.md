# Paper 28 — Survey of Deep Representation Learning for Speech Emotion Recognition

## 1. Bibliographic info

**Title:** Survey of Deep Representation Learning for Speech Emotion Recognition

**Authors:** Siddique Latif (University of Southern Queensland / Distributed Sensing Systems Group, Data61–CSIRO), Rajib Rana (USQ), Sara Khalifa (Data61–CSIRO / UNSW / University of Queensland), Raja Jurdak (Trusted Networks Lab, Queensland University of Technology), Junaid Qadir (Qatar University / Information Technology University Lahore), Björn W. Schuller (GLAM — Imperial College London / University of Augsburg). Corresponding: siddique.latif@usq.edu.au.

**Year / venue:** *IEEE Transactions on Affective Computing* (T-AFFC), vol. 14, no. 2, pp. 1634–1654, 2023. DOI 10.1109/TAFFC.2021.3114365. The local PDF is the accepted-manuscript version (QUT ePrints 213410, CC BY-NC 4.0); the camera-ready was accepted 2021 and assigned to the 2023 issue.

**Keywords (verbatim):** "Speech emotion recognition, multi task learning, representation learning, domain adaptation, unsupervised learning".

**Type:** Survey / landscape review. The authors position it as "the first comprehensive survey on the important topic of deep representation learning for SER," distinct from prior SER surveys that either focus on hand-engineered features or cover representation learning generically without an SER focus (Table 1, comparing against Bengio et al. 2013, Zhong et al. 2016, Basu et al. 2017, Swain et al. 2018, Akçay et al. 2020).

## 2. Why this paper for Pebble

Pebble's thesis includes (or will include) a **voice-modality / speech-emotion-recognition (SER) chapter** alongside the text encoder. This survey is the *positioning/landscape reference* for that chapter: it gives the taxonomy of feature types, the architecture families (CNN / RNN / CNN-RNN / attention / generative / SSL), the canonical English datasets with their label schemes, the standard evaluation metrics (UA/UAR, CCC), and the field's open challenges — all in one citable place from a top-tier venue with Schuller (the field's central figure, founder of the Interspeech ComParE challenge series) as senior author.

Two caveats that frame everything below:
- **Vintage.** Accepted 2021. It predates the SSL-on-raw-audio era that now dominates SER (wav2vec 2.0 / HuBERT / WavLM fine-tuning). SSL appears only as a short, forward-looking subsection (§3.4.3) flagged as "needs exploration in SER." For current SSL-SER numbers, Pebble's chapter must lean on newer papers (e.g. #24 MMER, #27 Morais SSL-SER, #40 wav2vec2-depression) — this survey is the *map of the territory before SSL*, not the SSL state of the art.
- **Scope.** It is a *representation-learning* survey, not an architecture leaderboard. SOTA numbers are scattered through Table 5 as illustrative points, not curated bests; they are not directly comparable across rows (different splits, features, fold protocols).

## 3. Taxonomy of feature types (§2.1, §5.1)

The survey frames the whole field as a migration **from feature engineering to representation learning**:

- **Hand-engineered acoustic features** (the legacy paradigm):
  - **MFCCs** — "the principal set of features for SER and other speech analysis tasks" for decades. Four steps: FFT → Mel-scale power projection → log → DCT. The last (DCT) step "loses information and destroys spatial relations," so it is "usually omitted, which results in the **LogMel spectrum**" — the single most popular feature for training DL networks in speech.
  - **Minimalist standardized sets:** **GeMAPS / eGeMAPS** (Eyben, Schuller et al.) — designed to (a) index affective physiological changes in voice production and (b) be automatically extractable; widely used as benchmarks.
  - **Challenge feature sets:** **IS09–IS13** (the Interspeech 2009–2013 ComParE/paralinguistics feature sets) and **LLDs** (low-level descriptors) appear throughout Table 5 as the standard inputs.
  - Categories named: **spectral features, prosodic features, voice-quality features** (Fig. 1).
- **Raw speech** as direct input to deep models — emerging; "requires enormous data to achieve competitive performance," mitigated by data augmentation. CNN early layers act as a "data-driven filterbank."
- **Learned representations** — the focus of the survey: hierarchical, abstract features learned automatically, "less time consuming … requires minimal human domain knowledge," with more generalisation ability and no per-task feature redesign (Table 2).

**Key field conclusion (§5.1):** recent studies show "deep representation learning techniques can extract discriminative representations and a particular choice of input features is not as important as the model architecture." LogMel/spectrograms remain popular because they "need less processing, fewer data samples, and training to achieve state-of-the-art classification performance compared to setups where raw audio is used" (Table 5 shows hand-engineered features are still more common than raw speech as input).

## 4. Taxonomy of architectures (§2.3, §5.2)

The DL-model taxonomy (Table 3 characteristics):

- **DNNs (fully-connected):** learn a hierarchy of distributed representations; higher layers give invariance to local input changes. Early SER use: utterance-level representation from segment-level DNN posteriors + ELM classifier (Han et al.), reported **20% classification improvement** on IEMOCAP over hand-engineered baselines.
- **CNNs:** specialised for grid-like topology (spectrogram = 2D, waveform = 1D). Variants **ResNet** and **DenseNet** are "especially popular in SER." CNN filters "capture emotions related to the fundamental frequency"; robust against noisy conditions.
- **RNNs (LSTM / GRU / BLSTM):** model temporal context; gating solves vanishing gradients; BLSTM models past+future. Lee et al.'s BLSTM reported **12% improvement** over DNN-ELM. RNN-CTC models also help.
- **CNN-RNN (CNN-LSTM / CNN-GRU):** the dominant supervised recipe — CNN for feature extraction, LSTM/GRU for long-term dependencies; shown "a better choice in contrast to using CNN or LSTM individually."
- **CapsNets:** sequential capsule structures for utterance-level representations; beat CNN-LSTM baseline on IEMOCAP.
- **Attention:** self-attention, local attention, multi-hop attention — "enable networks to focus on affect-salient components."
- **Autoencoders:** AE, **sparse AE** (can learn representations larger than input; "simple to train and can learn better representation compared to DAE and RBMs"), **DAE** (denoising — robust to noisy speech), **AAE** (adversarial AE).
- **Generative:** **DBN/RBM** (early), **VAE** (disentangled emotional representations), **GAN** (synthetic data generation; "convergence issues" are a recurring problem).
- **Transformers:** treated as *future direction* (§5.2) — "Emotions in speech are also contextually dependent. Therefore, Transformers need to be explored in SER." This is the dated framing: by 2023 transformers (and SSL transformers) were already dominant.

## 5. Taxonomy of learning paradigms (§3) — the survey's spine

Studies are clustered into five groups by *how* the representation is learned (Table 5 summarises all reviewed studies as Corpus / Input / Model / Performance):

1. **Supervised representation learning (§3.1):** learn from labelled samples. Best performance but "limited by the requisite of labels … creating and labelling these datasets is very expensive."
2. **Unsupervised representation learning (§3.2):** AEs, DAEs, VAEs, GANs, AAEs on unlabelled data. Verdict: "the performance of unsupervised representation learning techniques is **not as good as that of the supervised methods**."
3. **Semi-supervised representation learning (§3.3):** combine labelled + unlabelled, e.g. **ladder networks** (an unsupervised DAE trained jointly with a supervised head). Reported gains: ladder networks give "relative gains in CCC of 3.0% to 3.5% for within-corpus, and 16.1% to 74.1% for cross-corpus settings" (MSP-Podcast / IEMOCAP / MSP-IMPROV). Caveat: "blind training … may not necessarily improve the performance over supervised learning"; unlabelled data "only help in certain favourable situations … noisy and biased unlabelled data can even lead to worse performance."
4. **Representation transfer learning (§3.4):** the richest section, split into:
   - **Domain-adaptive (§3.4.1):** shared-hidden-layer AEs, **DANN** (domain-adversarial neural network with gradient-reversal layer), adversarial cross-corpus/cross-language methods. Cross-lingual DANN with a language classifier achieved "3.91% improved accuracy" over a naïve cross-lingual baseline on IEMOCAP/RECOLA.
   - **Multi-task representation learning (§3.4.2):** auxiliary tasks (arousal/valence, gender, speaker, naturalness) improve the main emotion task. Reported: MTRL with secondary-emotion auxiliary gives "**7.9% relative improvement in F1**" on an 8-class MSP-Podcast task; gender-auxiliary multi-head attention reached "**70.1% UA** … 5.3% higher than the state-of-the-art" for 4-class; speaker+gender auxiliary LSTM "5.5% relatively higher accuracy" on IEMOCAP; joint arousal/valence/dominance prediction gains "CCC as high as 4.7% within-corpus and 14.0% cross-corpora." Key property: MTRL gives "**no major increase in computational power** while improving recognition accuracy and decreasing the chance of overfitting."
   - **Self-supervised (§3.4.3):** "a new paradigm … needs exploration in SER." Cited examples: visual-guided SSL for speech; multi-task SSL encoder + multiple workers; transformer SSL fine-tuned from a masked-language-modelling task improves multimodal emotion recognition by **3% on CMU-MOSEI**.
5. **DRL for representation learning (§3.5):** deep reinforcement learning enables *exploration* (which static methods lack) and could disentangle factors of variation — but "the problem of emotional representation learning for improving SER is **not explored using DRL**." Flagged as a future direction.

## 6. Datasets table (Table 4) — exact label schemes

Table 4 ("Review of different SER databases") is the survey's canonical corpus list. (Note: the PDF's Table 4 cell alignment is partially garbled in text extraction; the corpus set and schemes below are recovered from the table plus body text. RAVDESS and CREMA-D are *not* in Table 4 — they appear only in the §3.3 body text on semi-supervised GANs.)

| Corpus | Language | Mode | Type | Emotion scheme | Public |
|---|---|---|---|---|---|
| **EMODB** | German | audio | simulated (acted) | discrete (anger, boredom, disgust, fear, happiness, sadness, neutral) | yes |
| **MSP-IMPROV** | English | audio | stimulated/induced | discrete (anger, happiness, sadness, neutral) | yes |
| **MSP-Podcast** | English | audio | naturalistic | discrete + dimensional (arousal, valence, dominance) | yes |
| **SEMAINE** | English | audio, video | induced | dimensional + social-behaviour labels | yes |
| **IEMOCAP** | English | audio (+video) | stimulated (scripted + improvised) | discrete (happy, sad, angry, neutral …) + dimensional (aro/val/dom) | yes |
| **EMOVO** | Italian | audio | simulated | discrete (disgust, happiness, fear, anger, surprise, sadness, neutral) | yes |
| **RECOLA** | French | multimodal | natural | dimensional (arousal, valence, dominance) | yes |
| **CMU-MOSEI** | English | audio, video | natural | dimensional / 5 affective dimensions (valence, activation, power, anticipation, intensity) | yes |

**Body-text corpora also referenced:** **ABC corpus**, **TED talks**, **BUAA emotional corpus**, **FAU-AIBO**, **PRIORI emotion dataset**, **GeWEC**, **CREMA-D**, **RAVDESS**.

**Validated canonical sizes** (✔ corroborated externally, since Table 4's numeric cells are unreliable in extraction):
- **IEMOCAP:** ~12 hours, **5,531 usable utterances**, 10 speakers (5M/5F) across 5 sessions, scripted + improvised dyadic conversations; the dominant SER benchmark, typically used 4-class (happy/sad/angry/neutral). ✔
- **MSP-Podcast:** naturalistic, podcast-sourced; large and growing (releases reach ~235 hours; 610 train / 30 dev / 50 test speakers in a later release). ✔
- **RAVDESS:** 24 actors (12M/12F), 1,440 utterances, 8 emotions (calm, happy, sad, angry, fearful, surprise, disgust, neutral). ✔
- **CREMA-D:** 91 actors (48M/43F), 7,442 clips, 6 emotions (anger, disgust, fear, happy, neutral, sad). ✔

## 7. Evaluation metrics (§2.5) — the SER measurement convention

- **Classification:** accuracy, but because naturalistic emotion corpora are **class-imbalanced**, the field standard is **unweighted accuracy (UA) / unweighted average recall (UAR)** — "the average recall across classes, unweighted by the number of instances per class." Introduced by the **Interspeech 2009 Emotion Challenge** (Schuller) and used by every subsequent challenge. (WA = weighted accuracy and F1 also appear.)
- **Regression (dimensional arousal/valence/dominance):** optimise **MSE** loss, report **CCC (concordance correlation coefficient)** as the headline metric.

This is load-bearing for Pebble: **UAR, not accuracy, is the correct primary metric** for an imbalanced emotion classifier, and **CCC** is the field-standard for any continuous severity/intensity head — directly relevant to Pebble's `severity` regression head.

## 8. SOTA / illustrative numbers cited (Table 5)

These are illustrative within-paper bests, *not* a curated leaderboard, and are **not cross-comparable** (different splits/folds/features). Tagged with validation status.

- IEMOCAP, **Transformer on Wav2Vec features: 70.1% UA** (Table 5, Lotfian et al. row) — the highest IEMOCAP UA in the table. ≈ approximate (Table 5 extraction is mangled; the value 70.1% appears twice, also for the gender-MTL result; treat as "best-reported ~70% UA" rather than a precise attributed number).
- IEMOCAP, CNN-LSTM: 66.8% UA; BLSTM: 62–66%; DNN baselines ~59–61% UAR. ≈ approximate.
- DBN fusion with hand-engineered features: +5.48% to +8.8% over classical features (EMODB / cross-corpus). ✔ (consistent with body text).
- MTRL F1 +7.9% relative (8-class, MSP-Podcast); gender-MTL +5.3% UA; speaker/gender-MTL +5.5% accuracy. ✔ (body text §3.4.2).
- SSL transformer (MLM pretext) +3% on CMU-MOSEI multimodal. ✔ (body text §3.4.3).
- Cross-corpus GAN: 61.05% (within-corpus) / 46.60% (cross-corpus) accuracy — illustrating the **large within→cross-corpus drop**. ✔ (body text §3.2).

**The single most important pattern:** within-corpus numbers cluster ~60–70% UA on IEMOCAP, but **cross-corpus / cross-language performance collapses** (e.g. 61% → 47%). This generalisation gap is the field's defining open problem (§4.3) and the most transferable lesson for Pebble.

## 9. Open challenges (§4) and future directions (§5, Table 6)

Five challenges, each with "solutions explored / existing gaps / future directions" (Table 6):

1. **Training complexity (§4.1):** speech manifolds entangle message + speaker + gender + age + health + mood + emotion; disentangling emotion is "a long-standing goal." Unsupervised training is harder than supervised and "can potentially ignore emotional attributes."
2. **Lack of emotional speech data (§4.2):** corpora are small, mostly lab-recorded **acted** emotions that "may not represent real-life human emotions"; raters annotate **'outer emotion'** which "can be highly different from the 'inner emotion'." Noise (background, mic) corrupts data; noise-injection only works for moderate SNR.
3. **Corpus and lingual variance (§4.3):** the generalisation gap — "performance … drops significantly if the test samples deviate from the distribution of the training data," worse across languages. >5,000 spoken languages exist; 389 cover 94% of the population, yet corpora are missing even for most of those. Few-shot and language-invariant representations are proposed but "a fully satisfactory solution has not yet emerged."
4. **Privacy and robustness (§4.4):** speech leaks gender, ethnicity, emotional state, identity; voiceprints enable spoofing. Mitigations: privacy-preserving representation learning, **on-device/edge** feature extraction, **federated learning**. SER models are also vulnerable to **adversarial attacks** (FGSM, JSMA, DeepFool); very deep architectures are found relatively robust.
5. **(Future) DRL, multi-modal, transformers, generative-synthetic-data, SSL** as the named research frontiers (§5, Conclusions).

## 10. How Pebble should position its voice-modality contribution

This section is the deliverable: where a Pebble SER chapter sits on this map and how to frame its novelty.

**Positioning statement.** Pebble's voice modality sits at the intersection the survey explicitly flags as under-explored: **(a) self-supervised / transfer representation learning (§3.4.3 — "needs exploration in SER")** applied to **(b) a real-world, in-the-wild, child-facing deployment** (§4.2's "emotion recognition in the wild" need), with **(c) multi-task heads** (§3.4.2 MTRL — the survey's strongest empirical story) and **(d) explicit generalisation/robustness handling** (§4.3, the field's defining gap). Pebble can claim contribution on *every one of these four axes the survey lists as open*, while honestly conceding it does not advance core representation-learning theory.

Concrete positioning moves for the chapter:

1. **Frame the encoder choice against the survey's CNN-RNN-then-SSL arc.** The survey establishes CNN-LSTM as the 2021 supervised default and SSL transformers as the open frontier. Pebble's SER head should be built on a **pretrained SSL audio encoder** (wav2vec2 / HuBERT / WavLM) — i.e. exactly the "self-supervised representation learning … needs exploration in SER" gap — and cite this survey as the statement of that gap, then cite the newer SSL-SER papers (#24, #27, #40) for the realisation. **(D-A:** the encoder-backbone decision generalises across modalities — the survey is the citation that "representation learning beats feature engineering, architecture matters more than input features," supporting a strong-pretrained-backbone-first policy for both the NeoBERT text encoder and any audio encoder.)

2. **Adopt UAR as the primary metric and CCC for any continuous head.** The survey (§2.5) is the canonical citation that **UA/UAR — not accuracy — is mandatory under class imbalance** (Interspeech-2009-challenge convention), and that **CCC** is the field metric for dimensional/intensity regression. Pebble's `emotion` head must report **macro-recall / UAR** (already its bar: 47.8% macro-recall) and Pebble's `severity` regression head should report **CCC (and Pearson)**, not just MSE/MAE. **(D-C, D-D:** this fixes the metric for the severity/emotion heads to the field standard, making Pebble's numbers comparable and citable.)

3. **Lead with multi-task representation learning as the empirically-justified design.** The survey's strongest, most consistent positive result is MTRL: **+7.9% F1, +5.3–5.5% UA, +4.7–14% CCC** from auxiliary tasks, with **"no major increase in computational power"** and reduced overfitting. This is direct external support for Pebble's multi-head MTL design (emotion + severity + the heuristic heads sharing one encoder). **(D-B:** the survey corroborates that MTL helps under-resourced emotion tasks — Pebble's shared-encoder multi-head plan is the well-trodden path, and the "auxiliary task with abundant data improves the label-scarce main task" finding (Latif et al. ref in §3.4.2) is the citation for using a high-resource auxiliary, e.g. arousal/valence or gender, to lift Pebble's scarce child-emotion signal.)

4. **Make cross-corpus generalisation the headline evaluation, not within-corpus accuracy.** The survey's single biggest cautionary result (61%→47% cross-corpus collapse, §3.2/§4.3) means a within-IEMOCAP number is *worthless* as evidence for a child-facing product. Pebble's SER chapter should **report cross-corpus / out-of-distribution evaluation as the primary result** and cite domain-adaptation / DANN methods (§3.4.1) as the mitigation toolbox. **(D-D, D-H:** transfer-source and dataset/calibration decisions must assume a generalisation gap; the survey is the citation that adult-acted-corpus performance does NOT transfer to in-the-wild child speech without explicit domain adaptation.)

5. **Own the "in-the-wild + inner-vs-outer-emotion + child" gap as the contribution.** §4.2 states corpora are lab-acted, rater-annotated *outer* emotions far from *inner* emotion; §4.3 states real-world generalisation is unsolved. A child-facing, naturalistic, *silver-labelled* SER setup is squarely in the unaddressed space — Pebble can claim novelty precisely on the population (children), the register (naturalistic in-app speech), and the label regime (silver/LLM rather than expert-rater outer-emotion). No paper in this survey covers child speech.

## 11. Recommended citation use

In a Pebble paper, this survey supports these claims:

- **"Representation learning has superseded feature engineering in SER; architecture matters more than the choice of input feature."** (§2.1, §5.1). Cite to justify a learned-encoder approach over GeMAPS/MFCC pipelines.
- **"UA/UAR is the standard imbalance-robust metric in SER (Interspeech-2009 convention); CCC is standard for dimensional emotion regression."** (§2.5). Cite for Pebble's metric choices on the emotion (macro-recall) and severity (CCC) heads.
- **"Multi-task representation learning improves the main emotion task with auxiliary tasks (gender/speaker/arousal-valence) at no major compute cost and reduced overfitting."** (§3.4.2). Cite to motivate Pebble's shared-encoder multi-head MTL.
- **"Cross-corpus and cross-language SER performance degrades sharply relative to within-corpus."** (§3.2, §4.3). Cite to justify out-of-distribution evaluation and domain adaptation as central, not optional.
- **"Self-supervised representation learning is an under-explored but promising frontier for SER."** (§3.4.3, Conclusions). Cite to position an SSL-audio-encoder Pebble SER head as filling a named gap.
- **"SER corpora are predominantly lab-acted, capturing 'outer' rather than 'inner' emotion, limiting real-world generalisation."** (§4.2). Cite to motivate naturalistic / in-the-wild data collection and to honestly bound expectations.
- **Canonical English SER dataset roster + label schemes** (Table 4: EMODB/MSP-IMPROV/MSP-Podcast/SEMAINE/IEMOCAP/EMOVO/RECOLA/CMU-MOSEI). Cite as the established benchmark set when describing Pebble's choice of pretraining/eval corpora.

**Do NOT cite this survey for:** current SSL-SER state-of-the-art numbers (it predates the wav2vec2/HuBERT-SER era — use #24/#27/#40), any child-speech result (none exist here), any specific leaderboard ranking (Table 5 is illustrative, not curated), or transformer-SER results (treated as future work, not surveyed).

## Deep research — full-PDF read (2026-06-16)

### Source-access note

The local PDF (`pdfs/28-latif-ser-survey.pdf`, 9.7 MB) is the **accepted-manuscript** version downloaded from QUT ePrints (eprints.qut.edu.au/213410/, "Emotional_Representations_Review_minor_revision_2_3.pdf"), CC BY-NC 4.0, with a banner warning it "may not be the Version of Record." Text was extracted with `pdftotext -layout` (1,628 lines) and read in full (Introduction → §2 Background/Concepts → §3 the five representation-learning paradigms → §4 Challenges → §5 Discussion/Future → §6 Conclusions → references).

Web-validated:
- **Bibliographic record** — query "Latif Rana Khalifa Schuller Survey of Deep Representation Learning for Speech Emotion Recognition IEEE Transactions Affective Computing 2023". Resolved: https://eprints.qut.edu.au/213410/ and https://opus.bibliothek.uni-augsburg.de/opus4/files/91554/91554.pdf. Confirms **T-AFFC vol. 14(2), pp. 1634–1654, 2023, DOI 10.1109/TAFFC.2021.3114365** (the local accepted-manuscript matches the venue record). ✔
- **Dataset canonical sizes** (Table 4's numeric cells are garbled in PDF extraction, so external corroboration was required) — query "IEMOCAP MSP-Podcast RAVDESS CREMA-D speech emotion recognition dataset size speakers utterances". Confirms **IEMOCAP 5,531 utterances / ~12h / 10 speakers; RAVDESS 24 actors / 1,440 utterances / 8 emotions; CREMA-D 91 actors / 7,442 clips / 6 emotions; MSP-Podcast naturalistic, ~235h in later releases**. ✔ (Sources: arxiv.org/pdf/2402.13018 EMO-SUPERB; github.com/usc-sail/trust-ser; medium audio-datasets overview.)
- **Conflict note:** the local PDF is an accepted manuscript, not the typeset IEEE Version of Record. No numeric conflicts were found between it and the venue record; section/figure numbering used here follows the manuscript. Where the manuscript's Table 4/Table 5 cells are misaligned in extraction, this dossier flags the affected numbers as ≈ approximate and uses externally-corroborated values instead.

### What the paper actually does

A landscape survey (no new experiments) that organises **deep representation learning for SER** along three axes: (a) **feature types** — hand-engineered (MFCC, LogMel, GeMAPS/eGeMAPS, IS09–IS13, LLDs) vs raw speech vs learned (§2.1, §5.1); (b) **DL model families** — DNN, CNN (ResNet/DenseNet), RNN (LSTM/GRU/BLSTM), CNN-RNN, CapsNet, attention, AE/DAE/sparse-AE/AAE, DBN/RBM, VAE, GAN, transformer (§2.3, Table 3); (c) **learning paradigms** — supervised, unsupervised, semi-supervised, transfer (domain-adaptive / multi-task / self-supervised), and DRL (§3, summarised in Table 5). It catalogues canonical corpora (Table 4), evaluation conventions (UA/UAR, CCC; §2.5), and five open challenges with future directions (§4, Table 6). Senior author Schuller anchors it to the Interspeech ComParE challenge tradition.

The empirically load-bearing findings (all from cited studies, not the authors' own runs):
- Supervised > semi-supervised > unsupervised in raw SER accuracy; unsupervised "not as good as supervised" (§3.2).
- **MTRL is the strongest positive lever:** +7.9% F1 (8-class MSP-Podcast), +5.3% UA (gender-aux), +5.5% accuracy (speaker/gender-aux IEMOCAP), +4.7–14% CCC (joint aro/val/dom), at "no major increase in computational power" (§3.4.2). ✔ (body text).
- IEMOCAP within-corpus tops out ~70% UA (Transformer/Wav2Vec features; Table 5). ≈ approximate (Table 5 extraction mangled).
- **Cross-corpus collapse:** 61.05% within → 46.60% cross-corpus accuracy (GAN study, §3.2). ✔ — the field's central failure mode.
- SSL framed as open frontier; transformer SSL with MLM pretext gives +3% on CMU-MOSEI (§3.4.3). ✔.

### Parts directly useful for Pebble

1. **Metric convention: UA/UAR (imbalance) + CCC (regression)** (§2.5). → fixes Pebble's emotion head to macro-recall/UAR and severity head to CCC/Pearson. **(D-C, D-D)**
2. **MTRL evidence base** (§3.4.2): auxiliary tasks lift the label-scarce main task at near-zero extra compute. → external justification for Pebble's shared-encoder multi-head MTL and for adding a high-resource auxiliary (arousal/valence or gender) to lift scarce child-emotion signal. **(D-B)**
3. **"Architecture/representation matters more than input feature; representation learning > feature engineering"** (§2.1, §5.1). → supports a strong-pretrained-backbone-first policy across modalities. **(D-A)**
4. **Cross-corpus generalisation gap** (§3.2, §4.3) + domain-adaptation toolbox (DANN/GRL, shared-hidden-layer AE, §3.4.1). → mandates OOD/cross-corpus evaluation as the primary SER result and domain adaptation as a first-class step. **(D-D, D-H)**
5. **Dataset roster + label schemes** (Table 4) → the citable benchmark set for choosing Pebble SER pretraining/eval corpora. **(D-H)**
6. **"Outer vs inner emotion" + lab-acted-corpus limitation** (§4.2) → the honest framing that lab-acted adult corpora bound, not predict, child-in-the-wild performance. **(D-H)**

### How each part helps Pebble succeed

- **Metrics (1) → reporting harness.** Add **UAR/macro-recall** as the emotion head's primary scalar (Pebble's bar is already 47.8% macro-recall — the survey is the citation that this is the *right* bar under imbalance) and **CCC + Pearson** as the severity head's primary scalar. Transfer risk: **low** — this is a measurement convention, fully portable; the only caveat is that Pebble's 12-label GoEmotions-mapped scheme has finer granularity than the 4–8-class SER norm, so per-class recall variance will be wider.
- **MTRL (2) → training recipe.** Keep the shared NeoBERT/audio encoder with multiple heads; consider a **high-resource auxiliary** (e.g. arousal/valence from a labelled SER corpus, or gender) trained jointly to regularise the scarce, silver-labelled child-emotion head. Transfer risk: **medium** — the survey's MTRL gains are on adult acted/podcast speech; whether a gender/arousal auxiliary helps *child* emotion is untested, but the mechanism (shared representation regularisation) is modality- and population-agnostic, so the downside is bounded.
- **Backbone (3) → encoder policy.** Choose a strong pretrained SSL audio encoder over a GeMAPS/MFCC + shallow-classifier pipeline; mirror Pebble's text-side NeoBERT-over-handcrafted choice. Transfer risk: **low** for the principle, **medium** for the specific encoder (SSL encoders are pretrained on adult read/podcast speech; child acoustic characteristics — higher F0, different formants — may need domain-adaptive continued pretraining, see #40).
- **Generalisation (4) → eval design.** Make the SER chapter's headline a **cross-corpus / OOD** number (train on one corpus, test on a held-out corpus and on a child slice), and budget for a domain-adaptation step. Transfer risk: **low** — the gap is universal; if anything it *under*-states Pebble's risk because the adult→child shift is larger than the corpus→corpus shifts the survey measured.
- **Datasets (5) → corpus selection.** Use IEMOCAP/MSP-Podcast/CREMA-D/RAVDESS as the established English SER set for pretraining/benchmarking; note none are child speech, so a child calibration slice is mandatory. Transfer risk: **high** for any direct number transfer (all adult acted/naturalistic) — these corpora calibrate the *method*, not the *deployment*.

### Child mental-health lens

- **No child speech anywhere.** Every corpus in Table 4 (and the body) is adult — actors, podcasters, lab participants. The closest is FAU-AIBO (children speaking to a robot dog), mentioned only in passing for cross-corpus domain adaptation. **Transfer validity to a child-facing product is unestablished by this survey** — it is the *method* map, not evidence for child SER.
- **Acoustic shift risk.** Children have higher fundamental frequency, different formant structure, less stable prosody, and developmental variation. An SSL encoder pretrained on adult speech (the survey's whole premise) will be **off-distribution** for child voices — exactly the §4.3 generalisation gap, amplified. Mitigation: domain-adaptive continued pretraining on child/younger-speaker audio before head fine-tuning, and a child calibration set with reported per-age-band performance.
- **"Outer vs inner emotion" is sharper for children** (§4.2). The survey's caution — raters label *outer* (expressed) emotion, which can differ greatly from *inner* (felt) emotion — is more acute for children, who mask, under-report, or express distress indirectly. A child SER head must be framed as detecting *expressed acoustic affect*, never *felt internal state*, and feed a human-in-the-loop pathway (consistent with FAIIR's role-boundary discipline, paper #01).
- **Privacy is non-negotiable** (§4.4). The survey itself flags that speech leaks identity, gender, ethnicity, emotional state, and enables spoofing. For a child-facing voice product this is a hard ethical/legal constraint: on-device/edge feature extraction, federated learning, no raw-audio retention, guardian consent — all named by the survey as the mitigation set, all mandatory for Pebble.
- **Acted-corpus emotions ≠ crisis affect.** The survey's corpora encode posed prototypical emotions (anger/happiness/sadness) in short clips. Child mental-health-relevant signals (flat affect, anxiety, withdrawal, dysregulation) are largely absent from these label schemes — another reason Table 4 calibrates method, not Pebble's actual targets.

### Limitations & open questions for Pebble

- **Vintage / SSL gap (contradiction vs Pebble's plan and vs newer papers).** The survey treats **transformers and SSL as future work** ("Transformers need to be explored in SER," §5.2; SSL "needs exploration," §3.4.3). Pebble's plan (and papers #24 MMER, #27 Morais, #40 wav2vec2-depression in this very repo) assume **SSL transformers are the SER default**. This is a direct contradiction born of vintage: the survey is the *map before the SSL revolution*. Pebble must cite it for the *gap statement* and the newer papers for the *resolution* — never as evidence on current SSL-SER performance.
- **Table 5 numbers are illustrative, not benchmarks.** Different splits, fold protocols, and features make the rows non-comparable; the PDF extraction further mangles Table 5's cell alignment. Pebble cannot quote a "SOTA UA" from this paper as a target bar — only the *pattern* (within ~60–70% UA, cross-corpus ~47%).
- **MTRL gains are adult-corpus and task-specific.** The +7.9% F1 / +5.3% UA figures are on MSP-Podcast/IEMOCAP with gender/secondary-emotion auxiliaries. Whether those specific auxiliaries help a 12-label child-emotion head is untested — Pebble should treat MTRL as a *mechanism* to validate empirically, not a guaranteed gain.
- **No calibration / no uncertainty discussion.** Like FAIIR (#01), the survey reports point metrics only — no reliability/ECE for any SER model. Pebble's Decision Engine consumes probabilities, so the audio head's calibration is an open requirement this literature does not address.
- **Cross-modality contradiction with the text plan.** The survey's central claim — "the choice of input feature is not as important as the model architecture" (§5.1) — sits in mild tension with Pebble's text-side investment in domain-adaptive MLM and label-scheme engineering (D-C/D-F), which presume input/representation design *does* matter. Reconciliation: in SER the claim is about *acoustic* feature engineering (MFCC vs LogMel vs raw), whereas Pebble's text-side decisions concern *label* design and *domain* adaptation, not input-feature handcrafting — so the survey supports "don't hand-craft inputs, do adapt the representation," which is exactly Pebble's MLM/transfer stance.
- **Open question — child SER corpus.** The survey makes plain no standardised child SER corpus exists in the canonical set. Whether Pebble must build/curate one (with the ethics/consent/privacy regime §4.4 demands) is the largest unresolved dependency for the voice chapter.
