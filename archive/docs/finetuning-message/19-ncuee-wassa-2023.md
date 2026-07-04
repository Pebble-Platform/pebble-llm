# Paper 19 — NCUEE-NLP at WASSA 2023: Sentiment-Enhanced RoBERTa for Empathy + Emotion

> Enrichment set · Pillar 5 (intensity/empathy regression). Analysis depth: abstract + task desc. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** NCUEE-NLP, WASSA 2023 Shared Task 1 (ACL workshop).
- **Link:** [ACL Anthology 2023.wassa-1.49](https://aclanthology.org/2023.wassa-1.49/) · open
- **Pebble pillar:** continuous affect regression with RoBERTa-family encoders.

## Summary
An ensemble of three RoBERTa-family models (RoBERTa, RoBERTa-Twitter, EmoBERTa) for turn-level and essay-level empathy/distress/emotion-intensity **regression** at WASSA 2023. Track 2 (essay empathy/distress) Pearson 0.4178, rank 1 of 9.

## Overlap with Pebble — 31% (peripheral)
`D1=1, D2=1, D3=1, D4=0, D5=0, D6=0, D7=2` → (3·1 + 2·1 + 1·1 + 1·2)/26 = 8/26 = **31%**
- **Closest on:** D7 (RoBERTa encoder family) and D1 (continuous affect regression — but via separate ensembled models, not heterogeneous heads on a shared `[CLS]`; no categorical emotion or safety head).

## Best point — Method to adopt
Warm-starting from **affect/sentiment-domain-adapted checkpoints** (RoBERTa-Twitter, EmoBERTa) measurably lifts empathy/emotion regression over vanilla RoBERTa.
- **How to apply to Pebble:** Treat "affect-adapted init" as an explicit ablation arm alongside the GoEmotions warm-start and the staged freeze/unfreeze schedule — cheap signal on how much gain comes from affect-aware initialization vs the heads.

## Dataset
WASSA 2023 shared-task data (extends Buechel 2018; the base is acquired — see paper 23). Extended set is CodaLab-gated.

## Caveats
PDF body unreadable; architecture-level scores (D1, D5) rest on the ACL abstract + task description. "Ensemble of three RoBERTa variants" implies separate per-model heads, not one shared-encoder multi-task model → D1=1 (if a shared encoder w/ multiple heads, D1→2, ≈35%). No distillation/balancing/safety content.

> [2026-06-16] The "PDF body unreadable" caveat above is **now obsolete** — `pdftotext` extracts the
> full body, both result tables, and all hyperparameters cleanly. The deep-read section below supersedes
> it. The architecture read is confirmed: this is **not** a shared-encoder multi-head model; it is three
> **separately fine-tuned, single-output regressors per target**, averaged. So the original D1=1 stands.

## Deep research — full-PDF read (2026-06-16)

### Source-access note
- Local PDF `docs/papers/pdfs/19-ncuee-wassa-2023.pdf` read end-to-end via
  `pdftotext "docs/papers/pdfs/19-ncuee-wassa-2023.pdf" -`. Body, both Tables (1 = validation set,
  2 = test set), the §3.2 Settings block, and references all extracted cleanly — the earlier
  "PDF body unreadable" caveat no longer applies.
- Provenance validated against the **published venue version** (ACL Anthology, *Proceedings of the
  13th WASSA*, pages 548–552, Toronto, 2023):
  - Query: "NCUEE-NLP WASSA 2023 sentiment-enhanced RoBERTa Track 1 0.7236 Track 2 0.4178 ranking"
    → resolved `https://aclanthology.org/2023.wassa-1.49/` and the PDF `…/2023.wassa-1.49.pdf`.
  - WebFetch of the Anthology page confirms title, author list (Tzu-Mi Lin, Jung-Ying Chang,
    Lung-Hao Lee), and both headline numbers/ranks **verbatim**. The local PDF == the camera-ready;
    no preprint/venue delta. The published paper title is "…**Shared Task 1: Empathy and Emotion
    Prediction**…"; the running-head/abstract phrasing "…Empathy, Emotion, and Personality Shared
    Task: **Perceived Intensity Prediction**…" is the same paper (note the title-vs-header wording drift).

### What the paper actually does
**Task.** WASSA 2023 Shared Task 1, two regression tracks, both scored by **average Pearson correlation**:
- **Track 1 (CONV, speech-turn level):** predict perceived **empathy**, **emotion polarity**, **emotion
  intensity** for each speech-turn in a conversation.
- **Track 2 (EMP, essay level):** predict **empathy** and **distress** scores per essay (Buechel-2018 lineage).

**Method — three separately fine-tuned RoBERTa-family backbones, average-ensembled** (Fig. 1, §2):
1. **RoBERTa** (`roberta-base`, Liu et al. 2019) — vanilla baseline init.
2. **RoBERTa-Twitter** (`cardiffnlp/twitter-roberta-base-sentiment`, Barbieri et al. 2020) — RoBERTa
   continued-pretrained on **~58M tweets** and fine-tuned for sentiment on the **TweetEval** benchmark.
   This is the "sentiment-enhanced" affect-adapted init.
3. **EmoBERTa** (`tae898/emoberta-base`, Kim & Vossen 2021) — RoBERTa adapted for **emotion recognition
   in conversation (ERC)**; learns speaker-aware states by prepending speaker names and inserting
   separator tokens between utterances.

Crucially (§2): "we **separately fine-tuned these transformers for empathy, emotion polarity and
emotion intensity** prediction" (Track 1) and "**respectively trained** the transformers for empathy
and distress" (Track 2). So there is **one model per (backbone × target)** — no shared `[CLS]`,
no multi-task head sharing, no loss balancing. The three backbones' outputs are combined by a plain
**average ensemble** (unweighted mean of predictions).

**Backbone source = exact HuggingFace checkpoints** (footnote 1, §3.3):
`huggingface.co/roberta-base`, `huggingface.co/tae898/emoberta-base`,
`huggingface.co/cardiffnlp/twitter-roberta-base-sentiment`.

**Hyperparameters (§3.2 Settings — identical across all backbones/targets):**
epochs **25**, batch size **8**, learning rate **1e-5**, max sequence length **256**.
No staged unfreezing, no discriminative LR, no MLM pass, no scheduler/optimizer detail given.

**Data sizes (§3.1, all organizer-provided):**
- Track 1: train **8,776** / val **2,400** / test **1,425** conversations.
- Track 2: train **792** / val **208** / test **100** essays. (Track 2 is *tiny*.)

**Table 1 — validation set (Pearson):**

| Backbone | T1 Empathy | T1 EmoPol | T1 EmoInt | **T1 Avg** | T2 Empathy | T2 Distress | **T2 Avg** |
|---|---|---|---|---|---|---|---|
| RoBERTa | 0.7715 | 0.7608 | 0.6941 | 0.7421 | 0.6660 | 0.5596 | 0.6128 |
| RoBERTa-Twitter | 0.7871 | 0.7671 | 0.7061 | **0.7534** | 0.6000 | 0.5564 | 0.5782 |
| EmoBERTa | 0.7693 | 0.7659 | 0.6899 | 0.7417 | 0.6278 | 0.5454 | 0.5866 |
| **Ensemble** | 0.7901 | 0.7751 | 0.7076 | **0.7576** | 0.6702 | 0.5905 | **0.6304** |

**Table 2 — test set (Pearson; "Ensemble" row = official submission):**

| Backbone | T1 Empathy | T1 EmoPol | T1 EmoInt | **T1 Avg** | T2 Empathy | T2 Distress | **T2 Avg** |
|---|---|---|---|---|---|---|---|
| RoBERTa | 0.7849 | 0.6851 | 0.6384 | 0.7028 | 0.3327 | 0.3819 | 0.3573 |
| RoBERTa-Twitter | 0.7898 | 0.6941 | 0.6760 | **0.7200** | 0.3661 | 0.3415 | 0.3538 |
| EmoBERTa | 0.7720 | 0.6638 | 0.6418 | 0.6925 | 0.4074 | 0.4663 | **0.4368** |
| **Ensemble (official)** | 0.8035 | 0.6981 | 0.6692 | **0.7236** | 0.4150 | 0.4206 | 0.4178 |

**Official results & ranks (§3.4, abstract — ✔ corroborated against ACL page):**
- Track 1 ensemble avg Pearson **0.7236 → rank 4** (✔).
- Track 2 ensemble avg Pearson **0.4178 → rank 1 of 9** (✔).

**The load-bearing ablation (what affect-adapted init buys), read straight off Table 2:**
- **Track 1 test avg:** RoBERTa-Twitter standalone **0.7200** > vanilla RoBERTa **0.7028** (**+0.0172**,
  ≈ +2.4% relative). On the single emotion-intensity head — Pebble's nearest analogue — RoBERTa-Twitter
  **0.6760** vs RoBERTa **0.6384** (**+0.0376**, ≈ +5.9% rel). ✔ (Table 2, test).
- **Track 2 test avg:** **EmoBERTa standalone 0.4368** is the **single best system in the whole paper**
  — it beats the official average-ensemble (**0.4178**) and crushes vanilla RoBERTa (**0.3573**):
  affect-adapted init buys **+0.0795 avg Pearson, ≈ +22% relative** over vanilla. On distress alone,
  EmoBERTa **0.4663** vs RoBERTa **0.3819** = **+0.0844** (≈ +22% rel). ✔ (Table 2, test).
- **The ensemble is not free.** On Track 2 *test*, averaging in the two weaker backbones (RoBERTa 0.357,
  RoBERTa-Twitter 0.354) *dragged the EmoBERTa winner down* from 0.4368 → 0.4178 (−0.019). The authors
  picked the ensemble as the official submission because on the *validation* set the ensemble led every
  column (Table 1); on *test* it did not — a small-N (100-essay) overfit-to-val signature.
- **Affect init is target-dependent, not universal.** On Track 2, RoBERTa-Twitter *underperformed
  vanilla* (val 0.578 vs 0.613; test 0.354 vs 0.357). Twitter-sentiment adaptation helped the
  turn-level affect targets (Track 1) but hurt the long-essay empathy/distress target; **EmoBERTa**
  (ERC-adapted) was the consistent affect-init winner on Track 2.

### Parts directly useful for Pebble
1. **Exact affect-adapted init checkpoints + their measured lift over vanilla RoBERTa** —
   `cardiffnlp/twitter-roberta-base-sentiment` and `tae898/emoberta-base`, with Table-2 deltas of
   +0.017 (T1 avg) / +0.038 (emotion-intensity head) and +0.080 (T2 avg) / +0.084 (distress).
   **→ D-D, D-F.** This is a clean, public-checkpoint precedent that domain-/affect-adapted
   initialization measurably lifts continuous-affect regression.
2. **Pearson is the operative metric for the affect-regression heads** (both tracks, all tables).
   The bars: turn-level affect heads land **0.64–0.80 Pearson**; essay-level empathy/distress land
   **0.35–0.47 Pearson** on a 100-item test. **→ D-D** (severity/energy regression metric = Pearson;
   realistic ceilings per granularity).
3. **One-model-per-target, average-ensembled** baseline with full hyperparameters
   (epochs 25 / bs 8 / lr 1e-5 / maxlen 256). **→ D-D** as the *naïve* contrast to Pebble's
   shared-encoder multi-head design — a cheap reference point.
4. **The ablation method itself** (standalone-backbone rows vs ensemble row, val *and* test) is a
   template for Pebble's "affect-adapted init" ablation arm. **→ D-F**.
5. **Negative result: affect-init transfer is target-specific** (Twitter-sentiment helped Track 1,
   hurt Track 2; ERC-adapted EmoBERTa helped Track 2). **→ D-F** — pick the init whose *adaptation
   domain matches the target head*, don't assume one affect-init wins everywhere.

### How each part helps Pebble succeed
- **D-F (domain-adaptive init / MLM ablation) — concrete arms.** Pebble's planned "affect-adapted init"
  ablation now has named, public baselines to cite and (optionally) reproduce as RoBERTa-family
  reference rows: vanilla `roberta-base` vs `cardiffnlp/twitter-roberta-base-sentiment` vs
  `tae898/emoberta-base`. The lesson for Pebble's NeoBERT: budget an **MLM/affect continued-pretrain
  pass** (FAIIR-style) *and* report the lift, because here the affect-adapted init bought up to
  **+22% relative Pearson** on distress with zero architecture change. The transferable claim is
  "match the adaptation domain to the head": Pebble's `severity` head (distress-like) should warm-start
  from an *emotion/distress*-adapted init, not a generic Twitter-sentiment one.
- **D-D (severity/energy regression) — set the metric and the ceiling.** Adopt **Pearson** as the
  primary regression metric for `severity`/`energy` (this paper, FAIIR-adjacent WASSA lineage, and the
  whole WASSA shared task all use it). Calibrate expectations by granularity: this paper shows
  **turn-level** affect regression (Pebble's regime) reaching **~0.64–0.80 Pearson**, while *essay*-level
  empathy/distress on 100 items only reaches **~0.42** — small test sets give noisy, low Pearson. Pebble
  should size its severity-regression eval set accordingly (the 100-essay test here flipped the
  val-winning ensemble into a test-loser).
- **D-D contrast — justify the shared-encoder design.** This paper's separate-model-per-target ensemble
  is the *anti-pattern* Pebble departs from: it trains 3 backbones × N targets and averages, with no
  parameter sharing and no loss balancing. Cite it as the simple baseline Pebble's single NeoBERT +
  heterogeneous heads aims to beat on cost (1 encoder vs 3) while keeping the affect-init benefit.

### Child mental-health lens
- **Domain mismatch is total.** Both tracks are **adult** data: Track 2 is the Buechel-2018 news-empathy
  essay corpus (adult crowdworkers reacting to news); Track 1 is adult conversational empathy. The
  affect-init checkpoints are adult-register too — TweetEval is general adult Twitter; EmoBERTa is trained
  on MELD/IEMOCAP (adult TV/acted dialogue). **None of these touch child register.** The *magnitude* of
  the affect-init lift (+22% rel on distress) is an adult-essay number and must be treated as an
  upper-bound hypothesis for Pebble, not a transferable estimate.
- **What *does* transfer** is the **mechanism and the metric**, not the numbers: (a) affect-/emotion-
  adapted initialization lifts continuous-affect regression, and (b) Pearson is the right yardstick.
  Pebble should re-measure the lift on its own (silver-labelled, child-facing) data before claiming any
  effect size.
- **Granularity is favorable.** Unlike FAIIR (whole-conversation) and most C-SSRS work (post-level),
  this paper's Track 1 is genuinely **turn-level** — matching Pebble's mid-conversation scoring regime —
  and turn-level affect regression there is *easier* (0.64–0.80) than essay-level (0.42). That's mild
  encouragement that Pebble's turn-level severity/emotion targets are tractable.
- **Ethics / safety:** the paper has **no safety component, no calibration, no recall floor, no
  thresholding** — it is a pure leaderboard regression system. Nothing here informs Pebble's safety
  pathway; it informs only the affect-regression heads.

### Limitations & open questions for Pebble
- **Contradiction vs FAIIR (paper 01) on domain adaptation cost/benefit.** FAIIR *claims* domain-adaptive
  MLM "significantly enhances" performance but **never isolates** it (no ablation). This paper *does*
  isolate the affect-adapted-init contribution (standalone-backbone rows) and shows it is **large
  (+22% rel on distress) but target-dependent and not always positive** (RoBERTa-Twitter *hurt* Track 2).
  Together they tell Pebble: domain/affect adaptation is worth an explicit ablation arm (FAIIR never ran
  one; this paper's is informal), and the result may differ per head — do not assume one adapted init
  helps all of `emotion` + `severity`.
- **Contradiction with the paper's own conclusion.** The abstract/§3 conclude "the ensemble averaging
  mechanism works well." Table 2 (test) contradicts this for Track 2: the **standalone EmoBERTa (0.4368)
  beat the official ensemble (0.4178)**. The ensemble "win" was a validation-set artifact on a 100-essay
  test — a cautionary tale for Pebble about trusting ensemble gains measured on tiny dev sets.
- **No shared-encoder multi-task evidence.** This paper cannot inform **D-A/D-B** (backbone choice, MTL
  loss balancing) — it deliberately avoids parameter sharing. Pebble's central design bet (one encoder,
  many heads, balanced losses) is *untested* here; the paper is only a baseline for the affect-init
  question (D-D/D-F).
- **No MLM pass at all.** Despite being the headline "domain-adaptive init" exemplar in this run, the
  paper does **continued-pretrain-then-use-off-the-shelf** (it consumes already-adapted public
  checkpoints) — it never runs its **own** MLM pass on the task corpus. So it validates *using* an
  affect-adapted init, but gives Pebble **zero guidance on the cost/recipe of an in-house MLM pass**
  (epochs, mask rate, corpus size). For that, Pebble must lean on FAIIR (paper 01: 15% mask, 1 epoch,
  maxlen 1500) — these two papers are complementary, not redundant, on D-F.
- **Open question:** is the affect-init lift additive with a shared-encoder + MTL setup, or does
  multi-task training already absorb most of it? Neither paper answers this; it is exactly the
  measurement Pebble's D-F ablation on NeoBERT would contribute first.
