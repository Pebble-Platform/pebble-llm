# Related Work — Enrichment Set

> **Purpose.** Companion to [`related-work-survey.md`](./related-work-survey.md) (the 5 *closest*
> papers). This set is organized by **Pebble's methodological pillars** — each entry says how the
> paper concretely enriches the project (a baseline to run, a backbone to try, a method to adopt,
> or a dataset to add). Picked for *actionability*, not just topical closeness.
>
> **Compiled:** 2026-06-09

---

## Pillar 1 — Multi-task loss balancing *(Pebble's strongest novelty angle)*

The survey found every closest paper uses static / grid-searched λ. These give Pebble the actual
methods + a ready-made library to run the static-vs-principled comparison.

- **Kendall, Gal, Cipolla (CVPR 2018) — *Multi-Task Learning Using Uncertainty to Weigh Losses.***
  The homoscedastic-uncertainty weighting Pebble's strategy already names. The canonical citation
  for the uncertainty-weighting arm.
- **Chen et al. (ICML 2018) — *GradNorm.*** Gradient-norm balancing; the other named arm.
- **Yu et al. (NeurIPS 2020) — *PCGrad / Gradient Surgery for MTL.*** Projects conflicting task
  gradients; cheap to add as a third arm. [arXiv](https://arxiv.org/abs/2001.06782)
- **Navon et al. (ICML 2022) — *Nash-MTL.*** Treats weighting as a bargaining game; a stronger,
  more recent baseline. [arXiv](https://arxiv.org/abs/2202.01017)
- **🔧 Lin & Zhang (JMLR 2023) — *LibMTL.*** A PyTorch library implementing **Uncertainty Weights,
  GradNorm, DWA, PCGrad, MGDA, Nash-MTL** under one API. **Use this to run Pebble's
  static-vs-principled comparison without reimplementing each method.**
  [JMLR](https://www.jmlr.org/papers/volume24/22-0347/22-0347.pdf)
- **(2025) — *Revisit the Imbalance Optimization in Multi-task Learning.*** Recent experimental
  analysis showing well-tuned static weights often match fancy methods — exactly the null
  hypothesis Pebble's experiment must rule out. [arXiv](https://arxiv.org/abs/2509.23915)

> **How it enriches:** turns Pebble's "compare static λ vs Kendall vs GradNorm under a recall
> constraint" claim from aspiration into a concrete, library-backed experiment with a fair baseline.

---

## Pillar 2 — Mental-health domain encoders *(backbone + baselines)*

- **Ji et al. (LREC 2022) — *MentalBERT / MentalRoBERTa.*** Publicly available transformers
  domain-adaptively pretrained on Reddit mental-health text; benchmarked on depression, stress,
  **suicidal-ideation** detection. [arXiv](https://arxiv.org/abs/2110.15621) ·
  [HF: mental-roberta](https://huggingface.co/AIMH/mental-roberta-large)

> **How it enriches:** the obvious **baseline/backbone comparison** — does NeoBERT (general,
> 250M, 2.1T tokens) beat a domain-pretrained MentalRoBERTa on Pebble's heads? Also a free
> warm-start alternative if NeoBERT underperforms on crisis text. Strengthens the encoder-choice
> justification the paper will need.

---

## Pillar 3 — LLM-teacher → small-encoder distillation *(beyond Emo Pillars)*

- **(2024) — *Performance-Guided LLM Knowledge Distillation for Efficient Text Classification at
  Scale.*** Black-box distillation of a frontier LLM's labels into a small classifier with a
  performance-gating step — the closest template to Pebble's Gemini→NeoBERT silver-label setup
  beyond Emo Pillars.
  [ResearchGate](https://www.researchgate.net/publication/386201474)
- **(2025) — *Knowledge & Dataset Distillation of LLMs: trends, challenges, directions* (survey).**
  Frames black-box (output-only, closed teacher like Gemini) vs white-box KD — situates Pebble's
  approach and its teacher-bias risk. [Springer](https://link.springer.com/article/10.1007/s10462-025-11423-3)
  · [arXiv](https://arxiv.org/pdf/2504.14772)

> **How it enriches:** gives Pebble a current (2024–25) distillation framing and vocabulary
> (black-box label distillation, performance gating) to position the Gemini-teacher contribution
> against, and to cite for the teacher-bias limitation.

---

## Pillar 4 — Suicide-risk severity on the *exact* dataset you just downloaded

These benchmark on the **Reddit C-SSRS 500-user dataset now in `data/external/cssrs/`** — direct
baselines and a key design lesson for the safety head.

- **🔧 (2024) — *Enhancing Suicide Risk Detection through Semi-Supervised Deep Label Smoothing.***
  Improves the C-SSRS benchmark from **~43% → 52%** via label smoothing. Reports the standard
  split + numbers Pebble's safety head should beat. [arXiv](https://arxiv.org/abs/2405.05795)
- **(2025) — *Detection of Suicidal Risk on Social Media: A Hybrid Model* (RoBERTa-TF-IDF-PCA).**
  Another recent C-SSRS baseline. [arXiv](https://arxiv.org/html/2505.23797v1)
- **(2025) — *Evaluating LLM Reasoning for Suicide Screening with the C-SSRS.*** Zero-shot LLM
  reasoning on the same scale — a useful "is the teacher even good at this?" reference for the
  Gemini-teacher calibration question. [arXiv](https://arxiv.org/html/2505.13480v1)
- **(2025) — *RSD-15K.*** A larger user-level suicide-risk dataset if 500 users proves too small.
  [arXiv](https://arxiv.org/pdf/2507.11559)

> **How it enriches:** the label-smoothing paper makes the explicit point that **C-SSRS errors are
> ordinal** — mispredicting high-risk as low-risk must cost more than an adjacent-level slip. This
> directly informs the **C-SSRS→`severity`/safety mapping decision** flagged in the acquisition
> plan (ordinal loss / distance-weighted penalty, not plain CE). And it hands you a published
> accuracy bar (52%) to target.

---

## Pillar 5 — Emotion-intensity & empathy/distress regression *(continuous-head transfer)*

- **WASSA@IITK (WASSA 2021) — *Multi-task Learning + Transformer Finetuning for Emotion + Empathy.***
  RoBERTa multi-task with a **regression head (empathy/distress) alongside emotion classification**
  — structurally the closest to Pebble's regression+classification combo, evaluated by Pearson.
  [arXiv](https://arxiv.org/abs/2104.09827)
- **PVG at WASSA 2021 — *Multi-Input, Multi-Task Transformer for Empathy & Distress.*** Another
  multi-task regression design point. [paper](https://www.academia.edu/70404630/)
- **NCUEE-NLP (WASSA 2023) — *Sentiment-Enhanced RoBERTa* for empathy + emotion.** Recent,
  reports Pearson baselines. [ACL](https://aclanthology.org/2023.wassa-1.49/)

> **How it enriches:** concrete prior art for **training a continuous regression head jointly with
> emotion classification on a transformer**, plus the standard metric (Pearson) and λ-weighting
> choices Pebble's `severity`/`energy` heads should be compared against.

---

## Pillar 6 — Staged fine-tuning / catastrophic forgetting *(warm-start ablation)*

- **Howard & Ruder (ACL 2018) — *ULMFiT.*** Origin of **gradual unfreezing**, discriminative LRs,
  slanted triangular LR — the canonical citation for Pebble's frozen-encoder → staged-unfreeze
  schedule. [ACL](https://aclanthology.org/P18-1031.pdf)
- **Chen et al. (EMNLP 2020) — *Recall and Learn* (RecAdam).** Fine-tuning pretrained LMs with
  **less catastrophic forgetting** via a recall objective — directly relevant to keeping
  NeoBERT's pretraining + GoEmotions warm-start intact while adding the safety head.
  [arXiv](https://arxiv.org/pdf/2004.12651)

> **How it enriches:** gives the warm-start/unfreezing ablation (survey angle #3) a principled
> citation base and a concrete alternative (RecAdam) to compare against naive staged unfreezing.

---

## Pillar 7 — Encoder choice & emotional-support domain *(context / framing)*

- **Warner et al. (2024) — *ModernBERT.*** 8,192-token efficient encoder; the natural
  **alternative backbone + comparison** to NeoBERT (4,096 ctx, 250M). Useful for justifying the
  encoder choice and for a longer-context multi-turn variant.
  [arXiv](https://arxiv.org/pdf/2412.13663)
- **Liu et al. (ACL 2021) — *ESConv: Emotional Support Conversation dataset.*** 1,300 multi-turn
  support dialogues annotated with **8 support strategies** + the explore/comfort/action framework.
  Pebble's downstream domain; a source of multi-turn support context and a `receptivity`-adjacent
  signal. [dataset overview](https://www.emergentmind.com/topics/esconv-dataset)
- **(2026) — *HEART: Unified Benchmark for Humans & LLMs in Emotional Support Dialogue.*** Recent
  five-axis evaluation framework — useful for framing what a deployed Pebble-fed agent should be
  measured on. [arXiv](https://arxiv.org/pdf/2601.19922)

> **How it enriches:** ModernBERT is the encoder Pebble will be asked "why not this instead?" — pre-empt
> it. ESConv supplies in-domain multi-turn support data and a strategy taxonomy that maps onto
> Pebble's Decision-Engine outputs.

---

## Highest-leverage additions (if you only chase a few)

1. **🔧 LibMTL** — run the static-vs-principled MTL comparison for ~free. Core to the novelty claim.
2. **🔧 C-SSRS deep-label-smoothing (2024)** — published baseline (52%) + the **ordinal-loss lesson**
   for your safety-head mapping decision, on the *exact* dataset you downloaded.
3. **MentalBERT / MentalRoBERTa** — the encoder baseline the reviewers will demand against NeoBERT.
4. **WASSA@IITK 2021** — closest published regression+classification multi-task design to copy/beat.
5. **ULMFiT + RecAdam** — citation base for the staged-unfreeze warm-start ablation.

---

---

## Per-paper analysis — overlap % + best point

> Produced by the `analysis-paper` agent (one per paper), 2026-06-09. Overlap = `(Σ wᵢ·scoreᵢ)/26 × 100`
> across the 7 Pebble dimensions (D1 heterogeneous heads ×3, D2 mental-health ×2, D3 emotion-transfer ×1,
> D4 LLM-teacher distillation ×2, D5 MTL balancing ×2, D6 safety-recall constraint ×2, D7 encoder backbone ×1).
> **Honest finding:** all are **peripheral (<40%)** except WASSA@IITK (42%, adjacent) — these are *method /
> baseline / dataset* contributors, not close *systems* (the 5 close systems live in `related-work-survey.md`).
> Each scored mostly from abstract/HTML; deep-read caveats are in the agent notes (not all reproduced here).

| Paper | Overlap | Best-point type | Single most useful point for Pebble |
|-------|:------:|-----------------|-------------------------------------|
| **WASSA@IITK 2021** | **42%** | Baseline to beat | Closest published regression+classification MTL; clear the bar: empathy/distress Pearson r≈0.53, emotion macro-F1≈0.55 |
| **Kendall 2018** | 38% | Method to adopt | Learned per-head log-variance: `L=Σ exp(−sᵢ)·Lᵢ+sᵢ` — try **first**, but floor the safety head so it can't down-weight below recall 0.95 |
| **GradNorm 2018** | 38% | Method to adopt | Equalize normalized gradient norms at shared `[CLS]`; one knob α≈1.5. Second MTL arm vs Kendall |
| **LibMTL (JMLR 2023)** | 31% | Method (tool) | Wrap NeoBERT as shared backbone; swap `weighting=EW\|UW\|GradNorm\|PCGrad` by config → the whole MTL ablation at ~zero impl cost |
| **CSSRS hybrid 2025** | 31% | Baseline to beat | 4-level Reddit severity, weighted-F1 **0.75** (RoBERTa+TF-IDF+PCA) — comparison bar for the severity/crisis head |
| **LLM C-SSRS screening 2025** | 31% | Design lesson | Errors cluster between *adjacent* C-SSRS levels → use an **ordinal/distance-aware loss + metric** (MAE/QWK), not flat CE |
| **RSD-15K 2025** | 31% | Dataset (see below) | 15K user-level C-SSRS Reddit corpus, temporally ordered — but **not obtainable** (repo unpublished) |
| **NCUEE-NLP WASSA 2023** | 31% | Method to adopt | Affect-adapted init (RoBERTa-Twitter/EmoBERTa) lifts regression → add "domain-adapted init" as an ablation arm |
| **ESConv (ACL 2021)** | 31% | Dataset (acquired) | Human emotion-type + 1–5 intensity + strategy labels in-domain → calibration anchor for Gemini silver scores |
| **PCGrad 2020** | 27% | Method to adopt | Projects *conflicting* gradient directions — targets direction conflict (Kendall/GradNorm target scale); exempt the crisis head from projection |
| **Nash-MTL 2022** | 27% | Method to adopt | Scale-invariant bargaining update — keeps high-recall BCE gradient from being swamped by MSE/CE; note per-step solve cost |
| **MTL imbalance 2025** | 27% | Design lesson | Gradient-norm scaling ≈ grid search in vision; **untested under a recall floor** → the null hypothesis Pebble's experiment must rule out |
| **MentalBERT 2022** | 27% | Method to adopt | Domain-adaptive MLM on mental-health Reddit lifts downstream — short MLM pass on NeoBERT before head fine-tuning |
| **CSSRS label-smoothing 2024** | 23% | Baseline to beat | Same 500-user dataset Pebble has: CNN gets **43%→52%** acc, 47.8% macro-recall — the bar to clear |
| **PGKD (EMNLP 2024)** | 19% | Method to adopt | Iterative *error-targeted* distillation: feed the safety head's false-negatives back to Gemini for targeted silver examples |
| **RecAdam 2020** | 15% | Method to adopt | Anneal downstream loss + anchor to pretrained init → less forgetting on the tiny target set; drop-in optimizer for the unfreeze stage |
| **ModernBERT 2024** | 8% | Baseline to beat | Strongest same-class encoder alt (base 149M / large 395M, 8K ctx) — fine-tune the same 3-head stack to justify NeoBERT |
| **ULMFiT 2018** | 4% | Method (citation) | Canonical source for gradual unfreezing + discriminative LRs + STLR — cite for the staged-unfreeze schedule |

### Corrected metadata (from deep fetch)
- **PGKD** real id is **arXiv:2411.05045 / EMNLP 2024** (the ResearchGate link 403s); its teacher is **Claude-3**, student BERT-base.
- **ESConv** anthology id is **2021.acl-long.269** (arXiv:2106.01144).

---

## Dataset acquisition results (find-dataset agent, 2026-06-09)

| Dataset | Status | Location / gate | License → deploy? |
|---------|--------|-----------------|-------------------|
| **WASSA empathy/distress** (Buechel et al. 2018) | ✅ **acquired** | `data/external/wassa_empathy/messages.csv` (1,860 essays) | **CC-BY-4.0 → YES (deployable)** |
| **ESConv** (Liu et al. 2021) | ✅ **acquired** | `data/external/esconv/` (1,300 convs, 38K turns) | **CC-BY-NC-4.0 → research-only, NO deploy** |
| **RSD-15K** (2025) | ❌ not obtainable | Promised GitHub repo unpublished (404); no DUA/contact | unknown |
| **MentalBERT/RoBERTa** | weights available (not downloaded) | HF soft-gate; pretraining corpus private | CC-BY-NC-4.0 → research-only |

- **WASSA empathy** is a *deployment-compatible* continuous-affect source (maps `distress/7 → severity`, `empathy/7 → aux`) — joins CSSRS-Reddit in the deployed arm.
- **ESConv** adds in-domain human emotion + **1–5 intensity** labels → best use is a **calibration slice** to check Gemini silver scores against real human intensity (research arm only — NC license).
- **RSD-15K** substitute if needed: **UMD Reddit Suicidality** (GATED-DUA, IRB) or **SWMH** (CC-BY-NC, HF gate) — both research-only.
- **MentalBERT** weights are usable as a *research-arm* warm-start/baseline only (NC); the **deployed** encoder must warm-start from an openly-licensed backbone.

### Recommended next actions (from the analysis)
1. **C-SSRS severity head → ordinal loss** (LLM-screening + label-smoothing papers agree); targets to beat: 52% acc / 0.75 weighted-F1 / 47.8% macro-recall.
2. **MTL ablation via LibMTL**: static λ → Kendall → GradNorm → PCGrad/Nash-MTL, with the safety head's weight floored — Pebble's #1 novelty.
3. **Add two loaders** to `external.py`: `load_wassa_empathy()` (fills the existing `load_wassa_intensity` stub) and `load_esconv()` — both mirror `load_semeval_intensity`.

---

## Sources

- [LibMTL (JMLR 2023)](https://www.jmlr.org/papers/volume24/22-0347/22-0347.pdf) · [PCGrad](https://arxiv.org/abs/2001.06782) · [Nash-MTL](https://arxiv.org/abs/2202.01017) · [MTL imbalance re-analysis (2025)](https://arxiv.org/abs/2509.23915) · [Kendall 2018](https://arxiv.org/abs/1705.07115) · [GradNorm 2018](https://arxiv.org/abs/1711.02257)
- [PGKD (EMNLP 2024, arXiv:2411.05045)](https://arxiv.org/abs/2411.05045) · [ESConv (arXiv:2106.01144)](https://arxiv.org/abs/2106.01144) · [WASSA empathic-reactions data (Buechel 2018)](https://github.com/wwbp/empathic_reactions) · [LLM C-SSRS screening](https://arxiv.org/abs/2505.13480) · [RSD-15K](https://arxiv.org/abs/2507.11559)
- [MentalBERT (LREC 2022)](https://arxiv.org/abs/2110.15621) · [mental-roberta (HF)](https://huggingface.co/AIMH/mental-roberta-large)
- [LLM-KD for text classification (2024)](https://www.researchgate.net/publication/386201474) · [KD survey (2025)](https://link.springer.com/article/10.1007/s10462-025-11423-3)
- [C-SSRS label smoothing (2024)](https://arxiv.org/abs/2405.05795) · [C-SSRS hybrid (2025)](https://arxiv.org/html/2505.23797v1) · [LLM C-SSRS screening (2025)](https://arxiv.org/html/2505.13480v1) · [RSD-15K (2025)](https://arxiv.org/pdf/2507.11559)
- [WASSA@IITK 2021](https://arxiv.org/abs/2104.09827) · [NCUEE-NLP WASSA 2023](https://aclanthology.org/2023.wassa-1.49/)
- [ULMFiT (ACL 2018)](https://aclanthology.org/P18-1031.pdf) · [Recall and Learn / RecAdam (EMNLP 2020)](https://arxiv.org/pdf/2004.12651)
- [ModernBERT (2024)](https://arxiv.org/pdf/2412.13663) · [HEART (2026)](https://arxiv.org/pdf/2601.19922)
