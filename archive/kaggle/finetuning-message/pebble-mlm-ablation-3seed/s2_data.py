# Block s2 — tokenizer + downstream data (GoEmotions simplified -> emotion, EI-reg -> severity)
# Also builds FT_EVAL_TEXTS: the normalized text of every fine-tune/eval example,
# so the MLM corpus (block s3) can be deduped against it (no leakage / no overfit).
tok = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, trust_remote_code=True)
VOCAB = tok.vocab_size
print("vocab", VOCAB, "| mask_token", tok.mask_token, tok.mask_token_id)

def norm(t):  # canonical form for dedup
    return " ".join(t.lower().split())

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
    print("!! eireg unavailable -> synthetic severity fallback")
    rnd = lambda: random.random()
    ei_tr = [{"text": f"i feel low energy and distress sample {i} {rnd():.2f}", "severity": rnd()} for i in range(4000)]
    ei_va = [{"text": f"a tough day sample {i} {rnd():.2f}", "severity": rnd()} for i in range(600)]
print(f"GoEmotions train={len(go_tr)} val={len(go_va)} ({N_EMO} classes) | EI-reg train={len(ei_tr)} dev={len(ei_va)}")

# text that must NOT appear in the MLM corpus (everything we fine-tune on or eval on)
FT_EVAL_TEXTS = set()
for split in (go_tr, go_va, ei_tr, ei_va):
    FT_EVAL_TEXTS.update(norm(r["text"]) for r in split)
print(f"dedup guard: {len(FT_EVAL_TEXTS)} fine-tune/eval texts blacklisted")

def encode(texts):
    e = tok(texts, truncation=True, max_length=MAX_LEN, padding="max_length", return_tensors="pt")
    return e["input_ids"], e["attention_mask"]
print("data ready")
