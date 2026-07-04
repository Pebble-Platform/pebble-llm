# Synthesis — Deep-read of papers 15–23, read against Pebble's open decisions

> **What this is.** The research output of the deep-read run (see [`PLAN-deep-read.md`](./PLAN-deep-read.md)).
> The 9 per-paper files are the evidence; this file is the *cross-paper* layer the plan required: where the
> same-problem papers **agree**, where they **contradict**, and — per Pebble decision (D-A…D-H) — **what to do**.
> Compiled 2026-06-16. Every number traces to a per-paper deep-read section (which carries its own venue/URL
> validation + status tag). "✓ done" papers = 01, 06–14 (deep-read in the prior run), referenced for context.

---

## Headline findings (read this if nothing else)

1. **The C-SSRS "bars" are not comparable to each other.** Papers 14/15/16/17 use four different datasets,
   class sets, metrics, and granularities. Quoting a single "C-SSRS SoTA" number is wrong. The transferable
   thing they *agree* on is a **method lesson, not a leaderboard**: C-SSRS errors are **ordinal/adjacent**, so
   use a distance-aware loss + ordinal metrics (MAE/QWK), not flat CE + accuracy.
2. **Naive MTL is a real competitor.** The closest published regression+classification system (18) won its
   shared task with a **plain unweighted MSE sum** — no Kendall/GradNorm/PCGrad. Pebble's "principled balancing"
   novelty (D-B) must beat *uniform-sum*, and the honest argument for weighting is the **MSE+CE scale mismatch**
   that paper 18 never had (it summed two scale-matched MSEs).
3. **Pebble's stub fine-tuning plan is contradicted by its own cited source.** ULMFiT (20) Table 7 shows
   **head-only ("frozen encoder → train heads") is the *worst* recipe on small data** (TREC-6 val error 16.09 vs
   5.69 for the staged recipe). Use *gradual* unfreezing, not a static freeze.
4. **The backbone choice (D-A) cannot be settled from the literature.** ModernBERT (22) and NeoBERT share no
   common benchmark and neither was ever evaluated on mental-health/affect/MTL. Only a Pebble-internal
   head-to-head decides it.
5. **Two datasets are anchors, not training data.** RSD-15K (17) re-confirmed **not obtainable** (repo 404);
   ESConv (23) is **CC-BY-NC → research-arm calibration slice only**, never in the deployed model.

---

## Pillar matrices (agreement / contradiction / what holds)

### Pillar 4 — C-SSRS suicide-risk severity (papers 14 ✓, 15, 16, 17 → D-C, D-G, D-H)

| Axis | 14 label-smoothing ✓ | 15 hybrid | 16 LLM-screening | 17 RSD-15K |
|---|---|---|---|---|
| Data | CSSRS-Reddit **500 users** | **2,999 posts / 473 users** | **~1,200 posts** (1/user) | **14,613 posts / 1,265 users** (not 15K) |
| Classes | **5** (incl. Supportive) | **4** (IN/ID/BR/AT, no Supportive) | 5-level C-SSRS | **4** (Indicator=*no-risk*/ID/BR/AT) |
| Metric | accuracy, macro-recall | **weighted-F1** | acc, **QWK, MAE** | acc, macro-F1 |
| Headline | 43%→**52%** acc, 47.8% macro-recall | **0.7512** wF1 (RoBERTa-only 0.7499) | Claude F1 0.7505 / QWK 0.876; Gemini weakest | DeBERTa **76%/77%**; RoBERTa 71%/65% |
| Annotation | — | Fleiss κ 0.564 | human κ 0.82 | Fleiss κ **0.7206** |
| Obtainable | ✅ in `data/finetuning-message/external/cssrs/` | dataset = different corpus | code public | ❌ **404, not obtainable** |

- **Hard contradiction (numbers don't compose):** "IN" = *Ideation* in 17 but *Indicator* in 15 — **opposite ends
  of the scale**. Attempt scores **F1 0.65 (15)** vs **recall ≈0 (14)** — a pure post-vs-user **granularity
  artifact**, not a modeling result. → *Never* average or rank these as one bar.
- **Strong agreement (the real lesson):** every paper's error structure is **adjacent-level** (16 shows ±1
  dominates; 15's confusion matrix is near-diagonal yet they still used flat CE; 17 has a graded scheme but no
  ordinal loss). → **D-C: adopt ordinal/distance-aware loss (ordinal-CE/CORN or regression+MSE) + report MAE +
  QWK + Spearman**, not flat CE + macro-F1.
