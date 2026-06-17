# Paper 34 — Tone Recognition Using Lifters and CTC

## 1. Bibliographic info

**Title:** Tone Recognition Using Lifters and CTC

**Authors:** Loren Lugosch, Vikrant Singh Tomar (Fluent.ai Inc., Montréal, Québec, Canada).

**Year / venue:** Interspeech 2018 (Hyderabad, India), pp. 2305–2309. DOI 10.21437/Interspeech.2018-2293. Preprint: arXiv:1807.02465v1 [eess.AS], 6 Jul 2018.

**Index terms (verbatim):** "tone recognition, tonal languages, speech recognition, cepstrogram, sequence processing, deep learning, CTC".

**One-line:** A trainable cepstrogram + CNN ("lifter") front-end feeding a BiGRU-CTC head that recognizes the sequence of Mandarin tones in *continuous* utterances end-to-end (no forced alignment, no syllable segmentation), reaching 11.7% tone error rate on AISHELL-1 — the best reported for continuous Mandarin tone recognition at the time.

## 2. Why this paper is in Pebble's set (the voice-message lens)

Pebble's thesis includes a **voice-message modality**: children send spoken messages, and Pebble must extract affect/prosody-bearing signal from *real, continuous, casually-spoken* audio — not isolated, carefully-articulated syllables. Tone (pitch-pattern) recognition is the closest published, fully-supervised sequence task to "extract a prosodic label sequence from a real utterance." This paper matters to Pebble for three reasons:

1. **It targets continuous speech, not isolated syllables.** Most prior tone work (e.g. Chen et al. 2016, 4.5% TER) classifies one carefully-spoken syllable at a time. That regime does not exist in a voice message. Lugosch & Tomar deliberately solve the harder problem where tone *boundaries are unknown* — exactly Pebble's setting.
2. **It is end-to-end with a sequence-level (CTC) loss**, so it needs **no frame-level labels and no forced alignment**. Pebble cannot obtain frame-aligned affect labels on children's voice messages; a CTC-style sequence head is the only label regime that scales to silver-labelled audio.
3. **The "lifter" front-end is a learned, discrimination-optimized pitch feature** — a template for replacing hand-engineered prosody features (F0/PoV) with features the network learns for the downstream task. Pebble's prosody/energy signal extraction faces the same hand-feature-vs-learned-feature choice.

## 3. Problem motivation

Tones are phonologically contrastive in many languages: in Mandarin, "mom" (mā), "hemp" (má), "horse" (mǎ), and "scold" (mà) share the same two phones and differ *only* in tone. ASR for tonal languages therefore cannot rely on phones alone.

Standard ASR features (MFCCs, FBANKs, PLP) carry no pitch information, so state-of-the-art tonal recognizers **append hand-decision pitch features (HDPFs)** — an F0 estimate plus probability-of-voicing (PoV) per frame [Ghahremani et al. 2014]. The authors' central hypothesis: **HDPFs throw away information.** By analogy to phone recognition — where recognizers do not explicitly estimate formants yet implicitly learn them and more — a model that consumes *all* the signal can out-discriminate one fed only the linguistically-motivated pitch summary. They cite Ryant et al. 2014, where an MFCC-only recognizer "handily outperforms" an F0+amplitude recognizer, as direct evidence that F0 is not the optimal tone feature.

Second motivation: **reproducibility.** Prior tone work used expensive/in-house corpora (HKUST/MTS, CALLHOME), preventing objective comparison. They use **AISHELL-1**, a freely-downloadable LVCSR corpus (openslr.org/33), so results are reproducible.

## 4. Position in the literature

Three threads are contrasted:

- **HDPF-based recognizers.** Huang et al. 2000 (F0 + delta-F0 + degree-of-voicing → GMM); Lei et al. 2006 (F0 contour + syllable duration → MLP); RNN tone recognizers fed MFCC+HDPF [Huang et al. 2017]; tonal-phone models [Liu et al. 2015; Metze et al. 2013].
- **Alternative spectral features.** Li et al. 2011 and Kalinli 2011 (Gabor filters on the spectrogram → frame-level MLP, requiring forced alignment); Deep Speech 2 [Amodei et al. 2016] (raw spectrogram → Chinese characters, pitch learned implicitly).
- **Isolated-syllable CNN classifiers.** Chen et al. 2016 (window of MFCCs → CNN per single syllable, 4.5% TER on isolated syllables).

