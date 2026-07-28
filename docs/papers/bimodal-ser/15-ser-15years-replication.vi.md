# Paper 15 — Charting 15 Years of Progress in Deep Learning for SER: A Replication Study

> Bản dịch tiếng Việt của [15-ser-15years-replication.md](15-ser-15years-replication.md) — cập nhật 2026-07-10.

- **Authors:** Andreas Triantafyllopoulos, Anton Batliner, Björn W. Schuller
- **Venue / year:** arXiv 2025 (code: github.com/CHI-TUM/ser-progress-replication)
- **Links:** abs https://arxiv.org/abs/2508.02448 · PDF `pdfs/15-ser-15years-replication.pdf`
- **Group:** survey / benchmark (reproducibility)

**Summary:** Nghiên cứu tái lặp (replication study) về tiến bộ của SER kể từ Interspeech 2009 Challenge, cả trên audio lẫn text; kết luận rằng có hiện tượng diminishing returns (lợi ích giảm dần) sau kỷ nguyên transformer, và "tiến bộ" phụ thuộc vào cách so sánh.

**Relevance to Pebble:** Lời cảnh báo về phương pháp luận cho mọi tuyên bố benchmarking — cùng tinh thần gold-holdout / honest-metric (chỉ số trung thực) của repo.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Profile assembled at analysis time** (from `docs/intent/constraints.md` + `docs/spec/capabilities/voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`):
Chương trình chính của Pebble là **phân loại ordinal nguy cơ tự sát trên văn bản (*text*)**, đặt câu hỏi liệu weak label từ LLM có *thực sự* tăng cường một cách trung thực cho bộ gold lâm sàng vốn khan hiếm hay không — bị ràng buộc bởi **gold-holdout** (train trên weak/LLM label, eval trên bộ CSSRS gold held-out tách biệt), split theo cấp độ subject, **có thể tái lập theo thiết kế** (stack đã pin + seed + multi-fold với std/CI được báo cáo), và các metric có nhận thức ordinal (QWK/MAE). Nhánh **voice** liền kề là một backbone WavLM/emotion2vec đóng băng (frozen) với 3 head MTL không đồng nhất (emotion CE + affect V/A **CCC** + **crisis dưới một sàn recall bắt buộc**), được cân bằng bằng Kendall uncertainty weighting; MSP-Podcast (A/V/D) + DAIC (crisis) là các mục tiêu hoán đổi "real-label" (nhãn thật) được nêu tên.

### Analysis — 15 Years of SER Progress (replication)
- **Overlap:** 23% (peripheral) — D1=1, D2=0, D3=1, D4=0, D5=0, D6=0, D7=2
  - (Σwᵢ·scoreᵢ = 3·1 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·2 = 6; 6/26 × 100 = 23%)
