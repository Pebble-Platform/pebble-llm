# Bài báo 24 — MMER: Multimodal Multi-task Learning for Speech Emotion Recognition

## 1. Thông tin thư mục

**Tiêu đề:** MMER: Multimodal Multi-task Learning for Speech Emotion Recognition

**Tác giả:** Sreyan Ghosh, Utkarsh Tyagi, S Ramaneswaran, Harshvardhan Srivastava, Dinesh Manocha (University of Maryland, College Park; NVIDIA, Bangalore; IIT Delhi).

**Năm / hội nghị:** Interspeech 2023 (ISCA), `ghosh23b_interspeech`. Bản preprint: arXiv:2203.16794 (v5, 3 Jun 2023). Tiêu đề arXiv ban đầu là "MMER: Multimodal Multi-task learning for Emotion Recognition in Spoken Utterances"; tiêu đề bản xuất bản tại Interspeech là tiêu đề ở trên.

**Từ khóa (nguyên văn):** "speech emotion recognition, human-computer interaction".

**Mã nguồn:** https://github.com/Sreyan88/MMER

## 2. Vì sao bài báo này nằm trong tập tài liệu của Pebble

Pebble v1 là một encoder chỉ-văn-bản (NeoBERT) chấm điểm văn bản sức khỏe tâm thần của trẻ em ở
mức turn-level. Luận án dành riêng một phần **mở rộng modality tin nhắn thoại (voice-message)**:
trẻ em ngày càng tương tác bằng voice note, và sắc thái cảm xúc được truyền tải bởi prosody (cao
độ, năng lượng, nhịp điệu) nhiều ngang với từ ngữ. MMER là công thức được xuất bản gọn gàng nhất
cho việc **hợp nhất (fuse) acoustic + text vào một bộ phân loại cảm xúc duy nhất**, và — quan trọng
hơn — nó là **multi-task**, đúng chính là kiến trúc của Pebble (encoder dùng chung, nhiều head).
Do đó MMER là thiết kế tham chiếu cho câu hỏi "head cảm xúc của Pebble trông như thế nào một khi đã
có kênh thoại, và audio sẵn có bên cạnh bản phiên âm ASR mà Pebble đằng nào cũng cần?"

Nó cũng là một mốc cảnh báo: các con số của MMER đến từ **giọng nói diễn xuất của người lớn trong
studio (IEMOCAP)**, năm cảm xúc dạng phân loại (categorical), ở mức utterance-level. Không điều kiện
nào trong số đó đúng với Pebble (giọng nói tự phát của trẻ em, không gian 12-nhãn GoEmotions,
turn-level, audio thực tế ngoài đời). Phần đọc sâu bên dưới tách biệt phần kiến trúc có thể chuyển
giao khỏi phần benchmark không thể chuyển giao.

---

## Deep research — full-PDF read (2026-06-16)

### Ghi chú về truy cập nguồn

File PDF cục bộ `pdfs/24-mmer-multimodal-mtl-ser.pdf` đã được đọc trọn vẹn từ đầu đến cuối bằng
`pdftotext` (công cụ Read không hiển thị được PDF). File cục bộ là arXiv:2203.16794 **v5**
(3 Jun 2023). Mọi con số mang tính then chốt sau đó được đối chiếu chéo với **bản xuất bản tại
Interspeech 2023** (ISCA Archive `ghosh23b_interspeech.pdf`), được tải xuống và trích xuất trực
tiếp bằng `pdftotext` — bởi vì mô hình tóm tắt của WebFetch đã bịa ra bảng số liệu (nó trả về
WA 72.98% / 39M params / batch 16 / LR 1e-4, không con số nào trong số đó xuất hiện trong bất kỳ
PDF nào). Việc trích xuất văn bản trực tiếp từ PDF đã xuất bản là nguồn có thẩm quyền và **khớp
nguyên văn với arXiv v5 cục bộ** trên tất cả các con số chính.