- **Agreement on imbalance, with a warning:** distributions are steep (17: Attempt 5.5% vs Ideation 49%). But
  15 found **every rebalancing technique (oversample/undersample/weighted-loss/augmentation) *hurt* weighted-F1**
  under an imbalanced-*test* protocol. → rebalance cautiously; measure on a realistic test distribution.
- **Teacher-quality flag (D-G):** 16 shows **Gemini 1.5 Pro is the *weakest* LLM** (acc 0.596) on C-SSRS while
  Claude/Mistral reach QWK ≈0.876 (near the human κ 0.82). If Pebble's silver-label teacher is Gemini-class,
  **audit the teacher's C-SSRS labels against humans before trusting them**.
- **What's missing everywhere:** no per-level recall table (16's are image-only), no threshold policy, no
  calibration/ECE, no recall floor. **That gap is precisely Pebble's D-G contribution** (per-class Attempt
  recall ≥0.95, tuned threshold, calibrated probabilities).

### Pillar 5 — Emotion-intensity / empathy regression (papers 18, 19 → D-D, D-B, D-F)

| Axis | 18 WASSA@IITK 2021 | 19 NCUEE-NLP 2023 |
|---|---|---|
| Backbone | **ELECTRA-large**, shared encoder | **RoBERTa**, separate model per target |
| Reg head | single linear, **MSE** | per-target, MSE |
| MTL weighting | **unweighted sum** λ=1,1 (trivial) | n/a (separate models) |
| Metric | Pearson r | Pearson r |
| Headline | empathy **0.558** / distress 0.507 / avg **0.533**; emotion macro-F1 **0.5528** | Track1 avg **0.7236** (rank 4); Track2 avg **0.4178** (rank 1/9) |
| Key lever | GoEmotions→Ekman **augmentation +4.3pt** | **affect-adapted init**: EmoBERTa +0.0795 (+22% rel) on distress |

- **Agreement:** Pearson r is the metric; a single linear MSE head on a shared transformer is the standard,
  effective design for continuous affect. → **D-D: single-linear MSE severity head, evaluate by Pearson (+
  Spearman).**
- **Contradiction on balancing (feeds D-B):** 18 *won* with a **trivial unweighted MSE sum** → principled
  weighting is not automatically better; Pebble must beat the uniform-sum baseline. **But** 18 summed two
  **scale-matched MSE** losses, whereas Pebble mixes **MSE(severity)+CE(emotion)** with mismatched gradient
  scales — *that* is the legitimate case for weighting, and it's the experiment 18 never ran.
- **Contradiction on init (D-F):** affect-adapted init helps (19: +22% rel on distress) **but is
  target-dependent** — RoBERTa-Twitter *hurt* Track 2. → **match the adaptation domain to the head**
  (emotion/distress-adapted init for severity, not generic sentiment); treat as an ablation arm, not a default.
- **Cross-pillar contradiction:** 18 warns **oversampling distorts the train distribution** and prefers balanced
  external augmentation — the opposite of **FAIIR (01 ✓)**, which oversamples rare tags. The two closest
  analogues disagree on the imbalance remedy → Pebble must test both on its own data.
- **Caveat:** both are **adult** essay/conversation data; magnitudes (r≈0.53 essay, ≈0.72 turn-ish) are
  external baselines / upper-bound hypotheses, only the **mechanism + metric** transfer to child register.

### Pillar 6 — Staged fine-tuning / catastrophic forgetting (papers 20, 21 → D-E)

| Axis | 20 ULMFiT | 21 RecAdam |
|---|---|---|
| Mechanism | **control which params move when**: gradual unfreeze + discriminative LR (`η_{l-1}=η_l/2.6`) + STLR | **anchor + anneal**: `½γΣ(θ−θ*)²` + sigmoid `λ(t)`, all params move from step 0 |
| Init | unchanged | **random init beats pretrained** (3/4 small tasks) |
| Evidence | head-only is **worst** on small data (TREC-6 16.09 vs 5.69) | **+1.1%** GLUE / **+1.7%** on <10k-example tasks; base+RecAdam (84.3) > BERT-large (84.1) |
| Knobs | unfreeze schedule + 2 LR rules | one knob (anneal `k`) + γ |

