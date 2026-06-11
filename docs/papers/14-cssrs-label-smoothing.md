# Paper 14 — Semi-Supervised Deep Label Smoothing for Suicide Risk Detection

> Enrichment set · Pillar 4 (C-SSRS severity). Analysis depth: abstract + arXiv HTML. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** 2024.
- **Link:** [arXiv:2405.05795](https://arxiv.org/abs/2405.05795) · open
- **Pebble pillar:** suicide-risk severity — benchmarks the **exact Reddit C-SSRS 500-user dataset Pebble already downloaded** (`data/external/cssrs/`).

## Summary
A CNN over learnable embeddings does single-task 5-class C-SSRS suicide-risk classification, with soft-label smoothing via MC-Dropout uncertainty. Improves the C-SSRS benchmark from 43.12% → 52.33% accuracy.

## Overlap with Pebble — 23% (peripheral)
`D1=0, D2=2, D3=0, D4=0, D5=0, D6=1, D7=0` → (2·2 + 2·1)/26 = 6/26 = **23%**
- **Closest on:** D2 (suicide-risk domain) and partial D6 (crisis-class recall reported, not enforced).

## Best point — Baseline to beat
A clean, citable benchmark on the dataset Pebble has: **43.12% → 52.33% acc, 49.23% weighted-balanced acc, 47.77% macro recall**, using only a CNN.
- **How to apply to Pebble:** Report Pebble's NeoBERT crisis/severity path against these numbers; a 250M pretrained encoder + GoEmotions warm-start should clear 52% acc / 49% balanced acc, and macro-recall is where the high-recall safety head shows its value.
- *Secondary (not headline):* MC-Dropout soft labels capture inter-rater disagreement — a possible regularizer for noisy Gemini silver labels.

## Dataset
Uses CSSRS-Reddit (already acquired, CC-BY-4.0). No new acquisition.

## Caveats
Architecture details from arXiv HTML v1. Despite the "semi-supervised" title, no unlabeled-data/pseudo-label mechanism is described (MC-Dropout self-relabeling only) — D4 and the semi-supervised claim are weaker than the title. No transformer/MTL/regression. Value to Pebble is almost entirely a comparison number on a shared dataset.

## Deep research — full-PDF read (2026-06-10)

> Source: full-text read via the arXiv HTML v1 mirror of arXiv:2405.05795 (the local `pdftoppm` renderer for the stored PDF was unavailable, so the canonical HTML — same tables/equations/numbers as the PDF — was read instead). Numbers below are quoted from the paper's results table and method section. Where the paper is silent (filter sizes, per-class confusion matrix), it is marked "not reported" rather than inferred.

### What the paper actually does (method, data, results — from the PDF, with exact numbers)

**Task & framing.** Single-task **5-class** supervised classification of a Reddit user into a C-SSRS-derived severity scheme. The problem the paper attacks is *label noise / annotator disagreement*: four clinical psychiatrists labelled the data with **pairwise agreement only ~60–80%**, so the authors argue one-hot targets are unfaithful and a softened target distribution is better.

**Method — three escalating label treatments:**
1. **Hard labels** (one-hot, plain categorical cross-entropy, Eq. 2: `C = −Σ_k y_k·log(ŷ_k)`).
2. **Uniform label smoothing** (Eq. 3): `y_i = 1−α` for the true class, `y_i = α/(k−1)` otherwise, `k=5`. Tested at **α=0.1 and α=0.05**.
3. **Deep Bayesian (non-uniform / "fuzzy") label smoothing** — the contribution. Train once on hard labels, then run **MC-Dropout with T=100** stochastic forward passes and average the softmax (Eq. 9: `p_k = (1/T)·Σ_{t=1}^{T} p_{kt}`). The averaged per-example distribution becomes the **new soft target**, and the network is retrained against it. The smoothing is **per-example and data-driven** — it concentrates probability mass where the model itself is uncertain — unlike uniform smoothing which spreads a fixed α to all off-diagonal classes.

**"Semi-supervised" caveat (confirmed on full read):** there is **no unlabeled corpus and no pseudo-labeling of new data**. The "semi-supervised" label refers only to the model relabeling its *own already-labelled* training set via MC-Dropout. This is self-distillation / soft-relabeling, not semi-supervised learning in the usual sense — treat the title as overselling.

**Data.** Reddit C-SSRS, **500 users → 500 examples** (one aggregated text per user), 5 classes with severe imbalance:
- Suicidal **Ideation (ID): 171**
- **Supportive (SU): 108**
- Suicide **Indicator (IN): 99**
- Suicidal **Behaviour (SB): 77**
- Actual **Attempt (AT): 45**

(Sum = 500.) Split: **80/20 train/test hold-out**, no cross-validation reported (so the test set is ~100 examples — small, high-variance). Preprocessing: each user's text is tokenized into a **fixed sequential array of length 5,041 tokens**, fed to a **learnable (from-scratch) embedding layer** (dim not reported). No pretraining; no subword tokenizer specified.

**Architecture.** Small 1-D CNN: input (5,041) → learnable embedding → Conv → Conv → MaxPool → Flatten → Dense(5, softmax). Filter/kernel/pool sizes **not reported**.

**Results (Table 2 — the full grid, exact numbers):**

| Method | Accuracy | Weighted-Balanced Acc | Macro Precision | Macro Recall |
|---|---|---|---|---|
| Gaur et al. (baseline) | 0.4312 | 0.2567 | 0.2903 | 0.2734 |
| Hard labels (this work) | 0.4451 | 0.3036 | 0.3337 | 0.3036 |
| Uniform smoothing α=0.1 | 0.4699 | 0.3698 | 0.5284 | 0.3698 |
| Uniform smoothing α=0.05 | 0.4783 | 0.4226 | 0.4364 | 0.4266 |
| **Deep Bayesian smoothing** | **0.5233** | **0.4923** | 0.4721 | **0.4777** |

Headline 43.12% → 52.33% (= **+9.21 pts** accuracy). The bigger story is in the **balanced** metrics: weighted-balanced accuracy nearly doubles (0.2567 → 0.4923) and macro recall rises 0.2734 → 0.4777 — smoothing pulls the model off the "always predict the majority class" failure mode. The paper notes the Gaur baseline "overwhelmingly predicts the predominant class" (≈92% of predictions land in Ideation/Supportive).

**Critical failure mode (stated in the PDF):** the **Actual-Attempt (AT) class had zero true positives across every method**, including the best one. The most clinically severe class — the one Pebble's safety head exists to catch — is the one *all* models in this paper completely miss. No confusion matrix or ordinal/adjacent-error analysis is reported (so the "ordinal" framing is Pebble's inference, not something this paper measures).

