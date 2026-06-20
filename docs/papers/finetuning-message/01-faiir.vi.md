# Bài báo 01 — FAIIR: Trợ lý Tác tử AI Hội thoại cho Việc Cung cấp Dịch vụ Sức khỏe Tâm thần Thanh thiếu niên

## 1. Thông tin thư mục

**Tiêu đề:** FAIIR: Building Toward A Conversational AI Agent Assistant for Youth Mental Health Service Provision (FAIIR: Hướng tới một Trợ lý Tác tử AI Hội thoại cho việc Cung cấp Dịch vụ Sức khỏe Tâm thần Thanh thiếu niên)

**Tác giả:** Stephen Obadinma (Đại học Queen's / Vector Institute, tác giả liên hệ), Alia Lachana, Maia Norman (Vector Institute / Đại học Waterloo), Jocelyn Rankin (Kids Help Phone), Joanna Yu (Vector Institute), Xiaodan Zhu (Queen's / Vector), Darren Mastropaolo (Kids Help Phone), Deval Pandya (Vector), Roxana Sultan (Vector / Đại học Toronto), Elham Dolatabadi (Vector / Đại học Toronto / Đại học York). Lachana, Norman, Rankin và Yu đóng góp ngang nhau.

**Đơn vị công tác:** Khoa Kỹ thuật Điện và Máy tính tại Đại học Queen's, Vector Institute (Toronto), Đại học Waterloo, Kids Help Phone (KHP), Đại học Toronto, Đại học York.

**Năm / nơi công bố:** Bản tiền ấn (preprint) đăng trên arXiv ngày 28 tháng 5 năm 2024 (v1); v4 đề ngày 12 tháng 2 năm 2025 (cs.AI). Được xuất bản trên *npj Digital Medicine* (2025) với mã bài báo s41746-025-01647-6. DOI 10.48550/arXiv.2405.18553.

**Từ khóa (nguyên văn):** "conversational AI, mental health, crisis conversations, large language models, multi-label classification" (AI hội thoại, sức khỏe tâm thần, hội thoại khủng hoảng, mô hình ngôn ngữ lớn, phân loại đa nhãn).

## 2. Động cơ của vấn đề

Các tác giả định khung công trình này như một phản ứng trước sự mất cân đối kéo dài giữa nhu cầu hỗ trợ khủng hoảng sức khỏe tâm thần ở thanh thiếu niên và năng lực của đội ngũ tuyến đầu. Họ dẫn chứng rằng "cứ bảy người trẻ trong độ tuổi 10 đến 19 thì có một người trải qua một tình trạng sức khỏe tâm thần", rằng "tự tử xếp thứ tư trong các nguyên nhân gây tử vong hàng đầu ở nhóm 15 đến 29 tuổi", và rằng tại Canada "cứ năm người thì có một người sẽ trải qua một căn bệnh tâm thần trước tuổi 25". Mặc dù "70% các bệnh tâm thần khởi phát trong giai đoạn thơ ấu hoặc thanh thiếu niên, chỉ một phần nhỏ người trẻ có thể tiếp cận được sự chăm sóc phù hợp".

Bối cảnh vận hành là Kids Help Phone (KHP), một tổ chức phi lợi nhuận của Canada. Kể từ khi ra mắt dịch vụ SMS của KHP vào năm 2018, "KHP đã tạo điều kiện cho hơn 1 triệu lượt tương tác qua Tin nhắn Văn bản (SMS), với mức tăng đáng kể 51% được ghi nhận trong đại dịch COVID-19 vào năm 2020". Các Nhân viên Ứng phó Khủng hoảng (Crisis Responders — CRs) — bao gồm cả chuyên gia được trả lương và tình nguyện viên được đào tạo — xử lý các cuộc hội thoại này dưới áp lực nhận thức nặng nề trong khi quản lý "những cá nhân đang căng thẳng cảm xúc trong các tình huống có thể nguy hiểm đến tính mạng". Sau mỗi cuộc hội thoại, các CR phải "hoàn thành các khảo sát sau hội thoại để xác định các vấn đề chính như tự tử và lạm dụng, làm tăng thêm khối lượng công việc của họ".

Vai trò của FAIIR mang tính **hỗ trợ và hành chính một cách rõ ràng, không mang tính lâm sàng**. Công cụ này "đề xuất các vấn đề tiềm năng từ một danh sách gồm 19 nhãn được định nghĩa trước" để "có thể cung cấp các nguồn lực phù hợp và để các hoạt động cứu hộ chủ động cùng việc báo cáo bắt buộc có thể diễn ra trong những tình huống nghiêm trọng". Nó không tạo ra các phản hồi trị liệu, không đưa ra lời khuyên lâm sàng, cũng không thay thế CR; nó giảm gánh nặng gắn nhãn sau hội thoại và làm nổi bật các tín hiệu ưu tiên. Các tác giả định khung điều này là một "thiết kế có-con-người-trong-vòng-lặp (human-in-the-loop) với sự tham gia tích cực của CR để tinh chỉnh mô hình, xây dựng đồng thuận và đánh giá tổng thể".

## 3. Vị trí trong y văn

Các tác giả đặt FAIIR ở giao điểm của ba luồng nghiên cứu. Thứ nhất, **NLP cho phân loại văn bản sức khỏe tâm thần** — họ dẫn các công trình về nhận diện dấu hiệu trầm cảm trên mạng xã hội (tài liệu tham khảo 15–17), ý định tự tử trong các bài đăng mạng xã hội (tài liệu 18), và các chủ đề liên quan đến tự tử cùng tình trạng sức khỏe tâm thần từ ghi chú lâm sàng (tài liệu 19, 20). Thứ hai, **phân loại ưu tiên (triage) trên các nền tảng khủng hoảng** — họ dẫn công trình hỗ trợ "phân loại ưu tiên và giảm thời gian chờ trên các nền tảng hỗ trợ tự tử dựa trên tin nhắn" (tài liệu 21). Thứ ba, **các transformer chuyên cho tài liệu dài và hội thoại** — Li và cộng sự (tài liệu 23) cho thấy Longformer vượt trội ClinicalBERT trên các tài liệu lâm sàng dài; Dai và cộng sự (tài liệu 32) về phân loại tài liệu dài; Zhong và cộng sự (tài liệu 26, DialogLED) về khử nhiễu cửa sổ hội thoại; và Ji và cộng sự (tài liệu 34) về RoBERTa/Longformer/XLNet được tiền huấn luyện trên các kho ngữ liệu sức khỏe tâm thần.

Khoảng trống được tuyên bố là các công trình NLP cho đường dây khủng hoảng trước đây có quy mô nhỏ, phạm vi hẹp (thường chỉ riêng xu hướng tự tử), và hiếm khi được kiểm chứng tiền cứu (prospectively) với chính những nhân viên ứng phó phải sử dụng các dự đoán. FAIIR giải quyết điều này bằng cách kết hợp (a) một trong những kho ngữ liệu hội thoại khủng hoảng lớn nhất từng được dùng trong y văn (~780 nghìn cuộc hội thoại), (b) một hệ thống phân loại 19 nhãn mang tính vận hành thay vì một biến nhị phân đơn lẻ, (c) việc thích ứng miền (domain adaptation) một cách rõ ràng thông qua MLM trên kho ngữ liệu trong-miền, và (d) một đánh giá hai pha với cả một tập hồi cứu được giữ riêng (held-out) lẫn một tập kiểm tra "im lặng" (silent test) được triển khai cộng với đánh giá có cấu trúc của chuyên gia.

