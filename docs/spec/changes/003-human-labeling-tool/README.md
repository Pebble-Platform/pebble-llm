# Change 003 — Human-labeling tool (FastAPI + state.jsonl)

**Status:** in progress — phase 0–3 + 5 done (seam + label/state.jsonl + recut/text + progress/reject + split/speaker); phase 4 chưa build
**Goal:** thực thi pivot [ADR-003](../../decisions/ADR-003-human-labels-drop-weak-supervision.md)
— biến `tools/labeler/` thành **công cụ label chính**: con người gán nhãn của
record cho từng clip (teacher chỉ gợi ý mờ), lưu vào **một file trạng thái
`state.jsonl`**, export ra Kaggle để train. Kèm 3 tính năng
([SPEC-features.md](../../../../tools/labeler/SPEC-features.md)): F1 recut+edit
text, F2 progress, F3 reject.
**Spec nguồn:** [`tools/labeler/SPEC.md`](../../../../tools/labeler/SPEC.md) (tool
hiện tại) + [`SPEC-features.md`](../../../../tools/labeler/SPEC-features.md) (đích).
**ADR liên quan:** ADR-003 (pivot), ADR-002 (test-split whole-series),
ADR-001 (superseded).

**Ordering principle:** seam trước — kiến trúc client-server + đường đọc
(backend serve clip, frontend fetch) phải chạy trước mọi tính năng ghi; rồi lõi
label + `state.jsonl` (hợp đồng dữ liệu, nguồn sự thật) trước các thao tác phá
huỷ (recut/reject); downstream export + I4 test cuối, sau khi có dữ liệu thật để
assert.

| Phase | File | Goal | Status |
|---|---|---|---|
| 0 | [phase-0-backend-seam.md](phase-0-backend-seam.md) | FastAPI (.venv-vnser) + đường đọc `/episodes /episode /clip`; frontend đổi File→fetch | **done** (API verified; chưa browser-drive) |
| 1 | [phase-1-labeling-state.md](phase-1-labeling-state.md) | Lõi human-label + `state.jsonl` nguồn sự thật; teacher = gợi ý mờ, no pre-fill; annotator field | **done** (E2E verified; chưa browser-drive) |
| 2 | [phase-2-recut-text.md](phase-2-recut-text.md) | F1: recut server-side (`soundfile`) + backup `_orig/` + Undo + edit `gold_text` | **done** (E2E verified; chưa browser-drive) |
| 3 | [phase-3-progress-reject.md](phase-3-progress-reject.md) | F2 progress% từ state; F3 reject-flag trong state (giữ file) | **done** (E2E verified; chưa browser-drive) |
| 4 | [phase-4-export-invariants.md](phase-4-export-invariants.md) | Export gold.csv/zip; `build_kaggle_dataset.py` dùng nhãn human + loại rejected + strip text public + loại test-series; test I4 | not started |
| 5 | [phase-5-split-speaker.md](phase-5-split-speaker.md) | F5 split (chia clip → 2 con **id seg mới = max+1/+2**, cha **giữ+reject** reason `split`, undo) + **F6 speaker sửa được** (dropdown/tập + `＋ mới`); con label riêng (speaker+script+emotion) | **done** (E2E verified; chưa browser-drive) |

Khi mỗi phase ship, cập nhật `capabilities/extraction-pipeline.md` cho khớp.
Execution rules: [WORKFLOW.md](../../../../WORKFLOW.md).

## Judgment calls (đảo bằng cách sửa phase file)

1. **Seam-first, không feature-first.** Migrate File→FastAPI (phase 0) trước mọi
   F1–F3, vì cả 3 tính năng đều cần ghi đĩa; build tính năng trên nền read-only
   cũ sẽ phải làm lại.
2. **`state.jsonl` là hợp đồng, chốt sớm (phase 1).** Mọi phase sau đọc/ghi nó;
   định hình schema trước khi recut/reject/export bám vào.
3. **I4 test ở phase 4, phối hợp với change `001-invariant-suite`.** Test
   `test_speaker_disjoint.py` thuộc 001; ở đây chỉ cần đủ dữ liệu (`state.jsonl`
   mang `series/ep/speaker`) để 001 assert được — không nhân đôi test.
4. ~~**Giữ `cut.html`** như trang phụ~~ — **đảo bởi [change 004](../004-labeler-refactor/README.md):** `cut.html` retire (stale + trùng lặp; F5 split phủ nhu cầu).

## Cross-phase open decisions (resolved → ADR ở ../../decisions/)

1. **Series nào làm test set** (ADR-002 scope) — *người quyết*; P1 3-series có chừa
   1 series khỏi train không. Chặn phase 4 (loại test-series khỏi export).
2. ~~gold_text release~~ — **RESOLVED**: local + Kaggle-private để train, **public
   CC-BY strip text** (intent §1). Phase 4.
3. ~~backup trước recut~~ — **RESOLVED**: bật mặc định + Undo (ADR-none, quyết
   2026-07-07). Phase 2.
4. ~~reject ở đâu~~ — **RESOLVED**: trong `state.jsonl` (1 file trạng thái). Phase 3.
5. **Số annotator + κ** — single-pass giai đoạn này (ADR-003); double-annotate
   một subset để có κ human–human là *further work*, chưa thuộc change này.
6. **Corpus-size mục tiêu** — *người quyết* (hand-label tuyến tính; ~3611 utt
   hiện có). Không chặn code, nhưng chặn "đủ để báo per-class UAR" (ADR-002 sàn ≥50/lớp).
