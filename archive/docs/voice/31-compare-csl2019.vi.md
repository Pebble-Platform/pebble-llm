# Bài báo 31 — Tính toán Cảm xúc và Hành vi: Những Bài học Rút ra từ Cuộc thi Tính toán Ngôn ngữ Phụ (Paralinguistics) Đầu tiên

## 1. Thông tin thư mục

**Tiêu đề:** Affective and behavioural computing: Lessons learnt from the First Computational Paralinguistics Challenge

**Tác giả:** Björn Schuller (Imperial College London / University of Augsburg / Université de Genève), Felix Weninger (TU München / Nuance), Yue Zhang (Imperial / TUM), Fabien Ringeval (Université Grenoble Alpes, CNRS, LIG / audEERING), Anton Batliner (Augsburg / FAU Erlangen-Nürnberg), Stefan Steidl (FAU Erlangen-Nürnberg), Florian Eyben (audEERING), Erik Marchi (audEERING / TUM), Alessandro Vinciarelli (University of Glasgow), Klaus R. Scherer (Swiss Center for Affective Sciences), Mohamed Chetouani (Sorbonne / UPMC), Marcello Mortillaro (Swiss Center for Affective Sciences).

**Năm / nơi công bố:** *Computer Speech & Language*, 2019, tập 53, tr. 156–180. Nhận 10/12/2016; chỉnh sửa 1/10/2017; chấp nhận 19/2/2018; xuất bản 2019. DOI 10.1016/j.csl.2018.02.004. Bản truy cập mở: archive-ouverte.unige.ch/unige:110103 (PDF cục bộ chính là bản xuất bản UNIGE này). Đây là một bài tổng quan/phân tích tổng hợp (review/meta-analysis) hồi cố về Cuộc thi **INTERSPEECH 2013 ComParE** (bài báo gốc của cuộc thi là Schuller và cộng sự, Interspeech 2013).

**Từ khóa (nguyên văn):** "Computational Paralinguistics; Social Signals; Conflict; Emotion; Autism; Survey; Challenge".

## 2. Bài báo này là gì và tại sao quan trọng với Pebble

Đây là tài liệu tham khảo nền tảng cho **bộ đặc trưng âm thanh 6373 chiều của ComParE** — vector đặc trưng thủ công tiêu chuẩn đã thống trị nghiên cứu nhận diện cảm xúc qua giọng nói / ngôn ngữ phụ trong suốt một thập kỷ và vẫn là baseline mặc định (qua openSMILE) cho bất kỳ hệ thống "giọng nói → trạng thái cảm xúc/tâm trạng" nào. Bài báo tổng quan cuộc thi ComParE đầu tiên (Interspeech 2013), gồm bốn tiểu thử thách (sub-challenges) dưới một mái nhà chung, một bộ đặc trưng chung, một công thức bộ phân loại (SVM/SVR tuyến tính trong WEKA) và một độ đo đánh giá (unweighted average recall — UAR).

Đối với luận án Pebble, bài báo này là **danh mục các tín hiệu âm học/ngôn điệu (prosodic) phân biệt các trạng thái ngôn ngữ phụ** trong *kênh tin nhắn thoại (voice-message)* — kênh mà một ứng dụng đồng hành cho trẻ em sẽ nhận khi trẻ gửi ghi âm thay vì (hoặc cùng với) văn bản. Nó không nói về bộ phân loại văn bản NeoBERT của Pebble; nó nói về *pipeline âm học bổ trợ* và cho ta biết (a) đặc trưng âm học cấp thấp nào mang tín hiệu cảm xúc/lâm sàng nào, (b) bộ đặc trưng đầy đủ 6373 chiều mang lại lợi ích bao nhiêu so với một đặc trưng tốt nhất duy nhất, và (c) kỹ thuật bộ phân loại/hợp nhất (fusion) mang lại bao nhiêu so với bộ đặc trưng. Quan trọng, một trong bốn tiểu thử thách (Tự kỷ / CPSD) là trên **trẻ em 6–18 tuổi**, khiến đây là một trong số ít benchmark ngôn ngữ phụ có quần thể trẻ em.

## 3. Bốn tiểu thử thách, kho dữ liệu và nhiệm vụ

| Tiểu thử thách | Kho dữ liệu | Quy mô | Nhiệm vụ | Độ đo |
|---|---|---|---|---|
| **Tín hiệu Xã hội (Social Signals)** | SSPNet Vocalisation Corpus (SVC) | 2.763 clip × 11 s = 8,4 h; 120 người; 2.988 filler + 1.158 sự kiện cười | **Phát hiện + định vị** theo khung (frame) tiếng cười và filler (um/er/uh) | UAAUC (trung bình AUC của cười+filler, theo khung, 100 fps) |
| **Xung đột (Conflict)** | SSPNet Conflict Corpus (SC2) | 1.430 clip × 30 s = 11,9 h; 45 cuộc tranh luận chính trị Thụy Sĩ (tiếng Pháp); 110 người | **Hồi quy** (điểm xung đột ∈ [−10,+10]) + **nhị phân** cao/thấp | CC (Pearson) cho Score; UAR cho Class |
| **Cảm xúc (Emotion)** | Geneva Multimodal Emotion Portrayals (GEMEP) | 1.260 mẫu = 8,9 h; 10 diễn viên chuyên nghiệp; diễn xuất, câu vô nghĩa | **12 lớp** category; **nhị phân** arousal; **nhị phân** valence | UAR |
| **Tự kỷ (Autism)** | Child Pathological Speech Database (CPSD) | 2.542 mẫu = 1 h; **99 trẻ em 6–18 tuổi**; nhại câu theo gợi ý | **Nhị phân** Typicality (điển hình vs không điển hình); **4 lớp** Diagnosis (TYP/PDD/NOS/DYS) | UAR |

