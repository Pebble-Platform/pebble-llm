# Pebble‑LLM — Toàn cảnh Thesis (tổng hợp để báo cáo)

**Dự án:** Pebble‑LLM — Mô hình hoá cảm xúc nhạy‑khủng‑hoảng cho **text** và **voice**
**Ngày tổng hợp:** 2026‑06‑27 · **Nhánh:** main · **Người tổng hợp:** Research team

> Tài liệu này dựng lại toàn bộ hành trình thesis: **mục đích ban đầu → các version → cải tiến → thực nghiệm → kết quả**.
> Nguồn: `pebble-finetuning-strategy-v3.md`, `progress.md`, `docs/phases/`, `docs/reports/*`, `docs/tasks/*`, `docs/papers/*`.

---

## 0. Tóm tắt 1 phút (cho sếp)

- **Xuất phát điểm:** Pebble là app companion sức khoẻ tinh thần. Bài toán gốc là **thay kiến trúc single‑call Gemini** (một lời gọi Gemini vừa chấm cảm xúc vừa sinh phản hồi) bằng **một classifier cảm xúc fine‑tune riêng**, chạy *trước* bước sinh phản hồi để Decision Engine định tuyến tốt hơn.
- **Đã pivot** từ "một classifier 6‑đầu‑ra cho sản phẩm" sang **2 bài báo IEEE** có đóng góp học thuật rõ ràng: **(A) Text** — phân loại **ordinal** nguy cơ tự sát; **(B) Voice** — affect giọng nói nhạy‑khủng‑hoảng.
- **Kết quả lõi đã có số thật, trung thực:**
  - **Text: VƯỢT PAPER** trên thước đo within‑distribution: macro‑F1 **0.653 vs 0.510** của paper (+28%). Trên thước đo gold‑holdout trung thực (khó hơn), cải thiện **0.19 → 0.42**.
  - **Voice: chọn xong backbone** (WavLM‑Large thắng emotion2vec, 3/3 seed) + **crisis head có precision 0.617 tại sàn recall ≥ 0.90**.
- **Việc còn lại trên đường tới‑hạn là *dữ liệu/chất lượng nhãn*, không phải code model** — đo κ chất lượng nhãn‑LLM (Text) và xin quyền MSP‑Podcast (Voice).

> **Lưu ý thuật ngữ:** trong doc nội bộ, **"R2"** = tên paper tham chiếu *"Hierarchical Dual‑Head"* (suicide‑risk, 2025) mà ta **tái lập & vượt** — KHÔNG phải "version 2" của hệ thống. "R1" = paper HMT‑BB (BERT+BiLSTM, 2025), dùng làm baseline thiết kế.

---

## PHẦN A — VERSION ĐẦU TIÊN: Emotion Classifier cho sản phẩm (Strategy v1 → v3)

### A.1 Mục đích ban đầu & mong muốn

Thay **single‑call Gemini** bằng một **classifier chuyên biệt, fine‑tune, self‑hosted**, chạy trước bước generation. 4 mong muốn:

1. **Tăng tính nhất quán** khi chấm điểm (specialist ổn định hơn generalist được prompt).
2. **Cho Decision Engine làm việc trên điểm có cấu trúc *trước* khi sinh phản hồi** → định tuyến giàu thông tin hơn.
3. **Tách hoàn toàn khỏi vòng đời model Gemini** ở thời điểm inference (Gemini deprecate không đụng tới luồng routing).
4. **Xoá lỗi JSON malformed** (encoder xuất head tensor có kiểu, không parse JSON).

**Đầu ra mong muốn — 1 object/tin nhắn (6 chiều):**
`energy`, `severity`, `socialIsolation`, `receptivity`, `detectedEmotion`, `safetyFlag`.
(2 chiều `themeRepetition` & `sessionTrajectory` để lại cho Decision Engine vì cần bộ nhớ xuyên‑phiên.)

### A.2 Các version chiến lược

