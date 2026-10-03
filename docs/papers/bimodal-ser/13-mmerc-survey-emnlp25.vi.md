# Paper 13 — Multimodal Emotion Recognition in Conversations: A Survey of Methods, Trends, Challenges and Prospects

> Bản dịch tiếng Việt của [13-mmerc-survey-emnlp25.md](13-mmerc-survey-emnlp25.md) — cập nhật 2026-07-10.

- **Authors:** Chengyan Wu, Yiqiang Cai, Yang Liu, Pengxu Zhu, Yun Xue, Ziwei Gong, Julia Hirschberg, Bolei Ma
- **Venue / year:** EMNLP 2025 Findings
- **Links:** abs https://arxiv.org/abs/2505.20511 · PDF `pdfs/13-mmerc-survey-emnlp25.pdf`
- **Group:** survey / benchmark

**Summary:** Survey mới nhất bản đồ hóa các phương pháp fusion + giao thức đánh giá cho nhận diện cảm xúc hội thoại (conversational ER) text+audio(+visual).

**Relevance to Pebble:** Bản đồ chiến lược fusion audio+text — điểm vào chọn kiến trúc cho voice+message.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled profile (từ `docs/intent/constraints.md` + `docs/spec/capabilities/voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`):** Pebble là một chương trình chính về **văn bản đánh giá nguy cơ tự tử theo thang thứ tự (ordinal suicide-risk text)** (bộ mã hóa lớp BERT, nhãn silver từ teacher-LLM, đánh giá gold-holdout, QWK/MAE thứ tự) cộng với một luồng **voice** liền kề đang hoạt động (backbone emotion2vec/WavLM đóng băng; 3 head MTL không đồng nhất — emotion CE + affect valence/arousal CCC + crisis BCE dưới ràng buộc sàn recall cứng ≥ 0.90 — được cân bằng bằng Kendall uncertainty weighting). Hướng đi phía trước: **fusion voice+text**. "Hữu ích" nghĩa là thúc đẩy các head MTL không đồng nhất, cân bằng loss có nguyên tắc, an toàn crisis-recall, chưng cất nhãn silver, hoặc một kiến trúc fusion cho thiết lập text-primary + voice-auxiliary.

### Analysis — MMERC survey (Wu et al., EMNLP 2025 Findings)
- **Overlap:** 31% (peripheral) — D1=0, D2=1, D3=1, D4=1, D5=1, D6=0, D7=1
  - D1=0 (survey tập trung vào *fusion* modal, không phải các head phân loại+liên tục không đồng nhất; toàn bộ các chỉ số được báo cáo đều là phân loại — WA/WF1/macro-F1/micro-F1)
  - D2=1 (nhận diện cảm xúc là nền tảng cảm xúc cho voice crisis head của Pebble, nhưng không có khung sức khỏe tâm thần/khủng hoảng; chỉ có một đề cập lướt qua về ứng dụng "intelligent healthcare")
  - D3=1 (liệt kê các corpus cảm xúc kinh điển IEMOCAP/MELD/CMU-MOSEI/MEmoR/AVEC — liên quan đến voice, nhưng không phải các tập chuyển giao văn bản có tên GoEmotions/EmpatheticDialogues/intensity)
  - D4=1 (khảo sát các phương pháp LLM-for-ERC dựa trên generation — InstructERC, DialogueLLM, MLLM — liên quan lỏng lẻo với việc gán nhãn teacher-LLM, nhưng không có mẫu hình chưng cất nhãn silver để tăng cường dữ liệu)
  - D5=1 (phân loại "equal modality weights" so với "text-dominant primary-auxiliary" fusion của nó, và phần challenges thúc đẩy learnable modality gates / uncertainty-aware fusion / modality dropout, có liên quan đến cân bằng loss — nhưng đây là cân bằng *modality*, không phải cân bằng loss *task* MTL như Kendall/GradNorm/PCGrad)
  - D6=0 (không có ràng buộc an toàn/recall crisis ở bất kỳ đâu; chỉ có các mục tiêu phân loại chuẩn)
  - D7=1 (bảng feature-extraction văn bản liệt kê RoBERTa/sBERT — khớp với backbone văn bản họ BERT của Pebble; các bộ trích xuất audio thì cũ hơn openSMILE/COVAREP/librosa, **không phải** backbone SSL emotion2vec/WavLM mà luồng voice của Pebble sử dụng)
  - `(3·0 + 2·1 + 1·1 + 2·1 + 2·1 + 2·0 + 1·1)/26 × 100 = 8/26 × 100 = 31%`
