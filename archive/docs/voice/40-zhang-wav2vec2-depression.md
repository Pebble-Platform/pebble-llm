# Paper 40 — Improving Speech Depression Detection Using Transfer Learning with wav2vec 2.0 in Low-Resource Environments

## 1. Bibliographic info

**Title:** Improving speech depression detection using transfer learning with wav2vec 2.0 in low-resource environments

**Authors:** Xu Zhang (School of Software Engineering, Xiamen University of Technology), Xiangcheng Zhang (School of Computer and Information Engineering, Xiamen University of Technology, corresponding — fufuturbo@163.com), Weisi Chen, Chenlong Li (Xiamen University of Technology), Chengyuan Yu (Jiangxi Agricultural University).

**Year / venue:** *Scientific Reports* 14:9543 (2024). Received 11 Jan 2024, accepted 21 Apr 2024. DOI 10.1038/s41598-024-60278-1. Open Access (CC BY 4.0). No preprint — Scientific Reports is the version of record.

**One-line summary:** An end-to-end, dual-corpus speech depression-detection pipeline that fine-tunes wav2vec 2.0 (all layers) for frame-level features, compresses each 7-second segment with a 1D-CNN + additive-attention-pooling block, then classifies the whole interview with an LSTM + self-attention temporal head — reaching **79.00% F1 on DAIC-WOZ (English)** and **90.53% F1 on CMDC (Chinese)** with a single feature class and no data augmentation, beating prior speech-depression baselines in a low-resource regime.

## 2. Why this paper is in the Pebble set

Pebble's thesis includes a **voice-message modality**: children may send short spoken clips rather than typed text, and Pebble needs a path from raw child audio to a `severity` / distress signal. This paper is the **most replicable end-to-end wav2vec2 depression pipeline** in the set — it specifies every block (preprocessing → SSL feature extraction → segment encoder → temporal classifier), every hyperparameter, two public corpora, and an ablation per component. It is the audio-side analogue of Pebble's text `severity` head: where Pebble transfers SemEval/WASSA emotion-intensity into a regression head on NeoBERT text, this paper transfers wav2vec 2.0 (and even IEMOCAP emotion fine-tuning) into a *binary* depression head on clinical-interview audio. The architecture, the low-resource transfer-learning strategy, and the F1 numbers are the concrete reference for a future Pebble **voice depression / distress head**.

This paper is **not** about children (DAIC-WOZ and CMDC are adults in clinical interviews), **not** turn-level (one label per ~15-min interview / 12 fixed questions), and **not** silver-labelled (PHQ-8 / clinical confirmation). Its value to Pebble is the *pipeline shape, component ablations, and transfer-learning recipe* — never the absolute numbers as a child-data target.

## Deep research — full-PDF read (2026-06-16)

### Source-access note

Read from the local PDF `docs/papers/pdfs/40-zhang-wav2vec2-depression.pdf` via `pdftotext` (full body; abstract, all method sections, Tables 1–4 transcribed verbatim; the figure-only ablations — pooling F1 deltas, segment-length curve, ROC/AUC, clustering — read from their narrative text). The Read tool cannot render PDFs.

Provenance validation (published Scientific Reports version is authoritative; there is no preprint, so no preprint-delta question arises):

- **Venue / identity / headline numbers** — WebSearch (`Zhang "Improving speech depression detection using transfer learning with wav2vec 2.0" Scientific Reports 2024 DAIC-WOZ CMDC F1 79%`) resolved the paper to *Sci Rep* 14:9543 (2024), DOI 10.1038/s41598-024-60278-1, and confirmed **F1 79% on DAIC-WOZ and 90.53% on CMDC**. URLs: https://www.nature.com/articles/s41598-024-60278-1 and https://pmc.ncbi.nlm.nih.gov/articles/PMC11045867/ . Status: ✔ corroborated.
- **Table 1–4 numbers** (DAIC P/R/F1 84.49 / 76.99 / 79.00; CMDC P/R/F1 94.83 / 88.33 / 90.53; full Table 3 fine-tuning grid; Table 4 self-attention; pooling +4.69% / +2.26% F1; all hyperparameters; dataset splits) — WebFetch on the PMC full text https://pmc.ncbi.nlm.nih.gov/articles/PMC11045867/ returned every one of these numbers identical to the local PDF. Status: ✔ corroborated (two independent copies, PDF + PMC, agree exactly).
- **Datasets** — DAIC-WOZ at https://dcapswoz.ict.usc.edu/ and CMDC at https://ieee-dataport.org/open-access/chinese-multimodal-depression-corpus (both stated in the paper's Data Availability). Status: ✔ corroborated (links live in paper).

