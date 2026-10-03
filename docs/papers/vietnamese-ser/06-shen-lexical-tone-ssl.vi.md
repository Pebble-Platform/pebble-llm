# Paper vn-06 — Encoding of Lexical Tone in Self-Supervised Models of Spoken Language

> Bản dịch tiếng Việt của [06-shen-lexical-tone-ssl.md](06-shen-lexical-tone-ssl.md) — cập nhật 2026-07-10.

- **Authors:** Gaofei Shen et al. (verify against anthology page)
- **Venue / year:** NAACL 2024 (long)
- **Links:** anthology https://aclanthology.org/2024.naacl-long.239/ · PDF `pdfs/06-shen-lexical-tone-ssl.pdf`
- **Group:** vietnamese-ser / tonal prior art (phonetic premise)

**Tóm tắt:** Bài báo kiểm tra (probe) xem các bộ mã hóa SSL kiểu wav2vec2 ở
trạng thái đóng băng (frozen) có mã hóa tuyến tính (linearly encode) thanh
điệu từ vựng (lexical tone) hay không, bao gồm cả tiếng Việt (VIVOS) so với
tiếng Quan Thoại (THCHS-30). Kết quả cho thấy thanh điệu tiếng Việt khó giải
mã hơn và phụ thuộc nhiều hơn vào các tín hiệu về phát âm/chất giọng
(phonation/voice-quality) thay vì các tín hiệu đường nét/độ cao F0
(F0-contour/height) vốn chi phối thanh điệu tiếng Quan Thoại; không có sự
chuyển giao (transfer) từ Quan Thoại sang tiếng Việt.

**Mức độ liên quan với ViEmoSpeech:** Đây là bài báo nền tảng quan trọng
nhất (load-bearing) cho tiền đề ngữ âm học của mối liên kết tone×emotion
(VN tone is phonation-heavy — kênh mà cảm xúc cũng sử dụng). Trước đây repo
chỉ biết đến bài này qua mục đã lưu trữ
`archive/docs/voice/35-shen-lexical-tone-ssl.md`; nay đã có PDF ở local.

> Stub created 2026-07-10 (task `docs/tasks/paper-deep-analysis.md`); deep-read pending.

## Deep research — đọc toàn văn PDF (2026-07-10)

> Đọc toàn bộ bài báo NAACL 2024 long từ đầu đến cuối, từ PDF local
> (`pdfs/06-shen-lexical-tone-ssl.pdf`) qua `pdftotext`. Đây là **tiền đề ngữ âm
> học nền tảng** (load-bearing phonetic premise) của method paper ViEmoSpeech
> (thanh điệu tiếng Việt phụ thuộc nhiều vào phonation). Vì bài báo báo cáo mọi
> độ chính xác probing dưới dạng **biểu đồ đường (line-plot)** (Fig 2–8) và
> **không có bảng số liệu chính xác dạng số**, phần này rất cẩn trọng trong
> việc phân biệt số liệu nào tồn tại dưới dạng văn bản so với chỉ tồn tại
> dưới dạng biểu đồ, và gắn nhãn tương ứng cho từng số liệu. Các tham chiếu
> chéo trỏ ngược lại phần stub ở trên.

### Ghi chú về cách tiếp cận nguồn

- **Cách đọc:** `pdftotext "docs/papers/vietnamese-ser/pdfs/06-shen-lexical-tone-ssl.pdf" -`
  (46.6 KB văn bản, đầy đủ phần method + toàn bộ chú thích hình + cả hai bảng
  tách đôi + tài liệu tham khảo).