## 4. Phân tích sâu về tập dữ liệu

Kho ngữ liệu phát triển bao gồm **703.975 cuộc đối thoại SMS đa lượt, đa chiều, đã được ẩn danh và làm sạch (scrubbed)** giữa người dùng dịch vụ và các CR, được thu thập tại KHP từ **tháng 1 năm 2018 đến tháng 2 năm 2023**. Một lô thứ hai gồm **84.832 cuộc hội thoại từ tháng 2 đến tháng 9 năm 2023** được giữ riêng để kiểm tra im lặng tiền cứu. Dữ liệu huấn luyện đại diện cho 340.512 người dùng dịch vụ duy nhất và 7.937 CR; dữ liệu kiểm tra im lặng đại diện cho 57.031 người dùng dịch vụ duy nhất và 2.038 CR.

**Độ dài hội thoại.** Độ dài trung bình là 913 token và trung vị là 850. "Phần lớn các cuộc hội thoại (53%) [nằm] trong khoảng 500 đến 1.500 token, và chỉ một số ít vượt quá 3.000 (0,7%)." Độ dài đầu vào tối đa 2.000 token được chọn, bao phủ 94,4% tổng số cuộc hội thoại.

**Làm sạch (Scrubbing).** "Thông tin định danh được làm sạch để đảm bảo tuân thủ quyền riêng tư" bằng cách tự động thay thế tên và địa điểm bằng ký hiệu giữ chỗ `[scrubbed]`. Các tác giả nêu rõ một chi phí đã biết: "trong nhiều trường hợp, toàn bộ cụm từ và câu đã bị làm sạch... Quá trình này do đó đã tạo ra một số nhiễu do việc vô tình loại bỏ những từ vô hại, như 'turkey' (gà tây)."

**Hệ phân loại 19 nhãn.** Các nhãn (mỗi nhãn được định nghĩa trong Phụ lục A): *3rd Party (Bên thứ ba), Abuse Emotional (Lạm dụng Cảm xúc), Abuse Physical (Lạm dụng Thể chất), Abuse Sexual (Lạm dụng Tình dục), Anxiety/Stress (Lo âu/Căng thẳng), Bully (Bắt nạt), Depressed (Trầm cảm), Did Not Engage — DNE (Không Tham gia), Eating Body Image (Ăn uống/Hình thể), Gender/Sexual Identity (Bản dạng Giới/Tính dục), Grief (Đau buồn), Isolated (Cô lập), Other (Khác), Prank (Trò đùa), Relationship (Mối quan hệ), Self Harm (Tự gây thương tích), Substance Abuse (Lạm dụng Chất gây nghiện), Suicide (Tự tử), Testing (Thử nghiệm/Dò xét).* Các cuộc hội thoại mang tính **đa nhãn**: 53,73% có một nhãn duy nhất, và 46% có từ 2 đến 9 nhãn. Phân bố mất cân bằng nghiêm trọng — nhãn xuất hiện nhiều nhất (Anxiety/Stress) có trong hơn 244.000 cuộc hội thoại, trong khi nhãn ít nhất (Prank) chỉ xuất hiện trong khoảng ~2.800.

**Hệ thống cờ ưu tiên (Phụ lục D).** Ở đầu mỗi cuộc hội thoại, một thuật toán thuộc sở hữu của Crisis Text Line gán mức rủi ro *high / medium / low / no ground truth* (cao / trung bình / thấp / không có chân lý nền). "Mức rủi ro trung bình được gán khi người dùng bày tỏ ý nghĩ tự tử hoặc tự gây thương tích, và mức rủi ro cao được gán khi một cá nhân được đánh giá là có 'rủi ro cận kề' (imminent risk), được định nghĩa là sự kết hợp của ý nghĩ tự tử, một kế hoạch, khả năng tiếp cận phương tiện, và một mốc thời gian 0–48 giờ." Việc kích hoạt bất kỳ từ khóa nào trong số 56 từ tiếng Anh hoặc 73 từ tiếng Pháp trong tin nhắn đầu tiên sẽ làm leo thang mức ưu tiên. Trên thực tế, 87% các cuộc hội thoại ở mức rủi ro trung bình, ~13% rủi ro cao, và ~0,0001% rủi ro thấp.

**Nhiễu nhãn.** Quan trọng là, "quá trình gắn nhãn này được thực hiện bởi các CR theo quyết định riêng của họ, và theo sự đào tạo của họ. Do nguồn lực hạn chế và lượng lớn yêu cầu của người dùng dịch vụ, các nhãn vấn đề thường không trải qua thêm bước rà soát." Các tác giả nhiều lần quay lại đặc tính một-người-chú-thích-cho-mỗi-cuộc-hội-thoại này như nguồn nhiễu lớn nhất không thể giảm thiểu được.

**Nhân khẩu học.** Một khảo sát sau hội thoại không bắt buộc được hoàn thành bởi ~17% người dùng dịch vụ (n=59.603 trên 340.512). Trong số những người trả lời, phân nhóm đông nhất là nữ (75,6%), dị tính (55,5%), gốc Âu (78,1%); 67,3% người trả lời về bản dạng cho biết họ có một Khuyết tật Vô hình (Invisible Disability). Các tác giả cảnh báo rằng "kết quả không phản ánh đầy đủ phân bố hoặc đặc điểm nhân khẩu học của người dùng dịch vụ nói chung".

**Đạo đức.** Không có số hiệu IRB bên ngoài nào được báo cáo. "Tuyên bố Đạo đức" của KHP mô tả việc tuân thủ chính sách quyền riêng tư của KHP và các quy định về quyền riêng tư của Canada, việc loại bỏ các định danh trực tiếp, lưu trữ trong-hạ-tầng (in-infrastructure), và một "thông báo đồng thuận cho nghiên cứu cùng việc giảm thiểu dữ liệu nghiêm ngặt". Mã nguồn nằm tại một kho GitHub riêng tư (`KidsHelpPhone/AI-ML`) có thể truy cập theo yêu cầu; dữ liệu không được chia sẻ công khai "vì lý do nhạy cảm".

## 5. Phương pháp

**Định khung tác vụ.** Phân loại đa nhãn: mỗi trong số 19 nhãn là một đầu (head) dương/âm độc lập đặt trên một bộ mã hóa (encoder) dùng chung, được huấn luyện với hàm mất mát binary cross-entropy.

**Bước 1: so sánh các bộ mã hóa.** Bốn transformer được tiền huấn luyện được tinh chỉnh (fine-tune) trên một tập con ngẫu nhiên gồm 50.000 cuộc hội thoại với phép chia phân tầng 60/20/20:

| Mô hình | Loại | Tham số | Lý do chọn |
|---|---|---|---|
| Longformer | chỉ-encoder | 149M | bộ mã hóa attention-thưa được xây dựng cho chuỗi dài |
| Conversational BERT | chỉ-encoder | 110M | được tiền huấn luyện trên kho ngữ liệu hội thoại |
| DialogLED | encoder-decoder | 139M | mô hình hội thoại dài được khử nhiễu theo cửa sổ hội thoại |
| MVP (Multi-task superVised Pre-training) | encoder-decoder | 406M | tiền huấn luyện sinh đa tác vụ mạnh |

