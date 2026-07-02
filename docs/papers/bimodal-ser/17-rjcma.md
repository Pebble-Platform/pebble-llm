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
