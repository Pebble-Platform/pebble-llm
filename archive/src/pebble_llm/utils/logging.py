"""Logging + experiment-tracking init (strategy §6.1 Step 5, §9).

Every run logs hyperparameters, per-epoch and per-seed metrics, confusion matrices,
checkpoints, and the training-data snapshot id to W&B (or MLflow). Every deployed
version must trace to its data snapshot + config + Protocol B eval.
"""

from __future__ import annotations

import logging


def get_logger(name: str = "pebble_llm") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
