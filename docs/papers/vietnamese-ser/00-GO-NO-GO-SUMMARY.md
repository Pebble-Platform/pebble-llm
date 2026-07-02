# Vietnamese Bimodal SER — Tổng hợp GO/NO-GO (scoping pass 2026-07-02)

> Tổng hợp từ 3 vòng rà song song (agent `research-paper`):
> [`01-vn-ser-corpora-benchmarks.md`](01-vn-ser-corpora-benchmarks.md) ·
> [`02-tonal-language-ser-prior-art.md`](02-tonal-language-ser-prior-art.md) ·
> [`03-vn-text-asr-building-blocks.md`](03-vn-text-asr-building-blocks.md)
> Câu hỏi: có nên làm "bimodal (audio + ASR-transcript) SER tiếng Việt, crisis recall-floor" làm bài 3?

## VERDICT: ⚠ CONDITIONAL GO — niche mở & hook thật, nhưng chân dữ liệu chưa sạch

| Trục | Verdict | Căn cứ |
|---|---|---|
| **Novelty** | ✅ MỞ (nhưng hẹp hơn kỳ vọng & "in the air") | Chưa ai build tone-aware SER cho tiếng Việt hay bất kỳ ngôn ngữ thanh điệu nào; premise ngữ âm (tone × emotion tranh kênh F0) đã vững cho Mandarin (citable, không ai model hoá) |
| **Data (SER corpus)** | ⚠ CHƯA SẠCH | Không corpus nào đồng thời (a) lấy được (b) nói tự do (c) license rõ. ViSEC: mở, tải được, spontaneous — nhưng **không có license field**. VLSP 56h: volume tốt nhưng nhãn chỉ binary, site 503 cả phiên |
| **Pipeline text/ASR** | ✅ SẴN SÀNG | PhoWhisper (BSD-3, WER 4.7–8% clean) · PhoBERT/ViSoBERT/CafeBERT · ViGoEmotions (EACL 2026, 27 nhãn kiểu GoEmotions, 20,664 mẫu) |
| **Crisis head tiếng Việt** | 🔴 KHÔNG CÓ GOLD | Không tồn tại corpus text crisis/mental-health tiếng Việt nào → không có gì để "gold-holdout" — đụng thẳng vào thương hiệu honest-eval của thesis |

## Hook đã được mài sắc hơn nhờ vòng rà

Phát hiện giá trị nhất: **Shen et al. NAACL 2024** (đã có sẵn trong repo — `docs/papers/voice/35-shen-lexical-tone-ssl.md`!) chứng minh thanh điệu tiếng Việt khó decode từ SSL representation hơn Mandarin và **dựa nhiều vào phonation/chất giọng chứ không chỉ đường F0**. Tức là hook không còn là câu chung chung "F0 bận chở nghĩa" mà thành: *tiếng Việt là ngôn ngữ thanh điệu THIÊN VỀ PHONATION — đúng kênh mà cảm xúc cũng dùng — nên xung đột tone×emotion giàu hơn Mandarin, và nhánh text/ngữ nghĩa phải gánh nhiều hơn so với SER phi thanh điệu.* Giả thuyết đo được, chưa ai claim.

## 3 prior work phải cite-and-distinguish (mối đe dọa novelty)

1. **arXiv:2601.04564** "When Tone and Words Disagree" (01/2026) — bimodal audio+text disentangle "tone" — nhưng là tone-of-voice (paralinguistic), KHÔNG phải lexical tone. Phải phân biệt tường minh.
2. **arXiv:2604.01711** (04/2026, VN SER + LLM reasoning) — *nêu tên* tone confound trong motivation mà không giải → chứng minh gap có thật nhưng cũng cho thấy framing đang "in the air" → **yếu tố thời gian: niche này sẽ không mở lâu**.
3. **arXiv:2412.09829** (VNU Hà Nội) — PhoWhisper+PhoBERT fusion rule-based, preprint, corpus 250 clip → baseline trực tiếp để vượt (fusion học được + recall-floor là phần họ không có).

## Việc phải làm TRƯỚC khi quyết (đều rẻ, latency ngoài tầm kiểm soát → khởi động ngay)

- [ ] **Email nhóm ViSEC** (ICASSP 2024) hỏi license — corpus khả dụng nhất hiện tại đang mơ hồ đúng một trường này.
- [ ] **Re-check `vlsp.org.vn`** (503 cả phiên) → điều khoản đăng ký/license corpus SER 56h; hỏi luôn có nhãn nhiều lớp hơn binary không.
- [ ] Watch corpus arXiv 2604.01711 (angry/calm/panic, κ=0.857 — label scheme sát crisis nhất) — chưa release.
- [ ] Quyết scope crisis head: (a) bỏ crisis khỏi bài VN (emotion-only), hay (b) weak-label bằng LLM teacher tiếng Việt và *nói rõ không có gold* — phương án (b) yếu vì mất gold-holdout.

## So với ứng viên bài-3 còn lại (bimodal crisis trên DAIC-WOZ)

| | DAIC-WOZ cascade | VN bimodal SER |
|---|---|---|
| Data | Tồn tại, đang chờ ký EULA | ⚠ conditional (ViSEC license / VLSP access) |
| Gold cho crisis | ✅ PHQ-8 lâm sàng | 🔴 không có |
| Nối thesis | Trực tiếp (tái dùng classifier + protocol) | Phương pháp luận (paired-delta, recall-floor, honest-eval) |
| Khớp sản phẩm | Trung bình | **Cao nhất** (user Việt) |
| Áp lực thời gian | Thấp | **Cao** (framing "in the air", 2604.01711) |

**Khuyến nghị:** chưa commit GPU cho hướng VN. Bắn 2 email/check ở trên ngay (0 chi phí, chờ là chính — đúng bài học DUA), giữ DAIC-WOZ EULA là ưu tiên 🔴 số 1, và quyết bài 3 khi có (a) trả lời license ViSEC/VLSP và (b) kết quả M3 voice.
