# Scale plan — ViEmoSpeech corpus, tính từ SỐ ĐO THẬT của pilot ep01

- **Ngày:** 2026-07-03 · **Trạng thái:** DRAFT chuẩn bị quyết định — **GO/mức quy mô thuộc về user**
- **Căn cứ số:** pilot ep01 (`data/vietnamese-ser/pilot/ep01/report.md`, `m4_report.md`, `m4b_wer_report.md`)
- **Một câu:** biến 1 tập đã đo thành dự báo giờ/utterance/chi phí cho 1·3·6 bộ phim, mọi con số truy ngược được về bảng hằng số dưới đây (kèm phép tính, không số trần).

---

## 1. Hằng số ĐO THẬT (không ước lượng lại)

| Đại lượng | Giá trị đo | Nguồn |
|---|---|---|
| 1 tập 35.6 phút → thoại sạch | **11.9 phút** (yield 33%) | `report.md` |
| Số utterance / tập (2–10s) | **158** · median 3.9s | `report.md` |
| Auto-filter loop/unk giữ lại | **95%** | pipeline M3 |
| Đơn-người-nói (pyannote, **lạc quan** — gộp giọng nữ giống nhau) | **54%** (86/158) | `report.md` |
| Số giọng / tập | **18** | speakers.csv |
| κ 2-teacher (Opus↔Sonnet, 7 lớp) | **0.584** · 69% raw · 109/158 đồng thuận | `m4_report.md` |
| Similarity PhoWhisper↔YouTube | mean **87.2** / median **90.5** | `m4b_wer_report.md` |
| Mục tiêu §3 design doc (TRƯỚC pilot) | weak pool "50–100h (~40–80k utt)", gold 2–3k utt | `04-…§3` |

**Giả định scale:** 1 bộ phim = **40 tập** × **~36 phút/tập** (khớp 35.6 phút đo được).

---

## 2. Scale math — 1 / 3 / 6 bộ phim (phép tính hiện rõ)

Công thức 1 bộ (40 tập):
- thoại sạch = 40 × 11.9 phút = **476 phút = 476/60 = 7.93 h**
- utterance thô = 40 × 158 = **6 320 utt**
- sau auto-filter 95% = 6 320 × 0.95 = **6 004 utt** (đây là pool đưa đi label)
- đơn-người-nói (×0.54, lạc quan) = 6 320 × 0.54 = **3 413 utt**

| Kịch bản | Tập | Thoại sạch (h) | Utt thô | Utt sau filter (×0.95) | Utt đơn-nói (×0.54) |
|---|---:|---:|---:|---:|---:|
| **1 bộ** | 40 | 40×11.9/60 = **7.9** | 40×158 = **6 320** | **6 004** | **3 413** |
| **3 bộ** | 120 | 120×11.9/60 = **23.8** | 120×158 = **18 960** | **18 012** | **10 238** |
| **6 bộ** | 240 | 240×11.9/60 = **47.6** | 240×158 = **37 920** | **36 024** | **20 477** |

**Caveat đơn-người-nói:** 54% là mức LẠC QUAN (pyannote gộp các giọng nữ giống nhau → đếm thiếu speaker, đếm dư "đơn-nói"). Phần multi-speaker (46%) **không mất trắng**: turn-split (cắt utterance tại ranh giới lượt nói của pyannote) cứu lại được một phần đáng kể → con số "đơn-nói" ở trên là sàn dùng được, không phải trần.

**18 giọng/tập** → 3 bộ ≈ vài trăm speaker phân biệt: đủ đa dạng người nói, nhưng bắt buộc split theo speaker (gold-holdout by construction, `04-…§6`).

---

## 3. Đối chiếu mục tiêu §3 → kết luận trung thực

Mục tiêu §3 hiện tại là **50–100h / 40–80k utt**. Quy ra số tập bằng hằng số thật:

- 50h ÷ 7.93 h/bộ = **6.3 bộ ≈ 252 tập**; 100h ÷ 7.93 = **12.6 bộ ≈ 504 tập**
- 40k utt ÷ 6 320/bộ = **6.3 bộ**; 80k ÷ 6 320 = **12.7 bộ** (khớp cách tính theo giờ)

→ **Mục tiêu "50–100h" = ~250–500 tập = ~6–13 bộ phim.** Với 1 người tự vận hành pipeline, đây **không thực tế** (chỉ riêng thu + chạy đã hàng tháng GPU-quota, xem §4).

