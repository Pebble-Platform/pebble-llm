# Paper 52 — STATENet: Time-aware Suicidal Ideation Detection

> Family D · mental-health / suicide-risk SOTA. Analysis depth: abstract (ACL Anthology, VERIFIED) + official GitHub README architecture notes. Compiled 2026-06-25.

## Bibliographic info
- **Authors / Year / Venue:** Ramit Sawhney, Harshit Joshi, Saumya Gandhi, Rajiv Ratn Shah. **2020. EMNLP 2020** (Proceedings of the 2020 Conf. on Empirical Methods in NLP, pp. 7685–7697). *Exact title:* "A Time-Aware Transformer Based Model for Suicide Ideation Detection on Social Media" — STATENet is the model name.
- **Link:** [aclanthology.org/2020.emnlp-main.619](https://aclanthology.org/2020.emnlp-main.619/) · open (DOI 10.18653/v1/2020.emnlp-main.619) · code: [github.com/midas-research/STATENet_Time_Aware_Suicide_Assessment](https://github.com/midas-research/STATENet_Time_Aware_Suicide_Assessment) — VERIFIED via WebSearch + WebFetch (ACL Anthology page + GitHub README).
- **R2 pillar:** temporal modeling of a user's post history for suicide-risk screening — the strongest related-work baseline for R2's *unused* temporal head (W3).

## Summary
STATENet is a dual-encoder, time-aware model for binary suicidal-ideation screening on tweets. The **current tweet** is encoded with SentenceBERT (768-d). The **historical tweets** are each encoded with a BERT fine-tuned on **EmoNet** (so each historical embedding carries emotional context, the paper's core thesis: "the emotional spectrum of a user's historical activity … can be indicative of their mental state over time"). The historical sequence is then consumed by a **time-aware module** — a Time-Aware LSTM (T-LSTM) / time-aware Transformer that conditions on the **inter-post time intervals** (`hist_dates`, the datetime of each prior post) so that the decay/weighting of past posts depends on *when* they were written, not just their order. Current + historical representations are fused for the final 0/1 (non-suicidal / suicidal) decision. It outperforms order-only and content-only baselines, demonstrating that **emotional + temporal context** improves suicide-risk screening.

## Overlap with Pebble/R2 — 31% (peripheral)
`D1=0, D2=2, D3=1, D4=0, D5=0, D6=1, D7=1` → (3·0 + 2·2 + 1·1 + 2·0 + 2·0 + 2·1 + 1·1)/26 = 8/26 = **31%**
- **Closest on:** D2 (suicidal-ideation/crisis text — direct) and D6 (suicide screening, but no recall-floor objective → partial).
- D3=1: emotional context is injected (BERT-on-EmoNet for historical posts) but via EmoNet, not Pebble's GoEmotions/intensity corpora. D7=1: BERT/SentenceBERT family but small and not the contribution. D1/D4/D5=0: single-task binary, no continuous/multi-head stack, no LLM distillation, no MTL loss balancing.

## Best point — Design lesson (+ related-work baseline)
**Temporal context only pays off when inter-post *time intervals* are real signal, not order.** STATENet's whole contribution is that a time-aware module conditioned on actual `hist_dates` (irregular Δt between posts) beats an order-only sequence model — i.e. the lift comes from *when* posts happened, which is precisely the input R2 currently feeds as a constant zero. This is the single highest-leverage datum for R2 because it directly adjudicates W3: R2 built a temporal head (`time_fc`/`time_ln`) and a `dt` tensor, then trained it with Δt≡0, so that head can contribute nothing — STATENet is the published evidence that the head is only worth keeping *if real timestamps are wired in*.

## ▶ Apply to R2 (MANDATORY)
R2's temporal path exists but is starved of signal. Two mutually exclusive actions; pick based on whether timestamps are recoverable for the Reddit pool.

**Path A — wire real Δt (preferred if timestamps exist).**
File `kaggle/finetuning-message/r2-suicide-risk-dualhead/r2-suicide-risk-dualhead.py`:
1. In `CSSRSDataset.__getitem__` (line ~270): replace `dt = torch.zeros(self.cfg.seq_len, ...)` with the real per-post inter-arrival intervals (e.g. log-seconds between consecutive posts, normalized). This feeds `time_fc`/`time_ln` (lines 296–298, used at line 339 `e_time = ... self.time_fc(dt.unsqueeze(-1))`) so the temporal embedding becomes non-trivial.
2. In `stat_features` (lines 246–250): replace the `pad = [0.0, 0.0, 0.0, 0.0]` time-interval stats with real mean/std/min/max of the intervals, so the `feat_mlp`/`fuse` path (lines 312–314) also sees temporal signal.
3. No architecture change needed — `seq_encoder` already consumes `e = e + e_time`. STATENet's lesson is just: make `e_time` carry information.

**Path B — honestly justify Δt=0 (if timestamps cannot be recovered).** Add a Limitations paragraph: R2's CSSRS-500 / combined pool has no usable per-post timestamps and most users are effectively single-post, so the temporal head (`time_fc`/`time_ln`, the `dt` tensor, the four zeroed time-interval `stat_features`) is **architecturally present but inert by construction**. Cite STATENet as the method that *would* exploit timestamps, and frame R2's choice as content+ordinal modeling on a timestamp-free corpus — turning a weakness into a scoped, defensible design boundary for the IEEE submission.

## ▶ Kaggle experiment (MANDATORY)
**±real-Δt ablation** (only if timestamps are recovered — Path A):
- **Arms:** (1) current Run B, Δt≡0 (baseline); (2) identical, but `dt` + time-interval `stat_features` populated with real intervals.
- **Expected signal:** if STATENet's thesis transfers, arm (2) lifts gold macro-F1 / QWK, concentrated where multi-post users exist; if both arms tie, that *itself* is the result — it empirically licenses Path B (drop or freeze the temporal head and say so). Either way the ablation closes W3.
- **Secondary diagnostic:** ±temporal-head (zero out `e_time` entirely) on the current Δt≡0 model to confirm the head currently contributes ~0 — a cheap sanity check that needs no new data.
- **Cost:** ablation is 2× the existing 5-fold gold-holdout run (~no new tuning), small on Kaggle GPU. **If timestamps are unavailable, do NOT run an experiment — file this as a Limitations + related-work item (Path B), not a Kaggle job.**

## Caveats
- **Different label scheme:** STATENet is **binary** suicidal-ideation (0/1); R2 is **4-level ordinal** C-SSRS (Indicator/Ideation/Behavior/Attempt). The temporal *mechanism* transfers; the head/loss do not.
- **Data-availability gap is the crux:** STATENet *requires* timestamped post histories (Twitter `hist_dates`). R2's corpus lacks usable timestamps and is dominated by single-post users (W3 root cause), so Path A may be infeasible — verify timestamp recoverability before committing. If most users remain single-post, even real Δt has little to act on.
- **Verification status:** venue/authors/year/link VERIFIED (ACL Anthology). Architecture (T-LSTM / time-aware Transformer, SentenceBERT current encoder, BERT-on-EmoNet historical encoder, binary task) sourced from the **abstract + official GitHub README**, not a full-PDF read — temporal-module specifics (T-LSTM vs time-aware Transformer exact gating, Hawkes formulation) are README-level, marked as such; per-class metrics not extracted.
- **Population mismatch (carried):** adult Twitter self-disclosure, not child-register chat — the temporal-emotional decay learned here is on adult posting cadence.
