# Change 015 §3 — eGeMAPS vs emotion / valence / arousal

> ⚠ **Pilot, single-annotator labels** (ADR-003; owner↔blind κ 0.513) — NOT a headline
> accuracy (I6). F0 / phonation features here carry **lexical tone and emotion mixed**:
> no syllable-tone labels exist yet to separate them. Northern dialect only.
> Normalised by (gender × age_group) only — **recording / mix differences between the
> two series remain in these features** (D1). Clips are not independent (shared
> speakers, episodes): read effect sizes; q-values only filter.

- clips: 1323 · normalisation groups: {'female/young_adult': 661, 'male/young_adult': 335, 'female/middle_aged': 187, 'male/middle_aged': 115, 'male/senior': 25}
- ε² = Kruskal–Wallis effect size over 7 classes; ρ = Spearman; q = BH over all 264 tests

## Pre-registered hypotheses (§1)

| | Hypothesis | Result |
|---|---|---|
| H1a | arousal ρ > 0 with F0 mean AND loudness mean (q < 0.05) | **TRUE** |
| H1b | max \|ρ valence\| < max \|ρ arousal\| over 88 features | **TRUE** |
| H1c | ≥1 voice-quality feature with \|ρ valence\| ≥ 0.1, q < 0.05 | **TRUE** |

## prosody (27 features)

| feature | ε² | q KW | ρ valence | q | ρ arousal | q |
|---|--:|--:|--:|--:|--:|--:|
| `F0semitoneFrom27.5Hz_sma3nz_percentile80.0` | 0.192 | 9.3e-51 | -0.162 | 6.8e-09 | +0.562 | 1.8e-108 |
| `F0semitoneFrom27.5Hz_sma3nz_amean` | 0.173 | 2.3e-45 | -0.151 | 6.8e-08 | +0.551 | 6.6e-104 |
| `F0semitoneFrom27.5Hz_sma3nz_percentile50.0` | 0.171 | 6.4e-45 | -0.161 | 9e-09 | +0.545 | 2.7e-101 |
| `loudness_sma3_percentile80.0` | 0.151 | 1.9e-39 | -0.181 | 8.9e-11 | +0.551 | 6.6e-104 |
| `F0semitoneFrom27.5Hz_sma3nz_percentile20.0` | 0.149 | 7.8e-39 | -0.134 | 1.8e-06 | +0.517 | 6.1e-90 |
| `loudness_sma3_pctlrange0-2` | 0.144 | 1.7e-37 | -0.190 | 8.3e-12 | +0.525 | 8.8e-93 |
| `loudness_sma3_amean` | 0.137 | 1.3e-35 | -0.160 | 1.1e-08 | +0.533 | 3.4e-96 |
| `loudness_sma3_meanRisingSlope` | 0.117 | 4.2e-30 | -0.185 | 3.3e-11 | +0.452 | 2.4e-66 |
| `loudness_sma3_percentile50.0` | 0.104 | 1.6e-26 | -0.139 | 7.8e-07 | +0.464 | 2.1e-70 |
| `loudness_sma3_meanFallingSlope` | 0.096 | 2.3e-24 | -0.169 | 1.5e-09 | +0.395 | 1.8e-49 |
| `equivalentSoundLevel_dBp` | 0.085 | 3e-21 | -0.172 | 6.6e-10 | +0.448 | 3.3e-65 |
| `loudness_sma3_stddevRisingSlope` | 0.071 | 2e-17 | -0.136 | 1.3e-06 | +0.370 | 3.2e-43 |
| `loudness_sma3_stddevFallingSlope` | 0.065 | 9.9e-16 | -0.141 | 5.1e-07 | +0.310 | 3.4e-30 |
| `F0semitoneFrom27.5Hz_sma3nz_pctlrange0-2` | 0.054 | 7.5e-13 | -0.113 | 5.9e-05 | +0.165 | 3.4e-09 |
| `F0semitoneFrom27.5Hz_sma3nz_meanFallingSlope` | 0.044 | 3e-10 | -0.167 | 2.2e-09 | +0.176 | 3.2e-10 |
| `F0semitoneFrom27.5Hz_sma3nz_stddevFallingSlope` | 0.043 | 4e-10 | -0.151 | 6.8e-08 | +0.184 | 4.5e-11 |
| `loudness_sma3_percentile20.0` | 0.041 | 1.8e-09 | -0.028 | 0.34 | +0.282 | 4.9e-25 |
| `F0semitoneFrom27.5Hz_sma3nz_stddevNorm` | 0.034 | 8.5e-08 | -0.096 | 0.0007 | +0.069 | 0.016 |
| `StddevVoicedSegmentLengthSec` | 0.030 | 1.2e-06 | -0.128 | 5.2e-06 | +0.178 | 1.9e-10 |
| `MeanVoicedSegmentLengthSec` | 0.028 | 3.7e-06 | -0.099 | 0.00044 | +0.200 | 6e-13 |
| `loudnessPeaksPerSec` | 0.027 | 5.2e-06 | -0.035 | 0.22 | +0.067 | 0.018 |
| `MeanUnvoicedSegmentLength` | 0.016 | 0.0027 | +0.044 | 0.13 | -0.061 | 0.032 |
| `StddevUnvoicedSegmentLength` | 0.015 | 0.0043 | +0.024 | 0.41 | -0.086 | 0.0025 |
| `VoicedSegmentsPerSec` | 0.014 | 0.0089 | +0.062 | 0.029 | -0.133 | 2.1e-06 |
| `F0semitoneFrom27.5Hz_sma3nz_stddevRisingSlope` | 0.010 | 0.046 | -0.022 | 0.45 | -0.054 | 0.057 |
| `F0semitoneFrom27.5Hz_sma3nz_meanRisingSlope` | 0.009 | 0.077 | -0.047 | 0.097 | -0.033 | 0.25 |
| `loudness_sma3_stddevNorm` | 0.006 | 0.25 | -0.028 | 0.33 | -0.032 | 0.26 |

