# Bài báo 36 — J-ToneNet: Mạng Mã hóa dựa trên Transformer nhằm Cải thiện Phân loại Thanh điệu trong Giọng nói Liên tục thông qua Chuỗi F0

## 1. Thông tin thư mục

**Tiêu đề:** J-ToneNet: A Transformer-based Encoding Network for Improving Tone Classification in Continuous Speech via F0 Sequences

**Tác giả:** Yi-Fen Liu (tác giả liên hệ, yfliu@fcu.edu.tw) và Xiang-Li Lu, Khoa Kỹ thuật Thông tin và Khoa học Máy tính, Đại học Phùng Giáp (Feng-Chia University), Đài Loan.

**Năm / hội nghị:** Interspeech 2023 (Dublin, Ireland, 20–24 tháng 8 năm 2023), trang 2138–2142. Mã ISCA Archive `liu23e_interspeech`. DOI 10.21437/Interspeech.2023-695.

**Bản mở rộng trên tạp chí:** cùng nhóm tác giả đã công bố một bản tiếp nối dài hơn, "Learning and consolidating the contextualized contour representations of tones from F0 sequences and durational variations via transformers," *The Journal of the Acoustical Society of America* **156**(5):3353 (2024) — thiết kế J-ToneNet được kế thừa và mở rộng.

**Tài trợ:** National Science and Technology Council, Đài Loan, dự án 110-2222-E-035-005-MY2.

**Từ khóa chỉ mục (nguyên văn):** "pitch contour, tonal coarticulation, speech rhythm, jointly learning, encoder, BERT, Transformer layers".

## 2. Động lực của vấn đề

Tiếng Trung phổ thông (Mandarin) là ngôn ngữ thanh điệu: bốn thanh điệu từ vựng trên các âm tiết đầy đủ (cao `/55/`, lên `/25/`, võng xuống `/214/`, xuống `/51/`) phân biệt nghĩa của từ hoàn toàn thông qua hình dạng của đường bao tần số cơ bản (f0). Hầu hết các bộ phân loại thanh điệu trước đây làm việc trên **âm tiết cô lập** và dựa vào các đặc trưng phong phú hơn f0 đơn thuần — quang phổ (spectrogram), MFCC, năng lượng — để đạt độ chính xác cao. Luận điểm của bài báo là khó khăn thực sự không nằm ở âm tiết cô lập mà ở **giọng nói liên tục**, nơi đường bao thanh điệu bị bóp méo bởi **đồng phát âm (coarticulation)** (đường bao của một thanh điệu bị kéo về phía các thanh điệu lân cận) và bởi các hiệu ứng **nhịp điệu / tốc độ nói**. Các mô hình xây dựng "trong sự vắng mặt của ngữ cảnh" không thể phân biệt một thanh điệu bị đồng phát âm với một thanh điệu chuẩn (citation). Các tác giả lưu ý rằng, ví dụ, Thanh 3 thường được hiện thực hóa thành dạng thấp-xuống `/21/` và Thanh 2 thành dạng võng `/323/` trong tiếng phổ thông Đài Loan — các biến thể mà một mô hình không có ngữ cảnh không bao giờ thấy một cách rõ ràng.

Phân loại thanh điệu quan trọng đối với (a) học ngôn ngữ hỗ trợ máy tính (CALL) cho người học Mandarin như ngôn ngữ thứ hai (L2) và (b) nâng độ chính xác nhận dạng trong ASR tiếng Mandarin. Khoảng trống được nêu: "có tương đối ít mô hình học sâu được ghi nhận dựa trên transformer hoặc khung BERT để mã hóa thông tin đường cong cao độ từ các chuỗi giá trị f0 cho phân loại thanh điệu." J-ToneNet lấp khoảng trống đó bằng một mô hình chỉ-dùng-f0, hoàn toàn-transformer, cấp độ phát ngôn (utterance-level).

## 3. Vị trí trong tài liệu

