# Vietnamese Text-Emotion + ASR Building Blocks — Discovery Pass

> **Angle.** Checks the TEXT/ASR side of a planned cascade: acoustic encoder (WavLM-class) + Vietnamese ASR → Vietnamese text-emotion classifier, fused with a crisis-sensitive recall floor. Covers (1) Vietnamese text emotion/mental-health corpora, (2) Vietnamese encoders + ASR, (3) prior bimodal/multimodal work in Vietnamese/SEA, (4) Vietnamese-English code-switching.
>
> **Compiled:** 2026-07-02. Cross-checked against `docs/related-work-survey.md` (English-language mental-health/affect MTL literature) — no overlap; this is a disjoint, language-specific building-blocks pass, not a ranked "closeness to Pebble" survey.

---

## 1. Vietnamese text emotion / sentiment corpora

### UIT-VSMEC — Vietnamese Social Media Emotion Corpus
- **Authors / Year / Venue (or HF org):** Vong Anh Ho, Duong Huynh-Cong Nguyen, Danh Hoang Nguyen, Linh Thi-Van Pham, Duc-Vu Nguyen, Kiet Van Nguyen, Ngan Luu-Thuy Nguyen. 2020, PACLING (also IEEE-indexed as "Exploiting Vietnamese Social Media Characteristics for Textual Emotion Recognition in Vietnamese").
- **Link:** [arXiv:2009.11005](https://arxiv.org/pdf/2009.11005) · [IEEE Xplore](https://ieeexplore.ieee.org/document/9310495/) · request access via kietnv@uit.edu.vn · **Access:** open paper / **gated dataset** (corpus user agreement required, not a direct download).
- **Summary:** 6,927 human-annotated sentences (Facebook social-media comments), 6 basic Ekman-style emotion classes (+ "other"), 82% inter-annotator agreement.
- **Role in the pipeline:** text-emotion training/eval data (small, categorical-only).
- **Why it matters here:** the de-facto standard Vietnamese emotion benchmark; every downstream Vietnamese text-emotion model (ViSoBERT, ViGoEmotions) reports against it — but it is 6-class, single-label, and social-media (not crisis-oriented).

### ViGoEmotions — fine-grained (27-class) Vietnamese emotion benchmark
- **Authors / Year / Venue:** Hung Quang Tran, Nam Tien Pham, Son T. Luu, Kiet Van Nguyen (UIT). **EACL 2026 (main conference, accepted)**; preprint Feb 2026.
- **Link:** [arXiv:2602.08371](https://arxiv.org/abs/2602.08371) · **Access:** open (paper + code/dataset stated as "publicly available" on GitHub; exact license not stated in the fetched abstract — verify before use).
- **Summary:** 20,664 social-media comments (Facebook/Reddit/TikTok/Threads/X/YouTube + re-annotated UIT-VSMEC), labeled with a 27-class GoEmotions-style taxonomy. Best baseline (ViSoBERT) reaches macro-F1 61.50% / weighted-F1 63.26%.
- **Role in the pipeline:** text-emotion training/eval data — **the closest Vietnamese analogue to GoEmotions**, i.e., the natural warm-start corpus for a Vietnamese text-emotion head.
- **Why it matters here:** directly mirrors Pebble's GoEmotions-transfer dimension in Vietnamese; very recent (2026), not yet widely cited — worth flagging to `analysis-paper`/`find-dataset` for a closer look at license terms and download mechanics.

### UIT-VSFC — Vietnamese Students' Feedback Corpus
- **Authors / Year / Venue:** Kiet Van Nguyen, Vu Duc Nguyen, Phu X. V. Nguyen, Tham T. H. Truong, Ngan Luu-Thuy Nguyen. **2018, IEEE NICS / IEEE Xplore**.
- **Link:** [IEEE Xplore](https://ieeexplore.ieee.org/document/8573337/) · [HF: uitnlp/vietnamese_students_feedback](https://huggingface.co/datasets/uitnlp/vietnamese_students_feedback) · [GitHub](https://github.com/kietnv/uit-vsfc) · **Access:** open (HF dataset loads directly), **license listed as "unknown"** on the HF card — flag before any redistribution/commercial use.
- **Summary:** 16,175 sentences (11,426 train / 1,583 val / 3,166 test), 3-class sentiment (pos/neg/neutral) + 4-class topic; 91.2% sentiment IAA; ~88% F1 with a MaxEnt baseline.
- **Role in the pipeline:** text-emotion training/eval data (sentiment-only, domain-mismatched — student feedback, not affect/crisis).
- **Why it matters here:** widely used as a cheap sentiment sanity-check corpus, but not close to the emotional/crisis domain Pebble needs — low priority as a direct source, useful only as an encoder-sanity eval.

### Vietnamese mental-health / crisis text dataset — **not found**
- No dedicated, published Vietnamese-language mental-health, depression, or suicide-risk **text** corpus was found in this pass (2022–2026 window). Searches surfaced only: (a) clinical/epidemiological studies on suicide risk in Vietnam (e.g., Frontiers in Psychiatry 2025, cohort data, not NLP-usable text), (b) a general BERT-BiLSTM depression-detection line of work that is **not Vietnamese-specific**, and (c) UIT's broader social-media benchmark suite (ViHSD hate speech, ViCTSD constructiveness, ViOCD complaint detection — adjacent but not mental-health/crisis labeled).
- **Explicit gap statement:** this is a real hole in the literature, not a search-coverage failure — the UIT NLP group's own dataset page (https://nlp.uit.edu.vn/datasets) lists emotion/sentiment/hate-speech/complaint corpora but no suicide-risk or clinical mental-health text corpus as of this pass.
- **Why it matters here:** confirms that a crisis-recall-floor text head for Vietnamese would need to be trained via **cross-lingual transfer** (e.g., translate Pebble's English silver/gold labels, or use a multilingual LLM teacher directly on Vietnamese text) rather than an existing Vietnamese gold corpus — this is the single biggest blocker for the text branch.

---

## 2. Vietnamese encoders and ASR

### PhoBERT
- **Authors / Year / Venue:** Dat Quoc Nguyen, Anh Tuan Nguyen (VinAI). **Findings of EMNLP 2020.**
- **Link:** [arXiv:2003.00744](https://arxiv.org/abs/2003.00744) · [ACL Anthology](https://aclanthology.org/2020.findings-emnlp.92/) · [HF: vinai/phobert-base-v2](https://huggingface.co/vinai/phobert-base) · **Access:** open, MIT-style research license per VinAI GitHub.
- **Summary:** RoBERTa-style Vietnamese encoder (base ~135M / large ~370M params) pretrained on 20GB word-segmented Vietnamese text; SOTA at release on POS, dependency parsing, NER, NLI.
- **Role in the pipeline:** text encoder candidate.
- **Why it matters here:** the default, best-supported Vietnamese BERT-family backbone; requires VnCoreNLP word-segmentation preprocessing (a Vietnamese-specific step with no English analogue — must be budgeted for in the pipeline).

### ViSoBERT
- **Authors / Year / Venue:** Nam Nguyen et al. (UIT). **EMNLP 2023.**
- **Link:** [arXiv:2310.11166](https://arxiv.org/abs/2310.11166) · [ACL Anthology](https://aclanthology.org/2023.emnlp-main.315/) · [HF: uitnlp/visobert](https://huggingface.co/uitnlp/visobert) · **Access:** open, "research-only" per HF card.
- **Summary:** 97M-param XLM-R-architecture encoder pretrained specifically on Vietnamese **social-media** text (Facebook/TikTok/YouTube); on UIT-VSMEC-style emotion recognition reaches 68.10% accuracy / 65.88% macro-F1, beating PhoBERT; also current best baseline on ViGoEmotions (macro-F1 61.5%).
- **Role in the pipeline:** text encoder candidate — **strongest match for social-media/informal register**, which is closer to how crisis-adjacent speech-derived transcripts will read.
- **Why it matters here:** smaller than PhoBERT-large yet outperforms it on emotion tasks in-domain — a strong first candidate for the text-emotion head encoder.

### CafeBERT
- **Authors / Year / Venue:** Phong Do, Son Tran, Phu Hoang, Kiet Nguyen, Ngan Nguyen (UIT). **Findings of NAACL 2024** (paper: "VLUE: A New Benchmark and Multi-task Knowledge Transfer Learning for Vietnamese NLU").
- **Link:** [arXiv:2403.15882](https://arxiv.org/pdf/2403.15882) · [ACL Anthology](https://aclanthology.org/2024.findings-naacl.15) · [HF: uitnlp/CafeBERT](https://huggingface.co/uitnlp/CafeBERT) · **Access:** open, **Apache 2.0**.
- **Summary:** XLM-RoBERTa-based (~0.6B params) continued-pretrained on a large multi-domain Vietnamese corpus; SOTA on the VLUE benchmark and on ViHOS / NER-COVID19 tasks.
- **Role in the pipeline:** text encoder candidate (largest of the three; best general-domain accuracy but heaviest and least social-media-specific).
- **Why it matters here:** viable higher-capacity alternative if ViSoBERT/PhoBERT underperform on crisis-adjacent registers, at ~5x the parameter cost.

### ViDeBERTa
- **Authors / Year / Venue:** Cong Dao Tran et al. (FPT Software AI Center). **Findings of EACL 2023.**
- **Link:** [arXiv:2301.10439](https://arxiv.org/abs/2301.10439) · [ACL Anthology](https://aclanthology.org/2023.findings-eacl.79/) · [GitHub](https://github.com/HySonLab/ViDeBERTa) · **Access:** open.
- **Summary:** DeBERTa-architecture Vietnamese encoder in xsmall/base/large variants; base is 86M params (~23% of PhoBERT-large) yet matches/beats it on POS/NER/QA.
- **Role in the pipeline:** text encoder candidate — lightweight option if inference-cost matters for the crisis-recall floor stage.
- **Why it matters here:** best parameter-efficiency data point among the four encoders; not yet benchmarked on emotion tasks in the sources found — would need verification before adoption.

### PhoWhisper
- **Authors / Year / Venue:** Thanh-Thien Le, Linh The Nguyen, Dat Quoc Nguyen (VinAI). **ICLR 2024 Tiny Papers track.**
- **Link:** [arXiv:2406.02555](https://arxiv.org/pdf/2406.02555) · [OpenReview](https://openreview.net/pdf?id=x3c3MkJfpG) · [GitHub](https://github.com/VinAIResearch/PhoWhisper) · [HF: vinai/PhoWhisper-large](https://huggingface.co/vinai/PhoWhisper-large) (tiny/base/small/medium/large all published) · **Access:** open, **BSD-3-Clause**.
- **Summary:** Whisper fine-tuned on 844h of diverse-accent Vietnamese speech (incl. 26K speakers across 63 provinces). Verified WER table (self-reported, GitHub README):

  | Model | Params | Common Voice-VI | VIVOS | VLSP-T1 | VLSP-T2 (noisy) |
  |---|---|---|---|---|---|
  | tiny | 39M | 19.05 | 10.41 | 20.74 | 49.85 |
  | base | 74M | 16.19 | 8.46 | 19.70 | 43.01 |
  | small | 244M | 11.08 | 6.33 | 15.93 | 32.96 |
  | medium | 769M | 8.27 | 4.97 | 14.12 | 26.85 |
  | large | 1.55B | 8.14 | 4.67 | 13.75 | 26.68 |
- **Role in the pipeline:** ASR (primary candidate).
- **Why it matters here:** **bounds the text branch's input quality** — even the large model has ~8-14% WER on clean/read benchmarks and ~27% on noisy speech (VLSP-T2), meaning the downstream Vietnamese text-emotion classifier must be robust to substantial transcription noise; this is the single most load-bearing number for the cascade design.

### wav2vec2-base-vietnamese-250h (nguyenvulebinh)
- **Authors / Year / Venue (HF org):** Nguyen Vu Le Binh (independent researcher), 2021–2022.
- **Link:** [HF: nguyenvulebinh/wav2vec2-base-vietnamese-250h](https://huggingface.co/nguyenvulebinh/wav2vec2-base-vietnamese-250h) · **Access:** open, **CC BY-NC 4.0 (non-commercial only)**.
- **Summary:** wav2vec2-base self-supervised-pretrained on 13K hours unlabeled Vietnamese YouTube audio, fine-tuned on 250h labeled VLSP data. WER with 4-gram LM: VIVOS 6.15%, Common Voice-VI 11.52%, VLSP-T1 9.11%.
- **Role in the pipeline:** ASR (alternative to PhoWhisper — self-supervised acoustic-encoder family, closer architecturally to the WavLM-class acoustic branch already planned).
- **Why it matters here:** CC BY-NC license is a hard constraint if the eventual paper/product path is commercial — flag for `find-dataset`/licensing review; also a `wav2vec2-large-vi` variant exists (WER 6.90% VLSP) per search results but was not independently verified here.

### TSPC — Vietnamese-English code-switching ASR
- **Authors / Year / Venue:** Tran Nguyen Anh, Truong Dinh Dung, Vo Van Nam, Minh N. H. Nguyen. **arXiv preprint, submitted Sept 2025 (latest revision March 2026), venue not yet confirmed as peer-reviewed.**
- **Link:** [arXiv:2509.05983](https://arxiv.org/abs/2509.05983) · **Access:** preprint-only.
- **Summary:** Two-stage phoneme-centric architecture using an extended Vietnamese phoneme set as an intermediate representation for VN-EN mixed-lingual ASR; reports **19.06% WER** on code-switched speech with lower training cost than baselines.
- **Role in the pipeline:** ASR (code-switching-specific).
- **Why it matters here:** directly relevant if the target speech population code-switches (common in Vietnamese youth/urban speech) — establishes that code-switched WER (~19%) is markedly worse than monolingual WER (~5-14%), a second, larger noise bound for the text branch in bilingual speakers.

### ViMedCSS — Vietnamese medical code-switching speech dataset
- **Authors / Year / Venue:** Tung X. Nguyen, Nhu Vo, Giang-Son Nguyen, Duy Mai Hoang, Chien Dinh Huynh, Inigo Jauregi Unanue, Massimo Piccardi, Wray Buntine, Dung D. Le. **arXiv preprint, Feb 2026 (rev. June 2026); venue not yet confirmed.**
- **Link:** [arXiv:2602.12911](https://arxiv.org/abs/2602.12911) · **Access:** preprint-only.
- **Summary:** 34 hours / 16,576 utterances of Vietnamese speech with inserted English medical terms, for ASR benchmarking on domain code-switching.
- **Role in the pipeline:** eval corpus (domain-mismatched — medical, not affect/crisis — but methodologically relevant as the only Vietnamese code-switching **dataset** found, vs. TSPC which is architecture-only).
- **Why it matters here:** low direct relevance to Pebble's crisis domain, but confirms code-switching datasets/benchmarks for Vietnamese exist and are being actively published in 2026 — worth monitoring for a crisis-domain analogue.

---

## 3. Prior bimodal / multimodal emotion work — Vietnamese and Southeast-Asian

### Speech-based Multimodal Pipeline for Vietnamese Services Quality Assessment
- **Authors / Year / Venue:** Quang-Anh N.D., Minh-Duc Pham, Thai Kim Dinh (VNU Hanoi). **arXiv preprint, Dec 2024**; venue not confirmed as peer-reviewed.
- **Link:** [arXiv:2412.09829](https://arxiv.org/html/2412.09829v1) · **Access:** preprint-only.
- **Summary:** The closest existing precedent to Pebble's planned cascade design: WhisperX diarization → denoiser → dual stream (PhoWhisper ASR → PhoBERT-CNN hate-speech text classifier; separate Dynamic-Attention-Network SER on raw audio over the VNEMOS 5-emotion set) → rule-based grading module fusing both streams. Reports PhoBERT-CNN accuracy 86.14% on ViHSD (hate speech, not emotion); **no WER or SER accuracy numbers reported** in the fetched text.
- **Role in the pipeline:** prior bimodal system.
- **Why it matters here:** **the strongest directly-comparable prior art found** — a real Vietnamese ASR-plus-text-plus-audio fusion pipeline for a call-center/QA use case. Its fusion is a hand-written rule-based grading module, not a learned/weighted fusion with a recall floor — this is exactly the gap Pebble's crisis-sensitive recall-floor fusion would fill. Flag strongly for `analysis-paper`.

### VNEMOS — Vietnamese Speech Emotion dataset
- **Authors / Year / Venue:** (per IEEE listing) 2024, IEEE conference publication.
- **Link:** [IEEE Xplore](https://ieeexplore.ieee.org/document/10616411/) · [Papers with Code](https://paperswithcode.com/dataset/vnemos) · **Access:** paper open-preprint-adjacent (ResearchGate PDF), dataset access not verified as downloadable.
- **Summary:** 250 annotated audio segments (~30 min total) from movies/live shows, 5 emotions (anger, happiness, sadness, neutral, fear/anxiety), covering North/Central/South Vietnamese accents. Reported 89% accuracy with a Dynamic Attention Network baseline (small test set, likely optimistic).
- **Role in the pipeline:** eval corpus (audio-only, used by the pipeline above for the SER stream).
- **Why it matters here:** extremely small (250 segments) — usable only as a small held-out sanity check, not a training corpus; sets a low ceiling on how much Vietnamese emotion-audio ground truth currently exists publicly.

### OmniMER / IndoMER — Indonesian Multimodal Emotion Recognition
- **Authors / Year / Venue:** (per arXiv listing) 2025/2026, arXiv preprint; venue not confirmed.
- **Link:** [arXiv:2512.19379](https://arxiv.org/html/2512.19379v2) · **Access:** preprint-only.
- **Summary:** First multimodal (text+audio+video) emotion recognition benchmark for **Indonesian** — 1,944 clips, 203 speakers, 7 emotion categories; OmniMER framework adds auxiliary modality-specific tasks (emotion-keyword extraction for text, prosody analysis for audio, facial-expression analysis for video).
- **Role in the pipeline:** prior bimodal system (SEA-region analogue, not Vietnamese).
- **Why it matters here:** demonstrates the same "low-resource SEA language + multimodal fusion + auxiliary per-modality tasks" pattern Pebble would need for Vietnamese — a template for framing/positioning, not directly reusable data.

### SeaLLMs-Audio — Southeast Asian audio-language model
- **Authors / Year / Venue:** Chaoqun Liu, Mahani Aljunied, Guizhen Chen, Hou Pong Chan, Weiwen Xu, Yu Rong, Wenxuan Zhang (DAMO Academy / Alibaba). **arXiv preprint, Nov 2025.**
- **Link:** [arXiv:2511.01670](https://arxiv.org/pdf/2511.01670) · [GitHub](https://github.com/DAMO-NLP-SG/SeaLLMs-Audio) · [HF collection] · **Access:** open weights, **CC BY-NC-SA 4.0** (non-commercial).
- **Summary:** Large audio-language model covering Indonesian, Thai, Vietnamese, English, Chinese; accepts audio-only, text-only, or audio+text input and explicitly lists Speech Emotion Recognition as a supported task. Specific Vietnamese SER numbers were not retrievable from the fetched excerpt.
- **Role in the pipeline:** prior bimodal system / potential off-the-shelf baseline.
- **Why it matters here:** an existing large multimodal (audio+text) model that already claims Vietnamese SER support — a natural zero-shot baseline to compare Pebble's cascade against, though its NC-SA license blocks commercial use and its "LLM does everything" design is architecturally opposite to Pebble's lightweight cascade.

---

## 4. Vietnamese-English code-switching (emotion/ASR context)

No paper was found that studies code-switching **specifically in an emotion-recognition** context for Vietnamese; all code-switching work found (TSPC, ViMedCSS above) is ASR-only, general-domain or medical-domain. This means: **code-switched WER numbers (19% TSPC, monolingual-ASR-trained systems facing VN-EN mixing) are a relevant upper-bound risk for the text branch, but no prior work quantifies how code-switching affects downstream emotion-label accuracy in Vietnamese.** This is an open angle, not a filled one.

---

## Pipeline readiness verdict

| Stage | Status | Basis |
|---|---|---|
| **ASR** | **READY** (with caveats) | PhoWhisper (BSD-3, open, verified WER 4.67–49.85% depending on model size/noise) and wav2vec2-base-vietnamese-250h (CC BY-NC, verified WER 6.15–11.52%) are both real, open, benchmarked systems. Caveat: noisy/code-switched speech pushes WER to 27–49%, which will materially degrade downstream text-emotion accuracy — must be budgeted for, not assumed away. |
| **Text-emotion data** | **PARTIAL** | UIT-VSMEC (gated, 6-class, small) and ViGoEmotions (open-ish, 27-class GoEmotions-style, 20.6K, very recent EACL 2026) exist and are usable for warm-start/transfer, mirroring Pebble's GoEmotions dimension. But **no Vietnamese mental-health/crisis-labeled text corpus exists** — the crisis-recall-floor head has no native Vietnamese gold data and must rely on cross-lingual transfer or new annotation. |
| **Text encoder** | **READY** | Four real, open, verifiable Vietnamese encoders (PhoBERT, ViSoBERT, CafeBERT, ViDeBERTa) span 86M–600M params with license terms confirmed (MIT-style / research-only / Apache-2.0 / open respectively); ViSoBERT is the strongest in-domain match for social-media/informal-register emotion text. |
| **Prior bimodal VN work** | **PARTIAL** | One directly comparable prior system exists (arXiv:2412.09829, VNU Hanoi) combining PhoWhisper + PhoBERT-CNN + audio SER with rule-based fusion — a real precedent, but preprint-only, unpublished-venue, no learned/recall-constrained fusion, and its SER corpus (VNEMOS, 250 clips) is too small to be a training set. No peer-reviewed Vietnamese bimodal emotion paper was found. |

**Overall:** the ASR and text-encoder legs are solid and verifiable; the two blockers are (1) **no Vietnamese crisis/mental-health text corpus** exists to train or validate the safety-recall head in-language, and (2) the only prior bimodal precedent is an unpublished preprint with a small, non-crisis SER dataset and hand-tuned (not learned) fusion — meaning the recall-floor fusion mechanism itself would be a genuine contribution, not a reproduction.
