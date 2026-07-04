# Related Work — Voice & Multimodal Affect *(stress-from-speech extension)*

> **Purpose.** Companion to [`related-work-survey.md`](./related-work-survey.md) and
> [`related-work-enrichment.md`](./related-work-enrichment.md). This set covers the **new voice
> modality**: detecting stress / affect from speech (tone, prosody, acoustics) and fusing it with
> Pebble's existing NeoBERT text classifier. Organized by the three *jobs* the modality requires —
> audio backbone, fusion, and stress targets/data — and ranked by closeness to Pebble's heterogeneous
> multi-task architecture (emotion softmax + continuous regression + high-recall safety head, with
> LLM silver-label distillation and uncertainty/GradNorm loss balancing).
>
> **Closeness dimensions** (same rubric as the survey): D1 categorical+continuous heads · D2
> mental-health/crisis · D3 transfer/warm-start · D4 LLM-teacher distillation · D5 principled MTL
> balancing · D6 safety-recall constraint · D7 encoder backbone.
>
> **Compiled:** 2026-06-16 · discovery + ranking only (no overlap %; hand to `/analysis-paper` for scores).

---

## How this maps to Pebble

The text-only NeoBERT plan is unchanged and becomes the **unimodal baseline**. Adding voice means
attaching a **speech encoder** (the audio analogue of NeoBERT) + a **fusion layer**, then sharing or
duplicating the multi-task heads. Three jobs:

| Job | What the literature provides |
|---|---|
| **Audio backbone** | A pretrained speech encoder to fine-tune (the "speech NeoBERT") |
| **Fusion** | How to join a text encoder + audio encoder for affect |
| **Stress targets + data** | Which acoustic signal carries *stress*, and which datasets to use |

---

## Tier 1 — Closest to Pebble *(read first)*

