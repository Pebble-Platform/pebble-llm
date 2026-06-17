# Paper 27 — Nhận dạng Cảm xúc từ Giọng nói sử dụng Đặc trưng Tự giám sát (Self-Supervised Features)

## 1. Thông tin thư mục

**Tiêu đề:** Speech Emotion Recognition using Self-Supervised Features (Nhận dạng cảm xúc từ giọng nói sử dụng đặc trưng tự giám sát)

**Tác giả:** Edmilson Morais (Edmilson da Silva Morais), Ron Hoory, Weizhong Zhu, Itai Gat, Matheus Damasceno, Hagai Aronowitz — đều thuộc IBM Research AI.

**Năm / hội nghị:** ICASSP 2022 (IEEE International Conference on Acoustics, Speech and Signal Processing), trang 6922–6926. Bản tiền in arXiv:2202.03896.

**Từ khóa chỉ mục (nguyên văn):** "Speech emotion recognition, self-supervised features, end-to-end systems."

**Tóm tắt một dòng:** Một hệ thống SER mô-đun Upstream (bộ mã hóa âm thanh tự giám sát) + Downstream (pooling + bộ phân loại tuyến tính) mà, nhờ fine-tuning cẩn thận, lấy trung bình checkpoint (checkpoint averaging) và bộ tổng hợp ECAPA-TDNN, đạt SOTA chỉ-dùng-giọng-nói trên IEMOCAP (77.76% UA) — sánh ngang với một baseline đa phương thức audio+text mạnh (78.30% UA).

## 2. Vì sao bài này nằm trong tập Pebble

Luận điểm của Pebble có một **phương thức tin-nhắn-giọng-nói (voice-message)**: trẻ em có thể gửi đoạn âm thanh nói ngắn thay vì gõ văn bản. Với hướng đó Pebble cần một **bộ mã hóa cảm xúc âm thanh (acoustic emotion encoder)**, và quyết định thiết kế đầu tiên là *chọn backbone giọng nói tự giám sát nào* (wav2vec 2.0 vs HuBERT vs WavLM) và *gắn head downstream nào* lên trên. Bài này là một ma trận baseline sạch, có kiểm soát đúng cho lựa chọn đó trên giọng nói tiếng Anh: nó tách bạch đóng góp của (a) backbone SSL, (b) fine-tuning backbone vs đóng băng (freeze), (c) pooling/aggregator frame→utterance, (d) checkpoint averaging, và (e) fusion backbone — tất cả trên benchmark chuẩn IEMOCAP với split SUPERB chuẩn. Đây là phiên bản phía-âm-thanh của cuộc so kè text-encoder mà Pebble chạy cho NeoBERT/ModernBERT/MentalBERT (D-A).

Bài này **không** nói về giọng nói trẻ em, **không** về giọng nói sức khỏe tâm thần, và **không** về chấm điểm theo lượt-thoại giữa-hội-thoại — nó là tiếng Anh người lớn diễn xuất/hội thoại đôi. Giá trị của nó với Pebble là *phương pháp và thứ hạng tương đối của các lựa chọn thiết kế*, không phải các con số IEMOCAP tuyệt đối.

## Deep research — đọc toàn văn PDF (2026-06-16)

### Ghi chú về cách truy cập nguồn

Đọc từ PDF cục bộ `docs/papers/pdfs/27-morais-ssl-ser.pdf` qua `pdftotext` (toàn bộ thân bài, tất cả các mục, Bảng 1 và Bảng 2 được chép nguyên văn). Công cụ Read không render được PDF, nên việc trích xuất văn bản dùng `pdftotext "27-morais-ssl-ser.pdf" -`.

