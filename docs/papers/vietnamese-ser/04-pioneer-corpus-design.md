# ViEmoSpeech (tên tạm) — Corpus Design Doc: Vietnamese Bimodal Speech-Emotion Corpus

- **Ngày:** 2026-07-02 · **Trạng thái:** DRAFT để đi thuyết phục đối tác (lâm sàng + đại học) và duyệt nội bộ
- **Căn cứ:** scoping pass 2026-07-02 (`00-GO-NO-GO-SUMMARY.md`, `01`–`03`) + phương pháp luận thesis Pebble (weak-label ở quy mô + gold nhỏ chuẩn + gold-holdout)
- **Một câu:** corpus SER tiếng Việt đầu tiên **nói tự do + đa lớp + có lớp tone-annotation + có distress flag + license rõ (CC-BY)** — được xây bằng đúng recipe weak-supervision đã kiểm chứng của thesis.

---

## 1. Khoảng trống nó lấp (vì sao chưa ai có)

| Corpus hiện có | Giờ | Nội dung | Nhãn | License | Thiếu gì |
|---|---|---|---|---|---|
| ViSEC (ICASSP'24) | 3.18h | YouTube, tự do | 4 cảm xúc | **không ghi** | quá nhỏ, license vô hiệu hóa |
| VLSP 2023/25 SER | 56h | TV/social, tự do | **binary** neu/neg | chưa xác nhận | nhãn quá thô |
| VNEMOS | ~0.5h | acted+natural | 5 cảm xúc | không rõ | không tải được thật |
| arXiv 2604.01711 | ? | ? | angry/calm/panic (κ=.857) | chưa release | chưa tồn tại công khai |
| **ViEmoSpeech (đề xuất)** | 50–100h weak + gold nhỏ | tự do | đa lớp + VA + distress | **CC-BY 4.0 từ ngày 1** | — |

Không corpus nào trên thế giới (mọi ngôn ngữ) có **lớp thanh điệu âm tiết** đi kèm nhãn cảm xúc → ViEmoSpeech sinh ra đã nghiên cứu được câu hỏi tone×emotion (hook: tiếng Việt thanh điệu thiên phonation — Shen, NAACL 2024).

## 2. Label scheme (3 lớp nhãn + 1 lớp tự động)

1. **Cảm xúc categorical (primary):** 6 lớp + neutral — vui / buồn / giận / sợ-lo / ngạc-nhiên / ghê-chán / trung tính. Lý do: đủ mịn hơn ViSEC (4) và VLSP (2), nhưng không tham 27 lớp kiểu ViGoEmotions (κ sẽ sập với audio). Map được sang cả 4-lớp ViSEC (so sánh chéo) lẫn taxonomy Pebble.
2. **Valence–Arousal liên tục (1–5):** cho affect head CCC (đồng bộ với bài Voice / MSP-Podcast style).
3. **Distress flag (nhị phân) — lớp "tiên phong" cho Pebble:** "người nói có đang ở trạng thái đau khổ/khủng hoảng tâm lý rõ rệt không". ⚠ **Phạm vi trung thực:** đây là *distress*, KHÔNG phải thang C-SSRS — audio tự sát thật gần như không thu thập được có đạo đức từ nguồn công khai; recall-floor head sẽ train trên distress proxy và nói rõ điều đó. Nhãn này bắt buộc có **đối tác lâm sàng** viết guideline + adjudicate.
4. **Lớp tone (tự động, 0 chi phí annotator):** thanh điệu từng âm tiết từ chính tả transcript (dấu = thanh) + forced alignment (MFA có model tiếng Việt) → timestamp âm tiết + thanh. Đây là trường độc quyền của corpus.

**Metadata mỗi utterance:** speaker-id (pseudonym), giới tính (nghe/kênh), **phương ngữ Bắc/Trung/Nam** (hệ thanh điệu khác nhau: Bắc 6 thanh, Nam 5 — hỏi/ngã nhập một; stratify theo vùng là thiết kế bắt buộc và là một trục phân tích riêng), nguồn, chất lượng thu.

## 3. Quy mô & cấu trúc 2 tầng (đúng recipe thesis)

| Tầng | Quy mô (target v2 — đề xuất sau pilot, chờ chốt) | Số đo thật từ pilot (ep01) | Nhãn bởi | Vai trò |
|---|---|---|---|---|
| **Weak pool** | **~24h / ~18–19k utterance** (3 bộ ≈ 120 tập) — thay target cũ "50–100h" vốn quy ra **~250–500 tập ≈ 6–13 bộ**, không khả thi cho 1 người (chi tiết phép tính: `05-scale-plan.md` §2–§3) | 1 tập 35.6′ → **11.9′ thoại sạch** (yield 33%), **158 utt**, **54% đơn-người-nói** (lạc quan), κ 2-teacher **0.584** | LLM trên transcript + acoustic teacher (WavLM fine-tuned) — 2 nguồn độc lập, lưu confidence + disagreement | train |
| **Gold set** | 2.000–3.000 utterance (~4–6h) | chọn từ weak pool bằng disagreement sampling (49/158 ca 2 teacher cãi nhau ở pilot) | ≥3 annotator người + clinical adjudication cho distress | **held-out eval** (không bao giờ train) |

Gold chọn bằng **stratified + disagreement sampling** (ưu tiên chỗ 2 teacher cãi nhau — rẻ nhất về thông tin). Speaker của gold **disjoint** hoàn toàn với weak pool → gold-holdout by construction.

## 4. Nguồn thu & vấn đề pháp lý phải quyết trước (OPEN QUESTION #1)

Ứng viên nguồn: podcast tiếng Việt, talkshow/phỏng vấn YouTube, radio confession/tâm sự đêm khuya (mật độ cảm xúc + distress cao), livestream hội thoại. **Nhưng:** thu từ YouTube rồi phát hành lại audio dưới CC-BY là **không tự động hợp lệ** (mình không sở hữu bản quyền âm thanh). ViSEC lách bằng cách không ghi license — chính là cái bẫy ta chê. Ba phương án, phải chọn 1 (hoặc trộn):

| Phương án | Cách làm | Được | Mất |
|---|---|---|---|
| **A. Xin phép kênh** | Email chủ podcast/kênh xin quyền phát hành lại cho nghiên cứu (CC-BY phần corpus) | audio thô sạch pháp lý | chậm, tỉ lệ đồng ý thấp |
| **B. Features + con trỏ** (tiền lệ phổ biến) | Phát hành **embedding/features + transcript + timestamp + link nguồn**, không phát hành audio thô | CC-BY được ngay, tránh copyright audio | người dùng phải tự tải audio; kém tiện |
| **C. Tự thu** | Cộng tác viên kể chuyện/phỏng vấn có consent form | quyền sạch 100%, consent chuẩn IRB | đắt, dễ mất tính tự nhiên |

**Đề xuất:** B làm mặc định (ship được chắc chắn) + A cho một tập con "audio-included" + C cho riêng phần distress (consent là bắt buộc đạo đức ở đây). → cần ý kiến pháp lý/đối tác trước khi thu.

## 5. Annotation protocol

- **Pilot 200 utterance** trước → đo κ, sửa guideline, rồi mới chạy chính.
- ≥3 annotator/utterance; nhãn chính = majority; lưu **phân phối nhãn đầy đủ** (không chỉ argmax — cho soft-label research). Mục tiêu κ: ≥0.6 emotion 7-lớp, ≥0.75 distress (mốc so sánh: 2604.01711 κ=0.857 với 3 lớp; Gaur CSSRS pairwise 0.79).
- **Distress:** annotator thường gán sơ bộ → **bác sĩ/chuyên viên lâm sàng adjudicate** mọi ca positive + 10% negative ngẫu nhiên.
- **Bảo vệ annotator (bắt buộc, hay bị quên):** nội dung distress gây hại tâm lý người nghe — giới hạn giờ/ngày, debrief định kỳ, quyền skip; ghi thành mục trong hồ sơ ethics.
- Guideline song ngữ Việt–Anh (để paper audit được).

## 6. Splits, metrics & giao thức công bố (thương hiệu của ta)

- Split cố định theo **speaker**, stratify phương ngữ; công bố seed + script split.
- Metrics chính thức: macro-F1 + **UAR** (chuẩn SER) cho emotion; CCC cho V/A; **precision @ recall ≥ 0.90** cho distress — benchmark SER đầu tiên có recall-floor như metric chính thức.
- Công bố kèm **giao thức gold-holdout**: mọi mở rộng weak-label sau này phải eval trên gold held-out — luật chơi honest-eval do ta đặt.
- Baseline ship kèm: acoustic-only (WavLM) / text-only (PhoWhisper→PhoBERT) / fusion — chính là 3 arm của method paper.

## 7. License & ethics

- **CC-BY 4.0, tuyên bố trong LICENSE + README từ commit đầu tiên.** (Phương án B ở §4 làm điều này khả thi bất kể copyright audio nguồn.)
- De-identification: bỏ tên riêng/SĐT/địa chỉ trong transcript (NER + regex + duyệt tay tập gold); không thu nội dung có trẻ vị thành niên.
- **IRB/ethics:** cần tổ chức học thuật đứng tên (đối tác đại học — ứng viên tự nhiên: các nhóm đang hoạt động UIT/HUST/VNU; cân nhắc mời nhóm ViSEC làm đồng tác giả thay vì đối thủ).
- Kênh gỡ bỏ (takedown request) công khai trong README.

## 8. Ngân sách & timeline thô (điền số khi có báo giá)

| Hạng mục | Ước lượng (cập nhật từ pilot — phép tính: `05-scale-plan.md` §4–§5) |
|---|---|
| GPU extract pipeline (ffmpeg→Demucs→VAD→PhoWhisper→pyannote) trên Kaggle P100 | ~0.30 GPU-h/tập → 3 bộ/120 tập = **36 GPU-h ≈ 2 tuần** quota (30 GPU-h P100/tuần) |
| Weak-label 2-teacher (Batch API) | 3 bộ ≈ 18k utt × $0.001225 = **~$22** (không còn là biến số lớn) |
| Annotation gold 2–3k × 3 người | [BÁO GIÁ] — biến số lớn nhất |
| Clinical adjudication | theo đối tác |
| Thời gian | Pilot ✓ → GPU extract **~2 tuần** (3 bộ, Kaggle quota) + weak-label vài ngày → gold annotation 2–3 tháng → dataset paper. Tổng còn lại **~3–4 tháng** (extract rút từ ước lượng 1–2 tháng xuống ~2 tuần đo được), khởi động toàn lực **sau khi 2 bài thesis nộp** |

## 9. Rủi ro chính & giảm nhẹ

1. **Bị vượt:** nhóm 2604.01711 release corpus trước → mất "first VN SER corpus", giữ "first tone-layer + first recall-floor benchmark + first bimodal gold-holdout". Giảm nhẹ: chốt design + pilot sớm, cân nhắc liên hệ hợp tác thẳng.
2. **Pháp lý nguồn (§4)** — quyết trước khi thu, không sau.
3. **κ distress thấp** (distress từ audio là khó) → pilot sẽ lộ sớm; fallback: gộp distress vào arousal-negative.
4. **Chi phí annotation vượt** → giảm gold xuống 1.5k, giữ 3 annotator (chất lượng > số lượng — bài học 35.8% nhãn nhiễu).

## 10. Bước tiếp theo (theo thứ tự)

- [ ] Trả lời 2 email đang chờ (ViSEC license, VLSP access) — nếu ViSEC được cấp license, nó thành **seed gold** tiết kiệm hẳn một phần annotation.
- [ ] Chọn phương án pháp lý §4 (cần ý kiến đối tác/pháp lý).
- [ ] Tiếp cận 1 đối tác đại học + 1 đối tác lâm sàng bằng chính doc này.
- [ ] **Pilot kỹ thuật 5–10h** (0 quyết định cần chờ): scrape → PhoWhisper → LLM weak-label → tone alignment → đo disagreement 2 teacher → số liệu khả thi đưa vào phiên bản 2 của doc.
- [ ] Sau pilot: chốt GO/NO-GO toàn lực (điều kiện: 2 bài thesis đã nộp).
