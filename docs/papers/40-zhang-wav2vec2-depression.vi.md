# Bài báo 40 — Cải thiện phát hiện trầm cảm qua giọng nói bằng học chuyển giao với wav2vec 2.0 trong môi trường ít tài nguyên

## 1. Thông tin thư mục

**Tiêu đề:** Improving speech depression detection using transfer learning with wav2vec 2.0 in low-resource environments (Cải thiện phát hiện trầm cảm qua giọng nói bằng học chuyển giao với wav2vec 2.0 trong môi trường ít tài nguyên)

**Tác giả:** Xu Zhang (School of Software Engineering, Xiamen University of Technology), Xiangcheng Zhang (School of Computer and Information Engineering, Xiamen University of Technology, tác giả liên hệ — fufuturbo@163.com), Weisi Chen, Chenlong Li (Xiamen University of Technology), Chengyuan Yu (Jiangxi Agricultural University).

**Năm / nơi công bố:** *Scientific Reports* 14:9543 (2024). Nhận 11/01/2024, chấp nhận 21/04/2024. DOI 10.1038/s41598-024-60278-1. Truy cập mở (CC BY 4.0). Không có bản preprint — Scientific Reports là phiên bản chính thức.

**Tóm tắt một dòng:** Một pipeline phát hiện trầm cảm qua giọng nói đầu-cuối, dùng hai corpus, fine-tune wav2vec 2.0 (toàn bộ các lớp) để lấy đặc trưng cấp khung (frame), nén mỗi đoạn 7 giây bằng khối 1D-CNN + attention pooling cộng tính, rồi phân loại toàn bộ cuộc phỏng vấn bằng đầu thời gian LSTM + self-attention — đạt **F1 79.00% trên DAIC-WOZ (tiếng Anh)** và **F1 90.53% trên CMDC (tiếng Trung)** với một lớp đặc trưng duy nhất và không cần tăng cường dữ liệu, vượt các baseline phát hiện trầm cảm qua giọng nói trước đó trong chế độ ít tài nguyên.

## 2. Vì sao bài báo này nằm trong bộ Pebble

Luận điểm của Pebble bao gồm một **phương thức tin nhắn thoại (voice-message)**: trẻ em có thể gửi các đoạn nói ngắn thay vì gõ văn bản, và Pebble cần một con đường từ âm thanh thô của trẻ tới một tín hiệu `severity` / mức độ căng thẳng. Bài báo này là **pipeline phát hiện trầm cảm wav2vec2 đầu-cuối dễ tái lập nhất** trong bộ — nó đặc tả từng khối (tiền xử lý → trích đặc trưng SSL → bộ mã hóa đoạn → bộ phân loại thời gian), từng siêu tham số, hai corpus công khai, và một thí nghiệm loại bỏ (ablation) cho mỗi thành phần. Đây là phiên bản phía âm thanh của đầu `severity` văn bản của Pebble: nơi Pebble chuyển giao cường độ cảm xúc SemEval/WASSA vào một đầu hồi quy trên văn bản NeoBERT, bài báo này chuyển giao wav2vec 2.0 (thậm chí cả fine-tune cảm xúc IEMOCAP) vào một đầu trầm cảm *nhị phân* trên âm thanh phỏng vấn lâm sàng. Kiến trúc, chiến lược học chuyển giao ít tài nguyên, và các con số F1 là tài liệu tham chiếu cụ thể cho một **đầu phát hiện trầm cảm / căng thẳng qua giọng nói** tương lai của Pebble.

Bài báo này **không** nói về trẻ em (DAIC-WOZ và CMDC là người lớn trong phỏng vấn lâm sàng), **không** ở mức turn-level (một nhãn cho mỗi cuộc phỏng vấn ~15 phút / 12 câu hỏi cố định), và **không** dùng nhãn bạc (PHQ-8 / xác nhận lâm sàng). Giá trị của nó với Pebble là *hình dạng pipeline, các ablation thành phần, và công thức học chuyển giao* — không bao giờ là con số tuyệt đối như một mục tiêu trên dữ liệu trẻ em.

## Nghiên cứu sâu — đọc toàn bộ PDF (2026-06-16)

### Ghi chú truy cập nguồn

Đọc từ PDF cục bộ `docs/papers/pdfs/40-zhang-wav2vec2-depression.pdf` qua `pdftotext` (toàn bộ phần thân; tóm tắt, tất cả các phần phương pháp, Bảng 1–4 chép nguyên văn; các ablation chỉ có trong hình — các delta F1 của pooling, đường cong độ dài đoạn, ROC/AUC, phân cụm — đọc từ phần văn bản mô tả). Công cụ Read không thể render PDF.

