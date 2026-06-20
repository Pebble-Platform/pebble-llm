# Cell 2 — RAVDESS load, resample to 16 kHz, speaker-independent split.
import torchaudio
from datasets import load_dataset

ds = load_dataset("narad/ravdess", split="train", trust_remote_code=True)
print("RAVDESS:", ds)
INT2STR = ds.features["labels"].int2str

def fix_len(wav):
    if len(wav) >= MAX_SAMPLES:
        return wav[:MAX_SAMPLES]
    return np.pad(wav, (0, MAX_SAMPLES - len(wav)))

def parse_actor(ex):
    # speaker_id like "Actor_07" or an int; be robust.
    sid = ex.get("speaker_id")
    if isinstance(sid, str):
        digits = "".join(c for c in sid if c.isdigit())
        return int(digits) if digits else -1
    return int(sid) if sid is not None else -1

def to_records(ds):
    train, val = [], []
    for ex in ds:
        a = ex["audio"]
        wav = np.asarray(a["array"], dtype=np.float32)
        src_sr = a["sampling_rate"]
        if src_sr != SR:
            wav = torchaudio.functional.resample(torch.from_numpy(wav), src_sr, SR).numpy()
        wav = fix_len(wav.astype(np.float32))
        emo = INT2STR(ex["labels"])
        rec = {"wav": wav, "emo": EMO2ID[emo], "distress": int(emo in DISTRESS)}
        (train if parse_actor(ex) in TRAIN_ACTORS else val).append(rec)
    return train, val

train_recs, val_recs = to_records(ds)
print(f"train={len(train_recs)} val={len(val_recs)} clips "
      f"| train distress+={sum(r['distress'] for r in train_recs)} "
      f"val distress+={sum(r['distress'] for r in val_recs)}")

# stash one val clip as the FastAPI sample (16 kHz mono wav).
import soundfile as sf
sample = val_recs[0]
sf.write(f"{ART}/sample_val.wav", sample["wav"], SR)
print(f"sample wav -> {ART}/sample_val.wav (emo={EMOTIONS[sample['emo']]}, distress={sample['distress']})")
