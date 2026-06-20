# Improvement Plan — what the deep-read evidence changes in Pebble

> **Input:** the full-PDF deep reads of papers 01–23 and their cross-paper
> [`papers/SYNTHESIS-deep-read.md`](./papers/SYNTHESIS-deep-read.md).
> **Compared against:** the current process — [`../pebble-finetuning-strategy-v3.md`](../pebble-finetuning-strategy-v3.md),
> [`phases.md`](./phases.md), [`decisions.md`](./decisions.md), and the actual code
> (`src/pebble_llm/models/losses.py`, `models/heads.py`, `evaluation/metrics.py`, `training/trainer.py`,
> `data/external.py`).
> **Output:** concrete changes to methodology, dataset, experiment, and evaluation, each traceable to a paper.
> Compiled 2026-06-16.

Each item is tagged **[v1]** (active now — `decisions.md`: reuse public labels; only `emotion` + `severity`
learned; no safety head) or **[v2]** (deferred — evidence banked for when the safety/C-SSRS head is added).

---

## 0. Executive summary — current vs evidence vs change

| Dec | Area | Current process | What the evidence says | Change | Stage |
|----|------|-----------------|------------------------|--------|:-----:|
| **D-B** | MTL loss balancing | `MultiTaskLoss` = **static weighted sum** (score×1+emotion×1+safety×2), Kendall/GradNorm only a TODO comment | Naive unweighted sum is a *real competitor* (18 won a shared task with it); principled methods unproven under a recall floor (11) | Make **uniform-sum an explicit baseline arm**; implement Kendall (UW) via LibMTL as the first principled arm; frame novelty as **MSE+CE scale-mismatch** balancing; floor the safety weight | v1 (emo+sev) |
| **D-C** | Severity/safety label scheme + loss | `severity` = continuous sigmoid+**MSE**; metrics = MAE only; no ordinal handling | C-SSRS errors are **ordinal/adjacent** → distance-aware loss + MAE/QWK/Spearman; "bars" not comparable across papers | Add **ordinal/distance-aware loss + QWK/Spearman** for any *discretized* severity and the (v2) safety/C-SSRS head; pick **one** C-SSRS mapping | v1 (discretized sev) / v2 (safety) |
| **D-D** | Regression transfer | single linear sigmoid-MSE score head; **no Pearson** in metrics; generic NeoBERT init | single-linear MSE + **Pearson** is the standard; **affect-matched init** lifts regression (+22% rel, but target-dependent) | Add **Pearson/Spearman** to `metrics.py`; add an **affect-matched-init** ablation arm; ESConv calibration slice | v1 |
| **D-E** | Staged fine-tuning | freeze encoder 2 ep → unfreeze at low LR (a **static freeze→unfreeze**) | **Head-only/static freeze is the *worst* recipe on small data** (ULMFiT Table 7); gradual unfreeze+discriminative-LR+STLR, or RecAdam — competing arms | Replace static freeze with **gradual unfreeze + discriminative LR + STLR**; add **RecAdam** as a second arm; measure both on the regression head | v1 |
| **D-F** | Domain-adaptive MLM | emotion-head GoEmotions pretrain only; **no in-domain MLM pass** | In-domain MLM helps (01, 12, 19); modern recipe uses **30% masking** (22) | Add a **30%-mask MLM pass** before head FT **with an isolation ablation** (the clean measurement FAIIR never did) | v1 |
| **D-A** | Encoder backbone | NeoBERT primary; ModernBERT a documented *fallback note* | Literature **cannot** separate NeoBERT/ModernBERT; neither tested on affect/MH | Promote ModernBERT from "fallback note" to an **actual head-to-head experiment arm** (identical recipe, emotion-F1 + severity-Pearson); verify license | v1 |
| **D-G** | Threshold / recall-floor / calibration | safety recall ≥0.95 *target*; **no calibration (ECE)**, no per-head threshold tuning, no teacher audit | C-SSRS papers report none of these → **this gap is Pebble's contribution**; teacher LLMs vary widely (Gemini weakest, 16) | Add **ECE/reliability + per-head threshold tuning**; audit the silver-label teacher *if* a Gemini-class teacher returns (v2) | v2 (mostly) |
| **D-H** | Datasets / anchors | strategy lists many; ESConv+WASSA acquired; RSD-15K pending | **RSD-15K not obtainable (404, re-confirmed)**; ESConv **CC-BY-NC → research-arm calibration only** | **Drop RSD-15K**; add `load_esconv()` (UTF-8, NC-flagged) as a calibration slice; reuse RSD-15K's QC protocol, not its data | v1 |

