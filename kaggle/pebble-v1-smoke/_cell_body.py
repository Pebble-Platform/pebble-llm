# Cell 2 — Pebble v1 "short" experiment: demonstrates the high-leverage items of
# docs/improvement-plan-from-deep-read.md on a NeoBERT P100 smoke run.
#   * metrics gap (plan section 4): pearson / spearman / QWK / ECE
#   * MTL loss arms (plan section 1.1): static-lambda -> uniform-sum -> Kendall-UW(+floor)
#   * fine-tuning recipe (plan section 1.2): gradual-unfreeze + discriminative-LR + STLR
#                                            vs the current static-freeze baseline
import os, re, math, random, warnings, urllib.request
warnings.filterwarnings("ignore")
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset as TorchDataset
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import f1_score
from transformers import AutoModel, AutoTokenizer

print("torch", torch.__version__, "| cuda", torch.cuda.is_available(),
      "|", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu")

SEED = 42
def set_seed(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)
set_seed(SEED)

DEVICE   = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL    = "chandar-lab/NeoBERT"
REVISION = "5424c8efeea6491b151d62dee55a752165407430"   # pinned, src/.../config.py
MAX_LEN, BATCH, EPOCHS = 64, 32, 3
N_TRAIN, N_VAL = 2400, 600
EMOTIONS = ["anger", "fear", "joy", "sadness"]
EMO2ID   = {e: i for i, e in enumerate(EMOTIONS)}
NEG      = {"anger", "fear", "sadness"}

# ----------------------------------------------------------------------------- data
# SemEval-2018 EI-reg (same source as src/pebble_llm/data/external.py): one dataset
# with BOTH a 4-class emotion label and a severity in [0,1] -> a clean MSE+CE pair.
BASE = "https://raw.githubusercontent.com/cbaziotis/ntua-slp-semeval2018/master/datasets/task1/EI-reg"
def fetch_eireg(file_split):
    rows = []
    for emo in EMOTIONS:
        url = f"{BASE}/EI-reg-En-{emo}-{file_split}.txt"
        try:
            raw = urllib.request.urlopen(url, timeout=40).read().decode("utf-8")
        except Exception as e:
            print("download failed:", url, "->", e); return None
        for ln in raw.splitlines()[1:]:
            c = ln.split("\t")
            if len(c) < 4: continue
            try: inten = float(c[3])
            except ValueError: continue
            rows.append({"text": c[1], "emotion": EMO2ID[emo],
                         "severity": inten if emo in NEG else 0.0})
    return rows

train_rows, val_rows = fetch_eireg("train"), fetch_eireg("dev")
if not train_rows or not val_rows:                       # unattended-safe fallback
    print("!! using synthetic fallback dataset")
    def synth(n):
        r = []
        for i in range(n):
            e = random.randrange(4)
            sev = 0.0 if EMOTIONS[e] == "joy" else random.random()
            r.append({"text": f"i feel {EMOTIONS[e]} today sample {i} level {sev:.2f}",
                      "emotion": e, "severity": sev})
        return r
    train_rows, val_rows = synth(N_TRAIN), synth(N_VAL)

random.shuffle(train_rows); random.shuffle(val_rows)
train_rows, val_rows = train_rows[:N_TRAIN], val_rows[:N_VAL]
print(f"train={len(train_rows)}  val={len(val_rows)}")

tok = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, trust_remote_code=True)

class MTDataset(TorchDataset):
    def __init__(self, rows):
        enc = tok([r["text"] for r in rows], truncation=True, max_length=MAX_LEN,
                  padding="max_length", return_tensors="pt")
        self.ids, self.attn = enc["input_ids"], enc["attention_mask"]
        self.emo = torch.tensor([r["emotion"] for r in rows], dtype=torch.long)
        self.sev = torch.tensor([r["severity"] for r in rows], dtype=torch.float)
    def __len__(self): return len(self.emo)
    def __getitem__(self, i): return self.ids[i], self.attn[i], self.emo[i], self.sev[i]

train_loader = DataLoader(MTDataset(train_rows), batch_size=BATCH, shuffle=True)
val_loader   = DataLoader(MTDataset(val_rows),   batch_size=BATCH)

# --------------------------------------------------------------------------- metrics
# These four are exactly what plan section 4 asks to add to evaluation/metrics.py.
def mae(p, t): return float(np.mean(np.abs(p - t)))
def pearson(p, t):
    return 0.0 if np.std(p) < 1e-8 or np.std(t) < 1e-8 else float(pearsonr(p, t)[0])
def spearman(p, t):
    return 0.0 if np.std(p) < 1e-8 or np.std(t) < 1e-8 else float(spearmanr(p, t)[0])
