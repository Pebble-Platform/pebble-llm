# Bài báo 41 — Nhận diện Cảm xúc qua Giọng nói trong Sức khỏe Tâm thần: Tổng quan Hệ thống về các Ứng dụng Dựa trên Giọng nói

## 1. Thông tin thư mục

**Tiêu đề:** Speech Emotion Recognition in Mental Health: Systematic Review of Voice-Based Applications

**Tác giả:** Eric Jordan (ObTIC, Sorbonne Université, Paris), Raphaël Terrisse (Khoa Sức khỏe Tâm thần URCI, Bệnh viện Đại học Y khoa Brest; EA 7479 SPURBO, Université de Bretagne Occidentale), Valeria Lucarini (Université Paris Cité, IPNP / INSERM U1266; GHU-Paris Psychiatrie et Neurosciences, Hôpital Sainte-Anne), Motasem Alrahabi (ObTIC, Sorbonne), Marie-Odile Krebs (IPNP / GHU-Paris), Julien Desclés (Université Paris Cité), Christophe Lemey (tác giả liên hệ; URCI Brest; SPURBO; IMT Atlantique, Lab-STICC).

**Năm / nơi công bố:** *JMIR Mental Health* 2025; tập 12, e74260. DOI 10.2196/74260. Đăng ký PROSPERO CRD420251006669.

**Từ khóa (nguyên văn):** "affective computing; machine learning; mental health; psychology; psychiatry; speech emotion recognition; voice".

**Định khung cho Pebble:** Đây là **tài liệu tham chiếu phạm vi bằng chứng lâm sàng** cho giao điểm tin-nhắn-thoại × sức khỏe tâm thần của luận án Pebble. Đây KHÔNG phải bài báo phương pháp mà Pebble sao chép siêu tham số; đây là khảo sát hệ thống (a) xác lập rằng các đặc trưng cảm xúc giọng nói/âm học mang tín hiệu chẩn đoán thực sự cho trầm cảm, nguy cơ tự sát và loạn thần, (b) chỉ rõ đặc trưng âm học nào dự đoán bệnh lý nào, (c) lập bản đồ bối cảnh dữ liệu và mô hình hóa, và (d) liệt kê các khoảng trống còn mở (khan hiếm dữ liệu, tổng quát hóa, triển khai) — những điều định phạm vi và biện minh cho chương phương thức giọng nói của Pebble. Pebble v1 **chỉ dùng văn bản** (NeoBERT trên tin nhắn trẻ em đã phiên âm/gõ); bài báo này là cơ sở bằng chứng cho **mở rộng phương thức giọng nói trong tương lai** và để giới hạn một cách trung thực điều mà giọng nói có thể bổ sung.

## 2. Động lực vấn đề

Các tác giả định khung SER như một lĩnh vực đang trưởng thành (khởi nguồn từ xử lý tiếng nói thập niên 1990) nay giao thoa với tâm thần học, nơi "mối liên hệ giữa trạng thái cảm xúc của cá nhân và các chẩn đoán bệnh lý đặc biệt được quan tâm." Tiền đề lâm sàng: "Ngữ điệu, nhịp điệu, cao độ và các đặc trưng âm học khác của lời nói truyền tải những tín hiệu cảm xúc tinh tế, phản ánh tình trạng tâm lý của cá nhân," và phân tích tự động các tín hiệu này "mang lại nhiều lợi thế cho cải thiện chăm sóc bệnh nhân, phát hiện sớm các vấn đề sức khỏe tâm thần, và nâng cao trải nghiệm chăm sóc sức khỏe tổng thể." Các lợi thế được nêu của SER là tính **không xâm lấn, khách quan và phù hợp với giám sát tự động/theo chiều dọc** — một "cửa sổ không xâm lấn và khách quan vào trạng thái tâm thần của bệnh nhân."

Mục tiêu nêu của tổng quan: "khảo sát hiệu năng của các công cụ kết hợp SER và các phương pháp trí tuệ nhân tạo nhằm hướng tới việc sử dụng chúng trong bối cảnh lâm sàng, và xác định mức độ SER đã được ứng dụng trong bối cảnh lâm sàng đến đâu."

## 3. Vị trí trong tài liệu

Các tác giả đặt công trình tại điểm hội tụ của ba mạch. Thứ nhất, **lịch sử SER** — các mô hình cảm xúc phân loại (sáu cảm xúc lớn của Ekman: hạnh phúc, buồn, giận, sợ, ghê tởm, ngạc nhiên; "bánh xe cảm xúc" 8 cảm xúc nguyên thủy của Plutchik bổ sung tin tưởng và mong đợi cộng thêm chiều cường độ) so với **các mô hình chiều / liên tục** (mô hình circumplex 2 chiều valence–arousal của Russell). Họ lưu ý các mô hình phân loại chiếm ưu thế trong SER "vì chúng cung cấp các phạm trù được định nghĩa rõ ràng giúp thuận lợi cho gán nhãn và phân loại," trong khi các cách tiếp cận theo chiều "vẫn còn tương đối ít được khám phá." Thứ hai, **sự dịch chuyển trong phân loại bệnh học tâm thần từ phân loại sang chiều** — các phạm trù DSM/ICD so với Research Domain Criteria (RDoC) của NIMH và Hierarchical Taxonomy of Psychopathology (HiTOP), cả hai đều định khung các rối loạn như những phổ liên tục của rối loạn chức năng (hướng nội / hướng ngoại / rối loạn tư duy). Thứ ba, một **vận hành hóa phương pháp luận đặc thù của tổng quan này: phân biệt SER trực tiếp vs gián tiếp** — SER *trực tiếp* nhận diện cảm xúc một cách tường minh như một tác vụ (huấn luyện/tinh chỉnh trên dữ liệu gán nhãn cảm xúc, rồi liên hệ cảm xúc phát hiện được với bệnh lý); SER *gián tiếp* dùng các đặc trưng âm học liên quan cảm xúc (vd. các bộ đặc trưng openSMILE) trong bộ phân loại sức khỏe tâm thần mà không dùng bất kỳ nhãn cảm xúc nào.

