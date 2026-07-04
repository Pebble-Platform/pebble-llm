# Giải thích code — `pebble-mlm-ablation-3seed`

Đây là một **Kaggle kernel** (một thư mục, không phải một file). Notebook
`pebble_mlm_ablation_3seed.ipynb` được *lắp ráp* từ các file `s1`–`s8` bởi
`build_ipynb.py`. Tài liệu này giải thích từng block.

## Mục tiêu tổng thể

Trả lời một câu hỏi khoa học có kiểm soát: **việc "domain-adaptive MLM
pre-training" (TAPT/DAPT) trên NeoBERT có thực sự giúp model downstream tốt hơn
không?**

Cách làm: adapt encoder **một lần** bằng MLM trên một corpus lớn *riêng biệt*
(s3/s4), rồi fine-tune **2 nhánh** — `MLM-on` (đã adapt) vs `MLM-off` (NeoBERT
gốc) — qua **3 seed** (13, 42, 1337) để lấy **delta có ghép cặp theo seed** →
kết luận có ý nghĩa thống kê thay vì may rủi 1 lần chạy.

---

## `build_ipynb.py` — bộ lắp ráp notebook
Đọc từng file `s*.py` thành 1 code cell, chèn markdown header ở giữa, rồi ghi ra
file `.ipynb`. State (biến) **chảy xuyên suốt các cell** — chạy từ trên xuống.
Điểm khéo: chạy lại s5–s7 để tinh chỉnh fine-tune **mà không phải làm lại MLM**
(s3/s4).

## `kernel-metadata.json` — cấu hình Kaggle
ID kernel, bật **GPU** (`enable_gpu`) và **internet** (`enable_internet`, cần để
tải dataset), private. Không gắn dataset/competition source nào → data tải qua
mạng lúc chạy.

## Block 0 — `_cell_install.py` — cài stack đã pin
Cài **torch 2.5.1 + transformers 4.48.2** với version cố định. Lý do quan trọng:
torch mặc định của Kaggle (2.10) **bỏ hỗ trợ sm_60 → crash trên GPU P100**. Đặt
UTF-8 cho an toàn encoding.

## Block s1 — imports & config (`s1_imports.py`)
Khai báo siêu tham số trung tâm:
- `MODEL = chandar-lab/NeoBERT`, ghim `REVISION` (reproducible).
- `MAX_LEN=64, BATCH=32`.
- **Ngân sách MLM**: `MLM_EPOCHS=2, MLM_MASK_PROB=0.15` (masking 15% chuẩn),
  `MLM_CORPUS_CAP=80000`.
- **Fine-tune**: `FT_EPOCHS=3, FT_PER_POOL=2500` (2500 mẫu mỗi task).
- `SEEDS=[13,42,1337]`.
- `set_seed()` cố định toàn bộ random (random/numpy/torch) để tái lập.

## Block s2 — dữ liệu downstream + lá chắn chống rò rỉ (`s2_data.py`)
Hai task downstream:
- **Emotion**: GoEmotions (simplified) → lấy nhãn cảm xúc đầu tiên (rỗng thì
  `neutral`).
