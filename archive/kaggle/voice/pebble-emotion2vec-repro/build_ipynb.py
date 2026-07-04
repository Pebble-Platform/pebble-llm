"""Assemble the emotion2vec-reproduction Kaggle notebook (markdown headers + one code cell per block)."""
import json, pathlib

here = pathlib.Path(__file__).parent
def code(path):
    src = (here / path).read_text(encoding="utf-8").splitlines(keepends=True)
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": src}
def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}

cells = [
    md("# Reproduce emotion2vec (ACL Findings 2024) — RAVDESS linear probe\n\n"
       "Frozen **emotion2vec_base** (+ **WavLM-Large** comparator) + a **SUPERB linear probe**, "
       "**random 10-fold CV (80/10/10), all 1440 speech clips, 8 classes**, reporting **WA/UA/WF1** "
       "against the paper's Table 3 (emotion2vec RAVDESS = WA 82.43 / UA 82.86 / WF1 82.39).\n"
       "Protocol + sources: `docs/tasks/emotion2vec-reproduction.md`."),
    md("## 0. Install pinned audio stack  (run once)"),
    code("_cell_install.py"),
    md("## 1. Imports & config"),
    code("c1_imports.py"),
    md("## 2. RAVDESS data  (all 1440 clips, resample 48k->16k, no fixed split)"),
    code("c2_data.py"),
    md("## 3. Frozen feature extraction  (each encoder runs once over all clips)"),
    code("c3_features.py"),
    md("## 4. SUPERB linear probe  (random 10-fold CV, WA/UA/WF1)"),
    code("c4_probe.py"),
    md("## 5. Results vs paper + artifacts"),
    code("c5_results.py"),
    md("## 6. Demo inference on held-out clips  (tests emotion2vec too)"),
    code("c6_demo.py"),
]
nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4, "nbformat_minor": 5,
}
out = here / "pebble_emotion2vec_repro.ipynb"
out.write_text(json.dumps(nb, indent=1), encoding="utf-8")
print("wrote", out, "with", len(cells), "cells")
