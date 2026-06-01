"""Vendor NeoBERT's custom modeling code at a pinned revision (strategy §6.1 Step 0).

Vendoring protects against silent upstream changes to code loaded via
`trust_remote_code=True`. Run after bumping PINNED_REVISION (and the matching
`model.revision` in configs/).

    uv run python scripts/vendor_neobert.py

Downloads only the modeling files (model.py, rotary.py, config.json) — not weights.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = "https://huggingface.co/chandar-lab/NeoBERT"
PINNED_REVISION = "5424c8efeea6491b151d62dee55a752165407430"
VENDOR_FILES = ["model.py", "rotary.py", "config.json"]
DEST = Path(__file__).resolve().parents[1] / "src" / "pebble_llm" / "models" / "_neobert_vendor"


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            ["git", "clone", "--depth", "1", REPO, tmp],
            check=True,
            env={"GIT_LFS_SKIP_SMUDGE": "1"},  # skip the LFS weights
        )
        subprocess.run(["git", "-C", tmp, "checkout", PINNED_REVISION], check=True)
        DEST.mkdir(parents=True, exist_ok=True)
        for name in VENDOR_FILES:
            shutil.copy2(Path(tmp) / name, DEST / name)
    print(f"Vendored {VENDOR_FILES} at {PINNED_REVISION} → {DEST}")


if __name__ == "__main__":
    main()