**Các lớp chẩn đoán CPSD (DSM-IV):** TYP = 64 trẻ phát triển điển hình; PDD = rối loạn phát triển lan tỏa / phổ tự kỷ (12 trẻ: 10 nam/2 nữ); NOS = PDD không xác định khác (10: 9 nam/1 nữ); DYS = suy giảm ngôn ngữ đặc hiệu / chứng khó nói (13: 10 nam/3 nữ). Tổng 35 trẻ phổ ASC vs 64 TYP. Phân chia độc lập theo người nói, phân tầng theo tuổi và giới tính (Bảng 5: TYP 566/543/542; tổng train/dev/test = 903/307/337). **Yếu tố gây nhiễu do điều kiện ghi âm được nêu rõ:** trẻ TYP và trẻ không điển hình được ghi âm ở các phòng khác nhau, nên đặc trưng phổ (spectral) một phần phản ánh *âm học phòng* chứ không phải bệnh lý (§3.4, §3.4.2; Bone et al. 2013) — liên quan trực tiếp đến bất kỳ triển khai giọng nói thực địa nào.

**Chi tiết GEMEP (Bảng 4):** 18 lớp cảm xúc, đánh giá giới hạn ở **12 lớp thường gặp nhất** (6 lớp hiếm ≤30 mẫu gộp vào "other"); không thể chia tách đồng thời độc lập-văn-bản và độc-lập-người-nói, nên nguyên âm + cụm #2 dùng cho train/dev và cụm #1 dùng cho test; **các mẫu điều tiết "masked" (che giấu cảm xúc) chỉ xuất hiện trong tập test** — một dịch chuyển phân phối train/test có chủ đích để kiểm tra độ bền vững.

## 4. Bộ đặc trưng ComParE 6373 chiều (lõi danh mục)

**Số chính:** 6.373 đặc trưng âm học ✔ (đã đối chiếu: bài Interspeech-2013 ComParE, isca-archive.org/interspeech_2013/schuller13_interspeech.pdf, "6,373 features"; truy vấn "ComParE 2013 6373 features 65 LLDs baseline UAR"). Tạo bằng cách áp dụng **functionals** thống kê lên **65 đặc trưng cấp thấp (LLDs)** ✔, trích bằng **openSMILE**. Bắt nguồn từ bộ IS12 Speaker Trait (khi đó 6.125 thuộc tính) với jitter/shimmer cải tiến, phát hiện đỉnh F0 tham lam (greedy), quy tắc functional đơn giản hóa.

**Các họ LLD (Bảng 6 — danh mục tín hiệu):**
- **4 liên quan năng lượng** (ngôn điệu): tổng phổ thính giác (độ to/loudness), tổng phổ thính giác lọc RASTA, năng lượng RMS, tỷ lệ qua-không (ZCR).
- **55 phổ (spectral)** (phổ + cepstral): các dải phổ thính giác RASTA 1–26 (0–8 kHz), **MFCC 1–14**, năng lượng phổ 250–650 Hz & 1k–4 kHz, spectral roll-off (.25/.50/.75/.90), spectral flux/centroid/entropy/slope/harmonicity, độ sắc tâm-âm học (psychoacoustic sharpness), spectral variance/skewness/kurtosis.
- **6 liên quan phát âm hữu thanh (voicing)** (ngôn điệu + chất giọng): **F0** (SHS + làm mượt Viterbi), xác suất hữu thanh, **log-HNR (tỷ lệ hài-trên-nhiễu)**, **jitter** (local, delta), **shimmer** (local).

**Số học functional (§3.3):** Nhóm A = 4 năng lượng + 55 phổ = 59 LLD; 54 functionals trên LLD + 46 trên ΔLLD → 59 × (54+46) = 5.900. Nhóm B = 6 LLD voicing; 39 functionals trên LLD + 39 trên Δ → 6 × (39+39) = 468. Cộng 5 thống kê thời gian đoạn hữu thanh (mean/SD/min/max độ dài đoạn + tỷ lệ F0 khác không). **Tổng 5.900 + 468 + 5 = 6.373** ✔ (Bảng 6/7, §3.3; tái lập được từ số học trong PDF).

**Biến thể theo khung (định vị Social Signals):** bộ nhỏ hơn theo khung — MFCC 1–12 + log-energy + Δ + ΔΔ, cộng voicing-prob/HNR/F0/ZCR + Δ, mỗi cái được bổ sung mean & SD trên cửa sổ 9-khung (±4) → **47 × 3 = 141 mô tả/khung** (được hầu hết người dự thi Social-Signals dùng dưới tên "ComParE (141)").

## 5. Kết quả baseline (SVM/SVR, các con số tiêu đề)

