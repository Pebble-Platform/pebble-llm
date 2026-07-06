# docs/spec/changes — units of work

Mỗi đơn vị công việc / vòng thí nghiệm = một folder `NNN-<slug>/` (bất biến sau
khi ship). Đánh số lại từ 001 sau pivot 2026-07-04 (chuỗi cũ của thesis nằm ở
`archive/docs/spec/changes/`).

Ứng viên change tiếp theo (theo thứ tự):
- `001-invariant-suite/` — dựng `tests/invariants/` mirror I1–I6 mới
  (`docs/intent/invariants.md`) + gắn vào CI.
- `002-scale-batch-1/` — chạy bộ phim đầu tiên qua kernel Kaggle: chốt GPU-h/tập
  thật, yield/tập trên mẫu lớn, và κ ổn định theo tập.
- `003-gold-protocol/` — pilot annotation 200 utt (design doc §5): guideline,
  κ người-người, disagreement-sampling từ weak pool.
- `004-vnser-training/` — **shipped (2026-07-06)**: SER baseline speech-only
  (frozen WavLM-Large + 3 head) trên ViEmoSpeech 2-series. Eval cross-cast
  (leave-one-series-out) = **macro-F1 0.333** speaker-disjoint thật (silver).
  Capability: `capabilities/training-baseline.md`. Bậc thang #1 trước bimodal.
