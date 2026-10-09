"""Build the full-corpus queue consumed by /gold.html.

This is deliberately separate from gold-candidates.tsv: these rows are clips to be
reviewed, not clips already considered obvious enough to become gold anchors.
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "labeler"))
import store


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="build the full-corpus review queue")
    ap.add_argument("--root", default="data/vietnamese-ser/episodes")
    ap.add_argument(
        "--out", default="docs/spec/changes/011-online-multi-annotator/review-candidates.tsv"
    )
    ap.add_argument("--seed", type=int, default=1128)
    a = ap.parse_args()

    root = Path(a.root).resolve()
    store.set_root(root)
    store.load()
    rows = sorted(
        (r for r in store.STATE.values() if r.get("emotion") and not r.get("rejected")),
        key=lambda r: (r["epKey"], r["id"]),
    )
    rows = [r for r in rows if (root / r["epKey"] / "clips" / f"{r['id']}.wav").is_file()]
    random.Random(a.seed).shuffle(rows)

    lines = ["# epKey/clip_id\temotion\twav, relative to --root (full-corpus review queue)"]
    lines.extend(
        f"{r['epKey']}/{r['id']}\t{r['emotion']}\t{r['epKey']}/clips/{r['id']}.wav" for r in rows
    )
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"review candidates: {len(rows)} -> {out}")


if __name__ == "__main__":
    main()
