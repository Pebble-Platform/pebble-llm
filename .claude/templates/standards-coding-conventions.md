---
title: Coding Conventions
status: {{draft | active}}
creator: {{git user.name}}
last-reviewed: {{YYYY-MM-DD}}
generated-by: /init-project
---

# Coding Conventions

## Table of Contents
- [Summary](#summary)
- [Formatting](#formatting)
- [Naming](#naming)
- [Imports and Module Boundaries](#imports-and-module-boundaries)
- [Type System Strictness](#type-system-strictness)
- [Lint Rules of Note](#lint-rules-of-note)
- [Comment and Documentation Style](#comment-and-documentation-style)
- [Open Questions](#open-questions)

## Summary

<!-- One paragraph. Which tools enforce conventions (prettier, eslint, ruff, etc.) and the overall strictness posture. -->

{{one-paragraph summary}}

## Formatting

| Aspect | Rule | Source |
|--------|------|--------|
| Indent style | {{tabs / spaces}} | {{config file}} |
| Indent size | {{n}} | {{config file}} |
| Line width | {{n}} | {{config file}} |
| Quotes | {{single / double}} | {{config file}} |
| Semicolons | {{required / forbidden / optional}} | {{config file}} |
| Trailing commas | {{all / es5 / none}} | {{config file}} |
| End-of-file newline | {{required / not enforced}} | {{.editorconfig}} |

## Naming

| Symbol kind | Convention | Source |
|-------------|-----------|--------|
| Files | {{kebab-case / PascalCase / snake_case}} | {{example or rule}} |
| Variables / functions | {{camelCase / snake_case}} | {{rule}} |
| Types / classes | {{PascalCase}} | {{rule}} |
| Constants | {{UPPER_SNAKE / camelCase}} | {{rule}} |
| Test files | {{pattern}} | {{example}} |

## Imports and Module Boundaries

- **Order:** {{e.g., builtin -> external -> internal -> parent -> sibling}} ({{source}})
- **Path aliases:** {{list or "none"}} ({{tsconfig or equivalent}})
- **Barrel files:** {{allowed / forbidden}} ({{lint rule or convention}})
- **Cross-layer imports:** {{rule or "none enforced"}}

## Type System Strictness

- {{language}} strictness level: {{strict / standard / loose}} ({{config field}})
- Key flags: {{list of enforced flags}}
- Any intentional relaxations: {{list or "none"}}

## Lint Rules of Note

<!-- Non-obvious lint rules that shape the codebase. Include the
     rule name, what it enforces, and the source config. -->

- `{{rule-name}}` -- {{what it enforces}} ({{config file}})

## Comment and Documentation Style

- **In-code comments:** {{convention -- e.g., "why, not what"}} ({{CONTRIBUTING.md section if any}})
- **Doc comments:** {{JSDoc / docstrings / rustdoc / none}} ({{example path}})
- **Public API docs:** {{tool or "none"}} ({{config or output path}})

## Open Questions

- `[NEEDS CLARIFICATION]` {{question}}
