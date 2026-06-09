# Paper 02 — VAD-Assisted Multitask Transformer for Emotion + Intensity on Suicide Notes

## 1. Bibliographic info

- **Title:** VAD-assisted multitask transformer framework for emotion recognition and intensity prediction on suicide notes
- **Authors:** Soumitra Ghosh, Asif Ekbal, Pushpak Bhattacharyya
- **Affiliations:** Department of CSE, IIT Patna (Ghosh, Ekbal); Department of CSE, IIT Bombay (Bhattacharyya)
- **Venue:** *Information Processing & Management* (Elsevier), Vol. 60, Issue 2, Article 103234
- **Year:** 2023 (online late 2022)
- **DOI:** [10.1016/j.ipm.2022.103234](https://doi.org/10.1016/j.ipm.2022.103234)
- **Status:** Paywalled at ScienceDirect / ACM. Author preprint not located on arXiv, ResearchGate, IIT Patna or IIT Bombay homepages as of this search.
- **Author contacts (for full-text request):** Asif Ekbal — asif@iitp.ac.in; Pushpak Bhattacharyya — pb@cse.iitb.ac.in; Soumitra Ghosh — soumitra.pcs16@iitp.ac.in / ORCID 0000-0001-9908-7551.

## 2. Problem motivation

Suicide notes are a small but uniquely informative window into the affective state preceding a suicide attempt. Forensic investigators, suicidology researchers and prevention-research teams routinely study them to (a) distinguish genuine from simulated notes, (b) profile the dominant emotional trajectories of decedents (hopelessness, guilt, blame, love, instructions), and (c) feed evidence into theory-driven models of suicide risk such as the Interpersonal Theory of Suicide (Joiner). Standard polarity-only sentiment analysis collapses too much of this signal; clinicians need finer-grained categorical emotions and a sense of *how strongly* each one is expressed, because intensity is what differentiates passing ideation from acute crisis-level affect. Ghosh et al.'s research line — CEASE (LREC 2020), the cascaded multi-task framework in *Scientific Reports* 2022, the IJCAI-ECAI 2022 burdensomeness/belongingness paper, and this IPM 2023 paper — pursues exactly that finer-grained signal on real suicide notes rather than proxies like Reddit posts.

## 3. Position in the literature

The paper sits at the intersection of three threads:

1. **The authors' own CEASE line.** CEASE v1 (Ghosh, Ekbal, Bhattacharyya, [LREC 2020](https://aclanthology.org/2020.lrec-1.201/)) introduced a 2,393-sentence / ~205-note corpus annotated for 15 emotions. The same group then built increasingly elaborate multi-task systems on top: a CNN/GRU/LSTM ensemble (LREC), a cascaded depression+sentiment+emotion network ([Cognitive Computation 2021](https://link.springer.com/article/10.1007/s12559-021-09828-7)), the temporal+sentiment+emotion SPANMLC framework ([Scientific Reports 2022, PMC8923342](https://pmc.ncbi.nlm.nih.gov/articles/PMC8923342/)), and the IJCAI-ECAI 2022 PB/TB detector. The IPM paper is the *intensity-prediction* installment of the same program.
2. **VAD-based emotion modeling.** Mohammad's [NRC-VAD lexicon (ACL 2018)](https://aclanthology.org/P18-1017/) provides real-valued valence, arousal, and dominance scores for ~20,000 English words via Best-Worst Scaling, and Buechel & Hahn's EmoBank work showed that VAD continuous dimensions can be regressed jointly with categorical labels. The Ghosh paper plugs this lexicon into a transformer as an auxiliary signal — a known good but under-applied trick in the clinical-text setting.
3. **Joint categorical + continuous emotion multitask learning.** Akhtar, Ghosal et al.'s "All-in-One" ([AAAI 2019](https://www.semanticscholar.org/paper/d62bf3bffd175badcda3aa4d1d3248855eb793c2)) and SemEval-2018 Task 1 (EI-reg) established that emotion-category and emotion-intensity heads share useful gradients. The IPM paper transports this idea to suicide notes — a domain where joint training is harder because of dataset size and label sparsity.

## 4. CEASE-v2.0 dataset

CEASE-v2.0 is the corpus the paper uses and (per multiple secondary sources) extends. Confirmed facts:

- **Size:** **4,932 sentences** drawn from **325 real-life suicide notes** in English — i.e. ~2,539 sentences and ~120 notes more than CEASE v1's 2,393 sentences / 205 notes.
- **Granularity:** sentence-level multi-label annotation.
- **Taxonomy (15 fine-grained classes, from LREC 2020):** *forgiveness, happiness/peacefulness, love, pride, hopefulness, thankfulness, blame, anger, fear, abuse, sorrow, hopelessness, guilt, information, instructions*. The taxonomy mixes affective states with two pragmatic categories (information, instructions) that are extremely common in actual suicide notes ("the keys are in the drawer", "please call my sister").
- **Annotation protocol (LREC v1, presumed to carry over):** three annotators, with Krippendorff's α ≈ 0.61 (moderate-to-substantial for a 15-class affective task) and a multi-label distribution dominated by single-label sentences (~76% one label, ~22% two, ~2% three).

**Honest gap:** the precise IAA, exact label distribution, and the source breakdown of the 120 *new* notes added in v2.0 are not visible in any public snippet — those tables live in the paywalled paper and in the SPANMLC paper, the latter of which does confirm "CEASE-v2.0… 4,932 sentences… 2,539 additional instances."

The big distinction to flag in a Pebble writeup: **CEASE v1 = LREC 2020, 205 notes / 2,393 sentences; CEASE-v2.0 = IPM 2023 + Scientific Reports 2022, 325 notes / 4,932 sentences with added intensity labels.** It is easy to cite the wrong number from the wrong paper.

## 5. The new intensity annotation (paper's contribution)

The paper's headline contribution beyond CEASE-v2.0's categorical labels is that **every sentence is now additionally annotated with emotion-intensity labels**. From the abstract and ScienceDirect snippets:

- *Confirmed:* "all sentences labeled with emotion intensity annotations" (i.e. complete coverage of the 4,932 sentences).
- *Confirmed:* intensity is treated as the **auxiliary task**, emotion category as the **primary task**.
- *Unknown from public sources:* whether intensity is continuous [0,1] (the SemEval EI-reg convention, plausible given VAD's continuous nature), ordinal {low, medium, high}, or per-emotion-channel; whether one global intensity per sentence or one per active emotion label; the IAA achieved on intensity annotation; and the annotation guidelines.

In a Pebble paper this should be flagged as "label format unverified pending full PDF."

## 6. Method (best-effort reconstruction)

**Confirmed from abstract:**

- End-to-end **VAD-assisted, transformer-based multi-task network**.
- **Primary task:** emotion classification (15-way, multi-label).
- **Auxiliary task:** emotion-intensity prediction.
- The three VAD determinants (Valence, Arousal, Dominance) are injected as auxiliary signals to "help determine a person's exact emotion(s) and its intensity."

**Plausible from author's sibling architectures (triangulation, *not* confirmed for IPM):**

The IJCAI-ECAI 2022 paper by the same trio (PB/TB detection on the same CEASE-v2.0 + CoMCEASE-v2.0) is a Temporal Encoder Multi-task Framework (TEMF) that uses BERT [CLS] embeddings combined with a sentence-Transformer pathway, a Bahdanau additive attention head per task, and a differential loss L_Diff that encourages the task-specific representations to disagree productively. The 2022 *Scientific Reports* SPANMLC paper, by contrast, used Bi-GRU 256-d on 300-d GloVe with shared/private attention. The IPM 2023 paper, given that it announces a *transformer* framework and shares all three authors, almost certainly follows the BERT-encoder + per-task attention pattern of the IJCAI sibling rather than the GloVe/Bi-GRU SPANMLC pattern.

A reasonable best-effort sketch (clearly labeled as reconstruction):

1. Tokenize sentence; pass through pretrained BERT (likely `bert-base-uncased`).
2. Take the [CLS] embedding (or pooled mean of token embeddings) as the shared sentence representation.
3. Look up each token in NRC-VAD; aggregate per-sentence V, A, D scores (mean, max, weighted by attention) as an auxiliary 3-d vector.
4. Concatenate or gate the BERT representation with the VAD vector.
5. Two task heads: (a) multi-label sigmoid classifier over 15 emotions, (b) regression head for intensity (or one regression head per emotion channel).
6. Train jointly with a weighted sum of losses, possibly with a differential / disagreement regularizer L_Diff as in the IJCAI sibling.

**Honest gap:** the exact fusion mechanism (early concat? gated cross-attention? a VAD-conditioned attention layer?), whether VAD is per-token or per-sentence, and whether a separate VAD prediction head exists, all remain paywalled.

## 7. Loss formulation (best-effort)

The abstract does not give the loss. A defensible reconstruction:

$$
\mathcal{L} = \alpha \cdot \mathrm{BCE}(\hat{y}_{\text{emo}}, y_{\text{emo}}) + \beta \cdot \mathrm{MSE}(\hat{i}, i) \;[+\; \gamma \cdot \mathcal{L}_{\text{Diff}}]
$$

Triangulation supports static empirical weighting:

- **SPANMLC (Scientific Reports 2022):** `L(Ω) = 0.3·L1 + 0.3·L2 + 1.0·L3`, with the auxiliary weak-supervision tasks down-weighted relative to the primary emotion task.
- **IJCAI-ECAI 2022:** introduces a differential loss L_Diff term over task-specific representations.

It is therefore reasonable to expect IPM 2023 to set the primary (emotion BCE) weight near 1.0 and the auxiliary (intensity MSE) weight to a small empirical fraction (likely in the 0.1–0.5 range), possibly with a VAD-alignment or differential regularizer. The exact α, β, γ are paywalled.

## 8. Training setup

The abstract is silent on hyperparameters. Sibling-paper defaults from the same authors on the same dataset:

- **IJCAI-ECAI 2022 sibling (on CEASE-v2.0):** Adam, LR 2e-5, batch size 4, 6 epochs, 10-fold cross-validation, single RTX 2080 Ti.
- **SPANMLC / Scientific Reports 2022 (on CEASE-v2.0):** Adam, batch 32, 20 epochs, dropout 0.25, ReLU + sigmoid heads, 10-fold stratified CV, GTX 1080 Ti.

For the IPM paper, given it is a BERT-based transformer trained on the same small corpus, the LR 2e-5 / small batch / 10-fold CV configuration is the more probable baseline. The paper likely uses Mean Recall (MR) and samples-F1 for emotion and MAE / Pearson for intensity (the standard EI-reg metrics), but only MR is confirmed publicly.

## 9. Results

Confirmed from abstract / search snippets:

- **Best emotion MR = 65.25%** on CEASE-v2.0.
- The multi-task system outperforms its single-task counterparts (i.e. emotion-only and intensity-only baselines trained on the same backbone).
- The paper claims a **+8.78% improvement over prior state of the art** on the emotion task — the prior SOTA being almost certainly the CMSEKI cascaded multi-task framework from the same group's earlier work, which SPANMLC had improved on by +3.78% to reach 60.25% MR. A jump from ~60.25% (SPANMLC) to 65.25% (this paper) is consistent with the claimed +8.78% over CMSEKI's older ~56–57% range.

Not visible publicly: per-class F1, intensity MAE / Pearson, ablations isolating the VAD contribution, single-task baselines' numbers, statistical significance, error analysis. These all require the full PDF.

## 10. Authors' stated limitations

The full limitations section is paywalled, but the typical and likely limitations of this work — based on the dataset and method — are:

- **Small dataset:** 4,932 sentences from 325 notes is tiny by modern NLP standards; results are CV-mean numbers with non-trivial variance.
- **English-only**, US-centric note sources (CEASE v1 used Lounsbury and similar publicly archived collections).
- **VAD lexicon dependence:** NRC-VAD covers ~20k single English words; OOV handling and the inability to capture sentence-level compositional affect are inherent limits.
- **No causal / risk-factor head:** the paper detects what is *felt*, not what is *driving* the risk (the IJCAI sibling and the CARES paper attack those).
- **Class imbalance:** "instructions" and "information" dominate; rare emotions like *pride* and *forgiveness* almost certainly suffer.
- **Ethical scope:** all conclusions are descriptive; the system is not validated as a clinical tool.

## 11. Relevance to Pebble

This is the closest direct architectural analog to Pebble's emotion head in the surveyed literature, with both convergent and divergent design choices:

- **Convergent — joint categorical + continuous heads.** Ghosh et al. combine multi-label categorical emotion with a continuous intensity regressor in a single transformer; Pebble combines GoEmotions-style categorical emotion with a continuous EI-reg severity head. This is the *precedent* Pebble cites for "category + intensity together in one transformer on a small mental-health dataset."
- **Convergent — auxiliary affective signal.** Ghosh injects the NRC-VAD lexicon as a hand-curated auxiliary signal; Pebble warm-starts from GoEmotions as a learned auxiliary signal. Both reflect the same intuition that the primary emotion classifier benefits from a richer affective scaffold than the labels alone.
- **Divergent — no safety / crisis head.** Ghosh has emotion + intensity only. Pebble adds a crisis/safety head, making it a true mental-health *support* system rather than a forensic *characterization* system.
- **Divergent — loss balancing.** Ghosh (and the SPANMLC sibling) uses **static, empirically chosen** loss weights (e.g. 0.3/0.3/1.0). Pebble is considering principled dynamic schemes (Kendall task-uncertainty, GradNorm). This is a clean point of methodological advance Pebble can claim.
- **Domain match — partial.** Suicide notes are a single-sided, end-of-life monologue; emotional-support conversations are multi-turn dialogue. The *head-structure* analog is strong; the *domain* analog is weak. Honest framing matters.

## 12. Recommended citation use

In a Pebble paper, cite Ghosh, Ekbal & Bhattacharyya (IPM 2023) to support:

1. **Precedent for joint categorical + continuous emotion heads on a small, sensitive mental-health corpus** using a transformer backbone.
2. **Precedent for empirically-weighted static multi-task loss** in this exact domain — the foil against which Pebble's dynamic weighting is positioned.
3. **Use of an affective auxiliary signal** (their NRC-VAD lexicon ↔ Pebble's GoEmotions warm-start) to compensate for limited in-domain data.
4. **Benchmark anchoring** — MR=65.25% on CEASE-v2.0 is the most recent reported number on this corpus and is the right thing to point at when arguing that small-corpus mental-health emotion modelling is a live, unsolved research area.

Do **not** cite it as a precedent for safety/crisis detection, multi-turn dialogue modelling, or dynamic loss weighting — none of those are claimed.

## 13. Honest paywall note

The following details could **not** be verified from public sources and require the full PDF:

- Exact intensity-label format (continuous vs ordinal; one global vs per-emotion).
- Inter-annotator agreement on the intensity annotation.
- The precise architecture diagram, VAD-fusion mechanism, and whether a differential / VAD-prediction auxiliary loss is used.
- Loss-weight values (α, β, possibly γ).
- Training hyperparameters (LR, batch size, epochs, optimizer, CV folds, hardware) — sibling-paper values quoted above are *triangulation*, not the IPM paper's actual numbers.
- Full results table — per-class F1, intensity MAE/Pearson, ablation rows isolating VAD vs no-VAD and multi- vs single-task.
- Baseline list and significance tests.

Recommended next step: email **soumitra.pcs16@iitp.ac.in** (first author, IIT Patna) or **asif@iitp.ac.in** (corresponding) with a polite reprint request — Indian NLP groups routinely respond within a few days. The paper's accompanying CEASE-v2.0 release, if any, should be requested in the same email.

## Sources

- [VAD-assisted multitask transformer framework — ScienceDirect listing](https://www.sciencedirect.com/science/article/abs/pii/S0306457322003351)
- [VAD-assisted multitask transformer framework — ACM listing](https://dl.acm.org/doi/10.1016/j.ipm.2022.103234)
- [CEASE corpus (LREC 2020)](https://aclanthology.org/2020.lrec-1.201/)
- [Deep cascaded multitask framework / SPANMLC (Scientific Reports 2022, PMC8923342)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8923342/)
- [Am I No Good? IJCAI-ECAI 2022 preprint](https://arxiv.org/abs/2206.06141)
- [NRC-VAD lexicon, Mohammad ACL 2018](https://aclanthology.org/P18-1017/)
- [NRC-VAD project page](https://saifmohammad.com/WebPages/nrc-vad.html)
- [Results on CEASE-v2.0 dataset figure (ResearchGate)](https://www.researchgate.net/figure/Results-on-the-CEASE-v20-dataset-Here-ST-and-MT-denote-single-task-and-multi-task_tbl1_360257543)
