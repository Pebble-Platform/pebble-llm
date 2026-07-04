# Paper 31 — Affective and Behavioural Computing: Lessons Learnt from the First Computational Paralinguistics Challenge

## 1. Bibliographic info

**Title:** Affective and behavioural computing: Lessons learnt from the First Computational Paralinguistics Challenge

**Authors:** Björn Schuller (Imperial College London / University of Augsburg / Université de Genève), Felix Weninger (TU München / Nuance), Yue Zhang (Imperial / TUM), Fabien Ringeval (Université Grenoble Alpes, CNRS, LIG / audEERING), Anton Batliner (Augsburg / FAU Erlangen-Nürnberg), Stefan Steidl (FAU Erlangen-Nürnberg), Florian Eyben (audEERING), Erik Marchi (audEERING / TUM), Alessandro Vinciarelli (University of Glasgow), Klaus R. Scherer (Swiss Center for Affective Sciences), Mohamed Chetouani (Sorbonne / UPMC), Marcello Mortillaro (Swiss Center for Affective Sciences).

**Year / venue:** *Computer Speech & Language*, 2019, vol. 53, pp. 156–180. Received 10 Dec 2016; revised 1 Oct 2017; accepted 19 Feb 2018; published 2019. DOI 10.1016/j.csl.2018.02.004. Open-access copy: archive-ouverte.unige.ch/unige:110103 (the local PDF is this UNIGE published version). This is a retrospective review/meta-analysis of the **INTERSPEECH 2013 ComParE** Challenge (the original challenge paper is Schuller et al., Interspeech 2013).

**Keywords (verbatim):** "Computational Paralinguistics; Social Signals; Conflict; Emotion; Autism; Survey; Challenge".

## 2. What this paper is and why it matters for Pebble

This is the foundational reference for **the ComParE 6373-feature acoustic set** — the standard hand-crafted feature vector that dominated speech-emotion / paralinguistics research for a decade and is still the default baseline (via openSMILE) for any "voice → affect/state" system. The paper reviews the first ComParE challenge (Interspeech 2013), which bundled four sub-challenges under one umbrella, one common feature set, one classifier recipe (linear SVM/SVR in WEKA), and one evaluation metric (unweighted average recall, UAR).

For the Pebble thesis, this paper is the **catalogue of which acoustic/prosodic cues distinguish paralinguistic states** in the *voice-message modality* — the channel a child-facing companion app would receive when a child sends a voice note instead of (or alongside) text. It is not about Pebble's NeoBERT text classifier; it is about the *complementary acoustic pipeline* and tells us (a) which low-level acoustic descriptors carry which affective/clinical signal, (b) how much a full 6373-dim feature set buys over a single best feature, and (c) how much classifier/fusion engineering buys over the feature set. Crucially, one of the four sub-challenges (Autism / CPSD) is on **children aged 6–18**, making this one of the rare paralinguistic benchmarks with a child population.

## 3. The four sub-challenges, corpora, and tasks

| Sub-challenge | Corpus | Size | Task(s) | Metric |
|---|---|---|---|---|
| **Social Signals** | SSPNet Vocalisation Corpus (SVC) | 2,763 clips × 11 s = 8.4 h; 120 subjects; 2,988 fillers + 1,158 laughter events | Frame-wise **detection + localisation** of laughter and filler (um/er/uh) | UAAUC (unweighted avg AUC of laughter+filler, per-frame, 100 fps) |
| **Conflict** | SSPNet Conflict Corpus (SC2) | 1,430 clips × 30 s = 11.9 h; 45 Swiss French political debates; 110 subjects | **Regression** (conflict score ∈ [−10,+10]) + **binary** high/low conflict | CC (Pearson) for Score; UAR for Class |
| **Emotion** | Geneva Multimodal Emotion Portrayals (GEMEP) | 1,260 instances = 8.9 h; 10 professional actors; enacted, nonsense phrases | **12-way** category; **binary** arousal; **binary** valence | UAR |
| **Autism** | Child Pathological Speech Database (CPSD) | 2,542 instances = 1 h; **99 children aged 6–18**; prompted sentence imitation | **Binary** Typicality (typical vs atypical); **4-way** Diagnosis (TYP/PDD/NOS/DYS) | UAR |

