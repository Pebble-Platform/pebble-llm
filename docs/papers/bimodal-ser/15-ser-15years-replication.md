# Paper 15 — Charting 15 Years of Progress in Deep Learning for SER: A Replication Study

- **Authors:** Andreas Triantafyllopoulos, Anton Batliner, Björn W. Schuller
- **Venue / year:** arXiv 2025 (code: github.com/CHI-TUM/ser-progress-replication)
- **Links:** abs https://arxiv.org/abs/2508.02448 · PDF `pdfs/15-ser-15years-replication.pdf`
- **Group:** survey / benchmark (reproducibility)

**Summary:** Replication study tiến bộ SER từ Interspeech 2009 Challenge, cả audio- và text-based; kết luận diminishing returns hậu-transformer và "progress" phụ thuộc cách so sánh.

**Relevance to Pebble:** Caution phương pháp luận cho mọi benchmarking claim — cùng tinh thần gold-holdout / honest-metric của repo.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Profile assembled at analysis time** (from `docs/intent/constraints.md` + `docs/spec/capabilities/voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`):
Pebble's primary program is **ordinal suicide-risk *text* classification** asking whether LLM weak labels *honestly* augment a scarce clinical gold set — bound by **gold-holdout** (train on weak/LLM labels, eval on disjoint held-out CSSRS gold), subject-level splits, **reproducible-by-construction** (pinned stack + seed + multi-fold with reported std/CIs), and ordinal-aware metrics (QWK/MAE). The adjacent **voice** stream is a frozen WavLM/emotion2vec backbone with 3 heterogeneous MTL heads (emotion CE + affect V/A **CCC** + **crisis under a hard recall floor**), balanced by Kendall uncertainty weighting; MSP-Podcast (A/V/D) + DAIC (crisis) are the named "real-label" swap targets.

### Analysis — 15 Years of SER Progress (replication)
- **Overlap:** 23% (peripheral) — D1=1, D2=0, D3=1, D4=0, D5=0, D6=0, D7=2
  - (Σwᵢ·scoreᵢ = 3·1 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·2 = 6; 6/26 × 100 = 23%)
- **Closest on:** D7 (backbone match — the study directly benchmarks *both* of Pebble's active backbones: BERT/RoBERTa/DistilBERT/Electra text encoders and wav2vec2/HuBERT SSL speech encoders) and D1 partial (it models categorical emotion *and* continuous valence/arousal/dominance, though as separate models, not joint heterogeneous heads; no safety head).
- **Best point (Framing / citation):** The paper empirically shows that "progress" claims are *conditioned on the arbitrary set of models/hyperparameters compared* — bigger/newer models are not monotonically better, single-run rankings are unstable under huge hyperparameter variance, and only bootstrap 95% CIs on the progress measures keep the story honest.
  - **How to apply to Pebble:** Cite it in the paper's evaluation-protocol / related-work section as external precedent that a headline number without CIs and without a fixed comparison set misrepresents progress — reinforcing Pebble's "multi-fold + reported std/CI, never a single-run point estimate" rule and the gold-holdout honesty thesis (an SER-domain analogue to the within-LLM 0.67 vs honest-gold 0.385 gap).
- **Caveats:** Full main body (pp. 1–11) read; not paywalled. Appendices A/B/D/E (full model list, noise-robustness detail, linguistic-content analysis) skimmed only — does not affect the scored dimensions, which come from the main body. Overlap is low by construction: no mental-health/crisis domain (D2=0), no teacher-LLM distillation (D4=0), no MTL loss balancing (D5=0), no safety/recall-floor objective (D6=0). The value is methodological (honest-eval framing) + backbone/corpus adjacency (MSP-Podcast/IEMOCAP/EmoDB are exactly the voice stream's real-label swap targets), not architectural transfer.
