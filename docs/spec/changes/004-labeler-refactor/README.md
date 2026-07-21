# Change 004 — Labeler refactor (retire cut.html + split server.py + extract app.js)

**Status:** done (2026-07-08) — parity verified by full e2e regression.
**Goal:** giảm nợ kỹ thuật user nêu (dài + trùng lặp + `cut.html` lệch kiến trúc
+ god-script HTML), **KHÔNG đổi hành vi**. Không phải feature mới — chỉ dọn cấu trúc.

## (a) Retire `cut.html`

- **Xoá** `tools/labeler/cut.html` + link "cut mode ↗" trong `index.html`.
- **Lý do:** stale (chưa migrate lên FastAPI ở phase 0), trùng ~130 dòng với
  `index.html` (ZIP writer, `csvCell`, waveform, bảng màu emotion), và nhu cầu
  "cắt tươi từ audio bất kỳ" nay được **F5 split + pipeline** phủ.
- Nếu sau này cần cắt-tươi từ `audio_full`: làm **server-backed** trong index
  (đúng kiến trúc) thay vì hồi sinh tool client-side.
- `cut.html` untracked → xoá là không đảo ngược qua git; đã nêu trước khi xoá.

## (b) Tách `server.py` thành module (SRP mức module)

`server.py` (542 dòng, trộn routing + CSV + audio + persistence) → 4 file:

| File | Dòng | Trách nhiệm |
|---|---|---|
| `server.py` | 232 | FastAPI app + request models + routes (mỏng) + `main` |
| `store.py` | 178 | config (`ROOT`/`STATE`) + `state.jsonl` load/save + records + paths |
| `episodes.py` | 85 | đọc CSV + dựng `/episodes` listing & `/episode` join |
| `audio.py` | 77 | `soundfile` recut/split + backup/restore `_orig/` |

- Gom lặp: `store.put()` (write+save 1 chỗ), `store.episode_dir()` (validate id +
  resolve dir). Route giờ ~5–15 dòng.
- Import phẳng (chạy `python server.py` → sibling `import store/episodes/audio`);
  `store` không import ai → không vòng lặp. `ROOT/STATE` là global của `store`,
  module khác đọc `store.ROOT` (không `from store import ROOT`).

## (c) Tách + phân rã JS (ES modules)

Bước 1 — tách khỏi markup: `index.html` **455 → 122 dòng** (markup thuần); JS
inline → `app.js`. **Chưa đủ** — chỉ đổi chỗ god-script (user phản hồi đúng).

Bước 2 — **phân rã thật bằng ES modules** (import/export tường minh, hết global
chung). `app.js` → 5 file, nạp qua `<script type="module" src="main.js">`:

| File | Trách nhiệm | Phụ thuộc |
|---|---|---|
| `state.js` | consts (`EMO`) + `$`/`esc`/`gk` + state object **`S`** | — |
| `api.js` | mọi call server + `clipUrl` (gom `epPath` encode 1 chỗ) | — |
| `view.js` | waveform + render (sidebar/table/emo/speaker) + select/open | state, api |
| `actions.js` | confirm/recut/split/reject + export (csv/zip) | state, api, view |
| `main.js` | DOM wiring + keyboard + init `loadEpisodes()` | state, view, actions |

- Mọi biến `let` global → thuộc tính của `S` (`cutMode`→`S.cutMode`…); DAG không
  vòng lặp (`state`←tất cả; `api` leaf; `view`←api; `actions`←view; `main`←all).
- Cần MIME `text/javascript` cho `type=module` (Python 3.11 `mimetypes` OK — verify).
- **Verify:** node DOM-stub harness import cả graph (bắt lỗi reference/import lúc
  load, không chỉ syntax) + served 200 + backend e2e. Frontend runtime **vẫn cần
  browser-drive** (caveat như mọi phase).

## Không làm (giữ simplicity-first, ngoài scope)

- **Không** DI/repository/class hoá backend — over-engineering cho tool local
  1–2 người (đúng "Simplicity First" của repo).
- **Không** full-refresh `SPEC.md` (nó cũ so với code đã build) — chỉ gỡ cut.html
  + ghi kiến trúc module; refresh rộng là việc riêng.

## Verification

**Backend (a,b):** full e2e regression trên fixture 3-clip (**ALL PASS**): reads
(`/episodes /episode /clip`), gold + speaker (F6), done count, recut+undo (merge
giữ emotion), reject+undo, split+undo (id con `max+1/+2`, file dur, cha reject,
counts). `ruff check`+`format` sạch cả 4 file; `import server` OK (16 routes, no
circular).

**Frontend ES-module (c):** `app.js` (335) → `state.js` 28 · `api.js` 26 ·
`view.js` 194 · `actions.js` 154 · `main.js` 72. Verify: `node --check` mỗi file;
**node DOM-stub harness** `import('./main.js')` chạy cả graph + wiring + init
`loadEpisodes()` **không throw** (bắt lỗi import/reference/export lúc load); 5
module served **200 `application/javascript`** (đúng cho `type=module`);
`app.js`→404; backend POST gold 200. **Runtime UI vẫn cần browser click-test**
(caveat như mọi phase frontend).
