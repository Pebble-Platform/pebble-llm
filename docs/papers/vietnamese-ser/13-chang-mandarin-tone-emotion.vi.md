# Paper vn-13 — Emotional Tones of Voice Affect the Acoustics and Perception of Mandarin Tones

> Bản dịch tiếng Việt của [13-chang-mandarin-tone-emotion.md](13-chang-mandarin-tone-emotion.md) — cập nhật 2026-07-10.

- **Authors:** Chang et al. (Yueh-Chin Chang và cộng sự)
- **Venue / year:** PLOS ONE 18(4):e0283635, 2023
- **Links:** article https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0283635 · PDF `pdfs/13-chang-mandarin-tone-emotion.pdf`
- **Group:** vietnamese-ser / core empirical premise (phonetics)

**Tóm tắt:** Phân tích ngữ âm học + các thí nghiệm cảm nhận trên các âm tiết
tiếng Quan Thoại mang cảm xúc: giận dữ làm tăng F0/biên độ, buồn bã kéo dài
thời lượng, và cảm xúc ảnh hưởng đến việc nhận diện thanh điệu nhiều hơn là
thanh điệu ảnh hưởng đến việc nhận diện cảm xúc.

**Mức độ liên quan đến ViEmoSpeech:** Đây là bằng chứng thực nghiệm bình duyệt
mạnh mẽ nhất cho luận điểm nền tảng rằng thanh điệu từ vựng và ngôn điệu cảm
xúc cạnh tranh nhau trên cùng một kênh F0 (V-D). Có thể trích dẫn như hiện
tượng động lực; đây không phải một bài báo mô hình hóa, cũng không phải tiếng
Việt — bộ ngữ liệu của chúng ta biến phiên bản tiếng Việt của hiện tượng này
thành thứ đo lường được.

> Stub được tạo ngày 2026-07-10 (task `docs/tasks/paper-deep-analysis.md`); việc đọc sâu đang chờ xử lý.

## Nghiên cứu sâu — đọc toàn văn PDF (2026-07-10)

### Ghi chú về nguồn truy cập

Bài báo được đọc trọn vẹn từ đầu đến cuối từ PDF cục bộ
`pdfs/13-chang-mandarin-tone-emotion.pdf` thông qua `pdftotext` (trích xuất
đầy đủ 26 trang, 1083 dòng). Đây **không phải** là bản preprint: PLOS ONE
18(4):e0283635 là truy cập mở CC-BY (nhận bài 2021-07-23, chấp nhận
2023-03-14, xuất bản 2023-04-05), vì vậy PDF cục bộ **chính là** phiên bản
chính thức của tạp chí — không tồn tại chênh lệch preprint/bản xuất bản.
`pdftotext` đã làm xáo trộn thứ tự cột bên trong bốn ma trận nhầm lẫn (Tables
4, 5, 7, 8), nên mọi con số quan trọng đều đã được đối chiếu lại với bản HTML
đã xuất bản của PLOS.

Xác thực nguồn gốc (tất cả đều ✔ được đối chiếu khớp với bài báo đã xuất bản):
- Truy vấn: `Chang Lee Wang 2023 Emotional tones of voice affect acoustics perception Mandarin tones PLOS ONE asymmetry` →
  tìm ra `https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0283635` (cũng có trên PMC10075469).
- WebFetch từ URL đó xác nhận: bốn giá trị chi-square LME của Experiment 1
  (F0, F0-range, amplitude, duration) bao gồm hai **tương tác thanh
  điệu×cảm xúc không có ý nghĩa thống kê** (amplitude p=.98, duration p=.29);
  8 diễn viên / 36 người nghe; độ chính xác nhận diện thanh điệu 40–98%
  (isolation) / 78–100% (context); nhận diện cảm xúc 21–93% (isolation) /
  85–99% (context); kết luận về tính bất đối xứng và lưu ý "không cao hơn"
  đi kèm; thứ tự ANGRY > HAPPY/SAD > FEAR. Tất cả đều khớp với bản trích xuất.

