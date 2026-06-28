# Related work — emotional tone (positive ↔ negative) of user messages

> Topic: *analyze a user's messages for emotional tone (positive vs. negative)* — sentiment / valence polarity
> (binary, ordinal, or continuous) on user text, esp. mental-health / social-media / conversational contexts.
> Found 2026-06-25 by two parallel `research-paper` agents (methods/benchmarks + MH/conversational angles).
> Every link + venue verified; access flagged honestly. Deduplicated against papers Pebble already holds.
>
> **Closeness dims** (source `related-work-survey.md`): 1) MTL encoder w/ categorical+continuous affect heads ·
> 2) mental-health/crisis text · 3) transfer from GoEmotions/EmpatheticDialogues/intensity · 4) silver-label LLM
> distillation · 5) MTL loss balancing · 6) safety/crisis recall objective · 7) encoder backbone (BERT/RoBERTa/
> NeoBERT/ModernBERT ~250M).
>
> Top-4 picks get full per-paper dossiers (overlap %): **54 VADEC · 55 CLPsych 2025 · 56 MentaLLaMA · 57 Mitsios EMD**
> in [`finetuning-message/`](finetuning-message/). Dataset acquisition (IMHI, CLPsych): see
> [`../tasks/emotional-tone-papers.md`](../tasks/emotional-tone-papers.md).

---

## Top tier — closest to Pebble

