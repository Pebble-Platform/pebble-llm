# Paper 50 — Class-Balanced Loss Based on Effective Number of Samples

> Family C (imbalance) · Analysis depth: abstract + CVPR open-access verification. Compiled 2026-06-25.

## Bibliographic info
- **Authors / Year / Venue:** Yin Cui, Menglin Jia, Tsung-Yi Lin, Yang Song, Serge Belongie — 2019 — **IEEE/CVF CVPR 2019**, Long Beach, pp. 9268–9277 (arXiv:1901.05555).
- **Link:** [arXiv:1901.05555](https://arxiv.org/abs/1901.05555) · [CVPR open access](https://openaccess.thecvf.com/content_CVPR_2019/html/Cui_Class-Balanced_Loss_Based_on_Effective_Number_of_Samples_CVPR_2019_paper.html) · open — **VERIFIED**
- **R2 pillar:** class imbalance — a principled replacement for R2's inverse-frequency `alpha`/sampler weighting that directly targets the Behavior-class collapse.

## Summary
Argues that as a class accumulates samples, each new example overlaps with existing ones, so the *marginal* information saturates — raw count `n` over-states a head class's true coverage. It defines the **effective number** `E_n = (1 − β^n)/(1 − β)` (β ∈ [0,1), a hyperparameter governing how fast the marginal value decays) and re-weights each class by `w_c ∝ (1 − β)/(1 − β^{n_c})` instead of the usual `1/n_c`. This is a smooth interpolation: β→0 gives no re-weighting (all weights equal); β→1 collapses to plain inverse-frequency `1/n`. The class-balanced factor multiplies any base loss (softmax CE, sigmoid CE, or **focal loss**), and the paper shows consistent gains over inverse-frequency on long-tailed CIFAR/ImageNet/iNaturalist. Tested β grid in the paper: {0.9, 0.99, 0.999, 0.9999}.

## Overlap with Pebble/R2 — 0%
`D1=0, D2=0, D3=0, D4=0, D5=0, D6=0, D7=0` → (0)/26 = **0% (peripheral)**
- **Closest on:** none of the 7 rubric dimensions — it is a vision long-tailed-classification paper with no MTL heads (D1), no mental-health domain (D2), no emotion corpora (D3), no LLM distillation (D4), no task-level MTL balancing (D5, this is *class*-level not *task*-level), no recall constraint (D6), and a CNN/ResNet backbone (D7).
- **Honest framing:** the rubric scores *profile* overlap (domain + architecture + MTL), and on that axis this paper is genuinely peripheral. Its value to R2 is orthogonal to the rubric: it is a **drop-in, mechanism-level technique** that maps exactly onto two lines R2 already has. Low overlap %, high method-transfer leverage for the one bottleneck (Behavior) R2 cares about.

## Best point — Method to adopt (principled alpha)
Replace inverse-frequency class weights with **effective-number** weights `w_c = (1 − β)/(1 − β^{n_c})`, leaving the focal-loss machinery untouched. With R2 counts `[3992, 3612, 634, 1442]`, inverse-freq gives Behavior ~6.3× the weight of the largest head; effective-number with β=0.999 *softens* that toward the true marginal-coverage ratio (β acts as a dial between "flat" and "1/n"), which is exactly the over/under-correction knob R2 is currently missing.
- **How to apply to Pebble:** swap the `alpha` (and optionally sampler) formula in `train_fold` for the effective-number form with β as a sweepable hyperparameter; one-line change, no architecture impact.

## ▶ Apply to R2 (MANDATORY)
File: `kaggle/finetuning-message/r2-suicide-risk-dualhead/r2-suicide-risk-dualhead.py`, function `train_fold`.

**1. `alpha` (focal weight) — line 434–435.** Currently:
```python
alpha = torch.tensor(counts.sum() / (cfg.n_classes * np.maximum(counts, 1)),
                     dtype=torch.float32, device=DEVICE)
```
Replace with effective-number weights (normalize so the mean weight = 1, matching the current scale that `focal_loss` at line 362–368 expects, `a = alpha[y]`):
```python
beta = float(os.environ.get("R2_CB_BETA", "0.999"))
eff_num = (1.0 - np.power(beta, np.maximum(counts, 1))) / (1.0 - beta)  # E_n per class
cb = (1.0 - beta) / np.maximum(eff_num, 1e-8)                          # w_c ∝ 1/E_n
cb = cb / cb.mean()                                                    # mean-1 normalize (keep focal scale)
alpha = torch.tensor(cb, dtype=torch.float32, device=DEVICE)
```
`counts` is already computed at line 424 — no other change needed; `focal_gamma` (line 89) and the loss mix at line 451 stay as-is.

**2. (Optional, behind the same β) sampler weights — line 427.** Currently inverse-freq:
```python
w = (counts.sum() / np.maximum(counts, 1))[np.asarray(tr_lab)]
```
Effective-number variant (keep gated by `cfg.balance`):
```python
w = (cb / cb.sum() * len(counts))[np.asarray(tr_lab)]   # reuse cb from above
```
Keep arms separable: the cleanest ablation changes **only `alpha`** first (sampler held at current inverse-freq), so the β effect is attributable. Touch the sampler only as a second arm.

## ▶ Kaggle experiment (MANDATORY)
**Goal:** does principled effective-number re-weighting move the Behavior bottleneck past inverse-freq's 0.183 gold F1?

**Setup:** Run B + balance (the current best config: `R2_GOLD_HOLDOUT=1 R2_BALANCE=1 R2_EPOCHS=10`), gold-holdout eval on clinical CSSRS-500, 5-fold. Vary only `alpha`:

| Arm | `alpha` rule | β | Expected signal |
|-----|--------------|---|-----------------|
| A0 (baseline) | inverse-freq (current) | — | gold macro-F1 0.3849, Behavior 0.183 (reproduce) |
| A1 | effective-number | 0.99 | mild softening vs A0 |
| A2 | effective-number | 0.999 | most likely best (paper's CIFAR sweet spot) |
| A3 | effective-number | 0.9999 | ≈ inverse-freq (sanity: should ≈ A0) |

Report per-arm: **gold macro-F1, per-class gold F1 (esp. Behavior + Attempt), QWK, MAE.** Add one ablation row to `docs/tasks/r2-beat-paper-dual-report.md`.

**Expected signal — HONEST:** likely a **small** bump (Behavior +0.01–0.03 F1 at best), possibly noise on a ~100-row gold set. The R2 report already concludes Behavior collapse is now **label quality (W4), not sampling** — so re-weighting attacks a lever that is largely exhausted. The realistic win is a *cleaner, more defensible* alpha for the IEEE write-up (a principled β-curve beats an ad-hoc inverse-freq line) and a possible Attempt-class side gain, not a bottleneck fix. A3≈A0 is the key sanity check; if A2 ≫ A0 it would be surprising and worth scrutiny.

**Cost:** ~4 arms × existing 5-fold Run-B runtime; β is a single env var (`R2_CB_BETA`) so all arms share one kernel. Cheap (no new data, no architecture change).

## Caveats
- **Re-weighting ≠ fixing label noise.** R2's W4 (single-LLM Behavior labels) and W1 (collapse traced to label quality) put a hard ceiling on what *any* class-balancer can recover; this paper changes *how much* a class is weighted, never *whether* its labels are correct. Set expectations to "marginal + cleaner story," not "bottleneck solved."
- **β sensitivity.** With β→1 the method *is* inverse-freq (so no free lunch over the current baseline at the high end); with β→0 it is uniform. The useful regime (0.99–0.999) must be swept, not assumed — and on a ~100-example gold set the differences may be within fold variance, so report fold std/CIs.
- **Domain transfer is by analogy.** All paper evidence is vision (CIFAR/ImageNet/iNaturalist); no NLP/encoder/crisis validation exists. The formula is domain-agnostic, but the *magnitude* of gain seen on iNaturalist will not carry over to a 4-class, 7k-example, label-noisy R2 setting.
- **Verification status:** title/authors/venue (CVPR 2019, pp. 9268–9277) and links VERIFIED via CVPR open access + arXiv. Exact per-β numeric tables and the focal-combination equation were not legible in the fetched abstract (only the `E_n` formula and β grid were confirmed); cite the open-access PDF before quoting specific numbers.
