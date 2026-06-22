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

import json
from dataclasses import dataclass
from pathlib import Path

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


class MaskedMultiTaskDataset(Dataset[dict[str, torch.Tensor]]):
    """Masked multi-task records from ``build_dataset.py`` (Phase 5 → Phase 6).

    Each ``data/finetuning-message/processed/<split>.jsonl`` row carries the disjoint-pool mask
    ``{emotion, score, safety}`` (only the head that the row actually labels is
    active). ``__getitem__`` emits flat ``mask_<head>`` tensors that the masked
    ``MultiTaskLoss`` consumes. ``emotion_id`` may be ``-1`` (placeholder for
    non-emotion rows); the mask — not this value — governs inclusion.
    """

    def __init__(
        self,
        records: list[dict[str, object]],
        tokenizer: object,  # transformers.PreTrainedTokenizerBase
        score_dims: list[str],
        max_length: int = 256,
    ) -> None:
        self.records = records
        self.tokenizer = tokenizer
        self.score_dims = score_dims
        self.max_length = max_length

    @classmethod
    def from_jsonl(
        cls,
        path: Path | str,
        tokenizer: object,
        score_dims: list[str],
        max_length: int = 256,
    ) -> MaskedMultiTaskDataset:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        records = [json.loads(line) for line in lines if line.strip()]
        return cls(records, tokenizer, score_dims, max_length)

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        rec = self.records[idx]
        mask = rec["mask"]  # type: ignore[index]
        enc = self.tokenizer(  # type: ignore[operator]
            rec["text"],
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "scores": torch.tensor(
                [float(rec.get(d, 0.0)) for d in self.score_dims], dtype=torch.float  # type: ignore[attr-defined]
            ),
            "emotion_id": torch.tensor(int(rec["emotion_id"]), dtype=torch.long),  # type: ignore[arg-type]
            "safety_flag": torch.tensor(float(rec["safety_flag"]), dtype=torch.float),  # type: ignore[arg-type]
            "mask_score": torch.tensor(float(mask["score"]), dtype=torch.float),  # type: ignore[index]
            "mask_emotion": torch.tensor(float(mask["emotion"]), dtype=torch.float),  # type: ignore[index]
            "mask_safety": torch.tensor(float(mask["safety"]), dtype=torch.float),  # type: ignore[index]
        }
