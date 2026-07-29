# Giao thức QC & tính κ — **pre-registered**

> **Văn bản này phải được commit và ĐÔNG CỨNG trước khi annotator gán nhãn đầu tiên.**
> Sau thời điểm đó, mọi thay đổi ngưỡng/tiêu chí phải ghi thành một mục sửa đổi có
> ngày tháng ở cuối file, kèm lý do — **không sửa tại chỗ**. Bài báo dẫn commit hash
> của bản đông cứng.
>
> Phiên bản 1 · 2026-07-28 · [change 011](README.md) · trạng thái: **draft — CHƯA đông cứng**

## 0. Vì sao phải pre-register

Nếu loại annotator **sau khi** nhìn thấy dữ liệu, κ báo cáo sẽ tự phồng lên theo
kiểu lập luận vòng tròn: loại người bất đồng → người còn lại đồng thuận cao → "corpus
đáng tin". Con số đó vô giá trị.

Nên: **tiêu chí loại phải khách quan, có số cụ thể, và chốt trước.** Mọi thứ dưới đây
được thiết kế để trả lời đúng một câu hỏi — *người này có thật sự nghe và trả lời
nghiêm túc không?* — chứ **không** phải *người này có nghe giống chúng tôi không?*

## 1. Điều tuyệt đối không được làm

> **KHÔNG BAO GIỜ loại một annotator vì họ bất đồng với đa số, với owner, hay với
> annotator khác.**

Bất đồng **chính là đại lượng đang đo**. Loại người vì bất đồng = đo cái mình vừa tự
tạo ra. Điều này áp dụng cả sau khi thấy kết quả và cả khi κ thấp hơn mong đợi.

Nếu κ thấp: **báo cáo κ thấp**. Đó là một kết quả hợp lệ và có ý nghĩa khoa học
(thoại phim tự nhiên vốn mơ hồ). Ba corpus đã xuất bản và được trích dẫn rộng rãi
nằm ở κ 0.34 (MELD), 0.411 (MSP-Podcast), α 0.42 (CREMA-D).

## 2. Ba công cụ QC — đều khách quan

### 2.1 Gold item — *"có nghe không?"*

**Cách dựng gold set (bắt buộc theo đúng thứ tự này):**

1. Lọc các clip mà **owner, teacher Opus, và teacher Sonnet đều gán CÙNG một emotion**
   (đồng thuận ba chiều).
2. Owner **nghe lại từng clip** và chỉ giữ những clip mình thấy **hiển nhiên, không
   phân vân**.
3. Lấy ~**40 clip**, trải đủ 7 lớp trong khả năng cho phép và cả 2 series.

**Vì sao 40 chứ không phải 24 (sửa 2026-07-29):** gold dùng ở **hai nơi** — 18 clip
trong vòng qualification (§3.1) và ~22 clip rải trong vòng chính (§3.2 R1) — và
**hai tập phải RỜI NHAU**. Nếu vòng chính dùng lại clip annotator đã gặp lúc
qualification thì R1 đang đo **trí nhớ**, không đo việc họ còn nghe hay không. Con số
24 ở bản đầu là tính thiếu. `build_assignments.py` cắt tự động: 18 đầu cho pretest,
phần còn lại cho vòng chính, và cảnh báo nếu không đủ.

Nguồn ứng viên: `pick_gold_candidates.py --per-class 9` → **58 ứng viên** (`surprise`
chỉ có 4 trên toàn corpus — trần cứng, xem bảng dưới). Nghe rồi giữ lại ~40.

| lớp | toàn corpus | đồng thuận 3 chiều | ứng viên |
|---|--:|--:|--:|
| joy | 151 | 70 | 9 |
| sadness | 73 | 16 | 9 |
| anger | 160 | 105 | 9 |
| fear_anxiety | 81 | 30 | 9 |
| **surprise** | 40 | **4** | **4** ← trần cứng |
| disgust | 66 | 10 | 9 |
| neutral | 227 | 143 | 9 |

