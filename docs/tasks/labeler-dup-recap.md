# Labeler — detect + bulk-mark duplicate recap spans across episodes

- **Slug:** labeler-dup-recap
- **Status:** done
- **Created:** 2026-07-18  ·  **Updated:** 2026-07-18
- **Owner:** phat / agent

## Goal
VN TV dramas (e.g. `ve-nha-di-con`) replay the previous episode's final scene as a
**recap** at the start of the next episode → the extracted clips are duplicated
across two episodes. Add a way to **auto-detect** the repeated span between two
episodes and **bulk-mark** the duplicate clips (one contiguous run) so they are
excluded from labeling/export and the content is labeled only once. Done = user
clicks "dò recap" on an episode, tool proposes the duplicated clip range, user
confirms, those clips get flagged `duplicate` (excluded like reject); SPEC + change
doc updated; `make check` green.

## Requirements & Constraints
- **Functional:**
  - Auto-detect the repeated audio span between an episode and its neighbour
    (robust to different YouTube transcodes — NOT bit-identical). Return the
    matched time spans + the list of clip ids in that span.
  - Bulk-mark a set/contiguous range of clips as `duplicate` in one action
    (reuses the reject exclusion mechanism; excluded from done/export).
  - Keep the canonical copy in the other episode labeled once; the duplicate
    carries provenance of what it duplicates (source ep + span).
- **Constraints:**
  - Corpus integrity: cross-episode duplicate audio must not appear twice
    (leakage / inflation risk; relevant to I4 whole-series splits).
  - Media legality (intent §1): all audio stays under `data/**`, local-only,
    127.0.0.1.
  - Backend runs in `.venv-vnser` (numpy, soundfile, torch/torchaudio 2.11).
    Prefer light deps; justify any new one.
  - Simplicity-first / surgical: reuse the reject flag + `_orig`-style patterns;
    no heavy framework.

## Milestones
- [x] M1 — Research audio-match method — log-mel feature cross-correlation, no dep.
- [x] M2 — Backend bulk-mark — `duplicate` reason + `POST /reject-bulk` +
      `dup_source`. TestClient e2e pass.
- [x] M3 — Backend detect endpoint — `recap.py` + `GET /detect-recap`; calibrated
      on real ve-nha-di-con (2 recaps found, clean margin); ep02→MATCH, ep01→404.
- [x] M4 — Frontend — ⧉ dò recap → review panel → confirm → bulk-mark; recap-row
      highlight. node checks + DOM-stub boot + live served (read-only detect).
      (Manual shift-click NOT built — auto-detect→bulk covers it; near-miss
      "confirm anyway" + per-clip reject cover edges.)
- [x] M5 — Docs — SPEC.md (data model + REST + F8 + arch) + change 006 README +
      this doc. ruff green.

## Decision Log
<!-- newest first -->
- **2026-07-18 — Never test-write against the live data root while a labeler is
  running:** during M4 live smoke I ran throwaway servers on ports 8137/8139/8141
  with `--root data/vietnamese-ser/episodes` while the user's labeler was live on
  `:8000`. Two servers sharing one `state.jsonl` (full-file last-writer-wins save)
  can clobber. No damage occurred (the `:8000` server re-saves its authoritative
  in-memory state on every edit → healed my writes; verified 0 `duplicate`/
  `dup_source` rows, 3 touched clips restored, today's labels intact). Rule going
  forward: verify against an isolated tempdir root only; live-root calls must be
  read-only. **Op note:** the running `:8000` server has the OLD code — restart it
  + reload the tab to get `/detect-recap`, `/reject-bulk`, and the ⧉ dò recap UI.
- **2026-07-18 — Detect on `vocals_16k.wav` (fallback `audio_full.wav`):** each
  episode ships a pipeline `vocals_16k.wav` (16kHz mono, speech-separated) + a
  full-mix `audio_full.wav`. Use vocals — isolates replayed dialogue, robust to
  differing background-music mixes, no resample needed. Why: recaps replay the
  same speech; matching vocals avoids false hits on shared theme music. (see
  Research: M1 method.)
- **2026-07-18 — M1 method = log-mel feature cross-correlation, no new dep:**
  adopt the task-researcher recommendation (Research Findings M1). Rejected raw
  cross-correlation (transcode-brittle) + chromaprint/audfprint (external binary /
  overkill). Detection is a **read** (`GET /detect-recap`); marking stays the
  separate `POST /reject-bulk` (human confirms between).
- **2026-07-18 — Auto-detect + bulk (user-chosen):** tool cross-matches audio to
  propose the repeated span between consecutive episodes; user confirms; the
  duplicate clips (a contiguous run) are bulk-marked. Rejected: manual-only marking
  (user wants auto-detect); per-clip marking (recap spans many clips — too tedious).
- **2026-07-18 — Mark = exclude (reject reason `duplicate`), keep the other copy:**
  duplicate clips are flagged and excluded from done/export like F3 reject; the
  canonical copy in the neighbour episode is labeled once. Why: the audio is
  perceptually identical — including both would duplicate/leak. Provenance:
  store `dup_source` (source epKey + matched span) so audit knows what it covers.
  Rejected: copy/inherit the label onto the duplicate (recreates duplicate audio).

## Open Questions
- [x] **Audio-match method** — RESOLVED by M1 research (see Decision Log +
      Research Findings): log-mel feature-sequence cross-correlation, no new dep.

## Research Findings

### M1 — cross-episode recap-match method (task-researcher, 2026-07-18, medium-high)
- **Recommendation:** feature-sequence cross-correlation (option b). Reuse the
  repo's `torchaudio` mel front-end (16kHz, `n_fft=400`, `hop_length=160`,
  `n_mels=40`, per `scripts/vietnamese-ser/benchmark/extract_mfcc.py:27-30`),
  pool 10ms→100ms superframes, log1p, **L2-normalize** (kills loudness/transcode
  gain diff), energy-mask silence, cosine similarity matrix restricted to last
  3min of ep N-1 vs first 3min of ep N, best-diagonal search, longest contiguous
  run ≥15s as the span. No new dependency (~80–100 lines); <1s per pair.