Khoảng trống được nêu: "Theo hiểu biết tốt nhất của chúng tôi, đây là tổng quan hệ thống đầu tiên cung cấp cái nhìn tổng hợp về SER trong tâm thần học." Một tổng quan phạm vi đồng hành về cùng giao điểm (Frontiers in Psychology 2025, "Speech analysis and speech emotion recognition in mental disease: a scoping review") xuất hiện đồng thời, nhấn mạnh tính mới của chủ đề.

## 4. Phương pháp — tổng quan hệ thống PRISMA

**Quy trình.** Hướng dẫn PRISMA, đăng ký trước trong PROSPERO (CRD420251006669). Đánh giá nguy cơ thiên lệch bằng **QUADAS-2** (Quality Assessment of Diagnostic Accuracy Studies 2).

**Cơ sở dữ liệu & tìm kiếm.** PubMed, IEEE Xplore, arXiv và ScienceDirect, truy vấn "cho đến tháng 2 năm 2025." Chuỗi tìm kiếm (nguyên văn): `("emotion recognition" OR "affective computing" OR "emotional analysis") AND ("psychiatry" OR "psychology") AND ("speech" OR "voice")`. ✔ đã xác thực (PMC).

**Tiêu chí bao gồm (Textbox 1):** (1) phân tích tín hiệu **lời nói / âm thanh**; (2) một thành phần **nhận diện cảm xúc trực tiếp hoặc gián tiếp** (gián tiếp bao gồm sử dụng bộ đặc trưng openSMILE); (3) dữ liệu lời nói từ **bối cảnh lâm sàng**.

**Tiêu chí loại trừ:** âm thanh chỉ được phân tích kết hợp với phương thức khác (vd. văn bản); không có khía cạnh chẩn đoán/tiên lượng (cảm xúc được nghiên cứu cô lập không tương quan với kết cục bệnh nhân); bệnh lý là **thần kinh học thay vì sức khỏe tâm thần** (vd. Alzheimer); bài tổng quan không có thành phần thực nghiệm.

**Sàng lọc.** Hai tác giả áp dụng tiêu chí; bất đồng sẽ chuyển lên cả nhóm ("không gặp trường hợp nào như vậy"). Sàng lọc tiêu đề/tóm tắt, rồi đánh giá đầy đủ liệu thiết kế có bao gồm **đánh giá trực tiếp hiệu năng chẩn đoán** qua các chỉ số ML (F1, độ chính xác, AUC) hoặc tương quan thống kê.

**Luồng PRISMA (Hình 3).** **3648 nghiên cứu được sàng lọc → 85 (2.33%) báo cáo được truy xuất/đánh giá → 14 (20% của 85) được bao gồm.** ✔ đã xác thực (PMC). Lý do loại trừ phổ biến nhất ở bước cuối: "thiếu phân tích lời nói đơn thuần (vd. mô hình chỉ dùng văn bản hoặc kết hợp âm thanh với phương thức khác)" hoặc "thiếu góc nhìn chẩn đoán."

**Phân tách 14 nghiên cứu được bao gồm (Tóm tắt + Kết quả):**
- **Nguy cơ tự sát / ý tưởng tự sát (SI): 3/14 (21%)** ✔
- **Trầm cảm / rối loạn khí sắc: 8/14 (57%)** ✔
- **Rối loạn loạn thần: 3/14 (21%)** ✔
- ⚠ **Mâu thuẫn nội tại cần lưu ý:** Tóm tắt ghi 57% / 21% / 21%; đoạn kết quả PRISMA trong phần thân ghi lại cùng các số đếm là "3 (18%)… 8 (53%)… 3 (18%)" — các phần trăm này không cộng đủ và không khớp với tóm tắt. **Các số đếm (3 / 8 / 3 trên 14)** là con số có thẩm quyền; phần trăm trong thân là lỗi đánh máy. Trạng thái: số đếm ✔ đã xác thực; % trong thân ✖ (lỗi nội tại của bài báo).

**Nguy cơ thiên lệch QUADAS-2 (Hình 4).** "Hầu hết các nghiên cứu được bao gồm có nguy cơ thiên lệch thấp trên mọi lĩnh vực." Ngoại lệ chính: **lựa chọn bệnh nhân — 5 nghiên cứu nguy cơ cao** (3 chỉ lấy mẫu từ quần thể lâm sàng không có nhóm chứng; 2 thiếu mẫu đại diện). Lo ngại cao về tính áp dụng cho lựa chọn bệnh nhân trong 2 trường hợp; lo ngại không rõ ràng trong 4 nghiên cứu. ✔ đã xác thực (PMC). QUADAS-2 đầy đủ ở Multimedia Appendix 1.

## 5. Tổng quan tường thuật — phương pháp, đặc trưng, bộ dữ liệu

### 5a. Các họ đặc trưng âm học / ngôn điệu
- **Đặc trưng âm học** (thang mili-giây, tính chất vật lý của sóng âm): tần số/cao độ, cường độ, đặc tính phổ. **MFCC** "nắm bắt đặc tính phổ của lời nói (vd. năng lượng phân bố thế nào trên các tần số khác nhau)" — vd. năng lượng cao hơn ở tần số trung/cao cho giận dữ hoặc vui mừng.
- **Đặc trưng ngôn điệu** (thang thời gian dài hơn): **đường viền cao độ** (biến thiên tần số cơ bản F0 theo thời gian, phân biệt buồn với hứng khởi), **tốc độ nói**, **khoảng dừng (pause)**.
- **Formant** chịu ảnh hưởng của hình dạng/độ căng đường thanh quản (vd. mỉm cười dịch chuyển giá trị formant).
- **Phổ (spectral)**: MFCC, độ dốc phổ (spectral slope), formant, dòng phổ (spectral flux).

### 5b. Bộ công cụ openSMILE
"Một trong những công cụ phổ biến nhất để trích xuất đặc trưng âm học." Cung cấp các **bộ đặc trưng** chuẩn hóa — đáng chú ý là **eGeMAPS** (extended Geneva Minimalistic Acoustic Parameter Set), **emobase**, và **ComParE**. Điểm mạnh được nêu: dễ sử dụng và **chuẩn hóa** ("cho phép so sánh kết quả dễ dàng hơn") và **khả năng diễn giải** so với mô hình đầu-cuối (end-to-end).

