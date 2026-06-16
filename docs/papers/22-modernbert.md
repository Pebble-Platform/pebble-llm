# Paper 22 — ModernBERT: A Modern Bidirectional Encoder

> Enrichment set · Pillar 7 (encoder backbone). Analysis depth: abstract-only. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Warner et al. 2024.
- **Link:** [arXiv:2412.13663](https://arxiv.org/pdf/2412.13663) · open · weights on HF (base 149M / large 395M)
- **Pebble pillar:** alternative encoder backbone / baseline vs NeoBERT.

## Summary
An efficient encoder-only transformer (GeGLU, RoPE, alternating local-global attention, full unpadding) trained with MLM on 2T tokens, native 8,192-token context, SOTA classification/retrieval, best-in-class GPU efficiency. Released base (149M) and large (395M).

## Overlap with Pebble — 8% (peripheral)
`D1=0, D2=0, D3=0, D4=0, D5=0, D6=0, D7=2` → (1·2)/26 = 2/26 = **8%**
- **Closest on:** D7 only — same class of modern encoder as NeoBERT (named in the rubric); base/large bracket NeoBERT's ~250M.

## Best point — Baseline to beat
The strongest publicly available same-size-class encoder alternative to NeoBERT, with long (8K) context.
- **How to apply to Pebble:** Add ModernBERT-base/large as the head-to-head backbone baseline — fine-tune the identical three-head stack and report whether NeoBERT actually beats it, so the backbone choice is evidence-backed not assumed. Its long context is the natural fallback if multi-turn inputs exceed NeoBERT's window.

## Dataset
Backbone paper — no dataset to acquire.

## Caveats
Abstract-only, but the abstract fully determines D1–D6 absent / D7 strong, so score confidence is high. ModernBERT contributes no method on Pebble's core questions (heterogeneous MTL, distillation, crisis-recall) — value is purely backbone/baseline + efficiency reference.

## Deep research — full-PDF read (2026-06-16)

> Focus: **D-A** (encoder backbone choice). This section settles the question Pebble will be asked
> at review — "why NeoBERT and not ModernBERT?" — by laying the two encoders side by side on
> architecture, context length, efficiency, license, and (crucially) what evidence would actually
> decide it. ModernBERT is the strongest same-class alternative to NeoBERT, so this is the most
> load-bearing backbone comparison in the set. Append-only; cross-refs point back to §§ above.

### Source-access note

Read from the local PDF `pdfs/22-modernbert.pdf` via `pdftotext` — this is **arXiv:2412.13663 v2
(19 Dec 2024)**, the preprint. Every number below carries a Table/Section ref from that text.
Two-part validation:

- **Provenance.** The paper was subsequently **published in Findings of the ACL 2025** (same title,
  Warner et al.). Web-validation surfaced one preprint-vs-secondary-source delta: the Answer.AI launch
  blog reports **GLUE-base = 88.5**, while the PDF's Table 1 / Table 5 report **88.4** — a 0.1 rounding
  delta, immaterial to the decision. Status of the 88.4 number: ≈ approximate (preprint; blog rounds to 88.5).
  - Trace: WebSearch `"ModernBERT GLUE base 88.4 DeBERTaV3 8192 context Warner 2024 ACL published"` →
    https://www.answer.ai/posts/2024-12-19-modernbert.html (blog 88.5) and
    https://aclanthology.org/2025.ijcnlp-long.164/ (confirms ModernBERT-vs-DeBERTaV3 line of work).
- **NeoBERT side of the head-to-head** validated against the NeoBERT paper itself
  (arXiv:2502.19587 v2, 6 Jun 2025): 250M params, 4,096 ctx, two-stage pretraining, and the explicit
  claim that NeoBERT "achieves state-of-the-art results on the massive MTEB benchmark, **outperforming
  BERT large, RoBERTa large, NomicBERT, and ModernBERT under identical fine-tuning conditions**."
  Status: ✔ corroborated (this is the single most important fact for D-A — see Limitations).
  - Trace: WebSearch `"NeoBERT 250M 4096 context 2.1 trillion tokens GLUE MTEB encoder"` →
    https://arxiv.org/abs/2502.19587.

### What the paper actually does

**Claim.** A Pareto-improved encoder-only transformer ("BERT, modernized") — better downstream
*and* faster/leaner than every prior encoder of its size, with a native long context. No new task,
no domain; the contribution is the backbone and the training recipe (Abstract; §1 Contributions).

**Architecture (§2.1, §2.1.3, Appendix B).** Two models:

| | base | large |
|---|---|---|
| Params | **149M** | **395M** | ✔ §2.1.3 |
| Layers | 22 | 28 | ✔ §2.1.3 |
| Hidden size | 768 | 1,024 | ✔ §2.1.3 |
| GLU expansion (intermediate) | 2,304 | 5,248 | ✔ §2.1.3 |
| Native context | 8,192 | 8,192 | ✔ Abstract / §2.2.2 |
| Vocab | 50,368 (multiple of 64; 83 unused) | same | ✔ §2.2.1 |

Modern-transformer choices (§2.1.1): **RoPE** positional embeddings (not absolute); **GeGLU**
activation (GLU variant over BERT's GeLU); **pre-norm** + an extra LayerNorm after the embedding
layer, first attention-layer LayerNorm removed; **bias terms disabled** in all linear layers (except
the final decoder linear) and in all LayerNorms.
Efficiency (§2.1.2): **alternating attention** — every **third** layer is global (RoPE θ = 160,000),
the other two-thirds are **local sliding-window** attention with a **128-token window** (RoPE θ =
10,000); **full unpadding** (sequences concatenated into one batch-of-one; FlashAttention varlen +
RoPE on the jagged sequence; +10–20% over prior unpadding); **Flash Attention 3 for global layers,
Flash Attention 2 for local layers**; **torch.compile** (+10% throughput). Tokenizer: a modified
**OLMo BPE** tokenizer (code-aware), keeping BERT's `[CLS]`/`[SEP]` special tokens for backward
compatibility (§2.2.1).

**Training (§2.2).** **2 trillion tokens**, primarily English, web + **code** + scientific literature
(Abstract; §2.2.1). MLM only, **NSP removed**, **30% masking rate** (15% shown sub-optimal) (§2.2.2).
StableAdamW optimizer; **trapezoidal / Warmup-Stable-Decay** LR with a 1−√ decay. base: constant LR
8e-4 for 1.7T tokens (3B warmup); large: 5e-4 for 900B, rolled back and restarted at 5e-5 for the
remaining 800B after a loss plateau. **Context extension:** trained 1.7T tokens at 1,024 ctx (θ=10k),
then raised global-layer RoPE θ to 160k and trained +300B tokens at 8,192 ctx (250B at 3e-4 + a 50B
1−√ decay on upsampled high-quality data) (§2.2.2). large is **initialized from base** (Phi-style
tiling). Sequence packing >99% efficient.

**Results (§3.2, Table 1 — averages).** ModernBERT is the strongest *overall* encoder at both sizes:

| Metric (avg) | MB-base | best base rival | MB-large | best large rival |
|---|---|---|---|---|
| **GLUE** | **88.4** | DeBERTaV3-base 88.1 | **90.4** | DeBERTaV3-large 91.4 |
| BEIR (DPR) | 41.6 | GTE-en-MLM 41.4 | 44.0 | GTE-en-MLM 42.5 |
| BEIR (ColBERT) | 51.3 | GTE-en-MLM 48.2 | 52.4 | GTE-en-MLM 50.7 |
| CodeSearchNet | 56.4 | (only code-trained) | 59.5 | — |
| StackQA | 73.6 | — | 83.9 | — |

(Status: ✔ Table 1, lines read directly from the PDF; GLUE-base ≈ per the 88.4/88.5 delta above.)
Headline NLU claim: **ModernBERT-base is the first MLM-trained encoder to beat DeBERTaV3-base on
GLUE**; ModernBERT-large is 2nd-best on GLUE, "almost matching DeBERTaV3-large with one-tenth fewer
parameters while processing tokens in half the time" (§3.2). GLUE per-task detail in Table 5.

**Efficiency (§4, Table 2 — NVIDIA RTX 4090, k tokens/sec).** ModernBERT is the most speed- *and*
memory-efficient encoder. Long-context (8,192): processes documents **2.65× (base) / 3× (large)**
faster than the next-fastest encoder; **ModernBERT-large at 8,192 = 46,801 tok/s**, near GTE-en-MLM
*base*'s 47,507 and ~3× GTE-en-MLM-large's 16,532. On variable-length inputs it is 14.5–30.9% faster
than GTE at short ctx and 98.8–118.8% faster at long ctx (local attention + unpadding). Largest max
batch size of any encoder at both sizes. Caveat the paper itself states: on **fixed 512-token** inputs
it is **slower than the original BERT/RoBERTa** (their low param count), winning only among recent
encoders (§4.2). DeBERTaV3 is 5–7× more memory-hungry and ~2× slower (Appendix E.3).

### Parts directly useful for Pebble

1. **The full ModernBERT architecture spec (params/ctx/RoPE/alt-attn/GeGLU/unpadding) [D-A].** This is
   the exact configuration of the baseline Pebble must run head-to-head against NeoBERT. base 149M /
   large 395M brackets NeoBERT's 250M; native 8,192 ctx is **2× NeoBERT's 4,096**.
2. **30% MLM masking rate (vs the classic 15%) [D-F, D-A].** ModernBERT cites Wettig et al. 2023 that
   15% is sub-optimal and uses 30%. Directly relevant to Pebble's planned domain-adaptive MLM pass
   (D-F): the masking rate is a free hyperparameter Pebble was about to default to 15%.
3. **Priority-as-config: alternating local/global attention with a 128-token local window [D-A].** This
   is *why* ModernBERT is cheap at long context — but it also means most layers only see a 128-token
   neighborhood, which interacts with Pebble's short turn-level inputs (see lens).
4. **8,192-token native context as the long-input fallback [D-A].** If Pebble's multi-turn windowing
   ever exceeds NeoBERT's 4,096, ModernBERT is the drop-in long-context backbone with no architecture
   change to the 3-head stack.
5. **GLUE fine-tuning hyperparameter grid (Table 6, Appendix E.1) [D-A, D-E].** Per-task LR ∈ {1e-5,
   3e-5, 5e-5, 8e-5}, weight decay ∈ {1e-6, 5e-6, 8e-6, 1e-5}, epochs ∈ {1,2,3} or {2,5,10}, early
   stopping, and **RTE/MRPC/STS-B fine-tuned starting from the MNLI checkpoint** (intermediate-task
   transfer). The MNLI→small-task warm-start is a concrete pattern for D-E (staged fine-tuning).
6. **Backward-compatible tokenizer note [D-A].** ModernBERT keeps BERT's `[CLS]`/`[SEP]`; swapping
   backbones in Pebble's head code is low-friction — the `[CLS]`-pooling head transfers unchanged.

### How each part helps Pebble succeed

- **Make D-A evidence-backed, not assumed (parts 1, 4, 6).** Add a `models/backbones/modernbert.py`
  config and fine-tune the **identical 3-head stack** (emotion softmax/CE + severity regression +
  the heuristic placeholders) on ModernBERT-base **and** NeoBERT under one fixed recipe. Report
  emotion macro-F1 and severity Pearson side by side. The `[CLS]` pooling and BERT special tokens
  mean this is a backbone swap, not a rewrite (part 6). This is the experiment that closes D-A.
- **Set the MLM masking rate before the domain-adaptive pass (part 2) [D-F].** When Pebble runs MLM
  continued-pretraining on its emotion/mental-health corpus (the FAIIR-motivated step), use **30%
  masking**, not 15% — ModernBERT's recipe is the citation. Cheap config change, measurable on the
  downstream emotion head.
- **Use the MNLI→task warm-start for the small heads (part 5) [D-E].** Pebble's severity head trains
  on a tiny C-SSRS-style set; ModernBERT's "fine-tune RTE/MRPC/STS-B from the MNLI checkpoint"
  pattern is direct precedent for warm-starting the small severity/emotion heads from a larger
  related-task checkpoint rather than cold from the MLM backbone.
- **Long-input fallback is real, not hypothetical (part 4) [D-A].** Pebble scores turn-level, so 4,096
  is already generous (FAIIR's 2,000-token cap covered 94.4% of *whole* youth conversations — §01
  Limitations). But if product later needs full-session context, ModernBERT-base gives 8,192 ctx at
  **2.65× the long-context throughput** of the next encoder — the documented escape hatch.

### Child mental-health lens

- **Zero mental-health, affect, or multi-task evidence — state this loudly.** ModernBERT is evaluated
  *only* on GLUE (general NLU), BEIR/MLDR (retrieval), and code (CodeSearchNet/StackQA). There is
  **no emotion classification, no severity/intensity regression, no clinical/mental-health task, and
  no multi-task-learning experiment** anywhere in the paper. None of Pebble's three heads is exercised.
  GLUE includes SST-2 (binary sentiment) as the *closest* proxy to affect, and that is a long way from
  12-label GoEmotions or WASSA intensity. **Transfer risk for D-A: the paper proves ModernBERT is a
  better general encoder; it does NOT prove it is a better *Pebble* encoder.** Only Pebble's own
  head-to-head run can establish that.
- **Child register: untested (and English-only).** Training is web + code + scientific literature
  (§2.2.1); the Limitations (§6) state the work is "exclusively English" and "subject to the biases
  present in [web] data." No youth/child-register text, no crisis text. Same gap as NeoBERT — neither
  backbone has seen child mental-health language, so Pebble's domain-adaptive MLM pass (D-F) matters
  regardless of which backbone wins.
- **Local-attention interaction with short turn-level inputs.** Two-thirds of ModernBERT's layers
  attend only within a 128-token window. For Pebble's *short* mid-conversation turns (typically well
  under 128 tokens) this is harmless — the whole turn fits one window — but it means ModernBERT's
  headline long-context efficiency advantage is **irrelevant** to Pebble's actual workload, which is
  short inputs at high throughput. The honest D-A read: ModernBERT's wins (8K ctx, long-doc speed)
  are in the regime Pebble *doesn't* operate in.
- **No safety/harmfulness story to inherit.** §6 notes only that the MLM head can fill `[MASK]` and is
  "considerably less likely" to generate harmful content because it isn't generative. Nothing about
  crisis recall, false-negative cost, or calibration — Pebble's safety architecture (rule layer +
  recall floor, from FAIIR) is unaffected by the backbone choice.

