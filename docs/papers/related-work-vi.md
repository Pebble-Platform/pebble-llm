# Tổng hợp 5 bài báo liên quan nhất — Pebble Emotion Classifier (Phiên bản Tiếng Việt)

> Phiên bản đầy đủ tiếng Anh: xem các file `01-faiir.md` → `05-sharma-empathy.md` trong cùng thư mục `docs/papers/`. File này là bản tổng hợp tiếng Việt, mỗi bài ~600–900 chữ, đủ để viết phần Related Work cho một bài báo NLP về Pebble.
>
> **Ngày biên soạn:** 2026-06-08

---

## Bối cảnh dự án Pebble (tóm tắt)

Pebble fine-tune mô hình **NeoBERT** (encoder Transformer 250M tham số) thành bộ phân loại cảm xúc đa nhiệm cho hệ thống chatbot hỗ trợ sức khỏe tinh thần. Kiến trúc gồm **3 đầu ra dị thể** trên cùng một biểu diễn `[CLS]`:

1. **Đầu hồi quy liên tục** (sigmoid): `energy / severity / socialIsolation / receptivity` — giá trị trong [0,1]
2. **Đầu phân loại đa lớp** (softmax) trên taxonomy 12 cảm xúc: joy, gratitude, hope, sadness, frustration, anxiety, confusion, loneliness, exhaustion, guilt, calm, neutral
3. **Đầu phân loại nhị phân an toàn/khủng hoảng** (BCE với trọng số dương ~10×, yêu cầu recall ≥ 0.95)

Dữ liệu huấn luyện: ~5K nhãn bạc do Gemini sinh + 500 nhãn người (Protocol A) + 500 nhãn người (Protocol B). Học chuyển giao từ GoEmotions, EmpatheticDialogues, DailyDialog, SemEval-2025, WASSA, TalkLife. Mất mát kết hợp MSE + CE + BCE, dự kiến nâng cấp lên **Kendall uncertainty weighting** hoặc **GradNorm** nếu các đầu xung đột.

Các tiêu chí để chọn 5 bài "gần nhất":

1. Encoder đa nhiệm cho cảm xúc với đầu ra **phân loại + hồi quy liên tục** (lý tưởng có thêm đầu an toàn)
2. Phân loại văn bản **sức khỏe tinh thần** dùng transformer encoder
3. Học chuyển giao từ **GoEmotions / EmpatheticDialogues**
4. **Chưng cất nhãn bạc từ LLM giáo viên** sang student nhỏ hơn
5. **Cân bằng mất mát đa nhiệm** trong NLP cảm xúc

---

## Bài 1 — FAIIR: Trợ lý AI cho dịch vụ sức khỏe tinh thần thanh thiếu niên

