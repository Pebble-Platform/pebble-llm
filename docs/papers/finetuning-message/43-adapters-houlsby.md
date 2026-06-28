# Paper 43 — Adapters: Parameter-Efficient Transfer Learning for NLP

> Family A (PEFT / fine-tuning recipes) · Pillar: staged/efficient fine-tuning. Analysis depth: abstract + method (verified). Compiled 2026-06-25.

## Bibliographic info
- **Authors / Year / Venue:** Houlsby, Giurgiu, Jastrzębski, Morrone, de Laroussilhe, Gesmundo, Attariyan, Gelly. ICML 2019 (PMLR v97).
- **Link:** [arXiv:1902.00751](https://arxiv.org/abs/1902.00751) · [PMLR v97 (ICML 2019)](https://proceedings.mlr.press/v97/houlsby19a.html) · reference impl. [google-research/adapter-bert](https://github.com/google-research/adapter-bert) · open. (VERIFIED — venue, author list, and the "within 0.4% of full FT / 3.6% params" headline cross-checked against arXiv abstract + Semantic Scholar + ICML proceedings.)
- **R2 pillar:** parameter-efficient warm-start of the per-post encoder — an alternative to R2's current "freeze embeddings + first 6 layers" strategy (W2 framing).

## Summary
Inserts a small **bottleneck adapter** module *inside every transformer layer* of a frozen pretrained encoder (two per layer in BERT: one after the multi-head-attention projection, one after the feed-forward block). Each adapter is `down-project (d→m) → nonlinearity → up-project (m→d)` with a **residual skip**, where the bottleneck dim `m ≪ d` (e.g. m=64 for d=768); the near-identity init (small weights + skip) means an untrained adapter ≈ pass-through, so training stays stable. During fine-tuning **all original encoder weights are frozen**; only the adapters, layer-norms, and the task head are trained — **~3.6% of params per task**, reaching **within 0.4% of full fine-tuning on GLUE** (BERT-Large). The point is parameter efficiency + per-task modularity without catastrophic forgetting, not SOTA accuracy.

## Overlap with Pebble/R2 — 19% (peripheral)
`D1=1, D2=0, D3=0, D4=0, D5=0, D6=0, D7=2` → (3·1 + 1·2)/26 = 5/26 = **19%**
- **Closest on:** D7 (backbone — BERT/RoBERTa family, exactly R2's MentalRoBERTa per-post encoder) and weakly D1 (adapters are a *shared-trunk-with-task-modules* pattern, conceptually adjacent to R2's shared encoder feeding two heads, but the paper is single-head text classification).
- **Why low:** zero mental-health/crisis content (D2), no emotion corpora (D3), no LLM distillation (D4), no MTL loss balancing (D5), no safety/recall constraint (D6). It is a pure methodology paper about *how to fine-tune efficiently*, which is the one axis where it touches R2.

## Best point — Method to adopt (efficient warm-start under tiny target data)
Bottleneck adapters let you adapt a frozen BERT/RoBERTa encoder by training only ~3.6% of its parameters and still land within ~0.4% of full fine-tuning — a regularizer that resists forgetting/overfit on small target sets, which is exactly R2's regime (CSSRS-500 gold + LLM-labeled pool, a few thousand sequences).
- **How to apply to Pebble/R2:** Replace R2's blunt "freeze first 6 layers, fully train the top 6" split with adapters in *all 12* MentalRoBERTa layers (keeping the whole encoder frozen). This trains far fewer encoder params than the current 6-unfrozen-layer setup while letting *every* layer adapt a little — a better fit for the tiny, imbalanced data driving the Behavior collapse (W1) and over-fit risk.

## ▶ Apply to R2 (MANDATORY)
Target file: `kaggle/finetuning-message/r2-suicide-risk-dualhead/r2-suicide-risk-dualhead.py` (mirror `notebooks/r2-suicide-risk-dualhead.py`). The change is **localized to `HierarchicalDualHead.__init__` / `_freeze` and `make_optim`** — the sequence transformer, attention pooling, CORAL/CE/Focal heads, and tri-objective loss are untouched.

**Current vs adapters:**
- R2 today (`Config.freeze_layers=6`, `HierarchicalDualHead._freeze`): embeddings + encoder layers 0–5 frozen, layers 6–11 fully trainable (≈ half of a 12-layer RoBERTa-base = tens of millions of trainable encoder params). `make_optim` splits params into `encoder.*` (lr 2e-5) vs new (lr 1e-4).
- Adapters: **freeze the entire `self.encoder`** (all 12 layers + embeddings), then inject a bottleneck module after the attention output and after the FFN of each layer. Only adapters + LayerNorms + the existing R2 heads train.

**Concrete change:**
1. Add `adapter_dim: int = 64` and an `R2_ADAPTER` env flag to `Config`.
2. In `HierarchicalDualHead.__init__`, when `R2_ADAPTER`: after `AutoModel.from_pretrained`, set `requires_grad=False` on **all** `self.encoder` params (replace the partial `_freeze(k)` call), un-freeze the encoder's LayerNorms, and register-forward-hook a `nn.Sequential(Linear(h, adapter_dim), GELU(), Linear(adapter_dim, h))` (near-zero init on the up-projection so it starts as identity + residual `x + adapter(x)`) on each `encoder.encoder.layer[i].attention.output` and `…layer[i].output`. This is the cleanest no-fork route on HF RoBERTa; alternatively swap to the `adapters` library `add_adapter("r2", config=BnConfig(reduction_factor=12))`.
3. In `make_optim`, the existing `if not p.requires_grad: continue` filter already excludes the frozen encoder, so adapter params (named under `encoder.*`) automatically land in the `enc` group at `lr_encoder`. Optionally bump them to `lr_new=1e-4` (adapters tolerate higher LRs since the backbone is frozen) by routing adapter params to the `new` group.

**Comparison to R2's freeze-6 strategy:** freeze-6 is a coarse depth cut — lower-layer syntax frozen, upper-layer semantics fully retrained, which is the regime where small noisy data over-fits the top half. Adapters keep *all* layers frozen and add a thin, near-identity adaptation everywhere, training ~10–30× fewer encoder params. ULMFiT's Table 7 (paper 20) warns that "head-only" probing under-fits small NLP data; adapters sit between "head-only" and "unfreeze-half" and are the principled middle option for R2's data scale.

## ▶ Kaggle experiment (MANDATORY)
- **Ablation (isolated):** encoder adaptation strategy only. Arm A = current `R2_BALANCE=1 R2_GOLD_HOLDOUT=1` freeze-6 baseline (gold macro-F1 0.3849). Arm B = same config + `R2_ADAPTER=1` (whole encoder frozen, adapter_dim=64). Everything else identical: same MentalRoBERTa mirror (`R2_MODEL` default), max_length=256, tri-objective loss weights, 5-fold gold-holdout CV, seed 42. The *only* moving part is freeze-6-layers → adapters.
- **Env/config diff:** `R2_ADAPTER=1`, add `adapter_dim=64`; leave `R2_GOLD_HOLDOUT=1 R2_BALANCE=1 R2_EPOCHS=10`. Optionally a sub-arm with `adapter_dim=16` (cheaper) to sweep capacity.
- **Expected signal:** gold macro-F1 **≈ baseline ±0.02** (the paper's claim is ~0.4% off full FT; for R2 the realistic hope is parity, not a jump) with **lower fold variance / less over-fit gap** between val-on-LLM (0.666) and gold (0.385) — that gap is an over-fit symptom adapters should narrow. Watch per-class **Behavior F1 (0.183, the bottleneck)**: adapters won't fix W1 (a label-quality problem), so flat Behavior = expected and confirms W1 is not an encoder-capacity issue.
- **Cost:** ~same wall-clock as baseline (forward pass unchanged; backward is *cheaper* — fewer trainable params). One Kaggle GPU run, ~10 epochs × 5 folds, well within a single ≤9h session. Low risk: the change is reversible behind `R2_ADAPTER` and touches only encoder freezing + optimizer grouping.

## Caveats
- **Verification:** title/authors/venue (ICML 2019, PMLR v97) and the "3.6% params / within 0.4% of full FT on GLUE" headline are verified against arXiv:1902.00751 + ICML proceedings + Semantic Scholar. The exact adapter insertion points and near-identity init are taken from the published method (and `google-research/adapter-bert`), not re-derived line-by-line from a full-PDF read — depth here is abstract + method, not deep-PDF.
- **What does NOT transfer:** (1) the paper is **single-task, single-head** text classification — it says nothing about R2's hierarchical sequence transformer, CORAL ordinal head, or tri-objective loss; adapters only touch the per-post encoder, not the parts that drive ordinal QWK/MAE. (2) Zero evidence on **class imbalance / Behavior collapse (W1)** — adapters change *which* params adapt, not label quality, so they cannot be expected to fix the bottleneck. (3) GLUE is large, balanced, adult-register data; the "within 0.4%" margin is **not guaranteed** to hold on R2's tiny imbalanced clinical set — parity is a hypothesis to test, not a result. (4) Adapters address W2 only *partially*: they improve the freeze strategy but do nothing about the mirror-vs-gated-checkpoint issue or max_length=256. (5) Nothing for W3 (Δt temporal head) or W4 (single-LLM labels / κ).
