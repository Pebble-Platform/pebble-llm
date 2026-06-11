# Paper 12 — MentalBERT: Publicly Available Pretrained Language Models for Mental Healthcare

> Enrichment set · Pillar 2 (mental-health encoders). Analysis depth: abstract + PDF excerpt. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Ji, Zhang, Ansari, Fu, Tiwari, Cambria. LREC 2022.
- **Link:** [arXiv:2110.15621](https://arxiv.org/abs/2110.15621) · open · weights on HF (`mental/mental-bert-base-uncased`, `mental/mental-roberta-base`, `AIMH/mental-roberta-large`)
- **Pebble pillar:** domain-adaptive mental-health encoder backbone / baseline.

## Summary
BERT/RoBERTa-base (~110M) domain-adaptively MLM-pretrained on mental-health Reddit, evaluated on single-task depression, stress, and suicidal-ideation detection. Domain pretraining beats general-domain BERT on these tasks.

## Overlap with Pebble — 27% (peripheral)
`D1=0, D2=2, D3=0, D4=0, D5=0, D6=1, D7=1` → (2·2 + 2·1 + 1·1)/26 = 7/26 = **27%**
- **Closest on:** D2 (mental-health/crisis text incl. suicidality) and D7 (encoder-only BERT/RoBERTa family — but base ~110M, half NeoBERT's 250M).

## Best point — Method to adopt
Domain-adaptive MLM continued-pretraining on mental-health text is a cheap, validated win, upstream of head design.
- **How to apply to Pebble:** Run a short MLM continued-pretraining pass of NeoBERT on in-domain emotional-support/Reddit text (or benchmark against MentalRoBERTa) for a better-adapted `[CLS]` start in the low-resource regime.

## Dataset / weights status
Model weights available on HF (soft-gate), **CC-BY-NC-4.0 → research-only, NOT deployable**. Pretraining corpus is private (not released). Eval datasets (CLPsych 2015, eRisk 2018) are gated/research-only. → use as a **research-arm** warm-start/baseline only; the deployed encoder must warm-start from an openly-licensed backbone.

## Caveats
Pre-LLM-distillation work, so D4/D5 absence is expected. Exact param count / per-dataset F1 not fully rendered; D6/D7 scored conservatively. Already referenced as the "MentalBERT line" in `related-work-survey.md`.

## Deep research — full-PDF read (2026-06-10)

> Read via the rendered full text (ar5iv mirror of arXiv:2110.15621) because the local PDF could not be
> rasterized in this environment (`pdftoppm`/poppler unavailable) and the binary PDF defeated the text
> extractor. All numbers below are quoted from the paper body and its Tables 2–3; license/weights facts
> are from the HF model cards (the paper itself does not state a license). Where the rendered text omits a
> value (e.g. max sequence length, mask probability), it is marked **[not stated in paper]** rather than guessed.

### What the paper actually does (method, data, results — from the PDF, with exact numbers)

**Goal.** Domain-adaptive continued MLM pretraining of two general encoders on mental-health Reddit text,
then single-task fine-tuning on a battery of mental-disorder detection benchmarks. The thesis: in-domain
pretraining beats general-domain (BERT/RoBERTa) and biomedical/clinical (BioBERT, ClinicalBERT) encoders
on mental-health classification.

**Pretraining corpus (the recipe).**
- Source: Reddit, from **7 mental-health subreddits** — r/depression, r/SuicideWatch, r/Anxiety,
  r/offmychest, r/bipolar, r/mentalillness, r/mentalhealth.
- Size: **13,671,785 sentences** of training text. Only **anonymous, publicly available posts**; user
  profiles deliberately not collected. Date range and scraping tool: **[not stated in paper]**.
- The corpus itself is **not released** (only the resulting weights are).

**Models & training hyperparameters.**
- **MentalBERT** = continued MLM pretraining initialized from **BERT-base-uncased** (12-layer, 768-hidden,
  12-head, **110M params**). **MentalRoBERTa** = same procedure from **RoBERTa-base**, using RoBERTa's
  **dynamic masking**.
- Training: **624,000 iterations**, **batch size 16 per GPU**, on **4× Nvidia Tesla V100**, taking
  **~8 days**. Max sequence length, MLM mask probability and pretraining optimizer: **[not stated in
  rendered text]**.
- **Fine-tuning** (for the downstream benchmarks): feature = the **`[CLS]` embedding of the last hidden
  layer**, fed to an **MLP with tanh activation**; **Adam**; **lr 1e-5 for the encoder, 3e-5 for the
  classification layers**. The whole encoder is fine-tuned (not frozen). Epochs: **[not stated]**.

**Downstream datasets (8 benchmarks, all single-task classification).**

| Dataset | Platform | Task | Classes | Train / Valid / Test |
|---|---|---|---|---|
| SWMH | Reddit | multi-disorder | multi | 34,823 / 8,706 / 10,883 |
| eRisk18 T1 | Reddit | depression | 2 | 1,533 / 658 / 619 |
| Depression_Reddit | Reddit | depression | 2 | 1,004 / 431 / 406 |
| CLPsych15 | Twitter | depression | 2 | 457 / 197 / 300 |
| Dreaddit | Reddit | stress | 2 | 2,270 / 568 / 715 |
| UMD | Reddit | suicide risk | 3 | 993 / 249 / 490 |
| T-SID | Twitter | suicide/ideation | 2 | 3,072 / 768 / 960 |
| SAD | SMS-like | stress cause | multi | 5,548 / 617 / 685 |

**Results (Recall / F1, the paper's two reported metrics).**
- *Depression* (Table 2): MentalRoBERTa is best on eRisk T1 (**93.38 / 93.38** vs RoBERTa 92.25/92.25) and
  CLPsych (**70.33 / 69.71** vs RoBERTa 67.67/66.07); on Depression_Reddit RoBERTa (**95.07 / 95.11**)
  edges MentalBERT (94.58/94.62) and MentalRoBERTa (94.33/94.23).
- *Other disorders* (Table 3): MentalRoBERTa leads on T-SID (**88.96 / 89.01**), SWMH (**70.65 / 72.16**),
  SAD (**68.61 / 68.44**) and Dreaddit (**81.82 / 81.76**); on UMD-suicide **MentalBERT** has the top
  recall (**64.08**) but a low F1 (**58.26**), i.e. the gains are smallest and noisiest on the
  suicide-risk task.
- BioBERT / ClinicalBERT consistently **underperform** general RoBERTa here — biomedical-clinical
  adaptation does *not* transfer to social-media mental-health text; **social-media-domain** adaptation does.

**Honest size of the effect.** The domain-pretraining win is **real but small** — typically **~1–3 F1
points** over the RoBERTa baseline, and on several datasets vanilla RoBERTa ties or wins. It is a cheap
upgrade, not a step change.

### Parts directly useful for Pebble (specific)

1. **Corpus recipe Pebble can copy at lower cost.** The exact 7 subreddits (above) define a ready,
   reproducible in-domain MLM corpus for a NeoBERT domain-adaptive pass — note r/SuicideWatch and
   r/depression overlap the distribution of Pebble's CSSRS-Reddit safety data, so adaptation should help
   the `[CLS]` start *specifically on crisis text*.
2. **A concrete compute envelope.** 624k steps × bs16 × 4×V100 × ~8 days is the *upper bound* of what full
   re-pretraining costs; Pebble's pass should be far shorter (a few thousand steps of continued MLM on a
   250M model), so this de-risks the "is the MLM pass affordable?" question.
3. **The `[CLS]` → tanh-MLP fine-tune head + split learning rates (1e-5 encoder / 3e-5 head)** is exactly
   Pebble's architecture pattern and a sane default LR split for the staged-unfreeze schedule.
4. **A baseline matrix reviewers will cite.** The eight datasets with Recall/F1 per encoder give Pebble a
   published table to slot NeoBERT (and a NeoBERT+MLM-pass variant) into. The most load-bearing comparison
   numbers for Pebble: **MentalRoBERTa T-SID 88.96/89.01**, **SWMH 70.65/72.16**, **UMD-suicide
   MentalBERT 64.08 recall / 58.26 F1**, **CLPsych 70.33/69.71**.
5. **A settled negative result:** clinical/biomedical encoders (BioBERT, ClinicalBERT) lose to
   social-media adaptation — so Pebble should *not* reach for a clinical-notes backbone; the domain that
   matters is informal first-person social-media language.

### How each part helps Pebble succeed (concrete actions)

- **Run MentalRoBERTa as the demanded encoder baseline** under Pebble's own 3-head stack on CSSRS-Reddit
  severity + WASSA + the emotion head. This is the "why NeoBERT?" comparison reviewers will require;
  MentalRoBERTa is the strongest single competitor in Tables 2–3. *Payoff:* either NeoBERT (general, 250M,
  4K ctx) wins → justifies the backbone choice, or it loses on crisis text → motivates the MLM pass.
  Constraint: MentalBERT/RoBERTa weights are **CC-BY-NC (research-only)**, so this is a **research-arm**
  baseline; the deployed encoder must warm-start from an openly-licensed model.
- **Do one short domain-adaptive MLM pass on NeoBERT** over a corpus assembled from the same 7 subreddits
  (plus ESConv/WASSA text), then re-fine-tune the heads. *Expected payoff, calibrated by this paper:*
  **~1–3 F1 points**, concentrated on the suicide/severity tasks closest to r/SuicideWatch — material for
  a safety head fighting for recall ≥ 0.95, modest elsewhere. Treat it as an **ablation arm**, not a
  guaranteed win, because the paper shows the effect is small and sometimes negative.
- **Adopt the split-LR fine-tune (1e-5 / 3e-5)** as the default for Pebble's unfreeze stage rather than a
  single global LR.
- **Report on the suicide-relevant subset (UMD, T-SID).** The paper's weakest, noisiest gains are exactly
  on suicide-risk detection — a direct signal that Pebble's safety head is the hardest head and that
  recall there will not come "for free" from domain pretraining; it needs the dedicated objective + loss
  shaping flagged in Pillar 4.

### Child mental-health lens (Pebble serves children)

- **Population mismatch is the central caveat.** The entire corpus and all 8 benchmarks are **adult,
  self-selected Reddit/Twitter users** writing in long-form, idiomatic, often clinically-literate English
  (r/bipolar, r/mentalillness). Children/young users write shorter, simpler, less diagnostic-vocabulary
  text and disclose distress obliquely. So MentalBERT's learned `[CLS]` distribution — and any NeoBERT MLM
  pass built from the *same* subreddits — is **biased toward adult expression of crisis**, which can
  *lower* recall on the very population Pebble must protect.
- **Crisis-vocabulary risk.** r/SuicideWatch language is explicit; a child's crisis cue ("I don't want to
  go to school ever again", "I wish I could disappear") is softer. An encoder adapted only on adult
  explicit phrasing may under-respond to child phrasing — the worst possible failure mode given the
  recall ≥ 0.95 floor.
- **Mitigations:** (a) treat the MLM pass as adaptation *only*, and **calibrate/threshold the safety head
  on child-representative validation data**, not on adult Reddit; (b) keep the safety threshold tuned for
  recall on the child slice even at precision cost; (c) consider down-weighting or filtering the most
  adult-clinical subreddits (r/bipolar, r/mentalillness) from Pebble's MLM corpus in favor of r/depression
  / r/offmychest / general support text whose register is closer to a distressed young person.
- **Ethics caveats carried from the paper:** the authors explicitly state *"The model predictions are not
  psychiatric diagnoses"* and recommend directing users to a helpline — Pebble must inherit this:
  classifier output is a routing/safety signal, never a diagnosis shown to a child. They also flag
  *"bias, fairness, uncertainty, and interpretability issues"* in data and training; for a child product
  these are amplified, so the safety head's outputs need conservative thresholds and human-escalation
  paths, not autonomous action.

### Limitations & open questions for Pebble

- **The paper never measures recall under a constraint or a cost-sensitive objective** — it reports
  symmetric Recall/F1 with plain fine-tuning. It gives Pebble *no* guidance on hitting a recall floor;
  that remains Pebble's own contribution (Pillar 1 + Pillar 4).
- **Single-task only.** No multi-task / shared-`[CLS]` setup, no continuous-regression head, no loss
  balancing — so D1/D5 are genuinely absent; this paper informs only the *backbone* layer of Pebble.
- **No reported max-seq-length / mask-prob / pretraining optimizer** in the rendered text → if Pebble
  wants to replicate the MLM pass faithfully, these must be recovered from the released training config /
  HF repo, not the paper.
- **Effect size is small and dataset-dependent**; on UMD-suicide the F1 actually trails. Open question:
  *does a NeoBERT MLM pass help Pebble's CSSRS severity / safety head enough to justify the extra stage,
  or is the budget better spent on loss balancing and ordinal severity loss?* This paper suggests the MLM
  win alone is unlikely to be decisive — run it as an ablation, not a headline.
- **License blocks deployment.** MentalBERT/RoBERTa = CC-BY-NC; usable only to *baseline* against, not to
  ship. Pebble's deployed crisis-detection encoder cannot be MentalRoBERTa.
