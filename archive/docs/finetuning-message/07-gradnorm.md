# Paper 07 — GradNorm: Gradient Normalization for Adaptive Loss Balancing

> Enrichment set · Pillar 1 (MTL loss balancing). Analysis depth: abstract-level. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Chen, Badrinarayanan, Lee, Rabinovich. ICML 2018.
- **Link:** [arXiv:1711.02257](https://arxiv.org/abs/1711.02257) · open
- **Pebble pillar:** principled multi-task loss balancing (the "GradNorm" method named in Pebble's strategy).

## Summary
Rebalances task weights by equalizing the normalized gradient magnitudes at the last shared layer, using a single asymmetry hyperparameter α to control how aggressively faster-learning tasks are held back. Built for mixed regression + classification in one network.

## Overlap with Pebble — 38% (peripheral, borderline adjacent)
`D1=2, D2=0, D3=0, D4=0, D5=2, D6=0, D7=0` → (3·2 + 2·2)/26 = 10/26 = **38%**
- **Closest on:** D5 (named in Pebble's rubric) and D1 (explicitly for mixed regression + classification in one shared-trunk network — Pebble's MSE+CE+BCE situation).

## Best point — Method to adopt
Equalize per-task normalized gradient norms at the shared `[CLS]`/last-shared layer; α is the one knob.
- **How to apply to Pebble:** When the three heads diverge under static weights, apply GradNorm at the shared `[CLS]` with α≈1.5 and benchmark it head-to-head against Kendall uncertainty weighting (the two MTL arms on Pebble's roadmap).

## Dataset
Method paper — no dataset to acquire (vision + synthetic regression).

## Caveats
Abstract-level scoring. Two transfer risks: (1) GradNorm balances learning *rates*, not recall — it will not by itself guarantee the safety head's recall ≥ 0.95 (enforce via class weighting/thresholding on top). (2) Vision-only; no encoder, domain, or distillation content. Value is the optimization recipe, not domain/data.

## Deep research — full-PDF read (2026-06-10)

> **Sourcing note.** The local renderer for `pdfs/07-gradnorm.pdf` (`pdftoppm`) was unavailable in this
> environment and Bash extraction was disabled, so the deep read was performed against the identical
> canonical source — the arXiv v3 full text (arXiv:1711.02257, ar5iv HTML mirror of the same ICML 2018
> paper). Section/equation/table numbers below are the paper's own. Everything is the published content;
> no number is inferred. If a local-PDF-only check is later required, re-run once `pdftoppm` is on PATH.

### What the paper actually does (method, data, results — from the PDF, with exact numbers)

**Problem & idea.** In a hard-parameter-sharing multitask net the total loss is `L(t) = Σ_i w_i(t)·L_i(t)`.
Fixed `w_i` let whichever task has the largest/fastest gradients dominate the shared trunk; tasks then
train at different *rates* and the slow ones underfit. GradNorm makes the `w_i` **learnable parameters,
updated every step** so that the per-task gradient magnitudes at the shared trunk are driven toward a
common, training-rate-adjusted target (Sec. 1, Sec. 3).

**Exact quantities (Sec. 3.1–3.2).** Let `W` = the **last shared layer** of weights (chosen "to save
compute"; ~5% overhead, Sec. 3.1):
- `G_W^(i)(t) = ‖∇_W ( w_i(t)·L_i(t) )‖₂` — L2 norm of each task's *weighted* gradient at `W`.
- `Ḡ_W(t) = E_task[ G_W^(i)(t) ]` — mean gradient norm across tasks.
- `L̃_i(t) = L_i(t)/L_i(0)` — inverse training rate (loss now ÷ loss at step 0; lower = more trained).
- `r_i(t) = L̃_i(t) / E_task[ L̃_i(t) ]` — **relative** inverse training rate (a task training *slower
  than average* has `r_i > 1`).
- **Target (Eq. 1):** `G_W^(i)(t) → Ḡ_W(t) · [ r_i(t) ]^α` — slow tasks get a *larger* target gradient.
- **GradNorm loss (Eq. 2):** `L_grad(t; w_i) = Σ_i | G_W^(i)(t) − Ḡ_W(t)·[r_i(t)]^α |₁` (L1).

**Algorithm 1 (the part that's easy to get wrong).** Each step: (a) forward, get `L_i`; (b) compute
`G_W^(i)`, `r_i`, `Ḡ_W`; (c) form `L_grad`; (d) **differentiate `L_grad` only w.r.t. the `w_i`, holding
the target `Ḡ_W·[r_i]^α` as a constant** (no grad through the target); (e) step the `w_i`; (f)
**renormalize `Σ_i w_i = T`** (T = #tasks) each step to "decouple gradient normalization from the global
learning rate"; (g) normal backward pass updates `W` (and the rest of the net) with the *current* `w_i`.
`w_i(0)=1`. So there are two optimizers running: the main one on the network, a tiny one on the `T` weights.

**α — the single knob (Sec. 3.2, 5.4).** α is the "restoring-force strength" pulling tasks to a common
rate. α=0 ⇒ enforce *equal* gradient norms; larger α ⇒ tolerate asymmetry, push more on slow tasks.
Values actually used: **toy = 0.12** (statistically identical tasks, differ only in loss scale), **NYUv2
= 1.5** (heterogeneous vision tasks), **MTFL faces = 0.2–0.3**. Robustness claim: *"almost any value
0 < α < 3 improves performance over equal weights"* (Sec. 7.1).

**Data / nets / results.**
- *Toy (Sec. 4):* T regression tasks `f_i(x)=σ_i·tanh((B+ε_i)x)`, input 250→output 100, 4-layer FC ReLU.
  With T=2 and `σ₀=1, σ₁=100`, GradNorm raises `w₀` to counter task-1's larger gradients and beats equal
  weights; T=10 shows the same and is "more stable and outperforms uncertainty weighting" (Kendall).
- *NYUv2+seg (Table 1, VGG16 SegNet, 29M params, 795 train / 654 test, 320×320→80×80; depth=squared
  loss, seg=cross-entropy/13-class, normals=cosine):* Equal-weights depth-RMS **0.944 m**, seg-err
  (100−IoU) **70.1**, normals-err **0.192** → **GradNorm α=1.5: 0.925 / 67.8 / 0.174** — *all three
  improve at once*.
- *NYUv2+kpts (Table 2; 90k imgs, depth + 48 room-keypoints + normals; tested on ResNet-50-FCN 15M and
  VGG SegNet):* On VGG, Equal **0.658 / 8.39% / 0.155** vs Kendall **0.649 / 8.00 / 0.158** vs **GradNorm
  α=1.5 0.629 / 7.73 / 0.139**. On ResNet, **GradNorm α=1.5 0.663 / 7.32 / 0.155** beats Equal
  (0.697/7.80/0.172) and Kendall (0.702/7.96/0.182) on every task.
- *MTFL faces (Sec. 7.2):* GradNorm α=0.2–0.3 cuts gender error from 18.6→14.4% and smile 17.4→15.4% at
  160×160 vs equal weights; Kendall actually *degraded* gender to 38.1% at 160×160.
- *Grid-search showdown (Sec. 5.3, Fig. 4):* they trained **100 networks with random fixed weights**; even
  the best still **fall short of the single GradNorm run**, and there's a strong negative correlation
  between a net's distance from GradNorm's time-averaged weights and its performance (at L2≈3, ~double the
  per-task error). Headline: *"GradNorm found the optimal grid-search weights in one training run"* and
  "matches or surpasses exhaustive grid search despite a single hyperparameter α."
- *Regularization (Sec. 5.2, Fig. 3):* GradNorm improves **test** depth error ~5% *while converging to a
  much higher training loss* — "a clear signal of network regularization," and contrasts with uncertainty
  weighting which "always moves test and training error in the same direction" (not a regularizer).
- Overhead **~5%** training time. `w_i` can be driven tiny (α=1.75 ⇒ `w_depth < 0.02`; MTFL `w_kpt ≤ 0.01`)
  "at no detriment" to those tasks, per the paper.

### Parts directly useful for Pebble (specific: equations, hyperparameters, splits, thresholds)

1. **Eq. 1–2 + Algorithm 1 verbatim** are the implementable recipe. For Pebble `T=3` (emotion CE, severity/
   energy MSE, safety BCE). `W` = NeoBERT's **last shared transformer block / the `[CLS]` projection feeding
   the heads** — not the heads themselves.
2. **`r_i(t)=L̃_i/E[L̃]` is scale-free.** Because it normalizes by each task's *own* step-0 loss, GradNorm
   compares CE vs MSE vs BCE without any manual scaling — exactly Pebble's mixed-loss problem (the toy
   `σ₁=100` case is the analogue).
3. **The renormalize-to-T trick** keeps `Σw_i = 3` so the main LR stays meaningful — copy it exactly.
4. **α = 1.5** is the tested default for *heterogeneous* tasks (Pebble's heads are heterogeneous, like NYUv2,
   not the toy regime) — start there, sweep `0 < α < 3`, expect monotone-ish gains in that range.
5. **The grid-search protocol (Sec. 5.3)** is a ready experimental design: Pebble's "static-λ vs principled"
   claim can be made the *same way* — sample N static-λ triples, show none beats GradNorm's single run.
6. **The "hold the target constant" detail** is the #1 implementation gotcha; LibMTL's `GradNorm` already
   does this, so prefer the library over a hand roll.

### How each part helps Pebble succeed (concrete actions: which head/loss/experiment it changes, expected payoff)

- **MTL ablation arm (Pebble's #1 novelty).** Drop GradNorm in via LibMTL as the second principled arm
  (after Kendall). Wire `weighting=GradNorm`, `alpha=1.5`, point the shared module at NeoBERT's last block.
  *Payoff:* a single-knob method that, per Table 2, beats both equal-weights and Kendall on **every** task
  simultaneously — the clean win Pebble needs to claim "principled > static λ."
- **Kills the manual λ search for severity/energy.** Today severity-MSE and emotion-CE need hand-balanced
  λ; `r_i` removes that. *Payoff:* fewer training runs, and the severity head stops being swamped by the
  larger-scale loss (the exact `σ₀=1, σ₁=100` failure the toy reproduces).
- **Regularization on the small target sets.** Pebble's C-SSRS (500 users) and WASSA (1,860 essays) are
  tiny and overfit-prone. GradNorm's Sec. 5.2 result — better test error at *higher* train loss — is
  directly attractive. *Payoff:* better generalization on exactly the data-starved heads.
- **Fair-baseline experiment for the paper.** Run the Sec. 5.3 100-net grid-search protocol (scaled down,
  e.g. 25–50 static-λ triples) → a publishable figure that rules out the "well-tuned static weights match
  fancy methods" null (the 2509.23915 concern in `related-work-enrichment.md`, Pillar 1).
- **Safety head must be special-cased.** GradNorm *suppresses* fast/easy tasks' weights toward zero
  (α=1.75 ⇒ `w<0.02`). If the safety BCE trains fast (it often does — crisis cues are lexically salient),
  GradNorm could shrink `w_safety` and quietly erode recall. *Action:* **floor `w_safety` at a minimum
  after each renormalize step** (clip-then-renormalize the other two), or exclude safety from GradNorm and
  weight it by a fixed high λ. *Payoff:* keeps recall ≥ 0.95 while still auto-balancing emotion vs severity.

### Child mental-health lens (Pebble serves children: does this transfer to children's language & safety needs? risks, mitigations, ethics caveats)

- **Domain transfer is neutral-to-favorable.** GradNorm is a pure optimization rule over loss ratios; it
  has *zero* assumptions about the input modality, so children's-language text transfers as readily as
  adult text — nothing in Eq. 1–2 cares about vocabulary or register. The benefit (regularization on small
  sets) is *more* valuable for children's data, which is scarcer and noisier than adult corpora.
- **The central child-safety risk is the auto-suppression behavior.** The paper *celebrates* driving a
  task weight near zero "at no detriment" — but that judgment was made on depth/keypoint vision tasks where
  a small accuracy slip is harmless. For Pebble, an analogous silent down-weighting of the **suicide-risk
  head** is a child-safety failure, not a convenience. The paper offers *no* mechanism to protect a task
  from being optimized away. **Mitigation: a hard `w_safety` floor is non-negotiable**, plus a recall
  tripwire on the validation set that halts/reverts if recall dips below 0.95 during GradNorm training.
- **"Balance training *rates*, not metrics."** The paper is explicit (Sec. 3.2): GradNorm equalizes how
  *fast* tasks learn, never their end-quality or any fairness/recall metric. So it must **never be the
  thing Pebble relies on for the recall floor** — that stays an explicit constraint (class weighting,
  decision-threshold tuning, post-hoc recall calibration). GradNorm is a convenience layer *under* the
  safety guarantee, never part of it.
- **Calibration drift caveat.** Because GradNorm moves `w_i` every step and prefers higher train loss for
  regularization, the severity/energy head's *calibration* (not just ranking) can shift run-to-run. For a
  child-facing system, the severity score gates real escalations, so re-check calibration (reliability
  curve / ECE) after any GradNorm run, not just F1.
- **Ethics/eval.** GradNorm gives no interpretability into *why* a head was down-weighted; for a regulated
  child mental-health tool, log the `w_i(t)` trajectories as an auditable training artifact so a reviewer
  can confirm the safety head was never suppressed.

### Limitations & open questions for Pebble

1. **No NLP / no transformer evidence.** All results are vision (NYUv2, MTFL) with T≤10 and CNN/ResNet
   backbones; the paper never touches an encoder LM, attention trunk, or text losses. Whether the
   last-*block* of NeoBERT is as good a choice of `W` as the last *conv* layer is untested — open question.
2. **Mixed loss *types* untested in the strong sense.** The paper notes (its own closing caveat) it does
   **not** establish that GradNorm works equally for "vastly different loss types (BCE vs pixel regression)."
   Pebble mixes CE + MSE + BCE; needs an empirical check, not an assumption.
3. **Tiny-T regime only.** T=3 (Pebble) is within tested range (NYUv2 T=3), so this is fine — but the
   instability of `r_i` when a task's `L_i(0)` is near zero (e.g. an easy safety head almost solved at init)
   is not analyzed. Pebble should sanity-check `L_i(0)` is well above zero before relying on `r_i`.
4. **The near-zero-weight "no detriment" claim is unverified for safety-critical tasks** — see the child
   lens. Treat it as false-until-proven for `w_safety`.
5. **Compute knob.** `G_W^(i)` needs a per-task gradient w.r.t. `W` each step; on NeoBERT this is cheap if
   `W` is the small `[CLS]`-projection but grows if you choose a full transformer block — measure the real
   overhead (paper's "~5%" was a 29M VGG, not a 250M encoder).
6. **vs the newer arms.** Paper predates PCGrad/Nash-MTL; GradNorm fixes gradient *scale*, not *direction*
   conflict. If Pebble sees direction conflict (severity vs emotion pulling opposite ways), GradNorm won't
   help — that's PCGrad's job. Open question which conflict dominates in Pebble's heads.
