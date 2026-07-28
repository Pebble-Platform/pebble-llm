# Paper vn-11 — THAI-SER: Thai Speech Emotion Recognition Corpus

> Bản dịch tiếng Việt của [11-thai-ser-corpus.md](11-thai-ser-corpus.md) — cập nhật 2026-07-10.

- **Tác giả:** Jilamika Wongpithayadisai, Chompakorn Chaksangchaichot, Soravitt Sangnark, Patawee Prakrankamanant, và cộng sự.
- **Venue / năm:** arXiv preprint, 2025
- **Liên kết:** abs https://arxiv.org/abs/2507.09618 · PDF `pdfs/11-thai-ser-corpus.pdf`
- **Nhóm:** vietnamese-ser / tiền lệ ngữ liệu gần nhất cho ngôn ngữ có thanh điệu

**Tóm tắt:** Ngữ liệu SER tiếng Thái quy mô đáng kể đầu tiên — 41h36m, 27,854
câu nói (utterances), 200 diễn viên, 5 cảm xúc, kịch bản sẵn + ứng khẩu, gán
nhãn qua crowdsourcing, giấy phép CC-BY-SA 4.0.

**Mức độ liên quan với ViEmoSpeech:** Tiền lệ công bố gần nhất cho "ngữ liệu
SER cho một ngôn ngữ có thanh điệu với giấy phép rõ ràng" — điểm so sánh thiết
kế trực tiếp cho việc định vị bài báo ngữ liệu (V-H): diễn viên/kịch bản so
với thoại phim truyền hình "found" (thu thập tự nhiên) của chúng tôi; giao
thức gán nhãn và định dạng phát hành của họ là các điểm tham chiếu.

> Stub được tạo 2026-07-10 (task `docs/tasks/paper-deep-analysis.md`); đang chờ đọc sâu.

## Deep research — đọc toàn văn PDF (2026-07-10)

### Ghi chú về nguồn truy cập

