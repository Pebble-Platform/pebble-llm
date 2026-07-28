# Paper deep-analysis — download missing PDFs + deep-read all related papers (EN + VI)

- **Slug:** paper-deep-analysis
- **Status:** done
- **Created:** 2026-07-10  ·  **Updated:** 2026-07-10
- **Owner:** user (dev.phatdt) / agent

## Goal

Every paper related to ViEmoSpeech (the 21 bimodal-SER PDFs already downloaded
**plus** the VN/tone prior-art papers named in `docs/project-overview.md` §1.2–1.3
that have no local PDF yet) has: (1) its PDF downloaded under `docs/papers/`,
(2) a **deep, full-PDF English analysis** (6-part deep-read dossier, scored
against the **current ViEmoSpeech profile**, not the archived text-stream
profile), and (3) a sibling **Vietnamese translation** file (`NN-slug.vi.md`).

## Requirements & Constraints

- **Functional:**
  - Download open-access PDFs for the papers cited in the overview / VN scoping
    docs that lack one (list in M2 below).
  - Deep-analyze **all** related papers — both previously downloaded (21 bimodal)
    and newly downloaded — replacing the current shallow "compact entry + overlap
    score" analyses. English first.
  - For each analyzed paper, create `NN-slug.vi.md` — full Vietnamese translation
    of the analysis.
- **Constraints:**
  - Deep reads use agent `deep-read-paper`, **one per paper**, but its built-in
    profile/Decision-Register is stale (pre-pivot text stream) → every invocation
    must carry the current ViEmoSpeech profile + decision register (see Decision
    Log 2026-07-10).
  - Paper PDFs are open-access publications — fine to commit under `docs/papers/`
    (already the repo convention); episode media constraints don't apply here.
  - Append-only on existing analysis files: deep-read sections are added; the
    historical compact entries + old scores stay (they are cited by
    `00-INDEX.md` / task docs as history).
  - Paywalled papers (Annals of Telecom 2025, IEEE TAFFC Hsu&Wu, JSLHR Cantonese,
    SAGE Xiao&Liu) stay abstract-only — do **not** bypass paywalls.

## Current ViEmoSpeech profile + Decision Register (passed to every deep-read agent)

**Profile (2026-07-10, from `docs/intent/constraints.md` + `docs/project-overview.md`):**
ViEmoSpeech = first Vietnamese SER corpus that is free-content (cut from VN TV
drama; release = features+timestamps+labels+speaker-ids only, CC-BY), multi-class
(**7-way emotion + valence/arousal 1–5 (Russell) + distress flag**),
**syllable-tone-annotated** (+ dialect Bắc/Trung/Nam), **human-labeled** (ADR-003:
LLM teachers = on-screen suggestion only), speaker-disjoint splits with a
**whole-series held-out gold** (ADR-002). On top: a **tone×emotion bimodal
(audio+text/ASR) SER method paper** — hook: Vietnamese lexical tone is
**phonation-heavy** (Shen NAACL 2024), the same channel emotion uses, so the
semantic/text branch must carry more load than in non-tonal SER; distress head
carries a **recall-floor objective** (distress = acted-drama proxy, not clinical).
Pipeline: ffmpeg → Demucs → silero VAD → pyannote turn-split → PhoWhisper-base ASR
(mean sim 87.2 vs YouTube captions; ASR makes **tone-swap errors at high arousal**
— mày→máy, tao→tháo). Corpus now 3611 utt / 2 series; P1 target ~18k utt / 23.8h.

**Decision Register (current; replaces stale D-A…D-H):**
- **V-A Fusion architecture** — learned audio+text fusion to beat the rule-based
  PhoWhisper+PhoBERT baseline (arXiv:2412.09829); candidates: cross-attention,
  gated (WavFusion-style), query-based disentangling (CASE/FAS-style).
- **V-B Audio backbone/features** — WavLM vs emotion2vec(-S) vs Whisper-encoder;
  frozen vs fine-tuned; whether to add phonation/voice-quality features (jitter/
  shimmer/HNR/H1-H2) given VN tone is phonation-heavy.
- **V-C Text branch under ASR noise** — PhoBERT vs ViSoBERT vs CafeBERT; robustness
  to high-arousal tone-swap ASR errors; ASR-transcript vs gold-caption input.
