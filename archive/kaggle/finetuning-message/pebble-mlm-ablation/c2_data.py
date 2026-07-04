# Block 2 — tokenizer + data (GoEmotions -> emotion, SemEval EI-reg -> severity)
tok = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, trust_remote_code=True)
VOCAB = tok.vocab_size
print("vocab", VOCAB, "| mask_token", tok.mask_token, tok.mask_token_id)

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
NEUTRAL = EMO_NAMES.index("neutral")
N_EMO = len(EMO_NAMES)
def go_rows(ds):
    return [{"text": r["text"], "emotion": (r["labels"][0] if r["labels"] else NEUTRAL)} for r in ds]
go_tr, go_va = go_rows(go_train), go_rows(go_val)

ei_tr, ei_va = eireg("train"), eireg("dev")
if not ei_tr or not ei_va:
    print("!! eireg unavailable -> synthetic severity fallback")
    rnd = lambda: random.random()
    ei_tr = [{"text": f"i feel low energy and distress sample {i} {rnd():.2f}", "severity": rnd()} for i in range(3000)]
    ei_va = [{"text": f"a tough day sample {i} {rnd():.2f}", "severity": rnd()} for i in range(600)]
print(f"GoEmotions train={len(go_tr)} val={len(go_va)} ({N_EMO} classes) | EI-reg train={len(ei_tr)} dev={len(ei_va)}")

def encode(texts):
    e = tok(texts, truncation=True, max_length=MAX_LEN, padding="max_length", return_tensors="pt")
    return e["input_ids"], e["attention_mask"]
print("data ready")
