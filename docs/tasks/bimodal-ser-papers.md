# Bimodal Speech Emotion Recognition — literature sweep + PDF download

- **Slug:** bimodal-ser-papers
- **Status:** done
- **Created:** 2026-07-02  ·  **Updated:** 2026-07-02
- **Owner:** Fabio / Claude

## Goal
Tìm và tổng hợp các bài báo về **bimodal Speech Emotion Recognition** (ưu tiên
speech + text — khớp với hướng voice + message của Pebble; kèm audio-visual làm
đối chứng), ưu tiên **2023–2026** và **nguồn uy tín** (IEEE
TAFFC/ICASSP/Trans., Interspeech, ACL/EMNLP, ACM MM). Tải PDF (bản arXiv /
open-access) về `docs/papers/bimodal-ser/pdfs/` và ghi mỗi bài một entry
`NN-slug.md` theo convention của repo.

## Requirements & Constraints
- **Functional:** danh sách bài báo có venue + năm + link đã verify; PDF tải về được (arXiv/OA — IEEE bản chính thường paywalled, lấy bản preprint tương đương); mỗi bài một file entry Markdown.
- **Constraints:** ưu tiên ≥2023; nguồn uy tín (IEEE, Interspeech/ISCA, ACL, ACM); theo convention `docs/papers/<stream>/NN-slug.md` + `pdfs/NN-slug.pdf`; không commit dữ liệu — PDF paper công khai thì OK (đã có tiền lệ `docs/papers/finetuning-message/pdfs/`); không tải bản vi phạm bản quyền (chỉ arXiv/OA/tác giả tự đăng).

## Milestones
- [x] M1 — Literature sweep — 3 agent `research-paper` song song (audio+text fusion; audio-visual; survey/benchmark 2023+) trả về danh sách đã rank
- [x] M2 — Chọn lọc + dedupe — 23 bài tìm được → 21 bài có PDF mở + 2 paywalled (abstract-only)
- [x] M3 — Download PDFs — 21/21 PDF tải + verify (`file` + `pdfinfo` xác nhận đúng title; 3 file MDPI phải tải qua EuropePMC render / `res.mdpi.com/d_attachment` vì mdpi.com chặn bot)
- [x] M4 — Entries — 21 entry compact `docs/papers/bimodal-ser/NN-slug.md` + index `00-INDEX.md`
- [x] M5 — Analysis top picks — 5 agent `analysis-paper` song song (01, 02, 03, 10, 17) — **superseded bởi M6** (chấm theo profile text-only stale)
- [x] M6 — Re-score 5 bài với skill đã sửa (profile assemble từ intent + capabilities) — block trong entry đã thay, bảng M6 ở dưới

## Decision Log
- **2026-07-02 — Root-cause fix theo hướng user chỉ (profile đọc từ intent, không hardcode):** thay vì vá snapshot profile trong skill, sửa `analysis-paper` (skill + agent), `research-paper` (skill + agent) và `deep-read-paper` (agent) để **assemble profile lúc chạy** từ `docs/intent/constraints.md` + `docs/spec/capabilities/*.md` (text: ordinal-modeling/data-and-labeling/label-quality; voice: voice-multimodal) và phải in profile đã assemble ra output cho auditable. D7 mở rộng: backbone match với *stream đang active bất kỳ* (text BERT-family / voice emotion2vec-WavLM). Rejected: chỉ update đoạn profile hardcode (sẽ stale tiếp — đúng lỗi vừa xảy ra).
- **2026-07-02 — Phát hiện rubric analysis-paper lỗi thời (user flag):** claim "Pebble text-only" trong M5 truy về Pebble profile hardcode trong `.claude/skills/analysis-paper/SKILL.md` — chỉ mô tả stream NeoBERT text, thiếu stream voice active (WavLM/emotion2vec, `docs/tasks/voice-mtl-heads.md`). Điểm M5 v1 bị bias thấp với bài speech → re-score bằng skill đã sửa (xem bảng M5).
- **2026-07-02 — Stream mới `docs/papers/bimodal-ser/`:** tránh đụng dãy số 24–39 của stream `voice`; đánh số lại từ 01. Rejected: nhét vào `voice/` (rối numbering).
- **2026-07-02 — "Bimodal" hiểu chính là speech+text:** đây là cấu hình khớp Pebble (voice + message); audio-visual vẫn quét làm đối chứng nhưng ưu tiên thấp hơn. Rejected: chỉ audio-visual.
- **2026-07-02 — PDF lấy bản arXiv/OA thay vì IEEE Xplore:** IEEE paywalled, không có subscription trong môi trường này; preprint tương đương là chuẩn cho mục đích related-work.