Kiểm chứng xuất xứ (provenance):
- **Hội nghị / danh tính** — WebSearch (`Morais Hoory "Speech Emotion Recognition using Self-Supervised Features" ICASSP 2022 IEMOCAP wav2vec HuBERT 77.76`) xác định bài thuộc ICASSP 2022, trang 6922–6926, arXiv:2202.03896, tác giả IBM Research AI. URL: https://arxiv.org/abs/2202.03896 và https://www.semanticscholar.org/paper/3e8ac2a46b83498ddd171c179ad97763271908c6 . Trạng thái: ✔ đã đối chứng.
- **Tuyên bố trong abstract** (chỉ-giọng-nói sánh ngang SOTA đa phương thức speech+text) — WebFetch trên https://arxiv.org/abs/2202.03896 xác nhận tuyên bố trung tâm của abstract và cấu trúc ICASSP 2022 / 5-trang / 2-bảng. Trạng thái: ✔ đã đối chứng.
- **Chi tiết số liệu** (Bảng 1 WACC/UACC theo từng thí nghiệm; Bảng 2 so sánh SOTA) — các số này chỉ có trong thân PDF. PDF cục bộ chính là phiên bản gốc arXiv; abstract và hội nghị đã được đối chứng và nhất quán, nên các số trong bảng lấy từ văn bản trích xuất PDF và gắn nhãn ≈ (nguồn-đơn: có trong PDF arXiv có thẩm quyền, không tái-suy-ra độc lập từ bản hội nghị thứ hai). Không tìm thấy chênh lệch tiền-in-vs-xuất-bản.
- **Đối chiếu chéo cho khoảng trống WavLM** — WebSearch (`SUPERB benchmark wav2vec2 HuBERT WavLM IEMOCAP emotion recognition`) xác nhận WavLM là mô hình SSL *ra sau/song song* được benchmark ở nơi khác (EmoBox, benchmark SUPERB wav2vec2/HuBERT arXiv:2111.02735) nhưng **không** có trong bài này. URL: https://arxiv.org/abs/2111.02735 , https://arxiv.org/pdf/2406.07162 (EmoBox). Trạng thái: ✔ đã đối chứng rằng WavLM vắng mặt ở đây.

**Đính chính phạm vi quan trọng so với đề bài.** Đề bài yêu cầu "wav2vec2 vs HuBERT vs WavLM" và "những lớp (layer) nào giúp ích." Bài này chỉ so sánh **wav2vec 2.0 và HuBERT** (không có WavLM) và **không** chạy phân tích per-layer / trọng-số-lớp (nó fine-tune toàn bộ backbone và lấy trung bình checkpoint; nó không bao giờ báo cáo lớp transformer nào mang cảm xúc). Cả hai được nêu dưới đây như những khoảng trống tường minh, kèm các nguồn ngoài (benchmark SUPERB, EmoBox) mà Pebble phải tham khảo để hoàn thiện các góc WavLM và chọn-lớp của ma trận.

### Bài báo thực sự làm gì

**Khung bài toán (§2).** SER như một ánh xạ từ giọng nói liên tục `S` sang một cảm xúc phân loại rời rạc `E`, dùng mô hình **Upstream + Downstream** (phiên bản giọng nói của paradigm pretrain-rồi-gắn-head kiểu BERT): Upstream là bộ mã hóa âm thanh độc-lập-tác-vụ, tự giám sát, đóng-băng-hoặc-fine-tuned (front-end / bộ trích đặc trưng); Downstream là back-end phụ-thuộc-tác-vụ tổng hợp đặc trưng mức-frame thành embedding mức-utterance rồi phân loại nó.

**Các mô hình Upstream được so sánh (§2):** bản phát hành mới nhất của **Wav2Vec 2.0** (bản "Robust wav2vec 2.0", ref [14], arXiv:2104.01027) và **HuBERT** (Hidden-Unit BERT, ref [17], arXiv:2106.07447). Một **filter-bank (Fbank)** chuẩn và một **BERT** đã fine-tune (văn bản) làm baseline (§3.2). **Không có WavLM, không data2vec, không Whisper.**

