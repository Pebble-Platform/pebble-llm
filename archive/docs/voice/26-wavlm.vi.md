# Bài báo 26 — WavLM: Tiền-huấn luyện Tự-giám-sát Quy-mô-lớn cho Xử lý Tiếng nói Toàn-ngăn-xếp (Full Stack)

## 1. Thông tin thư mục

**Tiêu đề:** WavLM: Large-Scale Self-Supervised Pre-Training for Full Stack Speech Processing

**Tác giả:** Sanyuan Chen, Chengyi Wang, Zhengyang Chen, Yu Wu (liên hệ, yuwu1@microsoft.com), Shujie Liu, Zhuo Chen, Jinyu Li, Naoyuki Kanda, Takuya Yoshioka, Xiong Xiao, Jian Wu, Long Zhou, Shuo Ren, Yanmin Qian, Yao Qian, Jian Wu, Michael Zeng, Xiangzhan Yu, Furu Wei. (Ba tác giả đầu đóng góp ngang nhau; công trình thực hiện tại Microsoft.)

**Đơn vị:** Microsoft (Azure Speech / Microsoft Research), Đại học Giao thông Thượng Hải (SJTU), Học viện Công nghệ Cáp Nhĩ Tân (HIT).

**Năm / nơi công bố:** Đăng trên *IEEE Journal of Selected Topics in Signal Processing* (JSTSP), Tập 16, Số 6, tháng 10/2022, tr. 1505–1518. PDF cục bộ là arXiv:2110.13900v5 (cs.CL, 17/06/2022). DOI 10.1109/JSTSP.2022.3188113. Mã nguồn + checkpoint tại https://aka.ms/wavlm.

**Từ khóa (nguyên văn):** "Self-Supervised Learning, Speech Pre-Training".

## 2. Động lực vấn đề

Học tự-giám-sát (SSL) đã thành công trong NLP và trong tiếng nói cho các tác vụ ASR/phân loại âm vị, nhưng "ở các tác vụ tiếng nói khác, việc huấn luyện mô hình từ đầu với tập dữ liệu chuyên-tác-vụ vẫn là thực hành tiêu chuẩn." Các tác vụ tiếng nói phi-ASR (nhận dạng người nói, phân tách-người-nói/diarization, tách nguồn/separation, cận-ngôn-ngữ/paralinguistics & cảm xúc) thiếu dữ liệu có nhãn và sẽ hưởng lợi nhiều nhất từ một bộ mã hóa âm học (acoustic encoder) tiền-huấn-luyện đa-dụng. Luận điểm của bài là *một* mô hình SSL có thể phục vụ **toàn ngăn xếp** các tác vụ tiếng nói thay vì một họ mô hình chuyên-tác-vụ.

Hai nhược điểm cụ thể của các mô hình SSL trước (HuBERT, wav2vec 2.0) tạo động lực cho thiết kế:
1. Chúng "chưa thỏa đáng cho các tác vụ đa-người-nói" — tách nguồn trên nền HuBERT chỉ cải thiện biên so với huấn luyện từ đầu, vì tiền-huấn-luyện không thúc đẩy phân biệt người nói và không có âm thanh đa-người-nói.
2. Chúng phụ thuộc dữ liệu sách-nói (Libri-Light / LibriSpeech); ">90% dữ liệu âm thanh xuất phát từ sách nói," và sự lệch miền đó làm giảm hiệu năng các tác vụ hạ nguồn có đặc tính âm học khác với giọng đọc sạch.

## 3. Vị trí trong tài liệu

WavLM mở rộng mô thức **HuBERT** (gom cụm offline / dự đoán-có-mặt-nạ). Bài phân SSL thành ba họ: sinh-mẫu (autoencoding/dự đoán khung tự-hồi-quy), phân-biệt (CPC, wav2vec/vq-wav2vec/wav2vec 2.0, DiscreteBERT, HuBERT, w2v-BERT), và đa-tác-vụ (PASE/PASE+, UniSpeech). Bài đặt mình đối chiếu với benchmark **SUPERB** (Yang và cộng sự), nơi HuBERT là mô hình tổng-quát tốt nhất trước đó, và với **UniSpeech-SAT** (HuBERT có nhận biết người nói). WavLM tuyên bố là "công trình đầu tiên khám phá SSL cho các tác vụ toàn-ngăn-xếp thay vì tập trung vào ASR hay một tác vụ cụ thể," đạt được điều này "kể cả khi không phải mở rộng kích cỡ mô hình lên 8 tỷ tham số" (một lời đối chiếu với BigSSL cùng thời).

