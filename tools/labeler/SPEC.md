# Spec — `tools/labeler/` (human labeling UI + FastAPI backend)

> Công cụ **con người gán nhãn** cho ViEmoSpeech. Tầng **execution** — phải thỏa
> `docs/intent/` + `docs/spec/capabilities/extraction-pipeline.md`.
> Cập nhật: 2026-07-08 (khớp code đã build: phase 0–5 + refactor change 004).
> Chi tiết tính năng: [`SPEC-features.md`](SPEC-features.md). Lịch sử build:
> [change 003](../../docs/spec/changes/003-human-labeling-tool/README.md) (phase
> 0–5) + [change 004](../../docs/spec/changes/004-labeler-refactor/README.md) (refactor).

## Vị trí trong pipeline

Pipeline (`extraction-pipeline.md`) trích **clip sạch** (cắt tại speaker-turn) +
text + **gợi ý** 2-teacher (Opus/Sonnet). Con người gán **nhãn của record** cho
từng clip qua công cụ này ([ADR-003](../../docs/spec/decisions/ADR-003-human-labels-drop-weak-supervision.md):
nhãn người là corpus, teacher chỉ gợi ý). **Nguồn sự thật = `state.jsonl`**;
`gold.csv`/ZIP là *view export*. Constraint ràng: I4 (**test speakers ∩ train =
∅**, [ADR-002](../../docs/spec/decisions/ADR-002-whole-series-speaker-disjoint-gold.md))
và I6 (accuracy nêu test-split speaker-disjoint; tin cậy nhãn = κ **human–human**).

## Kiến trúc

**Backend** (FastAPI, `.venv-vnser`, bind `127.0.0.1`):
`server.py` (routes + models + main, mỏng) · `store.py` (config `ROOT/STATE` +
`state.jsonl` load/save + records + paths) · `episodes.py` (đọc CSV + dựng
`/episodes`, `/episode`) · `audio.py` (`soundfile` recut/split + backup `_orig/`).

**Frontend** (ES modules, nạp qua `<script type="module" src="main.js">`):
`state.js` (kernel `S` + consts) · `api.js` (mọi call server) · `view.js`
(waveform + render + select) · `actions.js` (confirm/recut/split/reject + export)
· `main.js` (DOM wiring + keyboard + init). `index.html` = markup thuần.

**Chạy** (từ repo root):
```
.venv-vnser/Scripts/python.exe tools/labeler/server.py --root data/vietnamese-ser/episodes
# mở http://127.0.0.1:8000/index.html  (cần server — không mở file:// trực tiếp)
```
`data/**` là media bản quyền, gitignored, **local-only** (intent §1).

## Data model — `state.jsonl` (nguồn sự thật)

Mỗi dòng JSON = 1 clip, khoá `(epKey, id)`. Ghi atomic (tmp→rename) sau mỗi mutation.

| Nhóm | Trường | Ghi chú |
|---|---|---|
| id | `epKey, id, series, episode` | |
| nhãn (F1) | `emotion` | 1/7: `joy sadness anger fear_anxiety surprise disgust neutral` (khớp `m4_prompt.md`) |
| | `valence, arousal` | int 1–5 (`null` khi chưa gán) |
| | `distress` | bool — proxy phim diễn, **không** lâm sàng (intent §7) |
| | `multi` | bool — tai người nghi ≥2 giọng |
| | `note` | text tự do |
| speaker (F6) | `speaker` | **người sửa được** (dropdown); mặc định = id diarization |
| biên | `start, end` | recut-aware (cộng dồn qua nhiều lần recut) |
| recut (F1) | `recut`, `gold_text` | `gold_text` = text người sửa sau recut |
| reject (F3) | `rejected`, `reject_reason` | reason `split` cho cha bị chia |
| split (F5) | `split_from` (con) / `split_children` (cha) | liên kết cha↔con |
| gợi ý | `opus, sonnet` | emotion 2 teacher — **chỉ tham chiếu**, không phải nhãn |
| provenance | `annotator, ts` | ai + khi nào (I2) |

`gold.csv` / `gold_bundle.zip` = **view export** dựng từ `state.jsonl` (dump thô;
export Kaggle đầy đủ — strip text public, loại rejected/test-series — là phase 4).

## REST API

