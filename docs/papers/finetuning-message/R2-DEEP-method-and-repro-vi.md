# R2 — Phân tích chi tiết + tái hiện: Hierarchical Dual-Head Model for Suicide Risk Assessment via MentalRoBERTa

> Yang, Wang, Tan, Tan, Ji, Zhou — **IEEE BigData 2025 Cup** (Detection of Suicide Risk on Social Media).
> arXiv:2510.20085 (23 Oct 2025). PDF local: [`pdfs/R2-hierarchical-dualhead-mentalroberta.pdf`](pdfs/R2-hierarchical-dualhead-mentalroberta.pdf).
> Tài liệu này: (1) phân tích method đầy đủ để code lại, (2) dataset + thay thế, (3) ghi chú tái hiện.

---

## 1. Bài toán
Dự đoán **mức nguy cơ tự sát của 1 user** `y ∈ {0,1,2,3}` từ chuỗi N bài đăng theo thời gian.
- **0 Indicator** — dấu hiệu/cảnh báo, không có ý định chết (gồm cả nói về người khác).
- **1 Ideation** — có ý nghĩ/mong muốn chết, chưa có kế hoạch.
- **2 Behavior** — chuẩn bị/lên kế hoạch, tự hại không rõ ý định chết.
- **3 Attempt** — đã từng cố tự sát trong quá khứ.
- Tính chất **kép**: vừa **ordinal** (0<1<2<3) vừa **categorical** (mỗi mức có can thiệp lâm sàng riêng).
- Cấu trúc mẫu: 1 sequence = **5 bài liên tiếp** + timestamp; **bài thứ 6** dùng để gán nhãn (ground truth).

## 2. Kiến trúc (Fig 1) — 6 khối
1. **Post-Level Encoding — MentalRoBERTa**: `mental/mental-roberta-base` (RoBERTa-base, 12 layer, hidden 768, 125M, pretrain trên Reddit MH). Mỗi bài → tokenize max-len 512 → lấy `[CLS]` → `eᵢ ∈ ℝ⁷⁶⁸`. **Đóng băng embedding + 6 layer đầu (50%)** → trainable 125M→~70M.
2. **Temporal Embedding**: `Δtᵢ = min(tᵢ₊₁−tᵢ, 365)` ngày, `Δt₀=0`. `eᵢᵗⁱᵐᵉ = Dropout(ReLU(LayerNorm(Wₜ·Δtᵢ + bₜ)))`, `Wₜ ∈ ℝ⁷⁶⁸ˣ¹`. Cộng vào: `ēᵢ = eᵢ + eᵢᵗⁱᵐᵉ`.
3. **Sequence Transformer**: 3 layer, **8-head** self-attn (head dim 96), residual+LayerNorm, FFN hidden **3072** + GELU. Ra `S = [s₁..s₅] ∈ ℝ⁵ˣ⁷⁶⁸`.
4. **Attention Pooling**: **4-head** MHA với **query học được** `q ∈ ℝ⁷⁶⁸`: `u = MHA(q, S, S)` + key-padding-mask cho bài pad → `u ∈ ℝ⁷⁶⁸`.
5. **Statistical Features (optional)**: thống kê độ dài bài (mean/std/min/max word) + thống kê time-interval → MLP 2 lớp → `f_stat ∈ ℝ⁶⁴`; fuse `u_fused = Linear([u; f_stat])`.
6. **Dual Heads**:
   - **CORAL** (ordinal): chia sẻ `w_c ∈ ℝ⁷⁶⁸` + bias có thứ tự `b₁<b₂<b₃`: `P(y>k|u)=σ(w_cᵀu+b_k)`, `k∈{0,1,2}`.
   - **Classification**: `z_class = W_class·u + b_class ∈ ℝ⁴`.
   - **Ensemble lúc infer**: `p_final = 0.5·p_CORAL + 0.5·p_class`.

## 3. Hàm loss — tri-objective
`L_total = 0.5·L_CORAL + 0.3·L_CE + 0.2·L_Focal`
- **CORAL**: target nhị phân `t_k = 𝟙[y>k]`, `L = −Σ_k [t_k logσ(z_k) + (1−t_k)log(1−σ(z_k))]`.
- **CE + label smoothing** ε=0.1.
- **Focal** γ=2, `α_i` = nghịch đảo tần suất lớp.