## Open Questions
(none hiện tại)

## Research Findings

### Finding 1 — Audio+Text bimodal SER (research-paper agent, 2026-07-02)

**Scope note từ agent:** đã đối chiếu `docs/related-work-voice-multimodal.md` để tránh trùng — các bài đã có ở đó (Zhao co-attention wav2vec2+BERT Interspeech 2022, MulT ACL 2019, Kim & Kang 2022, Sun 2023, Dutta & Ganapathy ICASSP 2025, Gómez-Zaragozá Interspeech 2025) KHÔNG lặp lại. Danh sách dưới là bài mới, 2023–2026, rank theo độ gần Pebble.

1. **C²SER: Steering Language Model to Stable Speech Emotion Recognition via Contextual Perception and Chain of Thought** — Zhao, Zhu, Wang et al. — IEEE TASLP 2025 — Whisper semantic + emotion2vec-S acoustic (emotion2vec = backbone Pebble đã chọn); CoT + self-distillation — https://arxiv.org/abs/2502.18186 — PDF: https://arxiv.org/pdf/2502.18186 (open)
2. **ABHINAYA — A System for SER In Naturalistic Conditions Challenge** — Dutta, Balaji, R, Salinamakki, Ganapathy — Interspeech 2025 — speech-SSL + text-LLM + fused speech-text, imbalance-aware losses (map sang crisis-class imbalance của Pebble) — https://arxiv.org/abs/2505.18217 — PDF: https://arxiv.org/pdf/2505.18217 (open)
3. **EAA: Emotion-Aware Audio LLMs with Dual Cross-Attention and Context-Aware Instruction Tuning** — Du, Lu, Zhou, Gao — Interspeech 2025 — dual cross-attention acoustic+semantic, motivation mental-health monitoring — https://www.isca-archive.org/interspeech_2025/du25b_interspeech.html — PDF: https://www.isca-archive.org/interspeech_2025/du25b_interspeech.pdf (open)
4. **Cross-Language SER Using Multimodal Dual Attention Transformers (MDAT)** — Zaidi, Latif, Qadir — preprint (under review IEEE TAFFC), 2024 — cross-modal attention, minimal target-domain data (low-resource adaptation) — https://arxiv.org/abs/2306.13804 — PDF: https://arxiv.org/pdf/2306.13804 (open, preprint-only)
5. **Beyond Classification: Towards Speech Emotion Reasoning with Multitask AudioLLMs** — Zhang et al. (A*STAR) — arXiv 2025 — reasoning-augmented supervision, gần silver-labeling Gemini-teacher của Pebble — https://arxiv.org/abs/2506.06820 — PDF: https://arxiv.org/pdf/2506.06820 (open, preprint-only)
6. **WavFusion: Towards wav2vec 2.0 Multimodal SER** — Li, Luo, Xia — MMM 2025 — gated cross-modal attention, IEMOCAP/MELD — https://arxiv.org/abs/2412.05558 — PDF: https://arxiv.org/pdf/2412.05558 (open)
7. **Bimodal Connection Attention Fusion for SER** — Luo, Phan, Wang, Reiss (QMUL) — arXiv 2025 — connection network + contrastive audio-text alignment; NOTE: cặp near-duplicate 2503.05858 / 2503.06405 cùng nhóm — cần xác nhận bản nào supersede — https://arxiv.org/abs/2503.05858 — PDF: https://arxiv.org/pdf/2503.05858 (open, preprint-only)
8. **Enhancing SER with Graph-Based Multimodal Fusion and Prosodic Features** — (challenge-system, Interspeech 2025 SER-Naturalistic Challenge) — Wav2Vec2/HuBERT/WavLM/Whisper/XEUS + RoBERTa qua graph attention — https://arxiv.org/abs/2506.02088 — PDF: https://arxiv.org/pdf/2506.02088 (open)
9. **BLSP-Emo: Towards Empathetic Large Speech-Language Models** — Wang, Liao, Huang et al. — arXiv 2024 — two-stage speech-LM, empathetic response — https://arxiv.org/abs/2406.03872 — PDF: https://arxiv.org/pdf/2406.03872 (open, preprint-only)
10. **Multimodal Emotion Recognition: Integrating Speech and Text for Improved VAD Prediction** — Awatef, Hayet, Zied — Annals of Telecommunications 2025 — continuous VAD regression, early/late fusion — https://link.springer.com/article/10.1007/s12243-025-01069-1 — **PAYWALLED, không có PDF mở** → không tải, chỉ ghi abstract-only.

