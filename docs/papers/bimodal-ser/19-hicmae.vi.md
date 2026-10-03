# Paper 19 — HiCMAE: Hierarchical Contrastive Masked Autoencoder for Self-Supervised Audio-Visual Emotion Recognition

> Bản dịch tiếng Việt của [19-hicmae.md](19-hicmae.md) — cập nhật 2026-07-10.

- **Authors:** Licai Sun, Zheng Lian, Bin Liu, Jianhua Tao
- **Venue / year:** Information Fusion (Elsevier), 2024
- **Links:** abs https://arxiv.org/abs/2401.05698 · PDF `pdfs/19-hicmae.pdf` (bản arXiv; journal paywalled)
- **Group:** audio-visual (đối chứng)

**Summary:** Masked-modeling + contrastive pretraining trên audio-visual không nhãn, fine-tune trên 9 dataset categorical/dimensional.

**Relevance to Pebble:** Cùng logic "pretrain rẻ, fine-tune trên nhãn khan hiếm" như GoEmotions warm-start + Gemini silver labels.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Profile assembled at analysis time** (from `docs/intent/constraints.md` + `docs/spec/capabilities/voice-multimodal.md` + `docs/tasks/voice-mtl-heads.md`): Ý định chính của Pebble là bài toán ordinal suicide-risk trên *văn bản* với nhãn yếu từ LLM dưới chế độ đánh giá trung thực/gold-holdout — HiCMAE không đụng đến phần đó. Bề mặt liên quan là **luồng giọng nói lân cận**: một *backbone SSL âm thanh đóng băng* (WavLM-Large / emotion2vec) + trunk SUPERB dùng chung mang **ba head dị chủng** — emotion (CE), affect valence/arousal (CCC), crisis (BCE dưới một sàn recall bắt buộc) — được cân bằng bằng Kendall uncertainty weighting, với **voice+text fusion là hướng phát triển chính**.

### Analysis — HiCMAE (audio-visual SSL emotion)
- **Overlap:** D1=1, D2=0, D3=1, D4=0, D5=0, D6=0, D7=1 → (3·1 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·1)/26 = 5/26 = **19% (peripheral)**
- **Closest on:** D1 (một backbone SSL phục vụ *cả* categorical emotion lẫn valence *dimensional* — cùng phép chia categorical+continuous mà voice MTL heads của Pebble nhắm tới, dù HiCMAE fine-tune từng task riêng biệt chứ không phải các head dị chủng đồng thời) và D7 (một backbone SSL audio(-visual) cho emotion, cùng họ "frozen-SSL-features + downstream probe" với WavLM/emotion2vec, nhưng là audio-*visual* chứ không phải audio-only, và tự huấn luyện trên VoxCeleb2 thay vì dùng checkpoint WavLM/emotion2vec).
- **Best point (Baseline to beat):** HiCMAE báo cáo WAR/WF1 theo từng dataset trên chính các corpus mà luồng giọng nói của Pebble sử dụng — RAVDESS, IEMOCAP, CREMA-D, MSP-IMPROV (categorical) và valence qua Pearson (dimensional) — kèm code công khai + checkpoint đã pretrain, tức là một trần *bimodal SSL* đã công bố cho SER trên các benchmark chung.
  - **How to apply to Pebble:** trong bài viết `voice-mtl-heads`, trích WAR trên RAVDESS/IEMOCAP của HiCMAE làm cận trên audio-visual SSL, và đóng khung các con số frozen-probe audio-only của Pebble như phần so sánh trung thực, ít tài nguyên hơn — cùng cảnh báo "modality gap" mà ghi chú proxy-label đã có; không coi đây là baseline apples-to-apples (nó có thêm kênh visual mà Pebble không có).
