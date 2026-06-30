# R2 text paper — finetuning methods from famous papers (→ IEEE)

- **Slug:** r2-finetuning-methods-for-ieee
- **Status:** done
- **Created:** 2026-06-25  ·  **Updated:** 2026-06-25
- **Owner:** Fabio / Claude

## Goal
Read the R2 text-training results, then research **how famous papers do fine-tuning** across four families
(PEFT recipes · weak-supervision/LLM-labeling/distillation · ordinal+imbalance · mental-health SOTA),
**analyze each paper one by one** into a per-paper `.md` (storage) plus **one combined HTML** (display), and
turn each analysis into a **concrete, prioritized "apply this to R2 + Kaggle experiment to run next"**. The
end state is an actionable experiment roadmap that pushes the R2 text paper toward an IEEE submission.

## Requirements & Constraints
- **Functional:** per-paper `.md` in `docs/papers/finetuning-message/` (match existing 01–23 format); one
  combined HTML report in `docs/reports/`; every analysis ends with an actionable R2 mapping + Kaggle run.
- **Constraints (locked with user 2026-06-25):**
  - Families: **all 4** (PEFT recipes · weak-sup/LLM-label/distill · ordinal+imbalance · mental-health SOTA).
  - Output: **per-paper md + one combined HTML**.
  - Objective: **actionable** — pick techniques to run next (not just related-work prose).
- **Numbering:** new papers continue the global sequence at **42+** (01–23 text, 24–41 voice already taken).
- **Surgical:** reference existing papers (ULMFiT 20, RecAdam 21, MentalBERT 12, PGKD 13, Emo Pillars 04,
  LLM-CSSRS 16, MTL-imbalance 11, CSSRS 14–17) instead of duplicating; only add genuinely-missing famous papers.
- **Non-goals:** running the Kaggle experiments themselves this round (blocked on `pathnguyen` phone-verify per
  `r2-beat-paper-dual-report.md`); this round produces the *plan + analyses*, not new training numbers.

## R2 context (the baseline these analyses target)
- **Task:** ordinal 4-level C-SSRS suicide risk (Indicator/Ideation/Behavior/Attempt) from Reddit post sequences.
- **Model:** Hierarchical dual-head (post-encoder MentalRoBERTa mirror → 3-layer seq-transformer → attn-pool →
  CORAL head + CE head), tri-objective loss (0.5·CORAL + 0.3·CE + 0.2·Focal), freeze 6 encoder layers, max_len 256.
- **Results (Run B, gold-holdout + balance):** gold macro-F1 **0.3849** (baseline 0.3569), QWK 0.398, MAE 0.822,
  val-on-LLM (within-dist proxy) 0.666 > paper 0.5098. Per-class gold F1: Indicator 0.502 · Ideation 0.480 ·
  **Behavior 0.183 (bottleneck)** · Attempt 0.374.
- **Known levers / weaknesses:** (1) Behavior collapse = LABEL-QUALITY (634 noisy LLM labels), (2) gated encoder
  not used (mirror only) + max_len 256 truncation, (3) Δt=0 temporal head unused, (4) single-LLM labels (no κ).
- **Paper plan & gap list:** `docs/papers/finetuning-message/PAPER-PLAN-text-ordinal-suicide.md`.

## Candidate paper set (existing = reference; new = analyze)
**Family A — PEFT / fine-tuning recipes**
- exists: 20 ULMFiT (gradual unfreeze + discriminative LR + STLR), 21 RecAdam (anti-forgetting).
- NEW: **42 LoRA**, **43 Adapters (Houlsby)**, **44 BitFit**.

**Family B — Weak-sup / LLM-labeling / distillation**
- exists: 04 Emo Pillars (LLM teacher), 13 PGKD (LLM distillation), 16 LLM-CSSRS screening.
- NEW: **45 Snorkel (data programming)**, **46 Confident Learning / cleanlab**, **47 Knowledge Distillation (Hinton)**.

**Family C — Ordinal + imbalance**
- exists: 11 MTL-imbalance-revisit, 14 CSSRS-label-smoothing.
- NEW: **48 CORAL**, **49 CORN**, **50 Class-Balanced Loss (Cui)**, **51 Focal Loss (Lin)**.

**Family D — Mental-health / suicide-risk SOTA**
- exists: 12 MentalBERT, 15 CSSRS-hybrid, 16/17 CSSRS systems.
- NEW: **52 STATENet (Sawhney)**, **53 Yates et al. 2017 (self-harm risk in forums)**.

