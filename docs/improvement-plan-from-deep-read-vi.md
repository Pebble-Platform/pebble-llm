# Kế hoạch cải tiến — những gì bằng chứng từ deep-read thay đổi trong Pebble

> **Đầu vào:** các bản deep-read toàn văn PDF của paper 01–23 và bản tổng hợp chéo
> [`papers/SYNTHESIS-deep-read.md`](./papers/SYNTHESIS-deep-read.md).
> **So sánh với:** quy trình hiện tại — [`../pebble-finetuning-strategy-v3.md`](../pebble-finetuning-strategy-v3.md),
> [`phases.md`](./phases.md), [`decisions.md`](./decisions.md), và mã nguồn thực tế
> (`src/pebble_llm/models/losses.py`, `models/heads.py`, `evaluation/metrics.py`, `training/trainer.py`,
> `data/external.py`).
> **Đầu ra:** các thay đổi cụ thể về phương pháp, dữ liệu, thực nghiệm và đánh giá, mỗi điểm đều truy vết được về một paper.
> Biên soạn 2026-06-16.
>
> *(Bản tiếng Anh: [`improvement-plan-from-deep-read.md`](./improvement-plan-from-deep-read.md). Các thuật ngữ kỹ thuật,
> tên head, đường dẫn file, số hiệu paper và tên metric được giữ nguyên tiếng Anh theo quy ước.)*

Mỗi mục được gắn nhãn **[v1]** (đang áp dụng — theo `decisions.md`: tái sử dụng nhãn từ dataset công khai; chỉ học
`emotion` + `severity`; chưa có safety head) hoặc **[v2]** (hoãn lại — bằng chứng được lưu sẵn cho khi thêm
head safety/C-SSRS).

---

## 0. Tóm tắt điều hành — hiện tại vs bằng chứng vs thay đổi

