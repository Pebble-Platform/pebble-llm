# Paper 32 — The INTERSPEECH 2009 Emotion Challenge

## 1. Thông tin thư mục

**Tiêu đề:** The INTERSPEECH 2009 Emotion Challenge

**Tác giả:** Björn Schuller (Institute for Human-Machine Communication, Technische Universität München, Đức), Stefan Steidl, Anton Batliner (Chair of Pattern Recognition, Friedrich-Alexander University Erlangen-Nuremberg, Đức).

**Năm / hội nghị:** Kỷ yếu INTERSPEECH 2009, 6–10 tháng 9 năm 2009, Brighton, Anh, trang 312–315. ISCA. DOI 10.21437/Interspeech.2009-103.

**Từ khóa (nguyên văn):** "emotion, challenge, feature types, classification".

**Vì sao bài này quan trọng với Pebble:** Đây là bài báo đã *chuẩn hóa* cách đánh giá nhận dạng cảm xúc từ giọng nói (speech-emotion-recognition, SER). Nó là phiên bản khai sinh của chuỗi thử thách INTERSPEECH ComParE / Paralinguistics kéo dài nhiều năm, và đã giới thiệu (a) kho ngữ liệu cảm xúc trẻ em FAU-AIBO với một phép chia (split) độc lập người nói (speaker-independent) cố định, (b) bộ đặc trưng âm học IS09 384 chiều (16 LLD × functionals), và (c) quy ước rằng **Unweighted Average (UA) recall**, chứ không phải accuracy, là độ đo chính cho cảm xúc mất cân bằng lớp (imbalanced). Đối với luận điểm modality voice-message của Pebble, đây là trích dẫn kinh điển cho việc *SER được đánh giá như thế nào* và *vì sao cảm xúc mất cân bằng lớp cần UA*.

## 2. Động lực của vấn đề

Các tác giả mở đầu bằng một phàn nàn mang tính cấu trúc về lĩnh vực SER khoảng năm 2009: trái với Automatic Speech Recognition (ASR) và Speaker Recognition, "thực tế không tồn tại kho ngữ liệu và điều kiện kiểm thử chuẩn hóa nào để so sánh hiệu năng dưới đúng cùng một điều kiện." Hai thất bại cụ thể được nêu tên:

1. **Đánh giá không thể so sánh.** "Đọc kết quả trên dữ liệu được phân hoạch ngẫu nhiên, người ta không biết cấu hình chính xác. Hệ quả là các con số không thể so sánh được, kể cả khi 10-fold cross-validation được hai nhóm khác nhau sử dụng: các phép chia có thể hoàn toàn khác nhau." Phần lớn công trình trước đó dùng kiểm thử phụ thuộc người nói (subject-dependent) hoặc percentage-split / cross-validation *với lựa chọn instance ngẫu nhiên*, làm rò rỉ dữ liệu người nói mục tiêu vào tập huấn luyện. Chỉ **Leave-One-Subject-Out** hoặc **Leave-One-Subject-Group-Out** mới thực sự đảm bảo độc lập người nói.
2. **Dữ liệu không thực tế.** "Thực tế gần như mọi cơ sở dữ liệu được các nhóm khác nhau sử dụng, chẳng hạn EMO-DB miễn phí và rất phổ biến, không chứa giọng nói thực tế, không-được-mớm-lời (non-prompted) mà là giọng nói được mớm lời, được diễn (acted)." Dữ liệu diễn có các lớp sạch, cân bằng mà âm học "không thể đơn giản chuyển sang dữ liệu thực tế được."

Một vấn đề thứ ba, âm thầm hơn: **hỗn loạn về bộ đặc trưng.** "Thực tế không có cùng một bộ đặc trưng nào được tìm thấy hai lần: sự đa dạng cao không chỉ ở việc lựa chọn low-level descriptor (LLD), mà còn ở perceptual adaptation, speaker adaptation, và — nhất là — việc lựa chọn và triển khai functionals." Điều này được đối chiếu với các chuẩn MFCC/RASTA/PLP đã ổn định của ASR.