**Vì sao phải qua bước lọc này:** gold **không phải** "nhãn đúng" — nhãn của owner
không phải sự thật nền độc lập (phim truyền hình tìm được không có nhãn do đạo diễn
gán, khác THAI-SER). Gold ở đây chỉ có nghĩa là **"clip dễ tới mức ai nghe nghiêm
túc cũng ra thế"**. Vì vậy chúng chỉ dùng để bắt người **không nghe**, không dùng để
bắt người **nghe khác**.

Trong hướng dẫn và khi trao đổi với annotator, gọi những clip này là **"mốc neo"**,
**không** gọi là "đáp án đúng".

### 2.2 Clip trùng lặp — *"có nhất quán không?"*

**10%** số clip trong hàng đợi mỗi annotator được **lặp lại lần thứ hai**, đặt cách
lần đầu **ít nhất 50 clip**. Annotator được báo trước là có clip lặp (hướng dẫn §7),
nhưng không biết clip nào.

Đo: tỉ lệ hai lần gán **trùng đúng nhãn emotion**.

### 2.3 Sàn thời gian — *"có thật sự nghe hết không?"*

Một lượt gán bị đánh dấu **quá nhanh** nếu tổng thời gian phát audio của clip đó
**nhỏ hơn độ dài clip**. Không nghe hết mà đã chấm thì về mặt vật lý không thể đã
nghe xong.

Đây là biến thể của logic trapping question trong ITU-T P.808. Server **log thời gian
phát**, không chỉ thời gian ở trên màn hình (annotator có thể mở tab rồi đi pha trà —
điều đó vô hại và không bị tính).

### 2.4 Trap trong vòng qualification

Vòng qualification có **2 clip bẫy**: lấy từ các clip **owner đã loại** với lý do
`noise` hoặc `bad_cut` (hiện có **17 clip** như vậy) — clip mà gán bất kỳ cảm xúc nào
cũng là đoán bừa. Đáp án đúng = **bỏ qua**. Người chấm một cảm xúc cho tiếng ồn là
người đang click bừa. `build_assignments.py --qualify` tự rút từ pool này.

## 3. Ngưỡng — chốt cứng

### 3.1 Vòng qualification (30 clip: 18 gold + 10 thường + 2 trap)

Đạt **khi và chỉ khi cả ba**:

| # | Tiêu chí | Ngưỡng |
|---|---|---|
| Q1 | Trùng emotion với gold | **≥ 9/18 (50%)** |
| Q2 | Bẫy được bỏ qua đúng | **≥ 1/2** |
| Q3 | Lượt gán "quá nhanh" (§2.3) | **≤ 20%** |

Ngưỡng 50% trên thang 7 lớp: xác suất ngẫu nhiên ~14%. Bar này bắt người click bừa,
**không** bắt người có cảm nhận khác. (Tham chiếu: THAI-SER dùng pretest có câu bẫy
ẩn, tỉ lệ đậu 56%.)

**Không đạt** → không nhận vào vòng chính; **vẫn trả công đầy đủ cho thời gian đã bỏ
ra**; dữ liệu qualification của người đó **không vào corpus**. Số người trượt và lý do
**được báo cáo trong bài báo**.

### 3.2 Trong vòng chính

| # | Tiêu chí | Ngưỡng loại |
|---|---|---|
| R1 | Trùng emotion với gold rải trong hàng đợi (~8% số clip) | **< 40%** |
| R2 | Tự nhất quán trên clip lặp (§2.2) | **< 40%** |
| R3 | Lượt gán "quá nhanh" (§2.3) | **> 25%** |
| R4 | Tỉ lệ dùng nút "bỏ qua" | **> 40%** |

