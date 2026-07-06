# Giải thích code training — `vnser-train.py`

> Tài liệu đọc-hiểu cho kernel `kaggle/vietnamese-ser/vnser-train/vnser-train.py`
> (change 004). Mục tiêu: một người mới đọc hiểu **luồng dữ liệu, từng bộ phận,
> và vì sao thiết kế như vậy** — kèm liên hệ tới kết quả đã đo (2026-07-05).

## 1. Bức tranh tổng thể

Kernel là **một file self-contained** (không import từ repo — đúng pattern
`vnser-extract`) chạy trọn trên Kaggle GPU. Luồng 6 bước:

```
manifest.csv + clips/*.wav
      │
      ▼  (1) lọc is_clean → 822 clip
  assign_folds()            (2) GroupKFold(ep,speaker) → cột fold
      │
      ▼
  extract_features()        (3) frozen WavLM-Large → 1 vector 1024-d/clip (cache .npz)
      │
      ▼
  cv_metrics() × 2          (4) chạy 2 eval out-of-fold: A=GroupKFold(ep,speaker),
      │                          B=Leave-one-series-out (cross-cast). Mỗi fold:
      │                          chuẩn hoá → train 3 head trên train → dự đoán val.
      ▼
  macro_f1 / ccc / auc      (5) đo trên toàn bộ dự đoán OOF + bootstrap 95% CI
      │
      ▼
  write_report() + config   (6) report.md (2 bảng) · metrics.json · artifact/config.json
```

Ý tưởng chốt: **backbone đóng băng** → chỉ học 3 "đầu" tuyến tính nhỏ. Vì thế
feature chỉ cần trích **một lần** rồi cache; huấn luyện head cực nhanh (vài giây).

## 2. Hằng số & môi trường (dòng 41–69)

```python
EMOTIONS = ["neutral", "anger", "joy", "fear_anxiety", "sadness"]  # bỏ surprise/disgust (n=2)
BACKBONE = "microsoft/wavlm-large"
N_SPLITS = 5
SEED = 0
GROUP_COLS = ("ep", "speaker")
```

- **`EMOTIONS` chỉ 5 lớp:** surprise/disgust mỗi lớp chỉ 2 mẫu → không train/eval
  được, bỏ hẳn (quyết định đã chốt).
- **`PIP_PINS`** ghim stack tương thích P100 (sm_60). Ba pin này là kết quả **3 lần
  fix lỗi môi trường Kaggle**, mỗi comment trong code giải thích tại sao:
  - `torch==2.5.1` — image mặc định không chạy trên P100.
  - `torchvision==0.20.1` — bạn đồng hành của torch 2.5.1; nếu để bản Kaggle (cho
    torch 2.10) thì `transformers` import torchvision sẽ chết `torchvision::nms`.
  - `transformers==4.46.3` — bản mới chặn `torch.load` khi torch<2.6 (CVE), mà
    `wavlm-large` là checkpoint `.bin` → phải dùng bản cũ hơn guard đó.

`_pip_install()` chỉ chạy **trên Kaggle** (`ON_KAGGLE and not SMOKE`); local smoke
dùng deps sẵn trong `.venv-voice`.

## 3. Trích đặc trưng — `extract_features()` (dòng 73–108)

```python
fe = AutoFeatureExtractor.from_pretrained(BACKBONE)
model = WavLMModel.from_pretrained(BACKBONE).to(device).eval()
...
inp = fe(wav, sampling_rate=16000, return_tensors="pt").input_values
hidden = model(inp).last_hidden_state          # [1, T, 1024]  T = số frame
emb = hidden.mean(dim=1).squeeze(0)            # [1024]  = masked-mean pool
```

- Đọc từng clip wav (16kHz), đưa qua WavLM-Large **đóng băng** (`eval()` +
  `torch.no_grad()` → không tính gradient, không cập nhật backbone).
- `last_hidden_state` là chuỗi vector theo thời gian `[T, 1024]`; **masked-mean
  pool** = trung bình theo trục thời gian → **1 vector 1024 chiều/clip**. Đây là
  cách gộp đơn giản nhất (mỗi clip đã cắt gọn 1 giọng nên không cần mask padding).