- **Closest on:** phân loại fusion đa phương thức (D5 — text-dominant primary-auxiliary so với equal-weight) và các corpus cảm xúc kinh điển mà nó bản đồ hóa (D3).
- **Best point (Design lesson):** Survey khẳng định rằng đối với một hệ thống text-primary, kiến trúc chiến thắng là **text-dominant primary-auxiliary fusion** — văn bản vẫn là cốt lõi và audio/prosody được đưa vào như một tín hiệu phụ trợ thông qua cross-modal attention (ví dụ "weaker modalities as multimodal prompts" của Zou et al.), điều mà survey báo cáo là vượt trội hơn phương pháp nối equal-weight đơn giản trong khi vẫn giữ được tính toàn vẹn của modality mạnh.
  - **How to apply to Pebble:** Khi kết nối luồng voice liền kề vào mô hình rủi ro văn bản chính, hãy áp dụng cơ chế text-dominant này (voice/prosody như phụ trợ được đưa vào qua cross-modal attention lên bộ mã hóa văn bản BERT) thay vì fusion equal-weight — điều này khớp với ý định text-primary của Pebble, giữ mô hình văn bản gold-holdout làm lõi giá trị đóng băng, và cho một cơ sở thiết kế có thể trích dẫn thay vì phải tự suy diễn lại trục fusion.
- **Caveats:** Đây là một **survey** — một bản đồ không gian thiết kế, không phải một phương pháp có thể chạy được hay một con số để vượt qua; không có chỉ số baseline nào để tái tạo. Được chấm điểm dựa trên việc đọc đầy đủ §1–7 (intro, methodology, datasets/eval, methods taxonomy, challenges, conclusion). Không có sự bao phủ nào đối với các yếu tố khác biệt của Pebble: miền sức khỏe tâm thần/khủng hoảng, các head MTL phân loại+liên tục không đồng nhất, mục tiêu an toàn sàn-recall cứng, tăng cường nhãn silver teacher-LLM, và các chỉ số nhạy với thứ tự (ordinal-aware) — do đó thuộc dải peripheral bất chấp sự liên quan chủ đề với hướng fusion voice. Các backbone SSL voice (emotion2vec/WavLM) không được nêu bật; các bộ trích xuất audio được khảo sát có trước chúng.

## Deep research — full-PDF read (2026-07-10)

> Đọc đối chiếu với hồ sơ ViEmoSpeech hiện tại + Decision Register V-A…V-H (xem
> `docs/tasks/paper-deep-analysis.md`), **không phải** hồ sơ luồng văn bản đã lưu trữ trong phần
> "Analysis" ở trên (trong đó trích dẫn D1–D7 và một chương trình suicide-risk/NeoBERT — đã cũ).
> Đây là một **survey**; phần trích xuất bên dưới là bản đồ phân loại + bối cảnh dữ liệu + vấn đề mở,
> không phải một phương pháp đơn lẻ. Toàn văn được đọc qua `pdftotext` trên `pdfs/13-mmerc-survey-emnlp25.pdf`
> (arXiv:2505.20511v2, 9 Sep 2025; 578 dòng văn bản, §1–7 + Limitations + Appendix A datasets).

### Source-access note

- **PDF read locally:** `pdftotext docs/papers/bimodal-ser/pdfs/13-mmerc-survey-emnlp25.pdf`
  → toàn bộ tệp (abstract, §1 intro, §2 task/methodology, §3 datasets+metrics, §4 feature
  extraction+context modeling, §5 method taxonomy graph/fusion/generation, §6 challenges,
  §7 conclusion, Limitations, Appendix A dataset details). Các hình (1–5) là hình vẽ đường nét
  trong bản trích xuất; nội dung của chúng có thể suy ra được từ văn bản xung quanh và cây phân
  loại (taxonomy tree) ở Figure 2.
