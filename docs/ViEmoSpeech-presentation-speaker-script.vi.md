# ViEmoSpeech — Kịch bản thuyết trình tiếng Việt

**Bài trình bày:** `ViEmoSpeech-progress-presentation-2026-07-29.pptx`  
**Thời lượng đề xuất:** 10–12 phút  
**Ngôn ngữ slide:** Tiếng Anh  
**Ngôn ngữ thuyết trình:** Tiếng Việt

---

## Slide 1 — ViEmoSpeech

Em xin chào thầy cô và các anh chị.

Hôm nay, em xin trình bày tiến độ hiện tại của ViEmoSpeech. Đây là đề tài xây dựng corpus nhận dạng cảm xúc từ giọng nói tiếng Việt, đồng thời nghiên cứu một câu hỏi đặc thù của ngôn ngữ thanh điệu: thanh điệu từ vựng tương tác với cách con người biểu đạt cảm xúc như thế nào.

Đề tài có hai mục tiêu liên kết với nhau. Mục tiêu thứ nhất là xây dựng một bộ dữ liệu từ lời thoại tiếng Việt tự nhiên, có nguồn gốc rõ ràng và toàn bộ số liệu có thể truy vết. Mục tiêu thứ hai là dùng chính bộ dữ liệu này để kiểm chứng một phương pháp kết hợp âm thanh và văn bản dành cho ngôn ngữ thanh điệu.

Bài trình bày hôm nay tổng hợp các công việc đã thực hiện từ đầu tháng Bảy đến đầu tháng Tám năm 2026.

**Chuyển ý:** Trước tiên, em xin trình bày bài toán thực tế dẫn đến đề tài này.

---

## Slide 2 — Vì sao SER tiếng Việt cần một điểm xuất phát mới?

Có ba lý do chính để thực hiện đề tài.

Thứ nhất là khoảng trống dữ liệu. Hiện chưa có corpus nhận dạng cảm xúc tiếng Việt nào đồng thời đáp ứng ba điều kiện: có thể tiếp cận, chứa lời nói tự nhiên và có giấy phép sử dụng rõ ràng. Vì vậy, trước khi so sánh hoặc cải tiến phương pháp, mỗi nhóm nghiên cứu thường phải tự xây dựng dữ liệu riêng.

Thứ hai là khoảng trống khoa học. Tiếng Việt là ngôn ngữ thanh điệu. Cao độ và chất giọng vừa tham gia xác định nghĩa của từ, vừa là những tín hiệu quan trọng để biểu đạt cảm xúc.

Thứ ba là giá trị ứng dụng. Nhận dạng cảm xúc từ giọng nói có thể hỗ trợ phân tích tổng đài chăm sóc khách hàng, trợ lý ảo và các nghiên cứu liên quan đến sàng lọc sức khỏe tinh thần.

Vì vậy, ViEmoSpeech bắt đầu bằng việc xây dựng tài nguyên còn thiếu, sau đó sử dụng tài nguyên này để trả lời một câu hỏi khoa học riêng của tiếng Việt.

**Chuyển ý:** Câu hỏi đó dẫn đến giả thuyết trung tâm của đề tài.

---

## Slide 3 — Giả thuyết trung tâm có thể đo được

Ý tưởng chính của đề tài là thanh điệu từ vựng và cảm xúc phải cùng sử dụng một kênh âm thanh.

Trong tiếng Việt, sự thay đổi về cao độ và phonation, hay chất giọng, có thể làm thay đổi nghĩa của một âm tiết. Đồng thời, con người cũng thay đổi cao độ, cường độ và chất giọng khi thể hiện các cảm xúc như giận dữ, buồn, sợ hãi hoặc vui vẻ.

Giả thuyết của em là sự chồng lấn này làm cho việc nhận dạng cảm xúc chỉ bằng âm thanh trở nên khó hơn trong tiếng Việt. Do đó, mô hình có thể phải dựa nhiều hơn vào nội dung văn bản hoặc thông tin ngữ nghĩa so với các mô hình dành cho ngôn ngữ phi thanh điệu.

Giả thuyết này có thể được kiểm chứng bằng thực nghiệm. Kết quả ban đầu đã cho hai tín hiệu đáng chú ý. Thứ nhất, điểm CCC của mô hình chỉ dùng âm thanh cho valence và arousal chỉ khoảng 0,09, tức là gần mức sàn. Thứ hai, hệ thống nhận dạng tiếng nói đôi khi nhận sai thanh điệu từ vựng ở các đoạn có cảm xúc mạnh, đặc biệt khi nhân vật đang quát.