- **Closest on:** D7 (backbone match — nghiên cứu này benchmark trực tiếp *cả hai* backbone đang hoạt động của Pebble: các text encoder BERT/RoBERTa/DistilBERT/Electra và các speech encoder SSL wav2vec2/HuBERT) và D1 một phần (nó mô hình hóa cả emotion phân loại (categorical) *lẫn* valence/arousal/dominance liên tục, tuy là các mô hình riêng biệt, không phải head không đồng nhất kết hợp; không có safety head).
- **Best point (Framing / citation):** Bài báo chứng minh bằng thực nghiệm rằng các tuyên bố "tiến bộ" là *có điều kiện theo tập hợp mô hình/hyperparameter được so sánh một cách tùy tiện* — mô hình lớn hơn/mới hơn không tốt hơn một cách đơn điệu (monotonic), thứ hạng single-run không ổn định dưới phương sai hyperparameter khổng lồ, và chỉ có bootstrap 95% CI trên các thước đo tiến bộ mới giữ cho câu chuyện trung thực.
  - **How to apply to Pebble:** Trích dẫn trong phần evaluation-protocol / related-work của paper như một tiền lệ bên ngoài rằng một con số headline không có CI và không có tập so sánh cố định sẽ trình bày sai lệch về tiến bộ — củng cố quy tắc "multi-fold + báo cáo std/CI, không bao giờ dùng điểm ước lượng single-run" của Pebble và luận điểm trung thực gold-holdout (một tương tự trong domain SER cho khoảng cách 0.67 trong-LLM so với 0.385 honest-gold).
  - **Caveats:** Đã đọc toàn bộ phần thân chính (tr. 1–11); không bị paywall. Các phụ lục A/B/D/E (danh sách mô hình đầy đủ, chi tiết noise-robustness, phân tích nội dung ngôn ngữ) chỉ được lướt qua — không ảnh hưởng đến các chiều đã chấm điểm, vốn lấy từ phần thân chính. Overlap thấp là do thiết kế: không có domain sức khỏe tâm thần/khủng hoảng (D2=0), không có teacher-LLM distillation (D4=0), không có cân bằng loss MTL (D5=0), không có mục tiêu safety/recall-floor (D6=0). Giá trị nằm ở khung phương pháp luận (honest-eval framing) + sự gần gũi về backbone/corpus (MSP-Podcast/IEMOCAP/EmoDB chính là các mục tiêu hoán đổi real-label của nhánh voice), không phải chuyển giao kiến trúc.

## Deep research — full-PDF read (2026-07-10)

> Đọc đối chiếu với profile ViEmoSpeech hiện tại + Decision Register V-A…V-H
> (`docs/tasks/paper-deep-analysis.md`), KHÔNG phải profile nhánh text đã lưu trữ ở trên.
> Bài báo này là **đồng minh phương pháp luận** mạnh nhất của ViEmoSpeech về honest evaluation
> (V-G), với sự củng cố có tính chịu tải (load-bearing) cho V-B (tính trung thực SSL-so với-handcrafted) và V-H
> (vệ sinh benchmark). Phần "Child mental-health lens" được diễn giải lại thành một lăng kính
> transfer-validity/đạo đức cho ViEmoSpeech (SER trên phim truyền hình VN có diễn xuất, không phải lâm sàng).

### Source-access note

- **Đọc file PDF cục bộ toàn bộ** qua `pdftotext "docs/papers/bimodal-ser/pdfs/15-ser-15years-replication.pdf" -`
  (phần thân chính §§I–VII tr. 1–11 + Bảng I–VIII + Hình 1–4; danh mục tài liệu tham khảo; các phụ lục A/B/D/E
  là chi tiết hình/danh sách không làm thay đổi các con số dưới đây). File cục bộ là
  **arXiv:2508.02448v1 [cs.SD], 4 Aug 2025**, đóng dấu watermark "Under review".
- **Phiên bản published/venue:** WebSearch phân giải ra **IEEE Transactions on Affective
  Computing, Early Access, April 2026** (bản ghi publication MCML `tbs+25`). Không tìm thấy
  xung đột về số liệu giữa bản preprint và metadata của venue; bản mirror HTML trên arXiv
  (`arxiv.org/html/2508.02448`) tái tạo lại đúng nguyên văn mọi giá trị bảng được trích dẫn ở đây, nên
  các số liệu của bản v1 được coi là chính thức. Câu truy vấn tìm kiếm: *"Charting 15 years progress deep
  learning speech emotion recognition replication study Triantafyllopoulos Batliner Schuller
  MSP-Podcast UAR"* → https://mcml.ai/publications/tbs+25/ và https://arxiv.org/abs/2508.02448.
