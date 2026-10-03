# Paper vn-13 — Emotional Tones of Voice Affect the Acoustics and Perception of Mandarin Tones

- **Authors:** Chang et al. (Yueh-Chin Chang and colleagues)
- **Venue / year:** PLOS ONE 18(4):e0283635, 2023
- **Links:** article https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0283635 · PDF `pdfs/13-chang-mandarin-tone-emotion.pdf`
- **Group:** vietnamese-ser / core empirical premise (phonetics)

**Summary:** Acoustic analysis + perception experiments on emotion-inflected
Mandarin syllables: anger raises F0/amplitude, sadness lengthens duration, and
emotion affects tone identification more than tone affects emotion identification.

**Relevance to ViEmoSpeech:** The strongest peer-reviewed empirical support for
the motivating claim that lexical tone and emotional prosody compete for the
same F0 channel (V-D). Citable as the motivating phenomenon; not a modeling
paper, not Vietnamese — our corpus makes the VN version measurable.

> Stub created 2026-07-10 (task `docs/tasks/paper-deep-analysis.md`); deep-read pending.

## Deep research — full-PDF read (2026-07-10)

### Source-access note

The paper was read end-to-end from the local PDF `pdfs/13-chang-mandarin-tone-emotion.pdf`
via `pdftotext` (full 26-page extract, 1083 lines). This is **not** a preprint: PLOS ONE
18(4):e0283635 is CC-BY open access (received 2021-07-23, accepted 2023-03-14, published
2023-04-05), so the local PDF **is** the venue-of-record version — no preprint/published delta
exists. `pdftotext` scrambled the column order inside the four confusion matrices (Tables 4, 5,
7, 8), so every load-bearing number was re-validated against the published PLOS HTML.

Provenance validation (all ✔ corroborated against the published article):
- Query: `Chang Lee Wang 2023 Emotional tones of voice affect acoustics perception Mandarin tones PLOS ONE asymmetry` →
  resolved `https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0283635` (also PMC10075469).
- WebFetch of that URL confirmed: the four Experiment-1 LME chi-squares (F0, F0-range, amplitude,
  duration) incl. the two **non-significant tone×emotion interactions** (amplitude p=.98,
  duration p=.29); 8 actors / 36 listeners; tone-ID accuracy 40–98% (isolation) / 78–100%
  (context); emotion-recognition 21–93% (isolation) / 85–99% (context); the asymmetry conclusion
  and its "not higher" caveat; the ANGRY > HAPPY/SAD > FEAR ordering. All matched the extract.

Full author list (verbatim): **Hui-Shan Chang, Chao-Yang Lee, Xianhui Wang, Shuenn-Tsong Young,
Cheng-Hsuan Li, Woei-Chyn Chu** (corresponding). Affiliations: National Yang Ming Chiao Tung
Univ. (Taipei), Asia Univ. (Taichung), National Taichung Univ. of Education, Ohio Univ.
(Athens, USA), MacKay Medical College. IRB No. 1000063 (NYCU). Funded by MOST Taiwan.

### What the paper actually does

A two-experiment psychophonetics study of how emotional prosody perturbs the acoustics and
perception of the four Mandarin lexical tones. It is a **perception/acoustics** paper, not a
modeling paper — no classifier, no ML.

**Experiment 1 — acoustics (production).** Eight professional actors (4 W / 4 M, mean age
32.4 ± 7.1, Taiwan Mandarin) produced 3 target syllables /fa/, /ɕi/, /pu/ (the three commonest
Taiwan-Mandarin vowels, all real words in all four tones, all emotionally neutral in meaning),
each in all 4 tones = 12 syllable-tone combinations, crossed with 5 emotions (ANGRY, FEAR,
HAPPY, SAD, NEUTRAL), embedded sentence-medially in one fixed carrier phrase
/ni³ uo¹ [target] ts̩⁵/ "You say the word [target]". 60 word-emotion combos × 2 reps × 8 talkers
= **960 stimuli** (44.1 kHz/16-bit, GRAS 40AC mic, 30 cm). Emotion presence was independently
verified: 30 native raters, four-alternative forced choice + 5-point Likert; only stimuli
correctly identified by **all 30** raters and rated ≥3.0 were analyzed (all passed). Target
syllables were excised at the last glottal pulse of the preceding syllable and the last glottal
pulse of the target (Praat [Boersma & Weenink]). Four acoustic measures: **mean F0, F0 range,
mean amplitude, duration**. Statistics: one linear mixed-effects model per measure — fixed
effects = tone, emotion, tone×emotion; random effects = talker, talker sex, syllable, repetition.