def macro_f1(pp, tt): return float(f1_score(tt, pp, average="macro"))
def band3(x): return np.minimum((np.asarray(x) * 3).astype(int), 2)   # 3 ordinal severity bands
def quadratic_weighted_kappa(a, b, n=3):
    a, b = np.asarray(a), np.asarray(b)
    O = np.zeros((n, n))
    for x, y in zip(a, b): O[x, y] += 1
    w = np.array([[((i - j) ** 2) / ((n - 1) ** 2) for j in range(n)] for i in range(n)])
    E = np.outer(O.sum(1), O.sum(0)) / max(O.sum(), 1)
    den = (w * E).sum()
    return float(1 - (w * O).sum() / den) if den > 0 else 0.0
def expected_calibration_error(probs, correct, n_bins=10):
    conf = probs.max(axis=1); bins = np.linspace(0, 1, n_bins + 1); ece = 0.0; N = len(conf)
    for i in range(n_bins):
        m = (conf > bins[i]) & (conf <= bins[i + 1])
        if m.sum() == 0: continue
        ece += (m.sum() / N) * abs(correct[m].mean() - conf[m].mean())
    return float(ece)

# ----------------------------------------------------------------------------- model
class ScoreHead(nn.Module):     # mirrors src/pebble_llm/models/heads.py
    def __init__(s, h, d=256, p=0.1):
        super().__init__()
        s.net = nn.Sequential(nn.Dropout(p), nn.Linear(h, d), nn.GELU(),
                              nn.Dropout(p), nn.Linear(d, 1))
    def forward(s, x): return torch.sigmoid(s.net(x)).squeeze(-1)
class EmotionHead(nn.Module):
    def __init__(s, h, n, d=256, p=0.1):
        super().__init__()
        s.net = nn.Sequential(nn.Dropout(p), nn.Linear(h, d), nn.GELU(),
                              nn.Dropout(p), nn.Linear(d, n))
    def forward(s, x): return s.net(x)
class MultiTask(nn.Module):     # v1 scope: only emotion + severity heads (no safety head)
    def __init__(s):
        super().__init__()
        s.encoder = AutoModel.from_pretrained(MODEL, revision=REVISION, trust_remote_code=True)
        h = getattr(s.encoder.config, "hidden_size", 768)
        s.score_head, s.emotion_head = ScoreHead(h), EmotionHead(h, len(EMOTIONS))
    def forward(s, ids, attn):
        cls = s.encoder(input_ids=ids, attention_mask=attn).last_hidden_state[:, 0, :]
        return s.score_head(cls), s.emotion_head(cls)

# ------------------------------------------------------------------------- MTL losses
class MTLoss(nn.Module):
    """static  : w_score*MSE + w_emo*CE   (covers static-lambda and uniform-sum)
       kendall : Kendall uncertainty weighting  exp(-s)*L + s/2  per task.
                 floor_score clamps the severity log-var so UW cannot down-weight it
                 (the safety-weight-floor mechanism of plan 1.1, applied to severity)."""
    def __init__(s, mode, w_score=1.0, w_emo=1.0, floor_score=None):
        super().__init__()
        s.mode, s.w_score, s.w_emo, s.floor_score = mode, w_score, w_emo, floor_score
        s.mse, s.ce = nn.MSELoss(), nn.CrossEntropyLoss()
        if mode == "kendall":
            s.log_var_score = nn.Parameter(torch.zeros(()))
            s.log_var_emo   = nn.Parameter(torch.zeros(()))
    def forward(s, sp, sev, el, emo):
        ls, le = s.mse(sp, sev), s.ce(el, emo)
        if s.mode == "kendall":
            svar = s.log_var_score
            if s.floor_score is not None:
                svar = torch.clamp(svar, max=s.floor_score)   # weight >= exp(-floor)
            total = (torch.exp(-svar) * ls + 0.5 * svar
                     + torch.exp(-s.log_var_emo) * le + 0.5 * s.log_var_emo)
        else:
            total = s.w_score * ls + s.w_emo * le
        return total, ls.item(), le.item()

# ----------------------------------------------------------------- recipe (plan 1.2)
def _layer_idx(name):
    for part in name.split("."):
        if part.isdigit(): return int(part)
    return 0
def _max_layer(model):
    return max(_layer_idx(n) for n, _ in model.encoder.named_parameters())
def set_min_trainable(model, min_layer):           # gradual unfreeze
    for n, p in model.encoder.named_parameters():
        p.requires_grad = _layer_idx(n) >= min_layer
