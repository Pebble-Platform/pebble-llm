# Paper 29 — openSMILE: The Munich Versatile and Fast Open-Source Audio Feature Extractor

## 1. Bibliographic info

**Title:** openSMILE — The Munich Versatile and Fast Open-Source Audio Feature Extractor

**Authors:** Florian Eyben, Martin Wöllmer, Björn Schuller (Institute for Human-Machine Communication, Technische Universität München).

**Year / venue:** *MM '10: Proceedings of the 18th ACM International Conference on Multimedia*, October 25–29, 2010, Firenze, Italy, pp. 1459–1462. ACM Press. DOI 10.1145/1873951.1874246.

**Keywords (verbatim):** "audio feature extraction, statistical functionals, signal processing, music, speech, emotion".

**Tool home (2010):** http://opensmile.sourceforge.net/ — now maintained by audEERING at https://github.com/audeering/opensmile.

## 2. One-paragraph summary

openSMILE (Speech & Music Interpretation by Large-space Extraction) is an open-source C++ toolkit that extracts audio **low-level descriptors (LLDs)** — pitch/F0, energy/loudness, MFCC/PLP, formants, voice-quality (jitter, shimmer, HNR), spectral and tonal features — and applies **statistical functionals** (means, moments, percentiles, regression coefficients, peaks, durations) to map variable-length LLD contours to fixed-length feature vectors. It is the de-facto standard front-end for computational paralinguistics and affective computing: it was the official feature extractor for the INTERSPEECH 2009 Emotion Challenge and the 2010 Paralinguistic Challenge, and it is the engine behind the standardized **eGeMAPS (88 parameters)** and **ComParE (6,373 features)** sets used across the speech-emotion literature. For Pebble it is the practical, license-clean way to turn a child's **voice message** into a fixed-length acoustic feature vector before any model stage.

## 3. Why this paper is in the Pebble set (voice-message modality)

Pebble's primary modality is text (NeoBERT encoder), but the thesis includes a **voice-message** path: a child may send an audio clip rather than type. Before any classifier can score that clip turn-level, the raw waveform must be reduced to features. openSMILE is the canonical tool for that reduction — it is what produced the feature sets every speech-emotion paper in this set assumes. This paper is the architectural/engineering reference for the **audio preprocessing stage** that sits upstream of (a) an ASR transcript fed to NeoBERT, or (b) a small acoustic head fed eGeMAPS/ComParE vectors. It is not a modeling paper; it moves D-D and D-H by supplying the concrete feature-extraction substrate and the standardized feature-set anchors.

## Deep research — full-PDF read (2026-06-16)

### Source-access note

The full PDF **was obtained** — the ACM author's version was downloaded directly from the University of Augsburg OPUS repository (`https://opus.bibliothek.uni-augsburg.de/opus4/files/76475/76475.pdf`, 3 pages, the camera-ready MM'10 paper, pp. 1459–1462) and extracted with `pdftotext -layout`. All architecture/feature/benchmark claims below are read from that full text, not from the abstract.

The 2010 paper itself **predates** the standardized feature sets Pebble actually cares about (eGeMAPS, ComParE 2016) — those are defined in later work. Those numbers were validated against secondary sources:

- **Provenance — eGeMAPS / GeMAPS counts.** Search: *"GeMAPS 62 parameters eGeMAPS 88 parameters 18 LLD ComParE 2016 6373 Eyben 2016 IEEE affective computing"*. Resolved: Eyben, Scherer, Schuller et al., "The Geneva Minimalistic Acoustic Parameter Set (GeMAPS) for Voice Research and Affective Computing," *IEEE Trans. Affective Computing* 2016 (preprint `https://sail.usc.edu/publications/files/eyben-preprinttaffc-2015.pdf`; summary `https://jmj3047.github.io/2023/04/21/eGeMAPS/`). Confirmed: **GeMAPS = 62 parameters from 18 LLDs**; **eGeMAPS = 88 parameters** (62 + 26 extended, adding MFCC 1–4, spectral flux, formant bandwidths). ✔ corroborated.
- **Provenance — ComParE 2016 set.** Resolved via audEERING/DeepWiki openSMILE docs (`https://deepwiki.com/audeering/opensmile/4.3-standard-feature-sets`) and challenge baseline papers: **ComParE 2016 = 6,373 features from 65 LLDs** (energy, spectral, MFCC, voicing-related LLDs + functionals). ✔ corroborated (the "6k+ / 6,373" total is consistent across sources; the exact 65-LLD count is from the ComParE baseline papers, ≈ corroborated).
- **In-paper benchmark numbers** (real-time factors, LLD count "56", rtf 0.012 / 0.044 / 0.026) are read directly from §5 of the PDF and tagged below.

### What the paper actually does

