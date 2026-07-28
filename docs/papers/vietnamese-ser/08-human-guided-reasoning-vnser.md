# Paper vn-08 — Human-Guided Reasoning with Large Language Models for Vietnamese Speech Emotion Recognition

- **Authors:** Truc Nguyen, Then Tran, Binh Truong, Phuoc Nguyen T. H.
- **Venue / year:** arXiv preprint, Apr 2026
- **Links:** abs https://arxiv.org/abs/2604.01711 · PDF `pdfs/08-human-guided-reasoning-vnser.pdf`
- **Group:** vietnamese-ser / most recent VN SER (baseline + gap evidence)

**Summary:** Hybrid acoustic-feature (pitch/energy/MFCC) + LLM-reasoning
pipeline for 3-class Vietnamese SER (calm/angry/panic) on a new 2,764-sample
corpus (Fleiss' κ = 0.857); ~86.6% accuracy, approaching human agreement.

**Relevance to ViEmoSpeech:** Most recent VN SER paper; *names* the tone
confound in its motivation without addressing it — strongest evidence the
tone-aware niche is open but closing fast. Natural baseline/label-scheme
comparator (their κ=0.857 on 3 classes vs our 7-class + V/A + distress).

> Stub created 2026-07-10 (task `docs/tasks/paper-deep-analysis.md`); deep-read pending.

## Deep research — full-PDF read (2026-07-10)

### Source-access note

The local PDF `pdfs/08-human-guided-reasoning-vnser.pdf` was extracted end-to-end with
`pdftotext` (all of §§I–VI plus Tables I–V and the reference list). This paper is an
**arXiv preprint only** (arXiv:2604.01711v1, cs.CL, 2 Apr 2026) — there is no journal/conference
venue version, so the preprint is authoritative and no preprint-vs-published delta exists.

Web-validation of load-bearing numbers:
- Query `Human-Guided Reasoning Large Language Models Vietnamese Speech Emotion Recognition arXiv 2604.01711`
  → resolved the arXiv abstract/HTML (`https://arxiv.org/html/2604.01711v1`, `https://arxiv.org/pdf/2604.01711`).
  Confirmed: 2,764 samples, 3 classes (calm/angry/panic), Fleiss' κ = 0.8574, up-to 86.59% accuracy,
  Macro-F1 ≈ 0.85–0.86. **✔ corroborated.**
- WebFetch of `https://arxiv.org/html/2604.01711v1` asking specifically about (a) data-availability,
  (b) tone/dialect as confound, (c) best-model number, (d) split sizes, (e) κ, (f) consent/license.
  Confirmed best = **86.59% by LLaMA3.2-3B**; splits Set1 706 / Set2 691 / Set3 696 / Test 671;
  and — the two research-bearing negatives — **no data-availability statement** and **no discussion
  of consent, licensing, or copyright** for the movie/TV/interview audio. **✔ corroborated** (validated
  as *absent*, not merely un-quoted by me).

### What the paper actually does

**Task.** 3-class Vietnamese SER — **calm / angry / panic** — framed as a healthcare/telehealth
early-warning problem (panic = the clinically salient class). Not 7-class, no valence/arousal, no
separate distress dimension; "panic" is the nearest analogue to a distress flag.

**Corpus (§IV).** 2,764 audio segments from **28 found sources** (5 movies, 10 entertainment
programs, 13 interview programs), spanning the three dialect regions (Bắc/Trung/Nam). Total duration
**14,841.79 s = 4.12 h**, ~453 MB. Class distribution is near-balanced: angry 942 (34.1%),
calm 980 (35.5%), panic 842 (30.5%) [§IV-A, ✔]. Preprocessing: 16 kHz mono, amplitude-normalized,
automatic + manual denoise, **VAD silence removal**, segmentation into utterances with manual
correction, low-quality filtering (§IV-B) — a pipeline structurally close to ViEmoSpeech's
ffmpeg→VAD→turn-split chain, minus source-separation and ASR.

**Annotation protocol (§IV-B/C).** Each segment labelled by **3 annotators** on the 3-class scheme,
guided by written rules keyed to **pitch, intensity, speaking rate** (calm = stable pitch/low energy
variation; angry = high intensity+pitch; panic = high variability in pitch/energy/rate). Disagreements
resolved by **re-evaluation or additional annotation; ambiguous samples refined or removed**.
Reliability reported two ways (Table I): **Fleiss' κ = 0.8574** across the 3 raters; pairwise Cohen's
κ = A–B 0.8573, A–C 0.8394, B–C 0.8757 (labelled "Avg 0.8575") — "substantial to almost perfect"
[Table I, ✔]. Table II gives **annotator-wise accuracy vs the consensus gold**: A 87.8%, B 90.5%,
C 90.4% (per-class 89.1–91.6%) — this is the "human ceiling" the model is later measured against [✔].

**Model pipeline (§III).** Three stages: (1) frame-level **pitch/energy/MFCC** aggregated to a
fixed-length vector; an **SVM** on those features gives an initial prediction + a **confidence** score;
(2) a **confidence-based router** sends high-confidence samples straight through and delegates
ambiguous ones to (3) an **LLM reasoning** module that receives a *textual description* of the acoustic
feature trends (stability/variability) plus **human-derived heuristic rules** and known
angry↔panic confusion patterns, and reasons to a label. An **iterative-refinement loop** turns
misclassified cases into updated rules/prompt edits. The LLM is the primary decision-maker; ML is
auxiliary "evidence." No learned audio backbone (no wav2vec2/WavLM/emotion2vec); wav2vec2 is only
cited as related work.

**Results.** Ablation by pipeline "version" on 3 splits with Qwen2.5-7B (Table III): v1 basic
(naive LLM) 31–37%; v2 +rules 43–48%; v3 refined 54–56%; **v4 hybrid 84.6–86.1%** (Macro-F1 0.847–0.858);
v5 "auto"/unguided reasoning collapses to 31–38% (Set-level) — evidence that *unstructured* LLM
reasoning adds noise [Table III, ✔]. Across LLM backbones on the Test set (Table IV):
v4 hybrid = **Qwen2.5-7B 85.84% / Qwen2.5-14B 85.54% / LLaMA3.2-3B 86.59% / Gemma3-4B 86.14%**,
Macro-F1 ≈ 0.85–0.86 — nearly backbone-independent, and within ~2–4 pts of the 88–90% human ceiling
[Table IV, ✔]. Table V is the key modality contrast: a **text-only** path (Audio→Whisper→Text→LLM)
scores only **38.70–44.11%**, versus the acoustic-feature pipeline's 85–86.6% — the paper's headline
claim that acoustic information is indispensable for this task [Table V, ✔].

**Data availability / ethics.** **None.** No release statement, no license, no consent/copyright
discussion for the scraped movie/TV/interview audio, no code link (validated present-absent via
WebFetch, ✔). The corpus is described but, on the evidence, closed.

### Parts directly useful for Pebble (tagged by Decision ID)

1. **Multi-annotator, rule-guided κ protocol as a reliability benchmark — but on a 3-class scheme
   (V-E).** 3 raters, written guidelines keyed to pitch/intensity/rate, disagreement→re-evaluation,
   ambiguous→removed, reported as Fleiss' κ = 0.8574 + pairwise Cohen 0.839–0.876 [Table I, ✔].
   *Transfer risk:* their κ is high **partly because the scheme is only 3 coarse, acoustically-separated
   classes**; ViEmoSpeech's 7-class + valence/arousal(1–5) + distress is a far finer target and will
   have structurally lower κ/α. So κ=0.857 is a **ceiling for a 3-class problem, not a bar ViEmoSpeech
   should expect to hit** — it argues for reporting κ *per label-dimension* and keeping at least
   one coarse rollup (e.g. distress binary) where high agreement is actually attainable.

2. **"Human-ceiling" framing for the eval (V-G).** They put model accuracy (86.6%) next to
   annotator-vs-consensus accuracy (87.8–90.5%, Table II) and claim "approaching human agreement"
   [§V-C, ✔]. *Transfer risk:* legitimate framing and directly reusable for ViEmoSpeech's gold-set
   report **only if** the human ceiling is computed the same disciplined way; note their model number
   is on splits that are **not stated to be speaker/source-disjoint** (see gap below), so their
   headline is not a clean comparator — ViEmoSpeech must compute both ceiling and model number under
   ADR-002 whole-series holdout.

3. **The tone/region confound named in motivation but never modelled — verbatim novelty-gap evidence
   (V-D).** Intro §I: *"for low-resource languages such as Vietnamese, SER remains challenging due to
   limited standardized datasets and complex acoustic characteristics influenced by tone, region, and
   speaking style."* And §I: *"Emotions such as angry and panic often exhibit overlapping patterns in
   pitch and energy, making them difficult to distinguish reliably."* Their entire feature set is
   pitch/energy/MFCC and their rules are "high variance in pitch/energy → panic" — i.e. they **use the
   exact channel (F0/energy) that Vietnamese lexical tone also occupies, yet never separate tone from
   emotion.** *Transfer risk:* none — this is the cleanest citable evidence that the newest VN SER work
   *acknowledges* the tone×emotion channel-competition and *leaves it unaddressed*, which is precisely
   ViEmoSpeech's V-D headline claim.

4. **Modality-ablation number: text-only VN SER collapses to 38–44% (V-C, V-G).** Table V, text-only
   Whisper→LLM = 38.70–44.11% acc [✔]. *Transfer risk:* **high — treat as a weak strawman, not a
   verdict.** Their text branch is zero-shot ASR→prompt with no fine-tuned encoder; ViEmoSpeech's text
   branch is PhoBERT/ViSoBERT fine-tuned on ASR transcripts. The number shows *ASR-text-alone-under-a-
   generic-LLM* is weak on 3-class acted drama; it does **not** license "text is useless for VN SER,"
   and must not be read as contradicting ViEmoSpeech's phonation-heavy hook (which says the text
   branch should carry *more* load *because* the audio F0 channel is contaminated by tone).

