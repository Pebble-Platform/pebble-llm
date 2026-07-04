"""Run GoEmotions emotion-head pre-training (§6.1 Step 1).

Usage: uv run python scripts/run_pretrain.py --config configs/training/pretrain_emotion.yaml
"""

from __future__ import annotations

import argparse

from pebble_llm.config import load_config
from pebble_llm.training.pretrain_emotion import pretrain_emotion_head


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/training/pretrain_emotion.yaml")
    args = parser.parse_args()
    cfg = load_config(args.config)
    pretrain_emotion_head(cfg)


if __name__ == "__main__":
    main()