Xác minh nguồn gốc (phiên bản Scientific Reports đã xuất bản là có thẩm quyền; không có preprint, nên không có vấn đề preprint-delta):

- **Nơi công bố / danh tính / con số tiêu đề** — WebSearch (`Zhang "Improving speech depression detection using transfer learning with wav2vec 2.0" Scientific Reports 2024 DAIC-WOZ CMDC F1 79%`) xác định bài báo là *Sci Rep* 14:9543 (2024), DOI 10.1038/s41598-024-60278-1, và xác nhận **F1 79% trên DAIC-WOZ và 90.53% trên CMDC**. URL: https://www.nature.com/articles/s41598-024-60278-1 và https://pmc.ncbi.nlm.nih.gov/articles/PMC11045867/ . Trạng thái: ✔ đã xác nhận.
- **Con số Bảng 1–4** (DAIC P/R/F1 84.49 / 76.99 / 79.00; CMDC P/R/F1 94.83 / 88.33 / 90.53; toàn bộ lưới fine-tuning Bảng 3; Bảng 4 self-attention; pooling +4.69% / +2.26% F1; tất cả siêu tham số; phân chia tập dữ liệu) — WebFetch trên toàn văn PMC https://pmc.ncbi.nlm.nih.gov/articles/PMC11045867/ trả về tất cả các con số này giống hệt PDF cục bộ. Trạng thái: ✔ đã xác nhận (hai bản độc lập, PDF + PMC, khớp chính xác).
- **Tập dữ liệu** — DAIC-WOZ tại https://dcapswoz.ict.usc.edu/ và CMDC tại https://ieee-dataport.org/open-access/chinese-multimodal-depression-corpus (cả hai được nêu trong phần Data Availability của bài). Trạng thái: ✔ đã xác nhận (liên kết sống trong bài).

### Bài báo thực sự làm gì

**Khung bài toán (Materials and methods → Problem definition).** Phân loại nhị phân: với người tham gia *i* có giọng nói thô `x_i`, dự đoán `y_i ∈ {0,1}` (0 = bình thường, 1 = trầm cảm). Mỗi người tham gia cũng mang một điểm PHQ-8, nhưng nhiệm vụ chính là nhãn trầm cảm *nhị phân*. Pipeline có bốn bước: tiền xử lý âm thanh → trích đặc trưng cấp khung → trích đặc trưng cấp đoạn → phân loại trầm cảm.

**Bước 1 — Tiền xử lý giọng nói.** Chỉ giữ giọng nói của **người tham gia**; loại bỏ giọng người phỏng vấn, khoảng lặng, và tiếng ồn nền. Âm thanh giữ lại được cắt thành **các đoạn 7 giây không chồng lấn, độ dài cố định** giữ nguyên thứ tự thời gian, và **lấy mẫu lên 16 kHz** (yêu cầu đầu vào của wav2vec 2.0). Độ dài 7 giây chọn bằng liệt kê (ablation, Hình 8: hiệu năng tăng theo độ dài đoạn tới ~7 s rồi bão hòa ở 7–8 s; đoạn ngắn hơn phá vỡ tính liên tục cảm xúc, đoạn dài hơn cắt giảm số mẫu). Ký hiệu: `x_i = {s_{i,1}, …, s_{i,M}}`, M đoạn cho mỗi đối tượng; mỗi đoạn `s_{i,j} = {h_1, …, h_N}`, N khung chiều d.

**Bước 2 — Đặc trưng cấp khung qua wav2vec 2.0 đã fine-tune.** wav2vec 2.0 (Baevski và cộng sự 2020, tài liệu 35) ánh xạ âm thanh thô qua một bộ mã hóa đặc trưng tích chập nhiều lớp (độ dài khung 25 ms, độ dịch khung 20 ms → latent `{Z_1…Z_T}`) rồi một bộ mã hóa ngữ cảnh Transformer (base = 12 lớp, large = 24 lớp) → `{h_1…h_N}`. **Các lớp tích chập dưới được đóng băng; các lớp Transformer được fine-tune.** Đầu ra của *tất cả* các lớp Transformer được **cộng lại** để cho ra chuỗi đặc trưng wav2vec 2.0 của đoạn. Bài so sánh base vs large, fine-tune lớp cuối vs toàn bộ lớp, và một biến thể wav2vec 2.0 fine-tune trên **IEMOCAP** (chuyển giao cảm xúc, lấy cảm hứng từ Wu và cộng sự tài liệu 36, chuyển giao "cảm xúc → trầm cảm").

