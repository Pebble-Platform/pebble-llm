# Paper 07 — Bimodal Connection Attention Fusion for Speech Emotion Recognition

> Bản dịch tiếng Việt của [07-bimodal-connection-attention.md](07-bimodal-connection-attention.md) — cập nhật 2026-07-10.

- **Authors:** Jiachen Luo, Huy Phan, Lin Wang, Joshua D. Reiss (QMUL)
- **Venue / year:** arXiv preprint 2025
- **Links:** abs https://arxiv.org/abs/2503.05858 · PDF `pdfs/07-bimodal-connection-attention.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Interactive connection network + bimodal attention + contrastive audio-text alignment để lọc nhiễu cross-modal.

**Relevance to Pebble:** Công thức cụ thể cross-attention + contrastive alignment. **Lưu ý:** có cặp near-duplicate arXiv 2503.05858 / 2503.06405 cùng nhóm — xác nhận bản supersede trước khi deep-read.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Pebble profile used (assembled at analysis time):** Primary = ordinal suicide-risk **text** classification (BERT-family encoder, teacher-LLM silver labels, gold-holdout eval, ordinal-aware QWK/MAE; contribution is methodological honesty, not SOTA). Adjacent **voice** stream = frozen SSL backbone (WavLM-Large / emotion2vec) + 3 **heterogeneous MTL heads** (emotion CE + affect valence/arousal **CCC regression** + crisis BCE under a **hard recall floor 0.90**), balanced by **Kendall uncertainty weighting**. Voice+text **fusion is the forward direction**, not the current stage.

### Analysis — BCAF (Bimodal Connection Attention Fusion)
- **Overlap:** 23% (peripheral) — D1=1, D2=0, D3=1, D4=0, D5=0, D6=0, D7=2
  - Formula: (3·1 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·2) / 26 × 100 = 6/26 × 100 = 23%.
- **Closest on:** D7 (backbone match — audio **wav2vec-large SSL** + text **RoBERTa**, tức chính xác cặp voice-SSL + text-BERT của Pebble) và D1/D3 khớp một phần (multi-head auxiliary supervision trên các corpus cảm xúc MELD/IEMOCAP).
- **Best point (Method to adopt):** Giữ lại **các head phụ trợ theo từng modality** (audio-only `L_a`, text-only `L_l`) song song với head hợp nhất `L_m`, cộng thêm một lớp **correlative/connection attention** để hạ trọng số tín hiệu cross-modal xung đột — đây chính là cơ chế phòng vệ cụ thể của BCAF trước hiện tượng sụp đổ nổi tiếng "text lấn át audio, nhánh audio bị bỏ qua" trong fusion audio+text.
  - **How to apply to Pebble:** khi luồng voice hợp nhất với text risk model, không concatenate-rồi-classify; hãy deep-supervise từng nhánh (logit audio-only + text-only) song song với logit hợp nhất và thêm một cross-attention correlative gate, để tín hiệu paralinguistic (voice) sống sót qua fusion thay vì bị text encoder mạnh hơn ghi đè.
- **Caveats:**
  - Chấm điểm dựa trên abstract + intro/method (tr.1–4); phần results/ablation chưa đọc — nhưng điều này không ảnh hưởng đến các trục domain/method/backbone được chấm ở đây.
  - **Không** thấy head liên tục, domain crisis/mental-health, teacher-LLM distillation, hay MTL loss balancing có nguyên tắc — cả bốn head đều là categorical emotion; phần "dynamic" weighting nằm ở mức attention, không phải mức task-loss (nên D1 khớp một phần, D5=0). Đây là một paper **kiến trúc fusion**, và rubric của Pebble ưu tiên tính đa dạng của MTL-head / crisis / distillation, điều này kéo % xuống dù công thức fusion vẫn liên quan trực tiếp đến hướng đi tiếp theo.
  - **Sibling disambiguation:** arXiv **2503.06405** là *"Heterogeneous Bimodal Attention Fusion (HBAF)"* — một paper **khác biệt, không phải bản trùng** từ cùng nhóm (cùng setup MELD/IEMOCAP). Bản v3 cuối cùng của HBAF có ngày **2025-04-01**, muộn hơn bản v3 của BCAF (**2025-03-22**), và HBAF bổ sung một **cơ chế dynamic gating + inter-modal contrastive learning** mà BCAF không có (BCAF thay vào đó dùng encoder-decoder connection loss + correlative attention). Cách đọc tốt nhất: HBAF là sibling **muộn hơn, mở rộng hơn**; coi BCAF (paper này) là biến thể connection-attention, không phải nội dung bị supersede — nên deep-read HBAF trước nếu chỉ đọc một trong hai.

