# Related Work Survey — Pebble Emotion Classifier

> **Purpose.** Five papers closest in idea and method to the Pebble Emotion Classifier (NeoBERT multi-task fine-tuning for mental-health/emotional-support conversational AI). Each paper is analyzed on dataset, architecture, multi-task setup, evaluation, limitations, and gap-vs-Pebble. The cross-paper synthesis at the end proposes candidate novel-contribution angles for a new paper.
>
> **Compiled:** 2026-06-08

---

## Pebble in one paragraph (for context)

Pebble fine-tunes **NeoBERT** (250M-parameter encoder) into a multi-task affect classifier with three heterogeneous heads on a shared `[CLS]`: (a) a sigmoid **continuous-score head** for `energy / severity / socialIsolation / receptivity`, (b) a softmax **emotion head** over a 12-label taxonomy warm-started from GoEmotions, and (c) a binary **safety/crisis head** with high positive-class weight (target recall ≥ 0.95). Training data is ~5K Gemini silver labels + 500 human Protocol-A + 500 human Protocol-B. Knowledge transfer from GoEmotions / EmpatheticDialogues / DailyDialog / SemEval-2025 / WASSA / TalkLife. Staged training (frozen encoder → unfreeze). Loss = MSE + CE + BCE, with planned escalation to Kendall uncertainty weighting or GradNorm if heads diverge.

The dimensions used to rank "closeness" of related work:

1. Multi-task encoder for emotion/affect with **categorical + continuous** outputs (ideally + safety head)
2. **Mental-health** text classification with transformer encoders
3. Transfer / pre-training using **GoEmotions / EmpatheticDialogues**
4. **Silver-label distillation from a teacher LLM** into a smaller student
5. **Multi-task loss balancing** (uncertainty weighting, GradNorm) in NLP affect tasks

---

## Paper 1 — FAIIR: Conversational AI Agent Assistant for Youth Mental Health Service Provision