| QĐ | Lĩnh vực | Quy trình hiện tại | Bằng chứng nói gì | Thay đổi | Giai đoạn |
|----|----------|--------------------|-------------------|----------|:---------:|
| **D-B** | Cân bằng loss đa nhiệm (MTL) | `MultiTaskLoss` = **tổng có trọng số cố định** (score×1+emotion×1+safety×2), Kendall/GradNorm chỉ là TODO | Tổng không trọng số (naive sum) là **đối thủ thực sự** (paper 18 thắng shared task với nó); các phương pháp "có nguyên lý" chưa được kiểm chứng dưới recall floor (11) | Đặt **uniform-sum làm baseline tường minh**; cài Kendall (UW) qua LibMTL làm arm nguyên lý đầu tiên; định khung điểm mới là cân bằng **lệch scale MSE+CE**; đặt sàn (floor) cho trọng số safety | v1 (emo+sev) |
| **D-C** | Sơ đồ nhãn + loss cho severity/safety | `severity` = sigmoid liên tục + **MSE**; metric chỉ có MAE; không xử lý thứ bậc (ordinal) | Lỗi C-SSRS mang tính **thứ bậc/kề nhau (adjacent)** → cần loss nhạy khoảng cách + MAE/QWK/Spearman; các "mốc" không so sánh được giữa các paper | Thêm **loss thứ bậc/nhạy khoảng cách + QWK/Spearman** cho bất kỳ severity *rời rạc hoá* nào và head safety/C-SSRS (v2); chọn **một** sơ đồ ánh xạ C-SSRS | v1 (sev rời rạc) / v2 (safety) |
| **D-D** | Transfer cho hồi quy | một head tuyến tính sigmoid-MSE; **không có Pearson** trong metric; init NeoBERT chung chung | single-linear MSE + **Pearson** là chuẩn; **init khớp affect** nâng hồi quy (+22% tương đối, nhưng phụ thuộc target) | Thêm **Pearson/Spearman** vào `metrics.py`; thêm arm **affect-matched-init**; lát cắt hiệu chỉnh (calibration) ESConv | v1 |
| **D-E** | Fine-tuning theo giai đoạn | đóng băng encoder 2 epoch → mở băng LR thấp (**đóng băng tĩnh**) | **Head-only/đóng băng tĩnh là công thức *tệ nhất* trên dữ liệu nhỏ** (ULMFiT Bảng 7); gradual unfreeze + discriminative LR + STLR, hoặc RecAdam — là các arm cạnh tranh | Thay đóng băng tĩnh bằng **gradual unfreeze + discriminative LR + STLR**; thêm **RecAdam** làm arm thứ hai; đo cả hai trên head hồi quy | v1 |
| **D-F** | MLM thích nghi miền | chỉ pretrain head emotion bằng GoEmotions; **không có bước MLM trong miền** | MLM trong miền có ích (01, 12, 19); công thức hiện đại dùng **masking 30%** (22) | Thêm **bước MLM masking 30%** trước khi fine-tune head **kèm ablation cô lập** (phép đo sạch mà FAIIR chưa từng làm) | v1 |
| **D-A** | Backbone encoder | NeoBERT là chính; ModernBERT chỉ là *ghi chú dự phòng* | Tài liệu **không thể** phân tách NeoBERT/ModernBERT; cả hai chưa được đánh giá trên affect/MH | Nâng ModernBERT từ "ghi chú dự phòng" thành **một arm thực nghiệm đối đầu** (cùng công thức, emotion-F1 + severity-Pearson); kiểm tra license | v1 |
| **D-G** | Ngưỡng / sàn recall / hiệu chỉnh | recall safety ≥0.95 *mục tiêu*; **không có calibration (ECE)**, không tinh chỉnh ngưỡng theo head, không kiểm toán teacher | Các paper C-SSRS không báo cáo điều này → **chính khoảng trống này là đóng góp của Pebble**; các LLM teacher rất khác nhau (Gemini yếu nhất, 16) | Thêm **ECE/đường tin cậy + tinh chỉnh ngưỡng theo head**; kiểm toán teacher gán nhãn *nếu* teacher dạng Gemini quay lại (v2) | v2 (chủ yếu) |
| **D-H** | Dataset / mỏ neo | strategy liệt kê nhiều; ESConv+WASSA đã có; RSD-15K còn treo | **RSD-15K không lấy được (404, đã xác nhận lại)**; ESConv **CC-BY-NC → chỉ dùng cho nhánh nghiên cứu/calibration** | **Bỏ RSD-15K**; thêm `load_esconv()` (UTF-8, gắn cờ NC) làm lát cắt calibration; tái dùng quy trình QC của RSD-15K, không dùng dữ liệu | v1 |

---

## 1. Phương pháp (Methodology)

### 1.1 Cân bằng loss đa nhiệm — điểm mới số 1 (D-B) **[v1]**
**Hiện tại:** `losses.py::MultiTaskLoss` là tổng có trọng số cố định; docstring có nhắc Kendall/GradNorm nhưng chỉ
là TODO chưa cài.
**Bằng chứng:** Paper **18** (hệ reg+classification gần nhất) đã *thắng* shared task chỉ với **tổng MSE không trọng số**
— nên "cân bằng có nguyên lý" không tự nhiên tốt hơn và phải được chứng minh. Quan trọng: 18 cộng **hai loss MSE
cùng scale**; còn Pebble trộn **MSE(severity)+CE(emotion)** lệch scale gradient — chính sự lệch này là lý do chính
đáng để dùng trọng số, và đó là thí nghiệm 18 chưa từng chạy. Paper **11** cảnh báo trong thị giác, trọng số tĩnh
được tinh chỉnh tốt thường ngang ngửa các phương pháp phức tạp, và chế độ recall-floor **chưa được kiểm chứng**.
**Thay đổi:**
1. Thêm **arm baseline uniform-sum (`w=1,1`)** — giả thuyết null trung thực mà 18 thiết lập.
2. Bọc trunk NeoBERT bằng **LibMTL** và thêm arm **Kendall uncertainty-weighting (UW)** trước (theo 06: học
   `s=logσ²`, `exp(−s)·L + s/2`), rồi đến GradNorm/PCGrad/Nash.
