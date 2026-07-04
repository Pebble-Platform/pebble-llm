# Intent-Driven Workflow for Pebble-LLM (ViEmoSpeech — Vietnamese SER)

How we work on this repo. This is a **research program**: the output is the
ViEmoSpeech corpus (releasable, CC-BY, provenance-clean) plus the tone×emotion
bimodal SER method paper, and the governing constraint is that nothing legally
or ethically unreleasable ever leaves the machine.

> The previous programs (ordinal suicide-risk text, crisis voice affect, the
> v1–v3 product classifier) are archived under `archive/` — pivot decision
> 2026-07-04, recorded in `docs/intent/constraints.md`.

## The three layers

| Layer | Holds | Changes | In this repo |
|---|---|---|---|
| **Intent** | Why the project exists; legality/ethics & research-validity constraints; the never-list | Rarely; only by deliberate human decision, never as a side effect of implementation | `docs/intent/` (`constraints.md`, `invariants.md`) |
| **Spec** | The current best solution, split into **state** and **change** | Living; updated whenever a result or learning changes — in the same PR as the code/kernel (rule 5) | `docs/spec/capabilities/` (current truth), `docs/spec/changes/` (units of work), `docs/spec/decisions/` (ADRs); seed design `docs/papers/vietnamese-ser/04-pioneer-corpus-design.md` + `05-scale-plan.md` |
| **Execution** | Fully determined work: pipeline code, kernels, label scripts, invariant suite | Derived from the spec; nothing left to guess *that a check wouldn't catch* | `scripts/vietnamese-ser/`, `kaggle/vietnamese-ser/` |

The escalation rule that makes the layering work: **ambiguity escalates up, it
is never resolved downward by improvisation.** If execution hits a question the
spec doesn't answer, that's a spec hole — fix the spec first. If the spec can't
answer without knowing *why*, that's an intent question — a human decides.
(In research terms: a number obtained by guessing past a protocol hole is worse
than no number.)

```
docs/intent/constraints.md         why + the constraints bounding any valid result
docs/intent/invariants.md          the never-list (I1–I6), to be mirrored by tests
docs/spec/capabilities/            CURRENT TRUTH — what each capability does now
docs/spec/changes/NNN-<slug>/      units of work: proposal + tasks + verification
docs/spec/decisions/               ADRs — resolved-on-evidence decisions, append-only
docs/papers/vietnamese-ser/        corpus design + scale plan + scoping research
docs/tasks/                        living tracking docs + executed implement plans (provenance)
scripts/vietnamese-ser/            local pipeline: extract, align, weak-label, prompts
kaggle/vietnamese-ser/             GPU batch kernels (pinned stack)
archive/                           the pre-pivot programs, frozen at archive time
```

## Execution-layer layout

```
scripts/vietnamese-ser/pilot_extract.py   video → Demucs → VAD → turn-split → ASR (+pyannote)
scripts/vietnamese-ser/align_youtube.py   caption ↔ segment alignment + ASR quality check
scripts/vietnamese-ser/m4_weak_label.py   dual-teacher labels via Batch API (scale path)
scripts/vietnamese-ser/m4_prompt.md       THE versioned labeling prompt (invariant I2)
kaggle/vietnamese-ser/vnser-extract/      batch extraction kernel (P100, turn-split default on)
```

## The five rules

### 1. Intent before implementation
No result or behavior change starts in `scripts/`/`kaggle/`. It starts in a
`docs/spec/changes/NNN-<slug>/` folder (or — human decision only —
`docs/intent/`): state what it must do, what it must never do, which
`capabilities/*.md` it modifies, and how we'll know. If you can't write the exit
criterion, the intent is underspecified — stop and resolve that first.

### 2. Exit criteria must be executable
Every exit criterion maps to a named check (test, CI gate, or measured metric)
in a **Verification** table. A phase is done when its checks pass — not when the
code looks done. "A measured metric" means a real run with a retained
report/log, not a hoped-for number. (The pilot's implement plans in
`docs/tasks/` with their "Verify trước khi báo xong" sections are the working
example of this rule.)

### 3. Invariants are permanent tests, not phase tasks
The non-negotiables in `docs/intent/invariants.md` (I1–I6) get a permanent
suite that runs on every CI run. A PR that breaks one is wrong by definition —
the fix is the code, unless a human deliberately revises the invariant (edit
`docs/intent/invariants.md` and the test in the same, explicitly-flagged PR).

### 4. Contracts/checks are written red-first
For new behavior: write the check (test / assertion / metric gate) first, then
make it pass. Per-task loop: restate intent → write failing check → implement
minimum → run suite → flip status.

### 5. Intent and code change together, or not at all
If a run reveals the spec was wrong or underspecified, update the capability /
tracking doc **in the same PR** as the code/kernel (worked example: turn-split
v1's zero-net-gain finding → v2 plan + code + tracking-doc update in one PR).
Intent-layer changes are stricter: human decision, explicitly flagged, never
bundled silently.

## What is intentionally NOT derivable from intent

Some decisions are discovered by **measurement**: teacher choice (Opus vs
Sonnet vs both — decided when gold exists, via teacher-vs-gold κ), MIN_UTT
thresholds, Demucs model size, diarization tuning. The intent is the *decision
procedure* — run the comparison, decide on the numbers, land the resolution as
an ADR in `docs/spec/decisions/`.

## Tooling (execution)

`uv` (Python ≥ 3.11), `ruff`; local heavy deps live in the dedicated
`.venv-vnser` (demucs, silero-vad, transformers, pyannote 4.x, soundfile) with
the `sitecustomize.py` torchaudio→soundfile shim (`PYTHONPATH=scripts/vietnamese-ser`).
GPU batch runs use the **pinned Kaggle stack** (`torch==2.5.1+cu121`,
`pyannote.audio==3.*` — note the 3.x `use_auth_token=` API differs from local
4.x `token=`); Kaggle auth at `~/.kaggle/access_token`, account phone-verified.
Windows console: always `PYTHONIOENCODING=utf-8`. `archive/**` is excluded from
lint/CI — it is frozen history, not maintained code. Never pnpm/npm/Biome.