Vết xác thực (validation traces):
- Tìm kiếm "MMER Multimodal Multi-task Learning Speech Emotion Recognition Ghosh Interspeech 2023 IEMOCAP" → dẫn tới `https://www.isca-archive.org/interspeech_2023/ghosh23b_interspeech.html` (xác nhận abstract, tác giả, hội nghị) và `.../ghosh23b_interspeech.pdf` (bảng đầy đủ).
- `pdftotext` grep trên PDF đã xuất bản xác nhận: MMER WA **81.2%**, **228M** params, **75.0%** WA với bản phiên âm Google ASR, các baseline RoBERTa **78.1%** / wav2vec-2.0 **78.9%** / naive multimodal **79.8%**, hyper-params batch 4 / accum-grad 4 / 100 epochs / LR 1e-5 / α,β,γ=0.1.
- Quy tắc xung đột: ở đây bản xuất bản == bản preprint v5, nên không có chênh lệch (delta). Các phiên bản arXiv cũ hơn dùng tiêu đề khác và một khung augmented-contrastive bổ sung, nhưng v5/bản xuất bản đã được căn chỉnh thống nhất.

Nhãn trạng thái bên dưới: ✔ đã đối chứng (có trong cả PDF cục bộ + bản xuất bản) / ≈ xấp xỉ / ✖ chưa đối chứng.

### Bài báo thực sự làm gì

**Mục tiêu.** Speech Emotion Recognition (SER): gán một trong *j* cảm xúc dạng phân loại cho một
utterance nói `u_i = (a_i, t_i)` trong đó `a_i` là audio thô và `t_i` là bản phiên âm (ASR hoặc do
người tạo). Luận điểm của MMER: text giờ đây là một tín hiệu bổ trợ rẻ (ASR đã gần tối ưu), và SER
hưởng lợi nhiều nhất từ **các tác vụ phụ trợ (auxiliary task) bơm thêm tri thức** vào một encoder
dùng chung.

**Kiến trúc — Multimodal Dynamic Fusion Network (MDFN).** Hai bộ trích đặc trưng SSL bị đóng băng
(frozen) đưa dữ liệu vào một module tương tác cross-modal được học:
- **Acoustic encoder:** `wav2vec-2.0-base`, checkpoint của Facebook pre-trained trên 960h LibriSpeech. Xuất ra `e^a_i ∈ R^{J×768}` (frame với stride 20ms / hop 25ms; J phụ thuộc độ dài audio). ✔
- **Text encoder:** `RoBERTa-BASE` từ HuggingFace, dùng **làm bộ trích đặc trưng bị đóng băng — KHÔNG fine-tune**. Xuất ra `e^t_i ∈ R^{M×768}` cho M token. ✔ (Đây là một lựa chọn thiết kế đáng chú ý: chỉ module fusion + nhánh acoustic được huấn luyện.)
- `d = 768` cho cả hai (kiến trúc base). ✔

**Multimodal Interaction Module (MMI).** Ba khối Cross-Modal Encoder (CME) (B, C, D), mỗi khối là
một transformer layer với cross-modal attention (CMA) h-head, residual + feed-forward, cộng với một
acoustic gate E:
- **Khối B** — `CMA(A, T)`: acoustic embeddings A làm query, RoBERTa T làm key/value → tạo ra P (token reps được điều kiện hóa bởi speech). Eq. (1): `CMA(A,T)=softmax([W_q A]·[W_k T]/√(d/m))[W_v T]`.
- **Khối C** — đưa P trở lại với T gốc làm query, P làm key/value → **Speech-Aware Word Representations** R.
- **Khối D** — T làm query, A làm key/value → **Word-Aware Speech Representations** Q (căn chỉnh word-to-frame).
- **Acoustic gate E** (Eq. 2): `g = σ(W_g[R;Q] + B_g)`, rồi `Q = g·Q` — một sigmoid gate triệt tiêu động các frame speech dư thừa/nhiễu.
- MMI rep cuối `M = [Q; R] ∈ R^{2d}`, được chiếu xuống (down-project) về d bởi linear `l(·)`. ✔

