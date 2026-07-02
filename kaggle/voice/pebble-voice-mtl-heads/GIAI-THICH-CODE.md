# Giải thích chi tiết — `pebble-voice-mtl-heads`

> Kernel Kaggle: **3 head dị chủng (heterogeneous MTL) trên một speech-encoder đông cứng**.
> Đây là phần mở rộng thesis của `pebble-emotion2vec-repro`: cùng backbone đông cứng
> (`emotion2vec_base` / `WavLM-Large`) + cùng **SUPERB trunk**, nhưng **3 head** thay vì 1 —
> emotion (8-lớp CE) · affect (valence+arousal, **CCC**) · crisis (BCE dưới **recall-floor cứng**) —
> cân bằng bằng **Kendall uncertainty weighting**.
>
> Mỗi mục: **code thật** ở trên, **giải thích** ngay dưới. Tài liệu giao thức + lý do thiết kế:
> `docs/tasks/voice-mtl-heads.md`.

---

## 0. Tổng quan kiến trúc

Pipeline một chiều, encoder **không train** (frozen), chỉ train cái "đầu" nhẹ phía trên:

```
        ┌─────────────── FROZEN (không cập nhật gradient) ───────────────┐
wav 16k │  WavLM-Large  →  frame features (T × 1024)                      │
 ~3-5s  │  emotion2vec  →  frame features (T × 768)                       │
        └────────────────────────────────────────────────────────────────┘
                                   │  (cache 1 lần cho cả 1440 clip)
                                   ▼
                    SUPERB trunk:  Linear(d, 256) → ReLU
                                   │
                          masked-mean-pool theo frame hợp lệ
                                   │   z = embedding utterance (256-d)
                  ┌────────────────┼────────────────┐
                  ▼                ▼                ▼
          emo Linear(256,8)  reg Linear(256,2)  safe Linear(256,1)
           emotion 8-lớp      valence+arousal     crisis (nhị phân)
              CE loss           CCC loss          BCE + recall-floor
                  └────────────────┼────────────────┘
                                   ▼
                  Kendall uncertainty weighting (gộp 3 loss)
```

**Điểm cốt lõi cần nhớ:**

- Backbone **đông cứng** → chỉ extract feature 1 lần, rồi train head nhẹ → rất rẻ, hợp ràng buộc "frozen-probe" của thesis.
- 3 head **dị chủng** (phân lớp + hồi quy + nhị phân an toàn) dùng chung một trunk.
- **Nhãn proxy:** RAVDESS *không có* nhãn valence/arousal liên tục hay nhãn crisis lâm sàng. Hai head mới học **nhãn giả** suy ra từ 8 cảm xúc (Russell circumplex cho V/A; tập cảm xúc high-distress cho crisis). → kernel này **validate cơ chế (mechanics)**, không phải con số khoa học thật. Số CCC/crisis có ý nghĩa cần MSP-Podcast / DAIC (task sau).

---

## 1. Cell 0 — cài stack đã ghim (`_cell_install.py`)

```python
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
get_ipython().system('pip install -q torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121')
get_ipython().system('pip install -q transformers==4.48.2 datasets==3.2.0 librosa soundfile scikit-learn scipy')
get_ipython().system('pip install -q funasr modelscope || echo "funasr install failed -> emotion2vec arm will be skipped"')
```

**Vì sao phải ghim cứng version:**

- **P100 = kiến trúc sm_60.** Torch mặc định của Kaggle (2.10) đã *bỏ* kernel cho sm_60 → crash khi chạy trên P100. Phải hạ về `torch==2.5.1` (cu121).
- **`torchvision` phải khớp `torch`.** `transformers` lazy-import torchvision; nếu lệch version sẽ lỗi `operator torchvision::nms does not exist` và **WavLM không load được**.
- **`transformers==4.48.2`** khớp config của các model.
- **`funasr`/`modelscope`** là nhánh của emotion2vec. Cài có `|| echo ...` để **nếu cài lỗi thì chỉ bỏ qua nhánh emotion2vec**, WavLM vẫn cho ra kết quả — không làm hỏng cả run.

