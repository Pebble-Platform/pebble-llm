# Paper vn-07 — When Tone and Words Disagree: Robust SER under Acoustic-Semantic Conflict (CASE / FAS)

> Bản dịch tiếng Việt của [07-case-tone-words-disagree.md](07-case-tone-words-disagree.md) — cập nhật 2026-07-10.

- **Authors:** (chưa trích xuất — cần đối chiếu lại từ PDF)
- **Venue / year:** arXiv preprint, tháng 1/2026
- **Links:** abs https://arxiv.org/abs/2601.04564 · PDF `pdfs/07-case-tone-words-disagree.pdf`
- **Group:** vietnamese-ser / đối thủ kiến trúc gần nhất

**Summary:** Giới thiệu CASE, một bộ dữ liệu tập trung vào các trường hợp mà tone-of-voice
paralinguistic mâu thuẫn với nội dung từ vựng/ngữ nghĩa, cùng mô hình Fusion
Acoustic-Semantic (FAS) tách rời hai luồng acoustic và semantic thông qua cơ chế
query-based attention; vượt qua các baseline dựa trên ASR/SSL/audio-LLM (59.38% trên CASE).

**Relevance to ViEmoSpeech:** Đối thủ kiến trúc gần nhất — bắt buộc phải trích dẫn và
phân biệt rõ: "tone" của họ là tone-of-voice paralinguistic, KHÔNG PHẢI thanh điệu từ
vựng (phonemic lexical tone) trong một ngôn ngữ có thanh điệu. Đồng thời là một mẫu
fusion tiềm năng (V-A).

> Stub created 2026-07-10 (task `docs/tasks/paper-deep-analysis.md`); deep-read pending.

## Deep research — đọc toàn văn PDF (2026-07-10)

### Ghi chú về nguồn truy cập

Đã đọc toàn văn PDF cục bộ qua `pdftotext "docs/papers/vietnamese-ser/pdfs/07-case-tone-words-disagree.pdf" -`
(toàn bộ phần thân bài + các Bảng 1–7, các thí nghiệm ablation, phụ lục nghiên cứu tình
huống và phần thảo luận confusion-matrix). PDF là `arXiv:2601.04564v1 [cs.SD], 8 Jan 2026` —
một preprint rất mới **chưa có phiên bản xuất bản/venue chính thức**, nên bản arXiv v1 là
nguồn có thẩm quyền (không có gì cần đối chiếu thêm). Đã kiểm chứng trên web các sự kiện
mang tính chịu tải (load-bearing) so với abstract/HTML của arXiv:
- Truy vấn `"When Tone and Words Disagree" FAS CASE ... arXiv 2601.04564` → dẫn tới
  https://arxiv.org/abs/2601.04564 và https://arxiv.org/pdf/2601.04564 — xác nhận tiêu đề,
  khung FAS/CASE, và con số **59.38% CASE SOTA** đầu bài; GitHub `github.com/24DavidHuang/FAS`.
- Đã fetch https://arxiv.org/html/2601.04564v1 → xác nhận **các ngôn ngữ trong CASE = "tiếng
  Anh, tiếng Quan thoại (Mandarin), và các phương ngữ Trung Quốc tiêu biểu"**; **"tone" =
  tone-of-voice/prosody paralinguistic, không phải thanh điệu phonemic/từ vựng**; công cụ
  TTS = Doubao-Seed-TTS 2.0; 378 mẫu; 7 cảm xúc; siêu tham số tốt nhất
  `k_aco=8, k_sem=16, N_q=2, d=512`. (Đây là dữ kiện bảo vệ tính mới V-D.)

Danh sách đầy đủ tác giả (stub trước đó còn thiếu): **Dawei Huang(1,2), Yongjie Lv(1), Ruijie
Xiong(1), Chunxiang Jin(1), Xiaojiang Peng(2)\*** — (1) Inclusion AI, Ant Group; (2) Shenzhen
University; \*tác giả liên hệ (Xiaojiang Peng). ✔ đã kiểm chứng (author block trên arXiv).

