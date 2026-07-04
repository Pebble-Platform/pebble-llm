# Paper 56 — MentaLLaMA: Interpretable Mental Health Analysis on Social Media with LLMs

> Enrichment set · Pillar 4 (LLM-teacher silver-label distillation). Analysis depth: arXiv abstract + official GitHub README. Compiled 2026-06-26.

## Bibliographic info
- **Title:** *MentaLLaMA: Interpretable Mental Health Analysis on Social Media with Large Language Models*
- **Authors:** Kailai Yang, Tianlin Zhang, Ziyan Kuang, Qianqian Xie, Jimin Huang, Sophia Ananiadou.
- **Year / Venue:** **WWW 2024** (The Web Conference).
- **Links:** [arXiv:2309.13567](https://arxiv.org/abs/2309.13567) · [ACM DL 10.1145/3589334.3648137](https://dl.acm.org/doi/10.1145/3589334.3648137) (ACM paywalled — scored from arXiv + GitHub) · code/data: [github.com/SteveKGYang/MentaLLaMA](https://github.com/SteveKGYang/MentaLLaMA)
- **Pebble pillar:** teacher-LLM (ChatGPT) → open student silver-label distillation on mental-health text. The most direct *published* analogue of Pebble's Gemini→student pipeline.

## Summary
The authors build **IMHI**, the first multi-task instruction-tuning dataset for interpretable mental-health analysis: **105K samples across 8 tasks drawn from 10 existing Reddit/Twitter sources** (DR, CLP, dreaddit, SWMH, T-SID, SAD, CAMS, loneliness, MultiWD, IRF — covering depression, stress, mental-disorder, stress-cause, depression/suicide-cause, loneliness, wellness-dimensions, and interpersonal-risk-factor detection). The labels already exist; what the teacher adds is the **explanation**. **ChatGPT is prompted with expert-written few-shot templates plus the gold label** to emit a free-text rationale for each sample, and these silver explanations are then **quality-gated** by automatic + human evaluation on four axes (fluency, completeness, reliability, overall) before entering training. **LLaMA2 (7B / 13B; 33B via LoRA)** is instruction-tuned on the gated set → MentaLLaMA, which matches or beats strong discriminative baselines on classification while also producing human-quality explanations. Both models and the full IMHI train/test split are released under **MIT license**.

## Overlap with Pebble — 42% (adjacent)
`D1=1, D2=2, D3=0, D4=2, D5=0, D6=0, D7=0` → (3·1 + 2·2 + 1·0 + 2·2 + 2·0 + 2·0 + 1·0)/26 = 11/26 = **42%**
- **Closest on:** D4 (teacher-LLM silver-label distillation — ChatGPT teacher → open student, with an explicit quality gate that Pebble currently lacks) and D2 (squarely the mental-health social-media domain, incl. suicide/depression/stress). D1 is partial: it is genuinely multi-task (8 tasks) but every task is categorical/generative — no continuous regression head and no shared multi-head encoder, the core of Pebble's architecture.

## Best point — Method to adopt
**Gate the teacher's silver labels before training, on explicit quality axes, instead of auto-accepting them.** MentaLLaMA runs automatic + human evaluation of every ChatGPT explanation on fluency / completeness / reliability / overall, validates that an automatic metric (BART-score) tracks the human judgement, and only the gated data is used for fine-tuning.
- **How to apply to Pebble:** Add a quality gate to the Gemini→NeoBERT pipeline. For each silver sample, have Gemini (or a second-pass judge) emit a short self-rationale + confidence, score a held-out human-annotated slice to calibrate an automatic acceptance metric, and **drop or down-weight low-reliability silver labels before they hit the heads** — especially for the safety/crisis head, where a single hallucinated "safe" label silently erodes the recall ≥ 0.95 floor. This is the highest-leverage import because Pebble's distillation already exists but is ungated; MentaLLaMA shows a published, MIT-licensed recipe for the gate.

## Dataset
- **IMHI** — 105K instruction samples, 8 tasks, 10 Reddit/Twitter sources; **MIT license, openly downloadable** (train + the released `/test_data` split). A sibling `find-dataset` agent is checking access; from the README the test set is ungated.
- **Candidate use for Pebble: held-out external evaluation, not training.** IMHI's depression/stress/suicide-cause/loneliness slices are a clean out-of-distribution probe for Pebble's safety and severity heads (label-only eval; ignore the explanation field). Caveat: it is **adult social-media** text — Pebble serves minors, so treat IMHI as a generalization stress-test, not an in-domain benchmark, and do not transfer its explanation style.

## Caveats
- ACM DL is paywalled; all scores are from the arXiv abstract + the official GitHub README (which carries the task list, source datasets, model sizes, license, and the 4-axis quality-eval description). Full method tables / exact gate thresholds were not read — confidence on the gating *mechanism* is medium, on its *existence* high.
- **Key divergence — distillation target.** MentaLLaMA distills into a **generative decoder LLM (7B–33B)** whose product is text predictions + explanations; Pebble distills into a **small discriminative encoder (~250M)** with fixed numeric/categorical heads. What transfers: the *teacher-labeling + quality-gating discipline* (D4) and the *domain/eval data* (D2). What does **not** transfer: the architecture (D7=0), the continuous + heterogeneous-head design (D1 only partial), MTL loss balancing (D5=0, the paper just mixes instruction data), and any recall-floored safety objective (D6=0). The interpretability/explanation contribution is orthogonal to Pebble's encoder, which emits scores, not rationales.
