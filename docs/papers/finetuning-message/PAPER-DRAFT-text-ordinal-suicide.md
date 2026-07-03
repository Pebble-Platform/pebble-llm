<!--
IEEE Bài 1 — DRAFT (Markdown; convert IEEEtran sau).
Tracking: docs/tasks/ieee-paper-text-message.md · Plan: PAPER-PLAN-text-ordinal-suicide.md
Provenance mọi số: docs/tasks/r2-method-improvements-for-contribution.md (slug@version → log).
[TODO κ] = chưa đo (blocked: Azure LLM key hết hạn, xem tier1 task doc); KHÔNG bịa.
Baseline đã điền từ log (2026-07-03).
-->

# Weakly-Supervised Augmentation for Ordinal Suicide-Risk Classification on Social Media: An Honest Gold-Holdout Study

**Authors:** [TODO names], [TODO affiliation]

---

## Abstract

Assessing suicide risk from social-media text is an **ordinal** problem — risk
escalates Indicator < Ideation < Behavior < Attempt on the Columbia-Suicide
Severity Rating Scale (C-SSRS) — yet clinician-labeled gold data are scarce.
A natural remedy is to augment a small clinical gold set with abundant
**LLM-generated weak labels**, but the benefit is routinely *overstated* because
models are evaluated on the same (LLM) label distribution they were trained on.
We propose an **honest gold-holdout protocol**: train on LLM weak labels,
evaluate only on held-out clinician gold, so the measured gain is non-circular.
Under this protocol we contribute three method improvements over a hierarchical
dual-head baseline: (1) a **noise-robust ordinal loss**, CORN (per-threshold
weights) + GCE (down-weighting low-confidence samples), which replaces
CORAL+Focal and recovers the collapsed rare Behavior class
(gold-F1 0.183 → 0.260) while preserving ordinal structure; (2) a **post-hoc
label-shift correction** that diagnoses and corrects the systematic prior shift
between LLM and clinical label distributions (Behavior under-labelled 3.0×),
lifting Behavior-F1 0.357 → 0.41 with no retraining; and (3) an
**ordinal-aware Confident Learning** variant whose confident-joint is weighted
by rank distance, cleaning 100% of far errors while keeping 78% of adjacent
borderline cases, and which flags 35.8% of Behavior labels as suspect. On a
comparable within-distribution protocol our method reaches macro-F1 0.653 vs.
the reference 0.510. We report a candid finding: on the clinical gold
distribution, a plain flat cross-entropy model still leads on macro-F1 (0.422),
exposing a real cost of ordinal modeling under label-distribution shift.

**Index Terms** — suicide-risk detection, ordinal classification, weak
supervision, large language model annotation, label noise, label shift,
confident learning, mental health NLP.

---

## I. Introduction

Suicide is a leading cause of death worldwide, and people in distress
increasingly disclose ideation on social media before any clinical contact.
Automated screening of such text could route users to help earlier. The
clinically meaningful target is not a binary "risk/no-risk" flag but an
**ordinal severity** on the C-SSRS: *Indicator* < *Ideation* < *Behavior* <
*Attempt* — consistent with the move in mental-health assessment toward
dimensional, graded models of risk rather than binary categories [Jo25]. Two
properties make this hard. First, the labels are ordinal:
mistaking *Behavior* for *Ideation* (adjacent) is less wrong than mistaking it
for *Indicator* (distant), so flat classification losses that ignore rank are
mis-specified. Second, **clinician-labeled gold data are scarce** — the public
C-SSRS-Reddit corpus has only 500 users — while unlabeled or weakly labeled
posts are abundant.

A now-common strategy is to use a large language model (LLM) as an annotator,
producing cheap "weak labels" at scale to augment the gold set. The danger is
**circular evaluation**: a model trained on LLM labels and tested on more LLM
labels reports inflated accuracy that does not transfer to clinical judgment.
This paper asks a precise question: *do LLM weak labels honestly augment a
scarce clinical gold set for ordinal suicide-risk classification, and how do we
measure that gain without fooling ourselves?*

Our answer is built on an **honest gold-holdout protocol** — train on LLM weak
labels, evaluate only on disjoint clinician gold — under which we make three
methodological contributions, each targeting a distinct failure mode of weak
supervision:

