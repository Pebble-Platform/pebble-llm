# Paper vn-09 — PhoWhisper + PhoBERT Bimodal Vietnamese SER (VNU Hà Nội)

- **Authors:** (VNU Hà Nội group — verify from PDF)
- **Venue / year:** arXiv preprint, Dec 2024
- **Links:** abs https://arxiv.org/abs/2412.09829 · PDF `pdfs/09-phowhisper-phobert-fusion.pdf`
- **Group:** vietnamese-ser / direct baseline to beat

**Summary:** Bimodal Vietnamese SER combining PhoWhisper ASR transcripts with
PhoBERT text features via rule-based fusion, on a ~250-clip corpus.

**Relevance to ViEmoSpeech:** The direct baseline the method paper must beat —
same building blocks (PhoWhisper+PhoBERT) but rule-based fusion, tiny corpus,
no tone treatment, no recall-floor. Our deltas: learned fusion (V-A), 3611+ utt
corpus, tone annotations (V-D), distress recall-floor (V-F).

> Stub created 2026-07-10 (task `docs/tasks/paper-deep-analysis.md`); deep-read pending.

## Deep research — full-PDF read (2026-07-10)

> **Stub-correction up front.** The stub above (and the task inventory) call this "PhoWhisper +
> PhoBERT bimodal Vietnamese SER, rule fusion, ~250-clip corpus." The full PDF is something else:
> a **service-quality-assessment pipeline** (call-centre grading: *Good / Neutral / Offensive*),
> not a SER paper. It does **not** build a corpus, does **not** fuse audio+text for emotion, and
> reports **no end-to-end evaluation of its fusion**. The text branch is PhoBERT-CNN doing
> **hate-speech** classification (not emotion); the ~250 clips are the *external* VNEMOS SER set it
> borrows a pretrained model from (that model is paper vn-10, arXiv:2412.08683, same authors). The
> paper is still the right "rule-fusion baseline" reference for **V-A**, but the baseline is a
> hand-written override rule with no measured accuracy, so "the number to beat" does not exist.

### Source-access note

- **Local read:** `pdftotext "docs/papers/vietnamese-ser/pdfs/09-phowhisper-phobert-fusion.pdf" -`
  extracted the full 8 pages cleanly (arXiv:2412.09829**v1** [cs.CY], 13 Dec 2024). All figures are
  images (architecture diagrams, GDP chart); the extraction captured every equation (Eqs 1–5,
  denoiser) and the only numeric block (the ViHSD component numbers in §2.4). A `grep` sweep for
  `table|accuracy|F1|precision|recall|%|WER|split|test` over the whole PDF returned **no results
  table and no fusion/service-quality evaluation** — confirming §2.4's ViHSD numbers are the sole
  quantitative content.
- **Web validation — status of the paper.** Query `arXiv 2412.09829 Speech-based Multimodel
  Pipeline Vietnamese Services Quality Assessment` → `https://arxiv.org/abs/2412.09829`. The paper
  was **withdrawn by the authors** at v2 (18 Dec 2024, five days after v1). Withdrawal note
  (verbatim, ✔ corroborated): *"I am writing to request the withdrawal of my preprint due to the
  discovery of significant inaccuracies in the results. These errors could mislead future research
  and applications, which compromises the integrity of my work. I believe withdrawing the paper is
  essential to uphold scientific standards…"* This is decision-bearing: the direct-baseline paper
  is self-retracted.
- **Web validation — borrowed text-branch numbers.** Query `PhoBERT-CNN ViHSD Vietnamese hate
  offensive detection accuracy macro F1 Tran 2022` → `https://arxiv.org/abs/2206.00524` (Tran et
  al., *Vietnamese Hate and Offensive Detection using PhoBERT-CNN*, Neural Computing & Applications
  2022, the ref [16]/[23] this paper reuses). Original reports **macro-F1 67.46%** on ViHSD (✔
  corroborated). This paper's §2.4 reports **86.14% accuracy** with per-class F1s that macro-average
  to ~53.7% — *lower* than and inconsistent with the source (see inconsistency flag below).
