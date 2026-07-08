# Phase 3 — F2 progress + F3 reject

**Status:** done (2026-07-07) — F2: `/episodes` trả `done`+`rejected`, sidebar
`done/eff ⚑rej` + header `Σ done/eff (%)`. F3: `POST /reject` + `/reject/.../undo`
(flag `rejected`/`reject_reason` trong `state.jsonl`, **giữ file**); `done` loại
rejected (`done = emotion & not rejected`, `eff = total − rejected`). Frontend:
dropdown reason + nút loại/bỏ-loại, hàng rejected mờ + `⚑`. **E2E verify**: reject
→ done 1→0, rejected 0→1, emotion giữ qua merge; unreject khôi phục. Chưa
browser-drive.
**Depends on:** phase 1 (`state.jsonl`)

**Goal:** hiển thị tiến độ % theo tập (tính từ `state.jsonl`), và cho **đánh dấu
clip không đạt chuẩn (reject)** — flag trong state, **giữ file** `.wav`.

## Scope

- **In (F2):** sidebar mỗi tập `done/total` + **%**; header `Σ done/Σ total · %`
  — tính trực tiếp từ `state.jsonl`, không file progress riêng.
- **In (F3):** `POST /reject/{epKey}/{id}` `{reason}` (`multi_speaker / noise /
  bad_cut / other` + note) → `rejected=true` + `reject_reason` vào `state.jsonl`.
  Un-reject được. Clip rejected: không tính `done`, hiện mờ + `⚑`.
- **Out:** downstream loại rejected khỏi export (phase 4); xoá/di chuyển file
  (đã quyết KHÔNG — chỉ flag).

## Exit criteria

- Label thêm/bớt/reject → % ở sidebar + tổng ở header cập nhật ngay, khớp đếm tay.
- Reject 1 clip → `state.jsonl` `rejected=true`+reason; file `.wav` **còn nguyên**;
  clip rời khỏi `done`; un-reject phục hồi.
- Restart server → % và trạng thái reject giữ nguyên (từ `state.jsonl`).

## Verification

| # | Intent | Check | Where |
|---|---|---|---|
| 1 | % đúng | Tập 175 clip, label 42, reject 3 → done 42/172 (?) — định nghĩa mẫu số rõ (total trừ rejected) | manual + unit |
| 2 | Reject giữ file | Sau reject, `clips/seg*.wav` vẫn tồn tại | manual |
| 3 | State bền | Restart → reject/% nguyên | manual |

## Review notes

- **Định nghĩa `done`/`total` khi có reject** phải chốt: đề xuất `total_effective =
  total − rejected`, `done` = số clip đã gán nhãn (không tính rejected). Ghi rõ để
  % không nhảy khó hiểu.
- Reject là **công cụ thủ công hỗ trợ I3** — bắt clip đa-giọng/rác mà cắt tự động
  bỏ sót (tai người nghe ra). Downstream phải tôn trọng (phase 4).
- Không có file `rejects.csv`/`progress.json` riêng — **một `state.jsonl`** (quyết
  2026-07-07). Đừng tách lại.