| Version | Quyết định kiến trúc chính | Vì sao đổi |
|---|---|---|
| **v2.0 / v2.1** | **Gemini 2.5 Flash‑Lite SFT** là model chính (không cần hạ tầng serving) | Đơn giản, không gánh serving; nhưng vẫn dính lỗi JSON + phụ thuộc vòng đời Gemini |
| **v3.0 (May 2026, hiện hành)** | **NeoBERT** (250M, self‑hosted, MIT) là **chính**; Gemini Flash‑Lite **hạ xuống backup**; ModernBERT là fallback thứ hai | Lấy tính nhất quán + decouple + bỏ lỗi JSON. **Đánh đổi: gánh nặng serving quay lại** (rủi ro lớn nhất) |

**Kiến trúc v3 (multi‑task trên `[CLS]` 768‑dim):** Score Head (sigmoid K chiều) · Emotion Head (warm‑start từ GoEmotions) · Safety Head (BCE, trọng số dương 10×). Loss = MSE + CE + 2×BCE.

**Dữ liệu transfer:** GoEmotions (58k) → emotion head; SemEval‑2018 EI‑reg intensity → severity; EmpatheticDialogues/DailyDialog/WASSA bổ trợ.

### A.3 Kết quả version đầu (thực chất là *nền tảng + kế hoạch*)

- Đây chủ yếu là **chiến lược + foundation code**, chưa ra số train sản phẩm (theo `progress.md`, dừng ở **Phase 5**).
- **Đã xong:** taxonomy 12‑nhãn + mapping GoEmotions; multi‑task heads + weighted loss; metrics §7; user‑level split; serving schema/FastAPI shape.
- **Kaggle GPU smoke test = GO:** NeoBERT (222M) load + forward fp32/fp16 + backward đều pass trên P100 — với **stack pin chuẩn** (torch 2.5.1+cu121, xformers 0.0.28, transformers 4.48.2). Đây là gotcha lớn còn dùng tới giờ.
- **Loaders + masked‑multitask assembler** xong (GoEmotions emotion + EI‑reg severity → bản ghi masked).
- **Quyết định v1 thu hẹp phạm vi:** chỉ học `detectedEmotion` + `severity`; 4 chiều còn lại thành heuristic của Decision Engine; bỏ annotation/safety/Gemini cho v1.

> **Cầu nối sang Phần B:** Khi chuyển trọng tâm sang **đóng góp học thuật (IEEE)**, dự án được tổ chức lại thành 2 stream — `finetuning-message` (text) và `voice` — và bài toán cảm xúc tổng quát được **chuyên biệt hoá** thành 2 bài có gold‑standard & benchmark rõ ràng.

---

## PHẦN B — VERSION HIỆN TẠI: 2 bài báo IEEE

| Stream | Bài báo | Lõi thực nghiệm | Blocker tới‑hạn |
|---|---|---|---|
| **Text/Message** | Weakly‑Supervised Augmentation cho Ordinal Suicide‑Risk | ✅ Xong | κ chất lượng nhãn‑LLM ↔ gold |
| **Voice** | Backbone + Recall‑Floored Heterogeneous Heads cho Crisis Affect | ✅ Backbone xong; MTL đang chờ | Quyền MSP‑Podcast |

---

## PHẦN B1 — TEXT: Ordinal Suicide‑Risk (tái lập & vượt paper "R2")

### B1.0 Bài toán & mô hình
- **Task:** phân loại **ordinal 4 mức C‑SSRS** (Indicator < Ideation < Behavior < Attempt) từ chuỗi post Reddit.
- **Mô hình:** Hierarchical dual‑head — encoder MentalRoBERTa(mirror) → seq‑transformer 3 lớp → attention‑pool → **CORAL head (ordinal) + CE head**, loss tri‑objective `0.5·CORAL + 0.3·CE + 0.2·Focal`, freeze 6 lớp encoder, max_len 256.
- **Đóng góp phương pháp luận (không claim SOTA):** **gold‑holdout protocol** — train trên nhãn‑LLM (rẻ, nhiều), **đánh giá trên nhãn lâm sàng held‑out** → đo lợi ích weak‑supervision **trung thực, không circular**.

