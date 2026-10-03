# ViEmoSpeech — Báo cáo tổng quan dự án

> Corpus SER tiếng Việt (free-content, multi-class +V/A +distress, tone-annotated,
> CC-BY) trích từ phim TV VN + phương pháp bimodal **tone×emotion**.
> Cập nhật: 2026-07-08. Nguồn: `docs/intent/`, `docs/papers/`, `docs/tasks/`,
> `docs/spec/` (ADRs + changes).

---

# Phần 1 — Cơ sở lý luận + bài báo tham khảo

## 1.0 Đề tài này làm gì

**Bài toán.** *Speech Emotion Recognition* (SER) — nhận diện cảm xúc từ giọng nói:
máy nghe một đoạn thoại và đoán người nói đang vui, buồn, giận, sợ hay bình thường.
Ứng dụng ở tổng đài chăm sóc khách hàng, trợ lý ảo, và sàng lọc sức khoẻ tinh thần.

**Vướng ở đâu với tiếng Việt.** Muốn huấn luyện mô hình thì phải có **dữ liệu giọng
nói đã gán nhãn cảm xúc**. Tiếng Anh có nhiều bộ lớn và dùng được tự do; tiếng Việt
thì **gần như không có bộ nào vừa lấy được, vừa là lời nói tự nhiên, vừa có giấy
phép rõ ràng**. Nghĩa là ở Việt Nam, bài toán này **chưa có điểm xuất phát** — không
có dữ liệu thì không có gì để so sánh, cũng không có gì để cải tiến.

**Đề tài làm hai việc, theo thứ tự:**

1. **Xây bộ dữ liệu (ViEmoSpeech).** Lấy thoại từ phim truyền hình Việt Nam, tách
   nhạc nền, cắt thành từng câu nói của **một người**, rồi cho **người thật nghe và
   gán nhãn cảm xúc**. Sản phẩm là bộ dữ liệu công bố công khai dưới giấy phép
   CC-BY — thứ hiện chưa tồn tại cho tiếng Việt.

2. **Bài báo phương pháp trên bộ dữ liệu đó.** Chỗ này mới là phần khoa học.

**Ý tưởng khoa học trung tâm.** Tiếng Việt là **ngôn ngữ thanh điệu**: cao độ giọng
quyết định *nghĩa của từ* (ma ≠ má ≠ mà ≠ mã ≠ mạ). Nhưng cao độ **cũng chính là**
kênh mà cảm xúc dùng để bộc lộ — người ta lên giọng khi giận, chùng giọng khi buồn.
Hai thứ **giành nhau một kênh âm thanh**.

Hệ quả kéo theo: ở tiếng Việt, nghe giọng thôi **không đủ** để đoán cảm xúc như ở
tiếng Anh, vì một phần biến thiên cao độ đã bị "trưng dụng" để chở thanh điệu. Vậy
mô hình phải **dựa nhiều hơn vào nội dung lời nói** (nhánh văn bản). Đây là giả
thuyết **đo được** và **chưa ai kiểm chứng** cho bất kỳ ngôn ngữ thanh điệu nào —
đó là đóng góp mới của đề tài.

**Ràng buộc cứng, chi phối toàn bộ thiết kế.** Nguồn dữ liệu là phim **có bản
quyền**. Nên bộ dữ liệu phát hành ra ngoài **chỉ gồm đặc trưng âm thanh + mốc thời
gian + nhãn**, **không bao giờ** có file audio hay transcript đầy đủ. Toàn bộ phần
còn lại của báo cáo này đọc dưới ràng buộc đó.

## 1.1 Bài toán & khoảng trống (vì sao làm)

**ViEmoSpeech** = corpus **speech-emotion tiếng Việt đầu tiên** đồng thời:
free-content · đa lớp (emotion 7 lớp + valence/arousal + distress) · gán thanh
điệu · **license rõ (CC-BY)** — trích từ phim truyền hình VN bằng pipeline đo
được, cộng **bài báo phương pháp tone×emotion** trên đó.

Ba khoảng trống nó lấp (nguồn: [`papers/vietnamese-ser/00-GO-NO-GO-SUMMARY.md`](papers/vietnamese-ser/00-GO-NO-GO-SUMMARY.md)):

