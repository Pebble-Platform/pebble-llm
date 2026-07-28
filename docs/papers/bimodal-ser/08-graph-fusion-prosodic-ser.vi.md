# Paper 08 — Enhancing SER with Graph-Based Multimodal Fusion and Prosodic Features

> Bản dịch tiếng Việt của [08-graph-fusion-prosodic-ser.md](08-graph-fusion-prosodic-ser.md) — cập nhật 2026-07-10.

- **Authors:** Alef Iury Ferreira, Lucas Rafael Gris, Alexandre Ferro Filho, Lucas Ólives, Daniel Ribeiro, Luiz Fernando, Fernanda Lustosa, Rodrigo Tanaka, Frederico Oliveira, Arlindo Galvão Filho (Federal University of Goiás, Brazil, et al.)
- **Venue / year:** Interspeech 2025 SER-Naturalistic-Conditions Challenge system, arXiv 2025
- **Links:** abs https://arxiv.org/abs/2506.02088 · PDF `pdfs/08-graph-fusion-prosodic-ser.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Fusion đa encoder — Wav2Vec2/HuBERT/WavLM/Whisper/XEUS + RoBERTa — qua graph attention networks, kèm prosodic features.

**Relevance to Pebble:** Trả lời trực tiếp câu "chọn SSL audio encoder nào + text encoder nào + fuse ra sao".

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Pebble profile used (assembled at analysis time):** Primary = ordinal suicide-risk **text** classification, LLM/weak silver labels augmenting a scarce clinical gold set under **gold-holdout**, ordinal-aware, BERT-family encoder. Adjacent **voice** stream = heterogeneous MTL trên **frozen WavLM-Large / emotion2vec** backbone — 3 heads (emotion CE, affect V/A qua **CCC**, crisis dưới **hard recall floor**) được cân bằng bởi **Kendall uncertainty weighting**; bước tiếp theo được nêu tên = thay proxy labels bằng **MSP-Podcast** (A/V/D) + DAIC. Fusion voice+text là hướng đi tiếp theo.

### Analysis — Graph-Fusion + Prosodic SER (Interspeech 2025 challenge)
- **Overlap:** 12% (ngoại vi) — D1=0, D2=0, D3=1, D4=0, D5=0, D6=0, D7=2
  - D1=0 single-task categorical emotion (không có các head continuous/safety không đồng nhất); D2=0 podcast affect, không phải crisis; D3=1 là emotion corpus và đó chính là **MSP-Podcast**, mục tiêu real-label tiếp theo được nêu tên của voice task; D4=0 CED audio-tag distillation + vote ensemble, không phải teacher-LLM silver labels; D5=0 inverse-freq weighted CE, không có principled MTL balancing; D6=0 Recall được báo cáo nhưng không có recall-floor objective; D7=2 khớp trực tiếp về backbone (WavLM/Wav2Vec2/HuBERT/Whisper/XEUS + RoBERTa-Large).
  - **Closest on:** D7 (họ SSL audio + text encoder, giống hệt voice stream) và D3 (MSP-Podcast, đúng corpus của bước tiếp theo).
  - **Best point (Design lesson):** Cuộc so tài frozen-feature SSL backbone của họ trên MSP-Podcast tự nhiên (naturalistic) xếp hạng **Whisper Large V3 (Macro F1 0.366) > XEUS 0.323 > WavLM-Large 0.313 > HuBERT 0.274 > Wav2Vec2 0.178** — trên spontaneous emotional speech, các đặc trưng Whisper/XEUS được huấn luyện trước theo ASR vượt qua WavLM/Wav2Vec2, và simple concat fusion (0.388) gần như bằng graph fusion / MDAT phức tạp (0.401) ở quy mô dữ liệu này.
  - **How to apply to Pebble:** khi task voice-mtl-heads thay proxy RAVDESS bằng MSP-Podcast thật, hãy thêm **Whisper Large V3 và XEUS** vào so sánh frozen-backbone thay vì mặc định WavLM/emotion2vec, và giữ fusion baseline là plain concatenation trước khi đầu tư vào graph attention.