### Khuyến nghị (user chọn — plan không quyết)

| Phương án | Quy mô | Con số | So ViSEC (3.18h) |
|---|---|---|---|
| **P1 — sửa target về mức khả thi** (đề xuất mặc định) | **3 bộ / 120 tập** | 23.8h sạch · ~18k utt (sau filter) | 23.8/3.18 = **~7.5×** |
| **P2 — giữ tham vọng §3, chấp nhận nhiều tháng** | 6+ bộ / 240+ tập | 47.6h+ · ~36k+ utt | **~15×** |

**Đề xuất:** lấy **P1 (3 bộ ≈ 24h / ~18–19k utt ≈ 7.5× ViSEC)** làm mục tiêu v2 của design doc, đánh dấu `(đề xuất sau pilot, chờ user chốt)`. Đây vẫn là corpus SER tiếng Việt tự-do lớn nhất công khai, đủ cho method paper; có thể mở lên P2 ở vòng sau. Gold giữ nguyên 2–3k utt (§3) — không phụ thuộc số bộ.

---

## 4. Chi phí Kaggle GPU (P100) — theo kịch bản

**Ước lượng GPU-phút/tập** (chưa đo trên P100 — batch đầu tiên sẽ chốt lại; CPU-time local ở `scripts/vietnamese-ser/README.md` là mốc trên):

