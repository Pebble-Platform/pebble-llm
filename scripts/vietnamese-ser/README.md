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

## Chạy pilot trên 1 tập phim

```powershell
# đặt file tập phim (mp4/mkv/...) vào data/vietnamese-ser/raw/  (gitignored — KHÔNG commit media)
python scripts/vietnamese-ser/pilot_extract.py --input data/vietnamese-ser/raw/ep01.mp4
# thêm diarization:  --hf-token hf_xxx
# chỉ đo yield, bỏ ASR: --skip-asr
# ASR tốt hơn (chậm hơn): --whisper vinai/PhoWhisper-medium
```

Output: `data/vietnamese-ser/pilot/<ep>/` — `report.md` (yield %), `segments.csv`,
`clips/*.wav`, `transcripts.csv`, `speakers.csv` (nếu bật diarization).
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
