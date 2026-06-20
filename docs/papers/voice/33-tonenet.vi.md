# Bài báo 33 — ToneNet: Một mô hình CNN phân loại thanh điệu tiếng Trung Quan Thoại

## 1. Thông tin thư mục

**Tiêu đề:** ToneNet: A CNN Model of Tone Classification of Mandarin Chinese

**Tác giả:** Qiang Gao, Shutao Sun (tác giả liên hệ), Yaping Yang — School of Computer and Cyberspace Security, Communication University of China, Bắc Kinh, Trung Quốc.

**Năm / hội nghị:** Interspeech 2019 (15–19 tháng 9 năm 2019, Graz, Áo). *Proc. Interspeech 2019*, tr. 3367–3371. DOI 10.21437/Interspeech.2019-1483. Xuất bản trong ISCA Archive (`gao19c_interspeech`).

**Từ khóa (nguyên văn):** "ToneNet; tone classification; mel-spectrogram; Mandarin Chinese; convolutional neural networks".

**Tài trợ (liên quan tới Pebble):** "Fundamental Research Funds for the Central Universities (2017XNG1749)" và **"dự án Research on Evaluation Technique of Children's Mandarin Speech Training (HG1711-1)"** — tức là bối cảnh tài trợ của bài báo rõ ràng là một chương trình *đánh giá giọng nói cho trẻ em*.

> Khung tham chiếu cho Pebble: đây là một bài báo thuộc **modality tin nhắn thoại (voice-message)**.
> Trong luận điểm Pebble, một tin nhắn thoại là tín hiệu ngôn ngữ-cận biên (paralinguistic), và nhận
> dạng thanh điệu từ vựng (lexical tone) là ví dụ kinh điển của bài toán **mô hình hóa đường nét cao
> độ / ngữ điệu (pitch-contour / prosody)**. ToneNet là minh chứng rõ ràng nhất trong tập bài báo
> liên quan rằng một bộ phân loại thanh điệu / đường nét cao độ có thể được xây dựng như một **CNN
> ảnh 2 chiều trên một vùng cắt mel-spectrogram**, né tránh việc trích xuất F0 tường minh vốn dễ vỡ.
> Ta đọc nó vì module thanh điệu spectrogram-CNN của nó đóng góp gì cho một front-end thoại của
> Pebble, chứ không phải vì tiếng Quan Thoại bản thân nó.

## 2. Động cơ của bài toán

Tiếng Trung Quan Thoại là ngôn ngữ có thanh điệu: cùng một âm tiết mang nghĩa từ vựng khác nhau tùy thuộc nó mang thanh nào trong bốn thanh — (1) cao-bằng, (2) lên, (3) thấp-trầm, (4) xuống. Thanh điệu đúng là "chìa khóa để truyền đạt nghĩa từ chính xác," nên phân loại thanh điệu là "một phần thiết yếu của hệ thống đánh giá giọng nói" và cũng quan trọng cho tỉ lệ lỗi ASR và cho tổng hợp giọng nói tự nhiên. Tác giả trích [5] (Chen, Wong, Hu 2014) rằng độ chính xác nhận dạng câu tiếng Quan Thoại giảm mạnh khi thông tin thanh điệu bị nhiễu làm hỏng.

Phàn nàn kỹ thuật trung tâm thúc đẩy bài báo: **phân loại thanh điệu truyền thống dựa vào F0 (cao độ) và năng lượng, hoặc dựa vào MFCC, và các đặc trưng này dễ vỡ** — "việc trích xuất các đặc trưng này thường chịu tác động của nhiễu và các yếu tố môi trường không kiểm soát được." Riêng F0 "không ổn định khi trích xuất" và "dễ gây bùng nổ gradient hoặc không hội tụ khi các đặc trưng âm học được dùng huấn luyện trực tiếp trong học sâu." Luận điểm của ToneNet là một **ảnh mel-spectrogram** giữ lại "nhiều thông tin thô hơn F0," tôn trọng tri giác thính giác của con người, và — khi cắt về dải tần thấp nơi đường nét thanh điệu nằm — cho một đặc trưng bền vững, chịu nhiễu mà CNN có thể đọc như một bức ảnh.

## 3. Vị trí trong tài liệu

Ba hướng nghiên cứu trước được đối chiếu:

- **Phương pháp ngữ điệu cổ điển F0 + năng lượng** [2] Levow 2006, [3] Lei và cộng sự 2006 — phản ánh ngữ điệu đơn âm tiết nhưng dễ bị nhiễu môi trường làm rối loạn.
- **Phương pháp MFCC + DNN/CNN** — Ryant và cộng sự [16] huấn luyện một DNN trên 40 MFCC (frame error rate 27.38% / segment error rate 15.62%, "không cần dò cao độ"); **Chen và cộng sự [1] (Interspeech 2016)** dùng MFCC đưa vào CNN với một bước tiền-huấn-luyện denoising autoencoder (dAE), đạt độ chính xác 95.53% — phương pháp trước mạnh nhất và là điểm so sánh trực tiếp của ToneNet. Tác giả lưu ý dAE của Chen "vẫn chưa khắc phục hoàn toàn ảnh hưởng của nhiễu."
- **Phương pháp gợi ý chú ý thính giác (auditory-attention-cue)** — Kalinli [13] (ICASSP 2011), phân loại thanh điệu và trọng âm cao độ chỉ đạt 72.8% độ chính xác.

Khoảng trống được tuyên bố: mọi phương pháp trước hoặc phụ thuộc vào đặc trưng cao độ/MFCC tường minh và dễ vỡ vì nhiễu, hoặc kém hiệu năng. ToneNet thay thế pipeline đặc trưng bằng một ảnh mel-spectrogram đã cắt đưa vào một CNN kiểu VGG, và báo cáo một bước nhảy lớn (99.16% so với 95.53%).

## 4. Phân tích sâu tập dữ liệu — SCSC

**Syllable Corpus of Standard Chinese (SCSC).** Đơn vị tạo: The Institute of Linguistics, Chinese Academy of Social Sciences. Đây là một kho ngữ liệu **đơn âm tiết**: 1.275 ký tự Trung Quốc đơn âm tiết, mỗi ký tự được phát âm bởi **15 thanh niên nam**, tổng cộng **19.125 lần phát âm**. Âm thanh là **mono, WAV 16-bit, tần số lấy mẫu 16.000 Hz**; mỗi đoạn dài **~0,5–1 giây**.

**Phân chia:** **8:1:1** train / validation / test. (≈15.300 / 1.912 / 1.912 lần phát âm.) Train+val để khớp mô hình và tinh chỉnh siêu tham số; test giữ riêng cho đánh giá cuối.

**Nhãn:** bốn thanh điệu kinh điển (T1–T4). Đây là bài toán 4 lớp cân bằng, sạch — một register người nói duy nhất (nam trưởng thành trẻ), các âm tiết đơn thu trong phòng thu sạch, nhãn ngữ âm chuẩn vàng. (Tương phản với chế độ nhãn-bạc nhiễu, register trẻ em, ngoài-thực-địa của Pebble — xem §Lăng kính trẻ em.)

**Truy cập:** SCSC là một kho ngữ liệu thuộc thể chế (Chinese Academy of Social Sciences); nó **không** nằm trong các kho thanh điệu tải mở trong `data/voice/external/` của Pebble (các kho đó là AISHELL-1, THCHS-30, VIVOS). Coi SCSC như không trực tiếp lấy được; *phương pháp* chuyển giao được, *dữ liệu* thì không.

## 5. Phương pháp

### 5.1 Tiền xử lý đặc trưng — mel-spectrogram đã cắt

- Dải tần đầy đủ của mel-spectrogram: **[0, 8000] Hz**, tính với **64 bộ lọc mel**, **độ dài khung 2048 mẫu**, **bước dịch khung 16 mẫu**, trích xuất bằng **librosa** [15].
- **Hiểu biết then chốt:** thông tin thanh điệu (đường nét ngữ điệu) nằm ở **dải tần thấp**. F0 nói của con người là ~100–300 Hz (thấp hơn với nam, cao hơn với nữ và trẻ em). Tác giả cắt mel-spectrogram về **[50, 350] Hz** — chọn có chủ đích "nhằm bao phủ dải F0 của thanh điệu con người," bao gồm rõ ràng cả F0 cao hơn của giọng **nữ và trẻ em**.
- Vùng tần thấp đã cắt được **lưu thành ảnh RGB** và dùng làm đầu vào mô hình. Kích thước ảnh **(225, 225, 3)** được chọn (xem ablation §6).

### 5.2 Kiến trúc ToneNet (Bảng 1)

Một bộ trích đặc trưng CNN 5 lớp + bộ phân loại MLP 3 lớp, ba module:

| Module | Các lớp |
|---|---|
| **Part-1** (đầu vào) | Conv2d(f=5×5, 64 bộ lọc, stride 3) → BatchNorm → MaxPool(3×3, stride 3). Đầu ra 25×25×64. Kernel lớn + stride 3 để giảm chiều + trích đặc trưng thô. |
| **Part-2** (kiểu VGG) | 4× [Conv2d(f=3×3, stride 1) → BatchNorm → MaxPool(2×2, stride 2)], với số bộ lọc **128 → 256 → 256 → 512**. Theo nguyên lý VGGNet "xếp chồng các kernel 3×3 nhỏ thay vì một kernel lớn." Đầu ra 2×2×512. |
| **Flatten** | nối khối conv với MLP. |
| **Part-3** (MLP) | FC-1024 → BatchNorm → FC-1024 → BatchNorm → **FC-4 → SoftMax** (4 thanh). |

> Lưu ý: phần văn xuôi §3 nói số kernel của Part-1 là 64 và conv đầu của Part-2 là 128; abstract/§contributions mô tả nó là "bộ trích đặc trưng CNN 5 lớp hiệu quả + bộ phân loại MLP 3 lớp." Bảng 1 là nguồn chuẩn cho số bộ lọc từng lớp (64 / 128 / 256 / 256 / 512). ≈ (một mâu thuẫn nội bộ: văn xuôi có lúc nói "2×2×512 ở Part-2" khớp với bảng).

**Cấu hình huấn luyện:** hàm kích hoạt **ReLU** (Công thức 1, `f(x)=max(0, wᵀx+b)`); hàm mất mát **categorical cross-entropy**; bộ tối ưu **SGD với momentum + Nesterov**; learning rate cơ sở **0.001**; mini-batch **128**; **50 epochs**. BatchNorm sau mỗi lớp conv (được dẫn là giúp hội tụ nhanh hơn + chống quá khớp).

### 5.3 Khả năng diễn giải

**Grad-CAM** [14] trên lớp conv cuối, hiển thị như một bản đồ nhiệt phủ lên mel-spectrogram đầu vào (Hình 5). Các bản đồ nhiệt xác nhận ToneNet chú ý tới **dải đường nét cao độ sáng** của mỗi thanh — "giống như con người chúng ta về thị giác" — bằng chứng rằng mạng đã học đường nét ngữ điệu chứ không phải một gợi ý giả.

## 6. Thí nghiệm và kết quả

### 6.1 Ablation dải tần × kích thước ảnh (Bảng 2)

Sáu cấu hình: {tần thấp [50,350] Hz, tần đầy đủ [0,8000] Hz} × {(113,113,3), (225,225,3), (449,449,3)}.

| Cấu hình | Độ chính xác % | F1 % | Test loss |
|---|---|---|---|
| tần thấp (113²) | 97.90 | 97.83 | 0.06207 |
| **tần thấp (225²)** | **99.16** | **99.11** | **0.05153** |
| tần thấp (449²) | 99.00 | 98.93 | 0.05312 |
| tần đầy đủ (113²) | 96.86 | 96.68 | 0.08151 |
| tần đầy đủ (225²) | 97.73 | 97.57 | 0.07082 |
| tần đầy đủ (449²) | 97.75 | 97.60 | 0.07011 |

Phát hiện: (a) **vùng cắt tần thấp thắng tần đầy đủ** ở mọi kích thước ảnh (test loss cũng thấp hơn) — loại bỏ dải tần cao vốn không mang thông tin thanh điệu thì có lợi; (b) **(225²) ≈ (449²)** nên chọn ảnh nhỏ hơn để tiết kiệm bộ nhớ/tốc độ; (c) cấu hình tốt nhất = **tần thấp + (225²) = 99.16% acc / 99.11% F1**.

### 6.2 So sánh với các phương pháp trước (Bảng 3)

| Hệ thống | Acc | P | R | F1 | Dữ liệu |
|---|---|---|---|---|---|
| Kalinli [13] | 72.80 | — | — | — | MCCC |
| Chen và cộng sự [1] | 95.53 | 93.51 | 94.63 | 94.06 | MCCS |
| Chen và cộng sự [1] (chạy lại) | 94.45 | — | — | — | SCSC |
| **ToneNet (của chúng tôi)** | **99.16** | **99.08** | **99.14** | **99.11** | **SCSC** |
| ToneNet (của chúng tôi, +nhiễu Gaussian) | **97.07** | **96.81** | **96.85** | **96.83** | SCSC (nhiễu) |
| Chen và cộng sự [1] (+nhiễu Gaussian) | 92.15 | 91.40 | 92.35 | 91.87 | SCSC (nhiễu) |

