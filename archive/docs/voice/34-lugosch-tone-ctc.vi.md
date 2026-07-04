# Bài báo 34 — Nhận dạng Thanh điệu bằng Lifter và CTC (Tone Recognition Using Lifters and CTC)

## 1. Thông tin thư mục

**Tiêu đề:** Tone Recognition Using Lifters and CTC

**Tác giả:** Loren Lugosch, Vikrant Singh Tomar (Fluent.ai Inc., Montréal, Québec, Canada).

**Năm / nơi công bố:** Interspeech 2018 (Hyderabad, Ấn Độ), trang 2305–2309. DOI 10.21437/Interspeech.2018-2293. Bản tiền in: arXiv:1807.02465v1 [eess.AS], 6/7/2018.

**Từ khóa (nguyên văn):** "tone recognition, tonal languages, speech recognition, cepstrogram, sequence processing, deep learning, CTC".

**Tóm tắt một dòng:** Một front-end khả huấn luyện gồm cepstrogram + CNN ("lifter") đưa vào một đầu (head) BiGRU-CTC, nhận dạng *chuỗi* thanh điệu tiếng Quan Thoại trong các phát ngôn *liên tục* theo kiểu end-to-end (không cần forced alignment, không cần phân đoạn âm tiết), đạt tone error rate (TER) 11.7% trên AISHELL-1 — kết quả tốt nhất từng được báo cáo cho nhận dạng thanh điệu trong tiếng Quan Thoại liên tục tại thời điểm đó.

## 2. Vì sao bài báo này nằm trong tập của Pebble (góc nhìn voice-message)

Luận điểm của Pebble bao gồm một **phương thức (modality) voice-message**: trẻ em gửi tin nhắn thoại, và Pebble phải trích xuất tín hiệu mang cảm xúc/ngữ điệu (prosody) từ âm thanh *thực, liên tục, nói tự nhiên* — chứ không phải các âm tiết tách rời, phát âm cẩn thận. Nhận dạng thanh điệu (mẫu hình cao độ - pitch pattern) là nhiệm vụ có giám sát đầy đủ gần nhất với việc "trích xuất một chuỗi nhãn ngữ điệu từ một phát ngôn thực". Bài báo này quan trọng với Pebble vì ba lý do:

1. **Nó nhắm tới ngôn ngữ nói liên tục, không phải âm tiết tách rời.** Phần lớn các công trình thanh điệu trước đây (ví dụ Chen et al. 2016, 4.5% TER) phân loại từng âm tiết được phát âm cẩn thận một lần một. Chế độ đó không tồn tại trong một tin nhắn thoại. Lugosch & Tomar cố ý giải bài toán khó hơn, nơi *ranh giới thanh điệu là chưa biết* — đúng bối cảnh của Pebble.
2. **Nó là end-to-end với một hàm mất mát ở cấp chuỗi (CTC)**, nên **không cần nhãn cấp khung (frame-level) và không cần forced alignment**. Pebble không thể có nhãn cảm xúc căn chỉnh theo khung trên tin nhắn thoại của trẻ em; một head kiểu CTC ở cấp chuỗi là chế độ nhãn duy nhất mở rộng được tới âm thanh gán nhãn bạc (silver-labelled).
3. **Front-end "lifter" là một đặc trưng pitch học được, tối ưu cho phân biệt** — một khuôn mẫu để thay thế các đặc trưng ngữ điệu thủ công (F0/PoV) bằng các đặc trưng mà mạng tự học cho nhiệm vụ phía dưới. Việc trích xuất tín hiệu ngữ điệu/năng lượng của Pebble đối mặt cùng lựa chọn đặc trưng-thủ-công-hay-học.

## 3. Động cơ của bài toán

Thanh điệu mang tính phân biệt nghĩa về mặt âm vị học trong nhiều ngôn ngữ: trong tiếng Quan Thoại, "mẹ" (mā), "gai dầu" (má), "ngựa" (mǎ), và "mắng" (mà) cùng hai âm vị và chỉ khác nhau *duy nhất* ở thanh điệu. Do đó ASR cho ngôn ngữ thanh điệu không thể chỉ dựa vào âm vị (phone).

