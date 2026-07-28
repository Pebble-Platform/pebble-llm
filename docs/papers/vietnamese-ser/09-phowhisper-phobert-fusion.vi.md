# Paper vn-09 — PhoWhisper + PhoBERT Bimodal Vietnamese SER (VNU Hà Nội)

> Bản dịch tiếng Việt của [09-phowhisper-phobert-fusion.md](09-phowhisper-phobert-fusion.md) — cập nhật 2026-07-10.

- **Tác giả:** (nhóm VNU Hà Nội — cần xác minh lại từ PDF)
- **Venue / năm:** arXiv preprint, tháng 12/2024
- **Liên kết:** abstract https://arxiv.org/abs/2412.09829 · PDF `pdfs/09-phowhisper-phobert-fusion.pdf`
- **Nhóm:** vietnamese-ser / baseline trực tiếp cần vượt qua

**Tóm tắt:** SER tiếng Việt bimodal, kết hợp bản chuyển văn ASR từ PhoWhisper
với đặc trưng văn bản từ PhoBERT thông qua fusion dựa trên luật (rule-based),
trên một corpus khoảng ~250 clip.

**Mức độ liên quan tới ViEmoSpeech:** Đây là baseline trực tiếp mà paper
phương pháp phải vượt qua — cùng các khối xây dựng (PhoWhisper+PhoBERT) nhưng
fusion dựa trên luật, corpus rất nhỏ, không xử lý thanh điệu, không có
recall-floor. Các điểm khác biệt (delta) của chúng ta: fusion có học
(learned fusion) (V-A), corpus 3611+ utterance, chú thích thanh điệu (V-D),
recall-floor cho distress (V-F).

> Stub được tạo ngày 2026-07-10 (task `docs/tasks/paper-deep-analysis.md`); việc đọc sâu (deep-read) đang chờ xử lý.

## Nghiên cứu sâu — đọc toàn văn PDF (2026-07-10)

> **Đính chính stub ngay từ đầu.** Stub ở trên (và bản kiểm kê task) mô tả paper này là
> "SER tiếng Việt bimodal PhoWhisper + PhoBERT, fusion dựa trên luật, corpus ~250 clip." Nhưng
> toàn văn PDF thực chất là một thứ khác hẳn: một **pipeline đánh giá chất lượng dịch vụ**
> (chấm điểm cuộc gọi tổng đài: *Good / Neutral / Offensive*), **không phải** một paper SER. Paper
> **không** xây dựng corpus, **không** fuse audio+text cho emotion, và **không** báo cáo bất kỳ
> đánh giá end-to-end nào cho phần fusion của nó. Nhánh văn bản là PhoBERT-CNN làm phân loại
> **hate-speech** (phát ngôn thù ghét, không phải emotion); ~250 clip là tập SER **VNEMOS bên ngoài**
> mà paper mượn một mô hình đã huấn luyện sẵn (mô hình đó chính là paper vn-10,
> arXiv:2412.08683, cùng nhóm tác giả). Paper vẫn là tài liệu tham chiếu đúng cho "baseline
> rule-fusion" trong **V-A**, nhưng baseline đó chỉ là một luật ghi đè viết tay, không có độ chính
> xác đo được, nên "con số cần vượt qua" thực ra không tồn tại.

### Ghi chú về nguồn truy cập

- **Đọc bản local:** `pdftotext "docs/papers/vietnamese-ser/pdfs/09-phowhisper-phobert-fusion.pdf" -`
  trích xuất sạch toàn bộ 8 trang (arXiv:2412.09829**v1** [cs.CY], 13/12/2024). Tất cả hình ảnh đều
  ở dạng ảnh (sơ đồ kiến trúc, biểu đồ GDP); phần trích xuất bắt được đầy đủ các công thức
  (Eqs 1–5, bộ khử nhiễu — denoiser) và khối số liệu duy nhất (các con số thành phần ViHSD ở §2.4).
  Quét bằng `grep` với `table|accuracy|F1|precision|recall|%|WER|split|test` trên toàn bộ PDF
  **không cho ra bảng kết quả nào và không có đánh giá fusion/chất lượng dịch vụ nào** — xác nhận
  các con số ViHSD ở §2.4 là nội dung định lượng duy nhất.
