# Thesis Pebble‑LLM — Giải thích từ đầu (cho người đọc lần đầu)

**Ngày viết:** 2026‑07‑02 · Mọi con số đã kiểm chứng khớp log gốc (xem `kaggle/finetuning-message/results-summary.csv` và `docs/tasks/thesis-message-review.md`).

> Tài liệu này trả lời 3 câu hỏi, cho từng giai đoạn: **phương pháp là gì → thực nghiệm kiểm chứng điều gì → kết quả ra sao, có đạt mục đích không.**

---

## 0. Thesis trong 3 câu

1. **Bài toán:** đọc chuỗi bài viết của một người trên mạng xã hội và xếp mức **nguy cơ tự sát** vào 1 trong 4 bậc **có thứ tự** (Indicator < Ideation < Behavior < Attempt) — nhưng nhãn do bác sĩ gán (nhãn "vàng") **cực kỳ khan hiếm** (chỉ 500 người dùng).
2. **Phương pháp:** dùng **LLM gán nhãn hàng loạt** (rẻ, nhiều, nhưng nhiễu) để train, và đề xuất một **giao thức đánh giá trung thực (gold‑holdout)**: chỉ chấm điểm trên nhãn bác sĩ được giữ riêng — cộng thêm 3 cải tiến phương pháp để xử lý cái giá của nhãn nhiễu.
3. **Kết quả:** nhãn LLM giúp thật — macro‑F1 trên nhãn bác sĩ tăng **0.19 → 0.42 (~×2.2)**; đồng thời phát hiện và định lượng được *vì sao* nhãn LLM chưa tốt hơn nữa (chệch phân bố 3×, ~36% nhãn lớp hiếm nhiễu, và cấu trúc ordinal phải trả giá dưới nhiễu).

---

## 1. Bối cảnh: thesis này từ đâu ra? (vì sao "emotion classifier" thành "suicide risk")

**Xuất phát từ sản phẩm.** Pebble là app companion sức khoẻ tinh thần. Kiến trúc cũ dùng **một lời gọi Gemini** vừa chấm cảm xúc vừa sinh phản hồi. Kế hoạch ban đầu (Strategy v1→v3): thay bằng **một classifier fine‑tune riêng** xuất 6 chiều mỗi tin nhắn (`energy`, `severity`, `socialIsolation`, `receptivity`, `detectedEmotion`, `safetyFlag`) để Decision Engine định tuyến *trước* khi sinh phản hồi.

**Vì sao pivot sang 2 bài báo?** Vì thesis cần **đóng góp học thuật** — mà "classifier 6 đầu ra cho app" không có benchmark, không có gold‑standard, không publish được. Nên dự án **thu hẹp có chủ đích** vào 2 chiều có gold‑standard lâm sàng:

| Chiều trong spec sản phẩm | Đi đâu trong thesis |
|---|---|
| `severity` + `safetyFlag` | → **Bài Text**: nâng safetyFlag nhị phân thành thang **ordinal 4 mức C‑SSRS** (thang lâm sàng chuẩn Columbia) |
| `detectedEmotion` (+ affect) | → **Bài Voice**: emotion + affect + crisis head cho giọng nói |
| `energy`, `socialIsolation`, `receptivity` | → không học; thành heuristic của Decision Engine (quyết định từ v1) |

Điểm nối quan trọng: **câu hỏi phương pháp của thesis chính là vấn đề Pebble sẽ gặp** — Pebble không có nhãn người gán, nếu build classifier thật sẽ phải nhờ LLM gán nhãn. Thesis trả lời trước: *nhãn LLM dùng được đến đâu, chệch/nhiễu kiểu gì, đo thế nào cho khỏi tự lừa mình.* Cái chuyển giao về sản phẩm là **phương pháp + bài học về nhãn**, không phải checkpoint model.

---

## 2. Bốn khái niệm nền (đọc 2 phút, hiểu cả bài)