**Goal (§1).** Provide one fast, open-source, cross-platform (Unix/Windows/Mac) feature extractor that unifies speech-processing and Music-Information-Retrieval features, supports **on-line incremental** *and* off-line/batch processing, and lets the live system use the **exact same** feature code that produced the published research results. Implemented in C++ with **no third-party dependencies** for core functionality; numeric stability across versions guaranteed by unit tests.

**Architecture (§3, Figure 1).** A central **Data Memory** links three component types:
- **Data Sources** — write external data in (file, sound card).
- **Data Processors** — read from data memory, transform, write back (windowing, FFT, Mel-filterbank, delta coefficients, functionals).
- **Data Sinks** — write out (CSV, ARFF, LibSVM, HTK files, or a LibSVM classifier).

Processing is **ring-buffer / incremental**: levels (e.g. `wave` → `frames` → `pitch` → `func`) each hold a sliding window; a `cFramer` produces frames from wave samples, a `cPitch` extracts pitch, functionals are computed over a window of pitch frames. Buffer sizes are auto-adjusted to reader/writer block sizes. "No feature has to be computed twice" — shared intermediates (e.g. FFT spectra) are reused across extractors. Each component can run in its **own thread** for multi-core parallelism. Everything is wired through a **single configuration file** — no recompilation needed to define new feature sets.

**Available LLDs (§4, Table 1).** Waveform/zero-crossings/extremes; signal energy; loudness (RMS & log); FFT spectrum (intensity, approx. loudness); ACF & cepstrum; **Mel/Bark spectra**; **Cepstral — MFCC, PLP-CC** (computed exactly as in HTK [15], so HTK-compatible); semitone spectra; **Pitch — F0 via ACF and SHS (sub-harmonic summation) methods, plus probability of voicing**; **Voice Quality — HNR, jitter, shimmer**; **LPC — LPC coefficients, reflection coefficients, residual**; **Auditory — line spectral pairs (LSP)**; **Formants — centre frequencies and bandwidths**; spectral (energy in N user bands, roll-off, centroid, entropy, flux, rel. pos. of max/min); **Tonal — CHROMA, CENS, CHROMA-based**. Delta-regression coefficients and a moving-average smoother can be applied to any contour; elementary ops (add, multiply, power) allow custom features.

**Functionals (§4, Table 2).** Applied to LLD contours to produce fixed-length vectors: Extremes (values/positions/ranges); Means (arithmetic, quadratic, geometric); Moments (std-dev, variance, kurtosis, skewness); Percentiles & percentile ranges; **Regression (linear & quadratic approximation coefficients, regression error, centroid)**; Peaks (number, mean distance, mean amplitude); Segments (number via delta-thresholding, mean length); Sample values at relative positions; Times/durations (up/down-level times, rise/fall times); Onsets; **DCT coefficients**; Zero/mean-crossing rate. Functionals can be **stacked hierarchically** ("functionals of functionals," after Schuller et al. ICASSP 2008 [13]), and the functional list is based on the **CEICES** feature-coding standard [2]. Because any processor can be applied to any time series, "researchers [can] generate millions of novel features without adding a single line of C++ code."

**Interoperability (§4).** Loads/saves WEKA ARFF, LibSVM, CSV, HTK parameter files, raw binary (readable in Matlab/Octave). **Live recording** + real-time incremental extraction; **built-in voice activity detection (VAD)** to pre-segment the stream; **on-line mean/variance normalisation** and on-line histogram equalisation; live visualisation via gnuplot.

**Performance (§5).** Benchmarked on a single AMD Phenom 64-bit core at 2.2 GHz, 4 GB RAM, timing CPU time to extract features from 10 minutes of monaural **16 kHz PCM** audio; real-time factor (rtf) = CPU-time / audio-duration (lower = faster):
- Standard PLP + MFCC frame features with log-energy and 1st/2nd-order deltas: **rtf 0.012** (≈83× faster than real time). ✔ in-PDF §5.
- **250 k features** = hierarchical functionals (2 levels) of **56 LLDs** (pitch, MFCC, LSP, etc.): **rtf 0.044** (≈23× real time). ✔ in-PDF §5.
- Prosodic LLDs only (pitch contour + loudness): **rtf 0.026**. ✔ in-PDF §5.

The takeaway: functionals are cheap; most cost is in LLD extraction (FFT, filtering). Even the 250k-feature brute-force set runs ~23× faster than real-time on a single 2010-era core.

**Provenance / adoption (§6).** openSMILE underpins the **openEAR** emotion-recognition toolkit [5]; it was the **official feature extractor for the INTERSPEECH 2009 Emotion Challenge** [11] and the 2010 Paralinguistic Challenge. Funded by EU FP7 grant 211486 (SEMAINE).

**The standardized sets Pebble will actually use (post-2010, validated externally — see Source-access note):**

