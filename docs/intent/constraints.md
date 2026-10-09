# Pebble-LLM: lồng tiếng Việt có cảm xúc cho phim nước ngoài (tầng intent)

> **Layer:** intent. File này chỉ thay đổi khi người quyết định có chủ ý, không bao giờ
> là tác dụng phụ của việc viết code hay sửa spec (xem `WORKFLOW.md`). Nếu một thay đổi
> code/spec cần sửa file này thì dừng lại: đó là việc người quyết, không phải chi tiết PR.
>
> **Pivot 2026-10-09 (người quyết).** Mục đích của dự án đổi thành **nghiên cứu và tự xây
> model lồng tiếng Việt** cho phim nước ngoài (Mỹ, Hàn, Trung, …) khi đưa về Việt Nam.
> Đầu ra là **paper**. Corpus **ViEmoSpeech** và SER tone×emotion (mục đích cũ) **được giữ
> lại làm thành phần** (§3). Bản intent trước pivot:
> `git show fc4dad7:docs/intent/constraints.md`. Các chương trình trước nữa (text
> suicide-risk, crisis voice affect, classifier v1–v3) vẫn nằm trong `archive/`.

## 1. Dự án để làm gì

Lồng tiếng là việc **thay tiếng thoại gốc của phim bằng tiếng Việt**. Mỗi nhân vật được
gán một giọng Việt riêng. Câu thoại Việt phải khớp thời lượng câu gốc, và nhạc nền cùng
hiệu ứng âm thanh (M&E) của phim được giữ nguyên.

**Đầu vào là kịch bản tiếng Việt có sẵn.** Mỗi câu thoại có nhân vật, câu chữ, **nhãn cảm
xúc** và khung thời gian. Vì vậy dịch thuật và nhận diện cảm xúc từ audio gốc **nằm ngoài
scope**, và ngôn ngữ gốc của phim không ảnh hưởng đến model.

Model nhận một câu thoại và sinh audio tiếng Việt thoả cả ba yêu cầu:

- **Đúng nhãn cảm xúc** ghi trong kịch bản.
- **Thanh điệu không méo vì cảm xúc.** Tiếng Việt dùng cao độ (F0) cho cả thanh điệu lẫn
  cảm xúc. Đẩy cảm xúc mạnh mà làm sai thanh thì sai luôn nghĩa từ. Đây là giả thuyết
  tone×emotion của chương trình cũ, chuyển từ phía *nhận diện* sang phía *sinh*, và là hook
  chính của paper.
- **Vừa khung thời gian** của câu gốc.

Phim chỉ là nơi kiểm chứng, không phải sản phẩm.

"Làm đúng" nghĩa là:
- mọi giọng phát ra thuộc kho giọng hợp lệ;
- mọi con số truy được về một báo cáo do script đã commit sinh ra;
- không có gì vi phạm pháp lý hay đạo đức rời khỏi máy trước khi qua rà soát pháp lý.

| | |
|---|---|
| **Scope (in)** | Model sinh giọng Việt điều khiển bằng nhãn cảm xúc + khớp thời lượng; giữ đúng thanh điệu; kho giọng từ dataset mở; tách thoại khỏi M&E và trộn lại; đánh giá bằng người nghe; corpus ViEmoSpeech + SER làm thành phần (§3); paper |
| **Scope (out)** | Dịch thuật; nhận diện cảm xúc từ audio gốc; khớp khẩu hình bằng cách sửa hình; phát hành phim đã lồng tiếng; sản phẩm thương mại; clone giọng diễn viên (phim gốc, phim Việt, bản lồng tiếng Việt chính thức); các chương trình trong `archive/` |
| **Ràng buộc cứng** | **Giọng phát ra chỉ thuộc kho giọng hợp lệ** (§2.2). **Media có bản quyền không bao giờ được commit hay phát hành** (§2.1). **Không công bố gì trước khi qua rà soát pháp lý** (§2.8) |
| **Không thương lượng** | **Hợp pháp quan trọng hơn chất lượng.** Một bản lồng hay hơn mà dùng giọng không hợp lệ hoặc phát hành media có bản quyền thì vô giá trị |

## 2. Ràng buộc chi phối mọi thứ

