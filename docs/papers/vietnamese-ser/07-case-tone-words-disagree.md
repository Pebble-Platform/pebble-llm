# Paper vn-07 — When Tone and Words Disagree: Robust SER under Acoustic-Semantic Conflict (CASE / FAS)

- **Authors:** (not yet extracted — verify from PDF)
- **Venue / year:** arXiv preprint, Jan 2026
- **Links:** abs https://arxiv.org/abs/2601.04564 · PDF `pdfs/07-case-tone-words-disagree.pdf`
- **Group:** vietnamese-ser / closest architectural competitor

**Summary:** Introduces CASE, a dataset dominated by cases where paralinguistic
tone-of-voice contradicts lexical/semantic content, and a Fusion
Acoustic-Semantic (FAS) model that disentangles acoustic and semantic pathways
via query-based attention; beats ASR-based/SSL/audio-LLM baselines (59.38% on CASE).

**Relevance to ViEmoSpeech:** The single closest architectural competitor —
must cite-and-distinguish: their "tone" is paralinguistic tone-of-voice, NOT
phonemic lexical tone in a tonal language. Also a candidate fusion template (V-A).

> Stub created 2026-07-10 (task `docs/tasks/paper-deep-analysis.md`); deep-read pending.

## Deep research — full-PDF read (2026-07-10)

### Source-access note

Read the full local PDF via `pdftotext "docs/papers/vietnamese-ser/pdfs/07-case-tone-words-disagree.pdf" -`
(all pages of body + Tables 1–7, ablations, appendix case studies and confusion-matrix
discussion). The PDF is `arXiv:2601.04564v1 [cs.SD], 8 Jan 2026` — a very recent preprint with
**no published/venue version yet**, so the arXiv v1 is the authoritative source (nothing to
reconcile). Web-validated the load-bearing facts against the arXiv abstract/HTML:
- Query `"When Tone and Words Disagree" FAS CASE ... arXiv 2601.04564` → resolved
  https://arxiv.org/abs/2601.04564 and https://arxiv.org/pdf/2601.04564 — confirms title, the
  FAS/CASE framing, and the **59.38% CASE SOTA** headline; GitHub `github.com/24DavidHuang/FAS`.
- Fetched https://arxiv.org/html/2601.04564v1 → confirms **CASE languages = "English, Mandarin,
  and representative Chinese dialects"**; **"tone" = paralinguistic tone-of-voice/prosody, not
  phonemic/lexical tone**; TTS engine = Doubao-Seed-TTS 2.0; 378 samples; 7 emotions; best
  hyperparameters `k_aco=8, k_sem=16, N_q=2, d=512`. (This is the V-D novelty-defense fact.)

Full author list (stub lacked it): **Dawei Huang(1,2), Yongjie Lv(1), Ruijie Xiong(1), Chunxiang
Jin(1), Xiaojiang Peng(2)\*** — (1) Inclusion AI, Ant Group; (2) Shenzhen University; \*corresponding
author (Xiaojiang Peng). ✔ corroborated (arXiv author block).

### What the paper actually does

**Problem.** Standard SER assumes acoustic–semantic *congruence* (a happy sentence said in a happy
voice). The paper targets *conflict* cases — sarcasm, cold fury, polite masking — where prosody
contradicts the literal words, and shows SOTA SER (SSL, ASR/semantic encoders, and audio-LLMs) all
degrade sharply because they carry either a semantic bias or entangled acoustic⊗semantic features.

**FAS framework** (§3.1, Fig. 1) — two frozen pathways + a lightweight learned fusion head, trained
on *pre-computed* features (encoders never fine-tuned):
- Semantic pathway = **Whisper-large encoder**, 1280-d features. Acoustic pathway =
  **MingTok-Audio** neural audio tokenizer (a TTS-derived codec), 64-d features. ✔ (§4.2)
