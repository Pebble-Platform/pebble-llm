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

## F2 — Danh sách folder + % labeling (nguồn: store nhãn)

**Decision: 1 store trạng thái duy nhất** (nguồn sự thật), progress tính từ nó —
không cần file progress riêng. **Cập nhật 2026-07-21 ([ADR-004](../../docs/spec/decisions/ADR-004-labeler-state-durability.md)):**
store nay là **SQLite `state.db`** (WAL, 1 dòng/record, JSON blob) thay `state.jsonl`
full-rewrite; các nhắc "state.jsonl" bên dưới là *store nhãn* (nay = `state.db`).
Record shape không đổi. `SPEC.md` là current-truth.

- **Store** tại root `--root` (backend, SQLite/WAL — `put()` upsert 1 dòng /
  `save()` reconcile trong 1 transaction), mỗi dòng
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

## F5 — Chia 1 clip thành nhiều đoạn (multi-split)  [built 2026-07-09, verified end-to-end]

**Vấn đề.** Một clip pipeline đôi khi chứa **≥2 lượt thoại** dính nhau (diarization
gộp/bỏ sót ranh giới). F1 recut chỉ **co** một đoạn — không tách được. Cần: chọn
**k điểm cắt** `t1 < … < tk` (k ≥ 1) trong clip → sinh **k+1 clip con** độc lập,
mỗi cái label riêng.

**Quyết định đã chốt (2026-07-07; cập nhật 2026-07-09: chia đôi → chia multi,
con kế thừa ASR/YouTube/Opus/Sonnet từ cha):**
- **ID con = số seg tiếp theo của tập** (KHÔNG hậu tố `_N`, KHÔNG đổi `CLIP_RE`):
  `next = max(số seg trong clips/) + 1`; k+1 con = `seg<next>` … `seg<next+k>`
  (5-chữ-số, theo thứ tự thời gian). Split lần sau lấy max mới. ⇒ con **nằm cuối**
  danh sách clip (đánh số tiếp), không cạnh cha — chấp nhận.
- **Cha GIỮ NGUYÊN** (file + id không đụng) nhưng **trạng thái → rejected**
  (`reject_reason="split"`, lưu `split_children=[id các con, theo thứ tự]`) ⇒
  **loại khỏi `done`/export** đúng cơ chế F3, mờ + `⚑` trong bảng. **Không** dùng
  `_orig/` cho split (cha không bị cắt).
- **Con:** k+1 clip **MỚI** — `soundfile` cắt k+1 đoạn từ cha theo các điểm cắt
  (atomic), ghi `clips/seg<next>.wav` … `seg<next+k>.wav`. Record con seed:
  `series/episode` từ tập, **`gender`/`age_group` kế thừa từ cha** (cùng người —
  sửa được per-con), `start/end` chia
  từ biên cha theo điểm cắt, `split_from=<parentId>`, **nhãn gold trống** (các
  đoạn có thể khác emotion → không kế thừa nhãn gold của cha).
- **Con kế thừa provenance/gợi ý của cha:** `asr` (`text_phowhisper`), `yt`
  (`text_youtube`), `opus`, `sonnet` **copy nguyên từ cha vào record con lúc
  tạo** — id con không có trong `transcripts*.csv`/`labels_*.csv` nên không tra
  CSV được; `/episode` ưu tiên field trong record cho con. Đây là **tham chiếu**:
  text/gợi ý là của cả clip cha (không cắt theo đoạn), người label sửa
  `gold_text` + emotion riêng cho từng con.
- **Con label riêng (PA3):** mỗi con đi qua **luồng label thường** — chọn
  **giới tính/tuổi** (kế thừa cha, sửa được per-con),
  **script** (`gold_text`), **emotion/V/A**. Split chỉ tạo các con chưa label
  (gold trống, gợi ý kế thừa).
- **Undo split** (`POST /split/.../undo`): **un-reject cha** + xoá toàn bộ wav
  con + record con (đọc `split_children`). Đảo ngược hoàn toàn.
- **UI:** cụm cut thêm nút `⁄ chia` → click **nhiều điểm** trên sóng (mỗi click
  thêm 1 marker dọc; click lại marker để bỏ) → nút `chia (k+1)` →
  `POST /split/{ep}/{id}` `{ts:[t1…tk]}`; re-fetch tập, nhảy tới con đầu tiên.

