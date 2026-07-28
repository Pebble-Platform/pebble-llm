# ViEmoSpeech benchmark-survey — reproduce SER methods on the labeled corpus & measure

- **Slug:** viemospeech-benchmark-survey
- **Status:** in-progress
- **Created:** 2026-07-13  ·  **Updated:** 2026-07-13
- **Owner:** user (dev.phatdt) / agent

## Goal
Write an **empirical benchmark-survey paper**: take the methods surveyed in the 29
deep-read papers (`docs/papers/**`), select the subset reproducible on the
**ViEmoSpeech** corpus (the TV-drama SER dataset we built + labeled), **re-implement
and run ~6 core methods on one dataset**, and **measure** them under one honest
protocol — emotion (macro-F1), valence/arousal (CCC), distress (recall) — evaluated on
a **held-out human-gold test set**, speaker-disjoint from train. Deliverable = a
survey/benchmark paper draft (EN first) with a reproducible results table + the
tone×emotion analysis the corpus exists to answer.

## Requirements & Constraints
- **Functional:** one dataset (ViEmoSpeech, our corpus); ~6 core methods; one shared
  split + metric module; a results table + analysis; a written paper.
- **Data (user, 2026-07-13, revised):** **assume the full 3,611-utt corpus is
  human-labeled** (labels of record = the corpus labels; real human labeling of the
  remainder is out of scope for this task). This supersedes the earlier Option C
  (156-only test) — see Decision Log. Split = **whole-series speaker-disjoint holdout**
  (ADR-002): one series trains, the other tests; both carry gold labels.
- **Hard invariants (non-negotiable, bind regardless of Q1):**
  - **Speaker-disjoint** train/test (I3 / ADR-002 spirit): drop from TRAIN every utt
    whose speaker appears in the human-gold TEST. Enforced, measured, reported.
  - Media legality (I1): clips/manifest never leave the machine; the paper releases
    features+timestamps+labels+speaker-ids only. Kaggle dataset stays **private**.
  - Provenance: every number traces to a committed script + a generated report.
  - Distress = acted-drama proxy, stated plainly (not clinical).
- **Compute (user Q3):** Kaggle P100/T4 only → **frozen SSL backbones + light
  heads/fusion**; NO large-backbone fine-tune, NO 7B ALM.
- **Non-goals:** new data collection; more human labeling as a *blocker* (optional
  milestone only); the archived text/voice thesis streams.

## Method set (user Q2 = Core 6) — each traced to a deep-read
1. **MFCC + CNN** baseline — VNEMOS-line ([vn-10]); the "no-SSL" floor.
2. **WavLM-Large frozen + probe** — audio-only SSL ([bimodal-12/15]); heads: emotion
   CE + V/A CCC + distress BCE.
3. **emotion2vec-S frozen + probe** — audio-only, emotion-pretrained ([bimodal-01]);
   same heads; A/B vs WavLM.
4. **PhoBERT on ASR transcript** — text-only ([bimodal-11 text branch / vn-03]).
5. **Concat fusion PhoBERT + WavLM** — the simplest learned bimodal ([bimodal-11]).
6. **Rule-fusion re-impl** — text-priority override tree ([vn-09 §2.6], withdrawn
   paper → we generate the number it never reported).
- **Shared head recipe:** emotion (7-class CE, class-weighted), V/A (**CCC loss
  L=1−ρc**, [bimodal-17/12]), distress (BCE, report recall). Same split, seeds×N, CIs.

- [x] M1 — Data prep & honest split — **DONE 2026-07-13, GO.** Built whole-series
      speaker-disjoint 2-fold split (`build_split.py`) + shared metrics module
      (`metrics.py`, self-tested, ruff-clean). Readiness report generated. All 7
      emotion classes present in both test series; V/A everywhere; distress+ small.
- [ ] M2 — Kaggle harness — kernel: load clips → cache frozen features (WavLM,
      emotion2vec-S, MFCC) + text (PhoWhisper→PhoBERT); shared train/eval loop +
      metrics. **Exit:** end-to-end smoke on a subset, metrics printed.
