# Paper 16 — Review and Comparative Analysis of Databases for Speech Emotion Recognition

- **Authors:** S. Serrano, O. Serghini, G. Esposito, S. Carbone, C. Mento, A. Floris, S. Porcu, L. Atzori
- **Venue / year:** Data (MDPI), 10(10):164, 2025 (OA)
- **Links:** abs https://doi.org/10.3390/data10100164 · PDF `pdfs/16-ser-databases-review.pdf`
- **Group:** survey / benchmark (datasets)

**Summary:** So sánh 50+ corpora SER (collection method, annotation scheme, demographic diversity, ecological validity).

**Relevance to Pebble:** Reference chọn/đánh giá dataset SER khi mở rộng voice stream.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled profile (scored against, from the IDD layers):**
- **Primary (text):** ordinal suicide-risk classification; teacher-LLM silver labels → **gold-holdout** eval; ordinal-aware losses/metrics (QWK/MAE); reproducibility + clinical-data ethics are repo-wide binds (`docs/intent/constraints.md`).
- **Adjacent (voice):** frozen emotion2vec/WavLM backbone + shared trunk, **3 heterogeneous heads** — emotion CE / affect V/A **CCC** / crisis BCE under a **hard recall floor** — balanced by **Kendall uncertainty weighting** (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`).
- **Current voice stage:** heads trained on **RAVDESS with proxy labels** (Russell circumplex V/A; high-distress crisis set). Explicit next action item: **swap proxies for MSP-Podcast (continuous A/V/D) + DAIC (crisis)** for scientifically meaningful numbers.

### Analysis — SER Databases Review (Serrano et al., 2025)
- **Overlap:** 27% (peripheral) — D1=1, D2=1, D3=2, D4=0, D5=0, D6=0, D7=0
  - Compute: (3·1 + 2·1 + 1·2 + 2·0 + 2·0 + 2·0 + 1·0) / 26 × 100 = 7/26 × 100 ≈ 27%.
- **Closest on:** D3 (it *is* a catalogue of emotion corpora, incl. intensity-labelled ones like MCAESD/MEAD — the voice-stream analog of the emotion-transfer corpora dimension) and D1-partial (organizes corpora by **categorical vs dimensional/continuous** label schema, exactly the label duality Pebble's emotion + V/A heads consume).
- **Best point (Dataset to reuse):** The review's comparative framework — Table 2 parameters + the AHP **quality index Q = 0.2615·S′ + 0.0872·E′ + 0.6114·C′ + 0.0400·R′** (speakers, emotions, citations/yr, recency) + the Table 3 usage map — is a ready-made vetting map that shortlists which corpora actually supply **continuous dimensional labels** and appear in robustness studies, with MSP-Podcast/MELD/CMU-MOSEI flagged as the natural/dimensional corpora now displacing acted ones.
  - **How to apply to Pebble:** Use it to justify and scope the voice stream's planned proxy→real swap — confirm **MSP-Podcast (continuous A/V/D)** as the RAVDESS-proxy replacement for the affect (CCC) head, note it lacks a native crisis label (keep DAIC-class for the recall-floor head), then hand both candidates to `find-dataset` for license/gate checks against the repo's ethics bind.
- **Caveats:** Read selectively — intro/methodology/taxonomy/emotion-models (pp.1-6), database-characteristics + acted/elicited/**natural-corpus ethics** (pp.7-9), the tail of the 52-corpus catalogue (pp.44-48), and the full synthesis/discussion/conclusions incl. Q and Table 3 (pp.49-52). The **individual RAVDESS / IEMOCAP / MSP-Podcast** descriptions in the mid-section-6 catalogue were **not** read line-by-line (their coverage is confirmed via Table 3, which lists IEMOCAP=11, RAVDESS=11, MSP-PODCAST=2 occurrences); **DAIC-WOZ** does not appear in Table 3 and may be outside this review's SER-corpus scope (it covers stress/emergency-call corpora generically). Score is structurally low because it is a *dataset review* — orthogonal to Pebble's modeling dimensions (D4-D7 absent by construction); its real value is practical dataset selection, which the overlap % does not capture.

## Deep research — full-PDF read (2026-07-10)

> Scored against the **current ViEmoSpeech profile + Decision Register (V-A…V-H)** in
> `docs/tasks/paper-deep-analysis.md`, NOT the stale text-stream "Analysis" section above.
> This is THE corpus-landscape paper for V-H; it also anchors V-E (label-scheme conventions) and
> V-D (any tonal-language / tone-annotated corpus in the 52).

### Source-access note

- **PDF read end-to-end** via `pdftotext docs/papers/bimodal-ser/pdfs/16-ser-databases-review.pdf -`
  (1358 lines; all of §§1–8, Table 1, the full 52-row Table 2 spread across pp. 11–19, every
  individual corpus description §6.1–6.52, the §7 discussion incl. the quality index and Table 3,
  and the reference list). The local PDF **is the published venue version**: its header carries
  "*Data* **2025**, *10*, 164", "Published: 14 October 2025", DOI 10.3390/data10100164, and the
  MDPI CC-BY notice — MDPI *Data* is fully open-access and ships the final typeset PDF, so there is
  **no preprint/venue delta** to reconcile.
- **Web-validated** the headline framing against the venue landing page:
  query `Serrano "Review and Comparative Analysis of Databases for Speech Emotion Recognition"
  Data MDPI 2025 fifty-two corpora quality index` → resolved
  `https://www.mdpi.com/2306-5729/10/10/164`, which corroborates **"fifty-two databases across
  acted, elicited, and natural speech"**, the Oct-14-2025 publication date, and the four-axis
  narrative-review framing (✔). A direct `WebFetch` of the MDPI HTML returned **HTTP 403** (bot
  block), so the Q-index coefficients and the four-dimension definitions below are quoted from the
  venue PDF itself (equation (1), §5, §7.1) rather than re-fetched — acceptable because the local
  PDF *is* the published artifact.

### What the paper actually does

A **narrative** (explicitly *not* PRISMA-systematic) review + comparative analysis of **52 SER
corpora** released up to mid-2025 (§2). It contributes four things:

1. **A four-dimension classification framework** (§5, the load-bearing V-H artifact):
   - **Scope** — what the corpus captures and *how it is elicited*: **acted / elicited / natural**;
     target task/application; **lab vs "in the wild"**.
   - **Physical Existence** — "*whether the corpus can actually be obtained and reused*": **access
     and licensing**, documentation/metadata quality, **persistent identifier (DOI)**, and
     **defined train/val/test splits**.
   - **Contents** — speakers, total duration (hours/utterances), recording/channel + sampling rate,
     **class distribution**, **label schema (categorical vs dimensional)**, *who labels*
     (self/observer/expert/crowd), inter-rater reliability, transcripts/lexical layers, extra
     modalities.
   - **Language Composition** — languages, **dialects/accents, code-switching**, demographic breadth.
2. **A speech-type taxonomy** with an advantages/limitations table (Table 1, §5): acted =
   controlled/wide-emotion-range/comparable but low ecological validity; elicited = compromise,
   lower inter-rater agreement; natural = ecologically valid but noisy, imbalanced, and **raises
   "ethical and privacy concerns"**. The review states **">60% of emotional speech databases are
   simulated [ref 47, Schröder 2001]"** (§5.1) — ≈ (a cited secondary statistic, not their own count).
3. **The 52-corpus inventory (Table 2)** — columns: *corpus name, ref/year, language(s), speech
   type/speakers, emotions, recording conditions, annotation method*. (Note: **Table 2 has NO
   license, DOI, split, or size-in-hours column** — see Limitations; the "Physical Existence"
   dimension is described in prose but never tabulated.)
4. **A quality index** for weighting corpora (§7.1, eq. 1) —
   **Q = 0.2615·S + 0.0872·E + 0.6114·C + 0.0400·R** (S = normalized #speakers, E = #emotions,
   C = citations/year, R = recency), AHP-weighted (✔, eq. (1), venue PDF). **Citations dominate
   (0.61)** and **speaker count is second (0.26)**; emotions (0.087) and recency (0.040) are near
   noise. Plus Table 3 (usage map of 26 early-2024 SER papers): IEMOCAP and Chou each cited 11×,
   DES/TESS/CREMA-D 5×, MSP-Podcast/MELD 2× — acted English benchmarks still dominate real usage.

**Key facts for our three target decisions (from a full scan of Table 2 + §6.1–6.52):**

- **Languages (V-D, V-H):** English dominates; then German, French, Italian, Mandarin, plus
  Hindi, Bangla, Arabic, Persian, Spanish, Polish, Punjabi, Amharic, Greek, Danish, Slovenian, and
  multilingual (CREST, INTERFACE). **Vietnamese appears in 0 of 52 corpora** (✔, full Table 2 read).
- **Tonal-language corpora (V-D):** **6 of 52** are tonal-language — CASIA (Mandarin, acted, 4 spk),
  CHEAVD (Chinese, natural+acted, films/TV), NNIME (Chinese, acted, 44 spk), EMOVIE (Mandarin,
  acted, 9724 samples from movie clips, polarity labels), MCAESD (Mandarin, acted, 6 spk), and
  **CAVES (Cantonese, elicited, 10 spk)**. **CAVES is the only entry that even names tone**: it is
  "*a tonal language (with two more phonetic tones than Mandarin)*" and its 50 CHINT carrier
  sentences were "*selected to have a good coverage of the different lexical tones, both in initial
  and final sentence positions*" (§6.51) — but that is tone **balancing for stimulus control**, not
  a tone **annotation layer** and **not** a study of tone×emotion interaction. **0 of 52 corpora
  annotate lexical tone or treat tone as an analysis variable** (✔). This confirms the V-D
  whitespace from the corpus-supply side, matching the model-side finding across vn-06…13.
- **Label schema (V-E):** the review sets up the categorical vs dimensional duality (§4) but
  **never tabulates how many corpora use which** — a gap it leaves open. From my own read of Table 2
  + descriptions: the **large majority are categorical-only** (Ekman-style 5–8 discrete classes);
  **~8 of 52 carry a dimensional or continuous layer** — VAM (V/A/Dominance, purely dimensional),
  IEMOCAP (categorical + V/A/D 5-pt), MSP-IMPROV (discrete + continuous-in-time), NNIME
  (discrete + continuous-in-time), MSP-Podcast (attribute + categorical), Real-Life Call Center (2D
  activation-evaluation), CREMA-D (labels + real-valued **intensity**), CMU-MOSEI (Likert sentiment
  + emotion), SAFE (categorical + intensity/evaluation/reactivity) (≈ — my count from Table 2, not
  a figure the paper states). **None of the ~8 both-scheme corpora are tonal-language or Vietnamese;
  none carry a distress/severity flag alongside V/A.**
- **Found-from-media corpora exist but none match our box-set (V-H):** film/TV/online-sourced
  corpora are common — CREST (TV/DVD), SAFE (30 movies), ITA-DB (40 movies/TV series, dubbed),
  EMOTV1 (French TV), VAM (German TV talk show), CHEAVD (films/TV), ANAD (Arabic TV), MELD (*Friends*
  TV series), CMU-MOSEI (YouTube), EMOVIE (movie clips), PEMO (Punjabi movies), ITA-DB-RE
  (courtroom). So "cut emotion clips from TV/film" is a well-trodden collection method — **but every
  one either releases audio (triggering the copyright problem the review itself flags) or is
  gated/undocumented, and none is tonal + feature-only + CC-BY.**
- **The ethics/legality passage that directly authorizes our release model (V-H):** §5.3 and §7.3.
  §5.3: "*For media-derived corpora (film, TV, online platforms), researchers must address
  copyright/neighboring rights and terms of service; fair use or fair dealing depends on
  jurisdiction and rarely permits redistribution of raw audio… use clear dataset licenses and,
  where needed, controlled-access repositories.*" §7.3 closes with the operative sentence:
  "*Where these conditions cannot be met, distribution should be limited (for example, on-site
  access or **sharing only derived features**) or avoided.*" (✔, §5.3/§7.3 venue PDF). This is a
  peer-reviewed survey explicitly naming **feature-only release** as the legitimate answer for
  copyrighted found-media speech — precisely ViEmoSpeech's design.