### 5c. Các họ mô hình (theo thời gian)
- **ML truyền thống trên đặc trưng thủ công:** SVM, k-NN, cây quyết định, random forest, hồi quy logistic.
- **RNN:** LSTM và LSTM hai chiều (nắm bắt phụ thuộc thời gian).
- **CNN trên ảnh phổ (spectrogram)** (sau 2012).
- **Transformer / SSL:** "cách tiếp cận tiên tiến nhất," bao gồm các mô hình kiểu BERT và **wav2vec 2.0**; một mô hình lai 2D-CNN+LSTM tự-chú-ý (self-attention) trên MFCC được trích dẫn đạt "độ chính xác kiểm tra trung bình 90%." **CLAP** đa phương thức (contrastive language-audio pretraining) được nêu như kiến trúc tiền tuyến có khả năng 0-shot (nhưng các công trình đa phương thức bị loại khỏi 14 nghiên cứu).

### 5d. Bộ dữ liệu được khảo sát (SER tổng quát; **lưu ý: "rất ít đến không có bộ dữ liệu nào phục vụ cả SER lẫn ứng dụng sức khỏe tâm thần"**)
| Bộ dữ liệu | Loại | Kích thước / chi tiết | Liên quan |
|---|---|---|---|
| **DAIC-WOZ** | phỏng vấn lâm sàng bán cấu trúc (âm thanh+bản ghi) | 193 phỏng vấn, mỗi cuộc 5–20 phút, tiếng Anh Bắc Mỹ; bộ câu hỏi distress trầm cảm/lo âu/PTSD (PHQ-8) | bộ dữ liệu lâm sàng thực sự duy nhất; nhiều nghiên cứu trầm cảm dùng |
| **RAVDESS** | đa phương thức diễn xuất (âm thanh+mặt), nói+hát | 7365 bản ghi (4320 nói / 3036 hát), 24 diễn viên, 2 mức cường độ + trung tính | SER tổng quát, diễn xuất |
| **FAU-AIBO** | **lời nói tự phát của trẻ em Đức** tương tác với robot | gán nhãn mức từ cho **11 trạng thái cảm xúc** bởi 5 giám khảo; Thử thách INTERSPEECH 2009; "thách thức đáng kể… ngay cả với các phương pháp tiên tiến nhất" | corpus lời nói trẻ em duy nhất được nêu — liên quan trực tiếp đến ngữ vực trẻ em của Pebble |
| **IEMOCAP** | đa phương thức diễn xuất+ứng tác (âm thanh+motion capture) | ~12 giờ; cả nhãn phân loại lẫn nhãn chiều | benchmark SER tổng quát |
| **CaFE** | lời nói cảm xúc diễn xuất tiếng Pháp-Canada | 12 diễn viên, 6 cảm xúc Ekman + trung tính, ~69 phút | minh họa sự khan hiếm tài nguyên phi-tiếng-Anh |

Các tác giả nhấn mạnh **sự thống trị của tiếng Anh/tiếng Quan Thoại** và thành phần đơn-bối-cảnh-văn-hóa của các bộ dữ liệu này như một rủi ro tổng quát hóa.

## 6. Kết quả theo bệnh lý (bằng chứng then chốt)

### Nguy cơ tự sát / SI (3 nghiên cứu)
- **Gerczuk và cộng sự [19]** — phân loại nguy cơ tự sát theo giới tính với đặc trưng diễn giải được (âm học) + đặc trưng sâu; kết quả tốt nhất từ **wav2vec 2.0 tinh chỉnh theo cảm xúc**, **độ chính xác cân bằng 81%** (nguy cơ cao vs thấp), đạt được nhờ **huấn luyện riêng theo từng giới**. Hướng tác động khác nhau theo giới: kích động → ↑nguy cơ tự sát ở nam, ngược lại ở nữ. Đặc trưng phổ dự đoán: **độ dốc phổ (0–500 Hz), tỷ lệ alpha, băng thông F1.** ✔ đã xác thực (81% độ chính xác cân bằng, PMC).
- **Gideon và cộng sự [20]** — các cuộc gọi điện thoại tự nhiên, bệnh nhân vừa xuất viện; bộ phân loại SER trên đặc trưng âm học dùng nhãn cảm xúc tự báo cáo **PANAS**. **AUC tối đa 0.78** phân loại nhãn cảm xúc; **AUC 0.79** dùng **độ biến thiên cảm xúc** để tách SI vs nhóm khác. Phát hiện: nhóm SI có **độ biến thiên cảm xúc thấp hơn**. ✔ đã xác thực (các AUC, PMC). (Lưu ý: đây là pipeline gián tiếp *lời nói→cảm xúc→bệnh lý*.)
- **Belouali và cộng sự [3]** — cựu chiến binh Mỹ; đặc trưng âm học + ngôn điệu + ngôn ngữ, nhiều mô hình (random forest, hồi quy logistic, deep NN), lựa chọn đặc trưng. Tốt nhất (âm học + ngôn ngữ): **độ nhạy 0.86, độ đặc hiệu 0.70, AUC 0.80.** Giọng nói SI: **độ lệch chuẩn của đường viền năng lượng thấp hơn trong các đoạn có thanh, độ nhọn/độ lệch thấp hơn** → "giọng phẳng và ít sinh động hơn… đơn điệu hơn." ✔ đã xác thực (0.86 / 0.70 / 0.80, PMC).
- **Tín hiệu tự sát tổng thể:** "AUC khoảng 0.8 và độ chính xác khoảng 80%."