Các mô hình chỉ-encoder gắn một đầu phân loại trên token `[CLS]`; DialogLED dùng `[EOS]` và MVP dùng token đầu tiên. Tất cả được tinh chỉnh trên 4× GPU NVIDIA A10 (24 GB VRAM, 16 nhân CPU), kích thước batch hiệu dụng 16, learning rate quét từ 1e-5 đến 3e-5. Longformer bị giới hạn ở 2.048 token; các mô hình khác dùng giới hạn mặc định 512 token. Số epoch tối ưu: BERT 2, DialogLED 3, Longformer 5, MVP 2.

**Kết quả Bảng B2:** Longformer accuracy 0,938 / exact-accuracy 0,336 / sample-avg P 0,660 / R 0,530 / F1 0,560; BERT 0,936 / 0,339 / 0,650 / 0,540 / 0,560; DialogLED 0,922 / 0,206 / 0,430 / 0,320 / 0,350; MVP 0,351 / 0,000 / 0,200 / 0,820 / 0,310. Longformer được chọn làm xương sống (backbone) vì ngang bằng với BERT cộng thêm khả năng xử lý ngữ cảnh dài.

**Tiền huấn luyện tiếp tục bằng MLM.** Mỗi Longformer được thích ứng miền thông qua mô hình hóa ngôn ngữ có che (masked language modelling) trên toàn bộ kho ngữ liệu huấn luyện: "15% token mỗi cuộc hội thoại", một epoch, độ dài chuỗi tối đa 1.500, bộ tối ưu AdamW, bộ lập lịch tuyến tính với 500 bước khởi động (warm-up), kích thước batch hiệu dụng 64 nhờ tích lũy gradient. Pha này cần ~24 giờ.

**Bước 2: tinh chỉnh cuối cùng cho cụm Longformer (ensemble).** Phần backend được triển khai của FAIIR là một cụm (ensemble) gồm ba Longformer, mỗi mô hình có thiết lập khởi tạo và tinh chỉnh hơi khác nhau. Việc tinh chỉnh được thực hiện trên một phép chia 60/20/20 cân bằng nhãn của 563.180 cuộc hội thoại (422.385 huấn luyện / 140.795 kiểm định / 140.795 kiểm tra hồi cứu). Với mỗi thành viên cụm: tối đa 3 epoch, kích thước batch 16 thông qua tích lũy gradient, LR 2e-5, hàm mất mát BCE, AdamW, bộ lập lịch tuyến tính với warm-up trong 20% bước huấn luyện đầu tiên. **Việc lấy mẫu thừa (oversampling) các cuộc hội thoại có nhãn vấn đề hiếm hơn được áp dụng cho hai trong ba thành viên cụm** để chống mất cân bằng lớp; thành viên thứ ba được huấn luyện trên phân bố tự nhiên để bảo toàn việc hiệu chuẩn (calibration).

**Điều kiện hóa bằng cờ ưu tiên.** Theo khuyến nghị của chuyên gia miền, cuộc hội thoại được thêm tiền tố là một câu nguyên văn: `"This conversation is of <<X>> priority"` (Cuộc hội thoại này có mức ưu tiên <<X>>) trong đó X là *high*, *medium*, hoặc *low*. Điều này tiêm tín hiệu phân loại ưu tiên dựa-trên-luật vào luồng đầu vào, để bộ mã hóa nhìn nó như văn bản thông thường.

**Điều chỉnh ngưỡng.** Bước 1 dùng một ngưỡng cắt đồng nhất 0,25 trên cả 19 đầu sigmoid sau khi quét 0,25–0,50 trên tập kiểm định. Đối với cấu hình được triển khai (kiểm tra im lặng), các tác giả áp dụng một chính sách theo-từng-nhãn: 0,4 cho ba lớp tần suất cao nhất (*Anxiety/Stress*, *Depressed*, *Relationship*), 0,3 cho hai lớp tiếp theo (*Suicide*, *Isolated*), và 0,2 cho 14 nhãn còn lại. Lý do: "chúng tôi điều chỉnh ngưỡng để giảm tần suất xuất ra các nhãn phổ biến nhất trong khi hạ ngưỡng cho các nhãn hiếm".

## 6. Thí nghiệm và kết quả

**Kiểm tra hồi cứu (n=140.795).** AUROC trung bình 0,94 trên 19 nhãn, với hầu hết các nhãn trên 0,90 và thấp nhất ở 0,74 (*Other*). Tại ngưỡng 0,25, các điểm trung bình theo mẫu là **precision 0,58, recall 0,81, F1 0,64, accuracy 0,94**. Tại ngưỡng 0,50, precision tăng lên ~0,61 nhưng recall trung bình theo mẫu giảm xuống ~0,60 (theo Hình 2 bên trái). Các tác giả công khai chấp nhận sự đánh đổi precision/recall: "sự đánh đổi giữa recall và precision này là chấp nhận được trong bối cảnh này, vì nó ưu tiên việc nắm bắt các vấn đề nghiêm trọng".

**Hiệu năng theo từng nhãn (ngưỡng 0,25, hồi cứu).** Mạnh: *3rd Party* F1 0,76 (P 0,64 / R 0,95), *Anxiety/Stress* F1 0,69, *Depressed* F1 0,75, *Relationship* F1 0,73, *Self Harm* F1 0,69, *Suicide* F1 0,73, *Gender/Sexual Identity* F1 0,67, *Eating Body Image* F1 0,64. Yếu: *Other* F1 0,35, *Prank* F1 0,45, *Abuse Emotional* F1 0,46, *Abuse Physical* F1 0,47, *Isolated* F1 0,56, *Testing* F1 0,53. AUROC cho *Suicide* là 0,94, *Self Harm* 0,97, *Abuse Sexual* 0,98.

**Kiểm tra im lặng tiền cứu (n=84.832, tháng 2–9/2023).** "Precision, recall và F1 trung bình theo mẫu lần lượt là 0,57, 0,79, và 0,62 tại ngưỡng 0,25, so với 0,58, 0,81, và 0,64 cho các giá trị hồi cứu, cho thấy mức giảm dưới 2%." Phân bố AUROC tương tự (hầu hết >0,90, thấp nhất 0,73). Các tác giả quy khoảng cách này cho sự trôi dạt tự nhiên (drift) — tập im lặng "tự nhiên bao gồm các chủ đề và sự kiện cập nhật hơn của năm 2023 như thiên tai và khủng hoảng chính trị", và nhãn DNE trở nên phổ biến hơn về mặt tỷ lệ.

**Phân tầng theo nhân khẩu học (Bảng 2).** Trên 27 phân nhóm thuộc bốn danh mục (Giới / Xu hướng / Bản dạng / Sắc tộc), F1 được phân cụm chặt chẽ. Độ lệch chuẩn của F1 theo danh mục: Giới ±0,023, Xu hướng ±0,010, Bản dạng ±0,018, Sắc tộc ±0,024. Một kiểm định t một mẫu (p < 0,001) báo cáo "không có sự khác biệt đáng kể giữa F1 của từng phân nhóm nhân khẩu học và hiệu năng tổng thể". Ví dụ F1 theo nhóm: Nam 0,64, Nữ 0,65, Chuyển giới Nam 0,64, Chuyển giới Nữ 0,59 (n=32), Phi nhị giới 0,63, Dị tính 0,65, Đồng tính nam/nữ 0,66, Song tính 0,64, Gốc Âu 0,65, Gốc Phi hoặc Caribe 0,61, Bản địa 0,65, Đông/Đông Nam Á 0,63.

