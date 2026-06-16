# Block s5 — masked two-pool multi-task fine-tune setup (dataset, model, metrics, finetune fn).
# finetune("MLM-off", None, seed)          -> vanilla NeoBERT
# finetune("MLM-on", adapted_state, seed)  -> encoder adapted in block s4
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

METRICS = ["emo_macroF1", "emo_ece", "sev_pearson", "sev_spearman", "sev_mae"]
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
print("fine-tune setup ready | pools:", len(recs), "| metrics:", METRICS)