- [ ] M3 — Run the 6 methods on the frozen split; results table (macro-F1, CCC-V,
      CCC-A, distress-recall, per-class F1, seeds±CI). **Exit:** full table.
- [ ] M4 — Analysis & ablations — tone×emotion (high-arousal ASR-tone-swap slice:
      does the text branch degrade?); ASR-transcript vs YouTube-caption (clean-text
      ceiling); rare-class caveats. **Exit:** analysis section w/ measured evidence.
- [ ] M5 — Write the benchmark-survey paper (EN) — gap+framing from the synthesis,
      related-work from the 29 deep-reads, dataset, methods, results, analysis,
      honest limitations. **Exit:** paper draft in `docs/`.

## Decision Log
- **2026-07-13 (revised, SUPERSEDES Option C) — assume full corpus is human-labeled +
  whole-series speaker-disjoint holdout (user):** the user directed "assume human
  labels all those audio files." So the label of record for **all 3,611 utt** is the
  corpus label (operationalized as `emotion_consensus` where present, else the
  `opus` teacher pick; V/A means; distress OR), and the split is a proper **whole-series
  holdout** — train on one series, test on the other, both gold. Why: this satisfies
  the hard speaker-disjoint invariant (I3 / ADR-002) *and* the honest-eval brand
  cleanly, and removes Option C's fatal flaws. **Superseded Option C** (156-only test):
  M1 exploration showed the 155 human labels concentrate in ve-nha-di-con/ep01 (134) +
  chay-tron/ep01_1 (20); because pyannote speaker IDs are per-episode and actors recur
  across episodes within a series, a 156-scattered test could not be made
  actor-disjoint without whole-series holdout anyway — so the revised assumption is
  both easier and more correct. Rejected earlier: **A** (train+test both on machine
  labels, circular); **B-as-blocker** (wait for real human labeling — user unblocked
  by assuming it done).
- **2026-07-13 — Split = 2-fold cross-series (speaker-disjoint), primary + robustness
  (agent default under the revised assumption):** fold-1 train=chay-tron-thanh-xuan /
  test=ve-nha-di-con; fold-2 the reverse; report each + mean. Uses all data, honest by
  construction. A single held-out direction is the fallback if compute is tight.
- **2026-07-13 — Method scope = Core 6 (user).** Broad-10 (gated/BCAF/CASE fusion,
  ViSoBERT/CafeBERT, Whisper-enc/XEUS, distress recall-floor, ASR-robustness) deferred
  to future work / a v2 table if time permits.
- **2026-07-13 — Compute = Kaggle frozen-backbone (user).** No local GPU; frozen
  WavLM/emotion2vec + light heads; no 7B ALM. Matches the recipe in the paper-analysis
  synthesis (`docs/tasks/paper-deep-analysis.md`).
