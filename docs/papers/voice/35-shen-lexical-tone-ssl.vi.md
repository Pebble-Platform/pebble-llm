# Bài báo 35 — Mã hóa Thanh điệu Từ vựng trong các Mô hình Tự giám sát của Ngôn ngữ Nói

## 1. Thông tin thư mục

**Tiêu đề:** Encoding of lexical tone in self-supervised models of spoken language (Mã hóa thanh điệu từ vựng trong các mô hình tự giám sát của ngôn ngữ nói)

**Tác giả:** Gaofei Shen (Tilburg University), Michaela Watkins (University of Amsterdam), Afra Alishahi (Tilburg University), Arianna Bisazza (University of Groningen), Grzegorz Chrupała (Tilburg University).

**Năm / hội nghị:** NAACL 2024 (Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1: Long Papers), trang 4250–4261. arXiv:2403.16865. ACL Anthology: 2024.naacl-long.239.

**Mã nguồn:** https://github.com/techsword/tone-encoding-in-speech-model

## 2. Tóm tắt một đoạn (góc nhìn Pebble)

Đây là một bài báo về tính diễn giải (interpretability), không phải bài báo xây dựng mô hình. Nó đặt câu hỏi: liệu các mô hình ngôn ngữ nói tự giám sát (SLM) thuộc lớp `wav2vec2` có **mã hóa thanh điệu từ vựng (lexical tone)** trong các trạng thái ẩn của chúng **mà chưa từng được huấn luyện trên dữ liệu có thanh điệu** hay không? Bằng cách dùng các đầu dò tuyến tính (linear probe) trên các kích hoạt trạng thái ẩn đã đóng băng, các tác giả cho thấy ngay cả các SLM được tiền huấn luyện chỉ trên các ngôn ngữ **không có thanh điệu** (tiếng Anh, tiếng Pháp) cũng mã hóa thanh điệu tiếng Quan Thoại và tiếng Việt vượt xa các đường cơ sở (baseline) âm học (F0, MFCC) và văn bản (BERT). Đây là bài báo có sức nặng nhất cho câu hỏi về **phương thức tin nhắn thoại (voice-message modality)** của Pebble: *liệu một bộ mã hóa `wav2vec2` đã tiền huấn luyện có sẵn nắm bắt được tín hiệu ngữ điệu/thanh điệu mà chúng ta quan tâm, hay Pebble cần một đầu thanh điệu chuyên dụng và dữ liệu huấn luyện có thanh điệu?* Câu trả lời ngắn gọn mà bài báo ủng hộ: **thanh điệu đã có sẵn trong biểu diễn, có thể phục hồi bằng một đầu dò tuyến tính — nhưng nó nằm ở các tầng giữa/trên cụ thể, việc tinh chỉnh ASR trên một ngôn ngữ không thanh điệu sẽ phá hủy nó, và thanh điệu tiếng Việt khó phục hồi hơn thanh điệu tiếng Quan Thoại.**

## Nghiên cứu sâu — đọc toàn văn PDF (2026-06-16)

> Đọc đối chiếu với phiên bản NAACL 2024 đã xuất bản. File PDF nội bộ `pdfs/35-shen-lexical-tone-ssl.pdf`
> mang số trang ACL Anthology 4250–4261, tức là nó CHÍNH LÀ bản camera-ready đã xuất bản (giống hệt
> arXiv:2403.16865 bản đã xuất bản). Kết quả định lượng của bài báo gần như hoàn toàn nằm trong các **hình
> đồ thị** (Hình 2–8) — các đường cong độ chính xác theo từng tầng được vẽ dưới dạng ảnh. `pdftotext` phục
> hồi được chú thích hình và toàn bộ văn bản thân bài/bảng nhưng KHÔNG phục hồi được giá trị trục y của các
> đường cong đó; các con số tôi đọc từ hình được gắn thẻ ≈ (xấp xỉ, đọc-từ-hình) và *xu hướng* của chúng là
> điều mà bài báo tự khẳng định trong phần văn xuôi (✔). Các sự kiện được nêu bằng chữ (kích thước tập dữ
> liệu, chia tập, tham số mô hình, baseline) là ✔.

### Ghi chú về truy cập nguồn

- **Trích xuất:** `pdftotext "docs/papers/pdfs/35-shen-lexical-tone-ssl.pdf" -` — toàn bộ văn bản thân bài,
  abstract, Bảng 1–4, và tất cả chú thích hình được phục hồi sạch sẽ. Các ký tự IPA tiếng Việt và Pinyin
  tiếng Quan Thoại bị lỗi mã hóa trong bản dump nhưng nội dung ngôn ngữ học vẫn nguyên vẹn.