**Bốn tác vụ được tối ưu đồng thời** (tổng loss `L = L_CE + α·L_CTC + β·L_SCL + γ·L_ACL`): ✔
1. **Cross-Entropy (L_CE)** — mục tiêu SER. Embedding cuối = concat của max-pool wav2vec-2.0 reps `mp(A)` và MMI reps `mp(M)` → linear + softmax trên 4 lớp cảm xúc (Eq. 3).
2. **CTC loss (L_CTC)** — một **tác vụ phụ trợ ASR**: chiếu linear các A chưa pool → character logits, CTC so với bản phiên âm đã viết hoa và loại bỏ dấu câu. Buộc mô hình học được sự căn chỉnh đơn điệu (monotonic) speech↔text và cấu trúc ngôn ngữ.
3. **Supervised Contrastive Learning (L_SCL)** — instance discrimination trên MMI reps M sử dụng nhãn cảm xúc: các instance cùng cảm xúc là positive, khác cảm xúc là negative (Algorithm 1). Làm sắc nét các đặc trưng phân biệt cảm xúc.
4. **Augmented Contrastive Learning (L_ACL / "AGL")** — tác vụ robustness/invariance: text được **back-translate** (augmentation giữ ngữ nghĩa), sau đó được **tổng hợp lại thành speech qua zero-shot speaker-conditioned TTS (YourTTS)** được điều kiện hóa trên một speaker *khác* thể hiện một cảm xúc *tương tự*. Contrastive loss giữa reps multimodal gốc và đã augment → ép buộc các đặc trưng cảm xúc bất biến với speaker và bất biến về ngữ nghĩa.

**Dataset — IEMOCAP.** ~12 giờ speech, 10 speaker, 5 phiên kịch bản dyadic, do diễn viên chuyên
nghiệp diễn. Thiết lập 4-lớp chuẩn: Happy, Angry, Neutral, Sad, Excited → **Excited gộp vào Happy**
(nên thực tế là 4 lớp). Đánh giá = **5-fold leave-one-session-out cross-validation**, lấy trung bình
**weighted accuracy (WA)** qua các fold. ✔

**Hyper-parameters.** batch size **4**, accum-grad **4** (effective batch 16), **100 epochs**, LR
giữ cố định ở **1e-5**, ngụ ý AdamW. `α=β=γ=0.1`, grid-search trên `{1, 0.1, 0.01, 0.001}`.
Mỗi bước ~10 phút trên một **A100**. **MMER = 228M tham số.** ✔

**Kết quả — Table 1 (IEMOCAP, WA, 5-fold CV):** ✔
| Hệ thống | Modality | WA |
|---|---|---|
| Cai et al. [1] (SOTA trước, re-implement 5-fold) | {a,t} | 77.1% |
| Yang et al. [39] | {a,t} | 77.7% |
| Morais et al. [2] (gần nhất; 2× speech encoder, >2× params) | {a,t} | 77.4% |
| **Baseline** RoBERTa-BASE | {t} | **78.1%** |
| **Baseline** wav2vec-2.0 | {a} | **78.9%** |
| **Baseline** naive multimodal (concat pooled reps) | {a,t} | **79.8%** |
| **MMER w/o CTC** | {a,t} | **78.1%** |
| **MMER w/o SCL** | {a,t} | **78.9%** |
| **MMER w/o ACL** | {a,t} | **79.8%** |
| **MMER (đầy đủ)** | {a,t} | **81.2%** |

(Lưu ý: các baseline unimodal/naive của chính tác giả ở mức 78–80% đã vượt prior-art được trích dẫn
77.1% — một phần do công thức huấn luyện mạnh hơn, một phần do các con số prior đến từ tài liệu với
các fold CV khác nhau; chỉ Cai et al. được chạy lại dưới 5-fold CV khớp.)

