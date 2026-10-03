# Paper 16 — Review and Comparative Analysis of Databases for Speech Emotion Recognition

> Bản dịch tiếng Việt của [16-ser-databases-review.md](16-ser-databases-review.md) — cập nhật 2026-07-10.

- **Authors:** S. Serrano, O. Serghini, G. Esposito, S. Carbone, C. Mento, A. Floris, S. Porcu, L. Atzori
- **Venue / year:** Data (MDPI), 10(10):164, 2025 (OA)
- **Links:** abs https://doi.org/10.3390/data10100164 · PDF `pdfs/16-ser-databases-review.pdf`
- **Group:** khảo sát / benchmark (bộ dữ liệu)

**Summary:** So sánh hơn 50 kho ngữ liệu (corpora) SER (phương pháp thu thập, sơ đồ gán nhãn, mức đa dạng nhân khẩu học, tính hợp lệ sinh thái - ecological validity).

**Relevance to Pebble:** Tài liệu tham khảo để chọn/đánh giá dataset SER khi mở rộng voice stream.

> Mục ghi chép ngắn gọn (compact entry) từ đợt rà soát tài liệu (literature sweep) (`docs/tasks/bimodal-ser-papers.md`); chưa đọc sâu (deep-read).

## Analysis (overlap with Pebble)

