"""Build deterministic GroupKFold splits over the ViEmoSpeech weak pool.

Change 004-vnser-training. The split unit is (ep, speaker): pyannote speaker
labels are episode-local (`SPEAKER_NN` is reused across episodes), so the group
key must include the episode. With a single series the cast still recurs across
episodes under different labels, so this is *best-effort* I4, not true
speaker-disjoint eval — the training report must carry that caveat (see the
change's proposal.md R2).

No sklearn dependency (this repo's env is numpy+pandas only): GroupKFold is
implemented as a deterministic greedy assignment — groups sorted by descending
clip count (ties broken by group key) are each placed in the currently-lightest
fold. Deterministic ⇒ no seed needed; `split_hash` lets a caller assert stability.

Usage (from repo root):
  python scripts/vietnamese-ser/make_splits.py \
      --manifest data/vietnamese-ser/.../manifest.csv --out .../splits.csv
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pandas as pd

GROUP_COLS = ("ep", "speaker")


def load_manifest(path: str | Path) -> pd.DataFrame:
    """Read manifest.csv and keep only single-speaker-clean rows (I3)."""
    df = pd.read_csv(path)
    is_clean = df["is_clean"].astype(str).str.lower().isin({"true", "1"})
    return df[is_clean].reset_index(drop=True)


def assign_folds(
    df: pd.DataFrame, n_splits: int = 5, group_cols: tuple[str, ...] = GROUP_COLS
) -> pd.DataFrame:
    """Return a copy of the clean rows with an added integer `fold` column.

    Every (ep, speaker) group is placed wholly in one fold (group-disjoint).
    """
    is_clean = df["is_clean"].astype(str).str.lower().isin({"true", "1"})
    out = df[is_clean].copy().reset_index(drop=True)

    sizes = out.groupby(list(group_cols)).size()
    # heaviest first; group key as deterministic tiebreak
    order = sorted(sizes.index, key=lambda g: (-int(sizes[g]), g))

    fold_load = [0] * n_splits
    group_fold: dict[tuple, int] = {}
    for g in order:
        f = min(range(n_splits), key=lambda i: (fold_load[i], i))
        group_fold[g] = f
        fold_load[f] += int(sizes[g])

    keys = list(zip(*(out[c] for c in group_cols)))
    out["fold"] = [group_fold[k] for k in keys]
    return out


def split_hash(df: pd.DataFrame) -> str:
    """Stable hash of the (clip, fold) assignment — for determinism checks.

    `clip` (the wav path) is the unique row key; `id` (`segNNNNN`) repeats per
    episode, so it must NOT be used to join folds back to the manifest.
    """
    pairs = sorted(f"{r.clip},{r.fold}" for r in df[["clip", "fold"]].itertuples(index=False))
    return hashlib.md5("\n".join(pairs).encode()).hexdigest()


def _summary(df: pd.DataFrame, n_splits: int) -> str:
    lines = [f"# splits — {len(df)} clean clips, {n_splits}-fold GroupKFold(ep,speaker)"]
    lines.append(f"split_hash: {split_hash(df)}")
    lines.append("fold | clips | groups")
    for f in range(n_splits):
        sub = df[df["fold"] == f]
        lines.append(f"  {f}  | {len(sub):5d} | {sub.groupby(list(GROUP_COLS)).ngroups}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", required=True, help="path to manifest.csv")
    ap.add_argument("--out", required=True, help="output splits.csv (id, ep, speaker, fold)")
    ap.add_argument("--n-splits", type=int, default=5)
    args = ap.parse_args()

    df = load_manifest(args.manifest)
    df = assign_folds(df, n_splits=args.n_splits)
    cols = ["clip", *GROUP_COLS, "fold"]
    df[cols].to_csv(args.out, index=False)
    print(_summary(df, args.n_splits))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