- **Caveats:** Bản journal bị paywall; điểm số được chấm từ PDF arXiv (abstract + Sec. 1–3 + Fig. 2 radar) — chưa đọc đầy đủ các bảng theo từng dataset và trọng số loss. D5=0/D6=0 chắc chắn (không có cơ chế cân bằng MTL nguyên tắc, không có mục tiêu safety/recall — các loss của HiCMAE là reconstruction + contrastive, không phải task-balanced heads); D1 giữ ở 1 vì categorical+dimensional là hai lần fine-tune riêng biệt, không phải các head dị chủng đồng thời. Không có mental-health/crisis (D2=0) và không có distillation từ teacher-LLM (D4=0).

## Deep research — full-PDF read (2026-07-10)

> Phân tích dựa trên **profile ViEmoSpeech hiện tại + Decision Register V-A…V-H** (từ
> `docs/tasks/paper-deep-analysis.md`, 2026-07-10), KHÔNG phải profile text-stream cũ trong mục
> "Analysis" bên trên (mục đó đã được lưu trữ và giữ nguyên). HiCMAE là một paper **đối chứng
> SSL audio-VISUAL**: nó có mặt ở đây để kiểm tra xem công thức pretraining tự giám sát, cơ chế
> fusion phân cấp, hay mục tiêu contrastive xuyên-modal của nó có chuyển giao được sang chế độ
> **audio+text, không video, backbone đóng băng, tone×emotion tiếng Việt** của ViEmoSpeech hay
> không. Trả lời ngắn gọn: nó dịch chuyển V-B và V-A chủ yếu như bằng chứng **phủ định / có giới
> hạn**, và V-D như một trường hợp làm rõ sự không-chuyển-giao.

### Source-access note

Đọc toàn bộ PDF qua `pdftotext "docs/papers/bimodal-ser/pdfs/19-hicmae.pdf" -` (arXiv:2401.05698v2,
1 Apr 2024) — phần method §3 (mọi phương trình), implementation §4.1, tất cả các bảng kết quả
(Tables 2–16), các ablation, và phân tích lỗi. Bản journal bị paywall (Elsevier). Đã kiểm chứng
qua web:

- **Venue/DOI** — WebSearch `HiCMAE Hierarchical Contrastive Masked Autoencoder Information Fusion
  2024`; xác định là *Information Fusion* **vol. 108, article 102382, 2024** (ScienceDirect PII
  `S156625352400160X`; ISSN 1566-2535 = Information Fusion) và OpenReview `6N6I6FjHyK`. Status ✔.
  Bản PDF local là preprint của tác giả; không phát hiện xung đột số liệu nào giữa preprint và
  abstract/hình minh họa của venue tìm được qua search.
- **Release** — WebFetch `github.com/sunlicai/HiCMAE`: **giấy phép MIT**; **cả code pretraining
  lẫn code fine-tuning downstream** đều công khai; **một checkpoint kích thước base đã pretrain trên
  VoxCeleb2 (audio-visual)** được phát hành qua SharePoint, cùng các checkpoint và log fine-tune
  theo từng fold cho CREMA-D / MAFW. Status ✔. **Không có checkpoint audio-only và không đề cập
  đến việc sử dụng chỉ-audio** — artifact được phát hành là một cặp encoder audio-visual.

### What the paper actually does

**Objective.** Pretraining tự giám sát audio-VISUAL cho nhận diện cảm xúc (AVER), sau đó fine-tune
theo từng dataset. Hai tín hiệu SSL được kết hợp (§3.3, Eq. 11): masked audio-visual reconstruction
(MSE trên các token bị mask, Eq. 8) **cộng với** hierarchical cross-modal contrastive learning
(InfoNCE đối xứng giữa các cặp clip audio↔video, Eqs. 9–10). Tổng loss `L = L_MAE + λ·L_HCMCL`.

**Chiến lược "ba mũi" phân cấp** (điểm mới của paper):
1. **Kết nối tắt phân cấp (hierarchical skip connections)** (kiểu U-Net) từ các layer encoder
   **4/7/10** vào các layer decoder 2/3/4 qua multi-head cross-attention (Eq. 7) — dẫn dắt các layer
   *trung gian*, không chỉ layer trên cùng.
