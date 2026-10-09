# vnser-train — pilot SER baseline (speech-only, frozen WavLM-Large)

> ⚠ **PILOT, HUMAN single-annotator labels (train labels single-pass; blind owner↔rater κ 0.513 on a 343-clip sample, change 014).**
> Report as pilot baselines, NOT a settled accuracy claim (I6). Two evals below:
> **GroupKFold(ep)** pools both series → identity leaks WITHIN a series (cast
> recurs) → optimistic. **Leave-one-series-out** trains on one show and tests the
> other → cross-cast, TRUE speaker-disjoint (I4 / ADR-002) — the honest number.

- backbone: `microsoft/wavlm-large` (frozen, masked-mean pool) + linear probe
- series: ['chay-tron-thanh-xuan', 've-nha-di-con']
- clips: 1139 human-clean · emotion 5-class
- split_hash (gkf): `f6dd57308a35bad6efc357aec611beb0` · seed 0
- emotion class counts (full set): {'neutral': 367, 'anger': 251, 'joy': 234, 'fear_anxiety': 131, 'sadness': 156}

## Eval A — GroupKFold(ep), within-pool (optimistic)

| Head | Metric | Value | 95% CI |
|---|---|---|---|
| emotion (5-class) | macro-F1 | 0.428 | [0.397, 0.455] |
| emotion (5-class) | UAR | 0.432 | [0.402, 0.460] |
| affect | CCC valence | 0.147 | [0.127, 0.166] |
| affect | CCC arousal | 0.162 | [0.147, 0.177] |

## Eval B — Leave-one-series-out, cross-cast (TRUE speaker-disjoint)

| Head | Metric | Value | 95% CI |
|---|---|---|---|
| emotion (5-class) | macro-F1 | 0.351 | [0.324, 0.375] |
| emotion (5-class) | UAR | 0.351 | [0.324, 0.376] |
| affect | CCC valence | 0.092 | [0.072, 0.112] |
| affect | CCC arousal | 0.101 | [0.090, 0.112] |

> The gap A→B measures how much the within-series identity leak inflates A.

UAR (unweighted average recall = balanced accuracy) is the imbalanced-SER
standard; macro-F1 shown alongside. Thin classes (fear_anxiety/sadness) have small
test support — read their contribution with the CI, not point values.

Anchor (NOT apples-to-apples): WavLM-Large ~34/33 macro-F1 on MSP-Podcast
8-class [bimodal-ser paper 02] — different language, labels, class count.