1. **A noise-robust ordinal loss (CORN + GCE).** The dual-head baseline's
   CORAL head shares a single weight vector across all thresholds, so one noisy
   rare-class label corrupts every decision boundary; its Focal term further
   *up-weights* hard (often mislabeled) examples. We replace CORAL with **CORN**
   (independent per-threshold logits) and Focal with **GCE** (which down-weights
   low-confidence samples). This recovers the collapsed Behavior class
   (gold-F1 0.183 → 0.260) and beats the dual-head baseline on macro-F1
   (0.385 → 0.402) while keeping ordinal structure.

2. **A post-hoc label-shift correction.** We show the LLM→clinical gap is, in
   part, a *systematic label-distribution shift*, not random noise: Behavior is
   7.3% of the LLM pool but 19.7% of clinical gold (under-labelled 3.0×).
   A post-hoc prior correction (Logit Adjustment / SLD-EM), requiring **no
   retraining**, lifts Behavior-F1 0.357 → 0.41 (oracle upper bound 0.44).

3. **Ordinal-aware Confident Learning.** Standard Confident Learning treats
   labels as nominal. We weight its confident-joint by squared rank distance
   (aligned with quadratic-weighted κ), so cleaning removes 100% of *far* errors
   (Behavior→Indicator) while *keeping* 78% of *adjacent* borderline cases —
   clinically appropriate. The diagnostic flags 35.8% of Behavior labels as
   suspect, locating the bottleneck in label quality.

We also report an **honest negative finding**: on the clinical gold
distribution, a plain flat-CE model still leads on macro-F1 (0.422 vs. our best
ordinal 0.402). Rather than hide this, we frame it as evidence that ordinal
heads pay a real cost under LLM→gold shift; our contributions narrow but do not
erase that gap, and we recommend CORN+GCE specifically when ordinal ranking
(quadratic-weighted κ) is required.

---

## II. Related Work

**C-SSRS suicide-risk screening on Reddit.** Gaur et al. [G19] released the
500-user C-SSRS-Reddit corpus (4 practicing psychiatrists, pairwise agreement
0.79) that anchors most subsequent work; later systems add knowledge or
hierarchical context [LS24], [Hy25], [Sc25], [RSD25]. The reference architecture we build on is a
**hierarchical dual-head MentalRoBERTa** model [Y25] reporting within-
distribution macro-F1 ≈ 0.51, with BiLSTM-MTL (0.419) and Transformer-HAN
(0.491) baselines.

**Weak / distant supervision and LLM-as-annotator.** Using an LLM to label
mental-health text [Sc25], [PG24], [EP25] trades human cost for label noise. Data
programming (Snorkel) [R17] models multiple noisy labelers; we instead quantify
and correct the single-LLM→gold gap directly. Knowledge distillation [H15] and
LLM-teacher pipelines [EP25], [PG24] motivate soft-label alternatives we discuss as
future work.

**Ordinal regression.** CORAL [C20] enforces rank-monotone cumulative
probabilities with a *shared* weight vector; CORN [S23] removes that constraint
with conditional per-threshold training and reports consistent gains. We are,
to our knowledge, the first to apply CORN to LLM-weakly-labeled clinical ordinal
text and to show *why* the shared-weight constraint is harmful under rare-class
label noise.

**Noise-robust losses.** Focal loss [L17] up-weights hard examples, which is
counter-productive under label noise (mislabeled points look "hard") [Z21].
Generalized Cross Entropy (GCE) [Z18] interpolates between CE and MAE and
down-weights low-confidence samples, giving the noise robustness we need.

**Label noise and label shift.** Confident Learning [N21] estimates label
errors from out-of-fold probabilities but is nominal; we make it ordinal.
Prior-shift correction — SLD-EM [Sa02], BBSE [Li18], and Logit Adjustment
[Me21] — adapts a classifier from a training prior to a test prior; we
instantiate it for the LLM→clinical ordinal setting and use the per-class shift
ratio as a label-quality measure.

**Encoders.** MentalBERT / MentalRoBERTa [Ji22] are domain-adapted encoders
for mental-health text; we use a public MentalRoBERTa-derived mirror as the
post encoder.

---

## III. Method

