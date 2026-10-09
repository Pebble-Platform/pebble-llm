"""Human-human emotion agreement from a BLIND gold-review pass (change 014).

Reads gold-reviews/<rater>.json written by the blind `gold.html` flow: the rater picks
the emotion from audio (+ transcript) BEFORE the owner's label is revealed, so
`original.emotion` vs `answer.emotion` is an independent pair -> Cohen's kappa.

Only EMOTION is blind. Valence/arousal are revealed right after the rater commits
the emotion and then only edited, so they are anchored -> no kappa for V/A here.

Reviews stamped before the blind code landed are excluded (CUTOFF); they are
counted in a sensitivity line instead. `--anchored` adds the same clips from an
anchored (pre-014) review file for comparison -- a different person AND a different
protocol, so the gap is not a clean estimate of the anchoring effect.

    .venv-vnser/Scripts/python.exe scripts/vietnamese-ser/gold_review_kappa.py \
        --blind data/vietnamese-ser/episodes/gold-reviews/nhinguyen.json \
        --anchored data/vietnamese-ser/episodes/gold-reviews/vyphan.json \
        --out docs/reports/014/kappa.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from iaa_report import EMOTIONS, krippendorff_alpha

# last write of tools/labeler/gold.js for change 014 (2026-09-11 14:53:41 +07)
CUTOFF = "2026-09-11T07:53:41+00:00"


def cohen_kappa(a: np.ndarray, b: np.ndarray, cats: list[str]) -> float:
    po = float((a == b).mean())
    pe = sum(float((a == c).mean()) * float((b == c).mean()) for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def kappa_ci(a: np.ndarray, b: np.ndarray, cats: list[str], n=1000, seed=0):
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n):
        i = rng.integers(0, len(a), len(a))
        v = cohen_kappa(a[i], b[i], cats)
        if v == v:
            vals.append(v)
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return float(lo), float(hi)


def pair_rows(name: str, a: np.ndarray, b: np.ndarray) -> str:
    k = cohen_kappa(a, b, EMOTIONS)
    lo, hi = kappa_ci(a, b, EMOTIONS)
    alpha = krippendorff_alpha([[x, y] for x, y in zip(a, b)], EMOTIONS)
    return f"| {name} | {len(a)} | {(a == b).mean():.1%} | **{k:.3f}** | [{lo:.3f}, {hi:.3f}] | {alpha:.3f} |"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--blind", required=True, help="gold-reviews/<rater>.json from the 014 flow")
    ap.add_argument("--anchored", help="pre-014 gold-reviews/<rater>.json, same clips compared")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    rater = Path(a.blind).stem
    blind = json.loads(Path(a.blind).read_text(encoding="utf-8"))
    usable = {k: v for k, v in blind.items() if not v["rejected"] and v["answer"].get("emotion")}
    main_set = {k: v for k, v in usable.items() if v["ts"] >= CUTOFF}
    keys = sorted(main_set)
    own = np.array([main_set[k]["original"]["emotion"] for k in keys])
    blz = np.array([main_set[k]["answer"]["emotion"] for k in keys])

    L = [
        f"# κ người–người (emotion) — vòng soát mù change 014 · `{rater}`",
        "",
        "> Sinh bởi `scripts/vietnamese-ser/gold_review_kappa.py`. Chỉ **emotion** là mù",
        "> (người soát chốt trước khi thấy nhãn owner). V/A lộ ra ngay sau khi chốt rồi chỉ",
        "> được sửa ⇒ **bị neo, không có κ V/A**. Người soát **thấy transcript** (khác `rate.html`).",
        "",
        f"- Lượt soát: {len(blind)} · loại (rejected): {len(blind) - len(usable)} · "
        f"trước khi code mù land ({CUTOFF}): {len(usable) - len(main_set)} ⇒ **n = {len(keys)}**",
        "- Mẫu: phần đầu của hàng đợi đã xáo trộn `review-candidates.tsv` (change 011).",
        "",
        "## 1. Headline",
        "",
        "| cặp | n | trùng thô | Cohen κ | 95% CI (bootstrap) | α nominal |",
        "|---|--:|--:|--:|---|--:|",
        pair_rows(f"owner ↔ {rater} (mù)", own, blz),
    ]
    if len(usable) != len(main_set):
        ks = sorted(usable)
        L.append(
            pair_rows(
                "↳ độ nhạy: gồm cả lượt trước cutoff",
                np.array([usable[k]["original"]["emotion"] for k in ks]),
                np.array([usable[k]["answer"]["emotion"] for k in ks]),
            )
        )

    if a.anchored:
        anc_name = Path(a.anchored).stem
        anc = json.loads(Path(a.anchored).read_text(encoding="utf-8"))
        shared = [k for k in keys if k in anc and not anc[k]["rejected"]]
        m = [keys.index(k) for k in shared]
        anz = np.array([anc[k]["answer"]["emotion"] for k in shared])
        L += [
            "",
            "## 2. So với vòng có neo (cùng clip)",
            "",
            f"> `{anc_name}` soát theo giao thức cũ (thấy nhãn owner trước). **Khác người VÀ",
            "> khác giao thức** ⇒ chênh lệch dưới đây *gợi ý* độ lớn của neo, không đo sạch nó.",
            "",
            "| cặp | n | trùng thô | Cohen κ | 95% CI (bootstrap) | α nominal |",
            "|---|--:|--:|--:|---|--:|",
            pair_rows(f"owner ↔ {anc_name} (có neo)", own[m], anz),
            pair_rows(f"{anc_name} (có neo) ↔ {rater} (mù)", anz, blz[m]),
        ]

    L += [
        "",
        "## 3. κ theo từng lớp (one-vs-rest, owner ↔ mù)",
        "",
        "| lớp | owner n | mù n | κ |",
        "|---|--:|--:|--:|",
    ]
    for c in EMOTIONS:
        L.append(
            f"| {c} | {int((own == c).sum())} | {int((blz == c).sum())} | "
            f"{cohen_kappa(own == c, blz == c, [True, False]):.3f} |"
        )

    L += [
        "",
        "## 4. Ma trận nhầm (hàng = owner, cột = mù)",
        "",
        "| owner \\ mù | " + " | ".join(EMOTIONS) + " |",
        "|---|" + "--:|" * len(EMOTIONS),
    ]
    for r in EMOTIONS:
        L.append(
            f"| {r} | "
            + " | ".join(str(int(((own == r) & (blz == c)).sum())) for c in EMOTIONS)
            + " |"
        )

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
