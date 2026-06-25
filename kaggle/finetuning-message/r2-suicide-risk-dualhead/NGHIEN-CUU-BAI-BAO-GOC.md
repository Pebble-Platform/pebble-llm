# Nghiên cứu bài báo gốc — Hierarchical Dual-Head Model for Suicide Risk Assessment via MentalRoBERTa

> **Yang, Wang, Tan, Tan, Ji, Zhou** — *2025 IEEE International Conference on Big Data* (BigData 2025).
> arXiv:2510.20085 (23/10/2025). Bài dự **IEEE BigData 2025 Cup**: Detection of Suicide Risk on Social Media.
> Nguồn đọc: arXiv abstract + full-text (ar5iv). Doc này là bản nghiên cứu lại, đối chiếu số liệu chính xác.

---

## 1. Bài toán

Dự đoán **mức nguy cơ tự sát của 1 user** `y ∈ {0,1,2,3}` từ chuỗi bài đăng Reddit theo thời gian.

| Mức | Tên | Ý nghĩa |
|---|---|---|
| 0 | **Indicator** | Dấu hiệu/cảnh báo, không ý định chết (gồm cả nói về người khác) |
| 1 | **Ideation** | Có ý nghĩ/mong muốn chết, chưa có kế hoạch |
| 2 | **Behavior** | Chuẩn bị/lên kế hoạch, tự hại không rõ ý định chết |
| 3 | **Attempt** | Đã từng cố tự sát |

Ba thách thức bài báo nêu ngay ở abstract:
1. **Mất cân bằng lớp nghiêm trọng** (Attempt rất hiếm).
2. **Độ phức tạp thời gian** trong mẫu hình đăng bài.
3. **Bản chất kép** của mức nguy cơ: vừa **ordinal** (0<1<2<3) vừa **categorical** (mỗi mức ứng một can thiệp lâm sàng riêng).

Cấu trúc mẫu: **1 sequence = 5 bài liên tiếp + timestamp**; **bài thứ 6** dùng làm tham chiếu gán nhãn ground-truth cho 5 bài trước.

---

## 2. Kiến trúc — 6 khối (Fig 1)

```
5 bài + Δt
   │
[1] MentalRoBERTa (đóng băng 50%)  → eᵢ ∈ ℝ⁷⁶⁸  (lấy [CLS] mỗi bài)
   │  + [2] Temporal embedding  ēᵢ = eᵢ + eᵢᵗⁱᵐᵉ
   ▼
[3] Sequence Transformer (3 lớp, 8-head)  → S = [s₁..s₅]
   ▼
[4] Attention Pooling (4-head, query học được)  → u ∈ ℝ⁷⁶⁸
   │  + [5] Statistical features (optional)  u_fused
   ▼
[6] Dual Heads:  CORAL (ordinal) + Classification (categorical)
   ▼
p_final = 0.5·p_CORAL + 0.5·p_class   (ensemble lúc infer)
```

1. **Post-Level Encoding — MentalRoBERTa.** `mental/mental-roberta-base` (RoBERTa-base, 12 lớp, hidden 768, 125M, pretrain trên Reddit mental-health). Mỗi bài → tokenize max-len **512** → lấy `[CLS]` → `eᵢ ∈ ℝ⁷⁶⁸`. **Đóng băng embedding + 6 lớp đầu (50%)** → trainable ~70M.
2. **Temporal Embedding.** `Δtᵢ = min(tᵢ₊₁−tᵢ, 365)` ngày, `Δt₀=0`. `eᵢᵗⁱᵐᵉ = Dropout(ReLU(LayerNorm(Wₜ·Δtᵢ + bₜ)))`, `Wₜ ∈ ℝ⁷⁶⁸ˣ¹`. Cộng: `ēᵢ = eᵢ + eᵢᵗⁱᵐᵉ`.
3. **Sequence Transformer.** 3 lớp, **8-head** self-attn (head dim 96), residual + LayerNorm, FFN hidden **3072** + GELU.
4. **Attention Pooling.** **4-head** MHA với **query học được** `q ∈ ℝ⁷⁶⁸`: `u = MHA(q, S, S)` + key-padding-mask cho bài pad.
5. **Statistical Features (optional).** Thống kê độ dài bài (mean/std/min/max từ) + thống kê time-interval → MLP 2 lớp → `f_stat`; fuse `u_fused = Linear([u; f_stat])`.
6. **Dual Heads.**
   - **CORAL** (ordinal): chia sẻ `w_c ∈ ℝ⁷⁶⁸` + bias có thứ tự `b₁<b₂<b₃`: `P(y>k|u)=σ(w_cᵀu+b_k)`, `k∈{0,1,2}`.
   - **Classification**: `z_class = W_class·u + b_class ∈ ℝ⁴`.

