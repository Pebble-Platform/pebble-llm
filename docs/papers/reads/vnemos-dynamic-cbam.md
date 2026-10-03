# Read — Emotional Vietnamese Speech-Based Depression Diagnosis Using Dynamic Attention Mechanism

- **Source:** ICAMCS 2024 (Springer) · [arXiv 2412.08683](https://arxiv.org/abs/2412.08683) · [code](https://github.com/fiyud/Emotional-Vietnamese-Speech-Based-Depression-Diagnosis-Using-Dynamic-Attention-Mechanism)
- **Read:** 2026-07-15, stopped after Pass 2
- **Reading question:** bài này thay đổi gì cho ViEmoSpeech (prior art SER tiếng Việt + claim "depression")?

## Verdict
Dừng sau Pass 2 — phương pháp (CBAM biến thể) không đáng tái tạo; giá trị nằm ở related work + ví dụ phản diện, không phải ở method.

## Notes
- **Claim:** Dynamic-CBAM (ODConv thay spatial attention) + Attention-GRU nhận diện cảm xúc giọng nói tiếng Việt, từ đó "đánh giá xu hướng trầm cảm".
- **Evidence:** SER 5 lớp (anger/happiness/sadness/neutral/fear) trên VNEMOS ~250 đoạn / ~30 phút cắt từ 27 phim & show; MFCC input; 5-fold stratified CV; UA 0.87 / WA 0.86 / F1 0.87 (prior [20]: UA 0.85 / WA 0.83 / F1 0.85).
- **Gap / red flags:** (1) tiêu đề "depression diagnosis" nhưng không có nhãn lâm sàng nào — suy diễn hậu nghiệm từ cảm xúc; (2) CV không nói speaker-independent — data từ phim gần như chắc chắn speaker leakage, số 0.87 khả năng bị thổi phồng; (3) không nêu số speaker, không nêu license; (4) không có mục limitations thực chất.
- **For Pebble:** related work củng cố positioning (corpus VN hiện có chỉ ~30 phút, không license, không speaker-disjoint) + cautionary example cho invariant speaker-disjoint và cấm nói quá emotion→distress.
- **Stream entry:** [docs/papers/vietnamese-ser/10-vn-depression-dynamic-cbam.md](../vietnamese-ser/10-vn-depression-dynamic-cbam.md)
