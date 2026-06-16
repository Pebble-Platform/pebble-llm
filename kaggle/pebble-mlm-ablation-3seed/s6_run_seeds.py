# Block s6 — run BOTH arms across all seeds. Writes results_per_seed.csv after EVERY
# seed, so if the run is interrupted you keep the seeds already finished.
import pandas as pd
rows = []
csv_seed = f"{ART}/results_per_seed.csv"
for seed in SEEDS:
    print(f"\n=== seed {seed} ===")
    off = finetune("MLM-off", None, seed);          print("  off:", {k: round(off[k], 4) for k in METRICS})
    on  = finetune("MLM-on", adapted_state, seed);  print("  on :", {k: round(on[k], 4) for k in METRICS})
    rows += [off, on]
    pd.DataFrame(rows).to_csv(csv_seed, index=False)   # incremental checkpoint
print(f"\nper-seed results saved -> {csv_seed} ({len(rows)} rows)")
