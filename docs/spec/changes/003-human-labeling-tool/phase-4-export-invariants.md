# Phase 4 — Export Kaggle + downstream + invariants

**Status:** not started
**Depends on:** phase 1–3 (`state.jsonl` đầy đủ: nhãn + recut + reject)

**Goal:** dựng artifact train từ `state.jsonl`, cập nhật `build_kaggle_dataset.py`
theo pivot (nhãn human, loại rejected, strip text ở bản public, loại test-series),
và cấp dữ liệu để test I4 (`test speakers ∩ train = ∅`) assert được.

## Scope

- **In:** `GET /export/gold.csv` · `/export/gold.zip` — view dựng từ `state.jsonl`
  (clip đã nhãn, bỏ rejected). `build_kaggle_dataset.py`: đọc `state.jsonl`, dùng
  **nhãn human** làm nhãn train (không còn teacher-consensus), **loại `(ep,id)`
  rejected**, **loại series test** khỏi train (ADR-002), giữ `text`/`gold_text`
  cho **Kaggle-private**, và một chế độ **public: strip mọi cột text** (intent §1).
- **Out:** dựng chính `tests/invariants/test_speaker_disjoint.py` (thuộc change
  `001-invariant-suite`) — ở đây chỉ đảm bảo dữ liệu đủ field để nó chạy.

## Exit criteria

- `gold.csv` export chứa đúng clip đã-nhãn-không-reject, có `series/ep/speaker`
  + nhãn human; `gold.zip` kèm wav (media, local-only).
- `build_kaggle_dataset.py` (chế độ public) **không có cột text nào**; chế độ
  Kaggle-private có `gold_text`; cả hai **loại** rejected + test-series.
- Chạy được một assert `(series,ep,speaker)` của test ∩ train = ∅ trên
  `state.jsonl` + manifest train (dù test chính thức nằm ở change 001).

## Verification

| # | Intent | Check | Where |
|---|---|---|---|
| 1 | Public strip text (I1/§1) | `git`-facing/public manifest: 0 cột text; grep fail nếu có | test + report-lint |
| 2 | Loại rejected & test-series | Export không chứa `(ep,id)` rejected, không speaker của series test | unit test trên fixture |
| 3 | Nhãn human, không teacher (ADR-003) | Cột nhãn train = từ `state.jsonl` human; không lấy `labels_{opus,sonnet}` làm nhãn | code review + test |
| 4 | Speaker-disjoint (I4) | `(series,ep,speaker)` test ∩ train = ∅ | test (phối hợp change 001) |

## Review notes

- **Hai đích export khác nhau** (dễ nhầm): **Kaggle-private để train** (có text,
  clip) vs **public CC-BY** (features + timestamps + labels + speaker id, **no
  text, no audio**). gold_text chỉ vào cái đầu.
- **Chặn của người:** chưa chốt **series nào là test** → chưa loại đúng khỏi train.
  Không chốt thì export train có thể dính speaker test (vỡ I4). Đây là blocker
  scope, không phải code (open decision #1 ở README).
- `build_kaggle_dataset.py` hiện tính `is_clean` + `teacher-consensus` — phase này
  **thay** logic nhãn sang human; giữ `is_clean` (single-speaker gate I3) nhưng
  bỏ nhánh coi teacher là nhãn.
