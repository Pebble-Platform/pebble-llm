# Bimodal SER — paper stream index

Literature sweep 2026-07-02 (task: `docs/tasks/bimodal-ser-papers.md`). Ưu tiên 2023–2026 + venue uy tín (IEEE, Interspeech, ACL, ACM, CVPRW). PDF (bản arXiv/OA) trong `pdfs/`, cùng số với entry.

## Audio + Text (trục chính — khớp voice + message của Pebble)

| # | Paper | Venue / Year | PDF |
|---|---|---|---|
| 01 | C²SER — audio-LLM với emotion2vec-S + CoT | IEEE TASLP 2025 | ✅ |
| 02 | ABHINAYA — speech-SSL + text-LLM + fusion, imbalance-aware | Interspeech 2025 | ✅ |
| 03 | EAA — dual cross-attention audio-LLM, mental-health framing | Interspeech 2025 | ✅ |
| 04 | MDAT — cross-language SER, low-resource adaptation | preprint (u.r. IEEE TAFFC) 2024 | ✅ |
| 05 | Speech Emotion Reasoning with Multitask AudioLLMs | arXiv 2025 | ✅ |
| 06 | WavFusion — gated cross-modal attention | MMM 2025 | ✅ |
| 07 | Bimodal Connection Attention Fusion (near-dup 2503.06405) | arXiv 2025 | ✅ |
| 08 | Graph-Based Multimodal Fusion + Prosodic Features | Interspeech 2025 Challenge | ✅ |
| 09 | BLSP-Emo — empathetic speech-language model | arXiv 2024 | ✅ |

## Survey / Benchmark / Reproducibility

| # | Paper | Venue / Year | PDF |
|---|---|---|---|
| 10 | SER in Mental Health — systematic review (gồm suicide risk) | JMIR Mental Health 2025 | ✅ |
| 11 | Bridging Text and Speech — explainable RoBERTa+WavLM fusion | J. Intelligence (MDPI) 2025 | ✅ |
| 12 | MSP-Podcast Corpus — categorical + continuous VAD | arXiv 2025 (→ IEEE TAC) | ✅ |
| 13 | Multimodal ERC Survey | EMNLP 2025 Findings | ✅ |
| 14 | Multi-modal Conversational ER Survey | ACM TOIS (arXiv) | ✅ |
| 15 | 15 Years of SER Progress — replication study | arXiv 2025 (Schuller lab) | ✅ |
| 16 | Databases for SER — 50+ corpora review | Data (MDPI) 2025 | ✅ |

## Audio-Visual (đối chứng — fusion mechanism transferable)

| # | Paper | Venue / Year | PDF |
|---|---|---|---|
| 17 | RJCMA — recursive cross-modal attention, CCC loss | CVPRW 2024 (ABAW6) | ✅ |
| 18 | Joint Multimodal Transformer — key-based cross-attention | CVPRW 2024 | ✅ |
| 19 | HiCMAE — SSL contrastive masked autoencoder | Information Fusion 2024 | ✅ |
| 20 | AVT-CA — audio-video transformer cross-attention | arXiv 2024 (preprint-only) | ✅ |
| 21 | Hybrid Multi-Attention AV-ER | Mathematics (MDPI) 2025 | ✅ |

## Paywalled — abstract-only, không có PDF mở

- **Awatef, Hayet, Zied** — Multimodal ER: Speech+Text for VAD Prediction — Annals of Telecommunications 2025 — https://link.springer.com/article/10.1007/s12243-025-01069-1 (topical fit rất cao — continuous VAD từ speech+text — cần institutional access)
- **Hsu & Wu** — Segment-Level Attention on Bi-Modal Transformer Encoder — IEEE TAFFC 2023 — https://ieeexplore.ieee.org/document/10075429/

## Gợi ý đọc trước (theo overlap M6 — profile voice-aware; chi tiết trong entry từng bài)

1. **10 JMIR review — 42% (adjacent)** — domain match SER × suicide risk; baseline-to-beat cho crisis head (sens ~0.86 / AUC ~0.8).
2. **01 C²SER — 35%** — Emotion2Vec-S checkpoint: ứng viên A/B thay frozen extractor của voice stream.
3. **02 ABHINAYA — 19%** — baseline WavLM-Large trên MSP-Podcast (~34/33 macro-F1) cho emotion head.
4. **03 EAA — 19%** — bidirectional dual cross-attention + residual concat cho bước fusion voice+text.
5. **17 RJCMA — 19%** — code public làm template joint cross-modal attention fusion.

> Điểm M5 (2026-07-02, chấm theo profile text-only stale trong skill cũ) đã bị supersede — xem Decision Log trong `docs/tasks/bimodal-ser-papers.md`.
