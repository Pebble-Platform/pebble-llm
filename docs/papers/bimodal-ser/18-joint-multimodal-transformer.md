# Paper 18 — Joint Multimodal Transformer for Emotion Recognition in the Wild

- **Authors:** Paul Waligora, Haseeb Aslam, Osama Zeeshan, Soufiane Belharbi, Alessandro Lameiras Koerich, Marco Pedersoli, Simon Bacon, Eric Granger
- **Venue / year:** CVPRW 2024
- **Links:** abs https://arxiv.org/abs/2403.10488 · PDF `pdfs/18-joint-multimodal-transformer.pdf`
- **Group:** audio-visual (đối chứng)

**Summary:** Key-based cross-attention giữa transformer backbone từng modality (face+voice, Affwild2), bắt quan hệ intra- + inter-modal.

**Relevance to Pebble:** Block cross-attention đơn giản, dễ port nhất để ghép audio branch vào text branch hiện có.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled Pebble profile (at analysis time):**
- *Primary (intent, `constraints.md`):* ordinal suicide-risk **text** classification; LLM/weak silver labels honestly augmenting a scarce clinical gold set; **gold-holdout** eval; ordinal-aware throughout (QWK/MAE); subject-level splits; BERT-family encoder.
- *Adjacent voice stream (`voice-multimodal.md` → `voice-mtl-heads.md`):* frozen WavLM-Large / emotion2vec backbone + shared trunk, **3 heterogeneous heads** — emotion CE, affect **valence+arousal with CCC loss**, crisis BCE under a **hard recall floor (0.90)** — balanced by **Kendall uncertainty weighting**. Forward direction: voice+text fusion.

### Analysis — Joint Multimodal Transformer (JMT)
- **Overlap:** 15% (peripheral) — D1=1, D2=0, D3=1, D4=0, D5=0, D6=0, D7=0
  - Computed: (3·1 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·0) / 26 × 100 = 4/26 × 100 = 15%.
