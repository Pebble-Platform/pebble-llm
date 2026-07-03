# M5 Implement Plan — Scale plan từ số thật + port Kaggle + shortlist phim

- **Executor:** Opus agent · **Ngày:** 2026-07-03 · **Người viết plan:** session chính
- **Goal:** biến kết quả pilot ep01 thành (1) bản scale-plan tính bằng SỐ ĐO THẬT,
  (2) design doc cập nhật số thật, (3) kernel Kaggle port pipeline lên GPU,
  (4) shortlist phim ứng viên. **Quyết định GO cuối cùng thuộc về user — plan này chuẩn bị, không quyết.**

## Hằng số ĐO THẬT từ pilot (dùng đúng các số này, không ước lượng lại)

| Đại lượng | Giá trị đo |
|---|---|
| 1 tập 35.6 phút → thoại sạch | 11.9 phút (yield 33%), **158 utterance**, median 3.9s |
| Auto-filter loop/unk giữ | 95% |
| Đơn-người-nói (pyannote, LẠC QUAN — có gộp giọng nữ giống nhau) | 54% |
| Số giọng/tập | 18 |
| κ 2-teacher (Opus↔Sonnet, 7 lớp) | 0.584 · 69% raw · 109/158 đồng thuận |
| Similarity PhoWhisper↔YouTube | mean 87.2 / median 90.5 |
| Mục tiêu design doc hiện tại (§3, TRƯỚC pilot) | weak pool "50–100h (~40–80k utt)", gold 2–3k utt |

## Các bước

### S1 — Scale math → `docs/papers/vietnamese-ser/05-scale-plan.md` (file mới)
Tính và trình bày bảng cho 3 kịch bản **1 / 3 / 6 bộ phim** (giả định 40 tập × ~36 phút/tập):
- giờ thoại sạch = tập × 11.9 phút; số utterance = tập × 158; số utt đơn-người-nói ≈ ×0.54
  (ghi rõ caveat lạc quan + phần multi-speaker có thể cứu bằng turn-split);
- đối chiếu với mục tiêu §3 design doc → **kết luận trung thực**: mục tiêu "50–100h" cần
  ~250–500 tập (không thực tế cho 1 người) → đề xuất mục tiêu sửa đổi (ví dụ 3 bộ ≈ 120 tập
  ≈ ~24h sạch / ~19k utt ≈ 6–7× ViSEC) — trình như KHUYẾN NGHỊ kèm 2 phương án, user chọn;
- chi phí Kaggle: ước lượng GPU-phút/tập cho từng stage (Demucs/PhoWhisper/pyannote trên
  P100), tổng theo kịch bản, so với quota **30h P100/tuần, tối đa 2 session** → số tuần cần;
- chi phí weak-label 2-teacher theo kịch bản (dùng giá Batch API: Opus $2.5/$12.5,
  Sonnet $1/$5 per 1M token sau giảm 50%; ~150 token/utt input + ~40 out);
- mục Rủi ro: upload tập phim lên Kaggle private dataset = đưa media bản quyền lên bên thứ ba
  (dù private) — nêu 2 phương án (Kaggle private vs chạy local GPU nếu có) để user quyết.

### S2 — Cập nhật design doc `docs/papers/vietnamese-ser/04-pioneer-corpus-design.md`
CHỈ sửa có phạm vi: (a) §3 bảng quy mô — thêm cột "số đo thật từ pilot" + sửa target theo
khuyến nghị S1 đánh dấu `(đề xuất sau pilot, chờ chốt)`; (b) §8 timeline — thay ước lượng
bằng số tuần tính từ S1. KHÔNG sửa mục khác.

### S3 — Kernel Kaggle: `kaggle/vietnamese-ser/vnser-extract/`
Port pipeline pilot lên GPU, xử lý HÀNG LOẠT tập:
- **Copy pattern repo:** xem `kaggle/finetuning-message/r2-corn-gce/kernel-metadata.json`
  làm mẫu metadata (script kernel, `enable_gpu: true`, `enable_internet: true`,
  `is_private: true`; id đặt `phatneurondai/vnser-extract`; dataset_sources để
  `["phatneurondai/vnser-episodes"]` — dataset user sẽ tạo sau).
