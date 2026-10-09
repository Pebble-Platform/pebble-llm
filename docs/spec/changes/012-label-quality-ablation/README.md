# Change 012 — Ablation chất lượng nhãn (vòng review vyphan → Kaggle)

**Status:** **xong 2026-09-02** — kernel `vnser-ablation-012` v1 chạy hết; kết quả ở
`docs/reports/012/ablation.md`, tóm tắt trong
[`training-baseline.md`](../../capabilities/training-baseline.md). Verdict: **H0**.
**Goal:** trả lời một câu hỏi vận hành: **dọn nhãn có làm model tốt lên không?**
Tức là bỏ thêm công annotate có đáng không — trước khi cam kết vòng label mù đầy đủ.
**Điều kiện có được:** vòng review của `vyphan` (2026-08-06 → 2026-08-14) đã xong
1071/1071 clip, tạo ra **hai bộ nhãn trên cùng một tập clip** — thứ trước giờ chưa có.

## Vì sao là ablation, không phải baseline mới

`docs/spec/capabilities/training-baseline.md` đang ghi macro-F1 cross-series
**0.249** trên **750** clip. Tập clip ở đây là **1071** → số không so trực tiếp được.
Nhánh baseline phải chạy lại đúng cỡ tập. Change này **không** cập nhật headline
accuracy (I6 vẫn đòi vòng mù); nó chỉ đo **delta giữa các bộ nhãn**.

## Văn bản của change này

| File | Việc |
|---|---|
| [`preregistration.md`](preregistration.md) | Giao thức + **quy tắc quyết định**, pre-registered — phải đông cứng trước khi chạy Kaggle. |

## Phạm vi

**Trong:** 4 nhánh nhãn trên cùng 1071 clip · cùng embedding WavLM đã đóng băng ·
cùng fold · cùng seed · chấm trên một tập test nhãn cố định.

**Ngoài:** đổi backbone, đổi head, thêm nhánh text/tone, mở rộng corpus. Không đụng
`state.db` — kết quả review **chưa** được merge vào corpus ở change này (adjudicate
là việc riêng, sau khi có số).

## Nợ đã biết trước khi chạy

- Vòng review **bị neo**: vyphan thấy nhãn owner trước khi trả lời → nhánh B không
  phải "ý kiến thứ hai độc lập", mà là "owner + 465 lần phân xử". Ablation này hợp lệ
  với cách hiểu đó, và **không** sinh ra κ human–human.
- **122 clip** đã label sau 2026-08-06 không nằm trong queue review → để ngoài cả 4
  nhánh, giữ các nhánh so được với nhau.
- Không script nào đọc `gold-reviews/*.json` (`iaa_report.py` đọc bảng `assignments`,
  đang rỗng). Change này thêm đường đọc đầu tiên, qua `build_kaggle_gold.py`.