Tất cả baseline: SVM tuyến tính với hậu nghiệm logistic Platt-scaled; SMO; tham số phức tạp C tinh chỉnh trên dev ∈ {1e-3,1e-2,1e-1,1}; đa lớp qua cặp 1-vs-1; SVR cho hồi quy Conflict; **tăng mẫu (upsampling)** cho Autism (PDD/NOS/DYS ×5 cho Diagnosis, ×2 cho Typicality), **giảm mẫu (downsampling)** xuống 5% khung garbage cho Social Signals; WEKA; "công thức" tái lập được gửi cho người dự thi. **Test = train+dev huấn luyện lại.** (Bảng 8.)

| Nhiệm vụ | Độ đo | Dev | **Test** | Ngẫu nhiên | Trạng thái |
|---|---|---|---|---|---|
| Social Signals — AUC Cười | AUC | 89,0 | 83,6 | 50,0±0,18 | ✔ |
| Social Signals — AUC Filler | AUC | 87,6 | 83,3 | 50,0±0,21 | ✔ |
| **Social Signals — UAAUC (chính thức)** | UAAUC | 86,2 | **82,9 → 83,3** | 50,0±0,13 | ✔ |
| **Conflict — Score** | CC | 81,6 | **82,6** | −10,8±2,3 | ✔ |
| **Conflict — Class (chính thức)** | UAR | 79,1 | **80,8** | 50,0 | ✔ |
| Emotion — Arousal | UAR | 82,4 | 77,9 | 50,0 | ✔ |
| Emotion — Valence | UAR | 75,0 | 61,6 | 50,0 | ✔ |
| **Emotion — Category (chính thức, 12 lớp)** | UAR | 40,1 | **40,9** | 8,33 | ✔ |
| **Autism — Typicality** | UAR | 92,8 | **90,7** | 50,0 | ✔ |
| **Autism — Diagnosis (chính thức, 4 lớp)** | UAR | 52,4 | **67,1** | 25,0 | ✔ |

> Lưu ý về UAAUC: thân Bảng 8 hiển thị 82,9 (test) nhưng phần tóm tắt/§3.4 và bản Interspeech-2013 xuất bản ghi **83,3% UAAUC**; chênh lệch nhỏ là giữa baseline tinh chỉnh-trên-dev và baseline huấn luyện-lại cuối cùng. ✔ đã đối chiếu với các baseline gốc của cuộc thi (WebSearch: "ComParE 2013 baseline 83.3 UAAUC 80.8 conflict 40.9 emotion 67.1 autism"; researchgate/bản tin SLTC xác nhận 83,3 / 80,8 / 40,9 / 67,1).

**Các mẫu hình tiêu đề:**
- **Arousal ≫ valence từ âm học** — arousal 77,9 vs valence 61,6 UAR; một bất đối xứng nổi tiếng, được khẳng định lặp lại: *năng lượng/cao độ mã hóa arousal một cách bền vững; valence hầu như không nghe được từ âm học đơn thuần*.
- **Cảm xúc diễn xuất 12 lớp rất khó ngay cả trong điều kiện lý tưởng** — 40,9 UAR (ngẫu nhiên 8,33); chỉ sadness có recall rõ >50%, amusement 50,7%; pride 14,7% và elation 15,3% kém nhất; các nhầm lẫn rải khắp các lớp, không theo chiều arousal/valence (Bảng 12). Trên dữ liệu tự phát thực tế còn giảm thêm.
- **Autism Typicality trông tốt nhưng bị nhiễu** — 90,7 UAR, nhưng một phần do âm học phòng; loại bỏ đặc trưng phổ *làm tăng* Typicality lên 91,8 và loại bỏ đặc trưng tĩnh (chỉ giữ Δ) cho 89,2 (Bảng 9) — tức đặc trưng chất-giọng/cao-độ/độ-to **bền vững với kênh hơn** đặc trưng phổ.

## 6. Phân tích tổng hợp hồi quy logistic đơn biến (ablation đơn-tín-hiệu)

Đóng góp đặc biệt của bài báo là baseline hồi quy logistic **đơn-đặc-trưng-tốt-nhất** (Bảng 10), trả lời "MỘT tín hiệu âm học đưa ta đi được bao xa, và là tín hiệu nào?" Đây chính là danh mục tín hiệu mà Pebble cần.

| Nhiệm vụ | Đặc trưng đơn tốt nhất | Hướng | Test (đơn) | Test (SVM 6373 đầy đủ) | Trạng thái |
|---|---|---|---|---|---|
| Conflict — Class | **Mean of positive log-HNR** (HNR thấp → xung đột cao; giọng nén/gắt) | thấp→xung đột | 76,2 UAR | 80,8 | ✔ |
| Conflict — Score | Mean HNR (đảo dấu) | — | CC 64,6 | 82,6 | ✔ |
| Emotion — Arousal | **Q3 của spectral roll-off 25%** (nhiều năng lượng tần-số-cao → arousal cao; liên quan F0, bền theo phân vị) | cao→arousal | 71,0 UAR | 77,9 | ✔ |
| Emotion — Valence | Skewness của MFCC 1 (khó diễn giải) | — | 57,2 UAR | 61,6 | ✔ |
| Emotion — Category | pairwise coupling | — | 29,9 UAR | 40,9 | ✔ |
| Autism — Typicality | **Flatness của RMS energy** (flatness thấp = đường năng lượng "nhọn" = khó điều tiết lời nói) | thấp→không điển hình | 82,2 UAR | 90,7 | ✔ |
| Autism — DYS vs NOS | IQR 1–3 của ZCR (thấp với NOS) | — | 70,4 UAR | — | ✔ |
| Autism — NOS vs PDD | Khoảng cách trung bình đỉnh thay-đổi-độ-to (cao hơn với PDD) | cao→PDD | 66,3 UAR | — | ✔ |
| Autism — {DYS,NOS,PDD} vs TYP | Flatness của RMS energy | — | 76,6–89,8 UAR | — | ✔ |
| Autism — Diagnosis (4 lớp) | pairwise coupling của các cái trên | — | 49,0 UAR | 67,1 | ✔ |

