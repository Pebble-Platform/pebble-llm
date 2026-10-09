# Capability — Training baseline (speech-only SER probe trên ViEmoSpeech)

> Spec layer / **state**: mô tả ĐÚNG những gì kernel train làm HÔM NAY, với số đo.
> Thay đổi hành vi/kết quả ⇒ cập nhật file này trong cùng PR (WORKFLOW rule 5).
> Cập nhật lần cuối: 2026-10-03 (ADR-006: baseline train/chấm 5 lớp; v8).
>
> **Pivot 2026-07-22 (ADR-003):** kernel giờ train trên **nhãn người** (state.db qua
> `build_kaggle_gold.py`), KHÔNG còn consensus 2-teacher. Số "silver 3338 clip / 5-class
> / distress" của run trước là **lịch sử tiền-pivot** (giữ ở `expected-results.md`).

## Hành vi hiện tại

`kaggle/vietnamese-ser/vnser-train/vnser-train.py` (self-contained, Kaggle P100):

1. Nạp `manifest.csv` (dataset `phatneurondai/viemospeech-pilot`, dựng bởi
   `build_kaggle_gold.py`): 1324 clip **nhãn người sạch** (có `emotion`, không rejected,
   không multi — I3), manifest giữ **đủ 7 nhãn**. Ở chế độ baseline, kernel bỏ clip
   disgust/surprise (**ADR-006**) → 1139 clip. Không xuất audio (I1).
2. **Frozen WavLM-Large** (đóng băng) → embedding masked-mean 1024-d/clip, cache `.npz`.
3. Hai **linear probe head** (chỉ train head, backbone giữ nguyên):
   - emotion **5-class** (neutral · anger · joy · sadness · fear_anxiety; ADR-006 — labeler
     và corpus vẫn 7 lớp, chế độ ablation 012 vẫn 7 lớp) — weighted-CE theo tần suất lớp,
     không sample-weight (nhãn người, không có teacher conf).
   - affect valence/arousal (1–5) — CCC loss.
   - *(distress bỏ: 750 clip sạch có 0 dương — form labeler đã bỏ distress 2026-07-10.)*
4. **Hai cách đánh giá out-of-fold:**
   - **A — GroupKFold(ep)** 5-fold theo tập: gộp cả 2 series; cast lặp trong 1 series
     → rò rỉ danh tính within-series → số **lạc quan**. (Không group theo `speaker`:
     diarization id thô chưa remap về nhân vật, không đáng tin.)
   - **B — Leave-one-series-out**: train 1 show, test show kia; 2 show khác dàn diễn
     viên → **cross-cast, speaker-disjoint danh tính THẬT** (I4/ADR-002) → số **trung thực**.
5. Report: nhãn train **single human annotator** (κ người–người mới có trên mẫu 343 clip,
   change 014) → pilot,
   KHÔNG phải accuracy chốt (I6). Metric: macro-F1 headline + **UAR** (balanced accuracy,
   bền hơn ở lớp hiếm) + per-class support, kèm 95% CI. Provenance qua `config.json`
   (backbone id, seed, split_hash, pip pin, `label_source`) + `metrics.json` (I5).

## Số đo hiện hành (5 lớp, 1139 clip, seed 0, nguồn: kernel run `vnser-train` v8 2026-10-03, `docs/reports/baseline-5cls-v8/report.md`)

| Head | Metric | A: GroupKFold(ep) (lạc quan) | B: cross-series (THẬT) |
|---|---|---|---|
| emotion 5-class | macro-F1 | 0.428 [0.397, 0.455] | **0.351 [0.324, 0.375]** |
| emotion 5-class | UAR | 0.432 [0.402, 0.460] | 0.351 [0.324, 0.376] |
| affect | CCC valence | 0.147 [0.127, 0.166] | 0.092 [0.072, 0.112] |
| affect | CCC arousal | 0.162 [0.147, 0.177] | 0.101 [0.090, 0.112] |

