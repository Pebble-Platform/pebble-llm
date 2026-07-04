# Paper 51 — Focal Loss for Dense Object Detection

> Family C (imbalance) · Analysis depth: abstract + CVF/arXiv verification + R2 code cross-check. Compiled 2026-06-25. **R2's citation anchor** — R2 already runs focal loss (γ=2); this paper is the reference + a knob to tune for the Behavior bottleneck.

## Bibliographic info
- **Authors / Year / Venue:** Tsung-Yi Lin, Priya Goyal, Ross Girshick, Kaiming He, Piotr Dollár · 2017 · **IEEE ICCV 2017** (Venice, pp. 2999–3007), **ICCV 2017 Best Student Paper Award**; extended journal version in **IEEE TPAMI 2020** (vol. 42, no. 2, pp. 318–327).
- **Link:** [arXiv:1708.02002](https://arxiv.org/abs/1708.02002) · open. CVF open-access: [openaccess.thecvf.com/.../Lin_Focal_Loss_for_ICCV_2017_paper.html](https://openaccess.thecvf.com/content_iccv_2017/html/Lin_Focal_Loss_for_ICCV_2017_paper.html) — **VERIFIED** (title, all five authors, ICCV 2017 venue and page range confirmed via CVF + ScienceResearchPublishing reference records).
- **R2 pillar:** imbalance / hard-example mining. **R2 already uses focal loss** — `focal_loss()` and `focal_gamma=2.0`, `w_focal=0.2` in `kaggle/finetuning-message/r2-suicide-risk-dualhead/r2-suicide-risk-dualhead.py`. This is the paper R2 must cite for that term, and the source of the γ default R2 inherited.

## Summary
Standard cross-entropy on extreme class imbalance is dominated by the gradient of vast numbers of easy, well-classified examples (background anchors in detection). Focal loss multiplies CE by a **modulating factor `(1 − p_t)^γ`** that smoothly down-weights easy examples (high `p_t`) and keeps the loss on hard examples (low `p_t`) near full strength; **γ controls how aggressively** easy examples are suppressed (γ=0 ⇒ plain CE). The authors add an **α-balanced variant**, `FL = −α_t (1 − p_t)^γ log(p_t)`, where α weights the rare class. Their best detector (RetinaNet) uses **γ=2, α=0.25** and, trained with focal loss, matches one-stage speed while beating all then-current two-stage detectors. The core claim: reshaping the loss to emphasize hard examples beats heuristic hard-negative mining / sampling.

## Overlap with Pebble/R2 — 31%
`D1=1, D2=2, D3=0, D4=0, D5=1, D6=1, D7=0` → (3·1 + 2·2 + 2·1 + 2·1)/26 = (3+4+2+2)/26 = 11/26 = **42%**

Re-scoring carefully against the rubric: D1 heterogeneous heads = 1 (R2 has dual heads but the paper itself is single-task detection → partial via R2's use); D2 mental-health/crisis = 2 (scored against R2's deployment, which is suicide-risk — the loss is *in* that pipeline); D3 emotion corpora = 0; D4 teacher-LLM distillation = 0; D5 principled loss balancing = 1 (focal is a loss-reshaping/weighting mechanism, partial); D6 safety-recall constraint = 1 (focal raises minority recall, the mechanism R2 leans on, but it is not a hard floor); D7 encoder backbone = 0 (CNN detector).
→ (3·1 + 2·2 + 0 + 0 + 2·1 + 2·1 + 0)/26 = 11/26 = **42% (adjacent).**
- **Closest on:** D2 (the loss already lives in R2's suicide-risk pipeline) and D5/D6 (it is the imbalance-handling mechanism R2 depends on for minority recall).

## Best point — Framing / citation anchor + tunable knob
This is **the canonical citation for the focal-loss term R2 already runs**, and γ is a **free, untuned hyperparameter** (R2 inherited γ=2, the detection default) that directly controls hard-example emphasis on R2's collapsed **Behavior** class.
- **How to apply to Pebble:** Cite Lin et al. 2017 for R2's `w_focal·FL` term, then **sweep γ and `w_focal`** to push Behavior F1 above its 0.183 floor — γ=2 is a detection default, not a value validated on R2's 5-class ordinal problem.

## ▶ Apply to R2
**Confirmed: R2's `focal_loss` matches the paper exactly.** R2 implements
`(-a * (1 - p_y) ** gamma * logp_y).mean()` with `a = alpha[y]` — i.e. `−α_y (1 − p_y)^γ log p_y`, the **α-balanced focal loss of Eq. in §3.1**. `alpha=inverse-freq` (R2) is the class-balanced choice; `focal_gamma=2.0` is the paper's RetinaNet default; `w_focal=0.2` is R2's weight in the tri-objective `0.5·CORAL + 0.3·CE + 0.2·Focal`. Lines: `focal_loss()` at `r2-suicide-risk-dualhead.py:362`; `focal_gamma`/`w_focal` in `Config` at lines 87/89; combined at line 451.

Recommended changes (all are Config knobs — no architecture change):
1. **Sweep `focal_gamma`** ∈ {0, 1, 2, 3, 5}. γ↑ pushes more gradient onto hard examples; Behavior is the hardest/most-confused class, so γ=3 or 5 may recover recall there. γ=0 is the ablation that reduces focal to weighted CE.
2. **Sweep `w_focal`** ∈ {0.0, 0.1, 0.2, 0.4} (renormalize the other two weights). w_focal=0.0 is the **±focal ablation** the plan calls for; raising it gives the focal term more say versus CORAL/CE.
3. **Consider a class-balanced α** instead of raw inverse-freq — the effective-number reweighting of **paper 50 (Cui et al., Class-Balanced Loss, CB-Focal)** is the principled successor to inverse-freq α and pairs directly with this focal term; cross-link 50 ↔ 51 when reporting.
4. **Decouple γ per-objective** is *not* recommended yet — keep one γ; the tri-objective already mixes CORAL (ordinal) + CE, so over-tuning focal risks fighting CORAL on adjacent-class structure.

## ▶ Kaggle experiment
**Grid (cheap — Config-only, reuses the dual-head kernel):**
- **Arm A (±focal ablation, plan-mandated):** `w_focal ∈ {0.0, 0.2}` at γ=2, holding `w_coral`/`w_ce` (renormalize when w_focal=0). Isolates whether the focal term helps at all vs Run B.
- **Arm B (γ sweep):** `focal_gamma ∈ {0, 1, 2, 3, 5}` at fixed `w_focal=0.2`. γ=0 collapses to α-weighted CE (a second read on the ablation).
- **Arm C (w_focal sweep):** `w_focal ∈ {0.1, 0.4}` at γ=2 (the {0.0, 0.2} points come from Arm A).
- **Optional Arm D:** swap inverse-freq α → CB effective-number α (paper 50) at the best (γ, w_focal).

**Primary signal:** per-class **gold Behavior F1** (current 0.183, the bottleneck) and **gold macro-F1** (current 0.3849, Run B). Watch for the focal-vs-CORAL trade-off: higher γ may lift Behavior recall while degrading adjacent-class ordinal accuracy — report **per-class F1 + QWK/MAE**, not macro-F1 alone. Use the existing within-dist CV harness for CIs; a single fold's Behavior F1 (small support) is high-variance.

**Cost:** one fine-tune per cell; ~9 cells (2 + 5 + 2) ≈ within a few Kaggle GPU sessions if Arms reuse warm-started checkpoints. Config-only edits → no code risk.

## Caveats
- **Focal helps hard-but-correctly-labeled examples; it can amplify label noise.** The modulating factor `(1−p_t)^γ` puts *more* weight on low-confidence examples — which includes **mislabeled** ones. R2's labels are single-LLM silver (W4); raising γ may make R2 over-fit Gemini's Behavior-class errors rather than learn the class. This directly couples the W1 (Behavior collapse) and W4 (single-LLM labels) weaknesses — if Behavior labels are themselves noisy, more focal is the wrong lever and label denoising (cf. paper 14 MC-Dropout soft labels) is the right one. Run the γ sweep *and* inspect Behavior false positives before trusting a high-γ win.
- **Domain transfer is by analogy.** The paper is object detection (background-vs-foreground anchor imbalance, ~1:1000), not 5-class ordinal text. The mechanism transfers (R2 already uses it), but the γ=2 default has no validation on R2's regime — hence the sweep.
- **α and γ interact** — the paper notes optimal α drops as γ rises (γ=2 pairs with α=0.25 there). R2's α is inverse-freq, not a tuned scalar, so the joint (α-scheme, γ) interaction is untested; the optional Arm D (CB-α) probes this.
- **Verification status:** title/authors/ICCV-2017 venue/page range VERIFIED via CVF + reference records; formula VERIFIED against R2 source (`focal_loss():362`). "Best Student Paper" and TPAMI-2020 journal-extension details are widely reported but not re-confirmed line-by-line in this session — treat the award line as high-confidence-but-unverified-here.