**Bước 3 — 1D-CNN + attention pooling (bộ mã hóa đoạn, Hình 2 phải).** Ba khối tích chập, mỗi khối = lớp tích chập 1-D + ReLU + dropout. Số bộ lọc `C = [80, 80, 80]`. Đầu ra tích chập `C_{i,j} = conv1D(s_{i,j}, K) ∈ R^{T×d}` (PT 1). Một **lớp pooling** sau đó nén các khung → một vector đoạn `V_{i,j}`. Ba phương pháp pooling được so sánh: average pooling (PT 2), max pooling (PT 3), và **attention pooling cộng tính** (PT 4): `V_{i,j} = Softmax(w_c · C_{i,j}^T) · C_{i,j}`, với `w_c` là trọng số học được dùng để gán trọng số cho khung theo độ quan trọng. Attention pooling thắng (xem ablation).

**Bước 4 — Đầu thời gian LSTM + self-attention (Hình 3).** Các vector từng đoạn `{v_{i,1}…v_{i,j}}` đưa vào một **LSTM** (PT 5) để bắt tương quan thời gian ngắn- và dài-hạn xuyên suốt toàn bộ phỏng vấn. Một lớp **self-attention** (PT 6, dot-product có tỉ lệ `Softmax(QK^T/√d_K)V`) sau đó tái-gán trọng số các đoạn sao cho những đoạn liên quan trầm cảm chiếm ưu thế. Đầu ra self-attention được cộng tổng đưa vào một lớp tuyến tính → nhị phân `y_i`. Động cơ: "không phải mọi bệnh nhân trầm cảm đều bộc lộ đặc điểm trầm cảm rõ ràng trong giọng nói", nên mô hình phải *chọn* các đoạn thông tin thay vì lấy trung bình.

**Tập dữ liệu (Result → Datasets description).**
- **DAIC-WOZ** (tài liệu 39): 189 cuộc phỏng vấn Wizard-of-Oz lâm sàng về căng thẳng (lo âu/trầm cảm/PTSD), tổng ~50 giờ. Phân chia: **107 train / 35 development / 47 test**. Phỏng vấn trung bình ~15 phút, 16 kHz. Theo công trình trước, thí nghiệm dùng tập **train + development** (tập dev là test trên thực tế để so sánh được). Đa phương thức (văn bản/hình ảnh/giọng nói); chỉ dùng giọng nói. Nhãn PHQ-8 + nhị phân.
- **CMDC** (tài liệu 40): Chinese Multimodal Depression Corpus, phỏng vấn bán cấu trúc với **12 câu hỏi cố định**. **78 mẫu (26 trầm cảm nặng, 52 khỏe mạnh).** Nhỏ hơn DAIC-WOZ — dùng để kiểm chứng tuyên bố ít tài nguyên trên ngôn ngữ thứ hai.

**Thiết lập thí nghiệm.** Linux, một **NVIDIA V100**, PyTorch. LR fine-tuning **1e-5**; LR nhiệm vụ downstream **0.006**; **Adam**, weight decay **0.001**; batch size **32**; **200 epoch** với dừng sớm (patience 10 trên validation). Một đặc trưng baseline để so sánh là **bộ IS09 emotion của OpenSMILE**: 16 LLD (MFCC, ZCR, …) → 32 với đạo hàm bậc nhất → 12 functionals → vector câu **384 chiều**.

**Kết quả — Bảng 1, DAIC-WOZ (so với các phương pháp SDD trước; in đậm = tốt nhất):**

| Phương pháp (năm) | Đặc trưng | Precision | Recall | F1 |
|---|---|---|---|---|
| ResNet (Chlasta 2019) | spectrogram | 57.14% | 57.14% | 57.14% |
| LSTM (Rejaibi 2022) | MFCC | 73.50% | 64.50% | 64.00% |
| EmoAudioNet (Othmani 2021) | MFCC+Spectrogram | — | — | 66.00% |
| DepAudioNet (Ravi 2022) | wav2vec 2.0 | 66.70% | 66.70% | 69.20% |
| MSCDR (Du 2023) | LPC+MFCC | 71.00% | 83.00% | 74.60% |
| CNN+Channel-wise Attention (Zhou 2022) | MFCC+Spectrogram+eGeMAPS | 79.60% | 68.66% | 77.00% |
| (baseline is09_emotion) | is09_emotion | 84.49%* | 76.99%* | 70.09% |
| **Ours** | **wav2vec 2.0** | **84.49%** | **76.99%** | **79.00%** |

