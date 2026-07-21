# docs/spec/decisions — ADRs (post-pivot)

Mỗi quyết định kiến trúc/phương pháp không tự suy ra được từ code = một ADR
`ADR-NNN-<slug>.md` (bất biến sau khi `accepted`; đánh số lại từ 001 sau pivot
2026-07-04 — chuỗi cũ ở `archive/docs/spec/decisions/`).

Format: `## ADR-NNN — <title>` · **Date/Status** · **Resolves** · **Context** ·
**Decision** · **Evidence** · **Consequences**.

| ADR | Chủ đề | Status |
|---|---|---|
| [ADR-001](ADR-001-blind-gold-annotation.md) | Gold annotation mù teacher (không pre-fill nhãn LLM) | superseded bởi ADR-003 |
| [ADR-002](ADR-002-whole-series-speaker-disjoint-gold.md) | Speaker-disjoint theo whole-series (test vs train) | proposed |
| [ADR-003](ADR-003-human-labels-drop-weak-supervision.md) | Bỏ weak-supervision — nhãn human là nguồn sự thật | accepted (intent edits chờ apply) |
| [ADR-004](ADR-004-labeler-state-durability.md) | Độ bền/khôi phục label DB (lock + backup xoay vòng → SQLite; git-version để ngỏ) | proposed (chưa build) |