Đã đọc toàn văn PDF cục bộ (`pdfs/11-thai-ser-corpus.pdf`, arXiv:2507.09618v1,
13/07/2025) qua `pdftotext` — Abstract, §1 Introduction + Table 1 (bản đồ ngữ
liệu ngành), §2 Corpus design (diễn viên, môi trường, các phiên kịch
bản/ứng khẩu, căn chỉnh), §3 Annotation (kiểm soát chất lượng crowdsourcing,
pretest, độ tin cậy), §4 Data evaluation (đồng thuận đa số, Krippendorff α,
HRA, Tables 8–11), §5 Downstream experiments (chia tập, baseline CNN+LSTM,
Tables 12–16), §6 Discussion, §7 Conclusion. **Không tồn tại phiên bản venue
riêng biệt** — đây là bản preprint arXiv chưa có công bố tạp chí/hội nghị nào,
nên arXiv v1 là văn bản có thẩm quyền. Các con số nổi bật đã được đối chiếu
chéo qua web với hai nguồn độc lập:
- Truy vấn `THAI-SER Thai Speech Emotion Recognition corpus 27854 utterances 200
  actors Krippendorff alpha` → abstract arXiv (https://arxiv.org/abs/2507.09618)
  xác nhận 41h36m / 27,854 câu nói / 100 phiên ghi âm / 200 diễn viên (112F/88M)
  / 5 cảm xúc / α 0.692 / HRA 0.772 / CC-BY-SA 4.0. ✔
- Cơ chế phát hành (V-H, có tính quyết định): HuggingFace `airesearch/thai-ser`
  (https://huggingface.co/datasets/airesearch/thai-ser) xác nhận **bản thân
  audio được phát hành** (FLAC, các kênh mic_clip/mic_con/mic_middle/mic_zoom)
  + nhãn theo dòng (assigned_emo, majority_emo, phản hồi thô) + metadata
  (phiên/diễn viên/giới tính/tuổi/phòng), ~27,900 dòng, CC-BY-SA-4.0. ✔ Code
  tại github.com/tann9949/thaiser-experiments.

Các con số nội bộ bảng (Tables 8–16) chỉ tồn tại trong bản preprint có thẩm
quyền duy nhất này; không có phiên bản mâu thuẫn, nên được gắn nhãn ✔ khi
tự nhất quán, ≈ khi đọc từ biểu đồ.

### Bài báo thực sự làm gì

THAI-SER là một ngữ liệu SER tiếng Thái xây dựng từ đầu, thuộc dạng **diễn
xuất + gợi cảm xúc (acted+elicited)**, được thúc đẩy rõ ràng bởi việc tiếng
Thái là một **ngôn ngữ có thanh điệu** với đặc tính âm học của cảm xúc khác
biệt so với các ngữ liệu phương Tây (§1.1, trích dẫn Anolli 2008, Chong/Kim/
Davis 2015). Thiết kế và các con số:

- **Ngữ liệu (Abstract, §2, Table 8):** 41.61 h / 27,854 câu nói / **100
  phiên ghi âm** (mỗi phiên = một cặp diễn viên duy nhất) → **200 diễn viên**
  (112 nữ, 88 nam; 6 người không nhị giới/LGBTQ được ghi riêng; tuổi trung
  bình 29, khoảng 18–55). Sáu đạo diễn chuyên nghiệp. ✔
- **Hai tập con (§2.3):** *kịch bản (scripted)* (diễn theo kịch bản) — 3 câu
  cố định được thiết kế để trung tính về cảm xúc và "bao phủ nhiều thanh điệu,
  phụ âm và nguyên âm đôi tiếng Thái," được nói ở 2 mức cường độ × 2 lần thu ×
  5 cảm xúc = 60 câu/phiên; và *ứng khẩu (improvised)* (gợi cảm xúc, kiểu
  Busso-2008) — 15 tình huống trong 3 đợt, các cảnh song thoại 3 phút, thiết
  kế từ khóa chống học vẹt (anti-overfit). Giờ thu âm trong phòng thu chia
  13.69 kịch bản / 18.01 ứng khẩu; Zoom 4.02 / 5.89 (Table 8). ✔
- **Hai môi trường (§2.2):** **80 phiên phòng thu** (5 micro/phiên: 2 lavalier
  RODE + 2 cardioid WARM WA-47Jr + 1 micro trung tâm hình số 8; WAV 44.1
  kHz/16-bit) so với **20 phiên Zoom** (Zencastr 48 kHz, phòng không kiểm
  soát) được ghi trong thời gian COVID như một tập nhiễu/OOD (ngoài phân
  phối) có chủ đích. ✔
- **Cảm xúc (§2.3):** 5 lớp — trung tính (neutral), giận (angry), vui (happy),
  buồn (sad), **bực bội (frustrated)** (frustration được chọn vì liên quan
  đến ngữ cảnh tổng đài chăm sóc khách hàng). Cân bằng lớp bị lệch theo
  *chủ đích thiết kế* nghiêng về bực bội (30.52% số giờ) và trung tính
  (23.30%); giận chỉ 10.05%, vui 13.32%, buồn 13.33%, None (không đồng thuận)
  9.48% (Table 8). ✔
- **Gán nhãn (§3):** crowdsourcing **chỉ dựa trên audio** (chủ đích không có
  video, "chỉ dựa vào nhận diện cảm xúc từ âm thanh") trên hai nền tảng Thái
  (wang.in.th, HOPE). **Pretest**: video hướng dẫn + 10 mục sàng lọc + 1 câu
  hỏi bẫy ẩn "âm thanh động vật"; **984 trong số 1,759 người đăng ký đã vượt
  qua (56%)** (§3.2). ✔ Mỗi câu nói có **3–8 người gán nhãn** (chủ yếu là 3;
  lên đến 8 ở giai đoạn đầu để hiệu chỉnh hướng dẫn) (§4.1.2 fn3). Mỗi tác vụ
  10 mục có cài xen **câu nói vàng (gold utterances)** (được đạo diễn xác
  nhận, → điểm "độ tin cậy" theo từng người gán nhãn) và một **câu nói nhất
  quán (consistency utterance)** (bản trùng lặp, → "điểm nhất quán"); người
  gán nhãn thất bại ở bất kỳ tiêu chí nào <50% sẽ bị loại và câu nói được gán
  nhãn lại đến khi đạt ≥3 người (§3.4). Người gán nhãn bị giới hạn tối đa 30
  tác vụ để tránh thiên lệch do ghi nhớ tình huống. Cho phép chọn nhiều nhãn;
  các cảm xúc "khác" được ánh xạ thủ công vào 5 lớp (Table 7) hoặc giữ nguyên
  là `other`.
- **Độ tin cậy (§4, Table 9):** IAR (chỉ số đồng thuận liên đánh giá) =
  **Krippendorff's α với khoảng cách tập hợp MASI** (được chọn vì số lượng
  người gán nhãn thay đổi và nhãn có dạng tập hợp — Cohen's κ không áp dụng
  được). **α thô của toàn ngữ liệu = 0.413** (dưới ngưỡng 0.667); quét một
  ngưỡng lọc theo điểm đồng thuận, điểm cắt tối ưu là **0.71**, nâng α lên
  **0.692** và giữ lại **14,182 câu nói** (≈7h43m khả dụng). ✔ **Độ chính
  xác nhận diện của con người** (bỏ phiếu đa số so với cảm xúc mà diễn viên
  được gán): 0.592 thô → **0.772 sau khi lọc ở ngưỡng 0.71**. ✔ Kịch bản
  cường độ cao dễ nhất (HRA 0.883, α 0.712); kịch bản cường độ thấp khó nhất
  (HRA 0.690, α 0.622); ứng khẩu nằm giữa và có **IAR thô cao nhất** trong
  số mọi phong cách đơn lẻ (0.426→0.697) dù HRA thấp hơn (§4.2.2). Trung
  tính được nhận diện tốt nhất (78%→93%); **bực bội là lớp thất bại** (~62%),
  bị nhầm lẫn với giận và buồn (§4.2.3, Fig 9). Việc lọc gần như không khác
  biệt theo giới tính/tuổi của diễn viên (Table 10).
- **Baselines (§5, CNN+LSTM kiểu Etienne 2018; mel-filterbank 64 chiều, đoạn
  cắt 3 giây, VTLP, CMVN):** **8-fold độc lập người nói** trên 80 phiên phòng
  thu (10 phiên/fold; **Zoom bị loại khỏi huấn luyện, giữ lại làm tập thách
  thức**). 5 seed/fold. **Cả 5 cảm xúc: WA 59.80±2.91 / UA 57.81±4.20**;
  **4 cảm xúc cơ bản (bỏ bực bội): WA 67.34±3.05 / UA 62.61±3.19** (Table 12).
  ✔ Trên tập **Zoom** giữ lại, cùng mô hình sụp xuống còn **WA 46.64 / UA
  46.57** (tất cả cảm xúc) — mức sụt OOD khoảng 13 điểm. ✔ **Huấn luyện chỉ
  bằng kịch bản vượt trội hơn ứng khẩu hoặc toàn bộ** trên 4 cảm xúc cơ bản
  (**WA 73.99 so với 61.80 của ứng khẩu so với 67.34 của toàn bộ**, Table 13)
  — *ngược lại* với kết quả của IEMOCAP rằng "ứng khẩu là tốt nhất"
  (Neumann&Vu 2017), được lý giải là do câu kịch bản cố định cho nhãn sạch
  hơn. ✔ So sánh liên ngữ liệu (Tables 14–16): các mô hình huấn luyện trên
  THAI-SER chuyển giao tốt hơn sang Emo-DB/EMOVO so với các mô hình huấn
  luyện trên IEMOCAP ngay cả sau khi cắt tỉa để cân bằng số giờ/số người nói.

### Các phần trực tiếp hữu ích cho ViEmoSpeech (gắn nhãn theo Decision ID)

1. **[V-H] Tiền lệ ngữ liệu ngôn ngữ có thanh điệu gần nhất, đánh đổi tính
   hợp pháp ngược chiều.** THAI-SER là điểm tương đồng đã công bố gần nhất
   (ngôn ngữ Đông Nam Á có thanh điệu, giấy phép rõ ràng) nhưng nằm ở *cực
   đối lập* trên trục tự nhiên/hợp pháp: diễn viên chuyên nghiệp có đồng ý
   → **bản thân audio có thể phát hành theo CC-BY-SA-4.0** (FLAC trên
   HuggingFace). ViEmoSpeech dùng thoại *found* (thu thập tự nhiên) từ phim
   truyền hình có bản quyền → **chỉ phát hành đặc trưng (feature-only) theo
   CC-BY, không bao giờ phát hành media**. Table 1 của THAI-SER (bản đồ ngữ
   liệu ngành: Emo-DB/IEMOCAP/CREMA-D/RAVDESS/MSP-*/LSSED với loại
   ∈{acted, elicited, natural}) chính là bảng định vị mà bài báo ngữ liệu
   của ViEmoSpeech nên mở rộng, thêm cột "Phát hành = chỉ đặc trưng / giữ
   lại media" mà không ngữ liệu nào được liệt kê cần đến và đó chính là
   ràng buộc định danh của ViEmoSpeech. Cách phân loại ở §1.1 của họ (tự
   nhiên = rủi ro riêng tư/bản quyền vs diễn xuất = kiểm soát được nhưng
   không tự nhiên vs gợi cảm xúc = ở giữa) là một khung sẵn có: ViEmoSpeech
   là *tự nhiên/found* (ô có độ tự nhiên cao nhất, rủi ro pháp lý cao nhất
   của họ) nhưng trung hòa rủi ro bằng cách chỉ phát hành đặc trưng — một
   điểm thiết kế mà ngữ liệu diễn xuất của họ không phải giải quyết.
   **Rủi ro chuyển giao:** quy mô của họ (41.6 h / 27,854 câu nói / 200
   người nói) và cân bằng lớp đạt được vì ghi âm diễn xuất rẻ để mở rộng
   quy mô; pipeline thoại found của ViEmoSpeech (3,611 câu nói / 2 series
   hiện tại, mục tiêu P1 ~18k/23.8h) sẽ nhỏ hơn và *mất cân bằng người nói
   theo nguồn*: nên trích dẫn THAI-SER làm thước đo quy mô, không phải mục
   tiêu cần đạt được.

2. **[V-E] Sơ đồ kiểm soát chất lượng crowdsourcing = giao thức cụ thể để
   ghép vào ADR-002/ADR-003.** Cỗ máy tạo độ tin cậy của họ có thể ghép trực
   tiếp vào công cụ gán nhãn thủ công của ViEmoSpeech: **cài xen mẫu vàng
   (gold-standard salting)** (mục không mơ hồ được đạo diễn xác nhận → điểm
   tin cậy), **bản trùng nhất quán (consistency duplicates)** (→ điểm nhất
   quán), **ngưỡng đáng tin cậy >50% trên cả hai tiêu chí kèm tự động loại +
   gán lại đến ≥3**, **pretest với câu hỏi bẫy ẩn** (tỉ lệ đỗ 56%), và **bộ
   lọc điểm đồng thuận theo từng câu nói → α toàn cục** (α thô 0.413 →
   0.692 ở ngưỡng cắt 0.71). Lập luận về việc κ không áp dụng được của họ
   có ý nghĩa với ViEmoSpeech: số người gán nhãn biến thiên + cảm xúc chọn
   nhiều nhãn ⇒ **dùng Krippendorff α với khoảng cách tập MASI, không dùng
   Cohen κ** — và lưu ý rằng ViEmoSpeech hiện đang báo cáo κ đồng thuận
   giáo viên (0.675/0.857 trong commit log); α+MASI mới là công cụ đúng
   đắn một khi chuyển sang V/A+distress đa-người-gán-nhãn của con người.
   **Rủi ro chuyển giao:** ngưỡng 0.71 của họ loại bỏ ~49% số câu nói
   (27,854→14,182) để đạt α 0.692; ViEmoSpeech không thể chấp nhận việc bỏ
   đi một nửa ngữ liệu found vốn đã khó lấp đầy sàn lớp hiếm (ADR-002,
   ≥50 clip), nên nên áp dụng *cơ chế* (điểm đồng thuận theo từng câu nói,
   giữ lại nhãn mềm) nhưng giữ lại các clip đồng thuận thấp với xử lý mềm/
   curriculum (câu hỏi mở của chính họ ở §6.4) thay vì lọc cứng.

3. **[V-G] Giao thức chia tập độc lập người nói + tập thách thức OOD trung
   thực — một khuôn mẫu trực tiếp.** Đánh giá của họ chính xác là ADR của
   ViEmoSpeech: **k-fold độc lập người nói** (các fold được cắt theo
   *phiên/cặp người nói*, val và test không bao giờ chia sẻ người nói với
   train), **độ chính xác có trọng số + không trọng số** báo cáo cùng
   **độ lệch chuẩn 5-seed**, và một **tập chuyển dịch phân phối được giữ
   lại có chủ đích** (Zoom) chưa từng thấy trong huấn luyện. Đây chính là
   trích dẫn mà ViEmoSpeech cần cho **tập gold giữ lại nguyên series**
   (ADR-002) và các phần chia độc lập người nói (I-invariant): THAI-SER
   chứng minh khoảng cách OOD bằng thực nghiệm (67.3→46.6 WA phòng thu→
   Zoom). Nó cũng cung cấp một *điểm neo thực tế cho baseline*: một
   CNN+LSTM đủ năng lực trên ngữ liệu diễn xuất 5 lớp tiếng Thái sạch đạt
   **WA ~60 / UA ~58** — vậy nên các con số 7 lớp thoại found của
   ViEmoSpeech nên được đọc so với con số này, không phải so với các con số
   0.86–0.87 bị rò rỉ (leak-inflated) của vn-08/vn-10. **Rủi ro chuyển
   giao:** chỉ số UA/WA của họ dành cho các lớp diễn xuất tương đối cân
   bằng; ngữ liệu found của ViEmoSpeech cần macro-F1 + CCC (V/A) +
   recall@floor (distress), nên chuyển giao *kỷ luật chia tập* và *báo cáo
   phương sai theo seed*, không phải lựa chọn chỉ số.

4. **[V-D] Ngữ liệu ngôn ngữ có thanh điệu chưa bao giờ đo tone×emotion —
   một khoảng trống không gian đổi mới.** THAI-SER *tự thúc đẩy* dựa trên
   tính thanh điệu của tiếng Thái (§1.1) và *thiết kế các câu kịch bản để
   "bao phủ nhiều thanh điệu, phụ âm và nguyên âm đôi tiếng Thái"* (§2.3.1)
   — nhưng **không nơi nào trong bài báo phân tích hay đo lường tương tác
   tone×emotion**; thanh điệu chỉ được dùng để cân bằng ngữ âm cho các câu
   kịch bản, sau đó bị bỏ qua. Nhầm lẫn bực bội↔giận↔buồn (Fig 9) của họ
   chỉ được bàn luận thuần túy như cường độ, không bao giờ như sự cạnh
   tranh giữa đường nét F0/thanh điệu. **Đây là bằng chứng rõ ràng nhất
   cho thấy ngữ liệu SER có thanh điệu gần nhất vẫn để ngỏ khẳng định
   trọng tâm của ViEmoSpeech (thanh điệu nặng về đặc tính phát âm, cạnh
   tranh với kênh của cảm xúc — Shen vn-06).** Hành động cụ thể: ViEmoSpeech
   nên trích dẫn THAI-SER như "một ngữ liệu SER ngôn ngữ có thanh điệu thừa
   nhận thanh điệu quan trọng nhưng chưa bao giờ định lượng sự cạnh tranh
   kênh tone-emotion," định vị hình phân tích tone×emotion (nền tảng V-D)
   như đóng góp mà THAI-SER đã gợi ý nhưng chưa thực hiện. **Rủi ro chuyển
   giao:** tiếng Thái có 5 thanh điệu và không nặng về đặc tính phát âm
   bằng tiếng Việt (thanh điệu tắc thanh hầu của tiếng Việt mang tải trọng
   chất giọng, Brunelle 2009); *khoảng trống* thì có thể chuyển giao, nhưng
   không được khẳng định rằng ngữ liệu của họ có thể đã đo được hiệu ứng
   phát âm đặc thù tiếng Việt.

### Từng phần giúp ViEmoSpeech thành công như thế nào

- **V-H →** Xây dựng bảng định vị bài báo ngữ liệu bằng cách mở rộng Table 1
  của THAI-SER với hai cột mà THAI-SER không cần — *Định dạng phát hành*
  (đặc trưng+dấu thời gian+nhãn so với toàn bộ audio) và *Tính hợp pháp
  nguồn* (found/có bản quyền so với có đồng ý). ViEmoSpeech chiếm ô "tự
  nhiên + có thanh điệu + chỉ đặc trưng-CC-BY" vốn trống trong toàn bộ bản
  đồ của họ (và của cả ViSEC/VLSP/VNEMOS). Sản phẩm cụ thể: dòng so sánh
  trong phần mở đầu bài báo ngữ liệu + phần đặc tả phát hành trích dẫn
  THAI-SER làm bằng chứng rằng một ngữ liệu SER có thanh điệu, giấy phép
  sạch có thể công bố được, đồng thời phân biệt ở cơ chế giữ lại media.
- **V-E →** Ghép sơ đồ vàng+nhất quán+pretest vào công cụ gán nhãn
  (`tools/labeler/`): thêm **clip vàng** được đạo diễn/chuyên gia xác nhận
  và **clip nhất quán trùng lặp** được cài xen vào mỗi lô gán nhãn thủ công,
  tính độ tin cậy & nhất quán theo từng người gán nhãn, và chặn ở ngưỡng
  >50%; chuyển chỉ số độ tin cậy được báo cáo từ κ sang **Krippendorff α +
  MASI** cho các chiều V/A+distress chọn nhiều nhãn. Giữ lại ma trận nhãn
  mềm (§6.4 của họ, "lên đến 8 người gán nhãn → nhãn mềm phong phú hơn
  IEMOCAP") cho mục tiêu hiệu chỉnh đầu distress trong tương lai.
- **V-G →** Áp dụng nguyên vẹn cách cắt fold độc lập người nói theo phiên
  và báo cáo độ lệch chuẩn 5-seed của họ cho benchmark ViEmoSpeech; đăng ký
  tập giữ lại nguyên series như tương đương với tập thách thức Zoom của họ
  (một lát cắt chuyển dịch phân phối được *thừa nhận* và báo cáo riêng).
  Dùng con số WA~60/UA~58 diễn xuất sạch 5 lớp của họ làm chú thích "trần
  baseline trung thực" cạnh các dòng bị gắn cờ rò rỉ vn-08 (86.6) / vn-10
  (0.87) trong bảng baseline.
- **V-D →** Neo hình phân tích probing tone×emotion (probe Ridge theo tầng
  kiểu Shen, bin cường độ (arousal) × nhãn thanh điệu, phoneme-disjoint)
  làm *đóng góp trung tâm*, định khung so với THAI-SER: "ngay cả ngữ liệu
  SER ngôn ngữ có thanh điệu gần nhất cũng thiết kế cho độ bao phủ thanh
  điệu nhưng chưa bao giờ đo tương tác kênh tone-emotion." Một câu trong
  related work; khẳng định có thể đo lường là của ViEmoSpeech.

### Lăng kính sức khỏe tâm thần trẻ em (tính chuyển giao của ViEmoSpeech)

ViEmoSpeech không hướng tới trẻ em; lăng kính liên quan là trục **tính hợp
pháp/tự nhiên/đồng ý**, và THAI-SER là điểm so sánh sắc nét nhất trên trục đó.

- **Sự đồng ý + audio có thể phát hành chính là điều ViEmoSpeech không thể
  có.** Toàn bộ cỗ máy QC của THAI-SER (câu nói vàng do đạo diễn chọn, diễn
  viên được hướng dẫn và thu lại đến khi đạo diễn chấp thuận, cảm xúc *được
  gán* làm ground-truth theo từng câu nói) đặt nền trên **thoại diễn xuất có
  đồng ý với nhãn dự định đã biết**. ViEmoSpeech có thoại phim truyền hình
  *found*, **không có ground truth được gán** — ý định của diễn viên không
  thể phục hồi, nên ViEmoSpeech không có chỉ số "HRA so với cảm xúc được gán"
  khả dụng và phải xem mọi nhãn là chỉ mang tính cảm nhận (perceived-only).
  Biện pháp giảm thiểu: các nhãn con người/giáo viên của ViEmoSpeech *chính
  là* đa số cảm xúc được cảm nhận (maj-vote của họ), nên báo cáo **IAR
  (α+MASI) như chỉ số độ tin cậy trung thực và không bao giờ là một "độ
  chính xác"** — điều này phù hợp với bất biến của repo "κ đồng thuận giáo
  viên không bao giờ được báo cáo như độ chính xác."
- **Chỉ phát hành đặc trưng là sự thay thế đạo đức/pháp lý cho audio mở của
  họ.** THAI-SER có thể phát hành FLAC vì 200 người trưởng thành đã đồng ý;
  ViEmoSpeech phát hành đặc trưng+dấu thời gian+nhãn+id người nói chính vì
  các diễn viên trong phim truyền hình đã **không** đồng ý cho một ngữ liệu
  nghiên cứu và media có bản quyền. Sự đối lập với THAI-SER là cách rõ ràng
  nhất để giải thích *tại sao* việc phát hành của ViEmoSpeech được định hình
  như vậy — đây là cùng một hạng mục ngữ liệu (thoại cảm xúc diễn xuất/kịch
  tính) nhưng thiếu sự đồng ý/quyền sở hữu vốn cho phép phát hành media.
- **Sự mơ hồ của bực bội là một cảnh báo cho proxy distress (V-F).** Lớp bị
  nhầm lẫn nhiều nhất của họ (bực bội, ~62% HRA, hòa lẫn vào giận+buồn) cho
  thấy cảm xúc tiêu cực có cường độ thấp không ổn định về mặt cảm nhận ngay
  cả với những người đánh giá chú tâm trên audio sạch. **Cờ distress** của
  ViEmoSpeech (proxy phim diễn xuất, mục tiêu sàn recall) nằm trong cùng
  vùng nguy hiểm về nhận thức — nên dự kiến độ đồng thuận thấp của con
  người ở ranh giới distress và thiết kế xử lý sàn-recall + nhãn mềm cho
  phù hợp, thay vì giả định tồn tại một nhãn distress rõ ràng.

### Hạn chế & câu hỏi mở cho ViEmoSpeech

- **Mâu thuẫn với IEMOCAP / với tiền đề thoại found của ViEmoSpeech (§5.2.1,
  Table 13):** THAI-SER thấy **kịch bản > ứng khẩu** (WA 73.99 so với
  61.80), *ngược lại* với phát hiện của IEMOCAP rằng thoại ứng khẩu/tự nhiên
  huấn luyện mô hình SER tốt hơn. Lời giải thích của họ — câu cố định cho
  nhãn sạch hơn — đi *ngược lại* với đặt cược cốt lõi của ViEmoSpeech rằng
  thoại phim *tự nhiên* found đáng để đánh đổi độ phức tạp pháp lý.
  ViEmoSpeech phải trả lời trực tiếp câu hỏi này: liệu thoại tự nhiên found
  có giá trị hơn (phong phú hơn, trong-điều-kiện-tự-nhiên) hay chỉ là dữ
  liệu nhãn nhiễu hơn mà một ngữ liệu diễn xuất kịch bản sẽ vượt trội hơn?
  Lập trường trung thực là ViEmoSpeech đánh đổi độ sạch nhãn lấy tính hợp
  lệ sinh thái và khả năng đo tone×emotion, và phải *chứng minh* lợi thế
  của thoại tự nhiên, không phải giả định nó.
- **Mâu thuẫn với sự lạc quan baseline của vn-08/vn-10:** trần của THAI-SER
  trên ngữ liệu diễn xuất sạch 5 lớp là **WA ~60 / UA ~58** dưới một phần
  chia *độc lập người nói đúng đắn*; vn-08 (86.6%) và vn-10 (0.87) báo cáo
  cao hơn nhiều trên tiếng Việt dưới các giao thức rò rỉ người nói
  (speaker-leaky). Đây là bằng chứng củng cố rằng các con số VN đó bị thổi
  phồng và rằng kết quả 7 lớp độc lập người nói của ViEmoSpeech sẽ trông
  "kém hơn" trong khi trung thực hơn — con số của THAI-SER là điểm neo so
  sánh công bằng.
- **Ngữ liệu có thanh điệu bỏ qua thanh điệu (khoảng trống so với V-D / so
  với Shen vn-06):** như trên — THAI-SER chưa bao giờ đo tone×emotion dù
  tự thúc đẩy dựa trên tính thanh điệu. Câu hỏi mở mà ViEmoSpeech sở hữu:
  liệu sự khác biệt âm học kịch bản-so-với-ứng khẩu có tương tác với sự
  hiện thực hóa đường nét thanh điệu dưới tác động của cảm xúc hay không?
  THAI-SER có dữ liệu (các câu kịch bản cân bằng thanh điệu) nhưng chưa
  bao giờ đặt câu hỏi này.
- **Lọc cứng loại bỏ một nửa ngữ liệu (§4.2.1, §6.4):** ngưỡng cắt 0.71 của
  họ làm giảm từ 27,854→14,182. ViEmoSpeech không thể sao chép cách này ở
  quy mô hiện tại; câu hỏi mở mà họ nêu ra (nhãn mềm / curriculum đồng
  thuận thấp, Lotfian&Busso 2019b) là con đường tốt hơn cho một ngữ liệu
  found khan hiếm dữ liệu — ViEmoSpeech nên xem đây là điều cần giải quyết,
  không phải một công thức đã được giải quyết.
- **Cũng đáng lưu ý — EMOLA (ngữ liệu cảm xúc phim truyền hình "Lakorn"
  tiếng Thái, tìm thấy qua tra cứu):** một nỗ lực trước đó của Thái với
  thoại cảm xúc kịch tính *found* đã tồn tại, tức là hướng đi phim kịch
  found không phải chưa từng có tiền lệ ngay cả ở Thái; ViEmoSpeech nên rà
  soát các lựa chọn giấy phép/phát hành của EMOLA như một điểm so sánh V-H
  bổ sung (chưa đọc ở đây; được gắn cờ để theo dõi tiếp).