---

## 2. Cell 1 — imports & config (`c1_imports.py`)

### Hằng số chính

```python
SR = 16000                 # mọi encoder ăn audio 16 kHz
MAX_SEC = 5.0              # clip RAVDESS ~3-5s; 5s phủ gần hết
MAX_SAMPLES = int(SR * MAX_SEC)     # 80 000 mẫu
FRAME_HOP = 320            # cả 2 encoder downsample 16kHz -> 50Hz (hệ số 320)
T_MAX = MAX_SAMPLES // FRAME_HOP    # 250 frame; feature mức-frame (T × d)

N_FOLDS = 10              # random 10-fold CV (cùng giao thức repro)
SPLIT = (0.80, 0.10, 0.10)         # train/val/test mỗi fold
BASE_SEED = 42
PROBE_EPOCHS, PROBE_LR, HEAD_DIM, WD = 100, 1e-3, 256, 1e-4
RECALL_FLOOR = 0.90       # sàn recall cứng cho crisis (cơ chế "novelty" của thesis)
```

- `FRAME_HOP = 320`: 16000 Hz / 320 = **50 frame/giây** → tính được số frame từ độ dài. `T_MAX = 250` là số frame của clip 5s.
- `PROBE_EPOCHS=100`, `PROBE_LR=1e-3`: head nhẹ, train nhanh, chọn epoch tốt nhất theo val-loss.

### Thứ tự nhãn cảm xúc RAVDESS

```python
EMOTIONS = ["neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised"]
EMO2ID = {e: i for i, e in enumerate(EMOTIONS)}
N_EMO = 8
```

Đúng thứ tự id chuẩn của RAVDESS (mã file `01..08` → `0..7`).

### Nhãn PROXY cho 2 head mới (mấu chốt cần hiểu)

```python
VALENCE_AROUSAL = {
    "neutral": (0.0, 0.0), "calm": (0.4, -0.6), "happy": (0.8, 0.5),
    "sad": (-0.6, -0.4), "angry": (-0.6, 0.8), "fearful": (-0.6, 0.6),
    "disgust": (-0.7, 0.2), "surprised": (0.3, 0.7),
}
CRISIS = {"angry", "fearful", "sad", "disgust"}
VA   = np.array([VALENCE_AROUSAL[e] for e in EMOTIONS], dtype=np.float32)   # (8, 2)
SAFE = np.array([1.0 if e in CRISIS else 0.0 for e in EMOTIONS], ...)        # (8,)
```

- **`VALENCE_AROUSAL`**: bản đồ cố định **Russell (1980) circumplex** — gán mỗi cảm xúc một điểm (valence, arousal) trong `[-1, 1]`. Đây chính là *nhãn giả* cho head affect: vì RAVDESS không có nhãn V/A liên tục, ta lấy giá trị "lý thuyết" theo cảm xúc.
- **`CRISIS`**: tập cảm xúc "high-distress" → nhãn dương của head crisis (an toàn). Cũng là proxy.
- `VA[y]` và `SAFE[y]` cho phép tra ngược: từ id cảm xúc → cặp V/A và cờ crisis.

> ⚠️ **Đây là giới hạn lớn nhất của kernel.** Hai head mới học nhãn *suy diễn máy móc từ cảm xúc*, nên gần như circular → số CCC/crisis ở đây **chỉ chứng minh cơ chế chạy đúng**, không phải bằng chứng khoa học. Đã chốt thay bằng MSP-Podcast (nhãn A/V/D thật).

---

## 3. Cell 2 — nạp RAVDESS (`c2_data.py`)