3. **Đặt sàn cho trọng số head safety** (cap log-variance) để UW không thể hạ trọng số nó xuống — đúng theo cảnh báo
   của chính paper 06.
4. Báo cáo so sánh theo trình tự static-λ → uniform-sum → UW → GradNorm dưới khung **lệch scale MSE+CE**.

### 1.2 Fine-tuning theo giai đoạn — đừng đóng băng cả encoder (D-E) **[v1]**
**Hiện tại:** strategy §6.1 + `trainer.py` đóng băng encoder ~2 epoch, rồi mở băng ở LR thấp — kiểu đóng băng→mở băng
*tĩnh*.
**Bằng chứng:** Paper **20 (ULMFiT) Bảng 7** cho thấy **fine-tune chỉ head / đóng băng encoder là công thức *tệ nhất*
trên dữ liệu nhỏ** (TREC-6 val error 16.09 so với 5.69 của công thức theo giai đoạn) — mâu thuẫn trực tiếp với kế
hoạch hiện tại. Cách sửa là *gradual* unfreeze + discriminative LR (`η_{l-1}=η_l/2.6`) + STLR. Paper **21 (RecAdam)**
là công thức *cạnh tranh* (anchor-về-init + anneal; +1.7% trên các task <10k mẫu) và **loại trừ lẫn nhau** với gradual
unfreeze (không chồng cả hai). Cả hai paper chỉ test phân loại — **phải đo lại trên head hồi quy**.
**Thay đổi:** thay đóng băng tĩnh bằng **gradual unfreeze + discriminative LR + STLR** làm arm A; thêm **RecAdam**
(γ phải quét, không lấy mặc định GLUE 5000) làm arm B; chọn người thắng trên tập nhỏ của Pebble, đo trên `severity`
(hồi quy), không chỉ `emotion`.

### 1.3 Thêm bước MLM thích nghi miền (D-F) **[v1]**
**Hiện tại:** pretrain duy nhất là GoEmotions trên *head emotion*; không có MLM tiếp tục huấn luyện trong miền cho
encoder.
**Bằng chứng:** FAIIR (01), MentalBERT (12), và NCUEE (19) đều ghi nhận thích nghi affect/MLM trong miền có ích;
ModernBERT (22) dùng **masking 30%** (không phải 15%). FAIIR *tuyên bố* MLM "nâng đáng kể" nhưng **chưa bao giờ cô
lập đo nó** — một ablation Pebble có thể sở hữu.
**Thay đổi:** thêm **bước MLM masking 30%** trên corpus trong miền (text GoEmotions/Empathetic/ESConv) trước khi
fine-tune head, **kèm ablation cô lập** (MLM-on vs MLM-off, cùng seed) — phép đo sạch đầu tiên trong miền này. Khớp
miền thích nghi với head (text emotion/distress cho `severity`).

**Kết quả thực nghiệm (2026-06-17 · 3 seed [13/42/1337] · NeoBERT · P100) — chạy ablation cô lập hai lần:**
- *Run A* (corpus = 25k **chính text fine-tune**, masking 30%, lưu encoder **fp16**): MLM-on **thua** mọi metric — Δ(on−off) macroF1 −0.007, **ECE +0.081**, Pearson −0.046. Negative sạch.
- *Run B* (corpus = 80k text trong miền **riêng biệt** [GoEmotions-raw 9k + tweet_eval sentiment/offensive/hate/irony/emotion 71k, khử trùng với fine-tune/eval], **masking 15%**, encoder **fp32**): kết luận lật thành **tradeoff theo task** — emotion macroF1 **+0.0127 ± 0.0099** (3/3 seed dương), nhưng severity **Pearson −0.045 ± 0.017** (3/3 seed âm) và **ECE +0.052** (vẫn tệ, ít hơn Run A ~36%). MLM loss 2.42→2.29.

