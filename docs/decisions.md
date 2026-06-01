# Decision Log (Phase 0 open questions)

Tracks the Phase 0 decisions from [`pebble-finetuning-strategy-v3.md`](../pebble-finetuning-strategy-v3.md) §11.
Status: ✅ resolved · 🟡 pending/deferred · ⛔ blocked on input.

| ID | Decision | Status |
|---|---|---|
| OQ5 | Data source | ✅ Reuse public dataset labels |
| — | Dimension scope | ✅ All 6 outputs (2 learned, 4 heuristic) |
| OQ6 | NeoBERT serving direction | 🟡 Deferred to post-PoC |
| OQ2 | Clinical reviewer | ✅ Not needed for v1 |
| OQ3 | Annotation hiring channel | ✅ Not needed for v1 |

---

## OQ5 — Data source ✅ (pivoted)

**Resolved 2026-05-29:** No Gemini generator / no Pebble-schema silver labels. **Data
source = reused public dataset labels** (§5.1 — GoEmotions for emotion, SemEval/WASSA
intensity for severity), mapped onto Pebble dimensions. Silver-label collection, the
Gemini path, and shadow scoring (§8.2) are **out of scope** for this approach.

## Dimension scope ✅

**Resolved 2026-05-29:** Keep all 6 `/classify` outputs, but only two are model-learned:

| Output | Source in v1 |
|---|---|
| `detectedEmotion` | **Learned** — emotion head, GoEmotions (mapped via `taxonomy.py`) |
| `severity` | **Learned** — score head, SemEval/WASSA intensity transfer |
| `energy` | Heuristic (Decision Engine; no public label) |
| `socialIsolation` | Heuristic — keyword (§3.3 fallback) |
| `receptivity` | Heuristic — interrogative/person-ratio (§3.4 fallback) |
| `safetyFlag` | Heuristic — keyword regex + generation net (§7); no learned safety head in v1 |

→ `model.score_dims = [severity]`; emotion head = 12 labels; no safety head trained in v1.

## OQ6 — NeoBERT serving direction 🟡 (deferred)

Not needed for the public-data PoC (train on free Kaggle GPU; no production endpoint yet).
When productionizing: recommend **Track A — GPU FP16 (NVIDIA L4)** baseline, CPU/ONNX as a
later spike (§4). Revisit after the PoC validates quality.

## OQ2 — Clinical reviewer ✅ (not needed for v1)

The reuse-labels v1 trains no safety head and builds no synthetic crisis data (§5.4),
so no clinical reviewer is required. Re-open if a learned safety head is added later.

## OQ3 — Annotation hiring channel ✅ (not needed for v1)

No human annotation pass under the reuse-labels approach — public datasets are already
labeled. Re-open if Pebble-specific human annotation is added later.
