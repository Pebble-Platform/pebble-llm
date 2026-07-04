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

import csv
import urllib.request
from collections.abc import Iterable
from pathlib import Path

from datasets import Dataset, load_dataset  # type: ignore[import-untyped]

from pebble_llm.data.taxonomy import map_goemotions


def load_goemotions_for_emotion_head(split: str = "train") -> Dataset:
    """Load GoEmotions (simplified) and remap its labels to the Pebble taxonomy.

    GoEmotions is multi-label; we take the first/primary label per example for the
    single-label emotion head and remap it. Examples with only filtered-out labels
    fall back to 'neutral'. ``split`` ∈ {train, validation, test}.
    """
    ds = load_dataset("go_emotions", "simplified", split=split)
    label_names: list[str] = ds.features["labels"].feature.names

    def _remap(row: dict) -> dict:
        primary = label_names[row["labels"][0]] if row["labels"] else "neutral"
        return {"text": row["text"], "pebble_label": map_goemotions(primary)}

    return ds.map(_remap, remove_columns=ds.column_names)


def load_empathetic_dialogues() -> Dataset:
    """TODO: load facebook/empathetic_dialogues; use speaker turns as examples."""
    raise NotImplementedError("EmpatheticDialogues loader not implemented yet (§5.1).")


# --- SemEval-2018 EI-reg → `severity` transfer (strategy §5.1, docs/decisions.md) ---
# EI-reg ships ONE file per emotion (anger/fear/joy/sadness); each tweet carries a
# single real-valued intensity in [0,1]. Negative-valence emotions map to
# `severity = intensity`; joy is a low-distress anchor at 0.0. The chosen
# "mean negative-valence" collapse reduces to the tweet's own intensity because
# each tweet has exactly one emotion. Files are not on the HF Hub, so we download
# the gold TSVs from the ntua-slp mirror on first use and cache them under external_dir.
_EIREG_BASE = (
    "https://raw.githubusercontent.com/cbaziotis/ntua-slp-semeval2018/master/datasets/task1/EI-reg"
)
_EIREG_EMOTIONS = ("anger", "fear", "joy", "sadness")
_EIREG_NEGATIVE = frozenset({"anger", "fear", "sadness"})
_EIREG_SPLIT_FILES = {"train": "train", "dev": "dev", "test": "test-gold"}


def _eireg_severity(emotion: str, intensity: float) -> float:
    """Collapse a per-emotion EI-reg intensity into Pebble `severity` ∈ [0,1]."""
    return intensity if emotion in _EIREG_NEGATIVE else 0.0


def _parse_eireg(lines: Iterable[str], emotion: str) -> list[dict[str, object]]:
    """Parse EI-reg TSV lines → ``[{text, severity}]``.

    Columns: ``ID, Tweet, Affect Dimension, Intensity Score`` (tab-separated). The
    header and any row whose intensity is not a float (e.g. the unlabeled non-gold
    test file) are skipped.
    """
    rows: list[dict[str, object]] = []
    reader = csv.reader(lines, delimiter="\t")
    next(reader, None)  # header row
    for rec in reader:
        if len(rec) < 4:
            continue
        try:
            intensity = float(rec[3])
        except ValueError:
            continue
        rows.append({"text": rec[1], "severity": _eireg_severity(emotion, intensity)})
    return rows


def _ensure_eireg_file(emotion: str, file_split: str, dest_dir: Path) -> Path:
    fname = f"EI-reg-En-{emotion}-{file_split}.txt"
    path = dest_dir / fname
    if not path.exists():
        dest_dir.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(f"{_EIREG_BASE}/{fname}", path)
    return path


def load_semeval_intensity(
    split: str = "train", external_dir: Path | str = "data/finetuning-message/external"
) -> Dataset:
    """Load SemEval-2018 EI-reg as a `severity` transfer set (strategy §5.1).

    Returns rows of ``{text, severity}`` with ``severity`` ∈ [0,1]. The four
    per-emotion files are downloaded on first use into
    ``<external_dir>/semeval2018_eireg/`` and cached. ``split`` ∈
    {``train``, ``dev``, ``test``}; ``test`` uses the gold-labeled test file.
    """
    if split not in _EIREG_SPLIT_FILES:
        raise ValueError(f"split must be one of {sorted(_EIREG_SPLIT_FILES)}, got {split!r}")
    dest_dir = Path(external_dir) / "semeval2018_eireg"
    file_split = _EIREG_SPLIT_FILES[split]
    rows: list[dict[str, object]] = []
    for emotion in _EIREG_EMOTIONS:
        path = _ensure_eireg_file(emotion, file_split, dest_dir)
        with path.open(encoding="utf-8") as f:
            rows.extend(_parse_eireg(f, emotion))
    return Dataset.from_list(rows)


def load_wassa_intensity() -> Dataset:
    """TODO: WASSA 2023/2024 intensity — `severity` augmentation/validation only (§5.1).

    Deferred: the EI-reg primary signal above covers v1. Source/format not yet
    verified (WASSA reuses the EmoInt/AIT lineage); wire once confirmed.
    """
    raise NotImplementedError("WASSA intensity augmentation loader not implemented yet (§5.1).")
