# Giải thích chi tiết quá trình fine-tuning model (Text — NeoBERT)

> Tài liệu này giải thích **toàn bộ** pipeline fine-tuning model text của Pebble: từ cách xử lý
> dữ liệu, các thông số khi training, đến ý nghĩa của từng con số kết quả. Bám sát đúng code
> trong `kaggle/pebble-mlm-ablation-3seed/` (các cell `s1`…`s8`) và file kết quả thật.
>
> Cách **chạy** thí nghiệm này nằm ở [`run-guideline.md`](./run-guideline.md). Tài liệu hiện tại
> trả lời câu hỏi **"nó hoạt động như thế nào và kết quả nghĩa là gì"**.

---

## 0. Bức tranh tổng thể

Pebble cần một bộ phân loại cảm xúc chạy **trước** bước sinh văn bản, cho ra điểm số có cấu trúc.
Model nền là **NeoBERT** (`chandar-lab/NeoBERT`, một encoder kiểu BERT hiện đại). Ta gắn thêm
**2 đầu ra (head)** lên trên encoder:

- **Emotion head** — phân loại cảm xúc (28 lớp của GoEmotions) bằng softmax.
- **Severity head** — hồi quy mức độ "nặng/khẩn cấp" của câu (1 số trong khoảng 0–1) bằng sigmoid.

Thí nghiệm này **không chỉ** fine-tune model — nó là một **ablation** (thí nghiệm đối chứng) để
trả lời một câu hỏi nghiên cứu cụ thể:

> *"Nếu ta cho encoder 'làm quen' với văn bản trong miền (in-domain) bằng MLM trước khi
> fine-tune, thì kết quả có tốt hơn không?"*

Để trả lời, ta huấn luyện **2 nhánh (arm)** và so sánh:

| Nhánh | Mô tả |
|---|---|
| **MLM-off** | NeoBERT gốc → fine-tune thẳng (baseline) |
| **MLM-on** | NeoBERT đã được "thích nghi miền" bằng MLM → rồi mới fine-tune |

Cả hai nhánh chạy trên **3 seed** `[13, 42, 1337]` để đo độ ổn định và lấy **delta theo cặp**
(paired delta) — đây mới là kết luận đáng tin, vì nó khử nhiễu ngẫu nhiên của từng seed.

Toàn bộ quy trình gồm **2 giai đoạn huấn luyện** nối tiếp nhau:

```
GIAI ĐOẠN 1 (làm 1 lần)            GIAI ĐOẠN 2 (lặp cho mỗi nhánh × mỗi seed)
─────────────────────────         ──────────────────────────────────────────
Corpus in-domain (80k câu)        Dữ liệu có nhãn (GoEmotions + EI-reg)
        │ MLM 15% masking                 │ fine-tune multi-task 2 head
        ▼                                 ▼
encoder đã thích nghi  ──────────►  so sánh MLM-on vs MLM-off  ──►  results_summary.csv
(mlm_encoder.pt)                    (3 seed, paired delta)
```

---

## 1. Xử lý dữ liệu

Có **hai loại dữ liệu hoàn toàn tách biệt**, đây là điểm cốt lõi của thiết kế.

### 1.1. Dữ liệu có nhãn để fine-tune + đánh giá (cell `s2`)

Đây là dữ liệu "dạy" cho 2 head và để chấm điểm.

- **Emotion → GoEmotions** (`go_emotions`, bản `simplified`): bình luận Reddit, mỗi câu có nhãn
  cảm xúc. Code lấy **nhãn đầu tiên** của mỗi câu (`r["labels"][0]`), nếu rỗng thì gán `neutral`.
  → 28 lớp cảm xúc.
- **Severity → EI-reg** (SemEval-2018 Task 1, tải trực tiếp từ GitHub): các tweet có điểm cường
  độ cảm xúc 0–1. Quy ước: các cảm xúc **tiêu cực** (`anger`, `fear`, `sadness`) giữ nguyên điểm
  cường độ làm `severity`; cảm xúc tích cực (`joy`) gán `severity = 0`. → đây là tín hiệu "mức độ
  nặng". Nếu tải lỗi, code có **fallback tổng hợp** (sinh dữ liệu giả) để pipeline không chết.
