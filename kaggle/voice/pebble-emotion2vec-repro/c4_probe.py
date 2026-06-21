# Cell 4 — SUPERB linear probe (v2, frame-level) + random 10-fold CV.
#   head = Linear(d,256) -> ReLU -> MASKED-mean-pool over valid frames -> Linear(256,8).
#   This is the faithful EmoBox/emotion2vec SuperbBaseModel (pool AFTER the first linear).
#   per fold: stratified 80/10/10 split (seeded), train on 80, best epoch by val acc,
#   report WA/UA/WF1 on 10% test. Aggregate mean +/- std over 10 folds.
class SuperbHead(nn.Module):
    def __init__(self, dim, n, hid=HEAD_DIM):
        super().__init__()
        self.pre = nn.Linear(dim, hid)
        self.post = nn.Linear(hid, n)
    def forward(self, x, mask):                              # x (B,T,dim), mask (B,T)
        h = F.relu(self.pre(x))                              # (B,T,hid)
        m = mask.unsqueeze(-1).float()
        h = (h * m).sum(1) / m.sum(1).clamp(min=1.0)         # masked mean over time
        return self.post(h)

def split_80_10_10(y, seed):
    idx = np.arange(len(y))
    tr, tmp = train_test_split(idx, test_size=SPLIT[1] + SPLIT[2], random_state=seed, stratify=y)
    rel = SPLIT[2] / (SPLIT[1] + SPLIT[2])
    va, te = train_test_split(tmp, test_size=rel, random_state=seed, stratify=y[tmp])
    return tr, va, te

def metrics(y_true, y_pred):
    return {"WA": 100 * accuracy_score(y_true, y_pred),
            "UA": 100 * recall_score(y_true, y_pred, average="macro", zero_division=0),
            "WF1": 100 * f1_score(y_true, y_pred, average="weighted", zero_division=0)}

def train_one(Xg, mask_g, y, dim, seed):
    tr, va, te = split_80_10_10(y, seed)
    set_seed(seed)
    yt = torch.tensor(y, dtype=torch.long, device=DEVICE)
    head = SuperbHead(dim, N_EMO).to(DEVICE)
    opt = torch.optim.Adam(head.parameters(), lr=PROBE_LR, weight_decay=WD)
    tr_t = torch.tensor(tr, device=DEVICE)
    best_val, best_state = -1.0, None
    for _ in range(PROBE_EPOCHS):
        head.train(); opt.zero_grad()
        loss = F.cross_entropy(head(Xg[tr_t], mask_g[tr_t]), yt[tr_t])
        loss.backward(); opt.step()
        head.eval()
        with torch.no_grad():
            va_pred = head(Xg[va], mask_g[va]).argmax(-1).cpu().numpy()
        va_acc = accuracy_score(y[va], va_pred)
        if va_acc > best_val:
            best_val = va_acc
            best_state = {k: v.detach().clone() for k, v in head.state_dict().items()}
    head.load_state_dict(best_state); head.eval()
    with torch.no_grad():
        te_pred = head(Xg[te], mask_g[te]).argmax(-1).cpu().numpy()
    return metrics(y[te], te_pred), head

# frame mask (N, T_MAX): True for valid frames.
mask_all = (torch.arange(T_MAX)[None, :] < torch.tensor(flen_all)[:, None]).to(DEVICE)

results = {}     # name -> list of per-fold metric dicts
artifacts = {}   # name -> head from fold 0
for name, b in BACKBONES.items():
    Xg = torch.tensor(b["X"], dtype=torch.float, device=DEVICE)   # (N,T,dim) f16->f32 on GPU
    results[name] = []
    for fold in range(N_FOLDS):
        m, head = train_one(Xg, mask_all, y_all, b["dim"], BASE_SEED + fold)
        results[name].append(m)
        if fold == 0:
            artifacts[name] = head
        print(f"[{name} fold={fold}] WA={m['WA']:.2f} UA={m['UA']:.2f} WF1={m['WF1']:.2f}")
    del Xg; torch.cuda.empty_cache()
    arr = {k: np.array([f[k] for f in results[name]]) for k in ("WA", "UA", "WF1")}
    print(f"[{name}] MEAN  WA={arr['WA'].mean():.2f}±{arr['WA'].std():.2f} "
          f"UA={arr['UA'].mean():.2f}±{arr['UA'].std():.2f} "
          f"WF1={arr['WF1'].mean():.2f}±{arr['WF1'].std():.2f}")