2. **Hierarchical cross-modal contrastive learning (HCMCL)** áp dụng ở chính các layer trung gian đó
   (không chỉ layer cuối), thu hẹp dần khoảng cách modality audio-video (§3.2).
3. **Hierarchical feature fusion (HFF)** tại thời điểm fine-tune: đặc trưng cuối cùng là
   `Concat(cross-modal pooled a→v, v→a, tổng có trọng số học được của mọi layer audio e_a, mọi layer
   video e_v)` (Eq. 12), tức là **trọng số học được theo từng layer trên toàn bộ stack encoder**,
   không chỉ hidden state cuối cùng.

**Architecture (§4.1).** Hai encoder Transformer riêng theo modality `Ns=10` layer + một fusion
encoder xuyên-modal `Nf=2` (MHCA hai chiều, Eqs. 5–6) + hai decoder nhẹ `Nd=4`. Ba kích thước theo
độ rộng hidden: **HiCMAE-T (C=256), -S (C=384), -B (C=512)**.

**Pretraining recipe (§4.1) — công thức chịu trách nhiệm chính cho V-B:**
- Data: **tập dev VoxCeleb2, 1,092,009 clip** (bài phát biểu người nổi tiếng, audio-visual)
  [✔ §4.1].
- Masking: **audio 80%, video 90%** (tube masking cho video, random cho audio) [✔ §3.1.1].
- `λ = 0.0025`, InfoNCE temperature `τ = 0.07` [✔ §4.1].
- **100 epoch, 4× Tesla V100, batch 160, base LR 3e-4, ~5 ngày** [✔ §4.1]. Fine-tune: 50–100 epoch,
  batch 56, base LR 1e-3.

**Downstream results (9 dataset, categorical + dimensional).** Các mức tăng chủ đạo nhờ
audio-visual [tất cả ✔, có trích bảng]:
- **CREMA-D 6-lớp** (diễn, subject-independent 5-fold): HiCMAE-B **WAR 84.89 / UAR 84.91**, so với
  SSL tốt nhất trước đó VQ-MAE-AV+Query2Emo 80.40 → **+4.49 WAR** (Table 6).
- **MAFW 11-lớp** (in-the-wild): HiCMAE-B **UAR 42.65 / WAR 56.17**, so với supervised SOTA T-MEP
  37.17 / 51.15 → **+5.48 UAR / +5.02 WAR** (Table 2).
- **DFEW**: HiCMAE-B A+V **WAR 75.01** so với T-MEP 68.85 → **+6.16 WAR** (Table 4).
- **RAVDESS** A+V WAR 87.99 (+3.19 so với VQ-MAE-AV, Table 9); **IEMOCAP** 4-lớp A+V WAR 68.36
  (+5.62 so với AVBERT, Table 10); **MSP-IMPROV** A+V WAR 74.95 (Table 8).
- **Dimensional Werewolf-XL** A+V (Table 11): HiCMAE-B **valence PCC 69.23 / CCC 64.81** nhưng
  **arousal PCC 33.74 / CCC 31.85**, dominance PCC 40.66 / CCC 37.54 — valence vượt xa arousal.
- **AVCAffe** A+V arousal/valence weighted-F1 43.18 / 44.20 (Table 12).

**Các hàng audio-only quan trọng (bị chôn vùi, và mang tính quyết định với chúng ta).** Khi chỉ
fine-tune encoder audio, HiCMAE lại **kém hơn các mô hình SSL giọng nói có sẵn đóng băng**:
- CREMA-D 6-lớp **chỉ-audio**: HiCMAE-B WAR **71.01** so với **WavLM-Plus 73.39**, HuBERT 72.57,
  Wav2Vec2 72.41 (Table 6). HiCMAE audio-only thấp hơn WavLM-Plus khoảng 2.4 WAR.
