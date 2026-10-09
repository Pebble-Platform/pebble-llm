## ADR-006 — Train và benchmark trên 5 lớp emotion; corpus vẫn giữ nhãn disgust / surprise

**Date:** 2026-10-03 · **Status:** accepted (quyết định owner 2026-10-03: *"chốt lại chỉ
giữ 5 lớp thôi"*; phạm vi chọn qua 3 câu hỏi: chỉ train/benchmark · giữ nguyên 185 clip
cũ, loại khi train · labeler không đổi).
**Resolves:** câu §4.3 của `docs/tasks/handoff-2026-10-03.md` ("Benchmark 5 lớp?").
**Tầng:** spec (phương pháp đánh giá). Không đụng intent: invariants I1–I6 không nhắc số lớp.

## Context

Taxonomy gán nhãn có 7 lớp: neutral · anger · joy · sadness · fear_anxiety · disgust ·
surprise. Hai lớp cuối yếu ở cả phía người lẫn phía model:

| Lớp | κ người (one-vs-rest, vòng mù 014) | F1 model, eval B (cross-series, 7 lớp) | Số clip |
|---|--:|--:|--:|
| disgust | 0.107 | 0.070 | 103 |
| surprise | 0.326 | 0.092 | 82 |
| (5 lớp còn lại) | 0.38 – 0.64 | 0.12 – 0.48 | 1139 |

Người soát mù chỉ gán disgust 4 lần trong 28 clip mà owner gán disgust. Ở eval B, disgust
học được trong cùng series nhưng không mang sang series khác (run 6 lớp: F1 A 0.218, B 0.048).

## Decision

1. **Train và benchmark dùng 5 lớp:** neutral · anger · joy · sadness · fear_anxiety. Kernel
   `vnser-train` (chế độ baseline) bỏ clip disgust/surprise rồi train và chấm trên 5 lớp.
2. **Corpus giữ nguyên nhãn:** không sửa `state.db`. 103 clip disgust và 82 clip surprise
   vẫn mang nhãn gốc; `build_kaggle_gold.py` vẫn xuất đủ 7 nhãn, kernel tự lọc. Đổi ý sau
   này không mất dữ liệu.
3. **Labeler không đổi:** form gán nhãn, `gold.html`, `rate.html` vẫn 7 lựa chọn. Người gán
   vẫn ghi disgust/surprise khi nghe thấy; các clip đó không vào train.
4. **Chế độ ablation 012 không đổi:** nó đã đông cứng với 7 lớp; kernel chỉ lọc 5 lớp ở
   chế độ baseline.

## Evidence

- Run Kaggle `vnser-train-5cls` (1139 clip, tập clip v7): A 0.428, **B 0.351** macro-F1.
  `docs/reports/baseline-1324-5cls/`.
- So công bằng (cùng clip, cùng tập lớp) thì 5 lớp **không** làm model tốt hơn đáng kể:
  phần thật +0.028 (`docs/reports/baseline-1324/class-subset.json`), +0.004 / +0.013 theo
  change 015 (`docs/reports/015/classset.md`). κ model / κ người giữ ~0.37 ở 7, 6 và 5 lớp.
- Lý do chọn là **độ tin cậy của nhãn**, không phải accuracy: κ người 0.513 (7 lớp) →
  0.621 (5 lớp, đo trên clip mà không ai chọn lớp bị bỏ, nên hơi thổi lên).

## Consequences

- **Quyết định được đưa ra sau khi đã thấy kết quả khám phá** (015 câu 3, các run 5/6 lớp
  của baseline-1324). Phải nói rõ điều này trong paper; không trình bày 5 lớp như một
  thiết kế định trước.
- **Không so macro-F1 5 lớp với số 7 lớp cũ** (0.256 v7, 0.249 v6, ablation 012). Mốc
  ngẫu nhiên khác (UAR 0.20 so với 0.14); phần lớn chênh lệch là cơ học. Số 7 lớp giữ lại
  như lịch sử.
- **Số mốc cho change 013 / 016 phải đo lại trên 5 lớp.** 0.296 của change 015 (chọn tầng
  WavLM) là số 7 lớp.
- **Ngoài phạm vi corpus:** clip ghê tởm/ngạc nhiên vẫn xuất hiện khi dùng thật; model 5 lớp
  buộc phải xếp chúng vào một trong 5 lớp. Benchmark không đo hành vi này.
- Tốn công gán nhãn cho clip không dùng để train (~14% clip sạch hiện tại). Owner chấp nhận
  để giữ labeler ổn định giữa các vòng soát.
- κ người–người (`gold_review_kappa.py`, `iaa_report.py`) vẫn tính trên 7 lớp vì labeler
  vẫn 7 lớp; κ 5 lớp là số phụ.
