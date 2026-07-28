# Paper 13 — Multimodal Emotion Recognition in Conversations: A Survey of Methods, Trends, Challenges and Prospects

- **Authors:** Chengyan Wu, Yiqiang Cai, Yang Liu, Pengxu Zhu, Yun Xue, Ziwei Gong, Julia Hirschberg, Bolei Ma
- **Venue / year:** EMNLP 2025 Findings
- **Links:** abs https://arxiv.org/abs/2505.20511 · PDF `pdfs/13-mmerc-survey-emnlp25.pdf`
- **Group:** survey / benchmark

**Summary:** Survey mới nhất map fusion methodologies + evaluation protocols cho conversational ER text+audio(+visual).

**Relevance to Pebble:** Bản đồ chiến lược fusion audio+text — điểm vào chọn kiến trúc cho voice+message.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled profile (from `docs/intent/constraints.md` + `docs/spec/capabilities/voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`):** Pebble is a primary **ordinal suicide-risk text** program (BERT-class encoder, teacher-LLM silver labels, gold-holdout eval, ordinal QWK/MAE) plus an adjacent active **voice** stream (frozen emotion2vec/WavLM backbone; 3 heterogeneous MTL heads — emotion CE + affect valence/arousal CCC + crisis BCE under a hard recall ≥ 0.90 floor — balanced by Kendall uncertainty weighting). Forward direction: **voice+text fusion**. "Useful" = advances heterogeneous MTL heads, principled loss balancing, crisis-recall safety, silver-label distillation, or a fusion architecture for the text-primary + voice-auxiliary setup.