Danh sách tác giả đầy đủ (nguyên văn): **Hui-Shan Chang, Chao-Yang Lee,
Xianhui Wang, Shuenn-Tsong Young, Cheng-Hsuan Li, Woei-Chyn Chu** (tác giả
liên hệ). Đơn vị công tác: National Yang Ming Chiao Tung Univ. (Taipei),
Asia Univ. (Taichung), National Taichung Univ. of Education, Ohio Univ.
(Athens, USA), MacKay Medical College. IRB No. 1000063 (NYCU). Được tài trợ
bởi MOST Taiwan.

### Bài báo thực sự làm gì

Đây là một nghiên cứu ngữ âm-tâm lý học (psychophonetics) gồm hai thí nghiệm,
xem xét ngôn điệu cảm xúc làm nhiễu loạn ngữ âm học và nhận thức của bốn
thanh điệu từ vựng tiếng Quan Thoại như thế nào. Đây là một bài báo về
**cảm nhận/ngữ âm học**, không phải bài báo mô hình hóa — không có bộ phân
loại, không có ML.

**Experiment 1 — ngữ âm học (tạo âm).** Tám diễn viên chuyên nghiệp (4 nữ /
4 nam, tuổi trung bình 32.4 ± 7.1, tiếng Quan Thoại Đài Loan) tạo ra 3 âm
tiết mục tiêu /fa/, /ɕi/, /pu/ (ba nguyên âm phổ biến nhất trong tiếng Quan
Thoại Đài Loan, đều là từ thật ở cả bốn thanh điệu, đều trung tính về mặt
cảm xúc), mỗi âm tiết ở cả 4 thanh điệu = 12 tổ hợp âm tiết-thanh điệu, kết
hợp chéo với 5 cảm xúc (ANGRY, FEAR, HAPPY, SAD, NEUTRAL), được lồng vào
giữa câu trong một cụm câu mang cố định
/ni³ uo¹ [target] ts̩⁵/ "You say the word [target]". 60 tổ hợp từ-cảm xúc ×
2 lần lặp × 8 người nói = **960 kích thích** (44.1 kHz/16-bit, micro GRAS
40AC, cách 30 cm). Sự hiện diện của cảm xúc được xác minh độc lập: 30 người
đánh giá bản ngữ, lựa chọn cưỡng bức bốn phương án + thang Likert 5 điểm; chỉ
những kích thích được **toàn bộ 30** người đánh giá nhận diện đúng và chấm
≥3.0 mới được đưa vào phân tích (tất cả đều đạt). Các âm tiết mục tiêu được
cắt tại xung thanh môn cuối cùng của âm tiết trước và xung thanh môn cuối
cùng của âm tiết mục tiêu (Praat [Boersma & Weenink]). Bốn thước đo ngữ âm
học: **F0 trung bình, biên độ F0 (F0 range), biên độ trung bình, thời
lượng**. Thống kê: mỗi thước đo được khớp một mô hình hiệu ứng hỗn hợp tuyến
tính (linear mixed-effects model) — hiệu ứng cố định = thanh điệu, cảm xúc,
thanh điệu×cảm xúc; hiệu ứng ngẫu nhiên = người nói, giới tính người nói, âm
tiết, lần lặp.

Kết quả Experiment 1 (tất cả đều ✔ được đối chiếu khớp; §Results, S1 Table):

| Thước đo | Hiệu ứng chính của thanh điệu | Hiệu ứng chính của cảm xúc | Tương tác Thanh điệu×Cảm xúc |
|---|---|---|---|
| F0 trung bình | χ²(3)=973.95, p<.001 | χ²(4)=1749.66, p<.001 | χ²(12)=**70.18, p<.001** (có ý nghĩa) |
| Biên độ F0 (F0 range) | χ²(3)=779.23, p<.001 | χ²(4)=123.02, p<.001 | χ²(12)=**114.64, p<.001** (có ý nghĩa) |
| Biên độ trung bình | χ²(3)=121.1, p<.001 | χ²(4)=1801.44, p<.001 | χ²(12)=**3.92, p=.98** (không có ý nghĩa) |
| Thời lượng | χ²(3)=32.5, p<.001 | χ²(4)=639.74, p<.001 | χ²(12)=**14.2, p=.29** (không có ý nghĩa) |

