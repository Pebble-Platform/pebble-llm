# Phase 2 — F1: recut + edit text

**Status:** done (2026-07-07) — `POST /recut` (soundfile trim, atomic
tmp→rename, backup `clips/_orig/` lần đầu) + `POST /recut/.../undo`; record
merge qua `_seed_record` (recut giữ nhãn, /gold giữ recut). Frontend: cut-mode
kéo chọn trên waveform + `#g-text` (gold_text) + nút lưu/gốc. **E2E verify**:
recut 2.0→1.0s + `_orig` 2.0s, biên 1.0/2.0→1.5/2.5, **emotion giữ qua merge**,
undo khôi phục hết + giữ emotion, empty-sel→400. Frontend syntax+served+wired;
chưa browser-drive.
**Depends on:** phase 1 (`state.jsonl` schema)

**Goal:** trong lúc label, cho **cắt lại (trim) clip** qua popup và **sửa text**
cho khớp audio mới. Cắt server-side bằng `soundfile` (atomic, giữ sample-rate),
backup bản gốc, có **Hoàn tác**.

## Scope

- **In:** `POST /recut/{epKey}/{id}` `{a,b,text}` → backend: (1) backup
  `clips/seg*.wav → clips/_orig/seg*.wav` lần recut đầu (nếu chưa có); (2)
  `soundfile` cắt `[a,b]`, atomic overwrite `seg*.wav`; (3) cập nhật
  `start'=start+a`, `end'=start+b`, `recut=true`, `gold_text` vào `state.jsonl`.
  `POST /recut/.../undo` → copy `_orig/` về + revert `start/end/gold_text/recut`.
  Frontend: popup waveform clip (kéo chọn `[a,b]`, nghe vùng), field text sửa
  được (prefill từ ASR), nút Lưu / Hoàn tác. Loader **bỏ qua `_orig/`**.
- **Out:** cắt từ `audio_full` / nới rộng biên (ngoài scope — chỉ trim trong
  clip); reject (phase 3).

## Exit criteria

- Recut 1 clip → `seg*.wav` ngắn lại đúng `[a,b]`, `_orig/seg*.wav` giữ bản gốc,
  `state.jsonl` có `recut=true` + biên/`gold_text` mới. Nghe lại đúng đoạn.
- **Hoàn tác** → `seg*.wav` == bản gốc byte-for-byte, `recut=false`, biên/text
  revert.
- Sample-rate + kênh của clip sau recut **giữ nguyên nguồn** (`soundfile`, không
  re-encode 16-bit như browser).

## Verification

| # | Intent | Check | Where |
|---|---|---|---|
| 1 | Cắt đúng + atomic | Recut → dur mới ≈ b−a (±1 frame); không có file cụt khi lỗi giữa chừng | manual + unit (soundfile) |
| 2 | Backup + Undo đảo ngược | `sha256(seg sau undo) == sha256(_orig)` | unit test |
| 3 | Giữ provenance | `transcripts.csv` KHÔNG bị sửa; divergence đánh dấu bằng `recut` | code review |
| 4 | Đơn-giọng vẫn giữ (I3) | Recut không tạo clip đa-giọng mới (người tự kiểm khi cắt) | manual |

## Review notes

- **Overwrite là phá huỷ** — backup `_orig/` + Undo là lưới an toàn; đừng bỏ để
  "tiết kiệm disk" (chỉ clip bị recut mới tốn).
- `gold_text` là **text của record** thay ASR/model (ADR-003) — vào `state.jsonl`,
  ra Kaggle-private để train, **strip khỏi public** (phase 4 / intent §1).
- Popup recut dùng chung vùng waveform với `cut.html` — cân nhắc tách 1 module JS
  chung, nhưng đừng hợp nhất 2 trang ở change này (judgment call #4).