### Parts directly useful for Pebble (tagged by Decision ID)

1. **[V-H] The four-dimension framework (Scope / Physical Existence / Contents / Language
   Composition) as our positioning-table skeleton.** Re-use these exact axes as the columns of the
   ViEmoSpeech "where we sit" table, but **add the two columns Table 2 omits**: `Release form`
   (raw-audio vs features-only) and `Source legality` (own-recording / CC-licensed / copyrighted
   found-media). Under this framework ViEmoSpeech is the unique row: Scope = **natural /
   found / in-the-wild (TV drama)**; Physical Existence = **CC-BY, features-only, DOI, speaker-
   disjoint splits with whole-series holdout**; Contents = **7-cat + V/A(1–5) + distress, human-
   labeled, syllable-tone layer**; Language = **Vietnamese + Bắc/Trung/Nam dialect**. Complements
   the THAI-SER positioning table already adopted for V-H (vn-11) — 16 gives the *canonical
   published dimension names*; THAI-SER gives the tonal-corpus comparison row.
2. **[V-H] The quality index Q and its weights as a scoping/expectation calibrator.** Q's
   coefficients say the field rewards **citations (0.61) and speaker count (0.26)** far above
   emotion breadth (0.087) or recency (0.040). Concretely: a brand-new corpus scores near-zero on Q
   for years regardless of design quality (C≈0, R small), and our **speaker count** (drama cast,
   tens not hundreds) is the one intrinsic lever we can move. Do **not** chase Q; use it to set
   realistic reviewer expectations and to justify reporting our own intrinsic-quality axes
   (tone annotation, dialect, distress) that Q ignores.
