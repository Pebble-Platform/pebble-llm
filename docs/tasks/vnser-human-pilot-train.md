# Kaggle pilot: train SER baseline on the 750 human-labeled ViEmoSpeech clips

- **Slug:** vnser-human-pilot-train
- **Status:** done
- **Created:** 2026-07-22  ·  **Updated:** 2026-07-22
- **Owner:** user (away 30′) / Claude (autonomous)

## Goal
Chạy **thử nghiệm training đầu tiên trên nhãn NGƯỜI** (ADR-003) cho ViEmoSpeech:
750 clip sạch (có `emotion` người gán, không rejected, không multi) → train baseline
SER (frozen WavLM-Large probe) trên Kaggle P100, báo cáo macro-F1 emotion + CCC
valence/arousal, với **hai eval**: within-pool (lạc quan) và leave-one-series-out
(honest, speaker-disjoint theo I4/ADR-002). Kết quả = `metrics.json` + `report.md`
tải về từ Kaggle.

## Requirements & Constraints
- **Functional:** manifest nhãn-người (state.db) → dataset Kaggle PRIVATE → kernel
  training → run P100 → pull metrics.
- **Constraints:**
  - **I1 media legality:** clip là media bản quyền → dataset Kaggle **PRIVATE mãi mãi**,
    không bao giờ public (đã theo pattern `viemospeech-pilot`).
  - **ADR-003:** nhãn của record = **người**; teacher chỉ là cột gợi ý, KHÔNG train/eval.
  - **I4 / ADR-002:** split speaker-disjoint = **held-out whole-series** → honest eval =
    leave-one-series-out (2 show không chung diễn viên).
  - **I6:** mọi số phải nêu rõ test set speaker-disjoint; nhãn hiện là **single
    annotator** (chưa có κ người–người, gap ADR-003) → nói thẳng trong report, KHÔNG
    gọi là accuracy chốt hạ.
  - **I5:** số truy được về report do script sinh; kernel P100 pin stack (torch 2.5.1).
  - Kaggle P100 = sm_60 → pin `torch==2.5.1+cu121` ([[kaggle-neobert-stack]]);
    drive headless qua CLI ([[kaggle-cli-automation]]).

## Milestones
- [x] M1 — Manifest nhãn-người 750 clip — `build_kaggle_gold.py` loại `multi` (750/750, 0 skip)
- [x] M2 — Kernel `vnser-train.py` đọc schema nhãn-người (7-class emotion + V/A, bỏ distress, +UAR)
- [x] M3 — Smoke test local CPU (60 clip, exit 0, report render đúng) trước khi push
- [x] M4 — Push dataset PRIVATE v (750 clip) + push kernel v6 → run P100 kích hoạt
- [x] M5 — Run COMPLETE (P100, 750 clip); pull metrics + ghi số vào doc + capability

## Decision Log
<!-- newest first -->
- **2026-07-22 — Bug push kaggle CLI trên Windows + workaround:** `datasets version`
  với `-p` nhiều tầng (`data/.../viemospeech-pilot`) làm CLI dựng path temp hỏng
  (`uploads\data/.../viemospeech-pilot_manifest.csv.json`, thiếu thư mục trung gian)
  → `clips.zip` lên được nhưng `manifest.csv` `[Errno 2] No such file`. Fix: chạy từ
  thư mục cha với `-p viemospeech-pilot` (một tầng) → OK. Đã vá `build_kaggle_gold.py`
  dùng `cwd=stage.parent` + `-p SLUG`. Rejected: đổi TEMP (không phải gốc lỗi).
- **2026-07-22 — Metrics: macro-F1 headline + UAR phụ + CCC:** research xác nhận
  MSP-Podcast/Odyssey-2024 rank theo macro-F1; UAR (balanced accuracy) rẻ, bền hơn khi
  lớp hiếm bị 0 prediction → thêm UAR. Rejected: chỉ macro-F1 (kém bền ở lớp <15 mẫu).
  (see Research 2026-07-22)
