# Paper 06 — Multi-Task Learning Using Uncertainty to Weigh Losses

> Enrichment set · Pillar 1 (MTL loss balancing). Analysis depth: abstract-level. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Kendall, Gal, Cipolla. CVPR 2018.
- **Link:** [arXiv:1705.07115](https://arxiv.org/abs/1705.07115) · open
- **Pebble pillar:** principled multi-task loss balancing (the canonical "Kendall" method named in Pebble's strategy).

## Summary
Jointly trains regression (depth) + classification (semantic/instance segmentation) heads on a shared CNN backbone, weighting each task loss by a learned homoscedastic-uncertainty term so noisier/harder tasks down-weight themselves automatically.

## Overlap with Pebble — 38% (peripheral)
`D1=2, D2=0, D3=0, D4=0, D5=2, D6=0, D7=0` → (3·2 + 2·2)/26 = 10/26 = **38%**
- **Closest on:** D5 (the canonical uncertainty-weighting method) and D1 (joint regression + classification on a shared trunk — the same heterogeneous-head structure Pebble has).

## Best point — Method to adopt
Replace hand-tuned λ with a learned per-task log-variance: `L = Σ exp(−sᵢ)·Lᵢ + sᵢ`, so MSE/CE/BCE units stop fighting each other.
- **How to apply to Pebble:** Add a learnable log-variance per head (continuous / emotion-softmax / safety-BCE); this is the first MTL arm to try, before GradNorm. **Floor or cap the safety head's weight** (or keep its asymmetric positive-class weight) — pure uncertainty weighting has no notion of a recall floor and could silently down-weight it below recall 0.95.

## Dataset
Method paper — no dataset to acquire (vision: NYUv2/CityScapes-style depth+segmentation).

## Caveats
Scored from abstract only; backbone is a CNN and the entire setup is computer-vision, so D2/D3/D4/D6/D7 are firmly 0. Value is purely the loss-balancing formulation. The "peripheral" band understates leverage: it's a method-only match on Pebble's single most relevant open question (D5).

## Deep research — full-PDF read (2026-06-10)

> Source-access note: the local PDF could not be rasterized in this environment (`pdftoppm` unavailable), so the body was read via the arXiv PDF text extraction ([arxiv.org/pdf/1705.07115](https://arxiv.org/pdf/1705.07115)), cross-checked against the CVPR 2018 camera-ready and independent reproductions. Equations, the log-variance trick, dataset/backbone, and the two headline IoU numbers (43.1 → 46.6) are corroborated across sources. The per-cell *instance* and *inverse-depth* error decimals quoted below come from a single extraction pass and are **marked approximate** — see Limitations.

### What the paper actually does (method, data, results — from the PDF, with exact numbers)

**Problem.** In multi-task learning a single shared network minimizes `L = Σᵢ wᵢ·Lᵢ`. The paper's opening claim (§1) is that final performance is *extremely* sensitive to the hand-chosen `wᵢ`, and that a grid search over weights is exponential in the number of tasks and prohibitively expensive — so they derive the weights instead of searching them.

**Core derivation (§3).** They treat each task's weight as the **homoscedastic (task-dependent, input-independent) observation noise** `σ` of a probabilistic output, then maximize the joint Gaussian/softmax likelihood.

- *Regression task* — Gaussian likelihood `p(y|f(x)) = N(f(x), σ²)` gives the negative-log-likelihood
  `L(W,σ) = (1/2σ²)·‖y − f(x)‖² + log σ`. The `1/2σ²` automatically down-weights a noisy task; the `+log σ` is a regularizer that prevents `σ→∞` (which would trivially zero the first term).
- *Two regression tasks* combine to `L(W,σ₁,σ₂) = (1/2σ₁²)L₁ + (1/2σ₂²)L₂ + log σ₁ + log σ₂` (Eq. ~7 in §3.2).
- *Classification task* — a **temperature-scaled softmax** `Softmax(f(x)/σ²)` (σ as a Boltzmann temperature). The combined regression+classification loss simplifies, using the approximation `(1/σ)·Σ exp(·) ≈ (Σ exp(·))^{1/σ²}`, to
  `L(W,σ₁,σ₂) ≈ (1/2σ₁²)L₁ + (1/σ₂²)L₂ + log σ₁ + log σ₂`
  — note the **classification term gets `1/σ²` (not `1/2σ²`)** and the regularizer is `log σ` for each task.
- **Numerical-stability trick (the load-bearing engineering detail):** in practice they do **not** predict `σ`; the network predicts `s := log σ²`. Then `1/σ² = exp(−s)` and `log σ = s/2`, so a regression task's term becomes `exp(−s)·L + s/2`. This (a) keeps `σ²` strictly positive without a constraint, (b) avoids division-by-zero when a weight collapses, and (c) is numerically stable because it only ever exponentiates a learned scalar. `s` is just an extra learnable parameter per task — no architecture change.

**Data + backbone (§5).** Single dataset: **NYUv2** indoor scenes — **40 semantic classes, 1449 images, 464 indoor scenes, 640×480**. Backbone: a DeepLabV3-style fully-convolutional encoder (ResNet-101 + ASPP), with three heads sharing the encoder: (1) **semantic segmentation** (40-way per-pixel classification), (2) **instance segmentation** cast as per-pixel **regression** to the instance centroid vector, (3) **monocular inverse-depth regression**. So the experiment is exactly a *categorical + multiple continuous* head mix on one shared trunk — structurally the same shape as Pebble.

**Headline results (§5, NYUv2 ablation — verified numbers in bold):**
- Equal/unweighted sum of losses → **segmentation IoU 43.1%**.
- Learned uncertainty weighting → **segmentation IoU 46.6%** — a **+3.5 IoU** gain over equal weighting, *and* the central claim that the 3-task uncertainty-weighted model **beats every single-task network trained alone** (the multi-task model is better than the sum of its parts, not just cheaper).
- Approximate-grid-search "optimal" weights land *close to* the learned-uncertainty result on segmentation, but the learned method needs **no search** and jointly optimizes all three metrics.
- Instance-centroid error and inverse-depth error both improve under uncertainty weighting vs equal weights (approx. instance ≈0.55 vs ≈0.60, inverse-depth ≈0.51 vs ≈0.61 — *decimals approximate, see Limitations*).

**Robustness observation (§5).** The authors report the learned `σ` values converge to similar relative weights **regardless of their initialization**, i.e. the method is insensitive to how you initialize the log-variances — you don't trade one hyperparameter (λ) for another fragile one.

### Parts directly useful for Pebble (specific: equations, hyperparameters, splits, thresholds)

1. **The exact per-head loss to drop into the multi-task objective.** For Pebble's three heads, replace the static `λ_emotion·CE + λ_sev·MSE + λ_safety·BCE` with learned `s_k = log σ_k²`:
   - emotion (classification): `exp(−s_emo)·CE + s_emo/2`
   - severity/energy (regression): `exp(−s_sev)·MSE + s_sev/2`
   - safety (binary classification): `exp(−s_safety)·BCE + s_safety/2`
   Three extra scalar parameters total, optimized by the same optimizer.
2. **The `s := log σ²` parameterization**, not `σ` — this is the single most reusable engineering detail and the thing most reimplementations get wrong (predicting `σ` directly leads to NaNs when a task collapses).
3. **The classification-vs-regression asymmetry** (`1/σ²` for the temperature-scaled classification term vs `1/2σ²` for regression). LibMTL's `UW` already encodes this; Pebble should not hand-roll it.
4. **"No grid search needed" + "robust to init"** — the justification Pebble's write-up needs for *why* it uses a principled weighter over tuned λ as its default arm.

### How each part helps Pebble succeed (concrete actions: which head/loss/experiment in Pebble it changes, expected payoff)

- **MTL experiment (Pebble's #1 novelty).** This *is* the canonical "Kendall arm" in the planned static-λ vs Kendall vs GradNorm vs PCGrad vs Nash-MTL comparison. Action: enable `weighting=UW` in LibMTL over the NeoBERT `[CLS]` trunk; expected payoff mirrors the paper — the emotion-CE, severity-MSE, and safety-BCE losses, which live on wildly different unit scales, stop fighting, and the joint model should match or beat per-head-tuned λ **without the λ sweep**, exactly the cost the paper eliminates.
- **Severity/energy regression head.** The Gaussian-likelihood term is literally the MSE head with a learned `1/2σ²` scale — this is the lowest-friction win: the noisier of severity vs energy auto-down-weights itself instead of needing a hand-set ratio.
- **Safety head — the critical divergence.** Kendall's method has **no notion of a recall floor**; a high-noise safety head (silver crisis labels are noisy) would *raise* its `σ`, i.e. **down-weight itself**, the opposite of what Pebble needs. Action: either (a) **floor `exp(−s_safety)`** (cap the safety log-variance) so the safety weight cannot fall below a minimum, or (b) keep an asymmetric positive-class weight inside the BCE, or (c) exempt the safety head from UW entirely and let UW balance only emotion+severity+energy. This caveat (already in the short analysis) is *confirmed and sharpened* by the full derivation: the `+log σ` regularizer actively pushes weights toward the noise level, which for a noisy-label safety task is exactly the wrong direction.
- **Write-up framing.** Cite the +3.5 IoU / "beats single-task" result as evidence that principled weighting is not just a convenience but can improve the constrained heads — then show whether that holds *under* Pebble's recall floor (the open question the vision paper never faced).

### Child mental-health lens (Pebble serves children: does this transfer to children's language & safety needs? risks, mitigations, ethics caveats)

- **Domain transfer is purely mechanical.** The method is a loss-weighting rule with zero domain assumptions — it transfers from vision pixels to children's text tokens unchanged. Nothing about it knows or cares that the input is a child's message; it only sees loss magnitudes.
- **The real child-safety risk is the homoscedastic assumption.** Kendall assumes one *global* noise scalar per task. Children's affect/crisis language is **higher-variance and more heteroscedastic** than adults' (developmental range, atypical phrasing, indirect crisis signals, sarcasm/play). A single learned `σ_safety` will key off the *average* noisiness of the silver safety labels — and because child-crisis examples are rarer and noisier, the method will tend to **inflate `σ_safety` and quietly down-weight precisely the head that must not be down-weighted.** Mitigation: the safety-weight floor above is not optional for a child product — it is a safety control.
- **Calibration ethics.** The learned `σ` is *not* a calibrated confidence and must never be surfaced to a child or caregiver as "how sure the model is." It is a training-time loss-balancing scalar only.
- **Heteroscedastic alternative.** The companion idea (input-dependent, *aleatoric* uncertainty from Kendall & Gal's "What Uncertainties Do We Need", arXiv:1703.04977) would let the model say *this particular message is ambiguous* — closer to what a child-safety system actually wants — but that is a different, heavier mechanism and out of scope for the first MTL arm.

### Limitations & open questions for Pebble

- **Unverified decimals.** The instance-centroid and inverse-depth error cell values (≈0.55 / ≈0.51 etc.) come from one PDF-text extraction and could not be re-confirmed against the camera-ready table in this environment; treat as directional. The two segmentation IoU numbers (43.1 → 46.6) and all equations *are* corroborated.
- **Single dataset, single domain.** All results are NYUv2 vision; **no NLP, no text encoder, no class-imbalanced safety task, no recall constraint** appears anywhere in the paper. The +3.5 IoU gain is not evidence the method helps Pebble's *safety* head — only that it removes the λ search.
- **Homoscedastic only.** One scalar per task; cannot express per-example uncertainty (the heteroscedastic case is a different paper).
- **Open question for Pebble's experiment:** does uncertainty weighting still satisfy **safety recall ≥ 0.95** once the floor is applied — and does the floor erase the "no tuning" benefit by reintroducing a hyperparameter (the floor value) that itself needs tuning? That trade is exactly what Pebble's static-vs-principled ablation must measure; the paper offers no guidance because it never operates under a hard per-task constraint.
