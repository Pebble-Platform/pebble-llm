# Enrich suicide-risk dataset toward 10k (R2 reproduction)

- **Slug:** enrich-suicide-risk-dataset
- **Status:** done ✅ (10,073 samples — target met)
- **Created:** 2026-06-21  ·  **Updated:** 2026-06-21
- **Owner:** Fabio / Claude

## Goal
Grow the R2 suicide-risk training set from the current **392 user-sequences** (Reddit C-SSRS-500)
toward **~10k labeled samples** by finding + downloading **public datasets similar to those described
in the R2 paper** (Reddit/social-media posts with C-SSRS-style ordinal severity:
Indicator → Ideation → Behavior → Attempt). Fold the new data into
`notebooks/r2-suicide-risk-dualhead.py`'s loader so a larger CV run can be launched.

## Requirements & Constraints
- **Functional:** end with ≈10k samples usable by the R2 dual-head model (4-level ordinal labels, or
  mappable to them); a single loader that reads CSSRS-500 + the new sources.
- **Ontology match:** paper uses C-SSRS 4 levels. New data must map to {0 Indicator,1 Ideation,2 Behavior,3 Attempt}.
- **License/access:** only download **open** datasets into the gitignored `data/finetuning-message/external/`.
  Gated sets (CLPsych/UMD DUA) → draft request, do not block on them.
