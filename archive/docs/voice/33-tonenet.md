# Paper 33 — ToneNet: A CNN Model of Tone Classification of Mandarin Chinese

## 1. Bibliographic info

**Title:** ToneNet: A CNN Model of Tone Classification of Mandarin Chinese

**Authors:** Qiang Gao, Shutao Sun (corresponding author), Yaping Yang — School of Computer and Cyberspace Security, Communication University of China, Beijing, China.

**Year / venue:** Interspeech 2019 (15–19 September 2019, Graz, Austria). *Proc. Interspeech 2019*, pp. 3367–3371. DOI 10.21437/Interspeech.2019-1483. Published in the ISCA Archive (`gao19c_interspeech`).

**Keywords (verbatim):** "ToneNet; tone classification; mel-spectrogram; Mandarin Chinese; convolutional neural networks".

**Funding (relevant to Pebble):** "Fundamental Research Funds for the Central Universities (2017XNG1749)" and **"the project of Research on Evaluation Technique of Children's Mandarin Speech Training (HG1711-1)"** — i.e. the paper's funding context is explicitly a *children's speech-evaluation* program.

> Framing for Pebble: this is a **voice-message-modality** paper. In the Pebble thesis, a voice
> message is a paralinguistic signal, and lexical-tone recognition is the canonical instance of a
> **pitch-contour / prosody-modeling** problem. ToneNet is the cleanest demonstration in the
> related-work set that a tone/pitch-contour classifier can be built as a **2-D image-CNN over a
> mel-spectrogram crop**, sidestepping fragile explicit F0 extraction. We read it for what its
> spectrogram-CNN tone module contributes to a Pebble voice front-end, not for Mandarin per se.

## 2. Problem motivation

Mandarin Chinese is tonal: the same syllable carries a different lexical meaning depending on which of four tones it bears — (1) flat-and-high, (2) rising, (3) low-and-dipping, (4) falling. Correct tone is "the key to convey word meaning correctly," so tone classification is "a critical part of speech evaluation system" and also matters for ASR error rate and for natural-sounding speech synthesis. The authors cite [5] (Chen, Wong, Hu 2014) that Mandarin sentence-recognition accuracy drops sharply when tone information is corrupted by noise.

The central technical complaint motivating the paper: **traditional tone classification relies on F0 (pitch) and energy, or on MFCCs, and these features are fragile** — "the extraction of these features is often subject to noise and other uncontrollable environmental factors." F0 in particular "is unstable to extract" and "easy to cause gradient explosion or non-convergence when acoustic features are used for training directly in deep learning." ToneNet's thesis is that a **mel-spectrogram image** retains "more raw information than F0," respects human auditory perception, and — when cropped to the low-frequency band where the tone contour lives — gives a robust, noise-tolerant feature that a CNN can read like an image.

## 3. Position in the literature

Three prior threads are contrasted:

- **F0 + energy classical prosody methods** [2] Levow 2006, [3] Lei et al. 2006 — reflect monosyllable prosody but are easily disturbed by environmental noise.
- **MFCC + DNN/CNN methods** — Ryant et al. [16] train a DNN on 40 MFCCs (27.38% frame error rate / 15.62% segment error rate, "without pitch tracking"); **Chen et al. [1] (Interspeech 2016)** use MFCCs into a CNN with a denoising autoencoder (dAE) pre-training step, reaching 95.53% accuracy — the strongest prior and ToneNet's direct comparison. The authors note Chen's dAE "still not overcome the influence of the noise completely."
- **Auditory-attention-cue methods** — Kalinli [13] (ICASSP 2011), tone-and-pitch-accent classification at only 72.8% accuracy.

The claimed gap: every prior method either depends on explicit, noise-fragile pitch/MFCC features, or underperforms. ToneNet replaces the feature pipeline with a cropped mel-spectrogram image fed to a VGG-style CNN, and reports a large jump (99.16% vs 95.53%).

## 4. Dataset deep dive — SCSC

**Syllable Corpus of Standard Chinese (SCSC).** Creator: The Institute of Linguistics, Chinese Academy of Social Sciences. It is a **monosyllabic** corpus: 1,275 monosyllabic Chinese characters, each pronounced by **15 young men**, for a total of **19,125 utterances**. Audio is **mono, 16-bit WAV, 16,000 Hz sample rate**; each clip is **~0.5–1 s** long.