Thử thách được định vị là người kế nhiệm công khai của sáng kiến CEICES (ref [5]), nơi bảy nhóm so sánh bộ phân loại dưới điều kiện giống hệt nhau nhưng "không hoàn toàn mở cho công chúng."

## 3. Thiết kế thử thách (ba sub-challenge)

Được xây dựng trên các bài toán cảm xúc **non-prototypical năm lớp hoặc hai lớp** (toàn bộ kho ngữ liệu, không phải một tập con sạch):

- **Open Performance Sub-Challenge** — đặc trưng riêng, bộ phân loại riêng, nhưng phải tuân theo phép chia test/train cố định.
- **Classifier Sub-Challenge** — người tham gia dùng các file ARFF 384-feature chuẩn của ban tổ chức (sub-sample, biến đổi, bootstrap, hợp nhất bộ phân loại qua ROVER / ensemble); không được dùng file audio.
- **Feature Sub-Challenge** — người tham gia tải lên ≤100 đặc trưng tốt nhất của họ mỗi đơn vị phân tích; ban tổ chức kiểm thử với cùng thiết lập và gộp chúng trong một quá trình lựa chọn đặc trưng. Nhãn của tập test bị ẩn; tối đa 25 lần tải dự đoán mỗi người tham gia trả về confusion matrix.

**Độ đo chính, nêu rõ ràng:** "Vì các lớp mất cân bằng, độ đo chính cần tối ưu sẽ là unweighted average (UA) recall, và thứ hai là weighted average (WA) recall (tức accuracy)." Câu này chính là đóng góp phương pháp luận then chốt cho Pebble.

## 4. Đào sâu dữ liệu — FAU-AIBO Emotion Corpus

**Thu thập.** Bản ghi của **51 trẻ em (tuổi 10–13, 21 nam, 30 nữ)** tương tác với robot thú cưng Aibo của Sony trong thiết lập Wizard-of-Oz — trẻ tin rằng Aibo tuân lệnh chúng, nhưng một người vận hành điều khiển nó theo một chuỗi bất tuân cố định để khơi gợi phản ứng cảm xúc. Thu thập tại **hai trường, MONT và OHM**. ~**9,2 giờ giọng nói** (không tính khoảng lặng). Headset không dây chất lượng cao, máy ghi DAT, 16-bit, 48 kHz hạ mẫu xuống 16 kHz. Giọng nói trẻ em **tiếng Đức** tự phát (spontaneous).

**Gán nhãn.** Phân đoạn tự động thành "turn" qua ngưỡng khoảng lặng 1 giây. **Năm người gán nhãn** (sinh viên ngôn ngữ học nâng cao) gán nhãn từng *từ* độc lập là neutral (mặc định) hoặc một trong mười lớp khác. Nhãn được giải quyết bằng **majority voting (MV)**: ≥3 trong 5 người gán nhãn phải đồng ý. Số đếm MV mức từ: joyful (101), surprised (0), emphatic (2.528), helpless (3), touchy/irritated (225), angry (84), motherese (1.260), bored (11), reprimanding (310), rest (3), neutral (39.169); 4.707 từ không có MV; **tổng 48.401 từ**.

**Đơn vị phân tích = chunk.** Công trình trước [1, Table 7.22] cho thấy đơn vị tốt nhất "không phải là từ cũng không phải turn, mà là một chunk trung gian nào đó." Các chunk được định nghĩa thủ công theo tiêu chí syntactic-prosodic được sử dụng. **Toàn bộ kho ngữ liệu = 18.216 chunk** được dùng (không phải tập con prototypical).

**Hai sơ đồ nhãn (trái tim của giao thức).**

*5-class* — các lớp bao phủ Anger (= angry + touchy + reprimanding), Emphatic, Neutral, Positive (= motherese + joyful), Rest:

