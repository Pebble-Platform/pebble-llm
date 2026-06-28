# Paper 46 — Confident Learning: Estimating Uncertainty in Dataset Labels

> Family B (weak-supervision / label-noise) · Depth: abstract + venue page + cleanlab docs. Compiled 2026-06-25.

## Bibliographic info
- **Authors / Year / Venue:** Curtis G. Northcutt, Lu Jiang, Isaac L. Chuang. **JAIR 2021**, Vol. 70 (published 2021-04-14).
- **Link:** [arXiv:1911.00068](https://arxiv.org/abs/1911.00068) (v6, 2022-08-22) · [JAIR view/12125](https://jair.org/index.php/jair/article/view/12125) · DOI [10.1613/jair.1.12125](https://doi.org/10.1613/jair.1.12125) — **VERIFIED** (title/authors/vol/year/DOI confirmed on the JAIR page; arXiv id confirmed).
- **cleanlab repo:** [github.com/cleanlab/cleanlab](https://github.com/cleanlab/cleanlab) (`from cleanlab.filter import find_label_issues`). Open-source reference implementation of every result in the paper.
- **R2 pillar:** weak-supervision / label-noise cleaning — the lever for W1 (Behavior collapse driven by noisy single-LLM labels). Methodology-grade for the "honest gold-holdout under noisy training labels" story in PAPER-PLAN-text-ordinal-suicide.md.

## Summary
Confident Learning (CL) is a **model-agnostic, theoretically-consistent** framework for finding label errors from a classifier's *out-of-sample* predicted probabilities. It assumes a **class-conditional noise process** and, instead of trusting argmax, **counts** examples into a `K×K` "confident joint" `Q̂` using **per-class average self-confidence thresholds** `t_j = mean predicted prob of class j over examples labeled j` — an example counts toward true-class `k` only when its `p(k) ≥ t_k`. Normalizing `Q̂` estimates the joint distribution of noisy (given) vs. latent (true) labels; off-diagonal mass localizes systematic mislabeling. CL then **prunes / ranks-and-prunes** the flagged examples (e.g. `prune_by_noise_rate`, or rank by self-confidence / normalized margin) so a model can be retrained on the cleaned set or with the bad examples down-weighted. It beat seven noisy-label baselines on CIFAR and generalized across MNIST, ImageNet, and Amazon-Reviews **text** sentiment — the same probabilistic interface R2 already produces.

## Overlap with Pebble/R2 — 27% (peripheral)
`D1=1, D2=0, D3=0, D4=2, D5=0, D6=0, D7=0` → (3·1 + 2·2)/26 = 7/26 = **27%**
- **Closest on:** D4 (teacher/LLM silver-label noise — CL is *exactly* a method to clean single-source noisy labels) and partial D1 (R2 is multi-head ordinal, but CL itself is single-task and head-agnostic).
- **Band note:** the % is low because CL touches none of Pebble's MTL/emotion/safety-recall/encoder dimensions — but it scores a full **2 on the one dimension that is R2's current bottleneck** (W1 label quality). For R2 specifically the leverage is far higher than 27% suggests; the rubric measures breadth of overlap, not bottleneck-fit.

## Best point — Method to adopt
A **drop-in, model-agnostic label-error detector** that consumes exactly what R2's CV already emits — out-of-fold predicted class probabilities — and returns a boolean mask of likely-mislabeled training examples, per class, with **no extra training and no hyperparameters** (thresholds are data-derived).
- **How to apply to Pebble:** run `find_label_issues` on the **noisy LLM-labeled pool** using R2's 5-fold out-of-fold probabilities (it already computes `coral_to_probs`), focus on the **Behavior** class (634 noisy labels, F1 0.183), then **drop or down-weight** the flagged Behavior examples before the final training pass.

## ▶ Apply to R2 (mandatory)
R2 already has every input CL needs; this is a wiring job, not new modeling.

**Pipeline (exact hooks in `kaggle/finetuning-message/r2-suicide-risk-dualhead/r2-suicide-risk-dualhead.py`):**

1. **Collect out-of-fold (OOF) probabilities over the pool.** In `run_gold_holdout`, the `StratifiedKFold.split(p_seq, p_lab)` loop already trains a model per fold and leaves the held-out **validation** slice of the *pool* unseen. Add: after `train_fold` returns `state`, rebuild the fold model and run `evaluate`-style inference over that fold's **`va_seq` (pool-validation)** rows, writing the 4-class probability vector `p_final = 0.5·coral_to_probs + 0.5·softmax(cls)` into a pre-allocated `oof_probs[N_pool, 4]` array indexed by `va_idx`. After 5 folds every pool example has one genuinely out-of-sample probability vector — the CL-correct input (CL requires OOF probs to avoid self-confidence leakage).
   - Note: `evaluate` currently returns only metrics; factor a thin `predict_proba(model, loader)` helper (returns the stacked `p_final`) so both `evaluate` and this OOF pass reuse it.
2. **Run CL once on the pool.** `from cleanlab.filter import find_label_issues; issues = find_label_issues(labels=p_lab, pred_probs=oof_probs, return_indices_ranked_by="self_confidence", filter_by="prune_by_class")`. Slice to Behavior: `behavior_issues = [i for i in issues if p_lab[i] == 2]`. Log counts per class (expect the heaviest off-diagonal mass on Behavior↔Ideation / Behavior↔Attempt — the confusions seen in the gold per-class F1).
3. **Clean, two variants (one flag, `R2_CL`):**
   - **Drop:** `keep = np.setdiff1d(np.arange(len(p_lab)), issues)`; filter `p_seq, p_lab` before the *final* fold loop (or before re-fitting on all pool data).
   - **Down-weight:** keep all rows but multiply their `WeightedRandomSampler` weight by a factor (e.g. 0.0–0.3) for flagged rows — hook into the `cfg.balance` branch of **`train_fold`** where `w = (counts.sum()/...)[tr_lab]` is built; element-wise scale `w[flagged_in_fold] *= cl_weight`. This preserves class balance while suppressing suspect Behavior labels.
4. **Re-train + re-eval on the *unchanged* clinical gold (CSSRS-500).** Gold is never touched by CL (CL only cleans the noisy *training* pool), so the gold macro-F1 / per-class-F1 comparison stays honest and directly tests W1.

**Where it lives:** OOF collection + CL call in `run_gold_holdout`; down-weight path in `train_fold`'s sampler block; new env flag `R2_CL` ("off"/"drop"/"downweight") in `Config`.

## ▶ Kaggle experiment (mandatory)
- **Goal:** does pruning/down-weighting the worst LLM-labeled Behavior examples lift the Behavior bottleneck without hurting other classes?
- **Env/config:** same kernel, GPU + Internet ON. Add `pip install cleanlab` to the §0 pin block (pure-python, sklearn-only dep — negligible). Run B settings unchanged: `R2_GOLD_HOLDOUT=1 R2_BALANCE=1 R2_EPOCHS=10`, `seed=42`, identical NeoBERT/MentalRoBERTa-mirror backbone, identical folds.
- **Arms / ablation rows (hold everything else fixed):**
  | Arm | `R2_CL` | Description |
  |-----|---------|-------------|
  | A (baseline) | off | Run B as-is — gold macro-F1 0.3849; Behavior F1 0.183 |
  | B | drop | drop CL-flagged pool examples (all classes), re-train |
  | C | downweight | keep rows, ×0.2 sampler weight on flagged rows |
  | D (diagnostic) | off + log | run CL, **report** flagged counts/joint per class but train on full pool (sanity: how many Behavior labels does CL distrust?) |
- **Expected signal:** Behavior F1 ↑ and macro-F1 ↑ if Behavior noise is real and class-conditional; near-flat MAE/QWK (CL targets categorical mislabels). Watch the **count** — if CL flags a huge fraction of the 634 Behavior labels, that is itself the paper's W1 evidence even if F1 barely moves. Report per-class flag rates as a table for the IEEE submission.
- **Cost:** **~zero extra compute** for the CL step (one sklearn-free numpy pass over `[N_pool,4]`). The only added cost is the OOF inference pass over pool-validation slices (already loaded per fold) + the re-train arms (~1 extra Run-B-length run per arm, i.e. the normal 5-fold cost ×3). No new GPU stack.

## Caveats
- **Needs probabilistic, out-of-sample predictions.** R2 produces probs (`coral_to_probs` + softmax), but they must be **OOF** (held-out fold), not training-set probs, or self-confidence leaks and CL under-flags. The wiring in step 1 is load-bearing.
- **Ordinal vs. flat.** CL is built for **nominal** class-conditional noise; it has no notion of ordinal distance (a Behavior→Attempt mislabel is "closer" than Behavior→Indicator). It will still flag both, but the joint `Q̂` treats classes as unordered — acceptable for *finding* errors, but don't read the off-diagonal as ordinal severity. (Northcutt's later regression-error work exists if an ordinal-aware variant is wanted; out of scope here.)
- **Class-conditional noise assumption.** CL assumes label noise depends only on the true class, not on features. Single-LLM labeling errors that are *content-dependent* (e.g. the LLM systematically mis-reads sarcasm) violate this; CL may then miss or over-flag. Treat results as a strong prior, not ground truth — spot-check a sample of flagged Behavior posts by hand for the paper.
- **Pool size / small-class fragility.** With only 634 Behavior labels, per-class thresholds `t_2` are estimated on few examples; flagged set may be noisy. Prefer the **down-weight** arm over hard **drop** for Behavior to avoid shrinking an already-tiny class.
- **Verification status:** citation, venue (JAIR vol 70, 2021), DOI, arXiv id, and cleanlab API VERIFIED via JAIR page + arXiv + cleanlab docs. Method mechanism is from the abstract + venue summary + cleanlab docs, not a full-PDF line read — exact threshold/pruning equations (`Q̂` normalization variants, `prune_by_noise_rate` vs `prune_by_class`) should be confirmed against §2–§3 of the PDF before final write-up.