Các đặc trưng ASR chuẩn (MFCC, FBANK, PLP) không mang thông tin cao độ (pitch), nên các bộ nhận dạng thanh điệu hiện đại **thêm các đặc trưng cao độ quyết-định-cứng (hard-decision pitch features, HDPF)** — một ước lượng F0 cộng xác suất hữu thanh (probability-of-voicing, PoV) cho mỗi khung [Ghahremani et al. 2014]. Giả thuyết trung tâm của tác giả: **HDPF vứt bỏ thông tin.** Bằng phép loại suy với nhận dạng âm vị — nơi các bộ nhận dạng không ước lượng tường minh formant nhưng vẫn ngầm học chúng và hơn thế — một mô hình tiêu thụ *toàn bộ* tín hiệu có thể phân biệt tốt hơn một mô hình chỉ được cho bản tóm tắt cao độ có động cơ ngôn ngữ học. Họ trích dẫn Ryant et al. 2014, nơi một bộ nhận dạng chỉ-MFCC "vượt trội dễ dàng" một bộ nhận dạng F0+biên độ, làm bằng chứng trực tiếp rằng F0 không phải đặc trưng thanh điệu tối ưu.

Động cơ thứ hai: **khả năng tái lập (reproducibility).** Công trình thanh điệu trước dùng các kho ngữ liệu đắt tiền/nội bộ (HKUST/MTS, CALLHOME), cản trở so sánh khách quan. Họ dùng **AISHELL-1**, một kho ngữ liệu LVCSR tải về miễn phí (openslr.org/33), nên kết quả có thể tái lập.

## 4. Vị trí trong tài liệu

Ba mạch được đối chiếu:

- **Bộ nhận dạng dựa trên HDPF.** Huang et al. 2000 (F0 + delta-F0 + mức độ hữu thanh → GMM); Lei et al. 2006 (đường F0 + thời lượng âm tiết → MLP); bộ nhận dạng RNN dùng MFCC+HDPF [Huang et al. 2017]; mô hình âm-vị-có-thanh [Liu et al. 2015; Metze et al. 2013].
- **Các đặc trưng phổ thay thế.** Li et al. 2011 và Kalinli 2011 (lọc Gabor trên spectrogram → MLP cấp khung, cần forced alignment); Deep Speech 2 [Amodei et al. 2016] (spectrogram thô → ký tự Trung, pitch học ngầm).
- **Bộ phân loại CNN âm-tiết-tách-rời.** Chen et al. 2016 (cửa sổ MFCC → CNN cho từng âm tiết, 4.5% TER trên âm tiết tách rời).

Các lỗ hổng được nêu: (1) đặc trưng HDPF/dẫn xuất vứt bỏ thông tin hữu ích; (2) cách tiếp cận cấp khung cần forced alignment hoặc gán nhãn thủ công — "tẻ nhạt và đắt đỏ". Giải pháp: một đầu vào **cepstrogram** (không phải spectrogram) để từ đó *học* đặc trưng, cộng một tiêu chí **CTC cấp chuỗi** loại bỏ bước căn chỉnh.

## 5. Phương pháp

Bộ nhận dạng là một mạng nơ-ron với ba tầng (Hình 1): module tiền xử lý → mạng tích chập ("lifter") → mạng hồi quy (BiGRU-CTC), huấn luyện end-to-end bằng SGD.

### 5.1 Tiền xử lý — cepstrogram

Tín hiệu được chia khung thành các cửa sổ chồng lấp ngắn (25 ms với bước nhảy 10 ms), mỗi cửa sổ nhân với một **cửa sổ Hamming** (độ dài 512). Với mỗi khung đã cửa-sổ-hóa `x`, **cepstrum** được tính:

```
cepstrum(x) = IDFT( log |DFT(x)| )                                   (Pt. 2)
```

Quan trọng, **không áp dụng filterbank Mel** — việc làm mượt của Mel sẽ làm mờ các đỉnh tuần hoàn của phổ, che giấu pitch. Phổ thô được dùng. Cepstrogram là ghép nối tất cả các cepstra theo thời gian. Động cơ (§3.1): trong cepstrogram, **cao độ của một giọng nói xuất hiện như một đỉnh đơn cục bộ tại mỗi bước thời gian** (Hình 2), trong khi ở spectrogram pitch là một *mẫu hình hài âm toàn cục* — khó học hơn nhiều. Cepstrogram, giống spectrogram, giữ lại tất cả thông tin trừ pha.

### 5.2 Mạng tích chập — "lifter"

Ba tầng tích chập với ReLU và max-pooling. Tác giả gọi các bộ lọc conv là **lifter** và các bản đồ đặc trưng đầu ra là **đặc trưng lifter (lifter features, LF)**, vì tích chập trong miền cepstral ("quefrency") *chính là* liftering. Lý do: nhận dạng thanh điệu **bất biến với phép tịnh tiến** theo thời gian và tần số (một giai điệu vẫn vậy dù hát ở thời điểm khác hay tông khác), nên tích chập + pooling trích xuất các mẫu hình bất biến tịnh tiến và hạ mẫu mạnh cả thời gian lẫn quefrency — cải thiện tính bất biến và rút ngắn chuỗi mà RNN phải xử lý. Theo Bảng 1, mỗi tầng conv là `11×11, 16 lifter, stride 1`, mỗi pool là `4×4 max, stride 2`, đều ReLU. Một dropout 50% theo sau khối conv. LF (bản đồ của tầng conv cuối) được xếp chồng theo từng bước thời gian thành một bản đồ 2D cho RNN.