- Class counts: neutral 367 · anger 251 · joy 234 · sadness 156 · fear_anxiety 131. Series:
  chay-tron-thanh-xuan 899 · ve-nha-di-con 240. Chance: UAR 0.20, luôn-neutral macro-F1 0.097.
- Trùng khít với run `vnser-train-5cls` (cùng split_hash `f6dd5730…`, cùng metrics.json):
  dataset pilot trên Kaggle vẫn là bản 1324 clip của v7, kernel tự lọc còn 1139.
- **0.351 là baseline-to-beat mới** cho change 013/016. **Không so với số 7 lớp bên dưới**
  (ADR-006): phần lớn chênh lệch là cơ học, so công bằng thì 5 lớp chỉ hơn ~0.03.

### Lịch sử: 7 lớp, 1324 clip (kernel run `vnser-train` v7 2026-09-27, `docs/reports/baseline-1324/report.md`)

| Head | Metric | A: GroupKFold(ep) (lạc quan) | B: cross-series (THẬT) |
|---|---|---|---|
| emotion 7-class | macro-F1 | 0.356 [0.330, 0.380] | **0.256 [0.234, 0.277]** |
| emotion 7-class | UAR | 0.361 [0.334, 0.387] | 0.256 [0.236, 0.279] |
| affect | CCC valence | 0.134 [0.116, 0.153] | 0.080 [0.062, 0.100] |
| affect | CCC arousal | 0.164 [0.149, 0.177] | 0.094 [0.084, 0.105] |

- Class counts (full 1324): neutral 367 · anger 251 · joy 234 · sadness 156 ·
  fear_anxiety 131 · disgust 103 · surprise 82. Series: chay-tron-thanh-xuan 1060 ·
  ve-nha-di-con 264. Chance macro-F1 7-class ≈ 0.04 (luôn-neutral) → cả A và B vượt chance rõ.
- **So với run v6 (750 clip, 2026-07-22):** A 0.314 → 0.356, B 0.249 → 0.256. Thêm nhãn
  gần như chỉ nâng A; B đứng yên → **A→B gap nới từ ~0.065 lên ~0.100**.
- B gộp OOF của cả 2 chiều trên mọi clip, nên ~80% điểm B (1060 clip test) đến từ chiều
  **train trên ve-nha-di-con (264 clip)**. Cỡ series nhỏ hơn là trần của B; thêm nhãn cho
  series lớn không nâng được nó.
- Con số **0.256 cross-cast** từng là baseline-to-beat 7 lớp (trước ADR-006).

## Chế độ ablation (change 012, thêm 2026-09-02)

Cùng một kernel, chọn chế độ **theo manifest**: dataset có cột `emotion_reviewed` **có giá trị**
(dựng bởi `build_kaggle_gold.py --keys --reviews`) ⇒ chạy ablation thay vì baseline
(kernel script trên Kaggle không nhận biến môi trường; `VNSER_ABLATION=1` là cửa
local). Bốn nhánh nhãn trên **cùng 1071 clip · cùng fold · cùng embedding đã cache**,
tất cả chấm trên **cùng 606 clip nhãn cố định** (clip rater thứ 2 giữ nguyên) — chỉ
nhãn train thay đổi. Giao thức + quy tắc quyết định đông cứng trước khi chạy:
[change 012](../changes/012-label-quality-ablation/preregistration.md).

### Số đo (kernel `vnser-ablation-012` run v1, 2026-09-02, 10 seed)

macro-F1 emotion trên 606 clip test, eval leave-one-series-out (eval trung thực):

| Nhánh | train n | macro-F1 | 95% CI |
|---|--:|--:|---|
| A nhãn owner | 1071 | 0.258 | [0.226, 0.292] |
| B nhãn sau review | 1071 | 0.283 | [0.242, 0.321] |
| C chỉ clip đồng thuận | 606 | 0.279 | [0.239, 0.316] |
| C′ owner, khớp cỡ mẫu | 606 | 0.269 | [0.236, 0.304] |

