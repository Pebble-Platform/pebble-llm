# Paper 08 — Enhancing SER with Graph-Based Multimodal Fusion and Prosodic Features

- **Authors:** Alef Iury Ferreira, Lucas Rafael Gris, Alexandre Ferro Filho, Lucas Ólives, Daniel Ribeiro, Luiz Fernando, Fernanda Lustosa, Rodrigo Tanaka, Frederico Oliveira, Arlindo Galvão Filho (Federal University of Goiás, Brazil, et al.)
- **Venue / year:** Interspeech 2025 SER-Naturalistic-Conditions Challenge system, arXiv 2025
- **Links:** abs https://arxiv.org/abs/2506.02088 · PDF `pdfs/08-graph-fusion-prosodic-ser.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Fusion đa encoder — Wav2Vec2/HuBERT/WavLM/Whisper/XEUS + RoBERTa — qua graph attention networks, kèm prosodic features.

**Relevance to Pebble:** Trả lời trực tiếp câu "chọn SSL audio encoder nào + text encoder nào + fuse ra sao".

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Pebble profile used (assembled at analysis time):** Primary = ordinal suicide-risk **text** classification, LLM/weak silver labels augmenting a scarce clinical gold set under **gold-holdout**, ordinal-aware, BERT-family encoder. Adjacent **voice** stream = heterogeneous MTL on a **frozen WavLM-Large / emotion2vec** backbone — 3 heads (emotion CE, affect V/A via **CCC**, crisis under a **hard recall floor**) balanced by **Kendall uncertainty weighting**; named next step = swap proxy labels for **MSP-Podcast** (A/V/D) + DAIC. Voice+text **fusion** is the forward direction.

### Analysis — Graph-Fusion + Prosodic SER (Interspeech 2025 challenge)
- **Overlap:** 12% (peripheral) — D1=0, D2=0, D3=1, D4=0, D5=0, D6=0, D7=2
  - D1=0 single-task categorical emotion (no heterogeneous continuous/safety heads); D2=0 podcast affect, not crisis; D3=1 emotion corpus and it is **MSP-Podcast**, the voice task's named next real-label target; D4=0 CED audio-tag distillation + vote ensemble, not teacher-LLM silver labels; D5=0 inverse-freq weighted CE, no principled MTL balancing; D6=0 Recall reported but no recall-floor objective; D7=2 direct backbone match (WavLM/Wav2Vec2/HuBERT/Whisper/XEUS + RoBERTa-Large).
- **Closest on:** D7 (SSL audio + text encoder family, identical to the voice stream) and D3 (MSP-Podcast, the exact next-step corpus).
- **Best point (Design lesson):** Their frozen-feature SSL backbone bake-off on naturalistic MSP-Podcast ranks **Whisper Large V3 (Macro F1 0.366) > XEUS 0.323 > WavLM-Large 0.313 > HuBERT 0.274 > Wav2Vec2 0.178** — on spontaneous emotional speech the ASR-pretrained Whisper/XEUS features beat WavLM/Wav2Vec2, and simple concat fusion (0.388) nearly matches complex graph fusion / MDAT (0.401) at this data scale.
  - **How to apply to Pebble:** when the voice-mtl-heads task swaps its RAVDESS proxy for real MSP-Podcast, add **Whisper Large V3 and XEUS** to the frozen-backbone comparison instead of assuming WavLM/emotion2vec, and keep the fusion baseline as plain concatenation before investing in graph attention.
- **Caveats:** Full PDF read (arXiv v1, not paywalled). Low overlap is honest, not incomplete: this is a single-task categorical **challenge system** with no heterogeneous MTL heads, no MTL loss-balancing, no crisis/recall constraint, and no LLM weak-label distillation — its value to Pebble is confined to backbone selection (D7) and the shared MSP-Podcast corpus (D3), not the core ordinal/MTL thesis.

## Deep research — full-PDF read (2026-07-10)

> Profile: current ViEmoSpeech (Vietnamese TV-drama SER corpus + tone×emotion bimodal method paper),
> Decision Register V-A…V-H per `docs/tasks/paper-deep-analysis.md`. The stale text-stream "Analysis"
> section above (D1–D7) is archived and not used here. Targets moved: **V-B** (their prosodic feature set
> and gain), **V-A** (graph-fusion mechanism), **V-D** (prosodic-feature choice vs. tone contamination).

### Source-access note

