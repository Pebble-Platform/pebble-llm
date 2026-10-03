# Tool label online đa người — đo κ human–human cho ViEmoSpeech

- **Slug:** online-multi-annotator-labeling
- **Status:** in-progress — **tool xong (M0–M5 + script M7/M8), chờ annotator thật**
- **Created:** 2026-07-28  ·  **Updated:** 2026-07-28
- **Owner:** user / Claude

## Goal

Đưa thêm **annotator từ xa** vào label lại các clip **đã cắt sẵn**, để ViEmoSpeech
có **κ/α human–human** — con số tin cậy nhãn mà ADR-003 bắt buộc và hiện đang
**thiếu hoàn toàn** (793 clip đều single-pass, 1 người). Không có số này thì
dataset paper không qua được vòng review. Tool online chỉ làm **một việc**: phát
clip đã cắt + thu nhãn. **Không cắt, không chia, không excise, không segment** —
những thao tác đó ở lại local, chỉ owner làm.

"Done" = có κ (7 lớp) + α (valence/arousal) tính từ ≥3 rater độc lập trên một
subset phân tầng, kèm script sinh báo cáo, và nhãn-của-record được nâng cấp từ
single-pass lên majority-vote trên subset đó.

## Requirements & Constraints

**Functional**
- Annotator đăng nhập bằng tài khoản đích danh → nhận hàng đợi clip đã gán sẵn →
  nghe → chọn emotion (7 lớp) + valence 1–5 + arousal 1–5 → lưu → clip kế.
- Mỗi nhãn mang `annotator_id + timestamp` (I2).
- Owner tạo được **assignment manifest**: clip nào giao cho ai, chồng lấn bao nhiêu.
- Tính được κ/α từ dữ liệu thu về, bằng script commit trong repo (I5).

**Constraints (ràng buộc cứng)**
- **Media legality (intent §1):** clip là phim có bản quyền. Chỉ **stream**, không
  cho tải, không endpoint export nào tới được bằng tài khoản annotator.
  Hosting = **tunnel từ máy owner** (quyết định user 2026-07-28) — không copy media
  lên hạ tầng bên thứ ba.
- **Blind (mới, load-bearing):** annotator **không được thấy** nhãn của owner,
  nhãn của annotator khác, hay gợi ý teacher (opus/sonnet). Thấy = κ vô nghĩa vì
  nhãn bị neo. Đây là khác biệt then chốt so với UI hiện tại (UI owner **có** hiện
  teacher read-only theo ADR-003).
- **Thứ tự clip xáo trộn** theo từng annotator — vừa chống hiệu ứng thứ tự/ngữ
  cảnh scene, vừa là biện pháp pháp lý (không ai ráp lại được một cảnh liền mạch).
- **Không mở rộng bề mặt sửa dữ liệu:** route cut/split/excise/segment/export
  **không** reachable bằng role annotator.
- Repo convention: Python + `uv` + `ruff`, không npm/pnpm/Biome. Thay đổi phẫu
  thuật, code tối thiểu.
- Không phá `state.db` hiện có: 793 nhãn của owner phải sống sót nguyên vẹn.

**Non-goals**
- Không tuyển crowd mở (MTurk/Prolific) — đã loại, xem Decision Log.
- Không xây dashboard IAA thời gian thực; κ tính offline bằng script.
- Không double-annotate toàn bộ 793 clip ở vòng 1 (xem M7 vs M9).

## Milestones

- [x] **M0 — Chốt cách đọc intent §1** — ✅ 2026-07-28. Quyết định user: stream cho
      annotator mời đích danh qua tunnel = **sử dụng nghiên cứu riêng tư, không phải
      release**; hosting bằng **ngrok** tới server local. Ghi vào
      `docs/intent/constraints.md` §1 + [ADR-005](../spec/decisions/ADR-005-annotation-streaming-not-release.md)
      (kèm 7 safeguard bắt buộc — thiếu 1 là quay về trạng thái chưa được phép).
- [x] **M1 — Protocol design (viết trước khi code)** — ✅ 2026-07-28.
      [`011-online-multi-annotator/`](../spec/changes/011-online-multi-annotator/README.md):
      `annotator-guideline.vi.md` · `consent.vi.md` · `qc-protocol.md`
      (pre-registered) + README ghi quyết định thiết kế. ⚠ **Chưa đông cứng** — chờ
      owner duyệt 4 việc ở README §"Cần owner duyệt".
- [x] **M2 — Schema đa annotator** — ✅ 2026-07-28. Bảng **mới** `ratings`
      khoá `(epkey, id, annotator)`; `records` **không đụng tới** → **không cần
      migrate** (xem Decision Log: đổi so với kế hoạch ban đầu). `store.py`:
      `connect()` tạo bảng idempotent + `put_rating` / `ratings_for_clip` /
      `rated_ids`. Verify trên bản copy tempdir: 3 annotator cùng 1 clip → 3 dòng
      riêng; re-rate chỉ thay dòng của chính mình; **813 nhãn owner nguyên vẹn**;
      integrity ok; ruff sạch.
- [x] **M3 — Backend role + auth + assignment** — ✅ 2026-07-28. `auth.py` (token
      `tokens.json` + role + log truy cập) · **một** middleware `guard` trong
      `server.py` làm biên bảo mật (deny-by-default) · route `/rate/*` ·
      `scripts/vietnamese-ser/build_assignments.py` (phân tầng + gold + dup + xáo).
      *Verified:* annotator **403 trên cả 9 route owner**; request qua tunnel
      **401** (không thừa hưởng loopback-admin); token sai/thiếu 401; slot ngoài
      hàng đợi 404; reassign từ chối ghi đè; 813 nhãn owner nguyên vẹn.
- [x] **M4 — Frontend `/rate`** — ✅ 2026-07-28. `rate.html` + `rate.js`: play +
      7 phím emotion + 2 thang 1–5 + gửi + bỏ qua có lý do. **Mù**: không
      transcript, không teacher, không nhãn owner, không epKey/clip_id. Audio địa
      chỉ hoá **theo vị trí hàng đợi**. *Verified:* shell không rò một chuỗi nhạy
      cảm nào; `/rate/next` chỉ trả `{seq, done, total}`; `listen_ms` được ghi.
      ⚠ Tương tác thật vẫn cần người click-test (nợ repo-wide).
