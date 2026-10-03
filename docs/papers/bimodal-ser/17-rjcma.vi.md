# Paper 17 — RJCMA: Recursive Joint Cross-Modal Attention for Multimodal Fusion in Dimensional Emotion Recognition

> Bản dịch tiếng Việt của [17-rjcma.md](17-rjcma.md) — cập nhật 2026-07-10.

- **Authors:** R. Gnana Praveen, Jahangir Alam
- **Venue / year:** CVPRW 2024 (ABAW6 — hạng 2 thử thách valence-arousal)
- **Links:** abs https://arxiv.org/abs/2403.13659 · PDF `pdfs/17-rjcma.pdf`
- **Group:** audio-visual (đối chứng)

**Summary:** Cơ chế attention chéo-modal phối hợp đệ quy (recursive joint cross-modal attention), dự đoán valence/arousal liên tục với CCC loss.

**Relevance to Pebble:** Fusion không phụ thuộc modality (modality-agnostic) + head hồi quy liên tục — pattern chuyển thẳng sang audio+text cho crisis/severity head.

> Mục nhập rút gọn từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa đọc sâu (deep-read).

## Analysis (mức độ trùng lặp với Pebble)

### Analysis — RJCMA (recursive joint cross-modal attention, DER)
- **Thay thế điểm số 19% ngày 2026-07-02, vốn được tính trên hồ sơ text-only đã lỗi thời.**
- **Hồ sơ được tổng hợp tại thời điểm phân tích** (intent + capabilities, không phải trí nhớ về văn bản text-only cũ): (1) `docs/intent/constraints.md` — chương trình chính là phân loại nguy cơ tự sát dạng thứ tự (ordinal) trên **văn bản** (nhãn bạc từ LLM bổ sung một cách trung thực cho dữ liệu gold lâm sàng khan hiếm), bị ràng buộc bởi gold-holdout, **tính toàn vẹn ở cấp độ đối tượng (subject-level integrity)**, các hàm loss/metric nhận biết thứ tự, khả năng tái lập, đạo đức lâm sàng. (2) `docs/spec/capabilities/voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md` — một **luồng voice liền kề đang hoạt động**: WavLM-Large / emotion2vec đóng băng + trunk dùng chung với **ba head không đồng nhất** (emotion CE · **head hồi quy affect V/A đã dùng CCC loss `1−ρc`** · crisis BCE dưới ngưỡng sàn recall cứng 0.90), được cân bằng bằng **Kendall uncertainty weighting**, 10-fold độc lập theo đối tượng (subject-independent). **Fusion voice+text là hướng đi tới đã được nêu tên.**
- **Overlap:** D1=1, D2=0, D3=1, D4=0, D5=0, D6=0, D7=1 → `(3·1 + 2·0 + 1·1 + 2·0 + 2·0 + 2·0 + 1·1)/26 × 100` = 5/26 × 100 = **19% (ngoại vi/peripheral)**.
- **Gần nhất ở:** D1 — hồi quy valence/arousal liên tục của RJCMA là **tương đồng trực tiếp với head `affect` của luồng voice** (`Linear(256,2)` V/A), chứ không phải tương đồng yếu kiểu "text-score" như khối phân tích cũ khẳng định; và D7 — nó fusion một **bộ mã hoá text họ BERT với một luồng audio**, đúng cặp voice+text mà Pebble đã nêu là hướng đi tới.
- **Điểm tốt nhất (Method nên áp dụng):** RJCMA là một **template đã công bố, có sẵn mã nguồn (github.com/praveena2j/RJCMA), hạng 2 tại ABAW6, dành đúng cho fusion affect-liên-tục audio+text mà Pebble nêu là hướng đi tới** — khối joint cross-modal attention của nó (xây một FC chung trên các đặc trưng modal đã ghép nối `J`, tính attention cross-correlation theo từng modal `H·W` so với `J`, tinh chỉnh đệ quy, ghép nối → head) là thành phần có thể chuyển giao mà khối phân tích text-only cũ đã sai khi bác bỏ là "không thể chuyển giao".
  - **Cách áp dụng cho Pebble:** Khi luồng voice chuyển từ đơn-modality sang **fusion voice+text**, fork khối joint cross-modal attention của RJCMA (Eqs 1–14) để nối đặc trưng **voice WavLM/emotion2vec đóng băng + đặc trưng text NeoBERT** thành một biểu diễn chung, tinh chỉnh đệ quy (`l=3` là tối ưu trong ablation của họ), sau đó đưa đặc trưng đã attend đã ghép nối vào các head **hiện có** emotion / affect-CCC / crisis — đây là fork-and-adapt trên mã nguồn công khai, không phải viết lại từ đầu. (Lưu ý: CCC loss mà khối phân tích *cũ* gắn cờ là điểm cần lấy thì **đã có sẵn** trong head affect của luồng voice, nên nó không còn là điểm mới nữa.)