3. **[V-H] The §5.3/§7.3 "sharing only derived features" clause as the citable legal-design
   anchor.** This is the single most useful sentence in the paper for us: cite it verbatim as
   independent, peer-reviewed justification that features-only release is the *recommended*
   disposition for copyrighted found-media SER — turning our media-legality constraint
   (`docs/intent/constraints.md`) from a limitation into an alignment with published best practice.
4. **[V-E] The categorical-vs-dimensional duality + the missing count.** The review confirms both
   label families are mainstream and that **carrying both is rare (~8/52) and never combined with a
   distress flag or a tonal language**. Use this to justify ViEmoSpeech's dual 7-cat + V/A scheme as
   deliberately spanning both conventions, and to position the distress flag as a *third* axis no
   corpus in the 52 provides. Also lift the review's naming of the annotator-source taxonomy
   (self / observer / expert / crowd) + inter-rater-reliability expectation into our ADR-002/003
   annotation-protocol spec fields.
5. **[V-D] The 0/52-tone-annotation finding as corpus-side novelty evidence.** Pair this with the
   model-side triangulation (vn-06/07/13): no SER *corpus* annotates lexical tone and no SER *model*
   measures tone×emotion channel competition. CAVES is the closest (tonal, tone-balanced stimuli)
   and is the cite-and-distinguish precedent — it *controls* for tone, we *annotate and measure* it.