- [x] **M5 — Tunnel + ops** — ✅ 2026-07-28 (dạng runbook, chưa chạy thật).
      [`RUNBOOK.md`](../spec/changes/011-online-multi-annotator/RUNBOOK.md): tạo
      token → dựng hàng đợi → chạy server `--no-local-admin` → `ngrok http 8000` →
      link `/rate.html?t=<token>` → theo dõi → đóng vòng. ⚠ **Chưa verify với
      ngrok thật**: giới hạn bandwidth tier + trang cảnh báo chen giữa của tier free.
- [ ] **M6 — Vòng qualification** — mời 4–6 người → pretest ~30 clip (có 1 câu bẫy)
      + practice batch có feedback → giữ ~3. *Exit:* **đo throughput thật**
      (clip/giờ) và ghi vào doc này — thay số ước lượng 50–70/h.
- [~] **M7 — Vòng reliability** — **script xong, dữ liệu chưa có.**
      `scripts/vietnamese-ser/iaa_report.py` ✅ 2026-07-28: Fleiss κ + Krippendorff
      α (nominal + ordinal) **tự cài, không thêm dependency**; loại gold/dup theo
      §5.1; tách κ headline (annotator↔annotator) khỏi κ có owner theo §5.3; κ
      theo từng lớp; nhãn-của-record + `no_agreement`; bảng QC. *Verified:* tính
      tay từ định nghĩa khớp code tới 6 chữ số (α=0.762712 trên ví dụ 3-observer
      có khuyết); α nominal ≡ Fleiss κ cho 2 rater ở 3 mức đồng thuận (đẳng thức
      lý thuyết); perfect→1.0, ngẫu nhiên→0.004; chạy full trên vòng tổng hợp
      120 clip × 2 rater ra báo cáo hoàn chỉnh.
      **Còn lại: người thật chấm** — không tự động hoá được.
- [~] **M8 — Nhãn-của-record + cập nhật spec** — **logic xong, chờ dữ liệu.**
      Majority + bucket `no_agreement` + trung bình V/A đã cài trong `iaa_report.py`
      §4 và chạy đúng trên dữ liệu tổng hợp (10.0% `no_agreement`).
      **Còn lại (làm sau khi có số thật):** cập nhật `extraction-pipeline.md` +
      ADR-003; cho `build_kaggle_gold.py` đọc nhãn hợp nhất thay vì nhãn single-pass.
- [ ] **M9 — (stretch) mở rộng ra toàn corpus** — chỉ làm nếu M6 cho thấy throughput
      đủ và annotator còn gắn bó. *Exit:* 793 clip đều ≥3 rater.

## Decision Log

<!-- newest first -->

- **2026-07-29 — GIỮ nút "bỏ qua" có lý do.** *(quyết định user)* Nằm ngoài phạm vi
  nhãn đã chốt ("emotion + V/A") nhưng được duyệt vì nó là **skip**, không phải
  trường nhãn mới: clip bình thường không chậm đi, κ không loãng. Không có đường
  thoát thì clip toàn nhạc / 2 người cãi nhau **buộc annotator đoán bừa**, nhiễu
  chảy thẳng vào κ. Lý do `multi_speaker` còn là tín hiệu miễn phí cho I3.
  Lượt skip loại khỏi tập tính κ khi ≥2/3 rater bỏ qua (qc-protocol §5.1).
- **2026-07-28 — M3 sửa lại khoá của M2: `(annotator, seq)` thay vì
  `(epkey, id, annotator)`.** Khi dựng hàng đợi mới thấy khoá M2 **không đỡ được
  chính QC protocol tôi viết ở M1**: §2.2 bắt seed ~10% clip **lặp lại** để đo tự
  nhất quán → cùng một clip trình bày cho cùng một người **hai lần**, mà khoá cũ
  chỉ cho một dòng ⇒ lần thứ hai đè lần thứ nhất, mất sạch phép đo. Đổi thành
  bảng `assignments` khoá `(annotator, seq)`: một dòng = **một lần trình bày**,
  gộp luôn hàng đợi và câu trả lời (cột nhãn NULL tới khi chấm). Vẫn giữ nguyên
  bảo đảm của M2 (annotator trong khoá ⇒ không ai đè ai; `records` không đụng).
  Bắt được sớm vì bảng M2 còn 0 dòng. Rejected: giữ 2 bảng riêng
  assignments + ratings (thêm khớp nối, không được gì).
- **2026-07-28 — Biên bảo mật = MỘT middleware, không phải dependency trên từng
  route.** `guard` trong `server.py` chặn mọi thứ trừ 2 file shell, và mọi route
  **không** thuộc `/rate/*` là owner-only. Lý do: biên audit được ở một chỗ thì
  không thể bị vô hiệu bằng cách **quên** trang trí một route mới — route thêm sau
  này mặc định là owner-only cho tới khi ai đó cố ý đặt nó dưới `/rate/`. Rejected:
  `Depends(admin)` trên ~20 route (dài hơn, và một lần quên là một lỗ hổng).
- **2026-07-28 — Loopback KHÔNG được tự động là admin khi có tunnel.** Cạm bẫy
  thật: ngrok nối tới server qua localhost, nên `request.client.host` của traffic
  từ internet **cũng là 127.0.0.1**. Tin vào socket thôi là **trao quyền admin cho
  cả internet** ngay khi mở tunnel. Fix: chỉ coi là local khi loopback **VÀ** không
  có header `x-forwarded-*` (proxy luôn tự khai). Thêm cờ `--no-local-admin` làm
  lớp thứ hai, runbook bắt dùng khi tunnel mở. Có test riêng cho đúng ca này.