1. **Ordinal (có thứ tự):** 4 mức nguy cơ có thứ bậc — đoán nhầm Behavior thành Ideation (kề nhau) *ít sai hơn* đoán thành Indicator (cách 2 bậc). Vì vậy ngoài macro‑F1 còn phải đo **QWK** (phạt lỗi xa nặng hơn, bậc hai) và **MAE** (độ lệch bậc trung bình).
2. **Nhãn vàng (gold) vs nhãn yếu (weak/LLM):** gold = 4 bác sĩ tâm thần gán trên corpus CSSRS‑Reddit 500 user — chuẩn nhưng quá ít. Weak = LLM đọc post và gán nhãn — rẻ, tạo được ~10k mẫu, nhưng nhiễu và chệch.
3. **Đánh giá circular (tự lừa mình):** train trên nhãn LLM rồi *chấm điểm cũng trên nhãn LLM* — giống ôn đúng bộ đề rồi thi lại chính bộ đề đó. Điểm rất cao (0.67) nhưng vô nghĩa: nó đo "model bắt chước LLM giỏi cỡ nào", không đo "model đúng với bác sĩ cỡ nào".
4. **Gold‑holdout (giao thức trung thực — xương sống của thesis):** train **chỉ** trên nhãn LLM, chấm điểm **chỉ** trên nhãn bác sĩ được giữ riêng hoàn toàn (tách theo *người dùng*, không phải theo post, để không rò rỉ). Con số thu được nhỏ hơn nhiều (0.36–0.42 thay vì 0.67) nhưng là con số **thật**.

Và một nhân vật xuyên suốt: **lớp Behavior** (đã có hành vi chuẩn bị/tự hại — lâm sàng quan trọng bậc nhất vì đứng ngay trước Attempt). Nó hiếm trong pool LLM (634/9680 ≈ 7%) và là lớp mọi thí nghiệm xoay quanh.

---

## 3. Phương pháp (version hiện tại) — một đoạn

**Mô hình:** tái lập kiến trúc paper tham chiếu "R2" (Yang et al., IEEE BigData 2025) — encoder MentalRoBERTa đọc từng post → transformer 3 lớp đọc *chuỗi* post của một người → attention‑pool → 2 đầu ra: **CORAL head** (chuyên ordinal) + **CE head** (phân loại thường), loss trộn `0.5·CORAL + 0.3·CE + 0.2·Focal`. **Giao thức:** gold‑holdout như trên, 5‑fold, seed cố định, stack pin (mọi số kèm std + log). **Ba cải tiến phương pháp (đóng góp của ta):** (1) thay CORAL+Focal bằng **CORN+GCE** — loss ordinal bền nhiễu hơn; (2) **label‑shift correction** — sửa chệch phân bố nhãn LLM→gold *sau khi train, không train lại*; (3) **ordinal‑aware confident learning** — dò nhãn nhiễu có ý thức về thứ bậc.

---

## 4. Chuỗi thực nghiệm — mỗi thí nghiệm: để kiểm chứng gì → ra gì → đạt không

### E1 — Train và chấm đều trên gold (gold‑CV) → macro‑F1 **0.19**
- **Kiểm chứng:** chỉ dùng 500 user nhãn bác sĩ thì học được đến đâu? (đo "trần" của hướng không‑augment)
- **Kết quả:** 0.19 — quá thấp, đúng như lo ngại: dữ liệu gold không đủ để học.
- **Đạt?** ✅ Đạt mục đích *chẩn đoán*: xác lập lý do tồn tại của cả thesis (phải augment bằng nhãn rẻ).

### E2 — Train và chấm đều trên nhãn LLM (within‑LLM) → **0.67**
- **Kiểm chứng:** minh hoạ cái bẫy circular — nếu đo kiểu "tự chấm bài mình" thì số đẹp cỡ nào?
- **Kết quả:** 0.67 — cao gấp rưỡi số thật. Con số này **không bao giờ** được dùng làm kết quả; nó tồn tại để chỉ ra vấn đề.
- **Đạt?** ✅ Đạt — nó là "bằng chứng buộc tội" cho luận điểm trung tâm: đánh giá within‑LLM tự lừa mình.

