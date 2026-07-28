# Runbook — chạy một vòng label online

> Quy trình vận hành cho owner. Mọi bước ở đây thực thi safeguard của
> [ADR-005](../../decisions/ADR-005-annotation-streaming-not-release.md) —
> **7 safeguard là cả gói, thiếu một cái là quyết định mất hiệu lực.**
>
> 2026-07-28 · [change 011](README.md)

## Trước khi mở vòng — checklist

- [ ] `qc-protocol.md` đã **đông cứng** (trạng thái `frozen` + ngày + commit).
- [ ] `gold-set.txt` đã dựng (qc-protocol §2.1).
- [ ] `consent.vi.md` **đã điền hết ô trống** (thù lao, người phụ trách, IRB).
- [ ] Mỗi annotator đã **xác nhận consent** trước khi được cấp token.

## 1. Tạo token

```bash
.venv-vnser/Scripts/python.exe -c "import sys; sys.path.insert(0,'tools/labeler'); import auth, json; \
print(json.dumps({auth.mint(): {'id': f'ann{i:02d}', 'role': 'annotator'} for i in range(1,4)}, indent=2))" \
  > data/vietnamese-ser/episodes/tokens.json
```

`tokens.json` nằm trong `data/**` → **gitignored, không bao giờ commit**. Một token
= một người (safeguard #1). Không dùng chung.

Giữ **bảng ánh xạ `ann01` → tên thật riêng, ngoài repo** — bản phát hành chỉ có mã
giả danh (consent §6).

## 2. Dựng hàng đợi

**Tắt server trước** (ADR-004: chưa có lock 1-writer).

```bash
.venv-vnser/Scripts/python.exe scripts/vietnamese-ser/build_assignments.py \
  --annotators ann01,ann02 --n 250 \
  --gold docs/spec/changes/011-online-multi-annotator/gold-set.txt
```

Bỏ `--dry-run` mới ghi thật. Script **từ chối ghi đè** hàng đợi đã có câu trả lời —
chạy lại không mất việc đã làm.

Xáo trộn khác nhau cho từng người (safeguard #4). Cùng một subset cho mọi người —
đó là điều làm Fleiss κ hợp lệ.

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