Đây chưa phải bằng chứng kết luận, nhưng là động cơ rõ ràng để thực hiện các thí nghiệm bimodal tiếp theo.

**Chuyển ý:** Để kiểm chứng giả thuyết đó, đề tài được thiết kế để tạo ra hai sản phẩm nghiên cứu.

---

## Slide 4 — Hai sản phẩm nghiên cứu và một ràng buộc cứng

Sản phẩm thứ nhất là bài báo về corpus ViEmoSpeech.

Corpus được xây dựng từ lời thoại tự nhiên trong phim truyền hình Việt Nam. Dữ liệu có bảy lớp cảm xúc, nhãn valence và arousal liên tục, cờ distress và phần gán nhãn liên quan đến thanh điệu.

Sản phẩm thứ hai là bài báo phương pháp về mô hình bimodal tone × emotion. Mô hình sẽ kết hợp âm thanh với văn bản, được đánh giá trên tập chia không trùng người nói và kiểm tra liệu nhánh ngữ nghĩa có thể bù lại sự mơ hồ của nhánh âm thanh hay không.

Tuy nhiên, đề tài có một ràng buộc bản quyền rất quan trọng. Video nguồn là nội dung có bản quyền. Vì vậy, sản phẩm công bố chỉ bao gồm đặc trưng âm thanh đã trích xuất, mốc thời gian và nhãn. File âm thanh gốc và transcript đầy đủ sẽ không được phát hành.

Ràng buộc này ảnh hưởng trực tiếp đến pipeline trích xuất, hệ thống gán nhãn, định dạng phát hành và thiết kế pháp lý của toàn bộ dự án.

**Chuyển ý:** Với ràng buộc đó, em xin trình bày pipeline dùng để chuyển một tập phim thành các clip đơn người nói.

---

## Slide 5 — Pipeline trích xuất đã chạy end-to-end

Pipeline trích xuất tự động đã hoàn thành và có thể chạy từ video đầu vào đến các clip đơn người nói đã được căn chỉnh.

Đầu tiên, hệ thống nhận một tập phim truyền hình. Nhạc nền và âm thanh không mong muốn được giảm bằng Demucs. Voice Activity Detection sau đó xác định những vùng có tiếng nói. Các vùng này tiếp tục được chia theo lượt nói, rồi được xử lý bằng PhoWhisper để nhận dạng lời nói và căn chỉnh với caption.

Trên tập pilot dài 35,6 phút, pipeline thu được 11,9 phút thoại sạch. Như vậy, tỷ lệ thoại có thể sử dụng là 33 phần trăm.

Sau bước chia lượt nói, kết quả là 175 clip với tổng thời lượng 10,3 phút. Theo kết quả diarization, toàn bộ clip được giữ lại đều là clip đơn người nói.

Lớp kiểm tra bằng văn bản cũng phát hiện một điểm mù quan trọng của diarization ở khoảng 11,4 phần trăm số clip. Trong các trường hợp này, hai giọng nữ tương đối giống nhau đã bị gộp thành một người nói. Kết quả này cho thấy lớp lọc thứ hai là cần thiết.

Cuối cùng, độ tương đồng ASR trung bình đạt 87,2. Vì vậy, phiên bản PhoWhisper-base hiện tại đã đủ cho pipeline và chưa cần nâng lên mô hình medium.

**Chuyển ý:** Khi áp dụng pipeline này cho hai bộ phim, em đã thu được corpus hiện tại.

---

## Slide 6 — Corpus đã được trích xuất; gán nhãn là giới hạn hiện tại

Giai đoạn trích xuất đã tạo ra 3.775 clip từ hai bộ phim truyền hình Việt Nam, tương đương khoảng 10 giờ lời thoại đơn người nói.

Tính đến ngày 1 tháng 8, 926 clip đã có nhãn cảm xúc, chiếm 24,5 phần trăm toàn corpus. Có thêm 445 clip, tương đương 11,8 phần trăm, đã bị loại do các vấn đề như cắt sai, có nhiều người nói hoặc không có lời thoại.

Như vậy, còn khoảng 64 phần trăm corpus chưa được duyệt.

Phân bố cảm xúc cũng chưa cân bằng. Trong ảnh chụp dữ liệu ngày 29 tháng 7, neutral là lớp lớn nhất, trong khi surprise chỉ có 40 mẫu. Điều này sẽ ảnh hưởng đến cả quá trình huấn luyện mô hình lẫn cách lấy mẫu cho nghiên cứu độ tin cậy nhãn.

