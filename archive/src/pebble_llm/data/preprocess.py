"""Input assembly and analysis checks (strategy §5.2).

Two responsibilities:
  1. Assemble the model input string: current message + last N messages, interleaved.
  2. The Week-2 energy/severity independence check (§5.2): if |corr| > 0.7, energy
     carries no independent signal and the head should be dropped before training.
"""

from __future__ import annotations

import numpy as np


def assemble_input(current_message: str, prior_messages: list[str], context_window: int = 3) -> str:
    """Interleave the current message with up to `context_window` prior messages.

    Most recent prior message last, current message clearly delimited so the model
    learns which turn it is scoring.
    """
    ctx = prior_messages[-context_window:]
    parts = [f"[prev] {m}" for m in ctx] + [f"[current] {current_message}"]
    return "\n".join(parts)


def energy_severity_independence(energy: list[float], severity: list[float]) -> float:
    """Pearson correlation between energy and severity across the silver labels.

    Run once ~1K labels exist. If abs(r) > 0.7, drop the energy head (§5.2) — it is
    redundant and wastes capacity/annotation budget on a 5K dataset.
    """
    r = float(np.corrcoef(energy, severity)[0, 1])
    return r
