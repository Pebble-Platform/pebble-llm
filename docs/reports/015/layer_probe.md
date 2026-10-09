# Change 015 §4 — where emotion lives in WavLM-Large (layer-wise linear probe)

> ⚠ **Pilot, single-annotator labels** (ADR-003; owner↔blind κ 0.513) — NOT a headline
> accuracy (I6). F0 / phonation features here carry **lexical tone and emotion mixed**:
> no syllable-tone labels exist yet to separate them. Northern dialect only.

- head/settings = baseline kernel (012 §10) · seeds [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] pooled · series ['chay-tron-thanh-xuan', 've-nha-di-con']
- §4.1 curve is DESCRIPTIVE: its peak was picked on the test folds. The decision
  (§5) reads only the in-fold selection below.

## §4.2 Decision — layer chosen inside the training fold vs layer 24 (LOSO)

| Δ macro-F1 (ℓ* − 24) | 95% CI (paired bootstrap) | per-seed Δ range | verdict (§5) |
|--:|---|---|---|
| +0.035 | [+0.014, +0.056] | [+0.010, +0.040] | in-fold layer selection beats layer 24 - switch the baseline feature (new change) |

ℓ* per (test series × seed): chay-t/s0=12, ve-nha/s0=16, chay-t/s1=21, ve-nha/s1=16, chay-t/s2=13, ve-nha/s2=16, chay-t/s3=13, ve-nha/s3=16, chay-t/s4=23, ve-nha/s4=16, chay-t/s5=13, ve-nha/s5=16, chay-t/s6=8, ve-nha/s6=16, chay-t/s7=12, ve-nha/s7=16, chay-t/s8=14, ve-nha/s8=13, chay-t/s9=11, ve-nha/s9=16

## §4.1 Curve (pooled seeds) + §4.3 eGeMAPS probe

| features | GKF macro-F1 | LOSO macro-F1 [CI] | LOSO UAR | LOSO CCC val | LOSO CCC aro |
|---|--:|---|--:|--:|--:|
| layer 0 | 0.269 | 0.180 [0.160, 0.198] | 0.189 | 0.083 | 0.122 |
| layer 1 | 0.320 | 0.231 [0.209, 0.252] | 0.227 | 0.097 | 0.103 |
| layer 2 | 0.323 | 0.236 [0.214, 0.255] | 0.235 | 0.077 | 0.105 |
| layer 3 | 0.335 | 0.258 [0.236, 0.277] | 0.260 | 0.095 | 0.119 |
| layer 4 | 0.362 | 0.262 [0.238, 0.284] | 0.261 | 0.115 | 0.109 |
| layer 5 | 0.354 | 0.269 [0.248, 0.289] | 0.273 | 0.117 | 0.104 |
| layer 6 | 0.368 | 0.272 [0.251, 0.293] | 0.274 | 0.114 | 0.086 |
| layer 7 | 0.373 | 0.280 [0.257, 0.302] | 0.281 | 0.102 | 0.103 |
| layer 8 | 0.368 | 0.285 [0.263, 0.305] | 0.287 | 0.104 | 0.105 |
| layer 9 | 0.386 | 0.293 [0.269, 0.314] | 0.298 | 0.090 | 0.115 |
| layer 10 | 0.379 | 0.291 [0.268, 0.313] | 0.295 | 0.102 | 0.104 |
| layer 11 | 0.391 | 0.314 [0.290, 0.338] | 0.315 | 0.093 | 0.109 |
| layer 12 | 0.386 | 0.298 [0.274, 0.321] | 0.299 | 0.108 | 0.114 |
| layer 13 | 0.386 | 0.287 [0.264, 0.310] | 0.291 | 0.112 | 0.108 |
| layer 14 | 0.388 | 0.299 [0.277, 0.323] | 0.300 | 0.116 | 0.119 |
| layer 15 | 0.392 | 0.296 [0.272, 0.317] | 0.296 | 0.115 | 0.112 |
| layer 16 | 0.376 | 0.277 [0.255, 0.299] | 0.280 | 0.111 | 0.113 |
| layer 17 | 0.366 | 0.281 [0.258, 0.302] | 0.284 | 0.108 | 0.112 |
| layer 18 | 0.378 | 0.275 [0.253, 0.297] | 0.277 | 0.102 | 0.106 |
| layer 19 | 0.376 | 0.299 [0.274, 0.322] | 0.302 | 0.107 | 0.111 |
| layer 20 | 0.375 | 0.276 [0.252, 0.299] | 0.279 | 0.112 | 0.108 |
| layer 21 | 0.382 | 0.282 [0.257, 0.304] | 0.286 | 0.109 | 0.118 |
| layer 22 | 0.385 | 0.280 [0.257, 0.302] | 0.281 | 0.100 | 0.114 |
| layer 23 | 0.369 | 0.281 [0.257, 0.304] | 0.283 | 0.091 | 0.102 |
| layer 24 (baseline) | 0.361 | 0.261 [0.237, 0.282] | 0.263 | 0.082 | 0.095 |
| eGeMAPS-88 | 0.289 | 0.229 [0.210, 0.248] | 0.237 | -0.001 | 0.071 |