- **Severity**: tải EI-reg (SemVal-2018) qua URL; intensity của
  anger/fear/sadness = giá trị thật, joy = 0.0 (vì joy không phải "negative
  severity"). Có **fallback synthetic** nếu tải lỗi.
- `norm()` chuẩn hoá text (lowercase + gộp space) để dedup.
- **`FT_EVAL_TEXTS`**: gom toàn bộ text fine-tune/eval vào một blacklist → để
  block s3 loại chúng khỏi corpus MLM, **tránh leakage/overfit** (điểm mấu chốt
  để thí nghiệm "sạch").

## Block s3 — xây corpus MLM lớn, *riêng biệt* (`s3_mlm_corpus.py`)
Nguồn unlabeled in-domain: **GoEmotions "raw" (~211k Reddit)** + nhiều subset
**tweet_eval** (emotion/sentiment/offensive/hate/irony). `add()` dedupe **2 lớp**:
trùng trong corpus *và* trùng với `FT_EVAL_TEXTS`. Shuffle rồi cắt còn 80k →
tokenize. Đây đúng tinh thần **TAPT/DAPT**: encoder học trên text **mới, không
nhãn, cùng domain**, không phải text sẽ dùng để eval.

## Block s4 — pre-training MLM (`s4_mlm_train.py`)
- `mask_batch()`: chiến lược BERT chuẩn — chọn 15% token (bỏ special token),
  trong đó 80% → `[MASK]`, 10% → token random, 10% giữ nguyên; token không chọn
  gán label `-100` (bỏ qua khi tính loss).
- Train `AutoModelForMaskedLM` 2 epoch, AdamW lr=5e-5, dùng AMP (mixed
  precision) + GradScaler.
- **Lưu encoder đã adapt ở fp32** (`mlm_encoder.pt`): lưu fp32 để **loại bỏ
  confound do làm tròn fp16** khi so với baseline MLM-off → so sánh công bằng.

## Block s5 — setup fine-tune multi-task hai pool (`s5_ft_setup.py`)
- Trộn 2500 mẫu emotion + 2500 mẫu severity thành dataset chung; mỗi record gắn
  `task` (EMO/SEV).
- Model `MultiTask`: encoder NeoBERT (nạp state đã adapt nếu MLM-on) + 2 head MLP
  — `emotion_head` (phân loại) và `score_head` (sigmoid → severity 0–1), lấy
  vector `[CLS]`.
- Hàm `finetune(tag, adapted, seed)`: **discriminative LR** (head 2e-5, encoder
  1e-5); loss **masked theo task** — mẫu EMO tính cross-entropy, mẫu SEV tính
  MSE. Đánh giá: macro-F1 + ECE (calibration) cho emotion; Pearson/Spearman/MAE
  cho severity.
- `finetune("MLM-off", None, seed)` = NeoBERT gốc; `finetune("MLM-on",
  adapted_state, seed)` = bản đã adapt.

## Block s6 — chạy cả 2 nhánh × 3 seed (`s6_run_seeds.py`)
Vòng lặp qua từng seed, chạy `off` rồi `on`, in metric. **Ghi
`results_per_seed.csv` sau mỗi seed** (checkpoint tăng dần) → nếu Kaggle ngắt
giữa chừng vẫn giữ được seed đã xong.

## Block s7 — bảng kết quả (`s7_results.py`)
Tính **mean ± std** mỗi nhánh và **delta ghép cặp (on − off) theo từng seed** rồi
mean±std của delta. Đây là con số kết luận: MLM giúp hay hại từng metric, và độ
ổn định. Lưu `results_summary.csv`, in `=== RESULT: SUCCESS ===`.

## Block s8 — export model dùng được + demo inference (`s8_export_infer.py`)
Ablation ở s6 vứt bỏ mọi model; block này train **một** model để giữ lại:
- `SHIP_ARM="MLM-off"` (vanilla cho severity tốt nhất; MLM-on cho emotion-F1 tốt
  nhất → kết quả ablation cho thấy MLM **không đồng đều**: lợi emotion nhưng hại
  severity).
- Train lại trên arm đã chọn, **lưu cả model + metadata** (`pebble_model.pt`) để
  rebuild khi inference.
- `analyze(text)`: trả về severity + top-3 emotion; chạy 5 câu test mẫu để chứng
  minh model hoạt động.

---

**Tóm tắt một câu:** pipeline ablation có kiểm soát đo *lợi ích của MLM
domain-adaptation cho NeoBERT* trên 2 task (emotion + severity), 3 seed, với
dedup chống rò rỉ và fp32 chống confound; kết luận thực nghiệm (theo s8) là MLM
**giúp emotion nhưng làm giảm severity**, nên bản ship mặc định chọn `MLM-off`.
