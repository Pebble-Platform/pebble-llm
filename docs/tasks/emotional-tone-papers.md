# Emotional-tone (positive↔negative) papers — save · analyze · datasets

- **Slug:** emotional-tone-papers
- **Status:** done
- **Created:** 2026-06-26  ·  **Updated:** 2026-06-26
- **Owner:** Fabio / Claude

## Goal
Process the 16 newly-found papers on "analyze a user's messages for emotional tone (positive vs. negative)"
through three sequential steps: (1) **save** them as a ranked related-work doc; (2) **score overlap %** of the
top 4 picks (VADEC, CLPsych 2025, MentaLLaMA, Mitsios EMD) via `analysis-paper` → per-paper dossiers; (3)
**acquire datasets** IMHI (MentaLLaMA) + CLPsych 2025 via `find-dataset` for use as held-out test sets.

## Requirements & Constraints
- **Sequential:** user asked "làm tuần tự" → do item 1 → 2 → 3 in order (fan-out allowed *within* an item).
- **Save (item 1):** ranked entries → `docs/papers/related-work-emotional-tone.md` (match existing related-work-*.md style).
- **Analyze (item 2):** `analysis-paper` agents → per-paper dossiers numbered **54–57** in `docs/papers/finetuning-message/`
  (continuing the global sequence: 01–23 text, 24–41 voice, 42–53 finetuning-recipes).
- **Datasets (item 3):** `find-dataset` for IMHI + CLPsych → download open / draft DUA into `data/finetuning-message/external/`.
- **Surgical:** don't duplicate papers Pebble already has; verified links only (already done in discovery).

