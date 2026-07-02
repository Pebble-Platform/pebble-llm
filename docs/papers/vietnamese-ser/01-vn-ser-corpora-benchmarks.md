# Vietnamese Speech-Emotion Corpora & Benchmarks — Discovery Pass

> **Purpose.** GO/NO-GO data-availability check for a possible 3rd-paper angle: bimodal (audio + ASR-transcript) speech emotion recognition for Vietnamese with a crisis-sensitive recall-floor head. This is a **dataset discovery** pass, not a related-work-closeness ranking — see `docs/related-work-survey.md` for the Pebble text-domain related work (not duplicated here).
>
> **Compiled:** 2026-07-02
> **Scope:** Vietnamese speech-emotion corpora/benchmarks only. Text-only Vietnamese emotion corpora (e.g. UIT-VSMEC, ViGoEmotions) are noted but out of scope and not detailed.

---

### VLSP 2025 ASR/SER — Vietnamese Speech Recognition + Speech Emotion Recognition shared task
- **Authors / Year / Venue:** VLSP (Association for Vietnamese Language and Speech Processing) organizers; shared-task overview + multiple participant-system papers. **11th VLSP Workshop, 2025** (co-located, ACL Anthology `2025.vlsp-1` volume).
- **Link:** [ACL Anthology 2025.vlsp-1.1](https://aclanthology.org/2025.vlsp-1.1/) (technical analysis paper) · [official task page](https://vlsp.org.vn/vlsp2025/eval/asr-ser) (returned HTTP 503 on every fetch attempt this session — could not independently verify registration/license terms) · **Access:** gated (presumed; VLSP challenges are historically registration-gated to participating teams, data usually released only during the active challenge window) · **unverified this session**
- **Summary:** Joint ASR+SER challenge; SER sub-task uses the **VLSP 2023 speech corpus, ~56 hours** of Vietnamese speech drawn from **diverse spontaneous media (TV series, entertainment videos, social-media clips)**. Labels are a coarse **binary scheme: "neutral" vs. "negative"** (per multiple participant papers, e.g. [2025.vlsp-1.2](https://aclanthology.org/2025.vlsp-1.2.pdf), [2025.vlsp-1.5](https://aclanthology.org/2025.vlsp-1.5.pdf)). Content is **spontaneous/found speech**, not scripted.
- **License / obtainability verdict:** Could not confirm license or post-challenge public release. VLSP corpora are typically distributed to registered participants only, sometimes released later on request to the organizers — **not confirmed as freely downloadable**. Official site was down (503) during this pass; needs a follow-up fetch or direct email to organizers before relying on it.
- **Why it matters here:** Largest known labeled Vietnamese SER corpus (56h) with spontaneous/free content — closest in spirit to a crisis-relevant "distress vs. neutral" framing, but access is the open question and the label scheme (binary) would need re-annotation for finer affect granularity.

### ViSEC — Vietnamese Speech Emotion Corpus (Pitch-Fusion paper)
- **Authors / Year / Venue:** P. V. Thanh, N. T. T. Huyen, P. N. Quan, N. T. T. Trang — *"A Robust Pitch-Fusion Model for Speech Emotion Recognition in Tonal Languages"*, **ICASSP 2024**.
- **Link:** [ResearchGate abstract](https://www.researchgate.net/publication/379817620_A_Robust_Pitch-Fusion_Model_for_Speech_Emotion_Recognition_in_Tonal_Languages) · [GitHub — thanhpv2102/ViSEC](https://github.com/thanhpv2102/ViSEC) (dataset download via linked Google Drive) · **Access:** open (direct Google Drive download, no registration observed) but **license unclear** (GitHub repo license field is `null` / unspecified — verified via GitHub API)
- **Summary:** **147 speakers, 5,280 utterances, 3.18 hours**, sourced from **YouTube (spontaneous/found speech, not scripted)**, covering all **3 Vietnamese dialect regions**. 4-class emotion scheme (**neutral, happy, sad, angry**) plus auxiliary gender/dialect/speaker-ID labels. 16kHz WAV + `data.csv` labels.
- **License / obtainability verdict:** File is directly downloadable today (verified redirect via GitHub → Google Drive), but the repository carries **no explicit license** — redistribution/commercial-use rights are legally ambiguous despite public accessibility. Treat as "obtainable but re-license-risk before any redistribution or product use"; fine for research replication.
- **Why it matters here:** Best-fit candidate found: multi-speaker, spontaneous, multi-region, openly downloadable today. Small (3.18h) — likely needs augmentation with VLSP or VNEMOS for a serious training set, and is 4-class categorical only (no ordinal/crisis-relevant severity dimension).

### VNEMOS — Vietnamese Speech Emotion dataset (movies + live shows)
- **Authors / Year / Venue:** Quang-Anh N.D. et al. — *"VNEMOS: Vietnamese Speech Emotion Inference Using Deep Neural Networks"*, **IEEE conference, 2024**.
- **Link:** [IEEE Xplore 10616411](https://ieeexplore.ieee.org/document/10616411/) (paywalled full text) · [ResearchGate](https://www.researchgate.net/publication/382622286_VNEMOS_Vietnamese_Speech_Emotion_Inference_Using_Deep_Neural_Networks) (403 on fetch this session) · **dataset "detail" link `bit.ly/VNEMOS`** → resolves to a **Google Sheet** (verified by following the redirect), not an audio download.
- **Summary:** **250 emotional segments** from **27 movies/movie-series/live shows**, **~26–30 minutes total**, mixed **acted + natural** speech (natural: live-TV/conversation clips; acted: movie/drama clips), 3 dialect regions, 5 emotion classes (**anger, happiness, sadness, neutral, anxiety**), gender + 3 age-bracket metadata.
- **License / obtainability verdict:** **The publicly reachable "dataset" link is only a metadata/statistics spreadsheet (counts by movie/emotion/gender/age) — the actual audio/video clips are NOT included or linked from it.** No license, no raw-audio download route found. Effectively **not obtainable** without directly contacting the authors. Also very small (~30 min) even if obtained.
- **Why it matters here:** Frequently cited baseline in follow-on Vietnamese SER papers (used by the depression-diagnosis paper below and by EmoFedProto), but **fails the "obtainable" bar** on the evidence found this session — flag as NO-GO for direct use, cite only as a benchmark number, not a data source.

### VLSP 2022/2023 Emotional Speech Synthesis (TTS) — VLSP-EMO / VLSP-NEU
- **Authors / Year / Venue:** VLSP organizers, shared-task track. **VLSP 2022** ([task page](https://vlsp.org.vn/vlsp2022/eval/tts), returned 503 this session) and continued as **VLSP 2023 Challenge on Emotional Speech Synthesis** ([task page](https://vlsp.org.vn/vlsp2023/eval/ess), not independently fetched — flag unverified).
- **Link:** [vlsp.org.vn/vlsp2022/eval/tts](https://vlsp.org.vn/vlsp2022/eval/tts) · **Access:** gated (presumed, standard VLSP registration) — **unverified this session** (site unreachable)
- **Summary:** Two sub-corpora: **VLSP-EMO** (~5 hours, single speaker, sourced from film/interview clips, 4 emotion labels: neutral/sad/happy/angry) used to train an emotional-TTS voice; **VLSP-NEU** (~4 neutral-only hours, a second speaker) used for the cross-speaker emotion-transfer sub-task. This is a **TTS-oriented corpus: single-speaker-per-emotion-set, curated/selected clips** — closer to "read/curated" than genuinely spontaneous multi-speaker conversational speech, and **not naturally content-free** (built for voice cloning, not classification benchmarking).
- **License / obtainability verdict:** Not independently confirmed (site down); historically VLSP TTS data is participant-gated during the challenge, sometimes released afterward for research. Needs a direct follow-up.
- **Why it matters here:** Wrong shape for a classification/crisis-detection use case (single-speaker TTS-oriented, tiny speaker diversity) even if obtainable — low priority for the SER angle, but flags that VLSP has run *two* separate emotion-speech tracks (TTS 2022/2023 and ASR/SER 2025), suggesting the community and possibly reusable infrastructure exists.

### "Human-Guided Reasoning with LLMs for Vietnamese Speech Emotion Recognition" — new 3-class corpus (movies/entertainment/interviews)
- **Authors / Year / Venue:** Truc Nguyen, Then Tran, Binh Truong, Phuoc Nguyen T. H. — arXiv preprint, **April 2026** (not yet peer-reviewed).
- **Link:** [arXiv:2604.01711](https://arxiv.org/abs/2604.01711) · **Access:** preprint-only; **dataset itself has no data-availability statement, no download link, no GitHub repo found** — treat as **not released / private to authors**.
- **Summary:** **2,764 segments, 4.12 hours total**, from **28 sources** (5 movies, 10 entertainment programs, 13 interview programs) spanning **3 dialect regions**, 3-annotator labeling with **Fleiss' κ = 0.857** (high agreement). **3-class scheme: angry (34.1%), calm (35.5%), panic (30.5%)** — notably a **panic/distress-adjacent label**, closest of anything found to a crisis-relevant category. Content appears to be **found/naturalistic media**, not scripted.
- **License / obtainability verdict:** Not obtainable — no public release found. Flag as a **watch item**: if the authors release data on publication, the 3-class scheme (calm/angry/**panic**) is unusually well-matched to a crisis-sensitivity framing and worth revisiting.
- **Why it matters here:** Directionally the best-matched *label scheme* (panic-adjacent class) of everything found, but currently a dead end on data access.

### VAIS-1000 — Vietnamese Speech Synthesis Corpus (neutral, not emotion-labeled)
- **Authors / Year / Venue:** VAIS / IEEE DataPort listing (exact paper authorship not resolved this session).
- **Link:** [IEEE DataPort](https://ieee-dataport.org/documents/vais-1000-vietnamese-speech-synthesis-corpus) · **Access:** unknown (IEEE DataPort typically requires a free account; not independently confirmed)
- **Summary:** 1,000 studio-quality single-speaker (Northern accent) read utterances with transcripts, built for **TTS**, **no emotion labels**.
- **License / obtainability verdict:** Not applicable to SER — no emotion annotation at all.
- **Why it matters here:** Ruled out; listed only to close the search space (confirms this is a general-TTS, not emotion, corpus).

### Papers-with-Code / HuggingFace check
- **Papers-with-Code "VNEMOS" dataset page** ([paperswithcode.com/dataset/vnemos](https://paperswithcode.com/dataset/vnemos)) — the URL **redirected to `huggingface.co/papers/trending`** on fetch, i.e. **dead/retired listing** (Papers-with-Code shut down its dataset pages and now forwards to HF). No independent PwC entry found.
- **HuggingFace Datasets search** — no Vietnamese-specific speech-emotion dataset found. Only generic English SER datasets (`UniDataPro/speech-emotion-recognition`, `TrainingDataPro/speech-emotion-recognition-dataset`) and an unrelated Vietnamese ASR set (`thanhnew2001/VietSuperSpeech`, 52,023 utterances, no emotion labels). **Verdict: no usable HF entry.**

### (Out of scope, noted only) UIT-VSMEC / ViGoEmotions — text-only Vietnamese emotion corpora
- **Link:** [UIT NLP Group datasets page](https://nlp.uit.edu.vn/datasets) confirms **no audio-based emotion dataset** is hosted by UIT; UIT-VSMEC (6,927 sentences, 6-class) and ViGoEmotions ([arXiv:2602.08371](https://arxiv.org/abs/2602.08371), 20,664 comments) are **text-only** social-media corpora. Included here only to close the "did UIT ever release a speech corpus" question — **they did not**. Not detailed further; out of scope for the audio angle.

---

## GO / NO-GO verdict

**Conditional GO, with a real access risk on the largest/best corpus.**

- **(a) Obtainable today, no gate:** **ViSEC** (open Google Drive download, verified working redirect) is the only corpus in this search that is unambiguously downloadable right now without registration or waiting on organizers.
- **(b) Free/spontaneous content:** ViSEC (YouTube-sourced), the VLSP 2025 ASR/SER corpus (TV/entertainment/social media), and the unreleased 2026 panic/calm/angry corpus are all naturalistic/spontaneous. VLSP-EMO/VNEMOS are TTS-oriented or acted+natural mixes — weaker fit. VAIS-1000 is fully scripted/read — excluded.
- **(c) Usable license:** **No corpus in this search has a clearly stated open license.** ViSEC has *no* license field (ambiguous, not confirmed-open); VLSP corpora are presumptively gated/participant-only (site unreachable this session, unverified); VNEMOS's public link is a stats sheet, not the data.

**Bottom line:** There is enough *volume* in principle (VLSP's 56h corpus) and enough *open access* in a smaller corpus (ViSEC, 3.18h) to justify **not killing the angle outright**, but neither is a clean "obtainable + licensed + sizeable" triple-check. Recommended next step before committing to this as paper #3: (1) re-fetch `vlsp.org.vn` when it's back up (503 all session — transient host issue, not necessarily a real gate) and directly check the VLSP 2023/2025 SER data-release terms; (2) email the ViSEC/VNEMOS/2026-panic-corpus authors to clarify license and ask for the VNEMOS raw clips; (3) treat ViSEC as the safe fallback minimum-viable corpus (open, small, spontaneous, multi-speaker) to prototype on while waiting on VLSP access.

---

## Sources
- [VLSP 2025 ASR/SER — Technical Analysis (ACL Anthology 2025.vlsp-1.1)](https://aclanthology.org/2025.vlsp-1.1/)
- [Speech recognition and SER approach for VLSP 2025 (2025.vlsp-1.2)](https://aclanthology.org/2025.vlsp-1.2.pdf)
- [VLSP 2025 ASR-SER: Data Exploration to Model Training (2025.vlsp-1.5)](https://aclanthology.org/2025.vlsp-1.5.pdf)
- [VLSP 2025 ASR/SER official task page](https://vlsp.org.vn/vlsp2025/eval/asr-ser) (503 — unverified)
- [VLSP 2022 TTS: Emotional speech synthesis](https://vlsp.org.vn/vlsp2022/eval/tts) (503 — unverified)
- [VLSP 2023 Challenge on Emotional Speech Synthesis](https://vlsp.org.vn/vlsp2023/eval/ess) (not fetched — unverified)
- [ViSEC / Pitch-Fusion Model, ICASSP 2024 (ResearchGate)](https://www.researchgate.net/publication/379817620_A_Robust_Pitch-Fusion_Model_for_Speech_Emotion_Recognition_in_Tonal_Languages)
- [ViSEC GitHub repo (thanhpv2102/ViSEC)](https://github.com/thanhpv2102/ViSEC)
- [VNEMOS, IEEE Xplore 10616411](https://ieeexplore.ieee.org/document/10616411/)
- [VNEMOS metadata sheet (via bit.ly/VNEMOS redirect)](https://docs.google.com/spreadsheets/d/1MhAdICuP7eQ1RVSXu_PJSnpI-Mp5bnlNuqqfp38eSHw/edit?usp=sharing)
- [Human-Guided Reasoning with LLMs for Vietnamese SER, arXiv:2604.01711](https://arxiv.org/abs/2604.01711)
- [EmoFedProto (EAI Endorsed Trans. AI & Robotics, 2026)](https://publications.eai.eu/index.php/airo/article/view/11595)
- [Emotional Vietnamese Speech-Based Depression Diagnosis, arXiv:2412.08683](https://arxiv.org/abs/2412.08683)
- [ViP-VL, arXiv:2606.10360](https://arxiv.org/pdf/2606.10360)
- [VAIS-1000, IEEE DataPort](https://ieee-dataport.org/documents/vais-1000-vietnamese-speech-synthesis-corpus)
- [UIT NLP Group datasets page](https://nlp.uit.edu.vn/datasets) (confirms no UIT speech-emotion corpus)
- [Papers-with-Code VNEMOS listing → redirects to HF trending (dead)](https://paperswithcode.com/dataset/vnemos)