### Parts directly useful for Pebble (specific)

1. **The exact published bar on Pebble's own dataset.** Pebble holds the identical 500-user C-SSRS split (`data/external/cssrs/`). Targets to beat: **accuracy 0.5233, weighted-balanced accuracy 0.4923, macro recall 0.4777, macro precision 0.4721**, vs a Gaur baseline of 0.4312 / 0.2567 / 0.2734. Because the test set is ~100 examples (80/20, no CV), Pebble should report **k-fold or repeated splits with confidence intervals** — beating 52.33% on a single 100-row hold-out is within noise.

2. **Per-example, uncertainty-driven soft labels (the actual transferable method).** The MC-Dropout-averaged target (Eq. 9, T=100) is a concrete recipe for turning noisy labels into per-example soft targets that concentrate mass where the model is genuinely unsure. Directly reusable for Pebble's **Gemini silver labels**, which share the pathology (a single noisy teacher, no inter-rater signal).

3. **The annotator-disagreement justification (60–80% pairwise).** A citable, domain-specific argument that one-hot crisis labels are *wrong* and soft targets are more faithful — framing for why Pebble's heads can consume soft/distributional targets rather than hard labels.

4. **The balanced-metric protocol.** Raw accuracy is misleading under this imbalance (a majority-only predictor already scores 43%). Pebble must headline **weighted-balanced accuracy + macro recall**, not accuracy.

5. **A negative result that defines Pebble's reason to exist:** even the SOTA here gets **0 true positives on Actual-Attempt**. That is the gap Pebble's recall-≥0.95 safety head must close.

### How each part helps Pebble succeed (concrete actions)

