# Changes — units of work (spec layer)

Every unit of work — a feature, a redesign, a bugfix big enough to plan — is a
numbered folder here: `NNN-<slug>/`. The initial build is simply change `001`;
its "phases" are its task breakdown. After 001 ships, the project evolves by
units of work (e.g. a new contribution, a new baseline, a new dataset), and each
gets the same discipline the initial build got.

A change folder describes **a delta**; the current truth always lives in
`../capabilities/`. Change folders are never edited after shipping — they are
the audit trail of how the system got here.

> **Research note:** in this repo a "unit of work" is often an *experiment round*
> that produces a paper-relevant number. The bar that does not scale down still
> applies: **exit criteria mapped to executable checks** (a kernel that runs, a
> metric with reported std, a test that stays green) and the **capability delta
> named explicitly**.

## Anatomy of a change

```
changes/NNN-<slug>/
├── README.md          # status, goal, intent constraints it touches
├── proposal.md        # requirements + capability delta (ADDED / MODIFIED / REMOVED)
├── tasks.md           # breakdown with exit criteria + Verification table
└── (large changes may split tasks into multiple files, like 001's phase-*.md)
```

Small change → `proposal.md` and `tasks.md` may be one file.

## Lifecycle

```
proposed → in progress → shipped
```

1. **Proposed:** write the folder; name which `capabilities/*.md` it will modify
   and how. An intent-layer change is a human decision first (WORKFLOW.md).
2. **In progress:** implement per tasks, red-first (rule 4).
3. **Shipped:** the *same PR* that completes the change updates the affected
   `capabilities/*.md` to present tense (rule 5 + CI spec-gate); the folder's
   status flips to `shipped` and is thereafter immutable.

## Index

| # | Change | Status |
|---|---|---|
| [001](001-initial-build/README.md) | Honest gold-holdout ordinal suicide-risk study (IEEE Bài 1) + its infrastructure | in progress |
