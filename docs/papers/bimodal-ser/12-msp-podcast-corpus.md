# Paper 12 — The MSP-Podcast Corpus

- **Authors:** Carlos Busso, Reza Lotfian, Kusha Sridhar, et al.
- **Venue / year:** arXiv 2025 (submitted IEEE Trans. Affective Computing)
- **Links:** abs https://arxiv.org/abs/2509.09791 · PDF `pdfs/12-msp-podcast-corpus.pdf`
- **Group:** survey / benchmark (dataset paper)

**Summary:** Dataset paper canonical cho MSP-Podcast: 400+ giờ, annotation categorical + continuous (valence/arousal/dominance).

**Relevance to Pebble:** Tiền lệ published gần nhất về thiết kế nhãn categorical + continuous (dual-head) — citation bắt buộc nếu eval trên MSP-Podcast.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled profile (at analysis time).** Pebble's *primary* stream is ordinal
suicide-risk **text** classification testing whether LLM/weak labels honestly
augment a scarce clinical gold set under strict **gold-holdout**, subject-level
splits, ordinal-aware metrics (QWK/MAE/macro-F1), and clinical-data ethics
(`docs/intent/constraints.md`). Its *adjacent active* **voice** stream
(`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`) attaches
**heterogeneous MTL heads on a frozen SSL backbone (WavLM-Large / emotion2vec)**:
emotion CE + **affect (valence/arousal) CCC** + crisis BCE under a **hard recall
floor**, balanced by Kendall uncertainty weighting. The voice roadmap explicitly
names **MSP-Podcast (A/V/D) as the next real-label target for the affect head**
(currently on Russell-circumplex proxy labels).

### Analysis — MSP-Podcast Corpus (Busso et al.)
- **Overlap:** D1=2, D2=0, D3=2, D4=0, D5=1, D6=0, D7=2 →
  (3·2 + 2·0 + 1·2 + 2·0 + 2·1 + 2·0 + 1·2) / 26 = 12/26 = **46% (adjacent)**
- **Closest on:** D1 (the SER baseline is a genuinely heterogeneous head set —
  categorical **focal** + continuous **CCC**, staged then jointly trained) and D7
  (baselines are **WavLM / Wav2vec2 / HuBERT ~310M SSL**, the exact backbone
  family Pebble's voice stream freezes); D3 close behind (this IS the named affect
  corpus for the V/A/D head).
- **Best point (Baseline to beat):** Section VI gives a published affect recipe +
  numbers — adapt an SSL encoder with **CCC loss to predict valence/arousal/
  dominance, then jointly train with the categorical focal head** (attribute stage
  uses a frozen encoder + per-attribute regression head), with WavLM CCC on Test1
  of **V≈0.72 / A≈0.72 / D≈0.65** (Table VII).
  - **How to apply to Pebble:** when the voice affect head swaps proxy V/A for real
    MSP-Podcast A/V/D (the roadmap's next task), adopt this staged CCC→joint recipe
    on the frozen WavLM trunk and report the affect head's CCC against these WavLM
    per-test-set numbers as the baseline to beat — turning the proxy-label mechanic
    into a real, citable affect result.
- **Caveats:** (1) No mental-health/crisis or clinical labels (D2=D6=0) — this
  corpus only fuels the **affect** head; the crisis/recall-floor head still needs a
  clinical source (e.g. DAIC). (2) Their baselines **fine-tune** the ~310M SSL,
  whereas Pebble's plan uses a **frozen** backbone + probe — the CCC numbers are a
  reference ceiling, not a like-for-like target unless the frozen-probe protocol is
  matched. (3) Access is via signed data-transfer agreement (329 groups), not a
  free download — hand to `find-dataset` to confirm the gate before relying on it.
  (4) Deep-read of pp.1–2 + 13–15 (baselines, partitions, discussion); middle
  sections (III–V annotation protocol) skimmed, so annotation-method scoring (D4)
  is from the abstract + protocol summary, not a full read.

## Deep research — full-PDF read (2026-07-10)

> Profile note: read against the **current ViEmoSpeech profile + Decision Register (V-A…V-H)**
> in `docs/tasks/paper-deep-analysis.md`, NOT the archived voice-MTL "Analysis (overlap with
> Pebble)" block above (which was scored pre-pivot and is retained only as history). All
> Decision IDs below are V-x.

