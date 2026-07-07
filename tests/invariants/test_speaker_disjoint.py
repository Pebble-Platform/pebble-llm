"""I4 (best-effort, pilot 1-series) — GroupKFold splits are group-disjoint.

Mirrors invariant I4 for change 004-vnser-training: with a single series the
true speaker unit is (ep, speaker) (pyannote labels are episode-local and reuse
`SPEAKER_NN` across episodes). A valid split therefore keeps every (ep, speaker)
group wholly inside one fold — no group may appear in more than one fold.

The test runs on a synthetic manifest (the real dataset is gitignored under
`data/**`), so it stays green in CI without the private Kaggle data.
"""

from __future__ import annotations

import pathlib
import sys

import pandas as pd

sys.path.insert(
    0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts" / "vietnamese-ser")
)

import make_splits  # noqa: E402


def _synthetic_manifest() -> pd.DataFrame:
    """5 episodes, speaker labels reused across episodes (the real quirk),
    a couple of non-clean rows that must be excluded, uneven clip counts."""
    rows = []
    cid = 0
    # (ep, speaker, n_clips) — SPEAKER_01/07 recur across episodes on purpose.
    spec = [
        ("ep01", "SPEAKER_01", 12),
        ("ep01", "SPEAKER_07", 5),
        ("ep01", "SPEAKER_17", 39),
        ("ep02", "SPEAKER_01", 8),
        ("ep02", "SPEAKER_15", 40),
        ("ep03", "SPEAKER_07", 25),
        ("ep03", "SPEAKER_12", 25),
        ("ep04", "SPEAKER_11", 47),
        ("ep05", "SPEAKER_02", 38),
        ("ep05", "SPEAKER_01", 6),
    ]
    for ep, spk, n in spec:
        for _ in range(n):
            rows.append({"ep": ep, "clip": f"clips/{ep}_seg{cid:05d}.wav", "speaker": spk, "is_clean": True})
            cid += 1
    # two non-clean rows that must be dropped before splitting
    rows.append({"ep": "ep01", "clip": f"clips/ep01_seg{cid:05d}.wav", "speaker": "SPEAKER_09", "is_clean": False})
    cid += 1
    rows.append({"ep": "ep02", "clip": f"clips/ep02_seg{cid:05d}.wav", "speaker": "SPEAKER_03", "is_clean": False})
    return pd.DataFrame(rows)


def test_groups_are_fold_disjoint():
    """Core I4 check: no (ep, speaker) group spans more than one fold."""
    df = make_splits.assign_folds(_synthetic_manifest(), n_splits=5)
    per_group_folds = df.groupby(["ep", "speaker"])["fold"].nunique()
    leaking = per_group_folds[per_group_folds > 1]
    assert leaking.empty, f"groups spanning >1 fold (I4 violation): {list(leaking.index)}"


def test_only_clean_rows_are_split():
    """Non-clean rows are excluded; every returned row has a valid fold."""
    df = make_splits.assign_folds(_synthetic_manifest(), n_splits=5)
    assert df["is_clean"].all()
    assert df["fold"].between(0, 4).all()
    assert len(df) == 245  # sum of clip counts above (12+5+39+8+40+25+25+47+38+6), non-clean dropped


def test_split_is_deterministic():
    """Same input → same fold assignment (stable split_hash)."""
    m = _synthetic_manifest()
    h1 = make_splits.split_hash(make_splits.assign_folds(m, n_splits=5))
    h2 = make_splits.split_hash(make_splits.assign_folds(m, n_splits=5))
    assert h1 == h2
