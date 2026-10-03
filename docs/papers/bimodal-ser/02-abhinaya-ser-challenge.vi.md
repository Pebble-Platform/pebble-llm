# Paper 02 — ABHINAYA: A System for Speech Emotion Recognition In Naturalistic Conditions Challenge

> Bản dịch tiếng Việt của [02-abhinaya-ser-challenge.md](02-abhinaya-ser-challenge.md) — cập nhật 2026-07-10.

- **Authors:** Soumya Dutta, Smruthi Balaji, Varada R, Viveka Salinamakki, Sriram Ganapathy
- **Venue / year:** Interspeech 2025 (challenge system, SOTA post-challenge)
- **Links:** abs https://arxiv.org/abs/2505.18217 · PDF `pdfs/02-abhinaya-ser-challenge.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Kết hợp speech-SSL + text-LLM + fused speech-text models, ensemble majority-voting, loss chống class imbalance.

**Relevance to Pebble:** Cùng lab với bài LLM-distillation ICASSP 2025 đã cite; blueprint production cho fusion speech+text với imbalance-aware losses — map thẳng sang bài toán crisis-class imbalance.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

### Analysis — ABHINAYA (SER Naturalistic Challenge, Interspeech 2025)
> Thay thế điểm số 12% ngày 2026-07-02 vốn được tính dựa trên profile text-only đã lỗi thời.

- **Profile được chấm điểm (lắp ráp tại thời điểm phân tích):** (1) intent chính — phân loại **văn bản** ordinal suicide-risk trung thực với nhãn bạc từ LLM + đánh giá gold-holdout; (2) stream **voice** đang hoạt động (`voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`) — các head MTL không đồng nhất trên backbone **WavLM-Large / emotion2vec đóng băng** (emotion CE + affect **CCC** + crisis **hard recall-floor 0.90**, Kendall uncertainty weighting), hiện đang dùng nhãn proxy RAVDESS, **bước tiếp theo đã đặt tên = chuyển sang MSP-Podcast (A/V/D) + DAIC (crisis)**.
- **Overlap:** D1=0, D2=0, D3=1, D4=0, D5=0, D6=1, D7=2 → 19% (peripheral)
  - Formula: (3·0 + 2·0 + 1·1 + 2·0 + 2·0 + 2·1 + 1·2) / 26 × 100 = 5/26 × 100 ≈ 19%.
- **Gần nhất trên:** D7 (**WavLM-Large SSL backbone** — khớp chính xác với encoder đóng băng của voice stream) và, yếu hơn, D6/D3 (objective chống mất cân bằng rare-class trên một corpus emotion phân loại).
- **Best point (Baseline cần vượt qua):** ABHINAYA's speech-only **S1 = WavLM-Large (317M)** với attentive-statistics pooling + một softmax emotion head đạt **34.43 balanced-val / 33 test macro-F1** trên **MSP-Podcast** 8-class categorical emotion — cùng backbone và (theo voice roadmap) cùng dataset mà emotion head của voice trong Pebble sẽ chuyển sang.
  - **Cách áp dụng vào Pebble:** Khi `voice-mtl-heads` chuyển từ nhãn proxy RAVDESS sang MSP-Podcast thật (task tiếp theo trong roadmap), lấy macro-F1 single-model WavLM-Large ~34% val / 33% test của ABHINAYA làm baseline trung thực để neo emotion head, và thử **attentive-statistics pooling** của nó so với masked-mean pool hiện tại trên shared trunk.
- **Caveats:** Đã đọc toàn văn (không paywall). Điểm tăng từ 12%→19% chỉ vì profile được lắp ráp giờ bao gồm voice stream, khiến D7 lật (0→2) do khớp WavLM backbone; các chiều text-primary (D1 heterogeneous heads, D2 crisis domain, D4 LLM-teacher distillation, D5 MTL gradient balancing) vẫn là 0 — đây là single-task categorical SER, và các LLM (LLaMA-3 8B/70B, SALMONN) là encoder/classifier, không phải label teacher. Baseline chỉ là **emotion-head only**: ABHINAYA không có continuous A/V/D head (dù MSP-Podcast có mang các nhãn đó) và không có objective recall-floor/safety, nên nó **không** phải comparator cho affect-CCC head hay crisis head của Pebble. Nhãn test của MSP-Podcast bị ẩn (chỉ có trên leaderboard), nên các con số là balanced-val macro-F1 + hidden-test macro-F1.