**CPSD diagnosis classes (DSM-IV):** TYP = 64 typically developing; PDD = pervasive developmental disorder / autism spectrum (12 children: 10M/2F); NOS = PDD-not-otherwise-specified (10: 9M/1F); DYS = specific language impairment / dysphasia (13: 10M/3F). 35 ASC-spectrum vs 64 TYP overall. Partition is speaker-independent, stratified by age and gender (Table 5: TYP 566/543/542; total train/dev/test = 903/307/337). **Recording-condition confound is explicit:** TYP and atypical children were recorded in different rooms, so spectral features partly index *room acoustics* rather than pathology (§3.4, §3.4.2; Bone et al. 2013) — directly relevant to any field voice deployment.

**GEMEP detail (Table 4):** 18 emotion categories, evaluation restricted to the **12 most frequent** (6 sparse categories ≤30 instances mapped to "other"); text-and-speaker-disjoint split is infeasible, so vowels + phrase #2 are train/dev and phrase #1 is test; **"masked" (hidden-emotion) regulation utterances appear only in the test set** — a deliberate train/test distribution shift to test robustness.

## 4. The ComParE 6373-feature set (the catalogue core)

**Headline:** 6,373 acoustic features ✔ (corroborated: Interspeech-2013 ComParE paper, isca-archive.org/interspeech_2013/schuller13_interspeech.pdf, "6,373 features"; query "ComParE 2013 6373 features 65 LLDs baseline UAR"). Built by applying statistical **functionals** to **65 low-level descriptors (LLDs)** ✔, extracted with **openSMILE**. Derived from the IS12 Speaker Trait set (then 6,125 attrs) with improved jitter/shimmer, greedy F0 peak detection, simplified functional rules.

**LLD families (Table 6 — the cue catalogue):**
- **4 energy-related** (prosodic): sum of auditory spectrum (loudness), RASTA-filtered auditory-spectrum sum, RMS energy, zero-crossing rate (ZCR).
- **55 spectral** (spectral + cepstral): RASTA auditory-spectrum bands 1–26 (0–8 kHz), **MFCC 1–14**, spectral energy 250–650 Hz & 1k–4 kHz, spectral roll-off (.25/.50/.75/.90), spectral flux/centroid/entropy/slope/harmonicity, psychoacoustic sharpness, spectral variance/skewness/kurtosis.
- **6 voicing-related** (prosodic + sound-quality): **F0** (SHS + Viterbi smoothing), probability of voicing, **log-HNR (harmonic-to-noise ratio)**, **jitter** (local, delta), **shimmer** (local).

**Functional arithmetic (§3.3):** Group A = 4 energy + 55 spectral = 59 LLDs; 54 functionals on LLDs + 46 on ΔLLDs → 59 × (54+46) = 5,900. Group B = 6 voicing LLDs; 39 functionals on LLD + 39 on Δ → 6 × (39+39) = 468. Plus 5 voiced-segment temporal statistics (mean/SD/min/max segment length + non-zero-F0 ratio). **Total 5,900 + 468 + 5 = 6,373** ✔ (Table 6/7, §3.3; reproducible from the PDF arithmetic).

**Frame-wise variant (Social Signals localisation):** smaller per-frame set — MFCC 1–12 + log-energy + Δ + ΔΔ, plus voicing-prob/HNR/F0/ZCR + Δ, each augmented by mean & SD over a 9-frame window (±4) → **47 × 3 = 141 descriptors/frame** (used by most Social-Signals participants as "ComParE (141)").

## 5. Baseline results (SVM/SVR, the headline numbers)

All baselines: linear SVM with Platt-scaled logistic posteriors; SMO; complexity C tuned on dev ∈ {1e-3,1e-2,1e-1,1}; multi-class via pairwise 1-vs-1; SVR for Conflict regression; **upsampling** for Autism (PDD/NOS/DYS ×5 for Diagnosis, ×2 for Typicality), **downsampling** to 5% garbage frames for Social Signals; WEKA; reproducible "recipe" shipped to participants. **Test = train+dev retrained.** (Table 8.)