### 5.3 Mạng hồi quy — BiGRU + CTC

Một **GRU hai chiều (BiGRU) với 128 đơn vị ẩn mỗi chiều** dịch chuỗi LF thành chuỗi thanh điệu qua **CTC** [Graves et al. 2006]. CTC loại bỏ bước căn chỉnh/phân đoạn: huấn luyện chỉ cần *chuỗi nhãn thanh điệu*, không cần nhãn cấp khung. CTC "lý tưởng để mô hình hóa các chuỗi sự kiện trong đó cùng một sự kiện có thể xuất hiện nhiều lần liên tiếp" — đúng như chuỗi thanh điệu. Tầng affine đầu ra có **6 đầu ra: 5 thanh điệu Quan Thoại + 1 nhãn "blank" của CTC**.

### 5.4 Huấn luyện & giải mã (§4.1)

- Mất mát: mất mát CTC chuẩn `−log p(Y|X)`, tối ưu bằng SGD.
- Bộ tối ưu: **Adam**, LR khởi tạo **0.001**, gradient clipping; LR **giảm một nửa** vào cuối epoch nếu mất mát trên dev tăng. **20 epoch**.
- **SortaGrad** học theo chương trình (curriculum) [Amodei et al. 2016]: epoch đầu lấy chuỗi theo thứ tự độ dài, sau đó ngẫu nhiên.
- Giải mã: greedy. Một beam search rất rộng chỉ cải thiện TER 0.1% so với greedy cho mọi bộ nhận dạng, nên báo cáo kết quả greedy.
- Công cụ: recipe **Kaldi** cho AISHELL-1 để chuẩn bị kho ngữ liệu và tính MFCC 13 chiều + HDPF 3 chiều (cho Baseline 1), chuẩn hóa theo từng phát ngôn về trung bình 0 / phương sai đơn vị.

### 5.5 Baseline / ablation

- **Baseline 1:** RNN-CTC trên `MFCC + HDPF`. Được cho *thêm một* tầng hồi quy với dropout và **160 đơn vị ẩn/tầng** — cố ý *nhiều tham số hơn mô hình đề xuất* để tạo lợi thế cho nó.
- **Baseline 2:** giống hệt mô hình đề xuất nhưng **25 hệ số cepstral đầu tiên bị đặt về 0** (giữ 231 trong 256) — tức chỉ giữ **cepstrum thời-gian-cao (high-time, HT)** (kích thích thanh môn/pitch), xóa thông tin thời-gian-thấp (đường thanh - vocal-tract). Kiểm tra tầm quan trọng của thông tin "phi-pitch".
- **Bộ nhận dạng dựa trên spectrogram:** mô hình đề xuất bỏ bước IFFT (đầu vào spectrogram). **Nó không thể học** và bị loại khỏi bảng — bằng chứng thực nghiệm rằng cepstrogram là đầu vào đúng.

## 6. Dữ liệu — AISHELL-1 (§4.1)

| Tập | Phát ngôn | Người nói | Giờ |
|---|---|---|---|
| Train | 120,098 | 340 | 150 |
| Dev | 14,326 | 40 | 10 |
| Test | 7,176 | 20 | 5 |
| **Tổng** | — | **400** | **165** |

165 giờ **giọng sạch**, 400 người nói khắp Trung Quốc (47% nam / 53% nữ), môi trường không nhiễu, 16-bit, lấy mẫu lại về 16 kHz. Miễn phí tại openslr.org/33.

## 7. Kết quả

**Tiêu điểm (Bảng 2):** bộ nhận dạng đề xuất `CG → CNN → RNN + CTC` đạt **TER 11.7%** — tốt nhất bảng với khoảng cách lớn, và "theo hiểu biết của chúng tôi là tỉ lệ lỗi tốt nhất từng báo cáo cho nhận dạng thanh điệu trong tiếng Quan Thoại liên tục".