### B1.1 Chuỗi "version" thực nghiệm (đây là phần "các version tiếp theo")

> Mỗi dòng là một vòng cải tiến: đổi gì → đo ra sao → kết quả.

| # | Version / vòng | Thay đổi chính | Giao thức đánh giá | Macro‑F1 | Ghi chú |
|---|---|---|---|---|---|
| 1 | **Baseline gold‑CV** | Train trên gold lâm sàng (ít), eval trên gold | gold→gold (circular‑an toàn nhưng quá ít data) | **0.19** | Quá ít nhãn lâm sàng → trần thấp |
| 2 | **Weak‑sup augment (within‑LLM)** | Làm giàu lên ~10k post **nhãn‑LLM**, train+eval trên LLM | within‑LLM (**circular**) | **0.67** | Cao nhưng *tự đánh lừa* — chỉ để lộ tính circular |
| 3 | **Gold‑holdout (trung thực)** | Train trên nhãn‑LLM, **eval trên gold lâm sàng held‑out** | cross‑to‑gold (honest) | **0.3569** | Con số trung thực đầu tiên |
| 4 | **+ Behavior rebalance (Run B)** | WeightedRandomSampler nghịch‑tần (`R2_BALANCE`) | gold‑holdout | **0.3849** | QWK 0.378→0.398, MAE 0.840→0.822 (đều tốt hơn) |
| 5 | **Within‑dist CV sạch (Run A)** | 5‑fold CV trên đủ **10,072** mẫu (sửa bug mount) | within‑distribution (như paper) | **0.6530** ±0.0048 | **VƯỢT PAPER 0.5098 (+28%)** |
| 6 | **Ablation flat‑CE** | Bỏ CORAL+Focal, chỉ CE thuần | gold‑holdout | **0.4215** ±0.024 | **Bất ngờ: > dual‑head; cứu Behavior 0.183→0.285** |

**Bảng 3 giao thức (đóng gói cho paper):**

| Giao thức | Train | Eval | Macro‑F1 | QWK |
|---|:--:|:--:|:--:|:--:|
| Gold‑CV | gold | gold | 0.19 | 0.24 |
| Within‑LLM *(circular — chỉ để lộ vấn đề)* | LLM | LLM | 0.67 | — |
| **Cross‑to‑gold (của ta)** | LLM | gold | **0.385** | **0.378** |

**Per‑class gold (Run B):** Indicator 0.50 · Ideation 0.48 · **Behavior 0.18 ⚠** · Attempt 0.37.

### B1.2 Phát hiện quan trọng
1. **Vượt paper trên within‑distribution** (0.653 > 0.510) — đóng khung là *"method vượt số báo cáo của paper trên giao thức within‑distribution tương đương"* (trên 10k đã làm giàu của ta, không phải benchmark gated gốc).
2. **flat‑CE > tri‑objective trên gold** (+0.037) và **cứu lớp Behavior** → gợi ý CORAL+Focal đang **overfit phân bố nhãn‑LLM**. ⚠ mới 1 seed/1 run — cần xác nhận CORAL‑only + lặp seed.
3. **Nút thắt Behavior là CHẤT LƯỢNG NHÃN, không phải sampling** — chỉ 634 mẫu Behavior, đa số là nhãn‑LLM nhiễu/under‑label. Rebalance không phá được trần này.

