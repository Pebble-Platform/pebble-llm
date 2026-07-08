# Spec — tính năng mở rộng labeler (planned, CHƯA build)

> Ba tính năng thêm vào `index.html`. Quyết định đã chốt 2026-07-07 (user).
> Đây là spec *kế hoạch* — `SPEC.md` vẫn là current-truth của công cụ hiện tại.
> Khi build: nên graduate thành một change `docs/spec/changes/NNN-labeler-cut-progress/`.
> Media legality không đổi: mọi file đọc/ghi nằm trong `data/**` (gitignored) —
> local-only, không release.

## Kiến trúc: FastAPI backend + HTML frontend

Cả ba tính năng cần **ghi/đọc/serve file trên đĩa**. Vì đằng nào cũng phải chạy
qua localhost, dùng thẳng **FastAPI backend** (Python) thay cho File System
Access API của browser — full quyền FS, không kẹt browser-compat, tái dùng stack
audio sẵn có.

- **Backend:** FastAPI + uvicorn, chạy trong **`.venv-vnser`** (đã có `soundfile`
  → cắt/ghi wav server-side **atomic + đúng sample format**, hơn `sliceWav`
  re-encode 16-bit in-browser). Bind **`127.0.0.1`** (single-user local, không
  auth). Tham số `--root` = thư mục `episodes/`.
- **Frontend:** `index.html` giữ UI, đổi từ đọc `File` object sang **REST +
  `<audio src>`**. Bỏ được ZIP-writer + CRC32 + WebAudio-decode-để-cắt; vẫn dùng
  WebAudio chỉ để **vẽ waveform**. (`cut.html` đã retire — change 004.)
- **Vì sao FastAPI > FS Access API:** không giới hạn Chrome/Edge; không prompt
  permission mỗi phiên; cắt bằng `soundfile` (atomic, đúng provenance); backend
  đọc/ghi thẳng `segments.csv`/`transcripts.csv` và feed reject-list cho
  pool-builder **cùng module Python**. Chi phí localhost đã trả sẵn.
- **Gold chuyển server-side** (`POST /gold`) thay localStorage → **xoá issue #3**
  (`SPEC.md`: localStorage đè nhau) và cho F2 tính progress server-side.
  `annotator` là field trên request. (Fix localStorage per-annotator ở `SPEC.md`
  thành thừa với kiến trúc này.)
- **Legality:** server chỉ bind 127.0.0.1, chỉ phục vụ `data/**` (gitignored) —
  local-only, không release. Không đổi.

### REST surface (đề xuất)

| Method · path | Việc |
|---|---|
| `GET /episodes` | list tập + progress (từ progress.json/gold) |
| `GET /episode/{epKey}` | clips + transcripts + nhãn 2-teacher (server đọc CSV) |
| `GET /clip/{epKey}/{id}.wav` | serve audio clip (HTTP range) |
| `POST /gold/{epKey}/{id}` | lưu gold 1 clip |
| `POST /recut/{epKey}/{id}` `{a,b,text}` | slice `seg*.wav`, backup `_orig/`, cập nhật start/end |
| `POST /reject/{epKey}/{id}` `{reason}` | flag rejected |
| `GET /export/gold.csv` · `/export/gold.zip` | server dựng export |

`progress.json` ghi lại (atomic) sau mỗi mutation.

---

## F1 — Re-cut + edit text ngay trong index

**Decision: trim trong chính clip `seg*.wav`** (chỉ CO ngắn, không nới rộng —
nếu cần nới phải dùng `audio_full.wav`, ngoài scope lần này).

- **UI:** nút `✂ cut` ở mỗi clip (trong `detail` hoặc hàng bảng) → **popup**:
  - waveform của clip (tái dùng decode + `drawWave` sẵn có), kéo chọn sub-range
    `[a,b] ⊆ [0, dur_clip]`; nghe vùng chọn; nút **Lưu** / **Huỷ**.
- **Lưu:** frontend `POST /recut/{epKey}/{id}` `{a,b,text}`; **backend** làm:
  - `soundfile` đọc `clips/seg*.wav`, cắt `[a,b]` (giữ `sr` nguồn), **atomic
    overwrite** (ghi tmp → rename), sau khi **backup `clips/_orig/seg*.wav`** lần
    recut đầu (copy server-side, rẻ, đảo ngược được).
  - Cập nhật biên tuyệt đối `start' = start + a`, `end' = start + b`
    (a,b từ đầu clip) + `recut=true` + `gold_text` vào record trong `state.jsonl`.
