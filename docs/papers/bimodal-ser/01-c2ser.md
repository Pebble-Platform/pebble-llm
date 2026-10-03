# Paper 01 — C²SER: Steering Language Model to Stable Speech Emotion Recognition via Contextual Perception and Chain of Thought

- **Authors:** Zhixian Zhao, Xinfa Zhu, Xinsheng Wang, Shuiyuan Wang, Xuelong Geng, Wenjie Tian, Lei Xie
- **Venue / year:** IEEE TASLP, 2025
- **Links:** abs https://arxiv.org/abs/2502.18186 · PDF `pdfs/01-c2ser.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Audio-LLM SER kết hợp Whisper (semantic) + **emotion2vec-S** (acoustic), dùng chain-of-thought + self-distillation để ổn định phân loại cảm xúc.

**Relevance to Pebble:** emotion2vec là audio backbone Pebble đã chọn — đây là reference kiến trúc trực tiếp cho việc nhúng nó vào pipeline có LLM teacher/distillation.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

### Analysis — C²SER
- **Profile assembled at analysis time** (intent + capabilities, not the stale text-only snapshot): Pebble = primary **ordinal suicide-risk text** program (NeoBERT ~250M, Gemini silver labels, honest gold-holdout eval; ordinal-aware QWK/MAE; ethics + reproducibility) **plus an active adjacent voice stream** (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`): a **frozen WavLM-Large / emotion2vec backbone** + shared trunk carrying **three heterogeneous heads** — emotion (CE), affect valence+arousal (**continuous, CCC loss**), crisis (BCE under a **hard recall floor 0.90**) — balanced by **Kendall uncertainty weighting**, currently on proxy labels with **MSP-Podcast (A/V/D)** and **DAIC (crisis)** as the next real-label targets. Backbone fine-tune is an explicit non-goal (features stay frozen).
- **Supersedes the 2026-07-02 score of 31% computed against the stale text-only profile.**
- **Overlap:** D1=0, D2=0, D3=1, D4=2, D5=1, D6=0, D7=2 → (Σ wᵢ·scoreᵢ = 3·0+2·0+1·1+2·2+2·1+2·0+1·2 = 9) / 26 × 100 = **35% (peripheral)**
- **Closest on:** D7 (Emotion2Vec-S is a released extension of **emotion2vec — the voice stream's actual frozen backbone**, and the paper also benchmarks WavLM) and D4 (dual-teacher intersection silver-labeling + explicit→implicit self-distillation).
- **Best point (Method to adopt):** C²SER's **Emotion2Vec-S** adds a **category-level contrastive loss** on top of emotion2vec's utterance/frame losses and, per Table V, consistently beats plain Emotion2Vec and WavLM-base on emotion accuracy across Chinese/English/multilingual test sets — and its checkpoint is publicly released.
  - **How to apply to Pebble:** swap the voice stream's frozen feature extractor to the released **Emotion2Vec-S** checkpoint for the emotion head — a drop-in upgrade that respects the "backbone stays frozen" non-goal (no fine-tune), needs no architecture change to the 3-head MTL probe, and is testable in the pending `pebble-voice-mtl-heads` Kaggle run as an A/B against the current emotion2vec features.
- **Caveats:** Single-task **categorical** SER via a generative ALM — **no** heterogeneous heads (D1=0), **no** continuous/ordinal or crisis-recall objective (D5 loss balancing is hand-tuned λ_utt=0.1 / λ_cate=100, explicitly **not** Kendall/GradNorm → D5=1 partial only; D6=0), and **no** mental-health/crisis domain (D2=0). D3=1 partial: it trains on real speech-emotion corpora incl. **MSP-Podcast** (a voice-stream target), but uses them as flat categorical SER, not continuous affect. The Emotion2Vec-S swap and the dual-teacher gate transfer to the **voice** stream and the **text** silver-label stage respectively; neither touches the NeoBERT architecture. Scored from pp. 1–8 (abstract, related work, full method, data prep, experiment setup, Table V results); ablation tables were skimmed and do not affect the dimension scores.

## Deep research — full-PDF read (2026-07-10)

> Read against the **published IEEE TASLP** version (DOI 10.1109/TASLPRO.2025.3648793; the
> arXiv:2502.18186 Comments field states "This work has been published in IEEE Transactions on
> Audio, Speech and Language Processing"). Local PDF = `pdfs/01-c2ser.pdf`, arXiv **v3** (29 Dec
> 2025). This section supersedes the stale "Analysis (overlap with Pebble)" block above, which was
> scored against the archived voice-MTL profile (D1–D7); it uses the current **ViEmoSpeech**
> profile + Decision Register (**V-A…V-H**). Append-only; the history above is untouched.

### Source-access note

- Full text extracted with `pdftotext docs/papers/bimodal-ser/pdfs/01-c2ser.pdf` (1080 lines).
  Read end-to-end: abstract, §I–VII, Tables I–IX, Figs 1–7, all 56 refs.
- Web-validated the load-bearing numbers against the arXiv HTML (`arxiv.org/html/2502.18186v1`)
  and the venue/DOI against the arXiv abstract page.
  - Query: *"C2SER Steering Language Model Stable Speech Emotion Recognition Contextual Perception
    Chain of Thought Emotion2Vec-S"* → resolved `arxiv.org/abs/2502.18186`,
    `arxiv.org/html/2502.18186v1`, `github.com/zxzhao0/C2SER`, `huggingface.co/papers/2502.18186`.
  - Venue check → `arxiv.org/abs/2502.18186`: Comments = "This work has been published in IEEE
    Transactions on Audio, Speech and Language Processing"; related DOI `10.1109/TASLPRO.2025.3648793`.
- **Provenance conflict rule:** v1 HTML numbers for Table V (Emotion2Vec-S) and Table VI/VII (C2SER)
  **match the local v3 PDF exactly** (CASIA 62.95, Emo-Emilia 80.66/69.00, ESD 79.84, MELD 21.31,
  λ_utt=0.1, λ_cate=100, "Emotion2Vec-S is frozen"). No preprint/published delta on the cited numbers.
  Code + checkpoints + Emo-Emilia test set are released (`github.com/zxzhao0/C2SER`, HF collection).

### What the paper actually does

**Task/claim.** An audio-language model (ALM) for **7-class categorical SER** (anger, happiness,
neutral, sadness, surprise, disgust, fear) that reduces the "hallucination" failure of generative
ALMs (fabricating ungrounded rationales, e.g. labelling a cheerful clip "sadness" because "maybe
he is preparing for an exam", Fig 1). It is **not** dimensional — no valence/arousal/distress, no
regression, no CCC/Pearson anywhere; metrics are WA / UA / Macro-F1 only.

**Architecture (§III).** Two frozen perception encoders feed a text LLM:
- *Semantic* = **Whisper-medium** encoder (2 conv layers, 2× downsample, 24 Transformer layers).
- *Acoustic* = **Emotion2Vec-S**, their extension of emotion2vec (data2vec2.0 backbone) that adds a
  **category-level contrastive loss** `L_Cate` (CLIP-style: same-emotion utterances = positive pairs,
  different-emotion = negatives, on the average-pooled global embedding G). Total loss
  **`L_e2v = L_Frm + λ_utt·L_Utt + λ_cate·L_Cate`** with **λ_utt=0.1, λ_cate=100** (Eq 2, §V-A). The
  motivation: emotion2vec's utterance+frame losses are both *instance-level*, so they confuse
  acoustically similar categories (fear vs sadness); the category loss pulls categories apart.
- A 4-layer-Transformer + linear **connection module** (ffn dim 2560) projects both into **Qwen2-7B-
  Instruct**, fine-tuned with **LoRA** (rank 8, α 32, dropout 0.1). During C2SER training,
  **Emotion2Vec-S is frozen** (§V-A); Whisper features are also used as-is.

**Chain-of-Thought + self-distillation (§III-C/D).**
- *Explicit CoT*: the model first emits a rationale describing speaking-rate / pitch / energy /
  transcript, then the emotion. Training data built by (1) extracting mean-F0 (PENN), loudness
  (pyloudnorm), speaking-rate (phonemes/duration); (2) **discretizing each to Low/Med/High via μ±σ**
  (Central-Limit-Theorem heuristic); (3) filling a template (Table I) into **GLM-4-9B-Chat** to
  generate a natural-language rationale grounded in those labels + the ground-truth emotion.
- *Implicit CoT*: self-distillation from explicit→direct output. Batch-level linear schedule — the
  probability of sampling an explicit example **decays 1.0→0.0** across the phase, so by the end the
  model outputs only the short emotion description (<10 tokens vs >40 for explicit), cutting latency
  ~10× and error accumulation.

**Data (§IV).** Trained on 6 public corpora + a ~439k-utt internal set = **672,668 utts / 1215.7 h**
(Table II); Chinese ≈ 2× English; **neutral ≈ half the data, fear+disgust < 2%** (Fig 4). Silver
labels for the internal + Emilia data via **intersection of Emotion2Vec (speech) ∩ GLM-4-9B-Chat
(text)** — a two-teacher agreement gate. New test set **Emo-Emilia** (Table III): 1400 in-the-wild
utts, 100/emotion × {CN,EN}, built by the same 2-teacher intersection then **4 bilingual experts
retain only unanimously-labelled samples**. Eval spans CASIA, M3ED (Mandarin), MELD, EmoV-DB
(English), ESD, ASVP-ESD, EMOVO (Italian), MESD (Mexican), Emo-Emilia (Table IV).

**Results — Emotion2Vec-S frozen features (Table V; EmoBox 5-fold leave-one-session-out, in-domain
linear probe on frozen features — i.e. exactly the "frozen backbone + trained head" regime).** All
✔ corroborated (v1 HTML = v3 PDF):

| Dataset (lang) | WavLM-base UA | Emotion2Vec UA | **Emotion2Vec-S UA** |
|---|---|---|---|
| **CASIA (Mandarin, acted)** | 47.25 | 47.58 | **62.95** (F1 60.2) |
| Emo-Emilia (mix, in-wild) | 67.26 | 68.02 | **80.66** |
| ESD (mix, acted) | 72.90 | 70.22 | **79.84** |
| MESD (Mexican) | 42.58 | 50.56 | **59.57** |
| **M3ED (Mandarin, spontaneous)** | 22.76 | 22.04 | 23.82 (all ≈ chance) |
| **MELD (English, conversational)** | 23.44 | 23.20 | **21.31 (NOT best;** data2vec2.0 = 24.79) |
| EmoV-DB (English, acted) | **98.38** | 96.71 | 97.04 (WavLM wins) |

Emotion2Vec-S is best on Chinese/multilingual/Mexican, competitive-or-worse on English
conversational. The single biggest gain is **CASIA Mandarin: +15.4 UA over WavLM, +15.4 over
emotion2vec**.

**Results — C2SER ALM (Tables VI–VIII; zero-shot cross-dataset except MELD/ESD in-domain).**
- Emo-Emilia: **C2SER-Implicit UA 69.00 / F1 61.61** vs Explicit 68.29/61.28 vs **Qwen2-Audio
  39.07/31.91** vs text-only cascade (Whisper-m→Qwen2-7B) **63.31/60.89** (Table VI/VII). ✔
- **Text-only cascade register split** (Table VI): CASIA (Mandarin acted) text-only collapses to
  **13.93 UA** (≈ chance for 6-class) while fused C2SER-Implicit = **53.33**; but on Emo-Emilia the
  same text-only cascade reaches **63.31**. ✔ Content carries emotion on in-the-wild speech, almost
  nothing on acted Mandarin.
- **Ablation (Table VIII, Emo-Emilia):** full **69.00** → w/o Emotion2Vec-S **57.93** (−11.1) → w/o
  CoT **43.14** (−25.9) → w/o Whisper **32.07** (−36.9, "fails to converge"). Semantic channel is the
  most load-bearing single component. ✔
- In-domain fine-tuning helps a lot (Table IX, MELD): 0-ep UA 38.66 → 3-ep 43.50 → 6-ep 49.30. ✔
- **Rare-class collapse:** on Emo-Emilia, anger/happiness/neutral/sadness/surprise all >90% category
  accuracy but **disgust and fear < 20%** (Fig 7), attributed to the <2% training share. ✔

**Tone:** the word "tone" appears **only** as paralinguistic prosody ("low-pitched tone", Table I
example). Two Mandarin corpora (CASIA, M3ED) are used and CASIA yields the largest single gain, yet
**lexical tone is never named as a variable or confound** — validated: "tone" = pitch descriptor
only (arXiv HTML check). The pitch feature fed to the CoT is **mean-F0 discretized Low/Med/High**,
with no tone normalization.

### Parts directly useful for ViEmoSpeech (tagged by Decision ID)

1. **[V-B] Emotion2Vec-S as a frozen audio-branch drop-in — with a register caveat.** The released
   checkpoint + Table V give a like-for-like "frozen features + trained linear head" comparison
   (EmoBox 5-fold), which is *exactly* our audio-branch regime. Headline: CASIA Mandarin UA
   **62.95 vs 47.25 WavLM / 47.58 emotion2vec** (✔). The mechanism is a single added loss term
   (`λ_cate=100·L_Cate`, Eq 2) that separates confusable categories — no architecture change, no
   fine-tune. **Transfer risk (real):** every large gain is on **acted / clean** sets (CASIA, ESD,
   Emo-Emilia-expert-filtered); on **M3ED (Mandarin *spontaneous*)** — the closest register to our
   VN TV-drama — Emotion2Vec-S (23.82) is within noise of WavLM (22.76) and near chance, and on
   **MELD English conversational** it is *worse* than data2vec2.0/WavLM. So the checkpoint is a
   defensible default, but the A/B must be run on our own spontaneous VN clips, not assumed.

2. **[V-A] Whisper-semantic + Emotion2Vec-S-acoustic + CoT fusion as a bimodal template.** This is a
   concrete design that beats a text-only cascade: ablation Table VIII shows *both* streams are
   needed (−11 without acoustic, −37 without semantic), and the fused model beats the
   Whisper→Qwen2 cascade on acoustic-dominant sets. **Transfer risk (large):** their "fusion" lives
   *inside a 7B LLM with LoRA* (Qwen2-7B) driven by CoT text generation — orders of magnitude
   heavier than our target lightweight learned-fusion head over PhoWhisper+PhoBERT, and their
   semantic channel is Whisper *encoder features*, not ASR *tokens*. It is a **template for what to
   fuse and an existence proof that acoustic+semantic > either alone**, not a copyable module.

3. **[V-C] The text channel under ASR: a register-dependent collapse, quantified.** The
   Whisper-m→Qwen2-7B cascade is the paper's own "ASR-transcript-only text branch". It swings from
   **63.31 UA (Emo-Emilia, in-wild)** to **13.93 UA (CASIA, acted Mandarin)** (Table VI, ✔). For
   ViEmoSpeech (acted TV drama, Mandarin-adjacent tonal register) this predicts our PhoWhisper text
   branch will carry **little** on high-arousal acted turns — the same turns where PhoWhisper makes
   tone-swap errors (mày→máy). **Transfer risk:** the cascade discards paralinguistics by
   construction (that is its point), and CoT *feeds the transcript into the rationale*, so a wrong
   ASR token propagates into a wrong reason — which is exactly why they added **explicit→implicit
   self-distillation** (batch prob 1.0→0.0) to damp error accumulation. That self-distillation trick
   is the transferable V-C mechanic for a noisy text channel.

4. **[V-B/V-E] Reusable frozen-feature recipe + rare-class warning.** Emotion2Vec-S training config
   (Adam, lr 7.5e-5, wd 1e-2, cosine, 5% warmup, grad-accum 2, classifier = 3 FC layers, backbone/
   dims identical to emotion2vec) is a ready arm for our audio-branch bake-off. And Fig 7's
   **disgust/fear < 20%** accuracy at 69% overall, from a <2% training share, is a direct rare-class
   red flag for our 7-class scheme + ≥50-clip floor (ADR-002).

### How each part helps ViEmoSpeech succeed

- **[V-B] Audio-branch bake-off gets a third contender + a hypothesis.** Add **Emotion2Vec-S** as an
  arm next to WavLM and emotion2vec in the frozen-feature probe, evaluated with our
  speaker-disjoint + whole-series-holdout protocol (V-G). The **pre-registered hypothesis**, from
  Table V's own pattern: Emotion2Vec-S wins on *acted/clean* and ties on *spontaneous* — so if it
  wins on our VN-TV-drama clips (which are acted but noisy), that is a genuine result; if it only
  ties (M3ED-like), we keep WavLM (the vn-12/bimodal-12 default). Either way the CASIA +15 pt gain
  is the citation for trying it.
- **[V-A] Fusion experiment scope + baseline ladder.** Adopt the *shape* — two frozen streams
  (audio = Emotion2Vec-S/WavLM, semantic = PhoBERT-over-PhoWhisper) into a light learned-fusion head
  — and borrow C2SER's **ablation grid** (full / −audio / −semantic / −fusion) verbatim as our own
  ablation table so the "both modalities needed" claim is measured, not asserted. Their −Whisper
  −37 pt result is the argument that the semantic branch is not optional even on tonal speech.
- **[V-C] Bake a conflict/high-arousal slice + audio-anchoring.** Because the text channel collapses
  on acted tonal speech (CASIA 13.93), our training must not let a strong PhoBERT dominate: carry a
  **high-arousal / ASR-tone-swap slice** in eval, and consider an **audio-only auxiliary head** or
  modality dropout (echoing vn-12's safeguard) so fusion cannot degenerate to text. Report the text
  branch's stand-alone number on *both* a clean-caption arm and a PhoWhisper-transcript arm to
  quantify the ASR gap directly (C2SER never runs this on tonal ASR — whitespace we can own).
- **[V-B/V-E] Rare-class floor is empirically justified.** Cite Fig 7 (disgust/fear <20% at 69%
  overall) as external evidence that a 7-class scheme with a <2% tail collapses on the tail — motivating
  our ≥50-clip floor, class-balanced sampling, and per-class (not just macro) reporting.

### Vietnamese SER transfer lens (frozen backbone · PhoWhisper ASR · tone×emotion · acted proxy)

- **Frozen-backbone fit is genuine.** Table V is a frozen-features + trained-head probe, and
  Emotion2Vec-S stays frozen inside C2SER — both match our non-negotiable frozen-encoder design. The
  Emotion2Vec-S checkpoint is openly released, so the V-B A/B costs no training of the backbone.
- **Tonal-language evidence is present but tone-blind.** The largest gain (CASIA Mandarin) and a
  second Mandarin set (M3ED) are used, yet the paper never treats lexical tone as a variable; its
  emotion pitch cue is raw mean-F0 → Low/Med/High. Per **vn-13 (Chang PLOS ONE)** F0 is precisely the
  channel where tone×emotion interact (F0-mean χ²(12)=70.18, F0-range χ²(12)=114.64, both p<.001),
  so C2SER's F0-as-emotion-cue is *tone-contaminated by construction* — for VN (6 phonation-heavy
  tones, vn-06) doubly so. This is **whitespace for V-D**: Emotion2Vec-S encodes tonal audio as a
  black box with no tone/emotion disentanglement, and no paper in the set (C2SER included) measures
  the interaction on lexical tone. Our tone×emotion claim is untouched by this strong bimodal SoTA.
- **Acted register is a two-edged match.** ViEmoSpeech is acted TV drama; C2SER's biggest wins are on
  acted corpora (CASIA/ESD) — encouraging. But its spontaneous set (M3ED) shows the gains largely
  evaporate, and its text channel collapses on acted speech — so "acted" cuts both ways for us.
- **No distress / no dimensional output.** C2SER is purely 7-class categorical: it offers **nothing**
  for our valence/arousal (CCC) or distress-recall-floor heads (V-F). Do not cite it for those.
- **Silver-label lineage worth borrowing (V-E boundary).** Their 2-teacher intersection
  (Emotion2Vec ∩ GLM-4-9B) then **4-expert-unanimous** filter for Emo-Emilia is a clean
  weak-then-human pattern — but note under **ADR-003** our LLM teachers are *on-screen suggestion
  only*, so we adopt the human-adjudication half, not machine-intersection-as-label.

### Limitations & open questions for ViEmoSpeech

- **Contradiction vs the ViEmoSpeech hook (and reconciliation of vn-08 ↔ vn-12).** Our method-paper
  hook is that *because VN tone is phonation-heavy, the semantic/text branch must carry more load
  than in non-tonal SER*. C2SER's own text-only cascade says the opposite for **acted** tonal
  speech: **CASIA Mandarin text-only = 13.93 UA (near chance)** — on acted tonal speech the semantic
  channel carries almost nothing and **acoustic dominates**. Yet on **in-the-wild** speech the same
  cascade hits **63.31**. This reconciles vn-08's "text near-useless (38.7–44.1%)" with vn-12's
  "semantics dominate": *how much content carries emotion is register-dependent*, high on
  naturalistic content-laden speech, low on short acted exclamations. Direct consequence: on our
  acted VN drama the text branch may underperform exactly where tone-swap ASR errors cluster (high
  arousal), so the "text carries more load" hook needs to be reframed as "text carries more load
  *when there is content to carry it*, and our tone×emotion competition is an *acoustic-channel*
  claim, not a text-reliance claim." Must confront this explicitly in the method paper.
- **F0-as-emotion-cue vs vn-13.** C2SER discretizes mean-F0 as an emotion feature with no tone
  control; vn-13 shows F0 is the tone-shared channel. Any VN system that copies this uncritically
  will conflate tone and emotion. Our audio branch should instead weight amplitude/energy + duration
  (vn-13: tone-independent emotion carriers) and treat F0 features as tone-contaminated.
- **Zero-shot vs in-domain confound in the tables.** Table V (Emotion2Vec-S) is in-domain 5-fold;
  Table VI (C2SER) is mostly zero-shot cross-dataset — so C2SER's 69.00 and Emotion2Vec-S's 80.66 on
  Emo-Emilia are *not* the same experiment. For our design (frozen features + trained head), **Table
  V is the relevant comparison**, not the C2SER ALM numbers.
- **Rare-class collapse persists even at SoTA** (disgust/fear <20%, Fig 7) — a warning that our 7-way
  scheme's tail will not be rescued by a better backbone alone; needs sampling/loss design (V-E/V-F).
- **Heavy, generative, non-turn-level.** C2SER is a 7B LoRA ALM emitting free-form text later mapped
  to a label by *another* 14B model (Qwen2.5-14B) — not a lightweight turn-level classifier. Its
  fusion recipe is a template, not a deployable module for our pipeline.
- **Open question worth one experiment:** run the released Emotion2Vec-S frozen features through a
  layer-wise tone-vs-arousal probe (Shen/vn-06 protocol) on VN syllables — does the category-
  contrastive loss that helps Mandarin emotion also *entangle* tone, or leave it separable? That
  answer decides whether Emotion2Vec-S helps or hurts our V-D disentanglement goal.