## Deep research — full-PDF read (2026-07-10)

> Đọc đối chiếu với **hồ sơ ViEmoSpeech hiện tại + Decision Register V-A…V-H**
> (`docs/tasks/paper-deep-analysis.md`), không phải hồ sơ text-stream đã lưu trữ trong
> phần "Analysis" bên trên. PDF được đọc toàn bộ qua `pdftotext` trên
> `pdfs/07-bimodal-connection-attention.pdf` (arXiv:2503.05858**v3**, 22 Mar 2025, QMUL
> Centre for Digital Music — Luo, Phan, Wang, Reiss). Các quyết định nhắm tới: **V-A** (cơ chế
> fusion audio+text đã học), **V-C** (nhánh text có phải là bộ mã hóa transcript thật sự không?),
> **V-G** (giao thức đánh giá/metric). Không tìm thấy venue trả phí — đây chỉ có bản arXiv; bản
> v3 tại chỗ là phiên bản có thẩm quyền.

### Source-access note

- **Read method:** `pdftotext ".../07-bimodal-connection-attention.pdf" -` (toàn bộ nội dung,
  tất cả phương trình, Bảng I–II, toàn bộ phần ablation, ma trận nhầm lẫn, tài liệu tham khảo).
  Hình 6, 8, 9 là ảnh raster — số liệu bên trong **không** trích xuất được dưới dạng văn bản, nên
  wF1 tuyệt đối của BCAF chỉ nằm trong hình và được ghi lại ở đây là **chưa được đối chiếu bằng
  số**.
- **Web validation:**
  - Truy vấn `"Bimodal Connection Attention Fusion BCAF ... arXiv 2503.05858"` → tìm ra
    https://arxiv.org/abs/2503.05858 và https://arxiv.org/html/2503.05858v3. Xác nhận
    hai delta chính: **+3.15% wF1 so với HCAM (MELD)**, **+4.11% wF1 so với Mamba (IEMOCAP)** ✔.
  - Cùng truy vấn cho ra sibling https://arxiv.org/abs/2503.06405 (HBAF) — xác nhận việc phân
    biệt trong stub hiện có: **2503.06405 = một paper khác biệt (Heterogeneous Bimodal
    Attention Fusion), không phải bản supersede** của paper này ✔.
  - `WebFetch` trên bản HTML v3 xác nhận số liệu biến thể attention trong **Bảng II** (xem
    bên dưới) và mô tả encoder nguyên văn; **không** khôi phục được F1 tuyệt đối ở Hình 6 (ảnh)
    và xác nhận các hệ số trọng số loss (μ/β/γ) **không được** nêu bằng số trong paper ✔.

### What the paper actually does

- **Task / data:** SER hội thoại, **chỉ categorical**, trên **MELD** (7 cảm xúc từ
  *Friends*; 13,708 utt / 1,433 hội thoại; Bảng I train+val 11,098 / test 2,610) và **IEMOCAP**
  (6 lớp; 10 người nói, 12.46 giờ; Bảng I train+val 5,810 / test 1,623). Metric chính = **chỉ
  weighted-F1** (chọn "do sự mất cân bằng tự nhiên") — không có macro-F1, không có V/A theo
  chiều liên tục, không có CCC ở đâu cả. Tất cả ✔ (Bảng I / §IV.A).
- **Uni-modal encoders (§III.A):** audio = **large wav2vec**, một vector **1024 chiều ở mức
  utterance** `Ha` ✔; text = **RoBERTa**, nhận "transcript của utterance làm đầu vào", lấy
  trung bình **bốn lớp cuối** thành một vector **1024 chiều** `Hl` ✔. Cả hai được dùng như
  **bộ trích xuất đặc trưng cố định ở mức utterance** (không mô tả việc fine-tune backbone; chỉ
  huấn luyện phần fusion) — một thiết kế **frozen-backbone**, khớp với kế hoạch của
  ViEmoSpeech.
