# Paper 18 — Joint Multimodal Transformer for Emotion Recognition in the Wild

> Bản dịch tiếng Việt của [18-joint-multimodal-transformer.md](18-joint-multimodal-transformer.md) — cập nhật 2026-07-10.

- **Authors:** Paul Waligora, Haseeb Aslam, Osama Zeeshan, Soufiane Belharbi, Alessandro Lameiras Koerich, Marco Pedersoli, Simon Bacon, Eric Granger
- **Venue / year:** CVPRW 2024
- **Links:** abs https://arxiv.org/abs/2403.10488 · PDF `pdfs/18-joint-multimodal-transformer.pdf`
- **Group:** audio-visual (đối chứng)

**Tóm tắt:** Cross-attention theo kiểu key-based giữa các transformer backbone riêng của từng modality (mặt+giọng nói, Affwild2), nắm bắt các quan hệ intra- và inter-modal.

**Mức liên quan tới Pebble:** Block cross-attention đơn giản, dễ port nhất để ghép audio branch vào text branch hiện có.

> Mục nhập rút gọn từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (mức chồng lấp với Pebble)

**Hồ sơ Pebble được tổng hợp (tại thời điểm phân tích):**
- *Primary (intent, `constraints.md`):* phân loại ordinal nguy cơ tự sát trên văn bản (**text**); nhãn silver từ LLM/weak supervision bổ sung một cách trung thực cho tập gold lâm sàng khan hiếm; đánh giá trên **gold-holdout**; xuyên suốt theo hướng ordinal-aware (QWK/MAE); chia tách theo cấp độ subject; encoder họ BERT.
- *Nhánh voice liền kề (`voice-multimodal.md` → `voice-mtl-heads.md`):* backbone WavLM-Large / emotion2vec đóng băng + trunk dùng chung, **3 head dị chủng (heterogeneous)** — emotion CE, affect **valence+arousal với CCC loss**, crisis BCE dưới một **ngưỡng sàn recall cứng (0.90)** — được cân bằng bằng **Kendall uncertainty weighting**. Hướng đi tới: fusion voice+text.

### Analysis — Joint Multimodal Transformer (JMT)
- **Mức chồng lấp:** 15% (ngoại vi) — D1=1, D2=0, D3=1, D4=0, D5=0, D6=0, D7=0
  - Tính toán: (3·1 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·0) / 26 × 100 = 4/26 × 100 = 15%.
- **Gần nhất trên:** D1 (affect liên tục được hồi quy bằng **CCC loss** — đúng objective của voice *affect* head của Pebble) và D3 (Affwild2 như một corpus valence/arousal liên tục kiểu in-the-wild).
- **Điểm tốt nhất (Method nên áp dụng):** Fusion block của JMT — cross-attention theo kiểu key-based giữa hai luồng transformer riêng của từng modality, **cộng thêm một nhánh "joint representation" thứ ba** (feature được concatenate rồi đưa ngược trở lại qua cross-attention) mà nhiệm vụ duy nhất là bơm thêm redundancy và khiến fusion vững hơn khi một modality bị nhiễu/thiếu; các ablation tách riêng nó cho thấy mức tăng **+1.3–1.8% so với transformer cross-attention thuần (vanilla)** và fusion vượt qua mọi baseline đơn-modal.
  - **Cách áp dụng cho Pebble:** Dùng đây làm template cho **fusion voice+text** đã hoãn lại — cross-attend luồng voice-encoder đóng băng với luồng text NeoBERT và thêm nhánh joint concatenate như cơ chế chống nhiễu khi modality voice bị thiếu/suy giảm; giữ **CCC loss** dùng chung trên affect target mà fusion kế thừa từ voice affect head.
