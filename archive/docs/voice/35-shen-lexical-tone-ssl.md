# Paper 35 — Encoding of Lexical Tone in Self-Supervised Models of Spoken Language

## 1. Bibliographic info

**Title:** Encoding of lexical tone in self-supervised models of spoken language

**Authors:** Gaofei Shen (Tilburg University), Michaela Watkins (University of Amsterdam), Afra Alishahi (Tilburg University), Arianna Bisazza (University of Groningen), Grzegorz Chrupała (Tilburg University).

**Year / venue:** NAACL 2024 (Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1: Long Papers), pages 4250–4261. arXiv:2403.16865. ACL Anthology: 2024.naacl-long.239.

**Code:** https://github.com/techsword/tone-encoding-in-speech-model

## 2. One-paragraph summary (Pebble lens)

This is an interpretability paper, not a model-building paper. It asks: do self-supervised `wav2vec2`-class spoken language models (SLMs) encode **lexical tone** in their hidden states **without ever being trained on tonal data**? Using linear probes on frozen hidden-state activations, the authors show that even SLMs pre-trained only on **non-tonal** languages (English, French) encode Mandarin and Vietnamese tone far above acoustic (F0, MFCC) and text (BERT) baselines. This is the single most load-bearing paper for the Pebble **voice-message modality** question: *does a pre-trained `wav2vec2` encoder already capture the prosodic/tonal signal we care about, or does Pebble need a dedicated tone head and tonal training data?* The short answer the paper supports: **tone is already there in the representation, recoverable by a linear probe — but it lives in specific middle/upper layers, ASR fine-tuning on a non-tonal language destroys it, and Vietnamese tone is harder to recover than Mandarin tone.**

## Deep research — full-PDF read (2026-06-16)

> Read against the published NAACL 2024 version. The local PDF `pdfs/35-shen-lexical-tone-ssl.pdf`
> carries ACL Anthology page numbers 4250–4261, i.e. it IS the published camera-ready (identical to
> arXiv:2403.16865 v-published). The paper's quantitative results are almost entirely in **figure
> plots** (Figures 2–8) — per-layer accuracy curves rendered as images. `pdftotext` recovers the
> captions and all body/table text but NOT the y-axis values of those curves; numbers I read off the
> figures are tagged ≈ (approximate, figure-read) and their *trends* are what the paper itself asserts
> in prose (✔). Text-stated facts (dataset sizes, splits, model params, baselines) are ✔.

### Source-access note

- **Extraction:** `pdftotext "docs/papers/pdfs/35-shen-lexical-tone-ssl.pdf" -` — full body text, abstract,
  Tables 1–4, and all figure captions recovered cleanly. The Vietnamese IPA and Mandarin Pinyin glyphs
  garble in the dump (encoding artifacts) but the linguistic content is intact.
- **Provenance validated:**
  - Query `Shen Watkins Alishahi Bisazza Chrupala "Encoding of lexical tone in self-supervised models of
    spoken language" NAACL 2024` → https://aclanthology.org/2024.naacl-long.239/ — confirms authors,
    venue, page range 4250–4261. ✔
  - WebFetch of the ACL Anthology page confirms abstract + author list + page numbers; the page does not
    expose the figure numbers (those are in the PDF only). ✔
  - arXiv mirror: https://arxiv.org/abs/2403.16865 (same title/authors). ✔
- **Conflict rule:** local PDF and published version coincide (same ACL page numbers); no preprint delta.
- **Contradiction-source validated:** query for discrete-SSL tone capture →
  https://arxiv.org/abs/2410.19935 ("Do Discrete Self-Supervised Representations of Speech Capture Tone
  Distinctions?", ICASSP 2025) — used below in Limitations as the explicit contradiction/gap. ✔

### What the paper actually does

**Question.** Three sub-questions (§1): (1) Do SLMs trained on tonal *and* non-tonal languages encode
tone? (2) How does supervised ASR fine-tuning change tone encoding? (3) Do SLMs show human-like
perceptual patterns and developmental trajectories?

**Models probed (§4.2, Table 1).** All `wav2vec2-base` (5 conv feature-encoder layers + 12 transformer
layers, 768-dim hidden, 95M params) except the Cantonese model (`wav2vec2-conformer`, 180M params):
- **English** — pre-trained + fine-tuned on LibriSpeech (960h/960h). Non-tonal. ✔
- **French** — pre-trained on MLS French (1,000h). Non-tonal. ✔
- **Mandarin** — pre-trained 1,000h, fine-tuned 178h (AISHELL-2 pre-train / AISHELL-1 fine-tune). Tonal. ✔
- **Vietnamese** — pre-trained on **13,000h** unlabelled YouTube audio, fine-tuned 250h (VLSP). Tonal. ✔
  (Note: ~13× more pre-training data than any other model — a confound the authors flag in §7.)
