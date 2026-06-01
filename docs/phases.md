# Pebble Emotion Classifier — Phased Plan

> Derived from [`pebble-finetuning-strategy-v3.md`](../pebble-finetuning-strategy-v3.md).
> Each phase cites the strategy sections (`§`) it implements. Phases are gated —
> **do not advance until the exit criteria pass.** Several gates can *terminate or
> redirect* the project (taxonomy merge, viability drops, Gemini fallback), so they
> are deliberately front-loaded.

## At a glance

| # | Phase | Span | Primary output | Hard gate to exit |
|---|---|---|---|---|
| 0 | Pre-work & Foundations | Week 0 | Decisions locked, env pinned | Serving direction set; generator version tracked |
| 1 | Data Collection & Tooling | Weeks 1–2 | Silver labels flowing, annotation tool | `training_data` live; energy/severity check run |
| 2 | Taxonomy & Viability Gates | Week 3 | Final taxonomy; head decisions | Taxonomy frozen; isolation/receptivity decided |
| 3 | Human Annotation | Weeks 4–5 | Protocol A + B sets | Protocol B α ≥ 0.6 per dimension |
| 4 | Safety Data | Week 6 | Augmented safety positives | Clinical review complete |
| 5 | Dataset Prep & Transfer Pre-train | Week 7 | Splits + pretrained emotion head + Gemini baseline | Splits leak-free; baseline bar set |
| 6 | Multi-task Training & Eval | Week 8 | Trained model (≥3 seeds), serving spike | Beats Gemini baseline; §7 targets |
| 7 | Serving Build & Integration | Week 9 | `/classify` in staging + shadow | E2E + safety scenarios pass |
| 8 | Iteration Buffer | Week 10 | Fixes for missed targets | Eval/latency targets met |
| 9 | Staged Rollout | Weeks 11–14 | 10% → 50% → 100% | No safety regression; path shift < 10% |
| 10 | Monitoring & Iteration | Ongoing | Drift dashboards, retrain cadence | (continuous) |

**Critical path & fallback ladder:** NeoBERT-GPU → ModernBERT (proven CPU/ONNX) →
Gemini Flash-Lite backup. The Week-8 gate (Phase 6) is the decision point; the
Gemini-Lite baseline from Phase 5 makes it evidence-based.

---

## Phase 0 — Pre-work & Foundations (Week 0)

**Objective:** Clear every blocker that would invalidate the 14-week plan if
discovered mid-flight. Nothing in Phases 1–9 should start until these are settled.

**Tasks**
- **Decide NeoBERT serving direction** — GPU FP16 baseline (L4, Cloud Run vs Vertex)
  vs CPU/ONNX ambition; re-derive the cost model at 500 DAU. *(§4, OQ6)*
- **Pin the silver-label generator and track its version** on every row, so a future
  generator change can be checked for drift before mixing labels. *(OQ5)*
- **Source the clinical reviewer** (C-SSRS/Columbia familiarity; start Week 1, contract by Week 3). *(OQ2)*
- **Decide annotation hiring channel**, budget 3 raters. *(OQ3)*
- **Engineering foundation:** `uv sync`; **pin NeoBERT to an exact revision** and
  **vendor** the modeling code; confirm GPU for training (FlashAttention). *(§6.1 Step 0)*

**Owners:** Product + AI eng (decisions), AI eng (env).

**Exit gate:** serving direction + budget approved; silver-label generator confirmed
and version-tracked; clinical + annotation channels in motion; model revision pinned & vendored.

**Risk if skipped:** serving cost discovered too late to change architecture; an
untracked generator change makes silver labels mixed-provenance.

---

## Phase 1 — Data Collection & Tooling (Weeks 1–2)

**Objective:** Start accumulating training data and build the means to label it. *(§5.2)*

**Tasks**
- Stand up the `training_data/{docId}` Firestore collection, separate from production
  messages. Store `(input, target)` + metadata: sessionId, userId, timestamp,
  **generator model version**, fallback flag (exclude fallbacks). Begin Day 1 of Phase 1.
