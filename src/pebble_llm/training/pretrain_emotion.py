"""Emotion-head pre-training on GoEmotions (strategy §6.1 Step 1).

Freeze the encoder for the first 2 epochs so the emotion head converges without
destabilizing the pretrained representations, then unfreeze 1-2 epochs at LR 1e-5
for shallow adaptation. Only the emotion head is active here.

TODO: build a single-task (emotion-only) loop reusing NeoBERTMultiTask but driving
only the emotion head + CrossEntropy on the mapped GoEmotions labels.
"""

from __future__ import annotations

from pebble_llm.config import Config


def pretrain_emotion_head(cfg: Config) -> None:
    raise NotImplementedError(
        "GoEmotions emotion-head pre-training not implemented yet (§6.1 Step 1)."
    )