- **Ba mô-đun fusion (§III.B):**
  1. **Interactive Connection Network** — encoder-decoder theo từng modality (3 FC+ReLU mỗi
     nhánh, `Hm` 1024→`em` 512→`dm` 1024) huấn luyện bằng **connection loss** (Eq. 3):
     `Lc = ‖Ha−da‖²_F + ‖Hl−dl‖²_F + μ(‖I−eₐeₗᵀ‖²_F − ‖I−dₐdₗᵀ‖²_F)` — tái tạo (reconstruction)
     cộng với **căn chỉnh không gian latent/reconstructed kiểu CLIP** giữa hai modality (μ cân
     bằng). ✔
  2. **Bimodal Attention Network** — self-attention chồng lớp (Eq. 4–6, intra-modal) +
     cross-attention (Eq. 7–12, inter-modal, query từ modality đối diện), mỗi khối có
     LayerNorm/AddNorm/FeedForward → `hsa,hsl,hca,hcl` (đều 1024 chiều). ✔
  3. **Correlative Attention Network** — một **Joint Attention Network** với *cặp softmax*
     (Eq. 14: `softmax(intra) − Φ·softmax(cross)`, Φ có thể học được — số hạng cross bị **trừ
     đi** để triệt tiêu tương tác cross-modal nhiễu) và một **Bimodal Correlation Evaluation**,
     **lấy cảm hứng từ CLIP**, dùng **cosine similarity** giữa mỗi mã latent uni-modal và mã
     hợp nhất `hb` → các hệ số `cor_a-b, cor_l-b` (Eq. 15) để **tái trọng số** các biểu diễn
     uni-modal: `ĥa = hsa·cor_a-b`, `ĥl = hsl·cor_l-b` (Eq. 16). ✔
- **Classification & loss (§III.C-D):** ghép nối `hca⊕hcl⊕ĥa⊕ĥl` → **3072 chiều** → 4 lớp FC.
  Ba head CE **độc lập** — audio `La` (Eq. 19–20), text `Ll` (Eq. 21–22), bimodal `Lm`
  (Eq. 23–24) — kết hợp lại: **`L = μ·Lc + β(La + Ll) + Lm`** (Eq. 18; deep supervision theo
  từng modality). Giá trị trọng số μ/β/γ **không được nêu** ✖. ✔ về mặt cấu trúc.
- **Config (§IV.C):** PyTorch 1.11, Adam **lr 1e-4**, early-stop **patience 15**, **L2 1e-4**,
  **dropout 0.3**. ✔
- **Headline results (§V.A, Fig. 6):** BCAF **+3.15% wF1 so với HCAM trên MELD**, **+4.11% wF1
  so với Mamba trên IEMOCAP** ✔ (đã đối chiếu). wF1 tuyệt đối của BCAF chỉ nằm trong hình
  ✖-numerically.
- **Ablations (§V.B, số liệu văn bản tham chiếu Fig. 6):** thứ tự tác động khi loại bỏ
  **correlative > bimodal > interactive**. Interactive connection net **+2.81% MELD / +2.83%
  IEMOCAP**; bimodal attention net **+4.1% / +5.12%**; **correlative attention net +5.24% /
  +6.68%** (lớn nhất) ✔ (nêu trong phần thân văn bản; các cột biểu đồ nằm ở Fig. 6). Nghiên cứu
  biến thể attention (**Bảng II**, F1 "w/o"): BAN 64.83/69.57, JAN 66.08/71.35,
  BAN-SA 67.21/72.16, BAN-CA 67.52/73.01 ✔; BAN đầy đủ cho **+3.6% MELD / +6.6% IEMOCAP** so
  với baseline không-BAN; việc loại bỏ chỉ cross-attention (BAN-CA) tốn kém ít nhất
  (−1.41% / −1.69%), vậy nên theo cách đọc của họ **self-attention intra-modal đóng góp nhiều
  hơn cross-modal**.
- **Error analysis (§V.D-E, ma trận nhầm lẫn Fig. 9):** các lớp hiếm sụp đổ — MELD
  **fear diag 34.00%, disgust 47.06%**, IEMOCAP happy 61.81% — trong khi neutral (84.95%) và
  angry (75.88%) chiếm ưu thế ✔. **Mâu thuẫn nội tại:** abstract/§V.A khẳng định BCAF vượt
  HCAM +3.15% trên MELD, nhưng phần case-study §V.D lại viết BCAF "hoạt động kém hơn mô hình
  state-of-the-art HCAM" (quy cho việc HCAM có mô hình hóa người nói bằng GCN) — paper tự mâu
  thuẫn về so sánh với HCAM ⚠✔.