Điểm quan trọng ở đây là trích xuất dữ liệu không còn là nút thắt chính. Gán nhãn thủ công và đo độ tin cậy của nhãn hiện là hai yếu tố giới hạn tiến độ.

**Chuyển ý:** Tuy dữ liệu mới ở giai đoạn pilot, em đã có thể huấn luyện một baseline chỉ sử dụng âm thanh.

---

## Slide 7 — Đánh giá trung thực cho thấy khoảng cách tổng quát hóa

Slide này so sánh hai cách đánh giá cho bài toán nhận dạng bảy lớp cảm xúc.

Với GroupKFold theo tập phim, mô hình đạt macro-F1 bằng 0,314. Tuy nhiên, cách đánh giá này tương đối lạc quan vì cùng một diễn viên có thể xuất hiện trong cả tập train và tập test.

Trong cách đánh giá thực tế hơn, mô hình được huấn luyện trên một bộ phim và kiểm thử trên bộ phim còn lại. Đây là phép chia cross-series và không trùng người nói. Khi đó, macro-F1 giảm xuống còn 0,249.

Khoảng cách giữa hai kết quả xấp xỉ 0,065. Khoảng cách này cho thấy hiệu năng có thể bị thổi phồng bao nhiêu nếu cùng một diễn viên xuất hiện ở cả hai phía của quá trình đánh giá.

Điểm 0,249 vẫn cao hơn đáng kể so với mức ngẫu nhiên khoảng 0,04. Điều này cho thấy dữ liệu và pipeline có chứa tín hiệu cảm xúc có thể học được. Tuy nhiên, đây vẫn chỉ là kết quả pilot vì phần lớn nhãn hiện tại mới được gán qua một lượt bởi một người.

Trong bài báo chính thức, kết quả cross-series sẽ là số liệu được báo cáo chính, thay vì kết quả lạc quan hơn.

**Chuyển ý:** Kết quả dự đoán cảm xúc liên tục còn cho thấy rõ hơn lý do cần nghiên cứu mô hình bimodal.

---

## Slide 8 — Kết quả dự đoán liên tục yếu ủng hộ hướng bimodal

Trong bài toán dự đoán cảm xúc liên tục, mô hình chỉ sử dụng âm thanh đạt hệ số tương quan đồng thuận, hay CCC, bằng 0,091 cho valence và 0,087 cho arousal trong phép đánh giá cross-series.

Giá trị CCC hoàn hảo là 1. Vì vậy, các kết quả này đang ở rất gần mức sàn.

Mặc dù các con số có vẻ thấp, chúng lại có giá trị về mặt khoa học. Chúng cho thấy biểu diễn chỉ dựa trên âm thanh chưa thể khôi phục đáng tin cậy các chiều cảm xúc liên tục, đặc biệt khi đánh giá trên người nói mới và một bộ phim khác.

Kết quả này tạo ra động cơ định lượng để bổ sung nhánh văn bản. Thí nghiệm quan trọng tiếp theo sẽ kiểm tra xem việc kết hợp âm thanh và văn bản có cải thiện kết quả trong cùng điều kiện không trùng người nói hay không.

Câu hỏi chính không đơn giản là một mô hình lớn hơn có tạo ra điểm số tốt hơn không. Câu hỏi khoa học là thông tin ngữ nghĩa có bù một cách có hệ thống cho sự mơ hồ âm học do thanh điệu từ vựng tạo ra hay không.

**Chuyển ý:** Tuy nhiên, trước khi thí nghiệm này có thể tạo ra bằng chứng đủ để công bố, đề tài cần giải quyết một vấn đề quan trọng.

---

## Slide 9 — Độ tin cậy giữa người gán nhãn là đường găng

Nút thắt chính hiện nay không phải là một thành phần phần mềm còn thiếu, mà là chưa có số đo độ tin cậy giữa người với người.

Hệ thống kỹ thuật đã hoàn thành. Hệ thống bao gồm cửa đồng ý tham gia, giao diện gán nhãn mù, kiểm soát truy cập, nhật ký hoạt động, vòng qualification và quy trình xây dựng gold set.

Giao thức kiểm soát chất lượng đã được định nghĩa trước khi xem kết quả độ tin cậy. Các script tính Fleiss' kappa và Krippendorff's alpha cũng đã được cài đặt và đối chiếu với phép tính thủ công.

Phần còn thiếu là khoảng ba người gán nhãn thật. Những người này cần cùng gán một tập chồng lấn hoàn toàn gồm khoảng 250 clip.

Bước này không thể thay bằng mô hình ngôn ngữ, vì mục đích của kappa là đo mức đồng thuận giữa các đánh giá độc lập của con người. Mức đồng thuận giữa người và máy sẽ trả lời một câu hỏi khác.

