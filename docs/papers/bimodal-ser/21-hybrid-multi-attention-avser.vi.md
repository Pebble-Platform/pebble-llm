# Paper 21 — Hybrid Multi-Attention Network for Audio-Visual Emotion Recognition Through Multimodal Feature Fusion

> Bản dịch tiếng Việt của [21-hybrid-multi-attention-avser.md](21-hybrid-multi-attention-avser.md) — cập nhật 2026-07-10.

- **Authors:** Sathishkumar Moorthy, Yeon-Kug Moon
- **Venue / year:** Mathematics (MDPI), 13(7):1100, 2025 (OA)
- **Links:** abs https://www.mdpi.com/2227-7390/13/7/1100 · PDF `pdfs/21-hybrid-multi-attention-avser.pdf`
- **Group:** audio-visual (đối chứng)

**Summary:** Hybrid multi-attention fusion network cho audio-visual affect.

**Relevance to Pebble:** Fallback fusion-ablation reference; venue tier thấp — không phải primary pick.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled profile (at analysis time).** Pebble = một chương trình chính về **ordinal suicide-risk TEXT** (bộ mã hoá họ NeoBERT/BERT ~250M tham số, nhãn bạc từ teacher-LLM, đánh giá trên gold-holdout, các chỉ số ordinal-aware QWK/MAE) dưới ràng buộc cứng "không bao giờ train+eval trên cùng một nguồn nhãn" (`docs/intent/constraints.md`); cộng thêm một luồng **VOICE** liền kề (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`): backbone SSL emotion2vec/WavLM-Large đóng băng cùng một trunk chia sẻ với **ba đầu ra dị chủng (heterogeneous heads)** — emotion (CE), affect (valence+arousal, **CCC loss**), crisis (BCE dưới **ngưỡng sàn recall cứng ≥0.90**) — được cân bằng bởi **Kendall uncertainty weighting**; hướng đi forward là fusion voice+text. Được chấm điểm dựa trên profile này.

**Paper in one line.** Một mô hình nhận diện cảm xúc audio-visual (và text, trên IEMOCAP) với đóng góp là một cơ chế fusion cross-modal attention lai (CSSA = SEMAT+SPAAT; HASPCM = SMA+PCMA; collaborative cross-attention) được xây dựng để duy trì độ bền vững khi các modality không bổ trợ lẫn nhau / nhiễu / thiếu vắng. Phân loại cảm xúc phạm trù (categorical) trên IEMOCAP; hồi quy valence–arousal liên tục (với CCC) trên AffWild2/AFEW-VA. Backbone: 3D-CNN/ResNet (visual), openSMILE/1D-CNN (audio), TextCNN (text).

**Per-dimension scores (before the number):** D1=1, D2=0, D3=1, D4=0, D5=0, D6=0, D7=0

- D1 (heterogeneous heads, w3) = **1** — cho ra cả đầu ra phạm trù (IEMOCAP) lẫn V/A liên tục với CCC (AffWild2/AFEW-VA), hai loại đầu ra mà luồng voice của Pebble cần, nhưng trên các dataset/thí nghiệm riêng biệt, không phải một topology heterogeneous-head thống nhất, và không có safety head.
- D2 (mental-health/crisis, w2) = **0** — affect nói chung; chỉ nhắc thoáng qua đến "chẩn đoán các rối loạn liên quan đến cảm xúc".
- D3 (emotion-transfer / intensity corpora, w1) = **1** — AffWild2 & AFEW-VA là các corpus V/A dimensional *intensity* (rubric có bao gồm "intensity"), nhưng không phải GoEmotions/EmpatheticDialogues và không phải các bộ V/A chỉ-giọng-nói (MSP-Podcast) mà Pebble nhắm tới.
- D4 (teacher-LLM silver-label distillation, w2) = **0** — không có trong phương pháp đề xuất.
- D5 (principled MTL loss balancing, w2) = **0** — mất cân bằng được xử lý bằng rời rạc hoá 20-bin + over/under-sampling; không có uncertainty/GradNorm/PCGrad/Nash-MTL.
- D6 (safety/crisis recall constraint, w2) = **0** — không có.
- D7 (backbone match, w1) = **0** — 3D-CNN/openSMILE/TextCNN; không có emotion2vec/WavLM SSL và không có bộ mã hoá text họ BERT.

**Overlap:** (3·1 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·0) / 26 × 100 = 4/26 × 100 = **15%** — **peripheral (<40%)**.

- **Closest on:** D1 (đầu ra affect phạm trù + liên tục-CCC) và D3 (corpus V/A intensity).
- **Best point (Design lesson):** Phát hiện mang tính động lực của paper — fusion cross-attention chuẩn *giả định các modality bổ trợ lẫn nhau* và suy giảm hiệu năng trên dữ liệu thực khi chúng không bổ trợ, nhiễu, hoặc thiếu vắng; giải pháp của họ là mô hình hoá các quan hệ intra- **và** cross-modal đồng thời để các luồng mâu thuẫn/vắng mặt không làm sập dự đoán.
  - **How to apply to Pebble:** Đối với fusion voice+text theo hướng forward, không giả định các luồng đồng thuận với nhau — một giọng nói bình tĩnh đi kèm văn bản có ý định tự sát là trường hợp non-complementary mang tính an toàn-trọng yếu; nên áp dụng một fusion head vừa bảo toàn tín hiệu intramodal của từng modality vừa chịu được một luồng thiếu/không cung cấp thông tin, và stress-test nó dưới modality dropout thay vì chỉ báo cáo con số khi cả hai modality đều có mặt.
- **Caveats:** Venue MDPI/`Mathematics`, tier thấp; các tác vụ phạm trù so với liên tục nằm trên các dataset khác nhau, nên việc ghi nhận "heterogeneous heads" chỉ là một phần. Audio-visual với backbone không-SSL — các con số CCC trên AffWild2 của nó (val 0.596 / aro 0.683) **không** phải baseline công bằng cho affect head chỉ-giọng-nói của Pebble. Đọc từ PDF local (abstract, §2.2 related work, §3.1, §4.3–4.4 results); MDPI HTML trả về HTTP 403, nên việc chấm điểm chỉ dựa trên PDF.

## Deep research — full-PDF read (2026-07-10)

> Kết luận trước: đây là một **audio-visual control độ liên quan thấp** (~15%) và, đối với V-A, một
> **paper fusion trùng lặp** — nó xếp chồng các khối attention đã biết (VQA co-attention [ref 65, Lu 2016],
> Transformer self-attention [ref 45], cộng với image semantic/spatial attention) và ý tưởng chuyển giao
> được rõ ràng nhất của nó (CCC loss) đã có sẵn từ bimodal-17 RJCMA. Nó bổ sung thêm **một bài học tiêu cực
> hữu ích** (một tuyên bố robustness nổi bật nhưng không có thí nghiệm hỗ trợ) và **một anti-pattern đánh giá**
> (trộn lẫn protocol subject-independent / random-split). Phần này được giữ ở mức tương xứng.

### Source-access note

Đọc toàn bộ từ PDF local (`pdfs/21-hybrid-multi-attention-avser.pdf`, 30 trang) qua
`pdftotext` (trích xuất đầy đủ, 1056 dòng). PDF local **là phiên bản chính thức (version of record)** — MDPI
*Mathematics* 2025, 13(7):1100, DOI 10.3390/math13071100, xuất bản 27/03/2025, CC-BY. Venue và
authorship được xác thực (checkmark) qua WebSearch (`Moorthy Moon Hybrid Multi-Attention … Mathematics
2025 13 1100`) → RePEc `gam/jmathe/v13y2025i7p1100-d1621912` và Semantic Scholar `cd41/…191a.pdf`. Việc
đối chiếu **số liệu** lần thứ hai với MDPI HTML bị chặn (HTTP 403, giống với stub gốc),
nên các con số dưới đây là single-source nhưng lấy từ phiên bản chính thức đã xuất bản, không phải preprint —
được gắn nhãn (checkmark) (version-of-record) thay vì dual-corroborated. Không có chênh lệch preprint/venue
(không có bản mirror arXiv; Data Availability chỉ nêu tên một repo GitHub, commit `b2c9e03`).

### What the paper actually does

**Task.** Hai tác vụ tách biệt trên ba corpus: (a) hồi quy dimensional valence–arousal trên
**AffWild2** (564 video YouTube, ~2.8M frame, V/A trong [-1,1], split subject-independent 341/71/152-video,
§4.1) và **AFEW-VA** (600 đoạn clip phim, random 400/200 train/test, 5-fold CV, §4.1); (b)
phân loại cảm xúc phạm trù trên **IEMOCAP** (split 5162/737/1481 utterance, §4.1). Loss cho các đầu ra
hồi quy là CCC loss **L = 1 − rho_c** (Eq. 27, §3.7).

**Backbones (không-SSL, do-not-copy).** Visual = Inflated-3D CNN (I3D, 12M) + R3D-18 (33M) + ResNet-18
2D-CNN+LSTM (13.3M) trên face crop; audio = ResNet-18 (11.7M) trên log-mel spectrogram (DFT 1024,
cửa sổ 20 ms / hop 10 ms) **cộng với MFCC thủ công**; text (chỉ IEMOCAP) = TextCNN trên transcript vàng
(gold); audio trên IEMOCAP thêm dùng openSMILE (§3.1–3.4, §4.4.3, Table 3). Huấn luyện trên một
RTX A6000, SGD, lr 1e-3, 50 epoch, dropout 0.8 (Table 2).

**Fusion (phần "đóng góp"), ba module xếp chồng:**
- **CSSA** = SEMantic Attention (SEMAT, Eqs 3–5, cổng sigmoid) + SPAtial Attention (SPAAT, Eqs 6–8,
  softmax), trong đó **audio dẫn dắt luồng visual** hướng tới các vùng khuôn mặt nổi bật; đầu ra được cộng
  lại (Eq. 9), sau đó qua Bi-LSTM theo từng modality (Eqs 10–11).
- **HASPCM** = Single-Modal Attention (SMA, multi-head self-attention chuẩn, Eqs 12–17) + Parallel
  Cross-Modal Attention (PCMA, một co-attention "lấy cảm hứng từ module parallel attention trong [65]"
  = Lu et al. VQA hierarchical co-attention 2016, Eqs 18–23).
- **CMRA** = Cross-Modality Relation Attention trên các đặc trưng đã fusion nối lại (Eqs 24–26).

**Headline numbers (tất cả là version-of-record, checkmark):**

| Result | Value | Ref | Note |
|---|---|---|---|
| AffWild2 **test** V / A / avg | 0.457 / 0.375 / **0.416** | Table 8 | **Không** phải SOTA — thua Zhang ABAW3 [84] 0.520/0.601/**0.560**, hoà với Nguyen [83] 0.449 |
| AffWild2 **validation** CCC (fold tốt nhất) | V 0.596 / A 0.683 | Table 9 | 6-fold; chỉ fold tốt nhất; trung bình các fold ~ V 0.496 / A 0.649 |
| AFEW-VA V / A / avg (5-fold CC) | 0.654 / 0.617 / **0.635** | Table 7 | Vượt các baseline được trích dẫn; random split (rủi ro rò rỉ, xem bên dưới) |
| IEMOCAP acc / WA-F1 | **75.39 / 78.56** | Tables 6,10,11 | +10.51 F1 so với GraphMFT; split không được nêu rõ là speaker-disjoint |
| IEMOCAP unimodal visual / audio | 67.52 / 61.77 (acc) | Table 6 | **visual > audio**; concat 70.12, cross-attn 72.75 |
| CSSA ablation (full vs w/o) | V 0.457/0.375 vs 0.421/0.343 | Table 4 | +0.036 / +0.032 |
| HASPCM ablation (full vs w/o) | V 0.457/0.375 vs 0.432/0.348 | Table 5 | +2.5% / +2.7% |

Lưu ý: "AffWild2 CCC val 0.596 / aro 0.683" trong stub là **fold validation tốt nhất duy nhất** (Table 9),
không phải con số test; con số test trung thực là mức trung bình 0.457 / 0.375 (Table 8).

### Parts directly useful for ViEmoSpeech (tagged with Decision IDs)

1. **[V-A — verdict: REDUNDANT, one-sentence distinguish]** Fusion của HMATN là một sự xếp chồng gia tăng
   các khối attention đã có từ trước: co-attention (VQA 2016), self-attention (Transformer 2017), và
   image attention **ngữ nghĩa/không gian**. Nó trích dẫn joint cross-attention của Praveen (ref 63) như một
   *baseline mà nó cạnh tranh*, tức là nó là một "anh em" của template **RJCMA** ở bimodal-17 mà chúng ta
   đã trích xuất, chứ không phải một cơ chế mới. **Không có gì ở đây chuyển giao được cho một hệ thống
   audio↔text tiếng Việt mà RJCMA/BCAF/WavFusion/FAS chưa cho ta sẵn** — và hai khối được gắn nhãn "mới"
   (SEMAT/SPAAT, module CSSA) được định nghĩa trên **các vùng không gian thị giác** ("tập trung vào các
   vùng quan trọng về mặt thị giác," §3.5), thứ **không có tương đương trong văn bản**. Vậy nên nửa
   mang tính cốt lõi (load-bearing) của kiến trúc là không thể hoán đổi được đối với chúng ta. *Transfer
   risk: cao/fatal* — CSSA về bản chất là image-spatial; chỉ PCMA/CMRA là modality-agnostic và những cái
   đó là co-attention thuần đã có sẵn trong tay.
2. **[V-G — CCC loss corroboration]** Các đầu ra V/A dùng **L = 1 − rho_c** (Eq. 27), cùng mục tiêu CCC
   scale/shift-invariant mà bimodal-17 khuyến nghị. Đây là *phiếu bầu độc lập thứ hai từ AV* cho việc dùng
   CCC loss trên đầu ra valence/arousal của ViEmoSpeech, không phải một artifact mới. *Transfer risk: thấp*
   — CCC loss không phụ thuộc dataset; nhưng lưu ý nhãn của chúng ta là 1–5 rời rạc (Russell), nên cần ghép
   CCC với QWK/MAE như bimodal-17 đã quy định.
3. **[V-G — eval anti-pattern to name and avoid]** Paper trộn lẫn các protocol: AffWild2 dùng đúng
   **subject-independent** (tốt, khớp với ADR-002 speaker-disjoint của chúng ta), nhưng AFEW-VA là một
   **random split clip 400/200**, và split 5162/737/1481 của IEMOCAP **không bao giờ được nêu rõ là
   speaker/session-disjoint** — nên con số bắt mắt IEMOCAP 75.39/78.56 rơi vào cùng nhóm rò rỉ-lạm phát
   với vn-08 (86.6), vn-10 (0.87), và bimodal-11. *Transfer risk: đây chính xác là phong cách nhà của chúng ta
   rồi* — trích dẫn nó trong bảng eval-protocol như một ví dụ *mixed-rigor*: subject-independent ở chỗ dễ
   (AffWild2), random ở chỗ làm lạm phát kết quả (AFEW-VA/IEMOCAP).
4. **[V-B — backbone do-not-copy]** Toàn CNN/openSMILE/TextCNN, không SSL, không bộ mã hoá text họ BERT.
   Kết quả IEMOCAP cho thấy **visual (67.52) > audio (61.77)** theo unimodal, và câu nói "vấn đề cảm xúc
   phi trung tính … do sự phụ thuộc của hầu hết các mô hình AVER vào đặc trưng dựa-trên-văn-bản" (§4.4.5),
   mô tả một chế độ *visual-primary* mà **đảo ngược** hoàn toàn với chế độ audio-primary nhiễu-ASR của
   ViEmoSpeech. Thứ hạng backbone và kết luận về modality-dominance của họ không chuyển giao được.
   *Transfer risk: cao* — sai cặp modality (audio↔visual, không phải audio↔text) và sai họ bộ mã hoá.

### How each part helps ViEmoSpeech succeed

- **V-A (fusion):** Đóng lại hướng này. Trong đoạn related-work / fusion-candidates của method paper,
  trích dẫn HMATN như *"một chồng cross-attention audio-visual (CSSA+HASPCM) mà module nổi bật nhất là
  image-spatial và do đó không áp dụng được cho audio↔text; nửa chuyển giao được là co-attention, đã được
  bao phủ bởi RJCMA/BCAF."* Không cần chi thí nghiệm cho nó. Việc này **tiết kiệm** được một hàng
  fusion-ablation thay vì phải thêm vào.
- **V-G (CCC loss):** Giữ `affect_head` với `L = 1 − rho_c`; thêm HMATN và RJCMA cùng nhau làm hai
  trích dẫn AV cho CCC-loss trên hồi quy V/A. Báo cáo con số của chúng ta bằng CCC **+ QWK + MAE** trên
  thang rời rạc 1–5.
- **V-G (eval hygiene):** Thêm một hàng vào bảng so sánh eval-protocol:
  "HMATN 2025 — subject-independent trên AffWild2 nhưng **random-split** trên AFEW-VA/IEMOCAP → con số
  75.39 IEMOCAP không phải speaker-disjoint." Dùng nó để lý giải tại sao ViEmoSpeech báo cáo con số
  whole-series-holdout trung thực và gắn cờ các đối tượng so sánh bị rò rỉ.
- **V-A / robustness claim (negative lesson):** động lực *tuyên bố* của paper — fusion duy trì độ bền vững
  "ngay cả khi dữ liệu đầu vào bị nhiễu hoặc thiếu modality" (Abstract) — **không bao giờ được kiểm chứng**:
  không có bảng modality-dropout, không có sweep noise-injection, không có gì cả. Đây là lý do cụ thể
  giải thích tại sao cơ chế phòng ngừa modality-dropout / audio-anchoring của chúng ta (được yêu cầu bởi
  vn-12) phải là một **nhánh ablation thực sự**, không phải một tuyên bố trong văn xuôi. Nó cũng **đính chính**
  phần Analysis hiện có của file này, vốn ghi nhận độ bền vững với modality không-bổ-trợ như bài học thiết kế
  chuyển giao được — nhưng paper chỉ khẳng định điều đó mà không cung cấp thí nghiệm hỗ trợ nào.

### Child mental-health lens (ViEmoSpeech transfer validity)

- **Sai cặp modality.** Cơ chế cốt lõi của paper (CSSA/SEMAT/SPAAT) fusion **audio↔face-video**;
  ViEmoSpeech fusion **audio↔ASR-text**. "Spatial attention trên các vùng khuôn mặt quan trọng về mặt
  thị giác" không có tương đương trong text, nên khả năng chuyển giao kiến trúc gần như bằng không. Chỉ
  toán học co-attention chung (PCMA) là sống sót qua phép hoán đổi, và chúng ta đã có nó từ RJCMA/BCAF.
- **Không tone, không tiếng Việt, không phonation.** Các corpus là tiếng Anh/wild (AffWild2, AFEW-VA) và
  tiếng Anh acted (IEMOCAP); "audio" là spectrogram+MFCC. Không có gì liên quan đến thanh điệu từ vựng hay
  cuộc cạnh tranh kênh F0/phonation vốn là điểm mới V-D của ViEmoSpeech — nên nó không ảnh hưởng gì đến
  tuyên bố của chúng ta (nhất quán với phát hiện 0/20-papers).
- **Điểm mù No-ASR, một lần nữa.** Text của IEMOCAP là **transcript vàng** qua TextCNN; không có giai đoạn
  ASR và không có ablation về nhiễu-ASR ở đâu cả. Mọi paper fusion trong bộ này đều chia sẻ điểm mù này;
  HMATN là thêm một điểm dữ liệu nữa cho thấy ablation về độ bền vững tone-swap-ASR khi arousal cao
  (mày→máy) của chúng ta thực sự là lãnh thổ chưa ai khai phá.
- **Ethics / framing.** §5 gợi ý "giám sát sức khoẻ tâm thần … phát hiện trạng thái cảm xúc để đánh giá
  stress, lo âu, và trầm cảm" như một ứng dụng downstream — cùng anti-pattern overclaim lâm sàng trên
  affect-diễn (acted) mà chúng ta đã gắn cờ cho vn-10/EAA. Paper huấn luyện trên affect phim/YouTube mà
  không có mỏ neo lâm sàng nào; trích dẫn như thêm một ví dụ what-not-to-do cho framing honest-proxy của
  distress-head (V-F).

### Limitations & open questions for ViEmoSpeech (incl. contradiction/gap)

- **Contradiction #1 (claim vs evidence, load-bearing):** abstract và §5 quảng bá độ bền vững "ngay cả
  khi dữ liệu đầu vào bị nhiễu hoặc thiếu modality," nhưng paper **không chạy thí nghiệm missing-modality
  và không có noise-injection nào** — các ablation (Tables 4–6) chỉ thêm/bớt các khối attention *của
  chính nó* với tất cả modality đều hiện diện. Điểm bán hàng về robustness không có căn cứ. (Điều này
  trực tiếp đính chính phần Analysis hiện có của file này, vốn coi tuyên bố đó là "bài học thiết kế"
  chuyển giao được.)
- **Contradiction #2 (vs bimodal-17 RJCMA and vs its own "SOTA" claim):** HMATN tuyên bố "vượt qua
  state-of-the-art," nhưng trên **tập test AffWild2**, trung bình của nó (0.416, Table 8) **thua** Zhang
  ABAW3 [84] (0.560) và chỉ nhỉnh hơn chút ít so với chính baseline joint-cross-attention kiểu-RJCMA mà
  nó trích dẫn (Praveen [63] 0.369). "SOTA" chỉ đúng cho CCC fold-validation so với các biến thể
  *unimodal*. RJCMA (bimodal-17) vẫn là template AV CCC-loss được benchmark trung thực hơn, sạch hơn.
- **Gap #3 (leaky eval):** Con số 75.39/78.56 của IEMOCAP và các con số random-split của AFEW-VA không
  phải speaker/session-disjoint — không so sánh được với thanh whole-series-holdout của ViEmoSpeech; chỉ
  dùng được như các đối tượng so sánh rò rỉ đã gắn cờ, tương tự vn-08 / vn-10 / bimodal-11.
- **Editorial-rigor flag:** cùng một từ viết tắt được diễn giải theo ba cách khác nhau — HMATN là "Hybrid
  Multi-ATtention Network" (Abstract) so với "Hierarchical Multimodal Attention-based Transformer Network"
  (§4.4.3); HASPCM là "…of Single and Parallel Cross-Modal" (Abstract) so với "Hybrid Attention-based
  Spatial-Pyramid Cross-Modal" (§4.3); PCMA là "Parallel" so với "pyramid" cross-modal attention. Nhất
  quán với venue tier thấp; coi tất cả các con số cụ thể là single-source (version-of-record, không có
  khả năng đối chiếu số liệu độc lập nào khả thi).
- **Open question (none blocking):** repo GitHub (commit `b2c9e03`) được nêu tên nhưng chưa được kiểm tra;
  do V-A đã bị đánh giá là dư thừa nên không có lý do để bỏ công tải dataset/code từ đó.