## Deep research — full-PDF read (2026-07-10)

> Đọc đối chiếu với **bản Interspeech 2025 / ISCA-archive đã công bố** (`dutta25_interspeech`,
> https://www.isca-archive.org/interspeech_2025/dutta25_interspeech.pdf) cùng với preprint local
> `pdfs/02-abhinaya-ser-challenge.pdf` (arXiv:2505.18217v1). **Mọi con số trọng yếu bên dưới đều đã
> được đối chiếu chéo giữa hai bản và giống hệt nhau** — không có bất kỳ chênh lệch preprint↔published
> nào trên các con số được dùng. Được chấm điểm theo profile ViEmoSpeech hiện hành + hệ đăng ký
> **V-A…V-H** (`docs/tasks/paper-deep-analysis.md`), không phải theo profile text-stream/D-A…D-H đã
> lưu trữ. Khối "Analysis (overlap)" ở trên bị thay thế cho mục đích ra quyết định bởi phần này.

### Source-access note

- **Đọc toàn bộ PDF** qua `pdftotext` trên bản PDF arXiv local (method §3, experiments §4, cả bốn
  bảng, references). Bài system paper Interspeech ngắn 5 trang — đọc trọn vẹn từ đầu đến cuối.
- **Đối chiếu web** với bản venue. Query: `ABHINAYA system Speech Emotion Recognition
  Naturalistic Conditions Challenge Interspeech 2025 44.02 macro-F1 SALMONN WavLM` → tìm ra
  PDF ISCA-archive (`isca-archive.org/interspeech_2025/dutta25_interspeech.pdf`), tải về và
  `pdftotext`-diff. Xác nhận giống hệt: SoTA 44.02, baseline 32.93, S1 34.43, S2 37.68, "4th of
  166", "neutral ~26x fear", splits 84260/31961/3200, balanced-val 326/class, và toàn bộ lưới loss
  Table 2. Tất cả ✔ **được xác thực** (published = preprint tại đây).
- Khung challenge được đối chiếu chéo với bài paper của organizer (Naini et al., `naini25_interspeech`,
  cùng proceedings) — MSP-Podcast bản phát hành mới, 8 lớp phân loại, train mất cân bằng / test cân bằng.

### Bài paper thực sự làm gì

**Task.** Interspeech 2025 SER-in-Naturalistic-Conditions Challenge, track phân loại: emotion
8 lớp (angry, contempt, disgust, fear, happy, neutral, sad, surprise) trên bản phát hành mới
**MSP-Podcast**. Train/val/test = **84,260 / 31,961 / 3,200** file (§4.1, ✔). Training mất cân bằng
nặng (**neutral ≈ 26× fear**, §3.4, ✔); test cân bằng theo lớp và **ẩn nhãn (chỉ có trên
leaderboard)**. Model selection dùng một **tập validation cân bằng gồm 326 utterance/lớp** (§4.1,
✔). Metric = **macro-F1**.

**Hệ thống = 5 model không đồng nhất được fuse bằng majority vote ở decision-level** (Fig 1, §3).
Đây là **late/decision fusion, không phải learned feature fusion** — vote ở tầng cao nhất là bộ
kết hợp chính; model duy nhất fuse các modality *bên trong* mạng là ST1:
- **S1 — WavLM-Large (317M), speech-only.** CNN feature-extractor **đóng băng**, các lớp
  transformer được **fine-tune**; **attentive statistics pooling** (Okabe 2018: mean có trọng số
  attention **+** std có trọng số) → softmax head (§3.1.1).
- **S2 — SALMONN-13B SLLM, speech-only.** Encoder Whisper+BEATs và LLaMA **đóng băng**; chỉ
  **Q-Former + LoRA** (r=8, α=32, dropout 0.1) được train; representation của lớp LLaMA cuối →
  attentive-stat pooling → softmax (§3.1.2). Hệ thống đơn lẻ tốt nhất.
- **T1 — LLaMA-3.3-70B-Instruct, text-only, zero-shot** trên transcript ASR Whisper-large-v3
  (§3.2.1).
- **T2 — LLaMA-3.1-8B, text-only, LoRA fine-tuned**, được dùng như **encoder** (representation lớp
  cuối → attentive-stat pooling → head), không phải generator (§3.2.2).
- **ST1 — SALMONN-7B, speech-text joint.** Transcript ASR được **nối vào chuỗi speech ngay tại
  input**, LoRA fine-tuned; một model bimodal duy nhất được train chung (§3.3).
Majority vote qua năm model; **S2 là tiebreaker** (best val) (§4.2).

**Xử lý mất cân bằng = chỉ dùng loss function (không resampling/oversampling ở bất kỳ đâu).** Ba
loss (§3.4): **WCE** (class weight `w_c = N/(N_c·C)`); **WFL** weighted focal, `w_c(1−p)^γ`,
**γ=2**; **VS (vector-scaling / logit-adjustment)**, pre-softmax `ẑ = (N_c/N_max)^τ · z +
γ·log(N_c/N)`, **τ=0.3, γ=1** (§4.2). Tất cả fine-tune với AdamW, LR **1e-5**, 20 epoch, cap
audio 10 giây, checkpoint theo best-val-F1.

**Kết quả chính (Table 1, tất cả ✔).** Baseline challenge (WavLM+WCE) **test macro-F1 32.93**.
Model đơn lẻ tốt nhất = S2 **val 37.68 / test 35.34**. S1 WavLM **val 34.43 / test 33**.
Text-only: T1 zero-shot **val 32.78**, T2 fine-tuned **val 33.68**; joint ST1 **val 35.43**.
Toàn bộ **ensemble ABHINAYA: test 44.02 (SoTA, post-challenge; hạng 4/166 tại deadline khi ST1
mới chỉ 3-epoch → test 41.81)**. Mức tăng: **+33.68% relative so với baseline**; **+24.56%
relative so với model đơn lẻ tốt nhất** (35.34→44.02) (§4.3, ✔).

**Ablation loss (Table 2, ✔).** Loss tốt nhất **phụ thuộc vào model**: **các model speech thích
WFL** (S1 33.07/**34.43**/32.12; S2 36.34/**37.68**/33.17 cho WCE/WFL/VS), **text & speech-text
thích VS** (T2 29.79/30.12/**33.68**; ST1 33.92/34.73/**35.43**). Giả thuyết của tác giả: text
khởi điểm với khả năng phân tách lớp tốt hơn (T2 zero-shot 28.47 so với S2 zero-shot 18.63), điều
này phù hợp với VS mang tính logit-adjusting; các representation speech kém phân biệt hơn thì
hưởng lợi từ việc reweight theo mẫu kiểu focal (§4.5).

**Phân tích rare-class (Table 3, ✔).** Các model speech sụp đổ trên ba lớp hiếm nhất: **fear** S1
12.22 / S2 16.79; contempt/disgust tương tự. **Các model text cứu lấy phần đuôi** — zero-shot T1
đạt **fear 29.22**, vượt cả toàn bộ ensemble (26.41) trên riêng lớp hiếm nhất này; T2 và ST1 cũng
nâng contempt/disgust. Ensemble thắng 4/8 lớp nhìn chung. Bỏ ST1 khỏi vote làm mất ~2% điểm tuyệt
đối (Table 4, Comb IV); vote đủ 5 model đạt val 42.31 (§4.8).

### Các phần trực tiếp hữu ích cho ViEmoSpeech (gắn nhãn theo Decision ID)

1. **[V-A] Template bimodal là một ensemble late-fusion 3 nhánh, và fusion học được *duy nhất* là
   nối input (ST1).** Artifact cụ thể: nhánh fusion của ViEmoSpeech = một model được train chung
   audio-đóng-băng + text-đóng-băng (dạng ST1) **cộng thêm** một majority-vote qua các head
   single-modality được tinh chỉnh chống mất cân bằng độc lập. ST1 (val 35.43) vượt SALMONN-7B
   speech-only (val 33.87, §4.6) **+1.56 điểm tuyệt đối** — mức lợi ích đo được của joint
   speech-text so với speech-only, cùng backbone. +1.56 đó là ngưỡng trung thực cho câu hỏi "liệu
   learned fusion có vượt nhánh đơn lẻ hay không."
2. **[V-A/V-B] Attentive-statistics pooling (mean có trọng số + std có trọng số) là bước gom
   (aggregation) chung, tương thích với trunk đóng băng trên mọi nhánh fine-tuned** (S1/S2/T2/ST1).
   Đây là một thay thế drop-in cho masked-mean pooling trên trunk **đóng băng** WavLM/emotion2vec
   và trunk **đóng băng** PhoBERT/ViSoBERT — không cần gradient của backbone.
3. **[V-E/V-G] Mất cân bằng được xử lý bằng loss function, không phải resampling — và loss tốt nhất
   phụ thuộc vào modality.** Artifact: head phân loại 7 lớp dùng **WFL (γ=2) trên nhánh audio** và
   **VS logit-adjustment (τ=0.3, γ=1) trên nhánh text PhoBERT/ViSoBERT**. Mức tăng đo được từ việc
   chọn đúng loss theo từng nhánh: S1 +2.31 điểm tuyệt đối (32.12→34.43), ST1 +1.51
   (33.92→35.43).
4. **[V-E/V-G] Majority voting ở decision-level tự nó là đòn bẩy mất cân bằng lớn nhất** —
   **+24.56% relative** so với model đơn lẻ tốt nhất, và cụ thể là vì các nhánh text mang phần
   đuôi hiếm (Table 3), vote nâng các lớp thiểu số mà các model đơn lẻ đánh rớt. Artifact: một
   audit rare-class-recall báo cáo macro-F1 single-branch so với ensemble *theo từng lớp*, không
   chỉ tổng hợp.
5. **[V-C] Nhánh text-LLM chạy trên transcript ASR (Whisper-large-v3), không có gold text lúc
   test, và fine-tuned-nhỏ-làm-encoder vượt zero-shot-lớn.** T2 (LLaMA-8B, LoRA, dùng như encoder)
   val 33.68 > T1 (LLaMA-70B zero-shot) val 32.78 (Table 1, ✔). Artifact: nhánh PhoBERT/ViSoBERT
   của ViEmoSpeech như một **encoder fine-tuned trên transcript PhoWhisper** (không phải generator
   được prompt), pooled với attentive-stats, train với VS-loss.

### Từng phần giúp ViEmoSpeech thành công như thế nào

- **Quyết định fusion V-A.** Áp dụng pattern ST1 làm comparator *learned-fusion* để vượt qua rule
  baseline đã rút lại (vn-09): một model bimodal nối transcript PhoWhisper với chuỗi speech
  WavLM/emotion2vec và train một head chung — rồi bọc nó trong một majority-vote với một head
  audio-only và một head text-only để không modality nào âm thầm lấn át. Nhưng **cần khớp ngân
  sách (budget-match)**: ST1 của ABHINAYA là SALMONN-7B và ensemble của nó trải dài các LLM
  7B/13B/70B — PhoBERT-base + WavLM-Large đóng băng của ViEmoSpeech nhỏ hơn khoảng ~2 bậc độ lớn,
  nên hãy port *hình dạng* (nối input + attentive-stat pool + decision vote), không phải quy mô.
  Cross-attention/gated fusion (WavFusion, vn-07 FAS) vẫn là các phương án nhẹ hơn để thử nghiệm
  so với ST1-concat.
- **Pooling V-B.** Đổi masked-mean → attentive-statistics pooling trên các trunk đóng băng; kênh
  weighted-std chính là tín hiệu prosodic-variability mà bài review JMIR (bimodal-10) đã gắn cờ là
  dấu hiệu distress, nên nó kiêm luôn vai trò feature rẻ cho distress-head.
- **Mất cân bằng V-E/V-G.** Chạy loss theo lựa chọn **từng nhánh, không phải toàn cục**: WFL(γ=2)
  trên audio, VS(τ=0.3,γ=1) trên text — đúng ma trận 4-model của ViEmoSpeech. Báo cáo macro-F1
  theo từng lớp, single so với ensemble, để chứng minh việc cứu lấy rare-class. Đây chính là
  phương pháp imbalance-aware cụ thể + mức tăng macro-F1 +24.56% relative / +2.31 tuyệt đối mà
  task yêu cầu trích xuất.
- **Độ bền text V-C.** Dùng PhoBERT/ViSoBERT như một encoder fine-tuned trên output PhoWhisper,
  train với VS-loss, attentive-pooled — ABHINAYA cho thấy cách này vượt qua một LLM lớn được
  prompt và cứu được phần đuôi hiếm ngay cả khi nhánh *speech* thất bại trên nó.

### Lăng kính sức khỏe tâm thần trẻ em → rủi ro chuyển giao (transfer-risk) sang ViEmoSpeech (7 lớp + V/A + distress, sàn ≥50-clip, backbone đóng băng, PhoBERT/ViSoBERT)

- **Rủi ro chuyển giao trên V-A (backbone đóng băng).** **Không giữ vững một cách rõ ràng.** S1
  34.43 của ABHINAYA **fine-tune cả stack transformer của WavLM** (chỉ CNN extractor bị đóng
  băng) và mọi nhánh LLM đều train adapter LoRA — không nhánh nào thực sự là backbone đóng băng.
  Ràng buộc frozen-trunk của ViEmoSpeech nhiều khả năng sẽ nằm *dưới* các con số single-model đã
  báo cáo này; phần chuyển giao được sang trunk đóng băng là **pooling head + loss + ensemble**,
  không phải các con số accuracy đã báo cáo. Cần nói rõ điều này trong method paper: các con số
  của ABHINAYA là một trần fine-tuned, không phải một mốc frozen-trunk.
- **Rủi ro chuyển giao trên V-C / V-D (nhánh text, ASR ngôn ngữ có thanh điệu).** ASR của ABHINAYA
  là **Whisper-large-v3 tiếng Anh** trên speech podcast; ViEmoSpeech chạy **PhoWhisper trên phim
  truyền hình tiếng Việt với lỗi hoán đổi thanh điệu ở mức arousal cao** (mày→máy, tao→tháo).
  Nhánh text của ABHINAYA chỉ nhỉnh hơn baseline một chút (33.68 so với 32.93) *ngay cả trong chế
  độ ASR dễ* và speech vượt text (37.68 > 33.68) — nên nhánh text-ASR có thanh điệu có nguy cơ
  *yếu hơn*, không phải nhánh trụ cột mà giả thuyết cạnh tranh tone của ViEmoSpeech dự đoán. Biện
  pháp giảm thiểu: giả thuyết tone×emotion nói rằng text nên gánh nhiều hơn vì F0 đã bị thanh
  điệu chiếm dụng — nhưng điều này phải được **đo trên tiếng Việt**, vì ABHINAYA là một
  phản-ví-dụ nơi text không chiếm ưu thế. Đưa vào biện pháp bảo vệ vn-12 về audio-anchoring (head
  audio-only phụ / modality dropout) để một nhánh text ASR yếu không thể đầu độc vote.
- **Rủi ro chuyển giao trên V-E/V-G (mất cân bằng so với sàn ≥50-clip).** ABHINAYA chống lại mất
  cân bằng **26:1** hoàn toàn hậu kỳ (loss + vote) và **fear vẫn chỉ đạt đỉnh ~26–29% F1** với
  toàn bộ bộ máy 5-model. Đó là lập luận mạnh mẽ nhất *ủng hộ* sàn **≥50-clip** ở tầng thiết kế
  corpus của ViEmoSpeech (ADR-002): cân bằng ở tầng thiết kế là đòn bẩy rare-class đáng tin cậy
  hơn bất kỳ mẹo loss nào, vốn chỉ khôi phục được vài điểm tuyệt đối. Loss/ensembling mang tính bổ
  sung, không thay thế cho sàn (floor). VS/WFL cũng chỉ áp dụng **cho head phân loại 7 lớp** —
  hồi quy V/A (CCC) và head recall-floor distress không dùng loss thuộc họ CE, nên bài paper này
  không chạm đến V-F.
- **Đạo đức / khung nhìn.** ABHINAYA là một hệ thống challenge-leaderboard không có khung lâm
  sàng, trẻ em, hay distress nào — MSP-Podcast là speech podcast tự nhiên của người lớn. Không có
  gì ở đây chuyển giao được cho câu hỏi trung thực của distress-head; hãy coi nó thuần túy như một
  template kỹ thuật.

### Hạn chế & câu hỏi mở cho ViEmoSpeech (bao gồm mâu thuẫn/khoảng trống)

- **Mâu thuẫn với giả thuyết tone-channel-competition của ViEmoSpeech VÀ với vn-12 ("semantics
  dominate"):** trong ABHINAYA, **nhánh speech vượt nhánh text** (S2 37.68 > T2 33.68 val;
  Table 1) và text-only chỉ vừa vượt qua baseline. Đây là tiếng Anh tự nhiên, nhưng nó là một
  data point trực tiếp cho thấy một nhánh text ASR mạnh **không nhất thiết** phải chiếm ưu thế
  trong SER — củng cố quan điểm "text gần như vô dụng" của vn-08 hơn là "semantics chiếm ưu thế"
  của vn-12, và cảnh báo ViEmoSpeech không nên *giả định* claim tone-buộc-text-phải-gánh-nhiều-hơn
  mà không đo lường nó. (Hòa giải, nhất quán với log wave-1/2: "text mang bao nhiêu thông tin" ≠
  "model dựa vào text bao nhiêu.")
- **Mâu thuẫn với FAIIR (exemplar) và với vn-09 fusion:** ABHINAYA **không dùng
  oversampling/resampling nào cả** — thuần túy reweight loss + logit-adjust + decision vote —
  trong khi công thức chống mất cân bằng của FAIIR là oversampling hai trong ba thành viên
  ensemble. ViEmoSpeech nên thử nghiệm loss-only (ABHINAYA) so với resample-based (FAIIR) và
  không nên gộp lẫn hai cách; ABHINAYA là lựa chọn phù hợp hơn với một corpus nhỏ đã cân bằng theo
  sàn, nơi oversampling các lớp ~50-clip có nguy cơ overfitting.
- **Khoảng trống — các con số backbone đóng băng chưa được biết.** ABHINAYA chưa bao giờ báo cáo
  một biến thể trunk-đóng-băng-hoàn-toàn, nên nó không cho ViEmoSpeech mốc nào cho ràng buộc thực
  tế của mình. Con số single-model WavLM-đóng-băng + attentive-pool + WFL của Pebble sẽ là một
  phép đo mới, không phải một sự tái tạo.
- **Khoảng trống — không có thảo luận speaker-disjoint, không có V/A/D.** ABHINAYA kế thừa các
  split challenge của MSP-Podcast (speaker-disjoint theo thiết kế, hơn 2000 speaker) nhưng không
  bao giờ phân tích speaker leakage, và nó **chỉ phân loại (categorical only)** — không có head
  V/A liên tục dù MSP có mang V/A/D. Vì vậy nó không phải comparator cho head CCC V/A của
  ViEmoSpeech hay whole-series holdout speaker-disjoint (V-G); những cái đó vẫn neo vào bimodal-12
  (MSP CCC) thay thế.
- **Khoảng trống — SoTA 44.02 nằm trên một test set ẩn, cân bằng, 326/lớp.** Macro-F1 trung thực
  của ViEmoSpeech (speaker-disjoint, class-floored, whole-series-holdout) không thể so sánh
  ngang hàng; chỉ dùng 44.02 như một mốc thể loại ("SER phân loại 8-lớp tự nhiên nằm ở mức thấp
  40 macro-F1"), bên cạnh các con số VN đã bị lạm phát do leak (vn-08 86.6, vn-10 0.87) như cực
  đối lập.
