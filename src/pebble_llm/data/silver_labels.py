"""Ingest Gemini silver labels from Firestore (strategy §5.2).

Silver labels are the bulk of the training data: every Gemini-scored message in
Phases 1-3. They are model-generated, not human-verified.

Provenance matters (OQ5): store the generator model version on every row. When
the generator migrates off 2.0 Flash (shutdown 2026-06-01), re-score a stratified
sample with the new generator and measure per-dimension divergence before mixing
old and new labels.

This module is a stub — it documents the contract. The real Firestore client is
added behind the `gemini` optional-dependency group.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SilverLabelRow:
    doc_id: str
    text: str  # current message + last 3 messages, interleaved
    energy: float
    severity: float
    social_isolation: float
    receptivity: float
    detected_emotion: str
    safety_flag: bool
    # metadata for splitting + provenance
    user_id: str
    session_id: str
    timestamp: str
    generator_model_version: str  # critical — see OQ5
    is_fallback: bool  # exclude fallbacks from training


def fetch_silver_labels(collection: str) -> list[SilverLabelRow]:
    """Fetch all silver-label rows from the Firestore training collection.

    TODO: implement with google-cloud-firestore (extra: `gemini`). Exclude rows
    where ``is_fallback`` is True. Page through the collection; do not load PII
    beyond what the training schema needs.
    """
    raise NotImplementedError(
        f"Firestore ingestion not implemented yet (collection={collection!r}). "
        "Install the 'gemini' extra and wire google-cloud-firestore here."
    )