- **Xác minh trên web — tình trạng của paper.** Truy vấn `arXiv 2412.09829 Speech-based Multimodel
  Pipeline Vietnamese Services Quality Assessment` → `https://arxiv.org/abs/2412.09829`. Paper đã
  bị **chính các tác giả rút lại (withdrawn)** ở phiên bản v2 (18/12/2024, năm ngày sau v1). Ghi chú
  rút bài (nguyên văn, ✔ đã đối chiếu): *"I am writing to request the withdrawal of my preprint due
  to the discovery of significant inaccuracies in the results. These errors could mislead future
  research and applications, which compromises the integrity of my work. I believe withdrawing the
  paper is essential to uphold scientific standards…"* (tạm dịch: "Tôi viết để yêu cầu rút lại
  preprint của mình do phát hiện những sai lệch đáng kể trong kết quả. Những sai sót này có thể gây
  hiểu lầm cho các nghiên cứu và ứng dụng trong tương lai, làm tổn hại đến tính toàn vẹn của công
  trình. Tôi tin rằng việc rút bài là cần thiết để giữ vững chuẩn mực khoa học…"). Đây là chi tiết
  mang tính quyết định: paper baseline trực tiếp đã tự rút lại.
- **Xác minh trên web — các con số của nhánh văn bản mượn từ nơi khác.** Truy vấn `PhoBERT-CNN
  ViHSD Vietnamese hate offensive detection accuracy macro F1 Tran 2022` →
  `https://arxiv.org/abs/2206.00524` (Tran và cộng sự, *Vietnamese Hate and Offensive Detection using
  PhoBERT-CNN*, Neural Computing & Applications 2022, ref [16]/[23] mà paper này tái sử dụng). Bản
  gốc báo cáo **macro-F1 67.46%** trên ViHSD (✔ đã đối chiếu). §2.4 của paper này báo cáo **độ chính
  xác 86.14%** với các F1 theo lớp mà khi lấy trung bình macro chỉ ra **~53.7%** — *thấp hơn* và
  **không nhất quán** với nguồn gốc (xem phần cờ cảnh báo mâu thuẫn bên dưới).
- **Tác giả/đơn vị công tác (stub trước đó thiếu, nay đã bổ sung, ✔ từ khối tiêu đề PDF + arXiv):**
  Quang-Anh N.D. (`anhnd@vnuis.edu.vn`), Minh-Duc Pham (`pmduc2808@gmail.com`), Thai Kim Dinh
  (`thaikd@vnu.edu.vn`, tác giả liên hệ) — **International School, Đại học Quốc gia Hà Nội
  (VNU-IS)**. Cùng phòng lab với vn-10 (VNEMOS / Dynamic-CBAM depression).

### Paper thực sự làm gì

Một **pipeline dạng cascade (chuỗi tầng)** gồm năm giai đoạn (§2, Hình 2–5) để chấm điểm một cuộc
gọi dịch vụ khách hàng:

1. **Bộ khử nhiễu (Denoiser)** (§2.1, Eqs 1–5): `resemble-enhance` của Resemble-AI, một UNet trên
   phổ phức (complex spectrogram) (dự đoán mặt nạ biên độ + xoay pha), hàm mất mát L1 trên waveform.
   Dùng sẵn (off-the-shelf), không huấn luyện lại trong paper này.
2. **WhisperX** (§2.2): phân tách người nói (diarization — "ai nói khi nào") qua căn chỉnh
   wav2vec2.0 + VAD/embedding/clustering của pyannote. Dùng sẵn.
3. **PhoWhisper** (§2.3): ASR tiếng Việt (speech-to-text). Được trích dẫn là đã fine-tune trên
   **844 giờ** (Common Voice-Vi, VIVOS, VLSP-2020, + một tập riêng 26,000 người nói / 63 tỉnh
   thành), "SOTA cho S2T tiếng Việt" (≈ đã đối chiếu; đây là tuyên bố của chính paper PhoWhisper,
   ref [15] Le & Nguyen, ICLR 2024 Tiny Papers, không được đo lại ở đây). Dùng sẵn.
