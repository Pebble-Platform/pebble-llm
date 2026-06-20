# Paper 09 — Multi-Task Learning as a Bargaining Game (Nash-MTL)

> Enrichment set · Pillar 1 (MTL loss balancing). Analysis depth: abstract-level. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Navon, Shamsian, Achituve, Maron, Kawaguchi, Chechik, Fetaya. ICML 2022.
- **Link:** [arXiv:2202.01017](https://arxiv.org/abs/2202.01017) · open
- **Pebble pillar:** principled multi-task loss balancing (named in Pebble's rubric).

## Summary
Frames per-task gradient combination as a Nash bargaining game, computing a single update direction whose per-task gains are balanced multiplicatively — making it scale-invariant across heterogeneous losses. Evaluated on vision/RL (NYUv2, CityScapes, CelebA, QM9, MTRL).

## Overlap with Pebble — 27% (peripheral)
`D1=1, D2=0, D3=0, D4=0, D5=2, D6=0, D7=0` → (3·1 + 2·2)/26 = 7/26 = **27%**
- **Closest on:** D5 (named in the rubric); weak partial D1 (head-agnostic, operates over any per-task gradient set).

## Best point — Method to adopt
Scale-invariance across MSE/CE/BCE is the property most likely to keep the high-recall BCE gradient from being swamped.
- **How to apply to Pebble:** Add Nash-MTL as a fourth balancing arm (static λ vs Kendall vs GradNorm vs Nash-MTL) — directly serves the survey's strongest angle (heterogeneous MTL under a hard safety-recall constraint).

## Dataset
Method paper — no dataset to acquire (vision/RL).

## Caveats
Abstract-only; vision/RL, not NLP-affect. Nash-MTL solves a small optimization per step (extra wall-clock) — relevant for Kaggle-GPU budgeting. A pure optimizer to borrow, not a comparable system.

## Deep research — full-PDF read (2026-06-10)

> Source: full text via ar5iv rendering of arXiv:2202.01017 (the local PDF could not be rasterized — `pdftoppm`/poppler is absent from this environment and no shell is available; the ar5iv full-text render of the same arXiv id was used instead, and equations/numbers below are cross-checked against the LibMTL `Nash_MTL` reference implementation that Pebble will actually call). Section/Table/Theorem numbers refer to the arXiv v2 layout.

### What the paper actually does (method, data, results — from the PDF, with exact numbers)

**Problem framing (Sec. 3).** At each optimization step the K task gradients `g_1…g_K` (computed at the *shared* parameters) span a set of achievable update directions inside a small ball `Δθ ∈ Bε`. Choosing the update is treated as a **bargaining game**: each task is a "player," its utility for an update `Δθ` is the first-order loss decrease `u_i(Δθ) = g_iᵀ Δθ`, and the disagreement point is `d_i = 0` (the no-update outcome). The **Nash Bargaining Solution (NBS)** is the unique point maximizing the product of utilities, i.e.

  `Δθ* = argmax_{Δθ ∈ Bε} Σ_i log(g_iᵀ Δθ)`   (proportional-fairness objective; product → sum of logs).

**The update / how the α weights are computed (Sec. 3, Eq. 5).** The NBS update is a *convex* combination of the raw gradients, `Δθ = Σ_i α_i g_i = G α`, where `G = [g_1 … g_K]` is the `d×K` gradient matrix. The optimal weight vector `α` (all `α_i > 0`) is the solution of the fixed-point system

  **`Gᵀ G α = 1/α`**   (element-wise reciprocal on the RHS).

This is solved per step by a **concave-convex procedure (CCP)** — a sequence of convex sub-problems `min_α Σ_i β_i(α) + φ(α)` with `β_i(α) = g_iᵀ G α` and `φ_i(α) = log α_i + log β_i` — run for **~20 iterations** (the RL setting uses a single iteration). Once `α` is found, the model takes an ordinary gradient step in direction `G α`.

**Scale invariance (Sec. 3.1 — the load-bearing property for Pebble).** Because the objective is `Σ log(g_iᵀΔθ)`, the solution is invariant to per-task affine rescaling of the losses: the paper states the solution "does not take into account the gradients' norms but rather treats all of them the same, as if they were normalized," and warns that "without enforcing this assumption, the solution can easily be dominated by a single direction." This is exactly the multiplicative balancing that distinguishes Nash-MTL from MGDA (min-norm, which collapses toward the smallest-norm gradient) and from linear scalarization (which the largest-norm gradient dominates).

**Theory (Sec. 5).** Under **Assumption 5.1** (task gradients are linearly independent except at Pareto-stationary points), **Theorem 5.4** states the iterate sequence has a subsequence converging to a **Pareto-stationary point**, with every task loss monotonically non-increasing along the way. So the method is not just a heuristic re-weighting; it carries a (local, first-order) Pareto guarantee.

**Update-frequency variants (Sec. 6.4).** Solving the CCP every step is the dominant cost. The paper introduces **Nash-MTL-k** that recomputes `α` only every *k* steps and reuses it in between:
- MT10 RL: full Nash-MTL = 0.91 success at 40.7 s/episode; **Nash-MTL-50 = 0.85 @ 8.6 s**; **Nash-MTL-100 = 0.87 @ 7.9 s** — i.e. ~5× faster for a ~0.04–0.06 success drop (vs CAGrad 0.83 @ 20.9 s; plain MTL-SAC 0.49 @ 7.3 s).
- QM9: stale-α gives ×3.7 speedup (every 5 steps) up to ×9.8 (every 50 steps) "with minimal performance loss."

**Experiments — exact headline numbers** (Δm% = mean per-task % degradation vs single-task baselines; **lower is better**, negative = beats single-task):

| Benchmark (tasks) | Nash-MTL | Best baseline | Notes |
|---|---|---|---|
| **NYUv2** (seg/depth/normals, Table 2) | **Δm% = −4.04** | CAGrad 25.61, LS 22.09, MGDA 29.18 | Nash-MTL wins seg mIoU **40.13**, pixel-acc **65.93**, depth-abs **0.5261**, rel **0.2171**; only the normal-angle metric (25.26) trails MGDA (24.88). It is the **only** method with negative Δm%. |
| **CityScapes** (seg/depth, Table 3) | **Δm% = 6.82** | LS 6.12 (best), CAGrad 11.64, MGDA 44.14 | mIoU **75.41**, depth-abs **0.0129**; here a *well-tuned LS* edges it out — note this for Pebble's null hypothesis. |
| **QM9** (11-property regression, Table 1) | **Δm% = 62.0 ± 1.4** | SI 77.8±9.2, CAGrad 112.8, LS 177.6 | Largest margin; the most *heterogeneous-scale* benchmark (11 physical units) — the case Nash-MTL is built for. |
| **MT10 RL** (10 robot tasks, Table 4) | **success 0.91 ± 0.031** | STL-SAC 0.90, CAGrad 0.83, PCGrad 0.72 | Matches independent single-task training while sharing one network. |

Baselines compared throughout: LS (linear scalarization), SI (scale-invariant), UW (uncertainty / Kendall), DWA, MGDA, PCGrad, CAGrad, IMTL, RLW. Nash-MTL has the best *average rank* across all benchmarks.

### Parts directly useful for Pebble (specific: equations, hyperparameters, splits, thresholds)

1. **The fixed-point solver `Gᵀ G α = 1/α` + ~20-iter CCP.** This is the entire computational object Pebble pays for. It operates on a `K×K` Gram matrix (here K = 3 heads), so the solve is *tiny* — the cost is forming `G`, which requires one backward pass **per head** to get each `g_i` at the shared `[CLS]`/encoder parameters.
2. **Compute `g_i` at the shared trunk only, not the full network.** The bargaining is over the *shared* gradient; per-head parameters update normally. For Pebble this means: backprop each head's loss to the shared NeoBERT output (or last shared layer) to get 3 vectors, run the CCP on their `3×3` Gram matrix, combine, then continue. LibMTL's `Nash_MTL` weighting already does this against any `shared_parameters()` set.
3. **Nash-MTL-k (k≈50–100) as the budget knob.** The "compute `α` every k steps" trick is the single most important deployability detail: on MT10 it cut wall-clock ~5× for a small quality loss. Pebble runs on Kaggle GPU quotas, so the k-stale variant is what makes Nash-MTL affordable next to the cheap arms (static-λ, Kendall).
4. **Δm% as the comparison metric.** The paper's headline metric — mean per-task percent change vs single-task models — is a clean, scale-free way to report Pebble's MTL ablation across heads with different units (CE F1, MSE, BCE recall). Adopt Δm% (or a recall-floored variant) as the ablation's summary number.
5. **The CityScapes result is a built-in caveat.** A *well-tuned* LS (static λ) beat Nash-MTL there (6.12 vs 6.82). This is the published evidence Pebble needs to keep static-λ as an honest baseline rather than a straw man.

### How each part helps Pebble succeed (concrete actions: which head/loss/experiment in Pebble it changes, expected payoff)

- **Action — add a `weighting=Nash_MTL` arm to the LibMTL ablation** (alongside `EW`/static-λ, `UW`/Kendall, `GradNorm`, `PCGrad`). *Changes:* the trainer's weighting strategy only; heads/losses unchanged. *Payoff:* a 4th, strong, scale-invariant point on the static-vs-principled curve that is Pebble's #1 novelty claim. QM9 (62.0 vs SI 77.8) is the evidence that Nash-MTL helps *most* exactly when task losses live on different scales — Pebble's CE (emotion) + MSE (severity/energy) + BCE (safety) mix is precisely that regime.
- **Action — set the CCP to stale-`α` (`update_weights_every=50`).** *Changes:* one hyperparameter in the Nash-MTL arm. *Payoff:* keeps the arm within Kaggle wall-clock budget (the per-step CCP is the only extra cost; the 5× speedup on MT10 shows the stale variant barely moves quality).
- **Action — report the ablation in Δm% with a recall gate.** *Changes:* the eval/reporting script. *Payoff:* one scale-free table comparing all 4 arms; pair it with the hard rule "row is invalid if safety recall < 0.95" so the winner is chosen *subject to* the safety floor, not on average loss alone.
- **Action — keep tuned static-λ as the baseline to beat.** *Payoff:* CityScapes shows fancy MTL can lose to well-tuned LS; if Nash-MTL doesn't clear tuned static-λ *and* hold recall ≥ 0.95, Pebble's honest finding is "static-λ suffices" — still a publishable, decision-relevant result.

### Child mental-health lens (Pebble serves children: does this transfer to children's language & safety needs? risks, mitigations, ethics caveats)

- **Domain transfer is neutral but real.** Nash-MTL is a pure optimizer over gradients — it is *agnostic to text, age, and language register*, so it transfers to children's affect text exactly as well (or as poorly) as it transfers to robot control. There is nothing child-specific to validate in the *method*; the risk lives entirely in **what it does to the safety head**.
- **Primary risk — the Pareto/equal-treatment objective has no notion of "this head must not lose."** Nash-MTL balances tasks *symmetrically* (proportional fairness, `d_i = 0` for all). It will happily trade a little crisis-recall for gains on emotion/severity if that improves the product of utilities. For a child-facing crisis detector a single missed high-risk message is catastrophic and asymmetric — a property the NBS does **not** encode. **Mitigation:** treat safety recall as a *hard constraint outside* the bargaining — e.g., floor the safety head's contribution, or reject any Nash-MTL step/epoch whose validation recall drops below 0.95, rather than trusting the balanced direction to protect it.
- **Scale-invariance cuts both ways for safety.** The property that prevents the BCE safety gradient from being *swamped* (good) also prevents Pebble from *deliberately over-weighting* it (a concern). On children's text — shorter, sparser crisis cues, more euphemism/coded language — the safety signal is already low-prevalence; an optimizer that normalizes it to parity with emotion may under-serve it. **Mitigation:** combine Nash-MTL with an explicit recall-oriented loss (focal/cost-sensitive BCE) *inside* the safety head so the head itself encodes the asymmetry, leaving Nash-MTL to balance the already-asymmetric gradients.
- **Ethics caveat — no convergence guarantee about *safety*.** Theorem 5.4 guarantees convergence to a *Pareto-stationary* point with monotone loss decrease; it says **nothing** about reaching a point that satisfies a recall floor. A "Pareto-optimal" model can be Pareto-optimal *and unsafe*. For a child mental-health deployment this must be stated explicitly: Nash-MTL optimizes a fairness objective, not a child-safety objective, and the recall floor must be enforced by an external gate + held-out crisis eval, never assumed from the optimizer's guarantees.

### Limitations & open questions for Pebble

- **Untested under a hard recall floor.** Every benchmark in the paper (NYUv2, CityScapes, QM9, MT10) is "minimize average degradation," never "satisfy a per-task constraint." Pebble's safety-floored regime is *out of distribution* for the published evidence — the central open question is whether Nash-MTL holds recall ≥ 0.95 while balancing, and whether the stale-`α` (k=50) variant degrades the safety gradient between recomputes.
- **No NLP / no transformer / no class-imbalance experiment.** All results are dense regression/segmentation/RL. There is zero evidence on text encoders, on a rare-positive BCE head, or on K=3 heterogeneous-loss heads of the CE+MSE+BCE kind. Transfer is plausible (the method is loss-agnostic) but unverified for Pebble's exact setup.
- **Gradient-conflict assumption.** Assumption 5.1 (gradients linearly independent off the Pareto set) and the whole NBS framing assume *non-degenerate, conflicting* gradients. If Pebble's heads turn out to be largely *aligned* (emotion and severity often co-vary), the bargaining buys little over static-λ — consistent with the CityScapes result where tuned LS won. Worth a quick gradient-cosine diagnostic before investing in the arm.
- **Cost vs the cheap arms.** Even stale, Nash-MTL needs one backward pass per head to form `G` each recompute; Kendall/static-λ need none. The k knob mitigates but does not eliminate this — budget it explicitly against Kaggle GPU quotas.
- **Hyperparameters not given for our regime.** The paper specifies ~20 CCP iters and the k-schedule for *their* tasks; Pebble must tune the CCP iteration count, the `update_weights_every` k, and which shared layer `G` is computed at (final `[CLS]` vs full encoder) — none of these have published guidance for a 250M text encoder.
