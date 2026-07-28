# Chạy labeler trên Windows

Hướng dẫn chạy công cụ gán nhãn (`tools/labeler/`) trên Windows/PowerShell.
Backend = FastAPI trong `.venv-vnser`, bind `127.0.0.1` (local-only). Chi tiết
kiến trúc: [`SPEC.md`](SPEC.md).

## Yêu cầu (đã có sẵn trong repo)

- **`.venv-vnser`** — virtualenv pipeline (đã cài `fastapi uvicorn soundfile numpy pydantic`).
- **`data/vietnamese-ser/episodes/`** — media bản quyền, **local-only**, gitignored (intent §1).

Kiểm tra nhanh (từ repo root):

```powershell
.venv-vnser\Scripts\python.exe -c "import fastapi, uvicorn, soundfile, numpy, pydantic; print('deps OK')"
```

## Chạy

Từ **repo root** (`C:\Users\phat.nguyen\Documents\Research\Pebble\pebble-llm`):

```powershell
$env:PYTHONIOENCODING = "utf-8"
.venv-vnser\Scripts\python.exe tools\labeler\server.py --root data\vietnamese-ser\episodes
```

- `PYTHONIOENCODING=utf-8` — bắt buộc trên console Windows (tên tập/nhãn tiếng Việt).
- Server in ra `-> http://127.0.0.1:8000/index.html`.

Mở trình duyệt: **http://127.0.0.1:8000/index.html**
(phải qua server — **không** mở `file://` trực tiếp; UI là ES-module gọi API).

**Dừng:** `Ctrl-C` trong cửa sổ đang chạy server.

### Cờ tuỳ chọn

| Cờ | Mặc định | Việc |
|---|---|---|
| `--root` | `data/vietnamese-ser/episodes` | thư mục `episodes/` (nguồn media + `state.db`) |
| `--host` | `127.0.0.1` | giữ local-only, đừng đổi ra `0.0.0.0` |
| `--port` | `8000` | đổi nếu cổng bận |

## Phím tắt (trong UI)

`Space` phát · `1`–`7` emotion · `Enter` xác nhận (lưu + nhảy clip kế) · `N`/`P` next/prev.

## Lỗi thường gặp

- **`--root is not a directory`** — chạy sai chỗ (không phải repo root) hoặc dùng `/` thay `\`.
  Chạy từ repo root, đường dẫn `data\vietnamese-ser\episodes`.
- **Cổng 8000 đã bận** (`address already in use`) — server cũ còn chạy, hoặc tab khác đang mở.
  Đổi `--port 8001`, hoặc tìm & tắt tiến trình:
  ```powershell
  Get-NetTCPConnection -LocalPort 8000 -State Listen | Select-Object OwningProcess
  Stop-Process -Id <PID>
  ```
- **Ký tự Việt bị lỗi / `UnicodeEncodeError`** — chưa set `$env:PYTHONIOENCODING = "utf-8"`.
- **Sửa UI (JS/HTML) mà không thấy đổi** — hard-reload trình duyệt (`Ctrl-Shift-R`);
  server đã gửi `Cache-Control: no-cache` nhưng cache cũ đôi khi vẫn dính.

## ⚠️ Lưu ý độ bền dữ liệu

- **Nguồn sự thật = `state.db`** (SQLite/WAL). Lock 1-writer chưa build → **tắt server
  trước khi chạy script ghi** (vd `scripts/vietnamese-ser/migrate_*`), tránh clobber.
- **Chỉ 1 server cho mỗi `--root`.** Đừng mở 2 server cùng trỏ vào
  `data/vietnamese-ser/episodes` (kể cả server test) khi phiên gán nhãn đang chạy.
- `data/**` là media bản quyền — **không commit, không release** (chỉ features + timestamps
  + labels + speaker id mới releasable, CC-BY).
