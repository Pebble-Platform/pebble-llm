# Voice Method Selection — Frozen Speech-Encoder Backbone Pilot *(decision + plan)*

> **Purpose.** Companion to [`related-work-voice-multimodal.md`](./related-work-voice-multimodal.md)
> (the voice survey, backbone table, and the "two backbones" decision) and to the text-only system in
> [`report-slides.md`](./report-slides.md). This document fixes the **first** voice-modality experiment,
> justifies it against the survey, names what it rejects, and describes the actual Kaggle notebook that
> runs it (`kaggle/pebble-voice-backbone/`).
>
> **Compiled:** 2026-06-17 · pilot decision + implementation plan (no results yet — Kaggle run pending).

---

## Summary

The pilot experiment is **frozen speech-encoder backbone selection for crisis-sensitive speech affect**:
**emotion2vec (primary) vs WavLM-Large (baseline)**, evaluated with Pebble's signature **heterogeneous
heads** — an 8-way emotion softmax plus a high-distress recall head — on **RAVDESS**, over **3 seeds**,
reported as a **paired emotion2vec − WavLM delta**. Each encoder is frozen and runs **once** to cache
utterance embeddings; only tiny MLP heads are trained on top (seconds on a P100). This is the smallest
honest experiment that resolves the voice survey's own central open question — *which speech encoder* —
while moving Pebble's recall-floored safety head into the speech modality. The text-only NeoBERT system
stays the unimodal baseline; this pilot becomes the thesis's "backbone selection" chapter and the
foundation for the later voice-led fusion.

---

## Why this method (justification)

- **It resolves the thesis's own open decision.** The voice survey ends on an explicit, undecided
  empirical choice between two backbones and states that *"this backbone comparison is itself a clean
  thesis chapter — backbone selection for crisis-sensitive speech affect — not an assumption to defend."*
  The survey's decision block names exactly this pairing: **emotion2vec as the primary** (strongest
  emotion features per parameter on the linear-probe table) and **WavLM-Large as the baseline / fallback**
  (MIT-licensed, the "did the emotion-specialized model actually beat the strong general one?" control).
  This pilot runs that comparison head-on.

- **It preserves Pebble's signature novelty, in the new modality.** Pebble's text system is defined by
  *heterogeneous heads under a hard crisis-recall floor* (emotion softmax + continuous regression +
  safety BCE at recall ≥ 0.95). The survey's gap analysis is precise that this is unclaimed for speech:
  *"no published system does heterogeneous … speech-driven affect MTL under a hard crisis-recall floor."*
  By attaching an emotion softmax + a recall-floored distress head to a frozen speech encoder, the pilot
  plants Pebble's contribution in the speech modality from the very first experiment.

- **It is small, low-risk, and cheap.** The encoders are **frozen**: each runs once to extract
  embeddings, then the only trainable parameters are two small MLP heads — training is seconds on a P100.
  It reuses the repo's proven **3-seed paired-delta methodology** from `pebble-mlm-3seed` (same seeds
  `[13, 42, 1337]`, mean ± std + per-seed delta) and mirrors the existing head architectures in
  `src/pebble_llm/models/heads.py` so the serving app can reuse them. The emotion2vec arm is **guarded**:
  if its `funasr` loader fails to install or import, that arm is skipped and the WavLM baseline still
  produces a complete result.

- **The data is open and light.** **RAVDESS** (CC-BY-NC-SA 4.0) gives an 8-way emotion label
  (`neutral, calm, happy, sad, angry, fearful, disgust, surprised`) plus a **derived binary distress
  label** (`sad / angry / fearful / disgust = positive`) that exercises the recall head. The split is
  **speaker-independent** — actors 1–20 train, actors 21–24 validation — so the probe is judged on unseen
  speakers, not memorized voices.

- **Honest caveat.** RAVDESS distress is a **proxy** — acted emotion, not clinical stress or crisis.
  It is the right *first* dataset (open, light, fast to iterate), but the survey's **StressID** and
  **DAIC / DAIC+** datasets are the next step toward a clinically grounded distress signal.

---

## Rejected alternatives

- **Full voice + text co-attention fusion.** This is the *eventual* system (survey scope dial **B**:
  voice-primary + NeoBERT text support), not the first pilot. It needs paired voice+text data and a
  fusion stack — too large and too coupled to start with. Deferred to the follow-on.

- **Training a speech encoder from scratch.** The survey rules this out directly: it needs *"tens of
  thousands of hours + large GPU budget."* We reuse pretrained encoders and probe them, exactly as the
  project already reuses NeoBERT for text.

- **Clinical depression multimodal (e.g. U-Fair / DAIC-WOZ).** The closest clinical analogue, but the
  data is **gated** and the pipeline is heavy (per-symptom PHQ heads, multimodal fusion). Too much to
  carry on day one; revisited once the head topology and recall framing are proven on open data.

---

## Implementation plan — the notebook pipeline

The experiment is the Kaggle notebook in `kaggle/pebble-voice-backbone/`, assembled cell-by-cell by
`build_ipynb.py` (markdown header + one code cell per stage). Cells 0–5:

| Cell | Stage | What it does |
|---|---|---|
| **0** | Install | Pin the audio stack — `torch==2.5.1 / torchaudio==2.5.1` (cu121, so P100 / sm_60 is not dropped), `transformers==4.48.2 datasets==3.2.0`, `librosa soundfile scikit-learn`. `funasr`/`modelscope` (emotion2vec route) install is best-effort; a failure only skips the emotion2vec arm. |
| **1** | Imports & config | Seeds `[13, 42, 1337]`, 16 kHz / 4 s clips, speaker-independent split (actors 1–20 train, 21–24 val), `RECALL_FLOOR = 0.90`, `SAFETY_POS_WEIGHT = 3.0`, 8 emotions, distress positives = `{sad, angry, fearful, disgust}`. |
| **2** | Data | Load `narad/ravdess`, resample 48 kHz → 16 kHz, pad/trim to 4 s, build records `{wav, emo, distress}` split by actor. Stash one validation clip as `sample_val.wav` for the FastAPI verifier. |
| **3** | Frozen features | Each encoder runs **once**. **WavLM-Large** via `transformers` (mean-pool `last_hidden_state` → 1024-d); **emotion2vec** via `funasr` utterance embedding (768-d). Both wrapped in try/except so a failed backbone is skipped, not fatal. |
| **4** | Multi-task probe | `EmotionHead` (CE) + `SafetyHead` (pos-weighted BCE), mirroring `src/pebble_llm/models/heads.py`. Trained per seed on cached embeddings. The distress threshold is chosen at **recall floor 0.90** and **precision at that floor** is reported (Pebble's safety framing). |
| **5** | Aggregate + serve | Mean ± std across seeds, the **paired emotion2vec − WavLM** per-seed delta (the real verdict), winner by mean emotion macro-F1. Saves per-backbone **serving bundles** (`config.json` + `emotion_head.pt` + `safety_head.pt`), `results_voice_backbone.{csv,json}`, and the sample wav. |

The serving bundle's `config.json` carries everything the FastAPI app needs to reload a backbone:
HF id, embed dim, emotion list, distress emotions, the recall-floored `safety_threshold`, pooling, and
head dims.

---

## How it maps to the thesis

- This pilot is the **"backbone selection" chapter** — the empirical answer to the survey's open
  emotion2vec-vs-WavLM question, with a paired delta as the verdict.
- The **recall-floored distress head** is the voice analogue of Pebble's text **safety head**
  (BCE under a hard recall floor) — the first transfer of Pebble's headline novelty into speech.
- The eventual **scope-dial-B voice-led fusion** (voice primary + NeoBERT text as a supporting cue,
  measuring how much text lifts crisis recall) is the **follow-on** that builds on the winning backbone
  chosen here.

---

## Results

Kaggle GPU (P100), RAVDESS, 3 seeds [13, 42, 1337], speaker-independent split (actors 1–20 train /
21–24 val). `mean ± std`.

| Backbone | Emotion macro-F1 | Distress recall@0.5 | Precision @ recall-floor (0.90) |
|---|---|---|---|
| **wavlm-large (baseline) — winner** | **0.609 ± 0.019** | 1.00 ± 0.00 | **0.617 ± 0.003** (thr 0.69) |
| emotion2vec (primary) | 0.537 ± 0.007 | 1.00 ± 0.00 | 0.597 ± 0.012 (thr 0.72) |
| **paired delta** (emotion2vec − wavlm) | **−0.071 ± 0.017** (3/3 seeds < 0) | — | −0.020 ± 0.015 (2/3 < 0) |

**Verdict.** WavLM-Large beats the emotion-specialized emotion2vec on RAVDESS frozen linear-probe —
on emotion macro-F1 by ~7 points (negative on *every* seed) and slightly on distress precision. This
answers the survey's explicit open question ("did the emotion-specialized model actually beat the
strong general one?"): **on this protocol, no.** The likely reasons match the survey's own caveats —
emotion2vec is validated on *categorical* emotion via its own linear-probe protocol, while WavLM-Large
is larger (1024-d vs 768-d) and pretrained on ~360× more audio; RAVDESS acted speech may also favor
the general acoustic encoder. This makes WavLM-Large the recommended Pebble voice backbone (and it
carries the MIT license + the proven dimensional-regression recipe the survey flagged).

> WavLM-Large verified end-to-end through the FastAPI verifier on held-out RAVDESS clips:
> fearful→distress 0.84 (flagged), angry→0.76 (flagged), sad→0.91 (flagged), neutral→0.68 (not
> flagged) — the safety head separates high-distress from neutral as intended. Emotion confusions
> concentrate on acoustically-close happy/sad/disgust, consistent with macro-F1 ≈ 0.61.
> (emotion2vec's `artifact_emotion2vec/` bundle is downloaded and serveable on any Linux/funasr host;
> it was not re-served here because funasr can't install on the Intel-mac dev box.)

---

## How to run

1. **Build the notebook:**
   ```bash
   python kaggle/pebble-voice-backbone/build_ipynb.py
   ```
2. **Push to Kaggle** (GPU + internet kernel):
   ```bash
   kaggle kernels push -p kaggle/pebble-voice-backbone
   ```
   Then download the outputs (`results_voice_backbone.{csv,json}`, `artifact_*/`, `sample_val.wav`).
3. **Local CPU smoke** for a real artifact without Kaggle: `scripts/voice_local_smoke.py` runs a
   WavLM-Base subset and emits a serving bundle that the FastAPI verifier
   `src/pebble_llm/serving/voice_app.py` can load to confirm the inference path end-to-end.