Các phát hiện về hướng: **ANGRY có F0 trung bình cao nhất và biên độ trung
bình cao nhất; NEUTRAL thấp nhất ở cả hai; SAD có thời lượng dài nhất.** Thứ
hạng tương đối của FEAR/HAPPY/SAD trên trục F0 thay đổi tùy theo thanh điệu;
biên độ F0 không cho thấy thứ hạng cảm xúc nhất quán. Kết quả cấu trúc quan
trọng nhất: hiệu ứng cảm xúc lên **biên độ và thời lượng có tính cộng gộp
(additive) trên các thanh điệu** (không có tương tác), trong khi hiệu ứng
cảm xúc lên **F0 trung bình và biên độ F0 phụ thuộc vào thanh điệu** (tương
tác mạnh). Các hướng dự đoán-so-với-thực-tế được trình bày ở Table 1/Table
2; điều bất ngờ chính so với các nghiên cứu trước là ANGRY **không** làm
ngắn thời lượng (thực tế là "="), và FEAR làm tăng biên độ ("thực tế >"
trong khi các nghiên cứu trước cho phép "> hoặc <").

**Experiment 2 — cảm nhận (nhận diện).** 36 người nghe (23 nữ / 13 nam, tuổi
19–23, trung bình 20.08 ± 0.91, tiếng Quan Thoại Đài Loan), được sàng lọc
trước bằng bài kiểm tra nhận diện thanh điệu trung tính (isolation
97/93/93/98% cho T1–T4; context 100/100/99/100%). Các kích thích lấy từ 1
diễn viên nữ và 1 diễn viên nam được đánh giá cao nhất. Hai nhiệm vụ 4AFC ×
hai bối cảnh (âm tiết mục tiêu **ở dạng cô lập** = được cắt ra khỏi cụm câu
mang, so với **trong bối cảnh** = kèm cụm câu mang): nhận diện thanh điệu (5
cảm xúc → 240 kích thích → 480 lượt thử) và nhận diện cảm xúc (NEUTRAL bị
loại bỏ để tránh nó trở thành đáp án mặc định "không chắc" → 192 kích thích
→ 384 lượt thử). Hồi quy logistic hiệu ứng hỗn hợp (cố định: thanh điệu,
cảm xúc, bối cảnh, thanh điệu×cảm xúc; ngẫu nhiên: giới tính người nói, âm
tiết, lần lặp).

Kết quả Experiment 2 (tất cả đều ✔ được đối chiếu khớp; §Results, Tables 3–8, S2/S3):
- **Nhận diện thanh điệu.** Tất cả hiệu ứng chính đều p<.001: thanh điệu
  χ²(3)=83.12, cảm xúc χ²(4)=486.38, bối cảnh χ²(1)=**1534.71** (lớn nhất
  bằng một khoảng cách xa), thanh điệu×cảm xúc χ²(12)=**492.89**. Độ chính
  xác **40–98% khi cô lập, 78–100% trong bối cảnh.** Nhầm lẫn khi cô lập
  (Table 4): dưới điều kiện ANGRY, Thanh 1 và Thanh 3 bị nghe nhầm thành
  **Thanh 4** (thanh xuống cao — thanh nghe "giận dữ nhất"); dưới điều kiện
  FEAR, các thanh điệu có xu hướng lệch về **Thanh 1**; HAPPY/SAD không cho
  thấy thiên hướng nhầm lẫn nổi bật nào. Trong bối cảnh, tỷ lệ lỗi gần 20%
  duy nhất là ANGRY-Thanh-1 → Thanh-4; cụm câu mang đã "vô hiệu hóa hiệu
  quả" tác hại của cảm xúc lên việc nhận diện thanh điệu.
- **Nhận diện cảm xúc.** Tất cả hiệu ứng chính đều p<.001: thanh điệu
  χ²(3)=92.92, cảm xúc χ²=775.08, bối cảnh χ²(1)=**1843.42**, thanh
  điệu×cảm xúc χ²(9)=**327.95**. Độ chính xác **21–93% khi cô lập, 85–99%
  trong bối cảnh.** Thứ tự **ANGRY > HAPPY ≈ SAD > FEAR** (ANGRY tốt nhất ở
  3 trên 4 thanh điệu, FEAR tệ nhất ở cả bốn). Độ chính xác trên đường chéo
  khi cô lập (Table 7, ≈ từ bản trích xuất, các khoảng ✔): ANGRY 77/76/53/93%
  (T1–T4), FEAR 21/36/34/37%, HAPPY 82/76/49/71%, SAD 42/72/73/61%. Nhầm lẫn
  khi cô lập: SAD→FEAR (T1, T4), FEAR→HAPPY (T1, T2) nhưng FEAR→SAD (T3, T4).