**Synthesis của agent:** hữu ích nhất cho Pebble: (1) C²SER (validate emotion2vec trong audio-LLM), (2) ABHINAYA (blueprint speech-LLM+text-LLM+fusion, imbalance-aware), (3) EAA (dual cross-attention, mental-health framing).

### Finding 2 — Surveys / benchmarks / reproducibility (research-paper agent, 2026-07-02)

Không trùng với related-work hiện có (các bộ đó là text-only NLP). 4 góc tìm: survey fusion, benchmark/dataset, reproducibility, mental-health domain. Link đã verify (MDPI 403 với bot nhưng OA thật — tải bằng curl với UA thường).

1. **SER in Mental Health: Systematic Review of Voice-Based Applications** — Jordan et al. — JMIR Mental Health 2025 — 14 studies gồm cả suicide risk; domain match gần Pebble nhất — https://mental.jmir.org/2025/1/e74260 — PDF: https://mental.jmir.org/2025/1/e74260/PDF (open, CC-BY)
2. **Bridging Text and Speech for Emotion Understanding: Explainable Multimodal Transformer Fusion (RoBERTa + WavLM)** — Pandey, Singh, Kaur — Journal of Intelligence (MDPI) 2025 — audio+text fusion + attribution; venue tier thấp hơn nhưng topical rất gần — https://www.mdpi.com/2079-3200/13/12/159 — PDF: https://www.mdpi.com/2079-3200/13/12/159/pdf (OA, MDPI chặn bot; mirror PMC12733550)
3. **The MSP-Podcast Corpus** — Busso et al. — arXiv 2025 (submitted IEEE TAC) — dataset paper canonical, categorical + continuous VAD (tiền lệ gần dual-head của Pebble) — https://arxiv.org/abs/2509.09791 — PDF: https://arxiv.org/pdf/2509.09791
4. **Multimodal Emotion Recognition in Conversations: A Survey** — Wu et al. — EMNLP 2025 Findings — map fusion methodologies text+audio(+visual) — https://arxiv.org/abs/2505.20511 — PDF: https://arxiv.org/pdf/2505.20511
5. **A Comprehensive Survey on Multi-modal Conversational Emotion Recognition with Deep Learning** — Shou et al. — ACM TOIS (accepted; arXiv 2312.05735) — taxonomy fusion + datasets IEMOCAP/MELD — https://arxiv.org/abs/2312.05735 — PDF: https://arxiv.org/pdf/2312.05735
6. **Charting 15 Years of Progress in Deep Learning for SER: A Replication Study** — Triantafyllopoulos, Batliner, Schuller — arXiv 2025 — replication study, caution cho benchmarking claims; có code — https://arxiv.org/abs/2508.02448 — PDF: https://arxiv.org/pdf/2508.02448
7. **Review and Comparative Analysis of Databases for SER** — Serrano et al. — Data (MDPI) 2025 — 50+ corpora comparison — https://doi.org/10.3390/data10100164 — PDF: https://www.mdpi.com/2306-5729/10/10/164/pdf (OA, MDPI chặn bot)

Flagged nhưng loại: George & Ilyas Neurocomputing 2023 (paywalled, không có bản OA).

**Synthesis của agent:** đọc sâu trước: #1 (JMIR — domain match) và #2 (fusion RoBERTa+WavLM); #3 là citation bắt buộc nếu eval trên MSP-Podcast.

### Finding 3 — Audio-visual bimodal SER, đối chứng (research-paper agent, 2026-07-02)

Rank theo độ transferable của fusion mechanism sang audio+text của Pebble.