(Kết luận §5 nhắc lại ToneNet sạch = 99.16 acc / 99.08 P / 99.14 R / 99.11 F1.)

Vì ba baseline dùng các tập dữ liệu khác nhau, tác giả **cài đặt lại Chen và cộng sự [1] trên SCSC** để so sánh công bằng: Chen tụt còn 94.45% trên SCSC, vẫn thấp hơn nhiều so với 99.16% của ToneNet. Dưới **nhiễu Gaussian thêm vào**, ToneNet suy giảm nhẹ nhàng còn 97.07% acc / 96.83% F1, thắng Chen-có-nhiễu (92.15% / 91.87%) khoảng ~5 điểm — đúng tuyên bố bền-với-nhiễu đã thúc đẩy lựa chọn mel-spectrogram.

### 6.3 Ma trận nhầm lẫn (Bảng 4, test sạch)

| thực \ dự đoán | T1 | T2 | T3 | T4 |
|---|---|---|---|---|
| **T1** | 536 | 0 | 1 | 0 |
| **T2** | 0 | 394 | 2 | 0 |
| **T3** | 2 | 7 | 451 | 1 |
| **T4** | 0 | 1 | 2 | 515 |

Gần như hoàn hảo; nhầm lẫn chính là **T3 (thấp-trầm) ↔ T2 (lên)** (7 + 2 lỗi), đúng cặp dễ nhầm về mặt ngôn ngữ học (biến điệu thanh-3 và một phần thanh lên chia sẻ hình dạng đường nét).

## 7. Hạn chế tác giả nêu (ngầm)