- **Tính bất đối xứng (kết quả nổi bật).** "Cảm xúc ảnh hưởng đến việc nhận
  diện thanh điệu tiếng Quan Thoại nhiều hơn là thanh điệu tiếng Quan Thoại
  ảnh hưởng đến việc nhận diện cảm xúc." Bằng chứng: thứ hạng độ chính xác
  nhận diện thanh điệu dao động mạnh trên các cảm xúc khác nhau (Table 3),
  nhưng thứ hạng nhận diện cảm xúc lại ổn định trên các thanh điệu khác nhau
  (Table 6). **Lưu ý quan trọng mà chính các tác giả nêu ra:** đây là tính
  bất đối xứng của *ảnh hưởng qua lại*, KHÔNG phải của độ khó — nhận diện
  cảm xúc (21–93% cô lập / 85–99% bối cảnh) **không chính xác hơn** nhận
  diện thanh điệu (40–98% cô lập / 78–100% bối cảnh). "Cảm xúc dường như
  không vốn dĩ dễ nhận diện hơn... ảnh hưởng qua lại giữa chúng chỉ là bất
  đối xứng."

Các hạn chế được nêu (§Conclusions): chỉ 4 cảm xúc cơ bản được diễn xuất
(không bao trùm valence/arousal — chỉ HAPPY là tích cực, chỉ SAD là arousal
thấp); một cụm câu mang / một ngữ cảnh thanh điệu; chỉ tiếng Quan Thoại Đài
Loan; NEUTRAL vắng mặt trong nhiệm vụ cảm nhận; các âm tiết "cô lập" là được
cắt ra chứ không phải vốn dĩ cô lập tự nhiên; thứ tự cô-lập-trước-bối-cảnh
có thể đã làm tăng ảo độ chính xác trong bối cảnh; và — quan trọng đối với
chúng ta — **không có thước đo chất lượng giọng nói (voice quality)** ("các
thước đo ngữ âm học bổ sung về chất lượng giọng nói... sẽ hữu ích") và chỉ
dùng F0 tóm tắt, không mô hình hóa đường bao F0 (F0-contour) (họ đề xuất
Functional Data Analysis).

### Các phần hữu ích trực tiếp cho Pebble

1. **Độ lớn tương tác như một thước đo định lượng cho cạnh tranh kênh —
   V-D (cốt lõi), V-B.** Bốn giá trị chi-square tương tác của LME chính là
   con số "thanh điệu và cảm xúc tranh giành nhau trên một kênh đến mức
   nào" mà bài báo phương pháp của chúng ta cần tạo ra cho tiếng Việt. Kết
   quả của Chang: F0 trung bình χ²(12)=70.18 và biên độ F0 χ²(12)=114.64
   là **có ý nghĩa thống kê** (thanh điệu làm rối các tín hiệu F0 của cảm
   xúc) trong khi biên độ χ²(12)=3.92 (p=.98) và thời lượng χ²(12)=14.2
   (p=.29) là **không có ý nghĩa thống kê** (thanh điệu để nguyên các tín
   hiệu biên độ/thời lượng của cảm xúc). Đây là một bản đồ cạnh tranh
   theo-từng-tham-số có thể trích dẫn, đã qua bình duyệt. *Rủi ro khi
   chuyển giao:* **hướng** (F0 bị vướng víu, biên độ/thời lượng tự do) nhìn
   chung có thể chuyển giao sang tiếng Việt vì thanh điệu ở cả hai ngôn ngữ
   đều mang trên kênh F0; nhưng **độ lớn** và phần mở rộng then chốt sang
   **kênh phát âm (phonation)** thì không — 4 thanh điệu tiếng Quan Thoại
   chủ yếu là dạng đường nét (contour-dominant), trong khi 6 thanh điệu
   tiếng Việt nặng về phát âm (glottalization/creak ở thanh ngã/nặng; Shen
   NAACL 2024, vn-06). Chang không hề đo phát âm, vì vậy ở tiếng Việt tồn
   tại cả một trục cạnh tranh (chất lượng giọng nói) mà kết luận "tự do"
   của ông về biên độ/thời lượng không nói lên điều gì — và đó chính xác
   là trục mà cảm xúc cũng sử dụng (buồn kèm creak, giận kèm giọng ép/pressed).
   Khoảng trống ĐÓ chính là đóng góp đo lường được của chúng ta.

2. **Biên độ và thời lượng là các chiều cảm xúc vững vàng trước thanh điệu
   (tone-robust) — V-B.** Vì hiệu ứng của cảm xúc lên biên độ và thời lượng
   không tương tác với thanh điệu, nên các đặc trưng năng lượng/độ lớn RMS
   và thời lượng/tốc độ nói là các chiều ngữ âm học vẫn đáng tin cậy cho
   nhánh cảm xúc ngay cả khi thanh điệu từ vựng đang chiếm dụng kênh F0.
   *Rủi ro khi chuyển giao:* điều này càng đúng hơn ở tiếng Việt so với
   tiếng Quan Thoại đối với hai đặc trưng cụ thể này (chúng không phải là
   đặc trưng chủ đạo của thanh điệu ở cả hai ngôn ngữ), nhưng hệ quả kéo
   theo — "vậy nên F0 là kênh duy nhất bị tranh chấp" — là SAI đối với
   tiếng Việt: phát âm là một kênh tranh chấp thứ hai mà Chang chưa từng
   kiểm tra. Vì vậy hành động cho V-B = giữ các đặc trưng biên độ/thời
   lượng như những kênh mang cảm xúc an toàn **và** bổ sung các đặc trưng
   phát âm rõ ràng (jitter/shimmer/HNR/H1–H2/CPP, theo vn-06 V-B), nhưng
   **không** coi chúng là tự động vững vàng trước thanh điệu theo cách mà
   biên độ/thời lượng được — chúng phải được kiểm chứng.

3. **Quy trình cảm nhận như một mẫu thiết kế kiểm định người nghe cho bộ
   dữ liệu vàng của ViEmoSpeech — V-E.** Experiment 2 của Chang là một
   thiết kế gọn gàng, có thể tái sử dụng: sàng lọc người nghe trước bằng
   nhận diện thanh điệu trung tính; một vòng xác minh cảm xúc độc lập
   (N=30 người đánh giá, cổng nhận vào yêu cầu tất cả đều đúng + Likert
   ≥3) *trước khi* tiến hành nghiên cứu chính; nhận diện 4AFC; phân tích
   ma trận nhầm lẫn + hồi quy logistic hiệu ứng hỗn hợp; và thao tác
   cô-lập-so-với-bối-cảnh. *Rủi ro khi chuyển giao:* có thể áp dụng trực
   tiếp về mặt hình thức, nhưng kích thích của chúng ta khác về bản chất —
   các lượt lời tự phát nhiều âm tiết từ phim truyền hình, 7 cảm xúc +
   V/A + distress, người nói thật chứ không phải diễn viên. Thao tác "cụm
   câu mang" của ông tương ứng với lựa chọn của chúng ta giữa "cắt clip
   sát tại VAD∩lượt lời" so với "giữ lại vài từ dẫn nhập bối cảnh".

4. **Hướng nhầm lẫn thanh điệu ở mức arousal cao củng cố lỗi thất bại ASR
   của chúng ta — V-C, V-D.** Phát hiện của Chang rằng ANGRY làm cảm nhận
   thanh điệu lệch về **Thanh 4 (thanh xuống cao)** còn FEAR lệch về
   **Thanh 1** là một phép tương tự về nhận thức con người của lỗi ASR mà
   chúng ta quan sát được ở PhoWhisper — **lỗi hoán đổi thanh điệu ở mức
   arousal cao** (mày→máy, tao→tháo). *Rủi ro khi chuyển giao:* các thanh
   điệu cụ thể không tương ứng trực tiếp (hệ thống thanh điệu khác nhau),
   nhưng *hiện tượng* — arousal cao làm sai lệch một cách có hệ thống
   thanh điệu nào được nhận ra — chính là điều mà nhánh văn bản của chúng
   ta phải bền vững trước, và Chang là trích dẫn khoa học về cảm nhận
   chứng minh rằng đây là một hiệu ứng thật, có hệ thống, chứ không chỉ
   là nhiễu ASR.

### Các phần này giúp Pebble thành công như thế nào

- **V-D (xương sống tính mới của bài báo phương pháp).** Chạy lại thiết kế
  Experiment 1 của Chang như một nghiên cứu đo lường ngữ âm học trên bộ dữ
  liệu vàng ViEmoSpeech: F0 trung bình, biên độ F0, biên độ, thời lượng
  theo từng câu nói, **cộng thêm** các thước đo phát âm (jitter, shimmer,
  HNR, H1–H2, CPP) mà Chang đã bỏ sót, sau đó khớp một mô hình LME cho mỗi
  thước đo với tương tác thanh điệu × cảm xúc (và phương ngữ). Báo cáo
  bảng chi-square tương tác cạnh nhau với bảng của Chang cho tiếng Quan
  Thoại. Kết quả nổi bật, có thể kiểm chứng được dự đoán: trong tiếng Việt,
  tương tác F0 sẽ tái lập kết quả của Chang, nhưng sẽ xuất hiện **một
  tương tác kênh phát âm không có đối ứng trong tiếng Quan Thoại** — phép
  đo trực tiếp đầu tiên cho điều mà vn-06 mới chỉ suy luận. Đây chính là
  hiện vật cụ thể: một thực nghiệm
  `docs/spec/.../tone-emotion-competition` tạo ra bảng so sánh đó.
- **V-B (lựa chọn đặc trưng/backbone).** Cụ thể: trong nhánh âm thanh, đảm
  bảo các thống kê năng lượng/độ lớn và tốc độ/thời lượng được giữ lại như
  đặc trưng (các lớp SSL đóng băng có thể mất thông tin biên độ tuyệt đối
  — thêm một vector RMS/thời lượng thủ công), vì Chang chứng minh đây là
  các kênh mang cảm xúc trực giao với thanh điệu. Và thêm vector phát âm
  như một đầu vào hạng nhất, vì trạng thái vững vàng trước thanh điệu mà
  Chang gán cho biên độ/thời lượng không thể mặc định áp dụng cho các tín
  hiệu phát âm mà thanh điệu tiếng Việt chiếm dụng.
- **V-E (cổng kiểm định người nghe).** Trước khi đưa ra bất kỳ tuyên bố SER
  nổi bật nào, chạy một nghiên cứu người nghe theo kiểu Chang trên một
  lát cắt vàng khoảng 200 clip: (a) một vòng xác minh cảm xúc với cổng
  nhận vào (đa số đúng + ngưỡng độ tin cậy) đồng thời đóng vai trò kiểm
  tra mức độ đồng thuận giữa hai giáo viên con người theo ADR-003; (b) một
  nghiên cứu con về nhận diện thanh điệu trên các clip arousal cao so với
  trung tính để đo mức độ arousal làm suy giảm khả năng phục hồi thanh
  điệu *của con người* trong tiếng Việt — trần năng lực con người cho vấn
  đề hoán đổi thanh điệu của ASR. Hiện vật: một tài liệu quy trình
  `eval/listener_validation/` + phiếu chú thích 4AFC.
- **V-C (độ bền của nhánh văn bản).** Trích dẫn nhầm lẫn ANGRY→Thanh-4 /
  FEAR→Thanh-1 của Chang làm căn cứ về mặt cảm nhận cho lý do tại sao
  nhánh văn bản ViSoBERT/PhoBERT phải gánh nhiều tải trọng hơn ở mức
  arousal cao: nếu người nghe được huấn luyện còn phục hồi sai thanh điệu
  dưới tác động cảm xúc, thì PhoWhisper chắc chắn cũng vậy, do đó bước
  fusion không được tin tưởng mù quáng vào các token ASR khi nhánh âm
  thanh báo hiệu arousal cao.

### Lăng kính sức khỏe tâm thần trẻ em

- **Tính hợp lệ của việc chuyển giao bị giới hạn theo ba hướng, tất cả đều
  chống lại việc tái sử dụng ngây thơ.** (1) *Ngôn ngữ:* 4 thanh điệu dạng
  đường nét của tiếng Quan Thoại ≠ 6 thanh điệu nặng về phát âm của tiếng
  Việt — kênh tranh chấp phát âm, vốn quan trọng nhất đối với distress
  (giọng creaky/pressed), hoàn toàn nằm ngoài bộ thước đo của Chang. (2)
  *Đăng ký/thể loại (register):* Chang sử dụng diễn viên chuyên nghiệp
  trưởng thành đọc các âm tiết CVC cô lập trong một câu khung cố định;
  ViEmoSpeech là lời nói hội thoại tự phát từ phim truyền hình. (3) *Độ
  tuổi:* tất cả đối tượng đều là người trưởng thành (diễn viên trung bình
  32 tuổi; người nghe 19–23 tuổi); Chang nêu rõ **"Không có trẻ vị thành
  niên nào tham gia nghiên cứu này."** Ở đây **không có** dữ liệu giọng
  nói trẻ em. Đường thanh quản nhỏ hơn của trẻ em làm tăng F0 và có thể
  nén khoảng trống của biên độ F0, có khả năng *làm gia tăng* cạnh tranh
  F0 giữa thanh điệu và cảm xúc so với người lớn — đây là một suy diễn
  chưa được kiểm chứng, không phải một phát hiện thực nghiệm.
- **Đối chiếu về đạo đức nghiên cứu (tiền lệ hữu ích).** Quy trình IRB của
  Chang (NYCU IRB 1000063, đồng ý bằng văn bản, diễn viên trưởng thành
  được trả thù lao, điều khoản rõ ràng không có trẻ vị thành niên) là một
  mô hình đồng thuận trong phòng thí nghiệm gọn gàng, nhưng nó *ngược
  lại hoàn toàn* với bộ ràng buộc của ViEmoSpeech: lời nói của chúng ta là
  phim truyền hình bản quyền của bên thứ ba, dưới một chế độ phát hành
  chỉ-đặc-trưng CC-BY, không có người tham gia đồng thuận nào. Chang không
  phải là một mẫu quản trị (governance template) cho chúng ta; nó là lời
  nhắc rằng đạo đức của một bài báo ghi âm trong phòng thí nghiệm không
  chuyển giao được sang một bộ ngữ liệu tìm thấy từ phương tiện truyền
  thông (found media).
- **Sắc thái liên quan đến distress.** SAD của Chang (thời lượng dài, F0
  thấp, không có biên độ đặc trưng) và FEAR (được nhận diện kém nhất, dễ
  nhầm lẫn với cả HAPPY *và* SAD) là hai cảm xúc gần nhất với proxy
  distress của chúng ta, và chúng chính xác là những cảm xúc *khó nhận
  diện nhất về mặt ngữ âm học* (FEAR chỉ 21–37% khi cô lập). Đây là một
  cảnh báo trực tiếp cho ngưỡng sàn recall của đầu distress (V-F): các
  trạng thái cảm xúc mà chúng ta cần bắt được nhất lại chính là những
  trạng thái có tín hiệu ngữ âm học yếu nhất, phụ thuộc bối cảnh nhiều
  nhất — củng cố thêm rằng distress không thể là một quyết định chỉ dựa
  trên âm thanh mà cần cả nhánh văn bản và bối cảnh mang câu mà Chang cho
  thấy có khả năng cứu vãn việc nhận diện (85–99% trong bối cảnh so với
  21–93% khi cô lập).

### Hạn chế & câu hỏi mở cho Pebble

- **Mâu thuẫn/khoảng trống #1 (so với vn-06 Shen + tiền đề của chính chúng
  ta).** Kết quả gọn gàng của Chang "biên độ và thời lượng mang cảm xúc
  độc lập với thanh điệu; chỉ F0 bị tranh chấp" được rút ra từ một ngôn
  ngữ có thanh điệu chủ yếu là dạng đường nét F0, và từ một bộ thước đo
  **hoàn toàn loại trừ phát âm**. Toàn bộ luận điểm của chúng ta (vn-06)
  là thanh điệu tiếng Việt nặng về phát âm — tức là tồn tại một kênh tranh
  chấp *thứ hai* mà Chang không thể nhìn thấy. Vì vậy bản đồ "hai chiều an
  toàn" đầy trấn an của Chang **không đầy đủ đối với tiếng Việt về mặt cấu
  trúc**, và nếu coi nó là đủ thì sẽ thiết kế bộ đặc trưng bỏ lỡ chính kênh
  mà cạnh tranh thanh điệu-cảm xúc tiếng Việt tồn tại. Khoảng trống chính
  là đóng góp: ViEmoSpeech có thể tạo ra bảng tương tác bao gồm cả phát âm
  mà thiết kế của Chang về mặt cấu trúc không thể làm được.