**Assembled profile (scored against, from the IDD layers):**
- **Chính (văn bản/text):** phân loại nguy cơ tự sát dạng thứ tự (ordinal suicide-risk classification); nhãn silver từ teacher-LLM → đánh giá trên **gold-holdout**; các hàm loss/metric có nhận biết thứ tự (ordinal-aware) (QWK/MAE); khả năng tái lập (reproducibility) + đạo đức dữ liệu lâm sàng (clinical-data ethics) là ràng buộc xuyên suốt toàn repo (`docs/intent/constraints.md`).
- **Liền kề (giọng nói/voice):** backbone emotion2vec/WavLM đóng băng (frozen) + thân chung (shared trunk), **3 head không đồng nhất** — emotion CE / affect V/A **CCC** / crisis BCE dưới một **ngưỡng sàn recall cứng (hard recall floor)** — được cân bằng bằng **Kendall uncertainty weighting** (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`).
- **Giai đoạn hiện tại của voice:** các head được huấn luyện trên **RAVDESS với nhãn proxy** (Russell circumplex V/A; tập crisis mức distress cao). Hành động tiếp theo đã xác định rõ: **thay các proxy bằng MSP-Podcast (A/V/D liên tục) + DAIC (crisis)** để có các con số có ý nghĩa khoa học.

### Analysis — SER Databases Review (Serrano et al., 2025)
- **Overlap:** 27% (peripheral) — D1=1, D2=1, D3=2, D4=0, D5=0, D6=0, D7=0
  - Compute: (3·1 + 2·1 + 1·2 + 2·0 + 2·0 + 2·0 + 1·0) / 26 × 100 = 7/26 × 100 ≈ 27%.
- **Closest on:** D3 (bài báo *chính là* một danh mục các kho ngữ liệu cảm xúc, bao gồm cả những kho có gán nhãn cường độ như MCAESD/MEAD — tương đương phía voice-stream của trục "kho ngữ liệu chuyển giao cảm xúc") và D1-một phần (tổ chức các kho ngữ liệu theo sơ đồ nhãn **categorical vs dimensional/continuous**, đúng là tính lưỡng hệ nhãn mà các head emotion + V/A của Pebble sử dụng).
- **Best point (Dataset to reuse):** Khung so sánh của bài review — các tham số ở Table 2 + chỉ số chất lượng AHP **Q = 0.2615·S′ + 0.0872·E′ + 0.6114·C′ + 0.0400·R′** (số lượng người nói, số cảm xúc, số trích dẫn/năm, độ mới) + bản đồ sử dụng ở Table 3 — là một bản đồ sàng lọc dựng sẵn giúp rút ra danh sách rút gọn các kho ngữ liệu thực sự cung cấp **nhãn liên tục theo chiều (continuous dimensional labels)** và xuất hiện trong các nghiên cứu về độ bền vững (robustness), với MSP-Podcast/MELD/CMU-MOSEI được đánh dấu là các kho ngữ liệu tự nhiên/theo chiều đang dần thay thế các kho ngữ liệu diễn (acted).
  - **How to apply to Pebble:** Dùng bài báo này để biện minh và xác định phạm vi cho kế hoạch thay proxy bằng dữ liệu thật của voice stream — xác nhận **MSP-Podcast (A/V/D liên tục)** là lựa chọn thay thế cho RAVDESS-proxy ở head affect (CCC), lưu ý rằng nó không có nhãn crisis gốc (giữ lại nhóm DAIC cho head ngưỡng sàn recall), sau đó chuyển cả hai ứng viên cho `find-dataset` để kiểm tra license/gate đối chiếu với ràng buộc đạo đức của repo.
- **Caveats:** Chỉ nên đọc chọn lọc: phần mở đầu/phương pháp/phân loại học/mô hình cảm xúc (tr.1-6), đặc điểm kho ngữ liệu + đạo đức của kho ngữ liệu diễn/khơi gợi/**tự nhiên** (tr.7-9), phần cuối của danh mục 52 kho ngữ liệu (tr.44-48), và toàn bộ phần tổng hợp/thảo luận/kết luận bao gồm Q và Table 3 (tr.49-52). Các mô tả riêng lẻ về **RAVDESS / IEMOCAP / MSP-Podcast** trong danh mục mục 6 giữa bài **không** được đọc từng dòng (mức độ bao phủ của chúng được xác nhận qua Table 3, liệt kê IEMOCAP=11, RAVDESS=11, MSP-PODCAST=2 lượt xuất hiện); **DAIC-WOZ** không xuất hiện trong Table 3 và có thể nằm ngoài phạm vi kho-ngữ-liệu-SER của bài review này (nó bao phủ các kho ngữ liệu stress/cuộc gọi khẩn cấp một cách chung chung). Điểm số thấp về mặt cấu trúc vì đây là một *bài review về dataset* — trực giao với các trục mô hình hóa của Pebble (D4-D7 vắng mặt do bản chất bài báo); giá trị thực sự của nó nằm ở việc lựa chọn dataset thực tiễn, điều mà tỷ lệ % trùng lặp không phản ánh được.

## Deep research — full-PDF read (2026-07-10)

> Được chấm điểm dựa trên **hồ sơ ViEmoSpeech hiện tại + Sổ đăng ký Quyết định (Decision Register, V-A…V-H)** trong
> `docs/tasks/paper-deep-analysis.md`, KHÔNG dựa trên phần "Analysis" (text-stream) đã lỗi thời ở trên.
> Đây *chính là* bài báo về bối cảnh kho ngữ liệu (corpus-landscape) cho V-H; nó cũng neo giữ V-E (quy ước sơ đồ nhãn) và
> V-D (bất kỳ kho ngữ liệu ngôn ngữ có thanh điệu / có gán nhãn thanh điệu nào trong số 52 kho).

### Source-access note

- **Đã đọc toàn bộ PDF từ đầu đến cuối** thông qua `pdftotext docs/papers/bimodal-ser/pdfs/16-ser-databases-review.pdf -`
  (1358 dòng; toàn bộ §§1–8, Table 1, toàn bộ Table 2 gồm 52 hàng trải dài từ tr. 11–19, từng
  mô tả kho ngữ liệu riêng lẻ ở §6.1–6.52, phần thảo luận §7 bao gồm chỉ số chất lượng và Table 3,
  và danh mục tài liệu tham khảo). File PDF cục bộ **chính là phiên bản đã xuất bản của tạp chí**: phần đầu trang ghi
  "*Data* **2025**, *10*, 164", "Published: 14 October 2025", DOI 10.3390/data10100164, và thông báo
  CC-BY của MDPI — tạp chí *Data* của MDPI hoàn toàn truy cập mở (open-access) và cung cấp bản PDF dàn trang cuối cùng, nên
  **không có chênh lệch preprint/bản-xuất-bản** cần đối chiếu.
- **Đã kiểm chứng qua web** khung nội dung chính so với trang landing của tạp chí:
  truy vấn `Serrano "Review and Comparative Analysis of Databases for Speech Emotion Recognition"
  Data MDPI 2025 fifty-two corpora quality index` → dẫn tới
  `https://www.mdpi.com/2306-5729/10/10/164`, xác nhận **"fifty-two databases across
  acted, elicited, and natural speech"**, ngày xuất bản 14-10-2025, và khung tường thuật bốn trục (four-axis
  narrative-review framing) (✔). Một lần `WebFetch` trực tiếp trang HTML của MDPI trả về **HTTP 403**
  (bị chặn bot), nên các hệ số của chỉ số Q và định nghĩa bốn trục dưới đây được trích dẫn từ bản PDF
  của tạp chí (equation (1), §5, §7.1) thay vì fetch lại — điều này chấp nhận được vì bản PDF cục bộ
  *chính là* tài liệu đã xuất bản.

### What the paper actually does

