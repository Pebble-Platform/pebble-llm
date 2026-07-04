# Paper 47 — Distilling the Knowledge in a Neural Network

> Family B (distillation) · foundational soft-target/temperature method. Analysis depth: abstract + arXiv PDF (canonical method). Compiled 2026-06-25.

## Bibliographic info
- **Authors / Year / Venue:** Hinton, Vinyals & Dean. 2015. NeurIPS 2014 Deep Learning Workshop.
- **Link:** [arXiv:1503.02531](https://arxiv.org/abs/1503.02531) · open — **VERIFIED** (title/authors/year/venue confirmed via arXiv abstract page).
- **R2 pillar:** Family B foundational citation — the soft-target/temperature method that PGKD (paper 13) and Emo Pillars (paper 04) build on. R2 effectively distills a single LLM teacher's labels into a small encoder.

## Summary
The teacher's output **logits are softened with a temperature `T`** in the softmax — `q_i = softmax(z_i / T)` — producing a smooth class distribution that exposes the relative probabilities of the *wrong* classes ("**dark knowledge**": e.g. that a "Behavior" example is much closer to "Ideation" than to "Indicator"). The student is trained on a **two-term loss**: a KL/soft cross-entropy between the student's temperature-`T` softmax and the teacher's soft targets (weighted `T²` to keep gradient magnitudes comparable), **plus** standard cross-entropy on the hard ground-truth labels at `T=1`. The soft targets carry far more information per example than a one-hot label and act as a strong regularizer, letting a small student match a large/ensemble teacher with much less data.

## Overlap with Pebble/R2 — 23%
`D1=0, D2=2, D3=0, D4=2, D5=0, D6=0, D7=1` → (3·0 + 2·2 + 1·0 + 2·2 + 2·0 + 2·0 + 1·1)/26 = (4 + 4 + 1)/26 = 9/26 = **23% (peripheral)**
- **Per-dimension scores written before the number** (formula `(Σ wᵢ·scoreᵢ)/26 × 100`, fixed). D2=2 because R2's domain *is* C-SSRS suicide-risk text (scored against R2, not generic Pebble). D4=2 — this is the canonical teacher→student distillation method and R2's pipeline is exactly a distillation. D7=1 — MentalRoBERTa-mirror student is in the BERT/RoBERTa family but not NeoBERT/~250M. D1/D5/D6 are genuine zeros: the paper is single-head softmax, no MTL balancing, no continuous/safety/ordinal head.
- **Closest on:** D4 (soft-target distillation — the method R2 currently *skips* by using hard argmax) and D2 (R2's crisis-text domain).

## Best point — Method to adopt
**Replace the hard-argmax CE term with a temperature-softened soft-target loss using the LLM teacher's class distribution** — recover the "dark knowledge" R2 currently throws away (W4). The single highest-leverage move because R2 already *has* the teacher (the labeling LLM) and a CE branch wired into the loss; only the target tensor and one loss term change.
- **How to apply to R2:** re-query the annotator LLM for a 4-way class probability vector (or build a soft target from its confidence) and feed it to the CE branch as a `T`-scaled KL soft-target loss instead of the current `F.cross_entropy(cls, y)` on hard labels.

## ▶ Apply to R2 (MANDATORY)
**Exact change** — file `kaggle/finetuning-message/r2-suicide-risk-dualhead/r2-suicide-risk-dualhead.py`, in `train_fold` (line 450):

Current CE term:
```python
+ cfg.w_ce * F.cross_entropy(cls, y, label_smoothing=cfg.label_smoothing)
```
Replace/augment with a **KD soft-target term** `L_kd` at temperature `T`:
```python
# soft_targets[b]: teacher 4-way prob vector from the LLM (logprobs or conf-derived), shape [B, n_classes]
log_p_student = F.log_softmax(cls / cfg.kd_T, dim=-1)
L_kd = F.kl_div(log_p_student, soft_targets, reduction="batchmean") * (cfg.kd_T ** 2)
loss = (cfg.w_coral * coral_loss(coral, y, cfg.n_classes)
        + cfg.w_ce * L_kd
        + cfg.w_focal * focal_loss(cls, y, alpha, cfg.focal_gamma))
```
- **Name the loss term:** `L_kd` (temperature-softened KD KL) takes the `w_ce` slot in the tri-objective `0.5*CORAL + 0.3*CE + 0.2*Focal`. Keep the `T²` scaling (Hinton) so it stays comparable to the CORAL/Focal magnitudes.
- **Data plumbing:** add a `soft_targets` field to the batch alongside `label`; obtain it by re-querying the annotator LLM with `logprobs`, OR construct a soft vector from the existing confidence (e.g. put `conf` on the argmax class and spread `(1-conf)` over ordinal-adjacent classes — this also injects ordinal structure).
- **Relation to CORAL's ordinal soft targets:** CORAL already turns the label into a set of P(rank>k) cumulative binary targets — an *ordinal* soft target derived from the hard label. The KD term is complementary: it adds the *teacher's empirical* class uncertainty (dark knowledge across non-adjacent classes) that CORAL's hand-built ordinal structure cannot express. A conf-spread soft target that respects ordinal adjacency is the cleanest bridge between the two.

## ▶ Kaggle experiment (MANDATORY)
- **Kernel:** clone `r2-suicide-risk-dualhead`; add config `kd_T` (sweep `{2, 4}`) and `soft_target_mode ∈ {hard, conf_spread, llm_logprobs}`.
- **Ablation rows** (same 5-fold within-dist CV + gold holdout as Run B):
  | Row | CE branch target | Expected signal |
  |-----|------------------|-----------------|
  | A (baseline = Run B) | hard argmax + label_smoothing 0.1 | gold macro-F1 0.3849, Behavior F1 0.183 |
  | B | `conf_spread` soft targets, `T=2` | better calibration (ECE↓), QWK↑, Behavior F1↑ (soft mass leaks into the confusable Behavior↔Ideation boundary) |
  | C | `llm_logprobs` soft targets, `T∈{2,4}` | strongest if teacher logprobs are well-ordered; main QWK/Behavior lift |
- **Expected signal:** primary = **QWK + calibration (ECE/Brier)** improvement and **Behavior gold F1** lift (the W1 bottleneck — Behavior is the most confusable class, exactly where dark knowledge helps most). Secondary = macro-F1.
- **Cost note:** Row B is **free** (reuses existing `conf`, no new LLM calls). Row C requires **one re-query of the annotator LLM with `logprobs`** over the ~10k training pool (one-off, hundreds of cheap calls — bounded, no training-time cost). GPU cost identical to Run B (one extra tensor in the batch).

## Caveats
- **Need teacher distributions for the strongest variant.** R2 stored only hard labels + a scalar `conf`; true KD (Row C) requires re-querying the LLM with `logprobs` to get a calibrated 4-way distribution. LLM class probabilities are often **mis-calibrated/over-confident** (the very reason Emo Pillars paper 04 chose hard-threshold BCE over a KL term) — so `conf_spread` (Row B) is the safer first cut and may already capture most of the gain.
- **Relation to label smoothing already in use.** Line 450 already applies `label_smoothing=0.1`, which is a *content-free* uniform soft target. KD's advantage is precisely that its soft target is **input-dependent** (dark knowledge), not uniform. When adding `L_kd`, **drop the label-smoothing** on that term to avoid double-smoothing.
- **Foundational vs already-covered.** This is the method PGKD (paper 13) and Emo Pillars (paper 04) build on — paper 13 does *error-targeted* LLM data generation, paper 04 does *hard-threshold BCE* on teacher labels. Neither uses temperature-softened soft targets; paper 47 is the citation for *why soft targets carry more signal than hard labels* and the exact `T`-scaled KL recipe. Cite it as the Family-B anchor, not as a competing method.
- **Single-task, no ordinal/MTL.** The paper says nothing about ordinal regression, CORAL, or multi-head balancing; the ordinal bridge above is R2's adaptation, not in the paper.