- **Patchify** each stream by downsample factor `s=5`, project to unified `d=512` (Eq. 1). ✔
- **Token distillation** (Eq. 2–3): saliency score `s_t = ||f_t||_2` (L2-norm as an energy proxy);
  **Top-K** keeps the most salient tokens per stream, asymmetric budgets `k_aco`, `k_sem`. ✔
- **Learnable queries** `Q_learn ∈ R^{n×d}` (Q-Former-style) cross-attend the concatenated distilled
  context: `F_fused = Attn(Q_learn, C·W_K, C·W_V)` (Eq. 4) → MLP → 7-way softmax. ✔ (§3.1)
- Config (Table 3): `d=512`, `N_q=2`, dropout 0.4, AdamW, LR `2e-4`, cosine schedule, weight decay
  `1e-4`, global batch 2048, CE loss, 100 epochs, warmup 0.05, 16 kHz, seed 42, 8×A6000. ✔
- Parameter count: **FAS 3.45M** (vs Concat 1.22M, Gated 1.65M, w/o-Qlearn 0.82M). ✔ (Table 4)

**CASE benchmark** (§3.2, Fig. 2). A *diagnostic* zero-shot testbed of **378** human-verified
conflict utterances, 7 emotions. Built by: Gemini-2.5-pro drafts a conflict scenario + an
emotion-laden text (semantic anchor); a **ground-truth acoustic emotion is deliberately chosen to
contradict** the text's semantic emotion; a timbre is drawn from **21 multi-emotion voices**;
**Doubao-Seed-TTS 2.0** synthesizes the audio; **12 expert annotators** discard samples whose acoustic
prosody is weak/ambiguous/overshadowed. Fully **synthetic, no PII** (Ethics §). Original utterances
are **Chinese** (Appendix Table 7 lists English glosses); language coverage = English + Mandarin +
Chinese dialects. ✔ (§3.2, Limitations, Appendix A.3)

**Training corpus** = ~66 h aggregated open SER sets: IEMOCAP, CMU-MOSEI, MER2024, MELD, RAVDESS, ESD
(Table 1). In-domain test = MELD/RAVDESS/ESD; zero-shot = CASE, Emo-Emilia (Mandarin), EMOVO
(Italian), EmoDB (German). ✔

**Headline results** (Table 2, ACC/F1):

| Model (paradigm) | CASE (zero-shot) | MELD | RAVDESS | ESD |
|---|---|---|---|---|
| Whisper (semantic) | 47.26 / 44.97 | 49.59 / 43.62 | 62.30 / 60.61 | 84.53 / 83.92 |
| WavLM (SSL) | 34.20 / 33.92 | 52.99 / 53.57 | 44.64 / 34.09 | 61.90 / 60.69 |
| Emotion2Vec (SOTA SER) | 31.48 / 28.42 | 45.04 / 45.49 | 70.06 / 68.84 | 51.39 / 50.87 |
| Qwen2.5-Omni (ALM) | 34.66 / 30.21 | 54.06 / 36.05 | 75.35 / 74.98 | 51.60 / 35.70 |
| **FAS (Ours)** | **59.38 / 55.08** | 51.89 / 48.42 | 76.61 / 76.19 | 87.27 / 86.72 |

All ✔ (Table 2). In-domain avg ACC **71.92%**; zero-shot avg ACC **54.66%**. ✔ Note the semantic
encoder (Whisper, 47.26) is the *strongest baseline on CASE* — even in "conflict" data, a
semantics-heavy model beats SSL/ALMs; FAS's +12 pt gain over Whisper is the real claim.

