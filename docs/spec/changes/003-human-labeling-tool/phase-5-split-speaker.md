# Phase 5 — F5 split + F6 speaker sửa được

**Status:** done (2026-07-08) — spec: [SPEC-features §F5–F6](../../../../tools/labeler/SPEC-features.md).
**Depends on:** phase 1 (`state.jsonl`), phase 2 (`soundfile` slice + `_seed_record` merge).

**Goal:** (F6) speaker thành **nhãn-của-record sửa được** (dropdown speaker/tập +
`＋ mới`); (F5) **chia 1 clip thành 2** con clip mới, cha giữ + reject, con label
riêng (speaker + script + emotion) — thực thi PA3.

## Scope

- **F6 backend:** `GoldIn.speaker` (tuỳ chọn) → `put_gold` ghi đè `speaker` khi
  có; `/episode` trả `speakers` (hợp `segments.csv` + record) + clip.speaker ưu
  tiên record. **F6 frontend:** ô `#g-spk` dropdown + `＋ mới` (prompt), gửi kèm
  `POST /gold`.
- **F5 backend:** `POST /split/{ep}/{id}` `{t}` — id con = `max(seg)+1/+2`,
  `soundfile` cắt 2 nửa (atomic), cha `rejected`+`reason="split"`+`split_children`,
  con record seed (speaker=cha, biên chia, `split_from`, nhãn trống). `POST
  /split/.../undo` xoá 2 con (file+record) + un-reject cha. **F5 frontend:** nút
  `⁄ chia` → click điểm trên sóng (marker cam) → `✔ chia đôi` → nhảy tới con A.
- **Out:** export/downstream hiểu id con + loại cha split (phase 4).

## Exit criteria

- F6: gán nhãn với speaker mới → `state.jsonl.speaker` = giá trị người chọn;
  dropdown gộp id cũ + mới; clip hiển thị speaker của record.
- F5: split tại `t` → 2 file `seg<next>.wav`/`<next+1>` đúng độ dài, cha rejected
  (reason split), 2 record con speaker=cha + nhãn trống; undo xoá sạch + un-reject.
- `done` không đếm cha (rejected) lẫn con chưa-nhãn; `total` +2 sau split.

## Verification (e2e, fixture 3-clip 2.0s)

| # | Intent | Kết quả |
|---|---|---|
| 1 | F6 speaker override + list | `speaker=ACTOR_X`; `/episode.speakers=[ACTOR_X,SPK1]`; clip.speaker=ACTOR_X |
| 2 | F5 id con = max+1/+2 | split seg00000 → con `seg00003`,`seg00004` |
| 3 | F5 biên + file | childA `[0,0.8]` dur 0.8s, childB `[0.8,2.0]` dur 1.2s; speaker=SPK1(cha), split_from |
| 4 | F5 cha giữ + reject | parent `rejected=true reason=split split_children=[…]` |
| 5 | counts | total 3→5, rejected 0→1 |
| 6 | undo | file con xoá, cha un-reject, split_children gỡ, total→3 rejected→0 |
| 7 | ruff/compile/JS-parse/served | pass; served UI có `g-spk/splitbtn/splitdo` |

Frontend chưa **browser-drive** (verify API-e2e + syntax + served + wiring).

## Review notes

- **Con nằm cuối danh sách** (đánh số tiếp, không cạnh cha) — chủ đích, chấp nhận.
- **Rủi ro I4 (F6):** id speaker gõ lệch → cùng giọng thành 2 id. Dropdown +
  `＋ mới` giảm thiểu; cần review danh sách id trước khi dựng test-set (ADR-002).
- Con `_N`… **không** dùng: đã đổi sang **id seg mới** (quyết 2026-07-08) → không
  cần nới `CLIP_RE`, tái dùng cơ chế reject cho cha.
- Downstream (phase 4): `build_kaggle_dataset.py` đọc nhãn con từ `state.jsonl`
  (không tra `segments.csv` cho id con), loại cha `reject_reason="split"`.
