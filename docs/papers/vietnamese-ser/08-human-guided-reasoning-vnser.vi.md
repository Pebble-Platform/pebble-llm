# Paper vn-08 — Human-Guided Reasoning with Large Language Models for Vietnamese Speech Emotion Recognition

> Bản dịch tiếng Việt của [08-human-guided-reasoning-vnser.md](08-human-guided-reasoning-vnser.md) — cập nhật 2026-07-10.

- **Authors:** Truc Nguyen, Then Tran, Binh Truong, Phuoc Nguyen T. H.
- **Venue / year:** arXiv preprint, Apr 2026
- **Links:** abs https://arxiv.org/abs/2604.01711 · PDF `pdfs/08-human-guided-reasoning-vnser.pdf`
- **Group:** vietnamese-ser / most recent VN SER (baseline + gap evidence)

**Tóm tắt:** Pipeline lai giữa đặc trưng âm học (pitch/energy/MFCC) và suy luận
LLM cho bài toán SER tiếng Việt 3 lớp (calm/angry/panic) trên một corpus mới
gồm 2,764 mẫu (Fleiss' κ = 0.857); độ chính xác ~86.6%, tiệm cận mức đồng
thuận của con người.

**Mức độ liên quan với ViEmoSpeech:** Là paper VN SER mới nhất; *nêu tên*
confound về thanh điệu (tone) ngay trong phần motivation nhưng không xử lý
nó — bằng chứng mạnh nhất cho thấy khoảng trống về tone-aware SER vẫn còn mở
nhưng đang khép lại nhanh. Là đối tượng so sánh baseline/label-scheme tự
nhiên (κ=0.857 trên 3 lớp của họ so với 7-class + V/A + distress của chúng
ta).

> Stub được tạo 2026-07-10 (task `docs/tasks/paper-deep-analysis.md`); deep-read đang chờ xử lý.

## Deep research — đọc toàn văn PDF (2026-07-10)

### Ghi chú về nguồn truy cập

PDF cục bộ `pdfs/08-human-guided-reasoning-vnser.pdf` đã được trích xuất
toàn bộ (end-to-end) bằng `pdftotext` (toàn bộ §§I–VI cùng Bảng I–V và danh
mục tài liệu tham khảo). Paper này **chỉ là arXiv preprint** (arXiv:2604.01711v1,
cs.CL, 2 Apr 2026) — không có phiên bản journal/conference nào khác, nên
bản preprint là bản có giá trị tham chiếu duy nhất, không tồn tại chênh lệch
preprint-so-với-bản-xuất-bản.

Kiểm chứng trên web đối với các con số trọng yếu:
- Truy vấn `Human-Guided Reasoning Large Language Models Vietnamese Speech Emotion Recognition arXiv 2604.01711`
  → dẫn tới trang abstract/HTML trên arXiv (`https://arxiv.org/html/2604.01711v1`,
  `https://arxiv.org/pdf/2604.01711`). Đã xác nhận: 2,764 mẫu, 3 lớp
  (calm/angry/panic), Fleiss' κ = 0.8574, độ chính xác tối đa 86.59%,
  Macro-F1 ≈ 0.85–0.86. **✔ được kiểm chứng.**
- WebFetch trang `https://arxiv.org/html/2604.01711v1` với các câu hỏi cụ
  thể về (a) tính khả dụng của dữ liệu (data-availability), (b) tone/dialect
  như một confound, (c) con số của mô hình tốt nhất, (d) kích thước các
  split, (e) κ, (f) consent/license. Đã xác nhận kết quả tốt nhất =
  **86.59% bởi LLaMA3.2-3B**; các split Set1 706 / Set2 691 / Set3 696 /
  Test 671; và — hai điểm phủ định mang giá trị nghiên cứu — **không có
  data-availability statement** và **không có bàn luận nào về consent,
  licensing, hay copyright** cho phần audio phim/TV/phỏng vấn. **✔ được
  kiểm chứng** (xác thực là *thực sự vắng mặt*, không chỉ đơn thuần là
  chưa được trích dẫn bởi tôi).

### Paper thực sự làm gì

**Bài toán (Task).** SER tiếng Việt 3 lớp — **calm / angry / panic** — được
khung (frame) như một bài toán cảnh báo sớm trong y tế từ xa/telehealth
(panic = lớp có ý nghĩa lâm sàng nhất). Không phải 7-class, không có
valence/arousal, không có chiều distress riêng biệt; "panic" là tương đồng
gần nhất với một cờ distress (distress flag).

**Corpus (§IV).** 2,764 đoạn audio từ **28 nguồn thu thập được** (5 phim
điện ảnh, 10 chương trình giải trí, 13 chương trình phỏng vấn), trải khắp
ba vùng phương ngữ (Bắc/Trung/Nam). Tổng thời lượng **14,841.79 s = 4.12
giờ**, ~453 MB. Phân bố lớp gần cân bằng: angry 942 (34.1%), calm 980
(35.5%), panic 842 (30.5%) [§IV-A, ✔]. Tiền xử lý: 16 kHz mono, chuẩn hóa
biên độ (amplitude-normalized), khử nhiễu tự động + thủ công, **loại bỏ
khoảng lặng bằng VAD**, phân đoạn thành các utterance có hiệu chỉnh thủ
công, lọc mẫu chất lượng thấp (§IV-B) — một pipeline có cấu trúc gần giống
chuỗi ffmpeg→VAD→turn-split của ViEmoSpeech, chỉ thiếu source-separation và
ASR.

**Quy trình gán nhãn (§IV-B/C).** Mỗi đoạn được gán nhãn bởi **3 người gán
nhãn** trên thang 3 lớp, theo hướng dẫn bằng văn bản dựa trên **pitch,
cường độ (intensity), tốc độ nói (speaking rate)** (calm = pitch ổn định/độ
biến thiên năng lượng thấp; angry = cường độ+pitch cao; panic = độ biến
thiên cao ở pitch/năng lượng/tốc độ). Bất đồng được giải quyết bằng **đánh
giá lại hoặc gán nhãn bổ sung; các mẫu mơ hồ được tinh chỉnh lại hoặc loại
bỏ**. Độ tin cậy được báo cáo theo hai cách (Bảng I): **Fleiss' κ = 0.8574**
trên 3 người gán nhãn; Cohen's κ theo cặp A–B 0.8573, A–C 0.8394, B–C
0.8757 (gọi là "Avg 0.8575") — "substantial to almost perfect" (mức đồng
thuận cao đến gần như tuyệt đối) [Bảng I, ✔]. Bảng II cho **độ chính xác
của từng người gán nhãn so với nhãn đồng thuận (consensus gold)**: A
87.8%, B 90.5%, C 90.4% (theo lớp 89.1–91.6%) — đây là "trần con người"
(human ceiling) mà mô hình sẽ được đo lường so sánh sau này [✔].

**Pipeline mô hình (§III).** Ba giai đoạn: (1) đặc trưng **pitch/energy/MFCC**
ở mức frame được tổng hợp thành một vector có độ dài cố định; một **SVM**
trên các đặc trưng đó cho ra dự đoán ban đầu kèm điểm **tin cậy
(confidence)**; (2) một **bộ định tuyến dựa trên confidence** (confidence-based
router) chuyển thẳng các mẫu có độ tin cậy cao và ủy quyền các mẫu mơ hồ
cho (3) một mô-đun **suy luận LLM** nhận vào một *mô tả dạng văn bản* về xu
hướng đặc trưng âm học (mức độ ổn định/biến thiên) cùng với **các quy tắc
heuristic do con người xây dựng** và các mẫu nhầm lẫn angry↔panic đã biết,
rồi suy luận ra nhãn. Một **vòng lặp tinh chỉnh lặp lại (iterative-refinement
loop)** biến các trường hợp bị phân loại sai thành các bản cập nhật quy
tắc/chỉnh sửa prompt. LLM là bên ra quyết định chính; ML chỉ đóng vai trò
"bằng chứng" phụ trợ. Không có backbone audio học được (không wav2vec2/WavLM/
emotion2vec); wav2vec2 chỉ được trích dẫn như related work.

**Kết quả.** Ablation theo "phiên bản" pipeline trên 3 split với Qwen2.5-7B
(Bảng III): v1 cơ bản (LLM thuần) 31–37%; v2 +quy tắc 43–48%; v3 tinh
chỉnh 54–56%; **v4 hybrid 84.6–86.1%** (Macro-F1 0.847–0.858); v5
"auto"/suy luận không có hướng dẫn sụp xuống còn 31–38% (theo Set) — bằng
chứng cho thấy suy luận LLM *không có cấu trúc* làm tăng nhiễu [Bảng III,
✔]. Trên các backbone LLM khác nhau ở tập Test (Bảng IV): v4 hybrid =
**Qwen2.5-7B 85.84% / Qwen2.5-14B 85.54% / LLaMA3.2-3B 86.59% /
Gemma3-4B 86.14%**, Macro-F1 ≈ 0.85–0.86 — gần như không phụ thuộc backbone,
và chỉ cách trần con người 88–90% khoảng ~2–4 điểm [Bảng IV, ✔]. Bảng V là
phần so sánh modality then chốt: nhánh **chỉ dùng text** (Audio→Whisper→
Text→LLM) chỉ đạt **38.70–44.11%**, so với 85–86.6% của pipeline đặc trưng
âm học — đây là luận điểm chính (headline claim) của paper rằng thông tin
âm học là không thể thiếu cho bài toán này [Bảng V, ✔].

**Tính khả dụng dữ liệu / đạo đức nghiên cứu.** **Không có.** Không có
tuyên bố phát hành (release statement), không có license, không có bàn
luận về consent/copyright cho phần audio phim/TV/phỏng vấn được scrape,
không có link code (đã xác thực sự vắng mặt qua WebFetch, ✔). Corpus được
mô tả nhưng, theo mọi bằng chứng, là đóng (closed).

### Các phần trực tiếp hữu ích cho Pebble (gắn thẻ theo Decision ID)

1. **Giao thức κ đa người gán nhãn, có quy tắc hướng dẫn, dùng làm chuẩn độ
   tin cậy — nhưng trên một thang 3 lớp (V-E).** 3 người gán nhãn, hướng
   dẫn bằng văn bản dựa trên pitch/intensity/rate, bất đồng→đánh giá lại,
   mơ hồ→loại bỏ, báo cáo dưới dạng Fleiss' κ = 0.8574 + Cohen theo cặp
   0.839–0.876 [Bảng I, ✔]. *Rủi ro khi chuyển giao (transfer risk):* κ
   của họ cao **một phần vì thang đo chỉ có 3 lớp thô, tách biệt rõ về mặt
   âm học**; thang 7-class + valence/arousal(1–5) + distress của
   ViEmoSpeech là một mục tiêu tinh hơn nhiều và sẽ có κ/α thấp hơn về mặt
   cấu trúc. Vì vậy κ=0.857 là một **trần dành cho bài toán 3 lớp, không
   phải một mức mà ViEmoSpeech nên kỳ vọng đạt tới** — điều này gợi ý nên
   báo cáo κ *theo từng chiều nhãn (per label-dimension)* và giữ lại ít
   nhất một mức gộp thô (ví dụ distress nhị phân) nơi mức đồng thuận cao
   thực sự khả thi.

2. **Cách khung "trần con người" (human-ceiling) cho việc đánh giá (V-G).**
   Họ đặt độ chính xác của mô hình (86.6%) cạnh độ chính xác của người gán
   nhãn so với đồng thuận (87.8–90.5%, Bảng II) và tuyên bố "tiệm cận mức
   đồng thuận của con người" [§V-C, ✔]. *Rủi ro khi chuyển giao:* đây là
   cách khung hợp lệ và có thể tái sử dụng trực tiếp cho báo cáo trên gold
   set của ViEmoSpeech **chỉ khi** trần con người được tính theo cùng cách
   kỷ luật đó; lưu ý con số mô hình của họ nằm trên các split **không được
   khẳng định là speaker/source-disjoint** (xem khoảng trống bên dưới), nên
   headline của họ không phải là một đối tượng so sánh sạch — ViEmoSpeech
   phải tính cả trần và con số mô hình theo **holdout toàn-series
   theo speaker-disjoint (ADR-002)**.

3. **Confound về tone/vùng miền được nêu tên trong motivation nhưng không
   bao giờ được mô hình hóa — bằng chứng nguyên văn về khoảng trống mới lạ
   (novelty gap) (V-D).** Phần mở đầu §I: *"for low-resource languages such
   as Vietnamese, SER remains challenging due to limited standardized
   datasets and complex acoustic characteristics influenced by tone,
   region, and speaking style."* (đối với các ngôn ngữ ít tài nguyên như
   tiếng Việt, SER vẫn là bài toán khó do các tập dữ liệu chuẩn hóa còn
   hạn chế và các đặc tính âm học phức tạp chịu ảnh hưởng bởi thanh điệu,
   vùng miền, và phong cách nói). Và §I: *"Emotions such as angry and panic
   often exhibit overlapping patterns in pitch and energy, making them
   difficult to distinguish reliably."* (các cảm xúc như angry và panic
   thường thể hiện các mẫu hình chồng lấp về pitch và năng lượng, khiến
   việc phân biệt đáng tin cậy trở nên khó khăn). Toàn bộ tập đặc trưng
   của họ là pitch/energy/MFCC và các quy tắc của họ là "độ biến thiên
   pitch/energy cao → panic" — tức là họ **sử dụng chính kênh (F0/energy)
   mà thanh điệu từ vựng (lexical tone) của tiếng Việt cũng chiếm dụng,
   nhưng chưa bao giờ tách tone ra khỏi emotion.** *Rủi ro khi chuyển
   giao:* không có — đây là bằng chứng có thể trích dẫn rõ ràng nhất cho
   thấy công trình VN SER mới nhất *thừa nhận* sự cạnh tranh kênh
   tone×emotion và *bỏ ngỏ không xử lý*, đúng chính là luận điểm chủ đạo
   V-D của ViEmoSpeech.

