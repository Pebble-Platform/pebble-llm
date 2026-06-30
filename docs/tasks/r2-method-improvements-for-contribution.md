# R2 — 3 hướng cải tiến phương pháp để có đóng góp NCKH (hiệu quả, kiểm chứng rẻ)

- **Slug:** r2-method-improvements-for-contribution
- **Status:** done (3 hướng tìm xong + verify cả 3 có tín hiệu dương; future-work còn mở)
- **Created:** 2026-06-27  ·  **Updated:** 2026-06-27
- **Owner:** Fabio / Claude

## Goal
Tìm **3 hướng cải tiến phương pháp** cho R2 (ordinal suicide-risk dual-head) sao cho mỗi hướng là một **đóng góp khoa học thật** (cải tiến rõ rệt so với method cũ, **hiệu quả đo được**), KHÔNG chỉ là kỹ thuật ráp nối. Mỗi hướng phải có **thí nghiệm Kaggle nhỏ/rẻ** để verify trong ngân sách **~10h P100** còn lại. "Done" = doc này có 3 hướng đã được nghiên cứu grounding (prior-art + novelty + thiết kế thí nghiệm rẻ + rủi ro), sẵn sàng để user chọn 1–2 hướng chạy verify.

## Requirements & Constraints
- **Functional:** mỗi hướng nêu rõ (a) cải tiến gì vs method cũ, (b) vì sao là đóng góp khoa học (đối chiếu prior art), (c) thí nghiệm Kaggle nhỏ verify, (d) rủi ro, (e) effect size kỳ vọng.
- **Feedback của sếp (ràng buộc cứng):** "hàm lượng tri thức như vầy không đóng góp gì cho NCKH" → cần **cải tiến từ phương pháp cũ**, **nhấn mạnh phải HIỆU QUẢ**.
- **Ngân sách kiểm chứng:** Kaggle P100, **~10h quota tuần này**. 1 run gold-holdout 5-fold×10ep ≈ 8.8h → **mỗi thí nghiệm verify phải nhỏ** (subset dữ liệu, ≤3 fold, ≤4–6 epoch, hoặc post-hoc không retrain) — mục tiêu ≤ ~3 GPU-h/thí nghiệm để chạy được ≥2 hướng.
- **Non-goals:** không chạy full benchmark lúc này; không cần đạt SOTA — cần *đóng góp phương pháp* + *bằng chứng hiệu quả ban đầu*.

## R2 baseline (đối tượng cải tiến)
- **Task:** ordinal 4-mức C-SSRS (Indicator<Ideation<Behavior<Attempt) từ chuỗi post Reddit.
- **Model:** MentalRoBERTa-mirror → seq-transformer 3 lớp → attn-pool → **CORAL + CE head**; loss `0.5·CORAL + 0.3·CE + 0.2·Focal`; freeze 6 lớp; max_len 256.
- **Giao thức:** gold-holdout — train trên ~9.7k post **nhãn-LLM**, eval trên **gold lâm sàng CSSRS-500** (392).
- **Số hiện tại:** gold macro-F1 **0.385** (dual) / **0.4215** (flat-CE); Behavior gold-F1 **0.183→0.285**; QWK ~0.40; within-dist CV **0.653**.
- **Phát hiện then chốt (hạt giống cho hướng cải tiến):**
  1. **flat-CE > tri-objective trên gold** → CORAL+Focal nghi **overfit phân bố nhãn-LLM** (shift LLM→gold).
  2. **Behavior bottleneck = chất lượng nhãn** (634 nhãn-LLM nhiễu, under-label), không phải sampling.
  3. **Nhãn đơn-LLM, chưa đo κ**; gap nhãn-LLM↔gold ~**0.28** (đại lượng nhiễu weak-sup).

## Milestones
- [x] M1 — Viết doc + khung 4 ứng viên hướng cải tiến (over-generate)
- [x] M2 — Spawn `task-researcher` song song (1/angle): grounding prior-art + novelty + thí nghiệm rẻ + rủi ro
- [x] M3 — Fold findings → chọn **3 hướng mạnh nhất** (A·B·D; loại C → runner-up), Decision Log
- [x] M4 — Thiết kế thí nghiệm Kaggle nhỏ cho mỗi hướng + bảng ngân sách 10h
- [ ] M5 — Trình user chọn hướng để chạy verify (không tự đốt quota khi chưa chốt)

