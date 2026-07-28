# Paper 14 — A Comprehensive Survey on Multi-modal Conversational Emotion Recognition with Deep Learning

> Bản dịch tiếng Việt của [14-mcer-survey-acm-tois.md](14-mcer-survey-acm-tois.md) — cập nhật 2026-07-10.

- **Authors:** Yuntao Shou, Tao Meng, Wei Ai, Nan Yin, Keqin Li
- **Venue / year:** ACM TOIS (accepted; arXiv 2312.05735, revised 2025)
- **Links:** abs https://arxiv.org/abs/2312.05735 · PDF `pdfs/14-mcer-survey-acm-tois.pdf` (bản arXiv; ACM paywalled)
- **Group:** survey / benchmark

**Summary:** Phân loại (taxonomy) các cơ chế fusion (context-free / sequential / speaker-differentiated / speaker-relationship) + các bộ dữ liệu MCER (IEMOCAP, MELD, …).

**Relevance to Pebble:** Tài liệu tham chiếu nền (backbone reference) cho phần benchmark + evaluation-protocol của related-work.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Pebble profile used (assembled at analysis time):**
- Chương trình chính (`docs/intent/constraints.md`): phân loại ordinal suicide-risk trên **văn bản** (**text**); teacher-LLM tạo silver labels → đánh giá trên gold-holdout; các loss/metric ordinal-aware (QWK, MAE, macro-F1); BERT-family encoder ~250M tham số.
- Nhánh voice liền kề (`docs/spec/capabilities/voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`): frozen backbone SSL **WavLM-Large / emotion2vec** + shared trunk, **3 head không đồng nhất (heterogeneous)** — emotion CE + hồi quy **affect valence/arousal CCC** + **crisis BCE dưới một sàn recall bắt buộc (0.90)** — được cân bằng bởi **Kendall uncertainty weighting**; task này *đang bị chặn bởi proxy labels* và rõ ràng cần các bộ dữ liệu continuous-affect + crisis thực sự.
- Hướng phát triển tiếp theo: fusion voice+text.

### Analysis — MCER survey (Shou et al., ACM TOIS)
- **Scores:** D1=0, D2=0, D3=1, D4=0, D5=0, D6=0, D7=1 → (3·0 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·1) / 26 × 100 = **8%** (**peripheral**, <40%)
- **Closest on:** D3 (các bộ dữ liệu cảm xúc gồm cả continuous-affect — SEMAINE V/A/Expectancy/Power, CH-SIMS intensity, MuSE valence/arousal/dominance) và D7 (phía text: BERT/RoBERTa là bộ trích xuất tiêu chuẩn — khớp với nhánh text của Pebble; nhưng phía audio dùng COVAREP/openSMILE/LibROSA/OpenEAR cổ điển, **không phải** dòng SSL WavLM/emotion2vec mà nhánh voice của Pebble đang dùng).
- **Why the rest score 0:** đây là một survey phân loại cảm xúc đơn nhiệm (single-task) — không có các head MTL không đồng nhất (D1), không thuộc lĩnh vực sức khỏe tâm thần/crisis (D2), không có distillation silver-label từ teacher-LLM (D4), không có cơ chế cân bằng loss MTL (uncertainty/GradNorm/PCGrad) (D5), và không có *mục tiêu* recall-floor/an toàn nào (D6; Bảng 6–8 chỉ báo cáo recall/AUC và ghi nhận các mô hình thiên về recall như EmotiCon đạt 81.6% recall là điều *quan sát được*, chứ không phải *được thiết kế sẵn* để đạt).
- **Best point (Dataset to reuse):** danh mục dữ liệu ở §2 phơi bày ba corpus hội thoại mang nhãn **continuous-affect** thực sự — **MuSE** (valence/arousal/dominance, người tham gia thật), **SEMAINE** (V/A/Expectancy/Power ∈ [-1,1]), **CH-SIMS** (continuous sentiment intensity) — đúng loại nhãn mà head affect-CCC của voice hiện đang giả lập bằng một proxy Russell-circumplex trên RAVDESS.
  - **How to apply to Pebble:** đưa MuSE + SEMAINE cho `find-dataset` (kiểm tra license/gate) như các ứng viên bổ sung bên cạnh phương án hoán đổi MSP-Podcast / DAIC đã được nêu trong `docs/tasks/voice-mtl-heads.md` M5 — chúng cung cấp cho head affect các mục tiêu V/A continuous *thực sự* để các chỉ số CCC trở nên có ý nghĩa khoa học.
