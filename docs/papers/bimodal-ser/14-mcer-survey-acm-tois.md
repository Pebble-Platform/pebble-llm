# Paper 14 — A Comprehensive Survey on Multi-modal Conversational Emotion Recognition with Deep Learning

- **Authors:** Yuntao Shou, Tao Meng, Wei Ai, Nan Yin, Keqin Li
- **Venue / year:** ACM TOIS (accepted; arXiv 2312.05735, revised 2025)
- **Links:** abs https://arxiv.org/abs/2312.05735 · PDF `pdfs/14-mcer-survey-acm-tois.pdf` (bản arXiv; ACM paywalled)
- **Group:** survey / benchmark

**Summary:** Taxonomy fusion (context-free / sequential / speaker-differentiated / speaker-relationship) + datasets MCER (IEMOCAP, MELD, …).

**Relevance to Pebble:** Backbone reference cho phần benchmark + evaluation-protocol của related-work.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Pebble profile used (assembled at analysis time):**
- Primary program (`docs/intent/constraints.md`): ordinal suicide-risk **text** classification; teacher-LLM silver labels → gold-holdout eval; ordinal-aware losses/metrics (QWK, MAE, macro-F1); BERT-family ~250M encoder.
- Adjacent voice stream (`docs/spec/capabilities/voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`): frozen **WavLM-Large / emotion2vec** SSL backbone + shared trunk, **3 heterogeneous heads** — emotion CE + **affect valence/arousal CCC** regression + **crisis BCE under a hard recall floor (0.90)** — balanced by **Kendall uncertainty weighting**; the task is *blocked on proxy labels* and explicitly wants real continuous-affect + crisis corpora.
- Forward direction: voice+text fusion.

### Analysis — MCER survey (Shou et al., ACM TOIS)
- **Scores:** D1=0, D2=0, D3=1, D4=0, D5=0, D6=0, D7=1 → (3·0 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·1) / 26 × 100 = **8%** (**peripheral**, <40%)
- **Closest on:** D3 (emotion corpora incl. continuous-affect sets — SEMAINE V/A/Expectancy/Power, CH-SIMS intensity, MuSE valence/arousal/dominance) and D7 (text side: BERT/RoBERTa are standard extractors — matches Pebble's text stream; but audio side is classical COVAREP/openSMILE/LibROSA/OpenEAR, **not** the SSL WavLM/emotion2vec family Pebble's voice stream uses).
- **Why the rest score 0:** it is a single-task emotion-classification survey — no heterogeneous MTL heads (D1), no mental-health/crisis domain (D2), no teacher-LLM silver-label distillation (D4), no MTL loss balancing (uncertainty/GradNorm/PCGrad) (D5), and no safety/recall-floor *objective* (D6; Tables 6–8 report recall/AUC and note recall-oriented models like EmotiCon at 81.6% recall as merely *observed*, not designed-in).
- **Best point (Dataset to reuse):** the §2 dataset catalog surfaces three real **continuous-affect** conversational corpora — **MuSE** (valence/arousal/dominance, real participants), **SEMAINE** (V/A/Expectancy/Power ∈ [-1,1]), **CH-SIMS** (continuous sentiment intensity) — exactly the label type the voice affect-CCC head currently fakes with a Russell-circumplex proxy on RAVDESS.
  - **How to apply to Pebble:** hand MuSE + SEMAINE to `find-dataset` (license/gate check) as additional candidates alongside the MSP-Podcast / DAIC swap already named in `docs/tasks/voice-mtl-heads.md` M5 — they give the affect head *real* continuous V/A targets so CCC numbers become scientifically meaningful.
- **Caveats:** scored mainly from the arXiv PDF (§1–3, §6 benchmark tables 6–8); the ACM version is paywalled and §7 (applications) was not read — if §7 lists mental-health monitoring as an application it would nudge D2 to a weak partial but not change the domain classification. Backbone read confirms text=BERT/RoBERTa/GLOVE/TextCNN, audio=classical toolkits (no SSL), so D7 held at partial.

## Deep research — full-PDF read (2026-07-10)

> Analyzed against the **current ViEmoSpeech profile + Decision Register (V-A…V-H)** in
> `docs/tasks/paper-deep-analysis.md`. The stale "Analysis (overlap with Pebble)" block above uses
> the archived text-stream profile (D1–D7) and is retained only as history — cite V-A…V-H below.

### Source-access note

- **PDF read:** `pdftotext docs/papers/bimodal-ser/pdfs/14-mcer-survey-acm-tois.pdf` → 3,566 lines,
  read in full (intro §1, datasets §2, feature-extraction §3, taxonomy §4, eval-metrics §5,
  benchmark §6 Tables 6–9, applications §7, privacy §8, challenges §9, future §10). Local PDF is
  **arXiv:2312.05735v2 (13 Nov 2025)**.