- IEMOCAP chỉ-audio: HiCMAE-B WAR **65.23** so với WavLM-Plus 67.12, Wav2Vec2 67.32 (Table 10).
- RAVDESS chỉ-audio: HiCMAE-B WAR **72.29** so với WavLM-Plus 75.36 (Table 9).
- MER-MULTI (phim truyền hình Trung Quốc) chỉ-audio: HiCMAE-B WF1 **55.33** so với **HuBERT-CH
  61.16** — chính paper cũng quy khoảng cách này cho "domain gap lớn giữa pre-training và
  fine-tuning" (tiếng Anh VoxCeleb2 → tiếng Trung) [§4.2.3, ✔].

**Ablations (§4.5).** Loại bỏ cả ba module phân cấp (→ AV-MAE nguyên bản) làm MAFW WAR giảm từ
54.79 xuống bản đầy đủ 56.17 = **+1.38 tổng cộng**; skip connections đóng góp nhiều nhất, HFF ít
nhất (Table 13). **Loss contrastive mang lại rất ít**: `λ=0` cho MAFW WAR 55.62 so với 56.17 tại
`λ=0.0025` (**≈+0.55 WAR**), và `λ=0.1` khiến kết quả sụp xuống 47.87 — masked reconstruction chiếm
ưu thế, contrastive chỉ là một phần bổ sung nhỏ (Table 14). Hướng fusion **không nhạy cảm** (audio
trước vs video trước vs mặc định chênh nhau trong khoảng ~0.4 WAR, Table 16). Quy mô lớn hơn giúp
cải thiện đơn điệu (T→S→B, Fig. 7); pretraining lâu hơn giúp ích và bão hòa quanh mức 80 epoch
(Fig. 6).

### Parts directly useful for Pebble (each tagged with Decision ID + transfer risk)

1. **Hierarchical feature fusion — trọng số học được theo từng layer trên toàn bộ encoder stack
   (Eq. 12).** `[V-B, V-A]` Thay vì chỉ probe hidden state cuối cùng của backbone audio đóng băng,
   học một tổ hợp có trọng số softmax trên *toàn bộ* các layer WavLM/emotion2vec (một head kiểu
   SUPERB weighted-sum). Ablation của HiCMAE xếp HFF là một đóng góp thực dù khiêm tốn, và điều này
   hội tụ với vn-06 Shen (đỉnh tone nằm ở các layer *giữa*) và bimodal-15 Schuller (SSL mã hóa thiếu
   động lực pitch). **Transfer risk: THẤP.** Đây là một thủ thuật fine-tune-head hoạt động trên bất
   kỳ encoder đóng băng nào; nó không cần checkpoint của HiCMAE hay nhánh video của nó. Artifact cụ
   thể: phần pooling nhánh-audio trong mô hình fusion của chúng ta đọc một vector trọng số theo layer
   học được, chứ không phải `hidden_states[-1]`.

2. **Contrastive/masked SSL như một công thức pretraining KHÔNG phải là chiến thắng cho
   frozen-backbone của chúng ta — giữ nguyên WavLM/emotion2vec.** `[V-B, negative]` Encoder *audio*
   của HiCMAE kém hơn WavLM-Plus đóng băng trên mọi corpus diễn/lab (CREMA-D −2.4, RAVDESS −3.1,
   IEMOCAP −1.9 WAR). Các mức tăng của nó hoàn toàn là hiệu ứng **fusion-với-video**, thứ
   ViEmoSpeech không có (audio+text, không có face video). **Transfer risk: KHÔNG-CHUYỂN-GIAO dứt
   khoát.** Công thức này còn tốn ~480 giờ-GPU V100 trên một corpus audio-visual 1 triệu clip mà
   chúng ta không có bằng tiếng Việt, so với ngân sách Kaggle P100. Hành động cụ thể: **không** dành
   công sức pretrain SSL một audio encoder tiếng Việt từ đầu cho pilot; dùng WavLM /
   emotion2vec-S đóng băng (theo bimodal-01/12), và nếu cần adapt, ưu tiên hướng domain adaptation rẻ
   PhoWhisper-warm (bimodal-15) hơn là kiểu pretrain masked+contrastive như HiCMAE.

