# Paper 08 — Gradient Surgery for Multi-Task Learning (PCGrad)

> Enrichment set · Pillar 1 (MTL loss balancing). Analysis depth: abstract-level. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Yu, Kumar, Gupta, Levine, Hausman, Finn. NeurIPS 2020.
- **Link:** [arXiv:2001.06782](https://arxiv.org/abs/2001.06782) · open
- **Pebble pillar:** principled multi-task loss balancing (named in Pebble's rubric).

## Summary
When two task gradients conflict (negative cosine similarity), projects one onto the normal plane of the other before the update — a model-agnostic, loss-weight-free way to stop tasks fighting. Demonstrated on vision and RL.

## Overlap with Pebble — 27% (peripheral)
`D1=1, D2=0, D3=0, D4=0, D5=2, D6=0, D7=0` → (3·1 + 2·2)/26 = 7/26 = **27%**
- **Closest on:** D5 (PCGrad is named in the rubric and the survey's recommended angle #1). Faint D1 (generic multi-head support).

## Best point — Method to adopt
Targets gradient *direction* conflict, complementary to magnitude schemes (Kendall/GradNorm target *scale*).
- **How to apply to Pebble:** Add PCGrad as a third arm in the balancing comparison. Especially relevant because Pebble's heads are heterogeneous (MSE vs CE vs high-weight BCE) where direction conflict is the likely failure mode. **Exempt/protect the crisis head from projection** so it can't erode the recall ≥ 0.95 floor.

## Dataset
Method paper — no dataset to acquire (vision/RL).

## Caveats
Abstract-only. No NLP, no encoder LM, no heterogeneous categorical+continuous+safety setup, no recall constraint — transfer is by analogy. A method/citation source, not a results baseline.

## Deep research — full-PDF read (2026-06-10)

> Read against the full text (ar5iv HTML of arXiv:2001.06782; the local `pdfs/08-pcgrad.pdf` could not be
> rasterized in-session — no poppler/`pdftoppm` — so numbers below are grounded in the arXiv full text, not
> the binary PDF). Section/Theorem/Algorithm references are to the published NeurIPS 2020 paper. Where a
> figure-only number is approximate in the source, it is marked "~".

### What the paper actually does (method, data, results — from the PDF, with exact numbers)

**The thesis ("tragic triad").** The paper argues multi-task optimization on a *shared* parameter set goes wrong
only when **three conditions co-occur**: (a) **conflicting gradients** — two task gradients point in opposing
directions, `cos φ_ij < 0`; (b) **high gradient-magnitude difference** — one task's gradient dominates the
other; and (c) **high curvature** in the shared optimization landscape. Under (b)+(c), a conflicting update
(a) over-/under-estimates the multi-task improvement and net-harms the dominated task ("negative transfer").

**Definitions (Sec. 3).**
- Conflicting gradients: `cos φ_ij = (g_i·g_j)/(‖g_i‖‖g_j‖) < 0`.
- **Gradient Magnitude Similarity** `Φ(g_i,g_j) = 2‖g_i‖₂‖g_j‖₂ / (‖g_i‖₂² + ‖g_j‖₂²)` — equals **1** when the
  two gradients are equal-norm, **→0** as they diverge. This is the formal handle on the "one head dominates"
  failure mode.
- **Multi-task curvature** `H(L;θ,θ′) = ∫₀¹ ∇L(θ)ᵀ ∇²L(θ+a(θ′−θ)) ∇L(θ) da`; "high curvature" means `H > C`.

**PCGrad (Algorithm 1).** For each task `i`, for each *other* task `j` drawn **in random order** from the batch:
if `g_i^PC · g_j < 0`, replace `g_i^PC ← g_i^PC − (g_i^PC·g_j / ‖g_j‖²) · g_j` — i.e. **project `g_i` onto the
normal plane of `g_j`**, removing only the conflicting component. The final update is the **sum** of the
de-conflicted per-task gradients, `Δθ = Σ_i g_i^PC`. Crucially: **no extra hyperparameters** — "PCGrad inherits
the hyperparameters of the respective baseline method in all experiments." It is an operation on gradients, not
a loss-weighting scheme.

**Theory (Theorem 1).** Assuming `L₁,L₂` convex and differentiable and `∇L` L-Lipschitz (`L>0`), the PCGrad
update with step size `t ≤ 1/L` converges to **either** a point where `cos(φ₁₂) = −1` (gradients exactly
anti-parallel — a degenerate stall) **or** the optimum `L(θ*)`. The 2-D two-task analysis shows PCGrad's basin
of attraction is *strictly larger* than vanilla gradient descent precisely when magnitudes differ and curvature
is high — i.e. it provably helps exactly in the "tragic triad" regime and is otherwise (near) a no-op.

**Empirical results (exact, where reported).**
- **CelebA** (40-attribute classification, treated as 40 tasks): average classification error **8.95 (Sener &
  Koltun MGDA-UB) → 8.69 (PCGrad)**.
- **NYUv2** (3 dense tasks — semantic seg / depth / surface-normal), MTAN backbone, PCGrad vs DWA weighting:
  mIoU **17.15 → 20.17**, Pixel-Acc **54.97 → 56.65**, depth Abs-Err **0.5956 → 0.5904**, Rel-Err
  **0.2569 → 0.2467**, normal Mean-Angle **31.60 → 30.01°**, Median **25.46 → 24.83°** — PCGrad improves *every*
  metric of *every* one of the three heterogeneous tasks simultaneously.
- **CIFAR-100** multi-task (20 tasks): Independent **67.7% → PCGrad 71% → Routing+PCGrad 77.5%** — PCGrad
  **stacks on top of** an architectural MTL method.
- **Multi-task RL (Meta-World)**: PCGrad+SAC **solves all 10** MT10 tasks and **~70%** of MT50; reaches the
  same performance using **~2M (MT10) / ~15M (MT50) fewer environment samples** than independent training.
- CityScapes (2-task) and MultiMNIST results are in the appendices (App. E / J.4) and not quoted in the main
  text; same qualitative finding (PCGrad ≥ baseline on each task).

### Parts directly useful for Pebble (specific: equations, hyperparameters, splits, thresholds)

1. **The projection update itself** — `g_i ← g_i − (g_i·g_j/‖g_j‖²)·g_j` when `g_i·g_j < 0`, applied at the
   shared `[CLS]`/encoder parameters where Pebble's three heads (emotion-CE, severity/energy-MSE, crisis-BCE)
   meet. This is the exact line LibMTL implements as `weighting=PCGrad`; no tuning knob to set.
2. **`Φ` magnitude-similarity as a diagnostic** — Pebble can log `Φ(g_crisis, g_emotion)` and
   `Φ(g_crisis, g_severity)` per step *without adopting PCGrad*, to **measure** whether the high-weight BCE
   crisis gradient is being dominated by the CE/MSE heads. This turns the "is there actually a conflict?" null
   hypothesis (Pillar 1 / arXiv:2509.23915) into a measured quantity, not an assumption.
3. **The "tragic triad" co-occurrence claim** is the precise precondition Pebble should test: PCGrad only helps
   when conflict + magnitude-imbalance + curvature all hold. If Pebble's per-step `cos φ` between heads is
   rarely negative, the theory predicts PCGrad ≈ no-op and static-λ will match it — a cheap pre-check before
   committing to the full ablation.
4. **Composability** (CIFAR-100 67.7→71→77.5) — PCGrad is *orthogonal* to magnitude schemes; Pebble can run
   **Kendall-uncertainty (scale) + PCGrad (direction)** together, not as either/or.
5. **No new hyperparameters** — for Pebble's staged freeze→unfreeze schedule this means PCGrad can be toggled on
   only in the unfreeze stage (when the shared encoder actually moves) with zero re-tuning of LR/λ.

### How each part helps Pebble succeed (concrete actions: which head/loss/experiment it changes, expected payoff)

- **Crisis-head protection (the highest-leverage action).** In vanilla PCGrad every gradient is projected,
  *including* the safety gradient — which can erode the very signal Pebble must protect to keep recall ≥ 0.95.
  **Action:** modify the ablation so the crisis-BCE gradient is the **fixed reference** that is *never*
  projected away, while the emotion/severity gradients are projected off *it*. Concretely, only run the inner
  loop with `j = crisis` and skip `i = crisis`. Payoff: de-conflicts the auxiliary heads from the safety head
  while structurally guaranteeing PCGrad cannot lower the crisis gradient's contribution → recall floor stays
  defensible. *(This is a deliberate asymmetric variant of Algorithm 1, justified by the recall constraint;
  document it as a Pebble modification, not stock PCGrad.)*
- **Diagnostic logging first, method second.** Add `cos φ` and `Φ` logging between each head-pair at the shared
  encoder for the static-λ baseline run. Payoff: if conflict is rare, Pebble *justifiably* reports that
  principled balancing gives no lift here (a publishable negative result on the recall-constrained setting that
  arXiv:2509.23915 says is untested) — saving the cost of a method that won't move the needle.
- **MTL ablation arm.** Add PCGrad as the **direction** arm alongside Kendall (scale) and GradNorm (norm), all
  via LibMTL `weighting=`. Expected payoff mirrors NYUv2: simultaneous small gains across all three heads rather
  than trading one head for another — exactly Pebble's worry that MSE/CE swamp the high-weight BCE.
- **Combine, don't choose.** Run `UW+PCGrad` as a fourth arm (CIFAR-100 evidence it stacks). Payoff: best shot
  at lifting emotion-F1 / severity-Pearson *without* touching crisis recall.

### Child mental-health lens (Pebble serves children: language & safety transfer? risks, mitigations, ethics)

- **Transfer is mechanism-level, not domain-level.** PCGrad operates purely on gradient geometry at the shared
  encoder; it is **agnostic to text, age, or domain**, so the method transfers unchanged to children's language.
  There is **nothing child-specific** in the paper (vision + robotics only) — so it neither helps nor hinders
  child-language modeling directly. Children's affect text (sparser, more idiosyncratic, code-mixed slang,
  developmentally varied) plausibly makes the crisis-head gradient *smaller and noisier* relative to the
  emotion head — exactly the magnitude-imbalance (`Φ→0`) regime PCGrad targets — so the mechanism is, if
  anything, *more* likely to be relevant here than in balanced vision benchmarks.
- **Safety risk — silent recall erosion.** The single biggest ethics caveat: stock PCGrad **projects the safety
  gradient too**. For a child-facing crisis detector this is unacceptable — a method tuned to maximize average
  multi-task performance can quietly trade away a fraction of suicide-risk recall for emotion-F1, and the paper
  optimizes *average* per-task performance with **no notion of an asymmetric/constrained objective**. Mitigation
  is the asymmetric variant above **plus** a hard gate: any ablation arm that drops crisis recall below 0.95 on
  the validation set is rejected regardless of its average-metric win.
- **Ordinal-cost blind spot.** PCGrad de-conflicts gradients but is indifferent to *which* errors matter. For
  children, a false-negative on high suicide-risk is categorically worse than an adjacent severity slip; PCGrad
  does nothing to encode that — it must be paired with the ordinal/distance-weighted crisis loss (Pillar 4) so
  the gradients it de-conflicts already carry the right asymmetric cost.
- **No calibration/uncertainty story.** A child-safety system needs calibrated risk scores; PCGrad changes the
  *optimization path*, not the output calibration, and Theorem 1's convergence guarantee assumes convex losses
  that NeoBERT does not satisfy — so empirical recall/calibration on held-out child-like data is the only
  acceptable acceptance test, not the theorem.

### Limitations & open questions for Pebble

1. **Evidence is vision/RL only** — zero NLP, zero transformer-encoder, zero heterogeneous CE+MSE+BCE evidence.
   All transfer to Pebble is by analogy; the NYUv2 "improves every task at once" result is the closest analogue
   but is dense-prediction CNNs, not a 250M encoder with a recall constraint.
2. **Convexity assumption is violated.** Theorem 1 needs convex, L-Lipschitz losses; NeoBERT fine-tuning is
   non-convex, so the "converges to optimum or `cos φ=−1`" guarantee is heuristic for Pebble. The `cos φ=−1`
   *stall* outcome is itself a risk to watch in logs.
3. **Random task-order dependence.** The projection is order-sensitive (App. H ablation); with only 3 Pebble
   heads this is cheap to enumerate, but it means PCGrad is not a single deterministic update — worth fixing the
   order (the crisis-reference variant fixes it by construction).
4. **No runtime/overhead numbers reported.** Each step needs one backward pass *per task* to get per-head
   gradients before projecting — roughly **3× backward cost** for Pebble's three heads vs a single summed-loss
   backward. On a 250M encoder this is non-trivial; budget it before committing.
5. **Average-performance objective ≠ Pebble's objective.** Every PCGrad result optimizes/reports *mean* task
   performance. Pebble's success criterion is constrained (recall ≥ 0.95 first, then lift the rest), a regime
   PCGrad was never evaluated under — so its published wins do not predict success on Pebble's actual metric.
6. **Open question:** does the asymmetric crisis-reference variant still de-conflict the emotion/severity heads
   usefully, or does protecting one head re-introduce conflict among the other two? Needs an empirical 3-head
   ablation; the paper gives no guidance for a "protected task."
