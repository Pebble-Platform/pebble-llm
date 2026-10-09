# Change 012 - label-quality ablation (pre-registered)

- clips: 1071 (fixed set, identical in every arm)
- test set: **606 clips the second rater left unchanged** - same labels
  for every arm, so only the TRAINING labels vary.
- seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] · split_hash `9d5d5c2edd0f5e6af2ff901ef5c9cae2`

> This is NOT a kappa and NOT a headline accuracy. The review pass was anchored
> (the rater saw the owner's label first) - preregistration §8.

## Eval - groupkfold

| Arm | train n | macro-F1 | 95% CI | UAR | CCC val | CCC aro |
|---|--:|--:|---|--:|--:|--:|
| A_owner | 1071 | 0.341 | [0.303, 0.378] | 0.346 | 0.147 | 0.174 |
| B_reviewed | 1071 | 0.337 | [0.298, 0.376] | 0.341 | 0.142 | 0.186 |
| C_agreed | 606 | 0.355 | [0.312, 0.395] | 0.352 | 0.122 | 0.175 |
| C_owner_sizematched | 606 | 0.377 | [0.334, 0.421] | 0.374 | 0.153 | 0.179 |

### Paired deltas (macro-F1, shared bootstrap over test clips)

| Comparison | Δ | 95% CI | per-seed Δ range | verdict (§7) |
|---|--:|---|---|---|
| B_reviewed-A_owner | -0.005 | [-0.043, +0.031] | [-0.007, +0.003] | H0 - label noise is not the bottleneck; stop spending adjudication on model quality |
| C_agreed-C_owner_sizematched | -0.022 | [-0.065, +0.017] | [-0.021, +0.056] | H0 - label noise is not the bottleneck; stop spending adjudication on model quality |

## Eval - leave_one_series_out

| Arm | train n | macro-F1 | 95% CI | UAR | CCC val | CCC aro |
|---|--:|--:|---|--:|--:|--:|
| A_owner | 1071 | 0.258 | [0.226, 0.292] | 0.258 | 0.071 | 0.114 |
| B_reviewed | 1071 | 0.283 | [0.242, 0.321] | 0.279 | 0.066 | 0.129 |
| C_agreed | 606 | 0.279 | [0.239, 0.316] | 0.273 | 0.077 | 0.132 |
| C_owner_sizematched | 606 | 0.269 | [0.236, 0.304] | 0.271 | 0.087 | 0.124 |

### Paired deltas (macro-F1, shared bootstrap over test clips)

| Comparison | Δ | 95% CI | per-seed Δ range | verdict (§7) |
|---|--:|---|---|---|
| B_reviewed-A_owner | +0.024 | [-0.011, +0.056] | [+0.019, +0.037] | H0 - label noise is not the bottleneck; stop spending adjudication on model quality |
| C_agreed-C_owner_sizematched | +0.011 | [-0.036, +0.049] | [-0.000, +0.048] | H0 - label noise is not the bottleneck; stop spending adjudication on model quality |

The decision rule was fixed before the run; the verdict column applies it
mechanically. `C_agreed` vs `A_owner` is NOT a valid comparison (different
training-set size) - compare it to `C_owner_sizematched` instead.