# Paper 04 — Cross-Language SER Using Multimodal Dual Attention Transformers (MDAT)

> Bản dịch tiếng Việt của [04-mdat-cross-language-ser.md](04-mdat-cross-language-ser.md) — cập nhật 2026-07-10.

- **Authors:** Syed Aun Muhammad Zaidi, Siddique Latif, Junaid Qadir
- **Venue / year:** arXiv preprint 2024 (under review, IEEE TAFFC)
- **Links:** abs https://arxiv.org/abs/2306.13804 · PDF `pdfs/04-mdat-cross-language-ser.pdf`
- **Group:** audio+text (trục chính)

**Tóm tắt:** Graph attention + co-attention trên cặp encoder audio+text pretrained, tối ưu cho ít dữ liệu target-domain (cross-language).

**Mức độ liên quan với Pebble:** Low-resource domain adaptation — đúng bài toán thích nghi sang miền clinical ít nhãn của Pebble. Lưu ý: preprint-only, cite trung thực.

> Mục gọn từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (mức độ trùng lặp với Pebble)

**Hồ sơ Pebble sử dụng (tổng hợp 2026-07-03 từ `docs/intent/constraints.md` + `docs/spec/capabilities/voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`):** Luồng text chính = phân loại ordinal nguy cơ tự sát, train trên nhãn silver yếu/LLM + đánh giá trên gold lâm sàng held-out (gold-holdout luôn luôn), loss/metric ordinal (QWK/MAE), encoder họ BERT. Luồng voice kế cận = SSL emotion2vec/WavLM đóng băng + trunk chia sẻ với các head MTL không đồng nhất (emotion CE + affect V/A CCC + crisis BCE dưới một sàn recall cứng ≥0.90), Kendall uncertainty weighting; hướng phát triển tới là fusion voice+text.

### Analysis — MDAT (Cross-Language SER via Dual Attention Transformers)
- **Mức độ trùng lặp:** 12% (ngoại vi) — D1=0, D2=0, D3=1, D4=0, D5=0, D6=0, D7=2 → (Σ wᵢ·scoreᵢ = 3)/26 × 100.
- **Gần nhất ở:** D7 (khớp backbone — XLS-R wav2vec2 SSL cho audio + RoBERTa/BERT-family cho text phản chiếu backbone của cả hai luồng của Pebble); yếu hơn ở D3 (corpus SER cảm xúc chuẩn).
- **Điểm hay nhất (phương pháp nên áp dụng):** **dual-attention fusion** — một lớp co-attention (kiểu Lu et al. 2016, chuẩn hoá softmax) cộng với graph attention theo từng modality trên hai encoder đóng băng, căn chỉnh theo chiều dài bằng pad/crop, giữ được thông tin đặc thù của từng modality trong khi vẫn fuse và vượt qua concatenation đơn giản cũng như fusion BiLSTM/HCAM trên bài toán emotion.
  - **Cách áp dụng cho Pebble:** khi luồng voice chuyển sang fusion voice+text, chèn một khối co-attention trên đặc trưng audio WavLM/emotion2vec đóng băng và đặc trưng text NeoBERT (căn chỉnh chiều dài trước), đưa vào 3 head MTL hiện có, thay vì concatenation — một nâng cấp fusion rẻ và có thể trích dẫn, giữ nguyên tín hiệu của từng modality.
- **Lưu ý cần cẩn trọng:** chỉ là preprint (arXiv v3, đang được review tại IEEE TAFFC) — trích dẫn trung thực, không claim benchmark. Chỉ có một head cảm xúc categorical duy nhất → không có gì chuyển giao được cho topology của head, cân bằng MTL (D1/D5=0), sàn recall crisis (D6=0), hay distillation từ LLM (D4=0). Chỉ báo cáo UA (không có metric ordinal). "Low-resource adaptation" K-shot dùng nhãn gold thật của target, nên đây *không* phải setting gold-holdout với nhãn weak, và không mô hình hoá đúng protocol khan hiếm dữ liệu lâm sàng của Pebble.