- **V-D Tone representation & the tone×emotion claim** — how to encode syllable-tone
  annotations; how to *quantify* tone-emotion F0/phonation channel competition
  (the paper's headline measurable claim).
- **V-E Label scheme & annotation protocol** — 7-class + V/A + distress; human
  single-pass now, κ/α plan later; rare-class floor ≥50 clips (ADR-002); teacher
  suggestions on-screen (bias risk).
- **V-F Distress head recall-floor** — objective/threshold/calibration; honest
  proxy framing (acted drama ≠ clinical).
- **V-G Eval protocol & baselines** — speaker-disjoint + whole-series holdout;
  metrics (macro-F1, CCC for V/A, recall@floor); cross-corpus comparability
  (MSP-Podcast V/A/D); baselines: 2412.09829 (rule fusion), 2604.01711 (LLM
  reasoning, 86.6%/κ0.857), VNEMOS-line audio-only.
- **V-H Corpus design & release** — feature-only release format that stays legally
  releasable yet usable; size/class-balance targets; how to position vs ViSEC
  (no license), VLSP-56h (binary, gated), VNEMOS (250 clips), THAI-SER, MSP-Podcast.

## Milestones

- [x] M1 — Inventory: papers cited without local PDF identified; plan + doc written.
- [x] M2 — Download 8 missing PDFs → `docs/papers/vietnamese-ser/pdfs/` + stub
      entries `06–13-*.md` created. Exit: all files exist, `%PDF` magic verified.
      (2026-07-10: 8/8 OK; 09 needed retry via `export.arxiv.org/pdf/2412.09829v1` —
      plain `arxiv.org/pdf/` returned an HTML shell page for this ID.)
- [x] M3 — Deep-read wave 1 (new VN/tone core): 06 Shen · 07 CASE · 08 HGR-VNSER ·
      09 PhoWhisper+PhoBERT · 10 Dynamic-CBAM. Exit: 6-part EN section in each.
      (2026-07-10: 5/5 gate PASS. vn-09 turned out withdrawn/non-SER — see findings.)
- [x] M4 — Deep-read wave 2: 11 THAI-SER · 12 Incongruent-SLM · 13 Chang PLOS ONE ·
      bimodal 12 MSP-Podcast · bimodal 10 JMIR review. (2026-07-10: 5/5 gate PASS.)
- [x] M5 — Deep-read waves 3–6 (remaining bimodal 01–09, 11, 13–21) against the
      ViEmoSpeech profile. (2026-07-10: all 19 done + wave 1/2 = all 29 papers deep-read.)
- [x] M6 — Vietnamese translations: sibling `NN-slug.vi.md` for every analyzed
      paper (29 files). Exit: every EN analysis has a same-content VI file.
      (2026-07-10: 29/29 done — 21 bimodal + 8 VN; verified via grep, all have
      backlink lines, no missing/dup.)
- [x] M7 — Indexes updated: `bimodal-ser/00-INDEX.md` deep-read note + venue
      corrections; new `vietnamese-ser/00-INDEX.md`; `project-overview.md` §1.3
      (2412.09829 withdrawn correction) + §1.5 (header 21→29, 8-paper VN table,
      link to this doc). Number-format normalized across all 29 `.vi.md`
      (decimals→period, thousands→comma, matching EN sources; no ID/URL corrupted).
      (2026-07-12: complete.)

## Missing-paper inventory (M2 download list)

| New # | Paper | Source URL | Why |
|---|---|---|---|
| vn 06 | Shen et al. — Encoding of Lexical Tone in SSL Models (NAACL 2024) | aclanthology.org/2024.naacl-long.239.pdf | Load-bearing phonetic premise (phonation-heavy VN tone) |
| vn 07 | When Tone and Words Disagree — CASE/FAS (arXiv:2601.04564) | arxiv.org/pdf/2601.04564 | Closest architectural competitor; must cite-and-distinguish |
| vn 08 | Human-Guided LLM Reasoning VN SER (arXiv:2604.01711) | arxiv.org/pdf/2604.01711 | Most recent VN SER; names tone-confound; baseline |
| vn 09 | PhoWhisper+PhoBERT rule fusion, VNU (arXiv:2412.09829) | arxiv.org/pdf/2412.09829 | Direct baseline to beat |
| vn 10 | VN depression Dynamic-CBAM (arXiv:2412.08683) | arxiv.org/pdf/2412.08683 | VNEMOS-line baseline; distress-adjacent |
| vn 11 | THAI-SER corpus (arXiv:2507.09618) | arxiv.org/pdf/2507.09618 | Nearest tonal-language corpus precedent (CC-BY-SA) |
| vn 12 | Emotionally Incongruent Speech SLM eval (arXiv:2510.25054) | arxiv.org/pdf/2510.25054 | "Semantics dominate" contrastive citation |
| vn 13 | Chang et al. 2023 — Mandarin tone×emotion acoustics (PLOS ONE) | journals.plos.org printable | Core empirical premise citation |

Not downloadable (kept abstract-only, no paywall bypass): Xiao & Liu (SAGE),
Cantonese JSLHR 2025, Hsu & Wu (IEEE TAFFC 2023), Awatef et al. (Springer AoT 2025).

## Decision Log

- **2026-07-10 — Per-invocation profile override for `deep-read-paper`:** the agent
  definition still carries the archived text-stream profile + D-A…D-H register;
  editing `.claude/agents/deep-read-paper.md` is out of scope (surgical-changes
  rule), and the agent spec says decisions are "given per-invocation" — so every
  spawn carries the ViEmoSpeech profile + V-A…V-H register above and instructs the
  agent to ignore the stale built-in block. Rejected: editing the agent file
  (bigger blast radius, not requested).
- **2026-07-10 — New VN papers live in `docs/papers/vietnamese-ser/` numbered 06+
  with a `pdfs/` subfolder,** mirroring the bimodal-ser layout (`NN-slug.md` +
  `pdfs/NN-slug.pdf`). 00–05 stay thematic scoping docs. Rejected: a new stream
  folder (fragments the VN stream); renumbering 00–05 (breaks links).
- **2026-07-10 — Translations are sibling files `NN-slug.vi.md`** next to each EN
  analysis, full-content translation (not summary). Rejected: one consolidated VI
  file (unwieldy at 29 papers; breaks per-paper linking). User asked EN first,
  then a separate VI md — per-paper siblings satisfy both at scale.
- **2026-07-10 — Scope of "deep analysis" = all 21 bimodal + 8 new VN/tone papers**
  (user: "cả những bài đã download từ trước và mới download"). Waves of 5
  (agent-per-paper), VN/tone core first since it carries the novelty claim.
  Existing compact entries stay; deep-read sections append (history preserved).
- **2026-07-10 — Deep-read section header dated 2026-07-10** (agent template
  hardcodes 2026-06-16 — instruct per-invocation to use today).

## Open Questions

- [ ] None blocking currently. (Paywalled 4 papers stay abstract-only by
  constraint, not a question.)

## Research Findings

### Wave 1 (vn-06…vn-10) — COMPLETE 2026-07-10, 5/5 gate PASS

**vn-06 Shen NAACL 2024 — done, gate PASS.** Decisions moved:
- **V-B:** add explicit handcrafted phonation/voice-quality vector (jitter, shimmer,
  HNR, H1–H2, CPP, spectral tilt) alongside SSL; prefer VN/PhoWhisper-fine-tuned
  encoder read from **mid layers** (tone peaks mid-stack; ASR-FT on tonal language
  enhances tone encoding).
- **V-D:** operationalize channel-competition with Shen's layer-wise Ridge probe run
  twice (tone label + arousal bin) under a phoneme-disjoint split — that figure IS
  the method paper's novelty backbone.
- **V-G:** carry F0/MFCC/ASR-text baseline ladder + phoneme-disjoint split in every
  probing figure (Ryant-2014a 15.56% MFCC-only shows lexical leakage inflates probes).
- ⚠ Key nuance: "phonation-heavy VN tone" is **inferred** in Shen (Mandarin→VN
  non-transfer + Brunelle 2009 citation), never directly measured — ViEmoSpeech can
  own the first direct measurement. Probing accuracies are figure-only (no numeric
  table citable).

**vn-07 CASE/FAS (2601.04564) — done, gate PASS.** Decisions moved:
- **V-D (novelty defense RESOLVED):** CASE "tone" = paralinguistic tone-of-voice;
  languages EN+Mandarin+Chinese dialects, fully synthetic TTS (378 samples); never
  studies lexical-tone×emotion → our claim untouched, one-sentence distinguish.
- **V-A:** adopt FAS *shape* as learned-fusion baseline: two frozen streams + Top-K
  L2-saliency token distillation + N_q=2 Q-Former head (3.45M params; best
  k_aco=8/k_sem=16, d=512; FAS 59.38% CASE vs Concat 53.65/Gated 53.12) — swap
  streams to WavLM/emotion2vec + PhoBERT-over-PhoWhisper.
- **V-G:** add held-out acoustic-semantic-conflict sub-slice metric line.
- ⚠ FAS never confronts ASR noise (clean features); rare-class collapse (0 correct
  fear/disgust on CASE) = V-F red flag for flat CE.

**vn-09 — see MAJOR CORRECTION below (withdrawn, no baseline number; re-implement
their §2.6 text-priority override rule ourselves as the rule-fusion baseline row;
V-C negative exemplar: clean-text-trained classifier run on ASR output unadapted).**

**vn-08 HGR VN-SER (2604.01711) — done 2026-07-10, gate PASS.** Deep-read in
`docs/papers/vietnamese-ser/08-human-guided-reasoning-vnser.md`. Decisions moved:
- **V-E:** adopt their 3-rater, written-guideline, disagree→adjudicate,
  ambiguous→drop structure; but report κ **per label-dimension** — their κ=0.8574
  is a ceiling for a coarse 3-class scheme, not a bar for our 7-class+V/A+distress;
  keep a coarse rollup (distress binary) where high agreement is attainable.
- **V-G:** comparator only, NOT a runnable baseline — corpus closed (no
  data-availability/license/consent statement, validated absent), splits not
  speaker-disjoint (likely leak-inflated 86.59%); reuse their model-vs-human-ceiling
  *table format* under ADR-002.
- **V-D:** verbatim §I quotes secured — newest VN SER names tone/region confound,
  builds features on pitch/energy (the tone channel), never disentangles tone.
  Cleanest novelty-gap evidence.
Contradiction vs vn-12: their Table V says "text near-useless" (38.7–44.1% text-only)
— opposite of vn-12's "semantics dominate"; both over-read weak baselines → our
measurable tone×emotion claim stays open.

**vn-09 fusion (2412.09829) — MAJOR CORRECTION (from deep-read section):** the paper
was **withdrawn by its authors at v2 (2024-12-18)** citing "significant inaccuracies
in the results," and is NOT a SER paper — it is a call-centre service-quality
pipeline (Good/Neutral/Offensive); text branch = PhoBERT-CNN **hate-speech** (ViHSD),
audio branch = pretrained Dynamic-CBAM (vn-10's model), fusion = hand-written
priority-override rule with **no end-to-end evaluation** — "the number to beat"
does not exist. §2.4's own numbers are internally inconsistent (CLEAN recall 36.71%
incompatible with 86.14% accuracy). ⇒ `project-overview.md` §1.3 framing "baseline
trực tiếp để vượt" must be corrected in M7: cite as *withdrawn rule-fusion prior
attempt* (V-A positioning: soft, feature-level, jointly-trained vs hard,
label-level, hand-ordered), not as a baseline number.

**vn-10 Dynamic-CBAM (2412.08683) — done 2026-07-10, gate PASS.** Deep-read section
in `docs/papers/vietnamese-ser/10-vn-depression-dynamic-cbam.md`. Decisions moved:
- **V-F:** cite as the *anti-pattern* — 5 acted emotions sold as "depression
  diagnosis" with zero clinical anchor; our distress-head spec should name this
  overclaim as the contrast.
- **V-G:** VNEMOS UA 0.87/WA 0.86/F1 0.87 goes in the baselines table **flagged
  speaker-leaky** (5-fold CV stratified by class, not speaker; 250 clips/27
  sources) — inflated upper bound, justifies our speaker-disjoint holdout.
- **V-B:** their "MFCC-only beats raw-waveform dual-stream" = from-scratch 1D-CNN
  on 250 clips, NOT evidence against pretrained WavLM/emotion2vec; keep an MFCC
  baseline arm and test, don't assume.
Contradictions: +0.01 UA margin within unreported CV variance; depression never
operationalized; their 0.87 not comparable to speaker-disjoint numbers.

### Wave 2 (vn-11…13, bimodal 12, bimodal 10)

**vn-11 THAI-SER (2507.09618) — done 2026-07-10, gate PASS.** Decisions moved:
- **V-H:** extend THAI-SER's Table-1 corpus-landscape as OUR positioning table,
  adding "release = features-only / media-withheld" + "source legality" columns;
  THAI-SER = same category (acted tonal-language SER, CC-BY-SA, audio released on
  HF) at the opposite legality/naturalness pole; scale bar (41.6h/27,854 utt/200
  actors), not a matchable target.
- **V-E (big, actionable):** port their crowd-QC into `tools/labeler/`: gold-salting
  (director-validated items → confidence score), consistency-duplicate, pretest with
  trick question (pass rate 984/1759=56%), <50% trust gate; report **Krippendorff α
  (+MASI for multi-select)** instead of Cohen κ; their raw α=0.413 → 0.692 after
  0.71 agreement-filter (keeps 14,182/27,854 utt) — precedent for keeping
  low-agreement clips soft rather than hard-filtering.
- **V-G:** session-level speaker-independent 8-fold + 5-seed std + held-out OOD set
  (their Zoom ≈ our whole-series ADR-002); honest clean-acted anchor WA 59.80/UA
  57.81 (5-emo) vs the leak-inflated VN numbers (vn-08 86.6, vn-10 0.87).
- **V-D bonus:** tone-balances scripts, never measures tone×emotion → nearest tonal
  corpus leaves our claim open.
- ⚠ Contradiction to confront: scripted > improvised (WA 73.99 vs 61.80) — reverses
  IEMOCAP lore and cuts against our found-natural-speech bet; we must *show* the
  naturalness advantage, not assume it.

**vn-12 Incongruent-SLM / EMIS (2510.25054) — done 2026-07-10, gate PASS.**
Authors: Corrêa, Lima, Moreno, Ueda, Paro Costa (UNICAMP). Decisions moved:
- **V-D:** adopt their **target/proxy accuracy + Cramér's V pair** (theirs: 0.08 vs
  0.65) as the reporting instrument for our channel-competition figure;
  cite-and-distinguish: their text dominance = model-bias artifact (LLM prior,
  English, synthetic TTS); ours = signal-level phonetic cause.
