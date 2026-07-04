# Viết bản giải thích thesis từ đầu (cho người chưa hiểu)

- **Slug:** thesis-explainer
- **Status:** done
- **Created:** 2026-07-02  ·  **Updated:** 2026-07-02
- **Owner:** user / Claude

## Goal
Một tài liệu giải thích thesis **từ con số 0** đến version hiện tại, trả lời cho
mỗi giai đoạn/thí nghiệm đúng 3 câu: (1) phương pháp là gì, (2) thực nghiệm để
kiểm chứng điều gì, (3) chạy xong ra kết quả gì — có đạt mục đích không.
Người đọc mục tiêu: chưa hiểu thesis, cần đọc một mạch là nắm được.

## Requirements & Constraints
- **Functional:** tiếng Việt, sư phạm (giải thích khái niệm trước khi dùng);
  mọi con số lấy từ số đã kiểm chứng log 2026-07-02 (`results-summary.csv`,
  `thesis-message-review.md`); trung thực cả điểm chưa đạt (QWK trade-off,
  significance, κ chưa có).
- **Constraints:** không thêm claim mới ngoài những gì đã verify; caveat
  "vượt paper" gắn liền headline.

## Milestones
- [x] M1 — Dựng khung theo 3 câu hỏi của user cho từng thí nghiệm E1–E10.
- [x] M2 — Viết `docs/reports/THESIS-GIAI-THICH-vi.md` (deliverable).
- [x] M3 — Đối chiếu chéo số liệu với `results-summary.csv` + paired stats phiên 2026-07-02.

## Decision Log
- **2026-07-02 — Cấu trúc theo chuỗi thí nghiệm E1–E10, mỗi cái 3 mục
  (mục đích/kết quả/đạt?):** khớp đúng 3 câu hỏi user đặt; thay vì cấu trúc
  theo report cũ (version table) vốn đã không giúp user hiểu. Rejected: viết
  lại THESIS-OVERVIEW lần nữa (đã làm, vẫn chưa đủ sư phạm).
- **2026-07-02 — Text stream sâu, voice tóm tắt:** toàn bộ hội thoại và điểm
  chưa-hiểu của user nằm ở text (emotion classifier vs suicide-risk); voice
  chưa có kết quả mới so với weekly 06-29.

## Completed Work
- 2026-07-02 — Viết `docs/reports/THESIS-GIAI-THICH-vi.md` — giải thích từ
  bối cảnh sản phẩm → pivot → khái niệm nền → phương pháp → 10 thí nghiệm →
  verdict đạt/chưa đạt.

## Remaining Action Items
- [ ] (tùy chọn) render bản HTML để gửi kèm báo cáo tuần.
