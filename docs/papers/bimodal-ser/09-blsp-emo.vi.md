# Paper 09 — BLSP-Emo: Towards Empathetic Large Speech-Language Models

> Bản dịch tiếng Việt của [09-blsp-emo.md](09-blsp-emo.md) — cập nhật 2026-07-10.

- **Authors:** Chen Wang, Minpeng Liao, Zhongqiang Huang, Junhong Wu, Chengqing Zong, Jiajun Zhang
- **Venue / year:** arXiv preprint, 06/2024
- **Links:** abs https://arxiv.org/abs/2406.03872 · PDF `pdfs/09-blsp-emo.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Speech-LM hai giai đoạn: semantic alignment (ASR data) → emotion alignment (SER continuation task), hướng tới phản hồi đồng cảm.

**Relevance to Pebble:** Audio-LLM analogue gần nhất với framing emotional-support-chat của Pebble.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Profile scored against (assembled 2026-07-03 from IDD layers):** primary = ordinal suicide-risk **text** classification, teacher-LLM **silver labels** → BERT-family encoder, **gold-holdout** eval, ordinal-aware losses (QWK/MAE) — validity/ethics over SOTA (`docs/intent/constraints.md`). Adjacent **voice** stream (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`): frozen **emotion2vec/WavLM-Large** backbone + shared trunk, **3 heterogeneous heads** (emotion CE · affect V/A **CCC** · crisis BCE under **hard recall-floor 0.90**), **Kendall uncertainty weighting**, trained trên **RAVDESS** proxy labels, Kaggle run đang chờ chạy.

### Analysis — BLSP-Emo
- **Overlap:** 35% (peripheral) — D1=1, D2=0, D3=1, D4=2, D5=0, D6=0, D7=1.
  - Formula: (3·1 + 2·0 + 1·1 + 2·2 + 2·0 + 2·0 + 1·1)/26 = 9/26 = 35%.
- **Closest on:** D4 (teacher-LLM silver-label distillation — LLM sinh ra các continuation gắn điều kiện cảm xúc làm supervision, chưng cất qua KD); kế đến là D3/D7 (SER corpora bao gồm RAVDESS; các baseline WavLM/HuBERT/wav2vec2 = chính các voice backbone của Pebble).
- **Best point (Baseline to beat):** Table 1 báo cáo **các bộ phân loại SER dựa trên encoder trên đúng backbone+corpus mà voice stream của Pebble đang dùng** — WavLM-Large = **70.3%** acc trên RAVDESS (5-class), 68.9% IEMOCAP; HuBERT-Large 70.5% RAVDESS; wav2vec2-Large 64.0% RAVDESS.
  - **How to apply to Pebble:** dùng WavLM-Large 70.3% / RAVDESS làm comparator sanity-check bên ngoài cho emotion head trong run `voice-mtl-heads` sắp chạy trên Kaggle — nhưng lưu ý các nhãn không tương đương 1-1 (BLSP-Emo ánh xạ RAVDESS về tập 5-class {neutral,happy,sad,angry,surprise} như một phép test OOD; MTL probe dùng RAVDESS 8-class với split random 10-fold), nên coi đây là một mốc tham chiếu ước lượng cho một SER head frozen-backbone, không phải một benchmark khớp hoàn toàn.
- **Caveats:** một Speech-LLM đồng cảm **generative** end-to-end (Whisper enc + Qwen-7B + modality adapter) — kiến trúc cách khá xa so với classifier MTL frozen-probe của Pebble; không có head continuous/regression, không có nguyên tắc cân bằng MTL, không có mục tiêu crisis/safety, không thuộc miền clinical/mental-health (do đó D2/D5/D6=0). PDF đã đọc trang 1–5 (method + các bảng kết quả chính); các phần sau (multi-turn conversation, cross-lingual generalization, appendix B/C) chưa đọc — không cần thiết cho điểm số, nhưng độ tin cậy ở các phần đó thấp hơn.

## Deep research — full-PDF read (2026-07-10)

> Được phân tích theo **hồ sơ ViEmoSpeech hiện hành + Decision Register (V-A…V-H)** trong
> `docs/tasks/paper-deep-analysis.md`, KHÔNG theo hồ sơ text-stream cũ trong khối "Analysis"
> ở trên (vốn chấm điểm paper này cho sản phẩm suicide-risk đã lưu trữ và chỉ được giữ lại
> làm lịch sử). Phần này được THÊM VÀO; không có gì ở trên bị thay đổi.

### Source-access note

PDF cục bộ `pdfs/09-blsp-emo.pdf` (arXiv:2406.03872**v1**, 6 Jun 2024) đã được đọc trọn vẹn qua
`pdftotext` — method (§2), experiment setup (§3), toàn bộ các bảng kết quả chính (Tables 1–5), bảng
cross-lingual (Table 3), ablation (§4.2), phân tích ChatGPT/MultiTask (§4.3),
Limitations, và Appendices B–E (bảng dataset, chi tiết training, prompt, ví dụ định tính).
Provenance validation:
- **Venue status** — tìm kiếm `BLSP-Emo … 2406.03872 published venue` dẫn về
  `https://arxiv.org/abs/2406.03872`; paper là một **arXiv preprint** (cs.CL, 6 Jun 2024),
  code+weights tại `github.com/cwang621/blsp-emo` / `huggingface.co/cwang621/blsp-emo`. Không xác
  nhận được venue peer-review nào trong bản arXiv HTML (một bản mirror trên ResearchGate gợi ý có
  đăng sau đó nhưng không thể xác minh) → coi là preprint; v1 là phiên bản duy nhất, nên không có
  chênh lệch preprint-vs-published cần đối chiếu. ✔
- **Table 1 numbers** — đối chiếu với bản render arXiv HTML
  `https://arxiv.org/html/2406.03872v1`; con số MELD trọng yếu **BLSP-Emo = 57.3%**
  khớp chính xác với PDF cục bộ và bằng đúng **0.573** mà bimodal-03 (EAA) trích dẫn. ✔
  Tất cả các dòng của Table 1 dưới đây đều được đối chiếu với bản HTML render đó.

### What the paper actually does

**Goal.** Xây dựng một empathetic speech-LLM end-to-end hiểu được *cả* ngữ nghĩa *lẫn*
cảm xúc paralinguistic trong lời nói và sinh ra văn bản đồng cảm, chỉ sử dụng các bộ dữ liệu ASR + SER
sẵn có (không có dữ liệu instruction gắn điều kiện cảm xúc mới nào). Đây là một **Audio-Language Model (ALM)**,
không phải một mạng fusion SER discriminative.

**Architecture (§2.1, App. C).** Whisper-large-v2 **encoder** → convolution **modality adapter**
(3× 1-D conv, stride 2, kernel 5, pad 2, ×8 downsample, bottleneck dim 512) → **Qwen-7B-Chat** LLM.
✔ (App. C).

**Two-stage alignment (phần lõi của phương pháp):**
1. **Semantic alignment (§2.2).** Behavior-cloning trên dữ liệu ASR: prompt *text* LLM để tiếp tục
   một transcript, sau đó train speech model để phát ra *cùng* continuation đó từ speech, thông qua một
   **loss knowledge-distillation dạng KL-divergence** (Eq. 1). **Chỉ modality adapter được tune;
   speech encoder + LLM giữ nguyên (frozen).** Cho ra checkpoint "BLSP".
2. **Emotion alignment (§2.3).** Từ các bộ ba SER (speech `s`, transcript `x`, emotion `e`), prompt
   LLM để viết một **continuation nhận biết cảm xúc** ("Continue … that reflects a `<emotion>` tone
   … `<transcript>`"). Sau đó fine-tune model để tái tạo continuation đó **chỉ từ speech** (prompt
   không còn nêu tên cảm xúc nữa — model phải đọc ra cảm xúc từ audio). Loss chính = LM
   loss trên continuation (Eq. 2), **cộng thêm một auxiliary SER classification head** trên pooled adapter
   hidden states (Eq. 3). **Ở bước này cả speech encoder VÀ LLM đều được unfreeze** (LLM qua **PLoRA**,
   R=16, α=16, chỉ áp dụng cho speech tokens), cộng với adapter và classifier. ✔ (§2.3, App. C).

**Data (§3.1, App. B/Table 6).** Semantic stage: ~**1.9M** cặp (speech, transcript) tiếng Anh
(LibriSpeech + CommonVoice 13 + GigaSpeech-M) + một tập tiếng Trung tương đương từ WeNetSpeech. Emotion
stage: ~**70k** utterance từ IEMOCAP + MELD + CMU-MOSEI + MEAD + ESD (EN+ZH), gộp về **5 class:
neutral, happy, sad, angry, surprise**. Test in-domain = IEMOCAP S5 + MELD-test; OOD = RAVDESS +
MerBench; zero-shot cross-lingual = AESDD (Gr), CaFE (Fr), RESD (Ru). ✔

**Key results (tất cả Acc%, đã đối chiếu ✔):**
- **Table 1 (standalone SER).** BLSP-Emo dẫn đầu tổng thể: **IEMOCAP 76.0 · MELD 57.3 ·
  RAVDESS 72.0** (MerBench t1/t2 60.0/54.7). Các bộ phân loại encoder: **WavLM-Large 68.9/54.6/70.3**,
  **HuBERT-Large 64.6/53.2/70.5**, **wav2vec2-Large 69.3/54.8/64.0**. **SALMONN-7B** (một ALM đối
  thủ) kém hơn hẳn: 67.0/32.9/38.8. Các baseline text-only là điểm mấu chốt: **Text+LLM RAVDESS = 11.1%**,
  **Whisper(ASR)+LLM RAVDESS = 13.7%**, nhưng Text/Whisper+LLM lại *tương đương-hoặc-tốt hơn trên MELD*
  (54.0/53.8) — tức là text có tính thông tin trên nội dung TV hội thoại nhưng gần như vô dụng trên
  nội dung diễn (acted)/câu cố định.
- **Table 2 (SpeechAlpaca, synthetic TTS instructions).** BLSP-Emo SER **83.8%**, GPT-4 quality
  **8.8**, empathy **7.7**; BLSP-SER (fine-tune để dự đoán trực tiếp nhãn) sụp đổ về chất lượng phản hồi
  (1.9/2.1) — chứng minh rằng chính mục tiêu *continuation*, chứ không phải label prediction, mới giữ
  được khả năng instruction-following. ✔
- **Table 3 (zero-shot cross-lingual).** BLSP-Emo trung bình **63.4** (AESDD 68.8 / CaFE 75.3 / RESD 46.2),
  cao nhất tổng thể; tri thức cảm xúc chuyển giao sang các ngôn ngữ chưa từng thấy. ✔
- **Table 4 (ablation).** Bỏ semantic-alignment pretraining → IEMOCAP **76.0→68.5**, quality
  **8.8→6.7** (semantic-first là thiết yếu). Bỏ auxiliary SER loss → IEMOCAP **76.0→72.2**,
  RAVDESS **72.0→66.6** (aux SER giúp ích cho SER trên *speech tự nhiên*, không ảnh hưởng đến
  SpeechAlpaca tổng hợp). ✔
- **Table 5.** Xây dựng continuation bằng **cùng LLM nội bộ** cho kết quả tốt hơn dùng ChatGPT
  (BLSP-ChatGPT kém hơn trên mọi metric), và **emotion-aware continuation** tốt hơn một framing
  **continuation+SER multi-task** naive (BLSP-MultiTask kém hơn ở mọi mặt). ✔

### Parts directly useful for ViEmoSpeech (tagged by Decision ID)

1. **[V-A] Chương trình huấn luyện "semantic-first, emotion-second" theo giai đoạn — như một khái
   niệm *lịch trình*, không phải một kiến trúc.** Ablation chủ đạo của BLSP-Emo (Table 4: không có
   semantic pretraining, IEMOCAP 76.0→68.5, quality 8.8→6.7 ✔) nói rằng emotion alignment
   paralinguistic chỉ hoạt động tốt *sau khi* model đã được ground về mặt ngữ nghĩa. Đây là cùng
   một tín hiệu về thứ tự như bimodal-05 (task-alternating > naive joint) và C²SER (bimodal-01).
   **Transfer risk: CAO ở kiến trúc, THẤP ở thứ tự.** BLSP-Emo đạt được "fusion" bằng cách *unfreeze
   và fine-tune một LLM 7B + toàn bộ Whisper encoder* với PLoRA — hoàn toàn trái ngược với ràng buộc
   frozen-backbone + small learned-fusion của ViEmoSpeech. Vậy nên đây là một **existence proof của
   ALM (giống C²SER), không phải một fusion template có thể copy** (vai trò đó thuộc về FAS/CASE
   vn-07 và EAA bimodal-03). Cái *có thể* chuyển giao: một kế hoạch training hai giai đoạn — (a)
   align/warm nhánh text PhoBERT-over-PhoWhisper trên transcript của chúng ta trước, (b) sau đó mới
   train audio↔text fusion cho emotion — thay vì một mục tiêu joint lạnh từ đầu.

2. **[V-C] Auxiliary categorical SER head bên trên mục tiêu chính cải thiện SER trên speech tự
   nhiên.** Dòng w/o-SER của Table 4: IEMOCAP 76.0→72.2 và RAVDESS 72.0→66.6 ✔ khi bỏ auxiliary
   classification loss (Eq. 3). **Transfer risk: THẤP/TRUNG BÌNH** — đây là một regularizer
   multi-objective mang tính tổng quát, vẫn giữ được hiệu quả khi đổi register (nó giúp ích cho
   speech *tự nhiên*, không phải tập tổng hợp). Cụ thể: giữ một **auxiliary emotion head categorical
   chỉ-audio (hoặc chỉ-text) song song với fused head** trong model của chúng ta, chính là biện pháp
   audio-anchoring mà vn-12 đã lập luận.

3. **[V-C] Bằng chứng về kênh text trên nội dung diễn (acted): Text/Whisper+LLM = 11.1% / 13.7% trên
   RAVDESS nhưng ≈54% trên MELD (Table 1 ✔).** **Transfer risk: THẤP — đây là con số liên quan nhất
   đến ViEmoSpeech trong paper.** RAVDESS là *acted, câu mang (carrier) cố định* (trung tính về mặt
   cảm xúc ngữ nghĩa) — kênh text hầu như không mang thông tin gì (gần mức ngẫu nhiên). MELD là
   *hội thoại TV mang tính tự nhiên* — text có tính thông tin. ViEmoSpeech được cắt từ **phim truyền
   hình VN diễn (acted)**, các câu thoại kịch bản nằm giữa hai cực này nhưng nghiêng về chế độ
   acted/tín hiệu-text-thấp ở nhiều lượt lời. Điều này nói rằng nhánh PhoBERT-over-PhoWhisper của
   chúng ta **không thể mặc định mang cảm xúc theo cách các kết quả trên corpus hội thoại gợi ý**,
   và định lượng hóa tính phụ thuộc-register mà bản tổng hợp cross-cutting đã cảnh báo.

4. **[V-B] Các mốc encoder frozen-vs-fine-tuned.** WavLM-Large **70.3** / HuBERT-Large **70.5** /
   wav2vec2-Large **64.0** trên RAVDESS; WavLM **68.9** / wav2vec2 **69.3** / HuBERT **64.6** trên
   IEMOCAP (Table 1 ✔). Whisper-large-v2 encoder, khi đã được **fine-tune cho emotion** bên trong
   BLSP-Emo, đạt 72.0 RAVDESS / 76.0 IEMOCAP — tức Whisper encoder là một backbone SER khả thi,
   nhưng *chỉ sau khi fine-tune*. **Transfer risk: TRUNG BÌNH** — mọi con số encoder ở đây đều đến từ
   một encoder *đã fine-tune* + pooling + linear head, nên đây KHÔNG phải các mốc frozen-backbone;
   chúng cho biết WavLM ≈ HuBERT ≥ wav2vec2 và Whisper-encoder là hợp lý, nhưng không giải quyết câu
   hỏi frozen-vs-FT của chúng ta. Giữ nhánh WavLM frozen làm mặc định (nhất quán với bimodal-12) và
   coi Whisper-encoder là một lựa chọn thay thế gần-ASR đáng để A/B, lưu ý PhoWhisper đã có sẵn
   trong pipeline cho ASR.

### How each part helps ViEmoSpeech succeed

- **V-A → ADR về lịch trình training, không phải hoán đổi model.** Viết thí nghiệm fusion thành hai
  giai đoạn: Phase-1 warm-start nhánh text (fine-tune PhoBERT trên transcript ASR + nhãn cảm xúc của
  chúng ta), Phase-2 train fusion head audio↔text với backbone giữ nguyên (frozen). Trích dẫn Table 4
  của BLSP-Emo làm bằng chứng rằng emotion alignment trên một model *lạnh về ngữ nghĩa* cho kết quả
  kém hơn — tín hiệu paralinguistic cần một khung ngữ nghĩa đã được ground trước. **Không** trích dẫn
  BLSP-Emo như một kiến trúc fusion; định vị của chúng ta: "không giống các ALM generative (BLSP-Emo,
  C²SER) fine-tune một LLM hàng tỷ tham số, chúng tôi giữ backbone frozen và học một module fusion
  nhỏ."
