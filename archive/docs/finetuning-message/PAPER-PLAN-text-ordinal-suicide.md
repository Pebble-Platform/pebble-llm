# Kế hoạch viết báo — BÀI 1 (Text/Message): Weakly-Supervised Augmentation cho Ordinal Suicide-Risk

> **Đích nộp:** IEEE (BigData / Access / EMBC-class). Format double-column ~6–10 trang.
> **Trạng thái:** thí nghiệm lõi đã chạy (luồng A+B); cần bổ sung label-quality + ablation + ethics.
> **Finetuning-method round (2026-06-25):** 12 bài 42–53 đã phân tích với đòn bẩy cụ thể + thí nghiệm Kaggle cho từng gap dưới đây —
> roadmap 3-tier + ánh xạ gap trong [`../../reports/r2-finetuning-methods.html`](../../reports/r2-finetuning-methods.html) ·
> tracking [`../../tasks/r2-finetuning-methods-for-ieee.md`](../../tasks/r2-finetuning-methods-for-ieee.md).
> (Gap #1 → bài 45/46; Gap #2 → 48/49/51/50; Gap #3 → 53; Behavior → 46/45/47.)
> **Nguồn:** code [`../../../kaggle/finetuning-message/r2-suicide-risk-dualhead/r2-suicide-risk-dualhead.py`](../../../kaggle/finetuning-message/r2-suicide-risk-dualhead/r2-suicide-risk-dualhead.py) ·
> kết quả [`../../../kaggle/finetuning-message/r2-suicide-risk-dualhead/KET-QUA-PHAN-TICH.md`](../../../kaggle/finetuning-message/r2-suicide-risk-dualhead/KET-QUA-PHAN-TICH.md) ·
> method [`R2-DEEP-method-and-repro-vi.md`](./R2-DEEP-method-and-repro-vi.md)

---

## 1. Tiêu đề nháp & đóng góp

**Title:** *Weakly-Supervised Augmentation for Ordinal Suicide-Risk Classification on Social Media: An Honest Gold-Holdout Study*

**Claim chính (KHÔNG phải SOTA — là phương pháp luận):**
> Nhãn-LLM trên dữ liệu mạng xã hội augment được một tập lâm sàng nhỏ cho phân loại **ordinal** nguy cơ tự sát. Dưới giao thức **gold-holdout** (train trên nhãn-LLM, đánh giá trên nhãn lâm sàng held-out), lợi ích đo được là **trung thực, không circular**: macro-F1 **0.19 → 0.385** (+~50% rel), QWK **0.241 → 0.378**.

**Gold-holdout protocol** (đóng khung đánh giá trung thực): tách bạch nhãn-LLM (train) vs nhãn lâm sàng (eval) → chống tự-đánh-lừa (within-LLM 0.67 ≠ gold 0.385). Đây là *khung*, không phải đóng góp lõi.

### ⭐ Ba đóng góp PHƯƠNG PHÁP (mới — đã verify Kaggle/local 2026-06-27)
> Đáp feedback "cần cải tiến từ phương pháp cũ, phải hiệu quả": 3 đòn bẩy bù nhau (inference · data · model), mỗi cái cải tiến đo được vs method cũ. Chi tiết: [`../../tasks/r2-method-improvements-for-contribution.md`](../../tasks/r2-method-improvements-for-contribution.md).

1. **CORN + GCE — loss ordinal bền-nhiễu.** Thay CORAL (shared-weight → 1 nhãn hiếm nhiễu hỏng mọi ngưỡng) bằng **CORN** (weight riêng mỗi ngưỡng) và Focal (khuếch đại mẫu nhiễu) bằng **GCE** (giảm trọng số mẫu tin-cậy-thấp). **Kết quả (5-fold×10ep):** gold macro-F1 **0.402** (> dual-head 0.385 **+0.017**) và **Behavior-F1 0.260 > dual 0.183 (+0.077)**, *giữ ordinal*. **Vẫn < flat-CE** (0.422/0.285) → finding trung thực: *trên gold, bỏ ordinal (flat-CE) vẫn tốt nhất; CORN+GCE là ordinal head tốt nhất, dùng khi cần QWK/ranking*. Đây là câu trả lời "có cơ chế" cho nghịch lý flat-CE>tri-objective (CORAL+Focal là thủ phạm).
2. **Label-shift correction — chẩn đoán + sửa dịch-chuyển nhãn LLM→gold (inference, 0 train lại).** Đo được `π_gold/π_train` Behavior = **3.0×** (under-label). **Logit-Adjustment** hậu kỳ nâng **Behavior-F1 0.357→0.41** (deploy) tới **0.44** (oracle), macro +0.005→+0.029. → đóng khung "LLM-annotation → clinical-gold là *label shift có hệ thống*", `w(y)` = thước đo bias nhãn-LLM theo lớp.
3. **Ordinal-aware Confident Learning — làm sạch nhãn theo cấu trúc thứ bậc (data).** Cleanlab nghi **35.8%** nhãn Behavior là sai (đáp gap #1). Confident-joint **trọng số `|ỹ−ŷ|²`**: làm sạch **100% lỗi-xa** (Behavior→Indicator) nhưng **giữ 78% lỗi-kề** (Behavior↔Ideation borderline) — nominal CL flag bừa 45% lỗi-kề. → cleaning *đúng lâm sàng*, novelty vì cleanlab không có chế độ ordinal.

*(Đóng góp phụ giữ lại: phân tích định lượng gap nhãn-LLM↔lâm sàng ~0.28 như đại lượng nhiễu weak-sup.)*

---

## 2. Đã có (mạnh) — không cần làm lại

| Hạng mục | Số / trạng thái |
|---|---|
| Kiến trúc dual-head + tri-objective | code chạy end-to-end (luồng B) |
| 3 điểm so sánh | gold-CV **0.19** / within-LLM **0.67** / cross-to-gold **0.385** |
| Within-distribution 5-fold CV | **0.653** > paper 0.5098 (+28%) |
| Ổn định | std **0.007** qua 5 fold |
| Per-class gold (dual-head) | Indicator 0.50 · Ideation 0.48 · Behavior 0.18 · Attempt 0.37 |

**Kết quả 3 cải tiến phương pháp (gold-holdout, đã verify 2026-06-27):**

| Method (gold-holdout, **5-fold×10ep**) | gold macro-F1 | Behavior-F1 | QWK |
|---|---|---|---|
| dual-head CORAL+CE+Focal (cũ) | 0.385 | 0.183 | 0.398 |
| **CORN+GCE** (đóng góp 1) | **0.402** ±0.013 | **0.260** | 0.361 |
| flat-CE (bỏ ordinal) | **0.422** | 0.285 | 0.388 |

→ **CORN+GCE > dual-head cũ** (macro +0.017, **Behavior +0.077**) *giữ ordinal*, nhưng **< flat-CE** → finding: trên gold, bỏ ordinal vẫn tốt nhất; CORN+GCE là *ordinal head tốt nhất*. (Preview 3-fold cho 0.418/0.317 — lạc quan quá, đã thay bằng số 5-fold chính thức.)

**Bảng ablation 2×2 [head × 3rd-loss] (5-fold×10ep, tách đóng góp CORN vs GCE):**

| | Focal | GCE |
|---|---|---|
| **CORAL** | dual 0.385 / 0.183 | gce-only 0.399 / 0.229 |
| **CORN** | corn-only 0.410 / 0.250 | corn+gce 0.402 / 0.260 |

→ **CORN (head) là đòn bẩy chính** (+0.025 macro / +0.067 Behavior vs dual); **GCE độc lập** giúp nhỏ hơn (+0.014 / +0.046); kết hợp **sub-additive** trên macro nhưng **Behavior cao nhất ở CORN+GCE (0.260)**. Khác biệt giữa 3 biến thể trong khoảng nhiễu (std 0.015–0.025).

| Đóng góp khác | Kết quả | Chi phí |
|---|---|---|
| **label-shift logit-adjust** (đóng góp 2) | Behavior **0.357→0.41** (oracle 0.44), macro +0.005 | local, 0 GPU |
| **ordinal-CL diagnostic** (đóng góp 3) | 35.8% nhãn Behavior nghi sai; clean 100% far / keep 78% adj | Kaggle diag (~4h) + numpy |

---

## 3. Còn thiếu để IEEE duyệt (ưu tiên giảm dần)

| # | Hạng mục | Vì sao cần | Việc cụ thể |
|---|---|---|---|
| 🟡 1 | **Định lượng chất lượng nhãn-LLM** | "0.28 gap" hiện không được giải thích → reviewer bác | **✅ một phần:** ordinal-CL diagnostic cho biết **35.8% nhãn Behavior** bị nghi sai. Còn lại: tập overlap + **Cohen's κ** + confusion LLM-vs-gold; mô tả pipeline label (đơn-model `gpt-5.4-mini`, conf≥0.6) |
| 🟢 2 | **Bảng ablation** | IEEE đòi tách đóng góp | **✅ XONG (5f×10e):** bảng 2×2 [CORAL/CORN × Focal/GCE] đầy đủ (dual 0.385 · gce-only 0.399 · corn-only 0.410 · corn+gce 0.402) + flat-CE 0.422 → CORN chủ đạo. Còn (tùy chọn): ±LLM-augment; q-sweep |
| 🟡 3 | **Baselines** | Cần cột so sánh | plain-RoBERTa-CE; BiLSTM-MTL (paper gốc có) trên cùng split |
| 🟢 4 | **Behavior collapse** (F1 0.18, 6.5% pool) | Điểm yếu lâm sàng (bỏ sót "lên kế hoạch") | **✅ 3 đòn bẩy đã verify:** CORN+GCE (0.183→0.260), label-shift logit-adjust (→0.41), ordinal-CL cleaning. Còn: B-Arm2 retrain trên pool đã làm sạch |
| 🟡 5 | **Ethics & provenance** | IEEE clinical bắt buộc | Mục data-collection: scrape r/SuicideWatch qua pullpush, ~9% content-filtered, de-identification |
| 🟢 6 | **Đồng bộ số** | 0.385 (rebalance) vs 0.357 (run cũ §6 spec) đang lệch | Thống nhất dùng số rebalance; cập nhật `R2-DEEP-method-and-repro-vi.md` |
| 🟢 7 | **Significance** | std 5-fold đã đủ; cân nhắc thêm seed | Tùy chỗ trống trang |

---

## 4. Outline IEEE

1. **Introduction** — gap: nguy cơ tự sát là ordinal + nhãn lâm sàng khan hiếm; câu hỏi: nhãn-LLM có cứu được không, và đo thế nào cho trung thực.
2. **Related Work** — C-SSRS screening (notes 14–17), weak/distant supervision + LLM-as-annotator (note 16, 13), CORAL ordinal, MentalBERT/RoBERTa (note 12).
3. **Method** — hierarchical dual-head (post→sequence); **(đóng góp 1) loss ordinal bền-nhiễu CORN+GCE**; **(đóng góp 2) label-shift correction** (Logit-Adjust/SLD-EM); **(đóng góp 3) ordinal-aware Confident Learning**; gold-holdout protocol (khung).
4. **Data & LLM-labeling pipeline** — CSSRS-500 gold + av9ash + scrape; pipeline label; **label-quality analysis** (κ vs gold + ordinal-CL: 35.8% Behavior nghi sai).
5. **Experiments** — baselines + **ablation loss** (dual / flat-CE / CORN+GCE) + **label-shift** (±correction, oracle) + bảng 3-mức + per-class + within-dist 0.653.
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
