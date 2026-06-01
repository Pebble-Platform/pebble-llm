# Annotation Guidelines

> Draft. Finalize the taxonomy section after the Week-3 pilot (§3.2) before the
> main annotation pass — the whole pipeline depends on it being stable.

## Dimensions

| Dimension | Type | Definition |
|---|---|---|
| energy | float [0–1] | User's activation level (subject to the §5.2 independence check). |
| severity | float [0–1] | Intensity of negative emotion. The core routing signal. |
| socialIsolation | float [0–1] | Degree of social-disconnection signals (subject to §3.3 gate). |
| receptivity | float [0–1] | Venting (0) vs. seeking input (1) (subject to §3.4 gate). |
| detectedEmotion | label | One of the 12-label taxonomy (§3.1). |
| safetyFlag | bool | Crisis signal. Err toward over-triggering. |

## Calibration examples (edge cases)

- Sarcasm: "Oh great, another Monday" → anxiety/frustration, not joy.
- Minimization: "I'm fine" with high-severity context → severity reflects context.
- Mixed: "Got the promotion but I feel empty" → exhaustion/sadness, not joy.
- Figurative: "This deadline is killing me" → frustration, safetyFlag **false**.
- Indirect crisis: "I've been giving away my things" → safetyFlag **true**.

## Agreement

Measure Krippendorff's α (continuous) and Cohen's κ (categorical). If α < 0.6 on any
dimension, the guidelines are ambiguous — revise and re-annotate before proceeding.