- **Read path:** local PDF `pdfs/08-graph-fusion-prosodic-ser.pdf` extracted in full with
  `pdftotext` (Method §3, Setup §4, all three result tables, References). This is the identical text
  to arXiv:2506.02088v1 (2 Jun 2025).
- **Web validation:** headline **Macro F1 39.79% test / 42.20% validation** confirmed against the
  arXiv abstract page — query `Ferreira Gris "Graph-Based Multimodal Fusion" Prosodic Speech Emotion
  Recognition Interspeech 2025 Macro F1 39.79` → resolved https://arxiv.org/abs/2506.02088 (WebFetch of
  the abstract returned "39.79% on the official test set, with 42.20% on the validation set"). **✔ corroborated.**
- **Venue authority:** this is an INTERSPEECH-2025 SER-in-Naturalistic-Conditions **Challenge system
  description**; the arXiv v1 is the only/authoritative version (no separate journal record; the
  ResearchGate / Interspeech proceedings entry carries the same numbers). No preprint-vs-published delta
  exists. Table 1/2/3 numbers below are single-source (arXiv v1 = venue) and tagged ✔ on that basis;
  none were independently re-derivable, so any that carry cross-corpus weight are flagged for that.
- Source code exists (github.com/alefiury/InterSpeech-SER-2025) — reusable if we adopt the F0-quant block.

### What the paper actually does

**Task/data.** Categorical emotion recognition (Track 1) on **MSP-Podcast** (the same naturalistic
found-speech corpus deep-read in bimodal-12), English, spontaneous. Metric = **Macro F1** (they note
Micro F1 = accuracy, so accuracy is not separately reported). Weighted Cross-Entropy (inverse-frequency
class weights), batch 8, 20 epochs, AdamW, cosine LR with 500 warm-up steps, LR bounded 5e-5→1e-5,
grad-clip norm 10. `X` / `O` (no-agreement / other) labels removed from the filtered validation set.

**Four-stage pipeline (Fig. 1, §3):**
1. **Unimodal SSL bake-off (Table 1, Macro F1, ✔ single-source):** Wav2Vec2-Large **0.178** <
   HuBERT-Large **0.274** < WavLM-Large **0.313** < XEUS **0.323** < **Whisper-Large-V3 0.366** (best;
   Micro F1 0.524, R 0.391). Features pre-extracted from the **last hidden layer** of each frozen SSL
   model. They attribute Wav2Vec2/HuBERT's collapse to read-speech pretraining and Whisper's win to
   "diverse, spontaneous, and noisy" pretraining.