- **Chuẩn hoá (`norm`)**: lowercase + gộp khoảng trắng → dạng chuẩn để so trùng.
- **"Hàng rào chống rò rỉ" (`FT_EVAL_TEXTS`)**: gom **toàn bộ** text fine-tune + eval vào một
  tập đen. Tập này dùng ở bước sau để đảm bảo corpus MLM **không chứa** bất kỳ câu nào sẽ được
  fine-tune/đánh giá → tránh model "học vẹt" đáp án (data leakage).

### 1.2. Corpus để thích nghi miền bằng MLM (cell `s3`)

Đây là dữ liệu **không nhãn**, **tách riêng**, chỉ để encoder "làm quen giọng văn" của miền.

- **Nguồn**: GoEmotions bản `raw` (~211k bình luận Reddit) + `tweet_eval` (các tập con `emotion`,
  `sentiment`, `offensive`, `hate`, `irony`).
- **Khử trùng lặp 2 lớp**: mỗi câu được chuẩn hoá rồi loại nếu (a) trùng câu khác trong corpus,
  hoặc (b) nằm trong `FT_EVAL_TEXTS`. → đảm bảo encoder học trên **văn bản MỚI** in-domain, đúng
  tinh thần **TAPT/DAPT** (Task/Domain-Adaptive Pre-Training).
- **Cắt ngưỡng**: xáo trộn rồi cắt còn `MLM_CORPUS_CAP = 80.000` câu.

### 1.3. Tokenize

Cả hai loại đều đi qua cùng một tokenizer của NeoBERT: cắt/đệm về độ dài cố định
`MAX_LEN = 64` token (`truncation + padding="max_length"`). Câu ngắn được đệm, câu dài bị cắt.

---

## 2. Giai đoạn 1 — Thích nghi miền bằng MLM (cell `s4`)

MLM = **Masked Language Modeling**: che ngẫu nhiên một số token rồi bắt model đoán lại token bị
che. Đây là cách BERT tự học ngữ nghĩa mà **không cần nhãn**.

**Cách che token (chuẩn BERT 15%)** — hàm `mask_batch`:
- Chọn **15%** số token (`MLM_MASK_PROB = 0.15`) để "đụng tới", bỏ qua các token đặc biệt
  (`[CLS]`, `[SEP]`, padding…).
- Trong số token được chọn: **80%** thay bằng `[MASK]`, **10%** thay bằng token ngẫu nhiên,
  **10%** giữ nguyên. Đây là "quy tắc 80/10/10" kinh điển, giúp model không chỉ học mỗi `[MASK]`.
- Các token **không** được chọn bị gán nhãn `-100` → bị bỏ qua khi tính loss
  (`ignore_index=-100`), tức loss chỉ tính trên token bị che.

**Thông số huấn luyện MLM:**

| Thông số | Giá trị | Ý nghĩa |
|---|---|---|
| Optimizer | AdamW, `lr = 5e-5`, `weight_decay = 0.01` | tốc độ học chuẩn cho adapt encoder |
| Epochs | `MLM_EPOCHS = 2` | quét corpus 80k câu 2 lượt |
| Batch | `BATCH = 32` | |
| Mixed precision | `autocast` + `GradScaler` (fp16) | tăng tốc trên GPU |

**Quan trọng — lưu ở fp32:** sau khi train xong, encoder được lưu ở **fp32** (`mlm_encoder.pt`),
*không* fp16. Lý do: nếu lưu fp16 thì nhánh MLM-on sẽ có sai số làm tròn khác baseline → khi so
sánh sẽ không biết cải thiện đến từ MLM hay từ độ chính xác số. Lưu fp32 **khử nhiễu confound**
này, để phép so sánh công bằng.

Encoder đã thích nghi được giữ trong biến `adapted_state` và **dùng lại cho cả 3 seed** ở giai
đoạn 2 (không train lại MLM mỗi seed → tiết kiệm và đảm bảo cùng một điểm xuất phát).

---

## 3. Giai đoạn 2 — Fine-tune multi-task 2 head (cell `s5`)

### 3.1. Kiến trúc model

