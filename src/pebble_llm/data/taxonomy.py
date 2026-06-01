"""Emotion taxonomy and the GoEmotions → Pebble label mapping (strategy §3.1).

IMPORTANT: this taxonomy is provisional until the Week-3 taxonomy pilot (§3.2)
finalizes it. Labels confused >40 % of the time get merged there. Update this
module — and the mapping table — only after the pilot signs off, because the
whole pipeline (annotation, eval, head dimensions) depends on it being stable.
"""

from __future__ import annotations

# The 12-label taxonomy. Order is the canonical class index order for the emotion head.
PEBBLE_LABELS: list[str] = [
    "joy",
    "gratitude",
    "hope",
    "sadness",
    "frustration",
    "anxiety",
    "confusion",
    "loneliness",
    "exhaustion",
    "guilt",
    "calm",
    "neutral",
]

LABEL_TO_ID: dict[str, int] = {label: i for i, label in enumerate(PEBBLE_LABELS)}
ID_TO_LABEL: dict[int, str] = {i: label for label, i in LABEL_TO_ID.items()}

# GoEmotions (27 + neutral) → Pebble. Used to warm-start the emotion head (§5.1, §6.1 Step 1).
# GoEmotions labels with no good Pebble target are mapped to "neutral".
GOEMOTIONS_TO_PEBBLE: dict[str, str] = {
    "joy": "joy",
    "amusement": "joy",
    "excitement": "joy",
    "admiration": "gratitude",
    "approval": "gratitude",
    "gratitude": "gratitude",
    "optimism": "hope",
    "desire": "hope",
    "grief": "sadness",
    "remorse": "guilt",
    "sadness": "sadness",
    "anger": "frustration",
    "annoyance": "frustration",
    "disapproval": "frustration",
    "nervousness": "anxiety",
    "fear": "anxiety",
    "confusion": "confusion",
    "embarrassment": "confusion",
    "relief": "calm",
    "caring": "calm",
    "neutral": "neutral",
    # GoEmotions labels with no direct Pebble equivalent → neutral (weak signal)
    "curiosity": "neutral",
    "disgust": "frustration",
    "disappointment": "sadness",
    "love": "gratitude",
    "pride": "joy",
    "realization": "neutral",
    "surprise": "neutral",
}

# loneliness and exhaustion have NO GoEmotions source (§3.1) — they rely on
# EmpatheticDialogues transfer + Pebble human annotation. Documented, not a bug.
LABELS_WITHOUT_GOEMOTIONS_SOURCE: frozenset[str] = frozenset({"loneliness", "exhaustion"})


def map_goemotions(label: str) -> str:
    """Map a single GoEmotions label to its Pebble taxonomy label."""
    return GOEMOTIONS_TO_PEBBLE.get(label, "neutral")