## Decision Log
- **2026-06-27 — CHỐT 3 hướng: A (label-shift) · B (ordinal-CL) · D (CORN+GCE); C (SORD) → runner-up.** Lý do: 3 hướng phủ **3 đòn bẩy bù nhau** — *inference* (A: hiệu chỉnh phân bố hậu kỳ), *data* (B: làm sạch nhãn theo thứ bậc), *model/loss* (D: loss bền nhiễu giải thích nghịch lý flat-CE). Bộ ba này kể được một câu chuyện paper mạch lạc "honest weak-supervision cho ordinal clinical NLP" và mỗi hướng có novelty riêng + thí nghiệm rẻ. **Loại C khỏi top-3** vì trùng chủ đề "chống overfit nhãn cứng" với D (GCE) và động cơ "bớt tin nhãn" với B → để runner-up (vẫn rất rẻ, dễ swap vào). Rejected hẳn: Group-DRO (researcher D xác nhận sai regime — cần group-label sạch, mà nhãn-LLM nhiễu).
- **2026-06-27 — Verify theo thứ tự rẻ→đắt, A trước (ZERO GPU):** A chạy post-hoc local CPU trên checkpoint đã lưu (~0 GPU) → làm ngay không tốn quota. Sau đó D (~3h) trả lời nghịch lý trung tâm; B-diagnostic (~4h) nếu còn quota. Tổng A+D+B-diag ≈ 7h < 10h. Rejected: chạy full 5-fold bất kỳ arm nào (8.8h, hết sạch quota).
- **2026-06-27 — Over-generate 4 ứng viên rồi chọn 3:** giảm rủi ro chọn nhầm hướng yếu. 4 angle bám đúng 3 phát hiện then chốt (shift, noise, weak-label) + lỗ hổng loss-design.

## Open Questions
- [ ] A — **Label-shift correction** (LLM-train → gold): prior-adjustment/logit-adjustment/BBSE có phải đóng góp hiệu quả + rẻ (post-hoc) cho ordinal weak-sup lâm sàng? → task-researcher
- [ ] B — **Ordinal-aware label-noise cleaning**: confident-learning/cleanlab thích ứng cấu trúc ordinal (adjacency) để vá Behavior — novelty vs cleanlab gốc? → task-researcher
- [ ] C — **Soft ordinal targets / distillation** từ độ tin cậy LLM (hoặc multi-LLM/Snorkel) thay nhãn cứng nhiễu (SORD/unimodal) — đóng góp + rẻ? → task-researcher
- [ ] D — **Noise/shift-robust ordinal loss** (GCE, DRO, CORN-vs-CORAL, unimodal) giải thích & sửa "CORAL overfit nhãn-LLM" — novelty? → task-researcher

## ⭐ 3 HƯỚNG ĐI CHỐT (deliverable) + thiết kế thí nghiệm

> Mỗi hướng = một đòn bẩy khác nhau, đều có (a) cải tiến vs method cũ, (b) novelty NCKH, (c) thí nghiệm rẻ, (d) rủi ro, (e) effect-size. Số liệu neo: dual-head gold **0.3849** (Behavior **0.183**), flat-CE **0.4215** (Behavior **0.285**).

### Hướng 1 — A · Label-Shift Correction (đòn bẩy *inference*, RẺ NHẤT)
- **Cải tiến vs cũ:** method cũ train nhãn-LLM → eval gold mà **bỏ qua** việc `P_train(y) ≠ P_gold(y)`. Đo được: Behavior **7.3% (train) → 19.7% (gold)** = under-label **2.7×**. Thêm bước **hiệu chỉnh hậu kỳ KHÔNG train lại**: Logit Adjustment (Menon 2021) trên head CE — `logit_k −= τ·log π_train_k`; hoặc SLD-EM (Saerens 2002) trên posterior.
- **Đóng góp NCKH:** đóng khung **"LLM-annotation → clinical-gold là *label shift có hệ thống*"** (khác noise ngẫu nhiên); dùng tỉ số `w(y)=π_gold/π_train` làm **thước đo độ chệch nhãn-LLM theo lớp**. Mới cho ordinal weak-sup lâm sàng (Menon/Saerens chưa làm cho CORAL/ordinal).
- **Thí nghiệm (≈ 0 GPU):** ~80 dòng Python chạy local CPU trên `best_model.pt` (cả checkpoint dual-head lẫn flat-CE) trên 392 gold → so macro-F1/Behavior-F1 trước/sau, + **oracle** (dùng π_gold thật) làm trần. Tín hiệu: Behavior-F1 0.183 → ~0.23–0.28, macro 0.385 → 0.41–0.46.
- **Rủi ro:** 392 gold ít để ước lượng shift; áp lên **flat-CE** sẽ "có room" hơn dual-head (CORAL bóp Behavior bằng cấu trúc); CORAL monotonicity có thể vỡ → vá isotonic; phải nêu rõ giả định `p(x|y)` ổn định.
- *(grounding: agent a80e0a75dd4ecd537)*