## voice quality (10 features)

| feature | ε² | q KW | ρ valence | q | ρ arousal | q |
|---|--:|--:|--:|--:|--:|--:|
| `logRelF0-H1-A3_sma3nz_amean` | 0.118 | 3.1e-30 | +0.050 | 0.078 | -0.333 | 7.5e-35 |
| `HNRdBACF_sma3nz_stddevNorm` | 0.111 | 2.3e-28 | -0.182 | 6.8e-11 | +0.310 | 4.6e-30 |
| `logRelF0-H1-A3_sma3nz_stddevNorm` | 0.097 | 1.2e-24 | -0.116 | 3.5e-05 | +0.313 | 1.3e-30 |
| `jitterLocal_sma3nz_amean` | 0.055 | 4e-13 | -0.196 | 1.8e-12 | +0.130 | 3.3e-06 |
| `shimmerLocaldB_sma3nz_stddevNorm` | 0.041 | 1.3e-09 | +0.110 | 9e-05 | -0.179 | 1.6e-10 |
| `HNRdBACF_sma3nz_amean` | 0.026 | 1.1e-05 | +0.067 | 0.02 | +0.061 | 0.033 |
| `jitterLocal_sma3nz_stddevNorm` | 0.023 | 4.5e-05 | -0.087 | 0.0022 | +0.132 | 2.5e-06 |
| `logRelF0-H1-H2_sma3nz_amean` | 0.021 | 0.00015 | -0.051 | 0.072 | +0.052 | 0.066 |
| `logRelF0-H1-H2_sma3nz_stddevNorm` | 0.010 | 0.04 | +0.060 | 0.035 | -0.029 | 0.32 |
| `shimmerLocaldB_sma3nz_amean` | 0.007 | 0.17 | -0.052 | 0.069 | -0.010 | 0.75 |

## spectral (51 features)

