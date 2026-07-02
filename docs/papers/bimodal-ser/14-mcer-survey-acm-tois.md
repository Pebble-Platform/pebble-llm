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
