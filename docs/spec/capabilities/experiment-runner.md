# Experiment runner (capability — STUB)

> **Status:** stub. Authoritative detail lives in `kaggle/`, `scripts/`,
> `docs/run-guideline.md`, and the pinned-stack notes in `progress.md` /
> `docs/decisions.md`.
> Owned by `../changes/001-initial-build/phase-0-foundations.md`.

**What it covers:** running reproducible experiments on free Kaggle GPU — the
**pinned stack** (`torch==2.5.1`, `torchvision==0.20.1`, `torchaudio==2.5.1`,
`xformers==0.0.28.post3`, `transformers==4.48.2`; Kaggle's default torch 2.10 is
broken for P100/NeoBERT), kernel push/pull via the kaggle CLI
(token at `~/.kaggle/access_token`; account must be **phone-verified** for
GPU+Internet), the 12h GPU cap discipline, env-gated config blocks
(`R2_BALANCE`, `R2_DATA`), and retaining run logs as the source of every number.

**Binds invariants:** I5 (pinned stack on GPU runs).