Bài báo ngắn và lạc quan; nó không liệt kê hạn chế, nhưng việc đọc làm lộ ra: (1) **chỉ đơn âm tiết** — không có giọng nói liên tục, không có ngữ cảnh đồng-cấu-âm / biến-điệu-thanh (so với bài #36 J-ToneNet nhắm tới tiếng Quan Thoại liên tục); (2) **một register người nói hẹp duy nhất** — 15 thanh niên nam, một kho ngữ liệu, thu phòng thu sạch; không có người nói nữ/trẻ em/cao tuổi thực sự trong dữ liệu mặc dù vùng cắt F0 được thiết kế cho họ; (3) **chỉ kiểm thử nhiễu Gaussian tổng hợp**, không phải dội âm/codec/micro thực tế; (4) **không báo cáo hiệu chỉnh (calibration) / chất lượng xác suất** — chỉ có accuracy/F1; (5) các siêu tham số cắt ảnh ngữ điệu ([50,350] Hz, 64 mel) được tinh chỉnh cho F0 nam trưởng thành và sẽ cần tinh chỉnh lại cho giọng trẻ em.

---

## Deep research — full-PDF read (2026-06-16)

> Các Decision ID bài báo này được đọc để dịch chuyển: **D-A** (backbone bộ mã hóa / trích đặc trưng
> cho modality thoại), **D-D** (nguồn chuyển giao + thước đo cho hồi quy đường nét cao độ / ngữ điệu),
> **D-H** (tập dữ liệu / phương án thay thế). Đọc đối chiếu với phiên bản hội nghị chuẩn của
> ISCA-Archive (`gao19c_interspeech`, *Proc. Interspeech 2019* tr. 3367–3371, DOI
> 10.21437/Interspeech.2019-1483); PDF cục bộ là `pdfs/33-tonenet.pdf`.

### Ghi chú truy cập nguồn

- **Đọc PDF:** toàn văn được trích bằng `pdftotext "docs/papers/pdfs/33-tonenet.pdf" -` (công cụ Read
  không render được PDF trong repo này, theo bộ nhớ dự án). Toàn bộ 5 mục + cả 4 bảng + abstract +
  tài liệu tham khảo được đọc từ đầu tới cuối. Các hình (mel-spectrogram, sơ đồ kiến trúc, bản đồ
  nhiệt Grad-CAM) là ảnh và chỉ được đọc qua chú thích/văn bản xung quanh.
- **Kiểm chứng web:** bốn con số chủ đạo được xác nhận đối chiếu với **phiên bản hội nghị đã xuất
  bản**.
  - Truy vấn: `"ToneNet CNN Tone Classification Mandarin Chinese Interspeech 2019 Gao Sun Yang 99.16% accuracy mel-spectrogram"` → dẫn tới trang ISCA Archive
    `https://www.isca-archive.org/interspeech_2019/gao19c_interspeech.html`.
  - WebFetch trang URL đó xác nhận: **sạch 99.16% acc / 99.11% F1**, **+nhiễu Gaussian 97.07% acc / 96.83% F1**, tập dữ liệu **SCSC**, tác giả Gao/Sun/Yang, trích dẫn "*Proc. Interspeech 2019*, 3367-3371," **DOI 10.21437/Interspeech.2019-1483**. ✔ PDF cục bộ và bản hội nghị khớp chính xác — đây là bài Interspeech camera-ready, không có sai lệch preprint.
- **Chú giải trạng thái con số:** ✔ đã kiểm chứng đối chiếu bản hội nghị / ≈ xấp xỉ hoặc suy ra nội
  bộ / ✖ chưa kiểm chứng.

### Bài báo thực sự làm gì

- **Nhiệm vụ:** phân loại **thanh điệu từ vựng** tiếng Quan Thoại 4 lớp trên các âm tiết đơn cô lập
  (T1 cao-bằng, T2 lên, T3 thấp-trầm, T4 xuống). [§1] ✔ (nhiệm vụ được abstract bản hội nghị xác nhận).
- **Đặc trưng:** một **mel-spectrogram cắt về dải tần thấp [50, 350] Hz** (64 bộ lọc mel, độ dài khung
  2048, bước dịch 16, qua librosa), lưu thành **ảnh RGB (225×225×3)**. Dải cắt được chọn để bao phủ
  F0 người gồm cả dải **nữ và trẻ em**. [§2, §4] ✔ (đặc trưng mel-spectrogram được abstract bản hội
  nghị xác nhận; chi tiết cắt/bước dịch ≈ chỉ từ PDF).
- **Mô hình:** **5 lớp conv (64→128→256→256→512, kiểu VGG xếp 3×3 sau một stem 5×5 stride-3, BatchNorm
  + MaxPool xuyên suốt) + MLP 3 lớp (1024→1024→4) + softmax.** SGD+Nesterov, LR 0.001, batch 128, 50
  epochs, categorical cross-entropy. [Bảng 1, §3, §5.2 ở trên] ✔ (họ kiến trúc được abstract bản hội
  nghị xác nhận: "CNN tùy biến + MLP"; số bộ lọc từng lớp ≈ chỉ từ Bảng 1).
- **Kết quả:** **99.16% acc / 99.11% F1** sạch; **97.07% acc / 96.83% F1** dưới nhiễu Gaussian.
  [Abstract, Bảng 2, Bảng 3, Kết luận] ✔ đã kiểm chứng.
- **Ablation then chốt:** **vùng cắt tần thấp thắng tần đầy đủ ở mọi kích thước ảnh** (vd 99.16 so với
  97.73 ở 225²); (225²) ≈ (449²) nên ảnh nhỏ hơn thắng về chi phí. [Bảng 2] ≈ (bảng nội bộ; con số
  chủ đạo 99.16 là số ✔ bản hội nghị).
- **Đánh bại baseline:** cài lại Chen và cộng sự 2016 [1] trên cùng dữ liệu SCSC → 94.45%, so với
  ToneNet 99.16%; dưới nhiễu ToneNet 97.07% so với Chen 92.15%. [Bảng 3] ≈ (bảng nội bộ).
- **Diễn giải:** các bản đồ nhiệt Grad-CAM cho thấy CNN chú ý tới dải đường nét cao độ sáng — nó học
  ngữ điệu, không phải đường tắt. [§4, Hình 5] ≈.

### Các phần trực tiếp hữu ích cho Pebble (mỗi phần gắn Decision ID)

1. **Spectrogram-dạng-ảnh + CNN 2 chiều thay thế trích xuất F0 tường minh** — toàn bộ luận điểm kiến
   trúc. Với front-end tin nhắn thoại của Pebble, một head thanh điệu/đường nét cao độ **không** cần
   một bộ dò cao độ dễ vỡ; một log-mel spectrogram đưa vào một CNN 2 chiều nhỏ là đủ và bền-với-nhiễu
   hơn. **(D-A)** — một ứng viên *bộ mã hóa ngữ điệu/thanh điệu* cho modality thoại, tách biệt với
   backbone văn bản NeoBERT. **(D-D)** — thiết lập mel-spectrogram (không phải F0 thô) làm đặc trưng
   chuyển giao cho mọi tín hiệu suy từ đường nét cao độ mà Pebble tính (vd một proxy năng lượng/kích
   hoạt từ ngữ điệu).
2. **Vùng cắt tần thấp [50, 350] Hz, có kích cỡ bao gồm F0 trẻ em** — lựa chọn thiết kế đặc trưng đòn
   bẩy cao nhất (tần thấp thắng tần đầy đủ ở mọi nơi; Bảng 2). **(D-D, D-A)** — một cấu hình tiền xử
   lý cụ thể, sao chép được cho một bộ mã hóa ngữ điệu Pebble; dải này *vốn đã* được kích cỡ để gồm F0
   cao hơn của trẻ em, đúng là dân số của Pebble.
3. **Suy giảm nhẹ nhàng dưới nhiễu cộng (97.07% so với 99.16% sạch của người lớn; +5 điểm so với
   baseline MFCC dưới nhiễu)** — bằng chứng thực nghiệm rằng công thức mel-spectrogram-CNN bền với
   loại nhiễu mà micro điện thoại của trẻ sẽ thêm vào. **(D-A, D-G)** — ủng hộ chọn spectrogram-CNN
   thay vì pipeline MFCC/F0 khi chất lượng đầu vào không kiểm soát được, và là điểm dữ liệu sàn-nhiễu
   cho một chính sách recall/ngưỡng trên một head thoại.
4. **Công thức huấn luyện cụ thể cho một CNN spectrogram nhỏ** — xếp 3×3 kiểu VGG, BatchNorm sau mỗi
   conv, SGD+Nesterov LR 0.001, batch 128, 50 epochs, đầu vào (225²). **(D-A)** — một bộ siêu tham số
   khởi đầu đã được chứng minh tốt cho một ablation CNN-ngữ-điệu của Pebble, tránh tìm kiếm mù.
5. **Grad-CAM làm bằng chứng kiểm chứng rằng một CNN spectrogram đã học đường nét, không phải một giả
   tượng** — **(D-A, D-G)** — một kiểm tra tỉnh táo rẻ, công bố được mà Pebble có thể tái dùng để cho
   thấy một head thoại chú ý tới ngữ điệu chứ không phải danh tính người nói/kênh truyền.
6. **Ghi chú thay thế tập dữ liệu** — SCSC thuộc thể chế/đóng; các kho thanh điệu *mở* mà Pebble đã
   theo dõi (AISHELL-1, THCHS-30 trong `data/voice/external/`, và **VIVOS** cho tiếng Việt) là các phương án
   tái lập được. **(D-H)** — nếu Pebble xây một probe thanh điệu/ngữ điệu, huấn luyện trên các kho mở,
   trích dẫn ToneNet cho phương pháp, không phải cho dữ liệu.

### Mỗi phần giúp Pebble thành công như thế nào

- **Thiết kế front-end thoại (1) → một module `prosody_cnn`.** Nếu/khi Pebble nạp tin nhắn thoại, xây
  một CNN 2 chiều nhỏ trên log-mel spectrogram làm một *bộ mã hóa ngôn ngữ-cận biên* nuôi cùng bộ
  head đa-nhiệm như nhánh văn bản. **Không** ship một bộ dò F0/cao-độ tường minh — ToneNet là trích
  dẫn rằng điều đó vừa không cần thiết vừa dễ vỡ hơn. Hành động: một thí nghiệm `voice/prosody_cnn.py`
  phản chiếu khối Bảng 1, đầu ra pool về một embedding cố định, nối với embedding văn bản NeoBERT
  trước các head.
- **Vùng cắt cỡ trẻ em (2) → cấu hình tiền xử lý.** Áp dụng **vùng cắt dải thấp [50, 350] Hz, 64 bộ
  lọc mel** làm mặc định cho bộ mã hóa ngữ điệu, và **tinh chỉnh cận trên lên cao hơn** cho giọng trẻ
  em (F0 trẻ em thường vượt 350 Hz; ToneNet cỡ dải cho nam người lớn + nữ + "trẻ em" nhưng *dữ liệu*
  của nó chỉ là nam người lớn — nên coi 350 Hz là một sàn để nâng, không phải trần). Hành động: một
  núm cấu hình `prosody.freq_band=[50, 500]` và một ablation quét cận trên trên một slice giọng trẻ
  em.
- **Bền với nhiễu (3) → câu chuyện recall của head thoại.** Đầu vào của Pebble là âm thanh điện thoại
  không kiểm soát. Con số +nhiễu-Gaussian của ToneNet (97.07%, chỉ −2 điểm so với sạch, và +5 điểm so
  với MFCC) là bằng chứng để dự trù một khoảng cách sạch→nhiễu nhỏ trên một head ngữ điệu và để ưu
  tiên công thức spectrogram thay vì các đặc trưng tay openSMILE/eGeMAPS (#29/#30) khi độ bền quan
  trọng hơn khả năng diễn giải. Hành động: thêm tăng cường Gaussian + dội âm vào huấn luyện
  prosody-CNN và báo cáo độ chênh sạch/nhiễu.
- **Công thức huấn luyện (4) → bỏ qua tìm kiếm mù.** Gieo ablation prosody-CNN bằng các siêu tham số
  của ToneNet (SGD+Nesterov, LR 0.001, BN-khắp-nơi, batch 128) trước khi thử thứ gì cầu kỳ hơn; đó là
  một cấu hình 99%+ đã được ghi nhận trên một bài toán đường nét 4 lớp.
- **Grad-CAM (5) → slide kiểm chứng công bố được.** Chạy Grad-CAM (hoặc một tương tự attention-rollout)
  trên prosody-CNN để cho thấy nó sáng lên trên đường nét cao độ, không phải trên giả tượng
  kênh/người nói — đúng bằng chứng xây-niềm-tin Pebble cần cho bất kỳ head modality mới nào.
- **Thay thế dữ liệu mở (6) → tính tái lập.** Vì SCSC đóng, bất kỳ probe ngữ điệu Pebble nào cũng phải
  huấn luyện trên AISHELL-1 / THCHS-30 / VIVOS. Điều này giữ pipeline tái lập được và sạch-giấy-phép
  (THCHS-30/AISHELL-1 Apache-2.0; VIVOS là CC-BY-NC-SA → chỉ nghiên cứu, không deploy).

### Lăng kính sức khỏe tâm thần trẻ em

- **Vùng cắt dải tần là lựa chọn thiết kế nhận-thức-trẻ-em duy nhất, và dữ liệu không hậu thuẫn nó.**
  ToneNet cỡ rõ ràng [50, 350] Hz "để bao phủ ... F0 của nữ và trẻ em," và **tài trợ của nó là một dự
  án đánh giá huấn luyện giọng nói Quan Thoại trẻ em (HG1711-1)**. *Nhưng kho SCSC chỉ là 15 thanh
  niên nam.* Vậy nên sự liên quan tới trẻ em của bài báo là **khát vọng, không được kiểm chứng**:
  phương pháp được thiết kế với trẻ em trong đầu, nhưng đánh giá không hề bao gồm một giọng trẻ em
  nào. Với Pebble đây vừa là cờ đỏ vừa là cơ hội — dải F0-trẻ-em phải được tinh chỉnh lại theo thực
  nghiệm (F0 trẻ em thường 250–500 Hz, vượt trần 350 Hz của ToneNet), và một slice đánh giá giọng trẻ
  em là một đóng góp thực sự mà chưa ai trong tập thoại này tạo ra.
- **Phân loại thanh điệu ≠ cảm xúc/mức độ — mượn *hệ thống ống nước*, không mượn *nhãn*.** Các head
  của Pebble là emotion (12 nhãn) và severity (hồi quy). ToneNet phân loại thanh điệu từ vựng, một
  phạm trù *ngôn ngữ*, không phải cảm xúc. Việc chuyển giao chỉ ở mức **đặc trưng + bộ mã hóa**
  (mel-spectrogram → CNN 2 chiều → embedding đã pool); khả năng *đọc-đường-nét* mới là thứ Pebble tái
  dùng để suy ra các gợi ý kích hoạt/năng lượng từ ngữ điệu, **không phải** head softmax-trên-4-thanh
  của ToneNet.
- **Sai lệch register & kênh.** SCSC thu phòng thu sạch, 16 kHz, đơn âm tiết, một phương ngữ/giọng.
  Tin nhắn thoại Pebble là ngoài-thực-địa, nén codec, liên tục, đa giọng, register trẻ em. Con số sạch
  99.16% **sẽ không** chuyển giao thành một con số độ chính xác; chỉ câu chuyện *tương đối* về độ bền
  (spectrogram thắng F0/MFCC dưới nhiễu) là chuyển giao được. Nói thẳng: **một con số thanh điệu phòng
  thu nam-người-lớn đã kiểm chứng không dự đoán hiệu năng giọng-trẻ-em ngoài-thực-địa.**
- **Quyền riêng tư/đạo đức.** Giọng nói là sinh trắc và có thể tái-định-danh; giọng trẻ em gấp đôi như
  vậy. Một module thoại Pebble cần đồng thuận tường minh, xử lý trên-thiết-bị hoặc truy-cập-có-kiểm-
  soát, và nên suy ra *các đặc trưng ngữ điệu chiều thấp* (năng lượng đường nét, không phải âm thanh
  thô lưu trữ) bất cứ khi nào có thể — bước "lưu vùng cắt tần thấp thành ảnh" của ToneNet, tiện thay,
  vốn đã là một biểu diễn mất mát loại bỏ nội dung lời nói có thể hiểu được (nó chỉ giữ [50,350] Hz),
  một tính chất thân-thiện-riêng-tư đáng giữ.

### Hạn chế & câu hỏi mở cho Pebble

- **Mâu thuẫn-hoặc-khoảng-trống #1 (so với bài #36 J-ToneNet và #34 Lugosch CTC):** ToneNet **chỉ**
  làm việc trên các âm tiết đơn cô lập và (theo Bảng 4) các lỗi còn lại của nó đúng là cặp đường nét
  T2↔T3 mà **ngữ cảnh giọng nói liên tục** sẽ làm rõ. J-ToneNet (#36) và Lugosch (#34) nhắm tới tiếng
  Quan Thoại *liên tục* nơi đồng-cấu-âm và biến-điệu-thanh chiếm ưu thế. Tin nhắn thoại Pebble là
  giọng nói liên tục, đối thoại, mang cảm xúc — nên **con số đơn-âm-tiết 99.16% của ToneNet là một cận
  trên thổi phồng hiệu năng thực**; các bài giọng-nói-liên-tục là thước đo trung thực hơn. Đừng trích
  99.16% như một con số đạt được của Pebble.
- **Mâu thuẫn-hoặc-khoảng-trống #2 (so với dòng đặc-trưng-tay #29 openSMILE / #30 eGeMAPS):** ToneNet
  lập luận *chống* các đặc trưng âm học tường minh (F0/MFCC) để ủng hộ một CNN học trên spectrogram;
  dòng eGeMAPS/openSMILE lập luận *ủng hộ* một bộ đặc-trưng-tay gọn, diễn-giải-được, đã-kiểm-chứng-lâm-
  sàng. Với tín hiệu ngữ điệu sức-khỏe-tâm-thần của Pebble đây là một căng thẳng **học-vs-thủ-công**
  chưa giải: ToneNet thắng về độ chính xác thô và độ bền nhiễu, eGeMAPS thắng về khả năng diễn giải,
  độ ổn định dữ-liệu-nhỏ, và một bề dày thành tích trong công tác giọng nói cảm xúc/lâm sàng. Pebble
  phải chọn (hoặc hợp nhất) có chủ đích — riêng bài này không giải quyết được.
- **Không calibration, không giọng liên tục, không nhiễu thực, không giọng trẻ em/nữ trong dữ liệu,
  không kiểm tra tổng quát hóa người nói.** Mỗi điều trong số này là một khoảng trống Pebble phải khép
  lại trước khi một head thoại có thể được tin cậy trong một pipeline an toàn hướng-trẻ-em.
- **Câu hỏi mở — một head thanh điệu/ngữ điệu có nằm trên lộ trình v1 của Pebble không?** Theo
  `docs/decisions.md`, v1 chỉ huấn luyện văn bản `emotion` + `severity`; thoại là một modality cấp
  luận án, không phải một giao phẩm v1. Do đó ToneNet là **bằng chứng nhìn-về-phía-trước cho một nhánh
  thoại v2 (D-A/D-D)**, không phải một vật cản v1. Đóng góp cụ thể của nó cho v1 là hẹp: nó kiểm chứng
  "mel-spectrogram → CNN 2 chiều nhỏ" là kiến trúc để prototype đầu tiên khi thoại xuất hiện.
- **Câu hỏi mở — truy cập SCSC.** SCSC thuộc thể chế (CASS Institute of Linguistics) và không nằm
  trong tập dữ liệu mở của Pebble; liệu nó có lấy được hay không là chưa kiểm chứng. Mặc định dùng
  AISHELL-1 / THCHS-30 / VIVOS làm các phương án thay thế tái lập được **(D-H)**.