### E3 — Gold‑holdout đầu tiên: train LLM, chấm gold → **0.3569**
- **Kiểm chứng:** câu hỏi trung tâm của thesis — *nhãn LLM có giúp thật không, khi đo trung thực?*
- **Kết quả:** 0.3569 — so với 0.19 của E1 là **gần gấp đôi**. Nhãn LLM giúp thật.
- **Đạt?** ✅ Đạt — đây là kết quả trả lời trực tiếp câu hỏi nghiên cứu. Đồng thời lộ ra vấn đề mới: lớp Behavior gần như sụp (F1 ~0.18).

### E4 — Thêm rebalance lớp hiếm (Run B) → **0.3849 ±0.007**, QWK 0.398
- **Kiểm chứng:** Behavior yếu có phải vì *sampling* (mẫu hiếm ít được gặp khi train) không? — thử cân bằng lại tần suất lấy mẫu.
- **Kết quả:** cả 3 metric toàn cục đều nhích (macro 0.357→0.385, QWK 0.378→0.398, MAE giảm) nhưng **Behavior vẫn 0.183**.
- **Đạt?** ✅ Đạt mục đích chẩn đoán dù "thất bại" về Behavior: **loại trừ được giả thuyết sampling** → nút thắt phải nằm ở *chất lượng nhãn*. (Kết luận này được E9 xác nhận độc lập.)

### E5 — Within‑distribution CV trên đủ 10,072 mẫu (Run A) → **0.6530 ±0.005**
- **Kiểm chứng:** phần tái lập kiến trúc có đúng không — đặt trong *cùng loại giao thức* mà paper gốc dùng (within‑distribution) thì số của ta đứng đâu so với 0.5098 của paper?
- **Kết quả:** 0.6530 — cao hơn số paper báo cáo. **Caveat gắn liền, không tách rời:** đây là cùng *giao thức* nhưng trên **tập 10k tự làm giàu bằng nhãn LLM của ta**, không phải benchmark gated gốc của họ, và số này đo trên nhãn LLM — đúng loại số mà E2 dạy ta phải nghi ngờ. Không claim SOTA.
- **Đạt?** ✅ Đạt mục đích thật của nó: chứng minh phần tái lập không "làm hỏng" kiến trúc (sanity check) — và cho một điểm so sánh tham khảo với paper. (Lịch sử: 2 lần chạy đầu vô hiệu vì bug mount dataset — đã sửa và chạy lại sạch.)

### E6 — Ablation "bỏ hết phần ordinal, chỉ CE thuần" (flat‑CE) → **0.4215 ±0.024**, Behavior 0.285
- **Kiểm chứng:** bộ loss ordinal cầu kỳ (CORAL+Focal) đang *đóng góp* hay đang *phá*? — tháo ra xem sao.
- **Kết quả:** **bất ngờ lớn nhất thesis**: bỏ ordinal lại TỐT HƠN (0.4215 vs 0.3849), và Behavior hồi 0.183→0.285. Kiểm chứng thống kê (paired per‑fold, 2026‑07‑02): thắng ở **5/5 fold, p<.05** — kết quả vững nhất toàn bộ chuỗi.
- **Đạt?** ✅ Đạt hơn cả mong đợi — một **negative finding trung thực**: cấu trúc ordinal phải trả giá khi train trên nhãn nhiễu/chệch. Nó đặt ra câu hỏi cho E7: *vì sao?*

### E7 — CORN+GCE + bảng ablation 2×2 → **0.4022 ±0.013**, Behavior **0.260**
- **Kiểm chứng:** giải thích *cơ chế* nghịch lý E6 bằng 2 giả thuyết: (a) CORAL dùng chung một vector trọng số cho mọi ngưỡng → 1 nhãn Behavior nhiễu làm bẩn *mọi* ranh giới; (b) Focal khuếch đại mẫu "khó" — mà mẫu khó thường chính là mẫu nhiễu. Nếu đúng, thay CORAL→CORN (mỗi ngưỡng trọng số riêng) và Focal→GCE (giảm trọng số mẫu đáng ngờ) phải phục hồi được. Chạy đủ 2×2 (CORAL/CORN × Focal/GCE) để tách vai trò từng thành phần.
- **Kết quả:** đúng hướng — CORN+GCE 0.402/Behavior 0.260, tốt hơn dual cũ (0.385/0.183); trong 2×2, đổi head (CORN) kéo nhiều hơn đổi loss (GCE). **Nhưng hai chữ "nhưng" trung thực:** (i) vẫn thua flat‑CE (0.422/0.285); (ii) **QWK giảm** — dual cũ 0.398 > flat‑CE 0.388 > CORN+GCE 0.361, nghĩa là CORN+GCE đổi *độ nhất quán xếp hạng toàn cục* lấy *khả năng cứu lớp hiếm*. Về thống kê: hơn dual chỉ ở mức xu hướng (4/5 fold, p<.10); mức tăng Behavior +0.077 chưa đạt ý nghĩa (variance fold lớn).
- **Đạt?** ⚠ **Đạt một nửa.** Cơ chế được xác nhận đúng hướng (đóng góp 1 có cơ sở), nhưng claim phải viết dưới dạng **trade-off** chứ không phải "ordinal head tốt nhất mọi mặt"; và cần thêm seed nếu muốn khẳng định thống kê.