- **Web-validated:**
  - **Venue/provenance ✔** — truy vấn `Multimodal Emotion Recognition in Conversations Survey Wu
    EMNLP 2025 Findings arXiv 2505.20511` → ACL Anthology `2025.findings-emnlp.332`
    (Findings of ACL: EMNLP 2025, tr. **6257–6274**, Suzhou, China). Xác nhận việc chấp nhận
    Findings-EMNLP-2025; bản preprint arXiv 2505.20511, v1 26 May 2025, **v2 9 Sep 2025** (phiên bản
    được đọc). PDF cục bộ = bản v2 đã được chấp nhận; không có mâu thuẫn số phiên bản preprint/venue.
    URL: https://aclanthology.org/2025.findings-emnlp.332/
  - **M3ED dataset stats ✔** — truy vấn `M3ED dataset 24449 utterances 990 dialogues 56 Chinese TV
    series emotion` → M3ED = **990 hội thoại đôi (dyadic dialogues) / 24,449 phát ngôn** từ **56 series
    TV Trung Quốc**, 7 cảm xúc (happy/surprise/sad/disgust/anger/fear/neutral), "bộ dữ liệu hội thoại
    cảm xúc đa phương thức đầu tiên bằng tiếng Trung." Khớp với Appendix A của survey nguyên văn.
    URL: https://aclanthology.org/2022.acl-long.391/
  - Các thống kê dataset khác (IEMOCAP 7,433 utt; MELD 13,708 utt / 1,433 conv; CMU-MOSEI 23,453
    segments) là kinh điển, đối chiếu chéo với Appendix A của chính survey; gắn nhãn ✔ khi là chuẩn
    cộng đồng, ≈ khi chỉ có một nguồn (ACE, MEmoR).
- **Not a number-to-reproduce paper:** một survey không có chỉ số headline để vượt qua. Các phần
  trích xuất mang tính chịu tải là (a) phân loại fusion, (b) quy ước dataset/metric, (c) định nghĩa
  context-modeling — được xác thực qua cấu trúc/trích dẫn, không phải qua điểm benchmark.

### What the paper actually does

MERC = dự đoán một nhãn cảm xúc `e_i ∈ Y` cho **mỗi phát ngôn `u_i` trong một hội thoại**
`D = {u_1…u_N}`, trong đó mỗi phát ngôn mang ba luồng modal `u_i = [u_i^t; u_i^a; u_i^v]`
(text/acoustic/visual) — §2, Eq. 1. Đặc điểm định nghĩa so với ER cấp câu (sentence-level ER) là
nhãn phụ thuộc vào **bối cảnh hội thoại và theo dõi người nói**, không chỉ riêng phát ngôn (§1, §4.2).

- **Datasets (§3, Table 1 + Appendix A).** Chín benchmark, chia thành nhóm trung tâm tiếng Anh và
  không phải tiếng Anh:
  IEMOCAP (en, video, 2008; 151 hội thoại / **7,433 utt** ✔, 6 cảm xúc), AVEC (en, 2012;
  valence/arousal/expectancy/power liên tục được tổng hợp lên cấp phát ngôn ≈), EmoryNLP (en, TV,
  2017; ~12,000 utt, 7 cảm xúc ≈), CMU-MOSEI (en, 2018; **23,453 segments** ✔, sentiment −3..+3 +
  6 cường độ Ekman), MELD (en, TV *Friends*, 2019; 1,433 conv / **13,708 utt** ✔, 7 cảm xúc), MEmoR
  (en, *Big Bang Theory*, 2020; 5,502 clip / 8,536 mẫu, 14 cảm xúc ≈), **M3ED** (zh, TV,
  2022; **990 hội thoại / 24,449 utt / 56 series TV Trung Quốc** ✔, 7 cảm xúc — corpus ngôn ngữ có
  thanh điệu duy nhất), M-MELD (fr/es/el/pl, MELD được dịch, 2023 ≈), ACE (Akan/châu Phi, phim, 2025;
  385 hội thoại / 6,162 utt / 21 phim / 308 người nói / chia 7:1.5:1.5, độ nổi bật ngôn điệu cấp từ ≈).