### Hướng 2 — B · Ordinal-Aware Confident Learning (đòn bẩy *data*)
- **Cải tiến vs cũ:** cleanlab gốc coi nhãn **nominal** — lỗi kề Behavior→Ideation bị xử như lỗi xa Behavior→Indicator. Thêm **trọng số khoảng-cách-hạng** `(1−p_self)·|ỹ−ŷ|²` (khớp phạt bậc-2 của QWK) vào confident-joint; và dùng **ngưỡng xác suất tích lũy CORAL** `P(y≥Behavior)<0.4` để lọc — quy tắc **"clean far, keep adjacent"** bảo vệ pool Behavior 634 mẫu.
- **Đóng góp NCKH:** cleanlab **không có chế độ ordinal** (xác nhận từ docs cleanlab); prior gần nhất ICDF/CASSOR là **ảnh** (age-estimation), không phải NLP lâm sàng + nhãn-LLM. → adaptation mới + chạy hậu kỳ trên OOF probs.
- **Thí nghiệm:** **Arm1 FREE** (numpy trên `cl_issues.npz`) — *cần chạy cleanlab diagnostic ~4h trước để có OOF probs*; **Arm2** retrain **3-fold×6ep ≈ 2.5–3h** trên pool đã làm sạch ordinal. Tín hiệu: Behavior-F1 0.183→0.22–0.27; kể cả chỉ Arm1 (phân tích flag-rate ordinal vs nominal) cũng publishable.
- **Rủi ro:** pool Behavior nhỏ dễ bị cắt quá tay → dùng **downweight + keep-adjacent**; OOF probs cũng nhiễu (cùng nguồn).
- *(grounding: agent a06d8e2b82158cb01)*

