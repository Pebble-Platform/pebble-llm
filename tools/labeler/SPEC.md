# Spec — `tools/labeler/` (human labeling UI + FastAPI backend)

> Công cụ **con người gán nhãn** cho ViEmoSpeech. Tầng **execution** — phải thỏa
> `docs/intent/` + `docs/spec/capabilities/extraction-pipeline.md`.
> Cập nhật: 2026-07-21 (khớp code: phase 0–5 + refactor 004 + excise/seek 005 + context ±N 008 + loại-nhiều 009 + **bỏ speaker/cast, gán giới tính+tuổi trực tiếp per-clip**).
> Chi tiết tính năng: [`SPEC-features.md`](SPEC-features.md). Lịch sử build:
> [change 003](../../docs/spec/changes/003-human-labeling-tool/README.md) (phase
> 0–5) + [change 004](../../docs/spec/changes/004-labeler-refactor/README.md) (refactor)
> + [change 005](../../docs/spec/changes/005-labeler-excise-seek/README.md) (excise + seek).

## Vị trí trong pipeline

Pipeline (`extraction-pipeline.md`) trích **clip sạch** (cắt tại speaker-turn) +
text + **gợi ý** 2-teacher (Opus/Sonnet). Con người gán **nhãn của record** cho
từng clip qua công cụ này ([ADR-003](../../docs/spec/decisions/ADR-003-human-labels-drop-weak-supervision.md):
nhãn người là corpus, teacher chỉ gợi ý). **Nguồn sự thật = `state.db`** (SQLite,
[ADR-004](../../docs/spec/decisions/ADR-004-labeler-state-durability.md));
`gold.csv`/ZIP là *view export*. Constraint ràng: I4 (**test speakers ∩ train =
∅**, [ADR-002](../../docs/spec/decisions/ADR-002-whole-series-speaker-disjoint-gold.md))
và I6 (accuracy nêu test-split speaker-disjoint; tin cậy nhãn = κ **human–human**).

## Kiến trúc

**Backend** (FastAPI, `.venv-vnser`, bind `127.0.0.1`):
`server.py` (routes + models + main, mỏng) · `store.py` (config `ROOT/STATE`
+ `state.db` SQLite/WAL load/save + records + paths) · `episodes.py` (đọc CSV + dựng
`/episodes`, `/episode`) · `audio.py` (`soundfile` recut/split/excise + context
slice + backup `_orig/`).

**Frontend** (ES modules, nạp qua `<script type="module" src="main.js">`):
`state.js` (kernel `S` + consts) · `api.js` (mọi call server) · `view.js`
(waveform + render + select) · `actions.js` (confirm/recut/split/reject
+ export) · `segment.js` (cắt thủ công: script YT + chọn vùng + tạo clip) ·
`main.js` (DOM wiring + keyboard + init). `index.html` = markup thuần.

**Chạy** (từ repo root):
```
.venv-vnser/Scripts/python.exe tools/labeler/server.py --root data/vietnamese-ser/episodes
# mở http://127.0.0.1:8000/index.html  (cần server — không mở file:// trực tiếp)
```
`data/**` là media bản quyền, gitignored, **local-only** (intent §1).

## Data model — `state.db` (nguồn sự thật)

SQLite `state.db` (WAL, `synchronous=NORMAL`): 1 **dòng** = 1 clip, khoá
`(epkey, id)`, cả record là **1 JSON blob** ở cột `data` ([ADR-004](../../docs/spec/decisions/ADR-004-labeler-state-durability.md)).
`STATE` là mirror in-RAM dựng lại từ DB lúc load; ghi = `put()` upsert 1 dòng /
`save()` reconcile cả STATE trong 1 transaction (ACID, `integrity_check`,
hot-backup `VACUUM INTO`). Bootstrap 1 lần từ `state.jsonl` cũ qua
`scripts/vietnamese-ser/migrate_state_to_sqlite.py`. Các trường JSON của record:

| Nhóm | Trường | Ghi chú |
|---|---|---|
| id | `epKey, id, series, episode` | |
| nhãn (F1) | `emotion` | 1/7: `joy sadness anger fear_anxiety surprise disgust neutral` (khớp `m4_prompt.md`) |
| | `valence, arousal` | int 1–5 (`null` khi chưa gán) |
| | `distress` | bool — **bỏ khỏi form 2026-07-10**; server default `false` (record cũ giữ giá trị đã gán) |
| | `multi` | bool — tai người nghi ≥2 giọng |
| | `note` | text — **bỏ khỏi form 2026-07-10**; server default `""` |
| nhân khẩu | `gender, age_group, dialect` | **gán trực tiếp per-clip khi label** (nghe giọng). `gender` = `"" \| female \| male`; `age_group` = `"" \| child \| teen \| young_adult \| middle_aged \| senior` (nhóm tuổi, không phải số); `dialect` = `"" \| north \| central \| south` (Bắc/Trung/Nam — hệ thanh điệu khác nhau, intent §6; metadata KHÔNG phải target train). Không bắt buộc — `""` tới khi chọn. Record cũ giữ thêm `speaker` (không dùng, không migrate) |
| biên | `start, end` | recut-aware (cộng dồn qua nhiều lần recut) |
| recut (F1) | `recut`, `gold_text` | `gold_text` = text người sửa sau recut |
| excise (F7) | `excised` | list `[[a,b]…]` (giây clip-local) đoạn GIỮA đã bỏ + nối; `recut=true`; undo qua `/recut/undo`. `start/end` **giữ nguyên** biên bao (provenance) |
| reject (F3) | `rejected`, `reject_reason` | reason `split` cho cha bị chia |
| split (F5) | `split_from` (con) / `split_children` (cha) | liên kết cha↔con |
| segment | `manual_segment` | `true` = clip người tự cắt từ vocals theo script YT (không có row segments.csv; mang `yt`/`gold_text` riêng) |
| gợi ý | `opus, sonnet` | emotion 2 teacher — **chỉ tham chiếu**, không phải nhãn |
| provenance | `annotator, ts` | ai + khi nào (I2) |

### Nhân khẩu per-clip — gán trực tiếp khi label (quyết định user 2026-07-20)

**Bỏ hẳn speaker/cast.** Trước đây identity clip = tên nhân vật (dropdown từ
`cast.json`), giới tính/tuổi resolve theo `(series, speaker)`. Nhưng diarization
`SPEAKER_xx` chưa bao giờ được gán lại về nhân vật → giới tính/tuổi ship **giá trị
sai** (xem note `build_kaggle_gold.py`). Nay người nghe giọng và **chọn thẳng
`gender` + `age_group` cho từng clip** khi label — lưu per-clip trong `state.db`,
không qua bảng cast. Không còn `cast.json`, không còn dropdown speaker, không còn
màn `⚙ nhân vật`. `age_group` là **nhóm tuổi, không phải số** (không suy chính
xác từ giọng). Giới-tính-disjoint không cần vì split đã **whole-series** (2 phim
khác đoàn → cast rời — I4 đảm bảo ở tầng series, không cần id per-clip).

**Migrate 2026-07-21** (`scripts/vietnamese-ser/migrate_labeler_demographics.py`):
232 clip đã gán nhân vật trước đó được backfill `gender`/`age_group` từ `cast.json`
theo `speaker` (idempotent, chỉ điền field rỗng, backup trước khi ghi) → không
label lại. `cast.json` giữ lại làm nguồn migrate; trường `speaker` cũ trong record
để nguyên (thừa, vô hại).

### Bảng `assignments` — hàng đợi + nhãn vòng 2 của annotator online (change 011)

Bảng **thứ hai** trong `state.db`, khoá **`(annotator, seq)`**, cột phẳng:
`epkey · id · kind · emotion · valence · arousal · skip_reason · listen_ms · ts`.
Một dòng = **một lần TRÌNH BÀY một clip cho một annotator**; hàng đợi và câu trả
lời ở chung (cột nhãn rỗng/NULL tới khi chấm, `ts IS NULL` = chưa chấm).

Khoá theo `seq` chứ không theo `(epkey, id)` vì QC protocol seed ~10% **clip lặp**
để đo tự nhất quán — cùng một clip trình bày cho cùng một người **hai lần**, phải
ra hai dòng độc lập. `kind` ∈ `normal | gold | dup | trap` để báo cáo κ loại
gold/dup ra (qc-protocol §5.1).

`records` **không đụng tới** — nhãn của owner ở nguyên đó (`annotator='human'`,
813 dòng), nên **không có migrate nào** và mọi đường code cũ chạy y như trước.
Tách bảng vì `records.data` trộn **trạng thái clip** (recut/excised/rejected/split/
gold_text/gợi ý teacher — owner sở hữu, **không phải per-annotator**) với **phán
đoán nhãn**; nhét annotator vào khoá `records` sẽ nhân bản trạng thái clip và sinh
dòng annotator mang cờ `rejected` mà họ không có quyền đặt.

API (`store.py`): `assign()` cài hàng đợi (**từ chối ghi đè** hàng đợi đã có câu
trả lời) · `next_seq()` · `assignment_clip()` · `save_rating()` · `progress()` ·
`all_ratings()`. Skip = dòng có `skip_reason`, `emotion` rỗng.