- **Lưu ý (Caveats):** Đã đọc toàn bộ PDF (mở, không paywall). Mọi thứ chỉ chuyển giao được cho nhánh voice/fusion *liền kề*, không phải chương trình text chính — do đó ở mức ngoại vi. **Không** có MTL đa-head dị chủng, **không** có loss balancing (single-task CCC cho mỗi thí nghiệm, nên D5=0), **không** có teacher/silver-label distillation (D4=0), **không** thuộc domain sức khỏe tâm thần/crisis hay ràng buộc recall (D2=D6=0). Backbone **không** khớp với voice SSL stack của Pebble — audio branch là ResNet18 trên spectrogram, không phải WavLM/emotion2vec (D7=0). Các số liệu báo cáo trên Affwild2 (V/A) và BioVid pain, cả hai đều gated/external, nên không phải là baseline có thể so sánh trực tiếp cho các lượt chạy proxy-label RAVDESS của Pebble.

## Deep research — đọc toàn bộ PDF (2026-07-10)

> Đọc đối chiếu với **hồ sơ ViEmoSpeech hiện tại** (7 lớp + V/A 1–5 + distress; bimodal tone×emotion
> audio+text/ASR; đăng ký V-A…V-H) — khối "Analysis (mức chồng lấp với Pebble)" ở trên dùng hồ sơ text-stream
> **cũ** (pre-pivot) (D1–D7) và chỉ được giữ lại như lịch sử. Phần này là bản có thẩm quyền (authoritative).
> Paper đối chứng audio-VISUAL: phần có thể chuyển giao = cơ chế fusion (V-A) và objective CCC V/A (V-G);
> luồng visual chính là vị trí mà ViEmoSpeech thay bằng luồng text/ASR.

### Ghi chú tiếp cận nguồn (Source-access note)

- **Đã đọc toàn bộ PDF** qua `pdftotext docs/papers/bimodal-ser/pdfs/18-joint-multimodal-transformer.pdf`
  (bản local = arXiv:2403.10488v3, 20 Apr 2024) — method §3 (Eqs 1–3), toàn bộ bảy bảng, references.
- **Đã kiểm chứng trên web** đối chiếu với bản venue (CVPRW 2024, ABAW6 workshop):
  - Truy vấn `Joint Multimodal Transformer key-based cross-attention Affwild2 valence arousal CCC Waligora
    CVPRW 2024` → trang CVF Open Access
    `openaccess.thecvf.com/content/CVPR2024W/ABAW/html/Waligora_Joint_Multimodal_Transformer_for_Emotion_Recognition_in_the_Wild_CVPRW_2024_paper.html`
    (fetch tool trả về HTTP 403) + bản mirror HTML trên arXiv `arxiv.org/html/2403.10488`. Bản mirror HTML xác nhận:
    **Affwild2 official val CCC V 0.717 / A 0.614 / trung bình 0.666; test CCC V 0.472 / A 0.443 / trung bình 0.458;
    Biovid JMT 89.1% so với vanilla-transformer 87.8% so với concat 83.5%; +7% so với Joint Cross Attention [46]
    (0.369); audio backbone = ResNet18 trên spectrogram; modality text = không dùng.** [đã kiểm chứng].
  - So sánh trực diện với #17 (RJCMA) lấy từ chính phần deep-read đã kiểm chứng của paper đó
    (`docs/papers/bimodal-ser/17-rjcma.md`; RJCMA test mean **0.5807**, V 0.542 / A 0.619, hạng 2 ABAW6). [đã kiểm chứng].
- Không có số liệu nào bị bịa đặt; mọi con số load-bearing dưới đây đều kèm tham chiếu bảng + trạng thái.

### Paper thực sự làm gì

- **Task.** Hai task affect dạng liên tục/ordinal, cả hai đều **audio-visual (không có text)**: (1)
  **valence/arousal liên tục trên Aff-Wild2** (track ABAW6, mặt + giọng nói), chấm điểm bằng CCC; (2)
  **ước lượng cường độ đau (pain-intensity) trên BioVid Heat Pain Part A** (mặt + tín hiệu sinh lý EDA),
  chấm điểm bằng accuracy. Cùng lab LIVIA/ETS-Montréal với #17 (Granger et al.); cả hai đều bắt nguồn từ
  "Joint Cross Attention [46]" (Praveen 2022) tại CVPR-2022.