- **Author/affiliation (stub lacked it, now filled, ✔ from PDF title block + arXiv):**
  Quang-Anh N.D. (`anhnd@vnuis.edu.vn`), Minh-Duc Pham (`pmduc2808@gmail.com`), Thai Kim Dinh
  (`thaikd@vnu.edu.vn`, corresponding) — **International School, Vietnam National University, Hanoi
  (VNU-IS)**. Same lab as vn-10 (VNEMOS / Dynamic-CBAM depression).

### What the paper actually does

A five-stage **cascade pipeline** (§2, Figs 2–5) that grades a customer-service phone call:

1. **Denoiser** (§2.1, Eqs 1–5): Resemble-AI `resemble-enhance`, a UNet on complex spectrograms
   (predict amplitude mask + phase rotation), L1 waveform loss. Off-the-shelf, not trained here.
2. **WhisperX** (§2.2): speaker diarization ("who spoke when") via wav2vec2.0 alignment + pyannote
   VAD/embedding/clustering. Off-the-shelf.
3. **PhoWhisper** (§2.3): Vietnamese ASR (S2T). Cited as fine-tuned on **844 h** (Common Voice-Vi,
   VIVOS, VLSP-2020, + a private 26,000-speaker / 63-province set), "SOTA for Vietnamese S2T"
   (≈ corroborated; this is the PhoWhisper paper's claim, ref [15] Le & Nguyen, ICLR 2024 Tiny
   Papers, not measured here). Off-the-shelf.
