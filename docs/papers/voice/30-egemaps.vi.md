# Bài báo 30 — GeMAPS / eGeMAPS: Bộ Tham số Âm học Tối giản Geneva cho Nghiên cứu Giọng nói và Tính toán Cảm xúc

## 1. Thông tin thư mục

**Tiêu đề:** The Geneva Minimalistic Acoustic Parameter Set (GeMAPS) for Voice Research and Affective Computing (Bộ Tham số Âm học Tối giản Geneva cho Nghiên cứu Giọng nói và Tính toán Cảm xúc).

**Tác giả:** Florian Eyben (TU München / Univ. Genève / audEERING), Klaus R. Scherer (Univ. Genève), Björn W. Schuller (Univ. Passau / Imperial College London / Univ. Genève), Johan Sundberg (KTH Stockholm), Elisabeth André (Univ. Augsburg), Carlos Busso (UT Dallas), Laurence Y. Devillers (Paris-Sorbonne / CNRS-LIMSI), Julien Epps (UNSW / NICTA), Petri Laukka (Stockholm Univ.), Shrikanth S. Narayanan (SAIL, USC), Khiet P. Truong (Univ. Twente).

**Năm / nơi công bố:** *IEEE Transactions on Affective Computing*, Tập 7, Số 2, trang 190–202, tháng 4–6/2016. DOI 10.1109/TAFFC.2015.2457417. Cấp phép CC-BY 3.0. Khuyến nghị này được hình thành tại "Bridge Meeting" ở Geneva (Swiss Center of Affective Sciences, 1–2/9/2013).

**Từ khóa chỉ mục (nguyên văn):** "Affective Computing, Acoustic Features, Standard, Emotion Recognition, Speech Analysis, Geneva Minimalistic Parameter Set".

**Triển khai:** công khai trong bộ công cụ openSMILE (config `GeMAPSv01a` / `eGeMAPSv01a`; bản hiện đại `eGeMAPSv02`). Đây là bài báo chuẩn hóa nằm sau các bộ đặc trưng mà các bài báo giọng nói khác trong tập Pebble đều giả định.

## 2. Tóm tắt một đoạn

GeMAPS là động thái cố ý của lĩnh vực để đối lại các bộ đặc trưng âm học kiểu vét cạn (brute-force) (ComParE 6.373 đặc trưng, v.v.). Thay vì "thu thập mọi thứ từng giúp một bộ phân lớp," một hội đồng liên ngành các nhà khoa học giọng nói đã thống nhất về một bộ tham số âm học **tối giản, có động cơ lý thuyết, có thể diễn giải**, đánh chỉ mục các thay đổi sinh lý do cảm xúc trong quá trình tạo giọng. **GeMAPS tối giản = 62 tham số** dẫn xuất từ **18 mô tả mức thấp (low-level descriptors, LLD)** cộng 6 đặc trưng theo thời gian; **eGeMAPS mở rộng = 88 tham số**, thêm 7 LLD phổ/cepstral (MFCC 1–4, spectral flux, băng thông formant 2–3) và mức âm tương đương (equivalent sound level). Việc chọn lựa theo ba tiêu chí: (a) tiềm năng đánh chỉ mục thay đổi sinh lý do cảm xúc trong tạo giọng, (b) giá trị đã được chứng minh trong tài liệu trước cộng khả năng trích xuất tự động đáng tin, (c) ý nghĩa lý thuyết. Đánh giá trên sáu kho ngữ liệu giọng nói cảm xúc cho phân loại nhị phân arousal/valence với SVM leave-one-speaker-out, eGeMAPS đạt **~79,7% UAR cho arousal** và **~66,4% cho valence** — "tương đương đáng kinh ngạc" với các bộ vét cạn lớn nhất ở mức **dưới 2%** kích thước của chúng. Với Pebble, đây là bộ từ vựng âm học chuẩn vận hành hóa khái niệm "tone of voice / âm sắc": F0, jitter, shimmer, HNR, loudness, formant, cân bằng phổ — một **đường cơ sở đặc trưng có thể diễn giải, chiều thấp** cho phương thức tin nhắn thoại.

## 3. Vì sao bài báo này nằm trong tập Pebble (phương thức tin nhắn thoại)

