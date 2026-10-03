# Paper 03 — EAA: Emotion-Aware Audio LLMs with Dual Cross-Attention and Context-Aware Instruction Tuning

- **Authors:** Hongfei Du, Sidi Lu, Gang Zhou, Ye Gao
- **Venue / year:** Interspeech 2025 (pp. 5433–5437)
- **Links:** abs https://www.isca-archive.org/interspeech_2025/du25b_interspeech.html · PDF `pdfs/03-eaa-emotion-aware-audio-llm.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Dual cross-attention fuse luồng acoustic + semantic trong audio-LLM, instruction tuning theo context; motivation nêu rõ mental-health monitoring.

**Relevance to Pebble:** Reference kiến trúc sạch nhất cho một fusion layer cross-modal attention giữa audio và text.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

### Analysis — EAA (Emotion-Aware Audio LLM)
- **Profile used (voice-aware, assembled 2026-07-02):** text stream (NeoBERT ~250M, teacher-LLM silver labels, gold-holdout, ordinal) **+ active voice stream** (`voice-mtl-heads`: frozen WavLM-Large/emotion2vec SSL backbone → 3 heterogeneous heads emotion/affect-CCC/crisis-recall-floor, Kendall weighting; voice+text fusion is the forward direction).
- **Overlap:** D1=0, D2=1, D3=1, D4=0, D5=0, D6=0, D7=2 → **19%** (peripheral). Formula: (3·0 + 2·1 + 1·1 + 2·0 + 2·0 + 2·0 + 1·2)/26 × 100 = 5/26 × 100 = 19.2% ≈ 19%. **Supersedes the 2026-07-02 score of 12% computed against the stale text-only profile** (the lift is D7 0→2: HuBERT is a WavLM-class SSL speech encoder, a direct backbone-family match to the active voice stream).
- **Closest on:** D7 (frozen SSL speech-encoder backbone — HuBERT semantic + BEATs acoustic — is the same WavLM/emotion2vec-class family the voice stream uses) and D2/D3 (mental-health named as motivation; MELD is a 7-class categorical dialogue-emotion corpus overlapping the voice emotion head). Everything else — heterogeneous multi-task heads, continuous/affect + safety heads, LLM silver-label distillation, principled MTL loss balancing, crisis recall constraint — is absent (EAA is single-task categorical SER).
- **Best point (Design lesson):** The attention ablation settles a fusion-direction question for the voice+text roadmap — bidirectional **dual** cross-attention (0.687 acc) beats single-direction cross-attention (semantic-as-query 0.610, acoustic-as-query 0.671) and plain self-attention (0.675); *acoustic-as-query attending to semantic key/value* is the stronger single direction, and they concatenate the original un-fused features with the fused outputs to preserve modality-specific information (Eq. 4).
  - **How to apply to Pebble:** For the stated voice+text fusion step (after `voice-mtl-heads` lands), fuse the frozen-SSL voice features with the NeoBERT text stream via bidirectional dual cross-attention with a residual concat of original + fused streams — not a simple concat/linear projection — and default to acoustic/voice-as-query if forced to pick one direction. This is a near-term-relevant design choice now that voice is an active stream, not a deferred text-only footnote.
- **Caveats:** Full 5-page PDF read, no paywall — scores high-confidence. EAA is single-task (emotion word generated as LLaMA-3-8B text output, LoRA), so D1/D4/D5/D6 are genuinely 0; its "distillation" is an LLM producing labels directly, not a teacher silvering data for a small encoder. Mental-health is motivation only; evaluation is MELD (TV-show dialogue SER), not a clinical/crisis corpus. Value remains a fusion-architecture reference for the bimodal roadmap; the fusion sits inside audio (acoustic↔semantic), whereas Pebble's fusion is voice↔text, so the mechanism transfers but the modality pairing differs.

## Deep research — full-PDF read (2026-07-10)

> Read against the **current ViEmoSpeech profile + Decision Register V-A…V-H**
> (`docs/tasks/paper-deep-analysis.md`), which supersedes the stale text-stream
> D-x block in the deep-read agent definition **and** the "Analysis (overlap with
> Pebble)" section above (voice-aware 2026-07-02 profile). This section moves
> **V-A** (fusion-architecture template), **V-C** (text-branch / cross-attention
> over the LLM channel), and **V-F** (distress/mental-health framing honesty).

### Source-access note

- **Local PDF read in full** via `pdftotext "docs/papers/bimodal-ser/pdfs/03-eaa-emotion-aware-audio-llm.pdf" -`
  (method §3, all three result tables, ablations §4.3, references). The local PDF
  **is the published venue version** — the ISCA proceedings footer prints
  `10.21437/Interspeech.2025-1232`, pages 5433–5437, and the DOI resolves. There
  is no separate preprint delta to reconcile.
