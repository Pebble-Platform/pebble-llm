# Paper 05 — Beyond Classification: Towards Speech Emotion Reasoning with Multitask AudioLLMs

> Bản dịch tiếng Việt của [05-speech-emotion-reasoning-audiollm.md](05-speech-emotion-reasoning-audiollm.md) — cập nhật 2026-07-10.

- **Authors:** Wenyu Zhang et al. (I2R/A*STAR)
- **Venue / year:** arXiv preprint 2025
- **Links:** abs https://arxiv.org/abs/2506.06820 · PDF `pdfs/05-speech-emotion-reasoning-audiollm.pdf`
- **Group:** audio+text (trục chính)

**Summary:** AudioLLM dual-encoder sinh reasoning có bằng chứng thay vì chỉ nhãn, qua "reasoning-augmented supervision".

**Relevance to Pebble:** Analogue phía speech của silver-labeling bằng Gemini-teacher (điểm liên tục + giải thích).

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Pebble profile assembled at analysis time** (from `docs/intent/constraints.md` +
`docs/spec/capabilities/voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`):
Chương trình chính của Pebble là weak-supervision *trung thực (honest)* cho bài toán
phân loại **ordinal suicide-risk text** (nhãn silver từ teacher-LLM → bộ mã hoá lớp
NeoBERT → đánh giá trên **gold-holdout** CSSRS; các chỉ số ordinal QWK/MAE; chia tập
theo cấp độ subject). Luồng **voice** liền kề đặt các **head MTL không đồng nhất trên
một backbone SSL đóng băng (frozen)** (emotion2vec / WavLM-Large): cross-entropy cho
emotion + hồi quy **V/A CCC** cho affect + **head crisis dưới ràng buộc sàn recall cứng
(0.90)**, được cân bằng bằng **Kendall uncertainty weighting**; hợp nhất voice+text là
hướng đi tiếp theo. "Hữu ích cho Pebble" nghĩa là bài báo tác động đến một trong các đòn
bẩy này (head không đồng nhất, giám sát silver bằng teacher-LLM, cân bằng MTL có nguyên
tắc, mục tiêu crisis-recall, backbone SSL).

### Analysis — Speech Emotion Reasoning with Multitask AudioLLMs
- **Overlap:** 38% (ngoại vi, ranh giới của phần liền kề) — D1=1, D2=0, D3=0, D4=2, D5=1, D6=0, D7=1
  - Σ wᵢ·scoreᵢ = 3·1 + 2·0 + 1·0 + 2·2 + 2·1 + 2·0 + 1·1 = 10 → 10/26 = **38%**.
- **Closest on:** D4 (teacher-LLM sinh ra reasoning-augmented supervision — một teacher
  Gemma-2-9B-IT viết các rationale có căn cứ bằng chứng từ transcript+label để huấn
  luyện student AudioLLM — đây chính là analogue phía speech trực tiếp của silver-labeling
  bằng Gemini của Pebble). Hỗ trợ một phần trên D5 (huấn luyện task-alternating là một
  chiến lược cân bằng MTL, nhưng không thuộc nhóm uncertainty/GradNorm/PCGrad mà Pebble
  dùng) và D7 (emotion2vec / HuBERT / WavLM được thử nghiệm như bộ mã hoá tập trung vào
  emotion — khớp về lớp backbone — dù được dùng như bộ trích xuất đặc trưng cho LLM, chứ
  không phải frozen-SSL + probe head).
- **Best point (Method to adopt):** Ghép mỗi nhãn với một **rationale có căn cứ bằng
  chứng (evidence-grounded)** do LLM sinh ra (trích đoạn + lý giải) làm supervision phụ
  trợ đã nâng độ chính xác nhận diện lên ~20 điểm trung bình, không chỉ là khả năng diễn
  giải (Table 1: label-only trung bình 38.2 → evidence-grounded reasoning 58.1), và họ
  chấm chất lượng rationale bằng chỉ số **Groundedness** LLM-as-judge (trích dẫn có thật
  hay bị bịa) tách biệt khỏi độ đúng của nhãn.
  - **How to apply to Pebble:** Khi sinh nhãn silver risk bằng Gemini, cũng nên gợi ra
    một rationale ngắn có căn cứ bằng chứng (trích đoạn post + lý do vì sao ở mức độ
    này) và dùng **groundedness** của nó làm bộ lọc *chất lượng nhãn* — loại bỏ/hạ trọng
    số các nhãn silver có rationale không có căn cứ/bị bịa trước khi chúng đi vào tập
    huấn luyện. Điều này đóng góp trực tiếp cho `label-quality.md` và vẫn giữ nguyên
    gold-holdout (rationale chỉ bổ sung cho nhãn silver phía train; eval vẫn dùng CSSRS
    gold).
