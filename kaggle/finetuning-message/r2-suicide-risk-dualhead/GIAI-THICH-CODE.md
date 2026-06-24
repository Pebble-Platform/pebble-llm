# Giải thích chi tiết `r2-suicide-risk-dualhead.py`

> Tái hiện mô hình **Hierarchical Dual-Head cho đánh giá nguy cơ tự tử**
> (Yang et al., IEEE BigData 2025; arXiv:2510.20085).
> Method spec: `docs/papers/finetuning-message/R2-DEEP-method-and-repro-vi.md`

---

## Tổng quan

File Python tự chứa (self-contained) train một mô hình phân loại **nguy cơ tự tử** từ
**chuỗi bài post Reddit của một người dùng** thành **4 mức ordinal (có thứ tự)**:

```
Indicator (0) → Ideation (1) → Behavior (2) → Attempt (3)
```

Chạy được cả trên **Kaggle GPU** lẫn **local CPU** (chế độ smoke test).

Điểm cốt lõi của kiến trúc: **dual-head** (hai đầu ra song song)
— một đầu **CORAL** cho ordinal regression, một đầu **classification** thường — kết hợp lại khi dự đoán.

### Luồng tổng thể

```
5 posts của 1 user
   │
   ▼
[RoBERTa encoder]  ──► 5 CLS vectors (B, S, h)
   + temporal embedding (Δt)
   ▼
[3-layer Transformer over sequence]
   ▼
[attention pooling, learnable query] ──► 1 vector u (B, h)
   + [stat-feature MLP fusion]
   ▼
   ├─► CORAL head  (ordinal)
   └─► CLS head    (classification)
        │
        ▼
   p_final = 0.5·CORAL + 0.5·CLS  ──► argmax ──► nhãn 0-3
```

---

## 1. Khởi tạo môi trường (dòng 14–54)

```python
IS_KAGGLE = Path("/kaggle").exists()
```

Phát hiện đang chạy trên Kaggle hay không bằng sự tồn tại của thư mục `/kaggle`.

**Run B preset (dòng 22–26):** Khi trên Kaggle, mặc định bật:

- `R2_GOLD_HOLDOUT=1` — đánh giá trên tập gold lâm sàng giữ riêng
- `R2_BALANCE=1` — cân bằng class (chống mất cân bằng class Behavior)
- `R2_EPOCHS=10`

`setdefault` nghĩa là **chỉ set nếu chưa có** — bạn vẫn override được từ bên ngoài.

**Pinned GPU stack (dòng 29–36):** Trên Kaggle, cài cứng `torch==2.5.1 + cu121` và
`transformers==4.48.2` vì torch mặc định của Kaggle hay bị hỏng.

---

## 2. Config (dòng 58–112)

Tất cả hyperparameter gom vào một `@dataclass`. Các điểm đáng chú ý:

| Tham số | Giá trị | Ý nghĩa |
|---|---|---|
| `model_name` | `welsachy/mental-roberta-base-finetuned-depression` | **Backbone.** `mental/mental-roberta-base` gốc đã bị **gated** (401 nếu không có token), nên dùng mirror công khai có base encoder = MentalRoBERTa. `AutoModel` chỉ load `roberta.*` và bỏ classifier head của mirror. |
| `seq_len` | 5 | Số post mỗi user-sequence (đúng paper) |
| `max_length` | 256 | Token/post (paper dùng 512, giảm cho nhanh) |
| `n_classes` | 4 | 4 mức ordinal |
| `freeze_layers` | 6 | Đóng băng embeddings + 6 layer đầu của encoder (~50% như paper) |
| `n_transformer_layers` | 3 | Sequence transformer 3 lớp |
| `w_coral / w_ce / w_focal` | 0.5 / 0.3 / 0.2 | Trọng số 3 thành phần loss (paper eq.4) |
| `lr_encoder / lr_new` | 2e-5 / 1e-4 | **2 learning rate**: encoder pretrained học chậm, phần mới học nhanh |
| `batch_size / grad_accum` | 8 / 2 | Effective batch = 16 |
| `patience` | 5 | Early stopping |
| `n_folds` | 5 | 5-fold cross-validation |

**`__post_init__` (dòng 105–112):** Khi `smoke=True`, thu nhỏ mọi thứ
(`max_length=32, seq_len=3, epochs=1, folds=2…`) để kiểm tra "đường ống" chạy
thông trên CPU trong vài giây.

**LABEL_MAP (dòng 116):** Bỏ class "Supportive", ánh xạ 4 class còn lại sang 0-3.