| Gap | Hiện trạng văn liệu | ViEmoSpeech |
|---|---|---|
| **Corpus** | Không corpus VN SER nào vừa *lấy được* + *nói tự do* + *license rõ* (ViSEC: mở nhưng **thiếu license**; VLSP 56h: nhãn binary + site gated) | Cắt từ phim TV → free-content + CC-BY khai báo từ commit đầu |
| **Method (tone×emotion)** | Chưa ai model hoá tone-aware SER cho *bất kỳ* ngôn ngữ thanh điệu nào | Nhánh ngữ nghĩa gánh nặng hơn khi F0 bận chở thanh điệu |
| **Crisis recall-floor** | **21/21** bài bimodal SweeP không có recall-floor-as-objective ([`papers/bimodal-ser/00-INDEX.md`](papers/bimodal-ser/00-INDEX.md)) | Distress head sàn-recall (proxy phim, không lâm sàng) |

## 1.2 Cơ sở lý luận — hook tone×emotion

**Luận điểm trung tâm (đo được, chưa ai claim):** tiếng Việt là ngôn ngữ thanh
điệu **thiên về phonation/chất giọng** (không chỉ đường F0) — Shen et al.,
**NAACL 2024** — đúng kênh mà **cảm xúc cũng dùng**. ⇒ xung đột *tone × emotion*
**giàu hơn Mandarin**, và **nhánh text/ngữ nghĩa phải gánh nhiều hơn** so với SER
phi-thanh-điệu.

**Bằng chứng sớm từ pilot** ([`tasks/vn-tv-ser-pilot.md`](tasks/vn-tv-ser-pilot.md) M3):
ASR sai **thanh điệu** đúng ở đoạn high-arousal (seg00113/114: "mày→máy, tao→tháo"
khi quát) — vừa là *rủi ro nhiễu nhánh text ở high-arousal*, vừa là *bằng chứng
thực nghiệm* cho chính giả thuyết tone×emotion.

**Mô hình cảm xúc dùng:** categorical (7 lớp) **+ dimensional** (valence/arousal
1–5, mô hình Russell) **+ distress flag** — tương thích cross-corpus với
IEMOCAP/MSP-Podcast (dùng V-A-D).

## 1.3 Prior work phải cite-and-distinguish (đe doạ novelty — framing "in the air")

1. **arXiv:2601.04564** *"When Tone and Words Disagree"* (01/2026) — bimodal
   audio+text nhưng "tone" = *tone-of-voice* (paralinguistic), **không** lexical
   tone → phải phân biệt tường minh.
2. **arXiv:2604.01711** (04/2026, VN SER + LLM reasoning) — *nêu tên* tone-confound
   trong motivation mà **không giải** → chứng minh gap có thật + niche đang mở
   nhanh (áp lực thời gian).
3. **arXiv:2412.09829** (VNU Hà Nội) — ~~PhoWhisper+PhoBERT fusion SER~~ **[đính
   chính 2026-07-10 sau deep-read — xem [vn-09](papers/vietnamese-ser/09-phowhisper-phobert-fusion.md)]:**
   bài này **đã bị tác giả rút (v2, 18/12/2024)** vì "significant inaccuracies", và
   **không phải bài SER** — nó là pipeline chấm chất lượng cuộc gọi call-center
   (Good/Neutral/Offensive), nhánh text = PhoBERT-CNN hate-speech (ViHSD), fusion =
   luật ưu tiên text viết tay **không có eval end-to-end**. ⇒ **không tồn tại "số
   baseline để vượt"**; định vị nó là *tiền lệ rule-fusion đã rút*, và baseline
   rule-fusion phải **tự re-implement §2.6** của họ trên nhãn ViEmoSpeech. Baseline
   số thực dùng vn-08 (86.6%/κ0.857, nhưng leak-inflated) + VNEMOS audio-only.

## 1.4 Phương pháp luận (kế thừa + pivot)

- **Honest evaluation** (kế thừa từ thesis archive): speaker-disjoint splits +
  held-out human gold + provenance mọi nhãn.
