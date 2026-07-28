# Paper 02 — ABHINAYA: A System for Speech Emotion Recognition In Naturalistic Conditions Challenge

- **Authors:** Soumya Dutta, Smruthi Balaji, Varada R, Viveka Salinamakki, Sriram Ganapathy
- **Venue / year:** Interspeech 2025 (challenge system, SOTA post-challenge)
- **Links:** abs https://arxiv.org/abs/2505.18217 · PDF `pdfs/02-abhinaya-ser-challenge.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Kết hợp speech-SSL + text-LLM + fused speech-text models, ensemble majority-voting, loss chống class imbalance.

**Relevance to Pebble:** Cùng lab với bài LLM-distillation ICASSP 2025 đã cite; blueprint production cho fusion speech+text với imbalance-aware losses — map thẳng sang bài toán crisis-class imbalance.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

### Analysis — ABHINAYA (SER Naturalistic Challenge, Interspeech 2025)
> Supersedes the 2026-07-02 score of 12% computed against the stale text-only profile.

- **Profile scored against (assembled at analysis time):** (1) primary intent — honest ordinal suicide-risk **text** classification with LLM silver labels + gold-holdout eval; (2) active **voice** stream (`voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`) — heterogeneous MTL heads on a **frozen WavLM-Large / emotion2vec** backbone (emotion CE + affect **CCC** + crisis **hard recall-floor 0.90**, Kendall uncertainty weighting), currently on RAVDESS proxy labels, **named next step = swap to MSP-Podcast (A/V/D) + DAIC (crisis)**.
- **Overlap:** D1=0, D2=0, D3=1, D4=0, D5=0, D6=1, D7=2 → 19% (peripheral)
  - Formula: (3·0 + 2·0 + 1·1 + 2·0 + 2·0 + 2·1 + 1·2) / 26 × 100 = 5/26 × 100 ≈ 19%.