## 4. Training (II-D)
- Đóng băng embedding + 6 layer đầu → ~70M trainable.
- **LR phân biệt**: 2e-5 cho layer RoBERTa mở băng, **1e-4** cho phần khởi tạo mới.
- AdamW (wd 0.01), **cosine + 10% warmup**, grad-accum 2 × batch 8 (**effective 16**), clip 1.0.
- Dropout 0.3, label smoothing 0.1.
- **Text augmentation** (mỗi bài, 50%): chọn 1 trong {xóa ngẫu nhiên 10% từ, hoán đổi 2 từ, thay 10% từ bằng synonym WordNet}.
- **Mixed-precision (AMP)**.
- **5-fold stratified CV**, early stopping patience 5 theo val macro-F1.

## 5. Metrics + kết quả gốc
Macro-F1 (chính), MAE, QWK.
| Setting | Macro-F1 | MAE | QWK |
|---|---|---|---|
| Original (imbalanced) | 0.3540 | 0.7244 | 0.2410 |
| **Augmented (full)** | **0.5098** | 0.6474 | 0.4692 |
| Ablation No-Transformer | 0.5020 | 0.6747 | 0.4421 |
| Ablation No-Features | 0.5094 | 0.6706 | 0.4439 |
| Baseline BiLSTM-MTL | 0.4194 | — | (QWK 0.3419) |
| Baseline Transformer-HAN | 0.4906 | — | (QWK 0.4329) |
- Phân bố gốc (post-level): L0 2,480 · L1 3,536 · L2 1,019 · L3 348 (tổng 7,383).
- Sau augment (sequence-level): 3,722 mẫu — L0 718 · L1 1,887 · L2 931 · L3 186.

### Kết quả tái hiện của ta (Kaggle GPU, CSSRS-500)
> Run: kernel `fabiocarava/r2-suicide-risk-dual-head-mentalroberta` (COMPLETE).
> Code: [`notebooks/r2-suicide-risk-dualhead.py`](../../../notebooks/r2-suicide-risk-dualhead.py); checkpoint `best_model.pt` (≈568 MB) tải về `kaggle/finetuning-message/r2-suicide-risk-dualhead/out/`.
- **Dữ liệu nạp**: 392 user-sequences, class counts `[99, 171, 77, 45]` (Indicator/Ideation/Behavior/Attempt) — khớp đúng §6.
- **Encoder thực dùng**: `welsachy/mental-roberta-base-finetuned-depression` (thay `mental/mental-roberta-base` — biến thể MentalRoBERTa-base đã fine-tune depression, dễ tải public).
- **5-fold CV macro-F1**: mean **0.2374** ± 0.0358 — folds `[0.2502, 0.2017, 0.1973, 0.2952, 0.2425]`; best fold 0.2952 → lưu checkpoint.

| Setting | Macro-F1 (CV) |
|---|---|
| Paper — Augmented (full, HKIE 3,722) | 0.5098 |
| **Ta — CSSRS-500 (392), không LLM-augment, Δt=0** | **0.2374** |

- **Vì sao thấp hơn paper**: đúng như các sai lệch đã ghi ở §6 — data nhỏ hơn ~10× (392 vs 3,722), không có timestamp (temporal head ≈ bias hằng), bỏ LLM/crawl-augment, max-len 256. Đây là *method reproduction* (kiến trúc + loss + training chạy đúng end-to-end), **không** phải benchmark reproduction.
- **Kiểm chứng inference**: [`notebooks/r2_infer_sample.py`](../../../notebooks/r2_infer_sample.py) nạp checkpoint (không cần tải encoder) → trên chuỗi 5 bài leo thang (có nhắc "đã từng cố tự sát năm ngoái") dự đoán **mức 3 = Attempt** (p = .25/.32/.07/.35) — pipeline dual-head chạy thông suốt.