## Deep research — full-PDF read (2026-07-10)

> Deep-read đối chiếu với **hồ sơ ViEmoSpeech hiện tại + Decision Register (V-A…V-H)** trong
> `docs/tasks/paper-deep-analysis.md`, không phải hồ sơ luồng text đã lưu trữ ở trên. Phần
> "Analysis (overlap with Pebble)" cũ (D1–D7, lăng kính luồng text NeoBERT) đã lỗi thời — giữ lại
> chỉ để làm lịch sử. Các Decision mà paper này tác động: **V-B, V-G, V-H**.

### Ghi chú về nguồn truy cập

- Đọc toàn bộ PDF qua `pdftotext "docs/papers/bimodal-ser/pdfs/04-mdat-cross-language-ser.pdf"` —
  bản copy local là **arXiv:2306.13804v3** (14/07/2023), 14 trang, đọc đủ cả sáu bảng (I–VI) + Hình 1–3.
- **Ghi chú về nơi xuất bản / provenance (mang tính then chốt):** phần stub ở trên nói "arXiv preprint, under review
  IEEE TAFFC." Thông tin này giờ đã **lỗi thời** — paper đã được **xuất bản (open access) trên *IEEE Open
  Journal of the Computer Society*, 2024, DOI 10.1109/OJCS.2024.3486904**, với *tiêu đề đã đổi*:
  "Enhancing Cross-Language Multimodal Emotion Recognition With Dual Attention Transformers." Nên trích dẫn
  phiên bản OJCS, không phải "under review TAFFC." (Tìm kiếm: *"Enhancing Cross-Language Multimodal Emotion
  Recognition With Dual Attention Transformers" IEEE journal DOI* → https://ieeexplore.ieee.org/document/10736634/ ;
  ResearchGate pub 385334554.) ✔ đã đối chiếu.