### Nội dung thực tế của bài báo

**Vấn đề.** SER tiêu chuẩn giả định sự *tương hợp* (congruence) acoustic–semantic (một câu vui
được nói bằng giọng vui). Bài báo nhắm vào các trường hợp *xung đột* (conflict) — mỉa mai
(sarcasm), giận dữ kìm nén (cold fury), che giấu bằng phép lịch sự (polite masking) — nơi
prosody mâu thuẫn với lời nói theo nghĩa đen, và cho thấy các SER SOTA (SSL, semantic encoder
dựa trên ASR, và audio-LLM) đều suy giảm mạnh vì chúng hoặc mang thiên kiến semantic, hoặc có
đặc trưng acoustic⊗semantic đan xen (entangled).

**Framework FAS** (§3.1, Hình 1) — hai luồng đóng băng (frozen pathway) + một đầu fusion học
được nhẹ, huấn luyện trên các đặc trưng *đã tính sẵn* (pre-computed) (các encoder không bao giờ
được fine-tune):
- Luồng semantic = **Whisper-large encoder**, đặc trưng 1280 chiều. Luồng acoustic =
  **MingTok-Audio** (một bộ tokenizer âm thanh neural, dẫn xuất từ TTS codec), đặc trưng 64
  chiều. ✔ (§4.2)
- **Patchify** từng luồng theo hệ số downsample `s=5`, chiếu (project) về không gian chung
  `d=512` (Eq. 1). ✔
- **Token distillation** (Eq. 2–3): điểm saliency `s_t = ||f_t||_2` (chuẩn L2 dùng làm proxy
  năng lượng); **Top-K** giữ lại các token nổi bật nhất mỗi luồng, với ngân sách bất đối xứng
  `k_aco`, `k_sem`. ✔
- **Learnable queries** `Q_learn ∈ R^{n×d}` (kiểu Q-Former) cross-attend vào ngữ cảnh đã distill
  được nối lại: `F_fused = Attn(Q_learn, C·W_K, C·W_V)` (Eq. 4) → MLP → softmax 7 lớp. ✔ (§3.1)
- Cấu hình (Bảng 3): `d=512`, `N_q=2`, dropout 0.4, AdamW, LR `2e-4`, cosine schedule, weight
  decay `1e-4`, global batch 2048, hàm mất mát CE, 100 epoch, warmup 0.05, 16 kHz, seed 42,
  8×A6000. ✔
- Số lượng tham số: **FAS 3.45M** (so với Concat 1.22M, Gated 1.65M, w/o-Qlearn 0.82M). ✔ (Bảng 4)

**Bộ chuẩn CASE** (§3.2, Hình 2). Một testbed *chẩn đoán* (diagnostic) zero-shot gồm **378**
câu nói xung đột đã được con người kiểm chứng, 7 cảm xúc. Được xây dựng như sau: Gemini-2.5-pro
soạn kịch bản xung đột + một đoạn văn bản mang cảm xúc (semantic anchor); một **cảm xúc acoustic
ground-truth được chọn có chủ đích để mâu thuẫn** với cảm xúc semantic của văn bản; một chất
giọng (timbre) được lấy từ **21 giọng đa cảm xúc**; **Doubao-Seed-TTS 2.0** tổng hợp âm thanh;
**12 người chú thích chuyên gia** loại bỏ các mẫu có prosody acoustic yếu/mơ hồ/bị lấn át. Hoàn
toàn **tổng hợp (synthetic), không có PII** (mục Ethics). Các câu gốc là **tiếng Trung**
(Bảng 7 phụ lục liệt kê phần dịch nghĩa tiếng Anh); phạm vi ngôn ngữ = tiếng Anh + Quan thoại
+ các phương ngữ Trung Quốc. ✔ (§3.2, Limitations, Appendix A.3)