- **Web-validated:**
  - *Venue.* Query "Shou … Comprehensive Survey MCER arXiv 2312.05735 venue accepted journal" →
    `https://arxiv.org/abs/2312.05735` (fetched): **no `Journal reference` field; Comments = "36 pages,
    10 figures"; authors = Shou, Meng, Ai, Fangze Fu, Nan Yin, Keqin Li.** ✖ **The stub's "ACM TOIS
    (accepted; revised 2025)" is uncorroborated** — arXiv shows a preprint with no venue, and the PDF's
    running header "J. ACM, Vol. 37, No. 4, Article 111. Publication date: August 2025" is the **default
    `acmart` template placeholder**, not a real J. ACM/TOIS acceptance. Treat as **preprint, venue
    unconfirmed** (also listed on SSRN abstract_id=5017731). v1 author list (Shou/Meng/Ai/Yin/Li) differs
    from v2 (adds Fangze Fu); one index lists "Guinan Guo" — author list unstable across versions.
  - *Dimensional corpora (V-E).* Query "SEMAINE valence arousal expectancy power … CH-SIMS -1..1" →
    CH-SIMS ACL 2020 (`https://aclanthology.org/2020.acl-main.343/`, `https://thuiar.github.io/publication/chsims/`)
    confirms **CH-SIMS = -1..+1 sentiment intensity, but 2,281 clips** — the survey's §2.8 claim of
    "**about 10,000** Chinese sentence-level samples" is ✖ **inflated/inaccurate** (canonical = 2,281).
    SEMAINE V/A confirmed continuous; the survey's 4-dimension claim (V/A/Expectancy/Power ∈[-1,1]) is
    ≈ (FeelTrace multi-dimension annotation is documented for SEMAINE; external quick-search surfaced
    only V/A explicitly). Lesson: **do not cite this survey's per-dataset statistics uncritically.**
- Benchmark numbers in Tables 6–9 are **survey-compiled aggregations** (the authors re-tabulated
  numbers from ~40 primary papers); they are not independently reproducible against one external source,
  so each is tagged ≈ (survey-table) with its table ref.

### What the paper actually does

A methods survey of **Multi-modal Conversational Emotion Recognition (MCER)** — recognizing the emotion
of *each utterance in a dialogue* using text+audio+video with **conversational context**. Its stated
novelty is a **taxonomy organized by how models capture conversational dynamics**, explicitly contrasted
(§1) with prior surveys organized "by modality combination" or "by task-stage (extract/fuse/classify)":

- **Taxonomy (§4, Fig. 3) — four categories, ordered by increasing context/speaker structure:**
  1. **Context-free** (§4.1) — each utterance independent; this is where the survey's *fusion* methods
     live: **Add** (Eq. 3), **Concatenation** (Eq. 4), **SVM** (Eq. 5), **Multiple-Kernel-Learning**
     (Eq. 6), **Select-Additive-Learning CNN**, **Tensor Fusion (TFN)**. All **early / low-order fusion**.
  2. **Sequential context** (bc-LSTM, DialogueRNN-family, Transformer/HiTrans) — models inter-utterance
     temporal dependency.
  3. **Distinguishing-speaker** (DialogueRNN, COSMIC, EmotionIC) — conditions on speaker identity/state.
  4. **Speaker-relationship** (DialogueGCN, RGAT, DAG-ERC, MM-DFN, GraphCFC, LR-GCN) — GCN/GAT over a
     dialogue graph; **the survey's headline empirical claim is that this category wins** (§6).
- **"Which structure wins" (§6, Tables 6–9, WF1 on IEMOCAP/MELD):** context-free is worst (SAL 49.2/58.8,
  SVM 48.7/56.4, TFN 54.2/56.7 IEMOCAP/MELD; <50% F1 on MELD for TextCNN/LFM); sequential ≈
  speaker-differentiated (mid-60s IEMOCAP WF1); **speaker-relationship GCN best** — GraphCFC highest AUC
  **89.18%** (≈, Table 7), LR-GCN best per-class F1 (≈, Tables 8–9) at the cost of 15.77M params / 21s
  IEMOCAP / 147s MELD inference. **EmotiCon recall 81.63%** (≈, Table 7) is flagged as recall-oriented
  ("favors recall … useful where missing emotional signals is more critical than false alarms").