Experiment-1 results (all ✔ corroborated; §Results, S1 Table):

| Measure | Tone main effect | Emotion main effect | Tone×Emotion interaction |
|---|---|---|---|
| Mean F0 | χ²(3)=973.95, p<.001 | χ²(4)=1749.66, p<.001 | χ²(12)=**70.18, p<.001** (sig.) |
| F0 range | χ²(3)=779.23, p<.001 | χ²(4)=123.02, p<.001 | χ²(12)=**114.64, p<.001** (sig.) |
| Mean amplitude | χ²(3)=121.1, p<.001 | χ²(4)=1801.44, p<.001 | χ²(12)=**3.92, p=.98** (n.s.) |
| Duration | χ²(3)=32.5, p<.001 | χ²(4)=639.74, p<.001 | χ²(12)=**14.2, p=.29** (n.s.) |

Directional findings: **ANGRY has the highest mean F0 and highest mean amplitude; NEUTRAL the
lowest of both; SAD has the longest duration.** The relative ranking of FEAR/HAPPY/SAD on F0
varies by tone; F0 range shows no consistent emotion ranking. The single most important structural
result: the emotion effect on **amplitude and duration is additive across tones** (no
interaction), whereas the emotion effect on **F0 mean and F0 range is tone-dependent** (strong
interaction). Predicted-vs-actual directions are in Table 1/Table 2; the main surprise vs the
literature was that ANGRY did **not** shorten duration (actual "=") and FEAR raised amplitude
("actual >" where literature allowed "> or <").

**Experiment 2 — perception (identification).** 36 listeners (23 W / 13 M, age 19–23, mean
20.08 ± 0.91, Taiwan Mandarin), pre-screened on neutral tone-ID (isolation 97/93/93/98% for
T1–T4; context 100/100/99/100%). Stimuli from the top-rated 1 female + 1 male actor. Two 4AFC
tasks × two contexts (target syllable **in isolation** = excised from the carrier vs **in
context** = with carrier phrase): tone identification (5 emotions → 240 stimuli → 480 trials) and
emotion recognition (NEUTRAL dropped to prevent it being a default "unsure" answer → 192 stimuli
→ 384 trials). Mixed-effect logistic regression (fixed: tone, emotion, context, tone×emotion;
random: talker sex, syllable, repetition).

Experiment-2 results (all ✔ corroborated; §Results, Tables 3–8, S2/S3):
- **Tone identification.** Main effects all p<.001: tone χ²(3)=83.12, emotion χ²(4)=486.38,
  context χ²(1)=**1534.71** (by far the largest), tone×emotion χ²(12)=**492.89**. Accuracy
  **40–98% in isolation, 78–100% in context.** Isolation confusion (Table 4): under ANGRY,
  Tones 1 and 3 are misheard as **Tone 4** (high-falling — the "angriest"-sounding tone); under
  FEAR, tones bias toward **Tone 1**; HAPPY/SAD show no dominant bias. In context, the only
  near-20% error is ANGRY-Tone-1 → Tone-4; the carrier phrase "effectively neutralized" emotion's
  damage to tone ID.