- **Mâu thuẫn/khoảng trống #2 (so với câu tóm tắt một dòng của stub /
  project-overview).** Stub tóm tắt Chang là "cảm xúc ảnh hưởng đến nhận
  diện thanh điệu nhiều hơn là thanh điệu ảnh hưởng đến nhận diện cảm
  xúc" — cách diễn đạt này mời gọi cách hiểu rằng cảm xúc là kênh mạnh
  hơn, vững vàng hơn. Chang **bác bỏ rõ ràng** cách hiểu đó: nhận diện
  cảm xúc *không* chính xác hơn nhận diện thanh điệu (21–93% so với
  40–98% khi cô lập); tính bất đối xứng nằm ở *ảnh hưởng qua lại*, không
  phải ở độ vững vàng hay độ khó. Bất kỳ trích dẫn nào của Pebble cũng
  phải mang theo lưu ý này, nếu không một người bình duyệt đọc bài báo sẽ
  bắt được lỗi diễn giải quá mức.
- **Mâu thuẫn/khoảng trống #3 (so với vn-12 "ngữ nghĩa chiếm ưu thế" và
  vn-08 "văn bản gần như vô dụng").** Chang là một nghiên cứu thuần
  ngữ âm học/cảm nhận, **không có kênh văn bản/ngữ nghĩa nào cả** (âm tiết
  cô lập, 4AFC trên ngữ âm học) — vì vậy nó không thể ủng hộ cũng không
  thể bác bỏ cuộc tranh luận ngữ nghĩa-so-với-ngữ âm học mà các bài báo
  khác của chúng ta đang chia rẽ quan điểm. Nó định lượng sự cạnh tranh
  *ngữ âm học* giữa thanh điệu và cảm xúc, vốn là động lực cho việc cần
  một nhánh văn bản, nhưng không nói gì về việc văn bản nên chiếm bao
  nhiêu trọng số. Tuyên bố đo lường được của chúng ta (nhánh văn bản cần
  gánh bao nhiêu tải trọng) vẫn còn bỏ ngỏ và là điều chúng ta phải tự
  xác định bằng thực nghiệm.
