"""Assemble the voice-backbone Kaggle notebook (markdown headers + one code cell per block)."""
import json, pathlib

here = pathlib.Path(__file__).parent
def code(path):
    src = (here / path).read_text(encoding="utf-8").splitlines(keepends=True)
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": src}
def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}

cells = [
    md("# Pebble voice — frozen speech-encoder backbone selection\n\n"
       "**emotion2vec (primary) vs WavLM-Large (baseline)** for crisis-sensitive speech affect.\n"
       "Pebble's heterogeneous heads (emotion softmax + a high-distress recall head) on RAVDESS, "
       "3 seeds, paired delta. Mirrors `pebble-mlm-3seed`. Ref: `docs/voice-method-selection.md`."),
    md("## 0. Install pinned audio stack  (run once)"),
    code("_cell_install.py"),
    md("## 1. Imports & config"),
    code("c1_imports.py"),
    md("## 2. RAVDESS data  (resample 48k->16k, speaker-independent split)"),
    code("c2_data.py"),
    md("## 3. Frozen feature extraction  (each encoder runs once)"),
    code("c3_features.py"),
    md("## 4. Multi-task probe  (emotion softmax + distress BCE, 3 seeds, recall floor)"),
    code("c4_probe.py"),
    md("## 5. Results + serving artifacts"),
    code("c5_results.py"),
]
nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4, "nbformat_minor": 5,
}
out = here / "pebble_voice_backbone.ipynb"
out.write_text(json.dumps(nb, indent=1), encoding="utf-8")
print("wrote", out, "with", len(cells), "cells")