- **Lưu ý (Caveats):** Đã đọc toàn bộ PDF (6 trang, gồm cả CCC-loss Eq 16 `L = 1 − ρc` và Table 1); không có phần nào bị chặn trả phí (paywalled). **Tỷ lệ % trùng với con số 19% cũ nhưng trên cơ sở đã sửa lại** — bài báo vẫn không chạm tới **bất kỳ** chiều trọng số cao nào của Pebble: không phải sức khoẻ tâm thần/crisis (Affwild2 = video YouTube trong-tự-nhiên về V/A; D2=0), không có teacher-LLM distillation (D4=0), **không có cân bằng loss MTL nguyên tắc** (valence & arousal là đầu ra hồi quy thuần, không có uncertainty/GradNorm — đối lập với Kendall weighting của luồng voice; D5=0), không có mục tiêu an toàn/recall-floor (D6=0), và các head của nó **đồng nhất, liên tục**, không phải topology không đồng nhất emotion+affect+crisis, nên D1=1 (một phần), không phải 2. Backbone chỉ khớp **một phần** (D7=1): text họ BERT thì có, nhưng backbone audio là **VGGish, không phải WavLM/emotion2vec SSL**, và BERT được dùng như **đặc trưng cấp từ đóng băng (tổng 4 layer cuối), không phải bộ mã hoá ~250M được fine-tune**. Điểm hợp phần nhỏ tích cực (không tính điểm): RJCMA chia Affwild2 theo **subject-independent**, khớp với ràng buộc subject-level-integrity của Pebble (I2).

## Deep research — đọc toàn bộ PDF (2026-07-10)

> Đọc dựa trên **phiên bản venue CVPRW 2024 / ABAW6** (CVF Open Access:
> `openaccess.thecvf.com/content/CVPR2024W/ABAW/html/Praveen_Recursive_Joint_Cross-Modal_Attention_..._CVPRW_2024_paper.html`).
> PDF cục bộ `pdfs/17-rjcma.pdf` = arXiv:2403.13659v4 (13 Apr 2024). Các con số CCC nổi bật, khẳng định
> "hạng 2", và các con số baseline đã được đối chiếu độc lập với listing CVF + abstract; các bảng nội bộ theo từng fold
> được đọc từ venue PDF (arXiv v4 khớp với abstract CVF).
> Phần này được chấm điểm dựa trên **hồ sơ ViEmoSpeech hiện tại + hệ thống ký hiệu V-A…V-H** (paper-deep-analysis.md,
> 2026-07-10), thay thế cho khối "Analysis" D1…D7 đã cũ ở trên. Đây là bài báo thuộc **nhóm đối chứng audio-VISUAL**;
> các phần có thể chuyển giao là **cơ chế fusion (V-A)**, **CCC loss cho V/A liên tục (V-G)**,
> và (như một tín hiệu tiêu cực) **lựa chọn backbone audio (V-B)**.

### Ghi chú nguồn truy cập