1. **RJCMA — Recursive Joint Cross-Modal Attention for Dimensional Emotion Recognition** — Praveen & Alam — CVPRW 2024 (ABAW6, hạng 2 VA challenge) — continuous valence/arousal + CCC loss (analogue continuous-score heads của Pebble); fusion modality-agnostic — https://arxiv.org/abs/2403.13659 — PDF: https://arxiv.org/pdf/2403.13659
2. **Joint Multimodal Transformer for Emotion Recognition in the Wild** — Waligora et al. — CVPRW 2024 — key-based cross-attention giữa backbone từng modality; block dễ port sang text+audio nhất — https://arxiv.org/abs/2403.10488 — PDF: https://arxiv.org/pdf/2403.10488
3. **HiCMAE — Hierarchical Contrastive Masked Autoencoder for SSL Audio-Visual Emotion Recognition** — Sun, Lian, Liu, Tao — Information Fusion 2024 — pretrain cheap → fine-tune scarce labels (cùng logic warm-start của Pebble) — https://arxiv.org/abs/2401.05698 — PDF: https://arxiv.org/pdf/2401.05698
4. **Segment-Level Attention on Bi-Modal Transformer Encoder** — Hsu & Wu — IEEE TAFFC 2023 — segment-level attention gated by emotional consistency — https://ieeexplore.ieee.org/document/10075429/ — **PAYWALLED, không tìm được PDF mở** → abstract-only.
5. **AVT-CA — Audio-Video Transformer Fusion with Cross Attention** — Dhanith et al. — arXiv 2024 (preprint-only) — hierarchical attention + cross-attention, code mở — https://arxiv.org/abs/2407.18552 — PDF: https://arxiv.org/pdf/2407.18552
6. **Hybrid Multi-Attention Network for Audio-Visual Emotion Recognition** — Moorthy & Moon — Mathematics (MDPI) 2025 — venue tier thấp, fallback reference — https://www.mdpi.com/2227-7390/13/7/1100 — PDF: https://www.mdpi.com/2227-7390/13/7/1100/pdf

**Synthesis của agent:** RJCMA + Joint Multimodal Transformer là 2 bài đáng đọc nhất; HiCMAE nếu quan tâm pretraining strategy.

## Shortlist chốt (M2 — 2026-07-02)

21 bài có PDF mở được tải về `docs/papers/bimodal-ser/pdfs/`; 2 bài paywalled ghi abstract-only (Awatef 2025 Annals Telecom; Hsu & Wu IEEE TAFFC 2023). Đánh số 01–21 theo nhóm: 01–09 audio+text (trục chính), 10–16 survey/benchmark, 17–21 audio-visual (đối chứng).

## Analysis results (M5) — ❌ SUPERSEDED, chỉ giữ làm trace

> **Đừng dùng bảng này.** Chấm theo Pebble profile text-only đã stale trong skill cũ
> (user flag 2026-07-02 — xem Decision Log). Kết quả hiện hành: bảng **M6** ở section
> dưới; block phân tích trong từng entry `docs/papers/bimodal-ser/NN-*.md` cũng đã
> được thay bằng bản M6.

| # | Paper | Overlap | Best transferable point |
|---|---|---|---|
| 01 | C²SER (IEEE TASLP 2025) | **31% — adjacent/peripheral** | **Two-teacher agreement filter cho silver labels**: chạy 2 teacher độc lập (Emotion2Vec acoustic + GLM-4 text), chỉ giữ nhãn khi 2 bên đồng ý — chuyển thẳng sang stage silver-label Gemini của Pebble (thêm teacher/pass thứ 2, gate theo agreement). D4 là driver chính (4/8 điểm). |
| 02 | ABHINAYA (Interspeech 2025) | **12% — peripheral** | Bake-off 3 loss chống imbalance (26:1): weighted CE vs weighted focal vs **vector-scaling/logit-adjustment** — kết quả phụ thuộc backbone: encoder LLM/text tách lớp tốt sẵn hưởng lợi từ VS hơn focal → thử VS loss cho crisis head trên NeoBERT thay vì mặc định class-weighted CE. |
| 10 | JMIR SER Mental Health review (2025) | **31% — peripheral** | **Citation cho framing ordinal**: review dựa RDoC/HiTOP — suicide risk là continuum/severity spectrum, model trong review predict severity liên tục (PHQ-8, NSA-16) — cite ở related-work để biện minh về mặt tâm thần học cho ordinal head + continuous-score head của Pebble. Lưu ý: review audio-only (loại trừ text/multimodal), chỉ 3/14 study về suicide risk. |
| 17 | RJCMA (CVPRW 2024) | **19% — peripheral** | **CCC loss** (`1 − ρc`) thay MSE cho continuous head — modality-agnostic, plug vào MTL loss sum. Fusion recursive KHÔNG chuyển được (cần ≥2 modality); entry đã được agent chỉnh lại claim. |

