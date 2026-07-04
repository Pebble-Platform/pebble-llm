# Paper 44 — BitFit: Simple Parameter-efficient Fine-tuning for Transformer-based Masked Language-models

> Family A (PEFT / fine-tuning recipes). Analysis depth: abstract + ar5iv full-text + ACL/arXiv verification. Compiled 2026-06-25.

## Bibliographic info
- **Authors / Year / Venue:** Elad Ben Zaken, Yoav Goldberg, Shauli Ravfogel. ACL 2022 (Proceedings of the 60th Annual Meeting of the ACL, Vol. 2: Short Papers, pages 1–9, Dublin).
- **Link:** [arXiv:2106.10199](https://arxiv.org/abs/2106.10199) · [ACL 2022.acl-short.1](https://aclanthology.org/2022.acl-short.1/) · open. **VERIFIED** (both resolve to the same paper; author copy at nlp.biu.ac.il/~yogo/bitfit.pdf).
- **R2 pillar:** staged fine-tuning / freeze policy — a bias-only PEFT alternative to R2's current freeze-6 schedule, targeting the small-gold overfit regime (W4-adjacent, W2-adjacent).

## Summary
BitFit freezes **all** weight matrices of a pre-trained transformer and fine-tunes **only the additive bias vectors** (plus the task-specific head). On BERT_LARGE the trainable biases are **~0.08–0.09%** of all parameters; a smaller subset — the attention **query bias `b_q`** and the **second-FFN/output-MLP bias `b_m2`** — is **~0.04%** and still rivals full fine-tuning. Per transformer block the bias vectors are: attention `b_q`/`b_k`/`b_v`, attention-output dense `b_{m1}` + LayerNorm `b_{LN1}`, FFN dense `b_{m2}`/`b_{m3}` + LayerNorm `b_{LN2}`. The headline finding is a **data-size crossover**: "BitFit dominates over Full-FT in the smaller-data regime, while the trend is reversed when more training data is available" (SQuAD size sweep), supporting the view that fine-tuning mostly *exposes* knowledge already in the LM rather than learning new linguistic knowledge.

## Overlap with Pebble/R2 — 12% (peripheral)
`D1=0, D2=1, D3=0, D4=0, D5=0, D6=0, D7=2` → (2·1 + 1·2)/26 = 4/26 = **12%**
- **Closest on:** D7 (BERT/RoBERTa-class masked-LM encoder — exactly MentalRoBERTa's family, so the bias-term map transfers 1:1 to R2's per-post encoder) and a partial D2 (their MLM-encoder transfer-learning setting is the same paradigm R2 fine-tunes in, though BitFit's tasks are GLUE/SQuAD, not mental-health).
- The score is low because BitFit is single-task, single-encoder classification with no MTL heads (D1=0), no teacher-LLM distillation (D4=0), no loss balancing (D5=0), no safety/recall objective (D6=0). Its value to R2 is purely the **freeze policy**, not the task design.

## Best point — Method to adopt (PEFT freeze policy for the small-gold regime)
Bias-only fine-tuning: freeze every encoder weight matrix, train only the bias vectors + the heads. The data-size crossover is the decision-relevant claim — BitFit **beats** full fine-tuning precisely when the labeled set is small/medium, which is R2's gold-holdout reality (a few hundred clinical CSSRS-500 rows, ~250M-param encoder). This directly attacks R2's overfit risk on the gold set, where freeze-6 still leaves 6 full encoder layers + embeddings'-half worth of weights trainable.
- **How to apply to Pebble:** add a `R2_FREEZE_MODE=bitfit` arm to `HierarchicalDualHead._freeze` that sets `requires_grad=False` on all encoder params **except** those whose name ends in `.bias`; everything above the encoder (seq Transformer, attn pooling, CORAL/CE heads, feature MLP) stays trainable. This is the cheapest possible regularizer to test against freeze-6 on the gold-holdout protocol.

## ▶ Apply to R2 (MANDATORY)

**Current behavior (`_freeze`, lines 321–328).** Freezes `embeddings.*` and encoder layers with index `< freeze_layers` (=6). Encoder layers 6–11 are fully trainable (all weights + biases). `make_optim` (lines 384–401) then splits trainable params into two groups: `encoder.*` at `lr_encoder=2e-5`, everything else at `lr_new=1e-4`. So today R2 trains ~half the encoder's full weight matrices.

**BitFit change — make `_freeze` mode-switchable.** Add an env-gated branch; do not change the default. Concretely, in `Config` add `freeze_mode: str = os.environ.get("R2_FREEZE_MODE", "layers")` and rewrite `_freeze`:

```python
def _freeze(self, k: int):
    if self.cfg.freeze_mode == "bitfit":
        for name, p in self.encoder.named_parameters():
            p.requires_grad = name.endswith(".bias")   # train ONLY bias vectors
        return
    # default: existing freeze-k (embeddings + first k layers)
    for name, p in self.encoder.named_parameters():
        if name.startswith("embeddings"):
            p.requires_grad = False
        elif ".layer." in name:
            li = int(name.split(".layer.")[1].split(".")[0])
            if li < k:
                p.requires_grad = False
```

(RoBERTa bias param names are `roberta.encoder.layer.{i}.attention.self.query.bias`, `...attention.output.dense.bias`, `...attention.output.LayerNorm.bias`, `...intermediate.dense.bias`, `...output.dense.bias`, `...output.LayerNorm.bias`, plus `embeddings.LayerNorm.bias`. `name.endswith(".bias")` captures all of them.)

**`make_optim` interaction (lines 384–401).** No code change required — it already skips `not p.requires_grad` params, so in bitfit mode the `encoder.*` group collapses to just the bias vectors. **But** `lr_encoder=2e-5` is tuned for full-weight updates; BitFit papers use a higher LR for biases-only. Optional second arm: bump the encoder-group LR to ~1e-3 for the bitfit mode (biases are few and need a larger step). Keep `lr_new=1e-4` for the heads/seq-Transformer unchanged.

**Contrast with freeze-6.** freeze-6 trains the *full weight matrices* of layers 6–11 (~42M params on a base encoder). BitFit trains only the bias vectors across **all** 12 layers (~0.08% of the encoder ≈ tens of thousands of params). Same encoder family, far fewer trainable params, every layer's biases adapt instead of only the top half's weights — a much stronger regularizer for the small gold set.

**Optional ablation refinement.** Add a `bitfit-min` variant that trains only `b_q` (attention query bias) + `b_m2` (the `intermediate.dense.bias`, i.e. the first FFN bias the paper labels the "second MLP layer") — `name.endswith(("attention.self.query.bias", "intermediate.dense.bias"))` — the ~0.04% subset, to test whether R2 needs full-bias or the minimal subset.

## ▶ Kaggle experiment (MANDATORY)

**Goal:** does bias-only encoder fine-tuning beat freeze-6 on the **gold-holdout** protocol (the honest, non-circular metric), especially on the Behavior bottleneck and overall overfit?

- **Config diff:** identical kernel as Run B. Three arms, one variable (`R2_FREEZE_MODE`):
  - **A (baseline):** `R2_FREEZE_MODE=layers` (current freeze-6) — already have this (gold macro-F1 0.3849).
  - **B (bitfit):** `R2_FREEZE_MODE=bitfit` (all encoder biases) + encoder-group LR raised to ~1e-3.
  - **C (bitfit-min):** `R2_FREEZE_MODE=bitfit-min` (`b_q` + `b_m2` only).
  - Hold everything else fixed: `R2_GOLD_HOLDOUT=1 R2_BALANCE=1 R2_EPOCHS=10`, `R2_MODEL` unchanged, same 5-fold StratifiedKFold seed=42, `max_length=256`, tri-objective weights unchanged.
- **Ablation isolated:** only the encoder freeze policy (and its matched LR) changes; the seq Transformer, pooling, heads, losses, sampler, and data are constant — so any gold-F1 delta is attributable to the freeze policy alone.
- **Expected signal:** on the small gold set BitFit should reduce overfitting → the `val-on-LLM (0.666)` vs `gold (0.3849)` generalization gap should **narrow** even if peak val drops. Watch (i) **gold macro-F1** mean/std across folds, (ii) **Behavior per-class F1** (0.183 bottleneck — BitFit's milder adaptation may help or hurt; report it separately), (iii) **QWK/MAE** (ordinal coherence should be stable since CORAL/CE heads are untouched). Realistic outcome: BitFit ties or modestly beats freeze-6 on gold with **lower variance** — the paper's small-data crossover predicts a tie-or-win here, not a large jump. Overfit risk is *lower* than baseline by construction; the real risk is **underfitting** (biases-only may lack capacity for the domain shift to clinical Reddit), which arm C stresses hardest.
- **Cost:** cheapest arm in the family — bias-only means far fewer trainable params, lower memory, and same or faster wall-clock than freeze-6 (no extra forward/backward machinery). ~1 GPU-run per arm on the existing kernel; 2 new arms (B, C) ≈ 2 Kaggle GPU sessions. No new data, no new dependencies.

## Caveats
- **Verification:** citation/venue/authors and the 0.08–0.09% / 0.04% / `b_q`+`b_m2` / small-data-crossover facts are VERIFIED against arXiv:2106.10199, ACL 2022.acl-short.1, and the ar5iv full-text HTML. The author-PDF (nlp.biu.ac.il) returned binary and was not line-read; numbers come from the ar5iv render + ACL abstract, which agree.
- **What does NOT transfer:** (1) BitFit is validated on **GLUE/SQuAD** (adult-register topic/QA/NLI), never on mental-health, ordinal C-SSRS, or hierarchical post-sequence models — the *accuracy* claims do not carry over; only the freeze mechanism + the small-data-crossover heuristic do. (2) The crossover is about the *labeled-task* data size; R2's gold pool is small (favors BitFit) but the LLM-labeled training pool (av9ash+scraped) is medium — if folds train mostly on the larger LLM pool, the paper predicts the advantage **shrinks**, so the win is not guaranteed. (3) BitFit is single-encoder, single-task; R2 stacks a 3-layer seq Transformer + attn pooling + dual ordinal heads **on top** of the encoder. BitFit only governs the *per-post encoder*; the entire hierarchical stack above stays fully trainable, so this is "PEFT the encoder, full-train the head-stack," a hybrid the paper does not study. (4) BitFit does not address W1 (Behavior label quality), W3 (Δt=0), or W4 (single-LLM labels) — it is purely an overfit/freeze-policy lever (W2-adjacent). (5) The optional `b_q`+`b_m2` subset claim is for *full* fine-tuning quality; the paper itself notes a counter-test where excluding `b_m2`/`b_q` still worked, so treat the minimal subset as exploratory, not a guaranteed equivalent.