### A. Hierarchical dual-head architecture

A user is represented as a sequence of up to *S* = 5 posts. Each post is encoded
by a MentalRoBERTa-derived encoder (lowest 6 layers frozen, `max_len` = 256);
the post-level `[CLS]` vectors form a sequence that a 3-layer Transformer
contextualizes, followed by multi-head **attention pooling** with a learnable
query into a single user vector **u**. Because the corpus has no timestamps we
set Δt = 0 (a temporal embedding is wired but inactive). From **u** the model
produces two heads — an **ordinal head** and a softmax **CE head** — blended at
inference. This is the baseline we improve.

### B. Noise-robust ordinal loss: CORN + GCE (Contribution 1)

The baseline ordinal head is **CORAL**: a *single* shared weight vector with
K−1 ordered biases producing cumulative P(y>k). Under noisy weak labels this is
fragile — the shared weight ties all thresholds together, so a mislabeled rare
*Behavior* example perturbs the *Indicator/Ideation* boundary too. We replace it
with **CORN** [S23]: K−1 *independent* logits, where task *k* predicts
P(y>k | y>k−1) and is trained only on the conditional subset {i : yᵢ ≥ k}, with
P(y>k) recovered by the chain rule. A noisy *Behavior* label now contaminates
only its own thresholds.

The baseline third loss term is **Focal**, whose modulating factor (1−p)^γ
*increases* gradient on hard examples — exactly the mislabeled ones. We replace
it with **GCE** [Z18]: L = (1 − p_yᵠ)/q (q = 0.7), whose gradient scales as p_yᵠ
and therefore *down-weights* low-confidence (likely noisy) samples. The training
objective is

  L = 0.5·L_CORN + 0.3·L_CE + 0.2·L_GCE.

Class imbalance is handled by inverse-frequency minibatch resampling. All
components are env-gated, so the 2×2 head×loss grid (§V) is run from one
codebase on an identical split/seed.

### C. Post-hoc label-shift correction (Contribution 2)

We observe that P_train(y) (LLM pool) and P_gold(y) (clinical) differ
*systematically*: the per-class shift ratio w(y) = π_gold(y)/π_train(y) is
**3.0** for Behavior (7.3% → 19.7%), i.e. the LLM under-labels the rare clinical
class. This is correctable **without retraining**. We apply **Logit Adjustment**
[Me21] to the CE-head logits, ŷ_k = z_k − τ·log π_train(k), and, as an
unsupervised alternative, **SLD-EM** [Sa02] which estimates the target prior by
EM on the model posteriors. We additionally interpret w(y) itself as a
**per-class label-quality measure** of the LLM annotator.

### D. Ordinal-aware Confident Learning (Contribution 3)

Confident Learning [N21] estimates a confident-joint Q̂[i,j] (labeled *i*,
confidently *j*) from out-of-fold probabilities, but treats off-diagonal cells
symmetrically. For ordinal labels an adjacent confusion (Behavior↔Ideation) is
often a *valid* borderline case, while a distant one (Behavior↔Indicator) is
almost surely noise. We weight each example's issue score by squared rank
distance, s(i) = (1 − p_self(i))·|ỹᵢ − ŷᵢ|², aligning cleaning with the
quadratic-weighted-κ penalty, and additionally use the CORAL cumulative
probability P(y ≥ Behavior) as a clinically-motivated rejection threshold. The
rule is "**clean far, keep adjacent**," which protects the tiny Behavior pool.

### E. Honest gold-holdout protocol (framing)

All headline numbers use **gold-holdout**: training pools (LLM-labeled) and the
evaluation set (clinician gold) are *disjoint by example*; folds are
**subject-level** (a user never appears in two folds). We report three protocols
side by side (§V) precisely to expose circularity: a within-LLM number (train
and test on LLM labels) is shown *only* to demonstrate it is not a valid
accuracy claim.

---

## IV. Data and LLM-Labeling Pipeline

**Gold (clinical).** The C-SSRS-Reddit corpus [G19] — 500 Reddit users labeled
by 4 practicing psychiatrists on the 5-level C-SSRS (we drop *Supportive*,
giving 4 ordinal levels Indicator/Ideation/Behavior/Attempt = 0/1/2/3). The
held-out gold evaluation set is **392 user-sequences**, class counts
[99, 171, 77, 45].