- **Xác minh xuất xứ:**
  - Truy vấn `Shen Watkins Alishahi Bisazza Chrupala "Encoding of lexical tone in self-supervised models of
    spoken language" NAACL 2024` → https://aclanthology.org/2024.naacl-long.239/ — xác nhận tác giả, hội
    nghị, khoảng trang 4250–4261. ✔
  - WebFetch trang ACL Anthology xác nhận abstract + danh sách tác giả + số trang; trang này không hiển thị
    số hình (chỉ có trong PDF). ✔
  - Bản mirror arXiv: https://arxiv.org/abs/2403.16865 (cùng tiêu đề/tác giả). ✔
- **Quy tắc xung đột:** PDF nội bộ và bản xuất bản trùng khớp (cùng số trang ACL); không có chênh lệch bản
  tiền in (preprint).
- **Xác minh nguồn-mâu-thuẫn:** truy vấn về việc nắm bắt thanh điệu của SSL rời rạc →
  https://arxiv.org/abs/2410.19935 ("Do Discrete Self-Supervised Representations of Speech Capture Tone
  Distinctions?", ICASSP 2025) — được dùng dưới đây trong phần Hạn chế làm mâu thuẫn/khoảng-trống tường
  minh. ✔

### Bài báo thực sự làm gì

**Câu hỏi.** Ba câu hỏi con (§1): (1) Các SLM huấn luyện trên ngôn ngữ có thanh điệu *và* không thanh điệu
có mã hóa thanh điệu không? (2) Việc tinh chỉnh ASR có giám sát thay đổi mã hóa thanh điệu ra sao? (3) Các
SLM có thể hiện các mẫu hình tri giác (perceptual pattern) và quỹ đạo phát triển giống con người không?

**Các mô hình được dò (§4.2, Bảng 1).** Tất cả là `wav2vec2-base` (5 tầng bộ mã hóa đặc trưng tích chập +
12 tầng transformer, ẩn 768 chiều, 95M tham số) trừ mô hình tiếng Quảng Đông (`wav2vec2-conformer`, 180M
tham số):
- **Tiếng Anh** — tiền huấn luyện + tinh chỉnh trên LibriSpeech (960h/960h). Không thanh điệu. ✔
- **Tiếng Pháp** — tiền huấn luyện trên MLS French (1.000h). Không thanh điệu. ✔
- **Tiếng Quan Thoại** — tiền huấn luyện 1.000h, tinh chỉnh 178h (tiền huấn luyện AISHELL-2 / tinh chỉnh
  AISHELL-1). Có thanh điệu. ✔
- **Tiếng Việt** — tiền huấn luyện trên **13.000h** âm thanh YouTube không nhãn, tinh chỉnh 250h (VLSP). Có
  thanh điệu. ✔ (Lưu ý: nhiều hơn ~13× dữ liệu tiền huấn luyện so với bất kỳ mô hình nào khác — một yếu tố
  gây nhiễu mà tác giả nêu ở §7.)
- **Tiếng Quảng Đông** — tiền huấn luyện 2.800h (giọng người lớn tuổi + YouTube), kiến trúc conformer. Có
  thanh điệu. ✔

**Dữ liệu kiểm tra (§4.1).**
- **Tiếng Quan Thoại: THCHS-30** (Wang & Zhang 2015) — 30h tiếng Quan Thoại đọc thu trong phòng lab, phiên
  âm thành ký tự + Pinyin; căn chỉnh cưỡng bức (forced alignment) cấp ký tự qua Charsiu. Nhãn thanh điệu đọc
  trực tiếp từ Pinyin (một hình vị = một ký tự = một thanh điệu). Tiếng Quan Thoại **4 thanh** (T1–T4);
  **thanh nhẹ (neutral tone) bị loại bỏ** (xuất hiện ở âm tiết không trọng âm và không ổn định). ✔
- **Tiếng Việt: VIVOS** (Luong & Vu 2016) — 15h tiếng Việt đọc thu trong phòng lab; chữ viết → IPA + nhãn
  thanh điệu qua vPhon; căn chỉnh cưỡng bức cấp âm tiết qua Montreal Forced Aligner. Bài báo dùng hệ
  **8 thanh** của Kirby (2011) cho thiết lập; tiếng Việt thông thường là **6 thanh**. ✔