- **Đã kiểm chứng qua web:**
  - Tiêu đề / tác giả / venue / số trang — WebFetch trang ACL Anthology.
    Query: anthology 2024.naacl-long.239. Kết quả:
    `https://aclanthology.org/2024.naacl-long.239/`. Xác nhận
    "Encoding of lexical tone in self-supervised models of spoken language",
    Shen · Watkins · Alishahi · Bisazza · Chrupała, **NAACL 2024, pp. 4250–4261**. ✔
  - Hai luận điểm định tính nền tảng (không có sự chuyển giao Mandarin→Vietnamese;
    tiếng Việt phụ thuộc vào **phonation type + voice quality** thay vì
    **F0 contour / height** như tiếng Quan Thoại) — WebFetch bản mirror HTML trên
    arXiv `https://arxiv.org/html/2403.16865v1` (query: Shen encoding lexical
    tone Vietnamese phonation voice quality probing accuracy). Câu trích dẫn
    nguyên văn *"Vietnamese uses different acoustic cues such as phonation
    type and voice quality in tonal perception than f0 contours or height in
    Mandarin (Brunelle, 2009)"* được xác nhận đúng nguyên văn. ✔
  - **Xác nhận việc không có số liệu chính xác dạng số:** cả metadata trên
    Anthology lẫn bản HTML trên arXiv đều xác nhận bài báo **không có bất kỳ
    tỷ lệ phần trăm chính xác probing-accuracy nào bằng số** trong văn bản
    hay chú thích — mọi kết quả đều là biểu đồ đường. Do đó mọi luận điểm về
    độ chính xác bên dưới đều được gắn nhãn ≈ (đọc từ biểu đồ, mang tính xấp
    xỉ) hoặc ✖ (không được báo cáo bằng số); chỉ có kích thước tập split, số
    giờ dữ liệu, số lượng tham số và tỷ lệ lỗi baseline được *trích dẫn* là
    số liệu chắc chắn (✔). Không phát hiện xung đột nào giữa preprint/venue
    (arXiv v1 và bản camera-ready NAACL thống nhất với nhau ở mọi điểm đã
    kiểm tra).

### Bài báo thực sự làm gì

**Mục tiêu.** Kiểm tra xem các mô hình ngôn ngữ nói tự giám sát (SLM) kiểu
wav2vec2 ở trạng thái *đóng băng* có mã hóa tuyến tính **thanh điệu từ
vựng** (lexical tone) trong các hidden state của chúng hay không, sử dụng
tiếng Quan Thoại (chính) và tiếng Việt (kiểm tra khả năng khái quát hóa)
làm case study, và liệu việc fine-tune ASR cùng tính có-thanh-điệu của ngôn
ngữ pretrain có làm thay đổi sự mã hóa đó hay không. Đây là bài báo về
**diễn giải (interpretability)/probing**, không phải bài báo về SER và
cũng không phải một cuộc thi phân loại thanh điệu.

**Các mô hình (§4.2).** wav2vec2-**base** (95M tham số: 5 lớp conv
feature-encoder + 12 lớp transformer, hidden state 768 chiều) được
pretrain/fine-tune riêng theo từng ngôn ngữ: tiếng Anh (LibriSpeech), tiếng
Pháp (MLS), tiếng Quan Thoại (pretrain trên AISHELL-2 / ASR-FT trên
AISHELL-1), tiếng Việt (pretrain trên 13k giờ YouTube / ASR-FT trên VLSP —
lưu ý mô hình tiếng Việt được huấn luyện trên **13,000 giờ**, gấp ~13 lần
các ngôn ngữ khác, được nêu như một biến gây nhiễu (confound) ở §7), và một
mô hình wav2vec2-**conformer** tiếng Quảng Đông (180M, kiến trúc lớn hơn và
khác — cũng là một confound). ✔ đối với các con số tham số/số giờ (dạng
văn bản trong Table 1).

**Dữ liệu kiểm thử (§4.1).** Tiếng Quan Thoại **THCHS-30** (30 giờ giọng
đọc thu trong phòng lab; căn chỉnh cưỡng bức cấp ký tự bằng Charsiu; nhãn
thanh điệu từ Pinyin→tone, loại bỏ thanh nhẹ (neutral tone)). Tiếng Việt
**VIVOS** (15 giờ giọng đọc thu trong phòng lab; chuyển văn bản→IPA+thanh
điệu bằng **vPhon** (Kirby 2008); căn chỉnh âm tiết bằng **Montreal Forced
Aligner**; hệ thống **8 thanh điệu** theo Kirby-2011). ✔ (số giờ dữ liệu là
dạng văn bản).