4. **Con số ablation về modality: SER tiếng Việt chỉ-dùng-text sụp xuống
   còn 38–44% (V-C, V-G).** Bảng V, nhánh chỉ-dùng-text Whisper→LLM =
   38.70–44.11% acc [✔]. *Rủi ro khi chuyển giao:* **cao — nên coi đây là
   một strawman yếu, không phải một kết luận cuối cùng.** Nhánh text của
   họ là ASR zero-shot→prompt, không có encoder fine-tuned; nhánh text của
   ViEmoSpeech là PhoBERT/ViSoBERT fine-tuned trên transcript ASR. Con số
   này chỉ cho thấy *text-thuần-túy-từ-ASR-dưới-một-LLM-generic* là yếu
   trên bài toán acted drama 3-lớp; nó **không** cho phép kết luận "text
   là vô dụng đối với SER tiếng Việt," và không được đọc như là mâu thuẫn
   với luận điểm phonation-heavy của ViEmoSpeech (vốn cho rằng nhánh text
   nên gánh *nhiều* trọng số hơn *bởi vì* kênh F0 của audio bị nhiễu bởi
   tone).

5. **Định tuyến ưu tiên quy tắc, panic-như-distress (V-F).** Bộ định tuyến
   confidence: độ tin cậy SVM quyết định liệu suy luận LLM tốn kém có được
   kích hoạt hay không; "panic" là lớp mức-độ-rủi-ro-cao mà họ muốn bắt
   được nhất [§III-D, §I]. *Rủi ro khi chuyển giao:* ý tưởng định tuyến
   (mô hình rẻ xử lý các ca dễ, chuyển các ca mơ hồ lên cho một bộ suy
   luận nặng hơn) chỉ ánh xạ vào đầu distress recall-floor của ViEmoSpeech
   như một *pattern tại thời điểm suy luận (inference-time)*; nó không
   cung cấp con số hiệu chỉnh (calibration)/ngưỡng (threshold) và không có
   recall floor, nên đây là một tương tự về thiết kế (design analogue),
   không phải một công thức cụ thể (recipe).

