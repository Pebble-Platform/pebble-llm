# Runbook — chạy một vòng label online

> Quy trình vận hành cho owner. Mọi bước ở đây thực thi safeguard của
> [ADR-005](../../decisions/ADR-005-annotation-streaming-not-release.md) —
> **7 safeguard là cả gói, thiếu một cái là quyết định mất hiệu lực.**
>
> 2026-07-28 · [change 011](README.md)

## Trước khi mở vòng — checklist

- [ ] `qc-protocol.md` đã **đông cứng** (trạng thái `frozen` + ngày + commit).
- [ ] `gold-set.txt` đã dựng (qc-protocol §2.1): chạy
      `scripts/vietnamese-ser/pick_gold_candidates.py`, rồi mở
      **`http://127.0.0.1:8000/gold.html`** để nghe và chốt.
- [ ] `consent.vi.md` **đã điền hết ô trống** (thù lao, người phụ trách, IRB).
- [ ] Mỗi annotator đã **xác nhận consent** trước khi được cấp token.

## 1–2. Token + hàng đợi + thư mời — một lệnh

**Tắt server trước** (ADR-004: chưa có lock 1-writer).

```bash
# xem trước, không ghi gì
.venv-vnser/Scripts/python.exe scripts/vietnamese-ser/invite_annotators.py \
  --annotators ann01,ann02 --dry-run

# làm thật (chạy SAU khi đã có URL ngrok ở bước 4)
.venv-vnser/Scripts/python.exe scripts/vietnamese-ser/invite_annotators.py \
  --annotators ann01,ann02 --n 250 \
  --gold docs/spec/changes/011-online-multi-annotator/gold-set.txt \
  --base-url https://<subdomain>.ngrok.app
```

Script làm 3 việc: tạo token (người đã có thì **giữ nguyên token cũ**, nên link đã gửi
vẫn chạy) → dựng hàng đợi → in **thư mời sẵn kèm link riêng** cho từng người, copy
gửi thẳng.

Chạy lại được an toàn: hàng đợi đã có câu trả lời thì **không bị ghi đè**.

### Vòng qualification trước, vòng chính sau

`invite_annotators.py` dựng **vòng chính**. Vòng qualification (30 slot: 18 gold +
10 thường + 2 bẫy) dựng riêng:

```bash
.venv-vnser/Scripts/python.exe scripts/vietnamese-ser/build_assignments.py \
  --annotators ann01,ann02,ann03,ann04 --qualify \
  --gold docs/spec/changes/011-online-multi-annotator/gold-set.txt
```

Chấm theo §3.1 (`iaa_report.py` bảng QC) → ai đạt mới dựng hàng đợi vòng chính cho
người đó. **Gold của hai vòng rời nhau tự động** (18 đầu cho pretest, phần còn lại
cho vòng chính): dùng lại clip pretest ở vòng chính là đo trí nhớ, không đo việc còn
nghe hay không.

⚠️ `store.assign()` từ chối ghi đè hàng đợi **đã có câu trả lời** — nên sau khi ai đó
làm xong qualification, dựng vòng chính cho họ sẽ bị chặn. Xoá hàng đợi cũ của người
đó trước (hoặc dùng id khác, vd `ann01` → `ann01r`) và **giữ lại dữ liệu qualification**
để chấm.