```python
ds = load_dataset("narad/ravdess", split="train", trust_remote_code=True)
INT2STR = ds.features["labels"].int2str

def fix_len(wav):
    n = min(len(wav), MAX_SAMPLES)
    flen = int(np.clip(round(n / FRAME_HOP), 1, T_MAX))   # số frame THẬT (trước pad)
    if len(wav) >= MAX_SAMPLES:
        return wav[:MAX_SAMPLES], flen
    return np.pad(wav, (0, MAX_SAMPLES - len(wav))), flen
```

- **`fix_len`** cắt/đệm mọi clip về đúng 5s (80 000 mẫu) để batch đều, **đồng thời trả `flen`** = số frame hợp lệ thật. `flen` cực kỳ quan trọng: nó là cái mask để pooling chỉ tính trên frame thật, **bỏ qua phần pad bằng 0** (nếu không, mean-pool sẽ bị kéo loãng bởi các frame zero).

```python
def to_records(ds):
    for ex in ds:
        wav = np.asarray(ex["audio"]["array"], dtype=np.float32)
        if src_sr != SR:
            wav = torchaudio.functional.resample(..., src_sr, SR).numpy()  # 48k -> 16k
        wav, flen = fix_len(wav.astype(np.float32))
        recs.append({"wav": wav, "y": EMO2ID[emo], "flen": flen})

assert len(recs) == 1440      # tất cả 1440 clip speech của RAVDESS
sf.write(f"{ART}/sample_val.wav", recs[0]["wav"], SR)   # lưu 1 clip làm sample test local
```

- RAVDESS gốc 48 kHz → **resample về 16 kHz**.
- `assert len(recs) == 1440`: chốt cứng đủ 1440 clip speech (fail nhanh nếu dataset lệch).
- Lưu 1 clip ra `sample_val.wav` để test artifact bằng `voice_mtl_infer.py` ở local.

---

## 4. Cell 3 — extract feature đông cứng mức-frame (`c3_features.py`)

Mỗi encoder chạy **một lần** trên toàn bộ 1440 clip, trả về `(N, T_MAX, dim)` feature mức-frame.
Pooling diễn ra **sau** `Linear+ReLU` ở cell 4 (đúng công thức `SuperbBaseModel` của emotion2vec/EmoBox).

```python
def pad_T(arr):                          # (T, dim) -> (T_MAX, dim)
    if len(arr) >= T_MAX: return arr[:T_MAX]
    return np.pad(arr, ((0, T_MAX - len(arr)), (0, 0)))
```

### Nhánh WavLM

```python
def wavlm_extractor():
    fe = AutoFeatureExtractor.from_pretrained("microsoft/wavlm-large")
    model = WavLMModel.from_pretrained("microsoft/wavlm-large").to(DEVICE).eval()
    @torch.no_grad()
    def extract(wavs, bs=16):
        for i in range(0, len(wavs), bs):
            enc = fe(batch, sampling_rate=SR, return_tensors="pt", padding=True)
            with torch.cuda.amp.autocast(...):
                h = model(**enc).last_hidden_state          # (B, T, 1024)
            out.append(pad_T(h[j]).astype(np.float16))      # GIỮ chiều thời gian
        return np.stack(out)                                # (N, T_MAX, 1024)
    return extract, 1024
```

- `model.eval()` + `@torch.no_grad()` → **đông cứng**, không tính gradient cho backbone.
- Lấy `last_hidden_state` (feature mức-frame), **không** mean-pool tại đây — giữ `(T, 1024)`.
- Lưu **float16** để tiết kiệm RAM (1440 × 250 × 1024).

### Nhánh emotion2vec

```python
def emotion2vec_extractor():
    from funasr import AutoModel as FunASR
    model = FunASR(model="iic/emotion2vec_base", hub="hf", disable_update=True)
    def extract(wavs, bs=None):
        for w in wavs:
            sf.write(tf.name, w, SR)                        # funasr đọc từ file
            r = model.generate(path, granularity="frame", extract_embedding=True)
            f = np.asarray(r[0]["feats"], dtype=np.float32) # (T, 768)
            feats.append(pad_T(f).astype(np.float16))
        return np.stack(feats)                              # (N, T_MAX, 768)
    return extract, 768
```

