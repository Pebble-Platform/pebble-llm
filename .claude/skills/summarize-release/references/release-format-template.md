# Release File Format Template

Output file: `docs/releases/{version}.md`

## Structure

```markdown
# Release {version}

**Release Date:** YYYY-MM-DD

---

## Bug Fixes

### {Area} — {Short Problem Description}

> **Docs:** [bug report](../bugs/{area}/bug-file.md) | [bugfix plan](../bugs/{area}/bugfix-plan.md)

- {What was fixed, in business terms}
- {Another fix item}

### {Area} — {Another Bug} ({ticket-id})

> **Docs:** [bug report](../bugs/{area}/bug.md) | [bugfix plan](../bugs/{area}/bugfix-plan.md)

- {Fix description}

---

## Features

### {Feature Name}

> **Docs:** [requirement](../features/{slug}/requirement.md) | [solution](../features/{slug}/solution.md)

- {What was added}
- {Another addition}

---

## Other Changes

### Infrastructure

- {Infra change}

### Dependencies

- {Dependency change}
```

## Rules

1. **Only include sections that have content** — if no features, omit the Features section entirely
2. **Subsection headings** use format: `### {Area} — {Problem/Feature Description}`
3. **Doc links** use relative paths from `docs/releases/` (e.g. `../bugs/`, `../features/`)
4. **Ticket IDs** go in the heading when available: `### MCP Integration — Toggle Instability (NA-1352)`
5. **Merge small items** — avoid single-bullet subsections. Group under broader headings like Infrastructure or Dependencies
6. **Business language** — describe what changed for users, not implementation details
7. **No code references** in bullet points (no function names, file paths, variable names)

## Real Example (v0.3.5)

```markdown
### Workspace — File Upload Fails at Model Call Time

> **Docs:** [bug report](../bugs/workspace/bug-handle-file-upload.md) | [bugfix plan](../bugs/workspace/bugfix-plan.md)

- Add conversation file retrieval alongside workspace knowledge base retrieval
- Synchronize workspace agent with default agent for tools and step orchestration
- Add workspace capability-controlled tools: Web Search, Canvas, Image Generation
- Update system prompt with retrieval context for tool disambiguation
- Update knowledge base search UI status for clear distinction from file retrieval
```