5. **Panic-as-distress, rule-first routing (V-F).** Confidence router: SVM confidence gates whether the
   expensive LLM reasoning fires; "panic" is the high-stakes class they most want to catch [§III-D, §I].
   *Transfer risk:* the routing idea (cheap model handles easy cases, escalate ambiguous to a heavier
   reasoner) maps onto ViEmoSpeech's recall-floor distress head only as an *inference-time* pattern; it
   gives no calibration/threshold numbers and no recall floor, so it is a design analogue, not a recipe.

### How each part helps Pebble succeed

- **V-E (annotation):** Adopt their disciplined structure — ≥3 raters, written pitch/intensity/rate
  guideline, disagreement→adjudicate, ambiguous→drop — but **report κ per dimension** and do not
  advertise a single 0.857-style headline; ViEmoSpeech's finer scheme (7-class + V/A + distress) makes
  a global κ misleading. Concrete artifact: the `docs/spec/capabilities` annotation-protocol doc and
  the gold-set κ/α report should carry a coarse "distress binary" rollup where high agreement is
  reachable, plus per-class κ that is honestly lower for the 7-way head.
- **V-G (eval):** Build the same model-vs-human-ceiling table ViEmoSpeech will need for the method
  paper — but compute the model number under the **speaker-disjoint whole-series holdout (ADR-002)**,
  which this paper does not do. This paper is the citation for "reasoning/LLM VN SER exists and reaches
  ~86% on 3 classes"; it is **not a runnable baseline** (corpus closed, 3-class only). Keep
  arXiv:2412.09829 (rule fusion) as the comparable, reproducible baseline; cite 2604.01711 for
  label-scheme and κ context only.
