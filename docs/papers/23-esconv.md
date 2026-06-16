# Paper 23 — Towards Emotional Support Dialog Systems (ESConv)

> Enrichment set · Pillar 7 (emotional-support domain). Analysis depth: abstract + annotation summary + dataset fetch. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Liu, Zheng, Demasi, Sabour, Li, Yu, Jiang, Huang. ACL 2021.
- **Link:** [arXiv:2106.01144](https://arxiv.org/abs/2106.01144) · [ACL 2021.acl-long.269](https://aclanthology.org/2021.acl-long.269/) · open
- **Pebble pillar:** in-domain emotional-support dialogue dataset (Pebble's downstream domain).

## Summary
Introduces ESConv: 1,300 multi-turn emotional-support dialogues (38K turns) with pre-chat **emotion category + 1–5 emotion-intensity** ratings, per-utterance **support-strategy** labels, and seeker feedback scores. The modeling side is generative (strategy-conditioned BlenderBot), not a multi-task affect encoder.

## Overlap with Pebble — 31% (peripheral)
`D1=1, D2=2, D3=1, D4=0, D5=0, D6=0, D7=0` → (3·1 + 2·2 + 1·1)/26 = 8/26 = **31%**
- **Closest on:** D2 (emotional-support / psychological-distress domain) and D1 (label space spans categorical emotion/problem/strategy + continuous intensity & feedback — though no multi-head encoder is built).

## Best point — Dataset to reuse
Human **emotion category + 1–5 intensity** + feedback scores in exactly Pebble's support domain — paired categorical + continuous affect labels.
- **How to apply to Pebble:** Map intensity → `severity`/`energy` and emotion → the softmax head; use as a small in-domain **human-labeled calibration slice** to check Gemini silver scores against real human intensity (a calibration anchor for the distillation angle).

## Dataset status — ✅ ACQUIRED
`data/external/esconv/` (ESConv.json + train/valid/test = 910/195/195 convs). **License CC-BY-NC-4.0 → research-only, NOT deployable.** Source: [HF thu-coai/esconv](https://huggingface.co/datasets/thu-coai/esconv) / [GitHub thu-coai](https://github.com/thu-coai/Emotional-Support-Conversation).
- `emotion_type` (anxiety/depression/sadness/anger/fear/shame/disgust/nervousness/…) maps to the emotion head; `strategy` (8 classes) is a candidate new head.
- **Next step:** add `load_esconv()` to `external.py` (mirror `load_semeval_intensity`); document the NC license in the docstring (research arm only).

## Caveats
Architecture details from abstract + secondary summaries. A dialog-*generation* paper — no affect classifier/encoder, no continuous head, no safety head, no distillation, no MTL balancing → D4–D7 = 0. Value is the labeled dataset, not a method.

## Deep research — full-PDF read (2026-06-16)

> Read end-to-end from the local PDF `pdfs/23-esconv.pdf` (arXiv:2106.01144v1, "Towards
> Emotional Support Dialog Systems", Liu et al., ACL-IJCNLP 2021, anthology 2021.acl-long.269)
> via `pdftotext` — main text, all tables (1–7), all appendices (A–E), and the worked annotation
> example (Fig. 6). Also inspected the **acquired** dataset directly at `data/external/esconv/`
> (`ESConv.json`, 1,300 conversations) to confirm the exact on-disk schema, label vocabularies, and
> the 1–5 intensity field — because the released HF/GitHub corpus is **larger** than the paper's
> reported 1,053, and Pebble loads the on-disk version, not the paper's. This section only adds what
> §§ above do not; cross-refs point back.

### Source-access note

- **PDF read:** full text + Tables 1–7 + Appendices A (worked example), B (strategy definitions),
  C (impl. details), D (auto-approval / agreement), E (interface). Local PDF is the arXiv v1
  preprint; no later venue revision changes the dataset schema.
- **Provenance validations (query → URL → status):**
  - Venue/authors/year — "Towards Emotional Support Dialog Systems ACL 2021" →
    `https://aclanthology.org/2021.acl-long.269/` → ✔ ACL-IJCNLP 2021, all 8 authors confirmed.
    The anthology landing page does **not** print dataset stats (it carries only title/abstract).
  - License + on-disk fields + split sizes — `https://huggingface.co/datasets/thu-coai/esconv` →
    ✔ **CC-BY-NC-4.0**; fields `experience_type / emotion_type / problem_type / situation /
    survey_score / dialog`; split **910 / 195 / 195 = 1,300**.
  - Schema + label vocab + 1–5 intensity — read directly from the acquired `ESConv.json`
    (`len = 1300`; `survey_score.seeker.initial_emotion_intensity` ∈ {1,2,3,4,5}) → ✔ self-verified.
- **Numbers cited from the PDF that describe the *paper's* corpus (n=1,053) are tagged
  "paper-1053"; numbers describing the *acquired release* (n=1,300) are tagged "release-1300".**
  These are two snapshots of the same dataset — do not mix the two when quoting a stat.

### What the paper actually does

A **dialog-generation** paper, not an affect classifier. It (1) defines the Emotional Support
Conversation (ESC) **task**, (2) proposes the **ESC Framework** (3 stages × 8 strategies, grounded
in Hill 2009 *Helping Skills*), (3) crowd-collects the **ESConv** dataset, and (4) fine-tunes
BlenderBot-small / DialoGPT-small variants conditioned on strategy tokens. Pebble's value is
entirely in the **dataset + label schema**, not the modeling.

**The label schema (exact, the load-bearing extract for D-H/D-D):**

- **Three-stage framework** (§3.2): **Exploration** → **Comforting** → **Action**. (Hill's original
  middle stage *Insight* was deliberately renamed/replaced by *Comforting* because insight
  "is both difficult and risky for supporters without professional experience.") Order is
  *suggested, not enforced* — Fig. 4 shows Question dominates early, Providing-Suggestions late,
  Affirmation roughly constant throughout. ✔ (§3.2, Fig. 3–4)
- **8 support strategies** (per-supporter-utterance label; defined in Appendix B): **Question;
  Restatement or Paraphrasing; Reflection of Feelings; Self-disclosure; Affirmation and
  Reassurance; Providing Suggestions; Information; Others.** Seven are skills extracted from Hill;
  "Others" is the catch-all. ✔ (Fig. 3, App. B)
- **Pre-chat emotion category** (seeker self-report, **1 of 7** in the paper): anxiety, depression,
  sadness, anger, fear, disgust, shame. ✔ (§4.2, Table 3)
- **Pre-chat emotion intensity** (D-D anchor): **a single integer 1–5**, "the larger number
  indicates a more intense emotion," self-reported by the seeker *before* the chat. A **post-chat**
  1–5 intensity is also collected; *emotion improvement = pre − post*. ✔ (§3.1, §4.2, Fig. 6)
- **Problem category**: 1 of 5 in the paper (ongoing depression, job crisis, breakup with partner,
  problems with friends, academic pressure). ✔ (Table 3)

**Size & quality control:**

- Funnel (§4.3): 5,449 supporter applicants → **425 passed (7.8%)**; 2,472 raw convs → 1,342 after
  length/finish filter → **1,053 auto-approved (78.5%)** [paper-1053]. ✔ (§4.3)
- Stats (Table 2) [paper-1053]: **1,053 dialogues, 31,410 utterances, avg 29.8 utt/dialogue**,
  avg utt length 17.8 tokens, avg 22.6 min/chat, 854 workers (425 supporters / 532 seekers). ✔
  (NB the md stub's "38K turns / 1,300 convs" is the *release-1300* figure, not the paper's 31,410.)
- **Mean intensity 4.04 before → 2.14 after** the conversation — the headline evidence that support
  worked. ✔ (§4.3)
- Strategy frequency (Table 3, of 14,855 supporter utts) [paper-1053]: Question 20.9%, Others 18.1%,
  Affirmation 16.1%, Providing Suggestions 15.6%, Self-disclosure 9.4%, Reflection 7.8%, Information
  6.1%, Restatement 5.9%. ✔
- Seeker turn-level **feedback** is a 1–5 star score every 2 supporter utterances; phase means rise
  4.03 → 4.30 → 4.44 across the conversation. ✔ (§4.2)

**Inter-annotator agreement (the only IAA in the paper, Appendix D):** there is **no IAA on the
emotion/intensity/strategy labels themselves** — those are single-source self-reports (seeker) or
single-author (supporter) labels. The reported agreement is **Cohen's κ between rule-based
auto-approval filters and 3 trained human judges** on 100 sampled conversations: the chosen final
rule scores **κ = 0.576 average** ("significant agreement"); individual rule rows range κ ≈ 0.51–0.59.
✔ (Table 7, App. D). Separately, strategy-annotation **correction**: 2,545 utterances (17.1%) were
re-reviewed and 139 revised where >75% of reviewers disagreed; 130 intensity-anomaly conversations
re-checked, 92% revised (seekers had confused "negative intensity" with "positive emotion"). ✔ (§4.3)

**Modeling results (peripheral to Pebble):** strategy-conditioned **Oracle > Vanilla** on all auto
metrics (BlenderBot Oracle B-2 6.31 / R-L 17.90 / Extrema 51.65 vs Vanilla 5.45 / 15.43 / 50.49,
Table 4); in human eval the **Joint** model beats no-finetune / Vanilla / Random on all 5 axes
(e.g. 73:20 win:lose overall vs no-finetune, Table 5). Backbones: BlenderBot-small-90M, DialoGPT-small,
lr 5e-5, 5 epochs, dialog cut to 5-utterance windows, 6:2:2 split (App. C). ✔

**Acquired release vs paper (load-bearing for D-H):** `data/external/esconv/ESConv.json` is the
*expanded* release — **1,300 conversations** (910/195/195), and its label vocabularies are *wider*
than the paper's:
- **emotion_type (11 distinct on disk):** anxiety 354, depression 334, sadness 308, anger 111,
  fear 95, shame 42, disgust 40, nervousness 13, + singletons pain/jealousy/guilt (1 each). ✔
  (self-verified) — i.e. the paper's "7 emotions" became 11 (plus a long tail) in the release.
- **problem_type (13 distinct on disk):** ongoing depression 351, job crisis 280, breakup 239,
  problems with friends 179, academic pressure 156, + 8 newer types (sleep problems, procrastination,
  alcohol abuse, appearance anxiety, conflict with parents, issues with children/parents, school
  bullying). ✔
- **strategy (8, exact on-disk strings):** `Question` 3801, `Others` 3341, `Providing Suggestions`
  2954, `Affirmation and Reassurance` 2827, `Self-disclosure` 1713, `Reflection of feelings` 1436,
  `Information` 1215, `Restatement or Paraphrasing` 1089. ✔ **Note the casing: `Reflection of
  feelings` (lowercase f)** on disk — a loader must match the exact string.
- **survey_score** per conversation: `seeker.{initial_emotion_intensity, empathy, relevance,
  final_emotion_intensity}` and `supporter.{relevance}`, all **strings "1".."5"** (not ints). ✔
  Some conversations lack `final_emotion_intensity` (seeker didn't finish post-survey).

### Parts directly useful for Pebble

1. **A small in-domain HUMAN intensity anchor (1–5), in Pebble's exact domain** — `D-D, D-H`.
   `survey_score.seeker.initial_emotion_intensity ∈ {1..5}` is a *human* continuous-ish distress
   rating attached to a real support conversation with a known *emotion_type*. This is the only
   acquired dataset where human intensity, human emotion category, and support-domain text co-occur.
2. **Conversation-level only, one intensity per conversation** — `D-D, D-H` (a constraint, not a gift):
   the 1–5 label is **pre-chat** and **whole-conversation**, NOT per-turn. Pebble scores *turn-level*.
   So the anchor is a *calibration distribution* check, not a turn-level regression label source.
3. **An 8-class strategy vocabulary + 3-stage framework** — `D-H` (candidate auxiliary head / not v1):
   exact strings above; the explore/comfort/action arc and per-utterance strategy tag are a
   *possible* future multi-task head but are **out of v1 scope** (v1 = emotion + severity only).
4. **CC-BY-NC-4.0 → research-arm-only** — `D-H` (hard constraint): confirmed on HF. ESConv may be
   used to **evaluate/calibrate/analyze** Pebble, and in the research/paper arm, but **cannot be
   shipped in, or used to train, the deployed child-facing model** without a commercial sub-license.
   This is stricter than a transfer-source like SemEval; it bars deployment, not just attribution.
5. **The intensity-correction lesson** — `D-D`: the authors had to manually fix 130 conversations
   where seekers inverted the 1–5 scale (read low=bad). A direct caution for any silver/self-report
   intensity: scale-direction confusion is a real, measured annotation failure mode.

### How each part helps Pebble succeed

- **Calibration slice for `severity`/`emotion` (D-D, D-H).** Build a held-out
  `eval/calibration/esconv_intensity.jsonl` of (situation + early seeker turns → human
  emotion_type + initial_emotion_intensity). Run Pebble's silver-labeled scorer (and the Gemini
  silver labeler) over the same text and report **Pearson/Spearman of predicted severity vs the
  human 1–5**, plus a confusion matrix of predicted-emotion vs human emotion_type. This is the
  concrete "check silver scores against real human intensity" the stub promises — and it lands in
  exactly Pebble's domain, unlike the adult-essay WASSA/SemEval transfer source (D-D).
- **Add `load_esconv()` to `external.py` (D-H).** Mirror `load_semeval_intensity`: read
  `ESConv.json` with **`encoding='utf-8'`** (the file is non-cp1252 — a naive `open()` crashes on
  Windows), cast `survey_score` strings → int, map `emotion_type` → the 12-label GoEmotions space
  (anxiety/nervousness→nervousness; depression/sadness→sadness; anger; fear; disgust; shame→
  embarrassment-ish — needs an explicit mapping table, several ESConv emotions have no clean
  GoEmotions twin), and **normalize intensity 1–5 → severity's regression range**. Emit the NC
  license + "research arm only, do NOT include in training mixes for the deployed model" in the
  docstring (D-H).
- **Scale-direction guard (D-D).** When normalizing the 1–5 intensity, assert direction (5 = most
  intense) and spot-check against `final_emotion_intensity < initial` for "improved" conversations;
  this is the programmatic version of the manual fix the authors had to do for 130 conversations.
- **Do NOT add a strategy head in v1 (D-H).** The 8-strategy vocab is real and clean, but v1 trains
  only emotion + severity; treat strategy as a documented v2 candidate, not scope creep.

### Child mental-health lens

- **Domain match, population mismatch.** ESConv text is genuinely emotional-support dialogue — far
  closer to Pebble's domain than Reddit/essay corpora. **But it is adult crowdworkers role-playing**
  help-seekers (AMT supporters/seekers, IRB-approved, paid). It is *not* children, and the
  problem/emotion vocabularies (job crisis, breakup with partner, alcohol abuse) are adult-framed.
  Transfer validity: use it to **calibrate the severity/emotion scale's behavior**, not as evidence
  Pebble's heads work on *child-register* text — that claim still needs a child-register slice.
- **Self-report intensity ≠ clinical severity.** The 1–5 is a momentary self-rated emotion intensity,
  not a clinical risk/severity construct (unlike C-SSRS). Mapping it to Pebble's `severity` head is a
  reasonable *calibration anchor* but the two scales measure different things; don't conflate "high
  intensity" with "high safety risk." (Contrast: D-C / C-SSRS severity is clinician-grounded.)
- **No safety signal.** ESConv has no suicidality/self-harm/abuse labels and no risk taxonomy. It
  cannot inform Pebble's `safetyFlag` (heuristic in v1 anyway) — purely an affect-intensity anchor.
- **Ethics / license.** CC-BY-NC means even research use must be non-commercial; for a product like
  Pebble, keep ESConv strictly in the research arm and document the wall. The authors obtained IRB
  approval and paid fair wages — a governance pattern worth citing, but the NC term is the operative
  constraint for Pebble.

### Limitations & open questions for Pebble

- **Contradiction vs the md stub's own numbers.** The stub says "1,300 convs / ~38K turns" and lists
  "8 support-strategy labels"; the *paper* reports **1,053 convs / 31,410 utterances**, **7** emotions,
  **5** problems. Both are right but for different snapshots — the stub describes the *release* Pebble
  acquired, the paper describes the smaller frozen corpus. A loader/eval must pick one and state it;
  silently quoting "1,300 convs" next to the paper's "29.8 avg utterances" would be an unverifiable
  composite. (Resolution: trust the on-disk `len=1300` for anything Pebble computes; cite the paper's
  31,410 only when citing the paper.)
- **No IAA on the affect labels.** Unlike FAIIR (paper 01), which ran a 12-CR × 40-conversation expert
  consensus and reported model-vs-expert F1, ESConv has **no inter-annotator agreement on emotion,
  intensity, or strategy** — the only κ (0.576) is for *quality-filter rules*, not label reliability.
  So ESConv's human intensity is a *single-rater self-report*, which caps how strong a "ground truth"
  calibration claim Pebble can make against it. This is a real gap: it's a calibration *reference*,
  not a gold standard.
- **Per-conversation, pre-chat granularity** clashes with Pebble's turn-level scoring (same mismatch
  flagged for FAIIR). The 1–5 intensity attaches to the *seeker's pre-chat state*, so the cleanest
  calibration input is the situation text + first seeker turn(s), not arbitrary mid-conversation turns.
- **Emotion-label mapping is lossy.** ESConv's emotions (anxiety, shame, disgust, nervousness, +
  release-only pain/jealousy/guilt) don't map cleanly onto Pebble's 12-label GoEmotions space; the
  mapping table is a judgment call that should be written down and reviewed, not auto-generated.
- **License blocks the obvious shortcut.** ESConv is the most in-domain corpus Pebble has, so the
  temptation is to *train* on it. CC-BY-NC forbids that for the deployed model. Open question worth
  resolving early: does the research/paper arm need a separate data-governance note so ESConv-derived
  numbers in a Pebble paper don't imply ESConv was in the training mix.
