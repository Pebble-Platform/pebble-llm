# Block 8 — results table + save
import pandas as pd
df = pd.DataFrame([off, on])
delta = {"arm": "delta (on - off)"}
for c in ["emo_macroF1", "emo_ece", "sev_pearson", "sev_spearman", "sev_mae"]:
    delta[c] = round(on[c] - off[c], 4)
df = pd.concat([df, pd.DataFrame([delta])], ignore_index=True)
df.to_csv(f"{ART}/results_mlm_ablation.csv", index=False)
print("============ MLM ISOLATION ABLATION ============")
print(df.to_string(index=False))
print(f"\nartifacts -> {ART}/mlm_encoder.pt , {ART}/results_mlm_ablation.csv")
print("=== RESULT: SUCCESS ===")
