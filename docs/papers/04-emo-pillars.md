# Paper 04 — Emo Pillars: Knowledge Distillation for Fine-Grained Emotion Classification

## 1. Bibliographic info

**Title:** *Emo Pillars: Knowledge Distillation to Support Fine-Grained Context-Aware and Context-Less Emotion Classification*
**Author:** Alexander Shvets (single-author paper)
**Affiliations:** NLP Group, Universitat Pompeu Fabra (UPF), Barcelona, Spain; and Language Technologies Unit, Barcelona Supercomputing Center (BSC), Spain.
**Venue:** *Findings of the Association for Computational Linguistics: ACL 2025*, Vienna, Austria, pp. 174–191. ACL Anthology ID `2025.findings-acl.10`; DOI `10.18653/v1/2025.findings-acl.10`. arXiv preprint `2504.16856` (submitted 23 April 2025; license CC BY 4.0).
**Code / data / model releases:**
- Code: `https://github.com/alex-shvets/EmoPillars`
- Dataset: `https://huggingface.co/datasets/alex-shvets/EmoPillars`
- Model collection: `https://huggingface.co/collections/alex-shvets/EmoPillars-67ec9694541e0bc69d62861f`

The paper is fully open: synthetic data, training scripts, and the trained encoder family ("π-RoBERTa", "π-CRoBERTa", and downstream-tuned variants) are all released.

## 2. Problem motivation

Fine-grained emotion classification — the task of mapping a textual utterance to a label in a taxonomy substantially larger than the classical Ekman/Plutchik 6–8 — is severely data-bound. The canonical benchmark, GoEmotions (Demszky et al., 2020), provides ~58K Reddit comments labelled across 28 categories, but its single-domain (Reddit), single-genre (short comments, no preceding context), and partially noisy annotation profile imposes a hard ceiling on what classifiers can learn. Reproducing GoEmotions-style labelling at scale requires multiple human annotators per item across all 28 categories, which scales poorly: cost grows roughly linearly with corpus size and with taxonomy granularity, and inter-annotator agreement collapses as labels become semantically adjacent (e.g., *annoyance* vs *anger*, *nervousness* vs *fear*, *admiration* vs *approval*). Shvets explicitly notes that the GoEmotions human-eval Cohen's κ baseline is only 0.293.

A second, often-overlooked gap is **narrative context**. Most public emotion corpora (GoEmotions, ISEAR, EmoContext utterance-only mode) score an utterance in isolation, even though the same surface sentence — "Oh, that's just great." — flips polarity depending on the situation that preceded it. The author argues this leads to two failure modes in deployed classifiers: (a) models hallucinate emotions when context-free, and (b) when context is appended at inference time, the model either ignores it or pools emotions from the entire concatenated input, unable to distinguish "what the speaker feels" from "what the situation is". The paper sets out to close both gaps simultaneously by *synthesising* a large, diverse, context-annotated corpus rather than annotating one by hand.

## 3. Position in the literature

Emo Pillars sits at the intersection of three lines of work:

1. **Fine-grained emotion taxonomies.** GoEmotions (Demszky et al., 2020) defines the 28-class taxonomy reused here. Coarse-grained baselines include ISEAR (Scherer & Wallbott, 1994; 7 self-report categories), IEMOCAP (Busso et al., 2008; multimodal dyadic dialogue, 4-/6-way), and EmoContext (Chatterjee et al., 2019; SemEval-2019 dialogue, 4 classes including "others").
2. **LLM-as-teacher distillation.** The closest methodological precedent is Hsieh et al. 2023 ("Distilling Step-by-Step") and the broader family of works that elicit rationales or labels from a large generative model and train a smaller student on them. The paper also cites concurrent findings (Wang et al., 2024; Chochlakis et al., 2024) showing that LLMs *as classifiers* over-predict, hallucinate, and over-interpret on fine-grained emotion taxonomies — motivating distillation into an encoder rather than direct LLM inference.
3. **Context-aware emotion modelling.** Prior work on conversational emotion recognition (e.g., DialogueRNN, COSMIC, and the CORECT multimodal architecture of Nguyen 2023 used here for IEMOCAP) has shown that surrounding turns matter, but most rely on real, sparse dialogue data. Emo Pillars is, to the author's knowledge, the first to *synthetically* manufacture (context, utterance, multi-label) triples at hundreds-of-thousands scale.

