# Ngoài MLM — 2 hướng fine-tuning để đo cảm xúc: SupCon vs. Distillation

> **Bối cảnh.** Tài liệu này deep-dive 2 phương án thay cho bước MLM trong pipeline text của Pebble,
> rồi **so sánh** và **chọn solution phù hợp**. Đọc kèm [`giai-thich-finetuning-vi.md`](./giai-thich-finetuning-vi.md)
> (pipeline + kết quả ablation MLM hiện tại).
>
> **Phạm vi:** chỉ 2 hướng người dùng yêu cầu giữ lại:
> 1. **Supervised Contrastive Learning (SupCon)** — thay bước "khởi động encoder" (đúng chỗ MLM đang đứng).
> 3. **Soft-label Distillation từ LLM teacher** — thay/bổ sung cho tín hiệu huấn luyện (đúng kiểu Emo Pillars).
>
> Biên soạn: 2026-06-19. Mọi con số đều kèm nguồn (arXiv / venue / năm).

---

## 0. Nhắc lại vấn đề — vì sao tìm cách thay MLM

Pipeline hiện tại: **NeoBERT (250M)** + 2 head trên vector `[CLS]` — Emotion head (28 lớp GoEmotions,
CrossEntropy) và Severity head (hồi quy 0–1, MSE trên EI-reg). Dữ liệu **nhỏ (~5K)**. Thứ tự ưu tiên:
**severity (tương quan/MAE) và calibration (ECE) > vài điểm macro-F1 emotion**.

Ablation 3-seed đã kết luận MLM **không đáng**:

| Chỉ số | delta MLM-on − off | Diễn giải |
|---|---|---|
| emo_macroF1 | **+0.0127** | lợi nhỏ |
| sev_pearson | **−0.0454** | **hại** severity |
| sev_spearman | **−0.0415** | **hại** severity |
| emo_ece | **+0.0517** | **hại** calibration (~+48%) |

**Cơ chế hỏng của MLM:** corpus MLM (Reddit + tweet) nghiêng về tín hiệu *phân loại cảm xúc*, kéo
encoder lệch khỏi tín hiệu *cường độ* (severity) và làm logit-scale trôi → calibration tệ đi. Đây là
tiêu chí để chấm 2 phương án thay thế: **đừng hy sinh severity & calibration**.

> **Điểm cốt lõi cần phân biệt:** SupCon và Distillation **không cùng một trục** — chúng thay 2 thứ
> khác nhau, nên *có thể kết hợp*:
> - **SupCon** = thay cách **định hình hình học không gian biểu diễn của encoder** (đối thủ trực tiếp của MLM).
> - **Distillation** = thay **nguồn tín hiệu/nhãn huấn luyện** (soft labels từ teacher thay vì nhãn cứng).

---

## 1. Phương án 1 — Supervised Contrastive Learning (SupCon)

### 1.1. Ý tưởng & công thức

SupCon kéo các câu **cùng cảm xúc** lại gần và đẩy câu **khác cảm xúc** ra xa trong không gian
embedding. Khác MLM (học đoán từ bị che), SupCon học **trực tiếp cấu trúc cảm xúc**.