### How each part helps Pebble succeed

- **Positioning table (part 1) → the method/corpus paper's Table 1.** Build one comparison table
  keyed on 16's four dimensions + our two added columns, populated with the corpora our register
  already names (ViSEC, VLSP-56h, VNEMOS, THAI-SER, MSP-Podcast, IEMOCAP, CAVES). The empty cells
  (Vietnamese ∩ tonal-annotated ∩ features-only ∩ CC-BY ∩ dimensional+distress) *are* the
  contribution figure. Artifact: the positioning table in the ViEmoSpeech corpus paper + a stub in
  `docs/spec/capabilities/`.
  - **Transfer risk:** LOW — these are published dimension names, directly reusable. The only risk
    is that "natural/found" flattens our specific sub-case (single-speaker cut TV-drama); our two
    added columns resolve it.
- **Quality index (part 2) → honest scoping in the paper's limitations.** Add a sentence: "under
  Serrano et al.'s citation-dominated Q, any new corpus is undervalued by construction; we instead
  report intrinsic design axes (tone/dialect/distress) that Q's weights (0.087 emotions, 0.040
  recency) do not capture." This pre-empts a "low-impact new dataset" reviewer objection.
  - **Transfer risk:** MEDIUM — Q is descriptive of the surveyed set, not a normative benchmark; do
    not compute a Q for ViEmoSpeech and compare (it would be misleadingly near-zero pre-citations).