### Trầm cảm / rối loạn khí sắc (8 nghiên cứu — chiếm đa số)
- **Wang và cộng sự [6]** — DAIC-WOZ + PHQ-8; SVM/RF vs transformer; tốt nhất = transformer phức tạp, **độ chính xác 77%, F1 0.63** (transformer > ML truyền thống trên cùng dữ liệu).
- **Yang và cộng sự [46]** — trầm cảm lưỡng cực vs đơn cực vs chứng; hồ sơ cảm xúc từ SVM huấn luyện trên eNTERFACE, đưa vào LSTM+BiLSTM; **độ chính xác 3 lớp 77%.**
- **Yang và cộng sự [47]** (2013) — rối loạn trầm cảm chủ yếu trong 21 tuần; **thời lượng khoảng dừng chuyển lượt (switching pause) + F0**; khi mức độ trầm cảm ↓, **thời lượng khoảng dừng ngắn lại & ít biến thiên hơn**, giải thích **32% phương sai trong-đối-tượng** của điểm trầm cảm; bộ phân loại phân biệt tuyến tính **độ chính xác 69.5%** về mức độ nghiêm trọng.
- **Stepanov và cộng sự [48]** — AVEC 2017 / hồi quy PHQ-8 trên DAIC-WOZ; tốt nhất = **đặc trưng cấp thấp openSMILE → LSTM**; **đặc trưng phổ dự đoán tốt hơn ngôn điệu hay chất lượng giọng.**
- **Mao và cộng sự [49]** — đặc trưng ngôn điệu DAIC-WOZ (luồng thanh môn, chất lượng giọng, phổ); mô hình DL lai **độ chính xác 98.7%, F1 0.987** ("phân biệt gần như hoàn hảo… nhóm chứng và nhóm trầm cảm"). ✔ đã xác thực (98.7% / 0.987, PMC). ⚠ cao bất thường (xem §10).
- **Yang và cộng sự [50]** — transformer trên tham số tần số, DAIC-WOZ + dữ liệu riêng; **F1 0.78 (DAIC-WOZ) và 0.87 (dữ liệu riêng)**; **băng 600–700 Hz quan trọng nhất** (nguyên âm tiếng Quan Thoại /e/ hoặc /ɤ/) — đề xuất làm dấu ấn sinh học (biomarker) của trầm cảm.
- **Zhou và cộng sự [21]** — người cao tuổi có MCI (trầm cảm/lo âu/thờ ơ); **F2 và spectral flux liên quan âm với trầm cảm**; **MFCC 4 cao hơn liên quan dương** với trầm cảm.
- **Xu hướng (2013 → 2023):** độ chính xác tăng từ **69% (2 đặc trưng ngôn điệu, 2013) → 98% (đặc trưng ngôn điệu phong phú + DL, 2023)**.

### Rối loạn loạn thần (3 nghiên cứu)
- **Chakraborty và cộng sự [51]** — tâm thần phân liệt vs chứng qua **openSMILE emobase**; tốt nhất = **SVM tuyến tính + PCA, độ chính xác 79.49%** (so với 66.67% của baseline lớp đa số). Dự đoán mục triệu chứng âm tính NSA-16: **độ chính xác 62%–85%** (SVM/KNN/cây quyết định). ✔ đã xác thực (79.49%, PMC).
- **Çokal và cộng sự [18]** — tâm thần phân liệt ± rối loạn tư duy hình thức (FTD), người thân thế hệ một, nhóm chứng (15 mỗi nhóm, n=60); **phân tích khoảng dừng** (thời lượng, sự có mặt từ đệm, ngữ cảnh cú pháp). Tâm thần phân liệt không FTD → nhiều **khoảng dừng không có từ đệm (unfilled)**; FTD → **khoảng dừng đầu phát ngôn** dài hơn.
- **de Boer và cộng sự [53]** — **eGeMAPS + random forest**; **độ chính xác 86%** phổ tâm thần phân liệt vs chứng, **74%** bệnh nhân triệu chứng âm tính vs dương tính; lập luận cho "việc xác thực các đặc trưng ngôn ngữ như dấu ấn sinh học trong tâm thần học." ✔ đã xác thực (86%, PMC).
- **Khoảng trống đáng chú ý mà tác giả nêu:** "**không có công trình nào trong mẫu được khảo sát thực hiện phân tích trực tiếp cảm xúc trong bối cảnh rối loạn loạn thần**" — bằng chứng loạn thần hoàn toàn là SER *gián tiếp*.

### Tổng hợp dấu ấn sinh học (Overview of Biomarkers)
- **Ngôn điệu/thời gian:** cao độ (F0), năng lượng, mẫu hình khoảng dừng, tốc độ nói. Khoảng dừng ngắn hơn/ít biến thiên hơn ↔ mức độ trầm cảm tăng [47]; khoảng dừng đầu phát ngôn dài hơn ở FTD [18]; độ biến thiên năng lượng thấp / đường viền phẳng trong giọng nói tự sát [3].
- **Phổ:** MFCC, độ dốc phổ, formant, spectral flux; độ dốc phổ/tỷ lệ alpha/băng thông F1 → nguy cơ tự sát [19]; F2 + spectral flux (−) và MFCC 4 (+) → trầm cảm [21]; băng formant nguyên âm Quan Thoại → trầm cảm [50].
- **Tầm quan trọng theo mô hình:** số đoạn có thanh/giây, spectral flux, phân vị cao độ xếp hạng cao nhất cho tâm thần phân liệt/trầm cảm; phổ > ngôn điệu cho PHQ [48].
- **Chủ đề:** mô hình đặc trưng âm học được đề xuất như **giải pháp thay thế có thể diễn giải cho mô hình đầu-cuối** — một sự đánh đổi tường minh hiệu năng-vs-diễn giải.

## 7. Khoảng trống mở & định hướng tương lai theo tác giả

