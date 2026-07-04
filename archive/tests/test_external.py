from pebble_llm.data.external import _eireg_severity, _parse_eireg

# A few EI-reg rows as they appear in the gold TSVs (tab-separated, real header).
ANGER_LINES = [
    "ID\tTweet\tAffect Dimension\tIntensity Score",
    "2017-En-1\ti am so angry right now\tanger\t0.812",
    "2017-En-2\teverything is irritating today\tanger\t0.730",
]


def test_negative_emotion_keeps_intensity():
    assert _eireg_severity("anger", 0.8) == 0.8
    assert _eireg_severity("fear", 0.5) == 0.5
    assert _eireg_severity("sadness", 0.73) == 0.73


def test_joy_is_low_distress_anchor():
    assert _eireg_severity("joy", 0.95) == 0.0


def test_parse_maps_text_and_severity_and_skips_header():
    rows = _parse_eireg(ANGER_LINES, "anger")
    assert rows == [
        {"text": "i am so angry right now", "severity": 0.812},
        {"text": "everything is irritating today", "severity": 0.730},
    ]


def test_parse_joy_file_anchors_to_zero():
    joy_lines = [
        "ID\tTweet\tAffect Dimension\tIntensity Score",
        "2017-En-9\thaving the best day ever\tjoy\t0.910",
    ]
    assert _parse_eireg(joy_lines, "joy") == [
        {"text": "having the best day ever", "severity": 0.0}
    ]


def test_parse_skips_unlabeled_rows():
    bad = [
        "ID\tTweet\tAffect Dimension\tIntensity Score",
        "2017-En-x\tno gold score here\tanger\tNONE",
    ]
    assert _parse_eireg(bad, "anger") == []
