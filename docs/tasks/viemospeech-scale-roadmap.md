# Roadmap: từ pilot 1.2k clip → corpus + method paper ViEmoSpeech

- **Slug:** viemospeech-scale-roadmap
- **Status:** in-progress
- **Created:** 2026-09-03 · **Updated:** 2026-09-03
- **Owner:** user / Claude

## Goal

Đưa ViEmoSpeech từ **pilot đã chứng minh được** (2 series, 1.193 clip nhãn người,
LOSO macro-F1 0.258) tới **corpus phát hành được + method paper tone×emotion**.
Doc này là đường găng: cái gì chặn cái gì, cái gì tốn GPU, cái gì tốn thời gian người.

## Kết luận chi phối cả roadmap

**Kaggle GPU không phải nút thắt.** Scale extraction P1 = 120 tập × ~0.30 GPU-h ≈
**36 GPU-h ≈ 2 tuần** quota miễn phí (30 GPU-h/tuần). Nút thắt thật, theo thứ tự:

1. **Nhãn người** — 1.193 clip mất ~6 tuần (2026-07-20 → 2026-08-31). Mục tiêu gold
   là 2–3k utt ⇒ còn ~1–2k clip nữa.
2. **3 quyết định chưa chốt** (P0) — chặn cả P2 lẫn mọi số cuối cùng.
3. **Method chưa build** — tầng bimodal tone×emotion, đóng góp thật của paper, chưa
   có spec cho tới change 013 (tạo 2026-09-03).

## Trạng thái đo được (2026-09-03)

| | |
|---|--:|
| Series đã extract | 2 (`chay-tron-thanh-xuan` 22 phần · `ve-nha-di-con` 10 phần) |
| Record trong `state.db` | 1.916 |
| Clip nhãn người, không rejected/multi | **1.193** |
| Clip owner đã loại | 718 (631 `multi_speaker`) |
| Clip đã qua review vòng 2 (vyphan) | 1.071 |
| κ human–human | **chưa có** |
| Model | frozen WavLM-Large + linear probe · LOSO macro-F1 **0.258** · CCC valence **0.071** |

## Milestones

### P0 — Gỡ 3 quyết định (không GPU) — CHẶN P2

- [ ] **Chốt series test.** [ADR-002](../spec/decisions/ADR-002-whole-series-speaker-disjoint-gold.md)
      chốt hold-out **whole-series** nhưng chưa chọn series nào. Chưa có ⇒ mọi số LOSO
      vẫn là tạm.
- [ ] **Media lên Kaggle: PA A hay local GPU?** [`05-scale-plan.md §6`](../papers/vietnamese-ser/05-scale-plan.md)
      để ngỏ. PA A = upload media bản quyền cho bên thứ ba giữ (dù private). **Quyết định
      pháp lý của owner, không phải kỹ thuật.** Chặn P2.
- [ ] **Chốt quy mô P1 (3 bộ) hay P2 (6 bộ).** `05-scale-plan.md §8` vẫn đang chờ.

### P1 — Vòng label mù (không GPU) — ĐƯỜNG GĂNG CỦA PAPER

Tool xong từ 2026-07-28: `/rate.html` · `build_assignments.py` · `iaa_report.py` ·
[change 011](../spec/changes/011-online-multi-annotator/README.md). Bảng `assignments`
hiện **0 dòng** — chưa ai chạy vòng nào.

- [ ] Chốt gold set theo `qc-protocol.md §2.1` (~40 clip) → `gold-set.txt`
- [ ] Seed hàng đợi (`build_assignments.py`), mời annotator, chạy 2 vòng
- [ ] `iaa_report.py` → κ/α human–human

Trả **hai** món cùng lúc: κ mà ADR-003/I6 bắt buộc, **và** tập test đủ lớn để chốt
Δ(B−A) mà 606 clip của [change 012](../spec/changes/012-label-quality-ablation/README.md)
không phân giải nổi. Không có κ thì paper không nộp được, bất kể model tốt cỡ nào.