```
        input_ids ──► NeoBERT encoder ──► vector [CLS] (768 chiều)
                                              │
                        ┌─────────────────────┴─────────────────────┐
                        ▼                                            ▼
               Emotion head (28 lớp)                         Severity head (1 số)
          Dropout→Linear→GELU→Dropout→Linear            ... rồi sigmoid → [0,1]
                    → softmax
```

Mỗi head là một MLP nhỏ 2 lớp (`Head`: `Dropout(0.1) → Linear(768→256) → GELU → Dropout → Linear`).
Model lấy vector của token `[CLS]` (vị trí 0) làm đại diện cả câu rồi đưa vào 2 head.

### 3.2. "Two-pool masked multi-task" — huấn luyện 2 nhiệm vụ cùng lúc

Đây là phần tinh tế nhất. Dữ liệu fine-tune trộn **2 hồ (pool)**:
- `FT_PER_POOL = 2500` ví dụ emotion (gắn `task = EMO`)
- `FT_PER_POOL = 2500` ví dụ severity (gắn `task = SEV`)

Trong mỗi batch có lẫn cả hai loại. Loss được tính **có mặt nạ theo loại**:
- Ví dụ emotion → chỉ tính **cross-entropy** trên emotion head.
- Ví dụ severity → chỉ tính **MSE** trên severity head.
- `loss = el.sum() * 0.0` là mẹo khởi tạo loss = 0 nhưng vẫn nối vào đồ thị tính đạo hàm, phòng
  trường hợp một batch chỉ toàn một loại.

→ Mỗi head **chỉ học từ pool dữ liệu của nó**, nhưng **chung một encoder** → encoder học biểu
diễn phục vụ cả hai nhiệm vụ.

### 3.3. Discriminative learning rate (LR phân tầng)

Optimizer AdamW dùng **2 mức LR khác nhau** — điểm mấu chốt khi fine-tune một model đã pretrain:

| Nhóm tham số | Learning rate | Vì sao |
|---|---|---|
| 2 head (mới tinh) | `2e-5` | học nhanh hơn, vì khởi tạo ngẫu nhiên cần học từ đầu |
| encoder (đã pretrain) | `1e-5` | học chậm hơn, để **không phá vỡ** kiến thức đã có |

**Các thông số fine-tune khác:** `FT_EPOCHS = 3`, `BATCH = 32`, `weight_decay = 0.01`, mixed
precision (autocast + GradScaler).

### 3.4. Đánh giá (validation)

Sau khi train, model dự đoán trên tập val tách riêng (`EMO_VAL_N = 1000` câu emotion,
`SEV_VAL_N = 600` câu severity) và tính 5 chỉ số (xem mục 5). Hàm `finetune(tag, adapted, seed)`
trả về 1 dòng kết quả cho mỗi (nhánh, seed).

---

## 4. Chạy 3 seed & tổng hợp (cell `s6`, `s7`)

- **`s6`**: vòng lặp qua `SEEDS = [13, 42, 1337]`, mỗi seed chạy **cả hai** nhánh
  (`finetune("MLM-off", None, seed)` và `finetune("MLM-on", adapted_state, seed)`). Sau **mỗi**
  seed ghi `results_per_seed.csv` ngay (checkpoint tăng dần) → nếu kernel bị ngắt vẫn giữ được
  các seed đã xong.
- **`s7`**: tổng hợp thành `results_summary.csv` với:
  - **mean ± std** mỗi chỉ số cho từng nhánh.
  - **delta theo cặp** `(MLM-on − MLM-off)` tính **trên cùng seed** rồi lấy mean ± std. Đây là
    con số kết luận: nó khử nhiễu giữa các seed, cho biết MLM thực sự giúp hay hại.

### Bảng thông số (gom toàn bộ, từ `s1`)

| Thông số | Giá trị | Thuộc |
|---|---|---|
| Model nền | `chandar-lab/NeoBERT` (revision ghim) | chung |
| `MAX_LEN` | 64 | tokenize |
| `BATCH` | 32 | chung |
| `MLM_MASK_PROB` | 0.15 | MLM |
| `MLM_CORPUS_CAP` | 80.000 | MLM |
| `MLM_EPOCHS` | 2 | MLM |
| MLM LR / wd | 5e-5 / 0.01 | MLM |
| `FT_EPOCHS` | 3 | fine-tune |
| `FT_PER_POOL` | 2.500 / pool | fine-tune |
| FT LR (head / encoder) | 2e-5 / 1e-5 | fine-tune |
| `EMO_VAL_N` / `SEV_VAL_N` | 1000 / 600 | eval |
| `SEEDS` | 13, 42, 1337 | chung |

