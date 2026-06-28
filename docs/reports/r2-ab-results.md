# R2 — Kết quả & đánh giá: Run A (within-dist) + Run B (gold + rebalance)

> Cập nhật 2026-06-24. Mục tiêu: "vượt paper" trên hai thước đo (within-distribution như paper, và gold-holdout trung thực).
> Baseline: gold-holdout 0.3569 (chưa rebalance); paper 0.5098 (within-distribution CV).

## TL;DR
- **Run A (within-distribution CV) — HỢP LỆ (2026-06-26), VƯỢT PAPER:** đã tải đúng **10,072 mẫu** từ 10k
  (sửa xong lỗi đường dẫn), 5-fold CV macro-F1 = **0.6530 ±0.0048** → **> paper 0.5098 (+0.143, +28%)**.
  Con số sạch thay cho proxy val-on-LLM 0.666. (Lưu ý: cùng *giao thức* within-distribution trên tập 10k đã làm
  giàu của ta, không phải benchmark gated gốc của paper.)
- **Run B (gold-holdout + rebalance Behavior) — HỢP LỆ, đã cải thiện:** gold macro-F1 **0.3569 → 0.3849**
  (+0.028, +7.8%), QWK 0.378 → 0.398, MAE 0.840 → 0.822. Cả 3 metric đều tốt hơn.
- **Ablation flat-CE (2026-06-26) — bất ngờ:** bỏ CORAL+Focal, chỉ CE thuần → gold macro-F1 **0.4215** (> dual-head
  0.3849) và Behavior **0.285** (> 0.183). Tri-objective đang *kém hơn* CE thuần trên gold (xem §5).

## 1. Run B — gold-holdout + rebalance (HỢP LỆ)
Train pool 9,680 (nhãn-LLM) `[3992,3612,634,1442]` · test = gold lâm sàng CSSRS-500 392 `[99,171,77,45]` · ~9.2h.

| Metric | Baseline (no balance) | **Run B (balance)** | Δ |
|---|---|---|---|
| GOLD macro-F1 | 0.3569 | **0.3849** ±0.0071 | **+0.028** |
| GOLD QWK | 0.378 | **0.398** | +0.020 |
| GOLD MAE | 0.840 | **0.822** | −0.018 (tốt hơn) |
| val-on-LLM | 0.638 | 0.666 | +0.028 |

**Per-class F1 (gold, trung bình 5 fold):**
| Lớp | F1 |
|---|---|
| Indicator | 0.502 |
| Ideation | 0.480 |
| **Behavior** | **0.183** ⚠ |
| Attempt | 0.374 |

→ Rebalance **giúp toàn cục** (macro-F1, QWK, MAE đều lên). Nhưng **Behavior vẫn là nút thắt (0.183)** —
cân bằng sampling không đủ, vì chỉ có 634 mẫu Behavior và phần lớn là **nhãn LLM (under-label + nhiễu)**.
→ Trần của Behavior giờ là vấn đề **chất lượng nhãn**, không phải sampling.

## 2. Run A — within-distribution CV (HỢP LỆ, 2026-06-26)
- Chạy trên account đã phone-verify `phatneurondai`. Tải đúng dataset mount (recursive glob `**/sequences.csv`):
  **10,072 sequences** `[4091, 3783, 711, 1487]` — **không** còn rơi về Zenodo 392.
- **5-fold within-distribution CV macro-F1 = 0.6530 ±0.0048** (folds [0.649, 0.660, 0.656, 0.654, 0.646]).
- **vs paper 0.5098 → +0.143 (+28% rel) — VƯỢT PAPER** trên thước đo within-distribution của họ.
- (Lịch sử: 2 lần đầu hỏng do lỗi đường dẫn `/kaggle/input` → tải nhầm Zenodo 392; đã sửa bằng recursive glob.)
- Log: `kaggle/finetuning-message/r2-within-dist-cv/out/r2-within-dist-cv-10k-balanced.log`.

## 3. Verdict "vượt paper"
| Thước đo | Mốc paper | Của ta | Trạng thái |
|---|---|---|---|
| Within-distribution (5-fold CV sạch) | 0.5098 | **0.6530** | ✅ **vượt** (+0.143; số sạch, không còn proxy) |
| Gold-holdout (trung thực, khó hơn) | — (paper không đo) | **0.4215** (flat-CE) / 0.3849 (dual) | ▲ cải thiện từ 0.3569; flat-CE tốt nhất hiện tại |

## 4. Ablation ordinal-head: flat-CE vs dual-head (gold-holdout, 2026-06-26)
Cùng giao thức gold-holdout + balance + epochs 10; chỉ đổi trọng số loss (`R2_W_CORAL/CE/FOCAL`). Eval đã sửa để
chỉ blend head được train (flat-CE → chỉ dùng head CE).

| Cấu hình | GOLD macro-F1 | QWK | MAE | Per-class F1 (Ind·Idea·**Beh**·Att) |
|---|---|---|---|---|
| Dual-head (0.5/0.3/0.2 + Focal) — Run B | 0.3849 | 0.398 | 0.822 | 0.502·0.480·**0.183**·0.374 |
| **flat-CE (1/0/0)** | **0.4215** ±0.024 | 0.388 | 0.785 | 0.488·0.524·**0.285**·0.390 |

→ **Bất ngờ: CE thuần vượt tri-objective trên gold (+0.037)**, và **cứu lớp Behavior** (+0.10, 0.183→0.285).
Gợi ý CORAL+Focal đang *kìm* Behavior khi chuyển sang gold (có thể overfit phân bố nhãn-LLM). ⚠ Một seed/một run —
cần chạy **CORAL-only** (`1/0/0` cho coral) + lặp seed để chốt; nhưng đây là một dòng ablation mạnh cho bài IEEE.

## 5. Hạn chế còn lại (theo thứ tự đáng làm tiếp)
1. **Loss design** — flat-CE > tri-objective trên gold (mục 4): chạy nốt CORAL-only + lặp seed; xem lại trọng số.
2. **Chất lượng nhãn Behavior** — vẫn là nút thắt (kể cả flat-CE mới 0.285). Tier-1 cleanlab (đã build) để đo/lọc nhiễu.
3. **Encoder mirror + max-len 256** — chưa dùng `mental/mental-roberta-base` thật (gated) và bị cắt 256 token.
4. **Δt=0, đa số 1-post** — temporal head chưa khai thác.

## Provenance
- Run A (within-dist, sạch): kernel `phatneurondai/r2-within-dist-cv-10k-balanced` · log `kaggle/finetuning-message/r2-within-dist-cv/out/`.
- flat-CE ablation: kernel `phatneurondai/r2-ablation-flatce` · log `kaggle/finetuning-message/r2-ablation/out/`.
- Run B (gold + balance, dual-head): kernel `r2-suicide-risk-dual-head-mentalroberta` v7.
- Baseline gold-holdout (0.3569): `docs/reports/r2-gold-holdout-report.html`.
- Tracking: `docs/tasks/r2-beat-paper-dual-report.md` · `docs/tasks/r2-finetuning-methods-for-ieee.md`.