### 54 · VADEC — joint categorical emotion classification + continuous VAD regression on tweets
- **Authors / Year / Venue:** Mukherjee, Naik, Poddar, Dasgupta, Ganguly. 2021. **SIGIR 2021**. · **overlap 38%** → [dossier](finetuning-message/54-vadec.md)
- **Link:** [arXiv:2105.03983](https://arxiv.org/abs/2105.03983) · [ACM DL](https://dl.acm.org/doi/10.1145/3404835.3463080) · **open**
- **Summary:** Multi-task transformer that jointly trains multi-label categorical emotion classification **and** continuous VAD (valence/arousal/dominance) regression on a shared encoder, exploiting cross-task correlation. Eval: SemEval-2018 AIT + EmoBank.
- **Closeness:** Dim 1 (strong — cat+cont heads on one encoder, parallels Pebble) · Dim 3 (mod — AIT/EmoBank) · Dim 5 (weak — additive MTL loss).
- **Why it matters:** The single closest published design to Pebble's mixed categorical+regression MTL head structure. **Baseline architecture to beat.**

### 55 · CLPsych 2025 Shared Task — continuous wellbeing scoring + evidence extraction on social-media timelines
- **Authors / Year / Venue:** Tseriotou, Chim, Klein, … Liakata. 2025. **CLPsych 2025 @ NAACL**. · **overlap 54%** → [dossier](finetuning-message/55-clpsych-2025.md)
- **Link:** [aclanthology 2025.clpsych-1.16](https://aclanthology.org/2025.clpsych-1.16/) · **open**
- **Summary:** Extract adaptive/maladaptive self-state spans (evidence), assign a **continuous 1–10 wellbeing score** per post (regression), and post-/timeline-level summaries. MIND framework (Affect/Behavior/Cognition/Desire).
- **Closeness:** Dim 1 (strong — continuous wellbeing ≈ Pebble severity/energy head) · Dim 2 (strong — MH social media) · Dim 6 (maladaptive-state → crisis precursor).
- **Why it matters:** Only benchmark formalizing **continuous wellbeing regression + evidence extraction together** — closest analogue to Pebble's continuous severity + safety heads. **Dataset target (item 3).**

### 56 · MentaLLaMA — LLM-teacher → open student, interpretable multi-task mental-health on social media
- **Authors / Year / Venue:** Yang, Zhang, Kuang, Xie, Huang, Ananiadou. 2024. **WWW 2024**. · **overlap 42%** → [dossier](finetuning-message/56-mentallama.md)
- **Link:** [arXiv:2309.13567](https://arxiv.org/abs/2309.13567) · [ACM DL](https://dl.acm.org/doi/10.1145/3589334.3648137) · **open (arXiv); ACM paywalled**
- **Summary:** Builds **IMHI** (105K instruction samples, 8 MH tasks, 10 Reddit/Twitter sources); ChatGPT generates quality-gated silver explanations; fine-tunes LLaMA2 → MentaLLaMA, near discriminative SOTA + rationales.
- **Closeness:** Dim 4 (strong — ChatGPT-teacher → student, gated silver labels) · Dim 2 (strong — 8 MH tasks) · Dim 3 (mod — multi-source).
- **Why it matters:** Most direct analogue of Pebble's teacher→student silver-label distillation on MH text; **IMHI = candidate held-out test set (item 3).**

### 57 · Mitsios et al. — valence-ordinal emotion classification with a distance-aware ordinal loss (GoEmotions)
- **Authors / Year / Venue:** Mitsios, Vamvoukakis, Maniati et al. 2024. **NAACL 2024 (short)**. · **overlap 35%** → [dossier](finetuning-message/57-mitsios-emd-valence.md)
- **Link:** [arXiv:2404.01805](https://arxiv.org/abs/2404.01805) · [aclanthology 2024.naacl-short.72](https://aclanthology.org/2024.naacl-short.72/) · **open**
- **Summary:** Reframes GoEmotions discrete classification as **ordinal along the valence axis** (then 2D valence-arousal) with a **distance-aware ordinal loss** → SOTA accuracy + far fewer cross-valence (severe) errors. Backbone RoBERTa-CNN. ⚠ *Correction: the loss is MSE-on-ordinal-targets, not Earth Mover's Distance as first labeled — see dossier caveat (filename keeps `emd` for stability).*
- **Closeness:** Dim 3 (strong — GoEmotions taxonomy) · Dim 7 (RoBERTa-class) · Dim 1 (mod — valence structure on the emotion head).
- **Why it matters:** Concrete **loss design Pebble can adopt** to keep its discrete emotion head and continuous valence head coherent — port R2's existing CORAL machinery from the severity head to the emotion head ([`finetuning-message/48-coral.md`](finetuning-message/48-coral.md)).

---

## Mid tier — framing / backbone baselines

### SoftMCL — continuous valence as soft labels for contrastive sentiment pre-training
- Wang, Yu, Zhang. 2024. **LREC-COLING 2024**. [arXiv:2405.01827](https://arxiv.org/abs/2405.01827) · **open**
- Replaces hard pos/neu/neg with continuous valence (E-ANEW, EmoBank) as soft-label targets + momentum queue. *Dim 1/7.* Lesson: continuous valence supervision > hard polarity for fine-grained embeddings.

### Emotion Granularity from Text — emotion differentiation as a mental-health indicator
- Vishnubhotla, Teodorescu, Feldman, Lindquist, Mohammad. 2024. **EMNLP 2024**. [arXiv:2403.02281](https://arxiv.org/abs/2403.02281) · **open**
- Lower granularity (collapsing to coarse pos/neg) correlates with MH conditions on longitudinal Reddit posts. *Dim 1/2/3.* Psycholinguistic framing for why pos/neg tracking predicts wellbeing.

### SleepDepNet — MTL BERT: depressive sentiment + sleep quality from Reddit
- Kumar, Sangwan, Sharma. 2026. **PLOS Digital Health**. [PLOS](https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0000859) · **open**
- Shared BERT+BiLSTM-attn on 50K posts → sleep (good/poor) + depressive sentiment (pos/neu/neg); SleepDepScore. F1 0.89/0.86. *Dim 1/2/7.* Structural parallel to emotion+safety co-training.

### SentiWSP — dual-objective (word+sentence) sentiment-aware pre-training on RoBERTa
- Fan, Lin, Li, … Duan. 2022. **EMNLP 2022**. [arXiv:2210.09803](https://arxiv.org/abs/2210.09803) · **open**
- Generator-discriminator word-level + contrastive sentence-level objectives on RoBERTa; SOTA IMDB 96.17. *Dim 7.* The "sentiment-specialized pretrain vs vanilla RoBERTa" baseline a reviewer will raise.

### SentiLARE — sentiment-aware BERT pre-training with SentiWordNet polarity injection
- Ke, Ji, Liu, Zhu, Huang. 2020. **EMNLP 2020**. [arXiv:1911.02493](https://arxiv.org/abs/1911.02493) · [GitHub](https://github.com/thu-coai/SentiLARE) · **open**
- Injects POS + SentiWordNet polarity via label-aware MLM; SST-5 58.59 / IMDB 95.71. *Dim 7.* Lexicon-injection-into-pretrain baseline class.

### SentiBERT — compositional sentiment via constituency-tree attention on BERT
- Yin, Meng, Chang. 2020. **ACL 2020**. [arXiv:2005.04114](https://arxiv.org/abs/2005.04114) · **open**
- Phrase-level compositional sentiment (negation/contrast); transfers to EmoContext/EmoInt. *Dim 3/7.* Insight: phrase-level valence warm-start transfers to emotion tasks.

### Crisis Counselor Language — positive/negative affect cues in text-based crisis conversations
- Buda, Tripodi, Meagher, Olson. 2024. **Findings of EMNLP 2024**. [aclanthology 2024.findings-emnlp.418](https://aclanthology.org/2024.findings-emnlp.418/) · **open**
- Positive emotional language/affirmations ↔ higher perceived counselor concern; self-talk/templates ↔ lower. *Dim 2/6.* Framing for a receptivity head + why de-escalation tone matters.

### PLOS hotline crisis detection — multi-label crisis severity from transcripts (RoBERTa + GPT embeddings)
- Rao, Deng, Song, … Jiang. 2026. **PLOS Digital Health**. [PLOS](https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0001383) · **open**
- 1,057 Chinese hotline transcripts; GPT-embeddings + classifier → high-risk F1 80.48; text > audio. *Dim 6/4/2.* Baseline crisis-detection bar; validates text-only. ⚠ Chinese-language domain shift.

### SemEval-2017 Task 4 — Twitter sentiment benchmark (2/3/5-point polarity)
- Rosenthal, Farra, Nakov. 2017. **SemEval-2017 @ ACL**. [aclanthology S17-2088](https://aclanthology.org/S17-2088/) · **open**
- Canonical binary/3-/5-point polarity benchmark on tweets. *Dim 1/7 weak.* Citation for "binary & 5-point polarity on social text"; Pebble's continuous valence subsumes the 5-point scale.

### EmoDynamiX — fine-grained ERC + strategy prediction in emotional-support dialogue
- Wan, Labeau, Clavel. 2025. **NAACL 2025 (oral)**. [aclanthology 2025.naacl-long.81](https://aclanthology.org/2025.naacl-long.81/) · [arXiv:2408.08782](https://arxiv.org/abs/2408.08782) · **open**
- Heterogeneous graph over user emotion states + system strategies on a RoBERTa encoder; ESC datasets. *Dim 1/2/3.* Template for emotion-output → conversation-action (encoder→Decision Engine).

---

## Caution flags (not peer-reviewed / tiny sample)

### Park et al. — EMD categorical→VAD transfer (RoBERTa)
- Park, Kim, Ye, Jeon, Park, Oh. 2019/2021. **preprint-only (no confirmed venue)**. [arXiv:1911.02499](https://arxiv.org/abs/1911.02499) · ⚠
- EMD loss over valence-sorted categories induces VAD-correlated embeddings (zero-shot EmoBank). Clean technique kin to #57; verify venue before citing.

### Detecting Anxiety/Depression in Dialogues — LLM-feature + ML on chatbot logs
- de Arriba-Pérez, García-Méndez. 2024. **AIxIA Healthcare Workshop**. [arXiv:2412.17651](https://arxiv.org/abs/2412.17651) · ⚠ preprint/workshop
- Multi-label anxiety+depression from chatbot conversations; 90% acc but only **32 users**. *Dim 2/4.* Framing only — lowest confidence.

---

## Datasets (acquired 2026-06-26)
- **IMHI (MentaLLaMA)** — ✅ acquired: 19,051 labeled test rows (MIT) in `data/finetuning-message/external/imhi/`
  (8 MH tasks; swmh 5-class + t-sid suicide/self-harm best for the safety head). Label-only OOD eval; not for training.
- **CLPsych 2025** — ⛔ gated (per-member DUA, 2025 registration closed). Access steps drafted in
  `data/finetuning-message/external/clpsych-2025/ACCESS-REQUEST.md`. Research-only — cannot back the shipped checkpoint.

## Synthesis
- **Architecture / paper-writing for Pebble:** **VADEC (54)** (cat+cont MTL predecessor) + **Mitsios EMD (57)** (adoptable valence-ordinal loss).
- **MH / distillation stream:** **CLPsych 2025 (55)** (continuous wellbeing benchmark) + **MentaLLaMA (56)** (teacher→student distillation + IMHI dataset).
- **EmoDynamiX** is the strongest template for turning emotional-tone output into a downstream action.