### Limitations & open questions for Pebble

- **CONTRADICTION (the decisive one for D-A): NeoBERT claims to beat ModernBERT, on a benchmark
  ModernBERT never ran.** NeoBERT (arXiv:2502.19587) states it "outperform[s] … ModernBERT under
  identical fine-tuning conditions" on **MTEB** (✔ corroborated from NeoBERT's abstract). ModernBERT's
  paper predates NeoBERT and reports **no MTEB and no NeoBERT comparison at all** — its retrieval
  numbers are BEIR/MLDR, not MTEB. So the two papers do **not** share a common benchmark: ModernBERT
  wins GLUE+BEIR+code (vs DeBERTaV3/GTE/Nomic), NeoBERT claims MTEB (vs ModernBERT). **Neither result
  decides Pebble's question**, because (a) the comparison is on retrieval/embedding tasks, not emotion
  classification or severity regression, and (b) "identical fine-tuning conditions" is NeoBERT's own
  framing, unverified by a neutral third party. **The only evidence that settles D-A for Pebble is
  Pebble's own 3-head head-to-head** — exactly the experiment §"Best point" already proposes. This
  paper's role is to make that baseline rigorous, not to pre-decide it.
- **GLUE is near-saturated and not Pebble's task.** The paper itself concedes GLUE "is often regarded
  as saturated" (§3.1.1). ModernBERT-base 88.4 vs DeBERTaV3-base 88.1 is a 0.3-point margin on a
  saturated NLU suite — far too thin, and on the wrong task, to justify a backbone choice for a
  12-label emotion + intensity-regression stack. Don't cite the GLUE win as a reason to pick ModernBERT.