**Probe (§4.3).** Trung bình hóa (average-pool) hidden state của mỗi lớp
SLM trên cửa sổ căn chỉnh cưỡng bức của một âm tiết → vector 768 chiều →
bộ phân loại tuyến tính **Ridge** dự đoán thanh điệu, 5-fold CV, hệ số
regularization quét từ 10⁻⁴…10². **Kiểm soát confound then chốt:** tập
train/test được xây dựng sao cho **các chuỗi âm vị (phoneme string) trong
test không xuất hiện trong train** — điều này ngăn probe "ăn gian" bằng
liên hệ từ vựng (chuỗi âm vị↔thanh điệu) thay vì đặc trưng ngữ âm thanh
điệu thực sự. Kích thước split (**Table 2**, ✔ dạng văn bản): tiếng Quan
Thoại **223,851 train / 45,772 test**; tiếng Việt **124,248 train / 29,629
test**. Probe phụ âm (**Table 3**, ✔): **92,413 / 15,688**. Các baseline:
**F0 contour** (21 chiều, Praat), **MFCC** (40 chiều × 21 khung = 840
chiều, Librosa), và một baseline **Chinese-BERT văn bản** (768 chiều, theo
từng ký tự) đóng vai trò là "ngưỡng sàn — những gì có thể đoán được chỉ từ
văn bản".

**Kết quả.**
- **§5.1 Thanh điệu tiếng Quan Thoại (Fig 2):** *tất cả* các lớp SLM đều
  vượt qua baseline F0 và MFCC, hai baseline này lại vượt qua baseline văn
  bản BERT; các mô hình huấn luyện trên ngôn ngữ có thanh điệu đạt điểm cao
  hơn và **tăng dần ở các lớp trên**, trong khi các mô hình huấn luyện trên
  ngôn ngữ không có thanh điệu cho thấy **sự sụt giảm mạnh ở các lớp cuối**.
  Ngay cả các SLM tiếng Anh/tiếng Pháp (không có thanh điệu) cũng mã hóa
  thanh điệu tiếng Quan Thoại ở mức đáng kể. (độ chính xác ≈ chỉ có ở biểu
  đồ.)
- **§5.1 Thanh điệu tiếng Việt (Fig 3):** mô hình **tiếng Quảng Đông**
  vượt qua mô hình tiếng Anh (đặc biệt ở các lớp sau); mô hình **tiếng
  Quan Thoại** lại **có xu hướng giống mô hình tiếng Anh** — nghĩa là một
  bộ mã hóa thanh điệu Quan Thoại mạnh **không** chuyển giao được sang
  thanh điệu tiếng Việt, trong khi tiếng Quảng Đông (vốn có thanh điệu
  đăng ký/register dựa trên phonation) lại chuyển giao được một phần. Giải
  thích của tác giả: *"Vietnamese uses different acoustic cues such as
  phonation type and voice quality in tonal perception than f0 contours or
  height in Mandarin."* ✔ (trích dẫn nguyên văn) — nhưng bản thân độ chênh
  lệch về độ chính xác thì ≈ chỉ có ở biểu đồ.
- **§5.2 Fine-tune ASR (Fig 4–5):** fine-tune cho ASR **tăng cường** mã
  hóa thanh điệu đối với các mô hình ngôn ngữ có thanh điệu (Quan Thoại,
  tiếng Việt) nhưng **làm suy giảm** mã hóa này đối với mô hình không có
  thanh điệu (tiếng Anh) — vì thanh điệu cần thiết để xuất ra đúng ký
  tự/chính tả trong một ngôn ngữ có thanh điệu, và bị loại bỏ như nhiễu
  (nuisance) trong ngôn ngữ không có thanh điệu. (chiều hướng ✔; độ lớn ≈
  chỉ có ở biểu đồ.)
- **§5.3 Tính tương đồng với con người (Human-parity):** các SLM tái hiện
  lại thứ tự khó/dễ trong nhận thức của con người đối với các cặp thanh
  điệu Quan Thoại (T2–T3 và T1–T4 dễ nhầm lẫn nhất) và các nhóm phụ âm ánh
  xạ theo tiếng Anh, nhưng **không** tuân theo quỹ đạo phát triển ở trẻ em
  (thanh điệu học trước phụ âm). Không liên quan trọng yếu tới ViEmoSpeech.
