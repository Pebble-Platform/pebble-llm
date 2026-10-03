# Paper vn-10 — Emotional Vietnamese Speech-Based Depression Diagnosis Using Dynamic Attention Mechanism

> Bản dịch tiếng Việt của [10-vn-depression-dynamic-cbam.md](10-vn-depression-dynamic-cbam.md) — cập nhật 2026-07-10.

- **Tác giả:** Quang-Anh N.D., Manh-Hung Ha, Thai Kim Dinh, Minh-Duc Pham, Ninh Nguyen Van (VNU Hà Nội)
- **Venue / năm:** arXiv Dec 2024; chương sách Springer (10.1007/978-3-032-00267-9_23)
- **Links:** abs https://arxiv.org/abs/2412.08683 · PDF `pdfs/10-vn-depression-dynamic-cbam.pdf`
- **Nhóm:** vietnamese-ser / VNEMOS-line baseline, distress-adjacent

**Tóm tắt:** Dynamic-CBAM (omni-dimensional dynamic convolution attention) +
BiGRU trên bộ dữ liệu VNEMOS (250 clip, cấu hình tốt nhất chỉ dùng MFCC) cho
bài toán phân loại cảm xúc 5 lớp như một proxy cho chẩn đoán trầm cảm;
UA 0.87 / WA 0.86 / F1 0.87.

**Mức độ liên quan tới ViEmoSpeech:** Một con số baseline audio-only cho tiếng
Việt; bằng chứng cho thấy nhóm tác giả VNEMOS chưa khai thác hướng bimodal
hay tone-aware framing. Cách đóng khung "cảm xúc như proxy cho trầm cảm" của
họ là một ví dụ đối chứng cảnh báo cho kỷ luật "distress-là-proxy" của chúng
ta (V-F, honest framing).

> Stub được tạo 2026-07-10 (task `docs/tasks/paper-deep-analysis.md`); deep-read đang chờ.

## Deep research — đọc toàn văn PDF (2026-07-10)

### Ghi chú về nguồn truy cập

Đã đọc toàn bộ PDF local `pdfs/10-vn-depression-dynamic-cbam.pdf` (arXiv:2412.08683v1,
`cs.SD`, 11 Dec 2024) qua `pdftotext` — phương pháp, dữ liệu, toàn bộ phương trình (Eq 1–9), và
mọi bảng (Table 1–4). Bài báo dài 9 trang, một nghiên cứu duy nhất. **Bản đăng chính
thức/venue** là một chương sách Springer (kỷ yếu dòng ICAMCS 2024, DOI
10.1007/978-3-032-00267-9_23); toàn văn Springer bị paywall (link redirect tới
`idp.springer.com` auth) — **không bypass**.

Đã kiểm chứng trên web các con số cốt lõi (load-bearing) đối chiếu với các nguồn không bị
paywall:
- Headline UA/WA/F1 = 0.87/0.86/0.87 trên VNEMOS — **✔ được xác nhận**. Truy vấn: *"Emotional
  Vietnamese Speech-Based Depression Diagnosis Dynamic Attention Mechanism VNEMOS UA 0.87"* →
  cả `https://arxiv.org/abs/2412.08683` lẫn đoạn abstract của Springer đều báo cáo
  "0.87 UA, 0.86 WA, 0.87 F1-score". Preprint và venue khớp nhau; không tìm thấy sai lệch.
- Bậc thang ablation đầy đủ ở Table 4 (0.73 → 0.87) — **✔ được xác nhận** đối chiếu với arXiv
  HTML (`https://arxiv.org/html/2412.08683v1`), tái hiện y hệt từng dòng so với PDF local.
- VNEMOS = 250 đoạn / ~30 phút / 27 phim-series-live-show / 5 cảm xúc — **✔ được xác nhận**
  trong văn bản và đối chiếu chéo với chính bài báo gốc của bộ dữ liệu (VNEMOS, ICDV 2024,
  10.1109/icdv61346.2024.10616411, `https://ieeexplore.ieee.org/document/10616411/`). Có một
  sai lệch chéo-nguồn nhỏ: các bản tóm tắt trên web của *bài báo VNEMOS ICDV* trích dẫn "89%
  accuracy" cho DNN gốc, trong khi bài báo về trầm cảm này báo cáo baseline VNEMOS trước đó là
  UA 0.85 ở dòng "Anh, N. Q., et al. [20]" trong Table 4 — **≈ xấp xỉ** (khác metric/cấu hình;
  không load-bearing ở đây).

