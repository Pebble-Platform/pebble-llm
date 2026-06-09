# Claude Code Project Instructions

> These instructions are specific to Claude Code and supplement the root `AGENTS.md`.
> For project architecture, coding conventions, commands, and patterns, refer to `AGENTS.md` — it is the single source of truth.

## Quick Reference

- **Package manager**: `pnpm` (never use npm or yarn)
- **Node**: >= 20
- **Linter/Formatter**: Biome (`pnpm lint:fix`, `pnpm format`)
- **Type check**: `pnpm type-check`
- **Unit tests**: `pnpm test:unit`
- **E2E tests**: `pnpm test`
- **DB migrations**: `pnpm db:generate` then `pnpm db:migrate`

## Rules (Claude Code only)

- Do NOT run `pnpm build`, `pnpm dev`, `pnpm install`, or `pnpm add` unless explicitly asked
- After writing or modifying code, run `pnpm lint:fix` and `pnpm type-check` to validate
- All other coding rules are in `AGENTS.md` — do not duplicate them here

## Commit Convention
Format: `type(module): [NA-ticket] summary` — scope always required, ticket ID required for `feat`/`fix`/`refactor`/`perf`/`revert`, optional for `chore`/`docs`/`ci`/`build`/`test`/`pick`.

## Commands

| Command | Purpose |
|---------|---------|
| `/na-plan` | Phase 1 planning workflow — produces `01-spec.md`, `02-tdd.md`, `03-plan.md`, `04-task.md` for a ticket |
| `/na-investigate-bug` | Bug investigation workflow — produces `bug-context.md`, RCA docs, and the 3-doc fix package |

## Skills

| Skill | When to Use |
|-------|-------------|
| `/na-analyze-requirement` | Analyze a raw request → `01-spec.md` (used by `/na-plan`) |
| `/write-phase-plan` | Generate phased roadmap from spec + TDD → `03-plan.md` (used by `/na-plan`) |
| `/na-bug-reproduce` | Capture bug repro + logs → `bug-context.md` (used by `/na-investigate-bug`) |
| `/na-bug-rca` | Root-cause analysis from logs (used by `/na-investigate-bug`) |
| `/na-bug-fix-package` | Produce the 3-doc fix package (used by `/na-investigate-bug`) |
| `/azure-devops-cli` | Manage ADO resources via `az` CLI |
| `/diagram` | Generate Mermaid or ASCII diagrams |
| `/summarize-release` | Generate release summary in `docs/releases/` |
| `/research-paper` | Find papers related to a topic, ranked by closeness to Pebble (agent: `research-paper`) |
| `/analysis-paper` | Score a paper's % overlap with Pebble + pick the best transferable point (agent: `analysis-paper`) |
| `/find-dataset` | Find a paper's dataset, check license/gate, download open ones to `data/external/` (agent: `find-dataset`) |

## Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| `file-guard.js` | PreToolUse | Block access to sensitive files (.env, keys, credentials) |
| `search-before-code.js` | PreToolUse | Remind to search existing patterns before writing code |
| `post-edit-biome.js` | PostToolUse | Auto-format files with Biome after edits |

## Shared Protocols (`.claude/skills/shared/`)

| Protocol | Purpose |
|----------|---------|
| `evidence-based-reasoning-protocol.md` | Mandatory evidence gates for all code claims |
| `understand-code-first-protocol.md` | Read-before-write protocol |
| `design-patterns-quality-checklist.md` | DRY/responsibility layer quality checks |
| `double-round-trip-review-protocol.md` | Two-round review enforcement |

## MCP Servers

The following MCP servers are enabled in `settings.json`:

| Server               | Purpose                                              |
| -------------------- | ---------------------------------------------------- |
| `context7`           | Library documentation lookup — use for up-to-date API references |
| `memory`             | Persistent memory across conversations               |
| `sequential-thinking`| Step-by-step reasoning for complex problems           |

## Code Validation Checklist

Before considering a task complete, verify:

1. **Lint**: `pnpm lint:fix` passes with no errors
2. **Types**: `pnpm type-check` passes with no errors
3. **Tests**: `pnpm test:unit` passes (if tests exist for modified code)
4. **Imports**: All imports use `@/*` alias, no unused imports
5. **Patterns**: Follow existing patterns in `AGENTS.md` (API routes, server actions, components)

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