## 4. Knowledge-distillation framing

Knowledge distillation classically takes two forms: **soft-logit distillation** (the student minimises KL divergence to the teacher's full output distribution, à la Hinton et al. 2015) and **hard-label distillation** (the teacher's argmax is treated as a pseudo-label and the student trains with standard cross-entropy).

Emo Pillars uses neither pure form. Instead it does what is best described as **implicit hard-label distillation with teacher-generated multi-label sigmoid targets**. The teacher (Mistral-7B-Instruct-v0.2) is *prompted* to emit, for each utterance, a ranked list of the top-5 emotions with an "expressiveness level from 0 to 1" in 0.1 steps. These pseudo-probabilities are then **thresholded at 0.3**: every emotion above the cutoff becomes a positive label, everything else a negative. The student is trained with **binary cross-entropy** against this filtered multi-hot vector. There is no KL term, no temperature, no logit matching.

The design implication is important: the teacher is not asked to be a calibrated probabilistic classifier (LLMs are notoriously bad at that). It is asked to *enumerate plausible co-occurring emotions*, and the threshold cleanly separates "really present" from "weakly suggested". This is a pragmatic choice that sidesteps the well-known failure of LLM logit calibration while still extracting the multi-label structure that makes the 28-class taxonomy meaningful.

## 5. Teacher LLM setup

- **Model:** Mistral-7B-Instruct-v0.2.
- **Decoding:** greedy decoding with `repetition_penalty = 1.03`.
- **`max_new_tokens` per pipeline stage:** actor extraction = 300; utterance generation = 500; soft labeling = 100; context generation = 300; context cleaning = 300; utterance rewriting = 300.
- **Taxonomy injection:** the 28 GoEmotions categories — *admiration, amusement, anger, annoyance, approval, caring, confusion, curiosity, desire, disappointment, disapproval, disgust, embarrassment, excitement, fear, gratitude, grief, joy, love, nervousness, optimism, pride, realization, relief, remorse, sadness, surprise, neutral* — are injected as text together with their original GoEmotions definitions.
- **Hallucinated-label remapping:** when the LLM emits an off-taxonomy label, a small hand-built dictionary remaps frequent offenders (e.g., *anxiety → nervousness*, *indignation → anger*, *hope → optimism*); unmapped labels are discarded.
- **Compute budget:** ~700K total inferences consumed roughly **450 H100 GPU hours** (split ~200h for context-less generation and ~200h for context-full generation, plus auxiliary stages).

## 6. Synthetic data pipeline — full detail

**Seed corpus.** WikiPlots, a public collection of 113K English-Wikipedia plot synopses of books, films and TV shows. Only **2,000 plots** are used for the main run; the rest of WikiPlots is held in reserve to demonstrate scalability.

**Six stages**, each a separate LLM call with a dedicated prompt (Table 15 of the paper):

1. **Actor extraction** — "Who are the characters in the plot? Try to list all of them, one per line." Yields ~15 actors per plot (std ≈ 9.44).
2. **Utterance generation** — "Generate 8 possible utterances of this actor thinking aloud that express 8 various non-neutral emotions… Additionally, generate 2 neutral utterances." This produces ~10 utterances per actor.
3. **Soft labelling** — "Select from the list above the top 5 emotions the utterance expresses. List them with an expressiveness level from 0 to 1." This yields the multi-label soft targets that are later thresholded.
4. **Context generation** — "Explain why the actor was thinking aloud this way… only until the moment of the utterance. Be as concise as possible." Produces a situation summary that stops just before the utterance.
5. **Context cleaning** — "Remove clauses or entire sentences from the context that explicitly discuss the emotions." Preserves ~92% string similarity (µ = 0.92, σ = 0.08), i.e., the cleaning is mild and surgical.
6. **Utterance rewriting** — "Rewrite the utterance so that the emotions are ambiguous without the summary." Result: ~78% substring overlap with the original (µ = 0.78, σ = 0.15) — emotionally dampened but lexically close.