`tokens.json` nằm trong `data/**` → **gitignored, không bao giờ commit**. Một token
= một người (safeguard #1), không dùng chung. Giữ **bảng ánh xạ `ann01` → tên thật
riêng, ngoài repo** — bản phát hành chỉ có mã giả danh (consent §6).

Cùng một subset cho mọi người (điều làm Fleiss κ hợp lệ), xáo trộn khác nhau từng
người (safeguard #4).

### Gửi kèm gì

Đính kèm **2 file** vào thư mời: `annotator-guideline.vi.md` và `consent.vi.md`
(bản đã điền thù lao + IRB). Thư mời do script in đã nhắc sẵn.

Lần đầu mở link, annotator gặp **màn xác nhận đồng ý**; server **ghi lại** ai đồng ý,
lúc nào, **phiên bản văn bản nào** vào bảng `consent`. Chưa xác nhận thì **không lấy
được clip nào** — chặn ở server, không chỉ giấu trên giao diện. Đây là bằng chứng cho
phần ethics statement của bài báo:

```bash
.venv-vnser/Scripts/python.exe -c "import sys; sys.path.insert(0,'tools/labeler'); \
import store; from pathlib import Path; store.set_root(Path('data/vietnamese-ser/episodes')); \
store.load(); print(store.all_consent())"
```

⚠️ Nếu sửa `consent.vi.md`, **phải tăng `CONSENT_VERSION`** trong `server.py` — nếu
không, bản ghi sẽ trỏ tới một phiên bản văn bản không còn tồn tại.

## 3. Chạy server

```bash
.venv-vnser/Scripts/python.exe tools/labeler/server.py \
  --root data/vietnamese-ser/episodes --no-local-admin
```

**`--no-local-admin` là bắt buộc khi tunnel đang mở.** Không có nó, request loopback
vẫn được admin. Server *đã* chặn tunnel bằng cách phát hiện header `x-forwarded-*`,
nhưng cờ này là lớp thứ hai — dùng cả hai.

Khi bật cờ, chính owner cũng cần token admin trong `tokens.json`.

## 4. Mở tunnel

```bash
ngrok http 8000
```

Gửi cho từng annotator **link riêng của họ**:

```
https://<subdomain>.ngrok.app/rate.html?t=<token-của-người-đó>
```

Token bị xoá khỏi thanh địa chỉ ngay sau khi tải, chỉ còn trong `sessionStorage`
của tab đó.

**Tắt tunnel ngay khi hết phiên làm việc** (safeguard #7). Không để chạy qua đêm.

### Cần biết về ngrok

- **TLS terminate ở edge của ngrok** → traffic audio đi qua hạ tầng bên thứ ba dưới
  dạng **transit**. Khác VPS ở chỗ **không có bản sao thường trú**, nhưng data
  statement phải viết *"streamed via an authenticated tunnel"*, **không** viết
  *"never touched any third-party server"* (ADR-005, phần rủi ro).
- **Chưa verify** (kiểm trước khi mở vòng thật): giới hạn bandwidth của tier đang
  dùng, và **trang cảnh báo chen giữa** của tier free — annotator sẽ gặp mỗi phiên,
  khá khó chịu. Tier trả phí cho domain cố định đáng cân nhắc: link không đổi giữa
  các phiên nên không phải gửi lại link mới mỗi lần.
- Ước lượng băng thông: clip ~5s, 16 kHz mono WAV ≈ 160 KB. 275 slot × 3 người ×
  ~3 lần nghe ≈ **400 MB**. Nghe lại nhiều thì tăng theo.

## 5. Theo dõi trong lúc chạy

```bash
# tiến độ từng người
.venv-vnser/Scripts/python.exe -c "import sys; sys.path.insert(0,'tools/labeler'); \
import store; from pathlib import Path; store.set_root(Path('data/vietnamese-ser/episodes')); \
store.load(); \
print({a: store.progress(a) for a in ['ann01','ann02']})"
```

`data/vietnamese-ser/episodes/access.log` ghi ai nghe clip nào lúc nào
(safeguard #6). **Không công bố.**

⚠️ **Không xem nhãn của annotator trong lúc họ đang làm và đừng phản hồi về nội dung
gán nhãn** — trừ đúng những gì `qc-protocol.md` §4 cho phép (chỉ tiêu chí khách quan).
Góp ý kiểu "clip này chắc là giận chứ nhỉ" là neo nhãn, và làm hỏng cả vòng đo.

## 5b. Sau khi đóng vòng — soi từng clip

`http://127.0.0.1:8000/review.html` — bảng **so nhãn mọi người trên từng clip**:
owner + từng annotator cạnh nhau, ô nào lệch đa số thì tô đỏ, nghe được tại chỗ.
Lọc: `chỉ bất đồng` · `no_agreement` · `có bỏ qua` · `clip lặp` (clip lặp hiện **cả
hai lần gán** của cùng một người — nhìn ra ngay ai tự mâu thuẫn).

Dùng khi κ của một lớp thấp và cần biết **clip mơ hồ thật hay hướng dẫn chưa rõ** —
`iaa_report.py` chỉ trả lời "đồng thuận bao nhiêu", trang này trả lời "họ nói gì về
clip NÀY". Clip đồng thuận tuyệt đối tự xếp xuống cuối.

## 6. Đóng vòng

1. Tắt tunnel.
2. Backup: `VACUUM INTO 'state.db.bak-<ngày>'`.
3. Chấm QC theo `qc-protocol.md` §3 — **theo đúng ngưỡng đã đông cứng**, không
   nới tay vì kết quả không như ý.
4. Chạy báo cáo κ/α (M7).

## Sự cố thường gặp

| Triệu chứng | Nguyên nhân |
|---|---|
| Annotator thấy "Không truy cập được" | token sai / đã đổi `tokens.json` mà chưa restart server |
| Annotator thấy màn owner | thiếu `--no-local-admin`, **hoặc** token bị gán `role: admin` — sửa ngay |
| `/rate/next` trả `seq: null` ngay | chưa dựng hàng đợi cho id đó (bước 2) |
| Nút Nghe không tự phát | trình duyệt chặn autoplay — bấm nút là được, không phải lỗi |
| Reassign báo "already answered" | đúng như thiết kế — hàng đợi có câu trả lời rồi thì không ghi đè |
