# Ba đóng góp chính — BÀI 2 (Voice): *Recall-Floored Heterogeneous Heads for Crisis-Sensitive Speech Affect*

> **Mục đích.** Giải thích chi tiết 3 đóng góp khoa học của luồng Voice, mỗi đóng góp theo
> cùng một khung: **phần cũ là gì → kết quả cũ → cải tiến là gì → kết quả mới → đóng góp gì**.
> **Nguồn số liệu:** `kaggle/voice/pebble-voice-backbone/out/results_voice_backbone.json` (đã chạy thật),
> `docs/voice-method-selection.md`, `docs/tasks/voice-mtl-heads.md`, code kernel `c4_probe.py` / `c4_heads.py`.
>
> **Trạng thái tổng:** Đóng góp 1 & 2 **đã có số thật** (Kaggle P100, 3 seed). Đóng góp 3 **đã build kernel,
> chưa chạy Kaggle** (nhãn affect/crisis hiện là proxy → cần MSP-Podcast cho số meaningful).

---

## Bối cảnh chung — Pebble "bên text" để biết "cái cũ"

Hệ thống gốc của Pebble là **text-only** (NeoBERT) cho phân loại nguy cơ tự tử dạng **ordinal**.
Đặc trưng nhận diện (signature novelty) của nó là **heterogeneous heads dưới một sàn recall an toàn cứng**
(emotion softmax + regression liên tục + safety BCE ở recall ≥ 0.95). Toàn bộ luồng Voice là việc
**mang đặc trưng đó sang modality giọng nói** — và trả lời các câu hỏi mở mà chính bản survey voice nêu ra.

Mỗi đóng góp dưới đây = một bước "từ cái đã có (text / giả định) → cái mới (voice / đo thật)".

---

## Đóng góp 1 — Paired-delta backbone selection: emotion2vec vs WavLM-Large

