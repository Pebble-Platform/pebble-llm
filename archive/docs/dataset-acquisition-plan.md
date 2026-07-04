# Dataset Acquisition Plan — Crisis / Safety Signal

> **Purpose.** Acquire a real crisis/safety-labelled dataset to train Pebble's safety head
> (a **v2 concern** — the safety head is *not* trained in v1; see [`decisions.md`](./decisions.md)).
> The FAIIR dataset (Kids Help Phone) is **not obtainable** — held in controlled-access storage,
> never released — so this targets the closest publicly-requestable substitutes.
>
> **Compiled:** 2026-06-09 · **Decisions resolved:** 2026-06-09

---

## Resolved decisions

- **Affiliation:** ✅ Academic / research affiliation available (can be DUA signatory, academic email).
- **Use intent:** **Both** deployed *and* research → license compatibility is the hard filter.

This splits the sources into two arms:

| Arm | Allowed sources | Why |
|-----|-----------------|-----|
| **Deployed model** | **CSSRS-Reddit only** (CC-BY-4.0) | Only license that permits serving a trained model |
| **Research / paper** | CSSRS-Reddit **+** DAIC-WOZ **+** SMHD/RSDD | Research-use DUAs allow training + eval, not deployment |

> ⚠️ Anything trained on DAIC-WOZ or SMHD/RSDD **must not ship in the served product** — their
> agreements restrict use to non-profit research. Keep the deployed checkpoint trained only on
> CSSRS-Reddit + the existing open data (GoEmotions, SemEval EI-reg) + Gemini silver labels.

---

## 1. CSSRS-Reddit (Gaur et al., WWW 2019) — ✅ ACQUIRED

- **Status:** **Downloaded** to `data/finetuning-message/external/cssrs/` (gitignored). No agreement required.
- **License:** **CC-BY-4.0** — open; commercial use, ML training, and **serving permitted** with
  attribution. This is the **deployment-compatible** crisis source.
- **What it is:** 500 Reddit users, gold-labelled by 4 practicing psychiatrists on the Columbia
  Suicide-Severity Rating Scale. Pairwise annotator agreement 0.79, group-wise 0.73.
- **Files** (`data/finetuning-message/external/cssrs/`):
  - `500_Reddit_users_posts_labels.csv` — 500 users, columns `User, Post, Label`; 5-label C-SSRS
    scheme: **Supportive / Indicator / Ideation / Behavior / Attempt**.
  - `suicidal_{ideation,behavior,attempt,indicator}.csv` — severity lexicon files.
