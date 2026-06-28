# Paper 55 — CLPsych 2025 Shared Task: Capturing Mental Health Dynamics from Social Media Timelines

> Enrichment set · Pillar (continuous severity/wellbeing + safety). Analysis depth: ACL Anthology
> landing page + overview/system/baseline abstracts (overview & system PDFs are binary-unreadable via
> WebFetch; numbers below are corroborated across the system paper 1.24 and the organizer baseline
> arXiv:2504.14066). Compiled 2026-06-26.

## Bibliographic info
- **Title:** Overview of the CLPsych 2025 Shared Task: Capturing Mental Health Dynamics from Social Media Timelines
- **Authors / Year / Venue:** Talia Tseriotou, Jenny Chim, Ayal Klein, Aya Shamir, Guy Dvir, Iqra Ali, Cian Kennedy, Guneet Singh Kohli, Anthony Hills, Ayah Zirikly, Dana Atzil-Slonim, Maria Liakata — 2025 — Proc. 10th Workshop on Computational Linguistics and Clinical Psychology (CLPsych 2025 @ NAACL), Albuquerque.
- **Link:** [aclanthology 2025.clpsych-1.16](https://aclanthology.org/2025.clpsych-1.16/) (overview) · organizer baseline [arXiv:2504.14066](https://arxiv.org/abs/2504.14066) · example system [2025.clpsych-1.24](https://aclanthology.org/2025.clpsych-1.24/)
- **Pebble pillar:** the closest *published benchmark* to Pebble's continuous severity/energy head + safety head together — a continuous 1–10 wellbeing regression scored ALONGSIDE evidence/rationale span extraction over the same mental-health posts.
- **This is the SHARED-TASK OVERVIEW paper**, not an individual system. It defines the task, dataset, metrics, and baselines; the per-team methods (RoBERTa, Random Forest, LLM pipelines) live in the ~14 sibling system papers (e.g. 1.24, 1.25) and the organizer baseline (2504.14066).

## Summary
Four subtasks over temporally-ordered Reddit user timelines, structured by the **MIND framework**
(Atzil-Slonim 2024 — self-states as combinations of Affect / Behavior / Cognition / Desire):
**(A.1) Evidence extraction** — text spans reflecting adaptive vs. maladaptive self-states; **(A.2)
Well-Being Score prediction** — a **continuous 1–10 score** per post based on social/occupational/
psychological functioning; **(B) post-level** and **(C) timeline-level summarization** of self-state
dynamics. 14 teams completed it. A.1 is scored by **recall / max-pairwise BERTScore**; A.2 by
**MSE** (lower = better). Data is **human-annotated** (MIND), not LLM-labeled.

## Overlap with Pebble — 54% (adjacent)
`D1=2, D2=2, D3=0, D4=0, D5=0, D6=1, D7=2` → (3·2 + 2·2 + 1·0 + 2·0 + 2·0 + 2·1 + 1·2)/26 = 14/26 = **54%**
- **Closest on:** D1 (continuous regression head + a second heterogeneous span/evidence output over the same posts — the structural twin of Pebble's continuous-severity + safety pairing) and D2 (mental-health social-media text). D7 also strong: the organizer baseline and several systems are **RoBERTa**, an encoder in Pebble's family/size band.
- **Why not higher:** it is a multi-subtask *benchmark*, not a single shared-`[CLS]` MTL model. No GoEmotions/intensity emotion-transfer (D3=0), labels are human not teacher-LLM silver (D4=0), and there is no principled MTL loss balancing (D5=0); the "safety" link (D6=1) is only that A.1 is recall-headlined and the domain is risk-adjacent — there is no explicit crisis recall floor as a training objective.

## Best point — Baseline to beat / Dataset to reuse
The **A.2 well-being regression is a directly transferable template + eval target for Pebble's
continuous severity/energy head**: a 1–10 functioning score per post, evaluated by **MSE**, with a
published organizer/system baseline of **MSE ≈ 2.994 (Random Forest), and an LLM zero-shot upper-bound
that is *worse* (DeepSeek-7B MSE ≈ 6.610)** — i.e. on this continuous mental-health regression a small
supervised model beats a 7B LLM.
- **How to apply to Pebble:** treat A.2 as a held-out continuous-head benchmark — train Pebble's
  severity/energy head to predict the 1–10 wellbeing score and **report MSE against the 2.994 baseline
  (plus MAE + Pearson/Spearman for ordering)**; the RF-beats-DeepSeek gap is the citation that a
  ~250M supervised encoder is the right tool for continuous affect regression, and that the
  Gemini-teacher's *continuous* scores must be audited (an LLM here scored MSE 6.6, not free quality).

## Dataset
- **Source / size:** Reddit user **timelines** (temporally-ordered posts). The released training set is
  small — reported as **~30 timelines / 343 posts**, each post carrying *adaptive evidence,
  maladaptive evidence, summary, and a 1–10 well-being score*. Test set additional.
- **Access status (a sibling `find-dataset` agent is verifying):** the data is **gated behind
  shared-task registration** — per the CLPsych site, participation requires a **team registration form
  + per-member individual registration**, and data is released to registrants ("guidelines on accessing
  sample data" → "training data released"). I could NOT confirm from the public pages whether a signed
  **DUA / ethics-IRB approval** is additionally required, but CLPsych shared tasks historically gate
  Reddit/TalkLife clinical data behind a DUA — **assume a DUA/application is needed; not an open
  download.** This is the relevant flag for the find-dataset hand-off.

## Caveats
- **Overview + both PDFs (1.16, 1.24) are binary-unreadable via WebFetch** — all numbers (MSE 2.994 vs
  DeepSeek 6.610; A.1 recall 0.579–0.602; 30 timelines/343 posts; BERTScore metric) come from the
  system-paper 1.24 abstract, the organizer baseline arXiv:2504.14066, and search-result extracts, not
  from a full read of the overview itself → lowers confidence on the *exact* official baseline numbers
  and on whether the headline A.2 metric is MSE alone vs. MSE+correlation.
- **Overview vs. system distinction:** the 2.994 MSE is one *team's* RF result (1.24); the official
  organizer baseline number for A.2 specifically was not separable from the overview without the full
  PDF — verify before quoting "the baseline" in a Pebble paper.
- **D4/D5/D6 firmly low:** human-annotated MIND labels (no silver distillation), no MTL loss balancing,
  no crisis recall-floor objective — so this paper informs Pebble's **continuous-head eval/dataset**
  side, not its distillation or loss-balancing design.
- **Register mismatch:** adult Reddit timelines; Pebble targets children, turn-level — the *1–10
  functioning construct and MSE protocol* transfer, the absolute numbers do not.
