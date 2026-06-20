# Paper 25 — emotion2vec: Self-Supervised Pre-Training for Speech Emotion Representation

## 1. Thông tin thư mục

**Tiêu đề:** emotion2vec: Self-Supervised Pre-Training for Speech Emotion Representation

**Tác giả:** Ziyang Ma (Shanghai Jiao Tong University, tác giả liên hệ), Zhisheng Zheng (SJTU), Jiaxin Ye (Fudan University), Jinchao Li (The Chinese University of Hong Kong), Zhifu Gao (Alibaba), Shiliang Zhang (Alibaba), Xie Chen (SJTU).

**Đơn vị:** Shanghai Jiao Tong University; Fudan University; The Chinese University of Hong Kong; Alibaba.

**Năm / hội nghị:** Findings of the Association for Computational Linguistics: ACL 2024, trang 15747–15760, 11–16 tháng 8 năm 2024.

**Mã nguồn/checkpoint:** https://github.com/ddlBoJack/emotion2vec (mã nguồn, checkpoint, và đặc trưng đã trích xuất).

**Luận điểm một dòng:** Một backbone biểu diễn cảm xúc giọng nói *phổ quát* (universal) — được tiền-huấn-luyện bằng self-supervised online distillation trên 262 giờ audio cảm xúc — mà chỉ với encoder đóng băng + linear probe đã vượt các mô hình SSL tổng quát (HuBERT/WavLM/data2vec) và các mô hình chuyên biệt SER trên IEMOCAP và trên 10 ngôn ngữ.

## 2. Động lực của bài toán

Các tác vụ cảm xúc giọng nói (SER, sentiment analysis) trong lịch sử dùng đặc trưng FBank/MFCC (nghèo ngữ nghĩa) hoặc đặc trưng từ các mô hình SSL giọng nói tổng quát (wav2vec 2.0, HuBERT, WavLM). Loại sau mạnh nhưng "không hoàn toàn phù hợp cho tác vụ cảm xúc" — chúng được tiền-huấn-luyện cho nội dung phonetic/ASR, không phải cho affect (cảm xúc). Có hai cách khắc phục tạm thời: (a) fine-tune một mô hình SSL tổng quát trên từng tập dữ liệu cảm xúc (tốn kém; kết luận phụ thuộc dữ liệu/mô hình), hoặc (b) chưng cất (distill) một mô hình SER đơn lẻ (ví dụ Vesper, chưng cất từ WavLM-large) mà khả năng biểu diễn *phổ quát* chưa được chứng minh. Bài báo lập luận rằng lĩnh vực này cần một biểu diễn cảm xúc *phổ quát*, đóng băng, duy nhất, hoạt động ngay (out-of-the-box) trên nhiều tác vụ cảm xúc và nhiều ngôn ngữ — tương tự text emotion embedding bên văn bản. emotion2vec lấp khoảng trống đó.

## 3. Vị trí trong tài liệu

Hai họ SSL được phân biệt theo loại đích self-supervised. **Offline targets** cần một teacher đã huấn luyện trước khi tiền-huấn-luyện: HuBERT và WavLM (đích K-means), PBERT/MonoBERT/PolyBERT (đích phoneme). **Online targets** cập nhật teacher *trong khi* tiền-huấn-luyện qua online distillation: data2vec / data2vec 2.0 (frame-level MLM loss) và CA-DINO (utterance-level cross-entropy). emotion2vec thuộc họ online-distillation và đặc biệt ở chỗ **kết hợp utterance-level loss VÀ frame-level loss** — tính mới được tuyên bố là thông tin toàn cục (cả phát ngôn) và cục bộ (frame) đều mang cảm xúc, nên cần cả hai pretext task. Về phía biểu diễn, công trình cảm xúc giọng nói trước đây hoặc dùng trực tiếp đặc trưng SSL tổng quát đóng băng, hoặc fine-tune theo từng tác vụ; emotion2vec được định vị là mô hình biểu diễn *cảm xúc giọng nói phổ quát* đầu tiên, tương tự như text emotion embeddings (Emo2Vec, v.v.).

## 4. Đào sâu phương pháp

### 4.1 Pipeline (online distillation teacher–student)