(*Hàng is09 báo F1 70.09%; các cột precision/recall trong bảng trích bị gộp một phần — so sánh quan trọng là F1 wav2vec2 "Ours" **79.00%** vs baseline trước mạnh nhất F1 **77.00%**.) Các delta tiêu đề tác giả nêu: so với Du và cộng sự (1D-CNN+LSTM tương tự nhưng dùng MFCC+LPC), Ours **+17.79% precision, +10.29% recall, +4.4% F1**; so với Othmani và cộng sự **+16.62% F1**; so với Ravi và cộng sự (cũng wav2vec2 + đối kháng) **+9.8% F1**. Ma trận nhầm lẫn (Hình 4): Ours có nhiều true positive hơn và ít false positive hơn Du và cộng sự — "phân biệt tốt hơn" khi nhận biết người không trầm cảm. Tất cả ✔ đã xác nhận.

**Kết quả — Bảng 2, CMDC (tiếng Trung; in đậm = tốt nhất):**

| Phương pháp | Đặc trưng | Precision | Recall | F1 |
|---|---|---|---|---|
| Unsupervised encoder + Transformer (Sun 2022) | MFCC | 92.00% | 83.00% | 87.00% |
| (baseline is09_emotion) | is09_emotion | 82.31% | 79.17% | 80.36% |
| **Ours** | **wav2vec 2.0** | **94.83%** | **88.33%** | **90.53%** |

so với baseline prosodic IS09, Ours **+12.51% precision, +10.16% recall, +10.17% F1**. ROC/AUC (Hình 5): đặc trưng wav2vec đã fine-tune nằm về phía trên-trái hơn; trên CMDC, AUC đạt **1.0** (xếp hạng hoàn hảo, n nhỏ). Tất cả ✔ đã xác nhận.

**Ablation 1 — chiến lược fine-tuning (Bảng 3, trên DAIC-WOZ):**

| Thiết lập | Mô hình tiền huấn luyện | Precision | Recall | F1 |
|---|---|---|---|---|
| A. Đóng băng, lớp cuối | wav2vec2-base | 68.00% | 66.30% | 66.86% |
| A. Đóng băng, lớp cuối | wav2vec2-large | 68.30% | 68.30% | 68.30% |
| A. Đóng băng, lớp cuối | wav2vec2-IEMOCAP | 83.82% | 54.17% | 48.04% |
| B. Fine-tune, lớp cuối | wav2vec2-base | 64.32% | 62.14% | 70.86% |
| B. Fine-tune, lớp cuối | wav2vec2-large | 75.00% | 72.64% | 73.48% |
| B. Fine-tune, **toàn bộ lớp** | wav2vec2-base | 88.33% | 70.83% | 72.81% |
| B. Fine-tune, **toàn bộ lớp** | wav2vec2-large | **84.49%** | **76.99%** | **79.00%** |

Ba phát hiện: (1) **fine-tune > đóng băng** ở mọi cặp tương ứng; (2) **large > base**; (3) **fine-tune toàn bộ lớp > chỉ lớp cuối**. Biến thể fine-tune cảm xúc IEMOCAP (đóng băng) cho **precision cao (83.82%) nhưng recall sụp đổ (54.17%) → F1 48.04%** — chỉ chuyển giao cảm xúc *không đủ*; bắt buộc phải fine-tune trầm cảm trong miền. Tất cả ✔ đã xác nhận.

**Ablation 2 — pooling (Hình 7, mô tả):** attention pooling vượt **max pooling +4.69% F1** và **average pooling +2.26% F1**. ✔ đã xác nhận.

**Ablation 3 — self-attention (Bảng 4, DAIC-WOZ):**

| | Precision | Recall | F1 |
|---|---|---|---|
| Không self-attention (bước cuối LSTM → FC) | 82.14% | 72.83% | 74.72% |
| **Có self-attention** | **84.49%** | **76.99%** | **79.00%** |

Self-attention thêm **+4.28% F1** (74.72 → 79.00). ✔ đã xác nhận.

**Ablation 4 — độ dài đoạn (Hình 8):** F1 tăng từ 4 s tới 7 s, bão hòa 7–8 s, rồi yếu đi (số mẫu giảm). Chọn 7 s. ✔ đã xác nhận.

**Phân cụm (Hình 6, mô tả):** phân cụm kiểu t-SNE của is09_emotion (a, mờ), raw-wav2vec2 (b, một phần), wav2vec2-đã-fine-tune (c, hai nhóm chặt, tách biệt rõ) — bằng chứng định tính rằng fine-tuning là thứ làm trầm cảm vs khỏe mạnh tách được.

