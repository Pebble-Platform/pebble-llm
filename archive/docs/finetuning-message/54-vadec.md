# Paper 54 — VADEC: Joint Categorical Emotion Classification + Continuous VAD Regression on Tweets

> Topic-anchor for "analyze user messages for emotional tone (positive↔negative)". The closest published design to Pebble's mixed categorical+continuous affect MTL head structure. Analysis depth: abstract + author page + official GitHub + SIGIR program (PDF body not text-extractable in this environment). Compiled 2026-06-26.

## Bibliographic info

- **Title:** Understanding the Role of Affect Dimensions in Detecting Emotions from Tweets: A Multi-task Approach (the framework is named **VADEC**)
- **Authors:** Rajdeep Mukherjee, Atharva Naik, Sriyash Poddar, Soham Dasgupta, Niloy Ganguly
- **Affiliation:** IIT Kharagpur (Department of CSE)
- **Venue / Year:** SIGIR 2021 — 44th International ACM SIGIR Conference on Research and Development in Information Retrieval (short paper)
- **Links:** [arXiv:2105.03983](https://arxiv.org/abs/2105.03983) · [ACM DL 10.1145/3404835.3463080](https://dl.acm.org/doi/10.1145/3404835.3463080) · [code (GitHub atharva-naik/VADEC)](https://github.com/atharva-naik/VADEC) · [author post](https://rajdeep345.github.io/posts/2021/07-c04-sigir21)
- **Status:** arXiv open; code + datasets released. PDF body could not be text-extracted in this environment (binary stream), so architecture/loss details below are triangulated from the abstract, the author's project page, the SIGIR program, and the README — flagged where unverified.

## Summary

VADEC co-trains two heads on a **single shared BERTweet encoder** (a RoBERTa-base architecture, ~135M params, pre-trained on ~850M tweets): (1) a **multi-label emotion classifier** (EC) over categorical emotions, and (2) a **multi-dimensional emotion regressor** (VADR) predicting continuous **Valence / Arousal / Dominance**. Trained separately these are EC and VADR; trained jointly with a summed loss they become **VADEC**, which "exploits the correlation between the categorical and dimensional models of emotion representation." The headline finding is that **co-training mainly helps the classification head**: +3.4% Jaccard, +11% Macro-F1, +3.9% Micro-F1 on SemEval-2018 AIT over the strongest single-task baseline, +11.3% avg across six metrics on SenWave, and +7.6% (Valence) / +16.5% (Dominance) Pearson on EmoBank for the regression side. The continuous VAD signal acts as an affective scaffold that sharpens discrete emotion prediction.

## Overlap with Pebble — 38% (peripheral)

`D1=2, D2=0, D3=1, D4=0, D5=1, D6=0, D7=1` → (3·2 + 2·0 + 1·1 + 2·0 + 2·1 + 2·0 + 1·1)/26 = 10/26 = **38%**

| # | Dimension | Score | Why |
|---|-----------|-------|-----|
| D1 | Heterogeneous heads (categorical + continuous) | **2** | Multi-label emotion classifier + continuous VAD regressor on one shared encoder — the *exact* shape of Pebble's emotion head + continuous valence/energy head. No safety head, so not a 3-head match, but the cat+continuous core is a direct, strong hit. |
| D2 | Mental-health / crisis domain | **0** | General Twitter affect; no MH, support, or crisis framing. |
| D3 | Emotion-transfer corpora | **1** | SemEval-2018 AIT (EI/V-reg), EmoBank, SenWave — real affect/intensity corpora, but not GoEmotions / EmpatheticDialogues. Partial. |
| D4 | Teacher-LLM silver-label distillation | **0** | None; all gold/human-annotated. |
| D5 | Principled MTL loss balancing | **1** | Joint loss explicitly exploits cross-task correlation, but weighting is static/empirical (summed task losses), not uncertainty/GradNorm/PCGrad. Partial. |
| D6 | Safety/crisis recall constraint | **0** | None. |
| D7 | Encoder backbone match | **1** | BERTweet = RoBERTa-base *family* (Pebble's class), but ~135M vs Pebble's ~250M, and tweet-pretrained rather than NeoBERT/ModernBERT. Same lineage, smaller. Partial. |

**Closest on:** **D1** (the cleanest published instance of Pebble's categorical-emotion + continuous-affect two-head design on a shared transformer) and secondarily **D5** (it demonstrates the cross-task-correlation benefit Pebble is betting on, just with static weighting).

**Band note:** the 38% "peripheral" number understates leverage. Like the Kendall paper (06), this is a *method/design* match on Pebble's single most load-bearing architectural choice — the zeros on MH/crisis, distillation, and safety drag the weighted score down even though the head-structure transfer is near-perfect.

## Best point — Method to adopt (with a baseline-to-beat flavor)

VADEC's central, well-evidenced result is that **a continuous affect-dimension regressor co-trained with a categorical emotion classifier on a shared encoder measurably improves the categorical head** (+11% Macro-F1 on AIT) — i.e. the continuous valence signal is not just a parallel output, it is a *productive auxiliary* for emotion classification, and the gain flows mainly *into* the classifier.

- **How to apply to Pebble:** Wire Pebble's continuous valence/energy head and the GoEmotions emotion head onto the **same `[CLS]` trunk and co-train them with a joint loss from the start** (rather than training emotion alone and bolting valence on later) — then run the VADEC ablation as your in-house sanity check: emotion-only vs. emotion+valence co-trained, and confirm GoEmotions Macro-F1 *rises* under co-training. Use BERTweet/VADEC's AIT and EmoBank numbers as the **published baseline-to-beat for the cat+VAD design itself**, but expect Pebble to win on backbone (NeoBERT ~250M vs BERTweet ~135M) and on principled loss weighting (Kendall, paper 06) where VADEC uses a static sum. Adopt the *design*; beat the *weighting*.

## Dataset

- **SemEval-2018 Task 1 "Affect in Tweets" (AIT)** — multi-label emotion classification (E-c) + V-reg/EI-reg; English; open via the SemEval task page. Already on Pebble's radar (EI-reg).
- **EmoBank** — ~10k sentences with continuous VAD (reader/writer perspective); CC-BY; open. The standard cat↔VAD bridge corpus; **a strong candidate to hand to `find-dataset`** if Pebble wants a gold continuous-valence eval set to validate its valence head against a published Pearson number.
- **SenWave** — COVID-era tweet emotion corpus (gated/registration in places — verify license before use).
- VADEC's own code + preprocessed splits are public on GitHub.

## Caveats

- **PDF body not machine-readable in this environment.** The two-head architecture, BERTweet backbone, dataset list, and headline gains are corroborated across the abstract, author project page, SIGIR program, and README; but the **exact loss formulation, task-weighting scheme, and whether the regressor is one head over 3 VAD dims or three heads** were inferred (best-effort) and should be confirmed against the PDF/code before any reimplementation. The D5=1 score assumes static summed weighting (consistent with all visible descriptions) — if the full paper reveals a principled weighter, D5 would rise to 2 (→ 42%).
- **Domain gap is real.** Tweets ≠ multi-turn mental-health support dialogue, and there is **no safety/crisis head and no distillation** — do not cite VADEC for D2/D4/D6. It is a precedent for the *affect-head structure*, not for Pebble's safety or teacher-LLM story.
- **Backbone is smaller and tweet-specific.** BERTweet's tweet pretraining is part of *why* it wins on Twitter; Pebble's NeoBERT lacks that in-domain prior, so the absolute AIT gains are not directly portable — treat VADEC's numbers as a design-validation reference, not a target Pebble must literally exceed on AIT.

## Recommended use for Pebble

- **Method to adopt:** co-train categorical emotion + continuous valence on the shared `[CLS]` trunk; expect (and verify) the classifier to benefit.
- **Framing / citation:** the cleanest published precedent for "categorical emotion + continuous affect in one transformer," and the right anchor for Pebble's emotional-tone (positive↔negative) story.
- **Baseline to beat (design-level):** VADEC's EC-vs-VADEC ablation is the experiment Pebble should reproduce internally; Pebble's intended advances over it are the larger NeoBERT backbone, the added safety head, teacher-LLM distillation, and principled MTL weighting.

## Sources

- [arXiv:2105.03983](https://arxiv.org/abs/2105.03983)
- [ACM DL 10.1145/3404835.3463080](https://dl.acm.org/doi/10.1145/3404835.3463080)
- [GitHub: atharva-naik/VADEC (code + datasets)](https://github.com/atharva-naik/VADEC)
- [Author project post (Rajdeep Mukherjee)](https://rajdeep345.github.io/posts/2021/07-c04-sigir21)
- [SIGIR 2021 accepted papers](https://sigir.org/sigir2021/accepted-papers/)