**Khoảng cách đơn-tín-hiệu → bộ-đầy-đủ là bài học về độ phong phú đặc trưng:** một *đặc trưng ngôn điệu đơn được chọn tốt* đạt 76–82% UAR trên nhị phân conflict/typicality, nhưng bộ 6373 chiều đầy đủ thêm ~4–9 điểm nữa (Conflict 76,2→80,8; Typicality 82,2→90,7) và là thiết yếu cho Diagnosis 4 lớp tinh tế (49,0→67,1). Các tác giả dự đoán đường cong từ-tốt-nhất-đến-n-tốt-nhất "khá phẳng" và rằng SVM bền vững trên toàn vector dư thừa sẽ không có "cú nhảy thực sự" từ chọn lọc đặc trưng — tức **ném cả bộ đặc trưng vào một bộ phân loại bền vững thay vì chọn thủ công.**

## 7. Lợi ích bộ-đặc-trưng vs bộ-phân-loại (người dự thi + fusion)

65 nhóm đăng ký, 19 bài được chấp nhận. Tốt nhất mỗi tiểu thử thách trên test (Bảng 11):
- **Social Signals:** Gupta et al. **91,5 UAAUC** (DNN + làm mượt/che chuỗi thời gian xác suất trên ComParE-141) — **+6,1 tuyệt đối so với baseline 83,3** — cú nhảy lớn nhất, từ một phương pháp *phân đoạn/làm mượt* (kiểu ASR), không phải đặc trưng mới. Bỏ phiếu đa số 2-tốt-nhất 92,7.
- **Conflict:** Grézes et al. **83,1 UAR** bằng cách quy xung đột về một đặc trưng cấp-trung *tỷ-lệ-chồng-lấn-lời-nói* (SVR+SVM). Bỏ phiếu 3-tốt-nhất 85,9.
- **Emotion:** AdaBoost (Gosztolya) 42,3; ensemble ~41–42; fusion 12-hệ-thống tốt nhất **46,1** UAR. Lợi ích khiêm tốn — nhiệm vụ khó về âm học.
- **Autism:** Asgari et al. **69,4 UAR** (SVM trên chất-giọng/năng-lượng/phổ/cepstral + mô hình hài của lời nói hữu thanh) — chỉ nhỉnh trên baseline 67,1; fusion không vượt được.

**Bài học:** ở nơi nhiệm vụ là **phát hiện/phân đoạn** (Social Signals) hoặc **khai thác được về cấu trúc** (Conflict = chồng lấn), kỹ thuật phương pháp/đặc trưng vượt đáng kể bộ đặc trưng tổng quát. Ở nơi nhiệm vụ là **phân loại cảm xúc nội tại** (Emotion category, Autism diagnosis), cả bộ 6373 lẫn bộ phân loại tinh vi đều không nhúc nhích nhiều — trần nằm ở *tín hiệu*, không phải ở mô hình. **Ngưỡng ý nghĩa thống kê** (Hình 4, §3.5.5): để vượt baseline ở α=.05 cần +4,4 tuyệt đối (Conflict), +5,5 (Emotion), +3,8 (Autism) — hiệu chỉnh câu hỏi "lợi ích này có thật không?".

## 8. Các phần hữu ích trực tiếp cho Pebble (gắn theo Decision ID)

> Các decision ID (D-A…D-H) thuộc register *bộ phân loại văn bản* của Pebble. Đây là bài báo **kênh giọng nói**; phần chuyển giao chủ yếu vào *pipeline âm học tin-nhắn-thoại* (tương lai) chạy *song song* với NeoBERT, cộng vài tương tự phía văn bản. Mỗi điểm nêu rõ rủi ro chuyển giao.

1. **Danh mục tín hiệu 65-LLD + bộ openSMILE 6373 như front-end giọng nói có sẵn** → di chuyển **D-H (datasets / thay thế)** cho kênh giọng nói. Hiện vật cụ thể: `voice/features.py` gọi openSMILE với cấu hình `ComParE_2016` để xuất vector 6373 cho mỗi ghi-âm. *Rủi ro chuyển giao: TRUNG BÌNH.* Danh mục đúng-kênh (nó CHÍNH LÀ kênh giọng nói) và một kho dữ liệu là trẻ em, nhưng mọi con số ở đây trên giọng diễn xuất/người lớn hoặc trẻ em ghi âm lâm sàng; ghi-âm điện thoại của trẻ ngoài thực tế ồn hơn và tự phát. Dùng bộ đặc trưng, không dùng con số tuyệt đối, làm điểm khởi đầu.