- **V-D (tone claim):** Quote the two §I sentences above directly in the ViEmoSpeech related-work as
  the "named-but-unaddressed" evidence, then show ViEmoSpeech's tone-annotation + F0/phonation
  disentangling as the fill. This is the strongest single sentence in the prior art for motivating the
  tone×emotion measurable claim.
- **V-C (text under ASR noise):** Use Table V as *motivation* ("naive ASR-text alone is 38–44%, so a
  fine-tuned text branch is needed") but run ViEmoSpeech's own text-branch ablation (PhoBERT/ViSoBERT
  on PhoWhisper transcripts) rather than importing their number as a bound.
- **V-F (distress):** Borrow the confidence-router *inference pattern* for the distress head's
  escalate-on-uncertainty behavior, but supply the missing recall floor + calibration (their paper has
  neither).

### Child mental-health lens (ViEmoSpeech regime)

- **Found-media, human-labels-as-truth: strongly congruent.** Like ViEmoSpeech, they cut emotion
  segments from **found TV/movie/interview media** and treat multi-rater human labels as sole ground
  truth (no clinical labels). Their panic/angry/calm from acted drama is the same *acted-proxy*
  caveat ViEmoSpeech carries for distress — acted panic ≠ clinical panic. Reusable framing for the
  distress head's honest-proxy disclaimer.