- **Closest on:** D7 (**WavLM-Large SSL backbone** — exact match to the voice stream's frozen encoder) and, weaker, D6/D3 (rare-class imbalance objective on a categorical emotion corpus).
- **Best point (Baseline to beat):** ABHINAYA's speech-only **S1 = WavLM-Large (317M)** with attentive-statistics pooling + a softmax emotion head scores **34.43 balanced-val / 33 test macro-F1** on **MSP-Podcast** 8-class categorical emotion — the same backbone and (per the voice roadmap) the same dataset Pebble's voice emotion head will move to.
  - **How to apply to Pebble:** When `voice-mtl-heads` swaps RAVDESS proxy labels for real MSP-Podcast (the roadmap's next task), anchor the emotion head against ABHINAYA's ~34% val / 33% test WavLM-Large single-model macro-F1 as the honest baseline, and trial its **attentive-statistics pooling** against the current masked-mean pool on the shared trunk.
- **Caveats:** Full paper read (no paywall). Score rose from 12%→19% only because the assembled profile now includes the voice stream, flipping D7 (0→2) on the WavLM backbone match; the text-primary dimensions (D1 heterogeneous heads, D2 crisis domain, D4 LLM-teacher distillation, D5 MTL gradient balancing) remain 0 — this is single-task categorical SER, and the LLMs (LLaMA-3 8B/70B, SALMONN) are encoders/classifiers, not label teachers. The baseline is **emotion-head only**: ABHINAYA has no continuous A/V/D head (despite MSP-Podcast carrying those labels) and no recall-floor/safety objective, so it is **not** a comparator for Pebble's affect-CCC or crisis heads. MSP-Podcast test labels are hidden (leaderboard-only), so numbers are balanced-val macro-F1 + hidden-test macro-F1.

## Deep research — full-PDF read (2026-07-10)

> Read against the **published Interspeech 2025 / ISCA-archive version** (`dutta25_interspeech`,
> https://www.isca-archive.org/interspeech_2025/dutta25_interspeech.pdf) alongside the local
> preprint `pdfs/02-abhinaya-ser-challenge.pdf` (arXiv:2505.18217v1). **Every load-bearing number
> below was cross-checked between the two and is identical** — there is no preprint↔published delta
> on any figure I use. Scored against the **current ViEmoSpeech profile + V-A…V-H register**
> (`docs/tasks/paper-deep-analysis.md`), not the archived text-stream profile/D-A…D-H. The
> pre-existing "Analysis (overlap)" block above is superseded for decision purposes by this section.

### Source-access note

- **PDF read in full** via `pdftotext` on the local arXiv PDF (method §3, experiments §4, all four
  tables, references). Short 5-page Interspeech system paper — read end to end.
- **Web-validated** against the venue version. Query: `ABHINAYA system Speech Emotion Recognition
  Naturalistic Conditions Challenge Interspeech 2025 44.02 macro-F1 SALMONN WavLM` → resolved the
  ISCA-archive PDF (`isca-archive.org/interspeech_2025/dutta25_interspeech.pdf`), downloaded and
  `pdftotext`-diffed. Confirmed identical: SoTA 44.02, baseline 32.93, S1 34.43, S2 37.68, "4th of
  166", "neutral ~26x fear", splits 84260/31961/3200, balanced-val 326/class, and the full Table 2
  loss grid. All ✔ **corroborated** (published = preprint here).
- Challenge framing cross-referenced to the organizer paper (Naini et al., `naini25_interspeech`,
  same proceedings) — MSP-Podcast new release, 8 categorical classes, imbalanced train / balanced test.

### What the paper actually does

**Task.** Interspeech 2025 SER-in-Naturalistic-Conditions Challenge, categorical track: 8-class
emotion (angry, contempt, disgust, fear, happy, neutral, sad, surprise) on the new **MSP-Podcast**
release. Train/val/test = **84,260 / 31,961 / 3,200** files (§4.1, ✔). Training is highly imbalanced
(**neutral ≈ 26× fear**, §3.4, ✔); test is class-balanced and **label-hidden (leaderboard-only)**.
Model selection uses a **balanced validation set of 326 utterances/class** (§4.1, ✔). Metric =
**macro-F1**.

**System = 5 heterogeneous models fused by decision-level majority vote** (Fig 1, §3). This is
**late/decision fusion, not learned feature fusion** — the ensemble vote is the top-level combiner;
the only model that fuses modalities *inside* the network is ST1:
- **S1 — WavLM-Large (317M), speech-only.** CNN feature-extractor **frozen**, transformer layers
  **fine-tuned**; **attentive statistics pooling** (Okabe 2018: attention-weighted mean **+** weighted
  std) → softmax head (§3.1.1).
- **S2 — SALMONN-13B SLLM, speech-only.** Whisper+BEATs encoder and LLaMA **frozen**; only **Q-Former
  + LoRA** (r=8, α=32, dropout 0.1) trained; last LLaMA-layer reps → attentive-stat pooling → softmax
  (§3.1.2). Best individual system.
- **T1 — LLaMA-3.3-70B-Instruct, text-only, zero-shot** on Whisper-large-v3 ASR transcripts (§3.2.1).
- **T2 — LLaMA-3.1-8B, text-only, LoRA fine-tuned**, used as an **encoder** (last-layer reps →
  attentive-stat pooling → head), not a generator (§3.2.2).
- **ST1 — SALMONN-7B, speech-text joint.** ASR transcript **appended to the speech sequence at the
  input**, LoRA fine-tuned; single jointly-trained bimodal model (§3.3).
Majority vote across the five; **S2 is the tiebreaker** (best val) (§4.2).

**Imbalance handling = loss functions only (no resampling/oversampling anywhere).** Three losses
(§3.4): **WCE** (class weight `w_c = N/(N_c·C)`); **WFL** weighted focal, `w_c(1−p)^γ`, **γ=2**;
**VS (vector-scaling / logit-adjustment)**, pre-softmax `ẑ = (N_c/N_max)^τ · z + γ·log(N_c/N)`,
**τ=0.3, γ=1** (§4.2). All fine-tuned with AdamW, LR **1e-5**, 20 epochs, 10-s audio cap, best-val-F1
checkpoint.

**Headline results (Table 1, all ✔).** Challenge baseline (WavLM+WCE) **test macro-F1 32.93**.
Best individual = S2 **val 37.68 / test 35.34**. S1 WavLM **val 34.43 / test 33**. Text-only: T1
zero-shot **val 32.78**, T2 fine-tuned **val 33.68**; joint ST1 **val 35.43**. Full **ABHINAYA
ensemble: test 44.02 (SoTA, post-challenge; 4th/166 at deadline with ST1 only 3-epochs → test
41.81)**. Gains: **+33.68% relative over baseline**; **+24.56% relative over best single model**
(35.34→44.02) (§4.3, ✔).

**Loss ablation (Table 2, ✔).** Best loss is **model-dependent**: **speech models prefer WFL** (S1
33.07/**34.43**/32.12; S2 36.34/**37.68**/33.17 for WCE/WFL/VS), **text & speech-text prefer VS** (T2
29.79/30.12/**33.68**; ST1 33.92/34.73/**35.43**). Authors' hypothesis: text starts with better class
separation (T2 zero-shot 28.47 vs S2 zero-shot 18.63), which suits logit-adjusting VS; less
discriminative speech reps benefit from sample-wise focal reweighting (§4.5).

**Rare-class analysis (Table 3, ✔).** Speech models collapse on the three rarest classes: **fear**
S1 12.22 / S2 16.79; contempt/disgust similar. **Text models rescue the tail** — zero-shot T1 gets
**fear 29.22**, beating even the full ensemble (26.41) on the single rarest class; T2 and ST1 also
lift contempt/disgust. Ensemble wins 4/8 classes overall. Removing ST1 from the vote costs ~2%
absolute (Table 4, Comb IV); the all-5 vote reaches val 42.31 (§4.8).

### Parts directly useful for ViEmoSpeech (tagged by Decision ID)

1. **[V-A] The bimodal template is a 3-branch late-fusion ensemble, and the *only* learned fusion is
   input-concatenation (ST1).** Concrete artifact: ViEmoSpeech's fusion arm = one frozen-audio +
   frozen-text jointly-trained model (ST1-shape) **plus** a majority-vote over independently
   imbalance-tuned single-modality heads. ST1 (35.43 val) beats speech-only SALMONN-7B (33.87 val,
   §4.6) by **+1.56 absolute** — the measured payoff of joint speech-text over speech-only, same
   backbone. That +1.56 is the honest bar for "does learned fusion beat the branch."
2. **[V-A/V-B] Attentive-statistics pooling (weighted mean + weighted std) is the shared, frozen-
   compatible aggregation across every fine-tuned branch** (S1/S2/T2/ST1). It is a drop-in replacement
   for masked-mean pooling on a **frozen** WavLM/emotion2vec trunk and on a **frozen PhoBERT/ViSoBERT**
   trunk — no backbone gradient required.
3. **[V-E/V-G] Imbalance is fought with loss functions, not resampling — and the best loss is
   modality-dependent.** Artifact: the 7-class categorical head gets **WFL (γ=2) on the audio branch**
   and **VS logit-adjustment (τ=0.3, γ=1) on the PhoBERT/ViSoBERT text branch**. Measured lift from
   picking the right loss per branch: S1 +2.31 absolute (32.12→34.43), ST1 +1.51 (33.92→35.43).
4. **[V-E/V-G] Decision-level majority voting is itself the biggest imbalance lever** — **+24.56%
   relative** over the best single model, and specifically because text branches carry the rare tail
   (Table 3) the vote lifts minority classes the single models drop. Artifact: a rare-class-recall
   audit that reports single-branch vs. ensemble macro-F1 *per class*, not just aggregate.
5. **[V-C] The text-LLM branch runs on ASR transcripts (Whisper-large-v3), no gold text at test, and
   fine-tuned-small-as-encoder beats zero-shot-large.** T2 (LLaMA-8B, LoRA, used as encoder) val
   33.68 > T1 (LLaMA-70B zero-shot) val 32.78 (Table 1, ✔). Artifact: ViEmoSpeech's PhoBERT/ViSoBERT
   branch as a **fine-tuned encoder over PhoWhisper transcripts** (not a prompted generator), pooled
   with attentive-stats, VS-loss trained.

### How each part helps ViEmoSpeech succeed

- **V-A fusion decision.** Adopt the ST1 pattern as the *learned-fusion* comparator to beat the
  withdrawn rule baseline (vn-09): one bimodal model that concatenates PhoWhisper transcript with the
  WavLM/emotion2vec speech sequence and trains a joint head — and wrap it in a majority-vote with an
  audio-only and a text-only head so no single modality can silently dominate. But **budget-match it**:
  ABHINAYA's ST1 is SALMONN-7B and its ensemble spans 7B/13B/70B LLMs — ViEmoSpeech's frozen
  PhoBERT-base + WavLM-Large is ~2 orders of magnitude smaller, so port the *shape* (input-concat +
  attentive-stat pool + decision vote), not the scale. Cross-attention/gated fusion (WavFusion,
  vn-07 FAS) remain the lighter alternatives to trial against ST1-concat.
- **V-B pooling.** Swap masked-mean → attentive-statistics pooling on the frozen trunks; the weighted-
  std channel is exactly the prosodic-variability signal the JMIR review (bimodal-10) flagged as the
  distress signature, so it doubles as a cheap distress-head feature.
- **V-E/V-G imbalance.** Run the loss as a **per-branch, not global** choice: WFL(γ=2) on audio,
  VS(τ=0.3,γ=1) on text — ViEmoSpeech's exact 4-model matrix. Report per-class macro-F1 single vs.
  ensemble to prove the rare-class rescue. This is the concrete imbalance-aware method + the +24.56%
  relative / +2.31 absolute macro-F1 gains the task asked me to extract.
- **V-C text robustness.** Use PhoBERT/ViSoBERT as a fine-tuned encoder over PhoWhisper output, VS-loss
  trained, attentive-pooled — ABHINAYA shows this beats a prompted large LLM and rescues the rare tail
  even when the *speech* branch fails on it.

### Child mental-health lens → ViEmoSpeech transfer-risk (7-class + V/A + distress, ≥50-clip floor, frozen backbones, PhoBERT/ViSoBERT)

- **Transfer risk on V-A (frozen backbones).** **Does not cleanly hold.** ABHINAYA's S1 34.43
  **fine-tunes the WavLM transformer stack** (only the CNN extractor is frozen) and every LLM branch
  trains LoRA adapters — none is a truly frozen backbone. ViEmoSpeech's frozen-trunk constraint will
  likely land *below* these single-model numbers; the frozen-compatible carry-over is the **pooling
  head + the loss + the ensemble**, not the reported accuracies. State this explicitly in the method
  paper: ABHINAYA numbers are a fine-tuned ceiling, not a frozen-trunk bar.
- **Transfer risk on V-C / V-D (text branch, tonal-language ASR).** ABHINAYA's ASR is **English
  Whisper-large-v3** on podcast speech; ViEmoSpeech runs **PhoWhisper on Vietnamese TV drama with
  tone-swap errors at high arousal** (mày→máy, tao→tháo). ABHINAYA's text branch is barely above
  baseline (33.68 vs 32.93) *even in the easy ASR regime* and speech beats text (37.68 > 33.68) — so
  the tonal-ASR text branch is at risk of being *weaker*, not the load-bearing branch the ViEmoSpeech
  tone-competition hook predicts. Mitigation: the tone×emotion hook says text should carry more
  because F0 is tone-occupied — but that must be **measured on VN**, because ABHINAYA is a
  counter-example where text did not dominate. Bake the vn-12 audio-anchoring safeguard (aux
  audio-only head / modality dropout) in so a weak ASR text branch cannot poison the vote.
- **Transfer risk on V-E/V-G (imbalance vs. the ≥50-clip floor).** ABHINAYA fights **26:1** imbalance
  purely post-hoc (loss + vote) and **fear still tops out at ~26–29% F1** with the entire 5-model
  machinery. That is the strongest argument *for* ViEmoSpeech's corpus-design **≥50-clip floor**
  (ADR-002): design-level balancing is a more reliable rare-class lever than any loss trick, which
  only recovers a few absolute points. Losses/ensembling are complementary, not a substitute for the
  floor. VS/WFL also apply **only to the 7-class categorical head** — the V/A regression (CCC) and the
  distress recall-floor head do not use CE-family losses, so this paper does not touch V-F.
- **Ethics / framing.** ABHINAYA is a challenge-leaderboard system with no clinical, child, or
  distress framing — MSP-Podcast is adult naturalistic podcast speech. Nothing here transfers to the
  distress-head honesty question; treat it purely as an engineering template.

### Limitations & open questions for ViEmoSpeech (incl. contradictions/gaps)

- **Contradiction vs. the ViEmoSpeech tone-channel-competition hook AND vs. vn-12 ("semantics
  dominate"):** in ABHINAYA the **speech branch beats the text branch** (S2 37.68 > T2 33.68 val;
  Table 1) and text-only barely clears the baseline. This is naturalistic English, but it is a direct
  data point that a strong ASR text branch need **not** dominate SER — reinforcing vn-08's "text
  near-useless" over vn-12's "semantics dominate," and warning ViEmoSpeech not to *assume* the
  tone-forces-text-to-carry-more claim without measuring it. (Reconciliation, consistent with the
  wave-1/2 log: "how much text carries" ≠ "how much a model relies on text.")
- **Contradiction vs. FAIIR (exemplar) and vs. vn-09 fusion:** ABHINAYA uses **no
  oversampling/resampling at all** — pure loss reweighting + logit-adjust + decision vote — whereas
  FAIIR's imbalance recipe was oversampling two of three ensemble members. ViEmoSpeech should trial
  loss-only (ABHINAYA) vs. resample-based (FAIIR) and not conflate them; ABHINAYA is the cleaner fit
  given a small floor-balanced corpus where oversampling ~50-clip classes risks overfitting.
- **Gap — frozen-backbone numbers are unknown.** ABHINAYA never reports a fully-frozen-trunk variant,
  so it gives no bar for ViEmoSpeech's actual constraint. Our frozen-WavLM + attentive-pool + WFL
  single-model number would be a novel measurement, not a reproduction.
- **Gap — no speaker-disjoint discussion, no V/A/D.** ABHINAYA inherits MSP-Podcast's challenge splits
  (speaker-disjoint by construction, 2000+ speakers) but never analyzes speaker leakage, and it does
  **categorical only** — no continuous V/A head despite MSP carrying V/A/D. So it is not a comparator
  for ViEmoSpeech's CCC V/A head or speaker-disjoint whole-series holdout (V-G); those remain anchored
  to bimodal-12 (MSP CCC) instead.
- **Gap — the 44.02 SoTA is on a hidden balanced test with 326/class.** ViEmoSpeech's honest
  speaker-disjoint, class-floored, whole-series-holdout macro-F1 is not like-for-like; use 44.02 only
  as a genre anchor ("naturalistic 8-class categorical SER lives in the low-40s macro-F1"), next to
  the leak-inflated VN numbers (vn-08 86.6, vn-10 0.87) as the opposite pole.
