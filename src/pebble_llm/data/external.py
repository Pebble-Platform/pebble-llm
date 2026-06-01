"""Loaders for external transfer-learning datasets (strategy §5.1).

These warm-start the model before Pebble fine-tuning. They matter MORE on the
NeoBERT path than they would on Gemini because the encoder's heads start random
and the Pebble set is small (§5.3).

  - GoEmotions          → emotion head pre-training (mapped via taxonomy.py)
  - EmpatheticDialogues → multi-turn context, closest structural match
  - DailyDialog         → weak `receptivity` signal (act labels; noisy, §3.4)
  - SemEval-2025 Task 11→ strongest `severity` transfer (intensity ≈ severity)
  - WASSA 2023/2024     → augmentation/validation only (small)
  - TalkLife            → restricted DUA, off critical path (OQ1)

Most load via HuggingFace `datasets`. Stubs below mark the integration points.
"""

from __future__ import annotations

from datasets import Dataset, load_dataset  # type: ignore[import-untyped]

from pebble_llm.data.taxonomy import map_goemotions


def load_goemotions_for_emotion_head() -> Dataset:
    """Load GoEmotions (simplified) and remap its labels to the Pebble taxonomy.

    GoEmotions is multi-label; we take the first/primary label per example for the
    single-label emotion head and remap it. Examples with only filtered-out labels
    fall back to 'neutral'.
    """
    ds = load_dataset("go_emotions", "simplified", split="train")
    label_names: list[str] = ds.features["labels"].feature.names

    def _remap(row: dict) -> dict:
        primary = label_names[row["labels"][0]] if row["labels"] else "neutral"
        return {"text": row["text"], "pebble_label": map_goemotions(primary)}

    return ds.map(_remap, remove_columns=ds.column_names)


def load_empathetic_dialogues() -> Dataset:
    """TODO: load facebook/empathetic_dialogues; use speaker turns as examples."""
    raise NotImplementedError("EmpatheticDialogues loader not implemented yet (§5.1).")


def load_semeval_intensity() -> Dataset:
    """TODO: load SemEval-2025 Task 11 intensity for `severity` transfer (§5.1)."""
    raise NotImplementedError("SemEval intensity loader not implemented yet (§5.1).")