## 4. Phương pháp — ba sửa đổi so với HuBERT

WavLM = bộ-khung HuBERT + hàm mất-mát dự-đoán-có-mặt-nạ + **ba thay đổi bổ sung**:

**(A) Khử nhiễu + dự đoán tiếng nói có mặt nạ (đổi mới cốt lõi).** Đầu vào là tiếng nói *mô-phỏng nhiễu/chồng-lấn*; mục tiêu là dự đoán nhãn-giả của tiếng nói **gốc (sạch) của người nói chính** trên vùng bị mặt nạ (đích là cụm k-means kiểu HuBERT trên MFCC, rồi trên đặc trưng ẩn ở vòng lặp 2). Cụ thể (Thuật toán 1): với 20% câu thoại, một câu chính được trộn với hoặc một câu phụ từ cùng lô (tỉ số năng lượng U(−5,5) dB) hoặc một đoạn nhiễu DNS (tỉ số năng lượng U(−5,20) dB); độ chồng-lấn bị ràng buộc **< 50%** để người nói chính luôn áp đảo/dài hơn và vẫn nhận diện được. Mô hình phải khử nhiễu + tách + dự đoán nội dung của người nói chính — qua đó ngầm ép biểu diễn phải có khả năng phân biệt người nói, tách nguồn, và tăng cường (enhancement). Mất mát là entropy chéo trên vùng mặt nạ qua các ID cụm, chỉ áp ở các chỉ số bị mặt nạ (PT 7).

**(B) Thiên-lệch vị trí tương đối có cổng (gated relative position bias, gREP).** Thay thế nhúng vị trí tương đối dạng tích chập của wav2vec2/HuBERT bằng một thiên-lệch vị trí tương đối **có cổng** cộng vào logit chú ý (PT 3–6). Một nhúng vị trí tương đối dạng bucket với n=320 bucket, giãn theo logarit tới độ lệch tối đa m=800, dùng chung cho mọi lớp. Cổng `g_i = sigmoid(q_i·u)` điều kiện-hóa thiên-lệch vị trí theo **nội dung tiếng nói hiện tại** — "cùng một độ lệch khoảng cách ... có vai trò khác nhau nếu một khung là khoảng lặng còn khung kia thuộc đoạn có tiếng nói." Cải thiện tác vụ nội dung (ASR/PR) với chi phí tham số/tốc độ gần như bằng không.

**(C) Mở rộng + đa dạng hóa dữ liệu tiền-huấn-luyện → "Mix 94k giờ."** 60k giờ Libri-Light + 10k giờ GigaSpeech (sách nói/podcast/YouTube; chỉ dùng 10k giờ sạch trong 40k) + 24k giờ VoxPopuli tiếng Anh (ghi âm Nghị viện Châu Âu) = **94k giờ** âm thanh tiếng Anh công khai, so với dữ liệu chỉ-sách-nói của HuBERT/wav2vec2. Nền âm đa dạng làm giảm thiên-lệch sách-nói.

Cộng thêm một **mẹo ổn định huấn luyện** cho fp16: tái-co-giãn logit chú ý bằng cách trừ giá trị lớn nhất theo hàng trước khi exp (PT 8, hệ số c=32) để tránh tràn NaN trên mô hình lớn.

## 5. Các biến thể mô hình và thiết lập tiền-huấn-luyện

| Biến thể | Lớp | Ẩn | Đầu | Tham số | Dữ liệu tiền-HL | Bước | % khử-nhiễu / xác-suất-trộn-nhiễu |
|---|---|---|---|---|---|---|---|
| WavLM Base | 12 | 768 | 8 | **94.70M** | LS 960 giờ | 400k | 20% / p_n=0 |
| WavLM Base+ | 12 | 768 | 8 | 94.70M | Mix 94k giờ | 1M | 20% / p_n=10% |
| WavLM Large | 24 | 1024 | 12 | **316.62M** | Mix 94k giờ | 700k | 20% / p_n=10% |

