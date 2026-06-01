# Pebble Emotion Classifier — Fine-Tuning Strategy

**Version**: 3.0  
**Last Updated**: May 2026  
**Author**: AI Engineering  
**Status**: Draft — Internal Review

---

## Changelog from v2.1

**Major architectural decision:** The primary fine-tuning target is now **NeoBERT** (`chandar-lab/NeoBERT`), a self-hosted encoder. The **Gemini 2.5 Flash-Lite path is demoted to backup** — kept as a fast-to-stand-up fallback if NeoBERT serving or quality proves problematic. ModernBERT is documented as a second-line encoder fallback.

Consequences threaded through this revision:

- **Section 4 rewritten** around NeoBERT (250M params, 4,096 context, RoPE/SwiGLU/Pre-RMSNorm, MIT license). Gemini Flash-Lite moved to "Backup path."
- **Serving burden is back, and it is the biggest new risk (Sections 4, 6.1, 10, OQ6).** The v2.1 appeal of Flash-Lite was "no new serving infrastructure." NeoBERT reintroduces a self-hosted inference service. NeoBERT depends on FlashAttention/xformers, so the "cheap INT8 ONNX on CPU at 30–80ms" plan inherited from the old ModernBERT path is **unproven** and is now an explicit feasibility spike, not an assumption. Plan for GPU serving as the baseline.
- **Section 5.3 reframed.** The from-scratch multi-task-head, small-dataset risk was a footnote when Gemini was primary; with an encoder primary it is now the headline training risk. NeoBERT's larger capacity (250M vs ModernBERT's 150M) *increases* overfitting risk on a ~5K dataset.
- **Section 6 reordered:** 6.1 = NeoBERT (primary, detailed); 6.2 = Gemini Flash-Lite (backup).
- **Section 7:** the JSON-validation failure mode disappears on the primary path (the encoder emits structured head tensors, not parsed JSON) — a genuine benefit. Latency rows now lead with the self-hosted encoder.
- **Section 8 retitled** "Classifier–Generator Disagreement Handling." The classifier and generator are now entirely different model families, which makes generator-agreement an even weaker correctness proxy — lean harder on human audits.
- **OQ5 reframed and OQ6 added** (NeoBERT serving infrastructure decision). Note that silver-label *training targets* are still Gemini-generated, so the generator's 2.0-Flash migration still affects label provenance even though the classifier is no longer Gemini.

Carried over from v2.1: generator 2.0 Flash deprecation (shutdown **June 1, 2026**), the corrected cost/latency framing, the energy/severity independence check, the 0.5–0.8 human-annotation plan, the receptivity viability gate, annotator wellbeing, and the reconciled F1 thresholds.

---

## 1. Objective

Replace the current single-call Gemini architecture (where one Gemini Flash call handles both emotion scoring and response generation) with a dedicated, fine-tuned emotion classifier. This classifier runs before the generation call, producing structured emotion scores that feed the Decision Engine. The classifier is **NeoBERT, fine-tuned and self-hosted** (Gemini Flash-Lite is the backup).

**Goals:**