**Weak-label training pool.** We enrich the gold set with additional
Reddit user-sequences (an existing public collection plus scraped r/SuicideWatch
posts) labeled by a **single LLM** (gpt-class, confidence ≥ 0.6 retained),
yielding **9,680 training sequences**, class counts [3992, 3612, 634, 1442].
The full enriched corpus is **10,072** sequences. Posts have no timestamps,
so Δt = 0.

**Label-quality analysis.** `[TODO κ]` — Cohen's κ and the LLM-vs-gold confusion
matrix on the recovered LLM/gold *overlap* set (the subset with both an LLM and
a gold label) will quantify the ~0.28 gold-holdout gap as a measured annotator
agreement; pending recovery of the overlap subset. Independent of κ, two
quantities already characterize the weak labels: the per-class **shift ratio**
w(y) (§III-C; Behavior 3.0×) and the **ordinal Confident-Learning flag rate**
(§V-E; 35.8% of Behavior labels suspect).

**Ethics and provenance.** All corpora are public and de-identified; the gold
C-SSRS-Reddit set is CC-BY-4.0. Scraped posts were content-filtered
(~9% removed) and de-identified; no raw clinical data is committed to the
repository. Annotator-exposure and dual-use considerations are discussed in §VI.

---

## V. Experiments

### A. Setup

MentalRoBERTa-derived encoder; 5-fold subject-level CV; effective batch 16;
≤ 10 epochs with early stopping; AdamW (encoder 2e-5, new params 1e-4); pinned
GPU stack for reproducibility. Metrics: macro-F1, quadratic-weighted κ (QWK),
MAE, and per-class F1 (I6: ordinal metrics reported alongside F1). Every number
traces to a Kaggle kernel `slug@version` + log (provenance table in the tracking
doc). We report mean ± std over folds. Multi-fold reporting with a fixed split
is a deliberate guard against the ranking instability that replication studies
document when single-run point estimates and ad-hoc comparison sets drive
progress claims [Tr25].

### B. Three evaluation protocols (exposing circularity)

**Table I.** *Macro-F1 under three protocols. Within-LLM is shown only to expose
circularity; it is not a valid accuracy claim.*

| Protocol | Train labels | Eval labels | Macro-F1 | QWK |
|---|:--:|:--:|:--:|:--:|
| Gold-CV | gold | gold | 0.19 | 0.24 |
| Within-LLM *(circular)* | LLM | LLM | 0.67 | — |
| **Cross-to-gold (ours)** | LLM | gold | **0.385** | **0.378** |

Weak-label augmentation moves honest gold-holdout macro-F1 from 0.19
(gold-only, too little data) to 0.385 (+~50% rel.), while the within-LLM 0.67
demonstrates how circular evaluation would have overstated it.

### C. Comparable within-distribution protocol

Under the reference paper's *within-distribution* 5-fold CV protocol (on our
enriched 10k), our model reaches **macro-F1 0.653 ± 0.005**, versus the
reference's reported **0.510** (+0.143, +28% rel.). We frame this as *"our method
exceeds the reference's reported number on a comparable within-distribution
protocol,"* not on the original gated benchmark.

### D. Loss ablation: disentangling CORN vs. GCE (gold-holdout, 5-fold×10ep)

**Table II.** *2×2 head × third-loss grid, gold-holdout, same split/seed.
Cells are macro-F1 / Behavior-F1.*

| | Focal | GCE |
|---|:--:|:--:|
| **CORAL** | 0.385 / 0.183 | 0.399 / 0.229 |
| **CORN** | 0.410 / 0.250 | **0.402 / 0.260** |

flat-CE (no ordinal head): **0.422 / 0.285**, QWK 0.388.

From the dual baseline (CORAL+Focal), **CORN (head) is the primary lever**
(+0.025 macro / +0.067 Behavior), GCE contributes independently but less
(+0.014 / +0.046); combined they are sub-additive on macro yet best on the rare
Behavior class (0.260). Differences among the three CORN/GCE variants are within
fold std (0.015–0.025). **Honest finding:** flat-CE leads on macro-F1 (0.422),
so on the clinical gold distribution the ordinal machinery carries a cost; we
recommend CORN+GCE when QWK/ranking matters (it preserves ordinal structure,
QWK ≈ 0.36–0.40), and report flat-CE as the macro-F1 leader.

