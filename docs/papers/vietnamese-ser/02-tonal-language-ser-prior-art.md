# Tonal-Language SER Prior Art — Novelty Check for "Vietnamese Tone × Emotion, Bimodal SER"

> **Purpose.** Single-angle discovery pass for a candidate paper: *bimodal (audio+text) SER for
> Vietnamese, motivated by the claim that lexical tone lexically constrains F0/pitch — the primary
> emotion cue in non-tonal SER — making the text/semantic branch relatively more informative.*
> Goal: find out whether "tone-aware bimodal SER" or "emotion-vs-lexical-tone disentanglement" has
> already been published for Vietnamese (or Mandarin/Cantonese/Thai as the nearest analogues), and
> how crowded the niche is.
>
> **Compiled:** 2026-07-02. **Already known to the repo (not re-analyzed here, only flagged):**
> `docs/papers/voice/35-shen-lexical-tone-ssl.md` — Shen et al., NAACL 2024, "Encoding of Lexical
> Tone in Self-Supervised Models of Spoken Language" — probes whether frozen `wav2vec2`-class SSL
> encoders linearly encode lexical tone, **including Vietnamese (VIVOS) vs Mandarin (THCHS-30)**,
> and finds **Vietnamese tone is harder to decode and relies more on phonation/voice-quality cues
> than the F0-contour/height cues that dominate Mandarin tone**, with no Mandarin→Vietnamese
> transfer. This is the single most load-bearing prior-art paper for the new angle's phonetic
> premise — see "Novelty verdict" below for how it bears on it. It is **not** an SER paper (no
> emotion labels) and **not** bimodal, so it does not occupy the niche itself.

---

## A. Phonetics / psycholinguistics: does emotional prosody interact with lexical tone?