Hai mạng chia sẻ kiến trúc: một **teacher T** và một **student S**, mỗi mạng = bộ trích đặc trưng F (CNN 1-D 7 lớp) + backbone B (Transformer nhiều lớp). Cả hai được khởi tạo từ **cùng trọng số tiền-huấn-luyện** (data2vec hoặc data2vec 2.0). Cho audio thô X:
- Teacher: đặc trưng đã downsample Z0ᵀ = Fᵀ(X) đưa thẳng vào Bᵀ.
- Student: Z0ˢ = Fˢ(X), rồi **mask** (l = 5 frame liên tiếp, mỗi frame là điểm bắt đầu mask với xác suất p = 0.5), với một **utterance embedding U** học được đặt phía trước trước khi vào backbone Bˢ.
- Đích teacher Yᵀ là **trung bình của top k = 8 khối Transformer** đầu ra.
- Đầu ra: utterance-level embedding của student Uˢ và frame-level embedding Yˢ.

### 4.2 Utterance-level loss (cảm xúc toàn cục)

MSE giữa đầu ra frame của teacher đã pooling theo thời gian và đầu ra utterance của student đã pooling theo thời gian:

`L_Utt = (mean(Yᵀ) − mean(Uˢ))²`   (Eq. 6–8)

Ba biến thể để tính (Fig. 2): **Token** (một utterance token, Nu = 1), **Chunk** (nhiều utterance token — gộp nhiều thông tin toàn cục hơn), **Global** (không thêm token; pooling theo thời gian đầu ra frame Yˢ). Ablation chọn **Chunk** là tốt nhất.

### 4.3 Frame-level loss (cảm xúc theo ngữ cảnh)

MSE chỉ trên **các frame bị mask** (pretext MLM chuẩn): `L_Frm = (1/M) Σ_{i∈M} (Yᵢᵀ − Yᵢˢ)²`  (Eq. 9).

### 4.4 Mục tiêu online distillation

Tổng loss của student: **L = L_Frm + α · L_Utt** (Eq. 10), với α điều chỉnh được. Student cập nhật bằng backprop; **teacher cập nhật bằng EMA** của student: `θᵀ_{t+1} = τ·θᵀ_t + (1−τ)·θˢ_{t+1}` (Eq. 11), với τ **tăng tuyến tính từ 0.999 → 0.99999** trong quá trình tiền-huấn-luyện. Thực tế bộ trích đặc trưng Fᵀ của teacher được *sao chép trực tiếp* từ Fˢ mỗi bước; chỉ backbone Bᵀ được cập nhật bằng EMA. Không cần teacher ngoài/đóng băng — teacher *chính là* một bản sao chuyển động chậm của student (kiểu BYOL/data2vec).

### 4.5 Khởi tạo, siêu tham số, chi phí huấn luyện

- **Mô hình khởi tạo:** data2vec hoặc data2vec 2.0 (cả hai tiền-huấn-luyện trên LibriSpeech 960h). Cùng bộ trích đặc trưng CNN 1-D 7 lớp: kernel (5,2,2,2,2,2,2), stride (10,3,3,3,3,2,2) → **downsample 320×**; audio thô 16 kHz → đặc trưng 50 Hz / 512 chiều; linear projection 512→768 trước khi mask. Backbone = Transformer 12 lớp, model dim 768, FFN 3072, 12 heads (data2vec 2.0 thêm một CNN decoder 4 lớp, kiểu MAE, chỉ encode các frame không bị mask để tăng hiệu quả).
- **Tiền-huấn-luyện:** 262 giờ dữ liệu cảm xúc không nhãn; 4× GPU NVIDIA A10 mô phỏng 16 GPU (update frequency 4); **100 epoch**, ~37 phút/epoch; dynamic batch, tối đa 1×10⁶ token; Adam, LR 7.5×10⁻⁵, weight decay 1×10⁻², lịch cosine với 5% linear warm-up; α = 1; EMA teacher τ 0.999→0.99999.
- **Downstream:** emotion2vec đã tiền-huấn-luyện được **đóng băng**; chỉ huấn luyện một head nhẹ. Tác vụ không tuần tự dùng công thức SUPERB (hai linear + ReLU ở giữa, hidden dim 256). Tác vụ tuần tự dùng GRU 2 lớp.

## 5. Tập dữ liệu

