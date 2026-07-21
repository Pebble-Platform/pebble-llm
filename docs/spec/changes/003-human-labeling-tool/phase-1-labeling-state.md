# Phase 1 — Lõi human-label + `state.jsonl`

**Status:** done (2026-07-07) — `GET/POST /gold` + `state.jsonl` (atomic
tmp→rename, load on startup); `/episodes` trả `done`, `/episode` trả `clip.gold`;
provenance (speaker/start/end/opus/sonnet/ts) điền server-side. Frontend: bỏ
localStorage + `suggest()` pre-fill, V/A placeholder `—` + guard, POST khi confirm,
teacher hiển thị read-only. **E2E verify** (fixture cô lập): POST→state.jsonl 1
dòng, done 0→1, restart reload đúng. **Chưa** browser-drive (verify API + syntax).
**Depends on:** phase 0 (đường đọc + response schema)

**Goal:** con người gán nhãn của record cho từng clip; nhãn lưu server-side vào
**`state.jsonl`** (nguồn sự thật duy nhất). Teacher chỉ là **gợi ý mờ, read-only,
KHÔNG pre-fill** (ADR-003). `annotator` là field trên request — hết localStorage.

## Scope

- **In:** `POST /gold/{epKey}/{id}` ghi record vào `state.jsonl` (atomic
  tmp→rename); mỗi record: `series, ep, id, speaker, start, end,
  emotion, valence, arousal, distress, multi, annotator, ts`. Frontend: bỏ
  pre-fill/pre-select (kể cả nhánh "2 teacher đồng thuận"); teacher hiện **mờ,
  read-only** bên cạnh, không nạp vào ô nhập; guard `!emotion` giữ nguyên. Field
  `annotator` ở header đi kèm mỗi POST.
- **Out:** recut/text (phase 2), progress%/reject (phase 3), export (phase 4).

## Exit criteria

- Gán nhãn 1 clip → `state.jsonl` có đúng 1 dòng cho `(epKey,id)`; gán lại →
  update tại chỗ, không nhân dòng. Restart server → nhãn còn (đọc lại từ file).
- Màn nhập **không có giá trị mặc định từ teacher**; teacher labels hiển thị
  read-only, mờ; đổi `annotator` → nhãn ghi kèm đúng annotator đó.
- `state.jsonl` mang `speaker` (đọc từ `transcripts.csv`) cho mọi record — để
  phase 4 / I4 assert `(series,ep,speaker)`.

## Verification

| # | Intent | Check | Where |
|---|---|---|---|
| 1 | State là nguồn sự thật bền | Label 5 clip → kill server → restart → 5 nhãn còn nguyên | manual |
| 2 | Không pre-fill (ADR-003 / I6) | Mở clip có 2-teacher đồng thuận: ô emotion/V/A **trống**, teacher chỉ mờ read-only | manual |
| 3 | Provenance annotator (I2) | Mỗi dòng `state.jsonl` có `annotator` + `ts` non-empty | lint + manual |
| 4 | Ghi atomic | Không có dòng cụt khi ghi trùng lúc (tmp→rename) | code review |

## Review notes

- **Đây là hợp đồng dữ liệu.** Schema `state.jsonl` chốt ở phase này; recut
  (`recut`+biên mới), reject (`rejected`+reason), text (`gold_text`) là **field
  thêm dần** ở phase 2–3 — thiết kế record để mở rộng được, đừng khoá cứng.
- **Teacher mờ vẫn neo nhãn** (ADR-003 caveat, Schroeder ACL 2025): chấp nhận
  đánh đổi tốc độ ở giai đoạn single-pass; **không** báo teacher như baseline vì
  nhãn human đã bị neo (I6).
- localStorage của tool tĩnh **không migrate** sang `state.jsonl` (chưa có nhãn
  thật) — bỏ qua.