- **Authors / Year / Venue:** Stephen Obadinma, Alia Lachana, Maia Norman, Jocelyn Rankin, Joanna Yu, Xiaodan Zhu, Darren Mastropaolo, Deval Pandya, Roxana Sultan, Elham Dolatabadi. arXiv preprint May 2024; published in **npj Digital Medicine, 2025**.
- **Links:** [arXiv:2405.18553](https://arxiv.org/abs/2405.18553) · [npj Digital Medicine](https://www.nature.com/articles/s41746-025-01647-6)

### Summary
An ensemble of domain-adapted transformer encoders fine-tuned on **~780,000 Kids Help Phone crisis conversations** to multi-label-classify each session into **19 clinically-grounded "issue tags"** (suicidality, abuse, anxiety, depression, etc.) to assist frontline youth crisis responders.

### Dataset
- ~780K real youth crisis-line conversations (Kids Help Phone, Canada).
- 19 multi-label clinical issue tags including suicidality and abuse.
- Historical labels by frontline workers — noisy, as the paper itself documents.

### Architecture
- Ensemble of domain-adapted transformer encoders fine-tuned for long-conversation classification.
- 19 binary heads over a shared encoder (multi-label sigmoid, BCE-style loss).
- Param counts not detailed in abstract; built on Neural Agent Assistant framework.

### Multi-task setup
- Multi-label categorical only — no auxiliary regression, no affective dimensions, no explicit task-weighting balancing.

### Key results
- **Average AUROC = 0.94, sample-average F1 = 0.64, sample-average recall = 0.81** (retrospective test set).
- **<2% degradation in prospective "silent testing."**
- **90.9% agreement** between crisis responders and FAIIR predictions.
- Expert agreement with FAIIR exceeded their agreement with the original labels.

### Authors' limitations
- Label noise in historical Kids Help Phone tags (experts trusted FAIIR more than ground truth).
- Long-conversation segmentation challenges.
- Deployment risk: responder over-reliance.
- Ensemble cost.

### Overlap with Pebble
Dimensions **2** (mental-health classification with transformer encoders), **7** (production-oriented pipeline feeding a downstream workflow, suicidality as critical output), and partial **1** (multi-head classification on shared encoder).

### What Pebble does differently (gap)
- FAIIR is **purely multi-label categorical** — no continuous affective dimensions.
- No explicit task-weighting balancing scheme (no Kendall/GradNorm).
- No LLM-teacher silver-label distillation; labels are noisy human history.
- **Pebble adds:** continuous regression heads, uncertainty-weighted multi-task loss across regression+classification+BCE, teacher-LLM distillation as the silver-label source.

---

## Paper 2 — VAD-assisted Multitask Transformer for Emotion + Intensity on Suicide Notes

- **Authors / Year / Venue:** Soumitra Ghosh, Asif Ekbal, Pushpak Bhattacharyya. **2022. Information Processing & Management, Vol. 60(2), 103234.**
- **Link:** [DOI 10.1016/j.ipm.2022.103234](https://doi.org/10.1016/j.ipm.2022.103234) · [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0306457322003351)

### Summary
A pre-trained transformer encoder jointly trained for **multi-class emotion recognition** and **continuous emotion-intensity prediction** on suicide notes, using **lexicon-derived Valence/Arousal/Dominance** scores as both auxiliary supervision and input enrichment.

### Dataset
- **CEASE-v2.0:** 4,932 sentences from 205 real suicide notes.
- **15 fine-grained emotion classes** (forgiveness, happiness/peacefulness, love, pride, hopefulness, thankfulness, blame, anger, fear, abuse, sorrow, hopelessness, guilt, information, instructions).
- Authors extended every sentence with an **emotion-intensity label** (new contribution).

### Architecture
- Pre-trained BERT/RoBERTa encoder → sentence embedding, concatenated with VAD lexicon features.
- **Two task-specific heads:** softmax (emotion class) + regression (intensity).
- Trained jointly with weighted CE + MSE loss.

### Multi-task setup
- Two tasks (emotion + intensity), VAD as auxiliary input + regularization signal.
- Static weighted-sum loss; weights tuned empirically. **No uncertainty / GradNorm.**

### Key results
- **Best Mean Recall (MR) = 65.25%** on the emotion task.
- **+3.78% MR over prior SOTA** on CEASE-v2.0.
- Multi-task variants consistently beat single-task baselines.

### Authors' limitations
- Small dataset; class imbalance across 15 emotions.
- Difficulty disentangling intensity from class.
- English suicide notes only — limited generality.
- Reliance on a static VAD lexicon.

### Overlap with Pebble
Dimensions **1** (categorical + continuous on shared encoder), **2** (mental-health / suicide-adjacent classification), partial **5** (multi-task loss weighting).

### What Pebble does differently (gap)
- Pebble adds a **dedicated binary safety/crisis head** with high positive-class weight on top of categorical + continuous tasks — Ghosh & Ekbal have only two tasks, no separate crisis flag.
- **Kendall-style uncertainty / GradNorm** instead of static weights.
- **Silver-label distillation from a teacher LLM** vs. human annotation.
- **Conversational support domain** vs. single-sentence suicide notes.

---

## Paper 3 — Tri-Task Mental Health + Emotion + Sentiment on Motivational Conversations

- **Authors / Year / Venue:** A. Pathak, S. Bhattacharjee, Tulika Saha, Sriparna Saha. **2025. ACM Transactions on Computing for Healthcare.**
- **Link:** [ACM DOI 10.1145/3704740](https://dl.acm.org/doi/10.1145/3704740)

### Summary
A **"Core Fusion Network"** multi-task framework on a transformer encoder that jointly performs **mental-health disorder identification (primary), emotion recognition, and sentiment analysis (auxiliary)** on motivational dyadic support conversations. Tri-task variant beats bi-task and uni-task baselines.

### Dataset
- **Extended MotiVAte:** ~7,067 dyadic support-seeker / virtual-assistant motivational conversations, 1,839 unique users.
- Re-annotated **semi-automatically** with emotion and sentiment labels per turn.
- Mental-health disorder labels pre-existing; emotion + sentiment added in this work.

### Architecture
- BERT-family encoder backbone.
- "Core Fusion Network" learns **private vs. shared feature spaces** across the three tasks.
- Three CE classification heads (disorder, emotion, sentiment).

### Multi-task setup
- One primary + two auxiliary tasks.
- Weighted CE sum across heads; ablations confirm tri-task > bi-task > uni-task.
- **No uncertainty weighting reported.**

### Key results
- Quantitative numbers paywalled / not retrievable in this pass.
- Reported gain is qualitative: tri-task > bi-task > uni-task on primary mental-health task, with paired-comparison significance.

### Authors' limitations
- Emotion/sentiment labels are **semi-automatic silver labels** — noise.
- Non-clinical conversations limit generalizability.
- English-only.

### Overlap with Pebble
Dimensions **1** (multi-head shared-encoder classification), **2** (mental-health text), **7** (conversational support-seeker domain), partial **4** (auxiliary labels are silver labels from automation).

### What Pebble does differently (gap)
- Pebble's auxiliary outputs are **continuous regressions**, not categorical sentiment.
- Dedicated **safety/crisis head with asymmetric BCE weighting**.
- LLM teacher (Gemini) as silver-label source, not rules.
- Tests **principled MTL balancing** (Kendall / GradNorm), not empirical weighting.

---

## Paper 4 — Emo Pillars: Knowledge Distillation for Fine-Grained Emotion Classification

- **Authors / Year / Venue:** Alexander Shvets (UPF / BSC). **2025. Findings of ACL 2025.**
- **Links:** [arXiv:2504.16856](https://arxiv.org/abs/2504.16856) · [ACL Anthology](https://aclanthology.org/2025.findings-acl.10/)

### Summary
Uses **Mistral-7B as a teacher LLM** to synthesize **400K narrative-grounded silver-labelled examples** over a 28-emotion taxonomy, then fine-tunes BERT/RoBERTa-large **student encoders** that reach SOTA on GoEmotions, ISEAR, and IEMOCAP.

### Dataset
- Synthesized **100K context-aware + 300K context-less utterances** over 28 emotion classes.
- Evaluated on **GoEmotions** (27 + neutral), **ISEAR**, **IEMOCAP** (4-way), **EmoContext**.
- Teacher: Mistral-7B — **700K inferences, ~450 GPU hours.**

### Architecture
- Encoder-only students: RoBERTa-large primary, BERT-large-uncased baseline, Sentence-BERT for embeddings.
- **Multi-label sigmoid head + BCE.**
- AdamW, lr = 2e-5.

### Multi-task setup
- **Single multi-label head — not multi-task.**
- "Distillation" is **via teacher-generated synthetic labels**, not soft-logit distillation.

### Key results
- **GoEmotions macro-F1 = 0.55 ± 0.007** (reported SOTA).
- ISEAR macro-F1 = **0.75 ± 0.013** (5-fold CV).
- IEMOCAP 4-way F1 = **0.83**.
- EmoContext dev F1 = **0.82**.
- Human eval: **0.86 label accuracy** on unanimous-agreement subset.

### Authors' limitations
- Insufficient diversity in neutral-class examples.
- Difficulty handling out-of-taxonomy labels.
- Reliance on a single teacher model → teacher bias.

### Overlap with Pebble
Dimensions **3** (GoEmotions taxonomy / transfer) and **4** (silver-label distillation from a teacher LLM into a smaller encoder).

### What Pebble does differently (gap)
- Emo Pillars is **single-task multi-label only** — no continuous affect regression, no safety head, no MTL balancing problem.
- Pebble has **three heterogeneous heads** (regression + softmax + BCE) where the loss-balancing research question lives.
- Pebble's teacher is **Gemini in the conversational mental-health domain**.
- Pebble must satisfy a hard **safety-head recall ≥ 0.95 constraint**, which Emo Pillars does not address.

---

## Paper 5 — Computational Approach to Empathy in Text-Based Mental Health Support

- **Authors / Year / Venue:** Ashish Sharma, Adam S. Miner, David C. Atkins, Tim Althoff. **EMNLP 2020 (pp. 5263–5276).**
- **Links:** [ACL Anthology](https://aclanthology.org/2020.emnlp-main.425/) · [arXiv:2009.08441](https://arxiv.org/abs/2009.08441)

### Summary
Multi-task RoBERTa **bi-encoder** trained on TalkLife and mental-health Reddit data to jointly identify **expressed empathy** (3-level classification across three mechanisms) and extract **token-level rationales**, with domain-adaptive MLM pre-training on peer-support corpora.

### Dataset
- **TalkLife:** 6.4M threads, 18M interactions; 10K human-annotated post-response pairs.
- **55 mental-health subreddits:** 1.6M threads, 8M interactions.
- 235K filtered TalkLife interactions for analysis.
- **Label scheme:** 3 empathy mechanisms (Emotional Reactions / Interpretations / Explorations) × 3 communication levels (no / weak / strong).

### Architecture
- **RoBERTa-base bi-encoder** (~251M params total: 2 × 125M + heads): S-Encoder for seeker post + R-Encoder for response, joined by a single-head attention layer.
- **Domain-adaptive MLM pre-training** on 182M seeker tokens + 279M response tokens.

### Multi-task setup
- Two tasks: Empathy Identification (3-class CE per mechanism) + Rationale Extraction (token-level span prediction).
- Combined loss: **L = λ_EI · L_EI + λ_RE · L_RE**, with λ_EI = 1, λ_RE = 0.5 — **hand-tuned static weighting**.

### Key results
- Empathy identification (TalkLife): **~80% accuracy, macro-F1 ≈ 0.73–0.74** (+4 macro-F1 over single-task RoBERTa).
- Rationale token-F1 = **0.64–0.68**.
- Rationale span-F1 (IoU) = **0.83–0.86**.
- Annotator IAA = **0.6865**.

### Authors' limitations
- Captures **"expressed" rather than "perceived"** empathy.
- Moderate inter-rater agreement.
- Struggles with short emotional expressions amid instructions.
- Ethical concerns around deployment without clinical validation.
- Proof-of-concept involved only three participants.

### Overlap with Pebble
Dimensions **2** (mental-health peer-support transformer classifier), **3** (TalkLife is on Pebble's planned source list), partial **1** (multi-task shared encoder with categorical heads), partial **5** (hand-tuned multi-task loss weighting).

### What Pebble does differently (gap)
- Sharma et al. has **no continuous-score regression heads**, **no safety/crisis head**, and **no LLM-teacher distillation**.
- Bi-encoder (post + response) rather than single-utterance encoder.
- Static λ multi-task balancing.
- **Pebble extends to:** heterogeneous categorical + continuous + safety heads; Kendall/GradNorm dynamic balancing; Gemini silver-label distillation; staged freeze/unfreeze training with GoEmotions warm-start.

---

## Cross-Paper Synthesis

### Common methodological patterns
- Shared transformer encoder (BERT / RoBERTa / domain-adapted) + task-specific heads.
- Multi-label / multi-class softmax heads dominate; **continuous regression heads are rare** (only Ghosh & Ekbal 2022 and the WASSA empathy/distress line use them).
- **Static / hand-tuned λ weighting** of multi-task losses is the default. Principled methods (Kendall uncertainty, GradNorm) appear mostly in vision and only sporadically in NLP affect work (e.g., WASSA 2022 "Uncertainty Regularized MTL" on RoBERTa empathy/distress).
- **Domain-adaptive MLM pre-training** (Sharma 2020; MentalBERT line) is a recurring recipe before fine-tuning.
- When categorical + continuous co-exist, the continuous signal is usually VAD or empathy/distress — **never a "safety / crisis" binary**.

### Common dataset choices
GoEmotions (Demszky et al. 2020), EmpatheticDialogues, DailyDialog, TalkLife, Reddit mental-health subreddits, CEASE / CEASE-v2.0, WASSA empathy-distress essays, MotiVAte, DAIC, and (newest) SemEval-2025 Task 11 for intensity. **These match Pebble's intended training-data list almost exactly.**

### Common evaluation protocols
- Macro-F1 / weighted-F1 for classification.
- Pearson correlation for empathy/distress regression.
- MAE for intensity.
- AUROC + recall for safety-critical labels (FAIIR).
- **Recall-at-high-precision targeting** is rarely reported except by FAIIR — most affect papers do not enforce a hard recall floor on the safety class.

### Gaps acknowledged or unexplored
- Small target-domain datasets and reliance on silver labels (Pathak et al. 2025 explicitly flags this).
- **Lack of principled loss balancing for heterogeneous heads** (regression + classification + BCE) — most papers default to grid-searched λ.
- **Teacher-LLM bias and out-of-taxonomy emotions** (Shvets 2025 names both).
- **No published affect classifier in this set integrates a hard recall ≥ 0.95 constraint on a crisis head while jointly optimizing continuous affect regression.** FAIIR has a suicidality tag but does not formalize this trade-off; Ghosh & Ekbal regress intensity but have no safety head.
- Almost none study **staged freezing schedules or GoEmotions-as-warm-start** systematically for a downstream conversational mental-health task.

---

## Candidate Novel-Contribution Angles for the Pebble Paper

Ranked by publishability / defensibility given existing literature:

### 1. **Heterogeneous multi-head balancing for safety-critical affect classification** *(strongest)*
Empirically compare **static λ vs. Kendall uncertainty weighting vs. GradNorm** specifically when **one head is a high-recall BCE crisis head** and the others are sigmoid-regression affective dimensions. Current literature handles categorical+categorical or categorical+regression, but the **asymmetric, recall-constrained regime is open and deployment-motivated**. Strong fit for EMNLP / ACL Findings / WASSA.

### 2. **Distilling a frontier LLM into a small multi-task affect encoder for emotional-support chatbots**
Show that silver labels from Gemini can train a 250M NeoBERT student that reaches teacher-level agreement on continuous affect dimensions **while preserving a hard suicidality recall floor**. Direct extension of Emo Pillars (categorical only) to mixed regression+classification+safety. Clean, publishable at WASSA / CLPsych / EMNLP Findings.

### 3. **GoEmotions warm-start + staged unfreezing for low-resource conversational affect**
Quantify how much of the gain on 5K silver + 1K human target-domain data comes from (a) the staged freeze/unfreeze schedule and (b) the GoEmotions-pretrained emotion head. Clean ablation paper; less novel than (1) or (2) but useful as a section in either.

### 4. **Calibration and reliability of teacher-LLM silver labels on continuous affective dimensions**
Measurement study: how well do Gemini-produced continuous scores agree with human raters on `energy / severity / receptivity`, and does student-model calibration recover from teacher overconfidence? Highly publishable at **CLPsych / npj Digital Medicine** because it directly informs deployment risk.

### 5. **A unified affect+safety decision-engine front-end for emotional-support agents**
Frame Pebble as a **systems contribution**: encoder-side decoupling of affect estimation from generation, with the Decision Engine as the consumer of structured outputs. Weakest standalone but strongest **JMIR Mental Health / npj Digital Medicine** angle when paired with prospective deployment data.

---

## Recommended angle for the new paper

The two strongest, mutually compatible angles are **(1) heterogeneous MTL balancing under a hard safety-recall constraint** and **(2) teacher-LLM silver-label distillation into a multi-task affect encoder**. Bundling them into a single paper — *"Distilling a frontier LLM into a NeoBERT student for mental-health affect classification under a hard crisis-recall constraint, with uncertainty-weighted multi-task balancing across regression + classification + safety heads"* — covers the largest unclaimed area in the related work and aligns naturally with the existing Pebble training pipeline. **(3)** then becomes the warm-start ablation inside the same paper, and **(4)** becomes the calibration analysis section.

---

## Sources

- [FAIIR (npj Digital Medicine, 2025)](https://www.nature.com/articles/s41746-025-01647-6)
- [FAIIR arXiv preprint](https://arxiv.org/abs/2405.18553)
- [Ghosh, Ekbal, Bhattacharyya — VAD-assisted multitask transformer (IPM, 2022)](https://doi.org/10.1016/j.ipm.2022.103234)
- [Pathak et al. 2025 — CFN on MotiVAte (ACM THC)](https://dl.acm.org/doi/10.1145/3704740)
- [Shvets — Emo Pillars (arXiv 2504.16856)](https://arxiv.org/abs/2504.16856)
- [Shvets — Emo Pillars (ACL Findings 2025)](https://aclanthology.org/2025.findings-acl.10/)
- [Sharma et al. 2020 — Computational Empathy (EMNLP)](https://aclanthology.org/2020.emnlp-main.425/)
- [Uncertainty Regularized Multi-Task Learning (WASSA 2022)](https://aclanthology.org/2022.wassa-1.8/)
- [PVG at WASSA 2021](https://arxiv.org/abs/2103.03296)
- [WASSA@IITK at WASSA 2021](https://arxiv.org/abs/2104.09827)
- [SemEval-2025 Task 11 task description](https://arxiv.org/html/2503.07269v1)
- [GoEmotions (Demszky et al., ACL 2020)](https://aclanthology.org/2020.acl-main.372/)
- [MentalBERT (LREC 2022)](https://aclanthology.org/2022.lrec-1.778.pdf)