| Method · path | Việc |
|---|---|
| `GET /episodes` | list tập + `total/done/rejected` |
| `GET /episode/{epKey}` | clips (join CSV + gợi ý teacher + record) + `speakers` |
| `GET /clip/{epKey}/{id}.wav` | serve clip (range) |
| `GET /gold` | toàn bộ record (cho export) |
| `POST /gold/{epKey}/{id}` | lưu nhãn `{emotion,valence,arousal,distress,multi,note,speaker?,annotator}` |
| `POST /recut/{epKey}/{id}` `{a,b,text}` · `/undo` | trim + backup `_orig/` · khôi phục |
| `POST /reject/{epKey}/{id}` `{reason}` · `/undo` | flag rejected (giữ file) · gỡ |
| `POST /split/{epKey}/{id}` `{t}` · `/undo` | chia 2 con `seg<max+1/+2>`, cha giữ+reject · gỡ |

Path traversal chặn (mọi `epKey/clip_id` resolve dưới `--root`). `clip_id` khớp `^seg\d+$`.

## Chức năng

- **Label:** chọn emotion (phím `1`–`7` hoặc click), valence/arousal (**không
  default**, `—` tới khi chọn), distress/multi, note, speaker. Teacher hiển thị
  **read-only bên cạnh, KHÔNG pre-fill** (ADR-003). `Enter`/`Xác nhận` → lưu +
  tự nhảy clip chưa-nhãn kế.
- **F1 recut + text:** `✂ cắt` → kéo chọn đoạn GIỮ trên sóng → `✔ lưu cắt`
  (`soundfile` trim, backup `_orig/`); `↩ gốc` = undo. Ô text (`gold_text`) sửa được.
- **F2 progress:** sidebar `done/eff ⚑rej` mỗi tập; header `Σ done/eff (%)`.
- **F3 reject:** `⚑ loại` + reason (`multi_speaker/noise/bad_cut/other`) — **giữ
  file**, loại khỏi `done`/export; `↺ bỏ loại`.
- **F5 split:** `⁄ chia` → click điểm chia (vạch cam) → `✔ chia đôi` → 2 clip mới
  (id `seg` kế tiếp), cha giữ nguyên nhưng status→reject(`split`); mỗi con label
  riêng (speaker + text + emotion); undo xoá con + un-reject cha.
- **F6 speaker sửa được:** dropdown speaker của tập + `＋ mới`.
- **Export:** `gold.csv` / ZIP (dump state; media wav = local-only).
- **Phím tắt:** `Space` play · `1`–`7` emotion · `Enter` xác nhận · `N`/`P`
  next/prev · `D` distress · `M` multi.

## Ràng buộc & invariants

- **Media legality (§1):** clip `.wav` + `state.jsonl` + `clips/_orig/` + ZIP là
  **media/local-only**, không commit/release. `data/**` gitignored. Artifact
  releasable = features + timestamps + labels + speaker id.
- **I3 single-speaker:** clip đơn-giọng theo diarization; tai người bắt điểm mù
  bằng cờ `multi` / reject / split.
- **I4 speaker-disjoint:** `state.jsonl.speaker` (người sửa được) → khoá
  `(series, episode, speaker)`; hold-out **whole-series** (ADR-002);
  `tests/invariants/test_speaker_disjoint.py` thuộc change 001 (chưa dựng).
- **I6:** accuracy/UAR nêu test-split speaker-disjoint; tin cậy nhãn = κ
  **human–human**; teacher **không** báo như baseline (nhãn người bị neo).
- **ADR-003:** nhãn người là nguồn sự thật duy nhất; teacher = gợi ý.

## Biên đã biết / nợ

- **Frontend chưa browser-drive:** verify = API e2e + DOM-stub load-test + served
  200. Tương tác thật (kéo chọn, chia, dropdown) cần người click-test.
- **Single-pass** (1 annotator/clip) ⇒ **chưa có κ human–human** để báo (ADR-003
  known gap); double-annotate subset là further work.
- **Speaker-id consistency (F6):** gõ id lệch → cùng giọng thành 2 id → rò I4;
  dropdown + review danh sách id trước khi dựng test-set.
- **Export Kaggle đầy đủ = phase 4** (chưa build): nhãn human + loại rejected +
  loại test-series + strip text ở bản public.
- **Series test = quyết định người** (ADR-002), chưa chốt.

## Tham chiếu

- ADR: [001 blind-gold](../../docs/spec/decisions/ADR-001-blind-gold-annotation.md)
  (superseded bởi 003) · [002 whole-series test-split](../../docs/spec/decisions/ADR-002-whole-series-speaker-disjoint-gold.md)
  · [003 human labels](../../docs/spec/decisions/ADR-003-human-labels-drop-weak-supervision.md).
- Change: [003 human-labeling-tool](../../docs/spec/changes/003-human-labeling-tool/README.md)
  (phase 0–5) · [004 refactor](../../docs/spec/changes/004-labeler-refactor/README.md).
- Feature detail + quyết định đã chốt: [`SPEC-features.md`](SPEC-features.md).
