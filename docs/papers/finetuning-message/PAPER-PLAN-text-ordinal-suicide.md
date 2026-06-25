# Kế hoạch viết báo — BÀI 1 (Text/Message): Weakly-Supervised Augmentation cho Ordinal Suicide-Risk

> **Đích nộp:** IEEE (BigData / Access / EMBC-class). Format double-column ~6–10 trang.
> **Trạng thái:** thí nghiệm lõi đã chạy (luồng A+B); cần bổ sung label-quality + ablation + ethics.
> **Nguồn:** code [`../../../kaggle/finetuning-message/r2-suicide-risk-dualhead/r2-suicide-risk-dualhead.py`](../../../kaggle/finetuning-message/r2-suicide-risk-dualhead/r2-suicide-risk-dualhead.py) ·
> kết quả [`../../../kaggle/finetuning-message/r2-suicide-risk-dualhead/KET-QUA-PHAN-TICH.md`](../../../kaggle/finetuning-message/r2-suicide-risk-dualhead/KET-QUA-PHAN-TICH.md) ·
> method [`R2-DEEP-method-and-repro-vi.md`](./R2-DEEP-method-and-repro-vi.md)

---

## 1. Tiêu đề nháp & đóng góp

**Title:** *Weakly-Supervised Augmentation for Ordinal Suicide-Risk Classification on Social Media: An Honest Gold-Holdout Study*

**Claim chính (KHÔNG phải SOTA — là phương pháp luận):**
> Nhãn-LLM trên dữ liệu mạng xã hội augment được một tập lâm sàng nhỏ cho phân loại **ordinal** nguy cơ tự sát. Dưới giao thức **gold-holdout** (train trên nhãn-LLM, đánh giá trên nhãn lâm sàng held-out), lợi ích đo được là **trung thực, không circular**: macro-F1 **0.19 → 0.385** (+~50% rel), QWK **0.241 → 0.378**.

**Ba đóng góp đóng gói được:**
1. **Gold-holdout protocol** tách bạch nhãn-LLM (train) vs nhãn lâm sàng (eval) → chống tự-đánh-lừa (within-LLM 0.67 ≠ gold 0.385).
2. **Dual-head + tri-objective** (CORAL ordinal + CE + Focal) áp cho C-SSRS 4-mức — sửa "adjacent error" của các bài C-SSRS phẳng.
3. **Phân tích định lượng khoảng cách nhãn-LLM ↔ lâm sàng** (~0.28) như một đại lượng đo độ nhiễu weak-supervision.

---

## 2. Đã có (mạnh) — không cần làm lại

| Hạng mục | Số / trạng thái |
|---|---|
| Kiến trúc dual-head + tri-objective | code chạy end-to-end (luồng B) |
| 3 điểm so sánh | gold-CV **0.19** / within-LLM **0.67** / cross-to-gold **0.385** |
| Ổn định | std **0.007** qua 5 fold |
| Per-class gold | Indicator 0.50 · Ideation 0.48 · Behavior 0.18 · Attempt 0.37 |

---

## 3. Còn thiếu để IEEE duyệt (ưu tiên giảm dần)

| # | Hạng mục | Vì sao cần | Việc cụ thể |
|---|---|---|---|
| 🔴 1 | **Định lượng chất lượng nhãn-LLM** | "0.28 gap" hiện không được giải thích → reviewer bác | Lấy tập overlap có cả nhãn-LLM và nhãn gold; đo **Cohen's κ** + confusion LLM-vs-gold; mô tả pipeline label (đơn-model `gpt-5.4-mini`, conf≥0.6) đối chiếu ensemble GPT-4 của paper gốc |
| 🔴 2 | **Bảng ablation** | IEEE đòi tách đóng góp | Chạy thêm cấu hình qua env (code đã hỗ trợ): (a) flat-CE vs CORAL-only vs dual-head; (b) ±LLM-augment; (c) ±`R2_BALANCE`; (d) ±focal |
| 🟡 3 | **Baselines** | Cần cột so sánh | plain-RoBERTa-CE; BiLSTM-MTL (paper gốc có) trên cùng split |
| 🟡 4 | **Behavior collapse** (F1 0.18, 6.5% pool) | Điểm yếu lâm sàng (bỏ sót "lên kế hoạch") | Mục phân tích + ≥1 biện pháp thử: augment mạnh riêng class / nâng `focal_gamma` / lọc nhãn-LLM Behavior |
| 🟡 5 | **Ethics & provenance** | IEEE clinical bắt buộc | Mục data-collection: scrape r/SuicideWatch qua pullpush, ~9% content-filtered, de-identification |
| 🟢 6 | **Đồng bộ số** | 0.385 (rebalance) vs 0.357 (run cũ §6 spec) đang lệch | Thống nhất dùng số rebalance; cập nhật `R2-DEEP-method-and-repro-vi.md` |
| 🟢 7 | **Significance** | std 5-fold đã đủ; cân nhắc thêm seed | Tùy chỗ trống trang |

---

## 4. Outline IEEE

1. **Introduction** — gap: nguy cơ tự sát là ordinal + nhãn lâm sàng khan hiếm; câu hỏi: nhãn-LLM có cứu được không, và đo thế nào cho trung thực.
2. **Related Work** — C-SSRS screening (notes 14–17), weak/distant supervision + LLM-as-annotator (note 16, 13), CORAL ordinal, MentalBERT/RoBERTa (note 12).
3. **Method** — hierarchical dual-head (post→sequence), tri-objective loss, **gold-holdout protocol** (đóng góp).
4. **Data & LLM-labeling pipeline** — CSSRS-500 gold + av9ash + scrape; pipeline label; **label-quality analysis (κ vs gold)**.
5. **Experiments** — baselines + ablations + bảng 3-mức (gold-CV/within-LLM/cross-to-gold) + per-class.
6. **Limitations & Ethics** — nhãn đơn-model, Behavior hiếm, gold lệch protocol gốc (label theo user, Δt=0), ethics scrape.
7. **Conclusion.**

---

## 5. Reviewer-risk & phản biện

- *"Nhãn-LLM là nhiễu thuần"* → trả lời bằng κ + cho thấy gold-holdout vẫn tăng +50%.
- *"Dataset không phải HKIE gốc"* → đóng khung là method+weak-supervision study, không claim cùng benchmark.
- *"Behavior fail"* → nêu thẳng + biện pháp thử + để mở.
- *"Chỉ 392 mẫu test"* → std nhỏ + báo cáo CI; nêu là gold lâm sàng hiếm.

---

## 6. Timeline / checklist

- [ ] (1d) Đồng bộ số 0.385, dựng repo kết quả sạch.
- [ ] (2–3d) Tính κ LLM-vs-gold + confusion (cần truy lại tập overlap; xem [`docs/tasks/enrich-suicide-risk-dataset.md`](../../tasks/enrich-suicide-risk-dataset.md)).
- [ ] (3–4d) Chạy ablation 4 cấu hình + 2 baseline trên Kaggle.
- [ ] (2d) Thử 1 biện pháp vá Behavior.
- [ ] (3d) Viết draft IEEE + bảng + mục ethics.
- [ ] (2d) Vòng review nội bộ.