4. **Text branch — PhoBERT-CNN** (§2.4): PhoBERT-base (frozen, feature extractor) → Text-CNN head,
   **fine-tuned on ViHSD** for **3-way hate-speech** classification (**CLEAN / OFFENSIVE / HATE**),
   20 epochs. Reported (§2.4, the paper's only numbers): **accuracy 86.14%**; per-class
   (P / R / F1): CLEAN **94.90 / 36.71 / 47.38**, OFFENSIVE **91.55 / 41.79 / 60.48**,
   HATE **93.19 / 30.90 / 53.14**. Note this classifies **written social-media text**, and is
   applied at inference to **ASR transcripts** — no adaptation between the two registers.
5. **Audio branch — SER** (§2.5): the **Dynamic Attention Network / Dynamic-CBAM** (MFCC → stacked
   Conv-BatchNorm-MaxPool blocks → GRU → Dynamic CBAM → FC), used **as a pretrained model** trained
   on **VNEMOS** — **250 annotated segments from 27 movies/series/live-shows, 5 emotions** (anger,
   happiness, sadness, neutral, fear). This is the external SER set the stub mislabelled as "their
   corpus"; it is ref [26] (VNEMOS, ICDV 2024) and the model is ref [24] (= vn-10). No SER numbers
   are reported in *this* paper.

**The fusion (§2.6) — the whole "bimodal" claim.** A hand-written **grading rule** over the two
branch outputs, producing **Good / Neutral / Offensive**:

- **Text overrides:** if S2T (PhoBERT-CNN) returns **OFFENSIVE or HATE → grade = Offensive**
  (unconditional priority to the text stream).
- **Emotion escalation:** else if text is clean **but SER ∈ {Anger, Anxiety, Sadness} → Offensive**
  ("customer did not have a good experience"). (Note: the SER head only emits anger/happy/sad/
  neutral/fear — "Anxiety" in the rule has no corresponding class, a loose end.)
- **Otherwise:** clean text → grade follows SER: **Happiness → Good, Neutral → Neutral**.

That is the entire "fusion": a **priority-override decision tree**, text-dominant, with **no learned
parameters, no weighting, no confidence, and no evaluation**. There is no §3 experiments — the paper
goes straight from §2.6 to a one-paragraph §3 Conclusion.

**Internal inconsistency (supports the withdrawal, ✖ uncorroborated / self-contradictory):** ViHSD
is ~82–83% CLEAN. A CLEAN **recall of 36.71%** is mathematically incompatible with an overall
**accuracy of 86.14%** (majority-class recall of 0.37 caps accuracy near ~0.30). The §2.4 numbers
cannot all be true simultaneously; they also macro-average below the source paper's 67.46%. This is
concrete evidence for why the authors self-retracted.

### Parts directly useful for Pebble

1. **The rule-fusion baseline, stated exactly — [V-A].** The competitor our learned fusion must beat
   is: *text-verdict priority override → emotion fallback*, a hard decision tree, text-dominant,
   zero learned fusion parameters. Two properties matter for ViEmoSpeech: (a) it fuses **hard class
   labels**, not features/logits — it discards all cross-modal interaction and all confidence; (b)
   it is **text-first by construction** (text can veto; audio only decides among the residual
   cases). Our learned fusion (cross-attention / gated / query-based) should be positioned precisely
   as *soft, feature-level, jointly-trained* against this *hard, label-level, hand-ordered* rule.
2. **The "baseline number to beat" is empty — [V-A][V-G].** Because there is no end-to-end
   evaluation and the paper is withdrawn, ViEmoSpeech **cannot cite a fusion accuracy from vn-09**.
   The honest framing: vn-09 is the *architectural* baseline (rule fusion exists in the VN
   literature) but supplies **no quantitative bar**. The quantitative bars come from vn-08
   (arXiv:2604.01711, 86.6% / κ 0.857) and VNEMOS-line audio-only — not from here.
3. **The text branch is trained on the wrong register — [V-C].** PhoBERT-CNN is fit on **clean
   written ViHSD** and run on **PhoWhisper ASR output** with no domain adaptation and no
   noise-robustness treatment. This is exactly the ASR-noise gap V-C names. It is a *negative
   exemplar*: it shows what happens if you ignore the written↔ASR mismatch (and, in a tonal
   language, the high-arousal tone-swap errors — mày→máy — that flip meaning). ViEmoSpeech's V-C
   choice (PhoBERT vs ViSoBERT vs CafeBERT, trained/evaluated on ASR transcripts, tested against
   gold captions) directly fixes what vn-09 left unaddressed.
4. **The corpus/SER provenance chain — [V-G][V-H].** VNEMOS = **250 clips / 27 sources / 5 classes**
   is the concrete "small VN drama-sourced SER set" ViEmoSpeech's 3611-utt / 7-class + V/A + distress
   corpus supersedes. The 250-vs-3611 and 5-class-vs-7+V/A+distress deltas are the quantifiable
   corpus-design contribution, and vn-09 shows the ceiling of building *on top of* 250 clips: you
   can only borrow a pretrained model, you cannot do speaker-disjoint SER evaluation.
5. **Cascade error-propagation as a design warning — [V-A][V-B].** Five off-the-shelf stages in
   series (denoise → diarize → ASR → text-clf ‖ SER → rule) means errors compound and are never
   jointly optimised. This motivates ViEmoSpeech's **jointly-trained** audio+text fusion over a
   frozen cascade, and motivates keeping the audio branch (V-B) able to carry emotion even when ASR
   is wrong — the opposite of vn-09's text-veto ordering.

### How each part helps Pebble succeed

- **[V-A] Position the method paper's fusion ablation against a re-implemented vn-09 rule.** Concrete
  artifact: in the fusion experiment, include a **"rule-fusion" baseline row** that reproduces
  §2.6's logic on ViEmoSpeech labels (map: text-toxicity/negation override → emotion fallback), and
  show learned cross-attention/gated fusion beating it on macro-F1 and CCC. Because vn-09 gives no
  number, *we generate the baseline number ourselves* on our corpus — that is the fair, reproducible
  comparison, and it directly answers "does learned fusion beat the rule."
- **[V-C] Make the ASR-noise robustness an explicit experiment, not an assumption.** Artifact: train
  the text branch on **PhoWhisper transcripts** (not gold text) and evaluate on both ASR and gold
  captions; report the degradation. vn-09's train-on-clean / infer-on-ASR mismatch is the ablation's
  "naive" arm. Add a tone-swap stress slice (high-arousal utterances where mày/tao mis-transcribe)
  to quantify the phonation-channel confound the profile predicts.
- **[V-G] Do not report a vn-09 fusion accuracy; report its absence.** Artifact: the eval-protocol
  doc's baseline table lists vn-09 as *"rule fusion, no end-to-end eval, withdrawn"* and draws the
  numeric baselines from vn-08 and VNEMOS-line audio-only. This keeps ViEmoSpeech's comparison
  honest and avoids inheriting retracted numbers.
- **[V-H] Use the 250→3611 clip and 5→7+V/A+distress jumps as the stated corpus contribution.**
  Artifact: `docs/spec/capabilities/` corpus card cites VNEMOS-250 as the prior VN drama-SER ceiling
  and positions ViEmoSpeech's size/label-richness/speaker-disjoint-split/tone-annotation as the
  delta.
- **[V-B] Keep the audio branch load-bearing.** Artifact: in the fusion, avoid a text-veto ordering;
  use a symmetric learned fusion so the audio branch (WavLM/emotion2vec + phonation features) can
  override text when ASR is unreliable — the exact failure vn-09's text-priority rule cannot handle.

### Child mental-health lens

- **Domain is adult call-centre service quality, not child affect.** vn-09's *distress* proxy is
  "customer had a bad experience → Offensive grade" — a commercial-satisfaction construct, not a
  clinical or child-safety one. Transfer to ViEmoSpeech's **distress head is essentially nil at the
  label level**; only the *architecture* (VN ASR + VN text encoder + SER) transfers. State plainly:
  vn-09 corroborates that PhoWhisper+PhoBERT+SER is a workable VN stack, and **nothing about how to
  score distress in acted child-facing drama**.
- **Recall floor: vn-09 does the opposite of what ViEmoSpeech needs.** Its text branch has
  catastrophic recall on the minority classes it cares about (OFFENSIVE R 41.8%, HATE R 30.9% —
  ≈/✖ given the internal inconsistency), i.e. it *misses* most of the harmful cases while boasting
  86% accuracy. For a recall-floored distress head this is the anti-pattern: accuracy on an
  imbalanced set hides minority-class misses. ViEmoSpeech's V-F recall-floor objective exists
  precisely to avoid this failure.
- **Tone treatment: none.** vn-09 has no tone annotation and no awareness that VN lexical tone is
  phonation-heavy; it applies a written-text hate classifier to ASR output where high-arousal
  tone-swaps corrupt exactly the toxic/negation words the rule keys on. For child speech (higher
  pitch, more variable prosody) this ASR fragility would be worse, reinforcing why ViEmoSpeech
  annotates syllable tone and does not let text unilaterally veto (V-D).
- **Ethics/framing note.** vn-09 grades and stores judgements about individuals ("Offensive")
  from call audio with no consent/annotation-quality discussion. ViEmoSpeech's acted-drama,
  feature-only, CC-BY release and honest "acted proxy ≠ clinical" framing is the responsible
  contrast to draw.

### Limitations & open questions for Pebble

- **Contradiction / gap #1 (vs the paper's own status):** the direct architectural baseline is
  **self-retracted for "significant inaccuracies,"** and its only numbers are **internally
  inconsistent** (CLEAN recall 36.71% cannot co-exist with 86.14% accuracy on ~82%-CLEAN ViHSD).
  ViEmoSpeech therefore **must not** quote a vn-09 fusion metric as a bar; it can only cite the
  *design* (rule fusion) and must generate the comparison number itself.
- **Contradiction / gap #2 (vs ViEmoSpeech's tone×emotion thesis):** vn-09 is **text-priority**
  (text can unconditionally veto the emotion stream). ViEmoSpeech's core claim is the **opposite** —
  in a tonal, phonation-heavy language the audio/prosody channel is *more* load-bearing and ASR text
  is *less* trustworthy under high arousal. The two designs encode contradictory priors about which
  modality to trust; our method paper should make that disagreement explicit and settle it
  empirically (fusion ablation, ASR-noise slice).
- **Contradiction / gap #3 (vs vn-08 / vn-10 quantitatively):** vn-09 supplies **no SER or fusion
  accuracy at all**, while vn-08 (arXiv:2604.01711) reports 86.6% / κ 0.857 and vn-10 reports SER on
  VNEMOS. vn-09 cannot be placed on the same axis — a gap in the baseline landscape that
  ViEmoSpeech's own re-implemented rule-fusion row must fill.
- **Open question:** is the **VNEMOS 250-clip set** obtainable (license/gate) so ViEmoSpeech can run
  a *cross-corpus* audio-only sanity check (train ViEmoSpeech → test VNEMOS-5-class subset)? The
  paper gives no availability terms; VNEMOS is ref [26] (ICDV 2024, IEEE) — likely gated. If
  unobtainable, VNEMOS stays a *citation-only* prior, not a comparison corpus.
- **Open question:** the rule's undefined **"Anxiety"** SER class (not in the 5-way head) suggests
  the pipeline was never actually run end-to-end — consistent with the withdrawal. Treat every vn-09
  operational detail as *unverified intent*, not measured behaviour.
