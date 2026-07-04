# Paper 05 — Sharma et al.: Computational Empathy in Text-Based Mental Health Support

## 1. Bibliographic Info

**Title.** "A Computational Approach to Understanding Empathy Expressed in Text-Based Mental Health Support."

**Authors and affiliations.** Ashish Sharma (Paul G. Allen School of Computer Science & Engineering, University of Washington), Adam S. Miner (Department of Psychiatry and Behavioral Sciences, Stanford University; Center for Biomedical Informatics Research, Stanford), David C. Atkins (Department of Psychiatry and Behavioral Sciences, University of Washington), and Tim Althoff (Paul G. Allen School of Computer Science & Engineering, University of Washington). The author list is a deliberate UW-NLP × Stanford-psychiatry collaboration, mixing NLP modeling expertise (Sharma, Althoff) with clinical psychology and behavioral health expertise (Miner, Atkins).

**Venue and year.** EMNLP 2020, pages 5263–5276 of the main conference proceedings. DOI `10.18653/v1/2020.emnlp-main.425`. Available at `https://aclanthology.org/2020.emnlp-main.425/` and as arXiv `2009.08441` (submitted September 17, 2020).

**Code and data.** Code is released at `https://github.com/behavioral-data/Empathy-Mental-Health` under the `behavioral-data` org. The repo ships `process_data.py`, `train.py`, `test.py`, and the EPITOME annotated dataset CSV (the Reddit half is released directly; the TalkLife half is gated behind a data-use agreement because of TalkLife's ToS).

**IRB / ethics note.** The authors explicitly obtained IRB approval from both UW and Stanford, and the paper devotes an Ethics section to data licensing (TalkLife DUA), participant safety, and the deliberate framing of "expressed empathy" as a research construct rather than a clinical diagnosis. The TalkLife corpus is not redistributed; only Reddit text appears in the public release.

## 2. Problem Motivation

Text-based peer support platforms (TalkLife, 7 Cups, Reddit mental-health subreddits, Crisis Text Line, etc.) are the largest *de facto* mental-health resource in existence, especially for people who cannot access or afford clinical care. Yet the supporters on these platforms are typically untrained volunteers, and there is a well-documented gap between volunteer supporter quality and the empathy levels demonstrated by clinically-trained therapists. The paper opens by framing this gap as both a public-health problem (poor-quality peer support can fail or even harm vulnerable seekers) and an NLP opportunity (high-volume text logs are amenable to automated quality assessment).

The authors argue that empathy is the single most important active ingredient in talk therapy and peer support — but virtually all prior empathy measurement instruments were developed for face-to-face, synchronous, audio-visual settings (Truax-Carkhuff scales, multi-dimensional psychological self-report scales). These transfer poorly to short, asynchronous, text-only messages. The goal of the paper is therefore (a) to operationalise *textual* empathy with a clinically-grounded but text-native rubric, (b) to build a dataset and model that can score peer responses automatically, and (c) to demonstrate that the system can be wired into a real feedback loop that helps supporters improve.

## 3. Position in the Literature

The paper sits at the intersection of three streams. First, prior NLP work on empathy and affect: Buechel et al. (2018) released a dataset of news-reaction *distress* and *empathy* annotations, and Sharma & Cohan (2018) studied multidimensional aspects of empathy in online support, but neither operationalised the *mechanisms* by which a responder expresses empathy in a single turn. Second, prior work on peer-support platforms: Althoff, Clark & Leskovec (2016) showed counsellor strategies on Crisis Text Line predict conversation outcomes; De Choudhury & De (2014/2016) characterised mental-health subreddit dynamics; Zhang & Danescu-Niculescu-Mizil studied therapeutic alliance markers. Third, prior TalkLife-specific analyses by Sharma & Althoff. The paper's main contribution against this backdrop is the introduction of EPITOME, the first text-native, multi-mechanism, ordinal empathy rubric paired with a public corpus and a baseline model.

## 4. EPITOME Framework

EPITOME ("Empathy in Text-based, asynchronous Peer-to-peer support OutcoMEs") decomposes the empathy expressed by a supporter response into three orthogonal communication mechanisms, each scored on an ordinal three-level scale {0 = no, 1 = weak, 2 = strong}. The framework is drawn from third-wave clinical empathy theory (Elliott et al., Watson) but recast for text.

- **Emotional Reactions (ER).** Does the response express warmth, compassion, concern, or felt emotion? *Weak* = alludes ("Everything will be fine"); *Strong* = explicit emotional state ("I feel really sad for you"). ER captures the affective channel.
- **Interpretations (IP).** Does the response communicate cognitive understanding of what the seeker is feeling or going through? *Weak* = generic acknowledgement ("I understand how you feel"); *Strong* = specifying the inferred emotion ("This must be terrifying") or relating a similar lived experience. IP captures the cognitive channel.
- **Explorations (EX).** Does the response actively probe feelings the seeker has not stated? *Weak* = generic prompt ("What happened?"); *Strong* = a specific, labelled probe ("Are you feeling alone right now?"). EX captures the active-listening channel.

This decomposition departs from the older Truax-Carkhuff single-axis empathy scale and from the multi-dimensional self-report psychological scales (IRI, etc.) in three ways: (i) it is *behavioural* — it scores what the message *does*, not the responder's traits; (ii) it is *multi-mechanism* — a single response can be strong on ER, weak on IP, and absent on EX; and (iii) it is *text-native* — every level is defined with text exemplars.

## 5. Dataset Construction

The released EPITOME dataset contains **10,143 (seeker post, response post) pairs**, each annotated with three ordinal empathy labels (one per mechanism) *and* with rationale spans — the exact substrings of the response that justify the label. This dual annotation is unusual: most affect datasets give a label only.

Data come from two platforms. **TalkLife** (in-domain, mobile peer-support app for mental health) supplied 7,062 pairs sampled from a corpus of ~6.4M threads / 18M interactions. **Reddit** supplied 3,081 pairs drawn from **55 mental-health subreddits** (r/depression, r/anxiety, r/SuicideWatch, etc.), totalling ~1.6M threads / 8M interactions — used as an out-of-domain transfer set. Pairs were stratified to avoid mechanism imbalance.

Annotation was performed by **eight crowdworkers** trained intensively: each completed a 30–60 minute onboarding phone call with the authors plus 50–100 practice posts with iterative written feedback before producing production labels. Each pair received at least two independent annotations; disagreements were adjudicated. The resulting **Cohen's κ = 0.6865 (average pairwise)**, slightly above the 0.60 typical of in-person therapy-empathy coding studies, which the authors flag as evidence that text empathy is at least as reliably annotatable as audio empathy when the rubric is text-native.

## 6. Domain-Adaptive MLM Pre-training

Because off-the-shelf RoBERTa was trained on news/books/Wikipedia and is a poor fit for the register of mental-health peer support, the authors run a domain-adaptive masked-LM continued-pretraining phase on **two separate encoders**.

- **S-Encoder (seeker side).** Continued MLM on a corpus of **6.4M seeker posts ≈ 182M tokens**, 3 epochs, batch size 8, on 4× RTX 2080 Ti GPUs, ≈ **22 hours**.
- **R-Encoder (response side).** Continued MLM on **18M response posts ≈ 279M tokens**, 3 epochs, batch size 8, on 4× RTX 2080 Ti GPUs, ≈ **38 hours**.

Both start from RoBERTa-base (125M params). The split is motivated by a register difference: seeker posts are first-person, disclosure-heavy, and emotionally raw, while response posts are second-person, supportive, and often advice-shaped. Two encoders let each side specialise instead of averaging the two registers in one model.

## 7. Bi-encoder Architecture

The fine-tuning model is a cross-attentive bi-encoder. Given a seeker post `S` and a response post `R`:

```
e^S = S-Encoder([CLS], S, [SEP])               (1)
e^R = R-Encoder([CLS], R, [SEP])               (2)
a(e^R, e^S) = softmax(e^R · e^S^T / √d) · e^S   (3)   d = 768
h^R = e^R + a(e^R, e^S)                        (4)   residual
```

Each encoder produces 768-dim token embeddings. A single scaled dot-product cross-attention layer lets each response token attend over the seeker tokens (query = response, keys/values = seeker), producing a seeker-context-aware response representation `h^R`. The residual addition preserves the raw response signal.

Total parameter count is **≈ 251M** — two 125M RoBERTa-base encoders plus a thin cross-attention layer and the task heads. The architecture is intentionally asymmetric: the seeker encoder is read-only (no gradients flow back into its task head because there isn't one); only `h^R` feeds the prediction heads.

## 8. Task Heads

Two heads sit on top of `h^R`.

- **Empathy Identification (EI).** A linear projection from the `[CLS]` row of `h^R` to a 3-way softmax over {no, weak, strong}. Crucially the authors train **one model per mechanism**, so three EI heads exist across three separate fine-tuned models (ER-model, IP-model, EX-model), not a single shared head. This keeps each mechanism's loss surface clean.
- **Rationale Extraction (RE).** A *shared* linear projection from each response-token row of `h^R` to a per-token sigmoid, optimised with binary cross-entropy. Rationale tokens are positives, non-rationale tokens are negatives. **It is not BIO tagging** — there are no B-/I-/O- tags and no span decoder; tokens are scored independently and contiguous positives form a span at inference.

## 9. Loss

Multi-task scalar-weighted sum:

```
L = λ_EI · L_EI + λ_RE · L_RE
```

with **λ_EI = 1** and **λ_RE = 0.5**. λ_RE was selected by grid search over **{0.1, 0.2, 0.5, 1}** on the dev set; 0.5 won across mechanisms. This is a static-weight multi-task setup — no uncertainty weighting (Kendall), no GradNorm, no PCGrad.

## 10. Training Setup

- **Optimiser / LR.** AdamW (HuggingFace default), learning rate **2e-5**, selected from a small grid; weight decay and warmup at HF defaults.
- **Batch size.** 32.
- **Epochs.** 4.
- **Sequence length.** 512 in the paper (the released repo defaults `max_seq_len = 64` for speed; users override).
- **Dropout.** 0.1.
- **Seed.** 12 (released code).
- **Split.** **75 % train / 5 % dev / 20 % test** of the 10,143 labelled pairs, stratified per mechanism.
- **Hardware / time.** Single RTX 2080 Ti, ≈ **5 minutes** per fine-tune (the heavy compute is the one-off MLM stage in §6).

## 11. Baselines

Seven external baselines plus four targeted ablations:

External baselines: (1) **Logistic Regression** on tf-idf, (2) a 2-layer **RNN**, (3) **HRED** (hierarchical recurrent encoder-decoder, conversation-aware), (4) **BERT-base**, (5) **GPT-2**, (6) **DialoGPT**, (7) vanilla **RoBERTa-base**. Each baseline is run per mechanism and per task wherever applicable.

Ablations: (a) **− attention** (drop the cross-attention layer), (b) **− seeker post** (response-only input, removes the bi-encoder altogether), (c) **− rationales** (single-task EI, λ_RE = 0), (d) **− MLM** (skip domain-adaptive pretraining and start from off-the-shelf RoBERTa).

## 12. Evaluation Metrics

- **EI.** Accuracy and macro-F1 over the three ordinal classes. Macro-F1 is the headline number because the *strong* class is the minority.
- **RE.** Token-level F1 plus **IOU-F1**, where a predicted span counts as a true positive if its intersection-over-union with a gold span is ≥ 0.5. IOU-F1 rewards roughly-right spans even when boundaries jitter.

All metrics are reported per mechanism (ER / IP / EX) and per platform (TalkLife / Reddit).

## 13. Results

**EI on TalkLife (accuracy / macro-F1).** ER: 79.93 % / 74.29 %. IP: 87.50 % / 67.46 %. EX: 86.92 % / 73.47 %. The bi-encoder beats vanilla single-task RoBERTa by roughly **+4 macro-F1** on average across mechanisms, with the largest gains on the harder ER mechanism.

**RE on TalkLife (token-F1 / IOU-F1).** Token-F1 lands in the 0.64–0.68 range; IOU-F1 is **0.6682 (ER) / 0.8576 (IP) / 0.8319 (EX)** — comfortably above the 0.50 IOU threshold for most spans, indicating the model recovers rationale chunks even when token boundaries differ.

**Cross-domain transfer to Reddit.** All models degrade out-of-domain, but the EPITOME bi-encoder degrades **less** than the seven baselines on both EI macro-F1 and RE IOU-F1, which the authors attribute to (i) the cross-attention forcing the model to use seeker semantics rather than memorising surface response cues, and (ii) the domain-adaptive MLM corpus including both TalkLife and Reddit registers in spirit (peer-support English).

**Ablations.** Dropping the cross-attention is the **largest** single hit (macro-F1 falls 2.0–8.4 points depending on mechanism). Removing MLM pretraining is the **second-largest** hit. Removing the rationale auxiliary task (− rationales) costs ~1–2 macro-F1 — small but consistent across mechanisms and "free" since rationales are already annotated. Removing the seeker post drops RE IOU-F1 by 5–6 points.

## 14. Application Analyses

The trained models are then turned loose on **~235,000 TalkLife interactions** to characterise the platform.

- Only **~10 %** of TalkLife responses qualify as *strong* on any mechanism — i.e. the modal peer response is supportive in form but weak in empathy.
- The **average total EPITOME score is 1.09 out of 6**, again confirming that volunteer responses cluster near the low end.
- Supporters do *not* naturally improve over time: emotional-reactivity scores fell **36 %** over a three-year window for repeat supporters.
- Strong-empathy responses receive **45 %** more "likes" from seekers and a **79 %** higher follow-up rate, suggesting seekers can tell the difference.
- Female-to-female interactions are **32 %** more empathic on average than male-to-male.
- Reddit subreddits are more mixed than TalkLife — they contain more advice-shaped and less reaction-shaped responses.

A small proof-of-concept feedback prototype was tested with **three participants**, whose mean total EPITOME score rose from 0.8 to 3.0 after using the templated feedback (mean usefulness rating 3.5 / 5).

## 15. Authors' Stated Limitations

The authors are unusually candid: (1) the framework scores **expressed**, not **perceived**, empathy — there is no seeker self-report channel; (2) IAA at κ ≈ 0.69 is *moderate*, not strong, and short emotional expressions remain hard to classify; (3) the rubric and corpus are English-only and skewed toward US/UK-style peer-support norms; (4) the proof-of-concept involved only **3 participants**, so the feedback-system claims are exploratory; (5) deploying any automated feedback in a real mental-health setting without clinical validation is risky and out of scope; (6) the model cannot distinguish empathic-but-incorrect from empathic-and-correct interpretations.

## 16. Relevance to Pebble

This paper is the closest direct ancestor of Pebble's empathy-classification ambitions, and the overlap and gaps are both informative.

- **Shared problem space.** Both projects classify peer-support-style mental-health text; both treat empathy as multi-mechanism rather than scalar; both use TalkLife as a planned or actual data source (Pebble lists TalkLife behind a DUA caveat).
- **Architecture.** EPITOME's bi-encoder + cross-attention is **overkill for Pebble's input shape**, which is a single message plus up to three context messages rather than a structured (seeker, response) pair. A single shared encoder with prepended context tokens or short positional segments is a better fit; the seeker/response asymmetry that motivates EPITOME's bi-encoder simply does not exist in Pebble.
- **Multi-task structure.** EPITOME's MTL is structurally simple (3 mechanisms × {EI, RE} = same head shape repeated) while Pebble's MTL is **heterogeneous** (ordinal EI severity, multi-label emotion, valence/arousal regression, etc.). The EPITOME static-λ recipe (λ_EI=1, λ_RE=0.5 from a 4-point grid) is exactly the static-weight baseline Pebble plans to challenge with Kendall uncertainty weighting and GradNorm.
- **Domain-adaptive MLM.** EPITOME's 22 h + 38 h continued-MLM regime is something Pebble could layer on top of NeoBERT's RefinedWeb pretraining if a peer-support text dump is available; the result here (− MLM is the second-largest ablation hit) is a strong argument for doing so.
- **Annotation scale.** 10,143 pairs at κ ≈ 0.69 with 8 crowdworkers is a realistic ceiling for what Pebble can replicate in-house and is a reasonable budget target.

## 17. Recommended Citation Use

Cite Sharma et al. 2020 to support the following claims:

(a) **Multi-task loss with a rationale auxiliary improves empathy classification.** Their ablation shows − rationales costs ~1–2 macro-F1 across mechanisms while requiring no extra labelled data when rationales are already annotated.

(b) **Domain-adaptive MLM pre-training on peer-support text boosts performance.** − MLM is their second-largest ablation hit, behind only − attention.

(c) **Static-λ grid search is the state-of-practice baseline for multi-task affect.** Their headline numbers come from a λ-grid as small as {0.1, 0.2, 0.5, 1} with no adaptive weighting — exactly the baseline that uncertainty-weighting / GradNorm methods should be compared against.

(d) **~10K annotated pairs is small but workable when paired with strong transfer.** EPITOME hits ≈ 80 % accuracy and 0.67–0.74 macro-F1 on a three-class ordinal problem with only 10,143 labelled pairs, by leaning on RoBERTa + domain MLM + cross-attention — a useful precedent for Pebble's own data-scale planning.

(e) **Volunteer peer empathy is genuinely scarce** (~10 % strong responses on TalkLife; mean EPITOME 1.09 / 6) — a population-level statistic worth quoting to motivate automated empathy feedback as a research direction.