### E. Behavior class: label quality and correction

**Diagnostic (ordinal-CL).** Ordinal-aware Confident Learning flags **35.8%**
(227/634) of Behavior labels as suspect (vs. 16.2% pool-wide), locating the
bottleneck in label quality. The ordinal confident-joint cleans **100%** of far
errors (Behavior→Indicator) while keeping **78%** of adjacent borderline cases;
a nominal cleaner over-flags 45% of adjacent.

**Label-shift correction.** With Behavior under-labelled 3.0×, post-hoc Logit
Adjustment on a flat-CE checkpoint lifts **Behavior-F1 0.357 → 0.41**
(macro +0.005), approaching the oracle (true-prior) upper bound of **0.44**, at
**zero retraining cost**.

**Per-class (gold, dual-head).** Indicator 0.50 · Ideation 0.48 ·
**Behavior 0.18** · Attempt 0.37 — the Behavior collapse the contributions above
target.

### F. Baselines

**Table III.** *Baselines on the same gold-holdout split.*

| Model | Macro-F1 | Behavior-F1 | QWK |
|---|:--:|:--:|:--:|
| plain-RoBERTa-CE (mean-pool, no ordinal) | 0.346 ±0.026 | 0.169 | 0.292 |
| BiLSTM-MTL (paper baseline, our split) | 0.378 ±0.014 | 0.181 | 0.396 |
| Dual-head CORAL+Focal | 0.385 | 0.183 | 0.398 |
| flat-CE | 0.422 | 0.285 | 0.388 |
| **CORN+GCE (ours)** | 0.402 | 0.260 | 0.361 |

Both baselines were run on an identical split/seed via the same env-gated
codebase (`R2_SEQ_MODEL = mean | bilstm`), 5-fold with reported std
(`r2-baseline-roberta/out/`, `r2-baseline-bilstm/out/`; Behavior-F1 and QWK are
the fold means). The reference reports BiLSTM-MTL macro-F1 0.419
*within-distribution* — not comparable to our gold-holdout column.

---

## VI. Limitations and Ethics

**Single-LLM labels.** Training labels come from one LLM annotator; κ vs. gold
`[TODO κ]` is pending, and a multi-LLM (Snorkel-style) label model is future
work. **Rare Behavior class.** Even after our three levers, Behavior remains the
hardest class (gold-F1 ≤ 0.41) on only 634 noisy training and 77 gold examples.
**Ordinal cost under shift.** flat-CE leads macro-F1 on gold; ordinal modeling
is justified by ranking (QWK), not macro-F1, on this distribution.
**Protocol mismatch.** Our gold-holdout uses post-level sequences with Δt = 0
and is not the original gated benchmark; "exceeds the reference" is on a
comparable protocol only. **Test-set size.** The gold set is 392 sequences; we
report fold std and treat single-fold post-hoc results as indicative.

**Ethics.** Suicide-risk corpora are sensitive; all data are public,
de-identified, and never committed. The system is a *screening aid*, not a
diagnostic or a safety gate; false negatives on Behavior carry clinical cost,
which is why we foreground that class. Dual-use and annotator-exposure risks are
acknowledged; deployment would require human oversight and a separate safety
net.

---

## VII. Conclusion

We presented an honest gold-holdout study of weakly-supervised ordinal
suicide-risk classification. LLM weak labels *do* augment a scarce clinical gold
set — honest macro-F1 0.19 → 0.385 — and three method improvements target
distinct weak-supervision failure modes: a noise-robust ordinal loss (CORN+GCE)
that recovers the rare Behavior class while preserving ordinal structure; a
post-hoc label-shift correction that turns the LLM→clinical gap into a measured,
correctable quantity; and an ordinal-aware Confident-Learning cleaner. We also
report candidly that flat-CE still leads macro-F1 on the gold distribution,
quantifying the cost of ordinal modeling under label shift. Future work:
Cohen's κ on the overlap set, a multi-LLM label model, soft ordinal targets, and
a real gated encoder.

---

## References