- **Metrics (§3).** Accuracy, **Weighted-F1, Macro-F1, Micro-F1**, cộng với phân tích theo từng cảm
  xúc. Tất cả đều là phân loại. Không có quy ước CCC / không có affect liên tục (Pearson/CCC) ở bất kỳ
  đâu — ngay cả nhãn V/A liên tục của AVEC cũng "được tổng hợp trên từng phát ngôn" và gộp vào đánh giá
  phân loại.
- **Feature extraction (§4.1, Table 2).** Text: LSTM / CNN / Transformer / **RoBERTa / sBERT**.
  Visual: 3D-CNN / OpenFace / MTCNN / DenseNet / VisExtNet. Audio: **openSMILE / COVAREP / librosa /
  DialogueRNN** — tức các đặc trưng âm học thủ công (hand-crafted), **không có audio SSL nào (không
  WavLM / HuBERT / emotion2vec / Whisper-encoder)**. Điều này cho thấy front-end audio được khảo sát
  thuộc thời kỳ trước 2020.
- **Context modeling (§4.2, Eqs 2–4).** Hai loại phụ thuộc: **cấp tình huống (situation-level)** (các
  mô hình tuần tự trên các phát ngôn, `c_i^s, h_i^s = Model(u_i, h_{i-1}^s)`, Eq. 2) và **cấp người
  nói (speaker-level)** (embedding người nói `x^m = c_i^s + S_i`, Eq. 3, hoặc một đồ thị hội thoại
  `G=(V,E,W,R)` với một GNN `h_i^g = GNN(c_i^s, {…})`, Eq. 4). Đây là cơ chế khiến ERC mang tính
  *hội thoại*.
- **Method taxonomy (§5, Figure 2) — thành phần cốt lõi.** Ba họ phương pháp:
  1. **Graph-based (§5.1)** — các phát ngôn = node, các quan hệ = cạnh. Các phân nhóm: GNN truyền
     thống (DialogueGCN, MMGCN, CORECT), NN **hypergraph** (GCNet, ConxGNN — cho tương tác thiếu
     modality / bậc cao), **Fourier GNN** (GS-MCC — chia tần số cao/thấp qua DFT để khắc phục
     over-smoothing). Điểm mạnh: phụ thuộc tầm xa + tương tác người nói; điểm yếu: "các kết nối ngây
     thơ có thể đưa vào nhiễu nếu không có sự căn chỉnh modality phù hợp."
  2. **Fusion-based (§5.2, Figure 4)** — tương tác đa phương thức qua Transformer attention. Hai
     nhánh phụ: **(a) Equal Modality Weights** (attention nội-modal + liên-modal đối xứng, ví dụ
     EmoCaps, CMCF-SRNet, DialogueTRM, SDT với hierarchical gating + self-distillation) — "ngăn việc
     phụ thuộc quá mức vào một modality duy nhất"; **(b) Text-Dominant / primary–auxiliary** (văn bản
     là lõi, các modality yếu hơn được đưa vào như tín hiệu phụ trợ — MMT/Zou 2022 cross-modal
     attention bảo toàn tính toàn vẹn của modality chính, MPT/Zou 2023 "weaker modalities as
     multimodal prompts," CMATH/Zhu 2024 CMA-Transformer bất đối xứng + distillation phân cấp). Kết
     luận của survey: các phương pháp fusion "hiệu quả cho các tác vụ có đầu vào modality được căn
     chỉnh tốt nhưng thường bỏ qua các cấu trúc cấp hội thoại như phụ thuộc người nói… nhấn mạnh
     fusion cấp modality hơn là suy luận quan hệ (relational reasoning)."
  3. **Generation-based (§5.3, Figure 5)** — LLM/MLLM tái định dạng ERC thành sinh văn bản:
     instruction-tuned + speaker/context (InstructERC, CKERC, LaERC-S), MLLM nhận biết hành vi
     (behavior-aware) (DialogueLLM, BeMERC), fusion/adaptation nhẹ trên một LLM đóng băng
     (MSE-Adapter, SpeechCueLLM — chuyển đặc trưng giọng nói thành prompt ngôn ngữ tự nhiên, không
     thay đổi kiến trúc).
