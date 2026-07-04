---
marp: true
title: "Pebble Emotion Classifier — Related-Work Report"
paginate: true
theme: default
---

<!-- _class: lead -->

# Pebble Emotion Classifier
## A Multi-Task NeoBERT for Mental-Health Affect — Where It Sits in the Literature

**Research report**

Student: Nguyen Duy Tan Phat · Advisor: Nguyen Si Thin
Date: 2026-06-16

> Source material: `docs/related-work-survey.md`, `docs/related-work-enrichment.md`, `docs/papers/`

---

## Agenda

1. **Problem & system** — what Pebble's classifier is
2. **Research question** — the novelty we are chasing
3. **Method of the review** — how papers were found & scored
4. **Closest systems** — the 5 nearest papers
5. **Enrichment set** — 18 papers by methodological pillar
6. **Synthesis** — the gap in the literature
7. **Contribution** — what Pebble can claim
8. **Status & next steps**

---

## The problem

Pebble is an emotional-support chat system. Today a **single Gemini call** does *both* emotion scoring **and** response generation — the two are entangled in one pass.

**Goal:** split them. Put a dedicated, fine-tuned **emotion classifier** *before* generation, feeding structured scores to a Decision Engine.

Why this matters:
- **Consistency** — a specialist scores a narrow rubric more stably than a prompted generalist.
- **Decoupling** — a self-hosted classifier is independent of generator-model churn.
- **No JSON failures** — an encoder emits typed head tensors, not parseable text.

---

## The system under study — "Pebble in one paragraph"

Fine-tune **NeoBERT** (250M-param encoder) into a **multi-task affect classifier** with three heterogeneous heads on a shared `[CLS]`:

| Head | Type | Outputs |
|---|---|---|
| **Score head** | sigmoid regression | `energy`, `severity`, `socialIsolation`, `receptivity` |
| **Emotion head** | softmax | 12-label taxonomy, warm-started from GoEmotions |
| **Safety head** | binary BCE | crisis flag, target **recall ≥ 0.95** |

Loss = MSE + CE + BCE · staged training (freeze encoder → unfreeze) · planned escalation to **Kendall uncertainty weighting / GradNorm** if heads diverge.

> v1 scope: learn `detectedEmotion` (GoEmotions) + `severity` (SemEval intensity); other dims are heuristics.

---

## The research question

> Three head **types** on one encoder — regression **+** classification **+** a high-recall safety BCE — with the safety head under a **hard recall floor (≥ 0.95)**.

**No published affect classifier in our survey** jointly optimizes continuous affect regression *while* enforcing a hard recall constraint on a crisis head.

That asymmetric, recall-constrained, **heterogeneous** multi-task regime is the unclaimed area we position against.

---

## How the review was done

**Two layers, both reproducible:**

- **Closest systems (5 papers)** — deep 11-section dossiers: dataset · architecture · multi-task setup · results · limitations · gap-vs-Pebble.
- **Enrichment set (18 papers)** — organized by Pebble's *methodological pillars*; picked for **actionability** (a baseline to run, a backbone to try, a method to adopt, a dataset to add).

**Closeness scored on a 7-dimension rubric** → overlap %:

`Overlap = (Σ wᵢ · scoreᵢ) / 26 × 100`

---

## The 7 closeness dimensions (the rubric)

| Dim | Weight | What it measures |
|---|:--:|---|
| **D1** | ×3 | Heterogeneous heads (categorical **+** continuous) on shared encoder |
| **D2** | ×2 | Mental-health text classification with transformers |
| **D3** | ×1 | Transfer from GoEmotions / EmpatheticDialogues |
| **D4** | ×2 | Silver-label distillation from a teacher LLM |
| **D5** | ×2 | Principled multi-task loss balancing (uncertainty / GradNorm) |
| **D6** | ×2 | Hard safety-recall constraint on a crisis head |
| **D7** | ×1 | Encoder backbone choice |

Weights encode *what makes a paper close to Pebble*, not just topically related.

---

## Closest systems — the 5 nearest papers

