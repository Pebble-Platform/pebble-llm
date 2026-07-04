# Vendored NeoBERT modeling code

Custom modeling code for `chandar-lab/NeoBERT`, vendored so a remote change can't
silently alter behavior (strategy §4, §6.1 Step 0).

- **Source:** https://huggingface.co/chandar-lab/NeoBERT
- **Pinned revision:** `5424c8efeea6491b151d62dee55a752165407430`
- **Vendored:** 2026-05-29 via `scripts/vendor_neobert.py`

Files: `model.py` (modeling), `rotary.py` (RoPE), `config.json`. Weights
(`model.safetensors`) and tokenizer are downloaded at the pinned revision, not vendored.

To re-vendor at a new revision: update `PINNED_REVISION` in `scripts/vendor_neobert.py`
and the `model.revision` in `configs/`, then run `uv run python scripts/vendor_neobert.py`.
