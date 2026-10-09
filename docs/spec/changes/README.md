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

- [`012-label-quality-ablation/`](012-label-quality-ablation/README.md) — **xong
  (2026-09-02)**: ablation pre-registered đo xem **dọn nhãn có làm model tốt lên
  không**, dùng vòng review của rater thứ 2 (1.071 clip). 4 nhánh nhãn trên cùng clip/
  fold/feature, chấm trên cùng 606 clip nhãn cố định. Kết quả: Δ(B−A) = **+0.024, CI
  [−0.011, +0.056] ⇒ H0** (10/10 seed dương nhưng thiếu power); lọc theo đồng thuận
  **không** có lợi. Capability: `capabilities/training-baseline.md`.
- [`013-bimodal-tone-emotion/`](013-bimodal-tone-emotion/README.md) — **draft
  (2026-09-03), chỉ đặt vấn đề**: tầng method tone×emotion của paper. Động cơ đo được:
  **CCC valence 0.071** ở LOSO — audio một mình không đọc được cực tính. 4 câu hỏi thiết
  kế chờ owner (nguồn thanh điệu lúc inference · nhãn thanh điệu ở đâu ra · kiến trúc
  fusion · ngưỡng pre-register). Chặn bởi κ (011) + series test (ADR-002) + đủ gold utt.

- [`014-blind-gold-review/`](014-blind-gold-review/README.md) — **implemented
  (2026-09-11)**: bỏ neo nhãn ở màn soát `gold.html` — người soát tự chọn emotion (7 lựa
  chọn hiện sẵn, không pre-fill); nhãn owner **và** V/A chỉ lộ ra sau khi họ chốt, chặn ở
  server chứ không giấu bằng CSS; metadata giữ readonly nhưng sửa được. Vá nợ đã ghi ở
  [012](012-label-quality-ablation/README.md) ("vòng review bị neo") và khôi phục điều (1)
  của [ADR-001](../decisions/ADR-001-blind-gold-annotation.md) ("không pre-fill").

- [`015-emotion-acoustic-features/`](015-emotion-acoustic-features/README.md) — **xong
  (2026-09-28)**, pre-registered: đặc trưng âm học nào mang cảm xúc (eGeMAPS 88) và cảm
  xúc nằm ở layer nào của WavLM (probe 25 layer). H1a–c đều đúng: F0/loudness ↔ arousal
  ρ≈0.55; valence yếu hơn nhiều; jitter giữ ρ −0.18 với valence kể cả sau khi kiểm soát
  arousal. **Layer chọn trong fold thắng layer 24: Δ +0.035 [+0.014, +0.056]**, nên
  baseline nên đổi feature. Capability: `capabilities/training-baseline.md`.

- [`016-labeler-segment-page/`](016-labeler-segment-page/README.md) — **xong
  (2026-10-03)**: "✂ cắt thủ công" từ popup thành trang riêng `segment.html`. Click 1
  block script thì tải thêm block liền trước và liền sau; kéo trên sóng để chọn vùng làm
  clip; `＋ đoạn trước/sau` thay cho nút chỉnh mép ±0.2s. Không đổi backend. Spec:
  `tools/labeler/SPEC.md`.

- [`017-tone-checker/`](017-tone-checker/README.md) — **xong (2026-10-09)**: công cụ đo
  thanh điệu từng âm tiết (chấm CTC từng thanh trên wav2vec2-vi, không mô hình ngôn ngữ),
  phục vụ số đo sai thanh bắt buộc của pivot lồng tiếng. Trên giọng thật: chính xác
  **0.956** (ngẫu nhiên 0.198), phát hiện thanh sai **0.991**; báo nhầm tăng từ neutral
  0.023 lên anger 0.066, nguyên nhân chưa tách được. Capability:
  `capabilities/tone-checker.md`.

Ứng viên change còn lại (theo thứ tự):
- `001-invariant-suite/` — dựng `tests/invariants/` mirror I1–I6 mới
  (`docs/intent/invariants.md`) + gắn vào CI.
- `002-scale-batch-1/` — chạy bộ phim đầu tiên qua kernel Kaggle: chốt GPU-h/tập
  thật, yield/tập trên mẫu lớn, và κ ổn định theo tập.
- ~~`003-gold-protocol`~~ — reframe thành `003-human-labeling-tool` sau ADR-003
  (bỏ weak-supervision; "gold pilot" → "human labeling toàn bộ").
