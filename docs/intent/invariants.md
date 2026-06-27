# Invariants (intent layer)

> **Layer:** intent. Each entry here is mirrored by a permanent test in
> `tests/invariants/` that runs on every CI run, regardless of phase. A PR that
> breaks one is wrong by definition — the fix is the code, unless a human is
> deliberately revising the invariant itself (edit this file and the test in the
> same, explicitly-flagged PR).
>
> Every invariant below is **mechanically checkable**. Statements that express
> values but cannot be checked live in [constraints.md](constraints.md) instead.
>
> **Bootstrapping note (scaffold init):** `tests/invariants/` does not exist
> yet. I1 and I3 are *already* enforced today by `tests/test_splits.py`; I4 is
> *already* enforced by `.gitignore`. The remaining tests are to be added (see
> change `001`, phase 0). Until then these rows name the intended check, not a
> green one — do not treat an unchecked row as satisfied.

| # | Invariant | Source | Check (today → target) |
|---|---|---|---|
| I1 | Same subject/user always lands in the same split; no user's posts straddle train/val/test. | constraints §2 | `tests/test_splits.py::test_user_level_no_leakage` → move to `tests/invariants/` |
| I2 | Any reported **gold** metric trains only on weak/LLM labels and evaluates only on held-out clinical-gold labels; the train pool and the gold-eval pool are disjoint by example id. | constraints §1 | `tests/invariants/test_gold_holdout_disjoint.py` (to add) |
| I3 | Split and fold assignment are **deterministic** given a fixed seed. | constraints §4 | `tests/test_splits.py::test_split_is_deterministic` → `tests/invariants/` |
| I4 | No raw social-media/clinical corpus or PII is committed: `data/**/{raw,interim,processed,external}` and `kaggle/**/sequences.csv` stay untracked (only allow-listed tooling files are tracked). | constraints §5 | CI gate over `git ls-files data/ kaggle/` (allow-list in `.gitignore`) |
| I5 | GPU runs pin the documented reproducible stack (`torch==2.5.1`, `torchvision==0.20.1`, `torchaudio==2.5.1`, `xformers==0.0.28.post3`, `transformers==4.48.2`); a kernel that floats these is non-reproducible. | constraints §4 | grep over `kaggle/**` pip/requirements blocks |
| I6 | Every reported ordinal model comparison reports **QWK and MAE alongside macro-F1** (ordering-aware, not nominal-F1-only). | constraints §6 | report-lint over `docs/reports/**`, `docs/papers/**` metric tables |