- **Cache `.npz`:** nếu file cache tồn tại thì nạp lại thay vì tính lại → chạy lần
  2 chỉ mất vài giây (đã kiểm chứng: "cache hit"). Đây là điểm resumable.

> Vì sao trích một-clip-một-lần (không batch)? 822 clip là rất nhỏ; làm tuần tự
> tránh phải pad + mask khi batch, đổi lại chỉ tốn ~vài phút GPU.

## 4. Chia fold — `assign_folds()` (dòng 112–123)

```python
sizes = manifest.groupby(["ep","speaker"]).size()      # kích thước mỗi nhóm giọng
order = sorted(sizes.index, key=lambda g: (-sizes[g], g))  # nhóm to trước, tie-break theo tên
for g in order:
    f = min(range(n_splits), key=lambda i: (load[i], i))   # bỏ vào fold đang nhẹ nhất
    gf[g] = f; load[f] += sizes[g]
```

Đây là **GroupKFold tự viết** (không cần sklearn — giữ dep tối thiểu như repo):

- **Đơn vị chia = `(ep, speaker)`**, KHÔNG phải từng clip. Vì nhãn `speaker` của
  pyannote là **cục bộ theo tập** (SPEAKER_07 ở ep01 ≠ ep02), nên khoá nhóm phải
  kèm `ep`.
- **Tham lam cân bằng:** nhóm nhiều clip nhất được xếp trước, luôn bỏ vào fold
  đang ít clip nhất → 5 fold gần đều (thực tế 164–165 clip/fold).
- **Deterministic:** không random, tie-break bằng tên nhóm → chạy lại cho **cùng
  split_hash**. (Hàm này là bản sao của `scripts/vietnamese-ser/make_splits.py`;
  hash trùng khít giữa 2 bên đã xác nhận chúng đồng nhất.)

> ⚠ Đây là I4 **best-effort**, không phải speaker-disjoint thật: cùng diễn viên
> tái xuất xuyên tập dưới nhãn khác → danh tính vẫn rò rỉ. Vì thế mọi số là silver.

## 5. Ba đầu học + hàm huấn luyện — `_train_linear()` (dòng 127–163)

Mỗi head là **một lớp `Linear(1024 → out)`** (linear probe), huấn luyện full-batch
bằng Adam. `task` quyết định số đầu ra + hàm loss:

| Head | `task` | out | Loss | Ghi chú |
|---|---|---|---|---|
| emotion | `cls` | 5 | CrossEntropy **có class-weight** | thêm **sample-weight = `conf_min`** (nhãn confidence thấp bị nhẹ đi) |
| affect | `reg2` | 2 | **CCC loss** (`_ccc_loss`) | hồi quy valence & arousal cùng lúc |
| distress | `bin` | 1 | BCE **có `pos_weight`** | bù mất cân bằng 21 dương / 801 âm |

Chi tiết đáng chú ý:
- **`class_w`** (dòng 253–254) = nghịch đảo tần suất lớp → lớp hiếm (sadness) được
  loss coi trọng hơn, chống việc model chỉ đoán "neutral".
- **`sample_w = conf_min`** = độ tin cậy tối thiểu của 2 teacher cho clip đó → nhãn
  mơ hồ đóng góp ít. Đây là cách "honest weak supervision" đưa độ tin vào training.
- **`_ccc_loss`** tối ưu trực tiếp **1 − CCC** (Concordance Correlation Coefficient)
  — đúng metric dùng để đo, thay vì MSE.

## 6. Vòng cross-validation — `cv_metrics()` (gọi 2 lần)

> Hàm nhận một mảng `folds` bất kỳ và chạy vòng OOF. `main()` gọi nó **2 lần**:
> lần 1 với fold GroupKFold(ep,speaker) (eval A, within-pool), lần 2 với fold =
> chỉ số series (eval B, leave-one-series-out cross-cast). Cùng logic, khác cách chia.

