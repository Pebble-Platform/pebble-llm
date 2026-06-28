# Báo cáo tuần — Thesis Pebble‑LLM

**Tuần:** 2026‑06‑23 → 2026‑06‑27 · **Nhánh:** main · **Người báo cáo:** Research team
**Đính kèm:** `THESIS-OVERVIEW-vi.html` (toàn cảnh) · `r2-method-improvements.html` (chi tiết 3 cải tiến)

---

## 1. Tóm tắt điều hành (1 phút)

Trọng tâm tuần này: **chuyển thesis từ "ráp nối kỹ thuật" sang 3 đóng góp phương pháp có kiểm chứng** — đáp thẳng feedback của thầy/sếp rằng phần trước "chưa có đóng góp NCKH, cần cải tiến từ phương pháp cũ và phải hiệu quả".

- **Tìm + verify 3 hướng cải tiến** cho mô hình R2 (ordinal suicide‑risk), mỗi hướng là một **đòn bẩy bù nhau** (model · inference · data), đều có **cải tiến đo được** trên dataset nhỏ trong **~7h GPU**.
- **Kết quả nổi bật:** lớp nút thắt **Behavior** (lâm sàng quan trọng nhất) được nâng từ **0.183 → 0.260** (CORN+GCE 5‑fold chính thức) và lên **0.41** (label‑shift); xác nhận **35.8% nhãn Behavior** là nhiễu (ordinal‑CL).
- **Đầu tuần:** đã chốt "vượt paper" (within‑distribution 5‑fold CV **0.653 > 0.510**), hoàn tất 2 vòng nghiên cứu (12 paper finetuning‑methods + 16 paper emotional‑tone), gỡ blocker Kaggle.
- **Đang chạy:** số CORN+GCE **5‑fold×10ep chính thức** (apples‑to‑apples) để chốt bảng paper.

---

## 2. Việc đã hoàn thành tuần này

| # | Hạng mục | Kết quả | Trạng thái |
|---|---|---|---|
| 1 | R2 "vượt paper" (within‑distribution) | 5‑fold CV macro‑F1 **0.653 > paper 0.5098** (+28%) | ✅ |
| 2 | Vòng nghiên cứu finetuning‑methods | 12 paper (42–53), roadmap 3‑tier → report HTML | ✅ |
| 3 | Vòng nghiên cứu emotional‑tone | 16 paper, top‑4 chấm điểm; IMHI tải về | ✅ |
| 4 | Gỡ blocker Kaggle | account phone‑verified `phatneurondai` (GPU+Internet) | ✅ |
| 5 | **Tìm 3 hướng cải tiến phương pháp** | qua long‑task + 4 task‑researcher song song (grounding prior‑art) | ✅ |
| 6 | **Verify cả 3 hướng** | A (local 0 GPU) · B (Kaggle diag) · D (Kaggle 3‑fold) — đều dương | ✅ |
| 7 | Toàn cảnh thesis + DAIC‑WOZ | `THESIS-OVERVIEW-vi.{md,html}` + phần xin dataset/DUA | ✅ |
| 8 | Gộp 3 kết quả vào paper plan + report | `PAPER-PLAN-text-ordinal-suicide.md` §1–4 + `r2-method-improvements.html` | ✅ |
| 9 | CORN+GCE **5‑fold×10ep** (số chính thức) | macro **0.402** ±0.013 · Behavior **0.260** · QWK 0.361 | ✅ |

---

## 3. Đóng góp khoa học — 3 cải tiến phương pháp (lõi tuần này)

Baseline (method cũ): dual‑head `0.5·CORAL+0.3·CE+0.2·Focal`, gold‑holdout. gold macro‑F1 **0.385**, **Behavior‑F1 0.183**. Nghịch lý: flat‑CE thuần (0.422) lại *vượt* tri‑objective.

