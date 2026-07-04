# Phase 1 — Data Collection & Tooling

**Span:** Weeks 1–2
**Owners:** Backend eng (collection + tool), AI eng (independence check)
**Strategy refs:** §5.2
**Depends on:** [Phase 0](00-prework-foundations.md) (generator confirmed, env ready)

## Objective

Start accumulating training data and build the means to label it.

## Tasks

- Stand up the `training_data/{docId}` Firestore collection, **separate from
  production messages**. Begin Day 1 of Phase 1.
  - **Input:** current message + last 3 messages, interleaved.
  - **Target:** energy, severity, socialIsolation, receptivity, detectedEmotion,
    safetyFlag. Exclude themeRepetition and sessionTrajectory.
  - **Metadata:** sessionId, userId (for stratified splitting), timestamp,
    **generator model version** (critical — OQ5), fallback flag (exclude fallbacks).
- Build the annotation tool (admin dashboard page): fetch sample → show message +
  context → sliders for scores + dropdown for emotion → submit. Two modes: pre-filled
  (Protocol A) and blank (Protocol B), toggled per batch. ~2–3 days.
- **Energy/severity independence check** once ~1K labels exist: Pearson/Spearman across
  the collection. **If |r| > 0.7, drop the energy head** — it carries no independent
  signal (cut K in the score head; the Decision Engine derives a coarse proxy).

## Exit gate

- Silver labels flowing with full provenance metadata.
- Annotation tool supports both protocols.
- Energy-head decision recorded in `configs/config.yaml > model.score_dims`.

## Risk

The 5K target may not exist on schedule — early-phase DAU is *tens*, not 500
(500 DAU is ~Phase 4 / MVP scale). **Gate the training start on accumulated volume,
not the calendar.** Fallback: delay, or lean harder on external transfer data. This
risk is sharper on the data-hungry NeoBERT path. *(§5.2, §5.3)*

**Next:** [Phase 2 — Taxonomy & Viability Gates](02-taxonomy-viability-gates.md)