| Phương pháp | Mô hình & đặc trưng đầu vào | TER |
|---|---|---|
| Lei et al. | HDPF → MLP | 23.8% |
| Kalinli | Spectrogram → Gabor → MLP | 21.0% |
| Huang et al. | HDPF → GMM | 19.0% |
| Huang et al. | MFCC + HDPF → RNN | 17.1% |
| Ryant et al. | MFCC → MLP | 15.6% |
| **Baseline 1** | MFCC + HDPF → RNN + CTC | 18.1% |
| **Baseline 2** | HT cepstrogram → CNN → RNN + CTC | 15.1% |
| **Đề xuất** | cepstrogram → CNN → RNN + CTC | **11.7%** |

Tác giả lưu ý "không hoàn toàn công bằng" khi so sánh giữa các tập dữ liệu khác nhau của tài liệu; so sánh có kiểm soát là **Đề xuất (11.7%) vs Baseline 1 (18.1%) vs Baseline 2 (15.1%)** trên cùng một tách của AISHELL-1. Baseline 1 là tương đồng gần nhất với Huang et al. 2017 — nhưng lưu ý RNN của họ phân loại từng *âm tiết riêng* (ranh giới được cho), trong khi mô hình đề xuất *không nhận được vị trí thanh điệu* và phải học từ chuỗi thanh điệu thôi: một bài toán khó hơn hẳn, vậy mà vẫn thắng.

**Phân tích lỗi (Bảng 3):** mô hình đề xuất tạo ra hơi *nhiều hơn* lỗi chèn (insertions 544 vs 467) nhưng ít hơn nhiều lỗi xóa (deletions 1,382 vs 4,934) và lỗi thay thế (substitutions 21,854 vs 31,459) so với Baseline 1.

**Độ chính xác theo từng thanh điệu (Bảng 4):**

| | Thanh 0 | Thanh 1 | Thanh 2 | Thanh 3 | Thanh 4 |
|---|---|---|---|---|---|
| Baseline 1 | 77.2% | 81.7% | 88.1% | 69.5% | 85.7% |
| Đề xuất | 73.6% | 90.6% | 88.9% | **82.9%** | 91.9% |

Cả hai đều chật vật với **Thanh 0** (thanh trung tính - neutral tone). **Thanh 3** khó (thường nhầm với Thanh 2 do **tone sandhi** — một chuỗi thanh-3–thanh-3 /3,3/ thể hiện thành [2,3]; khi đã hiện thực hóa, /3,3/ và /2,3/ không thể phân biệt về mặt âm học và chỉ một **mô hình ngôn ngữ** mới giải được). Mô hình LF cải thiện Thanh 3 rõ rệt (69.5% → 82.9%).

**Hai "đề cập danh dự" (§4.2.1):**
- Lei et al.: trích thanh điệu từ một *bản phiên âm ASR đầy đủ* cho **9.3% TER** so với 23.8% chỉ-âm-học — vì mô hình ngôn ngữ sửa một số lỗi thanh ("gọi mẹ tôi" > "gọi cây gai dầu của tôi"). Bài này nghiên cứu **mô hình thanh điệu thuần âm học**, huấn luyện chỉ trên nhãn thanh điệu.
- Chen et al. 2016: **4.5% TER** nhưng trên *âm tiết tách rời* — một nhiệm vụ dễ hơn (phát âm cẩn thận; thanh tách rời một phần có thể phục hồi từ *thời lượng* âm tiết, trong khi thanh trong lời nói liên tục có thời lượng gần như bằng nhau).

## Deep research — full-PDF read (2026-06-16)

> Đã đọc toàn bộ PDF cục bộ `pdfs/34-lugosch-tone-ctc.pdf` (arXiv:1807.02465v1, 6/7/2018) từ đầu đến cuối —
> tóm tắt, cả năm mục, Phương trình 1–2, Hình 1–2, và cả bốn bảng. Bản đã công bố là Interspeech 2018,
> trang 2305–2309, DOI 10.21437/Interspeech.2018-2293; bản tiền in arXiv và bản ISCA giống hệt nội dung
> (cùng khối tác giả, cùng số liệu), nên không phát sinh xung đột bản-công-bố-vs-tiền-in. Các số bên dưới
> được gắn nhãn ✔ đã kiểm chứng đối chiếu metadata nơi công bố + văn bản arXiv, ≈ gần đúng, hoặc
> ✖ chưa kiểm chứng.

### Ghi chú về truy cập nguồn