def build_optimizer(model, loss_fn, recipe, base_lr=2e-5, enc_lr=1e-5, decay=2.6):
    head = [p for n, p in model.named_parameters() if not n.startswith("encoder.")]
    groups = [{"params": head + list(loss_fn.parameters()), "lr": base_lr}]
    if recipe == "discriminative":                 # per-layer LR decay from the top
        ml = _max_layer(model); buckets = {}
        for n, p in model.encoder.named_parameters():
            buckets.setdefault(_layer_idx(n), []).append(p)
        for li, ps in buckets.items():
            groups.append({"params": ps, "lr": enc_lr / (decay ** (ml - li))})
    else:
        groups.append({"params": list(model.encoder.parameters()), "lr": enc_lr})
    return torch.optim.AdamW(groups, weight_decay=0.01)
def stlr(opt, total, cut_frac=0.1, ratio=32):      # slanted triangular LR (ULMFiT)
    cut = max(int(total * cut_frac), 1)
    def fn(step):
        p = step / cut if step < cut else 1 - (step - cut) / max(total - cut, 1)
        return (1 + p * (ratio - 1)) / ratio
    return torch.optim.lr_scheduler.LambdaLR(opt, fn)

# --------------------------------------------------------------------------- one arm
def run_arm(name, loss_mode, recipe, w_score=1.0, w_emo=1.0, floor=None):
    set_seed(SEED)
    model   = MultiTask().to(DEVICE)
    loss_fn = MTLoss(loss_mode, w_score, w_emo, floor).to(DEVICE)
    opt     = build_optimizer(model, loss_fn, recipe)
    sched   = stlr(opt, EPOCHS * len(train_loader)) if recipe == "discriminative" else None
    scaler  = torch.cuda.amp.GradScaler()
    ml      = _max_layer(model)
    for ep in range(EPOCHS):
        if recipe == "discriminative":                       # gradual unfreeze
            chunk = math.ceil((ml + 1) / EPOCHS)
            set_min_trainable(model, max(0, ml + 1 - (ep + 1) * chunk))
        else:                                                # static freeze -> unfreeze
            for p in model.encoder.parameters(): p.requires_grad = ep >= 1
        model.train()
        for ids, attn, emo, sev in train_loader:
            ids, attn, emo, sev = ids.to(DEVICE), attn.to(DEVICE), emo.to(DEVICE), sev.to(DEVICE)
            opt.zero_grad()
            with torch.cuda.amp.autocast():
                sp, el = model(ids, attn)
                loss, _, _ = loss_fn(sp, sev, el, emo)
            scaler.scale(loss).backward(); scaler.step(opt); scaler.update()
            if sched: sched.step()
    # eval
    model.eval(); P, S, EL, EM = [], [], [], []
    with torch.no_grad():
        for ids, attn, emo, sev in val_loader:
            with torch.cuda.amp.autocast():
                sp, el = model(ids.to(DEVICE), attn.to(DEVICE))
            P.append(sp.float().cpu().numpy()); S.append(sev.numpy())
            EL.append(torch.softmax(el.float(), -1).cpu().numpy()); EM.append(emo.numpy())
    P, S = np.concatenate(P), np.concatenate(S)
    EL, EM = np.concatenate(EL), np.concatenate(EM)
    pe = EL.argmax(1)
    res = {"arm": name, "loss": loss_mode, "recipe": recipe,
           "sev_pearson":  round(pearson(P, S), 4),
           "sev_spearman": round(spearman(P, S), 4),
           "sev_mae":      round(mae(P, S), 4),
           "sev_qwk":      round(quadratic_weighted_kappa(band3(P), band3(S)), 4),
           "emo_macroF1":  round(macro_f1(pe, EM), 4),
           "emo_ece":      round(expected_calibration_error(EL, (pe == EM).astype(float)), 4)}
    print("  ->", res)
    del model, loss_fn, opt; torch.cuda.empty_cache()
    return res

# ----------------------------------------------------------------------------- grid
results = []
print("\n[1/4] static-lambda(5,1) + discriminative recipe");      results.append(run_arm("static-lambda(5,1)", "static", "discriminative", w_score=5.0))
print("[2/4] uniform-sum(1,1) + discriminative recipe");          results.append(run_arm("uniform-sum(1,1)",  "static", "discriminative"))
print("[3/4] Kendall-UW(floor=2.0) + discriminative recipe");     results.append(run_arm("kendall-UW(floor)", "kendall", "discriminative", floor=2.0))
print("[4/4] uniform-sum + static-freeze baseline (current)");    results.append(run_arm("uniform+static-freeze", "static", "static_freeze"))

import pandas as pd
df = pd.DataFrame(results)
df.to_csv("/kaggle/working/results.csv", index=False)
print("\n================= RESULTS =================")
print(df.to_string(index=False))
print("\nsaved -> /kaggle/working/results.csv")
print("=== RESULT: SUCCESS ===")
