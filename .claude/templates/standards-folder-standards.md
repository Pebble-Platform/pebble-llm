---
title: Folder Standards
status: {{draft | active}}
creator: {{git user.name}}
last-reviewed: {{YYYY-MM-DD}}
generated-by: /init-project
---

# Folder Standards

## Table of Contents
- [Summary](#summary)
- [Organization Principle](#organization-principle)
- [Top-Level Layout](#top-level-layout)
- [Source Tree Conventions](#source-tree-conventions)
- [Test Layout](#test-layout)
- [Assets and Static Files](#assets-and-static-files)
- [Docs and Metadata](#docs-and-metadata)
- [Where Things Belong](#where-things-belong)
- [Agent-Operable Infrastructure](#agent-operable-infrastructure)
- [Open Questions](#open-questions)

## Summary

<!-- One paragraph. Organization style (by layer / by feature / by domain),
     source root location, and any monorepo structure. -->

{{one-paragraph summary}}

## Organization Principle

- **Style:** {{by-layer / by-feature / by-domain / flat / hybrid}}
- **Reasoning signal:** {{cited folder structure that supports this}}
- **Monorepo:** {{yes -- tool: pnpm/turbo/nx/lerna | no}}

## Top-Level Layout

<!-- List observed top-level directories with their purpose. -->

| Path | Purpose |
|------|---------|
| `{{dir}}` | {{what lives here}} |

## Source Tree Conventions

- **Source root:** {{src/ / app/ / lib/ / packages/*/}}
- **Module boundaries:** {{rule, e.g., "no cross-feature imports except via shared/"}}
- **Shared code location:** {{path or "none"}}
- **Public API surface (if lib):** {{entry file}}

## Test Layout

- **Location:** {{co-located / tests/ / spec/ / __tests__/}}
- **Mirror pattern:** {{yes / no}}
- **Fixtures:** {{path}}

## Assets and Static Files

- **Static assets:** {{path or "none"}}
- **Generated artifacts:** {{path that is git-ignored}}

## Docs and Metadata

- **Documentation root:** {{docs/ or other}}
- **Architecture docs:** {{path or "none"}}
- **ADRs:** {{path or "none"}}
- **Specs produced by this workflow:** `spec/{feature}/` (feature hierarchy). Each feature folder holds `spec.md` (Part 1: Business Context) + `code_context.md` (Part 2: Coding Context). Per-change work lands in sub-feature folders `spec/{feature}/{subfeature}/` with their own `spec.md`, `plan.md`, and `tasks.md`.
- **Sub-feature slug casing:** {{kebab-case | snake_case}} -- stable; a later bug fix on the same sub-feature reuses the folder rather than creating a new one. Default is kebab-case if this field is absent.

## Where Things Belong

<!-- Quick lookup table so new contributors can place new code without
     asking. Limit to 8-12 rows -- avoid bureaucracy. -->

| If you are adding... | Put it under... |
|----------------------|-----------------|
| A new feature | {{path}} |
| A shared utility | {{path}} |
| A new API endpoint | {{path}} |
| A database migration | {{path}} |
| A new test | {{path}} |
| A new config | {{path}} |

## Agent-Operable Infrastructure

<!-- The parts of the repo that act as operational memory for agents --
     see guide Section 7.1 "Repository knowledge as agent-operable
     infrastructure." Flag which pieces exist so downstream skills know
     what they can rely on. -->

| Capability | Present? | Path / source |
|------------|----------|---------------|
| Agent instruction file (CLAUDE.md / AGENTS.md) | {{yes / no}} | {{path}} |
| Indexed documentation (README.md, docs/) | {{yes / no}} | {{path}} |
| ADRs (architectural decision records) | {{yes / no}} | {{path or "none"}} |
| Generated API / schema reference | {{yes / no}} | {{path or tool}} |
| Dev-server / reproducer command | {{yes / no}} | {{command}} |

## Open Questions

- `[NEEDS CLARIFICATION]` {{question}}
