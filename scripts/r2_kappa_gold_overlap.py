"""LLM-label the 392 gold CSSRS-500 eval sequences to measure Cohen's kappa(LLM, gold).

ANALYSIS-ONLY (invariant I1). These LLM-on-gold labels exist ONLY to measure
annotator agreement between the LLM labeling pipeline and the clinical gold. They
MUST NEVER enter a training pool or any file a training kernel reads. Output lives
under data/finetuning-message/interim/kappa-gold-overlap/ (gitignored) only.

Reuses the exact labeling prompt + provider path from r2_llm_label.py, so the
kappa describes the same pipeline that produced the 9,680-example training pool
(azure / gpt-5.4-mini, per docs/spec/capabilities/data-and-labeling.md).

The gold overlap set = every row with Source == "cssrs500" in the combined CSV
(the held-out clinical gold, 392 sequences, class counts [99, 171, 77, 45]).

Usage:
    .venv-voice/bin/python scripts/r2_kappa_gold_overlap.py --limit 3   # smoke test
    .venv-voice/bin/python scripts/r2_kappa_gold_overlap.py             # full 392 (resumable)
    .venv-voice/bin/python scripts/r2_kappa_gold_overlap.py --report    # compute kappa from jsonl
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from r2_llm_label import CALLERS, DEFAULT_MODEL, KEY_VAR, PROMPT, load_dotenv, parse

SRC = Path("data/finetuning-message/external/r2-combined/sequences.csv")
OUT_DIR = Path("data/finetuning-message/interim/kappa-gold-overlap")
OUT = OUT_DIR / "llm_labels.jsonl"
LABEL_MAP = {"Indicator": 0, "Ideation": 1, "Behavior": 2, "Attempt": 3}
LABEL_NAMES = ["Indicator", "Ideation", "Behavior", "Attempt"]
CONF_MIN = 0.6  # the training pool's retention rule


def load_gold() -> list[dict]:
    """Every Source==cssrs500 row: {user_id, gold_label, posts:list[str]}."""
    rows: list[dict] = []
    with SRC.open() as f:
        for row in csv.DictReader(f):
            if row["Source"] != "cssrs500":
                continue
            posts = ast.literal_eval(row["Post"])  # Post column = repr(list[str])
            rows.append({"user_id": row["User"],
                         "gold_label": LABEL_MAP[row["Label"]],
                         "posts": [str(p) for p in posts]})
    return rows


def build_prompt(posts: list[str]) -> str:
    """Mirror r2_llm_label.build_prompt: join posts with the same separator + 8k truncation."""
    joined = "\n---\n".join(posts)
    return PROMPT.format(posts=joined[:8000])


def label_gold(limit: int, workers: int) -> None:
    load_dotenv()
    provider = os.environ.get("LLM_PROVIDER", "anthropic").lower()
    if provider not in CALLERS:
        raise SystemExit(f"LLM_PROVIDER must be one of {list(CALLERS)}")
    model = os.environ.get("LLM_MODEL", DEFAULT_MODEL[provider])
    key = os.environ.get(KEY_VAR[provider], "")
    if not key:
        raise SystemExit(f"{KEY_VAR[provider]} not set (put it in .env)")
    call = CALLERS[provider]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gold = load_gold()
    done = set()
    if OUT.exists():
        done = {json.loads(l)["user_id"] for l in OUT.read_text().splitlines() if l.strip()}
    todo = [g for g in gold if g["user_id"] not in done]
    if limit:
        todo = todo[:limit]
    print(f">>> provider={provider} model={model} | {len(gold)} gold seqs, {len(done)} done, "
          f"labeling {len(todo)}", flush=True)

    lock = threading.Lock()
    counts = {"ok": 0, "err": 0}
    f = OUT.open("a")

    def work(g: dict) -> None:
        try:
            raw = call(build_prompt(g["posts"]), model, key)
        except Exception as e:                       # api / content-filter / network
            with lock:
                counts["err"] += 1
                print(f"  ERR {g['user_id']}: {str(e)[:120]}", flush=True)
            return
        parsed = parse(raw)
        with lock:
            if not parsed:
                counts["err"] += 1
            else:
                rec = {"user_id": g["user_id"], "gold_label": g["gold_label"],
                       "llm_label": parsed["label"], "llm_confidence": parsed["confidence"],
                       "raw_response": raw[:500]}
                f.write(json.dumps(rec) + "\n")
                f.flush()
                counts["ok"] += 1
            n = sum(counts.values())
            if n % 25 == 0:
                print(f"  [{n}/{len(todo)}] ok={counts['ok']} err={counts['err']}", flush=True)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(as_completed(ex.submit(work, g) for g in todo))
    f.close()
    print(f">>> done: labeled {counts['ok']}, errors {counts['err']} → {OUT}", flush=True)


def _bootstrap_ci(gold, llm, weights, n_boot=1000, seed=0):
    import numpy as np
    from sklearn.metrics import cohen_kappa_score
    rng = np.random.default_rng(seed)
    g, l = np.asarray(gold), np.asarray(llm)
    n = len(g)
    stats = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        gb, lb = g[idx], l[idx]
        if len(set(gb.tolist()) | set(lb.tolist())) < 2:
            continue
        stats.append(cohen_kappa_score(gb, lb, weights=weights,
                                       labels=[0, 1, 2, 3]))
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return float(lo), float(hi)


def compute_report() -> None:
    import numpy as np
    from sklearn.metrics import cohen_kappa_score, confusion_matrix, f1_score

    recs = [json.loads(l) for l in OUT.read_text().splitlines() if l.strip()]
    # keep only rows where the LLM gave a valid ordinal label (drop -1 off-topic)
    valid = [r for r in recs if r["llm_label"] in (0, 1, 2, 3)]
    offtopic = [r for r in recs if r["llm_label"] == -1]
    gold = [r["gold_label"] for r in valid]
    llm = [r["llm_label"] for r in valid]

    def kappas(g, l):
        return {
            "quadratic": float(cohen_kappa_score(g, l, weights="quadratic", labels=[0, 1, 2, 3])),
            "linear": float(cohen_kappa_score(g, l, weights="linear", labels=[0, 1, 2, 3])),
            "unweighted": float(cohen_kappa_score(g, l, labels=[0, 1, 2, 3])),
        }

    k_all = kappas(gold, llm)
    qlo, qhi = _bootstrap_ci(gold, llm, "quadratic")
    cm = confusion_matrix(gold, llm, labels=[0, 1, 2, 3])
    cm_norm = cm / cm.sum(axis=1, keepdims=True).clip(min=1)
    # per-class agreement = fraction of gold-class-c examples the LLM also put in c
    per_class = {LABEL_NAMES[c]: float(cm_norm[c, c]) for c in range(4)}

    # confidence->=0.6 subset (the labels that would have been retained by the pool)
    hi = [r for r in valid if r["llm_confidence"] >= CONF_MIN]
    gold_hi = [r["gold_label"] for r in hi]
    llm_hi = [r["llm_label"] for r in hi]
    k_hi = kappas(gold_hi, llm_hi) if len(set(gold_hi)) > 1 else None
    cm_hi = confusion_matrix(gold_hi, llm_hi, labels=[0, 1, 2, 3])

    numbers = {
        "n_total_recs": len(recs),
        "n_valid": len(valid),
        "n_offtopic": len(offtopic),
        "kappa_all": k_all,
        "kappa_quadratic_ci95": [qlo, qhi],
        "confusion_counts": cm.tolist(),
        "confusion_rownorm": cm_norm.round(4).tolist(),
        "per_class_agreement": per_class,
        "n_conf_ge_0.6": len(hi),
        "kappa_conf_ge_0.6": k_hi,
        "confusion_counts_conf_ge_0.6": cm_hi.tolist(),
        "gold_class_counts": np.bincount(gold, minlength=4).tolist(),
        "llm_class_counts": np.bincount(llm, minlength=4).tolist(),
    }
    (OUT_DIR / "kappa_numbers.json").write_text(json.dumps(numbers, indent=2))

    # human-readable report
    def cm_md(mat):
        head = "| gold\\LLM | " + " | ".join(LABEL_NAMES) + " |\n"
        head += "|---|" + "|".join([":--:"] * 4) + "|\n"
        for c in range(4):
            head += f"| {LABEL_NAMES[c]} | " + " | ".join(str(int(x)) for x in mat[c]) + " |\n"
        return head

    khq = f"{k_hi['quadratic']:.3f}" if k_hi else "n/a"
    khl = f"{k_hi['linear']:.3f}" if k_hi else "n/a"
    khu = f"{k_hi['unweighted']:.3f}" if k_hi else "n/a"
    md = f"""# Cohen's κ(LLM, gold) — 392 gold CSSRS-500 overlap set

