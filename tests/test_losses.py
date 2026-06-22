import torch

from pebble_llm.models.losses import MultiTaskLoss


def _batch(mask_emotion: float, mask_score: float, batch: int = 4, k: int = 1, n: int = 12) -> dict:
    return {
        "score_pred": torch.rand(batch, k),
        "score_target": torch.rand(batch, k),
        "emotion_logits": torch.randn(batch, n),
        "emotion_target": torch.randint(0, n, (batch,)),
        "safety_logit": torch.randn(batch),
        "safety_target": torch.zeros(batch),
        "mask_emotion": torch.full((batch,), mask_emotion),
        "mask_score": torch.full((batch,), mask_score),
        "mask_safety": torch.zeros(batch),
    }


def test_severity_only_batch_has_zero_emotion_loss():
    _, parts = MultiTaskLoss()(**_batch(mask_emotion=0.0, mask_score=1.0))
    assert parts["loss_emotion"] == 0.0
    assert parts["loss_score"] > 0.0


def test_emotion_only_batch_has_zero_score_loss():
    _, parts = MultiTaskLoss()(**_batch(mask_emotion=1.0, mask_score=0.0))
    assert parts["loss_score"] == 0.0
    assert parts["loss_emotion"] > 0.0


def test_safety_head_never_contributes_in_v1():
    _, parts = MultiTaskLoss()(**_batch(mask_emotion=1.0, mask_score=1.0))
    assert parts["loss_safety"] == 0.0


def test_placeholder_emotion_id_is_safe_when_masked():
    batch = _batch(mask_emotion=0.0, mask_score=1.0)
    batch["emotion_target"] = torch.full((4,), -1)  # build_dataset.py placeholder
    total, parts = MultiTaskLoss()(**batch)
    assert parts["loss_emotion"] == 0.0
    assert torch.isfinite(total)
