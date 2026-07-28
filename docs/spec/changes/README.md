# docs/spec/changes — units of work

Mỗi đơn vị công việc / vòng thí nghiệm = một folder `NNN-<slug>/` (bất biến sau
khi ship). Đánh số lại từ 001 sau pivot 2026-07-04 (chuỗi cũ của thesis nằm ở
`archive/docs/spec/changes/`).

Change đã tạo:
- [`003-human-labeling-tool/`](003-human-labeling-tool/README.md) — công cụ
  human-labeling (FastAPI + `state.jsonl`) thực thi pivot [ADR-003](../decisions/ADR-003-human-labels-drop-weak-supervision.md):
  nhãn người là nguồn sự thật, teacher chỉ gợi ý; F1 recut+text, F2 progress,
  F3 reject; export Kaggle + I4 test-split.
- [`004-vnser-training/`](004-vnser-training/README.md) — **shipped (2026-07-06)**:
  SER baseline speech-only (frozen WavLM-Large + 3 head) trên ViEmoSpeech 2-series.
  Eval cross-cast (leave-one-series-out) = **macro-F1 0.333** speaker-disjoint thật
  (silver). Capability: `capabilities/training-baseline.md`. Bậc thang #1 trước bimodal.

- [`011-online-multi-annotator/`](011-online-multi-annotator/README.md) —
  **in-progress (2026-07-28)**: tool label online đa annotator để lấy **κ/α
  human–human** (nợ đã biết của [ADR-003](../decisions/ADR-003-human-labels-drop-weak-supervision.md)).
  Cho phép bởi [ADR-005](../decisions/ADR-005-annotation-streaming-not-release.md)
  (stream cho annotator mời đích danh ≠ release, 7 safeguard). M1 xong: hướng dẫn
  annotator + consent + **QC protocol pre-registered**. Annotator chỉ label clip đã
  cắt — không cắt/chia.

Ứng viên change còn lại (theo thứ tự):
- `001-invariant-suite/` — dựng `tests/invariants/` mirror I1–I6 mới
  (`docs/intent/invariants.md`) + gắn vào CI.
- `002-scale-batch-1/` — chạy bộ phim đầu tiên qua kernel Kaggle: chốt GPU-h/tập
  thật, yield/tập trên mẫu lớn, và κ ổn định theo tập.
- ~~`003-gold-protocol`~~ — reframe thành `003-human-labeling-tool` sau ADR-003
  (bỏ weak-supervision; "gold pilot" → "human labeling toàn bộ").
