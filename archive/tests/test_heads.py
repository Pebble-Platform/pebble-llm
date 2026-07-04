import torch

from pebble_llm.models.heads import EmotionHead, SafetyHead, ScoreHead
from pebble_llm.models.losses import MultiTaskLoss


def test_score_head_outputs_in_unit_range():
    head = ScoreHead(hidden_size=768, num_scores=3)
    out = head(torch.randn(4, 768))
    assert out.shape == (4, 3)
    assert (out >= 0).all() and (out <= 1).all()


def test_emotion_head_shape():
    head = EmotionHead(hidden_size=768, num_labels=12)
    assert head(torch.randn(4, 768)).shape == (4, 12)


def test_safety_head_is_scalar_logit_per_example():
    head = SafetyHead(hidden_size=768)
    assert head(torch.randn(4, 768)).shape == (4,)


def test_multitask_loss_is_finite_and_decomposed():
    loss_fn = MultiTaskLoss()
    total, parts = loss_fn(
        score_pred=torch.rand(4, 3),
        score_target=torch.rand(4, 3),
        emotion_logits=torch.randn(4, 12),
        emotion_target=torch.randint(0, 12, (4,)),
        safety_logit=torch.randn(4),
        safety_target=torch.randint(0, 2, (4,)).float(),
    )
    assert torch.isfinite(total)
    assert set(parts) == {"loss_score", "loss_emotion", "loss_safety", "loss_total"}
