# Paper 01 — FAIIR: Conversational AI Agent Assistant for Youth Mental Health Service Provision

## 1. Bibliographic info

**Title:** FAIIR: Building Toward A Conversational AI Agent Assistant for Youth Mental Health Service Provision

**Authors:** Stephen Obadinma (Queen's University / Vector Institute, corresponding), Alia Lachana, Maia Norman (Vector Institute / University of Waterloo), Jocelyn Rankin (Kids Help Phone), Joanna Yu (Vector Institute), Xiaodan Zhu (Queen's / Vector), Darren Mastropaolo (Kids Help Phone), Deval Pandya (Vector), Roxana Sultan (Vector / University of Toronto), Elham Dolatabadi (Vector / University of Toronto / York University). Lachana, Norman, Rankin, and Yu contributed equally.

**Affiliations:** Electrical and Computer Engineering at Queen's University, Vector Institute (Toronto), University of Waterloo, Kids Help Phone (KHP), University of Toronto, York University.

**Year / venue:** Preprint posted to arXiv on 28 May 2024 (v1); v4 dated 12 Feb 2025 (cs.AI). Published in *npj Digital Medicine* (2025) as article s41746-025-01647-6. DOI 10.48550/arXiv.2405.18553.

**Keywords (verbatim):** "conversational AI, mental health, crisis conversations, large language models, multi-label classification".

## 2. Problem motivation

The authors frame the work as a response to a sustained mismatch between demand for youth mental-health crisis support and the capacity of frontline staff. They cite that "one in seven young individuals aged 10 to 19 years old experience a mental health condition," that "suicide ranks as the fourth leading cause of death among 15 to 29 year olds," and that in Canada "one in five individuals will experience a mental illness by age 25." Despite "70% of mental illness starting during childhood or adolescence, only a fraction of young individuals are able to access appropriate care."

The operational context is Kids Help Phone (KHP), a Canadian not-for-profit. Since the launch of KHP's SMS service in 2018, "KHP has facilitated over 1 million Short Message Service (SMS) interactions, with a significant 51% increase observed during the COVID-19 pandemic in 2020." Crisis Responders (CRs) — a mix of paid professionals and trained volunteers — handle these conversations under heavy cognitive load while managing "emotionally stressed individuals in potentially life-critical situations." After each conversation, CRs must "complete post-conversation surveys to identify key issues such as suicide and abuse, further adding to their workload."

The role of FAIIR is **explicitly assistive and administrative, not clinical**. The tool "recommends potential issues from a list of 19 predefined tags" so that "appropriate resources can be provided and that active rescues and mandatory reporting can take place in critical situations." It does not generate therapeutic responses, dispense clinical advice, or replace the CR; it reduces the post-conversation tagging burden and surfaces priority cues. The authors frame this as a "human-in-the-loop design with active CR engagement for model refinement, consensus-building, and overall assessment."

## 3. Position in the literature

The authors place FAIIR at the intersection of three threads. First, **NLP for mental-health text classification** — they cite work on identifying signs of depression in social media (refs 15–17), suicidal intentions in social media posts (ref 18), and themes related to suicide and mental-health status from clinical notes (refs 19, 20). Second, **triage on crisis platforms** — they cite work on aiding "triage and reduce wait times on message-based suicide support platforms" (ref 21). Third, **long-document and dialogue-specific transformers** — Li et al. (ref 23) showing Longformer outperforming ClinicalBERT on long clinical documents; Dai et al. (ref 32) on long-document classification; Zhong et al. (ref 26, DialogLED) on dialogue-window denoising; and Ji et al. (ref 34) on RoBERTa/Longformer/XLNet pre-trained on mental-health corpora.

The claimed gap is that prior crisis-line NLP work has been small in scale, narrowly scoped (typically suicidality alone), and rarely validated prospectively with the actual responders who must consume the predictions. FAIIR addresses this by combining (a) one of the largest crisis conversational corpora ever used in the literature (~780k conversations), (b) a 19-tag operational taxonomy rather than a single binary, (c) explicit domain adaptation via MLM on the in-domain corpus, and (d) a two-phase evaluation with both a held-out retrospective set and a deployed silent test plus structured expert review.

## 4. Dataset deep dive

