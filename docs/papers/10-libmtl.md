# Paper 10 — LibMTL: A Python Library for Deep Multi-Task Learning

> Enrichment set · Pillar 1 (MTL tooling). Analysis depth: abstract + README. Compiled 2026-06-09.

## Bibliographic info
- **Authors / Year / Venue:** Lin & Zhang. JMLR 2023.
- **Link:** [JMLR 24(2023)](https://www.jmlr.org/papers/volume24/22-0347/22-0347.pdf) · open · [GitHub](https://github.com/median-research-group/LibMTL)
- **Pebble pillar:** tooling for the MTL loss-balancing experiment (D5).

## Summary
A PyTorch library implementing 27 weighting strategies — Uncertainty Weighting (Kendall), GradNorm, DWA, PCGrad, MGDA, CAGrad, IMTL, Nash-MTL — under one unified `Weighting` API across 8 MTL architectures. Backbone-agnostic; ships a BERT example.

## Overlap with Pebble — 31% (peripheral, high-leverage)
`D1=1, D2=0, D3=0, D4=0, D5=2, D6=0, D7=1` → (3·1 + 2·2 + 1·1)/26 = 8/26 = **31%**
- **Closest on:** D5 (the exact balancing family Pebble plans) and partial D7 (backbone-agnostic; can wrap NeoBERT).
- Note: it's a *tool*, not a method paper — value is implementation reuse on the one dimension it nails.

## Best point — Method (tool) to adopt
Run the entire "static λ vs principled balancing" comparison by swapping a config flag instead of reimplementing each balancer.
- **How to apply to Pebble:** Wrap NeoBERT as the shared backbone, register the three heads (regression / softmax / BCE-safety) as tasks, sweep `weighting=EW|UW|GradNorm|PCGrad|NashMTL` → an apples-to-apples ablation at near-zero impl cost. This is Pebble's #1 publishable angle.

## Dataset
Tooling — no dataset. (Examples are CV-centric.)

## Caveats
Scored from abstract/README. Verify before adopting: (1) that per-task loss is fully user-supplied so MSE+CE+BCE can be mixed in one model (appears so, unconfirmed); (2) gradient-surgery methods add memory/compute that may matter under Kaggle limits. Contributes engineering leverage on D5 only.

## Deep research — full-PDF read (2026-06-10)

> **Sourcing note.** The local PDF (`docs/papers/pdfs/10-libmtl.pdf`) could not be rendered in-session (the Read tool's PDF rasterizer `pdftoppm` is unavailable on this Windows host) and the JMLR PDF is FlateDecode-compressed binary. To stay grounded I instead read the **authoritative, version-matched** sources: the [GitHub repo](https://github.com/median-research-group/LibMTL), the [ReadTheDocs API/user-guide](https://libmtl.readthedocs.io/en/latest/), and the actual example sources (`examples/nyu/main.py`, `examples/qm9/main.py`, `LibMTL/trainer.py`). API/argument names and code snippets below are quoted from those. Result *numbers* in the paper's benchmark tables could **not** be extracted from the binary PDF and are flagged `[PDF-number-unverified]` — the (3) and (5) sections below avoid asserting table values I could not see.

### What the paper actually does (method, data, results — from the PDF, with exact numbers)
LibMTL is a **systems/tooling** contribution, not a new MTL algorithm. It decomposes the MTL training pipeline into nine decoupled modules so that **loss-weighting strategy** and **network architecture** become orthogonal, swappable axes selected by the `--weighting` and `--arch` flags. Its claims are *unification* (one API for 27 weighting + 8 architecture methods), *fair comparison* (shared encoder, data pipeline, metrics, seeds), and *extensibility* (subclass one base class to add a method).

- **Weighting methods (27), via `--weighting`** — Equal Weighting (EW); GradNorm (ICML 2018); Uncertainty Weighting / UW (CVPR 2018, = Kendall); MGDA (NeurIPS 2018); DWA (CVPR 2019); GLS (CVPRW 2019); PCGrad (NeurIPS 2020); GradDrop (NeurIPS 2020); IMTL (ICLR 2021); GradVac (ICLR 2021); CAGrad (NeurIPS 2021); MOML (NeurIPS 2021); Nash-MTL (ICML 2022); RLW (TMLR 2022); Auto-Lambda (TMLR 2022); MoCo (ICLR 2023); Aligned-MTL (CVPR 2023); FAMO, SDMGrad, MoDo (NeurIPS 2023); FORUM (ECAI 2024); STCH, ExcessMTL, FairGrad (ICML 2024); DB-MTL, UPGrad (arXiv). (The "27" count and the most recent entries reflect the current library; the JMLR 2023 paper enumerated a subset — `[PDF-list-version-skew possible]`.)
- **Architectures (8), via `--arch`** — Hard Parameter Sharing (HPS); Cross-stitch (CVPR 2016); MMoE (KDD 2018); MTAN (CVPR 2019); CGC and PLE (RecSys 2020); LTB (ICML 2020); DSelect-k (NeurIPS 2021).
- **Benchmark datasets shipped:** NYUv2 (3 dense-prediction tasks: 13-class semantic segmentation, depth, surface normals), Office-31 and Office-Home (multi-domain image classification), and QM9 (11-target molecular-property **regression**). These are *vision/scientific* benchmarks — there is **no mental-health or text-classification benchmark**; the only NLP touchpoint is a BERT example outside the core benchmark tables.
- **Reported results:** the paper presents per-task metric tables (e.g., NYUv2 mIoU/pixAcc for segmentation, abs/rel error for depth, angular error for normals) comparing the weighting methods under a fixed backbone — **exact table values are `[PDF-number-unverified]`** because the compressed PDF body could not be decoded this session. The *qualitative* finding LibMTL is cited for (and which the 2025 "Revisit imbalance" paper, entry in `related-work-enrichment.md` Pillar 1, sharpens) is that **no single weighting method dominates across tasks/datasets**, and well-tuned EW is a strong baseline — the exact null hypothesis Pebble's experiment must rule out.

### Parts directly useful for Pebble (specific: API classes, config flags, supported weighting methods, how to plug a custom HuggingFace encoder + custom heads)
The whole value is the **`Trainer` contract**, which cleanly separates *backbone*, *heads*, *losses*, and *weighting* — exactly Pebble's four moving parts. Verified constructor (`LibMTL/trainer.py`):

```python
Trainer(task_dict, weighting, architecture, encoder_class, decoders,
        rep_grad, multi_input, optim_param, scheduler_param,
        save_path=None, load_path=None, **kwargs)
# train(train_dataloaders, test_dataloaders, epochs,
#       val_dataloaders=None, return_weight=False, **kwargs)
```

1. **`task_dict` — per-task loss is fully user-supplied (the caveat from the short analysis is now CONFIRMED).** Each task maps to `{'metrics':[...], 'metrics_fn': <obj>, 'loss_fn': <callable>, 'weight':[...]}`. The NYUv2 example mixes three *different* loss objects in one model — `'segmentation': {'loss_fn': SegLoss()...}`, `'depth': {'loss_fn': DepthLoss()...}`, `'normal': {'loss_fn': NormalLoss()...}` — and the QM9 example uses `'loss_fn': MSELoss()` across 11 **regression** heads. So a heterogeneous **MSE (severity/energy) + CE (emotion) + BCE (safety)** model is directly expressible; no library change needed.
2. **`encoder_class` is any zero-arg callable returning an `nn.Module`** (NYUv2: `def encoder_class(): return resnet_dilated('resnet50')`). For Pebble this becomes `def encoder_class(): return NeoBertCLSPooler(...)` wrapping the HuggingFace `AutoModel` and returning the `[CLS]` representation — **fully backbone-agnostic, confirming D7**.
3. **`decoders` is an `nn.ModuleDict` keyed by task name** (NYUv2: `nn.ModuleDict({task: DeepLabHead(2048, n_out[task]) for task in task_dict})`). Pebble's three heads become `nn.ModuleDict({'severity': nn.Linear(d,1), 'emotion': nn.Linear(d,28), 'safety': nn.Linear(d,1)})`.
4. **`multi_input` is the flag that fits Pebble's reality.** Docs: `multi_input=False` means "all tasks share the input data"; `multi_input=True` means "each task has its own input data." Pebble's tasks come from **different corpora** (CSSRS for safety/severity, GoEmotions for emotion, WASSA for distress) — so Pebble needs `multi_input=True` with one dataloader per task, *not* the single-input dense-prediction setup the NYUv2 demo uses.
5. **`rep_grad` is the cost/accuracy knob for gradient methods.** Setting `rep_grad=True` computes the balancing on the **post-encoder representation gradient** (separating the graph via `detach`) as a cheaper approximation to true shared-parameter gradients — directly relevant to running PCGrad/MGDA/Nash-MTL under Kaggle memory limits (the second open caveat from the short analysis).
6. **Weighting hyperparameters are passed as `**kwargs`/`weight_args`** with sane defaults: GradNorm `alpha=1.5`; DWA `T=2.0`; MGDA `mgda_gn='none'`; CAGrad `calpha=0.5, rescale=1`; Nash-MTL `update_weights_every=1, optim_niter=20, max_norm=1.0`; PCGrad/GradDrop/EW take none. UW (Kendall) adds learnable log-variances internally.
7. **`process_preds(preds, task_name=None)` override** lets a `Trainer` subclass post-process head outputs before loss/metrics (NYUv2 interpolates; Pebble can squash the severity head through a sigmoid×scale, or apply the ordinal transform the C-SSRS papers call for).
8. **Extensibility is one subclass.** A custom balancer subclasses the abstract `Weighting` base and implements `backward(losses, **kwargs)`; a custom architecture subclasses `Architecture`. This is the hook for Pebble's **safety-floor** modification (below).

### How each part helps Pebble succeed (concrete actions: which experiment in Pebble it enables, expected payoff)
- **Enables the headline ablation cheaply.** Build the `task_dict`/`encoder_class`/`decoders` once, then run the planned matrix by flag: `--weighting EW` (static-λ baseline) → `UW` → `GradNorm --alpha 1.5` → `PCGrad` → `NashMTL`. Payoff: an apples-to-apples table holding backbone, data, seed, and metrics fixed — the credibility bar reviewers expect, produced at near-zero implementation cost. This is Pebble's #1 publishable angle and the central claim of `related-work-enrichment.md` Pillar 1.
- **Lets the safety constraint become a *method*, not a footnote.** Because adding a balancer is "subclass `Weighting`, implement `backward()`", Pebble can ship a **`SafetyFloorWeighting`** wrapper that runs any base balancer but **clamps the safety task's effective weight to a floor** so no method (especially UW, which can learn to down-weight a low-variance head) can starve the crisis gradient below what holds recall ≥ 0.95. That converts the hard floor into a *novel contribution* layered on the library rather than a hack.
- **`return_weight=True` gives the audit trail.** `train(..., return_weight=True)` returns the per-epoch task weights each method assigned. Pebble can log and plot the **safety head's weight trajectory** per method — direct evidence for the paper that (e.g.) Nash-MTL kept the crisis head adequately weighted while EW did not, tying the MTL choice to the recall outcome.
- **`multi_input=True` + per-task dataloaders** is the integration path for Pebble's masked-multitask assembler (`f3c4301` added the masked assembler) — each batch carries only the tasks with labels, which is exactly how heterogeneous corpora (CSSRS / GoEmotions / WASSA) must be fed.
- **`rep_grad=True`** is the lever to keep PCGrad/MGDA/Nash-MTL within Kaggle GPU memory so the *full* method sweep (not just the cheap ones) is actually runnable — protecting the completeness of the ablation.

### Child mental-health lens (Pebble serves children: risks, mitigations, ethics caveats of automating the MTL ablation for a safety-critical child-facing model)
- **Automated weight-balancing can silently sacrifice the most important head.** UW/GradNorm/Nash-MTL optimize an *aggregate* objective (loss balance, gradient norm balance, Nash bargaining) that is **blind to the asymmetric cost of a missed crisis in a child**. A method that improves average multi-task metrics by trimming the safety gradient is "better" by the library's lens and catastrophic by Pebble's. **Mitigation:** never let the chosen weighting select itself on aggregate validation loss — gate every method on **safety recall ≥ 0.95 as a hard pass/fail first**, and only then compare the survivors on the other heads. The `SafetyFloorWeighting` subclass plus `return_weight=True` logging are the technical enforcement and audit of this.
- **A point-estimate flag sweep hides variance that matters for a safety floor.** Gradient-surgery methods (PCGrad, MGDA) are seed- and order-sensitive; a recall of 0.95 on one seed can be 0.92 on another. For a child-facing crisis head, **report recall as a mean ± CI over multiple seeds, with the worst-case seed shown**, not a single best run — the library makes single-run sweeps so easy that this discipline must be imposed externally.
- **Threshold, not just weighting, controls recall.** LibMTL balances *training* gradients; the deployed recall depends on the **decision threshold** on the safety logit. The MTL ablation must be evaluated at a **recall-pinned operating point** (choose the threshold that yields ≥0.95 recall on a held-out set, then report precision/FPR there) so methods are compared at the constraint Pebble actually ships, not at 0.5.
- **License/provenance for a child product.** LibMTL is a benign tool, but the heads it trains learn from CSSRS / WASSA / ESConv and **Gemini silver labels**; the dataset notes in this repo already flag ESConv as NC (research-only) and teacher-bias risk. The MTL ablation must run on the *deployable* data subset for any number that informs the shipped model — a clean weighting sweep on research-only data does not license deployment.
- **Distribution shift to children's language.** All benchmark heuristics here come from adult corpora; child/teen expressions of distress differ. The MTL method that wins on adult-sourced validation may not preserve recall on children's text — the safety-floor evaluation should, where possible, include a child-language validation slice before the weighting choice is locked.

### Limitations & open questions for Pebble
- **No text/mental-health benchmark in the paper** — every reported result is vision/molecular (NYUv2, Office, QM9). LibMTL gives Pebble *no* prior number to beat on its domain; it is plumbing, not a baseline (consistent with the 31% peripheral score).
- **Exact paper table values unverified this session** — the binary PDF could not be decoded; the method/architecture/API facts above are from the version-matched repo+docs, but specific NYUv2/QM9 metric numbers are `[PDF-number-unverified]`. Pebble does not depend on those numbers, so this does not block adoption.
- **`multi_input=True` + heterogeneous losses is the untested combination.** The shipped examples are either single-input multi-loss (NYUv2) or multi-task same-loss (QM9, all MSE). Pebble needs **multi-input + mixed MSE/CE/BCE** simultaneously; that path should be smoke-tested on a tiny run before trusting the full sweep (the masked-multitask assembler from `f3c4301` is the place to verify label-masking interacts correctly with each balancer's per-task gradient computation).
- **Gradient-method cost under Kaggle.** MGDA/PCGrad/Nash-MTL compute per-task gradients; even with `rep_grad=True` the per-step solver in Nash-MTL (`optim_niter=20`) adds wall-clock. Budget a runtime check before committing to the full method matrix.
- **Weight floor vs. method purity.** Clamping the safety weight changes what each balancer is actually optimizing, so a floored UW is no longer "vanilla UW." For a fair *scientific* comparison Pebble should report both the unconstrained method (to characterize its native behavior) and the floored variant (the deployable one), and be explicit that the floor is a Pebble modification, not the published method.
