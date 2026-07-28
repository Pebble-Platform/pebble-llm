# Paper vn-12 — Evaluating Emotion Recognition in Spoken Language Models on Emotionally Incongruent Speech

> Bản dịch tiếng Việt của [12-emotionally-incongruent-slm.md](12-emotionally-incongruent-slm.md) — cập nhật 2026-07-10.

- **Authors:** (not yet extracted — verify from PDF)
- **Venue / year:** arXiv preprint, Oct 2025
- **Links:** abs https://arxiv.org/abs/2510.25054 · PDF `pdfs/12-emotionally-incongruent-slm.pdf`
- **Group:** vietnamese-ser / contrastive citation (semantics dominate)

**Tóm tắt:** Kiểm tra các SLM (SALMONN, DeSTA2, Qwen2-Audio, Audio Flamingo-3)
trên ngữ liệu giọng nói tổng hợp có cảm xúc không tương hợp (emotionally-incongruent);
các SLM dựa gần như hoàn toàn vào ngữ nghĩa văn bản (độ chính xác 80–100%) và gần
như ngẫu nhiên (~25%) đối với cảm xúc chỉ dựa trên âm học, trong khi một baseline SER
chuyên biệt xử lý các tín hiệu âm học tốt hơn nhiều.

**Mức liên quan với ViEmoSpeech:** Trích dẫn đối chứng — hiện tượng "ngữ nghĩa có thể
lấn át" đã xảy ra trong các SLM nhưng như một *artifact do thiên lệch mô hình*; luận
điểm của chúng ta là một *nguyên nhân ngữ âm mang tính nguyên lý* (F0/cách phát âm bị
khóa theo thanh điệu). Cũng cung cấp thông tin cho V-A/V-C (rủi ro nhánh văn bản lấn
át) và thiết kế đánh giá cho các trường hợp xung đột.

> Stub created 2026-07-10 (task `docs/tasks/paper-deep-analysis.md`); deep-read pending.

## Deep research — full-PDF read (2026-07-10)

### Source-access note

File PDF cục bộ `pdfs/12-emotionally-incongruent-slm.pdf` đã được trích xuất toàn bộ bằng `pdftotext`
(phần tóm tắt, §§1–5, Bảng 1, chú thích Hình 1–2, lời cảm ơn, tuyên bố đạo đức, tài liệu tham khảo).
Đây là một **bản preprint trên arXiv** (arXiv:2510.25054v2 [cs.CL], 30 Oct 2025), định dạng hai cột
kiểu ICASSP ("Index Terms"), nhiều khả năng đã nộp cho ICASSP 2026 — không tìm thấy phiên bản đã
xuất bản chính thức, nên bản preprint này là bản có giá trị tham chiếu và không tồn tại chênh lệch
preprint-so-với-bản-xuất-bản.