| Stage | Ước lượng/tập (~36') | Ghi chú |
|---|---:|---|
| ffmpeg | ~1' | CPU |
| Demucs htdemucs | ~5' | GPU |
| silero VAD | ~1' | nhẹ |
| cut | ~2' | ffmpeg |
| PhoWhisper-base ASR | ~4' | GPU, ~158 utt |
| pyannote 3.1 diarization | ~4' | GPU |
| **Tổng** | **~17' ≈ 0.30 GPU-h/tập** (làm tròn lên cho an toàn) | |

Quota Kaggle: **30 GPU-h P100/tuần**, tối đa 2 session song song (song song rút ngắn wall-clock, **không tăng** trần 30h/tuần).

| Kịch bản | Tập | GPU-h = tập×0.30 | Số tuần = GPU-h/30 |
|---|---:|---:|---:|
| 1 bộ | 40 | 40×0.30 = **12** | 12/30 = **<1 tuần** |
| 3 bộ | 120 | 120×0.30 = **36** | 36/30 = **~2 tuần** |
| 6 bộ | 240 | 240×0.30 = **72** | 72/30 = **~3 tuần** |

---

## 5. Chi phí weak-label 2-teacher (Batch API)

Giá (per 1M token, sau giảm 50% batch): **Opus $2.5 in / $12.5 out** · **Sonnet $1 in / $5 out**.
Token/utt: **~150 in + ~40 out**.

- Opus/utt = 150×2.5/1e6 + 40×12.5/1e6 = 0.000375 + 0.0005 = **$0.000875**
- Sonnet/utt = 150×1/1e6 + 40×5/1e6 = 0.00015 + 0.0002 = **$0.00035**
- **2-teacher/utt = $0.001225**

Áp lên utt sau filter (cột §2):

| Kịch bản | Utt (×0.95) | Chi phí = utt×$0.001225 |
|---|---:|---:|
| 1 bộ | 6 004 | **$7.4** |
| **3 bộ** (đề xuất) | 18 012 | **$22.1** |
| 6 bộ | 36 024 | **$44.1** |

→ Chi phí label **không phải ràng buộc** (cả 3 kịch bản < $50). Ràng buộc thật là GPU-quota (§4) + công thu media + rủi ro pháp lý (§6).

---

## 6. Rủi ro: đưa media bản quyền lên Kaggle

Pipeline batch cần file phim nằm trong 1 Kaggle dataset (`phatneurondai/vnser-episodes`). **Upload phim lên Kaggle private dataset = đưa media bản quyền cho bên thứ ba (dù private).** Hai phương án — **user quyết**:

| PA | Cách | Được | Mất |
|---|---|---|---|
| **A. Kaggle private dataset** | upload media, chạy kernel này trên P100 | dùng được 30h GPU/tuần miễn phí; nhanh | media rời máy → bên thứ ba giữ (dù private); vùng xám bản quyền |
| **B. GPU local (nếu có)** | chạy cùng pipeline trên máy có CUDA | media không rời máy; sạch pháp lý hơn | cần GPU local thật (máy hiện tại torch CPU/torchcodec hỏng → không đủ) |

Nhất quán với `04-…§4`: bản phát hành công khai chỉ gồm **features + timestamp + nhãn**, không phát hành audio thô — nên rủi ro chỉ ở khâu xử lý nội bộ, giảm nhẹ bằng PA B nếu có GPU.

---

## 7. Shortlist phim ứng viên (web research — KHÔNG tải, KHÔNG link tải)

Phim truyền hình VN thể loại tâm lý/gia đình, ưu tiên kênh YouTube **chính thức** (giảm rủi ro nguồn). Caption: **không có kênh nào ship CC do người viết** — chỉ có track auto (ASR) của YouTube, dùng làm seed transcript thô, **không** phải gold alignment (đúng như pilot đã chứng minh: PhoWhisper↔YouTube similarity mean 87.2, hai bên đều ASR).

| Phim | Số tập | Năm | Kênh YouTube chính thức | Caption | Mật độ thoại | Cần user xác nhận |
|---|---:|---:|---|---|---|---|
| **Sống chung với mẹ chồng** | 34 | 2017 | VTV Giải Trí Official (VTV1) | auto only | rất cao — gần thuần thoại mẹ chồng–nàng dâu | caption + chất lượng audio |
| **Về nhà đi con** | 85 | 2019 | VTV Giải Trí Official (VFC/VTV1) | auto only | rất cao — chính kịch gia đình | caption + chất lượng audio |
| **Gạo nếp gạo tẻ** (P1) | 109 | 2018 | Vie Channel Official (HTV2) | auto only | rất cao — melodrama, khối lượng thoại lớn | caption + chất lượng audio |
| Hương vị tình thân (P1+P2) | ~143 | 2021 | VTV Giải Trí Official (VTV1) | auto only | rất cao — mâu thuẫn gia đình liên tục (upload chia nhiều playlist) | caption + chất lượng audio |
| Hoa hồng trên ngực trái | 46 | 2019 | VTV Giải Trí Official (VTV3) | auto only | cao — drama hôn nhân | caption + chất lượng audio |
| Cây táo nở hoa | 70 | 2021 | Vie Channel / VieON (HTV2) | auto only | cao — remake, nhiều cảnh giằng xé | caption + chất lượng audio |
| Thương ngày nắng về (P1+P2) | 87 | 2021–22 | VTV Giải Trí Official (VTV3) | auto only | cao — mẹ–con gái, giàu cảm xúc | caption + chất lượng audio |
| 11 tháng 5 ngày | 46 | 2021 | VTV Giải Trí Official (VTV3) | auto only | trung bình–cao — thanh xuân/tình cảm | caption + chất lượng audio |

**Top-3 (mật độ thoại × kênh chính thức × dễ đối chiếu):**
1. **Sống chung với mẹ chồng** — dày thoại nhất, gọn 34 tập, 1 run VTV Giải Trí sạch → mật độ/giờ tốt nhất.
2. **Về nhà đi con** — mật độ thoại-cảm-xúc cao nhất nhóm "phim lớn", upload VTV chính thức, iconic dễ cross-check timestamp.
3. **Gạo nếp gạo tẻ** — 109 tập trên Vie Channel (HTV2) → lựa chọn nếu cần **quy mô** (một mình ~ đủ P2).

> Cờ đỏ cho user: rủi ro lớn nhất **không** phải tìm phim mà là **ground-truth caption** — kênh chính thức không cho CC người-viết, nên phải ngân sách cho ASR + sửa tay (hoặc mua phụ đề). Đúng lý do gold-set 2–3k utt vẫn cần annotator người (§3).

---

## 8. Việc chờ user quyết

- [ ] **Chốt mức quy mô:** P1 (3 bộ, đề xuất) hay P2 (6+ bộ)? → cập nhật `04-…§3` target.
- [ ] **Chốt nơi chạy GPU:** PA A (Kaggle upload) hay PA B (GPU local) — quyết rủi ro media bản quyền (§6).
- [ ] **Chọn phim** từ shortlist §7 (xác nhận caption + chất lượng audio từng phim).
- [ ] Sau khi chốt: tạo dataset `phatneurondai/vnser-episodes` + push kernel `kaggle/vietnamese-ser/vnser-extract/`.
