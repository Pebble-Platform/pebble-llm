# Change 014 — Vòng soát gold mù nhãn (`gold.html`: người soát tự chọn)

**Status:** **implemented (2026-09-11)** — code đã land, chưa chạy vòng nào.
**Goal:** bỏ neo nhãn ở màn soát gold. Người soát **tự chọn** emotion từ audio trước,
nhãn owner chỉ được lộ ra **sau khi họ đã chốt**; metadata vẫn hiển thị readonly như cũ
nhưng **sửa được khi sai**.

## Vì sao

[Change 012](../012-label-quality-ablation/README.md) đã ghi thẳng nợ này:

> Vòng review **bị neo**: vyphan thấy nhãn owner trước khi trả lời → nhánh B không phải
> "ý kiến thứ hai độc lập", mà là "owner + 465 lần phân xử". […] **không** sinh ra
> κ human–human.

[ADR-001](../../decisions/ADR-001-blind-gold-annotation.md) bị supersede, nhưng điều
(1) của nó còn sống nguyên: **"không pre-fill — human luôn tự quyết"**. `gold.js` trước
change này pre-fill **cả 6 trường** từ nhãn owner, nên màn soát đang đi ngược đúng
nguyên tắc đó.

## Luồng mới — hai chặng

| | Chặng 1 · chọn nhãn | Chặng 2 · soát thông tin |
|---|---|---|
| Audio + transcript | hiện | hiện |
| Giới tính · Tuổi · Vùng miền | hiện, **readonly** | hiện, readonly + nút **Sửa** |
| **Emotion** | **7 lựa chọn hiện hết cùng lúc**, chưa chọn gì; nhãn owner **không có mặt** | đã chốt, **khoá lại** (không đổi được nữa) |
| **Valence · Arousal** | **không tồn tại trên máy người soát** | hiện readonly + nút **Sửa** |
| Nút | **Xác nhận nhãn** · Loại | **Lưu** · **Sửa** · Loại |

Guard "phải nghe hết audio mới trả lời được" (`GOLD_HEARD`) giữ nguyên — càng quan trọng
hơn khi không còn nhãn mồi để đoán theo.

### Vì sao V/A phải giấu, và giấu ở server

Valence/Arousal **là hình chiếu của phán đoán emotion**: thấy `valence = 1 · rất tiêu cực`
thì `joy` coi như bị loại trước khi kịp nghe. Giấu emotion mà vẫn hiện V/A thì cái neo
vẫn còn nguyên, chỉ đổi đường đi.

Việc giấu làm ở **server**, không phải bằng CSS: `GET /gold-review/next` **không gửi**
`emotion`/`valence`/`arousal` xuống trình duyệt. Chúng chỉ được trả về ở
`POST /gold-review/commit/<key>` — sau khi người soát đã chốt nhãn của chính mình. Một
tấm rèm phủ lên dữ liệu mà trình duyệt đã cầm trong tay thì **không phải là bảo đảm**;
đây là cùng lập luận đã dùng cho consent gate ở [change 011](../011-online-multi-annotator/RUNBOOK.md)
("chặn ở server, không chỉ giấu trên giao diện").

Đổi nhãn sau khi chốt cũng bị chặn ở server, không chỉ bằng việc disable nút: `POST
/gold-review/item/<key>` từ chối nếu `emotion` khác với cái đã commit.

## Hợp đồng dữ liệu — giữ nguyên hình dạng, chỉ đổi *ai* tính `agreed`

`gold-reviews/<user>.json` giữ nguyên schema (`key · agreed · rejected · reject_reason ·
original · answer · ts`), nên `build_kaggle_gold.py --reviews` **không phải sửa**.

| | Trước | Sau |
|---|---|---|
| `agreed` | client khẳng định, server chặn 400 nếu khẳng định sai | **server tự tính** = `answer == original` (cả 6 trường) |
| Guard `"agreed answer must keep original values"` | cần, vì client tự khai | **bỏ** — không còn client nào khai |

Nghĩa của `agreed` **không đổi** (vẫn là "người soát để nguyên toàn bộ giá trị owner"),
nên số của 012 vẫn đọc được theo đúng cách cũ. Đồng thuận **riêng phần emotion** — đại
lượng liên quan tới κ — suy ra được từ `original.emotion` vs `answer.emotion`, cả hai đã
lưu sẵn: **không thêm trường mới**.

