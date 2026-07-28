# Paper 03 — EAA: Emotion-Aware Audio LLMs with Dual Cross-Attention and Context-Aware Instruction Tuning

> Bản dịch tiếng Việt của [03-eaa-emotion-aware-audio-llm.md](03-eaa-emotion-aware-audio-llm.md) — cập nhật 2026-07-10.

- **Tác giả:** Hongfei Du, Sidi Lu, Gang Zhou, Ye Gao
- **Hội nghị / năm:** Interspeech 2025 (tr. 5433–5437)
- **Liên kết:** abs https://www.isca-archive.org/interspeech_2025/du25b_interspeech.html · PDF `pdfs/03-eaa-emotion-aware-audio-llm.pdf`
- **Nhóm:** audio+text (trục chính)

**Tóm tắt:** Cơ chế dual cross-attention hợp nhất luồng acoustic + semantic trong audio-LLM, tinh chỉnh theo chỉ dẫn (instruction tuning) có ngữ cảnh (context-aware); động lực nghiên cứu nêu rõ ứng dụng giám sát sức khỏe tâm thần (mental-health monitoring).

**Mức độ liên quan đến Pebble:** Đây là tham chiếu kiến trúc "sạch" nhất cho một fusion layer dùng cross-modal attention giữa audio và text.

> Mục ghi chép gọn (compact entry) từ đợt rà soát tài liệu (literature sweep) (`docs/tasks/bimodal-ser-papers.md`); chưa đọc sâu (deep-read).

## Phân tích (mức độ trùng lặp với Pebble)

### Phân tích — EAA (Emotion-Aware Audio LLM)
- **Hồ sơ sử dụng (voice-aware, tổng hợp ngày 2026-07-02):** luồng text (NeoBERT ~250M, nhãn silver từ teacher-LLM, gold-holdout, ordinal) **+ luồng voice đang hoạt động** (`voice-mtl-heads`: backbone SSL WavLM-Large/emotion2vec đóng băng (frozen) → 3 head không đồng nhất emotion/affect-CCC/crisis-recall-floor, trọng số hóa kiểu Kendall; hợp nhất voice+text là hướng đi tiếp theo).
- **Mức trùng lặp:** D1=0, D2=1, D3=1, D4=0, D5=0, D6=0, D7=2 → **19%** (ngoại vi / peripheral). Công thức: (3·0 + 2·1 + 1·1 + 2·0 + 2·0 + 2·0 + 1·2)/26 × 100 = 5/26 × 100 = 19.2% ≈ 19%. **Thay thế điểm 12% tính ngày 2026-07-02 dựa trên hồ sơ text-only đã lỗi thời** (mức tăng đến từ D7 0→2: HuBERT là một speech encoder SSL cùng lớp WavLM, khớp trực tiếp với họ backbone của luồng voice đang hoạt động).
- **Gần nhất ở:** D7 (backbone speech-encoder SSL đóng băng — HuBERT semantic + BEATs acoustic — cùng họ WavLM/emotion2vec mà luồng voice đang dùng) và D2/D3 (sức khỏe tâm thần được nêu như động lực; MELD là corpus cảm xúc hội thoại phân loại 7 lớp, trùng với head emotion của voice). Mọi thứ khác — các head multi-task không đồng nhất, head continuous/affect + safety, distillation nhãn silver từ LLM, cân bằng loss MTL có nguyên tắc, ràng buộc crisis recall — đều không có (EAA là SER phân loại đơn nhiệm/single-task).
- **Điểm hữu ích nhất (Bài học thiết kế):** Ablation về attention giải quyết câu hỏi về hướng fusion cho lộ trình voice+text — dual cross-attention hai chiều (0.687 acc) vượt qua cross-attention một chiều (semantic-as-query 0.610, acoustic-as-query 0.671) và self-attention thuần (0.675); *acoustic-as-query attend vào semantic key/value* là hướng một chiều mạnh hơn, và nhóm tác giả nối (concatenate) các đặc trưng gốc chưa fuse với đầu ra đã fuse để giữ lại thông tin đặc thù theo modality (Eq. 4).
  - **Cách áp dụng cho Pebble:** Đối với bước hợp nhất voice+text đã đề ra (sau khi `voice-mtl-heads` hoàn tất), hãy fuse các đặc trưng voice từ SSL đóng băng với luồng text NeoBERT bằng dual cross-attention hai chiều kèm residual concat giữa luồng gốc + luồng đã fuse — không phải concat/linear projection đơn giản — và mặc định chọn acoustic/voice-as-query nếu buộc phải chọn một hướng duy nhất. Đây là một lựa chọn thiết kế có liên quan trong ngắn hạn, vì giờ đây voice là một luồng đang hoạt động, không còn là ghi chú phụ text-only bị hoãn lại.