2. **Bimodal fusion with text (Table 3, Macro F1, ✔):** text = **RoBERTa-Large** over **Canary-ASR**
   transcripts (they deliberately use ASR text, *bypassing the dataset's original transcripts*). Fusion
   strategies: **Simple** concat (mean-pool both modalities → MLP) **0.388**; single-layer Transformer
   early-fusion **0.364**; **HCAM** (BiGRU + self-attn + cross-attn) **0.383**; **MDAT** (the
   graph-attention dual-attention transformer, 8 heads) **0.401** (best). Bimodal >> unimodal
   (0.401 vs 0.366). Notably simple concat (0.388) nearly matches MDAT (0.401) — they credit MDAT's
   graph attention but flag complex models overfit "given the limited dataset size."
3. **Prosodic + spectral integration (Table 3):** **F0 is the only prosodic feature.** Raw F0 from
   **RMVPE**, mel-scaled, **quantized into 256 bins + 1 padding index**, mapped to learnable 256-dim
   embeddings, projected to 512, mean-pooled over time, concatenated with speech+text. Gains over the
   0.388/MDAT base: **+ raw F0 0.397**, **+ quantized F0 0.407** (quantization beats a raw-F0 1D-CNN
   baseline, kernel 3/stride 1/256ch, by +1.0 Macro F1), + Data-Aug 0.400, **+ SwiGLU 0.411** (best
   single config). Spectral branch: **CED-Small (22M)** audio-tagging model over Kaldi Mel-filterbanks
   — randomly-init CED 0.342 < pretrained CED 0.376 < +Data-Aug 0.393 < +SwiGLU 0.405. F0 (0.411) and
   CED (0.405) are "complementary."
4. **Ensemble (Table 2):** majority vote over ≥3 configs from a 13-way exhaustive search (adds XEUS,
   E5-Large-V2 text encoder — worse than RoBERTa, Focal loss, balanced sampling); best single member
   Whisper+RoBERTa+MDAT+F0Quant+SwiGLU+DataAug **0.411**, **ensemble 0.422 val → 39.79% test**.
   SeqAug (modality-agnostic sequential feature resampling, 50% prob, beta α=0.5, independent
   per-dimension permutation) is the augmentation. SwiGLU MLP gives a "slight but consistent" gain.

**Punchline:** graph fusion (MDAT) is the best *fusion* but only +1.3 Macro F1 over plain concat;
the two biggest deltas are **modality** (unimodal 0.366 → bimodal 0.401, +3.5) and the **quantized-F0
prosodic block** (+1.9 over simple fusion). Everything else (SwiGLU, SeqAug, CED, ensemble) is ≤+1.5.

### Parts directly useful for Pebble

1. **[V-B] The prosodic feature *is F0-only, and F0-quantized* — extract the block, but know its ceiling.**
   Their entire prosodic contribution is one channel: RMVPE F0 → 256 mel-bins → learnable embeddings.
   Quantized-F0 (+1.9 Macro F1 over concat; 0.388→0.407, ✔ Table 3) beats a raw-F0 CNN (0.397, +0.9),
   so **discretize F0 rather than feed the raw contour**. Concrete artifact: the ViEmoSpeech audio
   branch's prosody sub-vector — adopt the mel-scale-quantize-embed pattern, but see V-D below for why
   F0 alone is the wrong prosodic choice for Vietnamese.
2. **[V-A] Graph fusion (MDAT/GAT) barely beats concatenation at ~20k-utterance scale.** MDAT 0.401 vs
   Simple-concat 0.388 (+1.3 Macro F1, ✔ Table 3); Transformer early-fusion (0.364) and HCAM (0.383)
   both *lose* to concat. Their own explanation: complex fusion overfits at "limited dataset size."
   ViEmoSpeech P1 is ~18k utt — the same regime. Concrete artifact: keep **mean-pool concat → MLP** as
   the V-A fusion baseline the learned fusion must beat, and treat GAT as an *upper-tier* option only if
   a cross-attention/gated variant clears concat by a margin larger than seed variance.
3. **[V-B] On naturalistic MSP-Podcast, Whisper-Large-V3 > XEUS > WavLM > HuBERT > Wav2Vec2.**
   (0.366/0.323/0.313/0.274/0.178, ✔ Table 1.) Read-speech-pretrained encoders (W2V2, HuBERT) collapse
   on spontaneous speech. Concrete artifact: the V-B frozen-backbone comparison must include a
   **Whisper-encoder arm and XEUS arm**, not just WavLM/emotion2vec — and this directly contradicts
   the "WavLM default" reading carried from bimodal-12 (see contradictions).
4. **[V-D] They control for *nothing* tone-like — the single prosodic feature they add is the exact
   tone-confounded one.** F0 is the only prosodic channel; no energy, no duration, no phonation/voice-
   quality features; no tone modelling; MSP-Podcast is English (atonal), so lexical-tone×F0 confounding
   never arises for them. This paper is the clean demonstration of the design ViEmoSpeech must *not*
   copy blindly (see child/tone lens). Concrete artifact: the V-D prosody-design decision — pair or
   replace F0 with amplitude/energy + duration features (tone-independent emotion carriers per vn-13).

### How each part helps Pebble succeed

- **Prosody sub-vector (V-B).** Implement the F0-quantization block (RMVPE → 256 mel-bins → 256-d
  learnable embedding → 512 proj → mean-pool) as one arm, but run it in an **ablation against an
  amplitude/energy+duration arm and a phonation arm (jitter/shimmer/HNR/H1-H2 from vn-06)**. Their
  +1.9-Macro-F1 F0 gain on English is the *upper bound* of what raw-F0 prosody can buy; the ViEmoSpeech
  experiment is whether that gain survives — or inverts — once F0 is tone-loaded (V-D measurable claim).
- **Fusion baseline ladder (V-A).** Bake their exact ladder into the V-A experiment table:
  concat 0.388 / Transformer 0.364 / HCAM 0.383 / MDAT 0.401. On our small corpus the null hypothesis
  is "learned fusion ≈ concat"; we only claim a fusion win if a cross-attn/gated/query-based module
  beats concat by > seed std (their own +1.3 for MDAT is inside the noise band they warn about).
- **Backbone choice (V-B).** Add Whisper-encoder + XEUS frozen arms to the WavLM/emotion2vec bake-off.
  For Vietnamese, this dovetails with vn-06's mid-layer finding — but note they used the **last** hidden
  layer (a known-suboptimal probe layer for tone); our bake-off should sweep layers, not copy last-layer.
- **Text-under-ASR (V-C, incidental).** They feed **ASR (Canary) transcripts, not gold**, into RoBERTa
  and still get bimodal >> unimodal — a data point that ASR-text fusion is viable, though Canary on
  English ≠ PhoWhisper on high-arousal tone-swap Vietnamese (mày→máy); our V-C robustness question stays open.

### Child mental-health lens (ViEmoSpeech transfer validity)

- **The core transfer failure is the prosodic feature itself.** ViEmoSpeech's premise (vn-13 Chang,
  vn-06 Shen) is that **Vietnamese lexical tone lives in F0**: emotion's effect on **F0 mean and F0
  range is tone-dependent** (sig. tone×emotion interaction, F0 χ²(12)=70.18 p<.001; F0-range
  χ²(12)=114.64 p<.001 — vn-13), whereas emotion's effect on **amplitude and duration is
  tone-independent/additive** (amp p=.98, dur p=.29). This paper's *only* prosodic channel is F0 — i.e.
  precisely the dimension that is tone-contaminated in Vietnamese. Their quantized-F0 embedding would,
  in Vietnamese, encode a blend of **lexical-tone identity + emotion + speaker** with no way to separate
  them; on English MSP-Podcast that confound is absent, so their +1.9 gain does **not** transfer
  unchanged. **Mitigation:** (a) prefer amplitude/energy + duration prosodic features (tone-robust emotion
  carriers); (b) if F0 is used, condition it on the syllable-tone annotation (ADR tone labels) so the
  model can factor tone out — this is the V-D tone-representation experiment; (c) add a phonation/
  voice-quality vector since VN tone is phonation-heavy (vn-06) and Chang only measured F0/amp/dur.