- **2026-07-13 — Text input = PhoWhisper ASR transcript as PRIMARY, YouTube caption as
  a clean-text-ceiling ablation (agent default):** ASR transcript is the realistic
  deployable input and carries the tone×emotion story (PhoWhisper tone-swap at high
  arousal); YouTube caption (better text, but won't exist for arbitrary audio) is the
  ceiling comparison at M4. Rejected: YouTube caption as primary (unrealistic ceiling,
  off-story).
- **2026-07-13 — Kaggle SSL run DEFERRED until human labeling completes (user):** build
  the feature-extraction kernel now (code, ready to push), but **do not run the
  definitive benchmark until the corpus is fully human-labeled** — so the headline
  numbers are on real human gold, not the 2-teacher stand-ins. Consequence: the
  "assume full corpus human-labeled" assumption is a *pipeline-building* device; the
  harness reads whatever labels the manifest/`state.jsonl` carry, so re-running once
  labeling is done yields the final numbers with zero code change. All builds are
  validated on current labels (e.g. the MFCC baseline) but are not the paper's numbers.
- **2026-07-13 — Framing = empirical benchmark-survey** ("first bimodal SER benchmark
  on a Vietnamese free-content TV-drama corpus, with a tone×emotion analysis"), not a
  pure literature survey — user said "run methods and measure".

## Open Questions
- [x] Does the speaker-disjoint split leave enough TRAIN data and a usable TEST? →
  **RESOLVED at M1: yes.** 2-fold cross-series: chay-tron 1,784 ↔ ve-nha-di-con 1,554
  clean utt; all 7 emotion classes present in both test folds; V/A on all. GO.
- [x] Distress recall meaningful? → **RESOLVED: small but non-zero** (distress+ 59
  chay-tron / 68 ve-nha-di-con) → report recall with an explicit small-support caveat.
- [ ] emotion2vec-S exact released checkpoint + frozen-loading in the Kaggle stack
  (torch/pyannote pins, no trust_remote_code issues)? → **researching now** (blocks M2
  audio-feature extraction) via task-researcher.

## Research Findings

### emotion2vec-S / emotion2vec / WavLM-Large frozen loading on Kaggle (2026-07-13, task-researcher, confidence medium-high)
- **emotion2vec-S** = HF **`ASLP-lab/Emotion2Vec-S`** (`checkpoint.pt`, 768-dim, Apache-2.0,
  non-gated). No HF/FunASR wrapper exists → load via **fairseq** (archived Mar-2026;
  needs pinned install: `pip<24.1` + `omegaconf==2.0.6` + `hydra-core==1.0.7` +
  `PyYAML==5.4.1` then `fairseq==0.12.2`). Also sparse-fetch only
  `Emotion2Vec-S/examples/data2vec/` (4 small .py) from `github.com/zxzhao0/C2SER`
  (don't full-clone — large unrelated assets). `model.extract_features(wav)` →
  `out["utt_x"]` = (768,) pooled utterance vector (ready to use). **Wrap in
  try/except-skip so a failed fairseq install drops only this arm.**
- **Base emotion2vec** (`iic/emotion2vec_base`, FunASR, 768-dim, `granularity="utterance"`)
  and **WavLM-Large** (`microsoft/wavlm-large`, transformers `WavLMModel`, frozen,
  mean-pool `last_hidden_state` → 1024-dim, no trust_remote_code, no gating): this repo
  already has a **working previously-Kaggle-run loader** —
  `archive/kaggle/voice/pebble-emotion2vec-repro/c3_features.py` (torch 2.5.1+cu121,
  transformers 4.48.2, funasr optional-guarded). **Reuse verbatim** (read-only, archive).
- **Contract, not loader, is unified:** `BACKBONES = {name: {"X": (N,dim) np.array of utt
  vectors, "dim": int}}` (same shape as the archived recipe).
- **Caveats:** fairseq pin fragile vs Kaggle's drifting image → verify with a throwaway
  install cell first; install fairseq FIRST in a separate pip call, smoke-test
  `import fairseq; import transformers` together (omegaconf 2.0.6 may clash with
  transformers 4.48.2); `checkpoint.pt` ~1.13 GB may be a training ckpt → budget disk vs
  WavLM+emotion2vec+cached wavs. And per the C²SER deep-read, emotion2vec-S's wins are on
  *acted/clean* sets, ~tied with WavLM on *spontaneous* → must actually run the A/B.

## Completed Work
- 2026-07-13 — Repo state verified: full corpus = 3,611 utt w/ 2-teacher labels
  (Kaggle private `phatneurondai/viemospeech-pilot`, `manifest.csv`); human labels =
  156/3,611 (`data/vietnamese-ser/episodes/state.jsonl`, annotator="human", scattered
  across episodes); ADR-002 whole-series test split still unresolved; no local GPU.
- 2026-07-13 — Forks resolved with user (Q1=C, Q2=Core-6, Q3=Kaggle); tracking doc
  written.

## Completed Work (review HTML — paper basis)
- 2026-07-13 — `scripts/vietnamese-ser/benchmark/build_review_html.py` → generates
  `docs/survey-review/` : **18 self-contained HTML pages** (one per paper the survey is
  based on, rendered from the deep-read analyses) + `index.html` grouping them by role
  (6 benchmarked methods · 4 fusion-surveyed · 4 novelty/premise · 4 honest-eval/corpus).
  Each page carries the paper's role-in-survey banner + links to its PDF / .vi.md /
  source .md; all relative links verified to resolve; ruff-clean. Open
  `docs/survey-review/index.html`.

## Completed Work (M2 core + first baseline)
- 2026-07-13 — Harness core (framework-agnostic, local-tested in `.venv-vnser`,
  ruff-clean): `data.py` (load split → aligned targets; **asserts speaker-disjoint**),
  `train_eval.py` (shared MTL probe: emotion class-weighted CE + V/A **CCC loss** +
  distress BCE; standardize; seeds±std; random-feature sanity passes), `metrics.py`
  (M1). `run_benchmark.py` aligns an id-keyed feature `.npz` to the folds and prints
  the table row.
- 2026-07-13 — `extract_mfcc.py` — local MFCC(20)+Δ+ΔΔ mean+std → 120-d/utt for all
  3,338 clean clips (0 missing), no GPU. **First real result (MFCC+MLP baseline):**
  mean macro-F1 **0.181**, CCC-V 0.164, CCC-A 0.371, distress-recall ~0.33.
  Per-class F1 (fold1): neutral .38 / anger .36 / joy .17 / sadness .17 / fear .07 /
  disgust .01 / surprise .02. Sensible: cross-series honest baseline is weak, arousal >
  valence CCC, rare classes ~0. **Validates the whole pipeline end-to-end, 0 Kaggle quota.**
- 2026-07-13 — **Kaggle feature-extraction kernel BUILT** (not run, per user):
  `kaggle/vietnamese-ser/benchmark-features/extract_features.py` — WavLM-Large
  (mean-pool, per-clip exact) + emotion2vec-S (fairseq `utt_x`) + base emotion2vec
  (FunASR) + MFCC, each guarded, with the pinned-fairseq setup cell from the research.
  Ruff + py_compile clean. Output contract = `{name}.npz{ids,X}` matching
  `run_benchmark.py`.
- **Still open in M2 (ready-to-build, run deferred until labeling done):** PhoBERT
  text extractor (CPU-local); fusion wiring (concat two npz — `run_benchmark` already
  trains any feature matrix, add a concat helper); rule-fusion (method 6, post-hoc
  combiner of text+audio branch predictions). Definitive SSL/full run waits for human
  labeling (user, 2026-07-13).

## Completed Work (M1)
- 2026-07-13 — `scripts/vietnamese-ser/benchmark/build_split.py` — whole-series
  speaker-disjoint 2-fold split; outputs `data/vietnamese-ser/benchmark/splits/`
  (`fold{1,2}_{train,test}.csv` + `readiness_report.md`). Ran + verified.
- 2026-07-13 — `scripts/vietnamese-ser/benchmark/metrics.py` — macro-F1 (over present
  classes) + per-class F1 + CCC(V,A) + distress recall/precision; self-test OK; ruff clean.

## Remaining Action Items
- [ ] M2 next (local, no quota): PhoBERT text-only features (CPU-feasible) → runs
  methods 4 (text-only) toward M3.
- [ ] M2/M3 (Kaggle GPU, **needs user quota + `kaggle.json`** — CHECKPOINT):
  WavLM-Large + emotion2vec-S frozen feature extraction kernel (reuse
  `archive/kaggle/voice/pebble-emotion2vec-repro/c3_features.py` loader + the fairseq
  pin for emotion2vec-S). Then methods 2, 3, 5 (concat fusion) + 6 (rule-fusion).
- [ ] M4–M5 per milestones above.