- **Lưu ý (Caveats):** Đã đọc toàn bộ PDF 5 trang, không bị paywall — điểm số có độ tin cậy cao. EAA là single-task (từ cảm xúc được sinh ra như output text của LLaMA-3-8B, dùng LoRA), nên D1/D4/D5/D6 thực sự bằng 0; "distillation" ở đây là một LLM sinh nhãn trực tiếp, không phải một teacher silvering dữ liệu cho một encoder nhỏ. Sức khỏe tâm thần chỉ là động lực; đánh giá thực hiện trên MELD (SER hội thoại phim truyền hình), không phải một corpus lâm sàng/khủng hoảng (clinical/crisis). Giá trị còn lại là một tham chiếu kiến trúc fusion cho lộ trình bimodal; việc fusion ở đây nằm bên trong audio (acoustic↔semantic), trong khi fusion của Pebble là voice↔text, nên cơ chế có thể chuyển giao được nhưng cặp modality lại khác nhau.

## Nghiên cứu sâu — đọc toàn bộ file PDF (2026-07-10)

> Được đọc lại và đối chiếu với **hồ sơ ViEmoSpeech hiện tại + Decision Register V-A…V-H**
> (`docs/tasks/paper-deep-analysis.md`), tài liệu này thay thế cho khối D-x
> (text-stream) đã lỗi thời trong định nghĩa deep-read agent **và** mục "Phân tích
> (mức độ trùng lặp với Pebble)" ở trên (hồ sơ voice-aware 2026-07-02). Mục này
> tác động đến **V-A** (mẫu kiến trúc fusion), **V-C** (nhánh text / cross-attention
> trên kênh LLM), và **V-F** (tính trung thực trong việc đóng khung
> distress/mental-health).

### Ghi chú về nguồn truy cập

- **Đã đọc toàn bộ PDF cục bộ (local)** qua lệnh `pdftotext "docs/papers/bimodal-ser/pdfs/03-eaa-emotion-aware-audio-llm.pdf" -`
  (phần phương pháp §3, cả ba bảng kết quả, ablation §4.3, tài liệu tham khảo). Bản PDF cục bộ
  **chính là phiên bản được xuất bản chính thức tại hội nghị** — chân trang kỷ yếu ISCA in
  `10.21437/Interspeech.2025-1232`, trang 5433–5437, và DOI phân giải được. Không có
  chênh lệch nào so với một bản preprint riêng cần đối chiếu.
