"""Assemble the multi-block Kaggle notebook (markdown headers + one code cell per block)."""
import json, pathlib

here = pathlib.Path(__file__).parent
def code(path):
    src = (here / path).read_text(encoding="utf-8").splitlines(keepends=True)
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": src}
def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}

cells = [
    md("# Pebble v1 — Stage 1: MLM pre-training + isolation ablation\n\n"
       "Run the blocks top-to-bottom. State carries across cells, so each block "
       "uses what the previous one defined. Plan ref: `improvement-plan-from-deep-read.md` 1.3 / D-F."),
    md("## 0. Install pinned NeoBERT stack  (run once, ~4 min)"),
    code("_cell_install.py"),
    md("## 1. Imports & config"),
    code("c1_imports.py"),
    md("## 2. Tokenizer & data  (GoEmotions -> emotion, SemEval EI-reg -> severity)"),
    code("c2_data.py"),
    md("## 3. MLM pre-training — 30% masking on in-domain text\nWatch the loss drop across epochs."),
    code("c3_mlm_train.py"),
    md("## 4. Save the adapted encoder  (the reusable artifact)"),
    code("c4_save_encoder.py"),
    md("## 5. Fine-tune setup — masked two-pool multi-task"),
    code("c5_ft_setup.py"),
    md("## 6. Ablation arm A — MLM-OFF (vanilla NeoBERT)"),
    code("c6_arm_off.py"),
    md("## 7. Ablation arm B — MLM-ON (adapted encoder)"),
    code("c7_arm_on.py"),
    md("## 8. Results table"),
    code("c8_results.py"),
]
nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4, "nbformat_minor": 5,
}
out = here / "pebble_mlm_ablation.ipynb"
out.write_text(json.dumps(nb, indent=1), encoding="utf-8")
print("wrote", out, "with", len(cells), "cells")