- **No tone-awareness anywhere.** They add zero controls for tone, dialect, or speaker; acceptable for
  English, disqualifying as a template for a tonal-language corpus. This *is* the ViEmoSpeech novelty
  whitespace restated: even a 2025 prosody-focused SER system treats F0 as a pure emotion cue.
- **Ethics/label caveat is mild here** (MSP-Podcast, adult podcast speech, no clinical claim) — unlike
  vn-10, this paper does not overclaim a mental-health application, so no anti-pattern to flag; it is
  simply an emotion-recognition system whose prosodic design is tone-naive.

### Limitations & open questions for Pebble

- **Contradiction vs. bimodal-12 (WavLM-default):** the MSP-Podcast deep-read concluded "WavLM ≥
  Wav2vec2 ≥ HuBERT clean → WavLM default." On the **same corpus**, this paper ranks
  **Whisper-Large-V3 (0.366) > XEUS (0.323) > WavLM (0.313)** — WavLM is third, beaten by ASR-pretrained
  encoders on spontaneous speech. Resolution for V-B: "WavLM default" holds for clean/read benchmarks;
  on naturalistic found-speech (our regime), Whisper/XEUS encoders should be in the bake-off and may win.
- **Contradiction vs. our own tone×emotion premise (V-D):** their result "quantized F0 helps
  (+1.9 Macro F1)" is true on English but is the *opposite* of what ViEmoSpeech predicts for Vietnamese,
  where F0 is tone-loaded — so the same feature that helps them may hurt us or require tone-conditioning.
  That inversion is itself a measurable ViEmoSpeech contribution (the VN-vs-English/Mandarin F0-prosody delta).
- **Graph-fusion win is within noise (V-A gap):** MDAT beats concat by only +1.3 Macro F1 and both
  Transformer- and HCAM-fusion *lose* to concat; the paper never reports seed variance or significance,
  so "graph fusion is effective" is asserted on a single split. Open question: does any learned fusion
  actually beat concat at ~18k utterances, or is fusion complexity a net negative at our scale?
- **Last-layer probing only:** SSL features taken from the last hidden layer — suboptimal for tone
  (vn-06: tone peaks mid-stack). Their backbone ranking may shift under a layer sweep; don't inherit it as final.
- **No dimensional/attribute track, no distress:** categorical-only (Track 1). Contributes nothing to
  V/A-CCC (V-G) or the distress recall-floor head (V-F); the challenge's attribute track is out of scope here.
- **Single-source numbers:** every table value is arXiv-v1-only (challenge system, no journal version);
  only the headline 39.79/42.20 was independently corroborable. Table 1/3 deltas are usable as design
  signal but not as cross-paper leaderboard anchors.