The claimed gaps: (1) HDPF/derivative features discard useful information; (2) frame-level approaches need forced alignment or manual labelling — "tedious and expensive." The fix: a **cepstrogram** input (not spectrogram) from which features are *learned*, plus a **sequence-level CTC** criterion that removes the alignment step.

## 5. Method

The recognizer is one neural network with three stages (Fig. 1): a preprocessing module → a convolutional ("lifter") network → a recurrent (BiGRU-CTC) network, trained end-to-end with SGD.

### 5.1 Preprocessing — the cepstrogram

The signal is framed into short overlapping windows (25 ms with 10 ms stride), each multiplied by a **Hamming window** (length 512). For each windowed frame `x` the **cepstrum** is computed:

```
cepstrum(x) = IDFT( log |DFT(x)| )                                   (Eq. 2)
```

Crucially, **no Mel filterbank is applied** — Mel smoothing would blur the periodic peaks of the spectrum, hiding pitch. The raw spectrum is used. The cepstrogram is the concatenation of all cepstra across time. The motivation (§3.1): in the cepstrogram, **the pitch of a voice appears as a single localized peak at each timestep** (Fig. 2), whereas in the spectrogram pitch is a *global* harmonic pattern — far harder to learn. The cepstrogram, like the spectrogram, preserves all information except phase.

### 5.2 Convolutional network — "lifters"