- **Cantonese** — pre-trained 2,800h (older-adult speech + YouTube), conformer architecture. Tonal. ✔

**Test data (§4.1).**
- **Mandarin: THCHS-30** (Wang & Zhang 2015) — 30h lab-recorded read Mandarin, transcribed to characters
  + Pinyin; character-level forced alignment via Charsiu. Tone labels read directly off Pinyin (one
  morpheme = one character = one tone). Mandarin **4 tones** (T1–T4); the **neutral tone is removed**
  (it appears in unstressed syllables and is unstable). ✔
- **Vietnamese: VIVOS** (Luong & Vu 2016) — 15h lab-recorded read Vietnamese; orthography → IPA + tone
  labels via vPhon; syllable-level forced alignment via Montreal Forced Aligner. Paper adopts Kirby's
  (2011) **8-tone** system for setup; Vietnamese is generally **6 tones**. ✔

**Probing methodology (§4.3) — the core recipe.**
1. Run frozen SLM on test audio; **average-pool the hidden-state output over the duration of each
   syllable** (using forced-alignment timestamps) → one **768-dim vector per syllable/morpheme**. ✔
2. Train a **Ridge linear classifier** (per layer) to predict the tone label from that vector. Model
   selected via **5-fold CV**; regularization swept over {10⁻⁴ … 10²}; report **test accuracy**. ✔
3. **Lexical-confound control (critical):** construct an **exclusive train/test split where phoneme
   strings in the test set never appear in train** — so the probe cannot cheat by memorizing
   phoneme-string→tone associations and must rely on the acoustic tone signal. ✔
4. Splits (Table 2): Mandarin **223,851 train / 45,772 test**; Vietnamese **124,248 train / 29,629 test**.
   80:20 randomized within the exclusive-phoneme constraint. ✔ Consonant probe (Table 3): 92,413 / 15,688. ✔

**Baselines (§4.3).**
- **F0 contour** baseline: 21-frame window around the word center → 21-dim vector (Praat). ✔
- **MFCC** baseline: 40-dim MFCCs, 21-frame window → 840-dim vector (Librosa). ✔
- **Text (BERT)** baseline: Chinese `bert-base-chinese`, per-character 768-dim embedding — measures "how
  much tone is guessable from text alone". ✔

**Results.**

*(1) Tone encoding across languages (§5.1, Figs 2 & 3).*
- **All layers of all SLMs beat F0 and MFCC baselines, which in turn beat the text-BERT baseline** (✔
  prose). i.e. the speech signal carries far more tone information than text, and even a non-tonal-trained
  SLM beats hand-crafted pitch features. Absolute best-layer Mandarin accuracies sit in the **~0.80–0.90+**
  range for tonal models and clearly above baselines for non-tonal models (≈ figure-read, Fig 2).
- **Tonal-language models encode tone better overall, and the encoding increases in higher layers.** ✔
- **Non-tonal (English/French) models still encode substantial tone**, but show a **sharp drop in their
  final layers** — the corresponding drop is much smaller in tonal-language models. ✔ (This is the
  signature autoencoder-like behavior: top layers of a non-tonal model re-specialize away from tone.)
- **Vietnamese (Fig 3) is harder.** The **Cantonese** model transfers to Vietnamese tone *slightly better*
  than English, especially in later layers; but the **Mandarin** model patterns **like the English
  (non-tonal) model** on Vietnamese tone — i.e. Mandarin-tone competence does **not** transfer to
  Vietnamese. ✔ Authors' explanation: Vietnamese tone relies more on **phonation type / voice quality**
  than the **F0-contour/height** cues that dominate Mandarin tone (Brunelle 2009); and Vietnamese has more
  tonal contrasts (6) than Mandarin (4). ✔

