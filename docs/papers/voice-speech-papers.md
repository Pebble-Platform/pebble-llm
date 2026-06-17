# Voice / Speech papers — tone, timbre & paralinguistics (thesis: voice-message modality)

> Discovered 2026-06-17. Scope (per thesis): Speech Emotion Recognition + Paralinguistics/prosody +
> tonal-language tone + paralinguistic mental-health markers. Language focus: English speech.
> PDFs live in `docs/papers/pdfs/NN-*.pdf`. Datasets (gitignored) under `data/external/`.
> 18 papers (#24–#41). 17 PDFs downloaded; #29 openSMILE = manual download (host unreachable from CI).
>
> **Deep reads:** every paper has a full-PDF deep-read in two languages — EN at `docs/papers/NN-name.md`
> and VI at `docs/papers/NN-name.vi.md` (same `name` as the PDF). Headline numbers per paper below.

## A. Speech Emotion Recognition (SER)

| # | Paper | Venue / Year | PDF | Dataset(s) |
|---|-------|--------------|-----|------------|
| 24 | MMER: Multimodal Multi-task Learning for SER — Ghosh, Tyagi, Ramaneswaran et al. | Interspeech 2023 | `pdfs/24-mmer-multimodal-mtl-ser.pdf` · [arXiv](https://arxiv.org/abs/2203.16794) | IEMOCAP (gated) |
| 25 | emotion2vec: Self-Supervised Pre-Training for Speech Emotion Representation — Ma, Zheng, Ye et al. | ACL Findings 2024 | `pdfs/25-emotion2vec.pdf` · [ACL](https://aclanthology.org/2024.findings-acl.931/) | IEMOCAP + ESD/MELD/MOSI (mixed) |
| 26 | WavLM: Large-Scale SSL Pre-Training for Full-Stack Speech Processing — Chen, Wang, Chen et al. | IEEE JSTSP 2022 | `pdfs/26-wavlm.pdf` · [arXiv](https://arxiv.org/abs/2110.13900) | VoxPopuli/LibriLight/GigaSpeech (open) |
| 27 | Speech Emotion Recognition using Self-Supervised Features — Morais, Hoory, Zhu et al. | ICASSP 2022 | `pdfs/27-morais-ssl-ser.pdf` · [arXiv](https://arxiv.org/abs/2202.03896) | IEMOCAP (gated) |
| 28 | Survey of Deep Representation Learning for SER — Latif, Rana, Khalifa et al. (incl. Schuller) | IEEE T-AFFC 2023 | `pdfs/28-latif-ser-survey.pdf` · [ACM/DOI](https://dl.acm.org/doi/10.1109/TAFFC.2021.3114365) | survey (IEMOCAP, MSP, RAVDESS, …) |

## B. Paralinguistics & prosody (pitch / timbre / voice quality)

| # | Paper | Venue / Year | PDF | Dataset(s) |
|---|-------|--------------|-----|------------|
| 29 | openSMILE: Munich Versatile & Fast Open-Source Audio Feature Extractor — Eyben, Wöllmer, Schuller | ACM MM 2010 | **manual** · [Augsburg PDF](https://opus.bibliothek.uni-augsburg.de/opus4/files/76475/76475.pdf) · [ACM](https://dl.acm.org/doi/10.1145/1873951.1874246) | FAU-AIBO (gated) |
| 30 | GeMAPS/eGeMAPS for Voice Research & Affective Computing — Eyben, Scherer, Schuller et al. | IEEE T-AFFC 2016 | `pdfs/30-egemaps.pdf` · [DOI](https://doi.org/10.1109/TAFFC.2015.2457417) | AVEC/SAVEE/Belfast/FAU-AIBO |
| 31 | Affective & Behavioural Computing: First ComParE Challenge — Schuller, Weninger, Zhang et al. | Computer Speech & Language 2019 | `pdfs/31-compare-csl2019.pdf` · [Elsevier](https://www.sciencedirect.com/science/article/abs/pii/S0885230816303928) | FAU-AIBO/SSPNet/AVEC2013 |
| 32 | The INTERSPEECH 2009 Emotion Challenge — Schuller, Steidl, Batliner | Interspeech 2009 | `pdfs/32-interspeech2009-emotion-challenge.pdf` · [ISCA](https://www.isca-archive.org/interspeech_2009/schuller09_interspeech.html) | FAU-AIBO (gated) |

## C. Lexical tone in tonal languages

| # | Paper | Venue / Year | PDF | Dataset(s) |
|---|-------|--------------|-----|------------|
| 33 | ToneNet: A CNN Model of Tone Classification of Mandarin — Gao, Sun, Yang | Interspeech 2019 | `pdfs/33-tonenet.pdf` · [ISCA](https://www.isca-archive.org/interspeech_2019/gao19c_interspeech.html) | SCSC (institutional) |
| 34 | Tone Recognition Using Lifters and CTC — Lugosch, Tomar | Interspeech 2018 | `pdfs/34-lugosch-tone-ctc.pdf` · [arXiv](https://arxiv.org/abs/1807.02465) | AISHELL-1 (open, large) |
| 35 | Encoding of Lexical Tone in Self-Supervised Models — Shen, Watkins, Alishahi et al. | NAACL 2024 | `pdfs/35-shen-lexical-tone-ssl.pdf` · [ACL](https://aclanthology.org/2024.naacl-long.239/) | THCHS-30, **VIVOS (vi)** |
| 36 | J-ToneNet: Transformer Encoding for Tone Classification via F0 — Liu, Lu | Interspeech 2023 | `pdfs/36-j-tonenet.pdf` · [ISCA](https://www.isca-archive.org/interspeech_2023/liu23e_interspeech.html) | Mandarin continuous (see PDF) |

## D. Paralinguistic mental-health markers in voice

| # | Paper | Venue / Year | PDF | Dataset(s) |
|---|-------|--------------|-----|------------|
| 37 | AVEC 2016 — Depression, Mood & Emotion Challenge — Valstar, Gratch, Schuller et al. | AVEC@ACM-MM 2016 | `pdfs/37-avec2016.pdf` · [arXiv](https://arxiv.org/abs/1605.01600) | DAIC-WOZ (gated) |
| 38 | AVEC 2019 — Detecting Depression with AI, Cross-Cultural Affect — Ringeval, Schuller, Valstar et al. | AVEC@ACM-MM 2019 | `pdfs/38-avec2019.pdf` · [arXiv](https://arxiv.org/abs/1907.11510) | E-DAIC (gated) |
| 39 | Self-Supervised Representations in Speech-Based Depression Detection — Wu, Zhang, Woodland | ICASSP 2023 | `pdfs/39-wu-ssl-depression.pdf` · [arXiv](https://arxiv.org/abs/2305.12263) | DAIC-WOZ (gated) |
| 40 | Improving Speech Depression Detection w/ wav2vec 2.0 Transfer Learning — Zhang, Zhang, Chen | Scientific Reports 2024 | `pdfs/40-zhang-wav2vec2-depression.pdf` · [Nature](https://www.nature.com/articles/s41598-024-60278-1) | DAIC-WOZ + CMDC (gated) |
| 41 | SER in Mental Health: Systematic Review of Voice-Based Applications — Jordan, Terrisse, Lucarini et al. | JMIR Mental Health 2025 | `pdfs/41-jordan-ser-mentalhealth-review.pdf` · [JMIR](https://mental.jmir.org/2025/1/e74260) | review (DAIC-WOZ, RAVDESS, …) |

---

## Datasets — local status (`data/external/`)

**Downloaded (open):**

| Dataset | Path | #wav | Size | License | Used by |
|---------|------|------|------|---------|---------|
| RAVDESS (speech) | `ravdess/` | 1,440 | 766 MB | CC-BY-NC-SA (no deploy) | survey, mental-health review |
| TESS | `tess/` | 2,800 | 489 MB | CC-BY-NC-ND (no deploy) | SER benchmark |
| EmoDB (Berlin) | `emodb/` | 535 | 85 MB | **CC-BY-4.0 (deploy OK)** | ComParE/eGeMAPS lineage |
| VIVOS (Vietnamese) | `vivos/` | 12,420 | 1.4 GB | CC-BY-NC-SA (no deploy) | #35 Shen NAACL 2024 |

**Gated — request access (see `ACCESS.md` in each folder):**

| Dataset | Folder | Gate | Request URL | Used by |
|---------|--------|------|-------------|---------|
| IEMOCAP | `iemocap/` | signed release form | https://sail.usc.edu/iemocap/ | #24 #25 #27 #28 |
| DAIC-WOZ / E-DAIC | `daic-woz/` | online app + DUA | https://dcapswoz.ict.usc.edu/ | #37 #38 #39 #40 |
| FAU-AIBO | `fau-aibo/` | license agreement (email FAU) | https://www5.cs.fau.de/.../fau-aibo-emotion-corpus/ | #29 #31 #32 |

**Too large for auto-download (open; see `SOURCE.md`):**

| Dataset | Folder | Size | License | Link | Used by |
|---------|--------|------|---------|------|---------|
| THCHS-30 | `thchs30/` | 6.4 GB | Apache-2.0 | https://www.openslr.org/18/ | #35 |
| AISHELL-1 | `aishell1/` | 15 GB | Apache-2.0 | https://www.openslr.org/33/ | #34 #35 |
| CREMA-D | `crema-d/` | 7.55 GB (git-lfs) | ODbL | https://github.com/CheyneyComputerScience/CREMA-D | SER benchmark |

> ⚠️ License note: only **EmoDB (CC-BY-4.0)** permits shipping a model commercially. RAVDESS / TESS / VIVOS
> carry NC clauses → research/ablation only. IEMOCAP / DAIC-WOZ / FAU-AIBO are academic-only.