| Task | Metric | Dev | **Test** | Chance | Status |
|---|---|---|---|---|---|
| Social Signals — Laughter AUC | AUC | 89.0 | 83.6 | 50.0±0.18 | ✔ |
| Social Signals — Filler AUC | AUC | 87.6 | 83.3 | 50.0±0.21 | ✔ |
| **Social Signals — UAAUC (official)** | UAAUC | 86.2 | **82.9 → 83.3** | 50.0±0.13 | ✔ |
| **Conflict — Score** | CC | 81.6 | **82.6** | −10.8±2.3 | ✔ |
| **Conflict — Class (official)** | UAR | 79.1 | **80.8** | 50.0 | ✔ |
| Emotion — Arousal | UAR | 82.4 | 77.9 | 50.0 | ✔ |
| Emotion — Valence | UAR | 75.0 | 61.6 | 50.0 | ✔ |
| **Emotion — Category (official, 12-way)** | UAR | 40.1 | **40.9** | 8.33 | ✔ |
| **Autism — Typicality** | UAR | 92.8 | **90.7** | 50.0 | ✔ |
| **Autism — Diagnosis (official, 4-way)** | UAR | 52.4 | **67.1** | 25.0 | ✔ |

> Note the UAAUC: Table 8 body shows 82.9 (test) but the abstract/§3.4 prose and the published Interspeech-2013 version report **83.3% UAAUC**; the small delta is between the dev-tuned and final retrained baseline. ✔ corroborated against the original challenge baselines (WebSearch: "ComParE 2013 baseline 83.3 UAAUC 80.8 conflict 40.9 emotion 67.1 autism"; researchgate/SLTC newsletter confirm 83.3 / 80.8 / 40.9 / 67.1).

**Headline patterns:**
- **Arousal ≫ valence from acoustics** — arousal 77.9 vs valence 61.6 UAR; a well-known, repeatedly confirmed asymmetry: *energy/pitch encode arousal robustly; valence is largely inaudible from acoustics alone*.
- **12-way enacted emotion is hard even in ideal conditions** — 40.9 UAR (chance 8.33); only sadness recalled clearly >50%, amusement 50.7%; pride 14.7% and elation 15.3% worst; confusions spread across categories, not along arousal/valence dimensions (Table 12). On realistic spontaneous data this drops further.
- **Autism Typicality looks great but is confounded** — 90.7 UAR, but driven partly by room acoustics; removing spectral features *raised* Typicality to 91.8 and removing static features (keeping only Δ) gave 89.2 (Table 9) — i.e., voice-quality/pitch/loudness features are **more robust to channel** than spectral ones.

## 6. The univariate logistic-regression meta-analysis (the single-cue ablation)

The paper's distinctive contribution is a **single-best-feature** logistic-regression baseline (Table 10), answering "how far does ONE acoustic cue get you, and which cue?" This is the actual cue catalogue Pebble wants.

| Task | Best single feature | Dir. | Test (single) | Test (full 6373 SVM) | Status |
|---|---|---|---|---|---|
| Conflict — Class | **Mean of positive log-HNR** (low HNR → high conflict; pressed/harsh voice) | low→conflict | 76.2 UAR | 80.8 | ✔ |
| Conflict — Score | (negated) Mean HNR | — | CC 64.6 | 82.6 | ✔ |
| Emotion — Arousal | **Q3 of 25% spectral roll-off** (more high-freq energy → higher arousal; F0-related, percentile-robust) | high→arousal | 71.0 UAR | 77.9 | ✔ |
| Emotion — Valence | Skewness of MFCC 1 (hard to interpret) | — | 57.2 UAR | 61.6 | ✔ |
| Emotion — Category | pairwise coupling | — | 29.9 UAR | 40.9 | ✔ |
| Autism — Typicality | **Flatness of RMS energy** (low flatness = "spiky" energy = impaired speech regulation) | low→atypical | 82.2 UAR | 90.7 | ✔ |
| Autism — DYS vs NOS | IQR 1–3 of ZCR (low for NOS) | — | 70.4 UAR | — | ✔ |
| Autism — NOS vs PDD | Mean dist. of loudness-change peaks (higher for PDD/autism) | high→PDD | 66.3 UAR | — | ✔ |
| Autism — {DYS,NOS,PDD} vs TYP | Flatness of RMS energy | — | 76.6–89.8 UAR | — | ✔ |
| Autism — Diagnosis (4-way) | pairwise coupling of above | — | 49.0 UAR | 67.1 | ✔ |