### Bài báo thực sự làm gì

**Claim so với nội dung thực tế.** Tiêu đề và abstract quảng bá "chẩn đoán trầm cảm". Mô hình
thực tế lại là một **bộ phân loại cảm xúc diễn xuất 5 lớp** (giận dữ, vui, buồn, sợ hãi, trung
tính) huấn luyện bằng cross-entropy đơn thuần (Eq 6). **Trầm cảm chưa bao giờ được vận hành hóa
(operationalized)** — không có nhãn trầm cảm, không có neo lâm sàng PHQ/BDI, không có quy tắc
ánh xạ cảm xúc→trầm cảm, và không có dữ liệu từ người mắc trầm cảm. Cách đóng khung trầm cảm
hoàn toàn mang tính tu từ: phần Introduction khẳng định người trầm cảm "nói chậm, run rẩy, và
mất cảm xúc", còn Conclusion gọi mô hình cảm xúc là "bước tiền đề" hướng tới một hệ thống chẩn
đoán trầm cảm trong tương lai. §4 thậm chí liệt kê các lớp cảm xúc không nhất quán ("giận dữ,
buồn, vui, lo âu, và trung tính" — "lo âu" bị hoán đổi cho "sợ hãi"), cho thấy chính bộ nhãn cảm
xúc cũng được xử lý lỏng lẻo. Đây là điều quan trọng nhất mà bài báo cho chúng ta thấy, và nó là
một ví dụ *tiêu cực* (xem V-F bên dưới).

**Kiến trúc.** Hai thiết kế được so sánh (Fig 3):
- (a) **Dual-stream**: stream 1 = waveform thô (5 giây @ 16 kHz) → bốn khối CBM 1D
  (Conv-BatchNorm-MaxPool) → Bi-GRU (Eq 5); stream 2 = MFCC → bốn khối CBM 2D →
  **Dynamic-CBAM** → nối (concatenate) → dense classifier (đầu ra 0–4).
- (b) **Proposed / cuối cùng**: **chỉ dùng MFCC, single stream** — bỏ nhánh waveform thô
  "để tránh các đột biến nhiễu (spike-noise) làm hỏng dữ liệu trong waveform thô."
- **Dynamic-CBAM** = CBAM chuẩn (channel attention Eq 1 + spatial attention Eq 2, kết hợp ở
  Eq 3) với phép convolution của spatial-attention được thay bằng **ODConv** (omni-dimensional
  dynamic convolution, Eq 4) để trọng số kernel phụ thuộc vào đầu vào (input-dependent).

**Dữ liệu & tiền xử lý.** VNEMOS: 250 clip, tổng ~30 phút, từ 27 phim / series / live show
(pha trộn tự nhiên + diễn xuất). **Mirror-padding** (lặp lại clip) đệm các đoạn ngắn để đạt
cửa sổ 5 giây. Văn bản tiền xử lý ghi "resample với 160kHz … windows với 8kHz" — rõ ràng là
lỗi đánh máy của 16 kHz sample rate; không nên hiểu theo nghĩa đen.

**Giao thức huấn luyện / đánh giá.** epoch=100, lr=0.001, batch=32, Adam, cross-entropy;
RTX 2080 Ti. **5-fold cross-validation phân tầng, phân tầng theo lớp** (§3.3). Metric: UA
(unweighted / macro accuracy), WA (weighted accuracy), precision/recall/F1 (Eq 7–9).

**Kết quả (Table 4, trung bình 5-fold CV) — ✔ được xác nhận:**

| Cấu hình | Đầu vào | UA | WA | F1 |
|---|---|---|---|---|
| One-stream | waveform | 0.73 | 0.72 | 0.73 |
| One-stream GRU | waveform | 0.80 | 0.79 | 0.80 |
| One-stream GRU | MFCC | 0.82 | 0.81 | 0.82 |
| One-stream Bi-GRU | waveform | 0.76 | 0.75 | 0.76 |
| Dual-stream Bi-GRU | waveform+MFCC | 0.84 | 0.83 | 0.84 |
| Dual-stream Dynamic-CBAM | waveform+MFCC | 0.85 | 0.85 | 0.85 |
| Dual-stream Dynamic-CBAM Bi-GRU | waveform+MFCC | 0.86 | 0.85 | 0.86 |
| **Proposed (chỉ MFCC)** | MFCC | **0.87** | **0.86** | **0.87** |
| Anh et al. [20] (VNEMOS trước đó) | MFCC | 0.85 | 0.83 | 0.85 |

Headline: mô hình **chỉ-MFCC vượt cấu hình dual-stream tốt nhất +0.01 UA** (0.87 so với 0.86);
việc thêm nhánh waveform thô chưa bao giờ giúp ích và thường làm giảm hiệu năng.

### Các phần hữu ích trực tiếp cho Pebble

1. **Khoảng trống trong cách đóng khung "cảm xúc-như-proxy-cho-trầm-cảm" — một anti-pattern
   về governance/labeling [V-F].** Bài báo này gán nhãn 5 cảm xúc diễn xuất và *khẳng định*
   mức liên quan tới trầm cảm mà không có bất kỳ liên kết lâm sàng hay dữ liệu từ quần thể
   trầm cảm nào. Đây là ví dụ overclaim rõ ràng nhất trong tập tài liệu tiếng Việt của chúng
   ta về đúng loại sai lầm mà distress head của ViEmoSpeech KHÔNG được mắc phải. Sản phẩm cụ
   thể: distress-head spec trong `docs/spec/capabilities/` và đoạn framing của method paper
   nên trích dẫn bài này làm đối chứng — "distress flag = proxy trên phim truyền hình diễn
   xuất, minh thị không phải là tín hiệu lâm sàng hay trầm cảm; chúng tôi không suy luận rối
   loạn tâm thần từ cảm xúc."
   **Rủi ro khi transfer:** không có về mặt kỹ thuật — chúng ta chỉ chuyển giao *bài học,
   không phải phương pháp*. Rủi ro nằm ở uy tín, nếu ViEmoSpeech trôi dạt theo hướng overclaim
   tương tự, điều mà bài báo này minh họa rất rõ.

2. **VNEMOS như một con số baseline audio-only cho tiếng Việt — nhưng là một con số *mềm*
   [V-G].** UA 0.87 / WA 0.86 / F1 0.87 là con số nên trích dẫn trong bảng baseline của chúng
   ta (cùng với 2412.09829 và 2604.01711). **Điểm then chốt là split ở đây là 5-fold CV phân
   tầng *theo lớp*, KHÔNG phải speaker-disjoint** (§3.3), trên chỉ 250 clip từ 27 nguồn với sự
   lặp lại diễn viên nặng nề trong từng nguồn — nên gần như chắc chắn cùng diễn viên xuất hiện
   ở cả train và test fold. Sản phẩm cụ thể: tài liệu eval-protocol `V-G` và bảng baseline phải
   ghi chú con số này là **"speaker-leaky, không so sánh được với holdout speaker-disjoint của
   chúng ta"** — một tham chiếu *bị thổi phồng do rò rỉ speaker (upper-bound-inflated)*, không
   phải một mức để cạnh tranh ngang hàng.
   **Rủi ro khi transfer:** cao. Một con số 0.87 đạt được dưới điều kiện rò rỉ speaker trên 250
   clip sẽ không trụ được qua một split speaker-disjoint; các con số tương đương của chúng ta
   sẽ trông thấp hơn, và điều đó là *đúng đắn*, không phải là thoái lui. Cần nêu rõ điều này ở
   bất cứ nơi nào con số xuất hiện.

3. **MFCC-only ≥ dual-stream với raw-waveform — một data point về lựa chọn feature [V-B].**
   Mô hình tốt nhất của họ bỏ nhánh waveform thô; mọi dòng có chứa waveform thô đều ≤ dòng
   chỉ-MFCC (Table 4). Họ quy nguyên nhân thất bại của nhánh waveform thô cho "spike-noise".
   Sản phẩm cụ thể: thí nghiệm audio-backbone `V-B` — bằng chứng yếu cho thấy trên các corpus
   phim truyền hình tiếng Việt nhỏ, các feature phổ được thiết kế thủ công (MFCC) có thể sánh
   ngang hoặc vượt một CNN raw-waveform được huấn luyện đồng thời (jointly-trained), nghĩa là
   một mô hình raw-audio không tự động tốt hơn khi dữ liệu khan hiếm.
   **Rủi ro khi transfer:** cao, và phần nào đi *ngược* lại kế hoạch của chúng ta. Kết quả này
   là của một 1D-CNN huấn luyện from-scratch trên 250 clip — nó không nói lên điều gì về các
   **pretrained** raw-waveform SSL encoder (WavLM / emotion2vec), vốn là điều mà V-B thực sự đề
   xuất. Nên đọc nó theo hướng "đừng huấn luyện một CNN raw-audio from-scratch trên corpus của
   chúng ta", chứ không phải "đừng dùng WavLM."

### Từng phần giúp Pebble thành công như thế nào

- **V-F / distress head.** Viết ngay cách đóng khung honest-proxy vào distress-head spec và
  trích dẫn bài báo này như một anti-pattern: phân loại cảm xúc trên media tiếng Việt diễn xuất
  không phải là phát hiện trầm cảm. Mục tiêu recall-floor của chúng ta được định nghĩa trên một
  *proxy distress trên phim truyền hình diễn xuất*; bất kỳ đoạn văn bản nào trong paper chạm tới
  tính hữu dụng lâm sàng đều nhận cùng một cảnh báo (hedge). Hành động: thêm một câu vào file
  capability của distress — "chúng tôi cố tình tránh phép suy luận cảm xúc→rối loạn tâm thần mà
  Quang-Anh et al. (2024) đã thực hiện, khi họ khẳng định chẩn đoán trầm cảm từ một mô hình cảm
  xúc diễn xuất 5 lớp mà không có neo lâm sàng nào."
- **V-G / giao thức đánh giá + baseline.** Thêm dòng này vào bảng baseline kèm cảnh báo rò rỉ,
  và dùng nó để *biện minh* cho giao thức speaker-disjoint + whole-series-holdout của chúng ta
  (ADR-002): sự đối lập "0.87 dưới class-stratified CV so với con số thấp-hơn-nhưng-trung-thực
  của chúng ta theo speaker-disjoint" tự nó là một luận điểm phương pháp luận trong method paper.
  Hành động: bảng baseline có thêm cột "split" để CV phân tầng-theo-lớp của VNEMOS được phân
  biệt rõ ràng với các con số speaker-disjoint của chúng ta.
- **V-B / audio feature.** Chạy thí nghiệm ablation về feature với phép so sánh *đúng*: pretrained
  WavLM/emotion2vec so với MFCC so với fusion của chúng — *không phải* raw-CNN-from-scratch so
  với MFCC. Kết quả của họ chỉ cho phép kết luận "MFCC là một baseline rẻ và mạnh trên dữ liệu
  tiếng Việt nhỏ"; nên giữ một nhánh baseline MFCC để có thể chỉ ra liệu các feature SSL có thực
  sự vượt trội hơn trong chế độ (regime) của chúng ta hay không. Một thí nghiệm đáng chạy: liệu
  lợi thế của MFCC ở đây có phải vì các CNN raw-waveform from-scratch bị overfit trên 250 clip
  hay không (điều mà backbone pretrained của chúng ta né tránh được).

### Góc nhìn sức khỏe tâm thần trẻ em

- **Tính hợp lệ khi transfer: thấp với vai trò corpus, hữu ích như một lời cảnh báo.** VNEMOS
  là media diễn xuất/tự nhiên của người lớn Việt Nam (phim, series, live show), 5 cảm xúc cơ
  bản, không có trẻ em, không có nhãn distress/lâm sàng. Không có gì transfer trực tiếp sang
  đối tượng trẻ em; ngay cả *taxonomy cảm xúc* (5 cơ bản) cũng hẹp hơn scheme 7-lớp + V/A +
  distress của chúng ta.
- **Overclaim chính là bài học đạo đức.** Một mô hình phân loại giận dữ/buồn diễn xuất rồi được
  đặt tên "chẩn đoán trầm cảm … để có thể bắt đầu điều trị và phòng ngừa" chính xác là kiểu
  bước nhảy về tính hữu dụng lâm sàng nguy hiểm trong bối cảnh hướng tới trẻ em. Kỷ luật của
  ViEmoSpeech — distress là một *proxy flag với một recall floor*, nuôi cho một lớp ra quyết
  định, không bao giờ là một chẩn đoán — là lập trường đúng đắn, và bài báo này cho thấy chế độ
  thất bại (failure mode) cần tránh.
- **Kỷ luật gán nhãn con người (ADR-003).** Nhãn của VNEMOS đến từ cùng một nhóm tác giả, không
  báo cáo inter-annotator agreement, không có kỷ luật speaker-disjoint, và có một tuyên bố
  proxy. Điều này củng cố lý do tại sao gold set của chúng ta cần κ/α và một holdout được gán
  nhãn bởi con người trên toàn bộ series trước khi đưa ra bất kỳ headline claim nào.
- **Biện pháp giảm thiểu cho chúng ta:** giữ cho đầu ra của distress head luôn mang tính phi
  chẩn đoán (non-diagnostic) nghiêm ngặt trong copy và API; không bao giờ để "mẫu hình cảm xúc"
  (emotion pattern) đứng thay cho "tình trạng sức khỏe tâm thần" trên các bề mặt hướng tới trẻ
  em.

### Hạn chế & câu hỏi mở cho Pebble

- **Mâu thuẫn/khoảng trống so với kế hoạch của chúng ta (V-B):** kết luận "MFCC vượt raw
  waveform" của bài báo này *dường như* làm suy yếu tiền đề của V-B rằng một backbone SSL
  raw-waveform (WavLM/emotion2vec) đáng giá chi phí bỏ ra. Mâu thuẫn này có thể được giải quyết
  — của họ là một 1D-CNN from-scratch trên 250 clip, của chúng ta là một pretrained SSL encoder
  — nhưng cần được nêu ra và kiểm chứng, chứ không được giả định là không tồn tại. Nếu ablation
  của chính chúng ta từng cho thấy MFCC ≈ WavLM trên corpus ViEmoSpeech, thì đó là một phát hiện
  thật sự, và bài báo này chính là tiền lệ. **Câu hỏi mở:** ở quy mô corpus nào thì một backbone
  raw-audio pretrained sẽ vượt qua MFCC trên tiếng nói phim truyền hình tiếng Việt?
- **Mâu thuẫn/khoảng trống so với kỷ luật đánh giá của chúng ta (V-G):** con số 0.87 của họ
  không phải speaker-disjoint (5-fold CV phân tầng theo lớp trên 250 clip / 27 nguồn). Bất kỳ
  phép so sánh nào đặt con số speaker-disjoint của chúng ta cạnh 0.87 của họ mà không kèm cảnh
  báo về split đều là so sánh khập khiễng (apples-to-oranges) và sẽ làm ViEmoSpeech bị đánh giá
  thấp hơn thực tế. Đây là mâu thuẫn cụ thể cần được nêu rõ trong bảng baseline.
- **Không có tone, không có text, không có bimodality.** Nhóm VNEMOS chỉ mới công bố các mô
  hình audio-only, tone-agnostic — xác nhận rằng khoảng trống của ViEmoSpeech (tone×emotion,
  bimodal audio+text) thực sự chưa bị nhóm này khai thác.
- **Biên độ chênh lệch nằm trong nhiễu.** +0.01 UA trên khoảng ~50 clip test/fold không phải là
  một xếp hạng đáng tin cậy; kết luận "chỉ-MFCC là tốt nhất" dựa trên một chênh lệch nhỏ hơn cả
  phương sai CV mà bài báo không báo cáo (không có std, không có CI). Nên coi toàn bộ bậc thang
  Table-4 chỉ mang tính định hướng (directional).
- **Các sai lệch nhỏ chưa được giải quyết:** bộ 5 cảm xúc được nêu không nhất quán (sợ hãi so
  với lo âu); phần tiền xử lý "160 kHz / 8 kHz" là lỗi đánh máy của 16 kHz; và baseline VNEMOS
  trước đó được trích dẫn là UA 0.85 ở đây so với "89% accuracy" trong một số bản tóm tắt trên
  web của bài báo ICDV — không có gì load-bearing, nhưng chúng làm giảm độ tin cậy về sự cẩn
  trọng số liệu của bài báo.