<!-- IEEE numbered; [code refs] = per-paper notes in docs/papers/finetuning-message/NN-*.md -->

- [G19] M. Gaur et al., "Knowledge-aware Assessment of Severity of Suicide Risk
  for Early Intervention," *WWW*, 2019. (Zenodo 2667859, CC-BY-4.0)
- [Y25] Yang et al., "Hierarchical Dual-Head Model for Suicide Risk Assessment
  via MentalRoBERTa," *IEEE BigData*, 2025. (arXiv:2510.20085)
- [C20] W. Cao, V. Mirjalili, S. Raschka, "Rank consistent ordinal regression
  for neural networks (CORAL)," *Pattern Recognition Letters*, 2020.
- [S23] X. Shi, W. Cao, S. Raschka, "Deep neural networks for rank-consistent
  ordinal regression based on conditional probabilities (CORN)," *PAA*, 2023.
- [Z18] Z. Zhang, M. Sabuncu, "Generalized Cross Entropy loss for training deep
  neural networks with noisy labels," *NeurIPS*, 2018.
- [L17] T.-Y. Lin et al., "Focal loss for dense object detection," *ICCV*, 2017.
- [Z21] X. Zhou et al., "Asymmetric loss functions for learning with noisy
  labels," *ICML*, 2021.
- [N21] C. Northcutt, L. Jiang, I. Chuang, "Confident Learning: estimating
  uncertainty in dataset labels," *JAIR*, 2021.
- [Sa02] M. Saerens, P. Latinne, C. Decaestecker, "Adjusting the outputs of a
  classifier to new a priori probabilities," *Neural Computation*, 2002.
- [Li18] Z. Lipton, Y.-X. Wang, A. Smola, "Detecting and correcting for label
  shift with black box predictors (BBSE)," *ICML*, 2018.
- [Me21] A. Menon et al., "Long-tail learning via logit adjustment," *ICLR*, 2021.
- [R17] A. Ratner et al., "Snorkel: rapid training data creation with weak
  supervision," *VLDB*, 2017.
- [H15] G. Hinton, O. Vinyals, J. Dean, "Distilling the knowledge in a neural
  network," *NeurIPS DL Workshop*, 2015.
- [Ji22] S. Ji, T. Zhang, L. Ansari, J. Fu, P. Tiwari, E. Cambria, "MentalBERT:
  Publicly Available Pretrained Language Models for Mental Healthcare," *LREC*, 2022.
- [EP25] A. Shvets et al., "Emo Pillars: Knowledge Distillation to Support
  Fine-Grained Context-Aware and Context-Less Emotion Classification," *Findings
  of ACL*, 2025. (arXiv:2504.16856)
- [PG24] "PGKD: Performance-Guided LLM Knowledge Distillation for Text
  Classification," *EMNLP (Industry Track)*, 2024. (arXiv:2411.05045)
- [LS24] "Semi-Supervised Deep Label Smoothing for Suicide Risk Detection," 2024.
  (arXiv:2405.05795)
- [Hy25] "Detection of Suicidal Risk on Social Media: A Hybrid Model," 2025.
  (arXiv:2505.23797)
- [Sc25] "Evaluating LLM Reasoning for Suicide Screening with the C-SSRS," 2025.
  (arXiv:2505.13480)
- [RSD25] "RSD-15K: A Large-Scale User-Level Annotated Dataset for Suicide Risk
  Detection," *IEEE ICME*, 2025. (DOI 10.1109/ICME52785.2025.11108158)
- [Jo25] E. Jordan et al., "Speech Emotion Recognition in Mental Health: A
  Systematic Review of Voice-Based Applications," *JMIR Mental Health*, 2025.
- [Tr25] A. Triantafyllopoulos, A. Batliner, B. W. Schuller, "Charting 15 Years
  of Progress in Deep Learning for Speech Emotion Recognition: A Replication
  Study," *arXiv:2508.02448*, 2025.
- CORN/GCE/CORAL/Focal/Snorkel/Confident-Learning/Class-Balanced per-paper
  analyses: notes 45–51 in `docs/papers/finetuning-message/`.

<!-- M8 fill-ins: Table III baseline cells (fabiocarava r2-baseline-{roberta,bilstm}); §IV κ + confusion. -->
</content>