4. **Nhánh văn bản — PhoBERT-CNN** (§2.4): PhoBERT-base (đóng băng — frozen, dùng làm bộ trích xuất
   đặc trưng) → đầu Text-CNN, **fine-tune trên ViHSD** cho phân loại **hate-speech 3 lớp**
   (**CLEAN / OFFENSIVE / HATE**), 20 epoch. Kết quả báo cáo (§2.4, các con số duy nhất của paper):
   **accuracy 86.14%**; theo từng lớp (P / R / F1): CLEAN **94.90 / 36.71 / 47.38**, OFFENSIVE
   **91.55 / 41.79 / 60.48**, HATE **93.19 / 30.90 / 53.14**. Lưu ý là mô-đun này phân loại **văn
   bản mạng xã hội dạng viết**, nhưng lại được áp dụng lúc suy luận (inference) lên **bản chuyển văn
   ASR** — không có bất kỳ sự thích nghi (adaptation) nào giữa hai văn phong (register) này.
5. **Nhánh audio — SER** (§2.5): **Dynamic Attention Network / Dynamic-CBAM** (MFCC → các khối
   Conv-BatchNorm-MaxPool xếp chồng → GRU → Dynamic CBAM → FC), được dùng **như một mô hình đã
   huấn luyện sẵn**, huấn luyện trên **VNEMOS** — **250 đoạn được gán nhãn từ 27 phim/series/
   chương trình trực tiếp, 5 cảm xúc** (giận dữ, vui, buồn, trung tính, sợ hãi). Đây chính là tập
   SER bên ngoài mà stub trước đó nhầm là "corpus của họ"; nó là ref [26] (VNEMOS, ICDV 2024) và mô
   hình là ref [24] (= vn-10). Paper này **không** báo cáo con số SER nào.

**Phần fusion (§2.6) — toàn bộ tuyên bố "bimodal".** Một **luật chấm điểm viết tay** trên đầu ra
của hai nhánh, cho ra **Good / Neutral / Offensive**:

- **Text ghi đè (override):** nếu S2T (PhoBERT-CNN) trả về **OFFENSIVE hoặc HATE → grade =
  Offensive** (ưu tiên tuyệt đối cho luồng văn bản).
- **Leo thang cảm xúc (Emotion escalation):** ngược lại, nếu text sạch **nhưng SER ∈ {Anger,
  Anxiety, Sadness} → Offensive** ("khách hàng không có trải nghiệm tốt"). (Lưu ý: đầu SER chỉ phát
  ra anger/happy/sad/neutral/fear — "Anxiety" trong luật không có lớp tương ứng, một điểm hở/thiếu
  nhất quán.)
- **Còn lại:** text sạch → grade theo SER: **Happiness → Good, Neutral → Neutral**.

Đó là toàn bộ "fusion": một **cây quyết định ưu tiên-ghi đè (priority-override)**, thiên về text,
**không có tham số học được, không có trọng số, không có độ tin cậy (confidence), và không có đánh
giá**. Paper không có mục §3 thực nghiệm — đi thẳng từ §2.6 sang một đoạn Kết luận duy nhất ở §3.

**Mâu thuẫn nội tại (củng cố việc rút bài, ✖ không đối chiếu được / tự mâu thuẫn):** ViHSD có tỷ lệ
CLEAN khoảng ~82–83%. Một **recall của CLEAN là 36.71%** là điều **không thể tương thích về mặt
toán học** với một **accuracy tổng thể 86.14%** (recall của lớp đa số ở mức 0.37 giới hạn accuracy
tối đa chỉ khoảng ~0.30). Các con số ở §2.4 không thể đồng thời đúng; chúng cũng cho ra macro-average
thấp hơn con số 67.46% của paper nguồn. Đây là bằng chứng cụ thể cho lý do các tác giả tự rút bài.

### Các phần hữu ích trực tiếp cho Pebble

1. **Baseline rule-fusion, phát biểu chính xác — [V-A].** Đối thủ mà fusion có học của chúng ta
   phải vượt qua là: *ưu tiên phán quyết từ text → dự phòng bằng emotion*, một cây quyết định
   cứng, thiên về text, không có tham số fusion học được. Hai đặc điểm quan trọng đối với
   ViEmoSpeech: (a) nó fuse **nhãn lớp cứng (hard class labels)**, không phải feature/logit — bỏ
   qua toàn bộ tương tác liên-modal và toàn bộ độ tin cậy; (b) nó **ưu tiên text theo thiết kế**
   (text có thể phủ quyết; audio chỉ quyết định trong các trường hợp còn lại). Fusion có học của
   chúng ta (cross-attention / gated / query-based) nên được định vị chính xác là *mềm, ở mức
   feature, được huấn luyện đồng thời (jointly-trained)* đối lập với luật *cứng, ở mức nhãn, sắp
   xếp thủ công* này.