Đây là một bài review dạng **tường thuật (narrative)** (nêu rõ *không phải* hệ thống hóa theo PRISMA) + phân tích so sánh **52 kho ngữ liệu SER** được công bố cho tới giữa năm 2025 (§2). Bài báo đóng góp bốn điểm:

1. **Một khung phân loại bốn trục (four-dimension classification framework)** (§5, artifact chịu lực (load-bearing) cho V-H):
   - **Scope (Phạm vi)** — kho ngữ liệu ghi lại cái gì và *được khơi gợi (elicited) như thế nào*: **acted / elicited / natural**;
     tác vụ/ứng dụng mục tiêu; **trong phòng lab vs "in the wild" (ngoài thực địa)**.
   - **Physical Existence (Sự tồn tại vật lý)** — "*liệu kho ngữ liệu có thực sự lấy được và tái sử dụng được hay không*": **quyền truy cập
     và giấy phép (license)**, chất lượng tài liệu/metadata, **định danh bền vững (persistent identifier, DOI)**, và
     **các phần chia train/val/test đã định nghĩa**.
   - **Contents (Nội dung)** — số người nói, tổng thời lượng (giờ/utterance), điều kiện thu âm/kênh + tần số lấy mẫu,
     **phân bố lớp (class distribution)**, **sơ đồ nhãn (categorical vs dimensional)**, *ai gán nhãn*
     (tự đánh giá/quan sát viên/chuyên gia/crowd), độ tin cậy liên-người-đánh-giá (inter-rater reliability), lớp transcript/từ vựng, các
     modal bổ sung.
   - **Language Composition (Thành phần ngôn ngữ)** — ngôn ngữ, **phương ngữ/giọng vùng miền, code-switching**, độ rộng nhân khẩu học.
2. **Một phân loại học về kiểu speech (speech-type taxonomy)** kèm bảng ưu điểm/hạn chế (Table 1, §5): acted (diễn) =
   có kiểm soát/dải cảm xúc rộng/dễ so sánh nhưng tính hợp lệ sinh thái (ecological validity) thấp; elicited (khơi gợi) = một sự
   thỏa hiệp, độ đồng thuận liên-người-đánh-giá thấp hơn; natural (tự nhiên) = hợp lệ sinh thái nhưng nhiễu, mất cân bằng, và **đặt ra
   "các mối quan ngại về đạo đức và quyền riêng tư"**. Bài review nêu **">60% các kho ngữ liệu speech cảm xúc là
   giả lập (simulated) [ref 47, Schröder 2001]"** (§5.1) — ≈ (một số liệu thứ cấp được trích dẫn lại, không phải số liệu tự đếm của nhóm tác giả).
3. **Danh mục 52 kho ngữ liệu (Table 2)** — các cột: *tên corpus, tài liệu tham khảo/năm, (các) ngôn ngữ, loại
   speech/số người nói, cảm xúc, điều kiện thu âm, phương pháp gán nhãn*. (Lưu ý: **Table 2 KHÔNG có
   cột license, DOI, split, hay số giờ** — xem phần Hạn chế; trục "Physical Existence" chỉ được mô tả bằng văn xuôi chứ chưa bao giờ được đưa vào bảng.)
4. **Một chỉ số chất lượng (quality index)** để đánh trọng số cho các kho ngữ liệu (§7.1, eq. 1) —
   **Q = 0.2615·S + 0.0872·E + 0.6114·C + 0.0400·R** (S = số người nói đã chuẩn hóa, E = số cảm xúc,
   C = số trích dẫn/năm, R = độ mới), trọng số theo AHP (✔, eq. (1), PDF tạp chí). **Số trích dẫn chiếm ưu thế
   (0.61)** và **số người nói đứng thứ hai (0.26)**; số cảm xúc (0.087) và độ mới (0.040) gần như nhiễu (noise).
   Ngoài ra còn có Table 3 (bản đồ sử dụng của 26 bài báo SER đầu năm 2024): IEMOCAP và Chou mỗi cái được trích dẫn 11×,
   DES/TESS/CREMA-D 5×, MSP-Podcast/MELD 2× — các benchmark tiếng Anh dạng diễn (acted) vẫn chiếm ưu thế trong sử dụng thực tế.

**Key facts for our three target decisions (from a full scan of Table 2 + §6.1–6.52):**

- **Ngôn ngữ (V-D, V-H):** Tiếng Anh chiếm ưu thế; tiếp theo là tiếng Đức, Pháp, Ý, Quan Thoại (Mandarin), cộng thêm
  Hindi, Bangla, Ả Rập, Ba Tư, Tây Ban Nha, Ba Lan, Punjabi, Amharic, Hy Lạp, Đan Mạch, Slovenia, và
  đa ngôn ngữ (CREST, INTERFACE). **Tiếng Việt xuất hiện trong 0/52 kho ngữ liệu** (✔, đã đọc toàn bộ Table 2).