- **2026-07-28 — Annotator địa chỉ hoá audio THEO VỊ TRÍ hàng đợi
  (`/rate/clip/<seq>.wav`), không theo `epKey/clip_id`.** Họ không bao giờ biết
  danh tính clip ⇒ không liệt kê được corpus, không ráp lại được cảnh liền mạch —
  safeguard #2/#4 của ADR-005 được bảo đảm **bằng cấu trúc**, không phải bằng kỷ
  luật. Rejected: trả epKey/id rồi tin annotator không mò (safeguard thành lời hứa).
- **2026-07-28 — Tự cài Fleiss κ + Krippendorff α thay vì thêm package.** Repo
  chưa có dependency `krippendorff`; ~60 dòng số học đối chiếu thẳng được với định
  nghĩa, reviewer kiểm dễ hơn một wheel bị pin. Đã verify: tính tay khớp code tới
  6 chữ số; α nominal ≡ Fleiss κ cho 2 rater (đẳng thức lý thuyết). Rejected: thêm
  dependency cho một script chạy vài lần.
- **2026-07-28 — M2: bảng `ratings` RIÊNG, không đổi khoá của `records` (lệch khỏi
  kế hoạch ban đầu).** Kế hoạch M2 ban đầu ghi "đổi khoá thành `(epkey, id,
  annotator)` + migrate nhãn owner thành `annotator='owner'`". **Khi vào code mới
  thấy làm thế là sai:** `records.data` là một JSON blob **trộn hai loại thứ** — (a)
  trạng thái clip do owner sở hữu (`recut`, `excised`, `rejected`, `split_*`,
  `start/end`, `gold_text`, gợi ý teacher) và (b) phán đoán nhãn. Trạng thái clip
  **không phải per-annotator**. Đổi khoá `records` sẽ nhân bản trạng thái clip cho
  từng annotator (sai về ngữ nghĩa: dòng của annotator sẽ mang cờ `rejected` mà họ
  không có quyền đặt), và muốn tách đúng thì phải mổ `store.py` + `server.py` +
  `episodes.py` + toàn bộ frontend — phá vỡ nguyên tắc surgical và đặt 813 nhãn thật
  vào rủi ro. → Thay bằng **bảng `ratings` riêng**, chỉ chứa phán đoán
  (`emotion, valence, arousal, skip_reason`) khoá `(epkey, id, annotator)`.
  **Lợi thêm ngoài dự tính: không cần migrate gì cả** — nhãn owner ở nguyên trong
  `records`, đường code cũ không đổi một dòng. Script tính κ sẽ đọc cả hai nguồn và
  chuẩn hoá (owner trong `records` mang `annotator='human'`, 813 dòng). Rejected:
  đổi khoá `records` (lý do trên); copy nhãn owner sang `ratings` cho "đồng nhất"
  (2 nguồn sự thật cho cùng một nhãn — kiểu lỗi đồng bộ kinh điển).
- **2026-07-28 — M0 GIẢI QUYẾT: "never leaves the machine" = "never committed /
  never released"; stream cho annotator mời đích danh qua tunnel KHÔNG phải
  release.** *(quyết định user: "cho phép user khác read thông qua máy local, dùng
  ngrok vẫn thoả được yêu cầu")* Đã ghi vào `docs/intent/constraints.md` §1 +
  [ADR-005](../spec/decisions/ADR-005-annotation-streaming-not-release.md). Lý do
  đứng được: I1 — invariant vận hành duy nhất của §1 — **luôn luôn** chỉ đo
  commit/release (`git ls-files data/` + lint release manifest), chưa bao giờ đo
  network; câu tóm tắt ở constraints.md:32 mới là chỗ nghiêm quá tay so với chính
  invariant của nó. Hiệu lực **kèm 7 safeguard bắt buộc cả gói** (token đích danh ·
  không endpoint download/export cho role annotator · excerpt ngắn · thứ tự xáo
  trộn · thoả thuận sử dụng dữ liệu · log truy cập · tunnel chỉ bật khi chạy vòng
  label) — thiếu một cái là quay về trạng thái chưa được phép. Vẫn cấm nguyên vẹn:
  publish/commit media · truy cập bulk/liền mạch · crowd mở · **mọi bản sao thường
  trú ngoài máy này**. Rejected: đọc nghĩa đen (giết cả task, chỉ còn label tại chỗ
  → không bao giờ có κ → dataset paper không qua review).
- **2026-07-28 — Tunnel: ngrok.** *(quyết định user)* Thay cho Cloudflare Tunnel nêu
  ở M5 bản đầu. Cả hai tương đương về điểm cốt lõi (không tạo bản sao thường trú
  ngoài máy). ⚠ **Lưu ý phải nói thẳng:** ngrok **terminate TLS ở edge của họ** —
  traffic audio đi qua hạ tầng bên thứ ba dưới dạng **transit**. Khác VPS ở chỗ
  không có bản sao thường trú, nhưng **không** phải "không bên thứ ba nào chạm tới".
  → data statement viết *"streamed via an authenticated tunnel"*, **đừng** viết
  *"never touched any third-party server"*. Việc cần kiểm trước M5: giới hạn
  bandwidth/phiên của tier đang dùng, và trang cảnh báo chen giữa của tier free
  (gây khó chịu cho annotator) — tier trả phí cho domain cố định đáng cân nhắc.
- **2026-07-28 — Thiết kế chồng lấn: subset phân tầng ~250 clip trước, KHÔNG
  triple-annotate cả 793 ngay.** Hai research block mâu thuẫn nhau ở đúng điểm
  này: block "κ protocol" khuyến nghị full-corpus (vì mọi corpus được trích dẫn —
  IEMOCAP/MELD/CREMA-D/MSP-Podcast/THAI-SER — đều multi-rate 100% phần họ phát
  hành); block "recruitment" khuyến nghị subset 150–250 clip (vì full-coding
  ~13 giờ/người là quá sức cho tình nguyện viên). Chốt **theo giai đoạn**: M7 lấy
  subset để có κ + kiểm chứng protocol chạy được; M9 mở rộng nếu người ở lại.
  Lý do chọn thế: con số κ — thứ đang chặn bài báo — chỉ cần subset là hợp lệ và
  đúng chuẩn báo cáo; còn "nâng mọi nhãn lên majority-vote" là phần thưởng thêm,
  không nên đem cả task đi cược vào việc 3 tình nguyện viên chịu ngồi 13 giờ.
  Rủi ro phải nói thẳng trong paper: phần corpus ngoài subset vẫn là single-pass.
  Rejected: full-corpus ngay (rủi ro annotator bỏ giữa chừng → không có gì);
  chỉ 150 clip (mỏng cho 7 lớp — lớp `surprise` chỉ có 39 clip toàn corpus).
- **2026-07-28 — Thống kê báo cáo: Fleiss κ (7 lớp) + Krippendorff ordinal α
  (valence, arousal riêng).** Cohen κ sai ở đây (chỉ dành cho 2 rater). Trên
  subset full-overlap thì coverage đều nên Fleiss κ hợp lệ, và κ là con số các
  corpus cùng ngành báo (so sánh được: MELD 0.34, MSP-Podcast 0.411, CREMA-D α
  0.42, THAI-SER α thô 0.413). V/A là thang thứ bậc 1–5 → ordinal α, **không**
  dùng ICC/CCC (những cái đó cho rating liên tục theo thời gian kiểu RECOLA).
  Ngưỡng chấp nhận: **κ/α ≈ 0.35–0.55 là đạt** cho phim truyền hình diễn xuất —
  đúng vùng mà các corpus đã được xuất bản đang nằm; **không** áp ngưỡng 0.667/0.8
  của Krippendorff (không corpus SER nào được trích dẫn đạt nổi).
  (see Research: κ protocol)
- **2026-07-28 — Nhãn-của-record: majority/plurality + bucket `no_agreement`;
  V/A = trung bình 3 rater. KHÔNG dùng EWE.** EWE cần pool rater lớn và ổn định
  để ước lượng trọng số tin cậy; ở N=3 là quá tay và không kiểm chứng được. Bản
  phát hành MSP-Podcast 2025 hiện cũng dùng plurality + mean chứ không EWE.
  (see Research: κ protocol)
- **2026-07-28 — QC không được làm phồng κ: chỉ loại annotator theo tiêu chí
  KHÁCH QUAN chốt trước.** Gold clip (owner đã adjudicate) + clip trùng lặp kiểm
  tra tính nhất quán + sàn thời-gian-nghe tối thiểu; ngưỡng loại (<50% gold hoặc
  consistency) **ghi ra giấy trước khi vòng label bắt đầu**. Tuyệt đối **không**
  loại người vì bất đồng với đa số — làm thế là lập luận vòng tròn, κ tự phồng lên.
  Nếu muốn thêm, báo cả số thô lẫn số hiệu chỉnh MACE, không lặng lẽ lọc.
  (see Research: recruitment & QC — THAI-SER pretest 56% pass; MSP-Podcast loại
  430 worker + 44.968 annotation TRƯỚC khi tính κ 0.411)
- **2026-07-28 — Build, không buy: mở rộng `tools/labeler/` thay vì Label Studio /
  Potato.** Label Studio Community (Apache-2.0) **paywall đúng thứ ta cần** —
  overlap, gán task cho user cụ thể, và agreement metrics đều là Enterprise.
  Potato (GPLv3+) hợp mục đích nhất trong nhóm "buy" nhưng là stack thứ hai, phải
  mô hình lại toàn bộ schema nhãn bằng YAML rồi ETL ngược về `(epKey, clip_id)`
  của `state.db`. Bề mặt cần xây thực ra là **tập con** của UI đã có (phát clip +
  form nhãn đã dựng đúng y như spec), phần thiếu chỉ là identity + assignment +
  auth. Rejected: doccano (không có widget audio), INCEpTION (text span),
  Prodigy ($390–490/ghế, vẫn phải tự viết logic overlap), CVAT (video bbox).
  Đối luận trung thực: nếu pool annotator sau này lớn hơn nhiều hoặc cần dashboard
  IAA/reviewer workflow thì Potato đáng xem lại — nó thua ở "ta đã sở hữu schema
  chạy được", không thua ở năng lực. (see Research: build vs buy)
- **2026-07-28 — Hosting: tunnel từ máy owner, không VPS.** *(quyết định user)*
  Giữ số bản sao media ở đúng **một** — không tạo bản sao thường trú trên hạ tầng
  bên thứ ba, không dính TOS/tài phán của một host nữa. Đổi lại: máy owner phải bật
  khi annotator làm việc. Rejected: VPS có auth (thêm 1 bản sao media, phải biện
  minh riêng trong data statement); chỉ LAN/VPN (thực tế chặn mất người tham gia).
- **2026-07-28 — Annotator pool: người quen / sinh viên mời đích danh, 4–6 mời →
  giữ ~3.** *(quyết định user)* Prolific và MTurk **không dùng được**: Việt Nam
  không nằm trong danh sách quốc gia được hỗ trợ/chi trả của cả hai. Crowd mở còn
  là phương án rủi ro pháp lý cao nhất với media có bản quyền. MSP-Podcast cũng đã
  **từ bỏ** AMT mở để chuyển sang 14–20 sinh viên được sàng lọc.
  (see Research: recruitment & QC)
- **2026-07-28 — Nhãn thu ở vòng online: emotion 7 lớp + valence + arousal.**
  *(quyết định user)* Đủ để báo κ categorical + α ordinal cho đúng phần nhãn cốt
  lõi. Giới tính/tuổi/vùng miền **không** thu ở vòng này (không phải target train,
  và thêm trường thì mỗi clip chậm hơn, κ loãng ra).

## Open Questions

- [x] ~~**M0 — "Copyrighted media never leaves the machine" nghĩa là gì?**~~
      **Giải quyết 2026-07-28** → xem Decision Log +
      [ADR-005](../spec/decisions/ADR-005-annotation-streaming-not-release.md).
- [ ] Owner có kênh IRB/hội đồng đạo đức nào không? Quyết định nội dung phần ethics
      statement. Nếu không có, **nói thẳng là không có** trong bài báo, đừng lờ đi.
- [ ] Data-use agreement cho annotator có cần là văn bản pháp lý thật (luật sư /
      phòng nghiên cứu duyệt) hay một bản cam kết ngắn là đủ? Research không trả
      lời được câu này và **không phải tư vấn pháp lý**.
- [ ] Series nào làm test-split (ADR-002) — chưa chốt, và nó ảnh hưởng tới cách
      phân tầng subset ở M7 (nên phủ cả 2 series).

## Research Findings

<!-- 4 block task-researcher, 2026-07-28. Rút gọn phần luận option; giữ nguyên số liệu, khuyến nghị, nguồn. -->

### Finding 1 — Giao thức κ tối thiểu cho một corpus paper SER

**Short answer:** N=3 rater/clip. Fleiss κ cho 7 lớp; Krippendorff **ordinal** α
cho V/A. Chấp nhận κ/α ~0.35–0.55 cho drama diễn xuất. Nhãn-của-record =
plurality + mean, **không** EWE.

| Corpus | N rater/clip | % multi-rated | Stat | Giá trị báo | Quy tắc hợp nhất |
|---|---|---|---|---|---|
| IEMOCAP (2008) | 3 (đôi khi 4) | 100% | Fleiss κ | κ **0.48** / **0.27** (tùy subset — đừng neo vào 1 số) | majority 2/3; ~25% không majority để ngỏ |
| MELD (2019) | 5 (AMT) | 100% | Fleiss κ | κ **0.34** | majority vote |
| CREMA-D (2014) | ≥6, TB **9.8** | 100% | Krippendorff α | α **0.42** | plurality/mode |
| MSP-Podcast v2.0 (2025) | ≥5 TB (1.446M annot / 267.905 turn) | 100% | plurality + lớp "no-agreement" | κ **0.411**; V α **0.508**, A α **0.441**, D α **0.386** | **plurality** + **mean** across rater |
| THAI-SER (2025) | 3–8, đa số 3 | 100% (rồi lọc) | Krippendorff α + MASI | α thô **0.413** → lọc (cắt 0.71) **0.692** | consensus + gold/consistency gate |
| EmoDB (2005) | 20 listener | 100% | % recognition | 84–86% | lọc chọn, không vote |

*Caveat:* κ của IEMOCAP dao động 0.27–0.48 tùy nguồn/subset. RECOLA/SEWA/MSP-IMPROV
**chưa verify được** → đã loại khỏi lập luận ngưỡng. THAI-SER lọc bỏ ~49% clip
thấp-đồng-thuận để nâng α — repo mình **đã tự khuyến nghị không copy cách này**
(`docs/papers/vietnamese-ser/11-thai-ser-corpus.md:230-233`), vì corpus mình nhỏ và
lớp hiếm đã mỏng sẵn.

*Blocker kỹ thuật agent này tự phát hiện (đã tự xác minh lại trong code):*
`state.db` khoá `(epkey, id)`, không có chiều annotator → rater #2/#3 sẽ **đè**
nhãn của owner. Phải sửa schema trước khi ai đó bắt đầu label.

*Nguồn:* [IEMOCAP](https://sail.usc.edu/iemocap/Busso_2008_iemocap.pdf) ·
[MELD arXiv:1810.02508](https://arxiv.org/pdf/1810.02508) ·
[CREMA-D](https://pmc.ncbi.nlm.nih.gov/articles/PMC4313618/) ·
[MSP-Podcast arXiv:2509.09791](https://arxiv.org/abs/2509.09791) (deep-read repo:
`docs/papers/bimodal-ser/12-msp-podcast-corpus.md:104-135`) ·
[THAI-SER arXiv:2507.09618](https://arxiv.org/abs/2507.09618) (`docs/papers/vietnamese-ser/11-thai-ser-corpus.md:60-92`) ·
[EmoDB](https://www.isca-archive.org/interspeech_2005/burkhardt05b_interspeech.html) ·
[Artstein & Poesio 2008](https://aclanthology.org/J08-4004/).

### Finding 2 — Build vs buy

**Short answer:** Mở rộng `tools/labeler/`. Bề mặt cần thêm là tập con của cái đã
có; thiếu đúng 3 thứ: identity per-annotator, assignment/overlap manifest, auth.

- **Label Studio Community** (Apache-2.0, verify 2026-07-28): audio có trong bản
  free, nhưng **overlap, gán task cho user cụ thể, agreement metrics, RBAC đều là
  Enterprise/Starter-Cloud** — tức là đúng thứ cần nhất thì bị khoá; dùng Community
  vẫn phải tự viết assignment, lúc đó đã xây gần hết Option B trên một stack React
  nặng hơn. ([docs.humansignal.com/guide/label_studio_compare](https://docs.humansignal.com/guide/label_studio_compare))
- **Potato / Potato 2.0** (GPLv3+, ACL demo 2026): hợp mục đích nhất trong nhóm
  buy — form đa widget theo config, claim có audio + overlap + κ/α. Nhưng là stack
  thứ hai, schema YAML riêng, phải ETL ngược về `(epKey, clip_id)`. *Độ tin cậy
  trung bình* — các claim về widget audio (sóng hay chỉ `<audio>` trần) lấy từ tóm
  tắt trang, chưa đọc doc từng dòng; nếu sau này nghiêng về Potato thì phải verify lại.
- **doccano** (MIT): không có widget audio; overlap là điểm yếu đã biết
  ([issue #288](https://github.com/chakki-works/doccano/issues/288)). Loại.
- **INCEpTION**: span/relation trên text (UIMA CAS). Loại.
- **Prodigy**: $390–490/ghế, có audio, nhưng **không** có recipe "gán N trong M
  annotator có overlap" sẵn — vẫn phải tự viết, nên không tiết kiệm được cái mà
  Option A lẽ ra phải tiết kiệm. Loại.
- **CVAT**: bbox ảnh/video. Loại.

*Bằng chứng trong code (agent trích, tôi đã tự xác minh):* `tools/labeler/store.py:71-74`
`PRIMARY KEY (epkey, id)` — không có chiều annotator; `tools/labeler/server.py:32-42`
`GoldIn.annotator` **có tồn tại nhưng không nằm trong khoá lưu**; `server.py:348`
mặc định `127.0.0.1`, **không auth**. `tools/labeler/SPEC.md:186-187` chính repo đã
ghi single-pass/chưa có κ là nợ đã biết.

*Cảnh báo bảo mật agent nêu:* phải kiểm route `/gold` và `/episode` xem có rò một
manifest URL audio đầy đủ cho role không-phải-owner không.

### Finding 3 — Pháp lý: stream clip có bản quyền cho annotator đích danh

**Short answer:** Chạy được, nhưng phải coi là **sử dụng nghiên cứu riêng tư, có
kiểm soát truy cập** — không phải "phát hành" — và phải làm đủ bộ safeguard. Đây là
**vùng xám pháp lý thật sự ở VN**, không phải chuyện đã ngã ngũ.

- **Khoảng vênh trong repo (điểm mấu chốt của M0):** `constraints.md:32` "never
  leaves the machine" **nghiêm hơn** chính invariant vận hành của nó,
  `invariants.md:15` (I1) = "committed or released", và I1 **không nhắc tới truyền
  qua mạng**; check của I1 là `git ls-files data/` + lint release manifest.
- **Field làm gì:** truy cập có kiểm soát/ký thoả thuận là **chuẩn mực**, không
  phải mở. MSP-Podcast né hẳn vấn đề bằng cách **chỉ lấy podcast đã có licence cho
  phép phân phối**, mà vẫn còn gate sau thoả thuận ký với cơ sở → **playbook đó
  không chuyển sang được** cho phim truyền hình VN. LDC (Switchboard/Fisher) chỉ
  phân phối cho cơ sở có licence. VoxCeleb: CC-BY-4.0 cho **annotation của họ**,
  bản quyền video vẫn của chủ gốc — **đúng hình dạng thiết kế của repo mình**.
  MELD phát hành thẳng file video/audio từ Friends mà agent **không tìm thấy** giấy
  phép nào từ chủ sở hữu — đây là **cảnh báo, không phải hình mẫu**.
- **Luật VN:** Điều 25/25a (Luật 07/2022/QH15 sửa 50/2005/QH11) cho phép **một cá
  nhân** sao chép phục vụ nghiên cứu khoa học/tự học, có dẫn nguồn, không xung đột
  khai thác bình thường; Điều 26 thêm "sao chép hợp lý **một phần** tác phẩm… không
  quá một bản". **Điểm yếu nhất:** văn bản luật viết theo khung "một cá nhân, một
  bản, một phần" — **không** viết cho tình huống stream cho nhiều cộng tác viên
  qua mạng. Agent **không tìm được án lệ hay hướng dẫn** giải quyết điểm này → coi
  là **chưa ngã ngũ**. Chiếu three-step test Berne: excerpt 2–10s, không liền mạch,
  có kiểm soát truy cập, phi thương mại → khá mạnh ở bước 2–3, **yếu ở bước 1**
  ("special case" cho truy cập nhiều người).
- **Venue:** ARR nói rõ vấn đề bản quyền/licence **tự nó không kích hoạt** ethics
  review đầy đủ; reviewer nêu trong review, và bài báo phải nêu rõ nguồn gốc +
  kiểm soát truy cập. Một data statement né tránh/vắng mặt **dễ bị flag hơn** một
  bản thừa nhận thẳng vùng xám.
- **Safeguard bắt buộc — cả gói, không chọn lẻ:** tài khoản đích danh (không phải
  link mở) · chỉ excerpt ngắn · **không** bulk download, **không** endpoint export
  tới được bằng role annotator (`/gold` + ZIP phải admin-only) · **thứ tự xáo trộn**
  để không ráp lại được cảnh · **thoả thuận sử dụng dữ liệu ngắn** annotator ký
  trước khi truy cập (không phát tán, không ghi màn hình, xoá cache) · **log truy
  cập** · **ưu tiên tunnel từ máy nghiên cứu viên hơn VPS** (giữ số bản sao ở một,
  gần với "một cá nhân" của Điều 25/26 hơn) — *phần tunnel-vs-VPS là suy luận quản
  trị rủi ro, **không** có nguồn trích dẫn, agent tự flag độ tin cậy thấp hơn*.
- **Off the table:** crowd mở (MTurk) trên media này · truy cập bulk/liền mạch cả
  tập · hosting công khai/bán công khai · phát hành clip kiểu MELD.
- **Câu chữ đề xuất cho data/ethics statement** (chỉnh theo sự thật cuối cùng):
  > *"Source episodes are copyrighted Vietnamese television drama, obtained for
  > research use only. Neither full episodes nor the released dataset contain raw
  > audio, video, or full transcripts; the released artifact is limited to
  > acoustic/prosodic features, timestamps, emotion/valence-arousal labels, and
  > speaker ids, under CC-BY 4.0. For inter-annotator reliability, a subset of
  > short (2–10s) excerpts was streamed — never downloaded or redistributed — to a
  > small number of named, authenticated research collaborators under a data-use
  > agreement, for annotation purposes only; no annotator retained a copy of the
  > underlying media."*

*Nguồn:* [MSP-Podcast](https://www.lab-msp.com/MSP/MSP-Podcast.html) ·
[arXiv:2509.09791](https://arxiv.org/abs/2509.09791) ·
[MELD arXiv:1810.02508](https://arxiv.org/abs/1810.02508) ·
[VoxCeleb](https://www.robots.ox.ac.uk/~vgg/data/voxceleb/) ·
[LDC Catalog](https://catalog.ldc.upenn.edu/) ·
[ARR ethics flagging](http://aclrollingreview.org/ethics-flagging-guidelines/) ·
[WIPO Lex VN IP Law](https://www.wipo.int/wipolex/en/legislation/details/12011) ·
[vietnamcopyright.com fair use](https://vietnamcopyright.com/principle-of-fair-use-in-vietnamese-intellectual-property-law/).

> ⚠️ Đây là **báo cáo về thực tiễn của ngành và nội dung nguồn luật, không phải tư
> vấn pháp lý.**

### Finding 4 — Tuyển người, đào tạo, QC, đạo đức

**Short answer:** Mời 4–6 → giữ ~3 qua kênh VLSP/sinh viên đại học (Prolific và
MTurk **không phủ Việt Nam**). Qualification có gold trước khi nhãn được tính. QC
bằng gold/consistency **pre-registered**, **không bao giờ** loại vì bất đồng với
đa số. Ethics statement theo checklist ARR Responsible NLP.

- **Tuyển:** Prolific (danh sách nước neo OECD) và MTurk (23 nước được chi trả)
  **đều không có VN** → thực tế không có pool VN-L1 nào trên đó. Nền tảng thương
  mại nội địa có số liệu lương thật ($5.6–$25/h) nhưng tối ưu cho label khối lượng
  lớn, không phải rating tri giác cẩn thận. → **Sinh viên / mạng lưới VLSP / người
  quen của advisor** là pool duy nhất khớp ràng buộc.
- **Trả công:** neo giữa mức trung bình thương mại VN (~$5.6/h) và mức cao cho
  ngôn ngữ VN (~$11/h) → đề xuất **~100.000–150.000 VNĐ/giờ (~$4–6)**, hoặc
  micropayment theo clip. Bài báo **phải ghi rõ mức trả + biện minh tính thoả đáng
  so với mức sống địa phương** — đó là mức công bố ARR yêu cầu.
- **Đào tạo:** guideline nêu rõ nhãn là **cảm xúc TRI GIÁC ĐƯỢC, không phải sự thật
  nền**; ví dụ mẫu cho từng lớp ở ca biên; định nghĩa mốc neo cho từng điểm thang
  V/A; hướng dẫn cờ multi-speaker/reject khớp semantic labeler hiện có. Pretest
  ~20–30 clip **có câu bẫy ẩn** (THAI-SER: tỉ lệ đậu 56%), rồi practice batch
  30–50 clip có feedback, **trước khi** nhãn được tính vào corpus.
- **QC không làm phồng κ:** gold clip + clip trùng kiểm tra nhất quán + **sàn thời
  gian tối thiểu mỗi clip** (logic trapping question kiểu ITU-T P.808: ~1 gold + 1
  trapping / 11 trial). **Pre-register** ngưỡng loại (<50% gold hoặc consistency)
  **trước** khi vòng bắt đầu. THAI-SER loại/label lại **chỉ** theo gold/consistency
  khách quan, không theo bất đồng với đa số. Tuỳ chọn: đối chiếu MACE
  (down-weight thay vì loại), **báo cả số thô lẫn số hiệu chỉnh**, không lọc lặng lẽ.
- **Bằng chứng crowd mở thất bại:** MSP-Podcast **bỏ** AMT (bot, submit ngẫu nhiên)
  → chuyển 14–20 sinh viên được sàng lọc, feedback xếp hạng tương đối hằng tuần,
  bắt buộc retrain; loại **430 worker + 44.968 annotation** *trước khi* tính κ 0.411
  (`docs/papers/bimodal-ser/12-msp-podcast-corpus.md:104-112`).
- **Đạo đức/consent:** không qua platform ⇒ **phải tự xây luồng consent**. Nội dung:
  mục đích + nhãn dùng/phát hành thế nào (chỉ features+labels, không bao giờ audio
  — I1) · **cảnh báo nội dung** (clip diễn giận dữ/sợ hãi/đau buồn/distress) ·
  tự nguyện, được bỏ qua/rút lui · điều khoản trả công · **mỗi nhãn gắn annotator
  id + timestamp (I2)** và nêu rõ id đó có công bố hay ẩn danh · **điều khoản không
  phát tán** clip (cầu nối I1 vào thoả thuận annotator). Clip ngắn 2–10s diễn xuất
  ⇒ IRB không hiển nhiên bắt buộc, nhưng **kiểm tra với cơ sở của owner**; nếu
  không có kênh IRB nào thì **ghi thẳng khoảng trống đó** vào ethics statement thay
  vì bỏ trống. Theo constraints §7: mở rộng khung "distress là proxy diễn xuất,
  không phải nguy cơ lâm sàng" **sang cả annotator**, không chỉ chủ thể dữ liệu.
- **Throughput:** không tìm được số công bố cho đúng tổ hợp task này (đã tìm
  IEMOCAP/MSP-Podcast — không công bố). Ước lượng **~50–70 clip/giờ** *(độ tin cậy
  thấp, suy từ P.808)*. 3 annotator × subset 150–250 clip ≈ **5–10 giờ/người**,
  vừa trong 1–2 tuần. → **Lấy log thời gian của vòng qualification làm số đo thật**
  và ghi đè ước lượng này (đã đưa vào exit criterion của M6).

*Caveat agent tự nêu:* 793 nhãn single-pass của owner dùng làm "gold" pretest
**không phải ground truth độc lập** (phim truyền hình tìm được không có nhãn do
đạo diễn/diễn viên gán như THAI-SER) → trong guideline phải gọi là **"mốc neo"**,
không gọi là "sự thật".

*Nguồn:* [Prolific eligibility](https://www.prolific.com/participants-frequently-asked-questions) ·
[MTurk 23 countries](https://blog.mturk.com/amazon-mechanical-turk-workers-in-23-countries-outside-of-the-us-can-now-transfer-their-earnings-98ec29ef7f7f) ·
[MACE, Hovy et al. NAACL 2013](https://www.cs.cmu.edu/~hovy/papers/13HLT-MACE.pdf) ·
[Artstein & Poesio 2008](https://aclanthology.org/J08-4004/) ·
[ITU-T P.808 impl., Interspeech 2020](https://arxiv.org/abs/2005.08138) ·
[Beyond Fair Pay, arXiv:2104.10097](https://arxiv.org/abs/2104.10097) ·
[Worker Discretion Advised, CHI 2026](https://arxiv.org/html/2509.12140v3) ·
[ARR Responsible NLP checklist](http://aclrollingreview.org/responsibleNLPresearch/) ·
[Second Talent VN 2026](https://www.secondtalent.com/resources/data-annotation-market-in-vietnam/) ·
[Outlier AI vi-VN](https://outlier.ai/languages/vi-vn).

## Completed Work

- 2026-07-28 — Khảo sát hiện trạng: `state.db` có **1164 record / 793 có nhãn
  emotion / 380 rejected**, 2 series (`chay-tron-thanh-xuan` 518,
  `ve-nha-di-con` 275); phân bố nhãn `neutral 219 · anger 163 · joy 153 ·
  fear_anxiety 82 · sadness 70 · disgust 67 · surprise 39` (⚠ `surprise` mỏng —
  ràng buộc cho phân tầng subset ở M7).
- 2026-07-28 — 4 vòng research song song (κ protocol · build-vs-buy · pháp lý ·
  tuyển người/QC) → `## Research Findings`.
