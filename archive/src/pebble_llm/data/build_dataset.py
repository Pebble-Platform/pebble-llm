"""Assemble the v1 transfer-learning splits → data/finetuning-message/processed/ (Phase 5 Task 1; §5.5).

Two DISJOINT public pools feed two heads:
  - GoEmotions     → emotion head  (detectedEmotion)
  - SemEval EI-reg → score head    (severity)

No public example carries BOTH labels, so every record gets a per-task ``mask``
and the Phase-6 multi-task loss ignores the absent head. Neither source has a
userId, so the user-level split (``data/splits.py``) is N/A for this transfer
pool — we reuse each dataset's own train / val(dev) / test partitions. Output is
one JSONL file per split under ``processed_dir``. Safety is never a learned head
in v1 (heuristic only — see docs/decisions.md), so its mask is always 0.
"""

from __future__ import annotations

import json
from pathlib import Path

from pebble_llm.data.external import (
    load_goemotions_for_emotion_head,
    load_semeval_intensity,
)
from pebble_llm.data.taxonomy import LABEL_TO_ID

# Our split name → each source's own partition name.
_GOEMOTIONS_SPLITS = {"train": "train", "val": "validation", "test": "test"}
_EIREG_SPLITS = {"train": "train", "val": "dev", "test": "test"}


def emotion_record(text: str, pebble_label: str) -> dict[str, object]:
    """GoEmotions row → masked record: emotion head active, score/safety masked off."""
    return {
        "text": text,
        "emotion_id": LABEL_TO_ID[pebble_label],
        "severity": 0.0,
        "safety_flag": 0,
        "mask": {"emotion": 1, "score": 0, "safety": 0},
    }


def severity_record(text: str, severity: float) -> dict[str, object]:
    """EI-reg row → masked record: score head active, emotion/safety masked off.

    ``emotion_id`` is a placeholder (-1); the ``mask`` — not this value — governs
    whether the emotion head contributes to the loss for this example.
    """
    return {
        "text": text,
        "emotion_id": -1,
        "severity": float(severity),
        "safety_flag": 0,
        "mask": {"emotion": 0, "score": 1, "safety": 0},
    }


def build_split(split: str, external_dir: Path | str = "data/finetuning-message/external") -> list[dict[str, object]]:
    """Combine the GoEmotions + EI-reg partitions for one split into masked records."""
    if split not in _GOEMOTIONS_SPLITS:
        raise ValueError(f"split must be one of {sorted(_GOEMOTIONS_SPLITS)}, got {split!r}")
    emo = load_goemotions_for_emotion_head(_GOEMOTIONS_SPLITS[split])
    sev = load_semeval_intensity(_EIREG_SPLITS[split], external_dir=external_dir)
    records = [emotion_record(r["text"], r["pebble_label"]) for r in emo]
    records += [severity_record(r["text"], r["severity"]) for r in sev]
    return records


def write_processed(processed_dir: Path | str = "data/finetuning-message/processed") -> dict[str, int]:
    """Build all three splits and write ``data/finetuning-message/processed/<split>.jsonl``. Returns row counts."""
    out_dir = Path(processed_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for split in _GOEMOTIONS_SPLITS:
        records = build_split(split)
        with (out_dir / f"{split}.jsonl").open("w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec) + "\n")
        counts[split] = len(records)
    return counts


if __name__ == "__main__":
    print(write_processed())