Đường chính của Pebble là văn bản (bộ mã hóa NeoBERT), nhưng luận điểm bao gồm phương thức **tin nhắn thoại**: trẻ có thể gửi một đoạn âm thanh ngắn. Để chấm điểm đoạn đó ở mức lượt (turn-level), trước hết dạng sóng phải trở thành đặc trưng. eGeMAPS định nghĩa *những* đặc trưng đó — bộ từ vựng âm học do chuyên gia tuyển chọn, có thể diễn giải, mà mọi benchmark giọng nói-cảm xúc trong tập này (ComParE, AVEC, các thử thách INTERSPEECH) đều báo cáo theo. Trong khi bài 29 (openSMILE) cung cấp *bộ máy*, bài này cung cấp *bộ từ vựng và sự xác thực của nó*: chính xác 18 LLD GeMAPS / 88 tham số eGeMAPS, lý do cho từng đặc trưng, và các con số arousal/valence liên kho ngữ liệu biện minh cho việc chọn một bộ nhỏ có thể diễn giải thay vì bộ vét cạn 6k. Nó dịch chuyển **D-D** (hồi quy severity/energy — nguồn chuyển giao âm học + nền tảng đặc trưng diễn giải được và các thước đo arousal/valence) và **D-H** (datasets / điểm neo đặc trưng / hiệu chỉnh). Đây là trích dẫn Pebble cần bất cứ khi nào tuyên bố một "đường cơ sở âm học có thể diễn giải cho phương thức thoại."

## Deep research — full-PDF read (2026-06-16)

### Ghi chú truy cập nguồn

PDF đầy đủ **đã được đọc từ đầu đến cuối** — `pdfs/30-egemaps.pdf` là bản được IEEE chấp nhận (CC-BY) của *IEEE T-AFFC* 2016, 10.1109/TAFFC.2015.2457417, trích xuất bằng `pdftotext`. Mọi liệt kê LLD, số lượng tham số, định nghĩa functional, mô tả tập dữ liệu và số liệu Bảng 1/2/3 dưới đây được đọc trực tiếp từ văn bản đầy đủ đó (§3.1 bộ tối giản, §3.2 phần mở rộng, §4 đánh giá cơ sở, Bảng 1–3, §5 thảo luận).

Xác thực xuất xứ phiên bản đã công bố:

- **Nơi công bố + số lượng.** Tìm kiếm: *"GeMAPS 62 parameters eGeMAPS 88 parameters 18 LLD Eyben 2016 IEEE Transactions Affective Computing arousal valence UAR"*. Giải quyết: dblp `https://dblp.org/rec/journals/taffco/EybenSSSABDELNT16.html` và preprint USC-SAIL `https://sail.usc.edu/publications/files/eyben-preprinttaffc-2015.pdf`. Xác nhận đã công bố là **IEEE T-AFFC Tập 7, Số 2, trang 190–202 (2016)**; **eGeMAPS = 88 tham số**; "eGeMAPS đạt tốt nhất cho arousal, gần 80% UAR." ✔ đã đối chiếu. Bản PDF được chấp nhận (cục bộ) và bản công bố thống nhất ở mọi con số then chốt; không có sai biệt preprint trên các con số.
- **GeMAPS = 62 / 18 LLD; mở rộng eGeMAPS = +7 LLD → 88.** Đọc từ §3.1 ("In total, 62 parameters are contained in the Geneva Minimalistic Standard Parameter Set") và §3.2 ("the extended … eGeMAPS contains 88 parameters"). Đối chiếu chéo với tài liệu openSMILE/audEERING được tóm tắt trong bản deep-read của bài 29. ✔ đã đối chiếu.
- **Số liệu UAR (Bảng 2):** GeMAPS arousal 79,59 / valence 65,32; eGeMAPS 79,71 / 66,44; ComParE 78,00 / 67,17. Đọc trực tiếp từ Bảng 2 của PDF. Phần văn xuôi của PDF cục bộ có một lỗi đảo chữ ("third best for arousal" trong khi dữ liệu rõ ràng nghĩa là valence — eGeMAPS *tốt nhất* về arousal ở 79,71 và *hạng ba* về valence sau ComParE 67,17 và InterSp12 66,71); các con số trong bảng là rõ ràng và được dùng ở đây. ≈ xấp xỉ ở văn xuôi, ✔ đã đối chiếu ở các con số bảng.

### Bài báo thực sự làm gì

