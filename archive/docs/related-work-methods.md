# Related Work — Methods Sections (Extracted)

> Companion to [`related-work-survey.md`](./related-work-survey.md). For each of the 5 closest-adjacent papers, this document extracts the **methods** in detail: data preprocessing, architecture, multi-task setup, loss, training hyperparameters, evaluation protocol. Paywalled details are flagged explicitly.
>
> **Compiled:** 2026-06-08

---

## Paper 1 — FAIIR (Obadinma et al., npj Digital Medicine 2025 / arXiv:2405.18553)

*Source: arXiv PDF, Section 5 "Online Methods" and Appendices B/D.*

### 1.1 Data preprocessing & label engineering
- **Corpus.** 703,975 unique, scrubbed, multi-turn SMS dialogues between service users and crisis responders (CRs), Jan 2018 – Feb 2023. Second batch of **84,832** conversations (Feb–Sep 2023) held out for prospective "silent testing." (The 780K figure in the abstract is the sum.)
- **Population:** training spans 340,512 users + 7,937 CRs; silent test spans 57,031 users + 2,038 CRs.
- **De-identification:** names/locations auto-replaced with `[scrubbed]`. The process is noisy — sometimes scrubs harmless words (e.g., "turkey"). No additional PII pipeline (regex, NER) is described.
- **Label scheme:** the **19 issue tags** are KHP's existing operational taxonomy (Depressed, Anxiety/Stress, Gender/Sexual Identity, Suicide, Abuse, Bully, Grief, Isolated, Prank, DNE, 3rd Party, Other, etc.). Labels are single-annotator (the CR who handled the conversation), at CR discretion, and "typically do not undergo additional review" — i.e., noisy operational silver labels.
- **Auxiliary priority feature.** A priority flag (Low / Medium / High) is generated at conversation start (suicidal ideation → Medium; ideation + plan + means + 0–48 h → High) and **injected as a textual prefix**: `"This conversation is of <<X>> priority."`
- **Splits.**
  - Step-1 model comparison: 50K conversations, **60/20/20 stratified**.
  - Step-2 final fine-tuning: full corpus, **60/20/20 label-balanced** → 422,385 train / 140,795 val / 140,795 test. The 84,832 silent-test conversations are an additional temporally-held-out cohort.
- **Class imbalance:** Anxiety/Stress dominant; rarest tag (Prank) appears in only 2,800 conversations. Handled by **oversampling rare-tag conversations in 2 of 3 ensemble members** (no per-class loss weighting).

### 1.2 Model architecture
- **Step-1 base encoders compared:** Longformer (149M, encoder-only), Conversational BERT (110M, encoder-only), DialogLED (139M, enc-dec), MVP (406M, enc-dec).
- **Long-conversation handling:** Longformer capped at **2,048 tokens** (1,500 during MLM). No sliding-window/hierarchical scheme — relies on Longformer's native sparse attention.
- **Multi-label head:** **single linear layer + sigmoid** over `[CLS]` → 19 independent probabilities. (For enc-dec models: `[EOS]` for DialogLED, first token for MVP.)
- **Deployed FAIIR ensemble:** **3 Longformer models** with different init / fine-tuning settings. Combination rule not stated explicitly — natural reading is **probability averaging across the 3 models then per-tag thresholding** (not stated verbatim).
- **Ensemble diversity:** 2 of the 3 use rare-tag oversampling; the third trains on natural distribution.

### 1.3 Training setup
- **Step-1 fine-tuning:** effective batch 16, **4× NVIDIA A10 (24 GB)** + 16 CPU cores, ~12 h/epoch, LR sweep 1e-5 – 3e-5, epochs by hyperparam search (**5 for Longformer**).
- **Step-2 final fine-tuning:** max 3 epochs, batch 16 (gradient accumulation), **LR 2e-5**, **AdamW**, **linear schedule with 20% warmup**, **standard BCE loss** (no focal loss, no class weights — imbalance handled via oversampling).
- **Dropout, weight decay, gradient clipping: not reported.**