- **Hiệu ứng bối cảnh là hiệu ứng đơn lẻ lớn nhất trong Experiment 2**
  (chi-square của bối cảnh vượt xa thanh điệu và cảm xúc: 1534.71 cho
  nhận diện thanh điệu, 1843.42 cho nhận diện cảm xúc). Câu hỏi mở cho
  chính sách cắt clip của chúng ta: việc cắt clip sát tại VAD∩lượt lời
  (giống isolation) so với giữ lại một đoạn dẫn nhập ngắn (giống context)
  có thể thay đổi đáng kể mức độ có thể khôi phục được của cả thanh điệu
  lẫn cảm xúc — một biến thiết kế mà Chang cho thấy còn lớn hơn cả bản
  thân hiệu ứng cảm xúc. Đáng để thực hiện một nghiên cứu loại bỏ (ablation)
  về độ đệm của clip.
- **Không mô hình hóa đường bao F0, không có chất lượng giọng nói, một
  câu mang duy nhất, một phương ngữ duy nhất, diễn viên chứ không phải
  lời nói tự phát.** Mỗi hạn chế mà chính Chang liệt kê đều là một điểm
  mà thiết kế của ViEmoSpeech đã rộng hơn (6 thanh điệu, 3 phương ngữ, phim
  truyền hình tự phát đa cảm xúc, các đặc trưng phát âm) — vì vậy Chang
  được trích dẫn tốt nhất như *tiền đề động lực* mà phương pháp của chúng
  ta mở rộng, chứ không phải một kết quả mà chúng ta tái lập.
