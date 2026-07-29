# Change 011 — Tool label online đa annotator (κ human–human)

**Status:** in-progress — **tool xong 2026-07-28 (M0–M5 + script κ/α)**; còn lại là
hai vòng label do **người thật** thực hiện (M6, M7) + M9.
**Goal:** đưa annotator từ xa vào label lại clip **đã cắt sẵn**, để ViEmoSpeech có
**κ/α human–human** — con số ADR-003 bắt buộc và hiện thiếu hoàn toàn (793 clip đều
single-pass, 1 người).
**Doc sống:** [`docs/tasks/online-multi-annotator-labeling.md`](../../../tasks/online-multi-annotator-labeling.md)
(milestone, decision log, 4 khối research đầy đủ kèm nguồn).
**Cho phép bởi:** [ADR-005](../../decisions/ADR-005-annotation-streaming-not-release.md)
— stream cho annotator mời đích danh ≠ "release", kèm 7 safeguard bắt buộc.

## Văn bản của change này

| File | Việc |
|---|---|
| [`annotator-guideline.vi.md`](annotator-guideline.vi.md) | Hướng dẫn gán nhãn — annotator đọc. **Bài báo sẽ đăng nguyên văn** (yêu cầu ARR). |
| [`consent.vi.md`](consent.vi.md) | Đồng ý tham gia + thoả thuận sử dụng dữ liệu. **Còn ô trống phải điền.** |
| [`qc-protocol.md`](qc-protocol.md) | Giao thức QC + quy tắc tính κ — **pre-registered, phải đông cứng trước khi label**. |
| [`RUNBOOK.md`](RUNBOOK.md) | Vận hành một vòng: token → hàng đợi → server → ngrok → theo dõi → đóng vòng. |
| `gold-set.txt` | *(chưa có)* danh sách clip id của gold set, dựng theo qc-protocol §2.1. |

## Code đã build

| Nơi | Việc |
|---|---|
| `tools/labeler/auth.py` | token + role + log truy cập |
| `tools/labeler/server.py` | middleware `guard` (biên bảo mật) + route `/rate/*` + `--tokens` / `--no-local-admin` |
| `tools/labeler/store.py` | bảng `assignments` + `assign`/`next_seq`/`assignment_clip`/`save_rating`/`progress`/`all_ratings` |
| `tools/labeler/rate.html` · `rate.js` | màn annotator (mù, tối giản) |
| `scripts/vietnamese-ser/build_assignments.py` | dựng hàng đợi: phân tầng + gold + dup + xáo trộn |
| `scripts/vietnamese-ser/iaa_report.py` | Fleiss κ + Krippendorff α + nhãn-của-record + bảng QC |
| `scripts/vietnamese-ser/pick_gold_candidates.py` | lọc đồng thuận ba chiều + phân tầng → `gold-candidates.tsv` |
| `tools/labeler/gold.html` · `gold.js` | màn nghe & chốt gold set (owner-only) → ghi `gold-set.txt` |

## Phạm vi

**Trong:** phát clip đã cắt + thu emotion (7 lớp) + valence (1–5) + arousal (1–5) từ
annotator được mời đích danh; identity per-annotator; assignment + chồng lấn; auth;
tính κ/α.

**Ngoài:** cắt / chia / excise / segment — **không** có trong tool online, ở lại
local và chỉ owner làm. Không thu giới tính/tuổi/vùng miền ở vòng này (quyết định
user: thêm trường thì mỗi clip chậm hơn, κ loãng ra). Không dashboard IAA thời gian
thực — κ tính offline bằng script.

## Quyết định thiết kế

- **Mở rộng `tools/labeler/`, không dùng Label Studio / Potato.** Label Studio
  Community (Apache-2.0) **paywall đúng thứ cần nhất** — overlap, gán task cho user
  cụ thể, agreement metrics đều là Enterprise. Bề mặt cần xây là **tập con** của UI
  đã có; phần thiếu chỉ là identity + assignment + auth. Rejected: Potato (hợp mục
  đích nhất trong nhóm "buy" nhưng là stack thứ hai, phải ETL ngược về
  `(epKey, clip_id)`), doccano (không widget audio), INCEpTION (text span), Prodigy
  ($390–490/ghế, vẫn phải tự viết logic overlap), CVAT (bbox).
- **Annotator MÙ HOÀN TOÀN** — không thấy nhãn của owner, của annotator khác, hay gợi
  ý teacher (opus/sonnet). Đây là **khác biệt then chốt so với UI owner**, nơi teacher
  vẫn hiện read-only theo ADR-003. Thấy nhãn có sẵn = nhãn bị neo = κ vô nghĩa.
- **Không hiện transcript.** Corpus này về **giọng nói**; chữ viết kéo phán đoán về
  phía nội dung câu nói thay vì cách nói. (UI owner **có** hiện text vì owner còn phải
  sửa `gold_text` — vai trò khác.)