**Các mô hình Downstream (§2):** hai biến thể —
1. **Mean Average Pooling** aggregator → Bộ phân loại tuyến tính (LC).
2. **ECAPA-TDNN** aggregator [20] → Bộ phân loại tuyến tính (LC). ECAPA-TDNN mượn từ xác minh người nói: channel-attention nhấn mạnh, lan truyền & tổng hợp đặc trưng đa-lớp, với attentive statistics pooling.

**Tập dữ liệu (§2.1): IEMOCAP** [21], ~12 giờ hội thoại đôi đa phương thức, 5 phiên, 10 người nói. Theo công trình trước, chỉ dùng các utterance `angry`, `happy`, `excited`, `sad`, `neutral`, và **`excited` được gộp vào `happy`** → bài toán 4-lớp, **5,531 utterance** (happy 1,636, angry 1,103, sad 1,084, neutral 1,708). Đánh giá là **leave-one-session-out 5-fold CV**: mỗi fold dùng 2 người nói để test, 8 người nói còn lại chia 80/20 train/val. **Split giống hệt SUPERB** [18] (train/val/test mỗi fold).

**Công thức fine-tuning (§2.2):** mỗi mô hình Upstream được fine-tune *cùng lúc* với một head Mean-Pooling + Linear-Classifier đơn giản trên nhãn phân loại IEMOCAP, riêng cho từng fold trong 5 fold → 5 mô hình Upstream đã fine-tune (mỗi fold một).

**Lấy trung bình checkpoint (§2.3):** để giảm phương sai đầu ra, **5 checkpoint fine-tune tốt nhất** (chọn thuần theo accuracy trên tập validation; tập test không bao giờ được quan sát) được **lấy trung bình trọng số** [22] — làm theo từng fold, cho cả wav2vec 2.0 và HuBERT → 10 mô hình Upstream "FT-AVG". Cùng kiểu lấy trung bình áp dụng cho checkpoint của mô hình Downstream.

**Lưới thí nghiệm (§3.1, Hình 3 / Hình 4, Bảng 1):**
- Exp 1–2: W2V2 / HuBERT, Mean pooling, **không** lấy trung bình mô hình nào.
- Exp 3–4: W2V2 / HuBERT, Mean pooling, **cả** Upstream + Downstream đều lấy trung bình.
- Exp 5–6: W2V2 / HuBERT, aggregator **ECAPA-TDNN**, cả hai đều lấy trung bình.
- Exp 7: **early fusion (hợp nhất sớm)** đặc trưng HuBERT + W2V2 (ghép nối trước một ECAPA-TDNN duy nhất).
- Exp 8: **late fusion (hợp nhất muộn)** hai embedding utterance từ hai ECAPA-TDNN (một trên W2V2, một trên HuBERT).
- Exp 9 (baseline): Fbank → ECAPA → LC (không SSL, âm thanh).
- Exp 10 (baseline): BERT (văn bản, trên transcript gốc) → ECAPA → LC.
- Exp 11 (baseline): Fbank & BERT late fusion (âm thanh+văn bản).

**Kết quả — Bảng 1 (WACC = weighted accuracy, UACC = unweighted accuracy; đều %):**

| Set | # | Phương thức | Upstream (FT / AVG) | Downstream (AGG / AVG) | WACC | UACC |
|---|---|---|---|---|---|---|
| 1.A | 1 | S | W2V2 (FT, không AVG) | Mean (không AVG) | 74.09 | 74.56 |
| 1.A | 2 | S | HuBERT (FT, không AVG) | Mean (không AVG) | 72.99 | 73.45 |
| 1.A | 3 | S | W2V2 (FT, AVG) | Mean (AVG) | 76.47 | 76.86 |
| 1.A | 4 | S | HuBERT (FT, AVG) | Mean (AVG) | 75.20 | 75.80 |
| 1.B | 5 | S | W2V2 (FT, AVG) | ECAPA (AVG) | 76.58 | 77.36 |
| 1.B | 6 | S | HuBERT (FT, AVG) | ECAPA (AVG) | 75.56 | 77.04 |
| 1.B | 7 | S | **HuBERT + W2V2 (early fusion, FT, AVG)** | **ECAPA (AVG)** | **77.07** | **77.76** |
| 1.B | 8 | S | HuBERT & W2V2 (late fusion, FT, AVG) | ECAPA (AVG) | 76.78 | 77.52 |
| 2 | 9 | S | Fbank (không FT) | ECAPA (AVG) | 56.52 | 57.60 |
| 2 | 10 | T | BERT (FT, AVG) | ECAPA (AVG) | 69.34 | 70.07 |
| 2 | 11 | S+T | Fbank & BERT (late fusion) | ECAPA (AVG) | 70.56 | 71.46 |

