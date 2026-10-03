# Paper vn-06 — Encoding of Lexical Tone in Self-Supervised Models of Spoken Language

- **Authors:** Gaofei Shen et al. (verify against anthology page)
- **Venue / year:** NAACL 2024 (long)
- **Links:** anthology https://aclanthology.org/2024.naacl-long.239/ · PDF `pdfs/06-shen-lexical-tone-ssl.pdf`
- **Group:** vietnamese-ser / tonal prior art (phonetic premise)

**Summary:** Probes whether frozen wav2vec2-class SSL encoders linearly encode
lexical tone, including Vietnamese (VIVOS) vs Mandarin (THCHS-30). Finds
Vietnamese tone is harder to decode and relies more on phonation/voice-quality
cues than the F0-contour/height cues that dominate Mandarin tone; no
Mandarin→Vietnamese transfer.

**Relevance to ViEmoSpeech:** The single most load-bearing prior-art paper for
the phonetic premise of the tone×emotion hook (VN tone is phonation-heavy — the
same channel emotion uses). Previously known to the repo only via the archived
entry `archive/docs/voice/35-shen-lexical-tone-ssl.md`; PDF now local.

> Stub created 2026-07-10 (task `docs/tasks/paper-deep-analysis.md`); deep-read pending.

## Deep research — full-PDF read (2026-07-10)

> Read the full NAACL 2024 long paper end-to-end from the local PDF
> (`pdfs/06-shen-lexical-tone-ssl.pdf`) via `pdftotext`. This paper is the **load-bearing
> phonetic premise** of the ViEmoSpeech method paper (VN tone is phonation-heavy). Because the
> paper reports every probing accuracy as a **line-plot figure** (Figs 2–8) and gives **no numeric
> accuracy table**, this section is scrupulous about which numbers exist as text vs. only as
> plots, and tags each accordingly. Cross-references point back to the stub above.

### Source-access note

- **How read:** `pdftotext "docs/papers/vietnamese-ser/pdfs/06-shen-lexical-tone-ssl.pdf" -`
  (46.6 KB of text, full method + all figure captions + both split tables + references).
- **Web-validated:**
  - Title / authors / venue / pages — WebFetch of the ACL Anthology page. Query: anthology
    2024.naacl-long.239. Resolved: `https://aclanthology.org/2024.naacl-long.239/`. Confirms
    "Encoding of lexical tone in self-supervised models of spoken language", Shen · Watkins ·
    Alishahi · Bisazza · Chrupała, **NAACL 2024, pp. 4250–4261**. ✔
  - The two load-bearing qualitative claims (Mandarin→Vietnamese non-transfer; Vietnamese relies
    on **phonation type + voice quality** vs Mandarin **F0 contour / height**) — WebFetch of the
    arXiv HTML mirror `https://arxiv.org/html/2403.16865v1` (query: Shen encoding lexical tone
    Vietnamese phonation voice quality probing accuracy). The exact sentence *"Vietnamese uses
    different acoustic cues such as phonation type and voice quality in tonal perception than f0
    contours or height in Mandarin (Brunelle, 2009)"* is confirmed verbatim. ✔
  - **Confirmed absence of numeric accuracies:** both the Anthology metadata and the arXiv HTML
    confirm the paper contains **no specific numeric probing-accuracy percentages** in text or
    captions — all results are line plots. So every accuracy claim below is tagged ≈ (read off a
    figure, approximate) or ✖ (not numerically reported); only the split sizes, dataset hours,
    param counts and *cited* baseline error rates are hard numbers (✔). No preprint/venue
    conflict found (arXiv v1 and NAACL camera-ready agree on all checked facts).

### What the paper actually does

**Goal.** Probe whether *frozen* wav2vec2-class self-supervised speech models (SLMs) linearly
encode **lexical tone** in their hidden states, using Mandarin (primary) and Vietnamese
(generalization check) as case studies, and whether ASR fine-tuning and pre-training-language
tonality change that encoding. It is an **interpretability/probing** paper, not a SER paper and
not a tone-classifier competition.

**Models (§4.2).** wav2vec2-**base** (95M params: 5 conv feature-encoder layers + 12 transformer
layers, 768-dim hidden states) pre-trained/fine-tuned per language: English (LibriSpeech), French
(MLS), Mandarin (AISHELL-2 pretrain / AISHELL-1 ASR-FT), Vietnamese (13k h YouTube pretrain / VLSP
ASR-FT — note the VN model saw **13,000 h**, ~13× the others, flagged as a confound in §7), and a
Cantonese **wav2vec2-conformer** (180M, larger + different architecture — also a confound). ✔ for
the param/hours figures (Table 1 text).

