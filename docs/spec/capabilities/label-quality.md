# Label quality (capability — STUB)

> **Status:** stub. Authoritative detail lives in
> `PAPER-PLAN-text-ordinal-suicide.md` §3 (contributions 2–3) and
> `docs/tasks/r2-method-improvements-for-contribution.md`.
> Owned by `../changes/001-initial-build/phase-4-label-quality.md`.

**What it covers:** quantifying and correcting the LLM→clinical-gold label gap —
(a) **ordinal-aware Confident Learning** (confident-joint weighted by `|ỹ−ŷ|²`:
cleans far errors, keeps adjacent-borderline; flags 35.8% of Behavior labels
as suspect), and (b) **label-shift correction** (measured `π_gold/π_train`
Behavior = 3.0×; post-hoc Logit-Adjustment lifts Behavior-F1 0.357 → 0.41),
plus the κ-vs-gold + confusion analysis still owed for IEEE.

**Binds invariants:** I6 (ordering-aware cleaning/metrics).