- **Challenges & prospects (§6).** Khoảng trống FAIR/cấp phép (dataset đơn ngữ, giới hạn bản quyền,
  nhãn không nhất quán → khó tái sử dụng); low-resource/đa ngôn ngữ/đa văn hóa (hầu hết SOTA chỉ dành
  cho tiếng Anh; "cảm xúc được biểu đạt khác nhau qua các ngôn ngữ và văn hóa… quy tắc thể hiện đặc thù
  văn hóa"); độ phức tạp của chiến lược fusion (early/mid/late/hybrid; các thang thời gian modality
  **bất đồng bộ (asynchronous)** khó căn chỉnh ở cấp phát ngôn); căn chỉnh liên-modal / nhiễu /
  **thiếu (missing)** / **xung đột (conflict)** modality (đề xuất modality dropout, **uncertainty-aware
  fusion**, RL để chú ý vào các modality đáng tin cậy); **lựa chọn modality hiệu quả** (learnable
  modality gates, sparsity regularization); tinh chỉnh MLLM hiệu quả (adapters, LoRA); mở rộng không
  gian modality (ánh mắt, sinh lý học).
- **Tone / Vietnamese check:** từ "tone" chỉ xuất hiện như một mô tả âm học chung trong định nghĩa
  modality ("Các đặc trưng ngôn điệu và cận ngôn ngữ (paralinguistic)… như tone, cao độ, và năng lượng,"
  §2). **Thanh điệu từ vựng (lexical tone) không bao giờ được bàn tới. Tiếng Việt không bao giờ xuất
  hiện. M3ED (tiếng Quan Thoại) được đưa vào nhưng tone không phải là một biến trong bất kỳ phương pháp
  hay chỉ số nào được khảo sát.** Artifact gần nhất liên quan đến ngôn điệu là chú thích "độ nổi bật
  ngôn điệu cấp từ" của ACE (Akan, không phải ngôn ngữ có thanh điệu từ vựng theo cách xử lý của survey).

### Parts directly useful for ViEmoSpeech

1. **[V-A] Phân loại fusion như bản đồ kiến trúc của chúng ta (§5.2, Figure 4).** Trục
   Equal-Weight-vs-Text-Dominant rõ ràng chính là quyết định thiết kế đứng sau V-A. Các mẫu hình được
   đặt tên, có thể trích dẫn cho mỗi cực: cross-attention đối xứng (SDT hierarchical-gating +
   self-distillation) so với cross-attention primary–auxiliary (MMT / MPT "weaker-modality-as-prompt"
   / CMATH CMA-Transformer bất đối xứng). Điều này cho V-A một trục đã công bố để định vị fusion
   WavLM+PhoBERT của chúng ta, thay vì phải tự suy diễn lại.
2. **[V-A] Họ graph-based mang tính *cấu trúc hội thoại (conversation-structural)* rõ ràng (§5.1,
   §4.2 Eqs 2–4).** Survey nói thẳng rằng giá trị của các phương pháp graph là "phụ thuộc tầm xa và
   tương tác người nói bằng cách mô hình hóa các phát ngôn như node" — tức toàn bộ lợi ích của chúng
   đến từ các cạnh liên-phát-ngôn / liên-người-nói. Với các clip đơn phát ngôn của chúng ta thì không
   có các cạnh như vậy. Hữu ích chính xác như phần phân loại mà chúng ta **loại trừ** có căn cứ.
3. **[V-G] Bối cảnh dataset + quy ước metric (§3, Table 1, Appendix A).** Bộ benchmark của ERC có
   nguồn từ series TV/phim, nhãn theo phát ngôn, và báo cáo Weighted-F1 / Macro-F1 / Micro-F1 cùng với
   phân tích theo từng cảm xúc. M3ED (TV Trung Quốc, 990 dial / 24,449 utt / 56 series ✔) là điểm
   tương đồng cấu trúc trực tiếp với corpus phim truyền hình Việt Nam của chúng ta và là một tham chiếu
   quy mô/định dạng cho V-H/V-G. **Sự vắng mặt của bất kỳ quy ước affect liên tục CCC/Pearson** trong
   ERC là một phát hiện của V-G: việc báo cáo V/A-CCC của chúng ta không kế thừa từ ERC mà phải mượn từ
   dòng SER theo chiều liên tục (dimensional-SER) (MSP-Podcast, bimodal-12).