2. **Arousal-từ-âm-học bền vững (77,9 UAR), valence thì không (61,6)** → định hướng **D-D (nguồn & độ đo hồi quy severity/energy)** và head `energy` heuristic. Hiện vật: `energy` v1 của Pebble là heuristic; nếu có ghi-âm tới, suy ra proxy arousal từ **Q3 spectral roll-off + loudness + F0** (tín hiệu arousal tốt nhất của bài báo) thay vì cố đọc valence âm học — để valence/emotion cho head văn bản. *Rủi ro chuyển giao: THẤP cho arousal-như-energy* (bất đối xứng này là một trong những phát hiện được tái lập nhiều nhất trong affect-from-speech); CAO nếu ai đó cố đọc cảm xúc tinh tế chỉ từ âm học.

3. **Tín hiệu ngôn điệu đơn tốt nhất đạt 76–82% UAR trên trạng thái nhị phân; bộ đầy đủ thêm ~4–9 điểm** → định hướng **D-D** và **D-B (cân bằng loss / đánh đổi độ phong phú đặc trưng)**. Hiện vật: một `voice/cue_rules.py` rẻ, kiểm-toán-được gồm các tripwire đơn-đặc-trưng (HNR thấp → căng thẳng/xung đột; flatness RMS-energy nhọn → lời nói rối loạn điều tiết; khoảng cách đỉnh-độ-to cao → không điển hình) làm *lớp đầu tiên* diễn giải được dưới bất kỳ head giọng nói học được nào — mẫu hình "luật-ngu-nhưng-kiểm-toán-được trước" kiểu FAIIR, ở đây có cơ sở từ UAR đơn-tín-hiệu đo được. *Rủi ro chuyển giao: TRUNG BÌNH* — hướng (HNR thấp↔căng thẳng) có cơ sở sinh lý và có khả năng đúng, nhưng các ngưỡng quyết định 0,5 được khớp trên các kho dữ liệu cụ thể này và phải tinh chỉnh lại.

4. **UAR (unweighted average recall) làm độ đo dưới mất cân bằng lớp + tăng mẫu lớp hiếm ×5** → di chuyển **D-C (sơ đồ nhãn severity + loss)** và **D-B**. Hiện vật: báo cáo **UAR / macro-recall** (không phải accuracy) trên head `emotion` (12 nhãn) và `severity` mất cân bằng của Pebble, và tái lập công thức tăng-mẫu-thiểu-số ComParE (×5 PDD/NOS/DYS) làm baseline đối chiếu với Kendall/GradNorm/focal. Bài báo chọn UAR rõ ràng "vì nó cũng có ý nghĩa với phân phối mất cân bằng cao" và thấy tăng-mẫu ×5 đơn giản ≈ SMOTE cho các nhiệm vụ của họ. *Rủi ro chuyển giao: THẤP* — lựa chọn độ đo và tăng-mẫu-thiểu-số chuyển giao sạch sang bất kỳ bộ phân loại mất cân bằng nào kể cả văn bản.

5. **Chọn đặc trưng bền-với-kênh: bỏ phổ, giữ chất-giọng/cao-độ/độ-to** (Typicality 90,7→91,8 khi bỏ phổ; Bảng 9) → định hướng **D-H** và một mỏ neo hiệu chuẩn kênh giọng nói. Hiện vật: với bất kỳ triển khai giọng-trẻ-em thực địa nào, ưu tiên đặc trưng **ngôn điệu/chất giọng** (jitter/shimmer/HNR/F0/loudness, bền với vọng âm) hơn đặc trưng phổ/MFCC thô vốn phản ánh môi trường ghi âm. *Rủi ro chuyển giao: THẤP-TRUNG BÌNH* — bài học nhiễu-phòng là tổng quát; mức tăng +1,1 cụ thể là đặc thù kho dữ liệu.

6. **Thiết kế dịch-chuyển-phân-phối train/test (cảm xúc masked / phòng chưa thấy chỉ ở test)** → định hướng **D-G (chính sách ngưỡng / hiệu chuẩn)** và xây dựng tập đánh giá. Hiện vật: xây tập test giọng nói/severity giữ-riêng của Pebble để *cố ý bao gồm* các điều kiện khó nhất, ngoài-train (affect bị che/gián tiếp, điều kiện ghi âm chưa thấy) để các con số báo cáo không lạc quan. *Rủi ro chuyển giao: THẤP* — đây là mẫu hình phương pháp luận, không phụ thuộc kênh.

## 9. Mỗi phần giúp Pebble thành công thế nào (hành động cụ thể)