### 1.4 Domain adaptation
Yes — explicit continued **MLM pre-training on KHP** before fine-tuning:
- 15% token masking, **1 epoch, max seq length 1,500**, AdamW, **linear schedule with 500 warmup steps**, gradient accumulation to effective batch 64, ~24 h.

### 1.5 Evaluation protocol
- **Retrospective test set** (n=140,795): per-tag and averaged Accuracy, Exact Accuracy, **Sample-Avg Precision/Recall/F1**, **AUROC (mean ≈ 0.94)**. Averaging is sample/example-based.
- **Prospective "silent testing"** (n=84,832): FAIIR ran on incoming traffic without modifying CR workflow. **<2% drop in all metrics**.
- **Threshold tuning:** swept 0.25 → 0.5 on validation; final per-tag tuned with expert feedback — **0.4 for Anxiety/Stress, Depressed, Relationship; 0.3 for Suicide, Isolated; 0.2 for the remaining 14 tags.**
- **Responder-agreement study:** 12 trained CRs reviewed 40 challenging conversations, **6 CRs per conversation in 2 groups of 3** (open + blind), with 5 consensus criteria. Aggregate: **90.9% agreement** with FAIIR.

### 1.6 Safety-specific design (suicidality)
The paper does **not** treat Suicide as a separate model or with a different loss term:
- **No higher BCE class weight.**
- **No separate model head** — one of the 19 sigmoid outputs.
- **Only safety-specific choice:** **lowered decision threshold (0.3)** to bias toward recall. Reported Suicide retrospective F1 = 0.73.
- **Priority-flag conditioning** indirectly encodes suicidality risk via the prefixed `<<High>> priority` string.

### 1.7 Items not reported
Dropout, weight decay, gradient clipping, ensemble combination rule (averaging vs voting), oversampling ratio, MLM hyperparameter sweep, demographic-stratified eval hyperparameters, per-CR κ for blind review.

---

## Paper 2 — Ghosh, Ekbal, Bhattacharyya (IPM 2022, DOI 10.1016/j.ipm.2022.103234)

> **Accessibility caveat.** Publisher PDF paywalled (ScienceDirect / ACM DL / linkinghub all HTTP 403). No arXiv preprint, ResearchGate full-text, or institutional repository PDF was reachable. Triangulation uses a same-author IJCAI-ECAI 2022 sibling paper (`ijcai22-mental.pdf`) on the same corpus with a structurally similar TEMF framework. Items below labeled **NRIAS** = "not reported in accessible source."

