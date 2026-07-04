# Pebble‑LLM — Toàn cảnh Thesis (tổng hợp để báo cáo)

**Dự án:** Pebble‑LLM — Mô hình hoá cảm xúc nhạy‑khủng‑hoảng cho **text** và **voice**
**Ngày tổng hợp:** 2026‑07‑02 (viết lại từ bản 2026‑06‑27) · **Nhánh:** main · **Người tổng hợp:** Research team

> Tài liệu này dựng lại toàn bộ hành trình thesis: **mục đích ban đầu → các version → cải tiến → thực nghiệm → kết quả**.
> Nguồn: `pebble-finetuning-strategy-v3.md`, `progress.md`, `docs/reports/*`, `docs/tasks/*`, `docs/papers/*`.
> **Mới so với bản trước:** ✅ toàn bộ số headline đã **kiểm chứng khớp retained‑log** (2026‑07‑02);
> ✅ 3 đóng góp phương pháp có số 5‑fold chính thức + bảng ablation 2×2; ✅ 2 baseline đã chạy xong.

---

## 0. Tóm tắt 1 phút (cho sếp)

- **Xuất phát điểm:** Pebble là app companion sức khoẻ tinh thần. Bài toán gốc là **thay kiến trúc single‑call Gemini** bằng **một classifier cảm xúc fine‑tune riêng**, chạy *trước* bước sinh phản hồi để Decision Engine định tuyến tốt hơn.
- **Đã pivot** (có chủ đích, ghi ở intent layer) sang **2 bài báo IEEE**: **(A) Text** — phân loại **ordinal** nguy cơ tự sát; **(B) Voice** — affect giọng nói nhạy‑khủng‑hoảng.
- **Kết quả lõi — thật, đã kiểm chứng log (2026‑07‑02):**
  - **Text:** gold‑holdout trung thực cải thiện **0.19 → 0.4215** (~×2.2); **3 đóng góp phương pháp** đều có hiệu quả đo được (CORN+GCE cứu Behavior 0.183→0.260; label‑shift correction 0.357→0.41 không train lại; ordinal‑CL phát hiện 35.8% nhãn Behavior nhiễu). Within‑distribution đạt **0.653** — cao hơn số paper 0.510, *cùng giao thức nhưng trên tập 10k tự làm giàu, không phải benchmark gated gốc* (không claim SOTA).
  - **Mọi cấu hình của ta đều vượt cả 2 baseline** (plain‑RoBERTa 0.346 · BiLSTM‑MTL 0.378) trên cùng split.
  - **Voice:** chọn xong backbone (WavLM‑Large thắng emotion2vec, 3/3 seed) + crisis head **precision 0.617 tại sàn recall ≥ 0.90**.
- **Việc còn lại trên đường tới‑hạn là *dữ liệu/chất lượng nhãn*, không phải code model** — đo κ nhãn‑LLM↔gold (Text) và xin quyền MSP‑Podcast/DAIC‑WOZ (Voice). Cả hai bị flag "start early" từ 2026‑06‑27, **chưa bắt đầu** → rủi ro lịch trình số 1.

> **Lưu ý thuật ngữ:** **"R2"** = tên paper tham chiếu *"Hierarchical Dual‑Head"* (Yang et al., IEEE BigData 2025) mà ta **tái lập & so sánh** — KHÔNG phải "version 2" của hệ thống. "R1" = paper HMT‑BB (BERT+BiLSTM, 2025), dùng làm baseline thiết kế.

---

## PHẦN A — VERSION ĐẦU TIÊN: Emotion Classifier cho sản phẩm (Strategy v1 → v3)

### A.1 Mục đích ban đầu & mong muốn

Thay **single‑call Gemini** bằng một **classifier chuyên biệt, fine‑tune, self‑hosted**, chạy trước bước generation. 4 mong muốn:

1. **Tăng tính nhất quán** khi chấm điểm (specialist ổn định hơn generalist được prompt).
2. **Cho Decision Engine làm việc trên điểm có cấu trúc *trước* khi sinh phản hồi.**
3. **Tách khỏi vòng đời model Gemini** ở thời điểm inference.
4. **Xoá lỗi JSON malformed** (encoder xuất head tensor có kiểu, không parse JSON).