- **Caveats:** Đã đọc toàn bộ PDF (arXiv v1, không trả phí). Overlap thấp là trung thực, không phải chưa đầy đủ: đây là một **challenge system** categorical single-task, không có heterogeneous MTL heads, không có MTL loss-balancing, không có ràng buộc crisis/recall, và không có LLM weak-label distillation — giá trị của nó đối với Pebble chỉ giới hạn ở việc chọn backbone (D7) và corpus MSP-Podcast chung (D3), không phải luận điểm cốt lõi ordinal/MTL.

## Deep research — full-PDF read (2026-07-10)

> Profile: ViEmoSpeech hiện tại (Vietnamese TV-drama SER corpus + tone×emotion bimodal method paper),
> Decision Register V-A…V-H theo `docs/tasks/paper-deep-analysis.md`. Phần "Analysis" (D1–D7) cũ ở
> trên thuộc text-stream đã lưu trữ và không được dùng ở đây. Các mục tiêu đã chuyển: **V-B** (tập
> prosodic feature của họ và mức tăng), **V-A** (cơ chế graph-fusion), **V-D** (lựa chọn prosodic
> feature so với nhiễm tone).

### Source-access note

- **Read path:** PDF cục bộ `pdfs/08-graph-fusion-prosodic-ser.pdf` được trích xuất toàn bộ bằng
  `pdftotext` (Method §3, Setup §4, cả ba bảng kết quả, References). Nội dung này giống hệt
  arXiv:2506.02088v1 (2 Jun 2025).
- **Web validation:** con số headline **Macro F1 39.79% test / 42.20% validation** được xác nhận đối
  chiếu với trang tóm tắt arXiv — truy vấn `Ferreira Gris "Graph-Based Multimodal Fusion" Prosodic Speech Emotion
  Recognition Interspeech 2025 Macro F1 39.79` → dẫn tới https://arxiv.org/abs/2506.02088 (WebFetch trang
  abstract trả về "39.79% on the official test set, with 42.20% on the validation set"). **✔ được xác thực chéo.**
- **Venue authority:** đây là **bản mô tả hệ thống dự thi (challenge system description)** cho INTERSPEECH-2025
  SER-in-Naturalistic-Conditions; arXiv v1 là phiên bản duy nhất/có thẩm quyền (không có bản journal riêng;
  mục ResearchGate / Interspeech proceedings mang cùng con số). Không tồn tại chênh lệch preprint-vs-published.
  Các con số ở Table 1/2/3 bên dưới là đơn nguồn (arXiv v1 = venue) và được gắn nhãn ✔ trên cơ sở đó;
  không con số nào có thể tái suy ra độc lập, vì vậy bất kỳ con số nào mang trọng lượng cross-corpus đều được
  gắn cờ theo đó.
- Có source code (github.com/alefiury/InterSpeech-SER-2025) — có thể tái sử dụng nếu ta áp dụng khối F0-quant.

### What the paper actually does

**Task/data.** Nhận diện cảm xúc categorical (Track 1) trên **MSP-Podcast** (cùng corpus naturalistic
found-speech đã được deep-read ở bimodal-12), tiếng Anh, spontaneous. Metric = **Macro F1** (họ ghi chú
Micro F1 = accuracy, nên accuracy không được báo cáo riêng). Weighted Cross-Entropy (trọng số lớp theo
inverse-frequency), batch 8, 20 epochs, AdamW, cosine LR với 500 bước warm-up, LR giới hạn 5e-5→1e-5,
grad-clip norm 10. Nhãn `X` / `O` (no-agreement / other) bị loại khỏi tập validation đã lọc.