- **Các số liệu đã được xác thực trên web** (query nêu trên, phân giải tới https://arxiv.org/html/2508.02448):
  MSP-Podcast tuning UAR .650 [.642–.658]; OOD EmoDB .806 / IEMOCAP .617; IID↔OOD Spearman
  .909 / .843; các tương quan year/MACs/params đều gần bằng không; clean↔noisy Spearman .953 và
  mức suy giảm .609→.546; best text UAR (Llama-2) .564; FAU-AIBO2/5 baseline/winner/fusion
  .677/.703/.712 và .382/.417/.440; Gini .329; FAU-AIBO = giọng nói trẻ em Đức,
  school-disjoint (test Mont / train Ohm). Tất cả đều ✔ được xác thực đối chiếu với bản mirror HTML.

### What the paper actually does

**Design.** Một nghiên cứu tái lặp quy mô lớn định lượng "15 năm tiến bộ SER" từ INTERSPEECH
Emotion Challenge 2009 đến 2024, dưới **ngân sách tính toán cố định và hyperparameter cố định**
(khung "bitter lesson", §II-A). Hai bộ dữ liệu: **FAU-AIBO** (bộ dữ liệu challenge 2009 — giọng nói
*trẻ em* Đức, Wizard-of-Oz, 18,216 đoạn (chunks), ánh xạ vào tác vụ 2 lớp NEG/IDL và 5 lớp
A/E/N/P/R, mất cân bằng nặng nghiêng về neutral; **school-disjoint** train Ohm / test Mont)
và **MSP-Podcast-v1.11** (naturalistic; 44,586 train / 11,947 dev / 20,845 test; các phân vùng
**speaker-independent** chính thức; tác vụ phân loại 4 lớp được dùng ở đây). §III-A.

**Models.** 43 mô hình audio trải khắp toàn bộ dòng thời gian — các đặc trưng functional
openSMILE IS09–IS16 + eGeMAPS đưa vào MLP/LSTM, các CNN ImageNet (AlexNet/VGG/ResNet50/ConvNeXt/EfficientNet/Swin),
AudioSet CNN14, CRNN, x-vector ETDNN, AST, và các transformer SSL (wav2vec2-base/large + các biến thể,
HuBERT-base/large, các encoder Whisper-s/b/t) — cộng thêm 7 mô hình text trên transcript (BERT, RoBERTa,
DistilBERT, Electra; Llama-2, Llama-3, Mistral qua 4-bit LoRA). Giai đoạn khám phá (exploration): Adam, lr 1e-4,
30 epoch, batch 4, weighted cross-entropy; giai đoạn tuning grid-search optimiser/lr/batch cho top-5 mỗi tác vụ. §III-B.
**Metric: UAR (unweighted average recall = macro-recall)** "chỉ số chuẩn cho SER kể từ challenge 2009
vì nó tính đến sự mất cân bằng lớp." §III-C.

**Headline results (all ✔ corroborated).**
- *Mô hình mới hơn/lớn hơn có thắng không?* **Không, không theo cách đơn điệu.** Spearman ρ giữa UAR và năm
  công bố là .122/.093/.050 (FAU2/FAU5/MSP), so với MACs là .151/.230/.095, so với số lượng tham số
  −.083/.085/.026 — tất cả đều có bootstrap CI 95% trải dài từ âm sang dương (ví dụ, MACs trên
  FAU5 = .230 [−.087, .512]). Bảng II. "Phương sai lớn… không cho phép rút ra kết luận
  vững chắc." ✔
- *Kết quả tuyệt đối tốt nhất.* Exploration: FAU2 CNN14 .692, FAU5 ResNet50 .428, MSP w2v2-L-12-avd .609
  (HuBERT-L .570). Bảng I. Tuning nâng MSP lên **.650 [.642–.658]** cho w2v2-L-12-avd
  (được phát hành với tên `w2v2-L-12-emo`). Bảng IV. ✔ Trên FAU-AIBO, các mô hình đã tuning tốt nhất vẫn
  *ở gần hoặc dưới* mức baseline .677/.382 của challenge 2009, winners .703/.417, và fusion
  .712/.440 (Bảng III) — nghĩa là 15 năm deep learning **không** vượt qua rõ ràng challenge 2009
  trên chính dữ liệu của nó. ✔
- *Phương sai hyperparameter là hiệu ứng chi phối.* Hình 2 cho thấy độ phân tán UAR rất lớn qua các
  hyperparameter cho cùng một kiến trúc; "một lựa chọn hyperparameter khác… có thể đã dẫn đến… một
  thứ hạng khác giữa các kiến trúc." Các kết luận về tiến bộ đều **"phụ thuộc điều kiện vào tập hợp
  mô hình cụ thể được đánh giá"** (§V). ✔
- *Khả năng khái quát hóa OOD trung thực và có thể dự đoán từ IID.* Các mô hình huấn luyện trên MSP chuyển giao đến
  **EmoDB UAR .806** và **IEMOCAP .617** (w2v2-L-12-avd tốt nhất trên cả hai), và **Spearman IID↔OOD
  là .909 (EmoDB) / .843 (IEMOCAP)** — chọn mô hình tốt nhất theo IID cũng chọn được mô hình OOD tốt
  nhất. Bảng V. Year/MACs/params so với OOD vẫn gần bằng không (.112/.166/.172 EmoDB). ✔
- *Robustness.* Spearman UAR clean↔noisy (nhiễu cộng đô thị 0 dB) **.953**, nhưng robustness lại
  không tương quan với năm (.05)/MACs (.10)/params (.03); ngay cả mô hình tốt nhất cũng giảm
  **.609→.546**. §IV-A5. ✔
- *Nhánh text.* Best text UAR: MSP Llama-2 **.564** (≈ Llama-3 .563 / Mistral .560; Bảng VIII),
  "sẽ xếp thứ ba trong giai đoạn exploration của chúng tôi, thua sát nút HuBERT-L (.570)"
  — text đơn thuần có tính cạnh tranh trên giọng nói naturalistic nhưng thấp hơn audio tốt nhất; trên FAU-AIBO
  text yếu hơn (nội dung ngôn ngữ Wizard-of-Oz hạn chế). Lợi thế về valence của Whisper được quy cho
  *nội dung ngôn ngữ ngầm (implicit)*, không phải paralinguistic mới (§IV-A1, trích dẫn ref [12]). ✔
- *Complementarity (tính bổ trợ).* Các mô hình audio nhất trí với nhau nhiều hơn (w2v2/CNN14 .815 trên FAU2) so với
  với text (w2v2/DistilBERT .666); cặp *bổ trợ nhất* là một CNN không phải transformer
  (EfficientNet) + LLM text (Llama-2), vì SSL transformer "đã nắm bắt ngầm ngôn ngữ học
  rồi." §IV-B1, Hình 4. ✔
- *Probing (Bảng VI).* Mô hình SER tốt hơn mã hóa các đặc trưng âm học mạnh hơn, nhưng **tất cả
  transformer đều mã hóa mean pitch (μ(P) lên tới .959) tốt hơn nhiều so với pitch variability
  (σ(P) ≈ .237) và jitter** — *động lực học (dynamics)* của pitch bị mã hóa dưới mức. ✔
- *Individual fairness (Bảng VII).* Gini theo cấp độ speaker **.329** trên MSP (bất bình đẳng vừa phải);
  các mô hình UAR cao hơn thì *công bằng hơn* trên MSP (ρ = −.344) nhưng mô hình mới hơn/lớn hơn lại *kém
  công bằng hơn* trên FAU-AIBO (ρ lên tới .55 so với params) — công bằng không tự nhiên đi kèm với quy mô.
  ✔
- *Models ≠ humans.* Độ khó của mô hình chỉ tương quan yếu với mức độ bất đồng giữa các annotator con người
  (ρ .33/.20), và mức độ đồng thuận cao hơn giữa con người **không** dẫn đến UAR cao hơn (ρ −.38/−.07). §IV-A.

### Parts directly useful for ViEmoSpeech (tagged with Decision IDs)

1. **UAR = macro-recall như *chỉ số* mất cân bằng chuẩn mực, cộng với bootstrap CI 95% trên mọi con số
   headline và trên mọi tương quan "tiến bộ" (Bảng II–IV).** `[V-G]` Đây chính xác là công cụ ADR-002
   cần: báo cáo recall trung bình theo lớp (UAR), không bao giờ dùng accuracy thuần, và đính kèm bootstrap CI
   để một điểm ước lượng single-run không thể ngụy trang thành một thứ hạng. **Rủi ro chuyển giao: không có** — thuần
   phương pháp, độc lập với register.
2. **Split speaker-independent / group-disjoint như baseline không thể thương lượng** — FAU-AIBO
   là *school-disjoint* (Mont/Ohm), MSP dùng các phân vùng *speaker-independent* chính thức. `[V-G]`
   Tiền lệ bên ngoài trực tiếp cho speaker-disjoint + whole-series holdout của ViEmoSpeech; hai
   corpus SER được trích dẫn nhiều nhất (IEMOCAP/EmoDB) bị chỉ trích chính xác vì *thiếu* một
   scheme speaker-independent đã được thiết lập (§II). **Rủi ro chuyển giao: không có** — đây chính xác là chế độ (regime) của chúng ta.
3. **Tính hợp lệ của việc chọn IID→OOD: Spearman .909/.843 (Bảng V).** `[V-G]` Biện minh cho eval
   hai tầng của chúng ta — tune/select trên dev split speaker-disjoint, sau đó xác nhận trên whole-series OOD
   holdout (ADR-002). **Rủi ro chuyển giao: thấp** — các bộ OOD của họ là *acted* (EmoDB/IEMOCAP) và do đó
   "dễ hơn"; whole-series holdout của chúng ta cùng thể loại phim truyền hình, nên độ ổn định ρ≈.9 IID→OOD là một
   kỳ vọng hợp lý-nhưng-chưa-được-chứng-minh đối với chúng ta, cần đo lường chứ không giả định.
4. **"Tiến bộ có điều kiện theo tập hợp mô hình + hyperparameter được so sánh" + phương sai HP khổng lồ
   (Hình 2, §V).** `[V-B]` `[V-G]` Mọi hàng bảng xếp hạng backbone chúng ta trích dẫn (WavLM so với emotion2vec
   so với Whisper) phải mang theo ngân sách hyperparameter và một CI, và được đóng khung là *có điều kiện*.
   **Rủi ro chuyển giao: không có** — yếu tố gây nhiễu (confound) này thuộc về kiến trúc, không thuộc domain.
5. **SSL/quy mô KHÔNG vượt trội một cách đơn điệu so với handcrafted (Bảng I/II): year/MACs/params ≈ 0
   tương quan với UAR; trên FAU-AIBO, DL đã tuning tốt nhất vẫn ở mức/dưới mức fusion .712/.440 của 2009.**
   `[V-B]` Mô hình chiến thắng duy nhất (w2v2-L-12-avd, .650 MSP / .806 EmoDB OOD) thắng vì nó được
   **domain-adapted** (pre-train trên MSP-Podcast dimensional SER trước), không phải vì nó
   lớn hơn — một mệnh lệnh ưu tiên một **encoder init đã VN-adapted/PhoWhisper** (vn-06) hơn là kích thước
   mô hình lớn, và giữ một nhánh openSMILE/eGeMAPS handcrafted một cách trung thực trong bậc thang V-B.
   **Rủi ro chuyển giao: thấp** — WavLM/emotion2vec (các ứng viên thực tế của chúng ta) *không* nằm trong số 43 mô hình của họ, nên
   thứ hạng cụ thể không chuyển giao được; nguyên tắc *domain-adapted-thắng-lớn-hơn* thì có.
6. **Khoảng trống probing: transformer mã hóa dưới mức pitch variability và jitter (Bảng VI: σ(P) .237
   so với μ(P) .959).** `[V-B]` `[V-D]` Kênh *dynamics* của F0 — chính xác là nơi thanh điệu từ vựng tiếng Việt
   nằm ở đó (contour + phonation, vn-06/vn-13) — là điểm mù của SSL. Bằng chứng cụ thể
   cho việc thêm một vector phonation/pitch-dynamics handcrafted rõ ràng (jitter/shimmer/HNR/H1-H2/
   σ(F0)) bên cạnh backbone SSL. **Rủi ro chuyển giao: trung bình-thuận lợi** — đo trên
   EmoDB tiếng Đức, không phải VN; nếu có khác biệt thì khoảng trống này có lẽ sẽ *lớn hơn* trên F0 tiếng Việt vốn mang tải thanh điệu, đó
   chính là điểm mở nghiên cứu của chúng ta.
7. **Cảnh báo vệ sinh dữ liệu (§I–II): FAU-AIBO "bị âm thầm bỏ rơi"; MSP-Podcast tái phát hành
   ~hàng năm với thay đổi kích thước + nhãn → các con số giữa các paper không thể so sánh; họ pin phiên bản v1.11.**
   `[V-H]` Yêu cầu ViEmoSpeech pin một phiên bản/hash corpus đóng băng cho mỗi con số được báo cáo
   (bất biến về provenance). **Rủi ro chuyển giao: không có** — chế độ thất bại về versioning là phổ quát.
8. **Fairness Gini theo cấp độ speaker (Eq. 1, Bảng VII).** `[V-G]` Một báo cáo utility/Gini
   theo từng speaker đã sẵn sàng để thêm vào bên cạnh macro-F1 — phơi bày liệu có một vài diễn viên
   gánh phần lớn điểm số hay không (một rủi ro thực trong một corpus phim truyền hình 2-series, nặng về diễn viên). **Rủi ro chuyển giao: thấp** — áp dụng
   trực tiếp được, và cấp bách hơn với chúng ta do quy mô diễn viên nhỏ.

### How each part helps ViEmoSpeech succeed

- **Eval protocol (1,2,3,8) → ADR-002 eval spec.** Áp dụng UAR/macro-recall + bootstrap-CI làm
  mặc định báo cáo trong `docs/spec/capabilities/extraction-pipeline.md` và bảng eval của method-paper;
  thêm một hàng Gini theo từng speaker. Cụ thể: bảng baseline của chúng ta (vn-08 86.6, vn-10 0.87,
  THAI-SER WA~60, MSP CCC) nên in kèm CI và macro-recall, và đánh dấu các hàng VN bị rò rỉ speaker
  — bài báo này là trích dẫn khiến việc đánh dấu đó trở thành *chuẩn phương pháp luận*, không phải thiên vị.
- **Two-tier holdout (3) → whole-series OOD gate.** Đối xử với series held-out y hệt cách
  bài báo này đối xử với EmoDB/IEMOCAP: select trên dev speaker-disjoint, báo cáo series holdout
  như OOD, và *kỳ vọng* (theo ρ≈.9) thứ hạng sẽ giữ nguyên — sự khác biệt khi đó là một cờ đỏ thực
  đáng được báo cáo, không phải nhiễu.
- **HP-conditioned framing (4) → kỷ luật ablation V-B/V-A.** Khi chúng ta khẳng định "WavLM ≥ X" hay
  "learned fusion > rule fusion", chạy ≥3 cấu hình hyperparameter cho mỗi arm và báo cáo khoảng dao động;
  trích dẫn bài báo này rằng các cải thiện kiến trúc thường xuyên bị gây nhiễu bởi tuning.
- **Domain-adapted init (5) → lựa chọn backbone audio.** Ưu tiên một checkpoint SSL VN-/PhoWhisper-adapted hoặc
  emotion-warm-started hơn là một mô hình lạnh (cold) lớn hơn; giữ một nhánh eGeMAPS-functionals-vào-MLP
  trong bậc thang như sàn trung thực "kiểu 2009" — bài báo cho thấy cái sàn đó không thấp hơn SSL bao nhiêu
  trên dữ liệu mất cân bằng.
- **Probing gap (6) → phép đo tone×emotion + đặc trưng phonation.** Đây là phát hiện liên quan nhất đến
  tính mới lạ: chạy eGeMAPS linear-probe của bài báo trên các layer encoder *của chúng ta*, kỳ vọng
  σ(F0)/jitter probe kém, và dùng đó làm luận cứ trực tiếp cho nhánh phonation handcrafted
  và cho việc đóng khung tone×emotion như một cuộc cạnh tranh kênh F0-*dynamics* (điểm nhấn V-D).
- **Version-pinning (7) → bất biến provenance.** Mọi con số phát hành của ViEmoSpeech mang theo
  ID snapshot corpus (đã là một bất biến thuộc dòng I); bài báo này là câu chuyện cảnh báo bên ngoài
  (versioning của MSP-Podcast) khiến nó trở thành một yêu cầu về *khả năng so sánh*, không chỉ là ghi sổ sách.

### Transfer-validity / ethics lens (ViEmoSpeech)

- **Góc độ giọng nói trẻ em là thực nhưng gián tiếp.** FAU-AIBO là giọng nói *trẻ em Đức*, nên
  các cảnh báo của bài báo về register trẻ em (Wizard-of-Oz → nội dung ngôn ngữ hạn chế → nhánh text yếu;
  mất cân bằng lớp neutral nặng) là một lời cảnh báo thực sự cho bất kỳ ứng dụng hướng đến trẻ em nào — nhưng ViEmoSpeech
  là **phim truyền hình VN người lớn/diễn viên**, nên việc chuyển giao chỉ là tương tự, không phải khớp về quần thể (population match). Bài học
  chuyển giao được là sự phụ thuộc register của nhánh text, đã là trung tâm trong tổng hợp xuyên suốt của chúng ta.
- **Thương hiệu honest-eval chuyển giao một cách sạch sẽ.** Mọi thứ trong V-G (macro-recall, speaker-disjoint,
  bootstrap CI, xác nhận OOD, fairness Gini) là phương pháp, không phải domain — nó chuyển giao sang phim
  VN có diễn xuất mà không cần dè dặt. Đây là giá trị cốt lõi của bài báo đối với chúng ta.
- **Cảnh báo về scale của metric.** UAR phân loại của họ không phải là cùng một đối tượng với **CCC** V/A của chúng ta hay
  **recall-floor** distress của chúng ta; nhập khẩu *kỷ luật* (CI, split tách biệt, khoảng dao động) nhưng không phải
  metric — CCC cần cách xử lý bootstrap-CI riêng, và recall-floor cần báo cáo fixed-recall/
  độ chính xác dạng float, không phải UAR.
- **Tính trung thực của dữ liệu diễn xuất (acted).** Bài báo nhiều lần chỉ ra rằng EmoDB/IEMOCAP/RAVDESS/CREMA-D
  là *acted và điển hình (prototypical)*, đó là lý do vì sao UAR OOD (.806) lại *cao hơn* IID naturalistic (.650) —
  "các bộ dữ liệu dễ hơn nhiều." Hỗ trợ trực tiếp cho khung acted-drama-proxy V-F của chúng ta: emotion diễn xuất
  làm tăng điểm số một cách giả tạo, nên một điểm ViEmoSpeech cao phải được đọc trong bối cảnh sự dễ dàng đó, và mọi
  tuyên bố lâm sàng/distress vẫn chỉ là proxy, không bao giờ là chẩn đoán.
- **Đạo đức về fairness.** Gini .329 trên giọng nói naturalistic = một vài speaker chiếm phần lớn utility;
  trong một corpus phim truyền hình có ít diễn viên, đây là một rủi ro về công bằng đáng được báo cáo theo từng speaker,
  đặc biệt trước bất kỳ ứng dụng affect-inference downstream nào.

### Limitations & open questions for ViEmoSpeech

- **Mâu thuẫn so với bảng xếp hạng backbone của bimodal-08.** bimodal-08 báo cáo một thứ hạng
  naturalistic rõ ràng **Whisper-V3 > XEUS > WavLM > HuBERT > Wav2Vec2**; mô hình chiến thắng MSP-Podcast của
  chính bài báo này lại là một **wav2vec2 domain-adapted** (w2v2-L-12-avd .650) với HuBERT-L đứng thứ hai (.624 tuning) và các
  encoder Whisper *thấp hơn* cả hai (Whisper-t .387 exploration), **và** nó cho thấy các thứ hạng
  năm/kích thước/kiến trúc không ổn định dưới hyperparameter và lựa chọn tập mô hình (ρ≈0, CI vắt qua số 0).
  ⇒ Chúng ta không thể coi *bất kỳ* bảng xếp hạng backbone đơn lẻ nào (kể cả của bimodal-08) là đã ổn định; nhánh V-B
  phải A/B WavLM so với emotion2vec so với Whisper-encoder so với một wav2vec2 domain-adapted *trên chính clip của chúng ta
  với CI*, không kế thừa một thứ hạng có sẵn. Bài báo này là lý do để không tin tưởng bảng xếp hạng.
- **Mâu thuẫn so với các baseline VN bị thổi phồng do rò rỉ (leak-inflated).** UAR trung thực speaker-independent
  4 lớp naturalistic đạt đỉnh ở **.650**; vn-08 (86.6%) và vn-10 (0.87 UA) nằm cao hơn hẳn mức đó chính xác
  vì chúng không speaker-disjoint trên dữ liệu naturalistic. Bài báo này là điểm neo bên ngoài sạch nhất của chúng ta
  cho thấy ~0.6 macro-recall — chứ không phải ~0.87 — mới là trần trung thực trên dữ liệu naturalistic.
- **Không có fusion, không có ngôn ngữ thanh điệu, không có CCC.** Nghiên cứu chỉ xét từng modality riêng lẻ tại một thời điểm
  (audio *hoặc* text, chỉ có phân tích lỗi về tính bổ trợ — không bao giờ là *learned* fusion), không kiểm tra bất kỳ
  ngôn ngữ thanh điệu nào, và chỉ báo cáo UAR phân loại — **không có CCC V/A** và **không có head lâm sàng/distress**.
  Vì vậy nó thúc đẩy mạnh V-G/V-B/V-H nhưng im lặng về V-A (kiến trúc fusion), V-C (robustness với nhiễu
  ASR — nó dùng transliteration sạch của con người cho FAU-AIBO và ASR Whisper-large-v2 cho MSP
  nhưng không bao giờ ablate lỗi ASR), các chi tiết thanh điệu của V-D, V-E, và V-F ngoài lời cảnh báo acted-proxy.
- **Khoảng trống so với kế hoạch của chúng ta: họ không có compute để giải quyết câu hỏi về scaling.** Họ nói rõ là không
  thể kiểm tra scaling trong cùng một kiến trúc hay các audio-LM lớn (ALM), và ghi nhận việc bỏ qua ALM là
  "thiếu sót quan trọng nhất" của họ (§VI). Do đó cược small-fusion-over-ALM của chúng ta (bimodal-09) *không* bị
  mâu thuẫn bởi bài báo này — nó chỉ đơn giản nằm ngoài phạm vi của bài báo, và phát hiện diminishing-returns
  của họ là bằng chứng hỗ trợ nhẹ cho việc không theo đuổi kích thước.
- **Câu hỏi mở cho chúng ta:** chạy eGeMAPS layer-wise linear probe của họ (μ(P)/σ(P)/jitter/shimmer/
  HNR/formants) trên encoder VN-adapted của chúng ta — liệu σ(F0)/jitter có probe *tệ hơn nữa* trên tiếng Việt
  (nơi thanh điệu mang tải F0) so với mức .237 họ báo cáo trên EmoDB tiếng Đức hay không? Một khoảng trống VN lớn hơn sẽ là
  bằng chứng đo lường trực tiếp cho luận điểm cạnh tranh kênh F0 tone×emotion (V-D) mà chưa có bài báo nào từng
  đưa ra.