### Emotional tones of voice affect the acoustics and perception of Mandarin tones — the core empirical premise
- **Authors / Year / Venue:** Chang et al. (Yueh-Chin Chang and colleagues). 2023. *PLOS ONE* 18(4):e0283635.
- **Link:** [PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0283635) · [PMC10075469](https://pmc.ncbi.nlm.nih.gov/articles/PMC10075469/) · **Access:** open
- **Summary:** Acoustic-analysis + perception-experiment study (actors recording emotion-inflected Mandarin syllables, Praat measurement, listener identification task). Finds anger raises F0/amplitude, sadness lengthens duration, and — the key asymmetry — **emotion affects tone identification more than tone affects emotion identification**.
- **Novelty impact:** Establishes the phonetic premise (tone and emotional prosody compete for the same F0 dimension) empirically for Mandarin, but is **not a modeling/SER paper** — no classifier, no Vietnamese, no bimodal architecture. Leaves the computational niche open; **directly citable as the motivating phenomenon**.
- **Why it matters here:** This is the strongest existing empirical support for the paper's scientific hook — cite it as the reason F0 is a lexically-loaded (hence noisier) channel in tonal-language SER.

### The perception of emotional prosody in Mandarin Chinese words and sentences
- **Authors / Year / Venue:** Cheng Xiao, Jiang Liu. Online 2024 (print 2026), *Second Language Research* 42(1).
- **Link:** [SAGE DOI 10.1177/02676583241286748](https://journals.sagepub.com/doi/10.1177/02676583241286748) · **Access:** paywalled (abstract only retrieved; numbers not retrievable)
- **Summary:** Emotion-judgment experiments with native Mandarin speakers, L2 Chinese learners, and native English speakers, testing whether lexical tone interferes with perceived emotional prosody across word/sentence length.
- **Novelty impact:** Reinforces the phonetic premise via an L1-vs-L2 lens; still a **behavioral perception study, not a model**, and Mandarin not Vietnamese. Narrows the "does this phenomenon exist" question further but leaves the modeling niche untouched.
- **Why it matters here:** Useful as a second, independent citation for "lexical tone interferes with emotional-prosody perception," and its L2-learner condition is a possible framing device (non-tonal-language listeners process the two channels differently) — relevant to justifying a text branch.

### Evaluating the Relative Perceptual Salience of Linguistic and Emotional Prosody in Quiet and Noisy Contexts
- **Authors / Year / Venue:** Minyue Zhang, Hui Zhang, Enze Tang, Hongwei Ding, Yang Zhang. 2023. *Behavioral Sciences* (Basel), MDPI.
- **Link:** [PMC10603920](https://pmc.ncbi.nlm.nih.gov/articles/PMC10603920/) · **Access:** open
- **Summary:** Native Mandarin listeners identify lexical tones faster/more accurately than vocal emotions under multi-talker babble noise — i.e., under signal degradation, the **linguistic (tone) channel is more robust than the emotional-prosody channel**.
- **Novelty impact:** A third phonetics-only data point; strengthens (does not contest) the hook's premise that tone and emotion compete for F0 and that tone "wins" perceptually for native listeners. No modeling contribution.
- **Why it matters here:** Supports a specific framing claim — "under noisy/degraded audio, tone information may dominate over emotional F0 cues, further motivating a text branch" — with a citable, open-access source.

---

## B. Tonal-language SER / acoustic-feature work (Cantonese, Thai) — adjacent but not tone-disentangling

### Exploring the Contributions of Various Acoustic Features in Cantonese Vocal Emotions
- **Authors / Year / Venue:** (not confirmed from abstract; author list unavailable). 2025. *Journal of Speech, Language, and Hearing Research* (ASHA).
- **Link:** [DOI 10.1044/2025_JSLHR-24-00677](https://pubs.asha.org/doi/10.1044/2025_JSLHR-24-00677) · **Access:** paywalled (HTTP 403 on fetch; numbers not retrievable — title/venue only confirmed via search index)
- **Summary (from indexed title/abstract snippet only):** Analyzes which acoustic features (pitch, intensity, voice quality, etc.) contribute to vocal-emotion recognition in **Cantonese**, a tonal language with a large tone inventory (6–9 tones depending on analysis).
- **Novelty impact:** The closest **acoustic-feature study on a tonal language's vocal emotion** found in this pass, but it is Cantonese (not Vietnamese), appears to be a phonetics/perception study (not a bimodal deep-learning SER system), and full text is inaccessible in this pass.
- **Why it matters here:** Flag for `find-dataset`/`analysis-paper` follow-up if institutional access is available — likely the nearest tonal-language analogue to the Vietnamese hook outside Mandarin.

### Cross-lingual speech emotion recognition using English and Mandarin on Thai data
- **Authors / Year / Venue:** Authors not fully confirmed from available metadata (EasyChair preprint PDF unparseable in this pass). ICAS2024 (International Conference on Applied Statistics), Chiang Mai, Thailand, Oct 24–25 2024.
- **Link:** [Scilit listing](https://www.scilit.com/publications/ea45ed29ea65de4b0b828a8d65e8acf1) · [EasyChair preprint](https://easychair.org/publications/preprint/Xd3D/open) · **Access:** preprint-only
- **Summary:** Trains SER models on English and Mandarin, transfers to Thai (a tonal language) as target. Finds Mandarin transfers better than English to Thai, but neither beats in-language Thai training.
- **Novelty impact:** A tonal→tonal (Mandarin→Thai) and non-tonal→tonal (English→Thai) cross-lingual SER transfer study — the closest thing to "does tonality of the source/target language matter for SER transfer" found in this pass. Does **not** model or disentangle tone-vs-emotion within a single language; purely a transfer-accuracy comparison.
- **Why it matters here:** Weak supporting evidence that tonal-language SER may behave differently from non-tonal (Mandarin↛Thai gains are limited), but it is not the same research question as the Vietnamese hook. Low confidence citation (preprint, unconfirmed authorship).

### THAI Speech Emotion Recognition (THAI-SER) corpus
- **Authors / Year / Venue:** Jilamika Wongpithayadisai, Chompakorn Chaksangchaichot, Soravitt Sangnark, Patawee Prakrankamanant, Krit Gangwanpongpun, Siwa Boonpunmongkol, Premmarin Milindasuta, Dangkamon Na-Pombejra, Sarana Nutanong, Ekapol Chuangsuwanich. 2025. arXiv preprint.
- **Link:** [arXiv:2507.09618](https://arxiv.org/abs/2507.09618) · **Access:** open (preprint; CC-BY-SA 4.0 corpus)
- **Summary:** First sizeable Thai SER corpus (41h36m, 27,854 utterances, 200 actors, 5 emotions), scripted+improvised, crowdsourced annotation.
- **Novelty impact:** A **dataset** paper, not a tone-aware modeling paper — no tone analysis or disentanglement. Relevant to `find-dataset` if a tonal-language (non-Vietnamese) validation corpus is wanted for a cross-lingual claim.
- **Why it matters here:** Candidate open dataset for a cross-tonal-language generalization experiment (Vietnamese + Thai) if the paper wants to argue the phenomenon generalizes beyond Vietnamese; flag for `find-dataset`.

---

## C. Bimodal / semantic-vs-acoustic-conflict SER — the closest architectural competitors (not tonal-language-specific)

### When Tone and Words Disagree: Towards Robust Speech Emotion Recognition under Acoustic-Semantic Conflict
- **Authors / Year / Venue:** Authors not extracted from the fetched abstract page (arXiv metadata page did not surface a full author list in this pass — flag for a follow-up author check before citing). arXiv preprint, dated Jan 2026.
- **Link:** [arXiv:2601.04564](https://arxiv.org/abs/2601.04564) · **Access:** preprint-only
- **Summary:** Introduces **CASE** (Conflict in Acoustic-Semantic Emotion), a dataset dominated by cases where **paralinguistic tone-of-voice contradicts lexical/semantic content**, and a **Fusion Acoustic-Semantic (FAS)** model that explicitly disentangles acoustic and semantic pathways via a query-based attention module, beating ASR-based/SSL/audio-LLM baselines (59.38% on CASE).
- **Novelty impact:** **This is the single closest architectural competitor found in this pass.** It already builds a bimodal (audio+text) SER architecture that explicitly disentangles a "tone" channel from a "semantic" channel and shows conventional SER models fail under that conflict. **Critically, "tone" here means paralinguistic tone-of-voice (general, language-agnostic), not lexical tone in a tonal language** — there is no indication in the retrieved abstract that CASE is Vietnamese, Mandarin, or otherwise tonal-language-specific. This **narrows but does not close** the Vietnamese niche: the generic acoustic-vs-semantic disentanglement architecture is claimed (Jan 2026, very recent), so the Vietnamese paper's novelty must rest specifically on **lexical tone as a structural, phonemically-forced confound** (not an incidental sarcasm-like conflict) — a distinct and stronger claim this paper does not make.
- **Why it matters here:** Must be cited and explicitly distinguished from in the related-work section; also a candidate architecture template (query-based attention fusion) to adapt for the Vietnamese tone-vs-emotion case. Flag for `analysis-paper` to confirm CASE's language coverage before finalizing the distinction.

### Evaluating Emotion Recognition in Spoken Language Models on Emotionally Incongruent Speech
- **Authors / Year / Venue:** Authors not fully extracted from the fetched page. arXiv preprint, Oct 2025.
- **Link:** [arXiv:2510.25054](https://arxiv.org/html/2510.25054) · **Access:** preprint-only
- **Summary:** Tests spoken-language models (SALMONN, DeSTA2, Qwen2-Audio, Audio Flamingo-3) on synthetic emotionally-incongruent speech (semantic content says one emotion, acoustic delivery says another). Finds SLMs rely almost entirely on **textual semantics** (80–100% acc.) and are near-random (~25%) on acoustic-only emotion, while a dedicated SER baseline handles acoustic cues far better.
- **Novelty impact:** Directly supports (for a *different*, non-tonal reason — model architecture bias, not lexical constraint) the hook's underlying intuition that **text/semantic signal can dominate over acoustic/prosodic signal in current SER-adjacent systems**. Not tonal-language work, not Vietnamese, no lexical tone. Does not occupy the niche but is a relevant "semantic branch can be more informative" precedent to cite and contrast (their cause is model bias; the Vietnamese paper's claimed cause is a phonemic constraint on F0).
- **Why it matters here:** Useful contrastive citation — frames the Vietnamese paper's contribution as showing this "semantics can dominate" phenomenon has a **principled phonetic cause** (tone-locked F0) rather than only a model-training artifact.

---

## D. Vietnamese SER papers found (small-scale, none tone-aware)

### VNEMOS: Vietnamese Speech Emotion Inference Using Deep Neural Networks
- **Authors / Year / Venue:** Quang-Anh N.D., Manh-Hung Ha, Quynh Chi Nguyen, Nguyen Thi Thu Hien, Quan Vu, Minh-Duc D.X, Duc-Chinh Nguyen, Thai Kim Dinh. 2024. IEEE, *9th International Conference on Integrated Circuits, Design, and Verification (ICDV) 2024*.
- **Link:** [IEEE Xplore 10616411](https://ieeexplore.ieee.org/document/10616411/) · [ResearchGate PDF](https://www.researchgate.net/publication/382622286_VNEMOS_Vietnamese_Speech_Emotion_Inference_Using_Deep_Neural_Networks) · **Access:** paywalled (IEEE); preprint PDF available via ResearchGate
- **Summary:** Introduces a Vietnamese SER dataset (250 clips from movies/live shows, 5 emotions) and a DNN classifier reaching ~89% accuracy.
- **Novelty impact:** Standard acoustic-feature + DNN Vietnamese SER; **no tone treatment, no bimodal architecture, no disentanglement**. Occupies "Vietnamese SER exists as a small-scale task" but leaves the tone-aware/bimodal niche fully open.
- **Why it matters here:** The dataset (VNEMOS) is the training data for two later papers below (same author cluster) — worth checking for `find-dataset` if small-scale Vietnamese SER validation data is needed, but it is acted/movie speech, not spontaneous, and license/availability need verification.

### Emotional Vietnamese Speech-Based Depression Diagnosis Using Dynamic Attention Mechanism
- **Authors / Year / Venue:** Quang-Anh N.D., Manh-Hung Ha, Thai Kim Dinh, Minh-Duc Pham, Ninh Nguyen Van (Vietnam National University, Hanoi). arXiv preprint Dec 2024; Springer book chapter (LNCS/CCIS-style, DOI prefix `978-3-032-00267-9_23`), ~2025/2026.
- **Link:** [arXiv:2412.08683](https://arxiv.org/html/2412.08683) · [Springer chapter](https://link.springer.com/chapter/10.1007/978-3-032-00267-9_23) · **Access:** preprint open (arXiv); Springer chapter paywalled
- **Summary:** A Dynamic-CBAM (Omni-Dimensional Dynamic Convolution attention) + BiGRU model trained on the VNEMOS dataset (MFCC-only features, best config) for 5-class emotion classification as a depression-diagnosis proxy; reports UA 0.87 / WA 0.86 / F1 0.87.
- **Novelty impact:** Same author cluster and dataset as VNEMOS above, repurposed for depression screening. **No tone analysis, audio-only (not bimodal), and explicitly finds raw-waveform+MFCC dual-stream underperforms MFCC-only** — i.e., they did not find value in a richer/text-channel signal. Does not touch the tone-emotion niche.
- **Why it matters here:** A candidate baseline number for a Vietnamese SER paper's non-tone-aware comparison point, and evidence that this author group has not yet explored bimodal or tone-aware framing — supports the niche being open for a differently-framed contribution.

### GMM for Emotion Recognition of Vietnamese
- **Authors / Year / Venue:** Đào T. L. Thủy, T. V. Loan, N. H. Quang. 2018 (published Mar 2018, dated "2017" cover). *Journal of Computer Science and Cybernetics* (Vietnam Academy of Science and Technology), Vol. 33, No. 3, pp. 229–246.
- **Link:** [VJS/JCC](https://vjs.ac.vn/jcc/article/download/11017/381626/382661) · **Access:** open
- **Summary:** Classical GMM classifier on Vietnamese speech (4 emotions: neutral/sadness/anger/happiness), using MFCC + F0 + energy + formants + F0-variant features; speaker/content-dependent accuracy up to 89.21%.
- **Novelty impact:** Pre-deep-learning Vietnamese SER; uses F0 as one of several hand-crafted features but **does not analyze or model the tone-emotion interaction** — F0 is treated purely as an acoustic feature, with no reference to Vietnamese's 6-tone system as a confound. Historical baseline only.
- **Why it matters here:** Shows Vietnamese SER work has existed since 2018 without ever engaging the tonal-confound question — reinforces that the specific angle is unclaimed even after ~8 years of small Vietnamese SER papers.

### Human-Guided Reasoning with Large Language Models for Vietnamese Speech Emotion Recognition
- **Authors / Year / Venue:** Truc Nguyen, Then Tran, Binh Truong, Phuoc Nguyen T. H. arXiv preprint, Apr 2026.
- **Link:** [arXiv:2604.01711](https://arxiv.org/html/2604.01711v1) · **Access:** preprint-only
- **Summary:** A hybrid acoustic-feature (pitch/energy/MFCC) + LLM-reasoning pipeline for 3-class Vietnamese SER (calm/angry/panic) on a new 2,764-sample corpus (Fleiss' κ = 0.857); ~86.6% accuracy, approaching human agreement.
- **Novelty impact:** The **most recent** Vietnamese SER paper found (Apr 2026) and the one closest in time to a hypothetical Pebble submission. It explicitly **names** "tone" as a source of acoustic complexity in its motivation ("complex acoustic characteristics influenced by tone, region, and speaking style") but **does not model or isolate tone's effect** — it is acknowledged as a confound, not addressed. This is the strongest single piece of evidence that **researchers are aware of the tone confound in Vietnamese SER but no one has yet built a system around disentangling it.**
- **Why it matters here:** Highest-priority related-work citation for the "even the most recent Vietnamese SER paper flags tone as an open confound" framing — directly supports the novelty claim. Also a natural baseline/dataset competitor to benchmark against or contrast methodologically (LLM-reasoning fusion vs a tone-aware bimodal architecture).

### EmoFedProto: Privacy-Preserving Vietnamese Speech Emotion Recognition via Prototype-Based Federated Learning
- **Authors / Year / Venue:** Not fully confirmed from indexed snippet. 2025/2026. *EAI Endorsed Transactions on AI and Robotics*.
- **Link:** [EAI](https://publications.eai.eu/index.php/airo/article/view/11595) · **Access:** open access (EAI journal; not independently verified in this pass)
- **Summary:** Federated-learning framework (prototype-based, clustering-enhanced) for privacy-preserving Vietnamese SER on the VNEMOS dataset; 0.875 accuracy vs 0.825 FedProto baseline.
- **Novelty impact:** Orthogonal contribution (privacy/federated learning), no tone treatment, no bimodal architecture. Confirms VNEMOS is becoming a de facto small Vietnamese SER benchmark across several unrelated methodological papers.
- **Why it matters here:** Low priority; mainly useful to note VNEMOS as a recurring (if small, acted) Vietnamese SER dataset other groups reuse.

---

## E. Note — false positive worth flagging

- **"On the Importance of Tonal Features for Speech Emotion Recognition"** ([ResearchGate](https://www.researchgate.net/publication/264182814_On_the_Importance_of_Tonal_Features_for_Speech_Emotion_Recognition)) surfaced repeatedly on "tonal" keyword searches but uses **"tonal" in the music-theory/chroma-feature sense** (major/minor key perception analogy), unrelated to lexical tone in tonal languages. Excluded from ranking; noted so a future search does not re-litigate it as a hit.

---

## Novelty verdict

**Overall: the niche is OPEN, though narrower than it looked before this search.**

1. **Phonetic premise (tone × emotional prosody compete for F0) is well-established for Mandarin** (Chang et al. 2023 PLOS ONE; Xiao & Liu 2024; Zhang et al. 2023) — this is good news: the paper's motivating claim is not speculative, it is citable, peer-reviewed phonetics. None of these are modeling papers.
2. **No paper found builds a tone-aware or tone-disentangling *SER model* for Vietnamese, Mandarin, Cantonese, or Thai.** Every Vietnamese SER paper found (VNEMOS 2024, GMM 2018, LLM-reasoning 2026, EmoFedProto, depression-diagnosis 2024) treats F0/pitch as a generic acoustic feature and never engages the 6-tone lexical constraint — the Apr-2026 paper even *names* "tone" as a confound in its own motivation without addressing it.
3. **The closest architectural competitor is language-agnostic, not tonal-language-specific**: "When Tone and Words Disagree" (arXiv:2601.04564, Jan 2026) already builds a bimodal audio+text SER model that disentangles acoustic "tone-of-voice" from semantic content — but its "tone" is paralinguistic (sarcasm-like conflict), not phonemic lexical tone, and there is no evidence it targets a tonal language. This is the single most important paper to explicitly cite-and-distinguish from, since a reviewer will ask "how is this different from CASE/FAS?"
4. **Vietnamese-specific phonetic evidence (already in the repo, #35 Shen et al. NAACL 2024) is a load-bearing asset**: it shows Vietnamese lexical tone is *harder to decode from speech representations than Mandarin* and leans on **phonation/voice-quality** more than F0-contour — meaning the tone-emotion confound in Vietnamese may have a *different acoustic signature* than in Mandarin, which is itself an unclaimed, citable, and testable sub-claim.

**Unclaimed framing that remains open:** *"A bimodal (audio+text) Vietnamese SER system that explicitly models/quantifies how much of the acoustic F0/pitch signal is consumed by lexical-tone realization vs. emotional prosody, and shows the text branch becomes relatively more load-bearing than in non-tonal-language SER (e.g. English/RAVDESS) as a consequence — with Vietnamese's phonation-heavy tone system (per Shen et al. 2024) potentially compounding the effect."* No prior work — phonetic or computational — makes this specific combined claim for any tonal language, let alone Vietnamese.

**Sources:**
- [Chang et al. 2023, PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0283635)
- [Xiao & Liu 2024/2026, Second Language Research](https://journals.sagepub.com/doi/10.1177/02676583241286748)
- [Zhang et al. 2023, Behavioral Sciences](https://pmc.ncbi.nlm.nih.gov/articles/PMC10603920/)
- [Cantonese vocal emotions, JSLHR 2025](https://pubs.asha.org/doi/10.1044/2025_JSLHR-24-00677)
- [Cross-lingual SER Thai target, ICAS2024](https://www.scilit.com/publications/ea45ed29ea65de4b0b828a8d65e8acf1)
- [THAI-SER corpus, arXiv:2507.09618](https://arxiv.org/abs/2507.09618)
- [When Tone and Words Disagree, arXiv:2601.04564](https://arxiv.org/abs/2601.04564)
- [Emotionally Incongruent Speech SLM eval, arXiv:2510.25054](https://arxiv.org/html/2510.25054)
- [VNEMOS, IEEE ICDV 2024](https://ieeexplore.ieee.org/document/10616411/)
- [Vietnamese depression diagnosis, arXiv:2412.08683](https://arxiv.org/html/2412.08683)
- [GMM Vietnamese emotion, JCC 2018](https://vjs.ac.vn/jcc/article/download/11017/381626/382661)
- [Human-Guided Reasoning Vietnamese SER, arXiv:2604.01711](https://arxiv.org/html/2604.01711v1)
- [EmoFedProto, EAI](https://publications.eai.eu/index.php/airo/article/view/11595)
- Already in repo: [Shen et al., NAACL 2024, docs/papers/voice/35-shen-lexical-tone-ssl.md](../voice/35-shen-lexical-tone-ssl.md) · [aclanthology](https://aclanthology.org/2024.naacl-long.239/)
