# Tasks — 004 vnser-training

Thứ tự thực thi; mỗi task có exit criteria map tới check chạy được (rule 4, red-first).
**Trạng thái: T1–T5 XONG (2026-07-06).** Kết quả: `expected-results.md` (Run 2).

## T1 — Split builder GroupKFold + test (I4) ✅
- ✅ done
- `scripts/vietnamese-ser/make_splits.py`: đọc `manifest.csv` (row `is_clean`) →
  group `(ep, speaker)` → `GroupKFold` 5-fold (deterministic, seed logged) →
  `splits.csv` (cột `id, fold`).
- `tests/invariants/test_speaker_disjoint.py`: không unit `(ep,speaker)` nào xuất
  hiện ở >1 fold.
- **Exit:** test đỏ trước, xanh sau; chạy lại 2 lần → cùng split-hash.

## T2 — Kernel training `vnser-train` ✅
- `kaggle/vietnamese-ser/vnser-train/`: frozen WavLM-Large trích feature (cache `.npz`)
  → 3 heads → `cv_metrics()` gọi 2 lần: **GroupKFold(ep,speaker) + Leave-one-series-out**.
- ✅ chạy Kaggle GPU exit 0 (v5, ~15'); `artifact_wavlm-large/config.json`; không audio
  trong output (I1). 3 lỗi môi trường đã fix: path mount → torchvision 0.20.1 → transformers 4.46.3.

## T4 — Report + provenance (I5, I6) ✅
- ✅ `report.md` 2 bảng (A GroupKFold + B LOSO) + 95% CI; banner silver; `metrics.json`
  + `config.json` (model_id, seed, split-hash, pip pin, cả 2 metrics).

## T5 — Ship (WORKFLOW rule 5) ✅
- ✅ `docs/spec/capabilities/training-baseline.md` (số thật Run 2); README status →
  shipped; index `changes/README.md` cập nhật.

## Verification

| # | Intent | Check | Where |
|---|---|---|---|
| 1 | Group-disjoint (ep,speaker) splits (I4 best-effort) | `test_speaker_disjoint.py` | CI, mỗi PR |
| 2 | Split deterministic | cùng split-hash qua 2 run | T1 manual |
| 3 | Không audio thô trong output kernel (I1) | grep output manifest kernel | T2 |
| 4 | Kernel pin stack (I5) | grep `torch==2.5.1+cu121` trong `kaggle/**` | CI |
| 5 | Silver ≠ accuracy + caveat I4 (I6) | report-lint disclaimer mỗi bảng metric | CI |
| 6 | Chỉ nạp `is_clean` row (I3) | assert trong kernel/loader | T2 nạp data |