> **Lưu ý quy mô:** đây là cấu hình **ablation nhanh** (2.500 ví dụ/pool, 3 epoch) để so sánh 2
> nhánh cho rẻ, **không phải** cấu hình train model production. Con số tuyệt đối sẽ thấp hơn SOTA;
> điều ta quan tâm là **chênh lệch giữa 2 nhánh**, không phải đỉnh tuyệt đối.

---

## 5. Ý nghĩa kết quả

### 5.1. Giải thích từng chỉ số

| Chỉ số | Đo cái gì | Tốt khi | Tham chiếu |
|---|---|---|---|
| **emo_macroF1** | F1 trung bình theo lớp của emotion (28 lớp). "Macro" = mỗi lớp tính ngang nhau, nên lớp hiếm cũng quan trọng | **cao** | random ≈ 1/28 ≈ 0.036 |
| **emo_ece** | *Expected Calibration Error* — độ "thành thật" của xác suất. Model nói "80% chắc" thì có đúng ~80% lần không | **thấp** | 0 = hoàn hảo |
| **sev_pearson** | Tương quan tuyến tính giữa severity dự đoán và thật | **cao** (→1) | 0 = không liên hệ |
| **sev_spearman** | Tương quan theo **thứ hạng** (model có xếp đúng câu nào nặng hơn câu nào) | **cao** (→1) | |
| **sev_mae** | Sai số tuyệt đối trung bình của severity (lệch trung bình bao nhiêu trên thang 0–1) | **thấp** | |

### 5.2. Kết quả thật (`results_summary.csv`)

| Nhánh | emo_macroF1 | emo_ece | sev_pearson | sev_spearman | sev_mae |
|---|---|---|---|---|---|
| **MLM-off** (baseline) | 0.3133 ± 0.0110 | **0.1076** ± 0.0352 | **0.6169** ± 0.0170 | **0.6125** ± 0.0235 | **0.1255** ± 0.0037 |
| **MLM-on** (adapted) | **0.3260** ± 0.0098 | 0.1593 ± 0.0099 | 0.5715 ± 0.0061 | 0.5710 ± 0.0084 | 0.1321 ± 0.0017 |
| **delta (on − off)** | **+0.0127** ± 0.0099 | +0.0517 ± 0.0254 | −0.0454 ± 0.0172 | −0.0415 ± 0.0214 | +0.0066 ± 0.0021 |

> Đọc bảng: **cột** = chỉ số; **`±`** = độ lệch chuẩn qua 3 seed (càng nhỏ càng ổn định);
> **in đậm** = nhánh tốt hơn ở chỉ số đó. Dưới đây giải thích từng cột: nghĩa là gì, **giá trị
> bao nhiêu là tốt/xấu**, và **mốc chuẩn để so**.

#### Bảng "thước đo" — mỗi chỉ số tốt/xấu ở đâu

| Chỉ số | Hướng tốt | Tệ nhất (random/naive) | "Chuẩn" tham chiếu (literature) | Rất tốt (SOTA) | **Pebble (MLM-off)** | Xếp loại |
|---|---|---|---|---|---|---|
| **emo_macroF1** | ↑ cao | ~0.036 (đoán ngẫu nhiên 1/28) | ~0.46 (BERT-base, GoEmotions, paper gốc) | ~0.50–0.52 | **0.3133** | Trung bình–thấp |
| **emo_ece** | ↓ thấp | ~0.5 (tự tin mù) | < 0.10 = chấp nhận; < 0.05 = tốt | ~0.02–0.03 | **0.1076** | Hơi cao (tạm được) |
| **sev_pearson** | ↑ cao (−1…1) | 0 (không liên hệ) | ~0.65–0.75 (EI-reg, SemEval-2018) | ~0.80 | **0.6169** | Khá |
| **sev_spearman** | ↑ cao (−1…1) | 0 | ~0.65–0.75 | ~0.80 | **0.6125** | Khá |
| **sev_mae** | ↓ thấp (0…1) | ~0.20–0.25 (đoán hằng số) | — | → 0 | **0.1255** | Tốt |

