# Block s3 — build the BIG, SEPARATE in-domain MLM corpus.
# Sources: GoEmotions *raw* (~211k Reddit comments) + tweet_eval subsets (tweets).
# Every text is deduped against itself AND against FT_EVAL_TEXTS (block s2), so the
# encoder adapts on NEW unlabeled in-domain text -- the real TAPT/DAPT setup.
seen = set(FT_EVAL_TEXTS)   # start from the blacklist; also dedupes within the corpus
corpus, src_counts = [], {}
def add(name, texts):
    kept = 0
    for t in texts:
        if not t: continue
        n = norm(t)
        if n and n not in seen:
            seen.add(n); corpus.append(t); kept += 1
    src_counts[name] = kept
    print(f"  + {name}: +{kept} (corpus={len(corpus)})")

try:
    raw = load_dataset("go_emotions", "raw", split="train")
    add("go_emotions/raw", raw["text"])
except Exception as e:
    print("go_emotions raw failed:", e)

for sub in ["emotion", "sentiment", "offensive", "hate", "irony"]:
    try:
        for sp in ["train", "validation"]:
            ds = load_dataset("tweet_eval", sub, split=sp)
            add(f"tweet_eval/{sub}/{sp}", ds["text"])
    except Exception as e:
        print(f"tweet_eval {sub} failed:", e)

random.shuffle(corpus)
corpus = corpus[:MLM_CORPUS_CAP]
print(f"\n[MLM corpus] {len(corpus)} texts after dedup+cap | sources: {src_counts}")

mlm_ids, mlm_attn = encode(corpus)
print("[MLM corpus] tokenized ->", tuple(mlm_ids.shape))
