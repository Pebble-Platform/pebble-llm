# Reproduce emotion2vec (paper #25) — RAVDESS linear-probe, Kaggle → local test

- **Slug:** emotion2vec-reproduction
- **Status:** done
- **Created:** 2026-06-21  ·  **Updated:** 2026-06-21 (all milestones done; v1+v2 evaluated)
- **Owner:** Fabio (agent: Claude)

## Goal
Empirically reproduce the core claim of emotion2vec (ACL Findings 2024, paper #25) — that a **frozen
emotion2vec encoder + a small SUPERB linear probe** is a top speech-emotion representation — on the one
open dataset the paper reports that we have locally (**RAVDESS**), train on **Kaggle GPU**, pull the
artifact to local, build a sample-test harness, and **compare our run's WA/UA/WF1 against the paper's
reported numbers** (Table 3: emotion2vec RAVDESS **WA 82.43 / WF1 82.86**). "Done" = a results table that
puts our numbers next to the paper's with an honest analysis of the gap and its causes.

## Requirements & Constraints
- **Functional:**
  - Frozen emotion2vec_base features → **SUPERB head** (two linear layers + ReLU between, hidden 256) →
    8-way RAVDESS emotion classification. Report **WA (accuracy), UA (macro-recall), WF1 (weighted-F1)**.
  - Include **WavLM-Large** as the thesis's mandatory comparator (and optionally data2vec-2.0, the paper's
    Table-3 comparator) under the same probe — so the run doubles as the thesis backbone comparison.
  - Train on **Kaggle GPU** (kernel pushed via the repo's existing flow), pull artifacts to local.
  - Local **sample-test harness**: load the pulled artifact, run inference on a held-out RAVDESS clip,
    print predicted emotion + scores. Reuse `src/pebble_llm/serving/voice_app.py` + `scripts/voice_verify_client.py` where possible.
  - Final **evaluation doc/section**: our WA/UA/WF1 vs paper, per-backbone, with gap analysis.
- **Constraints:**
  - **IEMOCAP (the 71.79 headline) is gated** → cannot reproduce; RAVDESS is the reproduction target.
  - RAVDESS is **out-of-domain** in the paper (not in pretraining), so 82.43 is a *generalization* number
    — a fair reproduction target with no train/test-leakage advantage.
  - Match the paper's **frozen** recipe (no backbone fine-tune), checkpoint `iic/emotion2vec_base`.
  - Reuse existing pilot infra (`kaggle/voice/pebble-voice-backbone/`), do not refactor it; new work goes
    in a **separate kernel** so the pilot stays intact (surgical).
  - Local env = `.venv-voice` (py3.12, torch 2.2.2 CPU, Intel-mac; soundfile+torchaudio, no librosa).
  - Kaggle auth via `~/.kaggle/access_token` → built into `kaggle.json` (user `fabiocarava`).
- **Non-goals:** continuous regression head, safety/crisis head, fusion with NeoBERT, fine-tuning the
  backbone, child-voice validation — all out of scope for this *paper reproduction* (they are thesis work,
  tracked elsewhere). This task answers only: "can we reproduce the paper's RAVDESS linear-probe number?"

## Milestones
- [x] M1 — Protocol locked — random 10-fold 80/10/10 (all 1440, 8 classes) + SUPERB head recipe researched & recorded (OQ1, OQ2 resolved)
- [x] M2 — Repro kernel built — `kaggle/voice/pebble-emotion2vec-repro/` (5 cells) builds a 13-cell .ipynb; cells compile; local infer script `scripts/emotion2vec_repro_infer.py` ready
- [ ] M3 — Kaggle run green — pushed, ran on GPU, `out/` pulled with results + artifact bundle
- [ ] M4 — Local sample test — pulled artifact loads locally and classifies a held-out RAVDESS clip end-to-end
- [x] M5 — Evaluation — v1+v2 WA/UA/WF1 vs paper Table 3 with gap analysis + thesis takeaways (see Final verdict)

## Decision Log
<!-- newest first -->
- **2026-06-21 — Run v2 = frame-level pooling (faithful SUPERB recipe)** [user-approved]: v1's pool-before
  -Linear deviation is the leading hypothesis for the −9 WA gap; the EmoBox/emotion2vec `SuperbBaseModel`
  pools *after* `Linear+ReLU` on frame features. v2 extracts frame-level `(T,d)` feats (emotion2vec
  `granularity="frame"`, WavLM `last_hidden_state`), head does `Linear→ReLU→masked-mean(flen)→Linear`. Same
  kernel (version 2), output pulled to `out2/` to preserve v1. Rejected: accept v1 as-is (gap untested).
- **2026-06-21 — Probe recipe = SUPERB head `Linear(d,256)→ReLU→Linear(256,8)`, single-layer frozen
  feats, CE, Adam lr 1e-3 ~100 ep, no normalization:** matches the EmoBox/emotion2vec downstream recipe
  (Research OQ2); pilot extractors already give the correct single-layer utterance features → reuse them.
  Rejected: SUPERB 25-layer learnable weighted-sum (neither emotion2vec nor EmoBox used it).
- **2026-06-21 — Eval protocol = random 10-fold CV, 80/10/10, all 1440 clips, all 8 classes, multi-seed
  mean±std:** this is the emotion2vec paper's own stated RAVDESS protocol (Research OQ1) → the only split
  that is directly comparable to Table 3's 82.43. Rejected: the pilot's fixed actors-1-20/21-24 split and
  EmoBox's 6-fold speaker-independent CV (both produce non-comparable numbers).
- **2026-06-21 — Reproduction target = RAVDESS, frozen SUPERB linear-probe, metrics WA/UA/WF1:** RAVDESS
  is the only open dataset both downloaded locally and reported in the paper (Table 3, WA 82.43 / WF1 82.86);
  IEMOCAP (the 71.79 headline) is gated. The paper's claim is "frozen encoder + small head is enough", so
  the faithful test is the SUPERB linear probe, scored by the paper's own metrics (WA/UA/WF1), not Pebble's
  macro-F1/recall. Rejected: (a) reproducing IEMOCAP 71.79 — data gated; (b) reusing the existing pilot's
  Pebble-head metrics — those measure a different (Pebble) task, not the paper.
- **2026-06-21 — Include WavLM-Large as comparator, separate kernel:** the thesis requires emotion2vec-vs-
  WavLM-Large as a mandatory comparison (deep-read Decision 1), and the pilot already extracts both, so
  adding WavLM-Large to the repo is nearly free and makes the run serve double duty. New kernel
  `pebble-emotion2vec-repro` (not editing the pilot) keeps changes surgical. data2vec-2.0 (paper's Table-3
  comparator, 81.04) is an optional stretch arm.
- **2026-06-21 — Reuse pilot feature-extraction + Kaggle flow verbatim:** `c3_features.py` already extracts
  frozen emotion2vec (utterance granularity, 768-d) and WavLM-Large (mean-pool, 1024-d); the auth/push/pull
  recipe is documented and verified. Only the **head + metrics + split** change for paper-faithfulness.

## Open Questions
- [x] **OQ1 — RAVDESS eval protocol** → RESOLVED: random 10-fold CV, 80/10/10, all 1440 clips, all 8
  classes, multi-seed mean±std (see Research OQ1 + Decision Log).
- [x] **OQ2 — SUPERB downstream recipe** → RESOLVED: `Linear(d,256)→ReLU→Linear(256,8)`, single-layer
  frozen feats, CE, no layer-weighting/normalization (see Research OQ2 + Decision Log).

## Research Findings

### OQ1 — RAVDESS evaluation protocol (task-researcher, 2026-06-21, confidence: high)
- **Verdict:** The emotion2vec paper's own §5.1 (arXiv 2312.15185v1) states RAVDESS/SAVEE use a
  **random leave-one-out 10-fold CV**: "all samples within the dataset are randomly split into 80%,
  10%, 10% train/val/test". So Table 3's 82.43 = **random 10-fold, all 1440 speech clips, all 8 classes,
  mean of per-fold metrics**. Seed unspecified (IEMOCAP config uses seed=42) → run multiple seeds, report
  mean±std (expect ±0.5–2% from seed).
- **Metric-label correction:** Table 3 columns are **WA 82.43 / UA 82.86 / WF1 82.39** (the deep-read's
  "RAVDESS WF1 82.86" mislabels UA as WF1). WF1 = sklearn `f1_score(average="weighted")`; WA = accuracy;
  UA = macro-recall (`recall_score(average="macro")`).
- **Do NOT use EmoBox's 6-fold speaker-independent folds** for this target — EmoBox (Interspeech 2024) is
  a *later* toolkit with a different protocol; its folds won't reproduce 82.43. (Researcher 2 inferred the
  number came from EmoBox; the emotion2vec paper predates EmoBox and its §5.1 text is the authoritative
  source — random 10-fold wins.)