- **Nút Hoàn tác** (popup): `POST /recut/.../undo` → backend copy `_orig/seg*.wav`
  → `seg*.wav`, revert `start/end/gold_text/recut` về giá trị pipeline gốc.
- **Edit text (vì audio đổi):** field text **sửa được** trong `detail`, prefill
  từ ASR (`text_phowhisper`). Lưu `gold_text` vào `state.jsonl`.
- **Không đụng `transcripts.csv`** (giữ provenance pipeline). Sau recut clip lệch
  với `transcripts.csv` — chấp nhận, cờ `recut`; **`state.jsonl` là nguồn sự
  thật**, `gold.csv` chỉ là export.

---

## F2 — Danh sách folder + % labeling (nguồn: `state.jsonl`)

**Decision: 1 file trạng thái duy nhất `state.jsonl`** (nguồn sự thật), progress
tính từ nó — không cần file progress riêng.

- **`state.jsonl`** tại root `--root` (backend, ghi atomic tmp→rename), mỗi dòng
  1 clip `(epKey, id)` chứa **toàn bộ**: gold emotion/V/A/distress/multi,
  `gold_text`, `recut`+biên mới, `rejected`+reason, `annotator`, timestamps.
- **Sidebar:** mỗi tập `done/total` + **%**; header `Σ done / Σ total · %` —
  tính trực tiếp từ `state.jsonl` (không có file progress tách rời).
- Phân biệt với `.cut_done` (marker pipeline *extraction* sẵn có mỗi ep) — KHÔNG
  gộp; `state.jsonl` là trạng thái *labeling*.

---

## F3 — Đánh dấu clip không đạt chuẩn (reject)

**Decision: flag `rejected`, GIỮ file** (không xoá, không di chuyển).

- **UI:** nút `⚑ reject` ở clip → chọn lý do ngắn (dropdown:
  `multi_speaker / noise / bad_cut / other` + note tuỳ chọn).
- **Lưu:** `rejected=true`, `reject_reason` vào record trong **`state.jsonl`**
  (không file rejects riêng — mọi trạng thái ở một chỗ).
- Clip rejected: **không tính vào `done`**; hiển thị mờ + nhãn `⚑` trong bảng;
  có thể un-reject.
- File `.wav` **giữ nguyên** → **điểm nối downstream (chưa build):**
  `build_kaggle_dataset.py` đọc `state.jsonl` và **loại** `(ep,id)` rejected khỏi
  export. Không có bước này, clip rác vẫn lọt corpus.

---

## F5 — Chia 1 clip thành 2 (split)  [planned, chưa build]

**Vấn đề.** Một clip pipeline đôi khi chứa **2 lượt thoại** dính nhau (diarization
gộp/bỏ sót ranh giới). F1 recut chỉ **co** một đoạn — không tách được. Cần: chọn
1 **điểm cắt** `t` trong clip → sinh **2 clip con** độc lập, mỗi cái label riêng.

**Quyết định đã chốt (2026-07-07):**
- **ID con = số seg tiếp theo của tập** (KHÔNG hậu tố `_N`, KHÔNG đổi `CLIP_RE`):
  `next = max(số seg trong clips/) + 1`; con A = `seg<next>`, con B = `seg<next+1>`
  (5-chữ-số). Split lần sau lấy max mới. ⇒ con **nằm cuối** danh sách clip (đánh số
  tiếp), không cạnh cha — chấp nhận.
- **Cha GIỮ NGUYÊN** (file + id không đụng) nhưng **trạng thái → rejected**
  (`reject_reason="split"`, lưu `split_children=[idA,idB]`) ⇒ **loại khỏi
  `done`/export** đúng cơ chế F3, mờ + `⚑` trong bảng. **Không** dùng `_orig/` cho
  split (cha không bị cắt).
- **Con:** 2 clip **MỚI** — `soundfile` cắt 2 nửa từ cha (atomic), ghi
  `clips/seg<next>.wav` + `seg<next+1>.wav`. Record con seed: `series/episode` từ
  tập, **`speaker` mặc định = speaker cha**, `start/end` chia từ biên cha,
  `split_from=<parentId>`, **nhãn trống** (2 nửa có thể khác emotion → không kế
  thừa nhãn cha).
