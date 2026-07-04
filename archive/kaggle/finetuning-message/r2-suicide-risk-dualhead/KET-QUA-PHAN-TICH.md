# Phân tích kết quả Kaggle — R2 Hierarchical Dual-Head (luồng A & B)

> Nguồn log: hai kernel Kaggle đã COMPLETE (24/06/2026).
> - **B:** `fabiocarava/r2-suicide-risk-dual-head-mentalroberta`
> - **A:** `fabiocarava/r2-within-dist-cv-10k-balanced`
> Backbone: `welsachy/mental-roberta-base-finetuned-depression` · GPU + Internet ON.

---

## 1. Hai luồng thực sự đã chạy gì (đọc từ log)

| | **Luồng A** `within-dist-cv-10k-balanced` | **Luồng B** `dual-head-mentalroberta` |
|---|---|---|
| `gold_holdout` | **False** | **True** |
| Data nạp | `load_cssrs` → tải Zenodo, **392 seq** CSSRS-500 `[99,171,77,45]` | `load_combined` → pool **9 680** `[3992,3612,634,1442]` + gold **392** |
| Cách đánh giá | 5-fold CV ngay trên 392 mẫu lâm sàng | Train trên pool nhãn-LLM, eval mọi fold trên 392 gold |
| Thời gian | ~19 phút (1 134 s) | **~9.2 giờ** (33 115 s) |
| Early stop | Cả 5 fold dừng sớm @epoch 5–8 | Chạy đủ 10 epoch/fold |

---

## 2. Kết quả thô

**Luồng A — CV trên 392 mẫu lâm sàng:**

```
CV macro-F1: mean=0.1888  std=0.0335  folds=[0.147, 0.172, 0.228, 0.229, 0.169]
per-class: Indicator ~0.35–0.49 | Ideation ≈ 0 | Behavior ≈ 0 | Attempt ~0.15–0.31
best fold macro-F1 = 0.2290
```

**Luồng B — train 10k pool, eval gold:**

```
GOLD macro-F1: mean=0.3849  std=0.0071  folds=[0.393, 0.384, 0.387, 0.388, 0.372]
(val-on-LLM macro-F1: mean=0.6661  folds=[0.674, 0.671, 0.659, 0.675, 0.652])
per-class-F1 gold (TB): Indicator 0.50 | Ideation 0.48 | Behavior 0.18 | Attempt 0.37
best GOLD macro-F1 = 0.3934
```

### Per-class F1 trên gold (luồng B), từng fold

| Fold | Indicator | Ideation | Behavior | Attempt |
|---|---|---|---|---|
| 0 | 0.514 | 0.479 | 0.211 | 0.370 |
| 1 | 0.471 | 0.461 | 0.194 | 0.411 |
| 2 | 0.523 | 0.478 | 0.174 | 0.372 |
| 3 | 0.487 | 0.509 | 0.208 | 0.348 |
| 4 | 0.516 | 0.472 | 0.130 | 0.370 |
| **TB** | **0.502** | **0.480** | **0.183** | **0.374** |

---

## 3. Diễn giải — ba con số, một câu chuyện

| Cấu hình đo | Macro-F1 | Ý nghĩa |
|---|---|---|
| **A: CV trên 392 gold lâm sàng** | **0.19** | Model nặng + dữ liệu quá ít → **sụp đổ**, không học nổi class giữa |
| **B (val): within-dist trên 10k nhãn-LLM** | **0.67** | Đủ dữ liệu thì model học tốt — nhưng đo trên chính nhãn LLM (lạc quan) |
| **B (gold): train 10k → test gold lâm sàng** | **0.385** | Con số **trung thực** để báo cáo |

### Bốn kết luận chính

1. **Dữ liệu là nút thắt, không phải kiến trúc.** Train chỉ trên 392 mẫu gold (A) →
   macro-F1 0.19, hai class Ideation/Behavior gần như bằng 0. Đổ thêm 9 680 mẫu nhãn-LLM
   (B) → gold macro-F1 **0.385, gấp đôi**. Augment bằng nhãn-LLM thực sự cứu model.

2. **Khoảng cách LLM↔gold ≈ 0.28** (0.67 → 0.385): nhãn LLM không khớp hoàn toàn nhãn lâm
   sàng. Nếu chỉ báo cáo 0.67 là tự đánh lừa — đây đúng là lý do thiết kế gold-holdout.

3. **Behavior là điểm yếu cố hữu** (F1 chỉ ~0.18 trên gold). Nguyên nhân lộ rõ ngay ở phân
   bố pool: Behavior chỉ **634/9 680 ≈ 6.5%**. `R2_BALANCE` (WeightedRandomSampler) chưa đủ
   vá — vì sampling lặp lại không tạo thêm đa dạng ngữ nghĩa.

4. **B rất ổn định** (std 0.007 qua 5 fold) → con số 0.385 đáng tin để đưa vào thesis.

---

## 4. ⚠️ Cảnh báo cấu hình Luồng A

Tên kernel là **"within-dist-cv-10k-balanced"** nhưng log cho thấy nó **không hề đụng tới
10k** — vì `gold_holdout=False` nên đi nhánh `load_cssrs`, tải CSSRS-500 từ Zenodo và CV
trên 392 mẫu. Tức A **không phải** "within-distribution CV trên 10k" như tên gọi; nó là
baseline "train trên gold nhỏ".

May là con số "within-dist trên 10k" đã có sẵn = `val-on-LLM mean = 0.667` bên trong B.
Nên về mặt khoa học vẫn đủ 3 điểm so sánh.

→ Nếu A định chạy đúng nghĩa CV-trên-10k riêng: code hiện **không có** nhánh CV trên
combined-pool khi `gold_holdout=False`; nó luôn dùng CSSRS-500.

---

## 5. Đề xuất bước tiếp theo

- **Cải thiện Behavior:** thay sampling-lặp bằng **oversample có augment mạnh** riêng cho
  class Behavior (paraphrase/back-translation), hoặc nâng `focal_gamma` / trọng số class
  Behavior trong loss.
- **Lọc nhãn-LLM:** kiểm tra độ tin cậy nhãn LLM cho Behavior (class hiếm + dễ nhầm với
  Attempt) — có thể nhãn nhiễu nhiều nhất ở đây.
- **Báo cáo thesis:** dùng **gold macro-F1 = 0.385 ± 0.007** làm số chính, kèm bảng 3-mức
  (gold-CV 0.19 / within-LLM 0.67 / cross-to-gold 0.385) để minh hoạ giá trị của augment +
  tính trung thực của gold-holdout.

---

## Phụ lục — số liệu nguồn

- **B data split:** `test(gold)=392 [99,171,77,45]` | `train-pool=9680 [3992,3612,634,1442]`
  (`Indicator/Ideation/Behavior/Attempt`)
- **B gold folds:** `[0.3934, 0.3841, 0.3868, 0.388, 0.3721]` → mean 0.3849, std 0.0071
- **B val (LLM) folds:** `[0.6735, 0.6705, 0.6592, 0.6749, 0.6523]` → mean 0.6661
- **A CV folds:** `[0.1465, 0.1716, 0.2276, 0.229, 0.1691]` → mean 0.1888, std 0.0335
