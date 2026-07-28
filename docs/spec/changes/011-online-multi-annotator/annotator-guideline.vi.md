# Hướng dẫn gán nhãn cảm xúc — ViEmoSpeech

> Văn bản này là **hướng dẫn chính thức** cho annotator. Bài báo sẽ **đăng nguyên
> văn** hướng dẫn này (yêu cầu công bố của ARR Responsible NLP checklist) — nên nó
> phải khớp đúng những gì anh/chị thực sự được yêu cầu làm.
>
> Phiên bản 1 · 2026-07-28 · [change 011](README.md)

## 1. Việc của anh/chị là gì

Nghe một đoạn thoại ngắn (2–10 giây) cắt từ phim truyền hình Việt Nam, rồi trả lời
**ba câu hỏi**: cảm xúc nào, tích cực hay tiêu cực, và mạnh hay bình lặng.

Chỉ vậy. Anh/chị **không** cắt, không chia, không sửa đoạn audio nào — công cụ
không cho phép và cũng không cần.

### Điều quan trọng nhất, đọc kỹ

Chúng tôi hỏi **cảm xúc anh/chị NGHE THẤY**, không hỏi "cảm xúc đúng là gì".

Không có đáp án đúng nào được giấu sẵn để anh/chị đoán. Đây là phim — diễn viên
đang diễn, và điều chúng tôi cần đo chính là **người nghe bình thường tri giác
được gì**. Nếu anh/chị nghe ra "giận dữ" mà người khác nghe ra "ghê tởm", **cả hai
đều không sai** — chính khoảng chênh đó là dữ liệu chúng tôi cần.

Vì vậy:

- **Đừng cố đoán xem người khác sẽ chọn gì.** Chọn cái anh/chị thật sự nghe thấy.
- **Đừng cố đoán "ý đồ của người ra đề".** Không có ý đồ nào cả.
- **Đừng tra cứu, đừng bàn với annotator khác.** Nếu anh/chị bàn bạc rồi thống nhất,
  con số chúng tôi đo được sẽ thành vô nghĩa và cả vòng label phải bỏ đi.

## 2. Nghe giọng trước, đọc chữ sau

Đây là corpus về **giọng nói**. Tín hiệu chính là **cách nói**: ngữ điệu, cường độ,
nhịp, giọng run/nghẹn/gắt, tiếng thở, tiếng cười, tiếng khóc.

Công cụ **không hiển thị transcript**. Đó là cố ý — chữ viết dễ kéo phán đoán của
anh/chị về phía **nội dung câu nói** thay vì **cách nó được nói ra**. Một câu
"không sao đâu" có thể là bình thản, có thể là đang cố nén khóc; chỉ giọng mới
phân biệt được.

Nghe lại bao nhiêu lần cũng được. Không có giới hạn thời gian.

## 3. Câu hỏi 1 — Cảm xúc (chọn 1 trong 7)

Chọn cảm xúc **chủ đạo của người nói**. Nếu đoạn có nhiều hơn một người, lấy cảm
xúc **nổi trội của cả đoạn**.

| Nhãn | Phím | Nghĩa | Dấu hiệu trong giọng |
|---|---|---|---|
| **joy** — vui | `1` | Vui, thích thú, hào hứng, âu yếm, trêu đùa | Cười, giọng nhẹ và cao hơn, nhịp nhanh, ngữ điệu lên |
| **sadness** — buồn | `2` | Buồn, thất vọng, tủi thân, đau lòng, nản | Giọng trầm, chậm, nhỏ dần, nghẹn, khóc, thở dài |
| **anger** — giận | `3` | Giận, cáu, quát mắng, gắt gỏng, đe dọa | To, gắt, nhấn mạnh từng từ, nhịp dồn, giọng căng |
| **fear_anxiety** — sợ/lo | `4` | Sợ hãi, hoảng loạn, lo lắng, bồn chồn, van xin | Run, hụt hơi, nói nhanh và cao, ngập ngừng, líu |
| **surprise** — bất ngờ | `5` | Ngạc nhiên, sững sờ, không tin nổi | Bật lên đột ngột, cao vống, ngắt quãng, "hả?", "gì cơ?" |
| **disgust** — ghê tởm | `6` | Ghê tởm, khinh bỉ, chán ghét, mỉa mai cay độc | Giọng kéo dài khinh khỉnh, mũi, "xì", cười nhạt mỉa |
| **neutral** — trung tính | `7` | Nói chuyện bình thường, không màu cảm xúc rõ | Đều, không nhấn, kể việc, hỏi đáp thông thường |