## The 16 papers (from the 2026-06-25 research-paper fan-out)
Top-4 (→ item 2 dossiers): **54 VADEC** (SIGIR'21), **55 CLPsych 2025**, **56 MentaLLaMA** (WWW'24), **57 Mitsios EMD** (NAACL'24).
Long tail (item 1 only): SoftMCL, Emotion-Granularity, SleepDepNet, SentiWSP, SentiLARE, SentiBERT, Crisis-Counselor-Language,
PLOS-hotline-crisis, SemEval-2017-Task4, EmoDynamiX, Park-et-al-EMD (preprint⚠), Detecting-Anxiety-Dialogues (workshop⚠).

## Milestones
- [x] M1 — Item 1: write `related-work-emotional-tone.md` with all 16 ranked entries + cross-links
- [x] M2 — Item 2: 4 `analysis-paper` agents → dossiers 54–57; link back from related-work doc
- [x] M3 — Item 3: 2 `find-dataset` agents (IMHI, CLPsych) → provenance + download/DUA status
- [x] M4 — Close out: update README index (54–57), tracking doc done

## Decision Log
- **2026-06-26 — Item 1 = single related-work doc, NOT 16 per-paper files:** matches the repo split (deep dossiers
  for close systems; a list doc for the wider set, cf. FAMOUS-cited-papers-vi.md). Only the top-4 get per-paper
  dossiers (item 2) → no file conflict, no double-write. Rejected: 16 per-paper md (heavy, low ROI for the tail).
- **2026-06-26 — New dossiers numbered 54–57:** continue the global sequence (42–53 just used). Top-4 = the exact
  papers the user named for analysis.
- **2026-06-26 — Items run in item-order (1→2→3) per "tuần tự":** but fan out agents *within* item 2 (4 parallel)
  and item 3 (2 parallel). Sequential applies across items, not within.

## Open Questions
<!-- none blocking; papers verified in discovery. find-dataset may surface gate/DUA issues → fold in. -->

## Research Findings
<!-- analysis-paper + find-dataset agent blocks fold in here -->
**Item 2 — overlap % (analysis-paper, 2026-06-26):**
- **54 VADEC — 38% (peripheral)** [D1=2,D3=1,D5=1,D7=1]. Strongest D1 (cleanest published cat-emotion + continuous-affect
  two-head-on-shared-trunk = Pebble's design). Best point: co-training a continuous valence regressor *improves* the
  emotion classifier (+11% Macro-F1 on AIT) → wire Pebble's GoEmotions head + valence head on the same CLS, co-train,
  reproduce VADEC's emotion-only-vs-co-trained ablation. **Method-to-adopt + baseline.**
- **55 CLPsych 2025 — 54% (adjacent)** [D1=2,D2=2,D6=1,D7=2]. Strongest D1 (continuous 1–10 wellbeing regression +
  evidence spans = Pebble severity+safety twin). Best point: A.2 wellbeing-regression as a drop-in benchmark for the
  severity head (MSE vs baseline; supervised RF *beats* zero-shot DeepSeek-7B → small encoder > LLM on continuous affect,
  and Gemini teacher's continuous scores must be audited). **Baseline + dataset.** ⚠ Dataset GATED (shared-task registration).
- **56 MentaLLaMA — 42% (adjacent)** [D2=2,D4=2,D1=1]. Strongest D4 (ChatGPT teacher→student WITH an explicit quality
  gate Pebble lacks). Best point: gate teacher silver labels on calibrated quality axes before training (esp. the safety
  head, recall≥0.95). **Method-to-adopt + framing.** IMHI dataset = **MIT license, openly downloadable** (use as label-only
  OOD eval, not training — adult vs minors). Distills into a generative 7B LLM (not a 250M encoder) → not a head-to-head baseline.
- **57 Mitsios — 35% (peripheral)** [D3=2,D7=2,D1=1]. Strongest D3 (GoEmotions+WASSA = Pebble's transfer corpora).
  Best point: valence-rank the taxonomy + distance-aware ordinal loss → fewer cross-valence errors; port R2's CORAL
  machinery from the severity head to the emotion head. **Method-to-adopt.** ⚠ Loss is **MSE-on-ordinal, not EMD**
  (first labeling wrong); filename `57-mitsios-emd-valence.md` kept for stability, prose corrected.

**Item 3 — dataset acquisition (find-dataset, 2026-06-26):**
- **IMHI (MentaLLaMA) — ACQUIRED.** 19,051 labeled TEST rows (25 MB) across 8 MH tasks → `data/finetuning-message/external/imhi/`
  (dreaddit, DR, loneliness, SAD, CAMS, t-sid, swmh, Irf, MultiWD). **MIT license** (code/instructions); raw text under Reddit/
  Twitter ToS → local OOD-eval only, no redistribution. Schema: `query` (instruction+post) + `gpt-3.5-turbo` (label + reasoning;
  parse first sentence for label). Highest-value for Pebble safety head: **swmh** (10,882, 5-class) + **t-sid** (959, suicide/self-harm).
  Skipped: training splits (HF gated, not needed) + CLP split (not yet released). Use as label-only OOD eval (adult text ≠ Pebble minors).
- **CLPsych 2025 — GATED, request drafted.** Per-member DUA + password-protected; 2025 registration CLOSED (deadline 2025-02-09);
  no open sample/script/guidelines. `data/finetuning-message/external/clpsych-2025/ACCESS-REQUEST.md` created with provenance +
  ready-to-send email (→ t.tseriotou@qmul.ac.uk, academic affiliation required) or CLPsych 2026 route. **Research-only arm — cannot
  ship in the deployed product** (same restriction class as DAIC-WOZ / SMHD / RSDD). Schema confirmed from arXiv:2504.14066:
  30 timelines / 343 posts, per-post wellbeing_score 1–10 (A.2 MSE, baselines RF 2.994 vs DeepSeek-7B zero-shot 6.610).

## Completed Work
- 2026-06-25 — Discovery: 2 `research-paper` agents → 16 verified papers (methods/benchmarks + MH/conversational).
- 2026-06-26 — M1 (item 1): wrote `docs/papers/related-work-emotional-tone.md` — 16 ranked entries (top-4 + mid
  tier + caution flags), closeness dims, access flags, synthesis, cross-links to 54–57 + dataset task.
- 2026-06-26 — M2 (item 2): 4 `analysis-paper` agents wrote dossiers `54-vadec`, `55-clpsych-2025`, `56-mentallama`,
  `57-mitsios-emd-valence` (overlap 38/54/42/35%); back-linked overlap % into the related-work doc + corrected the
  Mitsios EMD→MSE-ordinal label.

## Remaining Action Items
All 3 items complete. Optional follow-ups (not part of this task):
- [ ] Build `load_imhi_eval(task, external_dir)` to use IMHI swmh/t-sid as an OOD eval for the safety head (when asked).
- [ ] If CLPsych A.2 is wanted: email the organizers from an academic address (template in the ACCESS-REQUEST.md) — research-only.
- [ ] Consider `analysis-paper` on EmoDynamiX (mid-tier) if the encoder→action framing becomes a paper section.