- 2026-07-28 — Xác minh trực tiếp 3 sự thật trong code chặn thiết kế:
  `tools/labeler/store.py:71-74` (PK không có chiều annotator),
  `tools/labeler/server.py:32-42` (`GoldIn.annotator` không nằm trong khoá),
  `tools/labeler/server.py:348` (không auth).
- 2026-07-28 — Chốt 3 quyết định phạm vi với owner: pool mời đích danh · hosting
  bằng tunnel · nhãn thu = emotion + V/A.
- 2026-07-28 — **M3+M4+M5 xong:** `tools/labeler/auth.py` (mới) · `server.py`
  (middleware `guard` + 4 route `/rate/*` + `--tokens`/`--no-local-admin`) ·
  `rate.html` + `rate.js` (mới) · `scripts/vietnamese-ser/build_assignments.py`
  (mới) · `RUNBOOK.md`. Dry-run trên dữ liệu thật: pool 798 → subset 250 cân bằng
  (`joy 38 · sadness 37 · anger 38 · fear_anxiety 38 · surprise 28 · disgust 33 ·
  neutral 38`) + 25 clip lặp = 275 slot/người.
- 2026-07-28 — **M7/M8 hạ tầng xong:** `scripts/vietnamese-ser/iaa_report.py` —
  Fleiss κ + Krippendorff α (nominal/ordinal) tự cài, verify bằng tính tay + đẳng
  thức lý thuyết; chạy full trên vòng tổng hợp ra báo cáo hoàn chỉnh gồm cả tách
  κ headline theo §5.3.
