"""Build each annotator's fixed, shuffled rating queue (change 011, M3).

Implements the pre-registered sampling of
`docs/spec/changes/011-online-multi-annotator/qc-protocol.md`:

* a **stratified** reliability subset — balanced across the 7 emotion classes and
  both series, drawn from the owner's labeled, non-rejected clips;
* the **same** subset for every annotator (full overlap — κ needs all raters on the
  same items);
* **gold** anchors (§2.1) seeded through the queue for the QC gate;
* ~10% **duplicates** (§2.2) re-presented ≥50 slots later for self-consistency;
* order **shuffled per annotator** (different seed each), so no two annotators share
  an order and nobody can reassemble a scene (ADR-005 safeguard #4).

Gold and duplicate second-presentations are marked in `kind` so the κ report can
exclude them (qc-protocol §5.1).

Run with the labeler server STOPPED (ADR-004: no 1-writer lock yet):

    .venv-vnser/Scripts/python.exe scripts/vietnamese-ser/build_assignments.py \
        --root data/vietnamese-ser/episodes --annotators ann01,ann02 --n 250
"""

from __future__ import annotations

import argparse
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "labeler"))
import store

EMOTIONS = ["joy", "sadness", "anger", "fear_anxiety", "surprise", "disgust", "neutral"]
DUP_FRACTION = 0.10
DUP_MIN_GAP = 50  # slots between a duplicate's two presentations (qc-protocol §2.2)

# qualification round (qc-protocol §3.1): 30 slots = 18 gold + 10 filler + 2 trap
QUAL_GOLD, QUAL_FILL, QUAL_TRAP = 18, 10, 2

# The qualification round consumes the FIRST QUAL_GOLD anchors; the main round uses the
# REST. The two sets must stay disjoint — reusing a qualification anchor in the main
# round would score recall of a clip the annotator already met, not whether they are
# still listening.
TRAP_REASONS = {"noise", "bad_cut"}  # owner-rejected -> "skip" is the only right answer


def eligible(state: dict) -> list[dict]:
    """Owner-labeled, not rejected — the pool the reliability subset is drawn from."""
    return [r for r in state.values() if r.get("emotion") and not r.get("rejected")]


def traps(state: dict) -> list[dict]:
    """Clips the owner rejected as noise/bad-cut: rating an emotion here means guessing."""
    return [
        r for r in state.values() if r.get("rejected") and r.get("reject_reason") in TRAP_REASONS
    ]


def build_qualification(
    pool: list[dict], gold: list[dict], trap_pool: list[dict], rng: random.Random
) -> list[tuple[str, str, str]]:
    """The 30-slot pretest (qc-protocol §3.1) — scored, and it gates entry to the round."""
    fillers = stratify([r for r in pool if r not in gold], QUAL_FILL, rng)
    items = [(r["epKey"], r["id"], "gold") for r in gold[:QUAL_GOLD]]
    items += [(r["epKey"], r["id"], "normal") for r in fillers]
    items += [
        (r["epKey"], r["id"], "trap") for r in rng.sample(trap_pool, min(QUAL_TRAP, len(trap_pool)))
    ]
    rng.shuffle(items)
    return items


def stratify(pool: list[dict], n: int, rng: random.Random) -> list[dict]:
    """Draw ~n clips balanced over (emotion x series), taking what thin cells allow.

    Round-robin over cells rather than a fixed quota: rare cells (e.g. `surprise` is
    the thinnest class in the corpus) contribute everything they have instead of
    capping the whole draw at the smallest cell.
    """
    cells: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in pool:
        cells[(r["emotion"], r.get("series", ""))].append(r)
    for v in cells.values():
        rng.shuffle(v)
    keys = sorted(cells)
    picked: list[dict] = []
    while len(picked) < n and any(cells[k] for k in keys):
        for k in keys:
            if cells[k] and len(picked) < n:
                picked.append(cells[k].pop())
    return picked