**Hiệu năng phân tầng theo ưu tiên (Phụ lục D, Bảng D3).** Tại ngưỡng 0,25, P/R/F1 trung bình có trọng số cho mức ưu tiên Trung bình là 0,54/0,80/0,64 và cho mức Cao là 0,56/0,81/0,65 — gần như phẳng giữa các mức rủi ro, điều mà các tác giả định khung là bằng chứng cho thiên lệch cờ-ưu-tiên thấp.

**Hiệu chuẩn / độ tin cậy.** Không được báo cáo — không có biểu đồ độ tin cậy (reliability diagrams), chỉ số ECE, hay thí nghiệm hiệu chỉnh nhiệt độ (temperature-scaling).

## 7. Nghiên cứu thẩm định bởi chuyên gia

Các tác giả tuyển **12 CR đã được đào tạo** để rà soát **40 cuộc hội thoại đầy thử thách**, tạo ra **240 chú thích** (sáu cho mỗi cuộc hội thoại). Việc chọn mẫu được cố ý làm khó: 20 trong số 40 cuộc được lấy từ tập kiểm tra với 4+ nhãn được gán; 20 cuộc còn lại pha trộn các cuộc hội thoại có ít nhãn với các trường hợp được chọn thủ công để bao phủ nhãn, các cuộc hội thoại dài mơ hồ một cách cố ý chỉ với 1–2 nhãn, và các trường hợp nghi ngờ bị gắn nhãn sai. Phương pháp luận chia các người chú thích theo từng cuộc hội thoại: **ba CR thực hiện "rà soát mở" (open review)** (các dự đoán của FAIIR được cho họ xem làm tham chiếu), và **ba CR còn lại thực hiện "rà soát mù" (blind review)** (không tiếp xúc với FAIIR, phân loại nhãn chính (primary) so với nhãn phụ (secondary) từ đầu).

Năm tiêu chí đồng thuận được định nghĩa cho bối cảnh mù: (1) FA: 1° — đồng thuận hoàn toàn về nhãn chính; (2) PA: 1° Maj. — đa số đồng thuận về nhãn chính trùng với FAIIR; (3) PA: 1°+2° Maj. — đa số đồng thuận về nhãn chính và phụ trùng với FAIIR; (4) FA: 1° ≥ 1 — ít nhất một nhãn chính của một người chú thích trùng với FAIIR; (5) FA: 1°+2° ≥ 1 — ít nhất một nhãn chính hoặc phụ của một người chú thích trùng với FAIIR.

**Kết quả nổi bật:** trung bình trên 40 cuộc hội thoại, các người rà soát mù đồng ý với FAIIR ở **90,9% các nhãn** (khoảng 33%–100%); FAIIR tạo ra 165 nhãn và theo biểu quyết đa số chỉ bỏ sót 13. Trên năm tiêu chí đồng thuận, FAIIR-so-với-chuyên-gia đạt precision trung bình 0,62 ± 0,22, recall 0,82 ± 0,13, F1 0,64 ± 0,11 — tất cả đều cao hơn đáng kể so với nhãn-gốc-so-với-chuyên-gia (P 0,52 ± 0,18, R 0,56 ± 0,08, F1 0,47 ± 0,07; kiểm định t không ghép cặp p < 0,001). Nói cách khác, **mô hình đồng thuận với các chuyên gia nhiều hơn so với các nhãn gốc của CR**, điều mà các tác giả coi là bằng chứng rằng các nhãn vận hành nhiễu hơn so với mô hình đã được huấn luyện. Sau khi kết hợp các phản hồi mù để tinh chỉnh lại ngưỡng, precision tăng ~4% (lên 0,66 ± 0,20) với cái giá là recall (xuống 0,76 ± 0,14). Đồng thuận mạnh xuất hiện ở *Anxiety/Stress*, *Bully*, *Relationship*, *3rd Party*, *Suicide*, *Abuse Emotional*; bất đồng nhiều hơn xuất hiện ở *Grief*, *Self Harm*, *Abuse Physical*, *Other*, *Eating Body Image*.

## 8. Khảo sát loại bỏ (Ablation) / các chế độ thất bại

Bài báo không chạy một lưới khảo sát loại bỏ chính thức, nhưng một số trục được mô tả đặc tính. **Khảo sát loại bỏ bộ mã hóa** (Bảng B2): các mô hình encoder-decoder MVP và DialogLED sụp đổ trên tác vụ đa nhãn này (F1 0,31 và 0,35); Longformer và BERT tương đương ở F1 0,56, với Longformer thắng về khả năng xử lý ngữ cảnh dài. **Độ nhạy ngưỡng** được báo cáo dưới dạng các hàng cạnh nhau (0,25, 0,5, đã cập nhật) trong Bảng 1 — chuyển từ 0,25 lên 0,5 làm tăng precision nhưng cắt giảm mạnh recall của các nhãn hiếm hơn (ví dụ: recall của *Abuse Physical* giảm từ 0,70 xuống 0,50; recall của *Prank* từ 0,66 xuống 0,55). **Mất cân bằng lớp** được xử lý bằng oversampling trên hai thành viên cụm cộng với tái cân trọng số (re-weighting); các nhãn yếu dai dẳng (*Other*, *Prank*, *Abuse Physical*, *Isolated*, *Testing*) được quy cho hoặc sự hiếm gặp hoặc sự mơ hồ về ngữ nghĩa — ví dụ, *Other* "bao hàm bất cứ thứ gì ngoài phạm vi của 19 nhãn đã định" và *Isolated* "có thể áp dụng cho một phổ rộng các cuộc hội thoại, nhưng mức độ liên quan của nó có thể được áp dụng một cách chọn lọc". Các nhãn mạnh nhất là những nhãn quan trọng về mặt vận hành (*Suicide*, *Self Harm*, *Depressed*, *Anxiety/Stress*, *Relationship*) — một hồ sơ thất bại đáng mong muốn cho một công cụ hỗ-trợ-an-toàn.

## 9. Các hạn chế do tác giả nêu

Phần Thảo luận và Hạn chế xác định năm mối lo lặp lại. (1) **Hệ phân loại đóng:** "Hạn chế chính của nghiên cứu chúng tôi là sự phụ thuộc vào một tập 19 nhãn vấn đề được định nghĩa trước... Hạn chế này giới hạn khả năng của mô hình trong việc trích xuất thông tin vượt ngoài danh sách đã định trước" — các CR muốn có những nhãn động, lấy-thanh-thiếu-niên-làm-trung-tâm mà mô hình hiện tại không thể tạo ra. (2) **Nhiễu nhãn một-người-chú-thích:** "chúng tôi ghi nhận các thiên lệch tiềm tàng trong quá trình gắn nhãn gốc, vì mỗi cuộc hội thoại được gắn nhãn bởi một người chú thích duy nhất mà không có rà soát tiếp theo... một tập dữ liệu lớn được chú thích cho một tác vụ có giám sát với nhiều người chú thích cho mỗi cuộc hội thoại sẽ là tối ưu". (3) **Hiệu năng kém ở các nhãn hiếm:** sự mất cân bằng "giải thích cho hiệu năng tương đối kém hơn của FAIIR trên các nhãn vấn đề ít được đại diện... Các nhãn như Prank và Abuse, Physical cũng chịu thiệt về hiệu năng do sự hiếm gặp của chúng". (4) **Nhiễu do làm sạch và nhiễu hội thoại:** "chất lượng khác nhau của các cuộc hội thoại, bao gồm sự khác biệt trong cách dùng ngôn ngữ, ngữ pháp, và sự hiện diện của nhiễu như lỗi chính tả hoặc tiếng lóng... đòi hỏi các nỗ lực tiền xử lý sâu rộng, điều này đưa vào tính chủ quan và thiên lệch tiềm tàng trong dữ liệu". (5) **Khả năng giải thích chưa được kiểm chứng:** quy trình từ-khóa-tự-nhiên được trình bày như mang tính thăm dò — "độ tin cậy và ý nghĩa của các từ khóa tự nhiên này cần được đánh giá nghiêm ngặt hơn nữa". Rủi ro triển khai được thừa nhận một cách ngầm ẩn: kiểm tra im lặng được trình bày chính xác như cầu nối giữa các chỉ số ngoại tuyến (offline) và việc sử dụng thời gian thực, nhưng không có đánh giá triển khai đầy đủ nào được báo cáo. Chi phí suy luận của cụm (ensemble inference) chỉ được đề cập gián tiếp thông qua phần thảo luận về chi phí-tài-nguyên của các baseline encoder-decoder.

