# Bản đồng ý tham gia & Thoả thuận sử dụng dữ liệu — ViEmoSpeech

> Annotator xác nhận văn bản này **một lần, trước khi được cấp quyền truy cập**.
> Bản xác nhận (mã annotator + thời điểm + phiên bản văn bản) lưu trong `state.db`.
>
> Phiên bản 1 · 2026-07-28 · [change 011](README.md) · An toàn dữ liệu:
> [ADR-005](../../decisions/ADR-005-annotation-streaming-not-release.md)

---

## 1. Dự án này là gì

**ViEmoSpeech** là dự án nghiên cứu xây dựng **corpus cảm xúc giọng nói tiếng Việt**
đầu tiên có nhãn đa lớp, chú thích thanh điệu và giấy phép rõ ràng. Dữ liệu được
trích từ phim truyền hình Việt Nam.

Kết quả dự kiến là một **bộ dữ liệu công bố công khai** và các **bài báo khoa học**.
Dự án không nhằm mục đích thương mại.

## 2. Anh/chị được mời làm gì

Nghe các đoạn thoại ngắn (2–10 giây) đã được cắt sẵn và gán ba nhãn: **cảm xúc**
(1 trong 7 loại), **valence** (1–5), **arousal** (1–5). Chi tiết ở
[hướng dẫn gán nhãn](annotator-guideline.vi.md).

Anh/chị **không** cắt, chia, hay sửa audio — công cụ không có chức năng đó.

**Khối lượng dự kiến:** khoảng 250–300 clip cho vòng chính, cộng một vòng làm quen
ngắn trước đó. Ước tính **5–10 giờ**, chia nhỏ tuỳ ý, không có deadline gấp.

## 3. Anh/chị hoàn toàn tự nguyện

- Tham gia là **tự nguyện**. Từ chối không có bất kỳ hậu quả nào.
- Anh/chị có thể **bỏ qua bất kỳ clip nào** mà không cần lý do.
- Anh/chị có thể **dừng bất cứ lúc nào**, không cần giải thích. Phần công đã làm vẫn
  được trả đầy đủ.
- Anh/chị có thể **yêu cầu xoá toàn bộ nhãn của mình** khỏi dự án — bất cứ lúc nào
  **trước khi bộ dữ liệu được công bố**. Sau khi công bố thì về mặt kỹ thuật không
  thu hồi được nữa (dữ liệu đã phát tán công khai); chúng tôi sẽ báo trước thời điểm
  công bố để anh/chị kịp quyết định.

## 4. Cảnh báo về nội dung

Các đoạn audio là **diễn xuất** trong phim truyền hình gia đình/tâm lý. Anh/chị **sẽ**
gặp các cảnh cãi vã gay gắt, quát mắng, khóc, hoảng sợ, đe dọa, và **đau khổ tâm lý
rõ rệt**.

Đây đều là diễn viên diễn, **không phải người thật đang gặp chuyện thật**, và dự án
này **không** nghiên cứu nguy cơ tự hại hay bất kỳ tình trạng lâm sàng nào — nhãn
"đau khổ" trong corpus là chỉ dấu về **biểu cảm diễn xuất**, không phải chẩn đoán.

Dù vậy, nghe liên tục nội dung như trên có thể gây mệt mỏi cảm xúc. Chúng tôi khuyến
nghị **nghỉ ~10 phút sau mỗi ~45 phút** và **không quá ~2 giờ/ngày**. Nếu thấy khó
chịu kéo dài, hãy dừng và nhắn cho người phụ trách.

## 5. Thù lao

- Mức: **[ĐIỀN TRƯỚC KHI GỬI: … VNĐ/giờ]**, trả theo **[giờ / số clip]**.
- Trả **theo phần đã làm**, kể cả khi anh/chị dừng giữa chừng.
- Thời điểm và cách thanh toán: **[ĐIỀN TRƯỚC KHI GỬI]**.

> ⚠️ **Không gửi bản này cho annotator khi các ô trên còn trống.** Bài báo bắt buộc
> phải công bố mức trả và biện minh tính thoả đáng so với mức sống địa phương
> (ARR Responsible NLP checklist) — nên con số phải có thật và được chốt từ đầu.

## 6. Dữ liệu của anh/chị được dùng và công bố ra sao

**Được công bố công khai** (giấy phép CC-BY 4.0), như một phần của bộ dữ liệu:

- các nhãn anh/chị gán (cảm xúc, valence, arousal);
- **mã annotator giả danh** — dạng `ann01`, `ann02`… — **không phải tên thật**;
- thời điểm gán nhãn.