### Các biến môi trường điều khiển

| Env var | Tác dụng |
|---|---|
| `R2_SMOKE=1` | Chạy smoke test (CPU, siêu nhỏ) |
| `R2_MODEL=...` | Đổi backbone |
| `R2_GOLD_HOLDOUT=1` | Train trên nhãn-LLM, eval trên gold lâm sàng |
| `R2_BALANCE=1` | Cân bằng class bằng WeightedRandomSampler |
| `R2_EPOCHS=N` | Số epoch |
| `R2_DATA=path` | Trỏ tới CSV khác |

---

## 3. Data (dòng 125–271)

**`_parse_posts` (dòng 125–134):** Cột `Post` trong CSV là một list Python lưu dạng
string. Dùng `ast.literal_eval` để parse; 28/500 dòng fail (do ký tự escape) →
fallback dùng nguyên cell làm 1 post.

**`load_cssrs` (dòng 137–164):** Load tập CSSRS-500 cơ bản. Thứ tự ưu tiên:
file local → cache → tải từ Zenodo. Bỏ "Supportive", lấy **`seq_len` post gần nhất**
(`posts[-cfg.seq_len:]`).

**`load_combined` (dòng 176–191):** Load tập kết hợp **có cột Source**
(`cssrs500`, `av9ash`, `scraped`) — phục vụ chế độ gold-holdout.
`cssrs500` = nhãn lâm sàng gold; còn lại = nhãn do LLM gán.

**Text augmentation (dòng 194–235):** Chỉ áp dụng cho train. 3 phép (paper §III):

- `delete`: xóa ngẫu nhiên ~10% từ
- `swap`: hoán đổi 2 từ
- `synonym`: thay từ bằng synonym từ WordNet

**`stat_features` (dòng 238–242):** Tính 8 đặc trưng thống kê: 4 về độ dài post
(mean/std/min/max số từ) + 4 về khoảng thời gian — nhưng dataset không có timestamp
nên **4 cái sau luôn = 0**.

**`CSSRSDataset` (dòng 245–271):** Mỗi sample trả về:

- `input_ids`, `attention_mask`: shape `(seq_len, max_length)` — tokenize cả 5 post
- `valid`: mask boolean (True = post thật, False = padding)
- `dt`: Δt = 0 (không có timestamp)
- `feats`: 8 đặc trưng thống kê
- `label`: nhãn 0-3

Nếu sequence có ít hơn `seq_len` post → pad bằng chuỗi rỗng.

---

## 4. Model — `HierarchicalDualHead` (dòng 275–343)

Phần kiến trúc trung tâm.

**Khởi tạo (dòng 276–311):**

- `encoder`: RoBERTa pretrained. `_freeze(6)` đóng băng embeddings + 6 layer đầu
  (dòng 313–320 — parse tên parameter để biết layer index).
- `time_fc / time_ln`: nhúng temporal `ReLU(LayerNorm(W·Δt+b))` (dù Δt=0 ở đây).
- `seq_encoder`: Transformer 3 lớp xử lý chuỗi 5 post.
- `query` + `pool`: **attention pooling** với 1 learnable query — gom 5 post-vector
  thành 1 vector đại diện user.
- `feat_mlp` + `fuse`: hợp nhất 8 stat-feature.
- **Dual heads:**
  - `coral_fc` (dòng 309): 1 weight chung `w_c` (`bias=False`)
  - `coral_bias` (dòng 310): `n_classes-1 = 3` ngưỡng **có thứ tự** (điểm mấu chốt của
    CORAL — đảm bảo monotonic)
  - `cls_head` (dòng 311): classification thường, 4 output

**`encode_posts` (dòng 322–327):** Reshape `(B,S,L)→(B*S,L)`, đẩy qua encoder 1 lần
(hiệu quả), lấy CLS token `[:, 0]`, reshape về `(B,S,h)`.

**`forward` (dòng 329–343):** Cộng temporal embedding → sequence transformer (với
`src_key_padding_mask` bỏ qua post pad) → attention pooling → fuse feature →
ra **coral_logits (B,3)** và **cls_logits (B,4)**.

---

## 5. Losses (dòng 347–372)

**`coral_loss` (dòng 347–351):** CORAL = ordinal regression. Biến nhãn `y` thành 3 mục
tiêu nhị phân `t_k = 1[y > k]`. Ví dụ `y=2` → `[1,1,0]` (lớn hơn 0? có; lớn hơn 1? có;
lớn hơn 2? không). Dùng BCE. Vì `coral_fc` chung 1 weight + bias có thứ tự → đảm bảo dự
đoán **đơn điệu** (không mâu thuẫn kiểu "P(y>2) > P(y>1)").

