# Block 3 — MLM pre-training: 30% masking on in-domain text. Watch the loss drop.
corpus = [r["text"] for r in go_tr] + [r["text"] for r in ei_tr]
random.shuffle(corpus); corpus = corpus[:MLM_CORPUS_CAP]
mlm_ids, mlm_attn = encode(corpus)
print(f"[MLM] corpus={len(corpus)} texts, {int(MLM_MASK_PROB*100)}% masking, {MLM_EPOCHS} epochs")

SPECIAL = torch.tensor(tok.all_special_ids)
def mask_batch(ids):
    ids = ids.clone(); labels = ids.clone()
    keep = torch.isin(ids, SPECIAL)
    prob = torch.full(ids.shape, MLM_MASK_PROB); prob[keep] = 0.0
    sel = torch.bernoulli(prob).bool()
    labels[~sel] = -100
    r = torch.rand(ids.shape)
    ids[sel & (r < 0.8)] = tok.mask_token_id
    rnd_pos = sel & (r >= 0.8) & (r < 0.9)
    ids[rnd_pos] = torch.randint(VOCAB, ids.shape)[rnd_pos]
    return ids, labels

# NeoBERTLMHead: .model is the inner encoder; forward -> MaskedLMOutput(logits), no loss.
mlm = AutoModelForMaskedLM.from_pretrained(MODEL, revision=REVISION, trust_remote_code=True).to(DEVICE)
enc_ref = mlm.model
opt = torch.optim.AdamW(mlm.parameters(), lr=5e-5, weight_decay=0.01)
scaler = torch.cuda.amp.GradScaler()
order = list(range(len(corpus)))
mlm.train()
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
print("[MLM] training done")
