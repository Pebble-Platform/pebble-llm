---
title: Git Branching Strategy
status: {{draft | active}}
creator: {{git user.name}}
last-reviewed: {{YYYY-MM-DD}}
generated-by: /init-project
---

# Git Branching Strategy

## Table of Contents
- [Summary](#summary)
- [Primary Strategy](#primary-strategy)
- [Branches](#branches)
- [Feature Branch Naming](#feature-branch-naming)
- [Merge Style](#merge-style)
- [Commit Convention](#commit-convention)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)
- [Hotfix Path](#hotfix-path)
- [Open Questions](#open-questions)

## Summary

<!-- One paragraph. Name the strategy (trunk-based, GitHub Flow, Git Flow,
     GitLab Flow, custom) and how work flows from branch creation to
     deployed. -->

{{one-paragraph summary}}

## Primary Strategy

- **Strategy:** {{name}}
- **Evidence:** {{cited signals that classify it}}

## Branches

| Branch | Role | Protected? | Source |
|--------|------|------------|--------|
| {{e.g., main}} | {{deployable / integration / release}} | {{yes / no}} | {{CI config or rule}} |

## Feature Branch Naming

- **Pattern:** {{e.g., `feat/<short-desc>`, `<ticket-id>-<desc>`}}
- **Examples:** {{2-3 real examples from current branches}}

## Merge Style

- **Default merge mode:** {{merge commit / squash / rebase}} ({{source}})
- **Rebase expectation before merge:** {{required / preferred / not enforced}}

## Commit Convention

- **Style:** {{Conventional Commits / free-form / ticket-prefixed}}
- **Enforcement:** {{commitlint / pre-commit hook / none}} ({{config file}})
- **Example good commit:** `{{example}}`

## Pull Request Process

- **Review requirement:** {{n approvers, team rules}} ({{CODEOWNERS or branch protection}})
- **Required checks:** {{list of CI jobs gating merge}}
- **PR template:** {{path to template or "none"}}

## Release Process

- **Tag pattern:** {{e.g., `v1.2.3`}}
- **Automation:** {{semantic-release / release-please / manual}}
- **Changelog:** {{path or "none"}}
- **Release cadence:** {{continuous / weekly / on-demand / unknown}}

## Hotfix Path

- **Procedure:** {{documented steps or "none documented"}}

## Open Questions

- `[NEEDS CLARIFICATION]` {{question}}