1. **Khan hiếm & không tương thích dữ liệu.** "Rất ít đến không có bộ dữ liệu nào phục vụ cả SER lẫn ứng dụng sức khỏe tâm thần." Bộ duy nhất thực sự lâm sàng (DAIC-WOZ) nhỏ (193 phỏng vấn). Hầu hết bộ dữ liệu SER là **diễn xuất** (RAVDESS, IEMOCAP, CaFE), không phải lời nói lâm sàng tự phát.
2. **Tổng quát hóa qua quần thể/văn hóa/ngôn ngữ.** Bộ dữ liệu chủ yếu là **tiếng Anh hoặc Quan Thoại, đơn-bối-cảnh-văn-hóa**; "biến thể trong mẫu hình lời nói, phương ngữ, và chuẩn mực văn hóa có thể ảnh hưởng… hiệu năng," đòi hỏi "các chiến lược xác thực và thích nghi vững chắc… qua các nhóm dân số khác nhau."
3. **Thiếu khả năng so sánh / không có thử thách chung.** "Sự đa dạng của phương pháp… dẫn đến khó khăn trong so sánh trực tiếp các nghiên cứu, ngay cả những nghiên cứu áp dụng cho cùng bệnh lý." Họ kêu gọi **thử thách chung** (cf. INTERSPEECH 2009, AVEC) để chuẩn hóa dữ liệu/đặc trưng/chỉ số — bị cản trở bởi "việc chia sẻ dữ liệu bảo mật."
4. **Đánh đổi diễn giải vs hiệu năng.** Mô hình phức tạp vượt mô hình đặc trưng âm học có thể diễn giải nhưng kháng diễn giải lâm sàng; "phải tìm một sự đánh đổi giữa hiệu năng phân loại và khả năng diễn giải."
5. **Triển khai / tích hợp luồng làm việc lâm sàng.** "Chuyển kết quả NLP vào thực hành lâm sàng thường quy… ngụ ý phân tích nhanh, lặp lại được, và có khả năng mở rộng, đặt ra những thách thức cụ thể," gồm sai sót ghi âm/phiên âm và tích hợp luồng EHR. "Công trình tương lai nên tập trung vào cách bác sĩ có thể sử dụng các công nghệ này một cách **hợp tác**."
6. **Hai pipeline được đề xuất.** **(A) Lời nói → Bệnh lý** (chiếm ưu thế trong tài liệu; ánh xạ trực tiếp). **(B) Lời nói → Cảm xúc → Bệnh lý** (hiếm; chỉ Gideon [20]) — các tác giả **ủng hộ (B)** vì nó "cung cấp diễn giải rõ ràng tại sao một phân loại được đưa ra" và hỗ trợ sử dụng lâm sàng hợp tác; rủi ro = lan truyền lỗi từ hệ SER, nên việc lựa chọn hệ SER là then chốt.
7. **Phân tích cảm xúc trực tiếp cho loạn thần** chưa được khám phá.
8. **Giám sát trong-đối-tượng / theo chiều dọc** (đánh giá tức thời sinh thái) là tiền tuyến được nêu, vượt trên chẩn đoán giữa-đối-tượng.

---

## Deep research — full-PDF read (2026-06-16)

> Đọc đối chiếu với **phiên bản công bố JMIR Mental Health** (mental.jmir.org/2025/1/e74260; DOI 10.2196/74260) và bản sao PMC (PMC12521853). PDF cục bộ là `pdfs/41-jordan-ser-mentalhealth-review.pdf` (bản render JMIR XSL-FO). Mọi con số then chốt bên dưới đều được đối chiếu chéo với HTML PMC. Phần này bổ sung phán đoán đặc thù-Pebble mà §§1–7 ở trên chưa có, và gắn mỗi phần chuyển giao được với ID Quyết định.

### Ghi chú truy cập nguồn

- **Đọc PDF:** `pdftotext "docs/papers/pdfs/41-jordan-ser-mentalhealth-review.pdf" -` → toàn bộ thân bài, chú thích cả 4 hình, hai pipeline đề xuất, danh mục tham khảo. Dấu phụ bị lỗi trong pdftotext (vd. "Çokal" → "�okal"; "eGeMAPS" còn nguyên) nhưng các con số sạch.
- **Xác thực web:** WebSearch `Jordan Terrisse Lucarini "Speech Emotion Recognition in Mental Health" JMIR systematic review` → tìm được trang JMIR và PMC12521853. WebFetch của PMC xác nhận: 14 nghiên cứu / phân tách 3/8/3 / 3648 sàng lọc → 85 truy xuất → 14 bao gồm / 5 nguy cơ cao lựa chọn bệnh nhân / và mọi chỉ số then chốt (Gerczuk 81% độ chính xác cân bằng; Belouali 0.86/0.70/0.80; Mao 98.7%/0.987; de Boer 86%; Chakraborty 79.49%). DOI 10.2196/74260, PROSPERO CRD420251006669 đã xác nhận.
- **Ghi chú xung đột:** Đây là phiên bản *đã công bố* tại nơi xuất bản, không phải preprint — không có chênh lệch preprint cần điều hòa. Bất đồng nội tại duy nhất (tóm tắt 57/21/21% vs thân 53/18/18%) là lỗi đánh máy của bài báo; các số đếm (3/8/3 trên 14) là chuẩn.
- **Nhãn trạng thái:** ✔ đã xác thực đối chiếu PMC; ≈ xấp xỉ / làm tròn; ✖ chưa xác thực hoặc lỗi nội tại bài báo.

### Bài báo thực sự làm gì

Một **tổng quan hệ thống PRISMA** (đăng ký PROSPERO, chấm thiên lệch QUADAS-2) về SER **chỉ-giọng-nói** áp dụng cho chẩn đoán/tiên lượng sức khỏe tâm thần. Từ **3648 sàng lọc → 85 truy xuất → 14 bao gồm** (✔). Phân tách: **trầm cảm/khí sắc 8/14 (57%)**, **tự sát/SI 3/14 (21%)**, **loạn thần 3/14 (21%)** (✔ số đếm; phần trăm trong thân là ✖ lỗi đánh máy nội tại). Đóng góp: (1) một **phân loại vận hành trực tiếp-vs-gián tiếp SER** (gián tiếp = đặc trưng openSMILE trong bộ phân loại không có nhãn cảm xúc; trực tiếp = nhận diện cảm xúc tường minh rồi liên hệ với bệnh lý); (2) một **bản đồ dấu ấn sinh học đặc trưng→bệnh lý** (năng lượng phẳng/giọng đơn điệu → tự sát; khoảng dừng rút ngắn + F0 → mức độ trầm cảm; khoảng dừng không-từ-đệm/đầu-phát-ngôn → tâm thần phân liệt±FTD; độ dốc phổ/tỷ lệ alpha → tự sát; F2/spectral-flux/MFCC4 → trầm cảm); (3) một **đề xuất hai pipeline** ủng hộ **Lời nói→Cảm xúc→Bệnh lý** thay vì **Lời nói→Bệnh lý** chiếm ưu thế, vì khả năng diễn giải. **Bao bì hiệu năng then chốt: AUC ≈ 0.8 và độ chính xác ≈ 70–80% cho phân biệt giữa-nhóm**, với ML cổ điển + đặc trưng thủ công (SVM/RF trên openSMILE/eGeMAPS) vẫn cạnh tranh với mô hình deep/SSL, và một ngoại lệ trầm cảm DAIC-WOZ ở 98.7%/0.987 (Mao [49], ✔ nhưng xem rủi ro bên dưới).

