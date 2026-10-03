# Paper 01 — C²SER: Steering Language Model to Stable Speech Emotion Recognition via Contextual Perception and Chain of Thought

> Bản dịch tiếng Việt của [01-c2ser.md](01-c2ser.md) — cập nhật 2026-07-10.

- **Authors:** Zhixian Zhao, Xinfa Zhu, Xinsheng Wang, Shuiyuan Wang, Xuelong Geng, Wenjie Tian, Lei Xie
- **Venue / year:** IEEE TASLP, 2025
- **Links:** abs https://arxiv.org/abs/2502.18186 · PDF `pdfs/01-c2ser.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Audio-LLM SER kết hợp Whisper (semantic) + **emotion2vec-S** (acoustic), dùng chain-of-thought + self-distillation để ổn định phân loại cảm xúc.

**Relevance to Pebble:** emotion2vec là audio backbone Pebble đã chọn — đây là reference kiến trúc trực tiếp cho việc nhúng nó vào pipeline có LLM teacher/distillation.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

### Analysis — C²SER
- **Profile assembled at analysis time** (intent + capabilities, không phải bản snapshot chỉ-văn-bản đã lỗi thời): Pebble = chương trình chính **ordinal suicide-risk text** (NeoBERT ~250M, Gemini silver labels, đánh giá gold-holdout trung thực; QWK/MAE có ý thức về thứ tự; đạo đức + khả năng tái lập) **cộng với một luồng voice liền kề đang hoạt động** (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`): một **backbone WavLM-Large / emotion2vec đóng băng** + trunk chung mang **ba head không đồng nhất** — emotion (CE), affect valence+arousal (**liên tục, CCC loss**), crisis (BCE dưới **sàn recall cứng 0.90**) — được cân bằng bằng **Kendall uncertainty weighting**, hiện đang chạy trên nhãn proxy với **MSP-Podcast (A/V/D)** và **DAIC (crisis)** là mục tiêu nhãn thật kế tiếp. Fine-tune backbone là một non-goal tường minh (các đặc trưng vẫn giữ đóng băng).
- **Thay thế điểm số 31% ngày 2026-07-02, vốn được tính trên profile chỉ-văn-bản đã lỗi thời.**
- **Overlap:** D1=0, D2=0, D3=1, D4=2, D5=1, D6=0, D7=2 → (Σ wᵢ·scoreᵢ = 3·0+2·0+1·1+2·2+2·1+2·0+1·2 = 9) / 26 × 100 = **35% (peripheral)**
- **Closest on:** D7 (Emotion2Vec-S là một bản mở rộng đã công bố của **emotion2vec — backbone đóng băng thực tế của luồng voice**, và paper cũng benchmark cả WavLM) và D4 (silver-labeling bằng giao của hai teacher + self-distillation explicit→implicit).
- **Best point (Method to adopt):** **Emotion2Vec-S** của C²SER thêm một **loss tương phản (contrastive) ở cấp category** lên trên các loss utterance/frame sẵn có của emotion2vec, và theo Table V, nó liên tục vượt qua Emotion2Vec thuần và WavLM-base về độ chính xác cảm xúc trên các tập test tiếng Trung/Anh/đa ngôn ngữ — và checkpoint của nó được công bố công khai.
  - **How to apply to Pebble:** đổi bộ trích xuất đặc trưng đóng băng của luồng voice sang checkpoint **Emotion2Vec-S** đã công bố cho head emotion — một bản nâng cấp drop-in tôn trọng non-goal "backbone giữ đóng băng" (không fine-tune), không cần thay đổi kiến trúc của bộ probe MTL 3-head, và có thể kiểm chứng trong lần chạy Kaggle `pebble-voice-mtl-heads` sắp tới dưới dạng A/B so với đặc trưng emotion2vec hiện tại.
- **Caveats:** SER **phân loại (categorical)** đơn nhiệm qua một ALM sinh (generative) — **không có** head không đồng nhất (D1=0), **không có** mục tiêu liên tục/ordinal hay crisis-recall (cân bằng loss ở D5 là λ_utt=0.1 / λ_cate=100 chỉnh tay, rõ ràng **không phải** Kendall/GradNorm → D5=1 chỉ đạt một phần; D6=0), và **không có** miền mental-health/crisis (D2=0). D3=1 chỉ đạt một phần: paper huấn luyện trên các corpus speech-emotion thật gồm cả **MSP-Podcast** (một mục tiêu của luồng voice), nhưng dùng chúng như SER phân loại phẳng, không phải affect liên tục. Việc đổi sang Emotion2Vec-S và cổng dual-teacher chuyển giao lần lượt sang luồng **voice** và giai đoạn silver-label của luồng **text**; cả hai đều không đụng đến kiến trúc NeoBERT. Chấm điểm từ trang 1–8 (abstract, related work, toàn bộ method, chuẩn bị dữ liệu, thiết lập thực nghiệm, kết quả Table V); các bảng ablation chỉ được lướt qua và không ảnh hưởng đến điểm số các chiều.

## Deep research — full-PDF read (2026-07-10)

> Đọc đối chiếu với bản **IEEE TASLP đã xuất bản** (DOI 10.1109/TASLPRO.2025.3648793; trường
> Comments của arXiv:2502.18186 ghi "This work has been published in IEEE Transactions on
> Audio, Speech and Language Processing"). PDF local = `pdfs/01-c2ser.pdf`, arXiv **v3** (29
> Dec 2025). Mục này thay thế khối "Analysis (overlap with Pebble)" đã cũ ở trên, vốn được
> chấm điểm dựa trên profile voice-MTL lưu trữ (D1–D7); mục này dùng profile **ViEmoSpeech**
> hiện hành + Decision Register (**V-A…V-H**). Chỉ bổ sung thêm (append-only); phần lịch sử
> ở trên giữ nguyên không đổi.

### Source-access note

- Trích xuất toàn văn bằng `pdftotext docs/papers/bimodal-ser/pdfs/01-c2ser.pdf` (1080 dòng).
  Đọc từ đầu đến cuối: abstract, §I–VII, Table I–IX, Fig 1–7, toàn bộ 56 tài liệu tham khảo.
- Đối chiếu qua web các con số trọng yếu với bản HTML arXiv (`arxiv.org/html/2502.18186v1`)
  và đối chiếu venue/DOI với trang abstract arXiv.
  - Query: *"C2SER Steering Language Model Stable Speech Emotion Recognition Contextual Perception
    Chain of Thought Emotion2Vec-S"* → dẫn tới `arxiv.org/abs/2502.18186`,
    `arxiv.org/html/2502.18186v1`, `github.com/zxzhao0/C2SER`, `huggingface.co/papers/2502.18186`.
  - Kiểm tra venue → `arxiv.org/abs/2502.18186`: Comments = "This work has been published in IEEE
    Transactions on Audio, Speech and Language Processing"; DOI liên quan `10.1109/TASLPRO.2025.3648793`.
- **Provenance conflict rule:** các số liệu ở bản HTML v1 cho Table V (Emotion2Vec-S) và Table VI/VII (C2SER)
  **khớp chính xác với bản PDF v3 local** (CASIA 62.95, Emo-Emilia 80.66/69.00, ESD 79.84, MELD 21.31,
  λ_utt=0.1, λ_cate=100, "Emotion2Vec-S is frozen"). Không có chênh lệch preprint/xuất-bản trên các số được trích dẫn.
  Code + checkpoint + tập test Emo-Emilia đều đã được công bố (`github.com/zxzhao0/C2SER`, HF collection).

### What the paper actually does

**Task/claim.** Một mô hình audio-language (ALM) cho **SER phân loại 7 lớp** (giận dữ, vui, trung
tính, buồn, ngạc nhiên, ghê tởm, sợ hãi) nhằm giảm lỗi "hallucination" của các ALM sinh (bịa lý do
không có căn cứ, ví dụ gán nhãn "buồn" cho một đoạn clip vui vẻ vì "có lẽ anh ấy đang chuẩn bị thi",
Fig 1). Đây **không phải** mô hình đa chiều (dimensional) — không có valence/arousal/distress,
không hồi quy, không CCC/Pearson ở bất kỳ đâu; chỉ số duy nhất là WA / UA / Macro-F1.

**Architecture (§III).** Hai bộ mã hóa nhận thức (perception encoder) đóng băng đưa vào một text
LLM:
- *Semantic* = bộ mã hóa **Whisper-medium** (2 lớp conv, downsample 2×, 24 lớp Transformer).
- *Acoustic* = **Emotion2Vec-S**, bản mở rộng của họ từ emotion2vec (backbone data2vec2.0), thêm
  một **loss tương phản cấp category** `L_Cate` (kiểu CLIP: các utterance cùng cảm xúc = cặp
  dương, khác cảm xúc = cặp âm, trên embedding toàn cục average-pooled G). Tổng loss
  **`L_e2v = L_Frm + λ_utt·L_Utt + λ_cate·L_Cate`** với **λ_utt=0.1, λ_cate=100** (Eq 2, §V-A). Động
  cơ: các loss utterance+frame của emotion2vec đều ở cấp *instance*, nên gây nhầm lẫn giữa các
  category giống nhau về mặt âm học (sợ hãi vs buồn); loss category kéo các category tách xa nhau.
- Một **connection module** gồm Transformer 4 lớp + linear (ffn dim 2560) chiếu cả hai luồng vào
  **Qwen2-7B-Instruct**, được fine-tune bằng **LoRA** (rank 8, α 32, dropout 0.1). Trong lúc huấn
  luyện C2SER, **Emotion2Vec-S bị đóng băng** (§V-A); đặc trưng Whisper cũng được dùng nguyên trạng.

**Chain-of-Thought + self-distillation (§III-C/D).**
- *Explicit CoT*: mô hình trước tiên sinh ra một lý giải (rationale) mô tả tốc độ nói / cao độ /
  năng lượng / transcript, rồi mới đến cảm xúc. Dữ liệu huấn luyện được xây dựng bằng cách (1) trích
  xuất F0 trung bình (PENN), độ to (pyloudnorm), tốc độ nói (âm vị/thời lượng); (2) **rời rạc hóa mỗi
  đặc trưng thành Thấp/Trung/Cao qua μ±σ** (heuristic theo Central-Limit-Theorem); (3) điền vào một
  template (Table I) rồi đưa vào **GLM-4-9B-Chat** để sinh lý giải bằng ngôn ngữ tự nhiên bám theo
  các nhãn đó + cảm xúc ground-truth.
- *Implicit CoT*: self-distillation từ đầu ra explicit sang đầu ra direct. Lịch tuyến tính theo
  batch — xác suất lấy mẫu một ví dụ explicit **giảm dần 1.0→0.0** qua giai đoạn này, nên đến cuối
  mô hình chỉ sinh ra mô tả cảm xúc ngắn (<10 token so với >40 của explicit), cắt giảm độ trễ ~10×
  và giảm tích lũy sai số.

**Data (§IV).** Huấn luyện trên 6 corpus công khai + một tập nội bộ ~439k utt = **672,668 utt /
1215.7 giờ** (Table II); tiếng Trung ≈ gấp 2 lần tiếng Anh; **neutral chiếm ≈ một nửa dữ liệu,
fear+disgust < 2%** (Fig 4). Nhãn silver cho dữ liệu nội bộ + Emilia qua **giao của Emotion2Vec
(speech) ∩ GLM-4-9B-Chat (text)** — một cổng đồng thuận hai-teacher. Tập test mới **Emo-Emilia**
(Table III): 1400 utt trong-điều-kiện-thực (in-the-wild), 100/cảm xúc × {CN,EN}, xây dựng bằng cùng
phép giao 2-teacher rồi **4 chuyên gia song ngữ chỉ giữ lại các mẫu được gán nhãn đồng thuận tuyệt
đối**. Việc đánh giá trải trên CASIA, M3ED (tiếng Quan Thoại), MELD, EmoV-DB (tiếng Anh), ESD,
ASVP-ESD, EMOVO (tiếng Ý), MESD (tiếng Mexico), Emo-Emilia (Table IV).

**Results — đặc trưng đóng băng Emotion2Vec-S (Table V; EmoBox 5-fold leave-one-session-out, linear
probe in-domain trên đặc trưng đóng băng — tức đúng là chế độ "backbone đóng băng + head huấn
luyện".)** Tất cả đều ✔ được đối chiếu xác nhận (HTML v1 = PDF v3):

| Dataset (lang) | WavLM-base UA | Emotion2Vec UA | **Emotion2Vec-S UA** |
|---|---|---|---|
| **CASIA (Mandarin, acted)** | 47.25 | 47.58 | **62.95** (F1 60.2) |
| Emo-Emilia (mix, in-wild) | 67.26 | 68.02 | **80.66** |
| ESD (mix, acted) | 72.90 | 70.22 | **79.84** |
| MESD (Mexican) | 42.58 | 50.56 | **59.57** |
| **M3ED (Mandarin, spontaneous)** | 22.76 | 22.04 | 23.82 (all ≈ chance) |
| **MELD (English, conversational)** | 23.44 | 23.20 | **21.31 (NOT best;** data2vec2.0 = 24.79) |
| EmoV-DB (English, acted) | **98.38** | 96.71 | 97.04 (WavLM wins) |

Emotion2Vec-S tốt nhất trên các tập tiếng Trung/đa ngôn ngữ/tiếng Mexico, ngang bằng-hoặc-kém hơn
trên hội thoại tiếng Anh. Mức tăng lớn nhất là ở **CASIA Mandarin: +15.4 UA so với WavLM, +15.4 so
với emotion2vec**.

**Results — ALM C2SER (Table VI–VIII; zero-shot cross-dataset trừ MELD/ESD in-domain).**
- Emo-Emilia: **C2SER-Implicit UA 69.00 / F1 61.61** so với Explicit 68.29/61.28 so với **Qwen2-Audio
  39.07/31.91** so với cascade chỉ-text (Whisper-m→Qwen2-7B) **63.31/60.89** (Table VI/VII). ✔
- **Chia theo register của cascade chỉ-text** (Table VI): CASIA (Mandarin acted) chỉ-text sụp xuống
  còn **13.93 UA** (≈ mức đoán ngẫu nhiên với 6 lớp) trong khi C2SER-Implicit đã fused = **53.33**;
  nhưng trên Emo-Emilia, cũng cascade chỉ-text đó đạt **63.31**. ✔ Nội dung mang thông tin cảm xúc
  trên speech trong-điều-kiện-thực, hầu như không mang gì trên tiếng Quan Thoại đã diễn (acted).
- **Ablation (Table VIII, Emo-Emilia):** full **69.00** → bỏ Emotion2Vec-S **57.93** (−11.1) → bỏ
  CoT **43.14** (−25.9) → bỏ Whisper **32.07** (−36.9, "không hội tụ được"). Kênh semantic là thành
  phần đơn lẻ mang trọng lượng lớn nhất. ✔
- Fine-tune in-domain giúp ích rất nhiều (Table IX, MELD): 0-epoch UA 38.66 → 3-epoch 43.50 →
  6-epoch 49.30. ✔
- **Sụp đổ ở lớp hiếm (rare-class collapse):** trên Emo-Emilia, các lớp anger/happiness/neutral/
  sadness/surprise đều đạt >90% độ chính xác theo category nhưng **disgust và fear < 20%** (Fig 7),
  được lý giải là do tỷ lệ <2% trong dữ liệu huấn luyện. ✔

**Tone:** từ "tone" chỉ xuất hiện **duy nhất** với nghĩa ngữ điệu paralinguistic ("low-pitched
tone", ví dụ ở Table I). Hai corpus tiếng Quan Thoại (CASIA, M3ED) được sử dụng và CASIA cho mức
tăng đơn lẻ lớn nhất, nhưng **thanh điệu từ vựng (lexical tone) không bao giờ được coi là một biến
hay yếu tố gây nhiễu** — đã kiểm chứng: "tone" = chỉ mang nghĩa mô tả cao độ (đối chiếu qua bản
HTML arXiv). Đặc trưng cao độ đưa vào CoT là **F0 trung bình rời rạc hóa thành Thấp/Trung/Cao**,
không có chuẩn hóa thanh điệu.

### Parts directly useful for ViEmoSpeech (tagged by Decision ID)

1. **[V-B] Emotion2Vec-S như một audio-branch drop-in đóng băng — kèm một lưu ý về register.**
   Checkpoint đã công bố + Table V cho một phép so sánh kiểu "đặc trưng đóng băng + head huấn
   luyện" tương đồng-đối-tương-đồng (EmoBox 5-fold), *chính xác* là chế độ của audio-branch chúng
   ta. Điểm nổi bật: UA CASIA Mandarin **62.95 so với 47.25 WavLM / 47.58 emotion2vec** (✔). Cơ chế
   là một số hạng loss được thêm vào duy nhất (`λ_cate=100·L_Cate`, Eq 2) để tách các category dễ
   nhầm lẫn — không đổi kiến trúc, không fine-tune. **Rủi ro chuyển giao (có thật):** mọi mức tăng
   lớn đều nằm trên các tập **acted / clean** (CASIA, ESD, Emo-Emilia đã lọc qua chuyên gia); trên
   **M3ED (tiếng Quan Thoại *tự phát/spontaneous*)** — register gần nhất với TV drama VN của chúng
   ta — Emotion2Vec-S (23.82) nằm trong biên độ nhiễu so với WavLM (22.76) và gần mức đoán ngẫu
   nhiên, còn trên **MELD hội thoại tiếng Anh** nó *kém hơn* data2vec2.0/WavLM. Vậy checkpoint này
   là một lựa chọn mặc định hợp lý, nhưng phép A/B phải chạy trên chính các clip VN tự phát của
   chúng ta, không được giả định trước.

2. **[V-A] Fusion Whisper-semantic + Emotion2Vec-S-acoustic + CoT như một template bimodal.** Đây
   là một thiết kế cụ thể vượt qua cascade chỉ-text: bảng ablation Table VIII cho thấy *cả hai*
   luồng đều cần thiết (−11 khi thiếu acoustic, −37 khi thiếu semantic), và mô hình đã fused vượt
   qua cascade Whisper→Qwen2 trên các tập mà acoustic chiếm ưu thế. **Rủi ro chuyển giao (lớn):**
   phần "fusion" của họ nằm *bên trong một LLM 7B với LoRA* (Qwen2-7B) được điều khiển bằng sinh
   văn bản CoT — nặng hơn nhiều bậc so với head học-fusion nhẹ mà chúng ta nhắm tới trên nền
   PhoWhisper+PhoBERT, và kênh semantic của họ là đặc trưng *encoder* của Whisper, không phải
   *token* ASR. Đây là một **template cho việc nên fuse cái gì và một bằng chứng tồn tại rằng
   acoustic+semantic > từng phần riêng lẻ**, không phải một module có thể sao chép trực tiếp.

3. **[V-C] Kênh text dưới ASR: một sự sụp đổ phụ thuộc register, đã được định lượng.** Cascade
   Whisper-m→Qwen2-7B là "nhánh text chỉ-transcript-ASR" của chính paper. Nó dao động từ
   **63.31 UA (Emo-Emilia, in-wild)** xuống **13.93 UA (CASIA, acted Mandarin)** (Table VI, ✔). Với
   ViEmoSpeech (TV drama đã diễn, register gần với tiếng Quan Thoại về mặt tonal), điều này dự báo
   nhánh text PhoWhisper của chúng ta sẽ mang **rất ít** thông tin trên các lượt lời cường độ cao
   đã diễn (acted) — chính là những lượt lời mà PhoWhisper mắc lỗi hoán đổi thanh điệu (mày→máy).
   **Rủi ro chuyển giao:** cascade này loại bỏ paralinguistics theo thiết kế (đó chính là mục đích
   của nó), và CoT *đưa transcript vào thẳng phần lý giải*, nên một token ASR sai sẽ lan truyền
   thành một lý do sai — đây chính là lý do họ thêm **self-distillation explicit→implicit** (xác
   suất theo batch 1.0→0.0) để giảm tích lũy sai số. Kỹ thuật self-distillation đó chính là cơ chế
   V-C có thể chuyển giao cho một kênh text nhiễu.

4. **[V-B/V-E] Công thức đặc trưng đóng băng có thể tái sử dụng + cảnh báo về lớp hiếm.** Cấu hình
   huấn luyện Emotion2Vec-S (Adam, lr 7.5e-5, wd 1e-2, cosine, warmup 5%, grad-accum 2, classifier =
   3 lớp FC, backbone/số chiều giống hệt emotion2vec) là một phương án sẵn dùng cho bake-off
   audio-branch của chúng ta. Và tỷ lệ **disgust/fear < 20%** ở Fig 7, trong khi tổng thể đạt 69%,
   xuất phát từ tỷ lệ <2% trong dữ liệu huấn luyện, là một cảnh báo trực tiếp về lớp hiếm cho scheme
   7 lớp của chúng ta + sàn ≥50-clip (ADR-002).

### How each part helps ViEmoSpeech succeed

- **[V-B] Bake-off audio-branch có thêm ứng viên thứ ba + một giả thuyết.** Thêm **Emotion2Vec-S**
  như một nhánh cạnh WavLM và emotion2vec trong probe đặc trưng đóng băng, đánh giá bằng giao thức
  speaker-disjoint + whole-series-holdout của chúng ta (V-G). **Giả thuyết đăng ký trước**, rút ra
  từ chính mẫu hình của Table V: Emotion2Vec-S thắng trên *acted/clean* và hòa trên *spontaneous* —
  vậy nếu nó thắng trên các clip TV drama VN của chúng ta (vốn đã diễn nhưng ồn), đó là một kết quả
  thật sự; nếu nó chỉ hòa (kiểu M3ED), chúng ta giữ WavLM (mặc định vn-12/bimodal-12 hiện tại). Dù
  theo hướng nào, mức tăng +15 điểm trên CASIA vẫn là căn cứ để thử nghiệm.
- **[V-A] Phạm vi thí nghiệm fusion + bậc thang baseline.** Áp dụng *hình dạng* thiết kế — hai
  luồng đóng băng (audio = Emotion2Vec-S/WavLM, semantic = PhoBERT-over-PhoWhisper) đưa vào một
  head học-fusion nhẹ — và mượn nguyên **lưới ablation** của C2SER (full / −audio / −semantic /
  −fusion) làm bảng ablation của riêng chúng ta để tuyên bố "cần cả hai modality" được đo lường,
  chứ không chỉ khẳng định suông. Kết quả −37 điểm khi bỏ Whisper của họ là luận cứ cho việc nhánh
  semantic không phải là tùy chọn, kể cả trên speech có tính tonal.
- **[V-C] Xây một slice xung đột/cường độ-cao + neo bằng audio.** Vì kênh text sụp đổ trên speech
  tonal đã diễn (CASIA 13.93), việc huấn luyện của chúng ta không được để một PhoBERT mạnh lấn át:
  duy trì một **slice cường độ-cao / lỗi hoán-đổi-thanh-điệu ASR** trong eval, và cân nhắc một
  **head phụ chỉ-audio** hoặc modality dropout (theo cơ chế bảo vệ của vn-12) để fusion không thoái
  hóa thành chỉ-text. Báo cáo số liệu độc lập của nhánh text trên *cả hai* nhánh — caption sạch và
  transcript PhoWhisper — để định lượng trực tiếp khoảng cách do ASR gây ra (C2SER chưa bao giờ
  chạy thí nghiệm này trên ASR tonal — đây là khoảng trống chúng ta có thể chiếm lĩnh).
- **[V-B/V-E] Sàn lớp hiếm được biện minh bằng thực nghiệm.** Trích dẫn Fig 7 (disgust/fear <20% khi
  tổng thể đạt 69%) như bằng chứng bên ngoài rằng một scheme 7 lớp với đuôi <2% sẽ sụp đổ ở phần
  đuôi — làm căn cứ cho sàn ≥50-clip, lấy mẫu cân bằng theo lớp, và báo cáo theo từng lớp (không chỉ
  macro) của chúng ta.

### Vietnamese SER transfer lens (frozen backbone · PhoWhisper ASR · tone×emotion · acted proxy)

- **Độ phù hợp với backbone đóng băng là thật.** Table V là một probe đặc trưng-đóng-băng +
  head-huấn-luyện, và Emotion2Vec-S vẫn đóng băng bên trong C2SER — cả hai đều khớp với thiết kế
  encoder-đóng-băng không thể thương lượng của chúng ta. Checkpoint Emotion2Vec-S được công bố mở,
  nên phép A/B ở V-B không tốn chi phí huấn luyện backbone.
- **Bằng chứng về ngôn ngữ có thanh điệu hiện diện nhưng "mù" thanh điệu.** Mức tăng lớn nhất
  (CASIA Mandarin) và một tập tiếng Quan Thoại thứ hai (M3ED) được sử dụng, nhưng paper không bao
  giờ coi thanh điệu từ vựng là một biến số; đầu mối cao độ cho cảm xúc của họ là F0 trung bình thô
  → Thấp/Trung/Cao. Theo **vn-13 (Chang PLOS ONE)**, F0 chính xác là kênh mà thanh điệu và cảm xúc
  tương tác (F0-mean χ²(12)=70.18, F0-range χ²(12)=114.64, cả hai p<.001), nên việc dùng F0 làm đầu
  mối cảm xúc của C2SER *bị nhiễm thanh điệu ngay từ thiết kế* — với tiếng Việt (6 thanh nặng về
  phonation, vn-06) mức độ nhiễm còn gấp đôi. Đây là **khoảng trống cho V-D**: Emotion2Vec-S mã hóa
  audio tonal như một hộp đen không có sự tách bạch thanh điệu/cảm xúc, và không paper nào trong bộ
  sưu tập (kể cả C2SER) đo lường sự tương tác này trên thanh điệu từ vựng. Tuyên bố tone×emotion
  của chúng ta không bị ảnh hưởng bởi SoTA bimodal mạnh này.
- **Register đã diễn (acted) là một sự tương đồng hai mặt.** ViEmoSpeech là TV drama đã diễn;
  những chiến thắng lớn nhất của C2SER cũng nằm trên các corpus acted (CASIA/ESD) — điều đáng
  khích lệ. Nhưng tập tự phát (M3ED) cho thấy mức tăng gần như biến mất, và kênh text của họ sụp đổ
  trên speech đã diễn — nên "acted" là con dao hai lưỡi với chúng ta.
- **Không có distress / không có đầu ra đa chiều.** C2SER thuần túy là phân loại 7 lớp: nó **không
  đóng góp gì** cho các head valence/arousal (CCC) hay distress-recall-floor (V-F) của chúng ta.
  Không nên trích dẫn nó cho các mục đích đó.
- **Dòng dõi silver-label đáng học hỏi (biên giới V-E).** Việc giao hai teacher của họ
  (Emotion2Vec ∩ GLM-4-9B) rồi lọc **4-chuyên-gia-đồng-thuận-tuyệt-đối** cho Emo-Emilia là một mẫu
  hình weak-rồi-human sạch sẽ — nhưng lưu ý theo **ADR-003**, các LLM teacher của chúng ta chỉ *gợi
  ý trên màn hình*, nên chúng ta chỉ nên áp dụng nửa phần con-người-phán-quyết, không áp dụng phần
  giao-của-máy-làm-nhãn.

### Limitations & open questions for ViEmoSpeech

- **Mâu thuẫn với luận điểm cốt lõi của ViEmoSpeech (và điều hòa vn-08 ↔ vn-12).** Luận điểm cho
  method paper của chúng ta là *vì thanh điệu tiếng Việt nặng về phonation nên nhánh
  semantic/text phải mang trọng lượng lớn hơn so với SER phi tonal*. Cascade chỉ-text của chính
  C2SER lại nói điều ngược lại đối với speech tonal **đã diễn**: **CASIA Mandarin chỉ-text = 13.93
  UA (gần mức đoán ngẫu nhiên)** — trên speech tonal đã diễn, kênh semantic gần như không mang gì
  và **acoustic chiếm ưu thế**. Tuy nhiên trên speech **trong-điều-kiện-thực**, cùng cascade đó đạt
  **63.31**. Điều này điều hòa được nhận định "text gần như vô dụng (38.7–44.1%)" của vn-08 với
  nhận định "semantics chiếm ưu thế" của vn-12: *mức độ nội dung mang thông tin cảm xúc phụ thuộc
  vào register*, cao trên speech tự nhiên giàu nội dung, thấp trên các câu cảm thán ngắn đã diễn.
  Hệ quả trực tiếp: trên TV drama VN đã diễn của chúng ta, nhánh text có thể hoạt động kém đúng ở
  những chỗ lỗi hoán-đổi-thanh-điệu ASR tập trung (cường độ cao), nên luận điểm "text mang trọng
  lượng lớn hơn" cần được diễn đạt lại thành "text mang trọng lượng lớn hơn *khi có nội dung để
  mang*, và tuyên bố cạnh tranh tone×emotion của chúng ta là một tuyên bố về *kênh acoustic*, không
  phải một tuyên bố dựa vào text." Phải đối mặt trực diện với điều này trong method paper.
- **F0 làm đầu mối cảm xúc, đối chiếu với vn-13.** C2SER rời rạc hóa F0 trung bình làm đặc trưng
  cảm xúc mà không kiểm soát thanh điệu; vn-13 cho thấy F0 là kênh dùng chung với thanh điệu. Bất
  kỳ hệ thống VN nào sao chép điều này một cách thiếu phê phán sẽ làm lẫn lộn thanh điệu và cảm
  xúc. Nhánh audio của chúng ta nên ưu tiên biên độ/năng lượng + thời lượng thay vào đó (theo
  vn-13: các kênh mang cảm xúc độc lập với thanh điệu) và coi các đặc trưng F0 là đã bị nhiễm
  thanh điệu.
- **Nhầm lẫn giữa zero-shot và in-domain trong các bảng.** Table V (Emotion2Vec-S) là in-domain
  5-fold; Table VI (C2SER) chủ yếu là zero-shot cross-dataset — nên con số 69.00 của C2SER và
  80.66 của Emotion2Vec-S trên Emo-Emilia *không phải* cùng một thí nghiệm. Với thiết kế của chúng
  ta (đặc trưng đóng băng + head huấn luyện), **Table V mới là phép so sánh liên quan**, không
  phải các con số của ALM C2SER.
- **Sụp đổ ở lớp hiếm vẫn tồn tại kể cả ở mức SoTA** (disgust/fear <20%, Fig 7) — một lời cảnh báo
  rằng phần đuôi của scheme 7-lớp của chúng ta sẽ không được cứu chỉ bằng một backbone tốt hơn; cần
  thiết kế lấy mẫu/loss (V-E/V-F).
- **Nặng, sinh (generative), không phải turn-level.** C2SER là một ALM LoRA 7B sinh văn bản tự do,
  sau đó được ánh xạ sang nhãn bởi *một mô hình khác* 14B (Qwen2.5-14B) — không phải một bộ phân
  loại nhẹ ở cấp turn-level. Công thức fusion của nó là một template, không phải một module có thể
  triển khai trực tiếp cho pipeline của chúng ta.
- **Câu hỏi mở đáng làm một thí nghiệm:** chạy các đặc trưng đóng băng Emotion2Vec-S đã công bố qua
  một probe theo-tầng (layer-wise) thanh-điệu-so-với-arousal (giao thức Shen/vn-06) trên âm tiết
  tiếng Việt — liệu loss tương phản cấp-category giúp cảm xúc tiếng Quan Thoại có làm *quyện lẫn*
  thanh điệu, hay để nó tách biệt được? Câu trả lời đó sẽ quyết định Emotion2Vec-S giúp ích hay gây
  hại cho mục tiêu tách bạch V-D của chúng ta.