- **⭐ MUSER — Yao, Papakostas, Burzo, Abouelenien, Mihalcea (NAACL 2021).**
  Transformer that detects **stress as the primary task with emotion as an auxiliary task** on
  multimodal input (audio+text+video), using a *speed-based dynamic sampling* strategy to balance the
  two tasks (MuSE dataset, SOTA). Hits **D1, D5** — the exact stress+emotion joint framing Pebble would
  adopt; dynamic sampling is a cheap MTL baseline to compare against Kendall/GradNorm.
  [ACL](https://aclanthology.org/2021.naacl-main.216/) · [arXiv:2105.08146](https://arxiv.org/abs/2105.08146) · open

- **⭐ U-Fair — Cheong, Bangar, Kalkan, Gunes (ML4H 2024 / PMLR v259, 2025).**
  **Kendall uncertainty weighting applied to a clinical multimodal (audio+text+visual) depression model**
  on DAIC-WOZ / E-DAIC, with PHQ-8 decomposed into per-symptom task heads; shows naive MTL causes
  *negative transfer* and uncertainty-reweighting partially corrects it. Hits **D1, D2, D5, D6** — the
  single closest analogue to Pebble's heterogeneous-head + uncertainty-balancing novelty in a
  multimodal mental-health setting.
  [arXiv:2501.09687](https://arxiv.org/abs/2501.09687) · [PMLR](https://proceedings.mlr.press/v259/cheong25a.html) · open

- **⭐ LLM-Supervised Pre-training for Multimodal ERC — Dutta & Ganapathy (ICASSP 2025).**
  **LLM (GPT-3.5) pseudo-labels → frozen audio encoder + text encoder → co-attention fusion** at
  utterance and conversation levels (WF1 86.48% IEMOCAP, 66.02% MELD, 86.81% CMU-MOSI). Hits **D1, D4, D7** —
  Pebble's Gemini→NeoBERT distillation pipeline extended to audio almost line-for-line. The most reusable
  engineering blueprint here.
  [arXiv:2501.11468](https://arxiv.org/abs/2501.11468) · IEEE Xplore paywalled; arXiv open

> **How it enriches:** these three jointly define the target system — MUSER (stress+emotion framing),
> U-Fair (uncertainty MTL on clinical multimodal), Dutta & Ganapathy (LLM-distillation + frozen-encoder
> fusion). The unclaimed gap holds: none combine heterogeneous regression+classification+safety-BCE MTL
> under a **hard crisis-recall floor** in a multimodal setting.

---

## Job A — Audio backbone *(the "speech NeoBERT")*

- **Dawn of the Transformer Era in SER — Wagner et al. (IEEE TPAMI 2023).**
  Fine-tunes wav2vec 2.0 / HuBERT directly on **continuous valence/arousal/dominance with CCC loss**
  (valence CCC 0.638, closing the "valence gap"); best model released. **D1, D7** — the speech-side
  counterpart of Pebble's MSE regression heads; the canonical dimensional-regression recipe.
  [arXiv:2203.07378](https://arxiv.org/abs/2203.07378) · arXiv open, journal paywalled

- **🔧 emotion2vec — Ma et al. (Findings of ACL 2024).**
  **Emotion-specialized SSL speech encoder** (online self-distillation on 262 h), open weights; a linear
  probe beats HuBERT/WavLM/wav2vec2 (IEMOCAP WA 71.79%). **D7, D4** — the audio analogue of Pebble's
  GoEmotions-warm-started NeoBERT. Strong default backbone candidate.
  [ACL](https://aclanthology.org/2024.findings-acl.931/) · [arXiv:2312.15185](https://arxiv.org/abs/2312.15185) · open weights

- **🔧 Odyssey 2024 SER Challenge — Goncalves et al. (ISCA 2024).**
  WavLM-Large baseline with **joint categorical (8-class) + dimensional (A/V/D) heads** on MSP-Podcast;
  open baseline weights on HuggingFace (`3loi/SER-Odyssey-Baseline-WavLM-*`). **D1, D7** — drop-in
  multi-task audio starting point that structurally mirrors Pebble.
  [ISCA](https://www.isca-archive.org/odyssey_2024/goncalves24_odyssey.html) · open

- **PEFT-SER — Feng & Narayanan (ACII 2023).**
  Systematic **LoRA / adapter / prompt tuning** of WavLM/HuBERT/wav2vec2 for SER; LoRA gives best
  accuracy at minimal extra params and improves fairness. **D7, D5** — how to adapt a large audio
  encoder cheaply on top of an already-large NeoBERT.
  [arXiv:2306.05350](https://arxiv.org/abs/2306.05350) · [code](https://github.com/usc-sail/peft-ser) · arXiv open

- **Efficient Finetuning for Dimensional SER — Sampath, Tavernor, Mower Provost (ICASSP 2025).**
  Five fine-tuning strategies for wav2vec2 on **continuous activation/valence (CCC loss)**; partial
  fine-tune + caching matches full fine-tune at up to 88% speedup, 71% fewer params. **D1, D7** — answers
  "fine-tune an audio encoder for regression without paying full-FT cost." Engineering win.
  [arXiv:2503.03756](https://arxiv.org/abs/2503.03756) · arXiv open

- **EmoBox — Ma et al. (Interspeech 2024).**
  Toolkit + benchmark over **32 emotion datasets / 14 languages / 10 SSL models**; standardized intra-
  and cross-corpus SER. **D7, D3** — the model-selection guide for picking the audio backbone and
  estimating cross-domain generalization.
  [arXiv:2406.07162](https://arxiv.org/abs/2406.07162) · open

- *Baseline reference (preprint):* **Wang, Boumadane, Heba (arXiv:2111.02735, 2021)** — partial vs full
  fine-tuning of wav2vec2/HuBERT on IEMOCAP (WA 79.58% / 73.01%); validates Pebble's staged
  freeze→unfreeze choice. Preprint-only; verify before citing as a venue paper.
  [arXiv:2111.02735](https://arxiv.org/abs/2111.02735)

---

## Job B — Text + audio fusion

- **Multi-level Fusion of wav2vec2 + BERT — Zhao, Wang, Wang (Interspeech 2022).**
  **Co-attention early fusion + late fusion** of exactly the encoder pair Pebble would use
  (BERT-family text + wav2vec2 audio), multi-granularity embeddings, +1.3% UA on IEMOCAP. **D7, D1** —
  the reference fusion baseline.
  [arXiv:2207.04697](https://arxiv.org/abs/2207.04697) · open

- **MulT (Multimodal Transformer) — Tsai et al. (ACL 2019).**
  Introduces **directional pairwise crossmodal attention** for unaligned text/audio/video sequences;
  the canonical cross-attention fusion every later work cites (IEMOCAP, CMU-MOSI). **D1, D7** — the
  architectural foundation any non-concatenation fusion must position against.
  [arXiv:1906.00295](https://arxiv.org/abs/1906.00295) · [ACL](https://aclanthology.org/P19-1656/) · open

- **Cross-Modal Distillation (BERT + wav2vec2) — Kim & Kang (Neurocomputing 2022).**
  wav2vec2 + BERT as teachers → lightweight audio-text student via **contrastive cross-modal
  distillation** + cross-attention (IEMOCAP, MELD, CMU-MOSEI). **D4, D7** — bridges Pebble's distillation
  framing with multimodal fusion. Paywalled; numbers not retrievable from abstract.
  [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0925231222008931) · paywalled

- **Auxiliary Tasks in wav2vec2+BERT Fusion — Sun, He, Han (arXiv 2023).**
  Adds **auxiliary task heads at the fusion layer** (not just the final classifier) to improve
  cross-modal alignment (IEMOCAP WA 78.42% / UA 79.71%). **D1, D7** — directly transferable to attaching a
  crisis/safety auxiliary head at the fusion layer. Preprint-only; verify venue.
  [arXiv:2302.13661](https://arxiv.org/abs/2302.13661) · preprint

> **How it enriches:** gives Pebble a concrete fusion ablation ladder —
> concat → late → co-attention (Zhao) → crossmodal attention (MulT) → cross-modal distillation (Kim & Kang),
> with the safety-recall floor as the evaluation lens.

---

## Job C — Stress targets, acoustics & datasets

- **🔧 StressID — Chaptoukaev et al. (NeurIPS 2023 Datasets & Benchmarks).**
  65-participant multimodal stress dataset (audio + video + ECG/EDA/resp) over 11 tasks, with **both
  binary stress and continuous arousal/valence labels** + unimodal/multimodal baselines. **D1, D3** —
  matches Pebble's head topology; best open dataset for prototyping the voice head. Hand to `/find-dataset`.
  [NeurIPS](https://neurips.cc/virtual/2023/poster/73454) · [code](https://github.com/robustml-eurecom/stressID) · open

- **Kappen et al. (Scientific Reports 2024).**
  Two stress paradigms (Cyberball = mood-only; MIST = physiological): **F0, speech rate, jitter change
  with physiological/arousal stress but NOT mood alone**. **D2 (indirect)** — the evidence base for which
  acoustic features belong in the voice head and which are confounds. Open (data likely on OSF).
  [doi:10.1038/s41598-024-55550-3](https://doi.org/10.1038/s41598-024-55550-3) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10918109/) · open

- **Schewski et al. (PLoS ONE 2025).**
  PRISMA systematic review (38 articles) of **acoustic correlates of stress / negative emotion**:
  prosodic features (F0, intensity, rate) most reliable; jitter/shimmer/HNR inconsistent. The
  authoritative citation chain for feature-choice justification.
  [doi:10.1371/journal.pone.0328833](https://doi.org/10.1371/journal.pone.0328833) · open

- **Namkung et al. (Psychiatry Investigation 2024).**
  115 real office workers, SECPT-induced stress, **ECAPA-TDNN on Mel spectrograms = 70% accuracy**
  (> CNN/Conformer), validated against salivary cortisol; free speech > scripted. **D2** — closest to
  Pebble's real-individual deployment; a sobering accuracy ceiling.
  [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11611465/) · open

- **Wang et al. (Brain Sciences 2025).**
  Real oral-exam stress; network analysis finds **jitter is the only consistently anxiety-linked
  parameter**, plus intensity–formant coupling. **D2** — pinpoints the single most reliable feature for
  anxiety; complements Kappen with a clinical-anxiety framing.
  [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11939969/) · open

- **Speech+Text Foundation Models for Depression — Gómez-Zaragozá et al. (Interspeech 2025).**
  **HuBERT + RoBERTa early fusion** (incl. emotion-fine-tuned variants) on DAIC+ / DEPTALK; best
  multimodal F1 0.75 (DAIC+), surfaces gender bias. **D2, D6, D7** — open clinical text+audio baseline to
  beat; lesson: pre-fine-tune the audio encoder on emotion *before* fusing. Hand to `/find-dataset`.
  [ISCA](https://www.isca-archive.org/interspeech_2025/gomezzaragoza25_interspeech.html) · open

- **Explainable Multimodal Depression (PhqMML) — Zheng et al. (arXiv 2025).**
  **LLM annotates per-utterance PHQ-8 symptom labels** → auxiliary PHQ-8 item classification +
  dialogue-level severity. **D2, D4, D5** — closest clinical analogue to Pebble's Gemini silver-label
  pipeline on a real severity scale. Preprint; verify numbers.
  [arXiv:2501.16106](https://arxiv.org/abs/2501.16106) · preprint

- **BESST — Pešán et al. (Interspeech 2024).**
  90-participant Czech speech stress corpus (16.9 h) with paired ECG/EDA/temp; cognitive + physical
  stress paradigms. Data-collection design reference if Pebble collects its own voice data later.
  [ISCA](https://www.isca-archive.org/interspeech_2024/pesan24_interspeech.html) · open

> **Excluded:** WESAD (Schmidt et al., ICMI 2018) — physiological only, no speech; Menne et al. 2025
> (Acta Neuropsychiatrica) — paywalled, same feature question covered open by Kappen/Schewski.

**Datasets at a glance:** StressID · MuSE (MUSER) · MSP-Podcast (dimensional SER) ·
DAIC-WOZ / E-DAIC / DAIC+ (clinical, text+audio) · IEMOCAP (standard SER) · BESST.

---

## Backbone selection — which speech encoder *(decision)*

We do **not** train a speech encoder from scratch (needs tens of thousands of hours + large GPU budget);
we **reuse a pretrained encoder and fine-tune it** — exactly as the project already does with NeoBERT
for text. The question is *which* one. Numbers below are from a **single common protocol** (IEMOCAP
4-way, frozen linear probe, emotion2vec paper Table 2), so they are directly comparable.

| Model | Params | Pretraining data | License | IEMOCAP WA (linear probe) | Dimensional (V/A/D) recipe? |
|---|---|---|---|---|---|
| wav2vec 2.0 Large | 317M | 60k h general ASR speech | Apache-2.0 | 65.6% | ✅ Wagner TPAMI valence CCC **0.638** |
| HuBERT Large | 317M | 60k h general | Apache-2.0 | 67.6% | ✅ |
| **WavLM Large** | 316M | **94k h** (LibriLight+GigaSpeech+VoxPopuli) | **MIT** | **70.0%** | ✅ Odyssey-2024 open baseline |
| data2vec 2.0 Base | ~94M | 960 h | Apache-2.0 | 68.6% | — |
| **emotion2vec** | **~94M** | **262 h emotion-only** | ⚠️ research-use, ambiguous | **71.8%** | mostly categorical; less proven on regression |
| Whisper-encoder | 650M+ | 680k h weakly-sup. | MIT | poor frozen / good fine-tuned | — (ASR-optimized) |

Sources: emotion2vec [arXiv:2312.15185](https://arxiv.org/abs/2312.15185) (Table 2 linear-probe column) ·
WavLM [arXiv:2110.13900](https://arxiv.org/abs/2110.13900) · Wagner TPAMI [arXiv:2203.07378](https://arxiv.org/abs/2203.07378) ·
EmoBox 32-dataset benchmark [arXiv:2406.07162](https://arxiv.org/abs/2406.07162).

**For emotion2vec:** best emotion representation *per parameter* — 71.8% at ~94M, beating WavLM-Large
(70.0%) which is 3.4× larger and pretrained on ~360× more audio, because it is the only encoder
pretrained specifically on emotional speech.

**Caveats against picking it blindly:** (1) it is validated on **categorical** emotion, while Pebble's
severity/score heads are **continuous regression** — the verified dimensional CCC numbers come from
wav2vec2-robust (Wagner) and WavLM (Odyssey), not emotion2vec; (2) its weight **license is ambiguous**
for shipping (WavLM is MIT, wav2vec2/HuBERT Apache-2.0); (3) the widest single-protocol benchmark
(**EmoBox**, 32 datasets) crowns **WavLM-Large** as the best *general* backbone (emotion2vec is used
there as the evaluation oracle, not the ranked winner across the board).

> **Decision — two backbones, chosen empirically:**
> - **Primary: emotion2vec** — lead with it, justified by the linear-probe table (strongest emotion
>   features, smallest model).
> - **Baseline / fallback: WavLM-Large** (MIT) — the "did the emotion-specialized model actually beat
>   the strong general one?" comparison, *and* the encoder with the proven dimensional-regression recipe
>   that matches Pebble's continuous heads.
>
> This backbone comparison is itself a clean thesis chapter — *"backbone selection for crisis-sensitive
> speech affect"* — not an assumption to defend.

---

## Suggested thesis topic *(voice-primary)*

> **"Stress and crisis detection from voice for emotional-support chat: a speech-encoder affect model
> with uncertainty-weighted heterogeneous heads under a hard safety-recall constraint, supported by a
> NeoBERT text signal."**

The thesis is about **the voice**: the speech encoder (emotion2vec / WavLM / wav2vec2) and its acoustic
stress signal are the object of study. The NeoBERT text classifier is the **supporting modality** — it
provides a strong baseline, a warm-start of the affect heads, and a complementary cue that the voice
model fuses in, *not* the headline contribution.

Shorter title options (pick by taste):
- **"Hearing distress: voice-first stress and crisis detection for emotional-support chat, with text as a supporting cue."**
- **"Vocal biomarkers of stress under a safety-recall constraint: a speech-encoder affect model with NeoBERT text support."**
- **"Speech-driven multi-task affect detection for crisis-sensitive support, text-assisted."**

Why this altitude:
- **Voice is the novelty, text is scaffolding** — the existing text-only NeoBERT becomes the *support
  baseline*; the speech model + its fusion of text is the new delta.
- **The unclaimed gap holds and strengthens:** no published system does heterogeneous (regression +
  classification + safety-BCE) **speech-driven** affect MTL under a *hard crisis-recall floor*. U-Fair is
  closest but is text/visual-led depression without the recall constraint or LLM distillation.
- Every component has a paper to stand on: voice backbone (emotion2vec / WavLM-Odyssey), acoustic stress
  grounding (Kappen, Schewski, StressID), text support + fusion (Zhao co-attention / MulT), distillation
  (Dutta & Ganapathy), balancing (U-Fair / Kendall).

**Scope dials:**
- **(A) Voice-only core** *(lowest risk)* — "Dimensional stress regression from speech with a high-recall
  crisis head" (emotion2vec/WavLM + CCC loss + safety constraint). Text added only as an ablation arm.
- **(B) Voice-led fusion** *(recommended)* — voice is the primary branch; text is fused in to measure how
  much the supporting cue lifts crisis recall. Quantifies the "text as support" claim directly.

**Recommendation:** **(B)** — it keeps voice as the headline while making the text-support role an
explicit, measured contribution. Natural venues: **Interspeech · ICASSP · WASSA · CLPsych**.