## 10. Mức độ liên quan tới bộ phân loại cảm xúc của Pebble

FAIIR là bài báo tương đồng nhất đã được công bố với bộ phân loại cảm xúc của Pebble về hình dạng vấn đề — cả hai đều là bộ phân loại văn bản sức khỏe tâm thần đa-đầu-ra mà đầu ra đưa vào các luồng hạ nguồn an-toàn-trọng-yếu. Một số tương phản và bài học cụ thể được áp dụng.

- **Cùng lớp vấn đề.** Cả hai đều là bộ phân loại đa-đầu-ra trên văn bản sức khỏe tâm thần, nơi âm tính giả (false negative) trên các tín hiệu hiếm-nhưng-trọng-yếu (xu hướng tự tử, tự gây thương tích, lạm dụng đối với FAIIR; các chiều cảm xúc đau khổ cao tương tự đối với Pebble) tốn kém hơn dương tính giả (false positive). Do đó cả hai nhóm đều cố ý thiên về recall.
- **Tương phản về nguồn nhãn.** FAIIR huấn luyện trên **nhãn vận hành từ một-người-chú-thích** (mỗi cuộc hội thoại được gắn nhãn bởi một CR theo quyết định riêng, không có rà soát thứ hai) và coi nhiễu đó như một hạn chế cấu trúc. Pebble huấn luyện trên **nhãn bạc (silver labels) từ LLM**, một nguồn nhiễu khác nhưng song song — mang tính hệ thống, không phải cá nhân-con-người, và có thể tái-gắn-nhãn theo lập trình. Chiến lược giảm thiểu khác nhau: FAIIR làm giàu chân lý nền của mình bằng một nghiên cứu đồng thuận chuyên gia nhỏ; Pebble có thể giảm thiểu bằng cách lấy mẫu nhiều LLM-thẩm-định (judges) hoặc tái-gắn-nhãn khi có bất đồng.
- **Cấu trúc đầu (head).** FAIIR có 19 đầu sigmoid độc lập được huấn luyện với BCE — một thiết lập đa-nhãn phân loại thuần túy. Đầu phân loại của Pebble không đồng nhất (hồi quy + softmax + BCE qua các chiều). Chính sách ngưỡng theo-từng-đầu sạch sẽ của FAIIR không chuyển giao một-đối-một, nhưng **nguyên tắc điều chỉnh ngưỡng theo-từng-đầu-ra** thì áp dụng trực tiếp cho các đầu sigmoid/BCE của Pebble.
- **Xử lý an toàn.** Cơ chế thiên-về-an-toàn của FAIIR thuần dựa trên ngưỡng — ba mức (0,4 / 0,3 / 0,2) được chọn theo tần suất nhãn và tầm quan trọng vận hành. Pebble dự định một can thiệp nặng hơn: trọng số mất mát cao cho lớp dương và một sàn recall ≥ 0,95 rõ ràng trên các chiều trọng yếu. Kế hoạch của Pebble nghiêm ngặt hơn nhưng được hỗ trợ tốt bởi minh chứng thực nghiệm của FAIIR rằng "mô hình rất hiệu quả trong việc xác định các nhãn liên quan, nhưng đôi khi cũng có thể xác định các vấn đề không liên quan trong cuộc hội thoại" là một sự đánh đổi chấp nhận được cho một công cụ hỗ-trợ-phân-loại-ưu-tiên.
- **Kỹ thuật chuyển giao được cho Pebble.** (a) **Điều kiện hóa ưu-tiên-như-tiền-tố** — FAIIR tiêm cờ ưu tiên dựa-trên-luật như một câu nguyên văn ở đầu đầu vào thay vì như một đặc trưng riêng biệt; Pebble có thể tương tự tiêm bất kỳ tín-hiệu-meta nào (mức độ nghiêm trọng, vị trí trong phiên, nguồn) như một tiền tố văn bản mà không cần sửa đổi kiến trúc đầu. (b) **Tiền huấn luyện tiếp tục bằng MLM trên kho ngữ liệu trong-miền** trước khi tinh chỉnh tác vụ — FAIIR chạy 1 epoch với 15% che trên toàn bộ kho ngữ liệu và ghi nhận công lao của nó cho cả việc tăng hiệu năng lẫn việc "giải quyết các thiên lệch nhãn". Đối với kho ngữ liệu hội-thoại-cảm-xúc của Pebble, đây là một bước rẻ tiền, đòn-bẩy-cao. (c) **Điều chỉnh ngưỡng theo-từng-chiều theo tần suất lớp** — phép chia 0,4/0,3/0,2 của FAIIR là một chính sách đơn giản, có thể bảo vệ được, đánh bại một ngưỡng toàn cục duy nhất. (d) **Cụm nhỏ để giảm phương sai với ít nhất một thành viên oversampling lớp hiếm** — cụm 3-Longformer của FAIIR (hai với oversampling, một không) là một mẫu thực tiễn để nắm bắt cả hành vi lớp-phổ-biến được hiệu chuẩn lẫn recall trên các lớp hiếm. (e) **Đồng thuận chuyên gia có cấu trúc trên một tập khó nhỏ** như một sự thay thế cho việc tái-chú-thích đầy đủ — Pebble không thể tái-gắn-nhãn kho ngữ liệu bạc của mình, nhưng một đồng thuận chuyên gia 40-cuộc-hội-thoại × 6-người-đánh-giá trên một mẫu khó được cố ý chọn là một cổng kiểm chứng khả thi đã thay đổi đáng kể chính sách ngưỡng của FAIIR.

## 11. Đề xuất sử dụng trích dẫn

Trong một bài báo của Pebble, FAIIR có thể được trích dẫn để hỗ trợ các tuyên bố cụ thể sau:

- **Quy mô và mức độ liên quan vận hành của NLP đường-dây-khủng-hoảng.** "FAIIR được phát triển trên 703.975 cuộc hội thoại hỗ trợ khủng hoảng dựa trên văn bản đã được ẩn danh được trao đổi... từ tháng 1 năm 2018 đến tháng 2 năm 2023" (Phương pháp §5.2). Dùng cái này để xác lập rằng các bộ phân loại sức khỏe tâm thần ở quy-mô-sản-xuất, trong-miền giờ đây là một thực tế đã được công bố, không phải suy đoán.
- **Khoảng cách nhu-cầu–năng-lực thúc đẩy sự hỗ trợ của ML.** "Kể từ khi ra mắt dịch vụ văn bản vào năm 2018, KHP đã tạo điều kiện cho hơn 1 triệu lượt tương tác qua Tin nhắn Văn bản (SMS), với mức tăng đáng kể 51% được ghi nhận trong đại dịch COVID-19 vào năm 2020" (Giới thiệu). Dùng để thúc đẩy khung tăng-cường-nhân-viên-ứng-phó của Pebble.
- **Trần hiệu năng đạt được trên nhãn vận hành nhiễu.** "FAIIR đạt AUC ROC trung bình 94%, điểm F1 trung bình theo mẫu 64%, và điểm recall trung bình theo mẫu 81% trên tập kiểm tra hồi cứu" (Tóm tắt; Kết quả §2.1). Dùng làm một chuẩn so sánh cho điều gì là thực tế trên các kho ngữ liệu sức khỏe tâm thần nhiễu.
- **Tính bền vững của bộ phân loại transformer trong-miền dưới sự trôi dạt theo thời gian.** "Mức giảm dưới 2% về precision, recall và F1 trung bình theo mẫu" giữa kiểm tra hồi cứu và kiểm tra im lặng tiền cứu 8 tháng (Thảo luận §3). Trích dẫn để biện minh rằng đánh giá tiền cứu là khả thi và mang lại thông tin.
- **Đường cơ sở công-bằng-nhân-khẩu-học.** Độ lệch chuẩn F1 trên 27 phân nhóm vẫn < 0,025 (Kết quả §2.1, Bảng 2). Trích dẫn như bằng chứng rằng các bộ phân loại transformer được thích-ứng-miền có thể công bằng một cách xấp xỉ trên các tầng nhân khẩu học chính, đồng thời vẫn đảm bảo việc báo cáo theo phân nhóm.
- **Nhiễu một-người-chú-thích như một hạn chế cấu trúc, không phải lỗi của mô hình.** "Sự đồng thuận của chuyên gia với FAIIR vượt qua sự đồng thuận của họ với các nhãn gốc" (Tóm tắt; Thảo luận §3). Trích dẫn để biện minh cho chiến lược gắn-nhãn-bạc đa-thẩm-định được lên kế hoạch của Pebble.
- **Điều chỉnh ngưỡng theo-từng-lớp như một đòn bẩy an toàn có thể triển khai.** Ngưỡng 0,4 cho các nhãn tần-suất-cao-nhất, 0,3 cho tần-suất-tiếp-theo, 0,2 cho phần đuôi dài (Phương pháp §5.4). Trích dẫn như tiền lệ cho chính sách ngưỡng/sàn-recall theo-từng-chiều của Pebble.
- **MLM thích-ứng-miền như một đóng góp đo lường được.** "Thích ứng miền thông qua học tự giám sát nâng cao đáng kể hiệu năng công cụ, đặc biệt trong các tác vụ có giám sát và khi giải quyết các thiên lệch nhãn" (Thảo luận §3). Trích dẫn để biện minh cho một bước tiền-huấn-luyện-tiếp-tục bằng MLM của Pebble.

Những mục KHÔNG nên trích dẫn từ bài báo này (vì chúng không được báo cáo): các chỉ số hiệu chuẩn / ECE, khảo sát loại bỏ chính thức cô lập tiền tố cờ-ưu-tiên, khảo sát loại bỏ chính thức cô lập đóng góp của MLM, thống kê đồng thuận theo-từng-thẩm-định ngoài con số nổi bật 90,9%, các con số về độ trễ hay chi phí suy luận cho cụm được triển khai, và bất kỳ dữ liệu kết quả sau-triển-khai nào — kiểm tra im lặng là giai đoạn mới nhất được báo cáo.

## Nghiên cứu sâu — đọc toàn-bộ-PDF (2026-06-10)

> Đọc dựa trên bản đã xuất bản của npj Digital Medicine (s41746-025-01647-6); PDF cục bộ là
> `pdfs/01-faiir.pdf` (arXiv:2405.18553). Bản chuyển đổi HTML của ar5iv cho bài báo này bị hỏng
> ("Fatal error"), nên các trích dẫn bên dưới đến từ toàn văn của npj. Phần này chỉ bổ sung những gì
> §§1–11 ở trên chưa đề cập; các tham chiếu chéo trỏ ngược lại các phần đó.

### Những gì bài báo đầy đủ bổ sung ngoài phân tích hiện có

- **Lộ trình quản trị: hoàn toàn không có REB/IRB.** "Ấn phẩm này là kết quả của một sáng kiến cải tiến
  chất lượng tại Kids Help Phone, và do đó, không có phê duyệt REB nào được tìm kiếm hay
  thu được." §4 ở trên nói "Không có số hiệu IRB bên ngoài nào được báo cáo" — sự thật còn mạnh hơn: *toàn
  bộ* nghiên cứu khủng-hoảng-thanh-thiếu-niên với 780 nghìn cuộc hội thoại chạy dưới một khung cải-tiến-chất-lượng
  nội bộ cộng với chính sách quyền riêng tư của KHP (thông báo đồng thuận, giảm thiểu dữ liệu, lưu trữ
  trong-hạ-tầng truy-cập-có-kiểm-soát). Đó là một mẫu quản trị có chủ ý, không phải một sự thiếu sót.
- **Việc lấy mẫu thẩm-định-chuyên-gia là nửa-ngẫu-nhiên, nửa-đối-kháng.** 40 cuộc hội thoại chia
  thành 20 cuộc được *chọn ngẫu nhiên* trong số những cuộc có ≥4 nhãn (đa dạng, khó) và 20 cuộc được *tuyển chọn
  có chủ đích* — <3 nhãn, mơ hồ một cách cố ý, hoặc nghi ngờ bị gắn nhãn sai — được chọn sao cho cả 19 nhãn đều
  được bao phủ. Sáu đánh giá cho mỗi cuộc hội thoại: 3 mở (dự đoán FAIIR hiển thị, đánh giá
  mức độ hữu ích) và 3 mù (gắn nhãn từ đầu). Việc tinh chỉnh lại ngưỡng sau nghiên cứu mua được một
  "mức tăng 4%" về precision (0,62→0,66) với cái giá về recall (0,82→0,76).
- **Xuất xứ của cờ ưu tiên.** Thuật toán phân loại ưu tiên *thuộc sở hữu của Crisis Text Line*, không phải KHP, và
  kích hoạt chỉ trên *tin nhắn đầu tiên* của người dùng: "sự hiện diện của bất kỳ từ nào trong 56 từ tiếng Anh hoặc 73 từ tiếng Pháp trong
  một tin nhắn ban đầu từ người dùng dẫn đến việc tự động phân loại họ lên một mức ưu tiên cao hơn".
  Rủi ro cao = ý nghĩ tự tử + kế hoạch + khả năng tiếp cận phương tiện + mốc thời gian 0–48 giờ; trung bình = ý nghĩ tự tử
  hoặc tự gây thương tích. Phân bố: 87% trung bình / 13% cao / ~0,0001% thấp.
- **Khả năng giải thích = layer-integrated gradients.** Các từ khóa được trích xuất theo từng nhãn thông qua
  layer-integrated gradients, được lọc bỏ các stop-word/dấu câu/token đặc biệt và một
  danh sách từ-thông-dụng được định trước ("User", "Hello"). Các từ khóa của nhãn Suicide: *happy, sad, mood,
  anxiety, scared, pain, plan, home, school, friend*; *assault* chỉ tới Abuse-Sexual trong khi
  *mom/dad* thiên về Abuse-Physical. Các tác giả thừa nhận độ tin cậy "cần được đánh giá nghiêm ngặt hơn nữa"
  và báo cáo **không có phản hồi của CR** về tính hữu ích của từ khóa.