4. **[V-C] Xử lý kênh văn bản phụ thuộc vào bối cảnh, trên bản chép lời *sạch* (§4.1, §5.2).** Nhánh
   văn bản của ERC = RoBERTa/sBERT trên bản chép lời phát ngôn chuẩn (gold) với bối cảnh
   tình huống+người nói (Eqs 2–3). Nhánh văn bản của chúng ta là PhoBERT trên **ASR PhoWhisper nhiễu
   của một phát ngôn đơn lẻ, không có bối cảnh hội thoại**. Tuyên bố "Text-Dominant Modality" của
   survey (văn bản là lõi đáng tin cậy) dựa trên giả định bản chép lời sạch + bối cảnh đó — điều mà
   chúng ta không có.
5. **[V-A/V-G] Chương trình nghị sự về xung đột/nhiễu/thiếu-modality ở §6 ánh xạ tới các chế độ lỗi
   của chúng ta.** Các biện pháp khắc phục được đề xuất — **modality dropout, uncertainty-aware
   fusion, learnable modality gates** — chính xác là các cơ chế bảo vệ neo-audio (audio-anchoring) mà
   lát cắt xung đột tone×emotion của chúng ta cần (vọng lại yêu cầu của vn-08 rằng fusion không được
   sụp đổ về văn bản). Survey nêu tên đây là các vấn đề *mở*, tức lát cắt ablation ASR-noise +
   tone-conflict của chúng ta nằm trong khoảng trống đã được thừa nhận.

### How each part helps ViEmoSpeech succeed

- **V-A fusion choice:** Định vị fusion WavLM+PhoBERT đã học trên trục của survey và chọn
  **primary–auxiliary với AUDIO làm primary** — ngược lại với mặc định text-dominant của ERC.
  Cơ sở lý luận, có thể bảo vệ được từ tổng hợp của chính chúng ta: register của chúng ta (VN-ASR
  nhiễu, phát ngôn đơn lẻ) là audio-dominant, do đó *hình dạng* "weaker-modality-as-prompt" của
  MMT/MPT nên được dùng với văn bản là prompt yếu hơn/phụ trợ và audio (+phonation) là lõi — hình ảnh
  đối xứng ngược với Zou et al. Trích dẫn Figure 4 làm không gian thiết kế; trích dẫn lập luận về
  register của chúng ta cho việc đảo ngược primary. Cụ thể: bảng ablation V-A có một hàng cho mỗi cực
  (nối equal-weight vs cross-attn audio-primary vs cross-attn text-primary), trực tiếp cụ thể hóa §5.2.
- **V-A exclusion of graph methods:** **Không** đưa vào cơ chế DialogueGCN/MMGCN/hypergraph. Viết một
  đoạn trích dẫn §5.1 + Eqs 2–4 để chứng minh rằng các clip ViEmoSpeech không mang cạnh liên-phát-ngôn
  hay liên-người-nói (đơn người nói theo thiết kế, cắt VAD∩turn), do đó toàn bộ lợi ích của họ graph
  không khả dụng — đây là một quyết định về phạm vi (scoping), không phải một thiếu sót. Điều này giúp
  chặn trước câu hỏi của người phản biện "tại sao không có mô hình bối cảnh hội thoại?"
- **V-G eval protocol:** Áp dụng Weighted-F1 + Macro-F1 làm headline phân loại (khớp với quy ước ERC
  mà M3ED/MELD báo cáo, do đó con số 7-lớp của chúng ta có thể so sánh được), **nhưng bổ sung rõ ràng
  CCC cho V/A và recall@floor cho distress** và ghi chú trong văn bản rằng ERC không báo cáo những
  chỉ số này — các chỉ số liên tục + an toàn của chúng ta đến từ dòng SER/lâm sàng, không phải survey
  này. Sử dụng quy mô 990-dial/24,449-utt/56-series của M3ED làm hàng neo "corpus định dạng
  VN-drama có thể so sánh" trong bảng định vị V-H (cùng với THAI-SER, MSP-Podcast, VNEMOS).