**Analysis-only (I1).** LLM labels produced here measure LLM↔gold agreement; they
never enter any training pool. Same pipeline as the 9,680 training pool
(azure / gpt-5.4-mini). Overlap set = all Source==cssrs500 rows.

- n scored (valid ordinal LLM label): **{len(valid)}** / {len(recs)} labeled
  ({len(offtopic)} returned off-topic/−1, excluded from κ).
- Gold class counts (scored): {np.bincount(gold, minlength=4).tolist()} {LABEL_NAMES}
- LLM class counts (scored):  {np.bincount(llm, minlength=4).tolist()} {LABEL_NAMES}

## κ (full valid set, n={len(valid)})

| weighting | κ |
|---|:--:|
| **quadratic (primary)** | **{k_all['quadratic']:.3f}** (95% CI [{qlo:.3f}, {qhi:.3f}]) |
| linear | {k_all['linear']:.3f} |
| unweighted | {k_all['unweighted']:.3f} |

## Confusion matrix — raw counts (rows = gold, cols = LLM)

{cm_md(cm)}

## Confusion matrix — row-normalized

{cm_md((cm_norm * 100).round(1))}
(values are % of each gold row)

## Per-class agreement (diagonal of row-normalized)

""" + "\n".join(f"- {k}: {v:.3f}" for k, v in per_class.items()) + f"""

## Confidence ≥ 0.6 subset (the pool's retention rule) — n={len(hi)}

This is the κ that describes the labels actually kept by the training pool.

| weighting | κ |
|---|:--:|
| quadratic | {khq} |
| linear | {khl} |
| unweighted | {khu} |

Confusion (conf≥0.6):

{cm_md(cm_hi)}

_Numbers: `kappa_numbers.json` (same directory). Script: `scripts/r2_kappa_gold_overlap.py`._
"""
    (OUT_DIR / "kappa_report.md").write_text(md)
    print(f">>> quadratic κ = {k_all['quadratic']:.3f} [{qlo:.3f}, {qhi:.3f}] | "
          f"linear {k_all['linear']:.3f} | unweighted {k_all['unweighted']:.3f}")
    print(f">>> per-class agreement: {per_class}")
    print(f">>> report → {OUT_DIR/'kappa_report.md'}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="0 = all 392")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--report", action="store_true", help="compute κ from existing jsonl")
    args = ap.parse_args()
    if args.report:
        compute_report()
    else:
        label_gold(args.limit, args.workers)


if __name__ == "__main__":
    main()