- **Web-validated** against the ISCA archive landing page: authors (Du, Lu, Zhou,
  Gao, William & Mary), venue (Interspeech 2025, Rotterdam), pages 5433–5437, the
  headline **"improving accuracy by 11.4%"**, and the abstract sentence naming
  **"mental health monitoring"** as motivation.
  - Query: `EAA Emotion-Aware Audio Large Language Models Dual Cross-Attention Context-Aware Instruction Tuning Interspeech 2025 MELD 68.7%`
  - Resolved URL: https://www.isca-archive.org/interspeech_2025/du25b_interspeech.html
    (+ PDF mirror https://www.isca-archive.org/interspeech_2025/du25b_interspeech.pdf)
- **Status tags:** Table 1 / Table 2 / Table 3 numbers are in the extracted body
  text → ✔ corroborated. **Figure 2** (attention-mechanism comparison) is a bar
  chart; its per-bar values do **not** appear in the extractable text — the
  0.610 / 0.671 / 0.675 figures quoted in the older "Analysis" block above were
  read off the plot → tagged ≈ approximate here.

### What the paper actually does

**Task.** Single-task categorical speech-emotion recognition, framed as *text
generation*: an audio-LLM emits one emotion word. Evaluated on **MELD** (Friends
sitcom dialogue; 7 classes neutral/joy/sadness/anger/fear/disgust/surprise;
13,847 utterances, 407 speakers, 12.2 h English; §4.1) using **accuracy only**.

**Architecture (§3, Fig. 1).** Two frozen-ish audio encoders feed a *dual
cross-attention* fusion block, whose output plus a text instruction and one line
of dialogue context is consumed by a LoRA-tuned LLaMA-3-8B that generates the
emotion word.
- Semantic encoder `f_s` = **HuBERT**; acoustic encoder `f_a` = **BEATs**
  (Eq. 1: `S = f_s(x) ∈ R^{Ts×ds}`, `A = f_a(x) ∈ R^{Ta×da}`). Both encoders are
  **frozen except their last two layers**, which are fine-tuned (§4). Note both
  branches are derived from the **same audio signal** — "semantic" here means
  HuBERT's linguistic-ish SSL features, **not** a text/LLM embedding.
- Linear projection to a shared dim `d` + LayerNorm (Eq. 2); sequences aligned by
  **zero-padding the shorter to `T = max(Ts, Ta)`** so attention is temporally
  aligned.
- **Dual cross-attention (Eq. 3):** `Att_s = Softmax(Q_s K_a^T / √d) V_a` (semantic
  queries acoustic) and `Att_a = Softmax(Q_a K_s^T / √d) V_s` (acoustic queries
  semantic).
- **Residual concat fusion (Eq. 4):** `F = Concat(S̃, Ã, Att_s, Att_a)` — the
  original un-fused projections are kept alongside the two attended streams, then
  projected into LLaMA's hidden space.
- **Context-aware instruction tuning (§3.2):** for utterance `x_t`, prepend its
  immediately preceding utterance `x_{t-1}` in the same dialogue (`C_t = x_{t-1} ⊕ x_t`,
  Eq. 5); prompt = *"Describe the speaker's emotion in one word."*
- **Tuning config (§4):** LoRA rank 2, α 16, dropout 0.2, batch 2, hidden 768,
  AdamW lr 5e-6, linear warm-up → cosine decay, single H100, 16 kHz mono audio.

**Headline results.**
- **EAA MELD accuracy = 0.687** (Table 1) ✔ corroborated. Beats every listed
  ALLM: BLSP-Emo 0.573, OSUM 0.566, Qwen-audio 0.557, AffectGPT 0.557,
  Qwen2-audio 0.553, WavLM-large 0.542, WavLLM 0.411, Whisper+Llama3 0.334,
  SALMONN 0.331, MERaLiON 0.302, Pengi 0.289 (Table 1) ✔. The **"11.4%"** claim
  = 0.687 − 0.573 (vs BLSP-Emo, the strongest emotion-support ALLM) ✔ corroborated
  by abstract + venue page.
- **Traditional multimodal ERC methods (Table 2)** sit at 0.651–0.687; EAA (audio+text)
  ties the best, **ELR-GNN 0.687, which additionally uses video** ✔. EAA closes the
  ALLM-vs-classifier gap rather than exceeding SOTA classifiers.
- **Context ablation (Table 3):** audio-only (no text at all) **0.523** → current
  utterance text **0.667** → current + preceding **0.687** ✔. The single largest
  jump is adding *any* text context (+14.4 pp); the preceding sentence adds +2.0 pp.
- **Attention ablation (Fig. 2):** dual cross-attention **0.687** > self-attention
  **≈0.675** > acoustic-as-query single **≈0.671** > semantic-as-query single
  **≈0.610** ≈ approximate (figure-only). Takeaway they draw: acoustic-as-query is
  the stronger single direction; dual beats both single directions and self-attn.

### Parts directly useful for ViEmoSpeech (each tagged with Decision ID)

1. **Dual cross-attention + residual-concat fusion block (Eq. 3–4)** — a clean,
   citable *template* for V-A. Two projected streams, LayerNorm, bidirectional
   cross-attention (each modality queries the other), then **concat original +
   both attended** so nothing collapses. **[V-A]**
2. **Acoustic-as-query is the stronger single direction; dual is best (Fig. 2).**
   A concrete fusion-direction prior: if forced to pick, let audio query text; but
   run both. **[V-A]**
3. **Frozen backbone + last-2-layers-unfrozen + LoRA-on-LLM recipe (§4).** Trains
   a large audio-LLM stack on 12.2 h with H100-single-GPU budget by freezing the
   bulk. Directly supports V-B's frozen-backbone lean and a light unfreeze budget. **[V-B]**
4. **Context ablation quantifies the text channel's value (Table 3):** going from
   audio-only 0.523 to +text 0.667 is +14.4 pp — the biggest single lever in the
   whole paper. External quantitative support that the semantic/text branch carries
   heavy load, which is exactly ViEmoSpeech's tone×emotion thesis (text must carry
   more because F0 is tone-loaded). **[V-C, V-D]**