| # | Paper | Venue | Theme |
|---|---|---|---|
| 1 | **FAIIR** | npj Digital Medicine 2025 | Crisis-line multi-label classification (780K convs) |
| 2 | **Ghosh et al. VAD-MTL** | IPM 2022 | Emotion **+** intensity on suicide notes |
| 3 | **Pathak et al. CFN** | ACM THC 2025 | Tri-task: disorder + emotion + sentiment |
| 4 | **Emo Pillars** | ACL Findings 2025 | LLM-teacher distillation over GoEmotions |
| 5 | **Sharma et al.** | EMNLP 2020 | Empathy in text-based mental-health support |

> These are the *closest in idea and method* — each shares some, never all, of Pebble's pieces.

---

## #1 FAIIR — the production analogue

**Ensemble of domain-adapted encoders → 19 clinical "issue tags"** on ~780K Kids Help Phone youth crisis conversations.

- AUROC **0.94**, sample-F1 **0.64**, recall **0.81**; **90.9% agreement** with responders.
- Experts trusted FAIIR **more than the original labels** (label noise).

**Overlap:** D2, D7, partial D1.
**Gap vs Pebble:** purely multi-label *categorical* — no continuous heads, no task-weight balancing, no LLM-teacher distillation, no formalized recall trade-off.

---

## #2 Ghosh & #3 Pathak — multi-task affect

**Ghosh et al. (IPM 2022)** — BERT/RoBERTa + VAD lexicon → **softmax emotion + regression intensity** on CEASE-v2.0 suicide notes. Best Mean Recall 65.25% (+3.78 over SOTA).
→ *Closest to D1 (categorical + continuous), but two tasks only, static weights, no safety head.*

**Pathak et al. (ACM THC 2025)** — "Core Fusion Network", **tri-task** (disorder + emotion + sentiment), private/shared feature spaces. Tri > bi > uni-task.
→ *Auxiliary outputs are categorical, not continuous; no uncertainty weighting; semi-automatic silver labels.*

---

## #4 Emo Pillars & #5 Sharma — distillation & empathy

**Emo Pillars (ACL Findings 2025)** — **Mistral-7B teacher** synthesizes 400K silver examples → RoBERTa student, GoEmotions macro-F1 **0.55** (SOTA).
→ *The template for D4 (teacher→student), but single multi-label head only — no regression, no safety, no MTL-balancing problem.*

**Sharma et al. (EMNLP 2020)** — RoBERTa **bi-encoder** for empathy (3 mechanisms × 3 levels) + rationale extraction on TalkLife/Reddit. Macro-F1 ≈ 0.73–0.74.
→ *Hand-tuned static λ; no continuous heads; no safety head; no LLM teacher.*

---

## Enrichment set — 18 papers by pillar

| Pillar | Papers | Role for Pebble |
|---|---|---|
| **1 · MTL balancing** | Kendall, GradNorm, PCGrad, Nash-MTL, **LibMTL**, MTL-imbalance | Methods + library for the novelty experiment |
| **2 · MH encoders** | MentalBERT/RoBERTa | Backbone/baseline vs NeoBERT |
| **3 · LLM distillation** | PGKD, KD survey | Frame the Gemini→NeoBERT setup |
| **4 · C-SSRS severity** | label-smoothing, hybrid, LLM-screening, RSD-15K | Safety-head baselines + ordinal-loss lesson |
| **5 · Intensity/empathy** | WASSA@IITK, PVG, NCUEE-NLP | Continuous-head transfer + Pearson baselines |
| **6 · Staged fine-tuning** | ULMFiT, RecAdam | Warm-start / unfreeze ablation |
| **7 · Encoder & domain** | ModernBERT, ESConv, HEART | Backbone alt + in-domain data |

---

## Overlap scores — the honest finding

All enrichment papers are **peripheral (<40%)** except one — they are *method/baseline/dataset* contributors, not close *systems*.

| Paper | Overlap | Type |
|---|:--:|---|
| **WASSA@IITK 2021** | **42%** | Baseline to beat (closest reg+cls MTL) |
| Kendall 2018 / GradNorm 2018 | 38% | Method to adopt |
| LibMTL · CSSRS-hybrid · ESConv · NCUEE | 31% | Tool / baseline / dataset |
| PCGrad · Nash-MTL · MentalBERT | 27% | Method / design lesson |
| ModernBERT (8%) · ULMFiT (4%) | low | Backbone alt / citation |

