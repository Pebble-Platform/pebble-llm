"""Request/response schemas for the /classify endpoint (strategy §2, §6.1 Step 4).

The encoder emits typed head tensors; the backend assembles them into the exact
object the rest of the Pebble pipeline already expects. Note that themeRepetition
and sessionTrajectory are intentionally NOT model outputs (§2) — the Decision
Engine computes those.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ClassifyRequest(BaseModel):
    message: str = Field(..., description="The user's current message")
    context: list[str] = Field(default_factory=list, description="Last up to 3 prior messages")


class ClassifyResponse(BaseModel):
    energy: float = Field(..., ge=0.0, le=1.0)
    severity: float = Field(..., ge=0.0, le=1.0)
    socialIsolation: float = Field(..., ge=0.0, le=1.0)
    receptivity: float = Field(..., ge=0.0, le=1.0)
    detectedEmotion: str
    safetyFlag: bool
