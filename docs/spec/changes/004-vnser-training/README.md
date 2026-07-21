# 004 — vnser-training: SER baseline speech-only trên ViEmoSpeech (Kaggle)

- **Status:** shipped (2026-07-06)
- **Created:** 2026-07-04 · **Owner:** user / Claude
- **Depends on:** 001 (invariant suite — cung cấp `tests/invariants/`), 002
  (scale-batch — sinh weak pool đủ lớn + `speaker_id`). Giả định làm việc của
  change này: **dataset đã tồn tại** (weak pool 2-teacher, chưa có human gold).

## Dataset thật (đã mở rộng — đo 2026-07-06, `phatneurondai/viemospeech-pilot`)

**2 series khác dàn diễn viên** — ve-nha-di-con (10 tập) + chay-tron-thanh-xuan
(22 phần) · **3611 utt · 3338 `is_clean` · 2422 clean+consensus**. `manifest.csv`
(cột: `ep,id,clip,start,end,dur,speaker,text_phowhisper,text_youtube,
emotion_{opus,sonnet,consensus},valence_mean,arousal_mean,distress_or,
multi_speaker_or,conf_min,is_clean`) + `clips/<series>_<ep>_segNNNNN.wav` 16kHz.
Emotion consensus (clean): neutral 1233 · anger 451 · joy 392 · sadness 199 ·
fear_anxiety 106 · **disgust 26 · surprise 15** (→ bỏ 2 lớp thưa, train **5-class**).
Distress 127 dương (mechanics). Vẫn **silver** (nhãn weak 2-teacher) — headline cần
human gold — nhưng **2 series cho phép eval cross-cast speaker-disjoint THẬT** (I4).

> **Lịch sử:** Run 1 (2026-07-05) chạy trên bản 1-series/822-clip — chi tiết +
> đối chiếu dự đoán ở [`expected-results.md`](expected-results.md).

## Goal

Train **model SER speech-only đầu tiên** trên corpus ViEmoSpeech và đo baseline
**silver** (weak-pool held-out theo speaker) cho 3 head: emotion 7 lớp,
valence/arousal, distress. Backbone **WavLM-Large đóng băng**, chỉ train heads.
Đây là bậc thang #1 — thiết lập cơ chế + baseline để tầng bimodal (speech+text,
tone×emotion) so delta sau, và để cắm human gold holdout vào khi có.

**KHÔNG phải** headline number. Mọi số báo cáo là silver trên weak pool; câu
accuracy/F1 thật chờ gold holdout (I6).

## Intent constraints file này chạm

| Inv | Vai trò trong change này |
|---|---|
| **I1** | ⚠ Dataset thật (`phatneurondai/viemospeech-pilot`) chứa **clips wav thô** (private), KHÔNG feature-only như dự kiến ban đầu — media đã nằm trên Kaggle. Chấp nhận cho pilot (private + user tự upload), nhưng rủi ro bên-thứ-ba đã nêu ở `05-scale-plan §rủi ro` VẪN áp dụng khi scale; artifact release CC-BY vẫn phải là feature-only. Kernel train KHÔNG xuất audio ra output. |
| **I3** | Chỉ nạp row `is_clean == True` (single-speaker theo cả 2 cửa: diarization turn-cut + không OR-flag `multi_speaker_or`). 3338/3611 clean. Change này *tiêu thụ* I3, không sửa. |
| **I4** | Kernel chạy **2 eval**: (A) `GroupKFold(ep,speaker)` gộp 2 series — `speaker` là nhãn pyannote cục-bộ-theo-tập + cast lặp within-series → rò rỉ danh tính → **lạc quan**; (B) **Leave-one-series-out** — 2 show khác cast → **cross-cast, speaker-disjoint danh tính THẬT**. Test `test_speaker_disjoint.py` kiểm group-disjoint (ep,speaker) cho builder local. Con số trung thực = eval B (0.333 macro-F1). |
| **I5** | Kernel pin `torch==2.5.1+cu121` (+ torchvision 0.20.1, transformers 4.46.3 cho P100); mọi số ghi `report.md`/`metrics.json` do script sinh; `config.json` mang model_id + seed + split-hash + pip pin. |
| **I6** | Report gọi kết quả là **weak-pool silver**, đặt tên rõ; không có dòng nào trình κ 2-teacher như accuracy. |

## Capability delta

- **ADDED:** `docs/spec/capabilities/training-baseline.md` — capability mới "train
  probe heads trên WavLM features + đo silver metrics". Viết ở thì hiện tại khi
  change ship (WORKFLOW rule 5).
- **MODIFIED:** không sửa `extraction-pipeline.md` (pipeline không đổi).

## Non-goals (đẩy sang change sau)

- Bimodal fusion speech+text / PhoBERT / tone×emotion (bậc thang #2).
- Human gold annotation + headline eval (change `003-gold-protocol`).
- Fine-tune backbone (giữ frozen — non-goal như voice stream).
