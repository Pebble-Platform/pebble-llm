# Phase 5 — Dataset Prep & Transfer Pre-training

**Span:** Week 7
**Owners:** AI eng (3 days)
**Strategy refs:** §5.1, §5.5, §6.1 Step 1
**Depends on:** [Phase 4](04-safety-data.md) (annotation + safety augmentation complete)

## Objective

Assemble the final splits, warm-start the emotion head, and set the fallback bar.

## Tasks

- **Build splits** (§5.5): filter/merge silver (filtered) + Protocol A human-corrected +
  safety Layers 2–4 + GoEmotions/EmpatheticDialogues transfer examples for
  underrepresented classes.
  - **User-level split first** (deterministic userId hash → split, stored as metadata),
    **then** stratify by severity quartile *within* the assigned users. Never stratify at
    message level then dedup by user — that reintroduces leakage.
  - Target composition: Train 4,000–5,500 · Val 500 (250 human + 250 silver) ·
    **Test 500 = 100% Protocol B (unanchored)** — non-negotiable.
  - Export to `data/processed/`.
- **GoEmotions emotion-head pre-training** (§6.1 Step 1): map 27 labels → taxonomy
  (team-reviewed); freeze encoder 2 epochs so the head converges, then unfreeze 1–2
  epochs at LR 1e-5. Only the emotion head is active.
- **Gemini-Lite SFT baseline** (§10 W7): run a quick Vertex SFT baseline on the same
  data to set the bar the NeoBERT run must beat at the Week-8 gate.

## Exit gate

- Leak-free splits (test = 100% Protocol B); user-split metadata stored.
- Pretrained emotion-head checkpoint.
- Gemini-Lite baseline metrics computed on the Protocol B set.

**Next:** [Phase 6 — Multi-task Training & Evaluation](06-training-evaluation.md)