3. **Fusion encoder xuyên-modal hai chiều (MHCA cả hai hướng, Eqs. 5–6) với đặc tính
   không-nhạy-hướng.** `[V-A]` Một khối cross-attention 2 layer củng cố mỗi modality từ modality kia
   là một mẫu learned-fusion sạch để đặt lên trên các luồng đóng băng — và kết quả ablation cho thấy
   **hướng fusion hầu như không quan trọng** (Table 16) nhắc chúng ta đừng over-engineer thứ tự
   audio-trước vs text-trước. **Transfer risk: TRUNG BÌNH.** Trong HiCMAE nó được *pretrain đồng
   thời* bên trong encoder, không phải ghép lên trên các đặc trưng đóng băng, và nó fusion
   audio↔video (tương ứng thời gian tự nhiên) chứ không phải audio↔ASR-text (nhiễu, mang tính ngữ
   nghĩa). Fusion của chúng ta phải chịu được nhiễu ASR tone-swap, điều HiCMAE chưa từng đối mặt
   (video ghép cặp sạch). Artifact cụ thể: một nhánh fusion cross-attention hai chiều 2 layer trong
   tập ứng viên V-A (cùng với CASE/FAS Q-Former, WavFusion gate).

4. **Mục tiêu contrastive là *alignment* xuyên-modal, đối lập với việc *tách rời* tone/emotion.**
   `[V-D, clarifying non-transfer]` HCMCL (Eqs. 9–10) kéo audio+video đã ghép cặp lại *gần nhau* để
   thu hẹp khoảng cách modality — nó không tách các yếu tố tín hiệu bên trong một modality. Vì vậy
   contrastive learning của HiCMAE **không** cho chúng ta cách tách kênh tone khỏi kênh emotion trong
   F0/phonation. **Transfer risk: N/A (sai công cụ).** Nếu chúng ta từng muốn một mục tiêu
   contrastive cho V-D, nó phải là *within-audio, factor-separating* (ví dụ: đối chiếu
   tone-invariant vs emotion-invariant), một cấu trúc khác với InfoNCE xuyên-modal của HiCMAE. Ghi
   nhận điều phủ định này để không trích dẫn nhầm HiCMAE như bằng chứng ủng hộ một mục tiêu
   disentangling.

5. **Các mốc chỉ-audio trung thực trên dữ liệu diễn cho baseline ladder.** `[V-G]` Các con số
   chỉ-audio subject-independent của HiCMAE là các mốc so sánh dùng được cho nhánh audio của chúng ta
   trên giọng diễn: **CREMA-D 6-lớp audio WAR ≈ 71–73 (HiCMAE-B 71.01, WavLM-Plus 73.39)** và
   **valence khó hơn arousal nhiều khi chỉ dùng audio** (Werewolf-XL audio valence CCC ≈ 0.08–0.12 so
   với arousal CCC ≈ 0.27). **Transfer risk: TRUNG BÌNH** — diễn, subject-independent 5-fold (không
   phải whole-series holdout), tiếng Anh/register người nổi tiếng, và *chỉ-audio* chứ không phải
   *audio+text*. Artifact cụ thể: thêm các hàng này có gắn cờ vào bảng baseline V-G, và dùng phát
   hiện valence-khó-từ-audio để biện minh cho việc dựa vào **nhánh text cho valence** trong head V/A
   của ViEmoSpeech.

### How each part helps ViEmoSpeech succeed