- **Trích xuất:** `pdftotext "docs/papers/bimodal-ser/pdfs/17-rjcma.pdf" -` (đọc đầy đủ 6 trang gồm cả
  4 bảng, Eqs 1–16, và cả phần tiền xử lý + huấn luyện). Các công thức được in dưới dạng LaTeX bên trong
  PDF, nên Eqs 1–16 được đọc nguyên văn, không phải tái dựng bằng OCR.
- **Đã đối chiếu trên web (venue = có thẩm quyền):**
  - Truy vấn `RJCMA Recursive Joint Cross-Modal Attention Aff-Wild2 CCC valence 0.542 arousal 0.619 ABAW6 second place`
    → trả về trang **CVF Open Access CVPRW 2024** + abstract arXiv, cả hai đều nêu CCC **valence 0.585 (0.542)
    và arousal 0.674 (0.619)** cho validation (test), "hạng 2 trong thử thách valence-arousal của ABAW lần thứ 6",
    baseline **valence 0.240 (0.211) / arousal 0.200 (0.191)**. ✔ đã đối chiếu (headline, thứ hạng, baseline).
  - Không tìm thấy xung đột preprint/venue; arXiv v4 (13 Apr 2024) == bản camera-ready CVPRW. Mã nguồn:
    `github.com/praveena2j/RJCMA` (được trích dẫn trong bài, không tải lại — không mang tính quyết định cho bất kỳ con số nào).

### Bài báo thực sự làm gì

- **Tác vụ.** Nhận diện cảm xúc theo chiều liên tục (Dimensional Emotion Recognition — DER) trên **Aff-Wild2** (track
  ABAW6): hồi quy **valence và arousal liên tục trong [-1,1]**, đánh giá bằng Concordance Correlation Coefficient (CCC).
  Không phải phân loại theo lớp rời rạc.
- **Ba modality, một khối fusion.** Audio + **Visual** + Text, mỗi cái được mã hoá rồi mô hình hoá theo thời gian
  bằng **TCN**, sau đó fusion bằng cơ chế đề xuất **Recursive Joint Cross-Modal Attention (RJCMA)** (§3.4).
  - Visual: ResNet-50 (pretrain trên MS-CELEB-1M → fine-tune trên FER+) → TCN (§3.1).
  - Audio: **VGGish** (VGG được pretrain trên AudioSet) trên **log-mel spectrogram**, hop = 1/fps → TCN (§3.2).
  - Text: **rút ra từ ASR.** Speech → ASR **Vosk** → khôi phục dấu câu/viết hoa →
    đặc trưng cấp từ **BERT** = **tổng 4 layer cuối** (đóng băng; không fine-tune) → TCN, với
    đặc trưng từ được phát tán theo thời gian (time-broadcast) tới tốc độ khung hình nhờ timestamp của ASR (§3.3, §4.2.1).
- **Cơ chế fusion RJCMA (§3.4, các công thức mang tính quyết định, tất cả ✔ đọc nguyên văn từ venue PDF):**
  - **Eq 1 — biểu diễn chung (joint representation):** `J = FC([X_a ; X_v ; X_t]) ∈ R^{d×K}`, `d = d_a+d_v+d_t`, K khung hình.
  - **Eqs 2–4 — cross-correlation chung** của mỗi modal so với `J`:
    `C_a = tanh( X_aᵀ W_ja J / √d )`, tương tự cho `C_v`, `C_t` (`W_j·` có thể học được).
  - **Eqs 5–7 — bản đồ attention:** `H_a = ReLU( X_a W_ca C_a )`, tương tự cho `H_v`, `H_t` (`W_c· ∈ R^{K×K}`).
  - **Eqs 8–10 — đặc trưng đã attend kèm residual:** `X_att,a = H_a W_ha + X_a`, tương tự cho v, t.
  - **Eqs 11–13 — đệ quy:** đưa đặc trưng đã attend quay lại: `X_att,·^(l) = H_·^(l) W_·^(l) + X_·^(l-1)`, l = bước đệ quy.
  - **Eq 14 — ghép nối:** `X_att^(l) = [X_att,a^(l); X_att,v^(l); X_att,t^(l)]` → head hồi quy MLP → valence *hoặc* arousal.