**Phương pháp dò (§4.3) — công thức cốt lõi.**
1. Chạy SLM đóng băng trên audio kiểm tra; **gộp trung bình (average-pool) đầu ra trạng thái ẩn theo thời
   lượng của mỗi âm tiết** (dùng mốc thời gian căn chỉnh cưỡng bức) → một **vector 768 chiều cho mỗi âm
   tiết/hình vị**. ✔
2. Huấn luyện một **bộ phân loại tuyến tính Ridge** (mỗi tầng) để dự đoán nhãn thanh điệu từ vector đó. Mô
   hình chọn qua **CV 5-fold**; cường độ chính quy hóa quét trên {10⁻⁴ … 10²}; báo cáo **độ chính xác trên
   tập kiểm tra**. ✔
3. **Kiểm soát yếu tố gây nhiễu từ vựng (quan trọng):** xây dựng một **chia tập train/test loại trừ, trong
   đó các chuỗi âm vị trong tập test không bao giờ xuất hiện trong tập train** — để bộ dò không thể "gian
   lận" bằng cách ghi nhớ liên kết chuỗi-âm-vị→thanh-điệu mà phải dựa vào tín hiệu thanh điệu âm học. ✔
4. Chia tập (Bảng 2): tiếng Quan Thoại **223.851 train / 45.772 test**; tiếng Việt **124.248 train / 29.629
   test**. 80:20 ngẫu nhiên trong ràng buộc loại-trừ-âm-vị. ✔ Bộ dò phụ âm (Bảng 3): 92.413 / 15.688. ✔

**Các đường cơ sở (§4.3).**
- **Đường cơ sở đường viền F0**: cửa sổ 21 khung quanh tâm từ → vector 21 chiều (Praat). ✔
- **Đường cơ sở MFCC**: MFCC 40 chiều, cửa sổ 21 khung → vector 840 chiều (Librosa). ✔
- **Đường cơ sở văn bản (BERT)**: `bert-base-chinese` tiếng Trung, embedding 768 chiều mỗi ký tự — đo "có
  thể đoán bao nhiêu thanh điệu chỉ từ văn bản". ✔

**Kết quả.**

*(1) Mã hóa thanh điệu giữa các ngôn ngữ (§5.1, Hình 2 & 3).*
- **Tất cả các tầng của tất cả các SLM đều vượt baseline F0 và MFCC, và đến lượt chúng vượt baseline văn bản
  BERT** (✔ văn xuôi). Tức là tín hiệu giọng nói mang nhiều thông tin thanh điệu hơn văn bản nhiều, và ngay
  cả một SLM huấn luyện trên ngôn ngữ không thanh điệu cũng vượt các đặc trưng cao độ thủ công. Độ chính xác
  tiếng Quan Thoại ở tầng tốt nhất tuyệt đối nằm trong khoảng **~0,80–0,90+** cho các mô hình có thanh điệu
  và rõ ràng trên baseline cho các mô hình không thanh điệu (≈ đọc-từ-hình, Hình 2).
- **Các mô hình ngôn ngữ có thanh điệu mã hóa thanh điệu tốt hơn nhìn chung, và mức mã hóa tăng ở các tầng
  cao hơn.** ✔
- **Các mô hình không thanh điệu (Anh/Pháp) vẫn mã hóa thanh điệu đáng kể**, nhưng cho thấy một **sự sụt
  giảm mạnh ở các tầng cuối** — sự sụt giảm tương ứng nhỏ hơn nhiều ở các mô hình ngôn ngữ có thanh điệu. ✔
  (Đây là hành vi giống autoencoder đặc trưng: các tầng trên cùng của một mô hình không thanh điệu tái
  chuyên biệt hóa ra khỏi thanh điệu.)
- **Tiếng Việt (Hình 3) khó hơn.** Mô hình **tiếng Quảng Đông** chuyển giao sang thanh điệu tiếng Việt *tốt
  hơn một chút* so với tiếng Anh, đặc biệt ở các tầng sau; nhưng mô hình **tiếng Quan Thoại** lại có mẫu
  hình **giống mô hình tiếng Anh (không thanh điệu)** trên thanh điệu tiếng Việt — tức là năng lực thanh
  điệu Quan Thoại **không** chuyển giao sang tiếng Việt. ✔ Giải thích của tác giả: thanh điệu tiếng Việt dựa
  nhiều hơn vào **kiểu phát âm (phonation type) / chất giọng (voice quality)** so với các tín hiệu **đường
  viền F0/độ cao** vốn chi phối thanh điệu Quan Thoại (Brunelle 2009); và tiếng Việt có nhiều tương phản
  thanh điệu hơn (6) so với Quan Thoại (4). ✔