- 2026-07-28 — **M2 xong:** `tools/labeler/store.py` — bảng `ratings` trong
  `connect()` + `put_rating` / `ratings_for_clip` / `rated_ids`. Hot-backup trước
  khi động (`state.db.bak-pre-m2-20260728`, `VACUUM INTO`, integrity ok). Verify
  chạy trên **bản copy tempdir**, không đụng data thật. Schema đã áp lên DB thật
  (chỉ `CREATE TABLE IF NOT EXISTS`, `records` không đổi: 1198 dòng, integrity ok).
  ⚠ Số liệu corpus đã nhích: **1198 record / 813 có nhãn** (lúc khảo sát đầu phiên
  là 1164/793 — owner còn đang label tiếp).
- 2026-07-28 — **M1 xong:** `docs/spec/changes/011-online-multi-annotator/` —
  hướng dẫn annotator (bài báo sẽ đăng nguyên văn theo yêu cầu ARR), consent +
  thoả thuận sử dụng dữ liệu, QC protocol pre-registered (ngưỡng cụ thể + quy tắc
  tính κ + phân tách κ headline), README ghi quyết định thiết kế. Index change
  cập nhật. **Chưa đông cứng** — 4 việc chờ owner ở README.
- 2026-07-28 — **M0 xong:** làm rõ intent §1 trong `docs/intent/constraints.md`
  (đoạn "Clarification (human decision 2026-07-28, ADR-005)") + viết
  `docs/spec/decisions/ADR-005-annotation-streaming-not-release.md` (quyết định,
  7 safeguard bắt buộc, rủi ro đã biết gồm cả điểm TLS-terminate của tunnel).