---

## Synthesis — gaps in the literature

- **Continuous regression heads are rare** — mostly VAD or empathy/distress; **never a safety/crisis binary** alongside them.
- **Static / grid-searched λ is the default** — principled balancing (Kendall, GradNorm) is mostly a *vision* technique, sporadic in NLP affect.
- **Reliance on noisy silver labels** + teacher-LLM bias is acknowledged but under-studied for *continuous* dimensions.
- **A hard recall floor on a crisis head is essentially absent** — FAIIR has a suicidality tag but doesn't formalize the trade-off.

> **The unclaimed area:** heterogeneous (regression + classification + BCE) MTL **under a hard crisis-recall constraint**.

---

## What Pebble can contribute (ranked)

1. **Heterogeneous multi-head balancing for safety-critical affect** *(strongest)* — static λ **vs** Kendall **vs** GradNorm when one head is a high-recall BCE crisis head.
2. **Distilling a frontier LLM into a small multi-task affect encoder** — teacher-level agreement on continuous dims *while preserving a hard recall floor*.
3. **GoEmotions warm-start + staged unfreezing** for low-resource conversational affect (ablation).
4. **Calibration of teacher-LLM silver labels** on continuous dimensions.

---

## Recommended paper angle

> *"Distilling a frontier LLM into a NeoBERT student for mental-health affect classification under a hard crisis-recall constraint, with uncertainty-weighted multi-task balancing across regression + classification + safety heads."*

- Bundles novelty **(1)** + distillation **(2)** — the largest unclaimed area.
- **(3)** becomes the warm-start ablation; **(4)** becomes the calibration section.
- Natural fit: **EMNLP / ACL Findings / WASSA / CLPsych**.

---

## Datasets — acquisition status

| Dataset | Status | Deploy? |
|---|---|---|
| **GoEmotions** (emotion) | in use | open |
| **SemEval-2018 EI-reg** (severity) | in use | open |
| **WASSA empathy/distress** | ✅ acquired | **CC-BY-4.0 → yes** |
| **ESConv** (in-domain support) | ✅ acquired | CC-BY-NC → research-only |
| **CSSRS-Reddit** (C-SSRS severity) | ✅ acquired | research arm |
| **RSD-15K** | ❌ repo unpublished | n/a |

> Baselines to beat: C-SSRS **52% acc / 0.75 weighted-F1**; WASSA empathy/distress Pearson r ≈ 0.53.

---

## Where the project is now

- **Phase 0 done** — NeoBERT revision pinned & modeling code vendored; **Kaggle GPU smoke test = GO** (loads + forward/backward on P100, pinned stack).
- **Phase 5 in progress** — severity & emotion loaders done; masked multi-task assembler done (each example activates only its labeled head).
- **v1 pivot** — reuse public labels (no Gemini silver labels / no human annotation yet); learn `detectedEmotion` + `severity`, the rest heuristic.

---

## Next steps

1. **Emotion-head pre-train loop** + trainer with masked multi-task loss (Phase 6).
2. **MTL ablation via LibMTL** — static λ → Kendall → GradNorm → PCGrad/Nash-MTL, with the safety head's weight **floored**. *(the #1 novelty)*
3. **Ordinal loss** for the C-SSRS severity/crisis head (MAE / QWK, not flat CE).
4. Evaluate on **Protocol B** against §7 targets: severity MAE < 0.15 · emotion macro-F1 > 0.65 · safety recall > 0.95.

---

<!-- _class: lead -->

## Thank you

**Questions?**

Key references:
FAIIR (npj Digital Medicine 2025) · Ghosh et al. (IPM 2022) · Emo Pillars (ACL Findings 2025) · Sharma et al. (EMNLP 2020) · Kendall et al. (CVPR 2018) · GradNorm (ICML 2018) · LibMTL (JMLR 2023) · WASSA@IITK (2021)

> Full survey: `docs/related-work-survey.md` · `docs/related-work-enrichment.md`