- Input = current message + last 3 messages, interleaved. Target = the 6 dims
  (exclude themeRepetition, sessionTrajectory).
- Build the annotation tool (admin dashboard page): sample → show message+context →
  sliders + emotion dropdown → submit. Two modes: pre-filled (A) / blank (B). ~2–3 days.
- **Energy/severity independence check** once ~1K labels exist: Pearson/Spearman over
  the collection. **|r| > 0.7 → drop the energy head** (cut K in the score head). *(§5.2)*

**Owners:** Backend eng (collection + tool), AI eng (independence check).

**Exit gate:** silver labels flowing with provenance metadata; tool supports both
protocols; energy head decision recorded.

**Risk:** the 5K target may not exist on schedule — early-phase DAU is *tens*, not 500.
**Gate the training start on accumulated volume, not the calendar** (§5.2); fallback to
lean harder on external transfer data. Sharper on the data-hungry NeoBERT path.

---

## Phase 2 — Taxonomy & Viability Gates (Week 3)

**Objective:** Freeze the taxonomy and decide which subjective dimensions survive —
*before* the expensive annotation pass. Changing these later forces a pipeline restart. *(§3.2–3.4)*

**Tasks**
- **Taxonomy pilot:** 100 messages, stratified by severity quartile, 3 annotators
  label from scratch (no Gemini pre-fill). Compute pairwise confusion.
  **Rule:** any two labels confused > 40% → merge (likely frustration/anger,
  anxiety/confusion, exhaustion/sadness). Finalize; update the GoEmotions mapping. *(§3.2)*
- **socialIsolation gate:** Krippendorff α on the pilot. < 0.5 → drop, use keyword
  heuristic in the Decision Engine. 0.5–0.6 → keep with relaxed MAE 0.25. ≥ 0.6 → normal. *(§3.3)*
- **receptivity gate:** same α thresholds; < 0.5 → prefer collapsing to binary
  venting/seeking head. Treat DailyDialog act-labels as noisy. *(§3.4)*

**Owners:** 3 annotators (2 days), AI eng (1 day).

**Exit gate:** taxonomy frozen (`src/pebble_llm/data/taxonomy.py` updated);
isolation/receptivity dispositions recorded in `configs/config.yaml > model.score_dims`.

**Decision point:** these gates can permanently remove model heads. Lock before Phase 3.

---

## Phase 3 — Human Annotation (Weeks 4–5)

**Objective:** Produce the human-corrected training augment (A) and the unanchored
test set (B). *(§5.2)*

**Tasks**
- **Protocol A (Week 4)** — 500 anchored (Gemini pre-filled, annotators adjust).
  **Oversample the 0.5–0.8 severity band (~150, human-annotated, not silver)** — the
  moderate blind spot (§8.3). Human label replaces silver where 2 annotators agree on a
  correction (>0.15 deviation, or emotion disagreement); else adjudicate. 2 annotators ok.
- **Protocol B (Week 5)** — 500 unanchored (blank UI), 3 annotators score from scratch.
  Measure Krippendorff α (continuous) + Cohen κ (categorical). **α < 0.6 on any
  dimension → revise guidelines and re-annotate.** Compute Gemini-vs-human correlation
  per dimension (silver-label quality measure).
- Enforce **annotator wellbeing** throughout (volume caps, rotation off safety queue,
  EAP, no-penalty opt-out). *(§5.2)*

**Owners:** 2 annotators (A), 3 annotators (B), AI eng.

**Exit gate:** Protocol B α ≥ 0.6 on all retained dimensions; both sets finalized;
silver-label trust quantified.

---

## Phase 4 — Safety Data (Week 6)

**Objective:** Build a usable safety-positive set from a ~1–2% base rate. *(§5.4)*

