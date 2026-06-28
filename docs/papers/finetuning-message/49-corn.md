# Paper 49 — CORN: Conditional-Probability Rank-Consistent Ordinal Regression

> Family C (ordinal) · R2 text stream · Analysis depth: abstract + arXiv HTML v5 + coral-pytorch source. Successor to CORAL that removes the shared-weight constraint. Compiled 2026-06-25.

## Bibliographic info
- **Authors / Year / Venue:** Xintong Shi, Wenzhi Cao, Sebastian Raschka — published **2023** in **Pattern Analysis and Applications** (Springer), DOI [10.1007/s10044-023-01181-9](https://link.springer.com/article/10.1007/s10044-023-01181-9). First posted on arXiv Nov 2021.
- **Link:** [arXiv:2111.08851](https://arxiv.org/abs/2111.08851) · open · **VERIFIED** (Springer DOI + arXiv both resolve; reference implementation in [coral-pytorch](https://github.com/Raschka-research-group/coral-pytorch)).
  - *Note:* the task brief said "Pattern Recognition" — the actual venue is **Pattern Analysis and Applications**. Corrected here.
- **Pebble pillar:** R2 ordinal suicide-risk head. CORN is the **direct successor to CORAL**, the loss R2 currently runs (`coral_loss` / `coral_to_probs` in `r2-suicide-risk-dualhead.py`). This is the CORAL-vs-CORN ablation arm in [`PAPER-PLAN-text-ordinal-suicide.md`](./PAPER-PLAN-text-ordinal-suicide.md) §3 row 🔴2.

## Summary
CORN trains **K−1 independent binary classifiers** for the cumulative events but, unlike CORAL, does **not** force them to share a single weight vector. Instead it enforces rank consistency through the *training scheme*: the k-th binary task `P(y > k | y > k−1)` is trained only on the **conditional subset** of examples with `y > k−1` (nested, shrinking subsets). Because each head models a genuine conditional probability, the unconditional cumulative probabilities are recovered by the **chain rule** — `P(y > k) = ∏_{j≤k} P(y > j | y > j−1)` — which is monotonically non-increasing in k *by construction*, so predictions can never be rank-inconsistent. The payoff: rank consistency is preserved while each threshold gets its **own full-rank weight vector**, making the head strictly more expressive than CORAL's single shared `w_c` + ordered biases. The paper reports CORN beating CORAL on MAE/accuracy across MORPH-2, AFAD, AES, and FireMan with no architecture changes.

## Overlap with Pebble/R2 — 15% (peripheral)
`D1=1, D2=0, D3=0, D4=0, D5=0, D6=0, D7=1` → (3·1 + 1·1)/26 = 4/26 = **15%**
- **Closest on:** D1 (ordinal output head feeding R2's severity path) and D7 (architecture-agnostic — drops onto a NeoBERT `[CLS]` pooled vector unchanged).
- The low % reflects the generic rubric: this is a pure-ML methods paper with no mental-health domain, no LLM-distillation, no MTL balancing, no safety-recall objective. Its **utility to R2 is far higher than 15% implies** — it is a one-file drop-in upgrade to a component R2 already ships. The rubric scores *project-surface* overlap, not engineering leverage; see Caveats.

## Best point — Method to adopt (drop-in upgrade)
Replace R2's CORAL head with **CORN**: keep rank consistency (the property that made CORAL worth using over flat softmax for adjacent-error/QWK) but **drop the shared-weight bottleneck**, giving each of the 3 thresholds (4-class C-SSRS → K−1=3) its own weight vector. This is the single highest-leverage change because R2's documented weakness is exactly ordinal-head expressivity (QWK 0.398, MAE 0.822, and the Behavior class collapse at F1 0.183), and CORN's whole contribution is "more expressive ordinal head, same rank guarantee, zero architecture cost."
- **How to apply to Pebble:** swap `coral_fc(shared)+coral_bias` for `nn.Linear(h, K-1)`, swap `coral_loss` for the CORN conditional-subset BCE, and swap `coral_to_probs` for chain-rule decoding — same tri-objective weights, same everything else; run head-for-head against CORAL.

## ▶ Apply to R2 (MANDATORY)
Exact edits to `kaggle/finetuning-message/r2-suicide-risk-dualhead/r2-suicide-risk-dualhead.py`:

1. **`HierarchicalDualHead.__init__` (lines 316–318)** — replace the shared-weight pair
   ```python
   self.coral_fc = nn.Linear(h, 1, bias=False)               # shared weight w_c
   self.coral_bias = nn.Parameter(torch.zeros(cfg.n_classes - 1))
   ```
   with **K−1 independent logits**:
   ```python
   self.corn_fc = nn.Linear(h, cfg.n_classes - 1)            # K-1 independent rows + biases
   ```

2. **`HierarchicalDualHead.forward` (line 349)** — replace
   ```python
   coral_logits = self.coral_fc(u) + self.coral_bias
   ```
   with `corn_logits = self.corn_fc(u)` (shape `(B, K-1)`; rename the returned tensor or keep the variable name `coral_logits` to minimize downstream churn).

3. **`coral_loss` (lines 355–359)** — replace the single global BCE over `t_k = 1[y>k]` with the **CORN conditional loss**: for each rank `k`, compute BCE of logit `k` against target `1[y>k]` **only over rows where `y >= k`** (the conditional subset `y > k−1`), then sum/average over the K−1 tasks. Sketch:
   ```python
   def corn_loss(logits, y, n_classes):
       loss = 0.0; n = 0
       for k in range(n_classes - 1):
           mask = y >= k                         # conditional subset: y > k-1
           if mask.sum() == 0: continue
           t = (y[mask] > k).float()
           loss = loss + F.binary_cross_entropy_with_logits(logits[mask, k], t, reduction="sum")
           n += int(mask.sum())
       return loss / max(n, 1)
   ```

4. **`coral_to_probs` (lines 371–380)** — replace cumulative-sigmoid decode with **chain-rule decode**: `P(y>k) = ∏_{j≤k} σ(logit_j)`, then difference adjacent cumulatives to per-class probs:
   ```python
   def corn_to_probs(logits, n_classes):
       pcond = torch.sigmoid(logits)                         # P(y>k | y>k-1)
       pgt = torch.cumprod(pcond, dim=1)                     # P(y>k) — monotone by construction
       B = logits.size(0)
       probs = torch.zeros(B, n_classes, device=logits.device)
       probs[:, 0] = 1 - pgt[:, 0]
       for k in range(1, n_classes - 1):
           probs[:, k] = pgt[:, k-1] - pgt[:, k]
       probs[:, -1] = pgt[:, -1]
       return probs.clamp_min(1e-6)
   ```
   The `argmax` / threshold-counting prediction logic downstream is unchanged.

5. Keep the **tri-objective `0.5*CORN + 0.3*CE + 0.2*Focal`** weights identical (CORN swaps in for the CORAL term 1:1) so the ablation isolates head expressivity. Optionally gate via an env flag `R2_ORDINAL_HEAD=coral|corn` so both run from one kernel.

## ▶ Kaggle experiment (MANDATORY)
- **Design:** CORN head vs CORAL head, **everything else frozen** — same backbone, same 5-fold gold-holdout split, same loss weights, same `R2_BALANCE`, same seeds. One env flag toggles the head. Run both arms × 5 folds.
- **Primary signal:** QWK and MAE (CORN's claimed win is lower MAE / fewer rank violations) — beat Run B's **QWK 0.398 / MAE 0.822**.
- **Secondary signal (the W1 lever):** per-class **Behavior** F1 and **adjacent-error rate** around Behavior. Behavior is the middle-rank bottleneck (F1 0.183, 6.5% of pool); CORAL's shared weight forces the Behavior threshold to share direction with all others, which is plausibly *why* the squeezed middle class collapses. CORN gives Behavior its own threshold vector — watch whether Behavior recall and adjacent-confusion (Behavior↔Ideation, Behavior↔Attempt) improve.
- **Decision rule:** adopt CORN if it improves QWK/MAE without dropping macro-F1, or if it raises Behavior F1 at equal QWK. Report both arms with 5-fold mean ± std (std ≈ 0.007 historically — a real win must clear that).
- **Cost:** negligible. Identical model size and compute to the CORAL run (one extra `cumprod`, K−1 small linear rows instead of 1). ~1 extra Kaggle GPU run for the second arm; no new data, no new download.

## Caveats
- **Rubric vs leverage divergence:** 15% is honest *project-surface* overlap (no MH domain, no MTL, no safety head, no LLM labels). Engineering leverage is much higher — it is a one-file drop-in on a component R2 already runs and the plan already calls for ablating. Do not let the low % deprioritize it.
- **Conditional-subset training shrinks effective batch per rank:** the k-th task trains only on rows with `y >= k`, so higher ranks (Attempt) see *fewer* examples per batch than CORAL, which uses every row for every threshold. On R2's already-imbalanced 4-class problem (Attempt rare, Behavior 6.5%) the top thresholds may get noisy gradients — mitigate with larger batch / gradient accumulation, and treat "CORN helps tail classes" as a hypothesis to test, not a given. This is the main risk that could make CORN *lose* to CORAL despite higher expressivity.
- **coral-library availability:** Raschka's `coral-pytorch` ships reference `corn_loss` and `corn_label_from_logits`; cross-check the hand-rolled implementation above against it (especially the conditional-mask indexing and the `cumprod` decode) before trusting fold numbers. If `pip install coral-pytorch` is permitted in the Kaggle env, prefer the library's `corn_loss` to remove implementation risk.
- **Verification status:** title/authors/venue/DOI/arXiv all VERIFIED via Springer + arXiv. CORN-beats-CORAL benchmark numbers are from the paper's own experiments (MORPH/AFAD/AES/FireMan) — **not** mental-health text; the gain on R2's C-SSRS task is unverified until the ablation runs. CORAL companion note `48-coral.md` did not exist at compile time; contrast above is drawn from the live R2 CORAL code.