**Đầu ra mong muốn — 1 object/tin nhắn (6 chiều):** `energy`, `severity`, `socialIsolation`, `receptivity`, `detectedEmotion`, `safetyFlag`.

### A.2 Các version chiến lược

| Version | Quyết định kiến trúc chính | Vì sao đổi |
|---|---|---|
| **v2.0 / v2.1** | **Gemini 2.5 Flash‑Lite SFT** là model chính | Đơn giản, không gánh serving; nhưng vẫn dính lỗi JSON + phụ thuộc vòng đời Gemini |
| **v3.0 (May 2026)** | **NeoBERT** (250M, self‑hosted, MIT) là **chính**; Gemini Flash‑Lite backup; ModernBERT fallback | Lấy nhất quán + decouple + bỏ lỗi JSON. Đánh đổi: gánh serving quay lại |

### A.3 Kết quả version đầu (nền tảng + kế hoạch)

- Chủ yếu là **chiến lược + foundation code** (taxonomy 12‑nhãn, multi‑task heads, user‑level split, serving schema), dừng ở Phase 5, chưa ra số train sản phẩm.
- **Kaggle GPU smoke test = GO** với stack pin chuẩn (torch 2.5.1+cu121 trên P100) — gotcha còn dùng tới giờ.

> **Cầu nối sang Phần B:** khi chuyển trọng tâm sang đóng góp học thuật (IEEE), dự án tổ chức lại thành 2 stream — `finetuning-message` (text) và `voice` — và bài toán cảm xúc tổng quát được chuyên biệt hoá thành 2 bài có gold‑standard & benchmark rõ ràng.

---

## PHẦN B — VERSION HIỆN TẠI: 2 bài báo IEEE

| Stream | Bài báo | Lõi thực nghiệm | Blocker tới‑hạn |
|---|---|---|---|
| **Text/Message** | Weakly‑Supervised Augmentation cho Ordinal Suicide‑Risk | ✅ Xong phần model (3 đóng góp + ablation 2×2 + 2 baseline) | κ chất lượng nhãn‑LLM |
| **Voice** | Backbone + Recall‑Floored Heterogeneous Heads | ✅ Backbone xong; MTL (M3) chờ chạy | Quyền MSP‑Podcast |

---

## PHẦN B1 — TEXT: Ordinal Suicide‑Risk

### B1.0 Bài toán & mô hình
- **Task:** phân loại **ordinal 4 mức C‑SSRS** (Indicator < Ideation < Behavior < Attempt) từ chuỗi post Reddit.
- **Mô hình nền (tái lập paper R2):** MentalRoBERTa(mirror) → seq‑transformer 3 lớp → attention‑pool → CORAL head + CE head, loss tri‑objective, freeze 6 lớp, max_len 256.
- **Khung đánh giá (không phải đóng góp lõi): gold‑holdout protocol** — train trên nhãn‑LLM (rẻ, nhiều ~9.7k), **eval trên nhãn lâm sàng CSSRS held‑out** (392, disjoint theo user) → lợi ích weak‑supervision đo được **trung thực, không circular**.

### B1.1 Chuỗi version thực nghiệm (mỗi dòng: đổi gì → đo ra sao → kết quả)

> ✅ = số đã kiểm chứng khớp retained‑log 2026‑07‑02 (bảng đối chiếu: `docs/tasks/thesis-message-review.md`;
> tổng hợp máy‑đọc‑được: `kaggle/finetuning-message/results-summary.csv`).