| Đóng góp | Đòn bẩy | Cải tiến vs cũ | Kết quả đo được | Chi phí |
|---|---|---|---|---|
| **1. CORN + GCE** | model/loss | CORN thay CORAL (bỏ shared‑weight), GCE thay Focal (bỏ noise‑amplify) | macro **0.402** ±0.013 (>dual +0.017, <flat‑CE), **Behavior 0.260** (>dual +0.077), giữ ordinal | Kaggle 5f×10e |
| **2. Label‑shift correction** | inference | hiệu chỉnh hậu kỳ `P_train→P_gold` (KHÔNG train lại) | **Behavior 0.357→0.41** (deploy) / 0.44 (oracle); shift Behavior **3.0×** | local, **0 GPU** |
| **3. Ordinal‑aware Confident Learning** | data | thêm trọng số khoảng‑cách‑hạng `\|ỹ−ŷ\|²` vào cleanlab | **35.8%** nhãn Behavior nghi sai; clean **100%** lỗi‑xa, giữ **78%** lỗi‑kề | Kaggle diag (~4h) |

→ **Khung IEEE:** một bài *"Honest Weak‑Supervision cho Ordinal Clinical NLP"* với 3 đóng góp bù nhau, không trùng. A (label‑shift) + B (ordinal‑cleaning) làm 2 trụ; D = "ordinal head bền‑nhiễu CORN+GCE > CORAL+Focal" + finding trung thực "flat‑CE vẫn tốt nhất trên gold" (cái giá của ordinal dưới shift). Mỗi đóng góp đối chiếu prior‑art (CORN Shi'23, GCE Zhang&Sabuncu'18, Logit‑Adjust Menon'21, SLD Saerens'02, Confident‑Learning Northcutt'21) và nêu rõ phần *novelty cho setting này*.

---

## 4. Trạng thái 2 stream thesis

- **Text/Message (trọng tâm tuần):** core experiments ✅ + 3 đóng góp phương pháp ✅. Còn: số 5‑fold chính thức (đang chạy), κ chất lượng nhãn, baselines, draft IEEE.
- **Voice:** backbone đã chọn (WavLM thắng emotion2vec 3/3 seed), crisis head recall‑floor xong; MTL heads (M3–M5) chờ chạy. Tuần này không có thay đổi lớn.

---

## 5. Blocker & độ trễ ngoài tầm kiểm soát (cần khởi động sớm)

| Hạng mục | Stream | Hành động | Độ trễ |
|---|---|---|---|
| Quyền **DAIC‑WOZ** (EULA) | Voice/Text safety | ký EULA từ email học thuật (`dcapswoz.ict.usc.edu`) | ~1–3 tuần |
| **MSP‑Podcast** (A/V/D) | Voice | xin quyền | gated |
| Tập overlap **κ** nhãn‑LLM↔gold | Text | truy lại overlap, đo Cohen's κ | nội bộ |
| Kaggle quota | cả hai | ~30h P100/tuần, tối đa 2 GPU đồng thời | reset hàng tuần |

---

## 6. Kế hoạch tuần sau

1. ✅ (xong) CORN+GCE 5‑fold = macro 0.402 / Behavior 0.260 — đã chốt vào paper plan + report.
2. **Tách đóng góp:** chạy CORN‑only & GCE‑only (5‑fold) → tách riêng phần CORN vs GCE đóng góp bao nhiêu cho bảng ablation IEEE.
3. **B Arm2:** retrain trên pool đã ordinal‑clean (drop far / downweight) → đo Behavior‑F1 sau làm sạch.
4. Đo **Cohen's κ** nhãn‑LLM↔gold (đáp gap #1).
5. Khởi động **DAIC‑WOZ EULA** + **MSP‑Podcast** (độ trễ ngoài tầm kiểm soát).
6. Bắt đầu draft IEEE: Method (3 đóng góp) + Experiments (bảng ablation + label‑shift).

---

*Nguồn: `docs/tasks/r2-method-improvements-for-contribution.md` · `docs/reports/{THESIS-OVERVIEW-vi, r2-method-improvements, r2-ab-results}.*` · `docs/papers/finetuning-message/PAPER-PLAN-text-ordinal-suicide.md` · `docs/dataset-acquisition-plan.md` · logs `kaggle/finetuning-message/{r2-corn-gce, r2-tier1-cleanlab, r2-label-shift}/out`.*
</content>