**Tập tiền-huấn-luyện (tổng 262 giờ, toàn tiếng Anh; Table 1 / Appendix B.1):** IEMOCAP (7.0 h), MELD (12.2 h), CMU-MOSEI (91.9 h), MEAD (37.3 h), MSP-Podcast v1.8 (113.5 h) → 169.053 phát ngôn. (Lưu ý: năm tập này trùng lặp với các benchmark tiếng Anh downstream; khả năng tổng quát out-of-domain được chứng minh trên các ngôn ngữ/tập giữ riêng.)

**Downstream / đánh giá (tổng 18 tập cảm xúc, 10 ngôn ngữ):** IEMOCAP, MELD, RAVDESS-Speech, RAVDESS-Song, SAVEE, CMU-MOSI, CMU-MOSEI (tiếng Anh); M3ED (tiếng Trung), SUBESCO (tiếng Bangla), CaFE (tiếng Pháp), EmoDB (tiếng Đức), AESDD (tiếng Hy Lạp), EMOVO (tiếng Ý), ShEMO (tiếng Ba Tư), RESD (tiếng Nga), URDU (tiếng Urdu). RAVDESS và SAVEE là **out-of-domain** (không thấy trong tiền-huấn-luyện); 9 tập ngoài tiếng Anh là các ngôn ngữ out-of-domain.

## 6. Kết quả

### 6.1 Kết quả chính IEMOCAP — linear probe so với các backbone SSL (Table 2)

Giao thức SUPERB: đóng băng upstream, huấn luyện linear head (downstream hidden dim 256). IEMOCAP gộp `excited`+`happy` → 4 lớp. WA = weighted accuracy (tổng thể), UA = unweighted (trung bình theo lớp), WF1 = weighted-F1. WA báo cáo (%):

| Mô hình | Corpus tiền-huấn-luyện | #Tham số upstream | Downstream | WA(%) |
|---|---|---|---|---|
| wav2vec 2.0 base | LS-960 | 95.04M | Linear | 63.43 |
| HuBERT base | LS-960 | 94.68M | Linear | 64.92 |
| WavLM base | LS-960 | 94.70M | Linear | 65.94 |
| WavLM base+ | Mix-94k | 94.70M | Linear | 67.98 |
| data2vec base | LS-960 | 93.75M | Linear | 67.38 |
| data2vec 2.0 base | LS-960 | 93.78M | Linear | 68.58 |
| Vesper-4 | Mix-94k + LSSED-206 | 63.52M | Linear | 68.40 |
| Vesper-12 | Mix-94k + LSSED-206 | 164.29M | Linear | 70.70 |
| **emotion2vec** | LS-960 + Emo-262 | **93.79M** | Linear | **71.79** |
| **emotion2vec\*** | LS-960 + Emo-262 | 93.79M | Linear | **74.48** (leave-one-speaker-out, cùng fold val/test) |
| wav2vec 2.0 large | LL-60k | 317.38M | Linear | 65.64 |
| HuBERT large | LL-60k | 316.61M | Linear | 67.62 |
| WavLM large | Mix-94k | 316.62M | Linear | 70.03 |
| TIM-Net (chuyên biệt, MFCC) | – | – | CNN (0.40M) | 68.29 |
| MSTR (chuyên biệt) | – | HuBERT-large | Transformer (27.0M) | 70.03 |
| DST (chuyên biệt) | – | WavLM-large | Transformer (22.78M) | 71.80 |

Điểm nổi bật: với ~93.79M tham số upstream + một **linear head 0.20M**, emotion2vec (WA 71.79; 74.48 theo giao thức speaker-independent cùng fold) **vượt mọi mô hình SSL tổng quát base và large**, vượt Vesper-12 (mô hình SER chuyên biệt chưng cất từ WavLM-large, 164.29M) với ít tham số hơn, và ngang/vượt các mô hình SER chuyên biệt có mạng downstream lớn hơn **2× (TIM-Net), 135× (MSTR), 114× (DST)**.

### 6.2 Các tập tiếng Anh khác (Table 3, WA%)

| Mô hình | MELD | RAVDESS | SAVEE |
|---|---|---|---|
| WavLM-base | 46.95 | 37.01 | 42.08 |
| data2vec 2.0 | 48.92 | 81.04 | 83.13 |
| **emotion2vec** | **51.88** | **82.43** | **84.38** |

(WF1 của emotion2vec: MELD 48.70, RAVDESS 82.86, SAVEE 84.45. RAVDESS/SAVEE là out-of-domain.)

### 6.3 Tổng quát theo ngôn ngữ (Table 4)