- `granularity="frame"` → feature mức-frame `(T, 768)` (khác với "utterance" trả 1 vector).
- funasr nhận đường dẫn file → phải `sf.write` ra file tạm rồi xoá.

### Vòng lặp + guard

```python
for name, builder in [("emotion2vec", ...), ("wavlm-large", ...)]:
    try:
        extract, dim = builder()
        X = extract(all_wavs)
        BACKBONES[name] = {"X": X, "dim": dim}
    except Exception as e:
        print(f"[{name}] SKIPPED -> {type(e).__name__}: {e}")
assert BACKBONES, "no backbone produced features"
```

- Bọc `try/except`: nếu emotion2vec hỏng (thiếu funasr) thì **bỏ qua nhánh đó**, WavLM vẫn chạy.
- `assert BACKBONES`: ít nhất một backbone phải ra feature, nếu không thì dừng.

---

## 5. Cell 4 — 3-head MTL probe + Kendall weighting (`c4_heads.py`) ⭐

Đây là **trái tim** của kernel. Chia nhỏ từng phần:

### 5.1 Kiến trúc head

```python
class MTLHead(nn.Module):
    def __init__(self, dim, hid=HEAD_DIM):
        self.pre  = nn.Linear(dim, hid)     # SUPERB trunk dùng chung
        self.emo  = nn.Linear(hid, N_EMO)   # emotion 8-lớp
        self.reg  = nn.Linear(hid, 2)       # affect: valence, arousal
        self.safe = nn.Linear(hid, 1)       # crisis nhị phân
    def forward(self, x, mask):             # x (B,T,dim), mask (B,T)
        h = F.relu(self.pre(x))
        m = mask.unsqueeze(-1).float()
        z = (h * m).sum(1) / m.sum(1).clamp(min=1.0)   # MASKED-mean pool
        return self.emo(z), self.reg(z), self.safe(z).squeeze(-1)
```

- **`pre`** = trunk dùng chung: `Linear(dim, 256) → ReLU`. Cả 3 head nhìn vào cùng một embedding.
- **Masked-mean-pool**: nhân feature với mask (1 cho frame thật, 0 cho pad), cộng theo thời gian, chia cho số frame thật (`clamp(min=1)` chống chia 0). → utterance embedding `z` (256-d) **không bị pad làm loãng**.
- 3 head tuyến tính riêng → 3 output: logits cảm xúc, (valence, arousal), logit crisis.

### 5.2 Kendall uncertainty weighting

```python
class UncertaintyWeighter(nn.Module):
    def __init__(self, n=3):
        self.log_var = nn.Parameter(torch.zeros(n))   # log σ² học được, 1 cho mỗi task
    def forward(self, losses):
        return sum(0.5 * torch.exp(-self.log_var[i]) * L + 0.5 * self.log_var[i]
                   for i, L in enumerate(losses))
```

Công thức **Kendall, Gal & Cipolla (CVPR 2018)** — homoscedastic uncertainty weighting:

`total = Σ_i [ ½·exp(−s_i)·L_i + ½·s_i ]`, với `s_i = log σ_i²` là tham số **học được**.

- Task khó (loss cao) → mô hình tự tăng `σ²` → `exp(−s)` nhỏ → **giảm trọng số** task đó, tránh nó lấn át.
- Số hạng `+½·s_i` là phạt regularization, chặn `σ²` phình vô hạn.
- → **không cần dò tay trọng số 3 loss**; mô hình tự cân. (Đây là comparator để sau này so với GradNorm/PCGrad trong bảng ablation.)

### 5.3 CCC — loss & metric cho affect

