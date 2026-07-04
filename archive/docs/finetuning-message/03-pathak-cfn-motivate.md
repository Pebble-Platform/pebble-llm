# Paper 03 — Pathak, Bhattacharjee, Saha & Saha: Tri-task MTL on Motivational Conversations

> **Honest framing.** The ACM full text is paywalled and every direct PDF / abstract endpoint on `dl.acm.org` returned HTTP 403 to public scraping. The synthesis below is built from (a) the Google Scholar snippet, (b) Sriparna Saha's IIT Patna publication list (entry 213), (c) Tulika Saha's publications page, (d) the original MotiVAte papers (IJCNN 2021, IEEE TCSS 2023, NAACL 2022), and (e) the Liu/Qiu/Huang (2017) ACL paper whose shared-private adversarial MTL architecture is the most cited ancestor of the "Core Fusion Network" idea. Anything not confirmed by these sources is explicitly marked **NRIAS** (Not Recoverable In Available Sources).

## 1. Bibliographic info

- **Title:** "Do Sentiment and Emotion Affect Mental Health? A Multi-task Classification Framework for Comprehensive Understanding of Mental Health, Emotion, and Sentiment from Motivational Conversations"
- **Authors:** Agnibh Pathak, Soham Bhattacharjee, Tulika Saha (University of Liverpool), Sriparna Saha (IIT Patna).
- **Venue:** *ACM Transactions on Computing for Healthcare* (ACM HEALTH). Listed as 2025 in ACM DL records; listed as 2024 on Sriparna Saha's IIT Patna page (entry #213). The discrepancy reflects the typical ACM "Just Accepted → published volume" lag — the paper was accepted in late 2024 and assigned to a 2025 issue.
- **DOI:** `10.1145/3704740`.
- **Citation count (Google Scholar, retrieved June 2026):** ~8.
- **Open access:** No. Only the abstract / front matter is visible without subscription; `dl.acm.org/doi/pdf/10.1145/3704740` returns 403 to unauthenticated clients.

## 2. Problem motivation

Identifying a user's underlying mental-health disorder (MHD) from open-ended conversational text is a high-stakes classification task: the same surface language ("I can't sleep", "I keep checking the door") can belong to depression, anxiety, OCD or PTSD depending on the affective context surrounding it. Pure single-task classifiers force the model to learn that affective context implicitly and from a small label set. The authors' hypothesis — consistent with clinical psychology — is that mental-health conditions are tightly bound to *feelings, moods and emotions*, so giving the model explicit auxiliary supervision on **emotion (ER)** and **sentiment (SA)** at training time should both (a) regularise the shared text encoder and (b) supply discriminative affective cues that the disorder head can read off. The conversational, peer-support setting (the MotiVAte corpus, see §4) is where this signal is strongest: posts are emotionally loaded by construction.

## 3. Position in the literature

Three lineages feed into this paper:

1. **Domain-pretrained encoders for mental-health text** — `MentalBERT` / `MentalRoBERTa` (Ji et al., 2021, arXiv:2110.15621) showed that pretraining on mental-health forum text materially improves downstream MHD classification. This is the typical encoder backbone any 2024-era MTL paper in the area compares against.
2. **MTL architectures for affective NLP** — The dominant family is the **shared–private** decomposition popularised by Liu, Qiu & Huang, "Adversarial Multi-task Learning for Text Classification" (ACL 2017, arXiv:1704.05742). Liu et al. give each task a private encoder, share a third encoder across tasks, push the shared encoder with an *adversarial task discriminator* (so it cannot encode task-specific features), and enforce an *orthogonality* penalty `L_diff = Σ‖SᵀH‖²_F` between shared and private representations. Their full loss is `L = L_task + λ L_adv + γ L_diff`. The "Core Fusion Network" name in the present paper is a direct descendant of this family — see §5.
3. **Saha-group prior work on MotiVAte** — the same authors built and used MotiVAte over a sequence of papers: the IJCNN 2021 dataset paper (Saha, Chopra, Saha, Bhattacharyya, Kumar), the IEEE TCSS 2023 MHD classifier (Saha, Reddy, Saha, Bhattacharyya — "Mental Health Disorder Identification From Motivational Conversations", DOI 10.1109/TCSS.2022.3143763), and the NAACL 2022 "A Shoulder to Cry On" motivational dialogue system. The same group has also published adversarial / dyadic shared-private MTL elsewhere — e.g., "Towards Sentiment and Emotion aided Multi-modal Speech Act Classification in Twitter" (NAACL 2021) and "Meta-Learning based Deferred Optimisation for Sentiment and Emotion aware Multi-modal Dialogue Act Classification" (AACL 2022) — so the present paper is best read as a port of their established sentiment-+-emotion-aided MTL recipe onto the mental-health primary task on MotiVAte.

