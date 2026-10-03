# Paper 21 — Hybrid Multi-Attention Network for Audio-Visual Emotion Recognition Through Multimodal Feature Fusion

- **Authors:** Sathishkumar Moorthy, Yeon-Kug Moon
- **Venue / year:** Mathematics (MDPI), 13(7):1100, 2025 (OA)
- **Links:** abs https://www.mdpi.com/2227-7390/13/7/1100 · PDF `pdfs/21-hybrid-multi-attention-avser.pdf`
- **Group:** audio-visual (đối chứng)

**Summary:** Hybrid multi-attention fusion network cho audio-visual affect.

**Relevance to Pebble:** Fallback fusion-ablation reference; venue tier thấp — không phải primary pick.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled profile (at analysis time).** Pebble = a primary **ordinal suicide-risk TEXT** program (NeoBERT/BERT-family ~250M encoder, teacher-LLM silver labels, gold-holdout eval, ordinal-aware QWK/MAE) under a hard "never train+eval on the same label source" constraint (`docs/intent/constraints.md`); plus an adjacent **VOICE** stream (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`): frozen emotion2vec/WavLM-Large SSL backbone + shared trunk with **three heterogeneous heads** — emotion (CE), affect (valence+arousal, **CCC loss**), crisis (BCE under a **hard recall floor ≥0.90**) — balanced by **Kendall uncertainty weighting**; forward direction is voice+text fusion. Scored against this profile.

**Paper in one line.** An audio-visual (and text, on IEMOCAP) emotion-recognition model whose contribution is a hybrid cross-modal attention fusion (CSSA = SEMAT+SPAAT; HASPCM = SMA+PCMA; collaborative cross-attention) built to stay robust when modalities are non-complementary / noisy / missing. Categorical emotion classification on IEMOCAP; continuous valence–arousal regression (with CCC) on AffWild2/AFEW-VA. Backbones: 3D-CNN/ResNet (visual), openSMILE/1D-CNN (audio), TextCNN (text).

**Per-dimension scores (before the number):** D1=1, D2=0, D3=1, D4=0, D5=0, D6=0, D7=0

- D1 (heterogeneous heads, w3) = **1** — produces both a categorical output (IEMOCAP) and continuous V/A with CCC (AffWild2/AFEW-VA), the two output types Pebble's voice stream needs, but on separate datasets/experiments, not one joint heterogeneous-head topology, and no safety head.
- D2 (mental-health/crisis, w2) = **0** — general affect; only a passing "diagnosis of emotion-related disorders" mention.
- D3 (emotion-transfer / intensity corpora, w1) = **1** — AffWild2 & AFEW-VA are dimensional V/A *intensity* corpora (rubric includes "intensity"), but not GoEmotions/EmpatheticDialogues and not the speech-only V/A sets (MSP-Podcast) Pebble targets.
- D4 (teacher-LLM silver-label distillation, w2) = **0** — none in the proposed method.
- D5 (principled MTL loss balancing, w2) = **0** — imbalance handled by 20-bin discretization + over/under-sampling; no uncertainty/GradNorm/PCGrad/Nash-MTL.
- D6 (safety/crisis recall constraint, w2) = **0** — absent.
- D7 (backbone match, w1) = **0** — 3D-CNN/openSMILE/TextCNN; no emotion2vec/WavLM SSL and no BERT-family text encoder.

**Overlap:** (3·1 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·0) / 26 × 100 = 4/26 × 100 = **15%** — **peripheral (<40%)**.

- **Closest on:** D1 (categorical + continuous-CCC affect outputs) and D3 (V/A intensity corpora).
- **Best point (Design lesson):** The paper's motivating finding — standard cross-attention fusion *assumes complementary modalities* and degrades on real data where they are non-complementary, noisy, or missing; their fix models intra- **and** cross-modal relations jointly so conflicting/absent streams don't collapse the prediction.
  - **How to apply to Pebble:** For the forward voice+text fusion, do not assume the streams agree — a calm voice over a suicidal text is the safety-critical non-complementary case; adopt a fusion head that preserves each modality's intramodal signal and tolerates a missing/uninformative stream, and stress-test it under modality dropout rather than reporting only the both-present number.
- **Caveats:** MDPI/`Mathematics` venue, low tier; categorical vs continuous tasks are on different datasets, so the "heterogeneous heads" credit is partial. Audio-visual with non-SSL backbones — its AffWild2 CCC numbers (val 0.596 / aro 0.683) are **not** a fair baseline for Pebble's speech-only affect head. Read from the local PDF (abstract, §2.2 related work, §3.1, §4.3–4.4 results); MDPI HTML returned HTTP 403, so scoring is from the PDF only.

## Deep research — full-PDF read (2026-07-10)

> Verdict up front: this is a **low-relevance audio-visual control** (~15%) and, for V-A, a
> **redundant fusion paper** — it stacks known attention blocks (VQA co-attention [ref 65, Lu 2016],
> Transformer self-attention [ref 45], plus image semantic/spatial attention) and its cleanest
> genuinely-transferable idea (CCC loss) is already held from bimodal-17 RJCMA. It adds **one useful
> negative lesson** (a headline robustness claim with no supporting experiment) and **one eval
> anti-pattern** (mixed subject-independent / random-split protocols). Section kept proportionate.

### Source-access note

Read end-to-end from the local PDF (`pdfs/21-hybrid-multi-attention-avser.pdf`, 30 pp) via
`pdftotext` (full extract, 1056 lines). The local PDF **is the version of record** — MDPI
*Mathematics* 2025, 13(7):1100, DOI 10.3390/math13071100, published 27 March 2025, CC-BY. Venue and
authorship corroborated (checkmark) via WebSearch (`Moorthy Moon Hybrid Multi-Attention … Mathematics
2025 13 1100`) → RePEc `gam/jmathe/v13y2025i7p1100-d1621912` and Semantic Scholar `cd41/…191a.pdf`. A
second **numeric** cross-check against the MDPI HTML was blocked (HTTP 403, same as the original stub),
so the numbers below are single-source but taken from the published version of record, not a preprint —
tagged (checkmark) (version-of-record) rather than dual-corroborated. No preprint/venue delta exists
(no arXiv mirror; Data Availability names only a GitHub repo, commit `b2c9e03`).

### What the paper actually does

**Task.** Two disjoint tasks on three corpora: (a) dimensional valence–arousal regression on
**AffWild2** (564 YouTube videos, ~2.8M frames, V/A in [-1,1], subject-independent 341/71/152-video
split, §4.1) and **AFEW-VA** (600 movie clips, random 400/200 train/test, 5-fold CV, §4.1); (b)
categorical emotion classification on **IEMOCAP** (5162/737/1481 utterance split, §4.1). Loss for the
regression heads is the CCC loss **L = 1 − rho_c** (Eq. 27, §3.7).

**Backbones (non-SSL, do-not-copy).** Visual = Inflated-3D CNN (I3D, 12M) + R3D-18 (33M) + ResNet-18
2D-CNN+LSTM (13.3M) on face crops; audio = ResNet-18 (11.7M) over log-mel spectrograms (DFT 1024,
20 ms window / 10 ms hop) **plus handcrafted MFCCs**; text (IEMOCAP only) = TextCNN over gold
transcripts; audio on IEMOCAP additionally uses openSMILE (§3.1–3.4, §4.4.3, Table 3). Trained on one
RTX A6000, SGD, lr 1e-3, 50 epochs, dropout 0.8 (Table 2).

**Fusion (the "contribution"), three stacked modules:**
- **CSSA** = SEMantic Attention (SEMAT, Eqs 3–5, sigmoid-gated) + SPAtial Attention (SPAAT, Eqs 6–8,
  softmax), where **audio guides the visual stream** toward salient facial regions; outputs summed
  (Eq. 9), then per-modality Bi-LSTM (Eqs 10–11).
- **HASPCM** = Single-Modal Attention (SMA, standard multi-head self-attention, Eqs 12–17) + Parallel
  Cross-Modal Attention (PCMA, a co-attention "motivated by the parallel attention module in [65]"
  = Lu et al. VQA hierarchical co-attention 2016, Eqs 18–23).
- **CMRA** = Cross-Modality Relation Attention over the concatenated fused features (Eqs 24–26).

**Headline numbers (all version-of-record, checkmark):**

| Result | Value | Ref | Note |
|---|---|---|---|
| AffWild2 **test** V / A / avg | 0.457 / 0.375 / **0.416** | Table 8 | **Not** SOTA — loses to Zhang ABAW3 [84] 0.520/0.601/**0.560**, ties Nguyen [83] 0.449 |
| AffWild2 **validation** CCC (best fold) | V 0.596 / A 0.683 | Table 9 | 6-fold; best fold only; mean across folds ~ V 0.496 / A 0.649 |
| AFEW-VA V / A / avg (5-fold CC) | 0.654 / 0.617 / **0.635** | Table 7 | Beats cited baselines; random split (leak risk, below) |
| IEMOCAP acc / WA-F1 | **75.39 / 78.56** | Tables 6,10,11 | +10.51 F1 over GraphMFT; split not stated speaker-disjoint |
| IEMOCAP unimodal visual / audio | 67.52 / 61.77 (acc) | Table 6 | **visual > audio**; concat 70.12, cross-attn 72.75 |
| CSSA ablation (full vs w/o) | V 0.457/0.375 vs 0.421/0.343 | Table 4 | +0.036 / +0.032 |
| HASPCM ablation (full vs w/o) | V 0.457/0.375 vs 0.432/0.348 | Table 5 | +2.5% / +2.7% |

Note the stub's "AffWild2 CCC val 0.596 / aro 0.683" is the **single best validation fold** (Table 9),
not a test number; the honest test figure is the mid-pack 0.457 / 0.375 (Table 8).

### Parts directly useful for ViEmoSpeech (tagged with Decision IDs)

1. **[V-A — verdict: REDUNDANT, one-sentence distinguish]** HMATN's fusion is an incremental stack of
   pre-existing attention blocks: co-attention (VQA 2016), self-attention (Transformer 2017), and
   image **semantic/spatial** attention. It cites Praveen's joint cross-attention (ref 63) as a
   *baseline it competes with*, i.e. it is a sibling of the bimodal-17 **RJCMA** template we already
   extracted, not a new mechanism. **Nothing here ports to an audio↔text VN system that RJCMA/BCAF/
   WavFusion/FAS don't already give us** — and the two novel-labeled blocks (SEMAT/SPAAT, the CSSA
   module) are defined on **visual spatial regions** ("concentrate on visually critical areas,"
   §3.5), which have **no analog in text**. So the load-bearing half of the architecture is
   un-swappable for us. *Transfer risk: high/fatal* — CSSA is intrinsically image-spatial; only
   PCMA/CMRA are modality-agnostic and those are plain co-attention already in hand.
2. **[V-G — CCC loss corroboration]** The V/A heads use **L = 1 − rho_c** (Eq. 27), the same
   scale/shift-invariant CCC objective bimodal-17 recommends. This is a *second independent AV vote*
   for using CCC loss on ViEmoSpeech's valence/arousal head, not a new artifact. *Transfer risk: low*
   — CCC loss is dataset-agnostic; but note our labels are discrete 1–5 (Russell), so pair CCC with
   QWK/MAE as bimodal-17 already prescribed.
3. **[V-G — eval anti-pattern to name and avoid]** The paper mixes protocols: AffWild2 is properly
   **subject-independent** (good, matches our ADR-002 speaker-disjoint), but AFEW-VA is a **random
   400/200 clip split** and IEMOCAP's 5162/737/1481 split is **never stated to be speaker/session-
   disjoint** — so the eye-catching IEMOCAP 75.39/78.56 sits in the same leak-inflated bucket as
   vn-08 (86.6), vn-10 (0.87), and bimodal-11. *Transfer risk: this is exactly our house style already*
   — cite it in the eval-protocol table as a *mixed-rigor* example: subject-independent where it's easy
   (AffWild2), random where it inflates (AFEW-VA/IEMOCAP).
4. **[V-B — backbone do-not-copy]** All-CNN/openSMILE/TextCNN, no SSL, no BERT-family text encoder.
   The IEMOCAP result that **visual (67.52) > audio (61.77)** unimodally, and the stated "non-neutral
   emotion problem … due to the reliance of most AVER models on text-based features" (§4.4.5), describe
   a *visual-primary* regime that **inverts** ViEmoSpeech's noisy-ASR audio-primary register. Their
   backbone rankings and modality-dominance conclusions do not transfer. *Transfer risk: high* — wrong
   modality pair (audio↔visual, not audio↔text) and wrong encoder family.

### How each part helps ViEmoSpeech succeed

- **V-A (fusion):** Close the door. In the method paper's related-work / fusion-candidates
  paragraph, cite HMATN as *"an audio-visual cross-attention stack (CSSA+HASPCM) whose salient module
  is image-spatial and therefore inapplicable to audio↔text; the transferable half is co-attention,
  already covered by RJCMA/BCAF."* No experiment arm to spend on it. This **saves** a fusion-ablation
  row rather than adding one.
- **V-G (CCC loss):** Keep `affect_head` on `L = 1 − rho_c`; add HMATN and RJCMA together as the two
  AV citations for CCC-loss on V/A regression. Report our own number as CCC **+ QWK + MAE** on the
  discrete 1–5 scale.
- **V-G (eval hygiene):** Add a one-line row to the eval-protocol comparison table:
  "HMATN 2025 — subject-independent on AffWild2 but **random-split** on AFEW-VA/IEMOCAP → the 75.39
  IEMOCAP figure is not speaker-disjoint." Use it to justify why ViEmoSpeech reports the honest
  whole-series-holdout number and flags leaky comparators.
- **V-A / robustness claim (negative lesson):** the paper's *stated* motivation — fusion that stays
  robust "even when the input data are noisy or missing modalities" (Abstract) — is **never tested**:
  there is no modality-dropout table, no noise-injection sweep, nothing. This is the concrete reason
  our modality-dropout / audio-anchoring safeguard (demanded by vn-12) must be an **actual ablation
  arm**, not a claim in prose. It also **corrects** this file's existing Analysis "Best point," which
  credited the non-complementary-modality robustness as the transferable design lesson — the paper
  asserts it but provides zero supporting experiment.

### Child mental-health lens (ViEmoSpeech transfer validity)

- **Wrong modality pair.** The paper's core machinery (CSSA/SEMAT/SPAAT) fuses **audio↔face-video**;
  ViEmoSpeech fuses **audio↔ASR-text**. The "spatial attention over visually critical face regions"
  has no text analog, so the architectural transfer is near-zero. Only the generic co-attention math
  (PCMA) survives the swap, and we already have that from RJCMA/BCAF.
- **No tone, no VN, no phonation.** Corpora are English/wild (AffWild2, AFEW-VA) and English acted
  (IEMOCAP); "audio" is spectrogram+MFCC. Nothing engages lexical tone or the F0/phonation channel
  competition that is ViEmoSpeech's V-D novelty — so it leaves our claim untouched (consistent with
  the 0/20-papers finding).
- **No-ASR blind spot, again.** IEMOCAP text is **gold transcript** via TextCNN; there is no ASR stage
  and no ASR-noise ablation anywhere. Every fusion paper in this set shares this blind spot; HMATN is
  one more data point that our high-arousal tone-swap-ASR robustness ablation (mày→máy) is genuinely
  unclaimed territory.
- **Ethics / framing.** §5 gestures at "mental health monitoring … detecting emotional states to
  assess stress, anxiety, and depression" as a downstream application — the same clinical-overclaim-on-
  acted-affect anti-pattern we flagged for vn-10/EAA. The paper trains on movie/YouTube affect with no
  clinical anchor; cite as another what-not-to-do for the distress-head (V-F) honest-proxy framing.

### Limitations & open questions for ViEmoSpeech (incl. contradiction/gap)

- **Contradiction #1 (claim vs evidence, load-bearing):** the abstract and §5 sell robustness "even
  when the input data are noisy or missing modalities," but the paper runs **no missing-modality and
  no noise-injection experiment** — the ablations (Tables 4–6) only add/remove *its own* attention
  blocks with all modalities present. The robustness selling point is unsupported. (This directly
  corrects the existing Analysis section of this file, which took that claim as the transferable
  "design lesson.")
- **Contradiction #2 (vs bimodal-17 RJCMA and vs its own "SOTA" claim):** HMATN claims to "surpass
  state-of-the-art," but on the **AffWild2 test set** its average (0.416, Table 8) **loses** to Zhang
  ABAW3 [84] (0.560) and barely edges the very RJCMA-style joint-cross-attention baseline it cites
  (Praveen [63] 0.369). "SOTA" holds only for validation-fold CCC vs *unimodal* variants. RJCMA
  (bimodal-17) remains the cleaner, honestly-benchmarked AV CCC-loss template.
- **Gap #3 (leaky eval):** IEMOCAP 75.39/78.56 and AFEW-VA random-split numbers are not
  speaker/session-disjoint — not comparable to ViEmoSpeech's whole-series-holdout bar; usable only as
  flagged leaky comparators, mirroring vn-08 / vn-10 / bimodal-11.
- **Editorial-rigor flag:** the same acronym is expanded three different ways — HMATN as "Hybrid
  Multi-ATtention Network" (Abstract) vs "Hierarchical Multimodal Attention-based Transformer Network"
  (§4.4.3); HASPCM as "…of Single and Parallel Cross-Modal" (Abstract) vs "Hybrid Attention-based
  Spatial-Pyramid Cross-Modal" (§4.3); PCMA as "Parallel" vs "pyramid" cross-modal attention. Consistent
  with the low venue tier; treat all specific numbers as single-source (version-of-record, no
  independent numeric replication reachable).
- **Open question (none blocking):** the GitHub repo (commit `b2c9e03`) is named but was not inspected;
  given V-A redundancy there is no reason to spend a dataset/code pull on it.