1. **Media có bản quyền.** Gồm:
   - phim hoạt hình dùng để test, cùng **bản lồng tiếng Việt chính thức** của chúng;
   - phim truyền hình Việt của ViEmoSpeech;
   - mọi clip cắt ra, transcript và kịch bản đầy đủ;
   - **audio sinh ra cho các phim đó**.

   Những thứ trên không bao giờ commit, không bao giờ phát hành. `data/**` luôn nằm trong
   gitignore. Thứ được phép phát hành (sau §2.8): đặc trưng, timestamp, nhãn, speaker id,
   model và vector điều khiển, **và audio demo chỉ dùng câu chữ tự viết**. Ngoại lệ stream
   cho annotator được mời (ADR-005) vẫn giữ nguyên.

2. **Kho giọng hợp lệ.** Mỗi nhân vật được gán một giọng lấy từ **dataset giọng Việt mở**,
   thoả cả hai điều kiện:
   - (a) license cho phép dùng để nghiên cứu và công bố paper;
   - (b) giọng được **thu âm cho chính dataset đó** (người nói đọc để đóng góp dữ liệu),
     không phải cào từ YouTube, sách nói hay phim.

   Mỗi giọng trong kho được ghi lại: dataset, speaker id, license, và căn cứ của (b). Điều
   này **cấm** dùng giọng (timbre) của diễn viên phim gốc, của diễn viên phim Việt trong
   ViEmoSpeech, của diễn viên lồng tiếng trong bản Việt chính thức, hay của dataset cào
   (viVoice, PhoAudiobook…), **kể cả chỉ để làm audio tham chiếu**.

3. **Cảm xúc đúng nhãn, đo bằng người nghe.** "Đúng cảm xúc" là người nghe mù nhận ra đúng
   nhãn trong kịch bản. Không được báo cáo bằng độ tương đồng embedding (emotion2vec E-SIM)
   như thể đó là độ chính xác, vì E-SIM thưởng cho việc bắt chước âm học
   (`docs/papers/vietnamese-emotional-tts.md`). Số đo tự động chỉ là số phụ.

4. **Thanh điệu nguyên vẹn.** Tỉ lệ sai thanh của audio sinh ra so với kịch bản là số đo
   bắt buộc trong mọi báo cáo chất lượng.

5. **Khớp thời lượng.** Mỗi câu sinh ra phải nằm trong khung thời gian của câu gốc. Độ lệch
   là số đo bắt buộc. Khớp khẩu hình nằm ngoài scope.

6. **Đánh giá trung thực.** Phim, nhân vật và giọng trong tập test phải **tách rời** tập
   dùng để phát triển. Mọi con số truy được về báo cáo do script đã commit sinh ra. Đánh giá
   bằng người ghi rõ: ai chấm, chấm mù hay không, và độ đồng thuận giữa người chấm.

7. **Gắn nhãn nội dung do AI tạo.** Mọi audio sinh ra, kể cả bản demo, phải được gắn nhãn
   là do AI tạo. *(Căn cứ: Nghị định 142/2026/NĐ-CP, theo nguồn thứ cấp; **cần xác nhận lại
   văn bản gốc**.)*

8. **Rà soát pháp lý trước khi công bố (người quyết 2026-10-09).** Được phép dùng media có
   bản quyền (§2.1) làm dữ liệu train và test **trong máy** để nghiên cứu. **Trước khi** nộp
   paper, công bố demo, hay phát hành bất kỳ artifact nào, đội pháp lý phải rà soát và đồng
   ý. Việc rà soát này không thay thế §2.1 và §2.2; hai ràng buộc đó vẫn luôn áp dụng.

## 3. ViEmoSpeech: thành phần phục vụ lồng tiếng

Corpus cảm xúc tiếng Việt (phim truyền hình VN, nhãn người) và SER tone×emotion được giữ
lại với ba vai trò:

- **Dữ liệu cảm xúc để train** (người quyết D5, 2026-10-09). Cho phép dùng audio để model
  học **cách thể hiện cảm xúc tiếng Việt**, kể cả train hoặc fine-tune. Giọng phát ra vẫn
  phải thuộc kho §2.2. Đây chính là bài toán chuyển cảm xúc từ người này sang giọng người
  khác (tương tự sub-task 2 của VLSP 2022). Phải đo để chắc giọng sinh ra không giống
  diễn viên trong corpus.
