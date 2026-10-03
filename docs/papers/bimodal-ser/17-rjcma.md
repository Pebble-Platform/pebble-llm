# Paper 17 — RJCMA: Recursive Joint Cross-Modal Attention for Multimodal Fusion in Dimensional Emotion Recognition

- **Authors:** R. Gnana Praveen, Jahangir Alam
- **Venue / year:** CVPRW 2024 (ABAW6 — hạng 2 valence-arousal challenge)
- **Links:** abs https://arxiv.org/abs/2403.13659 · PDF `pdfs/17-rjcma.pdf`
- **Group:** audio-visual (đối chứng)

**Summary:** Recursive joint cross-modal attention, predict continuous valence/arousal với CCC loss.

**Relevance to Pebble:** Fusion modality-agnostic + head hồi quy liên tục — pattern chuyển thẳng sang audio+text cho crisis/severity head.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

### Analysis — RJCMA (recursive joint cross-modal attention, DER)
- **Supersedes the 2026-07-02 score of 19% computed against the stale text-only profile.**
- **Profile assembled at analysis time** (intent + capabilities, not remembered text-only text): (1) `docs/intent/constraints.md` — primary program is ordinal suicide-risk **text** classification (LLM silver labels honestly augmenting scarce clinical gold), bound by gold-holdout, **subject-level integrity**, ordinal-aware losses/metrics, reproducibility, clinical ethics. (2) `docs/spec/capabilities/voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md` — an **active adjacent voice stream**: frozen WavLM-Large / emotion2vec + shared trunk with **three heterogeneous heads** (emotion CE · **affect V/A regression that already uses CCC loss `1−ρc`** · crisis BCE under a hard recall floor 0.90), balanced by **Kendall uncertainty weighting**, subject-independent 10-fold. **Voice+text fusion is the named forward direction.**
- **Overlap:** D1=1, D2=0, D3=1, D4=0, D5=0, D6=0, D7=1 → `(3·1 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·1)/26 × 100` = 5/26 × 100 = **19% (peripheral)**.
- **Closest on:** D1 — RJCMA's continuous valence/arousal regression is the **direct analog of the voice stream's `affect` head** (`Linear(256,2)` V/A), not a weak "text-score" analog as the stale block claimed; and D7 — it fuses a **BERT-family text encoder with an audio stream**, the exact voice+text pairing that is Pebble's named forward direction.
- **Best point (Method to adopt):** RJCMA is a **published, code-available (github.com/praveena2j/RJCMA), ABAW6-2nd-place template for exactly the audio+text continuous-affect fusion Pebble names as its forward direction** — its joint cross-modal attention block (build a joint FC over concatenated modality features `J`, compute per-modality cross-correlation attention `H·W` against `J`, recursively refine, concatenate → head) is the transferable element that the stale text-only analysis wrongly dismissed as "not transferable."
  - **How to apply to Pebble:** When the voice stream moves from single-modality to **voice+text fusion**, fork RJCMA's joint cross-modal attention (Eqs 1–14) to wire frozen **WavLM/emotion2vec voice features + NeoBERT text features** into a joint representation, recursively refine (`l=3` was optimal in their ablation), then feed the concatenated attended features into the **existing** emotion / affect-CCC / crisis heads — a fork-and-adapt on public code, not a reimplementation. (Note: the CCC loss the *stale* block flagged as the takeaway is **already in** the voice affect head, so it is no longer the novel point.)
- **Caveats:** Full PDF read (6 pp, incl. CCC-loss Eq 16 `L = 1 − ρc` and Table 1); nothing paywalled. The **% coincides with the stale 19% but on a corrected basis** — the paper still touches **none** of Pebble's high-weight dimensions: not mental-health/crisis (Affwild2 = in-the-wild YouTube V/A; D2=0), no teacher-LLM distillation (D4=0), **no principled MTL loss balancing** (valence & arousal are plain regression outputs, no uncertainty/GradNorm — contrast the voice stream's Kendall weighting; D5=0), no safety/recall-floor objective (D6=0), and its heads are **homogeneous continuous**, not the heterogeneous emotion+affect+crisis topology, so D1=1 (partial), not 2. Backbones only **partially** match (D7=1): BERT-family text yes, but the audio backbone is **VGGish, not WavLM/emotion2vec SSL**, and BERT is used as **frozen word-level features (sum of last 4 layers), not a fine-tuned ~250M encoder**. Minor positive alignment (not scored): RJCMA partitions Affwild2 **subject-independently**, matching Pebble's subject-level-integrity constraint (I2).

## Deep research — full-PDF read (2026-07-10)