- **Kho ngữ liệu ngôn ngữ có thanh điệu (V-D):** **6/52** là ngôn ngữ có thanh điệu — CASIA (Quan Thoại, acted, 4 người nói),
  CHEAVD (tiếng Trung, natural+acted, phim/TV), NNIME (tiếng Trung, acted, 44 người nói), EMOVIE (Quan Thoại,
  acted, 9724 mẫu từ đoạn phim, nhãn cực tính - polarity), MCAESD (Quan Thoại, acted, 6 người nói), và
  **CAVES (tiếng Quảng Đông, elicited, 10 người nói)**. **CAVES là mục duy nhất thậm chí có nhắc tới thanh điệu**: nó được mô tả là
  "*một ngôn ngữ có thanh điệu (với nhiều hơn Quan Thoại hai thanh điệu ngữ âm)*" và 50 câu mang (carrier sentences) CHINT của nó được
  "*chọn sao cho bao phủ tốt các thanh điệu từ vựng khác nhau, cả ở vị trí đầu và cuối câu*" (§6.51) — nhưng đó là việc
  **cân bằng thanh điệu để kiểm soát kích thích (stimulus control)**, không phải một **lớp gán nhãn** thanh điệu và **không** phải một nghiên cứu về tương tác thanh điệu×cảm xúc. **0/52 kho ngữ liệu
  gán nhãn thanh điệu từ vựng hoặc coi thanh điệu là một biến phân tích** (✔). Điều này xác nhận khoảng trống (whitespace) V-D
  từ phía nguồn cung kho ngữ liệu, khớp với phát hiện ở phía mô hình xuyên suốt vn-06…13.
- **Sơ đồ nhãn (V-E):** bài review thiết lập tính lưỡng hệ categorical vs dimensional (§4) nhưng
  **không bao giờ lập bảng thống kê bao nhiêu kho ngữ liệu dùng loại nào** — một khoảng trống bị bỏ ngỏ. Từ việc tự đọc Table 2
  + các mô tả: **phần lớn chỉ dùng categorical** (kiểu Ekman, 5–8 lớp rời rạc);
  **~8/52 có thêm lớp dimensional hoặc liên tục** — VAM (V/A/Dominance, thuần dimensional),
  IEMOCAP (categorical + V/A/D thang 5 điểm), MSP-IMPROV (rời rạc + liên tục-theo-thời-gian), NNIME
  (rời rạc + liên tục-theo-thời-gian), MSP-Podcast (attribute + categorical), Real-Life Call Center (activation-evaluation
  2 chiều), CREMA-D (nhãn + **cường độ (intensity)** giá trị thực), CMU-MOSEI (sentiment thang Likert
  + emotion), SAFE (categorical + intensity/evaluation/reactivity) (≈ — số đếm của tôi từ Table 2, không phải
  con số bài báo tự công bố). **Không có kho ngữ liệu nào trong số ~8 kho song-sơ-đồ này là ngôn ngữ có thanh điệu hay là tiếng Việt;
  cũng không có kho nào mang cờ distress/mức độ nghiêm trọng đi kèm V/A.**
- **Có tồn tại các kho ngữ liệu lấy từ media nhưng không kho nào khớp bộ tiêu chí của chúng ta (V-H):** các kho ngữ liệu nguồn
  phim/TV/online khá phổ biến — CREST (TV/DVD), SAFE (30 phim), ITA-DB (40 phim/series TV, lồng tiếng),
  EMOTV1 (TV Pháp), VAM (talk show TV Đức), CHEAVD (phim/TV), ANAD (TV Ả Rập), MELD (series TV *Friends*),
  CMU-MOSEI (YouTube), EMOVIE (đoạn phim), PEMO (phim Punjabi), ITA-DB-RE
  (phòng xử án). Vậy "cắt clip cảm xúc từ TV/phim" là một phương pháp thu thập đã được nhiều người đi trước —
  **nhưng mọi kho ngữ liệu đó hoặc là phát hành audio (kéo theo vấn đề bản quyền mà chính bài review nêu ra) hoặc là
  bị giới hạn truy cập/không có tài liệu, và không kho nào vừa có thanh điệu + chỉ-phát-hành-feature + CC-BY.**