Bộ mã hóa đặc trưng tích chập: 7 khối tích-chập-thời-gian, 512 kênh, stride (5,2,2,2,2,2,2), kernel (10,3,3,3,3,2,2) → mỗi khung đầu ra ≈ 25 ms âm thanh với stride 20 ms (tức tốc độ khung 50 Hz). Base dùng đặc trưng lớp-6 của HuBERT Base vòng-1 làm đích gom cụm; Base+/Large dùng đặc trưng lớp-9 của HuBERT Base vòng-2 đã phát hành.

## 6. Thí nghiệm và kết quả

### 6.1 Benchmark biểu-diễn-đa-dụng SUPERB (Bảng I)

Mô hình tiền-huấn-luyện bị **đóng băng**; các tác vụ hạ nguồn tiêu thụ một **tổng-có-trọng-số khả-học của trạng thái ẩn mọi lớp**. 15 tác vụ trải các khía cạnh nội dung / người nói / ngữ nghĩa / cận-ngôn-ngữ / sinh-mẫu. Điểm tổng = trung bình trên các tác vụ (QbE ×100; tỉ lệ lỗi → 1−lỗi).

Các số SUPERB chính (Bảng I), tập trung vào cột **Nhận dạng Cảm xúc (ER, khía cạnh cận-ngôn-ngữ, IEMOCAP, độ chính xác ↑)** và điểm tổng:

| Mô hình | Tham số | ER Acc ↑ | SID Acc ↑ | SD DER ↓ | Tổng ↑ |
|---|---|---|---|---|---|
| HuBERT Base | 94.68M | 64.92 | 81.42 | 5.88 | 70.9 |
| WavLM Base | 94.70M | **65.94** | 84.51 | 4.55 | 72.0 |
|   – bỏ tác-vụ-khử-nhiễu | 94.70M | 65.55 | 84.39 | 6.03 | 71.7 |
|   – bỏ sửa-đổi-cấu-trúc | 94.68M | 65.60 | 84.74 | 4.72 | 71.9 |
| WavLM Base+ | 94.70M | **68.65** | 89.42 | 3.50 | 73.4 |
| wav2vec 2.0 Large | 317.38M | 65.64 | 86.14 | 5.62 | 70.4 |
| HuBERT Large | 316.61M | 67.62 | 90.33 | 5.75 | 72.2 |
| **WavLM Large** | 316.62M | **70.62** | 95.49 | 3.24 | **74.6** |

WavLM Large tốt nhất ở điểm tổng (74.6) và "vượt HuBERT Large ở 14 tác vụ con, ... cải thiện tuyệt đối 2.4 điểm ở đánh giá tổng thể." Lưu ý **WavLM Base+ (94.7M) vượt HuBERT Large và wav2vec 2.0 Large (≈317M) ở điểm tổng** dù nhỏ hơn ~3 lần. Riêng ER, tiến triển là HuBERT Base 64.92 → WavLM Base 65.94 → WavLM Base+ 68.65 → WavLM Large 70.62; bước nhảy lớn nhất đến từ quy mô dữ liệu (Base→Base+: +2.71 tuyệt đối).

**Phân tích trọng-số-lớp (Hình 2–3):** lớp dưới mang thông tin người nói; lớp trên mang nội dung/ngữ nghĩa; lớp giữa quan trọng nhất cho tác vụ người nói ở mô hình Large. (ER cận-ngôn-ngữ rút từ một hỗn hợp — chính thiết kế tổng-có-trọng-số cho phép một encoder đóng băng phục vụ cả tác vụ người nói lẫn nội dung.)

### 6.2 Hai phép loại-bỏ (ablation) (Bảng I, nội dòng)

- **bỏ tác-vụ-khử-nhiễu** (gỡ trộn nhiễu/chồng-lấn mô phỏng): tổn hại lớn nhất là **diarization** (DER 4.55 → 6.03) và SD/SS/SV suy giảm — xác nhận tác-vụ-khử-nhiễu là thứ tạo ra năng lực đa-người-nói. ER gần như không đổi (65.94 → 65.55).
- **bỏ sửa-đổi-cấu-trúc** (gỡ thiên-lệch vị trí tương đối có cổng): tổn hại **PR và ASR** (tác vụ nội dung) — xác nhận gREP là đòn bẩy tác-vụ-nội-dung. ER về cơ bản không đổi (65.94 → 65.60).

