# Paper 15 — Charting 15 Years of Progress in Deep Learning for SER: A Replication Study

- **Authors:** Andreas Triantafyllopoulos, Anton Batliner, Björn W. Schuller
- **Venue / year:** arXiv 2025 (code: github.com/CHI-TUM/ser-progress-replication)
- **Links:** abs https://arxiv.org/abs/2508.02448 · PDF `pdfs/15-ser-15years-replication.pdf`
- **Group:** survey / benchmark (reproducibility)

**Summary:** Replication study tiến bộ SER từ Interspeech 2009 Challenge, cả audio- và text-based; kết luận diminishing returns hậu-transformer và "progress" phụ thuộc cách so sánh.

**Relevance to Pebble:** Caution phương pháp luận cho mọi benchmarking claim — cùng tinh thần gold-holdout / honest-metric của repo.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Profile assembled at analysis time** (from `docs/intent/constraints.md` + `docs/spec/capabilities/voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`):
Pebble's primary program is **ordinal suicide-risk *text* classification** asking whether LLM weak labels *honestly* augment a scarce clinical gold set — bound by **gold-holdout** (train on weak/LLM labels, eval on disjoint held-out CSSRS gold), subject-level splits, **reproducible-by-construction** (pinned stack + seed + multi-fold with reported std/CIs), and ordinal-aware metrics (QWK/MAE). The adjacent **voice** stream is a frozen WavLM/emotion2vec backbone with 3 heterogeneous MTL heads (emotion CE + affect V/A **CCC** + **crisis under a hard recall floor**), balanced by Kendall uncertainty weighting; MSP-Podcast (A/V/D) + DAIC (crisis) are the named "real-label" swap targets.

### Analysis — 15 Years of SER Progress (replication)
- **Overlap:** 23% (peripheral) — D1=1, D2=0, D3=1, D4=0, D5=0, D6=0, D7=2
  - (Σwᵢ·scoreᵢ = 3·1 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·2 = 6; 6/26 × 100 = 23%)