- **V-C:** SLM target≈chance (21–41%) / proxy 80–100% = warning that fusion with a
  strong text encoder collapses to text → bake conflict slice into training +
  audio-anchoring safeguard (modality-dropout / aux audio-only head).
- **V-G:** conflict-slice template: 1 congruent + 3 incongruent per stem;
  acoustic=target, semantic=proxy; explicit/implicit/neutral strata; validate
  stimuli with SER baseline + human perception.
- Reconciliation vn-08↔vn-12 done: "how much text *carries*" (spontaneous VN ASR,
  low) ≠ "how much a model *relies* on text" (LLM prior, high) — both over-read
  weak baselines; our text branch must be fine-tuned AND regularized.
- ⚠ Caveat: humans only 39.4% on StyleTTS2 acoustics (chance 25%) — part of "SLMs
  random on acoustics" is "the acoustics weren't there."

**bimodal-10 JMIR review — done 2026-07-10, gate PASS.** Decisions moved:
- **V-F:** reproducible clinical distress signature = *reduced prosodic range*
  (flat affect; energy-SD/kurtosis/skewness; lower emotional variability) → feed
  distress head an utterance-level prosodic-variability vector; clinical
  AUC≈0.80/sens 0.86 band = analogy anchor for "screening favours sensitivity"
  only, never a target (our flag = acted proxy).
