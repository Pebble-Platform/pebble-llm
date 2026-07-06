# Expected results — pre-registration (004 vnser-train)

> Ghi **trước khi chạy** trên Kaggle GPU (822 clip). Mục đích: có mốc để đối
> chiếu sau run, tránh hợp lý hoá hậu kỳ. Đây là **dự đoán**, không phải số đo.
> Ngày ghi: 2026-07-05.

## Thí nghiệm này CHỨNG MINH / THỬ NGHIỆM điều gì

**Đây là cột mốc kỹ thuật + baseline, KHÔNG phải kết quả khoa học công bố được.**

1. **Thử nghiệm (kiểm chứng chính):** từ corpus đã trích (manifest + clips) có
   dựng được model SER trên Kaggle với splits trung thực + provenance, chạy trong
   quota không? → de-risk hạ tầng train trước khi cam kết scale. Exit-0 = PASS.
2. **Thăm dò (gợi ý, KHÔNG kết luận):** audio-một-mình có mang tín hiệu cảm xúc
   trong phim VN này không; khoảng cách arousal vs valence (nếu valence ≪ arousal
   → *mũi tên chỉ hướng* cho nhánh text tone×emotion, chưa phải bằng chứng);
   xác nhận nghẽn thật = nhãn + quy mô + mất cân bằng, không phải backbone.
3. **KHÔNG chứng minh:** accuracy công bố; giả thuyết tone×emotion (chưa có nhánh
   text để so); tổng quát hoá sang giọng mới (1 series, cast lặp → rò rỉ danh
   tính); "corpus tốt".

Vai trò trong bức tranh lớn = **bậc thang #1**: (a) baseline-to-beat để tầng
bimodal speech+text đo *delta*; (b) chứng minh cơ chế chạy trước khi scale
(≥2 series + gold). Claim khoa học thật nằm ở các bước sau, không ở run này.

## Dự đoán số (out-of-fold, 5-fold GroupKFold(ep,speaker), n=822)

| Head | Metric | Dự đoán (khoảng) | Lý do |
|---|---|---|---|
| emotion 5-class | macro-F1 | **0.30–0.45** | baseline "luôn neutral" ≈0.13; anger kéo điểm, sadness/fear/joy yếu |
| affect | CCC arousal | **0.30–0.50** | năng lượng/pitch — audio bắt tốt |
| affect | CCC valence | **0.15–0.35** | valence từ audio vốn yếu — điểm mấu chốt cho luận điểm bimodal |
| distress | AUC | **0.55–0.75, CI rất rộng** | chỉ 21 dương → gần vô định, mechanics-only |

Kỳ vọng per-class: **anger > joy > fear/sadness**. CI **rộng** (n≈580, sadness ~37).

## Hướng lệch đã biết (đọc số với cảnh giác này)

Số trên **nhiều khả năng LẠC QUAN**: GroupKFold theo `(ep,speaker)` nhưng cùng
diễn viên tái xuất xuyên tập dưới nhãn khác → danh tính rò rỉ train↔val.
**Speaker-disjoint thật sẽ thấp hơn.** Dù đẹp cỡ nào vẫn KHÔNG phải headline.

## Đối chiếu sau khi chạy — ĐO THẬT (kernel v4, 2026-07-05, COMPLETE)

Nguồn: Kaggle `phatneurondai/vnser-train` v4 · split_hash `6c55bedbc24e274f56415eb2459d0b21`
(TRÙNG hash của `make_splits.py` local → GroupKFold inline trong kernel == builder T1).

