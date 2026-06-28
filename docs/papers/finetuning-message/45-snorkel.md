# Paper 45 — Snorkel: Rapid Training Data Creation with Weak Supervision (Data Programming)

> Family B (weak-supervision / LLM-labeling / distillation) · Analysis depth: abstract + extended-version cross-check. Compiled 2026-06-25.

## Bibliographic info
- **Authors / Year / Venue:** Ratner, Bach, Ehrenberg, Fries, Wu, Ré. **PVLDB 11(3):269–282, 2017** (VLDB 2017). Extended journal version: **The VLDB Journal 29:709–730 (2020)**, DOI [10.1007/s00778-019-00552-1](https://link.springer.com/article/10.1007/s00778-019-00552-1) (open access).
- **Link (VERIFIED):** [arXiv:1711.10160](https://arxiv.org/abs/1711.10160) · [PVLDB camera-ready (Brown CS mirror)](https://cs.brown.edu/people/sbach/files/ratner-vldb17.pdf) · [VLDBJ 2020 extended](https://link.springer.com/article/10.1007/s00778-019-00552-1). Authors/year/venue confirmed against all three.
- **R2 pillar:** weakly-supervised label creation — the methodological backbone of R2's "weakly-supervised gold-holdout" claim and the direct answer to weakness **W4** (single-LLM labels, no label model, no inter-annotator agreement).

## Summary
Snorkel is the first end-to-end implementation of **data programming**. Instead of hand-labeling, users write **labeling functions (LFs)** — arbitrary heuristics (lexicons, regexes, distant-supervision rules, third-party models) that each emit a noisy vote or abstain, with *unknown* accuracy and correlations. A **generative label model** then estimates each LF's accuracy (and inter-LF dependencies) **without any ground truth**, purely from the LFs' agreement/disagreement structure, and outputs **denoised probabilistic (soft) labels** per example. A downstream discriminative model is trained on those soft labels with a **noise-aware loss** (expected loss under the label distribution rather than treating one hard label as certain). Reported gains: 132% over heuristic baselines, within 3.6% of large hand-curated label sets, with SMEs building models 2.8× faster.

## Overlap with Pebble/R2 — 23% (peripheral)
`D1=0, D2=1, D3=0, D4=2, D5=0, D6=0, D7=0` → (3·0 + 2·1 + 1·0 + 2·2 + 2·0 + 2·0 + 1·0)/26 = (2 + 4)/26 = 6/26 = **23%**
- **Closest on:** **D4** (silver-label distillation/weak supervision — direct, strong) and weakly **D2** (the paper's flagship deployments are clinical VA/FDA text, adjacent to MH). Architecture/heads/loss-balancing/recall-floor/encoder dimensions are all absent — this is a *labeling* paper, not a *model* paper, which is exactly why its overlap % is low yet its leverage on R2's specific weakness (W4) is high.

## Best point — Method to adopt
Replace R2's **single LLM-as-one-labeler** regime with **multiple labeling functions denoised by a generative LabelModel** that estimates per-LF accuracies (and correlations) without gold, yielding **probabilistic labels** for noise-aware training — turning W4 from an unaddressed gap into a measured, citable methodology.
- **How to apply to Pebble:** stand up ≥3 LFs (2–3 distinct LLM prompts/models + 1–2 lexicon/heuristic LFs), fit a Snorkel LabelModel over the training pool, and feed its soft labels (plus per-LF accuracy/κ estimates) into R2 in place of the single `conf≥0.6` gpt label.

## ▶ Apply to R2
**Exact change — three edits, all upstream of the model:**

1. **Build the LF matrix (offline, before R2 runs).** For each Reddit post-sequence in the training pool (av9ash + scraped), produce a vote from each LF into a class in `{0,1,2,3}` or abstain (`-1`):
   - LF1 = current single gpt-style prompt (already exists).
   - LF2 = a *second* LLM prompt with a different rubric framing (or a different model).
   - LF3 = a third LLM prompt focused specifically on the **Behavior** distinction (the bottleneck class).
   - LF4 = a C-SSRS lexicon/heuristic LF (keyword/regex cues for behavior vs. attempt vs. ideation; abstains otherwise).
2. **Fit the LabelModel** (`snorkel.labeling.model.LabelModel`, cardinality=4) on the LF matrix → get (a) **probabilistic labels** `P(y|x)` per sequence, and (b) **estimated per-LF accuracies + learned LF weights**; also compute pairwise LF agreement/Cohen's κ for the report (W4 needs this — there is currently *no* inter-annotator number).
3. **Feed soft labels into R2.** In `load_combined` (line 184, `kaggle/finetuning-message/r2-suicide-risk-dualhead/r2-suicide-risk-dualhead.py`), the loader currently reads a hard `row["Label"]` and tags `Source ∈ {cssrs500, av9ash, scraped}` (line 198). Add a `SoftLabel` column (4-way probability vector) emitted by the LabelModel, keyed by `Source` so **only the LLM-pool rows** (av9ash/scraped) get soft labels while the clinical `cssrs500` gold-holdout test stays untouched. Then in `train_fold` (line 422), make the loss **noise-aware**: replace the hard-target `cross_entropy(cls, y)` / `coral_loss(coral, y)` arms with their soft-target expected-loss form (KL/soft-cross-entropy against `P(y|x)`); the focal arm and CORAL ordinal structure can be retained by computing expected loss over the label distribution. The `cssrs500` test fold keeps hard gold labels so the gold-holdout metric is unchanged and comparable.

This converts W4 from "single LLM, no κ, no label model" into a measured weak-supervision pipeline, and it attacks W1 (Behavior collapse = label quality) at its source: LF3 + the lexicon LF specifically denoise the 634 noisy Behavior samples rather than re-weighting them after the fact (`R2_BALANCE`).

## ▶ Kaggle experiment
- **Env/config:** LabelModel fitting is cheap CPU and runs **offline** before the kernel (no GPU); ship the resulting soft-labeled combined CSV as a Kaggle dataset input, identical wiring to today's combined CSV. R2 itself runs unchanged (GPU + Internet, torch 2.5.1 stack already pinned).
- **Ablation (±label-model), one moving part:**
  - **Arm A (control):** current single-LLM hard labels (Run B baseline, gold macro-F1 0.3849).
  - **Arm B:** multi-LF **majority vote** (no generative model) → hard labels, same R2 loss. Isolates "more labelers" from "the denoising model."
  - **Arm C:** multi-LF **LabelModel soft labels** + noise-aware loss. Isolates the generative-denoising contribution (B→C is the paper's core claim).
  - Keep architecture, freeze schedule, folds, and the held-out clinical CSSRS-500 eval identical across arms (mirror the honest-comparison discipline).
- **Expected signal:** **Behavior F1 up** from the 0.183 bottleneck (LF3 + lexicon LF target exactly that class), gold macro-F1 above Arm A, and — critically for the paper plan's **gap #1** — a reportable **inter-LF agreement / κ** number plus the **silver↔gold gap** that the single-LLM setup cannot produce. If C > B > A, you have the citable "generative label model beats majority vote beats single LLM" result.
- **Cost note:** dominant cost is **offline relabeling** — 2–3 extra LLM passes over the av9ash+scraped pool (one-time, batchable, no GPU). LabelModel fit is seconds. Kaggle GPU cost is unchanged vs. current Run B (three training arms = 3× one training run).

## Caveats
- **Ordinal vs categorical.** Snorkel's LabelModel is built for **categorical** LFs; R2's labels are **ordinal** (Indicator<Ideation<Behavior<Attempt). The vanilla LabelModel ignores class order, so its soft labels may not respect ordinal distance — mitigate by keeping R2's CORAL arm (which carries the ordinal structure) and computing its expected loss over the soft distribution, or by using ordinal-aware LFs. This is the main transfer risk and is not something the paper solves.
- **Few LFs.** Snorkel's accuracy estimates are most reliable with several diverse, conditionally-independent LFs; with only 3–4 LFs that are *all LLM-derived* (correlated errors), the generative model's accuracy estimates can be biased — include at least one genuinely independent heuristic/lexicon LF and report the learned LF correlations. With <3 LFs the LabelModel degenerates toward majority vote.
- **Domain-shift unverified for crisis text.** The paper's denoising gains are on VA/FDA clinical IE and open text/image sets, **not** adolescent Reddit suicide-risk language; the 132%/3.6% figures do not transfer — treat the *mechanism* as adopted, the *magnitudes* as hypotheses to measure on the gold holdout.
- **Verification status:** authors/year/venue/links VERIFIED (arXiv 1711.10160, PVLDB 11(3) camera-ready, VLDBJ 2020 extended); mechanism summarized from abstract + extended-version cross-check, not a line-by-line read of the full methods section.
