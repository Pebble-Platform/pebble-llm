# Implement Plan — Turn-aware cutting (cắt utterance tại ranh giới đổi người nói)

- **Executor:** Opus agent · **Ngày:** 2026-07-03 · **Người viết plan:** session chính
- **Goal:** utterance đơn-người-nói **by construction** — cắt tại (VAD ∩ speaker-turn) thay vì
  chỉ VAD — trong CẢ HAI file: `scripts/vietnamese-ser/pilot_extract.py` (local) và
  `kaggle/vietnamese-ser/vnser-extract/vnser-extract.py` (kernel batch). Lý do (tracking doc
  M-note 2026-07-03): file nhiều giọng = nhãn mất nghĩa + phá speaker-disjoint split.

## Thiết kế (đã chốt — làm đúng, không đổi kiến trúc)

### Thuật toán turn-split (áp cho từng VAD region ĐÃ MERGE, TRƯỚC bước cắt 2–10s)
1. Input: (a) list VAD regions `[start,end]` (sau merge gap<0.4s, trước split 2–10s);
   (b) list diarization turns `[(start,end,speaker)]` từ pyannote.
2. Với mỗi region: giao với từng turn → các mảnh `(s,e,speaker)`. Khoảng thời gian được
   ≥2 turn phủ CHỒNG LẤN (2 người nói cùng lúc) → **bỏ hẳn** (không gán cho ai).
   Khoảng trong region không thuộc turn nào → gán speaker="" (diarization sót).
3. Merge các mảnh liên tiếp CÙNG speaker cách nhau <0.4s.
4. Sau đó mới áp logic cũ: mảnh dài >10s chia đều ≤10s; mảnh <2s bỏ.
5. `segments.csv` thêm cột `speaker` (giữa `dur` và `clip`): `id,start,end,dur,speaker,clip`.
   Không có diarization → cột speaker để rỗng, pipeline chạy y như cũ (fallback bắt buộc).

### Local (`pilot_extract.py`)
- Flag mới `--turn-split` (chỉ hợp lệ khi có `--hf-token`; thiếu token → lỗi rõ ràng).
- Tách stage: diarization chạy TRƯỚC khi dựng segments khi `--turn-split` bật; **lưu raw turns
  ra `diar_turns.csv`** (`start,end,speaker`) và cache stage này (tồn tại → không chạy lại
  pyannote). Giữ nguyên `speakers.csv` per-segment như cũ (tính sau khi có segments).
- Nhớ các fix đã có, KHÔNG regress: pyannote 4.x dùng `token=` + waveform-dict qua soundfile
  (né torchcodec) + `getattr(diar, "speaker_diarization", diar)`; stdout utf-8.

### Kernel (`vnser-extract.py`)
- Turn-split **mặc định BẬT** khi có HF_TOKEN secret (scale cần đơn-giọng ngay từ đầu);
  không token → in cảnh báo + fallback cắt kiểu cũ. Kernel dùng pyannote **3.x**:
  `use_auth_token=`, đọc file trực tiếp được (torchaudio 2.5.1 còn backend) — đừng bê
  nguyên code 4.x của local sang.
- Giữ smoke mode `VNSER_SMOKE=1` hoạt động (không token → đi nhánh fallback).

## Ràng buộc dữ liệu QUAN TRỌNG

- **TUYỆT ĐỐI không sửa/xóa gì trong `data/vietnamese-ser/pilot/ep01/`** — 158 segment id cũ
  đang được `labels_*.csv`, `transcripts_yt.csv`, `m4_report.md` tham chiếu. Chạy thử phiên
  bản mới vào **outdir riêng** `data/vietnamese-ser/pilot/ep01-turnsplit/` (xem Verify).
- KHÔNG sửa `docs/tasks/*` (trừ khi plan này yêu cầu — không yêu cầu). KHÔNG commit git.
  KHÔNG push Kaggle. Được phép cập nhật `scripts/vietnamese-ser/README.md` (thêm flag mới).

## Verify trước khi báo xong (bắt buộc)

1. `python -m py_compile` cả 2 file pass.
2. **Fallback không regress:** chạy kernel script `VNSER_SMOKE=1` KHÔNG token (nhánh cũ)
   trên `data/vietnamese-ser/raw/smoke60.wav` (đã có từ M5) → segments.csv + transcripts.csv
   ra bình thường, cột speaker rỗng, exit 0.
3. **Turn-split end-to-end trên ep01:** tạo `data/vietnamese-ser/pilot/ep01-turnsplit/`,
   copy 2 file `audio_full.wav` + `vocals_16k.wav` từ `ep01/` vào (2 stage đầu sẽ cache-skip),
   rồi chạy `pilot_extract.py --input data/vietnamese-ser/raw/ep01.mp3 --outdir <dir mới>
   --turn-split --hf-token <token user đã cấp — lấy trong git log KHÔNG có, hỏi session chính
   nếu thiếu; token: <REDACTED — lấy từ session chính, không ghi vào file> --skip-asr`
   (pyannote sẽ chạy lại 1 lần ~15–30 phút CPU — chấp nhận; ASR bỏ qua cho nhanh).
4. **Kiểm tra kết quả turn-split:** (a) mọi dòng segments.csv mới có speaker khác rỗng;
   (b) không utterance nào >10s hoặc <2s; (c) đối chiếu độc lập: với 10 segment mới ngẫu
   nhiên, giao lại với `diar_turns.csv` → đúng 1 speaker/segment; (d) bảng so sánh baseline:
   158 utt / 11.9 min / 54% đơn-giọng  →  N mới / X min / 100% đơn-giọng (kỳ vọng: N tăng,
   X giảm nhẹ do bỏ overlap + mảnh <2s).
5. Chạy lại lệnh (3) lần nữa → idempotent (cache diar_turns.csv, không gọi lại pyannote).

## Báo cáo cuối (final message, ≤12 dòng)

Bảng so sánh baseline↔turn-split (số utt, phút, % đơn-giọng, phút overlap bị bỏ) ·
fallback smoke pass/fail · idempotent pass/fail · file đã sửa + file output mới.