- **Đoạn văn về đạo đức/pháp lý trực tiếp cho phép mô hình phát hành của chúng ta (V-H):** §5.3 và §7.3.
  §5.3: "*Đối với các kho ngữ liệu bắt nguồn từ media (phim, TV, nền tảng online), nhà nghiên cứu phải giải quyết
  vấn đề bản quyền/quyền liên quan (neighboring rights) và điều khoản dịch vụ; fair use hay fair dealing tùy thuộc
  vào từng quốc gia và hiếm khi cho phép tái phân phối audio thô… nên dùng license dataset rõ ràng và,
  khi cần, các kho lưu trữ truy cập có kiểm soát.*" §7.3 kết bằng câu mang tính hành động:
  "*Khi những điều kiện này không thể đáp ứng được, việc phân phối nên bị giới hạn (ví dụ như truy cập
  tại-chỗ hoặc **chỉ chia sẻ các feature đã được rút trích (derived features)**) hoặc nên tránh hoàn toàn.*" (✔, §5.3/§7.3 PDF tạp chí). Đây là một
  bài khảo sát bình duyệt (peer-reviewed) nêu đích danh **phát hành chỉ-feature** là câu trả lời hợp pháp cho
  speech từ media có bản quyền — chính xác là thiết kế của ViEmoSpeech.

### Parts directly useful for Pebble (tagged by Decision ID)

1. **[V-H] Khung bốn trục (Scope / Physical Existence / Contents / Language
   Composition) làm khung xương cho bảng định vị (positioning table) của chúng ta.** Tái sử dụng chính xác các trục này làm cột cho
   bảng "vị trí của chúng ta" của ViEmoSpeech, nhưng **thêm hai cột mà Table 2 bỏ qua**: `Release form`
   (dạng phát hành — raw-audio vs features-only) và `Source legality` (tính hợp pháp nguồn — tự thu âm / có license CC / found-media
   có bản quyền). Theo khung này, ViEmoSpeech là hàng duy nhất: Scope = **natural /
   found / in-the-wild (phim truyền hình)**; Physical Existence = **CC-BY, chỉ-feature, DOI, các split
   tách biệt theo người nói (speaker-disjoint) với phần holdout toàn bộ series**; Contents = **7-cat + V/A(1–5) + distress, gán nhãn
   thủ công (human-labeled), có lớp thanh điệu âm tiết (syllable-tone)**; Language = **tiếng Việt + phương ngữ Bắc/Trung/Nam**. Bổ sung cho
   bảng định vị THAI-SER đã được dùng cho V-H (vn-11) — bài 16 cung cấp *tên trục đã được công bố chuẩn hóa*; THAI-SER cung cấp
   hàng so sánh kho-ngữ-liệu-có-thanh-điệu.
2. **[V-H] Chỉ số chất lượng Q và các trọng số của nó như một công cụ hiệu chỉnh phạm vi/kỳ vọng.**
   Các hệ số của Q cho thấy lĩnh vực này thưởng cho **số trích dẫn (0.61) và số người nói (0.26)** cao hơn nhiều so với
   độ rộng cảm xúc (0.087) hay độ mới (0.040). Cụ thể: một kho ngữ liệu hoàn toàn mới sẽ có điểm Q gần bằng không
   trong nhiều năm bất kể chất lượng thiết kế (vì C≈0, R nhỏ), và **số người nói** của chúng ta (dàn diễn viên phim, hàng chục chứ không phải hàng trăm) là đòn bẩy nội tại duy nhất ta có thể xoay chuyển. **Đừng** chạy theo Q; hãy dùng nó để đặt ra
   kỳ vọng thực tế cho reviewer và để biện minh cho việc báo cáo các trục chất lượng nội tại của riêng chúng ta
   (gán nhãn thanh điệu, phương ngữ, distress) mà Q không đo được.
3. **[V-H] Điều khoản §5.3/§7.3 "chỉ chia sẻ các feature đã rút trích" như một điểm neo pháp lý-thiết kế có thể trích dẫn.**
   Đây là câu hữu ích nhất trong toàn bài đối với chúng ta: trích dẫn nguyên văn như một minh chứng độc lập, đã qua bình duyệt,
   rằng phát hành chỉ-feature là hướng xử lý *được khuyến nghị* cho SER lấy từ found-media có bản quyền — biến ràng buộc
   pháp lý về media (`docs/intent/constraints.md`) của chúng ta từ một hạn chế thành một sự phù hợp với thực hành tốt nhất đã được công bố.
