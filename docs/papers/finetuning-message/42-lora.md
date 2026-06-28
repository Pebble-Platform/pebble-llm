# Paper 42 — LoRA: Low-Rank Adaptation of Large Language Models

> Family A (PEFT / fine-tuning recipes) · Pillar D-E (parameter-efficient warm-start). Analysis depth: abstract + OpenReview-verified. Compiled 2026-06-25.

## Bibliographic info
- **Authors / Year / Venue:** Hu, Shen, Wallis, Allen-Zhu, Li, Wang, Wang & Chen. 2021 (arXiv) / **ICLR 2022** (published).
- **Link:** [arXiv:2106.09685](https://arxiv.org/abs/2106.09685) · [OpenReview ICLR 2022 (id nZeVKeeFYf9)](https://openreview.net/pdf?id=nZeVKeeFYf9) · open. VERIFIED via WebFetch (arXiv) + WebSearch (ICLR/OpenReview).
- **R2 pillar:** parameter-efficient fine-tuning of the per-post encoder — frees layers to train without the memory/overfit cost of full fine-tuning.

## Summary
LoRA freezes the pretrained weight `W₀ ∈ ℝ^{d×k}` and learns a **low-rank update** `ΔW = B·A` with `B ∈ ℝ^{d×r}`, `A ∈ ℝ^{r×k}`, `r ≪ min(d,k)`; the forward pass becomes `h = W₀x + (α/r)·BAx`, where `A` is Gaussian-init and `B` is zero-init (so ΔW=0 at start) and `α/r` is a fixed scaling. Only `A,B` are trained — for GPT-3 175B this cuts trainable params ~10,000× and optimizer-state memory ~3× while matching or beating full fine-tuning quality, with **no added inference latency** (BA can be merged back into W₀). On RoBERTa/DeBERTa GLUE it ties full fine-tuning at a tiny fraction of trainable parameters; the standard recipe adapts the attention projection matrices (`W_q`, `W_v`) at small rank (r=4–8).

## Overlap with Pebble/R2 — 4% (peripheral)
`D1=0, D2=0, D3=0, D4=0, D5=0, D6=0, D7=1` → (1·1)/26 = 1/26 = **4%**
- **Closest on:** D7 only, and partial — LoRA is validated on RoBERTa/DeBERTa-class encoders (exactly R2's MentalRoBERTa backbone family), but it is a *fine-tuning method*, not a backbone, and touches none of R2's domain/head/loss content.
- Pure PEFT methodology paper: zero mental-health, zero multi-head, zero ordinal/loss-balancing, zero teacher-LLM content. Value is a citable, drop-in training-efficiency lever, same role as ULMFiT (paper 20) — a method-citation anchor, not a domain match.

## Best point — Method to adopt
Replace R2's coarse "freeze first 6 layers" trick with **LoRA adapters on the encoder's attention projections (`query`, `value`, r=8, α=16)**, leaving `W₀` frozen — this lets *every* encoder layer adapt to the clinical register at a fraction of the trainable params, directly attacking W2 (encoder is a frozen-bottom mirror with limited capacity to specialize) without inflating overfit risk on the small gold set.
- **How to apply to Pebble:** wrap `self.encoder`'s `q`/`v` Linear layers with LoRA via `peft.get_peft_model(...)` in `HierarchicalDualHead.__init__`, drop the static `_freeze` cutoff, and route the LoRA params into the `lr_new` group in `make_optim`.

## ▶ Apply to R2
Concrete, surgical change in `kaggle/finetuning-message/r2-suicide-risk-dualhead/r2-suicide-risk-dualhead.py` (mirror `notebooks/`):

1. **Config:** add `use_lora: bool = bool(int(os.environ.get("R2_LORA", "0")))`, `lora_r: int = 8`, `lora_alpha: int = 16`, `lora_dropout: float = 0.05`. Keep `R2_LORA=0` as the default so existing runs are untouched.
2. **`HierarchicalDualHead.__init__`:** after `self.encoder = AutoModel.from_pretrained(...)`, if `cfg.use_lora`, wrap it:
   ```python
   from peft import LoraConfig, get_peft_model
   self.encoder = get_peft_model(self.encoder, LoraConfig(
       r=cfg.lora_r, lora_alpha=cfg.lora_alpha, lora_dropout=cfg.lora_dropout,
       target_modules=["query", "value"], bias="none"))
   ```
   When `cfg.use_lora` is true, **skip `self._freeze(...)`** — LoRA already freezes `W₀`; only A/B and the new heads train. (`_freeze` matches on `name.startswith("embeddings")` / `.layer.`; PEFT renames params to `base_model.model.encoder.layer.*`, so the existing freeze logic would silently no-op — guard it with `if not cfg.use_lora`.)
3. **`make_optim`:** LoRA params live under `encoder.` but should learn at the *new-param* rate, not `lr_encoder=2e-5`. Change the split to route LoRA params to the `new` group: `(enc if (n.startswith("encoder.") and "lora_" not in n) else new)`. LoRA typically wants a higher LR (≈1e-4–3e-4), so `lr_new` is the right bucket.
4. **`train_fold` / pip:** add `peft>=0.11` to the Kaggle `pip install` line (block at L35). No other change — the tri-objective loss, CORAL/CE/focal heads, sampler, and gold-holdout flow are all untouched.

## ▶ Kaggle experiment
- **Run:** `R2_LORA=1 R2_GOLD_HOLDOUT=1 R2_BALANCE=1 R2_EPOCHS=10` (LoRA r=8, α=16 on q,v), compared head-to-head against the current Run B (`R2_LORA=0`, freeze-6) under the *identical* 5-fold gold-holdout split.
- **Ablation it isolates:** "full-depth LoRA adaptation vs static freeze-6 of the same MentalRoBERTa mirror" — same backbone, same data, same loss, same eval; the only moving part is how the encoder is adapted. Optional second cell: r∈{4,8,16} mini-sweep to check rank sensitivity.
- **Expected signal:** GOLD macro-F1 and QWK are the headline metrics to watch; the hypothesis is that letting deep layers adapt (currently frozen 0–5) lifts the under-served minority classes — primarily Ideation/Attempt, and possibly nudges the **Behavior** cell (0.183 bottleneck) if the collapse is partly capacity-limited rather than purely label noise (W1). A *null* result is itself informative: it argues Behavior collapse is label quality, not encoder capacity, redirecting effort to W1.
- **Cost:** ~same or slightly *cheaper* than Run B (fewer trainable params → lower optimizer memory; one extra `peft` install). ~1 GPU-hour for the 5-fold run on Kaggle T4/P100.

## Caveats
- **Verification status:** title/authors/method via WebFetch of arXiv abstract; ICLR 2022 venue + OpenReview id `nZeVKeeFYf9` via WebSearch. Method constants (zero-init B, α/r scaling, q/v-only adaptation, r=4–8) are the well-known published recipe, not re-verified line-by-line from the full PDF.
- **Preprint/venue delta:** none material — the ICLR 2022 camera-ready is the canonical version of arXiv:2106.09685; no number used here is contested between them.
- **What does NOT transfer:** every LoRA result is on *large decoder LMs* (GPT-2/3) and *adult-register GLUE* with full single-task fine-tuning. The 10,000× param saving is a 175B-model claim — on a ~125M RoBERTa-base encoder the absolute memory win is small, so LoRA's value for R2 is **adaptation reach + overfit control on a tiny gold set**, not memory. It says nothing about ordinal heads, MTL loss balancing (D5), crisis-recall constraints (D6), or the dual-head pooling stack — those stay exactly as-is. Whether full-depth LoRA beats freeze-6 on R2's small, noisy, clinical data is an open hypothesis, not an established result; treat the experiment as a test, not a guaranteed win.