- **The legality gap ViEmoSpeech is built to close is wide open here.** They scrape movies/entertainment/
  interviews with **zero license, consent, or release discussion** and ship no corpus. ViEmoSpeech's
  entire design premise — a **feature+timestamps+labels-only CC-BY release** so copyrighted media never
  leaves git — is exactly the problem this paper does not solve. That is both the risk (their corpus is
  legally unshippable as-is) and ViEmoSpeech's differentiator.
- **No speaker/source-disjoint discipline stated.** Set1/2/3/Test are described as random partitions
  "for fair assessment" (§V-A) with **no mention of speaker- or source-disjointness**. With only 28
  sources and acted drama, the same actor/scene can straddle train and test, which can inflate 86.6%.
  For a child-facing or clinical proxy this matters: a number that leaks speaker identity overstates
  generalization to a new speaker. ViEmoSpeech's ADR-002 whole-series holdout is the mitigation and the
  reason its numbers will look lower-but-honest.
- **Transfer of the specific accuracy is low.** 86.6% is on **3 acoustically-separated classes with a
  possibly-leaky split**; it is not a target ViEmoSpeech's 7-class + V/A + distress head should be
  benchmarked against. Cite it as prior-art context, not a performance bar.

### Limitations & open questions for Pebble

- **Contradiction/gap #1 (vs ViEmoSpeech plan — split discipline):** The paper's headline "approaching
  human-level" (86.6% vs 88–90%) rests on Set1/2/3/Test with **no stated speaker/source-disjoint
  constraint** (§V-A). Under ViEmoSpeech's ADR-002 whole-series holdout the honest number would very
  likely be lower. This is the direct methodological contradiction: their reliability claim is not
  reproducible under ViEmoSpeech's own eval invariant.
- **Contradiction/gap #2 (vs vn-12 "semantics dominate" / with ViEmoSpeech's phonation hook):** Table V
  asserts acoustics are indispensable and text-only is near-useless (38–44%), the *opposite* of the
  "semantics dominate" line (vn-12, arXiv:2510.25054). Both are over-readings of weak baselines: vn-12
  uses SLMs that under-weight prosody; this paper uses un-tuned ASR→LLM that under-weights semantics.
  ViEmoSpeech's tone×emotion claim threads between them — audio F0 is *contaminated by tone* so the
  fine-tuned text branch must carry more load than in non-tonal SER — and neither prior paper actually
  tests that, leaving the measurable claim open.
- **Novelty-gap confirmed (V-D):** the newest VN SER paper names tone/region as the source of acoustic
  ambiguity and builds its whole feature set on the F0/energy channel, yet never disentangles tone from
  emotion. The tone-aware niche is open — and, being April 2026, closing fast.
- **Open questions:** (a) Is the corpus obtainable on request? It is unreleased and unlicensed — likely
  not shareable, so no head-to-head on their exact data is possible. (b) What is the confidence router's
  threshold and how often does the LLM actually fire? Unreported — so the cost/latency of the reasoning
  stage is unknown. (c) No calibration, no recall floor, no per-class error breakdown beyond aggregate
  Macro-F1 — ViEmoSpeech must supply all three for the distress head.