- **Closest on:** D7 (backbone match — the study directly benchmarks *both* of Pebble's active backbones: BERT/RoBERTa/DistilBERT/Electra text encoders and wav2vec2/HuBERT SSL speech encoders) and D1 partial (it models categorical emotion *and* continuous valence/arousal/dominance, though as separate models, not joint heterogeneous heads; no safety head).
- **Best point (Framing / citation):** The paper empirically shows that "progress" claims are *conditioned on the arbitrary set of models/hyperparameters compared* — bigger/newer models are not monotonically better, single-run rankings are unstable under huge hyperparameter variance, and only bootstrap 95% CIs on the progress measures keep the story honest.
  - **How to apply to Pebble:** Cite it in the paper's evaluation-protocol / related-work section as external precedent that a headline number without CIs and without a fixed comparison set misrepresents progress — reinforcing Pebble's "multi-fold + reported std/CI, never a single-run point estimate" rule and the gold-holdout honesty thesis (an SER-domain analogue to the within-LLM 0.67 vs honest-gold 0.385 gap).
- **Caveats:** Full main body (pp. 1–11) read; not paywalled. Appendices A/B/D/E (full model list, noise-robustness detail, linguistic-content analysis) skimmed only — does not affect the scored dimensions, which come from the main body. Overlap is low by construction: no mental-health/crisis domain (D2=0), no teacher-LLM distillation (D4=0), no MTL loss balancing (D5=0), no safety/recall-floor objective (D6=0). The value is methodological (honest-eval framing) + backbone/corpus adjacency (MSP-Podcast/IEMOCAP/EmoDB are exactly the voice stream's real-label swap targets), not architectural transfer.

## Deep research — full-PDF read (2026-07-10)

> Read against the current ViEmoSpeech profile + Decision Register V-A…V-H
> (`docs/tasks/paper-deep-analysis.md`), NOT the archived text-stream profile above.
> This paper is ViEmoSpeech's strongest **methodological ally** on honest evaluation
> (V-G), with load-bearing corroboration for V-B (SSL-vs-handcrafted honesty) and V-H
> (benchmark hygiene). The "Child mental-health lens" sub-part is reframed as a
> transfer-validity/ethics lens for ViEmoSpeech (VN acted TV-drama SER, not clinical).

### Source-access note

- **Local PDF read in full** via `pdftotext "docs/papers/bimodal-ser/pdfs/15-ser-15years-replication.pdf" -`
  (main body §§I–VII pp. 1–11 + Tables I–VIII + Figs 1–4; reference list; appendices A/B/D/E
  are figure/list detail that does not change the numbers below). Local file is
  **arXiv:2508.02448v1 [cs.SD], 4 Aug 2025**, watermarked "Under review".
- **Published/venue version:** WebSearch resolved this to **IEEE Transactions on Affective
  Computing, Early Access, April 2026** (MCML publication record `tbs+25`). No numeric
  conflicts were found between the preprint and the venue metadata; the arXiv HTML mirror
  (`arxiv.org/html/2508.02448`) reproduces every table value cited here verbatim, so the v1
  numbers are treated as authoritative. Search query: *"Charting 15 years progress deep
  learning speech emotion recognition replication study Triantafyllopoulos Batliner Schuller
  MSP-Podcast UAR"* → https://mcml.ai/publications/tbs+25/ and https://arxiv.org/abs/2508.02448.
- **Web-validated numbers** (query above, resolved to https://arxiv.org/html/2508.02448):
  MSP-Podcast tuning UAR .650 [.642–.658]; OOD EmoDB .806 / IEMOCAP .617; IID↔OOD Spearman
  .909 / .843; year/MACs/params correlations all near-zero; clean↔noisy Spearman .953 and
  .609→.546 degradation; best text UAR (Llama-2) .564; FAU-AIBO2/5 baseline/winner/fusion
  .677/.703/.712 and .382/.417/.440; Gini .329; FAU-AIBO = German children's speech,
  school-disjoint (Mont test / Ohm train). All ✔ corroborated against the HTML mirror.

### What the paper actually does

**Design.** A large-scale replication that quantifies "15 years of SER progress" from the 2009
INTERSPEECH Emotion Challenge to 2024, under a **fixed compute budget and fixed hyperparameters**
("bitter lesson" framing, §II-A). Two datasets: **FAU-AIBO** (the 2009 challenge set — German
*children's* speech, Wizard-of-Oz, 18,216 chunks, mapped to a 2-class NEG/IDL and a 5-class
A/E/N/P/R task, heavily imbalanced toward neutral; **school-disjoint** train Ohm / test Mont)
and **MSP-Podcast-v1.11** (naturalistic; 44,586 train / 11,947 dev / 20,845 test; official
**speaker-independent** partitions; 4-class categorical task used here). §III-A.

**Models.** 43 audio models spanning the whole timeline — openSMILE IS09–IS16 + eGeMAPS
functionals into MLP/LSTM, ImageNet CNNs (AlexNet/VGG/ResNet50/ConvNeXt/EfficientNet/Swin),
AudioSet CNN14, CRNN, x-vector ETDNN, AST, and SSL transformers (wav2vec2-base/large + variants,
HuBERT-base/large, Whisper-s/b/t encoders) — plus 7 text models on transcripts (BERT, RoBERTa,
DistilBERT, Electra; Llama-2, Llama-3, Mistral via 4-bit LoRA). Exploration phase: Adam, lr 1e-4,
30 epochs, batch 4, weighted cross-entropy; tuning phase grid-searches optimiser/lr/batch for the
top-5 per task. §III-B. **Metric: UAR (unweighted average recall = macro-recall)** "the standard
metric for SER since the 2009 challenge which accounts for class imbalance." §III-C.

**Headline results (all ✔ corroborated).**
- *Do newer/bigger models win?* **No, not monotonically.** Spearman ρ between UAR and year of
  publication is .122/.093/.050 (FAU2/FAU5/MSP), against MACs .151/.230/.095, against #params
  −.083/.085/.026 — all with 95% bootstrap CIs spanning negative to positive (e.g. MACs on
  FAU5 = .230 [−.087, .512]). Table II. "The large variance… does not allow for robust
  conclusions." ✔
- *Best absolutes.* Exploration: FAU2 CNN14 .692, FAU5 ResNet50 .428, MSP w2v2-L-12-avd .609
  (HuBERT-L .570). Table I. Tuning lifted MSP to **.650 [.642–.658]** for w2v2-L-12-avd
  (released as `w2v2-L-12-emo`). Table IV. ✔ On FAU-AIBO the best tuned models stayed *close to
  or below* the 2009 **baseline .677/.382, winners .703/.417, and fusion .712/.440** (Table III)
  — i.e. 15 years of DL did **not** clearly beat the 2009 challenge on its own data. ✔
- *Hyperparameter variance is the dominant effect.* Fig. 2 shows huge UAR spread across
  hyperparameters for the same architecture; "a different choice of hyperparameters… could have
  resulted in… a different ranking across architectures." Conclusions about progress are
  **"pre-conditioned on the particular set of models that are evaluated"** (§V). ✔
- *OOD generalisation is honest and IID-predictable.* Models trained on MSP transfer to
  **EmoDB UAR .806** and **IEMOCAP .617** (w2v2-L-12-avd best on both), and **IID↔OOD Spearman
  is .909 (EmoDB) / .843 (IEMOCAP)** — picking the best model by IID selects the best OOD model
  too. Table V. Year/MACs/params vs OOD remained near-zero (.112/.166/.172 EmoDB). ✔
- *Robustness.* Clean↔noisy (0 dB additive urban noise) UAR Spearman **.953**, but robustness is
  uncorrelated with year (.05)/MACs (.10)/params (.03); even the best model drops **.609→.546**.
  §IV-A5. ✔
- *Text branch.* Best text UAR: MSP Llama-2 **.564** (≈ Llama-3 .563 / Mistral .560; Table VIII),
  which "would rank third in our exploration phase, trailing marginally behind HuBERT-L (.570)"
  — text alone is competitive on naturalistic speech but below the best audio; on FAU-AIBO text
  is weaker (limited Wizard-of-Oz linguistic content). Whisper's valence edge is attributed to
  *implicit linguistic content*, not new paralinguistics (§IV-A1, citing ref [12]). ✔
- *Complementarity.* Audio models agree more with each other (w2v2/CNN14 .815 on FAU2) than with
  text (w2v2/DistilBERT .666); the *most complementary* pair is a non-transformer CNN
  (EfficientNet) + LLM text (Llama-2), because transformer SSL "already captured linguistics
  implicitly." §IV-B1, Fig. 4. ✔
- *Probing (Table VI).* Better-SER models encode acoustic features more strongly, but **all
  transformers are far better at mean pitch (μ(P) up to .959) than at pitch variability
  (σ(P) ≈ .237) and jitter** — pitch *dynamics* are under-encoded. ✔
- *Individual fairness (Table VII).* Speaker-level **Gini .329** on MSP (moderate inequality);
  higher-UAR models are *more* fair on MSP (ρ = −.344) but newer/bigger models are *less* fair on
  FAU-AIBO (ρ up to .55 vs params) — fairness does not come free with scale. ✔
- *Models ≠ humans.* Model difficulty correlates only weakly with human annotator disagreement
  (ρ .33/.20), and higher human-agreement did **not** yield higher UAR (ρ −.38/−.07). §IV-A.

### Parts directly useful for ViEmoSpeech (tagged with Decision IDs)

1. **UAR = macro-recall as *the* imbalance metric, plus 95% bootstrap CIs on every headline and
   on every "progress" correlation (Tables II–IV).** `[V-G]` This is the exact instrument ADR-002
   needs: report per-class recall averaged (UAR), never plain accuracy, and attach bootstrap CIs
   so a single-run point can't masquerade as a ranking. **Transfer risk: none** — pure method,
   register-independent.
2. **Speaker-independent / group-disjoint splits as the non-negotiable baseline** — FAU-AIBO is
   *school-disjoint* (Mont/Ohm), MSP uses *official speaker-independent* partitions. `[V-G]`
   Direct external precedent for ViEmoSpeech's speaker-disjoint + whole-series holdout; the two
   most-cited SER corpora (IEMOCAP/EmoDB) are criticised precisely for *lacking* an established
   speaker-independent scheme (§II). **Transfer risk: none** — this is exactly our regime.
3. **IID→OOD selection validity: Spearman .909/.843 (Table V).** `[V-G]` Justifies our two-tier
   eval — tune/select on the speaker-disjoint dev split, then confirm on the whole-series OOD
   holdout (ADR-002). **Transfer risk: low** — their OOD sets are *acted* (EmoDB/IEMOCAP) and thus
   "easier"; our whole-series holdout is same-genre TV drama, so the ρ≈.9 IID→OOD stability is a
   reasonable-but-unproven expectation for us, to be measured not assumed.
4. **"Progress is conditioned on the model set + hyperparameters compared" + huge HP variance
   (Fig. 2, §V).** `[V-B]` `[V-G]` Every backbone leaderboard row we cite (WavLM vs emotion2vec
   vs Whisper) must carry the hyperparameter budget and a CI, and be framed as *conditional*.
   **Transfer risk: none** — the confound is architectural, not domain-specific.
5. **SSL/size does NOT monotonically beat handcrafted (Table I/II): year/MACs/params ≈ 0
   correlation with UAR; on FAU-AIBO the best tuned DL stays at/below the 2009 fusion .712/.440.**
   `[V-B]` The single winner (w2v2-L-12-avd, .650 MSP / .806 EmoDB OOD) won because it was
   **domain-adapted** (pre-trained on MSP-Podcast dimensional SER first), not because it was
   bigger — a mandate to prefer a **PhoWhisper/VN-adapted encoder init** (vn-06) over raw model
   size, and to keep an openSMILE/eGeMAPS handcrafted arm honestly in the V-B ladder.
   **Transfer risk: low** — WavLM/emotion2vec (our actual candidates) were *not* in their 43, so
   the specific ranking doesn't transfer; the *domain-adapted-beats-bigger* principle does.
6. **Probing gap: transformers under-encode pitch variability and jitter (Table VI: σ(P) .237
   vs μ(P) .959).** `[V-B]` `[V-D]` The F0-*dynamics* channel — exactly where Vietnamese lexical
   tone lives (contour + phonation, vn-06/vn-13) — is the SSL blind spot. Concrete corroboration
   for adding an explicit handcrafted phonation/pitch-dynamics vector (jitter/shimmer/HNR/H1-H2/
   σ(F0)) alongside the SSL backbone. **Transfer risk: medium-favourable** — measured on German
   EmoDB, not VN; if anything the gap should be *larger* on tone-loaded VN F0, which is itself
   our research opening.
7. **Dataset-hygiene warnings (§I–II): FAU-AIBO "quietly abandoned"; MSP-Podcast re-released
   ~yearly with size + label changes → cross-paper numbers not comparable; they pin v1.11.**
   `[V-H]` Mandates ViEmoSpeech pin a frozen corpus version/hash per reported number
   (provenance invariant). **Transfer risk: none** — the versioning failure mode is universal.
8. **Speaker-level Gini fairness (Eq. 1, Table VII).** `[V-G]` A ready-made per-speaker
   utility/Gini report to add next to macro-F1 — exposes whether a few actors carry the score
   (a real risk in a 2-series, actor-heavy drama corpus). **Transfer risk: low** — directly
   applicable, and more acute for us given small actor pools.

### How each part helps ViEmoSpeech succeed

- **Eval protocol (1,2,3,8) → ADR-002 eval spec.** Adopt UAR/macro-recall + bootstrap-CI as the
  reporting default in `docs/spec/capabilities/extraction-pipeline.md` and the method-paper eval
  table; add a per-speaker Gini row. Concretely: our baselines table (vn-08 86.6, vn-10 0.87,
  THAI-SER WA~60, MSP CCC) should print CIs and macro-recall, and flag the speaker-leaky VN rows
  — this paper is the citation that makes that flagging *methodologically standard*, not partisan.
- **Two-tier holdout (3) → whole-series OOD gate.** Treat the held-out whole series exactly as
  this paper treats EmoDB/IEMOCAP: select on the speaker-disjoint dev, report the series holdout
  as OOD, and *expect* (per ρ≈.9) the ranking to hold — a divergence is then a real red flag
  worth reporting, not noise.
- **HP-conditioned framing (4) → V-B/V-A ablation discipline.** When we claim "WavLM ≥ X" or
  "learned fusion > rule fusion", run ≥3 hyperparameter settings per arm and report the range;
  cite this paper that architectural gains are routinely confounded by tuning.
- **Domain-adapted init (5) → audio backbone choice.** Prioritise a VN-/PhoWhisper-adapted or
  emotion-warm-started SSL checkpoint over a bigger cold one; keep an eGeMAPS-functionals-into-MLP
  arm in the ladder as the "2009-era" honest floor — the paper shows that floor is not far below
  SSL on imbalanced data.
- **Probing gap (6) → the tone×emotion measurement + phonation features.** This is the most
  novelty-relevant finding: run the paper's eGeMAPS linear-probe on *our* encoder layers, expect
  σ(F0)/jitter to probe poorly, and use that as the direct argument for the handcrafted phonation
  branch and for framing tone×emotion as an F0-*dynamics* channel competition (V-D headline).
- **Version-pinning (7) → provenance invariant.** Every ViEmoSpeech release number carries the
  corpus snapshot ID (already an I-series invariant); this paper is the external cautionary tale
  (MSP-Podcast versioning) that makes it a *comparability* requirement, not just bookkeeping.

### Transfer-validity / ethics lens (ViEmoSpeech)

- **The child-speech angle is real but indirect.** FAU-AIBO is *German children's* speech, so the
  paper's child-register warnings (Wizard-of-Oz → limited linguistic content → text branch weak;
  heavy neutral-class imbalance) are a genuine caution for any child-facing use — but ViEmoSpeech
  is **adult/actor VN TV-drama**, so transfer is by analogy, not population match. The transferable
  lesson is register-dependence of the text branch, already central to our cross-cutting synthesis.
- **Honest-eval brand transfers cleanly.** Everything in V-G (macro-recall, speaker-disjoint,
  bootstrap CIs, OOD confirmation, Gini fairness) is method, not domain — it transfers to VN acted
  drama without caveat. This is the paper's core value to us.
- **Metric-scale caution.** Their categorical UAR is not the same object as our V/A **CCC** or our
  distress **recall-floor**; import the *discipline* (CIs, disjoint splits, ranges) but not the
  metric — CCC needs its own bootstrap-CI treatment, and the recall-floor needs a fixed-recall/
  float-precision report, not UAR.
- **Acted-data honesty.** The paper repeatedly flags that EmoDB/IEMOCAP/RAVDESS/CREMA-D are
  *acted and prototypical*, which is why OOD UAR (.806) is *higher* than naturalistic IID (.650) —
  "the datasets being much easier." Direct support for our V-F acted-drama-proxy framing: acted
  emotion inflates numbers, so a high ViEmoSpeech score must be read against that ease, and any
  clinical/distress claim stays a proxy, never a diagnosis.
- **Fairness ethics.** Gini .329 on naturalistic speech = a few speakers absorb the utility; in a
  small-actor drama corpus this is an equity risk worth reporting per-speaker, especially before
  any downstream affect-inference use.

### Limitations & open questions for ViEmoSpeech

- **Contradiction vs bimodal-08's backbone leaderboard.** bimodal-08 reports a crisp naturalistic
  ranking **Whisper-V3 > XEUS > WavLM > HuBERT > Wav2Vec2**; this paper's own MSP-Podcast winner is
  a **domain-adapted wav2vec2** (w2v2-L-12-avd .650) with HuBERT-L second (.624 tuned) and Whisper
  encoders *below* both (Whisper-t .387 exploration), **and** it shows year/size/architecture
  rankings are unstable under hyperparameters and model-set choice (ρ≈0, CIs crossing zero).
  ⇒ We cannot take *any* single backbone leaderboard (bimodal-08's included) as settled; the V-B
  arm must A/B WavLM vs emotion2vec vs Whisper-encoder vs a domain-adapted wav2vec2 *on our own
  clips with CIs*, not inherit a ranking. This paper is the reason to distrust the leaderboard.
- **Contradiction vs the leak-inflated VN baselines.** Honest speaker-independent naturalistic
  4-class UAR tops out at **.650**; vn-08 (86.6%) and vn-10 (0.87 UA) sit far above it precisely
  because they are not speaker-disjoint on naturalistic data. This paper is our cleanest external
  anchor that ~0.6 macro-recall — not ~0.87 — is the honest naturalistic ceiling.
- **No fusion, no tonal language, no CCC.** The study is single-modality-at-a-time (audio *or*
  text, error-analysis complementarity only — never a *learned* fusion), tests **no tonal
  language**, and reports categorical UAR only — **no V/A CCC** and **no distress/clinical** head.
  So it moves V-G/V-B/V-H strongly but is silent on V-A (fusion architecture), V-C (ASR-noise
  robustness — it uses clean human transliteration for FAU-AIBO and Whisper-large-v2 ASR for MSP
  but never ablates ASR error), V-D's tone specifics, V-E, and V-F beyond the acted-proxy caution.
- **Gap vs our plan: they had no compute to resolve the scaling question.** They explicitly could
  not test within-architecture scaling or large audio-LMs (ALMs), and note omitting ALMs as their
  "most important omission" (§VI). Our small-fusion-over-ALM bet (bimodal-09) is therefore *not*
  contradicted by this paper — it is simply outside its scope, and their diminishing-returns
  finding is mild supporting evidence for not chasing size.
- **Open question for us:** run their eGeMAPS layer-wise linear probe (μ(P)/σ(P)/jitter/shimmer/
  HNR/formants) on our VN-adapted encoder — does σ(F0)/jitter probe *even worse* on Vietnamese
  (where tone loads F0) than the .237 they report on German EmoDB? A larger VN gap would be direct
  measured evidence for the tone×emotion F0-channel-competition claim (V-D) that no paper has yet
  produced.
