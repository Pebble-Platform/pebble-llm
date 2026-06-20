# Bài báo 28 — Khảo sát về Học Biểu diễn Sâu cho Nhận dạng Cảm xúc Giọng nói (Survey of Deep Representation Learning for Speech Emotion Recognition)

## 1. Thông tin thư mục

**Tiêu đề:** Survey of Deep Representation Learning for Speech Emotion Recognition

**Tác giả:** Siddique Latif (University of Southern Queensland / Distributed Sensing Systems Group, Data61–CSIRO), Rajib Rana (USQ), Sara Khalifa (Data61–CSIRO / UNSW / University of Queensland), Raja Jurdak (Trusted Networks Lab, Queensland University of Technology), Junaid Qadir (Qatar University / Information Technology University Lahore), Björn W. Schuller (GLAM — Imperial College London / University of Augsburg). Liên hệ: siddique.latif@usq.edu.au.

**Năm / nơi công bố:** *IEEE Transactions on Affective Computing* (T-AFFC), tập 14, số 2, trang 1634–1654, năm 2023. DOI 10.1109/TAFFC.2021.3114365. Bản PDF cục bộ là phiên bản bản thảo đã được chấp nhận (accepted-manuscript) (QUT ePrints 213410, giấy phép CC BY-NC 4.0); bản camera-ready được chấp nhận năm 2021 và xếp vào số phát hành năm 2023.

**Từ khóa (nguyên văn):** "Speech emotion recognition, multi task learning, representation learning, domain adaptation, unsupervised learning".

**Loại:** Khảo sát / tổng quan toàn cảnh (survey / landscape review). Các tác giả định vị đây là "khảo sát toàn diện đầu tiên về chủ đề học biểu diễn sâu cho SER," khác với các khảo sát SER trước đó vốn hoặc tập trung vào đặc trưng thủ công (hand-engineered features) hoặc bao quát học biểu diễn một cách chung chung mà không tập trung vào SER (Bảng 1, so sánh với Bengio et al. 2013, Zhong et al. 2016, Basu et al. 2017, Swain et al. 2018, Akçay et al. 2020).

## 2. Vì sao bài này dành cho Pebble

Luận án Pebble bao gồm (hoặc sẽ bao gồm) một **chương về phương thức giọng nói / nhận dạng cảm xúc giọng nói (SER)** song song với bộ mã hóa văn bản (text encoder). Khảo sát này là *tài liệu định vị/toàn cảnh tham chiếu* cho chương đó: nó cung cấp phân loại các kiểu đặc trưng, các họ kiến trúc (CNN / RNN / CNN-RNN / attention / mô hình sinh / SSL), các bộ dữ liệu tiếng Anh kinh điển cùng lược đồ nhãn của chúng, các thước đo đánh giá chuẩn (UA/UAR, CCC), và các thách thức mở của lĩnh vực — tất cả trong một nguồn trích dẫn từ một nơi công bố hàng đầu với Schuller (nhân vật trung tâm của lĩnh vực, người sáng lập chuỗi thử thách Interspeech ComParE) là tác giả chính (senior author).