- **Caveats:** Đã đọc toàn bộ PDF (trang 1–6, gồm abstract, method, Table 1) — không bị
  paywall. Kiến trúc là một **AudioLLM dual-encoder sinh sinh** (Whisper-Large-v3 + bộ
  mã hoá emotion → Gemma-2-9B LoRA), khác biệt về mặt cấu trúc so với frozen-SSL +
  probe head MTL nhẹ và với text encoder NeoBERT của Pebble. **Không** có miền
  mental-health/crisis (D2=0), **không** có hồi quy liên tục hay head safety (mọi output
  đều là văn bản sinh ra, nên D1 chỉ là một phần), **không** có mục tiêu crisis-recall
  (D6=0). D4=2 được chấm hào phóng: *nhãn* phân loại vẫn là gold (IEMOCAP/MELD) — LLM
  sinh ra *rationale* (silver supervision), không phải chính nhãn, nên đây là chưng cất
  silver-**supervision** chứ không phải chưng cất silver-**label**. Điểm số nằm ở ranh
  giới 40% ngoại vi/liền kề.

## Deep research — full-PDF read (2026-07-10)

> Đọc lại toàn bộ đối chiếu với **hồ sơ ViEmoSpeech hiện tại + Decision Register (V-A…V-H)**
> từ `docs/tasks/paper-deep-analysis.md`. Phần "Analysis (overlap with Pebble)" ở trên dùng
> **hồ sơ luồng text đã lưu trữ (archived) (D1–D7, NeoBERT/CSSRS)** và đã lỗi thời — bỏ qua
> các điểm D của nó; phần này thay thế cho các quyết định của ViEmoSpeech. Đối chiếu chéo
> với vn-08 (HGR VN-SER, 2604.01711), bài báo VN-SER dùng LLM-reasoning còn lại.

### Source-access note

- **PDF read:** `pdftotext` trên `docs/papers/bimodal-ser/pdfs/05-speech-emotion-reasoning-audiollm.pdf`
  (arXiv:2506.06820**v2** [cs.CL], 29 Sep 2025), toàn văn gồm abstract, §§1–10, và toàn bộ
  Tables 1–7. Các cột 2/3/5–7 của bảng bị xen lẫn hỗn loạn trong bản dump text (do bố cục
  nhiều cột); các giá trị bên dưới được tái dựng bằng cách đối chiếu với bản arXiv HTML.
- **Web validation.** Tìm kiếm `Beyond Classification Towards Speech Emotion Reasoning
  Multitask AudioLLMs 2506.06820 venue` → bài báo **chỉ có trên arXiv** (cross-listed
  cs.CL / cs.SD / eess.AS), **không có tuyên bố được chấp nhận ở hội nghị/tạp chí nào**
  (Semantic Scholar + trang abs của arXiv, resolve tới
  `https://arxiv.org/abs/2506.06820`; alphaXiv `https://www.alphaxiv.org/overview/2506.06820v1`).
  Quy tắc về provenance: không tồn tại phiên bản venue, nên bản PDF v2 local là bản có
  thẩm quyền.
- **Preprint-delta check.** Đã tải bản HTML **v1** (`https://arxiv.org/html/2506.06820v1`) và
  xác nhận Table 1 (38.2 / 57.8 / 58.1 trung bình), Table 4 (Quotation 57.5 / Groundedness 82.8 /
  Relevance 65.3), và Table 5 (AudioLLM-Reasoning 59.3; WavLLM 50.8; Qwen2-Audio 49.8) là
  **giống hệt nhau giữa v1→v2** ✔. Các số liệu ở Tables 2/3/6/7 và §7 chỉ xuất hiện trong
  PDF (không được đối chiếu riêng trên web) → gắn nhãn ≈.

