# Paper 06 — WavFusion: Towards wav2vec 2.0 Multimodal Speech Emotion Recognition

- **Authors:** Feng Li, Jiusong Luo, Wanjun Xia
- **Venue / year:** MMM 2025 (Springer LNCS)
- **Links:** abs https://arxiv.org/abs/2412.05558 · PDF `pdfs/06-wavfusion.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Gated cross-modal attention + homogeneous-feature-discrepancy learning, wav2vec2 audio + text branch, eval IEMOCAP/MELD.

**Relevance to Pebble:** Reference ablation gọn cho lựa chọn cơ chế fusion.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled Pebble profile (at analysis time):** Primary intent = *ordinal* suicide-risk **text** classification with LLM silver labels under strict gold-holdout (ordinal-aware, subject-level splits, reproducible; `docs/intent/constraints.md`). Adjacent **voice** stream (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`) = heterogeneous multi-task heads on a **frozen SSL speech backbone** (WavLM-Large / emotion2vec): emotion (CE) + affect (valence/arousal **CCC regression**) + crisis (BCE under a **hard recall floor**), balanced by **Kendall uncertainty weighting**; **voice+text fusion** is the forward direction.

### Analysis — WavFusion (audio+text+visual SER)
- **Overlap:** 19% (peripheral) — D1=0, D2=0, D3=1, D4=0, D5=1, D6=0, D7=2.
  - Formula: (3·0 + 2·0 + 1·1 + 2·0 + 2·1 + 2·0 + 1·2) / 26 × 100 = 5/26 × 100 ≈ 19%.
  - D1=0 single categorical emotion head + a representation-level margin loss — no continuous/safety heads. D2=0 general acted/TV SER, not mental-health/crisis (mental health only namechecked in intro). D3=1 IEMOCAP/MELD are emotion corpora but not the intensity/transfer exemplars. D4=0 no teacher-LLM labels (fully supervised gold). D5=1 balances CE + margin loss but via a hand-tuned scalar λ grid (Table 5), not the principled methods (uncertainty/GradNorm/PCGrad). D6=0 no recall constraint. D7=2 wav2vec2.0 audio SSL backbone (same family as the voice stream's WavLM/emotion2vec) **and** RoBERTa-base text (BERT-family, matches the text stream).
- **Closest on:** D7 (SSL-speech + RoBERTa backbones match both Pebble streams); secondarily D5 (a concrete two-loss balancing sensitivity study).
- **Best point (Method to adopt):** Gated cross-modal attention fusion — a learnable per-channel sigmoid gate `P = σ(FC(X_A→T ⊕ X_A→V))`, `X_F = P⊙X_A→T + (1−P)⊙X_A→V` (Eqs 10–11) that dynamically filters redundant/misleading cross-modal signal, ablated cleanly against naive concatenation (concat 66.78 → gated attention 70.6 WF1 on IEMOCAP, Table 6).
  - **How to apply to Pebble:** when the voice MTL heads gain a text branch, fuse the audio and text streams with this learnable gate rather than concatenation — it is a drop-in, cheap, citable fusion block and its concat-vs-gated ablation is the reference comparison for that design choice.
- **Caveats:** Read in full (arXiv PDF, all 11 pp) — no paywall. Single **categorical** emotion task only; no continuous/CCC head, no crisis/recall-floor objective, no ordinal structure, no LLM weak labels, no gold-holdout — so it touches Pebble's *architecture forward-direction*, not its core evaluation thesis. Fusion gains are modest (+0.74 WF1 IEMOCAP, +0.44 MELD); MELD uses a fixed split while IEMOCAP is 5-fold (no reported std). The margin ("homogeneous feature discrepancy") loss needs paired same-emotion-across-modality samples, which Pebble's proxy-labeled RAVDESS voice-only setup cannot supply.

## Deep research — full-PDF read (2026-07-10)

> Read against the **ViEmoSpeech** profile (audio + PhoWhisper-ASR text, frozen backbone, 7-class +
> V/A(1–5) + distress, VN tone×emotion). The stale text-stream "Analysis (overlap with Pebble)" block
> above is archived — decisions cited here are **V-A…V-H** from `docs/tasks/paper-deep-analysis.md`.
> This section APPENDS below history; it does not edit it.

### Source-access note

- **PDF read in full** via `pdftotext "docs/papers/bimodal-ser/pdfs/06-wavfusion.pdf" -` (arXiv:2412.05558v1,
  11 pp incl. all 6 tables + Eqs 1–15 + reference list). Local PDF = arXiv preprint.
- **Provenance / venue check:** the paper is published as **MMM 2025 (MultiMedia Modeling), Springer LNCS,
  DOI 10.1007/978-981-96-2071-5_24** (Li, Luo, Xia). WebSearch `"WavFusion wav2vec 2.0 … IEMOCAP MELD MMM
  2025"` → `link.springer.com/chapter/10.1007/978-981-96-2071-5_24`. The Springer abstract reproduces the
  **exact headline deltas** in the local PDF (IEMOCAP +0.84% ACC / +0.74% WF1; MELD +0.43% ACC / +0.44% WF1)
  → the preprint's load-bearing numbers are corroborated by the venue version. **✔ corroborated (deltas).**
  Absolute table cells (WF1 70.6 etc.) are arXiv-only but internally consistent with the corroborated deltas.
- **Journal extension exists (flag, not read):** same authors/mechanism appear as *"Improving speech emotion
  recognition using gated cross-modal attention and multimodal homogeneous feature discrepancy learning"*,
  **Applied Soft Computing 2025** (Elsevier, `S1568494625012281`) — **paywalled, HTTP 403, abstract-only, not
  bypassed.** If the gate becomes ViEmoSpeech's fusion candidate, this extension likely holds the fuller
  ablations MMM omits (std, per-class F1); worth a licensed pull later.

### What the paper actually does

**Task.** Utterance-level **categorical** emotion classification (ERC), `y_j ∈ R^c`. No V/A, no dimensional
output, no distress. Trimodal: audio (a) + text (t) + **visual (v)**.

**Architecture (Eqs 1–11).** Two encoder groups feed a modified wav2vec 2.0:
- *Auxiliary encoders (frozen):* **visual** = EfficientNet → `A-GRU-LVC` block (GRU + self-attention `X_v1`
  ⊕ a 1-D **Learnable Visual Center** local block `X_v2`, Eqs 2–4); **text** = **RoBERTa-base (frozen)** →
  GRU + self-attention (Eqs 5–6). Last dims: text 768, visual 64.
- *Major encoder (partly fine-tuned):* wav2vec 2.0. The **shallow** (original) transformer layers stay
  self-attention; the **deep** transformer layers have their self-attention **replaced by gated cross-modal
  attention**. Crucially: *"we unfreeze the parameters of the deep transformer layer in wav2vec 2.0 … the
  other layers are freezing"* (§3.2). So the audio backbone is **partially fine-tuned**, not frozen.

**Gated cross-modal fusion (the V-A mechanism, Eqs 7–11):**
```
X_a  = FST(S_a)                       # shallow-transformer acoustic features   (Eq 7)
X_F1 = CMA-T(X_a, X_t)                 # audio<-text cross-modal attention       (Eq 8)
X_F2 = CMA-V(X_a, X_v)                 # audio<-visual cross-modal attention     (Eq 9)
P    = sigmoid( FC( X_F1 (+) X_F2 ) )  # per-channel learnable gate              (Eq 10)
X_F  = P (.) X_F1 + (1 - P) (.) X_F2   # gated convex mix of the two streams     (Eq 11)
```
The gate `P` is a per-channel sigmoid on the concatenation of the two cross-modal-augmented tensors; `X_F`
convex-mixes the text-augmented and visual-augmented acoustic features to "filter out misinformation
generated during cross-modal interactions." **⚠ Eq 10 in both the arXiv PDF and OCR literally reads
`FC(X_F1 ⊕ X_F1)` — a typo; it must be `X_F1 ⊕ X_F2` (otherwise `P` never sees the visual stream). Load-bearing
for any re-implementation.**

**Homogeneous-feature-discrepancy (margin) loss (Eqs 12–15).** Unfused `X_a, X_t, X_v` pass through a shared
linear encoder `SD`; a triplet **margin loss** `L_mar` (Eq 13) pulls *same-emotion / different-modality* pairs
together and pushes *same-modality / different-emotion* pairs apart (cosine sim, margin θ). Total loss
`L_total = L_task(CE) + β·L_mar` (Eq 15). **This loss requires paired samples of the same utterance across
≥2 modalities carrying the same gold emotion.**

**Data.** IEMOCAP (12 h, 10 actors, 7,380 samples, 5-fold CV — sessions 1–4 train/val, session 5 test) and
MELD (Friends TV, ~1,400 dialogues / ~13,000 utts, 7-way, predefined splits). Metrics: ACC, Weighted-F1.

**Results (exact, table refs):**
- **IEMOCAP (Table 1):** WavFusion **ACC 70.53 / WF1 70.6**; prior SOTA M2FNet WF1 69.86 / HAAN-ERC ACC 69.69,
  WF1 69.47. Delta **+0.84 ACC / +0.74 WF1** over SOTA. **✔ corroborated** (Springer abstract).
- **MELD (Table 2):** WavFusion **ACC 66.93 / WF1 66.1**; HAAN-ERC ACC 66.5 / WF1 65.66. Delta **+0.43 ACC /
  +0.44 WF1**. **✔ corroborated** (Springer abstract).
- **Modality ablation (Table 3, IEMOCAP, WF1):** A 65.59 · T 58.63 · **V 26.31** · A+T **67.45** · A+V 64.14 ·
  A+T+V **70.6**. **≈ arXiv-only.** Note: **A+V (64.14) is *lower* than A alone (65.59)** — visual hurts
  without text; text is the load-bearing partner (+1.86 WF1 over audio-only), the full trimodal adds +5.01.
- **LVC block (Table 4):** w/o 69.84 → w/ **70.60** WF1 (+0.76). **≈ arXiv-only** (visual-only, irrelevant to us).
- **Margin-loss weight β (Table 5, WF1):** β=0 → 67.66; 0.01 → 68.39; 0.1 → 68.96; **β=1 → 70.6**; β=10 → 64.19.
  Best β=1 gives **+2.94 WF1 over β=0**; β=10 *collapses* (−3.47 vs β=1). **≈ arXiv-only.**
- **Gated attention vs concat (Table 6, the V-A ablation, WF1):** plain **concat** (12 shallow / 0 deep) = **66.78**;
  gated attention at 11/1 = 68.55 · 10/2 = 68.32 · **9 shallow / 3 deep = 70.6** · 8/4 = 69.06. Gate at the
  optimal 9/3 split beats concat by **+3.82 WF1 / +3.86 ACC**. **≈ arXiv-only** (single-run, no std).

### Parts directly useful for ViEmoSpeech (tagged by Decision ID)

1. **[V-A] The gate itself (Eqs 8–11) as a learned-fusion candidate.** Concrete, cheap (one FC + sigmoid + a
   convex mix) alternative to concatenation, with a *clean concat-vs-gated ablation* (66.78 → 70.6 WF1,
   Table 6). This is the reference comparison row for "does learned gating beat rule/concat fusion?"
2. **[V-A/V-B] Where the gate lives is load-bearing.** WavFusion does **not** bolt the gate onto frozen
   features — it **replaces self-attention inside the last 3 wav2vec2 transformer layers** and **fine-tunes
   those layers** (§3.2, Table 6's shallow/deep sweep). The +3.82 WF1 is entangled with backbone fine-tuning.
3. **[V-C] Frozen RoBERTa-base + GRU + self-attention text head** feeding cross-attention (Eqs 5–6). Direct
   analogue for a frozen **PhoBERT-over-PhoWhisper** text branch — but they use **gold IEMOCAP transcripts**,
   never ASR output.
4. **[V-A/V-E] Margin (homogeneous-discrepancy) loss (Eqs 12–15), best β=1, +2.94 WF1.** A representation-level
   auxiliary that needs *same-utterance same-emotion cross-modality* pairs — ViEmoSpeech (audio + ASR-text,
   both from the same clip with one shared gold label) **can supply the audio↔text pair** (no visual).
5. **[V-G] Modality-ablation table format (Table 3)** as the reporting template for "how much does the text
   branch carry?" — the exact register-dependent measurement the ViEmoSpeech synthesis needs.

### How each part helps ViEmoSpeech succeed

- **[V-A] Add a "gated fusion" arm to the fusion bake-off.** Alongside CASE/FAS (vn-07) and plain
  cross-attention, implement Eqs 8–11 with **two** streams only (drop `CMA-V`): re-specify the gate over
  audio↔text (e.g. `X_F = P⊙X_audio-aug + (1−P)⊙X_text-aug`). Report it against the concat and
  rule-fusion baseline rows. **Transfer risk:** WavFusion's gate arbitrates **text-aug vs visual-aug** acoustic
  streams; with visual removed the two-way convex mix loses its original meaning and must be re-specified
  (audio↔text gate). The +3.82 WF1 does **not** transfer as-is — it is a trimodal number.
- **[V-B] Do NOT copy the "graft gate into wav2vec2 + fine-tune deep layers" recipe under the frozen-backbone
  constraint.** ViEmoSpeech's default is a **frozen** WavLM/emotion2vec. WavFusion's gains are confounded with
  unfreezing the last 3 transformer layers, so its ablation cannot certify a *post-hoc, frozen-feature* gate.
  **Action:** if we want the gate, put it in a **separate fusion head on top of frozen features**, and treat
  WavFusion's number as a fine-tuned ceiling, not a frozen bar. **Transfer risk: high** — the compact-entry
  claim above that this is a "drop-in" block is wrong; it is embedded in a fine-tuned backbone.
- **[V-C] Text branch is the load-bearing partner, but they cheated on transcript quality.** Table 3 shows text
  lifts audio +1.86 WF1 while visual *hurts* (−1.45). Encouraging for our audio+text-only design — **except**
  their text = **gold transcripts**; ViEmoSpeech feeds **PhoWhisper ASR that tone-swaps at high arousal**
  (mày→máy). **Action:** run the Table-3 ablation twice — gold-caption text vs ASR text — to size the ASR
  penalty on the fusion gain. **Transfer risk: high** — the +1.86 is an upper bound we will not see on ASR.
- **[V-A/V-E] Reuse the margin loss to align audio↔ASR-text of the same clip.** With one shared gold emotion per
  clip, we can form same-emotion/different-modality positives directly. β=1 (Table 5) is the starting weight;
  β=10 collapse warns against over-weighting. **Transfer risk: medium** — cosine-margin alignment assumes the
  two modalities *should* converge; on ASR-noised text of a high-arousal clip they may legitimately diverge,
  so cap β low and gate it out on low-ASR-confidence turns.
- **[V-G] Publish the modality-ablation table** (audio-only / text-only / audio+text) on our speaker-disjoint
  holdout, as the honest register-specific answer to the cross-cutting "text-vs-audio dominance is
  register-dependent" theme (synthesis pt 1).

### Cross-ref — is fusion gain register/dataset-dependent? Where does gating help most?

**Yes, and WavFusion under-reports it.** The full fusion/gating ablation (Tables 3–6) is run **only on
IEMOCAP** (acted, scripted+improvised, clean gold transcripts, 5-fold). MELD (Friends TV, short noisy
overlapping utterances) gets **no modality/gating ablation** — only the two headline SOTA-comparison rows,
where WavFusion's absolute WF1 is much lower (66.1 vs 70.6) and the margin over SOTA shrinks (+0.44 vs +0.74).
So the evidence says **gating/fusion helps most on the cleaner, acted, gold-transcript corpus (IEMOCAP)** and
its benefit on the noisier conversational corpus (MELD) is unmeasured/smaller. This directly matches the
program-level finding (vn-08 vs vn-12 vs bimodal-01): **fusion gain is register- and transcript-quality
dependent, largest where the text channel is clean.** For ViEmoSpeech — found TV-drama audio + *noisy ASR
text* — this predicts our fusion gain sits closer to the (unmeasured, likely smaller) MELD regime than the
IEMOCAP showcase. We must measure it on our own register rather than inherit the +3.82.

### Child mental-health / ViEmoSpeech transfer lens

- **No tone, no phonation, no VN.** WavFusion has zero notion of lexical tone or voice-quality; its "extra"
  modality is **visual (faces)**, which ViEmoSpeech does not have and legally would not release. The whole
  A-GRU-LVC apparatus (Eqs 1–4, Table 4) is dead weight for us. What survives is *only* the audio↔text gate.
- **Acted, categorical, adult.** IEMOCAP/MELD are adult acted/TV emotion, no distress, no V/A, no minors —
  consistent with the rest of the set; contributes **nothing** to V-D (tone×emotion), V-F (distress
  recall-floor), or the child-register question. Its value is purely architectural (V-A) and cautionary (V-B).
- **Ethics/risk:** none specific; but the "mental health" name-check in the intro (ref 4) with a purely acted
  benchmark is the same overclaim pattern flagged for vn-10/EAA — cite as *not-our-framing*.

### Limitations & open questions for ViEmoSpeech (≥1 contradiction/gap)

- **Contradiction vs the ViEmoSpeech frozen-backbone constraint (V-B):** WavFusion's headline gain requires
  **fine-tuning the deep wav2vec2 layers** and **embedding the gate inside them** (§3.2, Table 6). It is *not*
  a frozen-feature post-hoc fusion result. Any citation of "gated fusion beats concat by +3.82 WF1" must carry
  this caveat, or it misrepresents what a frozen-backbone ViEmoSpeech would get. **This also corrects the
  archived compact entry above, which called the gate a "drop-in" block.**
- **Contradiction vs bimodal-02 ABHINAYA & vn-07 CASE on rare classes:** WavFusion reports **no per-class F1
  and no std** — on a 4–7-class imbalanced task with a single 5-fold number, the +0.74 WF1 margin is plausibly
  within CV variance, and rare-class (fear/disgust) collapse — which ABHINAYA caps at ~26–29% F1 and CASE
  shows as 0-correct — is **completely hidden**. For our distress/rare-class floor (V-F/V-E) WavFusion offers
  no evidence the gate helps the tail; it may only move the head classes.
- **Gap — ASR never confronted:** text is gold transcripts throughout; the fusion gain under **ASR tone-swap
  noise** (our actual input) is untested. Open question: does the gate learn to **down-weight** the text stream
  (drive `P→1` toward audio) when ASR is wrong, or does it propagate the error? Worth a dedicated
  ASR-confidence×gate-value analysis on our clips.
- **Gap — margin loss needs cross-modal pairs we only half-have:** designed for 3 modalities; with audio↔ASR-text
  only, the "same-emotion/different-modality" positive set is thinner and noisier (ASR text may not carry the
  emotion at all on a short interjection). Untested whether β=1 survives the 2-modality, noisy-text regime.
- **Metric mismatch:** WavFusion is WF1-on-categorical only — no CCC, no V/A, no distress — so it moves **nothing**
  on V-D/V-F/V-G's dimensional and recall-floor evaluation; it is a V-A/V-B/V-C architectural input only.