| feature | ε² | q KW | ρ valence | q | ρ arousal | q |
|---|--:|--:|--:|--:|--:|--:|
| `mfcc2V_sma3nz_amean` | 0.161 | 3.1e-42 | +0.104 | 0.00024 | -0.494 | 7.8e-81 |
| `alphaRatioV_sma3nz_amean` | 0.154 | 4e-40 | -0.092 | 0.0011 | +0.451 | 4.8e-66 |
| `mfcc2_sma3_amean` | 0.153 | 5.9e-40 | +0.096 | 0.00071 | -0.470 | 3.1e-72 |
| `spectralFlux_sma3_amean` | 0.148 | 1.5e-38 | -0.203 | 3.3e-13 | +0.524 | 8.8e-93 |
| `spectralFluxV_sma3nz_amean` | 0.147 | 2.5e-38 | -0.198 | 1.1e-12 | +0.524 | 1.3e-92 |
| `mfcc1V_sma3nz_amean` | 0.134 | 1.1e-34 | +0.127 | 6.4e-06 | -0.427 | 1.5e-58 |
| `hammarbergIndexV_sma3nz_amean` | 0.133 | 2.3e-34 | +0.057 | 0.046 | -0.387 | 3e-47 |
| `F3amplitudeLogRelF0_sma3nz_stddevNorm` | 0.123 | 9.9e-32 | +0.144 | 3e-07 | -0.376 | 1.2e-44 |
| `F2amplitudeLogRelF0_sma3nz_stddevNorm` | 0.107 | 2e-27 | +0.143 | 3.1e-07 | -0.362 | 3.5e-41 |
| `mfcc4V_sma3nz_amean` | 0.098 | 9e-25 | +0.156 | 2.7e-08 | -0.372 | 1.6e-43 |
| `F1frequency_sma3nz_amean` | 0.096 | 2.8e-24 | -0.151 | 7.5e-08 | +0.373 | 8e-44 |
| `mfcc4_sma3_amean` | 0.096 | 3.1e-24 | +0.173 | 5.5e-10 | -0.350 | 1.5e-38 |
| `mfcc3_sma3_amean` | 0.087 | 6.4e-22 | +0.151 | 6.4e-08 | -0.352 | 7.1e-39 |
| `mfcc1V_sma3nz_stddevNorm` | 0.085 | 2.7e-21 | -0.170 | 1e-09 | +0.323 | 1e-32 |
| `mfcc3V_sma3nz_amean` | 0.084 | 5e-21 | +0.112 | 6.7e-05 | -0.365 | 6.2e-42 |
| `F3amplitudeLogRelF0_sma3nz_amean` | 0.082 | 2e-20 | -0.144 | 3.1e-07 | +0.299 | 4.1e-28 |
| `F2amplitudeLogRelF0_sma3nz_amean` | 0.076 | 9.6e-19 | -0.141 | 4.9e-07 | +0.293 | 7.4e-27 |
| `mfcc1_sma3_amean` | 0.068 | 1e-16 | +0.093 | 0.00097 | -0.285 | 2.1e-25 |
| `slopeV0-500_sma3nz_amean` | 0.066 | 4.3e-16 | -0.142 | 4.4e-07 | +0.322 | 1.8e-32 |
| `hammarbergIndexV_sma3nz_stddevNorm` | 0.064 | 1.4e-15 | -0.131 | 3.3e-06 | +0.303 | 9.6e-29 |
| `spectralFluxUV_sma3nz_amean` | 0.061 | 7.7e-15 | -0.122 | 1.3e-05 | +0.317 | 2e-31 |
| `slopeV500-1500_sma3nz_amean` | 0.057 | 8.4e-14 | -0.066 | 0.02 | +0.235 | 1.5e-17 |
| `alphaRatioV_sma3nz_stddevNorm` | 0.055 | 3.2e-13 | +0.061 | 0.034 | -0.286 | 1.1e-25 |
| `F1bandwidth_sma3nz_stddevNorm` | 0.053 | 1.2e-12 | -0.147 | 1.6e-07 | +0.273 | 2.3e-23 |
| `alphaRatioUV_sma3nz_amean` | 0.048 | 2.8e-11 | -0.055 | 0.052 | +0.221 | 1.5e-15 |
| `F1amplitudeLogRelF0_sma3nz_stddevNorm` | 0.043 | 4e-10 | +0.106 | 0.00016 | -0.189 | 1.2e-11 |
| `mfcc3V_sma3nz_stddevNorm` | 0.040 | 2.8e-09 | +0.087 | 0.0022 | -0.244 | 8.8e-19 |
| `mfcc4V_sma3nz_stddevNorm` | 0.039 | 6.6e-09 | -0.091 | 0.0014 | +0.220 | 1.9e-15 |
| `hammarbergIndexUV_sma3nz_amean` | 0.036 | 3.4e-08 | -0.005 | 0.86 | -0.120 | 1.8e-05 |
| `mfcc4_sma3_stddevNorm` | 0.035 | 4.2e-08 | -0.056 | 0.049 | +0.142 | 4.1e-07 |
| `F1amplitudeLogRelF0_sma3nz_amean` | 0.033 | 1.9e-07 | -0.096 | 0.00071 | +0.151 | 7.4e-08 |
| `F3frequency_sma3nz_amean` | 0.032 | 3.9e-07 | -0.067 | 0.018 | +0.054 | 0.057 |
| `slopeUV0-500_sma3nz_amean` | 0.029 | 1.4e-06 | -0.107 | 0.00014 | +0.198 | 1.2e-12 |
| `F2frequency_sma3nz_amean` | 0.029 | 1.4e-06 | -0.085 | 0.0027 | +0.174 | 4.5e-10 |
| `slopeV0-500_sma3nz_stddevNorm` | 0.025 | 1.5e-05 | +0.039 | 0.18 | -0.188 | 1.5e-11 |
| `mfcc2_sma3_stddevNorm` | 0.024 | 3.2e-05 | -0.008 | 0.78 | -0.158 | 1.8e-08 |
| `mfcc3_sma3_stddevNorm` | 0.024 | 3.7e-05 | +0.051 | 0.075 | -0.071 | 0.013 |
| `F1frequency_sma3nz_stddevNorm` | 0.023 | 4.1e-05 | -0.077 | 0.0067 | +0.177 | 2.5e-10 |
| `mfcc2V_sma3nz_stddevNorm` | 0.023 | 4.2e-05 | -0.035 | 0.22 | -0.153 | 4.9e-08 |
| `F1bandwidth_sma3nz_amean` | 0.022 | 9e-05 | +0.022 | 0.45 | -0.174 | 4.5e-10 |
| `mfcc1_sma3_stddevNorm` | 0.021 | 0.00019 | -0.071 | 0.013 | +0.075 | 0.0088 |
| `F2frequency_sma3nz_stddevNorm` | 0.018 | 0.0011 | +0.011 | 0.72 | -0.104 | 0.00024 |
| `F2bandwidth_sma3nz_amean` | 0.013 | 0.011 | -0.072 | 0.012 | +0.019 | 0.51 |
| `F3frequency_sma3nz_stddevNorm` | 0.013 | 0.013 | +0.070 | 0.014 | -0.075 | 0.0086 |
| `spectralFlux_sma3_stddevNorm` | 0.012 | 0.016 | -0.002 | 0.96 | -0.031 | 0.28 |
| `slopeUV500-1500_sma3nz_amean` | 0.011 | 0.035 | +0.008 | 0.8 | -0.044 | 0.12 |
| `spectralFluxV_sma3nz_stddevNorm` | 0.010 | 0.038 | -0.016 | 0.59 | +0.018 | 0.54 |
| `slopeV500-1500_sma3nz_stddevNorm` | 0.010 | 0.049 | -0.005 | 0.86 | -0.080 | 0.0052 |
| `F3bandwidth_sma3nz_amean` | 0.010 | 0.054 | +0.004 | 0.89 | -0.056 | 0.049 |
| `F2bandwidth_sma3nz_stddevNorm` | 0.009 | 0.082 | +0.018 | 0.54 | -0.025 | 0.38 |
| `F3bandwidth_sma3nz_stddevNorm` | 0.008 | 0.14 | -0.000 | 0.99 | +0.017 | 0.56 |

