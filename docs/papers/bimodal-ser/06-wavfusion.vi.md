# Paper 06 — WavFusion: Towards wav2vec 2.0 Multimodal Speech Emotion Recognition

> Bản dịch tiếng Việt của [06-wavfusion.md](06-wavfusion.md) — cập nhật 2026-07-10.

- **Authors:** Feng Li, Jiusong Luo, Wanjun Xia
- **Venue / year:** MMM 2025 (Springer LNCS)
- **Links:** abs https://arxiv.org/abs/2412.05558 · PDF `pdfs/06-wavfusion.pdf`
- **Group:** audio+text (trục chính)

**Summary:** Gated cross-modal attention + học biểu diễn dựa trên homogeneous-feature-discrepancy, nhánh audio wav2vec2 + nhánh text, đánh giá trên IEMOCAP/MELD.

**Relevance to Pebble:** Reference ablation gọn cho lựa chọn cơ chế fusion.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled Pebble profile (at analysis time):** Ý định chính = phân loại **text** nguy cơ tự tử dạng *ordinal*, dùng nhãn silver từ LLM dưới gold-holdout nghiêm ngặt (có ý thức về thứ tự, chia theo subject-level, có thể tái lập; `docs/intent/constraints.md`). Luồng **voice** liền kề (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`) = các head multi-task không đồng nhất trên một **backbone speech SSL đóng băng** (WavLM-Large / emotion2vec): emotion (CE) + affect (valence/arousal, **hồi quy CCC**) + crisis (BCE dưới **sàn recall cứng**), được cân bằng bằng **Kendall uncertainty weighting**; **fusion voice+text** là hướng đi tiếp theo.

### Analysis — WavFusion (audio+text+visual SER)
- **Overlap:** 19% (peripheral) — D1=0, D2=0, D3=1, D4=0, D5=1, D6=0, D7=2.
  - Công thức: (3·0 + 2·0 + 1·1 + 2·0 + 2·1 + 2·0 + 1·2) / 26 × 100 = 5/26 × 100 ≈ 19%.
  - D1=0 chỉ một head emotion phân loại (categorical) đơn lẻ + một margin loss ở cấp biểu diễn (representation-level) — không có head liên tục/safety nào. D2=0 SER TV/acted tổng quát, không phải mental-health/crisis (mental health chỉ được nhắc tên trong phần intro). D3=1 IEMOCAP/MELD là các corpus emotion nhưng không phải ví dụ mẫu về intensity/transfer. D4=0 không có nhãn từ teacher-LLM (giám sát đầy đủ bằng gold). D5=1 cân bằng CE + margin loss nhưng qua một lưới scalar λ chỉnh tay (Table 5), không phải các phương pháp có nguyên tắc (uncertainty/GradNorm/PCGrad). D6=0 không có ràng buộc recall. D7=2 backbone audio SSL wav2vec2.0 (cùng họ với WavLM/emotion2vec của luồng voice) **và** text RoBERTa-base (họ BERT, khớp với luồng text).
- **Closest on:** D7 (các backbone SSL-speech + RoBERTa khớp với cả hai luồng của Pebble); thứ hai là D5 (một nghiên cứu độ nhạy cụ thể về cân bằng hai loss).
- **Best point (Method to adopt):** Gated cross-modal attention fusion — một cổng (gate) sigmoid theo từng kênh có thể học `P = σ(FC(X_A→T ⊕ X_A→V))`, `X_F = P⊙X_A→T + (1−P)⊙X_A→V` (Eqs 10–11), giúp lọc động tín hiệu cross-modal dư thừa/gây nhiễu, được ablate rõ ràng so với concatenation đơn thuần (concat 66.78 → gated attention 70.6 WF1 trên IEMOCAP, Table 6).
  - **How to apply to Pebble:** khi các head voice MTL có thêm một nhánh text, hãy fuse luồng audio và text bằng cổng học được này thay vì concatenation — đây là một khối fusion drop-in, rẻ, có thể trích dẫn, và ablation concat-vs-gated của nó là phép so sánh tham chiếu cho lựa chọn thiết kế đó.
- **Caveats:** Đã đọc toàn văn (arXiv PDF, cả 11 trang) — không paywall. Chỉ có một task emotion **phân loại (categorical)** đơn lẻ; không có head liên tục/CCC, không có mục tiêu crisis/recall-floor, không có cấu trúc ordinal, không có nhãn weak từ LLM, không có gold-holdout — nên nó chạm vào *hướng phát triển kiến trúc* của Pebble, không phải luận điểm đánh giá cốt lõi. Mức tăng từ fusion khá khiêm tốn (+0.74 WF1 trên IEMOCAP, +0.44 trên MELD); MELD dùng split cố định trong khi IEMOCAP là 5-fold (không báo cáo std). Loss margin ("homogeneous feature discrepancy") cần các mẫu cùng-cảm-xúc-khác-modality theo cặp, điều mà thiết lập voice-only gán nhãn proxy trên RAVDESS của Pebble không thể cung cấp.

## Deep research — full-PDF read (2026-07-10)

> Đọc đối chiếu với profile **ViEmoSpeech** (audio + text PhoWhisper-ASR, backbone đóng băng, 7 lớp +
> V/A(1–5) + distress, tone×emotion tiếng Việt). Khối "Analysis (overlap with Pebble)" chỉ-text đã cũ
> ở trên được lưu trữ (archived) — các quyết định được trích dẫn ở đây là **V-A…V-H** từ `docs/tasks/paper-deep-analysis.md`.
> Mục này chỉ APPEND thêm vào bên dưới phần lịch sử; không chỉnh sửa phần đó.

### Source-access note

- **Đã đọc toàn văn PDF** qua `pdftotext "docs/papers/bimodal-ser/pdfs/06-wavfusion.pdf" -` (arXiv:2412.05558v1,
  11 trang bao gồm cả 6 bảng + Eqs 1–15 + danh mục tài liệu tham khảo). PDF local = bản preprint arXiv.
- **Provenance / kiểm tra venue:** paper được xuất bản tại **MMM 2025 (MultiMedia Modeling), Springer LNCS,
  DOI 10.1007/978-981-96-2071-5_24** (Li, Luo, Xia). WebSearch `"WavFusion wav2vec 2.0 … IEMOCAP MELD MMM
  2025"` → `link.springer.com/chapter/10.1007/978-981-96-2071-5_24`. Abstract của Springer tái hiện
  **đúng các con số delta chính** trong PDF local (IEMOCAP +0.84% ACC / +0.74% WF1; MELD +0.43% ACC / +0.44% WF1)
  → các con số trọng yếu của bản preprint được đối chiếu xác nhận bởi bản venue. **✔ corroborated (deltas).**
  Các ô bảng tuyệt đối (WF1 70.6 v.v.) chỉ có ở arXiv nhưng nhất quán nội tại với các delta đã được xác nhận.
- **Có bản mở rộng đăng tạp chí (đánh dấu, chưa đọc):** cùng tác giả/cơ chế xuất hiện dưới dạng *"Improving speech emotion
  recognition using gated cross-modal attention and multimodal homogeneous feature discrepancy learning"*,
  **Applied Soft Computing 2025** (Elsevier, `S1568494625012281`) — **bị paywall, HTTP 403, chỉ có abstract, chưa
  bypass được.** Nếu gate trở thành ứng viên fusion của ViEmoSpeech, bản mở rộng này nhiều khả năng có các
  ablation đầy đủ hơn mà MMM bỏ qua (std, per-class F1); đáng để lấy bản có bản quyền sau này.

### What the paper actually does

**Task.** Phân loại emotion **categorical** ở cấp utterance (ERC), `y_j ∈ R^c`. Không có V/A, không có
output dimensional, không có distress. Trimodal: audio (a) + text (t) + **visual (v)**.

**Architecture (Eqs 1–11).** Hai nhóm encoder đưa vào một wav2vec 2.0 đã được chỉnh sửa:
- *Auxiliary encoders (đóng băng):* **visual** = EfficientNet → khối `A-GRU-LVC` (GRU + self-attention `X_v1`
  ⊕ một khối local 1-D **Learnable Visual Center** `X_v2`, Eqs 2–4); **text** = **RoBERTa-base (đóng băng)** →
  GRU + self-attention (Eqs 5–6). Số chiều cuối: text 768, visual 64.
- *Major encoder (fine-tune một phần):* wav2vec 2.0. Các lớp transformer **shallow** (gốc) vẫn giữ
  self-attention; các lớp transformer **deep** có self-attention của chúng **được thay thế bằng gated cross-modal
  attention**. Điểm mấu chốt: *"we unfreeze the parameters of the deep transformer layer in wav2vec 2.0 … the
  other layers are freezing"* (§3.2). Vậy nên backbone audio được **fine-tune một phần**, không phải đóng băng.

**Gated cross-modal fusion (cơ chế V-A, Eqs 7–11):**
```
X_a  = FST(S_a)                       # shallow-transformer acoustic features   (Eq 7)
X_F1 = CMA-T(X_a, X_t)                 # audio<-text cross-modal attention       (Eq 8)
X_F2 = CMA-V(X_a, X_v)                 # audio<-visual cross-modal attention     (Eq 9)
P    = sigmoid( FC( X_F1 (+) X_F2 ) )  # per-channel learnable gate              (Eq 10)
X_F  = P (.) X_F1 + (1 - P) (.) X_F2   # gated convex mix of the two streams     (Eq 11)
```
Gate `P` là một sigmoid theo từng kênh trên phép concatenation của hai tensor đã được tăng cường cross-modal;
`X_F` trộn lồi (convex-mix) các đặc trưng acoustic đã tăng-cường-bởi-text và đã tăng-cường-bởi-visual để
"lọc bỏ thông tin sai lệch sinh ra trong quá trình tương tác cross-modal." **⚠ Eq 10 trong cả bản PDF arXiv lẫn
OCR đều viết đúng nguyên văn là `FC(X_F1 ⊕ X_F1)` — một lỗi đánh máy; đúng ra phải là `X_F1 ⊕ X_F2` (nếu không
`P` sẽ không bao giờ thấy được luồng visual). Load-bearing cho bất kỳ lần re-implementation nào.**

**Homogeneous-feature-discrepancy (margin) loss (Eqs 12–15).** Các `X_a, X_t, X_v` chưa fuse đi qua một
linear encoder dùng chung `SD`; một **margin loss** kiểu triplet `L_mar` (Eq 13) kéo các cặp *cùng-emotion /
khác-modality* lại gần nhau và đẩy các cặp *cùng-modality / khác-emotion* ra xa nhau (cosine sim, margin θ).
Tổng loss `L_total = L_task(CE) + β·L_mar` (Eq 15). **Loss này cần các mẫu theo cặp của cùng một utterance
trên ≥2 modality mang cùng một gold emotion.**

**Data.** IEMOCAP (12 giờ, 10 diễn viên, 7,380 mẫu, 5-fold CV — sessions 1–4 train/val, session 5 test) và
MELD (Friends TV, ~1,400 dialogue / ~13,000 utt, 7-way, split định trước). Metric: ACC, Weighted-F1.

**Results (chính xác, kèm tham chiếu bảng):**
- **IEMOCAP (Table 1):** WavFusion **ACC 70.53 / WF1 70.6**; SOTA trước đó M2FNet WF1 69.86 / HAAN-ERC ACC 69.69,
  WF1 69.47. Delta **+0.84 ACC / +0.74 WF1** so với SOTA. **✔ corroborated** (abstract Springer).
- **MELD (Table 2):** WavFusion **ACC 66.93 / WF1 66.1**; HAAN-ERC ACC 66.5 / WF1 65.66. Delta **+0.43 ACC /
  +0.44 WF1**. **✔ corroborated** (abstract Springer).
- **Modality ablation (Table 3, IEMOCAP, WF1):** A 65.59 · T 58.63 · **V 26.31** · A+T **67.45** · A+V 64.14 ·
  A+T+V **70.6**. **≈ arXiv-only.** Lưu ý: **A+V (64.14) *thấp hơn* A đơn lẻ (65.59)** — visual gây hại
  khi thiếu text; text là đối tác mang trọng lượng chính (+1.86 WF1 so với chỉ-audio), trimodal đầy đủ cộng thêm +5.01.
- **Khối LVC (Table 4):** không có 69.84 → có **70.60** WF1 (+0.76). **≈ arXiv-only** (chỉ-visual, không liên quan đến chúng ta).
- **Trọng số margin-loss β (Table 5, WF1):** β=0 → 67.66; 0.01 → 68.39; 0.1 → 68.96; **β=1 → 70.6**; β=10 → 64.19.
  β=1 tốt nhất cho **+2.94 WF1 so với β=0**; β=10 *sụp đổ* (−3.47 so với β=1). **≈ arXiv-only.**
- **Gated attention so với concat (Table 6, ablation V-A, WF1):** **concat** thuần (12 shallow / 0 deep) = **66.78**;
  gated attention ở 11/1 = 68.55 · 10/2 = 68.32 · **9 shallow / 3 deep = 70.6** · 8/4 = 69.06. Gate ở tỉ lệ
  tối ưu 9/3 vượt concat **+3.82 WF1 / +3.86 ACC**. **≈ arXiv-only** (chạy một lần, không có std).

### Parts directly useful for ViEmoSpeech (tagged by Decision ID)

1. **[V-A] Bản thân gate (Eqs 8–11) như một ứng viên learned-fusion.** Một phương án thay thế concatenation
   cụ thể, rẻ (một FC + sigmoid + một convex mix), với một *ablation concat-vs-gated sạch sẽ* (66.78 → 70.6 WF1,
   Table 6). Đây là hàng so sánh tham chiếu cho câu hỏi "liệu learned gating có vượt qua rule/concat fusion không?"
2. **[V-A/V-B] Vị trí đặt gate là điều load-bearing.** WavFusion **không** gắn gate lên trên các đặc trưng
   đóng băng — nó **thay thế self-attention bên trong 3 lớp transformer wav2vec2 cuối cùng** và **fine-tune
   các lớp đó** (§3.2, lưới sweep shallow/deep của Table 6). Mức +3.82 WF1 bị đan xen với việc fine-tune backbone.
3. **[V-C] Head text RoBERTa-base đóng băng + GRU + self-attention** đưa vào cross-attention (Eqs 5–6). Là
   một tương đồng trực tiếp cho một nhánh text **PhoBERT-trên-PhoWhisper đóng băng** — nhưng họ dùng
   **transcript gold của IEMOCAP**, không bao giờ dùng output ASR.
4. **[V-A/V-E] Margin (homogeneous-discrepancy) loss (Eqs 12–15), β=1 tốt nhất, +2.94 WF1.** Một auxiliary
   ở cấp biểu diễn cần các cặp *cùng-utterance cùng-emotion khác-modality* — ViEmoSpeech (audio + text-ASR,
   cả hai từ cùng một clip với một gold label dùng chung) **có thể cung cấp cặp audio↔text** (không có visual).
5. **[V-G] Định dạng bảng modality-ablation (Table 3)** như một template báo cáo cho câu hỏi "nhánh text
   mang bao nhiêu trọng lượng?" — chính là phép đo phụ thuộc-register mà bản tổng hợp ViEmoSpeech cần.

### How each part helps ViEmoSpeech succeed

- **[V-A] Thêm một nhánh "gated fusion" vào bake-off fusion.** Bên cạnh CASE/FAS (vn-07) và cross-attention
  thuần, hiện thực Eqs 8–11 chỉ với **hai** luồng (bỏ `CMA-V`): định nghĩa lại gate trên audio↔text (ví dụ
  `X_F = P⊙X_audio-aug + (1−P)⊙X_text-aug`). Báo cáo nó so với concat và các hàng baseline rule-fusion.
  **Rủi ro chuyển giao:** gate của WavFusion trọng tài giữa các luồng acoustic **text-aug và visual-aug**;
  khi bỏ visual, convex mix hai chiều mất đi ý nghĩa gốc và phải được định nghĩa lại (gate audio↔text). Mức
  +3.82 WF1 **không** chuyển giao nguyên trạng — đó là một con số trimodal.
- **[V-B] KHÔNG sao chép công thức "ghép gate vào wav2vec2 + fine-tune các lớp deep" dưới ràng buộc
  frozen-backbone.** Mặc định của ViEmoSpeech là một WavLM/emotion2vec **đóng băng**. Mức tăng của WavFusion
  bị nhiễu bởi việc unfreeze 3 lớp transformer cuối, nên ablation của nó không thể chứng nhận một gate
  *post-hoc, trên đặc trưng đóng băng*. **Hành động:** nếu muốn dùng gate, hãy đặt nó trong một **fusion head
  riêng biệt trên đặc trưng đóng băng**, và coi con số của WavFusion là một trần fine-tuned, không phải một
  mức chuẩn cho đóng băng. **Rủi ro chuyển giao: cao** — khẳng định "drop-in" ở compact entry phía trên là
  sai; nó nằm nhúng trong một backbone đã fine-tune.
- **[V-C] Nhánh text là đối tác mang trọng lượng chính, nhưng họ đã "ăn gian" về chất lượng transcript.**
  Table 3 cho thấy text nâng audio +1.86 WF1 trong khi visual lại *gây hại* (−1.45). Điều này đáng khích lệ
  cho thiết kế audio+text-only của chúng ta — **ngoại trừ** text của họ = **transcript gold**; ViEmoSpeech
  cấp **PhoWhisper ASR vốn hoán đổi thanh điệu ở arousal cao** (mày→máy). **Hành động:** chạy ablation của
  Table 3 hai lần — text-caption gold so với text-ASR — để đo mức phạt do ASR gây ra trên mức tăng fusion.
  **Rủi ro chuyển giao: cao** — +1.86 là một cận trên mà chúng ta sẽ không thấy được trên ASR.
- **[V-A/V-E] Tái sử dụng margin loss để căn chỉnh audio↔text-ASR của cùng một clip.** Với một gold emotion
  dùng chung cho mỗi clip, chúng ta có thể tạo trực tiếp các cặp dương cùng-emotion/khác-modality. β=1
  (Table 5) là trọng số khởi điểm; sự sụp đổ ở β=10 cảnh báo không nên đặt trọng số quá cao. **Rủi ro chuyển
  giao: trung bình** — căn chỉnh cosine-margin giả định hai modality *nên* hội tụ; trên text bị nhiễu ASR
  của một clip arousal cao, chúng có thể phân kỳ một cách hợp lý, nên cần giới hạn β ở mức thấp và tắt gate
  ở các lượt có độ tin cậy ASR thấp.
- **[V-G] Công bố bảng modality-ablation** (chỉ-audio / chỉ-text / audio+text) trên holdout speaker-disjoint
  của chúng ta, như một câu trả lời trung thực, theo-register cho chủ đề xuyên suốt "ưu thế text-so-với-audio
  phụ thuộc vào register" (synthesis pt 1).

### Cross-ref — is fusion gain register/dataset-dependent? Where does gating help most?

**Có, và WavFusion đang báo cáo thiếu.** Toàn bộ ablation fusion/gating (Tables 3–6) chỉ được chạy **trên
IEMOCAP** (acted, scripted+improvised, transcript gold sạch, 5-fold). MELD (Friends TV, các utterance ngắn,
ồn, chồng lấn) **không có** ablation modality/gating nào — chỉ có hai hàng so sánh SOTA chính, nơi WF1 tuyệt
đối của WavFusion thấp hơn nhiều (66.1 so với 70.6) và biên độ vượt SOTA thu hẹp lại (+0.44 so với +0.74).
Vậy nên bằng chứng cho thấy **gating/fusion giúp ích nhiều nhất trên corpus sạch hơn, acted, có transcript
gold (IEMOCAP)**, còn lợi ích của nó trên corpus hội thoại ồn hơn (MELD) thì chưa được đo/nhỏ hơn. Điều này
khớp trực tiếp với phát hiện ở cấp chương trình (vn-08 so với vn-12 so với bimodal-01): **mức tăng từ fusion
phụ thuộc vào register và chất lượng transcript, lớn nhất ở nơi kênh text sạch.** Đối với ViEmoSpeech — audio
TV-drama đã tìm được + *text ASR ồn* — điều này dự báo mức tăng fusion của chúng ta sẽ gần với chế độ MELD
(chưa đo, khả năng nhỏ hơn) hơn là màn trình diễn của IEMOCAP. Chúng ta phải tự đo trên register của chính
mình thay vì thừa hưởng con số +3.82.

### Child mental-health / ViEmoSpeech transfer lens

- **Không có tone, không có phonation, không có VN.** WavFusion hoàn toàn không có khái niệm về thanh điệu
  từ vựng hay chất giọng (voice-quality); modality "thêm" của nó là **visual (khuôn mặt)**, thứ mà
  ViEmoSpeech không có và về mặt pháp lý sẽ không được phát hành. Toàn bộ bộ máy A-GRU-LVC (Eqs 1–4, Table 4)
  là trọng lượng chết đối với chúng ta. Cái còn sót lại được *chỉ* là gate audio↔text.
- **Acted, categorical, người lớn.** IEMOCAP/MELD là emotion acted/TV của người lớn, không có distress, không
  có V/A, không có trẻ vị thành niên — nhất quán với phần còn lại của bộ sưu tập; **không đóng góp gì** cho
  V-D (tone×emotion), V-F (sàn recall của distress), hay câu hỏi về register trẻ em. Giá trị của nó thuần túy
  nằm ở kiến trúc (V-A) và mang tính cảnh báo (V-B).
- **Đạo đức/rủi ro:** không có gì đặc thù; nhưng việc nhắc tên "mental health" trong intro (ref 4) đi kèm một
  benchmark hoàn toàn acted là cùng một mẫu hình overclaim đã bị gắn cờ cho vn-10/EAA — trích dẫn như *không
  phải khung diễn giải của chúng ta*.

### Limitations & open questions for ViEmoSpeech (≥1 contradiction/gap)

- **Mâu thuẫn với ràng buộc frozen-backbone của ViEmoSpeech (V-B):** mức tăng chính của WavFusion đòi hỏi
  **fine-tune các lớp deep của wav2vec2** và **nhúng gate bên trong chúng** (§3.2, Table 6). Đây *không phải*
  một kết quả fusion post-hoc trên đặc trưng đóng băng. Bất kỳ trích dẫn nào về "gated fusion vượt concat
  +3.82 WF1" đều phải kèm lưu ý này, nếu không sẽ trình bày sai những gì một ViEmoSpeech frozen-backbone sẽ
  đạt được. **Điều này cũng đính chính compact entry đã lưu trữ ở trên, vốn gọi gate là một khối "drop-in".**
- **Mâu thuẫn với bimodal-02 ABHINAYA & vn-07 CASE về các lớp hiếm:** WavFusion **không báo cáo per-class F1
  và không có std** — trên một task mất cân bằng 4–7 lớp với một con số 5-fold duy nhất, biên độ +0.74 WF1
  hoàn toàn có thể nằm trong biên độ nhiễu của CV, và sự sụp đổ ở lớp hiếm (fear/disgust) — thứ mà ABHINAYA
  giới hạn ở mức ~26–29% F1 và CASE cho thấy là 0-correct — **hoàn toàn bị che khuất**. Đối với sàn distress/
  lớp-hiếm của chúng ta (V-F/V-E), WavFusion không cung cấp bằng chứng nào cho thấy gate giúp ích cho phần
  đuôi; nó có thể chỉ dịch chuyển các lớp đầu (head classes).
- **Khoảng trống — chưa bao giờ đối mặt với ASR:** text luôn là transcript gold; mức tăng fusion dưới
  **nhiễu hoán-đổi-thanh-điệu do ASR** (input thực tế của chúng ta) chưa được kiểm chứng. Câu hỏi mở: liệu
  gate có học được cách **giảm trọng số** luồng text (đẩy `P→1` về phía audio) khi ASR sai, hay nó lan truyền
  lỗi đi tiếp? Đáng để làm một phân tích riêng về ASR-confidence×gate-value trên các clip của chúng ta.
- **Khoảng trống — margin loss cần các cặp cross-modal mà chúng ta chỉ có một nửa:** được thiết kế cho 3
  modality; chỉ với audio↔text-ASR, tập dương "cùng-emotion/khác-modality" sẽ mỏng hơn và nhiễu hơn (text ASR
  có thể hoàn toàn không mang cảm xúc trên một câu cảm thán ngắn). Chưa kiểm chứng liệu β=1 có còn phù hợp
  trong chế độ 2-modality, text nhiễu hay không.
- **Không khớp metric:** WavFusion chỉ có WF1-trên-categorical — không có CCC, không có V/A, không có distress
  — nên nó **không dịch chuyển gì** trên đánh giá dimensional và recall-floor của V-D/V-F/V-G; nó chỉ là một
  input kiến trúc cho V-A/V-B/V-C.