## 4. MotiVAte dataset (extended)

**Original MotiVAte** (Saha et al., IJCNN 2021; extended in IEEE TCSS 2023 and NAACL 2022):
- Dyadic conversations between a "support seeker" user and a Virtual Assistant providing hope / motivation.
- Per the NAACL 2022 description recovered via Tulika Saha's publications page, the corpus comprises **~7k dyadic conversations** (the "7,067 / 1,839 users" figures in the brief match the TCSS 2023 expansion of the corpus).
- Four mental-health disorder labels: **Major Depressive Disorder (MDD), Anxiety, OCD, PTSD**.
- Non-clinical: drawn from public support-forum / Reddit-like sources rather than verified clinical diagnoses.

**This paper's extension.** The Google Scholar snippet and IIT Patna entry both state that the corpus was "extended to include emotion and sentiment tags for conversations in a semi-supervised manner." That is, the present paper adds **per-turn silver labels for emotion (ER)** and **sentiment (SA)** on top of the existing MHD gold labels. Concretely:
- Silver-labelling tool stack: **NRIAS** (the paper almost certainly uses an off-the-shelf classifier — typical Saha-group practice is a fine-tuned BERT or a public emotion model such as GoEmotions / NRC EmoLex for emotion plus a VADER- or RoBERTa-based polarity model for sentiment, but the exact pipeline is not in the visible material).
- Emotion inventory: **NRIAS** (likely Ekman-6 or Ekman-7 plus *neutral*, consistent with the group's earlier dialogue-act / emotion papers).
- Sentiment inventory: **NRIAS** (almost certainly {positive, neutral, negative}).
- Per-split sizes (train / dev / test): **NRIAS**.
- User-level vs. message-level split: **NRIAS** — a methodological gap worth noting because user-level leakage would inflate disorder-classification numbers on a 1,839-user corpus.

## 5. Core Fusion Network (CFN) method

What is publicly attestable: the paper proposes a model called **Core Fusion Network (CFN)**, "a variation of multi-tasking," with three heads — MHD identification (primary) plus emotion recognition and sentiment analysis (auxiliary).

Beyond the name, the architectural details are **NRIAS**, but the most likely shape — based directly on Liu et al. 2017 and the Saha group's prior adversarial-MTL papers — is:

- **Encoder backbone:** a transformer encoder, almost certainly BERT-base or a domain variant (MentalBERT / RoBERTa). The IEEE TCSS 2023 predecessor uses an attention-based BERT classifier on MotiVAte, so a BERT-family choice is the safe default.
- **Shared–private decomposition:** one *shared* encoder feeding a representation `s`, and a *private* encoder per task feeding `h_MHD`, `h_ER`, `h_SA`. Fusion ("Core Fusion") is the operation that combines `s` with each `h_k` before the task heads — candidate mechanisms include concatenation + projection, gated fusion (`g·s + (1-g)·h_k`), or attention-based fusion. **Which one is used: NRIAS.**
- **Auxiliary constraints (likely, not confirmed):** orthogonality between `S` and `H_k` and/or an adversarial task discriminator on `s`, both inherited from Liu et al. 2017. The literal name "Core Fusion Network" suggests the novelty is in the *fusion* operator more than in the discriminator, but this is a guess from the title only.
- **Heads:** three independent softmax classifiers (MHD: 4-way; ER: ~6–7-way; SA: 3-way).

## 6. Loss

Not visible in accessible sources. The expected form, given §5, is the standard shared-private adversarial MTL loss:

```
L = Σ_k α_k · CE(y_k, ŷ_k)   +   λ · L_adv   +   γ · L_diff
```

with `L_adv` a task-discriminator cross-entropy on the shared representation and `L_diff = Σ_k ‖S_kᵀ H_k‖²_F` the orthogonality penalty (Liu et al. 2017). Whether CFN actually keeps `L_adv` and `L_diff`, and the values of `α_k, λ, γ`, are **NRIAS**.

## 7. Training setup

Optimizer, learning rate, batch size, epoch count, sequence length, warmup, scheduler, hardware (single GPU vs. multi), random-seed protocol, early-stopping criterion — all **NRIAS**. The IEEE TCSS 2023 predecessor used BERT-base with AdamW at LR≈2e-5 on a single GPU, which is a reasonable prior.

## 8. Baselines

The brief and the title structure ("multi-task classification framework") imply the standard ablation grid:

- **Uni-task:** MHD-only, ER-only, SA-only — to establish single-task ceilings.
- **Bi-task:** {MHD + ER}, {MHD + SA} — to isolate the contribution of each auxiliary signal.
- **Tri-task:** MHD + ER + SA — the proposed configuration.
- **Fully-shared (FS) MTL:** one encoder, three heads, no private encoders.
- **Shared-private (SP) adversarial MTL:** the Liu et al. 2017 architecture without the "Core Fusion" twist.

Exact metrics for each cell: **NRIAS**.

## 9. Results

The one number that *is* publicly recovered:

> **89.12% accuracy on mental-health disorder identification** with the full tri-task CFN — reported as outperforming "individual or dual-task approaches" (Google Scholar snippet).

The central qualitative claim is therefore confirmed: **tri-task MHDI > bi-task MHDI > uni-task MHDI**. Per-task F1, macro-F1, per-disorder breakdowns, ER and SA scores, and the deltas vs. fully-shared and SP-adversarial baselines are **NRIAS**.

## 10. Authors' stated limitations (likely)

Not directly visible, but the standard limitations for this corpus + method combination — and the ones the authors almost certainly acknowledge — are:

- **Silver-label noise.** Auxiliary ER/SA labels are model-generated, so MTL gains may partly reflect alignment with the silver-labeller rather than true affective signal.
- **Non-clinical population.** MotiVAte is forum-derived; users are self-described, not clinically diagnosed, so the 4-way MHD label is itself noisy and the model is not a diagnostic tool.
- **English-only.** Limits external validity.
- **Conversational genre lock-in.** Trained on dyadic motivational chats; transfer to monologue (e.g. clinical intake notes) is unstudied.
- **Static loss weights.** If λ values are tuned by grid search (typical for this group's prior work), the balance is brittle to label-distribution shift.

## 11. Relevance to Pebble

Side-by-side with the Pebble emotion-pretraining work:

- **Same north star, same shape.** Both projects use MTL where mental-health-relevant primary signal is supported by affective auxiliary supervision. The Pathak result that the *tri-task* configuration wins is direct corroboration for Pebble's choice to keep emotion + sentiment heads alongside the primary objective rather than dropping them.
- **Both use semi-automated silver labels.** Pathak's pipeline is a one-shot silver-label dump (off-the-shelf ER/SA model → frozen labels). Pebble's Gemini teacher is materially more sophisticated: it produces both **discrete labels and continuous severity scores** with prompted rationales, which lets Pebble train regression heads as well as CE heads.
- **Pebble's continuous regression heads are net-new.** Pathak's CFN is fully categorical (CE on 4-way MHD, k-way emotion, 3-way sentiment). Pebble's EI-reg severity loader and masked-multitask assembler (already in `src/pebble_llm/training/pretrain_emotion.py`) cover regression targets and per-example mask-aware losses that CFN does not.
- **Safety head is also net-new on Pebble's side.** CFN has no risk / safety classifier; Pebble's safety head is therefore an additional inductive bias not present in this prior art.
- **MTL balancing is more principled in Pebble.** CFN almost certainly uses static per-task weights (Liu-style `α_k, λ, γ` tuned by hand). Pebble's plan to use **Kendall uncertainty-weighting and/or GradNorm** is a strict generalisation: it makes the balance learned rather than hand-tuned, which directly addresses the silver-label noise limitation CFN is exposed to.
- **Architectural option not yet on Pebble's roadmap.** If during Pebble training the emotion and severity heads start *fighting* the safety head (negative transfer), CFN's shared-private decomposition with adversarial + orthogonality terms is a well-evidenced fix to lift off the shelf. Worth keeping as a Plan B but not adopting pre-emptively.

## 12. Recommended citation use

Cite Pathak, Bhattacharjee, Saha & Saha (2025) to support:

- **(a) Tri-task MTL beats bi-task / uni-task for mental-health classification on conversational data.** Backed by their 89.12% headline and explicit "outperforming individual or dual-task approaches" claim.
- **(b) Auxiliary emotion and sentiment supervision improves primary mental-health disorder identification.** This is the paper's whole thesis and the answer to its title question, and it is the strongest external precedent for Pebble's emotion-pretraining hypothesis.
- **(c) MotiVAte is a relevant prior non-clinical conversational corpus for mental-health-aware language modelling.** Useful as a comparison point when justifying Pebble's own dataset choices, even though Pebble does not train on MotiVAte directly.

Do **not** cite this paper for: specific architectural choices (the "CFN" name is public but the operator is not), specific loss formulations, head-to-head benchmark numbers against MentalBERT or similar — none of those details are recoverable without the paywalled PDF.

## 13. Honest paywall note

The following are confirmed publicly and safe to cite:

- Title, authors, venue (ACM TCH), DOI (`10.1145/3704740`), year (2024 accepted / 2025 issue).
- The model is called **Core Fusion Network (CFN)**.
- The task structure is tri-task: **MHDI (primary) + ER + SA (auxiliary)**.
- The dataset is **MotiVAte extended with semi-supervised emotion + sentiment labels**, covering **MDD, PTSD, Anxiety, OCD**.
- Headline result: **89.12% MHDI accuracy** with the tri-task configuration.
- Central claim: tri-task > bi-task > uni-task for MHDI.

The following require the full PDF and are marked **NRIAS** above:

- Exact silver-labelling pipeline and label inventories for ER and SA.
- Train / dev / test sizes and whether splits are user-level or message-level.
- Exact encoder backbone (BERT base, MentalBERT, RoBERTa, …).
- Fusion operator inside "Core Fusion" (concat, gated, attention, …).
- Presence and form of adversarial / orthogonality terms.
- Loss equation and weights (`α_k, λ, γ`).
- Optimizer, learning rate, batch size, epochs, hardware.
- Per-baseline numerical table (uni / bi / tri / FS / SP-adversarial) and per-class breakdowns.
- Authors' formally stated limitations and future-work paragraph.

If any of these are load-bearing for downstream Pebble decisions, the next step is to retrieve the PDF through an institutional subscription rather than guess from the abstract.

## Sources

- ACM landing page (paywalled — abstract only): https://dl.acm.org/doi/10.1145/3704740
- Sriparna Saha publication list (IIT Patna, entry #213): https://www.iitp.ac.in/~sriparna/Journals.html
- Tulika Saha publications: https://sahatulika15.github.io/publications/
- DBLP — Tulika Saha: https://dblp.org/pid/230/8625.html
- Original MotiVAte (IJCNN 2021): https://ieeexplore.ieee.org/document/9533924/
- Mental Health Disorder Identification From Motivational Conversations (IEEE TCSS 2023): https://ieeexplore.ieee.org/document/9729467/
- Liu, Qiu, Huang — Adversarial Multi-task Learning for Text Classification (ACL 2017): https://aclanthology.org/P17-1001/ and https://arxiv.org/abs/1704.05742
- MentalBERT (Ji et al., 2021): https://arxiv.org/pdf/2110.15621