- **PIVOT 2026-07-07 ([ADR-003](spec/decisions/ADR-003-human-labels-drop-weak-supervision.md)):**
  bỏ weak-supervision LLM-teacher → **nhãn người là nguồn sự thật**; teacher (Opus/
  Sonnet) chỉ còn **gợi ý** trong công cụ label. Đổi lại quy mô ↔ độ tinh khiết nhãn.

## 1.5 Bài báo tham khảo — 29 PDF (mở trực tiếp)

Sweep 2026-07-02 ([index đầy đủ](papers/bimodal-ser/00-INDEX.md)); ưu tiên 2023–2026,
venue uy tín. Sát Pebble nhất: **#12 MSP-Podcast (46%)**, #10 JMIR (42%),
#05 AudioLLM reasoning (38%), #01 C²SER (35%). **Cập nhật 2026-07-10:** cả **21 bài bimodal** + **8 bài VN/thanh điệu
mới tải** đều đã có **phân tích sâu toàn văn PDF** (mục `## Deep research — full-PDF
read (2026-07-10)` trong từng file, chấm theo profile ViEmoSpeech + register V-A…V-H)
kèm **bản dịch tiếng Việt** `NN-slug.vi.md`. Tổng hợp phát hiện + synthesis:
[`docs/tasks/paper-deep-analysis.md`](tasks/paper-deep-analysis.md).

### Audio + Text (trục chính)
| # | Paper | Venue/Year | PDF |
|---|---|---|---|
| 01 | C²SER — audio-LLM + emotion2vec-S + CoT | IEEE TASLP 2025 | [pdf](papers/bimodal-ser/pdfs/01-c2ser.pdf) |
| 02 | ABHINAYA — SSL+LLM fusion, imbalance-aware | Interspeech 2025 | [pdf](papers/bimodal-ser/pdfs/02-abhinaya-ser-challenge.pdf) |
| 03 | EAA — dual cross-attn audio-LLM, mental-health | Interspeech 2025 | [pdf](papers/bimodal-ser/pdfs/03-eaa-emotion-aware-audio-llm.pdf) |
| 04 | MDAT — cross-language low-resource SER | preprint 2024 | [pdf](papers/bimodal-ser/pdfs/04-mdat-cross-language-ser.pdf) |
| 05 | Speech Emotion Reasoning — multitask AudioLLM | arXiv 2025 | [pdf](papers/bimodal-ser/pdfs/05-speech-emotion-reasoning-audiollm.pdf) |
| 06 | WavFusion — gated cross-modal attention | MMM 2025 | [pdf](papers/bimodal-ser/pdfs/06-wavfusion.pdf) |
| 07 | Bimodal Connection Attention Fusion | arXiv 2025 | [pdf](papers/bimodal-ser/pdfs/07-bimodal-connection-attention.pdf) |
| 08 | Graph Fusion + Prosodic Features | Interspeech 2025 Challenge | [pdf](papers/bimodal-ser/pdfs/08-graph-fusion-prosodic-ser.pdf) |
| 09 | BLSP-Emo — empathetic speech-language model | arXiv 2024 | [pdf](papers/bimodal-ser/pdfs/09-blsp-emo.pdf) |

### Survey / Benchmark / Reproducibility
| # | Paper | Venue/Year | PDF |
|---|---|---|---|
| 10 | SER in Mental Health — systematic review | JMIR Mental Health 2025 | [pdf](papers/bimodal-ser/pdfs/10-jmir-ser-mental-health-review.pdf) |
| 11 | Bridging Text & Speech — RoBERTa+WavLM fusion | J. Intelligence 2025 | [pdf](papers/bimodal-ser/pdfs/11-bridging-text-speech-fusion.pdf) |
| 12 | **MSP-Podcast Corpus** — categorical + continuous VAD | arXiv 2025→IEEE TAC | [pdf](papers/bimodal-ser/pdfs/12-msp-podcast-corpus.pdf) |
| 13 | Multimodal ERC Survey | EMNLP 2025 Findings | [pdf](papers/bimodal-ser/pdfs/13-mmerc-survey-emnlp25.pdf) |
| 14 | Multi-modal Conversational ER Survey | ACM TOIS | [pdf](papers/bimodal-ser/pdfs/14-mcer-survey-acm-tois.pdf) |
| 15 | 15 Years of SER Progress — replication | arXiv 2025 (Schuller) | [pdf](papers/bimodal-ser/pdfs/15-ser-15years-replication.pdf) |
| 16 | Databases for SER — 50+ corpora review | Data (MDPI) 2025 | [pdf](papers/bimodal-ser/pdfs/16-ser-databases-review.pdf) |

