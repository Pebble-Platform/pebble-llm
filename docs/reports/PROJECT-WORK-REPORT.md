# Pebble-LLM — Project Work Report

**Project:** Pebble-LLM — Crisis-sensitive affect modeling for text and voice
**Report date:** 2026-06-25
**Branch:** main
**Prepared by:** Research team

---

## 1. Executive Summary

The project runs **two parallel research workstreams**, each targeting an IEEE submission:

- **Text / Message** — Analyze a user's messages for **emotional tone (positive vs. negative)**, implemented as an ordinal suicide-risk classifier (R2 hierarchical dual-head).
- **Voice** — **Recall-floored heterogeneous heads** for crisis-sensitive speech affect.

Core experiments for both streams have produced **real, honest numbers**. The remaining critical-path items are **data acquisition / label-quality measurement**, not model code: κ label-quality for the text paper, and MSP-Podcast access for the voice paper. Both have external latency and should be started first.

| Workstream | Core experiments | Paper plan | Critical-path blocker |
|---|---|---|---|
| Text / Message | ✅ Done | ✅ Drafted | LLM-vs-gold κ overlap set |
| Voice | ✅ Backbone done; MTL pending | ✅ Drafted | MSP-Podcast access |

---

## 2. Task Status Table

| # | Task | Stream | Status | Key result / output |
|---|---|---|---|---|
| 1 | emotion2vec reproduction (RAVDESS linear-probe) | Voice | ✅ Done | v1+v2 evaluated; HF Space deployed |
| 2 | Enrich suicide-risk dataset → 10k | Text | ✅ Done | 10,073 samples; static viewer |
| 3 | R2 5-fold CV on Kaggle GPU (gold-holdout eval) | Text | ✅ Done | gold macro-F1 **0.357** vs 0.237 baseline |
| 4 | R2 beat-the-paper: dual report + Behavior rebalance | Text | 🟡 In progress | rebalanced gold macro-F1 **0.385** |
| 5 | Voice backbone selection (emotion2vec vs WavLM) | Voice | ✅ Done | WavLM wins, Δ −0.071 (3/3 seeds) |
| 6 | Voice MTL heads (emotion + affect CCC + crisis) | Voice | 🟡 In progress | kernel built; Kaggle run pending (M3–M5) |
| 7 | Paper 1 plan (Text, IEEE) | Text | ✅ Drafted | `PAPER-PLAN-text-ordinal-suicide.md` |
| 8 | Paper 2 plan (Voice, IEEE) | Voice | ✅ Drafted | `PAPER-PLAN-voice-crisis-affect.md` |

---

## 3. Experimental Results

### 3.1 Text — R2 Hierarchical Dual-Head

**Table I.** *Suicide-risk classification under three evaluation protocols (4-level C-SSRS). "Cross-to-gold" is the honest, non-circular protocol: train on LLM labels, evaluate on held-out clinical gold.*

| Protocol | Train labels | Eval labels | Macro-F1 | QWK |
|---|:--:|:--:|:--:|:--:|
| Gold-CV | gold | gold | 0.190 | 0.241 |
| Within-LLM *(circular)* | LLM | LLM | 0.670 | — |
| **Cross-to-gold (ours)** | LLM | gold | **0.385** | **0.378** |

*5-fold std = 0.007. Within-LLM is shown only to expose circularity; it is not a valid accuracy claim.*

**Table II.** *Per-class macro-F1 under the gold-holdout (cross-to-gold) protocol.*

| Class | Indicator | Ideation | Behavior | Attempt |
|---|:--:|:--:|:--:|:--:|
| Macro-F1 | 0.50 | 0.48 | **0.18** | 0.37 |

*Behavior collapses to 0.18 (rare class, 6.5% of pool) — flagged as a clinical limitation.*

### 3.2 Voice — Backbone & Crisis Head

**Table III.** *Speech-affect backbone selection on RAVDESS (frozen probe, 8-class emotion, mean ± std over 3 seeds). Paired delta computed per seed.*

| Backbone | Params | Macro-F1 |
|---|:--:|:--:|
| emotion2vec | ~94 M | 0.537 ± 0.007 |
| **WavLM-Large (ours)** | ~316 M | **0.609 ± 0.019** |
| Paired Δ (WavLM − emotion2vec) | — | −0.071 ± 0.017 |

*WavLM wins on 3/3 seeds (all paired deltas < 0).*

**Table IV.** *Recall-floored distress (crisis) head — operating point under a hard recall constraint.*

| Constraint | Threshold | Precision |
|---|:--:|:--:|
| Recall ≥ 0.90 | 0.69 | 0.617 ± 0.003 |

*Precision reported at the recall floor; full precision–recall curve in the paper.*

---

## 4. Deliverables Shipped

- emotion2vec reproduction + multi-model tester + Hugging Face Space deployment.
- Voice affect web demo (FastAPI + static sample picker).
- Headless Kaggle GPU run driver (drive GPU runs from session).
- Suicide-risk dataset enriched to 10k + static dataset viewer + fetch script.
- 23+ structured paper reading notes (related-work base for both papers).

---

## 5. Two-Paper Plans (IEEE)

### Paper 1 — Text
*Weakly-Supervised Augmentation for Ordinal Suicide-Risk Classification: An Honest Gold-Holdout Study.*
**Done:** dual-head + tri-objective architecture, 3-point comparison, per-class gold.
**Remaining:** 🔴 LLM-label quality (Cohen's κ vs gold) · 🔴 ablation table (CORAL vs CE, ±augment, ±balance, ±focal) · baselines · Behavior-collapse fix · ethics & provenance.

### Paper 2 — Voice
*Backbone Selection and Recall-Floored Heterogeneous Heads for Crisis-Sensitive Speech Affect.*
**Done:** paired-delta backbone selection, recall-floor distress head, end-to-end verifier.
**Remaining:** 🔴 MSP-Podcast access + loader (real V/A/D labels) · 🔴 Kaggle MTL-heads run (M3–M5) · 🔴 CCC affect head on real labels · ablation (Kendall vs GradNorm/PCGrad) · eGeMAPS SER baseline.

---

## 6. Critical Path & Next Actions

| Priority | Action | Stream | Why now |
|---|---|---|---|
| 🔴 1 | Verify the LLM↔gold overlap set exists; compute Cohen's κ | Text | Gates Paper 1 contribution #3; external latency |
| 🔴 2 | Submit MSP-Podcast access request (+ define fallback) | Voice | Longest external latency; gates Paper 2 affect head |
| 🟡 3 | Run Kaggle MTL-heads (M3–M5); pull 10-fold metrics | Voice | In our control; can run in parallel while waiting on data |
| 🟡 4 | Lock the 0.385 number; run the 4-config ablation + 2 baselines | Text | Every table/abstract depends on the locked number |

**Key risk:** both critical-path items are *data/label acquisition*, not model code — start them first because their latency is outside our control.

---

*Sources: `docs/papers/finetuning-message/PAPER-PLAN-text-ordinal-suicide.md`, `docs/papers/voice/PAPER-PLAN-voice-crisis-affect.md`, `docs/tasks/*.md`, `kaggle/finetuning-message/r2-suicide-risk-dualhead/KET-QUA-PHAN-TICH.md`.*