*(2) Tinh chỉnh ASR (§5.2, Hình 4 & 5).* Tinh chỉnh có **tác động ngược nhau theo tính thanh điệu của ngôn
ngữ**:
- Với **tiếng Quan Thoại** (có thanh điệu), tinh chỉnh ASR **cải thiện** độ chính xác phân loại thanh
  điệu. ✔
- Với **tiếng Anh** (không thanh điệu), tinh chỉnh ASR **làm hại** độ chính xác phân loại thanh điệu. ✔
- Cùng mẫu hình trên dữ liệu tiếng Việt (Hình 5: tinh chỉnh tiếng Việt giúp, tinh chỉnh tiếng Anh hại). ✔
- Diễn giải: tinh chỉnh ASR đẩy mô hình chuyên biệt hóa cho **đầu ra dạng-viết**; thanh điệu không liên quan
  đến việc phiên âm một ngôn ngữ không thanh điệu nên tinh chỉnh sẽ *loại bỏ* nó, nhưng thanh điệu thiết yếu
  để phân biệt các âm tiết Quan Thoại cùng-phụ-âm nên tinh chỉnh sẽ *khuếch đại* nó. ✔

*(3) So sánh với con người (§5.3, Hình 6–8).*
- **Quỹ đạo học (§5.3.1):** Các SLM vượt baseline F0/MFCC sau ~10.000 bước tiền huấn luyện, nhưng không cho
  thấy **sự khác biệt quỹ đạo** giữa thanh điệu và phụ âm — khác với trẻ em, vốn tiếp thu độ nhạy thanh điệu
  sớm hơn độ nhạy phụ âm. Nên **các SLM KHÔNG đi theo quỹ đạo phát triển của con người**. ✔ (SLM tùy chỉnh
  tiền huấn luyện từ đầu: tiếng Anh trên LibriSpeech 710h, tiếng Quan Thoại trên MAGICDATA 712h, fairseq,
  85.000 bước, 8×A100, lưu checkpoint mỗi 5.000 bước.) ✔
- **Tương phản thanh điệu/phụ âm (§5.3.2, Hình 7–8):** các cặp thanh điệu **T1–T4 và T2–T3** cho thấy khoảng
  cách độ chính xác lớn nhất giữa mô hình Quan Thoại và Anh, **gần khớp với mẫu hình dễ nhầm lẫn của con
  người** (T2–T3 là cặp dễ nhầm nhất cho cả người bản ngữ tiếng Anh lẫn người bản ngữ Quan Thoại). Nên ở
  **điểm cuối**, các SLM *có* phản chiếu mức dễ nhầm tri giác của con người, dù con đường phát triển khác
  nhau. ✔

**Công trình trước đó mà bài báo dựa vào / đối chiếu (§3.3).** Yuan và cộng sự (2021) tinh chỉnh một
`wav2vec2` tiếng Anh cho thanh điệu Quan Thoại và đạt **tỷ lệ lỗi thanh điệu 6%**; Ryant và cộng sự (2014)
đạt **lỗi 15,56%** chỉ từ MFCC. ✔ Bài báo này cố ý **không** cạnh tranh về độ chính xác phân loại — nó dò
xem điều gì xuất hiện **mà không có** giám sát thanh điệu.

### Các phần trực tiếp hữu ích cho Pebble

> Hiện vật (artifact) liên quan của Pebble ở đây là **đường nạp tin nhắn thoại của luận đề Pebble**: một bộ
> mã hóa âm thanh thuộc lớp `wav2vec2` đã tiền huấn luyện biến clip giọng nói của trẻ thành các đặc trưng nạp
> cho các đầu cảm xúc/mức độ nghiêm trọng phía sau. Các Decision ID mà bài báo này dịch chuyển: **D-A** (chọn
> backbone bộ mã hóa — ở đây là bộ mã hóa *âm thanh*), **D-D** (nguồn chuyển giao / khởi tạo hồi quy cho các
> tín hiệu dẫn xuất từ ngữ điệu), **D-E** (tinh chỉnh theo giai đoạn / cái gì bị tinh chỉnh phá hủy), **D-F**
> (lượt tiền huấn luyện thích ứng miền).