- **CCC loss (§4.2.3, mang tính quyết định cho V-G):**
  - **Eq 15 — metric:** `ρ_c = 2·σ²_xy / ( σ²_x + σ²_y + (μ_x − μ_y)² )` (x=dự đoán, y=ground truth).
  - **Eq 16 — objective:** `L = 1 − ρ_c`. Được chọn tường minh *thay cho MSE* vì là "loss chuẩn trong literature cho DER".
- **Huấn luyện (§4.2.2, ✔ từ PDF).** Adam, weight-decay 0.001, **batch 12**, tối đa 100 epoch + early stop; LR khởi tạo
  1e-5, LR tối thiểu 1e-8; **ReduceLROnPlateau trên CCC validation** (patience 5, factor 0.1) kèm warm-up;
  **progressive unfreezing** của backbone theo 3 nhóm layer; sub-sequence **K=300**, stride 200; **6-fold CV**
  (fold 0 = split chính thức); **l=3 vòng đệ quy** trong mọi lần chạy. **Valence và arousal được huấn luyện như hai model riêng biệt.**
- **Dataset (§4.1, ✔).** Aff-Wild2 / ABAW6: 594 video, ~2,993,081 khung hình, 584 đối tượng (subjects); V/A liên tục [-1,1],
  nhãn = **trung bình của 4 chuyên gia gán nhãn bằng joystick**; split **subject-independent** 356/76/162 (train/val/test).
- **Kết quả (✔ đã đối chiếu headline; ≈ per-fold nội bộ):**
  - Headline (abstract + CVF): **valence CCC 0.585 (0.542), arousal 0.674 (0.619)** cho val (test) — nhưng các
    con số val 0.585/0.674 là con số **fold tốt nhất (Fold 1)** (Table 1/Table 3), *không phải* validation Fold-0
    chính thức, vốn là **valence 0.455 / arousal 0.652** (Table 2). ✔ (cả hai đều xuất hiện ở Table 1 & Table 2).
  - Baseline: **valence 0.211 / arousal 0.191** (test, Table 4). ✔.
  - **Bảng xếp hạng test ABAW6 (Table 4):** RJCMA đứng **hạng 2** chung cuộc, trung bình 0.5807 (valence 0.5418 / arousal 0.6196);
    hạng 1 = Netease Fuxi (trung bình 0.6721, pretrain MAE + ensemble, chỉ audio-visual). ✔.
  - **Ablation về số vòng đệ quy (Table 3, Fold 1):** l=1 trung bình 0.607 → l=2 0.618 → **l=3 0.629 (tốt nhất)** → l=4 0.615
    (giảm, được cho là do overfitting). Tổng mức tăng l=1→l=3 = **+0.022 CCC trung bình**. ≈ (chỉ một fold, không có std).
  - **Thêm text so với RJCA audio-visual của chính họ (Table 2, test):** RJCA (bản họ tự cài lại, chỉ A+V)
    valence 0.537 / arousal 0.576 → RJCMA (A+V+**T**) valence 0.542 / arousal 0.619. **Thêm text tăng +0.005 valence,
    +0.043 arousal.** ≈ (bản tự cài lại của họ, một split). Đây là con số nội bộ liên quan nhất tới ViEmoSpeech.

### Các phần hữu ích trực tiếp cho ViEmoSpeech (mỗi phần gắn Decision ID + mức rủi ro chuyển giao)

