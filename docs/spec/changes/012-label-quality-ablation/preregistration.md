# Pre-registration — Ablation chất lượng nhãn (change 012)

> **Văn bản này phải được commit và ĐÔNG CỨNG trước khi chạy kernel Kaggle đầu tiên.**
> Sau thời điểm đó, mọi thay đổi nhánh / tập test / metric / ngưỡng phải ghi thành
> một mục sửa đổi có ngày tháng ở §11 — **không sửa tại chỗ**.
>
> Phiên bản 1 · 2026-08-31 · [change 012](README.md) · trạng thái: **ĐÔNG CỨNG 2026-08-31**
>
> Owner duyệt 2026-08-31: ngưỡng 0.02, 10 seed, giữ C′ — nguyên trạng như dưới đây.

## 0. Vì sao phải pre-register

Ablation này có 4 nhánh × 2 eval × 2 head. Đó là **16 con số**. Nếu chọn nhánh sau
khi nhìn thấy kết quả, ta sẽ luôn tìm được một ô nào đó ủng hộ kết luận mình muốn —
"review có ích" hoặc "review vô ích", tuỳ tâm trạng. Chốt trước quy tắc quyết định
(§7) là cách duy nhất để con số này có nghĩa.

Cùng lý do đó với **kết quả null**: §9 buộc phải báo cáo dù delta bằng 0.

## 1. Câu hỏi & giả thuyết

**Câu hỏi vận hành:** nhãn đã qua phân xử có làm SER probe tốt lên đủ để biện minh
cho công annotate thêm không?

- **H1:** nhãn sau review (B) > nhãn owner (A) trên macro-F1 emotion.
- **H0:** không khác biệt — nhiễu nhãn ở mức 15.8% emotion **không phải** nút thắt
  hiện tại (nút thắt nằm ở backbone English-centric / valence audio-only).

Cả hai kết quả đều hữu ích và đều được báo cáo. H0 chuyển hướng đầu tư công sức.

## 2. Tập clip — cố định, 1071

Giao của: queue `review-candidates.tsv` (1071) ∩ bộ lọc `build_kaggle_gold.py`
(`emotion` ≠ rỗng, không `rejected`, không `multi`) = **1071 clip, không mất clip nào**.

| | |
|---|--:|
| chay-tron-thanh-xuan | 807 |
| ve-nha-di-con | 264 |

**Loại trừ đã chốt trước:**

- **122 clip** label sau khi queue được dựng (2026-08-06) — không có nhãn vòng 2 nên
  không thể xuất hiện ở nhánh B/C; đưa vào chỉ nhánh A sẽ phá tính so sánh được.
- **718 clip** owner đã reject (631 `multi_speaker`) — chưa bao giờ vào queue review.

Tập clip **giống hệt nhau ở cả 4 nhánh**. Chỉ cột nhãn thay đổi.

## 3. Bốn nhánh

`agreed` = vyphan bấm "Đồng ý" ⇒ **cả 6 trường** giống nhãn owner (server ép:
`agreed` mà khác `original` → HTTP 400). Đã kiểm chứng: 606/606 agreed row khớp
tuyệt đối, 0 row thiếu V/A.

| Nhánh | Train trên | n | Vai trò |
|---|---|--:|---|
| **A** | nhãn owner | 1071 | baseline, chạy lại đúng cỡ tập |
| **B** | nhãn sau review (`answer`) | 1071 | A + 169 sửa emotion · 104 valence · 193 arousal |
| **C** | chỉ clip đồng thuận | 606 | "ít nhưng sạch" — lọc theo đồng thuận |
| **C′** | nhãn owner, **rút ngẫu nhiên 606** | 606 | **đối chứng cỡ mẫu** cho C |

**C′ là bắt buộc, không phải thêm thắt.** Nếu thiếu, C thua A không phân biệt được
là do ít mẫu hơn hay do lọc bỏ mất clip khó. C rút bằng `numpy.default_rng(seed)`,
**phân tầng theo (series × emotion owner)** để khớp phân bố lớp của C.

## 4. Tập test — nhãn cố định, 606 clip

**Đây là điểm dễ hỏng nhất của thiết kế.** Train A rồi chấm bằng nhãn A, train B rồi
chấm bằng nhãn B, là đổi **cả tín hiệu học lẫn cây thước** — B sẽ trông tốt hơn chỉ
vì đề thi đã đổi theo. Delta đó vô nghĩa.

**Quy tắc:** mọi nhánh chấm trên **đúng 606 clip đồng thuận**, nơi nhãn owner và nhãn
vyphan **giống hệt nhau theo định nghĩa**. Chỉ nhãn train thay đổi → delta trung thực.
Áp dụng cho **cả hai head** (agreed ⇒ V/A cũng khớp).

**Không rò rỉ:** metric tính trên **dự đoán out-of-fold**. Mỗi clip trong 606 được
dự đoán bởi mô hình của fold **không chứa** nó. Mask test áp **sau** khi đã gom OOF,
không đụng vào cách chia fold.

Phân bố tập test (606): neutral 194 · anger 135 · joy 96 · sadness 61 · disgust 48 ·
fear_anxiety 40 · surprise 32.

## 5. Metric

- **Headline:** macro-F1 emotion 7 lớp.
- **Kèm theo, không được lược bỏ:** UAR · per-class support · CCC valence · CCC arousal.
- **Gộp seed trước khi chấm.** Mỗi nhánh chạy 10 seed; dự đoán OOF gộp lại thành
  **một** dự đoán/clip: emotion lấy **nhãn xuất hiện nhiều nhất** qua 10 seed, V/A lấy
  **trung bình**. Seed chỉ đổi khởi tạo head (và mẫu rút của C′), không đổi fold.