**Ablations.** (a) Fusion strategy on CASE ACC (Table 4): Concat 53.65 < Gated 53.12 < w/o-Top-K
55.47 < w/o-Qlearn 55.99 < **FAS 59.38**; removing Top-K costs −3.91 ACC on CASE, removing Qlearn
costs **−9.27 ACC on RAVDESS**. ✔ (b) Token budgets (Table 5): best avg 62.06% ACC at
`k_aco=8, k_sem=16` — **asymmetric, more semantic than acoustic tokens is better**; enlarging `k_aco`
gives marginal/negative gains. ✔ (c) `N_q` saturates at **2** (Fig. 4); "SER is a low-complexity
utterance-level task, minimal query capacity suffices." ✔ (d) Plug-and-play across encoders (Table
6): MingTok+Whisper best on CASE; Whisper+XCodec2 best MELD; Whisper+VibeVoice best RAVDESS; CLAP as
the semantic branch underperforms Whisper. ✔ (e) Confusion matrices (Appendix A.2.3):
**"no method correctly predicts any samples of fear or disgust" on CASE** — the rare/high-conflict
classes fully collapse even for the SOTA. ✔

### Parts directly useful for ViEmoSpeech (tagged with Decision IDs)

1. **[V-D — THE novelty-defense fact]** CASE's "tone" is **paralinguistic tone-of-voice (prosody)**,
   explicitly *not* phonemic/lexical tone; languages are English + Mandarin + Chinese dialects, and
   even though Mandarin is tonal the paper **never studies lexical-tone×emotion channel competition** —
   its conflict is prosody-vs-semantics (sarcasm/masking) in **synthetic TTS** speech. ✔
   *Transfer risk: none — this is a citation, not a method to reuse.* This is the clean cite-and-
   distinguish: ViEmoSpeech's headline (Vietnamese lexical tone is phonation-heavy and shares the
   F0/phonation channel emotion uses) is **untouched** by CASE. CASE is the closest-named competitor
   yet operates in an orthogonal problem space; ViEmoSpeech's novelty claim survives intact.

2. **[V-A — fusion architecture template]** The FAS two-pathway + Q-Former distillation head:
   frozen-encoder, pre-computed features, `d=512`, Top-K L2-saliency token selection with **asymmetric
   budgets** (`k_sem=16 > k_aco=8`), `N_q=2` learnable queries, 3.45M trainable params, CE loss.
   *Transfer risk: MEDIUM-HIGH.* The **shape** (cheap learned fusion over two frozen streams) transfers
   and directly answers V-A ("beat the rule-based PhoWhisper+PhoBERT baseline"). But two components do
   **not** transfer as-is: (i) MingTok-Audio is a **Mandarin/English TTS codec** — no evidence it
   tokenizes Vietnamese *phonation/tone* cleanly; ViEmoSpeech's V-B candidates (WavLM / emotion2vec /
   phonation features) are the natural acoustic stream. (ii) FAS's semantic stream is **Whisper-encoder
   features**, not a text-LM over an ASR transcript — ViEmoSpeech's text branch is PhoBERT/ViSoBERT
   over a **PhoWhisper transcript** (V-C), so the "semantic pathway" is a different object.

3. **[V-A / V-B — the asymmetric-budget + saliency finding]** "Preserving more *semantic* tokens is
   more beneficial than more acoustic tokens" (Table 5, `k_sem=16>k_aco=8`), and L2-norm saliency
   (energy proxy) beats random/uniform token selection by up to 3.91 ACC. ✔
   *Transfer risk: MEDIUM and directionally interesting.* This is empirical evidence that, even for a
   task framed around *acoustic* conflict, the semantic stream should carry more capacity — which
   **rhymes with** ViEmoSpeech's own thesis that in a tonal language the text/semantic branch "must
   carry more load." But CASE's semantics are clean (ground-truth text → Whisper); under PhoWhisper
   tone-swap noise the ViEmoSpeech semantic stream is *corrupted precisely at high arousal*, so the
   "more semantic tokens" prescription may invert. Worth an explicit ablation, not a copy.