1. **[V-A] Khối joint cross-modal attention (Eqs 1–14) thu gọn về hai modal = một template fusion audio↔text
   sẵn sàng dùng ngay (drop-in).** ViEmoSpeech không có luồng visual, nên đặt `X_v = ∅`: Eq 1 trở thành
   `J = FC([X_a ; X_t])`, và chỉ hai nhánh audio + text của Eqs 2–14 còn tồn tại — đây *chính là*
   Joint Cross-Attention 2-modal trước đó của Praveen, ở đây đã được nối sẵn thêm một nhánh text. Cơ chế
   **không phụ thuộc số lượng modal**: biểu diễn chung `J` và cross-correlation theo từng modal
   `C_·` được định nghĩa trên bất kỳ tập modal nào được ghép nối. **Rủi ro chuyển giao — THẤP-đến-TRUNG BÌNH.** Phần
   toán học chuyển giao gọn gàng, nhưng (a) fusion của họ hoạt động trên **chuỗi đồng bộ theo khung hình**
   (K=300, đặc trưng từ được phát tán theo thời gian tới tốc độ khung hình) — việc căn chỉnh audio↔text của chúng ta ở **cấp
   utterance/turn** (một clip, một transcript ASR), nên chúng ta sẽ fusion vector audio *đã pool* + vector text *đã pool*,
   mất đi phần cross-attention theo từng khung hình vốn là một nửa giá trị của cơ chế; hoặc ta giữ ở cấp chuỗi bằng cách
   phát tán đặc trưng token PhoBERT trên các khung WavLM qua timestamp từ PhoWhisper (chúng ta đã có sẵn từ pipeline ASR).
   (b) tinh chỉnh đệ quy chỉ mang lại **+0.022 CCC trung bình** (Table 3) và overfit tại l=4 trên 356 video — trên
   corpus nhỏ hơn của chúng ta (3611 utt), l=1 (joint cross-attention thuần, không đệ quy) là mặc định trung thực và
   l>1 cần có bằng chứng từ held-out-fold mới được dùng. Artifact cụ thể: **nhánh learned-fusion** phải đánh bại
   baseline rule-based PhoWhisper+PhoBERT — RJCMA nằm cùng CASE/FAS Q-Former, WavFusion gate, BCAF deep-supervision
   trong menu fusion-candidate V-A, như một lựa chọn **cross-correlation-attention**.

2. **[V-G] CCC loss `L = 1 − ρ_c` (Eqs 15–16) là objective trực tiếp cho head valence/arousal của chúng ta.**
   Đây là điểm chuyển giao giá trị cao nhất: head V/A của chúng ta hồi quy valence/arousal theo Russell, và CCC là
   metric mà hồ sơ đã nêu tên cho đánh giá V-G ("CCC cho V/A"). Dùng `1 − ρ_c` làm loss **huấn luyện** (không chỉ
   metric đánh giá) làm cho objective khớp với metric và, khác với MSE, **bất biến với scale và shift** —
   nó thưởng cho *sự đồng thuận về xu hướng*, bền vững trước độ lệch giữa các annotator. Mức tăng của chính RJCMA so với
   baseline ABAW (valence 0.211→0.542, arousal 0.191→0.619 trên test) là một bằng chứng tồn tại rõ ràng rằng hồi quy
   dùng CCC-loss hoạt động tốt trên dữ liệu affect đa modal, ồn, trong-tự-nhiên, được nạp qua ASR. **Rủi ro chuyển giao — TRUNG BÌNH.**
   CCC được tính **trên toàn batch/sequence** (cần phương sai σ²_x, σ²_y trên các mẫu), nên đòi hỏi **batch đủ lớn** và
   **hỏng trên các batch quá nhỏ/suy biến** (σ²→0 khi mọi dự đoán bằng nhau); batch 12–32 của chúng ta trên 3611 utt
   nằm gần chế độ batch-12 của họ, khả thi nhưng cần đề phòng hiện tượng dự đoán gần-hằng-số sụp đổ ở giai đoạn đầu huấn luyện.
   Lưu ý lớn hơn: V/A của họ là **liên tục [-1,1], trung bình 4 chuyên gia bằng joystick**; **của chúng ta là 1–5 theo
   Russell, gán nhãn người một lượt duy nhất, rời rạc/thứ tự** (V-E). CCC trên thang rời rạc 5 điểm là hợp lý nhưng thô hơn
   nhiều — số hạng phương sai bị chi phối bởi 5 bin, nên cần báo cáo CCC **cùng với** một metric thứ tự (QWK / MAE), và
   coi con số CCC là **không tương đương** với Aff-Wild2 hay MSP-Podcast (thang 1–7 SAM; xem bimodal-12).
   Artifact cụ thể: loss của head V/A trong config huấn luyện fusion + hàng metric V-G.

