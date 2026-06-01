"""Run multi-task fine-tuning across seeds and report mean ± std (§6.1 Step 2, §7).

Usage: uv run python scripts/run_train.py --config configs/training/multitask.yaml
"""

from __future__ import annotations

import argparse

from pebble_llm.config import load_config
from pebble_llm.evaluation.metrics import SeedResults
from pebble_llm.utils.logging import get_logger

logger = get_logger("run_train")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/training/multitask.yaml")
    args = parser.parse_args()
    cfg = load_config(args.config)

    results: dict[str, list[float]] = {}
    for seed in cfg.training.seeds:
        logger.info("=== seed %d ===", seed)
        # TODO: build train/val DataLoaders from data/processed, then:
        #   from pebble_llm.training.trainer import train
        #   metrics = train(cfg, train_loader, val_loader, seed)
        #   for k, v in metrics.items(): results.setdefault(k, []).append(v)
        logger.info("seed %d: wire DataLoaders + trainer.train()", seed)

    if results:
        for name, (mean, std) in SeedResults(results).summary().items():
            logger.info("%s: %.4f ± %.4f", name, mean, std)


if __name__ == "__main__":
    main()