**Những gì KHÔNG có trong bài:** không có hiệu chỉnh (calibration) / ECE / đường cong độ tin cậy; không có kết quả hồi quy theo mức PHQ (PHQ-8 được nhắc nhưng chỉ đầu nhị phân được đánh giá); không có dữ liệu trẻ em hay vị thành niên; không có chấm điểm turn-level; không có số độ trễ suy luận / kích thước mô hình (thừa nhận là việc tương lai "triển khai thời gian thực"); không có kiểm định ý nghĩa thống kê trên các delta F1; không có khẳng định tách-biệt người nói giữa train/test ngoài phân chia DAIC chuẩn; không dùng ensemble (mô hình đơn).

### Các phần trực tiếp hữu ích cho Pebble

Mỗi phần gắn với Decision ID nó dịch chuyển và một ghi chú rủi ro chuyển giao.

1. **Toàn bộ pipeline trầm cảm-qua-giọng đầu-cuối như một mẫu cho đầu `severity`/căng thẳng giọng nói của Pebble (D-D, D-A).** Âm thanh thô → VAD/chỉ giọng người tham gia → bộ mã hóa SSL đã fine-tune (tổng-tất-cả-lớp-Transformer) → 1D-CNN + attention pooling mỗi đoạn → LSTM + self-attention trên các đoạn → đầu. Đây là bản thiết kế dễ sao chép nhất trong bộ voice để đi từ đoạn nói của trẻ tới một điểm căng thẳng. *Rủi ro chuyển giao: trung bình.* Bản thiết kế hợp lý và đúng phương thức, nhưng mọi khối đều tinh chỉnh trên phỏng vấn lâm sàng 15-phút của người lớn; clip của Pebble ngắn, tự phát, theo register trẻ em. *Hình dạng* chuyển giao được; *độ-dài-đoạn / độ-sâu-LSTM* phải tinh chỉnh lại cho clip ngắn (một clip trẻ em 30 giây cho ra ~4 đoạn, không phải hàng chục như phỏng vấn, nên đầu thời gian LSTM+self-attention có thể là quá mức — xem Hạn chế).

2. **Fine-tune toàn bộ lớp của backbone SSL vượt đóng băng và chỉ-lớp-cuối (D-A, D-E).** Bảng 3: FT toàn bộ lớp wav2vec2-large = 79.00% F1 vs đóng-băng-lớp-cuối 68.30% vs FT-lớp-cuối 73.48%. Mức +5.5 F1 từ lớp-cuối→toàn-bộ-lớp FT là phiên bản âm thanh của câu hỏi staged-fine-tuning văn bản của Pebble (gradual unfreeze / discriminative LR). *Rủi ro chuyển giao: trung bình-cao.* Trên dữ liệu giọng trẻ em **nhỏ** của Pebble, fine-tune toàn bộ một mô hình large 24 lớp có nguy cơ overfit — chế độ ngược với corpus phỏng vấn 50-giờ này. Pebble nên coi "FT toàn bộ lớp giúp ích" là một giả thuyết cần kiểm lại với gradual-unfreeze + discriminative-LR (D-E) như một trung gian có điều tiết, không áp dụng FT toàn bộ một cách mù quáng.

3. **Chuyển giao cảm xúc (fine-tune IEMOCAP) là cần-nhưng-không-đủ — nó phá hủy recall (D-D).** Biến thể wav2vec2-IEMOCAP đóng băng cho precision 83.82% nhưng recall chỉ 54.17% (F1 48.04%). Đây là bằng chứng trực tiếp rằng **chuyển giao một mô hình *cảm xúc* vào nhiệm vụ *mức-độ lâm sàng* mà không fine-tune trong miền sẽ làm sụp đổ recall** — đúng kế hoạch của Pebble chuyển cường độ cảm xúc SemEval/WASSA vào đầu `severity`. *Rủi ro chuyển giao: thấp (cảnh báo chuyển giao sạch sẽ).* Nó nói rằng: chuyển giao cảm xúc→mức-độ phải được *theo sau bởi* fine-tune mức-độ trong miền, và recall phải được theo dõi, không chỉ precision. Điều này trực tiếp thúc đẩy kỷ luật sàn-recall của Pebble trên đường severity/safety.

4. **Attention pooling > mean/max khi nén khung thành vector đoạn (D-A, D-B).** +4.69 F1 so với max, +2.26 so với mean. Bộ tổng hợp khung→đoạn là một đòn bẩy thiết kế thực, đo được. *Rủi ro chuyển giao: thấp.* Attentive pooling không phụ thuộc nhiệm vụ và nhất quán với bài 27 (ECAPA-TDNN ≥ mean pooling); đầu giọng nói của Pebble nên mặc định attentive pooling, với mean là baseline rẻ. (Lưu ý: trên clip trẻ em rất ngắn có ít khung để attention, làm hẹp khoảng cách lợi ích.)

