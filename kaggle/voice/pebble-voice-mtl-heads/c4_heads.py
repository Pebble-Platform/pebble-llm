# Cell 4 — 3-head MTL probe (shared SUPERB trunk) + Kendall uncertainty weighting,
# random 10-fold CV.
#   trunk = Linear(d,256) -> ReLU -> masked-mean-pool over valid frames  (= repro v2 trunk)
#   heads = emotion Linear(256,8) CE | affect Linear(256,2) CCC(valence,arousal) | crisis Linear(256,1) BCE
#   loss  = Kendall homoscedastic uncertainty weighting over the 3 task losses
# Per fold: train on 80%, select best epoch by VAL total loss, report on 10% test —
#   emotion WA/UA/WF1, valence/arousal CCC, and crisis recall/precision at a threshold
#   tuned ON VAL to guarantee recall >= RECALL_FLOOR (the hard-floor mechanic).
class MTLHead(nn.Module):
    def __init__(self, dim, hid=HEAD_DIM):
        super().__init__()
        self.pre = nn.Linear(dim, hid)        # shared SUPERB trunk
        self.emo = nn.Linear(hid, N_EMO)      # emotion (8-way)
        self.reg = nn.Linear(hid, 2)          # affect: valence, arousal
        self.safe = nn.Linear(hid, 1)         # crisis (binary)
    def forward(self, x, mask):               # x (B,T,dim), mask (B,T)
        h = F.relu(self.pre(x))
        m = mask.unsqueeze(-1).float()
        z = (h * m).sum(1) / m.sum(1).clamp(min=1.0)   # masked-mean utterance embedding
        return self.emo(z), self.reg(z), self.safe(z).squeeze(-1)

class UncertaintyWeighter(nn.Module):
    # Kendall, Gal & Cipolla (CVPR 2018) — homoscedastic uncertainty weighting over tasks.
    def __init__(self, n=3):
        super().__init__()
        self.log_var = nn.Parameter(torch.zeros(n))
    def forward(self, losses):
        return sum(0.5 * torch.exp(-self.log_var[i]) * L + 0.5 * self.log_var[i]
                   for i, L in enumerate(losses))

def ccc_loss(pred, tgt):
    pm, tm = pred.mean(), tgt.mean()
    pv, tv = pred.var(unbiased=False), tgt.var(unbiased=False)
    cov = ((pred - pm) * (tgt - tm)).mean()
    return 1 - 2 * cov / (pv + tv + (pm - tm) ** 2 + 1e-8)

def ccc_score(pred, tgt):
    pm, tm = pred.mean(), tgt.mean()
    cov = ((pred - pm) * (tgt - tm)).mean()
    return float(2 * cov / (pred.var() + tgt.var() + (pm - tm) ** 2 + 1e-8))

def threshold_for_recall(probs, labels, floor):
    # highest threshold (best precision) whose recall on these (val) examples is >= floor.
    pos = np.sort(probs[labels == 1])
    if len(pos) == 0:
        return 0.5
    k = min(int(np.floor((1 - floor) * len(pos))), len(pos) - 1)
    return float(pos[k])

def split_80_10_10(y, seed):
    idx = np.arange(len(y))
    tr, tmp = train_test_split(idx, test_size=SPLIT[1] + SPLIT[2], random_state=seed, stratify=y)
    rel = SPLIT[2] / (SPLIT[1] + SPLIT[2])
    va, te = train_test_split(tmp, test_size=rel, random_state=seed, stratify=y[tmp])
    return tr, va, te

def emo_metrics(y_true, y_pred):
    return {"WA": 100 * accuracy_score(y_true, y_pred),
            "UA": 100 * recall_score(y_true, y_pred, average="macro", zero_division=0),
            "WF1": 100 * f1_score(y_true, y_pred, average="weighted", zero_division=0)}

