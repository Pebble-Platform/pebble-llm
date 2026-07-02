# Kế hoạch bậc thang cho thesis — 3 tầng (từ M8 của bimodal-ser-papers)

- **Slug:** thesis-staged-plan
- **Status:** in-progress
- **Created:** 2026-07-03  ·  **Updated:** 2026-07-03
- **Owner:** Fabio / Claude

## Goal
Thực thi phương án bậc thang đã chọn trong [[bimodal-ser-papers]] (section M8):
**Tầng 1** chốt paper Text (A), **Tầng 2** nâng paper Voice (B) lên nhãn thật khi
EULA về, **Tầng 3** (điều kiện) chương fusion voice+text nhắm gap
"bimodal fusion dưới hard crisis-recall floor" (21/21 bài sweep không có).
"Done" = paper A submit-ready, paper B có số nhãn-thật, quyết định go/no-go tầng 3
có căn cứ số liệu.

## Requirements & Constraints
- **Gold-holdout luôn luôn** (I1); split theo subject (I2); mọi số trace về kernel+log (I5).
- GPU: Kaggle quota ~10h/tuần (đã dùng ~7h tuần trước — kiểm tra lại đầu tuần); ưu tiên việc 0-GPU trước.
- EULA MSP-Podcast + DAIC-WOZ: **đã gửi 2026-07-03 qua giáo sư** — latency 1–4 tuần, ngoài tầm kiểm soát → mọi task phụ thuộc nhãn thật xếp "chờ", không block tầng 1.
- Tham chiếu số/bài: `docs/papers/bimodal-ser/` [NN] + `docs/reports/STATUS-2026-07-02-vi.md`.

---

## TẦNG 1 — Chốt paper Text (0 phụ thuộc, làm ngay, tuần này)

| # | Việc | Chi tiết | Verify | Chi phí |
|---|---|---|---|---|
| T1.1 | **Đo Cohen's κ(LLM, gold) + confusion matrix** trên overlap set | Blocker IEEE #1 (`label-quality.md`: "still owed"). Script local trên 392 gold + nhãn LLM tương ứng; κ weighted (linear/quadratic — chọn quadratic, khớp ordinal QWK) + confusion 4×4. Giải thích "gap 0.28" (0.653 within-dist vs 0.402 gold) | Số κ + bảng confusion nằm trong log/`out/`, điền vào §IV draft, không còn `[TODO κ]` | 0 GPU, ~nửa ngày |
| T1.2 | **Điền bảng baseline vào draft** | Số đã có: RoBERTa 0.346 ±0.026, BiLSTM-MTL 0.378 ±0.014 (log `r2-baseline-*/out/`). Sửa dòng ~324–325 `PAPER-DRAFT-text-ordinal-suicide.md`; cập nhật provenance table "🔄 running" → done | `grep TODO` draft không còn hit baseline; provenance table khớp log | 0 GPU, ~1h |
| T1.3 | **Pilot rationale-groundedness filter** [05] | Trên mẫu ~500 nhãn silver: (a) Gemini re-elicit nhãn + rationale quote-span; (b) LLM-judge chấm groundedness; (c) đo overlap giữa "rationale ungrounded" và tập 16.2% nhãn bị ordinal-CL flag (đóng góp B) — nếu 2 tín hiệu độc lập bắt cùng nhãn xấu → filter mới citable, ghép vào §label-quality như mini-contribution | Report: % ungrounded, overlap với CL flags, ví dụ định tính; quyết định dùng/không dùng làm filter cho B-Arm2 | 0 GPU, chỉ API |
| T1.4 | **B-Arm2: retrain 3-fold trên pool đã clean** (nợ STATUS 3.4) | Drop far-flag / downweight adjacent theo ordinal-CL (+ groundedness filter nếu T1.3 dương); đo Behavior-F1 sau làm sạch vs 0.260 | Kernel + log mới; paired so sánh cùng split/seed | ~3h GPU (vừa quota tuần) |
| T1.5 | **Vá related-work + evaluation-protocol** | Cite [15] (replication — CI/multi-fold precedent) vào §eval; refs 14–17 mở rộng; cite [10] (RDoC/HiTOP) cho ordinal framing — secondary point M6 | Draft build PDF sạch, refs resolve | 0 GPU |

**Exit tầng 1:** draft hết `[TODO]`, κ có số, B-Arm2 chạy xong → paper A submit-ready (chỉ còn authors/affiliation).

