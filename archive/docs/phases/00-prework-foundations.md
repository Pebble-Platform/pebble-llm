# Phase 0 — Pre-work & Foundations

**Span:** Week 0 (blocking — before the 14-week plan starts)
**Owners:** Product + AI eng (decisions), AI eng (env)
**Strategy refs:** §4, §6.1 Step 0, OQ2, OQ3, OQ5, OQ6
**Depends on:** —

## Objective

Clear every blocker that would invalidate the 14-week plan if discovered mid-flight.
Nothing in Phases 1–9 starts until these are settled.

## Tasks

- **Decide NeoBERT serving direction** — GPU FP16 baseline (NVIDIA L4; Cloud Run vs
  Vertex endpoint) vs the CPU/ONNX cost-optimization ambition. Re-derive the cost model
  at 500 DAU (likely *more* than Flash-Lite per-token). *(§4, OQ6)*
- **Pin the silver-label generator and track its version.** Confirm which generator
  model scores production messages, and record its version on every `training_data` row.
  If you ever switch generators mid-collection, re-score a stratified sample with the new
  one and measure per-dimension divergence before mixing old and new labels. *(OQ5)*
- **Source the clinical reviewer** — one licensed individual with C-SSRS/Columbia-Protocol
  familiarity; start sourcing Week 1, contract by Week 3. Scope in writing as
  training-label review only. *(OQ2)*
- **Decide annotation hiring channel** — 2–3 contract annotators with mental-health
  background; budget **3 raters** for pilot + Protocol B. Not a crowd-labeling service. *(OQ3)*
- **Engineering foundation:** `uv sync`; **pin NeoBERT to an exact revision** and
  **vendor** the custom modeling code into the repo; confirm GPU availability for
  training (FlashAttention requires it). *(§6.1 Step 0)*

## Exit gate

- Serving direction + budget approved.
- Silver-label generator confirmed; version recorded on every row.
- Clinical + annotation channels in motion.
- Model revision pinned and modeling code vendored.

## Risk if skipped

Serving cost is discovered too late to change the architecture decision; if the
generator changes mid-collection without version tracking, silver labels become
mixed-provenance and the divergence check (OQ5) is impossible after the fact.

## Fallback ladder (set the trigger thresholds now)

NeoBERT-GPU → ModernBERT (proven CPU/ONNX, smaller) → Gemini Flash-Lite backup.

**Next:** [Phase 1 — Data Collection & Tooling](01-data-collection-tooling.md)