- **Các baseline được trích dẫn (không phải kết quả của chính bài báo này,
  ✔ dưới dạng trích dẫn):** Ryant et al. 2014a — một bộ phân loại thanh
  điệu Quan Thoại chỉ dùng MFCC đạt **15.56% lỗi** trên T1–4 *mà không cần
  F0 tường minh* (bằng chứng cho thấy MFCC ngầm mang theo tín hiệu chuỗi âm
  vị); Yuan et al. 2021 — một wav2vec2 đã *fine-tune* đạt **tỷ lệ lỗi thanh
  điệu 6%**. Hai kết quả này lý giải vì sao tập split phân tách theo âm vị
  (phoneme-disjoint) lại quan trọng.

### Các phần trực tiếp hữu ích cho ViEmoSpeech (gắn nhãn theo Decision ID)

1. **Tiền đề phonation/voice-quality cho nhánh audio — điểm mấu chốt
   (V-B).** §2 + §5.1(Fig 3) + trích dẫn Brunelle-2009 xác lập rằng thanh
   điệu tiếng Việt được mang bởi **loại phát âm (phonation type: creaky/
   breathy), chất giọng (voice quality), biên độ và độ nghiêng phổ
   (spectral tilt)**, chứ không chủ yếu là đường nét/độ cao F0 vốn định
   nghĩa thanh điệu tiếng Quan Thoại. Đây là bằng chứng thực nghiệm cho
   việc bổ sung các **mô tả voice-quality** tường minh (jitter, shimmer,
   HNR, H1–H2, CPP, spectral tilt) vào nhánh audio của ViEmoSpeech bên
   cạnh bộ mã hóa SSL. **[V-B]**
2. **Giao thức linear-probe theo từng lớp làm công cụ để *định lượng*
   cạnh tranh kênh tone×emotion (V-D, V-G).** Công thức của §4.3 — hidden
   state 768 chiều được average-pool theo âm tiết → probe Ridge → 5-fold
   CV → các baseline F0/MFCC/text → **tập split train/test phân tách theo
   âm vị** — có thể tái sử dụng trực tiếp để biến hook "cạnh tranh kênh"
   (channel competition) của ViEmoSpeech từ văn xuôi thành con số: chạy
   *cùng* probe đó trên bộ mã hóa audio của ViEmoSpeech cho **(a)** nhãn
   thanh điệu âm tiết và **(b)** cường độ cảm xúc/arousal, rồi đo xem các
   lớp và không gian con đặc trưng (feature-subspace) giải mã tốt nhất
   thanh điệu có trùng với các lớp/không gian con giải mã tốt nhất arousal
   hay không. Sự trùng lặp = cạnh tranh đã được định lượng. **[V-D, V-G]**
3. **Hướng dẫn chọn bộ mã hóa / chọn lớp cho V-B (Fig 2 tăng ở lớp trên +
   sụp đổ ở lớp cuối; Fig 4–5 chiều hướng ASR-FT).** Hai sự thật có thể
   hành động: (i) thông tin siêu đoạn tính (suprasegmental) đạt đỉnh ở các
   lớp transformer **giữa/trên** và **sụp đổ ở lớp cuối của các bộ mã hóa
   huấn luyện trên ngôn ngữ không có thanh điệu** — vì vậy lớp *cuối* của
   một WavLM tiếng Anh đóng băng là nơi tệ nhất để đọc cảm xúc mang thanh
   điệu; (ii) **fine-tune ASR trên ngôn ngữ có thanh điệu làm tăng cường**
   mã hóa thanh điệu. ASR của ViEmoSpeech là **PhoWhisper** (đã fine-tune
   cho tiếng Việt) — vì vậy bộ mã hóa của nó nằm ở phía "tăng cường", và
   một wav2vec2 được pretrain trên tiếng Việt là một lựa chọn backbone
   V-B chính đáng hơn so với WavLM tiếng Anh generic *nếu* thông tin thanh
   điệu thực sự có vai trò then chốt. **[V-B]**
4. **Tập split phân tách theo âm vị như một biện pháp kiểm soát confound
   cho V-G.** Kết quả 15.56% chỉ dùng MFCC của Ryant-2014a là một lời cảnh
   báo: một probe "thanh điệu" (hay "thanh điệu×cảm xúc") mà chia sẻ chuỗi
   âm vị giữa train và test sẽ báo cáo các con số bị thổi phồng do thực
   chất là ghi nhớ từ vựng (lexical memorization). Bất kỳ probing/eval nào
   của ViEmoSpeech tự nhận là tách biệt kênh thanh điệu *ngữ âm* thuần túy
   đều phải tái tạo lại tập split phân tách theo âm vị/từ. **[V-G, V-D]**