**Tổng kết M5:** không bài nào vượt band peripheral/adjacent (cao nhất 31%). **⚠️ Lưu ý quan trọng về điểm số:** các agent chấm theo "Pebble profile" trong `.claude/skills/analysis-paper/SKILL.md` — profile này chỉ mô tả stream text (NeoBERT/finetuning-message), **chưa cập nhật stream voice đang active** (`docs/tasks/voice-mtl-heads.md`: WavLM/emotion2vec + 3 head, affect head đã dùng CCC + Kendall). Vì vậy điểm của các bài speech-centric bị **bias thấp hệ thống** (D7 chỉ tính text encoder), và vài nhận định con bị lệch: CCC loss [17] không phải "điểm mới để adopt" — voice stream đã dùng; giá trị thật của [17]/[03] là pattern fusion cho bước voice+text sắp tới, không phải "tương lai xa". Điểm actionable đứng vững bất kể bias: (1) two-teacher agreement filter cho silver labels [01], (2) vector-scaling loss cho crisis head text [02] — và nên thử cả cho crisis head voice, (3) citation RDoC/HiTOP biện minh ordinal framing [10], (4) bidirectional dual cross-attention + residual concat làm default cho fusion voice+text [03].
| 03 | EAA (Interspeech 2025) | **12% — peripheral** | Ablation chốt hướng fusion: **bidirectional dual cross-attention** (0.687) > single-direction (0.610/0.671) > self-attention (0.675); concat residual features gốc + fused. Đính chính: dual cross-attention của EAA fuse HAI speech encoder (HuBERT+BEATs), không phải audio+text — bank cho voice extension tương lai. |

## Analysis results (M6 — re-score với profile assemble từ intent/capabilities, supersede M5)

| # | Paper | M5 (stale text-only) | M6 (voice-aware) | Thay đổi chính |
|---|---|---|---|---|
| 01 | C²SER (IEEE TASLP 2025) | 31% | **35%** | D7 1→2 (Emotion2Vec-S = extension của chính backbone voice stream, checkpoint public). **Best point đổi:** swap frozen extractor sang **Emotion2Vec-S** (thêm category-level contrastive loss, Table V thắng emotion2vec thường + WavLM-base) — drop-in, tôn trọng non-goal "backbone frozen", A/B được trong Kaggle run `voice-mtl-heads` đang chờ. Two-teacher agreement filter tụt xuống secondary (vẫn áp dụng cho text silver-label). |
| 02 | ABHINAYA (Interspeech 2025) | 12% | **19%** | D7 0→2 (WavLM-Large — trùng đúng frozen backbone của voice stream). **Best point đổi hẳn:** baseline to beat — WavLM-Large speech-only đạt ~34.43 val / 33 test macro-F1 trên MSP-Podcast 8-class, chính backbone + dataset mà `voice-mtl-heads` sắp chuyển sang; kèm thử attentive-statistics pooling thay masked-mean. Imbalance-loss bake-off tụt xuống secondary. |
| 03 | EAA (Interspeech 2025) | 12% | **19%** | D7 0→2 (HuBERT/BEATs = SSL speech backbone cùng họ WavLM/emotion2vec của voice stream). Best point giữ nguyên (bidirectional dual cross-attention + residual concat) nhưng giờ là near-term cho bước fusion voice+text, không phải footnote. |
| 10 | JMIR SER Mental Health review (2025) | 31% | **42% — adjacent** (bài duy nhất vượt band peripheral) | D1 0→1 (trichotomy categorical + dimensional V/A + severity/SI ≈ đúng 3 head types của voice stream). **Best point đổi:** baseline-to-beat cho crisis head — envelope SI-detection đã publish: sensitivity ~0.86 / AUC ~0.8 (Belouali), balanced acc 81% với wav2vec2 emotion-finetuned (Gerczuk) — anchor khi `voice-mtl-heads` chuyển sang nhãn clinical thật (DAIC). Citation RDoC/HiTOP tụt xuống secondary. |
| 17 | RJCMA (CVPRW 2024) | 19% | **19%** (giữ số, sửa cơ sở) | Điểm không đổi nhưng lập luận đảo: match dời từ "analog text yếu" sang **trùng trực tiếp affect head của voice stream + đúng cặp fusion voice+text**. CCC loss bị RETIRE khỏi best point (voice affect head đã dùng sẵn). **Best point mới:** fork code public RJCMA (github.com/praveena2j/RJCMA, ABAW6 hạng 2) làm template joint cross-modal attention cho bước fusion WavLM/emotion2vec + NeoBERT — điều mà bản phân tích text-only đã kết luận sai là "không chuyển được". |