**Robustness với ASR.** Với **bản phiên âm Google ASR thay cho bản gold tại inference, WA = 75.0%**
(giảm ~6.2 điểm so với 81.2%) — ✔, con số liên quan đến Pebble nhất, bởi vì Pebble sẽ không bao giờ
có bản phiên âm gold cho voice note của trẻ em.

**Đọc ablation (Table 1 + ma trận nhầm lẫn Fig. 2).** Loại bỏ từng tác vụ phụ trợ làm giảm WA:
−3.1 (CTC, 81.2→78.1), −2.3 (SCL, →78.9), −1.4 (ACL, →79.8). Vậy **CTC/ASR là tác vụ phụ trợ giá
trị nhất; ACL ít giá trị nhất** — nhưng ACL có một tác động định tính riêng biệt: Fig. 2 cho thấy
**ACL giảm bớt bias về lớp neutral** (một failure mode đã biết của SER), trong khi **CTC khuếch đại
nhẹ bias neutral** (mô hình dựa vào tín hiệu ngữ nghĩa/text và đánh giá thấp các tín hiệu speech).
SCL nằm ở giữa.

**Hạn chế được nêu.** (1) Contrastive learning cần **batch size lớn** (khó vì chi phí bộ nhớ của
audio). (2) **Đặc trưng text được tính trước (pre-computed)** (RoBERTa bị đóng băng) — nhánh text
không thể thích nghi với tác vụ cảm xúc.

### Các phần trực tiếp hữu ích cho Pebble (mỗi phần gắn với Decision ID)

1. **RoBERTa đóng băng làm bộ trích đặc trưng + module fusion được huấn luyện** — MMER chỉ fine-tune
   nhánh acoustic và module cross-modal; text encoder bị đóng băng. **(D-A, D-E)** Đối với phần mở
   rộng thoại của Pebble, đây là hình thái tích hợp rẻ nhất: giữ **encoder cảm xúc NeoBERT đã được
   huấn luyện ở trạng thái đóng băng**, thêm một nhánh acoustic wav2vec-2.0 + một module fusion
   cross-modal nhỏ, và chỉ huấn luyện các tham số mới. NeoBERT *chính là* "RoBERTa ở đây" của Pebble.
   Đây là một warm-start theo giai đoạn: head text được huấn luyện trước (v1), audio được gắn vào
   sau mà không làm xáo trộn nó. **Rủi ro chuyển giao:** MMER đóng băng RoBERTa vì IEMOCAP nhỏ
   (~12h); trên một corpus audio lớn hơn của Pebble, đồng thời fine-tune text encoder có thể có ích —
   đóng băng là cấu hình *khởi đầu* an toàn, không nhất thiết là trần (ceiling).

2. **CTC/ASR là tác vụ phụ trợ multi-task chủ đạo (−3.1 WA khi loại bỏ)** — **(D-B)** Đây là bằng
   chứng trực tiếp cho thiết kế MTL của Pebble: một **tác vụ phụ trợ neo biểu diễn dùng chung vào sự
   căn chỉnh speech↔text** đáng giá hơn các thủ thuật contrastive. Với Pebble, phép tương tự khi có
   audio là một **head phụ trợ CTC/ASR trên nhánh acoustic**, được giữ bật trong quá trình huấn
   luyện cảm xúc. **Rủi ro chuyển giao:** lợi ích lớn nhất chính xác vì text là modality mạnh cho
   cảm xúc; nếu bản phiên âm của người dùng thoại của Pebble là child ASR nhiễu, tác vụ phụ trợ có
   thể thay vào đó bơm nhiễu vào — xem điểm 5.