*(2) ASR fine-tuning (§5.2, Figs 4 & 5).* Fine-tuning has **opposite effects by language tonality**:
- For **Mandarin** (tonal), ASR fine-tuning **improves** tone classification accuracy. ✔
- For **English** (non-tonal), ASR fine-tuning **harms** tone classification accuracy. ✔
- Same pattern on Vietnamese data (Fig 5: Vietnamese fine-tune helps, English fine-tune hurts). ✔
- Interpretation: ASR fine-tuning pushes the model to specialize for the **written-form output**; tone is
  irrelevant to transcribing a non-tonal language so fine-tuning *removes* it, but tone is essential to
  disambiguate same-segment Mandarin syllables so fine-tuning *amplifies* it. ✔

*(3) Human comparison (§5.3, Figs 6–8).*
- **Learning trajectory (§5.3.1):** SLMs surpass F0/MFCC baselines after ~10,000 pre-training steps, but
  show **no differential trajectory** between tones and consonants — unlike children, who acquire tone
  sensitivity earlier than consonant sensitivity. So **SLMs do NOT follow the human developmental
  trajectory**. ✔ (Custom SLMs pre-trained from scratch: English on LibriSpeech 710h, Mandarin on
  MAGICDATA 712h, fairseq, 85,000 steps, 8×A100, checkpoints every 5,000 steps.) ✔
- **Tone/consonant contrasts (§5.3.2, Figs 7–8):** the tone pairs **T1–T4 and T2–T3** show the largest
  Mandarin-vs-English model accuracy gap, **roughly matching the human confusability pattern** (T2–T3 is
  the most confusable pair for both native English and native Mandarin listeners). So at the **endpoint**,
  SLMs *do* mirror human perceptual confusability, even though their developmental path differs. ✔

**Prior art the paper builds on / contrasts (§3.3).** Yuan et al. (2021) fine-tuned an English `wav2vec2`
for Mandarin tone and hit a **6% tone error rate**; Ryant et al. (2014) hit **15.56% error** from MFCC
alone. ✔ The present paper deliberately does **not** compete on classification accuracy — it probes what
emerges **without** tone supervision.

### Parts directly useful for Pebble

> Pebble's relevant artifact here is the **voice-message ingestion path of the Pebble thesis**: a
> pre-trained `wav2vec2`-class audio encoder turning a child's voice clip into features that feed
> downstream affect/severity heads. The Decision IDs this paper moves: **D-A** (encoder backbone choice —
> here, the *audio* encoder), **D-D** (transfer source / regression init for prosody-derived signals),
> **D-E** (staged fine-tuning / what fine-tuning destroys), **D-F** (domain-adaptive pre-training pass).

1. **Tone (and by extension pitch-contour prosody) is recoverable by a *linear* probe on frozen
   `wav2vec2-base` hidden states, even with zero tonal training data — and beats F0/MFCC baselines at
   every layer.** [**D-A**, **D-F**] This is the existence proof that Pebble's voice path does **not** need
   a tonal pre-training corpus to expose tone/prosody to a downstream head; a frozen off-the-shelf encoder
   + a thin probe already carries it.
   - *Transfer risk:* **Real and large.** The paper's signal is **lexical tone** (phonemic pitch on read,
     lab-clean, single-syllable-aligned speech) — *not* **affective/emotional prosody** in spontaneous
     child speech. Tone being linearly decodable does not prove emotional intonation is. But it is strong
     *directional* evidence: the same F0-contour/voice-quality cues that carry lexical tone are the
     substrate of affective prosody, and they survive into mid/upper `wav2vec2` layers. Treat as
     "prosody is in the representation" evidence, not "emotion is solved".

2. **Tone lives in *specific* layers — middle-to-upper transformer layers, with a final-layer collapse on
   non-tonal-trained models.** [**D-A**, **D-E**] (Figs 2–5: encoding rises through middle layers; the
   *last* layers of English/French models drop sharply.) Concrete config consequence: Pebble must **not**
   default to the encoder's final-layer / pooled output for prosodic features; it should **select an
   intermediate layer** (or weighted layer-sum) as the feature source for any prosody-sensitive head.
   - *Transfer risk:* Layer index is model-specific; the *principle* (don't use the top layer of an
     ASR-fine-tuned non-tonal encoder for prosody) transfers cleanly. If Pebble's audio encoder is an
     English ASR-fine-tuned `wav2vec2`, this paper predicts its **top layer is the worst** place to read
     prosody.

