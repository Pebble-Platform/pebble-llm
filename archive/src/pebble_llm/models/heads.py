"""Multi-task heads on the shared 768-dim [CLS] representation (strategy §4).

  - ScoreHead:   encoder → dropout → dense(256) → GELU → dropout → dense(K) → sigmoid
  - EmotionHead: encoder → dropout → dense(256) → GELU → dropout → dense(N)  (softmax at inference)
  - SafetyHead:  encoder → dropout → dense(64)  → GELU → dense(1)            (binary logit)
"""

from __future__ import annotations

import torch
from torch import nn


class ScoreHead(nn.Module):
    """K continuous scores in [0, 1] (severity, and survivors of the §3.3/§3.4 gates)."""

    def __init__(self, hidden_size: int, num_scores: int, head_dim: int = 256, dropout: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, head_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(head_dim, num_scores),
        )

    def forward(self, cls: torch.Tensor) -> torch.Tensor:
        return torch.sigmoid(self.net(cls))


class EmotionHead(nn.Module):
    """N-way emotion logits over the taxonomy. Warm-started from GoEmotions."""

    def __init__(self, hidden_size: int, num_labels: int, head_dim: int = 256, dropout: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, head_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(head_dim, num_labels),
        )

    def forward(self, cls: torch.Tensor) -> torch.Tensor:
        return self.net(cls)  # raw logits; CE applies log-softmax


class SafetyHead(nn.Module):
    """Single binary crisis logit. Trained with high positive-class weight (§4)."""

    def __init__(self, hidden_size: int, head_dim: int = 64, dropout: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, head_dim),
            nn.GELU(),
            nn.Linear(head_dim, 1),
        )

    def forward(self, cls: torch.Tensor) -> torch.Tensor:
        return self.net(cls).squeeze(-1)  # raw logit; BCEWithLogits applies sigmoid