| # | Version / vòng | Thay đổi chính | Giao thức | Macro‑F1 | Ghi chú |
|---|---|---|---|---|---|
| 1 | Baseline gold‑CV | Train trên gold lâm sàng (ít) | gold→gold | 0.19 | Quá ít nhãn lâm sàng → trần thấp |
| 2 | Weak‑sup within‑LLM | ~10k post nhãn‑LLM, train+eval trên LLM | within‑LLM (**circular**) | 0.67 | *Tự đánh lừa* — giữ lại chỉ để lộ tính circular |
| 3 | Gold‑holdout đầu tiên | Train nhãn‑LLM, eval gold held‑out | cross‑to‑gold (honest) | 0.3569 | Con số trung thực đầu tiên |
| 4 | + Behavior rebalance (Run B) | WeightedRandomSampler nghịch‑tần | gold‑holdout | **0.3849** ±0.007 ✅ | QWK 0.378→0.398, MAE 0.840→0.822 |
| 5 | Within‑dist CV sạch (Run A) | 5‑fold CV đủ 10,072 mẫu (sửa bug mount) | within‑distribution | **0.6530** ±0.005 ✅ | > số paper 0.5098; *cùng giao thức, khác dataset — xem caveat §B1.2* |
| 6 | Ablation flat‑CE | Bỏ CORAL+Focal, chỉ CE thuần | gold‑holdout | **0.4215** ±0.024 ✅ | Bất ngờ: > dual‑head; Behavior 0.183→0.285 |
| 7 | **CORN+GCE** (đóng góp 1) | CORAL→CORN, Focal→GCE | gold‑holdout | **0.4022** ±0.013 ✅ | Ordinal head tốt nhất; Behavior 0.260 |
| 8 | Ablation 2×2 tách đòn bẩy | corn‑only · gce‑only | gold‑holdout | 0.4095 / 0.3990 ✅ | CORN là đòn bẩy chính (bảng dưới) |
| 9 | **Label‑shift correction** (đóng góp 2) | Logit‑Adjust hậu kỳ, **0 train lại** | post‑hoc trên gold | Behavior 0.357→**0.41** ✅ | shift đo được 3.0×; oracle 0.44 |
| 10 | **Ordinal‑CL diagnostic** (đóng góp 3) | cleanlab + trọng số khoảng‑cách‑hạng | 5‑fold OOF | **35.8%** nhãn Behavior nghi sai ✅ | "clean far, keep adjacent" |
| 11 | 2 baseline IEEE | plain‑RoBERTa‑CE · BiLSTM‑MTL | gold‑holdout | **0.3456** / **0.3783** ✅ | chạy xong 2026‑06‑28; mọi cấu hình của ta đều vượt |

**Bảng 3 giao thức (đóng gói cho paper):**

| Giao thức | Train | Eval | Macro‑F1 | QWK |
|---|:--:|:--:|:--:|:--:|
| Gold‑CV | gold | gold | 0.19 | 0.24 |
| Within‑LLM *(circular — chỉ để lộ vấn đề)* | LLM | LLM | 0.67 | — |
| **Cross‑to‑gold (của ta)** | LLM | gold | **0.3849** (dual) → **0.4215** (flat‑CE, tốt nhất) | 0.398 / 0.388 |

**Bảng ablation 2×2 [head × 3rd‑loss] (gold‑holdout 5‑fold×10ep, cùng split/seed) + flat‑CE + baselines:**

| Cấu hình | gold macro‑F1 | Behavior‑F1 | QWK |
|---|:--:|:--:|:--:|
| baseline plain‑RoBERTa‑CE (mean‑pool, không seq/ordinal) | 0.3456 ±0.026 | — | — |
| baseline BiLSTM‑MTL (baseline của paper gốc, reimpl) | 0.3783 ±0.014 | — | — |
| CORAL + Focal (dual‑head cũ, Run B) | 0.3849 ±0.007 | 0.183 | 0.398 |
| CORAL + GCE (gce‑only) | 0.3990 ±0.015 | 0.229 | 0.382 |
| CORN + Focal (corn‑only) | 0.4095 ±0.025 | 0.250 | 0.377 |
| **CORN + GCE (đóng góp 1)** | 0.4022 ±0.013 | **0.260** | 0.361 |
| **flat‑CE (bỏ ordinal — finding trung thực)** | **0.4215** ±0.024 | 0.285 | 0.388 |

**Đọc bảng một cách khách quan:**
- **CORN là đòn bẩy chính** (+0.025 macro / +0.067 Behavior vs dual cũ); GCE giúp độc lập nhưng nhỏ hơn (+0.014 / +0.046); kết hợp sub‑additive trên macro nhưng **Behavior cao nhất ở CORN+GCE (0.260)**.
- ⚠ **Khác biệt giữa các biến thể ordinal (0.399–0.410) nằm trong khoảng nhiễu** (std 0.013–0.025, 5 fold, phần lớn 1 seed) — "CORN chủ đạo" là xu hướng nhất quán, chưa phải khẳng định thống kê; cần paired per‑fold test (rẻ, cùng split) trước khi vào bảng paper.
- Kiến trúc hierarchical mua được **+0.04–0.08** so với plain encoder trên gold (0.346 → 0.385–0.422).
- **Per‑class gold (Run B dual):** Indicator 0.50 · Ideation 0.48 · **Behavior 0.18 ⚠** · Attempt 0.37. Behavior sau 3 đóng góp: tốt nhất **0.285–0.41** tùy phương pháp — vẫn là lớp yếu nhất.

