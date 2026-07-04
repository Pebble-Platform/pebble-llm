"""Run multi-task fine-tuning across seeds and report mean ± std (§6.1 Step 2, §7).

Usage: uv run python scripts/run_train.py --config configs/training/multitask.yaml
"""

from __future__ import annotations

import argparse

from torch.utils.data import DataLoader
from transformers import AutoTokenizer  # type: ignore[import-untyped]

from pebble_llm.config import Config, load_config
from pebble_llm.data.datasets import MaskedMultiTaskDataset
from pebble_llm.evaluation.metrics import SeedResults
from pebble_llm.training.trainer import train
from pebble_llm.utils.logging import get_logger

logger = get_logger("run_train")


def _build_loaders(cfg: Config, tokenizer: object) -> tuple[DataLoader, DataLoader]:
    processed = cfg.data.processed_dir
    train_ds = MaskedMultiTaskDataset.from_jsonl(
        processed / "train.jsonl", tokenizer, cfg.model.score_dims, cfg.data.max_seq_length
    )
    val_ds = MaskedMultiTaskDataset.from_jsonl(
        processed / "val.jsonl", tokenizer, cfg.model.score_dims, cfg.data.max_seq_length
    )
    train_loader = DataLoader(
        train_ds, batch_size=cfg.training.batch_size, shuffle=True, num_workers=2, pin_memory=True
    )
    val_loader = DataLoader(
        val_ds, batch_size=cfg.training.batch_size * 2, shuffle=False, num_workers=2, pin_memory=True
    )
    return train_loader, val_loader


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/training/multitask.yaml")
    args = parser.parse_args()
    cfg = load_config(args.config)

    tokenizer = AutoTokenizer.from_pretrained(
        cfg.model.name, revision=cfg.model.revision, trust_remote_code=cfg.model.trust_remote_code
    )
    train_loader, val_loader = _build_loaders(cfg, tokenizer)

    results: dict[str, list[float]] = {}
    for seed in cfg.training.seeds:
        logger.info("=== seed %d ===", seed)
        metrics = train(cfg, train_loader, val_loader, seed)
        for k, v in metrics.items():
            results.setdefault(k, []).append(v)

    if results:
        for name, (mean, std) in SeedResults(results).summary().items():
            logger.info("%s: %.4f ± %.4f", name, mean, std)


if __name__ == "__main__":
    main()