- **2026-07-22 — Frozen WavLM-Large probe + weighted-CE (không focal, không finetune):**
  research xác nhận đúng chuẩn SUPERB/Odyssey ở n nhỏ; finetune 300M param trên 750 clip
  = overfit + tốn P100 vô ích; focal-loss bất ổn ở n nhỏ + nhãn single-annotator nhiễu.
  (see Research 2026-07-22)
- **2026-07-22 — Bỏ head distress:** 750 clean có **0 distress-positive** (distress bỏ
  khỏi form labeler 2026-07-10). Head BCE không học được gì. Rejected: giữ mechanics-only
  (vô nghĩa khi 0 positive).
- **2026-07-22 — Emotion 7-class (không drop surprise/disgust):** cả 2 series đều có đủ
  7 lớp (ve-nha: surprise 10 / disgust 14; chay-tron: 29 / 49). Đủ để LOSO có support ở
  cả 2 phía. Kernel teacher-era drop 2 lớp vì hiếm — nay giữ, báo per-class support +
  macro-F1 (không average-out lớp hiếm). Rejected: 5-class (mất 2 lớp có thật).
- **2026-07-22 — Bỏ trọng số `conf_min`:** đó là confidence 2-teacher (teacher-era).
  Nhãn người không có → weighted-CE theo tần suất lớp, sample-weight đồng nhất.
- **2026-07-22 — Split: eval A = GroupKFold theo `epKey` (5 fold); eval B = LOSO theo
  series:** `speaker` là diarization id thô, chưa remap về nhân vật → không tin được để
  group. Group theo tập tránh leak trong-tập; LOSO theo series = honest speaker-disjoint
  (ADR-002). Gap A→B = mức lạc quan do cast tái xuất trong-series. Rejected: GroupKFold
  (ep,speaker) như kernel cũ (speaker id không đáng tin).

## Open Questions
- [x] ~~Best practice baseline SER low-resource~~ → RESOLVED (Research 2026-07-22):
  kế hoạch draft ĐÚNG. Frozen WavLM-Large masked-mean + linear probe, weighted-CE,
  macro-F1 headline + UAR phụ, CCC cho V/A, eval A GroupKFold(ep) + eval B LOSO.
  2 bổ sung: (1) thêm UAR [đã làm], (2) report phải nêu bằng lời các lớp có <15 mẫu
  test là "chỉ tham khảo, không so sánh được".

## Research Findings
<!-- task-researcher output pasted verbatim -->

### Research 2026-07-22 — Best-practice frozen-SSL-probe baseline + honest cross-domain eval (750-clip, 7-class, 2-domain VN SER)
- **Confidence:** high (model/pooling & metric), medium (focal-loss/macro-F1-at-small-n = general-ML, not SER-specific).
- **Short answer:** Plan correct as stated — frozen WavLM-Large + masked-mean pool + linear/shallow probe, weighted-CE (not focal), macro-F1 (+per-class F1/support) headline + UAR secondary, CCC for V/A, eval A within-pool GroupKFold + eval B leave-one-series-out. Re-confirms existing repo pattern.
- **Options considered:** frozen probe (SUPERB-style, stable at n=750) vs partial finetune WavLM-Large (SOTA e.g. Wagner CCC .638 but on ~100k+ utt; at 750 = catastrophic overfit + burns P100 → reject); masked-mean vs attentive/STD pooling (top Odyssey-2024 use stat/attentive pooling, but extra trainable params unwanted at n=750 → keep masked-mean, attentive only as optional ablation); macro-F1 (MSP-Podcast/Odyssey ranking metric) vs UAR (IEMOCAP-era) → report both, headline macro-F1; weighted-CE vs focal vs oversampling → weighted-CE standard + stable at small n, focal's difficulty-reweighting destabilizes on small + noisy(single-annotator) labels.
- **Recommendation:** keep plan + 2 additions: (1) add UAR alongside macro-F1; (2) in report prose, flag any per-class metric from <15 test-fold samples (surprise=39/disgust=63 total → likely <15 in one LOSO split) as "indicative, not comparable".
- **Risks:** SER-specific pooling/metric evidence from web-search summaries not full PDFs; focal-loss/macro-F1-instability claims are general-ML priors, not SER-lit. Revisit frozen-probe call if n grows past ~few thousand (then finetune worth it).
- **Sources:** MSP-Podcast SER Challenge 2024 (arXiv:2407.05746); Dawn of Transformer Era in SER, Wagner et al. (arXiv:2203.07378); Adapting WavLM for SER, Odyssey 2024 (isca-archive diatlova24); Focal Loss vs BCE (marktechpost 2025-11); Macro-F1 instability at low support (emergentmind). Repo: benchmark/{metrics,train_eval}.py, vnser-train.py, training-baseline.md.

