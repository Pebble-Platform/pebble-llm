## ADR-001 — Gold annotation mù teacher (blind-first), không pre-fill nhãn LLM

**Date:** 2026-07-07 · **Status:** ~~proposed~~ **superseded bởi [ADR-003](ADR-003-human-labels-drop-weak-supervision.md)**

> **Superseded 2026-07-07:** ADR-003 bỏ weak-supervision → teacher không còn bị
> "chấm" nên tiền đề *evaluation leakage* của ADR-001 biến mất, và user chọn
> **giữ teacher làm gợi ý mờ** (ngược với "ẩn teacher" ở đây). Cái **còn giá
> trị**: (1) **không pre-fill** — human luôn tự quyết; (2) nguyên tắc *mù* đổi
> đích sang **độc lập giữa các annotator** (A không thấy nhãn B) khi có ≥2 người;
> (3) caveat anchoring (hiển thị teacher vẫn neo nhãn) được chuyển vào ADR-003.
> Phần dưới giữ nguyên làm lịch sử.

**Resolves:** `tools/labeler/SPEC.md` lỗ spec #2 (anchoring). Ràng buộc gốc:
invariant I6 (đã viết lại theo ADR-003).

**Context:** công cụ gold `tools/labeler/index.html` hiện **hiển thị** nhãn 2
teacher (Opus/Sonnet) và **pre-select** đồng thuận của chúng (`suggest()`,
`index.html:247-256`) làm giá trị mặc định trước khi người xác nhận gold. Gold
này lại là held-out set dùng để **chấm chính 2 teacher đó**. Cho người chấm thấy
output của hệ thống bị chấm là **evaluation leakage** (incorporation/review
bias), không phải bias nhẹ — nó bơm phồng agreement và biến "gold độc lập" thành
"adjudication của nhãn teacher", làm hỏng chính lý do I6 tồn tại (κ teacher không
được coi là accuracy; accuracy phải đo trên gold độc lập).

**Decision:** áp dụng **blind-first + adjudication** cho luồng gold:

1. Bỏ **toàn bộ** pre-fill/pre-select ở `index.html`, kể cả nhánh "2 teacher
   đồng thuận" — mọi clip bắt đầu **trống**, người chọn emotion/V/A/distress từ
   audio (giữ nguyên guard `!curEmotion` đã có ở `index.html:267`).
2. **Ẩn** cờ ☠ và 2 cột teacher trong màn nhập; chỉ hiện **read-only sau khi**
   gold đã lưu (phục vụ error-analysis, không sửa gold). `teacher_agree` vẫn xuất
   trong `gold.csv` như trường chẩn đoán hậu kỳ.
3. Nếu có **2 annotator**: cả hai label mù một subset chung; báo **κ human–human**
   làm độ tin cậy của gold (số này hợp thức hoá "gold", KHÔNG phải κ teacher).
   Adjudicate bất đồng người–người, adjudicator vẫn mù teacher.

**Evidence:**
- Schroeder, Kabbara & Roy, *"Just Put a Human in the Loop?"*, ACL 2025 Findings
  ([arXiv:2507.15821](https://arxiv.org/abs/2507.15821)): gợi ý LLM đẩy overlap
  human–LLM từ 40% (blind) → 81–87%; khi nhãn "human-reviewed" đó làm ground
  truth, F1 của model được chấm **phồng tới +0.32**. Khuyến nghị: baseline người
  độc lập, không gợi ý, cho mọi thứ làm ground truth.
- Skitka, Mosier & Burdick, *"Does automation bias decision-making?"*, IJHCS
  1999 — cơ chế nền (người dưới-soi gợi ý tự động).
- Läubli et al., JAIR 2020 — MT human-parity claim sai do đánh giá không mù.
- QUADAS-2 (Whiting et al., Ann Intern Med 2011) — "incorporation/review bias"
  là mối đe doạ giá trị chí tử khi người chấm reference biết kết quả index test.

**Consequences:**
- `index.html`: `suggest()` không còn pre-fill emotion/V/A; màn nhập ẩn teacher
  tới sau khi lưu. (Code change này **chờ ADR `accepted`** — chưa thực thi.)
- `tools/labeler/SPEC.md` mục "Gợi ý" + lỗ #2 cập nhật trỏ về ADR này.
- Chỉ sau thay đổi này `gold.csv` mới thoả I6 để chống lưng claim accuracy/UAR.
- Chi phí: annotation chậm hơn — chấp nhận; giảm bằng phím tắt sẵn có, **không**
  tái lập pre-fill. Nếu chỉ 1 annotator (không adjudicate được), độ tin cậy gold
  thấp hơn theo cấu trúc — ghi rõ trong capability doc, không bù bằng model-assist.
- Open: chốt số annotator thực tế (1 hay 2) cho pilot 003.
