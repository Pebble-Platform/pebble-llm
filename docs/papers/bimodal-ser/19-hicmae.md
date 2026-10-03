# Paper 19 — HiCMAE: Hierarchical Contrastive Masked Autoencoder for Self-Supervised Audio-Visual Emotion Recognition

- **Authors:** Licai Sun, Zheng Lian, Bin Liu, Jianhua Tao
- **Venue / year:** Information Fusion (Elsevier), 2024
- **Links:** abs https://arxiv.org/abs/2401.05698 · PDF `pdfs/19-hicmae.pdf` (bản arXiv; journal paywalled)
- **Group:** audio-visual (đối chứng)

**Summary:** Masked-modeling + contrastive pretraining trên audio-visual không nhãn, fine-tune trên 9 dataset categorical/dimensional.

**Relevance to Pebble:** Cùng logic "pretrain rẻ, fine-tune trên nhãn khan hiếm" như GoEmotions warm-start + Gemini silver labels.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Profile assembled at analysis time** (from `docs/intent/constraints.md` + `docs/spec/capabilities/voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`): Pebble's primary intent is *text* ordinal suicide-risk with LLM weak labels under gold-holdout/honest eval — HiCMAE touches none of that. The relevant surface is the **adjacent voice stream**: a *frozen SSL audio backbone* (WavLM-Large / emotion2vec) + shared SUPERB trunk carrying **three heterogeneous heads** — emotion (CE), affect valence/arousal (CCC), crisis (BCE under a hard recall floor) — balanced by Kendall uncertainty weighting, with **voice+text fusion as the forward direction**.