### 6.3 SOTA chuyên-tác-vụ vượt SUPERB (encoder mở-băng nơi có ghi chú)

- **Nhận dạng người nói (Bảng II, VoxCeleb1):** WavLM Large đạt **0.383% / 0.480% / 0.986% EER** trên Vox1-O/E/H (với fine-tune biên-lớn + hiệu chỉnh điểm), vượt ECAPA-TDNN và đội thắng VoxSRC-2021. Cải thiện EER tương đối >35% so với Fbank.
- **Diarization (Bảng III, CALLHOME):** WavLM Large + EEND-vector-clustering đạt **10.35% DER** tổng (SOTA mới), giảm tương đối 12.6% so với EEND-EDA-clustering. Chỉ riêng WavLM Base+ đã vượt HuBERT Large.
- **Tách nguồn tiếng nói (Bảng IV, LibriCSS):** WavLM Large (đóng băng) trung bình **6.0% WER**, giảm tương đối 27.7% so với baseline Conformer; 32.5% tương đối ở mức chồng-lấn 40%. (Đóng băng tốt hơn mở-băng vì tập đánh giá là âm thanh họp thật so với hỗn hợp huấn luyện mô phỏng.)
- **ASR (Bảng V–VI, LibriSpeech 960h):** WavLM Large đạt **1.8% / 3.2% WER** trên test-clean/test-other — ngang ngửa wav2vec 2.0 / HuBERT (ASR không phải nơi WavLM tập trung lợi thế). Mở rộng mô hình giảm WER tương đối 38% từ Base→Large.

## 7. Hạn chế / hướng tương lai tác giả nêu

Kết luận ngắn gọn: hướng tương lai gồm (1) mở rộng kích cỡ mô hình, (2) nén mô hình để triển khai ("tài nguyên thời-gian-kiểm-tra hạn chế trong tình huống thực"), và (3) đồng-học SSL văn-bản+tiếng-nói. Không có phân tích về công bằng, nhân khẩu, tiếng nói trẻ em, hay ngoài-tiếng-Anh — WavLM là **chỉ-tiếng-Anh** theo thiết kế (dùng rõ ràng chỉ tập con tiếng Anh 24k giờ của VoxPopuli đa ngôn ngữ). Giao thức SUPERB encoder-đóng-băng "không thể cho thấy sức mạnh của mô hình tiền-huấn-luyện," nên có các thí nghiệm chuyên-tác-vụ với encoder mở-băng.

---

## Deep research — full-PDF read (2026-06-16)

> Đọc đối chiếu với phiên bản công bố IEEE JSTSP 2022 (tập 16(6):1505–1518, DOI
> 10.1109/JSTSP.2022.3188113); PDF cục bộ là `pdfs/26-wavlm.pdf` (arXiv:2110.13900v5). Các số bên
> dưới được kiểm chéo với bảng benchmark SUPERB và các thẻ `aka.ms/wavlm` / HuggingFace
> `microsoft/wavlm-*` của Microsoft. WavLM là ứng viên **bộ mã hóa âm học cho phương thức tin-nhắn-thoại
> của Pebble** — một luồng đầu vào riêng, tùy chọn, tách biệt với bộ mã hóa *văn bản* NeoBERT, không
> phải thay thế nó. Phần này soi mọi điểm chuyển-giao qua lăng kính đó.

### Ghi chú truy cập nguồn

- Toàn văn được trích bằng `pdftotext "pdfs/26-wavlm.pdf" -` (công cụ Read không render được PDF;
  theo ghi nhớ repo `pdf-extraction-local.md`). Đọc đầu-cuối: phương pháp (§IV), Thuật toán 1
  (mô phỏng nhiễu/chồng-lấn), Bảng I (SUPERB, cả 15 tác vụ kể cả ER), Bảng II–VI (SV/SD/SS/ASR),
  và hai ablation nội dòng.