**`focal_loss` (dòng 354–360):** Focal loss có `alpha` (trọng số class) + `gamma=2` —
tập trung vào sample khó, chống mất cân bằng.

**`coral_to_probs` (dòng 363–372):** Chuyển xác suất tích lũy `P(y>k)` thành xác suất
từng class qua hiệu các tầng:

- `P(y=0) = 1 - P(y>0)`
- `P(y=k) = P(y>k-1) - P(y>k)`
- `P(y=last) = P(y>K-2)`

**Tổng loss (paper eq.4, dòng 441–443):**

```
loss = 0.5·coral + 0.3·cross_entropy(label_smoothing) + 0.2·focal
```

---

## 6. Train / Eval (dòng 376–460)

**`make_optim` (dòng 376–393):** AdamW với **2 nhóm param** (encoder lr thấp, phần mới
lr cao) + scheduler **warmup rồi cosine decay**.

**`evaluate` (dòng 396–411):** **Cách kết hợp dual head (dòng 403):**

```python
p_final = 0.5 * coral_to_probs(coral) + 0.5 * softmax(cls)
```

Lấy trung bình xác suất 2 head, rồi `argmax`. Tính 4 metric:

- **macro-F1**
- **MAE** (sai số tuyệt đối trung bình — hợp cho ordinal)
- **QWK** (Quadratic Weighted Kappa — phạt nặng sai lệch xa)
- per-class F1

**`train_fold` (dòng 414–460):**

- Tính `counts` class để có `alpha` (focal) và sampler.
- Nếu `balance=True` (dòng 418–421): dùng `WeightedRandomSampler` với trọng số nghịch
  tần số → minibatch cân bằng class.
- AMP (mixed precision) trên GPU.
- Gradient accumulation, grad clipping.
- **Early stopping** theo macro-F1 với `patience=5`, lưu lại `best_state`.

---

## 7. Main / Gold-holdout (dòng 464–543)

### `run_gold_holdout` (dòng 464–502) — đánh giá "trung thực" nhất

> **Vấn đề:** Tập train mở rộng (av9ash + scraped) được gán nhãn bởi LLM → đánh giá
> trên chính nhãn LLM thì **circular**, không khách quan.
>
> **Giải pháp:** Train trên **pool nhãn-LLM** với 5-fold CV, nhưng **đánh giá mọi fold
> trên tập gold lâm sàng giữ riêng (CSSRS-500)**. Chỉ số gold mới là số honest.

Luồng (dòng 467–502):

1. Tách gold (`source==cssrs500`) khỏi pool (av9ash+scraped).
2. Tạo `gold_loader` cố định.
3. `StratifiedKFold` chia pool thành 5 fold.
4. Mỗi fold: train trên train-split của pool, validate trên val-split của pool,
   **rồi evaluate model tốt nhất của fold đó trên gold**.
5. Báo cáo gold macro-F1 (mean ± std) — đây là con số chính.
6. Lưu model có gold-F1 cao nhất.

### `main` (dòng 505–543)

- Nếu `gold_holdout` → chạy `run_gold_holdout` rồi return.
- Ngược lại → chạy **5-fold CV chuẩn** trên CSSRS-500: chia stratified, train từng fold,
  báo cáo CV macro-F1, lưu best model.

---

## Tóm tắt 3 điểm thiết kế quan trọng nhất

1. **Dual-head CORAL + CLS:** kết hợp ordinal regression (giữ thứ tự nguy cơ) với
   classification thường, average xác suất lúc predict — tốt hơn dùng riêng từng cái cho
   bài toán có thứ tự.

2. **Hierarchical:** post-level encoder (RoBERTa) → user-level sequence transformer +
   attention pooling — mô hình hóa được cả nội dung từng post lẫn diễn biến qua nhiều post.

3. **Gold-holdout đánh giá:** train trên nhãn-LLM nhưng đo trên nhãn lâm sàng giữ riêng
   → tránh đánh giá circular, cho con số đáng tin để báo cáo trong thesis.

---

## Cách chạy

```bash
# Local smoke test (CPU, vài giây)
R2_SMOKE=1 R2_MODEL=prajjwal1/bert-tiny .venv-voice/bin/python \
    notebooks/r2-suicide-risk-dualhead.py

# Kaggle: upload làm script kernel, bật GPU + Internet ON, run.
# Khi trên Kaggle, Run B preset (gold-holdout + balance + 10 epochs) tự bật.
```