---

## 1. Methodology

### 1.1 Multi-task loss balancing — the #1 novelty (D-B) **[v1]**
**Current:** `losses.py::MultiTaskLoss` is a fixed weighted sum; the docstring names Kendall/GradNorm but they're
an unimplemented TODO.
**Evidence:** Paper **18** (closest reg+classification system) *won* its shared task with a **trivial unweighted
MSE sum** — so "principled balancing" is not automatically better and must be proven. Crucially, 18 summed **two
scale-matched MSE** losses; Pebble mixes **MSE(severity)+CE(emotion)** with mismatched gradient scales — that
mismatch is the legitimate case for weighting, and the experiment 18 never ran. Paper **11** warns well-tuned
static weights often match fancy methods in vision and the recall-floor regime is **untested**.
**Change:**
1. Add a **uniform-sum (`w=1,1`) baseline arm** — the honest null hypothesis 18 establishes.
2. Wrap the NeoBERT trunk in **LibMTL** and add a **Kendall uncertainty-weighting (UW)** arm first (per 06: learned
   `s=logσ²`, `exp(−s)·L + s/2`), then GradNorm/PCGrad/Nash.
3. **Floor the safety head's weight** (cap its log-variance) so UW cannot down-weight it — per 06's own caveat.
4. Report the comparison as static-λ → uniform-sum → UW → GradNorm under the **MSE+CE scale mismatch** framing.

### 1.2 Staged fine-tuning — stop freezing the whole encoder (D-E) **[v1]**
**Current:** strategy §6.1 + `trainer.py` freeze the encoder for ~2 epochs, then unfreeze at a low LR — a *static*
freeze→unfreeze.
**Evidence:** Paper **20 (ULMFiT) Table 7** shows **head-only / frozen-encoder fine-tuning is the *worst* recipe on
small data** (TREC-6 val error 16.09 vs 5.69 for the staged recipe) — directly contradicting the current plan. The
fix is *gradual* unfreezing + discriminative LR (`η_{l-1}=η_l/2.6`) + STLR. Paper **21 (RecAdam)** is a *competing*
recipe (anchor-to-init + anneal; +1.7% on <10k-example tasks) that is **mutually exclusive** with gradual unfreezing
(do not stack). Both papers tested only classification — **re-measure on the regression head**.
**Change:** replace the static freeze with **gradual unfreezing + discriminative LR + STLR** as arm A; add
**RecAdam** (swept γ, not the GLUE default 5000) as arm B; pick the winner on Pebble's small set, measured on
`severity` (regression), not just `emotion`.

### 1.3 Add a domain-adaptive MLM pass (D-F) **[v1]**
**Current:** the only pretraining is GoEmotions on the *emotion head*; there is no in-domain MLM continued
pretraining of the encoder.
**Evidence:** FAIIR (01), MentalBERT (12), and NCUEE (19) all credit in-domain affect/MLM adaptation; ModernBERT
(22) uses **30% masking** (not 15%). FAIIR *claims* MLM "significantly enhances" but **never isolated it** — an
ablation Pebble can own.
**Change:** add a short **MLM pass at 30% masking** on the in-domain corpus (GoEmotions/Empathetic/ESConv text)
before head fine-tuning, **with an isolation ablation** (MLM-on vs MLM-off, same seeds) — the first clean
measurement in this domain. Match the adaptation domain to the head (emotion/distress text for `severity`).

**Empirical result (2026-06-17 · 3 seeds [13/42/1337] · NeoBERT · P100) — ran the isolation ablation twice:**
- *Run A* (corpus = 25k of the **fine-tune text itself**, 30% masking, encoder saved **fp16**): MLM-on **lost** on every metric — Δ(on−off) macroF1 −0.007, **ECE +0.081**, Pearson −0.046. A clean negative.
- *Run B* (corpus = 80k **separate** in-domain text [GoEmotions-raw 9k + tweet_eval sentiment/offensive/hate/irony/emotion 71k, deduped vs fine-tune/eval], **15% masking**, encoder **fp32**): verdict flips to a **task-specific tradeoff** — emotion macroF1 **+0.0127 ± 0.0099** (3/3 seeds positive), but severity **Pearson −0.045 ± 0.017** (3/3 seeds negative) and **ECE +0.052** (worse, ~36% less than Run A). MLM loss 2.42→2.29.

