# Paper 13 — PGKD: Performance-Guided LLM Knowledge Distillation for Text Classification

> Enrichment set · Pillar 3 (LLM-teacher distillation). Analysis depth: abstract + arXiv HTML. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** EMNLP 2024 (Industry).
- **Link:** [arXiv:2411.05045](https://arxiv.org/abs/2411.05045) · [ACL Anthology](https://aclanthology.org/2024.emnlp-main.215/) · open
  - *(Corrected: the enrichment doc's ResearchGate link 386201474 returns 403; this is the real id.)*
- **Pebble pillar:** teacher-LLM silver-label distillation into a small student.

## Summary
A **Claude-3** teacher generates synthetic training data into a **BERT-base student** via a performance-guided active-learning loop: the student's per-class validation metrics + hard negatives (high-confidence misclassifications) are fed back to the teacher, which generates the next batch of targeted silver examples — rather than one static silver set.

## Overlap with Pebble — 19% (peripheral)
`D1=0, D2=0, D3=0, D4=2, D5=0, D6=0, D7=1` → (2·2 + 1·1)/26 = 5/26 = **19%**
- **Closest on:** D4 (teacher-LLM silver-label distillation into a small student) and partial D7 (BERT-base student, same family as NeoBERT but ~110M).

## Best point — Method to adopt
The **iterative, error-targeted** distillation loop — generate new silver data for exactly the student's current failure regions.
- **How to apply to Pebble:** Make Gemini silver-label generation iterative: after each training round, surface the safety head's false-negatives and worst per-bin severity/emotion errors back to Gemini and ask for new examples in those regions. Directly serves the recall ≥ 0.95 floor by concentrating new silver on missed crisis cases.

## Dataset
Method paper — datasets are general-domain (news/reviews/Q&A), not relevant to acquire.

## Caveats
ResearchGate URL 403'd; scored from open arXiv HTML + EMNLP abstract (full method/results visible). Single-task multi-class, general domain, no continuous heads / MTL / safety — those dimensions are genuine zeros. The 130×/25× efficiency claims are inference-cost, not relevant to Pebble's training-side use.

## Deep research — full-PDF read (2026-06-10)

> Source note: the local PDF (`docs/papers/pdfs/13-pgkd-llm-distillation.pdf`) could not be rasterized in
> this environment (`pdftoppm`/poppler not installed; Bash unavailable), so the full text was read from the
> authoritative arXiv HTML render of the same paper (`arxiv.org/html/2411.05045v1`), which carries the
> complete method, Algorithm 1, all five result tables, the appendix prompts, and the Limitations/Ethics
> sections. All numbers below are quoted from that render with section/table references; none are inferred.

### What the paper actually does (method, data, results — from the PDF, with exact numbers)

**Setup.** Teacher = **Claude-3 Sonnet** (via AWS Bedrock); student = **BERT-base** (Sec. 4). The task is
highly multi-class, sparsely-annotated **topic classification**. The student is *not* trained on a large
gold set — it bootstraps from only **1,000 initial samples** (80/20 train/val split, Sec. 4) and grows its
training set through teacher generation.

**The performance-guided loop (Algorithm 1, Sec. 3).** Each of up to `num_kd_steps` iterations:
1. Train the student to convergence on the current data; evaluate on `D_val` to produce a **per-class
   classification report** (Accuracy, Precision, Recall, F1 *for every class*).
2. **Hard-negative mining:** collect the *misclassified* training samples on which the student's
   classification-head confidence is *highest* — i.e. confident-but-wrong examples.
3. Build the teacher prompt from four blocks (Algorithm 1 line 7 / Appendix A.1): the **class taxonomy**,
   **16 correctly-classified** examples, **16 misclassified** examples, **16 hard-negative** examples, and
   the **full per-class validation report** injected verbatim into the prompt.
4. Teacher generates **32 new training samples per iteration**, explicitly steered to "maximize model
   accuracy" on the weak classes named in the report.
5. **Early stopping:** if validation loss does not improve for `patience_limit` consecutive iterations,
   return `model_best` (Algorithm 1 lines 11–15).

**Exact hyperparameters (Sec. 4).** Student: max_seq_len 512, batch 64, **30 epochs**, LR **2e-5**, early-stop
patience **5**. Loop: **10 PGKD iterations**, PGKD patience **5**, **32 samples generated/iteration**, **16**
few-shot + **16 correct / 16 incorrect / 16 hard-negative** examples shown per prompt. (So the loop adds at
most 10×32 = **320 synthetic samples** on top of the 1,000 seed — the gain below comes from *targeting*, not
volume.)

**Datasets (Table 1).** AG-News (4 classes, 120k/7.6k), Yahoo Answers (10, 1.4M/60k), Huffington Post
(**41** classes, 160k/40k), AMZN Reviews (**335** classes, 40k/10k); plus IMDB (2) and Inshorts (7) for the
EvoKD comparison.

**Headline results (Table 2, Sec. 5)** — PGKD lifts BERT-base most where there are many classes, and the
**distilled student beats the Claude-3 teacher's own zero-shot accuracy**:
- AG-News (4): acc 0.884 → **0.895** (teacher 0.826).
- Yahoo (10): acc 0.649 → **0.685** (teacher 0.680).
- Huffington (41): acc 0.474 → **0.519**; weighted-F1 0.411 → **0.495** (teacher acc 0.442).
- AMZN (335): acc 0.320 → **0.443**; weighted-F1 0.244 → **0.382** (teacher acc 0.416). Note macro-F1 here
  stays low (0.074 → 0.159) and the *teacher* actually wins macro-F1 (0.364) — i.e. PGKD fixes the
  frequent/confident classes faster than the long-tail rare ones.

**Ablations (Table 4, Sec. 5.2).** Both signals matter and their value *grows with class count*:
- Remove **validation metrics**: AMZN 0.443 → **0.419** (vs AG-News only 0.895 → 0.893).
- Remove **hard negatives**: AMZN 0.443 → **0.433**, Huffington 0.519 → 0.510 — "particularly relevant to
  datasets with a high number of classes."

**vs EvoKD (Table 3, Sec. 5.1).** PGKD 0.908 / 0.943 (IMDB / Inshorts weighted-F1) vs EvoKD 0.798 / 0.851;
the authors attribute the gap to EvoKD showing the teacher *only* a few misclassified examples, with **no
view of the full class taxonomy or the validation report** — exactly the two signals PGKD adds.

**Cost (Table 5 / Sec. 5.3).** Per-batch inference: BERT+PGKD 21.45 s / \$0.0046 (CPU), 0.46 s / \$0.0107
(GPU) vs Claude-3 zero-shot 60.64 s / \$0.3867. Stated as "≈3× slower and **25× more expensive** than
BERT+PGKD on CPU, and ≈**130× slower** and 6× more expensive on GPU." These are **inference-side** numbers —
the paper gives **no teacher-side generation cost** for the distillation phase (an acknowledged gap).

### Parts directly useful for Pebble (specific: the active-learning loop, prompts, gating criteria, hyperparameters, cost numbers)

1. **The closed loop itself** (Algorithm 1): train → per-class validation report → mine confident-wrong
   examples → feed report+examples back to the teacher → generate targeted silver → repeat with early stop.
   This is a drop-in template for **Gemini → NeoBERT**, one loop per head.
2. **The prompt recipe** (Appendix A.1): taxonomy + correct + incorrect + hard-negative exemplars + the
   *verbatim per-class report*. The ablation proves both the report and the hard negatives carry real signal
   — so Pebble should inject both, not just "generate more crisis examples."
3. **Gating = confident-but-wrong, not just wrong.** Hard negatives are defined by the student's *own
   classification-head confidence* on its errors — a free signal Pebble already has at the safety head's
   sigmoid.
4. **Concrete knobs to copy as starting points:** 10 iterations, patience 5, ~32 generated/round, 16
   exemplars per bucket, LR 2e-5, early-stop on val loss. Small numbers — the method's leverage is targeting,
   not data volume (only ~320 synthetic samples total).
5. **The "student beats teacher" result** is the framing Pebble wants: a 250M encoder distilled this way can
   exceed Gemini's own zero-shot labels on the narrow task, which is the entire economic case for Pebble.

### How each part helps Pebble succeed (concrete actions: how to apply the error-targeted loop to the Gemini→NeoBERT safety head, expected payoff)

- **Run a safety-head-specific PGKD loop with an asymmetric gate.** Pebble's hard negatives are not generic
  "confident-wrong" — they are **false negatives** (crisis text the safety head scored as safe). After each
  training round, pull the highest-confidence FNs at the safety threshold, plus the per-class
  recall/precision report, and prompt Gemini: "the model missed these crisis utterances; generate N new
  paraphrase/variant crisis examples in the same register." This directly attacks the **recall ≥ 0.95 hard
  floor**, because the loop concentrates new silver exactly on the missed-crisis manifold — the analogue of
  PGKD's +0.123 accuracy jump on the hardest (335-class) dataset.
- **Inject the validation report verbatim, per Appendix A.1.** The ablation (remove-val-metrics: AMZN
  0.443→0.419) shows the report is the single most valuable prompt block on the hardest task. For Pebble the
  "hard task" *is* the rare crisis class, so the report block is where the payoff lives.
- **Keep the loop tiny and gated.** 10 iterations / patience 5 / ~32 examples/round means the whole
  error-targeted pass is cheap (hundreds of Gemini calls, not millions of tokens) — feasible to re-run after
  every safety-head retrain without a large teacher budget.
- **Reuse the per-class report for the severity/emotion heads too.** The same machinery (per-bin MAE/recall
  report → "generate examples for bins X,Y where the model under-predicts") feeds the continuous severity
  head and the GoEmotions-warm-started emotion head; PGKD's strongest gains were precisely on the many-class
  / long-tail regime that Pebble's 27-way emotion head and ordinal severity bins live in.
- **Expected payoff:** PGKD turned a static student that *lost* to the teacher into one that beats it on
  frequent classes by targeting; for Pebble the realistic win is moving the safety head's recall from "good
  on common crisis phrasings" to "covers the long tail of missed phrasings" without acquiring more gold data.

### Child mental-health lens (Pebble serves children: silver-labeling crisis text for minors — risks, teacher bias, mitigations, ethics caveats)

- **PGKD's own ethics statement is the warning Pebble must heed (Sec. 8.2):** "if the teacher model contains
  bias or even worse hallucinates, it will generate biased and even hypothetical data points," which the
  student then trains on, "perpetuating and amplifying" the bias. The paper offers **no empirical analysis of
  synthetic-label noise or hallucination rate** — so the loop is validated only on benign topic labels, never
  on safety-critical or minor-specific text. Pebble inherits this gap and must close it itself.
- **Generation, not just labeling, is the sharp edge for minors.** PGKD asks the teacher to *fabricate new
  crisis-like text*. For an adult-topic corpus that is harmless; for a child crisis head it means asking
  Gemini to synthesize **simulated minors' suicidal/self-harm utterances**. This raises (a) provider
  acceptable-use constraints (Gemini may refuse or sanitize, biasing the distribution toward "safe-sounding"
  crisis text and *under-covering* the real missed cases — the exact opposite of the recall goal), and (b) an
  ethics duty: synthetic minor-crisis text must be quarantined, access-controlled, and never surfaced.
- **Teacher bias is age-mismatched.** Gemini's prior on "what crisis looks like" is adult/clinical register;
  children express distress differently (indirect, somatic, gaming/school framing). A loop that trusts the
  teacher's generations uncritically will drift the safety head *toward* adult phrasing and *away* from how
  the actual users present — silently lowering real-world recall while validation recall looks fine.
- **Mitigations (beyond what the paper does):** (1) **human-in-the-loop gate** on every synthetic crisis
  example before it enters training — PGKD's auto-accept is not acceptable for minor safety data; (2) measure
  a synthetic-label **noise/QWK against a held-out human-annotated child slice** each round (e.g. the ESConv
  human-intensity calibration slice already flagged in the dataset plan) so teacher drift is caught; (3)
  **floor, never down-weight, the safety head** — the loop must only *add* recall, with a guardrail that a
  PGKD round which lowers held-out FN recall is rolled back; (4) prefer **paraphrase/augment of real
  consented crisis text** over free fabrication where provider policy and ethics allow, to keep the
  distribution anchored to genuine minor language.

### Limitations & open questions for Pebble

- **Long tail is exactly where it's weakest.** On 335-class AMZN, PGKD lifted *accuracy* (0.320→0.443) but
  **macro-F1 stayed 0.159 and the teacher beat it** (0.364) — i.e. the loop fixes frequent/confident classes,
  not rare ones. Pebble's crisis class *is* the rare class, so the paper's own evidence cautions that naive
  PGKD may not reach the rare-class recall Pebble needs without the FN-specific reweighting above.
- **No teacher-side cost reported** (Sec. 5.3 is inference-only). Pebble must budget Gemini generation calls
  itself; the saving grace is the loop is small (~320 examples over 10 rounds in the paper).
- **Single-task, single-head, flat cross-entropy.** PGKD never touches multi-task balancing, continuous
  regression, or an ordinal target — Pebble must adapt the "per-class report" abstraction to per-bin MAE/QWK
  for severity and to a recall-floored objective for safety; none of this is in the paper.
- **Prompt-engineering sensitivity is an admitted limitation (Sec. 7).** The loop's gains hinge on the report
  + exemplar prompt format; Pebble will need its own prompt tuning, and for crisis text that tuning interacts
  with provider safety filters in ways the paper never encountered.
- **No validation that "student beats teacher" survives a safety constraint.** The headline result is on
  accuracy/F1 with symmetric error costs. Whether a PGKD-distilled student can beat the teacher *under a hard
  recall floor with asymmetric crisis-miss cost* is an open question Pebble would be the first to answer —
  and a genuine paper-worthy contribution if it does.