3. **[V-B] Backbone audio là một tín hiệu *tiêu cực* — VGGish/log-mel + 2D-CNN là một control đã lỗi thời, không phải
   một khuyến nghị.** RJCMA đạt hạng 2 với **VGGish (AudioSet) trên log-mel spectrogram** làm bộ mã hoá audio — không
   có WavLM, không có emotion2vec, không có wav2vec2. Với ViEmoSpeech đây là một điểm dữ liệu **không nên sao chép**:
   VGGish có trước các bộ mã hoá speech SSL và nắm bắt cấu trúc sự-kiện-âm-thanh chung, không phải phonation/chất giọng
   — chính kênh mà tone×emotion tiếng Việt nằm trong đó (vn-06 Shen, vn-13 Chang). **Rủi ro chuyển giao — CAO nếu sao chép
   nguyên xi.** Nhưng có hai phần con vẫn *có thể* chuyển giao: (a) **head thời gian TCN trên các embedding cấp khung hình**
   là một phương án pooling nhẹ, giữ thứ tự, có thể đặt lên trên các khung WavLM/emotion2vec đóng băng thay cho mean-pool;
   (b) lịch trình **progressive-unfreezing** của họ (3 nhóm layer, warm-restart LR theo từng nhóm, tải lại trạng thái tốt
   nhất) là một công thức cụ thể cho quyết định backbone đóng băng-hay-fine-tune (V-B). Artifact cụ thể: lựa chọn bộ mã hoá
   nhánh audio + lịch trình đóng băng/fine-tune trong config fusion — RJCMA là bằng chứng rằng ngay cả một bộ mã hoá audio
   *yếu* + fusion mạnh vẫn cạnh tranh được, điều này làm sắc nét hơn câu hỏi ablation của chúng ta "bao nhiêu phần của mức
   tăng đến từ fusion so với backbone."

### Từng phần giúp ViEmoSpeech thành công như thế nào

- **[V-A] Nhánh fusion.** Thêm một **thí nghiệm `rjcma_fusion`** vào menu V-A: hai nhánh đóng băng
  (audio WavLM/emotion2vec + text PhoBERT-trên-PhoWhisper), phát tán đặc trưng token PhoBERT trên các khung WavLM
  theo timestamp từ của ASR (pipeline đã phát ra sẵn), sau đó áp dụng Eqs 1–14 với **l=1 mặc định**, quét l∈{1,2,3}
  chỉ trên một fold held-out. Nối `X_att` đã fusion vào trunk dùng chung nuôi các head emotion 7 lớp,
  V/A-CCC, và distress. Đây là *fork-and-adapt* trên mã nguồn công khai (`github.com/praveena2j/RJCMA`),
  không phải xây từ đầu — khối joint-correlation chỉ khoảng ~10 dòng.
- **[V-G] Objective của head V/A.** Đặt loss của head valence/arousal là `1 − ρ_c` (Eq 16), tính theo từng batch,
  và thêm một **cơ chế bảo vệ** chống sụp đổ dự đoán hằng số (sàn phương sai tối thiểu / warm-up bằng MSE trong
  N bước đầu rồi anneal sang CCC). Báo cáo CCC song song với QWK+MAE để thang 1–5 rời rạc vẫn có thể diễn giải được.
  Điều này hiện thực hoá trực tiếp metric V-G "CCC cho V/A" thành một objective *có thể huấn luyện được*, không chỉ là đánh giá.