### B1.2 Phát hiện quan trọng (kèm caveat bắt buộc khi trình bày)

1. **Within‑distribution 0.653 > 0.510 của paper** — **caveat gắn liền, không tách rời headline:** đây là *cùng giao thức* within‑distribution nhưng trên **tập 10k tự làm giàu bằng nhãn‑LLM của ta**, không phải benchmark gated gốc của paper, và 0.653 đo **trên nhãn LLM** (đúng loại số mà protocol của ta dạy người đọc nghi ngờ). Framing đúng: *"tái lập kiến trúc đạt 0.653 trên protocol tương đương của chúng tôi; paper báo 0.510 trên benchmark của họ — không so trực tiếp được."* KHÔNG claim SOTA/benchmark.
2. **flat‑CE > mọi ordinal head trên gold** (0.4215 vs 0.402 tốt nhất) — **negative finding giữ lại làm đóng góp**: cấu trúc ordinal trả giá thật dưới label‑shift LLM→gold. Cơ chế đã xác định: CORAL shared‑weight cross‑contaminate lớp hiếm, Focal khuếch đại mẫu nhiễu → CORN+GCE thu hẹp nhưng không xoá gap. Khuyến nghị paper: *dùng CORN+GCE khi cần ordinal ranking (QWK); flat‑CE khi chỉ cần macro‑F1*.
3. **Nút thắt Behavior là CHẤT LƯỢNG NHÃN, không phải sampling** — 3 bằng chứng hội tụ: chỉ 634 mẫu Behavior trong pool LLM (7.3%) vs 19.7% ở gold (**under‑label 3.0×**, đo trực tiếp); cleanlab flag **35.8%** nhãn Behavior; rebalance không phá được trần.
4. **Gap LLM↔gold (~0.25 macro‑F1: 0.67 within vs 0.42 cross)** là đại lượng trung tâm của paper — hiện mới giải thích được một phần (shift 3× + 35.8% nhiễu); **Cohen's κ trên tập overlap là mảnh còn thiếu** để đóng khung định lượng.

### B1.3 Trạng thái provenance (constraint #4 / IDD I5) — ✅ ĐẦY ĐỦ (2026‑07‑02)

- Toàn bộ số headline trace được: **kernel code committed** (git) + **slug@version** (Kaggle bất biến) + **retained log** trong `kaggle/finetuning-message/<kernel>/out/` (local, gitignored) + **`results-summary.csv`** (committed, máy đọc được).
- Đối chiếu độc lập 2026‑07‑02: **6/6 số headline khớp chính xác log** (chi tiết: `docs/tasks/thesis-message-review.md`). Không phát hiện sai lệch nào giữa report và log gốc.
- Lịch sử trung thực đáng giữ: preview 3‑fold CORN+GCE (0.418/Beh 0.317) **lạc quan quá** → tự đính chính công khai xuống số 5‑fold chính thức (0.402/0.260).

### B1.4 Còn thiếu để IEEE duyệt (ưu tiên giảm dần)

- 🔴 **(1) Cohen's κ + confusion LLM‑vs‑gold** trên tập overlap — giải thích gap, mở khoá narrative đóng góp 3; reviewer sẽ hỏi đầu tiên. **Chưa bắt đầu.**
- 🟡 **(2) Significance:** paired per‑fold delta cho các cặp flat‑CE / CORN+GCE / dual (cùng split/seed nên rất rẻ).
- 🟡 **(3) Label‑shift trên cả 5 fold** (hiện 1 best‑fold checkpoint; kernel chỉ lưu best‑fold → cần sửa kernel lưu đủ 5).
- 🟡 **(4) B‑Arm2:** retrain trên pool đã ordinal‑clean (`cl_issues.npz` đã có local) → đo Behavior sau làm sạch.
- 🟡 **(5) Ethics & provenance scrape** (pullpush, ~9% content‑filtered, de‑identification) — IEEE clinical bắt buộc.
- 🟢 (6) Bảng ablation & baselines — **XONG**. 🟢 (7) Draft: abstract + intro + related work đã viết (`PAPER-DRAFT-text-ordinal-suicide.md`).

