# Scaled MLM isolation ablation: adapt encoder ONCE (bigger budget), then fine-tune
# BOTH arms across 3 seeds -> mean +/- std + paired per-seed delta (the real verdict).
import os, random, warnings, urllib.request
warnings.filterwarnings("ignore")
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset as TorchDataset
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import f1_score
from datasets import load_dataset
from transformers import AutoModel, AutoModelForMaskedLM, AutoTokenizer

print("torch", torch.__version__, "| cuda", torch.cuda.is_available(),
      "|", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu")

def set_seed(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)

DEVICE   = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL    = "chandar-lab/NeoBERT"
REVISION = "5424c8efeea6491b151d62dee55a752165407430"
MAX_LEN, BATCH = 64, 32
MLM_EPOCHS, MLM_MASK_PROB, MLM_CORPUS_CAP = 3, 0.30, 25000   # bigger MLM budget
FT_EPOCHS, FT_PER_POOL = 3, 2500
EMO_VAL_N, SEV_VAL_N = 1000, 600
SEEDS = [13, 42, 1337]                                       # matches config.py
EIREG_NEG = {"anger", "fear", "sadness"}
EIREG_EMOS = ["anger", "fear", "joy", "sadness"]
ART = "/kaggle/working"
set_seed(SEEDS[0])

# ----------------------------------------------------------------- data
tok = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, trust_remote_code=True)
VOCAB = tok.vocab_size
def eireg(file_split):
    base = "https://raw.githubusercontent.com/cbaziotis/ntua-slp-semeval2018/master/datasets/task1/EI-reg"
    rows = []
    for emo in EIREG_EMOS:
        url = f"{base}/EI-reg-En-{emo}-{file_split}.txt"
        try:
            raw = urllib.request.urlopen(url, timeout=40).read().decode("utf-8")
        except Exception as e:
            print("eireg download failed:", url, e); return None
        for ln in raw.splitlines()[1:]:
            c = ln.split("\t")
            if len(c) < 4: continue
            try: inten = float(c[3])
            except ValueError: continue
            rows.append({"text": c[1], "severity": inten if emo in EIREG_NEG else 0.0})
    return rows
go_train = load_dataset("go_emotions", "simplified", split="train")
go_val   = load_dataset("go_emotions", "simplified", split="validation")
EMO_NAMES = go_train.features["labels"].feature.names
NEUTRAL = EMO_NAMES.index("neutral"); N_EMO = len(EMO_NAMES)
def go_rows(ds):
    return [{"text": r["text"], "emotion": (r["labels"][0] if r["labels"] else NEUTRAL)} for r in ds]
go_tr, go_va = go_rows(go_train), go_rows(go_val)
ei_tr, ei_va = eireg("train"), eireg("dev")
if not ei_tr or not ei_va:
    print("!! eireg unavailable -> synthetic fallback")
    rnd = lambda: random.random()
    ei_tr = [{"text": f"distress sample {i} {rnd():.2f}", "severity": rnd()} for i in range(4000)]
    ei_va = [{"text": f"tough day {i} {rnd():.2f}", "severity": rnd()} for i in range(600)]
print(f"GoEmotions train={len(go_tr)} val={len(go_va)} ({N_EMO} classes) | EI-reg train={len(ei_tr)} dev={len(ei_va)}")
def encode(texts):
    e = tok(texts, truncation=True, max_length=MAX_LEN, padding="max_length", return_tensors="pt")
    return e["input_ids"], e["attention_mask"]

# ============================================================ STAGE 1: MLM (once)
corpus = [r["text"] for r in go_tr] + [r["text"] for r in ei_tr]
random.shuffle(corpus); corpus = corpus[:MLM_CORPUS_CAP]
mlm_ids, mlm_attn = encode(corpus)
print(f"\n[MLM] corpus={len(corpus)} texts, 30% masking, {MLM_EPOCHS} epochs")
SPECIAL = torch.tensor(tok.all_special_ids)
def mask_batch(ids):
    ids = ids.clone(); labels = ids.clone()
    keep = torch.isin(ids, SPECIAL)
    prob = torch.full(ids.shape, MLM_MASK_PROB); prob[keep] = 0.0
    sel = torch.bernoulli(prob).bool(); labels[~sel] = -100
    r = torch.rand(ids.shape)
    ids[sel & (r < 0.8)] = tok.mask_token_id
    rp = sel & (r >= 0.8) & (r < 0.9); ids[rp] = torch.randint(VOCAB, ids.shape)[rp]
    return ids, labels