**Tasks**
- **Layer 1:** confirm production positives via a dedicated (separate) annotator. ~50–150.
- **Layer 2:** 2–3 adversarial rephrasings per positive (intent-preserving), peer-reviewed. ~100–450.
- **Layer 3:** Gemini Pro synthetic generation across demographics/styles/explicitness,
  **every example reviewed by the licensed clinician** before training. ~200–300.
- **Layer 4 (if approved):** CLPsych / UMD Reddit (IRB/DUA). Layers 1–3 must suffice if not.
- Clinician reviews the **Layer-3 methodology before generation**, not just outputs.

**Owners:** AI eng (Layers 1–2), clinical reviewer (Layer 3 + methodology).

**Exit gate:** ~350–900 positives (≈7–15% rate); clinical sign-off recorded.

**Risk:** model learns synthetic *style*, not crisis signal — the Protocol B test set is
100% real production data to catch this. *(§5.4)*

---

## Phase 5 — Dataset Prep & Transfer Pre-training (Week 7)

**Objective:** Assemble final splits, warm-start the emotion head, and set the
fallback bar. *(§5.1, §5.5, §6.1 Step 1)*

**Tasks**
- Filter/merge silver + Protocol A + safety layers + transfer examples. **User-level
  split** (deterministic userId hash), **then** stratify by severity quartile within
  split-assigned users (never the reverse — leakage). Export to `data/processed/`. *(§5.5)*
- **GoEmotions emotion-head pre-training:** map 27→taxonomy; freeze encoder 2 epochs,
  unfreeze 1–2 at LR 1e-5. *(§6.1 Step 1)*
- **Run a quick Gemini-Lite SFT baseline** to set the bar the NeoBERT run must beat. *(§10 W7)*

**Owners:** AI eng (3 days).

**Exit gate:** leak-free splits (test = 100% Protocol B); pretrained emotion-head
checkpoint; Gemini-Lite baseline metrics on the Protocol B set.

---

## Phase 6 — Multi-task Training & Evaluation (Week 8) — **the decision gate**

**Objective:** Train the multi-task NeoBERT, evaluate honestly, and decide NeoBERT vs
fallback. *(§6.1 Steps 2–3, §7, §5.3)*

**Tasks**
- **Multi-task fine-tune:** emotion head from Phase 5; score/safety heads random.
  Encoder freeze 1–2 epochs then unfreeze (LR 5e-6 encoder / 2e-5 heads). Loss weights
  score×1, emotion×1, safety×2; safety pos-weight 10×. Early stop (patience 3). FP16.
  **≥3 seeds; report mean ± std.** Watch the train/val gap (overfitting, not under). *(§6.1 Step 2)*
- If per-head metrics diverge (emotion improves, severity stalls) → switch to
  uncertainty weighting (Kendall) or GradNorm. *(§6.1 multi-task caveat)*
- **Hard-example mining:** top 5% val loss + *all* safety false negatives → annotate →
  1 epoch at LR 1e-6. *(§6.1 Step 3)*
- **Serving spike (timeboxed):** Track A (GPU FP16) stand-up + Track B (CPU/ONNX)
  feasibility. *(§4, §6.1 Step 4)*

**Owners:** AI eng (4–5 days).

**Exit gate (§7 targets on Protocol B):** severity MAE < 0.15 · emotion macro-F1 > 0.65
· safety recall > 0.95 (else safety output supplementary only) · 0.5–0.8 band MAE ≤ 0.15
(else **do not deploy**) · latency p95 < 300ms.

**Decision:** if NeoBERT underperforms the Gemini-Lite baseline or serving is
intractable → **pivot to the backup path** (recovers most of the ~2 extra weeks). *(§5.3, §10)*

---

## Phase 7 — Serving Build & Integration (Week 9)

**Objective:** Productionize the chosen serving track and integrate end-to-end. *(§6.1 Step 4–5)*

**Tasks**
- Finalize Track A or B; build the `/classify` container (FastAPI + Torch/ONNX),
  `min-instances=1` to kill cold starts. Deploy to staging.