4. **[V-G — conflict-case evaluation design]** CASE's construction protocol: deliberately engineer a
   ground-truth acoustic emotion that **contradicts** the text's semantic emotion, then **discard any
   sample whose acoustic emotion is not clearly perceptible** (12-expert gate). Reported as a
   *zero-shot diagnostic slice*, separate from in-domain metrics; both ACC and unweighted-avg F1
   reported. ✔ *Transfer risk: LOW as a design pattern, but CASE-the-dataset does not transfer*
   (synthetic Chinese/English, no Vietnamese, no ASR). The reusable idea is a **held-out conflict
   sub-slice** with its own metric line.

### How each part helps ViEmoSpeech succeed

- **V-D → the paper's positioning paragraph writes itself.** In the ViEmoSpeech method paper, cite
  CASE as the state of the art on *paralinguistic* acoustic-semantic conflict and distinguish in one
  sentence: "Unlike CASE, whose 'tone' is prosodic tone-of-voice over synthetic English/Mandarin
  speech, ViEmoSpeech studies **phonemic lexical-tone×emotion channel competition** in natural
  Vietnamese TV-drama speech." Concrete artifact: the Related-Work / novelty paragraph and the
  `docs/project-overview.md §1.3` competitor table. This closes the biggest reviewer objection
  ("isn't this just CASE?") with a factual, checkable distinction.

- **V-A → a concrete fusion baseline to build and beat.** Implement FAS-lite as one arm of the fusion
  bake-off: two frozen streams (swap MingTok→WavLM/emotion2vec for the Vietnamese acoustic stream;
  swap Whisper→PhoBERT-over-PhoWhisper for the semantic stream), Top-K L2 saliency distillation,
  `N_q=2` learnable queries, CE + the V/A regression + distress heads bolted on the fused vector.
  Because encoders stay frozen and features are pre-computed, this is a **cheap** experiment (3.45M
  trainable params, single-GPU) — exactly the kind of learned-fusion candidate V-A needs against the
  rule-based 2412.09829 baseline. Artifact: a `fusion=fas` config in the SER training script.

- **V-A/V-B → set the token-budget prior from their ablation.** Start the ViEmoSpeech fusion head at
  `k_sem ≥ k_aco` and `N_q=2` (their saturation point) rather than sweeping blind — their Table 5/Fig 4
  give a defensible initialization and save compute. Then run the *inverted* ablation: does the
  semantic-heavy budget still win when the semantic stream is PhoWhisper-noisy? That ablation is a
  publishable result that directly tests the ViEmoSpeech tone×emotion thesis (V-D quantification).

- **V-G → add a "conflict slice" to the eval protocol.** ViEmoSpeech TV-drama naturally contains
  sarcasm/masking; mark a held-out **acoustic-semantic-conflict sub-slice** (human-labeled emotion ≠
  the emotion a text-only PhoBERT predicts from the transcript) and report macro-F1 / CCC on it as a
  separate line, à la CASE's zero-shot column. Artifact: a `conflict_subslice` flag in the gold
  held-out series, reported next to the overall numbers in `docs/tasks/vn-tv-ser-pilot.md`.

### Transfer-validity & ethics lens (ViEmoSpeech regime)

- **Register/language mismatch is total, and that is the point.** CASE = synthetic (Doubao-TTS),
  acted-by-design, English/Mandarin, no ASR in the loop (Whisper *features*, not noisy transcripts),
  7-class softmax only — no valence/arousal, no distress. ViEmoSpeech = natural Vietnamese TV-drama,
  PhoWhisper transcripts with **tone-swap errors at high arousal** (mày→máy, tao→tháo), 7-class + V/A
  (Russell 1–5, CCC) + a recall-floored distress flag. So FAS's numbers are **not comparable bars**;
  only its *architecture* and *ablation priors* transfer.
- **FAS's "trust the acoustics under conflict" heuristic is dangerous in a tonal language.** FAS
  resolves conflict by prioritizing the acoustic pathway (Fig. 5 case study: "Trust Acoustic"). In
  Vietnamese the acoustic channel (F0/phonation) is **shared** between lexical tone and emotion — so
  "trust acoustics" cannot be a blanket arbitration rule; the same F0 excursion can be a tone contour
  *or* an affect cue. ViEmoSpeech's fusion must *jointly* resolve, not default to one modality. This is
  a design-level warning, not a number to reuse.