**Pipeline bốn giai đoạn (Fig. 1, §3):**
1. **Unimodal SSL bake-off (Table 1, Macro F1, ✔ đơn nguồn):** Wav2Vec2-Large **0.178** <
   HuBERT-Large **0.274** < WavLM-Large **0.313** < XEUS **0.323** < **Whisper-Large-V3 0.366** (tốt nhất;
   Micro F1 0.524, R 0.391). Đặc trưng được trích xuất sẵn từ **lớp ẩn cuối cùng (last hidden layer)** của
   mỗi mô hình SSL đóng băng (frozen). Họ quy sự sụp đổ của Wav2Vec2/HuBERT cho việc pretraining trên
   read-speech, còn chiến thắng của Whisper là do pretraining trên dữ liệu "diverse, spontaneous, and noisy".
2. **Bimodal fusion với text (Table 3, Macro F1, ✔):** text = **RoBERTa-Large** trên transcript
   **Canary-ASR** (họ chủ ý dùng text từ ASR, *bỏ qua transcript gốc của dataset*). Các chiến lược fusion:
   **Simple** concat (mean-pool cả hai modality → MLP) **0.388**; single-layer Transformer
   early-fusion **0.364**; **HCAM** (BiGRU + self-attn + cross-attn) **0.383**; **MDAT** (dual-attention
   transformer dựa trên graph attention, 8 heads) **0.401** (tốt nhất). Bimodal >> unimodal
   (0.401 so với 0.366). Đáng chú ý, simple concat (0.388) gần như bằng MDAT (0.401) — họ ghi nhận công của
   graph attention trong MDAT nhưng cảnh báo mô hình phức tạp bị overfit "given the limited dataset size."
3. **Tích hợp prosodic + spectral (Table 3):** **F0 là prosodic feature duy nhất.** F0 thô từ
   **RMVPE**, chuyển thang mel, **lượng tử hóa (quantized) thành 256 bin + 1 chỉ số padding**, ánh xạ vào
   các embedding học được 256 chiều, chiếu lên 512, mean-pool theo thời gian, nối (concatenate) với
   speech+text. Mức tăng so với baseline 0.388/MDAT: **+ F0 thô 0.397**, **+ F0 lượng tử hóa 0.407**
   (lượng tử hóa vượt baseline F0 thô dùng 1D-CNN, kernel 3/stride 1/256ch, thêm +1.0 Macro F1), + Data-Aug
   0.400, **+ SwiGLU 0.411** (cấu hình đơn tốt nhất). Nhánh spectral: mô hình audio-tagging **CED-Small
   (22M)** trên Kaldi Mel-filterbanks — CED khởi tạo ngẫu nhiên 0.342 < CED pretrained 0.376 < +Data-Aug
   0.393 < +SwiGLU 0.405. F0 (0.411) và CED (0.405) "bổ trợ lẫn nhau" (complementary).
4. **Ensemble (Table 2):** majority vote trên ≥3 cấu hình từ một tìm kiếm vét cạn 13 hướng (thêm XEUS,
   text encoder E5-Large-V2 — kém hơn RoBERTa, Focal loss, balanced sampling); thành viên đơn tốt nhất
   Whisper+RoBERTa+MDAT+F0Quant+SwiGLU+DataAug **0.411**, **ensemble 0.422 val → 39.79% test**.
   SeqAug (resampling đặc trưng tuần tự không phân biệt modality, xác suất 50%, beta α=0.5, hoán vị độc lập
   theo từng chiều) là kỹ thuật tăng cường dữ liệu. SwiGLU MLP mang lại mức tăng "nhỏ nhưng ổn định".

**Punchline:** graph fusion (MDAT) là *fusion* tốt nhất nhưng chỉ hơn concat thuần túy +1.3 Macro F1;
hai độ chênh lớn nhất là **modality** (unimodal 0.366 → bimodal 0.401, +3.5) và **khối prosodic F0
lượng tử hóa** (+1.9 so với fusion đơn giản). Mọi thứ khác (SwiGLU, SeqAug, CED, ensemble) đều ≤+1.5.

