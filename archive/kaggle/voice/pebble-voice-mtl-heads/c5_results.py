# Cell 5 — aggregate (mean +/- std over folds), save 3-head artifacts + results.
import pandas as pd
HF_ID = {"wavlm-large": "microsoft/wavlm-large", "emotion2vec": "iic/emotion2vec_base"}
KEYS = ("WA", "UA", "WF1", "CCC_v", "CCC_a", "crisis_recall", "crisis_prec")

rows, agg = [], {}
for name, folds in results.items():
    agg[name] = {}
    for k in KEYS:
        vals = np.array([f[k] for f in folds])
        agg[name][k] = (float(vals.mean()), float(vals.std()))
        rows.append({"backbone": name, "metric": k,
                     "mean": round(float(vals.mean()), 3), "std": round(float(vals.std()), 3)})
df = pd.DataFrame(rows)
df.to_csv(f"{ART}/results_voice_mtl.csv", index=False)
print(df.to_string(index=False))

print(f"\n=== Multi-task summary (hard crisis-recall floor = {RECALL_FLOOR:.2f}) ===")
for name, a in agg.items():
    print(f"[{name}] emotion WA={a['WA'][0]:.2f}  |  affect CCC v={a['CCC_v'][0]:.2f}/a={a['CCC_a'][0]:.2f}"
          f"  |  crisis recall={a['crisis_recall'][0]:.2f} prec={a['crisis_prec'][0]:.2f}")

# save a serving/test bundle per backbone (fold-0 head).
for name, head in artifacts.items():
    d = f"{ART}/artifact_{name}"
    os.makedirs(d, exist_ok=True)
    torch.save(head.state_dict(), f"{d}/mtl_head.pt")
    cfg = {"backbone_hf_id": HF_ID[name], "backbone": name, "embed_dim": BACKBONES[name]["dim"],
           "emotions": EMOTIONS, "valence_arousal": VALENCE_AROUSAL, "crisis_set": sorted(CRISIS),
           "recall_floor": RECALL_FLOOR, "crisis_tau": results[name][0]["tau"],
           "sample_rate": SR, "max_samples": MAX_SAMPLES, "frame_hop": FRAME_HOP, "t_max": T_MAX,
           "pooling": "masked-mean", "head": "mtl-3head", "head_dim": HEAD_DIM}
    with open(f"{d}/config.json", "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"  saved bundle -> {d}")

with open(f"{ART}/results_voice_mtl.json", "w") as f:
    json.dump({"agg": agg, "per_fold": results, "recall_floor": RECALL_FLOOR,
               "n_folds": N_FOLDS, "split": SPLIT, "base_seed": BASE_SEED}, f, indent=2)
print("\nartifacts in /kaggle/working: results_voice_mtl.{csv,json}, sample_val.wav, "
      "artifact_*/ (mtl_head.pt + config.json)")
