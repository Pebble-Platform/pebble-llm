"""User-level train/val/test splitting (strategy §5.2, §5.5).

The same user must NEVER appear in more than one split — otherwise the model
can memorize a user and the test set leaks. We hash the userId deterministically
so the assignment is stable across runs and reproducible from metadata alone.

Sampling-constraint note (§5.2): split by user FIRST, then stratify by severity
quartile *within* the assigned users. Do not stratify at message level then dedup
by user — that reintroduces leakage.
"""

from __future__ import annotations

import hashlib
from typing import Literal

Split = Literal["train", "val", "test"]


def assign_split(
    user_id: str,
    *,
    val_fraction: float = 0.1,
    test_fraction: float = 0.1,
    salt: str = "pebble-v1",
) -> Split:
    """Deterministically map a userId to a split via a stable hash.

    Stored once as metadata on every training row so a re-export reproduces the
    exact same partition. ``salt`` lets us re-shuffle deliberately if ever needed.
    """
    digest = hashlib.sha256(f"{salt}:{user_id}".encode()).hexdigest()
    # take the first 8 hex chars → [0, 1) bucket
    bucket = int(digest[:8], 16) / 0xFFFFFFFF
    if bucket < test_fraction:
        return "test"
    if bucket < test_fraction + val_fraction:
        return "val"
    return "train"