Three convolutional layers with ReLU and max-pooling. The authors call the conv filters **lifters** and their output feature maps **lifter features (LFs)**, because convolving in the cepstral ("quefrency") domain *is* liftering. Rationale: tone identity is **translation-invariant** in time and frequency (a melody is the same sung at a different time or key), so convolution + pooling extract translation-invariant patterns and aggressively downsample both time and quefrency — improving invariance and shortening the sequence the RNN must process. Per Table 1, each conv layer is `11×11, 16 lifters, stride 1`, each pool is `4×4 max, stride 2`, all ReLU. A 50% dropout follows the conv stack. LFs (last conv layer's maps) are stacked per timestep into a 2D map for the RNN.

### 5.3 Recurrent network — BiGRU + CTC

A **bidirectional GRU with 128 hidden units per direction** translates the LF sequence into a tone sequence via **CTC** [Graves et al. 2006]. CTC removes the alignment/segmentation step: training needs only the *tone-label sequence*, not frame-level labels. CTC is "ideal for modelling sequences of events in which the same event may occur multiple times consecutively" — exactly tone sequences. The output affine layer has **6 outputs: 5 Mandarin tones + 1 CTC blank**.

### 5.4 Training & decoding (§4.1)

- Loss: standard CTC loss `−log p(Y|X)`, optimized by SGD.
- Optimizer: **Adam**, initial LR **0.001**, gradient clipping; LR **halved** at end of an epoch if dev loss rose. **20 epochs**.
- **SortaGrad** curriculum [Amodei et al. 2016]: first epoch draws sequences in length order, then randomly.
- Decoding: greedy. A very-wide-beam search improved TER by only **0.1%** over greedy for all recognizers, so greedy results are reported.
- Tooling: **Kaldi** AISHELL-1 recipe to prepare the corpus and compute 13-dim MFCCs + 3-dim HDPFs (for Baseline 1), per-utterance normalized to zero mean / unit variance.

### 5.5 Baselines / ablations

- **Baseline 1:** RNN-CTC on `MFCC + HDPF`. Given a *second* recurrent layer with dropout and **160 hidden units/layer** — deliberately *more parameters than the proposed model* to give it an advantage.
- **Baseline 2:** identical to the proposed model but with the **first 25 cepstral coefficients zeroed** (231 of 256 kept) — i.e. only the **high-time (HT) cepstrum** (glottal-excitation/pitch) retained, low-time (vocal-tract) info erased. Tests how important "non-pitch" information is.
- **Spectrogram-based recognizer:** proposed model with the IFFT removed (spectrogram input). **It was unable to learn** and is excluded from the table — empirical support that the cepstrogram is the right input.

## 6. Data — AISHELL-1 (§4.1)

| Split | Utterances | Speakers | Hours |
|---|---|---|---|
| Train | 120,098 | 340 | 150 |
| Dev | 14,326 | 40 | 10 |
| Test | 7,176 | 20 | 5 |
| **Total** | — | **400** | **165** |

165 hours of **clean speech**, 400 speakers from across China (47% male / 53% female), noise-free environment, 16-bit, resampled to 16 kHz. Free at openslr.org/33.

## 7. Results

**Headline (Table 2):** the proposed `CG → CNN → RNN + CTC` recognizer reaches **TER 11.7%** — best in the table by a wide margin, and "to our knowledge the best reported error rate for tone recognition in continuous Mandarin speech."

| Method | Model & input | TER |
|---|---|---|
| Lei et al. | HDPF → MLP | 23.8% |
| Kalinli | Spectrogram → Gabor → MLP | 21.0% |
| Huang et al. | HDPF → GMM | 19.0% |
| Huang et al. | MFCC + HDPF → RNN | 17.1% |
| Ryant et al. | MFCC → MLP | 15.6% |
| **Baseline 1** | MFCC + HDPF → RNN + CTC | 18.1% |
| **Baseline 2** | HT cepstrogram → CNN → RNN + CTC | 15.1% |
| **Proposed** | cepstrogram → CNN → RNN + CTC | **11.7%** |

The authors caution it is "not entirely fair" to compare across the literature's differing datasets; the controlled comparison is **Proposed (11.7%) vs Baseline 1 (18.1%) vs Baseline 2 (15.1%)** on the same AISHELL-1 split. Baseline 1 is the closest analogue to Huang et al. 2017 — but note their RNN classifies each *syllable separately* (boundaries given), while the proposed model gets *no tone locations* and must learn from the tone sequence alone: a strictly harder problem, yet it wins.

**Error breakdown (Table 3):** the proposed model makes slightly *more* insertions (544 vs 467) but far fewer deletions (1,382 vs 4,934) and substitutions (21,854 vs 31,459) than Baseline 1.

**Per-tone accuracy (Table 4):**

| | Tone 0 | Tone 1 | Tone 2 | Tone 3 | Tone 4 |
|---|---|---|---|---|---|
| Baseline 1 | 77.2% | 81.7% | 88.1% | 69.5% | 85.7% |
| Proposed | 73.6% | 90.6% | 88.9% | **82.9%** | 91.9% |

Both struggle on **Tone 0** (the neutral tone). **Tone 3** is hard (often confused with Tone 2 due to **tone sandhi** — a 3rd-tone–3rd-tone sequence /3,3/ surfaces as [2,3]; once realized, /3,3/ and /2,3/ are acoustically indistinguishable and only a **language model** can disambiguate). The LF model improves Tone 3 markedly (69.5% → 82.9%).

**Two "honorable mentions" (§4.2.1):**
- Lei et al.: extracting tones from a *full ASR transcript* gave **9.3% TER** vs 23.8% acoustic-only — because the language model fixes tone errors ("call my mom" > "call my hemp"). This paper studies the **acoustic tone model alone**, trained on tone labels only.
- Chen et al. 2016: **4.5% TER** but on *isolated syllables* — an easier task (careful articulation; isolated tones are partly recoverable from syllable *duration*, whereas continuous-speech tones share roughly equal duration).

## Deep research — full-PDF read (2026-06-16)

> Read the full local PDF `pdfs/34-lugosch-tone-ctc.pdf` (arXiv:1807.02465v1, 6 Jul 2018) end-to-end —
> abstract, all five sections, Equations 1–2, Figures 1–2, and all four tables. The published version is
> Interspeech 2018, pp. 2305–2309, DOI 10.21437/Interspeech.2018-2293; the arXiv preprint and the ISCA
> version are content-identical (same author block, same numbers), so published-vs-preprint conflict does
> not arise here. Numbers below are tagged ✔ corroborated against the venue metadata + arXiv text,
> ≈ approximate, or ✖ uncorroborated.

### Source-access note

- PDF extracted via `pdftotext "docs/papers/pdfs/34-lugosch-tone-ctc.pdf" -`; full text read including the (slightly garbled but legible) Tables 1–4. Mojibake in the raw extract ("Montre�al") was reconstructed from context.
- Venue/provenance validation:
  - Query `Lugosch Tomar "Tone recognition using lifters and CTC" Interspeech 2018 tone error rate 11.7% AISHELL-1` → ISCA Archive page `https://www.isca-archive.org/interspeech_2018/lugosch18_interspeech.html` confirms **Interspeech 2018, pp. 2305–2309, DOI 10.21437/Interspeech.2018-2293, AISHELL-1**. ✔
  - The ISCA abstract corroborates the *method* (cepstrogram → CNN → CTC) and the *dataset* (AISHELL-1) and the qualitative claim ("outperforms existing techniques in TER"); it does **not** print the numeric 11.7% in the HTML excerpt. The numeric values (11.7% / 15.1% / 18.1% / Tables 1–4) are taken from the arXiv full text, which is the same paper. Status for the numbers: ✔ for the headline TER and dataset split (cross-checked against AISHELL-1's published spec); ≈ for the exact per-tone percentages (single-source, preprint table, mild OCR risk but internally consistent).
  - arXiv landing `https://arxiv.org/abs/1807.02465` and author publication page `https://lorenlugosch.github.io/publication/2018-09-01-tone` corroborate authorship, year, and the lifter/CTC framing. ✔
- AISHELL-1 split (120,098 / 14,326 / 7,176 utts; 340/40/20 spk; 150/10/5 h; 165 h total, 400 spk) ✔ — these match the corpus's own published spec (Bu et al. 2017, arXiv:1709.05522 / openslr.org/33), an independent corroboration of the paper's data table.

### What the paper actually does

- **Task.** Sequence prediction of Mandarin tones in *continuous* speech: input waveform `X`, output tone sequence `Y` over alphabet of 5 tones; metric **TER = Levenshtein (I+D+S)/U** (Eq. 1). ✔
- **Front-end (learned pitch feature).** Waveform → 25 ms/10 ms Hamming frames → cepstrum `IDFT(log|DFT(x)|)` with **no Mel filterbank** (preserves pitch peaks) → cepstrogram → **3× conv ("lifter") layers, each 11×11, 16 filters, stride 1, + 4×4 max-pool stride 2, ReLU, then 50% dropout** (Table 1). ✔
- **Back-end.** **BiGRU, 128 units/direction → CTC, 6 outputs (5 tones + blank)** (Table 1, §3.3). ✔
- **Training.** CTC loss `−log p(Y|X)`, Adam, LR 0.001 with halving-on-dev-plateau, gradient clipping, 20 epochs, SortaGrad length-curriculum, greedy decode (beam helped only 0.1%). ✔ Kaldi recipe for corpus prep + 13-dim MFCC + 3-dim HDPF baselines, per-utterance CMVN. ✔
- **Headline result.** **TER 11.7%** (Table 2), best for continuous Mandarin tone recognition; beats Baseline 1 (MFCC+HDPF→RNN-CTC, 18.1%) and Baseline 2 (high-time cepstrogram only, 15.1%) on the *same* split. ✔ (headline) / ≈ (baseline decimals, single-source table)
- **Ablation findings.** (a) Spectrogram input **failed to learn** → cepstrogram is the right representation. (b) Baseline 2's 15.1% (vs proposed 11.7%) shows **"non-pitch" low-time cepstral info is genuinely useful** for tone — confirming the paper's core hypothesis that HDPFs discard useful signal. (c) Error breakdown: the model trades a few more insertions for far fewer deletions/substitutions (Table 3). (d) Per-tone: big win on Tone 3 (69.5%→82.9%), residual difficulty on neutral Tone 0; Tone-3/Tone-2 confusion is attributed to **tone sandhi**, fixable only with a language model. ✔ / ≈

### Parts directly useful for Pebble

1. **End-to-end CTC over a learned front-end with no frame alignment** (§3.3, §5) — **[D-A, D-B]**. The entire architecture is "learned features → sequence model → sequence-level loss," trainable from *sequence labels only*. For Pebble's voice-message head this is the label regime that scales: you never get frame-aligned affect labels on children's audio, so a CTC (or CTC-style) sequence criterion is the mechanism that lets a silver-labelled label *sequence* (e.g. per-utterance prosodic/affect tags) supervise a continuous-audio encoder. Tied to D-A (the modality encoder choice must support a CTC/sequence head) and D-B (CTC is itself a loss-balancing-free way to handle variable-length, repeated-event targets — relevant when choosing how the voice head's loss composes with the text MTL heads).
2. **Cepstrogram (raw-spectrum cepstrum, no Mel) as the pitch-preserving input** (§3.1, Eq. 2) — **[D-D]**. Pebble's `energy` / prosody signal is heuristic in v1 but a v2 candidate for a learned regression. The paper's evidence that **Mel smoothing destroys the pitch peak** and that the **cepstrogram localizes pitch to one peak/timestep** is a concrete feature-engineering directive: if Pebble ever learns a prosody/energy head from voice messages, feed it a (non-Mel) cepstrogram or an explicit pitch channel, not plain log-Mel. D-D is the regression-source/feature decision.
3. **"Lifter" CNN as a learned replacement for hand-engineered F0/PoV features** (§3.2, §5.5 Baseline 1) — **[D-D, D-F]**. The controlled result — learned cepstral features (11.7%) beat hand-crafted MFCC+HDPF (18.1%) *despite the baseline having more parameters* — is direct evidence for **learned over hand-engineered prosody features**. For Pebble: a learned audio front-end (or a domain-adaptive pre-trained audio encoder) should outperform piping hand-extracted F0/energy summaries into the head. Maps to D-D (feature/transfer source) and D-F by analogy (a self-supervised/domain-adaptive front-end pass before head fine-tuning).
4. **Concrete, reproducible hyperparameters for a small CTC tone/prosody head** (Table 1, §4.1) — **[D-A, D-E]**. 3 conv layers (11×11/16/s1) + 4×4 pool, 50% dropout, BiGRU-128, Adam LR 0.001 with plateau-halving, 20 epochs, SortaGrad, greedy decode. This is a turnkey recipe Pebble can clone for a first voice-message prosody/affect prototype on a public tonal/affect corpus before touching child audio. D-E is the staged fine-tuning / schedule decision (LR halving + length curriculum are directly reusable).
5. **AISHELL-1 as a free, large, reproducible audio corpus + the openslr.org/33 access pattern** (§4.1) — **[D-H]**. A concrete public-data anchor and the "use a freely-downloadable corpus for reproducibility" stance Pebble's voice pipeline should adopt (datasets/calibration-anchors decision).

### How each part helps Pebble succeed

- **D-A / voice-message head architecture.** Adopt the *shape* "learned audio front-end → BiGRU/transformer → CTC sequence head" for Pebble's voice modality prototype. Action: stand up a `voice/tone_ctc/` experiment that reproduces the 11.7% recipe on AISHELL-1 to validate the harness, *then* swap the AISHELL tone labels for the actual Pebble per-utterance affect/prosody silver labels. The reproduction is the integration test; only after it lands at ~11–12% TER do you trust the pipeline on child audio.
- **D-B / loss composition.** Use **CTC as the voice head's loss** so the voice modality contributes a properly normalized `−log p(Y|X)` term that does not need frame alignment, and balance it against the text heads' losses with the same scheme chosen in D-B (static λ first; revisit with Kendall/GradNorm only if the voice term dominates). Action: log per-head loss magnitudes early — CTC losses can be large at init and swamp the text MTL heads.
- **D-D / prosody-energy feature.** When (v2) Pebble learns `energy`/prosody from audio, feed a **non-Mel cepstrogram or explicit pitch channel**, and run the paper's own **Baseline-2 ablation** (zero low-time coefficients) on Pebble's data to confirm non-pitch information is also carrying affect — a cheap, decisive ablation. Action: add a `--cepstrum-no-mel` and `--high-time-only` flag to the audio front-end to reproduce the ablation.
- **D-E / training schedule.** Reuse **Adam LR 0.001 + halve-on-dev-plateau + 20 epochs + SortaGrad length curriculum** as the voice head's default schedule; SortaGrad (short utterances first) is especially apt for children's voice messages whose lengths vary wildly. Action: implement length-sorted first epoch in the voice dataloader.
- **D-H / data anchor.** Use AISHELL-1 (openslr.org/33) as the public reproducibility anchor and as a *negative control* corpus (adult, clean, read Mandarin) against which child-message audio metrics are contextualized. Action: pin AISHELL-1 in the voice-pipeline dataset manifest.

### Child mental-health lens

- **Transfer validity is partial and must be stated plainly.** AISHELL-1 is **adult, clean, read, Mandarin** speech in a noise-free booth. Pebble's voice messages are **children**, **spontaneous/affective**, **noisy** (phone mic, background), and (for Pebble's market) likely **non-Mandarin / multilingual**. So the *method* (cepstrogram → CNN → CTC, end-to-end, no alignment) transfers; the *numbers* (11.7% TER) do **not** transfer to child affect on noisy audio and must not be cited as an expected operating point. The paper itself flags the harder direction: continuous, casually-produced speech is *harder* than isolated syllables — children's voice messages are even further along that axis.
- **Why CTC is the right child-data fit.** The dominant practical barrier for child voice data is labels: you cannot ethically or feasibly hand-align affect frames in children's audio. CTC's "supervise from the label *sequence* only" property is precisely the regime that makes silver-labelled child voice tractable, and it avoids the forced-alignment step that would otherwise require a separate (adult-trained, transferring poorly) aligner.
- **Tone ≠ affect, but the prosodic substrate overlaps.** Lexical tone and affective prosody both live in the F0/pitch trajectory. The paper's finding that **non-pitch (low-time cepstral) information also helps** is encouraging for affect, where voice quality (breathiness, tension) — a low-time/vocal-tract phenomenon — carries distress signal. Mitigation/ethic: never let a learned voice-affect head *act*; it informs the Decision Engine only, mirroring the FAIIR "model never decides" invariant.
- **Risk: tone-sandhi-style context dependence.** Just as Tone 3 is ambiguous without a language model, a child's affect at one moment is ambiguous without conversational context. Mitigation: the voice head should output a *signal*, fused turn-level with the text encoder's context, not a standalone verdict.
- **Ethics.** Child voice is biometric and highly identifying; AISHELL's "freely downloadable" model does **not** transfer to child audio. Pebble must treat voice messages under stricter governance (no open release, on-device or controlled-access processing, explicit guardian consent) — the opposite of this paper's reproducibility-by-open-data stance.

### Limitations & open questions for Pebble

- **Contradiction-or-gap vs Pebble's plan (modality mismatch).** Every other paper in Pebble's set is **text**; this is the only **audio** paper. Pebble v1 (per `docs/decisions.md`) trains only text heads (`emotion`, `severity`) on a **4K-token NeoBERT**. A CTC tone/prosody head does **not** plug into NeoBERT — it needs a *separate audio encoder*. So the concrete gap: **Pebble has no audio backbone decision yet** (D-A covers only the text encoder NeoBERT-vs-ModernBERT). This paper surfaces that the voice modality is an *unscoped second model*, not a head on NeoBERT — a planning gap to flag before v2 voice work.
- **Contradiction vs the isolated-syllable literature (Chen et al. 2016, 4.5% TER).** A naive reader might anchor on 4.5% as "tone recognition is solved." This paper shows that number is **only for isolated, carefully-spoken syllables** and that the realistic continuous-speech number is ~11.7%, more than 2× worse. Pebble must internalize the same correction for affect: lab/isolated affect-recognition benchmarks vastly overstate what is achievable on real voice messages.
- **No calibration, no confidence.** Like FAIIR, this paper reports only error rates — no calibration, no per-utterance confidence. Pebble's Decision Engine needs *probabilities* from the voice head; a CTC posterior is not a calibrated affect probability, so a calibration step (v2, D-G) must be added on top.
- **Language coverage.** Method is demonstrated on Mandarin (a tonal language). Pebble's likely user languages may be non-tonal; the *lexical-tone* task itself may be moot, but the *learned-prosody-feature* and *CTC-from-sequence-labels* lessons survive. Open question: which public **affective-prosody** corpus (not tone) is the right substitute anchor — IEMOCAP / MSP-Podcast are adult; a child-speech affect corpus is the missing dataset (D-H).
- **Single-source numeric provenance.** The ISCA HTML did not print the numeric TER table; all per-tone/per-baseline decimals come from the arXiv preprint table only (✔ headline, ≈ decimals). If Pebble cites a specific per-tone number, pull the camera-ready PDF from the ISCA archive (`lugosch18_interspeech.pdf`) to upgrade ≈ → ✔.