> Read against the **CVPRW 2024 / ABAW6 venue version** (CVF Open Access:
> `openaccess.thecvf.com/content/CVPR2024W/ABAW/html/Praveen_Recursive_Joint_Cross-Modal_Attention_..._CVPRW_2024_paper.html`).
> Local PDF `pdfs/17-rjcma.pdf` = arXiv:2403.13659v4 (13 Apr 2024). The headline CCC numbers, the
> "2nd place" claim, and the baseline numbers were independently confirmed against the CVF listing +
> abstract; internal per-fold tables are read from the venue PDF (arXiv v4 matches the CVF abstract).
> This section is scored against the **current ViEmoSpeech profile + V-A…V-H register** (paper-deep-analysis.md,
> 2026-07-10), superseding the stale D1…D7 "Analysis" block above. This is an **audio-VISUAL control-group**
> paper; the transferable parts are the **fusion mechanism (V-A)**, the **CCC loss for continuous V/A (V-G)**,
> and (as a negative signal) the **audio backbone choice (V-B)**.

### Source-access note

- **Extraction:** `pdftotext "docs/papers/bimodal-ser/pdfs/17-rjcma.pdf" -` (full 6-page read incl. all
  4 tables, Eqs 1–16, and both preprocessing + training sections). Formulae are printed as LaTeX inside
  the PDF, so Eqs 1–16 were read verbatim, not OCR-reconstructed.
- **Web-validated (venue = authoritative):**
  - Query `RJCMA Recursive Joint Cross-Modal Attention Aff-Wild2 CCC valence 0.542 arousal 0.619 ABAW6 second place`
    → resolved the **CVF Open Access CVPRW 2024** page + the arXiv abstract, both stating CCC **valence 0.585 (0.542)
    and arousal 0.674 (0.619)** for validation (test), "second place in the valence-arousal challenge of the 6th ABAW",
    baseline **valence 0.240 (0.211) / arousal 0.200 (0.191)**. ✔ corroborated (headline, place, baseline).
  - No preprint/venue conflict found; arXiv v4 (13 Apr 2024) == CVPRW camera-ready. Code:
    `github.com/praveena2j/RJCMA` (cited in-paper, not re-fetched — not load-bearing for any number).

### What the paper actually does

- **Task.** Dimensional Emotion Recognition (DER) on **Aff-Wild2** (ABAW6 track): regress **continuous
  valence and arousal in [-1,1]**, evaluated by Concordance Correlation Coefficient (CCC). Not categorical.
- **Three modalities, one fusion block.** Audio + **Visual** + Text, each encoded then temporally modeled
  by a **TCN**, then fused by the proposed **Recursive Joint Cross-Modal Attention (RJCMA)** (§3.4).
  - Visual: ResNet-50 (MS-CELEB-1M pretrain → FER+ fine-tune) → TCN (§3.1).
  - Audio: **VGGish** (VGG pretrained on AudioSet) on **log-mel spectrograms**, hop = 1/fps → TCN (§3.2).
  - Text: **ASR-derived.** Speech → **Vosk** ASR → punctuation/capitalization restoration →
    **BERT** word-level features = **sum of the last 4 layers** (frozen; not fine-tuned) → TCN, with
    word features time-broadcast to frame rate by ASR timestamps (§3.3, §4.2.1).
- **The RJCMA fusion mechanism (§3.4, load-bearing equations, all ✔ read verbatim from venue PDF):**
  - **Eq 1 — joint representation:** `J = FC([X_a ; X_v ; X_t]) ∈ R^{d×K}`, `d = d_a+d_v+d_t`, K frames.
  - **Eqs 2–4 — joint cross-correlation** of each modality against `J`:
    `C_a = tanh( X_aᵀ W_ja J / √d )`, likewise `C_v`, `C_t` (learnable `W_j·`).
  - **Eqs 5–7 — attention maps:** `H_a = ReLU( X_a W_ca C_a )`, likewise `H_v`, `H_t` (`W_c· ∈ R^{K×K}`).
  - **Eqs 8–10 — attended features with residual:** `X_att,a = H_a W_ha + X_a`, likewise v, t.
  - **Eqs 11–13 — recursion:** feed attended features back: `X_att,·^(l) = H_·^(l) W_·^(l) + X_·^(l-1)`, l = recursive step.
  - **Eq 14 — concatenate:** `X_att^(l) = [X_att,a^(l); X_att,v^(l); X_att,t^(l)]` → MLP regression head → valence *or* arousal.