### Cách mỗi phần giúp ViEmoSpeech thành công

- **V-B (đặc trưng audio): bổ sung vector voice-quality thủ công, không
  chỉ tin vào F0.** Hành động cụ thể: trong nhánh audio, nối thêm một
  vector **kiểu eGeMAPS phonation** chiều thấp (jitter, shimmer, HNR,
  H1–H2, CPP, spectral tilt, theo từng âm tiết) vào embedding SSL trước
  khi fusion, và chạy một ablation V-B *có so với không có* nó. Kết quả
  của Shen dự đoán điều này sẽ giúp ích *nhiều hơn* cho tiếng Việt so với
  một ngôn ngữ không có thanh điệu, chính xác là vì cả thanh điệu và cảm
  xúc tiếng Việt đều tồn tại trong phonation — biểu diễn sau fusion phải
  tách được hai tín hiệu cùng mang bởi phonation. Đây chính là cấu hình
  hiện thực hóa hook "phonation-heavy" của method paper.
- **V-B (backbone): chọn bộ mã hóa tiếng Việt/PhoWhisper và đọc từ các lớp
  giữa.** Hành động: trong cuộc bake-off backbone V-B (WavLM vs emotion2vec
  vs bộ mã hóa Whisper/PhoWhisper), thêm một **layer sweep** và kỳ vọng
  lớp tốt nhất cho việc mã hóa cảm xúc-từ-phonation nằm ở giữa chồng lớp
  (mid-stack), không phải lớp cuối — phản ánh đúng Fig 2. Nếu dùng một
  WavLM tiếng Anh đóng băng, hãy trọng số hóa hoặc pool các lớp *giữa*
  thay vì mặc định dùng hidden state cuối cùng.
- **V-D (định lượng luận điểm): một probe hai mục tiêu trên chính bộ mã
  hóa của ViEmoSpeech.** Hành động — một thí nghiệm mới
  `probe/tone_vs_arousal/`: trên các clip gold có nhãn thanh điệu âm tiết
  + căn chỉnh MFA (ViEmoSpeech đã có cả hai), fit hai probe Ridge cho mỗi
  lớp — một cho nhãn thanh điệu, một cho mức arousal — dưới một **tập
  split phân tách theo từ/âm vị**, và báo cáo (i) đường cong độ chính xác
  theo từng lớp cho mỗi mục tiêu, (ii) lớp đạt đỉnh của từng mục tiêu, và
  (iii) một chỉ số về sự chồng lấn không gian con/giao thoa lẫn nhau
  (subspace-overlap / mutual-interference) (ví dụ: mức sụt giảm độ chính
  xác của thanh điệu sau khi loại bỏ các hướng phân biệt arousal). Chỉ
  riêng biểu đồ này *chính là* xương sống thực nghiệm cho luận điểm mới
  của method paper, được tạo ra bằng đúng phương pháp luận có thể trích
  dẫn của Shen.
- **V-G (vệ sinh giao thức): tái sử dụng bậc thang baseline F0/MFCC/text +
  tập split phân tách theo âm vị.** Hành động: bất kỳ biểu đồ probing nào
  trong bài báo ViEmoSpeech cũng mang theo cùng ba baseline (F0, MFCC,
  ASR-text) để reviewer thấy được kênh âm thanh vượt qua văn bản — luận
  điểm rằng trong tiếng Việt, nhánh audio mang thông tin mà nhánh
  ASR-text về cấu trúc không thể có được (dấu thanh bị mất khi ASR lỗi ở
  mức arousal cao, mày→máy). Bậc thang của Shen là mẫu để làm theo.

### Lăng kính chuyển giao trẻ em / giọng nói tìm được (chế độ ViEmoSpeech)