Mã giả danh là bắt buộc về mặt khoa học (mọi nhãn phải truy được về người gán, để
người khác kiểm chứng lại con số đồng thuận). Bảng ánh xạ giữa mã và danh tính thật
**chỉ nằm trên máy của người phụ trách và không bao giờ được công bố**.

**Không bao giờ công bố:** tên, email, hay bất kỳ thông tin nhận dạng nào của
anh/chị; audio; video; transcript đầy đủ.

**Trong bài báo**, nhóm annotator sẽ được mô tả ở dạng gộp (số lượng, khoảng tuổi,
vùng miền, trình độ) — không mô tả cá nhân.

## 7. Thoả thuận sử dụng dữ liệu — phần bắt buộc

Các đoạn audio là **phim có bản quyền của bên thứ ba**. Anh/chị được **nghe** chúng
qua công cụ, **chỉ nhằm mục đích gán nhãn cho dự án này**. Đây không phải là chuyển
giao quyền gì cho anh/chị.

Anh/chị cam kết:

1. **Không tải về, không ghi âm, không quay hoặc chụp màn hình** bất kỳ đoạn audio nào.
2. **Không chia sẻ, gửi lại, hay phát tán** audio dưới bất kỳ hình thức nào.
3. **Không chia sẻ tài khoản, mật khẩu, hay đường link truy cập** cho bất kỳ ai.
4. **Không cố tải hàng loạt** hoặc truy cập ngoài giao diện gán nhãn.
5. **Không giữ lại bản sao nào** sau khi kết thúc; xoá cache trình duyệt nếu được yêu cầu.
6. **Không bàn bạc nội dung gán nhãn cụ thể** với annotator khác trong lúc dự án chạy
   (điều này làm hỏng phép đo đồng thuận — xem hướng dẫn mục 1).

Hệ thống **ghi log** việc ai truy cập clip nào và lúc nào, phục vụ kiểm soát truy cập
và truy xuất nguồn gốc. Log không được công bố.

## 8. Rủi ro và lợi ích

- **Rủi ro:** thấp. Chủ yếu là **mệt mỏi cảm xúc** do nội dung (mục 4) và mỏi tai.
  Không thu thập thông tin nhạy cảm nào về anh/chị.
- **Lợi ích:** thù lao (mục 5); đóng góp vào bộ dữ liệu tiếng Việt mở đầu tiên thuộc
  loại này. Nếu anh/chị muốn, tên có thể được **ghi nhận trong phần cảm ơn** của bài
  báo — **chỉ khi anh/chị chủ động đồng ý riêng**, mặc định là không.

## 9. Xét duyệt đạo đức

**[ĐIỀN TRƯỚC KHI GỬI — chọn đúng một, và nói thật:]**

- [ ] Dự án đã được [tên hội đồng] phê duyệt, mã số […].
- [ ] Dự án đã được xác định là **miễn xét duyệt** bởi [tên hội đồng].
- [ ] **Dự án chưa qua hội đồng đạo đức nào.** Người phụ trách hiện không có kênh
      IRB/hội đồng khả dụng. Điều này sẽ được **nêu thẳng trong bài báo**, không lờ đi.

## 10. Liên hệ

Người phụ trách: **[ĐIỀN: tên · email]**

Mọi thắc mắc về công cụ, hướng dẫn, thù lao, dữ liệu của mình, hoặc muốn rút lui —
liên hệ trực tiếp.

---

## Xác nhận

Bằng việc tích vào ô dưới đây, tôi xác nhận rằng:

- Tôi **đã đọc và hiểu** văn bản này cùng [hướng dẫn gán nhãn](annotator-guideline.vi.md).
- Tôi hiểu nội dung có thể gây **mệt mỏi cảm xúc** và tôi **được quyền dừng bất cứ lúc nào**.
- Tôi đồng ý để **nhãn tôi gán + mã giả danh + thời điểm** được công bố công khai
  theo giấy phép CC-BY 4.0.
- Tôi **cam kết tuân thủ Thoả thuận sử dụng dữ liệu ở mục 7**, đặc biệt là không tải
  về, không ghi màn hình, và không chia sẻ audio hay quyền truy cập.
- Tôi **từ 18 tuổi trở lên**.

☐ **Tôi đồng ý tham gia.**

*(Hệ thống lưu: mã annotator · thời điểm xác nhận · phiên bản văn bản này.)*