**Trích dẫn:** Obadinma et al., npj Digital Medicine 2025; arXiv:2405.18553 — [link](https://arxiv.org/abs/2405.18553)

### Vấn đề nghiên cứu
Kids Help Phone (KHP) là một tổ chức phi lợi nhuận Canada, kể từ 2018 đã xử lý hơn 1 triệu cuộc hội thoại SMS hỗ trợ khủng hoảng cho thanh thiếu niên. Mỗi cuộc hội thoại do **Crisis Responder (CR)** — chuyên viên được đào tạo — xử lý và phải gán nhãn 19 vấn đề (suicide, abuse, anxiety…) sau khi kết thúc. Khối lượng công việc lớn + áp lực tâm lý cao. FAIIR là công cụ AI gợi ý nhãn để **giảm tải hậu hội thoại**, không phải để tư vấn lâm sàng.

### Dữ liệu
- **703,975 cuộc hội thoại SMS** (2018–2/2023) + **84,832 cuộc** giữ riêng để "silent testing" tiền triển khai (2/2023–9/2023).
- **19 nhãn vấn đề** (multi-label): 3rd Party, Abuse (Emotional/Physical/Sexual), Anxiety/Stress, Bully, Depressed, DNE, Eating Body Image, Gender/Sexual Identity, Grief, Isolated, Other, Prank, Relationship, Self Harm, Substance Abuse, Suicide, Testing.
- **Nhãn chỉ do 1 CR gán**, không có người đánh giá lại — đây là nguồn nhiễu cốt lõi.
- Trung bình 913 token/cuộc, max 2,048 token (phủ 94.4%).
- Có chỉ số **priority** (low/medium/high) do thuật toán của Crisis Text Line gán; được **chèn vào input dưới dạng câu prefix** `"This conversation is of <<X>> priority"`.

### Phương pháp
- **Bước 1:** so sánh 4 encoder (Longformer 149M, BERT 110M, DialogLED 139M, MVP 406M). Longformer thắng nhờ khả năng xử lý chuỗi dài.
- **MLM tiếp tục huấn luyện** trên toàn bộ corpus KHP: mask 15%, 1 epoch, ~24h.
- **Bước 2:** ensemble 3 Longformer. Hai mô hình dùng oversampling cho nhãn hiếm; mô hình thứ ba dùng phân phối tự nhiên. Đầu mỗi tag là 1 sigmoid; mất mát BCE. AdamW, LR 2e-5, batch 16, 3 epochs.
- **Tuning ngưỡng theo tần suất**: 0.4 (3 tag phổ biến nhất) / 0.3 (Suicide, Isolated) / 0.2 (14 tag còn lại).

### Kết quả
- Retrospective test (n=140,795): **AUROC trung bình 0.94**, sample-avg P=0.58 / R=0.81 / F1=0.64.
- Prospective silent test (n=84,832): suy giảm **<2%** trên mọi chỉ số.
- Per-tag: F1 mạnh ở Suicide=0.73 (AUROC 0.94), Self Harm=0.69, Depressed=0.75, 3rd Party=0.76; yếu ở Other=0.35, Prank=0.45.
- Công bằng nhân khẩu học: độ lệch chuẩn F1 giữa 27 subgroup < 0.025.
- **Nghiên cứu chuyên gia:** 12 CR x 40 hội thoại khó × 6 review/hội thoại (3 open + 3 blind, 5 tiêu chí đồng thuận). Kết quả: **chuyên gia đồng thuận với FAIIR 90.9%** — cao hơn cả mức đồng thuận giữa chuyên gia và nhãn gốc.

### Liên hệ với Pebble
- Cùng dạng bài toán: phân loại văn bản sức khỏe tinh thần với đầu ra critical cho an toàn.
- FAIIR dùng **threshold tuning** làm cơ chế ưu tiên recall — Pebble đi xa hơn với **trọng số positive 10×** và **ràng buộc cứng recall ≥ 0.95**.
- Kỹ thuật FAIIR Pebble có thể áp dụng: **priority-as-prefix conditioning**, **MLM tiếp tục huấn luyện trên corpus đặc thù**, **ngưỡng quyết định theo tần suất từng class**, **ensemble nhỏ với 1 thành viên oversampling**.

---

## Bài 2 — Ghosh, Ekbal & Bhattacharyya: Transformer đa nhiệm hỗ trợ VAD cho ghi chú tự tử

**Trích dẫn:** Information Processing & Management 60(2):103234, 2022 — [DOI](https://doi.org/10.1016/j.ipm.2022.103234)

> **Cảnh báo:** Bài báo đầy đủ bị tường thu phí ở ScienceDirect. Phần lớn chi tiết phương pháp được suy ra từ bài "anh em" cùng nhóm (IJCAI-ECAI 2022 và Scientific Reports 2022) trên cùng corpus CEASE-v2.0. Các chỗ không xác minh được đánh dấu rõ.

### Vấn đề nghiên cứu
Ghi chú tự tử (suicide notes) là cửa sổ duy nhất vào trạng thái tâm lý ngay trước hành vi tự tử. Phân loại cảm xúc thông thường (positive/negative) quá thô; nhà nghiên cứu cần **phân loại fine-grained kèm cường độ** vì cường độ phân biệt giữa ý nghĩ thoáng qua và khủng hoảng cấp tính.

### Dữ liệu — CEASE-v2.0
- **4,932 câu** từ **325 ghi chú tự tử** thật (mở rộng từ CEASE v1 LREC 2020 có 2,393 câu / 205 ghi chú).
- **15 nhãn fine-grained:** forgiveness, happiness/peacefulness, love, pride, hopefulness, thankfulness, blame, anger, fear, abuse, sorrow, hopelessness, guilt, information, instructions.
- 76% câu 1 nhãn, 22% 2 nhãn, 2% 3 nhãn.
- Krippendorff α ≈ 0.61 (3 annotator).
- **Đóng góp mới:** toàn bộ 4,932 câu được bổ sung **nhãn cường độ** (định dạng cụ thể không xác minh được).

### Phương pháp (tái dựng phỏng đoán)
- Transformer encoder (gần như chắc chắn BERT-base) → đầu ra `[CLS]`.
- Tra từ điển **NRC-VAD** (Valence/Arousal/Dominance, ~20k từ tiếng Anh) cho từng token; tổng hợp thành vector V/A/D cho câu.
- Kết hợp biểu diễn BERT với vector VAD (concat hoặc gated fusion — chưa rõ).
- 2 đầu nhiệm vụ: (a) phân loại đa nhãn 15 cảm xúc (BCE), (b) hồi quy cường độ (MSE).
- Có thể có thêm L_Diff differential loss như paper IJCAI cùng nhóm.

### Mất mát (suy đoán)
`L = α·CE_emotion + β·MSE_intensity (+γ·L_Diff)`. Các trọng số α, β tinh chỉnh thực nghiệm. Paper SPANMLC cùng nhóm dùng tỉ lệ 0.3/0.3/1.0.

### Kết quả
- **Mean Recall = 65.25%** trên CEASE-v2.0 — claimed +8.78% so với SOTA trước (CMSEKI).
- Multi-task vượt single-task tương ứng.
- F1 từng class, MAE cường độ: không xác minh được công khai.

### Liên hệ với Pebble
- **Tiền lệ trực tiếp nhất** cho việc kết hợp đầu phân loại + đầu hồi quy liên tục trong transformer cho corpus mental-health nhỏ.
- Tín hiệu phụ trợ: Ghosh dùng từ điển NRC-VAD; Pebble dùng warm-start GoEmotions — cùng tinh thần "bổ sung scaffold cảm xúc".
- **Khác biệt quan trọng:** Ghosh không có đầu an toàn/khủng hoảng. Ghosh cân bằng mất mát tĩnh; Pebble dự kiến dùng Kendall/GradNorm — đây là điểm tiến bộ phương pháp Pebble có thể claim.
- **Domain match yếu:** suicide notes là monologue cuối đời, không phải hội thoại nhiều turn.

---

## Bài 3 — Pathak, Bhattacharjee, Saha & Saha: Core Fusion Network ba nhiệm vụ trên hội thoại tạo động lực

**Trích dẫn:** ACM Transactions on Computing for Healthcare 2025; [DOI 10.1145/3704740](https://dl.acm.org/doi/10.1145/3704740)

> **Cảnh báo:** Toàn bộ PDF bị tường thu phí ACM. Phương pháp chi tiết hầu hết phải suy đoán từ paper tổ tiên (Liu et al. ACL 2017 về shared-private adversarial MTL) và các công trình trước của cùng nhóm Saha.

### Vấn đề nghiên cứu
Xác định rối loạn sức khỏe tinh thần (MHD) từ hội thoại tự nhiên là bài toán khó vì cùng câu chữ có thể thuộc nhiều rối loạn khác nhau tùy ngữ cảnh cảm xúc. Giả thuyết: cung cấp **giám sát phụ trợ về cảm xúc + sentiment** sẽ giúp đầu MHD chính học tốt hơn.

### Dữ liệu — MotiVAte mở rộng
- Gốc MotiVAte (Saha et al. IJCNN 2021): **7,067 hội thoại đôi** giữa "support seeker" và Virtual Assistant, **1,839 user duy nhất**.
- **4 nhãn rối loạn:** Major Depressive Disorder (MDD), Anxiety, OCD, PTSD.
- Phi lâm sàng (lấy từ forum hỗ trợ).
- **Đóng góp mới:** thêm nhãn cảm xúc + sentiment **bán giám sát** cho từng turn (công cụ silver-labeling không công khai).

### Phương pháp — Core Fusion Network (CFN)
- Họ kiến trúc **shared-private MTL** (Liu et al. 2017): một encoder dùng chung + encoder riêng cho từng nhiệm vụ.
- "Core Fusion" là toán tử kết hợp đặc trưng shared và private trước mỗi đầu (cơ chế cụ thể: concat, gated, attention — chưa rõ).
- 3 đầu softmax: MHD (4 lớp, chính), Emotion (~6–7 lớp, phụ), Sentiment (3 lớp, phụ).
- Có thể có thêm orthogonality penalty hoặc adversarial discriminator — không xác minh.

### Kết quả
- **89.12% accuracy MHD** với tri-task CFN — vượt qua "single-task và bi-task".
- Khẳng định trung tâm: **tri-task > bi-task > uni-task** cho MHD.
- Số liệu chi tiết: không xác minh được.

### Liên hệ với Pebble
- **Củng cố giả thuyết MTL:** kết quả của Pathak xác nhận thêm cảm xúc + sentiment làm phụ trợ giúp đầu chính (Pebble: emotion + severity hỗ trợ safety).
- Cả 2 dùng nhãn bán tự động, nhưng **teacher của Pebble (Gemini) tinh vi hơn** — sinh được cả nhãn rời rạc và điểm số liên tục, cho phép Pebble huấn luyện đầu hồi quy.
- Pebble có **đầu an toàn** mà CFN không có.
- **Tùy chọn kiến trúc dự phòng:** nếu trong huấn luyện Pebble các đầu xung đột (negative transfer), kiến trúc shared-private adversarial của CFN là phương án Plan B đã được chứng minh.

---

## Bài 4 — Emo Pillars: Chưng cất tri thức cho phân loại cảm xúc fine-grained

**Trích dẫn:** Shvets, Findings of ACL 2025; arXiv:2504.16856 — [link](https://arxiv.org/abs/2504.16856)

### Vấn đề nghiên cứu
Phân loại cảm xúc fine-grained (28 class GoEmotions) bị giới hạn dữ liệu nghiêm trọng. Tạo annotation tay quy mô lớn cho taxonomy lớn rất tốn kém và IAA tụt mạnh khi label gần nhau (annoyance vs anger, nervousness vs fear). Đồng thời, hầu hết dataset cảm xúc chỉ có utterance đơn độc, không có ngữ cảnh — gây ra hallucination khi triển khai. Giải pháp: **sinh dataset tổng hợp lớn có ngữ cảnh** bằng LLM teacher thay vì annotate tay.

### Framework chưng cất
- **Không phải KL distillation** trên logit. Cũng không phải hard-label CE.
- Là **implicit hard-label distillation với multi-label sigmoid targets do teacher sinh**: teacher Mistral-7B-Instruct-v0.2 được prompt để liệt kê top-5 cảm xúc với mức "expressiveness" 0–1 (step 0.1); ngưỡng tại **0.3** → label dương/âm; student train với **BCE**.

### Pipeline sinh dữ liệu
- **Seed:** WikiPlots (113K tóm tắt phim/sách), dùng **2,000 plot** cho run chính.
- **6 giai đoạn LLM** (mỗi giai đoạn có prompt riêng):
  1. Actor extraction (~15 nhân vật/plot)
  2. Utterance generation (8 non-neutral + 2 neutral utterance/nhân vật)
  3. Soft labeling (top-5 cảm xúc với expressiveness)
  4. Context generation (tóm tắt tình huống dẫn đến utterance)
  5. Context cleaning (xóa câu nhắc trực tiếp cảm xúc)
  6. Utterance rewriting (viết lại utterance sao cho cảm xúc mơ hồ nếu không có context)
- **Sản phẩm:** ~300K mẫu context-less + ~100K context-full.
- **Compute:** ~700K inference Mistral, **~450 H100 giờ**.

### Student
- **RoBERTa-large** (~355M tham số), đầu sigmoid 28 class, BCE loss.
- AdamW, LR 2e-5, batch 64 (context-less) / 32 (context-aware), seq 128/512, 10 epochs.
- Token-type IDs phân biệt context (0) vs utterance (1).

### Kết quả
| Benchmark | Macro-F1 |
|---|---|
| GoEmotions (fine-tuned) | **0.55 ± 0.007** (SOTA) |
| ISEAR (5-fold CV) | **0.75 ± 0.013** |
| IEMOCAP 4-way | **0.83** |
| IEMOCAP 6-way | 0.63 |
| EmoContext (dev4) | **0.82** |

- Context-aware vượt context-less **+2–3 p.p.** trên test rewritten+context.
- Scaling: 2000 plot → 0.79 F1, giảm 10× còn 200 plot vẫn được 0.77.
- Human eval: 3 postdoc × 200 mẫu; Cohen κ = 0.365 (vs 0.293 của GoEmotions); accuracy 0.86 khi cả 3 đồng thuận.

### Liên hệ với Pebble
- **Tiền lệ mạnh nhất** cho việc Pebble chưng cất LLM teacher (Gemini) vào encoder nhỏ.
- Cùng triết lý: teacher là **label oracle**, không phải logit oracle → BCE trên hard label sau ngưỡng, không KL.
- **3 trick Pebble nên áp dụng trực tiếp:**
  1. **Ngưỡng expressiveness 0.3** để chuyển soft score thành hard multi-label.
  2. **Sweep ngưỡng quyết định 0.05 → 0.95 step 0.01** để tối đa macro-F1 (tránh bẫy threshold 0.5 mặc định).
  3. **Thiết kế human eval:** 3 annotator × 200 mẫu, multiple choice, báo Cohen κ và accuracy theo mức đồng thuận.
- **Pebble khác biệt:** đầu dị thể (regression + softmax + BCE), ràng buộc recall an toàn, domain hội thoại sức khỏe tinh thần thật (không phải plot phim/sách), teacher lớn hơn (Gemini Flash > Mistral-7B).

---

## Bài 5 — Sharma et al.: Phân tích empathy trong hỗ trợ sức khỏe tinh thần qua text

**Trích dẫn:** EMNLP 2020, pp. 5263–5276; arXiv:2009.08441 — [link](https://aclanthology.org/2020.emnlp-main.425/)

### Vấn đề nghiên cứu
Các nền tảng peer support qua text (TalkLife, 7 Cups, Reddit) là tài nguyên sức khỏe tinh thần lớn nhất trên thực tế, nhưng người hỗ trợ là tình nguyện viên chưa qua đào tạo — có khoảng cách lớn về chất lượng empathy so với therapist chuyên nghiệp. Các thước đo empathy hiện có thiết kế cho giao tiếp mặt-đối-mặt, không hợp với text ngắn bất đồng bộ. Mục tiêu: **xây rubric empathy text-native** + bộ classifier để cung cấp feedback tự động.

### Framework EPITOME
3 cơ chế empathy độc lập, mỗi cơ chế ordinal 3 mức {0=no, 1=weak, 2=strong}:
- **Emotional Reactions (ER)** — kênh affective ("I feel really sad for you")
- **Interpretations (IP)** — kênh cognitive ("This must be terrifying")
- **Explorations (EX)** — kênh active-listening ("Are you feeling alone right now?")

### Dữ liệu
- **10,143 cặp (seeker post, response post)** đã annotate cả **empathy level** lẫn **rationale span** (substring giải thích).
- TalkLife (7,062 cặp, in-domain) + Reddit 55 subreddit sức khỏe tinh thần (3,081 cặp, out-of-domain).
- 8 crowdworker được đào tạo intensive (30–60 phút phone call + 50–100 practice post).
- **Cohen κ = 0.6865** (trung bình pairwise).

### Phương pháp
- **Domain-adaptive MLM** trên 2 corpus độc lập (TalkLife):
  - S-Encoder (seeker side): 6.4M post ≈ 182M token, ~22h.
  - R-Encoder (response side): 18M post ≈ 279M token, ~38h.
  - Cả hai start từ RoBERTa-base (125M).
- **Bi-encoder kiến trúc:**
  - `e^S = S-Encoder(S)`, `e^R = R-Encoder(R)`
  - **Cross-attention 1 head:** Q = response, K = V = seeker → `a = softmax(e^R · e^S^T / √d) · e^S`
  - **Residual:** `h^R = e^R + a`
  - Tổng tham số ≈ 251M.
- **2 đầu nhiệm vụ:**
  - EI (Empathy Identification): linear + softmax 3 class trên `h^R[CLS]`. **Mỗi cơ chế (ER/IP/EX) train 1 model riêng** (3 model tổng cộng).
  - RE (Rationale Extraction): linear chia sẻ → per-token binary BCE. **Không phải BIO tagging.**
- **Mất mát:** `L = λ_EI · L_EI + λ_RE · L_RE` với λ_EI=1, λ_RE=0.5 (grid {0.1, 0.2, 0.5, 1}).
- Training: AdamW, LR 2e-5, batch 32, 4 epochs, split 75/5/20, ~5 phút/fine-tune.

### Kết quả
- EI trên TalkLife: ER 79.93% / 74.29% macro-F1; IP 87.50% / 67.46%; EX 86.92% / 73.47%.
- Bi-encoder vượt RoBERTa single-task **+4 macro-F1** trung bình.
- RE: token-F1 0.64–0.68; IOU-F1 (ngưỡng IoU ≥ 0.5) 0.67/0.86/0.83.
- Cross-domain: degrade ít hơn baseline khi sang Reddit.
- Ablation: **− attention** mất nhiều nhất; **− MLM** mất thứ hai; **− rationale** mất 1–2 macro-F1.

### Phân tích ứng dụng (~235K interaction TalkLife)
- Chỉ **~10%** response của TalkLife đạt strong empathy.
- EPITOME trung bình **1.09/6** — đa số volunteer response thấp.
- Repeat supporter **không** cải thiện tự nhiên: ER score giảm 36% trong 3 năm.
- Strong-empathy response nhận **+45%** like và **+79%** follow-up.
- POC feedback với **3 người tham gia**: mean EPITOME tăng từ 0.8 → 3.0.

### Liên hệ với Pebble
- Cùng không gian bài toán: phân loại text peer-support sức khỏe tinh thần.
- Cả 2 dùng TalkLife (Pebble có DUA caveat).
- **Bi-encoder của EPITOME quá phức tạp cho Pebble**: Pebble có 1 message + ≤3 context message, không có cấu trúc seeker/response — shared encoder với prefix context phù hợp hơn.
- MTL static λ của EPITOME là chính baseline mà Pebble dự kiến challenge với Kendall/GradNorm.
- **MLM tiếp tục huấn luyện** trên corpus peer-support là kỹ thuật Pebble có thể bổ sung lên trên NeoBERT (RefinedWeb pretrain).
- **Quy mô annotation:** 10,143 cặp với 8 crowdworker đạt κ ≈ 0.69 là mục tiêu khả thi Pebble có thể nhắm tới.

---

## Tổng hợp so sánh — Pebble trong bối cảnh 5 bài

| Bài | Encoder | Cấu trúc đầu | Cân bằng MTL | Loss | Ràng buộc safety | Chưng cất? |
|---|---|---|---|---|---|---|
| FAIIR | Longformer 149M ×3 ensemble | Linear + sigmoid 19 đầu | Không (single-task multi-label) | BCE; oversampling nhãn hiếm | Threshold 0.3 cho Suicide | Không (nhãn người vận hành) |
| Ghosh et al. | BERT/RoBERTa | Softmax (emotion) + regression (intensity) trên `[CLS]` + VAD | Static α·CE + β·MSE | CE + MSE | Không | Không |
| Pathak et al. (CFN) | Transformer (NRIAS) | Shared + private → 3 CE đầu | Static weighted sum + có thể orthogonality/adversarial | 3× CE | Không | Không (nhãn bán tự động) |
| Emo Pillars | RoBERTa-large 355M | Linear + sigmoid 28 đầu | Không (single-task) | BCE trên hard-thresholded soft labels (≥0.3 → 1) | Không | **Có — Mistral-7B teacher sinh 400K nhãn synthetic** |
| Sharma et al. | RoBERTa-base bi-encoder (~251M) | EI softmax 3-way + RE per-token BCE; **1 model/cơ chế** | Static λ_EI=1, λ_RE=0.5 (grid) | CE + CE | Không | Không |

### Khoảng trống Pebble đang nhắm tới

1. **Ba đầu dị thể trên cùng encoder.** Không bài nào làm regression + softmax + BCE đồng thời. Ghosh gần nhất (CE + MSE) nhưng không có safety BCE; Pathak gần nhất (3 CE) nhưng không có regression. **Tổ hợp MSE + CE + BCE của Pebble thực sự mới.**

2. **Cân bằng mất mát có nguyên tắc.** Cả 5 bài đều dùng weighting tĩnh hoặc grid-searched λ. **Không bài nào áp dụng Kendall uncertainty / GradNorm cho phân loại affect** — đây là delta nghiên cứu sạch cho Pebble.

3. **Ràng buộc recall an toàn.** FAIIR là bài duy nhất có safety class nhưng chỉ dùng threshold tuning. **Không bài nào áp đặt floor recall ≥ 0.95 như mục tiêu huấn luyện** (qua constrained optimization, focal loss với γ cao, hoặc precision-at-recall surrogate) — khoảng trống phương pháp luận mở cho Pebble.

4. **Chưng cất LLM teacher cho affect.** Emo Pillars là template phương pháp, nhưng chỉ làm single-task multi-label. **Pebble mở rộng sang regression + classification + safety với teacher Gemini** là đóng góp rõ ràng cho ACL Findings / WASSA / CLPsych.

5. **Staged freeze/unfreeze.** Sharma có domain-adaptive MLM nhưng không có staged freezing; FAIIR có KHP MLM nhưng train toàn bộ tham số joint sau đó. **Warm-start đầu emotion trên GoEmotions rồi unfreeze tăng dần của Pebble** chưa được khảo sát ở cấu hình chính xác này — slot ablation hữu ích nhưng đóng góp standalone yếu hơn.

### Góc đề xuất cho bài báo Pebble

Tổ hợp mạnh nhất là **(1) cân bằng MTL dị thể dưới ràng buộc recall safety cứng** và **(2) chưng cất LLM teacher vào encoder affect đa nhiệm**. Gói chung vào 1 bài:

> **"Distilling a frontier LLM into a NeoBERT student for mental-health affect classification under a hard crisis-recall constraint, with uncertainty-weighted multi-task balancing across regression + classification + safety heads."**

Bao phủ vùng chưa có ai chiếm, phù hợp pipeline huấn luyện Pebble đang có. Mục **(3)** trở thành ablation warm-start trong cùng bài, mục **(4)** trở thành section calibration analysis.

---

## Nguồn tham khảo

- [FAIIR (npj Digital Medicine, 2025)](https://www.nature.com/articles/s41746-025-01647-6) · [arXiv:2405.18553](https://arxiv.org/abs/2405.18553)
- [Ghosh et al. (IPM, 2022)](https://doi.org/10.1016/j.ipm.2022.103234) — paywall
- [Pathak et al. (ACM THC, 2025)](https://dl.acm.org/doi/10.1145/3704740) — paywall
- [Shvets — Emo Pillars (ACL Findings 2025)](https://aclanthology.org/2025.findings-acl.10/) · [arXiv:2504.16856](https://arxiv.org/abs/2504.16856)
- [Sharma et al. (EMNLP 2020)](https://aclanthology.org/2020.emnlp-main.425/) · [arXiv:2009.08441](https://arxiv.org/abs/2009.08441)
- [Liu, Qiu, Huang — Adversarial Multi-task Learning (ACL 2017)](https://aclanthology.org/P17-1001/) (gốc shared-private)
- [MentalBERT (Ji et al., 2021)](https://arxiv.org/pdf/2110.15621)
- [NRC-VAD lexicon (Mohammad, ACL 2018)](https://aclanthology.org/P18-1017/)