Trên cả **9 tập ngoài tiếng Anh out-of-domain** emotion2vec dẫn đầu mọi baseline SSL về WA/UA/WF1, ví dụ WA: AESDD-Gr 72.33, EmoDB-De 84.34, SUBESCO-Bn 90.91, CaFE-Fr 74.52, EMOVO-It 61.21, ShEMO-Fa 79.97, RESD-Ru 64.75, M3ED-Zh 49.15, URDU 81.50.

### 6.4 Tổng quát theo tác vụ

- **Song emotion recognition (RAVDESS-Song, Table 5):** emotion2vec đóng băng + Linear → WA 85.0 / UA 85.2 / WF1 84.8, vượt mọi baseline SSL *đóng băng* và ngang các chuyên biệt VQ-MAE-S *đã fine-tune*.
- **Emotion prediction in conversation (IEMOCAP, Table 6):** thay đặc trưng giọng nói bằng emotion2vec nâng UAR/MacroF1 ở cả speech-only (UAR 77.19 / MacroF1 76.71 so với Shi 2023 đạt 65.01 / 65.91) và speech+text đa phương thức (UAR 81.68 / MacroF1 80.75). EPC dùng GRU phân cấp trên 6 lượt hội thoại trước đó.
- **Sentiment analysis (CMU-MOSI/MOSEI, Table 7):** nhị phân (bỏ neutral), trung bình 4 lớp cuối + linear. WF1 của emotion2vec 65.41 / 74.75 (MOSI/MOSEI), vượt data2vec base, WavLM, và Whisper-Encoder có giám sát.

### 6.5 Trực quan hóa (Fig. 3, 5)

UMAP của đặc trưng linear-layer đầu tiên: WavLM và data2vec chồng lấp nặng giữa các lớp arousal cao/thấp; emotion2vec tách arousal rõ ràng với chuyển tiếp mượt cao→thấp, và (Fig. 5, SUBESCO) cho biên trong-lớp chặt hơn / giữa-lớp rộng hơn trên các cảm xúc rời rạc.

## 7. Ablations (Appendix C, leave-one-session-out 5-fold trên IEMOCAP)

- **Khởi tạo (Table 8):** cold-start WA 61.34 → khởi tạo data2vec 70.2 → **khởi tạo data2vec 2.0 71.79**. Warm-start teacher/student của online-distillation từ một mô hình tiền-huấn-luyện đáng giá ~+10 WA so với cold start.
- **Loss huấn luyện (Table 9):** chỉ utterance-loss sụp đổ (WA 28.96). Chỉ frame-loss đã hoạt động (WA 70.85). **Frame + utterance** tốt nhất (WA 71.79). Nối utt+frame embeddings ở downstream ≈ chỉ frame.
- **Biến thể utterance-loss (Table 10):** Token 70.46 / **Chunk 71.79** / Global 70.30.
- **Trọng số loss α (Table 11):** α = 0 → 70.85; 0.1 → 71.06; **1 → 72.14**; 10 → 70.58. Tỉ lệ frame:utterance 1:1 là tốt nhất.

## 8. Hạn chế tác giả nêu

(1) emotion2vec cho biểu diễn phổ quát nhưng **vẫn cần huấn luyện một mô hình downstream riêng cho mỗi tác vụ** — nó là một bộ trích đặc trưng, không phải hệ thống đa-tác-vụ end-to-end. (2) **Chưa khảo sát liệu thông tin người nói có bị loại bỏ hay không** — quan trọng cho việc dùng biểu diễn vào emotional-TTS (tức embedding có thể vẫn mang danh tính người nói).

## Deep research — full-PDF read (2026-06-16)

> Khung tham chiếu: Luận điểm của Pebble bao gồm một **phương thức voice-message** dự kiến — một
> đứa trẻ gửi clip âm thanh, Pebble phải chấm điểm affect từ giọng nói (không chỉ văn bản).
> emotion2vec là ứng viên mạnh nhất cho một **backbone SSL chuyên biệt cảm xúc, đóng băng, drop-in
> cho tiếng Anh giọng nói** nuôi các head emotion/severity của Pebble ở phía audio, đúng kiểu
> NeoBERT phục vụ phía văn bản. Phần này đọc đối chiếu với **bản camera-ready ACL Findings 2024**
> (aclanthology.org/2024.findings-acl.931, tr. 15747–15760). Bản PDF cục bộ `pdfs/25-emotion2vec.pdf`
> mang footer trang ACL 2024 và số trang tương ứng, tức nó *chính là* bản camera-ready, nên có thẩm
> quyền; README GitHub được dùng làm nguồn thứ hai cho kích thước mô hình / phạm vi ngôn ngữ.