5. **Chọn-đoạn bằng self-attention thêm +4.28 F1 vì "không phải mọi bệnh nhân trầm cảm bộc lộ ở mọi đoạn" (D-A).** Đầu thời gian học để tăng trọng số vài đoạn thông tin. *Rủi ro chuyển giao: trung bình.* Tiền đề — căng thẳng *thưa* xuyên suốt một phỏng vấn dài — cũng đúng cho Pebble (căng thẳng của trẻ có thể chỉ xuất hiện ở một câu trong clip), nhưng clip của Pebble ngắn nên độ thưa trong-clip nhỏ hơn; lợi ích lớn hơn sẽ là chọn *xuyên-lượt (across-turn)* giữa hội thoại, điều bài này không kiểm thử.

6. **Siêu tham số cụ thể, đặc tả đầy đủ cho một fine-tune SSL (D-E).** LR 1e-5 (backbone) vs 0.006 (đầu) — tỉ lệ **discriminative-LR ~600×** giữa backbone tiền huấn luyện và đầu từ-đầu; Adam, weight decay 0.001; batch 32; dừng sớm patience 10. *Rủi ro chuyển giao: thấp.* LR hai-tốc-độ (rất nhỏ trên backbone, lớn trên đầu) chính là nguyên tắc discriminative-LR Pebble muốn cho D-E, và đây là giá trị khởi điểm hợp lý cho bất kỳ fine-tune bộ mã hóa SSL nào; LR tuyệt đối có thể cần thu nhỏ trên dữ liệu trẻ em nhỏ.

7. **Kiểm chứng ít-tài-nguyên hai-corpus, hai-ngôn-ngữ như một mẫu đánh giá (D-D, D-H).** Báo cáo cùng kiến trúc trên DAIC-WOZ (tiếng Anh, n≈142 dùng) và CMDC (tiếng Trung, n=78) cho thấy tuyên bố học-chuyển-giao không phụ thuộc corpus. *Rủi ro chuyển giao: thấp (phương pháp luận).* Pebble cũng nên kiểm chứng bất kỳ đầu giọng nói nào trên ≥2 corpus trước khi tuyên bố tổng quát hóa, vì kết quả giọng nói đơn-corpus nổi tiếng là overfit điều kiện người nói/ghi âm.

### Mỗi phần giúp Pebble thành công như thế nào

- **Bản thiết kế đầu căng thẳng giọng nói (D-D, D-A).** Dựng `experiments/voice_severity_head/` phản chiếu pipeline này: phân đoạn chỉ-giọng-người → bộ mã hóa SSL đã fine-tune → vector đoạn attention-pooled → đầu thời gian → đầu ra severity. Tái dùng đúng thứ tự khối; tham số hóa độ dài đoạn (mặc định 7 s nhưng quét 3–7 s cho clip trẻ em ngắn) và làm đầu thời gian có thể thay (LSTM+self-attention cho clip dài, attention-trên-đoạn đơn giản hoặc thậm chí một vector pooled cho clip ngắn). Đây là artifact biến "phương thức giọng nói" của Pebble từ khẩu hiệu thành một spike chạy được.
- **Chính sách fine-tune backbone (D-A, D-E).** Áp dụng **LR discriminative hai-tốc-độ** (backbone 1e-5, đầu ~6e-3) làm mặc định cho cả bộ mã hóa giọng nói *và* fine-tune văn bản NeoBERT. Nhưng trên dữ liệu trẻ em nhỏ, đặt "FT toàn bộ lớp" sau một lịch trình gradual-unfreeze (D-E): bắt đầu đóng băng, mở lớp trên trước, theo dõi recall validation — khoảng cách đóng-băng-vs-FT của Bảng 3 là bằng chứng rằng *một số* thích nghi backbone là cần, trong khi sự khan hiếm dữ liệu của Pebble phản đối FT *toàn bộ* mà bài này dùng.
- **Chuyển giao cảm xúc→mức-độ với lá chắn recall (D-D).** Pebble dự định chuyển cường độ cảm xúc WASSA/SemEval → hồi quy `severity`. Biến thể cảm xúc-IEMOCAP của bài (precision 83.82, recall **54.17**) là tài liệu cảnh báo: gắn một giai đoạn fine-tune severity trong miền *sau* khởi tạo chuyển-giao-cảm-xúc, và đặt sàn recall trên đầu ra severity/safety. Artifact cụ thể: một hàng ablation báo recall *trước và sau* giai đoạn trong miền, không chỉ F1.
- **Pooling + đầu thời gian như núm cấu hình (D-A, D-B).** Hiện thực pooling khung→đoạn là `{mean, max, attention}` và mặc định attention (theo bài này + bài 27). Hiện thực đầu đoạn→câu là `{mean, lstm_selfattn}` và chọn theo độ dài clip. Báo cáo delta có/không self-attention như một hàng ablation của Pebble, đúng như Bảng 4.
- **Kỷ luật đánh giá hai-corpus (D-D, D-H).** Làm bảng điểm đầu giọng nói trải ≥2 tập dữ liệu/điều kiện trước khi tuyên bố triển khai; báo precision VÀ recall VÀ F1 (không chỉ accuracy) do mất cân bằng lớp, phản chiếu Bảng 1–2.

