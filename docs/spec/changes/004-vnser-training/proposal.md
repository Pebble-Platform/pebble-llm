# Proposal — 004 vnser-training

## Requirements

### R1 — Hợp đồng dataset (thật: clips + manifest, 2 series)
Dataset `phatneurondai/viemospeech-pilot` (private) gồm `manifest.csv` +
`clips/<series>_<ep>_segNNNNN.wav` (16kHz mono); **2 series khác cast** (ve-nha-di-con,
chay-tron-thanh-xuan), 3338 clean. Kernel nạp:
- Chỉ row `is_clean == True` (I3). Emotion head thêm điều kiện `emotion_consensus`
  ∈ 5 lớp (bỏ surprise/disgust thưa).
- Feature: **trích on-the-fly bằng frozen WavLM-Large trong chính kernel train**
  (3338 clip → ~15' P100; cache `.npz` vào `/kaggle/working`). KHÔNG cần dataset
  feature riêng, KHÔNG cần kernel precompute tách rời.
- I1: media (clips) đã nằm trên Kaggle private — kernel KHÔNG xuất audio ra
  output; artifact release CC-BY (bước sau) vẫn phải feature-only.

### R2 — Splits & 2 eval (I4)
- `scripts/vietnamese-ser/make_splits.py`: `GroupKFold` 5-fold theo group
  `(ep, speaker)`, deterministic (seed logged). Test `test_speaker_disjoint.py`
  kiểm group-disjoint (không unit nào ở 2 fold).
- Kernel chạy **2 eval out-of-fold**:
  - **A — GroupKFold(ep,speaker)** gộp 2 series: `speaker` cục-bộ-theo-tập + cast
    lặp within-series → rò rỉ danh tính → **lạc quan**.
  - **B — Leave-one-series-out**: train 1 show, test show kia → **cross-cast,
    speaker-disjoint danh tính THẬT**; đây là con số trung thực.
- Report ghi cả A và B + gap A→B (lượng leak within-series).

### R3 — Model (speech-only, frozen)
```
frozen WavLM-Large → masked-mean pool (A/B attentive-statistics [paper 02])
  → emotion head : Linear→5   (weighted-CE; sample-weight = conf_min)
  → affect head  : Linear→2   (CCC loss trên valence_mean,arousal_mean — 3338 row)
  → distress head: Linear→1   (BCE; mechanics-only — 127 dương, không báo P@R thật)
```
- 5 lớp emotion = neutral/anger/joy/fear_anxiety/sadness (bỏ surprise+disgust thưa).
- Chỉ train heads. `conf_min` → sample weight, KHÔNG phải target.
- Loss tổng = Σ head; log riêng từng head. n≈2381 (5-class) → probe nông, regularize.

### R4 — Kernel training
- `kaggle/vietnamese-ser/vnser-train/`: imports/pin → manifest + series + GroupKFold
  → trích WavLM feature (cache) → `cv_metrics()` gọi 2 lần (GroupKFold + LOSO) →
  report 2 bảng.
- `kernel-metadata.json`: `enable_gpu:true`, `is_private:true`,
  `dataset_sources:[phatneurondai/viemospeech-pilot]`, pin `torch==2.5.1+cu121` (I5).
- Session < 1h (frozen-probe, 3338 clip ~15' feature).

### R5 — Báo cáo (I5, I6)
`out/report.md` + `metrics.json` + `artifact_wavlm-large/config.json`:
- **2 bảng metric:** Eval A (GroupKFold, lạc quan) + Eval B (LOSO, cross-cast thật)
  — emotion macro-F1 (5-class), CCC(V)/CCC(A), distress AUC. Kèm **95% CI bootstrap**.
- Banner gắn nhãn **"pilot silver — chưa human gold"**; eval B là số speaker-disjoint
  thật, eval A ghi rõ lạc quan do leak within-series.
- `config.json`: model_id backbone, seed, split-hash, pip pin, cả 2 metrics.
- Anchor (không apples-to-apples): emotion ~34/33 macro-F1 MSP-Podcast [paper 02].

## Capability delta

| Loại | Capability | Nội dung |
|---|---|---|
| ADDED | `capabilities/training-baseline.md` | Train probe heads trên WavLM features, splits speaker-disjoint, silver metrics + provenance. Viết khi ship. |

## Rủi ro / judgment calls

- **[giải quyết] Speaker-disjoint (I4):** dataset giờ có 2 series khác cast →
  eval B (LOSO) là speaker-disjoint danh tính THẬT (0.333 macro-F1). Eval A
  (GroupKFold) vẫn lạc quan do leak within-series — giữ để đo gap A→B, ghi rõ.
- **[trung bình] Silver, chưa gold:** nhãn weak 2-teacher → không phải headline
  accuracy; cần human gold (change 003). Mất cân bằng ~9:1 → weighted-CE + CI.
  distress 127 dương: có tín hiệu nhưng vẫn mechanics.
- **[mở] Affect gần sàn:** CCC V/A thấp ở cả 2 eval dù 4× dữ liệu → giới hạn
  audio-một-mình về valence; động cơ cho nhánh text (tầng bimodal), không block.
- **Backbone English-centric trên tiếng Việt:** WavLM-Large pretrain chủ yếu EN.
  Chấp nhận cho baseline #1; bake-off đa ngữ (XLS-R/PhoWhisper-encoder) là câu hỏi
  mở, ghi report, không block.
- **Silver ≠ accuracy (I6):** chống bằng nhãn bắt buộc mọi bảng + report-lint.
- **Media clips trên Kaggle (I1):** dataset pilot có audio thô (private); chấp nhận
  cho pilot, nhưng scale phải chuyển feature-only theo `05-scale-plan §rủi ro`.
