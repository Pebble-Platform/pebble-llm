import json

import torch

from pebble_llm.data.datasets import MaskedMultiTaskDataset


class _StubTokenizer:
    """Offline stand-in for a HF tokenizer (no model download in tests)."""

    def __call__(self, text, truncation, max_length, padding, return_tensors):
        return {
            "input_ids": torch.ones(1, max_length, dtype=torch.long),
            "attention_mask": torch.ones(1, max_length, dtype=torch.long),
        }


def test_masked_dataset_emits_per_head_masks(tmp_path):
    path = tmp_path / "train.jsonl"
    rows = [
        {"text": "a", "emotion_id": 3, "severity": 0.0, "safety_flag": 0,
         "mask": {"emotion": 1, "score": 0, "safety": 0}},
        {"text": "b", "emotion_id": -1, "severity": 0.7, "safety_flag": 0,
         "mask": {"emotion": 0, "score": 1, "safety": 0}},
    ]
    path.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")

    ds = MaskedMultiTaskDataset.from_jsonl(
        path, _StubTokenizer(), score_dims=["severity"], max_length=8
    )
    assert len(ds) == 2

    emo, sev = ds[0], ds[1]
    assert emo["mask_emotion"].item() == 1.0 and emo["mask_score"].item() == 0.0
    assert emo["emotion_id"].item() == 3
    assert sev["mask_score"].item() == 1.0 and sev["mask_emotion"].item() == 0.0
    assert sev["scores"][0].item() == 0.7
    assert sev["emotion_id"].item() == -1  # placeholder; mask governs inclusion
    assert emo["mask_safety"].item() == 0.0  # safety never active in v1
