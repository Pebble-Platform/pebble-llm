# Block s8 — train ONE shippable model on the chosen arm, save it whole, run a demo.
# The ablation (s6) throws every fine-tuned model away; this block keeps one so you
# get a usable artifact (encoder + both heads) plus an analyze(text) inference fn.
SHIP_ARM  = "MLM-off"   # "MLM-off" = vanilla (best severity) | "MLM-on" = adapted (best emotion F1)
SHIP_SEED = 42
adapted = adapted_state if SHIP_ARM == "MLM-on" else None

set_seed(SHIP_SEED)
ship = MultiTask(adapted).to(DEVICE)
opt = torch.optim.AdamW([
    {"params": [p for n, p in ship.named_parameters() if not n.startswith("encoder.")], "lr": 2e-5},
    {"params": ship.encoder.parameters(), "lr": 1e-5}], weight_decay=0.01)
scaler = torch.cuda.amp.GradScaler()
loader = DataLoader(ft_ds, batch_size=BATCH, shuffle=True)
for ep in range(FT_EPOCHS):
    ship.train()
    for ids, attn, task, emo, sev in loader:
        ids, attn, task = ids.to(DEVICE), attn.to(DEVICE), task.to(DEVICE)
        emo, sev = emo.to(DEVICE), sev.to(DEVICE)
        me, ms = task == EMO, task == SEV
        opt.zero_grad()
        with torch.cuda.amp.autocast():
            el, sp = ship(ids, attn)
            loss = el.sum() * 0.0
            if me.any(): loss = loss + F.cross_entropy(el[me], emo[me])
            if ms.any(): loss = loss + F.mse_loss(sp[ms], sev[ms])
        scaler.scale(loss).backward(); scaler.step(opt); scaler.update()
    print(f"  [ship/{SHIP_ARM}] epoch {ep+1}/{FT_EPOCHS} done")

# save the WHOLE model + the metadata needed to rebuild it for inference later
ckpt = {"state_dict": {k: v.detach().cpu() for k, v in ship.state_dict().items()},
        "emo_names": EMO_NAMES, "model": MODEL, "revision": REVISION,
        "max_len": MAX_LEN, "arm": SHIP_ARM, "seed": SHIP_SEED}
torch.save(ckpt, f"{ART}/pebble_model.pt")
print(f"[ship] saved -> {ART}/pebble_model.pt  ({SHIP_ARM}, seed {SHIP_SEED}, {len(ckpt['state_dict'])} tensors)")

# ---------------------------------------------------------------- inference
@torch.no_grad()
def analyze(text, topk=3):
    ship.eval()
    ids, attn = encode([text])
    with torch.cuda.amp.autocast():
        el, sp = ship(ids.to(DEVICE), attn.to(DEVICE))
    probs = torch.softmax(el.float(), -1).cpu().numpy()[0]
    sev = float(sp.float().cpu().numpy()[0])
    top = probs.argsort()[::-1][:topk]
    return {"severity": round(sev, 3),
            "emotions": [(EMO_NAMES[i], round(float(probs[i]), 3)) for i in top]}

TESTS = [
    "I just got promoted, best day of my life!",
    "the meeting is at 3pm tomorrow",
    "why does everyone always ignore me",
    "I can't do this anymore, nothing matters",
    "I'm so scared something bad will happen",
]
print("\n================= INFERENCE DEMO =================")
for t in TESTS:
    r = analyze(t)
    top = ", ".join(f"{e}:{p}" for e, p in r["emotions"])
    print(f"severity={r['severity']:.3f} | {top}   <= {t!r}")
print("=== RESULT: SUCCESS ===")