- **Rejected:** (a) raw-sample cross-correlation — brittle to lossy transcode
  phase/gain; (c) chromaprint/audfprint/dejavu — external `fpcalc` binary /
  DB-oriented, overkill for a single local pairwise compare.
- **Thresholds (starting points, must calibrate in M3):** per-superframe cosine
  τ≈0.80, run-mean cosine ≈0.75–0.80, min run ≈15s.
- **False positives:** min-run-length filters short shared jingles; if persistent,
  negative control vs a non-adjacent episode (N vs N-2). Montage recaps degrade
  as a shorter/weaker run → keep the human-confirm step (M4) in the loop.
- **Sources:** randombytes.org cross-correlated-fingerprint article; audfprint;
  dejavu; milvus fingerprinting overview; repo `extract_mfcc.py:27-30`.

## Completed Work
- 2026-07-18 — **M2 bulk-mark backend** — `duplicate` reject reason;
  `POST /reject-bulk/{epKey}` `{ids,reason,dup_source}` flags N clips in one
  atomic save with `dup_source` provenance — `server.py:155`; `api.rejectBulk` —
  `api.js:26`; `duplicate` in reject dropdown — `index.html`. Verified e2e
  (`test_bulk.py`, ALL PASS): 3 clips flagged + `dup_source`, listing rejected==3,
  per-clip undo reversible, bad-id → 400; ruff green.

- 2026-07-18 — **M1 research** — folded (Research Findings + Decision Log):
  log-mel feature cross-correlation, no new dep.
- 2026-07-18 — **M3 detect endpoint** — `tools/labeler/recap.py` (previous_episode,
  log-mel superframe features, best-diagonal run search, `clips_in_span`) +
  `GET /detect-recap/{epKey}` — `server.py:82`. **Calibrated on real
  ve-nha-di-con** (`test_recap.py` + `calib_recap.py`): found 2 real recaps —
  ep01→ep02 (0.967, 13.2s, 3 clips seg22–24) & ep05→ep06 (0.973, 13.5s, 0 clips)
  — vs incidental <0.89/<8s; neg-control ep01→ep03 = 0.828. Constants:
  WIN=240 (240s window caught ep02's recap at 226s), TAU_FRAME .85, TAU_MEAN .90,
  MIN_RUN 6s, GAP 8. Endpoint e2e: ep02→MATCH 3 clips, ep01→404. ruff green.
  Near-miss clips also returned (UI "confirm anyway").

- 2026-07-18 — **M4 frontend** — `api.detectRecap`/`rejectBulk` (`api.js`);
  `detectRecap`/`markRecap`/`dismissRecap` (`actions.js`); `⧉ dò recap` button +
  review panel + `duplicate` reason + highlight CSS (`index.html`); recap-row
  highlight + clear-on-switch (`view.js`); wiring (`main.js`). Verified node +
  DOM-stub boot + live served (detect read-only; bulk-mark round-trip).
- 2026-07-18 — **M5 docs** — SPEC.md (data model `dup_source`/F8, REST
  `/detect-recap` + `/reject-bulk`, Chức năng F8, arch `recap.py`); change 006
  README; this doc. ruff + node green.

## Remaining Action Items
- [x] all milestones complete — see Milestones. Only open item: user must
      **restart the `:8000` labeler + reload the tab** to load the 006 code, then
      click ⧉ dò recap on an episode and confirm (human browser-drive caveat).