- **Gốc — Khosla et al. 2020 (NeurIPS), [arXiv:2004.11362](https://arxiv.org/abs/2004.11362).** Mở rộng
  InfoNCE sang có giám sát: mọi mẫu cùng lớp trong batch là "positive".

  ```
  L_SupCon = Σ_i (−1/|P(i)|) Σ_{p∈P(i)} log( exp(z_i·z_p/τ) / Σ_{a∈A(i)} exp(z_i·z_a/τ) )
  ```
  `P(i)` = các mẫu cùng lớp trong batch; `z` = embedding đã chuẩn hoá L2; `τ` = temperature (≈0.1).

- **Công thức áp dụng cho PLM — Gunel et al. 2021 (ICLR), [OpenReview cu7IUiOhujH](https://openreview.net/forum?id=cu7IUiOhujH).**
  Huấn luyện **đồng thời** CE + SupCon trên `[CLS]`:

  ```
  L = (1 − λ)·L_CE + λ·L_SupCon       với λ ∈ {0.1–0.5}, τ ∈ {0.07–0.1}
  ```
  **Phát hiện quan trọng nhất cho Pebble:** SupCon **lợi nhất đúng ở chế độ ít dữ liệu / few-shot** —
  khớp với tập ~5K của Pebble. Cũng tăng độ bền với nhãn nhiễu.

### 1.2. Bằng chứng trên bài toán emotion / mất cân bằng

| Paper | Venue | Kết quả |
|---|---|---|
| **BERTEmo** — Shah et al. ([arXiv:2310.18930](https://arxiv.org/abs/2310.18930)) | EMNLP 2023 | retrofit PLM bằng contrastive emotion, **~+1% F1**, lợi lớn hơn ở few-shot; **giữ nguyên kiến thức ngôn ngữ** (không phá như MLM) |
| **SSLCL** — Shi et al. ([arXiv:2310.16676](https://arxiv.org/abs/2310.16676)) | EMNLP 2023 | chiếu nhãn → embedding, contrast mẫu với "prototype nhãn" → **chạy được ở batch nhỏ 32–64**; SOTA trên IEMOCAP/MELD |
| **Label-SupCon imbalanced text** ([ACL WNUT 2024](https://aclanthology.org/2024.wnut-1.6/)) | WNUT 2024 | dùng nhãn làm anchor → **+11% F1** trên text mất cân bằng |

### 1.3. Vấn đề khó — severity là HỒI QUY, SupCon vốn cho phân loại

SupCon chỉ định nghĩa được "positive/negative" trên **nhãn rời rạc**. Severity của Pebble là số liên
tục → cần biến thể contrastive-cho-regression:

- **Rank-N-Contrast (RnC)** — Zha et al. 2023, **NeurIPS Spotlight**, [arXiv:2210.01189](https://arxiv.org/abs/2210.01189).
  Sắp các mẫu theo khoảng cách nhãn `|y_i − y_j|`; ép thứ tự trong không gian embedding khớp thứ tự
  trong không gian nhãn. **Giảm 5.8–11.7% sai số** so với baseline hồi quy. **Cảnh báo: chỉ thử trên
  ảnh, CHƯA có ứng dụng text nào** → áp cho text là *vùng mới* (cơ hội đóng góp, nhưng cũng là rủi ro).
- **EmotionRankCLAP** ([arXiv:2505.23732](https://arxiv.org/abs/2505.23732), 2025) — RnC cho cường độ
  cảm xúc trên *speech* (Kendall τ 0.55–0.62). Bằng chứng RnC mở rộng được sang affect, nhưng đa mô thức.

### 1.4. Công thức đa nhiệm đề xuất (nếu chọn SupCon)

```
L = α·CE(emotion) + β·MSE(severity) + λ·SupCon(emotion) + γ·RnC(severity)
   khởi điểm: α=1, β=1, λ=0.1, γ=0.1, τ=0.1
```
SupCon định hình cụm theo cảm xúc; RnC giữ thứ tự theo severity — **cùng chia sẻ một `[CLS]`**.
Tổ hợp này **chưa từng có trong literature** → là novelty của Pebble (đồng thời là rủi ro chưa kiểm chứng).

### 1.5. Rủi ro & chi phí của SupCon

1. **Đòi batch lớn (rủi ro số 1).** SupCon chuẩn cần 2.048–6.144 mẫu/batch để đủ positive. Với 5K mẫu
   và 28 lớp, lớp hiếm (pride, relief…) có thể **0 positive trong batch 64** → gradient triệt tiêu đúng
   chỗ macro-F1 cần. → **Bắt buộc dùng SSLCL** (label-embedding) để né.
2. **Sụp đổ phương sai trong lớp (class collapse).** Kéo các mẫu cùng cảm xúc quá sát → mất biến thiên
   nội lớp. Hai câu "sad" có severity 0.2 vs 0.9 bị ép giống nhau → **hại severity Pearson**. Đây là
   xung đột đa nhiệm cốt lõi; phải cân RnC để chống lại.
3. **Calibration: KHÔNG có bằng chứng NLP trực tiếp.** Không tìm thấy paper nào đo ECE của SupCon trên
   text-BERT. *Lập luận cơ chế:* SupCon nắn hình học biểu diễn, **không** đẩy tham số về mục tiêu đoán
   token như MLM → *có khả năng* ít hại calibration hơn MLM, nhưng **chưa ai chứng minh** → Pebble đo
   được sẽ là phát hiện mới.
4. **Nhạy temperature** (`τ<0.05` dễ nổ gradient; `τ` quá cao → mất tín hiệu).

---

## 2. Phương án 3 — Soft-label Distillation từ LLM teacher

### 2.1. Nền tảng & vì sao hợp dữ liệu nhỏ

- **Hinton et al. 2015, [arXiv:1503.02531](https://arxiv.org/abs/1503.02531).** Học từ "soft target"
  của teacher ở nhiệt độ T:
  ```
  L = α·CE(nhãn cứng, σ(z_s)) + β·T²·KL( σ_T(z_t) ‖ σ_T(z_s) )    (thường β ≫ α)
  ```
  **"Dark knowledge":** phân phối mềm cho biết teacher thấy "joy" giống "excitement" hơn "anger" —
  thông tin mà nhãn cứng vứt đi. **Mỗi ví dụ mềm tải ~log₂(28)≈4.8 bit thay vì 1 bit** → với tập 5K
  của Pebble, đây là cấp số nhân thông tin **không tốn thêm công gán nhãn**.

### 2.2. Emo Pillars — và chỗ Pebble nên làm KHÁC

**Emo Pillars (Shvets, Findings ACL 2025, [arXiv:2504.16856](https://arxiv.org/abs/2504.16856))** —
đã có trong repo (`docs/papers/04-emo-pillars.md`). Đạt **GoEmotions macro-F1 = 0.55**, ISEAR 0.75,
IEMOCAP-4 0.83 từ dữ liệu tổng hợp.

> **Làm rõ một hiểu nhầm phổ biến:** Emo Pillars **KHÔNG** làm soft-label KL distillation thật. Mistral
> sinh điểm 0.0–1.0/lớp, nhưng họ **cắt ngưỡng ≥0.3 → nhãn cứng** rồi train **BCE**. Tức là vứt bỏ
> gradient nội lớp ("joy=0.7" và "joy=0.9" thành như nhau). Họ **bù bằng 400K ví dụ tổng hợp** — Pebble
> không có xa xỉ đó.

→ **Cơ hội nâng cấp của Pebble:** giữ **nguyên phân phối điểm mềm của Gemini** làm target (soft-BCE/KL),
không cắt ngưỡng. Đúng một dòng code:
`BCEWithLogitsLoss(logit, gemini_score)` thay vì `BCEWithLogitsLoss(logit, (gemini_score≥0.3).float())`.

### 2.3. Soft > hard cho calibration — bằng chứng định lượng

| Paper | Venue | Số liệu |
|---|---|---|
| Müller, Kornblith, Hinton ([arXiv:1906.02629](https://arxiv.org/abs/1906.02629)) | NeurIPS 2019 | label smoothing (≈soft đều) **cải thiện ECE**. *Lưu ý "teacher penalty":* teacher train bằng LS lại distill kém đi |
| Collins, Bhatt, Weller ([arXiv:2207.00810](https://arxiv.org/abs/2207.00810)) | AAAI HCOMP 2022 | soft-label: **−32% KL** so với phân phối người, **+61% tương quan entropy** |
| Soft-Label Preserves Uncertainty ([arXiv:2511.14117](https://arxiv.org/abs/2511.14117)) | 2025 | xác nhận lại 32% / 61% trên cả NLP |
| Fornaciari et al. ([ACL 2021.naacl-main.204](https://aclanthology.org/2021.naacl-main.204/)) | NAACL 2021 | soft-label MTL giảm overfit nhãn đa số → calibration tốt hơn |

→ Đây **đánh trúng** ưu tiên số 1 của Pebble (ECE). MLM làm ECE *tệ hơn*; soft-label làm ECE *tốt hơn*.

### 2.4. Distill cho head HỒI QUY (severity) — chính chỗ Pebble cần

- **FlexGuard** (Ding et al., [arXiv:2602.23636](https://arxiv.org/abs/2602.23636), 2026) — **paper duy
  nhất** distill điểm rủi ro **liên tục** (0–100) từ LLM judge vào model nhỏ. Bài học:
  1. **Calibrate điểm thô của LLM** cho đơn điệu với nhãn gốc (isotonic / rescale) trước khi train.
  2. Dùng **sai số tuyến tính/Huber** thay MSE thuần ở bối cảnh an toàn.
  3. Báo cáo **Spearman ρ** (đạt 0.828) — hợp severity thứ bậc hơn Pearson.
- **Khoảng trống literature:** chưa paper nào distill *đồng thời* head phân loại (28 cảm xúc) + head
  hồi quy (severity) từ một teacher. Emo Pillars có (phân loại), FlexGuard có (hồi quy) — **ghép lại là
  đóng góp mới của Pebble.**

### 2.5. Rủi ro — teacher bias là rủi ro số 1

| Paper | Cảnh báo |
|---|---|
| LLM Label Bias ([ACL 2024.naacl-long.378](https://aclanthology.org/2024.naacl-long.378.pdf), NAACL 2024) | model RLHF (như Gemini) **over-predict** nhãn an toàn/cảm xúc mạnh → severity head sẽ **lệch cao** |
| LLMs overconfident ([arXiv:2505.02151](https://arxiv.org/abs/2505.02151), 2025) | teacher lớn **quá tự tin** ở ngữ cảnh mơ hồ → nén phân phối student → ECE xấu |
| Teacher Calibration in KD ([arXiv:2508.20224](https://arxiv.org/abs/2508.20224), 2025) | teacher lệch calibration → student kém hơn → **calibrate teacher TRƯỚC khi distill** |
| SiDyP ([arXiv:2505.19675](https://arxiv.org/abs/2505.19675), KDD 2025) | khử nhiễu nhãn LLM lặp lại → **+7–8% acc**, không cần gọi lại teacher |

**Hệ quả thực hành:** Gemini sẽ thổi phồng severity. **Bắt buộc** audit điểm Gemini so với 500 nhãn
người (Protocol A), chỉnh isotonic *trước* khi train head severity — đừng train thẳng trên float thô.

---

## 3. So sánh trực diện

| Tiêu chí | **SupCon (P.án 1)** | **Distillation (P.án 3)** |
|---|---|---|
| **Thay cái gì** | hình học encoder (đối thủ trực tiếp của MLM) | nguồn tín hiệu/nhãn huấn luyện |
| **Đánh trúng ưu tiên Pebble?** | macro-F1 lớp hiếm ✅; severity ⚠️ (nguy cơ class-collapse); calibration ❓ chưa rõ | **calibration ✅✅** (có số liệu); severity ✅ (FlexGuard); F1 ✅ |
| **Hợp dữ liệu nhỏ ~5K?** | ✅ lợi nhất ở few-shot (Gunel) | ✅✅ soft-label = cấp số nhân thông tin/ví dụ |
| **Xử lý severity (hồi quy)** | cần RnC — **chưa ai làm trên text** (rủi ro cao) | FlexGuard có precedent + isotonic calibrate |
| **Tác động calibration** | ❓ chưa có bằng chứng NLP; *lập luận* trung tính | ✅ bằng chứng định lượng (−32% KL, +61% entropy) |
| **Chi phí hạ tầng** | rẻ; nhưng cần SSLCL để né batch lớn | **tốn token Gemini** sinh soft label (1 call/ví dụ) |
| **Độ phức tạp triển khai** | trung bình (loss mới + SSLCL + RnC) | thấp–trung bình (đổi target sang soft + isotonic) |
| **Rủi ro chính** | class-collapse hại severity; batch nhỏ; calibration chưa rõ | **teacher bias** (Gemini thổi severity); nhiễu silver |
| **Mức kiểm chứng** | nhiều mảnh, nhưng tổ hợp emotion-SupCon + RnC là mới | precedent gần (Emo Pillars + FlexGuard); ghép 2 head là mới |
| **Tính novelty (cho paper)** | cao (RnC-on-text) nhưng rủi ro | cao + an toàn hơn (joint distill class+reg) |

**Đọc bảng:** hai phương án **không loại trừ nhau**. SupCon là "cách nắn encoder", Distillation là
"cách cấp nhãn". Nhưng nếu **phải chọn một để bám sát ưu tiên của Pebble (severity + calibration)**,
Distillation thắng rõ: nó có **bằng chứng định lượng cải thiện calibration**, có precedent cho head hồi
quy, và rủi ro lớn nhất của nó (teacher bias) có cách sửa rẻ & xác định (isotonic trên 500 nhãn người).
SupCon có một rủi ro chưa kiểm chứng đúng vào chỗ Pebble quan tâm nhất (class-collapse hại severity,
calibration chưa ai đo).

---

## 4. Solution phù hợp cho Pebble

### 4.1. Khuyến nghị: **Distillation là trục chính, SupCon là arm phụ có kiểm soát**

**Bước A — Distillation làm recipe chính (đánh trúng calibration + severity):**

```
1. Gemini sinh 1 structured output/ví dụ: { emotion_scores: {28 lớp: 0–1}, severity: 0–1 }.
2. Calibrate severity Gemini bằng isotonic regression trên 500 nhãn người (Protocol A)  ← chống teacher-bias.
3. L_emo = soft-BCE(student_logits, gemini_scores)          ← GIỮ phân phối mềm, KHÔNG cắt ngưỡng 0.3.
4. L_sev = Huber(student_severity, severity_đã_calibrate)   ← robust hơn MSE thuần.
5. L = uncertainty-weight(L_emo, L_sev) (Kendall) ; sàn trọng số safety để không bị nén dưới recall 0.95.
6. Sau train: temperature scaling (Guo 2017) trên val để dọn nốt overconfidence.
```

Vì sao hợp Pebble: trực tiếp hạ ECE (ưu tiên #1), có precedent cho severity (FlexGuard), sửa được rủi
ro teacher-bias bằng dữ liệu đã có. Đây cũng là contribution mà `related-work-methods.md` đã xác định
(joint distill regression + classification từ Gemini teacher).

**Bước B — SupCon làm arm đối chứng, thay đúng chỗ MLM:**

- Dùng **SSLCL** (label-embedding, [arXiv:2310.16676](https://arxiv.org/abs/2310.16676)) để chạy được
  ở batch 32–64 — **không** dùng SupCon chuẩn (đòi batch lớn).
- Thêm `λ·SupCon(emotion)` vào loss; **chỉ trên head emotion**. Để bảo vệ severity, hoặc (a) **không**
  đưa severity vào contrastive, hoặc (b) thêm `γ·RnC(severity)` và *đo* xem có hại severity không.
- Bắt buộc **đo ECE và sev_pearson** — đây là điều MLM đã thất bại; SupCon phải chứng minh không lặp lại.

### 4.2. Thiết kế thí nghiệm — bám đúng phương pháp 3-seed/paired-delta đang có

Tái dùng đúng khung ablation hiện tại (`SEEDS=[13,42,1337]`, paired delta, `results_summary.csv`),
chỉ thêm các **arm** mới so với baseline `MLM-off`:

| Arm | Mô tả | Câu hỏi nó trả lời |
|---|---|---|
| **Baseline** | `MLM-off` hiện tại (hard label, CE+MSE) | mốc so |
| **Distill-soft** | thay target bằng soft Gemini + isotonic severity | soft-label có hạ ECE & giữ severity không? |
| **SupCon (SSLCL)** | baseline + `λ·SupCon(emotion)` | SupCon có hơn MLM ở chỗ MLM thua không? |
| **SupCon+RnC** | thêm `γ·RnC(severity)` | RnC có cứu severity khỏi class-collapse không? |
| **Distill+SupCon** | gộp A + B | hai trục có cộng hưởng không? |

**Tiêu chí thành công (giữ nguyên hướng tốt/xấu của repo):**
- `emo_ece` **giảm** so với baseline (đây là chỗ MLM làm hỏng).
- `sev_pearson`/`sev_spearman` **không giảm** (≥ baseline), `sev_mae` không tăng.
- `emo_macroF1` ≥ baseline.
- Đánh giá qua **paired delta trên cùng seed** (đúng như ablation MLM) để khử nhiễu seed.

### 4.3. Thứ tự thực thi đề xuất

1. **Distill-soft trước** — rẻ, một thay đổi target + isotonic, đánh trúng calibration. Nếu ECE giảm &
   severity giữ → đã có cải thiện thật để ship.
2. **SupCon (SSLCL) song song** — trả lời đúng câu hỏi gốc "có cách nắn encoder tốt hơn MLM không"
   bằng số đo, không lặp lại lỗi calibration của MLM.
3. **Gộp** chỉ khi cả hai arm đơn lẻ đều không hại severity/ECE.

---

## 5. Bài báo uy tín bổ sung (IEEE & venue hạng A)

> Bổ sung các nguồn ở **venue uy tín cao**, ưu tiên IEEE (đặc biệt *IEEE Transactions on Affective
> Computing* — tạp chí hàng đầu về cảm xúc), kèm TPAMI / Proceedings of the IEEE / IEEE J-BHI / IEEE
> Access và các hội nghị hạng A (ACL/EMNLP/NAACL/KDD/CIKM). Tất cả đã verify DOI; bài sau paywall được
> đánh dấu (chỉ xác nhận qua abstract). Các bài đã nêu ở §1–§2 không lặp lại.

### 5.1. Hướng SupCon / Contrastive

| Paper | Venue (uy tín) | Số liệu / điểm chính | Liên quan Pebble |
|---|---|---|---|
| **HyCon** — Mai et al. | **IEEE TAC** 2023, [10.1109/TAFFC.2022.3172360](https://doi.org/10.1109/TAFFC.2022.3172360) *(paywall)* | hybrid + semi-contrastive + pair-selection; lợi khi dữ liệu ít | template IEEE-TAC cho contrastive trên head emotion ở chế độ ít dữ liệu/mất cân bằng |
| **COLD Fusion** — Tellamekala et al. | **IEEE TPAMI** 2024, [10.1109/TPAMI.2023.3325770](https://doi.org/10.1109/TPAMI.2023.3325770) · [arXiv:2206.05833](https://arxiv.org/abs/2206.05833) | ràng buộc **calibration** + **ordinal ranking** đồng thời cho emotion (cả classification & regression) | **prior-art IEEE mạnh nhất** cho thiết kế calibration + severity-ordinal của Pebble |
| **SACL** — Hu et al. | **ACL** 2023, [arXiv:2306.01505](https://arxiv.org/abs/2306.01505) | adversarial + class-spread contrastive; WF1 **69.22 IEMOCAP / 66.45 MELD / 39.65 EmoryNLP** (+1.1% TB); giảm nhầm cặp gần nghĩa | giảm nhầm cặp cảm xúc dễ lẫn của 28 lớp GoEmotions, stack thẳng lên CE |
| **EACL** (emotion-anchored) — Yu et al. | Findings **NAACL** 2024, [arXiv:2403.20289](https://arxiv.org/abs/2403.20289) | dùng label-embedding làm anchor, tách các anchor ra xa | prior hình học tách lớp gần nghĩa; nhẹ tham số, hợp `[CLS]` |
| **LCL** "Not All Negatives Are Equal" — Suresh & Ong | **EMNLP** 2021, [arXiv:2109.05427](https://arxiv.org/abs/2109.05427) | trọng số negative theo độ giống lớp; hơn SupCon/CE; "phân phối đầu ra tách bạch hơn" (ngụ ý lợi calibration) | gốc của dòng "distance-aware contrastive cho emotion" |
| **Ordinal-content-preserving aug.** — Zheng et al. | **ICLR** 2024, [OpenReview kx2XZlmgB1](https://openreview.net/forum?id=kx2XZlmgB1) | augment mạnh **phá tín hiệu thứ bậc** → SupCon thường hỏng trên ordinal regression | giải thích vì sao severity cần RnC (rank-based) chứ không phải SupCon thường |
| **Survey: Textual Emotion Recognition** — Deng & Ren | **IEEE TAC** 2023, [10.1109/TAFFC.2021.3053275](https://doi.org/10.1109/TAFFC.2021.3053275) *(paywall)* | khảo sát + 4 thách thức (thiếu data, ranh giới mờ, thiếu ngữ cảnh, ERC) | citation-anchor IEEE-TAC cho related-work |
| **Survey: Label-Efficient ESA** — Zhao et al. | **Proceedings of the IEEE** 2023, [10.1109/JPROC.2023.3309299](https://doi.org/10.1109/JPROC.2023.3309299) ([PDF](https://ise.thss.tsinghua.edu.cn/mig/2023-2.pdf)) | 7 paradigm học tiết kiệm nhãn (gồm weakly-supervised, low-shot, contrastive) | định vị chiến lược silver-label của Pebble là "weakly-supervised ESA" |

### 5.2. Hướng Distillation / Soft-label

| Paper | Venue (uy tín) | Số liệu / điểm chính | Liên quan Pebble |
|---|---|---|---|
| **Teacher Calibration in KD** — Kim et al. | **IEEE Access** 2025 (open), [10.1109/ACCESS.2025.3585106](https://doi.org/10.1109/ACCESS.2025.3585106) · [arXiv:2508.20224](https://arxiv.org/abs/2508.20224) | lỗi calibration của **teacher** tương quan mạnh với acc student; **temperature-scale teacher trước khi distill** → student tốt hơn | **hành động 1 đoạn:** calibrate điểm Gemini trước khi train → cải thiện cả MAE & ECE student |
| **LLM-Enhanced Multi-Teacher KD** — Zhang et al. | **IEEE J-BHI** 2025, [10.1109/JBHI.2024.3470338](https://doi.org/10.1109/JBHI.2024.3470338) *(paywall)* | LLM-teacher + graph-CNN teacher cho emotion (valence-arousal liên tục) trong healthcare | bằng chứng LLM-teacher distillation cho affect ở venue IEEE y-sinh |
| **3M-Health** — Cabral et al. | **CIKM** 2024, [arXiv:2407.09020](https://arxiv.org/abs/2407.09020) | multi-teacher KD cho mental-health text; macro-F1 **DEPTWEET 46.4 (severity 4 mức)**, **TwitSuicide 62.0** | hệ thống gần Pebble nhất (emotion + mental-health + severity); baseline để vượt |
| **"You Are an Expert Annotator"** — Bagdon et al. | **NAACL** 2024, [arXiv:2403.17612](https://arxiv.org/abs/2403.17612) | LLM gán nhãn **cường độ liên tục** (best-worst-scaling); regressor học từ nhãn LLM ≈ ngang nhãn người | **hợp thức hoá** điểm severity 0–1 do Gemini sinh cho head hồi quy |
| **KD ≈ Label Smoothing: Fact or Fallacy?** — Al Nahian | **EMNLP** 2023, [ACL 2023.emnlp-main.271](https://aclanthology.org/2023.emnlp-main.271) | trong NLP, KD **thừa hưởng overconfidence** của teacher (ngược với label smoothing) | cảnh báo: distill từ Gemini quá tự tin sẽ kéo ECE student xấu → cần calibrate teacher |
| **Model Calibration for Emotion Detection** — Petre-Vlad et al. | Findings **EMNLP** 2025, [ACL 2025.findings-emnlp.1114](https://aclanthology.org/2025.findings-emnlp.1114) | đo **ECE trên GoEmotions** + MixUp/temperature trong vòng distill cải thiện calibration | baseline ECE-trên-GoEmotions duy nhất để Pebble so & vượt |
| **EmoLLMs** — Liu et al. | **KDD** 2024, [arXiv:2401.08508](https://arxiv.org/abs/2401.08508) | LLM instruction-tuned làm **cả classification & regression** affect; gồm GoEmotions; vượt GPT-3.5/4 | teacher mở thay thế/đối chứng Gemini cho head severity/energy |
| **KD in Automated Annotation** — Pangakis & Wolken | NLP+CSS @ **ACL** 2024, [arXiv:2406.17633](https://arxiv.org/abs/2406.17633) | classifier học từ nhãn GPT-4 ≈ học từ nhãn người (14 task) | luận cứ "vì sao dùng nhãn LLM thay nhãn người" |
| **Optimised KD (DistilBERT/ALBERT)** — Hussain et al. | Scientific Reports 2025, [10.1038/s41598-025-16001-9](https://doi.org/10.1038/s41598-025-16001-9) | hybrid **focal + KL** loss; student giảm 40% size, <1–6% acc | focal+KL thay BCE thuần khi lớp mất cân bằng nặng |

### 5.3. 3 bài nên đọc đầu tiên (đã verify, đúng ưu tiên Pebble)

1. **COLD Fusion (IEEE TPAMI 2024)** — prior-art IEEE uy tín nhất ghép *calibration + ordinal regression*
   cho cảm xúc → đúng bài toán severity + ECE của Pebble.
2. **Teacher Calibration in KD (IEEE Access 2025)** — can thiệp rẻ, một đoạn: calibrate Gemini trước khi
   distill; trực tiếp đỡ rủi ro "teacher thổi phồng severity" đã nêu ở §2.5.
3. **"You Are an Expert Annotator" (NAACL 2024)** — bằng chứng nhãn **cường độ liên tục** do LLM sinh ≈
   nhãn người → hợp thức hoá severity-from-Gemini, mắt xích then chốt của hướng Distillation.

> Có thể giao tiếp `/analysis-paper` để chấm % overlap chi tiết cho từng bài (COLD Fusion, SACL,
> 3M-Health, Teacher-Calibration, "Expert Annotator" là các ứng viên nên chấm trước).

---

## 6. Tóm tắt một dòng

> **Distillation soft-label (giữ phân phối Gemini + calibrate severity bằng isotonic) là solution phù
> hợp nhất** vì nó đánh trúng đúng 2 thứ MLM làm hỏng — calibration và severity — và có bằng chứng định
> lượng (−32% KL, ρ=0.828). **SupCon (qua SSLCL) là phương án thay-MLM hợp lý nhất ở tầng encoder**,
> nhưng phải kèm RnC + đo ECE/severity để không tái phạm lỗi của MLM. Hai trục bổ sung nhau; chạy thành
> các arm trong đúng khung ablation 3-seed/paired-delta hiện có.

---

## Phụ lục — Nguồn chính

**SupCon:**
[Khosla 2020 NeurIPS](https://arxiv.org/abs/2004.11362) ·
[Gunel 2021 ICLR](https://openreview.net/forum?id=cu7IUiOhujH) ·
[BERTEmo EMNLP 2023](https://arxiv.org/abs/2310.18930) ·
[SSLCL EMNLP 2023](https://arxiv.org/abs/2310.16676) ·
[Label-SupCon WNUT 2024](https://aclanthology.org/2024.wnut-1.6/) ·
[Rank-N-Contrast NeurIPS 2023](https://arxiv.org/abs/2210.01189) ·
[EmotionRankCLAP 2025](https://arxiv.org/abs/2505.23732)

**Distillation:**
[Hinton 2015](https://arxiv.org/abs/1503.02531) ·
[Emo Pillars ACL 2025](https://arxiv.org/abs/2504.16856) ·
[Müller 2019 NeurIPS](https://arxiv.org/abs/1906.02629) ·
[Collins 2022 HCOMP](https://arxiv.org/abs/2207.00810) ·
[Soft-Label Uncertainty 2025](https://arxiv.org/abs/2511.14117) ·
[FlexGuard 2026](https://arxiv.org/abs/2602.23636) ·
[LLM Label Bias NAACL 2024](https://aclanthology.org/2024.naacl-long.378.pdf) ·
[Teacher Calibration in KD 2025](https://arxiv.org/abs/2508.20224) ·
[SiDyP KDD 2025](https://arxiv.org/abs/2505.19675) ·
[PGKD EMNLP 2024](https://arxiv.org/abs/2411.05045)