**The single-cue → full-set gap is the feature-richness lesson:** a *single well-chosen prosodic feature* reaches 76–82% UAR on binary conflict/typicality, but the full 6373-dim set adds another ~4–9 points (Conflict 76.2→80.8; Typicality 82.2→90.7) and is essential for the fine 4-way Diagnosis (49.0→67.1). The authors predict the best-to-n-best curve is "rather flat" and that a robust SVM over the full redundant vector will not get a "real boost" from feature selection — i.e., **throw the whole feature set at a robust classifier rather than hand-select.**

## 7. Feature-set vs classifier gains (participants + fusion)

65 groups registered, 19 papers accepted. Best per sub-challenge on test (Table 11):
- **Social Signals:** Gupta et al. **91.5 UAAUC** (DNN + probabilistic time-series smoothing/masking on ComParE-141) — **+6.1 abs over the 83.3 baseline**, the single biggest gain, from a *segmentation/smoothing* method (ASR-style), not a new feature. Best-2 majority vote 92.7.
- **Conflict:** Grézes et al. **83.1 UAR** by reducing conflict to a *speech-overlap-ratio* mid-level feature (SVR+SVM). Best-3 vote 85.9.
- **Emotion:** AdaBoost (Gosztolya) 42.3; ensembles ~41–42; best 12-system fusion **46.1** UAR. Modest gains — the task is acoustically hard.
- **Autism:** Asgari et al. **69.4 UAR** (SVM on voice-quality/energy/spectrum/cepstrum + harmonic model of voiced speech) — barely above the 67.1 baseline; fusion did not beat it.

**Lesson:** where the task is **detection/segmentation** (Social Signals) or **structurally exploitable** (Conflict = overlap), method/feature engineering beat the generic feature set substantially. Where the task is **intrinsic affect classification** (Emotion category, Autism diagnosis), neither the 6373-set nor fancy classifiers moved much — the ceiling is in the *signal*, not the model. **Significance floors** (Fig. 4, §3.5.5): to beat the baseline at α=.05 you needed +4.4 abs (Conflict), +5.5 (Emotion), +3.8 (Autism) — calibrating "is this gain real?"

## 8. Parts directly useful for Pebble (tagged by Decision ID)

> These decision IDs (D-A…D-H) are the Pebble *text-classifier* register. This paper is a **voice-modality** paper; its transfer is mostly to the (future) **voice-message acoustic pipeline** that would run *alongside* NeoBERT, plus a few text-side analogues. Each point states transfer risk explicitly.

1. **The 65-LLD cue catalogue + openSMILE 6373 set as the off-the-shelf voice front-end** → moves **D-H (datasets / substitutes)** for the voice modality. Concrete artifact: a `voice/features.py` that calls openSMILE with the `ComParE_2016` config to emit the 6373 vector per voice-note. *Transfer risk: MEDIUM.* The catalogue is modality-correct (it IS the voice channel) and one corpus is children, but every number here is on enacted/adult or clinically-recorded child speech; a child's phone voice-note in the wild is noisier and spontaneous. Use the feature set, not the absolute numbers, as the starting point.

2. **Arousal-from-acoustics is robust (77.9 UAR), valence is not (61.6)** → informs **D-D (severity/energy regression source & metric)** and the heuristic **`energy`** head. Concrete artifact: Pebble's v1 `energy` is heuristic; if a voice-note arrives, derive an arousal proxy from **Q3 spectral roll-off + loudness + F0** (the paper's best arousal cues) rather than trying to read valence acoustically — leave valence/emotion to the text head. *Transfer risk: LOW for arousal-as-energy* (this asymmetry is one of the most replicated findings in speech affect); HIGH if anyone tries to read fine emotion from voice acoustics alone.

3. **Single best prosodic cue gets 76–82% UAR on binary states; full set adds ~4–9 pts** → informs **D-D** and **D-B (loss balancing / feature richness tradeoff)**. Concrete artifact: a cheap, auditable `voice/cue_rules.py` of single-feature tripwires (low HNR → tension/conflict; spiky RMS-energy flatness → dysregulated speech; high loudness-peak distance → atypicality) as an interpretable *first layer* under any learned voice head — the FAIIR-style "dumb-but-auditable rule first" pattern, here grounded in measured single-cue UARs. *Transfer risk: MEDIUM* — directions (low HNR↔tension) are physiologically grounded and likely to hold, but the 0.5 decision thresholds were fit on these specific corpora and must be re-tuned.

