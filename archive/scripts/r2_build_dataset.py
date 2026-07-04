"""Merge all C-SSRS 4-level sources into ONE combined file for the R2 model.

Sources:
  1. CSSRS-500 (Gaur, Zenodo) — 4-level user-sequences (drop "Supportive").
  2. av9ash CSSR-S — r/SuicideWatch posts on the 0-6 C-SSRS scale → map to 4-level (1-post seqs).
  3. Scraped + LLM-labeled SuicideWatch sequences (scripts/r2_llm_label.py) — 4-level, confidence-filtered.

Output: data/finetuning-message/external/r2-combined/sequences.csv  (cols: User,Post,Label,Source)
matching the CSSRS-500 schema, so the training script reads it via  R2_DATA=<path>  with no loader change.
Post = repr(list[str]); Label = one of Indicator/Ideation/Behavior/Attempt.

Usage:
    .venv-voice/bin/python scripts/r2_build_dataset.py --min-confidence 0.6
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import re
from collections import Counter
from pathlib import Path

_WS = re.compile(r"\s+")


def _norm(text: str) -> str:
    """Light normalization: collapse runs of whitespace/newlines to single spaces, strip.
    No lowercasing / URL-stripping — MentalRoBERTa is cased and the tokenizer handles those."""
    return _WS.sub(" ", text).strip()

EXT = Path("data/finetuning-message/external")
OUT = EXT / "r2-combined" / "sequences.csv"
LABEL_NAMES = ["Indicator", "Ideation", "Behavior", "Attempt"]
LABEL_MAP = {"Indicator": 0, "Ideation": 1, "Behavior": 2, "Attempt": 3}
# standard C-SSRS 7-point (0-6) → paper's 4-level
SEV6_TO_4 = {0: 0, 1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 3}


def _parse_posts(cell: str) -> list[str]:
    try:
        v = ast.literal_eval(cell)
        if isinstance(v, list) and v:
            return [str(x) for x in v if str(x).strip()]
    except Exception:
        pass
    s = cell.strip("[]").strip()
    return [s] if s else []


def from_cssrs500() -> list[tuple[list[str], int]]:
    path = EXT / "cssrs" / "500_Reddit_users_posts_labels.csv"
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            lab = r["Label"].strip()
            if lab not in LABEL_MAP:          # drop Supportive
                continue
            posts = _parse_posts(r["Post"])[-5:]
            if posts:
                rows.append((posts, LABEL_MAP[lab]))
    return rows


def from_av9ash() -> list[tuple[list[str], int]]:
    path = EXT / "cssrs-llm-av9ash" / "labeled_rSuicidewatch_posts.csv"
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            sev = r.get("severity", "").strip()
            text = (r.get("content") or "").strip()
            if not text or not sev.isdigit():
                continue
            lab = SEV6_TO_4.get(int(sev))
            if lab is not None:
                rows.append(([text], lab))
    return rows


def from_scraped(min_conf: float) -> list[tuple[list[str], int]]:
    path = EXT / "scraped-suicidewatch" / "labeled.jsonl"
    if not path.exists():
        return []
    rows = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        o = json.loads(line)
        if float(o.get("confidence", 0)) < min_conf:
            continue
        posts = [p["text"] for p in o["posts"] if p.get("text", "").strip()]
        if posts and o["label"] in (0, 1, 2, 3):
            rows.append((posts[-5:], int(o["label"])))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-confidence", type=float, default=0.6)
    args = ap.parse_args()

    sources = {
        "cssrs500": from_cssrs500(),
        "av9ash": from_av9ash(),
        "scraped": from_scraped(args.min_confidence),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    dist = Counter()
    per_src = Counter()
    seen: set[str] = set()                 # global dedup by normalized sequence text
    dropped_dup = 0
    records = []                            # for the JSON viewer
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["User", "Post", "Label", "Source"])
        for src, rows in sources.items():
            for i, (posts, lab) in enumerate(rows):
                posts = [_norm(p) for p in posts if _norm(p)]
                if not posts:
                    continue
                key = "\n".join(posts)
                if key in seen:
                    dropped_dup += 1
                    continue
                seen.add(key)
                uid = f"{src}-{i}"
                w.writerow([uid, repr(posts), LABEL_NAMES[lab], src])
                records.append({"id": uid, "source": src, "label": LABEL_NAMES[lab],
                                "posts": posts})
                dist[LABEL_NAMES[lab]] += 1
                per_src[src] += 1
                total += 1

    (OUT.parent / "sequences.json").write_text(json.dumps(records, ensure_ascii=False))

    print(f">>> combined → {OUT}  (normalized: whitespace-collapsed, deduped)")
    for src in sources:
        print(f"    {src:10s}: {per_src[src]}")
    print(f"    {'TOTAL':10s}: {total}  (dropped {dropped_dup} duplicate sequences)")
    print(f">>> class dist: {dict(dist)} (conf>={args.min_confidence} for scraped)")


if __name__ == "__main__":
    main()