Tất cả số liệu Bảng 1 ≈ (PDF arXiv có thẩm quyền, nguồn-đơn).

**Kết quả — Bảng 2 (so sánh SOTA, UACC %, 5-fold CV IEMOCAP):**

| # | Phương pháp | Phương thức | UACC |
|---|---|---|---|
| 1 | Sajjad et al. [23] | Audio | 72.25 |
| 2 | Wang et al. [24] | Audio | 73.30 |
| 3 | Liu et al. [25] | Audio | 70.78 |
| 4 | Zhao et al. [26] | Audio | 71.70 |
| 5 | Wu et al. [6] | Audio + Text | 78.30 |
| — | **Của chúng tôi (exp. 7)** | **Audio** | **77.76** |

Tất cả số liệu Bảng 2 ≈ (PDF arXiv có thẩm quyền, nguồn-đơn).

**Quan sát thảo luận / ablation (§4.1), chênh lệch nguyên văn:**
1. **Checkpoint averaging** (exp 3,4 vs 1,2): +**2.38%** WACC cho W2V2, +**2.21%** WACC cho HuBERT. (Lấy trung bình cả Upstream và Downstream.)
2. **ECAPA-TDNN vs Mean pooling** (exp 5,6 vs 3,4): ECAPA "nhỉnh hơn một chút" so với mean pooling. (Số học: W2V2 76.58 vs 76.47 WACC; HuBERT 75.56 vs 75.20.)
3. **Early vs late fusion backbone** (exp 7 vs 8): early fusion của HuBERT+W2V2 **vượt** late fusion (77.07 vs 76.78 WACC; 77.76 vs 77.52 UACC).
4. **SSL vs Fbank** (bất kỳ exp 1–8 vs exp 9): SSL vượt filter-bank thủ công "với khoảng cách rất lớn" (tốt nhất 77.07 vs 56.52 WACC ≈ **+20 điểm**).
5. **SSL audio vs BERT fine-tune trên transcript chuẩn** (set 1.B vs exp 10): SSL audio-only tốt nhất vượt text-BERT khoảng "6%" (77.07 vs 69.34 WACC).
6. **SSL audio vs baseline đa phương thức Fbank+BERT** (set 1.B vs exp 11): SSL chỉ-audio vượt baseline audio+text khoảng "5%" (77.07 vs 70.56 WACC).
7. **Điểm nhấn** (Bảng 2): exp 7 (chỉ-audio, 77.76 UACC) ≈ baseline *audio+text* mạnh nhất trong tài liệu (Wu et al. 78.30) và là "kết quả tốt nhất được báo cáo cho SER dùng 5-fold CV trên IEMOCAP cho trường hợp đầu vào chỉ-giọng-nói."

**Những gì KHÔNG có trong bài:** không WavLM/data2vec/Whisper; không phân tích per-layer hay trọng-số-lớp (chỉ fine-tune toàn-backbone); không bảng so sánh kích cỡ base-vs-large; không confusion theo cảm xúc hay F1 theo lớp; không calibration; không bảng learning-rate / freeze-vs-fine-tune (luôn fine-tune); không số liệu độ trễ suy luận hay kích cỡ mô hình.

### Các phần trực tiếp hữu ích cho Pebble

Mỗi phần gắn nhãn Decision ID mà nó dịch chuyển và một ghi chú rủi-ro-chuyển-giao (transfer-risk).