- **Δ(B−A) = +0.024, CI [−0.011, +0.056]** → theo quy tắc §7 (CI chứa 0) = **H0**:
  chưa đủ bằng chứng rằng dọn nhãn cải thiện model. Nhưng **cả 10/10 seed đều dương**
  (khoảng [+0.019, +0.037]) — hướng nhất quán, khoảng tin cậy rộng vì tập test chỉ 606
  clip (surprise 32 · fear_anxiety 40). Đây là kết quả **thiếu power**, đúng như §6 đã
  cảnh báo trước khi chạy, **không** phải bằng chứng review vô ích.
- **GroupKFold ngược dấu**: Δ(B−A) = −0.005 (CI chứa 0). Hai eval không đồng thuận;
  §7 chốt trước là đọc trên LOSO.
- **Δ(C−C′) = +0.011 (LOSO) / −0.022 (GKF)**, CI đều chứa 0 → **không** có bằng chứng
  rằng lọc bỏ clip bất đồng có lợi. Đừng vứt 465 clip bất đồng.
- **CCC arousal** B > A ở cả hai eval (0.129 vs 0.114 LOSO; 0.186 vs 0.174 GKF) — arousal
  cũng là trường được sửa nhiều nhất (193/1071).
- Sanity: A ở đây (0.258, 1071 clip) khớp với baseline cũ (0.249, 750 clip).

## Layer của WavLM (change 015, 2026-09-28) — kernel CHƯA đổi

Kernel vẫn dùng `last_hidden_state` (layer 24). Change 015 (pre-registered) đo probe
cùng head trên đủ 25 layer, 1324 clip, 10 seed. Nguồn: `docs/reports/015/layer_probe.md`.

| Feature | LOSO macro-F1 | 95% CI | CCC val | CCC aro |
|---|--:|---|--:|--:|
| layer 24 (feature kernel đang dùng) | 0.261 | [0.237, 0.282] | 0.082 | 0.095 |
| layer chọn trong fold train (inner-CV) | 0.296 | [0.273, 0.319] | 0.117 | 0.116 |
| eGeMAPS-88 | 0.229 | [0.210, 0.248] | −0.001 | 0.071 |

- **Δ(chọn trong fold − 24) = +0.035, CI [+0.014, +0.056]**, cả 10 seed dương ⇒ theo §5
  của 015, **feature baseline nên đổi** (việc của một change riêng; số ở đầu file này vẫn
  là của kernel hiện hành).
- Layer được chọn: 16 khi train trên chay-tron-thanh-xuan (9/10 seed); dao động 8–23 khi
  train trên ve-nha-di-con (chỉ 3 tập, inner-CV nhiễu).
- Đường cong mô tả đạt đỉnh ở layer 11 (0.314), nhưng con số đó chọn bằng tập test, không
  dùng làm căn cứ.

## Chạy tập con lớp (thêm 2026-10-01)

Kernel lấy tập lớp = các lớp chuẩn **có mặt trong manifest**; dataset dựng bằng
`build_kaggle_gold.py --drop-emotions ...` ⇒ train + chấm đúng số lớp đó (không trộn
F1 = 0 của lớp vắng vào macro-F1). Kernel riêng `vnser-train-5cls`, dataset (đã xoá khỏi Kaggle 2026-10-03; dựng lại bằng `--keys` bên dưới)
`viemospeech-5cls` khoá vào đúng tập clip v7 (`docs/reports/baseline-1324/v7-clip-keys.tsv`).

**5 lớp (bỏ disgust + surprise), 1139 clip, seed 0** — nguồn `docs/reports/baseline-1324-5cls/report.md`:

| Metric | A: GroupKFold(ep) | B: cross-series |
|---|---|---|
| macro-F1 | 0.428 [0.397, 0.455] | **0.351 [0.324, 0.375]** |
| UAR | 0.432 [0.402, 0.460] | 0.351 [0.324, 0.376] |
| CCC valence | 0.147 | 0.092 |
| CCC arousal | 0.162 | 0.101 |