### Phần cũ là gì?
- **Giả định trong survey voice:** chọn **emotion2vec làm backbone chính** (vì nó cho "đặc trưng cảm xúc
  mạnh nhất trên mỗi tham số" theo bảng linear-probe của chính paper emotion2vec), WavLM-Large chỉ là
  **baseline/fallback** (MIT-licensed, mô hình tổng quát mạnh).
- Đây mới chỉ là **một lựa chọn chưa được kiểm chứng** — survey tự thừa nhận: *"backbone comparison này
  tự nó là một chương luận văn sạch — không phải một giả định để bảo vệ."*
- Bên text, việc so sánh mô hình đã dùng **phương pháp paired-delta 3-seed** (`pebble-mlm-3seed`,
  seeds `[13, 42, 1337]`, mean ± std + delta theo từng seed) — nhưng **chưa từng áp dụng cho voice**.

### Kết quả cũ?
- **Không có.** Trước thí nghiệm này chỉ là kỳ vọng "mô hình chuyên cảm xúc nên thắng mô hình tổng quát".
  Chưa có con số nào cho modality voice.

### Cải tiến là gì?
- **Chạy head-on comparison** với đúng phương pháp paired-delta đã proven bên text, lần đầu cho voice:
  - **Frozen probe:** mỗi encoder bị đóng băng, chỉ chạy **một lần** để cache embedding utterance
    (WavLM-Large: mean-pool `last_hidden_state` → 1024-d; emotion2vec: utterance embedding 768-d).
  - Chỉ huấn luyện các **MLP head nhỏ** bên trên (vài giây trên P100) → rẻ, có chủ đích.
  - **3 seed** `[13, 42, 1337]`, split **speaker-independent** (actor 1–20 train, 21–24 val) trên **RAVDESS**.
  - **Verdict = paired delta theo từng seed** (emotion2vec − WavLM), không chỉ so trung bình.
  - Arm emotion2vec được **guard**: nếu `funasr` lỗi cài/import thì bỏ qua arm đó, WavLM vẫn cho kết quả đủ.

### Kết quả mới? *(đã chạy thật — Kaggle P100, 3 seed)*

| Backbone | Emotion macro-F1 | Distress recall@0.5 | Precision @ recall-floor 0.90 |
|---|---|---|---|
| **WavLM-Large (winner)** | **0.609 ± 0.019** | 1.00 ± 0.00 | **0.617 ± 0.003** (thr 0.69) |
| emotion2vec | 0.537 ± 0.007 | 1.00 ± 0.00 | 0.597 ± 0.012 (thr 0.72) |
| **paired delta** (e2v − WavLM) | **−0.071 ± 0.017** — **3/3 seed < 0** | — | −0.020 ± 0.015 (2/3 < 0) |

- **WavLM-Large thắng** ~7 điểm macro-F1, **âm trên *mọi* seed** → kết luận ổn định, không phải may rủi.
- **Lý do (khớp caveat của survey):** WavLM-Large lớn hơn (1024-d vs 768-d) và pretrain trên **~360× lượng
  audio nhiều hơn**; emotion2vec chỉ được validate trên emotion *categorical* bằng protocol riêng của nó;
  RAVDESS là acted speech có thể ưu ái encoder âm học tổng quát.

### Đóng góp gì?
1. **Trả lời dứt điểm câu hỏi mở của survey** ("mô hình chuyên cảm xúc có thực sự thắng mô hình tổng quát
   mạnh không?"): **trên protocol này — KHÔNG.** Một negative result sạch, citable.
2. **Khuyến nghị backbone cho toàn bộ luồng Voice của Pebble = WavLM-Large** (kèm license MIT + công thức
   dimensional-regression mà survey đã đánh dấu).
3. **Chuyển phương pháp đánh giá paired-delta 3-seed từ text sang voice** → giữ tính reproducible-by-construction
   (mỗi số truy được về một kernel + log).

---

## Đóng góp 2 — Chuyển "hard crisis-recall-floor head" từ text sang giọng nói

### Phần cũ là gì?
- Bên **text**, novelty headline của Pebble là **safety head = BCE dưới một sàn recall cứng** (recall ≥ 0.95):
  trong bối cảnh nguy cơ tự tử, **bỏ sót (false negative) là chi phí không chấp nhận được**, nên hệ thống
  bị *ràng buộc cứng* phải bắt được tối thiểu X% ca dương, rồi mới tối ưu precision trong phần còn lại.
- Survey voice chỉ rõ đây là **khoảng trống chưa ai làm cho speech**: *"không hệ thống công bố nào làm
  heterogeneous … speech-driven affect MTL dưới một hard crisis-recall floor."*

### Kết quả cũ?
- Tồn tại bên **text** (recall-floor head trên NeoBERT) nhưng **chưa có bản voice** nào — recall-floor chưa
  từng được vận hành trên đặc trưng âm học.

### Cải tiến là gì?
- **Đưa cơ chế recall-floor sang voice:** gắn một **distress/safety head** (pos-weighted BCE,
  `SAFETY_POS_WEIGHT = 3.0`) lên frozen speech encoder. Cơ chế threshold:
  - Trên RAVDESS, **distress = nhãn nhị phân suy ra** từ emotion: `{sad, angry, fearful, disgust} = dương`.
  - **Tune ngưỡng τ trên tập val** = ngưỡng *cao nhất* (precision tốt nhất) mà vẫn giữ `recall ≥ 0.90`
    (`RECALL_FLOOR`), rồi **report precision@floor trên test** — đúng "safety framing" của Pebble.
  - Mã hoá trong `threshold_at_recall()` (backbone kernel) và `threshold_for_recall()` (MTL kernel).

### Kết quả mới? *(đã chạy thật)*
- **precision @ recall≥0.90 = 0.617 ± 0.003** (WavLM, threshold 0.69) — head an toàn vẫn giữ được
  ~62% precision *trong khi bị buộc cứng* phải đạt 90% recall.
- **Verify end-to-end** qua FastAPI verifier trên clip held-out RAVDESS:
  - fearful → distress **0.84** (flagged), angry → **0.76** (flagged), sad → **0.91** (flagged),
    neutral → **0.68** (không flagged) → safety head **tách đúng** high-distress khỏi neutral.
- Báo cáo **cả đường precision–recall**, không chỉ một điểm 0.90 (chống phản biện "0.90 là tuỳ chọn").

### Đóng góp gì?
1. **Lần đầu cắm novelty headline của Pebble (recall-floored safety head) vào modality speech** — biến
   "hard crisis-recall constraint" từ khái niệm text thành cơ chế chạy được trên đặc trưng âm học.
2. **Vận hành hoá ràng buộc an toàn** thành một quy trình đo lường rõ: tune-on-val → report-on-test
   precision@floor, có thể tái dùng cho mọi dataset distress sau này (StressID, DAIC).
3. **Caveat trung thực** đi kèm: RAVDESS distress là **proxy** (acted, không phải crisis lâm sàng) →
   định khung đúng phạm vi kết luận, mở đường cho dữ liệu lâm sàng (DAIC/E-DAIC) ở bước sau.

---

## Đóng góp 3 — Heterogeneous MTL: emotion CE + affect V/A CCC + crisis BCE, cân bằng bằng Kendall

### Phần cũ là gì?
- Backbone pilot (Đóng góp 1–2) chỉ có **2 head**: emotion softmax + distress BCE, train độc lập
  (loss = tổng đơn giản hai số hạng).
- Luận văn yêu cầu đúng **topology head dị thể (heterogeneous)** giống bên text: phân loại + **regression
  liên tục** + safety — nhưng bản voice mới chỉ dừng ở 2 head **đồng nhất kiểu phân loại**, **chưa có**
  head regression liên tục và **chưa có** cơ chế cân bằng đa nhiệm.

### Kết quả cũ?
- Có metric cho emotion + distress (xem Đóng góp 1–2), nhưng **không có affect liên tục (valence/arousal)**
  và **không có balancing** giữa các loss có thang đo rất khác nhau (CE ~ vài đơn vị vs CCC ∈ [0,2] vs BCE).

### Cải tiến là gì? *(kernel `pebble-voice-mtl-heads` — đã build, chưa chạy Kaggle)*
- **3 head dị thể trên cùng một shared SUPERB trunk** (`Linear(d,256) → ReLU → masked-mean-pool`):

  | Head | Kiến trúc | Loss | Metric |
  |---|---|---|---|
  | **emotion** | `Linear(256, 8)` | Cross-entropy | WA / UA / WF1 |
  | **affect** | `Linear(256, 2)` | **CCC loss** trên valence + arousal | CCC(v), CCC(a) |
  | **crisis** | `Linear(256, 1)` | BCE dưới **hard recall floor** | recall / precision@floor |

- **Cân bằng đa nhiệm bằng Kendall homoscedastic uncertainty weighting** (Kendall, Gal & Cipolla, CVPR 2018):
  mỗi task có một tham số **log-variance học được**; loss tổng = `Σ 0.5·exp(−log_var_i)·L_i + 0.5·log_var_i`.
  → mô hình **tự học trọng số** từng task thay vì chỉnh tay; đây cũng là **comparator** của luận văn so với
  GradNorm / PCGrad.
- **CCC loss** (`1 − 2·cov / (var_p + var_t + (μ_p − μ_t)² )`) — đúng metric chuẩn của dimensional affect
  (dòng AVEC), thay cho MSE.
- Giao thức **random 10-fold CV 80/10/10**; crisis threshold vẫn **tune-on-val theo recall floor 0.90**.
- **MTL math đã smoke-test trên CPU**: cơ chế recall-floor đạt **recall = 0.90 đúng bằng**; local infer
  `scripts/voice_mtl_infer.py`.

### Kết quả mới?
- **Chưa có số khoa học meaningful** — và đây là điểm trung thực quan trọng nhất:
  - RAVDESS **không có** nhãn V/A liên tục và **không có** nhãn crisis → hai head mới hiện học **nhãn proxy**
    (user-approved 2026-06-23): affect = **Russell (1980) circumplex** cố định theo emotion; crisis =
    tập `{angry, fearful, sad, disgust}`.
  - Proxy circumplex **gần circular** → CCC tự nó **không meaningful**; chỉ chứng minh được **cơ chế**
    (3-head MTL + Kendall + recall-floor) **chạy được trên frozen features thật**.
- **Việc còn lại để có số thật:**
  1. Chạy Kaggle MTL-heads (M3) → 10-fold metrics cho cả 3 head + artifact load local (M4).
  2. **Nâng cấp bằng MSP-Podcast** (nhãn arousal/valence/dominance liên tục **thật**, **voice-only** nên
     không vi phạm ràng buộc "không paired data") → CCC thật, citable so với AVEC.

### Đóng góp gì?
1. **Topology head dị thể đầy đủ cho speech affect** — phân loại + regression liên tục + safety **trong
   một mô hình**, lần đầu mang đủ bộ "heterogeneous heads" của Pebble sang voice.
2. **Áp dụng Kendall uncertainty weighting để cân bằng 3 loss khác thang đo** + đặt nền cho **ablation**
   Kendall vs GradNorm vs PCGrad (đóng góp phương pháp về MTL balancing cho crisis-affect).
3. **Kiến trúc + training loop đã được chứng minh chạy** (smoke-tested), tách bạch rõ "cơ chế đã proven"
   với "số khoa học cần dữ liệu thật" — một sự trung thực phương pháp luận mà reviewer IEEE đánh giá cao.

---

## Bảng tổng kết — cũ → mới cho cả 3 đóng góp

| # | Phần cũ | Kết quả cũ | Cải tiến | Kết quả mới | Trạng thái |
|---|---|---|---|---|---|
| 1 | Giả định emotion2vec là backbone chính (chưa kiểm chứng) | Không có số voice | Paired-delta 3-seed frozen probe, e2v vs WavLM trên RAVDESS | WavLM thắng: Δ macro-F1 **−0.071**, 3/3 seed < 0 | ✅ **đã chạy thật** |
| 2 | Recall-floor safety head chỉ tồn tại bên text (NeoBERT) | Không có bản voice | Đưa recall-floor BCE sang frozen speech encoder, tune-on-val | **precision@recall0.90 = 0.617 ± 0.003**; verify e2e OK | ✅ **đã chạy thật** |
| 3 | Mới có 2 head đồng nhất, train độc lập, không balancing | Có emotion + distress, **thiếu** affect liên tục & balancing | 3 head dị thể (CE + CCC + BCE) + Kendall uncertainty weighting, 10-fold | **Cơ chế chạy** (smoke-test); số CCC/crisis cần MSP-Podcast | ⚠️ **kernel built, chưa chạy Kaggle** |

## Đóng góp tổng (1 câu cho abstract)
> Pebble-Voice chuyển novelty "heterogeneous heads dưới hard crisis-recall floor" từ text sang speech,
> **chứng minh bằng paired-delta rằng WavLM-Large > emotion2vec cho crisis-sensitive speech affect**,
> vận hành recall-floored safety head trên đặc trưng âm học (precision@recall0.90 = 0.617), và đề xuất
> topology MTL dị thể (emotion CE + affect CCC + crisis BCE) cân bằng bằng Kendall uncertainty weighting.