---

## TẦNG 2 — Paper Voice trên nhãn thật (critical path đã kích hoạt)

### 2a. Ngay, không cần EULA (tuần này–tuần sau)
| # | Việc | Chi tiết | Verify | Chi phí |
|---|---|---|---|---|
| T2.1 | **Chạy M3 `voice-mtl-heads`** — kernel đã build, chờ push | Push `kaggle/voice/pebble-voice-mtl-heads/` lên Kaggle GPU (10-fold, 2 backbone), pull `out/` | M3 của doc đó: run green, results + artifact bundle về | ~2–3h GPU |
| T2.2 | M4 local sample test + M5 writeup proxy-caveat | Theo đúng exit criteria trong `voice-mtl-heads.md` | Artifact load + predict end-to-end; writeup có caveat proxy | 0 GPU |
| T2.3 | **Theo dõi EULA** (đã gửi 2026-07-03) | Nếu sau **2026-07-17** (2 tuần) chưa hồi âm → nhờ giáo sư follow-up. MSP-Podcast: DTA học thuật (329 nhóm đã có — khả năng cao OK); DAIC-WOZ: USC ICT form | Ghi ngày nhận vào doc này | 0 |

### 2b. Khi MSP-Podcast về (affect + emotion head)
| # | Việc | Chi tiết | Verify | Chi phí |
|---|---|---|---|---|
| T2.4 | **Ingest MSP-Podcast** | `/find-dataset` provenance; vào `data/voice/external/` (gitignored — I4); subject-disjoint theo speaker ID có sẵn của corpus | Provenance doc + speaker-disjoint splits kiểm bằng test | 0 GPU |
| T2.5 | **Swap affect head sang A/V/D thật + recipe staged CCC→joint** [12] | Stage 1: frozen trunk + per-attribute regression (CCC); stage 2: joint với emotion focal head. Báo CCC vs ceiling WavLM fine-tune V≈0.72/A≈0.72/D≈0.65 (Table VII [12]) — ghi rõ ta frozen-probe, họ fine-tune | CCC 3 attribute + std multi-fold; bảng so ceiling có caveat | ~3–4h GPU |
| T2.6 | **Bake-off backbone mở rộng** [08] | Thêm **Whisper-Large-V3 + XEUS** frozen features cạnh WavLM-Large (finding [08]: Whisper 0.366 > WavLM 0.313 trên MSP-Podcast naturalistic — phải kiểm tra lại lựa chọn backbone). Cùng protocol, 3 seed | Bảng per-backbone WA/UA/WF1 + CCC, cùng split; quyết định backbone cuối có số | ~4–6h GPU (tuần riêng) |
| T2.7 | **Anchor emotion head** | vs ABHINAYA WavLM-Large ~34.43 val / 33 test macro-F1 8-class [02] (ballpark, không apples-to-apples); thử **attentive-statistics pooling** vs masked-mean trên trunk [02] | Bảng anchor + ablation pooling | gộp vào T2.5/T2.6 |

### 2c. Khi DAIC về (crisis head)
| # | Việc | Chi tiết | Verify | Chi phí |
|---|---|---|---|---|
| T2.8 | **Crisis head trên nhãn clinical thật** | Threshold trên val cho recall ≥0.90, precision@floor trên test; anchor vs envelope JMIR [10]: sens ~0.86 / AUC ~0.8 (SI-detection đã publish) | precision@floor + so anchor; subject-disjoint | ~2–3h GPU |
| T2.9 | **Viết paper Voice (B)** | Câu chuyện: heterogeneous MTL + recall-floor trên nhãn thật; backbone bake-off; proxy→real như ablation trung thực | Draft đủ section, mọi số cite kernel+log (I5) | 0 GPU |

**Exit tầng 2:** paper B có số nhãn-thật cho cả 3 head + backbone đã chốt lại bằng bake-off.

---

## TẦNG 3 — Fusion voice+text dưới recall floor (ĐIỀU KIỆN)

**Gate mở tầng 3 (cả 3 điều kiện):** (1) tầng 1 xong; (2) T2.5–T2.8 xong; (3) còn ≥3 tuần + quota. Nếu không đủ → tầng 3 thành "Future Work" trong paper B, vẫn cite được gap D6.