| Set | Year | Features | LLDs | Contents (high level) | Status |
|---|---|---|---|---|---|
| GeMAPS | 2016 | **62** | 18 | F0, jitter, shimmer, loudness, HNR, formants F1–F3, alpha ratio, Hammarberg index, spectral slope + minimal functionals (mean, CV) | ✔ |
| eGeMAPS | 2016 | **88** | 25 | GeMAPS + MFCC 1–4, spectral flux, formant bandwidths 2–3 (the +26 extension) | ✔ |
| ComParE 2016 | 2016 | **6,373** | 65 | energy + spectral + MFCC + voicing LLDs × large functional bank | ✔ (≈ on 65-LLD) |

### Parts directly useful for Pebble

1. **eGeMAPS (88-param) as the default acoustic feature vector for a voice head.** A compact, expert-curated, fixed-length vector (F0, jitter, shimmer, HNR, loudness, formants, MFCC1–4, spectral slope) — small enough to train a head on Pebble's modest data without overfitting, and the standard every speech-emotion paper benchmarks on. **D-D** (severity/energy regression: the acoustic transfer source and feature substrate), **D-H** (datasets/feature anchors). *Tag: openSMILE config `eGeMAPSv02`.*
2. **The LLD → functionals architecture as Pebble's literal preprocessing recipe.** Frame-level LLD extraction (25 ms window / 10 ms hop conventional) → statistical functionals over the whole utterance → one vector per voice message. This is exactly the shape Pebble's `audio_preprocess` stage should emit. **D-D**, **D-H**. *Tag: a `pebble/audio/features.py` wrapper around `opensmile-python`.*
3. **Built-in VAD + on-line mean/variance normalisation.** openSMILE can pre-segment a noisy child voice message (trim silence/background) and per-utterance-normalise before functionals — directly relevant to turn-level scoring of short, noisy clips. **D-D** (robust regression init), **D-G** (calibration/normalisation policy, largely v2). *Tag: enable VAD + on-line MVN in the extraction config.*
4. **ComParE 6,373 as the "kitchen-sink" upper-bound ablation.** For a one-off experiment to see whether the heavier set buys anything over eGeMAPS on Pebble's data; the GeMAPS paper itself shows minimal sets reach "remarkably comparable performance" at <2% of ComParE's size — so eGeMAPS is the default, ComParE only an ablation. **D-D**, **D-B** (if the acoustic head is folded into MTL, feature dimensionality affects loss balancing). *Tag: a single `compare-vs-egemaps` ablation row.*
5. **rtf ≈ 0.012–0.044 on a single 2010 CPU core.** Feature extraction is effectively free relative to model inference, so the voice path adds negligible latency to turn-level scoring even on commodity hardware. **D-D**, **D-G** (real-time/turn-level feasibility). *Tag: latency budget line in the audio-pipeline design doc.*

### How each part helps Pebble succeed

