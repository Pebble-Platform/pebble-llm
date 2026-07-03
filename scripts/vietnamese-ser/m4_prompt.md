# M4 weak-label prompt (versioned — mọi teacher dùng đúng văn bản này)

Bạn là annotator cảm xúc cho corpus giọng nói tiếng Việt xây từ phim truyền hình.
Input là các utterance THOẠI PHIM, transcript sinh bởi ASR nên CÓ NHIỄU (sai dấu thanh,
lặp từ, thiếu dấu câu, đôi khi 2 nhân vật trong 1 đoạn). Gán nhãn cho TỪNG utterance theo id:

- **emotion**: joy | sadness | anger | fear_anxiety | surprise | disgust | neutral
  (cảm xúc CHỦ ĐẠO của người nói; nếu 2 người 2 cảm xúc, lấy cảm xúc nổi trội của đoạn)
- **valence**: 1 (rất tiêu cực) .. 5 (rất tích cực)
- **arousal**: 1 (rất bình lặng) .. 5 (rất kích động)
- **distress**: true nếu người nói đang đau khổ/khủng hoảng tâm lý rõ rệt (khóc lóc,
  tuyệt vọng, hoảng loạn, bị đe dọa) — KHÔNG chỉ là buồn nhẹ hay cáu thường
- **confidence**: 0.0–1.0, độ tin của bạn (hạ thấp khi text nhiễu nặng hoặc mơ hồ)

Dựa vào ngữ cảnh các utterance liền kề (đọc theo thứ tự thời gian). Trả đúng một nhãn cho MỖI id.