```python
for f in range(N_SPLITS):
    tr, va = folds != f, folds == f          # train = 4 fold, val = fold f
    mu, sd = X[tr].mean(0), X[tr].std(0)+1e-6 # chuẩn hoá theo THỐNG KÊ TRAIN
    Xtr, Xva = (X[tr]-mu)/sd, (X[va]-mu)/sd
    ... train 3 head trên Xtr, dự đoán Xva → lưu vào mảng OOF ...
```

- **Out-of-fold (OOF):** mỗi clip được dự đoán đúng **một lần**, bởi model **không
  thấy** fold chứa nó khi train. Gom hết dự đoán OOF rồi mới tính metric → đánh giá
  chéo trung thực, không rò rỉ train↔val (trong giới hạn I4 đã nêu).
- **Chuẩn hoá bằng thống kê train** (mu/sd của fold train, áp lên cả val) — tránh
  rò rỉ thông tin val vào bước chuẩn hoá.
- **Emotion chỉ train trên tập con 5-lớp** (`emo_label >= 0`); affect & distress
  train trên toàn bộ 822 clean. Mỗi head có tập mẫu riêng.

## 7. Đo lường — `macro_f1` / `ccc` / `auc` / `bootstrap_ci` (dòng 177–222)

Tất cả **tự implement bằng numpy** (không sklearn):
- **`macro_f1`** — F1 trung bình đều các lớp (không thiên vị lớp đông neutral).
- **`ccc`** — tương quan concordance cho V/A.
- **`auc`** — qua công thức Mann–Whitney U (thứ hạng), tránh dep ngoài.
- **`bootstrap_ci`** — lấy mẫu lại 1000 lần → khoảng tin cậy 95%. Vì n nhỏ, **CI là
  bắt buộc** để không báo một điểm số đơn lẻ gây hiểu nhầm chắc chắn.

## 8. Provenance & báo cáo — `main()` + `write_report()` (dòng 295–387)

- **`split_hash`** = MD5 của toàn bộ cặp `(clip, fold)` → dấu vân tay của cách chia,
  cho phép kiểm định lặp lại và đối chiếu với `make_splits.py`.
- **`config.json`** ghi: backbone, seed, `split_hash`, `pip_pins`, số clip, và
  toàn bộ metrics → mọi số trong report truy được về đây (I5 provenance).
- **`report.md`** luôn mở đầu bằng **banner cảnh báo silver** (I6): "NOT true
  speaker-disjoint, NOT a headline" — không thể vô tình đọc số như accuracy thật.
- **Không ghi file `.wav` nào ra output** → tôn trọng I1 (không phát tán media).

## 9. Chế độ smoke (test local trước khi push)

`VNSER_SMOKE=1` → chỉ 48 clip đầu, 40 epoch, bỏ pip install, đọc dữ liệu từ
`VNSER_INPUT`. Dùng để kiểm **cơ chế** trên CPU (`.venv-voice`) trước khi tốn GPU
quota — chính nhờ smoke mà logic train đã xanh trước khi 3 lỗi môi trường Kaggle
lộ ra (và đều là môi trường, không phải logic).

## 10. Nối với kết quả đã đo (Run 2, dataset 2-series, 2026-07-06)

| Head | Eval A (GroupKFold, lạc quan) | Eval B (cross-cast, THẬT) | Vì sao (theo code) |
|---|---|---|---|
| emotion macro-F1 | 0.413 | **0.333** | class-weight + sample-weight vượt baseline "luôn neutral" (~0.13); gap A→B = leak danh tính within-series |
| CCC valence / arousal | 0.111 / 0.152 | 0.075 / 0.131 | gần sàn ở cả 2 eval dù 4× dữ liệu → vấn đề **target V/A** / audio yếu về valence, KHÔNG phải lỗi feature |
| distress AUC | 0.736 | 0.717 | `pos_weight` cho head chạy; 127 dương → có tín hiệu nhưng vẫn mechanics |

Chi tiết đầy đủ + đối chiếu dự đoán (Run 1 & 2): [`expected-results.md`](expected-results.md).
