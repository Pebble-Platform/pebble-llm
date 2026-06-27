# Change 001 — Honest gold-holdout ordinal suicide-risk study (IEEE Bài 1)

**Status:** in progress (most phases substantially built before IDD init; this
folder formalizes them and names what remains for IEEE submission)
**Goal:** produce a defensible IEEE-class result — *LLM weak labels honestly
augment a scarce clinical gold set for ordinal suicide-risk classification* —
with every number reproducible, non-circular, and ethically sourced.
**Capabilities built:** all stubs in [../../capabilities/](../../capabilities/README.md)
except `serving` (deferred) and `voice-multimodal` (adjacent stream).

This is the project's first change under IDD, so its "delta" is the existing
research program, and its task breakdown is the phase files below. Execution
rules in [WORKFLOW.md](../../../../WORKFLOW.md). Source of record for status and
numbers: `PAPER-PLAN-text-ordinal-suicide.md`, `docs/tasks/r2-beat-paper-dual-report.md`.

**Ordering principle:** protocol/contract first (the *honest evaluation
protocol* and the leakage/holdout invariants are the integration seam — prove
them before any number counts); cross-cutting non-negotiables (subject-level
integrity, clinical-data ethics/de-identification) before the modeling they
gate; the highest-risk subsystem (label-quality / Behavior-class collapse) in
the middle behind a working eval skeleton; the paper write-up last.

| Phase | File | Goal | Status |
|---|---|---|---|
| 0 | [phase-0-foundations.md](phase-0-foundations.md) | Reproducible runner + leakage/holdout invariants encoded as permanent tests | in progress |
| 1 | [phase-1-data-and-labeling.md](phase-1-data-and-labeling.md) | CSSRS gold + scrape + LLM weak labels assembled, de-identified, provenance documented | mostly done |
| 2 | [phase-2-splits-and-holdout.md](phase-2-splits-and-holdout.md) | Subject-level splits + gold-holdout separation | mostly done |
| 3 | [phase-3-ordinal-modeling.md](phase-3-ordinal-modeling.md) | Dual-head + noise-robust ordinal loss (CORN+GCE) | mostly done |
| 4 | [phase-4-label-quality.md](phase-4-label-quality.md) | Ordinal-aware CL + label-shift correction + κ-vs-gold | partial |
| 5 | [phase-5-evaluation-and-ablation.md](phase-5-evaluation-and-ablation.md) | Within-dist CV + gold-holdout + baselines + ablation table | partial |
| 6 | [phase-6-paper-and-ethics.md](phase-6-paper-and-ethics.md) | IEEE draft + ethics/provenance + number-synced reports | not started |

As each phase ships under IDD it flips the corresponding `capabilities/*.md`
from stub to authoritative — phase "done" includes that update.

## Judgment calls vs the design docs (reverse by editing the phase files)

1. **Protocol-first, not data-first.** The paper plan opens with data; the phase
   ordering puts the *evaluation protocol + invariants* (phase 0) ahead of data,
   because every data/modeling number is meaningless until gold-holdout and
   no-leakage are mechanically guaranteed. Honest framing is the integration seam.
2. **Label-quality before final evaluation.** Behavior-class collapse (F1 0.18,
   the macro-F1 drag) is the riskiest open problem, so phase 4 precedes the
   final ablation table (phase 5) rather than being folded into it.
3. **Serving & voice excluded.** The strategy-v3 deploy work and the voice stream
   are not phases here — they are out of scope / adjacent per the intent layer.
4. **"Initial build" is partly retrospective.** Phases 1–3 are marked
   *mostly done* because the work predates IDD init; this folder records them as
   the audit trail and isolates the genuinely-remaining IEEE items in phases 4–6.

## Cross-phase open decisions (resolved ones become ADRs in ../../decisions/)

1. **Encoder choice** (MentalRoBERTa vs gated/NeoBERT) — *measurement-decided*;
   resolve when phase 5 baselines run on a common split. Blocked partly on a real
   gated encoder needing an HF token (noted as further work).
2. **Loss family** (CORN+GCE vs flat-CE vs dual CORAL) — phase 3/5 ablation
   decides; CORN+GCE currently leads on Behavior-F1 while holding ordinal QWK.
3. **Number synchronization** — 0.385 (rebalance) vs 0.357 (older spec) must be
   unified to the rebalance numbers before submission (phase 5/6). Non-engineering
   blocker: needs the author to pick the canonical run.
4. **κ-vs-gold overlap set** — computing Cohen's κ (phase 4) requires recovering
   the LLM-vs-gold overlap subset; owner + when in `docs/tasks/enrich-suicide-risk-dataset.md`.