- **The CCC loss (§4.2.3, load-bearing for V-G):**
  - **Eq 15 — metric:** `ρ_c = 2·σ²_xy / ( σ²_x + σ²_y + (μ_x − μ_y)² )` (x=predictions, y=ground truth).
  - **Eq 16 — objective:** `L = 1 − ρ_c`. Chosen explicitly *over MSE* as "the standard loss in the literature for DER."
- **Training (§4.2.2, ✔ from PDF).** Adam, weight-decay 0.001, **batch 12**, max 100 epochs + early stop; init
  LR 1e-5, min LR 1e-8; **ReduceLROnPlateau on validation CCC** (patience 5, factor 0.1) with warm-up;
  **progressive unfreezing** of backbones in 3 layer-groups; sub-sequences **K=300**, stride 200; **6-fold CV**
  (fold 0 = official split); **l=3 recursions** in all runs. **Valence and arousal trained as separate models.**
- **Dataset (§4.1, ✔).** Aff-Wild2 / ABAW6: 594 videos, ~2,993,081 frames, 584 subjects; V/A continuous [-1,1],
  labels = **average of 4 expert joystick annotations**; **subject-independent** split 356/76/162 (train/val/test).
- **Results (✔ corroborated headline; ≈ per-fold internal):**
  - Headline (abstract + CVF): **valence CCC 0.585 (0.542), arousal 0.674 (0.619)** for val (test) — but the
    val numbers 0.585/0.674 are the **best-fold (Fold 1)** figures (Table 1/Table 3), *not* the official Fold-0
    validation, which is **valence 0.455 / arousal 0.652** (Table 2). ✔ (both appear in Table 1 & Table 2).
  - Baseline: **valence 0.211 / arousal 0.191** (test, Table 4). ✔.
  - **ABAW6 test leaderboard (Table 4):** RJCMA **2nd** overall, mean 0.5807 (valence 0.5418 / arousal 0.6196);
    1st = Netease Fuxi (mean 0.6721, MAE-pretrained + ensemble, audio-visual only). ✔.
  - **Recursion ablation (Table 3, Fold 1):** l=1 mean 0.607 → l=2 0.618 → **l=3 0.629 (best)** → l=4 0.615
    (declines, attributed to over-fitting). Total lift l=1→l=3 = **+0.022 mean CCC**. ≈ (single-fold, no std).
  - **Adding text vs their own audio-visual RJCA (Table 2, test):** RJCA (their reimplementation, A+V only)
    valence 0.537 / arousal 0.576 → RJCMA (A+V+**T**) valence 0.542 / arousal 0.619. **Text added +0.005 valence,
    +0.043 arousal.** ≈ (their reimplementation, one split). This is the single most ViEmoSpeech-relevant internal number.

### Parts directly useful for ViEmoSpeech (each tagged with Decision ID + transfer risk)

1. **[V-A] The joint cross-modal attention block (Eqs 1–14) collapsed to two modalities = a drop-in
   audio↔text fusion template.** ViEmoSpeech has no visual stream, so set `X_v = ∅`: Eq 1 becomes
   `J = FC([X_a ; X_t])`, and only the audio + text branches of Eqs 2–14 survive — which is *exactly*
   Praveen's earlier 2-modality Joint Cross-Attention, here with a text branch already wired in. The
   mechanism is **modality-count-agnostic**: the joint representation `J` and per-modality cross-correlation
   `C_·` are defined over whatever modalities you concatenate. **Transfer risk — LOW-to-MEDIUM.** The math
   transfers cleanly, but (a) their fusion operates on **frame-synchronized sequences** (K=300, word features
   time-broadcast to frame rate) — our audio↔text alignment is **utterance/turn-level** (single clip, one
   ASR transcript), so we would fuse *pooled* audio + *pooled* text vectors, losing the per-frame cross-attention
   that is half the point; or we keep it sequence-level by broadcasting PhoBERT token features across WavLM
   frames via PhoWhisper word timestamps (we already have these from the ASR pipeline). (b) The recursive
   refinement bought only **+0.022 mean CCC** (Table 3) and over-fits at l=4 on 356 videos — on our smaller
   3611-utt corpus, l=1 (plain joint cross-attention, no recursion) is the honest default and l>1 needs a
   held-out-fold justification. Concrete artifact: the **learned-fusion arm** that must beat the rule-based
   PhoWhisper+PhoBERT baseline — RJCMA sits alongside CASE/FAS Q-Former, WavFusion gate, BCAF deep-supervision
   in the V-A fusion-candidate menu, as the **cross-correlation-attention** option.

