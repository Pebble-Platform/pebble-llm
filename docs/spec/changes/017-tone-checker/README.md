# Change 017 — Công cụ đo thanh điệu từng âm tiết (tone checker)

- **Status:** **công cụ xong, đã kiểm chứng 2026-10-09** (`docs/reports/017/`). Các số đo
  được định nghĩa trước khi chạy. Không có tham số nào được chỉnh theo kết quả (quy tắc
  argmax, không ngưỡng). Lưu ý: spec này **chưa được commit trước khi chạy** như 015 đã làm.
- **Kết quả** (1.394 clip, 20.069 âm tiết):
  - **Tổng:** chính xác **0.956** [0.952, 0.960], so với mức ngẫu nhiên 0.198. Phát hiện
    thanh sai **0.991**, AUC 0.997.
  - **Báo nhầm tăng theo cảm xúc:**
    - neutral **0.023** → anger **0.066**;
    - arousal thấp **0.025** → arousal cao **0.060**.

    CI của neutral và anger không chồng nhau.
  - **Nhầm nhiều nhất:** ngang↔huyền↔sắc và huyền→hỏi (huyền và hỏi đều trầm-xuống ở giọng
    Bắc). Âm tiết tắc gần như không nhầm (0.990).
  - **Chưa tách được nguyên nhân** của việc báo nhầm tăng theo cảm xúc. Có hai khả năng:
    (a) giọng cảm xúc làm thanh mơ hồ thật, đúng hiện tượng tone×emotion; hoặc (b)
    `gold_text` sai nhiều hơn ở đoạn kích động, vì nó được gợi ý từ ASR/YouTube, mà pilot M3
    đã thấy ASR sai thanh đúng khi quát. 31% số cờ dồn vào các clip có ≥ 3 cờ, phù hợp với
    lỗi text cả cụm. Muốn tách thì cần người soát một mẫu cờ, chia theo arousal (việc kế).
- **Owner:** user / Claude
- **Vì sao có change này:** intent §2.4 (pivot lồng tiếng 2026-10-09) bắt buộc mọi báo cáo
  chất lượng phải có **tỉ lệ sai thanh** của audio sinh ra so với kịch bản. Repo chưa có
  công cụ nào đo được điều đó: `analyze_emotion_features.py` tự ghi *"no syllable-tone
  labels exist yet"*.

## Công cụ phải làm gì

Đầu vào là audio + kịch bản tiếng Việt của câu đó. Với **mỗi âm tiết**, công cụ trả lời:
audio đang thể hiện thanh nào trong các thanh hợp lệ của âm tiết đó, và thanh đó có khớp
kịch bản không. Tỉ lệ sai thanh = số âm tiết không khớp / tổng số âm tiết.

## Vì sao không dùng ASR đọc dấu thanh

- **ASR có mô hình ngôn ngữ.** Nó "sửa" thanh sai thành từ có nghĩa, nên nhìn không ra lỗi.
- **ASR đọc sai thanh đúng ở đoạn cảm xúc mạnh.** Pilot M3 thấy "mày→máy", "tao→tháo" khi
  quát (`docs/tasks/vn-tv-ser-pilot.md`). Thước đo kiểu này sẽ bị chính cảm xúc làm nhiễu,
  mà cảm xúc lại là thứ ta đang điều khiển.

## Cách làm: chấm CTC từng thanh ("tone-GOP")

- **Model:** `nguyenvulebinh/wav2vec2-base-vietnamese-250h` (`Wav2Vec2ForCTC` chuẩn, 16 kHz,
  CC-BY-NC-4.0). Vocab có **đủ 72 nguyên âm mang thanh** (12 nguyên âm × 6 thanh).
  - CTC không có mô hình ngôn ngữ: xác suất từng khung chỉ phụ thuộc audio.
  - Bản large (VLSP2020) bị loại vì phải chạy code tuỳ biến (`model_handling.py`) của repo
    model.
- **Chấm:**
  1. Tính emission của audio **một lần**.
  2. Với âm tiết *i*, viết lại câu với âm tiết *i* mang từng thanh **hợp lệ**, các âm tiết
     khác giữ nguyên. Tính log-likelihood CTC của **cả câu** cho từng biến thể.
  3. Thanh có điểm cao nhất là "thanh audio thể hiện".
  4. `margin` = điểm(thanh trong kịch bản) − điểm cao nhất trong các thanh còn lại.
- **Thanh hợp lệ:**
  - âm tiết tắc (kết thúc p/t/c/ch) chỉ có **sắc / nặng**;
  - các âm tiết khác có đủ 6 thanh.

  Không cho model so với cách viết không tồn tại, vì như vậy phân biệt quá dễ.