### Parts directly useful for ViEmoSpeech (tagged by Decision)

1. **[V-A] Deep-supervision theo từng modality + head hợp nhất (Eq. 18–24).** Ba head CE (`La`
   audio-only, `Ll` text-only, `Lm` hợp nhất) dưới `L = μ·Lc + β(La+Ll) + Lm`. Một **ứng viên
   learned-fusion** cụ thể ở mức phương trình, và là cách phòng vệ tường minh của paper trước
   hiện tượng sụp đổ "text lấn át, nhánh audio chết" mà vn-12/bimodal-01 đã cảnh báo.
2. **[V-A] Connection loss Lc (Eq. 3) như một bộ điều chuẩn căn chỉnh modality.** Reconstruction
   cộng với căn chỉnh latent kiểu CLIP giữa các mã audio/text đóng băng — một auxiliary
   self-supervised có thể gắn kết audio WavLM/emotion2vec và text PhoBERT của chúng ta vào
   cùng một không gian *trước khi* đưa vào classifier. Ablation ghi nhận +2.81/+2.83%.
3. **[V-A] Correlative attention với tái trọng số cosine kiểu CLIP (Eq. 14–16).** Cặp softmax
   dạng trừ (`−Φ·softmax(cross)`) cộng với gating dựa trên cosine similarity là **đóng góp
   ablation đơn lẻ lớn nhất (+5.24/+6.68%)** và được nêu rõ là một **bộ lọc nhiễu cross-modal**
   — cơ chế ứng viên gần với vấn đề nhiễu ASR của chúng ta nhất cho V-C.
4. **[V-C] Nhánh text là một *bộ mã hóa transcript thật sự* (RoBERTa trên transcript của
   utterance, trung bình 4 lớp cuối → 1024 chiều).** Khác với EAA/bimodal-03 (audio↔audio
   HuBERT+BEATs), BCAF là fusion **audio↔text thật sự** — một tiền lệ kiến trúc V-C hợp lệ cho
   cặp audio+PhoWhisper-text của chúng ta. **Nhưng transcript ở đây là gold** (MELD/IEMOCAP đi
   kèm transcript do con người tạo); ASR chưa bao giờ được chạm tới.
5. **[V-G] Công thức fusion đặc trưng-utterance-đóng-băng + config** (wav2vec-1024 ⊕
   RoBERTa-1024, Adam 1e-4, early stop patience-15, L2 1e-4, dropout 0.3) — một bộ khung huấn
   luyện có thể chuyển dùng trực tiếp cho nhánh fusion frozen-backbone của chúng ta.
6. **[V-G] Báo cáo chỉ-weighted-F1 là anti-pattern cần sửa.** Fig. 9 của họ cho thấy fear 34%/
   disgust 47% trong khi wF1 headline trông vẫn khỏe mạnh — một minh chứng cụ thể rằng wF1
   **che giấu sự sụp đổ ở lớp hiếm**, là động lực cho việc báo cáo macro-F1 + ngưỡng sàn
   per-class của chúng ta.

### How each part helps ViEmoSpeech succeed

- **V-A (nhánh fusion):** Xây dựng nhánh learned-fusion vượt qua định vị rule-fusion đã rút lại
  (vn-09) bằng **ba head được deep-supervise** (`audio-only`, `text-only`, `fused`) và
  **connection loss** làm auxiliary. Điều này mang lại hai lợi ích cùng lúc: (a) head phụ
  audio-only chính là **cơ chế bảo hiểm neo-audio (audio-anchoring)** mà vn-12 yêu cầu để chặn
  hiện tượng text-collapse, và (b) nó đứng cạnh ứng viên Q-Former CASE/FAS (vn-07) và gating của
  WavFusion như một lựa chọn V-A thứ ba, hoàn chỉnh về mặt phương trình — chọn qua ablation trên
  clip của chúng ta. Artifact cụ thể: một module `fusion/bcaf_heads.py` với
  `L = μ·Lc + β(La+Ll) + Lm` và một config sweep trên β (trọng số audio so với text) như
  **knob điều chỉnh tải kênh tone (tone-channel-load)** của chúng ta.