- **V-C text branch under ASR noise:** Coi phát hiện "text-dominant" của survey là *có điều kiện* và
  kiểm tra điều kiện đó. Vì text dominance của ERC giả định bản chép lời sạch + bối cảnh, hãy chạy
  ablation V-C dưới dạng **gold-caption so với đầu vào PhoWhisper-ASR** cho nhánh văn bản trên cùng
  các clip; mức sụt giảm dự kiến là nội dung thực nghiệm cho lập luận về register của chúng ta. Giữ
  cấu hình PhoBERT nhẹ (bối cảnh phát ngôn đơn ngắn, không có mạng lịch sử hội thoại — Eqs 2–4 không
  áp dụng).
- **V-A/V-G conflict slice:** Đưa một lát cắt xung đột phụ tone×emotion / âm học–ngữ nghĩa vào đánh
  giá và ghép nó với một **cơ chế bảo vệ neo-audio** (modality dropout hoặc một head audio-only phụ)
  lấy trực tiếp từ các biện pháp khắc phục "conflict modality" ở §6. Điều này biến vấn đề mở của
  survey thành đóng góp đo lường được của chúng ta.

### Child mental-health / ViEmoSpeech transfer lens

ViEmoSpeech là SER **cấp phát ngôn, clip đơn, ngôn ngữ có thanh điệu (VN), phim truyền hình diễn xuất**
— ba giả định cốt lõi của survey không đúng, và việc nói rõ điều này chính là nhận định chuyển giao:

- **Context-modeling KHÔNG chuyển giao (lưu ý trung tâm nhất).** Bản chất của ERC là hội thoại: các
  mô hình tuần tự cấp tình huống + embedding/đồ thị cấp người nói (§4.2). Các clip của chúng ta được
  cắt tại VAD∩speaker-turn và là đơn người nói theo thiết kế — không có lịch sử hội thoại, không có
  người đối thoại để theo dõi, không có tín hiệu chuyển đổi cảm xúc qua các lượt lời. Mọi thứ mà survey
  liệt kê là *lợi thế* của các phương pháp graph-based (§5.1) đều không áp dụng được. Nhận định chuyển
  giao: **fusion-based (§5.2) chuyển giao được; graph-based và context cấp người nói (§4.2, §5.1)
  thì không.** Đây là kết quả góc nhìn quan trọng nhất — phần lớn số trang của survey được dành cho cơ
  chế mà chúng ta cố tình không sử dụng.
- **Front-end audio là pre-SSL — các kết luận fusion của survey đứng trên các đặc trưng audio yếu.**
  Các bộ trích xuất audio ở Table 2 (openSMILE/COVAREP/librosa) có trước WavLM/emotion2vec (mà
  bimodal-01/12 xác lập là mặc định). Một kết luận "text-dominant" được đưa ra khi nhánh audio là các
  mô tả thủ công một phần là hệ quả của một kênh audio yếu; với một backbone SSL audio mạnh thì sự cân
  bằng modality sẽ dịch chuyển. Chúng ta không nên kế thừa "văn bản chiếm ưu thế" như một quy luật —
  nó phụ thuộc vào bộ trích xuất audio, và nhánh WavLM(+phonation) của chúng ta thay đổi tiền đề này.
- **Tone×emotion vẫn chưa được chạm tới — khoảng trống mới xác nhận lần thứ 16.** M3ED (tiếng Quan
  Thoại, 56 series TV) nằm trong bộ benchmark, nhưng "tone" chỉ xuất hiện như một từ ngôn điệu chung;
  không có phương pháp nào được khảo sát coi thanh điệu từ vựng là một biến và không có chỉ số nào có
  điều kiện dựa trên nó. Artifact gần nhất là độ nổi bật ngôn điệu cấp từ của ACE (Akan). Yêu cầu về
  kênh F0/phonation cho thanh điệu từ vựng×cảm xúc của ViEmoSpeech (dựa trên vn-13 Chang + vn-06 Shen)
  vẫn chưa được yêu sách trong toàn bộ tài liệu MERC.
