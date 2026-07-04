"""NeoBERT multi-task classifier (strategy §4, §6.1).

A shared NeoBERT encoder feeds three heads off the [CLS] representation. The
encoder loads from `chandar-lab/NeoBERT` with `trust_remote_code=True`.

Production note (§4, §6.1 Step 0): PIN an exact revision and VENDOR the custom
modeling code into the repo (src/pebble_llm/models/_neobert_vendor/) so a remote
change can't silently alter behavior. NeoBERT needs FlashAttention/xformers on GPU.
"""

from __future__ import annotations

import torch
from torch import nn
from transformers import AutoModel  # type: ignore[import-untyped]

from pebble_llm.config import ModelConfig
from pebble_llm.models.heads import EmotionHead, SafetyHead, ScoreHead


class NeoBERTMultiTask(nn.Module):
    def __init__(self, cfg: ModelConfig):
        super().__init__()
        self.cfg = cfg
        self.encoder = AutoModel.from_pretrained(
            cfg.name,
            revision=cfg.revision,
            trust_remote_code=cfg.trust_remote_code,
        )
        self.score_head = ScoreHead(
            cfg.hidden_size, num_scores=len(cfg.score_dims),
            head_dim=cfg.head_hidden_dim, dropout=cfg.dropout,
        )
        self.emotion_head = EmotionHead(
            cfg.hidden_size, num_labels=cfg.num_emotion_labels,
            head_dim=cfg.head_hidden_dim, dropout=cfg.dropout,
        )
        self.safety_head = SafetyHead(cfg.hidden_size, dropout=cfg.dropout)

    def set_encoder_trainable(self, trainable: bool) -> None:
        """Freeze/unfreeze the encoder for the staged warmup (§5.3, §6.1)."""
        for p in self.encoder.parameters():
            p.requires_grad = trainable

    def forward(
        self, input_ids: torch.Tensor, attention_mask: torch.Tensor
    ) -> dict[str, torch.Tensor]:
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        # NeoBERT returns last_hidden_state; [CLS] is position 0
        cls = out.last_hidden_state[:, 0, :]
        return {
            "scores": self.score_head(cls),
            "emotion_logits": self.emotion_head(cls),
            "safety_logit": self.safety_head(cls),
        }
