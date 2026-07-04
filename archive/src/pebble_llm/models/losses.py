"""Weighted multi-task loss (strategy §4, §6.1 Step 2).

Loss = w_score · MSE(scores) + w_emotion · CE(emotion) + w_safety · BCE(safety)
with safety weighted 2x and a 10x positive-class weight inside the BCE to
prioritize recall at the ~1-2 % positive rate.

**Per-head masking.** The v1 transfer pools are disjoint — a GoEmotions row has
no severity label, an EI-reg row has no emotion label, and no public row carries
a safety label (``build_dataset.py``). Each example therefore supplies a per-head
mask; a head only contributes loss for the examples that actually label it. Each
head's loss is averaged over its *active* examples only, so a batch that is all
emotion (or all severity) yields exactly zero loss on the inactive heads. The
safety head is never active in v1 (mask always 0), so its branch contributes 0.

Multi-task balancing caveat (§6.1): static weights may let the clean-signal
emotion head dominate the shared [CLS] and starve the regression heads. If
per-head val metrics diverge, switch to uncertainty weighting (Kendall et al.)
or GradNorm — left as a TODO hook below.
"""

from __future__ import annotations

import torch
import torch.nn.functional as F
from torch import nn


def _masked_mean(per_sample: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """Mean of ``per_sample`` over the active rows (``mask == 1``).

    Returns 0 (no gradient) when no row is active, via a clamped denominator —
    the masked numerator is already 0, so the head simply drops out of the batch.
    """
    return (per_sample * mask).sum() / mask.sum().clamp_min(1.0)


class MultiTaskLoss(nn.Module):
    def __init__(
        self,
        w_score: float = 1.0,
        w_emotion: float = 1.0,
        w_safety: float = 2.0,
        safety_pos_weight: float = 10.0,
    ):
        super().__init__()
        self.w_score = w_score
        self.w_emotion = w_emotion
        self.w_safety = w_safety
        # Buffer so .to(device) moves it with the module (BCE needs it on-device).
        self.register_buffer("safety_pos_weight", torch.tensor(safety_pos_weight))

    def forward(
        self,
        *,
        score_pred: torch.Tensor,
        score_target: torch.Tensor,
        emotion_logits: torch.Tensor,
        emotion_target: torch.Tensor,
        safety_logit: torch.Tensor,
        safety_target: torch.Tensor,
        mask_score: torch.Tensor | None = None,
        mask_emotion: torch.Tensor | None = None,
        mask_safety: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, dict[str, float]]:
        batch = emotion_logits.shape[0]
        if mask_score is None:
            mask_score = score_pred.new_ones(batch)
        if mask_emotion is None:
            mask_emotion = score_pred.new_ones(batch)
        if mask_safety is None:
            mask_safety = score_pred.new_ones(batch)

        # Per-sample losses (reduction="none"), then averaged over active rows.
        score_ps = F.mse_loss(score_pred, score_target, reduction="none").mean(dim=-1)
        # emotion_target is -1 for non-emotion rows; clamp to a valid index so CE
        # doesn't error — the mask removes those rows from the average anyway.
        emotion_ps = F.cross_entropy(
            emotion_logits, emotion_target.clamp_min(0), reduction="none"
        )
        safety_ps = F.binary_cross_entropy_with_logits(
            safety_logit, safety_target, pos_weight=self.safety_pos_weight, reduction="none"
        )

        loss_score = _masked_mean(score_ps, mask_score)
        loss_emotion = _masked_mean(emotion_ps, mask_emotion)
        loss_safety = _masked_mean(safety_ps, mask_safety)
        total = (
            self.w_score * loss_score
            + self.w_emotion * loss_emotion
            + self.w_safety * loss_safety
        )
        parts = {
            "loss_score": loss_score.item(),
            "loss_emotion": loss_emotion.item(),
            "loss_safety": loss_safety.item(),
            "loss_total": total.item(),
        }
        return total, parts