The development corpus comprises **703,975 anonymized, scrubbed, multi-turn SMS dialogues** between service users and CRs collected at KHP between **January 2018 and February 2023**. A second batch of **84,832 conversations from February to September 2023** was held out for prospective silent testing. The training data represented 340,512 unique service users and 7,937 CRs; the silent-testing data 57,031 unique service users and 2,038 CRs.

**Conversation length.** The average length was 913 tokens and the median 850. "The majority of conversations (53%) [are] between 500 and 1,500 tokens, and only a small number extending above 3,000 (0.7%)." A 2,000-token maximum input length was chosen, covering 94.4% of all conversations.

**Scrubbing.** "Identifiable information was scrubbed to ensure privacy compliance" by automatic replacement of names and locations with the placeholder `[scrubbed]`. The authors flag a known cost: "in many instances, complete phrases and sentences were scrubbed... This process therefore introduced some noise due to the unintentional removal of harmless words, like turkey."

**The 19-tag taxonomy.** Tags (each defined in Appendix A): *3rd Party, Abuse Emotional, Abuse Physical, Abuse Sexual, Anxiety/Stress, Bully, Depressed, Did Not Engage (DNE), Eating Body Image, Gender/Sexual Identity, Grief, Isolated, Other, Prank, Relationship, Self Harm, Substance Abuse, Suicide, Testing.* Conversations are **multi-label**: 53.73% have a single tag, and 46% have between 2 and 9 tags. The distribution is steeply imbalanced — the most frequent tag (Anxiety/Stress) appears in over 244,000 conversations, while the least frequent (Prank) appears in only ~2,800.

**Priority-flag system (Appendix D).** At the start of each conversation an algorithm owned by Crisis Text Line assigns *high / medium / low / no ground truth* risk. "Medium risk is assigned when a user expresses suicidal thoughts or self harm, and high risk is assigned when an individual is deemed to be an 'imminent risk', defined as having a combination of suicidal thoughts, a plan, access to means, and a 0–48 hour timeline." Triggering on any of 56 English or 73 French keywords in the first message escalates priority. In practice 87% of conversations are medium-risk, ~13% high-risk, and ~0.0001% low-risk.

**Label noise.** Critically, "this labelling process is carried out by CRs at their own discretion, and according to their training. Due to limited resources and large volumes of service user inquiries, issue tags typically do not undergo additional review." The authors return to this single-annotator-per-conversation property repeatedly as the largest source of irreducible noise.

**Demographics.** An optional post-conversation survey is completed by ~17% of service users (n=59,603 of 340,512). Among respondents, the modal subgroup is female (75.6%), heterosexual (55.5%), of European ancestry (78.1%); 67.3% of identity respondents reported an Invisible Disability. The authors caution that "results do not fully represent the distribution or demographic features of service users overall."

**Ethics.** No external IRB number is reported. KHP's "Ethics Statement" describes adherence to KHP's privacy policy and Canadian privacy regulations, removal of direct identifiers, in-infrastructure storage, and a "consent notice for research and rigorous data minimization." Code is at a private GitHub repository (`KidsHelpPhone/AI-ML`) available on request; data is not openly shared "due to reasons of sensitivity."

## 5. Method

**Task framing.** Multi-label classification: each of 19 tags is an independent positive/negative head atop a shared encoder, trained with binary cross-entropy.

**Step 1: encoder comparison.** Four pre-trained transformers were fine-tuned on a 50,000-conversation random subset with a 60/20/20 stratified split:

| Model | Type | Params | Why chosen |
|---|---|---|---|
| Longformer | encoder-only | 149M | sparse-attention encoder built for long sequences |
| Conversational BERT | encoder-only | 110M | pre-trained on conversational corpora |
| DialogLED | encoder-decoder | 139M | dialogue-window-denoised long-dialogue model |
| MVP (Multi-task superVised Pre-training) | encoder-decoder | 406M | strong multi-task generative pre-training |

Encoder-only models attached a classification head on the `[CLS]` token; DialogLED used `[EOS]` and MVP used the first token. All were fine-tuned on 4× NVIDIA A10 GPUs (24 GB VRAM, 16 CPU cores), effective batch size 16, LR swept 1e-5 to 3e-5. Longformer was capped at 2,048 tokens; the others used their default 512-token cap. Optimal epochs: BERT 2, DialogLED 3, Longformer 5, MVP 2.