- **Source:** [Zenodo record 2667859](https://zenodo.org/records/2667859).
- **Required attribution (cite when used):**
  > Gaur, M., Alambo, A., Sain, J. P., Kursuncu, U., Thirunarayan, K., Kavuluru, R., Sheth, A.,
  > Welton, R., Pathak, J. (2019). *Knowledge-aware Assessment of Severity of Suicide Risk for
  > Early Intervention.* The World Wide Web Conference (WWW '19).
- **Next step (code):** add a `load_cssrs_severity()` loader to
  [`src/pebble_llm/data/external.py`](../src/pebble_llm/data/external.py) following the existing
  `load_semeval_intensity` pattern (lazy-download from Zenodo + cache under `data/finetuning-message/external/`).
  Decide the C-SSRS→`severity` / safety-head mapping (5 ordinal levels → binary crisis flag and/or
  [0,1] severity).

---

## 2. DAIC-WOZ (USC ICT) — research arm only · ACTION REQUIRED (you must sign)

- **Status:** not started. **Research-only** — distributed solely to academics / non-profit
  researchers; **cannot back the deployed model.**
- **What it is:** clinical interview transcripts + depression (PHQ-8) labels; conversational
  (participant ↔ virtual interviewer "Ellie") — closer to Pebble's domain than Reddit.
- **Access:** complete + sign the EULA on the portal, submit from an **academic email address**.
  - Portal: <https://dcapswoz.ict.usc.edu/>
  - EULA: <https://www.ihp-lab.org/downloads/Extended-DAIC-BLANK_EULA.pdf>
- **Action:** download the EULA, fill institutional details, sign, submit from academic email.
  **~1–3 weeks** turnaround.

## 3. SMHD / RSDD (Georgetown IR Lab) — research arm only · ACTION REQUIRED (you must send)

- **Status:** not started. **Research-only** DUA; condition-diagnosis labels (SMHD: 9 conditions;
  RSDD: depression) + matched controls. Best as a **domain-adaptive pretraining corpus**, not a
  direct safety label. **Cannot back the deployed model.**
- **Access:** submit the data-request form → sign DUA.
  - Request portal: <https://ir.cs.georgetown.edu/resources/>
  - SMHD: <https://ir.cs.georgetown.edu/resources/smhd.html> · RSDD:
    <https://georgetown-ir-lab.github.io/emnlp17-depression/>
- **Action:** fill the request form (below). **~2–4 weeks** turnaround.

## 4. CLPsych UMD Reddit Suicidality — ❌ EXCLUDED

Shared-task-only; mandatory deletion of data **and trained models** after the workshop —
incompatible with keeping or serving a model. Pursue only if entering the
[CLPsych shared task](https://clpsych.org/shared-task/) as a standalone exercise.

---

## Ready-to-send request drafts

> Fill the `[BRACKETED]` fields and send from your **academic** email. These commit you to the
> research-only terms above — do not use the resulting data/models in the deployed product.

### A. DAIC-WOZ (after signing the EULA, email the cover note if requested)

```
Subject: DAIC-WOZ database access request — [YOUR NAME], [INSTITUTION]

Dear DCAPS / DAIC-WOZ data team,

I am [YOUR NAME], [ROLE — e.g. PhD student / researcher] at [INSTITUTION / LAB],
working under [PI / SUPERVISOR NAME]. I request access to the DAIC-WOZ database for
non-commercial academic research on conversational affect and depression-signal modelling.

I have completed and signed the End User License Agreement (attached) and will use my
institutional email ([YOU]@[institution].edu) for all data handling. The data will be
stored on [SECURE STORAGE LOCATION], accessed only by [NAMES/ROLES], used solely for
research, not redistributed, and not used to train any deployed/commercial system.

Thank you,
[YOUR NAME]
[INSTITUTION], [DEPARTMENT]
```

### B. SMHD / RSDD (Georgetown IR Lab data-request)

```
Subject: SMHD + RSDD dataset request — [YOUR NAME], [INSTITUTION]

Dear Georgetown IR Lab,

I am [YOUR NAME], [ROLE] at [INSTITUTION / LAB] ([PI / SUPERVISOR NAME]). I would like to
request access to the SMHD and RSDD datasets for non-commercial academic research on
mental-health language modelling (domain-adaptive pretraining and auxiliary classification).

Affiliation: [INSTITUTION], [DEPARTMENT]
Academic email: [YOU]@[institution].edu
Intended use: research only — model pretraining/evaluation for a research publication.
Data handling: stored on [SECURE STORAGE], not redistributed, access limited to
[NAMES/ROLES], not used in any deployed/commercial system.

I am ready to sign the Data Use Agreement. Please let me know the next steps.

Thank you,
[YOUR NAME]
```

---

## Update 2026-06-09 — enrichment-paper datasets (via find-dataset agent)

| Dataset | Status | Location | License → deploy? | Arm |
|---------|--------|----------|-------------------|-----|
| **WASSA empathy/distress** (Buechel 2018) | ✅ acquired | `data/finetuning-message/external/wassa_empathy/messages.csv` | CC-BY-4.0 → **YES** | deployed + research |
| **ESConv** (Liu 2021) | ✅ acquired | `data/finetuning-message/external/esconv/` | CC-BY-NC-4.0 → **NO** | research only |
| **RSD-15K** (2025) | ❌ not obtainable | promised repo unpublished (404) | unknown | — |
| **MentalBERT/RoBERTa weights** | available, not downloaded | HF soft-gate | CC-BY-NC-4.0 → **NO** | research only |

- **WASSA empathy** joins CSSRS-Reddit in the **deployed arm** (`distress/7 → severity`).
- **ESConv** = research-only calibration slice (human emotion + 1–5 intensity; NC license).
- **RSD-15K** substitutes if needed: UMD Reddit Suicidality (GATED-DUA, IRB) or SWMH (CC-BY-NC).

## Status checklist

- [x] CSSRS-Reddit downloaded (CC-BY, deployment-OK) → `data/finetuning-message/external/cssrs/`
- [x] WASSA empathy downloaded (CC-BY, deployment-OK) → `data/finetuning-message/external/wassa_empathy/`
- [x] ESConv downloaded (CC-BY-NC, research-only) → `data/finetuning-message/external/esconv/`
- [ ] Add `load_cssrs_severity()` loader + **ordinal** C-SSRS→severity/safety mapping (ordinal-loss lesson confirmed)
- [ ] Fill `load_wassa_empathy()` stub + add `load_esconv()` in `external.py`
- [ ] Sign + submit DAIC-WOZ EULA (academic email) — research arm
- [ ] Submit SMHD/RSDD request form + sign DUA — research arm
- [ ] Re-confirm: deployed checkpoint trained **only** on serving-compatible data (CSSRS + WASSA-empathy + open + Gemini)

---

## Sources

- [FAIIR — npj Digital Medicine (2025)](https://www.nature.com/articles/s41746-025-01647-6) — data not obtainable
- [CSSRS-Reddit — Zenodo record 2667859 (CC-BY-4.0)](https://zenodo.org/records/2667859)
- [Knowledge-aware Assessment of Severity of Suicide Risk (WWW 2019)](https://dl.acm.org/doi/10.1145/3308558.3313698)
- [DAIC-WOZ portal](https://dcapswoz.ict.usc.edu/) · [DAIC EULA](https://www.ihp-lab.org/downloads/Extended-DAIC-BLANK_EULA.pdf)
- [Georgetown IR Lab resources](https://ir.cs.georgetown.edu/resources/) · [SMHD](https://ir.cs.georgetown.edu/resources/smhd.html) · [RSDD](https://georgetown-ir-lab.github.io/emnlp17-depression/)
- [CLPsych shared task](https://clpsych.org/shared-task/) · [CLPsych DUA](https://clpsych.org/wp-content/uploads/2022/03/DUA_new.pdf)