### Source-access note

Full text read via `pdftotext "docs/papers/bimodal-ser/pdfs/12-msp-podcast-corpus.pdf" -`
(local PDF = arXiv:2509.09791v1, eess.AS, 11 Sep 2025 — this is the "final release / v2.0"
dataset paper, submitted to *IEEE Trans. Affective Computing*; no separate published venue
version exists yet, so the arXiv/lab PDF is authoritative). All load-bearing numbers below were
cross-checked against the arXiv HTML rendering.
- Query `MSP-Podcast corpus 409 hours 3641 speakers 267905 speaking turns Busso 2025` →
  https://arxiv.org/abs/2509.09791 and the lab-canonical copy https://www.lab-msp.com/MSP/publications/Busso_2025.pdf
  (both = same paper). ✔ 409 h / 3,641 speakers / 267,905 turns confirmed.
- Query `MSP-Podcast WavLM baseline CCC valence 0.722 arousal Test1 categorical F1 macro focal loss`
  + WebFetch of https://arxiv.org/html/2509.09791v1 → returned the full Table VII / Table II /
  Table III / partition numbers verbatim (all ✔ corroborated below).
- One **internal inconsistency** flagged, not resolvable externally: prose (§IV-D and the arXiv
  abstract) says "2,043 female, 1,598 male", but **Table IV** lists Female **1,598** / Male
  **2,043**. Non-load-bearing here; noted so nobody quotes the gender split without checking the table.

### What the paper actually does

Describes the 10-year, final (v2.0) release of **MSP-Podcast**: a naturalistic English
speech-emotion corpus mined from Creative-Commons podcasts.

- **Scale (✔, §I, §V, Table VI):** 409 h; **267,905 speaking turns**; **3,641 speakers**
  (1,598 F / 2,043 M per Table IV); **6,007 unique podcasts**; **1,446,270 emotion annotations**
  from 13,280 workers; **≥5 raters per turn** (Fig. 3). Human transcriptions for the *entire*
  corpus (REV.com): 4.3 M tokens, 50,677 unique words, mean **15.89 words/turn** (§IV-E). MFA
  phonetic alignment released as TextGrids (§IV-F).
- **Licensing (✔, Table II):** every podcast is CC/PD so the *audio itself* is redistributable —
  **CC-BY 90.86%** (5,458 podcasts / 242,699 turns), CC-BY-SA 5.59%, Public Domain 2.88%,
  Unknown 0.67% (40 podcasts whose license screenshot was lost after the source was taken down).
  Practice: save a **screenshot of the license page** at collection time as provenance.
- **Retrieval/segmentation pipeline (§III, Fig. 1):** source → convert to 16 kHz/16-bit/mono PCM
  (Librosa) → diarize+ASR (Azure Video Indexer 61.0%, Whisper-large 13.3%, Whisper-large-v2
  21.1%; first 4.64% manual) → split into **speaking turns of 2.75–11 s** (long turns re-segmented
  by word-alignment at pauses ≥0.3 s; turns with <5 words dropped) → **music detector** (drop if
  >50% music) → **WADA-SNR** (drop if SNR <15 dB) → **pyannote.audio** single-speaker filter →
  LSTM gender predictor (for gender balancing) → **emotion-retrieval ranking over 48+ criteria**
  from many SER/sentiment models (to over-sample emotional, minority-class content) → trained-human
  final listen → perceptual evaluation. Net effect of retrieval: only **28% neutral** (vs the far
  higher neutral rate of untargeted conversation).
