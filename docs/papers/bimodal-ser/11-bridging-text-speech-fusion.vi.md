# Paper 11 — Bridging Text and Speech for Emotion Understanding: Explainable Multimodal Transformer Fusion with Unified Audio–Text Attribution

> Bản dịch tiếng Việt của [11-bridging-text-speech-fusion.md](11-bridging-text-speech-fusion.md) — cập nhật 2026-07-10.

- **Authors:** Ashutosh Pandey, Jasmeet Singh, Maninder Kaur
- **Venue / year:** Journal of Intelligence (MDPI), 13(12):159, 2025 (CC-BY; mirror PMC12733550)
- **Links:** abs https://www.mdpi.com/2079-3200/13/12/159 · PDF `pdfs/11-bridging-text-speech-fusion.pdf`
- **Group:** survey / benchmark (fusion framework)

**Summary:** RoBERTa (text) + WavLM (audio) chiếu vào latent space chung; attribution Integrated-Gradients/Occlusion tách phần đóng góp linguistic vs acoustic.

**Relevance to Pebble:** Kiến trúc audio+text fusion cụ thể + phương pháp explainability chuyển được sang voice-mode. Venue tier thấp hơn IEEE/Interspeech — rank vì topical fit.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Profile assembled at analysis time** (from `docs/intent/constraints.md` + `docs/spec/capabilities/voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`):
Pebble = một chương trình chính về **ordinal suicide-risk text** (BERT-family encoder, teacher-LLM silver labels, strict gold-holdout + subject-level splits, ordinal-aware QWK/MAE) **cộng thêm** một luồng **voice** đang hoạt động song song: backbone WavLM-Large / emotion2vec đóng băng (frozen) với **ba MTL heads dị chất** — emotion (CE), affect (valence+arousal, CCC loss), crisis (BCE dưới một **sàn recall cứng ≥0.90**) — được cân bằng bởi **Kendall uncertainty weighting**; fusion voice+text là hướng đi tiếp theo đã được nêu tên. Paper này là một bộ phân loại emotion **single-head, end-to-end late-fusion** (RoBERTa-base + WavLM-Base-Plus) trên MELD, 5 lớp, kèm attribution XAI hậu-kiểm (post-hoc).

**Per-dimension scores (before the number):**
- **D1** (multi-task heterogeneous heads; w=3) = **0** — chỉ một classification head trên 5 nhóm cảm xúc; không có regression head liên tục, không có safety head, hoàn toàn không có MTL.
- **D2** (mental-health / crisis domain; w=2) = **0** — cảm xúc hội thoại tổng quát (MELD / phim "Friends"); sức khỏe tâm thần chỉ là khung diễn ngôn tu từ trong phần mở đầu.
- **D3** (emotion-transfer corpora; w=1) = **1** — MELD là một corpus cảm xúc phân loại có thể dùng cho emotion head của Pebble, dù không nằm trong danh sách GoEmotions/EmpatheticDialogues/intensity đã liệt kê.
- **D4** (teacher-LLM silver-label distillation; w=2) = **0** — chỉ dùng nhãn do người gán cho MELD; không có distillation.
- **D5** (principled MTL loss balancing; w=2) = **0** — cross-entropy thuần, một mục tiêu duy nhất; không có uncertainty/GradNorm/PCGrad.
- **D6** (safety/crisis recall constraint as objective; w=2) = **0** — recall theo từng lớp có được báo cáo, nhưng không có ràng buộc sàn recall dẫn dắt việc huấn luyện/ngưỡng hóa.
- **D7** (encoder backbone match; w=1) = **2** — WavLM-Base-Plus **và** RoBERTa-base khớp trực tiếp với dòng backbone của cả hai luồng của Pebble.

**Overlap:** `(3·0 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·2) / 26 × 100 = 3/26 × 100` = **12%** — **peripheral (<40%)**.

- **Closest on:** D7 (khớp chính xác backbone WavLM+RoBERTa) và, yếu hơn, D3 (MELD như một corpus cảm xúc).
- **Best point (Method to adopt):** **attribution thống nhất theo từng modality** — Integrated Gradients trên token văn bản + Occlusion trên các cửa sổ âm thanh cố định — phân rã một dự đoán duy nhất thành bằng chứng linguistic vs acoustic-prosodic.
  - **How to apply to Pebble:** bọc cùng một pass IG(text)+Occlusion(audio) quanh crisis head để mỗi cờ báo được nâng lên dưới sàn recall cứng đều mang theo attribution "được thúc đẩy bởi ngữ điệu (prosody) hay bởi nội dung từ vựng" — lớp khả kiểm chứng lâm sàng (clinical-auditability) mà một con số recall trần trụi không thể cung cấp, và cũng là điều duy nhất ở đây mà một công thức fusion tổng quát chưa sẵn có cho ta.
