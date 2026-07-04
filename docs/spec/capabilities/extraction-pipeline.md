# Capability — Extraction pipeline (video tập phim → weak pool sạch)

> Spec layer / **state**: mô tả ĐÚNG những gì pipeline làm HÔM NAY, với số đo.
> Thay đổi hành vi/kết quả ⇒ cập nhật file này trong cùng PR (WORKFLOW rule 5).
> Cập nhật lần cuối: 2026-07-04 (sau pilot ep01 hoàn chỉnh, PR #6).

## Hành vi hiện tại

`scripts/vietnamese-ser/pilot_extract.py` (local, cache từng stage) và
`kaggle/vietnamese-ser/vnser-extract/vnser-extract.py` (batch GPU, cùng logic):

1. **ffmpeg**: video/audio → mono 16 kHz wav.
2. **Demucs htdemucs** (two-stems): tách nhạc/SFX → vocals.
3. **silero VAD** → speech regions, merge gap <0.4s.
4. **Turn-split v2** (khi có diarization; local pyannote 4.x `token=`, Kaggle 3.x
   `use_auth_token=`): pre-merge turns cùng speaker <0.6s → region chỉ 1 speaker
   giữ nguyên → region đa-speaker cắt tại biên turn, lỗ "" nhập vào hàng xóm,
   overlap ≥2 giọng DROP cứng → mảnh đa-speaker MIN 1.5s, còn lại MIN 2.0s,
   MAX 10s. Không token → fallback cắt VAD thuần, cột speaker rỗng.
5. **PhoWhisper-base** ASR trên raw array (né torchcodec) → `transcripts.csv`.
6. **align_youtube.py**: caption YouTube ↔ segment theo overlap ±1s →
   `transcripts_yt.csv` (2 nguồn text + sim).
7. **Weak-label 2 teacher** (Opus + Sonnet; prompt pin tại
   `scripts/vietnamese-ser/m4_prompt.md`): emotion 7 lớp + valence/arousal 1–5 +
   distress + confidence + `multi_speaker_suspect` → `labels_*.csv`.
8. **Weak pool** = segment có speaker ≠ rỗng VÀ không bị OR-flag đa-giọng-text.

## Số đo hiện hành (ep01, tập 35.6′ — nguồn: `docs/tasks/vn-tv-ser-pilot.md`)

| Đại lượng | Giá trị |
|---|---|
| Yield thoại sau Demucs+VAD | 11.9′ (33%) |
| Sau turn-split v2 | 175 utt / 10.3′, 100% đơn-giọng theo diarization (dung sai biên 50ms) |
| Điểm mù diarization (text-flag OR 2 teacher) | 20/175 = 11.4% |
| **Weak pool sạch** | **155 utt / 8.6′** |
| κ 2-teacher (emotion) | 0.697 (cắt cũ: 0.584) |
| Similarity PhoWhisper↔YouTube | mean 87.2 / median 90.5 (base đủ, không cần -medium) |
| Chiếu scale P1 (3 bộ/120 tập) | ~18.6k utt train-ready / ~17h |

## Biên đã biết (không phải bug)

- Diarization mù với 2 giọng rất giống nhau (nữ-nữ) → tầng text-flag tồn tại vì
  vậy; gold set vẫn cần tai người xác nhận.
- Clip xuất với PAD 0.1s mỗi đầu → tối đa ~100ms mép giọng hàng xóm (cố ý).
- Distress = proxy trên phim diễn, KHÔNG phải nhãn lâm sàng (intent §7).