- **Cơ chế fusion — JMT block (§3.2, payload của V-A).** Hai backbone đơn-modal đóng băng phát ra
  `f_A`, `f_B` (mỗi cái chiều 512). Một **nhánh "joint" thứ ba** được xây bằng concatenation và FC-reduction:
  - **Eq 1:** `f_J = [f_B ; f_A]` (chiều 1024) sau đó qua FC xuống chiều 512.
  - Ba encoder song song (mỗi cái cho `f_A`, `f_B`, `f_J`), mỗi encoder = multi-head self-attention + FFN
    kèm residual + LayerNorm. Attention theo kiểu **key-based (Eq 2):** `Attention(Q,K,V) = softmax(K·Qᵀ / √d_k)·V`,
    và điểm mấu chốt là **ma trận query `Q` được chia sẻ giữa các nguồn trong khi `K,V` đến từ từng modality** —
    "việc chia sẻ ma trận này ... giúp mô hình bổ sung redundancy và bổ trợ (complement) cho các modality
    visual và audio."
  - **Sáu layer cross-modal attention** (Q của một nguồn được chia sẻ với K,V của nguồn kia). Sáu output
    512-d của chúng được **xếp chồng thành một sequence, sau đó một block self-attention cuối cùng cân
    (weigh) chúng một cách động, rồi qua FC head.**
  - **Loss (Eq 3):** CCC loss `L_c = 1 − ρ_c = 1 − 2σ_xy / (σ²_x + σ²_y + (μ_x − μ_y)²)` — tối đa hóa
    concordance giữa dự đoán và ground truth. Valence và arousal được tách rời (decoupled): họ train các
    cấu hình riêng và, cho ensemble được báo cáo, lấy "cái tốt nhất ở mỗi hạng mục" (dual model).
- **Điểm mới so với cross-attention thuần** chính xác là nhánh thứ ba `f_J`: nó "đưa vào redundancy ... để
  mô hình có thể tập trung động vào thông tin mới được đưa vào này trong các sequence mà **cả hai modality
  đồng thời bị nhiễu**," giảm nhẹ độ nhạy của cross-attention đối với input nhiễu (§2.2, §3, Conclusion).
- **Backbone (đóng băng trong lúc fusion).** Visual = R(2+1)D và/hoặc I3D (pretrain trên Kinetics, 224×224,
  clip dài 8); audio = **ResNet18 trên log-power spectrogram** (DFT 1024, hop 10 ms, window 20 ms, 64×107 px,
  conv đầu tiên được chỉnh cho 1 kênh); BioVid physiological = một 1D-CNN tùy chỉnh trên EDA (Table 1).
  Fusion được train bằng SGD, LR grid [8e-4, 6e-4, 3e-4], batch 32, tối đa 5 epoch với early-stopping
  (Affwild2); ADAM LR 5e-6 batch 128 (BioVid).
- **Kết quả.**
  - **Aff-Wild2 official validation (Table 3):** V **0.717** / A **0.614** / trung bình **0.666**. [đã kiểm chứng] (arXiv HTML + Table 3).
  - **Aff-Wild2 test (Table 4):** V **0.472** / A **0.443** / trung bình **0.458**, so với challenge baseline
    0.180/0.170/0.175 và so với lượt chạy lại của họ với **Joint Cross Attention [46] = 0.369** nên JMT
    "**cải thiện 7%**". [đã kiểm chứng] (Table 4, §5.1).
    Lưu ý khoảng cách val→test lớn (**0.666 → 0.458**) — hiện tượng overfitting trên 341 video train.
  - **Ablation (Tables 5–7):** JMT so với vanilla multimodal transformer = **+1.8%** (backbone R2D1) / **+1.7%**
    (I3D) trên Aff-Wild2, **+1.3%** trên BioVid; so với concat thuần = **+6%** trên BioVid. [ước lượng gần đúng] —
    **không có std/CI, chỉ một split**, nên các delta này nằm trong khoảng biến thiên fold có thể xảy ra.
    (Tables 5, 6, 7.)
  - **BioVid (Table 2):** JMT **89.1%** > vanilla transformer 87.8% > concat 83.5%; unimodal chỉ-EDA 77.2%,
    chỉ-visual 72.9% — modality sinh lý (physiological) chiếm ưu thế. [đã kiểm chứng] (Table 2).

