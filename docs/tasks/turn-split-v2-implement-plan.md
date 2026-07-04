# Implement Plan v2 — Turn-split hybrid (sửa thiết kế v1: mất 50% material)

- **Executor:** Opus agent · **Ngày:** 2026-07-03 · **Tiếp nối:** `turn-split-implement-plan.md` (v1)
- **Bối cảnh:** v1 code ĐÚNG plan nhưng thiết kế plan sai → yield 11.9→5.5 phút, lợi ích ròng = 0
  (đo được: 5.5 = 3.4 giữ từ vùng đơn-giọng cũ [co từ 5.5] + 2.1 cứu từ vùng đa-giọng [6.4]).
- **Goal v2:** ~8–9+ phút đơn-giọng/tập — giữ nguyên vùng đơn-giọng, cứu nhiều hơn từ vùng đa-giọng.

## Cơ chế mất mát ĐÃ TRUY RA (thiết kế v2 phải trị đúng 3 bệnh này)

1. **Diarization vụn:** 895 turns/tập, trung bình 1.13s — giao với VAD tạo mảnh nhỏ, chết ở MIN_UTT=2.0.
2. **Lỗ hổng "" (không turn nào phủ):** trong 1 VAD region liên tục, turns không phủ kín →
   chuỗi mảnh `X, "", X` — merge v1 chỉ nối cùng-speaker nên mảnh X đầu (1–2s) chết lẻ.
   Đây là nguyên nhân CHÍNH làm vùng đơn-giọng co 5.5→3.4.
3. **MIN_UTT=2.0 quá cứng cho hội thoại ping-pong** (câu đáp "vâng ạ", "dạ" ~1–2s là hợp lệ).

## Thay đổi thiết kế (sửa hàm `turn_split()` trong CẢ 2 file — local + kernel)

Áp dụng theo thứ tự, trong cùng hàm:

- **T1 — Pre-merge turns:** trước khi giao, merge các turn LIỀN KỀ CÙNG speaker cách nhau <0.6s
  thành một turn (khử vụn pyannote).
- **T2 — Region đơn-speaker giữ nguyên (hybrid guarantee):** với mỗi merged-VAD region, xét các
  turn overlap thực chất (phần giao >0.05s — bỏ qua chạm-biên): nếu tất cả thuộc ĐÚNG 1 speaker
  (hoặc không có turn nào) → region là MỘT piece nguyên vẹn mang speaker đó (hoặc "") —
  KHÔNG cắt gì bên trong. Bảo đảm: vùng đơn-giọng baseline không bao giờ bị co nữa.
- **T3 — Trong region đa-speaker, xử lý mảnh "":** sau khi chia piece như v1:
  `X,"",X` → nhập "" vào X (một piece liền); `""` ở mép region cạnh X → nhập vào X;
  `X,"",Y` → cắt "" tại trung điểm, nửa đầu nhập X, nửa sau nhập Y. DROP (overlap ≥2 giọng)
  vẫn là barrier cứng như v1 — không nhập xuyên qua DROP.
- **T4 — MIN_UTT riêng cho mảnh turn-split:** hằng số mới `MIN_UTT_TURN = 1.5` (giây) áp cho
  pieces sinh từ region đa-speaker; region đơn-speaker (T2) và chế độ không-turn-split giữ
  MIN_UTT = 2.0 như cũ. Bước chia >10s giữ nguyên.
- Kernel: giữ turn-split default BẬT khi có HF_TOKEN (sau fix này yield ổn, bật là đúng cho scale).

## Verify (bắt buộc — thiết kế cho NHANH, không chờ pyannote)

1. `python -m py_compile` cả 2 file.
2. Chạy vào outdir MỚI `data/vietnamese-ser/pilot/ep01-turnsplit2/`:
   copy vào đó 2 wav từ `ep01/` **và copy `diar_turns.csv` từ `ep01-turnsplit/`**
   (cache hit → KHÔNG chạy lại pyannote — toàn bộ run chỉ vài phút) rồi:
   `PYTHONPATH=scripts/vietnamese-ser PYTHONIOENCODING=utf-8 .venv-vnser/Scripts/python.exe
   scripts/vietnamese-ser/pilot_extract.py --input data/vietnamese-ser/raw/ep01.mp3
   --outdir data/vietnamese-ser/pilot/ep01-turnsplit2 --turn-split --hf-token dummy --skip-asr`
   (token không dùng tới khi cache hit; nếu code hiện tại validate token trước cache → sửa để
   cache đi trước).
3. **Tiêu chí ĐẠT (so bằng script, in bảng):**
   - Tổng phút ≥ **8.0** (v1: 5.5; baseline đơn-giọng: 5.5);
   - Phân rã như đã đo ở v1: phần nằm trong vùng baseline-đơn-giọng ≥ **5.0** phút
     (v1: 3.4) VÀ phần cứu từ vùng đa-giọng ≥ **2.1** phút (v1: 2.1);
   - 100% piece có speaker (hoặc "" từ region không turn) · không piece nào <1.5s
     · piece từ region đơn-speaker không <2.0s · không piece >10.1s;
   - Cross-check 10 segment ngẫu nhiên với diar_turns (pre-merged): 1 speaker/segment
     (dung sai chạm-biên 50ms).
   Nếu tổng <8.0 nhưng ≥7.0 và 2 điều kiện phân rã đạt → báo PASS-với-ghi-chú (không fail cứng).
4. Fallback regression: kernel `VNSER_SMOKE=1` không token chạy lại OK (nhánh cũ không đổi).
5. Idempotent: chạy lại lệnh (2) → xong <30s, diar_turns.csv mtime không đổi.
6. KHÔNG đụng `ep01/` và `ep01-turnsplit/` (giữ làm baseline so sánh). KHÔNG commit, KHÔNG push.

## Báo cáo cuối (≤12 dòng)

Bảng 3 cột baseline / v1 / v2: tổng utt, tổng phút, phút-trong-vùng-đơn, phút-cứu-từ-đa,
% đơn-giọng · các check 3–5 pass/fail · file sửa.