- **V-E:** external support for carrying BOTH categorical + dimensional labels;
  warning: the two spaces don't map cleanly → distress stays a separate label,
  never derived from V/A.
- **V-G:** QUADAS-2 pitfalls (5/14 patient-selection bias, small-N, leakage —
  review even reports a 98.7% DAIC-WOZ number uncritically and omits an N=20) →
  our correctives named: speaker-disjoint, whole-series holdout, ≥50-clip floor,
  metrics split by ASR-error presence.
- **V-H/V-D:** review is EN+Mandarin-dominated, zero Vietnamese, zero
  tone-as-lexical-channel, and excludes bimodal by design → novelty whitespace
  confirmed; V-D stays open on all sides.

**vn-13 Chang PLOS ONE 2023 — done 2026-07-10, gate PASS.** The core empirical
premise, now with exact numbers. Decisions moved:
- **V-D (premise quantified):** emotion's effect on **F0 mean + F0 range is
  tone-dependent** (sig. tone×emotion: F0 χ²(12)=70.18 p<.001; F0-range
  χ²(12)=114.64 p<.001) but on **amplitude + duration is additive/tone-independent**
  (amp p=.98, dur p=.29). ⇒ this is the precise, citable statement that tone and
  emotion *share the F0 channel specifically*. The headline asymmetry: emotion
  perturbs tone-ID more than tone perturbs emotion-ID — but authors flag it is
  asymmetry of *mutual influence*, NOT of difficulty (emotion-ID not more accurate).
