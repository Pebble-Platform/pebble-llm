# Phase 4 — Safety Data

**Span:** Week 6
**Owners:** AI eng (Layers 1–2), clinical reviewer (Layer 3 + methodology)
**Strategy refs:** §5.4
**Depends on:** [Phase 3](03-human-annotation.md) (confirmed safety positives), clinician contracted (Phase 0 / OQ2)

## Objective

Build a usable safety-positive set. At a ~1–2% base rate the raw set holds only
50–100 real positives — not enough for a robust safety head.

## Tasks (layered augmentation)

- **Layer 1 — Real positives from production.** Every Gemini `safetyFlag=true` message
  from Phases 1–3 is confirmed/rejected by a **dedicated** annotator (separate from
  general annotation). Confirmed → training. Expected 50–150.
- **Layer 2 — Adversarial rephrasing.** 2–3 rephrasings per confirmed positive that
  preserve the crisis signal but change surface features, so the model learns intent
  not phrases. Each peer-reviewed for realism. Expected 100–450.
- **Layer 3 — Synthetic under clinical review.** Gemini Pro generates synthetic crisis
  messages varying explicitness (explicit ideation → indirect signals), demographics,
  styles; include near-miss non-crisis ("this movie is killing me"). **Every example
  reviewed by the licensed clinician** before training (realistic / discard / borderline).
  Clinician reviews the **methodology before generation**, not just outputs. Expected 200–300.
- **Layer 4 — Public datasets (if approved).** CLPsych / UMD Reddit Suicidality
  (IRB/DUA). Strongest source if approved; Layers 1–3 must suffice if not.

## Exit gate

- ~350–900 total positives (≈7–15% rate — manageable with positive-class weighting).
- Clinical sign-off recorded.

## Risk

The model may learn synthetic **style** rather than crisis signal. Mitigation: the
Protocol B test set is **100% real production data** — if recall is high on synthetic
validation but low on the real test set, reduce/regenerate synthetic data with clinical
feedback.

**Next:** [Phase 5 — Dataset Prep & Transfer Pre-training](05-dataset-prep-pretrain.md)
