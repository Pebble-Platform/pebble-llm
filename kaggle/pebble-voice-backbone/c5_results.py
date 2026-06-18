# Cell 5 — aggregate (mean +/- std), paired delta, and save serving artifacts.
import pandas as pd
HF_ID = {"wavlm-large": "microsoft/wavlm-large", "emotion2vec": "iic/emotion2vec_base"}
METRICS = ["emo_macroF1", "distress_recall@0.5", "precision@floor", "thr@floor"]

rows = []
agg = {}
for name, seeds in results.items():
    agg[name] = {}
    for k in METRICS:
        vals = np.array([s[k] for s in seeds])
        agg[name][k] = (vals.mean(), vals.std())
        rows.append({"backbone": name, "metric": k,
                     "mean": round(float(vals.mean()), 4), "std": round(float(vals.std()), 4)})
df = pd.DataFrame(rows)
df.to_csv(f"{ART}/results_voice_backbone.csv", index=False)
print(df.to_string(index=False))

# paired per-seed delta emotion2vec - wavlm (the real verdict), when both ran.
if "emotion2vec" in results and "wavlm-large" in results:
    print("\nPaired delta (emotion2vec - wavlm-large), per seed then mean+/-std:")
    for k in ["emo_macroF1", "precision@floor"]:
        d = np.array([results["emotion2vec"][i][k] - results["wavlm-large"][i][k]
                      for i in range(len(SEEDS))])
        print(f"  {k}: {d.mean():+.4f} +/- {d.std():.4f}  (per-seed {np.round(d,4).tolist()})")

# pick the winning backbone by mean emotion macro-F1.
winner = max(agg, key=lambda n: agg[n]["emo_macroF1"][0])
print(f"\nWINNER by emo_macroF1: {winner}")

# save a serving bundle per backbone so the FastAPI app can load either.
for name, (emo_h, saf_h, thr) in artifacts.items():
    d = f"{ART}/artifact_{name}"
    os.makedirs(d, exist_ok=True)
    torch.save(emo_h.state_dict(), f"{d}/emotion_head.pt")
    torch.save(saf_h.state_dict(), f"{d}/safety_head.pt")
    cfg = {"backbone_hf_id": HF_ID[name], "backbone": name, "embed_dim": BACKBONES[name]["dim"],
           "emotions": EMOTIONS, "distress_emotions": sorted(DISTRESS),
           "safety_threshold": float(thr), "recall_floor": RECALL_FLOOR,
           "sample_rate": SR, "max_samples": MAX_SAMPLES, "pooling": "mean",
           "head_dim": HEAD_DIM, "safety_head_dim": 64,
           "is_winner": name == winner}
    with open(f"{d}/config.json", "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"  saved bundle -> {d} (winner={name == winner})")

with open(f"{ART}/results_voice_backbone.json", "w") as f:
    json.dump({"agg": {n: {k: list(v) for k, v in m.items()} for n, m in agg.items()},
               "per_seed": results, "winner": winner, "seeds": SEEDS}, f, indent=2)
print("\nartifacts in /kaggle/working: results_voice_backbone.{csv,json}, sample_val.wav, artifact_*/")