## Class medians (normalised z) — H1a / H1c features

| feature | neutral | anger | joy | fear_anxiety | sadness | disgust | surprise |
|---|--:|--:|--:|--:|--:|--:|--:|
| `F0semitoneFrom27.5Hz_sma3nz_amean` | -0.56 | +0.59 | -0.14 | +0.38 | -0.47 | -0.20 | +0.46 |
| `loudness_sma3_amean` | -0.48 | +0.57 | -0.15 | +0.19 | -0.44 | -0.15 | -0.05 |
| `jitterLocal_sma3nz_amean` | -0.25 | +0.21 | -0.32 | -0.04 | -0.20 | -0.02 | -0.30 |
| `jitterLocal_sma3nz_stddevNorm` | -0.24 | -0.05 | -0.17 | -0.13 | -0.21 | +0.27 | -0.30 |
| `shimmerLocaldB_sma3nz_amean` | +0.01 | +0.06 | -0.18 | +0.03 | -0.16 | -0.03 | -0.19 |
| `shimmerLocaldB_sma3nz_stddevNorm` | +0.15 | -0.39 | -0.02 | -0.12 | +0.23 | -0.09 | -0.02 |
| `HNRdBACF_sma3nz_amean` | -0.08 | -0.20 | +0.02 | +0.12 | +0.19 | -0.18 | +0.15 |
| `HNRdBACF_sma3nz_stddevNorm` | -0.33 | +0.33 | -0.10 | -0.18 | -0.45 | +0.12 | -0.02 |
| `logRelF0-H1-H2_sma3nz_amean` | -0.08 | -0.00 | -0.05 | +0.24 | +0.29 | -0.21 | +0.13 |
| `logRelF0-H1-H2_sma3nz_stddevNorm` | -0.04 | -0.04 | -0.04 | -0.04 | -0.04 | -0.04 | -0.04 |
| `logRelF0-H1-A3_sma3nz_amean` | +0.24 | -0.58 | -0.10 | +0.14 | +0.55 | -0.12 | -0.10 |
| `logRelF0-H1-A3_sma3nz_stddevNorm` | -0.33 | +0.15 | -0.15 | -0.25 | -0.40 | -0.17 | -0.26 |