- **Caveats:** điểm số này được chấm chủ yếu từ bản PDF arXiv (§1–3, các bảng benchmark 6–8 ở §6); bản ACM bị paywall và §7 (applications) chưa được đọc — nếu §7 liệt kê mental-health monitoring như một ứng dụng thì điều đó sẽ đẩy D2 lên mức partial yếu nhưng không thay đổi phân loại domain. Đọc kỹ backbone xác nhận text=BERT/RoBERTa/GLOVE/TextCNN, audio=các bộ công cụ cổ điển (không có SSL), nên D7 vẫn giữ ở mức partial.

## Deep research — full-PDF read (2026-07-10)

> Được phân tích đối chiếu với **hồ sơ ViEmoSpeech hiện hành + Decision Register (V-A…V-H)** trong
> `docs/tasks/paper-deep-analysis.md`. Khối "Analysis (overlap with Pebble)" cũ ở trên dùng
> hồ sơ text-stream đã lưu trữ (archived) (D1–D7) và chỉ được giữ lại như lịch sử — hãy trích dẫn V-A…V-H bên dưới.

### Source-access note

- **PDF read:** `pdftotext docs/papers/bimodal-ser/pdfs/14-mcer-survey-acm-tois.pdf` → 3,566 dòng,
  đọc toàn bộ (intro §1, datasets §2, feature-extraction §3, taxonomy §4, eval-metrics §5,
  benchmark §6 Bảng 6–9, applications §7, privacy §8, challenges §9, future §10). Bản PDF cục bộ là
  **arXiv:2312.05735v2 (13 Nov 2025)**.
- **Web-validated:**
  - *Venue.* Truy vấn "Shou … Comprehensive Survey MCER arXiv 2312.05735 venue accepted journal" →
    `https://arxiv.org/abs/2312.05735` (đã fetch): **không có trường `Journal reference`; Comments = "36 pages,
    10 figures"; tác giả = Shou, Meng, Ai, Fangze Fu, Nan Yin, Keqin Li.** ✖ **Tuyên bố "ACM TOIS
    (accepted; revised 2025)" trong stub không được xác thực** — arXiv cho thấy đây là một preprint không có venue, và header
    running của PDF "J. ACM, Vol. 37, No. 4, Article 111. Publication date: August 2025" là **placeholder mặc định
    của template `acmart`**, không phải một sự chấp nhận đăng J. ACM/TOIS thật. Xem đây là **preprint, venue
    chưa xác nhận** (cũng được liệt kê trên SSRN abstract_id=5017731). Danh sách tác giả v1 (Shou/Meng/Ai/Yin/Li) khác
    với v2 (thêm Fangze Fu); một index liệt kê "Guinan Guo" — danh sách tác giả không ổn định qua các phiên bản.
  - *Dimensional corpora (V-E).* Truy vấn "SEMAINE valence arousal expectancy power … CH-SIMS -1..1" →
    CH-SIMS ACL 2020 (`https://aclanthology.org/2020.acl-main.343/`, `https://thuiar.github.io/publication/chsims/`)
    xác nhận **CH-SIMS = sentiment intensity -1..+1, nhưng chỉ có 2,281 clip** — tuyên bố ở §2.8 của survey rằng
    "**khoảng 10,000** mẫu tiếng Trung ở cấp câu" là ✖ **bị thổi phồng/không chính xác** (con số chuẩn = 2,281).
    SEMAINE V/A được xác nhận là continuous; tuyên bố 4 chiều của survey (V/A/Expectancy/Power ∈[-1,1]) ở mức
    ≈ (annotation đa chiều FeelTrace được ghi nhận cho SEMAINE; tìm kiếm nhanh bên ngoài chỉ thấy rõ V/A). Bài học: **không nên trích dẫn
    số liệu thống kê per-dataset của survey này một cách thiếu phê phán.**
- Các con số benchmark trong Bảng 6–9 là **tổng hợp do chính survey biên soạn** (các tác giả tự lập lại bảng
  số liệu từ ~40 bài báo gốc); chúng không thể tái lập độc lập đối chiếu với một nguồn ngoài duy nhất,
  nên mỗi con số đều được gắn nhãn ≈ (survey-table) kèm tham chiếu bảng.

