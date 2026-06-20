# Paper 18 — WASSA@IITK at WASSA 2021: Multi-task Emotion + Empathy/Distress

> Enrichment set · Pillar 5 (intensity/empathy regression). Analysis depth: abstract + fetch. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** WASSA@IITK, WASSA 2021 (EACL workshop).
- **Link:** [arXiv:2104.09827](https://arxiv.org/abs/2104.09827) · open
- **Pebble pillar:** the closest published **regression + classification** multi-task design.

## Summary
An ELECTRA encoder trained multi-task: a categorical emotion-classification head + a continuous empathy/distress **regression** head on a shared encoder, for the WASSA 2021 empathy/distress essay shared task.

## Overlap with Pebble — 42% (ADJACENT) — highest in the enrichment set
`D1=2, D2=1, D3=1, D4=0, D5=0, D6=0, D7=2` → (3·2 + 2·1 + 1·1 + 1·2)/26 = 11/26 = **42%**
- **Closest on:** D1 (categorical emotion + continuous regression jointly on one encoder — Pebble's exact softmax+sigmoid-regression pattern) and D7 (ELECTRA, same family/scale as NeoBERT).

## Best point — Baseline to beat
Concrete ranked shared-task numbers: empathy/distress **Pearson r ≈ 0.533** (3rd), emotion **macro-F1 ≈ 0.5528** (1st), on Pebble's planned WASSA transfer source.
- **How to apply to Pebble:** When warm-starting/evaluating Pebble's continuous-score + emotion heads on WASSA empathy/distress (now downloaded — see paper 23 / `data/finetuning-message/external/wassa_empathy/`), report against r≈0.53 and macro-F1≈0.55 to show what teacher-LLM distillation + principled balancing add over naive MTL.

## Dataset
WASSA 2021 empathy/distress essays — the Buechel et al. 2018 base is acquired (CC-BY, deployable) at `data/finetuning-message/external/wassa_empathy/`.

## Caveats
Abstract + fetch only; exact ELECTRA variant (base vs large), param count, and loss-balancing scheme unread → D5/D7 lower confidence. D5=0 (no principled balancing mentioned); if the full paper documents a non-trivial weighting scheme, D5→1 (→50%).

## Deep research — full-PDF read (2026-06-16)

> Read from the local PDF `pdfs/18-wassa-iitk-2021.pdf` (arXiv:2104.09827v1, 20 Apr 2021),
> cross-checked against the **published venue version** — ACL Anthology
> [2021.wassa-1.12](https://aclanthology.org/2021.wassa-1.12/), *Proc. of the 11th WASSA workshop
> (EACL 2021)*, pp. 112–116. Authors: Jay Mundra, Rohan Gupta, Sagnik Mukherjee (IIT Kanpur).
> The published version and the arXiv v1 agree on every load-bearing number below
> (Pearson 0.533, macro-F1 0.5528, ranks 1st/3rd) — no preprint delta. The stub above was
> "abstract + fetch only"; this section resolves the unread items the Caveat flagged
> (ELECTRA variant, param count, loss-balancing scheme) and adds the per-head architecture.

### Source-access note
- PDF extracted with `pdftotext` (full text + Tables 1–2, Figures 1–3 captions). This is a
  short 5-page workshop system-description paper; the entire method, dataset, and results
  section were read end to end.
- Web-validated the headline numbers and venue against ACL Anthology.
  - Query: *"WASSA@IITK WASSA 2021 Multi-task Learning Transformer Finetuning … ACL anthology"* →
    resolved [https://aclanthology.org/2021.wassa-1.12/](https://aclanthology.org/2021.wassa-1.12/)
    (confirms pp. 112–116, EACL-2021 workshop, Pearson 0.533 / macro-F1 0.5528 / 1st-emotion /
    3rd-empathy). ✔
  - The shared-task description paper (Tafreshi et al. 2021,
    [2021.wassa-1.10](https://aclanthology.org/2021.wassa-1.10/)) confirms the task framing and the
    Buechel et al. 2018 data base. ✔

### What the paper actually does
A WASSA-2021 shared-task system on essays written in reaction to news stories about harm to a
person. Two sub-tasks: **Track I** = predict essay-level **empathy** and **distress** scores
(continuous, range 1–7, 7-point scale) — a **regression** task; **Track II** = predict the
essay's **overall emotion** (7-way categorical, Ekman-style) — **classification**. The system
is built almost entirely on **ELECTRA** (Clark et al. 2020) finetuning + multi-task learning +
ensembling, all models taken off-the-shelf from HuggingFace.

- **Data (§2).** Extended Buechel et al. (2018) release from the organizers: **1,860 train /
  270 dev / 525 test** data points. Each point = essay + empathy score + distress score +
  annotator demographics (age, income) + overall emotion + personality metrics. Emotion classes:
  **7** = anger, disgust, fear, joy, neutral, sadness, surprise (Ekman + neutral). Heavy class
  imbalance (Fig. 1): `joy` is the *least* represented (data is about harm), `anger` is the 2nd
  most frequent. ✔ (numbers from §2; corroborated by the task paper 2021.wassa-1.10).

- **Empathy/distress regression (§3.1).** Two approaches:
  1. *Vanilla ELECTRA* — finetune **ELECTRA-large** separately for empathy and for distress,
     single feed-forward layer on top, **MSE** loss, ELECTRA params trainable. A single linear
     layer beat deeper/wider heads on validation.
  2. *Multi-task ELECTRA* — **ELECTRA-large** with **two dense heads** (one empathy, one distress)
     on the shared encoder, **MSE** loss, **trained on the SUM of the empathy and distress MSE
     losses**, end-to-end. Same recipe also tried with **RoBERTa**.
  - **D-B / loss-balancing — the key extracted fact:** the multi-task loss is literally
    `L = MSE(empathy) + MSE(distress)` — an **unweighted sum, λ = 1 for both**. There is **no**
    static-λ tuning, no uncertainty/Kendall weighting, no GradNorm/PCGrad/Nash. ✔ (§3.1.2,
    verbatim: "adding the loss for Empathy and Distress and jointly training … on that total loss").
  - **Final ensembles (§3.1.3):** empathy submission = avg of {RoBERTa multitask, Vanilla
    ELECTRA}; distress submission = avg of {two multitask ELECTRA models with different dev
    performance}. Combination = **simple average** of model outputs.

- **Emotion classification (§3.2).** ELECTRA finetuned, `[CLS]` → single linear layer → 7-way
  logits, **cross-entropy** loss. Highly seed-sensitive (validation accuracy varied a lot across
  seeds — consistent with Dodge et al. 2020); they retrained many times and kept best-validation
  snapshots. **Data augmentation** with **GoEmotions** (Demszky et al. 2020) Ekman-grouped data —
  *same 7-label Ekman taxonomy* — to fight imbalance. Two schemes: **BA** (Balanced Augmentation,
  2,800 total class-balanced samples) and **RA** (Random Augmentation, 1,000 random samples).
  Augmentation lifted ELECTRA-base val macro-F1 from **0.561 → 0.6042** (Table 1). ✔
  - Ensembles by **summing class probability scores** then argmax. Ensemble 1 (submitted) =
    2 ELECTRA-base + 1 ELECTRA-large on different aug schemes; Ensemble 2 = first 7 models
    (2 ELECTRA-base, 2 ELECTRA-large, 2 RoBERTa-large, 1 ALBERT-large).

- **Results (§5).**
  - Track I (test): Pearson **empathy 0.558**, **distress 0.507**, **avg 0.533 → 3rd place**. ✔
  - Track II (test): submitted **Ensemble 1 macro-F1 = 0.5528 → 1st place**; the (unsubmitted)
    Ensemble 2 scored **0.588** macro-F1. ✔ (note: dev macro-F1 in Table 2 is higher, 0.64/0.65 —
    the 0.5528 is the official **test** number.)
  - Dev Table 2 single models (macro-F1 / acc): ELECTRA-base RA 0.604/69.25, ELECTRA-base BA
    0.608/67.77, ELECTRA-large RA 0.582/68.51, ELECTRA-large BA 0.585/66.29, RoBERTa-large RA
    0.588/67.03, RoBERTa-large BA 0.583/66.29, ALBERT-large BA 0.595/68.51, Ensemble 1 0.64/71.11,
    Ensemble 2 0.65/72.59. ≈ (dev figures, not the ranked test bar).

- **Hyperparameters (§4 Experimental Setup).** LR **1e-5**; optimizer **AdamW** (β=(0.9,0.99),
  ε=1e-6, weight decay **0**); batch size **16** for vanilla single-task regression (§3.1.1),
  **8** for multi-task (§3.1.2) and emotion classification (§3.2.1); shuffle=True. Single
  **Tesla V100-SXM2-16GB** (Google Colab). No LR schedule / warmup / gradual-unfreeze mentioned.
  No epoch count reported. ✔

- **Param counts — uncorroborated by the paper.** The paper never states parameter counts; it
  only names the *checkpoints*. From the standard HuggingFace checkpoints (knowledge, not from
  this PDF): `google/electra-large-discriminator` ≈ **335M**, `electra-base` ≈ 110M,
  `roberta-large` ≈ 355M, `albert-large-v2` ≈ 18M. ✖ (not in paper — tagged as external).

### Parts directly useful for Pebble
1. **Exact joint regression-head + classification design on one encoder** — shared ELECTRA encoder,
   two MSE regression heads (empathy, distress) for Track I, separate CE softmax head for Track II.
   This is the closest published analogue to Pebble's `severity` (regression) + `emotion` (12-way
   softmax) on one NeoBERT trunk. **→ D-D, D-B.**
2. **The loss-balancing baseline to beat: unweighted MSE sum (λ=1,1).** No principled weighting
   at all. **→ D-B.**
3. **Single-linear-layer regression head won over deeper heads** on this small set — a concrete
   head-capacity datapoint. **→ D-D.**
4. **GoEmotions used purely as an augmentation/transfer source for an Ekman 7-class head**, with a
   measured +4.3pt macro-F1 lift (0.561→0.6042) from class-balanced augmentation. **→ D-H, D-D.**
5. **Concrete numeric bars on Pebble's planned WASSA transfer source:** empathy r=0.558,
   distress r=0.507, emotion test macro-F1=0.5528. **→ D-D (metric = Pearson r).**
6. **Hyperparameter starter kit:** LR 1e-5, AdamW(wd=0), small batch (8–16), and the explicit
   warning that this regime is **severely seed-sensitive** on ~1.8k essays. **→ D-D, D-E.**

### How each part helps Pebble succeed
- **D-B (loss-balancing).** This paper *raises* the bar exactly as the Caveat predicted but in the
  opposite direction: it documents a **non-trivial-by-omission** scheme — i.e. it deliberately uses
  the **naive unweighted sum** and still wins 1st/3rd. So Pebble's principled-balancing story
  (static-λ tuned per-head, or Kendall/GradNorm/PCGrad via LibMTL) should be benchmarked *against*
  "λ=1,1 sum" as the honest baseline. Action: in the MTL ablation, include a "uniform-sum" arm and
  report the delta your weighting buys over it. Note the regimes differ — here both tasks are MSE
  on the *same 1–7 scale*, so summing is roughly scale-matched; Pebble mixes **MSE(severity) +
  CE(emotion)**, whose gradient scales are *not* comparable, so an unweighted sum is a worse
  starting point for Pebble than it was here. That asymmetry is itself the argument for
  weighting/normalization in Pebble. **(Confidence: high — the loss form is stated verbatim.)**
- **D-D (severity/energy regression).** Adopt the metric and head shape directly: **Pearson r**
  as the severity-head eval metric, **single linear regression layer** on the pooled encoder
  output, **MSE** loss. Use empathy r≈0.558 / distress r≈0.507 as the *external* baseline when
  reporting Pebble's WASSA-transfer numbers (data already at `data/finetuning-message/external/wassa_empathy/`).
  Pebble's edge to demonstrate over this paper: teacher-LLM silver labels at scale + a domain-
  adapted encoder, vs. this paper's tiny 1,860-example finetune.
- **D-H / D-D (augmentation transfer).** GoEmotions→Ekman-7 augmentation is a *validated* recipe
  (+4.3pt). Pebble already maps GoEmotions→12-label emotion; this paper is the citation that
  GoEmotions augmentation measurably helps an imbalanced small-essay emotion head, and that
  **balanced** augmentation (BA) generalizes while over-sampling distorts the train/test
  distribution. Action: keep an explicit balanced-vs-random augmentation arm in the emotion-head
  data plan.
- **D-E (fine-tuning stability).** The paper's loudest empirical message is *seed variance* on
  small data. For Pebble's small high-severity / WASSA slices, budget multiple seeds + best-val
  snapshot selection, and consider it a confound when comparing MTL schemes — exactly the failure
  mode this paper hit.

### Child mental-health lens
- **Domain & register mismatch (high transfer risk).** The data is **adult-written argumentative
  essays** (mean length long; demographics include income) reacting to *news about harm to others* —
  empathy/distress are felt *about a third party in a story*, not the writer's own first-person
  crisis. Pebble scores **children's own turn-level mid-conversation distress**. So the *task shape*
  (regression head, Pearson metric, MSE) transfers cleanly, but the **construct does not**:
  "distress" here ≈ reader's vicarious distress over a news event, not a child's self-reported
  acute distress. Treat the r≈0.53 numbers as an **architecture/metric baseline only**, never as a
  reachable bar for child self-distress.
- **Essay-length vs. turn-level mismatch.** Essays are long-form, single-shot; Pebble text is short
  conversational turns. The single-linear-head + small-batch recipe should still hold, but the
  augmentation-distribution caution ("too much sampling makes train ≠ test") is sharper for Pebble,
  where child-register turns differ markedly from GoEmotions Reddit comments.
- **Silver-label parallel.** This paper has *human* gold labels on a tiny set and fights the size
  problem with augmentation; Pebble has *abundant* silver labels and fights the *noise* problem.
  The shared lesson: the bottleneck is label quality/quantity, and augmentation/transfer choices
  visibly move the score — so Pebble should ablate its silver-label volume vs. quality the way this
  team ablated augmentation volume.
- **Ethics.** No human-subjects/safety concerns specific to this paper (public essay corpus, no
  minors, no crisis decisions). Nothing to inherit on the governance side — for that, paper 01
  (FAIIR) remains the reference.

### Limitations & open questions for Pebble
- **Contradiction vs. Pebble's plan (D-B).** Pebble's Decision Register leans toward *principled*
  MTL weighting (Kendall/GradNorm/PCGrad/Nash via LibMTL). This paper is a **counter-example**: the
  1st-place emotion + 3rd-place empathy system used a **plain unweighted MSE sum** and no learned
  weighting — evidence that on small, scale-matched tasks the elaborate machinery may be
  unnecessary. The honest Pebble framing: principled weighting must *justify itself* against this
  uniform-sum baseline, especially since Pebble's MSE+CE mix is *not* scale-matched the way this
  paper's MSE+MSE is.
- **Contradiction vs. FAIIR (paper 01) on imbalance handling.** FAIIR fought class imbalance with
  **oversampling on 2 of 3 ensemble members + per-class thresholds**; this paper warns that
  **oversampling/over-augmentation distorts the train distribution** and instead prefers *balanced*
  augmentation from an external corpus (GoEmotions). Pebble must pick a lane per head — the two
  closest-analogue papers disagree on whether to oversample.
- **No param counts, no epochs, no schedule** in the paper — the recipe is under-specified for
  exact reproduction (param counts here are external/HuggingFace knowledge, tagged ✖).
- **Tiny test set (525 essays).** Pearson on 525 points has wide CIs; the 0.558 vs 0.507
  empathy/distress gap and the 0.5528 vs 0.588 ensemble gap may not be statistically robust — do
  not over-index on the exact decimals as targets.
- **No calibration, no ordinal treatment.** Empathy/distress are 1–7 ordinal but modeled as plain
  MSE regression (no ordinal loss, no calibration) — leaves open exactly the D-C/D-G questions
  (ordinal/distance-aware loss, calibration) that Pebble still has to answer elsewhere.