| Metric | Dự đoán | Đo thật (95% CI) | Trong khoảng? |
|---|---|---|---|
| emotion macro-F1 | 0.30–0.45 | **0.425** [0.381, 0.465] | ✅ cận trên |
| CCC arousal | 0.30–0.50 | **0.146** [0.120, 0.171] | ❌ thấp hơn NHIỀU |
| CCC valence | 0.15–0.35 | **0.086** [0.068, 0.103] | ❌ thấp hơn |
| valence < arousal? | có | **có** (0.086 < 0.146) | ✅ hướng đúng |
| distress AUC | 0.55–0.75 | 0.642 (n_pos=21) | ✅ nhưng vô định |
| GPU-h / run | ~0.3–0.5h | **~0.08h** (~5' wall) | thấp hơn (822 clip nhanh) |

**Diễn giải:**
- **Emotion 0.425 ≫ baseline "luôn neutral" (~0.13)** → feature WavLM MANG tín hiệu
  cảm xúc-phân-loại; pipeline lành mạnh. Ở cận trên khoảng, DƯỚI ngưỡng cảnh báo
  leak 0.45 → chưa báo động rò rỉ nặng, nhưng vẫn thiên lạc quan (cast lặp) → silver.
- **CẢ HAI affect CCC đều thấp (~0.09–0.15), lệch dự đoán** — không chỉ valence yếu
  như kỳ vọng, arousal cũng gần sàn. Vì emotion probe (cùng feature) hoạt động,
  đây KHÔNG phải lỗi feature/pipeline mà về **target V/A** (teacher-mean 1–5 phương
  sai hẹp, mass dồn quanh trung tâm) hoặc linear+CCC underfit. → Trước khi tin affect
  head: kiểm phương sai target + thử chuẩn hoá target / tăng epoch. KHÔNG block (mechanics).
- **valence < arousal đúng hướng** nhưng cả hai gần sàn → ủng hộ YẾU cho luận điểm
  cần nhánh text; kết luận thật vẫn phải chờ thí nghiệm bimodal (có nhánh text để so).
- **Không kích hoạt rule "mọi metric ≈ chance"** (emotion vượt chance rõ) → không cần
  soi feature/pooling.

---

## Run 2 — dataset mở rộng 2 series (kernel v5, 2026-07-06)

Dataset lớn lên: **3611 utt · 3338 clean · 2 series khác cast** (ve-nha-di-con +
chay-tron-thanh-xuan). Lần đầu làm được **eval chéo-cast = speaker-disjoint danh
tính THẬT** — thứ Run 1 (1 series) bị chặn. Kernel giờ chạy 2 eval; 5-class giữ
nguyên để so với Run 1. split_hash(gkf) `f0d4c877b051a27ad946e31cbe9f0aea`.

| Metric | Eval A: GroupKFold (within-pool, lạc quan) | Eval B: Leave-one-series-out (cross-cast, THẬT) |
|---|---|---|
| emotion macro-F1 | **0.413** [0.391, 0.435] | **0.333** [0.313, 0.354] |
| CCC valence | 0.111 [0.103, 0.120] | 0.075 [0.066, 0.083] |
| CCC arousal | 0.152 [0.140, 0.164] | 0.131 [0.119, 0.144] |
| distress AUC | 0.736 (n_pos=127) | 0.717 (n_pos=127) |

**Diễn giải:**
- **Đo được leak: A→B = 0.413 → 0.333** (giảm ~0.08, ~19% tương đối). Đây là lượng
  hoá trực tiếp mức "rò rỉ danh tính within-series thổi phồng số lạc quan" — điều
  Run 1 chỉ cảnh báo định tính, giờ có con số.
- **Con số TRUNG THỰC đầu tiên của dự án: macro-F1 0.333 cross-cast**, vẫn ≫ baseline
  "luôn neutral" (~0.13) → model tổng quát hoá qua dàn diễn viên khác, yếu nhưng thật.
- **CI hẹp lại rõ** (n=2381 vs ~580 ở Run 1) → 4× dữ liệu mua được độ chính xác.
- **Affect vẫn gần sàn ở CẢ HAI eval** (valence 0.075–0.111, arousal 0.131–0.152)
  dù 4× dữ liệu → củng cố kết luận Run 1: đây là vấn đề **target V/A** (teacher-mean
  phương sai hẹp) / audio-một-mình yếu về valence, KHÔNG phải thiếu dữ liệu →
  **động cơ mạnh cho nhánh text (tone×emotion)**. valence < arousal giữ ở cả 2 eval.
- **distress giờ có 127 dương** (Run 1: 21) → AUC ~0.72 bắt đầu có tín hiệu thật,
  nhưng vẫn giữ nhãn mechanics (chưa gold lâm sàng).
- So Run 1: emotion GroupKFold 0.425→0.413 (ổn định); giá trị mới là **0.333
  cross-cast** — con số đáng tin để tầng bimodal đo delta.