- Trích PDF bằng `pdftotext "docs/papers/pdfs/34-lugosch-tone-ctc.pdf" -`; đọc toàn văn bao gồm các Bảng 1–4 (hơi méo nhưng đọc được). Mojibake trong bản trích thô ("Montre�al") được khôi phục theo ngữ cảnh.
- Kiểm chứng nguồn gốc/nơi công bố:
  - Truy vấn `Lugosch Tomar "Tone recognition using lifters and CTC" Interspeech 2018 tone error rate 11.7% AISHELL-1` → trang ISCA Archive `https://www.isca-archive.org/interspeech_2018/lugosch18_interspeech.html` xác nhận **Interspeech 2018, trang 2305–2309, DOI 10.21437/Interspeech.2018-2293, AISHELL-1**. ✔
  - Tóm tắt ISCA chứng thực *phương pháp* (cepstrogram → CNN → CTC) và *tập dữ liệu* (AISHELL-1) và tuyên bố định tính ("vượt trội các kỹ thuật hiện có về TER"); nó **không** in con số 11.7% trong đoạn HTML. Các giá trị số (11.7% / 15.1% / 18.1% / Bảng 1–4) lấy từ toàn văn arXiv, vốn là cùng một bài. Trạng thái cho các số: ✔ cho TER tiêu điểm và phần tách dữ liệu (đối chiếu với đặc tả công bố của AISHELL-1); ≈ cho các phần trăm theo từng thanh điệu (nguồn đơn, bảng tiền in, rủi ro OCR nhẹ nhưng nhất quán nội tại).
  - Trang arXiv `https://arxiv.org/abs/1807.02465` và trang công bố của tác giả `https://lorenlugosch.github.io/publication/2018-09-01-tone` chứng thực tác giả, năm, và khung lifter/CTC. ✔
- Phần tách AISHELL-1 (120,098 / 14,326 / 7,176 phát ngôn; 340/40/20 người nói; 150/10/5 giờ; tổng 165 giờ, 400 người nói) ✔ — khớp với đặc tả công bố của chính kho ngữ liệu (Bu et al. 2017, arXiv:1709.05522 / openslr.org/33), một kiểm chứng độc lập cho bảng dữ liệu của bài báo.

### Bài báo thực sự làm gì

- **Nhiệm vụ.** Dự đoán chuỗi thanh điệu Quan Thoại trong lời nói *liên tục*: đầu vào dạng sóng `X`, đầu ra chuỗi thanh điệu `Y` trên bảng chữ cái 5 thanh; chỉ số **TER = Levenshtein (I+D+S)/U** (Pt. 1). ✔
- **Front-end (đặc trưng pitch học được).** Dạng sóng → khung Hamming 25 ms/10 ms → cepstrum `IDFT(log|DFT(x)|)` với **không Mel filterbank** (giữ đỉnh pitch) → cepstrogram → **3× tầng conv ("lifter"), mỗi tầng 11×11, 16 bộ lọc, stride 1, + max-pool 4×4 stride 2, ReLU, rồi dropout 50%** (Bảng 1). ✔
- **Back-end.** **BiGRU, 128 đơn vị/chiều → CTC, 6 đầu ra (5 thanh + blank)** (Bảng 1, §3.3). ✔
- **Huấn luyện.** Mất mát CTC `−log p(Y|X)`, Adam, LR 0.001 với giảm-một-nửa khi dev chững lại, gradient clipping, 20 epoch, curriculum độ-dài SortaGrad, giải mã greedy (beam chỉ giúp 0.1%). ✔ Recipe Kaldi để chuẩn bị kho ngữ liệu + baseline MFCC 13 chiều + HDPF 3 chiều, CMVN theo từng phát ngôn. ✔
- **Kết quả tiêu điểm.** **TER 11.7%** (Bảng 2), tốt nhất cho nhận dạng thanh điệu Quan Thoại liên tục; thắng Baseline 1 (MFCC+HDPF→RNN-CTC, 18.1%) và Baseline 2 (chỉ cepstrogram thời-gian-cao, 15.1%) trên *cùng* phần tách. ✔ (tiêu điểm) / ≈ (số thập phân baseline, bảng nguồn đơn)
- **Kết quả ablation.** (a) Đầu vào spectrogram **không học được** → cepstrogram là biểu diễn đúng. (b) 15.1% của Baseline 2 (so với 11.7% đề xuất) cho thấy **thông tin cepstral thời-gian-thấp "phi-pitch" thật sự hữu ích** cho thanh điệu — khẳng định giả thuyết cốt lõi rằng HDPF vứt bỏ tín hiệu hữu ích. (c) Phân tích lỗi: mô hình đánh đổi thêm vài lỗi chèn lấy ít hơn nhiều lỗi xóa/thay thế (Bảng 3). (d) Theo từng thanh: thắng lớn ở Thanh 3 (69.5%→82.9%), khó còn lại ở Thanh 0 trung tính; nhầm Thanh-3/Thanh-2 do **tone sandhi**, chỉ sửa được bằng mô hình ngôn ngữ. ✔ / ≈

