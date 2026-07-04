# Paper 48 — CORAL: Rank-Consistent Ordinal Regression for Neural Networks

> Family C (ordinal + imbalance) · Citation-anchor + implementation-verification depth (full method + R2 source cross-check). Compiled 2026-06-25.

## Bibliographic info
- **Authors / Year / Venue:** Wenzhi Cao, Vahid Mirjalili, Sebastian Raschka — submitted 2019, published 2020 in **Pattern Recognition Letters, Vol. 140, pp. 325–331**. Full title: *Rank consistent ordinal regression for neural networks with application to age estimation*.
- **Link:** [arXiv:1901.07884](https://arxiv.org/abs/1901.07884) · open — **VERIFIED** (title/authors/venue confirmed via arXiv abstract page, 2026-06-25).
- **Pebble pillar:** suicide-risk severity (ordinal). **R2's ordinal head IS this method** — `coral_fc = nn.Linear(h,1,bias=False)` (one shared weight vector) + `coral_bias = nn.Parameter(zeros(K-1))` (independent ordered thresholds). This paper is the foundation R2's tri-objective head sits on, so it is a mandatory citation anchor and the document against which R2's implementation faithfulness is checked.

## Summary
CORAL reframes K-class ordinal regression as **K−1 binary subtasks** with extended labels `t_k = 1[y > r_k]` (probability the example ranks above threshold k). The published failure mode it fixes: naive "OR-NN" with K−1 *independent* classifiers can produce **non-monotone** cumulative predictions (e.g. P(y>1) > P(y>0)), which are logically impossible for an ordinal scale and hurt rank metrics. CORAL's fix is structural: **all K−1 logits share a single weight vector w and differ only by per-rank bias terms** `g_k(x) = wᵀf(x) + b_k`. Because the slope `wᵀf(x)` is identical across thresholds, ordering the biases `b_0 ≥ b_1 ≥ … ≥ b_{K-2}` guarantees `P(y>0) ≥ P(y>1) ≥ …` for **every** input — rank-monotonicity is proven, not hoped for. The loss is a (optionally importance-weighted) sum of K−1 binary cross-entropies on the extended labels; rank prediction = count of thresholds whose sigmoid exceeds 0.5.

## Overlap with Pebble/R2 — 50% (adjacent)
`D1=1, D2=2, D3=0, D4=0, D5=0, D6=2, D7=2` → (3·1 + 2·2 + 2·2 + 1·2)/26 = (3+4+4+2)/26 = 13/26 = **50%**
- **Closest on:** D2 (C-SSRS suicide-risk is the headline application surface for R2) and D6 — CORAL's monotone severity scale is exactly the ordinal backbone behind a recall-sensitive crisis ladder; D7 (the head is architecture-agnostic and bolts onto R2's NeoBERT `[CLS]` unchanged). D1 partial: CORAL is one head, not the heterogeneous multi-head MTL setup. The 50% understates relevance for *this* deliverable — R2 literally implements the paper, so it is a citation anchor regardless of the rubric score.

## Best point — Verification + citation anchor
CORAL's rank-consistency guarantee is purely structural: **one shared slope + ordered biases ⇒ monotone cumulative probabilities for all inputs.** R2's head reproduces this exactly (`coral_fc` is a single `Linear(h,1,bias=False)`, biases are a per-threshold `Parameter`), so R2 inherits the guarantee — and CORAL is the correct foundational citation for R2's ordinal contribution.
- **How to apply to Pebble:** Cite CORAL (Cao et al., PRL 2020) as the ordinal foundation in Related Work and Method (the paper plan §4.2/§4.3 already lists it), and report that R2's head is a faithful CORAL implementation so the rank-monotone property carries to C-SSRS for free.

## ▶ Apply to R2 (MANDATORY)
1. **Implementation is FAITHFUL — confirmed against source.** `r2-suicide-risk-dualhead.py`:
   - `self.coral_fc = nn.Linear(h, 1, bias=False)` (line 317) → the **single shared weight vector** `w`. ✓ matches CORAL.
   - `self.coral_bias = nn.Parameter(torch.zeros(n_classes-1))` (line 318) → **independent per-threshold biases** `b_k`. ✓
   - `coral_logits = self.coral_fc(u) + self.coral_bias` (line 349) → `g_k(x) = wᵀu + b_k`, the exact CORAL form (shared slope, broadcast over K−1 biases). ✓
   - `coral_loss` (lines 355–359): `t = (y > levels)` builds extended labels `t_k = 1[y>k]`, then `binary_cross_entropy_with_logits` — exactly CORAL's K−1-BCE loss. ✓
   - **Verdict:** R2 is a correct CORAL implementation. The shared-weight construction is what matters for the guarantee, and it is present.