1. **Bake-off backbone như phương pháp chọn audio-encoder (D-A).** Paradigm Upstream+Downstream với downstream cố định và front-end SSL hoán đổi được chính là quy trình Pebble nên chạy để chọn bộ mã hóa tin-nhắn-giọng-nói. Ở đây W2V2 ≥ HuBERT ở mọi ô tương ứng (exp 1>2, 3>4, 5>6), nhưng khoảng cách nhỏ (≤1.3 WACC) và **fusion hai mô hình** thắng — nên câu trả lời "đúng" là một ma trận nhỏ, không phải một lựa chọn đơn. *Rủi ro chuyển giao: trung bình.* Thứ hạng dựa trên tiếng Anh diễn xuất người lớn; trên giọng trẻ em tự phát thứ tự có thể đảo (tài liệu ASR giọng trẻ em thường ưu ái các mô hình pretrain trên âm thanh đa dạng/robust hơn). *Phương pháp* chuyển giao sạch; *người thắng* phải đo lại trên dữ liệu trẻ em.

2. **Head downstream = aggregator + bộ phân loại tuyến tính; ECAPA-TDNN ≥ mean pooling (D-A, D-B).** Pooling frame→utterance là lựa chọn downstream chịu lực. ECAPA-TDNN (attentive statistics pooling với channel attention) nhỉnh hơn mean pooling ở cùng chi phí. Với voice head của Pebble, điều này nói: khởi đầu bằng mean pooling cho baseline rẻ, nhưng dự trù một biến thể attentive-pooling. *Rủi ro chuyển giao: thấp.* Lựa chọn pooling độc lập tác vụ; mức tăng nhỏ của ECAPA hợp lý là robust, dù trên đoạn clip trẻ em rất ngắn attentive pooling có ít thứ để chú ý hơn.

3. **Checkpoint (weight) averaging để giảm phương sai: +2.2–2.4% WACC (D-B, D-E).** Lấy trung bình 5 checkpoint validation tốt nhất của backbone đã fine-tune (và của downstream) là mức tăng "miễn phí" lớn nhất trong bài — lớn hơn cả chênh lệch ECAPA-vs-mean hay early-vs-late-fusion. Đây là một thủ thuật fine-tuning tổng quát (*không* riêng âm thanh) và áp dụng được ngay cho việc fine-tune **bộ mã hóa văn bản NeoBERT** của Pebble, không chỉ voice head. *Rủi ro chuyển giao: thấp.* Lấy trung bình trọng số các checkpoint từ cùng một lần chạy là độc lập kiến trúc và rẻ; nó ổn định fine-tuning nhiễu-nhãn-bạc (silver-label), đúng chế độ của Pebble.

4. **Early > late fusion đa phương thức/đa backbone (D-A, D-H).** Early fusion (ghép nối đặc trưng, một aggregator) thắng late fusion (aggregator riêng, fuse embedding). Nếu Pebble từng fuse audio+text (clip giọng + transcript ASR) hay hai backbone âm thanh, mặc định nên là early/feature-level fusion. *Rủi ro chuyển giao: trung bình.* Chỉ chứng minh trên hai luồng SSL âm thanh; fusion audio+text với một text encoder mạnh có thể khác (tài liệu SER đa phương thức không nhất quán), nên coi đây là mặc-định-để-thử, không phải định luật.

5. **Split SUPERB-giống-hệt 5-fold leave-one-session-out + cặp metric WACC/UACC (D-D, D-H).** Báo cáo cả weighted và unweighted accuracy trên split tách-người-nói là vệ sinh đánh giá đúng cho một benchmark cảm xúc mất cân bằng, và khớp SUPERB khiến kết quả so sánh được. Eval voice-head của Pebble nên áp dụng **fold tách-người-nói** và **báo cáo UA (macro/unweighted) cùng WA**, vì các lớp cảm xúc trẻ em sẽ mất cân bằng như IEMOCAP. *Rủi ro chuyển giao: thấp.* Thuần phương pháp đánh giá; chuyển giao trực tiếp. Kỷ luật tách-người-nói *quan trọng hơn* với Pebble, nơi overfit vào vài giọng trẻ là rủi ro thật.