**Diễn giải:** negative ban đầu một phần là artifact (corpus trùng tập fine-tune + confound fp16). Với corpus TAPT đúng nghĩa, MLM adaptation **giúp head emotion (classification) nhưng hại head severity (regression)** — hai head dùng chung một encoder. Corpus Run B ~71k/80k là sentiment/toxicity Twitter (chỉ 9k comment emotion sống sót sau khử trùng — GoEmotions-raw mỗi annotator một dòng), đẩy representation về phía tách lớp categorical, đánh đổi độ phân giải mức độ. **Bước tiếp theo còn mở:** cân lại corpus về phía affect có mức độ (bỏ offensive/hate; thêm EmoBank / SemEval V-reg / EI-oc) rồi đo lại severity, hoặc tách encoder theo pool. Notebook: `kaggle/finetuning-message/pebble-mlm-ablation-3seed/`.

### 1.4 Chọn backbone là một thí nghiệm, không phải ghi chú (D-A) **[v1]**
**Hiện tại:** NeoBERT là chính; ModernBERT là *dự phòng* tuyến hai trong tài liệu.
**Bằng chứng:** Paper **22** — ModernBERT và NeoBERT không có benchmark chung và **cả hai chưa được đánh giá trên
mental-health/affect/MTL**; lợi thế của ModernBERT là *ngữ cảnh dài*, sai chế độ cho input turn-level ngắn của Pebble.
Chỉ một cuộc đối đầu nội bộ của Pebble mới quyết định được.
**Thay đổi:** chạy **NeoBERT vs ModernBERT như một arm thực sự** (cùng công thức 3-head, cùng dữ liệu/seed; so emotion
macro-F1 + severity Pearson + latency ở input độ dài turn). Giữ NeoBERT làm mặc định (license MIT sạch) nhưng để con
số, chứ không phải tài liệu strategy, biện minh cho nó. (Tái dùng phát hiện **masking 30%** của 22 cho §1.3.)

---

## 2. Dữ liệu (Dataset)

### 2.1 Chọn một sơ đồ C-SSRS; đừng trích "mốc" chéo giữa các paper (D-C) **[v2 + v1-rời rạc]**
**Hiện tại:** strategy §5.4 liệt kê CLPsych/UMD cho safety; `severity` là hồi quy liên tục [0,1] từ cường độ
SemEval/WASSA.
**Bằng chứng:** các "mốc" C-SSRS trong 14/15/16/17 **không so sánh được** (khác dataset, khác tập lớp, khác metric,
khác mức độ chi tiết; "IN" nghĩa là *Ideation* ở paper này nhưng *Indicator* ở paper khác; Attempt F1 0.65 vs recall
≈0 là artefact post-vs-user). Bài học bền vững duy nhất là cấu trúc lỗi **thứ bậc (ordinal)**.
**Thay đổi:**
- Khi thêm **head safety/C-SSRS** (v2), chọn **một** ánh xạ lớp tường minh — đề xuất **4-class của paper 17**
  (Attempt/Behavior/Ideation/Indicator, Indicator = không-rủi-ro) — và ghi rõ trong lớp dữ liệu; tuyệt đối không
  trung bình hay xếp hạng các con số chéo bốn paper.
- Với bất kỳ **severity rời rạc hoá** nào (strategy đã nhắc "rời rạc hoá energy/severity thành 3 lớp thứ bậc"):
  dùng **loss thứ bậc/nhạy khoảng cách** (ordinal-CE / CORN) thay vì CE phẳng, vì lỗi giữa các mức kề nhau nên ít
  bị phạt hơn lỗi xa.
- **Cân bằng lại một cách thận trọng:** paper 15 thấy mọi thủ thuật resample/weighting đều *làm giảm* weighted-F1
  dưới một tập test mất cân bằng thực tế — hãy đo trên phân phối thực tế trước khi tin vào oversampling.