### Analysis — MMERC survey (Wu et al., EMNLP 2025 Findings)
- **Overlap:** 31% (peripheral) — D1=0, D2=1, D3=1, D4=1, D5=1, D6=0, D7=1
  - D1=0 (survey centers modality *fusion*, not heterogeneous categorical+continuous heads; all reported metrics are classification — WA/WF1/macro-F1/micro-F1)
  - D2=1 (emotion recognition is the affective substrate of Pebble's voice crisis head, but no mental-health/crisis framing; only a passing "intelligent healthcare" application mention)
  - D3=1 (catalogs canonical emotion corpora IEMOCAP/MELD/CMU-MOSEI/MEmoR/AVEC — voice-relevant, but not the named text transfer sets GoEmotions/EmpatheticDialogues/intensity)
  - D4=1 (surveys generation-based LLM-for-ERC methods — InstructERC, DialogueLLM, MLLMs — loosely adjacent to teacher-LLM labeling, but no silver-label-for-augmentation distillation pattern)
  - D5=1 (its "equal modality weights" vs "text-dominant primary-auxiliary" fusion taxonomy, and the challenges-section push for learnable modality gates / uncertainty-aware fusion / modality dropout, are adjacent to loss balancing — but it is *modality* weighting, not MTL *task*-loss balancing like Kendall/GradNorm/PCGrad)
  - D6=0 (no safety/crisis recall constraint anywhere; standard classification objectives only)
  - D7=1 (text feature-extraction table lists RoBERTa/sBERT — matches Pebble's BERT-family text backbone; audio extractors are older openSMILE/COVAREP/librosa, **not** the emotion2vec/WavLM SSL backbone Pebble's voice stream uses)
  - `(3·0 + 2·1 + 1·1 + 2·1 + 2·1 + 2·0 + 1·1)/26 × 100 = 8/26 × 100 = 31%`
- **Closest on:** the modality-fusion taxonomy (D5 — text-dominant primary-auxiliary vs equal-weight) and the canonical emotion corpora it maps (D3).
- **Best point (Design lesson):** The survey settles that for a text-primary system the winning architecture is a **text-dominant primary-auxiliary fusion** — text stays the core and audio/prosody is injected as an auxiliary cue via cross-modal attention (e.g. Zou et al.'s "weaker modalities as multimodal prompts"), which the survey reports outperforms naive equal-weight concatenation while preserving the strong modality's integrity.
  - **How to apply to Pebble:** When wiring the adjacent voice stream into the primary text risk model, adopt this text-dominant scheme (voice/prosody as auxiliary injected via cross-modal attention onto the BERT text encoder) rather than equal-weight fusion — it matches Pebble's text-primary intent, keeps the gold-holdout text model as the frozen-value core, and gives a citable design justification instead of re-deriving the fusion axis.
- **Caveats:** It is a **survey** — a design-space map, not a runnable method or a number to beat; no baseline metric to reproduce. Scored on a full read of §1–7 (intro, methodology, datasets/eval, methods taxonomy, challenges, conclusion). Zero coverage of Pebble's differentiators: crisis/mental-health domain, heterogeneous categorical+continuous MTL heads, hard recall-floor safety objective, teacher-LLM silver-label augmentation, and ordinal-aware metrics — hence the peripheral band despite the topical adjacency to the voice fusion direction. Voice SSL backbones (emotion2vec/WavLM) are not featured; the audio extractors surveyed predate them.

## Deep research — full-PDF read (2026-07-10)

> Read against the current ViEmoSpeech profile + Decision Register V-A…V-H (see
> `docs/tasks/paper-deep-analysis.md`), **not** the archived text-stream profile in the
> "Analysis" section above (which cites D1–D7 and a suicide-risk/NeoBERT program — stale).
> This is a **survey**; the extract below is the taxonomy + dataset landscape + open-problems
> map, not one method. Full text read via `pdftotext` on `pdfs/13-mmerc-survey-emnlp25.pdf`
> (arXiv:2505.20511v2, 9 Sep 2025; 578 text lines, §1–7 + Limitations + Appendix A datasets).

### Source-access note

- **PDF read locally:** `pdftotext docs/papers/bimodal-ser/pdfs/13-mmerc-survey-emnlp25.pdf`
  → whole file (abstract, §1 intro, §2 task/methodology, §3 datasets+metrics, §4 feature
  extraction+context modeling, §5 method taxonomy graph/fusion/generation, §6 challenges,
  §7 conclusion, Limitations, Appendix A dataset details). Figures (1–5) are line-art in the
  extract; their content is recoverable from the surrounding prose and Figure 2's taxonomy tree.
- **Web-validated:**
  - **Venue/provenance ✔** — query `Multimodal Emotion Recognition in Conversations Survey Wu
    EMNLP 2025 Findings arXiv 2505.20511` → ACL Anthology `2025.findings-emnlp.332`
    (Findings of ACL: EMNLP 2025, pp. **6257–6274**, Suzhou, China). Confirms Findings-EMNLP-2025
    acceptance; arXiv preprint 2505.20511, v1 26 May 2025, **v2 9 Sep 2025** (the version read).
    Local PDF = the accepted v2; no preprint/venue number conflict.
    URL: https://aclanthology.org/2025.findings-emnlp.332/
  - **M3ED dataset stats ✔** — query `M3ED dataset 24449 utterances 990 dialogues 56 Chinese TV
    series emotion` → M3ED = **990 dyadic dialogues / 24,449 utterances** from **56 Chinese TV
    series**, 7 emotions (happy/surprise/sad/disgust/anger/fear/neutral), "first multimodal
    emotional dialogue dataset in Chinese." Matches the survey's Appendix A verbatim.
    URL: https://aclanthology.org/2022.acl-long.391/
  - Other dataset stats (IEMOCAP 7,433 utt; MELD 13,708 utt / 1,433 conv; CMU-MOSEI 23,453
    segments) are canonical, cross-checked against the survey's own Appendix A; tagged ✔ where
    community-standard, ≈ where single-source (ACE, MEmoR).
- **Not a number-to-reproduce paper:** a survey has no headline metric to beat. The load-bearing
  extractions are (a) the fusion taxonomy, (b) the dataset/metric conventions, (c) the
  context-modeling definition — validated by structure/citation, not by a benchmark score.

### What the paper actually does

MERC = predict an emotion label `e_i ∈ Y` for **each utterance `u_i` in a dialogue**
`D = {u_1…u_N}`, where each utterance carries three modality streams `u_i = [u_i^t; u_i^a; u_i^v]`
(text/acoustic/visual) — §2, Eq. 1. The defining property vs sentence-level ER is that the label
depends on **conversational context and speaker tracking**, not the utterance alone (§1, §4.2).

- **Datasets (§3, Table 1 + Appendix A).** Nine benchmarks, split English-centred vs non-English:
  IEMOCAP (en, videos, 2008; 151 dialogues / **7,433 utt** ✔, 6 emotions), AVEC (en, 2012;
  continuous valence/arousal/expectancy/power aggregated to utterance level ≈), EmoryNLP (en, TV,
  2017; ~12,000 utt, 7 emotions ≈), CMU-MOSEI (en, 2018; **23,453 segments** ✔, sentiment −3..+3 +
  6 Ekman intensities), MELD (en, TV *Friends*, 2019; 1,433 conv / **13,708 utt** ✔, 7 emotions),
  MEmoR (en, *Big Bang Theory*, 2020; 5,502 clips / 8,536 samples, 14 emotions ≈), **M3ED** (zh, TV,
  2022; **990 dialogues / 24,449 utt / 56 Chinese TV series** ✔, 7 emotions — the one tonal-language
  corpus), M-MELD (fr/es/el/pl, translated MELD, 2023 ≈), ACE (Akan/African, movies, 2025; 385
  dialogues / 6,162 utt / 21 movies / 308 speakers / 7:1.5:1.5 split, word-level prosodic prominence ≈).
- **Metrics (§3).** Accuracy, **Weighted-F1, Macro-F1, Micro-F1**, plus per-emotion breakdowns.
  All classification. No CCC / no continuous-affect (Pearson/CCC) convention anywhere — even AVEC's
  continuous V/A labels are "aggregated over each utterance" and folded into categorical evaluation.
- **Feature extraction (§4.1, Table 2).** Text: LSTM / CNN / Transformer / **RoBERTa / sBERT**.
  Visual: 3D-CNN / OpenFace / MTCNN / DenseNet / VisExtNet. Audio: **openSMILE / COVAREP / librosa /
  DialogueRNN** — i.e. hand-crafted acoustic descriptors, **no SSL audio (no WavLM / HuBERT /
  emotion2vec / Whisper-encoder)**. This dates the surveyed audio front-end to pre-2020.
- **Context modeling (§4.2, Eqs 2–4).** Two dependency types: **situation-level** (sequential
  models over utterances, `c_i^s, h_i^s = Model(u_i, h_{i-1}^s)`, Eq. 2) and **speaker-level**
  (speaker embeddings `x^m = c_i^s + S_i`, Eq. 3, or a dialogue graph `G=(V,E,W,R)` with a GNN
  `h_i^g = GNN(c_i^s, {…})`, Eq. 4). This is the machinery that makes ERC *conversational*.
- **Method taxonomy (§5, Figure 2) — the core deliverable.** Three families:
  1. **Graph-based (§5.1)** — utterances=nodes, relations=edges. Sub-types: traditional GNN
     (DialogueGCN, MMGCN, CORECT), **hypergraph** NN (GCNet, ConxGNN — for missing-modality /
     high-order interactions), **Fourier GNN** (GS-MCC — DFT high/low-freq split to beat
     over-smoothing). Strength: long-range + speaker interaction; weakness: "naïve connections may
     introduce noise without proper modality alignment."
  2. **Fusion-based (§5.2, Figure 4)** — cross-modal interaction via Transformer attention. Two
     sub-schemes: **(a) Equal Modality Weights** (symmetric intra+inter-modal attention, e.g.
     EmoCaps, CMCF-SRNet, DialogueTRM, SDT with hierarchical gating + self-distillation) — "prevents
     over-reliance on a single modality"; **(b) Text-Dominant / primary–auxiliary** (text is the
     core, weaker modalities injected as auxiliary cues — MMT/Zou 2022 cross-modal attention
     preserving primary-modality integrity, MPT/Zou 2023 "weaker modalities as multimodal prompts,"
     CMATH/Zhu 2024 asymmetric CMA-Transformer + hierarchical distillation). The survey's verdict:
     fusion methods "are efficient for tasks with well-aligned modality inputs but often overlook
     dialogue-level structures such as speaker dependencies… emphasize modality-level fusion over
     relational reasoning."
  3. **Generation-based (§5.3, Figure 5)** — LLM/MLLM reformulation of ERC as text generation:
     instruction-tuned + speaker/context (InstructERC, CKERC, LaERC-S), behavior-aware MLLM
     (DialogueLLM, BeMERC), lightweight fusion/adaptation on a frozen LLM (MSE-Adapter, SpeechCueLLM
     — converts speech features to natural-language prompts, no architecture change).
- **Challenges & prospects (§6).** FAIR/licensing gaps (datasets monolingual, copyright-restricted,
  inconsistent labels → poor reuse); low-resource/multilingual/multicultural (most SOTA is
  English-only; "emotions expressed differently across languages and cultures… culture-specific
  display rules"); fusion-strategy complexity (early/mid/late/hybrid; **asynchronous** modality time
  scales hard to align at utterance level); cross-modal alignment / noise / **missing** / **conflict**
  modality (proposes modality dropout, **uncertainty-aware fusion**, RL to attend to trustworthy
  modalities); **effective modality selection** (learnable modality gates, sparsity regularization);
  efficient MLLM fine-tuning (adapters, LoRA); expanding the modality space (gaze, physiology).
- **Tone / Vietnamese check:** the word "tone" appears only as a generic acoustic descriptor in the
  modality definition ("Prosodic and paralinguistic features… such as tone, pitch, and energy," §2).
  **Lexical tone is never discussed. Vietnamese never appears. M3ED (Mandarin) is included but tone
  is not a variable in any surveyed method or metric.** Nearest prosody-aware artifact is ACE's
  "word-level prosodic prominence" annotation (Akan, non-lexical-tone in the survey's treatment).

### Parts directly useful for ViEmoSpeech

1. **[V-A] The fusion taxonomy as our architecture map (§5.2, Figure 4).** The clean
   Equal-Weight-vs-Text-Dominant axis is exactly the design decision behind V-A. Named, citable
   templates for each pole: symmetric cross-attention (SDT hierarchical-gating + self-distillation)
   vs primary–auxiliary cross-attention (MMT / MPT "weaker-modality-as-prompt" / CMATH asymmetric
   CMA-Transformer). This gives V-A a published axis to position our WavLM+PhoBERT fusion on,
   rather than re-deriving it.
2. **[V-A] The graph-based family is explicitly *conversation-structural* (§5.1, §4.2 Eqs 2–4).**
   The survey states plainly that graph methods' value is "long-range dependencies and speaker
   interactions by modeling utterances as nodes" — i.e. their entire lift comes from
   inter-utterance / inter-speaker edges. For our single-utterance clips there are no such edges.
   Useful precisely as the part of the taxonomy we **exclude** with justification.
3. **[V-G] Dataset landscape + metric convention (§3, Table 1, Appendix A).** ERC's benchmark set
   is TV-series/movie-sourced, utterance-labelled, and reports Weighted-F1 / Macro-F1 / Micro-F1
   with per-emotion breakdowns. M3ED (Chinese TV, 990 dial / 24,449 utt / 56 series ✔) is the direct
   structural analogue to our VN-TV-drama corpus and a scale/format reference for V-H/V-G. The
   **absence of any CCC/Pearson continuous-affect convention** in ERC is a V-G finding: our V/A-CCC
   reporting is not inherited from ERC and must be borrowed from the dimensional-SER line
   (MSP-Podcast, bimodal-12).
4. **[V-C] Text-channel handling is context-dependent, on *clean* transcripts (§4.1, §5.2).** ERC's
   text branch = RoBERTa/sBERT over gold utterance transcripts with situation+speaker context
   (Eqs 2–3). Our text branch is PhoBERT over **noisy PhoWhisper ASR of a single utterance, no
   conversational context**. The survey's "Text-Dominant Modality" claim (text as reliable core)
   rests on that clean-transcript + context assumption — which we do not have.
5. **[V-A/V-G] The §6 conflict/noise/missing-modality agenda maps to our failure modes.** Their
   proposed remedies — **modality dropout, uncertainty-aware fusion, learnable modality gates** —
   are exactly the audio-anchoring safeguards our tone×emotion conflict slice needs (echoing vn-12's
   demand that fusion not collapse to text). The survey names these as *open* problems, i.e. our
   ASR-noise + tone-conflict ablation sits in acknowledged whitespace.

### How each part helps ViEmoSpeech succeed

- **V-A fusion choice:** Position the learned WavLM+PhoBERT fusion on the survey's axis and pick
  **primary–auxiliary with the AUDIO as primary** — the inverse of ERC's text-dominant default.
  Rationale, defensible from our own synthesis: our register (noisy VN-ASR, single utterance) is
  audio-dominant, so the MMT/MPT "weaker-modality-as-prompt" *shape* should be used with text as the
  weaker/auxiliary prompt and audio (+phonation) as the core — the mirror image of Zou et al. Cite
  Figure 4 as the design space; cite our register argument for flipping the primary. Concretely: the
  V-A ablation table gets a row per pole (equal-weight concat vs audio-primary cross-attn vs
  text-primary cross-attn), directly instantiating §5.2.
- **V-A exclusion of graph methods:** Do **not** import DialogueGCN/MMGCN/hypergraph machinery. Write
  one paragraph citing §5.1 + Eqs 2–4 to justify that ViEmoSpeech clips carry no inter-utterance or
  inter-speaker edges (single-speaker by construction, VAD∩turn-cut), so the graph family's entire
  lift is unavailable — a scoping decision, not an omission. This pre-empts a reviewer asking "why no
  conversational context model?"
- **V-G eval protocol:** Adopt Weighted-F1 + Macro-F1 as the categorical headline (matches the ERC
  convention M3ED/MELD report, so our 7-class number is comparable), **but explicitly add CCC for
  V/A and recall@floor for distress** and flag in-text that ERC does not report these — our
  dimensional + safety metrics come from the SER/clinical line, not this survey. Use M3ED's
  990-dial/24,449-utt/56-series scale as the "comparable VN-drama-format corpus" anchor row in the
  V-H positioning table (alongside THAI-SER, MSP-Podcast, VNEMOS).
- **V-C text branch under ASR noise:** Treat the survey's "text-dominant" finding as *conditional*
  and test the condition. Because ERC text dominance assumes clean transcripts + context, run the
  V-C ablation as **gold-caption vs PhoWhisper-ASR** input to the text branch on the same clips; the
  expected drop is the empirical content of our register argument. Keep PhoBERT config lightweight
  (short single-utterance context, no dialogue-history network — Eqs 2–4 do not apply).
- **V-A/V-G conflict slice:** Bake a tone×emotion / acoustic–semantic conflict sub-slice into eval
  and pair it with an **audio-anchoring safeguard** (modality dropout or an aux audio-only head)
  drawn straight from §6's "conflict modality" remedies. This turns the survey's open problem into
  our measured contribution.

### Child mental-health / ViEmoSpeech transfer lens

ViEmoSpeech is **utterance-level, single-clip, tonal-language (VN), acted-drama** SER — three of
the survey's core assumptions do not hold, and saying so precisely is the transfer judgment:

- **Context-modeling does NOT transfer (the central caveat).** ERC's identity is conversational:
  situation-level sequence models + speaker-level embeddings/graphs (§4.2). Our clips are cut at
  VAD∩speaker-turn and are single-speaker by construction — there is no dialogue history, no
  interlocutor to track, no emotion-shift-across-turns signal. Everything the survey lists as the
  *advantage* of graph-based methods (§5.1) is inapplicable. Transfer verdict: **fusion-based (§5.2)
  transfers; graph-based and speaker-level context (§4.2, §5.1) do not.** This is the single most
  important lens result — most of the survey's page count is spent on machinery we deliberately do
  not use.
- **The audio front-end is pre-SSL — the survey's fusion verdicts sit on weak audio features.**
  Table 2's audio extractors (openSMILE/COVAREP/librosa) predate WavLM/emotion2vec (which
  bimodal-01/12 establish as the default). A "text-dominant" conclusion drawn when the audio branch
  is hand-crafted descriptors is partly an artifact of a weak audio channel; with a strong SSL audio
  backbone the modality balance shifts. We should not inherit "text dominates" as a law — it is
  contingent on the audio extractor, and our WavLM(+phonation) branch changes the premise.
- **Tone×emotion is untouched — novelty whitespace confirmed a 16th time.** M3ED (Mandarin, 56 TV
  series) is in the benchmark set, yet "tone" appears only as a generic prosody word; no surveyed
  method treats lexical tone as a variable and no metric conditions on it. The nearest artifact is
  ACE's word-level prosodic prominence (Akan). ViEmoSpeech's lexical-tone×emotion F0/phonation-channel
  claim (grounded in vn-13 Chang + vn-06 Shen) remains unclaimed across the entire MERC literature.
- **Ethics / release lens (§6 FAIR).** The survey's own FAIR critique — datasets copyright-restricted,
  monolingual, inconsistently licensed, hard to reuse — is exactly the gap our features-only,
  timestamps+labels+speaker-ids, CC-BY release format answers for a TV-drama source that cannot be
  redistributed. The survey frames "open licensing + standardized metadata via collaborative
  consortiums" as future work; our release design is a concrete instance. No child-specific ethics
  content here (the corpus is adult TV-drama acted speech), so the acted-drama-proxy framing (V-F)
  is unchanged — the survey offers no clinical or minor-facing anchor.

### Limitations & open questions for ViEmoSpeech

- **Contradiction #1 (vs the emerging cross-cutting synthesis + vn-08):** the survey elevates a
  **"Text-Dominant Modality"** sub-family (§5.2b) as a mainstream, effective scheme — text as the
  reliable core, audio/visual as auxiliary. This directly contradicts vn-08's VN-ASR finding that
  text is "near-useless" (38.7–44.1% text-only) and the register-dependence synthesis (clean gold
  transcript → text dominates; noisy spontaneous ASR → audio dominates). The survey never states its
  text-dominance is conditional on clean transcripts + conversational context — but every corpus it
  cites (MELD/IEMOCAP/M3ED) supplies exactly those. **Resolution for us:** cite Figure 4's axis, but
  flip the primary to audio and *measure* the register dependence (gold-caption vs ASR ablation)
  rather than inherit the survey's default.
- **Contradiction #2 (vs bimodal-01/08/12 audio-backbone finding):** the survey's audio feature table
  (Table 2: openSMILE/COVAREP/librosa) is pre-SSL, whereas our program and bimodal-01/08/12 treat
  WavLM/emotion2vec/Whisper-encoder as the baseline. Any modality-balance conclusion in this survey
  is therefore not portable to a strong-SSL-audio system — a gap, not a guide.
- **Gap: no continuous-affect (CCC) convention.** ERC evaluation is categorical F1 only (§3); AVEC's
  continuous V/A is folded into categorical use. Our V/A-CCC and distress-recall@floor metrics get
  **zero support** from this survey — V-G must source them from MSP-Podcast (bimodal-12) and the
  clinical review (bimodal-10). Do not cite this survey for dimensional evaluation.
- **Gap: survey has no numbers to beat.** It is a taxonomy, not a leaderboard; no method's score is
  reported. It moves V-A/V-G/V-C as a *map*, and cannot serve as a baseline row (unlike
  arXiv:2412.09829, THAI-SER, or VNEMOS). Every quantitative bar for ViEmoSpeech still comes from the
  primary papers, not here.
- **Open question:** the §6 "conflict modality" and "effective modality selection" agendas
  (uncertainty-aware fusion, learnable modality gates, modality dropout) are named as *unsolved*.
  ViEmoSpeech's tone×emotion conflict slice + audio-anchoring safeguard would be a concrete answer in
  acknowledged whitespace — but the survey gives no recipe, only the problem statement.