**Danh sách tác giả đầy đủ (stub trước đó thiếu):** Pedro Corrêa, João Lima, Victor Moreno, Lucas Ueda,
Paula Dornhofer Paro Costa — School of Electrical and Computer Engineering, Universidade Estadual de
Campinas (UNICAMP), Campinas, Brazil; liên kết với Recod.ai Artificial Intelligence Lab.
Được tài trợ bởi CAPES, FAPESP (#2020/09838-0 BI0S, #2023/12865-8 Horus), PPI-SOFTEX. Đánh giá trên
người tham gia được UNICAMP CEP phê duyệt, CAAE 59536022.8.0000.5404.

Xác minh trên web các con số mang tính căn cứ (load-bearing):
- Truy vấn `Evaluating Emotion Recognition Spoken Language Models Emotionally Incongruent Speech EMIS UNICAMP Correa`
  → tìm ra abstract/HTML trên arXiv (`https://arxiv.org/abs/2510.25054`, `https://arxiv.org/html/2510.25054v1`).
  Đã xác nhận các tác giả bao gồm tên đầy đủ "Paula Dornhofer Paro Costa", bộ dữ liệu EMIS, luận điểm
  "semantics dominate" [✔].
- Truy vấn `EMIS ... SALMONN DeSTA2 Qwen2-Audio Cramer's V 0.65 proxy` + `WebFetch` trang
  `arxiv.org/html/2510.25054v1`
  → đã xác nhận **toàn bộ các ô của Bảng 1** (SLM target ≈25–41%, proxy 66–100%; Baseline SER target
  46–52.5%), **Cramér's V = 0.08 (target) / 0.65 (proxy)**, **nhận thức của con người 39.4/58.1/62.0% +
  70.8% GT**, **EMIS = 1248 mẫu**, chi-square N = 4,978 [✔]. Các con số trong HTML v1 giống hệt PDF v2
  cục bộ.

### Bài báo thực sự làm gì

**Câu hỏi.** Các mô hình ngôn ngữ giọng nói (SLM) hợp nhất một bộ mã hóa giọng nói với một LLM đã
được tiền huấn luyện có thực sự tích hợp âm học hay không, hay chúng sụp đổ về kênh văn
bản/ngữ nghĩa? Nhận dạng cảm xúc được dùng làm phép thử vì kênh ngữ nghĩa và kênh ngôn điệu
(prosody) có thể được cố ý đặt vào thế xung đột.

**Xây dựng kích thích (bộ dữ liệu EMIS).** [§3.1, ✔]
- GPT-4.5 tạo ra **104 câu tiếng Anh giàu cảm xúc** trên 4 loại cảm xúc (angry/happy/neutral/sad),
  mỗi câu được chia thành **explicit** (chứa từ chỉ cảm xúc, ví dụ "I'm so happy we finally adopted a
  puppy!") và **implicit** (cảm xúc chỉ được suy ra từ ngữ cảnh, ví dụ "I can't stop smiling after our
  date last night"). Neutral không có phân chia explicit/implicit (được phân tích riêng).
- **Ba hệ thống TTS biểu cảm (expressive TTS) zero-shot SoTA** — CosyVoice2, StyleTTS2, F5-TTS — tổng
  hợp mỗi câu ở **cả 4 cảm xúc âm học**, với tính biểu cảm được điều kiện hóa dựa trên các bản ghi tham
  chiếu từ cơ sở dữ liệu giọng nói cảm xúc **ESD** (10 người nói tiếng Anh, 350 câu/cảm xúc; các tham
  chiếu = 7 câu dài nhất được ghép nối lại thành ~32.2±3.5 giây). Mỗi hệ thống TTS tạo ra 416 mẫu
  (104×4) → **EMIS = tổng cộng 1248 mẫu**.
- Với mỗi câu gốc, cách làm này cho ra **1 mẫu tương hợp (congruent) + 3 mẫu không tương hợp
  (incongruent)**. Ở điều kiện không tương hợp, **cảm xúc âm học là nhãn mục tiêu (target)**; **cảm
  xúc theo nội dung ngữ nghĩa là nhãn "proxy"**. Mức độ dựa vào từng phương thức (modality reliance)
  được đọc trực tiếp: độ chính xác *proxy* cao = thiên về văn bản; độ chính xác *target* cao = có chú
  ý tới ngôn điệu.

**Kiểm định kích thích (hai kiểm tra độc lập).** [§3.3, §4, ✔]
- Một **baseline SER âm học được tinh chỉnh** (dựa trên emotion2vec, ref [9], được fine-tune trên một
  tập con của ESD) xác nhận rằng âm học của TTS mang đúng cảm xúc dự định — nó đạt **target
  46–52.5% / proxy ≈1–33%**, tức là nó bám theo nhãn âm học, đúng như hành vi mong muốn.
- **Đánh giá cảm nhận của con người**, 40 người tham gia trên một tập con cân bằng: khả năng nhận
  diện cảm xúc *âm học* = **39.4% StyleTTS2, 58.1% CosyVoice2, 62.0% F5-TTS, 70.8% ground-truth ESD**
  [✔]. Lưu ý rằng con số này chỉ cao hơn mức ngẫu nhiên (25%) một chút đối với StyleTTS2 — sự không
  tương hợp tổng hợp được hiện thực hóa chưa hoàn hảo (đây là một giới hạn thực sự đối với luận điểm
  "SLM ngẫu nhiên trên âm học"; xem phần Limitations).

**Đánh giá SLM.** [§3.2] Bốn SLM — **SALMONN, DeSTA2, Qwen2-Audio, Audio Flamingo-3** — được nhận
một **chỉ dẫn cố định duy nhất, yêu cầu tường minh mô hình bỏ qua nghĩa của từ**: *"Using tone
of voice only (prosody: pitch, rhythm, loudness, timbre). Ignore word meaning; do not transcribe. Reply
with exactly one: angry — happy — sad — neutral."* (dịch nghĩa: "Chỉ dùng ngữ điệu giọng nói (ngôn
điệu: cao độ, nhịp điệu, độ to, âm sắc). Bỏ qua nghĩa của từ; không phiên âm. Trả lời đúng một trong
các từ: angry — happy — sad — neutral.") Sử dụng siêu tham số giải mã mặc định. Kiểm định chi-square
về tính độc lập trên N=4,978 dự đoán (≈4 mô hình × 1248, trừ đi các trường hợp phân tích lỗi — một
điểm chưa nhất quán nội bộ nhỏ, ≈; 4×1248=4992), 9 bậc tự do, cùng độ lớn hiệu ứng Cramér's V.

**Kết quả chính (Bảng 1 / Hình 2 / §4, tất cả đều ✔ được xác nhận chéo):**
- **Độ chính xác SLM target (âm học) ≈ mức ngẫu nhiên (25% cho bài toán 4 lớp) ở mọi nơi:** DeSTA2
  25.6–38.4%, Audio Flamingo-3 25.0–41.3%, Qwen2-Audio 21.1–30.1%, SALMONN 25.6–36.5%.
- **Độ chính xác SLM proxy (ngữ nghĩa) cao mỗi khi văn bản mang cảm xúc:** ở điều kiện **explicit**,
  DeSTA2/Qwen2-Audio đạt **95.5–100%**, Audio Flamingo-3 lên tới **100.0%** (mang tính hệ thống — luôn
  dự đoán proxy trên StyleTTS2), SALMONN 80.2–89.6%. Implicit thấp hơn (66–92%). **Neutral** làm sụp
  đổ độ chính xác proxy ở các mô hình nhạy với sắc thái tình cảm của văn bản (DeSTA2 7.6–10.5%,
  Qwen2-Audio 6.7–11.5%) nhưng vẫn cao ở SALMONN/Flamingo-3 (71–92%).
- **Baseline SER là hình ảnh đối xứng ngược lại:** target 46–52.5% (cao hơn hẳn mức ngẫu nhiên), proxy
  ≈1–33% — thực sự mang tính âm học.
- **Độ lớn hiệu ứng:** predicted-so-với-target **Cramér's V = 0.08** (không đáng kể); predicted-so-với-
  proxy **V = 0.65** (lớn). p<0.01 cho cả hai mối liên hệ nhưng khoảng cách về độ lớn hiệu ứng mới là
  điểm nhấn chính [§4, ✔].
- **Hình 2:** ở điều kiện **congruent**, dự đoán của SLM bám khá tốt theo cảm xúc (được truyền tải
  đồng thời bởi cả hai kênh) (đường chéo ≈53–97%); ở điều kiện **incongruent**, đường chéo sụp đổ và
  dự đoán lệch về phía **angry/happy trong khi bỏ qua sad** — một sự tương tác giữa thiên kiến cảm
  tính văn bản của LLM backbone và việc angry/happy có tính nổi bật về ngôn điệu cao hơn sad/neutral.

**Cách họ giải thích *lý do* SLM sụp đổ về văn bản.** [§4–§5] Thiên kiến biểu diễn văn bản của LLM
backbone lấn át biểu diễn hợp nhất; cảm xúc ngữ nghĩa càng "dễ tiếp cận" (explicit > implicit >
neutral), mô hình càng dựa vào nó — ngay cả dưới một prompt tường minh cấm dùng nghĩa của từ. Họ
xem đây là một **thiên lệch mô hình/kiến trúc** ("các biểu diễn liên quan đến văn bản phần lớn lấn át
các biểu diễn âm học"), chứ không phải là một đặc tính ngữ âm của bất kỳ ngôn ngữ nào, và cảnh báo
rằng các benchmark chỉ dùng dữ liệu tương hợp che giấu khiếm khuyết này.

### Những phần trực tiếp hữu ích cho ViEmoSpeech

1. **Giao thức độ chính xác target/proxy + Cramér's V như một chỉ số đo mức độ dựa vào phương thức
   [V-D, V-G, ✔].** Với mỗi mẫu xung đột, chấm dự đoán theo *hai* nhãn (target âm học và proxy văn
   bản) và báo cáo một Cramér's V cho mỗi nhãn; khoảng cách (0.08 so với 0.65 trong bài này) định
   lượng mức độ lấn át của văn bản bằng một cặp số duy nhất, dễ trích dẫn. Đây là một công cụ có sẵn
   để **định lượng sự cạnh tranh giữa kênh thanh điệu×cảm xúc** — áp dụng lên nhãn target âm học của
   chúng ta và nhãn proxy sắc thái tình cảm từ văn bản/ASR trên một tập con xung đột.
2. **Thiết kế bộ kiểm tra không tương hợp như một mẫu (template) cho slice xung đột [V-G].** Một mẫu
   tương hợp + ba mẫu không tương hợp cho mỗi câu gốc; cảm xúc âm học = target, cảm xúc ngữ nghĩa =
   proxy; các tầng tín hiệu văn bản explicit/implicit/neutral; kiểm định kích thích bằng (a) một
   baseline SER âm học và (b) cảm nhận của con người *trước khi* tin tưởng chúng. Đây là bản thiết kế
   sạch nhất từng được công bố cho slice xung đột của chúng ta.
3. **Cảnh báo thực nghiệm rằng một nhánh văn bản mạnh làm sụp đổ mô hình hợp nhất về phía văn bản
   [V-C].** Độ chính xác target của SLM ở mức ngẫu nhiên trong khi proxy đạt 80–100% mỗi khi văn bản
   mang cảm xúc — bằng chứng trực tiếp rằng một phép hợp nhất được học có chứa một bộ mã hóa văn bản
   mạnh sẽ chú ý quá mức vào kênh ngữ nghĩa trừ khi bị buộc không làm vậy. Đây là căn cứ cho các quyết
   định về chính quy hóa hợp nhất (fusion-regularization) và bảo đảm nhánh âm học không bị "bỏ đói"
   của chúng ta.
4. **Sự phân biệt đối chứng tường minh cho phần bảo vệ tính mới của chúng ta [V-D].** Sự lấn át của họ
   là một *artifact do thiên lệch mô hình* (thiên kiến LLM thắng bộ mã hóa giọng nói, trên **tiếng Anh
   phi thanh điệu**, dưới điều kiện không tương hợp tổng hợp bằng TTS). Luận điểm của chúng ta là một
   *nguyên nhân ngữ âm ở cấp độ tín hiệu* — thanh điệu từ vựng tiếng Việt khóa F0/cách phát âm, chính
   là kênh mà cảm xúc sử dụng, nên nhánh văn bản buộc phải gánh tải vì một lý do *ngữ âm* nội tại của
   ngôn ngữ, chứ không phải vì một LLM lớn lấn át một bộ mã hóa yếu. Câu trích dẫn-và-phân biệt giờ đã
   có thể chốt lại nguyên văn.
5. **Phát hiện về điều kiện neutral [V-C, V-D].** Khi văn bản trung tính về cảm xúc, độ chính xác
   target của một số SLM *tăng lên* (DeSTA2/Flamingo-3 lên 37–41%) — bằng chứng cho thấy sự lấn át của
   văn bản là **có điều kiện, phụ thuộc vào việc văn bản có mang tín hiệu hay không**. Điều này liên
   quan trực tiếp đến bối cảnh của chúng ta: văn bản ASR của phim truyền hình tự phát thường có tín
   hiệu cảm xúc thấp, điều này sẽ *làm giảm* sự lấn át của văn bản — nhưng các lỗi hoán đổi thanh điệu
   của ASR có thể tiêm vào tín hiệu văn bản *giả* đúng vào lúc mức độ kích động (arousal) cao (xem
   phần lăng kính bên dưới).

### Từng phần giúp ViEmoSpeech thành công như thế nào

- **V-D (luận điểm tone×emotion có thể đo lường).** Áp dụng công cụ target/proxy + Cramér's V làm
  *định dạng báo cáo* cho biểu đồ cạnh tranh kênh của chúng ta: trên slice xung đột, báo cáo V(pred,
  audio-emotion) so với V(pred, text-sentiment) của mô hình hợp nhất của chúng ta. Nếu mô hình của
  chúng ta — không giống các SLM này — cho thấy một V không đáng bỏ qua so với nhãn âm học trên các
  trường hợp xung đột tiếng Việt có thanh điệu, đó chính là kết quả tích cực mà bài báo phương pháp
  cần. Kết hợp nó với phép dò theo từng lớp (layer-wise probing) kiểu Shen (vn-06) để lý giải cơ chế,
  còn chỉ số này để nắm bắt kết quả hành vi.
- **V-D (bảo vệ tính mới).** Một câu trong phần Related Work: "Các công trình trước đây cho thấy SLM
  mặc định về phía ngữ nghĩa khi có sự không tương hợp (Corrêa et al. 2025), nhưng quy nguyên nhân này
  cho một *thiên lệch biểu diễn* của LLM backbone trong giọng nói tổng hợp tiếng Anh phi thanh điệu;
  chúng tôi thay vào đó xác định một *cơ chế ngữ âm* — sự cạnh tranh F0/cách phát âm do thanh điệu từ
  vựng — đặc thù cho SER ở ngôn ngữ có thanh điệu." Phân biệt rõ ràng mà không nhượng bộ điểm mấu chốt
  của chúng ta.
- **V-C (nhánh văn bản dưới nhiễu ASR).** Đưa một **slice xung đột vào cả huấn luyện, không chỉ đánh
  giá**, và thêm một cơ chế bảo vệ neo vào âm học (audio-anchoring safeguard) để phép hợp nhất không
  thể sụp đổ về PhoBERT: các phương án ứng viên — một lịch trình modality-dropout trên nhánh văn bản,
  một đầu ra (head) chỉ dùng âm học phụ trợ, hoặc một bộ chính quy hóa attention hợp nhất. Tiêu chí
  thành công: trên slice xung đột, độ chính xác target âm học phải giữ ở mức cao hơn hẳn ngẫu nhiên
  (các SLM của họ đã thất bại ở điều kiện này với V=0.08). Trích dẫn bài báo này làm căn cứ thực
  nghiệm cho việc cơ chế bảo vệ này là cần thiết.
- **V-G (giao thức đánh giá).** Thêm một **dòng chỉ số cho slice xung đột** vào bảng đánh giá bên
  cạnh các con số speaker-disjoint / whole-series-holdout: báo cáo macro-F1 riêng biệt trên congruent
  so với conflict, cùng hai giá trị Cramér's V, phản ánh theo cấu trúc Bảng 1 của họ. Kiểm định slice
  xung đột bằng độ đồng thuận hai giáo viên (dual-teacher agreement) cùng gold từ con người của chúng
  ta (tương đương với kiểm tra baseline-SER + nhận thức con người của họ).
- **Kỷ luật về tính hợp lệ của kích thích (stimulus-validity).** Nhận thức của con người trong bài
  báo của họ chỉ đạt 39.4% trên StyleTTS2 — một bài học để *gate* slice xung đột của chúng ta trên
  khả năng nhận diện được của con người trước khi báo cáo các con số của mô hình, để chúng ta không
  quy sự thất bại của mô hình cho việc lấn át bởi văn bản trong khi cảm xúc âm học chưa từng nghe
  được rõ ràng ngay cả đối với con người.

### Lăng kính trẻ em / phim truyền hình Việt Nam / sức khỏe tâm thần (khả năng chuyển giao, rủi ro, biện pháp giảm thiểu)

- **Khả năng chuyển giao của phát hiện là THẤP; khả năng chuyển giao của phương pháp và sự phân biệt
  là CAO.** Kết quả (SLM ngẫu nhiên trên âm học) được đo trên kích thích **tiếng Anh phi thanh điệu,
  tổng hợp bằng TTS, tham chiếu chéo giọng nói (cross-speaker-reference)**, được đánh giá trên **các
  SLM backbone LLM tiếng Anh khổng lồ** — không cái nào trong số này khớp với ViEmoSpeech (tiếng Việt
  có thanh điệu, giọng nói phim truyền hình thực, một phép hợp nhất WavLM+PhoBERT nhỏ, tùy biến riêng).
  Vì vậy *độ lớn* của sự lấn át văn bản sẽ không chuyển giao được. Cái chuyển giao được là (a) **công
  cụ target/proxy Cramér's V** [V-D/V-G] và (b) **cảnh báo về hướng rủi ro** [V-C].
- **Cơ chế của họ mang tính đặc thù theo prompt — mô hình của chúng ta không thể "không tuân theo"
  một prompt.** Các SLM của họ sụp đổ về văn bản *bất chấp một chỉ dẫn bảo bỏ qua nghĩa của từ*; sự
  thất bại một phần là do không tuân theo chỉ dẫn (instruction-following), không phải thuần túy do
  biểu diễn. Một phép hợp nhất được huấn luyện đồng thời (jointly-trained), không có giao diện chỉ
  dẫn bằng ngôn ngữ tự nhiên **không thể biểu hiện đúng kiểu thất bại này** — điều này vừa làm suy
  yếu việc chuyển giao ngây thơ luận điểm chính của họ, vừa nghĩa là rủi ro lấn át văn bản của chúng
  ta, nếu xuất hiện, sẽ là một sự mất cân bằng attention thực sự được học, dễ quy trách nhiệm rõ ràng.
- **Yếu tố khuếch đại đặc thù tiếng Việt mà họ chưa từng thấy: tín hiệu văn bản giả từ ASR ở mức kích
  động cao.** Trong pipeline của chúng ta, PhoWhisper mắc **lỗi hoán đổi thanh điệu chính xác ở mức
  kích động cao** (mày→máy, tao→tháo). Văn bản tiếng Anh của họ thì hoặc sạch (do GPT tạo ra) hoặc
  không tồn tại; văn bản của chúng ta thì *bị hỏng chính xác vào lúc âm thanh quan trọng nhất*. Một
  phép hợp nhất thiên về văn bản do đó sẽ bị dẫn dắt sai bởi tín hiệu từ vựng ảo giác (hallucinated)
  đúng vào những thời điểm có mức cược cao nhất (kích động cao / distress) — một phiên bản gay gắt hơn
  của rủi ro của họ, với hàm ý trực tiếp cho **V-F (sàn thu hồi distress)**. Biện pháp giảm thiểu:
  slice xung đột phải bao gồm các trường hợp lỗi ASR ở mức kích động cao, và đầu ra distress phải có
  khả năng kích hoạt chỉ từ nhánh âm học một mình.
- **Đạo đức / cách đóng khung.** EMIS của họ hoàn toàn là TTS tổng hợp tiếng Anh — không có dữ liệu
  con người thực ngoài phần kiểm định với 40 người nghe (được UNICAMP CEP phê duyệt). ViEmoSpeech
  không thể tổng hợp (dữ liệu được gán nhãn bởi con người trên phim thực dưới giấy phép CC-BY, media
  không bao giờ được công bố); slice xung đột của chúng ta **xuất hiện tự nhiên, hiếm hơn, và không
  cân bằng**, nên nó cần việc con người xác định các trường hợp xung đột thay vì tạo sinh có kiểm
  soát — một chi phí thiết kế cần được dự trù, không phải một đường tắt chúng ta có thể mượn.

### Hạn chế & câu hỏi mở cho ViEmoSpeech

- **Mâu thuẫn #1 (BẮT BUỘC — so với vn-08 Bảng V).** vn-08 (HGR VN-SER, arXiv:2604.01711) báo cáo một
  **nhánh chỉ-văn-bản chỉ đạt 38.70–44.11%** trên SER tiếng Việt 3 lớp — văn bản "gần như vô dụng" —
  trong khi bài báo này báo cáo độ chính xác SLM **proxy (ngữ nghĩa) là 80–100%** — "ngữ nghĩa lấn
  át." **Hòa giải:** hai kết quả đo lường những thứ khác nhau trên những đầu vào khác nhau. (i) *Tín
  hiệu văn bản khác nhau:* văn bản của vn-12 do GPT tạo ra, cố ý chứa cảm xúc bằng tiếng Anh (các nhãn
  tường minh như "I'm so happy"); văn bản của vn-08 là ASR PhoWhisper của hội thoại tiếng Việt tự
  phát với rất ít từ vựng cảm xúc tường minh — một bản ghi thực sự có tín hiệu thấp, nhiễu. (ii)
  *Đại lượng khác nhau:* "độ chính xác proxy" của vn-12 đo mức độ một mô hình *dựa vào* bất kỳ cảm xúc
  nào mà văn bản mang theo; "độ chính xác chỉ-văn-bản" của vn-08 đo lượng cảm xúc mà văn bản *mang
  theo* ngay từ đầu. (iii) *Mô hình khác nhau:* các SLM backbone LLM tiếng Anh khổng lồ so với một
  đường dẫn Whisper→LLM chưa được tinh chỉnh (un-tuned). **Cả hai đều là những sự diễn giải quá mức
  của các baseline yếu** (nhánh văn bản của vn-08 chưa được fine-tune; các SLM của vn-12 đánh giá thấp
  ngôn điệu theo kiến trúc). Đối với ViEmoSpeech, sự tổng hợp là chính xác: *văn bản mang rất ít cảm
  xúc trong phim truyền hình tiếng Việt tự phát (theo vn-08), nhưng một bộ mã hóa văn bản mạnh vẫn sẽ
  chú ý quá mức vào bất kỳ tín hiệu từ vựng yếu/giả nào tồn tại (theo vn-12)* — nên nhánh văn bản của
  chúng ta phải vừa được fine-tune (để trích xuất chút ít tín hiệu thực), vừa được chính quy hóa/neo
  giữ (để không sụp đổ vào các ảo giác của ASR). Luận điểm tone×emotion có thể đo lường vẫn còn bỏ
  ngỏ — không bài báo nào tách rời được kênh ngữ âm.
- **Khoảng trống #2 (tính hợp lệ của kích thích giới hạn luận điểm "ngẫu nhiên trên âm học").** Người
  nghe nhận diện đúng cảm xúc âm học chỉ **39.4% (StyleTTS2) / 58.1% / 62.0%** số lần (§4, ✔) — với
  StyleTTS2 chỉ nhỉnh hơn mức ngẫu nhiên 25% một chút. Nếu con người không thể nghe ra cảm xúc dự
  định, thì một SLM đạt ≈25% không nhất thiết là "đang bỏ qua âm học" — có thể âm học đó vốn không hề
  tồn tại. Luận điểm chính của bài báo hơi diễn giải quá mức sự không tương hợp tổng hợp được hiện
  thực hóa chưa hoàn hảo. ViEmoSpeech nên gate slice xung đột của mình trên khả năng nhận diện được
  của con người để tránh rơi vào cùng cái bẫy này.
- **Khoảng trống #3 (cơ chế không chuyển giao sang phép hợp nhất được huấn luyện đồng thời).** Sự lấn
  át của họ được chứng minh trên các SLM **được prompt**, được bảo bỏ qua văn bản nhưng không tuân
  theo. Một phép hợp nhất audio+PhoBERT được huấn luyện đồng thời không có chỉ dẫn nào như vậy để
  không tuân theo, nên bài báo này là **động cơ thúc đẩy, không phải một dự đoán**, cho kiến trúc của
  chúng ta — chúng ta phải tự đo Cramér's V của mô hình mình chứ không được giả định kết quả của SLM
  áp dụng luôn cho mình.
- **Câu hỏi mở.** EMIS và code đã được công bố; đáng để lấy trực tiếp **script chấm điểm target/proxy
  và bộ công cụ chi-square/Cramér's V** của họ để chuẩn hóa việc báo cáo slice xung đột của chúng ta
  (Github của họ được trích dẫn nhưng URL không có trong văn bản đã trích xuất — cần giải quyết từ
  trang abstract trên arXiv). Cũng chưa được giải quyết: liệu hiện tượng độ chính xác target *tăng
  lên* ở điều kiện neutral của họ có lặp lại trên âm học ngôn ngữ có thanh điệu hay không, nơi "văn
  bản trung tính" vẫn mang F0 thanh điệu cạnh tranh với F0 cảm xúc — một câu hỏi chỉ ViEmoSpeech mới
  có thể trả lời.