**Test data (§4.1).** Mandarin **THCHS-30** (30 h lab **read** speech; Charsiu char-level forced
alignment; Pinyin→tone labels, neutral tone removed). Vietnamese **VIVOS** (15 h lab **read**
speech; transcription→IPA+tone via **vPhon** (Kirby 2008); **Montreal Forced Aligner** syllable
alignment; Kirby-2011 **8-tone** system). ✔ (dataset hours are text).

**Probe (§4.3).** Average-pool each SLM layer's hidden states over a syllable's forced-alignment
window → 768-dim vector → **Ridge linear classifier** predicting tone, 5-fold CV, regularization
swept 10⁻⁴…10². **Critical confound control:** the train/test split is constructed so **phoneme
strings in test do not appear in train** — this blocks the probe from cheating via lexical
(phoneme-string↔tone) associations rather than genuine tonal acoustics. Split sizes (**Table 2**,
✔ text): Mandarin **223,851 train / 45,772 test**; Vietnamese **124,248 train / 29,629 test**.
Consonant probe (**Table 3**, ✔): **92,413 / 15,688**. Baselines: **F0 contour** (21-dim, Praat),
**MFCC** (40-d × 21-frame = 840-dim, Librosa), and a **Chinese-BERT text** baseline (768-dim,
per-character) as a "what can be guessed from text alone" floor.

**Results.**
- **§5.1 Mandarin tone (Fig 2):** *all* SLM layers beat F0 and MFCC baselines, which in turn beat
  the BERT text baseline; tonal-language models score higher and **rise in the upper layers**,
  whereas non-tonal-language models show a **sharp accuracy drop in their final layers**. Even
  English/French (non-tonal) SLMs encode Mandarin tone substantially. (accuracies ≈ figure-only.)
- **§5.1 Vietnamese tone (Fig 3):** the **Cantonese** model beats the English model (esp. later
  layers); the **Mandarin** model **patterns like the English model** — i.e., a strong Mandarin
  tone encoder does **not** transfer to Vietnamese tone, while Cantonese (which has phonation
  register) partially does. Authors' explanation: *"Vietnamese uses different acoustic cues such
  as phonation type and voice quality in tonal perception than f0 contours or height in
  Mandarin."* ✔ (quote) — but the accuracy gap itself is ≈ figure-only.
- **§5.2 ASR fine-tuning (Figs 4–5):** fine-tuning for ASR **enhances** tone encoding for
  tonal-language models (Mandarin, Vietnamese) but **degrades** it for non-tonal (English) models —
  because tone is needed to output the correct character/orthography in a tonal language, and is
  discarded as nuisance in a non-tonal one. (direction ✔; magnitudes ≈ figure-only.)
- **§5.3 Human-parity:** SLMs reproduce the human-perception difficulty ordering of Mandarin tone
  pairs (T2–T3 and T1–T4 most confusable) and English-mapped consonant groups, but do **not**
  follow the child developmental trajectory (tone-before-consonant). Peripheral to ViEmoSpeech.