### Parts directly useful for Pebble

1. **[V-B] Prosodic feature *chỉ là F0, và F0 được lượng tử hóa* — trích xuất khối này, nhưng biết trần
   của nó.** Toàn bộ đóng góp prosodic của họ là một kênh duy nhất: RMVPE F0 → 256 mel-bin → embedding
   học được. F0 lượng tử hóa (+1.9 Macro F1 so với concat; 0.388→0.407, ✔ Table 3) vượt qua F0 thô dùng
   CNN (0.397, +0.9), vậy nên **rời rạc hóa (discretize) F0 thay vì đưa nguyên contour thô vào**. Artifact
   cụ thể: sub-vector prosody của nhánh audio ViEmoSpeech — áp dụng mẫu mel-scale-quantize-embed, nhưng
   xem V-D bên dưới để biết vì sao F0 đơn lẻ là lựa chọn prosodic sai cho tiếng Việt.
2. **[V-A] Graph fusion (MDAT/GAT) chỉ nhỉnh hơn concatenation một chút ở quy mô ~20k utterance.**
   MDAT 0.401 so với Simple-concat 0.388 (+1.3 Macro F1, ✔ Table 3); Transformer early-fusion (0.364) và
   HCAM (0.383) đều *thua* concat. Chính giải thích của họ: fusion phức tạp bị overfit ở "limited dataset
   size". ViEmoSpeech P1 có ~18k utt — cùng chế độ dữ liệu. Artifact cụ thể: giữ **mean-pool concat → MLP**
   làm baseline fusion V-A mà mọi learned fusion phải vượt qua, và chỉ coi GAT là lựa chọn *tier trên* nếu
   một biến thể cross-attention/gated vượt concat với biên độ lớn hơn phương sai giữa các seed.
3. **[V-B] Trên MSP-Podcast tự nhiên, Whisper-Large-V3 > XEUS > WavLM > HuBERT > Wav2Vec2.**
   (0.366/0.323/0.313/0.274/0.178, ✔ Table 1.) Các encoder được pretrain trên read-speech (W2V2, HuBERT)
   sụp đổ trên spontaneous speech. Artifact cụ thể: so sánh frozen-backbone của V-B phải bao gồm **nhánh
   Whisper-encoder và nhánh XEUS**, không chỉ WavLM/emotion2vec — và điều này mâu thuẫn trực tiếp với
   cách đọc "WavLM mặc định" kế thừa từ bimodal-12 (xem phần contradictions).
4. **[V-D] Họ không kiểm soát *bất cứ điều gì* giống tone — prosodic feature duy nhất họ thêm vào chính
   là đặc trưng bị nhiễm tone nhất.** F0 là kênh prosodic duy nhất; không có energy, không có duration,
   không có phonation/voice-quality; không có mô hình hóa tone; MSP-Podcast là tiếng Anh (atonal), nên
   nhiễm lexical-tone×F0 không bao giờ xảy ra với họ. Bài báo này là minh chứng rõ ràng cho thiết kế mà
   ViEmoSpeech *không được* sao chép mù quáng (xem child/tone lens). Artifact cụ thể: quyết định thiết kế
   prosody của V-D — ghép hoặc thay F0 bằng đặc trưng amplitude/energy + duration (các carrier cảm xúc
   độc lập với tone theo vn-13).

### How each part helps Pebble succeed

- **Sub-vector prosody (V-B).** Triển khai khối F0-quantization (RMVPE → 256 mel-bin → embedding học được
  256-d → chiếu 512 → mean-pool) như một nhánh, nhưng chạy nó trong một **ablation đối chứng với nhánh
  amplitude/energy+duration và nhánh phonation (jitter/shimmer/HNR/H1-H2 từ vn-06)**. Mức tăng +1.9-Macro-F1
  của F0 trên tiếng Anh là *cận trên* của những gì prosody-F0-thô có thể mang lại; thử nghiệm ViEmoSpeech
  là xem mức tăng đó có sống sót — hay đảo ngược — một khi F0 mang tải tone (measurable claim của V-D).