3. **Trọng số loss tĩnh α=β=γ=0.1, grid-search trên {1,0.1,0.01,0.001}** — **(D-B)** MMER đạt SOTA
   với **trọng số λ tĩnh đơn giản**, không phải GradNorm/PCGrad/Nash. Toàn bộ không gian tìm kiếm là
   một scalar dùng chung cho mỗi auxiliary loss. **Rủi ro chuyển giao:** MMER có 4 tác vụ trên một
   dataset không có mất cân bằng lớp nghiêm trọng ngoài bias-neutral; MTL của Pebble đối mặt với mất
   cân bằng nhãn thực sự (high-severity hiếm) và các head không đồng nhất (regression + softmax), nơi
   một λ tĩnh duy nhất có thể không đủ — bài báo này ủng hộ việc *thử static-λ trước* (baseline rẻ)
   trước khi với tới LibMTL, không phải rằng static λ luôn đủ.

4. **Acoustic gate `g = σ(W_g[R;Q]+B_g)` (Eq. 2)** — **(D-A)** Một sigmoid gate một dòng làm giảm
   trọng số các frame speech dư thừa/nhiễu trước khi fusion. **(D-G liền kề)** Đối với audio trẻ em
   ngoài đời của Pebble (tiếng ồn nền, chất lượng mic, clip ngắn), một gate độ tin cậy frame tường
   minh là một primitive robustness rẻ có thể tái sử dụng trực tiếp trong module fusion.

5. **Inference với bản phiên âm Google ASR: WA 75.0% so với 81.2% gold (−6.2)** — **(D-D, D-H)** Cái
   giá trung thực của việc không có bản phiên âm gold. Pebble sẽ *chỉ luôn* có bản phiên âm ASR cho
   voice note, nên **75.0% là baseline chuyển giao thực tế hơn 81.2%.** **(D-H)** Đây là con số để
   neo kỳ vọng cho phần mở rộng thoại của Pebble và để thúc đẩy huấn luyện robustness-với-ASR (ví dụ,
   huấn luyện trên bản phiên âm ASR, không phải gold, để thu hẹp khoảng cách train/test).

6. **Augmentation back-translation + speaker-conditioned-TTS (ACL) giảm bias lớp neutral** —
   **(D-B, D-H)** Pipeline augmentation (BT cho bất biến ngữ nghĩa, YourTTS re-synthesis cho bất biến
   speaker) là một **công thức data-augmentation cụ thể cho một head cảm xúc audio**, và lợi ích định
   tính nằm cụ thể ở **lớp majority/neutral** — phép tương tự của mất cân bằng cảm xúc chủ đạo của
   Pebble. **Rủi ro chuyển giao:** speech trẻ em "cảm xúc" tổng hợp bằng TTS bản thân nó là một bài
   toán generation khó, chưa được kiểm chứng đầy đủ; đây là ý tưởng v2+, không phải v1.

### Mỗi phần giúp Pebble thành công như thế nào

- **Thiết kế head tin nhắn thoại (điểm 1).** Artifact cụ thể: một module `pebble/models/audio_fusion.py`
  nhận (NeoBERT token embeddings đóng băng, wav2vec-2.0 frame embeddings) → 2–3 khối cross-modal
  attention → gated concat → các head emotion/severity hiện có. Chỉ huấn luyện tham số fusion +
  acoustic. Đây là cách tối thiểu, theo giai đoạn để thêm thoại mà không phải huấn luyện lại v1.
- **Chọn tác vụ phụ trợ (điểm 2).** Khi Pebble chạy ablation MTL, **thêm CTC/ASR làm head phụ trợ
  ứng viên cho nhánh audio** và kỳ vọng nó là giá trị nhất — −3.1 WA của MMER là prior. Lên ngân
  sách cho thí nghiệm: emotion-only so với emotion+CTC so với emotion+CTC+SCL.