- **Các số đã kiểm-chứng-web + dấu vết:**
  - ER Acc / số giờ tiền-HL — truy vấn "WavLM SUPERB emotion recognition accuracy WavLM Large
    70.62 IEMOCAP HuBERT" → xác nhận WavLM Large ER **70.62%** và tiền-HL 94k giờ
    (Libri-Light 60k + GigaSpeech 10k + VoxPopuli 24k) qua
    https://arxiv.org/pdf/2110.13900v2 và HuggingFace `microsoft/wavlm-large`. **✔**
  - Khử-nhiễu/gREP/thành-phần-dữ-liệu — truy vấn "WavLM 94k hours pre-training ... masked speech
    denoising gated relative position bias" → xác nhận 20%-câu bị làm nhiễu, thiên-lệch vị trí
    tương đối có cổng, và phân chia ba-corpus qua trang chủ-đề WavLM emergentmind + README unilm. **✔**
  - Số tham số / số bước / +2.4-điểm tổng / 14 tác-vụ-con — WebFetch
    https://ar5iv.labs.arxiv.org/html/2110.13900 xác nhận 94.70M / 316.62M, 400k/1M/700k bước,
    "+2.4 điểm" tổng, "14 tác vụ con." **✔** *Lưu ý:* ar5iv lệch-hàng cột ER, in HuBERT Large ER
    thành 70.62 (= giá trị của WavLM Large). Cột ER trong PDF cục bộ là danh sách tuần tự sạch cho
    **HuBERT Large 67.62 / WavLM Large 70.62**, nhất quán nội tại và khớp thứ tự bảng xếp hạng
    SUPERB công bố; tôi dùng giá trị PDF và gắn nhãn HuBERT Large ER **≈** (có ghi nhận xung đột
    ar5iv), WavLM Large ER **✔**.

### Bài báo thực sự làm gì (số chính xác, tham chiếu bảng)

- **Một bộ mã hóa âm học đóng băng, 15 tác vụ SUPERB**, qua tổng-có-trọng-số khả-học theo lớp
  (Bảng I). WavLM Large tổng **74.6 ✔** (+2.4 tuyệt đối so HuBERT Large 72.2 ✔), tốt nhất 14/15.
- **Nhận dạng Cảm xúc (IEMOCAP, 4 lớp, độ chính xác):** WavLM Large **70.62% ✔**, WavLM Base+
  **68.65% ✔**, WavLM Base **65.94% ✔**, HuBERT Base 64.92 ✔, wav2vec 2.0 Large 65.64 ✔,
  HuBERT Large **67.62 ≈** (Bảng I, cột ParaL/ER). Quy mô dữ liệu là đòn bẩy ER chủ đạo
  (Base→Base+ = +2.71 tuyệt đối từ 960 giờ→94k giờ).
- **Ba sửa đổi, hai ablation** (Bảng I): bỏ **tác-vụ-khử-nhiễu** làm tăng DER diarization 4.55→6.03
  ✔ (năng lực đa-người-nói đến từ khử nhiễu); bỏ **thiên-lệch vị trí tương đối có cổng** làm giảm
  PR/ASR ✔ (đòn bẩy nội dung). Cả hai ablation đều không làm ER dịch đáng kể (±0.4), tức ER chủ yếu
  cưỡi trên quy mô dữ liệu + tín hiệu phân-biệt-người-nói, không phải trên gREP.
- **Tiền-huấn-luyện:** 94k giờ tiếng Anh công khai (60k Libri-Light + 10k GigaSpeech + 24k VoxPopuli)
  ✔; Base 400k / Base+ 1M / Large 700k bước ✔; 20% câu bị làm nhiễu, chồng-lấn < 50% ✔.
- **SOTA vượt SUPERB:** SV VoxCeleb1 0.383/0.480/0.986% EER ✔; CALLHOME diarization 10.35% DER ✔;
  LibriCSS tách nguồn 6.0% WER trung bình (−27.7% tương đối) ✔; LibriSpeech ASR 1.8/3.2% WER ✔.

### Phần trực tiếp hữu ích cho Pebble (mỗi phần gắn Mã Quyết định)