## Milestones
- [x] M0 — Read R2 results + code + existing paper plan; lock scope with user
- [x] M1 — Assemble candidate paper list (existing vs new), numbering 42+
- [x] M2 — Analyze each NEW paper (parallel agents) → per-paper `.md` (42–53), each ending with actionable R2 + Kaggle experiment
- [x] M3 — Synthesis: prioritized "run-next" experiment roadmap (rank techniques by ROI vs R2 weaknesses)
- [x] M4 — Combined HTML report (display) covering all analyses + the roadmap + IEEE-gap mapping
- [x] M5 — Update README index + cross-link from PAPER-PLAN; close out

## Decision Log
<!-- newest first -->
- **2026-06-25 — New papers numbered 42+ (global sequence):** 01–23 (text) and 24–41 (voice) are taken; continue
  globally to avoid collisions. Rejected: re-using 24+ inside the text folder (collides with voice global index).
- **2026-06-25 — Reference, don't duplicate, the 9 already-covered finetuning papers:** ULMFiT/RecAdam/MentalBERT/
  PGKD/Emo-Pillars/LLM-CSSRS/MTL-imbalance/CSSRS-14–17 already have dossiers; only add the 12 genuinely-missing
  famous papers. Keeps the round surgical and the combined HTML focused on net-new technique coverage.
- **2026-06-25 — Scope locked with user:** all 4 families · per-paper md + one combined HTML · actionable objective
  (each analysis → concrete R2 change + a Kaggle experiment). Drives a "run-next" roadmap rather than prose.
- **2026-06-25 — Each per-paper md ends with two mandatory blocks:** (1) "Apply to R2" (exact code/config change,
  referencing `r2-suicide-risk-dualhead.py` knobs), (2) "Kaggle experiment" (env flags + expected signal). This is
  what makes the round actionable per the user's objective.

## Open Questions
<!-- none blocking; established techniques + named papers. Agents will surface any per-paper uncertainty. -->

## Research Findings
<!-- per-paper agent output folds in here as analyses land -->
Each row = one analysis-paper agent's verdict (full dossier in `docs/papers/finetuning-message/NN-*.md`).
`ROI` = agent's 1–5 estimate of value-for-R2. `W` = R2 weakness targeted.

| # | Paper | Family | Targets | Technique (one line) | Kaggle experiment | ROI |
|---|-------|--------|:------:|----------------------|-------------------|:--:|
| 42 | LoRA (ICLR 2022) | A PEFT | W2 | Low-rank ΔW=(α/r)BA on q/v, freeze W₀ | `R2_LORA=1` vs freeze-6, same gold split | 2 |
| 43 | Adapters / Houlsby (ICML 2019) | A PEFT | W2 | Bottleneck adapter per layer, ~3.6% params | `R2_ADAPTER=1` vs freeze-6 | 2 |
| 44 | BitFit (ACL 2022) | A PEFT | W2/overfit | Train bias terms only (~0.09% params) | `R2_FREEZE_MODE∈{layers,bitfit,bitfit-min}` | 3 |
| 45 | **Snorkel** (VLDB 2017/2020) | B weak-sup | **W4+W1** | Multi-LF + LabelModel → denoised soft labels | single-LLM vs majority-vote vs LabelModel soft | **4** |
| 46 | **Confident Learning** (JAIR 2021) | B label-noise | **W1** | Confident-joint → prune/reweight mislabels | ±cleanlab-pruned pool (uses existing OOF probs) | **4** |
| 47 | **Knowledge Distillation** (Hinton 2015) | B distill | **W4+W1** | Temperature soft targets + KL; "dark knowledge" | hard CE vs conf-spread vs LLM-logprob soft targets | **4** |
| 48 | **CORAL** (Pat.Rec.Lett 2020) | C ordinal | W1/cite | Shared-weight K−1 binary thresholds (rank-monotone) | flat-CE vs CORAL-only vs dual-head ablation | **4** |
| 49 | **CORN** (Pat.Anal.Appl 2023) | C ordinal | **W1** | Conditional-prob thresholds, NO weight share (more expressive) | `R2_ORDINAL_HEAD=coral\|corn` | **4** |
| 50 | Class-Balanced Loss (CVPR 2019) | C imbalance | W1 | Reweight by effective number (1−β^n)/(1−β) | inverse-freq vs eff-num β∈{.99,.999,.9999} | 3 |
| 51 | **Focal Loss** (ICCV 2017) | C imbalance | W1/cite | (1−p_t)^γ down-weights easy examples | ±focal + γ∈{0,1,2,3,5} + w_focal sweep | **4** |
| 52 | STATENet (EMNLP 2020) | D MH-SOTA | W3/framing | Time-aware transformer on real inter-post Δt | ±real-Δt (only if timestamps recoverable) | 2 |
| 53 | Yates et al. (EMNLP 2017) | D MH-SOTA | framing | User-level CNN + ordinal-margin loss; RSDD corpus | cheap CNN baseline floor for IEEE table | 2 |

