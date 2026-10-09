# Capability — tone checker (đo thanh điệu từng âm tiết)

- **Hiện trạng:** có, từ change [017](../changes/017-tone-checker/README.md) (2026-10-09).
- **Code:** `scripts/vietnamese-ser/tone_check.py`. Test chính tả:
  `tests/test_tone_check.py`.
- **Làm gì:** nhận audio 16 kHz + kịch bản tiếng Việt. Với mỗi âm tiết, trả về thanh mà
  audio thể hiện (trong các thanh hợp lệ của vần) và `margin` so với thanh trong kịch bản.
  Cách làm: chấm CTC cả câu cho từng biến thể thanh trên
  `nguyenvulebinh/wav2vec2-base-vietnamese-250h`.
- **Không chấm được:** câu có chữ số, ký tự ngoài vocab, hoặc âm tiết không có nguyên âm.

## Nền nhiễu trên giọng thật (ViEmoSpeech, `docs/reports/017/`)

| Nhóm | Báo nhầm |
|---|---:|
| Tổng | 0.044 |
| neutral | 0.023 |
| sadness | 0.031 |
| disgust / joy | 0.048 |
| fear_anxiety | 0.055 |
| surprise | 0.060 |
| anger | 0.066 |

Phát hiện thanh sai (giả lập): 0.991 · AUC 0.997.

## Cách dùng khi chấm TTS (intent §2.4)

Báo **tỉ lệ sai thanh của giọng sinh ra trừ đi báo nhầm của giọng thật cùng cảm xúc**, không
báo con số tuyệt đối. Báo nhầm trên giọng thật là cận trên, vì `gold_text` chưa được soát.
Kết quả chỉ áp dụng cho phương ngữ Bắc.