- **Annotation protocol (§III-D, §IV):** primary = **one** of 8 categories
  (anger, sadness, happiness, surprise, fear, disgust, contempt, neutral) + free-text "Other";
  secondary = multi-select over 16 emotions; **valence/arousal/dominance on a 1–7 SAM Likert
  scale**, consensus attribute = mean across raters; primary consensus by **plurality rule**
  (with an explicit "no-agreement" class). Crowdsourcing was **abandoned mid-project** (bots,
  random submissions) in favour of **14–20 screened UT-Dallas student workers** with weekly
  relative-ranking feedback and mandatory targeted re-training on the single attribute they were
  weakest on; 430 bad crowd-workers + 44,968 annotations were removed and re-annotated. Student
  workers ultimately provided **65.82%** of annotations.
- **Agreement (✔, Table III):** primary κ **0.411** (All); valence α 0.508 / arousal 0.441 /
  dominance 0.386 (All). Test3 (balanced, careful) is highest (primary 0.510, arousal 0.610);
  **Test2 is lowest** (primary 0.294, valence 0.228) because it is neutral-heavy and neutral is
  intrinsically ambiguous.
- **Partitions (✔, §V-A, Tables IV/VI):** **speaker-independent** Train (2,220 spk / 169,190 turns)
  / Dev (704 spk / 34,399) / **Test1** (465 spk / 46,294; same class distribution as whole corpus)
  / **Test2** (112 spk / 14,822; collected **without** the emotion-retrieval step → ~45.8% neutral;
  a deliberate *selection-bias control*) / **Test3** (428 spk / **3,200 turns, balanced 400×8
  classes**; labels/transcripts/speaker-ids **withheld** — a blind challenge test served via a
  leaderboard, used for Odyssey-2024 & Interspeech-2025). Caveat (Table IV caption, §V): the
  **test sets share speakers with each other** (some speakers appear in both Test1 and Test2);
  only the train/dev-vs-test cut is disjoint, and even there "unknown"-speaker turns in Train may
  leak.
- **Baselines (✔, §VI, Table VII):** off-the-shelf **WavLM / Wav2vec2.0 / HuBERT (24-layer, 310M),
  fine-tuned**. Categorical = **focal loss** + 2-layer FC head over 8 classes. Attributes =
  **staged**: first adapt the SSL with **CCC loss** on V/A/D jointly, then joint-train with the
  categorical focal head, then a **single-task per-attribute regression head on a frozen encoder**.
  20 epochs, LR 1e-5, batch 32, Adam. Results — **WavLM wins everywhere**:
  - Categorical **F1-macro / F1-micro**: Test1 0.297/0.394, Test2 0.206/0.280, Test3 0.356/0.373.
  - Attribute **CCC** (V/A/D): **Test1 0.722 / 0.724 / 0.645**; Test2 0.549 / 0.547 / 0.467;
    Test3 0.632 / 0.632 / 0.479.
  - Reported ~8% relative gain over the v1.12 baselines from the larger/cleaner training set. The
    large macro-vs-micro gap on Test1 is the paper's own diagnosis of **severe class imbalance**.

### Parts directly useful for ViEmoSpeech (tagged with Decision IDs)

1. **Feature-only vs audio-releasable split of the release bundle** — **V-H**. MSP releases
   audio + per-turn categorical + V/A/D + secondary labels + speaker-ids + human transcripts +
   MFA TextGrids, *because its licenses permit audio redistribution*. ViEmoSpeech cannot release
   audio, but MSP is the precedent for **everything else in the bundle**: per-turn labels,
   timestamps, speaker-ids, and (crucially) the **license-provenance-by-screenshot** discipline.
2. **The three-test-set design, especially Test2 and Test3** — **V-G** (and **V-E**). Test1 =
   in-distribution; **Test2 = a slice sampled *without* the model-driven retrieval step, expressly
   to measure selection bias**; Test3 = class-**balanced**, labels-**withheld** blind challenge.
   A ready-made template for a speaker-disjoint + control-slice eval design.
3. **The staged CCC recipe + concrete WavLM CCC/F1 numbers** — **V-G**, **V-B**. CCC-then-joint,
   then frozen-encoder per-attribute regression head; WavLM > Wav2vec2 > HuBERT; Test1 CCC
   V 0.722 / A 0.724 / D 0.645 and **categorical F1-macro only ~0.30** on naturalistic 8-class.
