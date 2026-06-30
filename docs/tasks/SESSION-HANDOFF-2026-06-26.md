# Session handoff — 2026-06-26 (R2 text stream: papers + Kaggle runs)

> Single-file progress summary so the session can be cleared and resumed cold. Read top-to-bottom.
> Living tracking docs (source of truth, keep using these): `r2-finetuning-methods-for-ieee.md`,
> `r2-beat-paper-dual-report.md`, `emotional-tone-papers.md` (all in `docs/tasks/`).

## Headline results (DONE this session)
- **R2 beat the paper (clean number):** within-distribution 5-fold CV macro-F1 = **0.6530 ±0.0048 > paper 0.5098**
  (+0.143, +28%). Loaded the full **10,072** sequences (the old Zenodo-392 mount bug is fixed via recursive glob).
- **Ablation surprise:** plain **flat-CE** (no CORAL/Focal) gold macro-F1 = **0.4215 > dual-head 0.3849**, and it
  **rescues Behavior** (per-class F1 0.183 → **0.285**). The tri-objective is *underperforming* CE on gold.
  ⚠ One seed/one run — confirm with a CORAL-only arm + a seed repeat before rewriting the ordinal-contribution claim.
- **Run B (dual-head, gold + rebalance):** gold macro-F1 0.3849, QWK 0.398, MAE 0.822 (baseline was 0.3569).
- Canonical report (md+html, in sync): **`docs/reports/r2-ab-results.{md,html}`**.

## Three work streams this session

### 1. R2 finetuning-methods for IEEE  → `docs/tasks/r2-finetuning-methods-for-ieee.md` (status: done)
- Analyzed **12 famous fine-tuning papers (42–53)** across 4 families (PEFT · weak-sup/distill · ordinal/imbalance ·
  MH-SOTA), each a per-paper dossier in `docs/papers/finetuning-message/` ending with `▶ Apply to R2` + `▶ Kaggle experiment`.
- Combined HTML: **`docs/reports/r2-finetuning-methods.html`**.
- Key finding: R2's Behavior bottleneck is **label-quality**, so label-centric methods (45 Snorkel, 46 Confident
  Learning, 47 Distillation) out-rank imbalance/PEFT tweaks. 3-tier run-next roadmap is in the tracking doc.

### 2. Kaggle unblock + runs  → `docs/tasks/r2-beat-paper-dual-report.md`
- **Account switched to `phatneurondai`** (phone-verified — GPU Tesla P100 + Internet both work; the prior
  `pathnguyen` was NOT verified → kernels died at pip install). Dataset re-uploaded: `phatneurondai/r2-cssrs-combined-10k`.
- **Run A** (`r2-within-dist-cv-10k-balanced`) ✅ complete → 0.653 (above).
- **flat-CE ablation** (`r2-ablation-flatce`) ✅ complete → 0.4215 (above).
- **Tier-1 cleanlab kernel BUILT + smoke-validated but NOT yet run** (was blocked by the 2-concurrent-GPU cap):
  `kaggle/finetuning-message/r2-tier1-cleanlab/` — modes `R2_CL=diagnostic|drop|downweight`. Diagnostic ~4h, cap-safe.

### 3. Emotional-tone (positive↔negative) papers  → `docs/tasks/emotional-tone-papers.md` (status: done)
- **16 papers found + saved:** `docs/papers/related-work-emotional-tone.md`.
- **Top-4 scored** (analysis-paper dossiers 54–57): 54 VADEC (38%), 55 CLPsych 2025 (54%), 56 MentaLLaMA (42%),
  57 Mitsios valence-ordinal (35%).
- **Datasets:** IMHI ✅ downloaded (19,051 labeled test rows, MIT) → `data/finetuning-message/external/imhi/`
  (best for safety head: `swmh` 10,882 5-class + `t-sid` suicide/self-harm). CLPsych ⛔ gated (DUA, 2025 reg closed) →
  access steps drafted in `data/finetuning-message/external/clpsych-2025/ACCESS-REQUEST.md` (research-only).
- README index updated with 54–57.

## Environment & gotchas (carry forward)
- **Kaggle CLI** auths from `~/.kaggle/access_token` (raw `KGAT_` token), NOT kaggle.json. Current account
  `phatneurondai`. **Max 2 concurrent GPU sessions**; weekly quota ≈30h P100. Pin `torch==2.5.1+cu121` (P100=sm_60;
  base-image torch 2.10 is incompatible). Datasets/kernels are account-scoped. Recursive glob `**/sequences.csv` for
  the deep mount path. (All saved in memory `kaggle-run-needs-token`.)
- **Code changes made (kaggle dualhead kernel + notebook mirror):** loss weights are now env-gated
  (`R2_W_CORAL/R2_W_CE/R2_W_FOCAL/R2_FOCAL_GAMMA`) and `evaluate` blends only trained heads (valid ablation).
  `train_fold` gained a `sample_weight=` hook (for cleanlab down-weight). Defaults unchanged.
- `cleanlab>=2.6` was pip-installed into `.venv-voice` (for local smoke). Uninstall if undesired.
- ⚠ **Do NOT commit** the `kaggle/**/out/best_model.pt` files (~595 MB each).

## Next actions (2 GPU slots are now FREE)
1. **Push CORAL-only ablation** — `R2_W_CORAL=1 R2_W_CE=0 R2_W_FOCAL=0`, gold-holdout, to complete the §4 ablation
   table and explain the flat-CE finding. (Use a new kernel dir or re-version `r2-ablation` with the env block changed.)
2. **Push Tier-1 cleanlab diagnostic** — `kaggle kernels push -p kaggle/finetuning-message/r2-tier1-cleanlab`
   (defaults to `R2_CL=diagnostic`, ~4h). Answers IEEE gap #1: "how many Behavior labels does cleanlab distrust?".
   Then `drop`/`downweight` arms.
3. After CORAL-only completes: pull logs, fold numbers into `docs/reports/r2-ab-results.{md,html}` §4.
4. Lower-priority: a seed-repeat of flat-CE to confirm; Snorkel multi-LF (45) + LLM soft-target distillation (47);
   `load_imhi_eval()` to use IMHI swmh/t-sid as an OOD eval for the safety head.

## How to resume Kaggle (pull a finished run)
```
kaggle kernels status phatneurondai/<kernel-slug>
kaggle kernels output phatneurondai/<kernel-slug> -p kaggle/finetuning-message/<dir>/out
```
Result markers in the log: `>>> CV macro-F1: mean=...` (within-dist) · `>>> GOLD test macro-F1: mean=...` (gold-holdout)
· `>>> CONFIDENT JOINT` + per-class flag rates (cleanlab diagnostic).