- **Thứ tự clip xáo trộn per annotator.** Hai mục đích cùng lúc: chống hiệu ứng mạch
  truyện, và là safeguard #4 của ADR-005 (không ai ráp lại được một cảnh liền mạch).
- **Nút "bỏ qua" có lý do** (không nghe rõ / nhiều giọng / cắt hỏng / không có tiếng
  nói). ⚠️ **Đây là chỗ tôi đi hơi quá phạm vi user chốt** ("emotion + V/A", đã loại
  phương án có cờ multi) — xem §"Cần owner duyệt" bên dưới.
- **Mã annotator giả danh (`ann01`, `ann02`…) trong bản phát hành.** I2 đòi mọi nhãn
  truy được về người gán; giả danh thoả mãn I2 mà không lộ danh tính. Bảng ánh xạ
  chỉ nằm trên máy owner, không bao giờ công bố.
- **Gold set chỉ gồm clip đồng thuận ba chiều (owner + Opus + Sonnet) và owner nghe
  lại xác nhận hiển nhiên.** Vì nhãn owner **không phải sự thật nền độc lập** — gold
  ở đây chỉ có nghĩa "dễ tới mức ai nghe nghiêm túc cũng ra thế", dùng để bắt người
  **không nghe**, không dùng để bắt người **nghe khác**. Trong hướng dẫn gọi là
  **"mốc neo"**, không gọi "đáp án đúng".
- **Báo cáo κ tách bạch, headline là κ(ann01 ↔ ann02).** Vòng qualification sàng
  annotator bằng mức trùng với gold do owner adjudicate → κ(owner, annotator) **bị
  thổi lên bởi chính cách tuyển**. κ giữa hai annotator mới với nhau ít nhiễm nhất
  nên đứng đầu; κ có owner báo riêng kèm cảnh báo. Chi tiết: qc-protocol §5.3 — đây
  là chỗ dễ tự lừa mình nhất trong cả giao thức.
- **Gold + lần gán thứ hai của clip lặp bị LOẠI khỏi tập tính κ.** Gold được chọn *vì*
  dễ; để trong sẽ làm κ phồng giả tạo.

## Cần owner duyệt trước khi đông cứng

1. ~~**Nút "bỏ qua"**~~ — ✅ **user duyệt giữ (2026-07-29).** Skip có lý do
   (`unclear | multi_speaker | bad_cut | no_speech`), không phải trường nhãn mới:
   clip bình thường không chậm đi, κ không loãng. Không có nó thì clip toàn nhạc
   hoặc 2 người cãi nhau **buộc annotator đoán bừa**, nhiễu chảy thẳng vào κ.
   Lợi ích phụ: lý do `multi_speaker` là tín hiệu miễn phí cho invariant I3.
2. **Điền các ô trống trong `consent.vi.md`:** mức thù lao (§5), người phụ trách (§10),
   và **trạng thái xét duyệt đạo đức (§9)** — nếu không có hội đồng nào thì tick ô
   thứ ba, ta nói thẳng trong bài báo. Không gửi bản consent còn ô trống cho ai.
3. **Rà soát các ngưỡng ở `qc-protocol.md` §3** (Q1 ≥9/18, R1 <40%, R2 <40%, R3 >25%,
   R4 >40%). Chốt xong là **đông cứng**, sau đó chỉ được ghi thêm mục sửa đổi có ngày.
4. **Dựng `gold-set.txt`** theo qc-protocol §2.1 — cần owner nghe lại thủ công.
   Bước 1 (lọc + phân tầng) đã tự động: `pick_gold_candidates.py` → 34 ứng viên
   trong `gold-candidates.tsv`. Bước 2 nghe và xác nhận: mở **`/gold.html`** trong
   labeler (`Space` nghe · `K` giữ · `D` loại), bấm ghi → `gold-set.txt`.
   Màn này **đếm clip đã thật sự phát** và cảnh báo khi ghi nếu còn clip "giữ mà
   chưa nghe" — gold chưa nghe là gold không kiểm chứng, mà cả QC gate dựa lên nó.

## Milestone còn lại

M2 schema `(epkey, id, annotator)` · M3 backend auth + role + assignment ·
M4 frontend `/rate` · M5 ngrok + ops · M6 qualification · M7 vòng reliability ·
M8 nhãn-của-record. Chi tiết + exit criteria: [doc sống](../../../tasks/online-multi-annotator-labeling.md).

## Ràng buộc mang theo

- **I1 / ADR-005:** 7 safeguard là **cả gói** — thiếu một là quyết định mất hiệu lực.
  Dễ vỡ nhất khi code là safeguard #2: `/gold`, `/episode`, và mọi route export
  **phải admin-only** trước khi mở tunnel.
- **I2:** mọi nhãn mang annotator id + timestamp.
- **I6:** κ human–human là con số tin cậy nhãn; **không** báo teacher như baseline.
- **ADR-004:** `state.db` chưa có lock-file 1-writer → vẫn phải **tắt server** trước
  khi chạy script ghi (migrate M2).
