# Phase 0 — Backend seam (FastAPI) + đường đọc

**Status:** done (2026-07-07) — `tools/labeler/server.py` + `index.html` migrate
File→fetch. Verify: `/episodes` (32 tập), `/episode/ve-nha-di-con/ep01` (175 clip,
`speaker` từ segments.csv), `/clip` 200 audio/wav, traversal chặn, index.html
served là bản migrate (loadEpisodes có, webkitdirectory=0); `node --check` +
`ruff check/format` pass. **Chưa** browser-drive end-to-end (không có headless
browser) — verify ở mức API + served-HTML. Deps `fastapi`+`uvicorn` đã cài vào
`.venv-vnser`.
**Depends on:** —

**Goal:** thay cơ chế nạp folder read-only (`<input webkitdirectory>`) bằng
**FastAPI backend** (chạy trong `.venv-vnser`, bind `127.0.0.1`, `--root=episodes/`);
frontend `index.html` đọc dữ liệu qua **REST + `<audio src>`** thay vì `File`
object. Chưa có tính năng ghi nào — chỉ đường đọc.

## Scope

- **In:** app FastAPI + uvicorn; endpoints `GET /episodes` (list tập, duyệt
  `--root`), `GET /episode/{epKey}` (đọc `transcripts*.csv` + `labels_{opus,sonnet}.csv`
  + `segments.csv` server-side, trả JSON), `GET /clip/{epKey}/{id}.wav` (serve
  clip, HTTP range). Frontend `index.html` chuyển sang `fetch`; bỏ ZIP-writer +
  CRC32 + WebAudio-decode-để-cắt (giữ WebAudio chỉ để vẽ waveform).
- **Out:** mọi ghi (`/gold /recut /reject`, export) → phase 1–4; `cut.html`
  migrate (làm sau, dùng chung API).

## Exit criteria

- `uvicorn` chạy từ `.venv-vnser`; mở `http://127.0.0.1:<port>/` load được
  `index.html`, sidebar liệt kê đúng số tập/clip từ `--root`, chọn clip phát
  được audio + thấy ASR/YT text + gợi ý 2-teacher — **ngang tính năng đọc của
  tool tĩnh hiện tại**, không thiếu.
- Server **chỉ bind 127.0.0.1**, chỉ phục vụ path dưới `--root` (không path
  traversal ra ngoài `data/**`).
- `make check` xanh (nếu thêm code Python vào `scripts/` hoặc thư mục mới — theo
  ruff).

## Verification

| # | Intent | Check | Where |
|---|---|---|---|
| 1 | Đọc ngang tool cũ | Manual: load 1 tập thật (`ve-nha-di-con/ep01`, 175 clip), phát 3 clip, so text/gợi ý với tool tĩnh | manual |
| 2 | Không path-traversal | Request `GET /clip/../../etc` bị chặn (404/400) | manual + 1 unit test |
| 3 | Bind local | `curl` từ 127.0.0.1 OK; không mở ra 0.0.0.0 | manual |

## Review notes

- **File System Access API bị loại** (Chrome/Edge-only, chập chờn `file://`) — dùng
  FastAPI vì đã cần localhost và tái dùng `soundfile` cho phase 2. Xem lý do đầy đủ
  trong [SPEC-features.md](../../../../tools/labeler/SPEC-features.md) §kiến-trúc.
- **Serve `data/**` là media local-only** — server 127.0.0.1, không release; không
  đổi ràng buộc §1. Đừng để port lộ ra mạng.
- Đây là **seam**: sai schema JSON `/episode` ở đây kéo theo mọi phase. Chốt hình
  dạng response khớp field mà `state.jsonl` (phase 1) sẽ cần.