### E8 — Label‑shift correction (không train lại, 0 GPU) → Behavior **0.357 → 0.410**
- **Kiểm chứng:** gap LLM→gold có phải một phần là **chệch phân bố có hệ thống** (không phải nhiễu ngẫu nhiên) không? Đo trực tiếp: Behavior chiếm 7.3% pool LLM nhưng 19.7% gold → LLM **under‑label 3.0×**. Nếu là shift thật, một phép hiệu chỉnh xác suất hậu kỳ (Logit Adjustment) phải cải thiện được mà **không cần train lại**.
- **Kết quả:** đúng — Behavior‑F1 +0.053 (0.357→0.410), trần oracle 0.441. Chi phí: ~80 dòng Python chạy CPU.
- **Đạt?** ⚠ **Đạt về ý tưởng, mỏng về bằng chứng:** mới đo trên **1 checkpoint** (fold tốt nhất), và tham số τ đang được chọn trên chính tập gold dùng để báo cáo (lỗ hổng tune‑on‑test phải vá: cố định τ trước hoặc chọn trên tập validation riêng). Cần chạy đủ 5 fold trước khi vào paper.

### E9 — Ordinal‑aware confident learning (chẩn đoán nhãn nhiễu) → **35.8%** nhãn Behavior bị nghi sai
- **Kiểm chứng:** khẳng định của E4 ("nút thắt là chất lượng nhãn") bằng công cụ độc lập: cleanlab dò nhãn nghi sai từ xác suất out‑of‑fold. Kèm cải tiến: cleanlab gốc coi nhãn là *nominal* (lỗi kề bị xử như lỗi xa) → thêm trọng số khoảng‑cách‑hạng `|ỹ−ŷ|²` để "cắt lỗi xa, giữ lỗi kề" (lỗi kề Behavior↔Ideation thường là borderline hợp lệ về lâm sàng).
- **Kết quả:** 227/634 = **35.8%** nhãn Behavior bị flag (toàn cục chỉ 16.2%) — xác nhận nút thắt đúng là nhãn. Biến thể ordinal đạt đúng tín hiệu đăng ký trước: bắt 100% lỗi‑xa, giữ 78% lỗi‑kề (bản nominal flag bừa 45% lỗi‑kề).
- **Đạt?** ⚠ **Đạt phần chẩn đoán, thiếu phần hiệu quả:** chưa chạy **Arm2** — retrain trên pool đã làm sạch — nên chưa chứng minh việc *làm sạch cải thiện model*. (~3h GPU; dữ liệu `cl_issues.npz` đã có sẵn local.)

### E10 — Hai baseline chuẩn IEEE → plain‑RoBERTa **0.3456**, BiLSTM‑MTL **0.3783**
- **Kiểm chứng:** mọi kết quả trên có hơn được các mốc so sánh đơn giản không (cột bắt buộc của reviewer)?
- **Kết quả:** mọi cấu hình của ta vượt cả 2 baseline (flat‑CE thắng BiLSTM 5/5 fold, p<.05). Kèm một phát hiện thú vị: **kiến trúc dual‑head tái lập từ paper không phân biệt được với BiLSTM baseline trên gold** (0.385 vs 0.378, không có ý nghĩa thống kê) — củng cố thêm câu chuyện "dưới shift, giá trị nằm ở dữ liệu weak‑sup + loss đơn giản, không phải kiến trúc cầu kỳ".
- **Đạt?** ✅ Đạt.

