# Paper 21 — Recall and Learn: Fine-tuning with Less Forgetting (RecAdam)

> Enrichment set · Pillar 6 (staged fine-tuning). Analysis depth: abstract + method summary. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Chen, Hou, Gao, Jiang, et al. EMNLP 2020.
- **Link:** [arXiv:2004.12651](https://arxiv.org/pdf/2004.12651) · open
- **Pebble pillar:** catastrophic-forgetting mitigation during the unfreeze stage.

## Summary
A fine-tuning optimizer that mitigates catastrophic forgetting via (1) a quadratic L2 penalty anchoring weights to the pretrained init ("Pretraining Simulation," EWC-style, no original data needed) plus (2) an annealing coefficient that ramps the downstream loss in gradually ("Objective Shifting"). On GLUE, BERT-base matched fine-tuned BERT-large.

## Overlap with Pebble — 15% (peripheral)
`D1=0, D2=0, D3=0, D4=0, D5=1, D6=0, D7=2` → (2·1 + 1·2)/26 = 4/26 = **15%**
- **Closest on:** D7 (BERT encoder fine-tuning, same as NeoBERT) and partial D5 (principled annealed weighting between a "recall" objective and the downstream objective, framed as MTL).

## Best point — Method to adopt
Pretraining-anchor penalty + objective annealing → fine-tune with substantially less forgetting.
- **How to apply to Pebble:** Swap AdamW for RecAdam during the unfreeze stage so NeoBERT retains its pretrained/GoEmotions-warm-started representations while adapting to the ~5K Gemini silver labels — a principled, drop-in alternative/complement to the hand-tuned freeze→unfreeze ramp; addresses low-resource overfitting/forgetting.

## Dataset
Method paper — no dataset to acquire (GLUE).

## Caveats
Abstract/method-summary only; exact penalty formula, annealing schedule, and per-task GLUE numbers not retrievable → D5 scored on the mechanism, not verified equations. Single-task in the original work and head/balancing-agnostic — it does **not** address Pebble's core heterogeneous-head balancing problem; a complementary optimizer, not a substitute for Kendall/GradNorm.

## Deep research — full-PDF read (2026-06-16)

> Read end-to-end from the local PDF `pdfs/21-recadam.pdf` (arXiv:2004.12651v1, 27 Apr 2020).
> Published as **EMNLP 2020** (ACL Anthology `2020.emnlp-main.634`). The ACL landing page exposes
> only the abstract (the +1.1% / +1.7% figures were re-confirmed via web search against the
> published-version description, status ✔); the equations, Algorithm 1, the γ=5000 penalty and the
> k/t0 grids are verbatim from the local PDF §3–§4 and **independently corroborated** against the
> author's released optimizer config (`Sanyuan-Chen/RecAdam/run_glue_with_RecAdam.py`), which ships
> exactly `recadam_pretrain_cof=5000.0`, `recadam_anneal_fun='sigmoid'`, `recadam_anneal_k=0.5`,
> `recadam_anneal_t0=250`, `recadam_anneal_w=1.0`, and random init by default
> (`--start_from_pretrain` to override). This section focuses depth on **D-E** (staged FT / warm-start
> with less forgetting) and only adds what the stub above does not already cover.

### Source-access note

- **How read:** `pdftotext pdfs/21-recadam.pdf -` → full method (§3.1–§3.3), Algorithm 1, all of §4 incl. Table 1 / Table 2 / Figure 2.
- **Web-validated numbers (status ✔):** "RecAdam with BERT-base outperforms vanilla fine-tuning on 7 of 8 GLUE tasks, +1.1% average median; +1.7% average on the four small (<10k) tasks." — query *RecAdam "Recall and Learn" EMNLP 2020 GLUE BERT-base average improvement 1.1%* → https://aclanthology.org/2020.emnlp-main.634/ and the GitHub README https://github.com/Sanyuan-Chen/RecAdam .
- **Config corroboration (status ✔):** γ=5000, sigmoid anneal, k=0.5, t0=250 default — https://github.com/Sanyuan-Chen/RecAdam/blob/master/run_glue_with_RecAdam.py .
- **Conflict rule:** local PDF is v1 preprint; the published EMNLP abstract + author code agree with every load-bearing number used here. No preprint/published delta found on the figures cited.

### What the paper actually does

**The mechanism (D-E core).** RecAdam reframes "fine-tune without forgetting" as a 2-task problem and *anneals* between them. Two pieces:

1. **Pretraining Simulation (recall, EWC-style, data-free).** It approximates the unavailable source-task loss `Loss_S = −log p(θ|D_S)` by a quadratic anchor to the pretrained weights θ*. Starting from EWC's Laplace/Fisher diagonal approximation `(θ−θ*)ᵀH(θ*)(θ−θ*) ≈ NΣ_i F_i(θ_i−θ*_i)²`, it adds a **stronger assumption** — each diagonal Fisher value `F_i` is *independent of the parameter* — collapsing the per-weight Fisher into a single scalar. Result (§3.1):
   `Loss_S ≈ ½·γ·Σ_i (θ_i − θ*_i)²`, with `γ = ½·N·F̄`. **Every weight is anchored at the same rate** — that is the key simplification vs. EWC (no Fisher matrix, no pretraining data). γ=5000.
2. **Objective Shifting (learn, the anneal).** Replace the fixed MTL mixing weight λ in `Loss_M = λ·Loss_T + (1−λ)·Loss_S` with a **time-dependent sigmoid annealing coefficient**:
   `Loss = λ(t)·Loss_T + (1−λ(t))·Loss_S`,  `λ(t) = 1 / (1 + exp(−k·(t − t0)))`
   where `t` = optimizer update step, `k` = annealing rate, `t0` = annealing midpoint step. Early training: λ(t)≈0 → mostly *recall* the pretrained init; late training: λ(t)≈1 → mostly *target task* (the final objective is pure `Loss_T`). **Fine-tuning and MTL are the two limits**: k→∞ recovers vanilla sequential fine-tuning; k→0 recovers static-λ multi-task learning at λ=½. Grids swept: `k ∈ {0.05, 0.1, 0.2, 0.5, 1}`, `t0 ∈ {100, 250, 500, 1000}`.
3. **RecAdam optimizer (the decoupling, §3.3 + Algorithm 1).** Critically, the anchor is **decoupled** from Adam's adaptive moments — same insight as AdamW vs. L2. Per Algorithm 1, the *naive* in-loss version (Line 6) is `g_t ← λ(t)∇f(θ) + (1−λ(t))(θ−θ*)`, which lets the second-moment `v` rescale the penalty unevenly (high-gradient weights get penalized *less*). RecAdam instead applies the penalty **outside** the moment normalization (Line 12):
   `θ_t ← θ_{t−1} − η_t[ s(t)·m̂_t/(√v̂_t+ε) ] − η_t·(1−λ(t))·(θ_{t−1} − θ*)`
   i.e. only the *target* gradient flows through Adam's `m̂/√v̂`; the anchor pulls every weight toward θ* at the uniform rate `η·(1−λ(t))·γ`. It is a **one-line change** from Adam. `s(t)` = the usual LR schedule multiplier (warm-up etc.).

**Init twist (counter-intuitive, relevant to "warm-start").** Because recall is *built into the optimizer*, RecAdam's best config **initializes the model with random weights**, not the pretrained ones (Table 2): RI beats PI on CoLA/MRPC/RTE and ties on STS. The anchor θ* still *is* the pretrained weights — the model is *pulled toward* pretraining but *starts* random, giving a larger search space. Default code = random init.

**Headline results (Table 1, BERT-base, GLUE dev, median of 5 seeds, status ✔):**

| | MNLI 392k | QQP 363k | QNLI 108k | SST 67k | Avg>10k | CoLA 8.5k | STS 5.7k | MRPC 3.5k | RTE 2.5k | Avg<10k | Avg |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BERT-base (rerun) median | 88.6 | — | 91.4 | 93.0 | 89.5 | 60.6 | 89.8 | 86.5 | 71.1 | 77.0 | 83.2 |
| **+ RecAdam** median | 89.1 | — | 91.4 | 93.6 | 89.9 | **62.4** | **90.4** | **87.7** | **74.4** | **78.7** | **84.3** |
| BERT-large (Devlin) | 92.3 | — | 91.3 | 93.2 | 90.9 | 60.6 | 90.0 | 88.0 | 70.4 | 77.3 | 84.1 |

- **+1.1% avg median over vanilla** (83.2→84.3); **+1.7% on the four small (<10k) tasks** (77.0→78.7).
- **BERT-base+RecAdam (84.3) > BERT-large (84.1)** overall median: e.g. **RTE +4.0** (74.4 vs 70.4), CoLA +1.8, STS +0.4, SST +0.4. ✔
- ALBERT-xxlarge+RecAdam reaches **90.2** avg median (SOTA single-task single-model at the time), +0.7 over its own rerun; gains again concentrate on small tasks (+1.5 avg <10k).
- **Forgetting analysis (Figure 2, CoLA):** forgetting measured as Euclidean distance ‖θ_final − θ*‖. Smaller k ⇒ less forgetting but slower target convergence; larger k ⇒ fast convergence, more drift. The k knob *is* the forgetting/convergence tradeoff dial.

### Parts directly useful for Pebble

1. **The data-free anchor `½·γ·Σ(θ−θ*)²` with γ=5000 + sigmoid anneal `λ(t)`** — a drop-in AdamW replacement that protects the warm-start. **[D-E]** This is the whole point: Pebble's NeoBERT enters head-training already carrying (a) pretraining and (b) a GoEmotions emotion warm-start. RecAdam lets the severity head adapt on the tiny target set while a uniform-rate spring holds *all* encoder weights near that warm-started θ*.
2. **Random-init + pretrained-as-anchor (Table 2: RI > PI on 3/4 small tasks)** — a concrete alternative to "load warm-start as init, then fine-tune." **[D-E]** For Pebble the more useful read is the *PI* variant (anchor = θ* = warm-start, *and* init = θ*): still beats vanilla on all 4 tasks (Avg 78.3 vs 77.0), and keeps the encoder near the GoEmotions warm-start by construction.
3. **k as an explicit forgetting↔convergence dial, swept over {0.05…1}, t0 over {100…1000}** — a single principled hyperparameter to tune on a dev slice, replacing ULMFiT's *multiple* hand-set schedules. **[D-E]** Pebble can grid k×t0 on its ~1K human-labeled severity dev set and pick by validation Pearson, instead of hand-designing a per-layer unfreeze order + discriminative-LR ladder + STLR triangle.
4. **The decoupling insight (Algorithm 1, Line 12 vs Line 6)** — penalty must sit *outside* Adam's `√v̂` normalization or high-gradient (i.e. the new severity-head-adjacent) weights get under-penalized. **[D-E, D-B-adjacent]** If Pebble hand-rolls any weight-anchoring regularizer instead of using the released optimizer, this is the bug to avoid; simplest path is to reuse the published `RecAdam` class.
5. **Gains scale *inversely* with target-set size (+1.7% <10k vs +1.1% overall; "vanilla FT is brittle on small data and relies on the init being near-ideal")** — the explicit low-resource argument. **[D-E, D-D]** Pebble's severity target (~5K silver + ~1K human) sits *below* GLUE's smallest tasks (RTE 2.5k, MRPC 3.5k), i.e. squarely in the regime where RecAdam helped most.

### How each part helps Pebble succeed

- **Severity head on a tiny set (D-E, D-D).** Swap AdamW→RecAdam for the unfreeze stage with θ* = the GoEmotions-warm-started NeoBERT checkpoint, γ≈5000 as a starting point (it is `½NF̄`, so re-scale to NeoBERT's parameter count / batch — treat 5000 as a *GLUE-BERT-base* value, not a universal constant; sweep it). Verify: target = severity-dev Pearson ≥ vanilla-FT baseline *and* emotion-head F1 on a held-out GoEmotions slice does **not** drop (the "less forgetting" claim must be measured on Pebble's *own* warm-start task, not just assumed).
- **Replace the ULMFiT ramp with one knob (D-E).** Run the freeze→unfreeze baseline (paper 20) *and* a RecAdam arm; tune only k×t0 (and γ). If RecAdam matches/beats the hand-tuned ramp on severity-dev with fewer moving parts, adopt it — fewer hyperparameters is a direct simplicity win for a single-use training script.
- **Protect the emotion warm-start explicitly (D-E).** Use RecAdam's Euclidean-distance forgetting metric (‖θ_t − θ*‖ over steps) as a *training-time monitor* during severity head-fitting; if the curve runs away, lower k. This is the missing instrumentation the stub's "addresses forgetting" claim needs to be falsifiable.
- **Low-resource argument for the paper (D-D).** Cite RecAdam's "+1.7% on <10k, vanilla FT is brittle and over-relies on the init" as published support that an anchor-to-init regularizer is the right tool when the target set is smaller than RTE — exactly Pebble's severity regime.

### Child mental-health lens

- **Transfer validity:** RecAdam is *task- and domain-agnostic* — it operates purely in weight space (anchor to θ*), so unlike the GLUE accuracy numbers themselves, the *mechanism* carries cleanly from adult-NLU GLUE to Pebble's child-register severity regression. There is no child/adult assumption baked into a quadratic weight penalty. This is the rare case where a corroborated adult-data number (the GLUE gains) supports adopting the *method* even though the *numbers* don't transfer.
- **Why it matters for child safety specifically:** Pebble's emotion warm-start (GoEmotions) is the closest thing it has to a calibrated, broad affect prior. Catastrophically forgetting it while chasing a tiny silver severity set would *degrade the very signal the Decision Engine leans on*. RecAdam's uniform-rate anchor is a principled guard against that — and, unlike gradual unfreezing, it protects *all* layers continuously rather than sequentially exposing them.
- **Risk:** the anchor pulls toward θ* = a warm-start trained on **adult Reddit comments** (GoEmotions). On child-register distress text, over-strong anchoring (large γ / small k) could *lock in* an adult-affect prior and *suppress* learning genuinely child-specific severity cues. Mitigation: tune γ/k against a **child-register dev slice**, not just overall dev Pearson; prefer the configuration that maximizes child-slice severity recall, accepting more drift if needed.
- **Ethics/measurement:** "less forgetting" must be *demonstrated on Pebble's safety-relevant heads*, not inherited from a GLUE plot. Report the warm-start-task metric before/after severity training under both AdamW and RecAdam — a child-facing tool cannot claim "we preserved the emotion signal" without that number.

### Limitations & open questions for Pebble

- **Contradiction vs ULMFiT (paper 20) on the staged-FT question.** ULMFiT's entire thesis is that you fight forgetting by **controlling *which parameters move when*** — gradual unfreezing (top layers first, then deeper), discriminative per-layer LRs, and STLR. RecAdam does the **opposite**: it *lets every parameter move from step 0* (default **random init**, full-model updates, **no freezing, no per-layer LR, no unfreeze schedule**) and instead constrains *how far each parameter may drift* via a **uniform-rate** anchor `(1−λ(t))·γ·(θ−θ*)` — explicitly the *same penalty rate on every weight*. So the two canonical "staged FT" papers in Pebble's set prescribe *mutually exclusive* recipes: ULMFiT = layer-wise schedule, no init change; RecAdam = no schedule, anchor + anneal, random init. Pebble cannot "do both" naively — gradual unfreezing (frozen layers don't move) directly conflicts with RecAdam's premise that *all* weights are anchored and updated. **Open decision:** treat them as two competing D-E arms to benchmark head-to-head, not as a combinable stack. (A defensible hybrid — RecAdam on the *unfrozen* subset only — is untested by either paper and would be Pebble's own contribution.)
- **γ=5000 is not portable.** It equals `½·N·F̄` for BERT-base on GLUE; N (source-data size) and F̄ differ for NeoBERT. Using 5000 blindly is unjustified — it must be swept. The stub's "drop-in" framing understates this.
- **Single-task only; says nothing about D-B.** RecAdam was validated one GLUE task at a time. Pebble trains emotion+severity *jointly*; how the anchor interacts with MTL loss-balancing (Kendall/GradNorm) is unstudied. It is a regularizer *orthogonal* to the head-balancing problem, not a solution to it — confirming the stub's caveat with the now-verified mechanism.
- **Anchors to *pretraining*, not to a *prior fine-tune* — gap vs Pebble's actual setup.** RecAdam's θ* is the LM-pretrained checkpoint. Pebble's θ* would be the **GoEmotions-warm-started** checkpoint (a *fine-tuned*, narrower prior). The Fisher-independence approximation was justified for a broad pretraining minimum; whether a single scalar γ adequately anchors a *task-fine-tuned* init is an open empirical question RecAdam never tested.
- **No regression target in the paper.** All 8 GLUE tasks used here are classification/correlation; severity is a *regression* head. The anchor is task-loss-agnostic so it should apply, but the +1.7% small-data gain is a *classification* result — Pebble must reproduce the benefit on a regression objective before citing it as its own.