**Reading:** the original negative was partly an artifact (same-as-fine-tune corpus + fp16 confound). With a real TAPT corpus, MLM adaptation **helps the emotion (classification) head and hurts the severity (regression) head** — they share one encoder. Run B's corpus was ~71k/80k Twitter sentiment/toxicity (only 9k emotion comments survived dedup — GoEmotions-raw is one row per annotator), pushing representations toward categorical separability at the cost of intensity resolution. **Open next step:** rebalance the corpus toward intensity-graded affect (drop offensive/hate; add EmoBank / SemEval V-reg / EI-oc) and re-measure severity, or decouple the encoder per pool. Notebook: `kaggle/finetuning-message/pebble-mlm-ablation-3seed/`.

### 1.4 Backbone choice is an experiment, not a footnote (D-A) **[v1]**
**Current:** NeoBERT primary; ModernBERT documented as a second-line *fallback*.
**Evidence:** Paper **22** — ModernBERT and NeoBERT share no common benchmark and **neither was evaluated on
mental-health/affect/MTL**; ModernBERT's win is *long-context*, the wrong regime for Pebble's short turn-level
inputs. Only a Pebble-internal head-to-head decides it.
**Change:** run **NeoBERT vs ModernBERT as a real arm** (identical 3-head recipe, identical data/seeds; compare
emotion macro-F1 + severity Pearson + latency at turn-length inputs). Keep NeoBERT as default (MIT license is clean)
but let the number, not the strategy doc, justify it. (Reuse 22's **30% masking** finding for §1.3.)

---

## 2. Dataset

### 2.1 Pick one C-SSRS mapping; don't quote a cross-paper "bar" (D-C) **[v2 + v1-discretized]**
**Current:** strategy §5.4 lists CLPsych/UMD for safety; `severity` is a continuous [0,1] regression from
SemEval/WASSA intensity.
**Evidence:** the C-SSRS "bars" in 14/15/16/17 are **not comparable** (different datasets, class sets, metrics,
granularities; "IN" means *Ideation* in one paper and *Indicator* in another; Attempt F1 0.65 vs recall ≈0 is a
post-vs-user artifact). The one durable lesson is the **ordinal** error structure.
**Change:**
- When the **safety/C-SSRS head** is added (v2), adopt **one** explicit class mapping — recommend **17's 4-class**
  (Attempt/Behavior/Ideation/Indicator, Indicator = no-risk) — and state it in the data layer; never average or
  rank numbers across the four papers.
- For any **discretized severity** (strategy already floats "discretize energy/severity to 3 ordinal classes"):
  use an **ordinal/distance-aware loss** (ordinal-CE / CORN) not flat CE, because adjacent-level errors should cost
  less than far ones.
- **Rebalance cautiously:** paper 15 found every resampling/weighting trick *hurt* weighted-F1 under a realistic
  imbalanced test — measure on a realistic distribution before trusting oversampling.

### 2.2 Regression transfer + an affect-matched init arm (D-D) **[v1]**
**Current:** `severity` head warm-starts only from the generic NeoBERT encoder; no affect-specific init.
**Evidence:** Paper **19** — affect-matched init (EmoBERTa-class) lifts distress regression **+0.0795 (+22% rel)**,
but it is **target-dependent** (generic Twitter-sentiment init *hurt* one track). Paper **18** confirms single-linear
MSE + Pearson as the standard design.
**Change:** add an **affect-matched-init ablation arm** (warm-start the encoder from an emotion/distress-adapted
checkpoint vs vanilla) and keep it as an arm, not a default. Use **WASSA-empathy** (`data/external/wassa_empathy/`,
CC-BY → deployable) as the external severity baseline (empathy r≈0.558 / distress r≈0.507 from 18).

### 2.3 ESConv as a research-arm calibration slice; drop RSD-15K (D-H) **[v1]**
**Current:** `external.py` has loaders for SemEval/WASSA-intensity; ESConv acquired but no loader; RSD-15K listed as
a possible larger corpus.
**Evidence:** **RSD-15K re-confirmed not obtainable** (repo 404 on 2026-06-16; org has zero public repos). **ESConv
is CC-BY-NC** → research arm only, **never in the deployed model**; its 1–5 intensity is a *single-rater,
conversation-level self-report with no IAA on affect labels* → a **calibration distribution**, not turn-level gold.
**Change:**
- Add **`load_esconv()`** mirroring `load_semeval_intensity`, **opening `ESConv.json` with `encoding='utf-8'`**
  (it is not cp1252-decodable — crashes on Windows otherwise), and **flag it research-arm-only** so it can't leak
  into the deployable training set.
- Build an `eval/calibration/esconv_intensity` slice: Pearson/Spearman of predicted `severity` vs ESConv intensity.
- **Mark RSD-15K closed** in `dataset-acquisition-plan.md`; keep UMD-Reddit (DUA) as the only fallback. **Reuse
  RSD-15K's annotation-QC protocol** (95% pre-task gate, daily 10% audit, κ≈0.72), not its data.

---

## 3. Experiment design

### 3.1 The MTL ablation grid (D-B) **[v1]**
Run on identical data/splits/seeds, severity-Pearson + emotion-macro-F1 as joint objectives:
`static-λ` (current) → `uniform-sum` (18's null) → `Kendall-UW` (floored safety) → `GradNorm` → `PCGrad`/`Nash`.
**Success criterion:** a principled arm must beat *uniform-sum* (not just static-λ) on the joint metric to justify
the novelty claim. Report mean ± std over ≥3 seeds (already the `metrics.py` `SeedResults` contract).

### 3.2 The staged-FT bake-off (D-E) **[v1]**
Two mutually-exclusive arms — **(A)** ULMFiT gradual-unfreeze+discriminative-LR+STLR vs **(B)** RecAdam — plus the
current static freeze as the baseline. Measured on the **regression** head specifically (neither paper tested
regression). This also de-risks the §5.3 small-data overfitting concern with evidence instead of assumption.

### 3.3 The MLM isolation ablation (D-F) **[v1]**
MLM-on vs MLM-off, 30% masking, same seeds — the clean measurement FAIIR skipped. One row in the results table;
high citation value. **Run (2026-06-17):** empirically **15% masking on a *separate* 80k corpus** beat the
30%/same-corpus recipe, and the result is a **classification-vs-regression tradeoff**, not a uniform win — see §1.3.

### 3.4 The backbone head-to-head (D-A) **[v1]**
NeoBERT vs ModernBERT, identical recipe, at **turn-length** inputs (where 22 admits ModernBERT loses its
long-context edge). Decides the backbone with a number.

### 3.5 Eval-set construction borrowed from FAIIR (01) **[v1]**
Pebble's Protocol B test set is small (~500) and a purely random slice under-covers high-severity cases. Build it
the **FAIIR way: half random-hard, half curated** to cover every severity band + suspected silver-label errors —
that is what made FAIIR's 40-item expert set informative enough to change its production threshold. Pair with a
small **expert-consensus slice** (3 blind + 3 open raters) reporting model-vs-human *next to* silver-vs-human
agreement.

---

## 4. Evaluation & metrics (the most concrete code gap)

`evaluation/metrics.py` currently has MAE, macro-F1, safety P/R, and `severity_band_mae`. The evidence demands three
additions:

| Add | Why | Source |
|-----|-----|--------|
| **Pearson + Spearman** for `severity`/`energy` | the standard continuous-affect metric everywhere in Pillar 5; MAE alone hides rank quality | 18, 19, 23 |
| **QWK + ordinal MAE** for any discretized severity / (v2) safety levels | C-SSRS errors are ordinal; flat accuracy/F1 hides adjacent-vs-far error structure (best-F1 ≠ best-ordinal in 16) | 14, 16, 17 |
| **ECE + reliability curve** | the Decision Engine consumes *probabilities*; no paper in the set calibrates — Pebble's contribution and a deployment necessity | 01, 15, 16 |

Plus **per-head threshold tuning** on validation (FAIIR's per-frequency-tier policy) instead of a single cutoff —
publish the precision/recall trade (FAIIR: +4% P for −6% R).

---

## 5. Safety head (D-C/D-G) — **[v2]**, evidence banked
v1 has no learned safety head (`decisions.md`). When it returns:
- **Ordinal/distance-aware loss** + QWK (D-C), per-class **Attempt recall floor** + tuned threshold + calibration
  (D-G) — exactly the gap every C-SSRS paper left open.
- **Audit the silver-label teacher**: paper 16 shows **Gemini 1.5 Pro is the *weakest* LLM** on C-SSRS (acc 0.596)
  while Claude/Mistral reach QWK≈0.876 ≈ human κ 0.82. If a Gemini-class teacher returns for silver labels, audit
  its crisis labels against humans before trusting them.
- Keep FAIIR's **rule-layer-first** safety architecture (keyword tripwire that can only *escalate*, model second,
  human always decides) — already aligned with the strategy's union-of-triggers (§8.1).

---

## 6. Concrete code/file changes (smallest viable diffs)

| File | Change | Item |
|------|--------|------|
| `models/losses.py` | Add a `uniform-sum` mode + a LibMTL/Kendall-UW path with a **safety-weight floor**; replace the TODO comment with the real arm | 1.1 |
| `evaluation/metrics.py` | Add `pearson()`, `spearman()`, `quadratic_weighted_kappa()`, `expected_calibration_error()`; extend `TARGETS` | 4 |
| `training/trainer.py` | Replace static freeze→unfreeze with **gradual unfreeze + discriminative LR + STLR**; add a RecAdam optimizer option | 1.2 |
| `training/` (new) | Add an **MLM pretrain** step (30% mask) + an `mlm_on/off` flag for the ablation | 1.3 |
| `data/external.py` | Add **`load_esconv()`** (UTF-8, research-arm-only flag) | 2.3 |
| `data/taxonomy.py` / data layer | When safety/C-SSRS lands: encode **one** C-SSRS 4-class mapping (17) | 2.1 |
| `models/neobert_multitask.py` + config | Add a **ModernBERT** swap path for the backbone head-to-head | 1.4 |
| `docs/dataset-acquisition-plan.md` | Mark **RSD-15K closed**; record ESConv NC-only + UTF-8 caveat | 2.3 |

---

## 7. Prioritized roadmap

1. **Now (v1, high leverage, low cost):**
   - 4 — add Pearson/Spearman (+ ECE scaffold) to `metrics.py`. *(1 file, unblocks D-D/D-B eval)*
   - 1.2 — fix the fine-tuning recipe (gradual unfreeze + discriminative LR + STLR). *(ULMFiT contradiction is the
     clearest, highest-confidence finding)*
   - 1.1 — add the uniform-sum baseline + Kendall-UW arm. *(the #1 novelty; needs the metrics from step 1)*
2. **Next (v1):** 1.3 MLM isolation ablation · 2.2 affect-init arm · 1.4 backbone head-to-head · 2.3 ESConv loader.
3. **Experiment & report (v1):** 3.1–3.5 as the results tables; 3.5 builds the FAIIR-style eval set.
4. **When safety head returns (v2):** Section 5 in full.

---

## 8. What the evidence does *not* support (guardrails)
- **No cross-paper C-SSRS SoTA number.** Don't write "C-SSRS SoTA is 0.75 / 0.52 / 0.77" — they're different tasks
  (D-C). Quote each only against its own corpus.
- **Principled MTL is not assumed to win.** It must beat uniform-sum on Pebble's data; 18 is the cautionary case.
- **Adult magnitudes are upper bounds.** Every Pillar-4/5 number is adult Reddit/essay; only mechanisms + metrics
  transfer to Pebble's child register — treat absolute r/F1/QWK as hypotheses, validate on Pebble's own slice.
- **ESConv cannot train the deployed model** (CC-BY-NC) — research arm / calibration only.
- **RecAdam and gradual-unfreezing don't stack** — they're competing arms (D-E).

> Evidence index: per-paper deep reads in [`papers/15-cssrs-hybrid.md`](./papers/finetuning-message/15-cssrs-hybrid.md)–[`papers/23-esconv.md`](./papers/finetuning-message/23-esconv.md)
> and [`papers/01-faiir.md`](./papers/finetuning-message/01-faiir.md)/[`papers/06`](./papers/finetuning-message/06-kendall-uncertainty-mtl.md)–`14`; cross-paper
> reasoning + per-decision table in [`papers/SYNTHESIS-deep-read.md`](./papers/SYNTHESIS-deep-read.md).
