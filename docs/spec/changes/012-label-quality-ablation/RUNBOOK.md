# Runbook — chạy ablation change 012

> **Cổng bắt buộc:** [`preregistration.md`](preregistration.md) phải được owner duyệt và
> **commit** trước khi chạy bước 3. Chạy trước khi đông cứng là tự bỏ mất ý nghĩa của
> việc pre-register.

## 1. Dựng tập clip cố định (local)

```
PYTHONIOENCODING=utf-8 .venv-vnser/Scripts/python.exe scripts/vietnamese-ser/build_kaggle_gold.py \
    --slug viemospeech-ablation-012 \
    --keys docs/spec/changes/011-online-multi-annotator/review-candidates.tsv \
    --reviews data/vietnamese-ser/episodes/gold-reviews/vyphan.json
```

Kỳ vọng: `utterances=1071  clips=1071  skipped_off_queue=122  reviewed=1071`.
`--slug` riêng để **không đè** dataset pilot đang dùng cho baseline.

⚠️ Đọc `state.db` — không ghi, nhưng vẫn nên **tắt server labeler** cho chắc.

## 2. Đẩy dataset (private)

Thêm `--push` vào lệnh trên. Dataset là clip từ phim có bản quyền → **private, không
bao giờ public** (intent §1).

## 3. Đẩy + chạy kernel

Kernel dùng **chung một file** với `vnser-train` (một nguồn sự thật trong git); bản
copy trong thư mục kernel là artifact, đã gitignore:

```
cp kaggle/vietnamese-ser/vnser-train/vnser-train.py kaggle/vietnamese-ser/vnser-ablation-012/
uvx --from kaggle kaggle kernels push -p kaggle/vietnamese-ser/vnser-ablation-012
```

Script **tự nhận chế độ** từ manifest: có cột `emotion_reviewed` ⇒ chạy ablation
(kernel script trên Kaggle không nhận biến môi trường). Log dòng đầu phải là
`mode=ablation (change 012)`.

## 4. Lấy kết quả

```
uvx --from kaggle kaggle kernels output phatneurondai/vnser-ablation-012 -p docs/reports/012/
```

Ra `ablation.md` + `metrics_ablation.json`. Cột **verdict** đã áp sẵn quy tắc §7 —
đọc đúng như nó ghi, không diễn giải lại.

## Chạy thử local (không cần GPU, không tải WavLM)

`VNSER_ABLATION=1 VNSER_SEEDS=0,1 VNSER_INPUT=<stage> VNSER_OUTPUT=<tmp>` với
`extract_features` bị thay bằng feature giả — chỉ kiểm tra đường ống, **số vô nghĩa**.
