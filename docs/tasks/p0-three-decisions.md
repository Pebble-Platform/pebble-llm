# P0 — Ba quyết định đang chặn: phân tích phương án & khuyến nghị

- **Slug:** p0-three-decisions
- **Status:** chờ owner quyết
- **Created:** 2026-09-05 · **Owner:** user / Claude
- **Bối cảnh:** P0 của [roadmap](viemospeech-scale-roadmap.md). Ba câu này chặn P2 và
  chặn mọi số cuối cùng của paper.

## Tóm tắt khuyến nghị

| # | Quyết định | Khuyến nghị | Lý do một dòng |
|---|---|---|---|
| 1 | Series test | **Không phải series nào đang có.** Test = series thứ 3, **cùng miền Bắc** | Cả 2 series hiện tại đều trượt sàn ADR-002 hoặc làm rỗng train set |
| 2 | Media / compute | **CPU local** (đo được: 1,5–2h/tập) làm mặc định; thuê GPU rời ~$15–35 nếu cần nhanh. **Không** đưa tập phim đầy đủ lên Kaggle | Không có GPU local (đã kiểm), CPU local có wall-clock ngang Kaggle mà không phơi nhiễm pháp lý |
| 3 | Quy mô | **P1 làm mục tiêu, nhưng chia nhỏ**: extract series 3 trước (~30 tập), label tới sàn, rồi mới quyết tiếp | Ràng buộc thật là nhãn người (2–3k), không phải extraction (18k) |

