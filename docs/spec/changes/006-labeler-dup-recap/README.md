# Change 006 — Labeler: detect + bulk-mark duplicate recap spans (F8)

**Status:** done (2026-07-18) — backend calibrated on real ve-nha-di-con audio;
frontend node-checked + live-served; detect verified read-only end-to-end.
**Goal:** VN TV dramas replay the previous episode's final scene as a **recap** at
the start of the next → extracted clips are duplicated across two episodes. Add a
way to **auto-detect** the repeated span and **bulk-mark** the duplicate clips so
they are labeled only once (excluded like reject) — which also removes a corpus
leakage/inflation risk (same audio in two clips). User-chosen flow: tool detects,
human confirms. Living doc: [`docs/tasks/labeler-dup-recap.md`](../../../tasks/labeler-dup-recap.md).

## F8 — Recap duplicate detection + bulk mark

**Two-step, human-in-the-loop:**
1. `GET /detect-recap/{epKey}` (read-only) proposes the repeated span vs the
   predecessor episode + the cur-episode clip ids in it.
2. Human reviews (panel + can listen), confirms → `POST /reject-bulk` flags those
   clips `reject_reason="duplicate"` with `dup_source` provenance. The canonical
   copy stays labeled once in the other episode.

### Detection method (task-researcher M1 → calibrated)
Log-mel **feature-sequence cross-correlation** — no new dependency (`recap.py`,
~185 lines, reuses `torchaudio` mel + `numpy`):
- Load last/first `WIN=240s` of `vocals_16k.wav` (speech-separated 16k mono;
  fallback `audio_full.wav`) of prev-tail / cur-head.
- `MelSpectrogram(16k, n_fft=400, hop=160, n_mels=40)` → log1p → mean-pool
  10 frames → 100ms superframes → **L2-normalize** (robust to different YouTube
  transcodes / loudness).
- Cosine similarity matrix `A @ B.T`; per-lag diagonal, silence-masked
  (RMS < -50dBFS), smoothed, gap-bridged; longest contiguous run ≥ `TAU_FRAME`.
- Match if run ≥ `MIN_RUN_S` and mean cosine ≥ `TAU_MEAN`; else return the best
  candidate anyway (UI "confirm anyway" for near-misses).

**Rejected methods:** raw-sample cross-correlation (brittle to transcode
phase/gain); chromaprint/audfprint/dejavu (external `fpcalc` binary / DB-oriented,
overkill for one local pairwise compare).

### Calibration (on real ve-nha-di-con, `scratchpad/calib_recap.py`)
Constants are **tuned to measured data**, not the research defaults:

| const | value | why |
|---|---|---|
| `WIN` | 240s | ep02's recap sits at 226s — the 180s default missed it |
| `TAU_FRAME` | 0.85 | per-superframe match floor |
| `TAU_MEAN` | 0.90 | real recaps score 0.97 ≫ incidental ~0.80–0.88 |
| `MIN_RUN_S` | 6.0 | real recaps 13s; incidental runs <8s (vocals removes theme music → no long jingle matches) |
| `GAP` | 8 (~0.8s) | bridges brief dips; GAP=30 over-reached into low-score audio |

**Found on the real data:** two recaps — ep01→ep02 (0.967, 13.2s, 3 clips
seg22–24) and ep05→ep06 (0.973, 13.5s, 0 extracted clips) — vs every other
consecutive pair <0.89 / <8s; negative control ep01→ep03 = 0.828. Clean margin.

## File changes

| File | Change |
|---|---|
| `tools/labeler/recap.py` | **new** — `previous_episode`, log-mel `detect`, `clips_in_span` |
| `tools/labeler/server.py` | `import recap`; `GET /detect-recap`; `RejectBulkIn` + `POST /reject-bulk`; `duplicate` reason |
| `tools/labeler/store.py` | (unchanged; `dup_source` set only when marking) |
| `tools/labeler/api.js` | `detectRecap`, `rejectBulk` |
| `tools/labeler/actions.js` | `detectRecap`, `markRecap`, `dismissRecap` |
| `tools/labeler/view.js` | recap-row highlight in table; clear recap on episode switch |
| `tools/labeler/index.html` | `⧉ dò recap` button, review panel, `duplicate` reason, highlight CSS |
| `tools/labeler/main.js` | wire recap buttons |
| `tools/labeler/SPEC.md` | data model + REST + Chức năng (F8) + arch |

## Verify

- **M2 bulk-mark** (`scratchpad/test_bulk.py`, tempdir, ALL PASS): 3 clips flagged
  `duplicate` + `dup_source`, listing `rejected` count updates, per-clip undo
  reversible, path-traversal id → 400.
- **M3 detect** (`scratchpad/test_recap.py` + `calib_recap.py`, real audio):
  correct recap spans + clip mapping; endpoint e2e ep02→MATCH(3 clips),
  ep01→404 (no predecessor). ruff green.
- **M4 frontend:** `node --check` all 5 modules; DOM-stub `import("./main.js")`
  boots clean; live server serves button+panel; `GET /detect-recap` + `POST
  /reject-bulk` round-trip.
- **Caveat:** live click/confirm interaction needs human browser-drive (repo-wide).

## Incident / lesson (recorded)

During M4 live smoke, throwaway servers were run with `--root
data/vietnamese-ser/episodes` **while the user's labeler was live on `:8000`**.
Two servers sharing one `state.jsonl` (full-file last-writer-wins) is a clobber
hazard. **No damage** — the `:8000` server re-saves its authoritative in-memory
state on every edit and healed the test writes (verified 0 `duplicate`/`dup_source`
rows, touched clips restored, today's labels intact). Rule: verify against an
isolated tempdir; live-root calls read-only only.

**Op note:** the running `:8000` labeler has the pre-006 code — restart it and
reload the tab to pick up `/detect-recap`, `/reject-bulk`, and the ⧉ dò recap UI.

## Downstream / not done

- `build_kaggle_dataset.py` (phase 4, unbuilt): excludes `reject_reason="duplicate"`
  like any reject; `dup_source` documents what each covers.
- Manual shift-click range-select was **not** built — auto-detect → bulk-reject
  covers the "bulk" need; near-miss "confirm anyway" + per-clip reject cover edges.
- Montage recaps degrade to a shorter/weaker run; top-K candidate spans not
  surfaced (single best only) — human-confirm + manual reject is the safety net.
