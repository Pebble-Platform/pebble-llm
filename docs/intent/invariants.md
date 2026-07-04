# Invariants (intent layer) — ViEmoSpeech

> **Layer:** intent. Each entry is to be mirrored by a permanent test that runs
> on every CI run. A PR that breaks one is wrong by definition — the fix is the
> code, unless a human deliberately revises the invariant (edit this file and
> the test in the same, explicitly-flagged PR).
>
> **Bootstrapping note (pivot 2026-07-04):** the archived thesis suite lives in
> `archive/tests/`. The corpus invariant suite does not exist yet — building it
> is the first change under `docs/spec/changes/`. Until then these rows name
> the intended check, not a green one; I1 is already enforced by `.gitignore`.

| # | Invariant | Source | Check (today → target) |
|---|---|---|---|
| I1 | No episode media, clip, or full episode transcript is committed or released: `data/**` stays untracked; releases contain features + timestamps + labels + speaker ids only. | constraints §1 | `.gitignore` (`data/vietnamese-ser/**`) → CI gate over `git ls-files data/` + release-manifest lint |
| I2 | Every weak-label row carries a model identifier, and the prompt that produced it exists at a pinned path in git (`scripts/vietnamese-ser/m4_prompt.md`). No corpus label from untracked prompts or interactive chat. | constraints §5 | label-file lint: non-empty `model` column; prompt file exists at pinned path |
| I3 | Every clip in the released weak pool is single-speaker by BOTH gates: diarization turn-cut (non-empty `speaker`) AND not OR-flagged `multi_speaker_suspect` by the two teachers. | constraints §2 | pool-builder assertion over `segments.csv` × `labels_*.csv` |
| I4 | Speaker-disjoint splits: no speaker id in more than one of train/dev/test; gold speakers ∩ weak-pool speakers = ∅. | constraints §3 | `tests/invariants/test_speaker_disjoint.py` (to add with split builder) |
| I5 | Every reported number traces to a generated report file produced by a committed script (`report.md`, `m4*_report.md`, `05-scale-plan.md` arithmetic); GPU kernels pin their stack (`torch==2.5.1+cu121` line present). | constraints §5 | report-lint + grep over `kaggle/**` pip blocks |
| I6 | Inter-teacher κ is never presented as accuracy; any accuracy/F1/UAR claim names its held-out human-gold eval set. | constraints §4 | report-lint over `docs/**` metric tables |