4. **UAR (unweighted average recall) as the metric under class imbalance + upsampling rare classes ×5** → moves **D-C (severity label scheme + loss)** and **D-B**. Concrete artifact: report **UAR / macro-recall** (not accuracy) on Pebble's imbalanced `emotion` (12-label) and `severity` heads, and replicate the ComParE upsampling-of-minority recipe (×5 PDD/NOS/DYS) as a baseline against Kendall/GradNorm/focal. The paper explicitly chose UAR "because it is also meaningful for highly unbalanced distributions" and found simple ×5 upsampling ≈ SMOTE for their tasks. *Transfer risk: LOW* — metric choice and minority-upsampling transfer cleanly to any imbalanced classifier including text.

5. **Channel-robust feature selection: drop spectral, keep voice-quality/pitch/loudness** (Typicality 90.7→91.8 when spectral removed; Table 9) → informs **D-H** and a voice-modality calibration anchor. Concrete artifact: for any field child-voice deployment, prefer **prosodic/voice-quality** features (jitter/shimmer/HNR/F0/loudness, robust to reverb) over raw spectral/MFCC features that index recording environment. *Transfer risk: LOW-MEDIUM* — the room-confound lesson is general; the exact +1.1 gain is corpus-specific.

6. **The train/test distribution-shift design (masked emotion / unseen rooms only in test)** → informs **D-G (threshold / calibration policy)** and the eval-split construction. Concrete artifact: build Pebble's held-out voice/severity test to *deliberately include* the hardest, out-of-train conditions (masked/indirect affect, unseen recording conditions) so reported numbers are not optimistic. *Transfer risk: LOW* — it is a methodological pattern, modality-agnostic.

## 9. How each part helps Pebble succeed (concrete actions)

