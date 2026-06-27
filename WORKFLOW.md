# Intent-Driven Workflow for Pebble-LLM (Ordinal Suicide-Risk research)

How we work on this repo. This is a **research program**: the output is a
defensible IEEE paper plus the experiment infrastructure behind it, and the
governing question is whether LLM weak labels *honestly* augment scarce clinical
gold labels for ordinal suicide-risk classification.

## The three layers

| Layer | Holds | Changes | In this repo |
|---|---|---|---|
| **Intent** | Why the project exists; research-validity & ethics constraints; the never-list | Rarely; only by deliberate human decision, never as a side effect of implementation | `docs/intent/` (`constraints.md`, `invariants.md`) |
| **Spec** | The current best solution, split into **state** and **change** | Living; updated whenever a result or learning changes — in the same PR as the code/kernel (rule 5) | `docs/spec/capabilities/` (current truth), `docs/spec/changes/` (units of work / experiment rounds), `docs/spec/decisions/` (ADRs); seed docs `PAPER-PLAN-text-ordinal-suicide.md`, `pebble-finetuning-strategy-v3.md` (absorbed by capabilities) |
| **Execution** | Fully determined work: code, kernels, tests, invariant suite | Derived from the spec; nothing left to guess *that a check wouldn't catch* | `src/pebble_llm/`, `kaggle/`, `scripts/`, `tests/` |

The escalation rule that makes the layering work: **ambiguity escalates up, it
is never resolved downward by improvisation.** If execution hits a question the
spec doesn't answer, that's a spec hole — fix the spec first. If the spec can't
answer without knowing *why*, that's an intent question — a human decides. A
plausible guess filling a spec hole is the failure mode this structure exists to
exclude. (In research terms: a number obtained by guessing past a protocol hole
is worse than no number.)

"No guessing" at the execution layer is achieved by **verification, not
exhaustive prose**: micro-decisions remain, but nothing that matters can be
wrong without a check going red.

```
docs/intent/constraints.md       why + the constraints bounding any valid result
docs/intent/invariants.md        the never-list, mirrored by tests/invariants/
docs/spec/capabilities/          CURRENT TRUTH — what each capability does now
docs/spec/changes/NNN-<slug>/    units of work: proposal + tasks/phases + verification (001 = the IEEE Bài-1 study)
docs/spec/decisions/             ADRs — resolved-on-evidence decisions, append-only
PAPER-PLAN / strategy-v3         seed design; shrinks as capabilities absorb it
src/pebble_llm/, kaggle/, tests/ derived output — satisfies the above or it doesn't land
```

The state/change split keeps the spec layer alive past the initial build:
`capabilities/` always answers "what does the system do?", a new experiment round
or feature is the next `changes/NNN-<slug>/` folder, and shipping a change means
updating the touched capability files in the same PR.

## Execution-layer layout

```
src/pebble_llm/            data/ models/ training/ evaluation/ serving/ utils/
kaggle/finetuning-message/ Kaggle kernels (the GPU experiment runs)
scripts/                   prepare/run/eval/export entry points
tests/                     unit tests
tests/invariants/          permanent suite mirroring docs/intent/invariants.md (created in change 001 phase 0)
```

Output contract: `src/pebble_llm/serving/schemas.py` (the `/classify` shape, when
serving is revived) and the evaluation-protocol module (the honest framing).

## The five rules

### 1. Intent before implementation
No result or behavior change starts in `src/`/`kaggle/`. It starts in a
`docs/spec/changes/NNN-<slug>/` folder (or — human decision only —
`docs/intent/`): state what it must do, what it must never do, which
`capabilities/*.md` it modifies, and how we'll know. If you can't write the exit
criterion, the intent is underspecified — stop and resolve that first.

### 2. Exit criteria must be executable
Every exit criterion maps to a named check (test, CI gate, or measured metric
with reported std) in a **Verification** table in the phase/tasks file. A phase
is done when its checks pass — not when the code looks done. For research, "a
measured metric" means a real run with a retained log, not a hoped-for number.

### 3. Invariants are permanent tests, not phase tasks
The non-negotiables in `docs/intent/invariants.md` (I1–I6) live in
`tests/invariants/` and run on every CI run forever. A PR that breaks one is
wrong by definition — the fix is the code, unless a human is deliberately
revising the invariant itself (edit `docs/intent/invariants.md` and the test in
the same, explicitly-flagged PR).

### 4. Contracts/checks are written red-first
For new behavior: write the check (test / disjointness assertion / metric gate)
first, then make it pass. The per-task loop:

```
1. Read the phase file; restate intent + assumptions   → confirm nothing is ambiguous
2. Write/extend the failing check                       → red
3. Implement the minimum                                → green
4. Run invariant suite + relevant tests                 → still green
5. Flip the phase-file status / check off the criterion
```

### 5. Intent and code change together, or not at all
If a run reveals the spec was wrong or underspecified, update the phase
file/capability **in the same PR** as the code/kernel. A number quietly recorded
in a report but diverging from the written spec reintroduces doc rot. Intent-layer
changes are stricter: human decision, explicitly flagged, never bundled silently.

## Enforcing rule 5: preventing silent spec drift

1. **Prefer checks over prose.** A behavior encoded as a test, disjointness
   assertion, or metric gate cannot silently drift. When extending the spec, ask:
   can this be a check instead of a paragraph?
2. **CI spec-gate** (build in phase 0): a PR touching `src/**` or `kaggle/**`
   fails unless it also touches `docs/spec/capabilities/**` OR carries an explicit
   `Spec-Impact: none` trailer. Targets capabilities/, not all of docs/spec/ —
   task-list edits in changes/ are progress tracking, not truth maintenance.
3. **Semantic diff review:** a PR review step asking "given this diff, which
   statements in the relevant `docs/spec/` sections are now false?"
4. **Scheduled drift audit:** periodically walk capabilities section by section
   and verify each claim against the code/runs; findings become fix-the-spec PRs.

## What is intentionally NOT derivable from intent

Some decisions are discovered by **measurement**, not specified up front:
encoder choice (MentalRoBERTa vs gated/NeoBERT), loss family (CORN+GCE vs flat-CE
vs dual-CORAL), whether class rebalance helps. For these the intent is the
*decision procedure* ("run the ablation on a common split, decide on the
numbers") — the phase files record the criterion, the measurement decides, and
the resolution lands as an ADR in `docs/spec/decisions/`.

## Tooling (execution)

`uv` (Python ≥ 3.11), `ruff`, `mypy`, `pytest`. `make check` = lint + type +
test. GPU runs use the **pinned Kaggle stack** (`torch==2.5.1` /
`torchvision==0.20.1` / `torchaudio==2.5.1` / `xformers==0.0.28.post3` /
`transformers==4.48.2`); the Kaggle token is at `~/.kaggle/access_token` and the
account must be phone-verified for GPU+Internet. Never use pnpm/npm/Biome — the
old `.claude/CLAUDE.md` mention of a TypeScript stack was a wrong-project
artifact and has been removed.