6. **SSL vượt đặc trưng thủ công ~20 điểm (D-A).** Fbank→ECAPA (exp 9) sụp xuống 56.52 WACC vs 77.07 của SSL. Đây là cơ sở thực nghiệm cho việc dùng một bộ mã hóa SSL pretrained thay vì MFCC/Fbank + mạng huấn-luyện-từ-đầu. *Rủi ro chuyển giao: thấp.* Kết luận "dùng SSL, không dùng đặc trưng thủ công" robust xuyên suốt tài liệu SER và gần như chắc chắn đúng cho giọng trẻ em.

### Mỗi phần giúp Pebble thành công thế nào

- **Chọn encoder voice-head (D-A).** Dựng một bộ harness benchmark `voice_encoder` phản chiếu bài này: downstream cố định (mean pooling → linear), hoán đổi Upstream giữa {wav2vec2-base/large, HuBERT-base/large, **WavLM-base/large — bài này thiếu nhưng SUPERB/EmoBox cho thấy thường dẫn đầu SER**}, fine-tune từng cái, báo cáo WA+UA trên fold tách-người-nói. Dùng chênh lệch tương đối của bài này làm prior: kỳ vọng ECAPA ≈ mean + ~0.2–1%, checkpoint-avg ≈ +2%, early-fusion ≈ +0.3%. Hiện vật cụ thể: `experiments/voice_encoder_bakeoff/` tạo ra CSV dạng Bảng-1.
- **Mức tăng ổn định rẻ, cả hai head (D-B, D-E).** Thêm **lấy trung bình trọng số checkpoint** (trung bình top-k checkpoint validation của một lần chạy) vào vòng lặp fine-tuning chuẩn của Pebble — cho bộ mã hóa văn bản NeoBERT VÀ bất kỳ voice encoder nào. Bài đo +2.2–2.4% trên một tác vụ 4-lớp nhiễu; dưới nhiễu silver-label của Pebble việc giảm phương sai này đúng là công cụ cần, và chỉ tốn lưu trữ checkpoint. Hiện vật cụ thể: một cờ `--avg-top-k` trong trainer + báo cáo chênh lệch có/không như một dòng ablation.
- **Thiết kế pooling head (D-A, D-B).** Hiện thực voice classifier head dạng `aggregator → linear`, với aggregator cắm-rút được giữa `mean` và `ECAPA-TDNN`. Ship mean pooling làm baseline-v; giữ ECAPA làm bản nâng cấp. Khớp với head `emotion` (12-nhãn) và `severity` (hồi quy) của Pebble, mỗi cái nằm trên embedding utterance chung.
- **Mặc định fusion (D-A, D-H).** Khi/nếu Pebble fuse clip giọng của trẻ với transcript ASR (text → NeoBERT) cho emotion/severity, mặc định **ghép nối feature-level sớm trước head chung**, theo exp 7 > exp 8. Hiện vật cụ thể: một config `early_fusion` ghép nối embedding audio đã pool + [CLS] của NeoBERT trước các head.
- **Vệ sinh đánh giá (D-D, D-H).** Áp dụng **CV tách-người-nói** và **báo cáo cặp WA/UA** làm scorecard chuẩn của voice-head; đây cũng là khung đúng cho hướng hồi-quy-severity từ giọng (metric Pearson của D-D nên báo cáo theo từng fold-người-nói để tránh rò rỉ người nói thổi phồng nó).
- **Đừng ship Fbank (D-A).** Khoảng cách 20-điểm SSL-trên-Fbank là dẫn chứng biện minh cho chi phí GPU/tích hợp của một bộ mã hóa SSL trong hướng giọng thay vì một MLP đặc-trưng-phổ nhẹ.

