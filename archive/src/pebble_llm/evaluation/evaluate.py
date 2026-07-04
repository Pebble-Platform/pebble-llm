"""Run the Protocol B evaluation and check against §7 targets.

TODO: load the trained checkpoint, run inference over the test split, compute the
metrics in metrics.py, and emit a pass/fail report per dimension. No deployment is
allowed without a completed Protocol B evaluation (§6.1 Step 5).
"""

from __future__ import annotations

from pebble_llm.evaluation.metrics import TARGETS


def check_targets(results: dict[str, float]) -> dict[str, bool]:
    """Return per-metric pass/fail. MAE/latency are 'lower is better'; others higher."""
    lower_is_better = {"severity_mae", "energy_mae", "social_isolation_mae",
                       "receptivity_mae", "latency_p95_ms"}
    passed: dict[str, bool] = {}
    for name, target in TARGETS.items():
        if name not in results:
            continue
        passed[name] = (
            results[name] <= target if name in lower_is_better else results[name] >= target
        )
    return passed
