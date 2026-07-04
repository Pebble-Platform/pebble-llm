# Paper & reporting (capability)

> **Status:** authoritative for the plan, contributions, and result reports;
> the IEEE prose draft + ethics section (phase 6) not started.
> Source of record: `docs/papers/finetuning-message/PAPER-PLAN-text-ordinal-suicide.md`,
> `docs/reports/`, `docs/related-work-*.md`.
> Owned by `../changes/001-initial-build/phase-6-paper-and-ethics.md`.

**What it covers:** the IEEE paper (*Weakly-Supervised Augmentation for Ordinal
Suicide-Risk Classification: An Honest Gold-Holdout Study*) — its outline, the
**three methodological contributions** (CORN+GCE ordinal loss · label-shift
correction · ordinal-aware Confident Learning), related-work set (papers 42–57),
the ethics/provenance section, and the MD/HTML result reports that mirror the
experiment numbers.

**Result reports (number-synced to the 5-fold runs):**
`docs/reports/r2-method-improvements.{md? ,html}` (3 contributions + 2×2
ablation), `docs/reports/THESIS-OVERVIEW-vi.{md,html}` (whole-thesis overview),
`docs/reports/WEEKLY-REPORT-2026-06-27.{md,html}` (weekly), and the prior
`r2-ab-results` / `r2-finetuning-methods`. Every headline metric cites a runnable
source (I5).

**Binds invariants:** I5 (each headline number traces to a kernel+log),
I6 (metric tables report QWK/MAE alongside macro-F1).