2. **Rank-monotonicity caveat — guarantee holds at the logit level, but R2 does NOT enforce ordered biases or use rank-count decoding.** Two gaps vs the paper:
   - *Biases are free, not constrained to `b_0 ≥ b_1 ≥ …`.* CORAL's *proof* assumes ordered biases; in practice BCE training pushes them toward order but does not pin it. After training, **assert `coral_bias` is non-increasing** (it almost always is); if a fold violates it, the per-input monotonicity claim breaks for that fold. Cheap check, worth reporting.
   - *Decoding is not CORAL's rank-count.* `coral_to_probs` (lines 371–380) converts cumulative `P(y>k)` to per-class via differences `P(y=k)=P(y>k-1)−P(y>k)`; if biases are ordered these differences are non-negative, but if a fold's biases are out of order a difference can go negative (currently masked by `clamp_min(1e-6)`). The paper's native predictor is `rank = Σ_k 1[σ(g_k)>0.5]`, which is monotone by construction. **Recommend logging the CORAL rank-count prediction alongside the blended argmax** as a monotonicity sanity check.
3. **Reporting recommendation (paper plan §3 item 2 — ablation).** Report **flat-CE vs CORAL-only vs dual-head** as the headline ordinal ablation, and (caveat paper 49) flag that **CORN** is the strictly-more-expressive successor that removes CORAL's shared-weight restriction — position R2's CORAL choice as the simpler, guarantee-preserving baseline and cite CORN as future work.
4. **Importance weights per task.** CORAL supports per-threshold importance weights in the BCE sum (Eq. for the weighted loss). R2's `coral_loss` uses **unweighted** mean BCE. Given the Behavior collapse (W1), consider weighting the K−1 thresholds by inverse class frequency around each cut — the Behavior↔Attempt threshold is the rarest and least-learned. This is the in-paper knob most directly aimed at R2's bottleneck.

## ▶ Kaggle experiment (MANDATORY)
**The ordinal ablation the paper plan (§3 item 2a) calls for**, driven by the existing loss-weight env knobs (`w_coral` / `w_ce` / `w_focal`), no code change needed:

| Arm | env (`w_coral`,`w_ce`,`w_focal`) | Decoding |
|---|---|---|
| **flat-CE only** | `0.0, 1.0, 0.0` | `argmax(softmax(cls))` |
| **CORAL only** | `1.0, 0.0, 0.0` | `argmax(coral_to_probs)` (and log CORAL rank-count) |
| **dual-head (current)** | `0.5, 0.3, 0.2` | current 0.5/0.5 blend |

- **Expected signal:** CORAL-only and dual-head should show **lower MAE and lower adjacent-error, higher QWK** than flat-CE (ordinal structure penalizes high→low slips); flat-CE may match or edge out on raw macro-F1 since F1 is rank-blind. The interesting result for the paper is the **QWK/MAE gap** isolating CORAL's contribution from CE/Focal. Also emit, per arm: `coral_bias` ordering check + count of negative pre-clamp class probs (monotonicity audit).
- **Cost:** 3 arms × the existing 5-fold within-dist CV (already wired). ~3× one training run on the current 10k pool — single Kaggle GPU session range, no new dataset or kernel. Reuse `r2-within-dist-cv.py`; vary only the three env vars.

## Caveats
- **Verification status:** R2 source cross-check is **complete and confirms faithfulness** (lines 317–318, 349, 355–359 above). The paper's *proof preconditions* (ordered biases, rank-count decode) are **not asserted in R2** — guarantee holds empirically but is unverified per-fold; the audit in "Apply" item 2 is the gap-closer.
- **CORAL vs CORN (paper 49).** CORAL's shared-weight restriction is exactly what CORN (Shi, Cao, Raschka 2021) relaxes via conditional probabilities, often improving accuracy while keeping rank consistency. R2 uses CORAL; cite CORN as the natural extension / future-work, not as a flaw.
- **Rank-consistency caveat.** The guarantee is *per-input monotonicity of cumulative probabilities*, NOT a guarantee of better F1 or of fixing class imbalance — Behavior collapse (W1) is an imbalance problem CORAL alone does not solve (hence the importance-weight and focal arms). Do not oversell rank-consistency as a F1 lever.
- Method mechanism (shared-weight monotonicity proof, weighted BCE) is from the established CORAL formulation; the arXiv abstract page confirmed title/authors/venue but not the equations (full-PDF not re-rendered) — equations cross-checked against R2's implementation, which matches.
