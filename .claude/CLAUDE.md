# Pebble-LLM — Ordinal Suicide-Risk research

A **research repo** (Python · `uv` · `ruff`/`mypy`/`pytest`), not a product build.
It asks whether LLM weak labels *honestly* augment a scarce clinical gold set for
**ordinal** suicide-risk classification, and produces an IEEE paper plus the
experiment infrastructure behind it. The single most important constraint:
**gold-holdout — never report a metric trained and evaluated on the same label
source** (within-LLM 0.67 ≠ honest gold 0.385).

> This file is a loader. Full rules: [`WORKFLOW.md`](../WORKFLOW.md).
> It previously described a TypeScript/pnpm/Biome/`AGENTS.md` stack — a
> wrong-project artifact flagged in `README.md`; removed at IDD init. The
> correct Python tooling lives in `WORKFLOW.md` → Tooling.

## How this repo is organized (three-layer intent-driven workflow)

The change discipline for a file is determined by its directory:

| Layer | Path | Change discipline |
|---|---|---|
| Intent | `docs/intent/` | Rarely; explicit human decision only. Never edit as a side effect of a code/spec change. |
| Spec — state | `docs/spec/capabilities/` | Current truth per capability; a behavior/result change updates it in the same PR. |
| Spec — change | `docs/spec/changes/NNN-*/` | One folder per unit of work / experiment round; immutable once shipped. `docs/spec/decisions/` holds ADRs. |
| Execution | `src/pebble_llm/`, `kaggle/`, `scripts/`, `tests/` | Derived; must satisfy the layers above or it doesn't land. |

**Ambiguity escalates up, never gets improvised downward.** If the spec doesn't
answer a question, fix the spec before coding. If it can't answer without knowing
why, a human decides. A number obtained by guessing past a protocol hole is worse
than no number.

## Hard constraints (always binding — full list in `docs/intent/`)

- **Gold-holdout always:** train on weak/LLM labels, evaluate on held-out clinical gold; the pools are disjoint by example.
- **Subject-level integrity:** splits/folds by user, never by post (same user ⇒ same split).
- **Reproducible by construction:** pinned Kaggle stack + fixed seed + multi-fold with std; every headline number traces to a kernel + log.
- **Clinical-data ethics:** suicide-risk corpora are de-identified and **never committed** (`data/**` stays gitignored); provenance documented.
- The invariants in `docs/intent/invariants.md` (I1–I6) are mirrored by the permanent `tests/invariants/` suite; a PR that breaks one is wrong by definition.

## Before working

1. Read `docs/intent/constraints.md` (short) — the constraints that bound any valid result.
2. Read the change folder you're working in under `docs/spec/changes/` — its exit criteria + Verification table are the success criteria.
3. Check the touched files in `docs/spec/capabilities/`; a behavior/result change updates them in the same PR.

## Tooling

`make check` = `ruff` + `mypy` + `pytest` (Python ≥ 3.11, `uv`). GPU runs use the
pinned Kaggle stack — see `WORKFLOW.md` → Tooling. **Never pnpm/npm/Biome.**

## Skills

| Skill | When to Use |
|-------|-------------|
| `/research-paper` | Find papers related to a topic, ranked by closeness to Pebble (agent: `research-paper`) |
| `/analysis-paper` | Score a paper's % overlap with Pebble + pick the best transferable point (agent: `analysis-paper`) |
| `/find-dataset` | Find a paper's dataset, check license/gate, download open ones to `data/<stream>/external/` (agent: `find-dataset`) |
| `/long-task` | Run a long/multi-session task against a living doc at `docs/tasks/<slug>.md`; auto-spawns research on blocking uncertainties (agent: `task-researcher`) |
| `/diagram` | Generate Mermaid or ASCII diagrams |
| `/summarize-release` | Generate release summary in `docs/releases/` |

(Other skills — planning/bug workflows — are surfaced by the harness; they are generic, not tuned to this repo.)

## Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| `file-guard.js` | PreToolUse | Block access to sensitive files (.env, keys, credentials) |
| `search-before-code.js` | PreToolUse | Remind to search existing patterns before writing code |
| `post-edit-biome.js` | PostToolUse | Auto-format on edit (configured globally; Python files format via `ruff`) |

## Shared Protocols (`.claude/skills/shared/`)

| Protocol | Purpose |
|----------|---------|
| `evidence-based-reasoning-protocol.md` | Mandatory evidence gates for all code claims |
| `understand-code-first-protocol.md` | Read-before-write protocol |
| `design-patterns-quality-checklist.md` | DRY/responsibility layer quality checks |
| `double-round-trip-review-protocol.md` | Two-round review enforcement |

## MCP Servers

| Server | Purpose |
|---|---|
| `context7` | Library documentation lookup — up-to-date API references |
| `memory` | Persistent memory across conversations |
| `sequential-thinking` | Step-by-step reasoning for complex problems |

<!-- CODEGRAPH_START -->
## CodeGraph

This project has a CodeGraph MCP server (`codegraph_*` tools) configured. CodeGraph is a tree-sitter-parsed knowledge graph of every symbol, edge, and file. Reads are sub-millisecond and return structural information grep cannot.

### When to prefer codegraph over native search

Use codegraph for **structural** questions — what calls what, what would break, where is X defined, what is X's signature. Use native grep/read only for **literal text** queries (string contents, comments, log messages) or after you already have a specific file open.

| Question | Tool |
|---|---|
| "Where is X defined?" / "Find symbol named X" | `codegraph_search` |
| "What calls function Y?" | `codegraph_callers` |
| "What does Y call?" | `codegraph_callees` |
| "How does X reach/become Y? / trace the flow from X to Y" | `codegraph_trace` (one call = the whole path, incl. callback/React/JSX dynamic hops) |
| "What would break if I changed Z?" | `codegraph_impact` |
| "Show me Y's signature / source / docstring" | `codegraph_node` |
| "Give me focused context for a task/area" | `codegraph_context` |
| "See several related symbols' source at once" | `codegraph_explore` |
| "What files exist under path/" | `codegraph_files` |
| "Is the index healthy?" | `codegraph_status` |

### Rules of thumb

- **Answer directly — don't delegate exploration.** For "how does X work" / architecture questions, answer with 2-3 codegraph calls: `codegraph_context` first, then ONE `codegraph_explore` for the source of the symbols it surfaces. For a specific **flow** ("how does X reach Y") start with `codegraph_trace` from→to — one call returns the whole path with dynamic hops bridged — then ONE `codegraph_explore` for the bodies; don't rebuild the path with `codegraph_search` + `codegraph_callers`. Codegraph IS the pre-built index, so spawning a separate file-reading sub-task/agent — or running a grep + read loop — repeats work codegraph already did and costs more for the same answer.
- **Trust codegraph results.** They come from a full AST parse. Do NOT re-verify them with grep — that's slower, less accurate, and wastes context.
- **Don't grep first** when looking up a symbol by name. `codegraph_search` is faster and returns kind + location + signature in one call.
- **Don't chain `codegraph_search` + `codegraph_node`** when you just want context — `codegraph_context` is one call.
- **Don't loop `codegraph_node` over many symbols** — one `codegraph_explore` call returns several symbols' source grouped in a single capped call, while each separate node/Read call re-reads the whole context and costs far more.
- **Index lag**: the file watcher debounces ~500ms behind writes; don't re-query immediately after editing a file in the same turn.

### If `.codegraph/` doesn't exist

The MCP server returns "not initialized." Ask the user: *"I notice this project doesn't have CodeGraph initialized. Want me to run `codegraph init -i` to build the index?"*
<!-- CODEGRAPH_END -->