mlm = AutoModelForMaskedLM.from_pretrained(MODEL, revision=REVISION, trust_remote_code=True).to(DEVICE)
enc_ref = mlm.model
opt = torch.optim.AdamW(mlm.parameters(), lr=5e-5, weight_decay=0.01)
scaler = torch.cuda.amp.GradScaler(); order = list(range(len(corpus))); mlm.train()
for ep in range(MLM_EPOCHS):
    random.shuffle(order); tot = 0.0; nb = 0
    for i in range(0, len(order), BATCH):
        idx = order[i:i + BATCH]
        ids, labels = mask_batch(mlm_ids[idx])
        ids, labels, attn = ids.to(DEVICE), labels.to(DEVICE), mlm_attn[idx].to(DEVICE)
        opt.zero_grad()
        with torch.cuda.amp.autocast():
            logits = mlm(input_ids=ids, attention_mask=attn).logits
            loss = F.cross_entropy(logits.view(-1, VOCAB), labels.view(-1), ignore_index=-100)
        scaler.scale(loss).backward(); scaler.step(opt); scaler.update()
        tot += loss.item(); nb += 1
    print(f"  [MLM] epoch {ep+1}/{MLM_EPOCHS}  loss={tot/nb:.4f}")
adapted_state = {k: v.detach().half().cpu() for k, v in enc_ref.state_dict().items()}
torch.save(adapted_state, f"{ART}/mlm_encoder.pt")
print(f"[MLM] saved adapted encoder -> {ART}/mlm_encoder.pt ({len(adapted_state)} tensors, fp16)")
del mlm, enc_ref, opt; torch.cuda.empty_cache()

# ====================================== STAGE 2: masked two-pool fine-tune (x seeds)
EMO, SEV = 0, 1
recs  = [{"text": r["text"], "task": EMO, "emo": r["emotion"], "sev": 0.0} for r in go_tr[:FT_PER_POOL]]
recs += [{"text": r["text"], "task": SEV, "emo": -1, "sev": r["severity"]} for r in ei_tr[:FT_PER_POOL]]
class FTDataset(TorchDataset):
    def __init__(self, rs):
        self.ids, self.attn = encode([r["text"] for r in rs])
        self.task = torch.tensor([r["task"] for r in rs])
        self.emo  = torch.tensor([r["emo"] for r in rs], dtype=torch.long)
        self.sev  = torch.tensor([r["sev"] for r in rs], dtype=torch.float)
    def __len__(self): return len(self.task)
    def __getitem__(self, i): return self.ids[i], self.attn[i], self.task[i], self.emo[i], self.sev[i]
ft_ds = FTDataset(recs)
emo_val_ids, emo_val_attn = encode([r["text"] for r in go_va[:EMO_VAL_N]])
emo_val_y = np.array([r["emotion"] for r in go_va[:EMO_VAL_N]])
sev_val_ids, sev_val_attn = encode([r["text"] for r in ei_va[:SEV_VAL_N]])
sev_val_y = np.array([r["severity"] for r in ei_va[:SEV_VAL_N]], dtype=float)

class Head(nn.Module):
    def __init__(s, h, out, d=256, p=0.1):
        super().__init__()
        s.net = nn.Sequential(nn.Dropout(p), nn.Linear(h, d), nn.GELU(), nn.Dropout(p), nn.Linear(d, out))
    def forward(s, x): return s.net(x)
class MultiTask(nn.Module):
    def __init__(s, adapted=None):
        super().__init__()
        s.encoder = AutoModel.from_pretrained(MODEL, revision=REVISION, trust_remote_code=True)
        if adapted is not None: s.encoder.load_state_dict({k: v.float() for k, v in adapted.items()})
        h = getattr(s.encoder.config, "hidden_size", 768)
        s.emotion_head, s.score_head = Head(h, N_EMO), Head(h, 1)
    def forward(s, ids, attn):
        cls = s.encoder(input_ids=ids, attention_mask=attn).last_hidden_state[:, 0, :]
        return s.emotion_head(cls), torch.sigmoid(s.score_head(cls)).squeeze(-1)