**Mục tiêu (§1–2).** Hàng thập kỷ khoa học giọng nói tạo ra sự bùng nổ các tham số âm học được dùng có chọn lọc, trích xuất khác nhau (ngay cả trong "cùng một" công cụ như Praat, với cài đặt không công khai), khiến so sánh liên nghiên cứu là bất khả thi. Các bộ ML vét cạn (thường >6.000 đặc trưng) làm trầm trọng vấn đề: chúng quá khớp (over-adapt) vào tập huấn luyện nhỏ, tổng quát hóa kém khi liên kho ngữ liệu (kém hơn các bộ nhỏ dù điểm nội kho ngữ liệu cao hơn, theo [20]), và về cơ bản không thể diễn giải. Bài báo đề xuất một bộ tham số **chuẩn hóa, tối giản, có thể diễn giải** làm đường cơ sở chung — bất kỳ nhóm nào cũng có thể áp dụng cùng các đặc trưng riêng theo tác vụ của mình, cho phép tái lập và tích lũy bằng chứng. Triển khai mã nguồn mở trong openSMILE để chính xác cách tính được cố định, không chỉ tên tham số.

**Tiêu chí chọn lựa (§3).** Ba tiêu chí: (1) tiềm năng của một tham số đánh chỉ mục thay đổi sinh lý trong tạo giọng khi có quá trình cảm xúc; (2) tần suất và mức thành công của tham số trong tài liệu trước; (3) ý nghĩa lý thuyết. Đây là cách *do đồng thuận liên ngành dẫn dắt* một cách tường minh, đối lập (§2) với cách tiếp cận "người thu thập" do kỹ thuật dẫn dắt của CEICES.

**18 LLD của GeMAPS (§3.1), theo nhóm — đọc nguyên văn:**

*Liên quan tần số (6 LLD):*
- **Pitch** — F0 lôgarit trên thang bán cung (semitone) bắt đầu ở 27,5 Hz (bán cung 0).
- **Jitter** — độ lệch độ dài các chu kỳ F0 liên tiếp.
- **Formant 1, 2, 3 tần số** — tần số trung tâm của formant thứ nhất/hai/ba (3 LLD).
- **Băng thông Formant 1** — băng thông của formant thứ nhất.

*Liên quan năng lượng/biên độ (3 LLD):*
- **Shimmer** — hiệu biên độ đỉnh của các chu kỳ F0 liên tiếp.
- **Loudness** — ước lượng cường độ tín hiệu cảm nhận từ phổ thính giác.
- **Tỷ lệ Hài-trên-Nhiễu (HNR)** — năng lượng trong thành phần hài so với năng lượng trong thành phần giống nhiễu.

*Tham số phổ (cân bằng) (9 LLD):*
- **Alpha Ratio** — tỷ lệ năng lượng tổng 50–1000 Hz trên 1–5 kHz.
- **Hammarberg Index** — tỷ lệ đỉnh năng lượng mạnh nhất trong vùng 0–2 kHz trên đỉnh mạnh nhất trong 2–5 kHz.
- **Spectral Slope 0–500 Hz** và **Spectral Slope 500–1500 Hz** — độ dốc hồi quy tuyến tính của phổ công suất log trong mỗi băng (2 LLD).
- **Formant 1, 2, 3 năng lượng tương đối** — tỷ lệ năng lượng đỉnh hài phổ tại tần số trung tâm mỗi formant trên năng lượng đỉnh phổ tại F0 (3 LLD).
- **Hiệu hài H1–H2** — tỷ lệ năng lượng hài F0 thứ 1 trên thứ 2.
- **Hiệu hài H1–A3** — tỷ lệ năng lượng hài F0 thứ 1 trên hài cao nhất trong vùng formant thứ ba.

(Tức 6 + 3 + 9 = **18 LLD**.)

**Làm mượt.** Mọi LLD được làm mượt bằng trung bình trượt đối xứng 3 khung; với pitch/jitter/shimmer, làm mượt chỉ trong vùng hữu thanh (để chuyển tiếp hữu thanh/vô thanh không bị nhòe).

**Cách 18 LLD trở thành 62 tham số (§3.1):**
- **Trung bình cộng + hệ số biến thiên** (độ lệch chuẩn ÷ trung bình) áp cho cả 18 LLD → **36 tham số**.
- Chỉ cho **loudness và pitch**, thêm 8 functional mỗi cái: phân vị thứ 20/50/80, khoảng phân vị 20–80, và trung bình + độ lệch chuẩn của độ dốc các đoạn lên/xuống → +16, tổng **52 tham số**. Mọi functional chỉ áp cho vùng hữu thanh, *trừ* các functional của loudness (áp cho mọi vùng).
- Trung bình cộng của Alpha Ratio, Hammarberg Index, và hai spectral slope trên các đoạn **vô thanh** → +4, tổng **56 tham số**.
- **6 đặc trưng thời gian**: tốc độ đỉnh loudness mỗi giây; trung bình và độ lệch chuẩn độ dài vùng hữu thanh liên tục (F0 > 0); trung bình và độ lệch chuẩn độ dài vùng vô thanh (F0 = 0, ≈ khoảng lặng); số vùng hữu thanh liên tục mỗi giây (tốc độ giả-âm-tiết) → tổng **62 tham số**. Không áp độ dài tối thiểu nào lên vùng hữu/vô thanh; làm mượt F0 dựa trên Viterbi ngăn các khung hữu thanh đơn lẻ giả.