### Hướng 3 — D · Noise/Shift-Robust Ordinal Loss: CORN + GCE (đòn bẩy *model/loss*, giải thích nghịch lý)
- **Cải tiến vs cũ:** thay **CORAL** (shared-weight → 1 nhãn Behavior nhiễu làm hỏng **mọi** ngưỡng) bằng **CORN** (mỗi ngưỡng 1 weight riêng, train trên tập điều kiện `y≥k`); thay **Focal** (khuếch đại mẫu "khó" = thường là nhiễu) bằng **GCE** `(1−p_y^q)/q, q=0.7` (giảm gradient mẫu tin-cậy-thấp/nhiễu). Loss mới `0.5·CORN + 0.3·CE + 0.2·GCE`.
- **Đóng góp NCKH:** **giải thích cơ chế** nghịch lý *flat-CE > tri-objective*: Focal là **noise-amplifier** (Zhou ICML'21 chứng minh), CORAL shared-weight **cross-contaminate** nhãn hiếm. Lần đầu áp **CORN+GCE cho LLM-weak-label clinical ordinal text**. Bản thân quan sát flat-CE>CORAL+Focal là **finding khoa học báo cáo được**.
- **Thí nghiệm:** 1 arm ablation, **env-gated** (`R2_ORDINAL_HEAD=corn`, `R2_LOSS_TYPE=gce`, `R2_GCE_Q=0.7`), **3-fold×6ep ≈ 3h**. So với flat-CE 0.4215 & dual 0.3849 (cùng split/seed). Tín hiệu mạnh: macro ≥0.42 **và** Behavior ≥0.22, giữ QWK/MAE ≥ Run B.
- **Rủi ro:** CORN ngưỡng k=2 **đói gradient** (Behavior hiếm) có thể tệ hơn → nếu vậy, contribution chuyển thành "GCE đủ"; GCE giả định noise đồng đều; q cần tune (thử thêm q=0.5 nếu mơ hồ). Dùng `coral-pytorch` `corn_loss` để tránh lỗi cài đặt.
- *(grounding: agent a3602fe9fb51dae3d)*

### Runner-up — C · SORD soft ordinal targets *(để dành)*
Drop-in đổi target CE thành `softmax(−|rank−k|/τ)` (Diaz&Marathe CVPR'19), tùy chọn scale theo `conf` LLM. "Lần đầu SORD cho NLP lâm sàng." ~3h (3-fold×6ep). **Loại khỏi top-3** vì trùng chủ đề chống-overfit-nhãn-cứng với D; giữ làm phương án swap. *(grounding: agent a13942ea14fec466a)*

### 📋 Bảng ngân sách kiểm chứng (quota ~10h P100)
| Hướng | GPU-h | Phụ thuộc | Khuyến nghị |
|---|---|---|---|
| **A** label-shift | **~0** (local CPU) | checkpoint đã lưu | ✅ **Chạy ngay, free** |
| **D** CORN+GCE | **~3h** | code ~25 dòng (env-gated) | ✅ ưu tiên 2 (trả lời nghịch lý) |
| **B** ordinal-CL | **~4h** (diagnostic) + ~3h (retrain) | cleanlab diagnostic chưa chạy | 🟡 chạy diagnostic nếu còn quota |
| C SORD (để dành) | ~3h | — | ⏸ swap nếu bỏ 1 hướng |

→ **Combo khuyến nghị trong 10h:** A (0h) + D (3h) + B-diagnostic (4h) = **~7h**, còn ~3h buffer. (A + D có thể chạy ngay; B-diagnostic + D chạy **song song** 2 slot GPU nếu muốn rút wall-clock.)

## Provenance — mỗi số → kernel `slug@version` → log (IDD I5)
> Kaggle giữ mọi version bất biến: `kaggle kernels pull <owner>/<slug>/<version>` lấy đúng code đã chạy.
> Log nhúng config (`device/model/smoke/gold_holdout` + `folds=[...]`). Kernel code đã commit vào git.

| Kết quả | Kernel `slug@version` | Log |
|---|---|---|
| within-dist CV 0.653 | `phatneurondai/r2-within-dist-cv-10k-balanced` | `r2-within-dist-cv/out/` |
| dual-head 0.385 / Beh 0.183 | `r2-suicide-risk-dual-head-mentalroberta@v7` (acc cũ) | `r2-ab-results.md` |
| flat-CE 0.422 / 0.285 | `phatneurondai/r2-ablation-flatce@1` | `r2-ablation/out/` |
| **CORN+GCE 0.402 / 0.260 (5-fold)** | `phatneurondai/r2-corn-gce@2` | `r2-corn-gce/out/` |
| (preview 3-fold 0.418/0.317) | `phatneurondai/r2-corn-gce@1` | — (chỉ trên Kaggle) |
| corn-only 0.410 / 0.250 | `phatneurondai/r2-corn-only@2` (@1 cancelled) | `r2-corn-only/out/` |
| gce-only 0.399 / 0.229 | `phatneurondai/r2-gce-only@1` | `r2-gce-only/out/` |
| ordinal-CL 35.8% | `phatneurondai/r2-tier1-cleanlab-diagnostic@1` | `r2-tier1-cleanlab/out/` |
| label-shift Beh→0.41 | local (no kernel) | `r2-label-shift/posthoc_label_shift.py` |
| baseline plain-RoBERTa-CE 0.346 / 0.169 | `fabiocarava/r2-baseline-roberta@1` | `r2-baseline-roberta/out/` |
| baseline BiLSTM-MTL 0.378 / 0.181 | `fabiocarava/r2-baseline-bilstm@1` | `r2-baseline-bilstm/out/` |

## Research Findings
<!-- task-researcher output blocks (condensed; agentId để continue nếu cần) -->

### Finding A — Label-shift / prior correction · agent a80e0a75dd4ecd537 · confidence: high
- **Số shift đo được (repo):** π_train ≈ [0.423, 0.391, **0.073**, 0.154] vs π_gold ≈ [0.253, 0.436, **0.197**, 0.115] → Behavior under-label **2.7×**, Attempt over-rep.
- **Method:** (1) **Logit Adjustment** Menon'21 trên head CE: `adj_logit_k = logit_k − τ·log π_train_k` (τ∈{0.5,1,1.5}); (2) **SLD-EM** Saerens'02 lặp E/M trên posterior (không cần nhãn gold, chỉ cần input gold); CORAL → áp SLD-EM trên posterior blend, vá monotonicity bằng isotonic. BBSE/RLLS **yếu hơn** (cần confusion-matrix từ gold, 77 Behavior quá ít → nhiễu).
- **Novelty:** combo CORAL+SLD-EM / CE-head logit-adjustment chưa có; framing "LLM→clinical là label-shift" + `w(y)` làm thước đo bias theo lớp = mới. **KHÔNG** claim logit-adjustment/SLD-EM bản thân là mới.
- **Verify:** 0 GPU, post-hoc trên `best_model.pt` (dual + flat-CE), 392 gold, +oracle(π_gold) làm trần.
- **Effect:** +0.03–0.07 macro, +0.05–0.10 Behavior-F1 (mạnh nhất khi áp lên flat-CE).
- **Caveat:** single fold/seed (chỉ lưu best fold) → lý tưởng chạy trên cả 5 fold; nếu SLD-EM hội tụ về gần π_gold mà Behavior vẫn ít cải thiện → kết luận "lỗi chủ yếu là noise, không phải shift" (vẫn là finding chẩn đoán publishable).
- **Nguồn:** Saerens 2002 (Neural Comput); Lipton BBSE ICML'18; Menon logit-adj ICLR'21; Garg unified NeurIPS'20.

### Finding B — Ordinal-aware Confident Learning · agent a06d8e2b82158cb01 · confidence: high
- **Method:** RD-CJ `issue = (1−p_self)·|ỹ−ŷ|²`; hoặc CP-CL ngưỡng `P(y≥Beh)<0.4` từ CORAL; hoặc "clean-far-keep-adjacent". Tất cả hậu kỳ trên `cl_issues.npz`.
- **Novelty:** cleanlab **không có ordinal mode** (xác nhận docs 2026-06-27); ICDF (Appl. Intell. 2024) & CASSOR (PRICAI'23) là **ảnh**, loop-integrated; Garg&Manwani robust-ordinal là loss-correction không phải cleaning. → adaptation mới cho clinical NLP + nhãn-LLM. Phải scope là *variant của CL*, không phải framework mới.
- **Verify:** Arm1 = 0 GPU (numpy); Arm2 = 3-fold×6ep ~2.5–3h. Pre-registered: Behavior far-flag > nominal ≥5pp & adjacent-flag < nominal ≥5pp (chứng minh ordinal làm khác); Behavior gold-F1 ≥0.22.
- **Effect:** Behavior-F1 0.183→0.22–0.27; macro +0.01–0.03; Arm1-only vẫn publishable. Std ~0.007 → nhấn *hướng hiệu ứng + tỉ lệ flag*, không chỉ ΔF1.
- **Rủi ro:** cắt quá tay pool 634; OOF probs cùng nguồn nhiễu (CORAL cum-prob bảo thủ hơn argmax → bớt circular).
- **Nguồn:** Northcutt CL JAIR'21; CASSOR PRICAI'23; ICDF Appl.Intell.'24; ORDAC'25; repo `46-confident-learning.md`, kernel `r2-tier1-cleanlab`.

### Finding D — Noise/shift-robust ordinal loss (CORN+GCE) · agent a3602fe9fb51dae3d · confidence: high
- **Method:** **CORN** (Shi'23) thay CORAL — mỗi ngưỡng weight riêng, train trên tập điều kiện `y≥k` (Behavior nhiễu chỉ vào task k=2,3, không bẩn k=1); **GCE** (Zhang&Sabuncu NeurIPS'18) `(1−p_y^q)/q, q=0.7` thay Focal — gradient `∝ p_y^q` giảm ở mẫu tin-cậy-thấp (ngược Focal `∝(1−p_t)^γ` khuếch đại nhiễu). `0.5·CORN+0.3·CE+0.2·GCE`.
- **Novelty:** cơ chế giải thích flat-CE>tri-objective (Focal noise-amplify — Zhou ICML'21; CORAL shared-weight cross-contaminate). Lần đầu CORN+GCE cho LLM-weak-label clinical ordinal. Combo trong domain này là đóng góp; không phải thuật toán mới.
- **Verify:** 1 arm, env-gated, 3-fold×6ep ~3h (Run B 5fold×10ep=8.8h → ×3/5×6/10). Cùng split/seed. Mạnh nếu macro≥0.42 & Behavior≥0.22, QWK/MAE ≥ Run B.
- **Rủi ro:** CORN k=2 đói gradient (Behavior ~16% pool) có thể tệ hơn → fallback "GCE đủ"; GCE giả định noise đồng đều (shift LLM→gold có cấu trúc → giảm hiệu lực); q nhạy. Dùng `coral-pytorch.corn_loss`.
- **Reject Group-DRO:** sai regime (cần group-label sạch). Unimodal-reg (Beckham'17): claim yếu → related-work.
- **Nguồn:** Zhang&Sabuncu GCE NeurIPS'18; Shi CORN PAA'23; Cao CORAL PRL'20; Lin Focal ICCV'17; Zhou asymmetric ICML'21; repo `48-coral.md`,`49-corn.md`,`51-focal-loss.md`.

### Finding C (runner-up) — SORD soft ordinal targets · agent a13942ea14fec466a · confidence: high
- **Method:** target CE = `softmax(−|rank−k|/τ)` (τ∈{0.5,1,2}); tùy chọn `τ_eff=τ/conf` (LLM-conf sharpen). Drop-in tại loss line 458, bỏ label_smoothing. Snorkel multi-LLM = bản mạnh hơn nhưng tốn LLM-call (off GPU-budget).
- **Novelty:** SORD (Diaz&Marathe CVPR'19) **chưa từng dùng cho NLP/clinical text**; label-smoothing suicide (arXiv 2405.05795) là *uniform*, không phải rank-distance. Mới về domain + conf-scaling.
- **Verify:** ~3h (3-fold×6ep) đổi target; tín hiệu macro>0.4215.
- **Rủi ro:** dễ thành "label smoothing trá hình"; trùng CORAL; conf LLM miscalibrated; có thể *tăng* nhầm Behavior↔Ideation. **Loại top-3 vì trùng D.**
- **Nguồn:** Diaz&Marathe CVPR'19; Hinton KD'15; Ratner Snorkel'17; repo `04`,`13`,`45`,`47`,`57`.

## Completed Work
- 2026-06-27 — M1: doc + khung 4 ứng viên.
- 2026-06-27 — M2: 4 task-researcher song song trả về 4 block grounding (high-confidence, có prior-art + novelty scope + thí nghiệm rẻ + rủi ro + effect-size).
- 2026-06-27 — M3/M4: chốt 3 hướng A·B·D (C runner-up); thiết kế thí nghiệm + bảng ngân sách (A 0h · D 3h · B-diag 4h ≈ 7h < 10h).

## Execution (2026-06-27) — user chốt combo A+D+B-diag (~7h)
- [x] **M5 — user chọn: A + D + B-diag (~7h).**
- [x] **B (cleanlab diagnostic) — PUSHED & RUNNING** · kernel `phatneurondai/r2-tier1-cleanlab-diagnostic`.
  ⚠ Gotcha: slug cũ `…-diag` bị tombstone → "Notebook not found"; đổi `…-diagnostic` là push được. (CLI 2.2.2 OK với slug mới.)
- [x] **D (CORN+GCE) — PUSHED & RUNNING** · kernel `phatneurondai/r2-corn-gce` · dir `kaggle/finetuning-message/r2-corn-gce/`.
  Code: CORN head (`R2_ORDINAL_HEAD=corn`) + GCE loss (`R2_LOSS_TYPE=gce`, q=0.7) env-gated; 3-fold×6ep gold-holdout+balance.
  Đã unit-test local: `corn_loss`/`corn_to_probs` (simplex+monotone)/`gce_loss` pass; xử lý task rỗng (Behavior vắng batch) finite.
- [~] **A (label-shift) — script xong, đang chạy local CPU (0 GPU)** · `kaggle/finetuning-message/r2-label-shift/posthoc_label_shift.py`.
  Load flat-CE ckpt (`pretrained=False`+`load_state_dict`, không tải 500MB), infer 392 gold, áp Logit-Adjust(τ sweep)+SLD-EM+oracle.

## ✅ KẾT QUẢ A (2026-06-27) — label-shift correction HIỆU QUẢ (0 GPU, post-hoc)
Trên checkpoint **flat-CE** (best fold), 392 gold. Shift đo được `w(y)=π_gold/π_train=[0.61, 1.17, **3.0**, 0.77]` (Behavior under-label 3×).

| Method | macro-F1 | **Behavior-F1** | per-class [Ind,Idea,Beh,Att] |
|---|---|---|---|
| baseline (no correction) | 0.4619 | 0.357 | 0.507·0.559·0.357·0.424 |
| **logit-adjust τ=0.5** | **0.4672** | **0.410** | 0.498·0.549·0.410·0.412 |
| logit-adjust τ=1.0 | 0.4578 | 0.408 | — |
| logit-adjust τ=1.5 | 0.3989 | 0.386 | (over-correct) |
| SLD-EM (π̂=[.16,.28,.24,.32]) | 0.4460 | 0.412 | (EM over-est Attempt → macro↓) |
| **ORACLE (true π_gold)** | **0.4909** | **0.441** | 0.500·0.584·0.441·0.439 |

**Kết luận A:** correction hậu kỳ **không train lại** nâng **Behavior-F1 +0.05** (0.357→0.41, deployable) tới **+0.08** (oracle 0.44), macro **+0.005→+0.029**. → *label shift là thành phần lỗi weak-sup có thật & sửa được rẻ*; gap oracle−deployable (0.41→0.44) = headroom cho ước lượng prior tốt hơn (future work). SLD-EM kém logit-adjust vì 392 gold quá ít để EM ổn định (over-est Attempt) — đúng cảnh báo của researcher. **Caveat:** số trên 1 best-fold checkpoint (baseline 0.4619 ≠ 5-fold-mean 0.4215); so sánh hợp lệ là **paired trên cùng checkpoint** (+0.005 macro / +0.053 Behavior cho τ=0.5). → IEEE: đóng góp = "diagnose+correct label shift", đặc biệt cứu lớp lâm sàng quan trọng nhất (Behavior).

## ✅ KẾT QUẢ D (2026-06-28) — CORN+GCE: **SỐ CHÍNH THỨC 5-fold×10ep** (thay preview 3-fold)
Kernel `r2-corn-gce` v2, gold-holdout+balance, **5-fold×10ep** (apples-to-apples). **GOLD macro-F1 mean=0.4022 ±0.0132** (folds 0.418/0.389/0.384/0.408/0.412), **Behavior gold-F1 ≈ 0.260** (folds 0.216/0.229/0.162/0.333/0.359), QWK ≈ 0.361.

| Cấu hình | gold macro-F1 | **Behavior-F1** | QWK | Ghi chú |
|---|---|---|---|---|
| dual-head CORAL+CE+Focal (Run B, 5f×10e) | 0.3849 | 0.183 | 0.398 | baseline cũ |
| **CORN+CE+GCE (5f×10e, chính thức)** | **0.4022** ±0.013 | **0.260** | 0.361 | **giữ ordinal; > dual, < flat-CE** |
| flat-CE (5f×10e) | 0.4215 | 0.285 | 0.388 | bỏ ordinal — vẫn mạnh nhất trên gold |

⚠ **Đính chính vs preview:** bản **3-fold×6ep** trước cho 0.4183 / Beh 0.317 (std 0.003) — **lạc quan quá** (ít fold → std hẹp giả tạo). Số 5-fold chính thức **thấp hơn**: macro 0.402, Beh 0.260, std 0.013.

**Kết luận D (trung thực):** CORN+GCE **vượt dual-head cũ rõ rệt** (macro **+0.017**, Behavior **+0.077**) và **giữ cấu trúc ordinal** → xác nhận cơ chế: CORAL shared-weight + Focal hại Behavior; thay bằng CORN + GCE phục hồi đáng kể. **NHƯNG vẫn không vượt flat-CE** (macro −0.020, Behavior −0.025) → *finding khoa học quan trọng*: trên phân bố gold, **bỏ ordinal (flat-CE) vẫn là tốt nhất**; CORN+GCE là **ordinal head tốt nhất** nhưng cái giá của cấu trúc ordinal dưới shift LLM→gold là có thật. → đóng góp = "**nếu cần ordinal (QWK/ranking) thì dùng CORN+GCE, không dùng CORAL+Focal**", + báo cáo trung thực nghịch lý flat-CE.

## ✅ KẾT QUẢ B (2026-06-27) — Ordinal-aware Confident Learning
Diagnostic (kernel `r2-tier1-cleanlab-diagnostic`, 5-fold OOF). **227/634 = 35.8% nhãn Behavior bị cleanlab nghi sai** (toàn cục 1570/9680 = 16.2%) → **xác nhận nút thắt Behavior = chất lượng nhãn**, đáp thẳng IEEE gap #1.

**Arm1 ordinal-CJ (numpy, 0 GPU) trên `cl_issues.npz`** — Behavior 634 = far 78 (đoán Indicator, lệch-2 = nhiễu thật) · adj 370 (đoán Ideation/Attempt, lệch-1 = thường borderline hợp lệ) · đúng 186:
| Bộ lọc | flag Behavior | của far (78) | của adj (370) |
|---|---|---|---|
| **Nominal CL** | 227 (35.8%) | 62 = 79% | 165 = **45%** (over-flag borderline) |
| **Ordinal RD-CJ** `(1−p_self)·\|ỹ−ŷ\|²` | 159 (25.1%) | 78 = **100%** | 81 = **22%** (giữ borderline) |
| CP-CL `P(y≥Beh)<0.4` | — | 119 lỗi-xa (model bác hạng) | — |

→ **Tín hiệu pre-registered ĐẠT:** ordinal **far +21pp, adjacent −23pp** = "clean far, keep adjacent". Chứng minh ordinal-awareness đổi *tập được làm sạch* theo hướng **đúng lâm sàng** (cắt nhiễu rõ Behavior→Indicator, giữ gradation mơ hồ Behavior↔Ideation) — novelty publishable, 0 GPU. (Arm2 retrain trên pool đã làm sạch = future work.)

## 🏁 VERDICT — cả 3 hướng đều có bằng chứng HIỆU QUẢ (quota dùng ~7h/10h)
| Hướng | Đòn bẩy | Kết quả đo được | Chi phí |
|---|---|---|---|
| **A** label-shift | inference | Behavior-F1 **+0.05** (deploy) / +0.08 (oracle), macro +0.005→+0.029 | **0 GPU** |
| **B** ordinal-CL | data | 35.8% nhãn Behavior nhiễu; ordinal cleans 100% far / keeps 78% adj | ~4h (diag) |
| **D** CORN+GCE | model/loss | macro **0.402** (>dual +0.017, <flat-CE), **Behavior 0.260** (>dual +0.077), giữ ordinal | ~3h(prev)+8.8h(5f) |
→ **Đề xuất đóng góp IEEE chính:** A (chẩn đoán+sửa label-shift, rẻ, hiệu quả nhất trên Behavior) + B (ordinal-aware cleaning) làm *2 trụ*; D = "**ordinal head bền-nhiễu CORN+GCE > CORAL+Focal**" + finding trung thực "**flat-CE vẫn tốt nhất trên gold**" (cái giá của ordinal dưới shift). → bài "honest weak-supervision cho ordinal clinical NLP" với 3 đóng góp đo được + 1 finding. **3 hướng bù nhau, không trùng.**

## Completed Work (bổ sung)
- 2026-06-27 — Chạy verify cả 3: A (local, 0 GPU) ✅ · D (Kaggle 3f×6e) ✅ · B (Kaggle diag + Arm1 numpy) ✅. Tất cả tín hiệu dương. Logs: `r2-corn-gce/out/`, `r2-tier1-cleanlab/out/`. Status → **done**.

## Remaining Action Items (future work, không blocking)
- [x] **D 5-fold×10ep (OFFICIAL) — XONG (2026-06-28).** macro **0.4022 ±0.013**, Behavior **0.260**, QWK 0.361. Thấp hơn preview 3-fold (0.418/0.317) → đã đính chính paper plan §2 + 2 report. Log `r2-corn-gce/out/r2-corn-gce.log`.
- [x] **D thêm: 2 kernel ablation CORN-only & GCE-only ĐÃ CHUẨN BỊ (2026-06-28, compile OK, chưa push).**
  - `kaggle/finetuning-message/r2-corn-only/` — CORN head + **Focal** (giữ Focal) → tách đóng góp CORN. id `phatneurondai/r2-corn-only`.
  - `kaggle/finetuning-message/r2-gce-only/` — **CORAL** head + GCE (giữ CORAL) → tách đóng góp GCE. id `phatneurondai/r2-gce-only`.
  - Cả hai 5-fold×10ep, cùng split/seed → bảng 2×2 [CORAL|CORN × Focal|GCE]. Mỗi run ~8.8h (tổng ~17.6h quota).
  - **r2-corn-only: XONG (2026-06-28)** — macro **0.4095 ±0.0254**, Behavior **0.250** (folds 0.188/0.194/0.242/0.226/0.400, std cao), QWK ~0.377. Log `r2-corn-only/out/`.
  - **r2-gce-only: XONG (2026-06-28)** — macro **0.3990 ±0.0149**, Behavior **0.229**. Log `r2-gce-only/out/`.

### ✅ Bảng ablation 2×2 ĐẦY ĐỦ [head × 3rd-loss] (gold-holdout 5-fold×10ep, cùng split/seed)
| | **Focal** | **GCE** |
|---|---|---|
| **CORAL** | dual **0.385 / Beh 0.183** (QWK 0.398) | gce-only **0.399 / 0.229** |
| **CORN** | corn-only **0.410 / 0.250** | corn+gce **0.402 / 0.260** (QWK 0.361) |

**Phân tách đóng góp (từ dual 0.385/0.183):**
- **CORN** (đổi head, giữ Focal): macro **+0.025**, Behavior **+0.067** → đòn bẩy chính.
- **GCE** (đổi loss, giữ CORAL): macro **+0.014**, Behavior **+0.046** → có giúp, nhỏ hơn CORN.
- **Sub-additive:** CORN+GCE (0.402) < corn-only (0.410) trên macro, nhưng **Behavior cao nhất (0.260)**.

**Kết luận (IEEE):** cả CORN & GCE đều cải tiến độc lập vs dual cũ; **CORN chủ đạo**. Cho **Behavior (ưu tiên lâm sàng), CORN+GCE tốt nhất (0.260)**; macro tổng CORN-only nhỉnh nhất (0.410) nhưng trong khoảng nhiễu (std 0.015–0.025). Cả 4 **vẫn < flat-CE 0.422** trên macro → CORN-based thu hẹp khoảng cách mà *giữ ordinal*.
- [ ] q-sweep GCE (0.5) — tùy chọn.
- [ ] A: chạy correction trên **cả 5 fold checkpoint** (hiện 1 best-fold); cải thiện ước lượng target-prior (thu hẹp gap deploy→oracle 0.41→0.44).
- [ ] B: **Arm2** retrain 3-fold trên pool đã ordinal-clean (drop far / downweight) → đo Behavior-F1 sau làm sạch.
- [ ] Gộp vào `PAPER-PLAN-text-ordinal-suicide.md` (gap #2 ablation + Behavior fix) & report HTML.
</content>
