# Paper vn-12 — Evaluating Emotion Recognition in Spoken Language Models on Emotionally Incongruent Speech

- **Authors:** (not yet extracted — verify from PDF)
- **Venue / year:** arXiv preprint, Oct 2025
- **Links:** abs https://arxiv.org/abs/2510.25054 · PDF `pdfs/12-emotionally-incongruent-slm.pdf`
- **Group:** vietnamese-ser / contrastive citation (semantics dominate)

**Summary:** Tests SLMs (SALMONN, DeSTA2, Qwen2-Audio, Audio Flamingo-3) on
synthetic emotionally-incongruent speech; SLMs rely almost entirely on textual
semantics (80–100% acc.) and are near-random (~25%) on acoustic-only emotion,
while a dedicated SER baseline handles acoustic cues far better.

**Relevance to ViEmoSpeech:** Contrastive citation — "semantics can dominate"
already happens in SLMs but as a *model-bias artifact*; our claim is a
*principled phonetic cause* (tone-locked F0/phonation). Also informs V-A/V-C
(text-branch dominance risks) and eval design for conflict cases.

> Stub created 2026-07-10 (task `docs/tasks/paper-deep-analysis.md`); deep-read pending.

## Deep research — full-PDF read (2026-07-10)

### Source-access note

The local PDF `pdfs/12-emotionally-incongruent-slm.pdf` was extracted end-to-end with `pdftotext`
(abstract, §§1–5, Table 1, Figures 1–2 captions, acknowledgements, ethics statement, references).
This is an **arXiv preprint** (arXiv:2510.25054v2 [cs.CL], 30 Oct 2025), ICASSP-style two-column
format ("Index Terms"), most likely submitted to ICASSP 2026 — no published venue version was
locatable, so the preprint is authoritative and no preprint-vs-published delta exists.

