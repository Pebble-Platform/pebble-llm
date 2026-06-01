---
title: Tech Stack
status: {{draft | active}}
creator: {{git user.name}}
last-reviewed: {{YYYY-MM-DD}}
generated-by: /init-project
---

# Tech Stack

## Table of Contents
- [Summary](#summary)
- [Languages and Runtimes](#languages-and-runtimes)
- [Frameworks](#frameworks)
- [Data Layer](#data-layer)
- [Build and Tooling](#build-and-tooling)
- [Infrastructure and Deployment](#infrastructure-and-deployment)
- [External Services](#external-services)
- [Open Questions](#open-questions)

## Summary

<!-- One paragraph, max 4 sentences. What this project is, the top-level stack in plain language. No jargon a non-tech reader cannot parse. -->

{{one-paragraph summary}}

## Languages and Runtimes

| Language | Version | Source of truth |
|----------|---------|-----------------|
| {{Language}} | {{version}} | {{file:line or field}} |

## Frameworks

| Framework | Version | Role | Source of truth |
|-----------|---------|------|-----------------|
| {{Framework}} | {{version}} | {{e.g., web server / UI / ORM}} | {{file:line}} |

## Data Layer

- **Primary database:** {{name + version}} ({{source}})
- **ORM / data-access:** {{name + version}} ({{source}})
- **Cache:** {{name or "none"}} ({{source}})
- **Queue / message bus:** {{name or "none"}} ({{source}})
- **Search / analytics:** {{name or "none"}} ({{source}})

## Build and Tooling

- **Package manager:** {{manager + version}} ({{lockfile}})
- **Bundler / compiler:** {{tool + version}} ({{config file}})
- **Task runner:** {{npm scripts / make / just / nx / turbo}} ({{source}})
- **Type checker:** {{tsc / mypy / ruff / none}} ({{config}})

## Infrastructure and Deployment

- **CI:** {{GitHub Actions / GitLab CI / other}} ({{workflow path}})
- **Container runtime:** {{Docker / none}} ({{Dockerfile path}})
- **Hosting target:** {{Vercel / Fly / AWS / self-hosted}} ({{config file}})
- **IaC:** {{Terraform / Pulumi / none}} ({{config file}})

## External Services

<!-- Third-party APIs and SaaS dependencies the app calls at runtime.
     Cite the env var name or SDK dep that proves the integration exists. -->

| Service | Purpose | Source of truth |
|---------|---------|-----------------|
| {{Service}} | {{what it is used for}} | {{env var or dep}} |

## Open Questions

<!-- Everything the scan could not resolve. Leave as-is if unresolved;
     re-run /init-project later to refresh. -->

- `[NEEDS CLARIFICATION]` {{question}}