**Phần mở rộng eGeMAPS (§3.2): +7 LLD, +26 tham số → 88:**
- **MFCC 1–4** (Hệ số Cepstral theo thang Mel 1–4) và **spectral flux** (hiệu phổ của hai khung liên tiếp) — 5 LLD phổ/cepstral.
- **Băng thông Formant 2** và **băng thông Formant 3** — thêm cho đầy đủ với băng thông Formant 1 (2 LLD).
- Functional: trung bình + hệ số biến thiên trên cả 7 LLD thêm trên mọi đoạn (băng thông formant chỉ trên vùng hữu thanh) → +14. Cộng: trung bình spectral flux trong vùng vô thanh; trung bình + CV của spectral flux và của MFCC 1–4 trong vùng hữu thanh → +11. Cộng **mức âm tương đương (equivalent sound level)** → +1. Tổng **+26 → 88 tham số (eGeMAPS)**.

**Lý do chọn lựa, theo từng thành phần (§2 tổng hợp tài liệu):** F0 trung bình/biến thiên/khoảng và cường độ (loudness) là các mô tả tương quan arousal nhất quán nhất qua hàng thập kỷ; hình dạng phổ (alpha ratio, Hammarberg index, spectral slope) và **MFCC 1–4** mang thông tin **valence** và bền hơn với nhiễu/vang so với prosody; **formant** nhạy với cảm xúc và cho kết quả tải nhận thức và trầm cảm gần state-of-the-art ở một phần nhỏ số chiều, được cố ý đưa vào dù khó trích xuất nên nhiều bộ vét cạn bỏ qua; **jitter, shimmer, HNR** mã hóa thay đổi chất lượng giọng / nguồn kích thích; các hiệu hài **H1–H2 / H1–A3** đánh chỉ mục độ khép thanh môn (glottal adduction). MFCC bậc thấp được đưa vào (không phải bậc cao) vì qua cơ sở DCT-II, chúng nắm độ nghiêng phổ / phân bố năng lượng thô (liên quan cảm xúc) thay vì chi tiết âm vị tinh.

**Đánh giá (§4).** Tác vụ = phân loại nhị phân **arousal** và nhị phân **valence**. Sáu kho ngữ liệu giọng nói cảm xúc, mỗi cái ánh xạ về nhãn nhị phân arousal/valence chung (Bảng 1): FAU AIBO (giọng trẻ em tiếng Đức tự phát, chỉ valence), TUM-AVIC (mức độ quan tâm), EMO-DB (cảm xúc diễn xuất tiếng Berlin), GEMEP (khắc họa đa phương thức diễn xuất, 12 cảm xúc trên cả 4 góc phần tư), SING (cảm xúc giọng hát opera), VAM (talk-show tiếng Đức, tự phát). Bộ phân lớp = **SVM (SMO trong WEKA)**, kết quả lấy trung bình trên 9 thiết lập độ phức tạp (C) cao nhất trong 17 để ổn định. Kiểm định chéo **Leave-one-speaker(group)-out** (8 fold; AIBO dùng 2-fold OHM↔MONT). Phân vùng huấn luyện cân bằng lớp bằng up-sampling; đặc trưng **z-chuẩn hóa** (chuẩn hóa theo từng người nói được dùng cho các con số chính). So sánh với năm đường cơ sở vét cạn: InterSp09 (384), InterSp10 (1.582), InterSp11 (4.368), InterSp12 (6.125), ComParE 2013/14 (6.373).

**Kết quả (Bảng 2, UAR trung bình trên 5 kho ngữ liệu trừ FAU AIBO, chuẩn hóa theo người nói):**