- **Direct contradiction (mutually exclusive, not stackable):** ULMFiT freezes layers and varies per-layer LR
  with init unchanged; RecAdam moves *all* params from step 0 under a *uniform* anchor and even prefers random
  init. **Gradual unfreezing conflicts with "all weights anchored."** → run them as **two competing D-E arms**,
  do not combine.
- **Agreement:** on small target sets, *naive full fine-tuning* and *static head-only freezing* are both
  suboptimal; a forgetting-aware schedule helps. (ULMFiT data-size note: staged recipe earns its keep on Pebble's
  small ~1K human set; plain warm-up may suffice on the larger silver set.)
- **Shared gap:** **all evidence is classification/correlation — neither tested a regression target.** Pebble's
  severity head is regression, so the benefit must be re-measured before citing. RecAdam's γ=5000 is BERT-base/
  GLUE-specific and **must be swept**; it also anchors to *pretraining*, while Pebble's θ* is a *fine-tuned*
  (GoEmotions) init — an untested regime.

### Pillar 7 — Encoder backbone & support domain (papers 22, 23 → D-A, D-H, D-F)

| Axis | 22 ModernBERT | 23 ESConv |
|---|---|---|
| Role | **alternative backbone** vs NeoBERT | **dataset / calibration anchor** |
| Facts | 149M/395M, **8192 ctx**, RoPE, alternating attn, **2T tokens, 30% MLM**, GLUE 88.4 base | 1,053 convs (paper)/1,300 (release), **8 strategies, 3 stages, 1–5 intensity**, single-rater self-report |
| vs Pebble | NeoBERT = 250M, 4096 ctx, 2.1T; NeoBERT *claims* to beat ModernBERT on MTEB | License **CC-BY-NC** → research-arm only |
| Decides? | **No** — no shared benchmark, no MH/affect eval | calibration reference, **no IAA on affect labels** |

- **D-A is unresolvable from the literature:** ModernBERT and NeoBERT share no common benchmark, and **neither
  was evaluated on mental-health, affect, or multi-task** (closest proxy: SST-2 binary sentiment). ModernBERT's
  efficiency win is **long-context** — the *wrong regime* for Pebble's short turn-level inputs (where the paper
  admits it's slower than plain BERT). → **only a Pebble-internal head-to-head** (identical recipe, emotion
  macro-F1 + severity Pearson) decides the backbone.
- **Useful transfer anyway (D-F):** ModernBERT trains with **30% MLM masking** (citing Wettig 2023), not 15% →
  adopt 30% for Pebble's domain-adaptive MLM pass.
- **ESConv (D-H):** the 1–5 intensity is a **pre-chat, conversation-level, single-rater self-report** with **no
  inter-annotator agreement on the affect labels** → it's a **calibration distribution**, not a turn-level gold
  label source. Stub said "1,300/38K turns/8 emotions" (the release); the *paper* says 1,053/31,410 utt/7
  emotions; on-disk it's actually 11 emotion strings. Loader gotcha: `ESConv.json` **must be opened
  `encoding='utf-8'`** (crashes under cp1252 on Windows).

---

## Decision table (the deliverable: per open decision → evidence → recommendation)