- **[V-B] Thiết kế ablation backbone.** Dùng RJCMA làm **hàng control "bộ mã hoá yếu + fusion mạnh"**: chạy fusion
  của chúng ta với (i) nhánh VGGish/log-mel (setup của họ) so với (ii) WavLM so với (iii) emotion2vec-S — nếu fusion
  chiếm ưu thế, câu chuyện tone×emotion cần một bộ mã hoá *nhận biết phonation* để tạo khác biệt (là động lực cho vector
  jitter/shimmer/HNR/H1-H2 thủ công từ vn-06). Áp dụng công thức TCN-trên-khung + progressive-unfreeze của họ cho nhánh fine-tune.

### Lăng kính sức khoẻ tâm thần trẻ em / tính hợp lệ khi chuyển giao sang ViEmoSpeech

- **Sai lệch về register là toàn phần trên nội dung, chỉ một phần trên cơ chế.** Aff-Wild2 là video **YouTube
  reaction/vlog** người lớn, trong-tự-nhiên — không có trẻ em, không có distress lâm sàng, không có ngữ âm ngôn ngữ
  thanh điệu, và quan trọng là **audio-visual** nơi khuôn mặt chiếm ưu thế. Không có gì về *cái gì* được dự đoán
  chuyển giao được; chỉ có *toán học fusion* và *objective CCC* là chuyển giao được. Đây là một bài báo thuộc
  **nhóm đối chứng** theo đúng thiết kế (theo cách đặt tác vụ), và nên được trích dẫn như nguồn gốc phương pháp
  cho V-A/V-G, không bao giờ như một mốc thực nghiệm cho SER tiếng Việt.