3. **ASR fine-tuning on a non-tonal language *erases* tone encoding (Figs 4–5).** [**D-E**, **D-F**] If
   Pebble grabs a `wav2vec2` checkpoint that was **ASR-fine-tuned on English**, the tone/prosody signal is
   actively *degraded* relative to the **self-supervised-only (pre-trained, not fine-tuned)** checkpoint.
   Action: for Pebble's voice path, prefer the **SSL-pretrained-only** checkpoint (or a multilingual /
   tonal-language one) over an English-ASR-fine-tuned one as the prosody feature extractor.
   - *Transfer risk:* The result is for *lexical tone* under *English* ASR fine-tuning. The mechanism
     (task fine-tuning prunes features irrelevant to the written target) generalizes to "fine-tuning for a
     prosody-irrelevant objective prunes prosody". Pebble should treat any English-ASR checkpoint as
     prosody-lossy by default and validate with its own linear probe (cheap — see #4).

4. **The probing recipe is a directly reusable, near-free diagnostic for Pebble.** [**D-A**, **D-D**]
   Average-pool frozen hidden states over the unit of interest → 768-dim vector → **Ridge linear probe,
   5-fold CV, exclusive-content train/test split** → per-layer accuracy curve. This is *exactly* how
   Pebble should answer "does our chosen audio encoder already carry the affect signal, and in which
   layer?" **before** committing to a heavy fine-tuned tone/prosody head. Costs a CPU-hour, not a GPU run.
   - *Transfer risk:* None on the method itself; the only adaptation is swapping the label (tone → an
     affect proxy: valence/arousal bin, or even a coarse emotion label) and the alignment unit
     (syllable → utterance or fixed window). The **exclusive-content split** discipline is the key import:
     without it Pebble would over-credit the encoder by leaking lexical cues.

5. **Vietnamese tone is harder to recover than Mandarin, and Mandarin competence does NOT transfer to
   Vietnamese (Fig 3).** [**D-D**, **D-H**] For Pebble's **Vietnamese** voice angle specifically: do not
   assume a Mandarin- or English-trained encoder gives you Vietnamese prosody "for free" at the same
   quality as Mandarin. Vietnamese tone leans on **phonation/voice-quality** cues, which are a different
   (and the paper suggests less linearly separable from these encoders') part of the signal.
   - *Transfer risk:* This is the most Pebble-relevant *caution* in the paper. If Pebble's product serves
     Vietnamese-speaking children, the encoder's prosody competence is empirically weaker and more
     cue-dependent than the Mandarin headline suggests. Budget for a Vietnamese-specific probe and
     possibly a Vietnamese (or Cantonese) pre-trained encoder.

### How each part helps Pebble succeed

- **D-A (audio backbone choice).** This paper is the evidence base for **not** training a tone/prosody
  encoder from scratch and **not** requiring tonal pre-training data: a frozen `wav2vec2-base` already
  linearly exposes tone above F0/MFCC. Concrete action: for the Pebble voice-message encoder, start from
  an **SSL-pretrained `wav2vec2`-class** checkpoint and treat prosody as *probe-able*, not *trainable from
  zero*. Pair with paper 33/34-class HuBERT findings if available in the set.
- **D-E (staged fine-tuning / what unfreezing destroys).** The Figs 4–5 result is a direct warning for
  Pebble's staged fine-tuning of the audio encoder: **fine-tuning for the wrong objective deletes the
  prosody you wanted.** If Pebble fine-tunes the audio encoder end-to-end on, say, an ASR or transcription
  auxiliary task, it risks pruning the affective-prosody signal. Mitigation: **freeze the prosody-bearing
  intermediate layers**, or use discriminative LR / gradual unfreeze that protects mid-layers — the
  encoder-side analogue of the text-side D-E policy.
- **D-F (domain-adaptive pre-training pass).** The non-tonal-trained models still carry tone, but a
  **continued SSL pass on in-domain (child-voice / tonal) audio** is the lever to *raise* the mid-layer
  tone/prosody encoding without needing labels — the audio analogue of the text-side domain-adaptive MLM
  pass. The paper shows tonal-pretrain > non-tonal-pretrain on tone encoding, so a domain-adaptive
  SSL pass on child speech is a credible, label-free win for the prosody heads.
- **D-D (transfer source for a regression/severity-adjacent prosody signal).** If Pebble ever derives a
  prosody-based arousal/energy regressor from audio, this paper says the **transfer source matters**
  (tonal vs non-tonal pre-training) and the **metric should be per-layer** (best-layer accuracy, not
  pooled-output accuracy). Use the probe to pick the source checkpoint + layer empirically.

### Child mental-health lens

- **Modality fit, with a caveat.** Pebble is child-facing and turn-level; this paper's data is **adult,
  read, lab-clean** speech (THCHS-30, VIVOS). Children's voices differ in F0 range, articulation,
  hyperarticulation of tone (the paper itself cites Rhee et al. 2021 that *children hyperarticulate tonal
  differences*), and spontaneity. So the encoder's *adult-read* tone competence is an **upper bound** for
  what Pebble gets on spontaneous child voice messages — expect degradation from register and channel
  (phone mic, noise, emotion-driven prosody distortion).
- **Why this matters for safety.** Pebble's voice path is meant to surface affect/distress earlier and
  more obliquely than text. Affective prosody (flat/monotone affect in depression, agitation/pitch
  instability in anxiety, breathy/creaky voice quality) shares the **F0-contour + voice-quality** substrate
  this paper shows `wav2vec2` encodes. The paper's voice-quality finding (creaky voice shifts tonal
  perception, §3.2) is suggestive that the *same* encoder layers carry clinically-relevant prosodic affect
  cues — but **no affect label is tested here**, so this is a hypothesis Pebble must validate, not import.
- **Vietnamese-child risk specifically.** If Pebble serves Vietnamese children, the paper's Fig-3 result
  (Vietnamese tone harder, phonation-dependent, no Mandarin→Vietnamese transfer) means the voice path is
  **empirically weaker** for Vietnamese than the Mandarin headline implies. For a safety-adjacent product,
  weaker prosody recovery in one language is an equity/transfer risk that must be measured per-language,
  not assumed uniform.
- **Ethics.** All data here is public read-speech ASR corpora (no minors, no clinical content); the paper
  is purely interpretability. The transfer to a child-voice product introduces every minors-data concern
  (consent, on-device processing, retention) that the paper does not face — Pebble cannot inherit its
  light governance footprint when moving to live child voice capture.

### Limitations & open questions for Pebble

- **Contradiction/gap vs the discrete-SSL line of work.** This paper probes **continuous** hidden states
  and finds tone richly encoded. But Shen et al.'s sibling/follow-on question — answered by
  *"Do Discrete Self-Supervised Representations of Speech Capture Tone Distinctions?"* (arXiv:2410.19935,
  ICASSP 2025; validated ✔) — finds that **discretizing** SSL features (k-means / HuBERT-unit "textless
  NLP" pipelines) causes a **substantial loss of tone information, even for language-specialised SSL
  models**, and that discretization must be **task-aware** for tone-dependent tasks. **Direct consequence
  for Pebble:** if Pebble's voice path ever routes audio through a **discrete-unit / tokenized** speech
  representation (HuBERT codes, speech-token LLM front-ends), it will **lose** the very prosody/tone signal
  this paper proves is present in the continuous features. Pebble should keep the prosody/affect head on
  **continuous** hidden states, not on discretized speech tokens. This is the single most important
  cross-paper caveat for the voice modality.
- **No affective/emotional prosody is tested — only lexical tone.** The whole transfer to Pebble rests on
  the (reasonable but unproven) assumption that affect prosody shares the encoded substrate. The paper
  cannot tell Pebble whether `wav2vec2` linearly encodes *emotional* arousal/valence. This is the #1 open
  experiment: re-run the §4.3 probe with an affect label on child/affective speech.
- **Read, lab-clean, adult, monolingual test data.** Authors explicitly flag (§7) that THCHS-30/VIVOS
  "do not fully reflect the linguistic diversity of different accents and dialects" and are read speech.
  Pebble's spontaneous, noisy, child voice messages are out-of-distribution on every axis.
- **Vietnamese-model confound.** The Vietnamese encoder was pre-trained on **13,000h** vs ~1,000h for
  others (§7) — so any Vietnamese-model advantage may be *data scale*, not *tonality*. Pebble cannot read
  off a clean "tonal pre-training helps Vietnamese" conclusion; the cleanest lever it can take is the
  **continued-SSL domain-adaptive pass** (D-F), where scale is controllable.
- **Probe ≠ usable feature.** Linear-probe decodability shows the information *exists*; it does not show a
  downstream head will *use* it well, nor that it survives end-to-end fine-tuning (Figs 4–5 show fine-tuning
  can *destroy* it). Pebble must verify post-fine-tuning, not just on the frozen encoder.
- **No exact numbers extractable from the figures.** The per-layer accuracy values live in image plots;
  this dossier reports trends (✔, paper's own prose) and approximate ranges (≈, figure-read). If Pebble
  needs exact per-layer numbers for a citation, pull them from the authors' released code/outputs at the
  GitHub repo rather than the PDF.