### Source-access note (Ghi chú truy cập nguồn)

- **Đã đọc:** toàn bộ PDF trích bằng `pdftotext "pdfs/25-emotion2vec.pdf" -` (1207 dòng, ~52 KB);
  mọi bảng (2–11), phần methods/equations, và Appendices A–D đọc trọn vẹn.
- **Đã kiểm chứng web:**
  - Hội nghị, dải trang, abstract, tuyên bố "10 languages" — `aclanthology.org/2024.findings-acl.931/`
    (truy vấn: *"emotion2vec Self-Supervised Pre-Training for Speech Emotion Representation ACL Findings
    2024 IEMOCAP WA 262 hours"*). **✔ đã xác nhận** (hội nghị = Findings of ACL 2024, tr. 15747–15760;
    abstract xác nhận "10 different languages").
  - Kích thước mô hình (~90M base / ~300M large) + phạm vi đa ngôn ngữ — `github.com/ddlBoJack/emotion2vec/blob/main/README.md`.
    **✔ đã xác nhận** (base ~90M khớp với 93.79M của bài; README còn ghi các biến thể emotion2vec+
    seed/base/large fine-tune trên 201/4788/42526 giờ — *không có trong bài báo*).
- **Quy tắc xung đột:** không tìm thấy bất đồng preprint; PDF cục bộ = camera-ready, dùng số liệu nguyên trạng.
- Mọi số liệu dưới đây kèm ref Table/Eq./§ và một nhãn trạng thái (✔ đã xác nhận đối chiếu metadata
  hội nghị khi hội nghị có công bố; ≈ số liệu chỉ-trong-PDF của bản camera-ready, nhất quán nội bộ,
  không thể tái dẫn độc lập từ nguồn công khai thứ hai).

### Bài báo thực sự làm gì (số liệu đã kiểm chứng)

- **Dữ liệu tiền-huấn-luyện: 262 giờ** audio cảm xúc tiếng Anh không nhãn (IEMOCAP 7.0 + MELD 12.2 +
  CMU-MOSEI 91.9 + MEAD 37.3 + MSP-Podcast 113.5 = 169.053 phát ngôn) — Table 1 / Appendix B.1.
  **≈** (chỉ-trong-PDF; abstract chỉ nói "open-source unlabeled emotion data").
- **Mục tiêu: online self-distillation, `L = L_Frm + α·L_Utt`** (Eq. 10), teacher = **EMA của student**,
  τ tuyến tính **0.999→0.99999** (Eq. 11); đích teacher = trung bình top **k=8** khối Transformer; mask
  l=5 frame, p=0.5; **α=1** tốt nhất (Table 11). **≈** (chỉ-trong-PDF, có ablation hỗ trợ).
- **Kích thước mô hình: 93.79M** tham số upstream (base, Transformer 12 lớp, 768-dim), head downstream
  **0.20M** (hai linear + ReLU) — Table 2. Base ~90M **✔** đã xác nhận bằng README GitHub.
- **# benchmark: 18 tập cảm xúc, 10 ngôn ngữ** (9 tiếng Anh + Trung/Bangla/Pháp/Đức/Hy Lạp/Ý/Ba Tư/
  Nga/Urdu); "13 tập" dùng trong sweep SER đa ngôn ngữ — Table 1, §1. "10 languages" **✔** đã xác nhận (abstract).
- **WA linear-probe IEMOCAP: 71.79%** (leave-one-session-out 5-fold) / **74.48%** (emotion2vec\*,
  leave-one-speaker-out, cùng fold val/test) — Table 2. so với HuBERT-base **64.92**, WavLM-base **65.94**,
  WavLM-base+ **67.98**, data2vec-2.0-base **68.58**, WavLM-**large** **70.03**, Vesper-12 (chưng cất từ
  WavLM-large, 164.29M) **70.70**. **≈** (chỉ-trong-PDF; các delta SSL đại diện lớn và nhất quán xuyên
  Table 2–4).
- **Vượt các mô hình SER chuyên biệt với mạng downstream nhỏ hơn 2×/135×/114×** (TIM-Net 68.29 /
  MSTR 70.03 / DST 71.80 so với emotion2vec 71.79 với head 0.20M) — Table 2. **≈**.