- **Improve scoring consistency** — a fine-tuned specialist produces more stable, reproducible scores than a generalist prompted model on this narrow rubric. This is the primary win.
- **Enable the Decision Engine to operate on structured scores *before* generation begins**, allowing richer, longitudinally-informed response routing. The single-call architecture cannot do this — scoring and generation are entangled in one pass.
- **Full decoupling from generator-model churn.** A self-hosted NeoBERT classifier is completely independent of the Gemini generator at inference time. Generator deprecations and prompt changes no longer touch the routing path. (The training *targets* are still Gemini silver labels — see OQ5 — but inference is independent.)
- **Eliminate the structured-output failure mode.** An encoder with typed heads cannot emit malformed JSON; there is no parse/Zod-validation failure surface on the primary path. (This is the inverse of the Gemini path's main reliability risk.)

**A note on cost and latency (unchanged in substance from v2.1, re-costed for NeoBERT):** The two-call architecture does **not** reduce total cost or end-to-end latency.

- *Latency:* the classifier runs *before* generation (classifier → Decision Engine → generator, sequential, because generation consumes the routing decision). NeoBERT inference on suitable hardware is fast (~20–50ms GPU FP16; ~50–150ms CPU INT8 *if* ONNX export succeeds), but it is still additive in front of the unchanged 1–2s generation. End-to-end latency goes up slightly.
- *Cost:* the cost model changes shape entirely. Gemini Flash-Lite was per-token with no infra. NeoBERT is a **fixed self-hosted serving cost** (GPU/CPU instance hours) that is largely independent of message volume at our scale, plus a one-time training cost. At 500 DAU this is likely *more* expensive than Flash-Lite would have been (see Section 4 trade-offs and OQ6), not less.

The split is justified by consistency, pre-generation routing, decoupling, and the removal of the JSON failure mode — not by cost or speed.

---

## 2. What the Classifier Produces

A single structured output per user message. On the NeoBERT path these are typed head outputs (sigmoid scores, softmax logits, a binary logit); the backend assembles them into the same object the rest of the pipeline already expects:

```json
{
  "energy":           0.0,   // float [0–1], user's activation level
  "severity":         0.0,   // float [0–1], intensity of negative emotion
  "socialIsolation":  0.0,   // float [0–1], degree of social disconnection signals
  "receptivity":      0.0,   // float [0–1], venting (0) vs. seeking input (1)
  "detectedEmotion":  "",    // single label from a fixed taxonomy
  "safetyFlag":       false  // crisis signal
}
```

**Two dimensions from the original architecture are intentionally excluded from the model:**

- `themeRepetition` — requires cross-session memory (how often has this topic appeared across weeks?). No single-input classifier can compute this. It stays in the Decision Engine as a Firestore lookup against the memory store.
- `sessionTrajectory` — requires within-session progression (is the conversation getting better or worse?). Computed as a running delta of `severity` scores within the current session. Pure arithmetic, no model needed.

---

## 3. Emotion Taxonomy

### 3.1 Proposed 12-Label Taxonomy

| Label | Mapped From (GoEmotions) | Mapped From (EmpatheticDialogues) |
|---|---|---|
| joy | joy, amusement, excitement | joyful, excited, proud |
| gratitude | admiration, approval, gratitude | grateful, trusting |
| hope | optimism, desire | hopeful, anticipating |
| sadness | grief, remorse, sadness | sad, disappointed, devastated |
| frustration | anger, annoyance, disapproval | angry, annoyed, furious |
| anxiety | nervousness, fear | anxious, apprehensive |
| confusion | confusion, embarrassment | confused, embarrassed |
| loneliness | — (no direct label) | lonely |
| exhaustion | — (no direct label) | — |
| guilt | — | guilty, ashamed |
| calm | relief, caring | content, sentimental |
| neutral | neutral | neutral |

### 3.2 Mandatory Taxonomy Pilot (Pre-Annotation Gate)

The training pipeline, GoEmotions label mapping, annotation guidelines, and evaluation metrics all depend on this taxonomy being stable. Changing it after the full annotation pass forces a pipeline restart. A taxonomy pilot is therefore required before the main annotation effort begins.

**Protocol:**

1. Sample 100 messages from the silver label collection, stratified by severity quartile (25 per quartile) and primary path distribution.
2. Two annotators independently assign an emotion label from the 12-label taxonomy to each message, working from scratch (no Gemini pre-fill, no anchoring).
3. Compute pairwise confusion rates between all label pairs.
4. **Decision rule:** If any two labels are confused >40% of the time (i.e., annotators disagree between those two labels in >40% of cases where either label is chosen), merge them. Likely candidates: `frustration`/`anger` overlap, `anxiety`/`confusion` overlap, `exhaustion`/`sadness` overlap.
5. Finalize the taxonomy. Update the GoEmotions mapping table. Update the annotation guidelines. Only then proceed to the full annotation pass.

**Timeline cost:** 2–3 days. The cost of not doing this: 2–3 weeks if a taxonomy change is needed after the full annotation.

### 3.3 socialIsolation Viability Gate

The `socialIsolation` dimension has no strong public dataset equivalent and is inherently subjective. Its viability as a model output is uncertain. Rather than carry it through the full pipeline and potentially drop it at evaluation, we define an early decision gate.

**Gate (evaluated during the taxonomy pilot and early annotation):**

- During the 100-message taxonomy pilot, annotators also score `socialIsolation` on a [0–1] scale.
- Compute inter-annotator agreement (Krippendorff's alpha).
- **If alpha < 0.5:** Drop `socialIsolation` from the model. Replace with a keyword heuristic in the Decision Engine (match against phrases like "nobody understands," "I have no one," "no one cares," "all alone," frequency of first-person singular without social referents). The keyword heuristic is crude but at least deterministic and debuggable.
- **If alpha >= 0.5 but < 0.6:** Proceed with the model output but set a relaxed MAE target (0.25 instead of 0.20) and plan to re-evaluate after the first training run.
- **If alpha >= 0.6:** Proceed normally.

This decision is made in Week 3 (during the pilot), not discovered in Week 7.

### 3.4 receptivity Viability Gate

`receptivity` is the most subjective dimension with the lowest expected inter-annotator agreement, so it gets the same early gate as `socialIsolation` — it needs it more.

- During the 100-message pilot, annotators also score `receptivity` on a [0–1] scale (venting=0, seeking input=1).
- Compute Krippendorff's alpha.
- **If alpha < 0.5:** Do not ship `receptivity` as a continuous model output. Either (a) collapse it to a binary `venting | seeking_input` classification head, which is easier to annotate consistently and is what the Decision Engine actually consumes, or (b) replace with a Decision-Engine heuristic (interrogative parsing + first-/second-person ratio). Prefer the binary — it preserves the signal at a granularity humans can agree on.
- **If alpha >= 0.5 but < 0.6:** Proceed as continuous with a relaxed MAE target (0.25), re-evaluate after the first training run, and keep the binary fallback ready.
- **If alpha >= 0.6:** Proceed as continuous.

Known weakness in the `receptivity` training signal: the DailyDialog act-label mapping ("question"→high, "inform"→low) conflates dialogue act with emotional receptivity. Rhetorical questions while venting ("why does this always happen to me?") are syntactically questions but are vents. Treat DailyDialog as weak/noisy signal and weight human annotations heavily for this dimension.

---

## 4. Model Selection

### Primary: NeoBERT (`chandar-lab/NeoBERT`), Self-Hosted, Multi-Task Fine-Tune

**Model facts (verified against the model card / paper, arXiv 2502.19587):**

| Property | Value |
|---|---|
| Parameters | 250M |
| Depth × width | 28 × 768 (depth-efficient ratio) |
| Context length | 4,096 tokens |
| Positional embeddings | RoPE |
| Activation | SwiGLU |
| Normalization | Pre-RMSNorm |
| Attention | FlashAttention (GPU); xformers dependency |
| Tokenizer | google/bert WordPiece |
| Pretraining | RefinedWeb, ~2.1T tokens |
| License | **MIT** (commercial use OK) |
| Loading | `AutoModel.from_pretrained("chandar-lab/NeoBERT", trust_remote_code=True)` |

**Why NeoBERT:**

- State-of-the-art among base-size encoders: outperforms BERT-large, RoBERTa-large, NomicBERT, and ModernBERT on MTEB under identical fine-tuning conditions, despite being 100M params smaller than the large-size encoders.
- Fastest encoder of its kind — reported ~46.7% faster than ModernBERT on 4,096-token sequences (on GPU with FlashAttention).
- 4,096-token context is more than enough for our input ("current message + last 3 messages"); we do not need ModernBERT's 8,192.
- MIT license — clean for a commercial product. No data-use or model-license encumbrance.
- Full inference-time independence from Gemini and from GCP's managed model lifecycle.

**Architecture (multi-task heads on the shared 768-dim `[CLS]` representation):**

- **Score Head:** encoder → dropout(0.1) → dense(256) → GELU → dropout(0.1) → dense(K) → sigmoid. Outputs the K continuous scores in [0,1], where K ∈ {2,3,4} depending on which of energy/socialIsolation/receptivity survive their gates (Sections 3.3, 3.4, 5.2). `severity` always survives.
- **Emotion Head:** encoder → dropout(0.1) → dense(256) → GELU → dropout(0.1) → dense(N) over the taxonomy. Softmax at inference. Warm-started from GoEmotions (Section 6.1 Step 1).
- **Safety Head:** encoder → dropout(0.1) → dense(64) → GELU → dense(1). Binary logit, trained with high positive-class weight (10×) given ~1–2% positive rate.

Loss is a weighted sum: MSE (scores) + cross-entropy (emotion) + BCE (safety), safety weighted 2× to prioritize recall. See Section 6.1 for the multi-task-balancing caveat.

**Trade-offs — read these before committing; they are the real cost of this decision:**

- **Serving is now our problem.** This is the single biggest consequence of choosing NeoBERT over Flash-Lite. We must build, deploy, monitor, scale, and pay for a self-hosted inference service. The v2.1 plan explicitly avoided this.
- **The "cheap CPU + INT8 ONNX at 30–80ms" plan is unproven for NeoBERT.** That figure was inherited from the ModernBERT path. NeoBERT (a) is 250M, not 150M; (b) uses FlashAttention + xformers + custom modeling code loaded via `trust_remote_code`, which is GPU-oriented and not guaranteed to ONNX-export cleanly to CPU (RoPE, SwiGLU, RMSNorm, and the custom attention all must be traceable/quantizable). **Treat CPU ONNX as a feasibility spike, and plan GPU serving as the baseline** (NVIDIA L4 on Cloud Run or a Vertex endpoint). See OQ6.
- **Cost flips from per-token to fixed infra.** A GPU instance with `min-instances ≥ 1` (needed to avoid cold-start latency on a latency-sensitive path) is on the order of hundreds of dollars/month, several multiples of the v2.1 total infra estimate (~$30–65/mo). At 500 DAU this is almost certainly *more* expensive than Flash-Lite per-token pricing would have been. The architecture cost model must be re-derived.
- **Maturity / ecosystem risk.** NeoBERT is a Feb 2025 research model from an academic lab (Le Breton, Fournier, El Mezouar, Chandar — Mila/Chandar Lab). It is excellent but less battle-tested in production than ModernBERT, with thinner tooling (custom code path, `trust_remote_code` required, native HF `transformers` integration still maturing). Pin the exact revision and vendor the modeling code.
- **From-scratch heads on a small dataset** — the central training risk, detailed in Section 5.3.

### Backup: Gemini 2.5 Flash-Lite (Vertex AI Supervised Fine-Tuning)

Retained as the fallback if NeoBERT serving proves too costly/immature or its quality misses targets. Its advantages are exactly NeoBERT's weaknesses: no serving infra (managed Vertex endpoint), native structured-output support, single-model-string deployment, LoRA SFT.

- `gemini-2.5-flash-lite` reached GA with supervised fine-tuning on Vertex AI in May 2026; pricing is identical to the (now-deprecated) 2.0 Flash at $0.10/$0.40 per 1M tokens. SFT for Flash-Lite is freshly GA, so it is itself an early-adopter path.
- Failure mode unique to this path: fine-tuning can degrade JSON compliance on out-of-distribution inputs (Section 6.2 Step 4). The NeoBERT primary path does not have this failure mode.
- Switching to the backup is a non-trivial but well-scoped pivot (≈2–3 weeks faster than the NeoBERT path; see Section 10), since the data, taxonomy, annotation, and eval are all model-agnostic.

### Considered but not chosen

| Model | Disposition |
|---|---|
| ModernBERT-base | **Second-line encoder fallback.** Lower MTEB and slower than NeoBERT in identical-fine-tune comparisons, but more mature production tooling and a cleaner, proven CPU/ONNX path. If NeoBERT serving (esp. CPU ONNX) proves unworkable and we still want a self-hosted encoder, fall back to ModernBERT before falling back to Gemini. Its 8,192 context is unused here. |
| DistilBERT | Not used. 66M params too small for 6-output multi-task; 512 context forces truncation. Superseded by both encoders above. |
| Gemini 2.5 Pro / 2.5 Flash (full) | Not used for classification. Overkill and more expensive than Flash-Lite with no accuracy gain on this narrow task. (2.5 Flash is the likely *generator* replacement — separate decision, OQ5.) |
| Gemma 3 (1B/4B) / all-MiniLM-L6-v2 | Not used. Generative model is architecturally wrong for pure classification; MiniLM's 256 context and 22M params are too small. |

---

## 5. Datasets

### 5.1 External Datasets (Pre-Training and Transfer Learning)

These public datasets provide foundational emotion understanding. They warm-start the model before fine-tuning on Pebble-specific data. They matter **more** on the NeoBERT path than they would have on the Gemini path: the encoder's heads start randomly and the Pebble dataset is small, so transfer signal carries more weight (Section 5.3).

**GoEmotions (Primary)**

- Source: Google Research, Reddit comments
- Size: 58,000 examples
- Labels: 27 fine-grained emotion categories + neutral
- Role in Pebble: Pre-train the `detectedEmotion` head. Map GoEmotions' 27 labels down to Pebble's taxonomy (see Section 3.1 mapping table).
- Limitation: Reddit comments are short, context-free, and often sarcastic. Distribution differs from Pebble's conversational, emotional-support context.

**EmpatheticDialogues**

- Source: Facebook Research
- Size: 25,000 conversations across 32 emotion labels
- Role in Pebble: Most structurally similar to Pebble's data. Use the "speaker" turns as training examples; provides multi-turn context GoEmotions lacks.
- Limitation: Crowdsourced and prompted, so emotional expression is more explicit and less natural than real user messages.

**DailyDialog**

- Source: Yanran Li et al.
- Size: 13,000 dialogues
- Labels: 7 emotions + 4 dialogue act labels (question, inform, directive, commissive)
- Role in Pebble: Act labels are the main public signal for `receptivity` (weakly — see Section 3.4 caveat).
- Limitation: Daily conversation domain; emotion distribution skewed to "neutral."

**SemEval-2025 Task 11**

- Source: Shared task, multilingual; English subset has several thousand examples
- Labels: 6 emotion classes + emotion intensity scores
- Role in Pebble: Intensity provides the strongest transfer signal for `severity`. Intensity ≈ severity in Pebble's framing.
- Limitation: News-reaction domain, not personal sharing.

**WASSA 2023/2024 Shared Task**

- Source: Annual empathy-detection shared task; ~2,000 essays + dyadic conversations
- Role in Pebble: Turn-level emotion polarity/intensity directly relevant; empathy scores a weak proxy for `receptivity`.
- Limitation: Small. Augmentation/validation, not primary.

**TalkLife Dataset (Sharma et al., 2020)**

- Source: TalkLife mental-health peer-support platform; 235,000 supportive conversations
- Role in Pebble: Closest domain match; help-seeker messages resemble Pebble inputs.
- Limitation: Restricted access (DUA — see OQ1). Labels are on the supporter's response, not the seeker's message — requires inference reversal.

### 5.2 Pebble-Specific Dataset (Must Build)

No public dataset covers Pebble's exact output schema. The primary training data comes from Pebble's own production pipeline.

**Source: Phase 1–3 Gemini Silver Labels**

Every message processed by Gemini during Phases 1–3 produces a scored output. These are "silver labels" — model-generated, not human-verified. They form the bulk of the training data. (Note: even though the classifier is now NeoBERT, the *labels* are still Gemini-generated — the generator-migration provenance issue in OQ5 still applies to this training data.)

Collection requirements:

- Store every `(input, target)` pair in a dedicated Firestore collection (`training_data/{docId}`), separate from production messages.
- Input: the user's current message + the last 3 messages (interleaved) as context.
- Target: energy, severity, socialIsolation, receptivity, detectedEmotion, safetyFlag. Exclude themeRepetition and sessionTrajectory.
- Metadata: sessionId, userId (for stratified splitting — never let the same user appear in both train and test), timestamp, **generator model version** (now critical — see OQ5), fallback flag (exclude fallbacks).
- Begin collection from Day 1 of Phase 1.

Target volume: 5,000+ scored messages before fine-tuning.

**Volume timeline realism:** v2.0 claimed "2–3 weeks" while also citing 500 DAU at 5–15 msg/day — inconsistent (that's 2,500–7,500 messages/*day*, i.e. 5K in 1–2 days). The real constraint is that Phase 1–2 alpha has *tens* of users, not 500 (500 DAU is MVP scale reached ~Phase 4). Accumulation is governed by the actual early-phase DAU curve. **Risk: the 5K may not exist when training is scheduled.** Gate the training start on actual accumulated volume, not the calendar; have a fallback to delay or to lean harder on external transfer data. This risk is sharper on the NeoBERT path, which is more data-hungry (Section 5.3).

**Energy/severity independence check (run in Week 2, before any training):** `energy` ("activation level") inferred from short text likely correlates strongly with `severity` in the silver labels. Compute Pearson/Spearman correlation across the collection. **If |r| > 0.7, `energy` is not carrying independent signal** — drop the head (the Decision Engine can derive a coarse energy proxy) rather than spend model capacity and annotation budget on a redundant dimension. Cheap query, prevents a wasted training run, and reduces K in the score head.

**Source: Human Annotation Pass**

Silver labels are noisy. A human pass creates a high-quality test set and calibrates which dimensions Gemini scores reliably.

**Protocol A — Training Corrections (Anchored, 500 examples)**

These augment the training set. Anchoring to Gemini's scores is acceptable here — the training set tolerates some bias and human corrections fix the worst errors.

- Sample 500 from the silver labels, stratified by severity quartile.
- **Proactively oversample the 0.5–0.8 severity band.** This is the highest product-harm misclassification zone (Section 8.3): a user who should route to MOTIVATE/CONNECT gets LIGHTEN, with no safety flag firing because it's sub-crisis. Handle it up front, not as a post-hoc contingency, and use *human-annotated* (not silver) examples — silver oversampling amplifies Gemini's noise in exactly the band that matters. Allocate ~150 of the Protocol A budget here.
- Two annotators review each example with Gemini's scores pre-filled; they adjust rather than score from scratch.
- Where both agree on a correction (deviation >0.15 on any continuous dimension, or emotion-label disagreement), the human label replaces the silver label.
- Disagreements between annotators → adjudication.

**Protocol B — Test Set (Unanchored, 500 examples)**

The evaluation test set. Anchoring bias is unacceptable — the test set must be independent of the model under evaluation.

- Sample 500, stratified by severity quartile (125 per quartile).
- Annotators score all dimensions **from scratch, with no visibility into Gemini's scores.** The Protocol B interface shows no pre-filled values.
- Measure inter-annotator agreement: Krippendorff's alpha (continuous), Cohen's kappa (categorical). If alpha < 0.6 on any dimension, the guidelines are ambiguous — revise and re-annotate before proceeding.
- Resolve disagreements by averaging (continuous) or adjudication (categorical).
- Compute Gemini-vs-human correlation per dimension — an honest measure of silver-label quality, and the basis for how much to trust silver labels in training.

**Why the split protocol matters:** anchoring the test set would measure "does the model reproduce Gemini's scores (slightly human-adjusted)?" — the wrong question. The unanchored protocol measures "does the model match human judgment?" — the right one. This is especially important now: the NeoBERT classifier's ground truth is human annotation, *not* Gemini, so the test set must be Gemini-independent.

The annotation tool is a page in the admin dashboard: fetch a sample, display message + context, sliders for scores + dropdown for emotion label, submit. Two modes: pre-filled (Protocol A) and blank (Protocol B), toggled per batch. Build effort ~2–3 days.

**Annotator count:** Use **three** annotators on the pilot and Protocol B, not two. Two-rater Krippendorff's alpha is noisy, and the alpha gates throughout (Sections 3.3, 3.4) depend on stable estimates. A third gives a built-in adjudicator. Protocol A can run with two.

**Annotator wellbeing:** This work exposes annotators to crisis/distress/self-harm content for weeks. Required: cap daily volume of high-severity/safety-positive items per annotator, rotate annotators off the safety-positive queue rather than concentrating it, provide debriefing/EAP access, and brief annotators up front with a no-penalty opt-out. Both an ethical obligation and a data-quality measure — fatigued annotators produce noisier labels, degrading the alpha gates.

**Sampling-constraint interaction:** User-level splitting and severity-quartile stratification cannot be satisfied independently (a user's messages span multiple quartiles). **Split by user first, then stratify within the split-assigned users** — accept approximate quartile balance, especially with few early users. Do not stratify at message level then dedup by user; that reintroduces leakage.

**Dimension-Specific Data Gaps**

| Dimension | Public Data Available? | Gap Mitigation |
|---|---|---|
| `energy` | Partial — SemEval/WASSA intensity gives weak signal | Subject to the independence check above. If retained: rely on Pebble silver labels, human-annotate extremes. If convergence is poor, discretize to 3 ordinal classes. |
| `severity` | Yes — SemEval intensity, WASSA intensity | Pre-train head on SemEval intensity → fine-tune on Pebble. Strongest transfer signal. |
| `socialIsolation` | No direct dataset | Subject to the viability gate (3.3). If retained: GoEmotions "loneliness" as weak pre-training + Pebble silver labels + 500 isolation-targeted human examples. |
| `receptivity` | Partial — DailyDialog acts, TalkLife mechanisms | Subject to the viability gate (3.4). DailyDialog mapping is noisy; weight human annotations heavily. Binary fallback ready. |
| `detectedEmotion` | Yes — GoEmotions strong | Pre-train head on GoEmotions (mapped) → fine-tune. Converges fastest. |
| `safetyFlag` | Restricted — CLPsych, UMD Reddit need ethics approval | See Section 5.4 safety data protocol. |

### 5.3 Honest Assessment of Dataset Size — Now the Headline Training Risk

4,000–5,000 training examples for a 6-output multi-task problem is small. With an encoder as the **primary** model, this moves from a footnote to the central risk.

**Why this is tight for NeoBERT (the primary path):** NeoBERT's score and safety heads initialize randomly (only the emotion head gets GoEmotions pre-training). NeoBERT has a **250M** shared encoder — *larger* than ModernBERT's 150M — so it has more capacity to overfit a 5K dataset, not less. With batch 16 and ~5 epochs, ~1,600 gradient steps is enough to adapt the encoder but may be too few for the regression and safety heads to converge robustly. Expect to fight overfitting, not underfitting.

Mitigations baked into the plan:

- **Freeze the encoder longer.** Train heads on a frozen encoder first; unfreeze late with a low LR (Section 6.1). The larger the encoder, the more this matters.
- **Lean on transfer/pretraining** (Section 5.1) more heavily than the Gemini path would have — GoEmotions for the emotion head, SemEval intensity for severity.
- **Aggressive regularization** — dropout 0.1→0.2, weight decay, early stopping (Section 6.1).
- **Watch run-to-run variance.** With a small dataset and a big encoder, F1/MAE can swing across seeds. Report mean ± std over ≥3 seeds, not a single run.

**Why the backup path tolerates this size better:** fine-tuning Gemini Flash-Lite is teaching an already-fluent LLM a scoring rubric, not training heads from scratch; 1K–5K high-quality examples routinely suffice there. If NeoBERT's data-efficiency proves inadequate after the contingencies below, that is itself a signal to fall back to Gemini.

**Contingency plans if the first NeoBERT run underperforms:**

| Symptom | Likely Cause | Action |
|---|---|---|
| High variance across seeds (>5% F1 swing) | Too few examples for 250M encoder | Increase dropout to 0.2. Freeze encoder for more epochs. Reduce head hidden dim 256→128. If persistent, consider ModernBERT (smaller) or the Gemini backup. |
| `energy` MAE > 0.20 | Weak/redundant signal | Should already be caught by the Week-2 independence check. If retained and failing: discretize to 3 ordinal classes. |
| `socialIsolation` MAE > 0.25 | Inherently subjective | Drop from model; keyword heuristic (3.3). |
| `detectedEmotion` F1 < 0.65 | Taxonomy too fine for the data volume | Collapse to 8 labels (merge pilot-identified pairs). Retrain. |
| Safety recall < 0.90 | Too few positives | Execute Section 5.4 augmentation. Lower threshold. Hard-mine false negatives. |
| All heads underperform vs. a quick Gemini-Lite SFT baseline | NeoBERT data-efficiency inadequate at this scale | **Fall back to the Gemini backup path.** Run this baseline early (Week 7) so the fallback decision is data-driven, not late. |

These are pre-planned, not discovered mid-training.

### 5.4 Safety Data Protocol

The safetyFlag output is the most critical dimension and the most data-constrained. At ~1–2% positive rate, the training set holds only 50–100 real positives — not enough for a robust safety head.

**Augmentation strategy (layered):**

**Layer 1 — Real positives from production:** Every message where Gemini's safetyFlag = true during Phases 1–3 is flagged for human review. A dedicated annotator (separate from general annotation) confirms or rejects. Confirmed positives enter training directly. Expected: 50–150 over 3 weeks.

**Layer 2 — Adversarial rephrasing:** For each confirmed positive, manually write 2–3 rephrasings that preserve the crisis signal but change surface features (vocabulary, structure, explicitness), so the model learns intent, not phrases.
- Example: "I don't want to be here anymore" → "What's even the point of going on," "I keep thinking how much easier it'd be if I just wasn't around," "Everything would be better if I disappeared."
- Each reviewed by a second team member for realism. Expected: 100–450.

**Layer 3 — Synthetic generation under clinical review:** Use Gemini Pro (not Flash) to generate synthetic crisis messages across demographics, states, and styles. The prompt specifies: vary explicitness (explicit ideation → indirect signals like giving away possessions, sudden calm after distress); vary demographics; include near-miss non-crisis ("this movie is killing me").
- **Clinical review requirement:** every synthetic example is reviewed by a contracted licensed mental-health professional before entering training, classified (a) realistic/correct, (b) unrealistic—discard, (c) ambiguous—hard negative/borderline, with written feedback on what synthetic data gets wrong. Expected: 200–300.

**Layer 4 — Public datasets (if approved):** CLPsych and UMD Reddit Suicidality provide real crisis language at scale but need IRB-equivalent approval/DUA. Strongest source if approved; Layers 1–3 must suffice if not.

**Total safety positives (est.):** 350–900 depending on Layer 4, bringing the positive rate to ~7–15% — manageable with positive-class weighting.

**Known risk with synthetic data:** the model may learn synthetic "style" rather than crisis signal. Mitigation: the 500-sample test set contains only real production examples (Protocol B). If safety recall is high on synthetic validation but low on the real test set, reduce/regenerate the synthetic data with clinical feedback.

### 5.5 Final Dataset Composition

| Split | Size | Composition |
|---|---|---|
| Training | 4,000–5,500 | ~3,500 Pebble silver labels (filtered) + ~500 human-corrected (Protocol A) + augmented safety positives (Layers 2–4) + GoEmotions/EmpatheticDialogues transfer examples for underrepresented classes |
| Validation | 500 | 250 human-annotated (Protocol A methodology) + 250 silver labels |
| Test | 500 | 100% human-annotated via Protocol B (unanchored). Non-negotiable — evaluation on silver or anchored labels is circular. |

**User-level splitting:** all messages from a given user appear in exactly one split. Deterministic hash of userId → split, computed once and stored as metadata.

---

## 6. Training Plan

### 6.1 NeoBERT Path (Primary)

**Step 0 — Environment and model pinning.** Install `transformers`, `torch`, `xformers==0.0.28.post3` (and `flash_attn` for sequence packing / GPU training). Load `chandar-lab/NeoBERT` with `trust_remote_code=True`, **pinned to an exact revision**, and vendor the custom modeling code into the repo so a remote change can't silently alter behavior. Confirm GPU availability for training (FlashAttention requires it).

**Step 1 — Emotion Head Pre-Training on GoEmotions.**
- Map GoEmotions' 27 labels to Pebble's taxonomy (Section 3.1); document and team-review the mapping.
- Freeze the encoder for the first 2 epochs to let the emotion head converge without destabilizing pretrained representations.
- Unfreeze for 1–2 epochs at low LR (1e-5) for shallow adaptation.
- Only the emotion head is active here; score and safety heads are untrained.

**Step 2 — Multi-Task Fine-Tuning on Pebble Data.** All heads train jointly.
- Initialize the emotion head from Step 1; score and safety heads random.
- LR: 5e-6 encoder (already adapted), 2e-5 heads.
- Batch 16, ~5 epochs (~1,600 steps). Given the 250M encoder on ~5K examples, **start with a longer encoder freeze** (e.g., heads-only for the first 1–2 epochs, then unfreeze) and watch the train/val gap.
- Loss weights: score ×1.0, emotion ×1.0, safety ×2.0. Safety positive-class weight 10× in BCE.
- **Multi-task balancing caveat (NeoBERT-specific):** with one shared `[CLS]` feeding all heads and energy/severity likely correlated, the cleanest-signal task (emotion, warm-started) can dominate the shared representation and starve the regression heads. Static weights may not suffice. If per-head val metrics diverge (emotion improves while severity stalls), switch to uncertainty-based task weighting (Kendall et al.) or GradNorm before adding data.
- Early stopping on val loss, patience 3 (eval every 100 steps). Mixed precision (FP16).
- Regularization: dropout 0.1 (→0.2 if train/val diverge >20% after epoch 2), weight decay 0.01 on encoder.
- **Run ≥3 seeds; report mean ± std.** Single-run numbers are unreliable at this dataset size.

**Step 3 — Hard Example Mining.** After Step 2, run inference on the validation set; take the top 5% by loss (≈25 examples at 500 val) plus *all* safety false negatives regardless of loss rank. Human-annotate/correct, add to training, run 1 epoch at very low LR (1e-6). If this improves val metrics <1% relative, skip it in future retrains.

**Step 4 — Serving (the hard part — see Section 4 trade-offs and OQ6).**

Two serving tracks; decide via a Week-8 spike, not by assumption:

- **Track A (baseline): GPU FP16 on Cloud Run (NVIDIA L4) or a Vertex endpoint.** Lowest risk — runs NeoBERT as-is with FlashAttention. Target latency ~20–50ms. Cost: a `min-instances ≥ 1` GPU instance, hundreds of $/month. This is the assumed default.
- **Track B (cost-optimization spike): INT8 ONNX on CPU Cloud Run.** Target ~50–150ms, much cheaper. **Feasibility is unproven** for NeoBERT (custom attention/RoPE/SwiGLU/RMSNorm + `trust_remote_code` must export and quantize correctly). Timebox the spike; if it fails, stay on Track A or fall back to ModernBERT (proven CPU/ONNX path) before falling back to Gemini.

Serve a lightweight container (FastAPI + Torch/ONNX Runtime) exposing `/classify` (message + context → typed scores). The backend calls it before the Gemini generation call; the Decision Engine consumes the output to adjust path weights and passes a response-style directive to Gemini. Add `min-instances=1` to eliminate cold starts on whichever track is chosen.

**Step 5 — Experiment tracking & deployment.** Log every run (hyperparameters, per-epoch metrics, confusion matrices, checkpoints, seed) to Weights & Biases or MLflow. Every deployed version traces to its training-data snapshot + config + Protocol B evaluation. No deployment without a completed Protocol B eval. Rollback = repoint the backend to the previous container/endpoint revision.

### 6.2 Gemini Flash-Lite Path (Backup)

Stood up only if NeoBERT serving/quality fails the gates. Steps unchanged from v2.1.

**Step 1 — Data Preparation.** Convert to Vertex JSONL: classification prompt as user message, target JSON as model response. Freeze a system prompt defining task, schema, and taxonomy with per-label definitions, embedded in every example. Include 5–10 edge-case few-shots:
- Sarcasm: "Oh great, another Monday" → anxiety/frustration, not joy
- Minimization: "I'm fine" with high-severity context → severity reflects context
- Mixed: "Got the promotion but I feel empty" → exhaustion/sadness, not joy
- Figurative: "This deadline is killing me" → frustration, safetyFlag false
- Indirect crisis: "I've been giving away my things" → safetyFlag true

**Step 2 — Training Config.** Base `gemini-2.5-flash-lite`; LoRA via Vertex SFT; epochs 3 (converges fast; more risks overfit); LR multiplier 1.0 (→0.5 if val diverges after epoch 2); thinking budget off (no CoT needed for classification).

**Step 3 — Evaluation.** Protocol B test set: MAE per continuous dim, macro F1 for emotion, P/R/F1 for safety. Criteria in Section 7.

**Step 4 — Structured-Output Reliability.** Run 1,000 diverse inputs (500 val + 500 adversarial: very long, empty, other-language, emoji-only, code/URLs). Targets: JSON parse >99%, Zod validation >98%, p95 <300ms, p99 <500ms. Below → retrain with stricter formatting + malformed-input examples. (This failure mode does not exist on the NeoBERT path.)

**Step 5 — Deployment.** Tuned model → Vertex endpoint; backend swaps model identifier. Zod validation, timeout gate, fallback logic unchanged. Track JSON-validation failure rate (alert >2%/1h) and classifier-attributable fallback rate. Rollback = model-string swap.

---

## 7. Evaluation Criteria

All metrics computed on the 500-sample, 100% human-annotated test set (Protocol B — unanchored), reported as mean ± std over ≥3 seeds for the NeoBERT path.

| Metric | Target | Rationale | If Below Target |
|---|---|---|---|
| `severity` MAE | < 0.15 | Core routing signal — misscoring by >0.15 can route a distressed user to LIGHTEN instead of MOTIVATE/CONNECT | Inspect high-severity samples; likely underrepresented. Oversample and retrain. |
| `energy` MAE | < 0.15 | Affects pet mood and tone | If retained past the independence check: if Gemini-human correlation < 0.7, weight human examples 3×; else discretize to 3 ordinal classes. |
| `socialIsolation` MAE | < 0.20 | Higher tolerance; subjective. Subject to gate (3.3). | If persistently above 0.20, drop and use keyword heuristics. |
| `receptivity` MAE | < 0.20 | Determines listen-vs-advise; moderate error tolerable. Subject to gate (3.4). | If alpha < 0.5 even on the test set, revise the definition or convert to binary. |
| `detectedEmotion` macro F1 | > 0.65 | Must distinguish taxonomy labels meaningfully | Collapse similar emotions (merge pilot-identified pairs); retrain with fewer classes. |
| `safetyFlag` recall | > 0.95 | Non-negotiable. A missed crisis is a product failure. | Increase positive-class weight; add Section 5.4 positives; lower threshold. **Do not rely on the classifier's safety output until met** — see gate below. (Classifier still ships for routing; only its *safety function* is gated, since the keyword+generation union remains the primary safety net.) |
| `safetyFlag` precision | > 0.70 | Some false positives acceptable — better over- than under-trigger | If below, check whether false positives are borderline (then 0.70 is fine) or clearly non-crisis (investigate labeling). |
| End-to-end classifier latency (p95) | < 300ms | Must not add perceptible delay | **NeoBERT (primary):** GPU FP16 easily meets it; CPU ONNX must be verified in the Step-4 spike (cold starts → `min-instances=1`). **Gemini backup:** met by managed serving. |
| JSON validation rate | > 98% | **Backup (Gemini) path only.** | The NeoBERT path emits typed head outputs and has no JSON-parse failure mode — N/A for the primary path. |

**Safety deployment gate:** if safetyFlag recall does not reach 0.95, the classifier is not used *for safety detection*. The existing dual-trigger (keyword regex + Gemini generation safetyFlag) remains primary; the classifier's safety output is supplementary only. The classifier still ships for the routing dimensions.

---

## 8. Classifier–Generator Disagreement Handling

In the two-call architecture the classifier (NeoBERT) scores first, the Decision Engine routes, then Gemini generates. The generator still implicitly "understands" the message (it sees the raw input + context), so disagreement is possible — and is now *more* expected, because the classifier and generator are entirely different model families.

### 8.1 Safety Disagreements (Handled in Real-Time)

Union-of-triggers: the safety protocol activates if ANY fire —
- Classifier safetyFlag = true
- Keyword regex match
- Gemini generation produces crisis-indicative content (e.g., references crisis resources unprompted)

The last is a heuristic: if Gemini spontaneously surfaces crisis helplines or "I'm concerned about you," the generator detected crisis even though the classifier didn't. When this happens:
1. Log to `safety_events` with `triggerType: "generation_heuristic"`.
2. Allow Gemini's crisis-aware response through (do not override with the Decision Engine's routing).
3. Flag the message for human review and potential addition to the safety training set.

### 8.2 Severity/Routing Disagreements (Handled via Monitoring)

Real-time override is impractical for non-safety dimensions (it would require Gemini to also produce scores, defeating the split). Monitor for systematic drift instead.

**Baseline caveat:** the classifier's ground truth is the human-annotated Protocol B set, *not* any Gemini version. With a NeoBERT classifier and a Gemini generator — different architectures, different training — "agreement with the generator" is an even weaker proxy for correctness than in v2.1. Treat shadow divergence as a *signal to investigate*, never as proof the classifier is wrong, and rely primarily on periodic human-annotated audits (Section 9). Also: the generator that produced most silver labels (2.0 Flash) shuts down June 1, so any shadow comparison runs against the migrated generator (2.5 Flash/Lite), which scores on a different rubric (OQ5).

**Implementation:** for the first 4 weeks post-deployment, shadow-score 10% of traffic with the single-call generator (scores computed, not used for routing). Compare:
- Per-dimension divergence: classifier vs generator disagree >0.3 on severity for >5% of weekly messages → investigate (stale classifier, prompt change, population shift).
- Path-distribution shift: a sudden LIGHTEN spike (>10% relative) suggests the classifier systematically underscores severity.
- Session-level outcomes: session length, return rate, satisfaction signals across cohorts.

Log to a `classifier_monitoring` collection for weekly review.

**After 4 weeks:** discontinue shadow scoring only if the classifier and current generator agree on severity within 0.2 for >90% of messages **and** the latest human audit shows MAEs within target. Never discontinue on generator-agreement alone.

### 8.3 The Moderate Severity Blind Spot

The most dangerous pattern is the moderate case, not the extreme one: true severity ≈0.7 (MOTIVATE/CONNECT territory) but the classifier says 0.4 (LIGHTEN). The user gets levity when they needed empathy, and the safety flag doesn't fire because 0.7 isn't crisis-level.

Partially mitigated by the Decision Engine's longitudinal adjustments (a user trending high-severity gets MOTIVATE/CONNECT boosted regardless of the current message). But new users with no trajectory have only the classifier's score.

**Mitigation:** oversample 0.5–0.8 in *both* training (Protocol A, human-annotated — Section 5.2) and the test set (≥100 examples). If MAE within 0.5–0.8 exceeds 0.15, **do not deploy** — add human-annotated examples in this band and retrain.

---

## 9. Iteration and Monitoring

### Post-Deployment Monitoring

- **Classifier–generator drift** (shadow scoring first 4 weeks, then spot-checks). Investigate beyond Section 8.2 thresholds.
- **Safety flag agreement rate** across classifier, keyword regex, generation heuristic. Disagreements logged, reviewed weekly.
- **Serving health (NeoBERT primary):** endpoint p95/p99 latency, error rate, GPU/CPU utilization, container cold-start frequency, OOM/restarts. Alert on latency or error-rate regressions.
- **JSON validation failure rate** — backup (Gemini) path only; alert >2%/1h.
- **Fallback rate** attributable to classifier timeouts/failures vs Phase 1 baseline.
- **User-facing metrics:** session length, return rate, path distribution. A LIGHTEN spike post-deploy suggests systematically low severity scores.
- **Per-dimension score distributions:** weekly histograms; shifts indicate population change or model drift.

### Retraining Cadence

- **Monthly:** append new silver labels; retrain if the dataset grew >20% since the last run.
- **Quarterly:** fresh human annotation pass (200–500 new examples, Protocol B methodology) to recalibrate against distribution shift.
- **Ad-hoc:** retrain immediately if safety recall drops below 0.95 in production, if a critical misclassification surfaces in safety review, or (backup path) if JSON validation failure exceeds 5% sustained.

Retraining is manual for Phase 4 (team-triggered after dashboard review). See OQ4 for the automation position.

### Experiment Tracking

- **NeoBERT path (primary):** Weights & Biases or MLflow — hyperparameters, per-epoch and per-seed metrics, confusion matrices, checkpoints.
- **Gemini path (backup):** Vertex AI Model Registry — each version links to its training-data GCS snapshot, tuning job ID, and eval results.

Every deployed version must trace to its training-data snapshot, config, and evaluation. No deployment without a completed Protocol B evaluation.

---

## 10. Timeline

| Week | Milestone | Who | Dependencies |
|---|---|---|---|
| **Week 1–2** | Silver-label collection running. Build annotation tool (Protocol A + B modes). Run the energy/severity independence check once ~1K labels exist. | Backend eng (tool, 2–3 days), AI eng (check) | Phase 1 in production, `training_data` collection live |
| **Week 3** | **Taxonomy pilot:** 100-message pilot (Protocol B). Label confusion rates; socialIsolation + receptivity alpha. **Decision gate:** finalize taxonomy, decide socialIsolation/receptivity viability. | 3 annotators (2 days), AI eng (1 day) | Tool built, 100+ labels |
| **Week 4** | **Protocol A annotation:** 500 anchored, incl. ~150 human-annotated in the 0.5–0.8 severity band. | 2 annotators (3–4 days) | Taxonomy finalized |
| **Week 5** | **Protocol B annotation:** 500 unanchored. Compute agreement; fix guidelines where alpha < 0.6 and re-annotate. | 3 annotators (5–6 days) | Taxonomy finalized |
| **Week 6** | **Safety augmentation:** Layers 1–3. Clinical reviewer reviews methodology *and* outputs. | AI eng (Layers 1–2), clinical reviewer (Layer 3) | Confirmed safety positives |
| **Week 7** | **Dataset prep + transfer pre-training:** filter/merge, user-level split, export. GoEmotions emotion-head pre-training. **Also run a quick Gemini-Lite SFT baseline** to set the fallback bar. | AI eng (3 days) | Annotation complete |
| **Week 8** | **NeoBERT multi-task training** (≥3 seeds) + hard-example mining + Protocol B eval. **Serving spike:** Track A (GPU) stand-up + Track B (CPU/ONNX) feasibility, timeboxed. | AI eng (4–5 days) | Pre-training done |
| **Week 9** | **Serving build + integration:** finalize Track A or B, build `/classify` container, deploy to staging, set up shadow scoring. End-to-end tests across all four paths + safety scenarios. | Backend + AI eng (4–5 days) | Model passes eval; serving track chosen |
| **Week 10** | Iterate on training/serving if eval or latency targets missed (second run / task-weighting / Track switch). | AI eng | Week 9 issues identified |
| **Week 11** | **Rollout 10%.** Shadow scoring active. Monitor safety agreement, path distribution, serving health, latency. | AI eng | Staging clean |
| **Week 12** | **Rollout 50%.** Review Week 11 data. Proceed only if no safety regressions and path-distribution shift < 10% relative. | AI eng + product | Week 11 clean |
| **Week 13–14** | **Rollout 100%.** Shadow scoring continues 2 more weeks. | AI eng | Week 12 clean |

**Total: ~14 weeks** for the NeoBERT path (vs ~12 for the Gemini backup). The extra ~2 weeks are entirely serving: the GPU/CPU stand-up, the ONNX feasibility spike, and the iteration buffer for from-scratch heads on a small dataset. If at the Week-8 gate NeoBERT underperforms the Gemini-Lite baseline or serving proves intractable, pivoting to the backup path recovers most of that time.

**Week 0 / pre-work (do not start the 12–14-week plan without these):**

- **Generator migration off Gemini 2.0 Flash before June 1, 2026.** Independent of the classifier, but it blocks coherent silver-label collection and the shadow baseline. **Top priority, immediate.** (OQ5)
- **NeoBERT serving-infrastructure direction** (GPU baseline vs CPU/ONNX ambition; Cloud Run vs Vertex endpoint) — scope and budget before Week 8. (OQ6)
- **Energy/severity correlation check** (Section 5.2) — gates whether the energy head exists. Week 1–2.
- **Mixed-silver-label provenance decision** (OQ5) — settle before accumulating significant post-migration training data.
- **Clinical reviewer contracted by Week 3** (start sourcing Week 1). (OQ2)
- **Annotation hiring channel decided Week 1**, 3 raters budgeted for unanchored work. (OQ3)

---

## 11. Open Questions — Recommended Resolutions

Items still needing sign-off are flagged **[DECISION NEEDED]**.

**1. TalkLife dataset access → Try, keep off the critical path; treat as nice-to-have.**

Initiate the DUA request Week 1 but plan as if denied. The labels sit on the *supporter's* response (inference-reversal needed for a weak `receptivity` signal — our weakest dimension); a *commercial* DUA for a mental-health peer-support corpus is unlikely and slow; and consent concerns are real (users consented to peer support, not to training a commercial product). Given the `receptivity` gate (3.4) may collapse the dimension anyway, this is poorly justified to chase. Anchor `receptivity` on human annotation + DailyDialog (noisy). **Low-priority request, no dependency.**

**2. Clinical reviewer → Contract one licensed individual with crisis/suicidology expertise; resolve by Week 3.**

Not a generic telehealth clinician (lacks risk-assessment specialization) and not a university partnership (IRB/academic timelines miss our dates). 20–30 hours is too small for a consultancy's overhead. Source one individual with C-SSRS/Columbia-Protocol familiarity. **Resolve by Week 3, not Week 5** (contracting + NDA + onboarding eats a week). Have them review the **Layer-3 generation methodology *before* generation**, not only the outputs. Scope the engagement in writing as training-label review only — not clinical care, not a product safety endorsement. **[DECISION NEEDED]** budget (~$2–5K) and sourcing channel.

**3. Annotation staffing → 2–3 contract annotators with mental-health background; decide Week 1. Not a labeling service.**

Scale/Surge is wrong here: 1,100 examples is too small to amortize vendor onboarding, crowd workers on crisis content raise quality + welfare problems, and the alpha gates need stable trained raters. Internal staff disrupt Phase 4 and may lack calibration. Contract annotators (psych grad students, trained crisis-line volunteers) with a 1–2-week lead → decide Week 1. **Budget 3 raters for the pilot and Protocol B** (two-rater alpha is too noisy). Implement the wellbeing protocol (5.2). Keep the safety-positive confirmation annotator separate. **[DECISION NEEDED]** hiring channel + budget, by Week 1.

**4. Retraining automation → Automate retraining after ~3 clean cycles; keep deployment human-gated indefinitely for any safety-bearing version.**

Separate *automating retraining* (fine after 3 stable manual cycles) from *automating deployment* (keep a human gate indefinitely for any version whose output serves as a safety signal). An automated pipeline retraining on drifted data can silently lower safety recall; never auto-deploy a version whose safety recall isn't re-verified against a *fresh human-annotated* test set — and that quarterly refresh (Section 9) is the irreducibly manual, expensive step, which automation does not remove. Automation mostly saves orchestration time → modest ROI → deprioritize. Revisit at Phase 5 with a permanent human deployment gate on safety.

**5. Generator version coupling → The classifier is now decoupled at inference; the generator migration is still urgent, and silver-label provenance still matters.**

Choosing NeoBERT removes Gemini from the *inference* path entirely — generator deprecations no longer touch routing. But three coupling points remain:
- **The generator must still migrate off Gemini 2.0 Flash before June 1, 2026** (deprecated Feb 18, 2026; hard shutdown June 1 — ~3 days out). This is a product issue regardless of the classifier. Replacement: `gemini-2.5-flash-lite` (same price as old 2.0 Flash) or `gemini-2.5-flash` (better quality, ~3× input / ~6× output cost, set `thinkingBudget: 0`). **[DECISION NEEDED]** generator replacement + re-derived cost model.
- **Silver-label provenance.** Training targets are still Gemini-generated. If Phase 1–3 spans June 1, labels are mixed-provenance (2.0 Flash + 2.5 successor). When the generator migrates, **re-score a stratified sample of pre-migration silver labels with the new generator and measure per-dimension divergence.** MAE < ~0.1 → mix freely; larger → prefer post-migration labels and down-weight/discard old ones.
- **Shadow baseline** runs against the migrated generator, not 2.0 Flash (Section 8.2) — and with a NeoBERT classifier vs a Gemini generator, agreement is a weak correctness signal anyway.

**6. NeoBERT serving infrastructure → [DECISION NEEDED] — the biggest new open question.**

Choosing a self-hosted encoder reintroduces the serving burden Flash-Lite avoided. Decide before Week 8:
- **GPU vs CPU.** Baseline assumption: GPU FP16 (NVIDIA L4) on Cloud Run or a Vertex endpoint, `min-instances ≥ 1`, ~$X00/month. CPU INT8 ONNX is the cost-optimization ambition but is **unproven for NeoBERT** (FlashAttention/xformers/custom modeling code) — a timeboxed Week-8 spike, not a plan.
- **Platform.** Cloud Run GPU (simpler, scale-to-near-zero, cold-start risk) vs Vertex endpoint (managed, pricier, steadier latency).
- **Cost reconciliation.** Re-derive the architecture cost model: at 500 DAU this is likely *more* expensive than Flash-Lite per-token pricing. Confirm the team accepts the fixed-infra cost as the price of decoupling and consistency.
- **Fallback ladder if serving is intractable:** NeoBERT-GPU → ModernBERT (proven CPU/ONNX, smaller) → Gemini Flash-Lite backup. Decide the trigger thresholds in advance so the fallback is data-driven, not late.

**Highest-priority actions:** (a) migrate the generator off 2.0 Flash this week; (b) settle the NeoBERT serving direction and its cost before Week 8; (c) run the Gemini-Lite baseline in Week 7 so the NeoBERT-vs-backup decision at the Week-8 gate is evidence-based.