**Các con số then chốt đã xác thực:**
| # | Tuyên bố | Tham chiếu | Trạng thái | Dấu vết |
|---|---|---|---|---|
| 1 | 14 nghiên cứu; 8 trầm cảm / 3 tự sát / 3 loạn thần | Tóm tắt, Kết quả (PRISMA) | ✔ | PMC12521853 (WebFetch) |
| 2 | 3648 sàng lọc → 85 truy xuất → 14 bao gồm | Kết quả, Hình 3 | ✔ | PMC12521853 |
| 3 | Gerczuk wav2vec2 = 81% độ chính xác cân bằng, tách giới tính nguy cơ tự sát | Tự sát §[19] | ✔ | PMC12521853 |
| 4 | Belouali SI = độ nhạy 0.86 / độ đặc hiệu 0.70 / AUC 0.80 | Tự sát §[3] | ✔ | PMC12521853 |
| 5 | Mao DAIC-WOZ trầm cảm = 98.7% độ chính xác / 0.987 F1 | Trầm cảm §[49] | ✔ (giá trị) | PMC12521853 |
| 6 | de Boer eGeMAPS+RF tâm thần phân liệt = 86%; Chakraborty SVM 79.49% | Loạn thần §[53],[51] | ✔ | PMC12521853 |
| 7 | 5/14 nghiên cứu nguy cơ QUADAS-2 cao về lựa chọn bệnh nhân | Kết quả, Hình 4 | ✔ | PMC12521853 |

### Các phần hữu ích trực tiếp cho Pebble

1. **Thực đơn biểu diễn cảm xúc (phân loại Ekman/Plutchik vs chiều valence–arousal) định khung đối với bệnh học tâm thần theo chiều (RDoC/HiTOP).** → **D-C, D-D.** Tổng quan căn chỉnh tường minh **mô hình chiều valence–arousal** với tâm thần học mức-độ-như-phổ-liên-tục (RDoC, HiTOP các phổ hướng-nội/hướng-ngoại/rối-loạn-tư-duy). Đây là hậu thuẫn bên ngoài độc lập cho **đầu `severity` hồi quy** của Pebble (cường độ liên tục) và cho việc **định khung kiểu valence/arousal cho đầu `emotion`** thay vì nhãn phân loại cứng thuần túy. *Rủi ro chuyển giao:* ĐÚNG ở mức khái niệm (Pebble đã chọn đầu hồi quy severity); **ánh xạ 12-nhãn GoEmotions cụ thể** mà Pebble dùng mang tính phân loại, nên lập luận chiều hậu thuẫn đầu *severity* hơn là đầu *emotion*.
2. **Phát hiện đặc-trưng-thủ-công-thắng-mô-hình-sâu + đánh đổi diễn giải.** → **D-A, D-B.** Qua 14 nghiên cứu, **ML cổ điển trên đặc trưng openSMILE/eGeMAPS vẫn cạnh tranh** (de Boer RF 86%; Chakraborty SVM 79.49%; Stepanov LSTM trên openSMILE) và được đề xuất như **giải pháp thay thế có thể diễn giải cho mô hình đầu-cuối**. *Rủi ro chuyển giao:* MỘT PHẦN — đây là phát hiện về **âm thanh**; đầu vào của Pebble là **văn bản**, nơi bộ mã hóa transformer rõ ràng thống trị. Nhưng **đánh đổi diễn giải-vs-hiệu-năng** mà tổng quan đề cao chuyển giao trực tiếp sang D-A (NeoBERT vs backbone nặng hơn) và D-B (liệu cân bằng MTL phức tạp có đáng với độ mờ đục của nó cho một công cụ an toàn trẻ em phải kiểm toán được).
3. **Bản đồ dấu ấn sinh học đặc trưng→bệnh lý, đặc biệt năng-lượng-phẳng / giọng-đơn-điệu → tự sát và mẫu-hình-khoảng-dừng → mức độ trầm cảm.** → **D-D, D-G.** Belouali [3]: giọng tự sát có **độ lệch chuẩn đường viền năng lượng thấp hơn, độ nhọn/độ lệch thấp hơn** (phẳng, đơn điệu). Yang [47]: **rút ngắn khoảng dừng + giảm biến thiên theo dõi 32% phương sai mức-độ-trầm-cảm trong-đối-tượng.** *Rủi ro chuyển giao:* đây là các dấu ấn **âm học** và **không thể tính từ văn bản v1 của Pebble**. Chúng định phạm vi một **mở rộng giọng nói tương lai**, và là trích dẫn cho việc **`energy` là một cấu trúc thực** (hiện theo heuristic trong v1) — giọng nói sẽ biến `energy` thành tín hiệu học được, không phải phỏng đoán.
4. **DAIC-WOZ như mỏ neo lời-nói-lâm-sàng kinh điển + khoảng trống khan hiếm dữ liệu.** → **D-H.** DAIC-WOZ (193 phỏng vấn chấm điểm PHQ-8) là corpus thực sự lâm sàng duy nhất được tái sử dụng qua các nghiên cứu trầm cảm; phán quyết thẳng thắn của tổng quan là "**rất ít đến không có bộ dữ liệu nào phục vụ cả SER lẫn sức khỏe tâm thần**." *Rủi ro chuyển giao:* DAIC-WOZ là ngữ vực **người lớn, tiếng Anh, phỏng vấn lâm sàng** — không phải trò chuyện đồng hành trẻ em. Nó là **ứng viên mỏ neo hiệu chỉnh/chuyển giao** cho một đầu giọng nói tương lai, nhưng không phải vật thay thế ngữ vực trẻ em.
5. **Ủng hộ pipeline Lời nói→Cảm xúc→Bệnh lý.** → **D-G, D-A.** Các tác giả lập luận pipeline gián tiếp hai giai đoạn (nhận diện cảm xúc trước, rồi ánh xạ cảm xúc→nguy cơ) là ưu việt hơn về **khả năng diễn giải lâm sàng và sử dụng hợp tác**. *Rủi ro chuyển giao:* ĐÚNG — đây **chính xác là kiến trúc của Pebble**: một biểu diễn `emotion`/`severity` đưa vào Decision Engine hạ nguồn, thay vì bộ phân loại tin-nhắn→nguy-cơ hộp đen. Tổng quan là hậu thuẫn bằng-chứng-lâm-sàng bên ngoài cho lựa chọn thiết kế mô-đun của Pebble.
6. **FAU-AIBO: lời nói trẻ em tự phát khó ngay cả với SOTA.** → **D-H, D-C.** Corpus trẻ em duy nhất được nêu (trẻ em Đức, 11 trạng thái cảm xúc, 5 giám khảo) "đặt ra thách thức đáng kể trong đạt hiệu năng phân loại mạnh, ngay cả với phương pháp tiên tiến nhất." *Rủi ro chuyển giao:* ĐÚNG như một **cảnh báo**, liên quan trực tiếp đến ngữ vực trẻ em của Pebble — lời nói/văn bản cảm xúc trẻ em là yếu tố nhân-độ-khó đã được ghi nhận; các ngưỡng độ chính xác severity/emotion đặt trên dữ liệu người lớn (D-C: 52% acc / 0.75 wF1 / 47.8% macro-recall) có thể không chuyển giao xuống trẻ em.

