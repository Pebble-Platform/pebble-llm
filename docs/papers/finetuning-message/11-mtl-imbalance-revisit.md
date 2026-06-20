# Paper 11 — Revisit the Imbalance Optimization in Multi-task Learning

> Enrichment set · Pillar 1 (MTL loss balancing). Analysis depth: abstract + HTML. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** 2025 (experimental analysis).
- **Link:** [arXiv:2509.23915](https://arxiv.org/abs/2509.23915) · open
- **Pebble pillar:** principled MTL loss balancing — the **null hypothesis** Pebble's experiment must rule out.

## Summary
Benchmarks the exact methods Pebble is weighing (Kendall uncertainty, GradNorm, PCGrad, MGDA, CAGrad, Nash-MTL, FAMO) head-to-head on vision foundation models. Headline finding: simply scaling each task loss by its gradient norm matches an expensive grid search, and elaborate gradient-surgery methods give inconsistent gains.

## Overlap with Pebble — 27% (peripheral)
`D1=1, D2=0, D3=0, D4=0, D5=2, D6=0, D7=0` → (3·1 + 2·2)/26 = 7/26 = **27%**
- **Closest on:** D5 — it benchmarks the precise methods Pebble is choosing among.

## Best point — Design lesson
Gradient-norm scaling ≈ grid search; heavier methods (PCGrad/Nash-MTL/CAGrad) are inconsistent.
- **How to apply to Pebble:** Start with a cheap GradNorm-style gradient-norm rescale as the baseline balancer; treat PCGrad/Nash-MTL as something to *beat*, not the default — but note the asymmetry below.

## Dataset
Method/analysis paper — no dataset to acquire (NYUv2, Pascal, CelebA, Omnidata, Replica).

## Caveats
Pure computer-vision study — zero NLP/encoder/mental-health content, so transfer is by analogy. Crucially its tasks are homogeneous and **unconstrained**: it never tests a hard recall-floored head, so "gradient-norm scaling ≈ grid search" is **untested under Pebble's safety-recall ≥ 0.95 regime** — which is precisely Pebble's novel territory. Exact scaling formula not legible in the fetched PDF.

## Deep research — full-PDF read (2026-06-10)

> Read note: the local PDF (`docs/papers/pdfs/11-mtl-imbalance-revisit.pdf`) could not be image-rendered in this environment (no `pdftoppm`), so the deep read was done against the **arXiv v1 full-text HTML** of the *same* paper (arXiv:2509.23915v1, two passes). All numbers below are quoted from that full text; the prior short analysis above was abstract+HTML only and the earlier "scaling formula not legible" caveat is now resolved (formula given in §V-F / Eq. for AvgNorm).

### What the paper actually does (method, data, results — from the PDF, with exact numbers)
**Thesis.** MTL underperforms single-task (STL) baselines because of *unbalanced optimization* (task interference). The paper runs a large controlled benchmark and argues the field has over-invested in elaborate multi-task optimizers (MTOs) when a tuned static baseline — and one cheap gradient-norm rule — already captures most of the gain.

**Methods benchmarked (the full menu Pebble is choosing from).** Three families:
- *Loss-weighting:* Uniform, Uncertainty Weighting (UW / Kendall), DWA, FAMO, DTP, Auto-λ, GradNorm, MGDA, Nash-MTL, RLW (random loss weighting), and a **Grid Search** static-λ baseline.
- *Gradient-update / surgery:* PCGrad, GradDrop, CAGrad, RotoGrad, FairGrad.
- *Distillation:* URL.

**Data / tasks (dense-prediction vision).** NYUD-v2 (795 train / 654 test; 4 tasks: semantic seg, depth, surface normals, edges); PASCAL-Context (4,998 train / 5,105 test; 5 tasks: semantic seg, human-parts, normals, saliency, edges); Replica synthetic (56,783 / 23,725 / 13,889; seg, depth, normals). Backbones: ResNet-18/50, HRNet-18, ViT-T/16, ViT-B; MTL architectures MTAN, MTI-Net, InvPT; VFM inits ImageNet-1K/21K/22K, CLIP, SAM, DINO, DINO-v2. Metric throughout is **Δm%** — average per-task % change vs the single-task model (0% = ties STL, positive = beats it).

**Headline numbers (Δm%, higher better):**
- NYUD-v2 / ResNet-18: Uniform **−2.93**, Grid Search **−0.15**, best surgery method CAGrad **−0.34**, best MTO overall FairGrad **+0.59**; their proposed **AvgNorm +0.37** (beats grid search, no search needed). With MTAN: Grid Search **+1.29** vs AvgNorm **+1.33**.
- PASCAL-Context / ResNet-18: Uniform **−4.04**, Grid Search **−2.64**, AvgNorm **−2.38**, best MTO URL **−1.32**; with MTAN: Grid Search **−1.22** vs AvgNorm **−0.43** (their best overall).
- ResNet-50 / NYUD-v2: Grid Search **+0.60**, best MTO URL **+1.91**.
- **Inconsistency evidence:** MGDA collapses to **−7.19%** on PASCAL-Context — i.e. a "principled" method can be far *worse* than a tuned static λ.

**The proposed rule (AvgNorm).** Per-iteration weight `wᵢ = S / ‖∇_θ ℒᵢ‖`, where `S = ‖Σᵢ ∇_θ ℒᵢ‖` is the aggregate gradient norm, and the gradients used are those of the **last layer of the shared backbone** (cheap — no full backward per task). This rescales every task's gradient to a common norm each step. Claimed to be "automatic and much [more] efficient" than grid search, though the paper gives **no wall-clock or run-count comparison** (a stated gap).

**Robustness probes (§V-E, Replica).** Label noise: clean MTL **−3.21%** → noisy MTL **−19.69%** Δm (noise hurts badly, but the authors say it degrades STL too and is *not* clearly an imbalance effect). Data size: full data **−3.21%** → quarter-data **−7.03%** ("less samples can lead to severer imbalanced problem"; more data is *not* the fix).

**Stated observations (§V).** V-A: Uniform MTL is reliably imbalanced; grid search alone lifts vanilla MTL to ≈/> STL. V-B: MTOs are "brittle and inconsistent across datasets"; few beat grid search everywhere; grid search "remains competitive." V-C: dedicated MTL architectures still trail their own STL models and still lean on grid-searched weights. V-D: VFM initialization does not solve imbalance. V-E: noise/scarcity worsen results but aren't pure imbalance. V-F: performance correlates with **per-task gradient norm**, *not* with gradient-conflict angle — motivating AvgNorm.

**Conclusion.** "Understanding and controlling gradient dynamics is a more direct path to stable MTL than developing increasingly complex methods." Limitation acknowledged by the authors: no random-seed/repeat reporting, no cost accounting, AvgNorm still marginally below grid search in several settings.

### Parts directly useful for Pebble (specific: which experimental controls/protocols make the static-vs-principled comparison fair)
The transferable value is **not** the vision results — it is the **measurement protocol** that makes "static λ vs principled MTL" an honest test rather than a rigged one:
1. **A STL-normalized aggregate metric (Δm%).** Every method is scored as the *mean per-task delta against its own single-task model*, so a balancer can't win just by inflating the easy task. Pebble has no native Δm but the construction is exactly portable.
2. **A *seriously tuned* static baseline, not a token one.** Their grid search (e.g. edge-task weight up to 50, §Table VI) is the thing fancy methods must beat. The paper's whole credibility rests on the static arm being strong — V-A/V-B show it ties or beats most MTOs. This is the methodological bar Pebble's null hypothesis stands on.
3. **Same backbone, same schedule, same eval across arms** (ResNet-18 100ep / PASCAL 60ep / HRNet-ViT 40k iters), so the *only* moving part is the weighting rule. Pebble must mirror this: identical NeoBERT init, identical freeze→unfreeze schedule, identical eval set per arm.
4. **Gradient-norm diagnostic (V-F).** They log per-task last-shared-layer gradient norms and correlate them with Δm. This diagnostic is what turns "method X is better" into "*why*" — and it is the cheapest possible balancer to implement.
5. **Stress axes (noise §V-E, data scarcity).** Both directly mirror Pebble's reality: Gemini silver labels = label noise; C-SSRS 500-user = scarcity.

### How each part helps Pebble succeed (concrete actions: how to design Pebble's ablation so the null hypothesis is properly tested)
- **Build the strong static arm first, and tune it hard.** The paper's central lesson is that a *well-tuned* static λ ties most MTOs. Pebble's ablation is only valid if the static-λ arm is genuinely grid/Bayesian-searched (sweep emotion:severity:safety weights), *not* set to 1:1:1. If a principled method only beats a lazy static baseline, the result is worthless. **Action:** make "tuned static λ" the headline baseline and report how it was searched. **Payoff:** a credible null hypothesis; reviewers can't dismiss the comparison.
- **Adopt AvgNorm (`wᵢ = ‖Σ∇‖/‖∇ᵢ‖` on the shared `[CLS]`/last-shared-layer grads) as the *cheap* principled arm.** It is essentially GradNorm without the learned-rate machinery and costs one extra norm per task per step. **Action:** add it as the first non-static arm in the LibMTL sweep, between static-λ and GradNorm/PCGrad/Nash-MTL. **Payoff:** if AvgNorm already matches tuned static λ on Pebble's heads, you've reproduced the paper's finding cheaply and can stop — or, if it *fails under the recall floor*, you've found Pebble's positive contribution.
- **Adopt Δm-style STL-normalized reporting.** Train three single-task NeoBERT heads (emotion-only, severity-only, safety-only), then report each MTL arm as mean delta vs those STL baselines — plus the safety head's recall as a *separate, non-averaged* number. **Action:** add a `delta_m` reporter; never let the safety head be averaged into Δm. **Payoff:** prevents the classic trap where an MTL model "improves" by trading away crisis recall.
- **Log the gradient-norm diagnostic (V-F).** Track per-head last-layer gradient norms each step. **Payoff:** if the safety BCE gradient is being swamped by the MSE/CE heads (small norm), AvgNorm's `1/‖∇ᵢ‖` boost is exactly the corrective — but watch that it doesn't over-amplify a noisy crisis gradient.
- **Run the two stress axes the paper validates.** (a) **Noise:** compare Gemini-silver vs the human-labelled calibration slice — V-E says noise can swing Δm from −3.2 to −19.7, so silver-label quality may dominate any MTL-weighting effect. (b) **Scarcity:** the C-SSRS severity head is the small/imbalanced task; V-E predicts it is where imbalance bites hardest, so it is the head most likely to *need* a principled balancer. **Payoff:** tells you whether to spend effort on label quality or on the weighting rule.

### Child mental-health lens (Pebble serves children: risks, mitigations, ethics caveats)
- **The single most important divergence: this paper has *no asymmetric-cost task* (confirmed — "None reported"; all tasks weighted equally).** Δm rewards average improvement, so a method that wins on Δm can quietly *sacrifice the worst task*. For Pebble that worst task is the **crisis/suicide-risk head**, and trading its recall for emotion/severity gains is a child-safety failure, not a metric blip. **Mitigation:** the safety head must sit *outside* any Δm averaging and *outside* any norm-equalization that could shrink its weight — enforce a hard floor so recall ≥ 0.95 is a constraint, never a term to be balanced. AvgNorm's `1/‖∇ᵢ‖` rule can in principle *down*-weight a confident, low-loss crisis head exactly when it's doing well — the opposite of what a child-safety system wants. **Mitigation:** exempt/clamp the safety head's weight (floor it) before applying any gradient-norm rule.
- **Noise lesson lands harder for children.** V-E shows label noise can dominate (−3.2 → −19.7 Δm). Gemini-as-teacher on *child* crisis language is exactly where silver labels are least trustworthy (kids express distress idiosyncratically). **Mitigation:** human-verify the safety-head slice; never let a balancer paper over teacher false-negatives on crisis examples.
- **"More data won't fix it" (V-E).** Discourages the tempting shortcut of scraping more adolescent mental-health text to fix severity imbalance — scaling data is not the lever; the safety constraint and label quality are. Ethically this steers effort toward verified, consented data over volume.

### Limitations & open questions for Pebble
- **Domain gap is total.** Dense-prediction vision tasks (seg/depth/normals) vs Pebble's classification+regression+constrained-binary heads. Whether "gradient-norm scaling ≈ grid search" survives the jump to a frozen-then-unfrozen text encoder is **unestablished** — this is the gap Pebble's experiment fills.
- **No constrained-task experiment exists in the paper** — so it offers *zero* evidence on behavior under a recall floor. The paper's headline result is literally untested in Pebble's regime; treat it as a hypothesis to falsify, not a settled fact.
- **No reproducibility hygiene to copy here** — the authors themselves flag missing seeds/repeats and no cost accounting. Pebble should do *better*: report seeds, variance, and the actual cost of each MTL arm (the paper's efficiency claim for AvgNorm is asserted, not measured).
- **AvgNorm is per-iteration and noise-sensitive.** With small, noisy silver-labelled batches the `1/‖∇ᵢ‖` term can spike; Pebble may need EMA-smoothing of the norms (not discussed in the paper).
- **Open question for Pebble's contribution:** does *any* principled balancer beat a tuned static λ *while holding safety recall ≥ 0.95*? The paper says "no, not in unconstrained vision." If Pebble shows "yes, under the recall floor" — or even "static λ can't hold the floor but GradNorm/AvgNorm can" — that is precisely the novel, publishable result, and this paper is the null hypothesis it rules out.
