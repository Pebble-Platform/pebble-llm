"""Torch Dataset for multi-task emotion classification.

A row carries the tokenized input plus the multi-task targets:
  - continuous scores (severity always; energy/receptivity/socialIsolation if they
    survive their viability gates — see config.model.score_dims)
  - one emotion class id (taxonomy.py)
  - a binary safety flag

TODO: wire the real input assembly (current message + last `context_window`
messages, interleaved) once the silver-label schema is finalized (§5.2).
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch.utils.data import Dataset


@dataclass
class Example:
    text: str  # assembled "current message + context" string
    scores: dict[str, float]  # e.g. {"severity": 0.7, "energy": 0.4, ...}
    emotion_id: int
    safety_flag: bool


class EmotionDataset(Dataset[dict[str, torch.Tensor]]):
    def __init__(
        self,
        examples: list[Example],
        tokenizer: object,  # transformers.PreTrainedTokenizerBase
        score_dims: list[str],
        max_length: int = 256,
    ) -> None:
        self.examples = examples
        self.tokenizer = tokenizer
        self.score_dims = score_dims
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        ex = self.examples[idx]
        enc = self.tokenizer(  # type: ignore[operator]
            ex.text,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "scores": torch.tensor([ex.scores[d] for d in self.score_dims], dtype=torch.float),
            "emotion_id": torch.tensor(ex.emotion_id, dtype=torch.long),
            "safety_flag": torch.tensor(float(ex.safety_flag), dtype=torch.float),
        }