### Synthesis — the decisive finding
R2's headline weakness (Behavior gold-F1 0.183) was already diagnosed in `r2-ab-results.md` as a **label-quality**
problem (634 mostly-LLM, noisy Behavior samples), **not** a sampling/loss problem — rebalancing already helped
globally but left Behavior flat. The 12 analyses confirm this from the method side: **every imbalance/PEFT lever
(42–44, 50) is ROI-capped by the label ceiling**, while the three top-ROI levers (45 Snorkel, 46 Confident Learning,
47 Distillation) all attack the label noise (W4) at its source — which is *also* the IEEE gap-list's #1 item
(quantify LLM-label quality: κ vs gold). The ordinal-head pair (48 CORAL verify + 49 CORN upgrade) and 51 Focal are
the cheap, plan-mandated ablations that produce the contribution-separating tables IEEE reviewers expect.

## Run-next experiment roadmap (M3)
Ordered by ROI × cost, mapped to R2 weaknesses and the IEEE gap-list. All runs are blocked on the Kaggle
GPU/Internet access issue (`pathnguyen` phone-verify, see `r2-beat-paper-dual-report.md`); this is the *plan*.

**Tier 1 — attack the label ceiling (highest ROI; also closes IEEE gap #1).**
1. **Confident Learning (46)** — reuse R2's existing 5-fold OOF probs → `cleanlab.find_label_issues` on the pool
   (esp. Behavior) → retrain ±pruned/down-weighted. Near-zero added compute; directly tests "is Behavior noise?".
2. **Snorkel multi-LF relabel (45)** — convert the single-LLM labeler into ≥3 LFs (2–3 LLM prompts + 1 lexicon),
   fit a LabelModel → soft labels + per-LF κ. Yields the κ-vs-gold number IEEE gap #1 demands. Mostly offline cost.
3. **LLM soft-target distillation (47)** — re-query the teacher for class distributions / use confidence spread;
   swap the hard-CE term for a temperature-KL term. Free "conf-spread" first cut; logprob variant needs one re-query.

**Tier 2 — contribution-separating ablations (cheap, plan-mandated, paper-table fillers).**
4. **Ordinal-head ablation (48)** — flat-CE vs CORAL-only vs dual-head via `w_coral/w_ce/w_focal` env; report
   QWK/MAE/adjacent-error. Also audit R2's CORAL rank-monotonicity (bias ordering + non-negative probs).
5. **CORN upgrade (49)** — `R2_ORDINAL_HEAD=corn` drop-in vs CORAL; watch QWK + Behavior adjacent error.
6. **Focal sweep (51)** — ±focal and γ∈{0,1,2,3,5} + w_focal; the plan's ±focal ablation. NB: high γ amplifies
   mislabels → run *after* Tier 1 denoising, else it fights W1.
7. **Class-Balanced α (50)** — effective-number reweight (β grid) vs inverse-freq; expect a small, defensible bump.

**Tier 3 — PEFT recipes (low headline ROI; clean methodology/robustness story).**
8. **BitFit / Adapters / LoRA (44/43/42)** — one PEFT arm vs freeze-6; main payoff is disambiguating W1 (label)
   from W2 (encoder capacity): if PEFT doesn't move Behavior, that's positive evidence the bottleneck is labels.

**Framing-only (no run, or cheap baseline).**
9. **STATENet (52)** — Δt=0 is a genuine data limitation; justify in Limitations + cite (Path B). Only wire real
   Δt if timestamps are recoverable.
10. **Yates (53)** — cite as user-level + ordinal-loss precedent; optionally a pre-transformer CNN baseline-floor row.

**Sequencing rule:** run Tier 1 first (denoise), *then* Tier 2 (so focal/ordinal tune on clean labels), Tier 3 last.

## Completed Work
- 2026-06-25 — M0: read `docs/reports/r2-ab-results.md`, `notebooks/r2-suicide-risk-dualhead.py`,
  `PAPER-PLAN-text-ordinal-suicide.md`, `FAMOUS-cited-papers-vi.md`; confirmed Run B 0.3849 / Behavior 0.183.
- 2026-06-25 — M1: assembled candidate set (9 existing references + 12 new papers 42–53 across 4 families).
- 2026-06-25 — M2: 12 parallel `analysis-paper` agents wrote per-paper dossiers `42-lora` … `53-yates-2017`
  in `docs/papers/finetuning-message/`, each with `▶ Apply to R2` + `▶ Kaggle experiment` blocks + verified citations.
- 2026-06-25 — M3: ranked techniques into the 3-tier run-next roadmap above; key finding = label-quality (Tier 1)
  dominates because R2's Behavior bottleneck is noise, not sampling.

## Execution log — 2026-06-25 (Kaggle unblocked, runs launched)
- **Account unblocked:** user supplied phone-verified `phatneurondai`. Probe kernel confirmed GPU (Tesla P100)
  + Internet both work. Re-uploaded dataset `phatneurondai/r2-cssrs-combined-10k`. (memory `kaggle-run-needs-token` updated.)
- **Run A launched** (within-dist CV vs paper 0.5098): `phatneurondai/r2-within-dist-cv-10k-balanced` v1, RUNNING (~9h).
- **Tier-2 code ready + verified:** env-gated loss weights `R2_W_CORAL/R2_W_CE/R2_W_FOCAL/R2_FOCAL_GAMMA` +
  head-aware eval blend (only blends trained heads → valid ordinal ablation), in both
  `kaggle/finetuning-message/r2-suicide-risk-dualhead/r2-suicide-risk-dualhead.py` and the notebook mirror.
  CPU smoke passed for flat-CE and CORAL-only arms.
- **Tier-2 first arm launched:** flat-CE ablation `phatneurondai/r2-ablation-flatce` v1, RUNNING (~9h) — isolates
  "ordinal CORAL machinery vs plain CE" on the same gold-holdout protocol.
- **Quota note:** Run A + flat-CE ≈ 18h of the ~30h weekly P100 quota. Account allows ≥2 concurrent GPU sessions.
  Remaining ablation arms (CORAL-only, dual-head=baseline 0.3849, focal γ sweep) and Tier-1 should be sequenced
  as quota frees — do NOT push all at once.

## Results in (2026-06-26, pulled from phatneurondai)
- **Run A within-dist CV = 0.6530 ±0.0048 > paper 0.5098 (+0.143).** Loaded full 10,072 (mount fix worked). ✅ beat-paper clean number.
- **flat-CE ablation gold macro-F1 = 0.4215 ±0.024 > dual-head 0.3849**; Behavior 0.285 > 0.183. ⚠ **Surprise: plain CE
  beats the full tri-objective on gold and rescues Behavior** → CORAL+Focal may overfit the LLM-label distribution.
  → NEXT: run CORAL-only arm + a seed repeat to confirm before rewriting the ordinal-contribution claim. Folded into
  `docs/reports/r2-ab-results.md` §4 + §3 verdict.

## Remaining Action Items
- [x] Run A completed + recorded (0.653 vs 0.5098); flat-CE completed + recorded (0.4215 vs 0.3849).
- [ ] Push remaining Tier-2 arms (CORAL-only `R2_W_CORAL=1,R2_W_CE=0,R2_W_FOCAL=0`; focal γ sweep) as quota frees.
- [x] **Tier-1 cleanlab BUILT + validated (2026-06-25):** new kernel
  `kaggle/finetuning-message/r2-tier1-cleanlab/r2-tier1-cleanlab.py` — modes `R2_CL=diagnostic|drop|downweight`,
  OOF probs at `R2_CL_OOF_EPOCHS` (default 4) piggybacking the CV, `cleanlab.find_label_issues` + confident-joint
  report (per-class flag rates, esp. Behavior=W1), drop/down-weight retrain on cleaned pool + untouched-gold eval.
  All 3 modes pass CPU smoke. `train_fold` gained a backward-compatible `sample_weight=` hook for down-weighting.
  - **Launch blocked on the 2-concurrent-GPU cap** — push #3 rejected ("Maximum batch GPU session count of 2").
    Will push `phatneurondai/r2-tier1-cleanlab-diag` (diagnostic, ~4h, cap-safe) as soon as Run A or flat-CE frees a slot.
- [ ] Push remaining Tier-1 arms (`R2_CL=drop`, `R2_CL=downweight`) after the diagnostic.
- [ ] Then Snorkel multi-LF relabel (45) + LLM soft-target distillation (47).