5. **Accuracy-only reporting on class-imbalanced MELD** — a *negative* template:
   MELD is neutral-heavy, and accuracy hides minority-class collapse. ViEmoSpeech
   must report macro-F1 (+ CCC for V/A, recall@floor). **[V-G]**
6. **"Mental health monitoring" named in abstract+intro, never operationalized**
   — evaluation is 100% sitcom emotion, zero clinical/distress label. Direct
   material for V-F's honest-proxy framing (see lens below). **[V-F]**

### How each part helps ViEmoSpeech succeed

- **V-A (fusion block).** Adopt Eq. 3–4 as one candidate learned-fusion arm in the
  method paper's fusion bake-off (against the rule-based PhoWhisper+PhoBERT prior
  attempt and the vn-07 FAS Q-Former arm): two frozen streams → project → LN →
  bidirectional cross-attention → **concat(original, Att_s, Att_a)**. The residual
  concat is the load-bearing detail — it is EAA's own safeguard against a modality
  collapsing, and it directly answers vn-12's "fusion collapses to the strong text
  encoder" worry. Default the *single-direction fallback* to **acoustic-as-query**.
- **V-A (alignment).** EAA's zero-pad-to-`T=max(Ts,Ta)` trick is the wrong recipe
  for us (see risk below) — for audio↔ASR-text use **cross-attention without forced
  temporal alignment** (text tokens as K/V, audio frames as Q, no padding), because
  there is no frame-to-token time correspondence. Cite EAA for the *block shape*,
  not the alignment step.
- **V-B (budget).** Copy the freeze-all-but-last-2 + LoRA pattern so the WavLM /
  emotion2vec backbone stays frozen and only a thin fusion head + light unfreeze
  trains on our ~18k-utt P1 corpus — a corpus far smaller than what a fully
  fine-tuned dual-encoder stack needs.
- **V-C (text branch).** Table 3's +14.4 pp from adding text is the citation that
  the semantic branch is not optional in dialogue SER — it motivates investing in a
  robust PhoBERT/ViSoBERT branch rather than an audio-only model. But because EAA's
  "semantic" branch is HuBERT (audio), **EAA does not itself validate cross-attention
  over a real text/LLM channel** — our design does something EAA doesn't, so cite it
  as motivation-for-text, not as a proven text-cross-attention result.
- **V-D.** Use EAA's context ablation as one more external data point that the
  non-F0/non-acoustic (linguistic) channel carries substantial emotion load in
  dialogue — consistent with (not proof of) our tone×emotion channel-competition
  claim.
- **V-F.** Name EAA in the method paper alongside vn-10 (Dynamic-CBAM) as the
  "mental-health-in-the-abstract, sitcom-emotion-in-the-eval" pattern our
  acted-drama-distress-proxy framing explicitly refuses to repeat.