- **Synthetic vs. natural distress ethics.** CASE sidesteps consent by being fully synthetic; its
  ethics section warns SER "could be deployed in surveillance… interrogation." ViEmoSpeech uses real
  (copyrighted) TV-drama speech under the features-only release constraint and an explicitly honest
  **distress = acted-drama proxy, not clinical** framing — a *different* ethical posture that
  ViEmoSpeech already documents; CASE offers the misuse-warning language worth echoing.
- **Rare-class collapse is a red flag for the distress head (V-F).** On CASE **no model** predicts any
  fear or disgust sample correctly (Appendix A.2.3) — the rare, high-conflict classes vanish under a
  flat CE objective. ViEmoSpeech's distress flag is exactly such a rare, high-stakes class; this is
  direct evidence that a plain-CE fused head will **not** meet a recall floor, motivating the
  V-F recall-floor loss / threshold policy rather than trusting the softmax.

### Limitations & open questions for ViEmoSpeech

- **Contradiction/gap vs. ViEmoSpeech's core thesis (V-D).** CASE claims to study "tone vs words" yet,
  by including *Mandarin* (a tonal language) and still treating "tone" purely as prosody, it
  **demonstrates the gap ViEmoSpeech fills**: nobody in the closest competitor line has quantified
  *lexical-tone×emotion* channel competition. FAS's own best config (more semantic tokens than
  acoustic, Table 5) even suggests the acoustic stream is *less* separable than assumed — consistent
  with the ViEmoSpeech hypothesis that tone and emotion are entangled in the same acoustic channel and
  the text branch must compensate. ViEmoSpeech should cite this as *supporting evidence*, not a rival.
- **Contradiction vs. vn-12 (Incongruent-SLM "semantics dominate") and vs. FAS.** FAS asserts the
  *acoustic* channel should win under conflict and engineers CASE so acoustic emotion is ground truth;
  vn-12 reports SLMs default to *semantics*. These frame opposite arbitration priors. ViEmoSpeech sits
  between them and cannot adopt either as a rule, because in Vietnamese the acoustic F0/phonation
  channel is *itself semantically loaded* (it carries lexical tone). Open question: does a learned
  fusion (FAS-style) implicitly learn a per-utterance arbitration that beats both fixed priors on
  Vietnamese conflict cases?
- **No ASR-noise robustness anywhere in FAS.** FAS's semantic stream is clean Whisper features from
  ground-truth text; it never confronts transcription error. ViEmoSpeech's headline failure mode —
  PhoWhisper tone-swap at high arousal — is *outside* FAS's evaluated regime. Whether the Top-K
  saliency + Q-Former head is robust to a corrupted semantic stream is untested and is a genuine
  ViEmoSpeech-owned experiment (ties V-A × V-C).
- **CASE is 378 synthetic samples, diagnostic-only** (the authors' own Limitation: "insufficient in
  scale to serve as standalone training data," ✔). It cannot be a ViEmoSpeech training or fine-tuning
  source, and its acted-TTS distribution is far from spontaneous TV dialogue — usable as a *conceptual*
  eval-design template only.
- **Acoustic tokenizer portability is unverified for Vietnamese.** MingTok-Audio / XCodec2 / VibeVoice
  are TTS codecs trained on (largely) English/Mandarin; there is no evidence they preserve Vietnamese
  tone/phonation detail. Before adopting FAS's acoustic pathway, ViEmoSpeech must verify (V-B) whether
  a TTS codec or a phonation-aware SSL (WavLM/emotion2vec + jitter/shimmer/HNR/H1–H2) better retains
  the tone-emotion channel — the very signal ViEmoSpeech is built to measure.