4. **[V-E] Tính lưỡng hệ categorical-vs-dimensional + con số bị thiếu.** Bài review xác nhận cả hai họ nhãn
   đều phổ biến và rằng **mang cả hai là hiếm (~8/52) và chưa từng kết hợp với cờ distress hay một ngôn ngữ
   có thanh điệu**. Dùng điều này để biện minh cho sơ đồ kép 7-cat + V/A của ViEmoSpeech như một sự trải rộng
   có chủ đích qua cả hai quy ước, và để định vị cờ distress như một trục *thứ ba* mà không kho ngữ liệu nào trong 52 kho
   cung cấp. Cũng lấy cách bài review đặt tên cho phân loại học nguồn-người-gán-nhãn
   (self / observer / expert / crowd) + kỳ vọng về độ tin cậy liên-người-đánh-giá đưa vào các trường spec giao thức
   gán nhãn ADR-002/003 của chúng ta.
5. **[V-D] Phát hiện 0/52 gán nhãn thanh điệu như bằng chứng về tính mới từ phía kho ngữ liệu.** Kết hợp điều này với
   phép tam giác hóa (triangulation) phía mô hình (vn-06/07/13): không *kho ngữ liệu* SER nào gán nhãn thanh điệu từ vựng và không
   *mô hình* SER nào đo cạnh tranh kênh (channel competition) giữa thanh điệu×cảm xúc. CAVES là gần nhất (có thanh điệu, kích
   thích được cân bằng thanh điệu) và là tiền lệ để trích-dẫn-và-phân-biệt — nó *kiểm soát* thanh điệu, còn chúng ta *gán nhãn và đo lường* nó.

### How each part helps Pebble succeed

- **Positioning table (part 1) → the method/corpus paper's Table 1.** Xây một bảng so sánh
  dựa trên bốn trục của bài 16 + hai cột chúng ta thêm vào, điền bằng các kho ngữ liệu đã có tên trong sổ đăng ký
  (ViSEC, VLSP-56h, VNEMOS, THAI-SER, MSP-Podcast, IEMOCAP, CAVES). Các ô trống
  (tiếng Việt ∩ có gán nhãn thanh điệu ∩ chỉ-feature ∩ CC-BY ∩ dimensional+distress) *chính là*
  hình ảnh đóng góp (contribution figure). Artifact: bảng định vị trong bài báo corpus ViEmoSpeech + một stub trong
  `docs/spec/capabilities/`.
  - **Transfer risk:** THẤP — đây là các tên trục đã công bố, có thể tái sử dụng trực tiếp. Rủi ro
    duy nhất là "natural/found" làm phẳng trường hợp con cụ thể của chúng ta (phim truyền hình cắt theo một người nói); hai cột
    chúng ta thêm vào giải quyết được điều đó.
- **Quality index (part 2) → honest scoping in the paper's limitations.** Thêm một câu:
  "theo chỉ số Q bị chi phối bởi số trích dẫn của Serrano et al., bất kỳ kho ngữ liệu mới nào cũng bị định giá thấp
  do bản chất cấu trúc; thay vào đó chúng tôi báo cáo các trục thiết kế nội tại (thanh điệu/phương ngữ/distress) mà
  các trọng số của Q (0.087 cho cảm xúc, 0.040 cho độ mới) không nắm bắt được." Điều này ngăn trước phản đối kiểu
  "dataset mới ít tác động" từ reviewer.
  - **Transfer risk:** TRUNG BÌNH — Q mang tính mô tả cho tập được khảo sát, không phải một benchmark chuẩn tắc; không
    nên tính Q cho ViEmoSpeech rồi so sánh (nó sẽ gây hiểu lầm vì gần bằng không do chưa có trích dẫn).
- **Feature-only clause (part 3) → the Data Availability + Ethics section.** Trích dẫn §5.3/§7.3 trực tiếp
  ở nơi chúng ta mô tả việc phát hành = features+timestamps+labels+speaker-ids. Nó biến ràng buộc cứng của chúng ta
  thành "nhất quán với hướng xử lý phát hành được khuyến nghị bởi bài review SER-corpus gần đây nhất." Artifact: tuyên bố
  Data Availability + tham chiếu chéo tới `docs/intent/constraints.md`.
  - **Transfer risk:** THẤP — điều khoản này không phụ thuộc vào quốc gia (jurisdiction-agnostic) và nêu rõ bao gồm
    "phim, TV, nền tảng online"; nó ánh xạ 1:1 với nguồn phim truyền hình của chúng ta. Lưu ý: đây là hướng dẫn, không phải một
    ý kiến pháp lý — phân tích bản quyền theo luật Việt Nam thực tế của chúng ta vẫn phải đứng độc lập.