- **V-G.** Report macro-F1 (not accuracy) so a neutral-heavy corpus can't inflate
  the headline the way MELD-accuracy can.

### Child / distress mental-health lens (ViEmoSpeech transfer validity)

- **"Mental health" is motivation-only, and even weaker than a distress proxy.**
  The phrase "mental health monitoring" appears exactly in the abstract and intro
  as one of three application slots (HCI / mental-health / customer service, §1
  refs [1–3]); there is **no distress label, no clinical anchor, no affect/valence
  dimension** anywhere in the method or eval. The entire evaluation is MELD — acted
  US-sitcom (*Friends*) dialogue, 7 categorical emotions. For V-F this is the clean
  anti-pattern: a paper can invoke mental health for salience while its measurable
  claim is ordinary categorical SER. ViEmoSpeech's distress flag must therefore be
  framed as an **acted-drama proxy with a recall-floor objective**, explicitly not
  a clinical construct — and EAA is the citation for why that honesty is needed.
- **Acted, English, non-tonal — most transfer risk sits in the modality pairing,
  not the register.** MELD is acted (like our TV-drama source, so the acted-proxy
  register is a *fair* analogue), but (a) English & non-tonal → nothing about
  tone×emotion or VN phonation transfers; (b) the fusion is **intra-audio**
  (HuBERT-semantic ↔ BEATs-acoustic, both from the same waveform), whereas ours is
  **cross-source** (WavLM audio ↔ PhoBERT over noisy PhoWhisper ASR). EAA never
  confronts ASR noise or tone-swap errors (mày→máy). The mechanism transfers; the
  input regime does not.
- **Frozen backbone is an asset for the child/proxy setting**, where labels are
  scarce and we cannot risk a large stack overfitting a small acted corpus — EAA
  shows a competitive result is reachable with the bulk frozen.
- **Ethics note.** EAA makes no consent/data-governance statement (MELD is a public
  academic corpus). It is not a data-governance template — our media-legality
  constraint (features+timestamps+labels only) has no analogue here.

### Limitations & open questions for ViEmoSpeech (contradictions/gaps)

- **GAP vs V-C / the older "Analysis" block — EAA's cross-attention is over an
  audio channel, not a text/LLM channel.** The compact entry above sells EAA as
  "the cleanest reference for a cross-modal attention fusion layer between audio and
  text." Reading the method, the cross-attention runs between **HuBERT and BEATs —
  two audio encoders**; the only *text* in the system is the LLaMA prompt +
  preceding-utterance context, which is **not** cross-attended, just concatenated
  into the LLM input. So for V-C (cross-attention *over the text/LLM channel*), EAA
  is a **weaker template than claimed**: it demonstrates the block, not the
  audio↔text application. This is the ≥1 required contradiction/gap.
- **CONTRADICTION vs V-F / vn-10 parallel:** EAA repeats Dynamic-CBAM's move —
  invoke a clinical application, evaluate on acted categorical emotion — but goes
  further (no distress/affect head at all). Both are anti-patterns our distress-head
  spec should name.
- **Zero-pad temporal alignment (§3.1) is unsound for audio↔ASR-text.** EAA can pad
  to `T=max(Ts,Ta)` because both streams are time-indexed audio at 16 kHz; PhoBERT
  subword tokens have no frame-time correspondence to WavLM frames, and forcing one
  would inject spurious alignment. Open question: replace with length-agnostic
  cross-attention (text as K/V, no padding) and measure whether the residual-concat
  benefit (Eq. 4) survives without temporal alignment.
- **Accuracy-only on imbalanced MELD hides minority collapse** — same red flag as
  vn-07 FAS (0 correct fear/disgust) and MELD's known neutral dominance. EAA gives
  us no per-class or macro number, so its 0.687 is **not** a comparable bar for our
  speaker-disjoint macro-F1 protocol (V-G). Also note EAA reports **no
  speaker-disjoint claim** — MELD's standard split is used but speaker overlap
  across MELD splits is a known issue, so 0.687 may be leak-influenced (uncheckable
  from the paper).
- **Consistency check vs vn-12 (semantics dominate / SLMs collapse to text).** EAA's
  acoustic-as-query > semantic-as-query result (Fig. 2, ≈0.671 vs ≈0.610) is *mild
  evidence for audio-anchoring* and thus consistent with vn-12's proposed safeguard
  (aux audio-only head / modality dropout) — but Table 3's +14.4 pp text jump shows
  the text channel still carries most of the lift on MELD. Net: fuse, but regularize
  the text branch and keep an audio anchor — the same conclusion both papers push us
  toward, on a corpus (MELD) with weak, English, non-tonal audio.
