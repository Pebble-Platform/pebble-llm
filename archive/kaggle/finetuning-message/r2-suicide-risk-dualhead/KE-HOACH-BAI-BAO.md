# Kế hoạch nghiên cứu — Bài báo R2 (Reproduction + Augmentation study)

> **Hướng đã chốt:** *Reproduction + augmentation study.*
> Tái hiện mô hình Hierarchical Dual-Head (Yang et al., IEEE BigData 2025) trên benchmark
> công khai CSSRS-500, nghiên cứu LLM-augmentation cho low-resource, và dùng **gold-holdout**
> để bóc tách khoảng cách nhãn-LLM ↔ lâm sàng.
>
> Tài liệu nền: `KET-QUA-PHAN-TICH.md` (kết quả luồng A/B), `GIAI-THICH-CODE.md` (giải thích code).

---

## 0. Vì sao số liệu hiện tại CHƯA đủ thành bài báo

Ba lỗ hổng chặn xuất bản:

1. **Không có baseline & ablation.** Báo cáo 0.385 nhưng không trả lời được *"so với cái gì?"*.
   Chưa chứng minh kiến trúc phức tạp hơn một `TF-IDF + SVM`, chưa tách đóng góp từng thành phần.
2. **So sánh A↔B sai phương pháp luận.** B test trên **toàn bộ 392 gold**, A làm CV trong 392
   (test ~78/fold) → **hai tập test khác nhau**, không so trực tiếp. Kết luận "data là nút thắt"
   chưa đứng vững — 0.19 của A có thể chỉ là *overfit model nặng trên data ít*.
3. **Nhãn LLM không ghi nhận & chưa đo chất lượng.** Pool 9 680 (av9ash+scraped) gán nhãn bằng
   LLM nào, prompt gì, agreement với gold ra sao? Khoảng cách 0.67→0.385 chính là triệu chứng
   nhiễu nhãn LLM nhưng chưa được định lượng.

Cộng thêm: 1 seed duy nhất, không CI, không kiểm định, không confusion matrix, số tuyệt đối thấp.

---

## 1. Ba claim của bài & bằng chứng cần cho mỗi claim

| Claim | Bằng chứng cần |
|---|---|
| **C1.** Tái hiện được dual-head trên benchmark công khai (CSSRS-500) | Table 1 hàng dual-head + đường học hội tụ |
| **C2.** LLM-augmentation giúp low-resource | Table 1: 3 chế độ train, **cùng 1 gold-test cố định** |
| **C3.** Gold-holdout lộ khoảng cách LLM↔lâm sàng (~0.28) → cảnh báo chỉ đo in-distribution là ảo | Cột LLM-only vs val-on-LLM + kiểm định |

---

## 2. Tầng 0 — Sửa phép so sánh (BẮT BUỘC, làm trước)

Lỗi gốc hiện tại: B test trên **toàn bộ 392**, A CV trong 392 → không so được.
Sửa bằng **một gold-test đóng băng**, dùng chung cho MỌI thí nghiệm:

```
392 gold → [ gold-train 274 | gold-test 118 ]   (stratified, FROZEN)
pool LLM 9 680 = P
```

### Table 1 — xương sống (đo trên gold-test 118 cố định, 3 seed)

| Model \ Chế độ train | gold-train (274) | LLM-only (P) | LLM + gold-train |
|---|---|---|---|
| TF-IDF + SVM | · | · | · |
| flat MentalRoBERTa (mean-pool, 1 head) | · | · | · |
| **dual-head hierarchical** | · | · | · |

Một bảng này gánh cả **C1 + C2 + C3**. Cột giữa (LLM-only) so với `val-on-LLM` cho ra
con số khoảng cách của C3.

---

## 3. Tầng 1 — Ablation (nhẹ, 1 seed, chế độ LLM+gold)

Bỏ từng thành phần để chứng minh nó đáng có:

- dual-head → **chỉ-CE** / **chỉ-CORAL**
- ± sequence transformer
- ± attention pooling (so với mean-pool)
- ± augmentation
- ± balance (WeightedRandomSampler)
- ± feature-fusion