- **Caveats:** open-access, đã đọc toàn văn (không có phần nào bị paywall). Các điểm làm giảm độ tin cậy là do mismatch, không phải do khoảng trống chưa đọc: (1) fine-tuned **end-to-end**, ngược với hướng frozen-backbone probe của Pebble; (2) MELD dùng split chuẩn với **không có bảo đảm speaker/subject-disjoint**, điều này sẽ vi phạm ràng buộc toàn vẹn subject-level của Pebble nếu tái sử dụng nguyên trạng; (3) sức mạnh thống kê còn mỏng (Wilcoxon p=0.125, 3 seeds); (4) accuracy 83% trên MELD là con số within-distribution, không phải kết quả gold-holdout. Công thức fusion (project 768→256, concat→512, dropout 0.3, 2-layer head; ablation: bottleneck 128-d > 256 > 512) là một bản thiết kế phụ khả dụng khi Pebble tiến tới hướng fusion.

## Deep research — full-PDF read (2026-07-10)

> Được phân tích dựa trên **hồ sơ ViEmoSpeech hiện hành + Decision Register V-A…V-H**
> (`docs/tasks/paper-deep-analysis.md`), KHÔNG phải hồ sơ luồng-text đã lưu trữ / D-A…D-H mà
> phần "Analysis" ở trên sử dụng. Đây là **kiến trúc gần nhất với kế hoạch PhoBERT+WavLM của
> chúng ta** trong toàn bộ related-work set — một text encoder họ BERT + audio encoder WavLM được
> fuse cho phân loại cảm xúc theo hạng mục — nên phần đọc này tập trung vào cơ chế fusion chính
> xác, câu hỏi frozen-vs-fine-tuned, các con số đóng góp theo từng modality (bằng chứng về mức
> áp đảo text-vs-audio), và phương pháp attribution như một công cụ ứng viên cho biểu đồ cạnh
> tranh kênh (channel-competition) tone×emotion của chúng ta.

### Source-access note

Đọc từ file PDF cục bộ `docs/papers/bimodal-ser/pdfs/11-bridging-text-speech-fusion.pdf` qua
`pdftotext` (toàn bộ thân bài 24 trang, cả 4 bảng, 3 algorithm listing, Eqs 1–6). PDF cục bộ **chính
là phiên bản đã xuất bản của venue** — MDPI *Journal of Intelligence* 13(12):159, DOI
10.3390/jintelligence13120159, xuất bản 3 Dec 2025, CC-BY (chân trang `J. Intell. 2025, 13, 159`,
nhận 15 Sep / chấp nhận 28 Nov 2025), nên không có chênh lệch preprint-vs-published cần đối chiếu.
Xác minh trên web:
- Bản ghi xuất bản + các con số headline được xác nhận qua WebSearch (`Pandey Singh Kaur "Bridging Text
  and Speech" Journal of Intelligence 2025 …`) → tìm ra DOI https://doi.org/10.3390/jintelligence13120159
  và bản mirror PMC https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12733550/ (accuracy 0.83 / 5 lớp /
  RoBERTa+WavLM / IG+Occlusion — tất cả khớp với PDF cục bộ). Trang HTML của MDPI trả về HTTP 403
  cho công cụ fetch (bot protection), nên các sự kiện headline được đối chiếu qua các bản ghi PMC/DOI +
  PDF phiên bản venue. **✔**