### What the paper actually does

Một survey phương pháp luận về **Multi-modal Conversational Emotion Recognition (MCER)** — nhận diện cảm xúc
của *từng utterance trong một hội thoại* bằng text+audio+video với **ngữ cảnh hội thoại (conversational context)**. Điểm mới được tuyên bố của bài
là một **taxonomy được tổ chức theo cách mô hình nắm bắt động lực hội thoại (conversational dynamics)**, được đối lập rõ ràng
(§1) với các survey trước tổ chức "theo tổ hợp modality" hoặc "theo giai đoạn tác vụ (extract/fuse/classify)":

- **Taxonomy (§4, Fig. 3) — bốn nhóm, xếp theo cấu trúc context/speaker tăng dần:**
  1. **Context-free** (§4.1) — mỗi utterance độc lập; đây là nơi các phương pháp *fusion* của survey
     xuất hiện: **Add** (Eq. 3), **Concatenation** (Eq. 4), **SVM** (Eq. 5), **Multiple-Kernel-Learning**
     (Eq. 6), **Select-Additive-Learning CNN**, **Tensor Fusion (TFN)**. Tất cả đều là **fusion sớm / bậc thấp (early / low-order fusion)**.
  2. **Sequential context** (bc-LSTM, họ DialogueRNN, Transformer/HiTrans) — mô hình hóa phụ thuộc
     thời gian giữa các utterance.
  3. **Distinguishing-speaker** (DialogueRNN, COSMIC, EmotionIC) — điều kiện hóa theo danh tính/trạng thái speaker.
  4. **Speaker-relationship** (DialogueGCN, RGAT, DAG-ERC, MM-DFN, GraphCFC, LR-GCN) — GCN/GAT trên một
     đồ thị hội thoại; **tuyên bố thực nghiệm chủ chốt (headline) của survey là nhóm này thắng thế** (§6).
- **"Cấu trúc nào thắng" (§6, Bảng 6–9, WF1 trên IEMOCAP/MELD):** context-free kém nhất (SAL 49.2/58.8,
  SVM 48.7/56.4, TFN 54.2/56.7 IEMOCAP/MELD; <50% F1 trên MELD với TextCNN/LFM); sequential ≈
  speaker-differentiated (WF1 IEMOCAP tầm giữa 60%); **speaker-relationship GCN tốt nhất** — GraphCFC đạt AUC cao nhất
  **89.18%** (≈, Bảng 7), LR-GCN đạt per-class F1 tốt nhất (≈, Bảng 8–9) với cái giá là 15.77M tham số / 21s
  trên IEMOCAP / 147s trên MELD inference. **EmotiCon recall 81.63%** (≈, Bảng 7) được gắn cờ là hướng-recall
  ("favors recall … useful where missing emotional signals is more critical than false alarms").
- **Datasets (§2, Bảng 1–2 + §2.8–2.9):** IEMOCAP (6-class, 12.46h), MELD (7-class, Friends TV),
  DailyDialog (6-emo text), EmoryNLP (7 text), EmotionLines (7 text), EmoContext (3 text), cộng thêm
  **CH-SIMS** (Chinese/Mandarin video, **sentiment intensity −1..+1 + 3-class**) và **MuSE** (English+Spanish,
  **continuous valence/arousal/dominance**). **SEMAINE** = 95 hội thoại / 5,798 utt, **4 chiều
  Valence/Arousal/Expectancy/Power continuous [−1,1]**. **Không có tiếng Việt; không có corpus lexical-tone;**
  bộ tonal-language duy nhất (CH-SIMS) được xử lý như *sentiment*, tone chưa bao giờ là một biến.