- **V-B:** since amplitude + duration carry emotion *independently of tone*, they
  are the reliable emotion-acoustic dimensions when F0 is tone-loaded → weight
  amplitude/energy + duration features in the audio branch; treat F0-derived
  features as tone-contaminated.
- **V-E:** their all-30-raters-agree stimulus-validation gate is a template for a
  listener-validation study on our gold subset.
- ⚠ Transfer delta = itself a research point: Mandarin = 4 contour tones; Vietnamese
  = 6 phonation-heavy tones (vn-06). Chang's F0-channel-competition should transfer
  AND our phonation dimension may show additional VN-specific competition Mandarin
  doesn't — the measurable VN-vs-Mandarin delta.

**bimodal-12 MSP-Podcast (2509.09791) — done 2026-07-10, gate PASS.** The
found-speech corpus + V/A/D annotation precedent. Decisions moved:
- **V-H:** MSP releases everything *except audio* is NOT true — MSP releases audio;
  BUT its provenance model (license-screenshot-at-collection: CC-BY 90.86%,
  CC-BY-SA 5.59%) + per-turn labels/timestamps/speaker-ids is the template; position
  ViEmoSpeech in a Table-I-style comparison as the found-speech corpus that releases
  features-only because its source (TV drama) is *not* CC-licensed like podcasts.
- **V-E:** import their rejected-crowdsourcing→screened-raters→weekly-feedback→
  per-attribute remedial-retraining loop, the "no-agreement" class + plurality rule;
  build a slice sampled **without** LLM-teacher suggestion to measure ADR-003
  suggestion bias.
- **V-G:** three-partition speaker-disjoint design; report V/A head with **CCC**
  against WavLM anchors (Test1 V 0.722/A 0.724/D 0.645); honest bar = naturalistic
  8-class macro-F1 ≈ 0.30 next to vn-10's leaky 0.87.
- **V-B:** WavLM ≥ Wav2vec2 ≥ HuBERT clean → WavLM default.
- ⚠ Pipeline contradiction: MSP *discards* music/noisy audio (SNR<15 dB, music>50%
  rejected, no source-separation); we *restore* it with Demucs → our labels sit on a
  noisier substrate, MSP CCC not like-for-like. Scale mismatch: MSP 1–7 SAM vs our
  1–5 Russell. MSP explicitly rejects acted TV-drama emotion — our method paper must
  answer this via the acted-proxy framing (V-F/V-D).

### Wave 3 (bimodal 01–05) — COMPLETE 2026-07-10, 5/5 gate PASS

- **bimodal-01 C²SER:** V-B add **Emotion2Vec-S** frozen checkpoint (biggest jump on
  tonal acted CASIA UA 62.95 vs WavLM 47.25 / emotion2vec 47.58, but gains vanish on
  spontaneous speech → A/B on our clips). V-A Whisper+Emotion2Vec-S template
  (existence proof, not copyable 7B-LoRA module). V-C text-only cascade collapses
  register-dependently (13.93 acted vs 63.31 in-the-wild). Purely categorical — moves
  nothing for V/A-CCC or distress.
- **bimodal-02 ABHINAYA:** V-A "bimodal" = late majority vote over 5 models; only
  learned fusion = ST1 input-concat ASR-text+speech into SALMONN (+1.56). V-E/V-G
  imbalance is **loss-only** (WCE/weighted-focal/vector-scaling), best loss
  modality-dependent (WFL→audio, VS→text); even full machinery caps fear ~26–29% F1
  → ≥50-clip corpus floor is a better rare-class lever than loss tricks. Fine-tunes
  WavLM → ceiling not a frozen bar.
- **bimodal-03 EAA:** V-A dual cross-attention template BUT it's audio↔audio
  (HuBERT+BEATs), NOT audio↔text (corrects old entry). V-F anti-pattern: names
  mental-health, evals MELD sitcom, no distress label. MELD acc 0.687.
- **bimodal-04 MDAT:** venue corrected → IEEE OJCS 2024 (not "under review TAFFC").
  V-B add **XLS-R** multilingual frozen arm (128 langs incl. VN). V-H cross-lingual
  pretrain → K-shot own-gold (5–15 samples lifted 40–60%→80–92% UA) to seed rare
  classes faster than collection. NO tonal language tested anywhere.
- **bimodal-05 emotion-reasoning:** V-A **task-alternating** schedule > naive joint
  loss (+4–6 pts on emotion tasks). V-D reasoning grounds in **transcript, never
  acoustic/phonetic** channel — same blind spot as vn-08 → our whitespace is
  acoustic-grounded tone×emotion explanation. Reasoning buys explainability not
  accuracy (evidence-grounded 58.1 ≈ interpretive 57.8). No V/A/CCC anywhere.

