---
title: {{Feature Name}}
slug: {{feature-slug}}
kind: feature-brief
status: {{draft | active | deprecated}}
owner: {{team or person}}
last-reviewed: {{YYYY-MM-DD}}
generated-by: /init-project
---

# {{Feature Name}} -- Feature Brief (Part 1: Business Context)

<!-- **What this document is**: an orientation artifact for an existing feature.
     Business Context (Part 1) only. Zero file paths, class names, or code
     jargon. A non-technical reader should get their bearings here. Paired
     with `code_context.md` in the same folder for dev-facing Part 2
     (Coding Context).

     **What this document is NOT**: a normative delivery spec. It does not
     carry REQ/AC IDs and it is not the approval criterion for a change.
     Per-change normative specs are produced by `/analyze-business-requirements`
     and live under `spec/{feature-slug}/{subfeature-slug}/spec.md`.

     **When to update it**: when the feature's scope or boundaries change
     materially. `/verification` updates this file automatically when a
     sub-feature ships and introduces new user outcomes. -->

## Table of Contents
- [Business Context](#business-context)
- [Dependencies](#dependencies)
- [Open Questions](#open-questions)

## Business Context

<!-- For non-technical readers. Product, support, leadership, a new PM
     should be able to read this without asking a developer to translate.
     ZERO file paths, class names, framework names, or code jargon.
     If you cannot describe it this way, ask the feature owner -- do NOT
     back-fill from code. -->

**What it does:**
<!-- 2-4 sentences in plain language. -->
{{what}}

**Who it serves:**
<!-- Named user type(s), persona(s), or internal role(s). -->
{{who}}

**Why it exists:**
<!-- The problem, gap, or opportunity this feature addresses. -->
{{why}}

**Boundaries:**
<!-- What this feature does NOT do. Helps prevent scope creep
     and misattribution of bugs. -->
- In: {{what is included}}
- Out: {{what is explicitly excluded}}

**On ambiguity:**
<!-- What an agent or contributor should do when the brief does not
     cover a case. Default for orientation docs is "Halt and ask the
     feature owner"; override to "Conservative interpretation" or
     "Closest matching rule" only when the feature owner has explicitly
     said so. -->
{{Halt and ask | Conservative interpretation | Closest matching rule}}

**Key user outcomes:**
<!-- Observable outcomes a non-tech reader can verify. -->
- {{outcome 1}}
- {{outcome 2}}

## Dependencies

<!-- The web between features. Populate from scan + user review; leave
     empty buckets as "none" rather than deleting them. -->

**Depends on features:**
<!-- Other feature briefs this one assumes. Link to the sibling feature's
     spec.md via a relative path. -->
- `{{../{other-feature}/spec.md}}` -- {{one-line reason}}

**Inherits standards:**
<!-- Project standards actively enforced on this feature's code.
     Only list the standards whose rules apply here. -->
- `{{../../standards/coding-conventions.md}}`
- `{{../../standards/unit-test-strategy.md}}`

**Declared overrides:**
<!-- Any standard this feature deviates from, with justification. -->
- {{standard path}}: {{what is overridden}} -- {{why}}

## Open Questions

- `[NEEDS CLARIFICATION]` {{question}}