**Corpus huấn luyện** = ~66 giờ tổng hợp từ các bộ SER mở: IEMOCAP, CMU-MOSEI, MER2024, MELD,
RAVDESS, ESD (Bảng 1). Test trong miền (in-domain) = MELD/RAVDESS/ESD; zero-shot = CASE,
Emo-Emilia (tiếng Quan thoại), EMOVO (tiếng Ý), EmoDB (tiếng Đức). ✔

**Kết quả đầu bài** (Bảng 2, ACC/F1):

| Model (paradigm) | CASE (zero-shot) | MELD | RAVDESS | ESD |
|---|---|---|---|---|
| Whisper (semantic) | 47.26 / 44.97 | 49.59 / 43.62 | 62.30 / 60.61 | 84.53 / 83.92 |
| WavLM (SSL) | 34.20 / 33.92 | 52.99 / 53.57 | 44.64 / 34.09 | 61.90 / 60.69 |
| Emotion2Vec (SOTA SER) | 31.48 / 28.42 | 45.04 / 45.49 | 70.06 / 68.84 | 51.39 / 50.87 |
| Qwen2.5-Omni (ALM) | 34.66 / 30.21 | 54.06 / 36.05 | 75.35 / 74.98 | 51.60 / 35.70 |
| **FAS (Ours)** | **59.38 / 55.08** | 51.89 / 48.42 | 76.61 / 76.19 | 87.27 / 86.72 |

Tất cả ✔ (Bảng 2). ACC trung bình in-domain **71.92%**; ACC trung bình zero-shot **54.66%**. ✔
Lưu ý rằng semantic encoder (Whisper, 47.26) là *baseline mạnh nhất trên CASE* — ngay cả trên
dữ liệu "xung đột", một mô hình thiên về semantic vẫn vượt qua SSL/ALM; mức tăng +12 điểm của
FAS so với Whisper mới là luận điểm thực sự.

**Ablations.** (a) Chiến lược fusion trên ACC của CASE (Bảng 4): Concat 53.65 < Gated 53.12 <
w/o-Top-K 55.47 < w/o-Qlearn 55.99 < **FAS 59.38**; bỏ Top-K làm mất −3.91 ACC trên CASE, bỏ
Qlearn làm mất **−9.27 ACC trên RAVDESS**. ✔ (b) Ngân sách token (Bảng 5): trung bình tốt nhất
62.06% ACC tại `k_aco=8, k_sem=16` — **bất đối xứng, nhiều token semantic hơn acoustic là tốt
hơn**; tăng `k_aco` cho lợi ích không đáng kể hoặc âm. ✔ (c) `N_q` bão hòa ở **2** (Hình 4);
"SER là một tác vụ độ phức tạp thấp ở cấp độ câu nói (utterance-level), năng lực query tối
thiểu là đủ." ✔ (d) Khả năng cắm-và-chạy (plug-and-play) qua các encoder khác nhau (Bảng 6):
MingTok+Whisper tốt nhất trên CASE; Whisper+XCodec2 tốt nhất trên MELD; Whisper+VibeVoice tốt
nhất trên RAVDESS; CLAP dùng làm nhánh semantic thì kém hơn Whisper. ✔ (e) Ma trận nhầm lẫn
(Phụ lục A.2.3): **"không phương pháp nào dự đoán đúng bất kỳ mẫu nào thuộc lớp fear hoặc
disgust" trên CASE** — các lớp hiếm/xung đột cao sụp đổ hoàn toàn ngay cả với mô hình SOTA. ✔

### Các phần có thể áp dụng trực tiếp cho ViEmoSpeech (gắn thẻ theo Decision ID)