| Lớp | A | E | N | P | R | Tổng |
|---|---|---|---|---|---|---|
| train | 881 | 2.093 | 5.590 | 674 | 721 | 9.959 |
| test | 611 | 1.508 | 5.377 | 215 | 546 | 8.257 |
| tổng | 1.492 | 3.601 | 10.967 | 889 | 1.267 | 18.216 |

(Table 1.) Mất cân bằng nghiêm trọng: Neutral chiếm 60% dữ liệu; Positive và Rest mỗi lớp <5%.

*2-class* — NEGative (= angry + touchy + reprimanding + emphatic) so với IDLe (mọi trạng thái không tiêu cực):

| Lớp | NEG | IDL | Tổng |
|---|---|---|---|
| train | 3.358 | 6.601 | 9.959 |
| test | 2.465 | 5.792 | 8.257 |
| tổng | 5.823 | 12.393 | 18.216 |

(Table 2.)

**Phép chia độc lập người nói (đòn bẩy tái lập).** "Độc lập người nói được đảm bảo bằng cách dùng dữ liệu của một trường (OHM, 13 nam, 13 nữ) để huấn luyện và dữ liệu của trường kia (MONT, 8 nam, 17 nữ) để kiểm thử." Các chunk train theo thứ tự tuần tự với ID trẻ; **các chunk test được trình bày theo thứ tự ngẫu nhiên không có thông tin người nói** — ngăn mọi adaptation người nói lúc kiểm thử. Bản phiên âm (transliteration) + từ vựng kho ngữ liệu được cung cấp cho huấn luyện ASR / tính đặc trưng ngôn ngữ.

**Baseline ngẫu nhiên (chance).** Chọn lớp đa số cho WA (accuracy) **70,1%** (2-class) và **65,1%** (5-class); UA recall ngẫu nhiên là **50%** (2-class) và **20%** (5-class). Những con số này là lý do accuracy gây hiểu nhầm — một bộ phân loại không-làm-gì vẫn đạt 65–70% accuracy.

## 5. Bộ đặc trưng IS09 (384 đặc trưng)

Cung cấp qua bộ công cụ mã nguồn mở **openSMILE** để "minh bạch cao nhất." Cấu trúc:

**16 low-level descriptor (LLD)**, mỗi cái với hệ số delta (Δ) → 32 đường (contour):
zero-crossing-rate (ZCR), RMS frame energy, tần số pitch F0 (chuẩn hóa về 500 Hz), harmonics-to-noise ratio (HNR bằng autocorrelation), và **MFCC 1–12** (tương thích HTK).

**12 functionals** áp dụng theo từng chunk lên mỗi contour: mean, standard deviation, kurtosis, skewness, giá trị min, giá trị max, vị trí tương đối (của min/max), range, và hai hệ số linear-regression (offset, slope) cùng mean-square error (MSE) của chúng.

**Tổng: 16 × 2 × 12 = 384 thuộc tính mỗi chunk** (Table 3). Đây là bộ đặc trưng "IS09" / IS09-emotion vẫn được trích dẫn như một baseline chuẩn 15+ năm sau.

## 6. Hệ thống baseline và kết quả

Hai "kiến trúc chủ đạo" được đánh giá, cố ý chỉ dùng các công cụ công khai, cấu hình mặc định (HTK + WEKA) để tái lập:

**Mô hình động (HMM, trên các contour LLD).** HMM linear left-right, một mô hình mỗi cảm xúc, số trạng thái thay đổi (1/3/5), 2 Gaussian mixture, 6+4 vòng Baum-Welch, giải mã Viterbi. Up-sampling không có tác dụng ở đây (một HMM mỗi lớp, prior bằng nhau).

| Bài toán | #States | UA recall | WA recall |
|---|---|---|---|
| 2-class | 1 | 62,3 | 71,7 |
| 2-class | 3 | 62,9 | 57,5 |
| 2-class | 5 | **66,1** | 65,3 |
| 5-class | 1 | 35,5 | 50,8 |
| 5-class | 3 | 35,2 | 34,7 |
| 5-class | 5 | **35,9** | 37,2 |

