from pebble_llm.data.build_dataset import emotion_record, severity_record
from pebble_llm.data.taxonomy import LABEL_TO_ID


def test_emotion_record_activates_only_emotion_head():
    rec = emotion_record("i am grateful for today", "gratitude")
    assert rec["emotion_id"] == LABEL_TO_ID["gratitude"]
    assert rec["severity"] == 0.0
    assert rec["mask"] == {"emotion": 1, "score": 0, "safety": 0}


def test_severity_record_activates_only_score_head():
    rec = severity_record("everything hurts and i can't cope", 0.73)
    assert rec["severity"] == 0.73
    assert rec["emotion_id"] == -1  # placeholder; mask governs inclusion
    assert rec["mask"] == {"emotion": 0, "score": 1, "safety": 0}


def test_safety_head_never_active_in_v1():
    assert emotion_record("x", "joy")["mask"]["safety"] == 0
    assert severity_record("y", 0.5)["mask"]["safety"] == 0


def test_records_share_one_schema():
    assert emotion_record("x", "joy").keys() == severity_record("y", 0.5).keys()
