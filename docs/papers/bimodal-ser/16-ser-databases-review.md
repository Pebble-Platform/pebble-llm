# Paper 16 — Review and Comparative Analysis of Databases for Speech Emotion Recognition

- **Authors:** S. Serrano, O. Serghini, G. Esposito, S. Carbone, C. Mento, A. Floris, S. Porcu, L. Atzori
- **Venue / year:** Data (MDPI), 10(10):164, 2025 (OA)
- **Links:** abs https://doi.org/10.3390/data10100164 · PDF `pdfs/16-ser-databases-review.pdf`
- **Group:** survey / benchmark (datasets)

**Summary:** So sánh 50+ corpora SER (collection method, annotation scheme, demographic diversity, ecological validity).

**Relevance to Pebble:** Reference chọn/đánh giá dataset SER khi mở rộng voice stream.

> Compact entry từ literature sweep (`docs/tasks/bimodal-ser-papers.md`); chưa deep-read.

## Analysis (overlap with Pebble)

**Assembled profile (scored against, from the IDD layers):**
- **Primary (text):** ordinal suicide-risk classification; teacher-LLM silver labels → **gold-holdout** eval; ordinal-aware losses/metrics (QWK/MAE); reproducibility + clinical-data ethics are repo-wide binds (`docs/intent/constraints.md`).
- **Adjacent (voice):** frozen emotion2vec/WavLM backbone + shared trunk, **3 heterogeneous heads** — emotion CE / affect V/A **CCC** / crisis BCE under a **hard recall floor** — balanced by **Kendall uncertainty weighting** (`voice-multimodal.md` → `docs/tasks/voice-mtl-heads.md`).
- **Current voice stage:** heads trained on **RAVDESS with proxy labels** (Russell circumplex V/A; high-distress crisis set). Explicit next action item: **swap proxies for MSP-Podcast (continuous A/V/D) + DAIC (crisis)** for scientifically meaningful numbers.

### Analysis — SER Databases Review (Serrano et al., 2025)
- **Overlap:** 27% (peripheral) — D1=1, D2=1, D3=2, D4=0, D5=0, D6=0, D7=0
  - Compute: (3·1 + 2·1 + 1·2 + 2·0 + 2·0 + 2·0 + 1·0) / 26 × 100 = 7/26 × 100 ≈ 27%.
- **Closest on:** D3 (it *is* a catalogue of emotion corpora, incl. intensity-labelled ones like MCAESD/MEAD — the voice-stream analog of the emotion-transfer corpora dimension) and D1-partial (organizes corpora by **categorical vs dimensional/continuous** label schema, exactly the label duality Pebble's emotion + V/A heads consume).
- **Best point (Dataset to reuse):** The review's comparative framework — Table 2 parameters + the AHP **quality index Q = 0.2615·S′ + 0.0872·E′ + 0.6114·C′ + 0.0400·R′** (speakers, emotions, citations/yr, recency) + the Table 3 usage map — is a ready-made vetting map that shortlists which corpora actually supply **continuous dimensional labels** and appear in robustness studies, with MSP-Podcast/MELD/CMU-MOSEI flagged as the natural/dimensional corpora now displacing acted ones.
  - **How to apply to Pebble:** Use it to justify and scope the voice stream's planned proxy→real swap — confirm **MSP-Podcast (continuous A/V/D)** as the RAVDESS-proxy replacement for the affect (CCC) head, note it lacks a native crisis label (keep DAIC-class for the recall-floor head), then hand both candidates to `find-dataset` for license/gate checks against the repo's ethics bind.
- **Caveats:** Read selectively — intro/methodology/taxonomy/emotion-models (pp.1-6), database-characteristics + acted/elicited/**natural-corpus ethics** (pp.7-9), the tail of the 52-corpus catalogue (pp.44-48), and the full synthesis/discussion/conclusions incl. Q and Table 3 (pp.49-52). The **individual RAVDESS / IEMOCAP / MSP-Podcast** descriptions in the mid-section-6 catalogue were **not** read line-by-line (their coverage is confirmed via Table 3, which lists IEMOCAP=11, RAVDESS=11, MSP-PODCAST=2 occurrences); **DAIC-WOZ** does not appear in Table 3 and may be outside this review's SER-corpus scope (it covers stress/emergency-call corpora generically). Score is structurally low because it is a *dataset review* — orthogonal to Pebble's modeling dimensions (D4-D7 absent by construction); its real value is practical dataset selection, which the overlap % does not capture.