- **V-C → cấu hình head cụ thể.** Thêm một auxiliary emotion head 7-class chỉ-audio (linear nhỏ trên
  pooled WavLM features) train đồng thời với fused head; dùng Eq. 3 + ablation Table-4 của BLSP-Emo
  làm tiền lệ rằng aux head này nâng cao SER trên *speech tự nhiên*. Điều này cũng hiện thực hóa
  biện pháp "modality-dropout / audio-anchoring" mà vn-12 đề xuất.
- **V-C → stress test cho nội dung acted.** Xây dựng một tập eval tường minh gồm các lượt lời
  *ít nội dung từ vựng* (câu cảm thán ngắn, câu mang trung tính về cảm xúc) và báo cáo audio-only vs
  text-only vs fused trên tập đó. RAVDESS 11.1% text-only của BLSP-Emo là trích dẫn cho việc trên
  các lượt lời như vậy, nhánh text ở mức ngẫu nhiên — nên nhiệm vụ của fusion trên các lượt lời đó
  là *không* bị kéo lệch về phía text.
- **V-B → giữ ladder trung thực.** Đặt WavLM-Large (frozen) làm nhánh audio mặc định; ghi nhận các
  con số encoder đã fine-tune của BLSP-Emo như một tham chiếu upper-bound (fine-tuned, không phải
  frozen) để không nhầm mốc 70% RAVDESS fine-tuned với mục tiêu frozen-probe. Thêm một A/B
  Whisper-encoder vì PhoWhisper đã sẵn có cho ASR.