1. **WavLM làm bộ mã hóa âm học tin-nhắn-thoại cho đầu cận-ngôn-ngữ/cảm xúc [D-A, D-D].**
   Tương tự chính xác NeoBERT-cho-văn-bản. WavLM Large 70.62% / Base+ 68.65% trên SUPERB ER là trần
   công bố cho một encoder SSL *đóng băng* + đầu nhẹ trên cảm xúc tiếng nói tiếng Anh — một mục tiêu
   cụ thể và một kiến trúc (encoder đóng băng + tổng-trọng-số-lớp + đầu nhỏ). WavLM Base+ (94.7M) là
   điểm ngọt kích-cỡ/chất-lượng: vượt cả hai baseline ~317M Large ở điểm tổng mà vẫn triển-khai-được
   cho trẻ em.
2. **Encoder đóng băng + tổng-có-trọng-số-lớp khả-học, không chỉ lớp-cuối [D-A, D-E].** Giao thức
   SUPERB (và phân tích trọng-số-lớp của WavLM, Hình 2–3) cho thấy các tác vụ khác nhau cần lớp khác
   nhau; nội dung cận-ngôn-ngữ/cảm xúc *phân tán*, không nằm ở lớp trên cùng. Cho đầu thoại của Pebble,
   điều này ủng hộ đọc-ra tổng-có-trọng-số trên các lớp WavLM thay vì gộp một-khung kiểu-CLS — và cho
   phép trọng số WavLM giữ đóng băng (rẻ, đúng tinh thần fine-tune-theo-giai-đoạn v1 của Pebble).
3. **Mức độ nghiêm trọng/cường độ làm đích hồi quy từ đặc trưng WavLM [D-D].** Đầu `severity` của
   Pebble là hồi quy (metric Pearson, chuyển-giao cường độ). Các *chiều* cảm xúc tiếng nói
   (kích-hoạt/arousal–hóa-trị/valence) là tương tự âm thanh; đặc trưng WavLM đóng băng + một bộ hồi
   quy nhỏ là con đường tiêu chuẩn, rẻ, và độ-nhạy-quy-mô-dữ-liệu của ER (Base→Base+ +2.71) cho Pebble
   biết **với luồng thoại, nhiều âm thanh không-nhãn đa dạng hơn thắng một đầu lớn hơn** — đúng bài học
   mà D-F/D-H thúc đẩy ở phía văn bản.