| Bộ tham số | Số tham số | Arousal UAR | Valence UAR |
|---|---|---|---|
| **GeMAPS** | **62** | **79,59** | 65,32 |
| **eGeMAPS** | **88** | **79,71** | 66,44 |
| InterSp09 | 384 | 76,08 | 64,88 |
| InterSp10 | 1.582 | 76,50 | 64,44 |
| InterSp11 | 4.368 | 76,43 | 65,96 |
| InterSp12 | 6.125 | 77,26 | 66,71 |
| ComParE | 6.373 | 78,00 | 67,17 |

Mọi con số ✔ đọc từ Bảng 2. **eGeMAPS là bộ tốt nhất duy nhất về arousal (79,71) — vượt cả năm bộ vét cạn kể cả ComParE.** Về valence nó nằm tầm giữa (66,44), hạng ba sau ComParE (67,17) và InterSp12 (66,71). eGeMAPS ≥ GeMAPS ở mọi nơi, xác nhận phần mở rộng MFCC/spectral-flux quan trọng nhất cho valence (§4.4). Kết quả tốt nhất theo từng kho ngữ liệu (Bảng 3) cho thấy eGeMAPS thắng arousal nhị phân trên GEMEP và valence nhị phân trên SING; ở các tác vụ phân lớp đa lớp thô thì các bộ lớn ComParE/InterSp12 thắng, nhưng với các mục tiêu chiều arousal/valence thì các bộ tối giản cạnh tranh được.

**Kết luận chính (§4.4–5).** "Các bộ GeMAPS cho hiệu năng tương đương đáng kinh ngạc xét đến kích thước tối giản dưới 2% bộ lớn nhất (ComParE)." Tác giả lưu ý valence vẫn hưởng lợi từ các bộ lớn hơn (khoảng cách cần thu hẹp trong tương lai) và nhấn mạnh **tổng quát hóa liên kho ngữ liệu** — nơi các bộ nhỏ nên thắng nhất — là thí nghiệm tương lai then chốt. Bài kết bằng việc đặt các tham số nguồn-giọng/glottal (inverse filtering) làm phần mở rộng kế tiếp.

### Các phần trực tiếp hữu ích cho Pebble

1. **eGeMAPS (88 tham số) làm đường cơ sở đặc trưng âm học có thể diễn giải cho một head thoại.** Một vector chiều cố định, gọn, do chuyên gia tuyển chọn, trải F0, jitter, shimmer, HNR, loudness, formant F1–F3, alpha ratio, Hammarberg index, spectral slope, MFCC 1–4, spectral flux — chính bộ từ vựng "tone of voice / âm sắc", đủ nhỏ để huấn luyện một head trên dữ liệu khiêm tốn của Pebble mà không bị quá-khớp như bài cảnh báo với các bộ 6k. **D-D** (nguồn chuyển giao âm học + nền tảng diễn giải), **D-H** (điểm neo đặc trưng). *Tag: config openSMILE `eGeMAPSv02`; `pebble/audio/features.py` xuất một vector 88-float mỗi tin nhắn thoại.*
2. **GeMAPS-62 làm biến thể "tối đa diễn giải".** Khi tính diễn giải từng đặc trưng quan trọng hơn điểm valence cuối cùng (ví dụ giải thích *vì sao* một đoạn được đọc là arousal cao cho bác sĩ lâm sàng), bộ 62 tham số với functional trung-bình-cộng + hệ-số-biến-thiên là tập con dễ đọc. **D-D**, **D-G** (chính sách hiệu chỉnh/giải thích, phần lớn v2). *Tag: `GeMAPSv01b` làm config ablation/giải thích.*
3. **Sự bất đối xứng arousal/valence là một chỉ thị thiết kế.** eGeMAPS *tốt nhất lớp về arousal* (79,71 UAR) nhưng chỉ cạnh tranh về valence. Vì vậy chiều `energy` của Pebble (giống arousal) là mục tiêu âm học **được hỗ trợ tốt**; *valence* cảm xúc chỉ từ âm thanh yếu hơn và nên dựa vào head văn bản. **D-D** (chọn `energy`/arousal làm mục tiêu âm học chính), **D-B** (nếu gộp vào MTL, cân trọng số đóng góp của head âm học về phía các đầu ra kiểu arousal). *Tag: định tuyến đặc trưng âm học chủ yếu tới head `energy`, không phải valence của `emotion`.*
4. **Lý do bộ tối giản = lập luận quá-khớp / liên-kho-ngữ-liệu.** Tuyên bố thực nghiệm trung tâm của bài — các bộ nhỏ diễn giải tổng quát hóa nơi các bộ vét cạn 6k quá-khớp, đặc biệt liên kho ngữ liệu — trực tiếp hỗ trợ Pebble ưu tiên eGeMAPS hơn ComParE với dữ liệu nhỏ, lệch miền (người lớn→trẻ em). **D-D**, **D-H**. *Tag: mặc định eGeMAPS; ComParE-6373 chỉ là một dòng ablation cận trên.*
5. **Z-chuẩn-hóa theo người nói + cân bằng bằng up-sampling làm giao thức đánh giá.** Các con số chính dùng chuẩn hóa theo người nói (trung bình/phương sai theo từng người) và cân bằng lớp bằng up-sampling — trực tiếp chuyển giao sang chuẩn hóa theo từng trẻ và nhãn bạc mất cân bằng của Pebble. **D-D**, **D-C/D-B** (xử lý mất cân bằng). *Tag: chuẩn hóa đặc trưng theo từng trẻ + up-sample các bin severity thiểu số trong thí nghiệm head âm học.*
6. **Điểm neo giọng trẻ em FAU AIBO (§4.1.1).** Một trong sáu kho ngữ liệu là **trẻ em 10–13 tuổi** (51 trẻ, ~9,2 giờ, cảm xúc tiếng Đức tự phát Wizard-of-Oz), chính kho ngữ liệu đứng sau INTERSPEECH 2009 Emotion Challenge (bài 32). Đây là điểm dữ liệu giọng trẻ em *duy nhất* trong sự xác thực GeMAPS, và *valence* nhị phân là nhãn khả thi duy nhất. **D-H** (điểm neo hiệu chỉnh giọng trẻ em), **D-D**. *Tag: FAU AIBO làm tập hiệu chỉnh/kiểm tra giọng trẻ em ứng viên nếu có thể cấp phép.*

