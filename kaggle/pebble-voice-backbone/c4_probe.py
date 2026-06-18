# Cell 4 — multi-task probe: emotion softmax + distress BCE, 3 seeds, recall-floored threshold.
# Head architectures mirror src/pebble_llm/models/heads.py so the FastAPI app can reuse them.
class EmotionHead(nn.Module):
    def __init__(self, dim, n, head_dim=HEAD_DIM, dropout=0.1):
        super().__init__()
        self.net = nn.Sequential(nn.Dropout(dropout), nn.Linear(dim, head_dim), nn.GELU(),
                                 nn.Dropout(dropout), nn.Linear(head_dim, n))
    def forward(self, x): return self.net(x)

class SafetyHead(nn.Module):
    def __init__(self, dim, head_dim=64, dropout=0.1):
        super().__init__()
        self.net = nn.Sequential(nn.Dropout(dropout), nn.Linear(dim, head_dim), nn.GELU(),
                                 nn.Linear(head_dim, 1))
    def forward(self, x): return self.net(x).squeeze(-1)

emo_tr = torch.tensor([r["emo"] for r in train_recs], dtype=torch.long)
dis_tr = torch.tensor([r["distress"] for r in train_recs], dtype=torch.float)
emo_va = np.array([r["emo"] for r in val_recs])
dis_va = np.array([r["distress"] for r in val_recs])

def threshold_at_recall(y, prob, floor):
    # lowest threshold whose recall >= floor; report precision there (Pebble safety framing).
    best_t, best_p = 0.5, 0.0
    for t in np.linspace(0.01, 0.99, 99):
        pred = (prob >= t).astype(int)
        if recall_score(y, pred, zero_division=0) >= floor:
            p = precision_score(y, pred, zero_division=0)
            if t > best_t or best_p == 0.0:
                best_t, best_p = t, p
    return best_t, best_p

def train_probe(Xtr, Xva, dim, seed):
    set_seed(seed)
    Xtr_t = torch.tensor(Xtr, dtype=torch.float, device=DEVICE)
    Xva_t = torch.tensor(Xva, dtype=torch.float, device=DEVICE)
    emo_h, saf_h = EmotionHead(dim, N_EMO).to(DEVICE), SafetyHead(dim).to(DEVICE)
    opt = torch.optim.AdamW(list(emo_h.parameters()) + list(saf_h.parameters()),
                            lr=PROBE_LR, weight_decay=1e-2)
    et, dt = emo_tr.to(DEVICE), dis_tr.to(DEVICE)
    pw = torch.tensor(SAFETY_POS_WEIGHT, device=DEVICE)
    for _ in range(PROBE_EPOCHS):
        emo_h.train(); saf_h.train(); opt.zero_grad()
        loss = (F.cross_entropy(emo_h(Xtr_t), et)
                + F.binary_cross_entropy_with_logits(saf_h(Xtr_t), dt, pos_weight=pw))
        loss.backward(); opt.step()
    emo_h.eval(); saf_h.eval()
    with torch.no_grad():
        emo_pred = emo_h(Xva_t).argmax(-1).cpu().numpy()
        dis_prob = torch.sigmoid(saf_h(Xva_t)).cpu().numpy()
    f1 = f1_score(emo_va, emo_pred, average="macro")
    thr, prec = threshold_at_recall(dis_va, dis_prob, RECALL_FLOOR)
    auroc_rec = recall_score(dis_va, (dis_prob >= 0.5).astype(int), zero_division=0)
    return {"emo_macroF1": f1, "distress_recall@0.5": auroc_rec,
            "thr@floor": thr, "precision@floor": prec}, (emo_h, saf_h, thr)

results = {}     # name -> list of per-seed metric dicts
artifacts = {}   # name -> (emo_h, saf_h, thr) from seed 0 (for serving)
for name, b in BACKBONES.items():
    results[name] = []
    for si, seed in enumerate(SEEDS):
        m, art = train_probe(b["train"], b["val"], b["dim"], seed)
        results[name].append(m)
        if si == 0:
            artifacts[name] = art
        print(f"[{name} seed={seed}] emo_macroF1={m['emo_macroF1']:.4f} "
              f"distress_recall={m['distress_recall@0.5']:.3f} "
              f"prec@recall{RECALL_FLOOR}={m['precision@floor']:.3f} (thr={m['thr@floor']:.2f})")
