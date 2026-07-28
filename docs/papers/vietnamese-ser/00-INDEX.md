# Vietnamese SER + tonal prior-art — paper stream index

Hai lớp tài liệu cho nhánh Vietnamese SER của ViEmoSpeech:

## Scoping nội bộ (không PDF, sweep 2026-07-02)

Ba vòng rà `research-paper` + tổng hợp GO/NO-GO — dùng để quyết hướng, không phải
deep-read từng bài:
- [00 GO/NO-GO summary](00-GO-NO-GO-SUMMARY.md)
- [01 VN-SER corpora & benchmarks](01-vn-ser-corpora-benchmarks.md)
- [02 tonal-language SER prior art](02-tonal-language-ser-prior-art.md)
- [03 VN text/ASR building blocks](03-vn-text-asr-building-blocks.md)
- [04 pioneer corpus design](04-pioneer-corpus-design.md)
- [05 scale plan](05-scale-plan.md)

## Bài báo deep-read (PDF + phân tích toàn văn, 2026-07-10)

Tải + đọc sâu toàn văn PDF trong task `docs/tasks/paper-deep-analysis.md`; mỗi bài có
mục `## Deep research — full-PDF read (2026-07-10)` (chấm theo profile ViEmoSpeech +
register V-A…V-H) và bản dịch tiếng Việt `NN-slug.vi.md`.

| # | Paper | Venue/Year | Vai trò với ViEmoSpeech | PDF |
|---|---|---|---|---|
| 06 | Shen — Encoding of Lexical Tone in SSL | NAACL 2024 | Tiền đề phonation-heavy (V-B/V-D); premise là *suy luận*, chưa ai đo trực tiếp | [md](06-shen-lexical-tone-ssl.md) · [pdf](pdfs/06-shen-lexical-tone-ssl.pdf) |
| 07 | CASE/FAS — When Tone and Words Disagree | arXiv 2026 | Đối thủ kiến trúc gần nhất; "tone"=paralinguistic → novelty còn nguyên | [md](07-case-tone-words-disagree.md) · [pdf](pdfs/07-case-tone-words-disagree.pdf) |
| 08 | Human-Guided LLM Reasoning VN SER | arXiv 2026 | VN SER mới nhất; κ0.857 (3 lớp)/86.6% leaky; nêu tone-confound không giải | [md](08-human-guided-reasoning-vnser.md) · [pdf](pdfs/08-human-guided-reasoning-vnser.pdf) |
| 09 | PhoWhisper+PhoBERT (VNU) — **đã rút** | arXiv 2024 (withdrawn) | Không phải SER; rule-fusion tiền lệ, không có số baseline | [md](09-phowhisper-phobert-fusion.md) · [pdf](pdfs/09-phowhisper-phobert-fusion.pdf) |
| 10 | VN Depression Dynamic-CBAM (VNEMOS) | arXiv 2024 | Baseline audio-only VN (UA0.87 leaky, không speaker-disjoint); anti-pattern distress-proxy | [md](10-vn-depression-dynamic-cbam.md) · [pdf](pdfs/10-vn-depression-dynamic-cbam.pdf) |
| 11 | THAI-SER corpus | arXiv 2025 | Tiền lệ corpus ngôn ngữ thanh điệu (CC-BY-SA); crowd-QC + Krippendorff α | [md](11-thai-ser-corpus.md) · [pdf](pdfs/11-thai-ser-corpus.pdf) |
| 12 | Emotionally Incongruent Speech (SLM eval) | arXiv 2025 | Contrastive "semantics dominate" (model-bias); target/proxy + Cramér's V | [md](12-emotionally-incongruent-slm.md) · [pdf](pdfs/12-emotionally-incongruent-slm.pdf) |
| 13 | Chang — Mandarin tone×emotion acoustics | PLOS ONE 2023 | Tiền đề thực nghiệm: F0 mean/range tone-dependent, amp/dur không (V-D/V-B) | [md](13-chang-mandarin-tone-emotion.md) · [pdf](pdfs/13-chang-mandarin-tone-emotion.pdf) |

Bốn bài paywalled giữ abstract-only (không vượt paywall): Xiao & Liu (SAGE), Cantonese
JSLHR 2025, Hsu & Wu (IEEE TAFFC 2023), Awatef et al. (Springer AoT 2025) — xem
[02](02-tonal-language-ser-prior-art.md) / [`bimodal-ser/00-INDEX.md`](../bimodal-ser/00-INDEX.md).