**★ CROSS-CUTTING SYNTHESIS (emerging across 15 papers, load-bearing for the paper):**
1. **Text-vs-audio dominance is register-dependent, not settled.** vn-12 "semantics
   dominate" (English, LLM prior, synthetic) vs vn-08 "text near-useless" (VN
   spontaneous ASR, 38–44%) vs bimodal-02 speech>text vs bimodal-01 text collapses on
   acted tonal (13.93) but not in-the-wild (63.31). ⇒ ViEmoSpeech must **reframe its
   hook**: not a blanket "text branch carries more load," but a *measurable
   acoustic-channel* claim — tone competes with emotion in F0/phonation specifically
   (grounded in vn-13 Chang's sig. F0 interaction + vn-06 Shen's phonation finding) —
   and text-reliance is an empirical question to measure per-register, not assume.
2. **NO paper (0/15 so far) measures lexical-tone×emotion channel competition.** CASE,
   C²SER, MDAT all use tonal Mandarin yet treat "tone" as paralinguistic pitch or
   never as a variable. V-D novelty fully intact and now triangulated from 4 angles.
3. **Leak-inflated VN baselines** (vn-08 86.6, vn-10 0.87) vs honest speaker-disjoint
   anchors (THAI-SER WA~60, MSP naturalistic macro-F1 ~0.30) — our eval must publish
   the honest number and flag the leaky ones, not chase them.
4. **Recurring anti-pattern**: clinical/mental-health framing on acted categorical
   emotion with no clinical label (vn-10, EAA) — our acted-drama-proxy + recall-floor
   framing (V-F) is the deliberate correction, cite these as what-not-to-do.

### Wave 4 (bimodal 06,07,08,09,11) — COMPLETE 2026-07-10, 5/5 gate PASS

- **bimodal-06 WavFusion:** V-A gated fusion (Eqs 8–11) candidate BUT grafted inside
  unfrozen wav2vec2 deep layers (not drop-in on frozen; corrects old entry); all gold
  transcripts → gain (+3.82 WF1) predicts smaller on our noisy ASR. V-E margin loss
  (β=1, +2.94) to align audio↔ASR-text of same clip. No per-class F1/std → rare-class
  collapse hidden.
- **bimodal-07 BCAF:** genuine audio↔text fusion (RoBERTa transcript, NOT audio↔audio
  like EAA). V-A adopt per-modality **deep-supervision** (3 CE heads) as the
  audio-anchoring safeguard vn-12 demanded + correlative-attention noise-gate +
  CLIP-style connection loss. Gold transcripts only; "noise" = acoustic not ASR.
  Internal contradiction: abstract "+3.15% over HCAM" vs §V.D "worse than HCAM".
- **bimodal-08 graph-fusion:** V-B only prosodic feature = **F0 quantized to 256 bins
  → embed** (+1.9 F1) — exactly the tone-contaminated channel in VN (vn-13); prefer
  amplitude/duration or tone-condition F0. Backbone rank on naturalistic MSP:
  **Whisper-V3 > XEUS > WavLM > HuBERT > Wav2Vec2** (contradicts "WavLM default" →
  add Whisper-encoder + XEUS arms). Graph fusion only +1.3 over concat (within seed
  variance) → concat is the honest fusion baseline.
- **bimodal-09 BLSP-Emo:** ALM existence proof, NOT copyable (full fine-tune Whisper+
  Qwen-7B). ★ **EAA <1B fusion (MELD 0.687) beats BLSP-Emo 7B ALM (0.573) by ~11pts**
  → supports small-fusion-over-ALM bet. V-C add aux categorical emotion head (removing
  it drops RAVDESS 72→66.6); staged semantic-first curriculum. Text-only RAVDESS 11.1%
  (register-dependent collapse). "Tone" = intonation, not lexical → V-D intact.
- **bimodal-11 bridging (RoBERTa+WavLM) — CLOSEST to our PhoBERT+WavLM plan:** V-A
  their project→concat→dropout→MLP is the simplest learned-fusion baseline row (between
  rule-fusion and cross-attn); fine-tuned ceiling not frozen bar. V-C RoBERTa config
  (64-tok, [CLS], lr 2e-5) as PhoBERT default but feed ASR text not gold. V-G IG(text)+
  Occlusion(audio) XAI lens for the tone×emotion figure, aligned to syllable boundaries.
  ⚠ Their eval set is ill-defined (RandomSplit 0.8/0.2, not standard MELD; confusion-
  matrix counts unmappable; Table-4 SOTA compares 5-class acc vs TelME 7-class wF1
  67.37) → cite as what-NOT-to-do, motivates ADR-002 speaker-disjoint + macro-F1.