- **Datasets (§2, Tables 1–2 + §2.8–2.9):** IEMOCAP (6-class, 12.46h), MELD (7-class, Friends TV),
  DailyDialog (6-emo text), EmoryNLP (7 text), EmotionLines (7 text), EmoContext (3 text), plus
  **CH-SIMS** (Chinese/Mandarin video, **sentiment intensity −1..+1 + 3-class**) and **MuSE** (English+Spanish,
  **continuous valence/arousal/dominance**). **SEMAINE** = 95 dialogues / 5,798 utt, **4 dimensions
  Valence/Arousal/Expectancy/Power continuous [−1,1]**. **No Vietnamese; no lexical-tone corpus;** the
  only tonal-language set (CH-SIMS) is treated as *sentiment*, tone never a variable.
- **Feature extractors (§3.3, Table 5):** text = TextCNN/GLOVE/Word2Vec/**BERT/RoBERTa/T5**; audio =
  **classical toolkits COVAREP/openSMILE/LibROSA/OpenEAR** (MFCC, pitch, eGeMAPS; COVAREP also NAQ/MDQ/
  glottal LF params) — **no SSL (WavLM/HuBERT/emotion2vec)** anywhere; video = 3D-CNN/Facet/OpenFace/OKAO.
- **Eval metrics (§5):** **Accuracy, WA, F1, WF1 only** — all categorical. Notably WA is defined
  (Eq. 36) with weight **inversely proportional to class sample count** ("more samples → smaller weight"),
  i.e. a **macro/balanced-accuracy variant**, *not* the standard SER convention where WA = overall
  (frequency-weighted) accuracy and UA = unweighted. **No regression / CCC / Pearson metric appears
  despite SEMAINE/MuSE/CH-SIMS being continuous.**
- **Challenges (§9):** data scarcity (IEMOCAP 11,098 / MELD 5,810 / SEMAINE 394 utt), heterogeneity+noise,
  **class imbalance** (MELD fear 1.91%, disgust 2.61% → "0% accuracy on some algorithms," Table 9),
  consistency-vs-complementarity trade-off, multi-model collaboration.
- **Future work (§10):** data generation (VAE/GAN/diffusion); deep fusion (deformable temporal conv +
  dynamic gating); **unbiased learning §10.3 = focal / label-distribution-aware-margin (LDAM) loss +
  prototype contrastive + category-balanced training**; missing-modality recovery; zero-shot via
  CLIP/Whisper/MLLM; **multi-label §10.6 = Sigmoid-over-Softmax + label-graph + uncertainty-aware +
  aux emotion-intensity regression head**; dynamic-dialogue (TCN/dynamic-GNN); lightweight (KD/pruning/
  quantization). §7.4 lists **medical/mental-health** as an application (depression/anxiety early
  screening) but only in one generic paragraph.

### Parts directly useful for ViEmoSpeech (tagged by Decision ID)

1. **Dimensional-vs-categorical label landscape (V-E).** The catalog is the cleanest map of which public
   conversational corpora carry *categorical* labels (IEMOCAP-6, MELD-7, DailyDialog-6, EmoryNLP-7,
   EmotionLines-7, EmoContext-3) vs *dimensional continuous* (SEMAINE V/A/Expectancy/Power [−1,1];
   MuSE V/A/D; CH-SIMS intensity −1..+1). **CH-SIMS is the only corpus that carries *both* a categorical
   3-class label AND a continuous intensity** — the exact hybrid shape ViEmoSpeech proposes (7-class +
   V/A 1–5 + distress). Transfer risk: **partial** — all are *conversational, dialogue-level, non-tonal
   (or Mandarin-sentiment)*; usable as a **label-scheme precedent for a hybrid head**, not as training data.
2. **The unbiased-learning / rare-class recipe (V-E + V-G).** §9.3 + §10.3 give the concrete imbalance
   lever set — **focal loss, LDAM (label-distribution-aware margin), prototype-contrastive, category-balanced
   sampling** — motivated by the reproduced failure that MELD fear/disgust collapse to ~0% F1 (Table 9)
   at 1.91%/2.61% prevalence. Directly informs ViEmoSpeech's ≥50-clip rare-class floor (ADR-002) and the
   loss choice for the 7-class head. Transfer risk: **strong** — imbalance is corpus-agnostic; this is the
   most transferable content in the survey.
3. **Fusion-mechanism taxonomy, as the *early-fusion baseline ladder* (V-A).** §4.1 gives the canonical
   low-order fusion primitives with equations — **Add (Eq. 3) < Concat (Eq. 4) < Tensor-Fusion/MKL** —
   and §6 confirms context-free fusion is the floor. These are the honest **learned-fusion baseline rows**
   for ViEmoSpeech's V-A ablation (below cross-attention / gated / Q-Former). Transfer risk: **medium** —
   the *primitives* transfer to an utterance-level bimodal model, but the survey's **headline "which model
   wins" answer (speaker-relationship GCN) does NOT** (see §Child/transfer lens).
4. **Eval-metric definitions + a terminology trap (V-G).** §5 pins the categorical metric set
   (Accuracy/WA/F1/WF1) that IEMOCAP/MELD papers report, so ViEmoSpeech's baselines table can state
   comparability. **Load-bearing caveat:** this survey defines **WA as inverse-frequency-weighted
   (≈ macro/balanced accuracy)** — the *opposite* of the mainstream SER "WA = weighted (overall) accuracy /
   UA = unweighted" convention (as used by THAI-SER vn-11 and MSP bimodal-12). ViEmoSpeech must **name its
   metric formulas explicitly and prefer macro-F1 (+ CCC for V/A)** rather than an ambiguous "WA."
5. **Recall-oriented observation for the distress head (V-F).** EmotiCon's recall 81.63% (≈, Table 7),
   framed as acceptable where "missing emotional signals is more critical than false alarms," is a
   citable-but-weak precedent for a recall-first objective — **observed, never designed-in** (no
   recall-floor training anywhere in the survey). Transfer risk: **weak** — supports the *framing* of
   ViEmoSpeech's distress recall-floor, supplies no method.
6. **Multi-label design note (V-E, forward-looking).** §10.6 prescribes **Sigmoid-over-Softmax + aux
   emotion-intensity regression head** for co-occurring emotions — relevant only if ViEmoSpeech later
   moves from single-label 7-class to multi-label; today's single-label head does not need it. Logged, not
   actioned.

### How each part helps ViEmoSpeech succeed

- **(1 → the label spec, `tools/labeler/SPEC.md` + V-E):** cite CH-SIMS as the precedent that a single
  corpus can carry categorical + continuous-intensity labels jointly, justifying ViEmoSpeech's 7-class +
  V/A(1–5) + distress hybrid annotation schema; hand MuSE/SEMAINE/CH-SIMS to `find-dataset` for
  license/gate checks as **external anchors for the V/A head** (complementing MSP-Podcast from bimodal-12),
  not as in-domain data.
- **(2 → the 7-class emotion head + rare-class floor, V-E/V-G):** adopt **LDAM or class-balanced focal
  loss** (not flat CE) for the emotion head from day one, and keep the ADR-002 ≥50-clip floor as the
  structural complement — the survey's MELD 0%-fear result is the cautionary anchor that loss tricks alone
  do not rescue an under-sampled class (echoing bimodal-02 ABHINAYA's "corpus floor > loss trick" finding).
- **(3 → the V-A fusion ablation ladder, `arXiv:2412.09829` rule-fusion baseline row):** slot Add/Concat/
  TFN as the *lowest* learned-fusion rows in the ablation table, above the withdrawn rule-fusion prior
  (vn-09) and below cross-attention / gated / CASE-FAS Q-Former — giving a complete, citable fusion ladder.
- **(4 → the baselines table + eval protocol, V-G):** write metric formulas verbatim and default to
  **macro-F1 + CCC + recall@floor**; add a footnote that "WA" is defined inconsistently across the SER
  literature (this survey ≠ THAI-SER/MSP) to protect cross-corpus comparability under ADR-002.
- **(5 → distress-head framing, V-F):** cite EmotiCon only to say "recall-oriented emotion models exist and
  are considered acceptable in high-miss-cost settings"; supply the *method* (recall-floor objective +
  threshold policy) from bimodal-10 JMIR + FAIIR, not from here.

### ViEmoSpeech transfer-risk / child-and-tone lens

This is a **conversational (dialogue-level, context+speaker-modeling) survey**; ViEmoSpeech scores emotion
at the **single utterance level, single-speaker by construction** (clips cut at VAD ∩ speaker-turn). The
consequences are sharp:

- **The survey's entire headline contribution is non-transferable.** Categories 2–4 (sequential-context,
  distinguishing-speaker, speaker-relationship GCN) — and the §6 result that they beat context-free by
  10–20 WF1 points — are **exactly the context/speaker machinery ViEmoSpeech deliberately forgoes**. For
  ViEmoSpeech the survey effectively says "you are operating in the weakest (context-free) regime by
  design"; the honest reading is that **utterance-level ViEmoSpeech gives up the survey's biggest reported
  lever**, and must recover accuracy from *within-utterance* audio+text fusion + the tone×emotion signal,
  not from conversation graphs. This is a load-bearing scoping fact for the method paper, not a defect.
- **Zero tonal-language modeling.** CH-SIMS (Mandarin) is present but framed as *sentiment*; tone is never
  a variable, and there is no Vietnamese corpus. **V-D novelty (lexical-tone × emotion channel competition)
  is untouched** by this survey too — now confirmed across all 21 bimodal papers.
- **Audio backbone is a generation behind (V-B).** The survey's audio feature stack is 100% classical
  (COVAREP/openSMILE/LibROSA/OpenEAR); it predates SSL adoption. It is therefore **not** evidence about
  WavLM vs emotion2vec vs Whisper-encoder — that decision must come from bimodal-01/08/12, not here. One
  useful crumb: COVAREP exposes **glottal-source params (NAQ, MDQ, LF model)** — i.e. *phonation/voice-quality*
  descriptors — supporting the V-B plan to add a handcrafted phonation vector (jitter/shimmer/HNR/H1–H2)
  for VN's phonation-heavy tone, though the survey never connects them to tone.
- **Privacy §8 aligns with ViEmoSpeech's release constraint.** §8's anonymization / disentangled
  identity-suppression discussion is consistent with (weaker than) ViEmoSpeech's features-only, media-withheld
  release; not novel, but a citable "privacy is a named MCER concern" anchor.
- **Ethics.** Acted-TV-drama emotion (MELD is *Friends*) is treated as valid ground truth throughout — the
  survey never flags acted≠natural, the very caveat MSP-Podcast (bimodal-12) rejects and ViEmoSpeech must
  answer via the acted-proxy framing (V-F/V-D).

### Limitations & open questions for ViEmoSpeech

- **★ Contradiction/redundancy vs bimodal-13 (MMERC survey, EMNLP'25) on "which fusion wins" (V-A).**
  The two surveys answer **different questions** and their headline answers do not overlap:
  **bimodal-13** organizes by *modality weighting* and concludes **text-dominant primary-auxiliary
  cross-attention** wins (audio injected as auxiliary onto a text-primary core); **bimodal-14** organizes
  by *conversation dynamics* and concludes **speaker-relationship GCN** wins, with fusion proper reduced to
  early Add/Concat/TFN primitives. They **agree only on the floor** (naive equal-weight concat / context-free
  is weakest). For ViEmoSpeech this means **bimodal-13 is the load-bearing V-A source** (its modality-weighting
  answer transfers to an utterance-level bimodal model), while **bimodal-14 is largely redundant on V-A** and
  contributes instead the V-E label landscape, V-G metric conventions, and the imbalance recipe. Surfacing
  this prevents double-citing two surveys as if they corroborate one fusion recommendation — they do not.
- **★ Gap: no dimensional / CCC metric despite dimensional corpora.** §5 is 100% categorical (Acc/WA/F1/WF1),
  yet §2 catalogs three continuous-affect corpora (SEMAINE/MuSE/CH-SIMS). The survey **never states how to
  evaluate a continuous V/A head** — so ViEmoSpeech's V-A/V-G CCC metric has **no precedent here** and must
  import CCC/Pearson from bimodal-12 (MSP-Podcast) / the WASSA-style regression line. A whitespace, not a
  contradiction, but it means this survey cannot anchor the V/A head evaluation.
- **Metric-name trap (V-G).** The survey's "WA" (inverse-frequency-weighted, Eq. 36) is the *opposite* of the
  THAI-SER/MSP "WA = overall weighted accuracy" convention — a real cross-corpus comparability hazard;
  ViEmoSpeech must define its own formulas rather than reuse "WA" ambiguously.
- **Data-quality caution.** The paper's own dataset stats are unreliable (CH-SIMS "~10,000" vs canonical
  2,281; SEMAINE utterance counts vary between §2.5 "5,798" and §9.1 "394"). Use the survey as a *map* of
  which corpora and which label types exist, then verify every number against the primary source.
- **Venue unconfirmed.** Stub says "ACM TOIS accepted"; arXiv shows a preprint with no journal reference and
  an `acmart`-placeholder header. Cite as **preprint (arXiv:2312.05735v2, 2025), venue unconfirmed** — M7
  should correct the stub's venue line.
- **Contradiction vs ViEmoSpeech plan on where accuracy comes from.** The survey's strongest empirical
  message is that *context + speaker modeling* is the dominant accuracy lever (context-free is the floor).
  ViEmoSpeech's design (utterance-level, single-speaker) sits in that floor by construction — an open question
  the method paper must confront head-on: **can within-utterance tone×emotion + audio-text fusion recover
  what conversation-graph modeling delivers, or does utterance-level scoring cap achievable accuracy?**
