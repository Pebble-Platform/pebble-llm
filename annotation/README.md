# Annotation

Human annotation produces the high-quality test set and calibrates which dimensions
Gemini scores reliably (strategy §3.2, §5.2). The tool itself is a page in the admin
dashboard (separate repo); this folder holds the **guidelines, protocols, and gates**.

## Protocols

| Protocol | Anchored? | N | Purpose |
|---|---|---|---|
| Taxonomy pilot (§3.2) | No (from scratch) | 100 | Finalize the 12-label taxonomy; merge labels confused >40%. |
| Protocol A (§5.2) | Yes (Gemini pre-filled) | 500 | Training corrections. Oversample 0.5–0.8 severity band (~150). |
| Protocol B (§5.2) | **No** (blank UI) | 500 | The test set. Anchoring bias is unacceptable. |

## Viability gates (decided during the Week-3 pilot, not Week 7)

- **socialIsolation (§3.3):** Krippendorff α < 0.5 → drop, use keyword heuristic. 0.5–0.6 → relaxed MAE 0.25. ≥0.6 → normal.
- **receptivity (§3.4):** α < 0.5 → collapse to binary venting/seeking (preferred) or heuristic. 0.5–0.6 → relaxed. ≥0.6 → continuous.

## Annotators

- **Three** raters on the pilot and Protocol B (two-rater α is too noisy; third adjudicates). Protocol A can run with two.
- Contract annotators with mental-health background — not a crowd-labeling service (OQ3).
- Keep the safety-positive confirmation annotator **separate** from general annotation.

## Annotator wellbeing (mandatory — §5.2)

This work exposes annotators to crisis/self-harm content for weeks. Required:
cap daily high-severity volume per annotator, rotate off the safety-positive queue,
provide debriefing/EAP access, brief up front with a no-penalty opt-out. Ethical
obligation *and* data quality — fatigued annotators produce noisier labels.

See `guidelines.md` for the per-dimension scoring rubric.
