---
title: {{Feature Name}} -- Code Context
slug: {{feature-slug}}
kind: code-context
status: {{draft | active | deprecated}}
owner: {{team or person}}
last-reviewed: {{YYYY-MM-DD}}
generated-by: /init-project
---

# {{Feature Name}} -- Code Context (Part 2)

<!-- **What this document is**: the dev-facing companion to `spec.md` in
     the same folder. Every claim below cites a real file path (with line
     numbers where useful). A developer implementing, extending, or
     debugging this feature should read `spec.md` first (what / who / why)
     and then this file (how the code is laid out).

     **When to update it**: when the feature's entry points, data flow,
     or core modules change materially. `/verification` refreshes only
     the affected sections when a sub-feature ships; other sections stay
     untouched.

     **Unknowns stay `[NEEDS CLARIFICATION]` -- never invent file paths.** -->

## Table of Contents
- [Evidence Confidence](#evidence-confidence)
- [Entry Points](#entry-points)
- [Core Modules](#core-modules)
- [Data Flow](#data-flow)
- [Key Dependencies](#key-dependencies)
- [Seams](#seams)
- [Extension Points](#extension-points)
- [Known Gotchas](#known-gotchas)
- [Related Tests](#related-tests)
- [Open Questions](#open-questions)

## Evidence Confidence

<!-- Rank the sources that back the statements below. Options:
       - `runtime-verified`  -- statements confirmed by running the code
       - `structural`        -- derived from reading the code
       - `institutional`     -- derived from docs or feature owner interview
     Default for a fresh scan: "structural + institutional (code read;
     no runtime check)". Upgrade to `runtime-verified` after a user
     confirms a test or flow was run against the claims. -->

{{structural + institutional (code read; no runtime check)}}

## Entry Points

<!-- The files a developer should open first to understand or modify
     this feature. Include role per entry. -->

- `{{path/to/file.ext}}` -- {{role, e.g., HTTP route handler}}
- `{{path/to/file.ext}}` -- {{role}}

## Core Modules

<!-- The files that implement the feature's behavior. -->

| Path | Responsibility |
|------|----------------|
| `{{path}}` | {{what it does}} |

## Data Flow

<!-- 2-5 numbered steps. Each step cites a file:line where the transition
     happens. This is the single most valuable field for onboarding. -->

1. {{step -- `file:line`}}
2. {{step -- `file:line`}}
3. {{step -- `file:line`}}

## Key Dependencies

- Internal services: {{list or "none"}}
- External libraries: {{list with versions where relevant}}
- Environment variables: {{list or "none"}}

## Seams

<!-- For features with cross-module or external integrations, name the
     contracts. For internal-only features, write "not applicable" rather
     than deleting the section, so the file shape is uniform across
     features. Format per seam:
       {seam name}: {interface shape} -- {contract} -- {assumption about the other side} -->

- {{seam-name}}: {{interface}} -- {{contract}} -- {{assumption}}

## Extension Points

<!-- Where new behavior is typically added. If the feature has plugin
     hooks, config flags, or strategy slots, name them here. -->

- {{extension description -- `file:line`}}

## Known Gotchas

<!-- Non-obvious constraints, prior bugs worth remembering, invariants
     that must hold. Each entry should be concrete and actionable. -->

- {{gotcha with `file:line` if relevant}}

## Related Tests

<!-- Paths to the tests covering this feature. Include coverage gaps
     if obvious. -->

- `{{path/to/test}}` -- {{what it covers}}

## Open Questions

- `[NEEDS CLARIFICATION]` {{question}}