**Split:** **8:1:1** train / validation / test. (≈15,300 / 1,912 / 1,912 utterances.) Train+val for fitting and hyperparameter tuning; test held out for final evaluation.

**Labels:** the four canonical tones (T1–T4). This is a balanced, clean 4-class problem — a single speaker register (young adult male), studio-clean monosyllables, gold phonetic labels. (Contrast with Pebble's noisy silver-label, child-register, in-the-wild regime — see §Child lens.)

**Access:** SCSC is an institutional corpus (Chinese Academy of Social Sciences); it is **not** one of the openly downloadable tone corpora in Pebble's `data/voice/external/` (those are AISHELL-1, THCHS-30, VIVOS). Treat SCSC as not directly obtainable; the *method* transfers, the *data* does not.

## 5. Method

### 5.1 Feature preprocessing — the cropped mel-spectrogram

- Full mel-spectrogram frequency range: **[0, 8000] Hz**, computed with **64 mel filters**, **frame length 2048 samples**, **frame shift 16 samples**, extracted with **librosa** [15].
- **Key insight:** tone information (the prosodic contour) lives in the **low-frequency band**. Human speaking F0 is ~100–300 Hz (lower for males, higher for females and children). The authors crop the mel-spectrogram to **[50, 350] Hz** — deliberately chosen "in order to cover the range of human tones' F0," explicitly including the higher F0 of **female and child** voices.
- The cropped low-frequency region is **saved as an RGB image** and used as the model input. Image size **(225, 225, 3)** is selected (see ablation §6).

### 5.2 ToneNet architecture (Table 1)

A 5-layer CNN feature extractor + 3-layer MLP classifier, three modules:

| Module | Layers |
|---|---|
| **Part-1** (input) | Conv2d(f=5×5, 64 filters, stride 3) → BatchNorm → MaxPool(3×3, stride 3). Output 25×25×64. Big kernel + stride 3 for dimensionality reduction + coarse feature extraction. |
| **Part-2** (VGG-style) | 4× [Conv2d(f=3×3, stride 1) → BatchNorm → MaxPool(2×2, stride 2)], with filter counts **128 → 256 → 256 → 512**. Follows VGGNet's "stack small 3×3 kernels instead of one large kernel" principle. Output 2×2×512. |
| **Flatten** | connects conv stack to MLP. |
| **Part-3** (MLP) | FC-1024 → BatchNorm → FC-1024 → BatchNorm → **FC-4 → SoftMax** (4 tones). |

> Note: §3 prose says Part-1's kernel count is 64 and Part-2's first conv has 128; the abstract/§contributions describe it as "an efficient 5-layer CNN feature extractor + a 3-layer MLP classifier." Table 1 is authoritative for the per-layer filter counts (64 / 128 / 256 / 256 / 512). ≈ (one internal prose inconsistency: the running text once says "2×2×512 in Part-2" matching the table).

**Training config:** activation **ReLU** (Eq. 1, `f(x)=max(0, wᵀx+b)`); loss **categorical cross-entropy**; optimizer **SGD with momentum + Nesterov**; base learning rate **0.001**; mini-batch **128**; **50 epochs**. BatchNorm after every conv layer (cited for faster convergence + overfitting prevention).

### 5.3 Interpretability

**Grad-CAM** [14] on the last conv layer, rendered as a heat map over the input mel-spectrogram (Figure 5). The heat maps confirm ToneNet attends to the **bright pitch-contour band** of each tone — "the same as our human being on vision" — evidence the network learned the prosodic contour rather than a spurious cue.

## 6. Experiments and results

### 6.1 Frequency-band × image-size ablation (Table 2)

Six configs: {low-freq [50,350] Hz, full-freq [0,8000] Hz} × {(113,113,3), (225,225,3), (449,449,3)}.

| Config | Accuracy % | F1 % | Test loss |
|---|---|---|---|
| low-freq (113²) | 97.90 | 97.83 | 0.06207 |
| **low-freq (225²)** | **99.16** | **99.11** | **0.05153** |
| low-freq (449²) | 99.00 | 98.93 | 0.05312 |
| full-freq (113²) | 96.86 | 96.68 | 0.08151 |
| full-freq (225²) | 97.73 | 97.57 | 0.07082 |
| full-freq (449²) | 97.75 | 97.60 | 0.07011 |

Findings: (a) **low-frequency crop beats full-frequency** at every image size (lower test loss too) — discarding the high-frequency band that carries no tone information helps; (b) **(225²) ≈ (449²)** so the smaller image is chosen for memory/speed; (c) best config = **low-freq + (225²) = 99.16% acc / 99.11% F1**.

### 6.2 Comparison vs prior methods (Table 3)

| System | Acc | P | R | F1 | Data |
|---|---|---|---|---|---|
| Kalinli [13] | 72.80 | — | — | — | MCCC |
| Chen et al. [1] | 95.53 | 93.51 | 94.63 | 94.06 | MCCS |
| Chen et al. [1] (re-run) | 94.45 | — | — | — | SCSC |
| **ToneNet (ours)** | **99.16** | **99.08** | **99.14** | **99.11** | **SCSC** |
| ToneNet (ours, +Gaussian noise) | **97.07** | **96.81** | **96.85** | **96.83** | SCSC (noise) |
| Chen et al. [1] (+Gaussian noise) | 92.15 | 91.40 | 92.35 | 91.87 | SCSC (noise) |

(Conclusion §5 restates ToneNet clean = 99.16 acc / 99.08 P / 99.14 R / 99.11 F1.)

Because the three baselines used different datasets, the authors **re-implemented Chen et al. [1] on SCSC** for a fair fight: Chen drops to 94.45% on SCSC, still well below ToneNet's 99.16%. Under **added Gaussian noise**, ToneNet degrades gracefully to 97.07% acc / 96.83% F1, beating noisy-Chen (92.15% / 91.87%) by ~5 points — the noise-robustness claim that motivated the mel-spectrogram choice.

### 6.3 Confusion matrix (Table 4, clean test)

| true \ pred | T1 | T2 | T3 | T4 |
|---|---|---|---|---|
| **T1** | 536 | 0 | 1 | 0 |
| **T2** | 0 | 394 | 2 | 0 |
| **T3** | 2 | 7 | 451 | 1 |
| **T4** | 0 | 1 | 2 | 515 |

Almost perfect; the main confusion is **T3 (low-dipping) ↔ T2 (rising)** (7 + 2 errors), which is the linguistically expected confusable pair (Tone-3 sandhi and a partial rise share contour shape).

## 7. Authors' stated limitations (implicit)

The paper is short and bullish; it does not enumerate limitations, but the read surfaces them: (1) **monosyllabic only** — no continuous speech, no co-articulation / tone-sandhi context (cf. paper #36 J-ToneNet, which targets continuous Mandarin); (2) **single narrow speaker register** — 15 young men, one corpus, studio-clean; no female/child/elderly speakers actually in the data despite the F0 crop being sized for them; (3) **only synthetic Gaussian noise** tested, not real-world reverberation/codec/microphone noise; (4) **no calibration / probability quality** reported — accuracy/F1 only; (5) the prosody-image crop hyperparameters ([50,350] Hz, 64 mels) are tuned to adult-male F0 and would need re-tuning for child voices.

---

## Deep research — full-PDF read (2026-06-16)

> Decision IDs this paper is read to move: **D-A** (encoder/feature-extraction backbone for the
> voice modality), **D-D** (transfer source + metric for pitch-contour / prosody regression),
> **D-H** (datasets / substitutes). Read against the authoritative ISCA-Archive venue version
> (`gao19c_interspeech`, *Proc. Interspeech 2019* pp. 3367–3371, DOI
> 10.21437/Interspeech.2019-1483); local PDF is `pdfs/33-tonenet.pdf`.

### Source-access note

- **PDF read:** full text extracted with `pdftotext "docs/papers/pdfs/33-tonenet.pdf" -` (the Read
  tool cannot render PDFs in this repo, per project memory). All five sections + all four tables +
  abstract + references were read end-to-end. Figures (mel-spectrograms, architecture diagram,
  Grad-CAM heat maps) are images and were read via their captions/surrounding text only.
- **Web validation:** the four headline numbers were confirmed against the **published venue
  version**.
  - Query: `"ToneNet CNN Tone Classification Mandarin Chinese Interspeech 2019 Gao Sun Yang 99.16% accuracy mel-spectrogram"` → resolved the ISCA Archive landing page
    `https://www.isca-archive.org/interspeech_2019/gao19c_interspeech.html`.
  - WebFetch of that URL confirmed: **clean 99.16% acc / 99.11% F1**, **+Gaussian-noise 97.07% acc / 96.83% F1**, dataset **SCSC**, authors Gao/Sun/Yang, citation "*Proc. Interspeech 2019*, 3367-3371," **DOI 10.21437/Interspeech.2019-1483**. ✔ Local PDF and venue agree exactly — this is a camera-ready Interspeech paper, no preprint delta.
- **Numbers status legend:** ✔ corroborated against venue version / ≈ approximate or internally
  derived / ✖ uncorroborated.

### What the paper actually does

- **Task:** 4-way Mandarin **lexical-tone** classification of isolated monosyllables (T1 flat-high,
  T2 rising, T3 low-dipping, T4 falling). [§1] ✔ (task corroborated by venue abstract).
- **Feature:** a **mel-spectrogram cropped to the low-frequency band [50, 350] Hz** (64 mel filters,
  frame length 2048, hop 16, via librosa), saved as a **(225×225×3) RGB image**. The crop band is
  chosen to span human F0 including **female and child** ranges. [§2, §4] ✔ (mel-spectrogram feature
  confirmed by venue abstract; crop/hop specifics ≈ from PDF only).
- **Model:** **5 conv layers (64→128→256→256→512, VGG-style 3×3 stacks after a 5×5 stride-3 stem,
  BatchNorm + MaxPool throughout) + 3-layer MLP (1024→1024→4) + softmax.** SGD+Nesterov, LR 0.001,
  batch 128, 50 epochs, categorical cross-entropy. [Table 1, §3, §5.2 above] ✔ (architecture family
  confirmed by venue abstract: "customized CNN + MLP"; per-layer filter counts ≈ from Table 1 only).
- **Results:** **99.16% acc / 99.11% F1** clean; **97.07% acc / 96.83% F1** under Gaussian noise.
  [Abstract, Table 2, Table 3, Conclusion] ✔ corroborated.
- **Key ablation:** **low-freq crop beats full-freq at every image size** (e.g. 99.16 vs 97.73 at
  225²); (225²) ≈ (449²) so the smaller image wins on cost. [Table 2] ≈ (internal table; the
  headline 99.16 is the ✔ venue number).
- **Baseline beat:** re-implemented Chen et al. 2016 [1] on the same SCSC data → 94.45%, vs ToneNet
  99.16%; under noise ToneNet 97.07% vs Chen 92.15%. [Table 3] ≈ (internal table).
- **Interpretability:** Grad-CAM heat maps show the CNN attends to the bright pitch-contour band —
  it learned the prosody, not a shortcut. [§4, Fig 5] ≈.

### Parts directly useful for Pebble (each tagged with Decision IDs)

1. **Spectrogram-as-image + 2-D CNN replaces explicit F0 extraction** — the whole architectural
   thesis. For Pebble's voice-message front-end, a tone/pitch-contour head does **not** need a
   fragile pitch tracker; a log-mel spectrogram fed to a small 2-D CNN is enough and is more
   noise-robust. **(D-A)** — a candidate *prosody/tone encoder* for the voice modality, distinct
   from the NeoBERT text backbone. **(D-D)** — establishes mel-spectrogram (not raw F0) as the
   transfer feature for any pitch-contour-derived signal Pebble computes (e.g. an energy/arousal
   proxy from prosody).
2. **Low-frequency crop [50, 350] Hz, sized to include child F0** — the single highest-leverage
   feature-engineering choice (low-freq beats full-freq everywhere; Table 2). **(D-D, D-A)** — a
   concrete, copyable preprocessing config for a Pebble prosody encoder; the band is *already* sized
   to include children's higher F0, which is exactly Pebble's population.
3. **Graceful degradation under additive noise (97.07% vs adult clean 99.16%; +5 pts over the MFCC
   baseline under noise)** — empirical evidence that the mel-spectrogram-CNN recipe is robust to the
   kind of noise a child's phone microphone will add. **(D-A, D-G)** — supports choosing the
   spectrogram-CNN over MFCC/F0 pipelines when input quality is uncontrolled, and is the noise-floor
   datapoint for a recall/threshold policy on a voice head.
4. **Concrete training recipe for a small spectrogram CNN** — VGG-style 3×3 stacks, BatchNorm after
   every conv, SGD+Nesterov LR 0.001, batch 128, 50 epochs, (225²) input. **(D-A)** — a known-good
   starting hyperparameter set for a Pebble prosody-CNN ablation, avoiding a blind search.
5. **Grad-CAM as the validation that a spectrogram CNN learned the contour, not an artifact** —
   **(D-A, D-G)** — a cheap, publishable sanity check Pebble can reuse to show a voice head attends
   to prosody rather than speaker identity/channel.
6. **Dataset substitution note** — SCSC is institutional/closed; the *open* tone corpora Pebble
   already tracks (AISHELL-1, THCHS-30 under `data/voice/external/`, and **VIVOS** for Vietnamese) are the
   reproducible substitutes. **(D-H)** — if Pebble builds a tone/prosody probe, train on the open
   corpora, cite ToneNet for the method, not for the data.

### How each part helps Pebble succeed

- **Voice front-end design (1) → a `prosody_cnn` module.** If/when Pebble ingests voice messages,
  build a small 2-D CNN over log-mel spectrograms as a *paralinguistic encoder* feeding the same
  multi-task head bank as the text path. Do **not** ship an explicit F0/pitch-tracker — ToneNet is
  the citation that this is both unnecessary and more brittle. Action: a `voice/prosody_cnn.py`
  experiment that mirrors Table 1's stack, output pooled to a fixed embedding, concatenated with the
  NeoBERT text embedding before the heads.
- **Child-sized crop (2) → preprocessing config.** Adopt the **[50, 350] Hz low-band crop, 64 mel
  filters** as the default for the prosody encoder, and **re-tune the upper bound upward** for child
  voices (children's F0 routinely exceeds 350 Hz; ToneNet sized the band for adult male + female +
  "child" but its *data* was adult-male only — so treat 350 Hz as a floor to raise, not a ceiling).
  Action: a config knob `prosody.freq_band=[50, 500]` and an ablation sweeping the upper bound on a
  child-voice slice.
- **Noise robustness (3) → the voice-head recall story.** Pebble's input is uncontrolled phone
  audio. ToneNet's +Gaussian-noise number (97.07%, only −2 pts from clean, and +5 pts over MFCC)
  is the evidence to budget for a small clean→noisy gap on a prosody head and to prefer the
  spectrogram recipe over openSMILE/eGeMAPS hand-features (#29/#30) when robustness matters more than
  interpretability. Action: add Gaussian + reverberation augmentation to the prosody-CNN training
  and report the clean/noisy delta.
- **Training recipe (4) → skip the blind search.** Seed the prosody-CNN ablation with ToneNet's
  hyperparameters (SGD+Nesterov, LR 0.001, BN-everywhere, batch 128) before trying anything fancier;
  it is a documented 99%+ config on a 4-class contour problem.
- **Grad-CAM (5) → publishable validation slide.** Run Grad-CAM (or an attention-rollout analogue)
  on the prosody-CNN to show it lights up on the pitch contour, not on channel/speaker artifacts —
  the same trust-building evidence Pebble needs for any new modality head.
- **Open-data substitution (6) → reproducibility.** Because SCSC is closed, any Pebble prosody probe
  must train on AISHELL-1 / THCHS-30 / VIVOS. This keeps the pipeline reproducible and license-clean
  (THCHS-30/AISHELL-1 Apache-2.0; VIVOS is CC-BY-NC-SA → research-only, no deploy).

### Child mental-health lens

- **The crop band is the only child-aware design choice, and the data does not back it.** ToneNet
  explicitly sizes [50, 350] Hz "to cover ... the F0 of female and child," and its **funding is a
  children's Mandarin speech-training evaluation project (HG1711-1)**. *But the SCSC corpus is 15
  young men only.* So the paper's child relevance is **aspirational, not validated**: the method is
  designed with children in mind, the evaluation never includes a child voice. For Pebble this is a
  red flag and an opportunity — the child-F0 band must be empirically re-tuned (children's F0 often
  250–500 Hz, exceeding ToneNet's 350 Hz ceiling), and a child-voice evaluation slice is a genuine
  contribution no one in this voice set has produced.
- **Tone classification ≠ emotion/severity — borrow the *plumbing*, not the *label*.** Pebble's
  heads are emotion (12-label) and severity (regression). ToneNet classifies lexical tone, a
  *linguistic* category, not affect. The transfer is strictly at the **feature + encoder** level
  (mel-spectrogram → 2-D CNN → pooled embedding); the *contour-reading* capability is what Pebble
  reuses to derive prosodic arousal/energy cues, **not** ToneNet's softmax-over-4-tones head.
- **Register & channel mismatch.** SCSC is studio-clean, 16 kHz, monosyllabic, single dialect/accent.
  Pebble voice messages are in-the-wild, codec-compressed, continuous, multi-accent, child-register.
  The clean 99.16% will **not** transfer as an accuracy number; only the *relative* robustness story
  (spectrogram beats F0/MFCC under noise) transfers. State plainly: **a corroborated adult-male
  studio tone number does not predict child-voice in-the-wild performance.**
- **Privacy/ethics.** Voice is biometric and re-identifiable; child voice doubly so. A Pebble voice
  module needs explicit consent, on-device or controlled-access processing, and should derive
  *low-dimensional prosodic features* (contour energy, not stored raw audio) wherever possible —
  ToneNet's "save the low-freq crop as an image" step is, conveniently, already a lossy
  representation that discards intelligible speech content (it keeps only [50,350] Hz), which is a
  privacy-friendly property worth preserving.

### Limitations & open questions for Pebble

- **Contradiction-or-gap #1 (vs paper #36 J-ToneNet and #34 Lugosch CTC):** ToneNet works **only on
  isolated monosyllables** and (per Table 4) its residual errors are exactly the T2↔T3 contour pair
  that **continuous-speech context** disambiguates. J-ToneNet (#36) and Lugosch (#34) target
  *continuous* Mandarin where co-articulation and tone-sandhi dominate. Pebble voice messages are
  continuous, conversational, emotionally inflected speech — so **ToneNet's monosyllabic 99.16% is an
  upper-bound that overstates real performance**; the continuous-speech papers are the more honest
  bar. Do not cite 99.16% as an achievable Pebble number.
- **Contradiction-or-gap #2 (vs the hand-feature lineage #29 openSMILE / #30 eGeMAPS):** ToneNet
  argues *against* explicit acoustic features (F0/MFCC) in favor of a learned CNN over spectrograms;
  the eGeMAPS/openSMILE lineage argues *for* a compact, interpretable, clinically-validated
  hand-feature set. For Pebble's mental-health prosody signal this is an unresolved
  **learned-vs-handcrafted** tension: ToneNet wins on raw accuracy and noise robustness, eGeMAPS wins
  on interpretability, small-data stability, and a track record in affective/clinical voice work.
  Pebble must choose (or fuse) deliberately — this paper alone does not settle it.
- **No calibration, no continuous speech, no real noise, no child/female voice in-data, no speaker
  generalization test.** Every one of these is a gap Pebble would have to close before a voice head
  could be trusted in a child-facing safety pipeline.
- **Open question — is a tone/prosody head even on Pebble's v1 path?** Per `docs/decisions.md`, v1
  trains only text `emotion` + `severity`; voice is a thesis-level modality, not a v1 deliverable.
  ToneNet is therefore **forward-looking evidence for a v2 voice branch (D-A/D-D)**, not a v1
  blocker. Its concrete contribution to v1 is narrow: it validates "mel-spectrogram → small 2-D CNN"
  as the architecture to prototype first when voice does land.
- **Open question — SCSC access.** SCSC is institutional (CASS Institute of Linguistics) and not in
  Pebble's open-data set; whether it is obtainable at all is unverified. Default to AISHELL-1 /
  THCHS-30 / VIVOS as the reproducible substitutes **(D-H)**.
