# docs/spec/changes — units of work

Mỗi đơn vị công việc / vòng thí nghiệm = một folder `NNN-<slug>/` (bất biến sau
khi ship). Đánh số lại từ 001 sau pivot 2026-07-04 (chuỗi cũ của thesis nằm ở
`archive/docs/spec/changes/`).

Change đã tạo:
- [`003-human-labeling-tool/`](003-human-labeling-tool/README.md) — công cụ
  human-labeling (FastAPI + `state.jsonl`) thực thi pivot [ADR-003](../decisions/ADR-003-human-labels-drop-weak-supervision.md):
  nhãn người là nguồn sự thật, teacher chỉ gợi ý; F1 recut+text, F2 progress,
  F3 reject; export Kaggle + I4 test-split.

Ứng viên change còn lại (theo thứ tự):
- `001-invariant-suite/` — dựng `tests/invariants/` mirror I1–I6 mới
  (`docs/intent/invariants.md`) + gắn vào CI.
- `002-scale-batch-1/` — chạy bộ phim đầu tiên qua kernel Kaggle: chốt GPU-h/tập
  thật, yield/tập trên mẫu lớn.
- ~~`003-gold-protocol`~~ — reframe thành `003-human-labeling-tool` sau ADR-003
  (bỏ weak-supervision; "gold pilot" → "human labeling toàn bộ").