(Table 4, cột recall.)

**Mô hình tĩnh (SVM trên 384 đặc trưng).** Sequential minimal optimisation, **linear kernel**, pairwise multi-class. Mất cân bằng lớp xử lý bằng **SMOTE** up-sampling tập huấn luyện; **standardisation** toàn-tập cũng được thử. Chiến lược tiền xử lý: B = balancing (SMOTE), S = standardisation; "-" = không cái nào. Thứ tự quan trọng vì standardisation hành xử khác sau khi balancing.

| Bài toán | Process | UA recall | WA recall |
|---|---|---|---|
| 2-class | – | 62,7 | 72,6 |
| 2-class | S | **67,6** | 68,3 |
| 2-class | B | **67,7** | 65,5 |
| 5-class | – | 28,9 | **65,6** |
| 5-class | S | **38,2** | 39,2 |
| 5-class | B | 38,0 | 32,2 |

(Table 5, cột recall.)

**Các baseline chính thức của thử thách** (con số mà cộng đồng cạnh tranh): **2-class UA ≈ 67,7%, 5-class UA = 38,2%** (các hàng SVM tốt nhất). Lưu ý mẫu chẩn đoán ở hàng 5-class "–": **WA 65,6% nhưng UA chỉ 28,9%** — một bộ phân loại chủ yếu dự đoán Neutral đạt accuracy gần-ngẫu-nhiên nhưng *vô dụng*, điều UA phơi bày ngay lập tức. Tối ưu cho accuracy (WA) và tối ưu cho UA kéo theo hai hướng ngược nhau trên dữ liệu mất cân bằng; các tác giả tối ưu UA.

**Về tính thực tế (Sec. 4).** Các thí nghiệm chỉ-MV / tập-con-prototypical trước đó đạt 4-class UA "trên 65%", và "chỉ dùng các trường hợp rất prototypical, unweighted average recall gần 80%"; ánh xạ về 2 lớp "có thể đẩy lên trên 90%." Dùng *toàn bộ* kho ngữ liệu thực tế cố ý "hạ thấp kỳ vọng của chúng tôi" — bằng phép loại suy với chuyển tiếp read-to-spontaneous của ASR nơi lỗi gần như gấp đôi. Đây là phát biểu rõ ràng rằng *các con số SER trên tập-con-prototypical không chuyển sang dữ liệu thực tế.*

## Deep research — full-PDF read (2026-06-16)

### Ghi chú truy cập nguồn

Đọc từ PDF cục bộ `docs/papers/pdfs/32-interspeech2009-emotion-challenge.pdf` qua `pdftotext` (toàn văn, cả 4 trang gồm Bảng 1–5 và phần tài liệu tham khảo). PDF mang DOI `10.21437/Interspeech.2009-103` và dòng bản quyền ISCA, tức nó *chính là* phiên bản hội nghị, nên không có chênh lệch preprint-vs-published cần đối chiếu.

Xác minh web đã thực hiện:
- Tìm `"INTERSPEECH 2009 Emotion Challenge Schuller Steidl Batliner FAU Aibo 384 features baseline UA WA recall"` → trang ISCA Archive `https://www.isca-archive.org/interspeech_2009/schuller09_interspeech.html` xác nhận tiêu đề, tác giả, nền tảng FAU-Aibo, bộ 384-feature, và "unweighted average (UA) recall" là độ đo chính. ✔
- Tìm `"FAU Aibo Emotion Corpus 18216 chunks 51 children 5-class 2-class speaker independent OHM MONT"` → trang kho ngữ liệu FAU Pattern Recognition Lab + các bài corroborating xác nhận **18.216 chunk, 51 trẻ em, ~9,2 giờ, ~48k từ, 5 người gán nhãn, gán nhãn mức từ, ánh xạ 2- và 5-class**. ✔
- Tìm `"INTERSPEECH 2009 Emotion Challenge baseline 5-class unweighted average recall 38.2%"` → nhiều bài SER hậu kỳ trích dẫn **38,2% UA (5-class)** và ~67% UA (2-class) như *các* baseline IS09. ✔ Phân tách HMM-vs-SVM (5-class: 35,5% HMM dynamic, 28,9% SVM static thô) cũng được corroborate, khớp chính xác Bảng 4–5.