> ⚠️ Các mốc "literature/SOTA" được đo trên **tập test đầy đủ, điều kiện chuẩn** của từng dataset,
> còn số của ta đo trên **val subset nhỏ** (1000 câu emotion / 600 câu severity) sau cấu hình
> ablation nhanh. Vì vậy hãy xem chúng là **định hướng**, không phải so sánh 1-1.

#### Vậy `0.3133` (emo_macroF1) là tốt hay xấu?

- **Thang điểm**: 0 (tệ) → 1 (hoàn hảo). Đây là F1 trung bình **theo lớp** trên **28 lớp** cảm
  xúc của GoEmotions — bài toán rất khó vì nhiều lớp và mất cân bằng nặng.
- **So với đoán ngẫu nhiên** (`1/28 ≈ 0.036`): `0.3133` **tốt hơn ~9 lần** → model rõ ràng đã học
  được tín hiệu thật, không phải đoán mò.
- **So với chuẩn literature** (BERT-base fine-tune đầy đủ trên GoEmotions, macro-F1 ≈ **0.46**):
  `0.3133` **thấp hơn đáng kể** (~68% của mốc đó).
- **Kết luận**: đây là mức **"trung bình–thấp"**. **Không** phải vì model kém, mà vì đây là cấu
  hình **ablation rẻ** — chỉ 2.500 ví dụ/pool và 3 epoch, trong khi literature dùng ~43k câu train
  và train lâu hơn nhiều. Nói cách khác: `0.3133` là **bình thường cho quy mô thí nghiệm này**, và
  hoàn toàn đủ dùng cho mục đích **so sánh 2 nhánh** (đó mới là điều thí nghiệm cần trả lời).
  Để lên production thì phải tăng dữ liệu + epoch để đẩy con số này về gần ~0.46+.

#### Đọc nhanh 4 chỉ số còn lại

- **emo_ece = 0.1076** → ECE là sai số hiệu chỉnh độ tự tin; **0 là hoàn hảo, càng cao càng tệ**.
  Ngưỡng quen dùng: < 0.05 tốt, < 0.10 tạm được, > 0.15 kém. `0.1076` nằm **ngay trên ngưỡng "tạm
  được"** → model hơi **overconfident** (nói chắc hơn thực tế một chút). Nhánh MLM-on (`0.1593`)
  rơi vào vùng **kém**.
- **sev_pearson = 0.6169** và **sev_spearman = 0.6125** → tương quan, **thang −1…1, càng gần 1
  càng tốt**; 0 = vô dụng. `~0.61` nghĩa là severity dự đoán **bám khá sát** thứ tự/độ lớn thật,
  dưới các hệ thống top của SemEval (~0.7–0.8) nhưng là mức **khá** cho một head nhỏ.
- **sev_mae = 0.1255** → sai số tuyệt đối trung bình trên **thang 0–1**, **càng thấp càng tốt**.
  `0.1255` nghĩa là dự đoán lệch **trung bình ~0.125 điểm**. So với "đoán hằng số" (thường lệch
  ~0.20–0.25) thì đây là mức **tốt**, và còn **dưới ngưỡng hard-gate 0.15** mà Pebble đặt cho dải
  severity 0.5–0.8 (lưu ý: gate đo trên **dải hẹp**, còn `0.1255` là **toàn tập** — chỉ là tín
  hiệu tích cực, chưa đồng nghĩa đã pass gate).

**Tóm lại cách "chấm điểm" một dòng:** emotion còn **thấp** (do quy mô ablation), severity **khá–
tốt**, calibration **hơi yếu**. Nhánh `MLM-off` thắng ở 4/5 chỉ số → là nhánh được chọn để ship.

### 5.3. Đọc kết quả như thế nào

**1) MLM giúp emotion — nhẹ nhưng nhất quán.**
`emo_macroF1` tăng `+0.0127`, và độ lệch chuẩn của delta (`±0.0099`) nhỏ hơn giá trị trung bình,
lại **dương ở cả 3 seed** (kiểm chứng trong `results_per_seed.csv`: 13, 42, 1337 đều on > off).
→ Đây là cải thiện **thật và đều**, dù biên độ nhỏ. Hợp lý: corpus MLM là Reddit + tweet, rất gần
giọng văn của GoEmotions → encoder "quen miền" giúp head emotion một chút.