### Child mental-health / ViEmoSpeech transfer-risk lens

- **Đây là một ALM, nên nó là một *existence proof*, không phải một build target — cùng phán quyết
  như C²SER (bimodal-01).** BLSP-Emo fine-tune Whisper-large-v2 + Qwen-7B-Chat (PLoRA) trên ~1.9M
  ASR + 70k SER utterance qua 4× A100 (2.5 ngày + 3 giờ). Ràng buộc của ViEmoSpeech là một backbone
  *frozen* + fusion nhỏ trên ~18k utterance tiếng Việt. Chúng ta có thể mượn các *phát hiện* của nó
  (thứ tự semantic-first, lợi ích của aux-SER, xây dựng dữ liệu bằng cùng-LLM) nhưng không mượn công
  thức của nó.
- **Register match là một phần và thuận lợi để trích dẫn.** BLSP-Emo train/test khá nặng trên các
  corpus **acted** (IEMOCAP, RAVDESS, MEAD, ESD đều "Act" trong Table 6) — cùng register acted như
  phim truyền hình VN. Các con số acted trung thực của nó (IEMOCAP 76, RAVDESS 72, *với một ALM 7B
  đã fine-tune*) nằm thấp hơn nhiều so với các baseline VN bị leak (vn-08 86.6, vn-10 0.87) và là
  một mốc sanity hữu ích cho việc SER 5-class acted thực sự tốn kém bao nhiêu.