- **Sự lệch pha register — giọng đọc vs kịch truyền hình tìm được.** VIVOS
  và THCHS-30 là **giọng đọc sạch, thu trong phòng lab**; ViEmoSpeech là
  **kịch truyền hình tìm được** (found TV-drama) với ngữ điệu cảm xúc diễn
  xuất, dư âm nhạc/hiệu ứng âm thanh (sau Demucs), lời thoại chồng lấn, và
  vọng âm (reverberation). Việc theo dõi F0 và các mô tả phonation *nhiễu
  hơn* trên chất liệu này — điều này **củng cố** thêm luận điểm ủng hộ
  embedding SSL (bền vững hơn) so với F0 Praat thô, nhưng **làm suy yếu**
  độ tin cậy của các đặc trưng jitter/HNR thủ công trên các clip SNR thấp.
  Biện pháp giảm thiểu: chỉ tính các đặc trưng voice-quality trên các clip
  vượt qua ngưỡng SNR/voicing; báo cáo độ phủ (coverage) của chúng; giữ
  chúng như một phần nối thêm *phụ trợ* (auxiliary), không bao giờ là tín
  hiệu thanh điệu duy nhất.
- **Khoảng trống về phương ngữ — Shen chỉ kiểm tra giọng Bắc.** VIVOS +
  vPhon + hệ thống 8 thanh điệu Kirby-2011 là tiếng Việt **Hà Nội/miền
  Bắc**. ViEmoSpeech trải rộng cả **Bắc/Trung/Nam**. Hệ thống thanh điệu
  miền Trung và miền Nam mang tính đăng ký/phonation *nhiều hơn* và gộp
  nhiều cặp đối lập thanh điệu miền Bắc — vì vậy tiền đề phonation của
  Shen có khả năng **càng đúng hơn** đối với giọng miền Nam, nhưng bài báo
  **không** cung cấp bằng chứng trực tiếp nào cho các phương ngữ ngoài
  miền Bắc. Probe tone×emotion phải phân tầng theo phương ngữ, và lược đồ
  nhãn thanh điệu (V-D) phải nhận biết phương ngữ (dialect-aware) thay vì
  mặc định theo hệ 8 thanh điệu Hà Nội ở mọi nơi.
- **Đạo đức / phát hành.** Lăng kính này vô hại đối với việc phát hành
  CC-BY chỉ-đặc-trưng: probe của Shen không phát ra bất kỳ audio clip nào,
  chỉ có embedding pooled theo âm tiết và trọng số Ridge — hoàn toàn tương
  thích với ràng buộc "chỉ features+timestamps+labels+speaker-ids" của
  ViEmoSpeech. Không có vấn đề quyền riêng tư trẻ em (các corpus giọng đọc
  đều là người lớn), nên không có gì mới cần giảm thiểu ngoài quy tắc về
  tính hợp pháp của media (media-legality) tiêu chuẩn.
- **Lưu ý về tính hợp lệ của nhiệm vụ (task-validity).** Bài báo nói về
  **thanh điệu từ vựng**, không phải cảm xúc. Giá trị chuyển giao của nó
  cho ViEmoSpeech mang tính *cơ chế* (mechanistic) (thanh điệu và cảm xúc
  cùng chia sẻ kênh phonation; do đó hai thứ này cạnh tranh nhau), không
  phải là một kết quả SER trực tiếp. Mọi ứng dụng ở trên đều được đặt
  trong khung "nền tảng ngữ âm" (the phonetic substrate), còn bản thân sự
  cạnh tranh vẫn là điều ViEmoSpeech phải tự đo lường — Shen chỉ cung cấp
  tiền đề và công cụ.

### Hạn chế & câu hỏi mở đối với ViEmoSpeech

- **Mâu thuẫn/khoảng trống #1 — tiền đề "phonation-heavy" là *suy luận*,
  không phải *đo lường*.** Shen chưa bao giờ chạy một probe đặc trưng
  phonation: bài báo suy luận ra sự phụ thuộc vào phonation của tiếng Việt
  từ (a) việc bộ mã hóa tập trung vào F0 **không chuyển giao** được từ
  Quan Thoại sang tiếng Việt và (b) một **trích dẫn tới Brunelle (2009)**.
  *Không có* thí nghiệm nào trong bài báo này giải mã thanh điệu tiếng
  Việt từ các đặc trưng H1–H2/HNR/creak và cho thấy chúng vượt qua F0.
  **Đây chính xác là phép đo mà ViEmoSpeech nên sở hữu** — việc probe
  thanh điệu tiếng Việt (và cảm xúc) từ các đặc trưng phonation tường minh
  so với F0 sẽ là phép định lượng *trực tiếp đầu tiên*, biến tiền đề vay
  mượn của method paper thành một đóng góp gốc thay vì chỉ trích dẫn lại.
