# Block s4 — MLM pre-training (15% masking) on the separate corpus, then save the
# adapted encoder in fp32 (no fp16 rounding -> removes the precision confound vs the
# vanilla MLM-off baseline). Run once; block s6 reuses the saved state for every seed.
print(f"[MLM] corpus={len(corpus)} texts, {int(MLM_MASK_PROB*100)}% masking, {MLM_EPOCHS} epochs")
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

# NeoBERTLMHead: .model is the inner encoder; forward -> MaskedLMOutput(logits), no loss.
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

adapted_state = {k: v.detach().float().cpu() for k, v in enc_ref.state_dict().items()}
torch.save(adapted_state, f"{ART}/mlm_encoder.pt")
print(f"[MLM] saved adapted encoder -> {ART}/mlm_encoder.pt ({len(adapted_state)} tensors, fp32)")
del mlm, enc_ref, opt; torch.cuda.empty_cache()