- **Cách tổng hợp cụm không được nêu rõ.** Quy tắc kết hợp của cụm 3-Longformer (biểu quyết so với
  trung bình xác suất) không bao giờ được nêu — một khoảng trống thực sự nếu Pebble muốn sao chép công thức; chỉ
  có sự khác biệt ở cấp-thành-viên được đưa ra (2 trong 3 oversampling các nhãn hiếm; tất cả đều chia sẻ cùng một
  lượt MLM với che 15%, 1 epoch).
- **Ngôn ngữ thanh thiếu niên được thừa nhận nhưng không bao giờ được phân tích.** Sự xử lý duy nhất là nhiễu chung chung:
  "chất lượng khác nhau của các cuộc hội thoại, bao gồm sự khác biệt trong cách dùng ngôn ngữ, ngữ pháp, và sự
  hiện diện của nhiễu như lỗi chính tả hoặc tiếng lóng". Không có phân tích về cách những người 10–19 tuổi thực sự
  diễn đạt sự đau khổ (sự gián tiếp, emoji, chuyển-mã (code-switching), nhịp điệu tin nhắn). Trên *kho ngữ liệu khủng hoảng
  thanh thiếu niên lớn nhất trong y văn*, phân tích đó đơn giản là chưa tồn tại.

### Những phần hữu ích trực tiếp cho Pebble

1. **Mẫu thẩm định hai-giai-đoạn** (kiểm tra im lặng → đồng thuận 40-cuộc-hội-thoại × 6-người-đánh-giá với
   phân chia mở/mù và năm tiêu chí đồng thuận được đăng-ký-trước) — giao thức *duy nhất* đã được công bố,
   chuyên-cho-khủng-hoảng-thanh-thiếu-niên để thẩm định một bộ phân loại so với chuyên gia khi nhãn chân-lý-nền
   bị nhiễu.
2. **Mẫu thiết-kế-leo-thang**: một lớp từ-khóa/luật rẻ tiền, có thể kiểm toán mà *leo thang* (không bao giờ
   hạ-cấp) + lớp mô hình bên dưới + tiêm phán quyết của luật như một tiền tố văn bản
   (`"This conversation is of <<X>> priority"`). Ba lớp an toàn độc lập, mỗi lớp đều đơn giản.
3. **Mẫu quản trị cho dữ liệu của trẻ vị thành niên**: khung cải-tiến-chất-lượng, thông báo đồng thuận,
   làm sạch tự động thành `[scrubbed]`, lưu trữ nội-bộ truy-cập-có-kiểm-soát, không công bố mở —
   với cái giá đã biết là việc làm-sạch-quá-mức xóa đi những từ vô hại và thêm nhiễu nhãn.
4. **Việc xây dựng tập đánh giá nửa-ngẫu-nhiên/nửa-đối-kháng** (20 cuộc khó-ngẫu-nhiên + 20 cuộc tuyển chọn
   mơ-hồ/nghi-ngờ-gắn-nhãn-sai bao phủ mọi lớp).
5. **Chính sách ngưỡng recall-trước với một đường cong lợi-ích được công bố**: ngưỡng theo-từng-lớp theo
   tầng tần suất (0,4/0,3/0,2), và hệ quả đo lường được +4% precision / −6% recall của việc
   siết chặt sau phản hồi của chuyên gia.

### Cách mỗi phần giúp Pebble thành công

- **Thẩm định (1) → kế hoạch đánh giá của Pebble.** Các nhãn bạc của Pebble chính xác là "chân-lý-nền
  một-nguồn nhiễu" mà FAIIR đã đối mặt. Sao chép giao thức: trước bất kỳ tuyên bố triển khai nào, chạy một
  đồng thuận chuyên gia ~40-mục trên một lát cắt nửa-ngẫu-nhiên/nửa-đối-kháng của chính các cuộc hội thoại của Pebble,
  3 người đánh giá mù + 3 mở, và báo cáo mức đồng thuận mô-hình-so-với-chuyên-gia *bên cạnh* mức đồng thuận
  bạc-so-với-chuyên-gia. Kết quả nổi bật của FAIIR (mô hình đồng thuận với chuyên gia *nhiều hơn so với các nhãn gốc*,
  F1 0,64 so với 0,47, p<0,001) chính là lập luận mà Pebble sẽ cần khi một người phản biện nói "các nhãn
  Gemini của bạn bị nhiễu": các nhãn nhiễu vẫn có thể huấn luyện một mô hình đồng-thuận-vượt-trội so với chính
  sự giám sát của nó. Cụ thể: thêm một tài liệu giao thức `eval/expert_consensus/` + một phiếu chú thích 40-mục
  trước checkpoint được triển khai đầu tiên.
- **Mẫu leo thang (2) → đầu an toàn của Pebble không đơn độc.** Đừng để sàn recall ≥ 0,95
  chỉ tồn tại trong đầu đã-học. Thêm một dây-bẫy (tripwire) từ-khóa-tin-nhắn-đầu-tiên kiểu FAIIR (từ vựng của
  trẻ em, cả thuật ngữ tường minh và được mã hóa) mà chỉ có thể *nâng* mức rủi ro, và đưa
  mức đó trở lại bộ mã hóa như một tiền tố văn bản — không thay đổi kiến trúc, và Bảng D3 của FAIIR
  (P/R phẳng giữa các tầng ưu tiên) cho thấy tiền tố không làm méo hiệu năng theo-từng-lớp. Đầu
  đã-học khi đó chỉ cần đánh bại lớp từ-khóa, không phải thay thế nó.
- **Quản trị (3) → câu chuyện triển khai của Pebble.** Pebble không thể thu thập dữ liệu trò chuyện của trẻ em dưới
  một chế độ dữ-liệu-mở. FAIIR chứng minh hình dạng khả thi: lưu trữ trong-hạ-tầng, làm sạch,
  thông báo đồng thuận, truy cập nghiên cứu theo yêu cầu. Áp dụng nó sớm (phần xử lý dữ liệu của bài báo
  + chính sách kho mã), và dự trù cho chi phí nhiễu-do-làm-sạch mà FAIIR ghi nhận (việc xóa "turkey" →
  nhiễu trong-lúc-huấn-luyện).
- **Xây dựng tập đánh giá (4) → phép chia tập kiểm tra của Pebble.** Tập kiểm tra C-SSRS của Pebble nhỏ (~100
  hàng); một lát cắt thuần ngẫu nhiên sẽ chứa hầu như không có trường hợp mức-độ-nghiêm-trọng-cao nào. Xây dựng tập
  đánh giá được-giữ-riêng theo cách FAIIR: nửa khó-ngẫu-nhiên, nửa tuyển chọn để bao phủ mọi mức nghiêm trọng và các
  lỗi nhãn-bạc nghi ngờ — đó là điều đã làm cho 40 cuộc hội thoại của FAIIR đủ thông tin để thay đổi
  chính sách ngưỡng sản xuất.
- **Chính sách ngưỡng (5) → các điểm cắt của đầu an-toàn/cảm-xúc.** Điều chỉnh ngưỡng theo-từng-đầu,
  theo-từng-tầng-tần-suất trên tập kiểm định, và *công bố sự đánh đổi* (FAIIR: +4% P đổi lấy −6% R). Đối với Pebble, quy tắc
  đảo ngược trên đầu an toàn: cố định recall ở 0,95 và để precision thả nổi; đường cong đo lường được của FAIIR
  là trích dẫn cho việc sự đánh đổi này là chấp nhận được về mặt vận hành trong hỗ trợ khủng hoảng thanh thiếu niên.