- **Stack pin (gotcha P100 = sm_60):** cell đầu pip install
  `torch==2.5.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121`
  rồi `demucs silero-vad transformers soundfile pyannote.audio==3.*`.
  ⚠ pyannote **3.x** trên Kaggle (torch 2.5.1 không chạy pyannote 4.x mới nhất):
  3.x dùng `use_auth_token=` (KHÁC bản local 4.x dùng `token=`) và pipeline
  `pyannote/speaker-diarization-3.1` thật. torchaudio 2.5.1 còn backend nội bộ
  → KHÔNG cần shim soundfile trên Kaggle.
- **Logic:** loop mọi file audio/video trong `/kaggle/input/vnser-episodes/**`;
  mỗi tập chạy đủ stage (ffmpeg→demucs→VAD→cut→PhoWhisper→diarization) tái dùng cấu trúc
  hàm của `scripts/vietnamese-ser/pilot_extract.py` (import không được — copy hàm vào kernel,
  một file tự chứa theo pattern repo); output `/kaggle/working/<ep>/`:
  `segments.csv, transcripts.csv, speakers.csv, clips/` + `report.md`; cuối cùng in tổng hợp.
- **HF token:** `from kaggle_secrets import UserSecretsClient` → secret tên `HF_TOKEN`;
  nếu thiếu secret → bỏ diarization, in cảnh báo, KHÔNG crash.
- **Smoke mode local:** env `VNSER_SMOKE=1` → chỉ xử lý 60s đầu của file đầu tiên, bỏ
  diarization — để test CPU local trước khi push.

### S4 — Shortlist phim (web research, KHÔNG tải gì)
Trong `05-scale-plan.md`, thêm bảng 5–8 ứng viên phim truyền hình VN thể loại tâm lý/gia đình:
tên, số tập, năm, kênh YouTube chính thức (VTV/SCTV/THVL/kênh hãng), có caption không
(kiểm tra bằng WebSearch/WebFetch trang video nếu được), ghi chú mật độ thoại. Ưu tiên kênh
CHÍNH THỨC (giảm rủi ro nguồn). Cột cuối: "cần user xác nhận caption + chất lượng audio".
Không đưa link tải, không hướng dẫn tải.

## Ràng buộc

- KHÔNG sửa `docs/tasks/*` (session chính giữ). KHÔNG commit git. KHÔNG push kernel lên Kaggle.
- KHÔNG tải media. Mọi lệnh python kèm `PYTHONIOENCODING=utf-8`.
- Số trong S1/S2 phải truy ngược được về bảng hằng số ở trên (ghi phép tính, không ghi số trần).

## Verify trước khi báo xong (bắt buộc)

1. `python -m py_compile` kernel script pass.
2. **Smoke local:** tạo `data/vietnamese-ser/raw/smoke60.wav` bằng
   `ffmpeg -y -ss 60 -t 60 -i data/vietnamese-ser/pilot/ep01/audio_full.wav ...` rồi chạy kernel
   script với `VNSER_SMOKE=1` trong `.venv-vnser` (nhớ `PYTHONPATH=scripts/vietnamese-ser` để
   ăn shim torchaudio local) trỏ input vào thư mục chứa smoke60.wav → phải ra segments.csv +
   transcripts.csv không rỗng, exit 0.
3. Mọi con số trong 05-scale-plan.md: kiểm tra lại số học (tập × 11.9 phút, × 158 utt...).
4. `kernel-metadata.json` là JSON hợp lệ và các trường khớp pattern repo.

## Báo cáo cuối (final message, ≤15 dòng)

Kịch bản khuyến nghị + số giờ/utt của nó · GPU-h & số tuần quota · chi phí label 2 kịch bản
· smoke test pass/fail · top-3 phim ứng viên (kèm trạng thái caption) · đường dẫn 3 deliverable.