### Lăng kính sức khỏe tâm thần trẻ em

- **Lệch dân số/register là rủi ro chủ đạo.** DAIC-WOZ và CMDC là **người lớn trong phỏng vấn lâm sàng có cấu trúc** (phiên DAIC 15 phút; 12 câu hỏi CMDC cố định), ghi trong điều kiện kiểm soát, gán nhãn bằng **PHQ-8 / xác nhận lâm sàng** — không phải trẻ em, không tự phát, không nhãn bạc. Các F1 79% / 90.53% **không phải mục tiêu Pebble có thể kỳ vọng trên tin nhắn thoại của trẻ.** Tần số cơ bản, formant, tốc độ nói của trẻ, và *cách trẻ bộc lộ căng thẳng* (gián tiếp, chơi đùa, phát ngôn ngắn) đều nằm ngoài phân phối của một wav2vec2 tiền huấn luyện trên tiếng Anh người lớn (họ LibriSpeech) — và bài không đưa ra bằng chứng trẻ em nào cả. Dùng nó để *xếp hạng pipeline*, không bao giờ làm thước đo.
- **Trầm cảm lâm sàng nhị phân ≠ tín hiệu căng thẳng turn-level của Pebble.** Đây là một nhãn cho mỗi phỏng vấn dài ("người này có trầm cảm không?"). Pebble cần một tín hiệu căng thẳng/severity **giữa hội thoại, mức turn/clip**. Đầu LSTM+self-attention ở đây chọn các đoạn thông tin *trong một phiên chẩn đoán*; nhu cầu tương tự của Pebble là chọn các *khoảnh khắc thông tin trong một clip ngắn* và xuyên các lượt — một thang thời gian khác. Tiền đề kiến trúc ("căng thẳng thưa thớt trên một bản ghi dài") đảo ngược một phần cho clip trẻ em ngắn.
- **Sụp đổ recall của chuyển-giao-cảm-xúc là cảnh báo liên quan an toàn-trẻ-em.** Recall chuyển-giao IEMOCAP 54.17% nghĩa là *bỏ sót gần một nửa ca trầm cảm* khi chuyển một mô hình cảm xúc mà không fine-tune trong miền. Với tín hiệu an toàn hướng-trẻ-em, chế độ lỗi đó không chấp nhận được — nó trực tiếp ủng hộ giữ quyết định an toàn hướng-trẻ v1 của Pebble **dẫn-dắt-bởi-văn-bản và heuristic** (theo `docs/decisions.md`: không có đầu an toàn học được trong v1) và coi mọi đầu severity giọng nói là thử nghiệm cho tới khi dữ liệu trẻ em trong miền kiểm chứng được recall của nó.
- **Quyền riêng tư/đạo đức của giọng trẻ em nghiêm ngặt hơn văn bản.** Âm thanh thô của trẻ định danh hơn nhiều so với văn bản (vân giọng, người nói nền, dấu hiệu vị trí), và embedding SSL *không* ẩn danh. Một đường giọng nói trẻ em cần xử lý trên-thiết-bị/kiểm-soát-chặt, xóa-mặc-định âm thanh thô sau khi embed, và sự đồng ý của người giám hộ — chế độ nghiêm hơn pipeline văn bản của Pebble. Corpus của bài là dữ liệu lâm sàng đã đồng ý; Pebble không thể thừa hưởng cơ sở đồng ý đó cho một ứng dụng đồng hành.
- **Học chuyển giao ít-tài-nguyên là *chiến lược* đúng cho Pebble.** Luận điểm cốt lõi của bài — khi dữ liệu nhãn trong miền khan hiếm, hãy fine-tune một mô hình SSL lớn thay vì huấn luyện từ đầu hay tạo đặc trưng thủ công — chính là tình huống của Pebble cho giọng trẻ em (gần như không có âm thanh căng-thẳng-trẻ-em có nhãn). Công thức chuyển giao được dù con số thì không.
- **Giảm thiểu.** (1) Đo lại toàn bộ pipeline trên một corpus giọng trẻ em trước khi tin bất kỳ xếp hạng nào. (2) Ưu tiên gradual-unfreeze / FT một phần hơn FT toàn bộ do khan hiếm dữ liệu trẻ em. (3) Luôn ghép chuyển-giao cảm-xúc→mức-độ với fine-tune trong miền và một sàn recall. (4) Giữ giọng nói là tín hiệu *bổ sung* cho quyết định an toàn dẫn-dắt-bởi-văn-bản trong v1, không phải thay thế. (5) Coi embedding giọng nói là PII.