- **Closest on:** D1 (continuous affect regressed with **CCC loss** — the exact objective of Pebble's voice *affect* head) and D3 (Affwild2 as an in-the-wild continuous valence/arousal corpus).
- **Best point (Method to adopt):** The JMT fusion block — key-based cross-attention between two per-modality transformer streams, **plus a third "joint representation" branch** (concatenated features fed back through the cross-attention) whose sole job is to inject redundancy and make fusion robust when one modality is noisy/missing; ablations isolate it at **+1.3–1.8% over a vanilla cross-attention transformer** and fusion beats every unimodal baseline.
  - **How to apply to Pebble:** Use this as the template for the deferred **voice+text fusion** — cross-attend the frozen voice-encoder stream against the NeoBERT text stream and add the concatenated joint branch as the noise-robustness mechanism for when the voice modality is absent/degraded; keep the shared **CCC loss** on the affect target the fusion inherits from the voice affect head.
- **Caveats:** Full PDF read (open, not paywalled). Everything transfers only to the *adjacent voice/fusion* stream, not the primary text program — hence peripheral. **No** heterogeneous multi-head MTL, **no** loss balancing (single-task CCC per experiment, so D5=0), **no** teacher/silver-label distillation (D4=0), **no** mental-health/crisis domain or recall constraint (D2=D6=0). Backbone does **not** match Pebble's voice SSL stack — audio branch is ResNet18 on spectrograms, not WavLM/emotion2vec (D7=0). Reported numbers are on Affwild2 (V/A) and BioVid pain, both gated/external, so they are not a directly comparable baseline for Pebble's RAVDESS proxy-label runs.

## Deep research — full-PDF read (2026-07-10)

> Read against the **current ViEmoSpeech profile** (7-class + V/A 1–5 + distress; tone×emotion bimodal
> audio+text/ASR; V-A…V-H register) — the "Analysis (overlap with Pebble)" block above uses the **stale**
> pre-pivot text-stream profile (D1–D7) and is retained only as history. This section is authoritative.
> Audio-VISUAL control paper: transferable = the fusion mechanism (V-A) and the CCC V/A objective (V-G);
> the visual stream is the slot ViEmoSpeech fills with a text/ASR stream.

### Source-access note

- **PDF read in full** via `pdftotext docs/papers/bimodal-ser/pdfs/18-joint-multimodal-transformer.pdf`
  (local = arXiv:2403.10488v3, 20 Apr 2024) — method §3 (Eqs 1–3), all seven tables, references.
- **Web-validated** against the venue version (CVPRW 2024, ABAW6 workshop):
  - Query `Joint Multimodal Transformer key-based cross-attention Affwild2 valence arousal CCC Waligora
    CVPRW 2024` → CVF Open Access page
    `openaccess.thecvf.com/content/CVPR2024W/ABAW/html/Waligora_Joint_Multimodal_Transformer_for_Emotion_Recognition_in_the_Wild_CVPRW_2024_paper.html`
    (HTTP 403 to the fetch tool) + arXiv HTML mirror `arxiv.org/html/2403.10488`. The HTML mirror confirmed:
    **Affwild2 official val CCC V 0.717 / A 0.614 / avg 0.666; test CCC V 0.472 / A 0.443 / avg 0.458;
    Biovid JMT 89.1% vs vanilla-transformer 87.8% vs concat 83.5%; +7% over Joint Cross Attention [46]
    (0.369); audio backbone = ResNet18 on spectrograms; text modality = not used.** [corroborated].
  - Head-to-head with #17 (RJCMA) taken from that paper's own validated deep-read section
    (`docs/papers/bimodal-ser/17-rjcma.md`; RJCMA test mean **0.5807**, V 0.542 / A 0.619, 2nd ABAW6). [corroborated].
- No number was fabricated; every load-bearing figure below carries a table ref + status.

### What the paper actually does

- **Task.** Two dimensional/ordinal affect tasks, both **audio-visual (no text)**: (1) continuous
  **valence/arousal on Aff-Wild2** (ABAW6 track, face + voice), CCC-scored; (2) **pain-intensity estimation
  on BioVid Heat Pain Part A** (face + EDA physiological signal), accuracy-scored. Same LIVIA/ETS-Montréal
  lab as #17 (Granger et al.); both descend from the CVPR-2022 "Joint Cross Attention [46]" (Praveen 2022).
- **Fusion mechanism — the JMT block (§3.2, the V-A payload).** Two frozen per-modality backbones emit
  `f_A`, `f_B` (dim 512 each). A **third "joint" branch** is built by concatenation and FC-reduction:
  - **Eq 1:** `f_J = [f_B ; f_A]` (dim 1024) then FC to dim 512.
  - Three parallel encoders (one each for `f_A`, `f_B`, `f_J`), each = multi-head self-attention + FFN with
    residual + LayerNorm. Attention is **key-based (Eq 2):** `Attention(Q,K,V) = softmax(K·Qᵀ / √d_k)·V`,
    and critically **the query matrix `Q` is shared across sources while `K,V` come from each modality** —
    "sharing this matrix ... helps the model add redundancy and complement the visual and audio modalities."
  - **Six cross-modal attention layers** (Q of one source shared with K,V of the other). Their six 512-d
    outputs are **stacked into a sequence, then a final self-attention block dynamically weighs them, then FC head.**
  - **Loss (Eq 3):** CCC loss `L_c = 1 − ρ_c = 1 − 2σ_xy / (σ²_x + σ²_y + (μ_x − μ_y)²)` — maximise
    concordance between prediction and ground truth. Valence and arousal are decoupled: they train separate
    configs and, for the reported ensemble, take "the best at each category" (dual model).
- **The novelty vs plain cross-attention** is exactly the `f_J` third branch: it "introduces redundancy ... so
  the model can dynamically focus on this newly introduced information in sequences where **both modalities
  are simultaneously noisy**," mitigating cross-attention's sensitivity to noisy inputs (§2.2, §3, Conclusion).
- **Backbones (frozen during fusion).** Visual = R(2+1)D and/or I3D (Kinetics-pretrained, 224×224, clip len 8);
  audio = **ResNet18 on log-power spectrograms** (DFT 1024, hop 10 ms, window 20 ms, 64×107 px, first conv
  adapted to 1-channel); BioVid physiological = a custom 1D-CNN on EDA (Table 1). Fusion trained with SGD,
  LR grid [8e-4, 6e-4, 3e-4], batch 32, ≤5 epochs early-stopping (Affwild2); ADAM LR 5e-6 batch 128 (BioVid).
- **Results.**
  - **Aff-Wild2 official validation (Table 3):** V **0.717** / A **0.614** / avg **0.666**. [corroborated] (arXiv HTML + Table 3).
  - **Aff-Wild2 test (Table 4):** V **0.472** / A **0.443** / avg **0.458**, vs challenge baseline 0.180/0.170/0.175
    and vs their re-run of **Joint Cross Attention [46] = 0.369** so JMT "**improves 7%**". [corroborated] (Table 4, §5.1).
    Note the large **val→test gap (0.666 → 0.458)** — overfitting on 341 train videos.
  - **Ablation (Tables 5–7):** JMT over vanilla multimodal transformer = **+1.8%** (R2D1 backbone) / **+1.7%**
    (I3D) on Aff-Wild2, **+1.3%** on BioVid; over plain concat = **+6%** on BioVid. [approximate] — **no std/CI,
    single split**, so these deltas sit inside likely fold variance. (Tables 5, 6, 7.)
  - **BioVid (Table 2):** JMT **89.1%** > vanilla transformer 87.8% > concat 83.5%; unimodal EDA-only 77.2%,
    visual-only 72.9% — physiological modality dominates. [corroborated] (Table 2).

### Parts directly useful for ViEmoSpeech (tagged by Decision ID)

1. **[V-A] The "joint-representation third branch" as a noise-robustness fusion template.** `f_J = [f_B;f_A]`
   (Eq 1) fed as its own encoder alongside the two per-modality encoders, with key-sharing across the six
   cross-attention blocks (Eq 2), and a final self-attention block that re-weights all six streams. This is a
   **drop-in, frozen-backbone, non-recursive** fusion head — the simplest of the three fusion templates now
   in hand (CASE/FAS Q-Former, WavFusion gate, and this). It is cheaper than #17's recursion (no `l`-loop).
2. **[V-A / contrast with #17] The explicit "both modalities simultaneously noisy" motivation.** JMT's whole
   pitch is that concatenated-redundancy protects fusion when *both* streams degrade at once — which is
   ViEmoSpeech's exact worst case (high-arousal ASR tone-swaps corrupt the text stream **while** Demucs-restored
   TV-drama audio is itself noisy). This is the one fusion paper that names the double-noise regime as its
   target, even if it never measures it.
3. **[V-G] The CCC loss `L_c = 1 − ρ_c` (Eq 3)** is byte-identical to #17's Eq 16 — a second independent CVPRW
   vote for CCC-as-training-objective for the V/A head, and their **decoupled valence/arousal** (separate
   configs, dual-model pick) is a concrete design datapoint for whether ViEmoSpeech shares or splits the V/A head.
4. **[V-B] The audio backbone is a do-NOT-copy control.** ResNet18 on log-power spectrograms, frozen — the same
   spectrogram-CNN family as #17's VGGish. It is the baseline our WavLM/emotion2vec(-S)/PhoWhisper-encoder arms
   must beat, not a design to reuse; carry it (or an MFCC-CNN, cf. vn-10) only as the floor row.

### How each part helps ViEmoSpeech succeed

- **V-A (concrete artifact = the fusion head in the method paper's ablation grid).** Add a **"JMT-joint" row**
  to the V-A fusion ladder — between "concat+FC" (bimodal-11 floor) and the recursive/Q-Former options —
  wiring frozen WavLM/emotion2vec audio features against PhoBERT-over-PhoWhisper text features, with the
  concatenated `f_J` branch as the redundancy stream. Swap the visual encoder slot for the text encoder slot;
  the block is modality-agnostic (it already runs face↔voice and voice↔EDA). Report it with the
  **ASR-error-present vs -absent slice split** (V-G), because JMT's redundancy claim is *only* interesting if
  it survives our noisy substrate — which the paper never tested.
- **V-A double-noise safeguard.** The `f_J` branch is a cheap instantiation of the audio-anchoring / modality-
  dropout safeguard that vn-12 (EMIS) and bimodal-07 (deep-supervision) demanded: when the ASR text collapses
  under a tone-swap, the joint branch still carries the audio-derived signal. Pair it with a modality-dropout
  schedule during training so `f_J` learns to compensate — this is the actionable upgrade over a plain concat.
- **V-G (artifact = the V/A head loss + eval).** Set the V/A head loss to `1 − ρ_c` (Eq 3), and note both
  CVPRW audio-visual papers **decouple valence and arousal** — for ViEmoSpeech's 1–5 discrete Russell scale,
  train one head but report V and A separately with **CCC alongside QWK/MAE** (the CCC number is not
  like-for-like with Aff-Wild2's continuous [-1,1] — our variance term is dominated by 5 bins).
- **V-B (artifact = the backbone ablation arm).** Keep JMT's ResNet18-spectrogram result as the explicit
  "shallow spectrogram-CNN floor" row so our SSL-backbone gains are legible; do not adopt it.

### Child / clinical-adjacent + tone×emotion transfer lens

- **Visual→text swap is architecturally clean but empirically unproven for audio↔text.** JMT's block is
  modality-agnostic on paper, but **every reported number is face↔voice or voice↔EDA** — never audio↔text, and
  never on a tonal language. Key-based cross-attention *should* transfer (it is just Q-sharing over two token
  sequences), but the joint-branch's redundancy benefit was demonstrated only where the two streams are
  temporally aligned dense video/signal features; ASR text is sparse, token-level, and misaligned to audio
  frames. **Transfer risk = HIGH-MEDIUM:** the mechanism ports, the *evidence* does not.
- **The no-ASR-ablation blind spot recurs — and here it is load-bearing.** JMT's central claim is noise
  robustness "when both modalities are simultaneously noisy," yet the only evidence is an **attention-weight
  visualization (Fig 4)** — no controlled noise injection, no missing-modality curve, no ASR-error stratum.
  For ViEmoSpeech this is precisely the untested regime (VN tone-swap ASR errors at high arousal). Our
  ASR-robustness ablation would be the first actual measurement of the property JMT only asserts — a genuine
  contribution, not a reproduction.
- **Tone×emotion is untouched.** No F0/phonation handling; the audio branch is a generic spectrogram CNN.
  Nothing here informs V-D — consistent with the running finding that 0/N bimodal papers measure lexical-tone×
  emotion channel competition. The F0 channel that carries VN tone is simply averaged into the spectrogram.
- **Ethics/scope.** Acted/in-the-wild YouTube affect + experimentally-induced heat pain; no clinical or
  child data, no distress construct. Nothing transfers to V-F beyond the generic caution that CCC on external
  gated corpora (Aff-Wild2, BioVid) is not a ViEmoSpeech baseline.

### Limitations & open questions for ViEmoSpeech

- **★ Contradiction (direct, same venue + same lab): the newer "joint" method LOSES to the recursive one.**
  On the **same Aff-Wild2 test set**, JMT (#18) scores mean **0.458** (V 0.472 / A 0.443) while RJCMA (#17)
  scores mean **0.5807** (V 0.542 / A 0.619) — RJCMA is **+0.12 CCC ahead**, and RJCMA is the paper that
  *adds a text modality* and *recurses*, while JMT drops text and adds only the joint-redundancy branch.
  So the stub's claim that JMT is "the easiest to port, therefore preferred" is contradicted by the benchmark:
  the simpler-to-port mechanism is also the weaker one, and the winning ingredient on the shared task is
  **exactly the text stream ViEmoSpeech must add**. This is a data point *for* investing in the text branch
  and the recursive/Q-Former fusion families, and *against* treating the plain joint-concat branch as
  sufficient. (JMT's own within-paper +7% is over the older [46] baseline, not over RJCMA.)
- **Ablation gains are within noise.** +1.3–1.8% JMT-over-vanilla, single split, **no std/CI** — echoes
  bimodal-15 (Schuller): backbone/fusion rankings are HP-unstable and small deltas do not survive resampling.
  The large **val 0.666 → test 0.458 collapse** warns that on ViEmoSpeech's small held-out gold the joint
  branch's extra parameters are an overfitting risk; require bootstrap CIs before crediting any fusion delta.
- **Aff-Wild2 test CCC ≈ 0.46–0.58 is the honest naturalistic ceiling band** for in-the-wild V/A — far below
  the leaky VN numbers (vn-08 86.6, vn-10 0.87) and consistent with MSP-Podcast (~0.72 CCC on cleaner audio,
  bimodal-12) — reinforcing that ViEmoSpeech should publish a low, honest CCC and flag the leaky comparators.
- **Open question:** JMT's public code (`github.com/PoloWlg/Joint-Multimodal-Transformer-6th-ABAW`) is a
  frozen-backbone fusion module — worth forking as the V-A "joint-concat + key-sharing" baseline row, but only
  if we can graft the text encoder into the visual slot without the dense-alignment assumption; that graft is
  the untested engineering risk.
