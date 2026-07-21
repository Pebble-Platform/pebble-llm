# Change 009 — Labeler: multi-select bulk remove (F9 "loại nhiều clip")

**Status:** done (2026-07-18) — backend e2e-verified (isolated tempdir); frontend
node-checked + DOM-stub boot.
**Goal:** let the user **hand-pick several clips on screen and remove them in one
action**. This is the *correct* "loại multi" (loại nhiều = remove multiple) — the
earlier change 007 misread "multi" as multi-speaker and was reverted (see the revert
commit). Redo per user: "chọn các video trên màn hình, và remove 1 lần".

## F9 — multi-select bulk remove

- **Checkbox per row** in the clip table + a **select-all** checkbox in the header.
  Ticking a box adds the clip to the selection (`S.selIds`); the row highlights.
  Row click still opens/previews the clip (checkbox click is `stopPropagation`-ed).
- **Selection bar** above the table: live count, a reason dropdown
  (`other/multi_speaker/noise/bad_cut`), `⚑ loại đã chọn (N)`, and `bỏ chọn`.
- **Remove** = `POST /reject-bulk {ids, reason}` → all selected clips rejected in
  one atomic save (kept on disk, excluded from done/export like F3 — reversible per
  clip via `↺`). Selection is per-episode (cleared on episode switch).

"Remove" is **reject**, not file deletion — the tool never hard-deletes media
(provenance + reversibility, same as F3).

## Design decisions

- **Reuse the reject mechanism + a generic `/reject-bulk {ids, reason}`:** the
  endpoint removed in the 006/007 revert is re-introduced in its minimal form (no
  `dup_source` — that was recap-specific). Bulk reject is the right primitive for
  manual multi-select removal. Rejected: looping `POST /reject` per clip
  (N requests, non-atomic).
- **Checkboxes + select-all (vs shift-click range):** checkboxes are the least
  ambiguous "chọn nhiều" UI and match "chọn các clip trên màn hình"; select-all
  covers "remove everything shown". Row-click stays "open clip".
- **Reason dropdown in the bar (default `other`):** keeps a provenance reason on
  bulk removals without forcing the per-clip detail dropdown.

## File changes (all `tools/labeler/`)

| File | Change |
|---|---|
| `server.py` | `RejectBulkIn {ids, reason}` + `POST /reject-bulk` (minimal) |
| `api.js` | `rejectBulk(k, ids, reason)` |
| `state.js` | `selIds: new Set()` |
| `view.js` | checkbox column + select-all + row `sel` highlight + `updateSelBar`; clear selection on episode switch |
| `actions.js` | `removeSelected` (bulk reject) + `clearSel` |
| `index.html` | selection bar (count + reason + loại/bỏ chọn) + `.sel-bar`/`tr.clip.sel` CSS |
| `main.js` | wire `sel-remove`, `sel-clear` |
| `SPEC.md` | F9 (correct) + REST row + arch date |

## Verify

- **Backend** (`scratchpad/test_bulk2.py`, TestClient, isolated tempdir): 3
  selected clips → one `/reject-bulk` call → all rejected `reason=other`, listing
  `rejected==3`; per-clip `↺` undo reverses; bad clip id → 400. ruff clean.
- **Frontend:** `node --check` all 5 modules; DOM-stub `import("./main.js")` boots
  clean.
- **Op note:** re-adds a backend route (`/reject-bulk`) → **restart `:8000`** +
  reload tab.
- **Caveat:** live checkbox/click interaction needs human browser-drive (repo-wide).

## Relation to the reverted 007

Change 007 ("loại multi" = auto-reject multi-speaker-suspect clips) was a
misunderstanding of the request and was reverted. This change is the intended
feature under the same name.