### Các phần trực tiếp hữu ích cho Pebble

1. **End-to-end CTC trên một front-end học được, không cần căn chỉnh khung** (§3.3, §5) — **[D-A, D-B]**. Toàn bộ kiến trúc là "đặc trưng học được → mô hình chuỗi → mất mát cấp chuỗi", huấn luyện từ *chỉ nhãn chuỗi*. Với head voice-message của Pebble đây là chế độ nhãn mở rộng được: bạn không bao giờ có nhãn cảm xúc căn chỉnh theo khung trên âm thanh trẻ em, nên một tiêu chí chuỗi CTC (hoặc kiểu CTC) là cơ chế cho phép một *chuỗi* nhãn bạc (ví dụ nhãn ngữ điệu/cảm xúc theo từng phát ngôn) giám sát một encoder âm thanh liên tục. Gắn với D-A (lựa chọn encoder phương thức phải hỗ trợ head CTC/chuỗi) và D-B (CTC tự nó là cách xử lý mục tiêu độ-dài-thay-đổi, sự-kiện-lặp-lại mà không cần cân bằng mất mát — liên quan khi chọn cách mất mát của head voice hòa với các head text MTL).
2. **Cepstrogram (cepstrum từ phổ thô, không Mel) làm đầu vào giữ-pitch** (§3.1, Pt. 2) — **[D-D]**. Tín hiệu `energy`/ngữ điệu của Pebble là heuristic ở v1 nhưng là ứng viên v2 cho một hồi quy học được. Bằng chứng của bài rằng **làm mượt Mel phá hủy đỉnh pitch** và **cepstrogram định vị pitch về một đỉnh/bước thời gian** là một chỉ dẫn kỹ thuật đặc trưng cụ thể: nếu Pebble từng học một head ngữ điệu/năng lượng từ tin nhắn thoại, hãy cho nó một cepstrogram (không Mel) hoặc một kênh pitch tường minh, chứ không phải log-Mel thuần. D-D là quyết định nguồn-hồi-quy/đặc-trưng.
3. **CNN "lifter" như một thay thế học được cho đặc trưng F0/PoV thủ công** (§3.2, §5.5 Baseline 1) — **[D-D, D-F]**. Kết quả có kiểm soát — đặc trưng cepstral học được (11.7%) thắng MFCC+HDPF thủ công (18.1%) *dù baseline có nhiều tham số hơn* — là bằng chứng trực tiếp cho **học thay vì thủ công** đối với đặc trưng ngữ điệu. Với Pebble: một front-end âm thanh học được (hoặc một encoder âm thanh tiền-huấn-luyện thích nghi miền) nên vượt việc bơm các bản tóm tắt F0/năng lượng trích thủ công vào head. Ánh xạ tới D-D (nguồn đặc-trưng/transfer) và D-F bằng phép loại suy (một lượt front-end tự-giám-sát/thích-nghi-miền trước fine-tune head).
4. **Siêu tham số cụ thể, tái lập được cho một head CTC thanh-điệu/ngữ-điệu nhỏ** (Bảng 1, §4.1) — **[D-A, D-E]**. 3 tầng conv (11×11/16/s1) + pool 4×4, dropout 50%, BiGRU-128, Adam LR 0.001 với giảm-một-nửa-khi-chững, 20 epoch, SortaGrad, giải mã greedy. Đây là một recipe sẵn-dùng mà Pebble có thể nhân bản cho một nguyên mẫu ngữ-điệu/cảm-xúc voice-message đầu tiên trên một kho ngữ liệu thanh-điệu/cảm-xúc công khai trước khi chạm âm thanh trẻ em. D-E là quyết định fine-tuning theo giai đoạn / lịch học (giảm-một-nửa LR + curriculum độ-dài dùng lại trực tiếp).
5. **AISHELL-1 như một kho ngữ liệu âm thanh miễn phí, lớn, tái lập được + mẫu truy cập openslr.org/33** (§4.1) — **[D-H]**. Một mỏ neo dữ liệu công khai cụ thể và lập trường "dùng kho ngữ liệu tải-miễn-phí cho tái lập" mà pipeline voice của Pebble nên áp dụng (quyết định datasets/mỏ-neo-hiệu-chuẩn).

### Mỗi phần giúp Pebble thành công thế nào