def pearson(p, t):  return 0.0 if np.std(p) < 1e-8 or np.std(t) < 1e-8 else float(pearsonr(p, t)[0])
def spearman(p, t): return 0.0 if np.std(p) < 1e-8 or np.std(t) < 1e-8 else float(spearmanr(p, t)[0])
def ece(probs, correct, n=10):
    conf = probs.max(1); b = np.linspace(0, 1, n + 1); e = 0.0; N = len(conf)
    for i in range(n):
        m = (conf > b[i]) & (conf <= b[i + 1])
        if m.sum(): e += m.sum() / N * abs(correct[m].mean() - conf[m].mean())
    return float(e)
@torch.no_grad()
def predict(model, ids, attn):
    model.eval(); oe, os_ = [], []
    for i in range(0, len(ids), BATCH):
        with torch.cuda.amp.autocast():
            el, sp = model(ids[i:i+BATCH].to(DEVICE), attn[i:i+BATCH].to(DEVICE))
        oe.append(torch.softmax(el.float(), -1).cpu().numpy()); os_.append(sp.float().cpu().numpy())
    return np.concatenate(oe), np.concatenate(os_)
def finetune(tag, adapted, seed):
    set_seed(seed)
    loader = DataLoader(ft_ds, batch_size=BATCH, shuffle=True)
    model = MultiTask(adapted).to(DEVICE)
    opt = torch.optim.AdamW([
        {"params": [p for n, p in model.named_parameters() if not n.startswith("encoder.")], "lr": 2e-5},
        {"params": model.encoder.parameters(), "lr": 1e-5}], weight_decay=0.01)
    scaler = torch.cuda.amp.GradScaler()
    for ep in range(FT_EPOCHS):
        model.train()
        for ids, attn, task, emo, sev in loader:
            ids, attn, task = ids.to(DEVICE), attn.to(DEVICE), task.to(DEVICE)
            emo, sev = emo.to(DEVICE), sev.to(DEVICE)
            me, ms = task == EMO, task == SEV
            opt.zero_grad()
            with torch.cuda.amp.autocast():
                el, sp = model(ids, attn)
                loss = el.sum() * 0.0
                if me.any(): loss = loss + F.cross_entropy(el[me], emo[me])
                if ms.any(): loss = loss + F.mse_loss(sp[ms], sev[ms])
            scaler.scale(loss).backward(); scaler.step(opt); scaler.update()
    ep_probs, _ = predict(model, emo_val_ids, emo_val_attn)
    _, sv_pred  = predict(model, sev_val_ids, sev_val_attn)
    pe = ep_probs.argmax(1)
    res = {"arm": tag, "seed": seed,
           "emo_macroF1": float(f1_score(emo_val_y, pe, average="macro")),
           "emo_ece":     ece(ep_probs, (pe == emo_val_y).astype(float)),
           "sev_pearson": pearson(sv_pred, sev_val_y),
           "sev_spearman":spearman(sv_pred, sev_val_y),
           "sev_mae":     float(np.mean(np.abs(sv_pred - sev_val_y)))}
    del model, opt; torch.cuda.empty_cache()
    return res

METRICS = ["emo_macroF1", "emo_ece", "sev_pearson", "sev_spearman", "sev_mae"]
rows = []
for seed in SEEDS:
    print(f"\n=== seed {seed} ===")
    off = finetune("MLM-off", None, seed); print("  off:", {k: round(off[k],4) for k in METRICS})
    on  = finetune("MLM-on", adapted_state, seed); print("  on :", {k: round(on[k],4) for k in METRICS})
    rows += [off, on]

import pandas as pd
df = pd.DataFrame(rows)
df.to_csv(f"{ART}/results_per_seed.csv", index=False)
# mean +/- std per arm
summary = []
for arm in ["MLM-off", "MLM-on"]:
    sub = df[df.arm == arm]
    summary.append({"arm": arm, **{m: f"{sub[m].mean():.4f}+/-{sub[m].std():.4f}" for m in METRICS}})
# paired per-seed delta (on - off), reported mean +/- std
piv = df.pivot(index="seed", columns="arm")
delta = {"arm": "delta (on-off) mean+/-std"}
for m in METRICS:
    d = piv[(m, "MLM-on")] - piv[(m, "MLM-off")]
    delta[m] = f"{d.mean():+.4f}+/-{d.std():.4f}"
sdf = pd.DataFrame(summary + [delta])
sdf.to_csv(f"{ART}/results_summary.csv", index=False)
print("\n================= MLM ABLATION (3 seeds) =================")
print(sdf.to_string(index=False))
print(f"\nartifacts -> {ART}/mlm_encoder.pt , results_per_seed.csv , results_summary.csv")
print("=== RESULT: SUCCESS ===")
