# Serving (capability — STUB, deferred / further work)

> **Status:** stub — **out of scope** for the current research intent (see
> `docs/intent/constraints.md`: production deployment is deferred until the
> research validates quality). Authoritative detail (for when it is revived)
> lives in `src/pebble_llm/serving/` and `pebble-finetuning-strategy-v3.md` §3–4.
> Not owned by a `001` phase.

**What it covers (when revived):** the FastAPI `/classify` endpoint and its
structured output schema (`energy`, `severity`, `socialIsolation`,
`receptivity`, `detectedEmotion`, `safetyFlag`), checkpoint loading, and the
GPU-FP16 vs CPU/ONNX serving-direction decision (OQ6, deferred). The deploy
gates from the strategy (safetyFlag recall ≥ 0.95, severity-band MAE ≤ 0.15)
re-activate only if/when this capability is built.
