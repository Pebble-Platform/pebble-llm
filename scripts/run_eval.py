"""Evaluate a checkpoint on the Protocol B test set and check §7 targets.

Usage: uv run python scripts/run_eval.py --config configs/training/multitask.yaml
No deployment is allowed without a completed Protocol B evaluation (§6.1 Step 5).
"""

from __future__ import annotations

import argparse

from pebble_llm.config import load_config
from pebble_llm.evaluation.evaluate import check_targets
from pebble_llm.utils.logging import get_logger

logger = get_logger("run_eval")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/training/multitask.yaml")
    args = parser.parse_args()
    _ = load_config(args.config)

    # TODO: load checkpoint, run inference over the test split, compute metrics.
    results: dict[str, float] = {}
    for name, passed in check_targets(results).items():
        logger.info("%s: %s", name, "PASS" if passed else "FAIL")


if __name__ == "__main__":
    main()