- **Emotion recognition.** Main effects all p<.001: tone χ²(3)=92.92, emotion χ²=775.08,
  context χ²(1)=**1843.42**, tone×emotion χ²(9)=**327.95**. Accuracy **21–93% in isolation,
  85–99% in context.** Ordering **ANGRY > HAPPY ≈ SAD > FEAR** (ANGRY best in 3 of 4 tones,
  FEAR worst in all four). Isolation diagonal accuracies (Table 7, ≈ from extract, ranges
  ✔): ANGRY 77/76/53/93% (T1–T4), FEAR 21/36/34/37%, HAPPY 82/76/49/71%, SAD 42/72/73/61%.
  Isolation confusions: SAD→FEAR (T1, T4), FEAR→HAPPY (T1, T2) but FEAR→SAD (T3, T4).
- **The asymmetry (headline).** "Emotions affect Mandarin tone identification to a greater
  extent than Mandarin tones affect emotion recognition." Evidence: tone-ID accuracy ranking
  swings wildly across emotions (Table 3), but emotion-recognition ranking is stable across tones
  (Table 6). **Critical caveat the authors themselves flag:** this is an asymmetry of *mutual
  influence*, NOT of difficulty — emotion recognition (21–93% iso / 85–99% ctx) was **not more
  accurate** than tone ID (40–98% iso / 78–100% ctx). "Emotions do not seem to be inherently
  easier to identify... their mutual influence is asymmetrical."

Stated limitations (§Conclusions): only 4 acted basic emotions (no valence/arousal coverage —
only HAPPY is positive, only SAD is low-arousal); one carrier phrase / one tonal context;
Taiwan-Mandarin only; NEUTRAL absent from the perception task; "isolated" syllables were excised,
not natively isolated; isolation-before-context ordering may have inflated context accuracy; and
— load-bearing for us — **no voice-quality measures** ("additional acoustic measures on voice
quality... would be useful") and only summary F0, no F0-contour modeling (they recommend
Functional Data Analysis).

### Parts directly useful for Pebble