- **D-A / kiến trúc head voice-message.** Áp dụng *hình dạng* "front-end âm thanh học được → BiGRU/transformer → head chuỗi CTC" cho nguyên mẫu phương thức voice của Pebble. Hành động: dựng một thí nghiệm `voice/tone_ctc/` tái lập recipe 11.7% trên AISHELL-1 để xác thực bộ khung, *rồi* thay nhãn thanh AISHELL bằng nhãn bạc cảm-xúc/ngữ-điệu theo từng phát ngôn thực của Pebble. Việc tái lập là kiểm thử tích hợp; chỉ sau khi nó đạt ~11–12% TER bạn mới tin pipeline trên âm thanh trẻ em.
- **D-B / cấu thành mất mát.** Dùng **CTC làm mất mát của head voice** để phương thức voice đóng góp một số hạng `−log p(Y|X)` được chuẩn hóa đúng và không cần căn chỉnh khung, rồi cân bằng nó với các mất mát head text bằng cùng cơ chế chọn ở D-B (λ tĩnh trước; xem lại Kendall/GradNorm chỉ khi số hạng voice lấn át). Hành động: log độ lớn mất mát từng head sớm — mất mát CTC có thể lớn lúc khởi tạo và nhấn chìm các head text MTL.
- **D-D / đặc trưng ngữ-điệu-năng-lượng.** Khi (v2) Pebble học `energy`/ngữ điệu từ âm thanh, hãy cho một **cepstrogram không-Mel hoặc kênh pitch tường minh**, và chạy chính **ablation Baseline-2** của bài (đặt 0 các hệ số thời-gian-thấp) trên dữ liệu Pebble để xác nhận thông tin phi-pitch cũng mang cảm xúc — một ablation rẻ và quyết định. Hành động: thêm cờ `--cepstrum-no-mel` và `--high-time-only` vào front-end âm thanh để tái lập ablation.
- **D-E / lịch huấn luyện.** Dùng lại **Adam LR 0.001 + giảm-một-nửa-khi-dev-chững + 20 epoch + curriculum độ-dài SortaGrad** làm lịch mặc định của head voice; SortaGrad (phát ngôn ngắn trước) đặc biệt phù hợp với tin nhắn thoại trẻ em có độ dài rất khác nhau. Hành động: triển khai epoch đầu sắp-xếp-theo-độ-dài trong dataloader voice.
- **D-H / mỏ neo dữ liệu.** Dùng AISHELL-1 (openslr.org/33) làm mỏ neo tái lập công khai và làm corpus *đối chứng âm tính* (Quan Thoại người lớn, sạch, đọc) để đặt bối cảnh cho các chỉ số âm thanh tin-nhắn-trẻ-em. Hành động: ghim AISHELL-1 trong manifest dữ liệu của pipeline voice.

### Góc nhìn sức khỏe tâm thần trẻ em

- **Tính hợp lệ của transfer là một phần và phải nói rõ.** AISHELL-1 là giọng Quan Thoại **người lớn, sạch, đọc** trong buồng không nhiễu. Tin nhắn thoại của Pebble là **trẻ em**, **tự phát/cảm xúc**, **nhiễu** (mic điện thoại, nền), và (với thị trường Pebble) có lẽ **không-Quan-Thoại / đa ngôn ngữ**. Vậy *phương pháp* (cepstrogram → CNN → CTC, end-to-end, không căn chỉnh) chuyển giao được; *các con số* (11.7% TER) **không** chuyển giao sang cảm xúc trẻ em trên âm thanh nhiễu và không được trích dẫn như một điểm vận hành kỳ vọng. Chính bài báo cảnh báo hướng khó hơn: lời nói liên tục, nói tự nhiên *khó hơn* âm tiết tách rời — tin nhắn thoại trẻ em còn xa hơn nữa trên trục đó.
- **Vì sao CTC hợp với dữ liệu trẻ em.** Rào cản thực tế chủ đạo với dữ liệu thoại trẻ em là nhãn: bạn không thể căn chỉnh-tay khung cảm xúc trong âm thanh trẻ em một cách có đạo đức hay khả thi. Đặc tính "giám sát chỉ từ *chuỗi* nhãn" của CTC chính là chế độ làm cho dữ liệu thoại trẻ em gán-nhãn-bạc khả thi, và nó tránh bước forced-alignment vốn cần một bộ căn chỉnh riêng (huấn luyện trên người lớn, chuyển giao kém).
- **Thanh điệu ≠ cảm xúc, nhưng nền tảng ngữ điệu chồng lấp.** Thanh điệu từ vựng và ngữ điệu cảm xúc đều nằm trong quỹ đạo F0/pitch. Phát hiện của bài rằng **thông tin phi-pitch (cepstral thời-gian-thấp) cũng giúp** là tín hiệu khích lệ cho cảm xúc, nơi chất giọng (thở, căng) — một hiện tượng thời-gian-thấp/đường-thanh — mang tín hiệu khủng hoảng. Giảm thiểu/đạo đức: không bao giờ để một head cảm-xúc-thoại học được *hành động*; nó chỉ cấp tin cho Decision Engine, phản chiếu bất biến "mô hình không bao giờ quyết" của FAIIR.
- **Rủi ro: phụ thuộc ngữ cảnh kiểu tone-sandhi.** Giống như Thanh 3 mơ hồ nếu không có mô hình ngôn ngữ, cảm xúc của một đứa trẻ tại một thời điểm là mơ hồ nếu không có ngữ cảnh hội thoại. Giảm thiểu: head voice nên xuất một *tín hiệu*, hòa ở cấp lượt với ngữ cảnh của encoder text, chứ không phải một phán quyết độc lập.
- **Đạo đức.** Giọng nói trẻ em là sinh trắc và định danh cao; mô hình "tải miễn phí" của AISHELL **không** chuyển giao sang âm thanh trẻ em. Pebble phải xử lý tin nhắn thoại theo quản trị nghiêm hơn (không phát hành mở, xử lý trên thiết bị hoặc truy cập kiểm soát, đồng thuận giám hộ tường minh) — ngược lại với lập trường tái-lập-bằng-dữ-liệu-mở của bài này.