Mọi con số then chốt bên dưới được gắn thẻ ✔ corroborated (con số có cả trong PDF hội nghị và được ≥1 nguồn độc lập trích lại) hoặc ≈ approximate (làm tròn / cụm từ "above" trong chính bài).

### Bài báo thực sự làm gì

Nó định nghĩa một benchmark SER tái lập được và báo cáo hai baseline tham chiếu.

- **Kho ngữ liệu:** FAU-AIBO, **18.216 chunk** giọng nói trẻ em tiếng Đức tự phát (51 trẻ, tuổi 10–13, ~9,2 giờ) [§2 / Table 1–2]. ✔
- **Nhãn:** mức từ bởi 5 rater, majority-vote (≥3/5), gộp về mức chunk thành sơ đồ **5-class** (Anger / Emphatic / Neutral / Positive / Rest) và **2-class** (NEGative / IDLe) [§2]. ✔
- **Phép chia:** **độc lập người nói** nghiêm ngặt, tách theo trường — train = OHM (9.959 chunk), test = MONT (8.257 chunk); test trình bày theo thứ tự ngẫu nhiên không ID người nói [§2, Bảng 1–2]. ✔
- **Đặc trưng:** **IS09 = 384** = 16 LLD × 2 (+Δ) × 12 functionals, qua openSMILE [§3 / Table 3]. ✔
- **Baseline:** HMM (động, trên LLD) và **SVM** (tĩnh, trên 384 đặc trưng, SMOTE balancing + standardisation), cả hai trong công cụ công khai cấu hình mặc định (HTK, WEKA) [§5]. ✔
- **Độ đo:** **UA recall chính**, WA recall (= accuracy) phụ, *vì các lớp mất cân bằng* [§1, §4]. ✔
- **Kết quả baseline chính [Bảng 4–5]:** ✔
  - 2-class: SVM tốt nhất **UA 67,7% / WA 65,5%** (balancing); HMM tốt nhất UA 66,1%. Accuracy lớp đa số = 70,1%, UA ngẫu nhiên = 50%.
  - 5-class: SVM tốt nhất **UA 38,2% / WA 39,2%** (standardisation); SVM thô UA 28,9% nhưng WA 65,6%. Accuracy lớp đa số = 65,1%, UA ngẫu nhiên = 20%.
- **Cảnh báo về tính thực tế:** SER trên tập-con-prototypical đạt ~80% UA (4-class) / >90% (2-class), nhưng trên *toàn bộ kho ngữ liệu thực tế* hiệu năng "thấp hơn rõ rệt" [§4]. ≈ (bài dùng cụm "above"/"close to").

### Các phần trực tiếp hữu ích cho Pebble

1. **UA recall làm độ đo chính cho cảm xúc mất cân bằng** [§1, §4]. → **D-C, D-G.** Ý tưởng dễ chuyển giao nhất: với 60% Neutral, *accuracy là độ đo phù phiếm* (SVM thô đạt WA 65,6% / UA 28,9%). Cả emotion head (12-label, GoEmotions-mapped) và severity head của Pebble đều mất cân bằng lớp; UA recall (= macro-recall) phải là độ đo được báo cáo và tối ưu, không chỉ là accuracy/F1.
   - *Rủi ro chuyển giao:* **Thấp.** Đây là lựa chọn độ đo, không phụ thuộc modality — nó chuyển trực tiếp từ giọng nói sang cảm xúc văn bản. Lưu ý duy nhất: emotion head của Pebble là *multi-label* (GoEmotions) trong khi IS09 là single-label; macro-recall vẫn tổng quát hóa được nhưng phải tính theo từng-label rồi lấy trung bình.

