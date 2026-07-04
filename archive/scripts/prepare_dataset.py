"""Build the training/val/test datasets (strategy §5.5).

Pipeline:
  1. Ingest Gemini silver labels from Firestore (data/silver_labels.py).
  2. Filter fallbacks; run the energy/severity independence check (§5.2).
  3. Merge human-corrected (Protocol A) + safety-augmented positives (§5.4).
  4. User-level split (data/splits.py), then stratify by severity quartile.
  5. Export processed splits to data/finetuning-message/processed/.

This is the entry point — fill the TODOs as the data sources come online.
"""

from __future__ import annotations

from pebble_llm.utils.logging import get_logger

logger = get_logger("prepare_dataset")


def main() -> None:
    logger.info("Dataset preparation is a scaffold — wire silver-label ingestion + splits.")
    raise SystemExit("Not implemented yet — see TODOs and strategy §5.5.")


if __name__ == "__main__":
    main()
