"""Response schema for the voice affect endpoint (voice extension).

Companion to schemas.py (text /classify). The voice model emits an emotion
softmax + a high-distress safety head; the Decision Engine consumes these the
same way it consumes the text scores.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class VoiceClassifyResponse(BaseModel):
    detectedEmotion: str = Field(..., description="argmax of the 8-way RAVDESS emotion head")
    emotionProbs: dict[str, float] = Field(..., description="softmax over the emotion taxonomy")
    distressScore: float = Field(..., ge=0.0, le=1.0, description="sigmoid of the safety head")
    safetyFlag: bool = Field(..., description="distressScore >= recall-floored threshold")
    backbone: str = Field(..., description="speech encoder that produced the embedding")
