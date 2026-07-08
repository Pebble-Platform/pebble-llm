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
| I2 | Every corpus label row of record carries its **annotator id + timestamp**; any retained teacher-suggestion column carries its model id, and the suggestion prompt exists at a pinned path in git (`scripts/vietnamese-ser/m4_prompt.md`). No corpus label from an unattributed source. | constraints §5 | label-file lint: non-empty `annotator` column; pinned prompt exists |
| I3 | Every clip in the corpus is single-speaker by BOTH gates: diarization turn-cut (non-empty `speaker`) AND not flagged multi-voice by the **human annotator** (labeler `multi` / reject). | constraints §2 | corpus-builder assertion over `segments.csv` × human-label state |
| I4 | Speaker-disjoint splits: no speaker id in more than one of train/dev/test; **test speakers ∩ train speakers = ∅** (ADR-002: held-out whole-series). | constraints §3 | `tests/invariants/test_speaker_disjoint.py` (to add with split builder) |
| I5 | Every reported number traces to a generated report file produced by a committed script (`report.md`, `m4*_report.md`, `05-scale-plan.md` arithmetic); GPU kernels pin their stack (`torch==2.5.1+cu121` line present). | constraints §5 | report-lint + grep over `kaggle/**` pip blocks |
| I6 | Any accuracy/F1/UAR claim names its **speaker-disjoint held-out test set**; label reliability is reported as **inter-annotator κ/α (human–human)** and never conflated with accuracy. Since teacher suggestions are shown during labeling, teacher output must **not** be reported as a baseline method against the (anchored) human labels. | constraints §4, ADR-003 | report-lint over `docs/**` metric tables |