### Bài báo thực sự làm gì

**Mục tiêu.** Chuyển nhận diện cảm xúc giọng nói bằng AudioLLM từ phân loại chỉ-nhãn
sang **reasoning cảm xúc (emotion *reasoning*)** — mô hình xuất ra nhãn cảm xúc *cộng
với* một lời giải thích tự nhiên, có căn cứ bằng chứng ("The speaker is clearly angry.
Their statement 'I'm not starting over again'… suggests frustration"). Ba bậc output
được định nghĩa (Fig. 1): Label-Only < Interpretive Reasoning < Evidence-Grounded
Reasoning (trích đoạn có thật + diễn giải chúng).

**Method — ba thành phần kết hợp (§3):**
1. **Reasoning-augmented supervision (§3.1).** Một teacher LLM (**Gemma-2-9B-IT**) được
   cấp *transcript + nhãn emotion gold + một prompt reasoning* và viết lời giải thích,
   trở thành target huấn luyện. Hai kiểu prompt: **"Elaborate"** → evidence-grounded
   (trích dẫn các tín hiệu tường minh), **"Summarize"** → interpretive (ngữ cảnh ngụ ý).
   *Nhãn* emotion vẫn giữ nguyên gold (IEMOCAP/MELD); chỉ có rationale là do LLM sinh ra.
   Các cặp QA huấn luyện được xây dựng bằng cách lấy mẫu từ một tập câu hỏi được tuyển
   chọn ("How would you interpret the speaker's emotional state…").
2. **Dual-encoder fusion (§3.2).** Một **speech encoder** tổng quát (cố định = Whisper-Large-v3)
   + một **emotion-centric encoder** có thể hoán đổi, mỗi cái có một adapter MLP nhẹ
   (2 lớp ẩn, SiLU), chiếu vào một không gian chung rồi ghép nối, sau đó đưa vào LLM.
   Các utterance được zero-pad tới 30 giây → độ dài chuỗi encoder là 1500; adapter
   **định hình lại speech thành 100 token và emotion thành 10 token** ("biểu diễn cô đọng
   tập trung vào emotion… tín hiệu bổ trợ với độ dư thừa tối thiểu"). **Ghép nối theo
   chiều chuỗi (sequence-dim) > ghép nối theo chiều đặc trưng (feature-dim)** (Table 2).
3. **Task-alternating training (§3.3).** Các tác vụ tập trung vào speech (ASR, SQA)
   huấn luyện speech encoder+adapter+LLM-LoRA; các tác vụ tập trung vào emotion (ER +
   explanation) huấn luyện emotion encoder+adapter+LLM-LoRA; nhánh *còn lại* bị đóng
   băng ở mỗi vòng. **Epoch cuối cùng cập nhật tất cả adapter+LoRA cùng lúc** để căn
   chỉnh (alignment). LLM backbone được thích ứng chỉ bằng **LoRA** (không full fine-tune).

**Config (§4.1):** LLM Gemma-2-9B-IT; encoder Whisper-Large-v3; batch 48, 5 epoch,
8× H100, AdamW (β 0.9/0.999), lr 5e-5. ✔ (văn bản method).

**Data + eval (§4.2–4.3):** huấn luyện/đánh giá trên **IEMOCAP** (ER 10 lớp) và **MELD**
(MELD-ER 7 lớp, MELD-SR sentiment 3 lớp); các tác vụ semantic từ **MNSC** (SQA/ASR
Singlish, chọn vì ít bị nhiễm dữ liệu pre-training), Spoken-SQuAD, SLUE, LibriSpeech.
Đánh giá qua **AudioBench** với **LLM-as-a-Judge (Llama-3-70B-Instruct)** chấm điểm nhị
phân về mức độ khớp ngữ nghĩa cho ER/SR (chuẩn hoá 0–100); ASR = WER.

**Kết quả chính (đều là trung bình trên IEMOCAP/MELD-ER/MELD-SR trừ khi có ghi chú
khác):**
- **Target reasoning vượt label-only ~20 điểm** (Table 1): Label-Only **38.2** →
  Interpretive **57.8** → Evidence-Grounded **58.1** ✔. Lưu ý IEMOCAP nhảy vọt 18.6→60.8
  (Interpretive) nhưng Evidence-Grounded (58.6) lại *thấp hơn* Interpretive ở đó.
- **Chất lượng reasoning (Table 4):** ≥49% số phản hồi chứa một trích dẫn có thật
  (Quotation trung bình 57.5); **Groundedness 82.8** (trích dẫn trung thực với
  transcript), **Relevance 65.3** (trích dẫn hỗ trợ nhãn) ✔.
- **Mô hình end-to-end tốt nhất (Table 5):** **AudioLLM-Reasoning** cuối cùng (emotion
  encoder Emotion2Vec+ Large, Alt-4-epoch) đạt **59.3 trung bình**, vượt WavLLM 50.8,
  Qwen2-Audio 49.8, Audio-Reasoner 53.8, SALMONN 32.0 ✔ (các hàng trên cùng được đối
  chiếu web; các hàng còn lại ≈).
- **Ablation thiết kế (Tables 2–3, ≈):** task-alternating > joint multitask (ví dụ:
  seq-concat Alt-1ep 56.6 so với Joint 50.3); lựa chọn emotion encoder có ảnh hưởng —
  **Emotion2Vec+ Large (Alt-4ep) = 59.3** tốt nhất, Emotion2Vec+ base 54.8–56.2,
  **HuBERT-XL kém nhất (49.5–50.8)**, Whisper-Tiny 49.5.
- **Tổng quát hoá OOD (Table 6, ≈):** trên tập chưa từng thấy **M3ED (phim truyền hình
  Trung Quốc)** 48.6 và **CPQA-ER (YouTube Singapore)** 49.0, AudioLLM-Reasoning vượt
  Emotion2Vec+ Large (47.9 / 37.9) và Audio-Reasoner.
- **Emotion supervision có tính cộng dồn trên một base đã pre-train (Table 7, ≈):**
  thêm emotion supervision vào một AudioLLM base nâng ER/SR **+12.3** và **+22.4** điểm
  trên hai config trong khi SQA/ASR chỉ dao động trong khoảng ~2 điểm (WER 19.5→19.6;
  3.8→3.6).
- **LLM-judge audit (§7, ≈):** trên IEMOCAP 27.6% / MELD-ER 6% số dự đoán rơi vào
  "trường hợp đặc biệt" (đồng nghĩa, đa cảm xúc, các phạm trù chồng lấn) nơi exact-match
  thất bại. Kiểm tra thủ công 50 trường hợp đặc biệt: chỉ **2%** judge-đúng/human-sai,
  nhưng **16% (IEMOCAP) / 30% (MELD-ER)** judge-sai/human-đúng → **LLM judge có xu hướng
  bảo thủ (under-credit) một cách hệ thống**.

### Các phần hữu ích trực tiếp cho ViEmoSpeech (gắn Decision IDs)

1. **Huấn luyện multitask task-alternating thay vì cộng dồn loss (joint loss-summing) —
   [V-A][V-G].** Mỗi họ tác vụ chỉ cập nhật nhánh encoder+adapter+LLM-LoRA của riêng nó;
   một epoch cuối cùng chung căn chỉnh mọi thứ (Table 2: Alt vượt Joint cụ thể trên các
   tác vụ emotion, ~+4–6 điểm). Đây là câu trả lời cụ thể cho câu hỏi "làm sao mang
   emotion-CE + V/A-CCC + head distress cùng nhau mà không cái nào lấn át cái nào."
2. **Dual-encoder với ngân sách token emotion cô đọng, bất đối xứng —
   [V-A][V-B].** Speech encoder tổng quát → 100 token; **emotion-centric encoder → chỉ
   10 token** ("độ dư thừa tối thiểu"), được hợp nhất bằng **ghép nối theo chiều chuỗi**
   (> ghép nối theo chiều đặc trưng). Một mẫu thiết kế cho việc hợp nhất audio+text/tone
   của chúng ta: dành cho luồng chuyên biệt (emotion/tone/phonation) một khe nhỏ dành
   riêng thay vì hợp nhất đối xứng.
3. **Lựa chọn emotion-centric encoder: Emotion2Vec+ ≥ Whisper-Large ≫ HuBERT-XL cho ER —
   [V-B].** Table 3: Emotion2Vec+ Large (Alt-4ep) 59.3 so với HuBERT-XL 49.5–50.8, dù
   HuBERT-XL lớn hơn (962M so với 164M). Pre-training *cho emotion* thắng quy mô. (Là
   thứ yếu so với mục tiêu của bài báo này; củng cố xu hướng V-B của chúng ta.)
4. **Target reasoning có căn cứ bằng chứng + tiêu chí Groundedness/Relevance riêng —
   [V-D][V-G].** Cơ chế để sản sinh *và chấm điểm* một lời giải thích về lý do một
   emotion được gán: trích dẫn đoạn bằng chứng, sau đó chấm điểm (0–2) xem trích dẫn có
   thật hay không (Groundedness) và có hỗ trợ cho nhãn hay không (Relevance), *tách biệt*
   khỏi độ đúng của nhãn. Đây là mẫu (template) được công bố gần nhất cho việc phương
   pháp luận của ViEmoSpeech có thể **giải thích một trường hợp xung đột tone×emotion**.
5. **LLM-as-a-Judge kèm audit tính bảo thủ được xác thực bởi con người — [V-G].** Chấm
   điểm khớp ngữ nghĩa nhị phân xử lý được các nhãn emotion đồng nghĩa/chồng lấn mà
   exact-match bị vỡ (excited≈happy, anger≈frustration), *và* họ đo độ lệch sai số của
   judge so với 4 người chấm. Có thể tái sử dụng trực tiếp nếu hình ảnh giải thích
   tone×emotion của chúng ta cần chấm điểm văn bản tự do.
6. **Emotion supervision mang tính cộng dồn với hồi quy có giới hạn trên các tác vụ khác
   — [V-A].** Table 7: gắn thêm một nhánh emotion vào một base đã huấn luyện tăng
   +12–22 điểm ER với chỉ <2 điểm suy giảm ASR/SQA — bằng chứng rằng một head không đồng
   nhất có thể được *thêm vào* một backbone chung mà không phá hỏng các head khác, đúng
   là câu hỏi về sự cùng tồn tại đa-head trong V-A.

### Mỗi phần giúp ViEmoSpeech thành công như thế nào

- **[V-A] Áp dụng lịch trình task-alternating cho trainer đa-head.** Các head của ta
  không đồng nhất (emotion CE, V/A CCC, distress recall-floor) — một loss cộng dồn ngây
  thơ để head emotion-CE có gradient cao lấn át các head CCC/distress. Áp dụng công thức
  alternating: xoay vòng các bước *họ emotion* và các bước *họ dimensional/distress*,
  chỉ cập nhật head đang hoạt động + adapter của nó, sau đó một epoch cuối chung. Artifact
  cụ thể: một cờ `training/schedule` trong fusion trainer với một hàng ablation
  `alt_vs_joint` trong bảng eval V-G. **Transfer risk: HIGH.** Alternating của họ di
  chuyển các *encoder*; nếu ViEmoSpeech giữ một audio backbone **đóng băng** (V-B còn mở),
  chỉ có adapter+head luân phiên, một đòn bẩy yếu hơn nhiều so với những gì Table 2 đo
  được — coi mức tăng +4–6 điểm là một *cận trên* cần kiểm chứng, không phải điều mặc
  định đúng.
- **[V-A][V-B] Cấp cho luồng emotion/tone một ngân sách token nhỏ dành riêng trong
  fusion.** Sao chép cách ghép nối bất đối xứng 100-so-10: để nhánh nhạy với
  phonation/tone (emotion2vec / vector chất lượng giọng từ vn-06) chiếm một khe ngắn, cô
  đọng, được hợp nhất theo chiều chuỗi với luồng ngữ nghĩa PhoWhisper/PhoBERT đầy đủ hơn,
  sao cho kênh tone là một tín hiệu *bổ trợ*, không bị nhấn chìm. Artifact cụ thể: config
  module fusion `emotion_seq_len` << `speech_seq_len`. **Transfer risk: MEDIUM** —
  fusion của họ đưa vào một LLM sinh; của ta đưa vào các classifier head, nên "số lượng
  token" ánh xạ sang số lượng đoạn (segment) đã pooled. *Nguyên tắc* (ngân sách bất đối
  xứng, seq-concat > feature-concat) chuyển giao được; con số chính xác 100/10 thì
  không.
- **[V-B] Mặc định nhánh audio là một encoder đã pre-train cho emotion, chỉ giữ HuBERT
  như một arm.** Table 3 cho thấy pre-training cho emotion thắng quy mô thuần tuý cho
  ER — khớp với xu hướng V-B của ta nghiêng về emotion2vec(-S). Artifact cụ thể: bake-off
  encoder V-B giữ Emotion2Vec+ làm ứng viên ưa thích, HuBERT-XL làm baseline yếu được ghi
  nhận. **Transfer risk: MEDIUM** — được đo trên IEMOCAP/MELD tiếng Anh, không phải
  tiếng Việt có thanh điệu; lợi thế của emotion2vec có thể thu hẹp khi thanh điệu từ
  vựng cạnh tranh giành kênh F0/phonation (vn-06/vn-13), nên arm này phải được *chạy
  lại* trên ViEmoSpeech, không thể kế thừa nguyên trạng.
- **[V-D][V-G] Dùng target evidence-grounded của họ + tiêu chí Groundedness/Relevance
  làm *hình mẫu* cho output giải thích tone×emotion của ta.** Khi ta muốn method paper
  *cho thấy* một xung đột tone×emotion ("từ nói X nhưng tone nói Y"), hãy phát ra một
  rationale có cấu trúc (trích dẫn âm tiết/token + nêu tên kênh đang cạnh tranh) và chấm
  điểm Groundedness (tín hiệu được trích dẫn có thật không?) tách biệt khỏi độ chính xác
  của nhãn. Artifact cụ thể: một trường `explanation` tùy chọn trên các trường hợp xung
  đột thuộc gold-slice + một cột groundedness trong báo cáo V-G. **Transfer risk: HIGH /
  cần chuyển hướng** — grounding của họ nằm ở **transcript (nội dung ngữ nghĩa)**; một
  lời giải thích tone×emotion phải grounding vào kênh **acoustic/phonetic** (đường bao
  F0, phonation), điều mà pipeline của họ chưa bao giờ chấm điểm. Ta sẽ cần một chỉ số
  groundedness *âm học* — một mở rộng thực sự, không phải một bản sao.
- **[V-G] Mượn quy trình audit tính bảo thủ của LLM-judge, không mượn judge làm chỉ số
  chính (headline metric).** Nếu ta từng chấm điểm giải thích emotion/tone dạng văn bản
  tự do, hãy lặp lại việc kiểm tra thủ công 50 trường hợp đặc biệt bằng 4 người và báo
  cáo tỷ lệ judge-sai (của họ: lên tới 30% trên MELD-ER). Nhưng các head *chính* của ta
  xuất ra nhãn rời rạc + giá trị vô hướng V/A → dùng exact macro-F1 / CCC (V-G), dành
  LLM-judge cho hình ảnh giải thích mà thôi. **Transfer risk: LOW cho phương pháp audit;
  bản thân judge thì thiên về tiếng Anh** (Llama-3-70B) và chưa được xác thực trên tiếng
  Việt — không chạy LLM judge trên output tiếng Việt mà thiếu hiệu chỉnh bằng con người
  tiếng Việt.

### Lăng kính trẻ em / thanh điệu×cảm xúc tiếng Việt (tính hợp lệ khi chuyển giao)

- **Kiến trúc là cực đối lập với ViEmoSpeech.** Đây là một **AudioLLM sinh 9B (LoRA)**
  xuất ra văn bản tự do; ViEmoSpeech là một **classifier đa-head nhẹ trên một backbone
  SSL (khả năng cao là đóng băng)** xuất ra nhãn + giá trị vô hướng. Không con số tuyệt
  đối nào chuyển giao được như một cột mốc; chỉ các ý tưởng về *lịch trình huấn luyện,
  cấu trúc topology fusion, và công cụ đánh giá* là chuyển giao được. Phải nêu rõ điều
  này trong method paper để người phản biện không đọc con số 59.3 của Table 5 như một
  mục tiêu có thể so sánh.
- **Reasoning của họ được grounding về mặt ngữ nghĩa, đúng là kênh mà tone tiếng Việt
  gây nhiễu.** Groundedness của họ (82.8) thưởng cho việc trích dẫn **transcript** —
  "cái gì được nói." Toàn bộ tiền đề của ViEmoSpeech (vn-06 Shen, vn-13 Chang) là trong
  tiếng Việt, **"nói như thế nào" (F0/phonation)** *được chia sẻ với* thanh điệu từ vựng,
  nên một lời giải thích chỉ trích dẫn từ ngữ sẽ bỏ lỡ hoàn toàn xung đột tone×emotion.
  Kết luận nổi bật của họ rằng "evidence-grounded là đáng mong muốn nhất" do đó chưa
  phục vụ tốt cho một ngôn ngữ có thanh điệu: ta phải thêm một trục grounding
  **acoustic-evidence** mà họ chưa từng có.
- **Tiền lệ OOD trên found-speech, phim truyền hình đáng khích lệ.** Tập OOD của họ
  **M3ED = phim truyền hình Trung Quốc** (≈49.0) — một corpus phim đóng, ngôn ngữ có
  thanh điệu, khá giống với nguồn của ViEmoSpeech — và mô hình tổng quát hoá tốt nhất ở
  đó (Table 6, ≈). Tín hiệu yếu nhưng thực rằng cảm xúc trong phim truyền hình có thanh
  điệu là học được; không phải một tuyên bố về distress/lâm sàng (nhãn của họ là 7 cảm
  xúc diễn xuất, không có trục distress).
- **Distress / an toàn hoàn toàn vắng mặt.** Không có sàn recall, không có head distress,
  không có khung lâm sàng; Ethics §10 chỉ cảnh báo chung chung về "sự hiểu sai các tín
  hiệu cảm xúc." Không có gì ở đây thông tin cho V-F ngoài lời nhắc nhở rằng
  emotion≠distress. **Không** trích dẫn bài báo này cho head distress.
- **Ghi chú về đạo đức/consent cho việc sử dụng của chúng ta.** Supervision của họ là
  các rationale do LLM-teacher soạn trên các corpus diễn viên công khai; ViEmoSpeech
  theo **ADR-003** giới hạn LLM teacher chỉ ở *gợi ý hiển thị trên màn hình (on-screen
  suggestion only)*, nhãn huấn luyện phải do con người. Nếu ta từng nhập khẩu kỹ thuật
  sinh rationale của họ, nó phải nằm trên kênh *phụ trợ/giải thích phía train* trong khi
  vẫn giữ nguyên nhãn gold của con người — đúng chính xác là setup của họ (nhãn vẫn gold,
  chỉ rationale được sinh ra), nên tương thích với ADR-003 *chỉ khi* rationale không bao
  giờ trở thành nhãn.

### Hạn chế & câu hỏi mở cho ViEmoSpeech (kèm mâu thuẫn/khoảng trống)

- **Mâu thuẫn với vn-08 (HGR VN-SER, 2604.01711) — hai hướng LLM-reasoning khác nhau ở
  chỗ ai là người tạo ra reasoning.** vn-08 dùng reasoning **do con người dẫn dắt**
  (rationale lâm sàng/ngữ cảnh của người chấm điểm dẫn dắt mô hình; 86.6% / κ 0.857 trên
  một corpus tiếng Việt *đóng, không chia theo speaker-disjoint* — một trần bị thổi
  phồng do rò rỉ dữ liệu theo phát hiện của wave-1). Paper 05 dùng reasoning **được
  chưng cất từ LLM** (Gemma-2 viết rationale từ transcript+nhãn gold; ~+20 điểm trên
  IEMOCAP/MELD *công khai, được kiểm soát nhiễm dữ liệu*). **Điểm mù chung mà cả hai
  chia sẻ với nhau và với nhu cầu của ViEmoSpeech:** cả hai đều grounding reasoning vào
  **nội dung ngữ nghĩa/ngữ cảnh**, không bên nào grounding vào **tone âm học** — nên
  *không bên nào* thực sự reasoning trên sự cạnh tranh kênh tone×emotion, điều làm nên
  tính mới của ViEmoSpeech. Khoảng trống đó là vùng đất trống của ta: một lời giải thích
  có căn cứ bằng chứng với bằng chứng là *ngữ âm* (F0/phonation), được chấm bằng một chỉ
  số groundedness *âm học*, chưa được công bố ở cả hai phía.
- **Khoảng trống/mâu thuẫn với chính kết luận nổi bật của bài báo: grounding hầu như
  không giúp ích cho độ chính xác.** Evidence-Grounded (58.1) ≈ Interpretive (57.8) trung
  bình, và trên IEMOCAP Interpretive (60.8) *vượt* Evidence-Grounded (58.6) (Table 1 ✔).
  Mức nhảy ~20 điểm là từ **label-only → bất kỳ reasoning nào**, không phải riêng
  grounding. Bài học cho V-D: thêm một target reasoning có thể nâng độ chính xác emotion,
  nhưng *grounding âm học* nên được biện minh vì lợi ích **khả năng diễn giải
  (explainability)** (câu chuyện của method paper của ta), không phải được bán như một
  yếu tố thúc đẩy độ chính xác — ta phải đo cả hai một cách tách biệt.
- **Mâu thuẫn với giả định backbone đóng băng của ViEmoSpeech (V-B).** Lợi ích của họ
  dựa trên **encoder có thể huấn luyện + LoRA**; lợi ích của task-alternating (Table 2)
  chưa được đo với một backbone đóng băng. Nếu ta đóng băng (vì lý do compute/pháp
  lý/ổn định), đòn bẩy alternating của V-A có thể sụp đổ — đây là một thí nghiệm còn mở,
  không phải một điều đã được thiết lập để nhập khẩu.
- **LLM-as-a-Judge chỉ dành cho tiếng Anh và có xu hướng bảo thủ.** §7 cho thấy judge
  Llama-3-70B under-credit các câu trả lời đúng lên tới 30% (MELD-ER). Với tiếng Việt ta
  **chưa có LLM judge được xác thực**; V-G phải giữ nguyên trên exact macro-F1 / CCC /
  recall@floor cho các head, với LLM-judge chỉ giới hạn cho (và được hiệu chỉnh bằng con
  người cho) bất kỳ hình ảnh giải thích nào.
- **Không có target dimensional (V/A) hay ordinal nào cả.** Mọi thứ đều là ER phân loại
  + SR 3 lớp; không có hồi quy valence/arousal, không có CCC. Vậy nên bài báo này **không
  cung cấp gì cho head V/A-CCC của ta** (V-G) — một khoảng trống thực sự: thiết kế head
  hồi quy của ta phải đến từ bimodal-12 (MSP-Podcast CCC) và vn-13, không phải từ đây.
- **Câu hỏi mở:** liệu fusion bất đối xứng (khe emotion 10 token) có sống sót khi luồng
  "emotion" thay vào đó là một luồng **tone/phonation** đang cạnh tranh với F0 hay không?
  Emotion encoder và nhãn của họ chưa bao giờ có thanh điệu từ vựng trong cùng một kênh —
  chưa được kiểm chứng, và chính xác là thí nghiệm của ViEmoSpeech.

Sources: [arXiv abs 2506.06820](https://arxiv.org/abs/2506.06820) · [arXiv v1 HTML](https://arxiv.org/html/2506.06820v1) · [Semantic Scholar](https://www.semanticscholar.org/paper/a47dc5c7c024affc2312276a0bb6390dbb68d747) · [alphaXiv](https://www.alphaxiv.org/overview/2506.06820v1)