- **Voice front-end (point 1) → `voice/features.py`.** When Pebble ingests a voice-note, run openSMILE ComParE to a 6373-vector, optionally project to the 141-frame set for any localisation (e.g., detecting laughter/fillers as engagement/`receptivity` cues). This is the published, reproducible recipe; do not reinvent acoustic features.
- **Arousal proxy (point 2) → `energy` head.** Replace/augment the v1 heuristic `energy` with a 3-feature arousal regressor (roll-off Q3, loudness, F0). Calibrate Pearson correlation as the metric (matching the paper's CC convention and Pebble D-D). Do **not** attempt acoustic valence; route valence/emotion to NeoBERT text.
- **Cue tripwires (point 3) → `voice/cue_rules.py`.** Ship the single-feature rules as an interpretable safety/triage backstop (low HNR → tension flag; spiky energy → dysregulation flag), each with a documented direction-of-effect from Table 10, beneath the learned head — clinician-readable, recall-first.
- **Metric + imbalance (point 4) → training config.** Set UAR/macro-recall as a primary reporting metric for `emotion`/`severity`; add ×5 minority upsampling as the D-B baseline arm; the paper is the citation that "simple upsampling ≈ SMOTE."
- **Channel robustness (point 5) → calibration slice.** Tag features by robustness; when child voice-notes vary by device/room, lean on prosodic features and report a channel-stratified slice.
- **Hard-test design (point 6) → eval split.** Curate Pebble's voice/severity test to over-represent masked/indirect distress and unseen conditions, mirroring GEMEP's masked-only-in-test design.

## 10. Child mental-health lens — transfer validity, risks, ethics

- **Rare child-voice benchmark, but clinical not companion-app.** CPSD is **99 children aged 6–18**, prompted sentence imitation, recorded in hospitals/schools — directly child-modality (a genuine asset; almost no other paralinguistics benchmark has children), but it is *clinical, prompted, diagnostic* speech, not spontaneous self-disclosure to a companion app. The Typicality/Diagnosis tasks are ASC/language-impairment classification, **not** distress or mental-health-state detection. So the *cues* (HNR↔tension, RMS-flatness↔dysregulation, loudness-peak-distance↔atypicality) transfer as a hypothesis catalogue; the *task labels* do not map to Pebble's emotion/severity/safety targets.
- **Arousal-yes / valence-no is the load-bearing child-voice lesson.** A child's voice-note reliably signals *activation* (agitation, energy) but not *good-vs-bad*. Pebble must therefore treat voice as an **arousal/energy and engagement** channel and keep semantic/valence judgment in text — a clean separation that prevents over-reading a child's tone.
- **Recording-condition confound is an ethics-and-validity trap.** The paper's own finding — that "atypical" classification was partly driven by which *room* a child was recorded in — is a stark warning: a voice model can learn the child's *device/home acoustics* as a proxy for their *state* or *demographic*. For a child-facing product this is both a fairness risk (poorer-quality phones → systematic bias) and a privacy risk. Mitigation: prefer channel-robust prosodic features, report device-stratified performance, never let a raw spectral voice model gate a safety decision.
- **Acoustic affect is hard even in ideal lab conditions** — 40.9 UAR on 12-way *enacted* emotion. The authors stress performance "considerably deteriorates" on realistic spontaneous data. For Pebble this caps expectations: voice acoustics are a *weak, supporting* signal for fine emotion in children, not a primary classifier. The safety architecture must never depend on acoustic emotion recognition.
- **Ethics of voice in a child product.** Voice is biometric and identifying. The paper's clinical corpora were consented and IRB-adjacent (university child-psychiatry departments); a companion app collecting child voice-notes needs explicit guardian consent, on-device or ephemeral feature extraction (store the 6373-vector, not the audio), and an option to disable voice entirely.

## 11. Limitations & open questions for Pebble (incl. contradiction/gap)

- **Enacted, not spontaneous; prompted, not free.** GEMEP is professional actors; CPSD is sentence imitation. Pebble's children speak spontaneously, briefly, emotionally, on phone mics. Every number here is an *upper bound under clean/controlled conditions*; the paper itself says spontaneous data is worse. The 6373-set and cue directions transfer; the UARs do not.
- **No deep-learning end-to-end speech model.** This is a 2013-era SVM-over-hand-crafted-features world. Modern voice-affect would use wav2vec2/HuBERT embeddings. Pebble should treat ComParE-6373 as the *interpretable, cheap baseline* and benchmark a self-supervised audio encoder against it — the paper provides the baseline, not the state of the art.
- **Contradiction/gap vs Pebble's plan and vs FAIIR (Paper 01):** Pebble v1 derives **`energy`, `socialIsolation`, `receptivity`, `safetyFlag` heuristically and trains only `emotion` + `severity` from text** — i.e., v1 has **no voice channel at all**. This paper is the evidence that the *single most learnable thing from voice* is exactly **arousal/energy** (77.9 UAR, robust, single-cue 71.0), the dimension Pebble currently leaves heuristic. So there is a concrete tension: the cue Pebble heuristically guesses (`energy`) is the one a cheap openSMILE+logistic head could measure directly from a voice-note with published reliability. Conversely, FAIIR (Paper 01) and the whole text-classifier register assume **text-only, conversation/turn-level** input and never touch the voice modality — this paper is the reminder that a child-facing app receives *audio*, a channel the text pipeline structurally cannot see, and that the recording-condition confound (room→label leakage) is a failure mode text classifiers never face but a voice head must defend against.
- **Valence inaudibility is a hard ceiling, not a tuning problem.** If a Pebble reviewer asks "why not read emotion from voice?", this paper (61.6 valence UAR, dropping further on spontaneous data) is the citation that acoustic valence is fundamentally weak — the answer is architectural (text for valence, voice for arousal), not "train harder."
- **Open question worth pursuing:** does the HNR↔tension / RMS-flatness↔dysregulation cue catalogue hold on *spontaneous child voice-notes*? No paper in Pebble's set tests this. A small child-voice pilot computing these single cues against text-derived distress labels would be a genuine, publishable contribution and would directly de-risk a v2 voice head.

## Deep research — full-PDF read (2026-06-16)

### Source-access note

Read in full from the local published version `docs/papers/pdfs/31-compare-csl2019.pdf` (UNIGE archive-ouverte copy of the *Computer Speech & Language* 2019 article, DOI 10.1016/j.csl.2018.02.004), extracted with `pdftotext` (Read tool cannot render PDFs). Every table (1–13) and section (§1–§5) was read. Load-bearing numbers were cross-checked against the original **Interspeech-2013 ComParE** challenge paper and secondary summaries:
- **Feature count 6373 / 65 LLDs / 141 frame-features** — WebFetch of `isca-archive.org/interspeech_2013/schuller13_interspeech.pdf` ("6,373 features", "65 low-level descriptors") ✔; also reproducible from the §3.3 arithmetic in the local PDF (5,900 + 468 + 5).
- **Baselines 83.3 UAAUC / 80.8 Conflict UAR / 40.9 Emotion UAR / 67.1 Autism Diagnosis UAR** — WebSearch "ComParE 2013 6373 features baseline UAR social signals conflict emotion autism Schuller"; corroborated by the SLTC Newsletter Nov-2013 review and ResearchGate copies of both the 2013 challenge paper and this 2019 review ✔.
- Conflict-paper-vs-review note: the original Interspeech-2013 preliminary baseline reported a slightly different Conflict-Class UAR (≈0.565 in one early table) vs the **final 80.8%** in this CSL 2019 review's Table 8; the published review version (authoritative) uses the retrained train+dev baselines reported above.

### What the paper actually does

A review/meta-analysis of Interspeech-2013 ComParE: defines four sub-challenges (Social Signals/SVC, Conflict/SC2, Emotion/GEMEP, Autism/CPSD; §3.1, Tables 2–5), introduces the **6373-feature ComParE acoustic set** (65 LLDs × functionals; §3.3, Tables 6–7), computes **linear-SVM/SVR baselines** (Table 8: UAAUC 83.3 / Conflict UAR 80.8 & CC 82.6 / Emotion arousal 77.9, valence 61.6, category 40.9 / Autism typicality 90.7, diagnosis 67.1), adds a **univariate single-feature logistic-regression analysis** identifying the single best cue per task (Table 10: HNR for conflict, spectral roll-off Q3 for arousal, RMS-energy flatness for typicality), and reviews **65 registered / 19 accepted participant systems** (Table 11; best gains: Social Signals 91.5 UAAUC via DNN+smoothing = +6.1; Conflict 83.1 via overlap-ratio; Emotion fusion 46.1; Autism 69.4). It quantifies feature-set vs single-cue vs classifier/fusion gains and the channel-robustness of prosodic vs spectral features (Table 9).

### Parts directly useful for Pebble

See §8 above (six points, each tagged D-x with transfer risk). In brief: (1) openSMILE 6373 cue catalogue as the voice front-end [D-H]; (2) arousal-robust/valence-weak asymmetry for the `energy` head [D-D]; (3) single-cue tripwires (HNR/RMS-flatness/loudness-peaks) as auditable first layer [D-D, D-B]; (4) UAR metric + ×5 minority upsampling under imbalance [D-C, D-B]; (5) channel-robust prosodic-over-spectral selection [D-H]; (6) hard-test distribution-shift design [D-G].

### How each part helps Pebble succeed

See §9 above — concrete per-artifact actions: `voice/features.py` (openSMILE), `energy` arousal regressor (roll-off Q3 + loudness + F0, Pearson metric), `voice/cue_rules.py` interpretable tripwires, UAR + upsampling training arm, channel-stratified calibration slice, masked/unseen-condition eval split.

### Child mental-health lens

See §10. Key points: CPSD gives a rare child-voice benchmark (99 children, 6–18) but it is clinical/prompted ASC classification, not companion-app distress; the load-bearing transferable lesson is **arousal-yes / valence-no** (voice → energy/arousal, text → valence/emotion); the **recording-condition confound** (room→label leakage) is a fairness+privacy trap for a child product; acoustic affect is weak even in ideal labs (40.9 UAR enacted, worse spontaneous), so voice must remain a supporting, never safety-gating, channel; voice is biometric → guardian consent, store features not audio, allow opt-out.

### Limitations & open questions for Pebble

See §11. The explicit **contradiction/gap**: Pebble v1 leaves `energy` heuristic and has **no voice channel**, yet this paper shows arousal/energy is exactly the cheapest, most reliable thing learnable from a voice-note (77.9 UAR; single-cue 71.0) — the dimension Pebble guesses is the one openSMILE could measure. And against FAIIR/the text-classifier register (text-only, turn-level): a child-facing app receives *audio*, a channel the NeoBERT pipeline structurally cannot see, carrying a unique failure mode (room→label confound) text never faces. Acoustic valence (61.6 UAR, worsening) is a hard ceiling, justifying the architectural split rather than "train harder." Open question: do the HNR/RMS-flatness cues hold on spontaneous child voice-notes — untested by any paper in the set, and a clean v2 de-risking pilot.