### B1.3 Hai vòng nghiên cứu hỗ trợ paper
- **Vòng "finetuning‑methods" (2026‑06‑25):** phân tích **12 paper nổi tiếng (42–53)** qua 4 nhóm (PEFT · weak‑sup/distill · ordinal/imbalance · MH‑SOTA), mỗi paper kết bằng *"Apply to R2 + Kaggle experiment"*. **Kết luận:** vì nút thắt là *nhãn*, các method **label‑centric** (45 Snorkel, 46 Confident‑Learning/cleanlab, 47 Distillation) xếp hạng **cao hơn** mấy tinh chỉnh imbalance/PEFT → roadmap 3‑tier. Report: `docs/reports/r2-finetuning-methods.html`.
- **Vòng "emotional‑tone" (positive↔negative):** **16 paper**, top‑4 chấm điểm overlap (54 VADEC 38% · 55 CLPsych‑2025 54% · 56 MentaLLaMA 42% · 57 Mitsios 35%). Dataset **IMHI ✅ tải về** (19,051 hàng test, MIT); CLPsych ⛔ gated.

### B1.4 Còn thiếu để IEEE duyệt (ưu tiên giảm dần)
🔴 **(1)** Định lượng chất lượng nhãn‑LLM = **Cohen's κ** + confusion LLM‑vs‑gold (giải thích "gap 0.28").
🔴 **(2)** **Bảng ablation** đầy đủ: flat‑CE vs **CORAL‑only** vs dual‑head; ±augment; ±balance; ±focal.
🟡 **(3)** Baselines (plain‑RoBERTa‑CE, BiLSTM‑MTL). 🟡 **(4)** Vá Behavior. 🟡 **(5)** Ethics & provenance scrape.

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

### B2.2 Còn thiếu
🔴 Quyền **MSP‑Podcast** (nhãn V/A/D thật) — latency ngoài tầm kiểm soát, xin trước.
🔴 Chạy **MTL‑heads (M3–M5)** lấy số 10‑fold. CCC affect head trên nhãn thật. Ablation (Kendall vs GradNorm/PCGrad). Baseline eGeMAPS SER.

---

## PHẦN C — Thu thập dữ liệu & xin quyền sử dụng (DUA / EULA)

Đây là **đường tới‑hạn thật sự** của thesis: nhiều dataset lâm sàng bị *gated*, latency xin quyền **1–4 tuần** nằm ngoài tầm kiểm soát → phải khởi động sớm.

**Chiến lược 2 nhánh (license là bộ lọc cứng):**

| Nhánh | Nguồn được phép | Vì sao |
|---|---|---|
| **Model triển khai (deployed)** | **CHỈ** CSSRS‑Reddit (CC‑BY‑4.0) | License duy nhất cho phép *serve* model đã train |
| **Nghiên cứu / paper** | CSSRS‑Reddit **+** DAIC‑WOZ **+** SMHD/RSDD | DUA research‑only: cho train + eval, **KHÔNG** cho deploy |

> ⚠️ Bất cứ checkpoint nào train trên **DAIC‑WOZ / SMHD/RSDD KHÔNG được ship** trong sản phẩm — chỉ dùng cho nhánh nghiên cứu.

**Trạng thái từng dataset:**