### Hạn chế & câu hỏi mở cho Pebble

- **Mâu thuẫn-hoặc-lỗ-hổng so với kế hoạch Pebble (lệch phương thức).** Mọi bài khác trong tập của Pebble là **text**; đây là bài **âm thanh** duy nhất. Pebble v1 (theo `docs/decisions.md`) chỉ huấn luyện các head text (`emotion`, `severity`) trên một **NeoBERT 4K-token**. Một head thanh-điệu/ngữ-điệu CTC **không** cắm vào NeoBERT — nó cần một *encoder âm thanh riêng*. Vậy lỗ hổng cụ thể: **Pebble chưa có quyết định backbone âm thanh** (D-A chỉ phủ encoder text NeoBERT-vs-ModernBERT). Bài này phơi bày rằng phương thức voice là một *mô hình thứ hai chưa phạm vi hóa*, không phải một head trên NeoBERT — một lỗ hổng kế hoạch cần đánh dấu trước công việc voice v2.
- **Mâu thuẫn với tài liệu âm-tiết-tách-rời (Chen et al. 2016, 4.5% TER).** Một người đọc ngây thơ có thể neo vào 4.5% như "nhận dạng thanh điệu đã giải xong". Bài này cho thấy con số đó **chỉ dành cho âm tiết tách rời, phát âm cẩn thận** và con số thực tế cho lời nói liên tục là ~11.7%, tệ hơn 2 lần. Pebble phải nội tâm hóa cùng hiệu chỉnh đó cho cảm xúc: các benchmark nhận-dạng-cảm-xúc trong phòng thí nghiệm/tách rời phóng đại rất nhiều khả năng đạt được trên tin nhắn thoại thực.
- **Không có hiệu chuẩn (calibration), không có độ tin cậy.** Giống FAIIR, bài này chỉ báo cáo tỉ lệ lỗi — không hiệu chuẩn, không độ tin cậy theo từng phát ngôn. Decision Engine của Pebble cần *xác suất* từ head voice; một posterior CTC không phải xác suất cảm xúc đã hiệu chuẩn, nên một bước hiệu chuẩn (v2, D-G) phải thêm vào trên cùng.
- **Phủ ngôn ngữ.** Phương pháp được minh họa trên Quan Thoại (một ngôn ngữ thanh điệu). Các ngôn ngữ người dùng khả dĩ của Pebble có thể phi-thanh-điệu; chính *nhiệm vụ thanh điệu từ vựng* có thể vô nghĩa, nhưng các bài học *đặc-trưng-ngữ-điệu-học-được* và *CTC-từ-nhãn-chuỗi* vẫn còn. Câu hỏi mở: kho ngữ liệu **ngữ-điệu-cảm-xúc** công khai (không phải thanh điệu) nào là mỏ neo thay thế đúng — IEMOCAP / MSP-Podcast là người lớn; một kho cảm-xúc-giọng-nói-trẻ-em là tập dữ liệu còn thiếu (D-H).
- **Nguồn gốc số liệu đơn nguồn.** HTML của ISCA không in bảng TER số; mọi số thập phân theo-từng-thanh/theo-từng-baseline đến từ bảng tiền in arXiv (✔ tiêu điểm, ≈ thập phân). Nếu Pebble trích một con số cụ thể theo từng thanh, hãy lấy PDF camera-ready từ kho ISCA (`lugosch18_interspeech.pdf`) để nâng ≈ → ✔.
