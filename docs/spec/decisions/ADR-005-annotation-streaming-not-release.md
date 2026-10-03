## ADR-005 — Stream clip cho annotator mời đích danh ≠ "release" (làm rõ intent §1)

**Date:** 2026-07-28 · **Status:** accepted (quyết định user 2026-07-28: *"cho phép
user khác read thông qua máy local, dùng ngrok vẫn thoả được yêu cầu"*).
**Resolves:** M0 của `docs/tasks/online-multi-annotator-labeling.md` — câu chặn duy
nhất của tool label online.
**Tầng:** intent-layer clarification → đã ghi vào `docs/intent/constraints.md` §1.

## Context

ViEmoSpeech cần **κ/α human–human** để dataset paper qua được review: ADR-003 đặt
nhãn người làm nguồn sự thật duy nhất, nhưng cả 793 clip hiện có đều **single-pass,
1 người** — không có con số tin cậy nào. Cách duy nhất lấy được số đó là mời thêm
annotator từ xa label lại clip **đã cắt sẵn**, tức là clip phim có bản quyền phải
đến được trình duyệt của họ.

Việc đó đụng thẳng câu chữ nghiêm nhất của repo, và khảo sát phát hiện **hai tầng
văn bản của chính repo không khớp nhau**:

| Nguồn | Câu chữ | Phạm vi |
|---|---|---|
| `docs/intent/constraints.md:32` (bảng hard constraint) | "Copyrighted media **never leaves the machine**" | nghiêm hơn — nghe như cấm cả truyền qua mạng |
| `docs/intent/invariants.md:15` (I1, invariant vận hành) | "No episode media, clip, or full episode transcript is **committed or released**" | chỉ commit/release; **không nhắc tới truyền qua mạng** |

Check của I1 là `git ls-files data/` + lint release manifest — tức là I1 **luôn
luôn** chỉ đo commit/release, chưa bao giờ đo network. Khoảng vênh này phải do
người xử, không phải hệ quả phụ của một PR code (`WORKFLOW.md`, ba tầng).

## Decision

**"Never leaves the machine" = "never committed / never released".** Stream một
clip ngắn, qua tunnel có xác thực trỏ về server local của chính máy này, tới một
annotator **được mời đích danh**, **chỉ để label** — là **sử dụng nghiên cứu riêng
tư**, không phải publication. Không vi phạm intent §1.

**Hosting: ngrok tunnel tới server local** (quyết định user). Media vẫn nằm trên
đúng một máy; không tạo bản sao thường trú trên hạ tầng bên thứ ba.

**Vẫn cấm nguyên vẹn:** publish/commit media · truy cập bulk hoặc liền mạch cả tập
· annotation crowd mở (MTurk/Prolific) · **mọi bản sao thường trú ngoài máy này**
(gồm cả upload lên VPS/cloud) · phát hành clip kiểu MELD.

## Safeguard bắt buộc — cả gói, không chọn lẻ

Quyết định này **chỉ có hiệu lực khi đủ cả 7**; thiếu một cái là quay về trạng thái
chưa được phép:

1. Tài khoản/token **đích danh** per annotator — không phải link mở, không ẩn danh.
2. **Không** endpoint download/export nào tới được bằng role annotator (`/gold`,
   ZIP export, manifest audio → admin-only).
3. Chỉ excerpt ngắn (2–10s, đã đúng theo cấu tạo pipeline).
4. **Thứ tự clip xáo trộn** per annotator — không ai ráp lại được một cảnh liền mạch.
5. **Thoả thuận sử dụng dữ liệu** ngắn, annotator xác nhận trước khi truy cập:
   không phát tán, không ghi màn hình, không giữ bản sao.
6. **Log truy cập**: ai stream clip nào, lúc nào.
7. Tunnel **chỉ bật khi đang chạy vòng label**, tắt ngay sau đó.

## Consequences

- Mở khoá `docs/tasks/online-multi-annotator-labeling.md` M1→M8 (tool label online,
  vòng reliability, κ/α).
- Bài báo **phải** có data/ethics statement nêu thẳng chuyện này (bản nháp câu chữ
  ở Finding 3 của task doc). ARR nói rõ: một statement thừa nhận vùng xám **ít bị
  flag hơn** một statement né tránh hoặc vắng mặt.
- I1 giữ nguyên, không sửa — nó vẫn đo đúng thứ nó vẫn đo (commit/release). ADR này
  làm rõ câu tóm tắt ở constraints.md:32 cho khớp với I1, không nới lỏng I1.

## Rủi ro đã biết — nói thẳng

- **Vùng xám pháp lý VN, chưa ngã ngũ.** Điều 25/25a + 26 Luật SHTT VN viết theo
  khung "**một cá nhân**, **một bản**, **một phần** tác phẩm" — không viết cho tình
  huống stream tới nhiều cộng tác viên qua mạng. Research **không tìm được án lệ
  hay hướng dẫn** nào giải quyết điểm này. Chiếu three-step test Berne: excerpt
  ngắn, không liền mạch, có kiểm soát truy cập, phi thương mại → mạnh ở bước 2–3,
  **yếu nhất ở bước 1** ("special case" cho truy cập nhiều người). Đây là đánh giá
  rủi ro có cân nhắc, **không phải tư vấn pháp lý**.
- **Tunnel là điểm trung chuyển thật.** ngrok (và Cloudflare Tunnel) **terminate
  TLS ở edge của họ** — về nguyên tắc traffic audio đi qua hạ tầng bên thứ ba dưới
  dạng transit. Khác với VPS ở chỗ **không có bản sao thường trú**, nhưng không
  phải là "không bên thứ ba nào chạm tới byte nào". Data statement nên nói "streamed
  via an authenticated tunnel", đừng nói "never touched any third-party server".
- **Lập luận "tunnel an toàn hơn VPS" là suy luận quản trị rủi ro, không có nguồn
  trích dẫn** — research tự flag độ tin cậy thấp hơn phần còn lại.
- Nếu sau này pool annotator mở rộng đáng kể, hoặc chuyển sang hosting thường trú,
  **ADR này phải mở lại** — nó được quyết cho quy mô "một nhóm nhỏ mời đích danh".

## Tham chiếu

- `docs/tasks/online-multi-annotator-labeling.md` — Finding 3 (pháp lý: MSP-Podcast
  né vấn đề bằng nguồn có licence + vẫn gate sau thoả thuận ký; LDC phân phối theo
  licence cơ sở; VoxCeleb CC-BY cho annotation, bản quyền video vẫn của chủ gốc;
  MELD ship clip Friends không thấy giấy phép — cảnh báo, không phải hình mẫu).
- [ARR ethics flagging guidelines](http://aclrollingreview.org/ethics-flagging-guidelines/)
  · [WIPO Lex — VN IP Law](https://www.wipo.int/wipolex/en/legislation/details/12011).
- ADR liên quan: [003 human labels](ADR-003-human-labels-drop-weak-supervision.md)
  (vì sao cần κ human–human) · [004 state durability](ADR-004-labeler-state-durability.md)
  (schema `state.db` phải thêm chiều annotator trước khi rater thứ 2 chạy).