### Quy tắc khi phân vân

- **Giận vs ghê tởm:** giận là *bùng ra, hướng vào việc/người đang xảy ra*; ghê tởm
  là *hạ thấp, khinh, đẩy ra xa*. Mỉa mai cay độc thường là **disgust**.
- **Sợ vs buồn:** sợ hướng về *chuyện sắp xảy ra* (căng, gấp); buồn hướng về *chuyện
  đã xảy ra* (chùng, chậm).
- **Bất ngờ** hiếm khi đứng một mình lâu — nếu sau cú sững sờ là giận hoặc vui rõ
  rệt và chiếm phần lớn đoạn, chọn cảm xúc đó.
- **neutral không phải "thùng rác".** Chỉ chọn neutral khi giọng **thật sự** không
  màu cảm xúc, chứ không phải khi anh/chị lười phân vân. Nhưng cũng đừng ngại chọn
  neutral — thoại phim có rất nhiều câu bình thường thật.
- **Vẫn không quyết được?** Chọn cái **gần nhất** và đi tiếp. Đừng ngồi lâu một clip.
  Sự phân vân của anh/chị là thông tin hợp lệ, nó sẽ hiện ra trong số liệu.

## 4. Câu hỏi 2 — Valence (tích cực ↔ tiêu cực), thang 1–5

Người nói đang cảm thấy **dễ chịu hay khó chịu**?

| | |
|---|---|
| **1** | Rất tiêu cực — đau đớn, tuyệt vọng, căm giận, ghê tởm tột độ |
| **2** | Tiêu cực — buồn, bực, lo, khó chịu |
| **3** | Trung tính — không nghiêng bên nào |
| **4** | Tích cực — dễ chịu, vui vẻ, ấm áp |
| **5** | Rất tích cực — hạnh phúc, phấn khích, sung sướng |

## 5. Câu hỏi 3 — Arousal (bình lặng ↔ kích động), thang 1–5

Người nói đang ở mức **năng lượng/kích hoạt** nào? Câu hỏi này **độc lập** với câu
trên: có thể rất tiêu cực mà rất bình lặng (tuyệt vọng, buông xuôi → valence 1,
arousal 1), cũng có thể rất tích cực mà rất kích động (reo hò → valence 5, arousal 5).

| | |
|---|---|
| **1** | Rất bình lặng — thều thào, lịm đi, buông xuôi |
| **2** | Bình lặng — nói khẽ, chậm, đều |
| **3** | Trung bình — hội thoại bình thường |
| **4** | Kích động — nói to/nhanh, căng, gấp |
| **5** | Rất kích động — gào, thét, hoảng loạn, cuống |

> **Đừng để hai thang dính vào nhau.** Sai lầm hay gặp nhất: cứ tiêu cực là cho
> arousal cao. Buồn sâu thường là valence 1–2 **và arousal 1–2**.

## 6. Khi clip không dùng được — nút "bỏ qua"

Có nút **⊘ bỏ qua** kèm lý do. Dùng khi:

- **không nghe rõ** — nhạc/tiếng ồn át giọng, méo tiếng, quá nhỏ;
- **nhiều người nói** — có từ 2 người trở lên và không tách được ai là chính;
- **cắt hỏng** — cụt đầu/cụt đuôi tới mức không còn nghe ra cảm xúc;
- **không có tiếng nói** — chỉ nhạc, tiếng động, im lặng.