### 2.1 CEASE-v2.0 dataset
- 4,932 sentences from **over 350** suicide notes (the user's "205" figure refers to CEASE v1, LREC 2020; CEASE-v2.0 is the extension). Sources: news bulletins, e-newspapers, blogs. Handwritten transcribed; typed OCR'd.
- 15 fine-grained sentence-level emotion classes: forgiveness, happiness_peacefulness, love, pride, hopefulness, thankfulness, blame, anger, fear, abuse, sorrow, hopelessness, guilt, information, instructions.
- Multi-label: 1st/2nd/3rd emotion in predominance order; 76% single-label, 22% two-label, 2% three-label.
- Three annotators (two PhDs, one grad). Krippendorff's α = **0.61** for emotion (from CEASE-v2.0 source paper).
- **Intensity annotation procedure (scale, annotators, IAA): NRIAS.**

### 2.2 VAD lexicon integration
**NRIAS.** Abstract says only "Valence, Arousal, Dominance — three determinants of emotion" and that the system is "VAD-assisted." Lexicon identity (NRC-VAD vs Warriner et al. vs ANEW vs SentiWordNet), sentence aggregation rule (mean/max/POS-weighted), and fusion mechanism (concat to `[CLS]` vs early fusion vs gated vs auxiliary VAD regression) **not disclosed in any accessible snippet**.

### 2.3 Model architecture
**NRIAS** at the requested granularity. Abstract-level only: "end-to-end VAD-assisted transformer-based multi-task network" with emotion classification primary and intensity prediction auxiliary. Encoder choice (BERT vs RoBERTa vs MentalBERT), param count, pooling, and per-head layer dims: **not in abstract**.

Triangulation from sibling IJCAI-ECAI 2022 paper: BERT-base `[CLS]`, sentence-level Transformer (5 heads, d=300, FFN=600), GloVe + fastText averaged input, Bahdanau additive attention. The IPM paper is likely architecturally similar but unconfirmed.

### 2.4 Loss and multi-task balancing
**NRIAS** for the IPM paper.

Triangulation from sibling paper (Eq. 7–8):
```
L = α · L_PB + β · L_TB + L_Diff
L_T = -(1/N) Σ_i t_i log Ô^T
L_Diff = Σ_b (δ_i - ρ_i)²  (MSE alignment between BERT [CLS] and sentence Transformer pooled output)
```
α, β tuned via grid search (values not stated).

For the IPM paper, a plausible analogous form is `L = α · CE_emotion + β · MSE_intensity (+ possible L_Diff or auxiliary VAD term)` — but the exact equation, weights, and tuning procedure are paywalled.

### 2.5 Training setup
**NRIAS** for the IPM paper.

Triangulation from sibling paper (likely upper bound, not actual): Adam, **LR 2e-5**, batch 4, 6 epochs, seq length 15, ReLU on dense hidden, softmax on output, **10-fold CV** (best-fold checkpoint kept, F1 averaged across five 10-fold runs), **NVIDIA RTX 2080 Ti**, TensorFlow, BERT-Base from google-research/bert, grid-search hyperparam selection.

### 2.6 Baselines
**NRIAS for IPM.** Likely list (from group's prior CEASE work): CNN (Kim 2014), CNN+cLSTM (Poria et al. 2017), single-task BERT-base, **CMSEKI** (Ghosh et al. 2021 — CEASE-v2.0 source paper, multitask depression+sentiment+emotion using commonsense knowledge).

### 2.7 Evaluation metrics
- Primary metric: **Mean Recall (MR)** (macro-averaged per-class recall = balanced accuracy in the authors' usage; formal definition not in accessible snippet).
- **MR = 65.25% on emotion**, described as **+8.78% over the prior SOTA** on a comparable task. (Note: the survey doc previously cited +3.78%; the abstract phrasing is "+8.78%" — likely measured on a different baseline; verify against the full paper.)
- Per-class F1, MAE for intensity, inter-task analysis: **NRIAS**.

### 2.8 Action item
To get NRIAS items (VAD lexicon choice, fusion mechanism, exact α/β, intensity scale, intensity IAA, per-class F1, MAE) the writer needs institutional ScienceDirect access or to email the corresponding author (`ghosh.soumitra2@gmail.com`, `asif@iitp.ac.in`, `pb@cse.iitb.ac.in`).

---

## Paper 3 — Pathak et al. (ACM THC 2025, DOI 10.1145/3704740)

> **Accessibility caveat.** ACM full text (`/doi/...`, `/doi/pdf/...`, `/doi/abs/...`) all returned HTTP 403. No arXiv, ResearchGate, or IIT Patna preprint discoverable. Items below labeled **NRIAS** = "not reported in accessible source." Reconstructed from ACM landing-page snippets, Sriparna Saha's publication list, and Google Scholar excerpts.

### 3.1 MotiVAte dataset extension
- Extends the previously released **MotiVAte** corpus (Saha et al. 2022) of dyadic conversations between a "support seeker" and a virtual assistant offering hope/motivation.
- Original MotiVAte: mental-health disorder labels over **MDD, PTSD, anxiety, OCD**; **7,067 dyadic conversations** spanning **1,839 unique users** in a non-clinical support-forum setting.
- New contribution: emotion and sentiment tags added to every conversation in a **"semi-supervised manner."** Tool stack (GPT-3/4 vs lexicon vs supervised teacher), rule layer, human-validation sample size, and IAA on silver labels: **NRIAS**.
- Label inventories for emotion / sentiment, per-split counts, user-level vs message-level split policy, train/val/test ratios: **NRIAS**.

### 3.2 Core Fusion Network (CFN) architecture
- Named **Core Fusion Network (CFN)**, presented as "a variation of multi-tasking" that **"adeptly considers private and shared features across tasks"** (accessible snippet).
- Places CFN in the **shared-private MTL family** (cf. Liu et al. 2017 adversarial MTL): a shared encoder branch + per-task private branches, fused before each head.
- Base encoder identity (BERT vs RoBERTa vs MentalBERT), shared-layer depth, fusion module (gated / cross-attention / concatenation), hidden dims, param count: **NRIAS**. Comparisons against "fully-shared (FS) and shared-private (SP) models with adversarial learning" strongly imply a Transformer-encoder backbone.

### 3.3 The three task heads
- **MHDI (primary):** mental-health disorder identification, 4-way over MDD/PTSD/anxiety/OCD (a "no-disorder" class is plausible but unconfirmed).
- **ER (auxiliary):** emotion recognition. Class count and head depth **NRIAS**.
- **SA (auxiliary):** sentiment analysis (presumably 3-way positive/neutral/negative, unconfirmed).

### 3.4 Loss formulation
- Per-task losses almost certainly cross-entropy with weighted sum across three heads.
- **Exact combined-loss equation, λ values, presence of orthogonality/adversarial/reconstruction auxiliary: NRIAS.** The CFN vs "shared-private with adversarial learning" framing implies an orthogonality (Frobenius-norm) or adversarial discriminator may be used to disentangle shared vs private representations — but this is paywalled.

### 3.5 Training setup
**NRIAS:** optimizer, LR, batch size, epochs, hardware, dropout, weight decay, max seq length, pre-training/warm-start step, code repository link.

### 3.6 Baselines
Three-tiered comparison (from snippets):
- **Uni-task MHDI** (disorder classification alone).
- **Bi-task variants** (MHDI + ER, MHDI + SA).
- **Tri-task** (MHDI + ER + SA — proposed CFN).

MTL family baselines:
- **Fully-Shared (FS)** — hard parameter sharing.
- **Shared-Private (SP)** — Liu et al. 2017 adversarial.
- **MMoE, Cross-Stitch, PLE**: **not confirmed in accessible source**.

### 3.7 Evaluation
- Primary task evaluated is MHDI; reports tri-task vs bi-task vs uni-task ablations.
- **Primary metric (accuracy vs macro-F1 vs weighted-F1), per-class disorder F1, auxiliary ER/SA metrics, statistical significance, human evaluation: NRIAS.**
- Central claim: **tri-task MHDI > bi-task MHDI > uni-task MHDI.**

### 3.8 Items needing the ACM full text
Silver-labeling tool stack + validation, label inventories + split sizes, encoder checkpoint + CFN fusion details, combined loss + task weights + auxiliary-term presence, full hyperparameter table, per-class disorder F1, headline metric definition.

---

## Paper 4 — Emo Pillars (Shvets, Findings of ACL 2025; arXiv:2504.16856)

*Source: arXiv PDF + ACL Anthology PDF (full text accessible).*

### 4.1 Teacher LLM setup
- **Model:** `mistralai/Mistral-7B-Instruct-v0.2`. GPT-3.5 used during prompt prototyping only.
- **Decoding (Appendix B):** **greedy decoding** (sampling disabled), **repetition_penalty = 1.03**. `max_new_tokens` per stage: actor extraction 300, utterance generation 500, soft-label generation 100, context generation 300, context cleaning 300, utterance rewriting 300.
- **Taxonomy injection:** 28 GoEmotions categories with Demszky et al. 2020 definitions (emoticons stripped), placed inline as `"Available list of emotions: <emotions and their definitions>"`. Hallucinated out-of-taxonomy labels manually mapped to nearest GoEmotions equivalent (e.g., anxiety→nervousness, indignation→anger).
- **Verbatim prompt templates** (Table 15):
  - **Actor extraction:** `Plot: <text> / Who are the characters in the plot? Try to list all of them, one per line.`
  - **Utterance generation:** `Plot: <text> / Available list of emotions: <emotions and definitions> / Actor: <actor> / Generate 8 possible utterances of this actor thinking aloud that express 8 various non-neutral emotions according to the context in the plot. Additionally, generate 2 neutral utterances of this actor thinking aloud afterwards.`
  - **Soft labels:** `The only possible list of emotions with their definitions: <classes> / Select from the list above the top 5 emotions the utterance expresses. List them with an expressiveness level from 0 to 1 with a step of 0.1. / Utterance: <utterance> / Start your response with: "1. <primary emotion>" and then add the following emotions with their expressiveness levels:`
  - **Context generation:** `Plot: <text> / Actor: <actor> / Actor's utterance: <utterance> / Expressed emotions: <emotions> / Explain why the actor was thinking aloud this way starting from as close to the beginning of the story as needed to provide a complete picture but only until the moment of the utterance. Avoid talking about the given emotional state of the actor throughout the explanation. Be as concise as possible.`
  - **Context cleaning:** `Character: <actor> / Context: <context> / Remove clauses or even entire sentences from the context that explicitly discuss the emotions of <emotions> in the character. / Summary: <cleaned context>`
  - **Utterance rewriting:** `Character: <actor> / Character's utterance: <utterance> / Expressed emotions: <emotions> / Rewrite the utterance so that the emotions are ambiguous without the summary. Be as concise as possible.`

### 4.2 Synthetic data generation pipeline
- **Seed corpus:** **WikiPlots** — 113K English Wikipedia synopses of movies/books/TV. Production used **2,000 plots**; a preliminary 200-plot run already hit 0.77/0.5 F1.
- **Per-plot yield:** ~15 characters/plot (std 9.44); each character produces 10 utterances (8 non-neutral + 2 neutral) across the 28-class taxonomy.
- **Soft labeling:** Mistral assigns up to 5 emotions per utterance with expressiveness ∈ {0.0, 0.1, …, 1.0}. **Keep example if ≥1 label has expressiveness ≥ 0.3** → 1–5 labels/example, mean = 3.17, std = 0.97.
- **Splits:**
  - **300K context-less** (Orig) from 2,000 plots, 80/10/10 train/dev/test.
  - **100K context-full** — one-third of the 300K carried through context-generation, cleaning, rewriting → **COrig** (original utterance + cleaned context) and **CRewr** (ambiguity-rewritten utterance + same context), 90/5/5 split.
- **Filtering / discard:** drop utterances with all expressiveness < 0.3; later relabelling assigns "others" residual to neutral / soft set. **No explicit deduplication** — semantic diversity argued via near-dup similarity statistics (µ ≈ 0.30, σ ≈ 0.16).

### 4.3 Student model architecture
- **Primary student:** `FacebookAI/roberta-large` (~355M params).
- **Baseline:** `google-bert/bert-large-uncased` (~340M).
- **IEMOCAP variant:** `sentence-transformers/paraphrase-distilroberta-base-v1` (fed into CORECT).
- **Head:** single output layer dim **28** with **sigmoid per class** (multi-label). Standard HF sequence-classification head over `[CLS]` — no MLP.

### 4.4 Training objective
- **Loss:** `torch.nn.BCELoss` over 28 sigmoid outputs (multi-label). Hard-thresholded soft labels (≥ 0.3 → 1).
- **No temperature-based KL distillation** on teacher logits — distillation is "implicit" via hard multi-label targets after filtering.
- **No label smoothing, no class weighting** reported.

### 4.5 Training setup
- **Optimizer:** HF Trainer default **AdamW**, **LR 2e-5**.
- **Context-less RoBERTa (π-RoBERTa):** `epochs=10`, `max_seq=128`, `batch=64`.
- **Context-aware RoBERTa (π-CRoBERTa):** same, `batch=32`. Token-type IDs distinguish context (0) vs utterance (1).
- **Downstream fine-tuning:** 3 epochs on EmoContext + GoEmotions; 8 epochs on ISEAR.
- **No early stopping** ("worked with final checkpoints"). Warmup ratio + weight decay: HF defaults.
- **Hardware/cost:** NVIDIA H100, **450 GPU hours total** (200 context-less + 200 context steps + 44 preliminary 18K run); **~700K Mistral inferences**.

### 4.6 Evaluation
- **Threshold:** sigmoid cut-off swept 0.05 → 0.95 in steps of 0.01 on dev; one global threshold per task to maximize **macro-F1**.
- **GoEmotions** (58K Reddit, 28 classes): zero-shot eval with π-RoBERTa, also a `π-RoBERTa-fine-tuned` version (3 epochs on GoEmotions train, original splits). Macro-F1.
- **ISEAR** (7,666 self-reports, 7 classes mapped to GoEmotions): **5-fold CV, 80/20 split, 8 epochs, batch 4, max_seq 512**; multi-label.
- **IEMOCAP** (4-class and 6-class): **CORECT** (Nguyen et al. 2023) rebuilt with π-RoBERTa or π-SBERT replacing original SBERT; default CORECT splits/hyperparameters.
- **EmoContext** (SemEval-2019, 4 classes): context-aware π-CRoBERTa, 3 epochs; ablations with/without "others" relabelling + token-type embeddings.
- **Human eval:** **3 postdocs (CS background)** annotated 200 examples. **Cohen's κ = 0.365** (vs Demszky 0.293). **Accuracy = 0.86** on unanimous-agreement subset; **0.70** when ≥2 agree. Annotators picked up to 5 emotions; context revealed by double-click. Rewritten utterances judged less emotional 67/71/92% per annotator (validates rewriting).

### 4.7 Ablations
- **Context-aware vs context-less** (Tables 1, 5): π-CRoBERTaCRewr improves macro-F1 by **+2–3 p.p.** on rewritten+context test (0.72 vs 0.65–0.69), mild degradation on original utterances.
- **Rewriting ablation:** CRewr > COrig when context is needed; worse on self-explanatory utterances.
- **Relabelling ablation** (Table 7, EmoContext): w/o relab 0.81 → w/ relab 0.82 → w/ relab + token-type 0.82.
- **Seed-corpus size scalability:** 2,000 plots → 0.79 F1; 200 plots → 0.77 F1 (intra-dataset, context-aware).
- **Teacher size / taxonomy size ablations: not reported.** Only Mistral-7B-Instruct-v0.2 + 28-class GoEmotions evaluated.

---

## Paper 5 — Sharma et al. (EMNLP 2020) — Computational Empathy in Mental Health Support

*Source: arXiv:2009.08441 (ar5iv HTML + PDF); ACL Anthology page. Full text accessible.*

### 5.1 EPITOME framework / label taxonomy
**Three empathy communication mechanisms**, each on a 3-level ordinal scale (0=no, 1=weak, 2=strong):

- **Emotional Reactions (ER):** "expressing emotions such as warmth, compassion, concern…"
  - *Weak:* alludes to emotion without naming it ("Everything will be fine").
  - *Strong:* names the felt emotion ("I feel really sad for you").
- **Interpretations (IP):** "communicating an understanding of feelings/experiences inferred from the seeker's post."
  - *Weak:* generic ("I understand how you feel").
  - *Strong:* names inferred feeling or shares similar experience ("This must be terrifying").
- **Explorations (EX):** "improving understanding of the seeker by exploring feelings/experiences not stated."
  - *Weak:* generic probe ("What happened?").
  - *Strong:* specific, labeled probe ("Are you feeling alone right now?").

**Annotation protocol.** Crowdworkers shown `(seeker post, response post)` pairs, asked to identify each mechanism **one at a time**, and to highlight rationale spans. 8 crowdworkers trained via 30–60 min phone calls + 50–100 practice posts. **Corpus:** 10,143 (seeker, response) pairs with labels + rationales. **Pairwise Cohen's κ = 0.6865** (each annotator pair shared >50 posts).

### 5.2 Domain-adaptive MLM pre-training
- Base: **RoBERTa-BASE** (12 layers, d=768).
- **Two independent corpora from TalkLife:**
  - S-Encoder corpus: 6.4M seeker posts ≈ **182M tokens**.
  - R-Encoder corpus: 18M response posts ≈ **279M tokens**.
- **MLM, 3 epochs, batch 8.**
- Hardware **4× RTX 2080 Ti**: S-Encoder ≈ 22 h, R-Encoder ≈ 38 h.

### 5.3 Bi-encoder architecture
Two **independent** RoBERTa-BASE encoders (no weight sharing):
```
e_i^(S) = S-Encoder([CLS], S_i, [SEP])
e_i^(R) = R-Encoder([CLS], R_i, [SEP])
```
**Single-head cross-attention fusion.** Q=response, K=V=seeker:
```
a_i(e_i^(R), e_i^(S)) = softmax( e_i^(R) · e_i^(S) / √d ) · e_i^(S),   d=768
```
**Residual sum** forms seeker-aware response rep:
```
h_i^(R) = e_i^(R) + a_i
```
**Param count:** `≈ 2 × 125M (encoders) + 2 × 0.5M (heads) ≈ 251M`.

### 5.4 Two task heads
- **Empathy Identification (EI):** `h_i^(R)[CLS]` → **single linear + softmax** over **3 classes** (no/weak/strong) → `l̂_i ∈ {0,1,2}`. **One model per mechanism** (three separate models for ER, IP, EX), not a single multi-head model.
- **Rationale Extraction (RE):** per-token `h_i^(R)[r_i1,…,r_in]` → **shared linear** → per-token **binary** prediction. **Not BIO tagging**, not span-endpoint regression — just per-token binary CE.

### 5.5 Loss formulation
```
L = λ_EI · L_EI + λ_RE · L_RE
```
with **λ_EI=1, λ_RE=0.5**. Both `L_EI` (3-way CE) and `L_RE` (per-token binary CE). λ_RE chosen via grid search over **{0.1, 0.2, 0.5, 1}** on validation.

### 5.6 Training setup

| Item | Value |
|---|---|
| Fine-tuning LR | **2e-5** (grid `{1e-5, 2e-5, 5e-5, 1e-4, 5e-4}`) |
| Batch size | **32** |
| Epochs | **4** |
| Train/Val/Test | **75 / 5 / 20** of 10,143 pairs |
| Hardware | **1× RTX 2080 Ti** (~5 min fine-tune); MLM pre-train on 4× RTX 2080 Ti |
| λ_EI / λ_RE | 1.0 / 0.5 |

Optimizer name, max seq length, warmup, dropout, weight decay, gradient clipping: not explicitly stated — HF `RobertaForSequenceClassification` defaults (AdamW, 512 tokens, no/0.06 warmup, 0.1 dropout).

### 5.7 Baselines
Seven, all on same 75/5/20 split:
1. Logistic Regression (n-grams)
2. RNN (BiLSTM)
3. HRED (Serban et al.)
4. BERT-BASE
5. GPT-2
6. DialoGPT
7. RoBERTa-BASE (single-encoder, single-task)

**Ablations:** − attention (concat instead), − seeker post (R-Encoder only), − rationales (`λ_RE=0`), − domain-adaptive MLM.

### 5.8 Evaluation metrics
- **EI per mechanism:** accuracy (3 classes) + macro-F1 (3 classes).
- **RE per mechanism:** **token-F1 (T-F1)** + **IOU-F1** (span-level F1 using IOU ≥ 0.5 as TP criterion).
- Reported **separately per mechanism** (ER, IP, EX) and on **two test sets** (TalkLife in-domain, Reddit out-of-domain), not aggregated.

### 5.9 Notes
- Optimizer/seq-length/warmup/dropout/WD not explicitly quoted in paper text — fall back to HF defaults or check the released code: <https://github.com/behavioral-data/Empathy-Mental-Health>.
- RE head is **per-token binary CE**, not BIO — worth highlighting in a methods comparison.
- Trains **3 separate bi-encoders** (one per mechanism), not a single shared backbone with 3 heads — common point of confusion.

---

## Cross-paper methodological table

| Paper | Encoder | Head structure | Multi-task balancing | Loss | Safety/recall constraint | Distillation? |
|---|---|---|---|---|---|---|
| FAIIR | Longformer (149M) ×3 ensemble | Single linear + sigmoid over `[CLS]`, 19 outputs | None (single task, multi-label) | BCE, no class weights; rare-tag oversampling | Threshold = 0.3 for Suicide tag (vs 0.4 / 0.2 for others) | No — human operational silver labels |
| Ghosh et al. (IPM) | BERT/RoBERTa (NRIAS) | Softmax (emotion) + regression (intensity) on shared `[CLS]` + VAD features | Static α·CE + β·MSE (NRIAS values) | Likely CE + MSE | None | No |
| Pathak et al. (CFN) | Transformer encoder (NRIAS) | Shared + per-task private branches → 3 CE heads (disorder / emotion / sentiment) | Static weighted sum; possible orthogonality/adversarial auxiliary (NRIAS) | 3× CE | None | No (semi-supervised silver tags, tool stack NRIAS) |
| Emo Pillars | RoBERTa-large (355M) | Single linear + sigmoid over `[CLS]`, 28 outputs (multi-label) | None (single task) | BCE on hard-thresholded soft labels (≥0.3 → 1) | None | **Yes** — Mistral-7B teacher generates 400K synthetic labels |
| Sharma et al. | RoBERTa-base bi-encoder (2 × 125M ≈ 251M) | EI softmax (3-way) + RE per-token binary, **one model per mechanism** | Static λ_EI=1, λ_RE=0.5 (grid-searched on val) | CE + CE | None | No |

---

## Implications for Pebble's methods design

The methods extraction confirms the **unclaimed intersection** identified in the survey:

1. **Three heterogeneous heads on one shared encoder.** None of the 5 papers does regression + softmax + BCE simultaneously. Ghosh comes closest (CE + MSE) but has no safety BCE; Pathak comes closest (3 CE) but has no regression. **Pebble's MSE + CE + BCE composition is genuinely novel** at this overlap.

2. **Principled task-weight balancing.** All 5 papers use either no weighting, static `α·L₁ + β·L₂`, or grid-searched λ. **None applies Kendall uncertainty weighting or GradNorm to affect classification** — a clean research delta for Pebble.

3. **Safety-recall constraint.** FAIIR is the only paper that operationalizes a safety-critical class, and its only safety-specific mechanism is a **lowered decision threshold (0.3)**. **No paper imposes a recall ≥ 0.95 floor as a training-time objective** (e.g., via constrained optimization, focal loss with high γ, or precision-at-recall surrogates). This is an open methodological gap for Pebble to claim.

4. **Teacher-LLM silver-label distillation for affect.** Emo Pillars is the methodological template, but it does single-task multi-label only. **Pebble extending it to mixed regression + classification + safety with a Gemini teacher** is a clear ACL Findings / WASSA / CLPsych contribution.

5. **Staged freeze/unfreeze.** Sharma et al. has domain-adaptive MLM but no staged freezing; FAIIR has KHP MLM but trains all parameters jointly after. **Pebble's emotion-head warm-start on GoEmotions followed by staged encoder unfreeze is unexplored at this exact configuration** in the surveyed papers — a useful ablation slot but a weaker standalone contribution.

The strongest paper framing remains: **"Distilling a frontier LLM into a NeoBERT student for mental-health affect classification under a hard crisis-recall constraint, with uncertainty-weighted multi-task balancing across regression + classification + safety heads."** Items (1)–(4) all fit cleanly under this title.
