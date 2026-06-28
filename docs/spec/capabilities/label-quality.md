# Label quality (capability)

> **Status:** authoritative for ordinal-CL diagnostic + label-shift correction;
> κ-vs-gold and the cleaned-pool retrain (B-Arm2) still owed for IEEE.
> Implementation: `kaggle/finetuning-message/{r2-tier1-cleanlab,r2-label-shift}/`,
> `docs/tasks/r2-method-improvements-for-contribution.md`.
> Owned by `../changes/001-initial-build/phase-4-label-quality.md`.

**What it covers:** quantifying and correcting the LLM→clinical-gold label gap.

- **(a) Ordinal-aware Confident Learning** (kernel `r2-tier1-cleanlab-diagnostic`,
  5-fold OOF). Diagnostic: **35.8% of Behavior labels** (227/634) flagged suspect
  vs 16.2% pool-wide → confirms the Behavior bottleneck is a label-quality
  problem. The ordinal variant (confident-joint weighted by `|ỹ−ŷ|²`) cleans
  **100% of far errors** (Behavior→Indicator) while **keeping 78% of adjacent**
  borderline (Behavior↔Ideation) — nominal CL over-flags 45% of adjacent.
- **(b) Label-shift correction** (local, 0 GPU, on the flat-CE checkpoint).
  Measured shift `π_gold/π_train` Behavior = **3.0×** (under-labelled). Post-hoc
  Logit-Adjustment (no retrain) lifts Behavior-F1 **0.357 → 0.41** (oracle 0.44).

**Still owed:** Cohen's κ(LLM,gold) + confusion on the overlap set (IEEE §4);
the ordinal-cleaned-pool retrain (B-Arm2).

**Binds invariants:** I5 (each number cites its kernel+log), I6 (ordering-aware
cleaning/metrics).
