# Paper 12 — The MSP-Podcast Corpus

- **Authors:** Carlos Busso, Reza Lotfian, Kusha Sridhar, et al.
- **Venue / year:** arXiv 2025 (submitted IEEE Trans. Affective Computing)
- **Links:** abs https://arxiv.org/abs/2509.09791 · PDF `pdfs/12-msp-podcast-corpus.pdf`
- **Group:** survey / benchmark (dataset paper)

**Summary:** Dataset paper canonical cho MSP-Podcast: 400+ giờ, annotation categorical + continuous (valence/arousal/dominance).

**Relevance to Pebble:** Tiền lệ published gần nhất về thiết kế nhãn categorical + continuous (dual-head) — citation bắt buộc nếu eval trên MSP-Podcast.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled profile (at analysis time).** Pebble's *primary* stream is ordinal
suicide-risk **text** classification testing whether LLM/weak labels honestly
augment a scarce clinical gold set under strict **gold-holdout**, subject-level
splits, ordinal-aware metrics (QWK/MAE/macro-F1), and clinical-data ethics
(`docs/intent/constraints.md`). Its *adjacent active* **voice** stream
(`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`) attaches
**heterogeneous MTL heads on a frozen SSL backbone (WavLM-Large / emotion2vec)**:
emotion CE + **affect (valence/arousal) CCC** + crisis BCE under a **hard recall
floor**, balanced by Kendall uncertainty weighting. The voice roadmap explicitly
names **MSP-Podcast (A/V/D) as the next real-label target for the affect head**
(currently on Russell-circumplex proxy labels).

### Analysis — MSP-Podcast Corpus (Busso et al.)
- **Overlap:** D1=2, D2=0, D3=2, D4=0, D5=1, D6=0, D7=2 →
  (3·2 + 2·0 + 1·2 + 2·0 + 2·1 + 2·0 + 1·2) / 26 = 12/26 = **46% (adjacent)**
- **Closest on:** D1 (the SER baseline is a genuinely heterogeneous head set —
  categorical **focal** + continuous **CCC**, staged then jointly trained) and D7
  (baselines are **WavLM / Wav2vec2 / HuBERT ~310M SSL**, the exact backbone
  family Pebble's voice stream freezes); D3 close behind (this IS the named affect
  corpus for the V/A/D head).
- **Best point (Baseline to beat):** Section VI gives a published affect recipe +
  numbers — adapt an SSL encoder with **CCC loss to predict valence/arousal/
  dominance, then jointly train with the categorical focal head** (attribute stage
  uses a frozen encoder + per-attribute regression head), with WavLM CCC on Test1
  of **V≈0.72 / A≈0.72 / D≈0.65** (Table VII).
  - **How to apply to Pebble:** when the voice affect head swaps proxy V/A for real
    MSP-Podcast A/V/D (the roadmap's next task), adopt this staged CCC→joint recipe
    on the frozen WavLM trunk and report the affect head's CCC against these WavLM
    per-test-set numbers as the baseline to beat — turning the proxy-label mechanic
    into a real, citable affect result.
- **Caveats:** (1) No mental-health/crisis or clinical labels (D2=D6=0) — this
  corpus only fuels the **affect** head; the crisis/recall-floor head still needs a
  clinical source (e.g. DAIC). (2) Their baselines **fine-tune** the ~310M SSL,
  whereas Pebble's plan uses a **frozen** backbone + probe — the CCC numbers are a
  reference ceiling, not a like-for-like target unless the frozen-probe protocol is
  matched. (3) Access is via signed data-transfer agreement (329 groups), not a
  free download — hand to `find-dataset` to confirm the gate before relying on it.
  (4) Deep-read of pp.1–2 + 13–15 (baselines, partitions, discussion); middle
  sections (III–V annotation protocol) skimmed, so annotation-method scoring (D4)
  is from the abstract + protocol summary, not a full read.