```python
def ccc_loss(pred, tgt):
    pm, tm = pred.mean(), tgt.mean()
    pv, tv = pred.var(unbiased=False), tgt.var(unbiased=False)
    cov = ((pred - pm) * (tgt - tm)).mean()
    return 1 - 2 * cov / (pv + tv + (pm - tm) ** 2 + 1e-8)

def ccc_score(pred, tgt):   # giống trên nhưng trả CCC (không phải 1-CCC)
    return float(2 * cov / (pred.var() + tgt.var() + (pm - tm) ** 2 + 1e-8))
```

- **CCC (Concordance Correlation Coefficient)** ∈ `[-1, 1]`: đo vừa **tương quan** vừa **khớp tuyệt đối** (khác Pearson — phạt cả lệch mean/scale). Là metric chuẩn cho affect liên tục (AVEC).
- **Loss = `1 − CCC`** → minimize loss = maximize CCC.
- Áp **riêng cho valence và arousal** rồi cộng lại (xem 5.6).

### 5.4 Recall-floor: chọn ngưỡng đảm bảo recall ≥ sàn

```python
def threshold_for_recall(probs, labels, floor):
    pos = np.sort(probs[labels == 1])            # prob của các mẫu crisis thật, tăng dần
    if len(pos) == 0: return 0.5
    k = min(int(np.floor((1 - floor) * len(pos))), len(pos) - 1)
    return float(pos[k])                          # ngưỡng cao nhất mà recall >= floor
```

**Cơ chế an toàn cứng** — logic:

- Muốn `recall ≥ 0.90` nghĩa là **bắt được ≥ 90% mẫu crisis thật**.
- Sắp prob của các mẫu crisis tăng dần. Nếu đặt ngưỡng tại phân vị `(1−floor)` từ dưới lên, ta "thả" nhiều nhất `10%` mẫu crisis có prob thấp nhất → recall vẫn ≥ 90%.
- Lấy **ngưỡng cao nhất** thoả điều kiện → recall vừa đủ sàn nhưng **precision tốt nhất có thể**.
- Ngưỡng được dò **trên tập val**, rồi áp lên test (không peek test).

### 5.5 Chia fold

```python
def split_80_10_10(y, seed):
    tr, tmp = train_test_split(idx, test_size=0.20, random_state=seed, stratify=y)
    va, te  = train_test_split(tmp, test_size=0.5, random_state=seed, stratify=y[tmp])
    return tr, va, te
```

- **Stratify theo cảm xúc** → mỗi split giữ nguyên tỉ lệ 8 lớp.
- Mỗi fold dùng `seed = BASE_SEED + fold` → 10 fold = 10 cách chia ngẫu nhiên khác nhau.

### 5.6 `train_one` — train 1 fold

```python
def train_one(Xg, mask_g, y, va_tgt, safe_tgt, dim, seed):
    tr, va, te = split_80_10_10(y, seed)
    head = MTLHead(dim).to(DEVICE)
    weighter = UncertaintyWeighter(3).to(DEVICE)
    opt = torch.optim.Adam(list(head.parameters()) + list(weighter.parameters()), lr=PROBE_LR, weight_decay=WD)

    best_val, best_state = 1e9, None
    for _ in range(PROBE_EPOCHS):
        # --- train (full-batch trên tập train) ---
        e, r, s = head(Xg[tr_t], mask_g[tr_t])
        losses = [F.cross_entropy(e, yt[tr_t]),                                  # emotion
                  ccc_loss(r[:,0], vt[tr_t,0]) + ccc_loss(r[:,1], vt[tr_t,1]),   # affect = CCC(V)+CCC(A)
                  F.binary_cross_entropy_with_logits(s, st[tr_t])]               # crisis
        loss = weighter(losses)               # Kendall gộp 3
        loss.backward(); opt.step()
        # --- val: chọn epoch tốt nhất theo TỔNG loss (không trọng số) ---
        vl = (CE + CCC_v + CCC_a + BCE) on val
        if vl < best_val: best_state = head.state_dict() copy
    head.load_state_dict(best_state)          # early-stop "mềm": lấy state val tốt nhất
```