### 2.2 Transfer cho hồi quy + một arm init khớp affect (D-D) **[v1]**
**Hiện tại:** head `severity` chỉ warm-start từ encoder NeoBERT chung; không có init đặc thù affect.
**Bằng chứng:** Paper **19** — init khớp affect (dòng EmoBERTa) nâng hồi quy distress **+0.0795 (+22% tương đối)**,
nhưng **phụ thuộc target** (init Twitter-sentiment chung *làm hại* một track). Paper **18** xác nhận single-linear
MSE + Pearson là thiết kế chuẩn.
**Thay đổi:** thêm **arm ablation affect-matched-init** (warm-start encoder từ checkpoint thích nghi emotion/distress
vs vanilla) và giữ nó là một arm, không phải mặc định. Dùng **WASSA-empathy** (`data/external/wassa_empathy/`,
CC-BY → triển khai được) làm baseline severity ngoài (empathy r≈0.558 / distress r≈0.507 từ 18).

### 2.3 ESConv làm lát cắt calibration cho nhánh nghiên cứu; bỏ RSD-15K (D-H) **[v1]**
**Hiện tại:** `external.py` có loader cho SemEval/WASSA-intensity; ESConv đã tải nhưng chưa có loader; RSD-15K được
liệt kê như một corpus lớn tiềm năng.
**Bằng chứng:** **RSD-15K xác nhận lại không lấy được** (repo 404 ngày 2026-06-16; tổ chức không có repo công khai
nào). **ESConv là CC-BY-NC** → chỉ nhánh nghiên cứu, **không bao giờ vào model triển khai**; intensity 1–5 của nó là
*tự báo cáo một người chấm, mức hội thoại, không có IAA trên nhãn affect* → một *phân phối calibration*, không phải
nhãn vàng turn-level.
**Thay đổi:**
- Thêm **`load_esconv()`** theo mẫu `load_semeval_intensity`, **mở `ESConv.json` với `encoding='utf-8'`**
  (không decode được bằng cp1252 — crash trên Windows nếu không), và **gắn cờ chỉ-nhánh-nghiên-cứu** để nó không rò
  vào tập train triển khai được.
- Xây lát cắt `eval/calibration/esconv_intensity`: Pearson/Spearman giữa `severity` dự đoán và intensity ESConv.
- **Đánh dấu RSD-15K đã đóng** trong `dataset-acquisition-plan.md`; giữ UMD-Reddit (DUA) làm dự phòng duy nhất.
  **Tái dùng quy trình QC chú thích của RSD-15K** (cổng 95% trước nhiệm vụ, kiểm 10% mỗi ngày, κ≈0.72), không phải
  dữ liệu của nó.

---

## 3. Thiết kế thực nghiệm (Experiment design)

### 3.1 Lưới ablation MTL (D-B) **[v1]**
Chạy trên cùng dữ liệu/split/seed, với severity-Pearson + emotion-macro-F1 làm mục tiêu chung:
`static-λ` (hiện tại) → `uniform-sum` (null của 18) → `Kendall-UW` (safety có sàn) → `GradNorm` → `PCGrad`/`Nash`.
**Tiêu chí thành công:** một arm nguyên lý phải đánh bại *uniform-sum* (không chỉ static-λ) trên metric chung để
biện minh cho điểm mới. Báo cáo mean ± std trên ≥3 seed (đã có trong hợp đồng `SeedResults` của `metrics.py`).

### 3.2 Cuộc đấu staged-FT (D-E) **[v1]**
Hai arm loại trừ lẫn nhau — **(A)** ULMFiT gradual-unfreeze+discriminative-LR+STLR vs **(B)** RecAdam — cộng với
đóng băng tĩnh hiện tại làm baseline. Đo riêng trên head **hồi quy** (cả hai paper đều chưa test hồi quy). Việc này
cũng giảm rủi ro overfitting dữ liệu nhỏ ở §5.3 bằng bằng chứng thay vì giả định.

### 3.3 Ablation cô lập MLM (D-F) **[v1]**
MLM-on vs MLM-off, masking 30%, cùng seed — phép đo sạch mà FAIIR bỏ qua. Một dòng trong bảng kết quả; giá trị
trích dẫn cao. **Đã chạy (2026-06-17):** thực nghiệm **masking 15% trên corpus *riêng biệt* 80k** thắng công thức
30%/cùng-corpus, và kết quả là **tradeoff classification-vs-regression**, không phải thắng đồng đều — xem §1.3.