- **Severity head — adopt distance-aware/ordinal loss, not the paper's flat CE.** This paper's own data is the strongest argument *for* ordinality even though it never measures it: flat cross-entropy gives no extra penalty for predicting "Supportive" on an "Attempt" user vs an adjacent slip, and AT collapses to zero recall. Pebble should map the 5 levels to an ordinal scale (SU<IN<ID<SB<AT) and use **a distance-weighted loss (CORAL/ordinal-regression or a QWK-style penalty)** so a high→low miss costs far more than an adjacent one. *Expected payoff:* directly attacks the zero-true-positive-on-AT failure that flat-CE models (incl. this SOTA) all show.
- **Safety head — do not let the 5-way softmax own the AT class.** Pebble's binary crisis head should treat AT (and likely SB) as positive with a **recall floor ≥0.95**, evaluated separately from the 5-way head. The paper proves a single softmax head will *silently drop* the rarest, most dangerous class; a dedicated high-recall binary head with class-balanced/focal loss is the mitigation.
- **Silver-label denoising — apply MC-Dropout soft relabeling to Gemini labels.** Run T≈100 MC-Dropout passes of an early Pebble checkpoint over the Gemini-labelled set, average (Eq. 9), and use the result as soft targets for a second pass. *Expected payoff:* a cheap regularizer that down-weights confidently-wrong teacher labels — the paper shows this moved balanced accuracy 0.30→0.49.
- **Evaluation protocol — match then exceed.** Report Pebble on the same 5-class C-SSRS split with **accuracy / weighted-balanced accuracy / macro recall / macro precision**, plus **per-class recall for AT and SB explicitly** (the paper hides these in macro averages), using **repeated/k-fold splits with CIs**. A 250M pretrained encoder + GoEmotions warm-start should clear 0.5233 acc; the real test is whether it does so *while getting AT recall > 0*.

### Child mental-health lens (Pebble serves children)

- **Domain mismatch is severe.** This dataset is **adult Reddit users** writing long-form posts (5,041-token sequences) in adult registers. Children/young users express crisis differently: shorter messages, indirect/somatic language ("my tummy hurts and I don't want to wake up"), school/family/bullying framing, emoji and game-speak, far less clinical vocabulary. A severity mapping calibrated on adult C-SSRS will **systematically under-read child crisis signals** — the direction that costs lives.
- **The AT zero-recall result is a red flag for child deployment.** If the published SOTA cannot detect adult Attempt posts at all, a model warm-started on this distribution will be *worse* on child Attempt language it has never seen. Pebble must **not** treat C-SSRS-derived severity as deployment-ready for children; it is a research-arm signal only.
- **Mitigations.** (a) Use C-SSRS only to *pretrain/calibrate* the severity ordinal scale, never as the sole crisis authority for children; (b) bias the child-facing safety head toward **higher sensitivity** (accept more false positives → human escalation), since the cost asymmetry is steeper for children; (c) build/curate a **child-register crisis validation slice** (even small, expert-reviewed) before trusting any C-SSRS-trained head; (d) keep a human-in-the-loop escalation path — no model in this literature is accurate enough to act autonomously on a child.
- **Ethics caveats.** Reddit C-SSRS is adult, consent-questionable scraped data under CC-BY-4.0 — acceptable for research, but the *labels* encode adult clinician judgment that may not transfer to minors. Treat any model trained on it as **assistive, not diagnostic**, especially for children.

### Limitations & open questions for Pebble

- **Tiny, single-split evaluation.** ~100-example hold-out, no CV → the 52.33% headline has wide error bars. Pebble's "beat 52%" claim is meaningless without CIs; the real target is *balanced accuracy + AT recall with confidence intervals*.
- **No ordinal evidence in-paper.** The ordinal-loss lesson Pebble draws is *inferred* from the AT collapse, not measured here (no confusion matrix, no QWK/MAE). Pebble can make reporting ordinal metrics a genuine contribution.
- **"Semi-supervised" is a misnomer** (self-relabeling only); do not cite it as a semi-supervised baseline.
- **Architecture under-specified** (filter/kernel/embedding dims absent) → not exactly reproducible; treat the *numbers*, not the model, as the artifact.
- **Open question:** does MC-Dropout soft-relabeling still help with a 250M pretrained encoder (vs a from-scratch CNN)? Pretrained models are already better-calibrated, so the gain may shrink — ablate, don't assume.
- **Open question:** what is the right C-SSRS→Pebble-`severity` numeric mapping (equal-interval vs clinically-weighted spacing of SU/IN/ID/SB/AT)? The paper offers no guidance; Pebble must decide this, and it interacts with the ordinal loss.
