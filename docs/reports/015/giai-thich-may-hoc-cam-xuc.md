# Vì sao máy học được sự khác biệt cảm xúc trong audio

> Giải thích bằng lời thường, đi kèm báo cáo change 015 ([`report.html`](report.html)).
> Các con số trích từ báo cáo đó; nguồn gốc của từng số nằm trong `metrics.json` và
> `classset.json` cùng thư mục.

Máy học được vì **cảm xúc làm thay đổi cơ thể, cơ thể thay đổi thì âm thanh phát ra cũng
thay đổi, và những thay đổi đó đo được thành con số**. Máy không "hiểu" cảm xúc. Nó chỉ tìm
ra quy luật giữa các con số đo được và nhãn do người gán. Có thể chia ra làm ba bước.

## Bước 1: cảm xúc để lại dấu vết vật lý trong giọng nói

Giọng nói được tạo ra bởi phổi (đẩy hơi), dây thanh (rung) và khoang miệng (định hình âm).
Cảm xúc tác động trực tiếp lên cả ba:

| Trạng thái | Cơ thể | Âm thanh |
|---|---|---|
| Kích động (giận, sợ) | thở mạnh, cơ thanh quản căng | **cao giọng hơn**, **to hơn**, nói nhanh, nhiều năng lượng ở tần số cao |
| Trầm (buồn, mệt) | cơ chùng, hơi thở yếu | **thấp giọng**, nhỏ, chậm, giọng có hơi thở |
| Căng thẳng | dây thanh rung không đều | giọng **run** (jitter tăng) |

Những thay đổi này phần lớn là phản xạ, khó kiểm soát hoàn toàn. Vì vậy chúng xuất hiện khá
ổn định ở mọi người.

Dữ liệu ViEmoSpeech xác nhận điều đó: cao độ và độ to tương quan **ρ ≈ +0.55** với mức kích
động. Giận và sợ cao giọng hơn hẳn, trung tính và buồn thấp hơn hẳn.

## Bước 2: biến âm thanh thành con số

Máy không nghe được, nó chỉ nhận một dãy số (sóng âm, 16.000 số mỗi giây). Phải chuyển dãy
đó thành các **đặc trưng** có ý nghĩa. Có hai cách, và change 015 đã thử cả hai:

- **Cách thủ công (eGeMAPS):** chuyên gia định nghĩa sẵn 88 phép đo như cao độ trung bình,
  độ to, độ run, năng lượng tần số cao. Dễ hiểu, nhưng chỉ bắt được những gì con người nghĩ
  ra trước.
- **Cách tự học (WavLM):** một mạng nơ-ron được huấn luyện trước trên hàng chục nghìn giờ
  giọng nói, với nhiệm vụ đoán phần âm thanh bị che. Để làm tốt việc đó, nó buộc phải tự học
  cách mô tả giọng nói, gồm cả ngữ điệu, nhịp và chất giọng. Mỗi đoạn audio được nó biến
  thành 1024 con số ở mỗi tầng.

Các tầng của WavLM học những thứ khác nhau:

```
tầng đầu    →  âm thanh thô (năng lượng, tần số)
tầng giữa   →  ngữ điệu, nhịp, chất giọng, đặc điểm người nói   ← cảm xúc nằm nhiều ở đây
tầng cuối   →  "đang nói chữ gì" (âm vị, từ)
```

Vì vậy lấy thông tin ở tầng giữa cho điểm cao hơn tầng cuối (macro-F1 **0.296** so với
**0.261**). WavLM cũng vượt 88 đặc trưng thủ công (**0.229**), vì nó bắt được cả những tổ
hợp và diễn biến theo thời gian mà con người không liệt kê ra.

## Bước 3: học từ ví dụ có nhãn

Sau khi mỗi đoạn audio thành một vector số, máy được cho xem hàng nghìn ví dụ kiểu "đoạn
này là giận", "đoạn kia là buồn". Nó học một bộ **trọng số**: con số nào tăng thì nghiêng
về giận, con số nào giảm thì nghiêng về buồn. Hình dung các đoạn audio là những điểm trong
không gian: đoạn giận tụ về một vùng, đoạn buồn tụ về vùng khác, và máy học đường ranh giới
giữa các vùng.

Vì những dấu vết ở bước 1 xuất hiện ở hầu hết mọi người, một model học trên phim này vẫn
nhận ra cảm xúc ở phim khác với diễn viên khác. Điểm đạt khoảng **0.30**, so với khoảng
**0.13** nếu đoán ngẫu nhiên.

## Máy **không** học được gì, và vì sao

1. **Tích cực hay tiêu cực (valence).** Cơ thể phản ứng theo **mức kích động**, không theo
   cực tính. Vui sướng và giận dữ đều làm tim đập nhanh, giọng cao và to, nên trong âm thanh
   chúng **trông rất giống nhau**. Muốn phân biệt phải dựa vào nội dung lời nói hoặc ngữ
   cảnh. Vì thế valence chỉ đạt ρ tối đa **0.20**, và gần bằng 0 khi dự đoán sang phim khác.
2. **Cảm xúc không có dấu vết cơ thể rõ ràng.** Ghê/khinh trong phim thường là nói giọng
   bình thường với nội dung khinh bỉ. Âm thanh gần như không khác gì, nên cả model lẫn người
   soát lại đều nhầm sang trung tính, giận, buồn.
3. **Thanh điệu tiếng Việt.** Cao độ vừa dùng để phân biệt *ma / má / mà / mã / mạ*, vừa dùng
   để thể hiện cảm xúc. Máy phải tự gỡ hai thứ trộn lẫn này, và hiện chưa có nhãn thanh điệu
   để giúp nó.
4. **Nhãn của con người.** Máy chỉ học được tốt bằng nhãn nó được dạy. Khi hai người gán
   nhãn chỉ đồng thuận ở mức κ **0.51**, nhãn đã chứa nhiễu, và điểm của model bị giới hạn
   theo.

## Tóm lại

Máy học được phần cảm xúc **thể hiện qua cơ thể**, chủ yếu là mức kích động. Phần cảm xúc
**thể hiện qua ý nghĩa** (tích cực hay tiêu cực, khinh bỉ) thì âm thanh một mình không đủ.
Đó là lý do bước tiếp theo của dự án (change 013) là kết hợp thêm lời thoại và thanh điệu.