- **So sánh giữa các nhánh = delta theo cặp**, không phải hai CI độc lập.
  Hai nhánh được chấm trên **cùng một mảng nhãn test**, nên chỉ dự đoán khác nhau:
  bootstrap 1000 lần trên 606 clip test, **dùng chung chỉ số resample cho cả hai nhánh**,
  rồi lấy phân vị 2.5/97.5 của hiệu. Hai CI chồng nhau **không** đồng nghĩa "không khác
  biệt" — nên không dùng cách đó.
- **Độ nhạy theo seed** báo kèm: khoảng [min, max] của hiệu tính riêng từng seed.
- **Seed:** `0..9` (10 seed). Frozen. Không thêm seed sau khi thấy kết quả.
- CI của từng nhánh: bootstrap 1000 lần như kernel hiện tại.

## 6. Hai eval — giữ nguyên như baseline hiện hành

- **Eval A — GroupKFold(ep), 5 fold.** Cast lặp trong cùng series → rò rỉ danh tính
  → số **lạc quan**.
- **Eval B — Leave-one-series-out.** Cross-cast, speaker-disjoint thật (I4/ADR-002)
  → số **trung thực**, và là eval dùng cho quy tắc quyết định §7.

**Cảnh báo power, ghi trước khi thấy số:** ở LOSO, fold test `ve-nha-di-con` trong
tập 606 chỉ có **surprise 5 · disgust 7**. Macro-F1 7 lớp với lớp 5 mẫu là nhiễu.
→ Chiều LOSO→`ve-nha-di-con` **không kết luận được cho lớp hiếm**, và điều đó được
ghi nhận ở đây chứ không phải sau khi kết quả không đẹp. Quyết định §7 đọc trên
macro-F1 LOSO (gộp OOF của **cả hai** chiều, như kernel vẫn làm), kèm UAR.

## 7. Quy tắc quyết định — chốt trước

Đọc trên **Δ(B−A) macro-F1, eval LOSO, tập test 606, trung bình 10 seed**:

| Điều kiện | Kết luận | Hành động |
|---|---|---|
| Δ ≥ **+0.02** và CI 95% của Δ **không chứa 0** | review có lợi rõ | mở rộng review sang 122 clip còn lại + phần corpus mới |
| \|Δ\| < 0.02 **hoặc** CI chứa 0 | **H0** — nhiễu nhãn không phải nút thắt | **dừng** đầu tư adjudication cho mục tiêu model; chuyển sang backbone / nhánh text. Vòng mù vẫn chạy, nhưng lý do là **κ cho paper (I6)**, không phải hiệu năng |
| Δ ≤ **−0.02** và CI không chứa 0 | review làm nhãn **xấu đi** | dừng, soát lại guideline trục `fear_anxiety`↔`anger` trước khi annotate thêm |

Đọc riêng cho câu hỏi "lọc theo đồng thuận có đáng không": so **C vs C′** (cùng 606).
Δ(C−C′) ≥ +0.02, CI không chứa 0 → lọc theo đồng thuận có lợi. C so trực tiếp với A
**không** được dùng làm căn cứ (khác cỡ mẫu).

Ngưỡng **0.02** chọn theo: baseline LOSO hiện tại 0.249 với CI ±0.03; dưới 0.02 thì
không phân biệt được với nhiễu ở cỡ mẫu này, và cũng không đủ để biện minh cho ~4.2
giờ nghe/1071 clip (đo từ log vyphan: median 14 s/clip).

## 8. Điều này **không** thiết lập

- **Không** phải κ human–human. Vòng review bị neo (vyphan thấy nhãn owner trước khi
  trả lời) — `qc-protocol.md` §5.3 tách riêng owner-vs-annotator vì đúng lý do này.
- **Không** phải headline accuracy (I6 đòi test-split speaker-disjoint **và** độ tin
  cậy nhãn từ κ; ở đây chưa có κ).
- **Không** merge vào `state.db`. 465 bất đồng vẫn chờ owner phân xử — việc riêng.

## 9. Báo cáo bất kể kết quả

Cả 4 nhánh × 2 eval × 2 head được ghi vào `docs/reports/`, kèm `config.json`
(backbone id, seed list, split_hash, pip pin, `label_source`) + `metrics.json` (I5).
**Không** được chỉ báo nhánh thắng. Kết quả null được báo nguyên trạng.

## 10. Tham số đông cứng

| | |
|---|---|
| backbone | `microsoft/wavlm-large`, **đóng băng**, masked-mean pool 1024-d |
| head | `torch.nn.Linear`, Adam lr 1e-3, weight_decay 1e-4, 200 epoch |
| emotion | 7 lớp, weighted-CE theo tần suất lớp trong fold train |
| affect | valence/arousal 1–5, CCC loss |
| fold | GroupKFold(ep) 5 fold (greedy, nhóm nặng trước) · LOSO theo series |
| seed | 0–9 |
| feature cache | `.npz`, tính **một lần**, dùng chung cho cả 4 nhánh |

Embedding tính một lần rồi cache ⇒ 4 nhánh × 10 seed vẫn chỉ là linear probe trên
feature có sẵn: **một session P100** đủ.

## 10b. Code thực thi

| Nơi | Việc |
|---|---|
| `scripts/vietnamese-ser/build_kaggle_gold.py --keys --reviews` | dựng tập clip cố định + cột `*_reviewed` + `agreed` |
| `kaggle/.../vnser-train.py` `VNSER_ABLATION=1` | 4 nhánh × seed × 2 eval, chấm trên mask `agreed`, xuất `ablation.md` + `metrics_ablation.json` |
| `verdict()` trong cùng file | áp **máy móc** quy tắc §7 vào báo cáo — không có chỗ diễn giải lại sau khi thấy số |

## 11. Sửa đổi sau khi đông cứng

*(chưa có)*