**Tổng kết M6 (so với M5):** re-score với profile voice-aware đổi kết quả đáng kể — JMIR lên **42% adjacent** (cao nhất sweep), C²SER 35%, ABHINAYA/EAA 19%, RJCMA giữ 19% nhưng sửa cơ sở. Quan trọng hơn %: **4/5 best point đổi hẳn sang hướng voice/fusion**, cho ra danh sách hành động mới cho `voice-mtl-heads`: (1) A/B **Emotion2Vec-S checkpoint** làm frozen extractor [01]; (2) anchor emotion head vs **WavLM-Large MSP-Podcast ~34/33 macro-F1** + thử attentive-statistics pooling [02]; (3) anchor crisis head vs **envelope SI-detection sens ~0.86 / AUC ~0.8** khi có nhãn DAIC [10]; (4) khi fusion voice+text: fork **RJCMA joint cross-modal attention** [17] và/hoặc dùng **bidirectional dual cross-attention + residual concat** [03]. Bài học hệ thống: profile stale làm sai không chỉ điểm số mà cả *kết luận chuyển giao* — 2 trong số đó (CCC "nên adopt" trong khi đã dùng; fusion "không chuyển được" trong khi là forward direction) đã bị đảo hoàn toàn.

## Completed Work
- 2026-07-02 — Tạo tracking doc + kick off 3 research-paper agents.
- 2026-07-02 — 3 agent trả 23 bài (10 audio+text, 7 survey/benchmark, 6 audio-visual); findings paste đầy đủ ở trên.
- 2026-07-02 — Tải 21/21 PDF mở về `docs/papers/bimodal-ser/pdfs/` (verify bằng `pdfinfo` — đúng title, đủ trang). 3 file MDPI bị chặn bot: #11 lấy qua `europepmc.org/articles/PMC12733550?pdf=render`, #16/#21 qua `res.mdpi.com/d_attachment/...`.
- 2026-07-02 — Viết 21 entry compact + `docs/papers/bimodal-ser/00-INDEX.md` (bảng theo nhóm + mục paywalled + gợi ý đọc trước).

- 2026-07-02 — M5: 5 agent analysis-paper chấm overlap (01: 31%, 10: 31%, 17: 19%, 02: 12%, 03: 12%) — superseded bởi M6 (profile stale).
- 2026-07-02 — Sửa root-cause theo user: 5 file skill/agent (`analysis-paper` skill+agent, `research-paper` skill+agent, `deep-read-paper` agent) chuyển sang assemble profile từ intent/capabilities lúc chạy; lưu memory `skills-read-profile-from-intent`.
- 2026-07-02 — M6: re-score 5 bài (01: 35%, 10: **42% adjacent**, 02: 19%, 03: 19%, 17: 19%) — block mới đã thay block cũ trong từng entry, 4/5 best point đổi sang hướng voice/fusion (xem bảng M6).

## Remaining Action Items
(hết — task done. Follow-up tùy chọn: resolve cặp near-duplicate arXiv 2503.05858 vs 2503.06405 của paper 07; xin institutional access cho 2 bài paywalled; cân nhắc đưa 4 điểm actionable của M5 vào backlog experiment — đặc biệt vector-scaling loss cho crisis head và two-teacher agreement filter.)