4. **Nguyên tắc đa-dạng-miền-hơn-lượng-sạch [D-F, D-H].** Phát hiện chủ đạo của WavLM là thêm âm thanh
   phi-sách-nói (podcast/YouTube/nghị viện) — không chỉ thêm sách nói — mới là thứ nâng
   ASV/OOD-ASR/IC/SF/**ER**. Đây là sinh-đôi âm-thanh của quyết định MLM-thích-nghi-miền (D-F) và
   thay-thế-dữ-liệu (D-H) của Pebble: khớp register/miền của corpus *không-nhãn* dùng tiền-huấn-luyện
   là đòn bẩy bậc nhất, và một encoder huấn-luyện-trên-sách-nói sẽ phục vụ kém giọng trẻ tự phát.
5. **Tác-vụ tiền-huấn-luyện khử-nhiễu/chồng-lấn như đòn bẩy bền-vững [D-A].** WavLM nung sẵn tính bền
   với nhiễu/chồng-lấn vào encoder qua mục tiêu khử-nhiễu-có-mặt-nạ (ablation DER chứng minh). Tin
   nhắn thoại của trẻ thì nhiễu, xa-trường, thường đa-giọng (anh chị em, TV) — WavLM *đã* là encoder
   SSL được xây rõ ràng cho điều đó, đây là lập luận tốt nhất để chọn nó thay vì wav2vec 2.0 / HuBERT
   thuần cho luồng thoại của Pebble.

### Mỗi phần giúp Pebble thành công ra sao (hành động theo đầu / theo cấu hình)

- **Đầu cảm-xúc-thoại (ánh xạ tới `emotion` của Pebble):** thêm một thí nghiệm `voice_emotion` —
  đóng băng `microsoft/wavlm-base-plus`, trọng-số-lớp khả-học, một MLP 2-lớp trên đặc trưng
  tổng-trọng-số gộp-trung-bình, huấn luyện trên corpus SER tiếng Anh (IEMOCAP/MSP-Podcast) ánh xạ về
  lược đồ 12-nhãn GoEmotions của Pebble khi có thể. Ngưỡng thành công mượn từ SUPERB: ≥ Base+ 68.65% /
  Large 70.62% độ chính xác kiểu-IEMOCAP 4-lớp trên *lát thoại*; đây là một đầu *riêng* với đầu văn
  bản `emotion`, hợp-nhất ở hạ nguồn, không thay thế. [D-A]
- **Đầu mức-độ-nghiêm-trọng-thoại (ánh xạ tới `severity`):** tái dùng cùng đặc trưng WavLM đóng băng
  cho một đầu hồi quy Pearson trên nhãn arousal/cường độ; điều này cho Pebble một tín hiệu cường độ
  phía thoại song song với chuyển-giao cường độ phía văn bản WASSA/SemEval (D-D), để Decision Engine
  có thể kiểm-chứng-chéo mức nghiêm trọng văn bản bằng mức nghiêm trọng ngôn-điệu. [D-D]
- **Cấu hình kích-cỡ encoder:** mặc định **WavLM Base+ (94.7M)** cho luồng thoại — khớp ngân sách
  tổng ~250M của NeoBERT, chạy trên cùng stack Kaggle một-GPU, và bài chứng minh nó vượt các encoder
  lớn gấp 3 lần ở metric tổng. Chỉ dành Large nếu đầu thoại là nút thắt. [D-A]
- **Cấu hình tiền-huấn-luyện/thích-nghi:** nếu có lúc huấn luyện một encoder thoại thích-nghi-miền,
  sao chép nguyên tắc dữ liệu — trộn vào âm thanh tự-phát/nhiễu gần-trẻ-em, đừng chỉ thêm giọng đọc
  sạch; và giữ bật mục tiêu khử-nhiễu-có-mặt-nạ (đó là thứ mua được tính bền đa-người-nói/nhiễu).
  [D-F, D-H]

### Lăng kính sức khỏe tâm thần trẻ em (tính hợp lệ chuyển-giao, rủi ro, giảm-thiểu, đạo đức)

- **Tính hợp lệ chuyển-giao — tiếng Anh người lớn, đọc+tự-phát, KHÔNG phải giọng trẻ.** Mọi số WavLM
  trên corpus người lớn: IEMOCAP (cặp diễn người lớn), VoxCeleb (người nổi tiếng), LibriSpeech (người
  đọc sách người lớn), VoxPopuli (nghị sĩ người lớn). **Âm học của trẻ khác hẳn** — F0 cao hơn, đường
  thanh ngắn hơn, cấu trúc formant khác, nhiều ngập ngừng hơn, ngôn điệu chưa chín. Độ chính xác ER
  WavLM 70.62% trên IEMOCAP người lớn **KHÔNG** chuyển sang một đầu thoại trẻ em; coi nó nghiêm ngặt
  là *tương tự cận-trên / bằng chứng kiến trúc*, đúng như cách số người-lớn của FAIIR được xử lý cho
  văn bản. Đây là cảnh báo chuyển-giao chịu-tải.
- **Rủi ro — lệch miền + lệch tuổi kép.** Chính luận điểm của WavLM (thiên-lệch sách-nói gây hại khi
  âm học hạ nguồn khác) chống lại Pebble hai lần: cả register trẻ *và* ghi âm tại-nhà tùy tiện đều
  khác hỗn hợp tiền-huấn-luyện. Giảm-thiểu: bất kỳ luồng thoại nào cũng phải kiểm-chứng trên một lát
  giữ-lại của *tin nhắn thoại trẻ thật* (hoặc tập SER giọng-trẻ mở gần nhất), không bao giờ tuyên bố
  từ SUPERB.
- **Rủi ro — danh tính người nói được học rất mạnh (SID 95.49%, SV 0.383% EER).** WavLM, theo thiết
  kế, là bộ-lấy-vân-tay-giọng-nói xuất sắc. Với sản phẩm hướng-trẻ đó là *hiểm họa quyền riêng tư*:
  nhúng WavLM có thể tái-định-danh một đứa trẻ qua giọng. Giảm-thiểu: không lưu nhúng người-nói WavLM
  thô; chỉ trích đầu ra của đầu cảm-xúc/nghiêm-trọng; nếu phải cache nhúng, coi như PII sinh trắc theo
  cùng quản-trị Pebble áp cho văn bản (đồng thuận, tối-thiểu-hóa, lưu-trữ-kiểm-soát), và ưu tiên
  trích-xuất-đặc-trưng trên-thiết-bị.
- **Đạo đức — đồng thuận theo phương thức.** Giọng nói là sinh trắc; một luồng thoại hướng-trẻ cần
  đồng thuận phù-hợp-độ-tuổi rõ ràng và thông báo người-giám-hộ vượt mức văn bản cần. WavLM không cung
  cấp phân tích công bằng hay trẻ em, nên Pebble sở hữu hoàn toàn đánh giá đó.
- **Giảm-thiểu hợp với tinh thần sàn-recall của Pebble:** giữ đầu thoại *tư vấn* vào Decision Engine,
  không bao giờ là cò-an-toàn tự-trị — cùng bất biến sản phẩm như các đầu văn bản; hợp nhất văn-bản
  +thoại và để lớp-luật / lối-người chịu trách nhiệm leo thang.

### Hạn chế & câu hỏi mở cho Pebble (gồm ≥1 mâu thuẫn/khoảng trống)

- **Mâu thuẫn với kế hoạch Pebble (phương thức + chế độ nhãn).** Pebble v1 (`docs/decisions.md`) là
  mô hình NeoBERT **văn bản** trên *văn bản sức-khỏe-tâm-thần nhãn-bạc*, mức-lượt. WavLM là encoder
  **âm học đóng băng** đánh giá trên *nhãn vàng* cảm-xúc-tiếng-nói (IEMOCAP), mức-câu-thoại. Luồng
  thoại do đó **ngoài phạm vi v1** — chọn WavLM nghĩa là thêm phương thức thứ hai, encoder thứ hai,
  đường-ống dữ-liệu-có-nhãn (âm thanh) thứ hai, và quản-trị sinh trắc. Đọc thẳng: WavLM là ứng viên
  *tin-nhắn-thoại v2+* mạnh, không phải thành phần v1. Nêu rõ điều này để không lẫn với lộ trình văn
  bản v1.
- **Mâu thuẫn với khung ModernBERT/NeoBERT (D-A).** Quyết định encoder-backbone D-A, trong phần còn
  lại của corpus, là cuộc đọ encoder *văn bản* (NeoBERT vs ModernBERT vs MentalBERT). WavLM hoàn toàn
  không dự cuộc đó; nó trả lời một câu hỏi D-A *khác* (encoder **âm thanh** nào cho luồng thoại). Đừng
  để tuyên bố "vượt HuBERT/wav2vec2" của WavLM rò sang lập luận D-A văn bản — chúng rời nhau.
- **Không có cấu trúc cảm xúc thứ-bậc/nhận-biết-khoảng-cách (so với D-C).** SUPERB ER là độ chính xác
  4-lớp phẳng; WavLM không cho Pebble gì về mất-mát mức-độ thứ-bậc hay hiệu chỉnh sàn-recall (D-C,
  D-G). Đầu nghiêm-trọng-thoại sẽ phải nhập những thứ đó từ quyết định phía văn bản, không phải từ
  bài này.
- **Chỉ-tiếng-Anh.** WavLM chỉ dùng tập con tiếng Anh 24k giờ của VoxPopuli và không đa ngôn ngữ; hỗ
  trợ giọng trẻ phi-tiếng-Anh chưa được giải quyết.
- **Phụ thuộc nhãn-vàng.** Mọi lợi ích ER giả định nhãn được tuyển chọn; Pebble không có nhãn cảm xúc
  giọng-trẻ vàng và sẽ gặp cùng vấn đề nhãn-bạc ở phía âm thanh, *cộng thêm* chi phí thu thập âm thanh
  trẻ — một thế dữ liệu khó hơn hẳn so với luồng văn bản.
- **Câu hỏi mở cần giải trước mọi việc thoại:** có corpus cảm-xúc giọng-trẻ mở với giấy phép
  tái-phân-phối không? Không có nó, luồng thoại không thể kiểm-chứng, và 70.62% của SUPERB là mỏ-neo
  duy nhất (không-chuyển-giao) sẵn có.