- **V-A (correlative attention):** Chuyển correlative attention network thành **khối lọc nhiễu
  (noise-gating)** trong nhánh fusion — đây là đòn bẩy ablation lớn nhất của họ
  (+5.24/+6.68%) và mục đích được nêu rõ ("lọc các quan hệ cross-modal sai") chính là thứ chúng
  ta cần khi text PhoWhisper một phần bị sai. Ablate nó trên một **lát cắt lỗi-ASR held-out** để
  đo xem nó có thực sự hạ trọng số một token text bị hỏng ở mức arousal cao hay không.
- **V-C (thí nghiệm độ bền ASR):** Vì nhánh text của BCAF là thật nhưng **chỉ từng được cho ăn
  transcript gold**, việc chạy BCAF hai lần — một lần trên caption YouTube (gold proxy của
  chúng ta), một lần trên đầu ra ASR PhoWhisper (với các lỗi hoán đổi tone mày→máy /
  tao→tháo) — biến paper này thành một **phép thử độ bền V-C trực tiếp**: connection loss kiểu
  CLIP *giúp ích* (căn chỉnh audio để khử nhiễu text) hay *gây hại* (căn chỉnh audio theo một
  transcript bị hỏng)? Dù kết quả thế nào cũng là một phát hiện mà chưa thí nghiệm nào của
  BCAF/CASE từng báo cáo.
- **V-G (sửa metric):** Áp dụng bộ khung frozen-feature của BCAF nhưng **thay thế metric
  headline** — báo cáo **macro-F1 + ngưỡng sàn recall theo từng lớp + CCC cho V/A** dưới
  điều kiện speaker-disjoint + holdout toàn series (ADR-002). Sự sụp đổ ở Fig. 9 của họ là lý
  do biện minh của chúng ta: "weighted-F1 che giấu tỉ lệ fear 34%; chúng ta báo cáo macro để
  các lớp hiếm-nhưng-liên-quan-đến-an-toàn (distress) không thể bị 'giặt trắng' số liệu."

### Child mental-health / ViEmoSpeech transfer lens

- **Lệch register:** MELD = sitcom *Friends* (người lớn, tiếng Anh, kịch bản-diễn, nhiễu nền
  cao: "tiếng còi xe, tiếng chó sủa"); IEMOCAP = hội thoại đôi người lớn, diễn xuất, tiếng Anh.
  **Không có ngôn ngữ thanh điệu, không có tiếng Việt, không có giọng trẻ em.** *Cơ chế*
  (topology fusion, connection loss, correlative attention) không phụ thuộc ngôn ngữ và có thể
  chuyển giao; *các con số* (delta wF1, Bảng II) thì **không** chuyển giao sang phim truyền hình
  VN thanh điệu, gần-trẻ-em.
