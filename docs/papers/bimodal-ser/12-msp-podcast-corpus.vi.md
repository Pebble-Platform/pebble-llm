# Paper 12 — The MSP-Podcast Corpus

> Bản dịch tiếng Việt của [12-msp-podcast-corpus.md](12-msp-podcast-corpus.md) — cập nhật 2026-07-10.

- **Tác giả:** Carlos Busso, Reza Lotfian, Kusha Sridhar, et al.
- **Venue / năm:** arXiv 2025 (đã nộp cho IEEE Trans. Affective Computing)
- **Liên kết:** abs https://arxiv.org/abs/2509.09791 · PDF `pdfs/12-msp-podcast-corpus.pdf`
- **Nhóm:** khảo sát / benchmark (dataset paper)

**Tóm tắt:** Dataset paper canonical cho MSP-Podcast: 400+ giờ, chú thích (annotation) categorical + continuous (valence/arousal/dominance).

**Mức độ liên quan đến Pebble:** Tiền lệ được công bố (published) gần nhất về thiết kế nhãn categorical + continuous (dual-head) — bắt buộc phải trích dẫn (citation) nếu đánh giá (eval) trên MSP-Podcast.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa đọc sâu (deep-read).

## Phân tích (mức độ trùng lặp với Pebble)

**Hồ sơ tổng hợp (tại thời điểm phân tích).** Luồng *chính* (primary) của Pebble là
bài toán phân loại **văn bản** nguy cơ tự sát theo thang thứ tự (ordinal), kiểm tra
xem nhãn LLM/weak có thực sự tăng cường một cách trung thực cho tập gold lâm sàng
khan hiếm hay không, dưới ràng buộc **gold-holdout** nghiêm ngặt, chia tách theo
subject-level, các metric nhạy với tính thứ tự (QWK/MAE/macro-F1), và đạo đức dữ
liệu lâm sàng (`docs/intent/constraints.md`). Luồng *đang hoạt động, liền kề*
(adjacent active) **voice** (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`)
gắn thêm **các head MTL không đồng nhất (heterogeneous) trên một backbone SSL đóng
băng (WavLM-Large / emotion2vec)**: emotion CE + **affect (valence/arousal) CCC** +
crisis BCE dưới một **ngưỡng sàn recall cứng (hard recall floor)**, cân bằng bằng
Kendall uncertainty weighting. Lộ trình (roadmap) voice nêu đích danh **MSP-Podcast
(A/V/D) là mục tiêu nhãn thật tiếp theo cho affect head** (hiện đang dùng nhãn
proxy Russell-circumplex).

### Phân tích — MSP-Podcast Corpus (Busso và cộng sự)
- **Mức trùng lặp:** D1=2, D2=0, D3=2, D4=0, D5=1, D6=0, D7=2 →
  (3·2 + 2·0 + 1·2 + 2·0 + 2·1 + 2·0 + 1·2) / 26 = 12/26 = **46% (liền kề)**
- **Gần nhất ở:** D1 (baseline SER thực sự là một tập hợp head không đồng nhất —
  categorical **focal** + continuous **CCC**, được huấn luyện theo giai đoạn rồi
  joint-train) và D7 (các baseline là **WavLM / Wav2vec2 / HuBERT ~310M SSL**, đúng
  họ backbone mà luồng voice của Pebble đóng băng); D3 bám sát phía sau (đây CHÍNH LÀ
  corpus affect được nêu tên cho head V/A/D).
- **Điểm tốt nhất (baseline cần vượt qua):** Section VI đưa ra một công thức
  (recipe) affect đã công bố kèm số liệu — thích nghi (adapt) một bộ mã hóa SSL bằng
  **CCC loss để dự đoán valence/arousal/dominance, sau đó joint-train cùng head
  categorical focal** (giai đoạn attribute dùng một bộ mã hóa đóng băng + head
  regression riêng cho từng attribute), với CCC của WavLM trên Test1 là
  **V≈0.72 / A≈0.72 / D≈0.65** (Table VII).
  - **Cách áp dụng cho Pebble:** khi affect head của voice chuyển từ nhãn proxy V/A
    sang nhãn thật A/V/D của MSP-Podcast (nhiệm vụ tiếp theo trong roadmap), áp
    dụng công thức CCC-theo-giai-đoạn-rồi-joint này trên thân WavLM đóng băng, và
    báo cáo CCC của affect head so với các con số theo từng test-set của WavLM ở
    trên như baseline cần vượt qua — biến cơ chế nhãn proxy thành một kết quả
    affect thật, có thể trích dẫn được.
- **Lưu ý (caveats):** (1) Không có nhãn sức khỏe tâm thần/crisis hay nhãn lâm sàng
  (D2=D6=0) — corpus này chỉ nuôi được head **affect**; head crisis/recall-floor
  vẫn cần một nguồn dữ liệu lâm sàng (ví dụ DAIC). (2) Các baseline của họ
  **fine-tune** toàn bộ SSL ~310M, trong khi kế hoạch của Pebble dùng backbone
  **đóng băng** + probe — các con số CCC này là một ngưỡng trần tham chiếu
  (reference ceiling), không phải mục tiêu so sánh ngang hàng (like-for-like) trừ
  khi giao thức frozen-probe được khớp đúng. (3) Việc truy cập yêu cầu ký
  data-transfer agreement (329 nhóm), không phải tải miễn phí — cần chuyển cho
  `find-dataset` để xác nhận rào chắn (gate) này trước khi dựa vào nó.
  (4) Đã đọc sâu (deep-read) trang 1–2 + 13–15 (baseline, partition, thảo luận);
  các phần giữa (III–V, giao thức chú thích) mới chỉ đọc lướt, nên điểm cho phương
  pháp chú thích (D4) được lấy từ abstract + tóm tắt giao thức, chưa phải đọc toàn văn.

## Deep research — đọc toàn văn PDF (2026-07-10)

> Ghi chú hồ sơ (profile note): phần này được đọc và đối chiếu với **hồ sơ
> ViEmoSpeech hiện tại + Decision Register (V-A…V-H)** trong
> `docs/tasks/paper-deep-analysis.md`, KHÔNG phải khối "Analysis (overlap with
> Pebble)" (voice-MTL đã lưu trữ) ở trên (khối đó được chấm điểm từ trước khi pivot
> và chỉ được giữ lại như lịch sử). Mọi Decision ID bên dưới đều là V-x.

### Ghi chú về nguồn truy cập

Đọc toàn văn qua
`pdftotext "docs/papers/bimodal-ser/pdfs/12-msp-podcast-corpus.pdf" -`
(PDF local = arXiv:2509.09791v1, eess.AS, 11/9/2025 — đây là dataset paper bản
"phát hành cuối / v2.0", đã nộp cho *IEEE Trans. Affective Computing*; hiện chưa
có phiên bản venue xuất bản riêng nào khác, nên bản PDF arXiv/lab là bản có giá
trị tham chiếu). Mọi con số mang tính load-bearing bên dưới đều đã được đối chiếu
chéo (cross-checked) với bản render HTML trên arXiv.
- Truy vấn `MSP-Podcast corpus 409 hours 3641 speakers 267905 speaking turns Busso 2025`
  → https://arxiv.org/abs/2509.09791 và bản canonical của lab tại
  https://www.lab-msp.com/MSP/publications/Busso_2025.pdf (cả hai đều = cùng một
  paper). ✔ Đã xác nhận 409 giờ / 3,641 người nói / 267,905 lượt nói (turn).
- Truy vấn `MSP-Podcast WavLM baseline CCC valence 0.722 arousal Test1 categorical F1 macro focal loss`
  + WebFetch trang https://arxiv.org/html/2509.09791v1 → trả về nguyên văn toàn
  bộ Table VII / Table II / Table III / số liệu partition (tất cả đều ✔ được xác
  nhận bên dưới).
- Có một **mâu thuẫn nội tại (internal inconsistency)** được gắn cờ, không thể
  giải quyết bằng nguồn bên ngoài: phần văn xuôi (§IV-D và abstract trên arXiv)
  ghi "2,043 nữ, 1,598 nam", nhưng **Table IV** lại liệt kê Nữ **1,598** / Nam
  **2,043**. Không mang tính load-bearing ở đây; ghi chú lại để không ai trích
  dẫn tỷ lệ giới tính mà không kiểm tra lại bảng.

### Bài báo thực sự làm gì

Mô tả bản phát hành cuối cùng (v2.0), sau 10 năm xây dựng, của **MSP-Podcast**:
một corpus cảm xúc giọng nói tiếng Anh mang tính tự nhiên (naturalistic), được
khai thác (mined) từ các podcast Creative-Commons.

- **Quy mô (✔, §I, §V, Table VI):** 409 giờ; **267,905 lượt nói (speaking
  turns)**; **3,641 người nói** (1,598 nữ / 2,043 nam theo Table IV); **6,007
  podcast riêng biệt**; **1,446,270 lượt chú thích cảm xúc (emotion
  annotations)** từ 13,280 worker; **≥5 người chấm mỗi lượt nói** (Fig. 3). Bản
  chuyển văn (transcription) của con người cho *toàn bộ* corpus (qua REV.com):
  4.3 triệu token, 50,677 từ riêng biệt, trung bình **15.89 từ/lượt nói**
  (§IV-E). Căn chỉnh ngữ âm (phonetic alignment) bằng MFA được phát hành dưới
  dạng TextGrid (§IV-F).
- **Cấp phép (✔, Table II):** mọi podcast đều là CC hoặc Public Domain nên bản
  thân *audio* có thể phân phối lại được — **CC-BY 90.86%** (5,458 podcast /
  242,699 lượt nói), CC-BY-SA 5.59%, Public Domain 2.88%, Không rõ (Unknown)
  0.67% (40 podcast bị mất ảnh chụp màn hình giấy phép sau khi nguồn gốc bị gỡ
  xuống). Thực hành: lưu **ảnh chụp màn hình trang giấy phép** ngay tại thời
  điểm thu thập để làm bằng chứng xuất xứ (provenance).
- **Pipeline truy hồi/phân đoạn (§III, Fig. 1):** nguồn → chuyển sang PCM
  16 kHz/16-bit/mono (Librosa) → phân tách người nói (diarize) + ASR (Azure
  Video Indexer 61.0%, Whisper-large 13.3%, Whisper-large-v2 21.1%; 4.64% đầu
  tiên làm thủ công) → cắt thành **các lượt nói (speaking turns) dài
  2.75–11 giây** (lượt dài được phân đoạn lại theo căn chỉnh từ tại các khoảng
  lặng ≥0.3 giây; lượt <5 từ bị loại bỏ) → **bộ phát hiện nhạc nền (music
  detector)** (loại nếu >50% là nhạc) → **WADA-SNR** (loại nếu SNR <15 dB) →
  bộ lọc đơn-người-nói bằng **pyannote.audio** → bộ dự đoán giới tính LSTM (để
  cân bằng giới tính) → **xếp hạng truy hồi cảm xúc (emotion-retrieval
  ranking) trên 48+ tiêu chí** từ nhiều mô hình SER/sentiment (để lấy mẫu quá
  mức (over-sample) nội dung mang cảm xúc, thuộc lớp thiểu số) → nghe lại lần
  cuối bởi người đã qua đào tạo → đánh giá cảm quan (perceptual evaluation).
  Hiệu ứng ròng của bước truy hồi: chỉ còn **28% neutral** (so với tỷ lệ
  neutral cao hơn nhiều của hội thoại không được nhắm mục tiêu).
- **Giao thức chú thích (§III-D, §IV):** nhãn chính (primary) = chọn **một**
  trong 8 phạm trù (giận dữ, buồn bã, vui vẻ, ngạc nhiên, sợ hãi, ghê tởm,
  khinh miệt, trung tính) + ô văn bản tự do "Other"; nhãn phụ (secondary) =
  chọn nhiều trong số 16 cảm xúc; **valence/arousal/dominance trên thang
  Likert SAM 1–7**, giá trị đồng thuận (consensus) của attribute = trung bình
  qua các rater; đồng thuận nhãn chính theo **luật đa số tương đối (plurality
  rule)** (có hẳn một lớp "không đồng thuận" tường minh). Việc crowdsourcing
  đã bị **từ bỏ giữa chừng dự án** (do bot, nộp bài ngẫu nhiên) để chuyển sang
  **14–20 sinh viên UT-Dallas đã qua sàng lọc** làm worker, có phản hồi xếp
  hạng tương đối hàng tuần và bắt buộc đào tạo lại có mục tiêu (targeted
  re-training) trên đúng attribute mà họ yếu nhất; 430 worker crowd kém +
  44,968 lượt chú thích đã bị loại bỏ và chú thích lại. Cuối cùng, các worker
  sinh viên đóng góp **65.82%** tổng số lượt chú thích.
- **Độ đồng thuận (✔, Table III):** κ của nhãn chính **0.411** (toàn bộ - All);
  α của valence 0.508 / arousal 0.441 / dominance 0.386 (toàn bộ). Test3 (cân
  bằng, được chọn lọc cẩn thận) đạt cao nhất (primary 0.510, arousal 0.610);
  **Test2 thấp nhất** (primary 0.294, valence 0.228) vì tập này nặng về
  neutral và neutral vốn mơ hồ về bản chất.
- **Các partition (✔, §V-A, Table IV/VI):** **độc lập theo người nói
  (speaker-independent)** — Train (2,220 người nói / 169,190 lượt) / Dev (704
  người nói / 34,399) / **Test1** (465 người nói / 46,294; cùng phân bố lớp
  với toàn bộ corpus) / **Test2** (112 người nói / 14,822; thu thập **không**
  qua bước emotion-retrieval → ~45.8% neutral; một **cơ chế kiểm soát thiên
  lệch lựa chọn (selection-bias control)** có chủ đích) / **Test3** (428
  người nói / **3,200 lượt, cân bằng 400×8 lớp**; nhãn/bản chuyển văn/
  speaker-id đều **bị giữ kín (withheld)** — một bài kiểm tra mù (blind
  challenge) phục vụ qua leaderboard, dùng cho Odyssey-2024 & Interspeech-2025).
  Lưu ý (chú thích Table IV, §V): **các tập test chia sẻ người nói với nhau**
  (một số người nói xuất hiện ở cả Test1 lẫn Test2); chỉ có ranh giới
  train/dev-vs-test là tách biệt hoàn toàn, và ngay cả ở đó các lượt nói
  "người nói không rõ" trong Train vẫn có thể rò rỉ.
- **Baseline (✔, §VI, Table VII):** các mô hình SSL sẵn có **WavLM /
  Wav2vec2.0 / HuBERT (24 lớp, 310M), đã fine-tune**. Categorical = **focal
  loss** + head FC 2 lớp trên 8 lớp. Attribute = **theo giai đoạn (staged)**:
  đầu tiên thích nghi SSL bằng **CCC loss** trên V/A/D đồng thời, sau đó
  joint-train cùng head categorical focal, rồi mới tới **head regression đơn
  nhiệm cho từng attribute trên bộ mã hóa đóng băng**. 20 epoch, LR 1e-5,
  batch 32, Adam. Kết quả — **WavLM thắng ở mọi nơi**:
  - Categorical **F1-macro / F1-micro**: Test1 0.297/0.394, Test2 0.206/0.280,
    Test3 0.356/0.373.
  - Attribute **CCC** (V/A/D): **Test1 0.722 / 0.724 / 0.645**; Test2 0.549 /
    0.547 / 0.467; Test3 0.632 / 0.632 / 0.479.
  - Báo cáo mức tăng tương đối ~8% so với baseline v1.12 nhờ tập huấn luyện
    lớn hơn/sạch hơn. Khoảng cách macro-so-với-micro lớn trên Test1 chính là
    chẩn đoán của bài báo về **mất cân bằng lớp nghiêm trọng**.

### Các phần trực tiếp hữu ích cho ViEmoSpeech (gắn nhãn theo Decision ID)

1. **Phân tách giữa phần chỉ-đặc-trưng và phần audio-có-thể-phát-hành trong
   gói phát hành** — **V-H**. MSP phát hành audio + nhãn categorical theo
   từng lượt + V/A/D + nhãn phụ + speaker-id + bản chuyển văn của con người +
   TextGrid MFA, *vì giấy phép của họ cho phép phân phối lại audio*.
   ViEmoSpeech không thể phát hành audio, nhưng MSP là tiền lệ cho **mọi thứ
   còn lại trong gói**: nhãn theo từng lượt, mốc thời gian (timestamp),
   speaker-id, và (quan trọng nhất) kỷ luật **lưu bằng chứng giấy phép bằng
   ảnh chụp màn hình**.
2. **Thiết kế ba tập test, đặc biệt là Test2 và Test3** — **V-G** (và
   **V-E**). Test1 = in-distribution; **Test2 = một lát cắt được lấy mẫu
   *không* qua bước truy hồi dựa trên mô hình, với mục đích rõ ràng là đo
   thiên lệch lựa chọn (selection bias)**; Test3 = **cân bằng lớp**, **giữ
   kín nhãn**, dạng blind challenge. Một mẫu thiết kế eval sẵn có cho kiểu
   speaker-disjoint + lát cắt kiểm soát (control-slice).
3. **Công thức CCC theo giai đoạn + các con số CCC/F1 cụ thể của WavLM** —
   **V-G**, **V-B**. CCC-rồi-joint, sau đó head regression riêng từng
   attribute trên bộ mã hóa đóng băng; WavLM > Wav2vec2 > HuBERT; CCC trên
   Test1: V 0.722 / A 0.724 / D 0.645 và **F1-macro categorical chỉ ~0.30**
   trên bài toán 8 lớp tự nhiên (naturalistic).
4. **Giao thức chú thích từ chối crowdsourcing** — **V-E**. Bài kiểm tra
   sàng lọc → annotator nội bộ được đào tạo → phản hồi xếp hạng tương đối
   hàng tuần → bắt buộc đào tạo lại khắc phục (remedial re-training) theo
   từng attribute → loại bỏ và chú thích lại các rater kém; thang Likert SAM
   1–7 cho V/A/D với đồng thuận-trung bình; luật đa số tương đối + lớp
   "không đồng thuận" tường minh cho categorical.
5. **Emotion-retrieval để xây dựng một corpus *đậm đặc* cảm xúc** — **V-H**,
   **V-E**. Xếp hạng đa mô hình trên 48+ tiêu chí kéo tỷ lệ neutral xuống còn
   28%; và chính *thiên lệch* mà việc này gây ra sau đó được *đo lường* bằng
   Test2.

### Cách mỗi phần giúp ViEmoSpeech thành công

- **V-H — gói phát hành & bằng chứng xuất xứ (provenance).** Áp dụng gói của
  MSP *trừ audio*: theo từng lượt {emotion, V/A, distress, tone, phương ngữ
  (dialect), speaker-id, ts bắt đầu/kết thúc} + (tùy chọn) TextGrid
  phone/âm tiết đã forced-align, CC-BY. Sao chép quy tắc **chụp ảnh màn hình
  giấy phép ngay khi thu thập** cho các nguồn YouTube của chúng ta vào tài
  liệu capability của extraction-pipeline — MSP đã mất thông tin giấy phép
  của 40 podcast chính vì không làm điều này, một lỗi rẻ tiền cần ngăn chặn
  trước. Định vị ViEmoSpeech trong bảng so sánh corpus kiểu Table-I giống
  cách MSP làm (kích thước / số người nói / khả năng truy cập / loại / ngôn
  ngữ) để tuyên bố "corpus tiếng Việt CC-BY đa lớp + có thanh điệu đầu tiên"
  được đọc trực tiếp cạnh MSP, THAI-SER, DUSHA, BIIC.
- **V-G — eval & baseline.** (a) Xây dựng một **lát cắt kiểm soát kiểu
  Test2**: một tập held-out được lấy mẫu *không* qua gợi ý (suggestion) từ
  LLM-teacher (ADR-003), để có thể đo trực tiếp xem gợi ý của teacher có làm
  thiên lệch phân bố nhãn hay không — MSP chứng minh đây là một tài sản
  phương pháp luận hạng nhất, không phải chi phí phụ. (b) Báo cáo head V/A
  của chúng ta bằng **CCC** và trích dẫn CCC của WavLM trên Test1 (V 0.722 /
  A 0.724) làm điểm neo so sánh liên-corpus — nhưng chỉ như một *ngưỡng trần
  dưới điều kiện fine-tune*, xem rủi ro bên dưới. (c) Dùng **F1-macro ≈
  0.30** trên dữ liệu tự nhiên của MSP làm mức sàn thực tế cho head 7 lớp
  của chúng ta và đặt nó trong bảng baseline *cạnh* con số VNEMOS 0.87 bị rò
  rỉ (leaky) của vn-10 — hai con số đặt cạnh nhau làm rõ lý do vì sao
  F1-macro speaker-disjoint mới là metric trung thực.
- **V-B — backbone.** So sánh trực tiếp, sạch sẽ của MSP cho thấy **WavLM ≥
  Wav2vec2 ≥ HuBERT** cho cả SER categorical lẫn attribute trên dữ liệu tự
  nhiên; điều này ủng hộ trực tiếp việc chọn WavLM làm nhánh backbone audio
  mặc định trong sweep V-B, với head CCC-theo-giai-đoạn làm công thức cho
  attribute.
- **V-E — giao thức chú thích.** Việc gán nhãn con người một-lượt
  (single-pass) hiện tại của chúng ta (κ 0.675 = độ đồng thuận *giữa các
  teacher*, theo commit gần đây) thấp hơn chế độ ≥5-rater của MSP. Nhập vào
  **vòng lặp khắc phục (remedial loop)** của MSP (điểm yếu theo từng
  dimension → đào tạo lại có mục tiêu) và **công cụ SAM 1–7** của họ làm
  tham chiếu thiết kế, nhưng xem khoảng lệch về thang đo bên dưới. Áp dụng
  **lớp "không đồng thuận" + luật đa số tương đối** để các lượt categorical
  mơ hồ được đánh dấu tường minh, thay vì bị ép ngầm (phù hợp với quy tắc
  ambiguous→drop của ADR-002).

### Lăng kính tính hợp lệ khi chuyển giao (chế độ ViEmoSpeech)

- **Những gì chuyển giao sạch sẽ:** giao thức chú thích (quản lý rater, đào
  tạo khắc phục, lớp không đồng thuận), triết lý partition (speaker-disjoint
  + lát cắt kiểm soát thiên lệch + lát cắt mù giữ kín), công thức attribute
  CCC-theo-giai-đoạn, bằng chứng ủng hộ backbone-WavLM-trước-tiên, hình dạng
  gói phát hành, và kỷ luật bằng chứng xuất xứ giấy phép. Không cái nào
  trong số này phụ thuộc vào việc audio là tiếng Anh hay có nguồn gốc từ
  podcast.
- **Những gì KHÔNG chuyển giao:** (1) **Phát hành audio** — toàn bộ lý do
  tồn tại (raison-d'être) của MSP (audio CC có thể phân phối lại) chính xác
  là điều ViEmoSpeech không được phép làm về mặt pháp lý với media phim
  truyền hình; bản phát hành của chúng ta chỉ-đặc-trưng, nên nửa *audio*
  trong gói của MSP là bất khả thi. (2) **Pipeline làm sạch của MSP giả định
  podcast tương đối sạch sẵn**: MSP *lọc bỏ* nhạc nền (loại nếu >50% là
  nhạc) và loại SNR <15 dB — họ không bao giờ *tách* nhạc nền khỏi giọng
  nói. Phim truyền hình Việt Nam có nhạc nền liên tục, đó chính xác là lý do
  pipeline của chúng ta chạy **Demucs source-separation** *trước*
  VAD/turn-split. Lựa chọn "loại bỏ, không tách" của MSP sẽ vứt bỏ phần lớn
  chất liệu của chúng ta; chuỗi Demucs-rồi-giữ-lại của chúng ta là một sự
  phân kỳ (divergence) có chủ đích, mang tính load-bearing — và nó làm thay
  đổi domain âm học mà backbone V-B nhìn thấy (giọng đã tách ≠ audio podcast
  gốc của MSP), nên các con số CCC của họ **không** phải mục tiêu so sánh
  ngang hàng (like-for-like).
- **Quy ước về thang đo:** MSP dùng **SAM 1–7** cho V/A/D; spec của
  ViEmoSpeech dùng **Russell 1–5**. So sánh CCC liên-corpus đòi hỏi phải
  rescale/chuẩn hóa (normalisation) tường minh, và CCC nhạy với thang đo
  theo cách mà Pearson thì không — cần quyết định điều này ở V-E/V-G trước
  khi trích dẫn CCC của MSP làm thước đo (bar) của chúng ta.
- **Đạo đức/tính xác thực (authenticity):** §I của MSP *từ chối một cách
  tường minh* cảm xúc diễn xuất từ phim truyền hình, gọi đó là "sự phóng đại
  ra bên ngoài (exaggerated externalizations)… thiếu tính xác thực… có vấn
  đề đạo đức và bản quyền" — tức là họ nêu đích danh loại nguồn dữ liệu của
  chúng ta như một điểm yếu. Đây là một trích dẫn mà method paper của
  ViEmoSpeech phải trả lời trực diện: chúng ta không tuyên bố tính xác thực
  lâm sàng/tự nhiên; distress là một **proxy từ kịch diễn xuất (acted-drama
  proxy)** (khung V-F), và phép đo tone×emotion (V-D) là một tuyên bố về
  *kênh ngữ âm* không đòi hỏi cảm xúc phải là tự phát. Hãy biến lời phê bình
  đó thành việc xác định phạm vi (scope-setting), chứ không phải một cuộc
  phản biện mà chúng ta không thể thắng.

### Hạn chế & câu hỏi mở đối với ViEmoSpeech

- **Mâu thuẫn với pipeline của chúng ta (V-H / extraction-pipeline).** MSP
  **loại bỏ** audio nhiễu/nhiều nhạc nền (SNR <15 dB, >50% nhạc) thay vì
  khôi phục nó; ViEmoSpeech **khôi phục** nó bằng Demucs. Nếu chúng ta giữ
  lại các clip mà MSP sẽ loại bỏ, nhãn của chúng ta nằm trên một nền âm học
  nhiễu hơn so với MSP — vì vậy khi trích dẫn CCC của MSP, chúng ta phải
  thêm một lưu ý "domain sau tách nguồn (post-separation)", và nên báo cáo
  phân bố SNR của các clip *được giữ lại* để định lượng mức độ chúng ta vận
  hành xa khỏi chế độ sạch của MSP đến đâu.
- **Mâu thuẫn với vn-10 (V-G).** Các con số VNEMOS của vn-10 (UA 0.87 / F1
  0.87) là 5-fold CV bị rò rỉ speaker trên 250 clip; **F1-macro ≈ 0.30**
  speaker-disjoint, tự nhiên, 8 lớp của MSP mới là phép kiểm tra thực tế.
  Cả hai không thể cùng là "thước đo" — bảng baseline của chúng ta phải thể
  hiện chúng lần lượt như một ngưỡng trần bị thổi phồng và một mức sàn tự
  nhiên trung thực, nếu không reviewer sẽ chọn con số nào có lợi cho họ.
- **Khoảng cách so với chế độ nhãn của chúng ta (V-E).** MSP = **≥5 người
  chấm/lượt nói**, κ 0.411 trên bài toán 8 lớp tự nhiên, khó. ViEmoSpeech
  hiện đang **một-lượt (single-pass)** với *gợi ý* từ LLM, và κ 0.675 trong
  repo là **giữa teacher với teacher**, mà — theo đúng bất biến (invariant)
  về honest-weak-supervision của chính chúng ta — *không phải* là accuracy
  hay độ đồng thuận với human-gold. Câu hỏi mở: chúng ta có nên chạy một
  lượt ≥3-người-chấm trên ít nhất lát cắt gold toàn bộ series (ADR-002) để
  có một κ có thể bảo vệ được, đặt cạnh 0.411 của MSP? Phim diễn xuất *lẽ ra*
  nên có độ đồng thuận cao hơn giọng nói tự phát của MSP — một lợi thế đáng
  đo lường, không nên chỉ giả định.
- **Câu hỏi mở về thang đo attribute (V-E/V-G).** Russell 1–5 so với SAM 1–7
  của MSP: cần chọn một cách chuẩn hóa và một metric (CCC hay Pearson) trước
  khi đưa ra bất kỳ tuyên bố V/A liên-corpus nào; lưu ý vn-06/Shen đã lập
  luận dùng Pearson cho các biểu đồ probing của chúng ta, nên cuối cùng có
  thể chúng ta sẽ báo cáo CCC để so sánh được với MSP *và* Pearson cho probe
  kênh thanh điệu — nêu rõ cả hai.
- **Baseline đóng băng so với fine-tuned (V-B/V-G).** Các con số CCC của MSP
  đến từ SSL 310M đã **fine-tune**; nếu nhánh V-B của chúng ta đóng băng
  WavLM rồi probe, khoảng cách CCC là điều dự kiến trước và không được đọc
  như một thất bại của mô hình — cần khớp đúng giao thức (fine-tuned) trước
  khi coi 0.72 là mục tiêu.
- **Điểm tinh tế về chồng lấn người nói giữa các tập test (V-G).** *Các tập
  test của MSP chồng lấn lẫn nhau* về người nói; bất biến nghiêm ngặt hơn
  của chúng ta (gold speakers ∩ weak pool = ∅, holdout toàn bộ series) thực
  chất sạch hơn MSP ở điểm này — đáng nêu ra như một điểm mà giao thức của
  ViEmoSpeech *vượt qua* corpus chuẩn mực của lĩnh vực, chứ không chỉ đơn
  thuần đi theo nó.