**REST:** `POST /split/{epKey}/{id}` `{ts:[t1…tk]}` (tăng dần,
`0 < t1 < … < tk < dur`) → `{parent, children:[k+1 rec]}`;
`POST /split/{epKey}/{id}/undo`. (`/undo` route khai báo TRƯỚC route chung —
cùng bẫy path-converter như `/recut`.)

**Điểm nối downstream:** con là **id seg mới, không có trong CSV nào**
(`segments/transcripts*/labels_*`) → `gender/age_group` **và** `asr/yt/opus/sonnet` được
**ghi vào record lúc tạo** (demographics kế thừa cha, người sửa per-con;
asr/yt/opus/sonnet copy cha), KHÔNG tra CSV. `build_kaggle_dataset.py` loại cha
(`rejected`/`split`) + đọc nhãn con từ `state.jsonl` như mọi clip.

---

## F6 — Speaker/cast  [built rồi BỎ 2026-07-20]

Từng có: speaker sửa được (dropdown nhân vật từ `cast.json`) + màn `⚙ nhân vật`
khai báo giới tính/tuổi 1 lần/phim, clip resolve demographics theo `(series,
speaker)`. **Đã bỏ hẳn** (quyết định user): diarization chưa bao giờ gán lại về
nhân vật nên demographics ship sai; nay **gán `gender`/`age_group` trực tiếp
per-clip** khi label (nghe giọng). I4 vẫn giữ vì split **whole-series** (2 phim
khác đoàn → cast rời) đảm bảo disjoint ở tầng series, không cần speaker-id
per-clip. Xoá `cast.json`-flow + `/cast` + dropdown speaker + màn config; `GoldIn`
thêm `gender`/`age_group`. Migrate 2026-07-21 backfill 232 clip cũ từ `cast.json`
(`scripts/vietnamese-ser/migrate_labeler_demographics.py`). Xem [SPEC.md](SPEC.md)
§"Nhân khẩu per-clip".

---

## F7 — Excise: bỏ đoạn GIỮA bị nhiễu (giữ 1 clip)  [built 2026-07-18, change 005]

**Vấn đề.** F1 recut chỉ **co** hai đầu; F5 split **chia** thành nhiều con. Cần bỏ
một đoạn nhiễu **ở giữa** mà clip **không bị chia đôi** — nối `[0,a]+[b,dur]` lại.

**Quyết định (2026-07-18):**
- Server `soundfile` đọc wav → ghi `concat([:i0],[i1:])` (atomic), giữ `sr`/subtype;
  backup `_orig/` một lần; đoạn bỏ phải nằm GIỮA (chặn mép → dùng trim).
- **Provenance = giữ biên bao + ghi lỗ hổng** (user chọn): `start/end` **không**
  đổi; đoạn bỏ append vào `excised: [[a,b],…]` (giây clip-local, theo thứ tự).
  `recut=true`. Undo dùng chung `/recut/undo` (restore `_orig` + xoá `excised`).
- **UI:** dùng lại drag-select của `✂ cắt`; thêm nút `⌦ bỏ giữa` (song song
  `✔ lưu cắt`). Không thêm mode riêng — nhãn nút phân biệt GIỮ vs XOÁ.

**REST:** `POST /excise/{epKey}/{id}` `{a,b,text}`; undo qua `POST /recut/.../undo`.
Chi tiết + verify: [change 005](../../docs/spec/changes/005-labeler-excise-seek/README.md).

## Seek — nghe từ vị trí chọn  [built 2026-07-18, change 005]

Click trên sóng ở **chế độ thường** (không cut/split) dời `S.audio.currentTime` tới
vị trí đó; `Space` phát tiếp từ đó thay vì từ đầu. Frontend-only (`main.js`
mousedown), không thêm UI (con trỏ trắng sẵn có báo vị trí).

## Trường trong `state.jsonl` (nguồn) → `gold.csv` (export)

`state.jsonl` mỗi record: emotion/V/A/distress/multi, `gold_text`, `recut`+biên,
`rejected`+`reject_reason` (F3; cha split = rejected reason `"split"` +
`split_children`), `split_from` + `asr/yt/opus/sonnet` kế thừa từ cha (con, F5),
`annotator`, `gender`/`age_group` (gán trực tiếp per-clip khi label),
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
