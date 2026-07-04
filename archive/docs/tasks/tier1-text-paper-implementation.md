# Tier 1 Implementation Plan — Finish the Text Paper (executor: Opus)

- **Slug:** tier1-text-paper-implementation
- **Status:** planned (ready to execute)
- **Created:** 2026-07-03 · **Parent:** [[thesis-staged-plan]] (Tier 1) · **Origin:** [[bimodal-ser-papers]] M8
- **Executor note:** this document is self-contained. You do NOT need the conversation
  that produced it. Read this file top-to-bottom, then execute T1.1 → T1.5 in order
  (T1.4 is quota-gated and may be deferred). Update THIS file's checkboxes and the
  parent docs as you go.

---

## 0. Context you must load first (read in this order)

1. `docs/intent/constraints.md` — the binding constraints. The two you will touch:
   - **I1 Gold-holdout:** never train on gold labels; never report a metric trained
     and evaluated on the same label source. (T1.1 creates LLM labels *on* gold
     examples — these are for agreement analysis ONLY and must never enter any
     training pool. State this in every artifact you produce.)
   - **I5 Provenance:** every number you write into the paper must cite the kernel/
     log/script that produced it.
2. `docs/spec/capabilities/label-quality.md` — current truth for label-quality work;
   T1.1 and T1.3 results must be folded into this file in the same change.
3. `docs/reports/STATUS-2026-07-02-vi.md` §3 — the results table and the two open
   debts (κ, baseline TODO) this plan closes.
4. `docs/papers/finetuning-message/PAPER-DRAFT-text-ordinal-suicide.md` — the paper
   draft you will edit. Grep `TODO` first: the κ hole is at §IV (line ~231), the
   baseline holes at lines ~324–325.

**Environment:** Python via `uv` / `.venv-voice` for local scripts (repo convention:
`.venv-voice/bin/python scripts/<script>.py`). `make check` = ruff + mypy + pytest —
run it before any commit that adds/changes code. LLM API config is env-var-driven,
read from a local gitignored `.env` (see `scripts/r2_llm_label.py` header:
`LLM_PROVIDER`, `LLM_MODEL`, `GEMINI_API_KEY` / `ANTHROPIC_API_KEY` / ...).
Kaggle runs (T1.4 only) need `~/.kaggle/access_token` (user `fabiocarava`) built
into `kaggle.json`.

**Data locations (all gitignored — never commit anything under `data/`):**
- Combined 4-level C-SSRS dataset: `data/finetuning-message/external/r2-combined/sequences.csv`
  (columns `User,Post,Label,Source`; `Post` = `repr(list[str])`; `Label` ∈
  {Indicator, Ideation, Behavior, Attempt}; `Source` distinguishes gold CSSRS-500
  (Gaur) rows from av9ash and scraped-LLM rows). Rebuild if missing:
  `.venv-voice/bin/python scripts/r2_build_dataset.py --min-confidence 0.6`.
- Scraped + LLM-labeled pool: `data/finetuning-message/external/scraped-suicidewatch/labeled.jsonl`
  (has per-example `confidence`; produced by `scripts/r2_llm_label.py`).
- Gold eval set: the **392 user-sequences** (class counts [99, 171, 77, 45]) —
  the held-out split of the gold CSSRS-500 source. The split is subject-level and
  seeded; recover it exactly the way the training kernels do (see the split logic
  in `kaggle/finetuning-message/r2-ablation/` or `r2-corn-gce/` cells) rather than
  re-deriving your own. **If you cannot reproduce the exact 392-example split, stop
  and flag it — do not approximate** (a wrong overlap set silently invalidates κ).

---

## T1.1 — Cohen's κ(LLM, gold) + confusion matrix on the overlap set

**Why:** IEEE blocker #1. The paper claims a ~0.28 honest-evaluation gap
(within-dist 0.653 vs gold 0.402 macro-F1) and currently has no annotator-agreement
number to explain it. §IV of the draft says: κ "on the recovered LLM/gold overlap
set (the subset with both an LLM and a gold label)".