**Table B2 results:** Longformer accuracy 0.938 / exact-accuracy 0.336 / sample-avg P 0.660 / R 0.530 / F1 0.560; BERT 0.936 / 0.339 / 0.650 / 0.540 / 0.560; DialogLED 0.922 / 0.206 / 0.430 / 0.320 / 0.350; MVP 0.351 / 0.000 / 0.200 / 0.820 / 0.310. Longformer was selected as the backbone for its parity with BERT plus its long-context handling.

**MLM continued pre-training.** Each Longformer was domain-adapted via masked language modelling on the full training corpus: "15% of tokens per conversation," one epoch, max sequence length 1,500, AdamW optimizer, linear scheduler with 500 warm-up steps, gradient-accumulated effective batch size 64. This phase required ~24 hours.

**Step 2: final fine-tuning of the Longformer ensemble.** The deployed FAIIR backend is an ensemble of three Longformers, each with slightly different initialization and fine-tuning settings. Fine-tuning was done on a 60/20/20 label-balanced split of 563,180 conversations (422,385 train / 140,795 validation / 140,795 retrospective test). Per ensemble member: max 3 epochs, batch size 16 via gradient accumulation, LR 2e-5, BCE loss, AdamW, linear scheduler with warm-up over the first 20% of training steps. **Oversampling of conversations with rarer issue tags was applied to two of the three ensemble members** to combat class imbalance; the third was trained on the natural distribution to preserve calibration.

**Priority-flag conditioning.** Per domain-expert recommendation the conversation was prefixed with a literal sentence: `"This conversation is of <<X>> priority"` where X is *high*, *medium*, or *low*. This injects the rule-based triage signal into the input stream, so the encoder sees it as ordinary text.

**Threshold tuning.** Step 1 used a uniform 0.25 cut-off across all 19 sigmoid heads after sweeping 0.25–0.50 on validation. For the deployed (silent-testing) configuration the authors adopted a per-tag policy: 0.4 for the three highest-frequency classes (*Anxiety/Stress*, *Depressed*, *Relationship*), 0.3 for the next two (*Suicide*, *Isolated*), and 0.2 for the remaining 14 tags. Rationale: "we adjusted the threshold to reduce its frequency of outputting the most common tags while lowering the threshold for rare tags."

## 6. Experiments and results

**Retrospective test (n=140,795).** AUROC averaged 0.94 across the 19 tags, with most tags above 0.90 and the lowest at 0.74 (*Other*). At threshold 0.25 the sample-averaged scores were **precision 0.58, recall 0.81, F1 0.64, accuracy 0.94**. At threshold 0.50, precision climbed to ~0.61 but sample-averaged recall fell to ~0.60 (per Figure 2 left). The authors explicitly accept the precision/recall tradeoff: "this trade-off between recall and precision is acceptable within this context, as it prioritizes capturing critical issues."

**Per-tag performance (threshold 0.25, retrospective).** Strong: *3rd Party* F1 0.76 (P 0.64 / R 0.95), *Anxiety/Stress* F1 0.69, *Depressed* F1 0.75, *Relationship* F1 0.73, *Self Harm* F1 0.69, *Suicide* F1 0.73, *Gender/Sexual Identity* F1 0.67, *Eating Body Image* F1 0.64. Weak: *Other* F1 0.35, *Prank* F1 0.45, *Abuse Emotional* F1 0.46, *Abuse Physical* F1 0.47, *Isolated* F1 0.56, *Testing* F1 0.53. AUROC for *Suicide* was 0.94, *Self Harm* 0.97, *Abuse Sexual* 0.98.

**Prospective silent test (n=84,832, Feb–Sep 2023).** "Sample averaged precision, recall, and F1 scores are 0.57, 0.79, and 0.62, respectively, for a threshold of 0.25, compared to 0.58, 0.81, and 0.64 for the retrospective values, indicating a drop of less than 2%." AUROC distribution was similar (most >0.90, lowest 0.73). The authors attribute the gap to natural drift — the silent set "naturally includes more up-to-date topics and events of 2023 such as natural disasters and political crises," and the DNE tag became proportionally more common.

**Demographic stratification (Table 2).** Across 27 subgroups in four categories (Gender / Orientation / Identity / Ethnicity), F1 was tightly clustered. Standard deviations of F1 by category: Gender ±0.023, Orientation ±0.010, Identity ±0.018, Ethnicity ±0.024. A one-sample t-test (p < 0.001) reported "no significant difference between the F1-scores of individual demographic subgroups and the overall performance." Group F1 examples: Male 0.64, Female 0.65, Trans Male 0.64, Trans Female 0.59 (n=32), Non-binary 0.63, Heterosexual 0.65, Gay or Lesbian 0.66, Bisexual 0.64, European Ancestry 0.65, African or Caribbean 0.61, Indigenous 0.65, East/South-East Asian 0.63.

