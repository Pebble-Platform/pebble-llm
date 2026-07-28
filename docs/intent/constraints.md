# Pebble-LLM (ViEmoSpeech — Vietnamese SER corpus & bimodal method) — Intent & Constraints (intent layer)

> **Layer:** intent — changes rarely, only by deliberate human decision, never
> as a side effect of implementation (see `WORKFLOW.md`). If a code or spec
> change requires editing this file, stop: that is a human decision, not a PR
> detail.
>
> **Pivot 2026-07-04 (human decision):** the repo's prior programs — ordinal
> suicide-risk text classification and crisis-sensitive voice affect (the two
> IEEE thesis streams) plus the v1–v3 product classifier — are **archived in
> `archive/`** (fully recoverable; git history intact). Their methodology
> (honest gold-holdout evaluation + provenance discipline) is carried forward as
> the foundation of this program. *(The weak-label-teacher part was also
> inherited but later dropped — see §4 and ADR-003, pivot 2026-07-07.)*

This repo is a **research program**, not a product build. It builds
**ViEmoSpeech**: the first Vietnamese speech-emotion corpus that is
free-content, multi-class, distress-flagged, syllable-tone-annotated, and
clearly licensed — extracted from Vietnamese TV drama by a measured pipeline
(music removal → VAD → speaker-turn cutting → **human annotation** with LLM-
teacher suggestions → single-speaker filter), plus the **tone×emotion bimodal
SER method paper** built on it (hook: Vietnamese tones are phonation-heavy —
Shen, NAACL 2024 — so the semantic branch must carry more load than in non-tonal
SER). "Done right" means every released label traces to its **annotator id**,
every reported number traces to a run report, and nothing legally or ethically
unreleasable ever leaves the machine.

| | |
|---|---|
| **Scope (in)** | Corpus construction (extraction pipeline, human annotation protocol); dataset paper; tone×emotion bimodal SER method paper; recall-floored distress head. |
| **Scope (out)** | Production deployment; the archived text/voice thesis streams (revive = explicit human decision); full C-SSRS-style suicide labels on speech (ethically out of reach — distress proxy only). |
| **Hard constraint** | **Copyrighted media never leaves the machine:** episode files, clips, and full transcripts are never committed and never released. |
| **Non-negotiable** | **Legal/ethical releasability outranks corpus size.** A bigger corpus obtained by releasing copyrighted audio or unconsented content is worth nothing. |

## Design constraints that drive everything

1. **Media legality.** Source episodes are copyrighted. `data/**` stays
   gitignored; the releasable artifact is **features + timestamps + labels +
   speaker ids** (design doc §4 option B) under **CC-BY 4.0 declared from the
   first commit** — never raw audio, never full transcripts. This **forbids**
   committing or publishing episode media in any form.

   **Clarification (human decision 2026-07-28, ADR-005).** "Never leaves the
   machine" means **never committed and never released** — it does *not* forbid
   **streaming** a clip, over an authenticated tunnel to the machine's own local
   server, to a **named, invited annotator** for the sole purpose of labeling.
   That is private research use, not publication, and it is what I1 has always
   measured (`git ls-files data/` + release-manifest lint). The media stays on
   this one machine: no copy is created on third-party infrastructure, nothing
   is downloadable, and no annotator retains a copy. Everything else in this
   constraint stands unchanged — publishing, committing, bulk or contiguous
   access, open/crowd annotation, and any persistent off-machine copy remain
   **forbidden**.

2. **Single-speaker by construction.** A training clip carries one voice:
   utterances are cut at (VAD ∩ speaker-turn) boundaries, and clips flagged as
   containing multiple voices — by the **human annotator** (labeler `multi` flag
   / reject) — are dropped from the corpus. (Historically the flag was an OR of
   two LLM teachers; measured on ep01 that discipline raised teacher κ 0.584 →
   0.697 — kept as history.) It is load-bearing, not cosmetic.

3. **Speaker-disjoint splits.** Splits and folds are assigned by **speaker**,
   never by clip; **test-split speakers are disjoint from train** (ADR-002:
   held-out whole-series). Same voice ⇒ same split. This **forbids** random
   clip-level splitting.

4. **Human-annotated labels (pivot 2026-07-07, ADR-003).** Corpus labels are
   assigned by **humans** and are the **sole source of truth**; LLM-teacher
   output is retained only as an on-screen suggestion in the labeler, never as a
   training label or evaluation reference. This **forbids** treating teacher
   output as a corpus label. *(Superseded: the prior ≥2-LLM-teacher weak-
   supervision protocol — teacher disagreement, teacher-κ, "no train+eval on the
   same label source" — no longer applies; historical numbers stay in reports as
   history.)* Label reliability, when measured, is **inter-annotator κ/α (human–
   human)**; single-pass labeling is the current stage and carries no such number
   yet (known gap, ADR-003).

5. **Provenance by construction.** Every corpus label row carries its **author
   id** — annotator id + timestamp for the human label of record; model id for
   any retained teacher-suggestion column. The teacher-suggestion prompt stays
   versioned in git (`scripts/vietnamese-ser/m4_prompt.md`); every reported
   number traces to a report file generated by a committed script. This
   **forbids** hand-edited numbers and unattributed labeling for corpus data.

6. **Tone-aware by design.** Every utterance carries auto-generated
   syllable-level tone annotations and dialect metadata (Bắc/Trung/Nam —
   different tone systems); the corpus must stay analyzable for the
   tone×emotion question it exists to answer.

7. **Distress is a proxy, said plainly.** The distress flag means visible
   psychological distress in acted drama — **not** clinical suicide risk.
   Papers must state this; gold distress labels require clinical-partner
   adjudication and annotator-wellbeing safeguards (design doc §5).

The binding invariants derived from these constraints live in
[invariants.md](invariants.md). The archived thesis streams' invariant test
suite moved to `archive/tests/`; a corpus-specific suite is rebuilt as the
first change under `docs/spec/changes/`.