1. **[V-D — dữ kiện bảo vệ tính mới CỐT LÕI]** "Tone" của CASE là **tone-of-voice
   paralinguistic (prosody)**, tường minh *không phải* thanh điệu phonemic/từ vựng; các ngôn
   ngữ là tiếng Anh + Quan thoại + các phương ngữ Trung Quốc, và mặc dù tiếng Quan thoại có
   thanh điệu, bài báo **không hề nghiên cứu sự cạnh tranh kênh giữa thanh điệu từ vựng và cảm
   xúc** — xung đột của nó là prosody-đối-nghịch-semantic (mỉa mai/che giấu) trong giọng nói
   **TTS tổng hợp**. ✔
   *Rủi ro chuyển giao: không có — đây là một trích dẫn, không phải một phương pháp để tái sử
   dụng.* Đây chính là sự trích dẫn-và-phân biệt sạch sẽ: luận điểm đầu bài của ViEmoSpeech
   (thanh điệu từ vựng tiếng Việt nặng về phonation và chia sẻ kênh F0/phonation mà cảm xúc sử
   dụng) **không hề bị đụng chạm** bởi CASE. CASE là đối thủ cùng tên gần nhất nhưng lại hoạt
   động trong một không gian bài toán trực giao (orthogonal); luận điểm về tính mới của
   ViEmoSpeech vẫn còn nguyên vẹn.