### Mỗi phần giúp Pebble thành công như thế nào

- **`energy` / `severity` âm học (D-D).** Chiều `energy` của Pebble (heuristic ở v1) và hồi quy `severity` về bản chất là âm học (arousal/cường độ). eGeMAPS cho vector đặc trưng có nguyên tắc, *có thể diễn giải* để học hoặc neo các đại lượng này, và Bảng 2 của bài chứng minh tập con đòn bẩy cao cho arousal đúng là các LLD prosody + chất lượng giọng (loudness, khoảng F0, jitter, shimmer, HNR). Hành động cụ thể (đường thoại v2): trích `eGeMAPSv02` mỗi tin nhắn, rồi hoặc (a) huấn luyện một head ridge/MLP nhỏ dự đoán `energy`/`severity` từ vector 88, báo cáo **Pearson r** (khớp quy ước D-D), hoặc (b) dùng functional loudness + khoảng-F0 + HNR làm proxy `energy` heuristic *có nền tảng tốt hơn* heuristic văn bản v1. Kết quả arousal-79,71 là bằng chứng việc này hiệu quả ở mức tin nhắn.
- **Chọn arousal thay vì valence cho head âm học (D-D / D-B).** Sự bất đối xứng 79,71 so với 66,44 cho Pebble biết chính xác nơi âm thanh đáng giá: dẫn `energy` (arousal) từ âm học; giữ valence của `emotion` neo vào văn bản NeoBERT. Điều này tránh tiêu tốn năng lực mô hình cho tín hiệu valence âm học yếu và là một quyết định định tuyến MTL rõ ràng.
- **Đường cơ sở diễn giải cho mạch chuyện luận văn.** eGeMAPS cho Pebble *gọi tên* "tone of voice" nghĩa là gì (danh sách LLD này) và báo cáo theo các đường cơ sở phổ quát ComParE/AVEC — cách duy nhất để chất lượng một head âm học được người phản biện đánh giá. Câu "dưới 2% kích thước ComParE, hiệu năng tương đương" là trích dẫn rằng một bộ nhỏ diễn giải là mặc định đúng.
- **Công thức tiền xử lý (D-H).** `pebble/audio/` = giải mã → tái lấy mẫu 16 kHz mono → openSMILE `eGeMAPSv02` (18+7 LLD → functional) → vector 88-float → z-chuẩn-hóa theo từng trẻ → cache. Lớp mỏng bọc `opensmile-python` (audEERING), không cần build C++. Cùng vector đó nạp vào một head âm học độc lập hoặc hợp nhất muộn với embedding CLS của NeoBERT.
- **Bảo hiểm liên-kho-ngữ-liệu / quá-khớp.** Vì dữ liệu âm học của Pebble sẽ nhỏ và lệch miền (chuẩn huấn luyện người lớn → giọng trẻ em), cảnh báo quá-khớp của bài là lý do tường minh để mặc định eGeMAPS-88 và coi ComParE-6373 chỉ là ablation. Đây là biện pháp phòng vệ một head âm học trông tốt trong mẫu rồi sụp đổ trên clip trẻ em thật.