- **Thí nghiệm cân bằng loss (điểm 3).** Chạy **baseline static-λ trước** (một scalar dùng chung mỗi
  auxiliary, grid `{1,0.1,0.01,0.001}`) trước các phương pháp LibMTL; MMER cho thấy SOTA có thể đạt
  được ở đó, nên đó là control đúng để vượt qua — không phải để bỏ qua.
- **Gate robustness (điểm 4, 5).** Thêm acoustic gate vào module fusion, và **đánh giá head thoại
  trên bản phiên âm ASR, không bao giờ trên gold** — báo cáo khoảng cách ASR-vs-gold như MMER đã làm
  (−6.2 WA của họ là tiền lệ cho thấy khoảng cách này phải được đo, không được giả định bỏ qua).
- **Giảm thiểu mất cân bằng / bias-neutral (điểm 6).** Coi pipeline BT+TTS là một thí nghiệm
  augmentation v2 nhắm cụ thể vào lớp cảm xúc chủ đạo của Pebble, và kiểm tra ma trận nhầm lẫn
  theo từng lớp (không chỉ accuracy tổng hợp) để xác nhận nó giúp các cảm xúc thiểu số.

### Lăng kính sức khỏe tâm thần trẻ em

- **Sự phù hợp về modality là thật, sự phù hợp về benchmark thì không.** *Kiến trúc* (fuse acoustic
  + ASR text, multi-task, gate các frame nhiễu) chuyển giao gọn gàng sang use case voice-note của
  Pebble. *Bằng chứng* thì không: IEMOCAP là **giọng nói diễn xuất của người lớn trong studio, 4 cảm
  xúc đã gộp, tương đối cân bằng, mức utterance-level**. Pebble nhắm tới **giọng nói tự phát của trẻ
  em, không gian 12-nhãn map-GoEmotions, mất cân bằng nghiêm trọng, turn-level giữa cuộc trò chuyện,
  audio thực tế ngoài đời nhiễu.** Mọi con số của MMER (81.2/75.0 WA) là con số *người-lớn-diễn-xuất*
  nên được trích dẫn như tiền lệ kiến trúc, **không phải** như một mốc hiệu năng mà Pebble có thể kỳ
  vọng.
- **Prosody của trẻ em khác với của diễn viên người lớn.** wav2vec-2.0-base được pre-train trên
  LibriSpeech (giọng đọc audiobook người lớn). Giọng nói trẻ em có cao độ cao hơn, formant khác, và
  các mẫu disfluency khác; một acoustic encoder pre-train trên người lớn có thể chuyển giao kém nếu
  không có một pass thích nghi giọng nói trẻ em. Đây là phép tương tự về acoustic của khoảng cách
  child-register về text của Pebble.
- **ASR là mắt xích yếu, và nó tệ hơn với trẻ em.** MMER mất 6.2 WA trên Google ASR người lớn.
  Word-error-rate của child ASR cao hơn đáng kể so với adult ASR trong tài liệu, nên sự suy giảm thực
  tế của head thoại Pebble so với trần bản-phiên-âm-gold có thể **vượt** 6.2 điểm của MMER. Nhánh
  text (modality mạnh cho cảm xúc theo ablation CTC của MMER) lại chính là nhánh bị hỏng nhiều nhất
  bởi lỗi child-ASR.
- **Đạo đức: giọng nói là dữ liệu sinh trắc.** Audio của một đứa trẻ có tính định danh theo cách mà
  text không có. Bất kỳ phần mở rộng thoại nào của Pebble phải thêm consent dành riêng cho giọng nói,
  xử lý on-device hoặc đã được scrub, và một chính sách rõ ràng rằng audio thô không được lưu giữ —
  một ngưỡng quản trị nặng hơn so với bộ phân loại text.