def train_one(Xg, mask_g, y, va_tgt, safe_tgt, dim, seed):
    tr, va, te = split_80_10_10(y, seed)
    set_seed(seed)
    yt = torch.tensor(y, dtype=torch.long, device=DEVICE)
    vt = torch.tensor(va_tgt, dtype=torch.float, device=DEVICE)     # (N,2)
    st = torch.tensor(safe_tgt, dtype=torch.float, device=DEVICE)   # (N,)
    head = MTLHead(dim).to(DEVICE)
    weighter = UncertaintyWeighter(3).to(DEVICE)
    opt = torch.optim.Adam(list(head.parameters()) + list(weighter.parameters()),
                           lr=PROBE_LR, weight_decay=WD)
    tr_t = torch.tensor(tr, device=DEVICE)
    best_val, best_state = 1e9, None
    for _ in range(PROBE_EPOCHS):
        head.train(); weighter.train(); opt.zero_grad()
        e, r, s = head(Xg[tr_t], mask_g[tr_t])
        losses = [F.cross_entropy(e, yt[tr_t]),
                  ccc_loss(r[:, 0], vt[tr_t, 0]) + ccc_loss(r[:, 1], vt[tr_t, 1]),
                  F.binary_cross_entropy_with_logits(s, st[tr_t])]
        loss = weighter(losses)
        loss.backward(); opt.step()
        head.eval()
        with torch.no_grad():
            e, r, s = head(Xg[va], mask_g[va])
            vl = (F.cross_entropy(e, yt[va]) + ccc_loss(r[:, 0], vt[va, 0])
                  + ccc_loss(r[:, 1], vt[va, 1])
                  + F.binary_cross_entropy_with_logits(s, st[va])).item()
        if vl < best_val:
            best_val = vl
            best_state = {k: v.detach().clone() for k, v in head.state_dict().items()}
    head.load_state_dict(best_state); head.eval()
    with torch.no_grad():
        _, _, sv = head(Xg[va], mask_g[va])
        et, rt, st_ = head(Xg[te], mask_g[te])
    # hard crisis-recall floor: tune tau on val, apply to test.
    tau = threshold_for_recall(torch.sigmoid(sv).cpu().numpy(), safe_tgt[va], RECALL_FLOOR)
    pred = (torch.sigmoid(st_).cpu().numpy() >= tau).astype(int)
    m = emo_metrics(y[te], et.argmax(-1).cpu().numpy())
    m.update({"CCC_v": ccc_score(rt[:, 0].cpu().numpy(), va_tgt[te, 0]),
              "CCC_a": ccc_score(rt[:, 1].cpu().numpy(), va_tgt[te, 1]),
              "crisis_recall": float(recall_score(safe_tgt[te], pred, zero_division=0)),
              "crisis_prec": float(precision_score(safe_tgt[te], pred, zero_division=0)),
              "tau": tau})
    return m, head

# frame mask (N, T): True for valid frames; proxy targets from c1 maps.
mask_all = (torch.arange(T_MAX)[None, :] < torch.tensor(flen_all)[:, None]).to(DEVICE)
va_all = VA[y_all]        # (N, 2) valence/arousal
safe_all = SAFE[y_all]    # (N,)  crisis 0/1

results = {}     # name -> list of per-fold metric dicts
artifacts = {}   # name -> head from fold 0
for name, b in BACKBONES.items():
    Xg = torch.tensor(b["X"], dtype=torch.float, device=DEVICE)   # (N,T,dim) f16->f32 on GPU
    results[name] = []
    for fold in range(N_FOLDS):
        m, head = train_one(Xg, mask_all, y_all, va_all, safe_all, b["dim"], BASE_SEED + fold)
        results[name].append(m)
        if fold == 0:
            artifacts[name] = head
        print(f"[{name} f{fold}] WA={m['WA']:.1f} CCCv={m['CCC_v']:.2f} CCCa={m['CCC_a']:.2f} "
              f"crisis R={m['crisis_recall']:.2f} P={m['crisis_prec']:.2f}")
    del Xg; torch.cuda.empty_cache()
    keys = ("WA", "UA", "WF1", "CCC_v", "CCC_a", "crisis_recall", "crisis_prec")
    arr = {k: np.array([f[k] for f in results[name]]) for k in keys}
    print(f"[{name}] MEAN " + " ".join(f"{k}={arr[k].mean():.2f}±{arr[k].std():.2f}" for k in keys))
