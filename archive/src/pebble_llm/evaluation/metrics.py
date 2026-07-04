"""Evaluation metrics + targets (strategy §7).

All metrics are computed on the 500-sample, 100 %-human-annotated Protocol B test
set (unanchored), reported as mean ± std over >=3 seeds for the NeoBERT path.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score  # type: ignore[import-untyped]

# Targets from §7. "If below" actions live in the strategy doc.
TARGETS: dict[str, float] = {
    "severity_mae": 0.15,
    "energy_mae": 0.15,
    "social_isolation_mae": 0.20,
    "receptivity_mae": 0.20,
    "emotion_macro_f1": 0.65,
    "safety_recall": 0.95,
    "safety_precision": 0.70,
    "latency_p95_ms": 300.0,
}


def mae(pred: np.ndarray, target: np.ndarray) -> float:
    return float(np.mean(np.abs(pred - target)))


def emotion_macro_f1(pred_ids: np.ndarray, target_ids: np.ndarray) -> float:
    return float(f1_score(target_ids, pred_ids, average="macro"))


def safety_metrics(pred_flags: np.ndarray, target_flags: np.ndarray) -> dict[str, float]:
    return {
        "safety_recall": float(recall_score(target_flags, pred_flags, zero_division=0)),
        "safety_precision": float(precision_score(target_flags, pred_flags, zero_division=0)),
    }


@dataclass
class SeedResults:
    """Per-seed metric values, aggregated to mean ± std (§7)."""

    values: dict[str, list[float]]

    def summary(self) -> dict[str, tuple[float, float]]:
        return {k: (float(np.mean(v)), float(np.std(v))) for k, v in self.values.items()}


def severity_band_mae(
    pred: np.ndarray, target: np.ndarray, low: float = 0.5, high: float = 0.8
) -> float:
    """MAE restricted to the 0.5-0.8 moderate-severity blind spot (§8.3).

    If this exceeds 0.15, DO NOT DEPLOY — add human-annotated examples in this band
    and retrain.
    """
    mask = (target >= low) & (target <= high)
    if not mask.any():
        return float("nan")
    return mae(pred[mask], target[mask])