2. **[V-G] The CCC loss `L = 1 − ρ_c` (Eqs 15–16) is the direct objective for our valence/arousal head.**
   This is the highest-value transfer: our V/A head regresses Russell valence/arousal, and CCC is the metric
   the profile already names for V-G eval ("CCC for V/A"). Using `1 − ρ_c` as the **training** loss (not just
   the eval metric) aligns the objective with the metric and, unlike MSE, is **scale- and shift-invariant** —
   it rewards *agreement in trend*, robust to annotator offset. RJCMA's own lift over the ABAW baseline
   (valence 0.211→0.542, arousal 0.191→0.619 test) is a clean existence proof that CCC-loss regression works
   on noisy, in-the-wild, ASR-fed multimodal affect. **Transfer risk — MEDIUM.** CCC is computed **over a
   batch/sequence** (needs variance σ²_x, σ²_y across samples), so it demands **reasonably large batches** and
   **breaks on tiny/degenerate batches** (σ²→0 when all predictions equal); our batch 12–32 on 3611 utts is
   near their batch-12 regime, workable but watch for near-constant-prediction collapse early in training.
   Bigger caveat: their V/A is **continuous [-1,1], 4-expert-averaged joystick**; **ours is 1–5 Russell,
   single-pass human-labeled, discrete/ordinal** (V-E). CCC on a 5-point discrete scale is defensible but far
   coarser — the variance term is dominated by 5 bins, so report CCC **and** an ordinal metric (QWK / MAE), and
   treat the CCC number as **not like-for-like** with Aff-Wild2 or MSP-Podcast (which is 1–7 SAM; see bimodal-12).
   Concrete artifact: the V/A head loss in the fusion training config + the V-G metric row.

3. **[V-B] The audio backbone is a *negative* signal — VGGish/log-mel + 2D-CNN is a dated control, not a
   recommendation.** RJCMA reaches 2nd place with **VGGish (AudioSet) on log-mel spectrograms** as its audio
   encoder — no WavLM, no emotion2vec, no wav2vec2. For ViEmoSpeech this is a **do-NOT-copy** data point:
   VGGish predates SSL speech encoders and captures generic audio-event structure, not phonation/voice-quality
   — precisely the channel VN tone×emotion lives in (vn-06 Shen, vn-13 Chang). **Transfer risk — HIGH if copied
   naively.** But two sub-parts *do* transfer: (a) the **TCN temporal head over frame-level embeddings** is a
   lightweight, order-preserving pooling we can put on top of frozen WavLM/emotion2vec frames instead of mean-pool;
   (b) their **progressive-unfreezing** schedule (3 layer-groups, warm-restart LR per group, best-state reload)
   is a concrete recipe for the frozen-vs-fine-tuned backbone decision (V-B). Concrete artifact: the audio-branch
   encoder choice + the frozen/FT schedule in the fusion config — RJCMA is evidence that even a *weak* audio
   encoder + strong fusion is competitive, which sharpens our ablation question "how much of the gain is fusion
   vs. backbone."

### How each part helps ViEmoSpeech succeed

- **[V-A] Fusion arm.** Add an **`rjcma_fusion` experiment** to the V-A menu: two frozen branches
  (WavLM/emotion2vec audio + PhoBERT-over-PhoWhisper text), broadcast PhoBERT token features across WavLM
  frames by ASR word-timestamps (pipeline already emits these), then Eqs 1–14 with **l=1 default**, l∈{1,2,3}
  swept only on a held-out fold. Wire the fused `X_att` into the shared trunk feeding the 7-class emotion,
  V/A-CCC, and distress heads. This is a *fork-and-adapt* on public code (`github.com/praveena2j/RJCMA`),
  not a from-scratch build — the joint-correlation block is ~10 lines.
- **[V-G] V/A head objective.** Set the valence/arousal head loss to `1 − ρ_c` (Eq 16), computed per-batch,
  and add a **guard** against constant-prediction collapse (min-variance floor / warm-up with MSE for the
  first N steps then anneal to CCC). Report CCC alongside QWK+MAE so the discrete 1–5 scale is legible.
  This directly instantiates the V-G "CCC for V/A" metric as a *trainable* objective, not just an eval.
- **[V-B] Backbone ablation design.** Use RJCMA as the **"weak-encoder + strong-fusion" control row**: run our
  fusion with (i) a VGGish/log-mel arm (their setup) vs (ii) WavLM vs (iii) emotion2vec-S — if fusion dominates,
  the tone×emotion story needs a *phonation-aware* encoder to move the needle (motivating the handcrafted
  jitter/shimmer/HNR/H1-H2 vector from vn-06). Adopt their TCN-over-frames + progressive-unfreeze recipe for
  the fine-tuned arm.

### Child mental-health lens / ViEmoSpeech transfer validity