### Lăng kính sức khỏe tâm thần trẻ em

- **Chuyển giao miền là rủi ro trung tâm.** Mọi con số ở đây là **người lớn, diễn xuất/gợi mở, tiếng Anh, hội thoại đôi chất lượng phòng thu** (IEMOCAP). Tin nhắn giọng nói của Pebble là **trẻ em, tự phát, ngoài-thực-tế (mic điện thoại, tiếng ồn nền), có thể ngắn**, và về mặt cảm xúc xoay quanh đau khổ/an toàn chứ không phải bảng màu angry/happy/sad/neutral diễn xuất. 77.76 UA **không phải mục tiêu Pebble nên kỳ vọng đạt được trên dữ liệu trẻ em** — SER giọng trẻ em luôn kém hơn SER người lớn, và 4 lớp diễn xuất của IEMOCAP không phải 12 cảm xúc ánh-xạ-GoEmotions hay thang severity của Pebble. Dùng bài cho *xếp hạng phương pháp*, không bao giờ làm thước đo tuyệt đối.
- **Dữ liệu pretraining của backbone càng quan trọng hơn với trẻ em.** wav2vec2/HuBERT pretrain trên tiếng Anh người lớn đọc/hội thoại (LibriSpeech/Libri-Light). Tần số cơ bản (F0), formant và tốc độ nói của trẻ em nằm ngoài-phân-phối. Đây chính là nơi **WavLM** (pretrain với nhiều tăng cường người-nói/nhiễu và giọng chồng lấn) thường thắng về robustness — và bài này *bỏ qua nó*. Bake-off của Pebble phải gồm WavLM và, lý tưởng, một bước continued-pretraining thích-nghi-giọng-trẻ-em (phiên bản âm thanh của MLM thích-nghi-miền D-F).
- **Severity từ giọng là hướng cao-rủi-ro, ít-bằng-chứng hơn.** Bài này chỉ làm cảm xúc phân loại. Head `severity` (hồi quy) của Pebble trên giọng **không có hậu thuẫn ở đây** — cường độ đau khổ qua ngữ điệu từ giọng trẻ em là một bài toán thực sự mở và không được thừa hưởng sự lạc quan của các con số phân loại. Coi hướng severity-giọng là thử nghiệm; giữ quyết định an toàn child-facing v1 dẫn-dắt-bằng-văn-bản và heuristic, không dẫn-dắt-bằng-mô-hình-giọng.
- **Quyền riêng tư/đạo đức của giọng trẻ em.** Âm thanh trẻ em thô nhận-dạng-được nhiều hơn văn bản (voiceprint, người nói nền, manh mối vị trí). Bất kỳ hướng giọng nào cũng cần xử lý trên-thiết-bị hoặc kiểm-soát-chặt, xóa-mặc-định âm thanh thô sau khi embedding, và sự đồng ý của người giám hộ — một chế độ chặt hơn pipeline văn bản. Embedding SSL không ẩn danh; coi chúng là PII.
- **Biện pháp giảm thiểu.** (1) Đo lại toàn ma trận trên một tập cảm xúc giọng-trẻ-em trước khi tin bất kỳ xếp hạng nào. (2) Gồm WavLM và một backbone robust-với-nhiễu. (3) Thêm continued self-supervised pretraining giọng-trẻ-em nếu có bất kỳ âm thanh trẻ em chưa-gán-nhãn nào. (4) Báo cáo UA/macro và recall theo lớp (không chỉ WA) để các lớp đau khổ hiếm không bị che bởi đa số happy/neutral — cùng kỷ luật recall-floor Pebble áp cho văn bản.

### Hạn chế & câu hỏi mở cho Pebble