- **Feature-only clause (part 3) → the Data Availability + Ethics section.** Cite §5.3/§7.3 directly
  where we describe the release = features+timestamps+labels+speaker-ids. It converts our hard
  constraint into "consistent with the release disposition recommended by the most recent SER-corpus
  review." Artifact: Data Availability statement + `docs/intent/constraints.md` cross-reference.
  - **Transfer risk:** LOW — the clause is jurisdiction-agnostic and explicitly covers "film, TV,
    online platforms"; it maps 1:1 to our TV-drama source. Caveat: it is guidance, not a legal
    opinion — our actual VN-jurisdiction copyright analysis still stands on its own.
- **Label-duality count (part 4) → V-E label-scheme spec.** Justify the dual scheme and the
  standalone distress axis as filling the "~8/52 carry both, 0/52 carry a distress flag on a tonal
  language" gap; import the self/observer/expert/crowd + IRR fields into the labeler spec
  (`tools/labeler/SPEC.md`) so our annotation metadata is comparable to the surveyed corpora.
  - **Transfer risk:** MEDIUM — the "~8/52" tally is mine, not the paper's stated figure (≈); if
    cited as a number we must recount and own it, not attribute the count to Serrano et al.
- **Tone-annotation gap (part 5) → V-D novelty defense + the tone×emotion figure.** Use 16 as the
  corpus-supply half of the two-sided novelty claim; CAVES becomes a one-line cite-and-distinguish
  ("tone-balanced for control, not annotated") in the method paper's related-work.
  - **Transfer risk:** LOW — the 0/52 reading is direct from Table 2 + §6.51; CAVES is unambiguously
    control-only. Residual risk: a tonal corpus published *after* mid-2025 could annotate tone;
    re-check at submission time.

### Child mental-health lens (found-TV / tonal / feature-only transfer for ViEmoSpeech)

- **How many boxes are simultaneously unchecked in the 52?** ViEmoSpeech asks for the intersection
  of: **Vietnamese (0/52), lexical-tone-annotated (0/52), tone×emotion-measurable (0/52),
  found-copyrighted-TV-drama source (present but ~12/52 and always audio-released/gated),
  features-only CC-BY release (0/52 in Table 2 — no corpus in the inventory is documented as a
  features-only release), dimensional + categorical + distress labels (0/52 combine all three).**
  Every one of these boxes is *individually* unchecked or rare, and **their conjunction is empty** —
  the review's own inventory is the strongest evidence that ViEmoSpeech occupies genuine whitespace.
