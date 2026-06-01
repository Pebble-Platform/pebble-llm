# Domain Docs Handling

Step 2 of the skill must ground the spec in whatever business documentation already exists. This is where past decisions, constraints, and adjacent requirements come from.

Read `standards/README.md` and look for the **Domain docs** field, then follow the matching path.

## Path A -- Domain docs path IS configured

1. **MUST fetch/read the domain docs.** URL -> use `WebFetch`. Local path -> use `Read`. Do NOT skip -- it is compulsory when a path is configured.
2. From the docs, identify how the raw idea fits into the existing business landscape.
3. Note existing requirements, constraints, or decisions that relate to the new idea.
4. Surface gaps: what do the docs NOT tell us that the new spec needs?
5. **STOP if configured but unreadable.** Report the error to the user instead of proceeding without context.

## Path B -- Domain docs path is NOT configured

1. Ask the user via `AskUserQuestion`:

   > "No business documentation path is configured in standards. Do you have existing business documentation for this project? If so, provide the path (local directory/file or URL)."

2. **If the user provides a path** -- fetch/read the docs (URL via `WebFetch`, local via `Read`), then continue with Path A steps 2-5.
3. **If the user says no, skips, or says "go ahead"** -- treat as a **greenfield project**. Skip the context phase entirely. Record the assumption in the spec:

   > `OQ-XXX: No existing business documentation provided. Treated as greenfield project -- requirements written without prior system context.`

## Hard rule -- what you may and may not read

**Allowed inputs for this phase:**

- Domain docs (the path from `standards/README.md` or provided by the user)
- Existing `spec/*/spec.md` feature briefs (Part 1: Business Context only -- this is how Step 1 picks the parent feature)
- `standards/README.md` and `standards/folder-standards.md` (for the slug casing convention)
- User answers via `AskUserQuestion`
- Web research via `WebSearch` / `WebFetch` when justified

**NOT allowed:**

- Source code, test files, migrations, configs
- `spec/*/code_context.md` -- Part 2 (Coding Context) is derived from code with `file:line` citations; treat it as code, not spec
- Directory listings or glob/grep results that reveal code structure
- Sub-agent dispatches that investigate code (Explore, etc.)

Codebase and `code_context.md` exploration belong in Phase 2 (`/design-solution`). If you catch yourself wanting to read a file path or citation, stop -- that signal belongs to a later phase.