- **Khung "empathetic response" ≠ nhiệm vụ của chúng ta.** Downstream của họ là *sinh* văn bản đồng
  cảm (SpeechAlpaca quality/empathy 8.8/7.7 qua giám khảo GPT-4). ViEmoSpeech làm *gán nhãn* (7-class
  + V/A + distress), không sinh sinh, không hội thoại hướng-trẻ-em. Metric empathy của họ là một
  preference GPT-4 trên TTS tổng hợp — không có nền tảng clinical hay an toàn trẻ em; không nhập
  khẩu metric đó. Distress head của chúng ta vẫn là một proxy phim-diễn với recall floor (V-F),
  không bị ảnh hưởng bởi paper này.
- **Chuyển giao ngôn ngữ là đáng khích lệ nhưng còn nông.** Zero-shot sang Greek/French/Russian
  (Table 3, trung bình 63.4 ✔) cho thấy các tín hiệu cảm xúc học được từ EN+ZH chuyển giao sang các
  ngôn ngữ chưa từng thấy — một tín hiệu tích cực nhẹ rằng tín hiệu cảm xúc tiếng Việt là học được —
  nhưng không ngôn ngữ nào trong số đó là ngôn ngữ có thanh điệu theo nghĩa từ vựng, và họ chưa bao
  giờ khảo sát thanh điệu, nên điều này không nói lên được gì về sự cạnh tranh kênh tone×emotion vốn
  là điểm mới của chúng ta.

