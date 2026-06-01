---
title: Unit Test Strategy
status: {{draft | active}}
creator: {{git user.name}}
last-reviewed: {{YYYY-MM-DD}}
generated-by: /init-project
---

# Unit Test Strategy

## Table of Contents
- [Summary](#summary)
- [Frameworks and Tools](#frameworks-and-tools)
- [Test Layout](#test-layout)
- [Naming and Structure](#naming-and-structure)
- [Coverage](#coverage)
- [Mocking and Fixtures](#mocking-and-fixtures)
- [Test Scopes](#test-scopes)
- [CI Integration](#ci-integration)
- [Harness Surface](#harness-surface)
- [Open Questions](#open-questions)

## Summary

<!-- One paragraph. The testing posture today -- framework, scope split,
     coverage expectations. Describe reality, not aspiration. -->

{{one-paragraph summary}}

## Frameworks and Tools

| Tool | Version | Purpose | Source |
|------|---------|---------|--------|
| {{framework}} | {{version}} | {{unit / integration / e2e}} | {{dep file}} |
| {{coverage tool}} | {{version}} | Coverage reporting | {{dep file}} |

## Test Layout

- **Layout style:** {{co-located / parallel tree / separate root}}
- **Test directories:** {{list of paths}}
- **Example mapping:** `{{source-path}}` -> `{{test-path}}`

## Naming and Structure

- **Filename pattern:** {{e.g., `*.test.ts`, `test_*.py`, `*_test.go`}}
- **Test function / describe naming:** {{convention with one example}}
- **Arrange-Act-Assert discipline:** {{enforced / convention / not enforced}}

## Coverage

- **Tool:** {{name}}
- **Command:** {{exact command, e.g., `npm run test:coverage`}}
- **Threshold:** {{percent or "none set"}} ({{config source}})
- **Excluded paths:** {{list or "none"}}

## Mocking and Fixtures

- **Mocking library:** {{name or "built-in / none"}} ({{example usage}})
- **Fixture location:** {{path or "inline"}}
- **Factories:** {{library or convention or "none"}}
- **Test data seeds:** {{approach or "none"}}

## Test Scopes

| Scope | Framework | Location | Run command |
|-------|-----------|----------|-------------|
| Unit | {{framework}} | {{path}} | {{command}} |
| Integration | {{framework or "none"}} | {{path}} | {{command}} |
| End-to-end | {{framework or "none"}} | {{path}} | {{command}} |

## CI Integration

- **Workflow:** {{path to CI file}}
- **Triggers:** {{e.g., PR + push to main}}
- **Required to merge:** {{yes / no}} ({{source}})

## Harness Surface

<!-- Can an agent run, observe, and verify the system? Record what
     currently exists; mark missing pieces so a future harness-building
     pass knows where to start. See guide Section 7 -- Harness Engineering. -->

| Capability | Present? | Evidence |
|------------|----------|----------|
| Run test suite by command | {{yes / no / [NEEDS CLARIFICATION]}} | {{command + source}} |
| Run a single test | {{yes / no}} | {{command}} |
| Run with coverage | {{yes / no}} | {{command}} |
| Lint enforcement on commit | {{yes / no}} | {{.husky/ or CI config}} |
| Type-check gate | {{yes / no}} | {{CI job or script}} |
| Observable logs (structured) | {{yes / no / unknown}} | {{logger config or example}} |
| Observable metrics / traces | {{yes / no / unknown}} | {{instrumentation package}} |

## Open Questions

- `[NEEDS CLARIFICATION]` {{question}}
