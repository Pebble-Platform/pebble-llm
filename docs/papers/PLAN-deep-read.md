# Plan — Deep research across the PDF papers, to move Pebble's open decisions

## 🎯 Goal (the research question, not just "summarize")

> **Which way should Pebble resolve each of its open methodological decisions, and what does the
> published evidence — read in full, validated, and cross-compared — say about each?**

"How can this paper help Pebble?" is the lens; the **deliverable** is *movement on a fixed set of
Pebble decisions* (the Decision Register below), backed by evidence that has been (a) validated for
provenance and (b) tested for transfer to Pebble's **child-facing, turn-level, public-label** regime.

A pile of 9 dossiers is the failure mode. The output is: 9 deep reads **+ a synthesis** that resolves
each decision with cross-paper agreement/contradiction made explicit.

---

## Decision Register — what every read must move

Grounded in [`../decisions.md`](../decisions.md) (v1 = reuse public labels; only `severity` +
`emotion` learned; **no safety head trained in v1**) and [`../related-work-enrichment.md`](../related-work-enrichment.md).
Each paper is read to move ≥1 of these. "Stage" = v1 (active now) or v2 (deferred, but evidence still banked).

| ID | Open decision | Stage | Informing papers |
|----|---------------|:-----:|------------------|
| **D-A** | **Encoder backbone** — justify NeoBERT vs ModernBERT vs MentalBERT/RoBERTa | v1 | 22-modernbert, (12-mentalbert ✓) |
| **D-B** | **MTL loss-balancing under imbalance** — static λ vs Kendall/GradNorm/PCGrad/Nash via LibMTL (Pebble's #1 novelty) | v1 | 18-wassa; (06–11 ✓) |
| **D-C** | **C-SSRS severity label scheme + loss** — ordinal/distance-aware (QWK/MAE) vs flat CE; bars to beat (52% acc / 0.75 wF1 / 47.8% macro-recall) | v1 (severity) / v2 (safety) | 15-cssrs-hybrid, 16-llm-cssrs, 17-rsd-15k, (14 ✓) |
| **D-D** | **Severity/energy regression** — continuous-head transfer source, metric (Pearson), domain-adapted init | v1 | 18-wassa, 19-ncuee, 23-esconv |
| **D-E** | **Staged fine-tuning / warm-start** — gradual unfreeze + discriminative LR + STLR vs RecAdam | v1 | 20-ulmfit, 21-recadam |
| **D-F** | **Domain-adaptive MLM pass** before head fine-tuning — worth it? | v1 | 19-ncuee, (12-mentalbert ✓, 01-faiir ✓) |
| **D-G** | **Threshold / recall-floor + calibration policy** | v2 | 16-llm-cssrs, 15-cssrs-hybrid, (01-faiir ✓) |
| **D-H** | **Datasets / calibration anchors** — substitutes + silver-score calibration slice | v1 | 17-rsd-15k, 23-esconv |

*(✓ = already deep-read; listed for synthesis cross-links.)*

---

## Current state (verified 2026-06-16)

`docs/papers/pdfs/` holds **20 PDFs**; each has a `docs/papers/NN-*.md`.

- **Already deep-read (10)** — have a `## Deep research — full-PDF read` section (gold standard = `01-faiir.md`):
  `01`, `06`, `07`, `08`, `09`, `10`, `11`, `12`, `13`, `14`.
- **Stub only — has PDF, not yet deep-read (9):**
  `15`, `16`, `17`, `18`, `19`, `20`, `21`, `22`, `23`.

> `02–05` are deep dossiers with **no PDF** → out of scope for "papers which have a PDF."

**Tooling de-risked:** local `pdftotext` **and** `pymupdf` both work → PDFs read from the local file,
no dependence on each being online (last session had to web-fetch arXiv; `pdftoppm` is still missing).

---

## Scope + depth triage (gap: equal depth for unequal papers)

**Scope = the 9 stub papers (15–23).** Depth is set by overlap % so effort tracks centrality:

| Depth tier | Papers | Treatment |
|---|---|---|
| **Full** (`01-faiir` depth: all 6 sub-parts, exact numbers, per-head actions) | 18 (42%), 15/16/17/19/23 (31%) | Complete deep read; these decide D-B/C/D/H |
| **Targeted** (focused on the one decision it moves; numbers still validated, but no exhaustive method dump) | 21 (15%), 22 (8%), 20 (4%) | D-A and D-E; read for the specific transferable mechanism, not full coverage |

---

## Fix for gap #1 — a dedicated deep-read agent (NOT `analysis-paper`)

`analysis-paper` is a **scorer**: 7-dim overlap %, **exactly one** best point, "compact analysis block"
(= the stub format in `22-modernbert.md`). Reusing it regresses to a stub. So:

**Create `.claude/agents/deep-read-paper.md`** — a new agent whose output contract **is** the 6-part
gold-standard section, with the per-paper loop rules baked in. Each paper is one sequential invocation
of this agent, given: the extracted PDF text, the target decision(s) from the register, the depth tier,
and the gold-standard `01-faiir.md` deep-research section as the format exemplar.

---

## The per-paper loop (sequential, 15 → 23)

For each paper `NN`:

1. **Extract** — `pdftotext docs/papers/pdfs/NN-*.pdf` → full local text.
2. **Read against its decision(s)** — not "summarize the paper" but "what does this say about D-x?":
   method, data, exact numbers (metrics, hyperparameters, splits, thresholds, table/section refs), limits.
3. **Two-part validation per load-bearing claim** (gap #4):
   - **Provenance** — does the number match the **published/venue** version? *(Conflict rule, gap #7:
     the published/venue version is authoritative; if the local PDF is a preprint that disagrees, use the
     published number and note the preprint delta.)*
   - **Transfer risk** — does the method's assumption hold in Pebble's regime (child-register, turn-level,
     public/silver labels, recall floor)? A perfectly-corroborated adult-Reddit number can still not transfer.
     This is the research-bearing check and is **stated explicitly** for every transferable point.
   - **Reproducible trace** (gap #8): record the search query + resolved URL next to each validated number.
4. **Write back** — append `## Deep research — full-PDF read (2026-06-16)` to `NN-*.md`, 6 sub-parts:
   - *Source-access note* — how the PDF was read + what was web-validated (with queries/URLs).
   - *What the paper actually does* — method / data / results, exact numbers + table/section refs.
   - *Parts directly useful for Pebble* — equations, hyperparameters, splits, thresholds, **tagged with the
     Decision ID (D-x) each moves**.
   - *How each part helps Pebble succeed* — concrete per-head / per-experiment / per-config action.
   - *Child mental-health lens* — transfer validity, risks, mitigations, ethics.
   - *Limitations & open questions for Pebble* — incl. at least one contradiction-or-gap vs the other papers.
5. **Verify gate** (gap #6 — quality, not presence). Pass only if:
   - every load-bearing number carries a table/section ref **and** a validation status (✔ corroborated / ≈ approximate / ✖ uncorroborated);
   - ≥3 transferable points (full tier) / ≥1 (targeted tier), each tied to a concrete Pebble artifact (a head, an experiment, a config) **and** a Decision ID;
   - transfer risk stated explicitly for each;
   - ≥1 contradiction-or-gap surfaced (vs another paper or vs Pebble's plan).
6. Update the progress tracker, then start the next paper.

---

## Synthesis stage (gaps #3, #9 — the actual research deliverable, REQUIRED not conditional)

After all 9, produce **`docs/papers/SYNTHESIS-deep-read.md`** containing:

1. **Claim/contradiction matrix, per pillar** — where the same-problem papers agree, disagree, and report
   conflicting numbers:
   - *C-SSRS (15/16/17 + 14 ✓):* which split? what accuracy/F1 bar actually holds? ordinal vs flat — who wins, on what metric?
   - *WASSA intensity (18/19):* Pearson bars, MTL weighting choices, domain-adapted init — consistent or not?
   - *Staged FT (20/21):* gradual-unfreeze vs RecAdam — when does each help?
   - *Encoder/domain (22/23):* ModernBERT vs NeoBERT trade; ESConv's role.
2. **Decision table** — one row per Decision Register ID: `decision → papers that inform it → what they
   collectively say → recommendation for Pebble → confidence + residual transfer risk`.
3. **Update** `related-work-enrichment.md` to point at the synthesis (mandatory, not "if material").

---

## Execution & autonomy

- **Step 0:** create `.claude/agents/deep-read-paper.md`.
- Then loop 15 → 23, **one sequential agent per paper** (depth per triage), main loop verifies each against
  the gate before launching the next.
- Then the synthesis stage.
- Update `README.md` table (depth → full-PDF read) at the end.
- **No commit unless asked**; report a summary.
- **Autonomy:** once approved, the whole run is autonomous (user is out). If a claim can't be validated
  online at all, keep the local-PDF fact, mark it ✖ uncorroborated, and flag it — don't stall.

---

## Deliverables

1. `.claude/agents/deep-read-paper.md` (new agent).
2. 9 updated paper files (`15–23`) each with a gold-standard deep-research section.
3. **`docs/papers/SYNTHESIS-deep-read.md`** — claim/contradiction matrices + decision table (the research output).
4. Updated `README.md` + `related-work-enrichment.md` pointers.

---

## Progress tracker

| # | Paper | Decisions | Depth | Deep-read | Validated (prov + transfer) | Written back | In synthesis |
|---|-------|-----------|-------|:---------:|:---------------------------:|:------------:|:------------:|
| 15 | cssrs-hybrid | D-C, D-G | Full | ✅ | ✅ | ✅ | ✅ |
| 16 | llm-cssrs-screening | D-C, D-G | Full | ✅ | ✅ | ✅ | ✅ |
| 17 | rsd-15k | D-C, D-H | Full | ✅ | ✅ | ✅ | ✅ |
| 18 | wassa-iitk-2021 | D-D, D-B | Full | ✅ | ✅ | ✅ | ✅ |
| 19 | ncuee-wassa-2023 | D-D, D-F | Full | ✅ | ✅ | ✅ | ✅ |
| 20 | ulmfit | D-E | Full | ✅ | ✅ | ✅ | ✅ |
| 21 | recadam | D-E | Full | ✅ | ✅ | ✅ | ✅ |
| 22 | modernbert | D-A | Full | ✅ | ✅ | ✅ | ✅ |
| 23 | esconv | D-H, D-D | Full | ✅ | ✅ | ✅ | ✅ |
| — | **SYNTHESIS** | all | — | — | — | ✅ | — |