Chạm **bất kỳ** ngưỡng nào → xử lý theo §4. R1–R3 bắt hành vi không nghiêm túc; R4
bắt việc dùng "bỏ qua" để né việc (nhưng ngưỡng đặt cao — bỏ qua là hành vi được
khuyến khích khi clip thật sự hỏng).

**Ngưỡng R1 (40%) thấp hơn Q1 (50%) có chủ đích:** vòng chính dài hơn, mệt hơn, và ta
muốn khoan dung hơn với dao động tự nhiên.

## 4. Khi ai đó chạm ngưỡng

Theo THAI-SER/MSP-Podcast: **ưu tiên đào tạo lại, không loại thẳng.**

1. **Lần 1** — owner báo riêng, chỉ ra vấn đề cụ thể (vd "nhiều clip chấm trước khi
   nghe hết"), gửi lại hướng dẫn, **cho làm lại phần đã bị đánh dấu**. Không phạt,
   vẫn trả công.
2. **Lần 2 (vẫn chạm ngưỡng sau khi làm lại)** — dừng người đó khỏi vòng. Trả công
   đầy đủ phần đã làm.

**Nếu phải loại ai:** bài báo **bắt buộc** báo cáo (a) đã loại mấy người, (b) chạm
tiêu chí khách quan nào, (c) **κ tính cả hai cách — có và không có dữ liệu của người
bị loại**. Nếu hai con số lệch nhiều, con số *bao gồm* mới là con số trung thực và
phải nêu trước.

## 5. Tính κ/α — quy tắc chốt trước

### 5.1 Tập clip đưa vào tính

Chỉ các clip trong **tập reliability** (~250 clip phân tầng), **loại trừ**:

- **clip gold** — chúng được chọn *vì* dễ, đưa vào sẽ làm κ phồng lên một cách giả tạo;
- **lần gán thứ hai của clip lặp** — chỉ giữ lần đầu (nếu không, một clip có trọng số đôi);
- clip mà **≥2/3 rater bấm "bỏ qua"** — không đủ nhãn để so.

Clip mà **đúng 1 rater** bỏ qua: giữ lại, xử lý như **dữ liệu khuyết** (Krippendorff α
xử lý được; với Fleiss κ thì báo cáo riêng phần này — xem 5.2).

### 5.2 Thống kê báo cáo

| Nhãn | Thống kê | Ghi chú |
|---|---|---|
| emotion (7 lớp) | **Fleiss' κ** | so sánh được với IEMOCAP/MELD/MSP-Podcast. Cần rater đầy đủ → tính trên tập clip đủ 3 nhãn |
| emotion (7 lớp) | **Krippendorff's α (nominal)** | báo **song song** — xử lý được clip khuyết, nên dùng được toàn bộ tập |
| valence | **Krippendorff's α (ordinal)** | thang 1–5 có thứ bậc. **Không** dùng ICC/CCC |
| arousal | **Krippendorff's α (ordinal)** | như trên |

Báo **cả κ lẫn α nominal** cho emotion là cố ý: nếu hai số lệch nhau đáng kể thì
chính khoảng lệch đó nói lên ảnh hưởng của dữ liệu khuyết, và giấu đi là không trung thực.

### 5.3 Phân tách bắt buộc — điểm quan trọng nhất của giao thức này

**Vấn đề:** vòng qualification sàng annotator bằng mức trùng khớp với **gold do owner
adjudicate**. Dù gold đã lọc để chỉ còn clip hiển nhiên (§2.1), việc sàng lọc này
**vẫn ưu tiên nhẹ những người nghe giống owner**. Nên κ(owner, annotator) **bị thổi
lên bởi chính cách tuyển**, không thể coi là hoàn toàn độc lập.

**Xử lý — báo cáo tách bạch, không gộp:**

1. **κ giữa các annotator mới với nhau** (`ann01` ↔ `ann02`) — **con số headline**.
   Hai người này được tuyển độc lập với nhau, không ai neo vào ai.
2. **κ giữa owner và từng annotator** — báo riêng, **kèm cảnh báo rõ** rằng nó chịu
   ảnh hưởng của sàng lọc qualification.
3. **κ ba chiều (Fleiss, cả 3 rater)** — báo, nhưng phải đọc kèm cảnh báo ở (2).

Bài báo nêu **(1) trước tiên** và nói thẳng vì sao. Đây là chỗ dễ tự lừa mình nhất
trong cả giao thức.

### 5.4 Nhãn-của-record (dùng cho corpus, không phải cho κ)

- **emotion:** đa số (≥2/3). Cả 3 khác nhau → gán bucket **`no_agreement`**, giữ lại
  trong corpus có gắn cờ (theo MSP-Podcast), **không xoá âm thầm**.
- **valence / arousal:** **trung bình cộng** các nhãn hiện có. Ghi kèm **độ lệch chuẩn**
  làm chỉ dấu độ mơ hồ per-clip.
- **Không dùng EWE** (evaluator-weighted estimator): cần pool rater lớn, ổn định để
  ước lượng trọng số tin cậy; ở N=3 là không kiểm chứng được. Bản MSP-Podcast 2025
  hiện cũng dùng plurality + mean.

### 5.5 Bắt buộc báo cáo, kể cả khi khó coi

- Tỉ lệ `no_agreement` (nếu cao → corpus mơ hồ, đó là phát hiện, không phải thất bại).
- Tỉ lệ bỏ qua theo từng lý do.
- κ **theo từng lớp** — sẽ có lớp rất thấp (nghi ngờ `surprise`: toàn corpus chỉ có
  39 clip; và `disgust` vốn khó ở mọi corpus).
- **Không lọc bỏ clip thấp đồng thuận để nâng α.** THAI-SER làm thế (cắt ở 0.71, bỏ
  ~49% clip, α 0.413 → 0.692); repo này **đã tự khuyến nghị không copy**
  (`docs/papers/vietnamese-ser/11-thai-ser-corpus.md:230-233`) vì corpus nhỏ và lớp
  hiếm đã mỏng. Nếu sau này vẫn muốn báo số đã lọc, phải báo **cả hai** và nêu số thô trước.

## 6. Ngưỡng "đạt" cho chính κ

**Không có ngưỡng đạt/trượt.** κ là kết quả cần báo cáo, không phải bài kiểm tra cần qua.

Để đối chiếu khi viết bài: MELD κ 0.34 · MSP-Podcast κ 0.411 (V α 0.508, A α 0.441) ·
CREMA-D α 0.42 (diễn xuất — gần domain nhất) · THAI-SER α thô 0.413 · IEMOCAP κ
0.27–0.48 tuỳ subset. **Vùng ~0.35–0.55 là bình thường** cho lĩnh vực này. **Không**
áp ngưỡng 0.667/0.8 của Krippendorff — không corpus SER nào ở trên đạt nổi.

## 7. Thủ tục đông cứng

1. Owner rà soát và chốt mọi con số ở §3.
2. Điền thù lao ở [consent.vi.md §5](consent.vi.md) và mục xét duyệt đạo đức §9.
3. Dựng gold set theo §2.1 (`pick_gold_candidates.py` → nghe & chốt ở `/gold.html`
   → `gold-set.txt`). **Nhắm giữ ≥40 clip** để cắt được 18 + 22 rời nhau; dưới 33 thì
   `build_assignments.py` sẽ cảnh báo vòng chính còn quá ít neo.
4. Commit tất cả. **Đổi trạng thái file này thành `frozen` + ghi ngày.**
5. **Từ lúc này mới được mời annotator.**

Bài báo dẫn commit hash của bước 4.

## Sửa đổi sau khi đông cứng

*(chưa có — mọi thay đổi sau khi đông cứng ghi vào đây, kèm ngày + lý do, không sửa ở trên)*