- **Front-end giọng nói (điểm 1) → `voice/features.py`.** Khi Pebble nhận một ghi-âm, chạy openSMILE ComParE ra vector 6373, tùy chọn chiếu sang bộ 141-khung cho bất kỳ định vị nào (vd phát hiện cười/filler như tín hiệu gắn kết/`receptivity`). Đây là công thức đã công bố, tái lập được; đừng phát minh lại đặc trưng âm học.
- **Proxy arousal (điểm 2) → head `energy`.** Thay/bổ sung `energy` v1 heuristic bằng một bộ hồi quy arousal 3-đặc-trưng (roll-off Q3, loudness, F0). Hiệu chuẩn tương quan Pearson làm độ đo (khớp quy ước CC của bài báo và D-D của Pebble). **Không** cố đọc valence âm học; định tuyến valence/emotion sang NeoBERT văn bản.
- **Tripwire tín hiệu (điểm 3) → `voice/cue_rules.py`.** Triển khai các luật đơn-đặc-trưng làm lớp đệm an toàn/phân loại diễn giải được (HNR thấp → cờ căng thẳng; năng lượng nhọn → cờ rối loạn điều tiết), mỗi cái có chiều-hiệu-ứng tài liệu hóa từ Bảng 10, nằm dưới head học được — bác sĩ đọc được, ưu tiên recall.
- **Độ đo + mất cân bằng (điểm 4) → cấu hình huấn luyện.** Đặt UAR/macro-recall làm độ đo báo cáo chính cho `emotion`/`severity`; thêm tăng-mẫu-thiểu-số ×5 làm nhánh baseline D-B; bài báo là trích dẫn cho "tăng-mẫu đơn giản ≈ SMOTE".
- **Bền với kênh (điểm 5) → lát hiệu chuẩn.** Gắn nhãn đặc trưng theo độ bền; khi ghi-âm trẻ thay đổi theo thiết bị/phòng, dựa vào đặc trưng ngôn điệu và báo cáo lát phân tầng theo kênh.
- **Thiết kế test khó (điểm 6) → chia tập đánh giá.** Tuyển tập test giọng nói/severity của Pebble để đại diện quá mức cho distress bị che/gián tiếp và điều kiện chưa thấy, phản chiếu thiết kế masked-chỉ-ở-test của GEMEP.

## 10. Lăng kính sức khỏe tâm thần trẻ em — tính hợp lệ chuyển giao, rủi ro, đạo đức

- **Benchmark giọng-trẻ-em hiếm, nhưng lâm sàng không phải ứng-dụng-đồng-hành.** CPSD là **99 trẻ em 6–18 tuổi**, nhại câu theo gợi ý, ghi âm trong bệnh viện/trường học — đúng kênh-trẻ-em (một tài sản thực sự; gần như không benchmark ngôn ngữ phụ nào khác có trẻ em), nhưng đó là giọng *lâm sàng, có gợi ý, chẩn đoán*, không phải tự bộc lộ tự phát với ứng dụng đồng hành. Nhiệm vụ Typicality/Diagnosis là phân loại ASC/suy giảm ngôn ngữ, **không phải** phát hiện distress hay trạng thái sức khỏe tâm thần. Nên các *tín hiệu* (HNR↔căng thẳng, flatness-RMS↔rối loạn điều tiết, khoảng-cách-đỉnh-độ-to↔không điển hình) chuyển giao như một danh mục giả thuyết; các *nhãn nhiệm vụ* không ánh xạ vào mục tiêu emotion/severity/safety của Pebble.
- **Arousal-có / valence-không là bài học giọng-trẻ-em then chốt.** Ghi-âm của trẻ tin cậy báo hiệu *kích hoạt* (kích động, năng lượng) nhưng không báo *tốt-vs-xấu*. Pebble do đó phải coi giọng nói là kênh **arousal/energy và gắn kết**, giữ phán đoán ngữ nghĩa/valence ở văn bản — một phân tách sạch tránh đọc-quá tông giọng của trẻ.
- **Nhiễu điều kiện ghi âm là bẫy hợp-lệ-và-đạo-đức.** Chính phát hiện của bài báo — rằng phân loại "không điển hình" một phần do *phòng* nào ghi trẻ — là cảnh báo gắt: mô hình giọng nói có thể học *âm học thiết bị/nhà* của trẻ làm proxy cho *trạng thái* hay *nhân khẩu*. Với sản phẩm cho trẻ đây vừa là rủi ro công bằng (điện thoại chất lượng kém → thiên lệch hệ thống) vừa rủi ro riêng tư. Giảm thiểu: ưu tiên đặc trưng ngôn điệu bền-với-kênh, báo cáo hiệu năng phân tầng theo thiết bị, không bao giờ để mô hình giọng phổ thô quyết định an toàn.
- **Affect âm học khó ngay cả trong điều kiện lab lý tưởng** — 40,9 UAR trên cảm xúc *diễn xuất* 12 lớp. Tác giả nhấn mạnh hiệu năng "suy giảm đáng kể" trên dữ liệu tự phát thực tế. Với Pebble điều này giới hạn kỳ vọng: âm học giọng nói là tín hiệu *yếu, bổ trợ* cho cảm xúc tinh tế ở trẻ, không phải bộ phân loại chính. Kiến trúc an toàn không bao giờ được phụ thuộc nhận diện cảm xúc âm học.
- **Đạo đức của giọng nói trong sản phẩm cho trẻ.** Giọng nói là sinh trắc và định danh. Kho dữ liệu lâm sàng của bài báo có đồng thuận và gần-IRB (khoa tâm thần trẻ em đại học); ứng dụng đồng hành thu ghi-âm trẻ cần đồng thuận giám hộ rõ ràng, trích đặc trưng trên-thiết-bị hoặc tạm thời (lưu vector 6373, không lưu audio), và tùy chọn tắt giọng nói hoàn toàn.