> **Nêu thẳng:** temporal embedding gần như chết vì Δt=0 (không có timestamp) — biến nhược
> điểm thành sự trung thực thay vì giả vờ là đóng góp.

---

## 4. Tầng 2 — Độ chặt thống kê

- **3–5 seed** cho hàng dual-head; báo cáo mean ± khoảng tin cậy.
- Kiểm định ghép cặp **McNemar / bootstrap** trên gold-test (so các chế độ train).
- **Confusion matrix** + per-class F1.
- **Error analysis** riêng cho Behavior↔Attempt (hai class hay nhầm + Behavior hiếm 6.5%).

---

## 5. Tầng 3 — Nhãn LLM & định vị (điểm reviewer sẽ đâm)

- Ghi rõ **pipeline gán nhãn LLM**: model nào, prompt, hậu xử lý.
- **Đo agreement nhãn-LLM vs gold** trên phần user giao nhau (nếu có); hoặc gán lại một mẫu
  pool bằng LLM thứ 2 để ước lượng độ nhiễu.
- **Bảng literature CSSRS-500** để định vị con số của ta so với prior work.

---

## 6. Ngân sách GPU — ràng buộc thật

Heavy cell (dual-head trên P = 9 680) ≈ **9 giờ/seed**. Chạy thô:
3 seed × 2 chế độ (P, P+gold) ≈ **54 GPU-giờ** chỉ riêng dual-head, chưa kể ablation
→ vượt quota Kaggle (~30 giờ/tuần). Cách cắt:

| Biện pháp | Tiết kiệm |
|---|---|
| `R2_EPOCHS=6` (log cho thấy bão hòa epoch 5–6) | ~40% thời gian |
| Baseline (SVM, flat) rất rẻ → 3 seed thoải mái; chỉ dual-head mới đắt | — |
| Ablation prune bằng `val-on-LLM` (rẻ), chỉ config cuối eval gold | nhiều |
| 3 seed **chỉ** cho hàng headline; ablation 1 seed | ~½ |

→ Gói lại còn **~25–30 GPU-giờ**, vừa 1 tuần quota.

---

## 7. Thay đổi CODE cần thiết (điều kiện cần để chạy Table 1)

Refactor `r2-suicide-risk-dualhead.py`:

- **(a)** gold-test **đóng băng** (tách 118 stratified, không bao giờ train trên nó)
- **(b)** công tắc **3 chế độ train**: `gold-only` / `LLM-only` / `LLM+gold`
- **(c)** thêm **flat MentalRoBERTa** + **TF-IDF+SVM** baseline
- **(d)** vòng **multi-seed**
- **(e)** lưu **confusion-matrix + per-class JSON** cho bài báo

---

## 8. Lộ trình thực thi (đề xuất thứ tự)

1. **Chốt thiết kế** (doc này) → tránh chạy lại GPU sai như luồng A.
2. **Refactor kernel** cho Table 1 (mục 7).
3. **Chạy Table 1** (baseline trước — rẻ, để smoke pipeline; rồi dual-head).
4. **Ablation** (Tầng 1) prune bằng val-on-LLM.
5. **Thống kê + error analysis** (Tầng 2).
6. **Nhãn LLM + literature** (Tầng 3).
7. **Viết bản thảo** — số chính: gold macro-F1; bảng 3 mức minh hoạ giá trị augment + tính
   trung thực của gold-holdout.

---

## Phụ lục — số liệu hiện có (từ luồng A/B đã chạy)

- **B (gold-holdout):** GOLD macro-F1 = **0.3849 ± 0.0071**; val-on-LLM = 0.6661 → **gap ≈ 0.28**.
- **A (CV trên 392 gold):** macro-F1 = **0.1888 ± 0.0335** (model nặng overfit data ít — *cần
  baseline đơn giản để xác nhận diễn giải*).
- **Phân bố pool:** `[3992, 3612, 634, 1442]` → **Behavior chỉ 6.5%** = nút thắt per-class.
- Số chính dự kiến cho bài: **gold macro-F1 ≈ 0.385**, kèm bảng 3 mức (0.19 / 0.67 / 0.385).