- **Vị trí dấu:** mọi biến thể (kể cả thanh của kịch bản) đặt dấu theo **cùng một quy tắc**
  kiểu cũ ("hòa", "thủy"), để không biến thể nào bị phạt vì khác kiểu viết.
- **Loại clip** có chữ số, ký tự ngoài vocab, hoặc âm tiết không có nguyên âm, vì những clip
  này không viết được thành chuỗi CTC tương ứng audio. Số clip bị loại và lý do được ghi
  vào báo cáo.

## Kiểm chứng công cụ trên ViEmoSpeech (giọng thật)

Giọng thật **luôn đọc đúng thanh**, nên "thanh trong kịch bản" chính là đáp án. Mọi số đo
được định nghĩa **trước khi chạy**:

| Số đo | Định nghĩa | Dùng để |
|---|---|---|
| **Độ chính xác nhận thanh** | P(thanh có điểm cao nhất = thanh kịch bản), tính trên âm tiết | Tỉ lệ báo nhầm = 1 − độ chính xác: mức **nền nhiễu** của công cụ |
| **Tỉ lệ phát hiện lỗi** | Giả lập kịch bản ghi sai: với mỗi âm tiết và mỗi thanh sai *t'*, công cụ có gắn cờ không (thanh có điểm cao nhất ≠ *t'*). Điều này tương đương với audio đọc sai thanh so với kịch bản | Độ nhạy |
| **AUC** | Tách (âm tiết, thanh đúng) khỏi (âm tiết, thanh sai) bằng `margin`, không cần ngưỡng | So sánh không phụ thuộc ngưỡng |
| Theo nhóm | Theo thanh (ma trận nhầm 6×6), âm tiết tắc/không tắc, **theo cảm xúc (7 lớp)**, **theo arousal**, theo series | **Cảm xúc có làm công cụ báo nhầm nhiều hơn không** |
| Mức ngẫu nhiên | Trung bình 1/số thanh hợp lệ | Mốc so sánh |
| Khoảng tin cậy | Bootstrap theo clip, 1000 lần, 95% | |

**Cách dùng kết quả cho TTS sau này:** tỉ lệ sai thanh của giọng sinh ra phải được **so với
tỉ lệ báo nhầm trên giọng thật cùng cảm xúc**, không đọc như con số tuyệt đối. Ngưỡng chấp
nhận cho TTS thuộc D8 (`docs/intent/constraints.md` §4.2), chốt trước khi chấm TTS.

## Giới hạn đã biết

- **`gold_text` chưa được soát** (xem `docs/papers/vietnamese-emotional-tts.md` §3). Lỗi
  text sẽ hiện ra thành "báo nhầm", nên tỉ lệ báo nhầm đo được là **cận trên**. Danh sách
  âm tiết bị gắn cờ được ghi ra `data/` để người soát; mẫu soát này thuộc việc khác.
- Model ASR được train trên giọng đọc/YouTube **trung tính**, nên giọng cảm xúc nằm ngoài
  phân phối. Đây chính là thứ phép kiểm chứng đo.
- Quy tắc đặt dấu kiểu cũ có thể lệch với kiểu viết model đã học ("hoà" vs "hòa"). Mọi
  biến thể cùng lệch như nhau, nên ảnh hưởng nhỏ nhưng không bằng 0.
- 99% clip là phương ngữ Bắc. Kết quả không suy ra cho giọng Nam/Trung, vốn có hệ thanh
  khác.

## File

| File | Việc |
|---|---|
| `scripts/vietnamese-ser/tone_check.py` | Thư viện chấm thanh + CLI `validate` (chạy trên ViEmoSpeech → báo cáo) |
| `tests/test_tone_check.py` | Test cho phần chính tả: tách thanh, đặt dấu, âm tiết tắc, chuẩn hoá |
| `data/vietnamese-ser/features/017/syllables.csv` | Điểm từng âm tiết (có chữ → gitignored, I1) |
| `docs/reports/017/report.md`, `metrics.json` | Chỉ có số tổng hợp, không có text |

## Verification

| Kiểm tra | Cách |
|---|---|
| Phần chính tả đúng | `pytest tests/test_tone_check.py` xanh |
| Code chạy end-to-end | `tone_check.py validate --limit 20 --out <thư mục tạm>` |
| Báo cáo không lộ text | `report.md` / `metrics.json` chỉ có số đếm và tỉ lệ (rà tay + grep) |