### Analysis — HiCMAE (audio-visual SSL emotion)
- **Overlap:** D1=1, D2=0, D3=1, D4=0, D5=0, D6=0, D7=1 → (3·1 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·1)/26 = 5/26 = **19% (peripheral)**
- **Closest on:** D1 (one SSL backbone serves *both* categorical emotion and *dimensional* valence — the same categorical+continuous split Pebble's voice MTL heads target, though HiCMAE fine-tunes each task separately rather than as joint heterogeneous heads) and D7 (an SSL audio(-visual) emotion backbone, same "frozen-SSL-features + downstream probe" family as WavLM/emotion2vec, but audio-*visual* not audio-only, and self-trained on VoxCeleb2 rather than a WavLM/emotion2vec checkpoint).
- **Best point (Baseline to beat):** HiCMAE reports per-dataset WAR/WF1 on exactly the corpora Pebble's voice stream uses — RAVDESS, IEMOCAP, CREMA-D, MSP-IMPROV (categorical) and valence via Pearson (dimensional) — with public code + pretrained checkpoints, i.e. a published *bimodal SSL* ceiling for SER on shared benchmarks.
  - **How to apply to Pebble:** in the `voice-mtl-heads` writeup, cite HiCMAE's RAVDESS/IEMOCAP WAR as the audio-visual SSL upper bound and frame Pebble's audio-only frozen-probe numbers as the honest, lower-resource comparator — the same "modality gap" caveat the proxy-label note already carries; do not treat it as an apples-to-apples baseline (it adds the visual channel Pebble lacks).
- **Caveats:** Journal version paywalled; scored from the arXiv PDF (abstract + Sec. 1–3 + Fig. 2 radar) — exact per-dataset tables and loss weights not fully read. D5=0/D6=0 confident (no principled MTL balancing, no safety/recall objective — HiCMAE's losses are reconstruction + contrastive, not task-balanced heads); D1 held at 1 because categorical+dimensional are separate fine-tunes, not simultaneous heterogeneous heads. No mental-health/crisis (D2=0) and no teacher-LLM distillation (D4=0).

## Deep research — full-PDF read (2026-07-10)

> Analyzed against the **current ViEmoSpeech profile + Decision Register V-A…V-H** (from
> `docs/tasks/paper-deep-analysis.md`, 2026-07-10), NOT the stale text-stream profile in the
> "Analysis" section above (which is archived and left intact). HiCMAE is an **audio-VISUAL SSL
> control** paper: it is here to test whether its self-supervised pretraining recipe, its
> hierarchical fusion, or its cross-modal contrastive objective transfer to ViEmoSpeech's
> **audio+text, no-video, frozen-backbone, VN tone×emotion** regime. Short answer: it moves V-B and
> V-A mostly as **negative / bounded** evidence, and V-D as a clarifying non-transfer.

### Source-access note

Full PDF read via `pdftotext "docs/papers/bimodal-ser/pdfs/19-hicmae.pdf" -` (arXiv:2401.05698v2,
1 Apr 2024) — method §3 (all equations), implementation §4.1, every results table (Tables 2–16),
ablations, and error analysis. The journal version is paywalled (Elsevier). Web-validated:

- **Venue/DOI** — WebSearch `HiCMAE Hierarchical Contrastive Masked Autoencoder Information Fusion
  2024`; resolved to *Information Fusion* **vol. 108, article 102382, 2024** (ScienceDirect PII
  `S156625352400160X`; ISSN 1566-2535 = Information Fusion) and OpenReview `6N6I6FjHyK`. Status ✔.
  The local PDF is the author preprint; no numeric conflict found between preprint and the venue
  abstract/figures surfaced in search.
- **Release** — WebFetch `github.com/sunlicai/HiCMAE`: **MIT license**; **pretraining code +
  downstream fine-tuning code** both public; **one base-sized checkpoint pretrained on VoxCeleb2
  (audio-visual)** released via SharePoint, plus fine-tuned CREMA-D / MAFW per-fold checkpoints and
  logs. Status ✔. **No audio-only checkpoint and no mention of audio-only usage** — the released
  artifact is an audio-visual encoder pair.

### What the paper actually does

**Objective.** Self-supervised audio-VISUAL pretraining for emotion recognition (AVER), then
per-dataset fine-tuning. Two SSL signals combined (§3.3, Eq. 11): masked audio-visual reconstruction
(MSE on masked tokens, Eq. 8) **plus** hierarchical cross-modal contrastive learning (symmetric
InfoNCE across paired audio↔video clips, Eqs. 9–10). Total loss `L = L_MAE + λ·L_HCMCL`.

**The "three-pronged" hierarchical strategy** (the novelty):
1. **Hierarchical skip connections** (U-Net-style) from encoder layers **4/7/10** into decoder layers
   2/3/4 via multi-head cross-attention (Eq. 7) — guides *intermediate* layers, not just the top.
2. **Hierarchical cross-modal contrastive learning (HCMCL)** applied at those same intermediate
   layers (not only the last), progressively narrowing the audio-video modality gap (§3.2).
3. **Hierarchical feature fusion (HFF)** at fine-tune time: the final feature is `Concat(cross-modal
   pooled a→v, v→a, learnable-weighted sum of all audio layers e_a, all video layers e_v)` (Eq. 12),
   i.e. **learnable per-layer weights over the whole encoder stack**, not just the last hidden state.

**Architecture (§4.1).** Two modality-specific Transformer encoders `Ns=10` layers + a cross-modal
fusion encoder `Nf=2` (bidirectional MHCA, Eqs. 5–6) + two lightweight decoders `Nd=4`. Three scales
by hidden width: **HiCMAE-T (C=256), -S (C=384), -B (C=512)**.

**Pretraining recipe (§4.1) — the load-bearing recipe for V-B:**
- Data: **VoxCeleb2 dev set, 1,092,009 clips** (audio-visual celebrity speech) [✔ §4.1].
- Masking: **audio 80%, video 90%** (tube masking for video, random for audio) [✔ §3.1.1].
- `λ = 0.0025`, InfoNCE temperature `τ = 0.07` [✔ §4.1].
- **100 epochs, 4× Tesla V100, batch 160, base LR 3e-4, ~5 days** [✔ §4.1]. Fine-tune: 50–100 epochs,
  batch 56, base LR 1e-3.

**Downstream results (9 datasets, categorical + dimensional).** Headline audio-visual gains
[all ✔, tables cited]:
- **CREMA-D 6-class** (acted, subject-independent 5-fold): HiCMAE-B **WAR 84.89 / UAR 84.91**, vs best
  prior SSL VQ-MAE-AV+Query2Emo 80.40 → **+4.49 WAR** (Table 6).
- **MAFW 11-class** (in-the-wild): HiCMAE-B **UAR 42.65 / WAR 56.17**, vs supervised SOTA T-MEP 37.17
  / 51.15 → **+5.48 UAR / +5.02 WAR** (Table 2).
- **DFEW**: HiCMAE-B A+V **WAR 75.01** vs T-MEP 68.85 → **+6.16 WAR** (Table 4).
- **RAVDESS** A+V WAR 87.99 (+3.19 over VQ-MAE-AV, Table 9); **IEMOCAP** 4-class A+V WAR 68.36
  (+5.62 over AVBERT, Table 10); **MSP-IMPROV** A+V WAR 74.95 (Table 8).
- **Dimensional Werewolf-XL** A+V (Table 11): HiCMAE-B **valence PCC 69.23 / CCC 64.81** but
  **arousal PCC 33.74 / CCC 31.85**, dominance PCC 40.66 / CCC 37.54 — valence >> arousal.
- **AVCAffe** A+V arousal/valence weighted-F1 43.18 / 44.20 (Table 12).

**The critical audio-only rows (buried, and decisive for us).** When only the audio encoder is
fine-tuned, HiCMAE is **worse than off-the-shelf frozen-family speech SSL**:
- CREMA-D 6-class **audio-only**: HiCMAE-B WAR **71.01** vs **WavLM-Plus 73.39**, HuBERT 72.57,
  Wav2Vec2 72.41 (Table 6). HiCMAE audio-only is ~2.4 WAR **below** WavLM-Plus.
- IEMOCAP audio-only: HiCMAE-B WAR **65.23** vs WavLM-Plus 67.12, Wav2Vec2 67.32 (Table 10).
- RAVDESS audio-only: HiCMAE-B WAR **72.29** vs WavLM-Plus 75.36 (Table 9).
- MER-MULTI (Chinese TV series) audio-only: HiCMAE-B WF1 **55.33** vs **HuBERT-CH 61.16** — the paper
  itself attributes the gap to "large domain gap between pre-training and fine-tuning" (English
  VoxCeleb2 → Chinese) [§4.2.3, ✔].

**Ablations (§4.5).** Removing all three hierarchical modules (→ vanilla AV-MAE) drops MAFW WAR
54.79 → full 56.17 = **+1.38 total**; skip connections contribute most, HFF least (Table 13). The
**contrastive loss buys little**: `λ=0` gives MAFW WAR 55.62 vs 56.17 at `λ=0.0025` (**≈+0.55 WAR**),
and `λ=0.1` collapses to 47.87 — masked reconstruction dominates, contrastive is a small supplement
(Table 14). Fusion-direction is **insensitive** (audio-first vs video-first vs default within ~0.4
WAR, Table 16). Bigger scale monotonically helps (T→S→B, Fig. 7); longer pretraining helps and
saturates ~80 epochs (Fig. 6).

### Parts directly useful for Pebble (each tagged with Decision ID + transfer risk)

1. **Hierarchical feature fusion — learnable per-layer weights over the whole encoder stack (Eq. 12).**
   `[V-B, V-A]` Instead of probing only the last hidden state of our frozen audio backbone, learn a
   softmax-weighted combination across *all* WavLM/emotion2vec layers (a SUPERB-style weighted-sum
   head). HiCMAE's ablation ranks HFF as a real if modest contributor, and it converges with vn-06
   Shen (tone peaks in *mid* layers) and bimodal-15 Schuller (SSL under-encodes pitch dynamics).
   **Transfer risk: LOW.** This is a fine-tune-head trick that works on any frozen encoder; it does
   not need HiCMAE's checkpoint or its video branch. Concrete artifact: the audio-branch pooling in
   our fusion model reads a learnable layer-weight vector, not `hidden_states[-1]`.

2. **Contrastive/masked SSL as a pretraining recipe is NOT a frozen-backbone win for us — keep
   WavLM/emotion2vec.** `[V-B, negative]` HiCMAE's *audio* encoder underperforms frozen WavLM-Plus on
   every acted/lab corpus (CREMA-D −2.4, RAVDESS −3.1, IEMOCAP −1.9 WAR). Its gains are entirely a
   **fusion-with-video** effect, unavailable to ViEmoSpeech (audio+text, no face video). **Transfer
   risk: DECISIVE non-transfer.** The recipe also costs ~480 V100-GPU-hours on a 1M-clip *audio-visual*
   corpus we do not have in Vietnamese, against a Kaggle P100 budget. Concrete action: do **not**
   spend effort SSL-pretraining a VN audio encoder from scratch for the pilot; use frozen WavLM /
   emotion2vec-S (per bimodal-01/12) and, if adapting, prefer the cheap PhoWhisper-warm domain
   adaptation route (bimodal-15) over a HiCMAE-style masked+contrastive pretrain.

3. **Bidirectional cross-modal fusion encoder (MHCA both directions, Eqs. 5–6) with
   direction-insensitivity.** `[V-A]` A 2-layer cross-attention block that reinforces each modality
   from the other is a clean learned-fusion template to sit above frozen streams — and the ablation
   result that **fusion direction barely matters** (Table 16) tells us not to over-engineer
   audio-first vs text-first ordering. **Transfer risk: MEDIUM.** In HiCMAE it is *jointly pretrained*
   inside the encoder, not grafted onto frozen features, and it fuses audio↔video (natural temporal
   correspondence) not audio↔ASR-text (noisy, semantic). Our fusion must survive tone-swap ASR noise,
   which HiCMAE never confronts (clean paired video). Concrete artifact: a 2-layer bidirectional
   cross-attention fusion arm in the V-A candidate set (alongside CASE/FAS Q-Former, WavFusion gate).

4. **Contrastive objective is cross-modal *alignment*, the opposite of tone/emotion
   *disentangling*.** `[V-D, clarifying non-transfer]` HCMCL (Eqs. 9–10) pulls paired audio+video
   *together* to shrink the modality gap — it does not separate signal factors within a modality.
   So HiCMAE's contrastive learning does **not** give us a way to pull apart the tone channel from the
   emotion channel in F0/phonation. **Transfer risk: N/A (wrong tool).** If we ever want a contrastive
   objective for V-D it must be *within-audio, factor-separating* (e.g. tone-invariant vs
   emotion-invariant contrasts), which is a different construction than HiCMAE's cross-modal InfoNCE.
   Records the negative so we don't mis-cite HiCMAE as support for a disentangling objective.

5. **Honest acted audio-only anchors for the baseline ladder.** `[V-G]` HiCMAE's audio-only
   subject-independent numbers are usable comparators for our audio branch on acted speech:
   **CREMA-D 6-class audio WAR ≈ 71–73 (HiCMAE-B 71.01, WavLM-Plus 73.39)** and **valence far harder
   than arousal from audio alone** (Werewolf-XL audio valence CCC ≈ 0.08–0.12 vs arousal CCC ≈ 0.27).
   **Transfer risk: MEDIUM** — acted, subject-independent 5-fold (not whole-series holdout), English/
   celebrity register, and *audio-only* not *audio+text*. Concrete artifact: add these as flagged
   rows in the V-G baseline table, and use the valence-hard-from-audio finding to justify leaning on
   the **text branch for valence** in ViEmoSpeech's V/A head.

### How each part helps ViEmoSpeech succeed

- **V-B (backbone).** HiCMAE settles a temptation: SSL-pretraining our own audio encoder is not worth
  it for the pilot — a self-supervised AV encoder trained on 1M clips still loses to frozen WavLM on
  audio-only SER. Default stays frozen WavLM / emotion2vec-S. What we *do* import is the cheap HFF
  head (learnable per-layer weighting) so the frozen features are read across the stack where tone
  and prosody actually live (mid-layers per vn-06/bimodal-15), not only at the top.
- **V-A (fusion).** Two concrete, low-cost additions to the fusion bake-off: (a) a 2-layer
  bidirectional cross-attention block; (b) an HFF-style multi-layer aggregation before fusion. And a
  design economy: don't tune fusion *direction* as a hyperparameter — HiCMAE shows it's second-order.
- **V-D (tone×emotion).** Negative clarity: contrastive-SSL alignment is not a disentangling
  mechanism. Our channel-competition measurement stays on the vn-06 Ridge-probe / vn-13 F0-interaction
  / vn-12 Cramér's-V instruments, not on a HiCMAE-style contrastive loss.
- **V-G (eval).** Adds honest acted audio-only anchors (CREMA-D ~71–73 WAR; valence≪arousal from
  audio) that sit far below the leak-inflated VN numbers (vn-08 86.6, vn-10 0.87), reinforcing the
  speaker-disjoint / whole-series-holdout posture.

### Child mental-health lens (ViEmoSpeech transfer validity)

ViEmoSpeech is not child-facing (the stale profile above is archived); the relevant lens is
**Vietnamese TV-drama acted speech, audio+text, tone×emotion, features-only release**. HiCMAE's
transfer validity to that lens is limited on three axes:

- **No text, no tone.** HiCMAE's second modality is **facial video**, whose *valence* signal is
  strong (Werewolf-XL valence CCC 0.65) — precisely the channel ViEmoSpeech lacks. Its whole premise
  (audio-visual correspondence as a free contrastive signal) does not exist in an audio+text corpus.
  So the paper's headline results are structurally non-portable; only the *fine-tune-side* tricks
  (HFF, cross-attention) survive the modality change.
- **Domain-gap warning is directly relevant.** HiCMAE's own MER-MULTI result — an English-VoxCeleb2
  pretrained model losing to HuBERT-CH (Chinese-pretrained) on Chinese TV-series audio (WF1 55.33 vs
  61.16) — is a clean, cited demonstration that **cross-lingual SSL transfer degrades on tonal-language
  acted media**. That is exactly ViEmoSpeech's setting (VN TV drama). It is corroborating evidence for
  a VN-adapted text/audio branch (V-C PhoBERT/ViSoBERT; V-B PhoWhisper-warm) over a generic
  English-pretrained encoder — and against expecting a foreign SSL checkpoint to just work on VN.
- **Ethics/release.** No mental-health or distress construct anywhere (categorical basic emotions +
  V/A/D dimensions on celebrity/actor video); nothing to import for V-F. The released VoxCeleb2 model
  is audio-visual face data — irrelevant to and heavier than ViEmoSpeech's features-only CC-BY release
  model (V-H), which draws instead from bimodal-16 / MSP-Podcast.

### Limitations & open questions for ViEmoSpeech (incl. contradiction/gap)

- **Contradiction vs bimodal-15 (Schuller replication):** HiCMAE reports **monotonic "bigger is
  better"** (T→S→B, Fig. 7) and "longer pretraining helps" (Fig. 6), whereas bimodal-15 found model
  UAR vs params/MACs/year ≈ **ρ≈0** across the SER field and no trustworthy leaderboard. Reconciliation:
  HiCMAE's monotonicity is *within one architecture family on its own recipe and datasets* (and on
  5-fold CV that is subject/session-independent but small-N), not a cross-model law — so it is not
  evidence against Schuller. Practical upshot for us: still **A/B on our own clips with bootstrap CIs**
  (V-G); do not assume a bigger frozen backbone wins.
- **Contradiction vs ViEmoSpeech's frozen-backbone plan:** HiCMAE is a **full fine-tune** recipe
  (discard decoders, fine-tune both encoders); it never evaluates its encoder as a *frozen* feature
  extractor, and its audio branch already trails frozen WavLM. So it offers **no evidence** that an
  SSL-pretrained-then-frozen audio encoder is competitive — the opposite of what a frozen-feature
  program would hope, and a caution against reading its gains as backbone quality rather than
  fusion-with-video.
- **Gap — contrastive ≠ disentangling (vs V-D):** the paper's contrastive objective aligns modalities;
  ViEmoSpeech's open V-D need is to *separate* the tone and emotion factors that share F0/phonation.
  HiCMAE does not touch this, and no other paper in the set does either — V-D novelty stays intact.
- **Debunked-myth flag:** the introduction leans on the Mehrabian 7%/38%/55% "words/tone/face"
  figures [refs 3,4] to motivate audio+visual dominance — a widely-criticized over-generalization.
  Our tone×emotion hook must be grounded in phonetics (vn-06 Shen, vn-13 Chang), **not** cited through
  this myth; if HiCMAE is cited, cite it for its SSL recipe and results, not that framing.
- **Open question:** HFF's learnable-layer-weight vector is the one cheap, clearly-transferable idea —
  worth a small ablation in our pilot (weighted-sum-of-layers vs last-layer) on the frozen WavLM audio
  head, to confirm the mid-layer tone/prosody benefit vn-06 and bimodal-15 predict.