**2) Nhưng MLM làm HẠI severity và calibration — đây là cái giá phải trả.**
- `sev_pearson` **giảm** `−0.0454`, `sev_spearman` **giảm** `−0.0415`, `sev_mae` **tăng**
  `+0.0066` → severity kém đi đồng loạt trên cả 3 chỉ số, và đều ở cả 3 seed.
- `emo_ece` **tăng** `+0.0517` (calibration **tệ hơn** ~48%) → model trở nên "tự tin thái quá".

→ **Vì sao?** Corpus MLM nghiêng nhiều về dữ liệu cảm xúc/Reddit/tweet, nên encoder bị kéo về
phía tín hiệu **phân loại cảm xúc** mà **lệch khỏi** tín hiệu **cường độ** (severity là hồi quy
trên tweet SemEval, miền hơi khác). Đây là ví dụ kinh điển: thích nghi miền cho nhiệm vụ A có thể
**đánh đổi** bằng nhiệm vụ B.

**3) Kết luận của ablation: MLM không "đáng" cho bài toán đa nhiệm này.**
Cải thiện emotion (`+0.013`) quá nhỏ so với thiệt hại về severity (`−0.045` tương quan) và
calibration (`+0.052` ECE). Với Pebble, **severity và độ tin cậy của xác suất quan trọng hơn**
vài điểm F1 (xem các "hard gate" trong README: MAE dải severity ≤ 0.15, an toàn cần calibration
tốt). → Vì vậy ở cell `s8`, model **xuất xưởng chọn nhánh `MLM-off`** (`SHIP_ARM = "MLM-off"`),
đúng như ghi chú trong code: *"MLM-off = best severity, MLM-on = best emotion F1"*.

**4) Vì sao macro-F1 chỉ ~0.31?**
Vì đây là ablation nhỏ: 28 lớp GoEmotions rất mất cân bằng, chỉ lấy 1 nhãn/câu, chỉ 2.500 ví dụ
và 3 epoch. So với random `0.036` thì `0.31` đã tốt gấp ~9 lần, nhưng còn xa SOTA (~0.46–0.52).
**Đừng đọc con số tuyệt đối như chất lượng production** — mục tiêu của thí nghiệm là **so sánh
2 nhánh**, và phần đó đã trả lời rõ ràng.

---

## 6. Xuất model dùng được (cell `s8`)

Ablation (`s6`) **vứt bỏ** mọi model sau khi đo. Cell `s8` train lại **một** model trên nhánh đã
chọn (`MLM-off`, `seed 42`) bằng đúng vòng lặp fine-tune ở mục 3, rồi lưu **trọn gói**
`pebble_model.pt` gồm: `state_dict` (encoder + 2 head) + metadata (tên lớp cảm xúc, model nền,
revision, max_len, arm, seed) để dựng lại khi inference.

Kèm theo là hàm `analyze(text)` demo: đưa 1 câu → trả về `severity` + top-3 cảm xúc. Ví dụ output
mong đợi: câu *"I can't do this anymore, nothing matters"* → severity cao + cảm xúc tiêu cực
chiếm ưu thế.

---

## 7. So sánh nhanh với fine-tuning model Voice

Để tránh nhầm: pipeline **voice** (`pebble-voice-backbone`) **không** fine-tune encoder. Nó
**đóng băng** speech encoder (WavLM-Large) và chỉ huấn luyện 2 head nhỏ ("linear probe") trên
embedding — rẻ hơn nhiều, dùng để **chọn backbone** chứ không phải tối ưu toàn bộ. Còn ở đây
(text) ta fine-tune **cả encoder** (LR 1e-5) lẫn head. Đó là khác biệt cốt lõi giữa hai bên.

---

## Tóm tắt một dòng

> Adapt encoder bằng MLM trên 80k câu in-domain rồi fine-tune đa nhiệm (emotion + severity) qua
> 3 seed cho thấy: **MLM-on được +0.013 macro-F1 emotion nhưng mất 0.045 tương quan severity và
> xấu calibration** → chọn ship **MLM-off**, vì với Pebble severity & độ tin cậy quan trọng hơn.