- **Đã xác thực trên web (web-validated)** đối chiếu với trang landing của ISCA archive: tác giả (Du, Lu, Zhou,
  Gao, William & Mary), hội nghị (Interspeech 2025, Rotterdam), trang 5433–5437, tuyên bố
  chính **"cải thiện accuracy 11.4%"**, và câu trong abstract nêu
  **"mental health monitoring"** là động lực nghiên cứu.
  - Truy vấn: `EAA Emotion-Aware Audio Large Language Models Dual Cross-Attention Context-Aware Instruction Tuning Interspeech 2025 MELD 68.7%`
  - URL đã phân giải: https://www.isca-archive.org/interspeech_2025/du25b_interspeech.html
    (+ bản PDF mirror https://www.isca-archive.org/interspeech_2025/du25b_interspeech.pdf)
- **Nhãn trạng thái (status tags):** Các số liệu Table 1 / Table 2 / Table 3 nằm trong phần
  text trích xuất được → ✔ đã kiểm chứng. **Figure 2** (so sánh cơ chế attention) là biểu đồ
  cột; giá trị của từng cột **không** xuất hiện trong phần text trích xuất được — các con số
  0.610 / 0.671 / 0.675 trích dẫn trong khối "Phân tích" cũ ở trên là đọc trực tiếp từ biểu đồ
  → gắn nhãn ≈ ước lượng ở đây.

### Bài báo thực sự làm gì

**Nhiệm vụ (Task).** Speech-emotion recognition phân loại, đơn nhiệm (single-task), được đóng khung
như *sinh text*: một audio-LLM phát ra một từ cảm xúc duy nhất. Được đánh giá trên **MELD**
(hội thoại phim sitcom Friends; 7 lớp neutral/joy/sadness/anger/fear/disgust/surprise;
13,847 utterance, 407 người nói, 12.2 giờ tiếng Anh; §4.1) chỉ dùng **accuracy**.

**Kiến trúc (§3, Fig. 1).** Hai audio encoder gần như đóng băng (frozen-ish) đưa vào một
khối fusion *dual cross-attention*; đầu ra của khối này cùng với một instruction dạng text và
một dòng ngữ cảnh hội thoại được đưa vào một LLaMA-3-8B đã tinh chỉnh bằng LoRA để sinh ra
từ cảm xúc.
- Semantic encoder `f_s` = **HuBERT**; acoustic encoder `f_a` = **BEATs**
  (Eq. 1: `S = f_s(x) ∈ R^{Ts×ds}`, `A = f_a(x) ∈ R^{Ta×da}`). Cả hai encoder đều
  **đóng băng, trừ hai layer cuối** được fine-tune (§4). Lưu ý cả hai nhánh đều được
  suy ra từ **cùng một tín hiệu audio** — "semantic" ở đây nghĩa là các đặc trưng SSL
  mang tính ngôn ngữ (linguistic-ish) của HuBERT, **không phải** một embedding text/LLM.
- Linear projection về một chiều `d` dùng chung + LayerNorm (Eq. 2); các sequence được
  căn chỉnh bằng cách **zero-pad chuỗi ngắn hơn tới `T = max(Ts, Ta)`** để attention được
  căn chỉnh theo thời gian.
- **Dual cross-attention (Eq. 3):** `Att_s = Softmax(Q_s K_a^T / √d) V_a` (semantic
  query vào acoustic) và `Att_a = Softmax(Q_a K_s^T / √d) V_s` (acoustic query vào
  semantic).
- **Residual concat fusion (Eq. 4):** `F = Concat(S̃, Ã, Att_s, Att_a)` — các
  projection gốc chưa fuse được giữ lại song song với hai luồng đã qua attention,
  sau đó được project vào không gian hidden của LLaMA.
- **Context-aware instruction tuning (§3.2):** với utterance `x_t`, thêm vào phía trước
  utterance ngay trước nó `x_{t-1}` trong cùng hội thoại (`C_t = x_{t-1} ⊕ x_t`,
  Eq. 5); prompt = *"Describe the speaker's emotion in one word."*
- **Cấu hình tuning (§4):** LoRA rank 2, α 16, dropout 0.2, batch 2, hidden 768,
  AdamW lr 5e-6, linear warm-up → cosine decay, một H100 duy nhất, audio mono 16 kHz.

**Kết quả chính.**
- **Accuracy của EAA trên MELD = 0.687** (Table 1) ✔ đã kiểm chứng. Vượt qua mọi
  ALLM được liệt kê: BLSP-Emo 0.573, OSUM 0.566, Qwen-audio 0.557, AffectGPT 0.557,
  Qwen2-audio 0.553, WavLM-large 0.542, WavLLM 0.411, Whisper+Llama3 0.334,
  SALMONN 0.331, MERaLiON 0.302, Pengi 0.289 (Table 1) ✔. Tuyên bố **"11.4%"**
  = 0.687 − 0.573 (so với BLSP-Emo, ALLM hỗ trợ emotion mạnh nhất) ✔ đã được kiểm
  chứng qua abstract + trang hội nghị.
- **Các phương pháp ERC multimodal truyền thống (Table 2)** nằm ở mức 0.651–0.687; EAA
  (audio+text) hòa với mức tốt nhất, **ELR-GNN 0.687, vốn còn dùng thêm cả video** ✔. EAA
  thu hẹp khoảng cách ALLM-so-với-classifier chứ không vượt qua các classifier SOTA.
- **Ablation về context (Table 3):** chỉ audio (không có text nào) **0.523** → text của
  utterance hiện tại **0.667** → hiện tại + câu trước đó **0.687** ✔. Bước nhảy lớn nhất
  đến từ việc thêm *bất kỳ* text context nào (+14.4 điểm phần trăm); câu trước đó chỉ thêm
  +2.0 điểm phần trăm.
- **Ablation về attention (Fig. 2):** dual cross-attention **0.687** > self-attention
  **≈0.675** > acoustic-as-query một chiều **≈0.671** > semantic-as-query một chiều
  **≈0.610** ≈ ước lượng (chỉ có trong biểu đồ). Kết luận của nhóm tác giả: acoustic-as-query
  là hướng một chiều mạnh hơn; dual vượt qua cả hai hướng một chiều lẫn self-attention.

### Các phần hữu ích trực tiếp cho ViEmoSpeech (mỗi phần gắn Decision ID)

1. **Khối fusion dual cross-attention + residual-concat (Eq. 3–4)** — một *template*
   sạch, có thể trích dẫn cho V-A. Hai luồng đã project, LayerNorm, cross-attention hai
   chiều (mỗi modality query modality kia), sau đó **concat luồng gốc + cả hai luồng đã
   qua attention** để không có gì bị collapse. **[V-A]**
2. **Acoustic-as-query là hướng một chiều mạnh hơn; dual là tốt nhất (Fig. 2).**
   Một prior cụ thể về hướng fusion: nếu buộc phải chọn, hãy để audio query text; nhưng
   tốt hơn là chạy cả hai. **[V-A]**
3. **Công thức frozen backbone + mở khóa 2 layer cuối + LoRA-on-LLM (§4).** Train
   được một stack audio-LLM lớn trên 12.2 giờ dữ liệu với ngân sách một GPU H100 duy
   nhất, nhờ đóng băng phần lớn mô hình. Hỗ trợ trực tiếp cho thiên hướng frozen-backbone
   của V-B và một ngân sách unfreeze nhẹ. **[V-B]**
4. **Ablation về context lượng hóa giá trị của kênh text (Table 3):** đi từ audio-only
   0.523 lên +text 0.667 là +14.4 điểm phần trăm — đòn bẩy đơn lẻ lớn nhất trong toàn bộ
   bài báo. Đây là bằng chứng định lượng bên ngoài cho thấy nhánh semantic/text mang tải
   nặng, đúng với luận điểm tone×emotion của ViEmoSpeech (text phải gánh nhiều hơn vì F0
   đã bị tone chiếm dụng). **[V-C, V-D]**
5. **Chỉ báo cáo accuracy trên MELD vốn mất cân bằng lớp (class-imbalanced)** — một
   *template tiêu cực*: MELD thiên nặng về lớp neutral, và accuracy che giấu sự sụp đổ
   của các lớp thiểu số. ViEmoSpeech phải báo cáo macro-F1 (+ CCC cho V/A, recall@floor).
   **[V-G]**
6. **"Mental health monitoring" được nêu tên trong abstract+intro nhưng chưa bao giờ
   được vận hành hóa (operationalized)** — đánh giá là 100% cảm xúc phim sitcom, không có
   nhãn clinical/distress nào. Chất liệu trực tiếp cho cách đóng khung honest-proxy của
   V-F (xem lăng kính bên dưới). **[V-F]**

### Mỗi phần giúp ViEmoSpeech thành công như thế nào

- **V-A (khối fusion).** Áp dụng Eq. 3–4 như một nhánh learned-fusion ứng viên trong
  fusion bake-off của method paper (đối trọng với nỗ lực rule-based PhoWhisper+PhoBERT
  trước đó và nhánh vn-07 FAS Q-Former): hai luồng frozen → project → LN → cross-attention
  hai chiều → **concat(gốc, Att_s, Att_a)**. Residual concat là chi tiết mang tính then
  chốt — đây là cơ chế tự bảo vệ của EAA trước việc một modality bị collapse, và nó trả
  lời trực tiếp mối lo "fusion collapse về phía text encoder mạnh" của vn-12. Mặc định
  *phương án dự phòng một chiều* là **acoustic-as-query**.
- **V-A (căn chỉnh/alignment).** Thủ thuật zero-pad-tới-`T=max(Ts,Ta)` của EAA là công
  thức sai cho trường hợp của chúng ta (xem rủi ro bên dưới) — với audio↔ASR-text hãy dùng
  **cross-attention không ép căn chỉnh theo thời gian** (text token làm K/V, audio frame
  làm Q, không padding), vì không có sự tương ứng thời gian frame-với-token. Trích dẫn EAA
  cho *hình dạng của khối (block shape)*, không phải cho bước alignment.
- **V-B (ngân sách).** Sao chép pattern freeze-tất-trừ-2-layer-cuối + LoRA để backbone
  WavLM / emotion2vec giữ nguyên trạng thái đóng băng và chỉ một fusion head mỏng + một
  phần unfreeze nhẹ được train trên corpus P1 ~18k utterance của chúng ta — một corpus
  nhỏ hơn nhiều so với mức mà một stack dual-encoder fine-tune toàn phần cần đến.
- **V-C (nhánh text).** Mức +14.4 điểm phần trăm của Table 3 khi thêm text là bằng
  chứng trích dẫn cho thấy nhánh semantic không phải là tùy chọn trong dialogue SER —
  điều này tạo động lực đầu tư vào một nhánh PhoBERT/ViSoBERT vững chắc thay vì một mô
  hình chỉ dùng audio. Nhưng vì nhánh "semantic" của EAA thực chất là HuBERT (audio),
  **bản thân EAA không kiểm chứng cross-attention trên một kênh text/LLM thật sự** —
  thiết kế của chúng ta làm một điều mà EAA không làm, nên hãy trích dẫn nó như động lực
  cho nhánh text, chứ không phải như một kết quả text-cross-attention đã được chứng minh.
- **V-D.** Dùng ablation về context của EAA như thêm một điểm dữ liệu bên ngoài cho
  thấy kênh phi-F0/phi-acoustic (linguistic) mang tải cảm xúc đáng kể trong hội thoại —
  nhất quán với (chứ không phải bằng chứng cho) luận điểm cạnh tranh kênh tone×emotion
  của chúng ta.
- **V-F.** Nêu tên EAA trong method paper cùng với vn-10 (Dynamic-CBAM) như một
  pattern "mental-health-trong-abstract, sitcom-emotion-trong-eval" mà cách đóng khung
  acted-drama-distress-proxy của chúng ta chủ động từ chối lặp lại.
- **V-G.** Báo cáo macro-F1 (không phải accuracy) để một corpus thiên nặng về lớp
  neutral không thể thổi phồng con số headline theo cách mà accuracy trên MELD có thể.

### Lăng kính sức khỏe tâm thần trẻ em / distress (tính khả chuyển đối với ViEmoSpeech)

- **"Sức khỏe tâm thần" chỉ là động lực, và thậm chí còn yếu hơn một distress proxy.**
  Cụm từ "mental health monitoring" xuất hiện đúng một lần trong abstract và intro, như
  một trong ba ô ứng dụng (HCI / sức khỏe tâm thần / dịch vụ khách hàng, §1 refs [1–3]);
  không có **nhãn distress, không có mỏ neo lâm sàng, không có chiều affect/valence** nào
  ở bất kỳ đâu trong phần method hay eval. Toàn bộ phần đánh giá là MELD — hội thoại phim
  sitcom Mỹ (*Friends*) đóng theo kịch bản, 7 cảm xúc phân loại. Với V-F, đây là anti-pattern
  sạch sẽ: một bài báo có thể viện dẫn sức khỏe tâm thần để tăng tính nổi bật trong khi
  tuyên bố có thể đo lường được của nó chỉ là SER phân loại thông thường. Vì vậy, cờ distress
  của ViEmoSpeech phải được đóng khung như một **proxy kịch bản diễn (acted-drama) với mục
  tiêu recall-floor**, rõ ràng không phải một construct lâm sàng — và EAA chính là trích dẫn
  cho lý do vì sao sự trung thực đó là cần thiết.
- **Đóng theo kịch bản, tiếng Anh, phi thanh điệu — phần lớn rủi ro chuyển giao nằm
  ở cặp modality, không phải ở register.** MELD đóng theo kịch bản (giống nguồn TV-drama
  của chúng ta, nên register acted-proxy là một phép loại suy *công bằng*), nhưng (a)
  tiếng Anh & phi thanh điệu → không có gì về tone×emotion hay phonation tiếng Việt có thể
  chuyển giao; (b) fusion ở đây là **nội-audio (intra-audio)** (HuBERT-semantic ↔
  BEATs-acoustic, cả hai đều từ cùng một waveform), trong khi của chúng ta là
  **liên-nguồn (cross-source)** (audio WavLM ↔ PhoBERT trên ASR PhoWhisper nhiễu). EAA
  chưa bao giờ đối mặt với nhiễu ASR hay lỗi tone-swap (mày→máy). Cơ chế có thể chuyển
  giao; nhưng chế độ input thì không.
- **Frozen backbone là một lợi thế cho bối cảnh child/proxy**, nơi nhãn khan hiếm và
  chúng ta không thể mạo hiểm để một stack lớn overfit trên một corpus đóng theo kịch bản
  nhỏ — EAA cho thấy một kết quả cạnh tranh vẫn có thể đạt được khi phần lớn mô hình được
  đóng băng.
- **Ghi chú về đạo đức (Ethics note).** EAA không đưa ra tuyên bố nào về consent/quản trị
  dữ liệu (MELD là một corpus học thuật công khai). Đây không phải một template về quản trị
  dữ liệu — ràng buộc về tính hợp pháp media của chúng ta (chỉ features+timestamps+labels)
  không có phép loại suy tương ứng ở đây.

### Hạn chế & câu hỏi mở cho ViEmoSpeech (mâu thuẫn/khoảng trống)

- **GAP so với V-C / khối "Phân tích" cũ — cross-attention của EAA nằm trên kênh
  audio, không phải kênh text/LLM.** Mục ghi chép gọn ở trên quảng bá EAA là "tham chiếu
  sạch nhất cho một fusion layer dùng cross-modal attention giữa audio và text." Đọc kỹ
  phần method thì cross-attention chạy giữa **HuBERT và BEATs — hai audio encoder**;
  *text* duy nhất trong hệ thống là prompt LLaMA + context của utterance trước đó, và
  phần này **không** được cross-attend, mà chỉ được concatenate vào input của LLM. Vì
  vậy, đối với V-C (cross-attention *trên kênh text/LLM*), EAA là **một template yếu
  hơn so với những gì được nêu**: nó chứng minh khối kiến trúc, chứ không phải ứng dụng
  audio↔text. Đây là mâu thuẫn/khoảng trống (≥1) bắt buộc phải nêu.
- **MÂU THUẪN so với V-F / song song với vn-10:** EAA lặp lại nước đi của Dynamic-CBAM
  — viện dẫn một ứng dụng lâm sàng, đánh giá trên cảm xúc phân loại đóng theo kịch bản —
  nhưng còn đi xa hơn (hoàn toàn không có head distress/affect nào). Cả hai đều là
  anti-pattern mà spec distress-head của chúng ta nên nêu tên.
- **Zero-pad temporal alignment (§3.1) không hợp lý cho audio↔ASR-text.** EAA có thể
  pad tới `T=max(Ts,Ta)` vì cả hai luồng đều là audio được đánh chỉ số thời gian ở 16 kHz;
  các subword token của PhoBERT không có sự tương ứng frame-time với frame của WavLM, và
  ép một sự tương ứng như vậy sẽ tạo ra alignment giả. Câu hỏi mở: thay bằng cross-attention
  không phụ thuộc độ dài (length-agnostic) (text làm K/V, không padding) và đo xem lợi ích
  của residual-concat (Eq. 4) có còn tồn tại khi không có temporal alignment hay không.
- **Chỉ báo cáo accuracy trên MELD mất cân bằng che giấu sự sụp đổ ở lớp thiểu số** —
  cùng một red flag như vn-07 FAS (0 câu fear/disgust đúng) và tình trạng lớp neutral
  chiếm ưu thế đã biết của MELD. EAA không cho chúng ta số liệu per-class hay macro nào,
  nên con số 0.687 của nó **không phải** một mốc so sánh được cho protocol macro-F1
  speaker-disjoint của chúng ta (V-G). Cũng cần lưu ý EAA **không đưa ra tuyên bố nào về
  speaker-disjoint** — split chuẩn của MELD được dùng nhưng việc chồng lấn người nói giữa
  các split của MELD là một vấn đề đã biết, nên 0.687 có thể bị ảnh hưởng bởi rò rỉ dữ liệu
  (leak) (không thể kiểm chứng được từ bài báo).
- **Kiểm tra tính nhất quán so với vn-12 (semantics chiếm ưu thế / SLM collapse về
  phía text).** Kết quả acoustic-as-query > semantic-as-query của EAA (Fig. 2, ≈0.671
  so với ≈0.610) là *bằng chứng nhẹ cho việc neo vào audio (audio-anchoring)* và do đó
  nhất quán với cơ chế bảo vệ mà vn-12 đề xuất (head audio-only phụ / modality dropout)
  — nhưng bước nhảy +14.4 điểm phần trăm của text ở Table 3 cho thấy kênh text vẫn mang
  phần lớn mức tăng trên MELD. Kết luận chung: cứ fuse, nhưng regularize nhánh text và
  giữ lại một điểm neo audio — đây là kết luận chung mà cả hai bài báo đều đẩy chúng ta
  hướng tới, trên một corpus (MELD) có audio tiếng Anh, phi thanh điệu, yếu.