| ID | Decision | Papers | What the evidence collectively says | **Recommendation for Pebble** | Confidence | Residual transfer risk |
|----|----------|--------|-------------------------------------|-------------------------------|:----------:|------------------------|
| **D-A** | Encoder backbone | 22, (12 ✓) | No published benchmark separates NeoBERT/ModernBERT; neither tested on affect/MH | **Keep NeoBERT but treat as unsettled; run an internal ModernBERT-vs-NeoBERT head-to-head on the 3-head stack (emotion macro-F1 + severity Pearson, identical recipe).** Check HF weight license for a child-facing product. | Low | High — all encoder evidence is general-English; child register untested |
| **D-B** | MTL loss-balancing | 18, (06–11 ✓) | Naive unweighted sum won a shared task (18); principled methods unproven *under a recall constraint* (11 ✓) | **Make uniform-sum the baseline arm; justify weighting by the MSE+CE scale mismatch (not present in 18). Run static-λ → Kendall → GradNorm → PCGrad/Nash via LibMTL; floor the (v2) safety weight.** | Med | Med — vision/essay evidence; no recall-floor regime tested anywhere |
| **D-C** | C-SSRS label scheme + loss | 14 ✓, 15, 16, 17 | Errors are ordinal/adjacent across all; "bars" not comparable; rebalancing can hurt | **Use ordinal/distance-aware loss (ordinal-CE/CORN or regression+MSE); report MAE+QWK+Spearman, not flat CE/acc. Pick ONE C-SSRS mapping (17's 4-class is the cleanest) and state it; don't quote a cross-paper SoTA.** | High (lesson) / Low (any single bar) | Med — adult Reddit, post/user-level vs Pebble turn-level |
| **D-D** | Severity/energy regression | 18, 19, 23 | Single-linear MSE + Pearson is standard; domain-matched init helps but is target-dependent | **Single-linear MSE severity head, Pearson(+Spearman) eval; add "affect-matched init" as an ablation arm (EmoBERTa-class, not generic sentiment); use ESConv 1–5 intensity as a calibration slice.** | Med-High | Med — adult magnitudes are upper bounds; ESConv is self-report, no IAA |
| **D-E** | Staged fine-tuning / warm-start | 20, 21 | Head-only freeze is worst on small data (20); ULMFiT vs RecAdam are mutually exclusive; no regression evidence | **Drop the static "frozen encoder → heads-only" plan. Benchmark two arms: (a) ULMFiT gradual-unfreeze+discriminative-LR+STLR, (b) RecAdam (swept γ). Re-measure on the regression head; sweep, don't copy constants.** | Med | Med — all evidence is classification, adult; regression untested |
| **D-F** | Domain-adaptive MLM pass | 19, 22, (12 ✓, 01 ✓) | Affect-matched init/MLM helps but target-dependent; modern recipe uses 30% masking | **Run a short in-domain MLM pass before head FT, at 30% masking (per 22); ablate it (the clean measurement 01/FAIIR never did). Match adaptation domain to the head.** | Med | Med — lift magnitude unknown on child text |
| **D-G** | Threshold / recall-floor + calibration | 16, 15, (01 ✓) | C-SSRS papers report no per-level recall, no thresholds, no calibration; teacher LLMs vary widely | **This gap IS Pebble's contribution: per-class (Attempt) recall floor, tuned thresholds, calibrated probabilities + ECE. Audit the silver-label teacher (Gemini weakest in 16) against humans.** | High (gap is real) | Low — this is Pebble-owned methodology |
| **D-H** | Datasets / anchors | 17, 23, (14 ✓) | RSD-15K not obtainable (404); ESConv research-only | **Anchors: CSSRS-Reddit (14, obtainable) + WASSA-empathy (deployable) for training; ESConv as research-arm calibration slice (`encoding='utf-8'`). Drop RSD-15K; keep UMD-Reddit (DUA) as a fallback. Reuse RSD-15K's annotation-QC protocol, not its data.** | High | Low — provenance re-verified 2026-06-16 |

---

## Concrete next actions implied by the synthesis

1. **D-C / severity head:** implement an **ordinal/distance-aware loss** + add **MAE/QWK/Spearman** to eval;
   commit to a single C-SSRS class mapping (recommend 17's 4-class) in the data layer.
2. **D-B / MTL experiment:** add a **uniform-sum baseline** arm to the LibMTL comparison and frame the novelty as
   *MSE+CE scale-mismatch balancing under a recall floor* (the regime no prior paper tested).
3. **D-E / fine-tuning:** **remove the static head-only-freeze plan**; set up ULMFiT-arm vs RecAdam-arm, both
   measured on the regression head.
4. **D-D / D-F:** add an **affect-matched init** ablation and a **30%-mask MLM** pass with an isolation ablation.
5. **D-H / data:** add `load_esconv()` (UTF-8, NC-licensed → research arm only); mark RSD-15K closed; keep the
   teacher-audit (D-G) on the roadmap before any silver-label trust claim.

> Cross-references: per-paper evidence in [`15`](finetuning-message/15-cssrs-hybrid.md)–[`23`](finetuning-message/23-esconv.md); closest-system
> context in [`01-faiir.md`](finetuning-message/01-faiir.md) and the MTL set [`06`](finetuning-message/06-kendall-uncertainty-mtl.md)–[`11`](finetuning-message/11-mtl-imbalance-revisit.md);
> decision status in [`../decisions.md`](../decisions.md).