- **Optimizer train cả `head` lẫn `weighter`** (vì `log_var` là Parameter học được).
- Train **full-batch** (cả tập train một lần/epoch) — rẻ vì feature đã cache, head nhẹ.
- 3 loss: **CE** (emotion) · **CCC(valence)+CCC(arousal)** (affect) · **BCE** (crisis) → gộp bằng Kendall.
- **Model selection**: lưu lại state có **tổng val-loss thấp nhất** (early-stop mềm), tránh overfit.

```python
    # đánh giá trên test, áp recall-floor đã dò trên val
    tau = threshold_for_recall(sigmoid(sv_val), safe_tgt[va], RECALL_FLOOR)
    pred = (sigmoid(st_test) >= tau).astype(int)
    m = emo_metrics(y[te], et.argmax(-1))     # WA / UA / WF1
    m.update({"CCC_v": ..., "CCC_a": ...,
              "crisis_recall": recall_score(...), "crisis_prec": precision_score(...),
              "tau": tau})
    return m, head
```

- `emo_metrics`: **WA** (weighted acc), **UA** (unweighted/macro recall), **WF1** (weighted F1) — bộ 3 chuẩn SER.
- Crisis: dò `tau` trên **val**, áp lên **test** → báo recall & precision tại sàn.

### 5.7 Vòng CV ngoài

```python
mask_all = (torch.arange(T_MAX)[None,:] < torch.tensor(flen_all)[:,None])   # (N,T) mask từ flen
va_all   = VA[y_all]      # (N,2) nhãn proxy V/A
safe_all = SAFE[y_all]    # (N,)  nhãn proxy crisis

for name, b in BACKBONES.items():
    Xg = torch.tensor(b["X"], dtype=torch.float, device=DEVICE)   # f16 -> f32 trên GPU
    for fold in range(N_FOLDS):
        m, head = train_one(Xg, mask_all, y_all, va_all, safe_all, b["dim"], BASE_SEED+fold)
        results[name].append(m)
        if fold == 0: artifacts[name] = head     # giữ head fold-0 làm artifact
    # in mean ± std qua 10 fold
```

- **`mask_all`**: dựng từ `flen` — `frame_index < flen` → True. Đây là mask cho masked-mean-pool.
- Feature `f16` được nạp lên GPU và cast `f32` cho ổn định số học.
- Mỗi backbone × 10 fold → list metric; **giữ head của fold 0** làm artifact để export/serve.

---

## 6. Cell 5 — tổng hợp + lưu artifact (`c5_results.py`)

```python
for name, folds in results.items():
    for k in ("WA","UA","WF1","CCC_v","CCC_a","crisis_recall","crisis_prec"):
        vals = np.array([f[k] for f in folds])
        agg[name][k] = (vals.mean(), vals.std())
df.to_csv(f"{ART}/results_voice_mtl.csv")

for name, head in artifacts.items():       # 1 bundle / backbone (head fold-0)
    torch.save(head.state_dict(), f"{d}/mtl_head.pt")
    cfg = {"backbone_hf_id":..., "embed_dim":..., "emotions":..., "valence_arousal":...,
           "crisis_set":..., "recall_floor":..., "crisis_tau": results[name][0]["tau"],
           "frame_hop":..., "t_max":..., "pooling":"masked-mean", "head":"mtl-3head", ...}
    json.dump(cfg, f"{d}/config.json")
```

- Tổng hợp **mean ± std** qua 10 fold cho cả 7 metric → CSV + JSON.
- Mỗi backbone lưu một **bundle phục vụ/test**: `mtl_head.pt` (trọng số head) + `config.json` (đủ siêu dữ liệu để tái dựng pipeline: backbone id, dim, bản đồ V/A, tập crisis, **`crisis_tau`** đã dò, cách pool...).
- `crisis_tau` lưu lại để inference local áp đúng ngưỡng recall-floor đã chọn.