### Audio-Visual (đối chứng — fusion mechanism transferable)
| # | Paper | Venue/Year | PDF |
|---|---|---|---|
| 17 | RJCMA — recursive cross-modal attn, CCC | CVPRW 2024 (ABAW6) | [pdf](papers/bimodal-ser/pdfs/17-rjcma.pdf) |
| 18 | Joint Multimodal Transformer | CVPRW 2024 | [pdf](papers/bimodal-ser/pdfs/18-joint-multimodal-transformer.pdf) |
| 19 | HiCMAE — SSL contrastive masked AE | Information Fusion 2024 | [pdf](papers/bimodal-ser/pdfs/19-hicmae.pdf) |
| 20 | AVT-CA — audio-video transformer cross-attn | arXiv 2024 | [pdf](papers/bimodal-ser/pdfs/20-avt-ca.pdf) |
| 21 | Hybrid Multi-Attention AV-ER | Mathematics (MDPI) 2025 | [pdf](papers/bimodal-ser/pdfs/21-hybrid-multi-attention-avser.pdf) |

### Vietnamese SER + thanh điệu (8 PDF mới tải 2026-07-10, đều có deep-read + bản .vi)
| # | Paper | Venue/Year | Vai trò | PDF |
|---|---|---|---|---|
| 06 | Shen — Encoding of Lexical Tone in SSL | NAACL 2024 | Tiền đề phonation-heavy (V-B/V-D) | [pdf](papers/vietnamese-ser/pdfs/06-shen-lexical-tone-ssl.pdf) |
| 07 | CASE/FAS — When Tone and Words Disagree | arXiv 2026 | Đối thủ kiến trúc gần nhất; cite-and-distinguish | [pdf](papers/vietnamese-ser/pdfs/07-case-tone-words-disagree.pdf) |
| 08 | Human-Guided LLM Reasoning VN SER | arXiv 2026 | VN SER mới nhất; κ0.857/86.6% (leaky) | [pdf](papers/vietnamese-ser/pdfs/08-human-guided-reasoning-vnser.pdf) |
| 09 | PhoWhisper+PhoBERT (VNU) — **đã rút** | arXiv 2024 (withdrawn) | Không phải SER; rule-fusion tiền lệ | [pdf](papers/vietnamese-ser/pdfs/09-phowhisper-phobert-fusion.pdf) |
| 10 | VN Depression Dynamic-CBAM (VNEMOS) | arXiv 2024 | Baseline audio-only VN (leaky UA0.87) | [pdf](papers/vietnamese-ser/pdfs/10-vn-depression-dynamic-cbam.pdf) |
| 11 | THAI-SER corpus | arXiv 2025 | Tiền lệ corpus ngôn ngữ thanh điệu (CC-BY-SA) | [pdf](papers/vietnamese-ser/pdfs/11-thai-ser-corpus.pdf) |
| 12 | Emotionally Incongruent Speech (SLM eval) | arXiv 2025 | Contrastive "semantics dominate" | [pdf](papers/vietnamese-ser/pdfs/12-emotionally-incongruent-slm.pdf) |
| 13 | Chang — Mandarin tone×emotion acoustics | PLOS ONE 2023 | Tiền đề thực nghiệm F0-channel (V-D) | [pdf](papers/vietnamese-ser/pdfs/13-chang-mandarin-tone-emotion.pdf) |

**Scoping nội bộ (không PDF, sweep 2026-07-02):** thiết kế corpus + prior art thanh điệu —
[01 VN-SER corpora](papers/vietnamese-ser/01-vn-ser-corpora-benchmarks.md) ·
[02 tonal-language SER](papers/vietnamese-ser/02-tonal-language-ser-prior-art.md) ·
[03 VN text/ASR](papers/vietnamese-ser/03-vn-text-asr-building-blocks.md) ·
[04 corpus design](papers/vietnamese-ser/04-pioneer-corpus-design.md) ·
[05 scale plan](papers/vietnamese-ser/05-scale-plan.md).