## Trạng thái: tool xong, chờ người

Toàn bộ phần **máy làm được** đã xong và test (M0–M5, + script M7/M8). Ba việc còn
lại **chỉ người làm được** và không tự động hoá được:

| Việc | Vì sao máy không làm thay được |
|---|---|
| **M6 vòng qualification** | Phải mời người thật, họ ký consent, ngồi nghe và chấm |
| **M7 vòng reliability** | Nhãn phải do tai người tạo ra — script đã sẵn sàng, chỉ thiếu dữ liệu |
| **M9 mở rộng toàn corpus** | Phụ thuộc M6 (throughput thật + annotator có ở lại không) |

## Remaining Action Items

- [ ] **Owner duyệt 4 việc** trước khi đông cứng protocol (chi tiết:
      [change 011 README §"Cần owner duyệt"](../spec/changes/011-online-multi-annotator/README.md)):
      (a) giữ hay bỏ nút "bỏ qua" — **nằm ngoài phạm vi đã chốt, cần anh quyết**;
      (b) điền thù lao + người phụ trách + trạng thái IRB vào `consent.vi.md`;
      (c) rà ngưỡng QC §3; (d) dựng `gold-set.txt` (cần nghe lại thủ công).
- [ ] **Verify ngrok thật** trước vòng đầu: giới hạn bandwidth của tier đang dùng
      (ước tính cần ~400 MB cho 275 slot × 3 người × ~3 lần nghe) + trang cảnh báo
      chen giữa của tier free (annotator gặp mỗi phiên).
- [ ] **Click-test thật màn `/rate`** trên trình duyệt — nợ repo-wide (frontend
      chưa browser-drive được); kiểm autoplay bị chặn, phím tắt, nút bỏ qua.
- [ ] Sau khi có số thật: cập nhật `extraction-pipeline.md` + ADR-003, và cho
      `build_kaggle_gold.py` đọc nhãn hợp nhất (majority) thay vì nhãn single-pass.