| # | Việc | Chi tiết | Verify |
|---|---|---|---|
| T3.1 | **Thiết kế fusion** | Text-dominant primary-auxiliary [13]: NeoBERT/RoBERTa text làm core, voice làm auxiliary inject qua cross-attention. + **per-modality auxiliary heads** (audio-only + text-only logits cạnh fused) chống collapse text-đè-audio [07]. Fusion block: gated cross-attention [06] hoặc bidirectional dual + residual concat [03]; concat làm baseline bắt buộc [08] | Design note trong doc này, chốt trước khi code |
| T3.2 | **Dataset: DAIC** (duy nhất có audio + transcript + nhãn clinical) | Subject-disjoint; cả 2 encoder frozen (I5-friendly, rẻ) | Splits + provenance |
| T3.3 | **Thí nghiệm chính:** precision@recall-floor của bimodal vs voice-only vs text-only | Đây là claim novelty: *fusion dưới hard crisis-recall floor* — chưa có prior art (sweep 21/21) | Bảng 3 cột cùng floor 0.90, multi-fold + std |
| T3.4 | **Stress-test modality dropout** [21] | Case safety-critical "giọng bình thản + text tự sát" (non-complementary): drop từng modality lúc eval, đo degrade | Bảng dropout; fusion không được tệ hơn text-only khi mất audio |
| T3.5 | **Quyết định output** | Chương thesis vs bài IEEE thứ 3 — quyết sau khi có số T3.3 | Ghi Decision Log |

---

## Timeline dự kiến (điều chỉnh theo EULA)

- **Tuần 03–09/07:** T1.1, T1.2, T1.3, T1.5 (0 GPU) + T2.1 push kernel (2–3h GPU). Nếu quota còn: T1.4.
- **Tuần 10–16/07:** T1.4 (nếu chưa), T2.2, polish paper A; chờ EULA.
- **17/07:** checkpoint EULA — chưa hồi âm → follow-up.
- **Khi MSP-Podcast về (ước tuần 3–5):** T2.4→T2.7 (~2 tuần, GPU-bound).
- **Khi DAIC về:** T2.8, T2.9.
- **Sau đó:** gate tầng 3.

## Rủi ro & ứng phó
- **EULA trễ >4 tuần:** paper B nộp bản proxy-caveat (mechanics đã chứng minh) hoặc dời venue; tầng 3 auto-defer.
- **Whisper-L-V3 features nặng** (encoder 640M): nếu extract quá quota → chỉ XEUS + WavLM, Whisper để phụ lục.
- **DAIC nhãn crisis gián tiếp** (PHQ-8/binary depression, không phải SI trực tiếp): định nghĩa crisis label mapping TRƯỚC khi chạy, ghi vào spec — tránh cherry-pick sau khi thấy số (ambiguity escalates up).
- **MSP-Podcast DTA điều khoản báo cáo:** đọc kỹ điều khoản publish trước khi đưa số vào paper.

## Decision Log
- **2026-07-03 — Tạo plan này từ M8 [[bimodal-ser-papers]]:** phương án bậc thang user đã duyệt (EULA gửi qua giáo sư cùng ngày). Chi tiết căn cứ từng bài: bảng M6/M7 doc đó.
- **2026-07-03 — κ dùng quadratic weighting:** khớp QWK đã dùng làm ordinal metric chính. Rejected: unweighted κ (mù ordinal).
- **2026-07-03 — Tầng 3 gate cứng, không chạy song song:** novelty thật nhưng phụ thuộc DAIC + quota; chạy song song rủi ro trễ cả A và B. Rejected: all-in bimodal (đã loại ở M8).

## Open Questions
- [ ] DAIC-WOZ crisis label mapping: PHQ-8 threshold nào ↔ crisis positive? → quyết trước T2.8, cần đọc EULA docs + prior art (Wu SSL-depression [39 voice-stream]) khi data về.

## Completed Work
- 2026-07-03 — EULA MSP-Podcast + DAIC gửi (giáo sư, email).
- 2026-07-03 — Plan 3 tầng viết + mirror vào harness tasks.

## Remaining Action Items
- [ ] T1.1 κ + confusion (blocker #1)
- [ ] T1.2 điền baseline vào draft
- [ ] T1.3 pilot groundedness filter
- [ ] T2.1 push kernel voice-mtl-heads
- [ ] (chuỗi còn lại theo bảng từng tầng)