- **Constraints:** mental-health PII → data stays gitignored (see `external/README.md`); keep changes surgical;
  honest provenance (record every mapping + deviation, per the R2 doc's "Sai lệch có chủ đích" practice).
- **Non-goals:** no GPT-4 crawl/relabel pipeline unless explicitly chosen; no retrain of the model arch.

## Milestones
- [x] M1 — Map the landscape → done (Research Findings); only ~1.5k faithful open data exists, so chose hybrid.
- [x] M2 — Decided: scrape r/SuicideWatch + LLM-label (paper's method); per-author sequences, 4-level labels.
- [x] M3 — Downloaded av9ash (1,170) + scraped 11,108 SuicideWatch sequences (pullpush, no creds).
- [x] M4 — Labeled 11,108 via Azure gpt-5.4-mini → 8,511 on-topic hi-conf; merged → **10,073** combined.
- [x] M5 — Verified: combined CSV loads via `R2_DATA`, R2 pipeline smoke-trains end-to-end on it.
- [ ] M6 — (optional, not done) launch larger Kaggle CV run on the enriched 10k.

## ✅ FINAL RESULT
- 2026-06-21 — **Normalized + website added.** Builder now collapses whitespace + dedups full sequences
  → **10,072** (dropped 1 dup). Also emits `r2-combined/sequences.json` for a viewer. Built a self-contained
  offline web viewer `r2-combined/viewer.html` (summary cards, class-dist bars, search/filter by
  label/source/length, expandable post sequences, pagination). Serve:
  `cd data/finetuning-message/external/r2-combined && python3 -m http.server 8770` → `http://127.0.0.1:8770/viewer.html`.
  **Normalization audit:** all labels valid, 0 empty rows, ~0 cross-source duplicates, no PII beyond post text.

**10,073 samples** in `data/finetuning-message/external/r2-combined/sequences.csv` (gitignored, schema
`User,Post,Label,Source`). Sources: cssrs500 392 + av9ash 1,170 + scraped-LLM-labeled 8,511.
Class dist: Indicator 4,091 · Ideation 3,784 · Behavior 711 · Attempt 1,487.
Train with: `R2_DATA=data/finetuning-message/external/r2-combined/sequences.csv .venv-voice/bin/python notebooks/r2-suicide-risk-dualhead.py`
(or set the same env on Kaggle). Scraped seqs carry real timestamps in `scraped-suicidewatch/sequences.jsonl`
(not yet wired into Δt — pipeline still uses Δt=0; future work).

## Decision Log
<!-- newest first -->
- **2026-06-21 — Add r/SuicideWatch *comments* for volume + an off-topic `-1` label to keep it faithful:**
  pullpush.io rate-limits submissions at ~3,873 for us, so submissions alone can't reach 10k. Comments
  (separate endpoint, higher volume) fill the gap BUT many are off-topic supportive replies. Mitigation:
  labeler gets a `-1 = off-topic` option (not the author's own/another's suicide-risk/MH distress) → builder
  drops `-1` and only keeps {0,1,2,3}. So the final 10k stay genuine C-SSRS disclosures. Deviation logged:
  comments (not just submissions) now contribute. Rejected: padding with raw comments (noise/skew to label 0);
  looping submissions (diminishing — pass 2 added only ~400).
- **2026-06-21 — Labeling backend = Azure OpenAI `gpt-5.4-mini`** (from `run_model.py`; key auth works,
  Azure-AD path unused). Content filter blocks self-harm input → user will adjust the deployment's content
  filter (set self-harm threshold to High, or annotate-only). Labeler `azure` provider added + `.env` configured.
- **2026-06-21 — Path to 10k = Option C (scrape + LLM-label, the paper's method):** user-chosen.
  Rejected: augmentation (−0.077 F1 evidence), binary-data padding (ordinal label noise), faithful-only ~1.5k (misses target).
- **2026-06-21 — Scraper = pullpush.io (no Reddit creds):** verified working — 100 submissions/page, ~81% usable
  bodies, paginate via `before=<created_utc>`, full fields incl. `selftext`/`created_utc`/`author`. No PRAW/OAuth needed.
  Rejected: official Reddit API (needs app registration we don't have).
- **2026-06-21 — Research the dataset landscape before downloading:** reaching 10k with the paper's exact
  C-SSRS 4-level ontology is non-obvious — the only ungated 4-level Reddit set we know (CSSRS-500) is tiny
  (392). Whether 10k is reachable from open data, needs augmentation, or needs label-mapping of binary sets
  is the core unknown → spawned `task-researcher`. Rejected: blindly downloading the biggest Kaggle suicide
  set (it's binary, wrong ontology).

## Open Questions
- [ ] **BLOCKER (2026-06-21): Azure content filter blocks the data.** User provided an Azure OpenAI endpoint
  (`gpt-5.4-mini`, key auth verified working on benign prompts). But labeling real SuicideWatch posts returns
  HTTP 400 `content_filter` → `self_harm: filtered, severity: medium` on the *input*. Self-harm content is
  inherent to the task → no prompt fix. Need either: (A) user applies a modified/annotate-only content filter
  to the Azure deployment (Azure AI Foundry; may need Microsoft approval), or (B) switch to a provider that
  permits mental-health classification for research (Anthropic/OpenAI/Gemini key). → awaiting user.
- [ ] ~~What public datasets match R2's C-SSRS 4-level ontology~~ (resolved — see Research Findings)
- [ ] _(orig)_ What public datasets match R2's C-SSRS 4-level ontology (Reddit/social), and what are their sizes /
  licenses / access gates? Is ~10k reachable from open data alone, or only via augmentation / label-mapping
  of binary sets? → researching via task-researcher.

## Research Findings

#### Research: What public datasets match (or can be mapped to) the C-SSRS 4-level ontology on Reddit, and is ~10k reachable from open data? (task-researcher, 2026-06-21, confidence: high)

**Short answer:** True open-access 4-level C-SSRS Reddit data immediately downloadable = **only the ~392 CSSRS-500 sequences we already have**. ~10k of faithful open labeled data is **not achievable today**. The paper itself reached ~11k via Option C (real seed + self-scrape + LLM-ensemble labeling), not from released data.

**Inventory (4-level C-SSRS compatibility / downloadable-now / size):**
| Dataset | CSSRS-4 compatible | Downloadable now | Usable size |
|---|---|---|---|
| Gaur CSSRS-500 (Zenodo 2667859, CC-BY-4.0) | YES (drop Supportive) | ✅ YES (have it) | ~392 user-seqs |
| RSD-15K (arXiv:2507.11559) | YES, +timestamps, κ=0.72 | ❌ apply / GitHub 404 | 14,613 seqs |
| IEEE BigData 2024 Cup | YES (500 labeled) | ❌ post-comp unclear | 500 posts |
| Suicidal Comment Tree (arXiv:2510.14395) | YES | ❌ no URL | 500 segs |
| SDCNL (GitHub) | NO (binary) | ✅ yes | 0 toward CSSRS-4 |
| Komati/Kaggle 232k (CC0) | NO (binary) | ✅ yes | 0 toward CSSRS-4 |
| SWMH 54k (Zenodo/HF) | NO (subreddit taxonomy) | ❌ gated DUA | 0 toward CSSRS-4 |
| CLPsych/UMD Reddit Suicidality | NO (no-risk/low/mod/severe ≠ CSSRS) | ❌ DUA+IRB | 0 toward CSSRS-4 |

**Options to reach ~10k + honest tradeoff:**
- **A. Open real-data merge only** — ~392 now; ~15.5k *if* RSD-15K/IEEE/Tree author requests granted (weeks–months). Fidelity HIGH. Blocked on access + post-vs-user granularity mixing.
- **B. CSSRS-500 + paraphrase augmentation to 10k** — immediate, but fidelity LOW. The closest controlled experiment (Yang/ASONAM 2025, `docs/papers/finetuning-message/15-cssrs-hybrid.md:96`) found augmentation **−0.077 F1**. Not recommended.
- **C. Hybrid: real seed + self-scrape r/SuicideWatch (PRAW) + LLM-ensemble 4-level labeling** — this is exactly the paper's pipeline (~3,722 scraped+labeled). ~3–10k in days–weeks. Fidelity MEDIUM (LLM κ≈0.55–0.72). Needs Reddit API + LLM compute (~$50–200 GPT-4o for 10k, unverified).
- **D. Add label-mapped binary/subreddit data (Komati/SWMH)** — immediate to 10k+, but fidelity VERY LOW: r/SuicideWatch spans all 4 levels, mapping them all to one class injects ordinal label noise — the most damaging error for a CORAL model. Not recommended.

**Recommendation:** Option C, staged — (1) request RSD-15K now (biggest faithful win, +timestamps); (2) if granted, merge → ~15k done; (3) else self-scrape + LLM-label per the paper. Avoid B and D.

**Caveats:** Gaur CSV has **no per-post timestamps** (Δt slice unsupported for that portion); paper's 7,383 base corpus is unreleased (reproducing on 392 = ~28× less data → metrics depressed). Sources: Zenodo 2667859; arXiv:2507.11559; arXiv:2510.20085; arXiv:2505.23797; `15-cssrs-hybrid.md:96-99`.

## Completed Work
- 2026-06-21 — Set up tracking doc + confirmed current state: 392 usable user-sequences from
  `data/finetuning-message/external/cssrs/500_Reddit_users_posts_labels.csv` (R2 run CV macro-F1 0.2374).
- 2026-06-21 — Research (M1) done; folded into Research Findings + Decision Log.
- 2026-06-21 — **HF re-search found a candidate the first pass missed** and downloaded it:
  `av9ash/CSSR-S_labelled_suicidewatch_posts_reddit` (arXiv:2505.13480, CC-BY-4.0, not gated) →
  `data/finetuning-message/external/cssrs-llm-av9ash/labeled_rSuicidewatch_posts.csv`.
  **1,170 r/SuicideWatch posts**, 7-point C-SSRS `severity` ground-truth (0–6), **all with timestamps**
  (`created`) + 5 LLM label cols (gpt/claude/gemini/llama/mistral) — i.e. the paper's own LLM-ensemble approach.
  Severity dist (0–6): {0:351, 1:200, 2:302, 3:72, 4:37, 5:50, 6:158}.
  Defensible map to paper's 4-level: 0→Indicator, {1,2}→Ideation, {3,4,5}→Behavior, 6→Attempt
  → Indicator 351 · Ideation 502 · Behavior 159 · Attempt 158.
- 2026-06-21 — Confirmed `thisiskeithkwan/Reddit_C-SSRS` (HF) = the SAME Gaur 500 set (no new data);
  `dariolopez/*` = Spanish translations of it (off-language for the EN model). No other open 4-level sets on HF.

- 2026-06-21 — Built the enrichment toolchain (all tested):
  - `scripts/r2_scrape_suicidewatch.py` — pullpush.io scraper → per-author sequences (running, target 9k).
  - `scripts/r2_llm_label.py` — provider-agnostic (anthropic/openai/gemini) raw-HTTP labeler, 4-level + confidence, resumable.
  - `scripts/r2_build_dataset.py` — merges CSSRS-500 + av9ash(0-6→4-level) + scraped → `r2-combined/sequences.csv` (CSSRS schema).
  - `.env.example` — documented `LLM_PROVIDER`/`LLM_MODEL`/keys.
  - Builder verified on current data: **1,562 combined** (cssrs500 392 + av9ash 1170), class dist
    {Indicator 450, Ideation 673, Behavior 236, Attempt 203}. Scraped portion 0 until labeled.

- 2026-06-21 — Scrape pass 1 done: **3,478 author-sequences** (5,904 fetched → 4,431 usable posts;
  posts/author: 1:2937, 2:359, 3:103, 4:36, 5:43). Stopped early on a pullpush.io timeout streak (not true
  end). Made scraper **resumable** + able to distinguish timeout-failure from genuine empty; **resume running**.
  Pool now: 392 + 1,170 + 3,478 = **5,040** before labeling.
- 2026-06-21 — Azure `azure` provider wired into labeler; `.env` set. **Blocked on Azure content filter**
  (user adjusting; self-harm input filtered at medium). Validation call returned HTTP 400 content_filter.

- 2026-06-21 — **Scraper crash + fix:** comment scrape reached ~8,623 authors in memory but crashed on an
  uncaught `RemoteDisconnected` BEFORE the end-of-run write → all comment progress lost (files reverted to
  3,873). Fixed: `fetch_page` now catches all transient exceptions; added `save()` **checkpoint every 25
  pages** + save on interrupt/end. Re-launched comment scrape (resume from 3,873).
- 2026-06-21 — **Azure filter unblocked** (user adjusted; propagated). 20-seq test: 16 ok / 4 still
  content-filtered (~20% of the most graphic posts blocked even relaxed). **Cost trivial: ~$1–5 for 10k**
  (gpt-5.4-mini; ~454 in / 38 out tokens per seq). Latency 1.6s/seq → added `--workers` concurrency to labeler
  (8 threads → full run ~30–45 min). No budget approval needed given the cost.

- 2026-06-21 — Scrape finalized: **11,108 author-sequences** (49,607 fetched, 30,440 usable posts;
  submissions + comments). Labeled all 11,108 via Azure gpt-5.4-mini (8 workers, ~40 min): **10,011 labeled**,
  1,014 content-filtered (~9%), 83 errors. Of labeled: off-topic `-1` 1,397; on-topic {0-3} 8,614;
  conf≥0.6 → 8,511. Merged → **10,073** combined. Verified loads + R2 smoke-trains end-to-end.

## ⚠️ Reality vs target
**Faithful, open, downloadable-NOW 4-level C-SSRS data ≈ 1,562 samples** (CSSRS-500 392 user-seqs + av9ash 1,170 posts).
**10k of faithful open data does not exist today.** Bridging 1.5k→10k requires a fidelity tradeoff → user fork (M2).
Note granularity mismatch: CSSRS-500 = 5-post *user sequences*; av9ash = *single posts* (→ 1-post sequences). Loader must handle both.

## Remaining Action Items
- [ ] **Scrape running** (bg) — `scripts/r2_scrape_suicidewatch.py --target-authors 9000` → `scraped-suicidewatch/sequences.jsonl`
- [ ] **Waiting on user**: LLM API key in `.env` (`LLM_PROVIDER` + matching key) for `scripts/r2_llm_label.py`
- [ ] Run a 20-seq test label batch → measure per-seq cost → confirm full-run budget with user
- [ ] Full label run (resumable) → `scraped-suicidewatch/labeled.jsonl`
- [ ] Build unified loader: CSSRS-500 (4-level seqs) + av9ash (0-6→4-level posts) + scraped (LLM 4-level seqs, conf-filtered) → ~10k
- [ ] Verify count + class dist + R2 pipeline CPU smoke

## Decision Log additions (unit + tooling)
- **2026-06-21 — Unit = labeled samples, target ~10k total; scraped data grouped into per-author sequences
  (≤5 recent posts, real Δt timestamps).** More faithful to the paper's temporal-sequence design than
  av9ash's single posts; existing 392 CSSRS seqs + 1,170 av9ash posts (as 1-post seqs) count toward 10k.
- **2026-06-21 — Label directly on paper's 4-level scale + confidence (not av9ash's 0-6):** avoids a lossy
  0-6→4-level remap and matches CSSRS-500's native labels. Single-model labeling (user provides 1 key) →
  quality-filter by confidence threshold instead of the paper's inter-annotator agreement. Deviation logged.
- **2026-06-21 — Raw-HTTP LLM clients (anthropic/openai/gemini), no SDK install:** respects project rule
  "don't pip install unless asked"; provider chosen via `LLM_PROVIDER` env.