Hai lưu ý đóng khung cho mọi nội dung bên dưới:
- **Niên đại.** Được chấp nhận năm 2021. Nó có trước thời đại SSL-trên-âm-thanh-thô (raw-audio) hiện đang thống trị SER (tinh chỉnh wav2vec 2.0 / HuBERT / WavLM). SSL chỉ xuất hiện như một tiểu mục ngắn hướng tới tương lai (§3.4.3), được đánh dấu là "cần được khám phá trong SER." Đối với các con số SSL-SER hiện tại, chương của Pebble phải dựa vào các bài báo mới hơn (ví dụ #24 MMER, #27 Morais SSL-SER, #40 wav2vec2-depression) — khảo sát này là *bản đồ lãnh thổ trước thời SSL*, không phải hiện trạng SSL.
- **Phạm vi.** Đây là khảo sát về *học biểu diễn*, không phải bảng xếp hạng kiến trúc. Các con số SOTA nằm rải rác trong Bảng 5 như các điểm minh họa, không phải các giá trị tốt nhất được tuyển chọn; chúng không trực tiếp so sánh được giữa các dòng (khác nhau về split, đặc trưng, giao thức fold).

## 3. Phân loại các kiểu đặc trưng (§2.1, §5.1)

Khảo sát đóng khung toàn bộ lĩnh vực như một sự dịch chuyển **từ kỹ thuật đặc trưng (feature engineering) sang học biểu diễn (representation learning)**:

- **Đặc trưng âm học thủ công** (mô hình cũ):
  - **MFCC** — "tập đặc trưng chính cho SER và các tác vụ phân tích giọng nói khác" trong nhiều thập kỷ. Bốn bước: FFT → chiếu công suất lên thang Mel → log → DCT. Bước cuối (DCT) "làm mất thông tin và phá hủy quan hệ không gian," nên thường được bỏ qua, "kết quả là **phổ LogMel**" — đặc trưng phổ biến nhất duy nhất để huấn luyện mạng DL trong giọng nói.
  - **Các tập tối giản chuẩn hóa:** **GeMAPS / eGeMAPS** (Eyben, Schuller et al.) — được thiết kế để (a) chỉ thị các thay đổi sinh lý cảm xúc trong việc tạo giọng nói và (b) trích xuất tự động được; được dùng rộng rãi như benchmark.
  - **Các tập đặc trưng thử thách:** **IS09–IS13** (các tập đặc trưng ComParE/paralinguistics Interspeech 2009–2013) và **LLDs** (low-level descriptors, mô tả mức thấp) xuất hiện xuyên suốt Bảng 5 như các đầu vào chuẩn.
  - Các nhóm được nêu tên: **đặc trưng phổ (spectral), đặc trưng ngôn điệu (prosodic), đặc trưng chất lượng giọng (voice-quality)** (Hình 1).
- **Giọng nói thô (raw speech)** làm đầu vào trực tiếp cho mô hình sâu — đang nổi lên; "đòi hỏi lượng dữ liệu khổng lồ để đạt hiệu năng cạnh tranh," được giảm nhẹ bằng tăng cường dữ liệu (data augmentation). Các lớp CNN đầu hoạt động như một "filterbank dựa trên dữ liệu."
- **Biểu diễn học được** — trọng tâm của khảo sát: các đặc trưng phân cấp, trừu tượng, học tự động, "ít tốn thời gian hơn … đòi hỏi tối thiểu kiến thức miền của con người," với khả năng tổng quát hóa tốt hơn và không cần thiết kế lại đặc trưng cho từng tác vụ (Bảng 2).

**Kết luận then chốt của lĩnh vực (§5.1):** các nghiên cứu gần đây cho thấy "các kỹ thuật học biểu diễn sâu có thể trích xuất biểu diễn phân biệt được và việc lựa chọn đặc trưng đầu vào cụ thể không quan trọng bằng kiến trúc mô hình." LogMel/spectrogram vẫn phổ biến vì chúng "cần ít xử lý hơn, ít mẫu dữ liệu hơn, và ít huấn luyện hơn để đạt hiệu năng phân loại hàng đầu so với các thiết lập dùng âm thanh thô" (Bảng 5 cho thấy đặc trưng thủ công vẫn phổ biến hơn giọng nói thô làm đầu vào).

## 4. Phân loại kiến trúc (§2.3, §5.2)

Phân loại mô hình DL (đặc điểm theo Bảng 3):

- **DNN (kết nối đầy đủ):** học phân cấp các biểu diễn phân tán; các lớp cao hơn cho tính bất biến với thay đổi cục bộ của đầu vào. Ứng dụng SER sớm: biểu diễn cấp phát ngôn từ posterior cấp đoạn của DNN + bộ phân loại ELM (Han et al.), báo cáo **cải thiện 20%** trên IEMOCAP so với baseline thủ công.
- **CNN:** chuyên cho dữ liệu dạng lưới (spectrogram = 2D, waveform = 1D). Các biến thể **ResNet** và **DenseNet** "đặc biệt phổ biến trong SER." Bộ lọc CNN "nắm bắt cảm xúc liên quan đến tần số cơ bản"; bền vững với điều kiện nhiễu.
- **RNN (LSTM / GRU / BLSTM):** mô hình hóa ngữ cảnh thời gian; cơ chế cổng (gating) giải quyết vanishing gradient; BLSTM mô hình hóa cả quá khứ + tương lai. BLSTM của Lee et al. báo cáo **cải thiện 12%** so với DNN-ELM. Mô hình RNN-CTC cũng hỗ trợ.
- **CNN-RNN (CNN-LSTM / CNN-GRU):** công thức có giám sát chủ đạo — CNN trích xuất đặc trưng, LSTM/GRU cho phụ thuộc dài hạn; được chứng minh "là lựa chọn tốt hơn so với dùng CNN hoặc LSTM riêng lẻ."
- **CapsNet:** cấu trúc capsule tuần tự cho biểu diễn cấp phát ngôn; vượt baseline CNN-LSTM trên IEMOCAP.
- **Attention:** self-attention, local attention, multi-hop attention — "giúp mạng tập trung vào các thành phần nổi bật về cảm xúc (affect-salient)."
- **Autoencoder:** AE, **sparse AE** (có thể học biểu diễn lớn hơn đầu vào; "đơn giản để huấn luyện và học biểu diễn tốt hơn so với DAE và RBM"), **DAE** (khử nhiễu — bền với giọng nói nhiễu), **AAE** (adversarial AE).
- **Mô hình sinh (generative):** **DBN/RBM** (sớm), **VAE** (biểu diễn cảm xúc tách rời — disentangled), **GAN** (sinh dữ liệu tổng hợp; "vấn đề hội tụ" là khó khăn tái diễn).
- **Transformer:** được xem là *hướng tương lai* (§5.2) — "Cảm xúc trong giọng nói cũng phụ thuộc ngữ cảnh. Do đó, Transformer cần được khám phá trong SER." Đây là khung nhìn lỗi thời: tới năm 2023 transformer (và transformer SSL) đã thống trị.

## 5. Phân loại các mô hình học (§3) — xương sống của khảo sát

Các nghiên cứu được nhóm thành năm nhóm theo *cách* biểu diễn được học (Bảng 5 tóm tắt mọi nghiên cứu theo Corpus / Đầu vào / Mô hình / Hiệu năng):

1. **Học biểu diễn có giám sát (§3.1):** học từ các mẫu có nhãn. Hiệu năng tốt nhất nhưng "bị giới hạn bởi yêu cầu về nhãn … việc tạo và gán nhãn các bộ dữ liệu này rất tốn kém."
2. **Học biểu diễn không giám sát (§3.2):** AE, DAE, VAE, GAN, AAE trên dữ liệu không nhãn. Kết luận: "hiệu năng của các kỹ thuật học biểu diễn không giám sát **không tốt bằng các phương pháp có giám sát**."
3. **Học biểu diễn bán giám sát (§3.3):** kết hợp có nhãn + không nhãn, ví dụ **ladder network** (một DAE không giám sát được huấn luyện đồng thời với một đầu có giám sát). Mức tăng báo cáo: ladder network cho "mức tăng tương đối CCC 3,0% đến 3,5% cho trong-corpus (within-corpus), và 16,1% đến 74,1% cho thiết lập chéo-corpus (cross-corpus)" (MSP-Podcast / IEMOCAP / MSP-IMPROV). Cảnh báo: "huấn luyện mù … không nhất thiết cải thiện hiệu năng so với học có giám sát"; dữ liệu không nhãn "chỉ giúp trong một số tình huống thuận lợi … dữ liệu không nhãn nhiễu và thiên lệch thậm chí có thể dẫn đến hiệu năng tệ hơn."
4. **Học chuyển giao biểu diễn (§3.4):** mục phong phú nhất, chia thành:
   - **Thích nghi miền (Domain-adaptive, §3.4.1):** AE chia sẻ lớp ẩn, **DANN** (mạng nơ-ron đối kháng miền với lớp đảo gradient — gradient-reversal layer), các phương pháp đối kháng chéo-corpus/chéo-ngôn-ngữ. DANN chéo-ngôn-ngữ với bộ phân loại ngôn ngữ đạt "cải thiện 3,91% độ chính xác" so với baseline chéo-ngôn-ngữ ngây thơ trên IEMOCAP/RECOLA.
   - **Học biểu diễn đa tác vụ (Multi-task, §3.4.2):** các tác vụ phụ (arousal/valence, giới tính, người nói, độ tự nhiên) cải thiện tác vụ cảm xúc chính. Báo cáo: MTRL với tác vụ phụ cảm xúc thứ cấp cho "**cải thiện tương đối 7,9% F1**" trên tác vụ phân loại 8 lớp MSP-Podcast; attention đa-đầu với tác vụ phụ giới tính đạt "**70,1% UA** … cao hơn 5,3% so với hiện trạng" cho 4 lớp; LSTM tác vụ phụ người nói+giới tính "cao hơn 5,5% độ chính xác tương đối" trên IEMOCAP; dự đoán đồng thời arousal/valence/dominance tăng "CCC tới 4,7% trong-corpus và 14,0% chéo-corpus." Tính chất then chốt: MTRL cho "**không tăng đáng kể sức mạnh tính toán**" trong khi cải thiện độ chính xác và giảm nguy cơ overfitting.
   - **Tự giám sát (Self-supervised, §3.4.3):** "một paradigm mới … cần được khám phá trong SER." Ví dụ được trích: SSL hướng dẫn bằng thị giác cho giọng nói; bộ mã hóa SSL đa tác vụ + nhiều "workers"; transformer SSL tinh chỉnh từ tác vụ masked-language-modelling cải thiện nhận dạng cảm xúc đa phương thức **3% trên CMU-MOSEI**.
5. **DRL cho học biểu diễn (§3.5):** học tăng cường sâu (deep reinforcement learning) cho phép *khám phá* (mà phương pháp tĩnh thiếu) và có thể tách rời các yếu tố biến thiên — nhưng "vấn đề học biểu diễn cảm xúc để cải thiện SER **chưa được khám phá bằng DRL**." Được đánh dấu là hướng tương lai.

## 6. Bảng dữ liệu (Bảng 4) — lược đồ nhãn chính xác

Bảng 4 ("Review of different SER databases") là danh sách corpus kinh điển của khảo sát. (Lưu ý: căn lề các ô của Bảng 4 trong PDF bị xáo trộn một phần khi trích xuất văn bản; tập corpus và lược đồ dưới đây được phục hồi từ bảng cùng phần thân bài. RAVDESS và CREMA-D *không* nằm trong Bảng 4 — chúng chỉ xuất hiện trong phần thân §3.3 về GAN bán giám sát.)

| Corpus | Ngôn ngữ | Phương thức | Loại | Lược đồ cảm xúc | Công khai |
|---|---|---|---|---|---|
| **EMODB** | Đức | audio | mô phỏng (diễn) | rời rạc (giận, chán, ghê tởm, sợ, vui, buồn, trung tính) | có |
| **MSP-IMPROV** | Anh | audio | gợi mở/cảm ứng | rời rạc (giận, vui, buồn, trung tính) | có |
| **MSP-Podcast** | Anh | audio | tự nhiên (naturalistic) | rời rạc + chiều (arousal, valence, dominance) | có |
| **SEMAINE** | Anh | audio, video | cảm ứng | chiều + nhãn hành vi xã hội | có |
| **IEMOCAP** | Anh | audio (+video) | mô phỏng (có kịch bản + ứng tác) | rời rạc (vui, buồn, giận, trung tính …) + chiều (aro/val/dom) | có |
| **EMOVO** | Ý | audio | mô phỏng | rời rạc (ghê tởm, vui, sợ, giận, ngạc nhiên, buồn, trung tính) | có |
| **RECOLA** | Pháp | đa phương thức | tự nhiên | chiều (arousal, valence, dominance) | có |
| **CMU-MOSEI** | Anh | audio, video | tự nhiên | chiều / 5 chiều cảm xúc (valence, activation, power, anticipation, intensity) | có |

**Các corpus được tham chiếu trong phần thân bài:** **ABC corpus**, **TED talks**, **BUAA emotional corpus**, **FAU-AIBO**, **PRIORI emotion dataset**, **GeWEC**, **CREMA-D**, **RAVDESS**.

**Kích thước kinh điển đã được kiểm chứng** (✔ đã đối chiếu bên ngoài, vì các ô số của Bảng 4 không đáng tin khi trích xuất):
- **IEMOCAP:** ~12 giờ, **5.531 phát ngôn dùng được**, 10 người nói (5 nam/5 nữ) qua 5 phiên, hội thoại đôi có kịch bản + ứng tác; benchmark SER chủ đạo, thường dùng 4 lớp (vui/buồn/giận/trung tính). ✔
- **MSP-Podcast:** tự nhiên, lấy từ podcast; lớn và đang tăng (các bản phát hành đạt ~235 giờ; 610 train / 30 dev / 50 test người nói ở một bản sau). ✔
- **RAVDESS:** 24 diễn viên (12 nam/12 nữ), 1.440 phát ngôn, 8 cảm xúc (bình thản, vui, buồn, giận, sợ, ngạc nhiên, ghê tởm, trung tính). ✔
- **CREMA-D:** 91 diễn viên (48 nam/43 nữ), 7.442 clip, 6 cảm xúc (giận, ghê tởm, sợ, vui, trung tính, buồn). ✔

## 7. Thước đo đánh giá (§2.5) — quy ước đo lường của SER

- **Phân loại:** độ chính xác (accuracy), nhưng vì các corpus cảm xúc tự nhiên **mất cân bằng lớp (class-imbalanced)**, chuẩn của lĩnh vực là **độ chính xác không trọng số (unweighted accuracy — UA) / recall trung bình không trọng số (unweighted average recall — UAR)** — "recall trung bình qua các lớp, không trọng số theo số lượng mẫu mỗi lớp." Được giới thiệu bởi **Interspeech 2009 Emotion Challenge** (Schuller) và được mọi thử thách kế tiếp dùng. (WA = weighted accuracy và F1 cũng xuất hiện.)
- **Hồi quy (arousal/valence/dominance theo chiều):** tối ưu mất mát **MSE**, báo cáo **CCC (concordance correlation coefficient — hệ số tương quan đồng nhất)** làm thước đo chính.

Điều này quan trọng cho Pebble: **UAR, không phải accuracy, là thước đo chính đúng đắn** cho một bộ phân loại cảm xúc mất cân bằng, và **CCC** là chuẩn lĩnh vực cho bất kỳ đầu (head) hồi quy severity/intensity liên tục nào — liên quan trực tiếp đến đầu hồi quy `severity` của Pebble.

## 8. Các con số SOTA / minh họa được trích (Bảng 5)

Đây là các giá trị tốt nhất *trong nội bộ bài*, *không phải* bảng xếp hạng tuyển chọn, và **không so sánh chéo được** (khác split/fold/đặc trưng). Có gắn trạng thái kiểm chứng.

- IEMOCAP, **Transformer trên đặc trưng Wav2Vec: 70,1% UA** (Bảng 5, dòng Lotfian et al.) — UA IEMOCAP cao nhất trong bảng. ≈ xấp xỉ (trích xuất Bảng 5 bị xáo trộn; giá trị 70,1% xuất hiện hai lần, cũng cho kết quả gender-MTL; nên xem là "tốt nhất ~70% UA" hơn là một con số gán chính xác).
- IEMOCAP, CNN-LSTM: 66,8% UA; BLSTM: 62–66%; baseline DNN ~59–61% UAR. ≈ xấp xỉ.
- Hợp nhất DBN với đặc trưng thủ công: +5,48% đến +8,8% so với đặc trưng cổ điển (EMODB / chéo-corpus). ✔ (nhất quán với phần thân bài).
- MTRL F1 +7,9% tương đối (8 lớp, MSP-Podcast); gender-MTL +5,3% UA; speaker/gender-MTL +5,5% accuracy. ✔ (phần thân §3.4.2).
- SSL transformer (pretext MLM) +3% trên CMU-MOSEI đa phương thức. ✔ (phần thân §3.4.3).
- GAN chéo-corpus: 61,05% (trong-corpus) / 46,60% (chéo-corpus) accuracy — minh họa **sụt giảm lớn từ trong-corpus sang chéo-corpus**. ✔ (phần thân §3.2).

**Mẫu hình quan trọng nhất:** các con số trong-corpus tụ quanh ~60–70% UA trên IEMOCAP, nhưng **hiệu năng chéo-corpus / chéo-ngôn-ngữ sụp đổ** (ví dụ 61% → 47%). Khoảng cách tổng quát hóa này là vấn đề mở định nghĩa cả lĩnh vực (§4.3) và là bài học chuyển giao quan trọng nhất cho Pebble.

## 9. Thách thức mở (§4) và hướng tương lai (§5, Bảng 6)

Năm thách thức, mỗi cái có "giải pháp đã khám phá / khoảng trống hiện hữu / hướng tương lai" (Bảng 6):

1. **Độ phức tạp huấn luyện (§4.1):** manifold giọng nói trộn lẫn thông điệp + người nói + giới tính + tuổi + sức khỏe + tâm trạng + cảm xúc; tách rời cảm xúc là "mục tiêu lâu dài." Huấn luyện không giám sát khó hơn có giám sát và "có thể bỏ qua các thuộc tính cảm xúc."
2. **Thiếu dữ liệu giọng nói cảm xúc (§4.2):** các corpus nhỏ, phần lớn ghi trong phòng lab với cảm xúc **diễn (acted)** vốn "có thể không đại diện cho cảm xúc con người ngoài đời thực"; người chú thích gán nhãn **'cảm xúc bên ngoài' (outer emotion)** vốn "có thể rất khác với 'cảm xúc bên trong' (inner emotion)." Nhiễu (nền, micro) làm hỏng dữ liệu; tiêm nhiễu (noise-injection) chỉ hiệu quả với SNR vừa phải.
3. **Biến thiên corpus và ngôn ngữ (§4.3):** khoảng cách tổng quát hóa — "hiệu năng … giảm đáng kể nếu mẫu kiểm thử lệch khỏi phân phối dữ liệu huấn luyện," tệ hơn giữa các ngôn ngữ. Có >5.000 ngôn ngữ nói; 389 ngôn ngữ chiếm 94% dân số, nhưng corpus thiếu cho hầu hết. Few-shot và biểu diễn bất biến ngôn ngữ được đề xuất nhưng "chưa có giải pháp thỏa đáng hoàn toàn."
4. **Quyền riêng tư và độ bền vững (§4.4):** giọng nói rò rỉ giới tính, sắc tộc, trạng thái cảm xúc, danh tính; voiceprint cho phép giả mạo. Giảm thiểu: học biểu diễn bảo toàn riêng tư, trích xuất đặc trưng **trên thiết bị/edge**, **học liên kết (federated learning)**. Mô hình SER cũng dễ bị **tấn công đối kháng (adversarial attacks)** (FGSM, JSMA, DeepFool); kiến trúc rất sâu được thấy là tương đối bền.
5. **(Tương lai) DRL, đa phương thức, transformer, sinh dữ liệu tổng hợp, SSL** là các biên giới nghiên cứu được nêu tên (§5, Kết luận).

## 10. Pebble nên định vị đóng góp phương thức giọng nói của mình thế nào

Mục này là sản phẩm chính cần giao: vị trí của một chương SER Pebble trên bản đồ này và cách đóng khung tính mới của nó.

**Tuyên bố định vị.** Phương thức giọng nói của Pebble nằm tại giao điểm mà khảo sát đánh dấu rõ là chưa được khám phá đủ: **(a) học biểu diễn tự giám sát / chuyển giao (§3.4.3 — "cần được khám phá trong SER")** áp dụng cho **(b) một triển khai thực tế, trong-tự-nhiên (in-the-wild), hướng trẻ em** (nhu cầu "nhận dạng cảm xúc trong tự nhiên" của §4.2), với **(c) các đầu đa tác vụ** (§3.4.2 MTRL — câu chuyện thực nghiệm mạnh nhất của khảo sát) và **(d) xử lý tổng quát hóa/độ bền rõ ràng** (§4.3, khoảng trống định nghĩa lĩnh vực). Pebble có thể tuyên bố đóng góp trên *mỗi một trong bốn trục mà khảo sát liệt kê là mở*, đồng thời thẳng thắn thừa nhận nó không thúc đẩy lý thuyết học biểu diễn cốt lõi.

Các bước định vị cụ thể cho chương:

1. **Đóng khung lựa chọn bộ mã hóa theo cung CNN-RNN-rồi-SSL của khảo sát.** Khảo sát xác lập CNN-LSTM là mặc định có giám sát năm 2021 và transformer SSL là biên giới mở. Đầu SER của Pebble nên xây trên **bộ mã hóa âm thanh SSL được tiền-huấn-luyện** (wav2vec2 / HuBERT / WavLM) — tức chính xác khoảng trống "học biểu diễn tự giám sát … cần được khám phá trong SER" — và trích dẫn khảo sát này như tuyên bố về khoảng trống đó, rồi trích dẫn các bài SSL-SER mới hơn (#24, #27, #40) cho phần hiện thực hóa. **(D-A:** quyết định bộ mã hóa nền (backbone) tổng quát hóa qua các phương thức — khảo sát là trích dẫn cho "học biểu diễn vượt kỹ thuật đặc trưng, kiến trúc quan trọng hơn đặc trưng đầu vào," ủng hộ chính sách ưu-tiên-backbone-tiền-huấn-luyện-mạnh cho cả bộ mã hóa văn bản NeoBERT lẫn bất kỳ bộ mã hóa âm thanh nào.)

2. **Áp dụng UAR làm thước đo chính và CCC cho mọi đầu liên tục.** Khảo sát (§2.5) là trích dẫn kinh điển rằng **UA/UAR — không phải accuracy — là bắt buộc khi mất cân bằng lớp** (quy ước thử thách Interspeech-2009), và **CCC** là thước đo lĩnh vực cho hồi quy chiều/cường độ. Đầu `emotion` của Pebble phải báo cáo **macro-recall / UAR** (đã là chuẩn của nó: 47,8% macro-recall) và đầu hồi quy `severity` của Pebble nên báo cáo **CCC (và Pearson)**, không chỉ MSE/MAE. **(D-C, D-D:** điều này cố định thước đo cho các đầu severity/emotion theo chuẩn lĩnh vực, làm cho các con số của Pebble so sánh được và trích dẫn được.)

3. **Dẫn dắt bằng học biểu diễn đa tác vụ như thiết kế được biện minh thực nghiệm.** Kết quả tích cực mạnh nhất, nhất quán nhất của khảo sát là MTRL: **+7,9% F1, +5,3–5,5% UA, +4,7–14% CCC** từ các tác vụ phụ, với **"không tăng đáng kể sức mạnh tính toán"** và giảm overfitting. Đây là sự ủng hộ bên ngoài trực tiếp cho thiết kế đa-đầu MTL của Pebble (emotion + severity + các đầu heuristic dùng chung một bộ mã hóa). **(D-B:** khảo sát chứng thực rằng MTL giúp các tác vụ cảm xúc thiếu tài nguyên — kế hoạch đa-đầu chia sẻ bộ mã hóa của Pebble là con đường đã được đi nhiều, và phát hiện "tác vụ phụ có nhiều dữ liệu giúp tác vụ chính thiếu nhãn" (Latif et al. trong §3.4.2) là trích dẫn cho việc dùng một tác vụ phụ nhiều tài nguyên, ví dụ arousal/valence hoặc giới tính, để nâng tín hiệu cảm xúc trẻ em thiếu của Pebble.)

4. **Biến tổng quát hóa chéo-corpus thành đánh giá tiêu đề, không phải accuracy trong-corpus.** Kết quả cảnh báo lớn nhất của khảo sát (sụp đổ chéo-corpus 61%→47%, §3.2/§4.3) nghĩa là một con số trong-IEMOCAP là *vô giá trị* như bằng chứng cho một sản phẩm hướng trẻ em. Chương SER của Pebble nên **báo cáo đánh giá chéo-corpus / ngoài-phân-phối (OOD) làm kết quả chính** và trích dẫn các phương pháp thích nghi miền / DANN (§3.4.1) như bộ công cụ giảm thiểu. **(D-D, D-H:** các quyết định về nguồn chuyển giao và dữ liệu/hiệu chỉnh phải giả định có khoảng cách tổng quát hóa; khảo sát là trích dẫn rằng hiệu năng trên corpus diễn của người lớn KHÔNG chuyển sang giọng trẻ em trong-tự-nhiên nếu không có thích nghi miền rõ ràng.)

5. **Sở hữu khoảng trống "trong-tự-nhiên + cảm-xúc-bên-trong-vs-bên-ngoài + trẻ em" như đóng góp.** §4.2 nêu các corpus là cảm xúc diễn trong lab, gán nhãn *bên ngoài* bởi người chú thích, xa với *bên trong*; §4.3 nêu tổng quát hóa thực tế chưa được giải. Một thiết lập SER hướng trẻ em, tự nhiên, *gán nhãn-bạc (silver)* nằm thẳng trong không gian chưa được giải quyết — Pebble có thể tuyên bố tính mới chính xác trên dân số (trẻ em), đăng ký giọng (lời nói tự nhiên trong-ứng-dụng), và chế độ nhãn (silver/LLM thay vì người chú thích cảm-xúc-bên-ngoài). Không bài nào trong khảo sát này bao phủ giọng nói trẻ em.

## 11. Khuyến nghị sử dụng trích dẫn

Trong một bài báo Pebble, khảo sát này ủng hộ các tuyên bố sau:

- **"Học biểu diễn đã thay thế kỹ thuật đặc trưng trong SER; kiến trúc quan trọng hơn lựa chọn đặc trưng đầu vào."** (§2.1, §5.1). Trích để biện minh cách tiếp cận bộ-mã-hóa-học-được thay cho pipeline GeMAPS/MFCC.
- **"UA/UAR là thước đo chuẩn bền-với-mất-cân-bằng trong SER (quy ước Interspeech-2009); CCC là chuẩn cho hồi quy cảm xúc theo chiều."** (§2.5). Trích cho lựa chọn thước đo của Pebble trên đầu emotion (macro-recall) và severity (CCC).
- **"Học biểu diễn đa tác vụ cải thiện tác vụ cảm xúc chính bằng các tác vụ phụ (giới tính/người nói/arousal-valence) mà không tốn nhiều tính toán và giảm overfitting."** (§3.4.2). Trích để biện minh MTL đa-đầu chia sẻ bộ mã hóa của Pebble.
- **"Hiệu năng SER chéo-corpus và chéo-ngôn-ngữ suy giảm mạnh so với trong-corpus."** (§3.2, §4.3). Trích để biện minh đánh giá ngoài-phân-phối và thích nghi miền là trung tâm, không tùy chọn.
- **"Học biểu diễn tự giám sát là biên giới chưa được khám phá đủ nhưng hứa hẹn cho SER."** (§3.4.3, Kết luận). Trích để định vị một đầu SER SSL-âm-thanh của Pebble như lấp một khoảng trống được nêu tên.
- **"Các corpus SER chủ yếu là diễn-trong-lab, nắm bắt cảm xúc 'bên ngoài' hơn là 'bên trong', giới hạn tổng quát hóa thực tế."** (§4.2). Trích để biện minh thu thập dữ liệu tự nhiên / trong-tự-nhiên và đặt kỳ vọng một cách trung thực.
- **Danh sách bộ dữ liệu SER tiếng Anh kinh điển + lược đồ nhãn** (Bảng 4: EMODB/MSP-IMPROV/MSP-Podcast/SEMAINE/IEMOCAP/EMOVO/RECOLA/CMU-MOSEI). Trích như tập benchmark đã được thiết lập khi mô tả lựa chọn corpus tiền-huấn-luyện/đánh-giá của Pebble.

**KHÔNG trích khảo sát này cho:** các con số hiện trạng SSL-SER hiện tại (nó có trước thời wav2vec2/HuBERT-SER — dùng #24/#27/#40), bất kỳ kết quả giọng nói trẻ em nào (không có ở đây), bất kỳ thứ hạng bảng xếp hạng cụ thể nào (Bảng 5 là minh họa, không tuyển chọn), hay kết quả transformer-SER (được coi là việc tương lai, không được khảo sát).

## Deep research — full-PDF read (2026-06-16)

### Ghi chú truy cập nguồn

Bản PDF cục bộ (`pdfs/28-latif-ser-survey.pdf`, 9,7 MB) là phiên bản **bản thảo đã chấp nhận (accepted-manuscript)** tải từ QUT ePrints (eprints.qut.edu.au/213410/, "Emotional_Representations_Review_minor_revision_2_3.pdf"), CC BY-NC 4.0, kèm cảnh báo rằng nó "có thể không phải Phiên bản Bản ghi (Version of Record)." Văn bản được trích xuất bằng `pdftotext -layout` (1.628 dòng) và đọc toàn bộ (Giới thiệu → §2 Bối cảnh/Khái niệm → §3 năm mô hình học biểu diễn → §4 Thách thức → §5 Thảo luận/Tương lai → §6 Kết luận → tài liệu tham khảo).

Đã kiểm chứng qua web:
- **Bản ghi thư mục** — truy vấn "Latif Rana Khalifa Schuller Survey of Deep Representation Learning for Speech Emotion Recognition IEEE Transactions Affective Computing 2023". Đã giải quyết: https://eprints.qut.edu.au/213410/ và https://opus.bibliothek.uni-augsburg.de/opus4/files/91554/91554.pdf. Xác nhận **T-AFFC tập 14(2), trang 1634–1654, năm 2023, DOI 10.1109/TAFFC.2021.3114365** (bản thảo cục bộ khớp với bản ghi nơi công bố). ✔
- **Kích thước kinh điển của bộ dữ liệu** (các ô số của Bảng 4 bị xáo trộn khi trích xuất PDF, nên cần đối chiếu bên ngoài) — truy vấn "IEMOCAP MSP-Podcast RAVDESS CREMA-D speech emotion recognition dataset size speakers utterances". Xác nhận **IEMOCAP 5.531 phát ngôn / ~12h / 10 người nói; RAVDESS 24 diễn viên / 1.440 phát ngôn / 8 cảm xúc; CREMA-D 91 diễn viên / 7.442 clip / 6 cảm xúc; MSP-Podcast tự nhiên, ~235h ở các bản sau**. ✔ (Nguồn: arxiv.org/pdf/2402.13018 EMO-SUPERB; github.com/usc-sail/trust-ser; tổng quan audio-datasets trên Medium.)
- **Ghi chú xung đột:** PDF cục bộ là bản thảo đã chấp nhận, không phải Phiên bản Bản ghi IEEE đã được dàn trang. Không tìm thấy xung đột số học giữa nó và bản ghi nơi công bố; cách đánh số mục/hình ở đây theo bản thảo. Khi các ô của Bảng 4/Bảng 5 trong bản thảo bị lệch khi trích xuất, dossier này đánh dấu các con số bị ảnh hưởng là ≈ xấp xỉ và dùng các giá trị đã được đối chiếu bên ngoài thay thế.

### Bài báo thực sự làm gì

Một khảo sát toàn cảnh (không có thí nghiệm mới) tổ chức **học biểu diễn sâu cho SER** theo ba trục: (a) **kiểu đặc trưng** — thủ công (MFCC, LogMel, GeMAPS/eGeMAPS, IS09–IS13, LLDs) vs giọng nói thô vs học được (§2.1, §5.1); (b) **các họ mô hình DL** — DNN, CNN (ResNet/DenseNet), RNN (LSTM/GRU/BLSTM), CNN-RNN, CapsNet, attention, AE/DAE/sparse-AE/AAE, DBN/RBM, VAE, GAN, transformer (§2.3, Bảng 3); (c) **các mô hình học** — có giám sát, không giám sát, bán giám sát, chuyển giao (thích nghi miền / đa tác vụ / tự giám sát), và DRL (§3, tóm tắt trong Bảng 5). Nó liệt kê các corpus kinh điển (Bảng 4), quy ước đánh giá (UA/UAR, CCC; §2.5), và năm thách thức mở với hướng tương lai (§4, Bảng 6). Tác giả chính Schuller neo nó vào truyền thống thử thách Interspeech ComParE.

Các phát hiện mang trọng lượng thực nghiệm (tất cả từ các nghiên cứu được trích, không phải lần chạy của chính tác giả):
- Có giám sát > bán giám sát > không giám sát về độ chính xác SER thô; không giám sát "không tốt bằng có giám sát" (§3.2).
- **MTRL là đòn bẩy tích cực mạnh nhất:** +7,9% F1 (8 lớp MSP-Podcast), +5,3% UA (aux giới tính), +5,5% accuracy (aux người nói/giới tính IEMOCAP), +4,7–14% CCC (đồng thời aro/val/dom), với "không tăng đáng kể sức mạnh tính toán" (§3.4.2). ✔ (phần thân).
- IEMOCAP trong-corpus đạt đỉnh ~70% UA (đặc trưng Transformer/Wav2Vec; Bảng 5). ≈ xấp xỉ (trích xuất Bảng 5 bị xáo trộn).
- **Sụp đổ chéo-corpus:** 61,05% trong → 46,60% chéo-corpus accuracy (nghiên cứu GAN, §3.2). ✔ — chế độ thất bại trung tâm của lĩnh vực.
- SSL được đóng khung như biên giới mở; transformer SSL với pretext MLM cho +3% trên CMU-MOSEI (§3.4.3). ✔.

### Các phần trực tiếp hữu ích cho Pebble

1. **Quy ước thước đo: UA/UAR (mất cân bằng) + CCC (hồi quy)** (§2.5). → cố định đầu emotion của Pebble theo macro-recall/UAR và đầu severity theo CCC/Pearson. **(D-C, D-D)**
2. **Cơ sở bằng chứng MTRL** (§3.4.2): tác vụ phụ nâng tác vụ chính thiếu nhãn với chi phí tính toán gần như bằng không. → biện minh bên ngoài cho MTL đa-đầu chia sẻ bộ mã hóa của Pebble và cho việc thêm một tác vụ phụ nhiều tài nguyên (arousal/valence hoặc giới tính) để nâng tín hiệu cảm xúc trẻ em thiếu. **(D-B)**
3. **"Kiến trúc/biểu diễn quan trọng hơn đặc trưng đầu vào; học biểu diễn > kỹ thuật đặc trưng"** (§2.1, §5.1). → ủng hộ chính sách ưu-tiên-backbone-tiền-huấn-luyện-mạnh qua các phương thức. **(D-A)**
4. **Khoảng cách tổng quát hóa chéo-corpus** (§3.2, §4.3) + bộ công cụ thích nghi miền (DANN/GRL, AE chia sẻ lớp ẩn, §3.4.1). → bắt buộc đánh giá OOD/chéo-corpus làm kết quả SER chính và thích nghi miền là bước hạng nhất. **(D-D, D-H)**
5. **Danh sách bộ dữ liệu + lược đồ nhãn** (Bảng 4) → tập benchmark trích dẫn được để chọn corpus tiền-huấn-luyện/đánh-giá SER của Pebble. **(D-H)**
6. **"Cảm xúc bên ngoài vs bên trong" + giới hạn corpus diễn-trong-lab** (§4.2) → đóng khung trung thực rằng corpus người lớn diễn-trong-lab giới hạn, không dự đoán, hiệu năng trẻ-em-trong-tự-nhiên. **(D-H)**

### Mỗi phần giúp Pebble thành công thế nào

- **Thước đo (1) → bộ công cụ báo cáo.** Thêm **UAR/macro-recall** làm vô hướng chính của đầu emotion (chuẩn của Pebble đã là 47,8% macro-recall — khảo sát là trích dẫn rằng đây là chuẩn *đúng* khi mất cân bằng) và **CCC + Pearson** làm vô hướng chính của đầu severity. Rủi ro chuyển giao: **thấp** — đây là quy ước đo lường, hoàn toàn chuyển được; lưu ý duy nhất là lược đồ 12-nhãn ánh-xạ-GoEmotions của Pebble có độ chi tiết cao hơn chuẩn SER 4–8 lớp, nên phương sai recall theo lớp sẽ rộng hơn.
- **MTRL (2) → công thức huấn luyện.** Giữ bộ mã hóa NeoBERT/âm thanh dùng chung với nhiều đầu; cân nhắc một **tác vụ phụ nhiều tài nguyên** (ví dụ arousal/valence từ một corpus SER có nhãn, hoặc giới tính) huấn luyện đồng thời để chính quy hóa đầu cảm xúc trẻ em thiếu, gán nhãn-bạc. Rủi ro chuyển giao: **trung bình** — các mức tăng MTRL của khảo sát trên giọng người lớn diễn/podcast; việc tác vụ phụ giới tính/arousal có giúp cảm xúc *trẻ em* hay không chưa được kiểm thử, nhưng cơ chế (chính quy hóa biểu diễn dùng chung) không phụ thuộc phương thức và dân số, nên rủi ro giảm bị giới hạn.
- **Backbone (3) → chính sách bộ mã hóa.** Chọn một bộ mã hóa âm thanh SSL tiền-huấn-luyện mạnh thay vì pipeline GeMAPS/MFCC + bộ phân loại nông; phản chiếu lựa chọn NeoBERT-trên-thủ-công bên text của Pebble. Rủi ro chuyển giao: **thấp** cho nguyên lý, **trung bình** cho bộ mã hóa cụ thể (bộ mã hóa SSL tiền-huấn-luyện trên giọng đọc/podcast người lớn; đặc tính âm học của trẻ — F0 cao hơn, formant khác — có thể cần tiền-huấn-luyện tiếp tục thích nghi miền, xem #40).
- **Tổng quát hóa (4) → thiết kế đánh giá.** Biến kết quả tiêu đề của chương SER thành một con số **chéo-corpus / OOD** (huấn luyện trên một corpus, kiểm thử trên một corpus giữ-lại và trên một lát cắt trẻ em), và dự trù một bước thích nghi miền. Rủi ro chuyển giao: **thấp** — khoảng cách là phổ quát; nếu có thì nó *đánh giá thấp* rủi ro của Pebble vì dịch chuyển người-lớn→trẻ-em lớn hơn các dịch chuyển corpus→corpus mà khảo sát đo.
- **Bộ dữ liệu (5) → chọn corpus.** Dùng IEMOCAP/MSP-Podcast/CREMA-D/RAVDESS làm tập SER tiếng Anh đã thiết lập cho tiền-huấn-luyện/benchmark; lưu ý không cái nào là giọng trẻ em, nên một lát cắt hiệu chỉnh trẻ em là bắt buộc. Rủi ro chuyển giao: **cao** cho bất kỳ chuyển giao số trực tiếp nào (tất cả người lớn diễn/tự nhiên) — các corpus này hiệu chỉnh *phương pháp*, không phải *triển khai*.

### Lăng kính sức khỏe tâm thần trẻ em

- **Không có giọng nói trẻ em ở đâu cả.** Mọi corpus trong Bảng 4 (và phần thân) đều là người lớn — diễn viên, người làm podcast, người tham gia lab. Gần nhất là FAU-AIBO (trẻ em nói với một chú chó robot), chỉ được nhắc thoáng qua cho thích nghi miền chéo-corpus. **Tính hợp lệ chuyển giao cho một sản phẩm hướng trẻ em chưa được khảo sát này xác lập** — nó là bản đồ *phương pháp*, không phải bằng chứng cho SER trẻ em.
- **Rủi ro dịch chuyển âm học.** Trẻ em có tần số cơ bản cao hơn, cấu trúc formant khác, ngôn điệu kém ổn định hơn, và biến thiên theo phát triển. Một bộ mã hóa SSL tiền-huấn-luyện trên giọng người lớn (chính tiền đề của khảo sát) sẽ **ngoài-phân-phối** đối với giọng trẻ — chính là khoảng cách tổng quát hóa §4.3, khuếch đại. Giảm thiểu: tiền-huấn-luyện tiếp tục thích nghi miền trên âm thanh trẻ/người-trẻ-hơn trước khi tinh chỉnh đầu, và một tập hiệu chỉnh trẻ em với báo cáo hiệu năng theo dải tuổi.
- **"Cảm xúc bên ngoài vs bên trong" sắc nét hơn với trẻ em** (§4.2). Cảnh báo của khảo sát — người chú thích gán nhãn cảm xúc *bên ngoài* (biểu lộ), vốn có thể rất khác cảm xúc *bên trong* (cảm nhận) — gay gắt hơn với trẻ em, vốn che giấu, báo cáo thiếu, hoặc biểu lộ đau khổ gián tiếp. Một đầu SER trẻ em phải được đóng khung là phát hiện *cảm xúc âm học biểu lộ*, không bao giờ là *trạng thái nội tâm cảm nhận*, và phải đưa vào một luồng có-con-người-trong-vòng-lặp (nhất quán với kỷ luật ranh-giới-vai-trò của FAIIR, bài #01).
- **Quyền riêng tư là không thể thương lượng** (§4.4). Chính khảo sát đánh dấu rằng giọng nói rò rỉ danh tính, giới tính, sắc tộc, trạng thái cảm xúc, và cho phép giả mạo. Với một sản phẩm giọng nói hướng trẻ em, đây là ràng buộc đạo đức/pháp lý cứng: trích xuất đặc trưng trên-thiết-bị/edge, học liên kết, không lưu giữ âm thanh thô, đồng thuận của người giám hộ — tất cả được khảo sát nêu tên như tập giảm thiểu, tất cả bắt buộc với Pebble.
- **Cảm xúc corpus-diễn ≠ cảm xúc khủng hoảng.** Các corpus của khảo sát mã hóa cảm xúc nguyên mẫu diễn (giận/vui/buồn) trong các clip ngắn. Các tín hiệu liên quan sức khỏe tâm thần trẻ em (cảm xúc phẳng, lo âu, thu mình, rối loạn điều hòa) phần lớn vắng mặt trong các lược đồ nhãn này — một lý do nữa cho thấy Bảng 4 hiệu chỉnh phương pháp, không phải các mục tiêu thực tế của Pebble.

### Hạn chế & câu hỏi mở cho Pebble

- **Niên đại / khoảng trống SSL (mâu thuẫn với kế hoạch Pebble và với các bài mới hơn).** Khảo sát coi **transformer và SSL là việc tương lai** ("Transformer cần được khám phá trong SER," §5.2; SSL "cần được khám phá," §3.4.3). Kế hoạch Pebble (và các bài #24 MMER, #27 Morais, #40 wav2vec2-depression trong chính repo này) giả định **transformer SSL là mặc định SER**. Đây là mâu thuẫn trực tiếp sinh ra từ niên đại: khảo sát là *bản đồ trước cách mạng SSL*. Pebble phải trích nó cho *tuyên bố khoảng trống* và các bài mới hơn cho *lời giải* — không bao giờ làm bằng chứng về hiệu năng SSL-SER hiện tại.
- **Các con số Bảng 5 là minh họa, không phải benchmark.** Khác split, giao thức fold, và đặc trưng khiến các dòng không so sánh được; trích xuất PDF còn làm xáo trộn căn lề ô của Bảng 5. Pebble không thể trích một "SOTA UA" từ bài này làm chuẩn mục tiêu — chỉ *mẫu hình* (trong ~60–70% UA, chéo-corpus ~47%).
- **Mức tăng MTRL là theo corpus người lớn và đặc thù tác vụ.** Các con số +7,9% F1 / +5,3% UA là trên MSP-Podcast/IEMOCAP với tác vụ phụ giới tính/cảm-xúc-thứ-cấp. Việc các tác vụ phụ cụ thể đó có giúp một đầu cảm xúc trẻ em 12 nhãn hay không chưa được kiểm thử — Pebble nên coi MTRL như một *cơ chế* cần xác thực thực nghiệm, không phải mức tăng được bảo đảm.
- **Không hiệu chỉnh / không thảo luận về độ bất định.** Giống FAIIR (#01), khảo sát chỉ báo cáo các thước đo điểm — không reliability/ECE cho bất kỳ mô hình SER nào. Decision Engine của Pebble tiêu thụ xác suất, nên hiệu chỉnh của đầu âm thanh là một yêu cầu mở mà tài liệu này không giải quyết.
- **Mâu thuẫn liên-phương-thức với kế hoạch text.** Tuyên bố trung tâm của khảo sát — "việc lựa chọn đặc trưng đầu vào không quan trọng bằng kiến trúc mô hình" (§5.1) — hơi căng với khoản đầu tư bên text của Pebble vào MLM thích nghi miền và kỹ thuật lược đồ nhãn (D-C/D-F), vốn giả định thiết kế đầu vào/biểu diễn *có* quan trọng. Hòa giải: trong SER tuyên bố là về kỹ thuật đặc trưng *âm học* (MFCC vs LogMel vs thô), trong khi các quyết định bên text của Pebble liên quan đến thiết kế *nhãn* và thích nghi *miền*, không phải làm thủ công đặc trưng đầu vào — nên khảo sát ủng hộ "đừng làm thủ công đầu vào, hãy thích nghi biểu diễn," chính là lập trường MLM/chuyển-giao của Pebble.
- **Câu hỏi mở — corpus SER trẻ em.** Khảo sát làm rõ rằng không có corpus SER trẻ em chuẩn hóa nào tồn tại trong tập kinh điển. Việc Pebble có phải xây/tuyển một cái (với chế độ đạo đức/đồng thuận/riêng tư mà §4.4 đòi hỏi) hay không là phụ thuộc chưa giải quyết lớn nhất cho chương giọng nói.