## 11. Hạn chế & câu hỏi mở cho Pebble (kèm mâu thuẫn/khoảng trống)

- **Diễn xuất, không tự phát; có gợi ý, không tự do.** GEMEP là diễn viên chuyên nghiệp; CPSD là nhại câu. Trẻ của Pebble nói tự phát, ngắn, cảm xúc, qua mic điện thoại. Mọi con số ở đây là *cận trên trong điều kiện sạch/kiểm soát*; chính bài báo nói dữ liệu tự phát tệ hơn. Bộ 6373 và hướng tín hiệu chuyển giao; các UAR thì không.
- **Không có mô hình giọng nói deep-learning đầu-cuối.** Đây là thế giới SVM-trên-đặc-trưng-thủ-công thời 2013. Voice-affect hiện đại sẽ dùng embedding wav2vec2/HuBERT. Pebble nên coi ComParE-6373 là *baseline rẻ, diễn giải được* và đối chiếu một bộ mã hóa audio tự-giám-sát với nó — bài báo cung cấp baseline, không phải state-of-the-art.
- **Mâu thuẫn/khoảng trống so với kế hoạch Pebble và so với FAIIR (Bài 01):** Pebble v1 suy ra **`energy`, `socialIsolation`, `receptivity`, `safetyFlag` heuristic và chỉ huấn luyện `emotion` + `severity` từ văn bản** — tức v1 **không có kênh giọng nói nào cả**. Bài báo này là bằng chứng rằng *thứ học được nhất từ giọng nói* chính là **arousal/energy** (77,9 UAR, bền, đơn-tín-hiệu 71,0), chiều mà Pebble hiện để heuristic. Vậy có một căng thẳng cụ thể: tín hiệu Pebble đoán heuristic (`energy`) lại là tín hiệu mà một head openSMILE+logistic rẻ có thể đo trực tiếp từ ghi-âm với độ tin cậy đã công bố. Ngược lại, FAIIR (Bài 01) và toàn bộ register bộ-phân-loại-văn-bản giả định đầu vào **chỉ-văn-bản, cấp-cuộc-trò-chuyện/lượt** và không bao giờ chạm kênh giọng nói — bài báo này nhắc rằng ứng dụng cho trẻ nhận *audio*, một kênh mà pipeline văn bản về cấu trúc không thể thấy, và rằng nhiễu điều-kiện-ghi-âm (rò rỉ phòng→nhãn) là chế độ lỗi mà bộ phân loại văn bản không bao giờ gặp nhưng head giọng nói phải phòng vệ.
- **Không-nghe-được valence là trần cứng, không phải vấn đề tinh chỉnh.** Nếu reviewer Pebble hỏi "sao không đọc cảm xúc từ giọng nói?", bài báo này (61,6 valence UAR, giảm thêm trên dữ liệu tự phát) là trích dẫn rằng valence âm học cơ bản là yếu — câu trả lời là kiến trúc (văn bản cho valence, giọng nói cho arousal), không phải "huấn luyện chăm hơn".
- **Câu hỏi mở đáng theo đuổi:** danh mục tín hiệu HNR↔căng thẳng / flatness-RMS↔rối loạn điều tiết có giữ trên *ghi-âm tự phát của trẻ* không? Không bài báo nào trong bộ của Pebble kiểm tra điều này. Một thử nghiệm nhỏ giọng-trẻ-em tính các tín hiệu đơn này đối chiếu nhãn distress suy từ văn bản sẽ là một đóng góp thực sự, công bố được, và sẽ trực tiếp giảm rủi ro cho một head giọng nói v2.

## Deep research — full-PDF read (2026-06-16)

### Ghi chú truy cập nguồn

Đọc toàn văn từ bản xuất bản cục bộ `docs/papers/pdfs/31-compare-csl2019.pdf` (bản UNIGE archive-ouverte của bài *Computer Speech & Language* 2019, DOI 10.1016/j.csl.2018.02.004), trích bằng `pdftotext` (công cụ Read không render được PDF). Mọi bảng (1–13) và mục (§1–§5) đã được đọc. Các con số chịu tải được đối chiếu với bài cuộc thi gốc **Interspeech-2013 ComParE** và các tóm tắt thứ cấp:
- **Số đặc trưng 6373 / 65 LLD / 141 đặc-trưng-khung** — WebFetch `isca-archive.org/interspeech_2013/schuller13_interspeech.pdf` ("6,373 features", "65 low-level descriptors") ✔; cũng tái lập được từ số học §3.3 trong PDF cục bộ (5.900 + 468 + 5).
- **Baseline 83,3 UAAUC / 80,8 Conflict UAR / 40,9 Emotion UAR / 67,1 Autism Diagnosis UAR** — WebSearch "ComParE 2013 6373 features baseline UAR social signals conflict emotion autism Schuller"; được đối chiếu bởi Bản tin SLTC tháng 11/2013 và các bản ResearchGate của cả bài cuộc thi 2013 lẫn bài tổng quan 2019 này ✔.
- Ghi chú bài-cuộc-thi-vs-tổng-quan: baseline sơ bộ Interspeech-2013 gốc báo một Conflict-Class UAR hơi khác (≈0,565 trong một bảng đầu) so với **80,8% cuối cùng** trong Bảng 8 của bản tổng quan CSL 2019 này; bản tổng quan xuất bản (có thẩm quyền) dùng baseline train+dev huấn luyện-lại nêu trên.