### What the paper actually does

**Problem framing (Materials and methods → Problem definition).** Binary classification: for participant *i* with raw speech `x_i`, predict `y_i ∈ {0,1}` (0 = normal, 1 = depression). Each participant also carries a PHQ-8 score, but the central task is the *dichotomous* depression label. The pipeline has four steps: audio preprocessing → frame-level feature extraction → segment-level feature extraction → depression classification.

**Step 1 — Speech preprocessing.** Only the **subject's** speech is kept; interviewer voice, silent intervals, and background noise are removed. The kept audio is cut into **fixed-duration, non-overlapping 7-second segments** preserving temporal order, and **upsampled to 16 kHz** (wav2vec 2.0's input requirement). The 7-second length is chosen by enumeration (ablation, Fig. 8: performance rises with segment length up to ~7 s then plateaus at 7–8 s; shorter segments break emotional continuity, longer ones cut sample count). Notation: `x_i = {s_{i,1}, …, s_{i,M}}`, M segments per subject; each segment `s_{i,j} = {h_1, …, h_N}`, N frames of dimension d.

**Step 2 — Frame-level features via fine-tuned wav2vec 2.0.** wav2vec 2.0 (Baevski et al. 2020, ref 35) maps raw audio through a multi-layer conv feature encoder (25 ms frame length, 20 ms frame shift → latent `{Z_1…Z_T}`) then a Transformer context encoder (base = 12 layers, large = 24 layers) → `{h_1…h_N}`. **The lower convolutional layers are frozen; the Transformer layers are fine-tuned.** The outputs of *all* Transformer layers are **summed** to give the wav2vec 2.0 feature sequence for the segment. The paper compares base vs large, last-layer vs all-layer fine-tuning, and a wav2vec 2.0 variant fine-tuned on **IEMOCAP** (emotion-transfer, motivated by Wu et al. ref 36, "emotion → depression" transfer).

**Step 3 — 1D-CNN + attention pooling (segment encoder, Fig. 2 right).** Three convolutional blocks, each = 1-D conv layer + ReLU + dropout. Filter counts `C = [80, 80, 80]`. The conv output `C_{i,j} = conv1D(s_{i,j}, K) ∈ R^{T×d}` (Eq. 1). A **pooling layer** then compresses frames → one segment vector `V_{i,j}`. Three pooling methods are compared: average pooling (Eq. 2), max pooling (Eq. 3), and **additive attention pooling** (Eq. 4): `V_{i,j} = Softmax(w_c · C_{i,j}^T) · C_{i,j}`, where `w_c` is a learned weight that weights frames by importance. Attention pooling wins (see ablation).

**Step 4 — LSTM + self-attention temporal head (Fig. 3).** The per-segment vectors `{v_{i,1}…v_{i,j}}` feed an **LSTM** (Eq. 5) to capture short- and long-term temporal correlation across the whole interview. A **self-attention** layer (Eq. 6, scaled dot-product `Softmax(QK^T/√d_K)V`) then re-weights segments so depression-relevant segments dominate. The summed self-attention output goes to a linear layer → binary `y_i`. Motivation: "not all depressed patients exhibit obvious depressive characteristics in their speech," so the model must *select* the informative segments rather than average them.

**Datasets (Result → Datasets description).**
- **DAIC-WOZ** (ref 39): 189 clinical Wizard-of-Oz interviews for distress (anxiety/depression/PTSD), ~50 h total. Split: **107 train / 35 development / 47 test**. Average interview ~15 min, 16 kHz. Following prior work, experiments use **train + development** subsets (the dev set is the de-facto test for comparability). Multimodal (text/image/speech); only speech is used. PHQ-8 + binary labels.
- **CMDC** (ref 40): Chinese Multimodal Depression Corpus, semi-structured interview with **12 fixed questions**. **78 samples (26 severe-depression, 52 healthy).** Smaller than DAIC-WOZ — used to stress-test the low-resource claim in a second language.

**Experimental settings.** Linux, single **NVIDIA V100**, PyTorch. Fine-tuning LR **1e-5**; downstream-task LR **0.006**; **Adam**, weight decay **0.001**; batch size **32**; **200 epochs** with early stopping (patience 10 on validation). A baseline comparison feature is the **OpenSMILE IS09 emotion set**: 16 LLDs (MFCC, ZCR, …) → 32 with first-order deltas → 12 functionals → **384-dim** utterance vector.

