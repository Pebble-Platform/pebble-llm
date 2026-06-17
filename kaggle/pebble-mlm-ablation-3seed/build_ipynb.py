"""Assemble the multi-block 3-seed Kaggle notebook (markdown headers + one code cell per block)."""
import json, pathlib

here = pathlib.Path(__file__).parent
def code(path):
    src = (here / path).read_text(encoding="utf-8").splitlines(keepends=True)
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": src}
def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}

cells = [
    md("# Pebble v1 — MLM isolation ablation (3 seeds, scaled corpus)\n\n"
       "Run the blocks top-to-bottom; state carries across cells. The encoder is adapted "
       "ONCE on a big *separate* in-domain corpus (block s3/s4), then BOTH arms are fine-tuned "
       "across 3 seeds for a paired delta. Re-run s5–s7 to retune fine-tuning without redoing MLM."),
    md("## 0. Install pinned NeoBERT stack  (run once, ~4 min)"),
    code("_cell_install.py"),
    md("## 1. Imports & config  (15% masking, 80k corpus cap)"),
    code("s1_imports.py"),
    md("## 2. Downstream data  (GoEmotions -> emotion, EI-reg -> severity) + dedup guard"),
    code("s2_data.py"),
    md("## 3. Build the big SEPARATE MLM corpus  (GoEmotions raw + tweet_eval, deduped)"),
    code("s3_mlm_corpus.py"),
    md("## 4. MLM pre-training (15% masking) -> save adapted encoder (fp32)\nRun once; watch the loss drop."),
    code("s4_mlm_train.py"),
    md("## 5. Fine-tune setup — masked two-pool multi-task"),
    code("s5_ft_setup.py"),
    md("## 6. Run both arms across 3 seeds  (incremental CSV checkpoint per seed)"),
    code("s6_run_seeds.py"),
    md("## 7. Results table — mean +/- std + paired per-seed delta"),
    code("s7_results.py"),
    md("## 8. Export a shippable model + inference demo  (train once on chosen arm, save, test)"),
    code("s8_export_infer.py"),
]
nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4, "nbformat_minor": 5,
}
out = here / "pebble_mlm_ablation_3seed.ipynb"
out.write_text(json.dumps(nb, indent=1), encoding="utf-8")
print("wrote", out, "with", len(cells), "cells")
