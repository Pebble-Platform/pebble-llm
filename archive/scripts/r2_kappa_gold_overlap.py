"""T1.1 — Cohen's κ(LLM, gold) + confusion on the 392-sequence gold overlap set.

Recovers the gold eval set (all cssrs500-source sequences — verified [99,171,77,45]=392)
from the public Zenodo CSSRS-500 record, re-labels it with the SAME LLM pipeline that
produced the training pool (scripts/r2_llm_label.py — identical PROMPT + provider path),
then reports quadratic-weighted Cohen's κ + a 4x4 confusion matrix against the gold labels.

I1 (gold-holdout): these LLM-on-gold labels are ANALYSIS-ONLY — they measure annotator
agreement. They live under data/**/interim/ and must NEVER enter a training pool or any
file a training kernel reads.

Steps (each resumable; run all by default):
    recover : Zenodo CSSRS-500 -> 392 gold sequences (User, posts, gold_label)
    label   : LLM-label the 392 with the training-pool provider/model (needs .env credentials)
    report  : quadratic/linear/unweighted κ + confusion + conf>=0.6 subset + bootstrap CI

Usage:
    .venv-voice/Scripts/python.exe scripts/r2_kappa_gold_overlap.py                 # all steps
    .venv-voice/Scripts/python.exe scripts/r2_kappa_gold_overlap.py --steps recover
    .venv-voice/Scripts/python.exe scripts/r2_kappa_gold_overlap.py --steps label --workers 8
    .venv-voice/Scripts/python.exe scripts/r2_kappa_gold_overlap.py --steps report

Env (from .env, same as r2_llm_label.py): LLM_PROVIDER, LLM_MODEL, <PROVIDER>_API_KEY
(+ AZURE_OPENAI_ENDPOINT for azure). The training pool used gpt-5.4-mini.
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import os
import re
import threading
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Reuse the EXACT labeling pipeline + gold-parsing logic (surgical: no duplication).
from r2_llm_label import CALLERS, DEFAULT_MODEL, KEY_VAR, PROMPT, load_dotenv, parse  # noqa: E402

ZENODO_URL = ("https://zenodo.org/api/records/2667859/files/"
              "500_Reddit_users_posts_labels.csv/content")
CSSRS_CSV = Path("data/finetuning-message/external/cssrs/500_Reddit_users_posts_labels.csv")
OUTDIR = Path("data/finetuning-message/interim/kappa-gold-overlap")
GOLD = OUTDIR / "gold_overlap.jsonl"
LABELS = OUTDIR / "llm_labels.jsonl"
REPORT = OUTDIR / "kappa_report.md"
NUMBERS = OUTDIR / "kappa.json"

LABEL_NAMES = ["Indicator", "Ideation", "Behavior", "Attempt"]
LABEL_MAP = {n: i for i, n in enumerate(LABEL_NAMES)}
_WS = re.compile(r"\s+")


def _norm(text: str) -> str:
    return _WS.sub(" ", text).strip()


def _parse_posts(cell: str) -> list[str]:
    try:
        v = ast.literal_eval(cell)
        if isinstance(v, list) and v:
            return [str(x) for x in v if str(x).strip()]
    except Exception:
        pass
    s = cell.strip("[]").strip()
    return [s] if s else []


def recover() -> None:
    """Zenodo CSSRS-500 -> the 392 cssrs500-source gold sequences.

    Reproduces r2_build_dataset.from_cssrs500 + _norm + within-source dedup, i.e. exactly
    the rows tagged Source=cssrs500 in the combined CSV that the kernels evaluate on.
    """
    OUTDIR.mkdir(parents=True, exist_ok=True)
    CSSRS_CSV.parent.mkdir(parents=True, exist_ok=True)
    if not CSSRS_CSV.exists():
        print(">>> downloading CSSRS-500 from Zenodo ...", flush=True)
        urllib.request.urlretrieve(ZENODO_URL, CSSRS_CSV)

    rows: list[tuple[list[str], int]] = []
    with CSSRS_CSV.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            lab = r["Label"].strip()
            if lab not in LABEL_MAP:            # drop "Supportive" -> 4-level
                continue
            posts = _parse_posts(r["Post"])[-5:]
            if posts:
                rows.append((posts, LABEL_MAP[lab]))

    seen: set[str] = set()
    kept = []
    for i, (posts, lab) in enumerate(rows):
        posts = [_norm(p) for p in posts if _norm(p)]
        if not posts:
            continue
        key = "\n".join(posts)
        if key in seen:
            continue
        seen.add(key)
        kept.append({"user_id": f"cssrs500-{i}", "gold_label": lab, "posts": posts})

    with GOLD.open("w", encoding="utf-8") as f:
        for k in kept:
            f.write(json.dumps(k, ensure_ascii=False) + "\n")
    dist = Counter(k["gold_label"] for k in kept)
    bc = [dist.get(i, 0) for i in range(4)]
    print(f">>> recovered {len(kept)} gold sequences -> {GOLD}", flush=True)
    print(f"    class dist [Ind,Ide,Beh,Att] = {bc}", flush=True)
    if bc != [99, 171, 77, 45]:
        raise SystemExit(f"STOP: expected [99,171,77,45], got {bc} — gold set changed, do NOT proceed.")


def label(workers: int) -> None:
    """LLM-label the 392 gold sequences with the training-pool provider/model. Resumable."""
    load_dotenv()
    provider = os.environ.get("LLM_PROVIDER", "anthropic").lower()
    if provider not in CALLERS:
        raise SystemExit(f"LLM_PROVIDER must be one of {list(CALLERS)}")
    model = os.environ.get("LLM_MODEL", DEFAULT_MODEL[provider])
    key = os.environ.get(KEY_VAR[provider], "")
    if not key:
        raise SystemExit(f"{KEY_VAR[provider]} not set (put it in .env)")
    call = CALLERS[provider]

    seqs = [json.loads(x) for x in GOLD.read_text(encoding="utf-8").splitlines() if x.strip()]
    done = set()
    if LABELS.exists():
        done = {json.loads(x)["user_id"] for x in LABELS.read_text(encoding="utf-8").splitlines() if x.strip()}
    todo = [s for s in seqs if s["user_id"] not in done]
    print(f">>> provider={provider} model={model} | {len(seqs)} gold, {len(done)} done, "
          f"labeling {len(todo)}", flush=True)

    lock = threading.Lock()
    counts = {"ok": 0, "err": 0}
    f = LABELS.open("a", encoding="utf-8")

    def work(seq: dict) -> None:
        prompt = PROMPT.format(posts="\n---\n".join(seq["posts"])[:8000])
        try:
            raw = call(prompt, model, key)
        except Exception as e:
            with lock:
                counts["err"] += 1
                print(f"  ERR {seq['user_id']}: {e}", flush=True)
            return
        parsed = parse(raw)
        with lock:
            rec = {"user_id": seq["user_id"], "gold_label": seq["gold_label"],
                   "llm_label": parsed["label"] if parsed else None,
                   "llm_confidence": parsed["confidence"] if parsed else None,
                   "raw_response": raw[:500]}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            counts["ok" if parsed else "err"] += 1
            n = counts["ok"] + counts["err"]
            if n % 50 == 0:
                print(f"  [{n}/{len(todo)}] ok={counts['ok']} err={counts['err']}", flush=True)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(as_completed(ex.submit(work, s) for s in todo))
    f.close()
    print(f">>> labeled ok={counts['ok']} err={counts['err']} -> {LABELS}", flush=True)


def _kappa(y1, y2, weights, k=4):
    """Cohen's κ with optional linear/quadratic weighting (no sklearn dependency at import)."""
    from sklearn.metrics import cohen_kappa_score
    return float(cohen_kappa_score(y1, y2, labels=list(range(k)), weights=weights))


