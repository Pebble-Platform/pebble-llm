from pebble_llm.data.splits import assign_split


def test_split_is_deterministic():
    assert assign_split("user-123") == assign_split("user-123")


def test_split_returns_valid_label():
    assert assign_split("user-abc") in {"train", "val", "test"}


def test_user_level_no_leakage():
    # Same user always lands in the same split → no cross-split leakage.
    assigns = {assign_split(f"user-{i}") for _ in range(5) for i in [7]}
    assert len(assigns) == 1


def test_distribution_roughly_matches_fractions():
    counts = {"train": 0, "val": 0, "test": 0}
    for i in range(5000):
        counts[assign_split(f"user-{i}")] += 1
    # ~80/10/10 with tolerance
    assert 0.05 < counts["test"] / 5000 < 0.15
    assert 0.05 < counts["val"] / 5000 < 0.15
    assert counts["train"] / 5000 > 0.70