### Lăng kính sức khỏe tâm thần trẻ em

Đây là bài báo duy nhất trong toàn bộ tập nghiên-cứu-liên-quan mà dữ liệu *chính là* trẻ em trong khủng hoảng
(KHP phục vụ những người ~10–19 tuổi; 1 triệu+ lượt tương tác SMS, +51% trong thời kỳ COVID). Các bài học cụ thể cho
sứ mệnh của Pebble:

- **Tín hiệu khủng hoảng của trẻ em có thể khôi phục được ở quy mô lớn.** Suicide AUROC 0,94, Self-Harm 0,97,
  Abuse-Sexual 0,98 trên SMS thanh thiếu niên thực — không phải các đại diện (proxy) từ mạng xã hội. Đây là minh chứng
  về sự tồn tại rằng các mục tiêu của đầu an toàn của Pebble là đạt được trên văn bản đăng-ký-trẻ-em, nơi mọi bài báo
  khác trong tập (C-SSRS, MentalBERT, WASSA) đều là dữ liệu Reddit/bài-luận của người lớn.
- **Nhưng mô hình không bao giờ quyết định.** Ranh giới vai trò của FAIIR — hỗ trợ gắn nhãn sau-hội-thoại và
  làm-nổi-bật-tín-hiệu, với "cứu hộ chủ động và báo cáo bắt buộc" luôn được thực hiện bởi một con người được đào tạo —
  là kiến trúc an toàn mà Pebble nên sao chép nguyên văn: các đầu của Pebble đưa thông tin vào một Decision
  Engine (Bộ máy Quyết định); việc leo thang tới một luồng con-người/người-chăm-sóc là một bất biến của sản phẩm, không phải đầu ra của mô hình.
- **Lớp luật trước, mô hình sau.** Đối với việc phát hiện rủi-ro-cận-kề, KHP *không* tin tưởng vào
  mô hình đã-học: một danh sách từ khóa trên tin nhắn đầu tiên xử lý việc leo thang, cố ý
  kích-hoạt-quá-mức (87% tất cả các cuộc hội thoại nằm ở mức trung bình). Đối với trẻ vị thành niên, dở-nhưng-có-thể-kiểm-toán
  thắng thông-minh-nhưng-mờ-mịt ở tầng cao-rủi-ro-nhất; sàn recall của Pebble cũng nên được
  chống lưng bởi các luật mà một bác sĩ lâm sàng có thể đọc.
- **Nhiễu một-người-chú-thích là chuẩn mực trong các dịch vụ trẻ em.** Các CR quá tải gắn nhãn một mình, không được rà soát —
  và nghiên cứu chuyên gia cho thấy các nhãn đó *tệ hơn* mô hình. Kế hoạch của Pebble dùng
  nhiều LLM-thẩm-định + một lát cắt đồng thuận con người là sự sửa chữa đúng đắn, và FAIIR là
  trích dẫn cho lý do tại sao điều đó là cần thiết.
- **Khoảng trống mở mà Pebble có thể sở hữu: ngôn ngữ đăng-ký-thanh-thiếu-niên.** FAIIR xử lý văn bản thanh thiếu niên nhưng không bao giờ
  mô tả đặc tính của nó; các từ khóa khả-năng-giải-thích của nó (*plan, home, school, friend* cho tự tử) gợi ý
  rằng các dấu hiệu rủi ro của trẻ em mang tính *quan-hệ-theo-ngữ-cảnh*, không phải từ vựng lâm sàng. Một lát cắt
  hiệu chuẩn đăng-ký-trẻ-em của Pebble và bất kỳ phân tích nào về ngôn ngữ đau khổ gián tiếp/được mã hóa của trẻ em
  sẽ là một đóng góp đích thực mà chưa ai — kể cả FAIIR — công bố.
- **Bất đối xứng về đạo đức cần tôn trọng.** FAIIR không chạy REB vì nó vẫn là một công cụ
  cải-tiến-chất-lượng nội bộ trên dữ liệu dịch vụ đã-được-thu-thập. Pebble, với tư cách một sản phẩm hướng-tới-trẻ-em mới
  tạo ra văn bản khủng hoảng tổng hợp (nhãn bạc Gemini) và đưa ra các quyết định trực tiếp,
  không thể tuyên bố cùng một sự miễn trừ — hãy lên kế hoạch cho việc rà soát đạo đức thực sự, sự đồng thuận phù-hợp-với-độ-tuổi, và
  chính sách thông-báo-người-giám-hộ ngay từ đầu.

### Hạn chế & câu hỏi mở cho Pebble

- **Không có hiệu chuẩn ở bất cứ đâu** (không có đường cong ECE/độ tin cậy) — nhưng Decision Engine của Pebble tiêu thụ
  xác suất, không phải nhãn. Pebble phải thêm phần đánh giá hiệu chuẩn mà FAIIR đã bỏ qua.
- **Không có khảo sát loại bỏ MLM hay tiền tố** — FAIIR *tuyên bố* MLM thích-ứng-miền "nâng cao đáng kể"
  hiệu năng nhưng không bao giờ cô lập nó. Khảo sát loại bỏ lượt-MLM được lên kế hoạch của Pebble trên NeoBERT sẽ là
  phép đo sạch đầu tiên trong miền này.
- **Cách tổng hợp cụm không được nêu rõ** — nếu Pebble sao chép công thức 3-thành-viên/2-oversampling, thì
  quy tắc kết hợp (trung bình xác suất so với biểu quyết đa số) phải được chọn và báo cáo; FAIIR không đưa ra
  hướng dẫn nào.
- **Chỉ ở cấp-độ-hội-thoại.** FAIIR gắn nhãn cho toàn bộ cuộc hội thoại sau-thực-tế; Pebble phải chấm điểm
  *theo-từng-lượt, giữa-cuộc-hội-thoại* — các con số của FAIIR không phải là các thanh so sánh trực tiếp,
  chỉ là một tương đồng cận-trên (giới hạn 2.000 token của nó bao phủ 94,4% các cuộc đối thoại, tuy nhiên, là bằng chứng
  trực tiếp rằng cửa sổ 4K của NeoBERT là dư dả cho miền này).
- **Truy cập bị giới hạn (gated).** Mã nguồn riêng tư (`KidsHelpPhone/AI-ML`, theo yêu cầu), dữ liệu đóng. Câu
  hỏi mở đáng giá một email: liệu KHP có chia sẻ các định nghĩa của hệ phân loại 19-nhãn và các
  danh sách từ-khóa-leo-thang EN/FR hay không — cả hai đều có thể tái-sử-dụng trực tiếp cho lớp luật của Pebble.
- **Sự không khớp về dân số ở rìa.** Những người nhắn tin của KHP là những người tự-chọn tìm-kiếm-trợ-giúp, người trả lời
  điển hình là nữ/gốc-Âu, 67,3% có khuyết tật vô hình trong số những người trả lời về bản dạng —
  những người dùng ứng-dụng-bạn-đồng-hành của Pebble (trẻ hơn, chưa tìm-kiếm-trợ-giúp) có thể biểu lộ rủi ro sớm hơn và
  gián tiếp hơn so với những gì kho ngữ liệu này cho thấy.
