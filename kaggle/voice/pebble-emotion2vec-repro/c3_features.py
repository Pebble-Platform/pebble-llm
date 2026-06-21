# Cell 3 — frozen FRAME-LEVEL feature extraction (v2, faithful SUPERB recipe).
# Each encoder runs ONCE over all 1440 clips, returning (N, T_MAX, dim) frame features
# (padded/truncated to T_MAX); the probe pools AFTER the first Linear+ReLU using the
# true frame lengths (c2 `flen`) as a mask — matching emotion2vec/EmoBox SuperbBaseModel.
# emotion2vec = funasr granularity="frame" (T,768); WavLM-Large = last_hidden_state (T,1024).
from transformers import AutoFeatureExtractor, WavLMModel
import soundfile as sf

def pad_T(arr):
    # arr (T, dim) -> (T_MAX, dim) padded with zeros or truncated.
    if len(arr) >= T_MAX:
        return arr[:T_MAX]
    return np.pad(arr, ((0, T_MAX - len(arr)), (0, 0)))

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
            h = h.float().cpu().numpy()
            for j in range(h.shape[0]):
                out.append(pad_T(h[j]).astype(np.float16))    # keep time dim
        return np.stack(out)                                  # (N, T_MAX, 1024)
    return extract, 1024

def emotion2vec_extractor():
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
            r = model.generate(path, granularity="frame", extract_embedding=True,
                               output_dir=None)
            f = np.asarray(r[0]["feats"], dtype=np.float32)    # (T, 768)
            os.remove(path)
            feats.append(pad_T(f).astype(np.float16))
        return np.stack(feats)                                 # (N, T_MAX, 768)
    return extract, 768

all_wavs = [r["wav"] for r in recs]
flen_all = np.array([r["flen"] for r in recs])
BACKBONES = {}   # name -> {"X": (N,T_MAX,dim) f16, "dim": int}
for name, builder in [("emotion2vec", emotion2vec_extractor), ("wavlm-large", wavlm_extractor)]:
    try:
        print(f"\n[{name}] building extractor...")
        extract, dim = builder()
        X = extract(all_wavs)
        BACKBONES[name] = {"X": X, "dim": dim}
        print(f"[{name}] frame features: {X.shape} ({X.dtype}) | flen mean={flen_all.mean():.0f}")
        del extract; torch.cuda.empty_cache()
    except Exception as e:
        print(f"[{name}] SKIPPED -> {type(e).__name__}: {e}")

assert BACKBONES, "no backbone produced features"
print("\nbackbones with features:", list(BACKBONES))
