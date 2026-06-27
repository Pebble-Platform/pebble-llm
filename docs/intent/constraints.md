# Pebble-LLM (Ordinal Suicide-Risk research) — Intent & Constraints (intent layer)

> **Layer:** intent — changes rarely, only by deliberate human decision, never
> as a side effect of implementation (see `WORKFLOW.md`). If a code or spec
> change requires editing this file, stop: that is a human decision, not a PR
> detail.

This repo is a **research program**, not a product build. It asks one question:
**can LLM-generated weak labels honestly augment a small clinical gold set for
*ordinal* suicide-risk classification on social media — and how do we measure
that benefit without fooling ourselves?** The deliverable is an IEEE-class paper
(*Weakly-Supervised Augmentation for Ordinal Suicide-Risk Classification: An
Honest Gold-Holdout Study*) **plus the experiment infrastructure that makes
every reported number reproducible and defensible**. "Done right" means a
reviewer cannot find a number that is circular, leaked, or unrepeatable.

The predecessor framing — a deployable Pebble emotion/risk classifier
(`pebble-finetuning-strategy-v3.md`, `src/pebble_llm/serving/`) — is
**deliberately deferred**. v1 reuses public dataset labels and produces honest
research results first; production serving, a learned safety head, multi-LLM
ensemble relabeling, and real Δt wiring are out of scope until the research
validates quality. The classifier code remains as adjacent execution
infrastructure, not the current intent.

| | |
|---|---|
| **Scope (in)** | Ordinal suicide-risk text classification; weak-supervision & label-quality methods; the honest evaluation protocol; the paper and its reports. |
| **Scope (out)** | Production deployment; learned safety head; multi-LLM ensemble relabel; real-time Δt wiring — all "further work", not blocking. |
| **Hard constraint** | **Gold-holdout, always:** never report a metric that was trained and evaluated on the same label source. |
| **Non-negotiable** | **Research validity and clinical-data ethics outrank any metric.** A higher score obtained by leakage, by evaluating within-LLM, or on un-deidentified data is worth nothing. |

## Design constraints that drive everything

1. **Gold-holdout, always.** Training uses weak/LLM labels; evaluation uses
   *held-out clinical gold* (CSSRS) labels — and the two pools are disjoint by
   example. This **forbids** reporting a within-LLM validation number
   (e.g. 0.67) as a headline result: the honest gold number (0.385) is a
   different, smaller quantity, and conflating them is the central
   self-deception this study exists to exclude.

2. **Subject-level integrity.** Splits and folds are assigned by **user/subject**,
   never by post. This **forbids** random post-level splitting, which lets a
   single user's posts straddle train and test and silently inflates every
   metric. Same subject ⇒ same split, deterministically.

3. **Honest framing over SOTA.** The contribution is *methodological*, not a
   leaderboard win. "Beat the paper (0.5098 → 0.653)" is framed as a
   *comparable within-distribution protocol on our enriched 10k*, **not** the
   paper's exact gated benchmark. This **forbids** any claim of having run a
   benchmark or matched a population we did not actually reproduce.

4. **Reproducible by construction.** Every headline number comes from a
   **pinned stack + fixed seed + multi-fold run with reported std**, and traces
   to a runnable kernel and a retained log. This **forbids** floating
   dependency versions on GPU hosts and **forbids** quoting a single-run point
   estimate as a headline.

5. **Clinical-data ethics & provenance.** Suicide-risk corpora (r/SuicideWatch
   scrape, CSSRS gold) are **de-identified, content-filtered, and never
   committed**; their provenance (source, scrape method, filter rate) is
   documented. This **forbids** committing raw posts or PII, and **forbids**
   using any corpus without a provenance trail. `data/**/{raw,interim,processed,external}`
   stay gitignored.

6. **Ordinal-aware throughout.** Risk levels are ordered
   (Indicator < Ideation < Behavior < Attempt); losses, label-cleaning, and
   metrics must respect that order. This **forbids** evaluating the task as flat
   nominal classification — QWK and MAE are reported alongside macro-F1 on every
   model comparison, and a misclassification's *distance* matters.

The binding invariants derived from these constraints live in
[invariants.md](invariants.md) and are mirrored by the permanent invariant test
suite at `tests/invariants/`.