Bài báo định vị mình so với ba nhóm. **Mô hình CNN thanh điệu trên đặc trưng phổ** — Chen và cộng sự (Interspeech 2016) và **ToneNet** (Gao, Sun, Yang, Interspeech 2019; tài liệu tham khảo [14] ở đây — đây là bài #33 trong repo này) đạt kết quả mạnh trên tin tức phát thanh bằng cách dùng Mel-/FFT-spectrogram, nhưng trên các đoạn **cô lập**. **Các mô hình lai hồi quy / chú ý / huấn luyện chung** — Yang và cộng sự (CBLSTM+attention, Interspeech 2018), Tang & Li (end-to-end với ngữ cảnh ngắn hạn, APSIPA 2021), Huang và cộng sự (encoder-decoder theo dõi cao độ + huấn luyện chung, ICASSP 2021) giảm tỉ lệ lỗi bằng cách thêm ngữ cảnh. **Phân loại thanh điệu không cần cao độ** — Ryant và cộng sự (2014) phân loại thanh điệu mà hoàn toàn không theo dõi cao độ.

Định vị của J-ToneNet cố ý đi ngược dòng trên hai trục: (1) đầu vào **chỉ-dùng-f0** (không spectrogram/MFCC/năng lượng), đảo ngược xu hướng "nhiều đặc trưng hơn = tốt hơn" của lĩnh vực, để cô lập bài toán mô hình hóa đường bao; và (2) **bộ mã hóa kiểu transformer / BERT trên chuỗi f0**, mượn thủ thuật nhiều `[CLS]` với phân đoạn theo khoảng (interval-segmentation) từ **BERTSUM** (Liu & Lapata, EMNLP-IJCNLP 2019) vốn dùng cho tóm tắt nhiều câu, được tái sử dụng ở đây cho các phát ngôn nhiều âm tiết.

## 4. Phân tích sâu bộ dữ liệu — FCU-VOICE-100 và MCDC-8

Hai bộ dữ liệu ở **hai phong cách nói khác nhau** — sự tương phản này là xương sống thực nghiệm. Cả hai được ghi trong phòng yên tĩnh, lấy mẫu ở **16 kHz**, căn chỉnh cưỡng bức (force-align) bằng **ILAS phone aligner**, với chỉnh sửa thủ công / kiểm chứng bởi con người.

**FCU-VOICE-100 (giọng ĐỌC chuẩn bị trước).** Tuyển 400 sinh viên Đại học Phùng Giáp; mỗi nhóm 40 người nói (20 nam / 20 nữ) đọc cùng một bộ 250 câu nhắc đọc. 10 bộ câu nhắc riêng biệt rút từ Sinica Core Vocabulary Inventory — một nửa là các từ thường dùng, một nửa là các câu minh họa cách dùng từ. Người nói đọc "rõ ràng và tự nhiên." Thực nghiệm dùng một **tập con gồm 100 người nói**. Sau kiểm chứng, **4.641 trên 25.020 bản ghi bị loại** (chỉ giữ các âm "phát âm đúng và căn chỉnh chuẩn"; các trường hợp mơ hồ được giải quyết bằng đồng thuận giữa người chú thích và tác giả thứ nhất).

**MCDC-8 (giọng HỘI THOẠI tự phát).** Tám cuộc hội thoại tự phát dài 1 giờ, chủ đề tự do, 16 người nói theo cặp, từ **Mandarin Conversation Dialog Corpus (MCDC)** đã phát hành. Cắt thành **6.060 lượt nói**. Được kiểm chứng trên các đơn vị giữa-các-quãng-nghỉ (IPU), từ, âm tiết và phiên âm thanh điệu.

**Đơn vị xử lý:** các đoạn mệnh đề (clausal chunks) cho giọng đọc, IPU cho giọng hội thoại.

**Bảng 1 (đặc điểm bộ dữ liệu):**

| Corpus | #Người nói | #Phát ngôn | #Âm tiết | Kiểm chứng thanh điệu | Phát ngôn 1–2 âm tiết |
|---|---|---|---|---|---|
| FCU-VOICE-100 | 100 | 23.601 | 125.178 | Có (53,4%) | 46,3% (~11.000) |
| MCDC-8 | 16 | 13.407 | 131.003 | Có (75,9%) | 14,1% (1.890) |

Phân bố độ dài (Hình 2): trong MCDC-8 hội thoại, ~10% phát ngôn vượt quá **17 âm tiết** — tài liệu dài hơn, đồng phát âm nhiều hơn nhiều so với corpus đọc. Đây là bài kiểm tra khó cho mô hình ngữ cảnh.

## 5. Phương pháp

### 5.1 Pipeline đầu vào đường bao f0 (đặc trưng cấp đoạn)

f0 được trích bằng theo dõi cao độ của **PRAAT**, sau đó **log-transform** và **chuẩn hóa về [0,1]** theo từng người nói bằng cách dùng trần/sàn f0 ở **phân vị 0,1% và 99,9%** của dải f0 người nói — viết tắt là **normLogF0**. Hai bộ đặc trưng:

- **normLogF0(20):** mỗi âm tiết, một vector **20 điểm cố định** từ nội suy các quan sát f0 tuần tự. Đây là biểu diễn chỉ-dùng-f0.
- **ToneFea(17):** một mở rộng thủ công 17 chiều (Bảng 3 trong bài): hệ số đa thức bậc 2 khớp với đường bao (đặc trưng 1–3), vị trí tương đối của cực tiểu/cực đại (4–5), sáu đặc trưng hiệu tứ phân vị (6–11), và độ dốc tương ứng theo vùng (12–17). Dùng làm bộ "thêm vào" để kiểm tra liệu đặc trưng thiết kế thủ công có còn giúp ích so với đường bao thô hay không.

### 5.2 Các baseline cấp đoạn (âm tiết cô lập)

- **Random Forest** — 16.384 cây dự đoán; chọn vì độ bền với ước lượng f0 nhiễu từ theo dõi cao độ. Baseline thay thế cho mức state-of-the-art.
- **FFN** — hai lớp kết nối đầy đủ, kích hoạt **GeLU**, lớp ẩn cuối → 512 nơ-ron → softmax trên 4 thanh điệu.
- **1D-CNN** — sáu lớp tích chập, kích thước kernel 4, stride 1, số bộ lọc 128/256/512 (mỗi 2 lớp), average pooling (kernel 2) sau lớp 2 và 4, rồi hai lớp FC 512 → softmax trên 4 thanh điệu. GeLU xuyên suốt.

### 5.3 C-Net: bộ mã hóa đường bao thanh điệu (Hình 3)

Phần cốt lõi. Một **transformer hai chiều kiểu BERTSUM trên chuỗi f0**. Các khối xây dựng đầu vào (tất cả được cộng tại mỗi vị trí f0):

1. **Pitch Embedding** — ánh xạ tuyến tính giá trị f0 1 chiều sang chiều ẩn **d = 512**; các giá trị vô thanh/không theo dõi được và phần đệm cuối là số 0.
2. **Positional Embedding** — **sinusoidal** (kiểu Vaswani) để đánh dấu thứ tự cao độ.
3. **Token Embedding** — `[VAL]` cho token cao độ theo dõi được, `[NAN]` cho token không theo dõi được/đệm. Một token **`[CLS]` được chèn trước mỗi âm tiết hoặc từ**, tổng hợp thông tin đường bao đến một ranh giới `[SEP]`.
4. **Segment Embedding** — phân đoạn theo khoảng với hai ký hiệu `E_A` / `E_B` để phân biệt thanh điệu **lẻ vs chẵn** trong phát ngôn (thủ thuật nhiều câu của BERTSUM, ở đây là nhiều âm tiết).

Ngăn xếp transformer (**L = 4 lớp**):

```
h_l = LN(h_{l-1} + MHAtt(h_{l-1}))      (1)
h_l = LN(h_l + FFN(h_l))                (2)
```

"Các lớp Transformer thấp tập trung vào các cao độ liền kề; các lớp cao hơn, với self-attention, tập trung nhiều hơn vào hiệu ứng đồng phát âm của thanh điệu." Embedding đường bao của âm tiết *i* là vector ẩn lớp trên cùng của token `[CLS]` của nó.

### 5.4 R-Net: bộ mã hóa phụ trợ về nhịp điệu lời nói

Một bộ mã hóa song song nhận **hai chuỗi thời lượng (duration)**: (a) thời lượng âm tiết thô, (b) hiệu giữa mỗi thời lượng âm tiết và thời lượng trung bình. Một **Duration Embedding** (lớp FC → d = 512) + positional embedding đưa vào một **transformer 2 lớp** (cùng phương trình 1–2). Tạo ra một embedding nhịp điệu cho mỗi âm tiết. R-Net là thứ tiêm vào ngữ cảnh tốc độ nói / nhịp điệu mà f0 thuần không thể mang theo.

### 5.5 J-ToneNet: hợp nhất (fusion) + học chung (joint learning)

Hợp nhất embedding đường bao và embedding nhịp điệu bằng cách chiếu cả hai vào một không gian chung và nối (concatenate) trước layer norm. Một cơ chế **cổng kiểu squeeze-and-excitation** (nút thắt ngược: FC mở rộng → GeLU → FC thu hẹp) tính các trọng số chú ý theo kênh, nhân từng phần tử vào trạng thái đã hợp nhất, chiếu tuyến tính về d = 512, rồi một phép biến đổi **tanh** để dễ diễn giải, rồi đến bộ phân loại.

**Hàm mất mát học chung (đóng góp chủ chốt):**

```
L = CE(dự đoán thanh điệu âm tiết, nhãn vàng) + CE(dự đoán thanh điệu từ, nhãn vàng)   (7)
```

Hàm mất mát kết hợp cross-entropy trên **thanh điệu âm tiết** *và* trên **thanh điệu từ** (từ đơn âm tiết và "một số cặp thanh điệu từ song âm tiết nhất định"). Động lực là ý tưởng "ngữ cảnh tương hợp vs ngữ cảnh xung đột": một thanh điệu lân cận có register tương tự (ví dụ `/55/-/55/`) so với khác (ví dụ `/51/-/55/`) định hình sự đồng phát âm, nên việc dự đoán đồng thời cặp thanh điệu cấp từ củng cố các biểu diễn đường bao cấp âm tiết.

### 5.6 Phân chia dữ liệu

Mỗi bộ dữ liệu chia **80% train / 10% dev / 10% test** theo phát ngôn.

## 6. Thực nghiệm và kết quả — con số chính xác (Bảng 3)

Tất cả con số là **độ chính xác phân loại thanh điệu (%)**. Khối trái = các baseline cấp đoạn trên âm tiết cô lập; khối phải = ablation J-ToneNet theo độ dài phát ngôn.

**Các baseline cấp đoạn (âm tiết cô lập):**

| Mô hình | FCU-VOICE-100 F0 | FCU-VOICE-100 ToneFea | MCDC-8 F0 | MCDC-8 ToneFea |
|---|---|---|---|---|
| Random Forest | 52,5 | 57,2 | 44,8 | 48,9 |
| FFN | 50,5 | 55,9 | 43,6 | 44,9 |
| 1D-CNN | 52,6 | 56,7 | 45,4 | 45,4 |
| **J-ToneNet** | **91,0** | — | **61,7** | — |

**Ablation loại bỏ thành phần của J-ToneNet (tổng thể + theo độ dài phát ngôn tính bằng âm tiết):**

| Cấu hình | FCU Tổng | FCU ≤2 | FCU 3–20 | FCU ≥21 | MCDC Tổng | MCDC ≤2 | MCDC 3–20 | MCDC ≥21 |
|---|---|---|---|---|---|---|---|---|
| **J-ToneNet (đầy đủ)** | **91,0** | 80,0 | 93,0 | 94,1 | **61,7** | 67,1 | 61,9 | 60,7 |
| − joint learning | 87,7 | 78,2 | 89,4 | 91,2 | 58,6 | 63,4 | 59,7 | 55,8 |
| − joint learn. & R-Net | 86,0 | 78,9 | 87,4 | 73,5 | 58,9 | 63,8 | 60,2 | 55,6 |
| chỉ C-Net trên SYL | 59,0 | — | 50,6 | — | — | — | — | — |

**Những điểm đọc chính:**
- **Giọng đọc (FCU-VOICE-100):** J-ToneNet **91,0%** so với baseline cấp đoạn tốt nhất **57,2%** (RF + ToneFea) — bước nhảy tuyệt đối **+33,8 điểm**. Chiến thắng áp đảo và tăng theo độ dài phát ngôn (94,1% ở ≥21 âm tiết vs 80,0% ở ≤2).
- **Giọng tự phát (MCDC-8):** J-ToneNet **61,7%** so với baseline tốt nhất **48,9%** (RF + ToneFea) — **+12,8 điểm**, nhưng độ chính xác tuyệt đối thấp hơn nhiều, và (khác giọng đọc) độ chính xác **không** cải thiện theo độ dài (60,7% ở ≥21 vs 67,1% ở ≤2).
- **Joint learning** đóng góp **+3,3 điểm** trên giọng đọc (91,0 → 87,7) và **+3,1 điểm** trên giọng hội thoại (61,7 → 58,6).
- **R-Net** quan trọng cho các đoạn **giọng-đọc-dài**: loại bỏ nó làm sụp độ chính xác FCU ≥21 âm tiết từ 91,2 → **73,5** (−17,7 điểm). Trên giọng hội thoại, tác dụng của R-Net nhỏ/mơ hồ.
- **Chỉ C-Net trên âm tiết cô lập** chỉ đạt **59,0%** (FCU) — "hiệu quả, nhưng kém xa" so với mô hình có ngữ cảnh cấp phát ngôn. Đây là bằng chứng tồn tại rằng **ngữ cảnh phát ngôn, không phải riêng bộ mã hóa, mới là động lực của các cải thiện.**
- **Đặc trưng thủ công ToneFea(17)** giúp các baseline giọng đọc (RF 52,5→57,2) nhưng cho "cải thiện nhẹ hoặc gần như không tăng" trên các mô hình nơ-ron giọng tự phát — các đặc trưng thiết kế thủ công không chuyển sang được giọng tự phát.

Các tác giả gọi kết quả là "khá sơ bộ"; kết quả hội thoại được nêu rõ là "không thỏa đáng" và được đánh dấu là việc tương lai (mô hình hóa nhịp điệu / hợp nhất nguyên âm phong phú hơn).

## 7. Hạn chế do tác giả nêu

(a) Mô hình "vẫn đang phát triển," kết quả "sơ bộ." (b) Độ chính xác giọng hội thoại (~62%) không thỏa đáng; nguyên nhân quy cho mô hình hóa thiếu về thời gian nhịp điệu (rhythmic timing) và sự hợp nhất nguyên âm (vowel merging). (c) Việc tương lai = làm giàu các biểu diễn nhịp điệu của thời gian giữa các âm tiết. (d) Đáng chú ý, các tác giả nêu rõ giá trị của mô hình cho "**các ứng dụng lâm sàng sàng lọc giọng nói trẻ em về việc tạo thanh điệu**" (trích dẫn [33]) — móc nối hướng-tới-trẻ-em trực tiếp duy nhất trong bài.

## Nghiên cứu sâu — đọc toàn văn PDF (2026-06-16)

### Ghi chú truy cập nguồn

Toàn văn PDF `docs/papers/pdfs/36-j-tonenet.pdf` được trích bằng `pdftotext` (tệp cục bộ là PDF kỷ yếu camera-ready của Interspeech 2023, với footer "10.21437/Interspeech.2023-695" và trang 2138–2142 được nhúng). Kiểm chứng:

- **Hội nghị / DOI / trang / tác giả** — đã xác nhận với mục ISCA Archive. Truy vấn: "J-ToneNet Transformer Tone Classification Continuous Speech F0 Sequences Interspeech 2023 Liu Lu" → https://www.isca-archive.org/interspeech_2023/liu23e_interspeech.html (tiêu đề, tác giả Yi-Fen Liu & Xiang-Li Lu, trang 2138–2142, DOI 10.21437/Interspeech.2023-695). **✔ đã xác nhận.** Trang ISCA chỉ hiển thị tóm tắt (abstract), nên tên bộ dữ liệu và tất cả con số đến từ PDF cục bộ toàn văn, không phải từ web.
- **Bộ dữ liệu** — `FCU-VOICE-100` (đọc) và `MCDC-8` (tự phát, từ Mandarin Conversation Dialog Corpus) chỉ được nêu tên trong §2 của PDF toàn văn. Trang tóm tắt ISCA **không** nêu tên chúng; WebFetch trang ISCA trả về "không có bộ dữ liệu cụ thể nào xuất hiện." Vậy tên bộ dữ liệu là **✔ đã xác nhận từ văn bản PDF camera-ready cục bộ** (Bảng 1 + §2.1), không có trên web. **≈** đối với mọi đối chiếu ngoài về chính các corpus (ILAS/MCDC là tài nguyên của Tseng tại Academia Sinica, không tải mở được).
- **Bản mở rộng tạp chí** — bản JASA 156(5):3353 (2024) của cùng tác giả "Learning and consolidating the contextualized contour representations of tones from F0 sequences and durational variations via transformers" được xác nhận qua tìm kiếm (mục AIP/Semantic Scholar); toàn văn AIP bị tường phí (HTTP 403), nên các con số của nó **không** được dùng ở đây. Bản camera-ready Interspeech là nguồn có thẩm quyền cho mọi con số bên dưới.
- **Con số** — tất cả độ chính xác được đọc trực tiếp từ Bảng 3 của PDF. pdftotext làm rối bố cục hai-khối của Bảng 3 (các baseline cấp đoạn và ablation theo độ dài chia chung hàng); tôi tái dựng ánh xạ bằng cách khớp các giá trị "Overall" của J-ToneNet (91,0 / 61,7) xuất hiện ở cả hai khối, neo các cột một cách không mơ hồ. Gắn nhãn **✔ đã xác nhận (nguồn đơn: PDF camera-ready)** — không có bản công khai thứ hai chứa con số để đối chiếu chéo, nên xem như đã-xác-minh-bản-chép chứ không phải đã-tái-lập độc lập.

**Đính chính khung quan trọng cho yêu cầu nhiệm vụ:** nhiệm vụ yêu cầu "độ chính xác so với baseline ToneNet CNN." J-ToneNet **không** chạy lại ToneNet (Gao và cộng sự 2019, bài #33 của repo này). ToneNet chỉ xuất hiện dưới dạng tài liệu tham khảo [14]. Các baseline trong bài mà J-ToneNet vượt qua là **Random Forest, FFN, và một 1D-CNN** — 1D-CNN là vật thay thế gần nhất cho một mô hình tích chập kiểu ToneNet. Vậy "so với ToneNet CNN" ở đây nghĩa là **so với baseline 1D-CNN cấp đoạn (52,6% F0 đọc / 45,4% hội thoại)**, không phải đối đầu trực tiếp với ToneNet đã công bố. Sự phân biệt này mang tính chịu lực (load-bearing) và không được phóng đại trong bản viết cho Pebble.

### Bài báo thực sự làm gì

Một bộ phân loại thanh điệu **chỉ-dùng-chuỗi-f0**, hoàn toàn-transformer, cho **giọng nói Mandarin liên tục**. Pipeline: f0 từ PRAAT → log-chuẩn-hóa theo từng người nói về [0,1] (normLogF0) → một bộ mã hóa kiểu BERTSUM (**C-Net**, L=4) trên dòng f0 toàn phát ngôn với một `[CLS]` cho mỗi âm tiết và embedding phân đoạn khoảng lẻ/chẵn → hợp nhất qua cổng kiểu SE với một **bộ mã hóa nhịp điệu (R-Net, 2 lớp)** trên thời lượng âm tiết → **hàm mất mát cross-entropy học chung thanh-điệu-âm-tiết + thanh-điệu-từ** (eq. 7). Huấn luyện 80/10/10 trên hai corpus phong cách đối lập: đọc (FCU-VOICE-100, 23.601 phát ngôn) và tự phát (MCDC-8, 13.407 phát ngôn). Tiêu điểm: **91,0% đọc / 61,7% hội thoại** độ chính xác thanh điệu, so với baseline cấp đoạn tốt nhất 57,2% / 48,9%; ablation cho thấy **ngữ cảnh phát ngôn (không phải bộ mã hóa) là động lực** (chỉ C-Net trên âm tiết cô lập = 59,0%), **joint learning thêm ~3 điểm**, và **R-Net thiết yếu cho các đoạn giọng-đọc-dài** (≥21 âm tiết: 91,2 → 73,5 nếu thiếu nó).

### Các phần trực tiếp hữu ích cho Pebble (mỗi phần gắn các ID Quyết định)

Nhánh luận điểm liên quan của Pebble là **phương thức TIN-NHẮN-GIỌNG-NÓI (VOICE-MESSAGE)**: một mô-đun gọn, thân thiện chạy trên thiết bị, biến tin nhắn giọng nói của trẻ thành tín hiệu thanh điệu (prosody) cấp cho các head cảm xúc/độ nghiêm trọng. J-ToneNet là công thức được công bố sạch sẽ nhất cho một **transformer nhỏ trên chuỗi đường bao f0**.

1. **Đầu vào chỉ-dùng-đường-bao-f0 + chuẩn hóa normLogF0 theo từng người nói** (§5.1: log f0, chuẩn hóa về [0,1] dùng phân vị 0,1%/99,9%; nội suy 20 điểm cố định mỗi đoạn). **→ D-D (hồi quy severity/energy — nguồn chuyển giao & biểu diễn đầu vào), D-H (bộ dữ liệu / vật thay thế đặc trưng).** Đây là một công thức đầy đủ, rẻ cho front-end f0 của một head prosody-giọng-nói Pebble: f0 từ PRAAT/librosa → log → chuẩn hóa min/max theo từng người nói → lấy mẫu lại về độ dài cố định. **Rủi ro chuyển giao:** chuẩn hóa theo từng người nói dựa trên phân vị cần *đủ khung hữu thanh cho mỗi người nói* để ước lượng dải 0,1/99,9; một tin nhắn giọng nói trẻ ngắn có thể không cho dải ổn định → Pebble cần một dải chạy-theo-từng-trẻ hoặc một phương án dự phòng theo quần thể. Pipeline đường bao chuyển giao được; *việc hiệu chỉnh chuẩn hóa* không chuyển giao ngay được.

2. **Bộ mã hóa kiểu BERTSUM với nhiều `[CLS]` và embedding phân đoạn khoảng trên một chuỗi phi-văn-bản** (§5.3: `[CLS]` mỗi đơn vị, ranh giới `[SEP]`, id phân đoạn lẻ/chẵn `E_A`/`E_B`, vị trí sinusoidal, L=4, d=512). **→ D-A (encoder backbone — bằng chứng một transformer nhỏ chuyên dụng vượt CNN/RF trên dữ liệu đường bao), D-B (cấu trúc đa nhiệm).** Chứng minh rằng *kiến trúc đầu vào* của BERT (lược đồ cộng-embedding + token đặc biệt), không phải một checkpoint BERT đã tiền-huấn-luyện, mới là thứ mang việc mô hình hóa đường bao. **Rủi ro chuyển giao:** đây là một bộ mã hóa **âm thanh**, hoàn toàn tách biệt khỏi NeoBERT (bộ mã hóa văn bản). Nó chỉ có thể là một **tháp phương thức song song**, không phải một head trên NeoBERT. Áp dụng nó nghĩa là cam kết với kiến trúc hợp nhất đa-tháp, điều v1 (chỉ-văn-bản) không có.

3. **Hàm mất mát đa nhiệm học chung = CE cấp âm tiết + CE cấp từ trên cùng một bộ mã hóa chia sẻ** (eq. 7; ablation: +3,3 điểm đọc, +3,1 hội thoại). **→ D-B (cân bằng mất mát MTL).** Bằng chứng cụ thể rằng việc thêm một *head phụ trợ thô hơn* (thanh-điệu-từ) chia sẻ bộ mã hóa với *head tinh hơn* (thanh-điệu-âm-tiết) củng cố biểu diễn và nâng head tinh — một bản tương đồng quy mô nhỏ sạch sẽ của việc đồng-huấn-luyện emotion(12 nhãn) + severity(hồi quy) của Pebble. **Rủi ro chuyển giao:** ở đây hai head là *cùng họ nhãn ở hai độ chi tiết* (thanh điệu), nên chúng tự nhiên căn chỉnh; head emotion vs severity của Pebble là *các họ nhãn khác nhau* với thang đo khác nhau — kết quả "head thô phụ trợ giúp head tinh" có thể không chuyển giao khi các nhiệm vụ không lồng nhau. Dùng làm động lực cho một *head phụ trợ lồng-theo-độ-chi-tiết*, không phải bằng chứng rằng MTL tùy ý đều giúp.

4. **Đánh giá phân tầng theo độ dài** (Bảng 3: độ chính xác báo cáo riêng cho phát ngôn ≤2 / 3–20 / ≥21 âm tiết). **→ D-G (ngưỡng/sàn recall + chính sách đánh giá).** Ý tưởng *đánh giá* tái sử dụng được nhất: báo cáo metric **phân tầng theo độ dài đầu vào**, vì hành vi mô hình đảo ngược theo độ dài (giọng đọc cải thiện theo độ dài; hội thoại suy giảm). **Rủi ro chuyển giao:** không có — đây là thực hành vệ-sinh-đánh-giá thuần túy và chuyển giao trực tiếp sang chấm điểm cấp-lượt của Pebble (phân tầng theo độ dài token của lượt và vị trí trong hội thoại).

5. **Tháp phụ trợ nhịp điệu/thời lượng R-Net** (§5.4: chuỗi thời lượng + (thời lượng − trung bình), transformer 2 lớp, hợp nhất qua cổng SE). **→ D-D (proxy năng lượng/kích thích từ prosody), D-B.** Tốc-độ-nói / nhịp điệu chính xác là loại tín hiệu mà chiều `energy` heuristic của Pebble mong muốn. **Rủi ro chuyển giao:** R-Net giúp giọng đọc nhưng cho cải thiện "nhỏ/mơ hồ" trên giọng tự phát — và một tin nhắn giọng nói trẻ là **tự phát**, không phải đọc. Thành phần giống nhất với điều Pebble cần (nhịp điệu→kích thích) lại chính là thành phần *không tổng quát hóa được sang giọng tự phát ngay trong bài này.*

### Mỗi phần giúp Pebble thành công như thế nào

- **Dựng một mô-đun đặc trưng `voice-prosody` (điểm 1) làm front-end tin-nhắn-giọng-nói v2.** Tạo phẩm cụ thể: một hàm tiền xử lý `f0_contour(wav) -> normLogF0[N]` (f0 từ PRAAT/librosa → log → chuẩn hóa phân vị theo từng người nói → lấy mẫu lại độ dài cố định). Đây là công thức đầu vào tối thiểu, đã xác thực; nó cho phương thức giọng nói một đường bao số mà phần còn lại của stack tiêu thụ được. **(D-D, D-H)** Đưa ra sau một feature flag, chỉ-văn-bản giữ là v1.
- **Tạo nguyên mẫu một head `f0-transformer` thanh-điệu/prosody (điểm 2) làm một tháp phương thức riêng, hợp nhất muộn.** Tạo phẩm cụ thể: một bộ mã hóa 4 lớp, d=512 phản chiếu C-Net (nhiều `[CLS]`, vị trí sinusoidal, token `[VAL]`/`[NAN]`), huấn luyện trước trên một corpus Mandarin/thanh-điệu hoặc cao độ công khai để xác thực pipeline, rồi nhắm lại sang ánh xạ prosody-→-cảm-xúc. Embedding của nó được nối với `[CLS]` của NeoBERT ở lớp hợp nhất — **không** tiêm vào NeoBERT. **(D-A, D-B)**
- **Áp dụng mẫu head-phụ-trợ-lồng-theo-độ-chi-tiết (điểm 3) trong head emotion.** Tạo phẩm cụ thể: bên cạnh head emotion tinh 12 nhãn, thêm một head phụ trợ thô 3 lối (tích cực/tiêu cực/trung tính, nhóm sentiment của GoEmotions) chia sẻ bộ mã hóa, với CE cộng — bản tương đồng trực tiếp của mất mát âm-tiết+từ của J-ToneNet. Đo xem head thô có nâng macro-F1 nhãn tinh như cách thanh-điệu-từ nâng thanh-điệu-âm-tiết (+3 điểm) hay không. **(D-B)**
- **Bắt buộc báo cáo phân tầng theo độ dài trong bộ khung đánh giá (điểm 4).** Tạo phẩm cụ thể: mọi bảng đánh giá báo cáo metric chia theo độ dài lượt (và vị trí trong hội thoại). J-ToneNet cho thấy một mô hình có thể trông ổn ở trung bình trong khi đảo ngược theo độ dài — sàn recall của Pebble trên severity phải giữ vững *trong mỗi khoảng độ dài*, không chỉ tổng thể. **(D-G)**
- **Coi R-Net (điểm 5) là hạt giống thiết kế cho bản thay thế học-được cuối cùng của heuristic `energy` — nhưng xác thực trên giọng trẻ tự phát trước.** Tạo phẩm cụ thể: một đặc trưng thời lượng/nhịp điệu `(dur, dur−mean)` mỗi từ, cấp vào một transformer nhỏ, ánh xạ tới chiều `energy`. Cổng việc thăng cấp nó từ heuristic sang học-được dựa trên việc nó có vượt heuristic *trên giọng tự phát* hay không, theo cảnh báo của bài này. **(D-D)**

### Lăng kính sức khỏe tâm thần trẻ em

- **Sự ủng hộ trực tiếp của tác giả cho ca sử dụng trẻ em.** Nhận xét kết luận của bài (nhận xét kết luận d) nêu rõ "các ứng dụng lâm sàng sàng lọc giọng nói trẻ em về việc tạo thanh điệu" là một mục tiêu — một cầu nối hiếm hoi trên-giấy từ mô hình hóa thanh điệu tới sàng lọc hướng-tới-trẻ-em. Đây là sự ủng hộ có thể trích dẫn cho việc nhánh luận điểm tin-nhắn-giọng-nói của Pebble tồn tại.
- **Phương thức là prosody, không phải nội dung từ vựng — một lợi thế về quyền riêng tư và register.** Một đường bao f0 mang *cách* một đứa trẻ nói, không phải *từ gì*; với một sản phẩm hướng-tới-trẻ-em, một tháp prosody không bao giờ cần bản ghi (transcript) là bề mặt PII nhỏ hơn ASR-rồi-văn-bản. Pipeline normLogF0 (điểm 1) theo bản chất là không-cần-transcript.
- **Trần độ-hợp-lệ-chuyển-giao: đây là thanh điệu Mandarin, không phải cảm xúc, và phần lớn là giọng đọc của người lớn.** Mọi con số ở đây là *định-danh-thanh-điệu-từ-vựng* (thanh điệu nào trong 4), không phải *trạng thái cảm xúc*. Ánh xạ từ đường bao f0 → cảm xúc/kích thích là một nhiệm vụ khác, chưa được chứng minh; J-ToneNet xác thực *bộ máy bộ-mã-hóa-trên-đường-bao-f0*, không phải mục tiêu prosody→affect. Và các con số mạnh (91%) là giọng **đọc** từ **sinh viên đại học người lớn**; giọng trẻ tự phát là chế độ mà chính bài này hoạt động kém (61,7%).
- **Chế độ thất bại chính xác là chế độ của Pebble.** Giọng nói tự phát, dài hơn, tự nhiên — bản tương đồng gần nhất với một đứa trẻ nói tự do vào một ứng dụng đồng hành — là nơi độ chính xác rơi xuống ~62% và nơi thành phần nhịp điệu (R-Net) ngừng giúp ích. Pebble không được giả định các cải thiện giọng-đọc chuyển giao được; tiên nghiệm trung thực cho prosody trẻ tự phát là "khó, gần các con số hội thoại."
- **Giảm thiểu / đạo đức.** (1) Giữ tháp giọng nói **chặt chẽ ở v2 và sau một flag**; không để một tín hiệu prosody chưa xác thực chạm vào quyết định an toàn/độ-nghiêm-trọng ở v1. (2) Chuẩn hóa f0 theo từng người nói ngầm là một hồ sơ *sinh trắc* theo-từng-trẻ — lưu dưới dạng dải theo-từng-phiên tạm thời, không phải dấu giọng (voiceprint) lưu lâu dài. (3) Bất kỳ tuyên bố sàng lọc thanh-điệu/prosody giọng trẻ nào cũng cần kiểm duyệt lâm sàng/đạo đức (tác giả gọi chính kết quả của họ là "sơ bộ"); Pebble nên phản chiếu sự khiêm tốn đó.

### Hạn chế & câu hỏi mở cho Pebble

- **Mâu thuẫn với yêu cầu nhiệm vụ (và với bài #33 ToneNet):** J-ToneNet **không** được đối chuẩn so với ToneNet (#33). ToneNet báo cáo ~99,16% trên dữ liệu *âm-tiết-cô-lập SCSC sạch* (CNN mel-spectrogram); J-ToneNet báo cáo 91,0% đọc / 61,7% hội thoại trên giọng *chỉ-f0, liên tục*. Các con số này **không thể so sánh** — đầu vào khác (spectrogram vs f0), đơn vị khác (cô lập vs liên tục), corpus khác. Bất kỳ ai trích dẫn "J-ToneNet vượt ToneNet" sẽ sai. Tuyên bố bảo vệ được hẹp hơn: *trên phân loại thanh điệu giọng-liên-tục chỉ-f0, một transformer kiểu BERTSUM với hợp nhất nhịp điệu và học chung vượt các baseline cấp đoạn RF/FFN/1D-CNN 12–34 điểm.*
- **Con số nguồn-đơn.** Không có bản công khai thứ hai chứa Bảng 3 (trang ISCA chỉ có tóm tắt; bản mở rộng JASA bị tường phí). Con số đã-xác-minh-bản-chép từ camera-ready, không tái lập độc lập — đánh dấu như vậy trong mọi trích dẫn Pebble.
- **Khoảng trống với kiến trúc chỉ-văn-bản v1 của Pebble.** J-ToneNet là một tháp *âm thanh*; không gì trong nó có thể là một head trên NeoBERT. Áp dụng bất kỳ phần nào buộc một thiết kế hợp nhất đa-tháp mà v1 không có và `docs/decisions.md` chưa cấp ngân sách. Đây là phụ thuộc phạm vi v2, không phải đòn bẩy v1.
- **Không có nhãn affect ở đâu cả.** Bài chứng minh f0→*định-danh-thanh-điệu*; Pebble cần f0→*affect/severity*. Không có bộ dữ liệu nào trong bài này cung cấp mục tiêu emotion/severity cho tháp prosody, nên D-H không được gì về phía *nhãn* — chỉ *pipeline đặc trưng* chuyển giao. Câu hỏi mở: corpus công khai nào ghép giọng trẻ (hoặc ít nhất tự phát) f0 với nhãn affect/kích thích? J-ToneNet không trả lời.
- **Điểm yếu giọng-tự-phát của R-Net làm suy yếu kế hoạch head energy.** Pebble muốn nhịp điệu prosody làm tín hiệu `energy` học-được; tháp nhịp điệu của bài này chính là thành phần *không* tổng quát hóa được sang giọng tự phát. Câu hỏi mở cho Pebble: liệu một bộ mã hóa thời-lượng/nhịp-điệu có vượt heuristic `energy` v1 trên giọng *trẻ tự phát*, hay heuristic vẫn cạnh tranh? Phải kiểm tra trước bất kỳ việc thăng cấp nào.