- **V-B (backbone).** HiCMAE giải quyết một cám dỗ: pretrain SSL một audio encoder riêng không đáng
  công sức cho pilot — một encoder AV tự giám sát huấn luyện trên 1 triệu clip vẫn thua WavLM đóng
  băng trên SER chỉ-audio. Mặc định vẫn là WavLM / emotion2vec-S đóng băng. Thứ chúng ta *có* mượn
  là head HFF rẻ tiền (trọng số học được theo từng layer) để đọc các đặc trưng đóng băng trên toàn
  bộ stack, nơi tone và prosody thực sự tồn tại (các layer giữa theo vn-06/bimodal-15), không chỉ ở
  layer trên cùng.
- **V-A (fusion).** Hai bổ sung cụ thể, chi phí thấp cho cuộc thi fusion: (a) một khối
  cross-attention hai chiều 2 layer; (b) một phép tổng hợp đa layer kiểu HFF trước khi fusion. Và
  một sự tiết kiệm thiết kế: đừng tune *hướng* fusion như một hyperparameter — HiCMAE cho thấy đó là
  yếu tố thứ cấp.
- **V-D (tone×emotion).** Sự rõ ràng mang tính phủ định: alignment contrastive-SSL không phải là cơ
  chế disentangling. Phép đo channel-competition của chúng ta vẫn dựa trên các công cụ vn-06
  Ridge-probe / vn-13 F0-interaction / vn-12 Cramér's-V, không phải một loss contrastive kiểu
  HiCMAE.
- **V-G (eval).** Bổ sung các mốc chỉ-audio trên dữ liệu diễn trung thực (CREMA-D ~71–73 WAR;
  valence≪arousal từ audio) nằm thấp hơn nhiều so với các con số tiếng Việt bị thổi phồng do leak
  (vn-08 86.6, vn-10 0.87), củng cố lập trường speaker-disjoint / whole-series-holdout.

### Child mental-health lens (ViEmoSpeech transfer validity)

ViEmoSpeech không hướng đến trẻ em (profile cũ ở trên đã được lưu trữ); lăng kính liên quan ở đây
là **giọng nói diễn trong phim truyền hình Việt Nam, audio+text, tone×emotion, chỉ phát hành
features**. Tính chuyển giao của HiCMAE sang lăng kính đó bị giới hạn trên ba trục:

- **Không có text, không có tone.** Modality thứ hai của HiCMAE là **video khuôn mặt**, với tín hiệu
  *valence* mạnh (Werewolf-XL valence CCC 0.65) — chính xác là kênh mà ViEmoSpeech không có. Toàn bộ
  tiền đề của nó (tương ứng audio-visual như một tín hiệu contrastive miễn phí) không tồn tại trong
  một corpus audio+text. Vì vậy các kết quả chủ đạo của paper về mặt cấu trúc không thể chuyển giao;
  chỉ các thủ thuật *phía fine-tune* (HFF, cross-attention) sống sót qua sự thay đổi modality.
- **Cảnh báo domain-gap liên quan trực tiếp.** Kết quả MER-MULTI của chính HiCMAE — một mô hình
  pretrain trên VoxCeleb2 tiếng Anh thua HuBERT-CH (pretrain tiếng Trung) trên audio phim truyền hình
  Trung Quốc (WF1 55.33 so với 61.16) — là một minh chứng sạch, có trích dẫn, rằng **việc chuyển
  giao SSL xuyên ngôn ngữ suy giảm trên media diễn thuộc ngôn ngữ có thanh điệu**. Đó chính xác là
  bối cảnh của ViEmoSpeech (phim truyền hình Việt Nam). Đây là bằng chứng củng cố cho một nhánh
  text/audio thích nghi tiếng Việt (V-C PhoBERT/ViSoBERT; V-B PhoWhisper-warm) thay vì một encoder
  pretrain tiếng Anh chung chung — và cảnh báo không nên kỳ vọng một checkpoint SSL nước ngoài hoạt
  động tốt ngay trên tiếng Việt.
