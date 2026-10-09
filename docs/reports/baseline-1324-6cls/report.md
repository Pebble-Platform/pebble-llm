# vnser-train — pilot SER baseline (speech-only, frozen WavLM-Large)

> ⚠ **PILOT, HUMAN single-annotator labels (no inter-annotator κ yet — ADR-003).**
> Report as pilot baselines, NOT a settled accuracy claim (I6). Two evals below:
> **GroupKFold(ep)** pools both series → identity leaks WITHIN a series (cast
> recurs) → optimistic. **Leave-one-series-out** trains on one show and tests the
> other → cross-cast, TRUE speaker-disjoint (I4 / ADR-002) — the honest number.

- backbone: `microsoft/wavlm-large` (frozen, masked-mean pool) + linear probe
- series: ['chay-tron-thanh-xuan', 've-nha-di-con']
- clips: 1242 human-clean · emotion 6-class
- split_hash (gkf): `ab12f9a921dd6d0505a5ae17d1766f80` · seed 0
- emotion class counts (full set): {'neutral': 367, 'anger': 251, 'joy': 234, 'fear_anxiety': 131, 'sadness': 156, 'disgust': 103}

## Eval A — GroupKFold(ep), within-pool (optimistic)

| Head | Metric | Value | 95% CI |
|---|---|---|---|
| emotion (6-class) | macro-F1 | 0.384 | [0.357, 0.411] |
| emotion (6-class) | UAR | 0.389 | [0.361, 0.418] |
| affect | CCC valence | 0.148 | [0.130, 0.167] |
| affect | CCC arousal | 0.163 | [0.148, 0.177] |

## Eval B — Leave-one-series-out, cross-cast (TRUE speaker-disjoint)

| Head | Metric | Value | 95% CI |
|---|---|---|---|
| emotion (6-class) | macro-F1 | 0.288 | [0.264, 0.312] |
| emotion (6-class) | UAR | 0.290 | [0.267, 0.315] |
| affect | CCC valence | 0.087 | [0.066, 0.105] |
| affect | CCC arousal | 0.097 | [0.086, 0.107] |

> The gap A→B measures how much the within-series identity leak inflates A.

UAR (unweighted average recall = balanced accuracy) is the imbalanced-SER
standard; macro-F1 shown alongside. Thin classes (surprise/disgust) have small
test support — read their contribution with the CI, not point values.

Anchor (NOT apples-to-apples): WavLM-Large ~34/33 macro-F1 on MSP-Podcast
8-class [bimodal-ser paper 02] — different language, labels, class count.