### Hạn chế & câu hỏi mở cho Pebble

- **Mâu thuẫn/khoảng trống so với kế hoạch turn-level, clip-ngắn của Pebble.** Pipeline này xây cho **bản ghi đơn-nhãn dài** (phỏng vấn 15 phút; nhiều đoạn 7-s → đầu thời gian LSTM+self-attention). Pebble chấm các clip trẻ em **ngắn, giữa hội thoại, mức turn**. Một clip trẻ em 20–30 s chỉ cho ~3–5 đoạn — bộ máy "chọn-đoạn-thông-tin" LSTM+self-attention gần như không có gì để chọn, nên đóng góp kiến trúc tiêu đề của bài (chọn-đoạn theo thời gian, +4.28 F1) có thể **không chuyển giao** sang chế độ của Pebble. Đây là sự lệch kiến trúc thực, không chỉ là khoảng cách miền: Pebble có thể được phục vụ tốt hơn bằng một *embedding clip attention-pooled đơn* thay vì chồng LSTM của bài này.
- **Mâu thuẫn so với bài 27 (Morais SSL-SER) về độ sâu fine-tune backbone.** Bài 27 fine-tune toàn bộ backbone *và* dựa vào **trung bình hóa trọng số checkpoint** (+~2.3% WACC) như lợi ích miễn phí lớn nhất; bài này dựa vào **fine-tune toàn bộ lớp + một chồng downstream sâu hơn** và không bao giờ dùng trung bình checkpoint. Hai công thức "thực hành tốt nhất" cho một đầu cảm xúc/affect SSL do đó phân kỳ — Pebble nên thử trung-bình-checkpoint (rẻ, từ bài 27) *trên nền* pipeline của bài này, vì không bài nào kết hợp chúng. Ngoài ra, bài 27 thấy **wav2vec2 ≥ HuBERT và fusion tốt nhất**; bài này dùng **chỉ wav2vec2** và không bao giờ benchmark HuBERT/WavLM — nên lựa chọn backbone giọng nói của Pebble (D-A) *chưa được giải quyết bởi riêng bài này* và phải bao gồm cột WavLM.
- **Tập test nhỏ → con số mong manh.** DAIC dùng **tập dev 35 phỏng vấn** làm test trên thực tế; CMDC có **78 mẫu tổng** và báo **AUC = 1.0** — gần như chắc chắn là hiện vật mẫu-nhỏ, không phải bằng chứng cho bộ phân loại hoàn hảo. Không có kiểm định ý nghĩa trên bất kỳ delta F1 nào. Pebble nên coi con số tuyệt đối là minh họa và *thứ tự* ablation tương đối là tín hiệu chuyển giao được.
- **Không có hiệu chỉnh ở đâu cả.** Như hầu hết bộ Pebble, chỉ accuracy/F1 — nhưng Decision Engine của Pebble tiêu thụ *xác suất*. Một đầu severity giọng nói phải thêm đánh giá hiệu chỉnh mà bài này bỏ qua.
- **Tách-biệt người nói không được đảm bảo rõ ngoài phân chia DAIC chuẩn.** Mô hình giọng nói rò rỉ qua danh tính người nói; nếu Pebble sao chép pipeline thì phải áp **fold tách-biệt-người-nói** (theo kỷ luật bài 27) để tránh con số giọng-trẻ-em bị thổi phồng.
- **Câu hỏi mở cho Pebble.** Có *bất kỳ* corpus căng-thẳng/trầm-cảm giọng trẻ em có giấy phép nào để neo pipeline này không? Không có thì đường giọng nói vẫn là một spike nghiên cứu và quyết định an toàn hướng-trẻ v1 vẫn dẫn-dắt-bởi-văn-bản và heuristic (nhất quán với `docs/decisions.md`). Đáng xác định phạm vi một lát hiệu chỉnh giọng trẻ em nội bộ đã đồng ý — phiên bản âm thanh của lát hiệu chỉnh văn bản register-trẻ-em mà Pebble dự định.