### Limitations & open questions for ViEmoSpeech (incl. explicit contradictions/gaps)

- **MÂU THUẪN với ràng buộc lõi của ViEmoSpeech (frozen backbone).** Toàn bộ mức tăng "hiểu cảm xúc"
  của BLSP-Emo đến từ việc *unfreeze* encoder và LLM ở stage 2 (§2.3). Nếu kênh audio frozen tỏ ra
  quá yếu trên các clip VN acted của chúng ta, paper này là lời nhắc rằng các ALM đồng cảm mạnh nhất
  trong lĩnh vực này mua được độ nhạy paralinguistic bằng cách fine-tune — một đòn bẩy mà chúng ta
  đã chủ động từ bỏ. Biện pháp giảm thiểu cần test: một A/B partial-unfreeze nhẹ (chỉ các lớp
  encoder trên cùng), có ngân sách nhưng giới hạn.
- **MÂU THUẪN / tam giác hóa về sự chi phối của text.** Text+LLM **RAVDESS 11.1%** của BLSP-Emo
  (Table 1 ✔) mâu thuẫn trực tiếp với tuyên bố "semantics dominate" của vn-12 và củng cố tuyên bố
  "text gần như vô dụng trên VN acted (38–44%)" của vn-08 cũng như "text sụp đổ trên acted tonal
  (13.93)" của bimodal-01. Cách dung hòa vẫn giữ nguyên: sự phụ thuộc-vào-text là **phụ thuộc
  register** — cao trên nội dung hội thoại (MELD ≈54%), gần mức ngẫu nhiên trên nội dung câu cố định
  acted (RAVDESS 11.1%). Điểm neo của chúng ta phải là tuyên bố *kênh acoustic có thể đo được*
  (tone×emotion trong F0/phonation, vn-06/vn-13), không phải một tuyên bố chung chung "text mang
  nhiều tải trọng hơn".
