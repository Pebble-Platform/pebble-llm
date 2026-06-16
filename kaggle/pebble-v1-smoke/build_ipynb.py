"""Assemble the two cell sources into a Kaggle notebook (.ipynb)."""
import json, pathlib

here = pathlib.Path(__file__).parent
def cell(path):
    src = (here / path).read_text(encoding="utf-8").splitlines(keepends=True)
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": src}

nb = {
    "cells": [cell("_cell_install.py"), cell("_cell_body.py")],
    "metadata": {
        "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4, "nbformat_minor": 5,
}
out = here / "pebble_v1_smoke.ipynb"
out.write_text(json.dumps(nb, indent=1), encoding="utf-8")
print("wrote", out)