- **Label-duality count (part 4) → V-E label-scheme spec.** Biện minh cho sơ đồ kép và trục distress
  độc lập là để lấp khoảng trống "~8/52 mang cả hai, 0/52 mang cờ distress trên một ngôn ngữ có thanh điệu";
  đưa các trường self/observer/expert/crowd + IRR vào spec của công cụ gán nhãn
  (`tools/labeler/SPEC.md`) để metadata gán nhãn của chúng ta có thể so sánh với các kho ngữ liệu được khảo sát.
  - **Transfer risk:** TRUNG BÌNH — con số "~8/52" là của tôi tự đếm, không phải con số bài báo công bố (≈); nếu
    trích dẫn như một con số, chúng ta phải tự đếm lại và tự chịu trách nhiệm, không được gán con số này cho Serrano et al.
- **Tone-annotation gap (part 5) → V-D novelty defense + the tone×emotion figure.** Dùng bài 16
  làm nửa phía-nguồn-cung-corpus của luận điểm về tính mới hai mặt; CAVES trở thành một dòng trích-dẫn-và-phân-biệt
  ("cân bằng thanh điệu để kiểm soát, không phải để gán nhãn") trong phần related-work của bài báo phương pháp.
  - **Transfer risk:** THẤP — kết quả đọc 0/52 lấy trực tiếp từ Table 2 + §6.51; CAVES rõ ràng không mơ hồ,
    chỉ mang tính kiểm soát. Rủi ro còn lại: một kho ngữ liệu có thanh điệu công bố *sau* giữa năm 2025 có thể gán nhãn thanh điệu;
    cần kiểm tra lại vào thời điểm nộp bài.

### Child mental-health lens (found-TV / tonal / feature-only transfer for ViEmoSpeech)

- **How many boxes are simultaneously unchecked in the 52?** ViEmoSpeech đòi hỏi giao của:
  **tiếng Việt (0/52), có gán nhãn thanh điệu từ vựng (0/52), đo được tone×emotion (0/52),
  nguồn phim-truyền-hình-có-bản-quyền dạng found (có tồn tại nhưng ~12/52 và luôn phát hành audio/bị giới hạn),
  phát hành chỉ-feature CC-BY (0/52 trong Table 2 — không kho ngữ liệu nào trong danh mục được ghi nhận là
  phát hành chỉ-feature), nhãn dimensional + categorical + distress (0/52 kết hợp cả ba).**
  Mỗi ô trong số này *xét riêng lẻ* đều chưa có hoặc hiếm, và **giao của chúng là tập rỗng** —
  chính danh mục của bài review là bằng chứng mạnh nhất rằng ViEmoSpeech chiếm giữ một khoảng trống thực sự.
- **Children specifically:** bài review nêu (qua Matveev et al. [17], §3) rằng "*các mô hình cảm xúc
  [nên] được tùy biến cho từng nhóm nhân khẩu học cụ thể, chẳng hạn như trẻ em, vì kiểu speech của các em khác
  với người lớn*", tuy nhiên **chỉ có 1/52 kho ngữ liệu liên quan tới trẻ em — AIBO** (trẻ em Đức/Anh × robot Sony AIBO,
  speech khơi gợi qua tương tác người-robot), và nó không có thanh điệu, không phải tiếng Việt,
  không có nhãn dimensional, cũng không hướng tới sức khỏe tâm thần. SER cho register trẻ em gần như vắng bóng khỏi
  toàn bộ bối cảnh kho ngữ liệu đã công bố. (Lưu ý: nguồn của chính ViEmoSpeech = diễn viên phim truyền hình *người lớn*,
  nên bài 16 không loại bỏ được rủi ro chuyển giao register-trẻ-em của chúng ta — nó chỉ cho thấy toàn bộ lĩnh vực đều chia sẻ rủi ro này.)
- **Ethics the review foregrounds and we must honor:** §5.3 nêu rõ **"các biện pháp bảo vệ
  bổ sung cho các nhóm dân số dễ tổn thương như trẻ em hoặc bệnh nhân,"** giảm thiểu dữ liệu (data minimization), ẩn danh hóa
  (de-identification), và — đối với found media — xử lý bản quyền/ToS bằng truy cập có kiểm soát hoặc phát hành
  chỉ-feature. Đây là sự hỗ trợ độc lập từ bên ngoài cho bất biến (invariant) pháp lý về media của chúng ta và cho cách
  chúng ta khung hóa distress-như-proxy-diễn: bài review coi cảm xúc tự nhiên/found là mang tính đạo đức nặng nề và
  khuyến nghị đúng kỷ luật phát hành mà chúng ta đang áp dụng.