2. **"Con số baseline cần vượt qua" không tồn tại — [V-A][V-G].** Vì không có đánh giá end-to-end
   nào và paper đã bị rút, ViEmoSpeech **không thể trích dẫn một chỉ số fusion accuracy từ vn-09**.
   Cách trình bày trung thực: vn-09 là baseline *về mặt kiến trúc* (fusion dựa trên luật tồn tại
   trong tài liệu tiếng Việt) nhưng **không cung cấp thước đo định lượng nào**. Các thước đo định
   lượng đến từ vn-08 (arXiv:2604.01711, 86.6% / κ 0.857) và dòng VNEMOS chỉ-audio — không phải từ
   đây.
3. **Nhánh văn bản được huấn luyện trên sai văn phong — [V-C].** PhoBERT-CNN được fit trên **ViHSD
   dạng viết sạch** rồi chạy trên **đầu ra ASR của PhoWhisper** mà không có sự thích nghi miền
   (domain adaptation) hay xử lý chống nhiễu nào. Đây chính xác là khoảng hở nhiễu-ASR mà V-C nêu
   ra. Đây là một *ví dụ phản diện (negative exemplar)*: nó cho thấy điều gì xảy ra nếu bỏ qua sự
   lệch pha giữa văn bản viết và ASR (và, trong một ngôn ngữ có thanh điệu, các lỗi hoán đổi thanh
   điệu ở mức độ kích hoạt cao — mày→máy — làm đảo nghĩa). Lựa chọn V-C của ViEmoSpeech (PhoBERT
   so với ViSoBERT so với CafeBERT, huấn luyện/đánh giá trên bản chuyển văn ASR, kiểm thử trên
   phụ đề vàng) giải quyết trực tiếp điều mà vn-09 để ngỏ.
4. **Chuỗi nguồn gốc của corpus/SER — [V-G][V-H].** VNEMOS = **250 clip / 27 nguồn / 5 lớp** là tập
   SER "nguồn phim truyền hình Việt nhỏ" cụ thể mà corpus 3611-utterance / 7-lớp + V/A + distress
   của ViEmoSpeech vượt lên trên. Các delta 250-so-với-3611 và 5-lớp-so-với-7+V/A+distress là đóng
   góp thiết kế corpus có thể định lượng, và vn-09 cho thấy giới hạn của việc xây dựng *trên nền*
   250 clip: chỉ có thể mượn một mô hình đã huấn luyện sẵn, không thể làm đánh giá SER
   speaker-disjoint.
5. **Lan truyền lỗi theo chuỗi (cascade) như một cảnh báo thiết kế — [V-A][V-B].** Năm tầng dùng sẵn
   nối tiếp nhau (khử nhiễu → phân tách người nói → ASR → phân loại text ‖ SER → luật) đồng nghĩa
   với việc lỗi cộng dồn và không bao giờ được tối ưu hóa đồng thời. Điều này thúc đẩy việc
   ViEmoSpeech dùng fusion audio+text được **huấn luyện đồng thời (jointly-trained)** thay vì một
   chuỗi cascade đóng băng, và thúc đẩy việc giữ nhánh audio (V-B) có khả năng mang thông tin cảm
   xúc ngay cả khi ASR sai — ngược lại hoàn toàn với thứ tự ưu tiên-text của vn-09.

### Mỗi phần giúp Pebble thành công như thế nào

- **[V-A] Định vị phần ablation fusion của paper phương pháp trước một luật vn-09 được cài lại.**
  Sản phẩm cụ thể: trong thí nghiệm fusion, thêm một **hàng baseline "rule-fusion"** tái tạo logic
  của §2.6 trên nhãn ViEmoSpeech (ánh xạ: ghi đè theo độc hại/phủ định của text → dự phòng bằng
  emotion), và cho thấy fusion cross-attention/gated có học vượt qua nó trên macro-F1 và CCC. Vì
  vn-09 không đưa ra con số nào, *chính chúng ta tự tạo ra con số baseline* trên corpus của mình —
  đó là phép so sánh công bằng, có thể tái lập, và trả lời trực tiếp câu hỏi "fusion có học có
  vượt qua luật hay không."