- **Tone×emotion chưa được chạm tới:** ví dụ minh họa gốc của BCAF ("cao độ giọng nói cao hơn
  tương quan với sự phấn khích") coi pitch là tín hiệu cảm xúc paralinguistic **không có khái
  niệm về tranh chấp thanh điệu từ vựng** cạnh tranh trên cùng kênh F0/phonation. Nhất quán với
  phát hiện xuyên suốt: **0 paper đo lường sự cạnh tranh giữa thanh điệu từ vựng × cảm xúc** —
  tính mới của V-D vẫn còn nguyên vẹn; BCAF là thêm một điểm dữ liệu xác nhận, không phải một
  đối thủ cạnh tranh trên tuyên bố này.
- **Giả định transcript gold là rủi ro trọng yếu đối với chúng ta.** Connection loss và
  correlative attention của BCAF **giả định text mang tín hiệu bổ sung sạch**. Dưới nhiễu hoán
  đổi tone của ASR tiếng Việt (hồ sơ: PhoWhisper mean sim 87.2 so với caption; lỗi tăng vọt ở
  arousal cao — chính là các utterance mang cảm xúc), một mục tiêu "căn chỉnh audio theo text"
  kiểu CLIP có thể **kéo biểu diễn audio về phía một từ sai**. Giải pháp giảm thiểu: gate
  connection loss bằng một tín hiệu độ tin cậy ASR, hoặc huấn luyện head audio-only `La` với β
  cao hơn để một nhánh text bị hỏng không thể lấn át — có thể đo được qua thí nghiệm độ bền V-C
  ở trên.
- **Khung distress:** chỉ categorical, chỉ weighted-F1 — **không có tín hiệu liên tục hay lâm
  sàng**. BCAF không cho chúng ta điều gì cho **ngưỡng sàn recall V-F distress** một cách trực
  tiếp; nếu có thì hành vi wF1-che-giấu-lớp-hiếm của nó chính là kiểu thất bại mà ngưỡng sàn
  recall + ngưỡng sàn ≥50 clip (ADR-002) của chúng ta tồn tại để ngăn chặn. Trích dẫn như
  method-transfer cho fusion, **không** cho head distress.
- **Đạo đức:** corpus benchmark công khai, không có mối quan ngại human-subjects nào ngoài bản
  gốc; không có gì cần nhập khẩu hay né tránh về mặt governance.

### Limitations & open questions for ViEmoSpeech (≥1 contradiction/gap)

- **Mâu thuẫn #1 (nội tại trong paper):** abstract/§V.A khẳng định "vượt HCAM +3.15% trên
  MELD" trong khi §V.D lại viết "hoạt động kém hơn mô hình state-of-the-art HCAM." Một headline
  trọng yếu mà paper tự mâu thuẫn ⇒ coi con số +3.15% MELD là **mềm (soft)**; con số +4.11%
  IEMOCAP (so với Mamba) là tuyên bố sạch hơn. Không trích dẫn việc BCAF vượt SOTA trên MELD như
  một điều đã chốt.
- **Mâu thuẫn #2 (so với ghi chú cũ + so với EAA/bimodal-03):** ghi chú "Analysis" cũ ở trên và
  bản đọc EAA đã gộp hai paper này chung nhóm cross-attention fusion; **BCAF là một fusion
  audio↔text đã học thực sự**, trong khi EAA là audio↔audio (HuBERT+BEATs). Vậy BCAF là tiền lệ
  kiến trúc V-C/V-A **tốt hơn** trong hai paper — đã ghi nhận sửa chữa này.
- **Khoảng trống #1 (so với kế hoạch ViEmoSpeech — nhiễu ASR):** mọi thành phần của BCAF chạm
  đến text (connection loss, correlative attention, text head) đều chỉ được kiểm chứng **trên
  transcript gold**. "Nhiễu cross-modal" trung tâm của paper là **nhiễu âm thanh nền**, không
  phải lỗi phiên âm — vậy nên bằng chứng lọc nhiễu của nó **không** bao phủ chế độ thất bại của
  chúng ta. Chưa được kiểm chứng và mang tính nghiên cứu.
- **Khoảng trống #2 (so với V-G / so với bimodal-02):** BCAF xử lý mất cân bằng **chỉ qua metric
  weighted-F1** — không có reweighting, resampling, hay focal loss (toàn bộ bộ công cụ của
  bimodal-02), và không có macro-F1 để dù chỉ nhìn thấy sự sụp đổ. Chính ma trận nhầm lẫn của
  họ (fear 34%, disgust 47%) cho thấy cái giá phải trả. Đánh giá của chúng ta không được sao
  chép metric này; và một ngưỡng sàn corpus ≥50 clip vẫn là đòn bẩy lớp-hiếm tốt hơn bất kỳ cơ
  chế nào của BCAF (vốn không làm gì cho tính hiếm).
- **Khoảng trống #3 (khả năng tái lập):** các trọng số loss μ/β/γ (Eq. 3, 18) **không bao giờ**
  được nêu bằng số, và F1 tuyệt đối chỉ tồn tại trong Fig. 6 — sao chép BCAF đòi hỏi phải điều
  chỉnh lại các giá trị này một cách mù quáng. Cần dành ngân sách cho một β-sweep như thí
  nghiệm của riêng chúng ta thay vì giả định theo thiết lập chưa được nêu của họ.
- **Câu hỏi mở:** BCAF cho rằng self-attention intra-modal quan trọng hơn cross-attention (việc
  loại bỏ BAN-CA rẻ nhất). Nếu điều này đúng trên dữ liệu **thanh điệu tiếng Việt**, nó sẽ *làm
  suy yếu* tiền đề rằng text phải mang thêm tải — nhưng phát hiện của họ nằm trên tiếng Anh
  người lớn với transcript sạch, nên đây chính xác là kiểu kết quả phụ thuộc-register mà tổng
  hợp xuyên suốt gắn cờ là chưa-ổn-định. Đáng để tái lập trên clip của chúng ta như một điểm dữ
  liệu V-C/V-D.