2. **Kỷ luật phép chia độc lập người nói / nguồn** [§2, Bảng 1–2]. → **D-H.** Phép chia tách-theo-trường OHM/MONT, với chunk test bị loại bỏ ID người nói, là chuẩn vàng chống lại rò rỉ mà bài cảnh báo ("lựa chọn instance ngẫu nhiên... có thể chứa dữ liệu của người nói mục tiêu"). → Pebble phải chia kho ngữ liệu silver-label theo *trẻ / nguồn*, không bao giờ theo hàng ngẫu nhiên, nếu không sẽ báo cáo quá cao.
   - *Rủi ro chuyển giao:* **Thấp–trung bình.** Nguyên tắc là phổ quát; điểm khác biệt là silver label của Pebble đến từ các tập công khai tái sử dụng (GoEmotions/SemEval/WASSA), nên "độc lập người nói" trở thành "độc lập *dataset-gốc* và *tác giả/subreddit*". Rủi ro rò rỉ là có thật (GoEmotions có tác giả Reddit lặp lại) và biện pháp giảm thiểu giống nhau: chia tách theo nhóm (group-disjoint).

3. **Tư duy ngưỡng-sàn macro-recall cho các lớp thiểu số liên quan an toàn** [§4]. → **D-C, D-G.** Kết quả 5-class cho thấy các lớp thiểu số (Positive 5%, Rest 7%) chính là nơi mô hình accuracy-cao sụp đổ; UA buộc đo mô hình trên chúng. → Các tầng severity / high-distress của Pebble là các lớp hiếm-nhưng-then-chốt tương tự; chính sách recall-floor là phiên bản vận hành của "tối ưu UA."
   - *Rủi ro chuyển giao:* **Trung bình.** Các lớp của IS09 là cover-class cảm xúc không mang ngữ nghĩa an toàn; tầng high-severity của Pebble thực sự an toàn-then-chốt, nên một *floor* (recall ≥ mục tiêu) mạnh hơn "tối ưu trung bình" của IS09. Hướng đi chuyển giao được; độ nghiêm ngặt phải tăng.

4. **Cảnh báo "con số tập-con-prototypical không chuyển sang dữ liệu thực tế"** [§4]. → **D-C, D-D, D-H.** Cùng kho ngữ liệu: ~80% UA trên ca sạch so với 38,2% UA trên toàn tập. → Một cảnh báo trực tiếp cho kế hoạch transfer severity của Pebble (D-D): các bar mượn từ tập-con benchmark sạch sẽ phóng đại hiệu năng đạt được trên các turn child-register lộn xộn.
   - *Rủi ro chuyển giao:* **Thấp.** Đây là bài học xuyên suốt về dữ liệu thực tế vs được tuyển chọn, áp dụng càng đúng hơn cho chế độ silver-label / child-register của Pebble.

5. **Bản thân công thức 384-feature openSMILE** [§3, Table 3]. → **D-A (chỉ modality voice).** Nếu/khi Pebble thêm một nhánh *voice-message*, IS09 (và các hậu duệ eGeMAPS / ComParE) là front-end âm học kinh điển, rẻ, tái lập được và là baseline mà mọi bài SER báo cáo so với.
   - *Rủi ro chuyển giao:* **Cao cho v1.** Pebble v1 là một encoder *văn bản* (NeoBERT); các đặc trưng âm học này không nuôi nó. Điểm này là artifact v2/voice-modality, không phải head v1. Đánh dấu là hướng-tới-tương-lai, chưa hành động ngay.

### Mỗi phần giúp Pebble thành công như thế nào