**Priority-stratified performance (Appendix D, Table D3).** At threshold 0.25, weighted-avg P/R/F1 for Medium-priority was 0.54/0.80/0.64 and for High-priority 0.56/0.81/0.65 — essentially flat across risk levels, which the authors frame as evidence of low priority-flag bias.

**Calibration / reliability.** Not reported — no reliability diagrams, ECE numbers, or temperature-scaling experiments.

## 7. Expert validation study

The authors recruited **12 trained CRs** to review **40 challenging conversations**, yielding **240 annotations** (six per conversation). Selection was deliberately hard: 20 of the 40 were drawn from the test set with 4+ assigned tags; the other 20 mixed sparsely-tagged conversations with manually picked tag-coverage cases, deliberately ambiguous long conversations with only 1–2 tags, and suspected-mislabel cases. The methodology splits annotators per conversation: **three CRs do an "open review"** (FAIIR's predictions shown to them as a reference), and the **other three do a "blind review"** (no FAIIR exposure, classifying primary vs. secondary tags from scratch).

Five consensus criteria were defined for the blind setting: (1) FA: 1° — full agreement on primary tags; (2) PA: 1° Maj. — majority agreement on primary tags overlaps FAIIR; (3) PA: 1°+2° Maj. — majority agreement on primary and secondary tags overlaps FAIIR; (4) FA: 1° ≥ 1 — at least one annotator's primary tag matches FAIIR; (5) FA: 1°+2° ≥ 1 — at least one annotator's primary or secondary tag matches FAIIR.

**Headline result:** averaged across the 40 conversations, blind reviewers agreed with FAIIR on **90.9% of tags** (range 33%–100%); FAIIR produced 165 tags and by majority vote missed only 13. Across the five consensus criteria, FAIIR-vs-expert averaged precision 0.62 ± 0.22, recall 0.82 ± 0.13, F1 0.64 ± 0.11 — all significantly above original-label-vs-expert (P 0.52 ± 0.18, R 0.56 ± 0.08, F1 0.47 ± 0.07; unpaired t-test p < 0.001). In other words, **the model agreed with experts more than the original CR labels did**, which the authors take as evidence that operational labels are noisier than the trained model. After incorporating the blind responses to retune the threshold, precision rose ~4% (to 0.66 ± 0.20) at a recall cost (to 0.76 ± 0.14). Strong agreement appeared on *Anxiety/Stress*, *Bully*, *Relationship*, *3rd Party*, *Suicide*, *Abuse Emotional*; more disagreement appeared on *Grief*, *Self Harm*, *Abuse Physical*, *Other*, *Eating Body Image*.

## 8. Ablations / failure modes

The paper does not run a formal ablation grid, but several axes are characterised. **Encoder ablation** (Table B2): the encoder-decoder MVP and DialogLED collapsed on this multi-label task (F1 0.31 and 0.35); Longformer and BERT were comparable at F1 0.56, with Longformer winning on long-context handling. **Threshold sensitivity** is reported as side-by-side rows (0.25, 0.5, updated) in Table 1 — moving from 0.25 to 0.5 raises precision but cuts the rarer tags' recall sharply (e.g., *Abuse Physical* recall drops from 0.70 to 0.50; *Prank* recall from 0.66 to 0.55). **Class imbalance** was handled with oversampling on two ensemble members plus re-weighting; the persistent weak performers (*Other*, *Prank*, *Abuse Physical*, *Isolated*, *Testing*) are attributed to either rarity or semantic vagueness — e.g., *Other* "encompass[es] anything outside the scope of the set 19" and *Isolated* "can apply to a broad spectrum of conversations, but its relevance may be selectively applied." The strongest tags are the operationally important ones (*Suicide*, *Self Harm*, *Depressed*, *Anxiety/Stress*, *Relationship*) — a desirable failure profile for a safety-supporting tool.

## 9. Authors' stated limitations

The Discussion and Limitations identify five recurring concerns. (1) **Closed taxonomy:** "Our study's primary limitation is its reliance on a predefined set of 19 issue tags... This limitation restricts the model's ability to extract information beyond the predefined list" — CRs want dynamic, youth-centred tags that the current model cannot produce. (2) **Single-annotator label noise:** "we noted potential biases in the original labelling process, as each conversation was labelled by a single annotator without subsequent review... a large annotated dataset for a supervised task with multiple annotators per conversation would be optimal." (3) **Rare-tag underperformance:** the imbalance "explains the relatively poorer performance of FAIIR across less-represented issue tags... Tags like Prank and Abuse, Physical also suffered in performance due to their rarity." (4) **Scrubbing noise and conversational noise:** "the varying quality of conversations, including differences in language use, grammar, and the presence of noise such as typos or slang... required extensive pre-processing efforts, which introduced subjectivity and potential bias into the data." (5) **Explainability not yet validated:** the natural-keyword pipeline is presented as exploratory — "the reliability and meaningfulness of these natural keywords require further rigorous assessment." Deployment risk is acknowledged implicitly: silent testing is presented precisely as the bridge between offline metrics and real-time use, but no full deployment evaluation is reported. Ensemble inference cost is mentioned only indirectly through the resource-cost discussion of the encoder-decoder baselines.

## 10. Relevance to Pebble emotion classifier

FAIIR is the closest published analogue to Pebble's emotion classifier in problem shape — both are multi-output mental-health text classifiers whose outputs feed downstream safety-critical pathways. Several specific contrasts and lessons apply.

- **Shared problem class.** Both are multi-output classifiers over mental-health text where false negatives on rare-but-critical signals (suicidality, self-harm, abuse for FAIIR; the analogous high-distress emotion dimensions for Pebble) are costlier than false positives. Both teams therefore consciously bias toward recall.
- **Label source contrast.** FAIIR trains on **single-annotator operational labels** (each conversation labeled by one CR at their own discretion, no second review) and treats that noise as a structural limitation. Pebble trains on **LLM silver labels**, a different but parallel noise source — systematic, not human-individual, and amenable to programmatic re-labelling. The mitigation strategies diverge: FAIIR enriched its ground truth with a small expert consensus study; Pebble can mitigate by sampling multiple LLM judges or re-labelling on disagreement.
- **Head structure.** FAIIR is 19 independent sigmoid heads trained with BCE — a pure multi-label categorical setup. Pebble's classifier head is heterogeneous (regression + softmax + BCE across dimensions). FAIIR's clean per-head threshold policy doesn't translate one-to-one, but the **per-output threshold tuning principle** is directly applicable to Pebble's sigmoid/BCE heads.
- **Safety handling.** FAIIR's safety-bias mechanism is purely threshold-based — three tiers (0.4 / 0.3 / 0.2) selected by tag frequency and operational importance. Pebble plans a heavier intervention: high positive-class loss weighting and an explicit recall ≥ 0.95 floor on critical dimensions. Pebble's plan is stricter but is well-supported by FAIIR's empirical demonstration that "the model is highly effective at identifying relevant tags, but may occasionally also identify irrelevant issues in conversation" is an acceptable trade for a triage-support tool.
- **Transferable techniques for Pebble.** (a) **Priority-as-prefix conditioning** — FAIIR injects the rule-based priority flag as a literal sentence at the start of the input rather than as a separate feature; Pebble can analogously inject any meta-signal (severity tier, session position, source) as a textual prefix without modifying the head architecture. (b) **MLM continued pre-training on the in-domain corpus** before task fine-tuning — FAIIR ran 1 epoch of 15% masking on the full corpus and credits it for both performance gains and "addressing label biases." For Pebble's emotion-conversation corpus, this is a cheap, high-leverage step. (c) **Per-dimension threshold tuning by class frequency** — FAIIR's 0.4/0.3/0.2 split is a simple, defensible policy that beats a single global threshold. (d) **Small ensemble for variance reduction with at least one rare-class-oversampled member** — FAIIR's 3-Longformer ensemble (two with oversampling, one without) is a practical pattern for capturing both calibrated common-class behaviour and recall on rare classes. (e) **Structured expert consensus on a small hard set** as a substitute for full re-annotation — Pebble cannot re-label its silver corpus, but a 40-conversation × 6-rater expert consensus on a deliberately hard sample is a tractable validation gate that meaningfully changed FAIIR's threshold policy.

## 11. Recommended citation use

In a Pebble paper, FAIIR can be cited to support the following specific claims:

- **Scale and operational relevance of crisis-line NLP.** "FAIIR was developed on 703,975 anonymized text-based crisis support conversations exchanged... from January 2018 to February 2023" (Methods §5.2). Use this to establish that production-scale, in-domain mental-health classifiers are now a published reality, not speculation.
- **Demand–capacity gap motivating ML assistance.** "Since the launch of its text service in 2018, KHP has facilitated over 1 million Short Message Service (SMS) interactions, with a significant 51% increase observed during the COVID-19 pandemic in 2020" (Introduction). Use to motivate Pebble's responder-augmentation framing.
- **Achievable performance ceiling on noisy operational labels.** "FAIIR achieves an average AUC ROC of 94%, a sample average F1-score of 64%, and a sample average recall score of 81% on the retrospective test set" (Abstract; Results §2.1). Use as a benchmark for what is realistic on noisy mental-health corpora.
- **Robustness of in-domain transformer classifiers under temporal drift.** "Less than a 2% drop in sample average precision, recall and F1-score" between retrospective and 8-month prospective silent test (Discussion §3). Cite to justify prospective evaluation as feasible and informative.
- **Demographic-equity baseline.** F1 standard deviation across 27 subgroups remained < 0.025 (Results §2.1, Table 2). Cite as evidence that domain-adapted transformer classifiers can be approximately fair across major demographic strata, while still warranting subgroup reporting.
- **Single-annotator noise as a structural limitation, not a model bug.** "Expert agreement with FAIIR surpassed their agreement with the original labels" (Abstract; Discussion §3). Cite to justify Pebble's planned multi-judge silver-labeling strategy.
- **Per-class threshold tuning as a deployable safety lever.** Threshold 0.4 for most-frequent tags, 0.3 for next-frequent, 0.2 for the long tail (Methods §5.4). Cite as precedent for Pebble's per-dimension threshold/recall-floor policy.
- **Domain-adaptive MLM as a measurable contributor.** "Domain adaptation through self-supervised learning significantly enhances tool performance, especially in supervised tasks and when addressing label biases" (Discussion §3). Cite to justify a Pebble MLM continued-pre-training step.

Items that should NOT be cited from this paper (because they are not reported): calibration / ECE numbers, formal ablation isolating the priority-flag prefix, formal ablation isolating MLM contribution, per-judge agreement statistics beyond the headline 90.9%, latency or inference-cost numbers for the deployed ensemble, and any post-deployment outcome data — silent testing is the latest stage reported.

## Deep research — full-PDF read (2026-06-10)

> Read against the published npj Digital Medicine version (s41746-025-01647-6); the local PDF is
> `pdfs/01-faiir.pdf` (arXiv:2405.18553). ar5iv's HTML conversion of this paper is broken
> ("Fatal error"), so quotes below come from the npj full text. This section only adds what
> §§1–11 above do not already cover; cross-references point back to those sections.

### What the full paper adds beyond the existing analysis

- **Governance route: no REB/IRB at all.** "This publication was the result of a quality
  improvement initiative at Kids Help Phone, and as a result, no REB approval was sought or
  obtained." §4 above says "No external IRB number is reported" — the truth is stronger: the
  *entire* 780K-conversation youth-crisis study ran under an internal quality-improvement
  framing plus KHP's privacy policy (consent notice, data minimization, in-infrastructure
  controlled-access storage). That is a deliberate governance pattern, not an omission.
