# Phase 6 — Multi-task Training & Evaluation  *(the decision gate)*

**Span:** Week 8 (+ Week 10 iteration buffer)
**Owners:** AI eng (4–5 days)
**Strategy refs:** §6.1 Steps 2–3, §7, §5.3, §8.3
**Depends on:** [Phase 5](05-dataset-prep-pretrain.md) (splits + pretrained head + baseline)

## Objective

Train the multi-task NeoBERT, evaluate honestly on Protocol B, and decide NeoBERT vs
the fallback ladder.

## Tasks

- **Multi-task fine-tune** (§6.1 Step 2): emotion head from Phase 5; score/safety heads
  random. Encoder freeze 1–2 epochs then unfreeze (LR 5e-6 encoder / 2e-5 heads).
  Batch 16, ~5 epochs. Loss weights score×1, emotion×1, safety×2; safety positive-class
  weight 10×. Early stopping (patience 3, eval/100 steps). FP16. Dropout 0.1→0.2 if
  train/val diverge >20% after epoch 2. **≥3 seeds; report mean ± std.**
- **Multi-task balancing** (§6.1 caveat): if per-head val metrics diverge (emotion
  improves while severity stalls), switch from static weights to uncertainty weighting
  (Kendall) or GradNorm before adding data.
- **Hard-example mining** (§6.1 Step 3): top 5% val loss + **all** safety false
  negatives → annotate/correct → 1 epoch at LR 1e-6. Skip in future retrains if it
  improves val <1% relative.
- **Serving spike (timeboxed)** (§4, §6.1 Step 4): Track A (GPU FP16) stand-up +
  Track B (CPU/ONNX) feasibility.
- **Week-10 iteration buffer:** if eval/latency targets are missed — second run,
  task-weighting change, or serving-track switch.

## Exit gate (§7 targets on the Protocol B set, mean ± std over ≥3 seeds)

| Metric | Target | If below |
|---|---|---|
| severity MAE | < 0.15 | oversample high-severity, retrain |
| energy MAE | < 0.15 | (if retained) weight human 3× or discretize |
| socialIsolation MAE | < 0.20 | drop → keyword heuristic |
| receptivity MAE | < 0.20 | revise definition / binary |
| emotion macro-F1 | > 0.65 | collapse labels, retrain |
| safety recall | > 0.95 | else safety output **supplementary only** |
| safety precision | > 0.70 | check if FPs are borderline |
| 0.5–0.8 band MAE | ≤ 0.15 | **do not deploy** — add band examples, retrain |
| latency p95 | < 300ms | GPU meets; CPU/ONNX verify in spike |

## Decision

If NeoBERT underperforms the Gemini-Lite baseline **or** serving is intractable →
**pivot down the fallback ladder** (recovers most of the ~2 extra weeks).

**Next:** [Phase 7 — Serving Build & Integration](07-serving-integration.md)
