# Paper 20 — AVT-CA: Multimodal Emotion Recognition using Audio-Video Transformer Fusion with Cross Attention

> Bản dịch tiếng Việt của [20-avt-ca.md](20-avt-ca.md) — cập nhật 2026-07-10.

- **Authors:** Joe Dhanith P R, Shravan Venkatraman, et al.
- **Venue / year:** arXiv preprint 2024 (v4 01/2026; preprint-only — chưa thấy acceptance)
- **Links:** abs https://arxiv.org/abs/2407.18552 · PDF `pdfs/20-avt-ca.pdf` · code github.com/shravan-18/AVTCA
- **Group:** audio-visual (đối chứng)

**Summary:** Hierarchical visual attention (channel+spatial+local) fuse với audio qua cross-attention transformer; eval CMU-MOSEI, RAVDESS, CREMA-D.

**Relevance to Pebble:** Reference engineering cho fusion ablation; rank thấp vì chưa peer-reviewed.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled Pebble profile (at analysis time).** Primary stream: ordinal
suicide-risk **text** classification — teacher-LLM silver labels, gold-holdout
eval on held-out clinical CSSRS, subject-level splits, ordinal-aware losses/metrics
(QWK/MAE), reproducible-by-construction (`docs/intent/constraints.md`). Adjacent
**voice** stream (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`):
heterogeneous 3-head MTL trên một backbone **frozen emotion2vec / WavLM-Large** —
emotion (CE), affect valence+arousal (**CCC loss**), crisis (BCE dưới một **hard
recall floor ≥0.90**), cân bằng bởi **Kendall uncertainty weighting**, huấn luyện trên
RAVDESS frozen features; voice+text fusion là hướng đi tiếp theo (deferred).

### Analysis — AVT-CA (audio-video cross-attention fusion)
- **Overlap:** 4% (peripheral) — D1=0, D2=0, D3=1, D4=0, D5=0, D6=0, D7=0
  - Formula: (3·0 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·0) / 26 × 100 = 1/26 × 100 ≈ 4%.
- **Closest on:** D3 (dataset) — huấn luyện/đánh giá trên **RAVDESS** và **CREMA-D**;
  RAVDESS chính là corpus mà voice MTL probe của Pebble đang dùng. Điểm chung
  single-corpus đó là mối liên hệ thực sự duy nhất.
- **Why the rest score 0:** chỉ một tác vụ emotion **categorical** đơn nhiệm (Angry/Disgust/
  Fear/Happy/Neutral/Sad), chỉ báo cáo accuracy+F1 — không có head continuous/affect, nên
  không có heterogeneous MTL (D1=0) và không có principled loss balancing (D5=0); đây là
  general MER, không liên quan mental-health/crisis và không có recall constraint (D2=D6=0);
  không có teacher-LLM distillation (D4=0); backbone là một **custom audio-video transformer**
  tùy biến với channel/spatial attention trên các pre-extracted features, **không phải**
  emotion2vec/WavLM SSL mà voice stream của Pebble đang dùng (D7=0). CMU-MOSEI được dùng theo
  kiểu categorical, không phải sentiment-intensity regression.
- **Best point (Method to adopt — forward direction, low current leverage):** phần
  **intermediate transformer fusion + agreement-driven cross-attention** — module
  cross-attention chọn lọc để tăng cường các tín hiệu audio-visual *nhất quán lẫn nhau*
  và triệt tiêu các tín hiệu nhiễu, báo cáo mức tăng ablation lớn so với early/late fusion.
  - **How to apply to Pebble:** đưa vào kho làm công thức tham chiếu cho bước
    **voice+text fusion** (deferred) — thay nhánh video bằng frozen text encoder và
    gate các token voice↔text theo mức độ đồng thuận lẫn nhau, để một voice frame nhiễu
    không thể lấn át một tín hiệu text-risk đáng tin cậy; hiện chưa khả thi ở giai đoạn
    này (mới chỉ có single-modality voice MTL heads + primary text), nên nó vẫn chỉ là
    một citation cho chương fusion, chưa phải một task.
- **Caveats:** **preprint-only** (arXiv v4, chưa peer review) — coi mọi con số là
  **chưa được kiểm chứng**; các kết quả báo cáo RAVDESS 96.11% acc / CREMA-D / MOSEI 95.84%
  là kết quả **within-distribution** trên từng benchmark riêng lẻ, **không phải** gold-holdout,
  nên chúng không phải baseline để Pebble so sánh vượt qua. Loss function không được nêu rõ
  trong abstract/intro; được suy luận là single-task CE dựa trên cách báo cáo chỉ
  accuracy/F1 và tập nhãn categorical (đã đọc trang 1–2, 7–9; các phương trình loss trong
  phần method chưa được xác minh đầy đủ).

## Deep research — full-PDF read (2026-07-10)

> Scope note: đây là paper đối chứng audio-**visual** (overlap ưu tiên thấp nhất, ~4%,
> preprint-only). Theo task brief, phần này chủ đích **cân xứng** (proportionate) — nhiệm
> vụ của nó là xác nhận, bằng bằng chứng, rằng cơ chế fusion không đóng góp gì thêm ngoài
> các template audio-text/audio-audio fusion đã trích xuất từ bimodal 03/06/07/17
> và vn-07, đồng thời rút ra điều duy nhất nó *thực sự* đóng góp: một **V-G negative
> exemplar** rõ ràng (các con số benchmark bị thổi phồng do leak). Phần này ngắn có chủ đích.

### Source-access note

Đọc toàn văn từ file PDF local `docs/papers/bimodal-ser/pdfs/20-avt-ca.pdf` qua
`pdftotext -layout` (898 dòng; abstract, các mục I–VI, toàn bộ Bảng I–V, và danh mục
tài liệu tham khảo đều đã đọc). Xác minh trên web:
- Truy vấn `AVT-CA Audio-Video Transformer Fusion Cross Attention arXiv 2407.18552 RAVDESS
  96.11 CMU-MOSEI` -> phân giải ra arXiv abstract `https://arxiv.org/abs/2407.18552`, HTML
  `https://arxiv.org/html/2407.18552v4`, và bài literature review của Moonlight
  `https://www.themoonlight.io/en/review/multimodal-emotion-recognition-using-audio-video-transformer-fusion-with-cross-attention`.
- **Publication status (đã đối chiếu):** chỉ mới ở dạng preprint. arXiv:2407.18552v4 [cs.MM]
  đề ngày 20/01/2026; ResearchGate liệt kê là "Request PDF" (preprint), không tìm thấy chấp
  nhận đăng tại journal/conference nào. Stub local PDF ghi "v4 01/2026, preprint-only" là
  chính xác. Do đó mọi con số dưới đây đều là **kết quả preprint within-distribution, chưa
  qua peer-review**.
- Code repo được xác nhận vẫn tồn tại: `github.com/shravan-18/AVTCA`.

### What the paper actually does

- **Task/modalities.** Bài toán phân loại emotion **categorical** đơn nhiệm (6–8 lớp, tùy
  dataset) trên **audio + video (khuôn mặt) frames**. **Hoàn toàn không có nhánh text/ASR** —
  nhãn đúng phải là "audio-video" thay vì audio-text như stub cũ. Loss được xác nhận là
  **cross-entropy** thuần túy (Mục III-D, `L_CE = -1/N sum sum y log yhat`); optimizer Adam,
  lr 0.01, weight decay 0.001, batch 8, 128 epochs, huấn luyện ~72 giờ (Mục IV). (Phần
  "inferred single-task CE" trong stub cũ nay đã được xác nhận từ phần method. Corroborated.)
- **Architecture.** Nhánh video = chồng attention phân cấp: channel attention +
  spatial attention + local (patch) feature extractor + hai khối inverted-residual
  (depthwise-separable conv) (Mục III-A2). Nhánh audio = hai khối Conv1D->BN->ReLU->MaxPool
  (Mục III-A1). Fusion = **intermediate transformer fusion** (mỗi modality có các khối
  self-attention transformer riêng) theo sau bởi module **bidirectional cross-attention**:
  audio-as-query trên video-as-key/value (`o_AV`) và video-as-query trên audio-as-key/value
  (`o_VA`), kết hợp với residual self-attention (Mục III-B/C). Bước cuối: max-pool từng
  modality -> cộng theo phần tử -> FC -> softmax (Mục III-D).
- **Datasets (Mục IV-A, Bảng I).** RAVDESS (7,356 file, 24 diễn viên), CMU-MOSEI (~23,500
  utterance, 1,000+ speaker YouTube), CREMA-D (7,442 clip, 91 diễn viên). Chia tập =
  **random 80/20 train/val** (Bảng I "Train (80%) / Val (20%)"); **không có
  speaker-disjoint split, không có held-out OOD set, không có cross-corpus test** nào được
  nhắc đến.
- **Headline results (Bảng II–IV) — đã đối chiếu** (arXiv HTML + Moonlight review khớp
  với PDF local):
  - RAVDESS: AVT-CA **96.11% acc / 93.78% F1**; kế đến CNN [57] 95.95 / 92.17.
  - CMU-MOSEI: AVT-CA **95.84% acc / 94.13% F1**; kế đến MAG-BERT 84.71 / 84.51.
  - CREMA-D: AVT-CA **94.13% acc / 94.67% F1**; kế đến DE-III 83.70 / 79.50.
- **Ablation (Bảng V) — xấp xỉ** (bảng bị lỗi định dạng khi trích xuất, nhưng các ô đọc
  được vẫn tự nhất quán): các cấu hình chỉ dùng một cơ chế đơn lẻ cho kết quả thấp hơn hẳn —
  IT-4 (intermediate-transformer, 4 head) 76.41 / 67.72 / 71.50 acc trên
  RAVDESS/MOSEI/CREMA; CT-4 (cross-attention, 4 head) 76.00 / 64.94 / 72.10 — và mô hình
  đầy đủ **IT-4+CT-4 nhảy lên 96.11 / 95.84 / 94.13**, được tác giả mô tả là "mức tăng
  xấp xỉ 20% về accuracy và F1-score" (Mục V-D). Ablation chỉ thay đổi
  **số attention head (1 so với 4) và khối fusion nào được dùng**; **không có ablation
  audio-only so với video-only**, và vì không có text nên **không có ablation ASR-noise**.

### Parts directly useful for ViEmoSpeech (each tagged to a Decision ID + transfer risk)

Chỉ có hai decision nằm trong phạm vi, và một trong hai lại là một phát hiện dạng
"không nên áp dụng / trùng lặp" — bản thân điều đó chính là deliverable được yêu cầu.

1. **V-A (fusion) — TRÙNG LẶP; không áp dụng gì.** Cross-attention của AVT-CA là
   **bidirectional cross-modal attention** kiểu sách giáo khoa (softmax(Q_a K_v / sqrt(d)) * V_v
   và đường đối xứng video->audio). Cách diễn giải "agreement-driven / mutually-consistent
   cue reinforcement" trong abstract thực chất chỉ là tính chất thông thường của softmax
   attention — **không có cơ chế token-selection tường minh, không có Top-K distillation,
   không có gating, không có noise-gate operator nào** trong các phương trình (Mục III-B/C).
   Mọi thứ nó làm đều đã được các tài liệu Pebble đang có bao phủ, và bao phủ *tốt hơn cho
   register của Pebble*:
   - **RJCMA (bimodal-17)** cùng ý tưởng — joint cross-modal attention trên **audio-visual** —
     nhưng với đúng mục tiêu Pebble cần (**CCC loss L=1-rho_c** cho V/A) thay vì flat CE.
   - **CASE/FAS (vn-07)** đã cho sẵn cơ chế token-selection *thật* (Top-K L2-saliency
     token distillation + Q-Former) mà AVT-CA chỉ gợi ý sơ sài.
   - **BCAF (bimodal-07)** đã cho sẵn noise-aware fusion cùng cơ chế deep-supervision an
     toàn theo từng modality.
   - Phần hierarchy channel/spatial/local đặc thù cho video là **không thể chuyển giao**
     — nó vận hành trên tensor khuôn mặt `R^{HxWxC}`; ViEmoSpeech không có modality
     hình ảnh và thay video bằng text.
   - **Transfer risk (fatal):** toàn bộ kiến trúc là audio<->**video**; phép thay thế của
     Pebble là audio<->**text/ASR**. Cross-modal attention khi luồng thứ hai là chuỗi token
     ASR nhiễu là một bài toán khác hẳn (căn chỉnh, tokenization, lỗi ASR) mà paper này
     chưa từng chạm tới. **Recommendation for V-A: dẫn nguồn như một ví dụ khác của
     bidirectional cross-modal attention chuẩn; không áp dụng gì; shortlist fusion vẫn giữ
     FAS / gated / BCAF.**

2. **V-G (eval) — NEGATIVE exemplar mạnh.** Bộ kết quả này là một trường hợp kinh điển của
   benchmarking bị thổi phồng do leak, và việc nêu tên nó giúp làm rõ hơn protocol ADR-002
   của Pebble:
   - **Random 80/20 split trên RAVDESS 24-diễn-viên / CREMA-D 91-diễn-viên** (Bảng I) =
     gần như chắc chắn **speaker leakage** (clip của cùng một diễn viên nằm cả ở train lẫn
     val). 96.11% trên RAVDESS với random split nằm cùng nhóm với các con số VN bị leak
     (vn-08 86.6, vn-10 0.87) và đối lập với các anchor speaker-disjoint trung thực
     (THAI-SER WA~60, MSP naturalistic macro-F1~0.30, bimodal-15 naturalistic ceiling
     ~0.65 UAR).
   - **95.84% trên CMU-MOSEI — một corpus in-the-wild từ YouTube — là dấu hiệu cảnh báo.**
     SOTA multimodal thực tế trên MOSEI chỉ khoảng ~84% (baseline mạnh nhất của chính họ,
     MAG-BERT, đạt 84.71); việc nhảy vọt lên 95.84% trên dữ liệu *in-the-wild* trong khi
     RAVDESS/CREMA-D (dữ liệu diễn) đạt 96.11/94.13 nghĩa là mô hình cho **accuracy gần
     như giống hệt nhau trên dữ liệu diễn và dữ liệu in-the-wild**, điều này không đúng với
     cách register generalization thường vận hành (x. bimodal-01 text collapse từ 63->14
     khi đổi register; trục register là có thật). Đây là dấu hiệu của một evaluation
     artifact, không phải một mô hình mạnh thực sự.
   - **Mức "tăng ~20% qua ablation" khi thêm attention head** (Bảng V, Mục V-D) là quá lớn
     một cách phi thực tế cho một thay đổi chỉ ở số lượng head, càng củng cố nghi vấn rằng
     các con số headline không đo đúng cái chúng tuyên bố.
   - **Transfer risk:** các con số này **không phải là baseline để vượt qua** và không bao
     giờ được đưa vào bảng baseline của Pebble như một mục tiêu. Giá trị *thực sự* của
     chúng là làm citation cảnh báo cho việc vì sao ViEmoSpeech công bố con số
     speaker-disjoint + whole-series-holdout kèm bootstrap CI.
   - **Recommendation for V-G:** dẫn AVT-CA vào hàng "những gì không nên làm" cùng với
     RandomSplit thiếu định nghĩa rõ ràng của bimodal-11 và CV bị leak của vn-08/vn-10 —
     random split trong cùng corpus + accuracy phẳng một cách phi thực tế giữa dữ liệu
     diễn/in-the-wild = đúng loại sai lầm mà protocol đánh giá của Pebble được thiết kế để
     tránh.

### How each part helps ViEmoSpeech succeed (concrete actions)

- **V-A:** Không cần thêm thí nghiệm fusion mới. Trong đoạn related-work/fusion-shortlist
  của method paper, thêm một câu: "bidirectional cross-modal attention (ví dụ AVT-CA,
  RJCMA) là template chung; chúng tôi chọn biến thể FAS có token-selecting vì luồng thứ
  hai của chúng tôi là text ASR nhiễu, không phải video đã căn chỉnh." Kết quả: đóng lại
  nhánh audio-visual của việc tìm kiếm cho V-A bằng một citation, tiết kiệm một ablation arm.
