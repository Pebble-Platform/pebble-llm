# Bimodal SER — paper stream index

Literature sweep 2026-07-02 (task: `docs/tasks/bimodal-ser-papers.md`). Ưu tiên 2023–2026 + venue uy tín (IEEE, Interspeech, ACL, ACM, CVPRW). PDF (bản arXiv/OA) trong `pdfs/`, cùng số với entry.

> **Cập nhật 2026-07-10 (task `docs/tasks/paper-deep-analysis.md`):** cả 21 bài đã có
> **phân tích sâu toàn văn PDF** — mục `## Deep research — full-PDF read (2026-07-10)`
> trong từng `NN-*.md`, chấm lại theo profile **ViEmoSpeech** hiện hành (register
> V-A…V-H), thay các score M5/M6 cũ (chấm theo profile text-only/voice-MTL đã archive —
> giữ làm lịch sử). Mỗi bài kèm bản dịch tiếng Việt `NN-slug.vi.md`. Vài đính chính
> venue/nội dung nổi lên khi deep-read: **#04 MDAT** đã publish IEEE OJCS 2024 (không
> phải "under review TAFFC"); **#14 MCER** venue "ACM TOIS accepted" chưa kiểm chứng
> được (arXiv không có journal ref); **#03 EAA** fusion là audio↔audio (không phải
> audio↔text); **#21 HMATN** số headline stub nhầm validation-fold. Synthesis xuyên
> suốt 29 bài (21 bimodal + 8 VN) nằm ở cuối tracking doc.

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

## Xếp hạng overlap toàn sweep (M6+M7, profile voice-aware — chi tiết trong entry từng bài)

| Band | Bài |
|---|---|
| **Adjacent (40–69%)** | **12 MSP-Podcast 46%** · **10 JMIR review 42%** |
| Sát biên (35–38%) | 05 AudioLLM reasoning 38% · 01 C²SER 35% · 09 BLSP-Emo 35% |
| Giữa (23–31%) | 13 MMERC survey 31% · 16 SER databases 27% · 07 BCAF 23% · 15 replication 23% |
| Thấp (≤19%) | 02, 03, 06, 17, 19 (19%) · 18, 21 (15%) · 04, 08, 11 (12%) · 14 (8%) · 20 (4%) |

**Finding xuyên suốt:** 21/21 bài không có recall-floor-as-objective (D6) → crisis-recall floor của Pebble là gap thật trong văn liệu bimodal SER. Phương án thesis rút từ sweep: xem section M8 trong `docs/tasks/bimodal-ser-papers.md`.

> Điểm M5 (2026-07-02, chấm theo profile text-only stale trong skill cũ) đã bị supersede — xem Decision Log trong `docs/tasks/bimodal-ser-papers.md`.