### 3.4 Đối đầu backbone (D-A) **[v1]**
NeoBERT vs ModernBERT, cùng công thức, ở input **độ dài turn** (nơi 22 thừa nhận ModernBERT mất lợi thế ngữ cảnh dài).
Quyết định backbone bằng một con số.

### 3.5 Xây tập đánh giá theo cách của FAIIR (01) **[v1]**
Tập test Protocol B của Pebble nhỏ (~500) và một lát cắt ngẫu nhiên thuần sẽ thiếu các ca severity cao. Xây nó theo
**cách FAIIR: nửa ngẫu-nhiên-khó, nửa được tuyển chọn** để phủ mọi dải severity + các lỗi nhãn silver nghi vấn — đó
chính là điều khiến tập 40-mục của FAIIR đủ thông tin để thay đổi ngưỡng production. Kèm một **lát cắt đồng thuận
chuyên gia** nhỏ (3 chấm mù + 3 chấm mở) báo cáo model-vs-người *bên cạnh* silver-vs-người.

---

## 4. Đánh giá & metric (khoảng trống code cụ thể nhất)

`evaluation/metrics.py` hiện có MAE, macro-F1, safety P/R, và `severity_band_mae`. Bằng chứng đòi hỏi thêm ba thứ:

| Thêm | Vì sao | Nguồn |
|------|--------|-------|
| **Pearson + Spearman** cho `severity`/`energy` | metric chuẩn cho affect liên tục khắp Pillar 5; chỉ MAE che mất chất lượng thứ hạng | 18, 19, 23 |
| **QWK + MAE thứ bậc** cho severity rời rạc / mức safety (v2) | lỗi C-SSRS là thứ bậc; accuracy/F1 phẳng che cấu trúc lỗi kề-vs-xa (best-F1 ≠ best-ordinal ở 16) | 14, 16, 17 |
| **ECE + đường tin cậy (reliability)** | Decision Engine tiêu thụ *xác suất*; không paper nào trong tập calibrate — đóng góp của Pebble và là yêu cầu khi triển khai | 01, 15, 16 |

Cộng thêm **tinh chỉnh ngưỡng theo từng head** trên validation (chính sách theo tầng tần suất của FAIIR) thay vì một
ngưỡng duy nhất — và công bố đánh đổi precision/recall (FAIIR: +4% P đổi −6% R).

---

## 5. Safety head (D-C/D-G) — **[v2]**, bằng chứng đã lưu
v1 chưa có safety head học được (`decisions.md`). Khi nó quay lại:
- **Loss thứ bậc/nhạy khoảng cách** + QWK (D-C), **sàn recall lớp Attempt** + ngưỡng được tinh chỉnh + calibration
  (D-G) — đúng khoảng trống mà mọi paper C-SSRS bỏ ngỏ.
- **Kiểm toán teacher gán nhãn silver:** paper 16 cho thấy **Gemini 1.5 Pro là LLM *yếu nhất*** trên C-SSRS
  (acc 0.596) trong khi Claude/Mistral đạt QWK≈0.876 ≈ κ con người 0.82. Nếu teacher dạng Gemini quay lại cho nhãn
  silver, hãy kiểm toán nhãn khủng hoảng của nó so với con người trước khi tin.
- Giữ kiến trúc safety **rule-layer trước** của FAIIR (tripwire từ khoá chỉ có thể *leo thang*, model sau, con người
  luôn quyết định) — đã khớp với union-of-triggers của strategy (§8.1).

---

## 6. Thay đổi code/file cụ thể (diff nhỏ nhất khả thi)