- **Warm-start có ý nghĩa: +10.45 WA** (cold-start 61.34 → khởi tạo data2vec-2.0 71.79) — Table 8. **≈**.
- **Cần cả hai loss:** chỉ utt sụp đổ (WA 28.96); chỉ frame 70.85; frame+utt 71.79 — Table 9. **≈**.

### Các phần trực tiếp hữu ích cho Pebble (gắn nhãn từng Decision ID)

1. **Encoder đóng băng + linear-probe = công thức SER cạnh tranh rẻ nhất** — emotion2vec đóng băng +
   một linear head **0.20M** vượt các backbone SSL fine-tune-toàn-phần/large (Table 2). **[D-A, D-E]**
   Đây là phản chiếu phía audio của kế hoạch văn bản của Pebble: một backbone chuyên biệt đóng băng với
   head tác vụ nhẹ, không fine-tune toàn phần tốn kém.
2. **emotion2vec là backbone audio drop-in cho phương thức voice-message** — đã tiền-huấn-luyện,
   checkpoint công khai, mạnh tiếng Anh, giao diện đặc trưng đóng băng (768-dim). **[D-A, D-H]** Nó là
   tương đồng giọng nói của việc chọn NeoBERT thay vì fine-tune một encoder tổng quát: chọn mô hình SSL
   *chuyên biệt cảm xúc*, không phải SSL ASR tổng quát (HuBERT/WavLM), cho affect.
3. **Severity ≈ arousal, và emotion2vec tách arousal rõ ràng** (UMAP Fig. 3; cụm arousal cao/thấp,
   chuyển tiếp mượt) — liên quan trực tiếp tới **head severity regression** của Pebble. **[D-D]** Manifold
   arousal liên tục là một nguồn transfer cho tín hiệu cường độ phía giọng nói, đối ứng audio của
   chuyển giao cường độ WASSA/SemEval dùng trên văn bản.
4. **Online self-distillation với frame-MLM + utterance loss, warm-start từ một checkpoint tiền-huấn-luyện**
   (Eq. 10–11; Table 8 +10 WA từ warm start). **[D-E, D-F]** Bằng chứng độc lập rằng (a) warm-start một
   mục tiêu SSL từ checkpoint sẵn có vượt cold start với khoảng cách lớn, và (b) một pretext kiểu
   masked/MLM là loss gánh vác (chỉ-frame đã đạt 70.85; chỉ-utt sụp đổ) — cả hai củng cố kế hoạch MLM
   domain-adaptive (D-F) và warm-start theo giai đoạn (D-E) của Pebble bên văn bản.
5. **Ablation cân bằng loss = static 1:1 thắng** (α: 0→70.85, 0.1→71.06, 1→72.14, 10→70.58; Table 11).
   **[D-B]** Một điểm dữ liệu trong-miền sạch rằng một trọng số loss tĩnh đơn giản (ở đây 1:1) có thể
   thắng cả thiếu-trọng-số lẫn thừa-trọng-số — đạn dược liên quan cho lập trường "bắt đầu với static λ
   trước khi với tới Kendall/GradNorm" của Pebble về cân bằng MTL.
6. **Tổng quát đa ngôn ngữ từ tiền-huấn-luyện thiên tiếng Anh** — emotion2vec tiếng-Anh đóng băng dẫn
   đầu mọi baseline SSL trên 9 tập SER ngoài tiếng Anh (Table 4). **[D-H]** Bằng chứng rằng một backbone
   SSL cảm xúc transfer được xuyên ngôn ngữ chỉ với một linear head huấn luyện lại — hữu ích nếu Pebble
   từng mở rộng phương thức giọng nói ra ngoài tiếng Anh.

### Mỗi phần giúp Pebble thành công thế nào (hành động cụ thể)

- **Nối dây head voice-message [D-A/D-E].** Thêm một đường `audio/`: `emotion2vec (đóng băng) →
  đặc trưng 768-dim mean/4-lớp-cuối → {head emotion 12-nhãn, head severity regression}`, đúng công thức
  SUPERB (hai linear + ReLU, hidden 256). **Không** fine-tune backbone ở v1 — Table 2 cho thấy probe đóng
  băng đã vượt các baseline fine-tune, nên đây vừa rẻ hơn vừa là baseline mạnh hơn. Phản chiếu hình dạng
  head NeoBERT để Decision Engine thấy cùng một hợp đồng đầu ra từ text và audio.