**Full author list (stub previously lacked it):** Pedro Corrêa, João Lima, Victor Moreno, Lucas Ueda,
Paula Dornhofer Paro Costa — School of Electrical and Computer Engineering, Universidade Estadual de
Campinas (UNICAMP), Campinas, Brazil; affiliated with the Recod.ai Artificial Intelligence Lab.
Funded by CAPES, FAPESP (#2020/09838-0 BI0S, #2023/12865-8 Horus), PPI-SOFTEX. Human-eval approved by
UNICAMP CEP, CAAE 59536022.8.0000.5404.

Web-validation of load-bearing numbers:
- Query `Evaluating Emotion Recognition Spoken Language Models Emotionally Incongruent Speech EMIS UNICAMP Correa`
  → resolved arXiv abstract/HTML (`https://arxiv.org/abs/2510.25054`, `https://arxiv.org/html/2510.25054v1`).
  Confirmed authors incl. full name "Paula Dornhofer Paro Costa", EMIS dataset, "semantics dominate" claim [✔].
- Query `EMIS ... SALMONN DeSTA2 Qwen2-Audio Cramer's V 0.65 proxy` + `WebFetch` of `arxiv.org/html/2510.25054v1`
  → confirmed **all Table 1 cells** (SLM target ≈25–41%, proxy 66–100%; Baseline SER target 46–52.5%),
  **Cramér's V = 0.08 (target) / 0.65 (proxy)**, **human perception 39.4/58.1/62.0% + 70.8% GT**,
  **EMIS = 1248 samples**, chi-square N = 4,978 [✔]. HTML v1 numbers are identical to local PDF v2.

### What the paper actually does

**Question.** Do speech language models (SLMs) that fuse a speech encoder with a pretrained LLM actually
integrate acoustics, or do they collapse to the text/semantic channel? Emotion recognition is used as
the probe because semantic and prosodic channels can be deliberately put in conflict.

**Stimulus construction (EMIS dataset).** [§3.1, ✔]
- GPT-4.5 generates **104 emotion-rich English sentences** across 4 emotions (angry/happy/neutral/sad),
  each split into **explicit** (contains the emotion word, e.g. "I'm so happy we finally adopted a
  puppy!") vs **implicit** (emotion only from context, e.g. "I can't stop smiling after our date last
  night"). Neutral has no explicit/implicit split (analyzed separately).
- **Three SoTA zero-shot expressive TTS systems** — CosyVoice2, StyleTTS2, F5-TTS — synthesize each
  sentence in **all 4 acoustic emotions**, conditioning expressiveness on reference recordings from the
  **ESD** emotional-speech database (10 English speakers, 350 utt/emotion; refs = 7 longest utts
  concatenated to ~32.2±3.5 s). Each TTS produces 416 samples (104×4) → **EMIS = 1248 total**.
- Per sentence this yields **1 congruent + 3 incongruent** samples. In the incongruent condition the
  **acoustic emotion is the target label**; the **semantic-content emotion is the "proxy" label**.
  Modality reliance is read off directly: high *proxy* accuracy = text-dominant; high *target* accuracy
  = prosody-attentive.

**Stimulus validation (two independent checks).** [§3.3, §4, ✔]
- A **fine-tuned acoustic SER baseline** (emotion2vec-based, ref [9], fine-tuned on an ESD subset)
  confirms the TTS acoustics carry the intended emotion — it scores **target 46–52.5% / proxy ≈1–33%**,
  i.e. it tracks the acoustic label, the desired behavior.
- **Human perceptual eval**, 40 participants on a balanced subset: identification of the *acoustic*
  emotion = **39.4% StyleTTS2, 58.1% CosyVoice2, 62.0% F5-TTS, 70.8% ground-truth ESD** [✔]. Note this
  is only modestly above 25% chance for StyleTTS2 — the synthetic incongruence is imperfectly realized
  (a real ceiling on the "SLMs are random on acoustics" claim; see Limitations).

**SLM evaluation.** [§3.2] Four SLMs — **SALMONN, DeSTA2, Qwen2-Audio, Audio Flamingo-3** — are prompted
with a **single fixed instruction that explicitly tells the model to ignore word meaning**: *"Using tone
of voice only (prosody: pitch, rhythm, loudness, timbre). Ignore word meaning; do not transcribe. Reply
with exactly one: angry — happy — sad — neutral."* Default decoding hyperparameters. Chi-square tests of
independence over N=4,978 predictions (≈4 models × 1248, minus parse failures — a minor internal
inconsistency, ≈; 4×1248=4992), 9 dof, plus Cramér's V effect size.

**Key results (Table 1 / Figure 2 / §4, all ✔ corroborated):**
- **SLM target (acoustic) accuracy ≈ chance (25% for 4-class) everywhere:** DeSTA2 25.6–38.4%,
  Audio Flamingo-3 25.0–41.3%, Qwen2-Audio 21.1–30.1%, SALMONN 25.6–36.5%.
- **SLM proxy (semantic) accuracy is high whenever text carries emotion:** in the **explicit** condition
  DeSTA2/Qwen2-Audio **95.5–100%**, Audio Flamingo-3 up to **100.0%** (categorical — always predicts the
  proxy on StyleTTS2), SALMONN 80.2–89.6%. Implicit is lower (66–92%). **Neutral** collapses proxy for
  the text-sentiment-sensitive models (DeSTA2 7.6–10.5%, Qwen2-Audio 6.7–11.5%) but stays high for
  SALMONN/Flamingo-3 (71–92%).
- **Baseline SER is the mirror image:** target 46–52.5% (well above chance), proxy ≈1–33% — genuinely
  acoustic.
- **Effect sizes:** predicted-vs-target **Cramér's V = 0.08** (negligible); predicted-vs-proxy
  **V = 0.65** (large). p<0.01 for both associations but the effect-size gap is the headline [§4, ✔].
- **Figure 2:** under the **congruent** condition SLM predictions track the (jointly-signalled) emotion
  well (diagonal ≈53–97%); under **incongruent** the diagonal collapses and predictions skew toward
  **angry/happy while ignoring sad** — an interaction between LLM text-sentiment priors and the fact
  that angry/happy are more prosodically salient than sad/neutral.

**Their explanation of *why* SLMs collapse to text.** [§4–§5] The LLM backbone's text-representation
prior dominates the fused representation; the "more easily available" the semantic emotion (explicit >
implicit > neutral), the more the model leans on it — even under a prompt that explicitly forbids using
word meaning. They frame this as a **model/architecture bias** ("text-related representations largely
dominate over acoustic representations"), not a property of any language's phonetics, and warn that
congruent-only benchmarks mask this deficiency.

### Parts directly useful for ViEmoSpeech

1. **The target/proxy-accuracy + Cramér's V protocol as a modality-reliance metric [V-D, V-G, ✔].**
   For each conflict sample, score predictions against *two* labels (acoustic-target and text-proxy) and
   report a Cramér's V for each; the gap (0.08 vs 0.65 here) quantifies text dominance in a single,
   citable pair of numbers. This is a ready-made instrument for **quantifying tone×emotion channel
   competition** — run against our audio-target label and our text/ASR-sentiment proxy on a conflict
   sub-slice.
2. **The incongruent test-set design as a conflict-slice template [V-G].** One congruent + three
   incongruent per stem; acoustic emotion = target, semantic emotion = proxy; explicit/implicit/neutral
   text-signal strata; validate stimuli with (a) an acoustic SER baseline and (b) human perception
   *before* trusting them. This is the cleanest published blueprint for our conflict sub-slice.
3. **The empirical warning that a strong text branch collapses a fused model to text [V-C].** SLM target
   accuracy sits at chance while proxy hits 80–100% whenever text carries emotion — direct evidence that
   a learned fusion containing a strong text encoder will over-attend to the semantic channel unless
   forced not to. Load-bearing for our fusion-regularization and audio-branch-not-starved decisions.
4. **The explicit contrastive distinction for our novelty defense [V-D].** Their dominance is a
   *model-bias artifact* (LLM prior beats the speech encoder, in **non-tonal English**, under
   synthetic TTS incongruence). Our claim is a *signal-level phonetic cause* — Vietnamese lexical tone
   locks F0/phonation, the same channel emotion uses, so the text branch must carry load for a
   *phonetic* reason intrinsic to the language, not because a big LLM overrides a weak encoder. Cite-and-
   distinguish sentence is now securable verbatim.
5. **The neutral-condition finding [V-C, V-D].** When the text is emotion-neutral, some SLMs' target
   accuracy *rises* (DeSTA2/Flamingo-3 to 37–41%) — evidence that text dominance is **conditional on the
   text carrying signal**. Directly relevant to our regime: spontaneous drama ASR text is often
   low-emotion-signal, which should *reduce* text dominance — but ASR tone-swap errors can inject
   *false* text signal exactly at high arousal (see lens).

### How each part helps ViEmoSpeech succeed

- **V-D (tone×emotion measurable claim).** Adopt the target/proxy + Cramér's V instrument as the
  *reporting format* for our channel-competition figure: on the conflict sub-slice, report our fusion
  model's V(pred, audio-emotion) vs V(pred, text-sentiment). If our model — unlike these SLMs — shows a
  non-negligible V against the audio label on tonal Vietnamese conflict cases, that is the positive
  result the method paper needs. Pair it with Shen-style layer-wise probing (vn-06) for the mechanism
  and this metric for the behavioral outcome.
- **V-D (novelty defense).** One sentence in Related Work: "Prior work shows SLMs default to semantics
  under incongruence (Corrêa et al. 2025), but attributes this to an LLM-backbone *representation bias*
  in non-tonal English synthetic speech; we instead identify a *phonetic* mechanism — lexical-tone
  F0/phonation competition — specific to tonal-language SER." Distinguishes cleanly without conceding
  our hook.
- **V-C (text branch under ASR noise).** Bake a **conflict sub-slice into training, not just eval**, and
  add an audio-anchoring safeguard so the fusion cannot collapse to PhoBERT: candidate levers — a
  modality-dropout schedule on the text branch, an auxiliary audio-only head, or a fusion-attention
  regularizer. Success criterion: on the conflict slice, audio-target accuracy stays well above chance
  (their SLMs failed this at V=0.08). Cite this paper as the empirical justification that the safeguard
  is necessary.
- **V-G (eval protocol).** Add a **conflict sub-slice metric line** to the eval table alongside the
  speaker-disjoint / whole-series-holdout numbers: report macro-F1 on congruent vs conflict separately,
  plus the two Cramér's V values, mirroring their Table 1 structure. Validate the conflict slice with
  our dual-teacher agreement + human gold (our analogue of their SER-baseline + human-perception check).
- **Stimulus-validity discipline.** Their human perception only reached 39.4% on StyleTTS2 — a lesson to
  *gate* our conflict slice on human recognizability before reporting model numbers, so we don't attribute
  a model's failure to text-dominance when the acoustic emotion was never audible to humans either.

### Child / Vietnamese-drama mental-health lens (transfer validity, risks, mitigations)

- **Transfer of the finding is LOW; transfer of the method and the distinction is HIGH.** The result
  (SLMs random on acoustics) is measured on **non-tonal English, TTS-synthetic, cross-speaker-reference**
  stimuli, evaluated on **giant English LLM-backbone SLMs** — none of these match ViEmoSpeech (tonal
  Vietnamese, real TV-drama speech, a small bespoke WavLM+PhoBERT fusion). So the *magnitude* of text
  dominance will not transfer. What transfers is (a) the **target/proxy Cramér's V instrument** [V-D/V-G]
  and (b) the **direction-of-risk warning** [V-C].
- **Their mechanism is prompt-specific — our model can't disobey a prompt.** Their SLMs collapse to text
  *despite an instruction to ignore word meaning*; the failure is partly instruction-following, not pure
  representation. A jointly-trained fusion with no natural-language instruction interface **cannot exhibit
  this exact failure mode** — which both weakens naive transfer of their headline and means our
  text-dominance risk, if it appears, is a genuinely learned attention imbalance, cleanly attributable.
- **The Vietnamese amplifier they never see: ASR false-signal at high arousal.** In our pipeline PhoWhisper
  makes **tone-swap errors precisely at high arousal** (mày→máy, tao→tháo). Their English text is either
  clean (GPT-generated) or absent; ours is *corrupted exactly when the audio matters most*. A text-dominant
  fusion would therefore be misled by hallucinated lexical signal at the highest-stakes (high-arousal /
  distress) moments — a sharper version of their risk with direct **V-F (distress recall-floor)**
  implications. Mitigation: the conflict slice must include high-arousal ASR-error cases, and the
  distress head should be able to fire from the audio branch alone.
- **Ethics / framing.** Their EMIS is fully synthetic English TTS — no human-subjects data beyond the
  40-listener validation (UNICAMP CEP approved). ViEmoSpeech cannot synthesize (human-labeled real drama
  under CC-BY, media never released); our conflict slice is **naturally occurring, rarer, and unbalanced**,
  so it needs human identification of conflict cases rather than controlled generation — a design cost to
  budget, not a shortcut we can borrow.

### Limitations & open questions for ViEmoSpeech

- **Contradiction #1 (REQUIRED — vs vn-08 Table V).** vn-08 (HGR VN-SER, arXiv:2604.01711) reports a
  **text-only path scoring only 38.70–44.11%** on 3-class Vietnamese SER — text "near-useless" — while
  this paper reports SLM **proxy (semantic) accuracy of 80–100%** — "semantics dominate." **Reconciliation:**
  the two measure different things on different inputs. (i) *Different text signal:* vn-12's text is
  GPT-generated, deliberately emotion-loaded English (explicit tags like "I'm so happy"); vn-08's text is
  PhoWhisper ASR of spontaneous Vietnamese dialogue with little explicit emotion vocabulary — a genuinely
  low-signal, noisy transcript. (ii) *Different quantity:* vn-12's "proxy accuracy" measures how strongly a
  model *relies on* whatever emotion the text carries; vn-08's "text-only accuracy" measures how much
  emotion the text *carries* in the first place. (iii) *Different models:* huge English LLM-backbone SLMs
  vs an un-tuned Whisper→LLM prompt path. **Both are over-readings of weak baselines** (vn-08's text branch
  is un-fine-tuned; vn-12's SLMs under-weight prosody by architecture). For ViEmoSpeech the synthesis is
  precise: *text carries little emotion in spontaneous VN drama (per vn-08), yet a strong text encoder will
  still over-attend to whatever weak/false lexical signal exists (per vn-12)* — so our text branch must be
  both fine-tuned (to extract the little real signal) and regularized/anchored (to not collapse onto ASR
  hallucinations). The measurable tone×emotion claim stays open — neither paper disentangles the phonetic
  channel.
- **Gap #2 (stimulus validity caps the "random on acoustics" claim).** Human listeners identified the
  acoustic emotion only **39.4% (StyleTTS2) / 58.1% / 62.0%** of the time (§4, ✔) — for StyleTTS2 barely
  above 25% chance. If humans can't hear the intended emotion, an SLM scoring ≈25% is not necessarily
  "ignoring acoustics" — the acoustics may not be there. The paper's headline slightly over-reads
  imperfectly-realized synthetic incongruence. ViEmoSpeech should gate its conflict slice on human
  recognizability to avoid the same trap.
- **Gap #3 (mechanism does not transfer to jointly-trained fusion).** Their dominance is demonstrated on
  **prompted** SLMs told to ignore text and failing to comply. A jointly-trained audio+PhoBERT fusion has
  no such instruction to disobey, so this paper is **motivation, not a prediction**, for our architecture —
  we must measure our own model's Cramér's V rather than assume the SLM result carries over.
- **Open question.** EMIS + code are released; worth pulling their **target/proxy scoring script and
  chi-square/Cramér's V harness** directly to standardize our conflict-slice reporting (their Github is
  cited but URL not in the extracted text — resolve from the arXiv abstract page). Also unresolved: whether
  their neutral-condition target-accuracy *rise* replicates on tonal-language audio, where "neutral text"
  still carries tonal F0 that competes with emotional F0 — a question only ViEmoSpeech can answer.