- **Cited baselines (not this paper's own results, ✔ as citations):** Ryant et al. 2014a — an
  MFCC-only Mandarin tone classifier reaches **15.56% error** on T1–4 *without explicit F0*
  (evidence that MFCCs smuggle in phoneme-string cues); Yuan et al. 2021 — a *fine-tuned* wav2vec2
  reaches **6% tone error rate**. These frame why the phoneme-disjoint split matters.

### Parts directly useful for ViEmoSpeech (tagged with Decision IDs)

1. **The phonation/voice-quality premise for the audio branch — the whole point (V-B).** §2 +
   §5.1(Fig 3) + the Brunelle-2009 citation establish that Vietnamese tone is carried by
   **phonation type (creaky/breathy), voice quality, amplitude and spectral tilt**, not primarily
   the F0 contour/height that defines Mandarin tone. This is the empirical warrant for adding
   explicit **voice-quality descriptors** (jitter, shimmer, HNR, H1–H2, CPP, spectral tilt) to
   ViEmoSpeech's audio branch alongside the SSL encoder. **[V-B]**
2. **The layer-wise linear-probe protocol as the instrument to *quantify* tone×emotion channel
   competition (V-D, V-G).** §4.3's recipe — per-syllable average-pooled 768-dim hidden state →
   Ridge probe → 5-fold CV → F0/MFCC/text baselines → **phoneme-disjoint train/test split** — is
   directly reusable to turn ViEmoSpeech's "channel competition" hook from prose into a number:
   run the *same* probe on ViEmoSpeech's audio encoder for **(a)** syllable-tone label and **(b)**
   arousal/emotion, and measure whether the layers and feature-subspaces that best decode tone are
   the same ones that best decode arousal. Overlap = quantified competition. **[V-D, V-G]**
3. **Encoder / layer-selection guidance for V-B (Fig 2 upper-layer rise + final-layer collapse;
   Figs 4–5 ASR-FT direction).** Two actionable facts: (i) suprasegmental info peaks in **middle/
   upper transformer layers** and **collapses in the final layer of non-tonal-language encoders** —
   so a frozen English WavLM's *last* layer is the worst place to read tone-carried affect from;
   (ii) **ASR fine-tuning on a tonal language enhances** tone encoding. ViEmoSpeech's ASR is
   **PhoWhisper** (Vietnamese-fine-tuned) — so its encoder is on the "enhances" side, and a
   Vietnamese-pretrained wav2vec2 is a defensible V-B backbone over generic English WavLM *if* tone
   info is load-bearing. **[V-B]**
4. **The phoneme-disjoint split as an anti-confound control for V-G.** The Ryant-2014a 15.56%
   MFCC-only result is a warning: a "tone" (or "tone×emotion") probe that shares phoneme strings
   between train and test will report inflated numbers that are really lexical memorization. Any
   ViEmoSpeech probing/eval that claims to isolate the *acoustic* tone channel must replicate the
   phoneme/word-disjoint split. **[V-G, V-D]**

### How each part helps ViEmoSpeech succeed

- **V-B (audio features): add a handcrafted voice-quality vector, don't trust F0 alone.** Concrete
  action: in the audio branch, concatenate a low-dimensional **eGeMAPS-style phonation set**
  (jitter, shimmer, HNR, H1–H2, CPP, spectral tilt, per-syllable) to the SSL embedding before
  fusion, and run a V-B ablation *with vs. without* it. Shen's result predicts this helps *more*
  for Vietnamese than it would for a non-tonal language, precisely because VN tone and emotion both
  live in phonation — the fused representation has to separate two phonation-borne signals. This is
  the config that operationalizes the method paper's "phonation-heavy" hook.
- **V-B (backbone): pick a Vietnamese/PhoWhisper encoder and read from mid layers.** Action: in the
  V-B backbone bake-off (WavLM vs emotion2vec vs Whisper/PhoWhisper encoder), include a **layer
  sweep** and expect the best affect-from-phonation layer to be mid-stack, not final — mirroring
  Fig 2. If a frozen English WavLM is used, weight or pool *mid* layers rather than defaulting to
  the last hidden state.
- **V-D (quantify the claim): a two-target probe over ViEmoSpeech's own encoder.** Action — a new
  experiment `probe/tone_vs_arousal/`: on gold clips with syllable-tone annotations + MFA
  alignment (ViEmoSpeech already has both), fit two Ridge probes per layer — one for tone label,
  one for arousal bin — under a **word/phoneme-disjoint split**, and report (i) per-layer accuracy
  curves for each, (ii) their layer-of-peak, and (iii) a subspace-overlap / mutual-interference
  metric (e.g., accuracy drop on tone after projecting out the arousal-discriminative directions).
  That single figure *is* the empirical backbone of the method paper's novelty claim, produced with
  Shen's exact, citable methodology.
- **V-G (protocol hygiene): reuse the F0/MFCC/text baseline ladder + phoneme-disjoint split.**
  Action: any probing figure in the ViEmoSpeech paper carries the same three baselines (F0, MFCC,
  ASR-text) so a reviewer can see the acoustic channel beats text — the argument that in Vietnamese
  the audio branch carries information the ASR-text branch structurally cannot (tone diacritics
  dropped under high-arousal ASR errors, mày→máy). Shen's ladder is the template.

### Child / found-speech transfer lens (ViEmoSpeech regime)

- **Register mismatch — read speech vs found TV drama.** VIVOS and THCHS-30 are **clean,
  lab-recorded read speech**; ViEmoSpeech is **found TV-drama** with acted-emotional prosody,
  music/SFX residue (post-Demucs), overlapping turns, and reverberation. F0 tracking and phonation
  descriptors are *noisier* on this material — which **strengthens** the case for SSL embeddings
  (robust) over raw Praat F0, but **weakens** the reliability of handcrafted jitter/HNR features on
  low-SNR clips. Mitigation: compute voice-quality features only on clips passing a SNR/voicing
  gate; report their coverage; keep them as an *auxiliary* concatenation, never the sole tone cue.
- **Dialect coverage gap — Shen tested Northern only.** VIVOS + vPhon + Kirby-2011 8-tone system
  are **Hanoi/Northern** Vietnamese. ViEmoSpeech spans **Bắc/Trung/Nam**. Southern and Central
  Vietnamese tone systems are *more* register/phonation-based and merge several Northern tone
  contrasts — so Shen's phonation premise plausibly **strengthens** for Southern speech, but the
  paper provides **no** direct evidence for non-Northern dialects. The tone×emotion probe must
  stratify by dialect, and the tone-label scheme (V-D) must be dialect-aware rather than assuming
  the Hanoi 8-tone inventory everywhere.
- **Ethics / release.** This lens is benign for the CC-BY feature-only release: Shen's probe emits
  no clip audio, only per-syllable pooled embeddings and Ridge weights — fully compatible with
  ViEmoSpeech's "features+timestamps+labels+speaker-ids only" constraint. No child-privacy issue
  (adult read-speech corpora), so nothing new to mitigate beyond the standard media-legality rule.
- **Task-validity caveat.** The paper is about **lexical tone**, not emotion. Its transfer value to
  ViEmoSpeech is *mechanistic* (tone and emotion share the phonation channel; therefore the two
  compete), not a direct SER result. Every use above is framed as "the phonetic substrate," and the
  competition itself remains ViEmoSpeech's to measure — Shen only supplies the premise and the tool.

### Limitations & open questions for ViEmoSpeech

- **Contradiction/gap #1 — the "phonation-heavy" premise is *inferred*, not measured.** Shen never
  runs a phonation-feature probe: it infers Vietnamese phonation-reliance from (a) the Mandarin→VN
  **non-transfer** of an F0-centric encoder and (b) a **citation to Brunelle (2009)**. There is *no*
  experiment in this paper that decodes VN tone from H1–H2/HNR/creak features and shows they beat
  F0. **This is exactly the measurement ViEmoSpeech should own** — probing VN tone (and emotion)
  from explicit phonation vs F0 features would be the *first direct* quantification, converting the
  method paper's borrowed premise into an original contribution rather than a re-citation.
- **Contradiction/gap #2 — vs the "semantics dominate" line (vn-12, Incongruent-Speech SLM).**
  vn-12 argues SLMs' *emotion* judgments are driven mainly by semantics/text; Shen shows the
  *acoustic* channel encodes VN tone far above a text-BERT baseline and via **phonation** cues text
  cannot represent. For Vietnamese these are not simply opposed — they define the tension
  ViEmoSpeech quantifies: if emotion leans semantic but VN tone (and its emotional phonation) leans
  acoustic, then the audio and text branches carry **partially non-substitutable** signals, and ASR
  tone-diacritic loss under high arousal *removes exactly the shared phonation evidence*. The fusion
  design (V-A) and the tone-representation design (V-D) both hinge on this being real, so the probe
  in "How each part helps" is not optional decoration — it adjudicates a live disagreement.
- **Gap #3 — confound stack Shen itself flags (§7).** The Vietnamese encoder saw **13k h** (≈13×
  the others) and the Cantonese model differs in **architecture (conformer, 180M)** *and* data size —
  so the "Cantonese generalizes to VN, Mandarin doesn't" result is entangled with data/architecture,
  not purely tonality. ViEmoSpeech must not over-cite the Cantonese-transfer finding as clean
  evidence; the *safe* citations are (i) VN tone ≠ F0-only and (ii) ASR-FT on a tonal language
  enhances tone encoding.
- **No numeric bars.** Because all accuracies are figure-only, ViEmoSpeech cannot cite a specific
  "VN tone probing accuracy = X%" from this paper. Any such number in the method paper must come
  from ViEmoSpeech's *own* re-run of the probe on its own encoder — which is the intended use anyway.
- **Open question vs ViEmoSpeech's own plan.** ViEmoSpeech plans to **annotate and encode
  syllable-tone explicitly**. Shen shows a frozen SSL encoder *already* captures tone in its mid
  layers without labels — so an explicit tone-label head may be **redundant** with the audio encoder,
  or it may act as a **useful auxiliary/regularizer** that forces the phonation subspace to stay
  separable from the emotion subspace. Which one holds is untested here; a V-D ablation (tone head
  on vs off, measuring emotion-branch accuracy and the tone/arousal subspace overlap) would settle
  whether the annotation effort pays for itself.