2. **[V-A — mẫu kiến trúc fusion]** Đầu FAS hai luồng + Q-Former distillation: encoder đóng
   băng, đặc trưng tính sẵn, `d=512`, chọn token Top-K bằng saliency L2 với **ngân sách bất đối
   xứng** (`k_sem=16 > k_aco=8`), `N_q=2` learnable query, 3.45M tham số huấn luyện, hàm mất mát
   CE.
   *Rủi ro chuyển giao: TRUNG BÌNH-CAO.* **Hình dạng** (fusion học được rẻ trên hai luồng đóng
   băng) chuyển giao được và trả lời trực tiếp cho V-A ("vượt qua baseline rule-based
   PhoWhisper+PhoBERT"). Nhưng có hai thành phần **không** chuyển giao nguyên trạng: (i)
   MingTok-Audio là một **codec TTS cho tiếng Quan thoại/Anh** — không có bằng chứng nó
   tokenize *phonation/thanh điệu* tiếng Việt một cách sạch sẽ; các ứng viên V-B của
   ViEmoSpeech (WavLM / emotion2vec / đặc trưng phonation) mới là luồng acoustic tự nhiên.
   (ii) Luồng semantic của FAS là **đặc trưng Whisper-encoder**, không phải một text-LM chạy
   trên bản chép ASR — nhánh text của ViEmoSpeech là PhoBERT/ViSoBERT trên **bản chép
   PhoWhisper** (V-C), nên "luồng semantic" là một đối tượng khác.

3. **[V-A / V-B — phát hiện về ngân sách bất đối xứng + saliency]** "Giữ lại nhiều token
   *semantic* hơn có lợi hơn giữ lại nhiều token acoustic hơn" (Bảng 5, `k_sem=16>k_aco=8`), và
   saliency chuẩn L2 (proxy năng lượng) vượt qua lựa chọn token ngẫu nhiên/đồng đều tới 3.91
   ACC. ✔
   *Rủi ro chuyển giao: TRUNG BÌNH và đáng chú ý về mặt định hướng.* Đây là bằng chứng thực
   nghiệm rằng, ngay cả với một tác vụ được đóng khung xoay quanh xung đột *acoustic*, luồng
   semantic vẫn nên mang nhiều năng lực hơn — điều này **cộng hưởng** với chính luận điểm của
   ViEmoSpeech rằng trong một ngôn ngữ có thanh điệu, nhánh text/semantic "phải gánh tải nhiều
   hơn". Nhưng ngữ nghĩa của CASE thì sạch (văn bản ground-truth → Whisper); dưới nhiễu tone-swap
   của PhoWhisper, luồng semantic của ViEmoSpeech bị *nhiễu bẩn chính xác ở mức arousal cao*,
   nên khuyến nghị "nhiều token semantic hơn" có thể bị đảo ngược. Đáng làm một ablation tường
   minh, không phải sao chép trực tiếp.

4. **[V-G — thiết kế đánh giá trường hợp xung đột]** Quy trình xây dựng CASE: chủ đích thiết
   kế một cảm xúc acoustic ground-truth **mâu thuẫn** với cảm xúc semantic của văn bản, sau đó
   **loại bỏ bất kỳ mẫu nào có cảm xúc acoustic không cảm nhận rõ ràng** (cơ chế lọc bởi 12
   chuyên gia). Được báo cáo như một *lát cắt chẩn đoán zero-shot*, tách riêng khỏi các chỉ số
   in-domain; cả ACC và unweighted-avg F1 đều được báo cáo. ✔ *Rủi ro chuyển giao: THẤP với tư
   cách một mẫu thiết kế, nhưng bản thân bộ dữ liệu CASE thì không chuyển giao được* (tổng hợp
   tiếng Trung/Anh, không có tiếng Việt, không có ASR). Ý tưởng có thể tái sử dụng là một
   **lát cắt phụ về xung đột được giữ riêng (held-out)** với dòng chỉ số riêng của nó.

### Cách mỗi phần giúp ViEmoSpeech thành công

- **V-D → đoạn văn định vị của bài báo tự viết ra chính nó.** Trong bài báo phương pháp
  ViEmoSpeech, trích dẫn CASE như trạng thái nghệ thuật (state of the art) về xung đột
  acoustic-semantic *paralinguistic* và phân biệt trong một câu: "Khác với CASE, nơi 'tone' là
  tone-of-voice mang tính prosody trên giọng nói tiếng Anh/Quan thoại tổng hợp, ViEmoSpeech
  nghiên cứu **sự cạnh tranh kênh giữa thanh điệu từ vựng phonemic và cảm xúc** trong giọng nói
  tự nhiên của phim truyền hình Việt Nam." Sản phẩm cụ thể: đoạn Related-Work / tính mới và
  bảng đối thủ cạnh tranh tại `docs/project-overview.md §1.3`. Điều này khép lại phản đối lớn
  nhất từ reviewer ("đây chẳng phải chỉ là CASE thôi sao?") bằng một sự phân biệt thực tế, có
  thể kiểm chứng.

- **V-A → một baseline fusion cụ thể để xây dựng và vượt qua.** Triển khai FAS-lite như một
  nhánh trong đợt so sánh (bake-off) fusion: hai luồng đóng băng (thay MingTok→WavLM/emotion2vec
  cho luồng acoustic tiếng Việt; thay Whisper→PhoBERT-trên-PhoWhisper cho luồng semantic),
  distillation saliency L2 Top-K, `N_q=2` learnable query, CE + các đầu hồi quy V/A + distress
  gắn vào vector đã fusion. Vì các encoder giữ nguyên đóng băng và đặc trưng được tính sẵn, đây
  là một thí nghiệm **rẻ** (3.45M tham số huấn luyện, một GPU) — đúng loại ứng viên fusion học
  được mà V-A cần để đối chọi với baseline rule-based 2412.09829. Sản phẩm: một cấu hình
  `fusion=fas` trong script huấn luyện SER.

- **V-A/V-B → thiết lập prior về ngân sách token từ ablation của họ.** Bắt đầu đầu fusion của
  ViEmoSpeech tại `k_sem ≥ k_aco` và `N_q=2` (điểm bão hòa của họ) thay vì quét mù — Bảng
  5/Hình 4 của họ cho một khởi tạo có cơ sở bảo vệ được và tiết kiệm compute. Sau đó chạy
  ablation *đảo ngược*: liệu ngân sách thiên semantic có còn thắng khi luồng semantic bị nhiễu
  bởi PhoWhisper hay không? Ablation đó là một kết quả có thể công bố, kiểm định trực tiếp luận
  điểm thanh điệu×cảm xúc của ViEmoSpeech (định lượng V-D).

- **V-G → thêm một "lát cắt xung đột" vào giao thức đánh giá.** Phim truyền hình Việt Nam trong
  ViEmoSpeech tự nhiên chứa mỉa mai/che giấu; đánh dấu một **lát cắt phụ xung đột
  acoustic-semantic được giữ riêng** (cảm xúc do người gán nhãn ≠ cảm xúc mà một PhoBERT chỉ-đọc-
  văn-bản dự đoán từ bản chép) và báo cáo macro-F1 / CCC trên đó như một dòng riêng, tương tự
  cột zero-shot của CASE. Sản phẩm: một cờ `conflict_subslice` trong bộ held-out vàng, được báo
  cáo cạnh các con số tổng thể trong `docs/tasks/vn-tv-ser-pilot.md`.

### Lăng kính hiệu lực chuyển giao & đạo đức (bối cảnh ViEmoSpeech)

- **Sự không tương thích về register/ngôn ngữ là toàn diện, và đó chính là điểm mấu chốt.**
  CASE = tổng hợp (Doubao-TTS), diễn xuất theo thiết kế, tiếng Anh/Quan thoại, không có ASR
  trong vòng lặp (đặc trưng Whisper *thô*, không phải bản chép nhiễu), chỉ có softmax 7 lớp —
  không có valence/arousal, không có distress. ViEmoSpeech = phim truyền hình Việt Nam tự
  nhiên, bản chép PhoWhisper với **lỗi tone-swap ở mức arousal cao** (mày→máy, tao→tháo), 7 lớp
  + V/A (Russell 1–5, CCC) + một cờ distress có sàn recall. Vậy nên các con số của FAS **không
  phải là thanh đối chiếu tương đương**; chỉ có *kiến trúc* và *các prior từ ablation* của nó
  là chuyển giao được.
- **Nguyên tắc "tin vào acoustic khi có xung đột" của FAS nguy hiểm trong một ngôn ngữ có thanh
  điệu.** FAS giải quyết xung đột bằng cách ưu tiên luồng acoustic (nghiên cứu tình huống Hình
  5: "Trust Acoustic"). Trong tiếng Việt, kênh acoustic (F0/phonation) được **chia sẻ** giữa
  thanh điệu từ vựng và cảm xúc — nên "tin vào acoustic" không thể là một quy tắc phân xử áp
  dụng chung; cùng một biến thiên F0 có thể là một đường nét thanh điệu (tone contour) *hoặc*
  một tín hiệu cảm xúc. Cơ chế fusion của ViEmoSpeech phải giải quyết *đồng thời*, không được
  mặc định nghiêng về một modality. Đây là một cảnh báo ở cấp độ thiết kế, không phải một con số
  để tái sử dụng.
- **Đạo đức về distress tổng hợp so với tự nhiên.** CASE né tránh vấn đề đồng thuận (consent)
  bằng cách hoàn toàn tổng hợp; mục ethics của nó cảnh báo SER "có thể bị triển khai trong giám
  sát… thẩm vấn." ViEmoSpeech sử dụng giọng nói thật (có bản quyền) từ phim truyền hình dưới
  ràng buộc chỉ phát hành đặc trưng (features-only), với khung nhìn **distress = proxy diễn
  xuất, không phải lâm sàng** một cách trung thực tường minh — một *lập trường đạo đức khác*
  mà ViEmoSpeech đã tài liệu hóa; CASE đóng góp ngôn ngữ cảnh báo lạm dụng đáng để tham chiếu
  lại.
- **Sự sụp đổ của các lớp hiếm là dấu hiệu cảnh báo cho đầu distress (V-F).** Trên CASE, **không
  mô hình nào** dự đoán đúng bất kỳ mẫu fear hay disgust nào (Phụ lục A.2.3) — các lớp hiếm,
  xung đột cao biến mất dưới một mục tiêu CE phẳng. Cờ distress của ViEmoSpeech chính xác là
  một lớp hiếm, rủi ro cao như vậy; đây là bằng chứng trực tiếp rằng một đầu fusion CE thuần túy
  sẽ **không** đạt được sàn recall, thúc đẩy hàm mất mát sàn-recall / chính sách ngưỡng V-F thay
  vì tin tưởng vào softmax.

### Hạn chế & câu hỏi mở cho ViEmoSpeech

- **Mâu thuẫn/khoảng trống so với luận điểm cốt lõi của ViEmoSpeech (V-D).** CASE tuyên bố
  nghiên cứu "tone vs words" nhưng, bằng cách bao gồm cả *tiếng Quan thoại* (một ngôn ngữ có
  thanh điệu) và vẫn xem "tone" thuần túy là prosody, nó **chứng minh khoảng trống mà
  ViEmoSpeech lấp đầy**: chưa ai trong nhóm đối thủ gần nhất đã định lượng sự cạnh tranh kênh
  *thanh điệu từ vựng×cảm xúc*. Chính cấu hình tốt nhất của FAS (nhiều token semantic hơn
  acoustic, Bảng 5) còn gợi ý rằng luồng acoustic *kém* khả năng phân tách hơn giả định — nhất
  quán với giả thuyết ViEmoSpeech rằng thanh điệu và cảm xúc đan xen trong cùng một kênh
  acoustic và nhánh text phải bù đắp. ViEmoSpeech nên trích dẫn điều này như *bằng chứng ủng
  hộ*, không phải một đối thủ.
- **Mâu thuẫn so với vn-12 (Incongruent-SLM "semantics dominate") và so với FAS.** FAS khẳng
  định kênh *acoustic* nên thắng khi có xung đột và thiết kế CASE sao cho cảm xúc acoustic là
  ground truth; vn-12 báo cáo rằng SLM mặc định nghiêng về *semantic*. Hai khung nhìn này đối
  lập nhau về prior phân xử. ViEmoSpeech nằm giữa hai bên và không thể chọn theo bên nào làm
  quy tắc, bởi vì trong tiếng Việt kênh acoustic F0/phonation *tự nó đã mang tải ngữ nghĩa*
  (nó mang thanh điệu từ vựng). Câu hỏi mở: liệu một cơ chế fusion học được (kiểu FAS) có ngầm
  học được một sự phân xử theo từng câu nói vượt qua cả hai prior cố định trên các trường hợp
  xung đột tiếng Việt hay không?
- **Không có khả năng chống nhiễu ASR ở bất kỳ đâu trong FAS.** Luồng semantic của FAS là đặc
  trưng Whisper sạch từ văn bản ground-truth; nó không bao giờ đối mặt với lỗi phiên âm. Thất
  bại đầu bài của ViEmoSpeech — tone-swap của PhoWhisper ở mức arousal cao — nằm *ngoài* phạm
  vi đánh giá của FAS. Liệu đầu Top-K saliency + Q-Former có chống chịu được luồng semantic bị
  nhiễu bẩn hay không vẫn chưa được kiểm định và là một thí nghiệm thực sự thuộc sở hữu của
  ViEmoSpeech (kết nối V-A × V-C).
- **CASE chỉ có 378 mẫu tổng hợp, chỉ mang tính chẩn đoán** (Limitation của chính các tác giả:
  "không đủ quy mô để làm dữ liệu huấn luyện độc lập," ✔). Nó không thể là nguồn huấn luyện hay
  fine-tuning cho ViEmoSpeech, và phân phối TTS-diễn-xuất của nó cách xa hội thoại phim truyền
  hình tự phát — chỉ có thể dùng như một mẫu thiết kế đánh giá *khái niệm*.
- **Khả năng chuyển giao của bộ tokenizer acoustic chưa được kiểm chứng cho tiếng Việt.**
  MingTok-Audio / XCodec2 / VibeVoice là các codec TTS được huấn luyện trên (chủ yếu) tiếng
  Anh/Quan thoại; không có bằng chứng chúng bảo toàn chi tiết thanh điệu/phonation tiếng Việt.
  Trước khi áp dụng luồng acoustic của FAS, ViEmoSpeech phải kiểm chứng (V-B) xem một codec TTS
  hay một SSL nhạy phonation (WavLM/emotion2vec + jitter/shimmer/HNR/H1–H2) bảo toàn kênh
  thanh điệu-cảm xúc tốt hơn — chính tín hiệu mà ViEmoSpeech được xây dựng để đo lường.