- **Register mismatch is total on content, partial on mechanism.** Aff-Wild2 is adult, in-the-wild **YouTube
  reaction/vlog** video — no children, no clinical distress, no tonal-language phonetics, and crucially
  **audio-visual** where face dominates. Nothing about *what* is predicted transfers; only the *fusion math*
  and the *CCC objective* do. This is a **control-group** paper by design (per the task framing), and should be
  cited as method-provenance for V-A/V-G, never as an empirical anchor for VN SER.
- **Their text branch is the most ViEmoSpeech-relevant window — and it is a cautionary tale.** RJCMA's text is
  **ASR-derived (Vosk) + frozen BERT (sum of last 4 layers)**, i.e. exactly our ASR-noise regime and a *frozen*
  text encoder. Adding that text branch moved **arousal +0.043 but valence only +0.005** (Table 2, test). Read
  against the cross-cutting synthesis (theme #1, register-dependent text dominance): in a **noisy-ASR, non-fine-tuned**
  text regime, the text branch barely helps the *valence* (pleasantness) dimension — consistent with vn-08's
  "VN ASR text near-useless" pole and *opposite* to the clean-transcript text-dominance pole (bimodal-11).
  **Implication for our V-C:** a **frozen** ASR-fed text branch is near-useless for valence; PhoBERT must be
  **fine-tuned** (and regularized against tone-swap ASR noise) for the text branch to carry the load the
  tone×emotion hook needs. RJCMA is direct evidence that *frozen* text is not enough.
- **Ethics/legality.** No child data, no clinical claim, no scraped-media release issue that touches our
  constraints — Aff-Wild2 is a public academic benchmark. The only reusable practice is the **subject-independent
  split**, which matches our speaker-disjoint invariant (I2) — a small alignment, not a lesson.

### Limitations & open questions for ViEmoSpeech (incl. ≥1 explicit contradiction/gap)

- **CONTRADICTION vs our multi-task plan (V-A/V-G/V-E).** RJCMA trains **separate models for valence and
  arousal** (§4.2.2), and separate models per emotion dimension is standard in ABAW. ViEmoSpeech's whole design
  is a **single shared-trunk multi-task** model (7-class + V/A + distress). So RJCMA's fusion block and CCC loss
  transfer, but its **training topology does not** — we must fuse *once* and branch to heads, and balance V/A-CCC
  against categorical CE + distress recall-floor (an MTL loss-balancing problem RJCMA never faces, because it has
  one continuous output per model). RJCMA gives us **zero** guidance on loss-balancing across heterogeneous heads.
- **CONTRADICTION vs bimodal-11 / CASE on text-encoder handling.** RJCMA uses **frozen** BERT (sum of last 4
  layers); bimodal-11 (RoBERTa+WavLM, closest to our stack) and CASE/FAS both **fine-tune / distill** the text
  side. RJCMA's near-zero valence gain from frozen ASR-text is the empirical cost of that choice — evidence for
  the fine-tune camp. We should cite RJCMA as the "frozen text underperforms" data point, not follow its recipe.
- **GAP — no ASR-robustness analysis despite an ASR-fed pipeline.** RJCMA feeds Vosk ASR into the text branch
  but never measures how ASR errors affect CCC (no clean-vs-ASR ablation). This is the *same* gap as every fusion
  paper in the set (CASE, WavFusion, BCAF all use gold transcripts) — and it is precisely our novel contribution:
  ViEmoSpeech operates under **high-arousal tone-swap ASR errors** (mày→máy) that RJCMA's English Vosk pipeline
  never confronts. Our ASR-robustness ablation on the fusion + CCC head is genuinely unaddressed by this paper.
- **Weak internal evidence for the headline mechanism.** The recursion (the paper's named novelty over prior
  RJCA) buys **+0.022 mean CCC** on a *single fold* with no std (Table 3), and the text modality (the other
  novelty) adds **+0.005 valence** (Table 2). Both "improvements" are plausibly within fold/seed variance —
  a caution that we should **not** assume recursive depth or a bolted-on text branch will help our V/A head
  without our own held-out-fold + multi-seed measurement (the V-G protocol: speaker-disjoint 8-fold + seed std,
  per THAI-SER precedent).
- **Scale non-comparability.** Aff-Wild2 CCC is on **continuous [-1,1] 4-expert joystick** labels; our CCC will
  be on **discrete 1–5 single-pass** labels. Their 0.542/0.619 is **not** a target or a bar for us — it is only
  evidence the CCC-loss regression recipe converges. Any cross-corpus CCC comparison (Aff-Wild2 vs MSP-Podcast
  1–7 vs ours 1–5) must be flagged as scale-mismatched, same caveat we logged for bimodal-12 (MSP).