### Các phần giúp Pebble thành công như thế nào

- **V-E (gán nhãn):** Áp dụng cấu trúc kỷ luật của họ — ≥3 người gán nhãn,
  hướng dẫn bằng văn bản về pitch/intensity/rate, bất đồng→phân xử, mơ
  hồ→loại bỏ — nhưng **báo cáo κ theo từng chiều (per dimension)** và
  không quảng bá một con số headline kiểu 0.857 duy nhất; thang đo tinh
  hơn của ViEmoSpeech (7-class + V/A + distress) khiến một κ toàn cục dễ
  gây hiểu lầm. Artifact cụ thể: tài liệu annotation-protocol trong
  `docs/spec/capabilities` và báo cáo κ/α trên gold set nên có một mức
  rollup "distress nhị phân" thô nơi mức đồng thuận cao là khả thi, cộng
  với κ theo từng lớp được báo cáo trung thực là thấp hơn cho đầu 7-way.
- **V-G (đánh giá):** Xây dựng bảng model-vs-human-ceiling tương tự mà
  ViEmoSpeech sẽ cần cho paper phương pháp — nhưng tính con số mô hình
  dưới **holdout toàn-series theo speaker-disjoint (ADR-002)**, điều mà
  paper này không làm. Paper này là trích dẫn cho việc "SER tiếng Việt
  dùng reasoning/LLM đã tồn tại và đạt ~86% trên 3 lớp"; nó **không phải
  một baseline có thể chạy lại được** (corpus đóng, chỉ 3-class). Giữ
  arXiv:2412.09829 (rule fusion) làm baseline có thể so sánh và tái lập
  được; trích dẫn 2604.01711 chỉ cho ngữ cảnh label-scheme và κ.