### Bài báo thực sự làm gì

Tổng quan/phân tích tổng hợp Interspeech-2013 ComParE: định nghĩa bốn tiểu thử thách (Social Signals/SVC, Conflict/SC2, Emotion/GEMEP, Autism/CPSD; §3.1, Bảng 2–5), giới thiệu **bộ đặc trưng âm học ComParE 6373 chiều** (65 LLD × functionals; §3.3, Bảng 6–7), tính **baseline SVM/SVR tuyến tính** (Bảng 8: UAAUC 83,3 / Conflict UAR 80,8 & CC 82,6 / Emotion arousal 77,9, valence 61,6, category 40,9 / Autism typicality 90,7, diagnosis 67,1), thêm **phân tích hồi quy logistic đơn-đặc-trưng** xác định tín hiệu đơn tốt nhất mỗi nhiệm vụ (Bảng 10: HNR cho conflict, spectral roll-off Q3 cho arousal, flatness RMS-energy cho typicality), và tổng quan **65 nhóm đăng ký / 19 bài chấp nhận** (Bảng 11; lợi ích tốt nhất: Social Signals 91,5 UAAUC qua DNN+làm-mượt = +6,1; Conflict 83,1 qua tỷ-lệ-chồng-lấn; Emotion fusion 46,1; Autism 69,4). Bài định lượng lợi ích bộ-đặc-trưng vs đơn-tín-hiệu vs bộ-phân-loại/fusion và độ bền-với-kênh của đặc trưng ngôn điệu vs phổ (Bảng 9).

### Các phần hữu ích trực tiếp cho Pebble

Xem §8 ở trên (sáu điểm, mỗi điểm gắn D-x kèm rủi ro chuyển giao). Tóm tắt: (1) danh mục tín hiệu openSMILE 6373 làm front-end giọng nói [D-H]; (2) bất đối xứng arousal-bền/valence-yếu cho head `energy` [D-D]; (3) tripwire đơn-tín-hiệu (HNR/flatness-RMS/đỉnh-độ-to) làm lớp đầu kiểm-toán-được [D-D, D-B]; (4) độ đo UAR + tăng-mẫu-thiểu-số ×5 dưới mất cân bằng [D-C, D-B]; (5) chọn đặc trưng ngôn-điệu-hơn-phổ bền-với-kênh [D-H]; (6) thiết kế test dịch-chuyển-phân-phối khó [D-G].

### Mỗi phần giúp Pebble thành công thế nào

Xem §9 ở trên — hành động cụ thể theo từng hiện vật: `voice/features.py` (openSMILE), bộ hồi quy arousal `energy` (roll-off Q3 + loudness + F0, độ đo Pearson), `voice/cue_rules.py` tripwire diễn giải được, nhánh huấn luyện UAR + tăng-mẫu, lát hiệu chuẩn phân tầng theo kênh, chia tập đánh giá masked/điều-kiện-chưa-thấy.

### Lăng kính sức khỏe tâm thần trẻ em

Xem §10. Điểm chính: CPSD cho một benchmark giọng-trẻ-em hiếm (99 trẻ, 6–18) nhưng là phân loại ASC lâm sàng/có gợi ý, không phải distress ứng-dụng-đồng-hành; bài học chuyển giao chịu tải là **arousal-có / valence-không** (giọng → energy/arousal, văn bản → valence/emotion); **nhiễu điều kiện ghi âm** (rò rỉ phòng→nhãn) là bẫy công-bằng+riêng-tư cho sản phẩm trẻ em; affect âm học yếu ngay trong lab lý tưởng (40,9 UAR diễn xuất, tệ hơn khi tự phát), nên giọng nói phải là kênh bổ trợ, không bao giờ quyết định an toàn; giọng nói là sinh trắc → đồng thuận giám hộ, lưu đặc trưng không lưu audio, cho phép tắt.

### Hạn chế & câu hỏi mở cho Pebble

Xem §11. **Mâu thuẫn/khoảng trống** rõ ràng: Pebble v1 để `energy` heuristic và **không có kênh giọng nói**, nhưng bài báo này cho thấy arousal/energy chính là thứ rẻ nhất, tin cậy nhất học được từ ghi-âm (77,9 UAR; đơn-tín-hiệu 71,0) — chiều Pebble đang đoán lại là chiều openSMILE có thể đo. Và so với FAIIR/register bộ-phân-loại-văn-bản (chỉ-văn-bản, cấp-lượt): ứng dụng cho trẻ nhận *audio*, một kênh pipeline NeoBERT về cấu trúc không thể thấy, mang chế độ lỗi đặc thù (nhiễu phòng→nhãn) mà văn bản không bao giờ gặp. Valence âm học (61,6 UAR, giảm thêm) là trần cứng, biện minh cho phân tách kiến trúc thay vì "huấn luyện chăm hơn". Câu hỏi mở: các tín hiệu HNR/flatness-RMS có giữ trên ghi-âm tự phát của trẻ không — chưa bài nào trong bộ kiểm tra, và là thử nghiệm giảm-rủi-ro v2 sạch.
