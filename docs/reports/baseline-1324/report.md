# vnser-train — pilot SER baseline (speech-only, frozen WavLM-Large)

> ⚠ **PILOT, HUMAN single-annotator labels (no inter-annotator κ yet — ADR-003).**
> Report as pilot baselines, NOT a settled accuracy claim (I6). Two evals below:
> **GroupKFold(ep)** pools both series → identity leaks WITHIN a series (cast
> recurs) → optimistic. **Leave-one-series-out** trains on one show and tests the
> other → cross-cast, TRUE speaker-disjoint (I4 / ADR-002) — the honest number.

- backbone: `microsoft/wavlm-large` (frozen, masked-mean pool) + linear probe
- series: ['chay-tron-thanh-xuan', 've-nha-di-con']
- clips: 1324 human-clean · emotion 7-class
- split_hash (gkf): `0a24299b2df2327cf8a5934a1917f0f2` · seed 0
- emotion class counts (full set): {'neutral': 367, 'anger': 251, 'joy': 234, 'fear_anxiety': 131, 'sadness': 156, 'disgust': 103, 'surprise': 82}

## Eval A — GroupKFold(ep), within-pool (optimistic)

| Head | Metric | Value | 95% CI |
|---|---|---|---|
| emotion (7-class) | macro-F1 | 0.356 | [0.330, 0.380] |
| emotion (7-class) | UAR | 0.361 | [0.334, 0.387] |
| affect | CCC valence | 0.134 | [0.116, 0.153] |
| affect | CCC arousal | 0.164 | [0.149, 0.177] |

## Eval B — Leave-one-series-out, cross-cast (TRUE speaker-disjoint)

| Head | Metric | Value | 95% CI |
|---|---|---|---|
| emotion (7-class) | macro-F1 | 0.256 | [0.234, 0.277] |
| emotion (7-class) | UAR | 0.256 | [0.236, 0.279] |
| affect | CCC valence | 0.080 | [0.062, 0.100] |
| affect | CCC arousal | 0.094 | [0.084, 0.105] |

> The gap A→B measures how much the within-series identity leak inflates A.

UAR (unweighted average recall = balanced accuracy) is the imbalanced-SER
standard; macro-F1 shown alongside. Thin classes (surprise/disgust) have small
test support — read their contribution with the CI, not point values.

Anchor (NOT apples-to-apples): WavLM-Large ~34/33 macro-F1 on MSP-Podcast
8-class [bimodal-ser paper 02] — different language, labels, class count.