- **Expert-validation sampling is half-random, half-adversarial.** The 40 conversations split
  into 20 *randomly selected* among those with ≥4 tags (diverse, hard) and 20 *purposefully
  curated* — <3 tags, deliberately ambiguous, or suspected mislabels — chosen so all 19 tags are
  covered. Six assessments per conversation: 3 open (FAIIR predictions visible, rating
  helpfulness) and 3 blind (tagging from scratch). The post-study threshold retune bought a
  "4% increase" in precision (0.62→0.66) at a recall cost (0.82→0.76).
- **Priority-flag provenance.** The triage algorithm is *owned by Crisis Text Line*, not KHP, and
  fires on the user's *first message only*: "the presence of any 56 English or 73 French words in
  an initial message from a user leads to their automatic triage to a higher priority level."
  High risk = suicidal thoughts + plan + access to means + 0–48h timeline; medium = suicidal
  thoughts or self-harm. Distribution: 87% medium / 13% high / ~0.0001% low.
- **Explainability = layer-integrated gradients.** Keywords are extracted per tag via
  layer-integrated gradients, filtered against stop-words/punctuation/special tokens and a
  predefined common-word list ("User", "Hello"). Suicide-tag keywords: *happy, sad, mood,
  anxiety, scared, pain, plan, home, school, friend*; *assault* indexes Abuse-Sexual while
  *mom/dad* skew Abuse-Physical. Authors concede reliability "require[s] further rigorous
  assessment" and report **no CR feedback** on keyword usefulness.