### Mỗi phần giúp Pebble thành công thế nào

- **Đầu severity (D-C/D-D):** Trích dẫn lập luận chiều RDoC/HiTOP của tổng quan này để biện minh cho **đầu severity hồi quy** trong luận án, và dùng phát hiện **khoảng-dừng-→-mức-độ-trầm-cảm (32% phương sai) và giọng-đơn-điệu-→-tự-sát** làm động lực thực nghiệm rằng "cường độ/mức độ là có thật về mặt âm học" — tức là nếu/khi Pebble thêm giọng nói, severity có được một nền tảng đo-được-trực-tiếp. Cụ thể: trong chương giọng nói của luận án, định vị `severity` là đầu có khả năng hưởng lợi nhiều nhất từ đầu vào âm học.
- **Đầu `energy` (hiện theo heuristic, D-D):** Bài này là trích dẫn đơn lẻ mạnh nhất rằng **`energy` cuối cùng nên được học từ giọng nói**, không phải heuristic. Phát hiện độ-lệch-chuẩn-đường-viền-năng-lượng của Belouali cho một đặc trưng cụ thể (`std(energy_contour_voiced_segments)`) để trích từ pipeline âm thanh tương lai. Hành động: thêm ghi chú "mở rộng giọng nói v2" vào spec của `energy` trỏ tới các mô tả năng lượng eGeMAPS của openSMILE.
- **Backbone & cân bằng MTL (D-A/D-B):** Dùng định khung diễn-giải-vs-hiệu-năng của tổng quan để **bảo vệ NeoBERT-250M trước mô hình nặng hơn** và để **ưu tiên một sơ đồ cân bằng loss đơn giản, kiểm toán được** cho bối cảnh an toàn trẻ em. Luận điểm bằng-chứng-lâm-sàng — rằng người hành nghề coi trọng các mô hình đặc trưng thủ công có thể diễn giải — hậu thuẫn việc giữ stack của Pebble dễ đọc.
- **Kiến trúc pipeline (D-G/D-A):** Trích dẫn ủng hộ Lời-nói→Cảm-xúc→Bệnh-lý làm **xác thực bên ngoài cho thiết kế mô-đun emotion/severity → Decision Engine của Pebble** thay vì mô hình tin-nhắn→nguy-cơ đầu-cuối. Đây là luận điểm hướng-tới-người-phản-biện: một tổng quan JMIR được tôn trọng độc lập khuyến nghị chính xác sự phân tách mối quan tâm của Pebble vì khả năng diễn giải lâm sàng.
- **Bộ dữ liệu / mỏ neo (D-H):** Thêm **DAIC-WOZ** và **các bộ đặc trưng eGeMAPS/openSMILE** vào sổ đăng ký dữ liệu giọng-nói-tương-lai như mỏ neo lời-nói-lâm-sàng chuẩn-lĩnh-vực và bộ trích đặc trưng; thêm **FAU-AIBO** làm benchmark lời-nói-trẻ-em cảnh báo. **Không** coi bất kỳ cái nào là vật thay thế ngữ vực văn bản trẻ em cho v1.
- **Tính thực tế của bao bì hiệu năng (tất cả):** Dùng **AUC ≈ 0.8 / độ chính xác ≈ 70–80%** làm **trần giữa-nhóm** trung thực cho phân biệt sức khỏe tâm thần dựa-trên-giọng-nói trong luận án — và rõ ràng **chiết khấu ngoại lệ Mao 98.7%** (xem mâu thuẫn bên dưới) để Pebble không đặt kỳ vọng giọng nói phi thực tế.

### Lăng kính sức khỏe tâm thần trẻ em

