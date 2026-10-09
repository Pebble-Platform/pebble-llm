# Báo cáo tiến độ gửi Giáo viên hướng dẫn (kỳ 2026-07)

- **Slug:** advisor-progress-report
- **Status:** done
- **Created:** 2026-07-29  ·  **Updated:** 2026-07-30
- **Owner:** user (dev.phatdt) / Claude

## Goal
Đọc toàn bộ trạng thái repo (intent → spec → tasks → code → dữ liệu sống) và viết
**một báo cáo tiến độ cho GVHD (Tiến sĩ)**: đã làm được gì, số đo thật, cái gì
đang chặn, và **những gì cần thầy quyết/hỗ trợ**. Deliverable = 1 file `.md` chứa
nội dung + 1 file `.html` để trình bày.

## Requirements & Constraints
- **Functional:** báo cáo tiếng Việt, cho người đọc là GVHD (không phải người viết
  code) — nhưng mọi con số phải **truy được về file trong repo** (I5).
- **Constraints:**
  - Chỉ báo cáo số **đã đo**; không suy diễn, không làm tròn lên. Số nào là ước
    lượng phải ghi rõ là ước lượng.
  - Không đưa media/transcript vào tài liệu (I1) — báo cáo chỉ chứa thống kê.
  - HTML **self-contained** (mở bằng trình duyệt, không cần server), theo đúng
    style đã có ở `docs/project-overview.html`.
  - Surgical: chỉ thêm file mới, không sửa doc/spec/code hiện có.

## Milestones
- [x] M1 — Đọc trạng thái: intent, invariants, 5 ADR, 2 capability, 11 change,
      các doc task còn sống, git log — exit: nắm được mốc pivot + việc đang chặn.
- [x] M2 — Lấy **số sống** (không đọc lại số cũ trong doc): `state.db` (nhãn
      người), số clip trên đĩa, gold-candidates — exit: bảng số đến 2026-07-29.
- [x] M3 — Viết `docs/progress-report-2026-07-29.md` — exit: đủ 9 mục, mọi số có nguồn.
- [x] M4 — Viết `docs/progress-report-2026-07-29.html` — exit: mở được, sáng/tối, mục lục.

## Decision Log
<!-- newest first -->
- **2026-07-31 — Bỏ hẳn mục "cần hỗ trợ", báo cáo còn 5 mục:** owner sẽ nói miệng
  các đề nghị khi trình bày, không đưa vào văn bản. Cấu trúc chốt: 1 tóm tắt ·
  2 mục tiêu · 3 tiến độ · 4 số đã đo · 5 phụ lục. Các câu hỏi vẫn còn nguyên trong
  Open Questions của doc này (không mất dấu vết dù báo cáo không nhắc).