- **Không so thẳng với 0.256 của 7 lớp:** model 7 lớp chỉ lấy trung bình trên 5 lớp này
  đã đạt B = 0.330 (10 seed) → phần lớn mức tăng là cơ học. κ model↔nhãn (B, 10 seed):
  0.190 → 0.231, κ người 0.513 → 0.621 → tỷ lệ model/người giữ ~0.37. Nguồn:
  `docs/reports/baseline-1324/class-subset.json` (`class_subset_probe.py`).
- Chance 5 lớp: UAR 0.20 (7 lớp: 0.14); luôn-neutral macro-F1 0.097.

**6 lớp (chỉ bỏ surprise), 1242 clip, seed 0** — kernel `vnser-train-6cls`, dataset
`viemospeech-6cls` (khoá tập clip v7), nguồn `docs/reports/baseline-1324-6cls/report.md`:
A macro-F1 0.384 [0.357, 0.411] · **B macro-F1 0.288 [0.264, 0.312]** · B UAR 0.290 ·
B CCC V/A 0.087 / 0.097. Qua 10 seed: B 0.296, trong đó model 7 lớp tính trên 6 lớp đã
đạt 0.286 → phần thật chỉ **+0.010**; κ model/κ người 0.204/0.559 ≈ 0.36. Disgust ở B
chỉ F1 0.048 (7 lớp: 0.070). Chance 6 lớp: UAR 0.167, luôn-neutral macro-F1 0.076.

## Biên đã biết (không phải bug)

- **Ablation 012 thiếu power:** 606 clip test không phân giải nổi khác biệt ~0.02–0.03.
  Chỉ tập test lớn hơn (vòng label mù) mới chốt được Δ(B−A).
- **Vòng review bị neo:** rater thứ 2 thấy nhãn owner trước khi trả lời → nhánh B là
  "owner + 465 lần phân xử", **không** phải ý kiến độc lập, và **không** sinh ra κ.
- **Single-annotator; κ người–người mới có trên mẫu:** nhãn train vẫn là 1 lượt owner
  (ADR-003 gap) → pilot, chưa headline accuracy (I6). Vòng soát mù change 014
  (`nhinguyen`, 343 clip) cho **Cohen κ emotion owner↔mù = 0.513 [0.454, 0.572]**,
  trùng thô 60.1% (vòng có neo trên cùng clip: κ 0.765). Lớp yếu nhất: disgust κ 0.107
  (owner 28 · mù 4), surprise 0.326, fear_anxiety 0.377. Chỉ emotion là mù; V/A bị neo.
  Nguồn: `docs/reports/014/kappa.md` (`gold_review_kappa.py`).
- **Lớp hiếm support nhỏ ở LOSO:** surprise 39 / disgust 63 tổng → 1 test-split có thể
  <15 mẫu → đọc theo CI, không point value (research 2026-07-22).
- **Affect gần sàn** (CCC 0.08–0.16) ở cả 2 eval — **phần lớn là do head affect yếu, không
  chỉ do audio:** suy V/A từ emotion *dự đoán* (cùng audio, lấy trung bình V/A theo lớp ở
  fold train) cho CCC LOSO valence 0.162 / arousal 0.254, so với 0.080 / 0.094 của head hồi
  quy trực tiếp. Nhãn V/A không đụng tới head emotion (hai probe tách rời; F1 không đổi
  dưới mọi kiểu làm sai V/A trong mô phỏng). Nguồn: `docs/reports/baseline-1324/va-noise.json`
  (`va_label_noise.py`).
- **Head affect lệch thang (lỗi, chưa sửa):** dự đoán V/A của v9 có trung bình ~0.3 (nhãn
  2.75–3.21), độ lệch chuẩn ~2.4–2.9 (nhãn 0.8–0.9), **64–73% nằm ngoài thang 1–5** ở cả
  hai eval. Head hồi quy chưa hội tụ về đúng thang; sửa (chuẩn hoá target, thêm epoch
  hoặc suy từ emotion) cần một change riêng. Nguồn: `docs/reports/baseline-5cls-v9/predictions.csv`.
- **Backbone English-centric** (WavLM-Large) trên tiếng Việt — bake-off đa ngữ là
  câu hỏi mở, chưa chạy.