### Lăng kính sức khỏe tâm thần trẻ em

- **Một điểm dữ liệu giọng trẻ em tồn tại, và nó mang tải.** FAU AIBO (§4.1.1) — trẻ 10–13, cảm xúc tự phát — nằm trong sự xác thực GeMAPS, nhưng **chỉ valence nhị phân khả thi** (5 lớp gốc không ánh xạ về arousal), và AIBO bị *loại khỏi* trung bình Bảng 2 chính. Vậy con số arousal mạnh của eGeMAPS được thiết lập trên kho ngữ liệu **người lớn**; bằng chứng giọng trẻ em của nó chỉ là valence và yếu hơn (Bảng 3: eGeMAPS 73,4 UAR trên valence AIBO). **Rủi ro chuyển giao:** *bộ từ vựng* đặc trưng chuyển giao sang trẻ em; *các con số hiệu năng và bất kỳ chuẩn đã học nào thì không*. Một mô hình jitter/shimmer/HNR/F0 khớp trên người lớn sẽ sai trên trẻ 7 tuổi.
- **Giọng trẻ em là một chế độ âm học khác.** F0 cao hơn và biến thiên hơn, đường thanh ngắn hơn (formant cao hơn), phát âm tự nhiên kém ổn định hơn (jitter/shimmer nền cao hơn), và thay đổi theo tuổi phát triển. Thang F0 bán cung và các LLD formant/chất lượng giọng của eGeMAPS được *định nghĩa* hợp lý cho trẻ em, nhưng *ngưỡng* cảm xúc của chúng được hiệu chỉnh theo người lớn. **Giảm thiểu:** không bao giờ tái dùng ngưỡng âm học người lớn; khớp lại/hiệu chỉnh lại bất kỳ head âm học nào trên giọng trẻ em; coi tuổi là một biến đồng; ưu tiên chuẩn hóa theo từng trẻ (mà giao thức của bài đã dùng) để hấp thụ độ lệch ở mức người nói.
- **Ưu tiên arousal cũng là câu chuyện an toàn hơn cho trẻ em.** Vì tín hiệu âm học Pebble có thể tin nhất là arousal/`energy`, và arousal *mơ hồ về valence* (trẻ hét vì vui và trẻ hét vì khủng hoảng đều là arousal cao), head âm học phải là **tư vấn, không bao giờ là tác nhân kích hoạt leo thang duy nhất** — hoàn toàn nhất quán với quyết định "không có head an toàn học được ở v1" của Pebble. Các tín hiệu giọng (HNR thấp, jitter cao, loudness tăng) có thể *nâng sự chú ý* (chỉ-leo-thang, kiểu FAIIR) nhưng một lộ trình bác sĩ/người giám hộ đưa ra quyết định.
- **Bảo mật qua giảm chiều đặc trưng.** Giọng trẻ em thô là sinh trắc (định danh qua dấu giọng). eGeMAPS giảm một clip về một **vector 88-float không khả nghịch**; Pebble nên trích ngay lúc nhận, lưu vector, và xóa dạng sóng — một chính sách tối giản dữ liệu cụ thể mà định nghĩa eGeMAPS mở, đầy đủ làm cho có thể kiểm toán.
- **Chế độ nhãn bạc mở rộng sang âm thanh.** Pebble không có nhãn arousal giọng trẻ em do người chú thích. Bất kỳ mục tiêu `energy`/`severity` âm học nào tự thân cũng là bạc (chuyển từ kho cường độ người lớn hoặc dẫn xuất từ văn bản). eGeMAPS sửa vấn đề *đặc trưng*, không sửa vấn đề *nhãn*; rủi ro chuyển giao nhãn D-C/D-D không đổi và có lẽ tệ hơn với âm thanh (hoàn toàn không tồn tại nhãn C-SSRS/WASSA giọng trẻ em).

### Hạn chế & câu hỏi mở cho Pebble