---

## 3. Hàm loss — tri-objective

`L_total = 0.5·L_CORAL + 0.3·L_CE + 0.2·L_Focal`

- **CORAL**: target nhị phân `t_k = 𝟙[y>k]`, BCE trên `σ(z_k)` — chia sẻ trọng số + bias có thứ tự ⇒ dự đoán **đơn điệu**.
- **CE + label smoothing** ε=0.1 — giảm overconfidence.
- **Focal** γ=2, `α_i` = nghịch đảo tần suất lớp — chống mất cân bằng.

---

## 4. Chiến lược huấn luyện

- Đóng băng embedding + 6 lớp đầu → ~70M trainable.
- **LR phân biệt**: `2e-5` cho lớp RoBERTa mở băng, `1e-4` cho phần khởi tạo mới.
- AdamW (wd 0.01), **cosine + 10% warmup**, grad-accum 2 × batch 8 (**effective 16**), clip 1.0.
- Dropout 0.3, label smoothing 0.1, **AMP** (mixed-precision).
- **Text augmentation** (mỗi bài, xác suất 50%): 1 trong {xóa ngẫu nhiên 10% từ, hoán đổi 2 từ, thay 10% từ bằng synonym WordNet}.
- **5-fold stratified CV**, early stopping patience 5 theo val macro-F1.

---

## 5. Dataset & pipeline làm giàu (đây là phần quan trọng nhất cho bài của ta)

**Nguồn:** dataset tự xây từ Reddit (r/depression, r/SuicideWatch) — **không phải HKIE benchmark public**.

| Tập | Tổng | L0 Indicator | L1 Ideation | L2 Behavior | L3 Attempt |
|---|---|---|---|---|---|
| **Gốc** (post-level) | 7 383 | 2 480 | 3 536 | 1 019 | 348 |
| **Sau augment** (~) | ~11 105 | ~3 198 | ~5 423 | ~1 950 (+92%) | ~701 (+53%) |

**Pipeline làm giàu (2 nhánh):**

- **Nhánh 1 — In-sample LLM generation:** ưu tiên lớp hiếm (Level 3). Sinh **3 biến thể/bài** bằng paraphrase + back-translation mô phỏng, **giữ ngữ nghĩa + ngôi thứ nhất + mức nguy cơ**. Nhân ~3× số mẫu Level 3.
- **Nhánh 2 — External crawl + LLM label:** crawl bài thật r/SuicideWatch → ghép sequence 5 bài/user → **"bài thứ 6 làm tham chiếu gán nhãn"** → **ensemble nhiều LLM bỏ phiếu** (majority voting) → lọc còn **3 722 sequence** chất lượng cao.

---

## 6. Kết quả gốc (số chính xác — lưu ý paper tự vênh nhẹ giữa 3 bảng)

**Bảng I — So với baseline:**

| Model | Macro-F1 | QWK | Weighted-F1 |
|---|---|---|---|
| BiLSTM-MTL | 0.4194 | 0.3419 | 0.4688 |
| Transformer-HAN | 0.4906 | 0.4329 | 0.5028 |
| **Proposed** | **0.5091** | **0.4692** | 0.4870 |

**Bảng II — Ablation:**

| Variant | Macro-F1 | MAE | QWK |
|---|---|---|---|
| No Transformer | 0.5020 | 0.6747 | 0.4421 |
| No Features | 0.5094 | 0.6706 | 0.4439 |
| **Full Model** | **0.5193** | **0.6446** | **0.4575** |

**Tác động augmentation:**

