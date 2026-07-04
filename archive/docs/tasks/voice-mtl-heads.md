# Voice MTL heads — emotion + affect (CCC) + crisis (hard recall floor)

- **Slug:** voice-mtl-heads
- **Status:** in-progress (kernel built; Kaggle run pending)
- **Created:** 2026-06-23  ·  **Updated:** 2026-06-23
- **Owner:** Fabio (agent: Claude)

## Goal
Extend the single-head emotion probe from [`emotion2vec-reproduction`](./emotion2vec-reproduction.md)
into the **heterogeneous multi-task head topology** the thesis requires: on the same frozen backbone
(WavLM-Large / emotion2vec) + shared SUPERB trunk, attach **three heads** —
- **emotion** `Linear(256,8)` cross-entropy (WA/UA/WF1),
- **affect** `Linear(256,2)` regressing **valence + arousal** with **CCC loss**,
- **crisis** `Linear(256,1)` BCE under a **hard recall floor** —
balanced by **Kendall uncertainty weighting**. "Done" = a Kaggle GPU run reporting all three heads'
metrics per backbone (10-fold CV), an artifact that loads locally, and an honest note on what the proxy
labels do and don't prove.

## The proxy-label caveat (read first)
RAVDESS has **no** continuous V/A labels and **no** crisis labels, so the two new heads learn **proxy
targets** [user-approved 2026-06-23]:
- **affect** → fixed **Russell (1980) circumplex** (valence, arousal) per emotion (`VALENCE_AROUSAL` in c1),
- **crisis** → high-distress emotion set `{angry, fearful, sad, disgust}` (`CRISIS` in c1).

→ This run validates the **mechanics** (3-head MTL + Kendall balancing + recall-floor thresholding) on
real frozen features. It does **not** produce scientifically meaningful CCC / crisis-recall numbers —
those need real continuous + clinical labels (**MSP-Podcast** A/V/D, **DAIC** crisis). Keep this framing
in any thesis writeup; the deliverable here is the *architecture + training loop*, proven to run.

## Requirements & Constraints
- **Functional:** shared trunk `Linear(d,256)→ReLU→masked-mean-pool`; 3 heads; Kendall weighting; CCC
  loss for affect; crisis threshold tuned **on val** to guarantee `recall ≥ RECALL_FLOOR (0.90)`, then
  precision@floor reported on test. Same random 10-fold 80/10/10 protocol as the repro.
- **Constraints:** new kernel `kaggle/voice/pebble-voice-mtl-heads/` (do **not** edit the done repro
  kernel — surgical); reuse c2/c3 (data + frozen frame features) verbatim; local test in `.venv-voice`.
- **Non-goals:** real continuous/crisis datasets, text fusion, backbone fine-tune — separate tasks.

## Milestones
- [x] M1 — Head topology + proxy targets locked (circumplex V/A; crisis set; recall floor 0.90)
- [x] M2 — Kernel built — `kaggle/voice/pebble-voice-mtl-heads/` (c1–c5 + build + metadata + README);
  all cells `py_compile` clean; .ipynb (13 cells) valid; MTL math smoke-tested on CPU (recall-floor mechanic
  hits recall=0.90 exactly). Local infer `scripts/voice_mtl_infer.py`.
- [ ] M3 — Kaggle run green — pushed, GPU run, `out/` pulled with results + artifact bundle
- [ ] M4 — Local sample test — pulled artifact loads and predicts emotion + V/A + crisis end-to-end
- [ ] M5 — Writeup — per-backbone WA/UA/WF1 + CCC(v,a) + crisis recall/precision@floor, with the
  proxy-label caveat and thesis takeaways (feed back to `docs/related-work-voice-multimodal.md`)

## Decision Log
<!-- newest first -->
- **2026-06-23 — Proxy targets = Russell circumplex V/A + high-distress crisis set** [user-approved]:
  RAVDESS lacks continuous/crisis labels; circumplex V/A (continuous, citable) + `{angry,fearful,sad,
  disgust}` crisis proxy let the heads train on the reproduction's frozen features now. Rejected:
  intensity-as-severity (binary, `neutral` has no `strong`); plumbing-only smoke (no chapter numbers).
- **2026-06-23 — MTL balancing = Kendall homoscedastic uncertainty weighting**: learnable per-task
  log-variance over the 3 losses (CVPR 2018); cheap, citable, and the thesis comparator vs GradNorm/PCGrad.
- **2026-06-23 — Crisis head scored under a hard recall floor**: threshold tuned on val to the highest
  value still giving `recall ≥ 0.90`, precision@floor reported on test — operationalizes the thesis's
  "hard crisis-recall constraint" novelty on the proxy crisis label.
- **2026-06-23 — New kernel, reuse repro c2/c3 verbatim**: the repro task is done; new heads = new kernel
  (`pebble-voice-mtl-heads`) so the reproduction stays intact (surgical).

## Completed Work
- 2026-06-23 — M1+M2: built `kaggle/voice/pebble-voice-mtl-heads/` (3-head MTL probe, Kendall weighting,
  CCC loss, recall-floor thresholding), reusing repro data + frozen-feature cells. Cells compile; notebook
  valid; MTL math smoke-tested on CPU. Local infer script `scripts/voice_mtl_infer.py`.

## Remaining Action Items
- [ ] Push kernel to Kaggle GPU, pull `out/` (M3).
- [ ] Local sample test on pulled artifact (M4).
- [ ] Writeup with proxy caveat + thesis takeaways (M5).
- [ ] (next task) swap proxy labels for MSP-Podcast (A/V/D) + DAIC (crisis) for real numbers.