- **[V-C] Biến khả năng chống nhiễu ASR thành một thí nghiệm rõ ràng, không phải một giả định.**
  Sản phẩm cụ thể: huấn luyện nhánh text trên **bản chuyển văn PhoWhisper** (không phải văn bản
  vàng) và đánh giá trên cả bản chuyển văn ASR lẫn phụ đề vàng; báo cáo mức độ suy giảm. Sự lệch
  pha huấn luyện-trên-sạch / suy luận-trên-ASR của vn-09 chính là nhánh "ngây thơ (naive)" của phần
  ablation. Thêm một lát cắt stress-test hoán đổi thanh điệu (các câu nói mức độ kích hoạt cao nơi
  mày/tao bị chuyển văn sai) để định lượng yếu tố nhiễu (confound) ở kênh phát âm mà hồ sơ dự đoán.
- **[V-G] Không báo cáo một độ chính xác fusion của vn-09; báo cáo sự vắng mặt của nó.** Sản phẩm
  cụ thể: bảng baseline trong tài liệu giao thức đánh giá (eval-protocol doc) liệt kê vn-09 là
  *"rule fusion, không có đánh giá end-to-end, đã bị rút bài"* và lấy các thước đo định lượng từ
  vn-08 và dòng VNEMOS chỉ-audio. Điều này giữ cho phép so sánh của ViEmoSpeech trung thực và tránh
  kế thừa các con số đã bị rút lại.
- **[V-H] Dùng bước nhảy 250→3611 clip và 5→7+V/A+distress làm đóng góp corpus đã nêu.** Sản phẩm
  cụ thể: thẻ corpus tại `docs/spec/capabilities/` trích dẫn VNEMOS-250 như giới hạn trước đó của
  SER phim truyền hình Việt, và định vị quy mô/độ phong phú nhãn/split speaker-disjoint/chú thích
  thanh điệu của ViEmoSpeech là các delta.
- **[V-B] Giữ nhánh audio có vai trò thiết yếu (load-bearing).** Sản phẩm cụ thể: trong fusion,
  tránh thứ tự text-ghi-đè; dùng fusion có học đối xứng để nhánh audio (WavLM/emotion2vec + đặc
  trưng phát âm) có thể ghi đè text khi ASR không đáng tin cậy — đúng thất bại mà luật ưu tiên-text
  của vn-09 không thể xử lý.

### Lăng kính sức khỏe tâm thần trẻ em

- **Miền là chất lượng dịch vụ tổng đài người lớn, không phải cảm xúc trẻ em.** Proxy *distress*
  của vn-09 là "khách hàng có trải nghiệm tồi → grade Offensive" — một cấu trúc về mức độ hài lòng
  thương mại, không phải một cấu trúc lâm sàng hay an toàn trẻ em. Việc chuyển giao sang **đầu
  distress của ViEmoSpeech về cơ bản là bằng không ở mức nhãn**; chỉ có *kiến trúc* (VN ASR + bộ mã
  hóa văn bản VN + SER) là chuyển giao được. Cần nói rõ: vn-09 xác nhận rằng ngăn xếp
  PhoWhisper+PhoBERT+SER là khả thi cho tiếng Việt, và **không cho biết gì về cách chấm điểm
  distress trong phim truyền hình hướng-đến-trẻ-em có diễn xuất**.
- **Recall floor: vn-09 làm ngược lại điều ViEmoSpeech cần.** Nhánh text của nó có recall thảm hại
  trên chính các lớp thiểu số mà nó quan tâm (OFFENSIVE R 41.8%, HATE R 30.9% — ≈/✖ do có mâu thuẫn
  nội tại), tức là nó *bỏ sót* phần lớn các trường hợp có hại trong khi vẫn khoe accuracy 86%. Đối
  với một đầu distress có recall-floor, đây chính là phản-mẫu (anti-pattern): accuracy trên một tập
  mất cân bằng che giấu việc bỏ sót lớp thiểu số. Mục tiêu recall-floor V-F của ViEmoSpeech tồn tại
  chính xác để tránh thất bại này.