1. **The interaction-magnitude contrast as the quantitative channel-competition metric — V-D
   (core), V-B.** The four LME interaction chi-squares are exactly the "how much do tone and
   emotion fight over a channel" number our method paper needs to produce for Vietnamese. Chang's
   result: F0 mean χ²(12)=70.18 and F0 range χ²(12)=114.64 are **significant** (tone entangles
   emotion's F0 cues) while amplitude χ²(12)=3.92 (p=.98) and duration χ²(12)=14.2 (p=.29) are
   **non-significant** (tone leaves emotion's amplitude/duration cues intact). This is a citable,
   peer-reviewed, per-parameter competition map. *Transfer risk:* the **direction** (F0 entangled,
   amplitude/duration free) should transfer to Vietnamese in broad strokes because tone is
   F0-borne in both; but the **magnitude** and the crucial extension to the **phonation channel**
   will not — Mandarin's 4 tones are contour-dominant, Vietnamese's 6 are phonation-heavy
   (glottalization/creak in ngã/nặng; Shen NAACL 2024, vn-06). Chang never measured phonation, so
   in VN there is a whole competition axis (voice quality) that his amplitude/duration "free"
   verdict says nothing about — and it is precisely the axis emotion also uses (creaky sadness,
   pressed anger). The delta IS our measurable contribution.

2. **Amplitude and duration are the tone-robust emotion dimensions — V-B.** Because emotion's
   effect on amplitude and duration does not interact with tone, energy/RMS-loudness and
   duration/speaking-rate features are the acoustic dimensions that stay reliable for the emotion
   head even when lexical tone is loading F0. *Transfer risk:* holds *more* strongly in Vietnamese
   than Mandarin for these two specific features (they are not tone-primary in either language),
   but the corollary — "so F0 is the only contested channel" — is FALSE for VN: phonation is a
   second contested channel Chang didn't test. So V-B action = keep amplitude/duration features as
   the safe emotion carriers **and** add explicit phonation features (jitter/shimmer/HNR/H1–H2/CPP,
   per vn-06 V-B), but do **not** treat them as automatically tone-robust the way amplitude/duration
   are — they must be probed.

3. **The perception protocol as a listener-validation template for the ViEmoSpeech gold set —
   V-E.** Chang's Experiment 2 is a clean, reusable design: pre-screen listeners on neutral-tone
   ID; independent emotion-verification pass (N=30 raters, all-correct + Likert ≥3 inclusion gate)
   *before* the main study; 4AFC identification; confusion-matrix + mixed-effect logistic
   regression analysis; and the isolation-vs-context manipulation. *Transfer risk:* directly
   adoptable in shape, but our stimuli differ fundamentally — TV-drama spontaneous multi-syllable
   turns, 7 emotions + V/A + distress, real speakers not actors. His "carrier phrase" manipulation
   maps onto our "clip cut tight at VAD∩turn vs. with a few words of lead-in context" choice.

4. **The high-arousal tone-confusion direction corroborates our ASR failure mode — V-C, V-D.**
   Chang's finding that ANGRY biases tone perception toward **Tone 4 (high-falling)** and FEAR
   toward **Tone 1** is a human-perception analogue of our observed PhoWhisper **tone-swap ASR
   errors at high arousal** (mày→máy, tao→tháo). *Transfer risk:* the specific tone targets don't
   map (different tone inventory), but the *phenomenon* — high arousal systematically distorts
   which tone is recovered — is exactly what our text branch must be robust to, and Chang is the
   perceptual-science citation that this is a real, systematic effect, not ASR noise alone.

### How each part helps Pebble succeed

- **V-D (method-paper novelty backbone).** Run Chang's Experiment-1 design as an
  acoustic-measurement study on the ViEmoSpeech gold set: per-utterance mean F0, F0 range,
  amplitude, duration, **plus** phonation measures (jitter, shimmer, HNR, H1–H2, CPP) that Chang
  omitted, then fit one LME per measure with tone × emotion (and dialect) interaction. Report the
  interaction chi-square table side-by-side with Chang's Mandarin table. The predicted, testable
  headline: in Vietnamese the F0 interaction replicates Chang, but a **phonation-channel
  interaction appears that has no Mandarin counterpart** — the first direct measurement of what
  vn-06 only inferred. This is the concrete artifact: a `docs/spec/.../tone-emotion-competition`
  experiment producing that comparative table.
- **V-B (feature/backbone choice).** Concretely: in the audio branch, ensure energy/loudness and
  rate/duration statistics survive as features (frozen SSL layers can lose absolute-amplitude info
  — add a handcrafted RMS/duration vector), because Chang proves these are the tone-orthogonal
  emotion carriers. And add the phonation vector as a first-class input, since the tone-robust
  status Chang grants amplitude/duration cannot be assumed for the phonation cues VN tone occupies.
- **V-E (listener-validation gate).** Before any headline SER claim, run a Chang-style listener
  study on a ~200-clip gold slice: (a) an emotion-verification pass with an inclusion gate
  (majority-correct + confidence floor) that doubles as a second human-teacher agreement check
  under ADR-003; (b) a tone-ID sub-study on high-arousal vs neutral clips to measure how much
  arousal degrades *human* tone recovery in VN — the human ceiling for the ASR tone-swap problem.
  Artifact: an `eval/listener_validation/` protocol doc + 4AFC annotation sheet.
- **V-C (text-branch robustness).** Cite Chang's ANGRY→Tone-4 / FEAR→Tone-1 confusion as the
  perceptual grounding for why the ViSoBERT/PhoBERT text branch must carry more load at high
  arousal: if trained human listeners mis-recover tone under emotion, PhoWhisper certainly does,
  so the fusion must not trust ASR tokens blindly when the audio branch signals high arousal.

### Child mental-health lens

- **Transfer validity is bounded three ways, all working against naive reuse.** (1) *Language:*
  Mandarin 4 contour tones ≠ Vietnamese 6 phonation-heavy tones — the phonation-channel
  competition that matters most for distress (creaky/pressed voice) is entirely outside Chang's
  measurement set. (2) *Register:* Chang used adult professional actors reading isolated CVC
  syllables in a fixed frame sentence; ViEmoSpeech is spontaneous conversational TV-drama speech.
  (3) *Age:* all subjects were adults (actors mean 32; listeners 19–23); Chang explicitly states
  **"No minors participated in this study."** There is **no** child-speech data here. Children's
  smaller vocal tract raises F0 and can compress F0-range headroom, plausibly *intensifying*
  tone-emotion F0 competition relative to adults — an untested extrapolation, not a finding.
- **Ethics contrast (useful precedent).** Chang's IRB route (NYCU IRB 1000063, written informed
  consent, paid adult actors, explicit no-minors clause) is a clean lab-consent model, but it is
  the *opposite* of ViEmoSpeech's constraint set: our speech is copyrighted third-party TV drama
  under a features-only CC-BY release with no consenting participants. Chang is not a governance
  template for us; it is a reminder that a lab-recording paper's ethics do not transfer to a
  found-media corpus.
- **Distress-relevant nuance.** Chang's SAD (long duration, low F0, no distinctive amplitude) and
  FEAR (worst-recognized, confusable with HAPPY *and* SAD) are the two emotions closest to our
  distress proxy, and they are precisely the *hardest to recognize acoustically* (FEAR 21–37% in
  isolation). This is a direct warning for the distress head's recall floor (V-F): the affect
  states we most need to catch are the ones with the weakest, most context-dependent acoustic
  signature — reinforcing that distress cannot be an audio-only decision and needs the text branch
  and the carrier-context Chang shows rescues recognition (85–99% in context vs 21–93% isolated).

### Limitations & open questions for Pebble

- **Contradiction/gap #1 (vs vn-06 Shen + our own premise).** Chang's tidy result "amplitude and
  duration carry emotion independently of tone; only F0 is contested" is derived from a language
  whose tones are F0-contour-dominant and from a measurement set that **excludes phonation
  entirely**. Our whole thesis (vn-06) is that Vietnamese tone is phonation-heavy — i.e., there is
  a *second* contested channel Chang could not see. So Chang's reassuring "two safe dimensions"
  map is **incomplete for Vietnamese by construction**, and treating it as sufficient would design
  the feature set to miss the exact channel where VN tone-emotion competition lives. The gap is the
  contribution: ViEmoSpeech can produce the phonation-inclusive interaction table Chang's design
  structurally cannot.
- **Contradiction/gap #2 (vs the stub's / project-overview's one-liner).** The stub summarizes
  Chang as "emotion affects tone ID more than tone affects emotion ID" — which invites the reading
  that emotion is the stronger, more robust channel. Chang **explicitly refutes** that reading:
  emotion recognition was *not* more accurate than tone ID (21–93% vs 40–98% isolated); the
  asymmetry is in *mutual influence*, not robustness or difficulty. Any Pebble citation must carry
  the caveat, or a reviewer who reads the paper will catch the overclaim.
- **Contradiction/gap #3 (vs vn-12 "semantics dominate" and vn-08 "text near-useless").** Chang is
  a pure-acoustics/perception study with **no text/semantic channel at all** (isolated syllables,
  4AFC on acoustics) — so it can neither support nor refute the semantics-vs-acoustics debate our
  other papers are split on. It quantifies the *acoustic* tone-emotion competition that motivates
  needing a text branch, but says nothing about how much text should weigh. Our measurable claim
  (how much load the text branch must carry) remains open and is ours to settle empirically.
- **The context effect is the biggest single effect in Experiment 2** (context χ² dwarfs tone and
  emotion: 1534.71 for tone-ID, 1843.42 for emotion-recognition). Open question for our clipping
  policy: cutting clips tight at VAD∩turn (isolation-like) vs. keeping a short lead-in
  (context-like) may materially change how recoverable both tone and emotion are — a design knob
  Chang shows is larger than the emotion effect itself. Worth an ablation on clip padding.
- **No F0-contour modeling, no voice quality, single carrier, single dialect, actors not
  spontaneous.** Every one of Chang's own listed limitations is a place ViEmoSpeech's design is
  already broader (6 tones, 3 dialects, spontaneous multi-emotion drama, phonation features) — so
  Chang is best cited as the *motivating prior* whose method we extend, not a result we replicate.