1. **Thanh điệu (và mở rộng ra là ngữ điệu đường-viền-cao-độ) có thể phục hồi bằng một đầu dò *tuyến tính*
   trên các trạng thái ẩn `wav2vec2-base` đóng băng, ngay cả với không dữ liệu huấn luyện thanh điệu — và
   vượt baseline F0/MFCC ở mọi tầng.** [**D-A**, **D-F**] Đây là bằng chứng tồn tại rằng đường thoại của
   Pebble **không** cần một corpus tiền huấn luyện có thanh điệu để phơi bày thanh điệu/ngữ điệu cho một đầu
   phía sau; một bộ mã hóa sẵn-có đóng băng + một đầu dò mỏng đã mang nó.
   - *Rủi ro chuyển giao:* **Có thật và lớn.** Tín hiệu của bài báo là **thanh điệu từ vựng** (cao độ âm vị
     học trên giọng đọc, lab sạch, căn chỉnh đơn-âm-tiết) — *không phải* **ngữ điệu cảm xúc/tình cảm** trong
     giọng nói tự phát của trẻ. Việc thanh điệu giải mã được tuyến tính không chứng minh ngữ điệu cảm xúc
     cũng vậy. Nhưng đây là bằng chứng *định hướng* mạnh: cùng các tín hiệu đường-viền-F0/chất-giọng mang
     thanh điệu từ vựng cũng là nền tảng của ngữ điệu cảm xúc, và chúng tồn tại đến các tầng giữa/trên của
     `wav2vec2`. Hãy coi như bằng chứng "ngữ điệu nằm trong biểu diễn", không phải "cảm xúc đã được giải
     quyết".

2. **Thanh điệu nằm ở các tầng *cụ thể* — các tầng transformer giữa-đến-trên, với sự sụp đổ ở tầng cuối trên
   các mô hình huấn luyện không-thanh-điệu.** [**D-A**, **D-E**] (Hình 2–5: mã hóa tăng qua các tầng giữa;
   các tầng *cuối* của mô hình Anh/Pháp giảm mạnh.) Hệ quả cấu hình cụ thể: Pebble **không** được mặc định
   dùng đầu ra tầng-cuối / đã-pool của bộ mã hóa cho các đặc trưng ngữ điệu; nó nên **chọn một tầng trung
   gian** (hoặc tổng-tầng-có-trọng-số) làm nguồn đặc trưng cho bất kỳ đầu nhạy-ngữ-điệu nào.
   - *Rủi ro chuyển giao:* Chỉ số tầng phụ thuộc mô hình; *nguyên tắc* (đừng dùng tầng trên cùng của một bộ
     mã hóa không-thanh-điệu đã-tinh-chỉnh-ASR cho ngữ điệu) chuyển giao sạch sẽ. Nếu bộ mã hóa âm thanh của
     Pebble là một `wav2vec2` đã-tinh-chỉnh-ASR tiếng Anh, bài báo này dự đoán **tầng trên cùng của nó là nơi
     tệ nhất** để đọc ngữ điệu.