- **2026-07-31 — Thay chữ bằng chart trong bản HTML (owner: "chữ nhiều quá"):**
  4 hình mới, tất cả **inline SVG/CSS, không CDN** (báo cáo phải mở được offline
  bằng file://): funnel pipeline 35,6′→11,9′→10,3′ · stacked bar tiến độ corpus ·
  bar chart phân bố 7 lớp cảm xúc · bar chart macro-F1 có khoảng tin cậy + vạch
  ngưỡng ngẫu nhiên, kèm chart CCC trên thang 0→1 để thấy "gần sàn". §3 đổi từ
  bảng 9 dòng sang lưới thẻ trạng thái; §1.1 đổi từ 4 đoạn văn sang 4 thẻ.
  **Mọi bảng số vẫn giữ nguyên bên dưới chart** (chart là headline, bảng là
  table-view — số vẫn đọc được không cần màu).
- **2026-07-31 — Chart dùng token màu riêng, không tái dùng `--accent` của trang:**
  `--accent` bản dark (#589bff) **trượt khỏi dải sáng** khi kiểm bằng
  `validate_palette.js` (L 0,69 > 0,67) — đúng cho chữ/viền nhưng sai cho mảng tô.
  Chốt `--c1/--c2`: light #2563eb/#bc4c00, dark #3b82f6/#d97706 — cả hai mode PASS
  cả 5 kiểm (dải sáng · chroma · CVD ΔE ≥ 26 · normal ΔE ≥ 31 · contrast ≥ 3:1).
  Rejected: lật màu light sang dark tự động (dark phải chọn bước riêng).
- **2026-07-31 — Số "chưa duyệt" cố tình KHÔNG ghi con số trên chart:** bảng §4.2
  ghi 1.198 đã duyệt nhưng 813 + 395 = 1.208 (lệch 10 record). Chưa truy được
  nguyên nhân, và không truy vấn lại `state.db` vì báo cáo đã chốt mốc 2026-07-29
  (owner vẫn đang label, query hôm nay sẽ lệch với cả báo cáo). Chart vẽ 813 + 395
  theo tổng 3.775, phần còn lại chỉ ghi nhãn "chưa duyệt" — không bịa số.
- **2026-07-30 — Rút báo cáo còn 6 mục, thêm "Vì sao chọn đề tài này":** owner review
  bản đầu và yêu cầu (a) bỏ mọi lời xưng hô với GVHD — owner sẽ nói miệng khi trình
  bày, văn bản chỉ chứa nội dung; (b) §1 phải trả lời được **vì sao chọn đề tài**
  (bản đầu nhảy thẳng vào trạng thái, người đọc không thấy động cơ); (c) khối "cần
  hỗ trợ" rời khỏi §1 xuống cuối; (d) bỏ §5 quyết định phương pháp, §6 pháp lý,
  §7 kế hoạch 8 tuần, §8 bảng câu hỏi chi tiết. Cấu trúc mới: 1 tóm tắt (1.1 vì sao
  + 1.2 trạng thái) · 2 mục tiêu · 3 tiến độ · 4 số đã đo · 5 cần hỗ trợ · 6 phụ lục.
- **2026-07-30 — Khối "cần hỗ trợ" đặt ở §5, TRƯỚC phụ lục §6:** "section cuối cùng"
  hiểu là mục nội dung cuối cùng; phụ lục là tra cứu, không phải mạch trình bày.
  Rejected: đặt sau phụ lục (kết bài bằng bảng tra file là hỏng nhịp nói).
- **2026-07-30 — Giữ dạng liệt kê ①–⑤ gọn cho §5, không dựng lại bảng 4 cột của §8 cũ:**
  owner yêu cầu bỏ §8; chép lại bảng đó xuống cuối là vô hiệu hoá chính yêu cầu ấy.
  Lý do "vì sao cần" của từng mục vẫn còn trong bảng §8 của git history nếu cần tra lại.
- **2026-07-30 — Nội dung §1.1 lấy từ số đã có, không thêm claim mới:** 4 lý do =
  khoảng trống dữ liệu (§2.1) · xung đột thanh điệu×cảm xúc (§2.2, Shen NAACL 2024) ·
  bằng chứng đo được (CCC 0,09–0,13 + ASR sai thanh điệu ở high-arousal, §4.3) ·
  tính khả thi (yield 33%, §4.1). I5 giữ nguyên: mọi số trong §1.1 đều đã có nguồn ở §6.
- **2026-07-29 — Số corpus báo cáo theo ĐĨA (3.775 clip), không theo số đóng gói
  Kaggle v3 (3.611 utt):** owner đã recut/split thêm trong labeler sau lần đóng
  gói, nên số trên đĩa mới là hiện trạng. Báo cả hai kèm lý do chênh, thay vì
  chọn một số rồi im lặng. Rejected: dùng 3.611 cho "khớp doc cũ" (báo cáo tiến
  độ mà lấy số cũ hơn hiện trạng là sai mục đích).
- **2026-07-29 — Nhãn người lấy trực tiếp từ `state.db` bằng truy vấn read-only,
  không trích từ doc:** các doc task ghi 793 (28/07) rồi 813 — owner vẫn đang
  label, số trong doc lạc hậu ngay khi viết. Truy vấn cho 1.198 record / 813
  nhãn / 395 loại tại 2026-07-29. Rejected: trích doc (rủi ro báo sai cho thầy).
- **2026-07-29 — Báo cáo tách bạch "số đã đo" và "số dự phóng":** mọi con số
  chiếu-scale (P1 120 tập, throughput annotator) đưa vào mục riêng và gắn nhãn
  ước lượng. Lý do: I5/I6 — số không có report sinh ra thì không được đứng cạnh
  số có report.
- **2026-07-29 — Không publish Artifact, chỉ ghi file trong repo:** user yêu cầu
  "1 file md + 1 file html", và báo cáo bàn tới media có bản quyền + trạng thái
  pháp lý chưa ngã ngũ → giữ trong repo là đúng phạm vi. Rejected: Artifact
  (đẩy nội dung ra dịch vụ ngoài mà không được yêu cầu).

## Open Questions
- [ ] (chuyển cho GVHD — nay nằm ở **§5** của báo cáo) IRB/hội đồng đạo đức, thù lao
      annotator, chốt series test, mục tiêu quy mô corpus, venue + deadline.

## Research Findings
<!-- không cần research mới: báo cáo tổng hợp từ 4 khối research đã có trong
     docs/tasks/online-multi-annotator-labeling.md + docs/tasks/vnser-human-pilot-train.md -->

## Completed Work
- 2026-07-29 — Khảo sát trạng thái sống: `state.db` **1.198 record / 813 nhãn
  emotion / 395 rejected / bảng `assignments` 0 dòng** (chưa annotator nào chạy);
  clip trên đĩa **3.775** (chay-tron 2.082 / ve-nha 1.693); gold-candidates 58 dòng.
- 2026-07-29 — `docs/progress-report-2026-07-29.md` — báo cáo 9 mục.
- 2026-07-29 — `docs/progress-report-2026-07-29.html` — bản trình bày self-contained.
- 2026-07-30 — Vòng sửa theo review của owner: bỏ xưng hô GVHD (md + html), thêm
  §1.1 "Vì sao chọn đề tài này" (4 lý do), chuyển khối hỗ trợ từ §1 xuống §5, xoá
  §5–§8 cũ, phụ lục §9→§6, cập nhật mục lục + CSS mồ côi trong html.
- 2026-07-31 — Vòng 2: bỏ hẳn mục hỗ trợ (còn 5 mục); html thêm 4 chart inline
  SVG/CSS + lưới thẻ §3 + thẻ §1.1; md thêm sơ đồ mermaid pipeline + 4 khối bar
  ASCII (phân bố lớp, funnel, macro-F1, CCC) cho người đọc bản text.
  Đã render kiểm bằng Chrome headless ở **cả light lẫn dark** (`--blink-settings=
  preferredColorScheme`) — sửa 1 lỗi bắt được: SVG khai viewBox 640 nhưng vẽ ở
  ~940px nên chữ trong chart to gấp 1,5 lần chữ thân bài; dựng lại viewBox 960 (1:1).

## Remaining Action Items
- [ ] Gửi GVHD; sau khi có trả lời cho §5, cập nhật `docs/tasks/online-multi-annotator-labeling.md`
      (M6 mở được hay không) và `docs/spec/changes/011-online-multi-annotator/consent.vi.md`.