### Các phần trực tiếp hữu ích cho ViEmoSpeech (gắn nhãn theo Decision ID)

1. **[V-A] Nhánh thứ ba "joint-representation" như một template fusion chống nhiễu (noise-robustness).**
   `f_J = [f_B;f_A]` (Eq 1) được đưa vào như một encoder riêng bên cạnh hai encoder đơn-modal, kèm chia sẻ
   key trên sáu block cross-attention (Eq 2), và một block self-attention cuối cùng tái cân (re-weight)
   toàn bộ sáu luồng. Đây là một fusion head **drop-in, frozen-backbone, không đệ quy (non-recursive)** —
   đơn giản nhất trong ba template fusion hiện có trong tay (Q-Former của CASE/FAS, gate của WavFusion, và
   cái này). Nó rẻ hơn phần đệ quy của #17 (không có vòng lặp `l`).
2. **[V-A / đối chiếu với #17] Động cơ "cả hai modality đồng thời nhiễu" một cách tường minh.** Toàn bộ luận
   điểm của JMT là redundancy được concatenate bảo vệ fusion khi *cả hai* luồng cùng suy giảm một lúc — đây
   chính xác là trường hợp xấu nhất của ViEmoSpeech (lỗi tone-swap ASR ở high-arousal làm hỏng luồng text
   **trong khi** audio phim truyền hình VN được Demucs khôi phục tự nó cũng đang nhiễu). Đây là paper fusion
   duy nhất gọi tên chế độ double-noise này như mục tiêu, dù nó chưa từng đo lường nó.
3. **[V-G] CCC loss `L_c = 1 − ρ_c` (Eq 3)** giống hệt (byte-identical) với Eq 16 của #17 — một phiếu bầu
   CVPRW độc lập thứ hai cho CCC-làm-training-objective cho V/A head, và việc **tách rời valence/arousal**
   của họ (cấu hình riêng, chọn dual-model) là một datapoint thiết kế cụ thể cho câu hỏi liệu ViEmoSpeech
   nên dùng chung hay tách V/A head.
4. **[V-B] Audio backbone là một control KHÔNG nên sao chép.** ResNet18 trên log-power spectrogram, đóng
   băng — cùng họ spectrogram-CNN với VGGish của #17. Đây là baseline mà các arm WavLM/emotion2vec(-S)/
   PhoWhisper-encoder của chúng ta phải vượt qua, không phải một thiết kế để tái sử dụng; giữ nó (hoặc một
   MFCC-CNN, xem vn-10) chỉ như một hàng floor.

### Cách mỗi phần giúp ViEmoSpeech thành công

- **V-A (artifact cụ thể = fusion head trong lưới ablation của method paper).** Thêm một **hàng "JMT-joint"**
  vào thang fusion V-A — giữa "concat+FC" (floor của bimodal-11) và các lựa chọn recursive/Q-Former — nối
  feature audio WavLM/emotion2vec đóng băng với feature text PhoBERT-trên-PhoWhisper, dùng nhánh `f_J`
  concatenate làm luồng redundancy. Hoán đổi vị trí visual encoder bằng vị trí text encoder; block này
  agnostic với modality (nó đã chạy được face↔voice và voice↔EDA). Báo cáo cùng với split theo lát
  **có-lỗi-ASR vs không-có-lỗi-ASR** (V-G), vì tuyên bố về redundancy của JMT chỉ thú vị *nếu* nó sống sót
  qua substrate nhiễu của chúng ta — điều mà paper chưa bao giờ kiểm chứng.
- **Chốt an toàn double-noise của V-A.** Nhánh `f_J` là một hiện thực rẻ tiền của cơ chế audio-anchoring /
  modality-dropout mà vn-12 (EMIS) và bimodal-07 (deep-supervision) đòi hỏi: khi text ASR sụp đổ dưới một
  lỗi tone-swap, nhánh joint vẫn mang tín hiệu bắt nguồn từ audio. Kết hợp nó với một lịch trình
  modality-dropout trong lúc train để `f_J` học cách bù trừ — đây là nâng cấp khả thi so với concat thuần.
- **V-G (artifact = loss + eval của V/A head).** Đặt loss của V/A head thành `1 − ρ_c` (Eq 3), và ghi nhận
  rằng cả hai paper audio-visual CVPRW đều **tách rời valence và arousal** — với thang Russell rời rạc 1–5
  của ViEmoSpeech, train một head nhưng báo cáo V và A riêng với **CCC bên cạnh QWK/MAE** (con số CCC không
  tương đương like-for-like với dải liên tục [-1,1] của Aff-Wild2 — số hạng phương sai của chúng ta bị chi
  phối bởi 5 bin).
- **V-B (artifact = arm ablation backbone).** Giữ kết quả ResNet18-spectrogram của JMT như một hàng "floor
  của spectrogram-CNN nông" tường minh để mức tăng từ SSL-backbone của chúng ta trở nên rõ ràng; không áp
  dụng nó.

### Lăng kính chuyển giao cho trẻ em / lâm sàng-liền kề + tone×emotion

- **Việc hoán đổi visual→text sạch về mặt kiến trúc nhưng chưa được chứng minh thực nghiệm cho audio↔text.**
  Block của JMT agnostic với modality trên giấy tờ, nhưng **mọi con số được báo cáo đều là face↔voice hoặc
  voice↔EDA** — chưa bao giờ là audio↔text, và chưa bao giờ trên một ngôn ngữ có thanh điệu (tonal). Cross-attention
  theo kiểu key-based *về lý thuyết* nên chuyển giao được (nó chỉ là Q-sharing trên hai chuỗi token), nhưng
  lợi ích redundancy của nhánh joint chỉ được chứng minh ở nơi hai luồng được căn chỉnh (aligned) theo thời
  gian với các dense video/signal feature; text ASR thì thưa (sparse), ở cấp độ token, và không căn chỉnh
  với các frame audio. **Rủi ro chuyển giao = CAO-TRUNG BÌNH:** cơ chế thì port được, nhưng *bằng chứng* thì
  không.
- **Điểm mù thiếu ablation-ASR lặp lại — và ở đây nó mang tính load-bearing.** Tuyên bố trung tâm của JMT
  là khả năng chống nhiễu "khi cả hai modality đồng thời nhiễu," nhưng bằng chứng duy nhất là một **trực quan
  hóa attention-weight (Fig 4)** — không có noise injection có kiểm soát, không có đường cong missing-modality,
  không có lát cắt theo lỗi-ASR. Với ViEmoSpeech đây chính xác là chế độ chưa được kiểm chứng (lỗi ASR
  tone-swap tiếng Việt ở high-arousal). Ablation về độ bền vững ASR của chúng ta sẽ là phép đo thực sự đầu
  tiên của thuộc tính mà JMT chỉ khẳng định — một đóng góp thực thụ, không phải một sự tái tạo.
- **Tone×emotion chưa được đụng tới.** Không có xử lý F0/phonation; audio branch là một CNN spectrogram
  tổng quát. Không có gì ở đây soi sáng cho V-D — nhất quán với phát hiện xuyên suốt rằng 0/N paper bimodal
  đo lường sự cạnh tranh kênh giữa lexical-tone và emotion. Kênh F0 mang thanh điệu tiếng Việt đơn giản chỉ
  bị lấy trung bình vào trong spectrogram.
- **Đạo đức/phạm vi.** Affect diễn xuất/in-the-wild trên YouTube + pain nhiệt gây ra thực nghiệm; không có
  dữ liệu lâm sàng hay trẻ em, không có construct distress. Không có gì chuyển giao cho V-F ngoài lưu ý
  chung rằng CCC trên các corpus gated bên ngoài (Aff-Wild2, BioVid) không phải là baseline của ViEmoSpeech.

### Hạn chế & câu hỏi mở cho ViEmoSpeech

- **★ Mâu thuẫn (trực tiếp, cùng venue + cùng lab): phương pháp "joint" mới hơn lại THUA phương pháp đệ quy.**
  Trên **cùng tập test Aff-Wild2**, JMT (#18) đạt mean **0.458** (V 0.472 / A 0.443) trong khi RJCMA (#17)
  đạt mean **0.5807** (V 0.542 / A 0.619) — RJCMA **dẫn trước +0.12 CCC**, và RJCMA là paper *thêm một
  modality text* và *đệ quy*, trong khi JMT bỏ text và chỉ thêm nhánh joint-redundancy. Vậy nên tuyên bố
  của stub rằng JMT "dễ port nhất, do đó được ưu tiên" bị mâu thuẫn bởi benchmark: cơ chế dễ port hơn cũng
  chính là cơ chế yếu hơn, và thành phần thắng trên shared task **chính xác là luồng text mà ViEmoSpeech
  phải thêm vào**. Đây là một datapoint *ủng hộ* việc đầu tư vào text branch và các họ fusion
  recursive/Q-Former, và *phản đối* việc coi nhánh joint-concat thuần túy là đủ. (Mức +7% nội bộ của chính
  JMT là so với baseline [46] cũ hơn, không phải so với RJCMA.)
- **Mức tăng của ablation nằm trong khoảng nhiễu.** +1.3–1.8% JMT-so-với-vanilla, chỉ một split,
  **không có std/CI** — vọng lại bimodal-15 (Schuller): các thứ hạng backbone/fusion không ổn định theo
  hyperparameter (HP-unstable) và các delta nhỏ không sống sót qua resampling. Sự sụp đổ lớn từ **val 0.666
  xuống test 0.458** cảnh báo rằng trên tập held-out gold nhỏ của ViEmoSpeech, các tham số bổ sung của nhánh
  joint là một rủi ro overfitting; cần bootstrap CI trước khi ghi nhận bất kỳ delta fusion nào.
- **CCC test Aff-Wild2 ≈ 0.46–0.58 là dải trần (ceiling band) trung thực cho V/A in-the-wild tự nhiên** —
  thấp hơn nhiều so với các con số VN bị rò rỉ (leaky) (vn-08 86.6, vn-10 0.87) và nhất quán với MSP-Podcast
  (~0.72 CCC trên audio sạch hơn, bimodal-12) — củng cố thêm rằng ViEmoSpeech nên công bố một CCC thấp,
  trung thực và gắn cờ các đối tượng so sánh bị rò rỉ.
- **Câu hỏi mở:** Code công khai của JMT (`github.com/PoloWlg/Joint-Multimodal-Transformer-6th-ABAW`) là
  một module fusion frozen-backbone — đáng để fork làm hàng baseline V-A "joint-concat + key-sharing", nhưng
  chỉ nếu chúng ta có thể ghép text encoder vào vị trí visual mà không cần giả định căn chỉnh dày đặc
  (dense-alignment); phép ghép đó chính là rủi ro kỹ thuật chưa được kiểm chứng.