**Auth + role** (`auth.py`, change 011): `tokens.json` trong data root (gitignored)
map token → `{id, role}`; role `admin` (owner) vs `annotator`. Biên bảo mật = **một
middleware `guard`** trong `server.py`, deny-by-default: chỉ `/rate.html` +
`/rate.js` là public, mọi route **không** thuộc `/rate/*` là **owner-only** (route
thêm sau này mặc định được bảo vệ). Loopback được coi là admin **chỉ khi** không có
header `x-forwarded-*` — tunnel nối qua localhost nên nếu tin socket thôi sẽ trao
admin cho cả internet; `--no-local-admin` là lớp thứ hai, **bắt buộc khi tunnel mở**.
`access.log` ghi ai nghe clip nào lúc nào (ADR-005 safeguard #6), không công bố.

**Route annotator:** `GET /rate/next` (chỉ `{seq, done, total}`) · `GET
/rate/clip/{seq}.wav` (địa chỉ hoá **theo vị trí hàng đợi** — annotator không bao
giờ biết `epKey`/`clip_id`, không liệt kê được corpus) · `POST /rate/{seq}` ·
`GET /rate/whoami`. UI `rate.html`/`rate.js` **mù**: không transcript, không gợi ý
teacher, không nhãn owner.

Script: `build_assignments.py` (phân tầng + gold + dup + xáo trộn per-annotator) ·
`iaa_report.py` (Fleiss κ + Krippendorff α, nhãn-của-record). Giao thức + runbook:
[change 011](../../docs/spec/changes/011-online-multi-annotator/README.md).

`gold.csv` / `gold_bundle.zip` = **view export** dựng thẳng từ `state.db`
(gồm cột `gender`/`age_group` per-clip; dump thô; export Kaggle đầy đủ — strip text
public, loại rejected/test-series — là phase 4).

## REST API

| Method · path | Việc |
|---|---|
| `GET /episodes` | list tập + `total/done/rejected` |
| `GET /episode/{epKey}` | clips (join CSV + gợi ý teacher + record) |
| `GET /clip/{epKey}/{id}.wav` | serve clip (range) |
| `GET /context/{epKey}/{id}.wav` `?pad=10` | phát ngữ cảnh `[start−pad, end+pad]` cắt từ audio gốc của tập (chỉ đọc) |
| `GET /gold` | toàn bộ record (cho export) |
| `GET /script/{epKey}` | `{duration, blocks:[{start,end,text}]}` — script YouTube de-rolled (segment mode) |
| `GET /segment-audio/{epKey}.wav` `?a&b&pad` | slice vocals đã tách nhạc `[a−pad, b+pad]` (preview vùng, chỉ đọc) |
| `POST /segment/{epKey}` `{a,b,text}` | cắt clip MỚI từ vocals cho vùng `[a,b]` + seed record (`manual_segment`, gold_text=text YT) |
| `POST /gold/{epKey}/{id}` | lưu nhãn `{emotion,valence,arousal,gold_text,gender,age_group,dialect,annotator}` (distress/note: server default) |
| `POST /recut/{epKey}/{id}` `{a,b,text}` · `/undo` | trim (giữ `[a,b]`) + backup `_orig/` · khôi phục (`/undo` cũng xoá `excised`) |
| `POST /excise/{epKey}/{id}` `{a,b,text}` | bỏ đoạn GIỮA `[a,b]`, nối phần còn lại (1 clip); ghi `excised`; undo dùng chung `/recut/undo` |
| `POST /reject/{epKey}/{id}` `{reason}` · `/undo` | flag rejected (giữ file) · gỡ |
| `POST /reject-bulk/{epKey}` `{ids,reason}` | loại (reject) nhiều clip đã chọn trong 1 giao dịch |
| `POST /split/{epKey}/{id}` `{ts:[t1…tk]}` · `/undo` | chia k+1 con `seg<max+1…>`, cha giữ+reject · gỡ |

Path traversal chặn (mọi `epKey/clip_id` resolve dưới `--root`). `clip_id` khớp `^seg\d+$`.

## Chức năng

- **Cắt thủ công (✂ cắt thủ công, per tập):** cho tập **chưa label** mà auto-cut
  (VAD∩turn) đang cắt mất context. Overlay: **script YouTube** de-rolled
  (`youtube_transcripts.txt`, `GET /script`) làm view chính; click 1 block chọn
  vùng, shift-click block khác **gộp** vùng; waveform của vùng (`GET
  /segment-audio` từ **vocals đã tách nhạc**), `▶ nghe` kèm **± ngữ cảnh** (0/1/2/3s
  cắt từ audio đầy đủ — nghe lại phần bị mất), nút chỉnh mép `đầu/cuối ±0.2s`, ô
  text seed từ script (sửa được). `＋ tạo clip` → `POST /segment` cắt vocals
  `[a,b]` thành clip mới (seg kế tiếp, `manual_segment`), vào bảng để label như
  thường. **Auto clip giữ nguyên** (thêm vào, không xoá). ⚠️ Người tự chọn vùng →
  **người chịu trách nhiệm single-speaker (I3)** thay cho auto; dùng `>>` trong
  caption + split/multi để giữ đơn-giọng.
- **Label:** chọn emotion (phím `1`–`7` hoặc click), valence/arousal (**không
  default**, `—` tới khi chọn), **giới tính + tuổi** (2 dropdown, chọn thẳng khi
  nghe giọng — không bắt buộc; lưu per-clip trong `state.db`, hiện ở 2 cột cuối
  bảng). distress/note bỏ khỏi form 2026-07-10,
  quyết định user. Teacher hiển thị
  **read-only bên cạnh, KHÔNG pre-fill** (ADR-003). `Enter`/`Xác nhận` → lưu +
  tự nhảy clip chưa-nhãn kế.
- **F1 recut + text:** `✂ cắt` → kéo chọn đoạn GIỮ trên sóng → `✔ lưu cắt`
  (`soundfile` trim, backup `_orig/`); `↩ gốc` = undo. Ô text (`gold_text`) sửa được.
- **F7 excise (bỏ giữa):** trong chế độ `✂ cắt`, kéo chọn đoạn GIỮA bị nhiễu →
  `⌦ bỏ giữa` → server xoá `[a,b]` khỏi audio, **nối `[0,a]+[b,dur]` thành 1
  clip** (không chia đôi). `start/end` giữ nguyên biên bao; đoạn bỏ ghi vào
  `excised` (giây clip-local, provenance — không mất im lặng). `↩ gốc` khôi phục
  audio pristine + xoá `excised`. Đoạn bỏ phải nằm GIỮA (mép → dùng `✔ lưu cắt`).
- **Nghe từ vị trí chọn (seek):** click trên sóng (chế độ thường, không cut/split)
  → dời con trỏ phát tới đó; `Space` phát tiếp từ vị trí đó thay vì từ đầu.
- **Nghe ±N (ngữ cảnh):** nút `▶ nghe ±` + dropdown chọn **N giây** (1/3/5)
  phát đoạn `[start−N, end+N]` cắt từ audio gốc của tập (`audio_full.wav`, fallback
  `vocals_16k`) ở **player riêng** — nghe trước/sau clip để soát cắt/đa giọng;
  không đổi sóng/clip chính; bấm lại để dừng (tự tắt khi phát clip hoặc chuyển
  clip). Read-only (`GET /context?pad=N`).
- **F2 progress:** sidebar `done/eff ⚑rej` mỗi tập; header `Σ done/eff (%)`.
- **F3 reject:** `⚑ loại` + reason (`multi_speaker/noise/bad_cut/other`) — **giữ
  file**, loại khỏi `done`/export; `↺ bỏ loại`.
- **F9 loại nhiều clip (multi-select):** tick ô ☑ mỗi dòng (ô ở header = chọn/bỏ
  tất cả) → thanh trên bảng `⚑ loại đã chọn (N)` + chọn lý do → reject cả loạt 1
  lần (`POST /reject-bulk`, giữ file, loại khỏi export như F3). `bỏ chọn` xoá lựa
  chọn; un-reject từng clip qua `↺`. Lựa chọn theo từng tập (đổi tập là xoá).
- **F5 multi-split:** `⁄ chia` → click nhiều điểm chia (vạch cam; click lại để
  bỏ) → `✔ chia (k+1)` → k+1 clip mới (id `seg` kế tiếp), mỗi con kế thừa
  asr/yt/opus/sonnet của cha; cha giữ nguyên nhưng status→reject(`split`); mỗi
  con label riêng (giới tính/tuổi kế thừa từ cha + text + emotion); undo xoá con +
  un-reject cha.
- **Export:** `gold.csv` / ZIP (dump state; media wav = local-only).
- **Phím tắt:** `Space` play · `1`–`7` emotion · `Enter` xác nhận · `N`/`P`
  next/prev.

## Ràng buộc & invariants

- **Media legality (§1):** clip `.wav` + `state.db` (+`-wal`/`-shm`) + `clips/_orig/`
  + ZIP là **media/local-only**, không commit/release. `data/**` gitignored. Artifact
  releasable = features + timestamps + labels + speaker id.
- **I3 single-speaker:** clip đơn-giọng theo diarization (`segments.csv`); tai người
  bắt điểm mù bằng cờ `multi` / reject / split. **F7 excise** bỏ nhiễu GIỮA một
  giọng — giữ đơn-giọng (không gộp 2 giọng), `_orig/` + `excised` bảo toàn provenance.
  **Cắt thủ công** chuyển I3 sang **người bảo đảm** (auto VAD∩turn không còn ép):
  vùng người chọn có thể trúng ≥2 giọng → phải giữ đơn-giọng bằng `>>` caption +
  split/multi; đây là đánh đổi để không mất context (auto cắt quá sát).
- **I4 speaker-disjoint:** hold-out **whole-series** (ADR-002) — 2 phim khác đoàn
  làm phim ⇒ cast rời, disjoint đảm bảo ở **tầng series** (`build_split.py`), không
  cần speaker-id per-clip (đã bỏ). `tests/invariants/test_speaker_disjoint.py`
  thuộc change 001 (chưa dựng).
- **I6:** accuracy/UAR nêu test-split speaker-disjoint; tin cậy nhãn = κ
  **human–human**; teacher **không** báo như baseline (nhãn người bị neo).
- **ADR-003:** nhãn người là nguồn sự thật duy nhất; teacher = gợi ý.

## Biên đã biết / nợ

- **Frontend chưa browser-drive:** verify = API e2e + DOM-stub load-test + served
  200. Tương tác thật (kéo chọn, chia, dropdown) cần người click-test.
- **Single-pass** (1 annotator/clip) ⇒ **chưa có κ human–human** để báo (ADR-003
  known gap). Đang xử lý: [change 011](../../docs/spec/changes/011-online-multi-annotator/README.md)
  (tool label online đa annotator, cho phép bởi [ADR-005](../../docs/spec/decisions/ADR-005-annotation-streaming-not-release.md)).
  Đã xong M2 (bảng `ratings`); còn auth/role, UI `/rate`, tunnel, và 2 vòng label.
- **Nhân khẩu per-clip (bỏ speaker/cast 2026-07-20, migrate 2026-07-21):** record
  (nay trong `state.db`) còn giữ trường `speaker` (không migrate — vô hại, không ai
  đọc); 232 clip đã gán nhân vật được backfill `gender`/`age_group` từ `cast.json`
  qua migrate, `cast.json` giữ làm nguồn. `build_kaggle_gold.py` hiện vẫn bỏ
  speaker/gender/age (note cũ) — khi đủ nhãn per-clip nên thêm `gender`/`age_group`
  vào manifest (follow-up downstream).
- **Độ bền `state.db` ([ADR-004](../../docs/spec/decisions/ADR-004-labeler-state-durability.md)):**
  SQLite/WAL cho ACID + `integrity_check` + hot-backup, nhưng **lock-file 1-writer +
  backup xoay vòng tự động CHƯA build** — vẫn phải tắt server trước khi chạy script
  ghi (vd `migrate_*`). `state.jsonl` cũ giữ lại làm nguồn bootstrap, **đông cứng**
  (server không ghi vào nữa).
- **Cắt thủ công — nợ:** dùng script YT làm view (chưa render waveform full-track
  14′), timestamp M:SS (giây) nên mép ~±0.5s → phải nudge + nghe; chưa overlay
  speaker-turn (`diar_turns.csv`) để cảnh báo đa giọng. 1/33 tập thiếu
  `youtube_transcripts.txt` → script rỗng cho tập đó.
- **Export Kaggle đầy đủ = phase 4** (chưa build): nhãn human + loại rejected +
  loại test-series + strip text ở bản public.
- **Series test = quyết định người** (ADR-002), chưa chốt.

## Tham chiếu

- ADR: [001 blind-gold](../../docs/spec/decisions/ADR-001-blind-gold-annotation.md)
  (superseded bởi 003) · [002 whole-series test-split](../../docs/spec/decisions/ADR-002-whole-series-speaker-disjoint-gold.md)
  · [003 human labels](../../docs/spec/decisions/ADR-003-human-labels-drop-weak-supervision.md)
  · [004 state durability (SQLite)](../../docs/spec/decisions/ADR-004-labeler-state-durability.md).
- Change: [003 human-labeling-tool](../../docs/spec/changes/003-human-labeling-tool/README.md)
  (phase 0–5) · [004 refactor](../../docs/spec/changes/004-labeler-refactor/README.md).
- Feature detail + quyết định đã chốt: [`SPEC-features.md`](SPEC-features.md).
