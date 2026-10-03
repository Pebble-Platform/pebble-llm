# Paper vn-11 — THAI-SER: Thai Speech Emotion Recognition Corpus

- **Authors:** Jilamika Wongpithayadisai, Chompakorn Chaksangchaichot, Soravitt Sangnark, Patawee Prakrankamanant, et al.
- **Venue / year:** arXiv preprint, 2025
- **Links:** abs https://arxiv.org/abs/2507.09618 · PDF `pdfs/11-thai-ser-corpus.pdf`
- **Group:** vietnamese-ser / nearest tonal-language corpus precedent

**Summary:** First sizeable Thai SER corpus — 41h36m, 27,854 utterances, 200
actors, 5 emotions, scripted + improvised, crowdsourced annotation, CC-BY-SA 4.0.

**Relevance to ViEmoSpeech:** Closest published precedent for "SER corpus for a
tonal language with a clear license" — direct design comparator for corpus
paper positioning (V-H): actors/scripted vs our found TV-drama speech; their
annotation protocol and release format are reference points.

> Stub created 2026-07-10 (task `docs/tasks/paper-deep-analysis.md`); deep-read pending.

## Deep research — full-PDF read (2026-07-10)

### Source-access note

Read the full local PDF (`pdfs/11-thai-ser-corpus.pdf`, arXiv:2507.09618v1, 13 Jul 2025)
via `pdftotext` — Abstract, §1 Introduction + Table 1 (corpus landscape), §2 Corpus
design (actors, environments, scripted/improvised sessions, alignment), §3 Annotation
(crowdsourcing QC, pretest, trustworthiness), §4 Data evaluation (majority agreement,
Krippendorff α, HRA, Tables 8–11), §5 Downstream experiments (splits, CNN+LSTM baseline,
Tables 12–16), §6 Discussion, §7 Conclusion. **No separate venue version exists** — this
is an arXiv preprint with no journal/conference publication yet, so arXiv v1 is the
authoritative text. Headline numbers were web-corroborated against two independent sources:
- Query `THAI-SER Thai Speech Emotion Recognition corpus 27854 utterances 200 actors
  Krippendorff alpha` → arXiv abstract (https://arxiv.org/abs/2507.09618) confirms
  41h36m / 27,854 utt / 100 recordings / 200 actors (112F/88M) / 5 emotions / α 0.692 /
  HRA 0.772 / CC-BY-SA 4.0. ✔
- Release mechanics (V-H, load-bearing): HuggingFace `airesearch/thai-ser`
  (https://huggingface.co/datasets/airesearch/thai-ser) confirms **audio itself is released**
  (FLAC, channels mic_clip/mic_con/mic_middle/mic_zoom) + per-row labels
  (assigned_emo, majority_emo, raw responses) + metadata (session/actor/gender/age/room),
  ~27,900 rows, CC-BY-SA-4.0. ✔ Code at github.com/tann9949/thaiser-experiments.

Table-internal numbers (Tables 8–16) exist only in this single authoritative preprint;
no conflicting version, so tagged ✔ where self-consistent, ≈ where read off a figure.

### What the paper actually does

THAI-SER is a from-scratch **acted+elicited** Thai SER corpus, explicitly motivated by
Thai being a **tonal language** whose emotional acoustics differ from Western corpora (§1.1,
citing Anolli 2008, Chong/Kim/Davis 2015). Design and numbers:

- **Corpus (Abstract, §2, Table 8):** 41.61 h / 27,854 utt / **100 sessions** (each = one
  unique actor pair) → **200 actors** (112 F, 88 M; 6 non-binary/LGBTQ recorded separately;
  mean age 29, range 18–55). Six professional directors. ✔
- **Two subsets (§2.3):** *scripted* (acted) — 3 fixed sentences designed to be emotion-neutral
  and to "cover many Thai tones, consonants, and diphthongs," spoken at 2 intensity levels ×
  2 takes × 5 emotions = 60 utt/session; and *improvised* (elicited, Busso-2008 style) — 15
  situations in 3 batches, 3-min dyadic scenes, keyword-anti-overfit design. Studio hours split
  13.69 scripted / 18.01 improvised; Zoom 4.02 / 5.89 (Table 8). ✔
- **Two environments (§2.2):** **80 studio** sessions (5 mics/session: 2 lavalier RODE + 2
  cardioid WARM WA-47Jr + 1 center figure-8; 44.1 kHz/16-bit WAV) vs **20 Zoom** sessions
  (Zencastr 48 kHz, uncontrolled rooms) recorded during COVID as a deliberate noisy/OOD set. ✔
- **Emotions (§2.3):** 5 classes — neutral, angry, happy, sad, **frustrated** (frustration
  chosen for call-center relevance). Class balance is skewed by *design intent* toward
  frustration (30.52% of hours) and neutral (23.30%); angry only 10.05%, happy 13.32%,
  sad 13.33%, None (no-consensus) 9.48% (Table 8). ✔
- **Annotation (§3):** **audio-only** crowdsourcing (deliberately no video, "solely rely on
  audio-based emotion") on two Thai platforms (wang.in.th, HOPE). **Pretest**: tutorial video +
  10 screening items + 1 hidden "animal-sound trick question"; **984 of 1,759 applicants passed
  (56%)** (§3.2). ✔ Per utterance **3–8 annotators** (mostly 3; up to 8 early to tune
  guidelines) (§4.1.2 fn3). Each 10-item task salts in **gold utterances** (director-validated,
  → per-annotator "confidence score") and a **consistency utterance** (duplicate, → "consistency
  score"); annotators failing either <50% are dropped and the utterance re-annotated to ≥3
  (§3.4). Annotators capped at 30 tasks to prevent situation-memorization bias. Multi-select
  allowed; "other" emotions hand-mapped to the 5 classes (Table 7) or kept as `other`.
- **Reliability (§4, Table 9):** IAR = **Krippendorff's α with MASI set-distance** (chosen
  because annotator count varies and labels are set-valued — Cohen's κ inapplicable). **Raw
  corpus α = 0.413** (below the 0.667 bar); sweeping an agreement-score filter, the optimal
  cut is **0.71**, which raises α to **0.692** and leaves **14,182 utt** (≈7h43m usable). ✔
  **Human recognition accuracy** (majority vote vs actor's assigned emotion): 0.592 raw →
  **0.772 after 0.71-filter**. ✔ High-intensity scripted is easiest (HRA 0.883, α 0.712);
  low-intensity scripted worst (HRA 0.690, α 0.622); improvised sits between and has the
  *highest raw IAR* of any single style (0.426→0.697) despite lower HRA (§4.2.2). Neutral is
  best-recognized (78%→93%); **frustrated is the failure class** (~62%), confused with angry
  and sad (§4.2.3, Fig 9). Filtering barely differs by actor gender/age (Table 10).
- **Baselines (§5, CNN+LSTM à la Etienne 2018; 64-dim mel-filterbank, 3-s crops, VTLP, CMVN):**
  **speaker-independent 8-fold** over the 80 studio sessions (10 sessions/fold; **Zoom excluded
  from training, held out as a challenge set**). 5 seeds/fold. **All-5-emotions: WA 59.80±2.91 /
  UA 57.81±4.20**; **4-basic (drop frustrated): WA 67.34±3.05 / UA 62.61±3.19** (Table 12). ✔
  On the held-out **Zoom** set the same model collapses to **WA 46.64 / UA 46.57** (all-emo) —
  a ~13-pt OOD drop. ✔ **Scripted-only training beats improvised or all** on 4-basic
  (**WA 73.99 vs 61.80 improvised vs 67.34 all**, Table 13) — *opposite* of IEMOCAP's
  "improvised is best" (Neumann&Vu 2017), attributed to fixed-sentence scripting giving
  cleaner labels. ✔ Cross-corpus (Tables 14–16): THAI-SER-trained models transfer better to
  Emo-DB/EMOVO than IEMOCAP-trained ones even after pruning to equal hours/speakers.

### Parts directly useful for ViEmoSpeech (tagged with Decision IDs)

1. **[V-H] Nearest tonal-language corpus precedent, opposite legality trade-off.** THAI-SER is
   the closest published analogue (tonal SEA language, clear license) but sits at the *opposite*
   pole of the naturalness/legality axis: consented professional actors → **audio itself is
   CC-BY-SA-4.0-releasable** (FLAC on HuggingFace). ViEmoSpeech uses *found copyrighted TV-drama*
   → **feature-only CC-BY release, media never shipped**. THAI-SER's Table 1 (the corpus
   landscape: Emo-DB/IEMOCAP/CREMA-D/RAVDESS/MSP-*/LSSED with type∈{acted,elicited,natural}) is
   the exact positioning table ViEmoSpeech's dataset paper should extend, adding a "Release =
   features-only / media withheld" column that no listed corpus needs and that is ViEmoSpeech's
   defining constraint. Their §1.1 taxonomy (natural=privacy/copyright-risky vs acted=controlled
   but unnatural vs elicited=middle) is a ready-made framing: ViEmoSpeech is *natural/found*
   (their highest-naturalness, highest-legal-risk cell) but neutralizes the risk via
   feature-only release — a design point their acted corpus does not have to solve.
   **Transfer risk:** their size (41.6 h / 27,854 utt / 200 speakers) and class balance are
   achievable because acted recording is cheap to scale; ViEmoSpeech's found-speech pipeline
   (3,611 utt / 2 series now, ~18k/23.8h P1 target) will be smaller and *speaker-imbalanced by
   source* — cite THAI-SER as the scale bar, not a matchable target.

2. **[V-E] Crowdsourced QC scheme = concrete protocol to graft onto ADR-002/ADR-003.** Their
   trust machinery is directly portable to ViEmoSpeech's human-labeling tool: **gold-standard
   salting** (director-validated unambiguous items → confidence score), **consistency
   duplicates** (→ consistency score), **>50%-on-both trustworthiness gate with auto-drop +
   re-annotate-to-≥3**, **pretest with a hidden trick question** (56% pass rate), and a
   **per-utterance agreement-score → global-α filter** (raw α 0.413 → 0.692 at the 0.71 cut).
   Their κ-is-inapplicable argument matters for ViEmoSpeech: variable rater count + multi-select
   emotions ⇒ **use Krippendorff α with MASI set-distance, not Cohen κ** — and note that
   ViEmoSpeech currently reports teacher-agreement κ (0.675/0.857 in commit log); α+MASI is the
   correct instrument once we move to human multi-annotator V/A+distress. **Transfer risk:** their
   0.71 threshold discards ~49% of utterances (27,854→14,182) to reach α 0.692; ViEmoSpeech
   cannot afford to throw away half of a found corpus it already struggles to fill to rare-class
   floors (ADR-002, ≥50 clips), so adopt the *mechanism* (agreement score per utterance, soft
   labels retained) but keep low-agreement clips with a soft/curriculum treatment (their own §6.4
   open question) rather than hard-filtering.

3. **[V-G] Speaker-disjoint split protocol + honest OOD challenge set — a direct template.**
   Their eval is exactly ViEmoSpeech's ADR: **speaker-independent k-fold** (folds cut by
   *session/speaker-pair*, val and test never share speakers with train), **weighted +
   unweighted accuracy** reported with **5-seed std**, and a **deliberately held-out
   distribution-shift set** (Zoom) never seen in training. This is the citation ViEmoSpeech
   needs for its **whole-series held-out gold** (ADR-002) and speaker-disjoint splits (I-invariant):
   THAI-SER demonstrates the OOD gap empirically (67.3→46.6 WA studio→Zoom). It also supplies a
   *baseline realism anchor*: a competent CNN+LSTM on a clean acted 5-class tonal corpus lands at
   **WA ~60 / UA ~58** — so ViEmoSpeech's 7-class found-speech numbers should be read against
   that, not against the leak-inflated 0.86–0.87 of vn-08/vn-10. **Transfer risk:** their UA/WA
   metric is for balanced-ish acted classes; ViEmoSpeech's found corpus needs macro-F1 + CCC
   (V/A) + recall@floor (distress), so port the *split discipline* and *seed-variance reporting*,
   not the metric choice.

4. **[V-D] The tonal-language corpus that never measures tone×emotion — a novelty-space
   opening.** THAI-SER *motivates itself* on Thai tonality (§1.1) and *designs scripted sentences
   to "cover many Thai tones, consonants, and diphthongs"* (§2.3.1) — yet **nowhere in the paper
   is tone×emotion interaction analyzed or measured**; tone is used only to make the scripted
   sentences phonetically balanced, then dropped. Their frustrated↔angry↔sad confusion (Fig 9)
   is discussed purely as intensity, never as F0/tone-contour competition. **This is the cleanest
   evidence yet that the nearest tonal SER corpus leaves ViEmoSpeech's headline claim (tone is
   phonation-heavy, competing with emotion's channel — Shen vn-06) wide open.** Actionable:
   ViEmoSpeech should cite THAI-SER as "a tonal-language SER corpus that acknowledges tone
   matters but never quantifies tone-emotion channel competition," positioning the tone×emotion
   probing figure (V-D backbone) as the contribution THAI-SER gestured at but did not deliver.
   **Transfer risk:** Thai has 5 tones and is not as phonation-heavy as Vietnamese (whose glottal
   tones carry voice-quality load, Brunelle 2009); the *gap* transfers, but do not claim their
   corpus could have measured the Vietnamese-specific phonation effect.

### How each part helps ViEmoSpeech succeed

- **V-H →** Build the dataset-paper positioning table by extending THAI-SER's Table 1 with two
  columns THAI-SER doesn't need — *Release format* (features+timestamps+labels vs full audio) and
  *Source legality* (found/copyrighted vs consented). ViEmoSpeech occupies the "natural + tonal +
  feature-only-CC-BY" cell that is empty across their entire landscape (and across ViSEC/VLSP/
  VNEMOS). Concrete artifact: the comparators row in the corpus paper's intro + the release-spec
  section that cites THAI-SER as proof that a clean-license tonal SER corpus is publishable while
  distinguishing on the media-withheld mechanism.
- **V-E →** Port the gold+consistency+pretest scheme into the labeler tool (`tools/labeler/`):
  add director/expert-validated **gold clips** and **duplicate consistency clips** salted into
  each human labeling batch, compute per-rater confidence & consistency, and gate at >50%; switch
  the reported reliability statistic from κ to **Krippendorff α + MASI** for the multi-select
  V/A+distress dimensions. Keep the soft-label matrix (their §6.4 "up to 8 annotators → richer
  soft labels than IEMOCAP") for a future distress-head calibration target.
- **V-G →** Adopt their session-level speaker-disjoint fold cutting and 5-seed std reporting
  verbatim for the ViEmoSpeech benchmark; register the whole-series holdout as the analogue of
  their Zoom challenge set (an *acknowledged* distribution-shift slice reported separately). Use
  their WA~60/UA~58 clean-acted 5-class number as the "honest baseline ceiling" annotation next
  to the leak-flagged vn-08 (86.6) / vn-10 (0.87) rows in the baselines table.
- **V-D →** Anchor the tone×emotion probing figure (Shen-style layer-wise Ridge probe, arousal
  bin × tone label, phoneme-disjoint) as *the* contribution, framed against THAI-SER: "even the
  nearest tonal-language SER corpus designs for tonal coverage but never measures the tone-emotion
  channel interaction." One sentence in related work; the measurable claim is ViEmoSpeech's.

### Child mental-health lens (ViEmoSpeech transfer validity)

ViEmoSpeech is not child-facing; the relevant lens is the **legality/naturalness/consent**
axis, and THAI-SER is the sharpest comparator on it.

- **Consent + releasable audio is exactly what ViEmoSpeech cannot have.** THAI-SER's entire QC
  edifice (gold utterances chosen by directors, actors briefed and re-taking until the director
  approves, ground-truth *assigned* emotion per utterance) rests on **consented acted speech with
  a known intended label**. ViEmoSpeech has *found* TV-drama speech with **no assigned ground
  truth** — the actor's intent is unrecoverable, so ViEmoSpeech has no "HRA vs assigned emotion"
  metric available and must treat every label as perceived-only. Mitigation: ViEmoSpeech's
  human/teacher labels *are* the perceived-emotion majority (their maj-vote), so report **IAR
  (α+MASI) as the honest reliability statistic and never an "accuracy"** — which aligns with the
  repo invariant "teacher-agreement κ is never reported as accuracy."
- **Feature-only release is the ethical/legal substitute for their open audio.** THAI-SER can
  ship FLAC because 200 adults consented; ViEmoSpeech ships features+timestamps+labels+speaker-ids
  precisely because the drama actors did **not** consent to a research corpus and the media is
  copyrighted. The THAI-SER contrast is the cleanest way to explain *why* ViEmoSpeech's release is
  shaped the way it is — it is the same corpus category (acted/dramatic emotional speech) minus
  the consent/ownership that would permit media release.
- **Frustration ambiguity is a warning for the distress proxy (V-F).** Their most-confused class
  (frustrated, ~62% HRA, blends into angry+sad) shows that low-arousal negative affect is
  perceptually unstable even for attentive human raters on clean audio. ViEmoSpeech's **distress
  flag** (acted-drama proxy, recall-floor objective) is in the same perceptual danger zone —
  expect low human agreement on the distress boundary and design the recall-floor + soft-label
  treatment accordingly, rather than assuming a crisp distress label exists.

### Limitations & open questions for ViEmoSpeech

- **Contradiction vs IEMOCAP / vs ViEmoSpeech's found-speech premise (§5.2.1, Table 13):**
  THAI-SER finds **scripted > improvised** (WA 73.99 vs 61.80), the *reverse* of IEMOCAP's
  finding that improvised/natural speech trains better SER models. Their explanation — fixed
  sentences give cleaner labels — cuts *against* ViEmoSpeech's core bet that found *natural* drama
  speech is worth the legal complexity. ViEmoSpeech must answer this directly: is found natural
  speech more valuable (richer, in-the-wild) or is it just noisier-labeled data that a scripted
  acted corpus would beat? The honest position is that ViEmoSpeech trades label cleanliness for
  ecological validity and the tone×emotion measurement, and must *show* the natural-speech
  advantage, not assume it.
- **Contradiction vs vn-08/vn-10 baseline optimism:** THAI-SER's clean acted 5-class ceiling is
  **WA ~60 / UA ~58** under a *proper speaker-disjoint* split; vn-08 (86.6%) and vn-10 (0.87)
  report far higher on Vietnamese under speaker-leaky protocols. This is corroborating evidence
  that those VN numbers are inflated and that ViEmoSpeech's speaker-disjoint 7-class results will
  look "worse" while being more honest — the THAI-SER number is the fair-comparison anchor.
- **The tonal-corpus that skips tone (gap vs V-D / vs Shen vn-06):** as above — THAI-SER never
  measures tone×emotion despite motivating on tonality. Open question ViEmoSpeech owns: does the
  scripted-vs-improvised acoustic difference interact with tone-contour realization under
  emotion? THAI-SER has the data (tone-balanced scripted sentences) but never asked.
- **Hard-filtering discards half the corpus (§4.2.1, §6.4):** their 0.71 cut drops 27,854→14,182.
  ViEmoSpeech cannot copy this at its current scale; the open question they flag (soft labels /
  low-agreement curriculum, Lotfian&Busso 2019b) is the better path for a data-scarce found
  corpus — ViEmoSpeech should treat this as a to-solve, not a solved recipe.
- **Also worth noting — EMOLA (Thai TV-drama "Lakorn" emotional corpus, found via search):** a
  prior Thai attempt at *found dramatic* emotional speech exists, i.e. the found-drama route is
  not unprecedented even in Thai; ViEmoSpeech should scan EMOLA's license/release choices as an
  additional V-H comparator (not read here; flagged for follow-up).