- **Mâu thuẫn / lỗ hổng so với kế hoạch turn-level của Pebble (functional vứt bỏ động lực học trong-tin-nhắn).** eGeMAPS thu gọn cả một phát ngôn về một vector tĩnh 88 qua functional (trung bình, CV, phân vị). Pebble chấm điểm ở **mức lượt / giữa hội thoại**. Một tin nhắn thoại là một lượt nên điều này khớp ở mức tin nhắn — nhưng nếu Pebble từng muốn *quỹ đạo trong tin nhắn* (khủng hoảng dâng lên qua clip 30 giây), tóm tắt functional vứt bỏ chính điều đó. Bộ này cố ý chứa gần như không có đặc trưng động (chỉ thống kê độ dốc lên/xuống và, trong eGeMAPS, spectral flux). **Giảm thiểu:** giữ *đường bao (contour)* LLD nếu động lực học trong-tin-nhắn quan trọng, hoặc cửa sổ hóa clip.
- **Mâu thuẫn so với cách diễn đạt của bài 29 và phần còn lại của tập (lệch phương thức + nhãn).** Bài 29 liệt eGeMAPS ở 88 tham số / "25 LLD" — bài này xác định chính xác là **18 LLD GeMAPS + 7 LLD mở rộng = 25**, và con số 88 đến từ việc mở rộng functional, không phải từ 88 LLD riêng biệt; phân rã chính xác (62 + 26) chỉ tồn tại ở đây. Quan trọng hơn, mọi bài văn bản trong tập (01 FAIIR, 12 MentalBERT, 14–16 C-SSRS, 18–19 WASSA) đều **chỉ-văn-bản**, và *không* nhãn nào của chúng (C-SSRS, GoEmotions, WASSA intensity) được căn chỉnh với âm thanh. Không có kho ngữ liệu giọng trẻ em đã công bố nào mang nhãn bạc của Pebble, nên head âm học không thể huấn luyện theo nhãn hiện có của Pebble mà không có bước phiên âm + căn chỉnh — một lỗ hổng thực sự, không phải chi tiết tích hợp.
- **Valence là trục yếu — liên quan trực tiếp tới `emotion`.** eGeMAPS tầm giữa về valence (66,44, sau ComParE 67,17). Head `emotion` của Pebble về cơ bản là tác vụ valence/phân loại. Kết luận của chính bài ("với valence cần xác định thêm các tham số quan trọng") là cảnh báo tường minh rằng **chỉ âm học sẽ không gánh được việc phân loại cảm xúc của Pebble** — văn bản phải là chính, âm thanh là bổ trợ.
- **Không có số liệu liên-kho-ngữ-liệu — thí nghiệm Pebble cần nhất lại thiếu.** Bài *lập luận* các bộ tối giản tổng quát hóa liên kho ngữ liệu nhưng hoãn thí nghiệm liên-kho-ngữ-liệu thực tế sang tương lai ("Trong các nghiên cứu tương lai cần khảo sát liệu các bộ tối giản đề xuất có đạt tổng quát hóa tốt hơn trong phân loại liên-cơ-sở-dữ-liệu hay không"). Sự dịch chuyển người-lớn→trẻ-em của Pebble đúng là một vấn đề liên-kho-ngữ-liệu, và bài này cung cấp động cơ nhưng **không có con số chuyển giao đo được**. Câu hỏi mở Pebble phải tự trả lời: `energy` huấn luyện bằng eGeMAPS có sống sót qua dịch chuyển miền người-lớn→trẻ-em không, và bao nhiêu?
- **Thời SVM, không phải học sâu.** Mọi con số là SVM-trên-functional. eGeMAPS làm đầu vào cho một head neural hiện đại (hoặc hợp nhất với NeoBERT) chưa được nghiên cứu ở đây; các mốc UAR là mốc SVM, không phải neural. Chúng giới hạn kỳ vọng nhưng không trực tiếp là kiến trúc của Pebble.
- **Câu hỏi mở — điểm neo hiệu chỉnh giọng trẻ em (D-D / D-H).** FAU AIBO là điểm neo giọng trẻ em hiển nhiên trong bài này, nhưng là tiếng Đức, 10–13 tuổi, Wizard-of-Oz, chỉ valence, và bị gate. Khe D-H chưa được lấp vẫn còn: tập giọng trẻ em nào, có đồng thuận, gắn tuổi, hiệu chỉnh head âm học? Không có nó, đường thoại vẫn heuristic như `energy` v1. Đáng xác nhận giấy phép FAU AIBO / GEMEP làm tập kiểm tra/hiệu chỉnh dù không phải nguồn huấn luyện.