- Baseline so sánh **TelME** ở Table-4 của họ: được kiểm tra độc lập (WebSearch
  `TelME MELD emotion recognition weighted F1 …` → WebFetch https://arxiv.org/html/2401.12987v2).
  Kết quả MELD thực tế của TelME là **weighted-F1 67.37 trên tập 7-lớp đầy đủ**, và **metric headline
  của nó là weighted-F1, không phải accuracy**. Điều này xác nhận rằng dòng "TelME 67.4%" của paper
  này đang được so sánh với **accuracy 5-lớp 83%** của mô hình đề xuất — một sự lệch pha
  metric-và-số-lớp (xem Limitations). **✔**

### What the paper actually does

**Task / data.** Phân loại cảm xúc theo hạng mục 5 lớp, single-head, trên **MELD** (hội thoại tự
phát từ sitcom *Friends*). MELD vốn có 7 loại cảm xúc; các tác giả **bỏ `disgust` và `fear`**
(quá ít mẫu, độ đồng thuận liên-người-gán-nhãn thấp), giữ lại **Anger, Joy, Neutral, Sadness, Surprise**
(§3.1, §3.4). Pipeline âm thanh (§3.2, Alg. 1): trích WAV 48 kHz từ video, khử nhiễu neural
**DeepFilterNet v2** (trọng số mặc định, FFT 512 / hop 128), hạ mẫu xuống 16 kHz, chuẩn hóa
mean–variance theo từng utterance, pad/truncate về cố định **8 giây (128,000 samples)**. Text:
loại bỏ ký tự phi chữ-số, `RobertaTokenizerFast`, cố định **64 token**.

**Backbones (§4.1).** Audio = **WavLM-Base-Plus** (front-end 7-conv, kernel [10,3,3,3,3,2,2] /
stride [5,2,2,2,2,2,2]; 12 lớp transformer, 12 head × 64-d; FFN 768→3072→768; pre-LN) →
embedding speech **768-d**. Text = **RoBERTa-base** (byte-level BPE ~50k vocab; 12 lớp/12 head;
FFN 768→3072→768; post-LN) → embedding **[CLS] 768-d**. *Cách chuỗi frame của WavLM được pool
thành một vector 768-d duy nhất không hề được nêu rõ* (khoảng trống).

**Fusion (§4.2–4.4, cơ chế cốt lõi, Eqs 1–4).** Concat ở mức late/feature-level:
1. Chiếu mỗi modality vào một subspace chung: `a' = W_a·a + b_a`, `t' = W_t·t + b_t`, với
   `W_a, W_t ∈ ℝ^{256×768}` → mỗi modality về **256-d** (Eq 1).
2. **Concatenate**: `m = [a'; t'] ∈ ℝ^{512}` (Eq 2), sau đó **dropout p=0.3**.
3. MLP head 2 lớp: `h1 = ReLU(W1·m + b1)`, `W1 ∈ ℝ^{256×512}` (Eq 3); `ŷ = W2·h1 + b2`,
   `W2 ∈ ℝ^{C×256}` (Eq 4) → softmax.
**Không có cross-attention, không có gating, không có căn chỉnh dựa trên query** — đây là kiểu
fusion học được *đơn giản nhất có thể* (project → concat → MLP), tức baseline "Concat" mà các
thiết kế mạnh hơn sẽ vượt qua.

**Training (§4.6).** **Fine-tuned end-to-end, KHÔNG đóng băng lớp nào.** AdamW, lr **2e-5**,
weight decay **0.01**, batch **8**/GPU, warm-up tuyến tính trong **10%** bước đầu, dropout **0.3**,
grad-clip norm **1.0**, CrossEntropy, tối đa **15 epoch**, early-stop patience **2** trên val loss
(hội tụ tại epoch 4: train acc 55→87%, val 70→83%, §5.4), **3 seed (42, 123, 2025)** được báo cáo
dưới dạng mean±std. Stack: transformers **4.41.0**, PyTorch 2.2.0, dual Tesla T4 16 GB.

**Explainability (§4.5, §5.5–5.8, Alg. 3).** **Integrated Gradients** (Sundararajan 2017;
steps=10) áp dụng lên **cả** token văn bản lẫn waveform âm thanh; **Occlusion** trên âm thanh với
cửa sổ `w = 0.1·fs = 1600 samples (0.1 s)`, stride `s = w/2 = 800`, nội suy về lại độ dài gốc.
IG(text) làm nổi bật các từ mang sắc thái tình cảm ("great", "play", "song") và làm mờ các từ chức
năng; IG/Occlusion(audio) định vị các vùng ngữ điệu (prosodic) theo từng lớp (Surprise = bùng nổ
sớm/tập trung đầu; Sadness = lan tỏa, kéo dài; Anger = đỉnh sớm + đỉnh muộn). §5.8 báo cáo rằng
IG và Occlusion **đồng thuận** trên các vùng có giọng (voiced)/hài âm (harmonic).

**Results.** Accuracy multimodal **0.83 ± 0.01, macro-F1 0.82 ± 0.01** (5 lớp, Table 2). F1
theo từng lớp: **Sadness 0.90, Anger 0.85, Surprise 0.85, Joy 0.77, Neutral 0.74** (Table 2). AUC
one-vs-rest theo từng lớp: Anger 0.9389, Joy 0.9089, Neutral 0.9019, **Sadness 0.9623**,
Surprise 0.9546 (§5.2). Unimodal vs multimodal (Table 3): **RoBERTa text-only 0.79 / macro-F1
0.78** (vượt BERT 0.75, DistilBERT 0.76); **WavLM audio-only 0.65 / 0.61** (vượt Wav2Vec2
0.60 / 0.57); multimodal **0.83 / 0.82** — mức **tăng +4–5% so với unimodal tốt nhất (text)**.
Ý nghĩa thống kê qua 3 seed: **Wilcoxon W=6.00, p=0.125; Sign test p=0.25** — *cả hai đều không
có ý nghĩa thống kê ở mức α=0.05* (§5.2). Ablation (§4.7): bottleneck **128 → ~82%**, **512 →
~77%**, 256 là "cân bằng tốt nhất"; **bỏ bước khử nhiễu DeepFilterNet làm giảm accuracy**. Bảng
SOTA (Table 4): Proposed 83.0 so với Bi-LG-GCN 80.1 so với TelME 67.4 (xem Limitations — có sự
lệch pha metric/số-lớp).

### Parts directly useful for ViEmoSpeech (tagged by Decision ID)

1. **[V-A] Fusion concat-projection-MLP chính xác (Eqs 1–4) = nhánh baseline learned-fusion đơn
   giản nhất của chúng ta.** Chiếu WavLM-768 và PhoBERT-768 mỗi cái về một d chung (họ dùng 256;
   ablation nói bottleneck **nhỏ hơn** 128 lại tốt hơn), concat → dropout 0.3 → MLP ReLU 2 lớp →
   softmax. Đây là phương án học thay thế tối thiểu cho rule-fusion đã rút lại trước đó (vn-09) và
   là *sàn dưới* so với cross-attention (bimodal-03) / gated (WavFusion) / Q-Former (vn-07 FAS).
   **Trạng thái các con số: ✔** (Table 2/3, phiên bản venue).
2. **[V-C] Cấu hình RoBERTa-base như analogue trực tiếp của PhoBERT.** Trần 64 token, pooling
   [CLS], chiếu tuyến tính vào subspace chung, lr 2e-5, wd 0.01, warm-up 10%. RoBERTa text-only
   **0.79/0.78** ở đây là trần (ceiling) văn bản sạch (clean-transcript) của nhánh text
   (Table 3, **✔**).
3. **[V-A / V-B] Fine-tuned end-to-end, không lớp nào bị đóng băng** (§4.6) — con số 0.83 của họ
   là một trần *fully-fine-tuned*, không phải mức sàn frozen-probe. Đây là điểm đối trọng với
   thiên hướng V-B của chúng ta nghiêng về WavLM **đóng băng**; điều này có nghĩa là audio-only
   0.65 của họ là một ước lượng *cận trên* cho năng lực độc lập của WavLM, và một WavLM đóng băng
   trong stack của chúng ta sẽ nằm dưới mức đó. **✔** (§4.6).
4. **[V-G] Attribution thống nhất theo từng modality: IG(token văn bản) + Occlusion(cửa sổ
   audio)** (§4.5, Alg. 3) như một công cụ ứng viên để giải thích xung đột tone×emotion, cùng với
   **cách báo cáo**: mean±std trên 3 seed, AUC one-vs-rest theo từng lớp, và các kiểm định ý nghĩa
   phi tham số. **✔** (§5.2, §5.5–5.8).
5. **[V-B] Việc tăng cường (enhancement) bằng DeepFilterNet-v2 trước SSL encoder có tác dụng đo
   được** (ablation, §4.7). **≈ xấp xỉ** (được báo cáo là "suy giảm nhất quán" khi bỏ đi, không có
   con số tách riêng).

### How each part helps ViEmoSpeech succeed

- **Bậc thang baseline V-A (→ bảng fusion của method paper).** Thêm concat-projection-MLP này như
  **dòng "fusion học đơn giản nhất"** ngay phía trên dòng rule-fusion tái triển khai của vn-09 và
  phía dưới các ứng viên cross-attention / gated / kiểu-FAS của chúng ta. Cấu hình cụ thể để sao
  chép: chiếu cả hai luồng 768-d về một **dim chung nhỏ (128, theo ablation của họ, không phải
  256/512), dropout 0.3, MLP ReLU 2 lớp**. *Rủi ro chuyển giao (đã nêu):* mức tăng **+4–5%
  multimodal-so-với-text của họ được đo trên transcript gold tiếng Anh SẠCH** nơi text đã đạt
  0.79; dưới **PhoWhisper ASR tiếng Việt với lỗi tone-swap ở mức arousal cao**, nhánh text bị suy
  giảm, nên *đóng góp của audio trong chế độ của chúng ta phải lớn hơn* và mức +4–5% chính xác này
  sẽ không chuyển giao được. Họ cũng **fine-tune end-to-end**; nếu ta đóng băng WavLM (V-B),
  baseline concat có thể kém hơn — nên hãy chạy **cả hai nhánh WavLM đóng băng và fine-tuned** của
  baseline concat, đừng kế thừa nguyên con số của họ.
- **Cấu hình nhánh PhoBERT V-C.** Tái sử dụng công thức 64-token / [CLS] / lr 2e-5 làm mặc định
  cho nhánh PhoBERT. *Rủi ro chuyển giao:* kết quả của họ là bằng chứng mạnh nhất cho thấy **một
  text encoder mạnh áp đảo trên transcript sạch** — và cũng là lý do mạnh nhất để **không** giả
  định PhoBERT sẽ áp đảo trên transcript ASR của chúng ta. Cho nhánh này ăn **văn bản ASR** (chứ
  không phải caption gold) ở nhánh chính, và giữ một nhánh caption gold như cận trên transcript
  sạch, để hình phạt nhiễu-ASR lên nhánh text được đo, chứ không phải giả định (V-C chính xác là
  câu hỏi về độ bền vững này).
- **Công cụ attribution + đánh giá V-G.** Chuyển giao **Occlusion trên các cửa sổ âm thanh đã
  align** như một lăng kính cho biểu đồ cạnh tranh kênh (channel-competition) tone×emotion: occlude
  phần vần (rime) của một âm tiết và đọc sự thay đổi của logit cảm xúc, kết hợp với IG trên token
  PhoBERT tương ứng. Áp dụng cách báo cáo **mean±std trên 3 seed + AUC one-vs-rest theo từng lớp**
  của họ (nâng cấp lên ≥5 seed theo THAI-SER vn-11). *Rủi ro chuyển giao:* cửa sổ occlusion của họ
  là **0.1 s / stride 800-sample cố định, không align với âm vị** — quá thô để tách một tone âm
  tiết khỏi cảm xúc của nó; ta phải **align cửa sổ với ranh giới âm tiết của PhoWhisper**, và theo
  đúng lưu ý ở §5.8 của chính họ rằng sự đồng thuận attribution "có thể phản ánh các tương quan phụ
  thuộc-cảm-xúc giữa nội dung văn bản và âm thanh chứ không phải sự tích hợp xuyên-modal tường
  minh," **không bao giờ trình bày bức tranh attribution như bằng chứng cho sự cạnh tranh kênh** —
  phải kết hợp nó với một chỉ số định lượng (vn-13 Cramér's V trên tone-vs-emotion, vn-06 probe
  Ridge theo từng lớp). Attribution trực quan là minh họa, không phải phép đo.
- **Bước enhancement V-B.** Ablation khử nhiễu-trước-SSL của họ ủng hộ việc giữ một **giai đoạn
  enhancement trước WavLM**. *Rủi ro chuyển giao:* DeepFilterNet của họ *loại bỏ* nhiễu khỏi âm
  thanh sitcom sạch; giai đoạn Demucs của chúng ta *tách nguồn* để **khôi phục** một nền nhạc/nhiễu
  mà chúng ta cố tình giữ lại — mục tiêu khác nhau, nên chỉ coi "enhancement có ích" như hỗ trợ
  định hướng, và A/B đầu ra Demucs của ta so với âm thanh thô.

### Child mental-health / ViEmoSpeech transfer lens

Đây là **cặp backbone của chúng ta** (WavLM + một text encoder họ BERT), nên tính hợp lệ chuyển
giao cao bất thường về mặt kiến trúc và thấp bất thường về mặt chế độ (regime). Điều gì chuyển
giao được và điều gì không:

- **Khớp về thể loại (register), lệch về ngôn ngữ.** MELD là **hội thoại kịch bản trên TV
  (acted TV-show dialogue)** — cùng thể loại kịch acted-drama như corpus phim truyền hình Việt Nam
  của chúng ta, đây là tiền lệ thực sự hữu ích (hội thoại được tìm thấy/kịch bản hóa, tự phát
  trong phạm vi cảnh). Nhưng nó là **tiếng Anh và phi thanh điệu (non-tonal)**, nên paper này
  **không nói gì** về sự cạnh tranh kênh tone×emotion F0/phonation vốn là tuyên bố đầu bảng của
  chúng ta (V-D vẫn chưa được chạm tới — cộng vào bảng kiểm đang chạy: vẫn **0 trên 16 paper** đo
  sự cạnh tranh kênh lexical-tone×emotion).
- **Con số áp đảo của text mang tính đặc thù theo chế độ và không được suy diễn quá mức.**
  RoBERTa-alone **0.79** ≈ multimodal **0.83**, audio-alone **0.65** — trên **transcript gold
  sạch**, text gánh phần lớn nhiệm vụ và audio thêm vào ~4 điểm. Đây là **cực đối lập** so với
  "text gần như vô dụng" (38–44%) của vn-08 trên ASR tự phát tiếng Việt. ViEmoSpeech nằm ở giữa hai
  cực: PhoWhisper ASR sạch hơn setup của vn-08 nhưng bị tone-corrupted ở mức arousal cao, và tiếng
  Việt có thanh điệu nên nhánh audio phải mang *nhiều hơn* so với +4 điểm của MELD. ⇒ method paper
  của chúng ta phải đóng khung đóng góp của audio là **phụ thuộc chế độ và được đo theo từng thể
  loại**, dẫn paper này như mỏ neo cho tiếng Anh sạch — chứ không phải như bằng chứng chung chung
  "multimodal > unimodal".
- **Fine-tuned, không đóng băng, và không speaker-disjoint.** Hai xung đột bất biến đối với chúng
  ta: (a) họ fine-tune cả hai encoder end-to-end (V-B của chúng ta nghiêng về WavLM đóng băng), và
  (b) đánh giá của họ **không speaker-disjoint** (split chuẩn của MELD không hề như vậy, và
  `RandomSplit(0.8/0.2)` của Alg. 2 chắc chắn cũng không) — điều này sẽ vi phạm bất biến
  speaker-disjoint / whole-series-holdout của chúng ta (ADR-002) nếu tái sử dụng nguyên trạng.
  Con số 0.83 của họ là within-distribution, không speaker-disjoint; mỏ neo speaker-disjoint trung
  thực của chúng ta sẽ thấp hơn (so với THAI-SER WA ~60, MSP naturalistic macro-F1 ~0.30).
- **Không có đầu ra dimensional / distress.** Chỉ thuần phân loại 5 lớp; không có valence/arousal-
  CCC, không có distress head — không dịch chuyển gì cho V-D (dimensional) hay V-F (distress).
  Khung diễn ngôn lâm sàng chỉ là một câu trong kết luận ("các nền tảng sức khỏe tâm thần có thể hỗ
  trợ nhận thức cảm xúc bản thân"), không có nhãn lâm sàng nào — cùng mẫu hình
  acted-categorical-emotion-with-clinical-veneer mà V-F gọi tên như một anti-pattern.
- **Việc bỏ các lớp hiếm khó là một bài học phản-ví-dụ, không phải bài học nên theo.** Họ bỏ
  `fear` và `disgust` vì N thấp / độ đồng thuận thấp — trực tiếp ngược lại với **sàn tối thiểu
  ≥50-clip cho lớp hiếm** (ADR-002) của chúng ta. Thiết kế của chúng ta giữ lại các lớp hiếm với
  một sàn tối thiểu và báo cáo trung thực theo từng lớp thay vì xóa chúng để thổi phồng accuracy.

### Limitations & open questions for ViEmoSpeech (incl. explicit contradiction/gap)

- **MÂU THUẪN với vn-08 và tổng hợp xuyên-suốt (text-vs-audio dominance).** Sự áp đảo của text
  sạch trong paper này (RoBERTa 0.79 ≈ multimodal 0.83; audio 0.65) là **đối lập trực tiếp** với
  "text gần như vô dụng" (38–44% VN ASR) của vn-08 và xác nhận điểm tổng hợp xuyên-suốt #1: **sự
  áp đảo phụ thuộc thể loại/ngôn ngữ, chưa phải điều đã được xác định.** Nó neo vào cực
  *clean-transcript, phi-thanh-điệu, fine-tuned*. Hệ quả mang tính quyết định: hook của
  ViEmoSpeech không thể dẫn "multimodal thắng unimodal" một cách chung chung — độ lớn đóng góp của
  audio chính là điều chế độ tonal/ASR-nhiễu của chúng ta thay đổi, và là điều chúng ta phải *đo
  lường*.
- **KHOẢNG TRỐNG / sự không nhất quán nội bộ — tập đánh giá không được định nghĩa rõ ràng, nên
  metric headline không thể so sánh được.** §3.1 nêu **split MELD chuẩn** (train 10,000 / val
  1109 / **test 1353**) và audio **WavLM-Base-Plus**, nhưng **Algorithm 2** thực tế lại làm
  `RandomSplit(D, [0.8, 0.2])` thành chỉ **train/val** (không có tập test giữ riêng) và khởi tạo
  một **`Wav2Vec2Processor("wav2vec2-base-960h")`**, không phải WavLM. Tệ hơn, số lượng true-
  positive trong confusion matrix (§5.3: Sadness **898** + Surprise 837 + Anger 753 + Joy 746 =
  **3,234** chỉ trên bốn lớp) **vượt quá bất kỳ split 20% khả dĩ nào** của tập 5-lớp ~12,462-
  utterance (~2,500) và cao hơn nhiều so với tập test chuẩn 1,353-utterance — vậy nên con số 0.83
  được báo cáo **không thể ánh xạ về phân vùng test chuẩn của MELD**. Điều này khiến **so sánh SOTA
  ở Table 4 không hợp lệ**: accuracy 5-lớp trên một split được định nghĩa thiếu và không
  speaker-disjoint so với **weighted-F1 7-lớp 67.37 của TelME** (đã được xác nhận ✔) và con số của
  Bi-LG-GCN — khác metric, khác số lớp, khác split. ⇒ ViEmoSpeech trích dẫn điều này như một
  **ví dụ về điều-không-nên-làm khi báo cáo**: đây chính xác là lý do giao thức của chúng ta cố
  định các split speaker-disjoint (ADR-002), báo cáo macro-F1 (không phải accuracy) trên một tập
  mất cân bằng lớp, và không bao giờ so sánh giữa các metric lệch pha nhau.
- **Sức mạnh thống kê không tồn tại, chứ không chỉ mỏng.** Wilcoxon **p=0.125** và Sign-test
  **p=0.25** đều **không có ý nghĩa thống kê ở mức α=0.05**, vậy mà văn bản lại đọc chúng như là
  "vượt trội một cách nhất quán." 3 seed không đủ để hỗ trợ một tuyên bố về ý nghĩa thống kê —
  eval của chúng ta phải dùng ≥5 seed (vn-11) và báo cáo CI một cách trung thực.
- **Frozen-vs-fine-tuned chưa được trả lời cho chế độ của chúng ta.** Họ chỉ chạy fully-fine-tuned;
  **không có nhánh frozen-encoder**, nên paper này không cho bằng chứng nào về việc liệu một WavLM
  đóng băng (V-B) có đủ hay không — một A/B mở mà chúng ta phải tự chạy.
- **Attribution ≠ integration (lưu ý của chính họ).** §5.8 thừa nhận rằng sự đồng thuận IG/Occlusion
  giữa các modality "có thể phản ánh các tương quan phụ thuộc-cảm-xúc giữa nội dung văn bản và âm
  thanh chứ không phải sự tích hợp xuyên-modal tường minh." Với V-G đây là một lời cảnh báo trực
  tiếp: một biểu đồ attribution đơn thuần không thể chứng minh tuyên bố cạnh tranh kênh tone×emotion;
  nó phải được hậu thuẫn bởi một phép đo định lượng, dựa trên probe (vn-06 Ridge probe, vn-13
  tương tác thống kê / Cramér's V).
- **Pooling của WavLM không được nêu rõ** — cách chuỗi frame được rút gọn thành một vector 768-d
  duy nhất (mean-pool? CLS? attention-pool?) không hề được nêu; nếu chúng ta sao chép công thức
  này, ta phải chọn và báo cáo rõ (mean-pool ở lớp giữa theo vn-06 cho độ nhạy với tone).