- **Ethics / release lens (§6 FAIR).** Chính sự phê phán FAIR của survey — dataset bị hạn chế bản
  quyền, đơn ngữ, cấp phép không nhất quán, khó tái sử dụng — chính xác là khoảng trống mà định dạng
  phát hành chỉ-features, timestamps+labels+speaker-ids, CC-BY của chúng ta trả lời cho một nguồn phim
  truyền hình không thể được tái phân phối. Survey đóng khung "cấp phép mở + metadata chuẩn hóa qua
  các liên minh hợp tác" như hướng phát triển tương lai; thiết kế release của chúng ta là một thể hiện
  cụ thể. Không có nội dung đạo đức đặc thù trẻ em ở đây (corpus là phim truyền hình diễn xuất người
  lớn), do đó khung acted-drama-proxy (V-F) không thay đổi — survey không đưa ra điểm neo lâm sàng hay
  hướng tới trẻ vị thành niên nào.

### Limitations & open questions for ViEmoSpeech

- **Contradiction #1 (so với sự tổng hợp xuyên suốt đang nổi lên + vn-08):** survey nâng một họ phụ
  **"Text-Dominant Modality"** (§5.2b) lên thành một cơ chế phổ biến, hiệu quả — văn bản là lõi đáng
  tin cậy, audio/visual là phụ trợ. Điều này mâu thuẫn trực tiếp với phát hiện VN-ASR của vn-08 rằng
  văn bản "gần như vô dụng" (38.7–44.1% chỉ-văn-bản) và sự tổng hợp phụ thuộc-register (bản chép lời
  gold sạch → văn bản chiếm ưu thế; ASR tự phát nhiễu → audio chiếm ưu thế). Survey không bao giờ nêu
  rõ rằng tính chiếm ưu thế của văn bản là có điều kiện dựa trên bản chép lời sạch + bối cảnh hội
  thoại — nhưng mọi corpus mà nó trích dẫn (MELD/IEMOCAP/M3ED) đều cung cấp chính xác những điều đó.
  **Giải pháp cho chúng ta:** trích dẫn trục của Figure 4, nhưng đảo primary sang audio và *đo lường*
  sự phụ thuộc register (ablation gold-caption vs ASR) thay vì kế thừa mặc định của survey.
- **Contradiction #2 (so với phát hiện backbone audio của bimodal-01/08/12):** bảng đặc trưng audio
  của survey (Table 2: openSMILE/COVAREP/librosa) là pre-SSL, trong khi chương trình của chúng ta và
  bimodal-01/08/12 coi WavLM/emotion2vec/Whisper-encoder là baseline. Do đó bất kỳ kết luận cân bằng
  modality nào trong survey này đều không thể chuyển giao được cho một hệ thống có audio-SSL mạnh —
  đây là một khoảng trống, không phải một hướng dẫn.
- **Gap: không có quy ước affect liên tục (CCC).** Đánh giá ERC chỉ là F1 phân loại (§3); V/A liên tục
  của AVEC bị gộp vào cách dùng phân loại. Các chỉ số V/A-CCC và distress-recall@floor của chúng ta
  nhận được **hỗ trợ bằng không** từ survey này — V-G phải lấy nguồn từ MSP-Podcast (bimodal-12) và
  bài tổng quan lâm sàng (bimodal-10). Không trích dẫn survey này cho đánh giá liên tục (dimensional).
- **Gap: survey không có con số để vượt qua.** Đây là một phân loại (taxonomy), không phải một bảng
  xếp hạng; không có điểm số phương pháp nào được báo cáo. Nó di chuyển V-A/V-G/V-C như một *bản đồ*,
  và không thể đóng vai trò một hàng baseline (khác với arXiv:2412.09829, THAI-SER, hay VNEMOS). Mọi
  con số định lượng cho ViEmoSpeech vẫn phải đến từ các bài báo gốc, không phải từ đây.
- **Open question:** các chương trình nghị sự "conflict modality" và "effective modality selection" ở
  §6 (uncertainty-aware fusion, learnable modality gates, modality dropout) được nêu tên là *chưa được
  giải quyết*. Lát cắt xung đột tone×emotion + cơ chế bảo vệ neo-audio của ViEmoSpeech sẽ là một câu
  trả lời cụ thể trong khoảng trống đã được thừa nhận — nhưng survey không đưa ra công thức nào, chỉ
  có phát biểu vấn đề.
