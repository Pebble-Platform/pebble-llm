# Invariants (intent layer) — Vietnamese emotional dubbing (+ ViEmoSpeech component)

> **Layer:** intent. Each entry is to be mirrored by a permanent test that runs
> on every CI run. A PR that breaks one is wrong by definition — the fix is the
> code, unless a human deliberately revises the invariant (edit this file and
> the test in the same, explicitly-flagged PR).
>
> **Pivot 2026-10-09:** the goal is now research on a Vietnamese dubbing model
> for foreign films (constraints.md §1). I1 is widened to cover dubbing media;
> I2–I6 still bind the ViEmoSpeech component (constraints.md §3); I7–I9 are new
> for generated speech. Previous version: `git show fc4dad7:docs/intent/invariants.md`.
>
> **Bootstrapping note:** the archived thesis suite lives in `archive/tests/`.
> No invariant suite exists yet — these rows name the intended check, not a
> green one; I1 is already enforced by `.gitignore`.

| # | Invariant | Source | Check (today → target) |
|---|---|---|---|
| I1 | No copyrighted media is committed or released: test films and their official VN dubs, VN drama episodes, clips, full transcripts / scripts, and **dubbed audio generated for those films**. `data/**` stays untracked; releases contain features + timestamps + labels + speaker ids + models/control vectors + demo audio of self-written text only. | constraints §2.1 | `.gitignore` (`data/**`) → CI gate over `git ls-files data/` + release-manifest lint |
| I2 | Every corpus label row of record carries its **annotator id + timestamp**; any retained teacher-suggestion column carries its model id, and the suggestion prompt exists at a pinned path in git (`scripts/vietnamese-ser/m4_prompt.md`). No corpus label from an unattributed source. | constraints §3 | label-file lint: non-empty `annotator` column; pinned prompt exists |
| I3 | Every clip in the corpus is single-speaker by BOTH gates: diarization turn-cut (non-empty `speaker`) AND not flagged multi-voice by the **human annotator** (labeler `multi` / reject). | constraints §3 | corpus-builder assertion over `segments.csv` × human-label state |
| I4 | Speaker-disjoint splits: no speaker id in more than one of train/dev/test; **test speakers ∩ train speakers = ∅** (ADR-002: held-out whole-series). | constraints §3 | `tests/invariants/test_speaker_disjoint.py` (to add with split builder) |
| I5 | Every reported number traces to a generated report file produced by a committed script; GPU kernels pin their stack (`torch==2.5.1+cu121` line present). | constraints §2.6 | report-lint + grep over `kaggle/**` pip blocks |
| I6 | Any accuracy/F1/UAR claim names its **speaker-disjoint held-out test set**; label reliability is reported as **inter-annotator κ/α (human–human)** and never conflated with accuracy. Teacher output must **not** be reported as a baseline method against the (anchored) human labels. | constraints §3, ADR-003 | report-lint over `docs/**` metric tables |
| I7 | **Valid voice bank:** every generated utterance is synthesized with a voice id present in the voice registry (dataset, speaker id, license, basis that the speaker recorded *for* that dataset); no generated audio uses a reference/prompt clip or timbre from outside the registry (source-film actors, ViEmoSpeech actors, official VN-dub actors, scraped datasets). | constraints §2.2 | synthesis entry point asserts `voice_id ∈ voice registry` and reference clip ∈ that voice's registry recordings |
| I8 | **Dubbing quality reports are complete and honest:** every quality report names a held-out test set (films/characters/voices disjoint from development) and includes blind human emotion judgement (raters + agreement), **tone error rate**, and **duration deviation**; embedding similarity (e.g. emotion2vec E-SIM) is never reported as emotion accuracy. | constraints §2.3–2.6 | report-lint over dubbing eval reports |
| I9 | Every generated audio file carries an AI-generated disclosure label (metadata + audible/visible notice when presented). *(Legal basis pending verification — constraints §2.7.)* | constraints §2.7 | writer asserts label metadata on every output file |