- **Feature extractors (§3.3, Bảng 5):** text = TextCNN/GLOVE/Word2Vec/**BERT/RoBERTa/T5**; audio =
  **các bộ công cụ cổ điển COVAREP/openSMILE/LibROSA/OpenEAR** (MFCC, pitch, eGeMAPS; COVAREP còn có NAQ/MDQ/
  tham số glottal LF) — **không có SSL (WavLM/HuBERT/emotion2vec)** ở đâu cả; video = 3D-CNN/Facet/OpenFace/OKAO.
- **Eval metrics (§5):** chỉ **Accuracy, WA, F1, WF1** — toàn bộ đều là categorical. Đáng chú ý là WA được định nghĩa
  (Eq. 36) với trọng số **tỉ lệ nghịch với số lượng mẫu của class** ("nhiều mẫu hơn → trọng số nhỏ hơn"),
  tức là một **biến thể macro/balanced-accuracy**, *chứ không phải* quy ước SER chuẩn trong đó WA = overall
  (frequency-weighted) accuracy và UA = unweighted. **Không có metric regression / CCC / Pearson nào xuất hiện
  dù SEMAINE/MuSE/CH-SIMS đều là continuous.**
- **Challenges (§9):** thiếu dữ liệu (IEMOCAP 11,098 / MELD 5,810 / SEMAINE 394 utt), tính không đồng nhất+nhiễu,
  **mất cân bằng class** (MELD fear 1.91%, disgust 2.61% → "0% accuracy trên một số thuật toán," Bảng 9),
  đánh đổi giữa tính nhất quán (consistency) và tính bổ trợ (complementarity), hợp tác đa mô hình (multi-model collaboration).
- **Future work (§10):** sinh dữ liệu (VAE/GAN/diffusion); fusion sâu hơn (deformable temporal conv +
  dynamic gating); **unbiased learning §10.3 = focal loss / label-distribution-aware-margin (LDAM) + 
  prototype contrastive + category-balanced training**; khôi phục modality bị thiếu (missing-modality recovery); zero-shot qua
  CLIP/Whisper/MLLM; **multi-label §10.6 = Sigmoid-over-Softmax + label-graph + uncertainty-aware + 
  head hồi quy emotion-intensity phụ (aux)**; dynamic-dialogue (TCN/dynamic-GNN); lightweight (KD/pruning/
  quantization). §7.4 liệt kê **medical/mental-health** như một ứng dụng (sàng lọc sớm depression/anxiety)
  nhưng chỉ trong một đoạn văn chung chung.

### Parts directly useful for ViEmoSpeech (tagged by Decision ID)

1. **Bản đồ nhãn dimensional-vs-categorical (V-E).** Danh mục này là bản đồ rõ ràng nhất về các corpus hội thoại công khai mang
   nhãn *categorical* (IEMOCAP-6, MELD-7, DailyDialog-6, EmoryNLP-7,
   EmotionLines-7, EmoContext-3) so với nhãn *dimensional continuous* (SEMAINE V/A/Expectancy/Power [−1,1];
   MuSE V/A/D; CH-SIMS intensity −1..+1). **CH-SIMS là corpus duy nhất mang *đồng thời* một nhãn categorical
   3-class VÀ một intensity continuous** — đúng hình dạng hybrid mà ViEmoSpeech đề xuất (7-class + 
   V/A 1–5 + distress). Rủi ro chuyển giao: **partial** — tất cả đều là *hội thoại, cấp dialogue, phi thanh điệu
   (hoặc sentiment tiếng Quan Thoại)*; hữu ích như **tiền lệ về label-scheme cho một head hybrid**, chứ không phải làm dữ liệu huấn luyện.
2. **Công thức unbiased-learning / rare-class (V-E + V-G).** §9.3 + §10.3 đưa ra bộ đòn bẩy cụ thể cho mất cân bằng —
   **focal loss, LDAM (label-distribution-aware margin), prototype-contrastive, category-balanced
   sampling** — được thúc đẩy bởi phát hiện rằng MELD fear/disgust sụp về ~0% F1 (Bảng 9)
   ở mức phổ biến 1.91%/2.61%. Áp dụng trực tiếp cho sàn rare-class ≥50-clip của ViEmoSpeech (ADR-002) và
   lựa chọn loss cho head 7-class. Rủi ro chuyển giao: **strong** — mất cân bằng là hiện tượng độc lập với corpus; đây là
   nội dung dễ chuyển giao nhất trong survey.
3. **Taxonomy cơ chế fusion, xem như *ladder baseline early-fusion* (V-A).** §4.1 đưa ra các nguyên hàm fusion bậc thấp
   kinh điển kèm phương trình — **Add (Eq. 3) < Concat (Eq. 4) < Tensor-Fusion/MKL** —
   và §6 xác nhận fusion context-free là mức sàn. Đây là các hàng baseline **learned-fusion** trung thực
   cho ablation V-A của ViEmoSpeech (bên dưới cross-attention / gated / Q-Former). Rủi ro chuyển giao: **medium** —
   các *nguyên hàm* chuyển giao được sang một mô hình bimodal cấp utterance, nhưng **câu trả lời headline "mô hình nào
   thắng" của survey (speaker-relationship GCN) thì KHÔNG** (xem §Child/transfer lens).
4. **Định nghĩa metric đánh giá + một cái bẫy thuật ngữ (V-G).** §5 định vị bộ metric categorical
   (Accuracy/WA/F1/WF1) mà các bài IEMOCAP/MELD báo cáo, giúp bảng baselines của ViEmoSpeech nêu rõ tính
   khả so sánh. **Lưu ý load-bearing:** survey này định nghĩa **WA là inverse-frequency-weighted
   (≈ macro/balanced accuracy)** — *ngược* với quy ước SER chủ đạo "WA = weighted (overall) accuracy /
   UA = unweighted" (như được dùng bởi THAI-SER vn-11 và MSP bimodal-12). ViEmoSpeech phải **nêu rõ công thức
   metric của mình một cách tường minh và ưu tiên macro-F1 (+ CCC cho V/A)** thay vì dùng một "WA" mơ hồ.
5. **Quan sát hướng-recall cho head distress (V-F).** Recall 81.63% của EmotiCon (≈, Bảng 7),
   được đóng khung là chấp nhận được ở nơi mà "bỏ sót tín hiệu cảm xúc quan trọng hơn là báo động giả," là một
   tiền lệ có thể trích dẫn nhưng yếu cho một mục tiêu recall-first — **chỉ là quan sát, không bao giờ được thiết kế sẵn**
   (không có huấn luyện recall-floor nào trong survey). Rủi ro chuyển giao: **weak** — chỉ hỗ trợ cách *đóng khung* recall-floor
   của ViEmoSpeech, không cung cấp phương pháp.
6. **Ghi chú thiết kế multi-label (V-E, hướng tới tương lai).** §10.6 đề xuất **Sigmoid-over-Softmax + head hồi quy
   emotion-intensity phụ (aux)** cho các cảm xúc đồng xuất hiện — chỉ liên quan nếu sau này ViEmoSpeech chuyển
   từ single-label 7-class sang multi-label; head single-label hiện tại không cần điều này. Đã ghi nhận, chưa hành động.

### How each part helps ViEmoSpeech succeed

- **(1 → label spec, `tools/labeler/SPEC.md` + V-E):** trích dẫn CH-SIMS như tiền lệ rằng một
  corpus có thể mang đồng thời nhãn categorical + intensity continuous, biện minh cho schema annotation hybrid
  7-class + V/A(1–5) + distress của ViEmoSpeech; đưa MuSE/SEMAINE/CH-SIMS cho `find-dataset` để
  kiểm tra license/gate như các **mỏ neo bên ngoài (external anchors) cho head V/A** (bổ sung cho MSP-Podcast từ bimodal-12),
  không phải làm dữ liệu in-domain.
- **(2 → head emotion 7-class + sàn rare-class, V-E/V-G):** áp dụng **LDAM hoặc class-balanced focal
  loss** (thay vì CE thông thường) cho head emotion ngay từ đầu, và giữ sàn ADR-002 ≥50-clip
  như phần bổ trợ về cấu trúc — kết quả MELD 0%-fear của survey là lời cảnh báo rằng các thủ thuật loss đơn thuần
  không cứu được một class bị thiếu mẫu (đồng vọng phát hiện "corpus floor > loss trick" của bimodal-02 ABHINAYA).
- **(3 → ladder ablation fusion V-A, hàng baseline rule-fusion `arXiv:2412.09829`):** đặt Add/Concat/
  TFN làm các hàng learned-fusion *thấp nhất*, trên rule-fusion prior đã bị rút lại (vn-09) và dưới cross-attention / gated / CASE-FAS Q-Former — cho ra một ladder fusion đầy đủ, có thể trích dẫn.
- **(4 → bảng baselines + protocol đánh giá, V-G):** viết công thức metric nguyên văn và mặc định dùng
  **macro-F1 + CCC + recall@floor**; thêm chú thích rằng "WA" được định nghĩa không nhất quán trong toàn bộ
  literature SER (survey này ≠ THAI-SER/MSP) để bảo vệ khả năng so sánh cross-corpus theo ADR-002.
- **(5 → khung distress-head, V-F):** trích dẫn EmotiCon chỉ để nói rằng "các mô hình cảm xúc hướng-recall tồn tại và
  được xem là chấp nhận được trong các bối cảnh chi phí-bỏ-sót cao"; lấy *phương pháp* (mục tiêu recall-floor +
  chính sách threshold) từ bimodal-10 JMIR + FAIIR, không phải từ đây.

### ViEmoSpeech transfer-risk / child-and-tone lens

Đây là một survey **hội thoại (cấp dialogue, mô hình hóa context+speaker)**; ViEmoSpeech chấm điểm cảm xúc ở
**cấp utterance đơn lẻ, single-speaker theo thiết kế** (clip được cắt tại giao của VAD ∩ speaker-turn). Hệ quả
là rất rõ ràng:

- **Toàn bộ đóng góp headline của survey không chuyển giao được.** Các nhóm 2–4 (sequential-context,
  distinguishing-speaker, speaker-relationship GCN) — và kết quả §6 rằng chúng vượt context-free
  10–20 điểm WF1 — chính là **cơ chế context/speaker mà ViEmoSpeech cố tình từ bỏ**. Đối với
  ViEmoSpeech, survey này về bản chất nói rằng "bạn đang hoạt động ở chế độ yếu nhất (context-free) theo thiết kế";
  cách hiểu trung thực là **ViEmoSpeech cấp-utterance từ bỏ đòn bẩy lớn nhất mà survey báo cáo**, và
  phải khôi phục độ chính xác từ *fusion audio+text nội-utterance* + tín hiệu tone×emotion,
  chứ không phải từ các đồ thị hội thoại. Đây là một sự thật scoping load-bearing cho method paper, không phải một khiếm khuyết.
- **Không có mô hình hóa ngôn ngữ có thanh điệu (tonal-language).** CH-SIMS (tiếng Quan Thoại) có mặt nhưng được đóng khung là *sentiment*; tone chưa bao giờ
  là một biến, và không có corpus tiếng Việt nào. **Tính mới V-D (cạnh tranh kênh lexical-tone × emotion)
  vẫn chưa được đụng tới** bởi survey này — nay đã được xác nhận trên toàn bộ 21 bài bimodal.
- **Backbone audio đi chậm hơn một thế hệ (V-B).** Bộ trích xuất đặc trưng audio của survey hoàn toàn là cổ điển
  (COVAREP/openSMILE/LibROSA/OpenEAR); nó xuất hiện trước khi SSL được áp dụng. Do đó nó **không** phải là bằng chứng về
  WavLM so với emotion2vec so với Whisper-encoder — quyết định đó phải đến từ bimodal-01/08/12, không phải từ đây. Một mẩu
  hữu ích: COVAREP phơi bày các **tham số glottal-source (NAQ, MDQ, mô hình LF)** — tức các mô tả
  *phonation/voice-quality* — ủng hộ kế hoạch V-B thêm một vector phonation thủ công (jitter/shimmer/HNR/H1–H2)
  cho tone giàu phonation của tiếng Việt, dù survey chưa bao giờ liên kết chúng với tone.
- **Privacy §8 phù hợp với ràng buộc release của ViEmoSpeech.** Thảo luận về ẩn danh hóa / triệt tiêu danh tính tách biệt (disentangled
  identity-suppression) ở §8 nhất quán với (yếu hơn) việc release chỉ-features, giữ media riêng của ViEmoSpeech; không mới, nhưng là một mỏ neo có thể trích dẫn rằng "privacy là một mối quan tâm được nêu tên trong MCER."
- **Ethics.** Cảm xúc trong TV drama diễn (acted) (MELD là *Friends*) được xem là ground truth hợp lệ xuyên suốt — 
  survey chưa bao giờ gắn cờ acted≠natural, chính là caveat mà MSP-Podcast (bimodal-12) bác bỏ và ViEmoSpeech phải
  trả lời qua khung acted-proxy (V-F/V-D).

### Limitations & open questions for ViEmoSpeech

- **★ Mâu thuẫn/trùng lặp với bimodal-13 (MMERC survey, EMNLP'25) về "fusion nào thắng" (V-A).**
  Hai survey trả lời **các câu hỏi khác nhau** và câu trả lời headline của chúng không trùng nhau:
  **bimodal-13** tổ chức theo *trọng số modality (modality weighting)* và kết luận **cross-attention
  text-dominant primary-auxiliary** thắng (audio được đưa vào như auxiliary lên trên một core text-primary); **bimodal-14** tổ chức
  theo *động lực hội thoại (conversation dynamics)* và kết luận **speaker-relationship GCN** thắng, với fusion đúng nghĩa bị thu gọn thành các
  nguyên hàm Add/Concat/TFN sớm. Chúng **chỉ đồng thuận ở mức sàn** (naive equal-weight concat / context-free
  là yếu nhất). Đối với ViEmoSpeech, điều này có nghĩa là **bimodal-13 là nguồn V-A load-bearing** (câu trả lời modality-weighting
  của nó chuyển giao được sang một mô hình bimodal cấp utterance), trong khi **bimodal-14 phần lớn dư thừa về V-A** và
  đóng góp thay vào đó là bản đồ nhãn V-E, các quy ước metric V-G, và công thức xử lý mất cân bằng. Việc nêu rõ
  điều này ngăn việc trích dẫn kép hai survey như thể chúng củng cố lẫn nhau cho một khuyến nghị fusion — thực tế không phải vậy.
- **★ Khoảng trống: không có metric dimensional / CCC dù có các corpus dimensional.** §5 hoàn toàn là categorical (Acc/WA/F1/WF1),
  trong khi §2 lập danh mục ba corpus continuous-affect (SEMAINE/MuSE/CH-SIMS). Survey **chưa bao giờ nêu cách
  đánh giá một head V/A continuous** — nên metric CCC của V-A/V-G ở ViEmoSpeech **không có tiền lệ ở đây** và phải
  nhập khẩu CCC/Pearson từ bimodal-12 (MSP-Podcast) / hướng regression kiểu WASSA. Một khoảng trống, không phải một mâu thuẫn,
  nhưng nó có nghĩa là survey này không thể làm mỏ neo cho đánh giá head V/A.
- **Bẫy tên metric (V-G).** "WA" của survey (inverse-frequency-weighted, Eq. 36) *ngược* với quy ước
  THAI-SER/MSP "WA = overall weighted accuracy" — một mối nguy hiểm thực sự về khả năng so sánh cross-corpus;
  ViEmoSpeech phải định nghĩa công thức riêng của mình thay vì tái sử dụng "WA" một cách mơ hồ.
- **Cảnh báo về chất lượng dữ liệu.** Số liệu dataset của chính bài báo không đáng tin cậy (CH-SIMS "~10,000" so với con số chuẩn
  2,281; số lượng utterance của SEMAINE khác nhau giữa §2.5 "5,798" và §9.1 "394"). Dùng survey như một *bản đồ* về
  các corpus và loại nhãn tồn tại, sau đó xác minh mọi con số với nguồn gốc gốc (primary source).
- **Venue chưa xác nhận.** Stub ghi "ACM TOIS accepted"; arXiv cho thấy một preprint không có journal reference và
  một header placeholder kiểu `acmart`. Trích dẫn như **preprint (arXiv:2312.05735v2, 2025), venue chưa xác nhận** — M7
  nên sửa lại dòng venue của stub.
- **Mâu thuẫn với kế hoạch ViEmoSpeech về nơi độ chính xác đến từ đâu.** Thông điệp thực nghiệm mạnh nhất của survey là
  *mô hình hóa context + speaker* là đòn bẩy accuracy chủ đạo (context-free là mức sàn).
  Thiết kế của ViEmoSpeech (cấp utterance, single-speaker) nằm ở mức sàn đó theo thiết kế — một câu hỏi mở mà
  method paper phải đối mặt trực diện: **liệu tone×emotion nội-utterance + fusion audio-text có thể khôi phục lại
  những gì mô hình hóa conversation-graph mang lại, hay việc chấm điểm cấp utterance giới hạn trần độ chính xác đạt được?**
