# Paper 16 — Evaluating LLM Reasoning for Suicide Screening with the C-SSRS

> Enrichment set · Pillar 4 (C-SSRS severity). Analysis depth: abstract + arXiv HTML. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** 2025.
- **Link:** [arXiv:2505.13480](https://arxiv.org/abs/2505.13480) · open · [code](https://github.com/av9ash/llm_cssrs_code)
- **Pebble pillar:** suicide-risk severity; LLM-vs-human label agreement (informs the Gemini-teacher question).

## Summary
Zero-shot evaluation of frozen decoder LLMs (Claude/GPT/Mistral/LLaMA) on the C-SSRS 7-point ordinal scale over r/SuicideWatch posts — no fine-tuning, no heads. Analyzes where models' severity judgments err.

## Overlap with Pebble — 31% (peripheral)
`D1=0, D2=2, D3=0, D4=1, D5=0, D6=1, D7=0` → (2·2 + 2·1 + 2·1)/26 = 8/26 = **31%**
- **Closest on:** D2 (suicide-risk domain) and, weakly, D6/D4 (crisis severity as the task; LLM-vs-human agreement on severity labels).

## Best point — Design lesson
Models make almost all errors between **adjacent** C-SSRS levels (ordinal sensitivity); Mistral wins on ordinal *error*, not exact accuracy.
- **How to apply to Pebble:** For the CSSRS-Reddit signal feeding Pebble's severity head, use an **ordinal / distance-aware loss and metric** (MAE / QWK / ordinal-regression CE), not flat CE, so adjacent-level confusions cost less than far ones — and report ordinal error, not just macro-F1.

## Dataset
Uses public r/SuicideWatch; no new dataset to acquire. Code is open.

## Caveats
Scored from abstract + HTML landing page; full PDF (confusion matrices, dataset size/split, prompt design) unread → lowers confidence on D4/D6. Zero-shot evaluation of frozen LLMs — no encoder fine-tuning, MTL, or actual distillation training, so D1/D3/D5/D7 are firmly 0.

## Deep research — full-PDF read (2026-06-16)

> PDF read via `pdftotext "docs/papers/pdfs/16-llm-cssrs-screening.pdf" -` (local copy is
> arXiv:2505.13480**v1**, 11 May 2025). Every load-bearing number was re-checked against the
> published arXiv HTML (`https://arxiv.org/html/2505.13480v1`) and the abstract on HuggingFace
> Papers — all corroborated exactly (Table I matches to 4 decimals). Note a **title revision**: the
> v1 PDF reads "Evaluating **LLM Reasoning** for Suicide Screening…" while the current arXiv listing
> reads "Evaluating **Reasoning LLMs** for Suicide Screening…" — same paper, same authors (Patil,
> Tao, Gedhu), same numbers. This section adds full-PDF detail the stub above (abstract/HTML scoring)
> could not see; cross-refs point back to the stub.

### Source-access note
- **Local PDF**: `pdfs/16-llm-cssrs-screening.pdf`, extracted whole (method, dataset, Table I, the
  Confusion/Error-analysis prose, and the Appendix with the verbatim prompt and three example posts
  with each model's JSON output).
- **Web validation queries → URLs**:
  - `Patil Tao Gedhu "Evaluating LLM Reasoning for Suicide Screening" C-SSRS` → published arXiv PDF
    `https://arxiv.org/pdf/2505.13480` + HuggingFace `https://huggingface.co/papers/2505.13480`
    (confirms author list, 6-model set, "Mistral lowest ordinal error", adjacent-level errors).
  - `arXiv 2505.13480 C-SSRS … Claude QWK Mistral MAE confusion matrix` → arXiv HTML
    `https://arxiv.org/html/2505.13480v1` (confirms Claude acc 0.7331 / F1 0.7505 / QWK 0.8758,
    Mistral MAE 0.4398 / MSE 1.0067 / QWK 0.8767, κ=0.82, model versions, CoT prompt).
- **Status tags**: ✔ corroborated against published HTML · ≈ approximate · ✖ uncorroborated.

### What the paper actually does
- **Task** (§IV): zero-shot, chain-of-thought classification of single Reddit r/SuicideWatch posts
  onto the **7-point C-SSRS ordinal scale, Level 0–6** (0 = not suicide-related; 1–6 = the six
  successive C-SSRS questions: 1 wish-to-be-dead, 2 active ideation, 3 method-thinking, 4 ideation
  with some intent, 5 ideation with plan/intent, 6 behavior/attempt). ✔
- **Models** (§IV-B): five LLMs at their **default configs**, *exact versions* — **Claude 3 Sonnet,
  ChatGPT o3-mini, Gemini 1.5 Pro, Mistral (Pixtral) Large, LLaMA (2/3)** — plus an **SVM baseline**
  (six systems → six Table-I columns; the abstract's "six models" counts the SVM). ✔ The paper's body
  is internally sloppy ("We evaluated five advanced LLMs" §IV vs. abstract "six models") — the SVM is
  the sixth. ✔ *Caveat for Pebble:* "Mistral (Pixtral) Large" and "Gemini 1.5 Pro" are **multimodal**
  models run text-only; "LLaMA (2/3)" is not pinned to one version — provenance of the open-weight
  rows is weak. ≈
- **Prompt** (§IV-A.2 + Appendix, verbatim): one multi-part prompt for all models — instruction to
  score 0–6, the six C-SSRS questions each tagged with its severity number, and a **forced JSON
  schema** `{"Q1".."Q6": reasoning-or-"N/A", "severity": int 0-6}`. **CoT only** — few-shot and
  instruction-tuning variants were deliberately *not* run (deferred to the authors' companion paper,
  arXiv:2503.10095). ✔
- **Data** (§III): r/SuicideWatch via Reddit API, **>3,000 posts collected (Dec 2024)** → filtered to
  **~1,200** by (a) **title+selftext < 128 words** and (b) **one post per user** (drop multi-posters
  to avoid user-level confounds). The authors explicitly *reject* adding prior-post/temporal context
  — they found it "introduced irrelevant noise, occasionally even confounding human annotators." ✔
- **Labels** (§III-B): **trained psychologists + two trained C-SSRS assessors** annotated all ~1,200
  posts by official C-SSRS guidelines; final label by **majority vote**; **inter-annotator agreement
  Cohen's κ = 0.82** ("substantial"). ✔ The severity distribution is **imbalanced** (Fig. 4; authors
  flag the need for "weighted loss functions, or resampling"). ✔
- **Headline results (Table I, sorted by F1)** — all ✔ corroborated:

  | System | Acc | Prec\* | Recall\* | F1\* | MAE↓ | MSE↓ | QWK↑ | SRC↑ |
  |---|---|---|---|---|---|---|---|---|
  | **Claude 3 Sonnet** | **0.7331** | **0.7880** | **0.7331** | **0.7505** | 0.4502 | 1.0427 | 0.8758 | 0.8809 |
  | GPT o3-mini | 0.7278 | 0.7818 | 0.7278 | 0.7384 | 0.4884 | 1.1481 | 0.8692 | **0.8843** |
  | **Mistral (Pixtral) Lg** | 0.7132 | 0.7478 | 0.7132 | 0.7208 | **0.4398** | **1.0067** | **0.8767** | 0.8640 |
  | LLaMA | 0.6560 | 0.7477 | 0.6560 | 0.6839 | 0.6049 | 1.3633 | 0.8444 | 0.8766 |
  | Gemini 1.5 Pro | 0.5958 | 0.6901 | 0.5958 | 0.6160 | 0.6285 | 1.3565 | 0.8322 | 0.8308 |
  | SVM baseline | 0.5583 | 0.5437 | 0.5583 | 0.5385 | 0.8958 | 2.6792 | 0.6502 | 0.6137 |

  \*Prec/Recall/F1 are **weighted averages across classes** (note recall ≡ accuracy here because it is
  weighted recall on a single-label multiclass task). **The key split**: Claude/GPT win the
  classification metrics; **Mistral wins the *ordinal-error* metrics (MAE/MSE) and ties-best QWK** —
  i.e., the best-F1 model is *not* the best-calibrated-by-distance model. ✔
- **Confusion structure (§V-B, §V-C — narrative only; matrices are Fig. 6 images, no numeric table)**:
  *all* models' errors cluster on **adjacent severity levels** — diagonals dominant, off-diagonal mass
  one step away. Specific confusions called out: **Level 3↔4** (active ideation *without* vs *with*
  intent — "the nuanced language used to convey intent" — worst for **GPT and Claude**); **Level 5↔6**
  (plan vs. actual attempt — worst for **Gemini and LLaMA**, when a prior attempt is "omitted or
  obscured"); **Level 0→1/2 false positives** (Mistral and Gemini "overly sensitive to emotionally
  charged language," over-classify non-suicidal posts upward). SVM is the only model with
  *non-adjacent* (far) confusion → no strong diagonal. ✔ (per-cell counts ✖ — not published.)

### Parts directly useful for Pebble
1. **Adjacent-error → ordinal/distance-aware loss + metric (D-C, primary).** The paper's central
   empirical fact is that on C-SSRS, errors are overwhelmingly ±1 level, and the model that minimizes
   *distance* error (Mistral, MAE 0.4398) is *different* from the model that maximizes exact F1
   (Claude, 0.7505). Transfer: Pebble's C-SSRS-Reddit severity signal must be trained with a
   **distance-aware objective** (ordinal-regression CE / CORN / soft-label or a regression head with
   MSE) **and reported with MAE + QWK + Spearman**, not flat CE + macro-F1 alone — flat CE treats a
   0→6 miss the same as a 3→4 miss, which is exactly the cost structure this paper shows is wrong.
2. **QWK/SRC as the headline ordinal metric (D-C / D-G).** The paper uses **QWK and Spearman's ρ** as
   its agreement metrics, with QWK explicitly "penalizing bigger mistakes more heavily … useful for
   ordinal data." Transfer: add **QWK** (and Spearman) to Pebble's severity-head eval suite as the
   primary number for "did we get the ordering right," with MAE for magnitude.
3. **The teacher-calibration answer for silver labels (D-G, primary).** This is the
   "is the LLM teacher even good at C-SSRS?" datapoint. Best zero-shot agreement with *human* C-SSRS
   labels is **Claude QWK ≈ 0.876 / acc ≈ 0.73 / F1 ≈ 0.75**, against a human **inter-annotator
   κ = 0.82**. So the best LLM is *near but below* human–human reliability, and **Gemini 1.5 Pro is
   the *weakest* LLM (acc 0.596, QWK 0.832)** of the five. Transfer: if Pebble distills silver C-SSRS
   labels from a Gemini teacher, **expect teacher noise ≈ adult-Reddit QWK 0.83 at best**, concentrated
   as ±1-level error and as **upward over-classification of emotionally-charged-but-non-suicidal text
   (Level 0→1/2)** — budget for it and prefer a stronger teacher (Claude-class) or multi-judge vote.
4. **Imbalance handling is required, not optional (D-C / D-B).** Authors flag the severity
   distribution is imbalanced and prescribe "weighted loss functions, or resampling." Transfer:
   Pebble's severity head over silver C-SSRS labels needs class-frequency weighting / resampling on
   top of the ordinal loss, or the head will collapse toward the modal mid-levels.
5. **Input-length & context findings (D-H, minor).** Posts were capped at **<128 words** and the
   authors *removed* multi-post/temporal context as net-harmful. Transfer: corroborates that
   **short, single-turn text carries enough C-SSRS signal** for severity scoring — encouraging for
   Pebble's *turn-level* regime, and an argument that NeoBERT's 4K window is far more than this task
   needs. But note this is the opposite finding from context-rich pipelines (see contradiction below).

### How each part helps Pebble succeed
- **Severity head (D-C):** swap flat CE for an **ordinal loss** (ordinal-regression CE / CORN, or a
  regression head trained with MSE then rounded) on the CSSRS-Reddit signal; in `eval/`, report
  **QWK + MAE + Spearman** beside accuracy/macro-F1. Concretely: this paper's adjacent-error result is
  the citation justifying that choice, and Mistral-MAE-0.4398-beats-Claude-F1 is the worked example
  that exact-accuracy alone hides ordinal quality.
- **Teacher/silver-label calibration (D-G):** add a **teacher-audit step** to Pebble's distillation —
  score the chosen LLM teacher's C-SSRS labels against any available human-labeled slice and report
  QWK; this paper says **don't assume the teacher is at human reliability** (best LLM QWK 0.876 <
  human κ irrelevant-but-near; weakest, Gemini, only 0.832). If the v1 teacher is Gemini-class, this is
  a direct argument to upgrade or ensemble teachers for the severity head.
- **Loss balancing (D-B/D-C):** apply class-frequency weighting / resampling to the severity head, as
  the paper prescribes for the imbalanced C-SSRS distribution.
- **Eval-set design (D-H):** because errors are ±1, **build the severity test set to cover every level
  0–6** (a random Reddit slice under-samples the rare high levels 5/6) so QWK isn't dominated by the
  modal mid-levels — mirrors the half-curated eval lesson from 01-faiir.

### Child mental-health lens
- **Register mismatch is the dominant risk (transfer).** All data is **adult r/SuicideWatch** — users
  who *self-identify as in crisis and explicitly seek a suicide forum*. The C-SSRS questions assume
  fairly explicit disclosure ("worked out the details of how to kill yourself"). Pebble's targets are
  **children, turn-level, mid-conversation**, who voice distress *indirectly/relationally* (cf.
  01-faiir's suicide-tag keywords *plan, home, school, friend*). So the **±1-adjacent-error finding
  transfers as a principle** (use ordinal loss/metric), but the **absolute numbers (QWK ≈ 0.83–0.88)
  do NOT transfer** to child register — they are an *upper-bound on a maximally-explicit adult forum*.
  State plainly: a child-facing severity head should expect *worse* exact agreement and *more* of the
  Level-0→1/2 false-positive pattern (emotionally-charged-but-not-suicidal), because children's
  ordinary distress vocabulary overlaps crisis vocabulary more.
- **The false-negative asymmetry is the ethics core (matches Pebble).** §V-D: the authors single out
  **false negatives on Levels 5–6** (under-estimating imminent risk) as the gravest failure, exactly
  Pebble's recall-floor concern. Mitigation they advocate — **human-in-the-loop + tiered intervention,
  LLM as assistive not autonomous** — is the same role boundary Pebble enforces (heads inform a
  Decision Engine; escalation is a product invariant). Their finding that some models *over*-classify
  Level 0→up is actually the *safer* direction for a recall-first child tool.
- **No fine-tuning, no child data, no calibration curves** — this paper gives Pebble a *teacher-quality
  prior* and a *loss/metric prescription*, not a transferable model or threshold.

### Limitations & open questions for Pebble
- **Contradiction vs. Paper 06 (Gaur "Knowledge-aware … severity of suicide risk", ref [6] here)
  and vs. context-rich pipelines:** Paper 16 *deliberately strips* user-level/temporal context, finding
  it "introduced irrelevant noise," whereas the very C-SSRS-Reddit lineage it cites (Gaur et al.,
  WWW'19) argues *external/temporal knowledge improves* ideation-vs-intent separation — the exact
  Level-3↔4 confusion Paper 16 then reports as its hardest case. **Open question for Pebble:** is the
  3↔4 (intent) confusion a *context* problem (needs conversation history → favors multi-turn) or an
  *intrinsic* single-text ceiling? Pebble is turn-level, so if context is the cure, Pebble inherits the
  ceiling and should not over-promise fine-grained intent levels from one turn.
- **Contradiction vs. the stub's "Mistral wins on ordinal error" framing:** corroborated, but the stub
  under-states that **Claude and Mistral are nearly tied on QWK (0.8758 vs 0.8767)** — QWK does *not*
  cleanly separate them; the separation is on **MAE/MSE only**. The cleaner Pebble lesson is "report
  MAE *and* QWK, because they can disagree on the winner," not "Mistral is the ordinal champion."
- **Per-level recall is unavailable (✖).** The confusion matrices are **image figures (Fig. 6), with
  no numeric per-cell or per-level recall table** — the stub's hope for "per-level recall numbers"
  cannot be met from this paper; only the *narrative* adjacency pattern is published. To get per-level
  recall, Pebble would have to **re-run from the open code** (`github.com/av9ash/llm_cssrs_code`).
- **Model-version provenance is soft (≈).** "LLaMA" is unpinned; "Mistral (Pixtral) Large" and
  "Gemini 1.5 Pro" are multimodal models used text-only; the body says "five LLMs" but the abstract
  says "six." Treat the *ranking* as robust, individual open-weight rows as approximate.
- **No calibration/ECE, no thresholds, n≈1,200, single platform.** Tiny adult-Reddit sample, no
  reliability diagrams — so this paper informs **D-C (loss/metric)** and the **teacher-quality side of
  D-G**, but contributes **nothing to threshold/recall-floor policy** (that stays from 01-faiir's
  per-tier thresholds).
