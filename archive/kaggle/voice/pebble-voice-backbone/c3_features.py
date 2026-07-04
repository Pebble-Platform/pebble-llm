# Cell 3 — frozen feature extraction (each encoder runs ONCE; heads train on cached embeddings).
from transformers import AutoFeatureExtractor, WavLMModel

def wavlm_extractor():
    fe = AutoFeatureExtractor.from_pretrained("microsoft/wavlm-large")
    model = WavLMModel.from_pretrained("microsoft/wavlm-large").to(DEVICE).eval()
    @torch.no_grad()
    def extract(wavs, bs=16):
        out = []
        for i in range(0, len(wavs), bs):
            batch = [w for w in wavs[i:i + bs]]
            enc = fe(batch, sampling_rate=SR, return_tensors="pt", padding=True)
            enc = {k: v.to(DEVICE) for k, v in enc.items()}
            with torch.cuda.amp.autocast(enabled=DEVICE.type == "cuda"):
                h = model(**enc).last_hidden_state            # (B, T, 1024)
            out.append(h.float().mean(dim=1).cpu().numpy())   # mean-pool over time
        return np.concatenate(out, 0)
    return extract, 1024

def emotion2vec_extractor():
    # Primary backbone. Guarded: any failure here -> caller skips this arm.
    # "model not registered" is FunASR masking a modelscope-CN download failure;
    # hub="hf" pulls from HuggingFace instead, with a snapshot_download fallback.
    from funasr import AutoModel as FunASR
    try:
        model = FunASR(model="iic/emotion2vec_base", hub="hf", disable_update=True)
    except Exception:
        from huggingface_hub import snapshot_download
        local = snapshot_download("emotion2vec/emotion2vec_base")
        model = FunASR(model=local, disable_update=True)
    def extract(wavs, bs=None):
        feats = []
        for w in wavs:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                sf.write(tf.name, w, SR); path = tf.name
            r = model.generate(path, granularity="utterance", extract_embedding=True,
                               output_dir=None)
            feats.append(np.asarray(r[0]["feats"], dtype=np.float32))
            os.remove(path)
        return np.stack(feats)                                 # (N, 768)
    return extract, 768

import soundfile as sf
BACKBONES = {}   # name -> {"train": arr, "val": arr, "dim": int}
train_wavs = [r["wav"] for r in train_recs]
val_wavs = [r["wav"] for r in val_recs]

for name, builder in [("emotion2vec", emotion2vec_extractor), ("wavlm-large", wavlm_extractor)]:
    try:
        print(f"\n[{name}] building extractor...")
        extract, dim = builder()
        tr = extract(train_wavs); va = extract(val_wavs)
        BACKBONES[name] = {"train": tr, "val": va, "dim": dim}
        print(f"[{name}] features: train{tr.shape} val{va.shape}")
        del extract; torch.cuda.empty_cache()
    except Exception as e:
        print(f"[{name}] SKIPPED -> {type(e).__name__}: {e}")

assert BACKBONES, "no backbone produced features"
print("\nbackbones with features:", list(BACKBONES))
