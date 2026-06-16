# Block s7 — aggregate: per-arm mean +/- std and the paired per-seed delta (on - off).
df = pd.DataFrame(rows)
summary = []
for arm in ["MLM-off", "MLM-on"]:
    sub = df[df.arm == arm]
    summary.append({"arm": arm, **{m: f"{sub[m].mean():.4f}+/-{sub[m].std():.4f}" for m in METRICS}})
piv = df.pivot(index="seed", columns="arm")
delta = {"arm": "delta (on-off) mean+/-std"}
for m in METRICS:
    d = piv[(m, "MLM-on")] - piv[(m, "MLM-off")]
    delta[m] = f"{d.mean():+.4f}+/-{d.std():.4f}"
sdf = pd.DataFrame(summary + [delta])
sdf.to_csv(f"{ART}/results_summary.csv", index=False)
print("\n================= MLM ABLATION (3 seeds) =================")
print(sdf.to_string(index=False))
print(f"\nartifacts -> {ART}/mlm_encoder.pt , results_per_seed.csv , results_summary.csv")
print("=== RESULT: SUCCESS ===")