**Output trong `/kaggle/working`:** `results_voice_mtl.{csv,json}`, `sample_val.wav`, `artifact_*/` (`mtl_head.pt` + `config.json`).

---

## 7. Inference local — `scripts/voice_mtl_infer.py`

Test artifact đã pull về trên **1 clip**, không qua Kaggle:

```python
class MTLHead(nn.Module):        # bản rút gọn: 1 clip -> mọi frame hợp lệ -> mean-pool thường
    def forward(self, x):
        z = F.relu(self.pre(x)).mean(1)   # không cần mask vì input không pad
        return self.emo(z), self.reg(z), self.safe(z).squeeze(-1)

cfg = json.load(bundle/"config.json")
X = feat_wavlm(wav, cfg["backbone_hf_id"]) hoặc feat_emotion2vec(...)
head.load_state_dict(torch.load(bundle/"mtl_head.pt"))
emo_logits, reg, safe_logit = head(X)
crisis_p = sigmoid(safe_logit);  tau = cfg["crisis_tau"]
print emotion top-3, valence/arousal, "CRISIS" nếu crisis_p >= tau
```

- **Vì sao bỏ mask:** một clip đưa vào *không pad* → mọi frame đều hợp lệ → masked-mean rút gọn thành mean thường. Tái dựng đúng đường c3→c4 của kernel.
- In ra: cảm xúc (top-3), affect (valence/arousal proxy), và cờ **CRISIS** nếu `p ≥ tau` (ngưỡng recall-floor lưu trong config).
- WavLM chạy chỉ với `transformers`; emotion2vec cần `funasr` cài local.

---

## 8. Tóm tắt & cách chạy

### Bản chất khoa học

| Thành phần | Trạng thái | Ghi chú |
|---|---|---|
| Frozen probe + SUPERB trunk | ✅ thật | tái dùng từ repro |
| 3 head dị chủng + Kendall weighting | ✅ cơ chế đúng | validate được trên feature thật |
| Emotion 8-lớp (CE → WA/UA/WF1) | ✅ thật | nhãn RAVDESS thật |
| **Affect CCC (valence/arousal)** | ⚠️ **proxy** | nhãn Russell cố định → chưa meaningful; cần MSP-Podcast |
| **Crisis recall-floor** | ⚠️ **proxy** | nhãn = tập cảm xúc high-distress; cần nhãn lâm sàng (DAIC) |

> Kernel này **chứng minh cơ chế multi-head + recall-floor chạy đúng trên feature đông cứng thật**.
> Con số CCC / crisis chỉ có ý nghĩa khoa học khi thay nhãn proxy bằng nhãn liên tục + lâm sàng thật.

### Build + chạy

```bash
# build notebook từ các cell .py
.venv-voice/Scripts/python.exe kaggle/voice/pebble-voice-mtl-heads/build_ipynb.py

# push + chạy trên Kaggle GPU
.venv-voice/bin/kaggle kernels push   -p kaggle/voice/pebble-voice-mtl-heads
.venv-voice/bin/kaggle kernels status fabiocarava/pebble-voice-mtl-heads      # poll tới khi xong
.venv-voice/bin/kaggle kernels output fabiocarava/pebble-voice-mtl-heads -p kaggle/voice/pebble-voice-mtl-heads/out

# test artifact local trên 1 clip
PYTHONPATH=src .venv-voice/bin/python scripts/voice_mtl_infer.py \
  kaggle/voice/pebble-voice-mtl-heads/out/artifact_wavlm-large \
  kaggle/voice/pebble-voice-mtl-heads/out/sample_val.wav
```

**Trạng thái hiện tại:** kernel đã build xong, **chưa chạy Kaggle** (chưa có `out/`) → đây là việc kế tiếp (mốc M3–M5).