### P2 — Scale extraction trên Kaggle (lần "chạy thực" đầu tiên)

Kernel `kaggle/vietnamese-ser/vnser-extract/` đã build (torch 2.5.1 / pyannote 3.x,
HF token qua Kaggle Secrets, smoke local PASS) nhưng **CHƯA từng push**.

- [ ] Push + chạy **1 tập trước** để chốt GPU-h thật/tập — `0.30` mới là *ước lượng*,
      chưa bao giờ đo trên P100 vì kernel chưa push. Số này quyết lịch cả P2.
- [ ] Chạy batch theo quota (30 GPU-h/tuần · tối đa 2 session song song; song song rút
      wall-clock, **không** tăng trần)
- [ ] Cập nhật `extraction-pipeline.md` với số đo thật

### P3 — Label corpus đã scale tới mức gold (không GPU)

- [ ] Label thêm ~1–2k clip → tổng 2–3k gold utt
- [ ] **Không** lọc theo đồng thuận — change 012 đo được C không hơn C′ (Δ +0.011/−0.022,
      CI đều chứa 0) ⇒ giữ cả clip bất đồng
- [ ] Ưu tiên soát **arousal** hơn emotion nếu có vòng soát (012: CCC arousal là chỗ
      review có tác dụng rõ nhất)

### P4 — Train thật trên Kaggle

- [ ] **P4.1 — Fine-tune backbone** (bỏ frozen probe). Chi phí GPU **chưa đo** → chạy
      1 lần nhỏ lấy số trước khi lập lịch quota.
- [ ] **P4.2 — Bake-off backbone đa ngữ.** WavLM-Large là English-centric; câu hỏi mở đã
      ghi trong `training-baseline.md`, chưa ai chạy.
- [ ] **P4.3 — Bimodal tone×emotion** → [change 013](../spec/changes/013-bimodal-tone-emotion/README.md).
      Động cơ nằm ngay trong số đo: **CCC valence 0.071 ở LOSO** — audio một mình gần như
      không đọc được valence.

### P5 — Release

- [ ] Export public (phase 4, chưa build): nhãn người + loại rejected + loại test-series
      + strip text. `build_kaggle_gold.py` hiện mới là dump thô.
- [ ] Features + timestamps + labels + speaker id, CC-BY (intent §1)

## Thứ tự chạy

```
P0  ──┬─→ P2 (GPU) ──→ P3 (người) ──┐
      │                              ├─→ P4 ──→ P5
      └─→ P1 (người, song song) ─────┘
```

P1 và P2 chạy **song song**: một cái tiêu thời gian người, một cái tiêu GPU.

**Sai lầm dễ mắc:** nhảy thẳng vào P4 vì nó kỹ thuật và hấp dẫn, trong khi κ chưa có.

## Decision Log

- **2026-09-03 — Roadmap này lập sau khi có kết quả change 012.** Ba kết luận từ 012
  định hình P3/P4: (a) dọn nhãn **chưa** chứng minh được cải thiện model (Δ +0.024,
  CI chứa 0 ⇒ H0) nên không ưu tiên phân xử 465 bất đồng trước P1; (b) lọc theo đồng
  thuận **không** có lợi ⇒ giữ clip bất đồng; (c) CCC valence ~0.07 củng cố lý do tồn
  tại của nhánh bimodal.
- **2026-08-31 — Ngưỡng quyết định 012 chốt ở 0.02 macro-F1**, 10 seed, giữ nhánh C′.
  Xem [preregistration](../spec/changes/012-label-quality-ablation/preregistration.md).

## Câu hỏi mở

- Vòng mù cần bao nhiêu annotator và bao nhiêu clip để tập test đủ phân giải Δ ~0.02?
  (606 clip cho CI ±0.03 — chưa tính ngược ra cỡ cần thiết.)
- P4.1 fine-tune tốn bao nhiêu GPU-h trên 2–3k clip? Chưa đo, chặn việc lập lịch quota.
- Series thứ 3 lấy bộ nào trong shortlist `05-scale-plan.md §7`?