| Dataset | Vai trò trong thesis | License / cổng | Trạng thái |
|---|---|---|---|
| **CSSRS‑Reddit** (Gaur, WWW'19) | gold C‑SSRS 5 mức, 500 user, 4 bác sĩ tâm thần — nguồn crisis **serve được** | CC‑BY‑4.0 (mở) | ✅ **Đã tải** |
| **DAIC‑WOZ** (USC ICT) | transcript phỏng vấn lâm sàng + **PHQ‑8 depression**, hội thoại (gần domain Pebble hơn Reddit) → nhãn **crisis cho voice head** | Research‑only **EULA**, email học thuật | ⚠️ **ACTION REQUIRED — chưa bắt đầu** |
| **SMHD / RSDD** (Georgetown) | nhãn chẩn đoán (9 bệnh / depression) → **corpus domain‑adaptive pretrain** | Research‑only **DUA** | ⚠️ chưa bắt đầu (~2–4 tuần) |
| **MSP‑Podcast** | nhãn **A/V/D thật** cho affect head (voice) | gated | 🔴 cần xin |
| **IMHI** | OOD eval cho safety head (swmh / t‑sid) | MIT | ✅ đã tải (19,051 hàng) |
| **CLPsych UMD Suicidality** | (đã cân nhắc) | bắt **xoá data + model** sau workshop | ❌ loại — không tương thích giữ/serve |

**DAIC‑WOZ — các bước cần làm (bạn phải ký):**
1. Vào cổng <https://dcapswoz.ict.usc.edu/>, tải **EULA** (`Extended-DAIC-BLANK_EULA.pdf`).
2. Điền thông tin tổ chức (PI/lab), **ký**, gửi từ **email học thuật** (`@institution.edu`).
3. Turnaround **~1–3 tuần**. Cover‑note đã soạn sẵn trong `docs/dataset-acquisition-plan.md` (chỉ điền các trường `[BRACKETED]`).

---

## PHẦN D — Hạ tầng & bài học vận hành (carry‑forward)

- **Kaggle:** auth qua `~/.kaggle/access_token` (token `KGAT_`, KHÔNG phải kaggle.json). Account hiện hành **`phatneurondai`** (đã **phone‑verify** → GPU P100 + Internet chạy được; account chưa verify → kernel chết ở pip install). **Tối đa 2 GPU session đồng thời**, quota tuần ≈ 30h P100.
- **Stack pin bắt buộc:** `torch==2.5.1+cu121` (P100 = sm_60; base‑image torch 2.10 không tương thích).
- **Bug mount đã sửa:** dataset mount sâu 3 cấp → phải dùng recursive glob `**/sequences.csv` (trước đó rơi nhầm về Zenodo‑392 → số CV vô hiệu).
- **Code đã env‑gate:** trọng số loss (`R2_W_CORAL/CE/FOCAL`, `R2_FOCAL_GAMMA`), rebalance (`R2_BALANCE`), gold‑holdout (`R2_GOLD_HOLDOUT`); `evaluate` chỉ blend head được train (ablation hợp lệ); `train_fold` có hook `sample_weight=` cho cleanlab.
- ⚠ **Không commit** `kaggle/**/out/best_model.pt` (~595 MB/file).

---

## PHẦN E — Trạng thái & việc tiếp theo

| # | Việc | Stream | Vì sao |
|---|---|---|---|
| 🔴 1 | Đo **Cohen's κ** nhãn‑LLM ↔ gold trên tập overlap | Text | Mở khoá đóng góp #3; latency ngoài tầm kiểm soát |
| 🔴 2 | **Ký EULA DAIC‑WOZ** + xin **MSP‑Podcast / SMHD** (định fallback) | Voice | Latency xin quyền 1–4 tuần; chặn affect/crisis head |
| 🟡 3 | Chạy **CORAL‑only ablation** + **cleanlab diagnostic** trên Kaggle | Text | Hoàn thiện bảng ablation §4 + đo nhiễu nhãn Behavior |
| 🟡 4 | Chạy **MTL‑heads (M3–M5)** lấy 10‑fold | Voice | Trong tầm kiểm soát; chạy song song khi chờ data |

**Rủi ro then chốt:** cả 2 việc tới‑hạn là **thu thập dữ liệu/nhãn**, không phải code → phải khởi động trước vì latency ngoài tầm kiểm soát.

---

### Nguồn tham chiếu
`pebble-finetuning-strategy-v3.md` · `progress.md` · `docs/phases/` · `docs/reports/{PROJECT-WORK-REPORT, r2-ab-results, r2-finetuning-methods}.*` · `docs/tasks/{r2-beat-paper-dual-report, r2-finetuning-methods-for-ieee, emotional-tone-papers, SESSION-HANDOFF-2026-06-26}.md` · `docs/dataset-acquisition-plan.md` · `docs/papers/finetuning-message/PAPER-PLAN-text-ordinal-suicide.md` · `docs/papers/voice/PAPER-PLAN-voice-crisis-affect.md`
</content>
</invoke>
