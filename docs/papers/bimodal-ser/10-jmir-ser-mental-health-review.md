# Paper 10 — SER in Mental Health: Systematic Review of Voice-Based Applications

- **Authors:** Eric Jordan, Raphaël Terrisse, Valeria Lucarini, Motasem Alrahabi, Marie-Odile Krebs, Julien Desclés, Christophe Lemey
- **Venue / year:** JMIR Mental Health, 2025 (CC-BY)
- **Links:** abs https://mental.jmir.org/2025/1/e74260 · PDF `pdfs/10-jmir-ser-mental-health-review.pdf`
- **Group:** survey / benchmark

**Summary:** Systematic review 14 nghiên cứu SER trong mental health (gồm suicide risk, depression, psychosis); accuracy ~70–80%; cảnh báo non-comparability về phương pháp giữa các study.

**Relevance to Pebble:** Domain match gần nhất (SER × suicide risk); caution về so sánh phương pháp áp dụng cho mọi claim benchmark voice của Pebble.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

### Analysis — SER in Mental Health (systematic review)
> Supersedes the 2026-07-02 score of 31% computed against the stale text-only profile.

- **Profile scored against (assembled at analysis time):** primary **text** ordinal suicide-risk program (MentalRoBERTa/NeoBERT, teacher-LLM silver labels, gold-holdout, CORN+GCE, QWK/MAE) **+ active adjacent voice stream** (`voice-mtl-heads`): frozen WavLM-Large/emotion2vec SSL backbone + shared SUPERB trunk, three heterogeneous heads (emotion CE · affect V/A CCC · crisis BCE under a hard recall floor ≥0.90) balanced by Kendall uncertainty weighting; roadmap swaps proxy labels for MSP-Podcast (A/V/D) + DAIC (crisis).
- **Overlap:** D1=1, D2=2, D3=1, D4=0, D5=0, D6=1, D7=1 → (3+4+1+0+0+2+1)/26 × 100 = **42%** (adjacent). *(Voice-inclusive profile lifts it from peripheral to adjacent vs the stale text-only 31%: modality now matches the active voice stream, not just the text encoder.)*
- **Closest on:** D2 (mental-health/crisis domain — SER for suicide risk/SI 3/14, depression 8/14, psychosis 3/14; the nearest domain match in the sweep) and D1 (the review thoroughly motivates the **categorical emotion + dimensional/continuous valence–arousal + severity/SI** trichotomy — Fig. 2 is the Russell circumplex, IEMOCAP carries both categorical and dimensional labels — the exact head types Pebble's voice MTL instantiates; conceptual, not a single multi-head model).
- **Best point (Baseline to beat):** The review aggregates the SER-for-suicide/SI performance envelope — sensitivity ~0.86 / AUC ~0.80 (Belouali, acoustic+linguistic), balanced accuracy 81% via an emotion-finetuned **wav2vec 2.0** (Gerczuk), overall SI studies AUC ~0.8 / accuracy ~70–80% — the published bar Pebble's crisis head must be measured against.
  - **How to apply to Pebble:** When `voice-mtl-heads` swaps its proxy crisis label for real clinical labels (DAIC/MSP roadmap, M5+), report crisis recall/precision@floor against this SI-detection band (sens ~0.86 / AUC ~0.8) so the number is anchored to prior art instead of the proxy — and note wav2vec 2.0 emotion-finetuning as a same-family (WavLM/emotion2vec) backbone precedent.
- **Caveats:** Audio-only review — text-only and multimodal studies are **excluded by design**, so nothing transfers to Pebble's *text* ordinal program; the 42% overlap is entirely with the adjacent voice stream. No single reviewed study uses heterogeneous multi-head MTL, teacher-LLM distillation, or principled loss balancing (D1 is conceptual framing, D4=D5=0), and crisis studies report sensitivity but no recall *constraint* as an objective (D6 partial). Suicide-risk evidence is only 3/14 studies; high non-comparability (heterogeneous datasets/methods) and patient-selection bias (QUADAS-2: 5/14 high risk, mostly no control group / small samples). Full text read (CC-BY, open); Multimedia Appendix 2 (per-study overview table) not opened.
