# Phase 3 — Human Annotation

**Span:** Weeks 4–5
**Owners:** 2 annotators (Protocol A), 3 annotators (Protocol B), AI eng
**Strategy refs:** §5.2, §8.3
**Depends on:** [Phase 2](02-taxonomy-viability-gates.md) (taxonomy finalized)

## Objective

Produce the human-corrected training augment (Protocol A) and the unanchored,
Gemini-independent test set (Protocol B).

## Tasks

### Protocol A — Training Corrections (Week 4, anchored, 500)
- Sample 500 from silver labels, stratified by severity quartile.
- **Oversample the 0.5–0.8 severity band (~150, human-annotated — not silver).** This
  is the moderate-severity blind spot (§8.3): a user who should route to MOTIVATE/CONNECT
  gets LIGHTEN, no safety flag because it's sub-crisis.
- Annotators adjust Gemini's pre-filled scores. Where 2 agree on a correction
  (>0.15 deviation on any continuous dim, or emotion-label disagreement), the human
  label replaces silver. Disagreements → adjudication. 2 annotators acceptable.

### Protocol B — Test Set (Week 5, unanchored, 500)
- Sample 500, stratified by severity quartile (125/quartile).
- 3 annotators score **all dimensions from scratch, with no visibility into Gemini's
  scores** (blank UI).
- Measure Krippendorff α (continuous) + Cohen κ (categorical). **α < 0.6 on any
  dimension → revise guidelines and re-annotate.**
- Compute Gemini-vs-human correlation per dimension → honest silver-label quality measure.

### Throughout
- Enforce **annotator wellbeing**: cap daily high-severity volume, rotate off the
  safety-positive queue, EAP/debriefing access, no-penalty opt-out. Ethics *and* data
  quality — fatigued annotators produce noisier labels, degrading the α gates.

## Exit gate

- Protocol B α ≥ 0.6 on all retained dimensions.
- Both sets finalized; silver-label trust quantified per dimension.

**Next:** [Phase 4 — Safety Data](04-safety-data.md)