- **Nhánh text của họ là cửa sổ liên quan nhất tới ViEmoSpeech — và đó là một câu chuyện cảnh báo.** Text của RJCMA
  **rút ra từ ASR (Vosk) + BERT đóng băng (tổng 4 layer cuối)**, tức đúng chế độ nhiễu-ASR của chúng ta và một bộ
  mã hoá text *đóng băng*. Thêm nhánh text đó làm **arousal tăng +0.043 nhưng valence chỉ tăng +0.005** (Table 2, test).
  Đọc đối chiếu với tổng hợp xuyên suốt (theme #1, tính trội của text phụ thuộc register), trong một chế độ text
  **ASR nhiễu, không fine-tune**, nhánh text hầu như không giúp được chiều *valence* (tính dễ chịu) — nhất quán với
  cực "text ASR tiếng Việt gần như vô dụng" của vn-08 và *đối lập* với cực trội-của-text-trên-transcript-sạch (bimodal-11).
  **Hàm ý cho V-C của chúng ta:** một nhánh text được nạp từ ASR mà **đóng băng** thì gần như vô dụng cho valence;
  PhoBERT phải được **fine-tune** (và được chính quy hoá chống lại nhiễu ASR đổi thanh điệu) để nhánh text mang được
  gánh nặng mà điểm neo tone×emotion cần. RJCMA là bằng chứng trực tiếp rằng text *đóng băng* là không đủ.
- **Đạo đức/pháp lý.** Không có dữ liệu trẻ em, không có tuyên bố lâm sàng, không có vấn đề phát hành media thu thập
  chạm tới các ràng buộc của chúng ta — Aff-Wild2 là một benchmark học thuật công khai. Thực hành duy nhất có thể tái
  sử dụng là **split subject-independent**, khớp với bất biến speaker-disjoint của chúng ta (I2) — một điểm tương đồng
  nhỏ, không phải một bài học.

### Hạn chế & câu hỏi mở cho ViEmoSpeech (gồm ≥1 mâu thuẫn/khoảng trống tường minh)

- **MÂU THUẪN với kế hoạch multi-task của chúng ta (V-A/V-G/V-E).** RJCMA huấn luyện **các model riêng biệt cho
  valence và arousal** (§4.2.2), và việc dùng model riêng cho mỗi chiều cảm xúc là chuẩn mực trong ABAW. Toàn bộ
  thiết kế của ViEmoSpeech là một model **multi-task trunk dùng chung** duy nhất (7 lớp + V/A + distress). Vậy nên
  khối fusion và CCC loss của RJCMA chuyển giao được, nhưng **topology huấn luyện của nó thì không** — chúng ta phải
  fusion *một lần* rồi phân nhánh ra các head, và cân bằng V/A-CCC với CE phân loại + sàn recall của distress (một
  bài toán cân bằng loss MTL mà RJCMA không bao giờ gặp phải, vì nó chỉ có một đầu ra liên tục cho mỗi model). RJCMA
  cho chúng ta **bằng không** chỉ dẫn về cân bằng loss giữa các head không đồng nhất.
- **MÂU THUẪN với bimodal-11 / CASE về cách xử lý text-encoder.** RJCMA dùng BERT **đóng băng** (tổng 4 layer cuối);
  bimodal-11 (RoBERTa+WavLM, gần với stack của chúng ta nhất) và CASE/FAS đều **fine-tune / distill** nhánh text.
  Mức tăng valence gần-bằng-không từ text ASR đóng băng của RJCMA là cái giá thực nghiệm của lựa chọn đó — bằng chứng
  cho phe fine-tune. Chúng ta nên trích dẫn RJCMA như điểm dữ liệu "text đóng băng kém hiệu quả", không nên đi theo
  công thức của nó.
- **KHOẢNG TRỐNG — không có phân tích độ bền vững với ASR dù pipeline được nạp từ ASR.** RJCMA nạp ASR Vosk vào nhánh
  text nhưng không bao giờ đo lỗi ASR ảnh hưởng thế nào tới CCC (không có ablation clean-vs-ASR). Đây là *cùng*
  khoảng trống như mọi bài báo fusion khác trong tập hợp (CASE, WavFusion, BCAF đều dùng transcript gold) — và đây
  chính là đóng góp mới của chúng ta: ViEmoSpeech vận hành dưới **lỗi ASR đổi thanh điệu khi cường độ cao** (mày→máy)
  mà pipeline Vosk tiếng Anh của RJCMA không bao giờ gặp phải. Ablation độ bền vững ASR trên head fusion + CCC của
  chúng ta thực sự chưa được bài báo này đề cập tới.
- **Bằng chứng nội bộ yếu cho cơ chế chủ đạo.** Đệ quy (điểm mới được đặt tên của bài báo so với RJCA trước đó) chỉ
  mang lại **+0.022 CCC trung bình** trên *một fold duy nhất*, không có std (Table 3), và modal text (điểm mới còn
  lại) chỉ thêm **+0.005 valence** (Table 2). Cả hai "cải thiện" này đều có thể nằm trong biên độ dao động của fold/seed —
  một lời cảnh báo rằng chúng ta **không nên** mặc định cho rằng độ sâu đệ quy hay một nhánh text gắn thêm sẽ giúp
  ích cho head V/A của chúng ta mà không có phép đo held-out-fold + multi-seed của riêng chúng ta (protocol V-G:
  8-fold speaker-disjoint + std theo seed, theo tiền lệ THAI-SER).
- **Không thể so sánh về thang đo.** CCC của Aff-Wild2 dựa trên nhãn **liên tục [-1,1], trung bình 4 chuyên gia bằng
  joystick**; CCC của chúng ta sẽ dựa trên nhãn **rời rạc 1–5, một lượt duy nhất**. Con số 0.542/0.619 của họ **không
  phải** là mục tiêu hay ngưỡng cho chúng ta — nó chỉ là bằng chứng rằng công thức hồi quy dùng CCC-loss hội tụ được.
  Bất kỳ so sánh CCC xuyên corpus nào (Aff-Wild2 so với MSP-Podcast thang 1–7 so với thang 1–5 của chúng ta) đều phải
  được gắn cờ là không tương thích về thang đo, cùng một lưu ý mà chúng ta đã ghi cho bimodal-12 (MSP).