- **Acoustic head / `severity` & `energy` (D-D).** Pebble's `energy` dimension (heuristic in v1) and `severity` regression are *intrinsically acoustic* concepts (arousal/intensity). eGeMAPS gives a principled feature vector to learn or anchor these on: loudness, F0 range, jitter/shimmer and HNR are the textbook correlates of vocal arousal and distress. Concrete action: when the voice path lands (v2), extract eGeMAPSv02 per message and either (a) train a small MLP/ridge head to predict `energy`/`severity` from the 88-vector, or (b) use the raw loudness/F0-range functionals as a heuristic `energy` proxy that is *better-grounded* than the v1 text heuristic. Pearson r against any acoustic-arousal label is the metric (matches D-D's Pearson convention).
- **Preprocessing pipeline (D-H).** Build `pebble/audio/` as: decode → resample to 16 kHz mono → openSMILE eGeMAPSv02 (LLD + functionals) → 88-float vector → cache. This is a thin wrapper over `opensmile-python` (audEERING's pip package), so no C++ build is needed. The same vector feeds either a standalone acoustic head or is concatenated with NeoBERT's CLS embedding for a late-fusion multimodal head.
- **Two routes for the voice modality, both upstream of NeoBERT.** Route A (recommended v2): openSMILE eGeMAPS → acoustic head fused with NeoBERT text logits. Route B: ASR transcript → NeoBERT only (acoustic info discarded). openSMILE makes Route A cheap; the paper's rtf numbers prove the feature stage won't dominate latency.
- **Standardisation for citation/comparability.** Reporting eGeMAPS/ComParE numbers makes Pebble's acoustic results directly comparable to every INTERSPEECH ComParE-challenge baseline — the only way an acoustic head's quality can be judged against the field.

### Child mental-health lens

- **Transfer validity — the central caveat.** eGeMAPS/ComParE were tuned and validated on **adult** affective speech (challenge corpora, call-centre, acted emotion). Children's voices differ acoustically in load-bearing ways: **higher and more variable F0**, shorter vocal tract (higher formants), less stable phonation (naturally higher jitter/shimmer), and developmental change with age. A jitter/shimmer/HNR threshold learned on adults will mis-fire on a 7-year-old. **The feature extraction transfers; the feature *norms* and any pretrained acoustic model do not.** Mitigation: never reuse adult acoustic *thresholds*; re-fit or re-calibrate any acoustic head on child-voice data, and consider age as a covariate. The search corroborated children-specific acoustic work exists (e.g. sex/age classification of children's voices), confirming child voice is its own regime.
- **Robustness to real-world child audio.** Voice messages from children will be noisy (background, distance from mic, crosstalk, crying, laughing). openSMILE's built-in VAD + on-line MVN help, but functionals computed over a clip containing non-speech (a slammed door, a sibling) will be corrupted. Mitigation: VAD-gate aggressively, drop clips below a minimum voiced-frame count, and treat the acoustic head's output as *advisory* into the Decision Engine — never a sole escalation trigger.
- **No learned safety from audio in v1/v2.** Consistent with Pebble's "no learned safety head in v1" decision: acoustic features must not silently drive a safety flag. Vocal distress cues (low HNR, high jitter, sobbing prosody) are *suggestive*, not diagnostic, especially for children. They can *raise* attention (escalation-only, FAIIR-style) but a clinician/guardian pathway, not the acoustic head, makes the call.
- **Ethics / privacy.** Raw child voice is far more identifying than text (biometric voiceprint). openSMILE's value here is that it lets Pebble reduce audio to a **non-invertible 88-float feature vector on-device/at-ingest** and discard the waveform — a privacy-preserving design (features, not audio, are stored/transmitted). This should be an explicit data-minimisation policy: extract → store vector → delete raw audio. The 2010 paper's "no third-party dependencies, runs anywhere" property makes on-device/edge extraction realistic.
- **Silver-label regime extends to audio.** Pebble has no human-annotated child-voice arousal labels. Any acoustic `energy`/`severity` target would itself be silver (transferred from adult intensity corpora or LLM/text-derived). openSMILE doesn't fix the label problem — it only fixes the feature problem. The label-transfer risk (D-D, D-C) is unchanged.

### Limitations & open questions for Pebble

- **Contradiction / gap vs. Pebble's plan (turn-level vs. utterance functionals).** openSMILE's headline value — functionals — collapses a *whole utterance* to one static vector. Pebble scores **turn-level / mid-conversation**. A single voice message is one turn, so this aligns at the message level; but if Pebble ever wants *within-message temporal dynamics* (distress rising across a 30-second clip), the functional-summary approach throws exactly that away. The paper's own design (variable-length → static) is in tension with fine-grained temporal scoring. Mitigation: use LLD *contours* (not just functionals) if intra-message dynamics matter, or window the clip.
- **Contradiction / gap vs. the rest of the set (modality mismatch).** Every other Pebble paper (01 FAIIR, 12 MentalBERT, 14–16 C-SSRS, 18–19 WASSA) is **text-only**. openSMILE is the only acoustic tool in the set, and **none** of the text papers' labels are aligned to audio. There is no published child-voice corpus with the C-SSRS / GoEmotions / WASSA labels Pebble trains on. So the acoustic head cannot be trained against Pebble's existing silver labels without a transcription+alignment step — a genuine gap, not just an integration detail.
- **eGeMAPS/ComParE are not in this paper.** The 2010 paper provides the *engine* and the LLD/functional vocabulary, but the specific 88-param eGeMAPS and 6,373-feature ComParE configs come from 2016 work (validated externally above). Any Pebble doc citing "openSMILE eGeMAPS" must cite **both** the 2010 toolkit paper *and* Eyben et al. 2016 (GeMAPS) — they are different artifacts.
- **No accuracy numbers.** This is a *tools* paper: it reports rtf benchmarks, not classification accuracy. It cannot supply a performance bar for any Pebble head; it only supplies features. Bars must come from the speech-emotion challenge baselines (ComParE/AVEC), not here.
- **Version drift.** The 2010 SourceForge tool is superseded by audEERING's openSMILE 3.x (GitHub) and the `opensmile-python` package. Pebble should pin the modern package and the `eGeMAPSv02` config, not the 2010 binary. Open question: confirm `opensmile-python` license (it is permissive but verify per redistribution) before bundling it in a child-facing product.
- **Open question — child-voice calibration anchor (D-D / D-H).** What corpus calibrates the acoustic head for children? Adult intensity corpora (WASSA-style, but those are *text*) don't help acoustically. This is an unfilled D-H slot: Pebble likely needs a small child-voice calibration set (even a few hundred consented, age-tagged clips) before the eGeMAPS head can be trusted — without it, the voice path stays heuristic like v1 `energy`.