def build_queue(
    subset: list[dict], gold: list[dict], rng: random.Random
) -> list[tuple[str, str, str]]:
    """One annotator's queue: shuffled subset + gold + duplicates, as (epkey, id, kind).

    `gold` here is already the post-qualification slice (see QUAL_GOLD) — disjoint from
    what the annotator saw in the pretest.
    """
    items = [(r["epKey"], r["id"], "normal") for r in subset]
    items += [(r["epKey"], r["id"], "gold") for r in gold]
    rng.shuffle(items)

    n_dup = max(1, int(len(subset) * DUP_FRACTION)) if subset else 0
    for src in rng.sample([i for i in items if i[2] == "normal"], min(n_dup, len(subset))):
        first = items.index(src)
        lo = min(first + DUP_MIN_GAP, len(items))
        items.insert(rng.randint(lo, len(items)), (src[0], src[1], "dup"))
    return items


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="build per-annotator rating queues")
    ap.add_argument("--root", default="data/vietnamese-ser/episodes")
    ap.add_argument("--annotators", required=True, help="comma-separated ids, e.g. ann01,ann02")
    ap.add_argument("--n", type=int, default=250, help="reliability subset size")
    ap.add_argument("--gold", default=None, help="gold-set.txt (one 'epKey/clip_id' per line)")
    ap.add_argument("--seed", type=int, default=1128)
    ap.add_argument(
        "--qualify",
        action="store_true",
        help="build the 30-slot qualification pretest instead of the main round",
    )
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    store.set_root(root)
    store.load()

    gold_keys: set[tuple[str, str]] = set()
    if a.gold and Path(a.gold).is_file():
        for line in Path(a.gold).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                ep, _, cid = line.rpartition("/")
                gold_keys.add((ep, cid))
    else:
        print("WARNING: no gold set — QC gate (qc-protocol §3) cannot be scored", file=sys.stderr)

    pool = eligible(store.STATE)
    gold = sorted(
        (r for r in pool if (r["epKey"], r["id"]) in gold_keys), key=lambda r: (r["epKey"], r["id"])
    )
    rest = [r for r in pool if (r["epKey"], r["id"]) not in gold_keys]

    # disjoint split: pretest takes the first QUAL_GOLD, the main round takes the rest
    qual_gold, round_gold = gold[:QUAL_GOLD], gold[QUAL_GOLD:]
    if a.qualify and len(qual_gold) < QUAL_GOLD:
        print(
            f"WARNING: only {len(qual_gold)}/{QUAL_GOLD} gold anchors for the pretest "
            f"— Q1 threshold (>= 9/18) assumes 18",
            file=sys.stderr,
        )
    if not a.qualify and len(round_gold) < 15:
        print(
            f"WARNING: only {len(round_gold)} gold anchors left for the main round after the "
            f"pretest took {len(qual_gold)} — R1 will rest on very few items. "
            f"Confirm more gold (pick_gold_candidates.py --per-class 9).",
            file=sys.stderr,
        )

    # the SAME subset for everyone — full overlap is what makes Fleiss' kappa valid
    subset = stratify(rest, a.n, random.Random(a.seed))
    if a.qualify:
        print(f"pool={len(pool)}  QUALIFICATION pretest  gold={len(qual_gold)}/{len(gold)}")
    else:
        print(f"pool={len(pool)}  subset={len(subset)}  gold={len(round_gold)}/{len(gold)}")
        dist: dict[str, int] = defaultdict(int)
        for r in subset:
            dist[r["emotion"]] += 1
        print("  per class: " + "  ".join(f"{e}={dist[e]}" for e in EMOTIONS))

    trap_pool = traps(store.STATE)
    for i, ann in enumerate(x.strip() for x in a.annotators.split(",") if x.strip()):
        rng = random.Random(a.seed + 1000 + i)
        queue = (
            build_qualification(rest, qual_gold, trap_pool, rng)
            if a.qualify
            else build_queue(subset, round_gold, rng)
        )
        kinds: dict[str, int] = defaultdict(int)
        for _, _, k in queue:
            kinds[k] += 1
        print(f"{ann}: {len(queue)} slots ({dict(kinds)})")
        if not a.dry_run:
            store.assign(ann, queue)

    if a.dry_run:
        print("\n(dry run — nothing written)")


if __name__ == "__main__":
    main()