## 6. Dataset — gốc vs thay thế
- **Gốc**: Li et al. 2022, *HKIE Transactions* vol 29(4):268–282 — **gated** (không tải công khai được). Augment thêm bằng crawl r/suicidewatch + LLM-label (GPT-4 ensemble) → không tái tạo được nếu không có API + crawl.
- **Thay thế đã chọn (public, CC-BY-4.0)**: **Reddit C-SSRS 500 users** (Gaur et al., Zenodo 2667859) — `500_Reddit_users_posts_labels.csv`.
  - Cùng ontology C-SSRS. Nhãn: Supportive 108 · Indicator 99 · Ideation 171 · Behavior 77 · Attempt 45.
  - **Ánh xạ 4 mức của paper**: bỏ *Supportive*; **Indicator→0, Ideation→1, Behavior→2, Attempt→3** (392 user). Tái hiện đúng tính ordinal + imbalance nặng (Attempt hiếm).
  - 1 user = 1 sequence (lấy **5 bài cuối**, pad nếu <5). Cột `Post` là list bài → `ast.literal_eval` (28/500 lỗi escape → fallback coi cả ô là 1 bài).

### Sai lệch có chủ đích so với paper (ghi rõ để trung thực)
1. **Dataset khác** (CSSRS-500 thay HKIE gated) — cùng ontology, nhưng nhỏ hơn nhiều (392 vs 3,722).
2. **Không có timestamp** trong CSSRS-500 → đặt `Δt=0` ∀ bài → temporal-embedding thành bias hằng (ablation paper cho thấy text trội, đây là thành phần phụ).
3. **Nhãn mức-user**, không phải "bài thứ 6" — gán nhãn user cho cả sequence (CSSRS-500 vốn label theo user).
4. **Bỏ augment bằng LLM/crawl** (cần GPT-4 + crawl) — **giữ** text-augmentation (deletion/swap/synonym) đúng như paper.
5. max-len 256 (thay 512) để tiết kiệm thời gian GPU; có thể chỉnh lại.

→ Mục tiêu tái hiện: **kiến trúc + loss + training faithfully**; con số sẽ khác paper vì data thay thế. Đây là *method reproduction*, không phải *benchmark reproduction*.

### Làm giàu dataset → 10k (2026-06-21)
Để tiến gần quy mô paper (~11k), đã **làm giàu** từ 392 lên **10,073 mẫu** theo đúng pipeline của paper (scrape + LLM-ensemble label). Chi tiết + quyết định: [`docs/tasks/enrich-suicide-risk-dataset.md`](../../tasks/enrich-suicide-risk-dataset.md).
- **Nguồn**: CSSRS-500 (392) + av9ash CSSR-S (1,170 post, 0-6→4-level) + **scrape r/SuicideWatch** qua pullpush.io (không cần creds) rồi **LLM-label** bằng Azure `gpt-5.4-mini` (8,511 mẫu on-topic, conf≥0.6).
- **Sai lệch ghi rõ**: dùng comment ngoài submission để đủ volume (kèm nhãn `-1 off-topic` để lọc nhiễu); label đơn-model (không phải ensemble 5-LLM như av9ash) → lọc bằng confidence; ~9% bị Azure content-filter chặn (đã bỏ).
- **Phân bố**: Indicator 4,091 · Ideation 3,784 · Behavior 711 · Attempt 1,487.
- **Dùng**: `R2_DATA=data/finetuning-message/external/r2-combined/sequences.csv` (loader đọc qua env).

## 7. Map sang Pebble
- **CORAL ordinal head** = ứng viên trực tiếp cho head `severity` của Pebble (thay vì CE phẳng) — giải đúng "lỗi adjacent" mà các bài C-SSRS (14–17) chỉ ra.
- **Tri-objective CORAL+CE+Focal** = cách trộn ordinal + categorical + chống imbalance; so được với hướng MTL-balancing của Pebble.
- **Freeze 50% + differentiated LR** = trùng kế hoạch staged-unfreeze của Pebble (đối lại bài học ULMFiT).
- **Ensemble 2 head** (ordinal + categorical) = ý tưởng cho head đa-mục-tiêu.