- **Fusion baseline ladder (V-A).** Đưa nguyên bậc thang fusion của họ vào bảng thử nghiệm V-A:
  concat 0.388 / Transformer 0.364 / HCAM 0.383 / MDAT 0.401. Trên corpus nhỏ của ta, giả thuyết không
  (null hypothesis) là "learned fusion ≈ concat"; ta chỉ công nhận một chiến thắng của fusion nếu một
  module cross-attn/gated/query-based vượt concat quá độ lệch chuẩn giữa các seed (mức +1.3 của chính MDAT
  nằm trong dải nhiễu mà họ tự cảnh báo).
- **Backbone choice (V-B).** Thêm nhánh Whisper-encoder + XEUS đông lạnh (frozen) vào cuộc so tài
  WavLM/emotion2vec. Với tiếng Việt, điều này khớp với phát hiện về mid-layer của vn-06 — nhưng lưu ý họ
  dùng lớp ẩn **cuối cùng** (last hidden layer), một lớp probe được biết là kém tối ưu cho tone; cuộc so
  tài backbone của ta nên quét qua các lớp, không sao chép last-layer.
- **Text-under-ASR (V-C, phụ).** Họ đưa transcript **ASR (Canary), không phải gold**, vào RoBERTa và vẫn
  đạt bimodal >> unimodal — một điểm dữ liệu cho thấy fusion trên ASR-text là khả thi, dù Canary trên
  tiếng Anh ≠ PhoWhisper trên tiếng Việt high-arousal tone-swap (mày→máy); câu hỏi về độ bền V-C của ta
  vẫn còn để ngỏ.

### Child mental-health lens (ViEmoSpeech transfer validity)

- **Thất bại chuyển giao cốt lõi chính là bản thân prosodic feature.** Tiền đề của ViEmoSpeech (vn-13
  Chang, vn-06 Shen) là **lexical tone tiếng Việt sống trong F0**: hiệu ứng của cảm xúc lên **F0 trung
  bình và F0 range phụ thuộc vào tone** (tương tác tone×emotion có ý nghĩa thống kê, F0 χ²(12)=70.18
  p<.001; F0-range χ²(12)=114.64 p<.001 — vn-13), trong khi hiệu ứng của cảm xúc lên **amplitude và
  duration độc lập/cộng tính với tone** (amp p=.98, dur p=.29). Kênh prosodic *duy nhất* của bài báo này
  là F0 — tức chính xác chiều bị nhiễm tone trong tiếng Việt. Embedding F0 lượng tử hóa của họ, nếu áp
  dụng cho tiếng Việt, sẽ mã hóa một hỗn hợp của **định danh lexical-tone + cảm xúc + người nói** mà không
  có cách nào tách chúng ra; trên MSP-Podcast tiếng Anh, sự nhiễm đó không tồn tại, nên mức tăng +1.9 của
  họ **không** chuyển giao nguyên vẹn. **Mitigation:** (a) ưu tiên đặc trưng prosodic
  amplitude/energy + duration (các carrier cảm xúc bền vững với tone); (b) nếu dùng F0, điều kiện hóa nó
  theo chú thích syllable-tone (nhãn tone ADR) để mô hình có thể tách tone ra — đây là thử nghiệm
  tone-representation của V-D; (c) thêm một vector phonation/voice-quality vì tone tiếng Việt mang nhiều
  tính phonation (vn-06) và Chang chỉ đo F0/amp/dur.