| File | Thay đổi | Mục |
|------|----------|-----|
| `models/losses.py` | Thêm chế độ `uniform-sum` + đường LibMTL/Kendall-UW với **sàn trọng số safety**; thay TODO bằng arm thật | 1.1 |
| `evaluation/metrics.py` | Thêm `pearson()`, `spearman()`, `quadratic_weighted_kappa()`, `expected_calibration_error()`; mở rộng `TARGETS` | 4 |
| `training/trainer.py` | Thay đóng băng tĩnh bằng **gradual unfreeze + discriminative LR + STLR**; thêm tuỳ chọn optimizer RecAdam | 1.2 |
| `training/` (mới) | Thêm bước **MLM pretrain** (mask 30%) + cờ `mlm_on/off` cho ablation | 1.3 |
| `data/external.py` | Thêm **`load_esconv()`** (UTF-8, cờ chỉ-nhánh-nghiên-cứu) | 2.3 |
| `data/taxonomy.py` / lớp dữ liệu | Khi có safety/C-SSRS: mã hoá **một** ánh xạ 4-class C-SSRS (17) | 2.1 |
| `models/neobert_multitask.py` + config | Thêm đường swap **ModernBERT** cho cuộc đối đầu backbone | 1.4 |
| `docs/dataset-acquisition-plan.md` | Đánh dấu **RSD-15K đã đóng**; ghi ESConv chỉ-NC + lưu ý UTF-8 | 2.3 |

---

## 7. Lộ trình ưu tiên

1. **Ngay (v1, đòn bẩy cao, chi phí thấp):**
   - 4 — thêm Pearson/Spearman (+ khung ECE) vào `metrics.py`. *(1 file, mở khoá đánh giá D-D/D-B)*
   - 1.2 — sửa công thức fine-tuning (gradual unfreeze + discriminative LR + STLR). *(mâu thuẫn từ ULMFiT là phát
     hiện rõ ràng nhất, độ tin cậy cao nhất)*
   - 1.1 — thêm baseline uniform-sum + arm Kendall-UW. *(điểm mới số 1; cần metric từ bước trên)*
2. **Tiếp theo (v1):** 1.3 ablation cô lập MLM · 2.2 arm affect-init · 1.4 đối đầu backbone · 2.3 loader ESConv.
3. **Thực nghiệm & báo cáo (v1):** 3.1–3.5 làm các bảng kết quả; 3.5 xây tập đánh giá kiểu FAIIR.
4. **Khi safety head quay lại (v2):** toàn bộ Mục 5.

---

## 8. Những gì bằng chứng *không* ủng hộ (lan can an toàn)
- **Không có con số SoTA C-SSRS chéo paper.** Đừng viết "SoTA C-SSRS là 0.75 / 0.52 / 0.77" — chúng là các task khác
  nhau (D-C). Chỉ trích từng số so với chính corpus của nó.
- **MTL nguyên lý không mặc nhiên thắng.** Nó phải đánh bại uniform-sum trên dữ liệu Pebble; 18 là ca cảnh báo.
- **Độ lớn ở người lớn là cận trên.** Mọi con số Pillar-4/5 là Reddit/essay người lớn; chỉ cơ chế + metric chuyển
  giao sang miền trẻ em của Pebble — coi r/F1/QWK tuyệt đối là giả thuyết, phải kiểm chứng trên lát cắt của Pebble.
- **ESConv không thể train model triển khai** (CC-BY-NC) — chỉ nhánh nghiên cứu / calibration.
- **RecAdam và gradual-unfreeze không chồng nhau** — chúng là arm cạnh tranh (D-E).

> Chỉ mục bằng chứng: các bản deep-read từng paper trong [`papers/15-cssrs-hybrid.md`](./papers/finetuning-message/15-cssrs-hybrid.md)–[`papers/23-esconv.md`](./papers/finetuning-message/23-esconv.md)
> và [`papers/01-faiir.md`](./papers/finetuning-message/01-faiir.md)/[`papers/06`](./papers/finetuning-message/06-kendall-uncertainty-mtl.md)–`14`; lập luận chéo paper
> + bảng theo từng quyết định trong [`papers/SYNTHESIS-deep-read.md`](./papers/SYNTHESIS-deep-read.md).