---

## PHẦN B2 — VOICE: Crisis‑sensitive speech affect

### B2.1 Mục tiêu & version
Chọn **backbone giọng nói** mạnh nhất rồi gắn các **head dị‑chủng** (emotion + affect CCC + crisis) với **sàn recall** cho head khủng hoảng.

| Vòng | Thực nghiệm | Kết quả |
|---|---|---|
| **V1 — Reproduction** | emotion2vec linear‑probe trên RAVDESS | tái lập + deploy HF Space |
| **V2 — Backbone selection** | emotion2vec vs **WavLM‑Large** (frozen probe, 8‑class, 3 seed) | **WavLM thắng 0.609±0.019 vs 0.537±0.007**, paired Δ −0.071 (**3/3 seed**) |
| **V3 — Crisis head (recall‑floor)** | Distress head dưới ràng buộc cứng recall | **Precision 0.617±0.003 tại recall ≥ 0.90** (ngưỡng 0.69) |
| **V4 — MTL heads (M3–M5)** | emotion + affect CCC + crisis cùng lúc | ⏳ kernel đã build; **đang chờ chạy Kaggle** |

- **Caveat:** RAVDESS distress + affect = **proxy** (acted, circumplex ~ circular) → cần nhãn thật (MSP‑Podcast).

### B2.2 Còn thiếu
🔴 Quyền **MSP‑Podcast** (nhãn V/A/D thật) — latency ngoài tầm kiểm soát, xin trước. 🔴 Chạy **MTL‑heads (M3–M5)** lấy số 10‑fold. 🟡 Ablation (Kendall vs GradNorm/PCGrad) · baseline eGeMAPS SER.

---

## PHẦN C — Thu thập dữ liệu & xin quyền sử dụng (DUA / EULA)

Đây là **đường tới‑hạn thật sự** của thesis: nhiều dataset lâm sàng bị *gated*, latency xin quyền **1–4 tuần** ngoài tầm kiểm soát → phải khởi động sớm. **Trạng thái 2026‑07‑02: các đơn chưa được gửi — đã trễ so với flag "start early" 2026‑06‑27.**

**Chiến lược 2 nhánh (license là bộ lọc cứng):**

| Nhánh | Nguồn được phép | Vì sao |
|---|---|---|
| **Model triển khai (deployed)** | **CHỈ** CSSRS‑Reddit (CC‑BY‑4.0) | License duy nhất cho phép *serve* model đã train |
| **Nghiên cứu / paper** | CSSRS‑Reddit **+** DAIC‑WOZ **+** SMHD/RSDD | DUA research‑only: train + eval, **KHÔNG** deploy |

> ⚠️ Checkpoint train trên DAIC‑WOZ / SMHD/RSDD **KHÔNG được ship** trong sản phẩm.

