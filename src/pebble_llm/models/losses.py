"""Weighted multi-task loss (strategy §4, §6.1 Step 2).

Loss = w_score · MSE(scores) + w_emotion · CE(emotion) + w_safety · BCE(safety)
with safety weighted 2x and a 10x positive-class weight inside the BCE to
prioritize recall at the ~1-2 % positive rate.

Multi-task balancing caveat (§6.1): static weights may let the clean-signal
emotion head dominate the shared [CLS] and starve the regression heads. If
per-head val metrics diverge, switch to uncertainty weighting (Kendall et al.)
or GradNorm — left as a TODO hook below.
"""

from __future__ import annotations

import torch
from torch import nn


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
        self.mse = nn.MSELoss()
        self.ce = nn.CrossEntropyLoss()
        self.bce = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(safety_pos_weight))

    def forward(
        self,
        *,
        score_pred: torch.Tensor,
        score_target: torch.Tensor,
        emotion_logits: torch.Tensor,
        emotion_target: torch.Tensor,
        safety_logit: torch.Tensor,
        safety_target: torch.Tensor,
    ) -> tuple[torch.Tensor, dict[str, float]]:
        loss_score = self.mse(score_pred, score_target)
        loss_emotion = self.ce(emotion_logits, emotion_target)
        loss_safety = self.bce(safety_logit, safety_target)
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