- Wire the backend: classifier → Decision Engine → Gemini (sequential). Set up
  **shadow scoring** (10% traffic, scores computed not used). *(§8.2)*
- E2E tests across all four routing paths + safety scenarios (union-of-triggers: classifier
  flag ∪ keyword regex ∪ generation heuristic). *(§8.1)*
- Experiment tracking: every deployed version traces to data snapshot + config +
  Protocol B eval. **No deploy without a completed Protocol B eval.** *(§6.1 Step 5)*

**Owners:** Backend + AI eng (4–5 days).

**Exit gate:** staging clean; shadow scoring live; rollback path (revision repoint) verified.

---

## Phase 8 — Iteration Buffer (Week 10)

**Objective:** Absorb missed eval/latency targets without derailing rollout. *(§10 W10)*

**Tasks:** second training run / task-weighting change / serving-track switch as needed.

**Owners:** AI eng.

**Exit gate:** Phase 6 and Phase 7 gates all green.

---

## Phase 9 — Staged Rollout (Weeks 11–14)

**Objective:** Ship gradually with safety monitoring at each step. *(§10 W11–14, §8.2)*

**Tasks**
- **Week 11 — 10%.** Shadow scoring active. Monitor safety agreement, path distribution,
  serving health, latency.
- **Week 12 — 50%.** Proceed only if **no safety regressions and path-distribution shift
  < 10% relative.**
- **Weeks 13–14 — 100%.** Shadow scoring continues 2 more weeks.

**Shadow comparison thresholds (§8.2):** classifier vs generator severity disagreement
> 0.3 for > 5% weekly → investigate; LIGHTEN spike > 10% relative → suspect severity
underscoring. Treat divergence as a *signal*, never proof (different model families).
Discontinue shadow only when severity agreement within 0.2 for > 90% **and** the latest
human audit is within target — never on generator agreement alone.

**Owners:** AI eng + product.

**Exit gate:** 100% traffic, no safety regression, path shift within bounds.

---

## Phase 10 — Monitoring & Iteration (Ongoing)

**Objective:** Keep the classifier healthy against drift. *(§9)*

**Monitoring:** classifier–generator drift (shadow → spot-checks); safety-flag agreement
across the three triggers (weekly review); serving health (p95/p99, errors, GPU util,
cold starts, OOM); fallback rate vs baseline; per-dimension score histograms (weekly);
user-facing metrics (session length, return rate, path distribution).

**Retraining cadence:**
- **Monthly:** append new silver labels; retrain if the dataset grew > 20%.
- **Quarterly:** fresh **human** annotation (200–500, Protocol B method) — the
  irreducibly manual recalibration step.
- **Ad-hoc:** immediately if production safety recall < 0.95, a critical safety
  misclassification surfaces, or (backup path) JSON validation failure > 5% sustained.

**Automation stance (OQ4):** automate *retraining* after ~3 clean cycles; keep
*deployment* human-gated indefinitely for any safety-bearing version — never auto-deploy
without re-verifying safety recall on a *fresh human* test set.

---

## Cross-phase gates (the ones that can change the project)

| Gate | Phase | Trigger | Consequence |
|---|---|---|---|
| Energy independence | 1 | \|r\| > 0.7 | Drop energy head |
| Taxonomy merge | 2 | confusion > 40% | Merge labels, restart mapping |
| socialIsolation viability | 2 | α < 0.5 | Drop → keyword heuristic |
| receptivity viability | 2 | α < 0.5 | Collapse to binary / heuristic |
| Annotation agreement | 3 | α < 0.6 | Revise guidelines, re-annotate |
| Safety recall | 6 | < 0.95 | Safety output supplementary only |
| Moderate-band MAE | 6 | > 0.15 in 0.5–0.8 | **Do not deploy** |
| NeoBERT vs baseline | 6 | loses to Gemini-Lite / serving intractable | **Fall back** down the ladder |
| Rollout safety/path | 9 | regression or shift > 10% | Halt rollout |