**Yield arithmetic.** 2,000 plots × ~15 actors × ~10 utterances ≈ 300K **context-less** examples (the "Orig" set) plus ~100K **context-full** examples (the union of **COrig** = original utterance + context, and **CRewr** = rewritten utterance + cleaned context). Filtering at expressiveness ≥ 0.3 keeps 1–5 labels per example (mean = 3.17, std = 0.97). Neutral comprises 2.7% of raw labels and survives in 9% of post-filter examples — a documented weak spot.

**Splits.** 80/10/10 for the Orig context-less set; 90/5/5 for the smaller context-full sets (because they're ~3× smaller, more data is kept for training).

**Diversity sanity-check.** Pairwise cosine similarity for *neutral* utterances within the same character averages µ ≈ 0.30 (σ ≈ 0.16) — higher than the cross-character µ ≈ 0.16 (σ ≈ 0.12), i.e., the teacher repeats itself more on neutrals. This is flagged as a known limitation.

## 7. Student models

- **Primary student:** `FacebookAI/roberta-large` → "π-RoBERTa" (context-less) and "π-CRoBERTa" (context-aware).
- **Baseline student:** `google-bert/bert-large-uncased`.
- **Specialised student for IEMOCAP:** `sentence-transformers/paraphrase-distilroberta-base-v1` (SBERT), used as a drop-in inside the CORECT multimodal architecture.

All students share the same head: **a single linear layer + sigmoid over 28 classes**, trained multi-label. No CRF, no ordinal stacking, no multi-task heads.

## 8. Training objective + setup

- **Loss:** binary cross-entropy on the hard-thresholded soft labels (positive iff teacher expressiveness ≥ 0.3).
- **Optimiser:** AdamW, initial learning rate **2e-5**, HuggingFace Trainer defaults for warmup and weight decay.
- **π-RoBERTa (context-less):** 10 epochs, `max_seq_length = 128`, `batch_size = 64`. No early stopping; the final checkpoint is used.
- **π-CRoBERTa (context-aware):** 10 epochs base, `max_seq_length = 512`, `batch_size = 32`. **Token-type IDs** are repurposed to mark segments: `0` for context tokens, `1` for utterance tokens — letting the encoder learn *where* the emotion should come from.
- **Downstream fine-tuning** uses 3 epochs (GoEmotions, EmoContext) or 8 epochs (ISEAR) with task-appropriate batch/seq settings.

## 9. Evaluation

**Threshold sweep.** For every multi-label experiment, the global decision threshold is swept from **0.05 to 0.95 in steps of 0.01**, and the one yielding the highest **macro-F1** is reported. Micro-F1 is dismissed as an "over-promise" on imbalanced multi-label sets.

**GoEmotions.** Both zero-shot (apply π-RoBERTa directly) and fine-tuned for 3 epochs on the GoEmotions train split.

**ISEAR.** 5-fold cross-validation, 80/20 train/test per fold, 8 epochs, batch 4, `max_seq_length = 512`. The 7-way ISEAR taxonomy is mapped into the 28-class output space.

**IEMOCAP.** The CORECT multimodal architecture (Nguyen 2023) is used unchanged except that its text encoder (originally SBERT) is **replaced by π-RoBERTa**. Both 4-way and 6-way variants are evaluated.

**EmoContext.** Three-turn dialogue corpus. π-CRoBERTa is applied with the first two turns as context and the third as utterance, fine-tuned for 3 epochs.

**Human evaluation.** Three CS-postdoctoral annotators each judged a 200-example sample (with neutral upsampled to 10%). Each item is a multiple-choice question with 7 options: 5 plausible emotions ranked by teacher expressiveness, 1 less-plausible distractor, and a "none" option. **Cohen's κ = 0.365** (vs. 0.293 reported for GoEmotions); accuracy is **0.86 when all three annotators agree** and **0.70 when at least two agree**; recall on neutral examples is 0.9.

## 10. Results (with real numbers)

| Benchmark | Model | Macro-F1 |
|---|---|---|
| **GoEmotions** (fine-tuned) | emo π-RoBERTa | **0.55 ± 0.007** (claimed SOTA) |
| **ISEAR** (5-fold CV) | emo π-RoBERTa | **0.75 ± 0.013** |
| **IEMOCAP 4-way** | CORECT ← emo π-RoBERTa | **0.83** (SOTA) |
| **IEMOCAP 6-way** | CORECT ← emo π-RoBERTa | 0.63 (confusion concentrated on *excited/happy/neutral*) |
| **EmoContext (dev4)** | emo π-CRoBERTa fine-tuned on rewritten data | **0.82** |

**Context-aware vs context-less head-to-head.** On the intra-dataset rewritten-utterance + context test, context-aware models beat their context-less counterparts by **+2–3 percentage points** (Table 5: 0.79 vs 0.75 / 0.72 vs 0.67), exactly the kind of margin the synthesis pipeline was designed to expose.

**Seed-corpus scalability.** Shrinking the seed corpus 10× (200 plots instead of 2000) drops intra-dataset context-aware macro-F1 only from **0.79 → 0.77**, suggesting the pipeline's marginal data efficiency is high — useful when teacher inference is the budget constraint.

## 11. Ablations

The paper systematically ablates:

- **Context-aware vs context-less:** π-CRoBERTa vs π-RoBERTa on matched test sets (Table 5).
- **Rewriting:** CRewr (rewritten + cleaned context) vs COrig (original utterance + raw context). Rewriting forces the model to actually attend to context for emotion cues.
- **Label remapping for downstream tasks:** with vs without the "others" → 28-class remap on EmoContext (Table 7: 0.81 vs 0.82 with token-type IDs).
- **Seed-corpus size:** 2000 vs 200 plots → 0.79 vs 0.77.
- **Neutral diversity:** pairwise similarity within vs across characters.
- **Expressiveness ranking validation:** comparing annotator accuracy when the 5 candidate emotions are presented ranked vs shuffled (Table 14).

**What is *not* ablated** (worth flagging when borrowing this methodology): teacher model size (no GPT-4 / Llama-70B comparison; cost-prohibitive), taxonomy size (28 is taken as given), and the choice between hard-label BCE and a true KL/soft-logit distillation. Token-type IDs are tested only on EmoContext, not on every downstream benchmark.

## 12. Authors' stated limitations

The author flags four honest limitations:

1. **Insufficient neutral diversity.** Generated neutral utterances cluster tightly per character (µ = 0.30 within-character cosine similarity), and the neutral class is underweighted post-filter (9% of examples). This dampens performance on benchmarks where "neutral" is a dominant class — notably IEMOCAP 6-way.
2. **Out-of-taxonomy hallucinations.** Despite the manual remap table, the teacher occasionally emits emotion words outside the 28-class set, requiring discard.
3. **Single-teacher bias.** Only Mistral-7B-Instruct-v0.2 was used as teacher. A second, smaller validation pass with GPT-3.5 is reported, but a full second pipeline run with a different backbone is left to future work because of the 450-GPU-hour cost.
4. **English- and culture-bound.** WikiPlots is English; the LLM was trained predominantly on English. Multilingual extension (e.g., via the Salamandra model family) is proposed but not executed. Ethical concerns are also raised about applying the pipeline to non-fictional sources (news, social media) that involve real people.

## 13. Relevance to Pebble

Emo Pillars is, to date, the **strongest single precedent** in the literature for the Pebble approach of distilling a generative LLM teacher into a smaller encoder student for fine-grained emotion classification. The methodological overlap is substantial:

- **Same backbone family.** Both projects target a RoBERTa-class encoder with a multi-label classification head and BCE loss. The Pebble student architecture inherits directly from the same design space.
- **Same distillation philosophy.** Both treat the teacher as a *label oracle* rather than a logit oracle: BCE on filtered teacher labels, no KL term. This validates Pebble's hard-label setup against an ACL-accepted baseline.
- **Same evaluation grammar.** Threshold-sweep max-F1 and macro-averaging on imbalanced multi-label outputs are exactly the regime Pebble lives in.

Pebble differs along several axes worth being explicit about in any paper writeup:

- **Heterogeneous heads.** Pebble combines regression (intensity), softmax (categorical primary), and BCE (multi-label co-occurring emotions) on a shared backbone — Emo Pillars uses a single BCE head.
- **Safety-recall constraint.** Pebble's mental-health setting imposes asymmetric loss on high-risk emotion classes; Emo Pillars has no such asymmetry.
- **Conversational mental-health domain.** Pebble works on real user-facing conversational data; Emo Pillars synthesises narrative-fiction plots. Domain transfer is non-trivial.
- **Bigger teacher.** Pebble uses Gemini Flash, considerably larger than Mistral-7B; the qualitative distillation surface is identical but Pebble's teacher labels should be cleaner per inference, possibly allowing a higher (or class-conditional) expressiveness threshold.

**Three concrete tricks Pebble can adopt directly:**

1. The **0.3 expressiveness threshold** for converting LLM-emitted soft scores into hard multi-label targets — empirically validated to yield 1–5 labels per example with mean 3.17.
2. The **global threshold sweep 0.05→0.95 step 0.01** as the standard reporting protocol for max macro-F1, avoiding the default-0.5 trap.
3. The **human-eval design**: 3 annotators × 200 examples with ranked multiple choice, reporting Cohen's κ *and* accuracy stratified by agreement level (unanimous / ≥2). This is cheap, defensible, and benchmark-comparable.

## 14. Recommended citation use

In a Pebble paper, *Shvets (2025) — Emo Pillars* is the right citation for:

- **"LLM-teacher distillation works for encoder emotion classifiers."** Emo Pillars demonstrates SOTA on GoEmotions (macro-F1 = 0.55), ISEAR (0.75), and IEMOCAP 4-way (0.83) from a fully synthetic training set.
- **"Hard-label BCE on thresholded teacher outputs beats LLM-as-classifier."** The paper explicitly cites Wang et al. 2024 and Chochlakis et al. 2024 for LLM emotion-classification failures and shows that distilling solves them.
- **"Context-aware training improves rewriting-style robustness."** The +2–3 p.p. gap (0.79 vs 0.75; 0.72 vs 0.67) on rewritten utterances paired with contexts is the right number to quote when arguing that conversational emotion classifiers should be trained with surrounding turns, not just utterance-in-isolation.
- **"Synthetic emotion data scales gracefully."** The 200-plot vs 2000-plot ablation (0.77 vs 0.79) supports the argument that an LLM-generated corpus reaches a useful operating point well before the teacher budget is exhausted.
- **"Threshold sweep + macro-F1 is the standard reporting protocol"** for multi-label fine-grained emotion benchmarks, and the **3 × 200-example human-eval protocol with Cohen's κ** is a defensible cheap-to-run validation design.

Where Pebble *diverges* — heterogeneous heads, safety-asymmetric loss, real-conversation domain, and a larger Gemini-Flash teacher — Emo Pillars stands as the baseline against which those design choices need to be justified, not the method to be replicated wholesale.