- **Provenance delta to track:** local PDF is the v2 preprint (Dec 2024); cite the **Findings of ACL
  2025** version in any Pebble write-up. GLUE-base is 88.4 (paper) / 88.5 (blog) — use 88.4.
- **Efficiency win is in the wrong regime.** ModernBERT's flagship numbers are *long-context* (8,192)
  throughput and memory. Pebble runs *short* turn-level inputs, where the paper admits ModernBERT is
  **slower than vanilla BERT/RoBERTa** on fixed 512-token inputs (§4.2). For Pebble's workload the
  efficiency comparison vs NeoBERT must be re-measured at short lengths on Pebble's own hardware —
  the paper's numbers don't transfer. (NeoBERT separately claims to be *faster* than ModernBERT,
  another reason to measure locally rather than trust either paper's framing.)
- **License/access (open question, not in the PDF):** both ModernBERT and NeoBERT ship open weights on
  HF (ModernBERT base 149M / large 395M). The paper doesn't state the weight license; before adopting
  either as Pebble's production backbone, confirm the HF license permits a child-facing commercial
  product. This is a go/no-go item the paper cannot answer.
- **Gap vs Pebble's plan:** Pebble's plan assumes NeoBERT. This paper gives no reason to overturn that
  *and* no reason to keep it — it simply establishes that the strongest alternative is real, open, and
  on the wrong side of the context/efficiency tradeoff for short turn-level scoring. The unresolved
  question Pebble must answer itself: **does ModernBERT's larger/cleaner pretraining (2T tokens, code,
  newer cutoff) translate into a better emotion/severity head than NeoBERT's 2.1T-token recipe?** No
  published number answers it.