4. **The annotation protocol that rejected crowdsourcing** — **V-E**. Screening test → trained
   in-house annotators → weekly relative-ranking feedback → mandatory per-attribute remedial
   re-training → remove-and-re-annotate bad raters; 1–7 SAM Likert for V/A/D with mean-consensus;
   plurality rule + explicit "no-agreement" class for categorical.
5. **Emotion-retrieval to build an emotion-*dense* corpus** — **V-H**, **V-E**. 48+-criteria
   multi-model ranking drives neutral down to 28%; and the *bias* this induces is then *measured*
   by Test2.

### How each part helps ViEmoSpeech succeed

- **V-H — release bundle & provenance.** Adopt MSP's bundle *minus audio*: per-turn
  {emotion, V/A, distress, tone, dialect, speaker-id, start/end-ts} + (optionally) forced-aligned
  phone/syllable TextGrids, CC-BY. Copy the **license-screenshot-at-collection** rule for our
  YouTube sources into the extraction-pipeline capability doc — MSP lost 40 podcasts' license
  info exactly because they didn't, a cheap failure to pre-empt. Position ViEmoSpeech in the
  Table-I corpus-comparison the same way MSP does (size / #spk / avail / type / lang) so the
  "first CC-BY Vietnamese multi-class + tone" claim reads directly against MSP, THAI-SER, DUSHA, BIIC.
- **V-G — eval & baselines.** (a) Build a **Test2-analogue control slice**: a held-out set sampled
  *without* the LLM-teacher suggestion (ADR-003), so we can literally measure whether teacher
  suggestions bias the label distribution — MSP proves this is a first-class methodological asset,
  not overhead. (b) Report our V/A head with **CCC** and cite WavLM Test1 CCC (V 0.722 / A 0.724)
  as the cross-corpus comparability anchor — but as a *ceiling under fine-tuning*, see risk below.
  (c) Use MSP's naturalistic **F1-macro ≈ 0.30** as the realistic bar for our 7-class head and put
  it in the baselines table *next to* vn-10's leaky VNEMOS 0.87 — the two together make the case
  for why speaker-disjoint macro-F1 is the honest metric.
- **V-B — backbone.** MSP's clean head-to-head says **WavLM ≥ Wav2vec2 ≥ HuBERT** for both
  categorical and attribute SER on naturalistic data; this directly supports WavLM as the default
  audio backbone arm in the V-B sweep, with the staged-CCC head as the attribute recipe.
- **V-E — annotation protocol.** Our current single-pass human labeling (κ 0.675 = *teacher*
  agreement, per recent commit) is below MSP's ≥5-rater regime. Import MSP's **remedial loop**
  (per-dimension weakness → targeted re-training) and its **1–7 SAM instrument** as the design
  reference, but see the scale-mismatch gap below. Adopt the **"no-agreement" class + plurality
  rule** so ambiguous categorical turns are explicitly marked, not silently forced (aligns with
  ADR-002's ambiguous→drop).

### Transfer-validity lens (ViEmoSpeech regime)

- **What transfers cleanly:** the annotation protocol (rater management, remedial training,
  no-agreement class), the partition philosophy (speaker-disjoint + a bias-control slice + a
  withheld blind slice), the staged-CCC attribute recipe, WavLM-first backbone evidence, the
  release-bundle shape, and license provenance discipline. None of these depend on the audio being
  English or podcast-sourced.
- **What does NOT transfer:** (1) **Audio release** — MSP's whole raison-d'être (redistributable
  CC audio) is exactly what ViEmoSpeech legally cannot do with TV-drama media; our release is
  features-only, so the *audio* half of MSP's bundle is off-limits. (2) **The cleaning pipeline
  assumes clean-ish podcasts**: MSP *filters out* music (drop if >50% music) and drops SNR <15 dB —
  it never *separates* score from voice. VN TV drama has continuous background scoring, which is
  precisely why our pipeline runs **Demucs source-separation** *before* VAD/turn-split. MSP's
  "reject, don't separate" choice would discard most of our material; our Demucs-then-keep chain is
  a deliberate, load-bearing divergence — and one that changes the acoustic domain the V-B backbone
  sees (separated vocals ≠ MSP's native podcast audio), so their CCC numbers are **not** a
  like-for-like target.
- **Scale conventions:** MSP uses **1–7 SAM** for V/A/D; the ViEmoSpeech spec uses **1–5 Russell**.
  Cross-corpus CCC comparison requires an explicit rescale/normalisation, and CCC is scale-sensitive
  in ways Pearson is not — decide this in V-E/V-G before quoting MSP CCC as our bar.
- **Ethics/authenticity:** MSP's §I *explicitly rejects acted TV-show emotion* as "exaggerated
  externalizations… lack of authenticity… ethical and copyright issues" — i.e. it names our source
  type as a weakness. That is a citation ViEmoSpeech's method paper must answer head-on: we do not
  claim clinical/naturalistic authenticity; distress is an **acted-drama proxy** (V-F framing), and
  the tone×emotion measurement (V-D) is a *phonetic-channel* claim that does not require the emotion
  to be spontaneous. Turn the critique into scope-setting, not a rebuttal we can't win.

### Limitations & open questions for ViEmoSpeech

- **Contradiction vs our pipeline (V-H / extraction-pipeline).** MSP **discards** noisy/music-heavy
  audio (SNR <15 dB, >50% music) rather than restoring it; ViEmoSpeech **restores** it with Demucs.
  If we keep clips MSP would reject, our labels sit on a noisier acoustic substrate than MSP's — so
  when we cite MSP CCC we must add a "post-separation domain" caveat, and we should report an SNR
  distribution of our *kept* clips to quantify how far outside MSP's clean regime we operate.
- **Contradiction vs vn-10 (V-G).** vn-10's VNEMOS numbers (UA 0.87 / F1 0.87) are speaker-leaky
  5-fold CV on 250 clips; MSP's speaker-disjoint naturalistic 8-class **F1-macro ≈ 0.30** is the
  reality check. Both cannot be "the bar" — our baselines table must show them as, respectively, an
  inflated ceiling and an honest naturalistic floor, or a reviewer will pick whichever suits them.
- **Gap vs our label regime (V-E).** MSP = **≥5 human raters/turn**, κ 0.411 on hard naturalistic
  8-class. ViEmoSpeech is currently **single-pass** with LLM *suggestion*, and the κ 0.675 in the
  repo is **teacher-vs-teacher**, which — per our own honest-weak-supervision invariant — is *not*
  an accuracy or a human-gold agreement. Open question: do we run a ≥3-human-rater pass on at least
  the whole-series gold slice (ADR-002) so we have a defensible κ to sit next to MSP's 0.411?
  Acted drama *should* agree higher than MSP's spontaneous speech — an advantage worth measuring,
  not assuming.
- **Attribute-scale open question (V-E/V-G).** 1–5 Russell vs MSP 1–7 SAM: pick a normalisation and
  a metric (CCC vs Pearson) before any cross-corpus V/A claim; note vn-06/Shen argued Pearson for
  our probing figures, so we may end up reporting CCC for MSP-comparability *and* Pearson for the
  tone-channel probe — state both explicitly.
- **Frozen vs fine-tuned baseline (V-B/V-G).** MSP's CCC numbers come from **fine-tuned** 310M SSL;
  if our V-B arm freezes WavLM and probes, the CCC gap is expected and must not be read as a model
  failure — match the protocol (fine-tuned) before treating 0.72 as a target.
- **Test-set speaker overlap subtlety (V-G).** MSP's *test sets overlap each other* in speakers;
  our stricter invariant (gold speakers ∩ weak pool = ∅, whole-series holdout) is actually cleaner
  than MSP here — worth stating as a point where ViEmoSpeech's protocol *exceeds* the field-standard
  corpus, rather than merely following it.