- **Không có bất kỳ nhận thức về tone ở đâu cả.** Họ không thêm kiểm soát nào cho tone, dialect, hay
  người nói; điều này chấp nhận được với tiếng Anh, nhưng loại bài báo này khỏi vai trò khuôn mẫu cho một
  corpus ngôn ngữ có tone. Đây *chính là* khoảng trống mới lạ (novelty whitespace) của ViEmoSpeech được
  phát biểu lại: ngay cả một hệ thống SER tập trung vào prosody năm 2025 vẫn coi F0 là một tín hiệu cảm
  xúc thuần túy.
- **Cảnh báo về đạo đức/nhãn ở đây khá nhẹ** (MSP-Podcast, giọng nói podcast của người lớn, không có
  tuyên bố lâm sàng) — khác với vn-10, bài báo này không phóng đại một ứng dụng sức khỏe tâm thần, nên
  không có anti-pattern cần gắn cờ; đây đơn giản là một hệ thống nhận diện cảm xúc có thiết kế prosodic
  không nhận biết tone.

### Limitations & open questions for Pebble

- **Mâu thuẫn với bimodal-12 (WavLM-default):** deep-read MSP-Podcast trước đây kết luận "WavLM ≥
  Wav2vec2 ≥ HuBERT clean → WavLM default." Trên **cùng corpus**, bài báo này xếp hạng
  **Whisper-Large-V3 (0.366) > XEUS (0.323) > WavLM (0.313)** — WavLM đứng thứ ba, bị các encoder
  pretrain theo ASR vượt qua trên spontaneous speech. Cách giải quyết cho V-B: "WavLM default" vẫn đúng
  cho các benchmark clean/read; trên found-speech tự nhiên (chế độ của ta), các encoder Whisper/XEUS nên
  được đưa vào cuộc so tài và có thể thắng.
- **Mâu thuẫn với chính tiền đề tone×emotion của ta (V-D):** kết quả "F0 lượng tử hóa giúp ích
  (+1.9 Macro F1)" của họ đúng trên tiếng Anh nhưng *ngược lại* với những gì ViEmoSpeech dự đoán cho
  tiếng Việt, nơi F0 mang tải tone — nên cùng một feature giúp ích cho họ có thể gây hại cho ta hoặc đòi
  hỏi phải điều kiện hóa theo tone. Sự đảo ngược đó tự nó là một đóng góp đo lường được của ViEmoSpeech
  (độ chênh F0-prosody giữa VN so với tiếng Anh/Quan Thoại).
- **Chiến thắng của graph-fusion nằm trong khoảng nhiễu (V-A gap):** MDAT chỉ hơn concat +1.3 Macro F1
  và cả fusion kiểu Transformer lẫn HCAM đều *thua* concat; bài báo không bao giờ báo cáo phương sai theo
  seed hay ý nghĩa thống kê, nên "graph fusion hiệu quả" chỉ được khẳng định trên một split duy nhất. Câu
  hỏi mở: liệu có bất kỳ learned fusion nào thực sự vượt qua concat ở quy mô ~18k utterance, hay độ phức
  tạp của fusion là một điểm trừ ròng ở quy mô của ta?
- **Chỉ probing lớp cuối cùng:** đặc trưng SSL được lấy từ lớp ẩn cuối cùng — kém tối ưu cho tone (vn-06:
  tone đạt đỉnh ở giữa stack). Bảng xếp hạng backbone của họ có thể thay đổi dưới một layer sweep; đừng
  kế thừa nó như kết quả cuối cùng.
- **Không có dimensional/attribute track, không có distress:** chỉ categorical (Track 1). Không đóng góp
  gì cho V/A-CCC (V-G) hay distress recall-floor head (V-F); attribute track của challenge nằm ngoài
  phạm vi ở đây.
- **Con số đơn nguồn:** mọi giá trị trong bảng chỉ có ở arXiv-v1 (challenge system, không có bản journal);
  chỉ có headline 39.79/42.20 là được xác thực chéo độc lập. Các mức chênh ở Table 1/3 dùng được như tín
  hiệu thiết kế nhưng không phải như mốc leaderboard cross-paper.
