# 013 — Bimodal tone×emotion: tầng method của paper

- **Status:** **draft — chỉ đặt vấn đề, CHƯA có thiết kế được duyệt.** Không viết code
  trước khi §"Cần owner quyết" được chốt.
- **Created:** 2026-09-03 · **Owner:** user / Claude
- **Depends on:** [004](../004-vnser-training/README.md) (baseline speech-only — bậc
  thang để so delta) · [011](../011-online-multi-annotator/README.md) (κ; không có κ
  thì mọi delta ở đây không báo cáo được theo I6) · P3 của
  [roadmap](../../../tasks/viemospeech-scale-roadmap.md) (đủ gold utt)
- **Vị trí:** P4.3 trong roadmap. Đây là **đóng góp thật của method paper**; corpus là
  đóng góp còn lại.

## Vì sao change này tồn tại — động cơ nằm trong số đo, không phải trong ý tưởng

| Số đo | Nguồn |
|---|---|
| CCC **valence 0.071** ở LOSO (arousal 0.114) | [`training-baseline.md`](../../capabilities/training-baseline.md), run 2026-09-02 |
| emotion macro-F1 LOSO **0.258** | cùng nguồn |

Valence gần sàn ở eval trung thực trong khi arousal khá hơn hẳn — đúng dạng "audio một
mình đọc được **mức kích động**, không đọc được **cực tính**". Đó là chỗ nhánh text/tone
phải gánh. Đây là lý do có thật, đo được, chứ không phải "thêm modal cho sang".

## Tiền đề ngữ âm học (đã đọc toàn văn, không phải phỏng đoán)

- **[vn-06](../../../papers/vietnamese-ser/06-shen-lexical-tone-ssl.vi.md)** (Shen, NAACL
  2024): thanh điệu tiếng Việt **thiên về phonation/voice-quality**, không thiên về
  F0-contour như Quan Thoại; SSL frozen giải mã thanh điệu Việt **khó hơn**; **không có
  transfer** Quan Thoại→Việt. ⇒ Tiền đề chịu lực: thanh điệu Việt dùng **chính kênh** mà
  cảm xúc cũng dùng.
- **[vn-13](../../../papers/vietnamese-ser/13-chang-mandarin-tone-emotion.vi.md)** (Chang,
  PLOS ONE 2023): cạnh tranh **bất đối xứng** — cảm xúc ảnh hưởng nhận diện thanh điệu
  **nhiều hơn** chiều ngược lại; giận tăng F0/biên độ, buồn kéo dài thời lượng. ⇒ Hiện
  tượng có thật, đã bình duyệt, nhưng **trên tiếng Quan Thoại** — bản tiếng Việt là thứ
  corpus của ta biến thành đo được.
- **[vn-07](../../../papers/vietnamese-ser/07-case-tone-words-disagree.vi.md)** (CASE/FAS,
  arXiv 2601.04564): **đối thủ kiến trúc gần nhất** — query-based attention tách luồng
  acoustic/semantic, 59.38% trên CASE. ⚠️ "tone" của họ là **tone-of-voice
  paralinguistic**, KHÔNG phải **thanh điệu từ vựng**. Bắt buộc trích dẫn **và** phân
  biệt rõ trong related work; đồng thời là mẫu fusion tham khảo.

**Khoảng trống ta chiếm:** chưa ai mô hình hoá tương tác thanh-điệu-từ-vựng × cảm xúc
trên một ngôn ngữ có thanh điệu **với nhãn syllable-tone đi kèm**. Corpus ViEmoSpeech
được thiết kế để có đúng thứ đó.

## Phạm vi

**Trong:** tầng model đọc **cả** tín hiệu âm học và thanh điệu/text, đo delta so với
baseline speech-only 0.258 trên **cùng** eval LOSO cross-series.

**Ngoài:** thu thêm media (P2), gán thêm nhãn (P3), đổi giao thức κ (011). Change này
**không** được đổi định nghĩa eval — so delta trên cùng thước đo hoặc không so.

## Cần owner quyết — 4 câu, chưa câu nào có đáp án trong repo

Đây là chỗ **ambiguity escalates up**. Tôi không tự chọn.

### Q1. Nguồn thanh điệu lúc inference là gì?

| Phương án | Được | Mất |
|---|---|---|
| **A. Từ text** (ASR → âm tiết → dấu thanh) | dùng được PhoWhisper sẵn có | ASR **sai thanh điệu đúng ở đoạn cảm xúc mạnh** — đã quan sát ở pilot (`vn-tv-ser-pilot.md` M3: "mày→máy/mây, tao→tháo" khi quát). Nhiễu **tương quan với nhãn** ⇒ nguy hiểm |
| **B. Dự đoán thanh điệu từ audio** (head phụ) | không phụ thuộc ASR | cần nhãn thanh điệu per-syllable để train head đó |
| **C. Chỉ dùng lúc train** (auxiliary task, inference speech-only) | tránh hẳn lỗi ASR lúc test | delta có thể nhỏ hơn |

Quan sát pilot ở M3 khiến A trở nên **rủi ro có hệ thống**, không phải nhiễu ngẫu nhiên —
và trớ trêu, chính nó cũng là bằng chứng sớm cho giả thuyết tone×emotion.

### Q2. Nhãn thanh điệu ở đâu ra?

Intent gọi ViEmoSpeech là corpus **syllable-tone-annotated**, nhưng `state.db` hiện
**không có** trường nhãn thanh điệu nào — chỉ có `dialect` (metadata, không phải target).
Suy từ chính tả tiếng Việt (dấu) là tự động được, nhưng **chỉ đúng khi text đúng** → vòng
lại Q1. Nếu cần nhãn thanh điệu do người gán thì đó là **một P3 riêng**, phải vào roadmap
trước khi change này chạy được.

### Q3. Kiến trúc fusion nào?

Cross-attention kiểu FAS (vn-07) là mẫu gần nhất, nhưng nó tách acoustic/semantic —
còn ta cần tách **acoustic-cảm-xúc / acoustic-thanh-điệu**, hai thứ **dùng chung một
kênh vật lý** (vn-06). Đây là điểm khác biệt khoa học của paper, và cũng là chỗ dễ tự
lừa mình nhất. Cần chốt trước khi code.

### Q4. Ngưỡng "thành công" là bao nhiêu, chốt trước hay sau?

Change 012 cho thấy vì sao câu này quan trọng: pre-register ngưỡng rồi thì kết quả
Δ +0.024/CI-chứa-0 buộc phải đọc là H0, không lách được. Tầng bimodal cũng cần một
`preregistration.md` tương tự **trước** khi chạy, nếu không delta sẽ được diễn giải
theo hướng có lợi sau khi thấy số.

## Điều kiện tiên quyết (không thoả thì change này chưa chạy được)

- [ ] **κ human–human** (P1) — I6: không có κ thì delta không báo cáo được như accuracy
- [ ] **Series test chốt** (P0) — không thì không có thước đo ổn định để so delta
- [ ] **Đủ gold utt** (P3) — 1.193 clip hiện tại đã cho CI ±0.03 ở baseline; tách thêm
      nhánh model trên cùng cỡ mẫu sẽ không phân giải được gì
- [ ] Trả lời Q1–Q4

## Tham chiếu

- Baseline để so delta: [`training-baseline.md`](../../capabilities/training-baseline.md)
- Bài học về pre-registration: [change 012](../012-label-quality-ablation/preregistration.md)
- Khảo sát bài liên quan: [`docs/tasks/bimodal-ser-papers.md`](../../../tasks/bimodal-ser-papers.md)