- **Ethics/release.** Không có construct mental-health hay distress nào ở bất kỳ đâu (chỉ có cảm xúc
  cơ bản categorical + các chiều V/A/D trên video người nổi tiếng/diễn viên); không có gì để mượn cho
  V-F. Mô hình VoxCeleb2 được phát hành là dữ liệu khuôn mặt audio-visual — không liên quan và nặng
  hơn mô hình phát hành CC-BY chỉ-features của ViEmoSpeech (V-H), vốn lấy cảm hứng từ bimodal-16 /
  MSP-Podcast.

### Limitations & open questions for ViEmoSpeech (incl. contradiction/gap)

- **Mâu thuẫn với bimodal-15 (nhân bản Schuller):** HiCMAE báo cáo **"lớn hơn thì tốt hơn" một cách
  đơn điệu** (T→S→B, Fig. 7) và "pretraining lâu hơn giúp ích" (Fig. 6), trong khi bimodal-15 phát
  hiện UAR mô hình so với params/MACs/năm có ρ≈**0** trên toàn lĩnh vực SER và không có leaderboard
  đáng tin cậy. Cách dung hòa: tính đơn điệu của HiCMAE là *trong một họ kiến trúc duy nhất trên
  chính công thức và dataset của nó* (và trên 5-fold CV độc lập theo subject/session nhưng N nhỏ),
  không phải một quy luật xuyên-mô-hình — nên nó không phải bằng chứng chống lại Schuller. Hệ quả
  thực tiễn cho chúng ta: vẫn phải **A/B trên chính các clip của mình với bootstrap CI** (V-G); không
  giả định một backbone đóng băng lớn hơn sẽ thắng.
- **Mâu thuẫn với kế hoạch frozen-backbone của ViEmoSpeech:** HiCMAE là một công thức **full
  fine-tune** (bỏ decoder, fine-tune cả hai encoder); nó chưa bao giờ đánh giá encoder của mình như
  một *bộ trích xuất đặc trưng đóng băng*, và nhánh audio của nó đã thua WavLM đóng băng rồi. Vì vậy
  nó **không cung cấp bằng chứng** rằng một audio encoder pretrain-SSL-rồi-đóng-băng có tính cạnh
  tranh — ngược lại với điều một chương trình frozen-feature mong đợi, và là một lời cảnh báo không
  nên đọc các mức tăng của nó như chất lượng backbone thay vì hiệu ứng fusion-với-video.
- **Khoảng trống — contrastive ≠ disentangling (so với V-D):** mục tiêu contrastive của paper căn
  chỉnh các modality; nhu cầu mở của V-D trong ViEmoSpeech là *tách* các yếu tố tone và emotion đang
  chia sẻ F0/phonation. HiCMAE không đụng đến điều này, và không paper nào khác trong tập cũng vậy —
  tính mới của V-D vẫn còn nguyên vẹn.
- **Cờ myth-đã-bị-bác-bỏ:** phần giới thiệu dựa vào các con số Mehrabian 7%/38%/55% "lời nói/tông
  giọng/khuôn mặt" [refs 3,4] để biện minh cho ưu thế audio+visual — một sự khái quát hóa quá mức
  từng bị chỉ trích rộng rãi. Điểm neo tone×emotion của chúng ta phải bám vào phonetics (vn-06 Shen,
  vn-13 Chang), **không** trích dẫn qua myth này; nếu có trích HiCMAE, hãy trích cho công thức SSL và
  kết quả của nó, không phải cách đóng khung đó.
- **Câu hỏi mở:** vector trọng số-học-được-theo-layer của HFF là ý tưởng rẻ, rõ ràng có thể chuyển
  giao nhất — đáng làm một ablation nhỏ trong pilot của chúng ta (weighted-sum-of-layers so với
  last-layer) trên head audio WavLM đóng băng, để xác nhận lợi ích mid-layer cho tone/prosody mà
  vn-06 và bimodal-15 dự đoán.
