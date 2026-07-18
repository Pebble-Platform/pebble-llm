# Change 008 — Labeler: context preview (nghe ±N s before/after a clip)

**Status:** done (2026-07-18) — backend read-only e2e-verified on real audio;
frontend node-checked + DOM-stub boot.
**Goal:** let the labeler hear the clip **with surrounding context** — 10s before
and 10s after — so cut boundaries, multi-speaker, and emotion context can be
judged. The clip `.wav` is only the cut segment; context comes from the episode's
full audio at the clip's absolute position.

## Feature — `▶ nghe ±10s`

A button next to `▶ Play` + a seconds dropdown (**N = 10/20/30/60**). Plays
`[start−N, end+N]` of the episode's full audio in a **separate** audio player, so
the main clip audio + waveform are untouched. Toggle to stop; auto-stops when the
clip audio plays or you move to another clip. `N` selectable in the UI (user
follow-up 2026-07-18: "lấy thêm audio trước/sau" = hear a longer window, not widen
the clip) — the endpoint's `pad` already supported it, so this was UI-only.

- **Backend** `GET /context/{epKey}/{clip_id}.wav?pad=10` (read-only): resolves the
  clip's absolute episode-time bounds (state record if any, else `segments.csv`),
  slices `[start−pad, end+pad]` from `audio_full.wav` (fallback `vocals_16k.wav`)
  with `soundfile`, returns in-memory WAV bytes. `pad` defaults to 10s (query-param
  → trivially adjustable later without UI).
- **Frontend:** `S.preview` (a second `Audio`), `playContext` toggles it with
  `src = /context/…`; `main.js` swaps the button label on play/pause/ended;
  `view.js` pauses the preview when the clip audio plays or on clip switch.

## Design decisions

- **Backend pre-cuts the ±pad slice (vs. serve full audio + browser seek):** a
  ~20s WAV is a small payload and the frontend just plays it 0→end — no HTTP-range,
  no seek-after-metadata, no "stop at t" timer. Reads a slice of the 68MB
  `audio_full.wav` cheaply via `soundfile` start/stop frames. Rejected: serve full
  episode audio + seek/stop in the browser (more moving parts, 68MB transfer).
- **Full-mix `audio_full.wav` (fallback vocals):** context listening wants the
  natural scene audio, not the speech-separated track.
- **Separate `S.preview` player, waveform untouched:** the preview is a listening
  aid; syncing the clip waveform to full-episode time would be invasive for no
  gain. The two players never overlap (each pauses the other).
- **Absolute bounds from state/CSV:** the clip's `start`/`end` (recut/excise/split
  aware in state, else `segments.csv`) are absolute episode seconds → index
  straight into `audio_full.wav`.

## File changes (all `tools/labeler/`)

| File | Change |
|---|---|
| `audio.py` | `+io`; `read_context(ep,start,end,pad)` → WAV bytes of the full-audio slice |
| `server.py` | `+Response`; `GET /context/{epKey}/{id}.wav?pad=` |
| `api.js` | `contextUrl` |
| `state.js` | `preview: new Audio()` |
| `actions.js` | `playContext` (toggle) — reads `#ctxpad` → `?pad=N` |
| `view.js` | pause preview on clip audio play + on clip switch |
| `index.html` | `▶ nghe ±` button + `#ctxpad` seconds dropdown (10/20/30/60) |
| `main.js` | wire `ctxplay` + preview label on play/pause/ended |
| `SPEC.md` | Chức năng bullet + REST row + arch date |

## Verify

- **Backend** (`scratchpad/test_context.py`, TestClient, real audio, read-only):
  mid clip 3.2s → context 23.2s (=dur+20); edge clip (start=0) → 12.7s (clamped);
  bad clip id → 400. `pad` param: pad=20 → 43.2s, pad=60 → 123.2s. ruff clean.
- **Frontend:** `node --check` all 5 modules; DOM-stub `import("./main.js")` boots
  clean.
- **Op note:** this adds a backend route → the running `:8000` server must be
  **restarted** to serve `/context` (plus a tab reload for the new JS).
- **Caveat:** live audio playback needs human browser-drive (repo-wide).
