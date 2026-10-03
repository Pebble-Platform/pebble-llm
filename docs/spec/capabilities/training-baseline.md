# Capability — Training baseline (speech-only SER probe trên ViEmoSpeech)

> Spec layer / **state**: mô tả ĐÚNG những gì kernel train làm HÔM NAY, với số đo.
> Thay đổi hành vi/kết quả ⇒ cập nhật file này trong cùng PR (WORKFLOW rule 5).
> Cập nhật lần cuối: 2026-07-22 (chuyển sang **nhãn NGƯỜI**, ADR-003; run 750 clip).
>
> **Pivot 2026-07-22 (ADR-003):** kernel giờ train trên **nhãn người** (state.db qua
> `build_kaggle_gold.py`), KHÔNG còn consensus 2-teacher. Số "silver 3338 clip / 5-class
> / distress" của run trước là **lịch sử tiền-pivot** (giữ ở `expected-results.md`).

## Hành vi hiện tại

`kaggle/vietnamese-ser/vnser-train/vnser-train.py` (self-contained, Kaggle P100):

1. Nạp `manifest.csv` (dataset `phatneurondai/viemospeech-pilot`, dựng bởi
   `build_kaggle_gold.py`): 750 clip **nhãn người sạch** (có `emotion`, không rejected,
   không multi — I3). Không xuất audio (I1).
2. **Frozen WavLM-Large** (đóng băng) → embedding masked-mean 1024-d/clip, cache `.npz`.
3. Hai **linear probe head** (chỉ train head, backbone giữ nguyên):
   - emotion **7-class** (đủ cả surprise/disgust — cả 2 series đều có support) —
     weighted-CE theo tần suất lớp, không sample-weight (nhãn người, không có teacher conf).
   - affect valence/arousal (1–5) — CCC loss.
   - *(distress bỏ: 750 clip sạch có 0 dương — form labeler đã bỏ distress 2026-07-10.)*
4. **Hai cách đánh giá out-of-fold:**
   - **A — GroupKFold(ep)** 5-fold theo tập: gộp cả 2 series; cast lặp trong 1 series
     → rò rỉ danh tính within-series → số **lạc quan**. (Không group theo `speaker`:
     diarization id thô chưa remap về nhân vật, không đáng tin.)
   - **B — Leave-one-series-out**: train 1 show, test show kia; 2 show khác dàn diễn
     viên → **cross-cast, speaker-disjoint danh tính THẬT** (I4/ADR-002) → số **trung thực**.
5. Report: **single human annotator** (chưa có κ người–người, gap ADR-003) → pilot,
   KHÔNG phải accuracy chốt (I6). Metric: macro-F1 headline + **UAR** (balanced accuracy,
   bền hơn ở lớp hiếm) + per-class support, kèm 95% CI. Provenance qua `config.json`
   (backbone id, seed, split_hash, pip pin, `label_source`) + `metrics.json` (I5).

## Số đo hiện hành (750 clip nhãn-người, seed 0, nguồn: kernel run `vnser-train` v6 2026-07-22)

| Head | Metric | A: GroupKFold(ep) (lạc quan) | B: cross-series (THẬT) |
|---|---|---|---|
| emotion 7-class | macro-F1 | 0.314 [0.278, 0.348] | **0.249 [0.218, 0.277]** |
| emotion 7-class | UAR | 0.319 [0.281, 0.357] | 0.247 [0.216, 0.278] |
| affect | CCC valence | 0.116 [0.093, 0.141] | 0.091 [0.067, 0.114] |
| affect | CCC arousal | 0.132 [0.115, 0.150] | 0.087 [0.072, 0.101] |

- Class counts (full 750): neutral 203 · anger 156 · joy 146 · fear_anxiety 76 ·
  sadness 67 · disgust 63 · surprise 39. Chance macro-F1 7-class ≈ 0.04 (luôn-neutral) →
  cả A và B vượt chance rõ.
- **A→B gap ~0.065 macro-F1** = lượng rò rỉ danh tính within-series thổi phồng A.
- Con số **0.249 cross-cast** là baseline-to-beat trung thực cho tầng bimodal (thấp hơn
  0.333 silver-5-class cũ: khác cả nhãn [người vs teacher], số lớp [7 vs 5], và cỡ [750 vs 3338]).

## Biên đã biết (không phải bug)

- **Single-annotator, chưa có κ:** nhãn người 1 lượt (ADR-003 gap); là pilot, chưa
  headline accuracy. Cần lượt gán thứ 2 để có κ người–người (I6).
- **Lớp hiếm support nhỏ ở LOSO:** surprise 39 / disgust 63 tổng → 1 test-split có thể
  <15 mẫu → đọc theo CI, không point value (research 2026-07-22).
- **Affect gần sàn** (CCC 0.09–0.13) ở cả 2 eval → giới hạn của audio-một-mình về
  valence → động cơ cho nhánh text tone×emotion.
- **Backbone English-centric** (WavLM-Large) trên tiếng Việt — bake-off đa ngữ là
  câu hỏi mở, chưa chạy.