Một phát hiện xuyên suốt cả ba: **corpus hiện 100% giọng Bắc**, trong khi
`docs/intent/constraints.md §6` cam kết dialect metadata Bắc/Trung/Nam vì
"different tone systems". Xem [§4](#4-phát-hiện-xuyên-suốt-dialect).

---

## 1. Series nào làm test set?

### Câu hỏi thật sự là gì

[ADR-002](../spec/decisions/ADR-002-whole-series-speaker-disjoint-gold.md) đã chốt
**phương pháp** (hold out nguyên series, disjoint theo cấu trúc) nhưng để mở **series
nào**. ADR-002 cũng đặt sẵn tiêu chí định lượng:

> Kích thước: sàn **≥50 clip ở lớp emotion hiếm nhất**, target **80–100** trước khi báo
> per-class UAR/macro-F1.

### Dữ liệu thật (đo 2026-09-05 từ `state.db`)

| Series | n sạch | Lớp hiếm nhất | Sàn ≥50 | Target ≥80 |
|---|--:|---|:--:|:--:|
| `chay-tron-thanh-xuan` | 951 | surprise **62** | ✅ PASS | ❌ FAIL |
| `ve-nha-di-con` | 264 | surprise **10** | ❌ **FAIL (thiếu 5×)** | ❌ FAIL |

### Phương án

| PA | Nội dung | Vấn đề |
|---|---|---|
| **A.** `ve-nha-di-con` làm test | test 264 clip, train 951 | **Trượt sàn ADR-002 5 lần.** surprise 10 mẫu ⇒ per-class F1 là nhiễu thuần tuý. Đúng cái ablation 012 vừa vấp phải |
| **B.** `chay-tron-thanh-xuan` làm test | test 951 clip (đạt sàn) | Train còn **264 clip**. Không train nổi cái gì có nghĩa |
| **C.** Series thứ 3 làm test | train = 1.215 clip hiện có, test = series mới | Tốn label thêm cho series test — nhưng đây là **chi phí bắt buộc**, không phải chi phí phát sinh |
| **D.** Hoãn, dùng LOSO 2 chiều như hiện tại | không quyết gì | LOSO hiện tại **không phải** test-split; nó là cross-validation. Paper cần một held-out **không bao giờ** được train |

### ✅ Khuyến nghị: PA C — series thứ 3, **cùng miền Bắc**

Cụ thể: **Sống chung với mẹ chồng** (34 tập, VTV Giải Trí chính thức) theo top-1 của
[`05-scale-plan.md §7`](../papers/vietnamese-ser/05-scale-plan.md) — dày thoại nhất,
gọn, một run kênh chính thức.

**Vì sao cùng miền Bắc chứ không lấy series miền Nam làm test:** nếu test là giọng Nam
còn train là giọng Bắc, con số headline sẽ trộn **hai** hiệu ứng — đổi dàn diễn viên
(cái ta muốn đo) và đổi hệ thanh điệu (cái khác hẳn). Không tách được thì không diễn
giải được. Miền Nam nên là **một eval riêng về dialect-shift**, không phải test chính.

**Ngân sách nhãn cho test set** — với tỉ lệ lớp tự nhiên đo được (surprise 5,9% ·
disgust 8,3%):

| Mục tiêu | Clip cần label nếu lấy ngẫu nhiên |
|---|--:|
| surprise ≥ 50 (sàn) | ~844 |
| surprise ≥ 80 (target) | ~1.350 |

ADR-002 cho phép **ưu tiên clip để annotate** rồi backfill cân bằng lớp. Dùng gợi ý
teacher (opus/sonnet) để oversample ứng viên `surprise`/`disgust` ⇒ số thật sẽ thấp hơn
nhiều so với 844. **Nhưng phải backfill**, không để sampling quyết định phân bố cuối.

**Rủi ro cần kiểm trước khi chốt** (ADR-002 đã nêu): liếc cast của series test vs 2
series train để chắc không chung diễn viên. Rẻ, làm 15 phút, đừng tin vào id diarization.

---

## 2. Media lên Kaggle, hay chạy ở đâu?

### Điều kiện đã thay đổi so với lúc viết `05-scale-plan.md §6`

Scale-plan cho 2 phương án: **A. Kaggle private dataset** hoặc **B. GPU local**.

> **Đã kiểm 2026-09-05: máy này không có GPU NVIDIA.** Chỉ có `Intel(R) Iris(R) Xe
> Graphics` tích hợp. **PA B như mô tả trong scale-plan không tồn tại** trừ khi mua
> phần cứng.

Nhưng scale-plan bỏ sót hai phương án, và một trong hai hoá ra là tốt nhất.

### Bốn phương án

| PA | Chi phí tiền | Wall-clock 120 tập | Phơi nhiễm pháp lý |
|---|---|---|---|
| **A. Kaggle private dataset** | $0 | ~2 tuần (trần 30 GPU-h/tuần) | **Cao** — upload **nguyên tập phim** lên nền tảng bên thứ ba, kèm cam kết mình có quyền |
| **B. Mua GPU local** | $500–2.000+ | vài ngày | Không |
| **C. CPU local (đã có sẵn)** | **$0** | **8–10 ngày chạy liên tục** | **Không** — media không rời máy |
| **D. Thuê GPU rời** (vast.ai / RunPod) | **~$15–35 tổng** | ~1–2 ngày | Thấp–trung bình — VM riêng, không có điều khoản cấp phép nội dung kiểu nền tảng; nhưng host về kỹ thuật vẫn truy cập được đĩa |

**PA C dựa trên số đo có sẵn trong repo** (`scripts/vietnamese-ser/README.md`):
~1,5–2h CPU cho một tập ~45 phút, **resumable, cache theo từng stage** (Ctrl-C rồi chạy
lại vô hại). 120 tập × 1,75h ≈ **210 giờ ≈ 8,75 ngày** chạy liên tục.

**Con số này là điểm mấu chốt:** Kaggle mất ~2 tuần vì bị trần quota 30 GPU-h/tuần chặn,
chứ không phải vì tính toán chậm. CPU local mất ~9 ngày. **Wall-clock ngang nhau** —
nhưng một bên phải upload phim bản quyền, một bên thì không.

### Vì sao rủi ro Kaggle không nhỏ như "dù sao cũng private"

Kaggle yêu cầu người upload **cam kết** nội dung không xâm phạm quyền của bên khác
([Kaggle: rules for datasets](https://www.kaggle.com/general/159857)). Đưa nguyên tập
phim VTV/HTV2 lên là cam kết một điều mình không có quyền cam kết — đó là vấn đề, không
phải chuyện dataset để private hay public. (Tôi **không** đọc được nguyên văn Kaggle
Terms of Use bằng công cụ: trang render bằng JS, WebFetch chỉ lấy được tiêu đề. Nên
phần điều khoản cấp phép cụ thể tôi **không xác nhận** được — hãy tự đọc
[kaggle.com/terms](https://www.kaggle.com/terms) trước khi chọn PA A.)

**Phân biệt quan trọng về mức độ:** upload **nguyên bộ phim** (tác phẩm hoàn chỉnh,
hàng trăm GB) khác hẳn về bản chất với clip **2–3 giây** cắt rời phục vụ nghiên cứu.
Cái sau gần với thông lệ nghiên cứu hơn nhiều.

> ⚠️ **Cần nói thẳng:** hai dataset `viemospeech-pilot` và `viemospeech-ablation-012`
> **đã có** ~1.000 clip audio trên Kaggle rồi (91 MB, private) — trong đó bản
> ablation-012 do chính phiên làm việc này đẩy lên ngày 2026-08-31. Đó là phơi nhiễm ở
> mức **clip**, không phải mức tập phim. Nếu bạn muốn kể cả mức đó cũng không chấp nhận
> được, nói tôi xoá.

### ✅ Khuyến nghị: **C làm mặc định, D khi cần nhanh, không bao giờ A cho tập phim đầy đủ**

1. **P2 extraction chạy CPU local.** Miễn phí, sạch pháp lý, resumable, wall-clock ngang
   Kaggle. Chi phí thật là máy bị chiếm ~9 ngày — chấp nhận được vì nó chạy nền.
2. **Nếu 9 ngày là quá lâu**, thuê GPU rời (~$15–35 cho cả P1). Rẻ hơn nhiều so với mức
   người ta hình dung khi nghe "thuê GPU", và tránh được điều khoản nền tảng.
3. **P4 fine-tune** vẫn cần audio trên GPU ⇒ dùng D. Còn probe trên feature đã cache thì
   chỉ cần upload `.npz`, **không** cần audio — Kaggle vẫn dùng tốt cho việc đó.

**Điều sẽ sai nếu chọn A:** không phải "bị kiện" — mà là một reviewer hỏi "dữ liệu được
xử lý ở đâu" và câu trả lời trung thực làm hỏng phần data-statement của paper. Rủi ro
thật nằm ở chỗ đó.

---

## 3. Quy mô: P1 (3 bộ) hay P2 (6 bộ)?

### Đặt lại câu hỏi

Scale-plan tính quy mô theo **extraction** (P1 = 120 tập → ~18k utterance). Nhưng
`04-…§3` đặt mục tiêu gold là **2–3k utterance nhãn người**, và nhịp label đo được là
**1.193 clip trong ~6 tuần**.

Nghĩa là: extract 18k utterance rồi label 2–3k. **13k–16k utterance sẽ không bao giờ
được gán nhãn.** Chọn P1 hay P2 gần như không đổi được ngày ra paper, vì cái chặn không
phải extraction.

### Extract nhiều hơn mức label được có vô ích không?

Không — nhưng vì một lý do khác với lý do trong scale-plan: **pool lớn cho phép chọn
lớp**. Muốn đạt sàn surprise ≥50 mà chỉ có pool nhỏ thì phải label rất nhiều clip
neutral để vét được vài clip surprise. Pool lớn + gợi ý teacher ⇒ oversample được lớp
hiếm. Đó là giá trị thật của việc extract rộng.

### Phương án

| PA | Nội dung | Nhận xét |
|---|---|---|
| **A. Cam kết P1 (3 bộ/120 tập) ngay** | ~36 GPU-h hoặc ~210 CPU-h | Đúng hướng, nhưng dồn toàn bộ chi phí trước khi biết series 3 có dùng được không |
| **B. Cam kết P2 (6 bộ)** | gấp đôi | Không giải quyết nút thắt nào đang có. Hoãn lại |
| **C. P1 làm mục tiêu, chia nhỏ theo series** | extract series 3 trước (~34 tập ≈ 60 CPU-h ≈ 2,5 ngày) → label tới sàn → quyết tiếp | Chi phí nhỏ, học được sớm |

### ✅ Khuyến nghị: PA C

Giữ **P1 (3 bộ) làm target v2 của design doc** như scale-plan đề xuất — nhưng **đừng
extract 120 tập trước**. Trình tự:

1. Extract **Sống chung với mẹ chồng** (34 tập) → ~60 CPU-h ≈ 2,5 ngày.
2. Label nó tới sàn ADR-002 (ưu tiên lớp hiếm bằng gợi ý teacher).
3. Lúc đó mới biết: yield thật của series mới, nhịp label thật, và test set có đạt sàn
   không. **Rồi mới quyết** có mở bộ thứ tư không.

Đây cũng chính là kỷ luật `002-scale-batch-1` đã ghi sẵn trong danh sách change ứng viên:
*"chạy bộ phim đầu tiên qua kernel: chốt GPU-h/tập thật, yield/tập trên mẫu lớn"*.

---

## 4. Phát hiện xuyên suốt: dialect

`docs/intent/constraints.md §6` cam kết:

> Every utterance carries auto-generated syllable-level tone annotations and **dialect
> metadata (Bắc/Trung/Nam — different tone systems)**.

**Thực tế đo được: 1.215/1.215 clip đều là `north`.** Cam kết ở tầng intent đang chưa
được đáp ứng, và không phải chỉ là chuyện "thiếu đa dạng".

Vì sao nó quan trọng với chính giả thuyết của paper: tiếng Việt Nam Bộ **gộp thanh hỏi
và thanh ngã** — 5 thanh thay vì 6
([1-StopAsia](https://www.1stopasia.com/blog/vietnamese-dialects-a-beginners-guide-to-regional-variations/),
[Vietcetera](https://vietcetera.com/en/from-north-centre-to-south-exploring-vietnams-linguistic-diversity)).
Nếu luận điểm là *thanh điệu và cảm xúc cạnh tranh trên cùng một kênh*, thì một phương
ngữ có **tương phản thanh điệu bị thu hẹp** phải hành xử khác đi một cách đo được. Đó là
một **thí nghiệm tự nhiên**, không phải metadata trang trí.

**Nhưng đừng trộn nó vào test split chính** (xem §1). Đề xuất: series miền Nam
(**Gạo nếp gạo tẻ**, HTV2/Vie Channel, 109 tập) là **bộ thứ tư**, dùng cho một mục
phân tích riêng về dialect-shift — sau khi P1 xong, không phải bây giờ.

---

## Việc cần bạn làm

- [ ] **QĐ1:** duyệt "test = series 3 miền Bắc (Sống chung với mẹ chồng)"? Nếu duyệt,
      cập nhật ADR-002 từ `proposed` → `accepted` kèm series cụ thể.
- [ ] **QĐ2:** duyệt "CPU local cho P2, không đưa tập phim lên Kaggle"? Và cho biết có
      muốn xoá ~1k clip đang nằm trên Kaggle không.
- [ ] **QĐ3:** duyệt "P1 là target, nhưng extract từng series một"?
- [ ] Liếc cast series 3 vs 2 series hiện có (~15 phút) trước khi chốt QĐ1.

## Nguồn

- Nội bộ: `state.db` (đo 2026-09-05) · [ADR-002](../spec/decisions/ADR-002-whole-series-speaker-disjoint-gold.md)
  · [`05-scale-plan.md`](../papers/vietnamese-ser/05-scale-plan.md) ·
  [`constraints.md`](../intent/constraints.md) · `scripts/vietnamese-ser/README.md`
  (thời gian CPU) · [`docs/reports/012/ablation.md`](../reports/012/ablation.md)
- Kaggle: [rules for datasets](https://www.kaggle.com/general/159857) ·
  [Terms of Use](https://www.kaggle.com/terms) *(không đọc được bằng công cụ — cần tự đọc)*
- GPU thuê: [RunPod vs Vast.ai 2026](https://www.spheron.network/blog/gpu-cloud-pricing-comparison-runpod-vs-vastai-2026/)
  · [Cloud GPU providers compared 2026](https://earnifyhub.com/learning-guides/cloud-gpu-providers-compared-runpod-vastai-lambda-2026)
- Phương ngữ: [1-StopAsia](https://www.1stopasia.com/blog/vietnamese-dialects-a-beginners-guide-to-regional-variations/)
  · [Vietcetera](https://vietcetera.com/en/from-north-centre-to-south-exploring-vietnams-linguistic-diversity)