- **Ensemble aggregation is unspecified.** The 3-Longformer ensemble's combination rule (vote vs.
  probability averaging) is never stated — a real gap if Pebble wants to copy the recipe; only
  the member-level differences are given (2 of 3 oversample rare tags; all share the same
  15%-mask, 1-epoch MLM pass).
- **Youth language is acknowledged but never analyzed.** The only treatment is generic noise:
  "varying quality of conversations, including differences in language use, grammar, and the
  presence of noise such as typos or slang." No analysis of how 10–19-year-olds actually voice
  distress (indirectness, emoji, code-switching, message rhythm). On the *largest youth crisis
  corpus in the literature*, that analysis simply doesn't exist yet.

### Parts directly useful for Pebble

1. **The two-stage validation template** (silent test → 40-conversation × 6-rater consensus with
   open/blind split and five pre-registered consensus criteria) — the *only* published,
   youth-crisis-specific protocol for validating a classifier against experts when ground-truth
   labels are noisy.
2. **The escalation-design pattern**: a cheap, auditable keyword/rule layer that *escalates* (never
   de-escalates) + the model layer underneath + injecting the rule verdict as a text prefix
   (`"This conversation is of <<X>> priority"`). Three independent safety layers, each simple.
3. **The governance pattern for minors' data**: quality-improvement framing, consent notice,
   automated scrubbing to `[scrubbed]`, controlled-access in-house storage, no open release —
   with the known cost that over-scrubbing deletes harmless words and adds label noise.