- Các con số headline đã được đối chiếu chéo với bản render arXiv HTML v2 (https://arxiv.org/html/2306.13804v2):
  UA within-corpus và hai đường cong K-shot khớp chính xác với các bảng v3 local (xem bên dưới). ✔.
- IEEE Xplore full text được render bằng JS (WebFetch trả về rỗng); OJCS là open-access nhưng tôi đã kiểm chứng
  các con số load-bearing bằng arXiv HTML/PDF, và chúng khớp với abstract của venue.

### Paper thực sự làm gì

**Bài toán.** Cross-language SER: train một bộ phân loại cảm xúc 4 lớp bimodal (audio+text) trên một ngôn ngữ,
test trên ngôn ngữ khác, cộng thêm một đường cong thích nghi low-resource K-shot. Metric xuyên suốt = **unweighted
accuracy (UA)** duy nhất (không có F1/CCC/recall).

**Mô hình (MDAT, §III, Hình 1).** Hai encoder pretrained đa ngôn ngữ đóng băng — **XLS-R (wav2vec 2.0,
128 ngôn ngữ)** cho audio và **RoBERTa (đa ngôn ngữ)** cho text — đưa vào một stack **dual-attention**:
(1) **graph attention** theo từng modality (Veličković 2017), rồi (2) **co-attention** (Lu 2016, nhưng với một
phép biến đổi dense-layer + softmax thay vì sigmoid), rồi (3) một **lớp transformer-encoder cho mỗi modality**,
sau đó concat → dense-softmax. Chiều dài được căn chỉnh bằng **Conv1D (kernel 1) để khớp chiều text với chiều
audio + pad phần ngắn / crop phần dài** (Eq. 1). Baseline = BiLSTM với fusion concat đơn giản.

**Dữ liệu (§IV.A), 4 ngôn ngữ phi thanh điệu:** IEMOCAP (tiếng Anh, spontaneous+acted, 800 utt, 4 emo), EMODB
(tiếng Đức, acted, 420 utt, 7 emo), EMOVO (tiếng Ý, acted, 336 utt, 6 emo), URDU (tiếng Urdu, talk-show YouTube,
400 utt, 4 emo; **transcript được sinh bởi ASR của EmulationAI**). Các thí nghiệm cross-language chỉ dùng 4
cảm xúc cơ bản (vui/buồn/giận/trung tính).

**Kết quả.**
- **UA within-corpus (Bảng II):** MDAT IEMOCAP **75.58**, EMODB **84.50**, URDU **94.33**, EMOVO **82.81**
  so với baseline BiLSTM 63.33 / 81.00 / 91.13 / 72.25; trên IEMOCAP MDAT 75.58 > SAFRLM 75.08 > HCAM 73.67
  (Bảng III). ✔ đã đối chiếu (arXiv HTML v2).
- **UA cross-language 0-shot (Bảng IV):** cặp tốt nhất là *acted→acted* — IEMOCAP→EMOVO **85.51**,
  EMOVO→EMODB **81.60**, URDU→EMODB **75.31**, URDU→EMOVO **67.66**; tệ nhất là *→IEMOCAP* (target
  spontaneous): IEMOCAP→EMODB **42.48**, EMODB→IEMOCAP 55.55, URDU→IEMOCAP 58.32, EMOVO→IEMOCAP 59.96. ✔.
- **Thích nghi K-shot (Bảng V, Hình 2–3):** thêm một số ít mẫu *gold ngôn ngữ target thật* làm accuracy tăng
  mạnh — IEMOCAP→EMODB **42.48 (0-shot) → 91.48 (15-shot)**; IEMOCAP→EMOVO **85.51 → 92.05**;
  EMODB→EMOVO ở 5-shot vượt baseline hơn 9 điểm, URDU→tiếng Anh ở 15-shot vượt hơn 12 điểm. ✔ đã đối chiếu
  (arXiv HTML v2: 42.48→91.48 và 85.51→92.05 đều khớp).
- **Ablation (Bảng VI):** cả ba module đều có ích; **graph attention là thành phần quan trọng nhất**
  (bỏ nó gây tổn thất lớn nhất trên cả ba kịch bản IEMOCAP→{EMODB,EMOVO,URDU}); co-attention đứng thứ hai;
  transformer-encoder giúp nhiều nhất khi đi cùng co-attention.

**Xu hướng cross-language mà tác giả rút ra (§V.B):** (i) IEMOCAP là corpus *khó nhất* — "spontaneous and
natural speech with more variations and noise" (nguyên văn tác giả) — và là target có accuracy thấp nhất;
(ii) **tiếng Anh là *nguồn* tốt nhất** ("trained on English generalises better to others than vice versa");
(iii) **Urdu low-resource là nguồn kém** (ít đa dạng hơn → transfer ra ngoài kém).

### Các phần hữu ích trực tiếp cho ViEmoSpeech (gắn nhãn theo Decision ID)

1. **Backbone audio đa ngôn ngữ đóng băng làm cầu nối cross-lingual → V-B.** XLS-R (wav2vec 2.0, 128
   ngôn ngữ, **bao gồm tiếng Việt**) là thành phần mang cảm xúc xuyên ngôn ngữ ở đây; phía text là RoBERTa
   đa ngôn ngữ. Đóng băng, chỉ dùng để trích đặc trưng — không pretrain riêng cho từng ngôn ngữ.
   *Rủi ro chuyển giao:* tập ngôn ngữ của XLS-R bao gồm VN, nên tiền đề acoustic-transfer *về mặt kiến trúc*
   là khả dụng với chúng ta; **nhưng mọi cặp được kiểm thử đều phi thanh điệu**, nên paper không cho **bằng
   chứng nào** về việc kênh mà ViEmoSpeech quan tâm (F0/phonation, nơi thanh điệu tiếng Việt tồn tại — vn-06,
   vn-13) có sống sót qua cross-lingual transfer hay không. Dùng XLS-R như một *ứng viên* cho backbone audio
   (đối trọng với WavLM/emotion2vec, mặc định V-B của chúng ta), không phải như bằng chứng rằng transfer
   Âu→VN hoạt động trên cảm xúc mang tải thanh điệu.

2. **Thích nghi low-resource K-shot với mẫu *gold thật* của target → V-H, V-B.** Đòn bẩy low-resource chủ
   đạo: 5–15 mẫu target được gán nhãn di chuyển một mô hình bimodal backbone-đóng-băng từ 40–60% lên
   80–92% UA (Bảng V). Quan trọng là các mẫu K-shot là **gold ngôn ngữ target thật**, không phải silver —
   điều này *khớp* chính xác với chế độ gán nhãn thủ công của ViEmoSpeech (ADR-003). *Rủi ro chuyển giao:*
   các mức tăng được thể hiện trên **4 cảm xúc cơ bản** với target **acted**; các lớp hiếm của chúng ta
   (disgust/fear/surprise trong scheme 7 lớp) và bản chất **found natural** của chúng ta là những ca khó mà
   các target dễ của paper này không mô hình hoá. Vậy nên K-shot cross-lingual bootstrapping là một cách
   *khả dĩ* để gieo mầm cho các lớp hiếm trước khi ta có 50 clip/lớp (sàn V-E) — nhưng phải được kiểm chứng
   trên gold held-out của chính chúng ta, không được giả định.

3. **Protocol đánh giá cross-language → V-G.** Thiết kế gọn gàng, có thể sao chép: báo cáo **cả** UA
   within-corpus lẫn cross-corpus/cross-language trong cùng một bảng; quét một **đường cong K-shot (0/5/10/15)**
   để lượng hoá lượng dữ liệu target cần để thu hẹp khoảng cách; ablate các module fusion dưới setting
   *cross-language* (Bảng VI), không chỉ within-corpus. *Rủi ro chuyển giao:* chỉ dùng UA là quá mỏng với
   chúng ta — ViEmoSpeech cần **macro-F1 (nhạy với lớp hiếm), CCC cho V/A, recall@floor cho distress**
   (register V-G). Áp dụng *hình dạng bảng* (within vs cross vs đường cong K-shot) nhưng thay UA bằng thang
   metric của chúng ta, và làm split **speaker-disjoint** (MDAT chưa bao giờ nói rõ về speaker-disjointness —
   một khoảng trống thật sự, xem bên dưới).

4. **Phát hiện về lựa chọn ngôn ngữ nguồn → V-H.** Tiếng Anh (giàu, đa dạng) transfer *ra ngoài* tốt nhất;
   Urdu low-resource transfer *ra ngoài* tệ nhất; IEMOCAP spontaneous là *target* khó nhất. *Rủi ro chuyển
   giao:* đây là kết quả định tính liên quan nhất tới ViEmoSpeech — nó dự đoán rằng (a) một corpus nguồn lớn
   và giàu (ví dụ MSP-Podcast tiếng Anh, bimodal-12) là một donor transfer tốt hơn vào VN so với một corpus
   nhỏ, và (b) **target TV-drama found natural của chúng ta là hướng khó**, nên các con số cross-lingual
   0-shot vào ViEmoSpeech nhiều khả năng sẽ rơi gần đầu thấp (40–60%), và K-shot với gold của chính chúng
   ta mới là nơi tạo ra giá trị. (Phụ: stack fusion **graph-attention + co-attention + transformer theo từng
   modality** là một ứng viên cho V-A, nhưng V-A nằm ngoài phạm vi của lần gọi này và đã được ghi chú ở
   phần cũ bên trên.)

### Từng phần giúp ViEmoSpeech thành công như thế nào

- **Thí nghiệm V-B (bake-off backbone):** thêm một **nhánh XLS-R** vào phép so sánh backbone audio
  (WavLM vs emotion2vec-S vs Whisper-encoder vs XLS-R), đóng băng, đọc ở tầng giữa (theo phát hiện
  tone-peaks-mid của vn-06). Giả thuyết cần kiểm định rõ ràng: một encoder SSL *đa ngôn ngữ* (XLS-R) có
  vượt qua một encoder *chủ yếu tiếng Anh* (WavLM) trên cảm xúc mang tải thanh điệu VN hay không? MDAT
  không đưa ra câu trả lời — đó sẽ là phép đo của chúng ta.
- **Thí nghiệm bootstrap V-H:** chạy một pilot **cross-lingual → K-shot** để gieo mầm lớp hiếm: pretrain
  head bimodal trên một corpus nguồn giàu (IEMOCAP/MSP tiếng Anh hoặc EMODB tiếng Đức cho register acted),
  rồi fine-tune với K = {0,5,10,15,50} clip gold ViEmoSpeech *cho mỗi lớp hiếm*, vẽ macro-F1 theo K. Nếu
  chỉ 15 clip gold VN cho mỗi lớp hiếm đã phục hồi phần lớn khoảng cách (như MDAT thể hiện với các cảm xúc
  cơ bản), thì sàn ≥50 clip (V-E/ADR-002) có thể đạt được nhanh hơn cho phần đuôi dài thông qua transfer
  thay vì chỉ thông qua thu thập dữ liệu.
- **Artifact protocol V-G:** mở rộng bảng kết quả ViEmoSpeech với bố cục ba cột **within-series /
  cross-series / cross-lingual** + một đường cong K-shot, metric = macro-F1 + CCC(V/A) + recall@floor, tất
  cả đều **speaker-disjoint với holdout theo toàn bộ series** (ADR-002). Bảng II/IV/V của MDAT là *bố cục*
  cần sao chép; kỷ luật metric+split của chúng ta là phần điều chỉnh.

### Lăng kính trẻ em / sức khỏe tâm thần low-resource (tính hợp lệ của chuyển giao ViEmoSpeech)

- **Cross-lingual transfer có giúp gieo mầm cho các lớp hiếm của chúng ta không? Có, một cách thận trọng
  với các cảm xúc cơ bản high-arousal; chưa được chứng minh với các cảm xúc mang tải thanh điệu.** MDAT
  cho thấy giận/vui/buồn/trung tính transfer tốt qua các ngôn ngữ phi thanh điệu với một backbone SSL đa
  ngôn ngữ + vài shot gold. Đó chính xác là những cảm xúc *nặng về arousal* mà tín hiệu âm học (cường độ,
  tempo) của chúng, theo vn-13 (Chang), **có tính cộng gộp và độc lập với thanh điệu** — nên chúng *nên*
  là những cảm xúc transfer được cho VN nữa. Các lớp có rủi ro là những lớp chiếm dụng **kênh F0/phonation**
  mà thanh điệu VN cạnh tranh (vn-06, vn-13) — và MDAT chưa bao giờ chạm tới một ngôn ngữ có thanh điệu,
  nên việc transfer *các* tín hiệu đó chính là câu hỏi mở mà ViEmoSpeech tồn tại để trả lời.
- **Hình phạt do tính tự nhiên (naturalness) là có thật và có hướng.** Dữ liệu của chính MDAT: IEMOCAP
  (corpus spontaneous duy nhất) vừa là target khó nhất vừa là nguồn có accuracy thấp nhất. ViEmoSpeech là
  **TV-drama found natural** — chính là register target khó đó. Điều này làm giảm bớt sự lạc quan về việc
  gieo mầm cross-lingual 0-shot và ủng hộ con đường K-shot (dùng gold của chính mình).
- **Lưu ý về nhãn silver KHÔNG áp dụng — một điểm có lợi cho chúng ta.** Các mẫu K-shot của MDAT là gold
  target thật. ViEmoSpeech được gán nhãn thủ công (ADR-003), nên dữ liệu thích nghi của chúng ta là *đúng
  loại*; chúng ta không nhập khẩu một giả định weak-label. (Đối lập với lo ngại của phần cũ — vốn được viết
  dưới hồ sơ luồng text nhãn silver cũ, giờ không còn hiệu lực.)
- **Đạo đức / distress:** MDAT là SER 4-cảm-xúc thông thường, không có khung lâm sàng hay trẻ em, và không
  có construct distress — không có gì để mượn cho V-F. **Không** mượn cách báo cáo chỉ-dùng-UA của nó cho
  head distress; sự trung thực về sàn recall của chúng ta (proxy acted ≠ lâm sàng) không có điểm tương đồng
  ở đây.

### Hạn chế & câu hỏi mở cho ViEmoSpeech

- **Mâu thuẫn / khoảng trống #1 — không có ngôn ngữ thanh điệu nào cả, nên tiền đề của ViEmoSpeech chưa
  được kiểm định bởi paper giống phương pháp của chúng ta nhất.** MDAT là bimodal audio+text, XLS-R+RoBERTa,
  cross-lingual — cùng họ kiến trúc với chúng ta — nhưng bốn ngôn ngữ của nó (EN/DE/IT/Urdu) đều **phi thanh
  điệu**. Claim "cross-lingual transfer cải thiện SER low-resource" chỉ được đối chiếu ở nơi **thanh điệu và
  cảm xúc không chia sẻ kênh F0**. Với tiếng Việt (6 thanh điệu nặng về phonation, vn-06/vn-13) việc transfer
  có thể *tệ hơn* các con số này gợi ý, vì một mô hình Âu→VN không mang theo prior nào về thanh điệu. Đây là
  khoảng trắng mà ViEmoSpeech sở hữu.
- **Mâu thuẫn / khoảng trống #2 — sự lạc quan "transfer hoạt động" của MDAT đối lập với canh bạc found-natural.**
  MDAT: IEMOCAP spontaneous là khó nhất; vn-11 (THAI-SER) riêng biệt phát hiện scripted > improvised (WA
  73.99 so với 61.80). Cả hai đều đi ngược lại canh cược của ViEmoSpeech rằng TV-drama found natural là một
  chất liệu *tốt hơn* — cross-lingual transfer vào một target tự nhiên là hướng bất lợi trong cả hai paper.
  Chúng ta phải *chứng minh* lợi ích của tính tự nhiên, không được mặc định nó.
- **Khoảng trống về khả năng tái lập — không báo cáo hyperparameter huấn luyện.** PDF cho kiến trúc (các
  phương trình) nhưng **không có learning rate, số epoch, batch size, số lớp transformer, số head graph-attention,
  hay số chiều embedding**. Một lần tái lập (cần thiết trước khi coi XLS-R+dual-attention là baseline V-A/V-B)
  đòi hỏi phải dựng lại các giá trị này; coi MDAT là một *mẫu thiết kế*, không phải một công thức chạy được ngay.
- **Các điểm không nhất quán nội bộ trong PDF (cần đánh dấu khi trích dẫn).** (a) Cột "0-shot MDAT" của Bảng V
  in ra **48.48** cho IEMOCAP→EMODB, nhưng Bảng IV và arXiv HTML đều cho **42.48** — 42.48 là con số đáng tin
  (✔), 48.48 là lỗi đánh máy. (b) Phần văn xuôi §V.C nói English→Italian 0-shot là "82.51%", nhưng Bảng IV/V
  và bản HTML cho **85.51** — nên trích dẫn 85.51. Nhỏ, nhưng cần ghi chú để không lan truyền một mốc sai.
- **Chỉ dùng UA, không có metric cho lớp hiếm.** MDAT không bao giờ báo cáo recall/F1 theo từng lớp, nên
  accuracy của nó không cho biết gì về hành vi long-tail mà ViEmoSpeech quan tâm nhất — phản chiếu lá cờ đỏ
  vn-07/CASE (CE phẳng làm sụp đổ các lớp hiếm). Bất kỳ sự tái sử dụng thiết kế này của ViEmoSpeech đều phải
  thêm macro-F1 + một sàn cho lớp hiếm ngay từ đầu.