- **Severity từ arousal [D-D].** Huấn luyện head severity audio như một regression lên đích
  arousal/cường độ; manifold arousal sạch của emotion2vec (Fig. 3) là lý do một severity probe *tuyến tính*
  khả thi. Báo cáo Pearson (metric severity Pebble chọn) trên một lát child-voice giữ riêng, tương đồng
  audio của chuyển giao cường độ WASSA bên văn bản.
- **Bằng chứng warm-start + MLM [D-E/D-F].** Trích Table 8 (+10 WA cold→warm) và Table 9 (frame-MLM là loss
  gánh vác) làm corroboration xuyên phương thức cho lượt MLM domain-adaptive bên văn bản và staging
  gradual-unfreeze/warm-start của Pebble — "một warm start SSL + pretext MLM đáng ~10 điểm" là một prior
  transfer được dù phương thức khác nhau.
- **λ mặc định MTL [D-B].** Dùng Table 11 làm lý do *bắt đầu* MTL emotion+severity của Pebble với static
  1:1 (hoặc một λ tinh chỉnh đơn) và chỉ leo thang lên các phương pháp LibMTL nếu một head giữ-riêng tụt
  — emotion2vec thấy static 1:1 tối ưu trong {0, 0.1, 1, 10}.
- **Lập luận chọn backbone [D-A].** Khi biện minh NeoBERT-thay-vì-tổng-quát trên văn bản, trích emotion2vec
  làm kết quả audio song song: một backbone SSL *chuyên biệt cảm xúc* vượt SSL tổng quát (HuBERT/WavLM) và
  cả các mô hình lớn hơn về affect, với một head bé tí. Luận điểm "chuyên biệt thắng tổng quát ở ngân sách
  head nhỏ" đối xứng xuyên phương thức.

### Lăng kính sức khỏe tâm thần trẻ em (tính hợp lệ transfer, rủi ro, giảm thiểu, đạo đức)

- **Nguồn gốc giọng người lớn/đóng diễn — rủi ro transfer CAO.** Hỗn hợp tiền-huấn-luyện 262 h là giọng
  người lớn: IEMOCAP/MEAD/SAVEE/RAVDESS là cảm xúc **đóng diễn** bởi diễn viên người lớn; MSP-Podcast/
  CMU-MOSEI là podcast/YouTube người lớn; MELD là TV người lớn (*Friends*). **Không có giọng trẻ em ở
  đâu cả.** Giọng trẻ em khác về cao độ (f0 cao hơn nhiều), cấu trúc formant, prosody, và biểu đạt cảm
  xúc. Một backbone cảm xúc đóng-diễn-tiếng-Anh-người-lớn đóng băng có thể biểu diễn sai affect của trẻ.
  **Giảm thiểu:** coi emotion2vec *chỉ* là bộ trích đặc trưng và xác thực *probe* trên một lát child-voice
  giữ riêng trước mọi tuyên bố triển khai; dự trù một tập hiệu chuẩn child-voice nhỏ; cân nhắc một lượt
  continued distillation domain-adaptive nhẹ trên audio trẻ em nếu xuất hiện khoảng cách hiệu chuẩn (kết
  quả warm-start, Table 8, nói rằng việc này có đòn bẩy cao).
- **Đóng diễn so với distress tự phát.** Các số mạnh nhất (RAVDESS/SAVEE WA 82–84) là trên cảm xúc nguyên
  mẫu *đóng diễn*; distress thật của trẻ là tự phát, gián tiếp, thường arousal-thấp/thu mình. Kết quả MELD
  (nhiễu, tự phát, TV) thấp hơn nhiều (WA 51.88) — một proxy trung thực hơn cho độ khó ngoài thực tế.
  Pebble nên neo kỳ vọng vào con số kiểu MELD, không phải trần của tập đóng diễn.
- **Arousal ≠ severity với trẻ em.** emotion2vec tách *arousal*; nhưng một đứa trẻ trầm lặng, phẳng,
  thu mình có thể severity-cao ở arousal-thấp. Head severity không được đánh đồng "arousal cao" với
  "rủi ro cao" — tín hiệu severity audio là một *đóng góp*, không phải quyết định, nuôi cùng invariant
  human-escalation mà Pebble đã thực thi trên văn bản.