- **V-D (luận điểm về tone):** Trích dẫn trực tiếp hai câu §I nêu trên vào
  phần related-work của ViEmoSpeech như bằng chứng "được-nêu-tên-nhưng-
  không-được-xử-lý", sau đó trình bày việc gán nhãn tone + tách rời
  F0/phonation của ViEmoSpeech như phần lấp đầy khoảng trống đó. Đây là
  câu trích dẫn đơn lẻ mạnh nhất trong prior art để làm động lực cho luận
  điểm có thể đo lường được về tone×emotion.
- **V-C (text dưới nhiễu ASR):** Dùng Bảng V làm *động lực* ("text-thuần-
  từ-ASR-thô chỉ đạt 38–44%, nên cần một nhánh text được fine-tuned") nhưng
  chạy ablation nhánh text của riêng ViEmoSpeech (PhoBERT/ViSoBERT trên
  transcript PhoWhisper) thay vì lấy con số của họ làm cận trên/dưới.
- **V-F (distress):** Mượn *pattern suy luận* của bộ định tuyến confidence
  cho hành vi escalate-khi-không-chắc-chắn của đầu distress, nhưng bổ sung
  recall floor + hiệu chỉnh còn thiếu (paper này không có cả hai).

### Lăng kính sức khỏe tâm thần trẻ em (chế độ ViEmoSpeech)

- **Media thu thập được, nhãn con người-là-sự-thật: tương đồng mạnh.**
  Giống ViEmoSpeech, họ cắt các đoạn cảm xúc từ **media TV/phim/phỏng vấn
  thu thập được** và coi nhãn đa người gán nhãn của con người là chân lý
  duy nhất (không có nhãn lâm sàng). Panic/angry/calm từ acted drama của họ
  là cùng loại lưu ý *acted-proxy* (đại diện diễn xuất) mà ViEmoSpeech
  cũng mang cho đầu distress — panic diễn xuất ≠ panic lâm sàng. Cách khung
  này có thể tái sử dụng cho phần disclaimer honest-proxy của đầu
  distress.
- **Khoảng trống pháp lý mà ViEmoSpeech được xây dựng để lấp đầy vẫn hoàn
  toàn bỏ ngỏ ở đây.** Họ scrape phim/giải trí/phỏng vấn với **không hề có
  bàn luận về license, consent, hay copyright** và không phát hành corpus.
  Toàn bộ tiền đề thiết kế của ViEmoSpeech — một **bản phát hành chỉ gồm
  feature+timestamps+labels, CC-BY** sao cho media có bản quyền không bao
  giờ rời khỏi git — chính xác là bài toán mà paper này không giải quyết.
  Đó vừa là rủi ro (corpus của họ không thể phát hành hợp pháp ở dạng hiện
  tại) vừa là điểm khác biệt của ViEmoSpeech.
- **Không có kỷ luật speaker/source-disjoint được nêu rõ.** Set1/2/3/Test
  được mô tả là các phân vùng ngẫu nhiên "for fair assessment" (§V-A)
  **không hề đề cập đến tính disjoint theo speaker hay source**. Với chỉ
  28 nguồn và acted drama, cùng một diễn viên/cảnh có thể xuất hiện dàn
  trải cả ở train lẫn test, điều này có thể làm phồng con số 86.6%. Đối
  với một proxy hướng tới trẻ em hoặc lâm sàng, điều này quan trọng: một
  con số bị rò rỉ danh tính người nói sẽ phóng đại khả năng tổng quát hóa
  lên một người nói mới. Holdout toàn-series theo ADR-002 của ViEmoSpeech
  là biện pháp giảm thiểu và là lý do các con số của nó sẽ trông thấp
  hơn-nhưng-trung-thực.
- **Khả năng chuyển giao của con số accuracy cụ thể là thấp.** 86.6% là
  trên **3 lớp tách biệt rõ về mặt âm học với một split có khả năng bị rò
  rỉ**; đây không phải là một mục tiêu mà đầu 7-class + V/A + distress của
  ViEmoSpeech nên được đo lường theo. Trích dẫn nó như bối cảnh prior-art,
  không phải một mức chuẩn hiệu năng.

### Hạn chế & câu hỏi mở cho Pebble

- **Mâu thuẫn/khoảng trống #1 (so với kế hoạch ViEmoSpeech — kỷ luật
  split):** Luận điểm headline của paper "tiệm cận mức con người" (86.6%
  so với 88–90%) dựa trên Set1/2/3/Test **không nêu rõ ràng buộc
  speaker/source-disjoint** (§V-A). Dưới holdout toàn-series theo ADR-002
  của ViEmoSpeech, con số trung thực nhiều khả năng sẽ thấp hơn. Đây là
  mâu thuẫn phương pháp luận trực tiếp: tuyên bố về độ tin cậy của họ
  không thể tái lập được dưới invariant đánh giá riêng của ViEmoSpeech.
