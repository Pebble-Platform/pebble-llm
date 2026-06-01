from pebble_llm.data.taxonomy import (
    GOEMOTIONS_TO_PEBBLE,
    ID_TO_LABEL,
    LABEL_TO_ID,
    PEBBLE_LABELS,
    map_goemotions,
)


def test_twelve_labels_unique_and_indexed():
    assert len(PEBBLE_LABELS) == 12
    assert len(set(PEBBLE_LABELS)) == 12
    assert LABEL_TO_ID["joy"] == 0
    assert ID_TO_LABEL[0] == "joy"


def test_label_id_roundtrip():
    for label in PEBBLE_LABELS:
        assert ID_TO_LABEL[LABEL_TO_ID[label]] == label


def test_goemotions_maps_into_taxonomy():
    for target in GOEMOTIONS_TO_PEBBLE.values():
        assert target in PEBBLE_LABELS


def test_unknown_goemotions_label_falls_back_to_neutral():
    assert map_goemotions("not_a_real_label") == "neutral"