def report() -> None:
    import numpy as np

    recs = [json.loads(x) for x in LABELS.read_text(encoding="utf-8").splitlines() if x.strip()]
    n_total = len(recs)
    n_offtopic = sum(1 for r in recs if r["llm_label"] == -1)
    n_parsefail = sum(1 for r in recs if r["llm_label"] is None)
    # κ is defined over the 4 ordinal levels: drop off-topic(-1) and parse failures.
    ok = [r for r in recs if r["llm_label"] in (0, 1, 2, 3)]
    gold = np.array([r["gold_label"] for r in ok])
    llm = np.array([r["llm_label"] for r in ok])

    def kappas(g, m):
        return {"quadratic": _kappa(g, m, "quadratic"),
                "linear": _kappa(g, m, "linear"),
                "unweighted": _kappa(g, m, None)}

    full = kappas(gold, llm)

    # confidence>=0.6 subset — the retention rule that actually describes the training labels.
    conf = np.array([r["llm_confidence"] or 0.0 for r in ok])
    hi = conf >= 0.6
    sub = kappas(gold[hi], llm[hi]) if hi.sum() > 1 else {k: float("nan") for k in full}

    # bootstrap CI on quadratic κ over the full overlap (1000 resamples, seeded).
    rng = np.random.default_rng(42)
    boots = []
    idx = np.arange(len(gold))
    for _ in range(1000):
        s = rng.choice(idx, size=len(idx), replace=True)
        if len(set(gold[s].tolist())) > 1 and len(set(llm[s].tolist())) > 1:
            boots.append(_kappa(gold[s], llm[s], "quadratic"))
    lo, hiq = (float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))) if boots else (float("nan"),) * 2

    # 4x4 confusion (rows=gold, cols=llm), raw + row-normalized.
    cm = np.zeros((4, 4), dtype=int)
    for g, m in zip(gold, llm):
        cm[g, m] += 1
    row_sums = cm.sum(1, keepdims=True)
    cmn = np.divide(cm, row_sums, out=np.zeros_like(cm, float), where=row_sums != 0)

    # per-class agreement (diagonal recall).
    per_class = {LABEL_NAMES[i]: (float(cmn[i, i]) if row_sums[i] else float("nan")) for i in range(4)}

    numbers = {
        "n_overlap": n_total, "n_offtopic": n_offtopic, "n_parsefail": n_parsefail,
        "n_kappa": int(len(gold)), "n_conf_ge_0.6": int(hi.sum()),
        "kappa_full": full, "kappa_conf_ge_0.6": sub,
        "quadratic_ci95": [lo, hiq], "per_class_recall": per_class,
        "confusion_raw": cm.tolist(), "confusion_rownorm": cmn.round(4).tolist(),
        "provider_model": {"note": "same pipeline as training pool; see .env at run time"},
    }
    NUMBERS.write_text(json.dumps(numbers, indent=2), encoding="utf-8")

    def mtx(m, fmt):
        head = "| gold\\llm | " + " | ".join(LABEL_NAMES) + " |\n"
        head += "|" + "---|" * 5 + "\n"
        for i in range(4):
            head += f"| **{LABEL_NAMES[i]}** | " + " | ".join(fmt(m[i][j]) for j in range(4)) + " |\n"
        return head

    md = f"""# κ(LLM, gold) — gold overlap set (T1.1)

**Analysis-only (I1):** LLM labels on gold measure agreement; never used for training.

- Overlap n = {n_total} (off-topic/-1: {n_offtopic}; parse-fail: {n_parsefail}); κ computed on n = {len(gold)}.
- Confidence ≥ 0.6 subset: n = {int(hi.sum())}.

## Cohen's κ (gold vs LLM)

| weighting | full overlap | conf ≥ 0.6 |
|---|---|---|
| **quadratic** (primary) | {full['quadratic']:.4f} | {sub['quadratic']:.4f} |
| linear | {full['linear']:.4f} | {sub['linear']:.4f} |
| unweighted | {full['unweighted']:.4f} | {sub['unweighted']:.4f} |

Quadratic κ 95% CI (1000-resample bootstrap over examples): [{lo:.4f}, {hiq:.4f}].

## Confusion matrix (rows = gold, cols = LLM)

Raw counts:

{mtx(cm.tolist(), lambda v: str(int(v)))}
Row-normalized:

{mtx(cmn.tolist(), lambda v: f"{v:.3f}")}
## Per-class agreement (diagonal recall)

{chr(10).join(f"- {k}: {v:.3f}" for k, v in per_class.items())}

Numbers JSON: `{NUMBERS}`.
"""
    REPORT.write_text(md, encoding="utf-8")
    print(f">>> quadratic κ = {full['quadratic']:.4f}  (CI [{lo:.4f}, {hiq:.4f}], n={len(gold)})", flush=True)
    print(f">>> report -> {REPORT}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", nargs="+", default=["recover", "label", "report"],
                    choices=["recover", "label", "report"])
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    if "recover" in args.steps:
        recover()
    if "label" in args.steps:
        label(args.workers)
    if "report" in args.steps:
        report()


if __name__ == "__main__":
    main()