- **Không có cảm xúc safety/distress trong IEMOCAP.** 4 lớp của MMER (happy/angry/neutral/sad) không
  chứa tín hiệu fear/anxiety/self-harm. Sự chuyển giao từ cảm-xúc-diễn-xuất → distress-thật chưa được
  chứng minh; MMER không thể nói gì cho Pebble về việc phát hiện sắc thái *khủng hoảng (crisis)*, chỉ
  về valence/arousal thô.

### Hạn chế & câu hỏi mở cho Pebble

- **Mâu thuẫn với kế hoạch v1 của Pebble (modality).** Pebble v1 cố ý **chỉ-text**; toàn bộ đóng góp
  của MMER là **multimodal vượt trội so với bất kỳ unimodal nào** (81.2 so với text-only 78.1 so với
  speech-only 78.9). Đây là luận điểm được xuất bản mạnh nhất rằng *sắc thái giọng nói mang tín hiệu
  cảm xúc mà text bỏ lỡ* — tức là sự biện minh tường minh cho phần mở rộng thoại v2, **và** lời cảnh
  báo rằng một mô hình chỉ-text bỏ lại ~3 điểm WA trên bàn khi có audio. Mức +1.4 so với baseline
  naive-concat (79.8→81.2) là phần thuộc về fusion phức tạp; bước nhảy lớn hơn chỉ đơn giản là việc
  *có cả hai modality*.
- **Mâu thuẫn với FAIIR (bài 01) về tín hiệu phụ trợ.** Lợi ích của FAIIR đến từ **MLM thích nghi
  miền** (self-supervised, text trong miền) trước một head single-task; lợi ích của MMER đến từ
  **multi-task supervised + contrastive + ASR** không có pass MLM. Hai bài báo bất đồng về nơi mà
  hiệu năng rẻ nằm — Pebble nên coi MLM (D-F) và các auxiliary multi-task (D-B) là các đòn bẩy *độc
  lập* và ablate cả hai, vì không bài nào thử công thức của bài kia.
- **Text encoder đóng băng so với toàn bộ tiền đề của Pebble.** MMER **đóng băng** RoBERTa; giá trị
  của Pebble là một encoder miền được *fine-tune* (NeoBERT trên text sức khỏe tâm thần). Vì vậy có nên
  đóng băng NeoBERT trong giai đoạn fusion hay không là một câu hỏi mở mà MMER không thể trả lời —
  việc đóng băng của họ bị ép buộc bởi kích thước nhỏ của IEMOCAP, không phải nguyên tắc cho corpus
  lớn hơn của Pebble.
- **Benchmark nhỏ, diễn xuất, người lớn.** 12h / 10 speaker / kịch bản. Khoảng tin cậy (confidence
  interval) qua 5-fold leave-one-session-out CV **không được báo cáo** — với chỉ 5 fold và 10
  speaker, khoảng cách 81.2 so với 79.8 (1.4 WA) có thể không bền vững về mặt thống kê. Pebble không
  nên over-index vào thứ hạng của các delta ablation của MMER khi không có ước lượng phương sai.
- **Không calibration, không recall floor theo từng lớp.** MMER chỉ báo cáo WA (và ma trận nhầm lẫn).
  Đối với việc chấm điểm cảm xúc liên-quan-an-toàn của Pebble, accuracy tổng hợp là mục tiêu sai; MMER
  không đưa ra hướng dẫn nào về xác suất được calibrate hay recall floor cho các lớp thiểu
  số/distress (D-G), những thứ Pebble phải tự thêm vào.
- **Câu hỏi mở đáng một thí nghiệm:** liệu auxiliary CTC/ASR có còn giúp ích khi bản phiên âm là child
  ASR (WER cao) thay vì gold/adult-ASR không? MMER chỉ thử gold so với adult-Google-ASR. Nếu auxiliary
  suy giảm dưới các bản phiên âm child WER-cao, thì thành phần giá trị nhất của MMER lại là thành phần
  ít chuyển giao nhất — đây là điều quan trọng nhất Pebble cần đo trước khi cam kết với thiết kế thoại
  multi-task.