**Definition of the overlap set.** Gold examples do not currently carry LLM labels
(the training pool and gold pool are disjoint by construction). Therefore: produce
LLM labels **for the 392 gold eval sequences** using the *same* labeling pipeline
that produced the training pool, then compute agreement against their gold labels.
This is legitimate under I1 because these LLM labels are used only to *measure
agreement* — they must never be written anywhere a training script reads.

**Steps:**
1. Extract the 392 gold eval sequences (User, Post list, gold Label) using the
   exact kernel split logic (see Data locations above).
2. Label them with `scripts/r2_llm_label.py`'s prompt + provider path. Prefer
   writing a thin wrapper `scripts/r2_kappa_gold_overlap.py` that imports/reuses the
   prompt and request code from `r2_llm_label.py` rather than duplicating it
   (surgical-changes rule). Use the SAME `LLM_PROVIDER`/`LLM_MODEL` as the training
   pool run — check `.env` / ask the user if ambiguous; if the original model is
   unavailable, use the closest available and **state the substitution in the
   paper text** (it changes the interpretation of κ).
   Output: `data/finetuning-message/interim/kappa-gold-overlap/llm_labels.jsonl`
   (fields: user_id, gold_label, llm_label, llm_confidence, raw_response).
3. Compute and save to `data/finetuning-message/interim/kappa-gold-overlap/kappa_report.md`
   (+ a small JSON for numbers):
   - **Quadratically-weighted Cohen's κ** (primary — matches QWK used as the
     ordinal metric elsewhere in the paper), plus unweighted κ and linear-weighted κ
     for completeness. Use `sklearn.metrics.cohen_kappa_score(..., weights="quadratic")`.
   - 4×4 confusion matrix (rows=gold, cols=LLM), raw counts AND row-normalized.
   - Per-class agreement, and the same numbers on the confidence-≥0.6 subset
     (the training pool's retention rule) — this is the κ that actually describes
     the training labels.
   - n of the overlap set (expected 392; also report n after confidence filter).
4. Fill the draft: replace `[TODO κ]` at §IV (~line 231) with 2–4 sentences reporting
   quadratic κ (+ CI via bootstrap over examples, 1000 resamples), the confusion
   structure (expect Behavior↔Ideation confusion to dominate, consistent with the
   3.0× Behavior shift and 35.8% CL flag rate — but WRITE WHAT YOU MEASURE, not this
   expectation), and one sentence connecting κ to the 0.28 gap. Also update the
   `[TODO κ]` mention at ~line 340.
5. Fold the result into `docs/spec/capabilities/label-quality.md` ("Still owed" →
   done, with the number and artifact path).

**Acceptance:** draft has no `[TODO κ]`; kappa_report.md exists with all numbers;
label-quality.md updated; the LLM-labels-on-gold file lives under `data/**` only.
**Cost:** 0 GPU; ~392 LLM calls.

---

## T1.2 — Fill the baseline rows in the paper draft

**Why:** the numbers exist in logs; the draft table still says `[TODO baseline]`.

**Steps:**
1. Extract final metrics from the actual logs (do NOT copy from the status report —
   read the primary source): `kaggle/finetuning-message/r2-baseline-roberta/out/r2-baseline-roberta.log`
   and `kaggle/finetuning-message/r2-baseline-bilstm/out/r2-baseline-bilstm.log`.
   Expected ballpark (verify against log): RoBERTa 0.346 ±0.026 macro-F1 / 0.169
   Behavior-F1 / 0.292 QWK; BiLSTM-MTL 0.378 ±0.014 / 0.181 / 0.396. If a log
   number differs from the status report, **the log wins** — note the discrepancy.
2. Fill draft lines ~324–325 (three columns per row: macro-F1, Behavior-F1, QWK —
   match the table's existing column format exactly).
3. Update the provenance table in `docs/tasks/r2-method-improvements-for-contribution.md`
   (entries still marked "🔄 running" for these baselines → done with log paths).

**Acceptance:** `grep -n "TODO baseline" PAPER-DRAFT...md` returns nothing; every
filled number matches its log; provenance updated. **Cost:** 0 GPU, ~1h.

---

## T1.3 — Pilot: rationale-groundedness as a silver-label quality filter

**Why:** from the bimodal-SER sweep, paper [05] (`docs/papers/bimodal-ser/05-*.md`,
arXiv:2506.06820) showed evidence-grounded rationales improve label quality and can
be scored with an LLM-judge "groundedness" metric. If ungrounded-rationale flags
correlate with the ordinal-CL flags we already trust (35.8% of Behavior), this
becomes a new, cheap, citable mini-contribution for §label-quality — and a second
input to the B-Arm2 cleaning (T1.4).

**Steps:**
1. Sample **500 examples from the 9,680 training pool**, stratified by class with
   Behavior oversampled (e.g. 125/125/125/125) since Behavior is the bottleneck.
   Fixed seed; save the sample id list under `data/finetuning-message/interim/groundedness-pilot/`.
2. Re-elicit from the SAME LLM provider/model as the original labeling: label +
   a rationale that must **quote verbatim spans** from the posts supporting the
   level choice. Extend the T1.1 wrapper script with a `--rationale` mode.
3. LLM-judge pass (can be a stronger model): for each rationale, score
   `grounded ∈ {0,1}` — (a) do the quoted spans actually appear in the source posts
   (string-check first, judge only the semantic part), and (b) do they support the
   assigned level per C-SSRS definitions? Save per-example judgments.
4. Analysis (write `data/.../groundedness-pilot/report.md` + numbers JSON):
   - % ungrounded overall and per class.
   - **Overlap with ordinal-CL flags:** load `kaggle/finetuning-message/r2-tier1-cleanlab/out/cl_issues.npz`,
     map ids, report the 2×2 contingency (CL-flagged × ungrounded) + odds ratio.
   - Agreement between re-elicited label and original silver label (a free
     label-stability measurement).
   - 5–10 qualitative examples (ungrounded rationale + why).
5. Decision rule (record in this doc's Decision Log): if ungrounded-flags and
   CL-flags are positively associated (OR meaningfully > 1) AND ungrounded rate is
   neither ~0% nor ~100%, adopt groundedness as an additional drop/downweight
   signal for T1.4 and write it into the paper §label-quality as a mini-contribution
   (method + pilot numbers, honestly labeled as a 500-example pilot). Otherwise
   report the negative result in this doc and skip the paper claim.

**Acceptance:** report.md with the contingency table; decision recorded; nothing
under `data/` committed. **Cost:** 0 GPU; ~1,000–1,500 LLM calls (500 re-elicit +
500 judge + retries).

---

## T1.4 — B-Arm2: retrain on the ordinal-cleaned pool (QUOTA-GATED)

**Gate:** check remaining Kaggle GPU quota first (weekly ~10h; T2.1 voice kernel
run has priority per the parent plan — coordinate before spending). If quota is
insufficient this week, mark deferred and move on; do not silently skip T1.5.

**Why:** `label-quality.md` "Still owed". The CL diagnostic flagged 16.2% of the
pool (35.8% of Behavior); the paper currently reports the diagnostic but not the
retrain-after-cleaning number.

**Steps:**
1. New kernel `kaggle/finetuning-message/r2-barm2-cleaned/` cloned from
   `r2-corn-gce/` (the best ordinal config: CORN+CE+GCE) — do NOT edit finished
   kernels (surgical rule). Change ONLY the data-preparation cell:
   - Load `cl_issues.npz` flags; **drop far-flagged** examples, **downweight
     adjacent-flagged** (0.5 sample weight) — mirroring the ordinal-CL semantics
     already documented in `label-quality.md`.
   - If T1.3 adopted groundedness: also drop the ungrounded subset (only the 500
     piloted ids have this signal — apply where available, note the partial coverage).
2. 3-fold (not 5) to respect quota, same split/seed protocol as `r2-corn-gce`
   so numbers are paired-comparable.
3. Report: gold macro-F1, Behavior-F1, QWK vs the uncleaned CORN+GCE run
   (0.402 / 0.260 / 0.361 per STATUS — verify from its log). Paired same-fold delta.
4. Fold into the paper (§V, one paragraph + table row) and `label-quality.md`.

**Acceptance:** kernel + `out/` log committed (code only, no data); paired numbers
in draft; capability updated. **Cost:** ~3h GPU.

---

## T1.5 — References + evaluation-protocol paragraph

**Steps:**
1. In the draft's evaluation-protocol / limitations text, add the replication-study
   citation: Triantafyllopoulos, Batliner & Schuller 2025, arXiv:2508.02448
   (entry: `docs/papers/bimodal-ser/15-*.md`) — one sentence: progress claims are
   comparison-set-dependent and single-run rankings unstable, which motivates our
   multi-fold + std + fixed-split reporting.
2. In the ordinal-framing motivation (Introduction or Method), add the JMIR
   systematic review: Jordan et al., JMIR Mental Health 2025 (entry:
   `docs/papers/bimodal-ser/10-*.md`) — RDoC/HiTOP dimensional-psychopathology
   grounding for treating suicide risk as an ordinal/severity spectrum.
3. Resolve the `[TODO: expand ...]` refs note at draft line ~404 (papers 14–17 in
   `docs/papers/finetuning-message/`) — add them where the related-work text already
   points, keeping edits minimal.
4. Rebuild/export the PDF the same way the 06-30 export was produced (check
   `docs/papers/finetuning-message/` for the export artifact/tooling; if unclear,
   leave the PDF and note it — do not invent a new toolchain).

**Acceptance:** refs resolve; no orphan `[TODO]` other than authors/affiliation
(user-owned). **Cost:** 0 GPU.

---

## Exit criteria for Tier 1 (from the parent plan)

- [ ] T1.1 κ + confusion measured, in draft + capability doc — **gold set recovered + script ready; blocked on gpt-5.4-mini `.env` credentials for the label step**
- [x] T1.2 baseline rows filled from logs, provenance updated — done 2026-07-03
- [ ] T1.3 groundedness pilot run, adopt/reject decision recorded
- [ ] T1.4 B-Arm2 paired numbers (or explicitly deferred with quota reason)
- [~] T1.5 refs + protocol citation in (steps 1–3 done 2026-07-03); PDF: no
  toolchain/export artifact exists in-repo → left, per plan's "do not invent"
- [ ] Paper A is submit-ready except authors/affiliation

## Guardrails (repeat offenders — do not violate)

1. **No fabricated numbers.** Every number in the draft traces to a log/artifact
   you can name (I5). If a measurement fails, write the failure, not a plausible value.
2. **LLM labels on gold = analysis-only** (T1.1). Never let them near a training
   pool or a data file a kernel reads.
3. **`data/**` is never committed.** Reports/JSONs with aggregate numbers may be
   summarized into committed docs; raw per-example files stay gitignored.
4. **Surgical edits** to the draft: fill the holes, don't rewrite sections.
5. **Same PR discipline:** a result change updates `label-quality.md` (capability)
   together with the code/doc that produced it.
6. If any step's precondition fails (split not reproducible, log missing, model
   unavailable), **stop that step and escalate in this doc** — ambiguity goes up,
   never gets improvised downward.

## Decision Log
- **2026-07-03 — Overlap set := LLM-label the 392 gold eval sequences** (they carry
  no LLM labels today; pools are disjoint by construction). Analysis-only use keeps
  I1 intact. Rejected: κ on training-pool subsets (no gold labels there → measures
  nothing about gold agreement).
- **2026-07-03 — Quadratic-weighted κ primary:** matches QWK, ordinal-aware.
  Unweighted/linear reported alongside. Rejected: unweighted-only (ordinal-blind).
- **2026-07-03 — T1.4 gated behind quota, T2.1 has GPU priority** (parent plan).

## Progress / Completed Work
<!-- executor fills as it goes; keep timestamps absolute -->
- **2026-07-03 — T1.2 DONE.** Extracted 5-fold gold-holdout metrics from the primary
  logs (`r2-baseline-roberta/out/`, `r2-baseline-bilstm/out/`): plain-RoBERTa-CE
  0.346 ±0.026 / Beh 0.169 / QWK 0.292; BiLSTM-MTL 0.378 ±0.014 / Beh 0.181 / QWK 0.396.
  Numbers match the plan's ballpark and the log wins. Filled Table III (draft lines
  324–325) + updated the caption's "to be filled" sentence. Provenance (`r2-method-
  improvements-for-contribution.md` line 98) was already ✅ done. `grep TODO baseline`
  in draft → clean.
- **2026-07-03 — T1.1 gold overlap set RECOVERED + verified.** The gold eval set =
  all `Source==cssrs500` rows (used whole as the fixed test each fold; StratifiedKFold
  folds only the pool — no seeded gold sub-split, so no reproduction risk). Recovered
  deterministically from the public Zenodo record 2667859 (CSSRS-500, CC-BY-4.0) via
  `from_cssrs500 + _norm + within-source dedup`; class dist **[99,171,77,45]=392** —
  exact match. Artifact: `data/finetuning-message/interim/kappa-gold-overlap/gold_overlap.jsonl`.
- **2026-07-03 — T1.1 script WRITTEN:** `scripts/r2_kappa_gold_overlap.py`
  (recover/label/report; reuses PROMPT + provider callers from `r2_llm_label.py`,
  gold-parse from the same logic as `r2_build_dataset.py`). `recover` verified.
  Report step computes quadratic (primary) / linear / unweighted κ, 4×4 confusion
  (raw + row-norm), per-class recall, conf≥0.6 subset, and a 1000-resample bootstrap
  CI. **Needs `pip install scikit-learn` into `.venv-voice` at report time.**
- **2026-07-03 — T1.5 steps 1–3 DONE.** Added [T25] Triantafyllopoulos/Batliner/
  Schuller 2025 (arXiv:2508.02448) to the eval-protocol §V-A (motivates multi-fold +
  std + fixed-split) and [J25] Jordan et al. JMIR MH 2025 (dimensional/RDoC-HiTOP
  grounding) to the Introduction's ordinal-framing. Expanded the `[TODO: expand refs]`
  placeholder into 7 verified IEEE entries ([Ji22] MentalBERT, [Sq24], [YL25], [Pa25],
  [Zh25], [Sh25], [DP24]) — authors/titles fetched from arXiv, not fabricated. Draft
  `grep TODO` → only `[TODO κ]` (T1.1, blocked) + authors/affiliation (user-owned).
  Step 4 (PDF): no LaTeX/pandoc/export tooling or prior PDF exists in-repo → left
  per plan's "do not invent a new toolchain."
- **2026-07-03 — T1.1 quota-blocked, substitute-model decision PENDING user.** The
  gpt-5.4-mini subscription ran out of funds. Options surfaced (all $0): (A) Gemini
  free tier `gemini-2.5-flash` — script already supports it, closest mini-tier proxy,
  recommended; (B) local Ollama — NOT installed on this machine, needs setup + a new
  caller; (C) ship κ as future-work. **Any substitute changes κ's interpretation and
  MUST be stated in §IV** (plan L76–78). Ollama checked: absent. Awaiting user choice
  + a Gemini key in `.env`.
- **2026-07-03 — T1.1 BLOCKED on credentials.** The label step needs gpt-5.4-mini
  access in a local `.env` (none on this machine). Provider default map → `azure`
  (`LLM_PROVIDER=azure`, `LLM_MODEL=gpt-5.4-mini`, `AZURE_OPENAI_ENDPOINT`,
  `AZURE_OPENAI_API_KEY`). Once `.env` exists, run:
  `.venv-voice/Scripts/python.exe scripts/r2_kappa_gold_overlap.py --steps label report`
  then fill draft §IV (~L231, L340) + fold into `label-quality.md`.

## Open Questions
- [x] **RESOLVED 2026-07-03 — training pool used `gpt-5.4-mini`** (user-confirmed).
  `labeled.jsonl` stores no model field; interpretation of κ is tied to this model
  (state it in the paper §IV).
