# Kế hoạch viết báo — BÀI 2 (Voice): Recall-Floored Heterogeneous Heads cho Crisis-Sensitive Speech Affect

> **Đích nộp:** IEEE (ICASSP/INTERSPEECH-class hoặc IEEE Access/EMBC). Format double-column ~6–10 trang.
> **Trạng thái:** backbone-selection đã có kết quả thật; MTL-heads kernel **đã build, CHƯA chạy Kaggle**; quyết định nâng cấp affect bằng **MSP-Podcast** (nhãn A/V/D thật, voice-only).
> **Nguồn:** [`../../voice-method-selection.md`](../../voice-method-selection.md) (backbone results) ·
> [`../../tasks/voice-mtl-heads.md`](../../tasks/voice-mtl-heads.md) (MTL heads) ·
> kernels `../../../kaggle/voice/pebble-voice-backbone/` + `../../../kaggle/voice/pebble-voice-mtl-heads/`

---

## 1. Tiêu đề nháp & đóng góp

**Title:** *Backbone Selection and Recall-Floored Heterogeneous Heads for Crisis-Sensitive Speech Affect*

**Claim chính:**
> (1) **Paired-delta backbone selection** emotion2vec vs WavLM-Large (frozen probe, 3 seed) cho speech-affect → WavLM thắng (Δ macro-F1 = **−0.071**, 3/3 seed <0). (2) Chuyển **hard crisis-recall-floor head** sang modality giọng nói: precision @ recall≥0.90 = **0.617**. (3) **Heterogeneous MTL** (emotion CE + affect V/A CCC + crisis BCE) cân bằng bằng **Kendall uncertainty weighting** — với affect đo trên **nhãn V/A thật của MSP-Podcast**.

---

## 2. Đã có (mạnh, thật) — không làm lại

| Hạng mục | Số / trạng thái |
|---|---|
| Backbone paired-delta (RAVDESS, 3 seed) | WavLM macro-F1 **0.609 ± 0.019** vs emotion2vec **0.537 ± 0.007**; Δ **−0.071 ± 0.017** |
| Recall-floor distress head | precision@recall0.90 = **0.617 ± 0.003** (thr 0.69) |
| Verify end-to-end | FastAPI verifier chạy thông trên clip held-out |

---

## 3. ⚠️ Điểm yếu lớn nhất & hướng đã chốt

**Affect V/A head hiện dùng nhãn proxy circumplex cố định** → gần circular, *không meaningful* (chính `voice-mtl-heads.md` đã ghi). **Quyết định:** **nâng cấp bằng MSP-Podcast** (nhãn arousal/valence/dominance liên tục, thật; voice-only nên KHÔNG vi phạm ràng buộc "không paired data").
- CCC trên MSP-Podcast = con số affect thật, citable (so với AVEC notes 37–38).
- RAVDESS vẫn giữ cho **emotion 8-lớp + backbone-selection + crisis-proxy** (acted, đóng khung proxy).

---

## 4. Còn thiếu để IEEE duyệt (ưu tiên giảm dần)

| # | Hạng mục | Việc cụ thể |
|---|---|---|
| 🔴 1 | **Request + nạp MSP-Podcast** | Đăng ký access (nhẹ hơn DUA paired); viết loader A/V/D; cache frozen features WavLM/emotion2vec |
| 🔴 2 | **Chạy Kaggle MTL-heads** | M3–M5 đang pending; lấy 10-fold metrics cho cả 3 head + artifact load local |
| 🔴 3 | **CCC head trên MSP-Podcast** | Train affect head trên nhãn thật → báo cáo CCC(valence/arousal) thật |
| 🟡 4 | **Ablation MTL** | single-head vs 3-head; **Kendall vs GradNorm/PCGrad** (notes 06–08) — comparator đã định |
| 🟡 5 | **Baseline SER** | eGeMAPS/openSMILE + SVM (notes 29–31) làm sàn so sánh |
| 🟡 6 | **Limitations** | RAVDESS acted ≠ crisis lâm sàng; crisis-proxy; cross-corpus (RAVDESS↔MSP) khác domain |

---

## 5. Outline IEEE

1. **Introduction** — crisis-recall là ràng buộc an toàn cứng; câu hỏi backbone + head topology cho speech affect.
2. **Related Work** — SSL speech (WavLM note 26, emotion2vec note 25), SER survey (note 28), MTL balancing (Kendall/GradNorm/PCGrad notes 06–08), dimensional affect (AVEC notes 37–38), SSL-depression (notes 39–41).
3. **Method** — frozen probe; **heterogeneous heads** (emotion CE + affect CCC + crisis BCE); **recall-floor thresholding**; Kendall weighting.
4. **Experiments** — (a) backbone paired-delta (RAVDESS); (b) recall-floor distress; (c) **affect CCC trên MSP-Podcast**; (d) ablation MTL + baseline SER.
5. **Limitations** — proxy crisis, acted speech, cross-corpus.
6. **Conclusion.**

---

## 6. Reviewer-risk & phản biện

- *"Proxy V/A vô nghĩa"* → đã thay bằng MSP-Podcast nhãn thật.
- *"emotion2vec thua chỉ vì protocol"* → đã có paired-delta 3/3 seed + giải thích (WavLM lớn hơn, pretrain nhiều hơn ~360×).
- *"recall-floor 0.90 tùy chọn"* → báo cáo precision-recall curve, không chỉ 1 điểm.
- *"frozen probe quá đơn giản"* → đóng khung là backbone-selection + head-topology study, chi phí thấp có chủ đích.

---

## 7. Timeline / checklist

- [ ] (3–5d) Request MSP-Podcast access (đường găng — bắt đầu trước).
- [ ] (1–2d) Push + chạy Kaggle MTL-heads, pull `out/` (M3), test artifact local (M4).
- [ ] (3–4d) Loader MSP-Podcast + cache features + train CCC head.
- [ ] (2–3d) Ablation Kendall vs GradNorm/PCGrad + baseline eGeMAPS.
- [ ] (3d) Viết draft IEEE + bảng + limitations.
- [ ] (2d) Vòng review nội bộ.