- **Sources:** [emotion2vec arXiv HTML §5.1](https://arxiv.org/html/2312.15185v1) ·
  [WF1 def in repo utils.py](https://github.com/ddlBoJack/emotion2vec/blob/main/iemocap_downstream/utils.py) ·
  [EmoBox data/ravdess (6-fold, NOT used here)](https://github.com/emo-box/EmoBox/tree/main/data/ravdess).

### OQ2 — SUPERB linear-probe recipe (task-researcher, 2026-06-21, confidence: high)
- **Head (both backbones, identical):** `Linear(d,256) → ReLU → mean-pool-over-time → Linear(256, 8)`.
  **No** dropout, **no** layernorm, **no** learnable layer weighted-sum. Loss = cross-entropy.
- **Features = single (last) layer, frozen, NOT a SUPERB 25-layer weighted-sum.** emotion2vec
  `granularity="utterance"` already returns the mean of last-layer frame feats (768-d) → feed directly
  (mean of 1 = identity). WavLM-Large = `last_hidden_state` mean-pool over time (1024-d). **The existing
  pilot `c3_features.py` extractors are already correct — reuse verbatim.**
- **No feature normalization** by default (fallback: per-utterance `F.layer_norm` only if WA < 75%).
- **Probe hyperparameters:** two documented recipes — EmoBox (Adam, lr 1e-4, batch 32, 20 ep) vs
  emotion2vec iemocap_downstream (RMSprop+CyclicLR, lr 5e-4, batch 128, 100 ep, wd 1e-5). On a tiny linear
  probe over cached features the optimizer is second-order; use Adam, lr 1e-3, ~100 ep, wd 1e-4, CE, and
  report mean±std. Minor known deviation: pilot pools *before* the first Linear (utterance feats), the repo
  pools *after* the first Linear+ReLU — accept this (emotion2vec's utterance granularity is the intended
  representation), note it in M5.
- **Sources:** [EmoBox SuperbBaseModel](https://github.com/emo-box/EmoBox/blob/main/examples/sb/classifier_head.py) ·
  [emotion2vec model.py](https://github.com/ddlBoJack/emotion2vec/blob/main/iemocap_downstream/model.py) ·
  [s3prl canonical SUPERB ER config](https://github.com/s3prl/s3prl/blob/master/s3prl/downstream/emotion/config.yaml).

## Completed Work
- 2026-06-21 — Analyzed request, read deep-read (`docs/papers/voice/25-emotion2vec.md`) + existing pilot
  (`kaggle/voice/pebble-voice-backbone/`), confirmed reproduction target & gaps — this doc.
- 2026-06-21 — M1: resolved OQ1/OQ2 via 2 task-researchers (random 10-fold 80/10/10; SUPERB head recipe).
- 2026-06-21 — M2: built repro kernel `kaggle/voice/pebble-emotion2vec-repro/` (c1–c5 + build_ipynb +
  metadata + README), reusing pilot extractors; head=SUPERB, metrics=WA/UA/WF1, split=random 10-fold.
  All cells `py_compile` clean; .ipynb (13 cells) valid. Local test harness `scripts/emotion2vec_repro_infer.py`.
- 2026-06-21 — M3: pushed to Kaggle (GPU). Kaggle slugged from title → id
  `fabiocarava/pebble-emotion2vec-reproduction` (metadata synced). v1 done (~7.5 min) → pulled to `out/`.
- 2026-06-21 — M4: pulled `artifact_wavlm-large` runs end-to-end locally in `.venv-voice`
  (`scripts/emotion2vec_repro_infer.py`).
- 2026-06-21 — v2 (frame-level pooling, kernel version 2) → pulled to `out2/`; M5 evaluation + verdict
  written (gap −9.3→−5.4, WavLM>emotion2vec inversion holds). Status: done.

## Results — run v1 vs paper (Kaggle run `pebble-emotion2vec-reproduction`, 2026-06-21)

| Backbone | WA | UA | WF1 | Paper (Table 3) | ΔWA |
|---|---|---|---|---|---|
| **emotion2vec** | **73.12 ±3.33** | 72.41 ±3.49 | 72.78 ±3.52 | 82.43 / 82.86 / 82.39 | **−9.31** |
| wavlm-large | 77.15 ±2.95 | 76.84 ±3.44 | 76.97 ±2.96 | (paper has WavLM-*base* 37.01 only) | — |

- **Directional reproduction:** emotion2vec lands ~9–10 pts under the paper's RAVDESS number; both
  backbones are far above chance (12.5%) → features are valid, not degraded.
- **Inversion vs paper:** here **WavLM-Large > emotion2vec (+4.03 WA)**, opposite to the paper's
  emotion2vec>WavLM on IEMOCAP. Caveat: the paper never reports WavLM-*Large* on RAVDESS (only base 37.01).
- **Gap causes (ranked):**
  1. **(leading) frame-vs-utterance pooling.** Our v1 probe pools the frozen features to ONE vector, then
     `Linear→ReLU→Linear`. The paper/EmoBox reference pools *after* the first `Linear+ReLU` on **frame-level**
     (T×d) features (`SuperbBaseModel`) — strictly more expressive (keeps temporal detail). This was the
     accepted OQ2 deviation; likely worth several points, and plausibly hurts emotion2vec more (its value is
     in frame dynamics) → could explain both the gap AND the inversion.
  2. **modelscope 401 → HF fallback.** `iic/emotion2vec_base` (FunASR-packaged) 401'd; code fell back to
     `emotion2vec/emotion2vec_base` (raw HF). Possible minor pipeline diff (e.g. utterance special-token).
  3. **probe hyperparameters** not the paper's exact (unpublished) RAVDESS config; **random-split variance**
     ±3.3 with unspecified seed.
### Results — run v2 (frame-level pooling, faithful SUPERB recipe, `out2/`)

| Backbone | v1 WA | **v2 WA** | Δ(v2−v1) | v2 UA | v2 WF1 | Paper WA | Gap v2 |
|---|---|---|---|---|---|---|---|
| **emotion2vec** | 73.12 | **77.01 ±2.37** | **+3.89** | 76.13 | 76.73 | 82.43 | **−5.42** |
| wavlm-large | 77.15 | **80.56 ±2.50** | **+3.41** | 80.01 | 80.43 | (n/a) | — |

- **Pooling hypothesis CONFIRMED.** Switching to the faithful "pool-after-`Linear+ReLU`, masked over valid
  frames" recipe lifted **both** backbones ~+3.5–3.9 WA and cut variance (±3.3→±2.4). It closed ~40% of the
  v1 gap (−9.31 → −5.42). `flen mean=185/250` frames → masking is active (clips avg ~3.7s of 5s).
- **Residual −5.42 gap persists.** Most likely remaining causes: (a) emotion2vec loads via the **HF
  fallback** `emotion2vec/emotion2vec_base` (modelscope `iic/...` 401'd) — the raw HF checkpoint may differ
  from the FunASR-packaged pipeline the paper used (e.g. the utterance special-token representation); (b)
  unpublished exact RAVDESS probe hyperparameters + seed; (c) intrinsic random-split sensitivity.
- **WavLM-Large > emotion2vec inversion HOLDS** under the faithful recipe (−3.54 WA, was −4.03). A robust
  finding in this RAVDESS setup. Caveat: the paper never reports WavLM-*Large* on RAVDESS (only base 37.01),
  and our emotion2vec is the HF-fallback checkpoint — so this is a strong signal, **not** a clean refutation.
- **Local test (M4):** pulled `artifact_wavlm-large` (both v1 utterance-head and v2 frame-head) loads in
  `.venv-voice`, extracts features on CPU, predicts end-to-end (`scripts/emotion2vec_repro_infer.py`); v2
  prediction is sharper (`angry` p=0.897). ✅

## Final verdict (M5)

**Reproduction: directional success, ~5 WA short of the paper.** With the faithful SUPERB recipe our frozen
emotion2vec linear-probe reaches **WA 77.0** on RAVDESS vs the paper's **82.43** — same regime, ~5 pts low,
gap mostly explained (HF-fallback checkpoint + unpublished probe config + split variance). The single biggest
controllable factor was **pool-after-linear** (+3.9 WA), now fixed.

**Thesis-relevant takeaways** (feed back to `docs/related-work-voice-multimodal.md` Decision 1):
1. **The "mandatory WavLM-Large comparator" decision is vindicated** — WavLM-Large beat emotion2vec on
   RAVDESS in *both* runs (+3.5–4.0 WA). On out-of-domain spontaneous-ish acted speech the emotion specialist
   did **not** dominate the strong generalist. Keep WavLM-Large as a funded arm, not a fallback.
2. **Frozen linear probe is a strong, low-variance baseline** (WA 77–80 with a 0.2M head) — supports the
   thesis's "freeze emotion2vec in v1" decision (deep-read Decision 2).
3. **Reproduce-the-headline caution:** acted RAVDESS sits at ~77–82; the honest spontaneous bar (paper MELD
   ~52) is far lower — set crisis-recall feasibility against the spontaneous figure, not RAVDESS.

**Open follow-ups (not blocking; out of this task's scope):** try the FunASR-packaged checkpoint once
modelscope is reachable (or `emotion2vec+` large) to test if the −5.4 residual is checkpoint-driven; add a
fixed-seed sweep to bound split variance.

## Remaining Action Items
- [x] v2 frame-level refinement run + evaluated (gap −9.3 → −5.4; inversion holds).
- [x] M5 evaluation writeup — done (this section).
- [ ] (optional, future) FunASR-packaged / emotion2vec+ checkpoint test for the residual gap.
