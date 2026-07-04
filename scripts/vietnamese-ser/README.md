# vietnamese-ser — pilot pipeline (phim truyền hình → utterance thoại sạch)

Tracking: [`docs/tasks/vn-tv-ser-pilot.md`](../../docs/tasks/vn-tv-ser-pilot.md) ·
Design: [`docs/papers/vietnamese-ser/04-pioneer-corpus-design.md`](../../docs/papers/vietnamese-ser/04-pioneer-corpus-design.md)

## Setup (một lần)

```powershell
# 1. ffmpeg phải có trên PATH (kiểm tra: ffmpeg -version). Nếu chưa: winget install ffmpeg
# 2. venv riêng (deps nặng, không đụng venv chính của repo)
uv venv .venv-vnser
.venv-vnser\Scripts\activate
uv pip install demucs silero-vad "transformers[torch]" soundfile
# 3. (tùy chọn — diarization) pyannote model bị gated:
#    - tạo HF token tại hf.co/settings/tokens
#    - accept điều khoản tại hf.co/pyannote/speaker-diarization-3.1 VÀ hf.co/pyannote/segmentation-3.0
uv pip install pyannote.audio
```

## Bố cục dataset (layout v2, 2026-07-04 — series-based)

```
data/vietnamese-ser/                     (toàn bộ gitignored — KHÔNG commit media)
  raw/<series>/epNN.mp3 + epNN.vi.srt    media + caption (download_youtube.py)
  episodes/<series>/epNN/                output chuẩn mỗi tập: segments.csv (cột speaker),
                                         clips/, transcripts.csv, transcripts_yt.csv,
                                         labels_*.csv, diar_turns.csv, report.md
  episodes/<series>/summary.csv          bảng tổng hợp do run_batch.py sinh
  _pilot-history/                        ep01 baseline + turn-split v1 + smoke (bằng chứng, đóng băng)
```

Canonical của ep01 (pilot) = `episodes/ve-nha-di-con/ep01/` (chính là bản
turn-split v2 + labels vòng 2; các bản so sánh cũ nằm trong `_pilot-history/`).

## Chạy BATCH nhiều tập (khuyến nghị)

```powershell
# 0. tải media + caption (resumable, parse "Tập N" từ title):
python scripts/vietnamese-ser/download_youtube.py --playlist <URL> --episodes 2-10 `
    --outdir data/vietnamese-ser/raw/ve-nha-di-con
# 1. chạy tuần tự (resumable — Ctrl-C rồi chạy lại vô hại; ~1.5–2h CPU/tập):
$env:HF_TOKEN="hf_xxx"; $env:PYTHONIOENCODING="utf-8"
python scripts/vietnamese-ser/run_batch.py --series ve-nha-di-con --episodes 2-10
```

`run_batch.py` tự: convert SRT→caption (auto-detect kiểu rolling của YouTube
auto-sub), gọi `pilot_extract.py --turn-split`, align YouTube, và ghi
`summary.csv`. Tập nào đủ output thì skip.

## Chạy lẻ 1 tập

```powershell
python scripts/vietnamese-ser/pilot_extract.py --input data/vietnamese-ser/raw/<series>/epNN.mp3 `
    --outdir data/vietnamese-ser/episodes/<series>/epNN --turn-split --hf-token hf_xxx
# chỉ đo yield, bỏ ASR: --skip-asr · ASR tốt hơn (chậm): --whisper vinai/PhoWhisper-medium
```

Mỗi stage cache kết quả — chạy lại lệnh là tiếp tục từ chỗ dừng.

## Thời gian chạy dự kiến (CPU, tập ~45 phút)

| Stage | Thời gian |
|---|---|
| ffmpeg | ~1 phút |
| Demucs (htdemucs) | ~20–40 phút |
| silero VAD | ~2 phút |
| cut | ~vài phút |
| PhoWhisper-base ASR | ~20–40 phút (theo lượng thoại) |
| pyannote (tùy chọn) | ~15–30 phút |

Scale nhiều tập → port sang Kaggle GPU (pattern kernel sẵn trong `kaggle/`).

## Ranh giới pháp lý (nhắc lại từ design doc §4)

File phim + audio cắt ra **chỉ dùng nội bộ nghiên cứu/thesis**, nằm trọn trong
`data/**` (gitignored). Không commit, không phát hành audio thô; phát hành công
khai (nếu có) chỉ gồm features + timestamp + nhãn.