---

## 5. Trả lời thẳng: mục đích có đạt không?

**Câu hỏi nghiên cứu trung tâm** — *"nhãn LLM có augment được tập gold khan hiếm cho phân loại ordinal nguy cơ tự sát không, đo trung thực?"* — **ĐÃ được trả lời: CÓ**, với con số 0.19 → 0.42 (~×2.2) dưới giao thức không tự lừa. Kèm theo, thesis định lượng được *ba lý do* khiến nhãn LLM chưa tốt hơn nữa — mỗi lý do đi cùng một cải tiến đo được:

| Lý do gap LLM→gold | Bằng chứng | Cải tiến tương ứng | Trạng thái |
|---|---|---|---|
| Chệch phân bố có hệ thống | Behavior under‑label **3.0×** | Label‑shift correction (+0.05 Behavior, 0 train lại) | ⚠ cần đủ 5 fold + vá chọn τ |
| Nhãn lớp hiếm nhiễu | **35.8%** Behavior bị flag | Ordinal‑CL "cắt xa giữ kề" | ⚠ cần Arm2 đo hiệu quả cuối |
| Cấu trúc ordinal khuếch đại nhiễu | flat‑CE > mọi ordinal head (p<.05) | CORN+GCE thu hẹp gap, cứu Behavior | ⚠ viết lại thành trade‑off (QWK giảm) |

**Những gì CHƯA đạt (trung thực):**
1. **Cohen's κ LLM↔gold chưa đo** — mảnh định lượng trực tiếp "nhãn LLM tệ đến đâu"; là câu hỏi đầu tiên reviewer sẽ hỏi. 🔴
2. Ba cải tiến mới ở mức "bằng chứng ban đầu": E7 cần reframe + seed, E8 cần 5 fold, E9 cần Arm2 (chi tiết: `docs/tasks/thesis-message-review.md`).
3. Behavior sau mọi nỗ lực vẫn ≤0.29–0.41 tùy phương pháp — đủ để *kể chuyện phương pháp*, chưa đủ để *dùng lâm sàng*. Thesis không giấu điều này.

**Một câu cho người ngoài ngành:** thesis không cố đạt điểm cao nhất — nó chứng minh *cách đo trung thực* lợi ích của nhãn máy‑gán trong bài toán lâm sàng nhạy cảm, chỉ ra đúng chỗ nhãn máy hỏng, và đưa 3 công cụ vá từng chỗ hỏng đó với chi phí thấp.

---

## 6. Nhánh Voice (tóm tắt — chi tiết ở `docs/papers/voice/`)

Cùng triết lý "đo cho trung thực" áp vào giọng nói: **V1** tái lập emotion2vec (sanity) → **V2** so backbone công bằng (frozen probe, 3 seed): WavLM‑Large thắng emotion2vec **0.609 vs 0.537, 3/3 seed** — một *negative result sạch* cho giả định ban đầu "emotion2vec là chính" → **V3** crisis head với **sàn recall ≥ 0.90** (ưu tiên không bỏ sót): precision đạt **0.617** → **V4** MTL 3 head (emotion + affect + crisis): kernel đã build, ⏳ chờ chạy; cần quyền MSP‑Podcast cho nhãn affect thật.

---

## 7. Đọc tiếp ở đâu

| Cần gì | File |
|---|---|
| Toàn cảnh + bảng số đầy đủ | `docs/reports/THESIS-OVERVIEW-vi.md` |
| Số máy‑đọc‑được, từng fold | `kaggle/finetuning-message/results-summary.csv` |
| Kiểm chứng provenance + paired stats | `docs/tasks/thesis-message-review.md` |
| 3 cải tiến: thiết kế + research grounding | `docs/tasks/r2-method-improvements-for-contribution.md` |
| Kế hoạch & draft bài IEEE | `docs/papers/finetuning-message/PAPER-{PLAN,DRAFT}-text-ordinal-suicide.md` |