## Completed Work
- 2026-07-22 — Khảo sát trạng thái: 1119 record, **750 clean** (emotion người + không
  reject + không multi). Phân bố emotion (clean): neutral 203 · anger 156 · joy 146 ·
  fear_anxiety 76 · sadness 67 · disgust 63 · surprise 39. Per-series đều đủ 7 lớp.
  V/A đủ 750; distress 0. Clip có trên đĩa. Auth Kaggle OK (ACCESS_TOKEN); dataset
  `phatneurondai/viemospeech-pilot` tồn tại (đang là manifest teacher cũ).

- 2026-07-22 — M1: `build_kaggle_gold.py` loại thêm `multi` (I3) → manifest 750 clip
  (`utterances=750 clips=750 skipped_no_wav=0`). Cột: ep,id,clip,start,end,dur,
  emotion,valence,arousal,gold_text,opus_suggest,sonnet_suggest,annotator,ts.
- 2026-07-22 — M2: viết lại `kaggle/vietnamese-ser/vnser-train/vnser-train.py` cho
  nhãn-người: 7-class emotion (weighted-CE), V/A CCC, BỎ distress (0 positive), BỎ
  conf_min weight, group theo `ep`, +UAR + per-class support, ngôn ngữ report =
  single-annotator (I6). Lint pass.
- 2026-07-22 — M3: smoke local CPU (60 clip, WavLM cache local) exit 0, report render
  đúng cả 2 eval (số vô nghĩa ở n=60, chỉ để validate pipeline).
- 2026-07-22 — M4: dataset PRIVATE version 750-clip đã push (clips.zip 62MB +
  manifest.csv 177KB); kernel `vnser-train` version 6 pushed → run P100. Vá bug push
  Windows trong `build_kaggle_gold.py` (cwd=parent, `-p SLUG`). Lint pass.

- 2026-07-22 — M5: kernel run v6 COMPLETE trên P100 (750 clip). **Kết quả pilot
  (nhãn người, seed 0):**

  | Eval | emotion macro-F1 | UAR | CCC-V | CCC-A |
  |---|---|---|---|---|
  | A GroupKFold(ep) — lạc quan | 0.314 [.278–.348] | 0.319 | 0.116 | 0.132 |
  | **B LOSO — honest speaker-disjoint** | **0.249 [.218–.277]** | 0.247 | 0.091 | 0.087 |

  A→B gap ~0.065 macro-F1 = rò danh tính within-series. Affect gần sàn (CCC .09–.13)
  → động cơ nhánh text tone×emotion. Đã cập nhật `docs/spec/capabilities/training-baseline.md`.
  Output: `scratchpad/vnser_kaggle_out/` (report.md, metrics.json, config.json, features.npz).

## Remaining Action Items (follow-up, ngoài phạm vi pilot này)
- [ ] Lượt gán nhãn thứ 2 để có κ người–người (ADR-003 gap) — điều kiện để lên headline.
- [ ] (tùy chọn) ablation attentive-stat pooling; bake-off backbone đa ngữ (research follow-up).