- **Emotion head (D-C):** Thêm **UA recall (macro-recall trên 12 label GoEmotions)** vào eval card của emotion head bên cạnh micro-F1 và accuracy, và biến nó thành độ đo *chọn* checkpoint. Cụ thể: một mô hình đạt micro-F1 cao bằng cách luôn dự đoán các label thường gặp (neutral, approval) sẽ có UA thấp — đúng chế độ thất bại của IS09 — và phải bị từ chối. Đây là bar macro-recall C-SSRS hiện có (47,8%) tổng quát hóa sang emotion head.
- **Severity head (D-C, D-D, D-G):** Báo cáo hiệu năng severity với bảng recall theo-tầng, không chỉ Pearson r. Table 5 của IS09 là mẫu: hiển thị UA cạnh WA để người duyệt thấy chi phí mất cân bằng. Đặt recall tầng high-severity làm *floor* và để precision trôi nổi — phép tương đương vận hành của "tối ưu UA."
- **Phép chia dữ liệu (D-H):** Xây phép chia train/val/test *group-disjoint theo dataset nguồn và theo author/subreddit nơi có ID*, phản ánh OHM/MONT. Thêm một kiểm tra kiểu unit-test rằng không author/source ID nào xuất hiện ở hai phân vùng. Đây là phòng thủ rẻ nhất chống bẫy con-số-bị-phóng-đại mà cả bài này được xây để ngăn.
- **Đặt bar (D-D):** Khi nhập các transfer bar (SemEval/WASSA Pearson, C-SSRS accuracy), chú thích mỗi cái đến từ phép chia *prototypical/được-tuyển* hay *full/realistic*, và chiết khấu tương ứng — IS09 định lượng khoảng cách (≈80% → 38% UA) là chi phí của việc đi vào thực tế.
- **Nhánh voice (D-A, v2):** Nếu một voice-message head được phạm vi hóa, bắt đầu từ hậu duệ openSMILE eGeMAPS/ComParE của bộ 384 này làm front-end baseline và báo cáo UA trên giọng nói trẻ em kiểu FAU-AIBO để so sánh đối chiếu bên ngoài.

### Lăng kính sức khỏe tâm thần trẻ em

Đáng chú ý, đây là **một trong rất ít kho ngữ liệu giọng nói trẻ em trong toàn bộ tập công trình liên quan** — FAU-AIBO là 51 trẻ tuổi 10–13, giọng nói cảm xúc tự phát, trong-thực-tế. Điều đó khiến các bài học *phương pháp luận* của nó đặc biệt đúng-mục-tiêu cho một sản phẩm hướng-trẻ-em, dù modality (giọng nói âm học tiếng Đức) khác Pebble v1 (văn bản tiếng Anh).

- **Tính hợp lệ chuyển giao (tích cực):** *Giao thức đánh giá* (UA-chính, phép chia độc lập người nói, tính thực tế toàn-corpus) không phụ thuộc modality và ngôn ngữ, chuyển giao sạch sang các text head của Pebble. Kho ngữ liệu chứng minh tín hiệu cảm xúc trẻ em có thể khôi phục nhưng *khó* (38,2% UA trên 5 lớp thực tế) — một bar trung thực, tỉnh táo cho cảm xúc child-register.
- **Rủi ro chuyển giao (tiêu cực):** *Nội dung* không chuyển giao. (a) Modality: prosody âm học ≠ token văn bản NeoBERT; 384 đặc trưng vô dụng với encoder văn bản v1. (b) Ngôn ngữ: giọng trẻ Đức nói với robot Sony ≠ chat trẻ em tiếng Anh với companion app. (c) Phân loại cảm xúc: cover-class của AIBO (Anger/Emphatic/Neutral/Positive/Rest, cáu kỉnh hướng-robot) ≠ sơ đồ 12-label liên quan-sức-khỏe-tâm-thần của GoEmotions. Không *nhãn* nào của AIBO nên được tái dùng làm mục tiêu huấn luyện Pebble.
- **Biện pháp giảm thiểu:** Dùng FAU-AIBO chỉ như (1) trích dẫn cho độ đo UA và quy ước phép-chia-độc-lập-người-nói, và (2) — nếu một nhánh voice được xây — một tập so sánh SER giọng trẻ em bên ngoài, không bao giờ là nguồn huấn luyện v1.
- **Đạo đức:** FAU-AIBO là một nghiên cứu Wizard-of-Oz lừa dối trên trẻ vị thành niên (trẻ tin robot tự hành), thực hiện năm 2009 dưới chuẩn mực thời đó, và bị giới hạn truy cập cho nghiên cứu. Pebble không thể tái dùng dữ liệu của nó và không nên sao chép thiết kế lừa dối; trích dẫn nó cho giao thức, không cho phương pháp luận thu-thập-dữ-liệu.

