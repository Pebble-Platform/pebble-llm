"""Inference wrapper for serving (strategy §6.1 Step 4).

Loads a trained checkpoint once at startup and exposes a single classify() call.
Two serving tracks (decide via the Week-8 spike, §4 / OQ6):
  - Track A (baseline): GPU FP16 with FlashAttention. ~20-50ms. Assumed default.
  - Track B (spike):    INT8 ONNX on CPU. ~50-150ms. Feasibility UNPROVEN for NeoBERT.

This loads the Torch model. The ONNX path is gated behind cfg.serving.onnx (TODO).
"""

from __future__ import annotations

import torch

from pebble_llm.config import Config
from pebble_llm.data.preprocess import assemble_input
from pebble_llm.data.taxonomy import ID_TO_LABEL
from pebble_llm.models.neobert_multitask import NeoBERTMultiTask
from pebble_llm.serving.schemas import ClassifyRequest, ClassifyResponse


class Classifier:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.device = torch.device(cfg.serving.device)
        if cfg.serving.onnx:
            raise NotImplementedError("ONNX (Track B) serving is a feasibility spike — see §4/OQ6.")
        # TODO: load weights from cfg.serving.checkpoint_path (state_dict + tokenizer)
        self.model = NeoBERTMultiTask(cfg.model).to(self.device).eval()
        self.score_dims = cfg.model.score_dims

    @torch.no_grad()
    def classify(self, req: ClassifyRequest) -> ClassifyResponse:
        text = assemble_input(req.message, req.context, self.cfg.data.context_window)
        # TODO: tokenize `text`, run self.model, map outputs. Placeholder zeros below.
        _ = text
        scores = dict.fromkeys(self.score_dims, 0.0)
        return ClassifyResponse(
            energy=scores.get("energy", 0.0),
            severity=scores.get("severity", 0.0),
            socialIsolation=scores.get("socialIsolation", 0.0),
            receptivity=scores.get("receptivity", 0.0),
            detectedEmotion=ID_TO_LABEL[0],
            safetyFlag=False,
        )