- **Mâu thuẫn/khoảng trống so với đề bài và với tài liệu SER rộng hơn — WavLM vắng mặt.** Đề bài khung hóa đây thành ma trận "wav2vec2 vs HuBERT vs WavLM"; bài chỉ có wav2vec2 và HuBERT (WavLM ra sau/song song). Các benchmark SUPERB/EmoBox (arXiv:2111.02735, EmoBox arXiv:2406.07162) thường xếp **WavLM-large ngang hoặc trên HuBERT/wav2vec2 cho SER**. Vậy kết luận "W2V2 ≥ HuBERT" của bài này **chưa đầy đủ và có thể đã bị vượt qua** cho việc chọn backbone — Pebble không thể chọn voice encoder chỉ từ bài này; phải tự chạy cột thứ ba (WavLM).
- **Không phân tích lớp — mâu thuẫn với khung "lớp nào giúp ích."** Đề bài hỏi lớp nào mang cảm xúc; bài này fine-tune *toàn bộ* backbone và lấy trung bình checkpoint, không bao giờ soi đóng góp per-layer. Giao thức ER của SUPERB (backbone đóng băng + học trọng-số-lớp) là cách chuẩn để thấy "lớp nào giúp ích," và thường thấy **các lớp transformer giữa-tới-trên** mang cảm xúc nhiều nhất. Bake-off của Pebble nên thêm một biến thể frozen+layer-weighted để khôi phục tín hiệu này, vì fine-tune toàn backbone tốn kém và có thể không cần nếu vài lớp + pooling là đủ.
- **Frozen-vs-fine-tuned không được ablate.** Fine-tuning luôn bật ở đây; bài không bao giờ báo cáo con số (rẻ hơn nhiều) backbone-đóng-băng kiểu SUPERB, nên Pebble không có hướng dẫn về đánh đổi compute/accuracy của việc đóng băng — một câu hỏi thật khi dữ liệu giọng-trẻ-em khan hiếm (fine-tune một mô hình SSL lớn trên ít clip trẻ em có nguy cơ overfit; frozen + head nhỏ có thể chuyển giao tốt hơn).
- **Benchmark nhỏ, diễn xuất.** 5,531 utterance, 10 người nói, 4 lớp diễn xuất. Phương sai theo fold-người-nói lớn; các chênh lệch "nhỉnh hơn một chút" (ECAPA vs mean, 0.11 WACC) nằm trong nhiễu hợp lý. Pebble nên coi các chênh lệch dưới-1% ở đây là hòa, không phải thứ tự.
- **Không calibration, không xác-suất-để-quyết-định.** Như vài bài trong tập Pebble, chỉ báo cáo accuracy; Decision Engine của Pebble cần xác suất severity/emotion đã calibrate từ hướng giọng, điều bài này không đề cập.
- **Mâu thuẫn xuyên-phương-thức đáng nêu so với kế hoạch text-first của Pebble.** Bài cho thấy SSL chỉ-audio vượt một BERT fine-tune trên transcript *chuẩn* khoảng ~6% (set 1.B vs exp 10). Nếu điều đó đúng cho đau khổ trẻ em, nó sẽ lập luận giọng > văn bản — nhưng gần như chắc chắn **không** chuyển giao: baseline BERT ở đây cố ý under-tuned ("có thể không theo kỹ thuật SOTA tiên tiến nhất"), transcript đậm cảm-xúc-diễn-xuất, và hướng văn bản của Pebble dùng NeoBERT thích-nghi-miền, không phải BERT yếu. Pebble nên giữ văn bản là phương thức chính và coi giọng là tín hiệu bổ sung, không thay thế, cho tới khi đo trên dữ liệu trẻ em.
- **Câu hỏi mở cho Pebble.** Có *bất kỳ* kho ngữ liệu cảm xúc/đau-khổ giọng-trẻ-em có giấy phép nào để neo bake-off không? Không có nó, hướng giọng vẫn là một spike nghiên cứu và quyết định child-facing v1 vẫn dẫn-dắt-bằng-văn-bản. Đáng phạm vi hóa một slice calibration giọng-trẻ-em nội bộ nhỏ (có đồng ý) theo cách Pebble dự định một slice calibration văn-bản child-register.