- **Thước đo:** SER, chú thích thanh điệu từng âm tiết, công cụ gán nhãn cho người nghe mù.
- **Bộ nhãn:** 7 lớp cảm xúc + valence/arousal của corpus là ứng viên cho nhãn cảm xúc
  trong kịch bản (D10).

Các ràng buộc riêng của corpus vẫn giữ nguyên:

- **Một người nói mỗi clip.** Clip cắt tại (VAD ∩ speaker-turn); clip bị người gán nhãn
  đánh dấu nhiều giọng thì bị loại.
- **Chia tập theo speaker.** Chia theo speaker, không theo clip; speaker của tập test tách
  rời tập train (ADR-002).
- **Nhãn do người gán.** Nhãn là của người gán (ADR-003). Gợi ý của LLM chỉ để hiển thị.
- **Truy nguồn.** Mỗi dòng nhãn mang annotator id và timestamp; prompt gợi ý được ghim
  trong git.
- **Thanh điệu và phương ngữ.** Mỗi utterance có chú thích thanh điệu và phương ngữ.
- **Distress là proxy.** Cờ distress là proxy trong phim diễn, không phải nguy cơ lâm sàng.

## 4. Quyết định

### 4.1 Đã chốt (người quyết, 2026-10-09)

| # | Câu hỏi | Quyết định |
|---|---|---|
| — | Bản chất dự án | Nghiên cứu, tự xây model |
| — | Hình thức | Lồng tiếng đầy đủ (không phải thuyết minh) |
| — | ViEmoSpeech | Giữ làm thành phần (§3) |
| D1 | Đầu vào | Kịch bản tiếng Việt có sẵn |
| D2 | Cảm xúc lấy từ đâu | Nhãn ghi sẵn trong kịch bản, theo từng câu |
| D3 | Kho giọng | Dataset giọng mở có license (§2.2) |
| D5 | Audio phim Việt có được train không | Được; rà soát pháp lý trước khi công bố (§2.8) |
| D6 | Ngôn ngữ nguồn | Không liên quan: đầu vào luôn là kịch bản Việt |
| D7 | Phim test | Phim hoạt hình giàu cảm xúc, kiểu *Inside Out* |
| D9 | Đầu ra | Paper |

### 4.2 Chưa chốt: người phải quyết trước khi viết spec

Không change nào dưới `docs/spec/changes/` được đoán thay các câu hỏi này.

| # | Câu hỏi | Chặn việc gì |
|---|---|---|
| D4 | **Model nền:** fine-tune hoặc steer model mở (F5-TTS-Vietnamese, VieNeu…) hay train từ đầu. Weights F5-TTS gốc là phi thương mại; với paper thì được | Kế hoạch compute |
| D8 | **Tiêu chí thành công + mốc so sánh:** ngưỡng cho khớp cảm xúc (người nghe), tỉ lệ sai thanh, độ lệch thời lượng, độ tự nhiên. Mốc so sánh: bản lồng tiếng Việt chính thức của phim (người diễn) và/hoặc ElevenLabs Dubbing | Định nghĩa "xong" |
| D10 | **Nhãn cảm xúc trong kịch bản:** dùng bộ nhãn nào (7 lớp ViEmoSpeech? có cường độ không?), và **ai gán nhãn** cho kịch bản của phim test (kịch bản thường không có sẵn nhãn) | Tạo dữ liệu test |
| D11 | **Nguồn kịch bản + khung thời gian cho phim test:** phụ đề Việt chính thức, hay chép lại từ bản lồng tiếng Việt (có sẵn cả câu chữ lẫn thời gian)? | Tạo dữ liệu test |
| D12 | **Giọng cho nhân vật trẻ em / giọng cách điệu.** Hoạt hình có nhiều nhân vật trẻ em và giọng kịch tính, trong khi dataset mở chủ yếu là người lớn đọc văn bản. Chấp nhận lệch tuổi, hay tìm thêm dataset? | Kho giọng (D3) có đủ không |
| D13 | **Danh sách phim test cụ thể** (ứng viên: `docs/papers/vietnamese-emotional-tts.md` §6) | Đánh giá end-to-end |

Binding invariants: [invariants.md](invariants.md).