- **Mâu thuẫn/khoảng trống #2 — so với luận điểm "ngữ nghĩa chiếm ưu thế"
  (vn-12, Incongruent-Speech SLM).** vn-12 lập luận rằng phán đoán *cảm
  xúc* của SLM chủ yếu bị chi phối bởi ngữ nghĩa/văn bản; Shen thì cho
  thấy kênh *âm thanh* mã hóa thanh điệu tiếng Việt vượt xa baseline
  text-BERT và thông qua các tín hiệu **phonation** mà văn bản không thể
  biểu diễn được. Đối với tiếng Việt, hai luận điểm này không hẳn đối
  lập trực tiếp — chúng xác định chính căng thẳng mà ViEmoSpeech muốn
  định lượng: nếu cảm xúc thiên về ngữ nghĩa nhưng thanh điệu tiếng Việt
  (và phonation mang cảm xúc của nó) thiên về âm thanh, thì nhánh audio và
  nhánh text mang các tín hiệu **không thể thay thế lẫn nhau một phần**
  (partially non-substitutable), và việc mất dấu thanh khi ASR ở mức
  arousal cao *loại bỏ chính xác bằng chứng phonation chung* đó. Cả thiết
  kế fusion (V-A) lẫn thiết kế biểu diễn thanh điệu (V-D) đều phụ thuộc
  vào việc luận điểm này có đúng hay không, nên probe ở phần "Cách mỗi
  phần giúp ViEmoSpeech thành công" không phải là trang trí tùy chọn — nó
  phân xử một mâu thuẫn đang tồn tại.
- **Khoảng trống #3 — chồng chất confound mà chính Shen nêu ra (§7).** Bộ
  mã hóa tiếng Việt được huấn luyện trên **13k giờ** (≈13 lần các ngôn ngữ
  khác) và mô hình tiếng Quảng Đông khác biệt cả về **kiến trúc
  (conformer, 180M)** *lẫn* kích thước dữ liệu — vì vậy kết quả "tiếng
  Quảng Đông khái quát hóa sang tiếng Việt, tiếng Quan Thoại thì không" bị
  vướng víu (entangled) với dữ liệu/kiến trúc, chứ không thuần túy là do
  tính có-thanh-điệu. ViEmoSpeech không được trích dẫn quá mức phát hiện
  về sự chuyển giao từ tiếng Quảng Đông như bằng chứng sạch; các trích dẫn
  *an toàn* là (i) thanh điệu tiếng Việt ≠ chỉ dựa vào F0 và (ii) fine-tune
  ASR trên một ngôn ngữ có thanh điệu làm tăng cường mã hóa thanh điệu.
- **Không có con số cụ thể.** Vì mọi độ chính xác chỉ tồn tại dưới dạng
  biểu đồ, ViEmoSpeech không thể trích dẫn một con số cụ thể "độ chính xác
  probing thanh điệu tiếng Việt = X%" từ bài báo này. Bất kỳ con số như
  vậy trong method paper đều phải đến từ việc ViEmoSpeech *tự* chạy lại
  probe trên chính bộ mã hóa của mình — vốn cũng chính là mục đích sử
  dụng dự kiến.
- **Câu hỏi mở so với kế hoạch riêng của ViEmoSpeech.** ViEmoSpeech dự
  định **gán nhãn và mã hóa thanh điệu âm tiết một cách tường minh**. Shen
  cho thấy một bộ mã hóa SSL đóng băng *đã* nắm bắt được thanh điệu ở các
  lớp giữa mà không cần nhãn — vì vậy một head nhãn thanh điệu tường minh
  có thể là **dư thừa** so với bộ mã hóa audio, hoặc nó có thể đóng vai
  trò như một **phụ trợ/regularizer hữu ích** buộc không gian con
  phonation phải tách biệt khỏi không gian con cảm xúc. Điều nào đúng vẫn
  chưa được kiểm chứng ở đây; một ablation V-D (có/không có head thanh
  điệu, đo độ chính xác của nhánh cảm xúc và mức chồng lấn không gian con
  thanh điệu/arousal) sẽ trả lời được liệu công sức gán nhãn có xứng đáng
  hay không.