**★ SYNTHESIS UPDATE (now 20 papers):** cross-cutting theme #1 (register-dependent
text dominance) is now confirmed from 7 independent papers — bimodal-11 clean-transcript
text dominance (0.79≈0.83 multimodal) is the *opposite pole* from vn-08's VN-ASR
"text near-useless" (38–44%). The regime axis is: **clean gold transcript → text
dominates; noisy spontaneous ASR (our register) → audio dominates.** ViEmoSpeech sits
firmly in the audio-dominant regime, which *reframes the hook*: our text branch is NOT
automatically load-bearing — the tone×emotion claim is specifically that **lexical tone
degrades the AUDIO F0/phonation channel**, forcing the model to recover emotion from
(a) tone-independent acoustics (amplitude/duration, vn-13) and (b) whatever the noisy
ASR text still carries. That is the measurable, defensible framing. Also: 3 fusion
templates now in hand (CASE/FAS Q-Former, WavFusion gate, BCAF deep-supervision) all
validated on gold transcripts only → our ASR-robustness ablation is genuinely novel.

### Wave 5 (bimodal 13,14,15,16,17) — COMPLETE 2026-07-10, 5/5 gate PASS

- **bimodal-13 MMERC survey (EMNLP25):** V-A fusion taxonomy map — adopt primary–
  auxiliary cross-attention shape but **flip primary to audio** for our noisy-ASR/
  single-utterance register; **exclude graph family** (no inter-utterance edges).
  **M3ED (Chinese TV drama, 990 dial/24,449 utt/56 series)** = structural analogue
  anchor for V-H positioning. ERC has no CCC convention. Audio front-end pre-SSL.
- **bimodal-14 MCER survey (ACM TOIS?):** ⚠ **stub correction** — "ACM TOIS accepted"
  uncorroborated (arXiv no journal ref; "J. ACM" = acmart placeholder); CH-SIMS stat
  inflated (survey ~10k vs real 2,281). Complementary to 13 not redundant: 14 =
  speaker-GCN conversation-dynamics axis, 13 = text-dominant modality axis; they agree
  only naive concat is the floor → don't double-cite as one fusion recommendation.
  V-E LDAM/class-balanced-focal for rare classes; CH-SIMS = cat+continuous-intensity
  precedent. V-G their "WA" is inverse-freq-weighted (opposite of THAI-SER/MSP → trap).
- **bimodal-15 replication (Schuller, IEEE TAFFC 2026) — ★ strongest methodological
  ally:** V-G honest naturalistic speaker-independent ceiling **~0.65 UAR, NOT 0.87**
  (vs leaky vn-08 86.6/vn-10 0.87); model UAR vs year/MACs/params **ρ≈0** (bigger/
  newer ≠ better); backbone rankings HP-unstable → no leaderboard trustworthy, A/B on
  our clips with 95% bootstrap CIs. V-B domain-adapted (PhoWhisper-warm) SSL beats
  bigger cold one; keep eGeMAPS arm. V-D their probing shows SSL **under-encodes pitch
  dynamics** (σ(pitch) .237 vs μ .959) → corroborates phonation-feature branch + F0-
  channel framing. Contradicts bimodal-08's Whisper>WavLM leaderboard (rankings not
  portable). Pin corpus version/hash (MSP yearly re-releases broke comparability).
- **bimodal-16 databases review (MDPI Data 2025) — ★ strongest corpus-novelty
  evidence:** V-H adopt their 4 canonical dims (Scope/Physical-Existence/Contents/
  Language) as positioning-table skeleton + **add 2 columns they omit** (Release-form,
  Source-legality); §5.3/§7.3 "sharing only derived features" = **peer-reviewed
  justification for our features-only CC-BY release**. **0/52 Vietnamese · 6/52 tonal
  but 0/52 annotate lexical tone · 0/52 combine cat+dim+distress** (CAVES Cantonese =
  tone-balanced-for-control, cite-and-distinguish). V-E carrying cat+dim is rare
  (~8/52), never with distress or tonal. ⚠ Q-index citation-biased (penalizes new
  under-resourced-language corpora) — don't use Q to argue our value.
- **bimodal-17 RJCMA (CVPRW24, audio-visual control):** V-G **CCC loss L=1−ρc**
  (scale/shift-invariant) = the V/A head objective; report CCC + QWK/MAE (our labels
  discrete 1–5). V-A their joint cross-modal attention collapses to audio↔text fusion
  when visual dropped (l=1 on small corpus). V-B their VGGish encoder = do-NOT-copy
  control. Frozen BERT → near-zero valence gain = evidence text encoder must be
  fine-tuned (V-C). No ASR-robustness ablation (same blind spot as all fusion papers).

### Wave 6 (bimodal 18,19,20,21 — audio-visual controls) — COMPLETE 2026-07-10, 4/4 PASS

- **bimodal-18 JMT (CVPRW24):** V-A joint-branch + key-based cross-attention = cheapest
  non-recursive fusion-ladder row; targets "both modalities noisy" (our ASR-tone-swap
  + noisy drama audio). ★ **JMT (test CCC 0.458) LOSES to RJCMA #17 (0.5807)** on same
  Aff-Wild2 test — and RJCMA's winning ingredient is the **text stream JMT drops** →
  argues FOR keeping the text branch + recursive/Q-Former. V-G CCC loss (identical to
  RJCMA). V-B ResNet18-spectrogram = do-not-copy floor.