**Results — Table 1, DAIC-WOZ (vs prior SDD methods; boldface = best):**

| Method (year) | Feature | Precision | Recall | F1 |
|---|---|---|---|---|
| ResNet (Chlasta 2019) | spectrogram | 57.14% | 57.14% | 57.14% |
| LSTM (Rejaibi 2022) | MFCC | 73.50% | 64.50% | 64.00% |
| EmoAudioNet (Othmani 2021) | MFCC+Spectrogram | — | — | 66.00% |
| DepAudioNet (Ravi 2022) | wav2vec 2.0 | 66.70% | 66.70% | 69.20% |
| MSCDR (Du 2023) | LPC+MFCC | 71.00% | 83.00% | 74.60% |
| CNN+Channel-wise Attention (Zhou 2022) | MFCC+Spectrogram+eGeMAPS | 79.60% | 68.66% | 77.00% |
| (is09_emotion baseline) | is09_emotion | 84.49%* | 76.99%* | 70.09% |
| **Ours** | **wav2vec 2.0** | **84.49%** | **76.99%** | **79.00%** |

(*The is09 row's reported F1 is 70.09%; the precision/recall columns in the extracted table are partly merged — the load-bearing comparison is "Ours" wav2vec2 F1 **79.00%** vs the strongest prior baseline F1 **77.00%**.) Headline deltas the authors call out: vs Du et al. (similar 1D-CNN+LSTM but MFCC+LPC), Ours is **+17.79% precision, +10.29% recall, +4.4% F1**; vs Othmani et al. **+16.62% F1**; vs Ravi et al. (also wav2vec2 + adversarial) **+9.8% F1**. Confusion matrix (Fig. 4): Ours has more true positives and fewer false positives than Du et al. — "more discerning" at distinguishing non-depressed. All ✔ corroborated.

**Results — Table 2, CMDC (Chinese; boldface = best):**

| Method | Feature | Precision | Recall | F1 |
|---|---|---|---|---|
| Unsupervised encoder + Transformer (Sun 2022) | MFCC | 92.00% | 83.00% | 87.00% |
| (is09_emotion baseline) | is09_emotion | 82.31% | 79.17% | 80.36% |
| **Ours** | **wav2vec 2.0** | **94.83%** | **88.33%** | **90.53%** |

vs the IS09 prosodic baseline, Ours is **+12.51% precision, +10.16% recall, +10.17% F1**. ROC/AUC (Fig. 5): fine-tuned wav2vec features sit further upper-left; on CMDC the AUC reaches **1.0** (perfect ranking, small n). All ✔ corroborated.

**Ablation 1 — fine-tuning strategy (Table 3, on DAIC-WOZ):**

| Setting | Pretrained model | Precision | Recall | F1 |
|---|---|---|---|---|
| A. Frozen, last layer | wav2vec2-base | 68.00% | 66.30% | 66.86% |
| A. Frozen, last layer | wav2vec2-large | 68.30% | 68.30% | 68.30% |
| A. Frozen, last layer | wav2vec2-IEMOCAP | 83.82% | 54.17% | 48.04% |
| B. Fine-tune, last layer | wav2vec2-base | 64.32% | 62.14% | 70.86% |
| B. Fine-tune, last layer | wav2vec2-large | 75.00% | 72.64% | 73.48% |
| B. Fine-tune, **all layers** | wav2vec2-base | 88.33% | 70.83% | 72.81% |
| B. Fine-tune, **all layers** | wav2vec2-large | **84.49%** | **76.99%** | **79.00%** |

Three findings: (1) **fine-tuning > frozen** at every match; (2) **large > base**; (3) **all-layer fine-tuning > last-layer-only**. The IEMOCAP-emotion-fine-tuned frozen variant gives **high precision (83.82%) but collapsing recall (54.17%) → F1 48.04%** — emotion-transfer alone is *not* enough; in-domain depression fine-tuning is required. All ✔ corroborated.

**Ablation 2 — pooling (Fig. 7, narrative):** attention pooling beats **max pooling by +4.69% F1** and **average pooling by +2.26% F1**. ✔ corroborated.

**Ablation 3 — self-attention (Table 4, DAIC-WOZ):**

| | Precision | Recall | F1 |
|---|---|---|---|
| Without self-attention (LSTM last step → FC) | 82.14% | 72.83% | 74.72% |
| **With self-attention** | **84.49%** | **76.99%** | **79.00%** |

Self-attention adds **+4.28% F1** (74.72 → 79.00). ✔ corroborated.

**Ablation 4 — segment length (Fig. 8):** F1 rises from 4 s to 7 s, plateaus 7–8 s, then weakens (sample-count drop). 7 s chosen. ✔ corroborated.

**Clustering (Fig. 6, narrative):** t-SNE-style clustering of is09_emotion (a, blurred), raw-wav2vec2 (b, partial), fine-tuned-wav2vec2 (c, two tight, well-separated groups) — qualitative evidence that fine-tuning is what makes depressed vs healthy separable.

**What is NOT in the paper:** no calibration / ECE / reliability curves; no per-PHQ-severity regression result (PHQ-8 mentioned but only the binary head is evaluated); no child or adolescent data; no turn-level scoring; no inference-latency / model-size numbers (acknowledged as future "real-time deployment" work); no statistical significance tests on the F1 deltas; no train/test speaker-disjointness statement beyond the standard DAIC split; ensemble not used (single model).

### Parts directly useful for Pebble

Each tagged with the Decision ID it moves and a transfer-risk note.

1. **The full end-to-end voice-depression pipeline as a template for a Pebble voice `severity`/distress head (D-D, D-A).** Raw audio → VAD/subject-only segmentation → fine-tuned SSL encoder (sum-of-all-Transformer-layers) → 1D-CNN + attention pooling per segment → LSTM + self-attention over segments → head. This is the most copy-able blueprint in the voice set for getting from a child's spoken clip to a distress score. *Transfer risk: medium.* The blueprint is sound and modality-correct, but every block was tuned on adult 15-min clinical interviews; Pebble's clips are short, spontaneous, child-register. The *shape* transfers; the *segment-length / LSTM-depth* must be re-tuned for short clips (a 30-second child clip yields ~4 segments, not the dozens an interview yields, so the LSTM+self-attention temporal head may be overkill — see Limitations).

2. **All-layer fine-tuning of the SSL backbone beats frozen and last-layer-only (D-A, D-E).** Table 3: all-layer FT wav2vec2-large = 79.00% F1 vs frozen-last-layer 68.30% vs FT-last-layer 73.48%. The +5.5 F1 from going last-layer→all-layer FT is the audio analogue of Pebble's text staged-fine-tuning question (gradual unfreeze / discriminative LR). *Transfer risk: medium-high.* On Pebble's **small** child-voice data, full fine-tuning of a 24-layer large model risks overfitting — the opposite regime from this 50-h interview corpus. Pebble should treat "all-layer FT helps" as a hypothesis to re-test with gradual-unfreeze + discriminative-LR (D-E) as a regularised middle ground, not adopt full FT blindly.

3. **Emotion-transfer (IEMOCAP fine-tuning) is necessary-but-insufficient — it wrecks recall (D-D).** The wav2vec2-IEMOCAP frozen variant gets 83.82% precision but only 54.17% recall (F1 48.04%). This is direct evidence that **transferring an *emotion* model into a *clinical-severity* task without in-domain fine-tuning collapses recall** — exactly Pebble's plan to transfer SemEval/WASSA emotion-intensity into the `severity` head. *Transfer risk: low (the warning transfers cleanly).* It says: emotion→severity transfer must be *followed by* in-domain severity fine-tuning, and recall must be watched, not just precision. This directly motivates Pebble's recall-floor discipline on the severity/safety path.

4. **Attention pooling > mean/max for collapsing frames to a segment vector (D-A, D-B).** +4.69 F1 over max, +2.26 over mean. The frame→segment aggregator is a real, measurable design lever. *Transfer risk: low.* Attentive pooling is task-agnostic and consistent with paper 27 (ECAPA-TDNN ≥ mean pooling); Pebble's voice head should default to attentive pooling, with mean as the cheap baseline. (Caveat: on very short child clips there are few frames to attend over, shrinking the gain.)

5. **Self-attention segment-selection adds +4.28 F1 because "not all depressed patients show it in every segment" (D-A).** The temporal head learns to up-weight the few informative segments. *Transfer risk: medium.* The premise — distress is *sparse* across a long interview — is real for Pebble too (a child's distress may surface in one phrase of a clip), but Pebble's clips are short, so the within-clip sparsity is smaller; the bigger payoff would be *across-turn* selection mid-conversation, which this paper doesn't test.

6. **Concrete, fully-specified hyperparameters for an SSL fine-tune (D-E).** LR 1e-5 (backbone) vs 0.006 (head) — a **~600× discriminative-LR ratio** between the pretrained backbone and the from-scratch head; Adam, weight decay 0.001; batch 32; early stopping patience 10. *Transfer risk: low.* The two-speed LR (tiny on backbone, large on head) is exactly the discriminative-LR principle Pebble wants for D-E, and these are reasonable starting values for any SSL-encoder fine-tune; the absolute LRs may need shrinking on small child data.

7. **Two-corpus, two-language low-resource validation as an evaluation template (D-D, D-H).** Reporting the same architecture on DAIC-WOZ (English, n≈142 used) and CMDC (Chinese, n=78) demonstrates the transfer-learning claim isn't corpus-specific. *Transfer risk: low (methodology).* Pebble should likewise validate any voice head on ≥2 corpora before claiming generalisation, since single-corpus speech results overfit speaker/recording conditions notoriously.

### How each part helps Pebble succeed

- **Voice distress head blueprint (D-D, D-A).** Stand up `experiments/voice_severity_head/` mirroring this pipeline: subject-only segmentation → fine-tuned SSL encoder → attention-pooled segment vectors → temporal head → severity output. Reuse the exact block ordering; parameterise segment length (default 7 s but sweep 3–7 s for short child clips) and make the temporal head swappable (LSTM+self-attention for long clips, simple attention-over-segments or even a single pooled vector for short clips). This is the artifact that turns Pebble's "voice modality" from a slogan into a runnable spike.
- **Backbone fine-tuning policy (D-A, D-E).** Adopt the **two-speed discriminative LR** (backbone 1e-5, head ~6e-3) as the default for both the voice encoder *and* the NeoBERT text fine-tune. But on small child data, gate "all-layer FT" behind a gradual-unfreeze schedule (D-E): start frozen, unfreeze top layers first, monitor validation recall — the Table-3 frozen-vs-FT gap is the evidence that *some* backbone adaptation is needed, while Pebble's data scarcity argues against the *full* FT this paper used.
- **Emotion→severity transfer with a recall guard (D-D).** Pebble plans WASSA/SemEval emotion-intensity → `severity` regression transfer. This paper's IEMOCAP-emotion variant (precision 83.82, recall **54.17**) is the cautionary citation: bolt an in-domain severity fine-tuning stage *after* the emotion-transfer init, and put a recall floor on the severity/safety output. Concrete artifact: an ablation row reporting recall *before and after* the in-domain stage, not just F1.
- **Pooling + temporal head as config knobs (D-A, D-B).** Implement frame→segment pooling as `{mean, max, attention}` and ship attention as default (per this paper + paper 27). Implement the segment→utterance head as `{mean, lstm_selfattn}` and choose by clip length. Report the with/without-self-attention delta as a Pebble ablation row, exactly as Table 4 does.
- **Two-corpus evaluation discipline (D-D, D-H).** Make the voice head's scorecard span ≥2 datasets/conditions before any deployment claim; report precision AND recall AND F1 (not accuracy alone) given class imbalance, mirroring Tables 1–2.

### Child mental-health lens

- **Population/register mismatch is the dominant risk.** DAIC-WOZ and CMDC are **adults in structured clinical interviews** (15-min DAIC sessions; 12 fixed CMDC questions), recorded in controlled conditions, labelled by **PHQ-8 / clinical confirmation** — not children, not spontaneous, not silver-labelled. The 79% / 90.53% F1 are **not targets Pebble can expect on child voice messages.** Child fundamental frequency, formants, speaking rate, and *how children voice distress* (indirectness, play, shorter utterances) are out-of-distribution for a wav2vec2 pretrained on adult English (LibriSpeech-family) — and the paper offers no child evidence at all. Use it for *pipeline ranking*, never as a bar.
- **Binary clinical depression ≠ Pebble's turn-level distress signal.** This is a single label per long interview ("is this person depressed?"). Pebble needs a **mid-conversation, turn/clip-level** distress/severity reading. The LSTM+self-attention head here selects informative segments *within one diagnostic session*; Pebble's analogous need is selecting informative *moments within a short clip* and across turns — a different temporal scale. The architecture's premise ("distress is sparse across a long recording") partly inverts for short child clips.
- **Emotion-transfer recall collapse is a child-safety-relevant warning.** The IEMOCAP-transfer recall of 54.17% means *nearly half of depressed cases missed* when transferring an emotion model without in-domain fine-tuning. For a child-facing safety signal, that failure mode is unacceptable — it directly supports keeping Pebble's v1 child-facing safety decision **text-led and heuristic** (per `docs/decisions.md`: no learned safety head in v1) and treating any voice severity head as exploratory until in-domain child data validates its recall.
- **Privacy/ethics of child voice is stricter than text.** Raw child audio is far more identifying than text (voiceprint, background speakers, location cues), and SSL embeddings are *not* anonymous. A child voice path needs on-device/tightly-controlled processing, deletion-by-default of raw audio after embedding, and guardian consent — a stricter regime than Pebble's text pipeline. The paper's corpora are consented clinical data; Pebble cannot inherit that consent basis for a companion app.
- **Low-resource transfer learning is the right *strategy* for Pebble.** The paper's core thesis — when labelled in-domain data is scarce, fine-tune a large SSL model rather than train from scratch or hand-craft features — is exactly Pebble's situation for child voice (almost no labelled child-distress audio exists). The recipe transfers even if the numbers don't.
- **Mitigations.** (1) Re-measure the whole pipeline on a child-speech corpus before trusting any ranking. (2) Prefer gradual-unfreeze / partial FT over full FT given child-data scarcity. (3) Always pair emotion→severity transfer with in-domain fine-tuning and a recall floor. (4) Keep voice as an *additive* signal to the text-led safety decision in v1, not a replacement. (5) Treat voice embeddings as PII.

### Limitations & open questions for Pebble

- **Contradiction/gap vs Pebble's turn-level, short-clip plan.** This pipeline is built for **long single-label recordings** (15-min interviews; many 7-s segments → LSTM+self-attention temporal head). Pebble scores **short, mid-conversation, turn-level** child clips. A 20–30 s child clip yields only ~3–5 segments — the LSTM+self-attention "select-the-informative-segment" machinery has almost nothing to select over, so the paper's headline architectural contribution (temporal segment selection, +4.28 F1) may **not transfer** to Pebble's regime. This is a genuine architectural mismatch, not just a domain gap: Pebble may be better served by a *single attention-pooled clip embedding* than by this paper's LSTM stack.
- **Contradiction vs paper 27 (Morais SSL-SER) on backbone fine-tuning depth.** Paper 27 fine-tunes the whole backbone *and* relies on **checkpoint weight-averaging** (+~2.3% WACC) as its biggest free win; this paper relies on **all-layer fine-tuning + a deeper downstream stack** and never uses checkpoint averaging. The two "best practice" recipes for an SSL emotion/affect head therefore diverge — Pebble should test checkpoint-averaging (cheap, from paper 27) *on top of* this paper's pipeline, since neither paper combined them. Also, paper 27 finds **wav2vec2 ≥ HuBERT and fusion best**; this paper uses **only wav2vec2** and never benchmarks HuBERT/WavLM — so Pebble's voice backbone choice (D-A) is *unresolved by this paper alone* and must include the WavLM column.
- **Tiny test sets → fragile numbers.** DAIC uses the **35-interview dev set** as de-facto test; CMDC has **78 total samples** and reports **AUC = 1.0** — a near-certain small-sample artifact, not evidence of a perfect classifier. No significance tests on any F1 delta. Pebble should treat the absolute numbers as illustrative and the *relative* ablation orderings as the transferable signal.
- **No calibration anywhere.** Like most of the Pebble set, accuracy/F1 only — but Pebble's Decision Engine consumes *probabilities*. A voice severity head must add the calibration evaluation this paper skips.
- **Speaker-disjointness not explicitly guaranteed beyond the standard DAIC split.** Speech models leak via speaker identity; if Pebble copies the pipeline it must enforce **speaker-disjoint folds** (per paper 27's discipline) to avoid inflated child-voice numbers.
- **Open question for Pebble.** Is there *any* licensed child-speech distress/depression corpus to anchor this pipeline? Without one, the voice path stays a research spike and the v1 child-facing safety decision remains text-led and heuristic (consistent with `docs/decisions.md`). Worth scoping a small consented in-house child-voice calibration slice — the audio analogue of Pebble's planned child-register text calibration slice.