4. **The half-random/half-adversarial eval-set construction** (20 hard-random + 20 curated
   ambiguous/suspected-mislabel covering every class).
5. **The recall-first threshold policy with a published payoff curve**: per-class thresholds by
   frequency tier (0.4/0.3/0.2), and the measured +4% precision / −6% recall consequence of
   tightening after expert feedback.

### How each part helps Pebble succeed

- **Validation (1) → Pebble's eval plan.** Pebble's silver labels are exactly the "noisy
  single-source ground truth" FAIIR faced. Copy the protocol: before any deployment claim, run a
  ~40-item expert consensus on a half-random/half-adversarial slice of Pebble's own conversations,
  3 blind + 3 open raters, and report model-vs-expert agreement *next to* silver-vs-expert
  agreement. FAIIR's headline (model agreed with experts *more than the original labels did*,
  0.64 vs 0.47 F1, p<0.001) is the exact argument Pebble will need when a reviewer says "your
  Gemini labels are noisy": noisy labels can still train a model that out-agrees its own
  supervision. Concretely: add an `eval/expert_consensus/` protocol doc + a 40-item annotation
  sheet before the first deployed checkpoint.
- **Escalation pattern (2) → Pebble's safety head is not alone.** Don't let the recall ≥ 0.95
  floor live only in the learned head. Add a FAIIR-style first-message keyword tripwire (child
  vocabulary, both explicit and coded terms) that can only *raise* the risk tier, and feed the
  tier back into the encoder as a text prefix — zero architecture change, and FAIIR's Table D3
  (flat P/R across priority strata) shows the prefix doesn't distort per-class performance. The
  learned head then only has to beat the keyword layer, not replace it.
- **Governance (3) → Pebble's deployment story.** Pebble cannot collect children's chat data under
  an open-data regime. FAIIR proves the workable shape: in-infrastructure storage, scrubbing,
  consent notice, research access on request. Adopt it early (data handling section of the paper
  + repo policy), and budget for the scrubbing-noise cost FAIIR documents ("turkey" deletions →
  train-time noise).
- **Eval-set construction (4) → Pebble's test split.** Pebble's C-SSRS test set is tiny (~100
  rows); a purely random slice will contain almost no high-severity cases. Build the held-out
  eval the FAIIR way: half random-hard, half curated to cover every severity level and suspected
  silver-label errors — that's what made FAIIR's 40 conversations informative enough to change
  the production threshold policy.
