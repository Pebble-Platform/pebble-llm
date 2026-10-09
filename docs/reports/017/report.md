# Change 017 — kiểm chứng tone checker trên ViEmoSpeech (giọng thật)

Sinh bởi `scripts/vietnamese-ser/tone_check.py validate` · commit `086c292` · model `nguyenvulebinh/wav2vec2-base-vietnamese-250h` · 2026-10-09T15:52:46. Không chứa text (I1).

Giọng thật đọc đúng thanh, nên thanh trong kịch bản là đáp án. **Báo nhầm** = 1 − chính xác (mức nền nhiễu). **Phát hiện** = giả lập kịch bản ghi sai một thanh, tỉ lệ công cụ gắn cờ. Định nghĩa: `docs/spec/changes/017-tone-checker/README.md`.

- Clip: 1394 chấm được / 1420; loại: {'digit': 24, 'no_vowel': 2}
- Âm tiết giữ trong câu nhưng không chấm (thanh không hợp lệ với vần): 17
- ⚠ `gold_text` chưa được soát: lỗi text hiện ra thành báo nhầm, nên báo nhầm là cận trên.

## Tổng

| all | clip | âm tiết | chính xác [CI95] | báo nhầm | phát hiện | AUC | ngẫu nhiên |
|---|---:|---:|---|---:|---:|---:|---:|
| all | 1394 | 20069 | 0.956 [0.952, 0.960] | 0.044 | 0.991 | 0.997 | 0.198 |

## Theo cảm xúc

| emotion | clip | âm tiết | chính xác [CI95] | báo nhầm | phát hiện | AUC | ngẫu nhiên |
|---|---:|---:|---|---:|---:|---:|---:|
| anger | 274 | 3995 | 0.934 [0.924, 0.944] | 0.066 | 0.986 | 0.995 | 0.194 |
| disgust | 115 | 1739 | 0.952 [0.939, 0.964] | 0.048 | 0.990 | 0.997 | 0.192 |
| fear_anxiety | 144 | 2048 | 0.945 [0.928, 0.961] | 0.055 | 0.988 | 0.997 | 0.196 |
| joy | 239 | 3371 | 0.952 [0.944, 0.960] | 0.048 | 0.990 | 0.997 | 0.198 |
| neutral | 375 | 5676 | 0.977 [0.972, 0.982] | 0.023 | 0.995 | 0.999 | 0.201 |
| sadness | 166 | 2281 | 0.969 [0.959, 0.978] | 0.031 | 0.993 | 0.999 | 0.201 |
| surprise | 81 | 959 | 0.940 [0.916, 0.959] | 0.060 | 0.987 | 0.995 | 0.194 |

## Theo arousal

| arousal_band | clip | âm tiết | chính xác [CI95] | báo nhầm | phát hiện | AUC | ngẫu nhiên |
|---|---:|---:|---|---:|---:|---:|---:|
| high (4-5) | 554 | 7753 | 0.940 [0.932, 0.947] | 0.060 | 0.987 | 0.996 | 0.195 |
| low (1-2) | 283 | 3994 | 0.975 [0.969, 0.980] | 0.025 | 0.994 | 0.999 | 0.201 |
| mid (3) | 557 | 8322 | 0.963 [0.957, 0.968] | 0.037 | 0.992 | 0.998 | 0.198 |

## Theo thanh trong kịch bản

| tone | clip | âm tiết | chính xác [CI95] | báo nhầm | phát hiện | AUC | ngẫu nhiên |
|---|---:|---:|---|---:|---:|---:|---:|
| hoi | 898 | 1590 | 0.943 [0.932, 0.953] | 0.057 | 0.989 | 0.995 | 0.167 |
| huyen | 1286 | 4329 | 0.940 [0.933, 0.948] | 0.060 | 0.988 | 0.996 | 0.167 |
| nang | 1113 | 2569 | 0.958 [0.949, 0.966] | 0.042 | 0.989 | 0.996 | 0.274 |
| nga | 606 | 815 | 0.944 [0.924, 0.960] | 0.056 | 0.989 | 0.996 | 0.167 |
| ngang | 1358 | 5984 | 0.969 [0.964, 0.974] | 0.031 | 0.994 | 0.999 | 0.167 |
| sac | 1313 | 4782 | 0.961 [0.954, 0.967] | 0.039 | 0.991 | 0.998 | 0.238 |

## Âm tiết tắc / không tắc

| checked | clip | âm tiết | chính xác [CI95] | báo nhầm | phát hiện | AUC | ngẫu nhiên |
|---|---:|---:|---|---:|---:|---:|---:|
| checked (p/t/c/ch) | 954 | 1858 | 0.990 [0.985, 0.994] | 0.010 | 0.990 | 1.000 | 0.500 |
| open | 1393 | 18211 | 0.953 [0.948, 0.957] | 0.047 | 0.991 | 0.997 | 0.167 |

## Theo series

| series | clip | âm tiết | chính xác [CI95] | báo nhầm | phát hiện | AUC | ngẫu nhiên |
|---|---:|---:|---|---:|---:|---:|---:|
| cay-tao-no-hoa | 16 | 172 | 0.936 [0.883, 0.981] | 0.064 | 0.986 | 0.997 | 0.192 |
| chay-tron-thanh-xuan | 1039 | 15779 | 0.959 [0.955, 0.964] | 0.041 | 0.991 | 0.998 | 0.199 |
| ve-nha-di-con | 339 | 4118 | 0.946 [0.936, 0.956] | 0.054 | 0.988 | 0.996 | 0.194 |

## Ma trận nhầm (hàng = thanh kịch bản, cột = thanh công cụ đọc)

| | ngang | huyen | sac | hoi | nga | nang |
|---|---|---|---|---|---|---|
| ngang | 5800 | 85 | 65 | 8 | 12 | 14 |
| huyen | 99 | 4070 | 58 | 76 | 2 | 24 |
| sac | 107 | 43 | 4594 | 8 | 9 | 21 |
| hoi | 8 | 54 | 16 | 1499 | 1 | 12 |
| nga | 19 | 2 | 10 | 2 | 769 | 13 |
| nang | 32 | 36 | 28 | 11 | 2 | 2460 |
