# Change 015 — EXPLORATORY: class-set variants (not pre-registered)

- clips 1324 · 5-class subset 1139 · seeds [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] · LOSO
- human κ owner↔blind (014, n=343): 7-class 0.513 · disgust→anger 0.535 · drop disgust+surprise 0.621 (n=276)

| layer | variant | 7-class model | variant model | Δ | 95% CI |
|---|---|--:|--:|--:|---|
| 24 | drop disgust+surprise (5 cls) | 0.356 | 0.359 | +0.004 | [-0.011, +0.018] |
| 24 | merge disgust→anger (6 cls) | 0.296 | 0.292 | -0.004 | [-0.016, +0.006] |
| 16 | drop disgust+surprise (5 cls) | 0.394 | 0.407 | +0.013 | [+0.001, +0.026] |
| 16 | merge disgust→anger (6 cls) | 0.318 | 0.328 | +0.010 | [-0.002, +0.023] |