- **V-G:** Thêm một hàng tường minh "leak-inflated benchmarks" vào bảng baseline/eval-protocol
  trong method paper, liệt kê AVT-CA (RAVDESS 96.11 / MOSEI 95.84, random 80/20 split) như
  một ví dụ cụ thể về speaker leakage trong cùng corpus, và đặt cạnh con số
  speaker-disjoint trung thực của Pebble để làm rõ sự tương phản cho reviewer.

### Child / VN-SER transfer lens

Rất ít, vì paper này lệch register trên mọi trục quan trọng với Pebble:
- **Không có tone, không có tiếng Việt, không có phonation.** Chỉ là MER audio-visual
  thuần túy trên corpus tiếng Anh diễn/YouTube -> không đóng góp gì cho claim tone x
  emotion (V-D không thay đổi; con số thống kê "0/N paper đo lexical-tone x emotion"
  không đổi vì paper này).
- **Không có nhãn dimensional, không có distress.** Chỉ có một head categorical duy nhất
  -> không có gì cho V/A-CCC (V-B/E) hay distress recall-floor (V-F). RAVDESS là corpus
  chung với voice probe của Pebble, nhưng AVT-CA dùng nó theo kiểu categorical với split
  bị leak, nên ngay cả điểm chung corpus đó cũng không cho ra con số nào dùng được.
