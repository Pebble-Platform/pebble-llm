# Notebooks

Exploratory analysis only — nothing here is part of the training/serving path.
Keep reusable logic in `src/pebble_llm/`, not in notebooks. Clear outputs before
committing (`.ipynb_checkpoints/` is gitignored).

Suggested notebooks:

- `01_eda.ipynb` — silver-label distributions, per-dimension histograms.
- `02_energy_severity_independence.ipynb` — the §5.2 Week-2 correlation check.
- `03_annotation_agreement.ipynb` — Krippendorff α / Cohen κ for the pilot gates.
- `04_taxonomy_confusion.ipynb` — pairwise label confusion for the §3.2 pilot.