- **THAM CHIẾU CHÉO neo cùng EAA (bimodal-03).** EAA báo cáo **MELD 0.687** cho fusion cross-attention
  đôi audio↔audio (HuBERT+BEATs) so với **0.573** của BLSP-Emo (Table 1 ✔, = 0.573 mà EAA trích
  dẫn). Một fusion bimodal chuyên biệt dưới-tỷ-tham-số **vượt một ALM generative 7B khoảng ~11 điểm
  trên SER MELD** — bằng chứng trực tiếp cho luận điểm của ViEmoSpeech rằng một fusion nhỏ đã học có
  thể phân loại tốt hơn một ALM khổng lồ trên nhiệm vụ SER discriminative. (Lưu ý: tập train không
  giống hệt nhau, nên coi đây là tính định hướng, không phải head-to-head.)
- **GAP — "tone" được nêu tên, thanh điệu từ vựng vẫn chưa được đụng đến (paper thứ N trong tập).**
  Phần Limitations liệt kê "các loại tín hiệu paralinguistic khác trong lời nói con người, như tone
  và ý định … chưa được xử lý" — nhưng "tone" ở đây nghĩa là ngữ điệu/prosody, không phải **thanh
  điệu từ vựng (lexical tone)**. Giống như CASE, C²SER, MDAT, THAI-SER trước đó, BLSP-Emo dùng/nhắc
  đến "tone" mà chưa bao giờ coi thanh điệu từ vựng là một biến số. Tính mới của V-D vẫn còn nguyên
  vẹn hoàn toàn và giờ được tam giác hóa từ một góc độ khác.
- **Câu hỏi mở cho thiết kế aux-head của chúng ta.** BLSP-Emo cho thấy *chỉ fine-tune để dự đoán
  nhãn* (BLSP-SER) phá hủy hành vi downstream (Table 2: quality 1.9) trong khi một loss SER
  *auxiliary* bên trên một mục tiêu generative thì có ích (Table 4). Chúng ta không có mục tiêu
  generative, nên chế độ lỗi phá hủy đó không áp dụng — nhưng đây là một lời cảnh báo rằng một mục
  tiêu SER categorical có thể chi phối/làm méo một biểu diễn dùng chung. Kiểm thử aux categorical
  head của chúng ta ở trọng số loss thấp và theo dõi các head V/A-CCC và distress-recall xem có suy
  giảm hay không.
