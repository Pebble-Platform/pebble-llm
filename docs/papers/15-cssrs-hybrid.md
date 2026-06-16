# Paper 15 — Detection of Suicidal Risk on Social Media: A Hybrid Model

> Enrichment set · Pillar 4 (C-SSRS severity). Analysis depth: abstract-only. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** 2025.
- **Link:** [arXiv:2505.23797](https://arxiv.org/html/2505.23797v1) · open
- **Pebble pillar:** suicide-risk severity classification with a RoBERTa backbone.

## Summary
A four-level Reddit suicide-severity classifier combining RoBERTa contextual embeddings with TF-IDF + PCA handcrafted features, beating RoBERTa-only and BERT baselines.

## Overlap with Pebble — 31% (peripheral)
`D1=0, D2=2, D3=0, D4=0, D5=0, D6=1, D7=2` → (2·2 + 2·1 + 1·2)/26 = 8/26 = **31%**
- **Closest on:** D2 (suicide-risk/crisis text) and D7 (RoBERTa encoder backbone).

## Best point — Baseline to beat
Reports **weighted F1 = 0.7512** on a four-level Reddit suicide-severity task close to Pebble's safety head.
- **How to apply to Pebble:** Use 0.75 weighted-F1 as the comparison bar for Pebble's crisis/severity head on a four-level Reddit corpus; note their TF-IDF+PCA concatenation as a cheap ablation — but frame Pebble's advantage as a **recall-floored** safety head (≥0.95), since their weighted-F1 objective doesn't protect the highest-risk minority class.

## Dataset
Four-level Reddit severity setup, consistent with the C-SSRS / CSSRS-Reddit lineage (inferred, not confirmed). No new open dataset identified to acquire.

## Caveats
Abstract-only; PDF body not text-extractable. **Exact dataset name/size, the four class definitions, and per-class high-risk recall could not be verified.** D6 scored 1 (severity is the target) not 2 — no hard recall constraint or ordinal loss evidenced; lowest-confidence dimension.

## Deep research — full-PDF read (2026-06-16)

> Source: full-text read of the local PDF `pdfs/15-cssrs-hybrid.pdf` (arXiv:2505.23797v1, 26 May 2025)
> via `pdftotext` — the body extracted cleanly this time (the earlier "not text-extractable" caveat is
> superseded). **Provenance:** the headline numbers were cross-checked against the **published venue
> version** — this paper appears in the **ASONAM 2025 proceedings** (IEEE/ACM Int'l Conf. on Advances in
> Social Networks Analysis and Mining), paper `1304_094.pdf`. The proceedings PDF was fetched and
> `pdftotext`-extracted; **every load-bearing number below matches between preprint and proceedings**
> (weighted-F1 0.7512, 2,999 posts, Fleiss κ 0.5641, class split 45.28/28.21/17.97/8.54%, per-class F1
> 0.7541/0.7961/0.6767/0.6527), so there is no preprint-vs-published delta to reconcile. The proceedings
> retitles the affiliation "Department of Math and Computer Science, Suffolk University." Search trace:
> query `"Detection of Suicidal Risk on Social Media Hybrid Model RoBERTa TF-IDF PCA Suffolk weighted F1
> 0.7512"` → arXiv:2505.23797 (`arxiv.org/abs/2505.23797`) + ASONAM proceedings
> (`web.ntpu.edu.tw/~myday/doc/ASONAM2025/ASONAM2025_Proceedings/pdf/papers/1304_094.pdf`).

### What the paper actually does (method, data, results — exact numbers)

**Authors / venue.** Zaihan Yang, Ryan Leonard, Hien Tran, Rory Driscoll, Chadbourne Davis (Suffolk
University, Boston). **ASONAM 2025** (published) / arXiv:2505.23797v1 (preprint). ✔ corroborated.

**Task & framing.** Multi-class (4-way) classification of a **single Reddit post** into a suicide-risk
severity level. Categorical cross-entropy, softmax head. *Post-level, not user-level.* ✔ (§I, §IV-A).

**The 4-class scheme (Table II) — note: NO "Supportive" class.** ✔ corroborated (§III-B):
- **IN — Indicator:** "no explicit expression concerning suicide" (the *low/neutral* floor here).
- **ID — Ideation:** "explicit suicidal expression but no plan."
- **BR — Behavior:** "explicit suicidal expression AND a plan to commit suicide or self-harming behaviors."
- **AT — Attempt:** "explicit expressions concerning historic suicide [attempt]."
The authors explicitly adopt the scheme of ref [11] (Gaur/CSSRS-Reddit lineage) **as later pruned by ref
[12] (HKPU), which "deprecated the *supportive* category … and retained the remaining four severity
levels"** (§II). So this is the **Gaur 5-class minus Supportive**, ordered IN < ID < BR < AT. This is a
*different label space* from paper 14 (which keeps Supportive and is 5-class). Critical for D-C.

**Dataset (Table I) — built, not the 500-user benchmark.** ✔ corroborated (§III-A):
- **2,999 posts**, **473 unique users**, 13,062 distinct word tokens, **avg 150.27 tokens/post**.
- Composition: the **HKPU 500 labeled posts** (ref [12]) + **2,499 newly scraped + hand-labeled posts**
  (899 of which from r/SuicideWatch via PRAW, plus the rest). Posts span 2008-12-16 → 2025-01-03.
- **Class distribution (Fig 1):** Ideation **45.28%**, Indicator **28.21%**, Behavior **17.97%**,
  Attempt **8.54%** (≈ 1358 / 846 / 539 / 256 posts). AT is the rare, clinically-critical class.
- **Annotation:** 5 annotators (1 faculty + 4 undergrad CS students), Fleiss's **κ = 0.5641** ("moderate
  agreement"). ✔ corroborated.

**Model (the hybrid, §IV-A).** RoBERTa-base [CLS] embedding (768-d, 12 layers, 512-token cap, BPE) **⊕
concatenated with** a TF-IDF→PCA vector: TF-IDF over the **M = 3,000** top features, PCA-reduced to **N =
300** components. Combined vector = **768 + 300 = 1068-d** → linear → softmax → categorical CE. ✔ (§IV-A).
**Hyperparameters:** batch size **3**, LR **1e-5**, weight decay **0.01**, AdamW, early stopping. ✔ (§V-B).
(DistilBERT is also mentioned as a baseline in passing.)

**Evaluation protocol (§V-A).** **5-fold cross-validation, NON-stratified** ("each fold may have a
different distribution … better reflects real-world scenarios"); within each train+val split, an 80:20
stratified inner split. **All metrics are weighted** (weighted P/R/F1) and **averaged across the 5 folds.
No accuracy, no macro-recall, no per-class recall reported.** ✔ corroborated (§V-A). This is the opposite
metric choice from paper 14 (which headlines accuracy + macro-recall + weighted-balanced acc).

**Headline results — weighted F1, 5-fold averages:**

| Model | weighted P | weighted R | weighted F1 |
|---|---|---|---|
| **RoBERTa-TF-IDF-PCA (hybrid)** | **0.7557** | **0.7532** | **0.7512** ✔ |
| RoBERTa-only | 0.7523 | 0.7496 | 0.7499 ✔ |
| BERT | 0.7045 | 0.6996 | 0.6949 ✔ |

(Table VI). **The hybrid's gain over RoBERTa-only is +0.0013 weighted-F1 (0.7512 vs 0.7499) — within
cross-fold noise.** The TF-IDF+PCA concatenation is essentially a no-op on this data.

**Resampling ablation (Table IV).** Original 0.7499 / OSam 0.7421 / USam 0.7022 / SWL 0.7480 weighted-F1.
**"Original" (no rebalancing) wins**; oversampling, undersampling, and inverse-frequency weighted loss
all *hurt* — authors attribute this to the non-stratified test folds keeping the original imbalance, so a
rebalanced model mismatches the test distribution. ✔ (§V-B-1).

**Data-augmentation ablation (Table V).** Abbrev-expansion (111 pairs) + emoji→text + summarization +
Google-Translate round-trip (EN→ES→EN), all *with* oversampling: **w/o-DA 0.7421 → DA 0.6648 weighted-F1
— augmentation hurts badly** (−0.077). ✔ (§V-B-2). Final hybrid uses NO resampling, NO augmentation.

**Per-class F1 (Table VII) — the load-bearing table for Pebble:** ✔ corroborated.

| Severity | Hybrid F1 | RoBERTa-only F1 | share of data |
|---|---|---|---|
| Indicator (IN) | 0.7541 | 0.7681 | 28.21% |
| Ideation (ID) | 0.7961 | 0.7875 | 45.28% |
| Behavior (BR) | 0.6767 | 0.6721 | 17.97% |
| **Attempt (AT)** | **0.6527** | 0.6437 | **8.54%** |

F1 tracks class frequency (ID > IN > BR > AT). **Crucially, AT F1 = 0.65 is non-zero** — sharply unlike
paper 14, where AT collapsed to *zero* true positives. The difference is dataset granularity, see below.

**Confusion matrix (Fig 3, 5-fold totals).** Dominant errors: IN↔ID confused (213 + 105 instances),
BR→ID (129), AT→BR (43), AT→ID (39). The model conflates adjacent-and-near severities; AT is most often
mislabeled *down* to Behavior or Ideation. The errors are **structurally ordinal** (mass clusters near
the diagonal) — yet the paper uses **flat categorical CE with no ordinal/distance penalty**. ✔ (§V-B-3).

**Traditional baselines (Table VIII, weighted-F1).** Best TF-IDF classifier SVM 0.5880 (stemming);
LogReg ~0.57; Random Forest ~0.50; Naive Bayes ~0.31; Word2Vec features worse across the board. RoBERTa
(0.75) beats all traditional classifiers by ~0.16 weighted-F1. ✔ (§V-B-4).

### Parts directly useful for Pebble (each tagged with Decision IDs)

1. **A SECOND, independent bar on a 4-class C-SSRS-lineage severity task: weighted-F1 0.7512 [D-C].**
   This is a genuinely different operating point from paper 14's 0.5233 accuracy — *different dataset
   (2,999 posts vs 500 users), different granularity (post vs aggregated-user), different class set
   (4-class no-Supportive vs 5-class), different metric (weighted-F1 vs accuracy/macro-recall)*. Pebble
   now has **two non-comparable C-SSRS bars**; this paper supplies the **post-level, 4-level** one.

2. **Per-class F1 with a non-zero Attempt result (0.6527) [D-C].** Concrete target for Pebble's severity
   head on a 4-level mapping. The contrast with paper 14's AT=0 is itself the most useful datum (below).

3. **A clean negative result: TF-IDF+PCA concatenation buys ~0 (+0.0013 F1) over RoBERTa-only [D-A,
   D-C].** Pebble should **not** spend effort on handcrafted-feature concatenation — a pretrained encoder
   already subsumes TF-IDF term-weighting on this task. Saves an ablation.

4. **A clean negative result: oversampling / undersampling / inverse-freq weighted loss ALL hurt under a
   non-stratified-test protocol [D-B, D-C, D-G].** When the test distribution is left imbalanced,
   rebalancing the *training* set degrades weighted-F1. Directly informs Pebble's loss-balancing choice:
   naive class rebalancing is not free, and the eval protocol determines whether it helps.

5. **A clean negative result: NLP data augmentation (back-translation, abbrev/emoji expansion,
   summarization) hurt by −0.077 F1 [D-C].** For short crisis posts, meaning-altering augmentation
   damages the signal. Pebble should be skeptical of augmenting child crisis text.

6. **Exact reproducible hyperparameters [D-A]:** RoBERTa-base, 512-token cap, batch 3, LR 1e-5, weight
   decay 0.01, AdamW, early stopping, M=3000/N=300. A concrete (if weak-baseline) recipe.

### How each part helps Pebble succeed (concrete actions)

- **Severity head — use BOTH bars, but never average them [D-C].** Report Pebble's NeoBERT severity path
  against *this* paper's **weighted-F1 0.7512 on a 4-level post-level split** AND paper 14's **0.5233
  accuracy / 0.4777 macro-recall on the 5-level user-level split** — as two *separate* lines, each on its
  own dataset/metric. Do not claim "beat 0.75" against the 500-user data or "beat 0.52" against the
  2,999-post data; they are different tasks. The honest framing: Pebble targets ID/IN/BR/AT post-level
  (this paper) and SU/IN/ID/SB/AT user-level (paper 14) as two distinct calibration anchors.
- **Adopt distance-aware/ordinal loss — this paper's confusion matrix is fresh evidence [D-C].** Errors
  cluster near the diagonal (IN↔ID 213+105; AT→BR 43, AT→ID 39) yet the model used flat CE that does not
  penalize an AT→ID miss (2 steps, dangerous) more than IN→ID (1 step, benign). Pebble should map IN<ID<BR<AT
  to an ordinal scale and use a distance-weighted loss (CORAL/QWK). *Expected payoff:* targets exactly the
  AT→{BR,ID} down-grading this paper exhibits — the costliest miss for a safety pathway.
- **Skip TF-IDF concatenation and skip augmentation [D-A, D-C].** The paper measured both as net-negative
  or net-zero. Pebble should drop these from its candidate-ablation list and reallocate budget to ordinal
  loss + recall-floor + calibration, which this paper does *not* test.
- **Choose the eval protocol deliberately, because it changes the rebalancing verdict [D-B, D-G].** This
  paper's non-stratified-test 5-fold made rebalancing harmful. Pebble should decide up front whether the
  held-out test mirrors the deployed imbalance (then don't rebalance) or is rebalanced for fairness (then
  rebalancing the train set is consistent). Pebble's recall-floored safety head implies the test must
  *keep* the imbalance (you care about AT recall in the wild), which this paper's result supports.
- **Add the recall floor + calibration this paper omits [D-G].** The paper reports only weighted P/R/F1
  — **no per-class recall, no threshold policy, no calibration, no confidence intervals across folds.**
  Pebble's contribution is precisely to add **per-class (esp. AT) recall with a ≥0.95 floor**, a tuned
  decision threshold, and calibrated probabilities — none of which exist here.

### Child mental-health lens (Pebble serves children)

- **Domain mismatch — adult Reddit, self-selected, post-level.** Like paper 14, this is **adult Reddit**
  (r/SuicideWatch, r/depression, r/anxiety, r/selfharm), self-disclosing help-seekers, ~150-token posts.
  Children express crisis in shorter, indirect, somatic, school/family/bullying-framed language with
  emoji and game-speak. A 4-level mapping calibrated here will **under-read child crisis signals** — the
  fatal direction.
- **Annotation quality is a child-transfer red flag.** Fleiss κ = 0.5641 ("moderate") comes from **four
  undergraduates + one faculty member**, *not clinicians*. For a 4-level clinical severity scheme these
  are weak labels even for adults; for child-register text they would be weaker still. Treat the label
  *scheme* as transferable, the *labels* as adult-non-clinical silver.
- **The non-zero AT F1 (0.65) is encouraging but misleading for children.** AT F1 is non-zero here only
  because each post is short and self-contained (one post = one disclosed historic attempt), unlike paper
  14's 5,041-token aggregated-user inputs where AT drowned. A child rarely posts a clean "historic
  attempt" disclosure; the favorable granularity that rescues AT here does not exist for live child chat.
- **Mitigations.** (a) Use this 4-level scheme to *pretrain/calibrate* an ordinal severity scale, never
  as the sole child crisis authority; (b) bias the child safety head toward sensitivity (more false
  positives → human escalation); (c) build a small expert-reviewed child-register validation slice before
  trusting any C-SSRS-trained head; (d) keep human-in-the-loop escalation — no model here is deployment-grade
  for minors. (e) Because labels are student-annotated, do not cite this paper's κ as clinical validation.
- **Ethics.** Scraped public Reddit, no consent, no IRB statement, annotated by students — acceptable as a
  research benchmark, not as a clinical ground truth. Any model trained on it is assistive, not diagnostic.

### Limitations & open questions for Pebble

- **CONTRADICTION vs paper 14 (`14-cssrs-label-smoothing.md`) — the headline bars are NOT comparable, and
  the stub's framing overstates the link.** The stub for paper 15 (and the analysis card) treats "0.75
  weighted-F1" as a bar "close to Pebble's safety head" on the "C-SSRS / CSSRS-Reddit lineage." Full read
  shows: (1) **different dataset** — 2,999 short *posts* (473 users) self-scraped + HKPU 500, vs paper 14's
  500 *aggregated users*; (2) **different class set** — 4 classes *without* Supportive (IN/ID/BR/AT) vs
  paper 14's 5 classes *with* Supportive (SU/IN/ID/SB/AT); note this paper's "Behavior=BR" ≈ paper 14's
  "SB", and this paper's "Indicator=IN" is the *neutral floor* whereas paper 14's "IN" is *Suicide
  Indicator* — **the labels collide in name but differ in meaning**; (3) **different metric** —
  weighted-F1 only vs accuracy/macro-recall/balanced-acc; (4) **different granularity** — post vs user.
  **Net:** 0.7512 weighted-F1 (this) and 0.5233 accuracy (paper 14) measure different things; reporting
  them as a single "C-SSRS bar" would be wrong. They also *disagree on Attempt*: AT F1 0.65 here vs AT
  recall 0 in paper 14 — explained entirely by granularity, not modeling.
- **CONTRADICTION vs the Pebble plan's instinct to oversample/augment [D-B].** Pebble's imbalance plan
  leans on class-balancing; this paper shows oversampling, undersampling, weighted loss, AND augmentation
  *all hurt* weighted-F1 under a realistic (imbalanced-test) protocol. Pebble must justify rebalancing
  with the test protocol in mind, not assume it helps.
- **No recall floor, no calibration, no per-class recall, no CIs.** The paper's entire evaluation is
  fold-averaged weighted P/R/F1 — it cannot speak to D-G at all, and the +0.0013 hybrid gain has no error
  bar (5-fold, no CI). Pebble's "beat 0.75 weighted-F1" claim is meaningless without per-fold CIs.
- **The hybrid contribution is essentially null.** +0.0013 F1 over RoBERTa-only is the paper's own data
  arguing *against* its central method; the real artifact is the dataset + per-class table, not the model.
- **Open question — IN/BR vs SU/IN/ID/SB/AT crosswalk.** Which Pebble `severity` ordinal mapping reconciles
  this 4-class (no Supportive) scheme with paper 14's 5-class scheme so both can be calibration anchors?
  The naming collision (IN means opposite things) must be resolved before either is used. The two papers
  give no crosswalk; Pebble must define it, and it interacts with the ordinal-loss spacing decision.
- **Open question — does any handcrafted feature help a 250M encoder?** Here TF-IDF+PCA added ~0 to
  RoBERTa-base. Unlikely to help NeoBERT either, but if Pebble ever tests it, this is the null baseline.