| Dataset | Vai trò | License / cổng | Trạng thái |
|---|---|---|---|
| **CSSRS‑Reddit** (Gaur, WWW'19) | gold C‑SSRS 500 user, 4 bác sĩ tâm thần | CC‑BY‑4.0 | ✅ Đã tải |
| **DAIC‑WOZ** (USC ICT) | PHQ‑8 depression, hội thoại lâm sàng → crisis cho voice | Research‑only EULA, email học thuật | 🔴 **ACTION REQUIRED — chưa bắt đầu** (~1–3 tuần) |
| **SMHD / RSDD** (Georgetown) | corpus domain‑adaptive pretrain | Research‑only DUA | 🔴 chưa bắt đầu (~2–4 tuần) |
| **MSP‑Podcast** | nhãn A/V/D thật cho affect head (voice) | gated (~3–5 ngày) | 🔴 cần xin |
| **IMHI** | OOD eval cho safety head | MIT | ✅ đã tải (19,051 hàng) |
| **CLPsych UMD** | (đã cân nhắc) | bắt xoá data + model sau workshop | ❌ loại |

**DAIC‑WOZ — các bước (bạn phải ký):** tải EULA tại <https://dcapswoz.ict.usc.edu/> → điền PI/lab, ký, gửi từ email học thuật → chờ ~1–3 tuần. Cover‑note soạn sẵn trong `docs/dataset-acquisition-plan.md`.

---

## PHẦN D — Hạ tầng & bài học vận hành (carry‑forward)

- **Kaggle:** auth qua `~/.kaggle/access_token` (token `KGAT_`). Kernel headline text nằm trên account **`phatneurondai`** (phone‑verified → GPU P100 + Internet); baseline + Run B trên `fabiocarava`. Backup token: `access_token.fabiocarava.bak`. Tối đa 2 GPU session đồng thời, quota tuần ≈ 30h P100.
- **Stack pin bắt buộc:** `torch==2.5.1+cu121` (P100 = sm_60; base‑image torch 2.10 không tương thích).
- **Bug mount đã sửa:** dataset mount sâu 3 cấp → recursive glob `**/sequences.csv` (trước đó rơi nhầm về Zenodo‑392 → số CV vô hiệu; 2 run đầu của Run A bị huỷ vì lỗi này).
- **Code đã env‑gate:** trọng số loss (`R2_W_CORAL/CE/FOCAL`), head (`R2_ORDINAL_HEAD=corn`), loss (`R2_LOSS_TYPE=gce`), rebalance (`R2_BALANCE`), gold‑holdout (`R2_GOLD_HOLDOUT`); `evaluate` chỉ blend head được train; `train_fold` có hook `sample_weight=` cho cleanlab.
- **Provenance:** log các run về `kaggle/**/out/` (gitignored) + `results-summary.csv` (committed). ⚠ Không commit `best_model.pt` (~595 MB/file; hiện ~2.9 GB local, xoá được nếu cần ổ đĩa — log là thứ quan trọng). ⚠ Kernel hiện chỉ lưu best‑fold checkpoint → muốn label‑shift 5‑fold phải sửa kernel.

---

## PHẦN E — Trạng thái & việc tiếp theo (2026‑07‑02)

| # | Việc | Stream | Vì sao |
|---|---|---|---|
| 🔴 1 | Đo **Cohen's κ** nhãn‑LLM ↔ gold trên tập overlap | Text | Blocker #1 của paper; reviewer hỏi đầu tiên |
| 🔴 2 | **Ký EULA DAIC‑WOZ** + xin **MSP‑Podcast / SMHD** | Voice+Text | Latency 1–4 tuần ngoài tầm kiểm soát; đã trễ flag "start early" |
| 🔴 3 | Chạy **MTL‑heads (M3–M5)** lấy 10‑fold | Voice | Trong tầm kiểm soát; chạy song song khi chờ data |
| 🟡 4 | Paired per‑fold significance (flat‑CE vs CORN+GCE vs dual) | Text | Các gap nhỏ hiện chưa phân biệt được với nhiễu |
| 🟡 5 | Label‑shift đủ 5 fold + B‑Arm2 retrain trên pool đã clean | Text | Hoàn thiện đóng góp 2 & 3 |
| 🟡 6 | Viết tiếp draft IEEE (Method/Experiments đã có bảng đầy đủ) | Text | Bảng ablation + baseline đã chốt số |

**Rủi ro then chốt:** cả 2 việc tới‑hạn là **thu thập dữ liệu/nhãn**, không phải code → khởi động ngay vì latency ngoài tầm kiểm soát.

---

### Nguồn tham chiếu
`docs/tasks/thesis-message-review.md` (kiểm chứng provenance 2026‑07‑02) · `kaggle/finetuning-message/results-summary.csv` ·
`docs/reports/{r2-ab-results, WEEKLY-REPORT-2026-06-29-thesis}.md` · `docs/tasks/{r2-method-improvements-for-contribution, r2-beat-paper-dual-report}.md` ·
`docs/papers/finetuning-message/{PAPER-PLAN, PAPER-DRAFT}-text-ordinal-suicide.md` · `docs/papers/voice/PAPER-PLAN-voice-crisis-affect.md` · `docs/dataset-acquisition-plan.md` · `docs/intent/constraints.md`
