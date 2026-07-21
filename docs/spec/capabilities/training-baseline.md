# Capability — Training baseline (speech-only SER probe trên ViEmoSpeech)

> Spec layer / **state**: mô tả ĐÚNG những gì kernel train làm HÔM NAY, với số đo.
> Thay đổi hành vi/kết quả ⇒ cập nhật file này trong cùng PR (WORKFLOW rule 5).
> Cập nhật lần cuối: 2026-07-06 (change `004-vnser-training`, dataset 2-series).

## Hành vi hiện tại

`kaggle/vietnamese-ser/vnser-train/vnser-train.py` (self-contained, Kaggle P100)
+ `scripts/vietnamese-ser/make_splits.py` (split builder local, test I4):

1. Nạp `manifest.csv` từ dataset `phatneurondai/viemospeech-pilot`, giữ row
   `is_clean == True` (I3). Không xuất audio (I1).
2. **Frozen WavLM-Large** (đóng băng) → embedding masked-mean 1024-d/clip, cache `.npz`.
3. Ba **linear probe head** (chỉ train head, backbone giữ nguyên):
   - emotion 5-class (neutral/anger/joy/fear_anxiety/sadness; surprise/disgust bỏ vì
     thưa) — weighted-CE + sample-weight `conf_min`.
   - affect valence/arousal — CCC loss.
   - distress — BCE (mechanics, nhãn proxy).
4. **Hai cách đánh giá out-of-fold:**
   - **A — GroupKFold(ep,speaker)** 5-fold: gộp cả 2 series; `speaker` là nhãn
     pyannote cục-bộ-theo-tập và cast lặp trong 1 series → rò rỉ danh tính
     within-series → số **lạc quan**.
   - **B — Leave-one-series-out**: train 1 show, test show kia; 2 show khác dàn diễn
     viên → **cross-cast, speaker-disjoint danh tính THẬT** (I4) → số **trung thực**.
5. Report gắn cờ **SILVER** (nhãn 2-teacher, chưa human gold); provenance qua
   `config.json` (backbone id, seed, split_hash, pip pin) + `metrics.json` (I5).

## Số đo hiện hành (dataset 2-series, 3338 clean, nguồn: `expected-results.md` Run 2)

| Head | Metric | A: GroupKFold (lạc quan) | B: cross-series (THẬT) |
|---|---|---|---|
| emotion 5-class | macro-F1 | 0.413 [0.391, 0.435] | **0.333 [0.313, 0.354]** |
| affect | CCC valence | 0.111 | 0.075 |
| affect | CCC arousal | 0.152 | 0.131 |
| distress | AUC | 0.736 (n_pos=127) | 0.717 |

- Baseline "luôn neutral" ≈ 0.13 macro-F1 → cả A và B đều vượt chance rõ.
- **A→B gap ~0.08** = lượng rò rỉ danh tính within-series thổi phồng A.
- Con số **0.333 cross-cast** là baseline-to-beat trung thực cho tầng bimodal.

## Biên đã biết (không phải bug)

- **Silver, không phải headline:** nhãn weak 2-teacher; claim accuracy vẫn cần
  human gold (change `003-gold-protocol`). κ 2-teacher không bao giờ báo như accuracy (I6).
- **Affect gần sàn** ở cả 2 eval dù 4× dữ liệu → giới hạn của audio-một-mình về
  valence (target teacher-mean phương sai hẹp) → động cơ cho nhánh text tone×emotion.
- **distress = proxy** trên phim diễn (intent §7); 127 dương đủ có tín hiệu nhưng
  chưa nhãn lâm sàng.
- **Backbone English-centric** (WavLM-Large) trên tiếng Việt — bake-off đa ngữ là
  câu hỏi mở, chưa chạy.