3. **Tinh chỉnh ASR trên một ngôn ngữ không thanh điệu *xóa* mã hóa thanh điệu (Hình 4–5).** [**D-E**,
   **D-F**] Nếu Pebble lấy một checkpoint `wav2vec2` đã **tinh chỉnh ASR trên tiếng Anh**, tín hiệu
   thanh-điệu/ngữ-điệu bị *suy giảm* chủ động so với checkpoint **chỉ-tự-giám-sát (đã-tiền-huấn-luyện,
   chưa-tinh-chỉnh)**. Hành động: với đường thoại của Pebble, ưu tiên checkpoint **chỉ-SSL-tiền-huấn-luyện**
   (hoặc một checkpoint đa ngôn ngữ / ngôn-ngữ-có-thanh-điệu) thay vì một checkpoint đã-tinh-chỉnh-ASR tiếng
   Anh làm bộ trích đặc trưng ngữ điệu.
   - *Rủi ro chuyển giao:* Kết quả là cho *thanh điệu từ vựng* dưới tinh chỉnh ASR *tiếng Anh*. Cơ chế (tinh
     chỉnh theo tác vụ tỉa bỏ các đặc trưng không liên quan đến đích viết) khái quát hóa thành "tinh chỉnh
     cho một mục tiêu không-liên-quan-ngữ-điệu sẽ tỉa bỏ ngữ điệu". Pebble nên mặc định coi bất kỳ checkpoint
     ASR tiếng Anh nào là mất-ngữ-điệu và xác thực bằng đầu dò tuyến tính của riêng mình (rẻ — xem #4).

4. **Công thức dò là một chẩn đoán gần-như-miễn-phí, tái sử dụng trực tiếp cho Pebble.** [**D-A**, **D-D**]
   Gộp trung bình các trạng thái ẩn đóng băng trên đơn vị quan tâm → vector 768 chiều → **đầu dò tuyến tính
   Ridge, CV 5-fold, chia tập train/test loại-trừ-nội-dung** → đường cong độ chính xác theo từng tầng. Đây
   *chính xác* là cách Pebble nên trả lời "bộ mã hóa âm thanh đã chọn của chúng ta có sẵn mang tín hiệu cảm
   xúc không, và ở tầng nào?" **trước khi** cam kết một đầu thanh-điệu/ngữ-điệu được tinh chỉnh nặng. Tốn một
   giờ-CPU, không phải một lần chạy GPU.
   - *Rủi ro chuyển giao:* Không có rủi ro về bản thân phương pháp; điều chỉnh duy nhất là đổi nhãn (thanh
     điệu → một đại lượng cảm xúc thay thế: bin valence/arousal, hoặc thậm chí một nhãn cảm xúc thô) và đơn
     vị căn chỉnh (âm tiết → phát ngôn hoặc cửa sổ cố định). Kỷ luật **chia tập loại-trừ-nội-dung** là phần
     nhập khẩu then chốt: không có nó, Pebble sẽ ghi nhận quá mức công cho bộ mã hóa do rò rỉ tín hiệu từ
     vựng.

5. **Thanh điệu tiếng Việt khó phục hồi hơn tiếng Quan Thoại, và năng lực Quan Thoại KHÔNG chuyển giao sang
   tiếng Việt (Hình 3).** [**D-D**, **D-H**] Đối với góc-độ thoại **tiếng Việt** của Pebble cụ thể: đừng giả
   định một bộ mã hóa huấn luyện tiếng Quan Thoại hoặc tiếng Anh cho bạn ngữ điệu tiếng Việt "miễn phí" với
   cùng chất lượng như Quan Thoại. Thanh điệu tiếng Việt dựa vào các tín hiệu **kiểu phát âm/chất giọng**,
   vốn là một phần khác (và bài báo gợi ý là kém tách-tuyến-tính hơn từ các bộ mã hóa này) của tín hiệu.
   - *Rủi ro chuyển giao:* Đây là *cảnh báo* liên quan Pebble nhất trong bài báo. Nếu sản phẩm của Pebble
     phục vụ trẻ em nói tiếng Việt, năng lực ngữ điệu của bộ mã hóa thực nghiệm yếu hơn và phụ thuộc tín hiệu
     hơn so với tiêu đề Quan Thoại gợi ý. Hãy dự trù cho một đầu dò riêng cho tiếng Việt và có thể một bộ mã
     hóa tiền-huấn-luyện tiếng Việt (hoặc tiếng Quảng Đông).

### Mỗi phần giúp Pebble thành công như thế nào

- **D-A (chọn backbone âm thanh).** Bài báo này là cơ sở bằng chứng cho việc **không** huấn luyện một bộ mã
  hóa thanh-điệu/ngữ-điệu từ đầu và **không** đòi hỏi dữ liệu tiền huấn luyện có thanh điệu: một
  `wav2vec2-base` đóng băng đã phơi bày thanh điệu tuyến tính trên F0/MFCC. Hành động cụ thể: với bộ mã hóa
  tin-nhắn-thoại của Pebble, khởi đầu từ một checkpoint **`wav2vec2` chỉ-SSL-tiền-huấn-luyện** và coi ngữ
  điệu là *có-thể-dò*, không phải *huấn-luyện-từ-không*. Ghép với các phát hiện HuBERT thuộc lớp bài báo
  33/34 nếu có trong bộ.
- **D-E (tinh chỉnh theo giai đoạn / việc mở băng phá hủy gì).** Kết quả Hình 4–5 là cảnh báo trực tiếp cho
  việc tinh chỉnh theo giai đoạn bộ mã hóa âm thanh của Pebble: **tinh chỉnh cho mục tiêu sai sẽ xóa ngữ điệu
  bạn muốn.** Nếu Pebble tinh chỉnh bộ mã hóa âm thanh đầu-cuối trên, ví dụ, một tác vụ phụ ASR hay phiên âm,
  nó có nguy cơ tỉa bỏ tín hiệu ngữ-điệu-cảm-xúc. Giảm thiểu: **đóng băng các tầng trung gian mang ngữ điệu**,
  hoặc dùng LR phân biệt / mở băng dần dần bảo vệ các tầng giữa — bản tương ứng phía bộ mã hóa của chính sách
  D-E phía văn bản.
- **D-F (lượt tiền huấn luyện thích ứng miền).** Các mô hình huấn luyện-không-thanh-điệu vẫn mang thanh điệu,
  nhưng một **lượt SSL tiếp tục trên audio trong-miền (giọng-trẻ / có-thanh-điệu)** là đòn bẩy để *nâng* mức
  mã hóa thanh-điệu/ngữ-điệu tầng-giữa mà không cần nhãn — bản tương ứng phía âm thanh của lượt MLM thích ứng
  miền phía văn bản. Bài báo cho thấy tiền-huấn-luyện-có-thanh-điệu > tiền-huấn-luyện-không-thanh-điệu về mã
  hóa thanh điệu, nên một lượt SSL thích ứng miền trên giọng nói trẻ em là một thắng lợi không-cần-nhãn đáng
  tin cho các đầu ngữ điệu.
- **D-D (nguồn chuyển giao cho một tín hiệu ngữ-điệu kề-hồi-quy/mức-độ-nghiêm-trọng).** Nếu Pebble từng dẫn
  xuất một bộ hồi quy arousal/năng-lượng dựa trên ngữ điệu từ âm thanh, bài báo này nói rằng **nguồn chuyển
  giao có vai trò** (tiền huấn luyện có thanh điệu vs không thanh điệu) và **chỉ số nên theo từng tầng** (độ
  chính xác tầng-tốt-nhất, không phải độ chính xác đầu-ra-đã-pool). Dùng đầu dò để chọn checkpoint nguồn +
  tầng một cách thực nghiệm.

### Lăng kính sức khỏe tâm thần trẻ em

- **Sự phù hợp về phương thức, kèm cảnh báo.** Pebble hướng tới trẻ em và ở cấp lượt-thoại; dữ liệu bài báo
  này là giọng nói **người lớn, đọc, lab-sạch** (THCHS-30, VIVOS). Giọng trẻ em khác về dải F0, cách phát
  âm, sự cường điệu thanh điệu (chính bài báo trích Rhee và cộng sự 2021 rằng *trẻ em cường điệu các khác
  biệt thanh điệu*), và tính tự phát. Nên năng lực thanh điệu *người-lớn-đọc* của bộ mã hóa là **chặn trên**
  cho những gì Pebble nhận được trên giọng nói trẻ tự phát — hãy kỳ vọng suy giảm do văn phong và kênh (mic
  điện thoại, nhiễu, méo ngữ điệu do cảm xúc).
- **Tại sao điều này quan trọng cho an toàn.** Đường thoại của Pebble nhằm phơi bày cảm xúc/đau khổ sớm hơn
  và gián tiếp hơn so với văn bản. Ngữ điệu cảm xúc (cảm xúc phẳng/đơn điệu trong trầm cảm, kích
  động/bất-ổn-cao-độ trong lo âu, chất giọng thều thào/kẹt trong họng) chia sẻ nền tảng **đường-viền-F0 +
  chất-giọng** mà bài báo này cho thấy `wav2vec2` mã hóa. Phát hiện về chất giọng của bài báo (giọng kẹt
  trong họng thay đổi tri giác thanh điệu, §3.2) gợi ý rằng *cùng* các tầng bộ mã hóa mang các tín hiệu cảm
  xúc-ngữ-điệu liên quan lâm sàng — nhưng **không có nhãn cảm xúc nào được kiểm tra ở đây**, nên đây là một
  giả thuyết Pebble phải xác thực, không phải nhập khẩu.
- **Rủi ro cụ thể với trẻ em Việt.** Nếu Pebble phục vụ trẻ em Việt, kết quả Hình-3 của bài báo (thanh điệu
  tiếng Việt khó hơn, phụ thuộc kiểu-phát-âm, không có chuyển giao Quan-Thoại→Việt) có nghĩa là đường thoại
  **thực nghiệm yếu hơn** cho tiếng Việt so với tiêu đề Quan Thoại ngụ ý. Đối với một sản phẩm kề-an-toàn,
  việc phục hồi ngữ điệu yếu hơn ở một ngôn ngữ là một rủi ro công-bằng/chuyển-giao phải được đo theo từng
  ngôn ngữ, không được giả định đồng đều.
- **Đạo đức.** Toàn bộ dữ liệu ở đây là các corpus ASR giọng-đọc công khai (không trẻ vị thành niên, không
  nội dung lâm sàng); bài báo thuần túy về tính diễn giải. Việc chuyển giao sang một sản phẩm giọng-nói-trẻ
  giới thiệu mọi mối lo về dữ-liệu-trẻ-vị-thành-niên (đồng thuận, xử lý trên thiết bị, lưu giữ) mà bài báo
  không đối mặt — Pebble không thể kế thừa dấu chân quản trị nhẹ của nó khi chuyển sang thu giọng trẻ trực
  tiếp.

### Hạn chế & câu hỏi mở cho Pebble

- **Mâu thuẫn/khoảng-trống so với dòng công trình SSL rời rạc.** Bài báo này dò các trạng thái ẩn **liên tục**
  và thấy thanh điệu được mã hóa phong phú. Nhưng câu hỏi anh-em/tiếp-nối của Shen và cộng sự — được trả lời
  bởi *"Do Discrete Self-Supervised Representations of Speech Capture Tone Distinctions?"* (arXiv:2410.19935,
  ICASSP 2025; đã xác thực ✔) — thấy rằng việc **rời-rạc-hóa** các đặc trưng SSL (k-means / pipeline
  "textless NLP" đơn-vị-HuBERT) gây ra **mất mát đáng kể thông tin thanh điệu, ngay cả với các mô hình SSL
  chuyên-biệt-ngôn-ngữ**, và rằng rời-rạc-hóa phải **nhận-thức-tác-vụ (task-aware)** cho các tác vụ phụ thuộc
  thanh điệu. **Hệ quả trực tiếp cho Pebble:** nếu đường thoại của Pebble từng định tuyến audio qua một biểu
  diễn giọng nói **đơn-vị-rời-rạc / được-token-hóa** (mã HuBERT, front-end LLM token-giọng-nói), nó sẽ **mất**
  chính tín hiệu ngữ-điệu/thanh-điệu mà bài báo này chứng minh là có trong các đặc trưng liên tục. Pebble nên
  giữ đầu ngữ-điệu/cảm-xúc trên các trạng thái ẩn **liên tục**, không phải trên các token giọng nói đã rời rạc
  hóa. Đây là cảnh báo liên-bài-báo quan trọng nhất cho phương thức thoại.
- **Không có ngữ điệu cảm xúc/tình cảm nào được kiểm tra — chỉ thanh điệu từ vựng.** Toàn bộ việc chuyển giao
  sang Pebble dựa trên giả định (hợp lý nhưng chưa được chứng minh) rằng ngữ điệu cảm xúc chia sẻ nền tảng đã
  mã hóa. Bài báo không thể cho Pebble biết liệu `wav2vec2` có mã hóa tuyến tính arousal/valence *cảm xúc* hay
  không. Đây là thí nghiệm mở số 1: chạy lại đầu dò §4.3 với một nhãn cảm xúc trên giọng nói trẻ em/cảm xúc.
- **Dữ liệu kiểm tra đọc, lab-sạch, người lớn, đơn ngôn ngữ.** Tác giả nêu rõ (§7) rằng THCHS-30/VIVOS "không
  phản ánh đầy đủ sự đa dạng ngôn ngữ của các giọng và phương ngữ khác nhau" và là giọng đọc. Các tin nhắn
  thoại trẻ em tự phát, nhiễu của Pebble nằm ngoài phân phối trên mọi trục.
- **Yếu tố gây nhiễu của mô hình tiếng Việt.** Bộ mã hóa tiếng Việt được tiền huấn luyện trên **13.000h** so
  với ~1.000h cho các mô hình khác (§7) — nên bất kỳ lợi thế nào của mô hình tiếng Việt có thể là do *quy mô
  dữ liệu*, không phải *tính thanh điệu*. Pebble không thể rút ra một kết luận sạch "tiền huấn luyện có thanh
  điệu giúp tiếng Việt"; đòn bẩy sạch nhất nó có thể dùng là **lượt thích ứng miền tiếp-tục-SSL** (D-F), nơi
  quy mô có thể kiểm soát được.
- **Đầu dò ≠ đặc trưng dùng được.** Việc giải mã được bằng đầu dò tuyến tính cho thấy thông tin *tồn tại*; nó
  không cho thấy một đầu phía sau sẽ *dùng* nó tốt, cũng không cho thấy nó sống sót qua tinh chỉnh đầu-cuối
  (Hình 4–5 cho thấy tinh chỉnh có thể *phá hủy* nó). Pebble phải xác minh sau-tinh-chỉnh, không chỉ trên bộ
  mã hóa đóng băng.
- **Không thể trích con số chính xác từ các hình.** Các giá trị độ chính xác theo từng tầng nằm trong các đồ
  thị ảnh; tập tài liệu này báo cáo xu hướng (✔, văn xuôi của chính bài báo) và các khoảng xấp xỉ (≈,
  đọc-từ-hình). Nếu Pebble cần con số chính xác theo từng tầng cho một trích dẫn, hãy lấy chúng từ
  mã/đầu-ra đã phát hành của tác giả tại kho GitHub thay vì từ PDF.
