# Change 016 — Labeler: cắt thủ công thành trang riêng + chọn vùng trên ngữ cảnh ±1 block

**Status:** done (2026-10-03). Đã chạy thử trên trình duyệt (headless Edge qua CDP,
thời gian thực), dùng một tempdir riêng. Không có thay đổi backend.
**Goal:** overlay "✂ cắt thủ công" quá chật để chọn vùng, còn nút chỉnh mép `±0.2s`
không đủ khi câu cần lấy lan sang block script trước/sau. Theo yêu cầu của user:
- tách popup thành **trang riêng**;
- chọn 1 đoạn hội thoại thì **load thêm 2 đoạn liền kề**;
- user **chọn 1 vùng trên đó** làm clip chính;
- "thêm đầu/thêm cuối vài giây" → **thêm 1 đoạn trước / 1 đoạn sau**.

## Hành vi

- **Trang riêng** `segment.html?ep=<epKey>&annotator=<id>`. Nút `✂ cắt thủ công` ở
  `index.html` mở trang trong tab mới, mang theo tập đang chọn và annotator. Overlay
  `#segment` cùng CSS/markup của nó bị gỡ khỏi `index.html`.
- **Click 1 block script** → waveform tải `[start(i−1), end(i+1)]` từ
  `GET /segment-audio`, lấy vocals đã tách nhạc và clamp ở đầu/cuối tập. Vùng chọn mặc
  định là đúng block i. Shift-click gộp `i0..i1`, view vẫn là ±1 block quanh khoảng gộp.
- **Kéo trên sóng** → vùng chọn = clip chính (giây tuyệt đối của tập). Click không kéo
  (<4px) chỉ dời con trỏ phát. Vạch dọc kèm nhãn `M:SS` đánh dấu mép từng block.
- **`＋ đoạn trước` / `＋ đoạn sau`** nới **vùng hiển thị** thêm 1 block, còn vùng chọn
  giữ nguyên (kéo lại để lấy phần mới). Mỗi nút bị disable khi view đã chạm block đầu
  hoặc cuối tập.
- **Nghe:** `▶ phát` (Space) phát cả view từ con trỏ; `▶ nghe vùng chọn` chỉ phát
  `[a,b]`. Có slider khuếch đại 1–4× riêng cho trang.
- **Text seed** = text các block mà vùng chọn phủ quá nửa
  (`overlap > ½·min(độ dài block, độ dài vùng)`). Chỉ seed lại khi tập block phủ thay
  đổi, để không ghi đè text người vừa sửa khi kéo trong cùng block.
- **Tạo clip:** `POST /segment` không đổi (label ngay / label sau). Sau khi tạo, trang
  giữ view (clip kế thường nằm ngay cạnh) và xoá vùng chọn cùng form nhãn. Dialect mặc
  định suy từ series = thư mục cha của `epKey` (`dialectFor`).

## Quyết định thiết kế

- **"＋ đoạn" nới view, không nới vùng chọn.** View đã có sẵn ±1 block nên kéo là đủ
  lấy sang câu kề bên. Nút này dùng để lấy thêm ngữ cảnh khi cần xa hơn. Phương án bị
  loại: nút nới luôn vùng chọn ra hết block kế bên, vì buộc vùng chọn ăn trọn block đó
  rồi người dùng lại phải kéo thu về.
- **Tab mới, không điều hướng cùng tab:** tab labeler giữ nguyên clip đang mở và nhãn
  đang nhập dở. Đổi lại, clip mới **không tự hiện** trong bảng labeler: phải `↻`/mở lại
  tập. Không tự làm mới khi quay lại tab, vì `reopenClip()` nạp lại form từ record và
  sẽ xoá nhãn chưa lưu.
- **Một lần fetch cho mỗi view:** cùng `ArrayBuffer` vừa làm `Blob` cho `<audio>` (phát
  và seek) vừa `decodeAudioData` để vẽ sóng. Không có route mới, `segment.html` là file
  tĩnh nên owner-only qua middleware `guard` như `index.html`.
- **Trạng thái của trang là biến cục bộ trong module `segment.js`**, không nằm trong
  kernel `S` (gỡ `script/segDur/segSel/segBuf/segAudio` khỏi `state.js`).

## File thay đổi (đều trong `tools/labeler/`)

| File | Thay đổi |
|---|---|
| `segment.html` | **mới** — trang cắt thủ công (script trái · sóng + form phải) |
| `segment.js` | viết lại thành entry của trang: view ±1 block, kéo chọn, ＋ đoạn trước/sau, phát/seek, gain |
| `index.html` | gỡ overlay `#segment` + CSS `.seg*`; tooltip nút ✂ và slider gain |
| `main.js` | nút ✂ → `window.open("segment.html?…")`; gỡ wiring overlay; gain chỉ còn 2 player |
| `state.js` | gỡ các field segment khỏi `S` |
| `episodes.py` | docstring: "overlay" → "trang" (không đổi logic) |
| `SPEC.md`, `SPEC-features.md`, `RUN.md` | mô tả trang mới |

## Verify

- `node --check` cho `segment.js`, `main.js`, `state.js`.
- **Browser-drive** (headless Edge + CDP, server test ở cổng 8431 trên **bản sao
  `cay-tao-no-hoa/ep01` trong scratchpad**, không đụng `state.db` thật vì `:8421` đang
  chạy):
  - click block 10 → view 9–11, vùng chọn 49–61s;
  - kéo 40%→60% → 54.0–58.0s;
  - click không kéo → vùng chọn giữ nguyên;
  - `＋ trước` → 8–11, `＋ sau` → 8–12, vùng chọn giữ nguyên;
  - shift-click 20+22 → view 19–23, phủ 20–22;
  - tạo khi thiếu nhãn → cảnh báo; tạo có nhãn → record `manual_segment` với emotion,
    V/A, `dialect=south`, `annotator=tester` đúng.
- `index.html` boot không lỗi JS; nút ✂ mở
  `segment.html?ep=cay-tao-no-hoa%2Fep01&annotator=human`.
- **Op note:** chỉ đổi file tĩnh → không cần restart `:8421`, chỉ cần hard-reload tab.
- **Lưu ý khi test:** dưới `--virtual-time-budget`, headless Edge không bao giờ resolve
  `decodeAudioData`, nên phải drive thời gian thực qua CDP.

## Nợ

- Chưa đánh dấu trên script/sóng những vùng đã cắt thành clip, nên vẫn có thể cắt trùng.
- Chưa overlay speaker-turn (`diar_turns.csv`) để cảnh báo đa giọng (nợ cũ, xem `SPEC.md`).