**Bỏ qua không phải là thất bại**, và không ảnh hưởng gì tới đánh giá anh/chị. Ngược
lại: **đoán bừa một clip không nghe được mới là thứ làm hỏng dữ liệu.** Thà bỏ qua.

Nhưng đừng dùng nó để né những clip *khó phân vân* — chỉ dùng khi clip thật sự
không nghe được. Clip mơ hồ nhưng nghe rõ thì vẫn chọn nhãn gần nhất (mục 3).

## 7. Cách làm việc

- **Nghỉ giải lao.** Tai mệt là nhãn kém đi rõ rệt. Khuyến nghị nghỉ ~10 phút sau
  mỗi ~45 phút, và **không làm quá ~2 tiếng một ngày**. Không có deadline gấp.
- **Không cần làm liền một mạch.** Đăng nhập lại là tiếp đúng chỗ đang dở.
- **Thứ tự clip đã được xáo trộn** có chủ đích — anh/chị sẽ không nghe các đoạn
  theo mạch phim. Đó là cố ý (tránh việc mạch truyện kéo phán đoán, và là một yêu
  cầu về bản quyền), không phải lỗi.
- **Có clip lặp lại.** Một số clip sẽ xuất hiện hai lần cách xa nhau. Cứ nghe và
  chọn lại bình thường — **đừng cố nhớ lần trước đã chọn gì**. Đây là phép kiểm tra
  tính nhất quán và nó chỉ có ý nghĩa khi anh/chị trả lời tự nhiên.

## 8. Lưu ý về nội dung

Đây là phim truyền hình gia đình/tâm lý Việt Nam. Anh/chị **sẽ** gặp các đoạn diễn
tả cãi vã gay gắt, quát mắng, khóc lóc, hoảng sợ, đe dọa, và đau khổ tâm lý rõ rệt.

Tất cả đều là **diễn xuất trong phim**, không phải người thật đang gặp chuyện thật.
Dù vậy, nghe liên tục những đoạn như vậy vẫn có thể gây mệt mỏi hoặc khó chịu.

**Anh/chị được quyền dừng bất cứ lúc nào**, bỏ qua bất kỳ clip nào khiến mình không
thoải mái (dùng nút bỏ qua), hoặc rút khỏi dự án hoàn toàn — không cần giải thích lý
do, và không ảnh hưởng tới phần công đã làm. Nếu thấy khó chịu kéo dài, nhắn cho
người phụ trách.

## 9. Bảo mật — bắt buộc

Các đoạn audio là **phim có bản quyền**. Anh/chị được nghe **chỉ để gán nhãn**, theo
thoả thuận đã ký ([consent.vi.md](consent.vi.md)):

- **Không tải về, không ghi âm, không quay/chụp màn hình.**
- **Không chia sẻ** link, tài khoản, hay bất kỳ đoạn audio nào cho ai khác.
- Tài khoản là **của riêng anh/chị**, không dùng chung.

## 10. Nhãn của anh/chị được dùng làm gì

Nhãn anh/chị gán, kèm **mã annotator (dạng `ann01`, không phải tên thật)** và thời
điểm, sẽ trở thành một phần của corpus nghiên cứu ViEmoSpeech và được **công bố công
khai** dưới giấy phép CC-BY 4.0 — nhưng **chỉ là nhãn và mốc thời gian**. Audio,
video, và transcript đầy đủ **không bao giờ** được phát hành.

Chúng tôi cần nhiều người cùng gán nhãn để đo **mức đồng thuận giữa người với người**
— đó là con số nói lên độ tin cậy của corpus. Nếu ai cũng gán giống hệt nhau thì
corpus dễ, nếu chênh nhau nhiều thì bài toán khó; cả hai đều là kết quả hợp lệ và
đều phải được báo cáo trung thực.

## 11. Liên hệ

Vướng gì về công cụ, về hướng dẫn, hay muốn dừng — nhắn cho người phụ trách dự án.
**Đừng hỏi annotator khác** về cách gán nhãn cụ thể (mục 1).