Nếu chưa có độ tin cậy human–human, corpus vẫn chưa đủ điều kiện để trở thành một bài báo dataset, dù hệ thống phần mềm đã hoạt động tốt.

**Chuyển ý:** Vì vậy, giai đoạn tiếp theo phụ thuộc vào ba quyết định và hành động cụ thể.

---

## Slide 10 — Ba quyết định để mở khóa giai đoạn tiếp theo

Có ba ưu tiên trước mắt.

Thứ nhất là giải quyết phương án hosting cho quá trình gán nhãn từ xa. Kế hoạch ban đầu sử dụng tunnel vào máy cá nhân, nhưng chính sách công ty không cho phép cách này. Nếu chuyển media lên hạ tầng cloud, các giả định pháp lý trong thiết kế hiện tại sẽ thay đổi. Vì vậy, cần có một quyết định rõ ràng trước khi triển khai.

Thứ hai là tuyển người gán nhãn và thực hiện nghiên cứu độ tin cậy. Công việc này bao gồm nghe và chốt gold set thủ công, chạy vòng qualification và thu thập khoảng 250 clip có nhãn chồng lấn từ ba người tham gia.

Thứ ba, sau khi nhãn đã ổn định, em sẽ đóng băng phiên bản dữ liệu, chạy benchmark sáu phương pháp, tiếp tục giữ phép chia cross-series và bắt đầu viết hai bài báo.

Kết quả mong đợi vừa có giá trị thực tiễn, vừa có giá trị khoa học: một corpus nhận dạng cảm xúc tiếng Việt có thể truy vết và phép kiểm chứng trực tiếp đầu tiên về ảnh hưởng của thanh điệu từ vựng đối với nhận dạng cảm xúc từ giọng nói.

Em xin cảm ơn thầy cô và các anh chị đã lắng nghe. Em xin sẵn sàng trả lời câu hỏi.

---

## Phiên bản kết luận ngắn

Nếu thời gian không còn nhiều, có thể kết luận bằng đoạn sau:

> Tóm lại, pipeline trích xuất và corpus ban đầu đã hoạt động, đồng thời kết quả pilot cho thấy có cơ sở để nghiên cứu mô hình bimodal. Nút thắt trước mắt là độ tin cậy giữa những người gán nhãn. Sau khi giải quyết phương án hosting và tuyển người tham gia, đề tài có thể chuyển từ kết quả pilot sang một corpus và benchmark đủ điều kiện công bố.

## Các câu hỏi có thể được đặt ra

### Vì sao sử dụng phim truyền hình thay vì thu âm diễn viên hoặc phỏng vấn thực tế?

Phim truyền hình cung cấp lời thoại tiếng Việt đa dạng, giàu biểu cảm và có nhiều người nói ở quy mô phù hợp để một người nghiên cứu có thể xử lý. Tuy nhiên, đây vẫn là lời thoại diễn xuất chứ không hoàn toàn tự phát. Đề tài ghi rõ giới hạn này và không coi nhãn distress là bằng chứng lâm sàng.

### Vì sao không công bố file âm thanh?

Nội dung nguồn có bản quyền. Thiết kế phát hành vì vậy tách sản phẩm nghiên cứu khỏi media có bản quyền. Chỉ các đặc trưng đã trích xuất, mốc thời gian và nhãn được dự kiến công bố.

### Macro-F1 bằng 0,249 có tốt không?

Đây là baseline pilot, không phải hiệu năng mục tiêu. Kết quả cao hơn rõ rệt so với ngẫu nhiên, cho thấy dữ liệu có tín hiệu có thể học được. Quan trọng hơn, kết quả được đo bằng phép chia cross-series nghiêm ngặt nên đáng tin cậy hơn một điểm số cao nhưng có rò rỉ người nói.

### Vì sao cần đo đồng thuận giữa người gán nhãn?

Nhãn cảm xúc có tính chủ quan. Các chỉ số độ tin cậy cho biết những người độc lập có hiểu và áp dụng giao thức gán nhãn một cách nhất quán hay không. Nếu thiếu số đo này, rất khó phân biệt lỗi của mô hình với sự không chắc chắn trong nhãn.

### Kết quả nào sẽ ủng hộ giả thuyết tone × emotion?

Bằng chứng mạnh nhất sẽ là mức cải thiện có thể tái lập của nhánh văn bản trong phép đánh giá không trùng người nói, kết hợp với phân tích cho thấy cải thiện lớn hơn ở những đoạn dễ nhầm thanh điệu hoặc có arousal cao.