### Hạn chế & câu hỏi mở cho Pebble

- **Mâu thuẫn / khoảng trống vs kế hoạch Pebble — báo cáo lấy-accuracy-làm-trung-tâm.** Luận điểm cốt lõi của IS09 là **accuracy (WA) chủ động gây hiểu nhầm** trên cảm xúc mất cân bằng (SVM thô: WA 65,6% nhưng UA 28,9%, 5-class). Bất kỳ eval nào của Pebble dẫn đầu bằng accuracy hoặc micro-F1 trên emotion/severity head đều vi phạm trực tiếp chuẩn 15-năm-tuổi này. Eval card của Pebble phải đặt **macro/UA recall trước**. (Điều này cũng làm sắc D-C: các bar C-SSRS nêu là "52% acc / 0.75 wF1 / 47.8% macro-recall" nên được đọc với macro-recall là ràng buộc ràng buộc, đúng theo IS09.)
- **Mâu thuẫn vs Paper 01 (FAIIR) về độ đo.** FAIIR báo cáo precision/recall/F1 sample-averaged và AUROC và *không bao giờ báo cáo UA / macro-recall*; headline của nó là recall-tại-ngưỡng (0,81) trên tag multi-label. IS09 sẽ gọi đó là bức tranh không đầy đủ trên dữ liệu mất cân bằng. Pebble nên báo cáo *cả hai* họ (P/R/F1 theo-tag kiểu FAIIR *và* UA/macro-recall kiểu IS09) thay vì kế thừa điểm mù của một trong hai bài.
- **Bất khớp single-label vs multi-label.** IS09 là single-label (một cảm xúc mỗi chunk); emotion head của Pebble là multi-label (GoEmotions). "UA recall" như IS09 định nghĩa (trung bình recall theo-lớp trong confusion matrix) cần được định nghĩa lại cho multi-label — Pebble phải định nghĩa macro-recall là trung bình các recall nhị phân theo-label và nêu rõ điều này, vì định nghĩa IS09 không chuyển sang nguyên văn.
- **Không mô hình học được, không calibration, không xác suất.** IS09 chỉ báo cáo dự đoán điểm từ SVM/HMM; không calibration, không ngưỡng, không đầu ra xác suất. Nó cho Pebble *không* hướng dẫn nào về chính sách calibration / ngưỡng (D-G) ngoài "tối ưu UA." Khoảng trống đó phải được lấp từ các bài khác.
- **Khoảng cách modality là toàn diện cho v1.** Mọi artifact cụ thể trong bài này (đặc trưng, bộ phân loại, kho ngữ liệu) đều là âm học; chỉ *triết lý đánh giá* sống sót qua bước nhảy sang văn bản. Câu hỏi mở: luận điểm voice-message của Pebble có ý định một acoustic head thực sự (thì IS09/openSMILE là front-end và FAU-AIBO là tập so sánh), hay chỉ ASR-sang-văn-bản (thì IS09 chỉ đóng góp độ đo và kỷ luật phép chia, và 384 đặc trưng không liên quan)? Quyết định phạm vi này xác định liệu nhánh voice của D-A có sống hay không.
