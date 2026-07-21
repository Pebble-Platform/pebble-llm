# Change 005 — Labeler: excise middle chunk (F7) + click-to-seek

**Status:** done (2026-07-18) — backend e2e-verified; frontend node-checked + live-served.
**Goal:** hai tính năng user yêu cầu cho `tools/labeler/`:
1. **Bỏ đoạn GIỮA bị nhiễu** mà clip **không bị chia đôi** (khác F5 split).
2. **Nghe từ vị trí chọn** trên sóng thay vì luôn từ đầu.
Không đổi hành vi F1–F6 hiện có. Living doc: [`docs/tasks/labeler-excise-seek.md`](../../../tasks/labeler-excise-seek.md).

## F7 — Excise (bỏ đoạn giữa, giữ 1 clip)

**Vấn đề.** F1 recut chỉ **co** về `[a,b]` (bỏ hai đầu). F5 split **chia** thành
nhiều clip con. Không cái nào bỏ được một đoạn nhiễu **ở giữa** mà vẫn giữ clip
là một mảnh liền.

**Giải pháp.** Chọn `[a,b]` ở giữa → server đọc wav, ghi `concat([0,a],[b,dur])`
(atomic tmp→rename), giữ nguyên `sr`/subtype. Clip vẫn là **một** `seg*.wav`.

**Quyết định đã chốt:**
- **Provenance = giữ biên bao + ghi lỗ hổng** (user chọn 2026-07-18): excise
  **không** đổi `start`/`end` (vẫn là biên bao gốc); đoạn bỏ được **append** vào
  `excised: [[a,b],…]` (giây clip-local, theo thứ tự cắt). Lý do: với `_orig/` +
  `excised` có thứ tự, tái dựng chính xác được cái gì đã bỏ — **không mất im
  lặng** (đúng luật provenance CLAUDE.md). Bác: gộp `end = start + dur_mới` (đoạn
  bỏ biến mất khỏi record — không trung thực).
- **Dùng lại `recut=true` + `/recut/undo`:** excise set `recut=true` (kích cờ `✂`
  trong bảng) và **undo dùng chung** `POST /recut/undo` — vốn khôi phục audio
  pristine từ `clips/_orig/` + reset biên; nay **cũng xoá `excised`**. Bác:
  route `/excise/undo` riêng (trùng logic restore).
- **UI dùng lại drag-select của chế độ cut** (1 selection, 2 nút lưu): `✂ cắt` →
  kéo chọn → `✔ lưu cắt` = GIỮ `[a,b]` (trim, cũ) · `⌦ bỏ giữa` = XOÁ `[a,b]`
  (excise, mới). Bác: `exciseMode` riêng + highlight đỏ (trùng code toggle/reset/
  drag/draw; nhãn nút đã đủ phân biệt ý định lúc lưu).
- **Chặn mép:** excise validate `0 < i0` và `i1 < len` (đoạn phải nằm GIỮA) —
  bỏ mép là trim, dùng `✔ lưu cắt`. Selection quá ngắn/rỗng → 400.
- **I3 giữ nguyên:** excise bỏ nhiễu trong **một** giọng — không gộp, không đổi
  speaker; clip vẫn đơn-giọng.

**REST:** `POST /excise/{epKey}/{clip_id}` `{a,b,text}` → record (với `excised`
cập nhật, `recut=true`, `start/end` không đổi). Undo qua `POST /recut/{…}/undo`.

## Seek — nghe từ vị trí chọn

Trong `main.js` `mousedown` trên `#wave`, **chế độ thường** (không cut/không split)
trước đây `return;` (click vô tác dụng). Nay: `S.audio.currentTime = xToTime(e)`
+ vẽ lại con trỏ. `Space` phát tiếp từ đó (audio element giữ `currentTime`).
Không thêm UI mới; con trỏ trắng sẵn có báo vị trí.

## File đã đổi

| File | Đổi |
|---|---|
| `tools/labeler/audio.py` | `+numpy`, `excise()` (concat + backup + guard) |
| `tools/labeler/store.py` | seed_record `+ "excised": []` |
| `tools/labeler/server.py` | `ExciseIn`, `POST /excise`, `/recut/undo` clear `excised` |
| `tools/labeler/api.js` | `+ excise()` |
| `tools/labeler/actions.js` | `+ saveExcise()` (guard middle-only) |
| `tools/labeler/index.html` | `+ ⌦ bỏ giữa` button |
| `tools/labeler/main.js` | wire `excisesave`; cut prompt; **seek** in mousedown |
| `tools/labeler/SPEC.md` | data model + REST + Chức năng (F7 + seek) + I3 note |

## Verify

- **Backend e2e** (scratchpad `test_excise.py`, `.venv-vnser`, ALL PASS):
  - `audio.excise` length == input − removed, content == `concat([:i0],[i1:])`,
    `_orig/` backup created.
  - `POST /excise`: `excised==[[a,b]]`, `start/end` unchanged, `recut=true`,
    audio file shortened.
  - `POST /recut/undo`: `excised==[]`, `recut=false`, audio back to pristine len.
  - Guard: edge/empty excise → 400.
- **Frontend:** `node --check` all 5 modules; DOM-stub `import("./main.js")` boots
  clean (excisesave wired, no reference/export errors); live server serves the
  button, `main.js` as ESM (`application/javascript`), `/excise` route responds.
- `ruff check` + `ruff format --check` green on changed Python.
- **Caveat (repo-wide):** live click/drag interaction (excise selection, seek
  click) needs a human browser-drive — không tự động hoá được trong repo này.

## Không làm (ngoài scope / simplicity-first)

- Không map `excised` về toạ độ clip-gốc khi excise nhiều lần (hiếm); list có thứ
  tự + `_orig/` đã đủ tái dựng. Ghi rõ semantics "current-file-local, theo thứ tự".
- Không thêm chỉ báo thời gian seek ngoài con trỏ trắng sẵn có.
- Không đụng downstream `build_kaggle_dataset.py` (phase 4, chưa build) — nó sẽ
  đọc `excised` cùng `start/end` khi dựng.
