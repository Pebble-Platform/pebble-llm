# Cell 5 — aggregate (mean +/- std over folds), compare to paper Table 3, save artifacts.
import pandas as pd
HF_ID = {"wavlm-large": "microsoft/wavlm-large", "emotion2vec": "iic/emotion2vec_base"}

rows, agg = [], {}
for name, folds in results.items():
    agg[name] = {}
    for k in ("WA", "UA", "WF1"):
        vals = np.array([f[k] for f in folds])
        agg[name][k] = (float(vals.mean()), float(vals.std()))
        rows.append({"backbone": name, "metric": k,
                     "mean": round(float(vals.mean()), 2), "std": round(float(vals.std()), 2),
                     "paper": PAPER.get(name, {}).get(k)})
df = pd.DataFrame(rows)
df.to_csv(f"{ART}/results_emotion2vec_repro.csv", index=False)
print(df.to_string(index=False))

# headline comparison vs the paper's emotion2vec RAVDESS row.
print("\n=== Reproduction vs paper (emotion2vec, RAVDESS) ===")
for k in ("WA", "UA", "WF1"):
    if "emotion2vec" in agg:
        ours = agg["emotion2vec"][k][0]; paper = PAPER["emotion2vec"][k]
        print(f"  {k}: ours={ours:.2f}  paper={paper:.2f}  delta={ours - paper:+.2f}")
if "emotion2vec" in agg and "wavlm-large" in agg:
    d = agg["emotion2vec"]["WA"][0] - agg["wavlm-large"]["WA"][0]
    print(f"\nThesis comparator (our run): emotion2vec - wavlm-large WA delta = {d:+.2f}")

# save a serving/test bundle per backbone (fold-0 head).
for name, head in artifacts.items():
    d = f"{ART}/artifact_{name}"
    os.makedirs(d, exist_ok=True)
    torch.save(head.state_dict(), f"{d}/emotion_head.pt")
    cfg = {"backbone_hf_id": HF_ID[name], "backbone": name, "embed_dim": BACKBONES[name]["dim"],
           "emotions": EMOTIONS, "sample_rate": SR, "max_samples": MAX_SAMPLES,
           "frame_hop": FRAME_HOP, "t_max": T_MAX,
           "pooling": "masked-mean", "head": "superb-frame", "head_dim": HEAD_DIM}
    with open(f"{d}/config.json", "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"  saved bundle -> {d}")

with open(f"{ART}/results_emotion2vec_repro.json", "w") as f:
    json.dump({"agg": agg, "per_fold": results, "paper": PAPER,
               "n_folds": N_FOLDS, "split": SPLIT, "base_seed": BASE_SEED}, f, indent=2)
print("\nartifacts in /kaggle/working: results_emotion2vec_repro.{csv,json}, sample_val.wav, artifact_*/")
