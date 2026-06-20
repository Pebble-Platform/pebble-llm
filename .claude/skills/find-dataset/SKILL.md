---
name: find-dataset
description: "[Research] Find the dataset(s) a paper uses, check license + access gate, and try to download open ones into the gitignored data/<stream>/external/ (or draft a DUA request for gated ones). Use after a paper is identified as dataset-relevant. Triggers on: 'find the dataset', 'get the dataset', 'download the data for this paper', 'is this dataset available', 'how do we get this data'."
argument-hint: "<paper title / dataset name / URL>"
---

## Quick Summary

**Goal:** For a paper (or named dataset), locate the data, classify its access gate + license, and either **download it** (open) or **draft the request** (gated) — with provenance recorded.
**Workflow:** Identify dataset → locate source → classify gate + license → act (download / draft / record) → record provenance.
**Key rule:** Respect the gate. Open + license-compatible → download to `data/<stream>/external/<slug>/` (gitignored). Gated/DUA/private → **never circumvent**; produce the request steps instead. Always record license + citation.

---

## When to Use

- After `research-paper` / `analysis-paper` flags a paper whose data Pebble might reuse.
- When the user asks "can we get this dataset."

---

## Input / Output

**Input:** paper title / dataset name / URL.

**Output:** a status block (below) + either downloaded files under `data/<stream>/external/<slug>/` or a ready-to-send request draft. Optionally append the status block to `docs/dataset-acquisition-plan.md`.

## Step 1 — Identify the dataset
From the paper, name the dataset(s) and what labels they carry. If the paper introduces its own data, note that the **data-availability statement** is the authority.

## Step 2 — Locate the source
Search, in order: **HuggingFace Hub**, **Zenodo**, the paper's **GitHub / project page**, **Papers-with-Code**, then the **data-availability statement**. Capture the canonical URL and, for Zenodo/HF, the direct file/record API.

## Step 3 — Classify the access gate

| Gate | Signal | Action |
|------|--------|--------|
| **OPEN** | Direct download, permissive license | Download now (Step 4) |
| **GATED-DUA** | Form + signed Data Use Agreement, often academic-email/IRB | Draft the request (Step 4-alt); do not download |
| **PRIVATE** | "Controlled access", not released (e.g. FAIIR/KHP) | Record as not obtainable; suggest the closest open substitute |
| **PAYWALLED-PAPER** | Paper paywalled but data may still be open | Try Step 2 anyway; data ≠ paper access |

## Step 4 — Download (OPEN only)
Check the **license first** (`WebFetch` the Zenodo/HF page). Record name + terms (CC-BY → attribution; CC-BY-NC / research-only → **no deployment**; unknown → flag, do not assume permissive).

Then download into the **gitignored** data dir, mirroring `external.py`'s lazy-download pattern.
`<stream>` is the paper's stream: **`finetuning-message`** for text/NLP papers, **`voice`** for speech/paralinguistics papers (cf. `docs/papers/finetuning-message/` vs `docs/papers/voice/`).

```bash
mkdir -p data/<stream>/external/<slug>
curl -sL "<file-url>" -o "data/<stream>/external/<slug>/<file>"
```

- `data/<stream>/external/**`, `data/<stream>/raw/**` are gitignored — confirm before downloading; **never commit dataset files** (PII / mental-health content).
- Verify the download (row count, header, label distribution) and record the schema.
- If a HF dataset, prefer wiring a loader in `src/pebble_llm/data/external.py` over dumping a raw blob (note this as the follow-up; don't build it here unless asked).

## Step 4-alt — Draft request (GATED-DUA)
Do **not** attempt to obtain gated data without the agreement. Produce a ready-to-send request with `[BRACKETED]` fields (affiliation, academic email, intended use, storage, no-redistribution) — see `docs/dataset-acquisition-plan.md` for templates. Note the deployment-vs-research license constraint.

## Step 5 — Record provenance
Emit the status block:

```markdown
### Dataset — <name> (<paper short title>)
- **Status:** acquired | request-drafted | not-obtainable
- **Source:** <canonical URL>  ·  **Files:** `data/<stream>/external/<slug>/…` (if downloaded)
- **License:** <name> — <deployment allowed? attribution?>
- **Labels / schema:** <columns, label scheme, size>
- **Citation:** <required attribution>
- **Next step:** <loader to add / form to send / substitute to use>
```

---

## Key Rules

- **Respect the gate.** Open → download; gated → draft, never circumvent; private → record + substitute.
- **License before download.** Note deployment compatibility (CC-BY ok; NC/research-only = no shipping a trained model).
- **Never commit data.** `data/<stream>/external/**` is gitignored; mental-health/PII data stays out of git.
- **Provenance always.** License + citation + source recorded even for tiny downloads.
- **Prefer a loader.** For reusable data, wiring `external.py` beats a stray file — flag it as the follow-up.