- **Rò rỉ danh tính người nói (chính tác giả nêu hạn chế).** Bài nói nó chưa bao giờ kiểm tra liệu thông
  tin người nói có bị loại khỏi biểu diễn. Với một sản phẩm **child-facing** đây là cờ đỏ riêng tư:
  đặc trưng emotion2vec có thể mang voiceprint/danh tính. **Giảm thiểu:** không bao giờ lưu audio thô hay
  embedding thô gắn với một đứa trẻ; chấm điểm on-device/tạm thời khi có thể; ghi điều này vào phần
  xử-lý-dữ-liệu.
- **Không có tuyên bố safety/lâm sàng.** emotion2vec là SER/sentiment, không phải phát hiện rủi ro. Nó có
  thể nuôi head *emotion* và *severity* của Pebble nhưng cung cấp **không tín hiệu safety học được** —
  nhất quán với quyết định không-head-safety-học-được của Pebble v1; phía audio cũng định tuyến qua
  heuristic + Decision Engine, không phải một bộ phân loại safety học được.

### Hạn chế & câu hỏi mở cho Pebble

- **Mâu thuẫn-hoặc-khoảng-trống so với kế hoạch turn-level, text-first của Pebble.** emotion2vec vận hành
  trên cả *phát ngôn* (utterance-level loss là một nửa mục tiêu) và được benchmark ở mức utterance/clip;
  Pebble chấm điểm **turn-level, giữa hội thoại**. Một voice message tự nhiên là một phát ngôn, nên
  utterance-level ổn cho phương thức audio — *nhưng* phía văn bản và audio khi đó vận hành ở granularity
  khác nhau (text = lượt trong hội thoại streaming; audio = cả clip). Pebble phải định nghĩa cách một
  điểm audio mức-utterance hợp nhất với các điểm text mức-turn trong Decision Engine; emotion2vec không
  hướng dẫn gì về căn chỉnh thời gian xuyên phương thức. **Khoảng trống.**
- **Khoảng trống so với phần còn lại của corpus: đây là bài giọng nói duy nhất.** Mọi bài tham chiếu Pebble
  khác (FAIIR, C-SSRS, MentalBERT, WASSA, GoEmotions) đều là **văn bản**. emotion2vec không so được trên
  cùng các bar (52% acc / 0.75 wF1 / 47.8% macro-recall của C-SSRS là bar severity văn bản; WA IEMOCAP
  71.79 của emotion2vec là SER đóng diễn 4 lớp). Hai phương thức không chia sẻ *bất kỳ* benchmark chung —
  Pebble phải xây eval child-voice+text liên hợp của riêng mình, hoặc giữ metric của hai phương thức tách
  biệt nghiêm ngặt.
- **Tiền-huấn-luyện trùng lặp downstream.** Bốn trong năm tập tiền-huấn-luyện (IEMOCAP, MELD, CMU-MOSEI,
  MEAD) cũng được đánh giá downstream; bằng chứng out-of-domain sạch nhất là RAVDESS/SAVEE và 9 ngôn ngữ.
  Pebble nên trọng số các con số OOD (và đặc biệt MELD nhiễu-tự-phát) khi ước lượng hiệu năng child-voice
  ngoài thực tế, không phải con số headline trong-miền.
- **emotion2vec+ tồn tại nhưng không có trong bài.** README GitHub thêm emotion2vec+ seed/base/large
  fine-tune trên 201/4788/42526 h — backbone tiềm năng mạnh hơn, nhưng không có số liệu peer-review.
  Câu hỏi mở: Pebble nên dùng checkpoint nào cho phương thức giọng nói (base cấp-bài-báo so với
  emotion2vec+ lớn hơn phát hành sau); cần một bake-off thực nghiệm trên lát child-voice của Pebble.
- **Không hiệu chuẩn / không đầu ra xác suất.** Giống FAIIR trên văn bản, emotion2vec báo cáo WA/UA/WF1
  không hiệu chuẩn (ECE/reliability). Decision Engine của Pebble tiêu thụ điểm số, nên các probe
  severity/emotion audio sẽ cần bước hiệu chuẩn riêng (D-G), điều emotion2vec không cung cấp.
- **Chưa chạy ablation thông tin người nói** — tác giả đánh dấu nó; với một sản phẩm trẻ em đây là điều
  đầu tiên Pebble phải đo trước khi ship audio.