- **Xử lý thanh điệu: không có.** vn-09 không có chú thích thanh điệu và không nhận thức được rằng
  thanh điệu tiếng Việt phụ thuộc nặng vào phát âm (phonation-heavy); nó áp một bộ phân loại
  hate-speech dạng viết lên đầu ra ASR, nơi các lỗi hoán đổi thanh điệu ở mức độ kích hoạt cao làm
  hỏng chính những từ độc hại/phủ định mà luật dựa vào. Đối với giọng nói trẻ em (cao độ cao hơn,
  ngữ điệu biến thiên nhiều hơn) sự mong manh của ASR này sẽ còn tệ hơn, củng cố lý do vì sao
  ViEmoSpeech chú thích thanh điệu ở mức âm tiết và không để text đơn phương phủ quyết (V-D).
- **Ghi chú về đạo đức/khung tiếp cận.** vn-09 chấm điểm và lưu trữ các phán xét về cá nhân
  ("Offensive") từ audio cuộc gọi mà không có bất kỳ thảo luận nào về sự đồng thuận/chất lượng chú
  thích. Việc ViEmoSpeech phát hành dữ liệu phim có diễn xuất, chỉ-đặc-trưng, CC-BY, cùng khung tiếp
  cận trung thực "proxy có diễn xuất ≠ lâm sàng" chính là đối lập có trách nhiệm cần nêu bật.

### Hạn chế & câu hỏi mở cho Pebble

- **Mâu thuẫn / khoảng hở #1 (so với chính tình trạng của paper):** baseline kiến trúc trực tiếp
  **đã tự bị rút lại vì "những sai lệch đáng kể,"** và các con số duy nhất của nó **không nhất
  quán nội tại** (recall CLEAN 36.71% không thể cùng tồn tại với accuracy 86.14% trên ViHSD
  ~82%-CLEAN). Do đó ViEmoSpeech **không được** trích dẫn một chỉ số fusion của vn-09 như một
  thước đo; chỉ có thể trích dẫn *thiết kế* (rule fusion) và phải tự tạo ra con số so sánh của
  riêng mình.
- **Mâu thuẫn / khoảng hở #2 (so với luận điểm bimodal thanh điệu×cảm xúc của ViEmoSpeech):** vn-09
  **ưu tiên text** (text có thể phủ quyết luồng emotion vô điều kiện). Luận điểm cốt lõi của
  ViEmoSpeech lại **đối lập hoàn toàn** — trong một ngôn ngữ có thanh điệu, phụ thuộc nặng vào phát
  âm, kênh audio/prosody *đóng vai trò quan trọng hơn* và văn bản ASR *kém tin cậy hơn* dưới mức độ
  kích hoạt cao. Hai thiết kế mã hóa những tiền đề (prior) trái ngược nhau về việc nên tin tưởng
  modal nào; paper phương pháp của chúng ta nên nêu rõ sự bất đồng này và giải quyết nó bằng thực
  nghiệm (ablation fusion, lát cắt nhiễu ASR).
- **Mâu thuẫn / khoảng hở #3 (so với vn-08 / vn-10 về mặt định lượng):** vn-09 **không cung cấp bất
  kỳ độ chính xác SER hay fusion nào**, trong khi vn-08 (arXiv:2604.01711) báo cáo 86.6% / κ 0.857
  và vn-10 báo cáo SER trên VNEMOS. vn-09 không thể được đặt trên cùng một trục — một khoảng hở
  trong bức tranh baseline mà hàng rule-fusion tự cài lại của ViEmoSpeech phải lấp đầy.
- **Câu hỏi mở:** liệu **tập 250-clip VNEMOS** có thể tiếp cận được không (license/gate) để
  ViEmoSpeech có thể chạy một kiểm tra sanity *cross-corpus* chỉ-audio (huấn luyện trên
  ViEmoSpeech → kiểm thử trên tập con VNEMOS-5-lớp)? Paper không đưa ra điều khoản khả dụng nào;
  VNEMOS là ref [26] (ICDV 2024, IEEE) — có khả năng bị gate (giới hạn truy cập). Nếu không thể
  tiếp cận, VNEMOS vẫn chỉ là một nguồn tham chiếu *chỉ để trích dẫn*, không phải một corpus so
  sánh.
- **Câu hỏi mở:** lớp SER **"Anxiety"** không xác định trong luật (không có trong đầu 5-lớp) cho
  thấy pipeline có thể chưa từng thực sự được chạy end-to-end — nhất quán với việc rút bài. Hãy coi
  mọi chi tiết vận hành của vn-09 là *ý định chưa được kiểm chứng*, không phải hành vi đã được đo
  lường.