- **Tính hợp lệ chuyển giao thấp cho v1, định phạm vi cho v2.** Mỗi một trong 14 nghiên cứu là **âm thanh**, và **tất cả trừ FAU-AIBO đều là người lớn** (cựu chiến binh, bệnh nhân MDD, bệnh nhân tâm thần phân liệt, người cao tuổi). Pebble v1 **chỉ-văn-bản, hướng-trẻ-em**. Vậy bài này chuyển giao như **bằng chứng và định phạm vi cho phương thức giọng nói tương lai**, KHÔNG phải phương pháp Pebble thực thi ngay. Nêu rõ điều này trong luận án: chương giọng nói được **biện minh và giới hạn** bởi tổng quan này, không phải triển khai từ nó.
- **Lời nói trẻ em khó-có-ghi-nhận.** FAU-AIBO (corpus trẻ em duy nhất) được nêu là kháng SOTA. Kết hợp với khoảng trống tổng quát hóa của tổng quan (tiếng Anh/Quan Thoại, đơn-văn-hóa, chủ yếu diễn xuất), đây là hậu thuẫn trực tiếp cho sự thận trọng của Pebble rằng **các ngưỡng độ chính xác bắt-nguồn-từ-người-lớn (D-C) sẽ không chuyển giao sạch sang trẻ em** và rằng một **lát hiệu chỉnh ngữ vực trẻ em là bắt buộc** trước mọi tuyên bố triển khai.
- **Khả năng diễn giải là yêu cầu an toàn trẻ em, không phải sở thích.** Đánh đổi hiệu-năng-vs-diễn-giải của tổng quan đè nặng hơn cho một công cụ hướng-trẻ-em: một hệ thống hướng-tới-bác-sĩ/người-giám-hộ nên ưu tiên phân rã **Lời-nói→Cảm-xúc→Bệnh-lý kiểm toán được** mà Pebble vốn đã dùng. Mô hình hộp đen 98.7% chính xác là thứ Pebble *không* nên là.
- **Đạo đức: chia sẻ dữ liệu bảo mật là rào cản của lĩnh vực.** Các tác giả nêu "chia sẻ dữ liệu bảo mật" là trở ngại chính cho thử thách chung. Với **giọng nói trẻ em** — sinh trắc học, định danh, và nhạy cảm về phát triển — điều này còn gắt hơn. Mở rộng giọng nói của Pebble phải lập kế hoạch cho xử lý trên-thiết-bị hoặc trong-hạ-tầng, đồng thuận của người giám hộ, và không phát hành, nhất quán với mẫu hình quản trị mà bài 01 (FAIIR) thiết lập cho văn bản trẻ em.
- **Không có bằng chứng an toàn/sàn-recall ở đây.** Tổng quan này báo cáo **các chỉ số phân biệt (AUC/độ chính xác)**, không bao giờ sàn recall hay hiệu chỉnh. Nó không thể thông tin cho chính sách an toàn recall ≥ 0.95 của Pebble (D-G); đó vẫn là câu hỏi v2 lấy nguồn ở nơi khác (C-SSRS/FAIIR).

### Hạn chế & câu hỏi mở cho Pebble

- **Mâu thuẫn #1 — ngoại lệ Mao 98.7% / 0.987 vs bao bì của lĩnh vực.** Tổng hợp của chính tổng quan nói "AUC ≈ 0.8, độ chính xác ≈ 70–80%," nhưng lại báo cáo Mao và cộng sự [49] ở **98.7% độ chính xác / 0.987 F1** trên trầm cảm DAIC-WOZ. Một 98.7% trên corpus 193 phỏng vấn với 5/14 nghiên cứu đã được đánh dấu nguy cơ cao về lựa chọn bệnh nhân gần như chắc chắn là **overfitting / đánh giá lạc quan mẫu nhỏ**, và tổng quan trình bày nó không phê phán bên cạnh các con số khiêm tốn hơn nhiều. **Với Pebble:** **không** trích 98.7% như trần giọng nói đạt được; trích bao bì **AUC 0.8 / độ chính xác 70–80%**. Đây là khoảng trống tường minh — tổng quan tổng hợp các nghiên cứu không-thể-so-sánh mà không hài hòa độ chặt chẽ đánh giá (vốn cũng là một trong các hạn chế nêu của nó: "khó khăn trong so sánh trực tiếp các nghiên cứu").
- **Mâu thuẫn #2 — ủng hộ cảm-xúc-theo-chiều vs đầu `emotion` phân loại của Pebble.** Tổng quan lập luận mô hình **valence–arousal theo chiều** là biểu diễn căn-chỉnh-lâm-sàng hơn và rằng mô hình phân loại chỉ "thuận lợi cho gán nhãn." Đầu `emotion` của Pebble là **phân loại (12-nhãn ánh xạ GoEmotions)**. Tổng quan hậu thuẫn đầu **severity** (theo chiều) của Pebble nhưng tạo căng thẳng với lựa chọn phân loại của đầu **emotion** — một khoảng trống cần xử lý trong luận án: biện minh các phạm trù GoEmotions trên cơ sở kỹ thuật/sẵn-có-nhãn trong khi thừa nhận sở thích theo chiều của tổng quan.
- **Khoảng trống phương thức vs toàn bộ v1 của Pebble.** Bài này **chỉ-âm-thanh theo tiêu chí bao gồm** (các nghiên cứu có-văn-bản bị *loại*). Pebble v1 **chỉ-văn-bản**. Hai cái bổ sung nhau, không chồng lấn — bài báo không thể xác thực bất kỳ lựa chọn bộ-mã-hóa-văn-bản nào; nó chỉ định phạm vi mở rộng giọng nói. Coi nó là **cơ sở bằng chứng chương giọng nói**, không phải baseline phương pháp.
- **Vắng mặt mức-lượt / giữa-cuộc-trò-chuyện.** Mỗi nghiên cứu là **chẩn đoán giữa-đối-tượng** hoặc mức-phiên (tổng quan nêu giám sát trong-đối-tượng/theo-chiều-dọc là hướng *tương lai*). Pebble chấm điểm **mức-lượt, giữa-cuộc-trò-chuyện**. Các chỉ số của tổng quan ở mức phiên/đối-tượng và **không phải ngưỡng so sánh được** cho Pebble — chỉ là bằng chứng định hướng rằng giọng nói mang tín hiệu cảm xúc/mức độ.
- **Ngữ vực trẻ em: khoảng trống Pebble có thể sở hữu.** Tổng quan ghi nhận rằng lời nói trẻ em (FAU-AIBO) khó và rằng lĩnh vực **gần như không có dữ liệu lời nói sức khỏe tâm thần trẻ em**. Một tài nguyên cảm-xúc-mức-độ giọng-nói/văn-bản ngữ-vực-trẻ-em và bất kỳ phân tích nào về cách trẻ em gián tiếp diễn đạt đau khổ sẽ là đóng góp thực sự mà tổng quan này cho thấy đang thiếu — phản chiếu cùng khoảng trống ngữ-vực-thanh-thiếu-niên mà bài 01 (FAIIR) để mở cho văn bản.
- **Câu hỏi mở đáng theo đuổi:** liệu các nhãn mức độ PHQ-8 và đặc trưng eGeMAPS của DAIC-WOZ có thể gieo mầm cho một **mỏ neo học-chuyển-giao** cho đầu `severity` giọng nói tương lai của Pebble — hứa hẹn cho người lớn, chưa được chứng minh cho trẻ em, và phụ thuộc vào độ khó lời-nói-trẻ-em đã được ghi nhận.
