# Labeler — excise middle chunk + click-to-seek

- **Slug:** labeler-excise-seek
- **Status:** done
- **Created:** 2026-07-18  ·  **Updated:** 2026-07-18
- **Owner:** phat / agent

## Goal
Add two features to `tools/labeler/` (human labeling UI + FastAPI backend):
1. **Excise a middle chunk** — select a noisy region `[a,b]` inside a clip and
   remove it, concatenating `[0,a]+[b,dur]` into **one** clip (NOT split in two).
2. **Click-to-seek** — click anywhere on the waveform (in normal mode) to move
   the playhead there, so playback starts from the chosen position instead of the
   beginning.
Done = both work end-to-end, audio ops are atomic + undoable, provenance honest,
SPEC/SPEC-features updated, `make check` green.

## Requirements & Constraints
- **Functional:**
  - Excise keeps the clip as a single `seg*.wav`; removed region is gone from
    audio but **recorded** in `state.jsonl` (`excised` list) — nothing silently
    lost. Reuses `_orig/` backup so `↩ gốc` fully restores.
  - Seek is frontend-only; Space plays from the sought position.
- **Constraints:**
  - Media legality (intent §1): all reads/writes stay in `data/**` (gitignored),
    local-only. Server binds 127.0.0.1. No change.
  - Simplicity-first / surgical (`.claude/rules/`): mirror existing cut/recut
    patterns; reuse the cut-mode drag selection and the `_orig`/undo mechanism
    rather than inventing a new one. No backend DI/class-ification.
  - Backend runs in `.venv-vnser` (soundfile present). Atomic wav writes (tmp→rename).
  - Provenance (CLAUDE.md): excised clip's timestamps must stay honest — see
    Decision 2026-07-18.

## Milestones
- [x] M1 — Backend excise — `audio.excise()` + `POST /excise` + `/recut/undo`
      clears `excised` + `excised` default. Verified: unit + TestClient e2e.
- [x] M2 — Frontend excise — `api.excise`, `saveExcise()`, `⌦ bỏ giữa` button,
      wiring. Verified: node --check + DOM-stub boot + live served.
- [x] M3 — Click-to-seek — normal-mode waveform click sets `S.audio.currentTime`.
      Verified: node checks (live click = repo browser-drive caveat).
- [x] M4 — Docs — SPEC.md + SPEC-features.md + change 005 README + this doc.
      `make check` (ruff) green.

## Decision Log
<!-- newest first -->
- **2026-07-18 — Reuse cut-mode drag selection for excise (one selection, two
  save buttons):** `✂ cắt` enters cut mode + drag-select as today; `✔ lưu cắt`
  = keep `[a,b]` (trim, existing), new `⌦ bỏ giữa` = remove `[a,b]` (excise).
  Why: the drag UI is identical; adding a parallel `exciseMode` would duplicate
  the toggle/reset/drag/draw code. Rejected: separate excise mode with its own
  flag + red highlight (more code, marginal UX gain — button labels already
  disambiguate intent at save time).
- **2026-07-18 — Excise reuses `/recut/undo` + `recut=true` flag:** excise sets
  `recut=true` (drives the ✂ table flag) and is undone by the existing
  `/recut/undo` (restores `_orig` pristine audio, resets boundaries), extended to
  also clear `excised`. Why: `_orig` already holds the pristine clip; one undo
  path for all in-place audio edits. Rejected: a distinct `/excise/undo` route
  (would duplicate restore logic).
- **2026-07-18 — Timestamp provenance = keep span + record gap (user-chosen):**
  excise does NOT move `start`/`end`; it appends the removed region to a new
  `excised: [[a,b],…]` list (clip-local seconds of the file at the moment of the
  cut, appended in order). `start`/`end` stay the original bounding span; real
  audio duration is read from the file. Why: honest provenance — with `_orig` +
  ordered `excised`, exactly what was removed is reconstructable; nothing silently
  lost. Rejected: collapse `end = start + new_dur` (removed region vanishes from
  the record — dishonest per CLAUDE.md provenance rule).

## Open Questions
<!-- none blocking; provenance fork resolved by user (see Decision Log) -->

## Research Findings
<!-- none needed; the one fork was a user decision, not an external unknown -->

## Completed Work
- 2026-07-18 — **M1 backend** — `audio.excise()` (concat `[0,a]+[b,dur]`, backup
  `_orig` once, strictly-inside guard) — `tools/labeler/audio.py:65`; `POST
  /excise` route appends to `excised[]` + `recut=true` — `server.py:145`;
  `/recut/undo` now clears `excised` — `server.py:120`; `excised: []` default —
  `store.py:143`. Verified e2e (unit + TestClient `/excise`→`/recut/undo` +
  edge/empty guards) — scratchpad `test_excise.py`, ALL PASS; ruff green.
- 2026-07-18 — **M2 frontend excise** — `api.excise` — `api.js:23`; `saveExcise()`
  (reuses cut-mode selection, guards middle-only) — `actions.js:65`; `⌦ bỏ giữa`
  button — `index.html:85`; wiring + updated cut prompt — `main.js`. Verified:
  `node --check` all 5 modules; DOM-stub boot imports graph clean; live server
  serves button + `main.js` as ESM + `/excise` route responds.
- 2026-07-18 — **M3 click-to-seek** — normal-mode waveform `mousedown` sets
  `S.audio.currentTime = xToTime(e)` + redraws playhead — `main.js` mousedown
  handler; Space plays from there (audio element retains currentTime). Verified
  via node checks; live click is the repo-wide browser-drive caveat.

## Remaining Action Items
- [x] M1 backend: `audio.excise`, route, undo clear, seed default + test
- [x] M2 frontend excise UI
- [x] M3 click-to-seek
- [x] M4 docs + change 005 folder — `SPEC.md`, `SPEC-features.md`,
      `docs/spec/changes/005-labeler-excise-seek/README.md`; ruff green.
- (none) — all done. Human browser-drive smoke of the drag/click UI is the only
  open item, per the repo-wide frontend caveat.