- **Con label riêng (PA3):** mỗi con đi qua **luồng label thường** — nhập
  **speaker** (dropdown, con B có thể chọn người khác — [F6](#f6--speaker-sửa-được-label-of-record--planned-chưa-build)),
  **script** (`gold_text`), **emotion/V/A**. Split chỉ tạo 2 con trống.
- **Undo split** (`POST /split/.../undo`): **un-reject cha** + xoá 2 wav con +
  2 record con (đọc `split_children`). Đảo ngược hoàn toàn.
- **UI:** cụm cut thêm nút `⁄ chia` → click 1 điểm trên sóng (marker dọc) →
  `chia đôi` → `POST /split/{ep}/{id}` `{t}`; re-fetch tập, nhảy tới con A.

**REST:** `POST /split/{epKey}/{id}` `{t}` → `{parent, children:[recA,recB]}`;
`POST /split/{epKey}/{id}/undo`. (`/undo` route khai báo TRƯỚC route chung —
cùng bẫy path-converter như `/recut`.)

**Điểm nối downstream:** con là **id seg mới, không có trong `segments.csv`** →
`speaker` con được **ghi vào record lúc tạo** (default cha, người sửa qua F6),
KHÔNG tra segments.csv. `build_kaggle_dataset.py` loại cha (`rejected`/`split`) +
đọc nhãn con từ `state.jsonl` như mọi clip.

---

## F6 — Speaker sửa được (label-of-record)  [planned, chưa build]

**Vấn đề.** `speaker` hiện là provenance **read-only** từ diarization. Với split
(F5, con `_2` là người khác) và ADR-003 (người là nguồn sự thật), speaker cần
**người sửa được** → thành nhãn-của-record, ghi đè id diarization khi cần.

**Quyết định đề nghị:**
- Form label thêm ô **speaker**: **dropdown các speaker đã biết của tập** (hợp
  `segments.csv` + id đã nhập trong `state`) + **`＋ mới`** để thêm id. Dropdown
  thay free-text để **giữ id ổn định** cho I4 (cùng người → cùng id; tránh gõ lệch).
- Backend: `GoldIn` thêm `speaker` (tuỳ chọn); `POST /gold` lưu speaker người
  chọn. `_seed_record` mặc định = speaker diarization. `/episode` trả thêm
  `speakers` (danh sách id để dựng dropdown).
- **Provenance:** `state.jsonl.speaker` = speaker-của-record (người nếu đã sửa,
  else diarization); id diarization gốc vẫn ở `segments.csv` (không mất).
- **I4** dùng `state.jsonl.speaker` (nhãn người) làm authoritative.

**⚠ Rủi ro (không chặn):** gõ id lệch → cùng giọng thành 2 id → rò I4. Mitigation
= dropdown + `＋ mới` (kiểm trùng); review danh sách id trước khi dựng test-set.

---

## Trường trong `state.jsonl` (nguồn) → `gold.csv` (export)

`state.jsonl` mỗi record: emotion/V/A/distress/multi, `gold_text`, `recut`+biên,
`rejected`+`reject_reason` (F3; cha split = rejected reason `"split"` +
`split_children`), `split_from` (con, F5), `annotator`, `speaker` (sửa được, F6),
`series/ep/id`, timestamps. `gold.csv`/`.zip` là **view export** dựng từ đó (bỏ
`rejected` và cha `split=true`).

## Quyết định đã chốt (2026-07-07)

1. **`gold_text`** — nguồn sự thật text cho clip (thay ASR/model). **Local +
   vào Kaggle export private để TRAIN** (`build_kaggle_dataset.py` vốn đã mang
   text). **Bản public CC-BY strip text** (intent §1). ⇒ dùng để train, không
   release công khai.
2. **Backup `clips/_orig/` + Undo** — bật **mặc định**; recut thao tác trên file
   gốc, `_orig/` là bản an toàn, nút Hoàn tác lấy lại (F1).
3. **Reject** — nằm trong **`state.jsonl`** (1 file trạng thái duy nhất), không
   file rejects riêng, không nhúng gold.csv.

## Điểm nối / ràng buộc downstream (chưa build)

- `build_kaggle_dataset.py`: đọc `state.jsonl` → dùng nhãn **human** làm nhãn
  train (ADR-003, teacher chỉ gợi ý), loại `(ep,id)` rejected, xử lý biên recut.
- Invariants: recut đổi start/end nhưng clip **vẫn phải đơn-giọng** (I3); reject
  là công cụ thủ công hỗ trợ I3 (bắt điểm mù diarization mà tai người nghe ra).
- Trình tự: F1–F3 + hiển thị **teacher gợi ý mờ** (ADR-003) sửa cùng `index.html`
  — phối hợp để tránh xung đột vùng `detail`/`suggest()`.