- **Threshold policy (5) → the safety/emotion head cutoffs.** Tune per-head, per-frequency-tier
  thresholds on validation, and *publish the trade* (FAIIR: +4% P for −6% R). For Pebble the rule
  inverts on the safety head: fix recall at 0.95 and let precision float; FAIIR's measured curve
  is the citation that this trade is operationally acceptable in youth crisis support.

### Child mental-health lens

This is the one paper in the whole related-work set whose data *is* children in crisis
(KHP serves ~10–19-year-olds; 1M+ SMS interactions, +51% during COVID). Lessons specific to
Pebble's mission:

- **Children's crisis signal is recoverable at scale.** Suicide AUROC 0.94, Self-Harm 0.97,
  Abuse-Sexual 0.98 on real youth SMS — not social-media proxies. This is the existence proof
  that Pebble's safety head targets are achievable on child-register text, where every other
  paper in the set (C-SSRS, MentalBERT, WASSA) is adult Reddit/essay data.
- **But the model never decides.** FAIIR's role boundary — post-conversation tagging support and
  cue-surfacing, with "active rescues and mandatory reporting" always executed by a trained human
  — is the safety architecture Pebble should copy verbatim: Pebble's heads inform a Decision
  Engine; escalation to a human/caregiver pathway is a product invariant, not a model output.
- **Rule layer first, model second.** For imminent-risk detection KHP does *not* trust the
  learned model: a keyword list on the first message handles escalation, deliberately
  over-triggering (87% of all conversations sit at medium). For minors, dumb-but-auditable
  beats clever-but-opaque at the highest-stakes tier; Pebble's recall floor should likewise be
  backstopped by rules a clinician can read.
- **Single-annotator noise is the norm in child services.** Overworked CRs tag alone, unreviewed —
  and the expert study showed those labels are *worse* than the model. Pebble's plan to use
  multiple LLM judges + a human consensus slice is the right correction, and FAIIR is the
  citation for why it's necessary.
- **The open gap Pebble can own: youth-register language.** FAIIR processes youth text but never
  characterizes it; its explainability keywords (*plan, home, school, friend* for suicide) hint
  that children's risk markers are *contextual-relational*, not clinical vocabulary. Pebble's
  child-register calibration slice and any analysis of indirect/coded child distress language
  would be a genuine contribution no one — including FAIIR — has published.
- **Ethics asymmetry to respect.** FAIIR ran no REB because it stayed an internal
  quality-improvement tool on already-collected service data. Pebble, as a new child-facing
  product generating synthetic crisis text (Gemini silver labels) and making live decisions,
  cannot claim the same exemption — plan for genuine ethics review, age-appropriate consent, and
  guardian-notification policy from the start.

### Limitations & open questions for Pebble

- **No calibration anywhere** (no ECE/reliability curves) — yet Pebble's Decision Engine consumes
  probabilities, not tags. Pebble must add the calibration evaluation FAIIR skipped.
- **No MLM or prefix ablation** — FAIIR *claims* domain-adaptive MLM "significantly enhances"
  performance but never isolates it. Pebble's planned MLM-pass ablation on NeoBERT would be the
  first clean measurement in this domain.
- **Ensemble aggregation unspecified** — if Pebble copies the 3-member/2-oversampled recipe, the
  combination rule (mean probability vs. majority vote) must be chosen and reported; FAIIR gives
  no guidance.
- **Conversation-level only.** FAIIR tags whole conversations post-hoc; Pebble must score
  *turn-level, mid-conversation* — FAIIR's numbers are not directly comparable bars, only an
  upper-bound analogue (its 2,000-token cap covering 94.4% of dialogues is, however, direct
  evidence NeoBERT's 4K window is ample for this domain).
- **Access is gated.** Code private (`KidsHelpPhone/AI-ML`, on request), data closed. Open
  question worth one email: whether KHP would share the 19-tag taxonomy definitions and the
  EN/FR escalation keyword lists — either would be directly reusable for Pebble's rule layer.
- **Population mismatch at the margin.** KHP texters are self-selecting help-seekers, modal
  respondent female/European-ancestry, 67.3% invisible disability among identity respondents —
  Pebble's companion-app users (younger, not yet help-seeking) may express risk earlier and more
  obliquely than this corpus shows.