- **bimodal-19 HiCMAE (Information Fusion 2024, AV-SSL):** V-B **negative/bounded** —
  its audio-only branch loses to frozen WavLM-Plus on every acted corpus (CREMA-D
  71.01<73.39, IEMOCAP 65.23<67.12, RAVDESS 72.29<75.36); gains are AV-fusion effect we
  can't access → do NOT SSL-pretrain a VN encoder for pilot; DO import cheap **HFF trick**
  (learnable per-layer weighting over frozen stack). V-D clarifying non-transfer:
  contrastive = cross-modal *alignment*, opposite of within-audio tone/emotion
  *disentangling* → don't mis-cite; V-D intact. Cross-lingual: EN-pretrained loses to
  HuBERT-CH on Chinese TV audio (55.33<61.16 WF1). ⚠ leans on debunked Mehrabian 7/38/55.
- **bimodal-20 AVT-CA (preprint):** V-A **REDUNDANT** — textbook bidirectional
  cross-attention, nothing beyond RJCMA/FAS/BCAF for our register. V-G leak-inflated
  (random 80/20, 94–96% on acted + MOSEI) → "what-not-to-do" row next to honest number.
- **bimodal-21 HMATN (MDPI Math 2025):** V-A **REDUNDANT** (visual-spatial attention,
  no text analog). Stub headline number was wrong (validation-fold, not test 0.416 =
  NOT SOTA). V-G third CCC-loss vote for V/A head; mixed-rigor eval (IEMOCAP 75.39
  random-split, leak-inflated). Corrects old "Best point" that credited an unsupported
  noise-robustness claim (no modality-dropout/noise experiment exists).

**★ FINAL SYNTHESIS (all 29 papers deep-read):** the four load-bearing conclusions for
the ViEmoSpeech paper, each triangulated across ≥3 independent papers:
1. **Novelty is intact and now quadruply-confirmed** — 0/29 papers measure lexical-
   tone×emotion channel competition (vn-06/07/13, bimodal-01/08/13/16 all use tonal
   Mandarin/Cantonese yet treat tone as paralinguistic pitch or never as a variable);
   bimodal-16: 0/52 corpora annotate lexical tone, 0/52 Vietnamese, 0/52 cat+dim+distress.
2. **Reframe the hook** (from register-dependence, 7 papers): NOT "text branch carries
   more load" (that's regime-dependent — clean transcript→text dominates, noisy ASR→audio
   dominates, and we're in the audio-dominant regime). The defensible claim: **lexical
   tone degrades the AUDIO F0/phonation channel** (vn-13 sig. F0 interaction + vn-06
   phonation finding + bimodal-15 SSL under-encodes pitch dynamics), forcing recovery
   from tone-independent acoustics (amplitude/duration) + noisy ASR text — measured, not
   assumed, per register.
3. **Honest-eval brand is externally backed** (bimodal-15 Schuller): naturalistic
   speaker-independent ceiling ~0.65 UAR not 0.87; leaky VN baselines (vn-08 86.6, vn-10
   0.87) + AV papers (20,21) flagged; ρ≈0 model-size-vs-accuracy; A/B on our clips w/ CIs.
4. **Concrete build recipe assembled:** fusion = FAS Q-Former / WavFusion gate / BCAF
   deep-supervision shortlist (all gold-transcript-only → our **ASR-robustness ablation is
   genuinely novel**, the unclaimed axis across all fusion papers); V/A head = **CCC loss
   L=1−ρc** (4 independent votes: 17,18,21 + MSP-12); audio branch = frozen WavLM/
   emotion2vec(-S) + HFF layer-weighting + phonation features + tone-independent amp/dur;
   annotation = THAI-SER/MSP crowd-QC (gold-salt, consistency-dup, Krippendorff α);
   rare classes = ≥50-clip corpus floor (beats loss tricks) + optional K-shot transfer.

## Completed Work

- 2026-07-10 — Inventory + plan; tracking doc created — `docs/tasks/paper-deep-analysis.md`
- 2026-07-10 — M2 done: 8 PDFs in `docs/papers/vietnamese-ser/pdfs/` (magic-verified)
  + stubs `06–13-*.md` created.
- 2026-07-10 — Wave 1 deep-reads complete (vn-06…vn-10, 5/5 gate PASS) — 6-part EN
  sections in `docs/papers/vietnamese-ser/06…10-*.md`.
- 2026-07-10 — Wave 1 VI translations complete: `06…10-*.vi.md` (5 files, full-content,
  214–330 lines each).
- 2026-07-10 — Wave 2 deep-reads launched (vn-11, vn-12, vn-13, bimodal 12, bimodal 10).

## Remaining Action Items

**DONE — task complete 2026-07-12.** All milestones M1–M7 checked. Deliverables:
- 8 new VN/tone PDFs downloaded + stub entries (`vietnamese-ser/06–13`).
- **29 full-PDF deep-read analyses in English** (21 bimodal + 8 VN), each rescored
  against the current ViEmoSpeech profile (register V-A…V-H), all gate-PASS.
- **29 sibling Vietnamese translations** `NN-slug.vi.md` (full-content).
- Indexes + `project-overview.md` corrected; number-format normalized across all
  `.vi.md` (verified: zero metric-context decimal-commas, zero period-thousands
  counts, no arXiv/DOI/URL corrupted).
- Cross-cutting **final synthesis** (4 load-bearing conclusions) recorded above in
  Research Findings — the analytical payoff the old "compact entry + overlap score"
  stubs lacked.

Follow-ups for the human (not part of this task): fold the synthesis into the
method-paper related-work + the corpus-paper positioning table; the `V-A…V-H`
register here can seed a future `docs/spec` decision doc when training starts.
