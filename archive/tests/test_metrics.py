import numpy as np

from pebble_llm.evaluation.evaluate import check_targets
from pebble_llm.evaluation.metrics import mae, severity_band_mae


def test_mae_zero_for_identical():
    a = np.array([0.1, 0.5, 0.9])
    assert mae(a, a) == 0.0


def test_severity_band_filters_to_moderate_zone():
    pred = np.array([0.0, 0.6, 0.7])
    target = np.array([0.0, 0.6, 0.7])  # only the last two fall in [0.5, 0.8]
    assert severity_band_mae(pred, target) == 0.0


def test_check_targets_lower_vs_higher():
    results = {"severity_mae": 0.10, "safety_recall": 0.96}
    passed = check_targets(results)
    assert passed["severity_mae"] is True  # 0.10 <= 0.15
    assert passed["safety_recall"] is True  # 0.96 >= 0.95


def test_check_targets_flags_failure():
    assert check_targets({"severity_mae": 0.30})["severity_mae"] is False