`GOLD_COMMITTED` sống trong RAM như `GOLD_HEARD`: restart server giữa chừng thì clip đang
làm dở phải nghe + chốt lại. Chấp nhận được, và giống hệt hành vi sẵn có của `GOLD_HEARD`.

## Văn bản gửi người soát

| File | Việc |
|---|---|
| [`huong-dan-soat-gold.vi.html`](huong-dan-soat-gold.vi.html) → `huong-dan-soat-gold.vi.pdf` | Hướng dẫn thao tác **1 trang A4**: đăng nhập · 5 bước mỗi clip · 7 nhãn · 2 thang điểm · khi nào bấm Loại. Đính kèm cùng username/password khi mời. |

Nguồn là HTML; PDF render bằng Chrome headless — sửa HTML xong phải render lại:

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless --disable-gpu --no-pdf-header-footer `
  --print-to-pdf="docs\spec\changes\014-blind-gold-review\huong-dan-soat-gold.vi.pdf" `
  "file:///C:/Users/phat.nguyen/Documents/Research/Pebble/pebble-llm/docs/spec/changes/014-blind-gold-review/huong-dan-soat-gold.vi.html"
```

Định nghĩa đầy đủ 7 nhãn vẫn nằm ở [`annotator-guideline.vi.md`](../011-online-multi-annotator/annotator-guideline.vi.md)
(change 011) — trang này chỉ là thao tác, không thay thế nó. Khác biệt phải biết: guideline
011 viết cho `rate.html` (**không** có transcript); màn soát gold **có** hiện câu thoại.

## Nợ đã biết / giới hạn

- **Transcript vẫn hiện.** `rate.html` mù hoàn toàn (không transcript, không gợi ý);
  `gold.html` hiện `subtitle`. Lời thoại là gợi ý ngữ nghĩa mạnh — khác biệt này phải
  nói rõ nếu hai nguồn nhãn được đặt cạnh nhau trong paper.
- **Không gộp được với vòng 2026-08 của vyphan.** Hai vòng khác giao thức ⇒ `agreed` của
  chúng không cùng nghĩa vận hành. 012 đã đông cứng, giữ nguyên cách hiểu cũ.
- **Chạy lại trên cùng queue phải dùng user khác.** `/gold-review/next` bỏ qua mọi key đã
  có trong `gold-reviews/<user>.json`, nên `vyphan` mở lại sẽ thấy "đã xong" ngay.
- **Đường đọc κ:** `iaa_report.py` vẫn chỉ đọc bảng `assignments`; κ của vòng soát này
  đọc bằng `scripts/vietnamese-ser/gold_review_kappa.py` → `docs/reports/014/kappa.md`
  (vòng `nhinguyen` 2026-09-23: κ emotion 0.513, n = 343).

## Phạm vi

**Trong:** `gold.html` · `gold.js` · route `/gold-review/*` trong `server.py`.

**Ngoài:** `rate.html` (đã mù sẵn) · đường đọc κ từ `gold-reviews/*.json` · merge kết quả
soát vào `state.db` (adjudicate là việc riêng).

## Đã đổi

| File | Việc |
|---|---|
| `tools/labeler/server.py` | `/gold-review/next` lọc bỏ `emotion`/`valence`/`arousal` · route mới `POST /gold-review/commit/{key}` trả V/A sau khi chốt · `agreed` tự tính · `GoldReviewIn.agreed` bỏ |
| `tools/labeler/gold.js` | luồng 2 chặng; emotion là 7 nút, không prefill; nhãn khoá sau commit (kể cả khi nghe lại audio); nút **Sửa** mở khoá metadata |
| `tools/labeler/gold.html` | lưới 7 nút emotion thay `<select>` · khối V/A ẩn tới khi chốt · nút Đồng ý/Không đồng ý → **Xác nhận nhãn** + **Lưu** + **Sửa** |
| `tools/labeler/SPEC.md` | mô tả `/gold.html` viết lại cho đúng thực tế (màn soát có login, không phải màn chốt gold set cũ) |

Kiểm bằng smoke test trên root tạm (8/8 pass): `/next` không lộ emotion lẫn V/A · lưu khi
chưa nghe → 400 · lưu khi chưa chốt → 400 · commit trả đúng V/A của owner · đổi nhãn sau
khi chốt → 400 · `agreed` tính đúng cả hai chiều.