---

# Phần 2 — Danh sách công việc + tiến độ

## 2.1 Tổng quan trạng thái

| Khối | Nội dung | Trạng thái |
|---|---|---|
| A | Pipeline trích xuất (video→clip sạch) | ✅ **Xong** (chạy local + kernel Kaggle) |
| B | Corpus 2 series | ✅ **3611 utt** (đang mở rộng) |
| C | Pivot phương pháp (human labels) | ✅ **Chốt** (ADR-003) + intent updated |
| D | Công cụ human-labeling | ✅ **Phase 0–5 xong**; phase 4 export chưa |
| E | Related-work / scoping | ✅ **Xong** (21 bimodal + VN scoping) |
| F | Label human thật (dựng gold/train) | 🔄 **Đang chạy** (user label) |
| G | Train + eval bimodal | ⬜ **Chưa** |
| H | Viết paper (dataset + method) | ⬜ **Chưa** |

## 2.2 Chi tiết

**A — Pipeline trích xuất** (`scripts/vietnamese-ser/`, `kaggle/…`; [capability](spec/capabilities/extraction-pipeline.md)):
ffmpeg → Demucs (tách nhạc) → silero VAD → **turn-split v2** (pyannote diarization)
→ PhoWhisper-base ASR → align YouTube caption → gợi ý 2-teacher.
- Yield thoại sạch: **33%** (ep01 11.9/35.6′); sau turn-split v2: **175 utt/10.3′**, 100% đơn-giọng.
- Similarity PhoWhisper↔YouTube: mean 87.2 (base đủ, không cần -medium).
- κ 2-teacher (lịch sử, tiền-pivot): ~0.68–0.70.

**B — Corpus:** 2 series hoàn tất (**3611 utt**) + Kaggle packager đa-series (v2).
Scale plan **P1 = 3 bộ/120 tập → ~18k utt / 23.8h** (~36 GPU-h).

**C — Pivot ADR-003:** nhãn người = nguồn sự thật; teacher = gợi ý. Intent sửa:
`constraints.md` §2–5, `invariants.md` I2–I4/I6, capability. ADR liên quan:
[001 blind-gold](spec/decisions/ADR-001-blind-gold-annotation.md) (superseded) ·
[002 whole-series test-split](spec/decisions/ADR-002-whole-series-speaker-disjoint-gold.md).

**D — Công cụ label** `tools/labeler/` ([change 003](spec/changes/003-human-labeling-tool/README.md) + [004](spec/changes/004-labeler-refactor/README.md)):
FastAPI backend (server/store/episodes/audio) + frontend ES-module; `state.jsonl`
nguồn sự thật. Tính năng: label (teacher gợi ý read-only) · recut+text (F1) ·
progress (F2) · reject (F3) · split (F5) · editable speaker (F6) · export.

## 2.3 Đang chờ / blockers

- 🧑 **Chốt series test** (ADR-002, whole-series hold-out) — chặn phase 4 + I4.
- 🧑 **Corpus-size mục tiêu** — hand-label tuyến tính (~15–30h/annotator cho ~3.6k utt).
- 🔄 **Label human thật** đủ sàn ≥50 clip/lớp hiếm (ADR-002).
- ⬜ **Phase 4** — export Kaggle (nhãn human, loại rejected/test-series, strip text public) + test I4.
- ⬜ **κ human–human** — single-pass hiện tại chưa có (further work: double-annotate subset).
- ⬜ **`tests/invariants/test_speaker_disjoint.py`** (change 001, chưa dựng).
- 📧 **License ViSEC / VLSP** (nếu dùng làm đối chứng) — chờ trả lời.

## 2.4 Rủi ro

- **Media legality:** clip/media/state.jsonl **không release** (data/** gitignored); artifact = features+timestamps+labels+speaker id, CC-BY.
- **Tone-confound ở high-arousal** làm nhiễu nhánh text (cũng là điểm nghiên cứu).
- **Timing:** framing tone×emotion "in the air" (arXiv 2604.01711) → niche mở không lâu.
- **Không có crisis gold tiếng Việt** → distress chỉ là proxy phim, nói rõ trong paper.
- **Frontend labeler chưa browser-drive đầy đủ** → cần click-test khi label.