- **Distress transfer risk:** điểm chạm lâm sàng duy nhất của bài review là một nghiên cứu được trích dẫn
  về phát hiện trầm cảm qua giọng nói (Hansen et al. [9], §1), chỉ được mô tả là "chẩn đoán sớm." Không kho ngữ liệu nào
  trong số 52 kho mang nhãn distress/mức độ nghiêm trọng lâm sàng. Vậy bài 16 **không** cung cấp tiền lệ nhãn-distress
  nào để chuyển giao — nó *xác nhận* rằng head distress của chúng ta chưa có tiền lệ ở cấp độ kho ngữ liệu và củng cố
  cách khung hóa proxy-trung-thực V-F (distress trong phim diễn ≠ lâm sàng, chỉ dùng để sàng lọc recall).

### Limitations & open questions for Pebble

- **Contradiction / gap #1 (vs the paper's own framework):** bài 16 nêu tên **"Physical Existence
  (quyền truy cập và giấy phép… DOI… các split train/val/test)"** như một trong bốn trục chịu lực của mình,
  nhưng **Table 2 lại không lập bảng cho bất kỳ trục nào trong số đó** — không có cột license, không DOI, không split, không số giờ.
  Bản thân bài báo không thể trả lời "trong 52 kho này, tôi có thể tái sử dụng hợp pháp kho nào và license ra sao?"
  từ chính bảng của nó. Đây chính xác là trục mà ViEmoSpeech được xây dựng xoay quanh, nên bảng định vị của chúng ta
  **phải thêm hai cột `Release form` + `Source legality` mà bài 16 bỏ qua** — và chúng ta có thể trích dẫn sự thiếu sót
  này như một khoảng trống cụ thể mà tài liệu corpus của chúng ta lấp đầy.
- **Contradiction / gap #2 (vs THAI-SER, vn-11, on the naturalness bet):** THAI-SER
  bằng thực nghiệm phát hiện **scripted (có kịch bản) > improvised (ứng khẩu)** (WA 73.99 so với 61.80), đi ngược lại
  luận điểm "speech tự nhiên thì tốt hơn." Bài review 16 lại nghiêng về hướng *ngược lại* trên phương diện lập luận —
  nó nhiều lần khung hóa speech tự nhiên/found là có tính hợp lệ sinh thái cao hơn và "hướng đi của lĩnh vực," trong khi
  thừa nhận rằng các kho ngữ liệu tự nhiên cho **độ đồng thuận liên-người-đánh-giá thấp hơn** và gán nhãn khó hơn (Table 1, §5.4).
  Cả hai điều này không thể đúng một cách vô điều kiện cho chúng ta: phim truyền hình found vừa cho tính hợp lệ sinh thái
  **vừa** cho khó khăn trong gán nhãn. ViEmoSpeech phải *đo lường* xem register phim-found của nó có thực sự vượt qua
  baseline diễn (acted) hay không (V-G), chứ không mặc định theo câu chuyện tính-hợp-lệ-sinh-thái của bài review.
- **Gap #3 (V-E, unquantified):** bài review bàn luận khá dài về categorical vs
  dimensional nhưng **không bao giờ báo cáo con số phân chia**, nên "~8/52 mang cả hai" của chúng ta là số đếm tự làm,
  không phải một con số có thể trích dẫn (gắn thẻ ≈). Nếu cần một con số có thể trích dẫn, chúng ta phải tự đếm trong
  bài báo của mình và có thể ghi chú rằng bài 16 đã bỏ ngỏ việc định lượng này.
- **The Q-index is adoption-biased, not quality-biased:** với C (trích dẫn/năm) có trọng số 0.61,
  Q đo *vị thế sẵn có (incumbency)*, không đo chất lượng thiết kế kho ngữ liệu — về mặt cấu trúc nó trừng phạt chính xác
  những kho ngữ liệu mới, thuộc ngôn ngữ ít được đại diện mà bài review cho rằng lĩnh vực đang cần. Không nên dùng Q để
  lập luận cho giá trị của ViEmoSpeech; chỉ dùng nó để giải thích tại sao thay vào đó cần một lập luận về chất lượng thiết kế.
- **Open question — no modeling guidance:** bài 16 là một bài review về *dataset*; nó không đóng góp gì
  cho kiến trúc fusion (V-A), backbone audio (V-B), hay độ bền vững trước nhiễu ASR (V-C). Với các trục này, bài 16 im lặng
  và bản tổng hợp về sự phụ thuộc-register từ các bài báo bimodal vẫn không bị ảnh hưởng.
- **Open question worth one check:** một số kho ngữ liệu found-media trong Table 2 (CHEAVD, ANAD, MELD,
  CMU-MOSEI) có nguồn TV/online nhưng dường như vẫn phân phối audio — đáng để xác nhận xem có kho nào công bố
  một biến thể *chỉ-feature* mà chúng ta có thể trích dẫn như một tiền lệ trực tiếp hay không, vì việc Table 2 thiếu cột
  release-form đã che giấu điều này.