- **Ethics/mitigation:** đóng góp duy nhất được kế thừa là bài học về eval-integrity — với
  một corpus hướng đến trẻ em, một con số benchmark bị thổi phồng còn tệ hơn một con số
  thấp nhưng trung thực, vì nó có thể bị dùng để biện minh cho việc tự động hóa không an
  toàn. AVT-CA là ví dụ phản diện cụ thể.

### Limitations & open questions for ViEmoSpeech (>=1 explicit contradiction/gap)

- **Mâu thuẫn với bimodal-15 (Schuller replication, IEEE TAFFC 2026) và vn-11
  (THAI-SER):** bimodal-15 cho thấy ceiling naturalistic speaker-independent trung thực
  chỉ khoảng **~0.65 UAR**, và anchor clean-acted trung thực của THAI-SER là
  **WA 59.80 / UA 57.81**. Con số 94–96% acc của AVT-CA trên cùng *loại* dữ liệu diễn
  (và cả trên MOSEI in-the-wild) hoàn toàn không tương thích với các ceiling trung thực
  đó — khác biệt nằm ở protocol split (random-within-corpus so với speaker-disjoint).
  Điều này củng cố trực tiếp quyết định của Pebble về việc công bố con số speaker-disjoint
  và gắn cờ cảnh báo cho bất kỳ mục leaderboard nào dùng random-split.
- **Điểm mù không-ASR / không-text (giống mọi paper fusion đã đọc):** AVT-CA hoàn toàn
  không có modality text, nên giống RJCMA/BCAF/WavFusion, nó chưa bao giờ đối mặt với
  nhiễu ASR — trục mà đóng góp thực sự của ViEmoSpeech nằm ở đó. Điều này xác nhận
  ablation về ASR-robustness vẫn còn là vùng chưa ai khai thác.
- **Câu hỏi mở (không chặn tiến độ):** liệu mức nhảy "~20% từ việc thêm head" ở Bảng V
  phản ánh một lỗi báo cáo/gán nhãn trong bảng bị lỗi định dạng, hay là một kết quả thật
  (và do đó đáng ngờ) — không liên quan đến kế hoạch của Pebble, chỉ ghi chú lại để con
  số này không bao giờ bị trích dẫn như một con số đóng góp thành phần thực sự.