- **Mâu thuẫn/khoảng trống #2 (so với vn-12 "semantics dominate" / với
  luận điểm phonation của ViEmoSpeech):** Bảng V khẳng định âm học là
  không thể thiếu và text-thuần gần như vô dụng (38–44%), *ngược lại* với
  luận điểm "semantics dominate" (vn-12, arXiv:2510.25054). Cả hai đều là
  các đọc-quá (over-readings) từ các baseline yếu: vn-12 dùng SLM đánh giá
  thấp prosody; paper này dùng ASR→LLM chưa được tinh chỉnh nên đánh giá
  thấp semantics. Luận điểm tone×emotion của ViEmoSpeech đi giữa hai thái
  cực này — F0 của audio *bị nhiễu bởi tone* nên nhánh text được
  fine-tuned phải gánh nhiều trọng số hơn so với SER phi-thanh-điệu — và
  không paper nào trong hai paper trước thực sự kiểm chứng điều đó, để
  ngỏ luận điểm có thể đo lường được này.
- **Khoảng trống mới lạ (novelty gap) được xác nhận (V-D):** paper VN SER
  mới nhất nêu tên tone/vùng miền như nguồn gốc của sự mơ hồ âm học và xây
  dựng toàn bộ tập đặc trưng trên kênh F0/energy, nhưng chưa bao giờ tách
  rời tone khỏi emotion. Khoảng trống dành cho tone-aware SER vẫn còn mở —
  và, tính đến tháng 4 năm 2026, đang khép lại nhanh.
- **Câu hỏi mở:** (a) Corpus có thể xin được không? Nó chưa được phát hành
  và không có license — nhiều khả năng không thể chia sẻ, nên không thể
  so sánh trực diện (head-to-head) trên đúng dữ liệu của họ. (b) Ngưỡng
  của bộ định tuyến confidence là bao nhiêu và LLM thực sự được kích hoạt
  bao thường xuyên? Không được báo cáo — nên chi phí/độ trễ của giai đoạn
  suy luận là không rõ. (c) Không có hiệu chỉnh (calibration), không có
  recall floor, không có phân tích lỗi theo từng lớp ngoài Macro-F1 tổng
  hợp — ViEmoSpeech phải cung cấp cả ba điều này cho đầu distress.