| Dữ liệu | Macro-F1 | MAE | QWK |
|---|---|---|---|
| Original (imbalanced) | 0.3540 | 0.7244 | 0.2410 |
| **Augmented (full)** | **0.5098** | 0.6474 | 0.4692 |

→ Augment cho **+0.155 macro-F1 (~+44% rel)**, QWK `0.241 → 0.469`.

> ⚠️ **Số chính của paper không nhất quán tuyệt đối**: macro-F1 của model đề xuất xuất hiện dưới 3 giá trị `0.5091 / 0.5098 / 0.5193` ở 3 bảng khác nhau (so-baseline, augmentation, ablation-full). Khi trích dẫn nên ghi rõ **lấy từ bảng nào**. Điểm này cũng là một quan sát đáng nêu trong related-work của ta.

---

## 7. Hạn chế (paper không có mục riêng — suy ra từ nội dung)

1. **Mất cân bằng vẫn chỉ vá một phần** dù đã augment (Behavior/Attempt vẫn yếu).
2. **Phụ thuộc cửa sổ 5 bài** — không hỗ trợ đánh giá đơn-bài; không khảo sát độ nhạy theo độ dài chuỗi.
3. **Macro-F1 ~0.51** — còn nhiều dư địa.
4. **Chủ yếu tiếng Anh / Reddit** — chưa rõ tổng quát sang nền tảng/ngôn ngữ khác.
5. **Nhãn-LLM của nhánh crawl** chỉ được kiểm bằng majority-voting; **không đo agreement với nhãn lâm sàng** → đây chính là khe hở mà bài reproduction của ta khai thác (gold-holdout).

---

## 8. Đối chiếu với bản tái hiện của ta & ý nghĩa cho bài báo

| Khía cạnh | Paper gốc | Bản của ta |
|---|---|---|
| Dataset | Reddit tự xây (gated-style), 7 383 → ~11k | **CSSRS-500 public** (392) + làm giàu **9 680 nhãn-LLM** |
| Augment | In-sample LLM + crawl + **ensemble-LLM** | scrape pullpush + **đơn-LLM** (gpt-5.4-mini), lọc confidence |
| Timestamp | Có Δt thật | **Δt=0** (CSSRS-500 không có) → temporal head ≈ bias hằng |
| Đánh giá | 5-fold CV trên chính tập (in-distribution) | **gold-holdout** (train nhãn-LLM → test gold lâm sàng) |
| Macro-F1 | 0.51 (augmented) | **0.385 gold** / 0.667 within-LLM |

**Ba điểm bài reproduction của ta đóng góp thêm so với paper gốc:**

1. **Đánh giá trung thực hơn.** Paper đo in-distribution (5-fold CV trên chính tập đã augment-LLM) → lạc quan. Ta dùng **gold-holdout**, lộ khoảng cách **nhãn-LLM ↔ lâm sàng ≈ 0.28** mà paper không đo.
2. **Định lượng giá trị augment trên benchmark public** (CSSRS-500): từ 0.19 (gold-only) → 0.385 (LLM-augmented).
3. **Phơi bày nút thắt lớp hiếm.** Behavior chỉ 6.5% pool → F1 ~0.18; cảnh báo augment đơn-LLM không tự giải quyết được lớp hiếm.

---

## 9. Map sang Pebble

- **CORAL ordinal head** = ứng viên trực tiếp cho head `severity` của Pebble (thay CE phẳng) — giải đúng "lỗi adjacent".
- **Tri-objective CORAL+CE+Focal** = cách trộn ordinal + categorical + chống imbalance.
- **Freeze 50% + differentiated LR** = trùng kế hoạch staged-unfreeze của Pebble.
- **Ensemble 2 head** = ý tưởng cho head đa-mục-tiêu.

---

## Nguồn

- arXiv:2510.20085 — abstract + full-text (ar5iv.labs.arxiv.org).
- Số liệu tái hiện của ta: `KET-QUA-PHAN-TICH.md`, log Kaggle (luồng A/B).
- Doc nền cũ (đã thay bằng bản này): `docs/papers/finetuning-message/R2-DEEP-method-and-repro-vi.md`.
