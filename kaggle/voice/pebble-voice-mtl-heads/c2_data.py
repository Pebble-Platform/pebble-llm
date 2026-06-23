# Cell 2 — RAVDESS load (all 1440 speech clips), resample 48k->16k. No fixed split:
# folds are drawn randomly in the probe cell (paper protocol).
import torchaudio
from datasets import load_dataset
import soundfile as sf

ds = load_dataset("narad/ravdess", split="train", trust_remote_code=True)
print("RAVDESS:", ds)
INT2STR = ds.features["labels"].int2str

def fix_len(wav):
    # pad/truncate to 5s; also return the true (pre-pad) valid frame count for masking.
    n = min(len(wav), MAX_SAMPLES)
    flen = int(np.clip(round(n / FRAME_HOP), 1, T_MAX))
    if len(wav) >= MAX_SAMPLES:
        return wav[:MAX_SAMPLES], flen
    return np.pad(wav, (0, MAX_SAMPLES - len(wav))), flen

def to_records(ds):
    recs = []
    for ex in ds:
        a = ex["audio"]
        wav = np.asarray(a["array"], dtype=np.float32)
        src_sr = a["sampling_rate"]
        if src_sr != SR:
            wav = torchaudio.functional.resample(torch.from_numpy(wav), src_sr, SR).numpy()
        wav, flen = fix_len(wav.astype(np.float32))
        emo = INT2STR(ex["labels"])
        recs.append({"wav": wav, "y": EMO2ID[emo], "flen": flen})
    return recs

recs = to_records(ds)
y_all = np.array([r["y"] for r in recs])
print(f"clips={len(recs)} | per-class counts={np.bincount(y_all, minlength=N_EMO).tolist()}")
assert len(recs) == 1440, f"expected 1440 RAVDESS speech clips, got {len(recs)}"

# stash one clip as the local FastAPI/test sample (16 kHz mono wav).
sample = recs[0]
sf.write(f"{ART}/sample_val.wav", sample["wav"], SR)
print(f"sample wav -> {ART}/sample_val.wav (emo={EMOTIONS[sample['y']]})")
