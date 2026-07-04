"""Assemble the voice-MTL-heads Kaggle notebook (markdown headers + one code cell per block)."""
import json, pathlib

here = pathlib.Path(__file__).parent
def code(path):
    src = (here / path).read_text(encoding="utf-8").splitlines(keepends=True)
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": src}
def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}

cells = [
    md("# Voice MTL heads — emotion + affect (CCC) + crisis (recall floor)\n\n"
       "Frozen **emotion2vec_base** / **WavLM-Large** -> a shared **SUPERB trunk** -> **three heads**: "
       "emotion (8-way CE), affect regression (valence+arousal, **CCC**), and a **crisis** head (BCE) "
       "under a **hard recall floor**, balanced by **Kendall uncertainty weighting**. RAVDESS has no "
       "continuous/crisis labels, so the two new heads learn **proxy** targets (Russell circumplex V/A; "
       "high-distress emotion set). Validates the multi-head + recall-floor mechanics; real numbers need "
       "MSP-Podcast / DAIC. Protocol + rationale: `docs/tasks/voice-mtl-heads.md`."),
    md("## 0. Install pinned audio stack  (run once)"),
    code("_cell_install.py"),
    md("## 1. Imports & config"),
    code("c1_imports.py"),
    md("## 2. RAVDESS data  (all 1440 clips, resample 48k->16k, no fixed split)"),
    code("c2_data.py"),
    md("## 3. Frozen feature extraction  (each encoder runs once over all clips)"),
    code("c3_features.py"),
    md("## 4. 3-head MTL probe  (random 10-fold CV; Kendall weighting; recall floor)"),
    code("c4_heads.py"),
    md("## 5. Results + artifacts"),
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
out = here / "pebble_voice_mtl_heads.ipynb"
out.write_text(json.dumps(nb, indent=1), encoding="utf-8")
print("wrote", out, "with", len(cells), "cells")
