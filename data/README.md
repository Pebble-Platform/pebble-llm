# Data

> **Never commit data.** Contents of every subdir are gitignored (only `.gitkeep` is tracked).
> This data contains real mental-health / crisis content and PII. Handle per the
> annotator-wellbeing and privacy constraints in the strategy doc.

Organized by research stream — `finetuning-message/` (text/NeoBERT) and `voice/` (speech):

```
data/
  finetuning-message/   # text pipeline (the local code pipeline lives here)
    raw/        Untouched source dumps: Firestore silver-label exports, downloaded external datasets.
    interim/    Partially processed (assembled inputs, mapped labels) — reproducible from raw/.
    processed/  Final train/val/test splits ready for training. User-level split, then severity-quartile stratified (§5.5).
    external/   Public transfer datasets: GoEmotions, SemEval, tweeteval, WASSA, ESConv, CSSRS.
  voice/                # speech datasets (experiments run on Kaggle, no local pipeline)
    external/   RAVDESS, TESS, EmoDB, VIVOS, IEMOCAP, … (see docs/papers/voice/voice-speech-papers.md)
```

Code/config (`configs/config.yaml`, `pebble_llm.config.DataConfig`) point at `data/finetuning-message/{raw,interim,processed,external}`.

## Splits (strategy §5.5)

| Split | Size | Composition |
|---|---|---|
| Training | 4,000–5,500 | ~3,500 silver (filtered) + ~500 Protocol A human-corrected + safety positives (§5.4) + transfer examples |
| Validation | 500 | 250 human-annotated + 250 silver |
| Test | 500 | 100% Protocol B (unanchored human). Non-negotiable — eval on silver/anchored is circular. |

**User-level splitting:** every user appears in exactly one split. Deterministic
hash of userId (`pebble_llm.data.splits.assign_split`), stored as metadata.