- **Children specifically:** the review flags (via Matveev et al. [17], §3) that "*emotional models
  [should be] tailored to specific demographics, such as children, as their speech patterns differ
  from those of adults*", yet **only 1 of 52 corpora involves children — AIBO** (German/English
  children × Sony AIBO robot, human-robot elicited speech), and it is neither tonal, nor Vietnamese,
  nor dimensionally labeled, nor mental-health-oriented. Child-register SER is near-absent from the
  entire published corpus landscape. (Caveat: ViEmoSpeech's own source = *adult* TV-drama actors,
  so 16 does not remove our child-register transfer risk — it shows the whole field shares it.)
- **Ethics the review foregrounds and we must honor:** §5.3 explicitly lists **"extra safeguards for
  vulnerable populations such as children or patients,"** data minimization, de-identification, and
  — for found media — copyright/ToS handling with controlled-access or feature-only release. This is
  independent external support for our media-legality invariant and our distress-as-acted-proxy
  framing: the review treats natural/found affect as ethically loaded and recommends exactly the
  release discipline we adopt.
- **Distress transfer risk:** the review's clinical touchpoint is a single cited depression-from-
  voice study (Hansen et al. [9], §1), described only as "early diagnosis." No corpus in the 52
  carries a clinical distress/severity label. So 16 offers **no** distress-label precedent to
  transfer — it *confirms* that our distress head is unprecedented at the corpus level and reinforces
  the V-F honest-proxy framing (acted-drama distress ≠ clinical, screen for recall only).

### Limitations & open questions for Pebble

- **Contradiction / gap #1 (vs the paper's own framework):** 16 names **"Physical Existence
  (access and licensing… DOI… train/val/test splits)"** as one of its four load-bearing dimensions,
  yet **Table 2 tabulates none of them** — no license column, no DOI, no split, no size-in-hours.
  The paper cannot actually answer "which of these 52 can I legally reuse and how is it licensed?"
  from its own table. This is precisely the axis ViEmoSpeech is built around, so our positioning
  table **must add the `Release form` + `Source legality` columns 16 omits** — and we can cite this
  omission as the concrete gap our corpus documentation closes.
- **Contradiction / gap #2 (vs THAI-SER, vn-11, on the naturalness bet):** THAI-SER empirically
  found **scripted > improvised** (WA 73.99 vs 61.80), cutting against the "natural speech is
  better" thesis. Review 16 leans the *opposite* way rhetorically — it repeatedly frames natural/
  found speech as higher ecological validity and "the direction the field is moving," while conceding
  natural corpora yield **lower inter-rater agreement** and harder annotation (Table 1, §5.4). Both
  can't be uncritically true for us: found TV-drama gives ecological validity **and** annotation
  difficulty. ViEmoSpeech must *measure* whether its found-drama register actually beats an acted
  baseline (V-G), not assume the review's ecological-validity narrative.
- **Gap #3 (V-E, unquantified):** the review discusses categorical vs dimensional at length but
  **never reports the split count**, so our "~8/52 carry both" is our own tally, not a citable
  figure (tagged ≈). If we need a citable number, we must count it ourselves in the paper and can
  note that 16 left it unquantified.
- **The Q-index is adoption-biased, not quality-biased:** with C (citations/yr) weighted 0.61, Q
  measures *incumbency*, not corpus design quality — it structurally penalizes exactly the new,
  under-represented-language corpora the review says the field needs. Do not use Q to argue
  ViEmoSpeech's value; use it only to explain why a design-quality argument is needed instead.
- **Open question — no modeling guidance:** 16 is a *dataset* review; it contributes zero on fusion
  architecture (V-A), audio backbone (V-B), or ASR-noise robustness (V-C). For those, 16 is silent
  and the register-dependence synthesis from the bimodal papers stands unaffected.
- **Open question worth one check:** several found-media corpora in Table 2 (CHEAVD, ANAD, MELD,
  CMU-MOSEI) are TV/online-sourced yet apparently distribute audio — worth confirming whether any
  publishes a *features-only* variant we could cite as a direct precedent, since Table 2's lack of a
  release-form column hides this.
